from __future__ import annotations

import argparse
import logging
import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from mlbotnav.audit import audit_event
from mlbotnav.bybit_client import BybitClient, interval_to_tf
from mlbotnav.data_contract import CONTRACT_VERSION, validate_ohlcv_contract
from mlbotnav.dq import detect_gap_events, run_ohlcv_dq, utc_now_iso
from mlbotnav.governance import quarantine_day
from mlbotnav.ingest_policy import load_ingest_policy
from mlbotnav.meta_store import append_dq_report, append_gap_events, append_ingest_pair_status, append_ingest_run, upsert_watermark
from mlbotnav.postgres_runtime import is_postgres_mode, pg_upsert_raw_ohlcv
from mlbotnav.settings import load_settings
from mlbotnav.storage_registry import ensure_storage_layout, register_partition
from mlbotnav.timeframes import timeframe_delta


def _day_window_utc(day: str) -> tuple[datetime, datetime]:
    start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def _default_day_utc() -> str:
    now = datetime.now(timezone.utc)
    return (now - timedelta(days=1)).strftime("%Y-%m-%d")


def _make_logger(project_root: Path, day: str) -> tuple[logging.Logger, Path]:
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = logs_dir / f"ingest_day_{day}_{ts}.log"

    logger = logging.getLogger("ingest_day")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)sZ | %(levelname)s | %(message)s", "%Y-%m-%dT%H:%M:%S")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger, log_path


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest one UTC day of Bybit OHLCV")
    parser.add_argument("--date", default=_default_day_utc(), help="UTC day YYYY-MM-DD (default: yesterday UTC)")
    parser.add_argument("--symbol", default=None, help="Symbol, e.g. SOLUSDT")
    parser.add_argument("--timeframes", default=None, help="CSV intervals: 1,5,15,30,60,240,D")
    args = parser.parse_args()

    settings = load_settings()
    symbol = args.symbol or settings.symbol
    intervals = [x.strip() for x in (args.timeframes or ",".join(settings.timeframes)).split(",") if x.strip()]

    project_root = Path(__file__).resolve().parents[2]
    ensure_storage_layout(project_root)
    policy = load_ingest_policy(project_root)
    logger, log_path = _make_logger(project_root, args.date)
    logger.info("Start ingest day=%s symbol=%s intervals=%s", args.date, symbol, intervals)
    logger.info("Tunnel source env: %s", settings.source_env_path or "not set")

    if not settings.bybit_api_key or not settings.bybit_api_secret:
        logger.error("Bybit credentials are empty. Check SOURCE_ENV_PATH/.env.")
        return 2

    start_dt, end_dt = _day_window_utc(args.date)
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)

    client = BybitClient(base_url=settings.bybit_base_url)
    total_rows = 0
    rows_rejected = 0
    pair_errors = 0
    run_id = str(uuid.uuid4())
    run_started = utc_now_iso()
    meta_root = project_root / "data" / "meta"
    dq_root = project_root / "data" / "dq"

    for interval in intervals:
        tf = interval_to_tf(interval)
        pair_started = utc_now_iso()
        rows = []
        fetch_error = ""
        try:
            rows = _fetch_with_retry(
                client=client,
                category=settings.bybit_category,
                symbol=symbol,
                interval=interval,
                start_ms=start_ms,
                end_ms=end_ms,
                retry_max=policy.retry_max,
                retry_backoff_base_sec=policy.retry_backoff_base_sec,
                retry_jitter_sec=policy.retry_jitter_sec,
            )
        except Exception as e:  # noqa: BLE001
            fetch_error = str(e)
            pair_errors += 1
            logger.exception("Fetch failed interval=%s tf=%s", interval, tf)
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
                    "error_text": fetch_error,
                    "started_at_utc": pair_started,
                    "ended_at_utc": utc_now_iso(),
                },
            )
            continue

        if not rows:
            logger.warning("No rows for interval=%s", interval)
            append_ingest_pair_status(
                meta_root,
                {
                    "run_id": run_id,
                    "date": args.date,
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
        source_ts = utc_now_iso()
        for r in rows:
            open_ms = int(r[0])
            open_ts = datetime.fromtimestamp(open_ms / 1000, tz=timezone.utc)
            close_ts = open_ts + _tf_delta(tf)
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
                    "source_ts_utc": source_ts,
                }
            )

        df = pd.DataFrame(out).sort_values("open_time_utc")
        contract = validate_ohlcv_contract(
            df,
            expected_symbol=symbol,
            expected_timeframe=tf,
            expected_market_type=settings.bybit_category,
            expected_exchange="bybit",
            expected_trade_date_utc=args.date,
        )
        df = contract.clean_df
        before = len(df)
        df = df.drop_duplicates(subset=["exchange", "market_type", "symbol", "timeframe", "open_time_utc"])
        rows_rejected += before - len(df)
        rows_rejected += contract.dropped_rows

        dq = run_ohlcv_dq(
            df,
            timeframe=tf,
            is_current_day=(args.date == datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        )
        gap_events = detect_gap_events(df, timeframe=tf, time_col="open_time_utc")
        if is_postgres_mode(project_root):
            pg_upsert_raw_ohlcv(project_root, df)
        raw_out_dir = (
            project_root
            / "data"
            / "raw"
            / "bybit_ohlcv"
            / f"dt={args.date}"
            / f"tf={tf}"
            / f"symbol={symbol}"
        )
        raw_out_dir.mkdir(parents=True, exist_ok=True)
        raw_out_path = raw_out_dir / "part-final.csv"
        df.to_csv(raw_out_path, index=False)
        register_partition(
            project_root,
            layer="raw",
            dataset="bybit_ohlcv",
            trade_date_utc=args.date,
            symbol=symbol,
            timeframe=tf,
            file_path=raw_out_path,
            rows=len(df),
            run_id=run_id,
            status="written",
        )

        total_rows += len(df)
        contract_status = "PASS" if contract.is_valid else "FAIL"
        logger.info(
            "Saved interval=%s tf=%s rows=%s dq_status=%s contract_status=%s completeness=%.3f%% raw_path=%s",
            interval,
            tf,
            len(df),
            dq.status,
            contract_status,
            dq.completeness_pct,
            raw_out_path,
        )

        release_status = "PASS"
        if dq.status == "FAIL" or contract_status == "FAIL":
            release_status = "FAIL"
        elif dq.status == "WARN":
            release_status = "WARN"

        if release_status != "FAIL":
            core_out_dir = (
                project_root
                / "data"
                / "core"
                / "bybit_ohlcv"
                / f"dt={args.date}"
                / f"tf={tf}"
                / f"symbol={symbol}"
            )
            core_out_dir.mkdir(parents=True, exist_ok=True)
            core_out_path = core_out_dir / "part-final.csv"
            df.to_csv(core_out_path, index=False)
            register_partition(
                project_root,
                layer="core",
                dataset="bybit_ohlcv",
                trade_date_utc=args.date,
                symbol=symbol,
                timeframe=tf,
                file_path=core_out_path,
                rows=len(df),
                run_id=run_id,
                status=release_status,
            )
            upsert_watermark(
                meta_root,
                {
                    "exchange": "bybit",
                    "market_type": settings.bybit_category,
                    "symbol": symbol,
                    "timeframe": tf,
                    "last_loaded_open_time_utc": df["open_time_utc"].max(),
                    "last_success_run_id": run_id,
                    "updated_at_utc": utc_now_iso(),
                },
            )

        append_dq_report(
            dq_root,
            {
                "run_id": run_id,
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
                    "trade_date_utc": args.date,
                    "expected_open_time_utc": ts,
                    "created_at_utc": utc_now_iso(),
                }
                for ts in gap_events
            ],
        )

        if release_status == "FAIL":
            pair_errors += 1
            q = quarantine_day(
                project_root,
                date=args.date,
                symbol=symbol,
                timeframe=tf,
                reason="dq_or_contract_fail",
            )
            audit_event(
                project_root,
                event="ingest_day_quarantined",
                payload={
                    "run_id": run_id,
                    "date": args.date,
                    "symbol": symbol,
                    "timeframe": tf,
                    "dq_status": dq.status,
                    "contract_status": contract_status,
                    "contract_violations": contract.violations,
                    "quarantine": q,
                },
            )
            q_dst = q.get("dst")
            if isinstance(q_dst, str):
                register_partition(
                    project_root,
                    layer="quarantine",
                    dataset="bybit_ohlcv",
                    trade_date_utc=args.date,
                    symbol=symbol,
                    timeframe=tf,
                    file_path=Path(q_dst),
                    rows=len(df),
                    run_id=run_id,
                    status="quarantined",
                )

        append_ingest_pair_status(
            meta_root,
            {
                "run_id": run_id,
                "date": args.date,
                "symbol": symbol,
                "timeframe": tf,
                "status": "success" if release_status != "FAIL" else "failed",
                "rows_read": len(rows),
                "rows_written": len(df) if release_status != "FAIL" else 0,
                "rows_rejected": int(contract.dropped_rows + (before - len(df))),
                "error_text": "" if release_status != "FAIL" else f"release_status={release_status}",
                "started_at_utc": pair_started,
                "ended_at_utc": utc_now_iso(),
            },
        )

    run_ended = utc_now_iso()
    append_ingest_run(
        project_root / "data" / "meta",
        {
            "run_id": run_id,
            "started_at_utc": run_started,
            "ended_at_utc": run_ended,
            "status": "partial_success" if pair_errors > 0 else "success",
            "rows_read": total_rows + rows_rejected,
            "rows_written": total_rows,
            "rows_upserted": total_rows,
            "rows_rejected": rows_rejected,
            "error_text": "" if pair_errors == 0 else f"failed_pairs={pair_errors}",
        },
    )
    audit_event(
        project_root,
        event="ingest_day_completed",
        payload={"run_id": run_id, "date": args.date, "symbol": symbol, "total_rows": total_rows, "rows_rejected": rows_rejected},
    )
    logger.info("Done day=%s total_rows=%s run_id=%s log=%s", args.date, total_rows, run_id, log_path)
    return 0


def _tf_delta(tf: str) -> timedelta:
    return timeframe_delta(tf)


if __name__ == "__main__":
    raise SystemExit(main())
