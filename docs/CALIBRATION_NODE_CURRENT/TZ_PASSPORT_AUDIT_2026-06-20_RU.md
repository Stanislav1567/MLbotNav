# ТЗ: паспортный аудит фич, гипотез и инструментов Optuna/APTuna

Дата UTC: `2026-06-20T06:02:00Z`.

Статус: `ACTIVE_PASSPORT_AUDIT_TZ`.

## Цель

Сделать строгий паспортный аудит всех сущностей калибровки:

1. `feature_rows` - 83 паспорта фич.
2. `hypothesis_rows` - 20 паспортов гипотез.
3. `parameter_profiles` - 38 паспортов ручек.
4. `search_grid_rows` - 5 паспортов базовых search-полей.

Задача этого этапа - не запускать калибровку и не менять конфиги, а разобрать каждую сущность по очереди: что это за инструмент, что он измеряет, какие линии/зоны/операторы/шаги реально возможны по смыслу, что является калибруемым параметром, а что является только итоговой меткой.

## Границы

На этом этапе запрещено:

1. Запускать Optuna/APTuna runtime.
2. Запускать `C001 medium`.
3. Запускать forward/OOS/production.
4. Править код.
5. Править конфиги.
6. Брать задачи из старой хронологии.
7. Прыгать между инструментами без закрытия текущего паспорта.

Источник порядка:

1. `configs/calibration_full_matrix_v1.yaml` - рабочий порядок `feature_rows`, `hypothesis_rows`, `parameter_profiles`, `search_grid_rows`.
2. `configs/features_block.yaml` - группировка, русские названия и справочные имена.

Инвентарное замечание:

1. В `features_block.yaml` поле `features.columns_count` равно `68`, но фактический список и группы содержат `83` уникальные фичи.
2. Для паспортов использовать фактический порядок `calibration_full_matrix_v1.yaml`.

## Правило Работы

Идем строго по очереди:

```text
Этап 01: feature_rows 1-83, блок за блоком
Этап 02: hypothesis_rows 1-20
Этап 03: parameter_profiles 1-38
Этап 04: search_grid_rows 1-5
Этап 05: missing knobs registry
Этап 06: согласование расширения конфигов
```

Пока текущий паспорт не закрыт, следующий не начинать.

## Формат Паспорта

Каждый паспорт должен содержать:

1. `passport_id`.
2. Этап и порядковый номер.
3. Блок.
4. Техническое имя.
5. Русское имя.
6. Тип: `feature`, `hypothesis`, `parameter_profile`, `search_grid`, `indicator`, `filter`, `risk`, `action_label`.
7. Что измеряет.
8. Таймфрейм/интервал.
9. Режим проверки: `on_bar_close`, `per_minute`, другое.
10. Расчетные параметры: period/window/lookback/fast/slow/signal/smoothing.
11. Signal-level параметры: линии, зоны, пороги, расстояния, пересечения.
12. Операторы: `less_than`, `greater_than`, `cross_above`, `cross_below`, `between`, `outside_zone`, `return_to_zone`, `slope_up`, `slope_down`.
13. Диапазоны `min/max/step/values`.
14. LONG-смысл.
15. SHORT-смысл.
16. Общие фильтры / запреты для обеих сторон, если они есть.
17. Что является фильтром.
18. Что является подтверждением.
19. Что является action label и не калибруется.
20. Что уже есть в конфиге как справка, без ограничения аудита.
21. Что реально нужно проверить в коде позже.
22. Чего не хватает.
23. Решение: `оставить`, `добавить`, `проверить`, `не калибровать`.

## Важное Правило

Текущий конфиг не является пределом аудита.

Конфиг показывает текущую базу, но паспорт должен описать, что инструмент реально может калибровать по своей природе:

1. Расчетные окна.
2. Таймфреймы.
3. Режим срабатывания.
4. Операторы условий.
5. Линии и зоны.
6. Шаг перебора.
7. LONG/SHORT смысл.
8. Общие фильтры / запреты, если инструмент одинаково ограничивает обе стороны.

## Action Labels

Action labels не калибруются:

```text
LONG_ALLOWED
SHORT_ALLOWED
NO_TRADE
NO_TRADE_LOW_VOL
NO_TRADE_HIGH_RISK
ENTRY_ALLOWED
ENTRY_BLOCKED
```

Калибруются только условия, которые приводят к этим меткам.

## Этап 01: Feature Rows

### Block 01 `price_volatility`

1. `F001` - `ret_1`.
2. `F002` - `ret_3`.
3. `F003` - `ret_6`.
4. `F004` - `ret_12`.
5. `F005` - `ret_24`.
6. `F006` - `hl_spread`.
7. `F007` - `rolling_std_20`.
8. `F008` - `atr14`.

### Block 02 `trend_momentum`

9. `F009` - `ema_gap`.
10. `F010` - `ema_slope_5`.
11. `F011` - `ema200_gap`.
12. `F012` - `rsi14`.
13. `F013` - `macd_line`.
14. `F014` - `macd_signal`.
15. `F015` - `macd_hist`.
16. `F016` - `adx14`.
17. `F017` - `stoch_k14`.
18. `F018` - `stoch_d14`.

### Block 03 `volume_flow`

19. `F019` - `vol_chg`.
20. `F020` - `vol_z`.
21. `F021` - `delta_volume`.
22. `F022` - `obv_slope_5`.
23. `F023` - `mfi14`.
24. `F024` - `vwap_distance`.

### Block 04 `density_profile`

25. `F025` - `density_vpoc_distance_60`.
26. `F026` - `density_bin_share_60`.
27. `F027` - `density_cluster_share_60`.
28. `F028` - `density_vpoc_share_60`.
29. `F029` - `density_vpoc_distance_240`.
30. `F030` - `density_bin_share_240`.
31. `F031` - `density_cluster_share_240`.
32. `F032` - `density_vpoc_share_240`.
33. `F033` - `density_vpoc_drift_20`.
34. `F034` - `density_cluster_ratio_60_240`.

### Block 05 `structure_ta`

35. `F035` - `support_distance`.
36. `F036` - `resistance_distance`.
37. `F037` - `level_strength`.
38. `F038` - `position_in_range`.
39. `F039` - `trend_channel_pos`.
40. `F040` - `fib_0382_distance`.
41. `F041` - `fib_0618_distance`.
42. `F042` - `tp_context_distance`.
43. `F043` - `sl_context_distance`.
44. `F044` - `rr_context_estimate`.
45. `F045` - `breakout_flag`.
46. `F046` - `false_breakout_flag`.
47. `F047` - `retest_flag`.
48. `F048` - `swing_high_break_flag`.
49. `F049` - `swing_low_break_flag`.
50. `F050` - `bos_up_flag`.
51. `F051` - `bos_down_flag`.
52. `F052` - `choch_flag`.

### Block 06 `pattern`

53. `F053` - `doji_flag`.
54. `F054` - `inside_bar_flag`.
55. `F055` - `pin_bar_bull_flag`.
56. `F056` - `pin_bar_bear_flag`.
57. `F057` - `hammer_flag`.
58. `F058` - `shooting_star_flag`.
59. `F059` - `engulf_bull_flag`.
60. `F060` - `engulf_bear_flag`.
61. `F061` - `rsi_bull_div_flag`.
62. `F062` - `rsi_bear_div_flag`.
63. `F063` - `macd_bull_div_flag`.
64. `F064` - `macd_bear_div_flag`.
65. `F065` - `obv_bull_div_flag`.
66. `F066` - `obv_bear_div_flag`.
67. `F067` - `pattern_strength`.
68. `F068` - `pattern_age_bars`.
69. `F069` - `double_bottom_flag`.
70. `F070` - `double_top_flag`.
71. `F071` - `head_shoulders_flag`.
72. `F072` - `inverse_head_shoulders_flag`.
73. `F073` - `triangle_flag`.
74. `F074` - `pennant_flag`.
75. `F075` - `wedge_rising_flag`.
76. `F076` - `wedge_falling_flag`.
77. `F077` - `range_flag`.
78. `F078` - `pattern_volume_confirm_flag`.
79. `F079` - `pattern_level_confirm_flag`.
80. `F080` - `pattern_structure_volume_entry_long`.
81. `F081` - `pattern_structure_volume_entry_short`.
82. `F082` - `pattern_sl_buffer_distance`.
83. `F083` - `pattern_tp_ladder_score`.

## Этап 02: Hypothesis Rows

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

## Этап 03: Parameter Profiles

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

## Этап 04: Search Grid Rows

1. `S001` - `horizon_bars`.
2. `S002` - `p_enter_long`.
3. `S003` - `p_enter_short`.
4. `S004` - `min_expected_move`.
5. `S005` - `notional_usd`.

## Следующий Шаг

Начать с `F001 ret_1`.

Пока `F001 ret_1` не закрыт паспортом, к `F002 ret_3`, RSI, гипотезам или параметрам не переходить.
