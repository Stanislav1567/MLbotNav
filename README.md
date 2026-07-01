# MLbotNav

Standalone ML project for crypto market data ingestion and model training.

This project intentionally reuses only Bybit connectivity from an existing project
through an external `.env` tunnel, while keeping all ML logic and artifacts local.

## Quick Start

1. Configure local env:
   - Copy `.env.example` to `.env`
   - Set `SOURCE_ENV_PATH` to the external project env file
2. Run one-day ingestion:
   - `python -m mlbotnav.ingest_day --date 2026-05-20`
3. Run incremental ingestion from watermark:
   - `python -m mlbotnav.ingest_incremental --symbol SOLUSDT --timeframes 1,5,15,30,60,240,D --lookback-days 3`
3. Run baseline training:
   - `python -m mlbotnav.train_baseline --date 2026-05-20 --timeframe 1m`
4. Render clean candle chart:
   - `python -m mlbotnav.plot_candles --date 2026-05-20 --timeframe 1m --symbol SOLUSDT --show-volume`
5. Run unified train-eval pipeline:
   - `python -m mlbotnav.pipeline_train_eval --symbol SOLUSDT --timeframe 1m --start-date 2026-05-18 --end-date 2026-05-20 --promote-if-pass`
6. Run drift monitor:
   - `python -m mlbotnav.monitor_drift --symbol SOLUSDT --timeframe 1m --reference-start 2026-05-18 --reference-end 2026-05-19 --current-start 2026-05-20 --current-end 2026-05-21`
7. Build artifact pack:
   - `python -m mlbotnav.build_pack --date 2026-05-20 --symbol SOLUSDT --timeframe 1m`
8. Ingest CV screenshot with integrity metadata:
   - `python -m mlbotnav.cv_ingest --file <ABS_PATH_TO_IMAGE> --source-id terminal_manual --symbol SOLUSDT --timeframe 1m`

## Data Layout

- Raw OHLCV:
  - `data/raw/bybit_ohlcv/dt=YYYY-MM-DD/tf=<timeframe>/symbol=<symbol>/part-final.csv`
- Meta:
  - `data/meta/ingest_run.csv`
  - `data/meta/ingest_watermark.csv`
- DQ:
  - `data/dq/ohlcv_quality_report.csv`
- Logs:
  - `logs/ingest_day_*.log`
- Models:
  - `models/baseline/*.joblib`
  - `models/pipeline/*.joblib`
  - `models/registry/champion.json`
  - `models/registry/candidates.jsonl`
- Training reports:
  - `reports/training/*.json`
  - `reports/pipeline/*.json`
  - `reports/monitoring/*.json`
- Packs:
  - `packs/YYYY-MM-DD/session_id/`
- CV integrity:
  - `data/cv/original/...`
  - `data/cv/cv_index.csv`
- Audit:
  - `logs/audit.log`

## Execution Plan

- TZ decomposition and phase status: `docs/TZ_EXECUTION_PLAN.md`
- Unified chronology (append-only): `docs/CHANGELOG_CHRONOLOGY_RU.md`

## CPU Safety Rule (Strict)

- For heavy runs, keep host CPU at or below `85%`.
- If host CPU is above the limit, runners wait and retry (throttle) instead of forcing execution.
- No foreign jobs are stopped by this project. Only local throttling and per-process thread limits are applied.
- Policy source: `configs/prod_policy.yaml` -> `prod.cpu_budget`.

## Minute-First Workflow Gate

- Active gate config: `configs/workflow_gate.yaml`
- Default mode: locked to `1m`, 30-day runs blocked.
- Show current gate state:
  - `python -m mlbotnav.workflow_gate --show`
- Enable 30-day minute runs only after user confirmation:
  - `python -m mlbotnav.workflow_gate --allow-30d true --mark-minute-study-complete true --confirmation-note "user approved minute final"`
- 5+ master execution checklist: `docs/TZ_5PLUS_MASTER_CHECKLIST_RU.md`

## TA Pipeline (v1)
- New module: `python -m mlbotnav.technical_analysis --symbol SOLUSDT --timeframe 1m --start-date YYYY-MM-DD --end-date YYYY-MM-DD`
- Writes: `data/analytics/levels.csv`, `data/analytics/pattern_events.csv`, `data/analytics/signal_events.csv`.
- Invariants in signals: `TP>=1%` and `NO_TRADE` reason codes when constraints fail.

