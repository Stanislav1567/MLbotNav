from __future__ import annotations

import argparse
import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from mlbotnav.bybit_client import BybitClient, interval_to_tf
from mlbotnav.data_contract import CONTRACT_VERSION, validate_ohlcv_contract
from mlbotnav.dq import detect_gap_events, run_ohlcv_dq, utc_now_iso
from mlbotnav.governance import quarantine_day
from mlbotnav.ingest_policy import load_ingest_policy
from mlbotnav.meta_store import (
    append_dq_report,
    append_gap_events,
    append_ingest_pair_status,
    append_ingest_run,
    get_watermark,
    upsert_watermark,
)
from mlbotnav.settings import load_settings
from mlbotnav.storage_registry import ensure_storage_layout, register_partition
from mlbotnav.timeframes import canonical_timeframe, timeframe_aliases, timeframe_delta


def _tf_delta(tf: str) -> timedelta:
    return timeframe_delta(tf)


def _floor_to_closed_candle(now_utc: datetime, tf: str) -> datetime:
    t = canonical_timeframe(tf)
    if t == "1d":
        return now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    if t.endswith("h"):
        hrs = int(t[:-1])
        floored_hour = (now_utc.hour // hrs) * hrs
        return now_utc.replace(hour=floored_hour, minute=0, second=0, microsecond=0)
    mins = int(t[:-1])
    floored_minute = (now_utc.minute // mins) * mins
    return now_utc.replace(minute=floored_minute, second=0, microsecond=0)


def _fetch_with_retry(
    *,
    client: BybitClient,
    category: str,
    symbol: str,
    interval: str,
    start_ms: int,
    end_ms: int,
    retry_max: int,
    retry_backoff_base_sec: float,
    retry_jitter_sec: float,
) -> list[list[str]]:
    last_error: Exception | None = None
    for attempt in range(1, retry_max + 1):
        try:
            return client.get_klines(
                category=category,
                symbol=symbol,
                interval=interval,
                start_ms=start_ms,
                end_ms=end_ms,
            )
        except Exception as e:  # noqa: BLE001
            last_error = e
            if attempt >= retry_max:
                break
            backoff = retry_backoff_base_sec * (2 ** (attempt - 1))
            jitter = random.uniform(0.0, retry_jitter_sec)
            time.sleep(backoff + jitter)
    raise RuntimeError(f"fetch_failed interval={interval} retries={retry_max}: {last_error}") from last_error


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Incremental Bybit ingestion using watermark.")
    parser.add_argument("--symbol", default=None, help="Symbol, e.g. SOLUSDT")
    parser.add_argument("--timeframes", default=None, help="CSV intervals: 1,5,15,30,60,240,D")
    parser.add_argument("--lookback-days", type=int, default=3, help="Reconcile last N days (late data policy)")
    args = parser.parse_args()

    settings = load_settings()
    symbol = args.symbol or settings.symbol
    intervals = [x.strip() for x in (args.timeframes or ",".join(settings.timeframes)).split(",") if x.strip()]
    project_root = Path(__file__).resolve().parents[2]
    ensure_storage_layout(project_root)
    policy = load_ingest_policy(project_root)
    client = BybitClient(base_url=settings.bybit_base_url)
    meta_root = project_root / "data" / "meta"
    dq_root = project_root / "data" / "dq"

    run_id = str(uuid.uuid4())
    run_started = utc_now_iso()
    rows_written = 0
    rows_read = 0
    rows_rejected = 0
    pair_errors = 0

    now_utc = datetime.now(timezone.utc)
    run_date_utc = now_utc.strftime("%Y-%m-%d")
    for interval in intervals:
        tf = interval_to_tf(interval)
        pair_started = utc_now_iso()
        step = _tf_delta(tf)
        watermark_iso = _get_watermark_any(
            meta_root,
            exchange="bybit",
            market_type=settings.bybit_category,
            symbol=symbol,
            timeframe=tf,
        )

        if watermark_iso:
            from_dt = datetime.fromisoformat(watermark_iso) + step
        else:
            from_dt = now_utc - timedelta(days=policy.late_data_reconcile_days)
            if tf == "1d":
                from_dt = from_dt.replace(hour=0, minute=0, second=0, microsecond=0)

        reconcile_from = now_utc - timedelta(days=max(args.lookback_days, policy.late_data_reconcile_days))
        if from_dt > reconcile_from:
            from_dt = reconcile_from

        to_dt = _floor_to_closed_candle(now_utc, tf)
        if from_dt >= to_dt:
            continue

        try:
            rows = _fetch_with_retry(
                client=client,
                category=settings.bybit_category,
                symbol=symbol,
                interval=interval,
                start_ms=int(from_dt.timestamp() * 1000),
                end_ms=int(to_dt.timestamp() * 1000),
                retry_max=policy.retry_max,
                retry_backoff_base_sec=policy.retry_backoff_base_sec,
                retry_jitter_sec=policy.retry_jitter_sec,
            )
        except Exception as e:  # noqa: BLE001
            pair_errors += 1
            append_ingest_pair_status(
                meta_root,
                {
                    "run_id": run_id,
                    "date": run_date_utc,
                    "symbol": symbol,
                    "timeframe": tf,
                    "status": "failed",
                    "rows_read": 0,
                    "rows_written": 0,
                    "rows_rejected": 0,
                    "error_text": str(e),
                    "started_at_utc": pair_started,
                    "ended_at_utc": utc_now_iso(),
                },
            )
            continue

        rows_read += len(rows)
        if not rows:
            append_ingest_pair_status(
                meta_root,
                {
                    "run_id": run_id,
                    "date": run_date_utc,
                    "symbol": symbol,
                    "timeframe": tf,
                    "status": "success",
                    "rows_read": 0,
                    "rows_written": 0,
                    "rows_rejected": 0,
                    "error_text": "",
                    "started_at_utc": pair_started,
                    "ended_at_utc": utc_now_iso(),
                },
            )
            continue

        out = []
        for r in rows:
            open_ts = datetime.fromtimestamp(int(r[0]) / 1000, tz=timezone.utc)
            close_ts = open_ts + step
            out.append(
                {
                    "exchange": "bybit",
                    "market_type": settings.bybit_category,
                    "symbol": symbol,
                    "timeframe": tf,
                    "open_time_utc": open_ts.isoformat(),
                    "close_time_utc": close_ts.isoformat(),
                    "open": float(r[1]),
                    "high": float(r[2]),
                    "low": float(r[3]),
                    "close": float(r[4]),
                    "volume": float(r[5]),
                    "turnover": float(r[6]),
                    "ingest_run_id": run_id,
                    "source_ts_utc": utc_now_iso(),
                }
            )

        df_new = pd.DataFrame(out).drop_duplicates(subset=["open_time_utc"]).sort_values("open_time_utc")
        pair_written = 0
        pair_rejected = 0
        pair_failed_days = 0
        for trade_date, day_df in df_new.groupby(pd.to_datetime(df_new["open_time_utc"], utc=True).dt.strftime("%Y-%m-%d")):
            contract = validate_ohlcv_contract(
                day_df,
                expected_symbol=symbol,
                expected_timeframe=tf,
                expected_market_type=settings.bybit_category,
                expected_exchange="bybit",
                expected_trade_date_utc=str(trade_date),
            )
            day_df = contract.clean_df
            pair_rejected += contract.dropped_rows
            dq = run_ohlcv_dq(
                day_df,
                timeframe=tf,
                is_current_day=(str(trade_date) == datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            )
            gap_events = detect_gap_events(day_df, timeframe=tf, time_col="open_time_utc")
            contract_status = "PASS" if contract.is_valid else "FAIL"
            release_status = "PASS"
            if dq.status == "FAIL" or contract_status == "FAIL":
                release_status = "FAIL"
            elif dq.status == "WARN":
                release_status = "WARN"

            raw_out_dir = (
                project_root
                / "data"
                / "raw"
                / "bybit_ohlcv"
                / f"dt={trade_date}"
                / f"tf={tf}"
                / f"symbol={symbol}"
            )
            raw_out_dir.mkdir(parents=True, exist_ok=True)
            raw_out_path = raw_out_dir / "part-final.csv"

            if raw_out_path.exists():
                old = pd.read_csv(raw_out_path)
                merged = pd.concat([old, day_df], ignore_index=True)
                merged = merged.drop_duplicates(subset=["exchange", "market_type", "symbol", "timeframe", "open_time_utc"])
                merged = merged.sort_values("open_time_utc").reset_index(drop=True)
            else:
                merged = day_df.reset_index(drop=True)

            merged.to_csv(raw_out_path, index=False)
            register_partition(
                project_root,
                layer="raw",
                dataset="bybit_ohlcv",
                trade_date_utc=str(trade_date),
                symbol=symbol,
                timeframe=tf,
                file_path=raw_out_path,
                rows=len(merged),
                run_id=run_id,
                status="written",
            )

            append_dq_report(
                dq_root,
                {
                    "run_id": run_id,
                    "symbol": symbol,
                    "timeframe": tf,
                    "trade_date_utc": str(trade_date),
                    "expected_rows": dq.expected_rows,
                    "actual_rows": dq.actual_rows,
                    "completeness_pct": dq.completeness_pct,
                    "duplicate_rows": dq.duplicate_rows,
                    "invalid_rows": dq.invalid_rows,
                    "gap_count": dq.gap_count,
                    "status": dq.status,
                    "contract_version": CONTRACT_VERSION,
                    "contract_status": contract_status,
                    "contract_violations": "|".join(contract.violations),
                    "release_status": release_status,
                    "created_at_utc": utc_now_iso(),
                },
            )
            append_gap_events(
                dq_root,
                [
                    {
                        "run_id": run_id,
                        "dataset": "bybit_ohlcv",
                        "symbol": symbol,
                        "timeframe": tf,
                        "trade_date_utc": str(trade_date),
                        "expected_open_time_utc": ts,
                        "created_at_utc": utc_now_iso(),
                    }
                    for ts in gap_events
                ],
            )

            if release_status == "FAIL":
                pair_failed_days += 1
                pair_errors += 1
                quarantine_day(
                    # quarantine contains snapshot for failed contract/day
                    project_root,
                    date=str(trade_date),
                    symbol=symbol,
                    timeframe=tf,
                    reason="dq_or_contract_fail",
                )
                q_path = (
                    project_root
                    / "data"
                    / "quarantine"
                    / "bybit_ohlcv"
                    / f"dt={trade_date}"
                    / f"tf={tf}"
                    / f"symbol={symbol}"
                    / "part-final.csv"
                )
                if q_path.exists():
                    register_partition(
                        project_root,
                        layer="quarantine",
                        dataset="bybit_ohlcv",
                        trade_date_utc=str(trade_date),
                        symbol=symbol,
                        timeframe=tf,
                        file_path=q_path,
                        rows=len(day_df),
                        run_id=run_id,
                        status="quarantined",
                    )
                continue

            core_out_dir = (
                project_root
                / "data"
                / "core"
                / "bybit_ohlcv"
                / f"dt={trade_date}"
                / f"tf={tf}"
                / f"symbol={symbol}"
            )
            core_out_dir.mkdir(parents=True, exist_ok=True)
            core_out_path = core_out_dir / "part-final.csv"
            if core_out_path.exists():
                core_old = pd.read_csv(core_out_path)
                core_merged = pd.concat([core_old, day_df], ignore_index=True)
                core_merged = core_merged.drop_duplicates(subset=["exchange", "market_type", "symbol", "timeframe", "open_time_utc"])
                core_merged = core_merged.sort_values("open_time_utc").reset_index(drop=True)
            else:
                core_merged = day_df.reset_index(drop=True)
            core_merged.to_csv(core_out_path, index=False)
            register_partition(
                project_root,
                layer="core",
                dataset="bybit_ohlcv",
                trade_date_utc=str(trade_date),
                symbol=symbol,
                timeframe=tf,
                file_path=core_out_path,
                rows=len(core_merged),
                run_id=run_id,
                status=release_status,
            )
            pair_written += len(day_df)
            rows_written += len(day_df)

        upsert_watermark(
            meta_root,
            {
                "exchange": "bybit",
                "market_type": settings.bybit_category,
                "symbol": symbol,
                "timeframe": tf,
                "last_loaded_open_time_utc": df_new["open_time_utc"].max(),
                "last_success_run_id": run_id,
                "updated_at_utc": utc_now_iso(),
            },
        )
        rows_rejected += pair_rejected
        append_ingest_pair_status(
            meta_root,
            {
                "run_id": run_id,
                "date": run_date_utc,
                "symbol": symbol,
                "timeframe": tf,
                "status": "partial_success" if pair_failed_days > 0 else "success",
                "rows_read": len(rows),
                "rows_written": pair_written,
                "rows_rejected": pair_rejected,
                "error_text": "" if pair_failed_days == 0 else f"failed_days={pair_failed_days}",
                "started_at_utc": pair_started,
                "ended_at_utc": utc_now_iso(),
            },
        )

    append_ingest_run(
        meta_root,
        {
            "run_id": run_id,
            "started_at_utc": run_started,
            "ended_at_utc": utc_now_iso(),
            "status": "partial_success" if pair_errors > 0 else "success",
            "rows_read": rows_read,
            "rows_written": rows_written,
            "rows_upserted": rows_written,
            "rows_rejected": rows_rejected,
            "error_text": "" if pair_errors == 0 else f"failed_pairs_or_days={pair_errors}",
        },
    )
    print({"run_id": run_id, "rows_read": rows_read, "rows_written": rows_written, "rows_rejected": rows_rejected, "pair_errors": pair_errors})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
