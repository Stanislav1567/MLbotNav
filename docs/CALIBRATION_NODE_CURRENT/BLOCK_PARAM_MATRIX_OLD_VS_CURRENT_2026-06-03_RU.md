# Сравнение старого конфига с текущей блоковой матрицей

Дата UTC: `2026-06-03T17:32:00Z`.

Старый конфиг: `configs/calibration_feature_hypothesis_draft.yaml`.

Текущая матрица: `configs/calibration_full_matrix_v1.yaml`.

Машинный артефакт: `reports/qa_gate/calibration_old_vs_current_block_params_20260603T173200Z.json`.

## Короткий вывод

Старый конфиг найден. В нем действительно прописаны параметры `min/max/step/count` по каждому блоку.

В текущей матрице почти все диапазоны сохранены, но часть старых имен сведена к общим каноническим профилям. Это не потеря диапазона, а нормализация имен.

Примеры нормализации:

1. `atr_period`, `rsi_period`, `adx_period`, `stoch_k_period` сейчас идут через `period_standard`: `min=7`, `max=35`, `step=2`, `count=15`.
2. `rolling_std_window`, `sr_window`, `channel_window`, `fib_window` сейчас идут через `rolling_window`: `min=20`, `max=180`, `step=20`, `count=9`.
3. `vol_change_lookback`, `delta_volume_lookback`, `obv_slope_lookback`, `slope_lookback`, `swing_window` сейчас идут через `return_lookback`: `min=3`, `max=30`, `step=3`, `count=10`.

Главный реальный разрыв: старый параметр `fib_level` с диапазоном `min=0.236`, `max=0.786`, `step=0.146`, `count=5` сейчас не вынесен в текущую матрицу как отдельный калибруемый профиль. Текущие фичи `fib_0382_distance` и `fib_0618_distance` калибруют окно `rolling_window`, а уровни 0.382 и 0.618 фактически фиксированные.

## Как читать

Если запускаем блоковую матрицу `configs/calibration_matrices/catalog_blocks/catalog_block_XX_*.yaml`, то блок берется целиком. Все параметры блока ниже участвуют вместе, одной блоковой калибровкой.

## 1. `price_volatility` - Цена и волатильность

Фич: старый конфиг `8`, текущая матрица `8`.

Сейчас калибруются `7`, фиксированная `1`.

Параметры блока:

| Текущий параметр | Старые имена | min | max | step | count |
|---|---|---:|---:|---:|---:|
| `return_lookback` | `return_lookback` | 3 | 30 | 3 | 10 |
| `rolling_window` | `rolling_std_window` | 20 | 180 | 20 | 9 |
| `period_standard` | `atr_period` | 7 | 35 | 2 | 15 |

Фиксировано:

1. `hl_spread` - производная формула, не калибруется.

Вывод: блок совпадает со старым конфигом по диапазонам.

## 2. `trend_momentum` - Тренд и импульс

Фич: старый конфиг `10`, текущая матрица `10`.

Сейчас калибруются `10`, фиксированных `0`.

Параметры блока:

| Текущий параметр | Старые имена | min | max | step | count |
|---|---|---:|---:|---:|---:|
| `period_standard` | `ema_fast`, `ema_base_period`, `rsi_period`, `adx_period`, `stoch_k_period` | 7 | 35 | 2 | 15 |
| `return_lookback` | `slope_lookback` | 3 | 30 | 3 | 10 |
| `ema_slow_period` | `ema_slow` | 20 | 120 | 10 | 11 |
| `ema_ultra_period` | `ema_ultra` | 120 | 300 | 20 | 10 |
| `macd_fast_period` | `macd_fast` | 7 | 21 | 2 | 8 |
| `macd_slow_period` | `macd_slow` | 19 | 43 | 2 | 13 |
| `macd_signal_period` | `macd_signal_period` | 5 | 17 | 2 | 7 |
| `stoch_d_period` | `stoch_d_period` | 3 | 15 | 2 | 7 |

Вывод: блок совпадает со старым конфигом по диапазонам, но старые отдельные period-имена сведены в общий `period_standard`.

## 3. `volume_flow` - Объем и поток

Фич: старый конфиг `6`, текущая матрица `6`.

Сейчас калибруются `5`, фиксированная `1`.

Параметры блока:

| Текущий параметр | Старые имена | min | max | step | count |
|---|---|---:|---:|---:|---:|
| `return_lookback` | `vol_change_lookback`, `delta_volume_lookback`, `obv_slope_lookback` | 3 | 30 | 3 | 10 |
| `rolling_window` | `vol_z_window` | 20 | 180 | 20 | 9 |
| `period_standard` | `mfi_period` | 7 | 35 | 2 | 15 |

Фиксировано:

1. `vwap_distance` - производная фича, не калибруется.

Вывод: блок совпадает со старым конфигом по диапазонам. Сырой `volume` сам не калибруется; калибруются производные volume-фичи.

## 4. `density_profile` - Профиль плотности

Фич: старый конфиг `10`, текущая матрица `10`.

Сейчас калибруются `10`, фиксированных `0`.

Параметры блока:

| Текущий параметр | Старые имена | min | max | step | count |
|---|---|---:|---:|---:|---:|
| `density_window_short` | `density_window_short` | 20 | 120 | 20 | 6 |
| `density_window_long` | `density_window_long` | 120 | 360 | 30 | 9 |
| `density_bin_pct` | `bin_pct` | 0.0003 | 0.0012 | 0.0001 | 10 |
| `div_lookback` | `vpoc_drift_lookback` | 3 | 30 | 3 | 10 |

Вывод: блок совпадает со старым конфигом по диапазонам.

## 5. `structure_ta` - Структура и технический анализ

Фич: старый конфиг `18`, текущая матрица `18`.

Сейчас калибруются `12`, фиксированных `6`.

Параметры блока:

| Текущий параметр | Старые имена | min | max | step | count |
|---|---|---:|---:|---:|---:|
| `rolling_window` | `sr_window`, `channel_window`, `fib_window` | 20 | 180 | 20 | 9 |
| `threshold_fine` | `touch_threshold`, `false_breakout_retest_threshold`, `retest_threshold` | 0.0005 | 0.01 | 0.0005 | 20 |
| `return_lookback` | `swing_window` | 3 | 30 | 3 | 10 |

Фиксировано:

1. `tp_context_distance`.
2. `sl_context_distance`.
3. `rr_context_estimate`.
4. `bos_up_flag`.
5. `bos_down_flag`.
6. `choch_flag`.

Разрыв со старым конфигом:

| Старый параметр | Где был | min | max | step | count | Что сейчас |
|---|---|---:|---:|---:|---:|---|
| `fib_level` | `fib_0382_distance`, `fib_0618_distance` | 0.236 | 0.786 | 0.146 | 5 | Нет отдельного текущего профиля; уровни 0.382/0.618 фиксированы |

Вывод: блок почти совпадает, но `fib_level` нужно отдельно решить: либо вернуть как калибруемый профиль, либо явно зафиксировать, что уровни Фибо не калибруем.

## 6. `pattern` - Паттерны

Фич: старый конфиг `16`, текущая матрица `16`.

Сейчас калибруются `12`, фиксированных `4`.

Параметры блока:

| Текущий параметр | Старые имена | min | max | step | count |
|---|---|---:|---:|---:|---:|
| `doji_threshold` | `doji_body_to_range_max` | 0.05 | 0.20 | 0.01 | 16 |
| `ratio_pattern` | `pin_wick_to_body_min`, `hammer_lower_wick_ratio_min`, `star_upper_wick_ratio_min` | 1.2 | 3.4 | 0.2 | 12 |
| `ratio_opposite_wick_cap` | `hammer_upper_wick_ratio_max`, `star_lower_wick_ratio_max` | 0.4 | 1.2 | 0.1 | 9 |
| `div_lookback` | `divergence_lookback` | 3 | 30 | 3 | 10 |
| `pattern_age_cap` | `pattern_age_cap` | 5 | 100 | 5 | 20 |

Фиксировано:

1. `inside_bar_flag`.
2. `engulf_bull_flag`.
3. `engulf_bear_flag`.
4. `pattern_strength`.

Вывод: блок совпадает со старым конфигом по диапазонам.

## Shared параметры гипотез

| Текущий параметр | Старое имя | min | max | step | count |
|---|---|---:|---:|---:|---:|
| `min_abs_ema_gap` | `min_abs_ema_gap` | 0.0 | 0.08 | 0.01 | 9 |
| `horizon_bars` | `horizon_bars` | 1 | 20 | 1 | 20 |
| `p_enter_long` | `p_enter_long` | 0.52 | 0.80 | 0.02 | 15 |
| `p_enter_short` | `p_enter_short` | 0.20 | 0.48 | 0.02 | 15 |
| `min_expected_move` | `min_expected_move_pct` | 0.0005 | 0.01 | 0.0005 | 20 |
| `notional_usd` | `notional_usd` | 5 | 100 | 5 | 20 |

## Практический вывод

Если идем блоками, запускаем `catalog_blocks`, а не `feature_sweep/Hxxx`.

Перед боевым блоковым запуском нужно решить только один вопрос: что делать с `fib_level`.

Вариант А: вернуть `fib_level` в текущую матрицу как калибруемый профиль для `structure_ta`.

Вариант Б: зафиксировать, что уровни Фибо 0.382/0.618 не калибруются, а калибруется только окно `rolling_window`.
