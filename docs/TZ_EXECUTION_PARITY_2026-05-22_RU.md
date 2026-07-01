# ТЗ: Биржевая Идентичность Симуляции (Market/Limit) — 2026-05-22

## 1) Цель
Перевести оценку стратегии из исследовательского режима в максимально реалистичный режим исполнения, чтобы результаты прогона соответствовали логике реальных входов/выходов на бирже Bybit (фьючерсы SOLUSDT, 1m).

## 2) Аудит (что было до фикса)
1. Сигнал и доходность считались по схеме close->future close.
2. В фильтре входа использовался `future_return` (look-ahead).
3. Dynamic TP зависел от `future_return` (look-ahead).
4. Рендер вход/выход строился как смещение на horizon, а не по фактическому исполнению ордера.

Риск: завышенная/искаженная оценка стратегии относительно реального исполнения.

## 3) Требования к боевому режиму
1. Вход только на следующей свече после сигнала.
2. Поддержка типов входа:
   - `market`
   - `limit` (с настраиваемым offset).
3. Выходы:
   - `tp`
   - `sl`
   - `timeout` (по hold_bars).
4. Без использования будущих значений (`future_return`) в логике принятия входа/TP.
5. Комиссия/проскальзывание и плечо учитываются в итоговом PnL.
6. Рендер должен показывать фактические entry/exit из backtest-CSV.

## 4) Что внедрено
1. Добавлен режим `execution_mode`:
   - `research` (legacy)
   - `exchange_like` (новый боевой).
2. Добавлены параметры исполнения:
   - `order_type` = `market|limit`
   - `limit_offset_bps`
   - `hold_bars`.
3. В `exchange_like`:
   - вход по next bar;
   - TP/SL/timeout по high/low/close в окне удержания;
   - консервативная обработка двусмысленного бара (SL при одновременном касании TP/SL).
4. Убрана зависимость от `future_return` в фильтре входа для `exchange_like`.
5. Рендер обновлен: использует `entry_time_utc/exit_time_utc/entry_price/exit_price` из trades.
6. Прокинуто по контуру:
   - `search_gate_candidate`
   - `pipeline_train_eval`
   - `oos_evaluate`
   - `paper_trading`
   - `adaptive_auto_train`.

## 5) Проверка (как перепроверять сейчас)
### 5.1 Быстрый аудит режимов
Запуск сравнения одного и того же trained report в двух режимах:

```powershell
$env:PYTHONPATH='src'
python -m mlbotnav.audit_execution_parity `
  --train-pipeline-report <PATH_TO_PIPELINE_REPORT_JSON> `
  --test-day 2026-05-20 `
  --test-end-day 2026-05-21 `
  --signal-mode both `
  --leverage 10 `
  --order-type market `
  --limit-offset-bps 2
```

Артефакт: `reports/final_review/execution_parity_audit_*.json`.

### 5.2 Проверка графика
Убедиться, что в топ-папке есть:
1. `trade_simulation.png`
2. `trade_simulation_summary.json`
3. `oos_backtest_trades.csv` с полями entry/exit.

## 6) Критерии приемки
1. Нет look-ahead в `exchange_like` входах и TP-фильтрах.
2. OOS отчеты содержат `execution_mode/order_type/limit_offset_bps`.
3. График строится по фактическим entry/exit.
4. Для одинакового отчета `research` и `exchange_like` дают разные (реалистично более строгие) результаты.
5. Пайплайн проходит end-to-end без падений.

## 7) Ограничения
1. Это еще симулятор, не live-исполнение в стакан.
2. Частичное исполнение, глубина рынка и funding-impact пока не моделируются.
3. Для `limit` используется упрощенная модель касания в следующем баре.

## 8) Следующий шаг (P1)
1. Добавить модель исполнения maker/taker с вероятностью проскальзывания по волатильности.
2. Добавить модель частичного fill.
3. Добавить отдельные отчеты `entry_latency` и `fill_ratio`.
