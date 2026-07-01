# Список для паспортного аудита: фичи, индикаторы, гипотезы

Дата UTC: `2026-06-20T06:50:00Z`.

Статус: `INVENTORY_LIST`.

Источник порядка:
`configs/calibration_full_matrix_v1.yaml`.

Источник русских имен:
`configs/features_block.yaml`.

## Коротко

```text
feature_rows / фичи и индикаторы: 83
hypothesis_rows / гипотезы:       20
parameter_profiles / ручки:       38
search_grid_rows / search-поля:   5
блоки:                            6
```

Важно:
в `configs/features_block.yaml` поле `features.columns_count` равно `68`, но фактический список содержит `83` уникальные фичи. Для паспортного аудита используем фактический список `83`.

## Feature Rows / Фичи и Индикаторы

### Block 01: `price_volatility` / Цена и волатильность

1. `F001` - `ret_1` - Доходность за 1 бар.
2. `F002` - `ret_3` - Доходность за 3 бара.
3. `F003` - `ret_6` - Доходность за 6 баров.
4. `F004` - `ret_12` - Доходность за 12 баров.
5. `F005` - `ret_24` - Доходность за 24 бара.
6. `F006` - `hl_spread` - Диапазон high-low к open.
7. `F007` - `rolling_std_20` - Скользящая волатильность 20.
8. `F008` - `atr14` - ATR(14).

### Block 02: `trend_momentum` / Тренд и импульс

9. `F009` - `ema_gap` - Разрыв EMA20-EMA50.
10. `F010` - `ema_slope_5` - Наклон EMA20 за 5 баров.
11. `F011` - `ema200_gap` - Отклонение от EMA200.
12. `F012` - `rsi14` - RSI(14).
13. `F013` - `macd_line` - Линия MACD.
14. `F014` - `macd_signal` - Сигнальная линия MACD.
15. `F015` - `macd_hist` - Гистограмма MACD.
16. `F016` - `adx14` - ADX(14).
17. `F017` - `stoch_k14` - Стохастик K(14).
18. `F018` - `stoch_d14` - Стохастик D(14).

### Block 03: `volume_flow` / Объем и поток

19. `F019` - `vol_chg` - Изменение объема.
20. `F020` - `vol_z` - Z-оценка объема.
21. `F021` - `delta_volume` - Дельта объема.
22. `F022` - `obv_slope_5` - Наклон OBV за 5 баров.
23. `F023` - `mfi14` - MFI(14).
24. `F024` - `vwap_distance` - Дистанция до VWAP.

### Block 04: `density_profile` / Профиль плотности

25. `F025` - `density_vpoc_distance_60` - Дистанция до VPOC окно 60.
26. `F026` - `density_bin_share_60` - Доля объема бина окно 60.
27. `F027` - `density_cluster_share_60` - Доля объема кластера окно 60.
28. `F028` - `density_vpoc_share_60` - Доля объема VPOC окно 60.
29. `F029` - `density_vpoc_distance_240` - Дистанция до VPOC окно 240.
30. `F030` - `density_bin_share_240` - Доля объема бина окно 240.
31. `F031` - `density_cluster_share_240` - Доля объема кластера окно 240.
32. `F032` - `density_vpoc_share_240` - Доля объема VPOC окно 240.
33. `F033` - `density_vpoc_drift_20` - Смещение VPOC за 20 баров.
34. `F034` - `density_cluster_ratio_60_240` - Отношение плотности 60 к 240.

### Block 05: `structure_ta` / Структура и ТА

35. `F035` - `support_distance` - Дистанция до поддержки.
36. `F036` - `resistance_distance` - Дистанция до сопротивления.
37. `F037` - `level_strength` - Сила уровня.
38. `F038` - `position_in_range` - Позиция в диапазоне.
39. `F039` - `trend_channel_pos` - Позиция в тренд-канале.
40. `F040` - `fib_0382_distance` - Дистанция до Фибо 0.382.
41. `F041` - `fib_0618_distance` - Дистанция до Фибо 0.618.
42. `F042` - `tp_context_distance` - Контекстная дистанция TP.
43. `F043` - `sl_context_distance` - Контекстная дистанция SL.
44. `F044` - `rr_context_estimate` - Оценка риск/прибыль.
45. `F045` - `breakout_flag` - Флаг пробоя.
46. `F046` - `false_breakout_flag` - Флаг ложного пробоя.
47. `F047` - `retest_flag` - Флаг ретеста.
48. `F048` - `swing_high_break_flag` - Пробой swing high.
49. `F049` - `swing_low_break_flag` - Пробой swing low.
50. `F050` - `bos_up_flag` - BOS вверх.
51. `F051` - `bos_down_flag` - BOS вниз.
52. `F052` - `choch_flag` - CHOCH смена структуры.

### Block 06: `pattern` / Паттерны

53. `F053` - `doji_flag` - Флаг доджи.
54. `F054` - `inside_bar_flag` - Флаг внутреннего бара.
55. `F055` - `pin_bar_bull_flag` - Флаг бычьего пин-бара.
56. `F056` - `pin_bar_bear_flag` - Флаг медвежьего пин-бара.
57. `F057` - `hammer_flag` - Флаг молота.
58. `F058` - `shooting_star_flag` - Флаг падающей звезды.
59. `F059` - `engulf_bull_flag` - Флаг бычьего поглощения.
60. `F060` - `engulf_bear_flag` - Флаг медвежьего поглощения.
61. `F061` - `rsi_bull_div_flag` - Флаг бычьей дивергенции RSI.
62. `F062` - `rsi_bear_div_flag` - Флаг медвежьей дивергенции RSI.
63. `F063` - `macd_bull_div_flag` - Флаг бычьей дивергенции MACD.
64. `F064` - `macd_bear_div_flag` - Флаг медвежьей дивергенции MACD.
65. `F065` - `obv_bull_div_flag` - Флаг бычьей дивергенции OBV.
66. `F066` - `obv_bear_div_flag` - Флаг медвежьей дивергенции OBV.
67. `F067` - `pattern_strength` - Сила паттерна.
68. `F068` - `pattern_age_bars` - Возраст паттерна в барах.
69. `F069` - `double_bottom_flag` - Флаг двойного дна.
70. `F070` - `double_top_flag` - Флаг двойной вершины.
71. `F071` - `head_shoulders_flag` - Флаг головы и плеч.
72. `F072` - `inverse_head_shoulders_flag` - Флаг перевернутой головы и плеч.
73. `F073` - `triangle_flag` - Флаг треугольника.
74. `F074` - `pennant_flag` - Флаг вымпела.
75. `F075` - `wedge_rising_flag` - Флаг восходящего клина.
76. `F076` - `wedge_falling_flag` - Флаг нисходящего клина.
77. `F077` - `range_flag` - Флаг диапазона.
78. `F078` - `pattern_volume_confirm_flag` - Подтверждение фигуры объемом.
79. `F079` - `pattern_level_confirm_flag` - Подтверждение фигуры уровнем.
80. `F080` - `pattern_structure_volume_entry_long` - Вход long по фигуре, уровню и объему.
81. `F081` - `pattern_structure_volume_entry_short` - Вход short по фигуре, уровню и объему.
82. `F082` - `pattern_sl_buffer_distance` - Дистанция SL с буфером паттерна.
83. `F083` - `pattern_tp_ladder_score` - Оценка TP-лесенки паттерна.

## Hypothesis Rows / Гипотезы

1. `H001` - `none`.
2. `H002` - `ema_gap_sign`.
3. `H003` - `ema_cross_20_50`.
4. `H004` - `ema_cross_20_200`.
5. `H005` - `ema_stack_bull`.
6. `H006` - `channel_breakout_50`.
7. `H007` - `adx_trend_18`.
8. `H008` - `fib_retrace_0382_0618_trend_resume`.
9. `H009` - `fib_extension_targets`.
10. `H010` - `swing_hl_hh_long`.
11. `H011` - `swing_lh_ll_short`.
12. `H012` - `bos_continuation_confirm`.
13. `H013` - `min_max_range_revert`.
14. `H014` - `max_low_pullback_long`.
15. `H015` - `hvn_lvn_density_reaction`.
16. `H016` - `volume_profile_poc_vah_val_retest`.
17. `H017` - `value_area_rotation_vs_breakout`.
18. `H018` - `wedge_breakout_plus_profile_acceptance`.
19. `H019` - `orderbook_imbalance_l1_l50`.
20. `H020` - `spread_pressure_and_delta_absorption`.

## Parameter Profiles / Ручки

1. `P001` - `return_lookback`.
2. `P002` - `rolling_window`.
3. `P003` - `period_standard`.
4. `P004` - `ema_slow_period`.
5. `P005` - `ema_ultra_period`.
6. `P006` - `macd_fast_period`.
7. `P007` - `macd_slow_period`.
8. `P008` - `macd_signal_period`.
9. `P009` - `stoch_d_period`.
10. `P010` - `threshold_fine`.
11. `P011` - `fib_window`.
12. `P012` - `fib_level`.
13. `P013` - `doji_threshold`.
14. `P014` - `ratio_pattern`.
15. `P015` - `ratio_opposite_wick_cap`.
16. `P016` - `density_window_short`.
17. `P017` - `density_window_long`.
18. `P018` - `density_bin_pct`.
19. `P019` - `div_lookback`.
20. `P020` - `pattern_age_cap`.
21. `P021` - `pattern_window`.
22. `P022` - `min_touches`.
23. `P023` - `breakout_threshold`.
24. `P024` - `retest_window`.
25. `P025` - `level_distance_threshold`.
26. `P026` - `volume_confirm_threshold`.
27. `P027` - `vol_z_window`.
28. `P028` - `sl_buffer`.
29. `P029` - `tp_ladder`.
30. `P030` - `adx_threshold`.
31. `P031` - `min_abs_ema_gap`.
32. `P032` - `horizon_bars`.
33. `P033` - `p_enter_long`.
34. `P034` - `p_enter_short`.
35. `P035` - `min_expected_move`.
36. `P036` - `notional_usd`.
37. `P037` - `imbalance_threshold`.
38. `P038` - `spread_z_threshold`.

## Search Grid Rows / Search-поля

1. `S001` - `horizon_bars`.
2. `S002` - `p_enter_long`.
3. `S003` - `p_enter_short`.
4. `S004` - `min_expected_move`.
5. `S005` - `notional_usd`.
