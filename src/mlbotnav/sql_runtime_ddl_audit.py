from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_SCHEMAS: tuple[str, ...] = ("raw", "core", "analytics", "dq", "meta")
REQUIRED_TABLES: tuple[str, ...] = (
    "raw.bybit_ohlcv",
    "meta.ingest_run",
    "meta.ingest_watermark",
    "dq.ohlcv_quality_report",
    "dq.gap_events",
)

REQUIRED_TABLE_COLUMNS: dict[str, tuple[str, ...]] = {
    "raw.bybit_ohlcv": (
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
        "ingest_run_id",
        "source_ts_utc",
    ),
    "meta.ingest_run": (
        "run_id",
        "status",
        "rows_read",
        "rows_written",
        "rows_upserted",
        "rows_rejected",
    ),
    "meta.ingest_watermark": (
        "exchange",
        "market_type",
        "symbol",
        "timeframe",
        "last_loaded_open_time_utc",
        "last_success_run_id",
    ),
    "dq.ohlcv_quality_report": (
        "run_id",
        "symbol",
        "timeframe",
        "trade_date_utc",
        "expected_rows",
        "actual_rows",
        "completeness_pct",
        "status",
    ),
    "dq.gap_events": (
        "run_id",
        "symbol",
        "timeframe",
        "trade_date_utc",
    ),
}


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _normalize_sql(sql_text: str) -> str:
    return re.sub(r"\s+", " ", str(sql_text or "")).strip().lower()


def _extract_table_block(sql_text: str, table_name: str) -> str:
    pat = re.compile(
        rf"create\s+table\s+if\s+not\s+exists\s+{re.escape(table_name.lower())}\s*\((.*?)\)\s*;",
        re.IGNORECASE | re.DOTALL,
    )
    m = pat.search(sql_text)
    return m.group(1) if m else ""


def _has_market_type_check(sql_text: str) -> bool:
    return bool(
        re.search(
            r"market_type\s+in\s*\(\s*['\"]spot['\"]\s*,\s*['\"]linear['\"]\s*\)",
            sql_text,
            flags=re.IGNORECASE,
        )
    )


def _has_close_after_open_check(sql_text: str) -> bool:
    lower = sql_text.lower()
    return "close_time_utc > open_time_utc" in lower


def _has_fk_to_ingest_run(sql_text: str, table_name: str, col_name: str = "run_id") -> bool:
    block = _extract_table_block(sql_text, table_name)
    if block:
        if re.search(
            rf"foreign\s+key\s*\(\s*{re.escape(col_name)}\s*\)\s+references\s+meta\.ingest_run\s*\(\s*run_id\s*\)",
            block,
            flags=re.IGNORECASE,
        ):
            return True
    return bool(
        re.search(
            rf"alter\s+table\s+{re.escape(table_name)}\s+add\s+constraint\s+\S+\s+foreign\s+key\s*\(\s*{re.escape(col_name)}\s*\)\s+references\s+meta\.ingest_run\s*\(\s*run_id\s*\)",
            sql_text,
            flags=re.IGNORECASE,
        )
    )


def _has_column(table_block: str, col_name: str) -> bool:
    col_pat = re.compile(rf"\b{re.escape(col_name.lower())}\b", re.IGNORECASE)
    return bool(col_pat.search(table_block))


def evaluate_runtime_ddl_parity(*, sql_text: str) -> dict[str, Any]:
    normalized = _normalize_sql(sql_text)
    checks: list[dict[str, Any]] = []
    gaps: list[str] = []

    for schema in REQUIRED_SCHEMAS:
        ok = f"create schema if not exists {schema}" in normalized
        checks.append({"name": f"schema_{schema}_present", "ok": ok})
        if not ok:
            gaps.append(f"missing_schema:{schema}")

    for table_name in REQUIRED_TABLES:
        block = _extract_table_block(normalized, table_name)
        ok = bool(block)
        checks.append({"name": f"table_{table_name}_present", "ok": ok})
        if not ok:
            gaps.append(f"missing_table:{table_name}")
            continue
        req_cols = REQUIRED_TABLE_COLUMNS.get(table_name, ())
        missing_cols: list[str] = []
        for col in req_cols:
            if not _has_column(block, col):
                missing_cols.append(col)
        checks.append({"name": f"columns_{table_name}_required", "ok": len(missing_cols) == 0, "missing": missing_cols})
        if missing_cols:
            gaps.append(f"missing_columns:{table_name}:{','.join(missing_cols)}")

    # Section-21 critical contract checks.
    market_type_check_ok = _has_market_type_check(normalized)
    checks.append({"name": "market_type_domain_check_present", "ok": market_type_check_ok})
    if not market_type_check_ok:
        gaps.append("missing_check:market_type_spot_linear")

    close_after_open_ok = _has_close_after_open_check(normalized)
    checks.append({"name": "ohlcv_close_after_open_check_present", "ok": close_after_open_ok})
    if not close_after_open_ok:
        gaps.append("missing_check:close_time_after_open_time")

    ingest_wm_fk_ok = _has_fk_to_ingest_run(normalized, "meta.ingest_watermark", col_name="last_success_run_id")
    checks.append({"name": "ingest_watermark_fk_to_ingest_run", "ok": ingest_wm_fk_ok})
    if not ingest_wm_fk_ok:
        gaps.append("missing_fk:meta.ingest_watermark.last_success_run_id->meta.ingest_run.run_id")

    dq_ohlcv_fk_ok = _has_fk_to_ingest_run(normalized, "dq.ohlcv_quality_report", col_name="run_id")
    checks.append({"name": "dq_ohlcv_quality_report_fk_to_ingest_run", "ok": dq_ohlcv_fk_ok})
    if not dq_ohlcv_fk_ok:
        gaps.append("missing_fk:dq.ohlcv_quality_report.run_id->meta.ingest_run.run_id")

    dq_gap_fk_ok = _has_fk_to_ingest_run(normalized, "dq.gap_events", col_name="run_id")
    checks.append({"name": "dq_gap_events_fk_to_ingest_run", "ok": dq_gap_fk_ok})
    if not dq_gap_fk_ok:
        gaps.append("missing_fk:dq.gap_events.run_id->meta.ingest_run.run_id")

    status = "PASS" if not gaps else "WARN"
    return {"status": status, "checks": checks, "gaps": gaps}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SQL runtime DDL parity against section-21 subset.")
    parser.add_argument(
        "--sql-path",
        default="sql/postgres_storage_runtime.sql",
        help="Path to runtime SQL DDL file.",
    )
    parser.add_argument(
        "--out-dir",
        default="reports/qa_gate",
        help="Where to write parity report json.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    sql_path = Path(str(args.sql_path))
    if not sql_path.is_absolute():
        sql_path = (project_root / sql_path).resolve()
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    sql_text = sql_path.read_text(encoding="utf-8")
    result = evaluate_runtime_ddl_parity(sql_text=sql_text)

    out_dir = Path(str(args.out_dir))
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"sql_runtime_ddl_parity_{_utc_tag()}.json"
    payload = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "sql_path": str(sql_path),
        "status": result["status"],
        "gap_count": len(result["gaps"]),
        "gaps": result["gaps"],
        "checks": result["checks"],
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report_path": str(out_path), "status": payload["status"], "gap_count": payload["gap_count"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
