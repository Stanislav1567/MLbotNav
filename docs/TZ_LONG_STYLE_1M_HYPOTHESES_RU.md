# TZ: LONG STYLE 1M (Гипотезы)

## Цель
- Работать только в `timeframe=1m` и только `long_only`.
- Искать не одну фиксированную EMA-логику, а набор тренд-гипотез.
- Отбирать кандидаты по OOS-результату в `exchange_like` режиме.

## Что зашито в код
- Новый профиль `--long-style-1m` в `adaptive_auto_train`.
- Профиль перебирает гипотезы тренда по повторам:
  - `none`
  - `ema_gap_sign`
  - `ema_gap_sign` + `min_abs_ema_gap=0.02`
  - `ema_cross_20_50`
  - `ema_cross_20_200`
  - `ema_stack_bull`
  - `channel_breakout_50`
  - `adx_trend_18`
- Можно задать собственный порядок гипотез через `--trend-hypothesis-grid`.

## Правила запуска
- Для профиля обязательно `--timeframe 1m`.
- Профиль автоматически фиксирует `signal_mode=long_only`.
- Режим исполнения для реалистичных результатов: `--execution-mode exchange_like`.

## Что смотреть в отчете
- В `adaptive_loop_*.json` каждый repeat содержит:
  - `trend_filter`
  - `min_abs_ema_gap`
  - `oos_net_return_pct`
  - `oos_trades`
- Это дает прозрачный ответ, какая гипотеза отработала лучше.

