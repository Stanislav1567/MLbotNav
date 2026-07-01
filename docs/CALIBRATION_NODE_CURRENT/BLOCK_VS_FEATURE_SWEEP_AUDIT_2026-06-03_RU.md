# Audit: блоковая калибровка APTuna vs одиночный feature sweep

Дата UTC: `2026-06-03T16:59:00Z`.

Основной артефакт: `reports/qa_gate/aptuna_block_vs_feature_sweep_audit_20260603T170400Z.json`.

Примечание: предыдущий машинный артефакт `reports/qa_gate/aptuna_block_vs_feature_sweep_audit_20260603T165900Z.json` оставлен как исторический, но заменен новым ASCII-safe JSON из-за риска кракозябр при открытии в Windows/PowerShell.

## Короткий вывод

APTuna калибрует то, какую матрицу мы передаем через `-CalibrationMatrixPath`.

Есть два разных режима:

1. `configs/calibration_matrices/catalog_blocks/*.yaml` - блоковый режим. Берется целевой блок целиком, все его feature rows и общий union-набор параметров блока. Это соответствует требованию "калибровать блок целиком".
2. `configs/calibration_matrices/feature_sweep/h*.yaml` - одиночный feature-slot режим. Сгенерированные `H001/H002` содержат по одной feature row. Это не калибровка всего блока.

Важно: для блоковых матриц целевой блок идет вместе с always-on context blocks:

1. `volume_flow`.
2. `price_volatility`.

Это значит: блок калибруется целиком, но контекст объема/цены остается подключенным для принятия решения.

## Что делает APTuna

Runner: `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`.

Если передан параметр `-CalibrationMatrixPath`, runner кладет путь в переменную `MLBOTNAV_CALIBRATION_MATRIX_PATH`.

`src/mlbotnav/optuna_space.py` читает эту матрицу и собирает пространство:

1. берет `block_switches`;
2. добавляет `context_blocks.always_on`;
3. фильтрует `feature_rows` по `effective_feature_blocks`;
4. собирает общий список параметров из всех feature/hypothesis/search rows;
5. применяет профиль сетки `narrow`, `medium` или `wide`.

## Состав блоков

### 1. `price_volatility` - Цена и волатильность

Фич всего: `8`.

Калибруются: `7`.

Фиксированные: `1`.

Калибруемые фичи:

1. `ret_1`, `ret_3`, `ret_6`, `ret_12`, `ret_24` - параметр `return_lookback`.
2. `rolling_std_20` - параметр `rolling_window`.
3. `atr14` - параметр `period_standard`.

Фиксированная фича:

1. `hl_spread`.

Общий набор параметров блока:

1. `return_lookback`.
2. `rolling_window`.
3. `period_standard`.

Вывод: в `catalog_block_01_price_volatility.yaml` блок калибруется как общий блок.

### 2. `trend_momentum` - Тренд и импульс

Фич всего: `10`.

Калибруются: `10`.

Фиксированные: `0`.

Калибруемые фичи:

1. `ema_gap` - `period_standard`, `ema_slow_period`.
2. `ema_slope_5` - `period_standard`, `return_lookback`.
3. `ema200_gap` - `ema_ultra_period`.
4. `rsi14`, `adx14`, `stoch_k14` - `period_standard`.
5. `macd_line` - `macd_fast_period`, `macd_slow_period`.
6. `macd_signal`, `macd_hist` - `macd_fast_period`, `macd_slow_period`, `macd_signal_period`.
7. `stoch_d14` - `period_standard`, `stoch_d_period`.

Общий набор параметров блока:

1. `period_standard`.
2. `return_lookback`.
3. `ema_slow_period`.
4. `ema_ultra_period`.
5. `macd_fast_period`.
6. `macd_slow_period`.
7. `macd_signal_period`.
8. `stoch_d_period`.

Вывод: в `catalog_block_02_trend_momentum.yaml` блок калибруется как общий блок.

### 3. `volume_flow` - Объем и поток

Фич всего: `6`.

Калибруются: `5`.

Фиксированные: `1`.

Калибруемые фичи:

1. `vol_chg` - `return_lookback`.
2. `vol_z` - `rolling_window`.
3. `delta_volume` - `return_lookback`.
4. `obv_slope_5` - `return_lookback`.
5. `mfi14` - `period_standard`.

Фиксированная фича:

1. `vwap_distance`.

Общий набор параметров блока:

1. `return_lookback`.
2. `rolling_window`.
3. `period_standard`.

Вывод: в `catalog_block_03_volume_flow.yaml` блок калибруется как общий блок. Raw `volume` сам по себе не калибруемый параметр; калибруются производные volume-фичи.

### 4. `density_profile` - Профиль плотности

Фич всего: `10`.

Калибруются: `10`.

Фиксированные: `0`.

Калибруемые фичи:

1. `density_vpoc_distance_60`, `density_bin_share_60`, `density_cluster_share_60`, `density_vpoc_share_60` - `density_window_short`, `density_bin_pct`.
2. `density_vpoc_distance_240`, `density_bin_share_240`, `density_cluster_share_240`, `density_vpoc_share_240` - `density_window_long`, `density_bin_pct`.
3. `density_vpoc_drift_20` - `div_lookback`.
4. `density_cluster_ratio_60_240` - `density_window_short`, `density_window_long`, `density_bin_pct`.

Общий набор параметров блока:

1. `density_window_short`.
2. `density_window_long`.
3. `density_bin_pct`.
4. `div_lookback`.

Вывод: в `catalog_block_04_density_profile.yaml` блок калибруется как общий блок.

### 5. `structure_ta` - Структура и ТА

Фич всего: `18`.

Калибруются: `12`.

Фиксированные: `6`.

Калибруемые фичи:

1. `support_distance`, `resistance_distance`, `position_in_range`, `trend_channel_pos`, `fib_0382_distance`, `fib_0618_distance`, `breakout_flag` - `rolling_window`.
2. `level_strength` - `rolling_window`, `threshold_fine`.
3. `false_breakout_flag`, `retest_flag` - `rolling_window`, `threshold_fine`.
4. `swing_high_break_flag`, `swing_low_break_flag` - `return_lookback`.

Фиксированные фичи:

1. `tp_context_distance`.
2. `sl_context_distance`.
3. `rr_context_estimate`.
4. `bos_up_flag`.
5. `bos_down_flag`.
6. `choch_flag`.

Общий набор параметров блока:

1. `rolling_window`.
2. `threshold_fine`.
3. `return_lookback`.

Вывод: в `catalog_block_05_structure_ta.yaml` блок калибруется как общий блок.

### 6. `pattern` - Паттерны

Фич всего: `16`.

Калибруются: `12`.

Фиксированные: `4`.

Калибруемые фичи:

1. `doji_flag` - `doji_threshold`.
2. `pin_bar_bull_flag`, `pin_bar_bear_flag` - `ratio_pattern`.
3. `hammer_flag`, `shooting_star_flag` - `ratio_pattern`, `ratio_opposite_wick_cap`.
4. `rsi_bull_div_flag`, `rsi_bear_div_flag`, `macd_bull_div_flag`, `macd_bear_div_flag`, `obv_bull_div_flag`, `obv_bear_div_flag` - `div_lookback`.
5. `pattern_age_bars` - `pattern_age_cap`.

Фиксированные фичи:

1. `inside_bar_flag`.
2. `engulf_bull_flag`.
3. `engulf_bear_flag`.
4. `pattern_strength`.

Общий набор параметров блока:

1. `doji_threshold`.
2. `ratio_pattern`.
3. `ratio_opposite_wick_cap`.
4. `div_lookback`.
5. `pattern_age_cap`.

Вывод: в `catalog_block_06_pattern.yaml` блок калибруется как общий блок.

## Главная граница

Если цель - калибровать блок целиком, текущий следующий запуск не должен идти по `feature_sweep/h003_*.yaml` как основной боевой путь.

Для блоковой калибровки нужно брать:

1. `catalog_block_01_price_volatility.yaml`.
2. `catalog_block_02_trend_momentum.yaml`.
3. `catalog_block_03_volume_flow.yaml`.
4. `catalog_block_04_density_profile.yaml`.
5. `catalog_block_05_structure_ta.yaml`.
6. `catalog_block_06_pattern.yaml`.

`H001/H002/H003` можно оставить как диагностический одиночный режим, но не называть его полной калибровкой блока.
