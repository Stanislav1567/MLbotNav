# F008 - STRICT PASSPORT

Source file from user:
`C:\Users\007\Downloads\F008_atr14_1m_strict_passport_v2.md`

Status: active B004 passport.

## Contract

`ID`: `F008`

`FEATURE`: `atr14_1m`

`ACTION`: `F008_ATR14_ALLOW`

`ACTION_TYPE`: `ENTRY_FILTER`

`OUTPUT`: binary `1/0`

`TIMEFRAME`: `1m`

`CANDLE`: closed candle only.

`PRICE_SOURCE`: high, low, close.

`ATR_PERIOD`: fixed `14`.

`ATR_METHOD`: Wilder.

`UNIT`: percent.

Formula:

```text
TR = max(high - low, abs(high - previous_close), abs(low - previous_close))
atr14 = WilderMA(TR, 14)
atr14_pct = (atr14 / close) * 100
```

Signal:

```text
if cmp = GREATER and atr14_pct >= thr_pct -> allow
if cmp = LESS and atr14_pct <= thr_pct -> allow
else -> block
```

## Calibrated Params

Current Optuna profile encoding:

- `F008_cmp`: values `[-1, 1]`
  - `1` = `GREATER`
  - `-1` = `LESS`
- `F008_thr_pct`: min `0.01`, max `3.00`, step `0.01`

## Not Calibrated Here

These fields are not knobs of F008:

- side
- tf
- atr_period
- atr_method
- calc_method
- price_source
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
F008_ATR14_ALLOW
```

`1` means entry allowed. `0` means entry blocked.

LONG and SHORT are calibrated by external mode (`long_only` / `short_only`), not inside F008.
