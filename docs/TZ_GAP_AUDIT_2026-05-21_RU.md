# ТЗ Аудит: Что Не Готово До Полностью Рабочей Модели

Дата: 2026-05-21
Проект: `C:\Users\007\Desktop\MLbotNav`
Источник требований: `TECH_SPEC_ML_PLATFORM_RU.md` (v1.0)

## 1) Блокеры до режима "модель полностью готова"

1. Не реализованы обязательные источники данных кроме OHLCV.
Требование ТЗ: funding rate, open interest, внешние маркеры риска.
Факт: в коде нет ingest-модулей/контрактов для funding/OI/макро-маркеров.

2. Нет полноценного security-контура KMS/Vault/TLS-at-rest.
Требование ТЗ: секреты только через vault/KMS, шифрование в транзите и на диске.
Факт: секреты берутся из `.env`/`SOURCE_ENV_PATH`; signing есть, но KMS/Vault/TLS policy-runtime нет.

3. Нет формализованного malware-scan в CV-контуре.
Требование ТЗ (контур CV): hash + perceptual hash + dedup + malware-scan.
Факт: есть sha256/phash/dedup, malware scan отсутствует.

4. CV Analyzer не завершен до полного состава артефактов.
Требование ТЗ: хранить original/overlay/masks/metadata/decision.
Факт: есть original/overlay/metadata/decision, но `mask` артефакты не формируются.

5. Нет production-расписания retrain/event-trigger.
Требование ТЗ: schedule retrain (например, 1/сутки) + event retrain при drift.
Факт: есть CLI и `prod_cycle`, но нет планировщика/автотриггера retrain.

6. Drift alert <= 2 минут не гарантирован.
Требование ТЗ: дрейф-алерт не позднее 2 минут после нарушения порога.
Факт: alert создается при запуске `monitor_drift`, но SLA доставки/trigger <=2 мин не зафиксирован.

7. SQL DDL слой не внедрен в runtime.
Требование ТЗ (раздел 21): схемы raw/core/analytics/dq/meta в PostgreSQL.
Факт: текущая реализация на CSV/Parquet; DB-слой отсутствует.

8. Неполный набор обязательных торговых полей.
Требование ТЗ: хранить `expected_move_pct`, `tp_reach_prob`, `time_to_target`.
Факт: первые два есть, `time_to_target` отсутствует в backtest/pipeline/inference логах.

9. Неполный набор trading-метрик.
Требование ТЗ: Sharpe, Sortino, Max Drawdown, CAGR, hit-rate.
Факт: есть sharpe_like/hit_rate/MDD, но нет Sortino/CAGR.

10. Нефункциональные SLA (availability 99.5%, inference p95 <=300ms) не закрыты как системные KPI.
Требование ТЗ: измеримые SLA прод-инференса.
Факт: есть `monitor_sla` по шагам цикла, но нет API-сервиса инференса и uptime/latency контура как сервиса.

## 2) Что уже готово и не является блокером

1. Bybit OHLCV ingest day/incremental, watermark, idempotency, late-data reconcile.
2. DQ + quarantine + partial_success + retry/backoff/jitter.
3. Feature pipeline, walk-forward, leakage checks, backtest fee/slippage.
4. Registry, champion/challenger, rollback guard, negative memory, stage ladder.
5. TA контур, inference/paper trading, packs/signatures/audit-chain, CPU budget.
6. Minute-first gate и зафиксированный minute итог.

## 3) Управленческая фиксация

До закрытия блокеров из раздела 1 проект не считается "полностью рабочей моделью" по ТЗ.
Рекомендуемый процесс: инженерные доработки -> повторный audit -> только затем полноценные обучающие прогоны как основной этап.

## Update 2026-05-21 (later)

Блокер по п.1 (funding + open interest ingestion) закрыт:
1. Добавлены `ingest_context_day` и `ingest_context_incremental` (Bybit v5, UTC day-batch/incremental).
2. Добавлены контракты и DQ для market context (`context_contract`, `context_dq`).
3. Добавлены артефакты DQ/meta для контекста:
   - `data/dq/market_context_quality_report.csv`
   - watermark/run журналы в `data/meta`.
4. Приемочный smoke по `SOLUSDT` за `2026-05-20` успешен.

## Update 2026-05-21 (P2 start)

Блокер по SQL runtime (п.7) переведен в статус `IN PROGRESS`:
1. Добавлен PostgreSQL DDL runtime файл: `sql/postgres_storage_runtime.sql`.
2. Добавлен runtime adapter `file|postgres`: `src/mlbotnav/postgres_runtime.py`.
3. `meta_store`/`storage_registry` и ingest контуры поддерживают переключение backend через `STORAGE_MODE`.
4. Финальная приемка п.7 будет закрыта после smoke на окружении с `POSTGRES_DSN`:
   - `python -m mlbotnav.postgres_runtime --ensure-schema --smoke`.

## Update 2026-05-21 (P3 start)

Блокеры по CV hardening (п.3 и п.4) переведены в статус `IN PROGRESS`:
1. В `cv_ingest` добавлен policy-driven malware hook:
   - scanner status (`clean/suspicious/disabled`);
   - mode (`block|quarantine|report`) из `configs/security_governance.yaml`;
   - quarantine path: `data/quarantine/cv/...`;
   - suspicious inputs не допускаются в рабочий CV контур (`allowed_for_cv=false`).
2. В `cv_overlay_pipeline` добавлен `mask` artifact:
   - `*_mask.png` рядом с `original/overlay/metadata/decision`.
3. Metadata/decision расширены полями `mask_file`, `scanner_status`, `pipeline_version`.

## Update 2026-05-21 (P4 start)

Блокер по security hardening (п.2) переведен в `IN PROGRESS`:
1. Добавлен provider-слой секретов (`env|vault|kms`) в `src/mlbotnav/security.py`.
2. Добавлен `security gate` с отчетом `reports/security/security_gate_<stage>_*.json`.
3. `model_registry.promote_if_pass` теперь блокирует promote при `security_gate_fail`.
4. Добавлен CLI-check:
   - `python -m mlbotnav.security --stage promote`.
5. Обновлены конфиги:
   - `configs/security_governance.yaml` (`security.provider`, `security.gate`, `security.cv_scan`).

## Update 2026-05-21 (P5 start)

Блокеры по automation/SLA (п.5 и п.6) переведены в `IN PROGRESS`:
1. Добавлен event-trigger модуль:
   - `src/mlbotnav/drift_retrain_trigger.py`
   - формирует `reports/monitoring/retrain_trigger_*.json` и поле `alert_to_trigger_sec`.
2. `prod_cycle` расширен шагом `drift_retrain_trigger`.
3. Добавлен scheduler runner:
   - `src/mlbotnav/scheduler_runner.py`
   - поддерживает циклы `ingest_incremental|prod_cycle|drift_trigger|all`.
4. `monitor_sla` учитывает breach по drift-trigger SLA.

## Update 2026-05-21 (P6 start)

Блокеры по metric completeness (п.8 и п.9) переведены в `IN PROGRESS`:
1. В backtest добавлены:
   - `time_to_target_bars`, `time_to_target_sec`;
   - summary metrics `sortino`, `cagr`, `time_to_target_*_avg`.
2. В inference events/report добавлен `time_to_target_bars` (оценка по horizon).
3. Gate-логика расширена проверками `min_sortino`, `min_cagr` (в `configs/thresholds.yaml`).
