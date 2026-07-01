# P24 — Шаблон ручного операционного контроля (VS Code)

## 1) До запуска
1. Проверить активность `.venv` и `PYTHONPATH=src`.
2. Проверить, что дата теста закрыта (не текущий незакрытый день).
3. Выбрать режим запуска:
   - `long` (только long)
   - `short` (только short)
   - `combined` (оба режима)
   - `table_chain` (только канон таблиц + проверки)
4. Запускать только из корня проекта `C:\Users\007\Desktop\MLbotNav`.

## 2) Во время запуска
1. Следить за логом шагов `01..05` (или `03L/03S`) в `p23_operator_unified_*.log`.
2. Не останавливать чужие процессы.
3. Контроль CPU: держать не выше 85% по политике проекта.

## 3) После запуска (обязательно)
Проверить PASS-файлы:
1. `daily_long_short_cycle_*.json` (если режим `combined/long/short`)
2. `table_convergence_5plus_*.json`
3. `audit_chain_report.json`
4. `features_block_audit_*.json`
5. `orderbook_source_audit_*.json` (`expect active`)
6. `tz_gate_*.json`
7. `p72_freeze_ready_*.json`

## 4) Единая команда запуска
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
  -StepLabel P24
```

## 5) Быстрый контроль последних PASS-артефактов
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p24_latest_pass_report.ps1
```
