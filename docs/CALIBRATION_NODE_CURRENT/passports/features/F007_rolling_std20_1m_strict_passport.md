# F007 - STRICT PASSPORT

Source file from user:
`C:\Users\007\Downloads\F007_rolling_std20_1m_strict_passport.md`

Status: active B003 passport.

## Contract

`ID`: `F007`

`FEATURE`: `rolling_std_20_1m`

`ACTION`: `F007_RSTD20_ALLOW`

`ACTION_TYPE`: `ENTRY_FILTER`

`OUTPUT`: binary `1/0`

`TIMEFRAME`: `1m`

`CANDLE`: closed candle only.

`PRICE_SOURCE`: close.

`WINDOW`: fixed `20`.

`STD_METHOD`: population.

`UNIT`: percent.

Formula:

```text
ret1_pct = (Close[i] / Close[i - 1] - 1) * 100
rolling_std_20_pct = population_std(ret1_pct, window=20)
```

Signal:

```text
if cmp = GREATER and rolling_std_20_pct >= thr_pct -> allow
if cmp = LESS and rolling_std_20_pct <= thr_pct -> allow
else -> block
```

## Calibrated Params

Current Optuna profile encoding:

- `F007_cmp`: values `[-1, 1]`
  - `1` = `GREATER`
  - `-1` = `LESS`
- `F007_thr_pct`: min `0.01`, max `0.50`, step `0.01`

## Not Calibrated Here

These fields are not knobs of F007:

- side
- tf
- window
- calc_method
- price_source
- std_method
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
F007_RSTD20_ALLOW
```

`1` means entry allowed. `0` means entry blocked.

LONG and SHORT are calibrated by external mode (`long_only` / `short_only`), not inside F007.
