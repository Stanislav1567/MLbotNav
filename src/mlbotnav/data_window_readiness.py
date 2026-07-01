from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlbotnav.timeframes import canonical_timeframe, timeframe_aliases


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def expected_days(start_date: str, end_date: str) -> list[str]:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    if end < start:
        return []
    out: list[str] = []
    cur = start
    while cur <= end:
        out.append(cur.strftime("%Y-%m-%d"))
        cur += timedelta(days=1)
    return out


def _day_file_exists(
    project_root: Path,
    *,
    layer: str,
    day: str,
    symbol: str,
    timeframe: str,
) -> bool:
    for tf_label in timeframe_aliases(timeframe):
        p = (
            project_root
            / "data"
            / layer
            / "bybit_ohlcv"
            / f"dt={day}"
            / f"tf={tf_label}"
            / f"symbol={symbol}"
            / "part-final.csv"
        )
        if p.exists():
            return True
    return False


def evaluate_data_window_readiness(
    project_root: Path,
    *,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    layer: str = "raw",
    require_full_coverage: bool = True,
) -> dict:
    canonical_tf = canonical_timeframe(timeframe)
    days = expected_days(start_date, end_date)
    present_days = [d for d in days if _day_file_exists(project_root, layer=layer, day=d, symbol=symbol, timeframe=canonical_tf)]
    missing_days = [d for d in days if d not in set(present_days)]
    total = len(days)
    present = len(present_days)
    coverage_pct = (100.0 * float(present) / float(total)) if total > 0 else 0.0
    ok = (len(missing_days) == 0) if require_full_coverage else (present > 0)
    return {
        "status": "PASS" if ok else "FAIL",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "params": {
            "symbol": str(symbol),
            "timeframe": canonical_tf,
            "layer": str(layer),
            "start_date": str(start_date),
            "end_date": str(end_date),
            "require_full_coverage": bool(require_full_coverage),
        },
        "summary": {
            "total_days": total,
            "present_days": present,
            "missing_days": len(missing_days),
            "coverage_pct": round(coverage_pct, 3),
        },
        "missing_days": missing_days,
    }


def write_data_window_readiness_report(
    project_root: Path,
    *,
    payload: dict,
    action_name: str,
) -> Path:
    out_dir = project_root / "reports" / "qa_gate"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_action = "".join(ch if (ch.isalnum() or ch in {"_", "-"}) else "_" for ch in str(action_name))
    out_path = out_dir / f"data_window_readiness_{safe_action}_{_utc_tag()}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
