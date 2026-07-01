# BLOCK FICHI (FEATURES REGISTRY)

- Updated (UTC): `2026-05-23T04:08:01Z`
- Goal: one source for hypotheses, technical-analysis patterns, and feature blocks.

## 1) Audit Scope

- `src/mlbotnav/adaptive_auto_train.py` (hypothesis rotation)
- `src/mlbotnav/backtest.py` (trend filter application)
- `src/mlbotnav/search_gate_candidate.py` (candidate grid search)
- `src/mlbotnav/technical_analysis.py` (pattern catalog and TA signal logic)
- `src/mlbotnav/dataset.py` (`FEATURE_COLUMNS`, `FEATURE_GROUPS`)

## 2) Hypotheses

### 2.1 Trend Hypotheses (1m long-style)

- `none` + `min_abs_ema_gap=0.0`
- `ema_gap_sign` + `min_abs_ema_gap=0.0`
- `ema_gap_sign` + `min_abs_ema_gap=0.02`
- `ema_cross_20_50` + `min_abs_ema_gap=0.0`
- `ema_cross_20_200` + `min_abs_ema_gap=0.0`
- `ema_stack_bull` + `min_abs_ema_gap=0.0`
- `channel_breakout_50` + `min_abs_ema_gap=0.0`
- `adx_trend_18` + `min_abs_ema_gap=0.0`

### 2.2 Mode Hypotheses

- `signal_mode`: `both`, `long_only`, `short_only`
- `execution_mode`: `research`, `exchange_like`
- `order_type`: `market`, `limit`

## 3) Technical-Analysis Pattern Catalog

### 3.1 Candle Patterns

- `doji`
- `inside_bar`
- `engulf_bull`
- `engulf_bear`
- `hammer`
- `shooting_star`
- `pin_bar_bull`
- `pin_bar_bear`

### 3.2 Full Pattern Types

- `doji`
- `double_bottom`
- `double_top`
- `engulf_bear`
- `engulf_bull`
- `hammer`
- `head_and_shoulders`
- `inside_bar`
- `inverse_head_and_shoulders`
- `macd_bull_divergence`
- `macd_bear_divergence`
- `obv_bull_divergence`
- `obv_bear_divergence`
- `pennant`
- `pin_bar_bear`
- `pin_bar_bull`
- `range`
- `rsi_bear_divergence`
- `rsi_bull_divergence`
- `shooting_star`
- `triangle`
- `wedge_falling`
- `wedge_rising`

## 4) Features

- Total `FEATURE_COLUMNS`: `68`
- Total `FEATURE_GROUPS`: `6`

### 4.1 Feature Groups

- `price_volatility`: 8
- `trend_momentum`: 10
- `volume_flow`: 6
- `density_profile`: 10
- `structure_ta`: 18
- `pattern`: 16

### 4.2 Full `FEATURE_COLUMNS`

- `ret_1`
- `ret_3`
- `ret_6`
- `ret_12`
- `ret_24`
- `hl_spread`
- `rolling_std_20`
- `atr14`
- `vol_chg`
- `vol_z`
- `delta_volume`
- `obv_slope_5`
- `mfi14`
- `ema_gap`
- `ema_slope_5`
- `ema200_gap`
- `rsi14`
- `macd_line`
- `macd_signal`
- `macd_hist`
- `adx14`
- `stoch_k14`
- `stoch_d14`
- `vwap_distance`
- `support_distance`
- `resistance_distance`
- `level_strength`
- `position_in_range`
- `trend_channel_pos`
- `fib_0382_distance`
- `fib_0618_distance`
- `tp_context_distance`
- `sl_context_distance`
- `rr_context_estimate`
- `breakout_flag`
- `false_breakout_flag`
- `retest_flag`
- `swing_high_break_flag`
- `swing_low_break_flag`
- `bos_up_flag`
- `bos_down_flag`
- `choch_flag`
- `doji_flag`
- `inside_bar_flag`
- `pin_bar_bull_flag`
- `pin_bar_bear_flag`
- `hammer_flag`
- `shooting_star_flag`
- `engulf_bull_flag`
- `engulf_bear_flag`
- `rsi_bull_div_flag`
- `rsi_bear_div_flag`
- `macd_bull_div_flag`
- `macd_bear_div_flag`
- `obv_bull_div_flag`
- `obv_bear_div_flag`
- `pattern_strength`
- `pattern_age_bars`
- `density_vpoc_distance_60`
- `density_bin_share_60`
- `density_cluster_share_60`
- `density_vpoc_share_60`
- `density_vpoc_distance_240`
- `density_bin_share_240`
- `density_cluster_share_240`
- `density_vpoc_share_240`
- `density_vpoc_drift_20`
- `density_cluster_ratio_60_240`

## 5) Order and Governance

- Machine source of truth: `configs/features_block.yaml`
- Human-readable source: this file
- Rule: new hypothesis/feature must be added in code and synchronized to `configs/features_block.yaml`

## 6) Added From Screenshot (Volume Profile Style)

- Indicator family: `Volume Profile + Value Area + structure breakout/retest`
- Visual elements from screenshot mapped to hypotheses:
- `POC` (point of control) zone reaction
- `VAH/VAL` (value area high/low) acceptance or rejection
- range floor/ceiling (`min/max`) with breakout and retest
- wedge/triangle breakout with continuation filter
- pullback entry after impulse into profile zone

### Planned hypotheses (registered)

- `volume_profile_poc_vah_val_retest`
- `value_area_rotation_vs_breakout`
- `wedge_breakout_plus_profile_acceptance`
