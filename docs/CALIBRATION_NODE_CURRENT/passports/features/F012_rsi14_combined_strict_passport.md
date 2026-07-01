# F012 - RSI14 Combined Strict Passport

ID: F012
FEATURE: rsi14_1m
ACTION: RSI14_ALLOW
RUNTIME ACTION: F012_RSI14_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE

Fixed common rules:
- TF: 1m
- CALC_METHOD: CLOSE_BAR
- CANDLE: closed
- PRICE_SOURCE: close
- RSI_PERIOD: 14
- SHIFT: 0
- RSI_RANGE: 0..100
- RSI_MA_METHOD: SMA
- RSI_MA_PERIOD: 14

Calibration params:
- `F012_signal_mode`: `1=LEVEL`, `2=RSI_MA`
- LEVEL mode:
  - `F012_cmp`: `1=GREATER`, `-1=LESS`
  - `F012_level`: min `10`, max `90`, step `1`
- RSI_MA mode:
  - `F012_relation`: `1=ABOVE`, `-1=BELOW`
  - `F012_gap`: min `0`, max `20`, step `1`

Signal rules:
- LEVEL/GREATER: `rsi14 >= F012_level`
- LEVEL/LESS: `rsi14 <= F012_level`
- RSI_MA/ABOVE: `rsi14 - sma(rsi14, 14) >= F012_gap`
- RSI_MA/BELOW: `rsi14 - sma(rsi14, 14) <= -F012_gap`

Not calibrated here:
- side
- tf
- rsi_period
- shift
- calc_method
- price_source
- rsi_ma_method
- rsi_ma_period
- entry_exit
- order_size
- stop_loss
- take_profit
