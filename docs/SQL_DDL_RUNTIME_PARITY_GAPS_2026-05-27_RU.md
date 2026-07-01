# SQL DDL Runtime Parity (Section 21)

Дата (UTC): 2026-05-27T07:33:46Z
Контур: ML runtime без калибровки.
Основание: `TECH_SPEC_ML_PLATFORM_RU.md` (раздел 21) и `sql/postgres_storage_runtime.sql`.

## Что проверяется
1. Наличие обязательных схем: `raw/core/analytics/dq/meta`.
2. Наличие обязательных runtime-таблиц:
   - `raw.bybit_ohlcv`
   - `meta.ingest_run`
   - `meta.ingest_watermark`
   - `dq.ohlcv_quality_report`
   - `dq.gap_events`
3. Наличие обязательных колонок runtime-subset.
4. Критические DDL-контракты:
   - `market_type IN ('spot','linear')`
   - `close_time_utc > open_time_utc`
   - FK на `meta.ingest_run(run_id)` для `meta.ingest_watermark`, `dq.ohlcv_quality_report`, `dq.gap_events`.

## Автоматический аудит
1. Скрипт: `python -m mlbotnav.sql_runtime_ddl_audit`
2. Тест: `tests/test_sql_runtime_ddl_audit.py`
3. Итоговый артефакт PASS:
   - `reports/qa_gate/sql_runtime_ddl_parity_20260527T073337Z.json`

## Результат
1. G4 закрыт.
2. Обязательный runtime-subset раздела 21 формализован и проверяется автоматически.
3. Текущий статус: `PASS`, `gap_count=0`.
