from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _run_cmd(project_root: Path, cmd: list[str]) -> dict[str, Any]:
    p = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    lines = [x.strip() for x in (p.stdout or "").splitlines() if x.strip()]
    parsed = None
    for line in reversed(lines):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                parsed = obj
                break
        except Exception:
            continue
    return {
        "returncode": p.returncode,
        "stdout_tail": (p.stdout or "")[-2000:],
        "stderr_tail": (p.stderr or "")[-2000:],
        "parsed": parsed,
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _oos_metrics(report_path: Path) -> dict[str, Any]:
    rep = _load_json(report_path)
    bt = rep.get("backtest", {}) if isinstance(rep, dict) else {}
    return {
        "report_path": str(report_path),
        "net_return_pct": float(bt.get("net_return_pct", 0.0)),
        "trades": int(bt.get("trades", 0)),
        "hit_rate": float(bt.get("hit_rate", 0.0)),
        "max_drawdown_pct": float(bt.get("max_drawdown_pct", 0.0)),
        "avg_trade_return": float(bt.get("avg_trade_return", 0.0)),
        "net_pnl_total_usd": float(bt.get("net_pnl_total_usd", 0.0)),
        "execution_mode": str(bt.get("execution_mode", rep.get("risk_policy", {}).get("execution_mode", "unknown"))),
        "order_type": str(bt.get("order_type", rep.get("risk_policy", {}).get("order_type", "unknown"))),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare research vs exchange_like OOS behavior for same model/report")
    parser.add_argument("--train-pipeline-report", required=True)
    parser.add_argument("--test-day", required=True)
    parser.add_argument("--test-end-day", default=None)
    parser.add_argument("--goal-net-return-pct", type=float, default=100.0)
    parser.add_argument("--signal-mode", default="both", choices=["both", "long_only", "short_only"])
    parser.add_argument("--leverage", type=float, default=None)
    parser.add_argument("--order-type", default="market", choices=["market", "limit"])
    parser.add_argument("--limit-offset-bps", type=float, default=2.0)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    test_end = str(args.test_end_day) if args.test_end_day else str(args.test_day)

    base_cmd = [
        sys.executable,
        "-m",
        "mlbotnav.oos_evaluate",
        "--train-pipeline-report",
        str(args.train_pipeline_report),
        "--test-day",
        str(args.test_day),
        "--test-end-day",
        str(test_end),
        "--layer",
        "raw",
        "--goal-net-return-pct",
        str(float(args.goal_net_return_pct)),
        "--signal-mode",
        str(args.signal_mode),
    ]
    if args.leverage is not None:
        base_cmd += ["--leverage", str(float(args.leverage))]

    research_cmd = base_cmd + ["--execution-mode", "research"]
    exchange_cmd = base_cmd + [
        "--execution-mode",
        "exchange_like",
        "--order-type",
        str(args.order_type),
        "--limit-offset-bps",
        str(float(args.limit_offset_bps)),
    ]

    research_run = _run_cmd(project_root, research_cmd)
    exchange_run = _run_cmd(project_root, exchange_cmd)

    result: dict[str, Any] = {
        "run_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "train_pipeline_report": str(args.train_pipeline_report),
        "test_day": str(args.test_day),
        "test_end_day": str(test_end),
        "signal_mode": str(args.signal_mode),
        "goal_net_return_pct": float(args.goal_net_return_pct),
        "runs": {
            "research": research_run,
            "exchange_like": exchange_run,
        },
    }

    research_metrics = None
    exchange_metrics = None
    if research_run.get("returncode") == 0 and isinstance(research_run.get("parsed"), dict):
        rp = Path(str(research_run["parsed"].get("oos_report", "")))
        if rp.exists():
            research_metrics = _oos_metrics(rp)
    if exchange_run.get("returncode") == 0 and isinstance(exchange_run.get("parsed"), dict):
        ep = Path(str(exchange_run["parsed"].get("oos_report", "")))
        if ep.exists():
            exchange_metrics = _oos_metrics(ep)

    result["metrics"] = {
        "research": research_metrics,
        "exchange_like": exchange_metrics,
        "delta": {
            "net_return_pct": (float(exchange_metrics["net_return_pct"]) - float(research_metrics["net_return_pct"])) if (exchange_metrics and research_metrics) else None,
            "trades": (int(exchange_metrics["trades"]) - int(research_metrics["trades"])) if (exchange_metrics and research_metrics) else None,
            "hit_rate": (float(exchange_metrics["hit_rate"]) - float(research_metrics["hit_rate"])) if (exchange_metrics and research_metrics) else None,
            "max_drawdown_pct": (float(exchange_metrics["max_drawdown_pct"]) - float(research_metrics["max_drawdown_pct"])) if (exchange_metrics and research_metrics) else None,
        },
    }

    out_dir = project_root / "reports" / "final_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"execution_parity_audit_{ts}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"report_path": str(out_path), "has_research": research_metrics is not None, "has_exchange_like": exchange_metrics is not None}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
