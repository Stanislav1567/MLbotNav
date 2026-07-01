from __future__ import annotations

import unittest

from mlbotnav.sql_runtime_ddl_audit import evaluate_runtime_ddl_parity


_SQL_OK = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS dq;
CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE IF NOT EXISTS raw.bybit_ohlcv (
    exchange TEXT NOT NULL,
    market_type TEXT NOT NULL CHECK (market_type IN ('spot', 'linear')),
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    open_time_utc TIMESTAMPTZ NOT NULL,
    close_time_utc TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    ingest_run_id UUID NOT NULL,
    source_ts_utc TIMESTAMPTZ NOT NULL,
    CHECK (close_time_utc > open_time_utc)
);

CREATE TABLE IF NOT EXISTS meta.ingest_run (
    run_id UUID PRIMARY KEY,
    status TEXT NOT NULL,
    rows_read BIGINT NOT NULL,
    rows_written BIGINT NOT NULL,
    rows_upserted BIGINT NOT NULL,
    rows_rejected BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS meta.ingest_watermark (
    exchange TEXT NOT NULL,
    market_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    last_loaded_open_time_utc TIMESTAMPTZ NOT NULL,
    last_success_run_id UUID,
    FOREIGN KEY (last_success_run_id) REFERENCES meta.ingest_run (run_id)
);

CREATE TABLE IF NOT EXISTS dq.ohlcv_quality_report (
    run_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    expected_rows INTEGER NOT NULL,
    actual_rows INTEGER NOT NULL,
    completeness_pct NUMERIC NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES meta.ingest_run (run_id)
);

CREATE TABLE IF NOT EXISTS dq.gap_events (
    run_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    FOREIGN KEY (run_id) REFERENCES meta.ingest_run (run_id)
);
"""


class SqlRuntimeDdlAuditTests(unittest.TestCase):
    def test_parity_passes_on_complete_minimal_sql(self) -> None:
        out = evaluate_runtime_ddl_parity(sql_text=_SQL_OK)
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(out["gaps"], [])

    def test_parity_reports_missing_market_type_check(self) -> None:
        bad = _SQL_OK.replace(" CHECK (market_type IN ('spot', 'linear'))", "")
        out = evaluate_runtime_ddl_parity(sql_text=bad)
        self.assertEqual(out["status"], "WARN")
        self.assertTrue(any("missing_check:market_type_spot_linear" == g for g in out["gaps"]))


if __name__ == "__main__":
    unittest.main()
