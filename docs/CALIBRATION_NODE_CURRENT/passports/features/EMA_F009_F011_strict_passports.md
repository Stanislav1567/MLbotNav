# EMA FAMILY - STRICT PASSPORTS F009-F011

Source user file: `C:\Users\007\Downloads\EMA_F009_F011_strict_passports.md`.

## Family

`FEATURE_FAMILY: EMA`
`ACTION_TYPE: ENTRY_FILTER`
`OUTPUT: 1/0`
`TF: 1m`
`CALC_METHOD: CLOSE_BAR`
`CANDLE: closed`
`PRICE_SOURCE: close`
`UNIT: percent`

Output meaning:
1. `1` = entry allowed.
2. `0` = entry blocked.

Not calibrated in these feature passports:
`side`, `tf`, `calc_method`, `price_source`, `ema_periods`, `entry_exit`, `order_size`, `stop_loss`, `take_profit`.

## F009 - ema_gap

`FEATURE: ema_gap_20_50_1m`
`ACTION: EMAGAP_ALLOW`
`RUNTIME_ACTION: F009_EMAGAP_ALLOW`

Fixed:
1. `EMA_FAST=20`.
2. `EMA_SLOW=50`.
3. `ema_gap_pct = (EMA20[1] / EMA50[1] - 1) * 100`.

Calibration params:
1. `F009_bias`: `ABOVE / BELOW`, encoded as `1 / -1`.
2. `F009_thr_pct`: `0.00..2.00`, step `0.01`.

Signal:
1. `ABOVE`: allow when `ema_gap_pct >= thr_pct`.
2. `BELOW`: allow when `ema_gap_pct <= -thr_pct`.

## F010 - ema_slope_5

`FEATURE: ema20_slope_5_1m`
`ACTION: EMASLOPE5_ALLOW`
`RUNTIME_ACTION: F010_EMASLOPE5_ALLOW`

Fixed:
1. `EMA_PERIOD=20`.
2. `SLOPE_BARS=5`.
3. `ema_slope_5_pct = (EMA20[1] / EMA20[6] - 1) * 100`.

Calibration params:
1. `F010_slope`: `UP / DOWN`, encoded as `1 / -1`.
2. `F010_thr_pct`: `0.00..1.00`, step `0.01`.

Signal:
1. `UP`: allow when `ema_slope_5_pct >= thr_pct`.
2. `DOWN`: allow when `ema_slope_5_pct <= -thr_pct`.

## F011 - ema200_gap

`FEATURE: ema200_gap_1m`
`ACTION: EMA200GAP_ALLOW`
`RUNTIME_ACTION: F011_EMA200GAP_ALLOW`

Fixed:
1. `EMA_PERIOD=200`.
2. `ema200_gap_pct = (Close[1] / EMA200[1] - 1) * 100`.

Calibration params:
1. `F011_position`: `ABOVE / BELOW`, encoded as `1 / -1`.
2. `F011_thr_pct`: `0.00..5.00`, step `0.05`.

Signal:
1. `ABOVE`: allow when `ema200_gap_pct >= thr_pct`.
2. `BELOW`: allow when `ema200_gap_pct <= -thr_pct`.
