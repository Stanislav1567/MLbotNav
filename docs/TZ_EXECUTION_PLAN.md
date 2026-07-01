# MLbotNav: Декомпозиция ТЗ и статус исполнения

Источник: `TECH_SPEC_ML_PLATFORM_RU.md` (версия 1.0 от 2026-05-20)

## P0: Обязательная база (блокирует все следующее)

1. Контур выгрузки Bybit v5 дневными батчами UTC.
   - Статус: `DONE (MVP)`
   - Что есть: `src/mlbotnav/ingest_day.py`, `src/mlbotnav/bybit_client.py`
2. Туннель к внешним ключам без смешения кода проектов.
   - Статус: `DONE`
   - Что есть: `SOURCE_ENV_PATH` в `.env`, загрузка в `settings.py`
3. Свечной график для ручной проверки данных (candles + EMA + volume).
   - Статус: `DONE`
   - Что есть: `src/mlbotnav/plot_candles.py`
4. Data Quality Gate + отчеты полноты/валидности.
   - Статус: `IN PROGRESS`
   - Что добавляем: `src/mlbotnav/dq.py`, `data/dq/ohlcv_quality_report.csv`
5. Идемпотентность и watermark прогресса загрузки.
   - Статус: `IN PROGRESS`
   - Что добавляем: `data/meta/ingest_run.csv`, `data/meta/ingest_watermark.csv`

## P1: Базовый ML-контур

1. Baseline-модель и отчет метрик.
   - Статус: `DONE (MVP)`
   - Что есть: `src/mlbotnav/train_baseline.py`
2. Walk-forward и leakage-safe фичи.
   - Статус: `TODO`
3. Backtest с fee/slippage.
   - Статус: `TODO`

## P2: Прод-контур (следующий этап)

1. Champion/challenger + quality gates.
2. Drift/latency мониторинг и алерты.
3. Rollback policy.

## P3: CV-контур и ранцы

1. Скриншоты + integrity (hash/phash/dedup).
2. Overlay renderer.
3. Artifact packs + index.

## Правило работы в этом репозитории

Берем из внешнего проекта только доступ к бирже (ключи/endpoint), но вся логика ingest/DQ/ML хранится и развивается локально в `MLbotNav`.

## Rule Fix: Minute-First + User Approval Gate
1. Work only on `1m` timeframe until minute-stage result is fully reviewed.
2. Before user confirmation, any 30-day run is blocked.
3. Only after user confirms final minute-stage result, allow 30-day minute runs.
4. No timeframe switching is allowed while gate is locked to `1m`.
5. Confirmation command (after user approval):
   `python -m mlbotnav.workflow_gate --allow-30d true --mark-minute-study-complete true --confirmation-note "user approved minute final"`
