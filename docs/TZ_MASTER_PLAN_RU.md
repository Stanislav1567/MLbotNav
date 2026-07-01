# MLbotNav: Мастер-план выполнения оставшихся пунктов ТЗ

Дата плана: 2026-05-21
Источник требований: `TECH_SPEC_ML_PLATFORM_RU.md`

## 1. Текущее состояние

- DONE: ingestion day/incremental, DQ, watermark, baseline train, candles+EMA+volume, unified train-eval pipeline.
- IN PROGRESS: усиление фич и стабильность gate.
- TODO: champion/challenger automation, drift monitor, rollback flow, CV integrity contour, packs with checksums, security/governance hardening.

## 2. План по оставшимся пунктам

### Phase R1: Champion/Challenger + Gates
1. Реестр кандидатов и активной champion-модели.
2. Автоматическое добавление кандидата после каждого pipeline-run.
3. Правило promote только при `gate.pass = true`.
4. Аудит принятия/отклонения в `reports/registry`.

Критерий приемки:
- Есть `models/registry/champion.json` и `models/registry/candidates.jsonl`.

### Phase R2: Drift/Monitoring
1. Ежедневный drift-report по фичам (reference vs current).
2. Пороговый alert-file при превышении drift threshold.
3. История отчётов в `reports/monitoring`.

Критерий приемки:
- Формируется `drift_report_*.json` и `drift_alert_*.json` при нарушении порога.

### Phase R3: Packs (ранцы)
1. Сбор ранца по дню: свечи, dq, pipeline-report, модель, графики.
2. Подсчет sha256 по артефактам.
3. Индекс ранцев `packs/index.csv`.

Критерий приемки:
- Для дня создаётся `packs/YYYY-MM-DD/session_id/manifest.json` + `checksums.csv`.

### Phase R4: CV Integrity Contour (минимальный)
1. Прием скриншота с source-id и timestamp.
2. sha256 и простая perceptual-сигнатура.
3. Metadata JSON + локальный индекс.

Критерий приемки:
- Есть `data/cv/original/...`, `metadata.json`, `cv_index.csv`.

### Phase R5: Security/Governance Hardening (минимум)
1. Централизованный audit-log по ключевым операциям.
2. Политика хранения/маскировки секретов в отчетах.
3. Базовый runbook и SOP-файлы.

Критерий приемки:
- В `logs/audit.log` пишутся операции ingest/train/promote/pack/cv_ingest.

### Phase R6: Улучшение ML-качества до первого PASS
1. Расширить feature-set `Structure/Pattern`.
2. Запустить horizon-scan + threshold-scan.
3. Зафиксировать первый PASS-run и назначить champion.

Критерий приемки:
- Есть как минимум один pipeline report с `gate.pass=true`.

## 3. Последовательность выполнения

1. R1 -> R2 -> R3 -> R4 -> R5 (инфраструктурные контуры).
2. Параллельно R6 до первого PASS.
3. После первого PASS включить регулярный цикл incremental ingest -> train-eval -> registry decision -> drift check -> pack.

## Жесткие правила процесса (обязательно)
1. Сначала полностью закрываем минутный этап на `1m`.
2. Показываем итоговый визуальный отчет: график, точки входа/выхода, метрики.
3. Только после явного подтверждения результата разрешается 30-дневное окно на `1m`.
4. До подтверждения 30-дневный прогон блокируется, остаемся на минутном этапе по gate.
5. Gate-файл: `configs/workflow_gate.yaml`.
