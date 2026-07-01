# Строгий План Доделок По ТЗ (До Полностью Рабочей Модели)

Дата: 2026-05-21
Режим: сначала закрываем инженерные gap, затем выходим на обучение как этап эксплуатации.

## Фаза 0. Freeze и контроль процесса (P0)

1. Ввести кодовый флаг готовности проекта (`project_ready=false`) и блокировать train/retrain/prod-cycle heavy runs, пока не завершены критические пункты.
2. Разрешить только audit/ingest/validation dry-run до статуса ready.
3. Добавить отчет `reports/readiness/readiness_check_*.json`.

Критерий приемки:
1. Любой запуск обучения при `project_ready=false` завершаетcя с явной причиной блокировки.
2. Readiness-отчет показывает checklist по блокерам.

## Фаза 1. Data-source expansion (P1)

1. Добавить ingestion funding rate и open interest (Bybit v5), с UTC, day-batch и incremental.
2. Добавить контракты данных и DQ для funding/OI.
3. Добавить хранение в `raw/core/meta` и связать с текущим watermark/run журналом.

Критерий приемки:
1. По каждой дате есть записи OHLCV + funding + OI без дублей.
2. DQ отчеты формируются для всех источников.

## Фаза 2. Storage/DDL runtime (P2)

1. Реализовать опциональный PostgreSQL storage adapter по разделу 21 (raw/meta/dq).
2. Сохранить совместимость с текущим файловым контуром (режим `file`/`postgres`).
3. Добавить миграционный скрипт и smoke-проверку консистентности.

Критерий приемки:
1. Один и тот же ingest run корректно пишется в выбранный backend.
2. Уникальные ключи и upsert работают по ТЗ.

## Фаза 3. CV hardening (P3)

1. Добавить malware-scan hook в `cv_ingest` (policy-driven: block/quarantine).
2. Добавить генерацию mask-артефактов в `cv_overlay_pipeline`.
3. Расширить metadata/decision схему под masks + scanner status.

Критерий приемки:
1. На каждый CV run есть `original + overlay + mask + metadata + decision`.
2. infected/invalid файлы не проходят в рабочий CV контур.

## Фаза 4. Security hardening (P4)

1. Вынести секреты в provider-слой (`env|vault|kms`) с обязательной политикой выбора.
2. Добавить конфиг-политику TLS/at-rest encryption checks и аудит нарушений.
3. Интегрировать security-gate в release-пайплайн (до promote).

Критерий приемки:
1. Promote блокируется при security-gate fail.
2. В audit есть след policy check и источник секрета.

## Фаза 5. Monitoring/automation (P5)

1. Добавить планировщик (cron/heartbeat runner) для ingest + retrain.
2. Добавить event-trigger retrain от drift alert.
3. Зафиксировать SLA доставки drift-alert <= 2 минут и проверить на smoke.

Критерий приемки:
1. Есть автоматический цикл без ручного старта.
2. Drift breach приводит к alert и retrain-trigger в пределах SLA.

## Фаза 6. Metric completeness (P6)

1. Добавить `time_to_target` в backtest/pipeline/inference logs.
2. Добавить Sortino и CAGR в торговые отчеты.
3. Обновить gate-правила под полный набор метрик ТЗ.

Критерий приемки:
1. 100% сделок/решений содержат обязательные поля ТЗ.
2. Отчеты содержат полный набор ML + Trading метрик.

## Фаза 7. Final readiness audit (P7)

1. Повторный полный audit по ТЗ с чеклистом acceptance criteria.
2. Подтверждение `project_ready=true`.
3. Только после этого запуск полноценного цикла обучения/дообучения.

Критерий приемки:
1. Все пункты из `docs/TZ_GAP_AUDIT_2026-05-21_RU.md` закрыты.
2. Есть финальный отчет `reports/readiness/final_tz_readiness_*.json`.

## Порядок выполнения (строго)

1. P0
2. P1
3. P2
4. P3
5. P4
6. P5
7. P6
8. P7

Переход к следующей фазе допускается только после фиксации артефакта приемки текущей фазы.

## Фиксация Прогресса (2026-05-21)

1. `P0` закрыт:
   - readiness freeze активен;
   - train/prod heavy actions блокируются при `project_ready=false`;
   - readiness reports пишутся в `reports/readiness/readiness_check_*.json`.

2. `P1` закрыт:
   - добавлены `funding + open_interest` ingest контуры:
     - `src/mlbotnav/ingest_context_day.py`
     - `src/mlbotnav/ingest_context_incremental.py`
   - добавлены контракты/DQ:
     - `src/mlbotnav/context_contract.py`
     - `src/mlbotnav/context_dq.py`
   - подключен meta/dq storage:
     - `data/dq/market_context_quality_report.csv`
     - `data/meta/ingest_watermark.csv`
     - `data/meta/ingest_run.csv`
   - приемочный smoke:
     - day run `2026-05-20` по `SOLUSDT` успешен;
     - incremental report: `reports/ingestion/context_incremental_SOLUSDT_20260521T134625Z.json`.
   - источник Bybit для OI интервала `1m` возвращает пусто; интервал помечается как `skipped`, рабочие OI интервалы: `5,15,30,60,240,D`.

3. `P2` в работе (engineering implementation completed, acceptance pending):
   - добавлен runtime-адаптер `file|postgres`:
     - `src/mlbotnav/postgres_runtime.py`
     - `sql/postgres_storage_runtime.sql`
   - `meta_store` и `storage_registry` переключаются по `STORAGE_MODE`.
   - ingest контуры (`ingest_day`, `ingest_context_day`) пишут upsert в `raw.*` при режиме `postgres`.
   - добавлен CLI smoke/migrate:
     - `python -m mlbotnav.postgres_runtime --ensure-schema --smoke`
   - acceptance `P2` будет закрыт после реального smoke на окружении с валидным `POSTGRES_DSN`.

4. `P3` в работе:
   - добавлен malware-scan hook в `src/mlbotnav/cv_ingest.py`:
     - policy `block|quarantine|report`;
     - scanner fields в metadata/index/audit;
     - suspicious файлы не проходят в рабочий CV-контур.
   - добавлен mask-слой в `src/mlbotnav/cv_overlay_pipeline.py`:
     - формируются `original + overlay + mask + metadata + decision`.
   - конфиг сканера вынесен в `configs/security_governance.yaml` (`security.cv_scan`).

5. `P4` в работе:
   - добавлен provider-слой секретов `env|vault|kms` (`src/mlbotnav/security.py`);
   - добавлен `security gate` с артефактами `reports/security/security_gate_<stage>_*.json`;
   - promote в `model_registry` теперь блокируется при `security_gate_fail`.

6. `P5` в работе:
   - добавлен `drift_retrain_trigger` с SLA-полем `alert_to_trigger_sec`;
   - `prod_cycle` запускает trigger шаг после drift-monitor;
   - добавлен `scheduler_runner` для циклических автоматизированных запусков;
   - `monitor_sla` учитывает breach по drift-trigger SLA.

7. `P6` в работе:
   - в backtest добавлены `time_to_target_*`, `sortino`, `cagr`;
   - inference-report дополнен `time_to_target_bars`;
   - gate thresholds дополнены `min_sortino`, `min_cagr`.

## Update 2026-05-21 (фикс правил minute-first и цели доходности)

1. Зафиксировано правило этапов:
   - сначала полный цикл на `1m` и коротком окне;
   - итог показывается пользователю;
   - только после подтверждения разрешается переход на `30` дней.
2. Зафиксирована целевая метрика для gate:
   - `gates.min_net_return_pct = 10.0` (нетто, после fee/slippage).
3. Зафиксировано правило динамического take-profit:
   - `tp_min_pct = 0.7 * min_expected_move_pct`;
   - реализовано через `tp_min_factor=0.7` и `dynamic_tp_enabled=true` по умолчанию.
4. Добавлен адаптивный авто-цикл под minute-first:
   - train-window `17-19` -> OOS `20`;
   - до `10` повторов поиска/обучения/валидации;
   - минусовые сетапы записываются в negative-memory и исключаются из следующих повторов.

## Update 2026-05-21 (фиксы F1-F5 + повторная приемка P2-P6)

1. Фиксы `F1-F5` внедрены:
   - readiness bypass по умолчанию отключен;
   - strict goal режим активен (`no_goal_candidate` без fallback на слабые сетапы);
   - readiness-state корректно восстанавливается после временного unlock;
   - парсинг stdout сделан устойчивым (поиск валидного JSON с конца);
   - negative-memory сегментирован по ключу окна/цели.
2. `P3_CV_HARDENING` закрыт:
   - подтвержден malware quarantine flow (`.ps1` -> quarantine);
   - подтверждены артефакты `original + overlay + mask + metadata + decision`.
3. Текущие открытые блокеры:
   - нет.
4. Дополнительно закрыты:
   - `P4_SECURITY`: promote security-gate passed с at-rest encryption check;
   - `P5_AUTOMATION`: scheduler + drift-trigger smoke passed (`alert_to_trigger_sec <= 120`);
   - `P6_METRICS`: обязательные поля `time_to_target/sortino/cagr` подтверждены в runtime-артефактах.
4. Сводный audit-артефакт:
   - `reports/readiness/p2_p6_acceptance_20260521T162425Z.json`.
   - `reports/readiness/p5_p6_acceptance_20260521T162904Z.json`.
5. Финальный статус:
   - `P2` закрыт после live PostgreSQL smoke (`ensure-schema + smoke ok`, missing tables = 0);
   - `project_ready=true`, `open_blockers=0`;
   - финальный readiness artifact: `reports/readiness/final_tz_readiness_20260521T163718Z.json`.
