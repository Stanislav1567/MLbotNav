# P20 — Финальный релизный пакет TZ_FEATURES_BLOCK

## 1) Цель
Закрепить единый рабочий контур daily-run для long/short, чтобы запуск, контроль и handoff выполнялись по одному регламенту без разночтений.

## 2) Единая команда daily-run (рекомендовано)
```powershell
powershell -ExecutionPolicy Bypass -File .\run_p18_daily_combined.ps1 `
  -StepLabel P20 `
  -TrainDate 2026-05-19 `
  -TestDate 2026-05-20 `
  -Repeats 1 `
  -Threads 8 `
  -SearchWorkers 8
```

## 3) Обязательные PASS-артефакты
1. `daily_long_short_cycle_*.json`
2. `table_convergence_5plus_*.json` (long + short)
3. `hypothesis_coverage_long_only_*.json`
4. `hypothesis_coverage_short_only_*.json`
5. `features_block_audit_*.json`
6. `orderbook_source_audit_*.json` с `expect-status active`
7. `tz_gate_*.json` для текущего шага
8. `p72_freeze_ready_*.json`

## 4) Матрица артефактов (где смотреть)
- Контур цикла: `reports/qa_gate/`
- OOS отчеты: `reports/final_review/`
- Топ-стратегии: `reports/top_strategy/`
- Табличный канон: `reports/table_canon_current/`
- Прогресс adaptive: `reports/adaptive/<mode>/`

## 5) Stop/Go
- GO: все пункты раздела 3 = PASS.
- STOP: любой FAIL, сначала фикс причины, потом полный перезапуск проверки.

## 6) Handoff (что передаем оператору)
1. Последний `daily_long_short_cycle_*.json`.
2. Последние PASS по `table_convergence_5plus` (long/short).
3. Последние PASS по `features_block_audit`, `orderbook_source_audit`, `tz_gate`, `p72_freeze_ready`.
4. Команду daily-run из раздела 2.
