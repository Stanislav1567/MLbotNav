-- PostgreSQL runtime storage schema for MLbotNav
-- Covers raw/meta/dq layers used by ingest + DQ runtime.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS dq;
CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE IF NOT EXISTS raw.bybit_ohlcv (
    exchange TEXT NOT NULL,
    market_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    open_time_utc TIMESTAMPTZ NOT NULL,
    close_time_utc TIMESTAMPTZ NOT NULL,
    open NUMERIC(20,10) NOT NULL,
    high NUMERIC(20,10) NOT NULL,
    low NUMERIC(20,10) NOT NULL,
    close NUMERIC(20,10) NOT NULL,
    volume NUMERIC(30,10) NOT NULL,
    turnover NUMERIC(30,10),
    ingest_run_id UUID NOT NULL,
    source_ts_utc TIMESTAMPTZ NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (exchange, market_type, symbol, timeframe, open_time_utc)
);

CREATE INDEX IF NOT EXISTS idx_bybit_ohlcv_symbol_tf_time
    ON raw.bybit_ohlcv (symbol, timeframe, open_time_utc);

CREATE INDEX IF NOT EXISTS idx_bybit_ohlcv_trade_date
    ON raw.bybit_ohlcv (trade_date_utc);

CREATE TABLE IF NOT EXISTS raw.bybit_funding (
    exchange TEXT NOT NULL,
    market_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    event_time_utc TIMESTAMPTZ NOT NULL,
    funding_rate DOUBLE PRECISION NOT NULL,
    ingest_run_id UUID NOT NULL,
    source_ts_utc TIMESTAMPTZ NOT NULL,
    contract_version TEXT,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (exchange, market_type, symbol, timeframe, event_time_utc)
);

CREATE TABLE IF NOT EXISTS raw.bybit_open_interest (
    exchange TEXT NOT NULL,
    market_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    open_time_utc TIMESTAMPTZ NOT NULL,
    open_interest DOUBLE PRECISION NOT NULL,
    ingest_run_id UUID NOT NULL,
    source_ts_utc TIMESTAMPTZ NOT NULL,
    contract_version TEXT,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (exchange, market_type, symbol, timeframe, open_time_utc)
);

CREATE TABLE IF NOT EXISTS meta.ingest_run (
    run_id UUID PRIMARY KEY,
    started_at_utc TIMESTAMPTZ NOT NULL,
    ended_at_utc TIMESTAMPTZ,
    status TEXT NOT NULL,
    rows_read BIGINT NOT NULL DEFAULT 0,
    rows_written BIGINT NOT NULL DEFAULT 0,
    rows_upserted BIGINT NOT NULL DEFAULT 0,
    rows_rejected BIGINT NOT NULL DEFAULT 0,
    error_text TEXT
);

CREATE TABLE IF NOT EXISTS meta.ingest_watermark (
    exchange TEXT NOT NULL,
    market_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    last_loaded_open_time_utc TIMESTAMPTZ NOT NULL,
    last_success_run_id UUID,
    updated_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (exchange, market_type, symbol, timeframe)
);

CREATE TABLE IF NOT EXISTS meta.ingest_pair_status (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    date DATE NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    status TEXT NOT NULL,
    rows_read BIGINT NOT NULL DEFAULT 0,
    rows_written BIGINT NOT NULL DEFAULT 0,
    rows_rejected BIGINT NOT NULL DEFAULT 0,
    error_text TEXT,
    started_at_utc TIMESTAMPTZ NOT NULL,
    ended_at_utc TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS meta.storage_partitions (
    id BIGSERIAL PRIMARY KEY,
    created_at_utc TIMESTAMPTZ NOT NULL,
    layer TEXT NOT NULL,
    dataset TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    file_path TEXT NOT NULL,
    rows BIGINT NOT NULL DEFAULT 0,
    run_id UUID NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dq.ohlcv_quality_report (
    report_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    expected_rows INTEGER NOT NULL,
    actual_rows INTEGER NOT NULL,
    completeness_pct NUMERIC(6,3) NOT NULL,
    duplicate_rows INTEGER NOT NULL DEFAULT 0,
    invalid_rows INTEGER NOT NULL DEFAULT 0,
    gap_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, symbol, timeframe, trade_date_utc)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_quality_symbol_tf_date
    ON dq.ohlcv_quality_report (symbol, timeframe, trade_date_utc);

CREATE TABLE IF NOT EXISTS dq.market_context_quality_report (
    report_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    dataset TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    expected_rows INTEGER NOT NULL,
    actual_rows INTEGER NOT NULL,
    completeness_pct NUMERIC(6,3) NOT NULL,
    duplicate_rows INTEGER NOT NULL DEFAULT 0,
    invalid_rows INTEGER NOT NULL DEFAULT 0,
    gap_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    contract_status TEXT NOT NULL,
    release_status TEXT NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, dataset, symbol, timeframe, trade_date_utc)
);

CREATE TABLE IF NOT EXISTS dq.gap_events (
    event_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    dataset TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    trade_date_utc DATE NOT NULL,
    expected_open_time_utc TIMESTAMPTZ NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, dataset, symbol, timeframe, trade_date_utc, expected_open_time_utc)
);

CREATE INDEX IF NOT EXISTS idx_gap_events_symbol_tf_date
    ON dq.gap_events (symbol, timeframe, trade_date_utc, dataset);

DO $$
BEGIN
    ALTER TABLE raw.bybit_ohlcv
        ADD CONSTRAINT ck_raw_bybit_ohlcv_timeframe
        CHECK (timeframe IN ('1m','5m','15m','30m','1h','4h','1d'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE raw.bybit_ohlcv
        ADD CONSTRAINT ck_raw_bybit_ohlcv_prices
        CHECK (high >= low AND high >= GREATEST(open, close) AND low <= LEAST(open, close));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE raw.bybit_ohlcv
        ADD CONSTRAINT ck_raw_bybit_ohlcv_volume_nonnegative
        CHECK (volume >= 0 AND turnover >= 0);
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE raw.bybit_funding
        ADD CONSTRAINT ck_raw_bybit_funding_timeframe
        CHECK (timeframe = '8h');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE raw.bybit_open_interest
        ADD CONSTRAINT ck_raw_bybit_oi_timeframe
        CHECK (timeframe IN ('1m','5m','15m','30m','1h','4h','1d'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE raw.bybit_open_interest
        ADD CONSTRAINT ck_raw_bybit_oi_nonnegative
        CHECK (open_interest >= 0);
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE dq.ohlcv_quality_report
        ADD CONSTRAINT ck_dq_ohlcv_status
        CHECK (status IN ('PASS','WARN','FAIL'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE dq.ohlcv_quality_report
        ADD CONSTRAINT ck_dq_ohlcv_completeness
        CHECK (completeness_pct >= 0 AND completeness_pct <= 100);
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE dq.market_context_quality_report
        ADD CONSTRAINT ck_dq_context_status
        CHECK (status IN ('PASS','WARN','FAIL'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE dq.market_context_quality_report
        ADD CONSTRAINT ck_dq_context_contract_status
        CHECK (contract_status IN ('PASS','FAIL'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE dq.market_context_quality_report
        ADD CONSTRAINT ck_dq_context_release_status
        CHECK (release_status IN ('PASS','WARN','FAIL'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE dq.gap_events
        ADD CONSTRAINT ck_dq_gap_timeframe
        CHECK (timeframe IN ('1m','5m','15m','30m','1h','4h','8h','1d'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE raw.bybit_ohlcv
        ADD CONSTRAINT ck_raw_bybit_ohlcv_market_type
        CHECK (market_type IN ('spot','linear'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE raw.bybit_ohlcv
        ADD CONSTRAINT ck_raw_bybit_ohlcv_close_after_open
        CHECK (close_time_utc > open_time_utc);
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE meta.ingest_watermark
        ADD CONSTRAINT ck_meta_ingest_watermark_market_type
        CHECK (market_type IN ('spot','linear'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE meta.ingest_watermark
        ADD CONSTRAINT fk_meta_ingest_watermark_last_success_run
        FOREIGN KEY (last_success_run_id) REFERENCES meta.ingest_run (run_id);
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE dq.ohlcv_quality_report
        ADD CONSTRAINT fk_dq_ohlcv_quality_run
        FOREIGN KEY (run_id) REFERENCES meta.ingest_run (run_id);
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE dq.gap_events
        ADD CONSTRAINT fk_dq_gap_events_run
        FOREIGN KEY (run_id) REFERENCES meta.ingest_run (run_id);
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;
