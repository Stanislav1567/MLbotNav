# F006 - STRICT PASSPORT

Source file from user:
`C:\Users\007\Downloads\F006_hl_spread_1m_strict_passport_v2.md`

Status: active B001 passport.

## Contract

`ID`: `F006`

`FEATURE`: `hl_spread_1m`

`ACTION`: `F006_HLSPREAD_ALLOW`

`ACTION_TYPE`: `ENTRY_FILTER`

`OUTPUT`: binary `1/0`

`TIMEFRAME`: `1m`

`CANDLE`: closed candle only.

`PRICE_SOURCE`: high, low, open.

`UNIT`: percent.

Formula:

```text
hl_spread_pct = ((High[1] - Low[1]) / Open[1]) * 100
```

Signal:

```text
if cmp = GREATER and hl_spread_pct >= thr_pct -> allow
if cmp = LESS and hl_spread_pct <= thr_pct -> allow
else -> block
```

## Calibrated Params

Current Optuna profile encoding:

- `F006_cmp`: values `[-1, 1]`
  - `1` = `GREATER`
  - `-1` = `LESS`
- `F006_thr_pct`: min `0.02`, max `1.50`, step `0.01`

## Not Calibrated Here

These fields are not knobs of F006:

- side
- tf
- calc_method
- price_source
- vol_window
- log_simple
- momentum_reversal
- entry_exit
- order_size
- stop_loss
- take_profit
- candle_direction

## Runtime Output

Runtime must calculate:

```text
F006_HLSPREAD_ALLOW
```

`1` means entry allowed. `0` means entry blocked.

LONG and SHORT are calibrated by external mode (`long_only` / `short_only`), not inside F006.
