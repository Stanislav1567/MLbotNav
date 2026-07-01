from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlbotnav.bybit_client import interval_to_tf, is_oi_supported_interval
from mlbotnav.meta_store import get_watermark
from mlbotnav.settings import load_settings
from mlbotnav.timeframes import timeframe_aliases, timeframe_delta


def _tf_delta(tf: str) -> timedelta:
    if tf == "8h":
        return timedelta(hours=8)
    return timeframe_delta(tf)


def _get_watermark_any(
    meta_root: Path,
    *,
    exchange: str,
    market_type: str,
    symbol: str,
    timeframe: str,
) -> str | None:
    for tf in timeframe_aliases(timeframe):
        wm = get_watermark(
            meta_root,
            exchange=exchange,
            market_type=market_type,
            symbol=symbol,
            timeframe=tf,
        )
        if wm:
            return wm
    return None


def _days_between(start_dt: datetime, end_dt: datetime) -> list[str]:
    if end_dt <= start_dt:
        return []
    first = start_dt.date()
    last = (end_dt - timedelta(seconds=1)).date()
    out: list[str] = []
    cur = first
    while cur <= last:
        out.append(cur.strftime("%Y-%m-%d"))
        cur = cur + timedelta(days=1)
    return out


def _calc_needed_days(
    *,
    meta_root: Path,
    exchange: str,
    market_type: str,
    symbol: str,
    timeframe: str,
    lookback_days: int,
) -> list[str]:
    now_utc = datetime.now(timezone.utc)
    step = _tf_delta(timeframe)
    watermark_iso = _get_watermark_any(
        meta_root,
        exchange=exchange,
        market_type=market_type,
        symbol=symbol,
        timeframe=timeframe,
    )
    if watermark_iso:
        from_dt = datetime.fromisoformat(str(watermark_iso)) + step
    else:
        from_dt = now_utc - timedelta(days=lookback_days)
    reconcile_from = now_utc - timedelta(days=lookback_days)
    if from_dt > reconcile_from:
        from_dt = reconcile_from
    # Day-batch incremental ingests only fully closed UTC dates.
    to_dt = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    return _days_between(from_dt, to_dt)


def main() -> int:
    parser = argparse.ArgumentParser(description="Incremental ingest for Bybit market context (funding + open interest).")
    parser.add_argument("--symbol", default=None, help="Symbol, e.g. SOLUSDT")
    parser.add_argument("--timeframes", default=None, help="CSV intervals for open interest: 1,5,15,30,60,240,D")
    parser.add_argument("--lookback-days", type=int, default=3, help="Reconcile last N days")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    settings = load_settings()
    symbol = args.symbol or settings.symbol
    intervals = [x.strip() for x in (args.timeframes or ",".join(settings.timeframes)).split(",") if x.strip()]
    oi_intervals = [i for i in intervals if is_oi_supported_interval(i)]
    skipped_oi_intervals = [i for i in intervals if i not in oi_intervals]
    tf_list = [("8h", "bybit_funding")]
    for interval in oi_intervals:
        tf = interval_to_tf(interval)
        tf_list.append((tf, "bybit_open_interest"))

    project_root = Path(__file__).resolve().parents[2]
    meta_root = project_root / "data" / "meta"
    all_days: set[str] = set()
    for tf, ex in tf_list:
        days = _calc_needed_days(
            meta_root=meta_root,
            exchange=ex,
            market_type=settings.bybit_category,
            symbol=symbol,
            timeframe=tf,
            lookback_days=max(1, int(args.lookback_days)),
        )
        all_days.update(days)
    days_sorted = sorted(all_days)

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    ok_days: list[str] = []
    failed_days: list[dict] = []
    for day in days_sorted:
        cmd = [
            sys.executable,
            "-m",
            "mlbotnav.ingest_context_day",
            "--date",
            day,
            "--symbol",
            symbol,
            "--timeframes",
            ",".join(oi_intervals),
        ]
        proc = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
        if proc.returncode == 0:
            ok_days.append(day)
        else:
            failed_days.append({"date": day, "rc": proc.returncode, "stderr_tail": (proc.stderr or "")[-1200:]})
            if not args.continue_on_error:
                break

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "ingestion"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"context_incremental_{symbol}_{ts}.json"
    out = {
        "run_utc": ts,
        "symbol": symbol,
        "timeframes": oi_intervals,
        "skipped_oi_intervals": skipped_oi_intervals,
        "lookback_days": int(args.lookback_days),
        "days_total": len(days_sorted),
        "days_success": len(ok_days),
        "days_failed": len(failed_days),
        "ok_days": ok_days,
        "failed_days": failed_days,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report_path": str(out_path), "days_success": len(ok_days), "days_failed": len(failed_days)}))
    return 0 if not failed_days else 1


if __name__ == "__main__":
    raise SystemExit(main())
