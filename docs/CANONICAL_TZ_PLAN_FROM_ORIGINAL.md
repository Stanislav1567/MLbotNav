# Канонический План По Исходному ТЗ (v1.0)

Источник истины: `TECH_SPEC_ML_PLATFORM_RU.md` (дата: 2026-05-20).  
Цель: вернуть исполнение строго к исходному порядку ТЗ без добавления новых требований.

## Правило работы

1. Выполняем строго по этапам из раздела 14 исходного ТЗ: `0 -> 1 -> 2 -> 3 -> 4`.
2. Любые process-control механики (`readiness`, `minute-first`, локальные freeze-гейты) считаются вспомогательными и не подменяют пункты ТЗ.
3. Переход к следующему этапу только после фиксации acceptance-артефактов текущего.

## Этап 0: Инженерный фундамент (ТЗ 5, 21)

1. Довести storage runtime до полного соответствия SQL DDL раздела 21:
   - обязательные ограничения/ключи;
   - таблицы `raw/core/analytics/dq/meta`, включая `dq.gap_events`;
   - консистентные upsert для day/incremental.
2. Устранить расхождение train-контуров: обучение должно работать на `core`, а не на `raw`.
3. Нормализовать таймфреймы к единому контракту (`1m,5m,15m,30m,1h,4h,1d`) во всех слоях (ингест, контракт, DDL, отчеты).
4. Закрыть технический риск incremental+postgres (`ingest_pair_status.date` not null).

Acceptance:
1. Smoke `file` и `postgres` режимов проходят на одном и том же датасете.
2. DQ FAIL не попадает в `core`.
3. Все ingest run артефакты записываются без ошибок в выбранный backend.

## Этап 1: Baseline/Core ML (ТЗ 6, 8)

1. Проверить полный набор обязательных фич-блоков `Price/Trend/Volume/Structure/Pattern`.
2. Жестко зафиксировать leakage-safe train/validation.
3. Довести обязательные торговые поля и метрики:
   - `expected_move_pct`, `tp_reach_prob`, `time_to_target`;
   - `Sharpe, Sortino, Max Drawdown, CAGR, hit-rate`.
4. Убедиться, что эти поля единообразно есть в backtest/pipeline/inference/paper reports.

Acceptance:
1. Все отчеты содержат полный набор обязательных полей ТЗ.
2. Gate-логика учитывает обязательные метрики.

## Этап 2: Прод-контур (ТЗ 7, 12, 15.4, 19)

1. Сделать stage progression `D1 -> ... -> D90` обязательным перед promote.
2. Свести deployment gates в единый обязательный контур:
   - data quality;
   - leakage checks;
   - backtest thresholds;
   - security gate;
   - SLA checks.
3. Довести drift->event retrain и SLA `<= 2 мин` до проверяемого smoke.
4. Уточнить non-degradation policy (без ослабленных параметров в прод-конфиге).
5. Зафиксировать сервисные SLI/SLO для inference (availability/p95), не только step-level отчеты.

Acceptance:
1. Promote невозможен при провале любого gate.
2. Drift alert приводит к retrain trigger в SLA.
3. Есть отчетность по сервисным KPI inference.

## Этап 3: CV/Annotation + Rance (ТЗ 9, 10)

1. Закрыть CV integrity pipeline:
   - hash/phash/dedup/malware-scan;
   - `original + overlay + mask + metadata + decision`.
2. Проверить разделение CV-контура и ML-контуров (без смешивания).
3. Довести ранцы до полного формата и индексации артефактов.

Acceptance:
1. На каждый CV run формируется полный комплект артефактов.
2. Suspicious файлы не проходят в рабочий CV-поток.
3. Pack-индекс и подписи формируются стабильно.

## Этап 4: Hardening/Final (ТЗ 11, 13, 16)

1. Довести security provider до реального `env|vault|kms` (не stub).
2. Проверить аудит, retention и восстановление (RTO/RPO процедуры).
3. Провести финальный аудит соответствия исходному ТЗ и открыть обучение в штатном режиме.

Acceptance:
1. Все обязательные пункты ТЗ имеют статус `DONE` с артефактами.
2. `project_ready=true` выставляется только после финального чеклиста.
