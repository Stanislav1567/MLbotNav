# ТЗ: Автофиксация лучшего прогона (Top Strategy)

## 1) Цель
После завершения adaptive-прогона система должна автоматически публиковать **лучший OOS-результат** в одном месте, чтобы не искать вручную по множеству отчетов.

## 2) Критерий выбора TOP-1
- Основной критерий: `max(oos.backtest.net_return_pct)` в рамках одного adaptive run.
- Комиссии/проскальзывание учитываются как в OOS-отчете.

## 3) Результат публикации (без ZIP)
- Единая точка входа: `reports/top_strategy/TOP_LATEST.json`
- Папка с материалами конкретного top-прогона:
  - `reports/top_strategy/top_<symbol>_<tf>_<test_day>_<ts>_TF-<TF>_D-1_RET-<+/-X.XXXXpct>/`

Внутри папки top:
- `top_strategy_card.json` (структурированная карточка)
- `TOP_STRATEGY_CARD.md` (читаемый summary)
- `oos_report.json`
- `oos_backtest_trades.csv`
- `train_pipeline_report.json`
- `trade_simulation.png` (с входами/выходами)
- `trade_simulation_summary.json`
- `ranked_candidates.json` (ранжирование всех повторов run)

История:
- `reports/top_strategy/TOP_HISTORY.jsonl` (append-only лог карточек)

## 4) Что должно быть видно “глазами” сразу
В `TOP_LATEST.json` обязательно:
- метка прогона (`symbol`, `timeframe`, `test_day`)
- Best OOS (%)
- кол-во входов/выходов, long/short, wins/losses
- `notional_usd` и `net_pnl_total_usd`
- ссылки на все ключевые артефакты

## 5) Требования надежности
- Ошибка публикации top не должна ломать основной adaptive-прогон.
- При ошибке публикации она пишется в `summary.top_strategy_error`.
- Основной отчет прогона сохраняется в любом случае.

## 6) Definition of Done
- После каждого adaptive run появляется/обновляется `TOP_LATEST.json`.
- Создается новая папка `top_*` с полным набором артефактов.
- В `adaptive_loop_*.json` есть поле `top_strategy` с путями на опубликованный top.
