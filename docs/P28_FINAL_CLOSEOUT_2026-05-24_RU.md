# P28 — Финальный closeout TZ_FEATURES_BLOCK

## Итоговый статус
Блок `TZ_FEATURES_BLOCK` закрыт и готов к рабочему контуру.

## Проверенный рабочий контур
1. Канон таблиц: `table_canon_pack` (CSV/XLSX).
2. Проверка сходимости: `table_convergence_5plus`.
3. Цепочка таблиц: `audit_table_chain --require-trades`.
4. Контроль конфигурации/источников/гейтов:
   - `features_block_audit`
   - `orderbook_source_audit --expect-status active`
   - `tz_gate_runner`
   - `p72_freeze_ready_check`

## Финальные команды запуска
### Combined (рекомендуется)
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
  -StepLabel P28
```

### Table-chain only
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p23_operator_unified.ps1 -Mode table_chain -StepLabel P28
```

### Быстрый отчет PASS
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p24_latest_pass_report.ps1
```

## Контрольный перечень артефактов
- `reports/qa_gate/daily_long_short_cycle_*.json`
- `reports/qa_gate/table_convergence_5plus_*.json`
- `reports/table_canon_current/audit_chain_report.json`
- `reports/qa_gate/features_block_audit_*.json`
- `reports/qa_gate/orderbook_source_audit_*.json`
- `reports/qa_gate/tz_gate_*.json`
- `reports/qa_gate/p72_freeze_ready_*.json`
- `reports/qa_gate/p24_latest_pass_*.json`
- `reports/qa_gate/p26_audit_lock_*.json`
- `reports/qa_gate/p27_handoff_package_*.json`

## Примечание
Long/short разделены по режимам, смешивание допускается только в `combined`.
