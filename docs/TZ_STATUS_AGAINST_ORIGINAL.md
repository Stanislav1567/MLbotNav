# Статус По Исходному ТЗ: Матрица Соответствия

Источник истины: `TECH_SPEC_ML_PLATFORM_RU.md`  
Дата сверки: 2026-05-21

Формат:
1. `DONE` — реализовано и подтверждено кодом/артефактами.
2. `PARTIAL` — реализовано частично или с риском несоответствия.
3. `TODO` — не реализовано.

## Критичные разрывы (влияют на готовность модели)

1. Train должен читать `core`, сейчас используется `raw` — `PARTIAL`.
   - Доказательство: `src/mlbotnav/dataset.py`, `src/mlbotnav/pipeline_train_eval.py`.
   - Action: переключить data loader на `core` с fallback-policy только по явной опции.

2. Promote до полного stage-ladder — `PARTIAL`.
   - Доказательство: `src/mlbotnav/pipeline_train_eval.py`, `configs/prod_policy.yaml`.
   - Action: запрет promote без успешного прохождения требуемого stage.

3. Postgres DDL раздела 21 покрыт не полностью — `PARTIAL`.
   - Доказательство: `sql/postgres_storage_runtime.sql`.
   - Action: добавить недостающие ограничения/таблицы (включая `dq.gap_events`) и прогнать smoke.

4. Vault/KMS integration пока stub-уровня — `PARTIAL`.
   - Доказательство: `src/mlbotnav/security.py`.
   - Action: реализовать полноценные provider integration paths.

## Матрица По Разделам ТЗ

1. Раздел 5 (данные, контракты, Bybit ingest, DQ): `DONE/PARTIAL`.
   - DONE: OHLCV ingestion day/incremental, DQ, quarantine, watermark/meta.
   - DONE: funding + OI ingestion, contracts, DQ.
   - PARTIAL: полное соответствие SQL runtime разделу 21.

2. Раздел 6 (features/targets/models): `PARTIAL`.
   - DONE: feature blocks и leakage-safe базовый контур.
   - DONE: `time_to_target`, `sortino`, `cagr` добавлены.
   - PARTIAL: единообразие обязательных торговых полей во всех отчетах/контурах.

3. Раздел 7 (MLOps/registry/gates): `PARTIAL`.
   - DONE: champion/challenger, promotion guard, rollback guard.
   - PARTIAL: единый обязательный gate-пайплайн перед promote.

4. Раздел 8 (validation/backtest): `PARTIAL`.
   - DONE: walk-forward + fee/slippage.
   - TODO/PARTIAL: отдельный контур стресс-сценариев.

5. Раздел 9 (CV contour): `PARTIAL`.
   - DONE: integrity (hash/phash/dedup), malware hook, mask artifacts.
   - PARTIAL: сервисное отделение CV как отдельного production контура.

6. Раздел 10 (ранцы): `DONE/PARTIAL`.
   - DONE: packs + checksums + index + signatures.
   - PARTIAL: унификация с итоговым форматом всех обязательных CV/ML артефактов.

7. Раздел 11 (security/governance): `PARTIAL`.
   - DONE: RBAC, audit, retention, signing, security gate.
   - PARTIAL: полноценный Vault/KMS + at-rest/runtime policy enforcement.

8. Раздел 12 (NFR/SLA): `PARTIAL/TODO`.
   - DONE: SLA отчеты по pipeline steps.
   - TODO: inference-service KPI (availability 99.5%, p95 <= 300ms) как сервисный контур.

9. Раздел 19 (stage system): `PARTIAL`.
   - DONE: stage ladder runtime + negative memory.
   - PARTIAL: строгое соответствие формуле рейтинга и обязательности stage перед promote.

10. Раздел 21 (SQL DDL): `PARTIAL`.
   - DONE: postgres adapter + migrate/smoke каркас.
   - PARTIAL: полный DDL parity c исходным ТЗ.

## Очередь Доделок До Рабочей Модели (строго)

1. `Q1` Data correctness:
   - train-from-core;
   - timeframe normalization;
   - postgres incremental/status fix.

2. `Q2` Release safety:
   - mandatory stage gate before promote;
   - unified deployment gates.

3. `Q3` Storage parity:
   - full section-21 DDL parity + smoke `file/postgres`.

4. `Q4` Security/NFR:
   - real vault/kms integration;
   - inference service KPI/SLA contour.

5. `Q5` Final audit:
   - повторная сверка только с исходным ТЗ;
   - перевод всех `PARTIAL/TODO` в `DONE`.

## Update 2026-05-21 (Q1 start, in code)

1. Добавлен модуль нормализации таймфреймов:
   - `src/mlbotnav/timeframes.py` (`canonical_timeframe`, aliases, delta).
2. По умолчанию чтение датасета переведено на `core`:
   - `src/mlbotnav/dataset.py` (`load_ohlcv_range(..., layer=\"core\")`).
3. Нормализация `1h/4h` и совместимость с legacy `60m/240m` добавлены в:
   - `dataset`, `data_contract`, `dq`, `context_contract`, `context_dq`.
4. Исправлен incremental статус для Postgres (`date` теперь не пустая строка):
   - `src/mlbotnav/ingest_incremental.py`.
5. Добавлен watermark fallback по alias-таймфреймам для инкрементальных контуров:
   - `ingest_incremental`, `ingest_context_incremental`.

## Update 2026-05-21 (Q2 start, in code)

1. Добавлен единый deployment gate перед promote:
   - `src/mlbotnav/release_gate.py`.
2. `model_registry.promote_if_pass` теперь сначала проходит unified deployment gate, потом promotion-guard.
3. В политике проекта включен mandatory stage gate перед promote:
   - `configs/prod_policy.yaml -> prod.promotion.deployment_gate`.
   - Требование: `READY` или `last_completed_stage=D90`.
4. Добавлены unit tests для deployment gate:
   - `tests/test_release_gate.py`.
