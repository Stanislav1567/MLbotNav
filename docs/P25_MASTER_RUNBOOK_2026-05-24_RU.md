# P25 — Мастер-ранбук TZ_FEATURES_BLOCK (единая страница)

## 1. Назначение
Единая операционная страница для ежедневной работы: запуск, контроль, артефакты, stop/go.

## 2. Базовые правила
1. Рабочая папка: `C:\Users\007\Desktop\MLbotNav`.
2. Запускать только закрытые дни (не текущий незакрытый день).
3. Long и short не смешивать вне режима `combined`.
4. После каждого запуска обязательна проверка PASS-цепочки.
5. Лимит CPU: до 85%.
6. Перед запуском закрыть Excel/просмотрщики файлов из `reports/table_canon_current/data` (иначе возможен lock `WinError 32`).
7. После каждого шага фиксировать результат в `docs/CHANGELOG_CHRONOLOGY_RU.md` (append-only).

## 3. Основные команды
### 3.1 Единый операторский запуск (рекомендовано)
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p23_operator_unified.ps1 `
  -Mode combined `
  -Symbol SOLUSDT `
  -Timeframe 1m `
  -TrainDate 2026-05-19 `
  -TestDate 2026-05-20 `
  -Repeats 1 `
  -Threads 8 `
  -SearchWorkers 8 `
  -StepLabel P25
```

### 3.2 Только long
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p23_operator_unified.ps1 -Mode long -StepLabel P25
```

### 3.3 Только short
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p23_operator_unified.ps1 -Mode short -StepLabel P25
```

### 3.4 Только table-chain (CSV/XLSX + движок + аудит)
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p23_operator_unified.ps1 -Mode table_chain -StepLabel P25
```

### 3.5 Быстрый отчет последних PASS-артефактов
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p24_latest_pass_report.ps1
```

## 4. PASS-цепочка (обязательная)
1. `daily_long_short_cycle_*.json` (для long/short/combined)
2. `table_convergence_5plus_*.json`
3. `reports/table_canon_current/audit_chain_report.json`
4. `features_block_audit_*.json`
5. `orderbook_source_audit_*.json` (`expect active`)
6. `tz_gate_*.json`
7. `p72_freeze_ready_*.json`

## 5. Где смотреть таблицы
- `reports/table_canon_current/data/candles_canonical.xlsx`
- `reports/table_canon_current/data/feature_frame.xlsx`
- `reports/table_canon_current/data/feature_frame_full.xlsx`
- `reports/table_canon_current/data/readable_tables_ru.xlsx`
- `reports/table_canon_current/data/feature_dictionary_ru.xlsx`

## 6. Stop/Go
- GO: все обязательные отчеты из раздела 4 = `PASS`.
- STOP: любой `FAIL` -> сначала исправление причины -> повтор полной цепочки.

## 7. Связанные документы
- `docs/P19_DAILY_STOP_GO_RUNBOOK_2026-05-24_RU.md`
- `docs/P20_RELEASE_PACKAGE_2026-05-24_RU.md`
- `docs/P24_OPERATOR_CHECKLIST_2026-05-24_RU.md`

## 8. P14 — Боевой turbo-шаблон (раздельно long/short)
### 8.1 Подготовка окружения
```powershell
cd C:\Users\007\Desktop\MLbotNav
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='src'
$env:OMP_NUM_THREADS='12'
$env:MKL_NUM_THREADS='12'
$env:OPENBLAS_NUM_THREADS='12'
$env:NUMEXPR_NUM_THREADS='12'
```

### 8.2 Turbo long_only (1d train -> next 1d test)
```powershell
python -m mlbotnav.adaptive_auto_train `
  --symbol SOLUSDT `
  --timeframe 1m `
  --train-start 2026-05-19 `
  --train-end 2026-05-19 `
  --test-day 2026-05-20 `
  --signal-mode long_only `
  --speed-profile turbo `
  --repeats 1 `
  --min-train-rows 500 `
  --n-folds 3 `
  --cpu-max-pct 85 `
  --max-threads 12 `
  --allow-subgoal-candidates `
  --temporary-unlock-readiness `
  --unlock-reason "P14 turbo long 1d1d"
```

### 8.3 Turbo short_only (1d train -> next 1d test)
```powershell
python -m mlbotnav.adaptive_auto_train `
  --symbol SOLUSDT `
  --timeframe 1m `
  --train-start 2026-05-19 `
  --train-end 2026-05-19 `
  --test-day 2026-05-20 `
  --signal-mode short_only `
  --speed-profile turbo `
  --repeats 1 `
  --min-train-rows 500 `
  --n-folds 3 `
  --cpu-max-pct 85 `
  --max-threads 12 `
  --allow-subgoal-candidates `
  --temporary-unlock-readiness `
  --unlock-reason "P14 turbo short 1d1d"
```

### 8.4 Обязательная цепочка после каждого smoke/боевого шага
1. Берем соответствующий OOS-отчет (`long_only` или `short_only`).
2. Запускаем table-chain:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p23_operator_unified.ps1 `
  -Mode table_chain `
  -Symbol SOLUSDT `
  -Timeframe 1m `
  -TrainDate 2026-05-19 `
  -TestDate 2026-05-20 `
  -OosReportPath "<ABS_OOS_PATH>" `
  -StepLabel P14
```
3. Фиксируем latest-pass:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p24_latest_pass_report.ps1 `
  -SourceP23ReportPath "<ABS_P23_PATH>"
```
4. Проверяем lock-аудит:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p26_audit_lock.ps1 `
  -Symbol SOLUSDT -Timeframe 1m -TestDate 2026-05-20
```

### 8.5 CPU-профили ускорения (обязательная фиксация)
1. Целевой потолок загрузки CPU: `85%`.
2. Профиль `FAST-8`:
   1. `--max-threads 8`
   2. `--search-workers 8`
   3. `--cpu-max-pct 85`
3. Профиль `FAST-9`:
   1. `--max-threads 9`
   2. `--search-workers 9`
   3. `--cpu-max-pct 85`
4. Порядок применения:
   1. Сначала запускать `FAST-8`.
   2. Если CPU стабильно ниже 75% и нет деградации, переключаться на `FAST-9`.
   3. Если появляется деградация (thrash/скачки времени/ошибки), откат к `FAST-8`.

### 8.6 Шаблон запуска adaptive_auto_train с FAST-8
```powershell
python -m mlbotnav.adaptive_auto_train `
  --symbol SOLUSDT `
  --timeframe 1m `
  --train-start 2026-05-19 `
  --train-end 2026-05-19 `
  --test-day 2026-05-20 `
  --test-end-day 2026-05-20 `
  --signal-mode short_only `
  --search-engine optuna `
  --optuna-stage C `
  --optuna-n-trials-override 8 `
  --optuna-timeout-sec-override 600 `
  --cpu-max-pct 85 `
  --max-threads 8 `
  --search-workers 8 `
  --execution-mode exchange_like `
  --order-type market `
  --allow-subgoal-candidates `
  --temporary-unlock-readiness `
  --unlock-reason "FAST-8 profile run"
```

### 8.7 Шаблон запуска adaptive_auto_train с FAST-9
```powershell
python -m mlbotnav.adaptive_auto_train `
  --symbol SOLUSDT `
  --timeframe 1m `
  --train-start 2026-05-19 `
  --train-end 2026-05-19 `
  --test-day 2026-05-20 `
  --test-end-day 2026-05-20 `
  --signal-mode short_only `
  --search-engine optuna `
  --optuna-stage C `
  --optuna-n-trials-override 8 `
  --optuna-timeout-sec-override 600 `
  --cpu-max-pct 85 `
  --max-threads 9 `
  --search-workers 9 `
  --execution-mode exchange_like `
  --order-type market `
  --allow-subgoal-candidates `
  --temporary-unlock-readiness `
  --unlock-reason "FAST-9 profile run"
```

### 8.8 Быстрый single-pass smoke (строго 1 повтор без profile expansion)
Назначение: быстрый контроль Optuna-контура без раздувания до `repeats_effective > 1`.

```powershell
python -m mlbotnav.adaptive_auto_train `
  --symbol SOLUSDT `
  --timeframe 1m `
  --train-start 2026-05-19 `
  --train-end 2026-05-19 `
  --test-day 2026-05-20 `
  --test-end-day 2026-05-20 `
  --signal-mode short_only `
  --search-engine optuna `
  --optuna-stage B `
  --optuna-n-trials-override 1 `
  --optuna-timeout-sec-override 60 `
  --cpu-max-pct 85 `
  --max-threads 8 `
  --search-workers 8 `
  --allow-subgoal-candidates `
  --disable-backlog-active-append `
  --disable-hypothesis-profile `
  --enforce-repeats-effective-match `
  --temporary-unlock-readiness `
  --unlock-reason "FAST-8 single-pass smoke"
```

Проверка результата:
1. В summary должно быть `repeats_requested=1`.
2. В summary должно быть `repeats_effective=1`.
3. Если `repeats_effective > 1`, значит включился профиль гипотез или backlog-расширение.

### 8.9 Launcher-скрипт single-pass (P185)
Для исключения ручных ошибок использовать готовый launcher:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_p185_optuna_single_pass.ps1 `
  -Mode short_only `
  -UseTemporaryUnlock
```

Примечание:
1. Launcher по умолчанию после прогона автоматически выполняет:
   1. `python -m mlbotnav.optuna_single_pass_ledger_audit`
   2. `python -m mlbotnav.text_guard`
2. Для диагностики без post-audit:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p185_optuna_single_pass.ps1 `
  -Mode short_only `
  -UseTemporaryUnlock `
  -SkipPostAudit
```

Быстрая проверка без запуска:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_p185_optuna_single_pass.ps1 `
  -Mode short_only `
  -DryRun
```

Реестр запусков (общая таблица):
1. `reports/qa_gate/optuna_single_pass_runs.csv`
2. Поля: `task_id`, `mode`, `repeats_requested`, `repeats_effective`, `result_status`, `oos_net_return_pct`, `summary_path`.
3. Обязательный аудит реестра после правок launcher/формата:
```powershell
python -m mlbotnav.optuna_single_pass_ledger_audit
```
