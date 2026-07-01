# RET_N FAMILY - STRICT PASSPORTS F001-F005

Source file from user:
`C:\Users\007\Downloads\RET_N_F001_F005_strict_passports.md`

Status: active B001 passport family.

## Family Rules

`FEATURE_FAMILY`: `ret_N_1m`

`ACTION_TYPE`: `ENTRY_FILTER`

`OUTPUT`: binary `1/0`

`TIMEFRAME`: `1m`

`CANDLE`: closed candle only.

`PRICE_SOURCE`: close.

`UNIT`: percent.

Formula:

```text
retN_pct = (Close[1] / Close[1 + N] - 1) * 100
```

Signal:

```text
if move = +1 and retN_pct >= thr_pct -> allow
if move = -1 and retN_pct <= -thr_pct -> allow
else -> block
```

## Not Calibrated Here

These fields are not knobs of F001-F005:

- side
- timeframe
- price_source
- candle type
- return_lookback
- vol_window
- log/simple return mode
- momentum/reversal interpretation
- entry/exit mode
- order_size
- stop_loss
- take_profit
- timeout
- min_abs_ema_gap
- trend_filter

## F001

Feature: `ret_1`

N: `1`

Action column: `F001_RET1_ALLOW`

Calibrated params:

- `F001_move`: values `[-1, 1]`
- `F001_thr_pct`: min `0.01`, max `0.50`, step `0.01`

## F002

Feature: `ret_3`

N: `3`

Action column: `F002_RET3_ALLOW`

Calibrated params:

- `F002_move`: values `[-1, 1]`
- `F002_thr_pct`: min `0.02`, max `0.90`, step `0.01`

## F003

Feature: `ret_6`

N: `6`

Action column: `F003_RET6_ALLOW`

Calibrated params:

- `F003_move`: values `[-1, 1]`
- `F003_thr_pct`: min `0.03`, max `1.20`, step `0.02`

## F004

Feature: `ret_12`

N: `12`

Action column: `F004_RET12_ALLOW`

Calibrated params:

- `F004_move`: values `[-1, 1]`
- `F004_thr_pct`: min `0.05`, max `1.75`, step `0.05`

## F005

Feature: `ret_24`

N: `24`

Action column: `F005_RET24_ALLOW`

Calibrated params:

- `F005_move`: values `[-1, 1]`
- `F005_thr_pct`: min `0.10`, max `2.50`, step `0.05`

## Runtime Contract

Each passport action is independent. Optuna may tune only the two params declared by that passport. Backtest applies a runtime action only when its `*_ALLOW` column is present in the frame.

If several `RET_N_ALLOW` columns are present in one frame, entry is allowed only when all present action columns equal `1`.
