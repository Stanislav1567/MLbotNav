# Русские названия фич и гипотез

Дата UTC: `2026-06-03T16:02:12Z`.

Источники:
1. `configs/features_block.yaml`
2. `configs/calibration_full_matrix_v1.yaml`
3. `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`

Правило: в карточке прогона заголовок берем из русского названия фичи или гипотезы. Техническое имя оставляем ниже отдельной строкой.

## Блоки
- `price_volatility` - Цена и волатильность
- `trend_momentum` - Тренд и импульс
- `volume_flow` - Объём и поток
- `density_profile` - Профиль плотности
- `structure_ta` - Структура и ТА
- `pattern` - Паттерны

## Фичи по слотам H001-H068
- `H001` - Доходность за 1 бар; тип: фича; блок: Цена и волатильность; technical: `price_volatility.ret_1`; статус: калибруется.
- `H002` - Доходность за 3 бара; тип: фича; блок: Цена и волатильность; technical: `price_volatility.ret_3`; статус: калибруется.
- `H003` - Доходность за 6 баров; тип: фича; блок: Цена и волатильность; technical: `price_volatility.ret_6`; статус: калибруется.
- `H004` - Доходность за 12 баров; тип: фича; блок: Цена и волатильность; technical: `price_volatility.ret_12`; статус: калибруется.
- `H005` - Доходность за 24 бара; тип: фича; блок: Цена и волатильность; technical: `price_volatility.ret_24`; статус: калибруется.
- `H006` - Диапазон high-low к open; тип: фича; блок: Цена и волатильность; technical: `price_volatility.hl_spread`; статус: не калибруется.
- `H007` - Скользящая волатильность 20; тип: фича; блок: Цена и волатильность; technical: `price_volatility.rolling_std_20`; статус: калибруется.
- `H008` - ATR(14); тип: фича; блок: Цена и волатильность; technical: `price_volatility.atr14`; статус: калибруется.
- `H009` - Разрыв EMA20-EMA50; тип: фича; блок: Тренд и импульс; technical: `trend_momentum.ema_gap`; статус: калибруется.
- `H010` - Наклон EMA20 за 5 баров; тип: фича; блок: Тренд и импульс; technical: `trend_momentum.ema_slope_5`; статус: калибруется.
- `H011` - Отклонение от EMA200; тип: фича; блок: Тренд и импульс; technical: `trend_momentum.ema200_gap`; статус: калибруется.
- `H012` - RSI(14); тип: фича; блок: Тренд и импульс; technical: `trend_momentum.rsi14`; статус: калибруется.
- `H013` - Линия MACD; тип: фича; блок: Тренд и импульс; technical: `trend_momentum.macd_line`; статус: калибруется.
- `H014` - Сигнальная линия MACD; тип: фича; блок: Тренд и импульс; technical: `trend_momentum.macd_signal`; статус: калибруется.
- `H015` - Гистограмма MACD; тип: фича; блок: Тренд и импульс; technical: `trend_momentum.macd_hist`; статус: калибруется.
- `H016` - ADX(14); тип: фича; блок: Тренд и импульс; technical: `trend_momentum.adx14`; статус: калибруется.
- `H017` - Стохастик K(14); тип: фича; блок: Тренд и импульс; technical: `trend_momentum.stoch_k14`; статус: калибруется.
- `H018` - Стохастик D(14); тип: фича; блок: Тренд и импульс; technical: `trend_momentum.stoch_d14`; статус: калибруется.
- `H019` - Изменение объёма; тип: фича; блок: Объём и поток; technical: `volume_flow.vol_chg`; статус: калибруется.
- `H020` - Z-оценка объёма; тип: фича; блок: Объём и поток; technical: `volume_flow.vol_z`; статус: калибруется.
- `H021` - Дельта объёма; тип: фича; блок: Объём и поток; technical: `volume_flow.delta_volume`; статус: калибруется.
- `H022` - Наклон OBV за 5 баров; тип: фича; блок: Объём и поток; technical: `volume_flow.obv_slope_5`; статус: калибруется.
- `H023` - MFI(14); тип: фича; блок: Объём и поток; technical: `volume_flow.mfi14`; статус: калибруется.
- `H024` - Дистанция до VWAP; тип: фича; блок: Объём и поток; technical: `volume_flow.vwap_distance`; статус: не калибруется.
- `H025` - Дистанция до VPOC окно 60; тип: фича; блок: Профиль плотности; technical: `density_profile.density_vpoc_distance_60`; статус: калибруется.
- `H026` - Доля объёма бина окно 60; тип: фича; блок: Профиль плотности; technical: `density_profile.density_bin_share_60`; статус: калибруется.
- `H027` - Доля объёма кластера окно 60; тип: фича; блок: Профиль плотности; technical: `density_profile.density_cluster_share_60`; статус: калибруется.
- `H028` - Доля объёма VPOC окно 60; тип: фича; блок: Профиль плотности; technical: `density_profile.density_vpoc_share_60`; статус: калибруется.
- `H029` - Дистанция до VPOC окно 240; тип: фича; блок: Профиль плотности; technical: `density_profile.density_vpoc_distance_240`; статус: калибруется.
- `H030` - Доля объёма бина окно 240; тип: фича; блок: Профиль плотности; technical: `density_profile.density_bin_share_240`; статус: калибруется.
- `H031` - Доля объёма кластера окно 240; тип: фича; блок: Профиль плотности; technical: `density_profile.density_cluster_share_240`; статус: калибруется.
- `H032` - Доля объёма VPOC окно 240; тип: фича; блок: Профиль плотности; technical: `density_profile.density_vpoc_share_240`; статус: калибруется.
- `H033` - Смещение VPOC за 20 баров; тип: фича; блок: Профиль плотности; technical: `density_profile.density_vpoc_drift_20`; статус: калибруется.
- `H034` - Отношение плотности 60 к 240; тип: фича; блок: Профиль плотности; technical: `density_profile.density_cluster_ratio_60_240`; статус: калибруется.
- `H035` - Дистанция до поддержки; тип: фича; блок: Структура и ТА; technical: `structure_ta.support_distance`; статус: калибруется.
- `H036` - Дистанция до сопротивления; тип: фича; блок: Структура и ТА; technical: `structure_ta.resistance_distance`; статус: калибруется.
- `H037` - Сила уровня; тип: фича; блок: Структура и ТА; technical: `structure_ta.level_strength`; статус: калибруется.
- `H038` - Позиция в диапазоне; тип: фича; блок: Структура и ТА; technical: `structure_ta.position_in_range`; статус: калибруется.
- `H039` - Позиция в тренд-канале; тип: фича; блок: Структура и ТА; technical: `structure_ta.trend_channel_pos`; статус: калибруется.
- `H040` - Дистанция до Фибо 0.382; тип: фича; блок: Структура и ТА; technical: `structure_ta.fib_0382_distance`; статус: калибруется.
- `H041` - Дистанция до Фибо 0.618; тип: фича; блок: Структура и ТА; technical: `structure_ta.fib_0618_distance`; статус: калибруется.
- `H042` - Контекстная дистанция TP; тип: фича; блок: Структура и ТА; technical: `structure_ta.tp_context_distance`; статус: не калибруется.
- `H043` - Контекстная дистанция SL; тип: фича; блок: Структура и ТА; technical: `structure_ta.sl_context_distance`; статус: не калибруется.
- `H044` - Оценка риск/прибыль; тип: фича; блок: Структура и ТА; technical: `structure_ta.rr_context_estimate`; статус: не калибруется.
- `H045` - Флаг пробоя; тип: фича; блок: Структура и ТА; technical: `structure_ta.breakout_flag`; статус: калибруется.
- `H046` - Флаг ложного пробоя; тип: фича; блок: Структура и ТА; technical: `structure_ta.false_breakout_flag`; статус: калибруется.
- `H047` - Флаг ретеста; тип: фича; блок: Структура и ТА; technical: `structure_ta.retest_flag`; статус: калибруется.
- `H048` - Пробой swing high; тип: фича; блок: Структура и ТА; technical: `structure_ta.swing_high_break_flag`; статус: калибруется.
- `H049` - Пробой swing low; тип: фича; блок: Структура и ТА; technical: `structure_ta.swing_low_break_flag`; статус: калибруется.
- `H050` - BOS вверх; тип: фича; блок: Структура и ТА; technical: `structure_ta.bos_up_flag`; статус: не калибруется.
- `H051` - BOS вниз; тип: фича; блок: Структура и ТА; technical: `structure_ta.bos_down_flag`; статус: не калибруется.
- `H052` - CHOCH смена структуры; тип: фича; блок: Структура и ТА; technical: `structure_ta.choch_flag`; статус: не калибруется.
- `H053` - Флаг доджи; тип: фича; блок: Паттерны; technical: `pattern.doji_flag`; статус: калибруется.
- `H054` - Флаг внутреннего бара; тип: фича; блок: Паттерны; technical: `pattern.inside_bar_flag`; статус: не калибруется.
- `H055` - Флаг бычьего пин-бара; тип: фича; блок: Паттерны; technical: `pattern.pin_bar_bull_flag`; статус: калибруется.
- `H056` - Флаг медвежьего пин-бара; тип: фича; блок: Паттерны; technical: `pattern.pin_bar_bear_flag`; статус: калибруется.
- `H057` - Флаг молота; тип: фича; блок: Паттерны; technical: `pattern.hammer_flag`; статус: калибруется.
- `H058` - Флаг падающей звезды; тип: фича; блок: Паттерны; technical: `pattern.shooting_star_flag`; статус: калибруется.
- `H059` - Флаг бычьего поглощения; тип: фича; блок: Паттерны; technical: `pattern.engulf_bull_flag`; статус: не калибруется.
- `H060` - Флаг медвежьего поглощения; тип: фича; блок: Паттерны; technical: `pattern.engulf_bear_flag`; статус: не калибруется.
- `H061` - Флаг бычьей дивергенции RSI; тип: фича; блок: Паттерны; technical: `pattern.rsi_bull_div_flag`; статус: калибруется.
- `H062` - Флаг медвежьей дивергенции RSI; тип: фича; блок: Паттерны; technical: `pattern.rsi_bear_div_flag`; статус: калибруется.
- `H063` - Флаг бычьей дивергенции MACD; тип: фича; блок: Паттерны; technical: `pattern.macd_bull_div_flag`; статус: калибруется.
- `H064` - Флаг медвежьей дивергенции MACD; тип: фича; блок: Паттерны; technical: `pattern.macd_bear_div_flag`; статус: калибруется.
- `H065` - Флаг бычьей дивергенции OBV; тип: фича; блок: Паттерны; technical: `pattern.obv_bull_div_flag`; статус: калибруется.
- `H066` - Флаг медвежьей дивергенции OBV; тип: фича; блок: Паттерны; technical: `pattern.obv_bear_div_flag`; статус: калибруется.
- `H067` - Сила паттерна; тип: фича; блок: Паттерны; technical: `pattern.pattern_strength`; статус: не калибруется.
- `H068` - Возраст паттерна в барах; тип: фича; блок: Паттерны; technical: `pattern.pattern_age_bars`; статус: калибруется.

## Гипотезы из matrix.hypothesis_rows
- `none` - Без фильтра; тип: гипотеза; статус: калибруется; params: `min_abs_ema_gap`.
- `ema_gap_sign` - Знак EMA-разрыва; тип: гипотеза; статус: калибруется; params: `min_abs_ema_gap, period_standard, ema_slow_period`.
- `ema_cross_20_50` - Пересечение EMA 20/50; тип: гипотеза; статус: калибруется; params: `min_abs_ema_gap, period_standard, ema_slow_period`.
- `ema_cross_20_200` - Пересечение EMA 20/200; тип: гипотеза; статус: калибруется; params: `min_abs_ema_gap, period_standard, ema_ultra_period`.
- `ema_stack_bull` - Бычий стек EMA; тип: гипотеза; статус: калибруется; params: `min_abs_ema_gap, period_standard, ema_slow_period, ema_ultra_period`.
- `channel_breakout_50` - Пробой канала 50; тип: гипотеза; статус: калибруется; params: `rolling_window, threshold_fine`.
- `adx_trend_18` - ADX-тренд 18; тип: гипотеза; статус: калибруется; params: `period_standard, adx_threshold`.
- `fib_retrace_0382_0618_trend_resume` - Фибо-откат и продолжение; тип: гипотеза; статус: калибруется; params: `rolling_window, threshold_fine`.
- `fib_extension_targets` - Фибо-цели расширения; тип: гипотеза; статус: калибруется; params: `rolling_window, threshold_fine`.
- `swing_hl_hh_long` - Свинг HL/HH лонг; тип: гипотеза; статус: калибруется; params: `return_lookback, threshold_fine`.
- `swing_lh_ll_short` - Свинг LH/LL шорт; тип: гипотеза; статус: калибруется; params: `return_lookback, threshold_fine`.
- `bos_continuation_confirm` - Подтверждение BOS-продолжения; тип: гипотеза; статус: калибруется; params: `return_lookback, threshold_fine`.
- `min_max_range_revert` - Возврат в min/max-диапазон; тип: гипотеза; статус: калибруется; params: `rolling_window, threshold_fine`.
- `max_low_pullback_long` - Лонг от отката к max-low; тип: гипотеза; статус: калибруется; params: `return_lookback, threshold_fine`.
- `hvn_lvn_density_reaction` - Реакция на HVN/LVN; тип: гипотеза; статус: калибруется; params: `density_window_short, density_window_long, density_bin_pct`.
- `volume_profile_poc_vah_val_retest` - Ретест POC/VAH/VAL; тип: гипотеза; статус: калибруется; params: `density_window_short, density_window_long, density_bin_pct`.
- `value_area_rotation_vs_breakout` - Ротация VA vs пробой; тип: гипотеза; статус: калибруется; params: `density_window_short, density_window_long, density_bin_pct, threshold_fine`.
- `wedge_breakout_plus_profile_acceptance` - Клин-пробой и акцепт профиля; тип: гипотеза; статус: калибруется; params: `rolling_window, threshold_fine`.
- `orderbook_imbalance_l1_l50` - Дисбаланс стакана L1-L50; тип: гипотеза; статус: калибруется; params: `imbalance_threshold`.
- `spread_pressure_and_delta_absorption` - Давление спреда и абсорбция дельты; тип: гипотеза; статус: калибруется; params: `spread_z_threshold`.

## Проверка покрытия
- Пропущенные русские названия: `нет`.
- Вывод: все фичи и гипотезы из активной матрицы имеют русское название в словаре проекта.
