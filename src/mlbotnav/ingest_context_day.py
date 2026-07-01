from __future__ import annotations

import argparse
import json
import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from mlbotnav.audit import audit_event
from mlbotnav.bybit_client import BybitClient, interval_to_oi_interval_time, interval_to_tf, is_oi_supported_interval
from mlbotnav.context_contract import validate_funding_contract, validate_open_interest_contract
from mlbotnav.context_dq import STEP_SECONDS_BY_TF, run_context_dq
from mlbotnav.dq import detect_gap_events_for_step, utc_now_iso
from mlbotnav.ingest_policy import load_ingest_policy
from mlbotnav.meta_store import (
    append_context_dq_report,
    append_gap_events,
    append_ingest_pair_status,
    append_ingest_run,
    upsert_watermark,
)
from mlbotnav.postgres_runtime import is_postgres_mode, pg_upsert_raw_funding, pg_upsert_raw_open_interest
from mlbotnav.settings import load_settings
from mlbotnav.storage_registry import ensure_storage_layout, register_partition


def _day_window_utc(day: str) -> tuple[datetime, datetime]:
    start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def _default_day_utc() -> str:
    now = datetime.now(timezone.utc)
    return (now - timedelta(days=1)).strftime("%Y-%m-%d")


def _fetch_with_retry(fetch_fn, *, retry_max: int, retry_backoff_base_sec: float, retry_jitter_sec: float):
    last_error: Exception | None = None
    for attempt in range(1, retry_max + 1):
        try:
            return fetch_fn()
        except Exception as e:  # noqa: BLE001
            last_error = e
            if attempt >= retry_max:
                break
            backoff = retry_backoff_base_sec * (2 ** (attempt - 1))
            jitter = random.uniform(0.0, retry_jitter_sec)
            time.sleep(backoff + jitter)
    raise RuntimeError(f"context_fetch_failed retries={retry_max}: {last_error}") from last_error


def _release_status(*, dq_status: str, contract_ok: bool) -> str:
    if dq_status == "FAIL" or not contract_ok:
        return "FAIL"
    if dq_status == "WARN":
        return "WARN"
    return "PASS"


def _save_day_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest one UTC day of Bybit market context (funding + open interest).")
    parser.add_argument("--date", default=_default_day_utc(), help="UTC day YYYY-MM-DD")
    parser.add_argument("--symbol", default=None, help="Symbol, e.g. SOLUSDT")
    parser.add_argument("--timeframes", default=None, help="CSV intervals for open interest: 1,5,15,30,60,240,D")
    args = parser.parse_args()

    settings = load_settings()
    symbol = args.symbol or settings.symbol
    intervals = [x.strip() for x in (args.timeframes or ",".join(settings.timeframes)).split(",") if x.strip()]
    oi_intervals = [i for i in intervals if is_oi_supported_interval(i)]
    skipped_oi_intervals = [i for i in intervals if i not in oi_intervals]

    project_root = Path(__file__).resolve().parents[2]
    ensure_storage_layout(project_root)
    policy = load_ingest_policy(project_root)
    client = BybitClient(base_url=settings.bybit_base_url)

    run_id = str(uuid.uuid4())
    run_started = utc_now_iso()
    start_dt, end_dt = _day_window_utc(args.date)
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    is_current_day = args.date == datetime.now(timezone.utc).strftime("%Y-%m-%d")

    meta_root = project_root / "data" / "meta"
    dq_root = project_root / "data" / "dq"

    rows_read = 0
    rows_written = 0
    rows_rejected = 0
    pair_errors = 0

    # Funding (8h)
    funding_started = utc_now_iso()
    funding_tf = "8h"
    try:
        funding_rows = _fetch_with_retry(
            lambda: client.get_funding_history(
                category=settings.bybit_category,
                symbol=symbol,
                start_ms=start_ms,
                end_ms=end_ms,
                limit=200,
            ),
            retry_max=policy.retry_max,
            retry_backoff_base_sec=policy.retry_backoff_base_sec,
            retry_jitter_sec=policy.retry_jitter_sec,
        )
        rows_read += len(funding_rows)
        src_ts = utc_now_iso()
        funding_df = pd.DataFrame(
            [
                {
                    "exchange": "bybit_funding",
                    "market_type": settings.bybit_category,
                    "symbol": symbol,
                    "timeframe": funding_tf,
                    "event_time_utc": datetime.fromtimestamp(int(r["fundingRateTimestamp"]) / 1000, tz=timezone.utc).isoformat(),
                    "funding_rate": float(r["fundingRate"]),
                    "ingest_run_id": run_id,
                    "source_ts_utc": src_ts,
                }
                for r in funding_rows
            ],
            columns=[
                "exchange",
                "market_type",
                "symbol",
                "timeframe",
                "event_time_utc",
                "funding_rate",
                "ingest_run_id",
                "source_ts_utc",
            ],
        )
        contract = validate_funding_contract(
            funding_df,
            expected_symbol=symbol,
            expected_market_type=settings.bybit_category,
            expected_trade_date_utc=args.date,
        )
        funding_df = contract.clean_df
        rows_rejected += int(contract.dropped_rows)
        dq = run_context_dq(
            funding_df,
            timeframe=funding_tf,
            time_col="event_time_utc",
            value_col="funding_rate",
            is_current_day=is_current_day,
        )
        funding_gap_events = detect_gap_events_for_step(
            funding_df,
            time_col="event_time_utc",
            step_seconds=int(STEP_SECONDS_BY_TF[funding_tf]),
        )
        release = _release_status(dq_status=dq.status, contract_ok=contract.is_valid)
        if is_postgres_mode(project_root):
            pg_upsert_raw_funding(project_root, funding_df)

        raw_path = (
            project_root / "data" / "raw" / "bybit_funding" / f"dt={args.date}" / f"symbol={symbol}" / "part-final.csv"
        )
        _save_day_csv(raw_path, funding_df)
        register_partition(
            project_root,
            layer="raw",
            dataset="bybit_funding",
            trade_date_utc=args.date,
            symbol=symbol,
            timeframe=funding_tf,
            file_path=raw_path,
            rows=len(funding_df),
            run_id=run_id,
            status="written",
        )
        rows_written += int(len(funding_df))
        append_context_dq_report(
            dq_root,
            {
                "run_id": run_id,
                "dataset": "funding",
                "symbol": symbol,
                "timeframe": funding_tf,
                "trade_date_utc": args.date,
                "expected_rows": dq.expected_rows,
                "actual_rows": dq.actual_rows,
                "completeness_pct": dq.completeness_pct,
                "duplicate_rows": dq.duplicate_rows,
                "invalid_rows": dq.invalid_rows,
                "gap_count": dq.gap_count,
                "status": dq.status,
                "contract_status": "PASS" if contract.is_valid else "FAIL",
                "release_status": release,
                "created_at_utc": utc_now_iso(),
            },
        )
        append_gap_events(
            dq_root,
            [
                {
                    "run_id": run_id,
                    "dataset": "bybit_funding",
                    "symbol": symbol,
                    "timeframe": funding_tf,
                    "trade_date_utc": args.date,
                    "expected_open_time_utc": ts,
                    "created_at_utc": utc_now_iso(),
                }
                for ts in funding_gap_events
            ],
        )

        if release in {"PASS", "WARN"}:
            core_path = (
                project_root / "data" / "core" / "bybit_funding" / f"dt={args.date}" / f"symbol={symbol}" / "part-final.csv"
            )
            _save_day_csv(core_path, funding_df)
            register_partition(
                project_root,
                layer="core",
                dataset="bybit_funding",
                trade_date_utc=args.date,
                symbol=symbol,
                timeframe=funding_tf,
                file_path=core_path,
                rows=len(funding_df),
                run_id=run_id,
                status="released",
            )
            last_ts = pd.to_datetime(funding_df["event_time_utc"], utc=True).max()
            upsert_watermark(
                meta_root,
                {
                    "exchange": "bybit_funding",
                    "market_type": settings.bybit_category,
                    "symbol": symbol,
                    "timeframe": funding_tf,
                    "last_loaded_open_time_utc": last_ts.isoformat(),
                    "last_success_run_id": run_id,
                    "updated_at_utc": utc_now_iso(),
                },
            )
        else:
            pair_errors += 1
        append_ingest_pair_status(
            meta_root,
            {
                "run_id": run_id,
                "date": args.date,
                "symbol": symbol,
                "timeframe": funding_tf,
                "status": "success" if release in {"PASS", "WARN"} else "failed",
                "rows_read": int(len(funding_rows)),
                "rows_written": int(len(funding_df) if release in {"PASS", "WARN"} else 0),
                "rows_rejected": int(contract.dropped_rows),
                "error_text": "" if release in {"PASS", "WARN"} else f"release_status={release}",
                "started_at_utc": funding_started,
                "ended_at_utc": utc_now_iso(),
            },
        )
    except Exception as e:  # noqa: BLE001
        pair_errors += 1
        append_ingest_pair_status(
            meta_root,
            {
                "run_id": run_id,
                "date": args.date,
                "symbol": symbol,
                "timeframe": funding_tf,
                "status": "failed",
                "rows_read": 0,
                "rows_written": 0,
                "rows_rejected": 0,
                "error_text": str(e),
                "started_at_utc": funding_started,
                "ended_at_utc": utc_now_iso(),
            },
        )

    # Open interest for configured supported intervals.
    for interval in oi_intervals:
        tf = interval_to_tf(interval)
        oi_started = utc_now_iso()
        try:
            interval_time = interval_to_oi_interval_time(interval)
            oi_rows = _fetch_with_retry(
                lambda: client.get_open_interest(
                    category=settings.bybit_category,
                    symbol=symbol,
                    interval_time=interval_time,
                    start_ms=start_ms,
                    end_ms=end_ms,
                    limit=200,
                ),
                retry_max=policy.retry_max,
                retry_backoff_base_sec=policy.retry_backoff_base_sec,
                retry_jitter_sec=policy.retry_jitter_sec,
            )
            rows_read += len(oi_rows)
            src_ts = utc_now_iso()
            oi_df = pd.DataFrame(
                [
                    {
                        "exchange": "bybit_open_interest",
                        "market_type": settings.bybit_category,
                        "symbol": symbol,
                        "timeframe": tf,
                        "open_time_utc": datetime.fromtimestamp(int(r["timestamp"]) / 1000, tz=timezone.utc).isoformat(),
                        "open_interest": float(r["openInterest"]),
                        "ingest_run_id": run_id,
                        "source_ts_utc": src_ts,
                    }
                    for r in oi_rows
                ],
                columns=[
                    "exchange",
                    "market_type",
                    "symbol",
                    "timeframe",
                    "open_time_utc",
                    "open_interest",
                    "ingest_run_id",
                    "source_ts_utc",
                ],
            )

            contract = validate_open_interest_contract(
                oi_df,
                expected_symbol=symbol,
                expected_timeframe=tf,
                expected_market_type=settings.bybit_category,
                expected_trade_date_utc=args.date,
            )
            oi_df = contract.clean_df
            rows_rejected += int(contract.dropped_rows)
            dq = run_context_dq(
                oi_df,
                timeframe=tf,
                time_col="open_time_utc",
                value_col="open_interest",
                is_current_day=is_current_day,
            )
            oi_gap_events = detect_gap_events_for_step(
                oi_df,
                time_col="open_time_utc",
                step_seconds=int(STEP_SECONDS_BY_TF[tf]),
            )
            release = _release_status(dq_status=dq.status, contract_ok=contract.is_valid)
            if is_postgres_mode(project_root):
                pg_upsert_raw_open_interest(project_root, oi_df)

            raw_path = (
                project_root
                / "data"
                / "raw"
                / "bybit_open_interest"
                / f"dt={args.date}"
                / f"tf={tf}"
                / f"symbol={symbol}"
                / "part-final.csv"
            )
            _save_day_csv(raw_path, oi_df)
            register_partition(
                project_root,
                layer="raw",
                dataset="bybit_open_interest",
                trade_date_utc=args.date,
                symbol=symbol,
                timeframe=tf,
                file_path=raw_path,
                rows=len(oi_df),
                run_id=run_id,
                status="written",
            )
            rows_written += int(len(oi_df))
            append_context_dq_report(
                dq_root,
                {
                    "run_id": run_id,
                    "dataset": "open_interest",
                    "symbol": symbol,
                    "timeframe": tf,
                    "trade_date_utc": args.date,
                    "expected_rows": dq.expected_rows,
                    "actual_rows": dq.actual_rows,
                    "completeness_pct": dq.completeness_pct,
                    "duplicate_rows": dq.duplicate_rows,
                    "invalid_rows": dq.invalid_rows,
                    "gap_count": dq.gap_count,
                    "status": dq.status,
                    "contract_status": "PASS" if contract.is_valid else "FAIL",
                    "release_status": release,
                    "created_at_utc": utc_now_iso(),
                },
            )
            append_gap_events(
                dq_root,
                [
                    {
                        "run_id": run_id,
                        "dataset": "bybit_open_interest",
                        "symbol": symbol,
                        "timeframe": tf,
                        "trade_date_utc": args.date,
                        "expected_open_time_utc": ts,
                        "created_at_utc": utc_now_iso(),
                    }
                    for ts in oi_gap_events
                ],
            )

            if release in {"PASS", "WARN"}:
                core_path = (
                    project_root
                    / "data"
                    / "core"
                    / "bybit_open_interest"
                    / f"dt={args.date}"
                    / f"tf={tf}"
                    / f"symbol={symbol}"
                    / "part-final.csv"
                )
                _save_day_csv(core_path, oi_df)
                register_partition(
                    project_root,
                    layer="core",
                    dataset="bybit_open_interest",
                    trade_date_utc=args.date,
                    symbol=symbol,
                    timeframe=tf,
                    file_path=core_path,
                    rows=len(oi_df),
                    run_id=run_id,
                    status="released",
                )
                last_ts = pd.to_datetime(oi_df["open_time_utc"], utc=True).max()
                upsert_watermark(
                    meta_root,
                    {
                        "exchange": "bybit_open_interest",
                        "market_type": settings.bybit_category,
                        "symbol": symbol,
                        "timeframe": tf,
                        "last_loaded_open_time_utc": last_ts.isoformat(),
                        "last_success_run_id": run_id,
                        "updated_at_utc": utc_now_iso(),
                    },
                )
            else:
                pair_errors += 1
            append_ingest_pair_status(
                meta_root,
                {
                    "run_id": run_id,
                    "date": args.date,
                    "symbol": symbol,
                    "timeframe": tf,
                    "status": "success" if release in {"PASS", "WARN"} else "failed",
                    "rows_read": int(len(oi_rows)),
                    "rows_written": int(len(oi_df) if release in {"PASS", "WARN"} else 0),
                    "rows_rejected": int(contract.dropped_rows),
                    "error_text": "" if release in {"PASS", "WARN"} else f"release_status={release}",
                    "started_at_utc": oi_started,
                    "ended_at_utc": utc_now_iso(),
                },
            )
        except Exception as e:  # noqa: BLE001
            pair_errors += 1
            append_ingest_pair_status(
                meta_root,
                {
                    "run_id": run_id,
                    "date": args.date,
                    "symbol": symbol,
                    "timeframe": tf,
                    "status": "failed",
                    "rows_read": 0,
                    "rows_written": 0,
                    "rows_rejected": 0,
                    "error_text": str(e),
                    "started_at_utc": oi_started,
                    "ended_at_utc": utc_now_iso(),
                },
            )

    for skipped in skipped_oi_intervals:
        append_ingest_pair_status(
            meta_root,
            {
                "run_id": run_id,
                "date": args.date,
                "symbol": symbol,
                "timeframe": interval_to_tf(skipped),
                "status": "skipped",
                "rows_read": 0,
                "rows_written": 0,
                "rows_rejected": 0,
                "error_text": "unsupported_open_interest_interval",
                "started_at_utc": run_started,
                "ended_at_utc": utc_now_iso(),
            },
        )

    run_ended = utc_now_iso()
    append_ingest_run(
        meta_root,
        {
            "run_id": run_id,
            "started_at_utc": run_started,
            "ended_at_utc": run_ended,
            "status": "partial_success" if pair_errors > 0 else "success",
            "rows_read": rows_read,
            "rows_written": rows_written,
            "rows_upserted": rows_written,
            "rows_rejected": rows_rejected,
            "error_text": f"failed_pairs={pair_errors}",
        },
    )
    audit_event(
        project_root,
        event="ingest_context_day_completed",
        payload={
            "date": args.date,
            "symbol": symbol,
            "run_id": run_id,
            "rows_read": rows_read,
            "rows_written": rows_written,
            "rows_rejected": rows_rejected,
            "pair_errors": pair_errors,
        },
    )
    print(
        json.dumps(
            {
                "run_id": run_id,
                "date": args.date,
                "symbol": symbol,
                "status": "partial_success" if pair_errors > 0 else "success",
                "rows_read": rows_read,
                "rows_written": rows_written,
                "rows_rejected": rows_rejected,
                "pair_errors": pair_errors,
                "skipped_oi_intervals": skipped_oi_intervals,
            }
        )
    )
    return 0 if pair_errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
