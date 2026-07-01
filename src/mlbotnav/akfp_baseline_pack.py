from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest(root: Path, pattern: str) -> Path | None:
    items = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return items[0] if items else None


def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def _parse_trade_rows(csv_path: Path) -> list[dict[str, Any]]:
    if not csv_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Trade-like rows: we keep rows where net_return is non-zero or exit_time exists.
            net_ret = _to_float(r.get("net_return", 0.0), 0.0)
            exit_t = str(r.get("exit_time_utc", "") or "").strip()
            if abs(net_ret) > 1e-12 or exit_t:
                rows.append(r)
    return rows


def _max_loss_streak(values: list[float]) -> int:
    mx = 0
    cur = 0
    for v in values:
        if v < 0:
            cur += 1
            if cur > mx:
                mx = cur
        else:
            cur = 0
    return mx


def _side_baseline(project_root: Path, *, symbol: str, timeframe: str, test_date: str, side_mode: str) -> dict[str, Any]:
    fr = (project_root / "reports" / "final_review").resolve()
    rep = _latest(fr, f"oos_report_{symbol}_{timeframe}_{test_date}_{side_mode}_*.json")
    if not rep:
        return {"status": "MISSING", "side_mode": side_mode, "report_path": None}

    obj = _load_json(rep)
    bt = dict(obj.get("backtest") or {})
    artifacts = dict(obj.get("artifacts") or {})
    trades_path = Path(str(artifacts.get("backtest_path", "") or ""))
    if trades_path and not trades_path.is_absolute():
        trades_path = (project_root / trades_path).resolve()
    rows = _parse_trade_rows(trades_path) if trades_path else []

    pnl = [_to_float(r.get("net_pnl_usd", 0.0), 0.0) for r in rows]
    pnl_pos = [x for x in pnl if x > 0]
    pnl_neg = [x for x in pnl if x < 0]

    trades = int(bt.get("trades", 0) or 0)
    bars = len(rows)
    filtered_trades_count = max(0, bars - trades)
    no_trade_ratio = _to_float(bt.get("no_trade_ratio", 0.0), 0.0)
    overfilter_risk = bool(trades < 10 or no_trade_ratio > 0.98)

    return {
        "status": "OK",
        "side_mode": side_mode,
        "report_path": str(rep),
        "test_date": str(obj.get("test_day", test_date)),
        "train_pipeline_report": obj.get("train_pipeline_report"),
        "goal_pass": bool(obj.get("goal_pass", False)),
        "metrics": {
            "profit_total_pct": _to_float(bt.get("net_return_pct", 0.0), 0.0),
            "max_drawdown_pct": _to_float(bt.get("max_drawdown_pct", 0.0), 0.0),
            "winrate": _to_float(bt.get("hit_rate", 0.0), 0.0),
            "trades_count": trades,
            "avg_profit_usd": mean(pnl_pos) if pnl_pos else 0.0,
            "avg_loss_usd": mean(pnl_neg) if pnl_neg else 0.0,
            "loss_streak": _max_loss_streak(pnl),
            "stability_score": _to_float(bt.get("sharpe_like", 0.0), 0.0),
            "filtered_trades_count": int(filtered_trades_count),
            "no_trade_ratio_days": _to_float(bt.get("no_trade_ratio_days", 0.0), 0.0),
            "overfilter_risk": overfilter_risk,
            "profit_factor_proxy": (
                (sum(pnl_pos) / abs(sum(pnl_neg))) if pnl_pos and pnl_neg and abs(sum(pnl_neg)) > 1e-12 else 0.0
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack AKFP baseline report from latest long/short OOS reports.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--test-date", required=True)
    parser.add_argument("--output-dir", default="reports/akfp/baseline")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    long_side = _side_baseline(
        project_root,
        symbol=str(args.symbol),
        timeframe=str(args.timeframe),
        test_date=str(args.test_date),
        side_mode="long_only",
    )
    short_side = _side_baseline(
        project_root,
        symbol=str(args.symbol),
        timeframe=str(args.timeframe),
        test_date=str(args.test_date),
        side_mode="short_only",
    )

    sides_ok = [x for x in [long_side, short_side] if x.get("status") == "OK"]
    status = "PASS" if len(sides_ok) == 2 else "FAIL"
    total_pct = sum(_to_float((x.get("metrics") or {}).get("profit_total_pct", 0.0), 0.0) for x in sides_ok)

    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": str(args.symbol),
        "timeframe": str(args.timeframe),
        "test_date": str(args.test_date),
        "baseline": {
            "long_only": long_side,
            "short_only": short_side,
            "combined_simple_sum_profit_pct": total_pct,
        },
    }

    out = out_dir / f"akfp_baseline_{args.symbol}_{args.timeframe}_{args.test_date}_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "report_path": str(out)}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

