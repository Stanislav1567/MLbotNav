# MACD FAMILY - STRICT PASSPORTS F013-F015 - V2

## Family

```text
FEATURE_FAMILY: MACD
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
TF: 1m
CALC_METHOD: CLOSE_BAR
CANDLE: closed
PRICE_SOURCE: close
MACD_FAST_EMA: 12
MACD_SLOW_EMA: 26
MACD_SIGNAL_EMA: 9
SHIFT: 0
UNIT: percent_of_close
STATUS: ACTIVE
```

## Common Formula

```text
ema12 = EMA(Close, 12)
ema26 = EMA(Close, 26)
macd_line = ema12 - ema26
macd_signal = EMA(macd_line, 9)
macd_hist = macd_line - macd_signal
macd_line_pct = (macd_line / Close[1]) * 100
macd_signal_pct = (macd_signal / Close[1]) * 100
macd_hist_pct = (macd_hist / Close[1]) * 100
```

## Not Calibrated In Feature

```text
side
tf
calc_method
price_source
macd_fast_ema
macd_slow_ema
macd_signal_ema
shift
entry_exit
order_size
stop_loss
take_profit
```

## F013 - macd_line

```text
ID: F013
FEATURE: macd_line_1m
ACTION: F013_MACDLINE_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

Calibration params:

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| F013_state | enum | - | - | - | POSITIVE / NEGATIVE | direction | yes |
| F013_thr_pct | float | 0.00 | 2.00 | 0.01 | - | percent_of_close | yes |

Signal rule:

```text
IF state = POSITIVE AND macd_line_pct >= thr_pct: allow = 1
ELSE IF state = NEGATIVE AND macd_line_pct <= -thr_pct: allow = 1
ELSE: allow = 0
```

## F014 - macd_signal

```text
ID: F014
FEATURE: macd_signal_1m
ACTION: F014_MACDSIGNAL_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

Calibration params:

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| F014_state | enum | - | - | - | POSITIVE / NEGATIVE | direction | yes |
| F014_thr_pct | float | 0.00 | 2.00 | 0.01 | - | percent_of_close | yes |

Signal rule:

```text
IF state = POSITIVE AND macd_signal_pct >= thr_pct: allow = 1
ELSE IF state = NEGATIVE AND macd_signal_pct <= -thr_pct: allow = 1
ELSE: allow = 0
```

## F015 - macd_hist

```text
ID: F015
FEATURE: macd_hist_1m
ACTION: F015_MACDHIST_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

Calibration params:

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| F015_state | enum | - | - | - | POSITIVE / NEGATIVE | direction | yes |
| F015_thr_pct | float | 0.00 | 1.00 | 0.01 | - | percent_of_close | yes |

Signal rule:

```text
IF state = POSITIVE AND macd_hist_pct >= thr_pct: allow = 1
ELSE IF state = NEGATIVE AND macd_hist_pct <= -thr_pct: allow = 1
ELSE: allow = 0
```
