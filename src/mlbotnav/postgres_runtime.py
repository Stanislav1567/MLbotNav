from __future__ import annotations

import os
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class StorageRuntimeConfig:
    mode: str
    postgres_dsn: str


def _load_yaml_config(project_root: Path) -> dict[str, Any]:
    cfg_path = project_root / "configs" / "config.yaml"
    if not cfg_path.exists():
        return {}
    with cfg_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        return {}
    return data


def load_storage_runtime_config(project_root: Path) -> StorageRuntimeConfig:
    load_dotenv(project_root / ".env", override=False)
    cfg = _load_yaml_config(project_root)
    storage_cfg = cfg.get("storage", {}) if isinstance(cfg, dict) else {}
    if not isinstance(storage_cfg, dict):
        storage_cfg = {}

    mode = (os.getenv("STORAGE_MODE", str(storage_cfg.get("mode", "file"))).strip().lower() or "file")
    postgres_dsn = os.getenv("POSTGRES_DSN", str(storage_cfg.get("postgres_dsn", "")).strip()).strip()
    if mode not in {"file", "postgres"}:
        raise RuntimeError(f"Unsupported storage mode: {mode}")
    if mode == "postgres" and not postgres_dsn:
        raise RuntimeError("STORAGE_MODE=postgres requires POSTGRES_DSN")
    return StorageRuntimeConfig(mode=mode, postgres_dsn=postgres_dsn)


def is_postgres_mode(project_root: Path) -> bool:
    return load_storage_runtime_config(project_root).mode == "postgres"


def _connect(project_root: Path):
    cfg = load_storage_runtime_config(project_root)
    if cfg.mode != "postgres":
        raise RuntimeError("PostgreSQL mode is disabled")
    try:
        import psycopg  # type: ignore
    except Exception as e:  # noqa: BLE001
        raise RuntimeError("psycopg is required for STORAGE_MODE=postgres") from e
    return psycopg.connect(cfg.postgres_dsn, autocommit=True)


def ensure_postgres_schema(project_root: Path) -> None:
    ddl_path = project_root / "sql" / "postgres_storage_runtime.sql"
    if not ddl_path.exists():
        raise RuntimeError(f"DDL file not found: {ddl_path}")
    ddl = ddl_path.read_text(encoding="utf-8")
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)


def pg_append_ingest_run(project_root: Path, row: dict[str, Any]) -> None:
    ensure_postgres_schema(project_root)
    sql = """
    INSERT INTO meta.ingest_run (
      run_id, started_at_utc, ended_at_utc, status, rows_read, rows_written, rows_upserted, rows_rejected, error_text
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (run_id) DO UPDATE SET
      started_at_utc = EXCLUDED.started_at_utc,
      ended_at_utc = EXCLUDED.ended_at_utc,
      status = EXCLUDED.status,
      rows_read = EXCLUDED.rows_read,
      rows_written = EXCLUDED.rows_written,
      rows_upserted = EXCLUDED.rows_upserted,
      rows_rejected = EXCLUDED.rows_rejected,
      error_text = EXCLUDED.error_text
    """
    vals = (
        row.get("run_id"),
        row.get("started_at_utc"),
        row.get("ended_at_utc"),
        row.get("status"),
        int(row.get("rows_read", 0) or 0),
        int(row.get("rows_written", 0) or 0),
        int(row.get("rows_upserted", 0) or 0),
        int(row.get("rows_rejected", 0) or 0),
        row.get("error_text"),
    )
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, vals)


def pg_upsert_watermark(project_root: Path, row: dict[str, Any]) -> None:
    ensure_postgres_schema(project_root)
    sql = """
    INSERT INTO meta.ingest_watermark (
      exchange, market_type, symbol, timeframe, last_loaded_open_time_utc, last_success_run_id, updated_at_utc
    ) VALUES (%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (exchange, market_type, symbol, timeframe) DO UPDATE SET
      last_loaded_open_time_utc = EXCLUDED.last_loaded_open_time_utc,
      last_success_run_id = EXCLUDED.last_success_run_id,
      updated_at_utc = EXCLUDED.updated_at_utc
    """
    vals = (
        row.get("exchange"),
        row.get("market_type"),
        row.get("symbol"),
        row.get("timeframe"),
        row.get("last_loaded_open_time_utc"),
        row.get("last_success_run_id"),
        row.get("updated_at_utc"),
    )
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, vals)


def pg_get_watermark(
    project_root: Path,
    *,
    exchange: str,
    market_type: str,
    symbol: str,
    timeframe: str,
) -> str | None:
    ensure_postgres_schema(project_root)
    sql = """
    SELECT last_loaded_open_time_utc
    FROM meta.ingest_watermark
    WHERE exchange=%s AND market_type=%s AND symbol=%s AND timeframe=%s
    ORDER BY updated_at_utc DESC
    LIMIT 1
    """
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (exchange, market_type, symbol, timeframe))
            row = cur.fetchone()
    if not row:
        return None
    return str(row[0])


def pg_append_dq_report(project_root: Path, row: dict[str, Any]) -> None:
    ensure_postgres_schema(project_root)
    sql = """
    INSERT INTO dq.ohlcv_quality_report (
      run_id, symbol, timeframe, trade_date_utc, expected_rows, actual_rows, completeness_pct,
      duplicate_rows, invalid_rows, gap_count, status, created_at_utc
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (run_id, symbol, timeframe, trade_date_utc) DO UPDATE SET
      expected_rows = EXCLUDED.expected_rows,
      actual_rows = EXCLUDED.actual_rows,
      completeness_pct = EXCLUDED.completeness_pct,
      duplicate_rows = EXCLUDED.duplicate_rows,
      invalid_rows = EXCLUDED.invalid_rows,
      gap_count = EXCLUDED.gap_count,
      status = EXCLUDED.status,
      created_at_utc = EXCLUDED.created_at_utc
    """
    vals = (
        row.get("run_id"),
        row.get("symbol"),
        row.get("timeframe"),
        row.get("trade_date_utc"),
        int(row.get("expected_rows", 0) or 0),
        int(row.get("actual_rows", 0) or 0),
        float(row.get("completeness_pct", 0.0) or 0.0),
        int(row.get("duplicate_rows", 0) or 0),
        int(row.get("invalid_rows", 0) or 0),
        int(row.get("gap_count", 0) or 0),
        row.get("status"),
        row.get("created_at_utc"),
    )
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, vals)


def pg_append_context_dq_report(project_root: Path, row: dict[str, Any]) -> None:
    ensure_postgres_schema(project_root)
    sql = """
    INSERT INTO dq.market_context_quality_report (
      run_id, dataset, symbol, timeframe, trade_date_utc, expected_rows, actual_rows, completeness_pct,
      duplicate_rows, invalid_rows, gap_count, status, contract_status, release_status, created_at_utc
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (run_id, dataset, symbol, timeframe, trade_date_utc) DO UPDATE SET
      expected_rows = EXCLUDED.expected_rows,
      actual_rows = EXCLUDED.actual_rows,
      completeness_pct = EXCLUDED.completeness_pct,
      duplicate_rows = EXCLUDED.duplicate_rows,
      invalid_rows = EXCLUDED.invalid_rows,
      gap_count = EXCLUDED.gap_count,
      status = EXCLUDED.status,
      contract_status = EXCLUDED.contract_status,
      release_status = EXCLUDED.release_status,
      created_at_utc = EXCLUDED.created_at_utc
    """
    vals = (
        row.get("run_id"),
        row.get("dataset"),
        row.get("symbol"),
        row.get("timeframe"),
        row.get("trade_date_utc"),
        int(row.get("expected_rows", 0) or 0),
        int(row.get("actual_rows", 0) or 0),
        float(row.get("completeness_pct", 0.0) or 0.0),
        int(row.get("duplicate_rows", 0) or 0),
        int(row.get("invalid_rows", 0) or 0),
        int(row.get("gap_count", 0) or 0),
        row.get("status"),
        row.get("contract_status"),
        row.get("release_status"),
        row.get("created_at_utc"),
    )
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, vals)


def pg_append_gap_events(project_root: Path, rows: list[dict[str, Any]]) -> None:
    ensure_postgres_schema(project_root)
    if not rows:
        return
    sql = """
    INSERT INTO dq.gap_events (
      run_id, dataset, symbol, timeframe, trade_date_utc, expected_open_time_utc, created_at_utc
    ) VALUES (%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (run_id, dataset, symbol, timeframe, trade_date_utc, expected_open_time_utc) DO NOTHING
    """
    vals = [
        (
            r.get("run_id"),
            r.get("dataset"),
            r.get("symbol"),
            r.get("timeframe"),
            r.get("trade_date_utc"),
            r.get("expected_open_time_utc"),
            r.get("created_at_utc"),
        )
        for r in rows
    ]
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, vals)


def pg_append_ingest_pair_status(project_root: Path, row: dict[str, Any]) -> None:
    ensure_postgres_schema(project_root)
    sql = """
    INSERT INTO meta.ingest_pair_status (
      run_id, date, symbol, timeframe, status, rows_read, rows_written, rows_rejected, error_text, started_at_utc, ended_at_utc
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    vals = (
        row.get("run_id"),
        row.get("date"),
        row.get("symbol"),
        row.get("timeframe"),
        row.get("status"),
        int(row.get("rows_read", 0) or 0),
        int(row.get("rows_written", 0) or 0),
        int(row.get("rows_rejected", 0) or 0),
        row.get("error_text"),
        row.get("started_at_utc"),
        row.get("ended_at_utc"),
    )
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, vals)


def pg_register_partition(project_root: Path, row: dict[str, Any]) -> None:
    ensure_postgres_schema(project_root)
    sql = """
    INSERT INTO meta.storage_partitions (
      created_at_utc, layer, dataset, trade_date_utc, symbol, timeframe, file_path, rows, run_id, status
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    vals = (
        row.get("created_at_utc"),
        row.get("layer"),
        row.get("dataset"),
        row.get("trade_date_utc"),
        row.get("symbol"),
        row.get("timeframe"),
        row.get("file_path"),
        int(row.get("rows", 0) or 0),
        row.get("run_id"),
        row.get("status"),
    )
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, vals)


def _df_rows(df, cols: list[str]) -> list[tuple[Any, ...]]:
    if df.empty:
        return []
    return [tuple(r[c] for c in cols) for _, r in df.iterrows()]


def pg_upsert_raw_ohlcv(project_root: Path, df) -> None:
    ensure_postgres_schema(project_root)
    cols = [
        "exchange",
        "market_type",
        "symbol",
        "timeframe",
        "trade_date_utc",
        "open_time_utc",
        "close_time_utc",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover",
        "ingest_run_id",
        "source_ts_utc",
    ]
    rows = _df_rows(df, cols)
    if not rows:
        return
    sql = """
    INSERT INTO raw.bybit_ohlcv (
      exchange, market_type, symbol, timeframe, trade_date_utc, open_time_utc, close_time_utc,
      open, high, low, close, volume, turnover, ingest_run_id, source_ts_utc
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (exchange, market_type, symbol, timeframe, open_time_utc) DO UPDATE SET
      close_time_utc = EXCLUDED.close_time_utc,
      open = EXCLUDED.open,
      high = EXCLUDED.high,
      low = EXCLUDED.low,
      close = EXCLUDED.close,
      volume = EXCLUDED.volume,
      turnover = EXCLUDED.turnover,
      ingest_run_id = EXCLUDED.ingest_run_id,
      source_ts_utc = EXCLUDED.source_ts_utc
    """
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)


def pg_upsert_raw_funding(project_root: Path, df) -> None:
    ensure_postgres_schema(project_root)
    cols = [
        "exchange",
        "market_type",
        "symbol",
        "timeframe",
        "trade_date_utc",
        "event_time_utc",
        "funding_rate",
        "ingest_run_id",
        "source_ts_utc",
        "contract_version",
    ]
    rows = _df_rows(df, cols)
    if not rows:
        return
    sql = """
    INSERT INTO raw.bybit_funding (
      exchange, market_type, symbol, timeframe, trade_date_utc, event_time_utc, funding_rate, ingest_run_id, source_ts_utc, contract_version
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (exchange, market_type, symbol, timeframe, event_time_utc) DO UPDATE SET
      funding_rate = EXCLUDED.funding_rate,
      ingest_run_id = EXCLUDED.ingest_run_id,
      source_ts_utc = EXCLUDED.source_ts_utc,
      contract_version = EXCLUDED.contract_version
    """
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)


def pg_upsert_raw_open_interest(project_root: Path, df) -> None:
    ensure_postgres_schema(project_root)
    cols = [
        "exchange",
        "market_type",
        "symbol",
        "timeframe",
        "trade_date_utc",
        "open_time_utc",
        "open_interest",
        "ingest_run_id",
        "source_ts_utc",
        "contract_version",
    ]
    rows = _df_rows(df, cols)
    if not rows:
        return
    sql = """
    INSERT INTO raw.bybit_open_interest (
      exchange, market_type, symbol, timeframe, trade_date_utc, open_time_utc, open_interest, ingest_run_id, source_ts_utc, contract_version
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (exchange, market_type, symbol, timeframe, open_time_utc) DO UPDATE SET
      open_interest = EXCLUDED.open_interest,
      ingest_run_id = EXCLUDED.ingest_run_id,
      source_ts_utc = EXCLUDED.source_ts_utc,
      contract_version = EXCLUDED.contract_version
    """
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)


def postgres_smoke(project_root: Path) -> dict[str, Any]:
    ensure_postgres_schema(project_root)
    checks: dict[str, Any] = {
        "mode": load_storage_runtime_config(project_root).mode,
        "schema_ok": True,
        "tables": {},
    }
    q = """
    SELECT n.nspname, c.relname
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind='r' AND n.nspname IN ('raw','meta','dq')
      AND c.relname IN (
        'bybit_ohlcv','bybit_funding','bybit_open_interest',
        'ingest_run','ingest_watermark','ingest_pair_status','storage_partitions',
        'ohlcv_quality_report','market_context_quality_report','gap_events'
      )
    ORDER BY n.nspname, c.relname
    """
    with _connect(project_root) as conn:
        with conn.cursor() as cur:
            cur.execute(q)
            rows = cur.fetchall()
    found = {f"{r[0]}.{r[1]}" for r in rows}
    required = {
        "raw.bybit_ohlcv",
        "raw.bybit_funding",
        "raw.bybit_open_interest",
        "meta.ingest_run",
        "meta.ingest_watermark",
        "meta.ingest_pair_status",
        "meta.storage_partitions",
        "dq.ohlcv_quality_report",
        "dq.market_context_quality_report",
        "dq.gap_events",
    }
    missing = sorted(required - found)
    checks["tables"] = {
        "found_count": len(found),
        "missing": missing,
    }
    checks["ok"] = len(missing) == 0
    return checks


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="PostgreSQL runtime helper for MLbotNav storage.")
    parser.add_argument("--ensure-schema", action="store_true", help="Apply SQL DDL for runtime tables")
    parser.add_argument("--smoke", action="store_true", help="Run schema/table smoke check")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    out: dict[str, Any] = {
        "run_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "mode": load_storage_runtime_config(project_root).mode,
    }
    if args.ensure_schema:
        ensure_postgres_schema(project_root)
        out["ensure_schema"] = "ok"
    if args.smoke:
        out["smoke"] = postgres_smoke(project_root)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if "smoke" in out and not bool(out["smoke"].get("ok", False)):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
