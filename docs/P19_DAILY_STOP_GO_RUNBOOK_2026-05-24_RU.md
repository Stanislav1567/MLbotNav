# P19 — Рабочий Регламент Stop/Go (daily запуск)

## 1. Цель
- Единый ежедневный контур запуска long/short и проверки качества.
- Без смешивания режимов: long и short запускаются раздельно или через combined-обертку.
- После каждого запуска обязательны проверки CSV/XLSX, chain, gate и freeze.

## 2. Команды запуска

### 2.1 Только long
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p18_daily_long_only.ps1 `
  -TrainDate 2026-05-19 `
  -TestDate 2026-05-20 `
  -Repeats 1 `
  -Threads 8 `
  -SearchWorkers 8
```

### 2.2 Только short
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p18_daily_short_only.ps1 `
  -TrainDate 2026-05-19 `
  -TestDate 2026-05-20 `
  -Repeats 1 `
  -Threads 8 `
  -SearchWorkers 8
```

### 2.3 Combined (рекомендуется daily)
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p18_daily_combined.ps1 `
  -StepLabel P19 `
  -TrainDate 2026-05-19 `
  -TestDate 2026-05-20 `
  -Repeats 1 `
  -Threads 8 `
  -SearchWorkers 8
```

## 3. Обязательный порядок проверок (после запуска)
1. `daily_long_short_cycle_*.json` должен быть `PASS`.
2. `table_convergence_5plus_*.json` должен быть `PASS` для long и short.
3. `hypothesis_coverage_long_only_*.json` и `hypothesis_coverage_short_only_*.json` должны быть `PASS`.
4. `features_block_audit_*.json` должен быть `PASS`.
5. `orderbook_source_audit_*.json --expect-status active` должен быть `PASS`.
6. `tz_gate_*.json` для текущего шага должен быть `PASS`.
7. `p72_freeze_ready_*.json` должен быть `PASS`.

## 4. Критерии Stop/Go

### GO (разрешено продолжать)
- Все 7 проверок из раздела 3 — `PASS`.
- В `orderbook_source_audit` источник активен (`expect-status active` проходит).
- Нет пропусков обязательных таблиц (`signal_frame`, `execution_trace`, `strategy_summary`, словари).

### STOP (остановить дальнейший запуск)
- Любой из отчетов раздела 3 имеет `FAIL`.
- `orderbook_source_audit` не проходит в `active`.
- `tz_gate_runner` не проходит.
- `p72_freeze_ready_check` не проходит.

## 5. Действия при STOP
1. Не запускать следующий цикл.
2. Сначала исправить причину FAIL в контуре данных/движка/конфига.
3. Повторить полный контур проверок.
4. Только после полного `PASS` возвращаться к ежедневным прогонам.

## 6. Ограничения исполнения
- Лимит CPU: до `85%`.
- Не трогать чужие параллельные прогоны.
- Chain-проверки для `reports/table_canon_current` запускать последовательно (без параллельных вызовов на один и тот же run-dir).
