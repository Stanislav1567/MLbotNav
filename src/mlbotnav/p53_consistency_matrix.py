from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest(root: Path, pattern: str) -> Path | None:
    files = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _adaptive_step(cycle: dict[str, Any], mode: str) -> dict[str, Any] | None:
    for st in cycle.get("steps", []) if isinstance(cycle.get("steps"), list) else []:
        if isinstance(st, dict) and str(st.get("task", "")) == f"adaptive_auto_train_{mode}":
            return st
    return None


def _table_conv_step(cycle: dict[str, Any]) -> dict[str, Any] | None:
    for st in cycle.get("steps", []) if isinstance(cycle.get("steps"), list) else []:
        if isinstance(st, dict) and str(st.get("task", "")) == "table_convergence_5plus":
            return st
    return None


def _extract_report_path(step: dict[str, Any] | None) -> str | None:
    if not step:
        return None
    parsed = step.get("parsed_json")
    if isinstance(parsed, dict):
        rp = str(parsed.get("report_path", "") or "").strip()
        return rp or None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="P5.3 consistency matrix across long/short contour cycles.")
    parser.add_argument("--qa-dir", default="reports/qa_gate")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    qa = (root / args.qa_dir).resolve()
    qa.mkdir(parents=True, exist_ok=True)
    out = qa / f"p53_consistency_matrix_{_utc_tag()}.json"

    long_path = _latest(qa, "contour_cycle_long_only_*.json")
    short_path = _latest(qa, "contour_cycle_short_only_*.json")

    checks: list[dict[str, Any]] = []
    checks.append(_check("long_cycle_exists", long_path is not None and long_path.exists(), {"path": str(long_path) if long_path else None}))
    checks.append(_check("short_cycle_exists", short_path is not None and short_path.exists(), {"path": str(short_path) if short_path else None}))

    if not (long_path and short_path and long_path.exists() and short_path.exists()):
        payload = {
            "status": "FAIL",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
            "summary": {"total": len(checks), "failed": int(sum(1 for c in checks if not c["ok"]))},
        }
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "FAIL", "report_path": str(out)}, ensure_ascii=False))
        return 1

    long_cycle = _load_json(long_path)
    short_cycle = _load_json(short_path)
    checks.append(_check("long_cycle_pass", str(long_cycle.get("status", "")).upper() == "PASS"))
    checks.append(_check("short_cycle_pass", str(short_cycle.get("status", "")).upper() == "PASS"))

    lp = long_cycle.get("params", {}) if isinstance(long_cycle.get("params"), dict) else {}
    sp = short_cycle.get("params", {}) if isinstance(short_cycle.get("params"), dict) else {}
    for k in ["symbol", "timeframe", "train_start", "train_end", "test_day", "test_end_day", "repeats"]:
        checks.append(_check(f"params_{k}_match", str(lp.get(k)) == str(sp.get(k)), {"long": lp.get(k), "short": sp.get(k)}))

    long_ad = _adaptive_step(long_cycle, "long_only")
    short_ad = _adaptive_step(short_cycle, "short_only")
    checks.append(_check("long_adaptive_step_exists", long_ad is not None))
    checks.append(_check("short_adaptive_step_exists", short_ad is not None))

    long_summary_path = None
    short_summary_path = None
    if long_ad:
        parsed = long_ad.get("parsed_json")
        if isinstance(parsed, dict):
            s = str(parsed.get("summary_path", "") or "").strip()
            if s:
                long_summary_path = Path(s)
    if short_ad:
        parsed = short_ad.get("parsed_json")
        if isinstance(parsed, dict):
            s = str(parsed.get("summary_path", "") or "").strip()
            if s:
                short_summary_path = Path(s)

    if long_summary_path and not long_summary_path.is_absolute():
        long_summary_path = (root / long_summary_path).resolve()
    if short_summary_path and not short_summary_path.is_absolute():
        short_summary_path = (root / short_summary_path).resolve()
    checks.append(_check("long_summary_exists", bool(long_summary_path and long_summary_path.exists()), {"path": str(long_summary_path) if long_summary_path else None}))
    checks.append(_check("short_summary_exists", bool(short_summary_path and short_summary_path.exists()), {"path": str(short_summary_path) if short_summary_path else None}))

    long_oos = None
    short_oos = None
    long_report_obj = None
    short_report_obj = None

    if long_summary_path and long_summary_path.exists():
        long_summary = _load_json(long_summary_path)
        long_oos = str(((long_summary.get("best_oos") or {}).get("oos_report") or "")).strip()
    if short_summary_path and short_summary_path.exists():
        short_summary = _load_json(short_summary_path)
        short_oos = str(((short_summary.get("best_oos") or {}).get("oos_report") or "")).strip()

    long_oos_path = Path(long_oos) if long_oos else None
    short_oos_path = Path(short_oos) if short_oos else None
    if long_oos_path and not long_oos_path.is_absolute():
        long_oos_path = (root / long_oos_path).resolve()
    if short_oos_path and not short_oos_path.is_absolute():
        short_oos_path = (root / short_oos_path).resolve()
    checks.append(_check("long_oos_exists", bool(long_oos_path and long_oos_path.exists()), {"path": str(long_oos_path) if long_oos_path else None}))
    checks.append(_check("short_oos_exists", bool(short_oos_path and short_oos_path.exists()), {"path": str(short_oos_path) if short_oos_path else None}))

    if long_oos_path and long_oos_path.exists():
        long_report_obj = _load_json(long_oos_path)
        long_mode = str((long_report_obj.get("risk_policy") or {}).get("signal_mode", "") or "")
        checks.append(_check("long_oos_signal_mode_long_only", long_mode == "long_only", {"signal_mode": long_mode}))
        bt_csv = str(((long_report_obj.get("artifacts") or {}).get("backtest_path") or "")).strip()
        bt_path = Path(bt_csv) if bt_csv else None
        if bt_path and not bt_path.is_absolute():
            bt_path = (root / bt_path).resolve()
        exists = bool(bt_path and bt_path.exists())
        checks.append(_check("long_oos_backtest_csv_exists", exists, {"path": str(bt_path) if bt_path else None}))
        if exists and bt_path is not None:
            df_bt = pd.read_csv(bt_path)
            if "side" in df_bt.columns:
                rows = int((pd.to_numeric(df_bt["side"], errors="coerce").fillna(0.0).abs() > 0).sum())
            else:
                rows = int(len(df_bt))
            rep_trades = int(((long_report_obj.get("backtest") or {}).get("trades", -1)))
            checks.append(_check("long_oos_trades_match_csv_rows", rows == rep_trades, {"csv_rows": rows, "trades": rep_trades}))

    if short_oos_path and short_oos_path.exists():
        short_report_obj = _load_json(short_oos_path)
        short_mode = str((short_report_obj.get("risk_policy") or {}).get("signal_mode", "") or "")
        checks.append(_check("short_oos_signal_mode_short_only", short_mode == "short_only", {"signal_mode": short_mode}))
        bt_csv = str(((short_report_obj.get("artifacts") or {}).get("backtest_path") or "")).strip()
        bt_path = Path(bt_csv) if bt_csv else None
        if bt_path and not bt_path.is_absolute():
            bt_path = (root / bt_path).resolve()
        exists = bool(bt_path and bt_path.exists())
        checks.append(_check("short_oos_backtest_csv_exists", exists, {"path": str(bt_path) if bt_path else None}))
        if exists and bt_path is not None:
            df_bt = pd.read_csv(bt_path)
            if "side" in df_bt.columns:
                rows = int((pd.to_numeric(df_bt["side"], errors="coerce").fillna(0.0).abs() > 0).sum())
            else:
                rows = int(len(df_bt))
            rep_trades = int(((short_report_obj.get("backtest") or {}).get("trades", -1)))
            checks.append(_check("short_oos_trades_match_csv_rows", rows == rep_trades, {"csv_rows": rows, "trades": rep_trades}))

    # Ensure each contour cycle had a PASS table_convergence report.
    for mode, cycle in [("long", long_cycle), ("short", short_cycle)]:
        conv = _table_conv_step(cycle)
        checks.append(_check(f"{mode}_table_conv_step_exists", conv is not None))
        report_path = _extract_report_path(conv)
        if report_path:
            rp = Path(report_path)
            if not rp.is_absolute():
                rp = (root / rp).resolve()
            if rp.exists():
                ro = _load_json(rp)
                checks.append(_check(f"{mode}_table_conv_report_pass", str(ro.get("status", "")).upper() == "PASS", {"path": str(rp)}))
            else:
                checks.append(_check(f"{mode}_table_conv_report_exists", False, {"path": str(rp)}))
        else:
            checks.append(_check(f"{mode}_table_conv_report_path_present", False))

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "long_cycle": str(long_path),
        "short_cycle": str(short_path),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
