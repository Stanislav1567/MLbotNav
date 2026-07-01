from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_json(stdout: str) -> dict[str, Any] | None:
    txt = (stdout or "").strip()
    if not txt:
        return None
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    for line in reversed([x.strip() for x in txt.splitlines() if x.strip()]):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    parsed = _extract_json(p.stdout or "")
    return {
        "returncode": int(p.returncode),
        "cmd": cmd,
        "stdout_tail": (p.stdout or "")[-4000:],
        "stderr_tail": (p.stderr or "")[-4000:],
        "parsed_json": parsed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AKFP P9: final long-only cycle.")
    parser.add_argument("--policy", default="configs/akfp_policy.yaml")
    parser.add_argument("--best-combos", default="reports/akfp/combo_working/BEST_COMBOS.json")
    parser.add_argument("--output-dir", default="reports/akfp/final_long")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = (project_root / policy_path).resolve()
    cfg = _load_yaml(policy_path)
    akfp = dict(cfg.get("akfp") or {})
    exe = dict(akfp.get("execution") or {})

    symbol = str(exe.get("symbol", "SOLUSDT"))
    timeframe = str(exe.get("timeframe", "1m"))
    train_date = str(exe.get("train_date", "2026-05-19"))
    test_date = str(exe.get("test_date", "2026-05-20"))
    repeats = max(2, int(exe.get("repeats", 2)))
    threads = int(exe.get("threads", 8))
    search_workers = int(exe.get("search_workers", 8))
    cpu_max_pct = float(exe.get("cpu_max_pct", 85))

    best_combos_path = Path(args.best_combos)
    if not best_combos_path.is_absolute():
        best_combos_path = (project_root / best_combos_path).resolve()
    best_combos = _load_json(best_combos_path) if best_combos_path.exists() else {}
    long_best = best_combos.get("long_only") if isinstance(best_combos, dict) else {}
    combo_filters = []
    if isinstance(long_best, dict):
        combo_filters = [str(x) for x in (long_best.get("combo_filters") or []) if str(x).strip()]
    if not combo_filters:
        combo_filters = ["none"]

    python_exe = str((project_root / ".venv" / "Scripts" / "python.exe").resolve())
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        python_exe,
        "-m",
        "mlbotnav.adaptive_auto_train",
        "--symbol",
        symbol,
        "--timeframe",
        timeframe,
        "--train-start",
        train_date,
        "--train-end",
        train_date,
        "--test-day",
        test_date,
        "--test-end-day",
        test_date,
        "--signal-mode",
        "long_only",
        "--trend-hypothesis-grid",
        ",".join(combo_filters),
        "--disable-backlog-active-append",
        "--contour-id",
        "long_only",
        "--repeats",
        str(int(repeats)),
        "--goal-net-return-pct",
        "1",
        "--allow-subgoal-candidates",
        "--min-train-rows",
        "900",
        "--n-folds",
        "2",
        "--horizons-grid",
        "5,8,12,20,30,45,60,90",
        "--min-expected-move-grid",
        "0.001,0.0015,0.002,0.003,0.004,0.005",
        "--execution-mode",
        "exchange_like",
        "--order-type",
        "market",
        "--notional-usd",
        "10",
        "--leverage",
        "10",
        "--cpu-max-pct",
        str(float(cpu_max_pct)),
        "--max-threads",
        str(int(threads)),
        "--search-workers",
        str(int(search_workers)),
        "--speed-profile",
        "turbo",
        "--temporary-unlock-readiness",
        "--unlock-reason",
        "AKFP P9 LONG_FINAL",
    ]
    run = _run(cmd, project_root)
    parsed = run.get("parsed_json") or {}
    summary_path = str(parsed.get("summary_path", "")).strip()
    summary_obj: dict[str, Any] = {}
    if summary_path and Path(summary_path).exists():
        try:
            summary_obj = _load_json(Path(summary_path))
        except Exception:
            summary_obj = {}

    top = parsed.get("top_strategy") if isinstance(parsed, dict) else None
    top_card_path = None
    if isinstance(top, dict):
        raw = top.get("top_card")
        if isinstance(raw, str) and raw.strip():
            top_card_path = raw.strip()
    top_card = None
    if top_card_path and Path(top_card_path).exists():
        try:
            top_card = _load_json(Path(top_card_path))
        except Exception:
            top_card = None

    train_gate_pass = None
    net_return_pct = None
    trades = None
    if isinstance(top_card, dict):
        diag = top_card.get("diagnostics") or {}
        met = top_card.get("metrics") or {}
        train_gate_pass = bool(diag.get("train_gate_pass")) if diag.get("train_gate_pass") is not None else None
        try:
            net_return_pct = float(met.get("net_return_pct")) if met.get("net_return_pct") is not None else None
        except Exception:
            net_return_pct = None
        try:
            trades = int(met.get("trades")) if met.get("trades") is not None else None
        except Exception:
            trades = None

    technical_checks = [
        {"name": "adaptive_rc_zero", "ok": int(run.get("returncode", 1)) == 0},
        {"name": "summary_present", "ok": bool(summary_path and Path(summary_path).exists())},
    ]
    strategy_checks = [
        {"name": "top_card_present", "ok": bool(top_card_path and Path(top_card_path).exists()), "informational": True},
        {"name": "train_gate_pass", "ok": bool(train_gate_pass is True), "informational": True},
        {"name": "trades_positive", "ok": bool(isinstance(trades, int) and trades > 0), "informational": True},
    ]
    checks = technical_checks + strategy_checks
    failed = sum(1 for c in checks if (not bool(c["ok"])) and (not bool(c.get("informational"))))
    technical_pass = failed == 0
    strategy_pass = all(bool(c["ok"]) for c in strategy_checks)
    package_green = bool(strategy_pass)
    # P0 truth gate: package is PASS only when both technical and strategy checks pass.
    status = "PASS" if (technical_pass and strategy_pass) else "FAIL"

    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "timeframe": timeframe,
        "train_date": train_date,
        "test_date": test_date,
        "repeats": repeats,
        "combo_filters": combo_filters,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "failed": int(failed),
            "informational_failed": int(sum(1 for c in checks if bool(c.get("informational")) and not bool(c["ok"]))),
        },
        "technical_pass": bool(technical_pass),
        "strategy_pass": bool(strategy_pass),
        "package_green": bool(package_green),
        "run": run,
        "summary_path": summary_path or None,
        "top_card_path": top_card_path,
        "train_gate_pass": train_gate_pass,
        "net_return_pct": net_return_pct,
        "trades": trades,
        "summary_obj": summary_obj,
    }

    report_path = out_dir / f"akfp_long_final_cycle_{symbol}_{timeframe}_{test_date}_{_utc_tag()}.json"
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    package_path = out_dir / "LONG_FINAL_PACKAGE.json"
    package_path.write_text(
        json.dumps(
            {
                "status": status,
                "technical_pass": bool(technical_pass),
                "strategy_pass": bool(strategy_pass),
                "package_green": bool(package_green),
                "truth_gate_pass": bool(technical_pass and strategy_pass),
                "report_path": str(report_path),
                "top_card_path": top_card_path,
                "summary_path": summary_path or None,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": status,
                "report_path": str(report_path),
                "package_path": str(package_path),
                "technical_pass": bool(technical_pass),
                "strategy_pass": bool(strategy_pass),
                "package_green": bool(package_green),
            },
            ensure_ascii=False,
        )
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
