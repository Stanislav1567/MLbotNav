# CANDLE PATTERNS — STRICT PASSPORT F053-F060 — V1

```text
FAMILY: CANDLE_PATTERNS
FEATURES: F053-F060
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F053-F060 проверяют свечные price-action паттерны на последней закрытой 1m-свече или на последних двух закрытых 1m-свечах.

Блок НЕ открывает сделку сам.
Блок НЕ закрывает сделку.
Блок НЕ ставит TP/SL.

Он только возвращает:
1 = вход разрешён
0 = вход запрещён
```

---

# 1. COMMON_FIXED

```text
TF = 1m
CALC_METHOD = CLOSE_BAR
CANDLE = closed
PRICE_SOURCE = OHLC
PATTERN_SCOPE = last_closed_candle / last_two_closed_candles
CONFIRMATION_MODE = pattern_closed
CUSTOM_CALC = YES
```

## COMMENT_COMMON_FIXED

```text
Все свечные паттерны считаются только по закрытым свечам.
Текущая незакрытая свеча не используется.
```

---

# 2. COMMON_CANDLE_FORMULAS

```text
range[1] = High[1] - Low[1]
body[1] = abs(Close[1] - Open[1])

upper_wick[1] = High[1] - max(Open[1], Close[1])
lower_wick[1] = min(Open[1], Close[1]) - Low[1]

body_pct[1] = body[1] / range[1] * 100
upper_wick_pct[1] = upper_wick[1] / range[1] * 100
lower_wick_pct[1] = lower_wick[1] / range[1] * 100

range_pct[1] = range[1] / Open[1] * 100

bull_candle[1] = Close[1] > Open[1]
bear_candle[1] = Close[1] < Open[1]
```

## DATA_GUARD_COMMON

```text
IF range[1] <= 0:
    PATTERN_ALLOW = 0

IF Open[1] <= 0:
    PATTERN_ALLOW = 0
```

---

# 3. F053 — doji_flag

```text
ID: F053
FEATURE: doji_flag_1m
ACTION: DOJI_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если последняя закрытая 1m-свеча является doji.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| max_body_pct | float | 2 | 15 | 1 | - | percent_of_range | yes |
| min_range_pct | float | 0.01 | 0.50 | 0.01 | - | percent_of_price | yes |
| wick_mode | enum | - | - | - | ANY / BALANCED | wick_mode | yes |
| wick_balance_max_pct | float | 20 | 80 | 5 | - | percent_of_range | conditional |

## SIGNAL_RULE

```text
DOJI_BASE:
    body_pct[1] <= max_body_pct
    AND range_pct[1] >= min_range_pct

WICK_BALANCED:
    abs(upper_wick_pct[1] - lower_wick_pct[1]) <= wick_balance_max_pct

IF wick_mode = ANY AND DOJI_BASE:
    DOJI_ALLOW = 1

ELSE IF wick_mode = BALANCED AND DOJI_BASE AND WICK_BALANCED:
    DOJI_ALLOW = 1

ELSE:
    DOJI_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F053_max_body_pct
F053_min_range_pct
F053_wick_mode
F053_wick_balance_max_pct
F053_DOJI_ALLOW
```

## REGISTRY_ROW

```text
F053 | doji_flag_1m | DOJI_ALLOW | CANDLE_PATTERNS | max_body_pct(2–15 step 1),min_range_pct(0.01–0.50 step 0.01),wick_mode(ANY/BALANCED),wick_balance_max_pct(20–80 step 5) | output 1/0
```

---

# 4. F054 — inside_bar_flag

```text
ID: F054
FEATURE: inside_bar_flag_1m
ACTION: INSIDEBAR_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если последняя закрытая 1m-свеча находится внутри диапазона предыдущей свечи.
```

## FORMULA

```text
inside_range_ratio = range[1] / range[2]
mother_range_pct = (High[2] - Low[2]) / Open[2] * 100
```

## DATA_GUARD

```text
IF range[2] <= 0:
    INSIDEBAR_ALLOW = 0

IF Open[2] <= 0:
    INSIDEBAR_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| containment_mode | enum | - | - | - | STRICT / EQUAL_ALLOWED | containment | yes |
| max_inside_range_ratio | float | 0.30 | 1.00 | 0.05 | - | ratio | yes |
| mother_min_range_pct | float | 0.02 | 2.00 | 0.01 | - | percent_of_price | yes |

## SIGNAL_RULE

```text
STRICT_INSIDE:
    High[1] < High[2]
    AND Low[1] > Low[2]

EQUAL_ALLOWED_INSIDE:
    High[1] <= High[2]
    AND Low[1] >= Low[2]

RANGE_FILTER:
    inside_range_ratio <= max_inside_range_ratio
    AND mother_range_pct >= mother_min_range_pct

IF containment_mode = STRICT AND STRICT_INSIDE AND RANGE_FILTER:
    INSIDEBAR_ALLOW = 1

ELSE IF containment_mode = EQUAL_ALLOWED AND EQUAL_ALLOWED_INSIDE AND RANGE_FILTER:
    INSIDEBAR_ALLOW = 1

ELSE:
    INSIDEBAR_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F054_containment_mode
F054_max_inside_range_ratio
F054_mother_min_range_pct
F054_INSIDEBAR_ALLOW
```

## REGISTRY_ROW

```text
F054 | inside_bar_flag_1m | INSIDEBAR_ALLOW | CANDLE_PATTERNS | containment_mode(STRICT/EQUAL_ALLOWED),max_inside_range_ratio(0.30–1.00 step 0.05),mother_min_range_pct(0.02–2.00 step 0.01) | output 1/0
```

---

# 5. F055 — pin_bar_bull_flag

```text
ID: F055
FEATURE: pin_bar_bull_flag_1m
ACTION: PINBULL_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если последняя закрытая свеча является bullish pin bar.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| wick_body_ratio | float | 1.5 | 5.0 | 0.5 | - | ratio | yes |
| wick_min_pct | float | 50 | 85 | 5 | - | percent_of_range | yes |
| opposite_wick_max_pct | float | 0 | 30 | 5 | - | percent_of_range | yes |
| body_zone_pct | float | 20 | 50 | 5 | - | percent_of_range | yes |
| min_range_pct | float | 0.02 | 1.00 | 0.01 | - | percent_of_price | yes |

## SIGNAL_RULE

```text
BODY_IN_TOP_ZONE:
    min(Open[1], Close[1]) >= High[1] - range[1] * body_zone_pct / 100

PIN_BULL_SHAPE:
    lower_wick[1] >= body[1] * wick_body_ratio
    AND lower_wick_pct[1] >= wick_min_pct
    AND upper_wick_pct[1] <= opposite_wick_max_pct
    AND BODY_IN_TOP_ZONE
    AND range_pct[1] >= min_range_pct

IF PIN_BULL_SHAPE:
    PINBULL_ALLOW = 1
ELSE:
    PINBULL_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F055_wick_body_ratio
F055_wick_min_pct
F055_opposite_wick_max_pct
F055_body_zone_pct
F055_min_range_pct
F055_PINBULL_ALLOW
```

## REGISTRY_ROW

```text
F055 | pin_bar_bull_flag_1m | PINBULL_ALLOW | CANDLE_PATTERNS | wick_body_ratio(1.5–5.0 step 0.5),wick_min_pct(50–85 step 5),opposite_wick_max_pct(0–30 step 5),body_zone_pct(20–50 step 5),min_range_pct(0.02–1.00 step 0.01) | output 1/0
```

---

# 6. F056 — pin_bar_bear_flag

```text
ID: F056
FEATURE: pin_bar_bear_flag_1m
ACTION: PINBEAR_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если последняя закрытая свеча является bearish pin bar.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| wick_body_ratio | float | 1.5 | 5.0 | 0.5 | - | ratio | yes |
| wick_min_pct | float | 50 | 85 | 5 | - | percent_of_range | yes |
| opposite_wick_max_pct | float | 0 | 30 | 5 | - | percent_of_range | yes |
| body_zone_pct | float | 20 | 50 | 5 | - | percent_of_range | yes |
| min_range_pct | float | 0.02 | 1.00 | 0.01 | - | percent_of_price | yes |

## SIGNAL_RULE

```text
BODY_IN_BOTTOM_ZONE:
    max(Open[1], Close[1]) <= Low[1] + range[1] * body_zone_pct / 100

PIN_BEAR_SHAPE:
    upper_wick[1] >= body[1] * wick_body_ratio
    AND upper_wick_pct[1] >= wick_min_pct
    AND lower_wick_pct[1] <= opposite_wick_max_pct
    AND BODY_IN_BOTTOM_ZONE
    AND range_pct[1] >= min_range_pct

IF PIN_BEAR_SHAPE:
    PINBEAR_ALLOW = 1
ELSE:
    PINBEAR_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F056_wick_body_ratio
F056_wick_min_pct
F056_opposite_wick_max_pct
F056_body_zone_pct
F056_min_range_pct
F056_PINBEAR_ALLOW
```

## REGISTRY_ROW

```text
F056 | pin_bar_bear_flag_1m | PINBEAR_ALLOW | CANDLE_PATTERNS | wick_body_ratio(1.5–5.0 step 0.5),wick_min_pct(50–85 step 5),opposite_wick_max_pct(0–30 step 5),body_zone_pct(20–50 step 5),min_range_pct(0.02–1.00 step 0.01) | output 1/0
```

---

# 7. F057 — hammer_flag

```text
ID: F057
FEATURE: hammer_flag_1m
ACTION: HAMMER_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если последняя закрытая свеча является hammer после снижения.
```

## TREND_CONTEXT_FORMULA

```text
pretrend_return_pct = (Close[2] / Close[2 + trend_lookback_bars] - 1) * 100
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| wick_body_ratio | float | 1.5 | 5.0 | 0.5 | - | ratio | yes |
| lower_wick_min_pct | float | 50 | 85 | 5 | - | percent_of_range | yes |
| upper_wick_max_pct | float | 0 | 25 | 5 | - | percent_of_range | yes |
| body_zone_pct | float | 20 | 50 | 5 | - | percent_of_range | yes |
| trend_lookback_bars | int | 3 | 20 | 1 | - | bars | yes |
| trend_min_drop_pct | float | 0.05 | 2.00 | 0.05 | - | percent | yes |

## SIGNAL_RULE

```text
HAMMER_SHAPE:
    lower_wick[1] >= body[1] * wick_body_ratio
    AND lower_wick_pct[1] >= lower_wick_min_pct
    AND upper_wick_pct[1] <= upper_wick_max_pct
    AND min(Open[1], Close[1]) >= High[1] - range[1] * body_zone_pct / 100

DOWNTREND_CONTEXT:
    pretrend_return_pct <= -trend_min_drop_pct

IF HAMMER_SHAPE AND DOWNTREND_CONTEXT:
    HAMMER_ALLOW = 1
ELSE:
    HAMMER_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F057_wick_body_ratio
F057_lower_wick_min_pct
F057_upper_wick_max_pct
F057_body_zone_pct
F057_trend_lookback_bars
F057_trend_min_drop_pct
F057_HAMMER_ALLOW
```

## REGISTRY_ROW

```text
F057 | hammer_flag_1m | HAMMER_ALLOW | CANDLE_PATTERNS | wick_body_ratio(1.5–5.0 step 0.5),lower_wick_min_pct(50–85 step 5),upper_wick_max_pct(0–25 step 5),body_zone_pct(20–50 step 5),trend_lookback_bars(3–20 step 1),trend_min_drop_pct(0.05–2.00 step 0.05) | output 1/0
```

---

# 8. F058 — shooting_star_flag

```text
ID: F058
FEATURE: shooting_star_flag_1m
ACTION: SHOOTINGSTAR_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если последняя закрытая свеча является shooting star после роста.
```

## TREND_CONTEXT_FORMULA

```text
pretrend_return_pct = (Close[2] / Close[2 + trend_lookback_bars] - 1) * 100
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| wick_body_ratio | float | 1.5 | 5.0 | 0.5 | - | ratio | yes |
| upper_wick_min_pct | float | 50 | 85 | 5 | - | percent_of_range | yes |
| lower_wick_max_pct | float | 0 | 25 | 5 | - | percent_of_range | yes |
| body_zone_pct | float | 20 | 50 | 5 | - | percent_of_range | yes |
| trend_lookback_bars | int | 3 | 20 | 1 | - | bars | yes |
| trend_min_rise_pct | float | 0.05 | 2.00 | 0.05 | - | percent | yes |

## SIGNAL_RULE

```text
SHOOTING_STAR_SHAPE:
    upper_wick[1] >= body[1] * wick_body_ratio
    AND upper_wick_pct[1] >= upper_wick_min_pct
    AND lower_wick_pct[1] <= lower_wick_max_pct
    AND max(Open[1], Close[1]) <= Low[1] + range[1] * body_zone_pct / 100

UPTREND_CONTEXT:
    pretrend_return_pct >= trend_min_rise_pct

IF SHOOTING_STAR_SHAPE AND UPTREND_CONTEXT:
    SHOOTINGSTAR_ALLOW = 1
ELSE:
    SHOOTINGSTAR_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F058_wick_body_ratio
F058_upper_wick_min_pct
F058_lower_wick_max_pct
F058_body_zone_pct
F058_trend_lookback_bars
F058_trend_min_rise_pct
F058_SHOOTINGSTAR_ALLOW
```

## REGISTRY_ROW

```text
F058 | shooting_star_flag_1m | SHOOTINGSTAR_ALLOW | CANDLE_PATTERNS | wick_body_ratio(1.5–5.0 step 0.5),upper_wick_min_pct(50–85 step 5),lower_wick_max_pct(0–25 step 5),body_zone_pct(20–50 step 5),trend_lookback_bars(3–20 step 1),trend_min_rise_pct(0.05–2.00 step 0.05) | output 1/0
```

---

# 9. F059 — engulf_bull_flag

```text
ID: F059
FEATURE: engulf_bull_flag_1m
ACTION: ENGULFBULL_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если последняя закрытая свеча формирует bullish engulfing относительно предыдущей свечи.
```

## FORMULAS

```text
prev_body = abs(Close[2] - Open[2])
curr_body = abs(Close[1] - Open[1])
body_ratio = curr_body / prev_body
```

## DATA_GUARD

```text
IF prev_body <= 0:
    ENGULFBULL_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| engulf_mode | enum | - | - | - | BODY / FULL_RANGE | engulf_type | yes |
| min_engulf_ratio | float | 1.0 | 2.0 | 0.1 | - | ratio | yes |
| min_body_pct | float | 10 | 70 | 5 | - | percent_of_range | yes |
| trend_lookback_bars | int | 2 | 20 | 1 | - | bars | yes |
| trend_min_drop_pct | float | 0.00 | 2.00 | 0.05 | - | percent | yes |

## SIGNAL_RULE

```text
BULL_BODY_ENGULF:
    bear_candle[2]
    AND bull_candle[1]
    AND Open[1] <= Close[2]
    AND Close[1] >= Open[2]

BULL_FULL_RANGE_ENGULF:
    bear_candle[2]
    AND bull_candle[1]
    AND Low[1] <= Low[2]
    AND High[1] >= High[2]

QUALITY_FILTER:
    body_ratio >= min_engulf_ratio
    AND body_pct[1] >= min_body_pct

DOWNTREND_CONTEXT:
    (Close[2] / Close[2 + trend_lookback_bars] - 1) * 100 <= -trend_min_drop_pct

IF engulf_mode = BODY AND BULL_BODY_ENGULF AND QUALITY_FILTER AND DOWNTREND_CONTEXT:
    ENGULFBULL_ALLOW = 1

ELSE IF engulf_mode = FULL_RANGE AND BULL_FULL_RANGE_ENGULF AND QUALITY_FILTER AND DOWNTREND_CONTEXT:
    ENGULFBULL_ALLOW = 1

ELSE:
    ENGULFBULL_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F059_engulf_mode
F059_min_engulf_ratio
F059_min_body_pct
F059_trend_lookback_bars
F059_trend_min_drop_pct
F059_ENGULFBULL_ALLOW
```

## REGISTRY_ROW

```text
F059 | engulf_bull_flag_1m | ENGULFBULL_ALLOW | CANDLE_PATTERNS | engulf_mode(BODY/FULL_RANGE),min_engulf_ratio(1.0–2.0 step 0.1),min_body_pct(10–70 step 5),trend_lookback_bars(2–20 step 1),trend_min_drop_pct(0.00–2.00 step 0.05) | output 1/0
```

---

# 10. F060 — engulf_bear_flag

```text
ID: F060
FEATURE: engulf_bear_flag_1m
ACTION: ENGULFBEAR_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если последняя закрытая свеча формирует bearish engulfing относительно предыдущей свечи.
```

## FORMULAS

```text
prev_body = abs(Close[2] - Open[2])
curr_body = abs(Close[1] - Open[1])
body_ratio = curr_body / prev_body
```

## DATA_GUARD

```text
IF prev_body <= 0:
    ENGULFBEAR_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| engulf_mode | enum | - | - | - | BODY / FULL_RANGE | engulf_type | yes |
| min_engulf_ratio | float | 1.0 | 2.0 | 0.1 | - | ratio | yes |
| min_body_pct | float | 10 | 70 | 5 | - | percent_of_range | yes |
| trend_lookback_bars | int | 2 | 20 | 1 | - | bars | yes |
| trend_min_rise_pct | float | 0.00 | 2.00 | 0.05 | - | percent | yes |

## SIGNAL_RULE

```text
BEAR_BODY_ENGULF:
    bull_candle[2]
    AND bear_candle[1]
    AND Open[1] >= Close[2]
    AND Close[1] <= Open[2]

BEAR_FULL_RANGE_ENGULF:
    bull_candle[2]
    AND bear_candle[1]
    AND High[1] >= High[2]
    AND Low[1] <= Low[2]

QUALITY_FILTER:
    body_ratio >= min_engulf_ratio
    AND body_pct[1] >= min_body_pct

UPTREND_CONTEXT:
    (Close[2] / Close[2 + trend_lookback_bars] - 1) * 100 >= trend_min_rise_pct

IF engulf_mode = BODY AND BEAR_BODY_ENGULF AND QUALITY_FILTER AND UPTREND_CONTEXT:
    ENGULFBEAR_ALLOW = 1

ELSE IF engulf_mode = FULL_RANGE AND BEAR_FULL_RANGE_ENGULF AND QUALITY_FILTER AND UPTREND_CONTEXT:
    ENGULFBEAR_ALLOW = 1

ELSE:
    ENGULFBEAR_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F060_engulf_mode
F060_min_engulf_ratio
F060_min_body_pct
F060_trend_lookback_bars
F060_trend_min_rise_pct
F060_ENGULFBEAR_ALLOW
```

## REGISTRY_ROW

```text
F060 | engulf_bear_flag_1m | ENGULFBEAR_ALLOW | CANDLE_PATTERNS | engulf_mode(BODY/FULL_RANGE),min_engulf_ratio(1.0–2.0 step 0.1),min_body_pct(10–70 step 5),trend_lookback_bars(2–20 step 1),trend_min_rise_pct(0.00–2.00 step 0.05) | output 1/0
```

---

# 11. CALIBRATION_ORDER

```text
1. F055 pin_bar_bull_flag
2. F056 pin_bar_bear_flag
3. F059 engulf_bull_flag
4. F060 engulf_bear_flag
5. F057 hammer_flag
6. F058 shooting_star_flag
7. F054 inside_bar_flag
8. F053 doji_flag
```

## COMMENT_CALIBRATION_ORDER

```text
Сначала калибровать направленные свечные сигналы.
Потом разворотные с контекстом.
Потом inside bar и doji как нейтральные/контекстные свечи.
```

---

# 12. GLOBAL_NOT_CALIBRATED

```text
side
tf
calc_method
price_source
current_unclosed_candle
entry_exit
order_size
take_profit_order
stop_loss_order
```

---

# 13. REGISTRY_ROWS_SHORT

```text
F053 | doji_flag_1m | DOJI_ALLOW | CANDLE_PATTERNS | max_body_pct(2–15 step 1),min_range_pct(0.01–0.50 step 0.01),wick_mode(ANY/BALANCED),wick_balance_max_pct(20–80 step 5) | output 1/0

F054 | inside_bar_flag_1m | INSIDEBAR_ALLOW | CANDLE_PATTERNS | containment_mode(STRICT/EQUAL_ALLOWED),max_inside_range_ratio(0.30–1.00 step 0.05),mother_min_range_pct(0.02–2.00 step 0.01) | output 1/0

F055 | pin_bar_bull_flag_1m | PINBULL_ALLOW | CANDLE_PATTERNS | wick_body_ratio(1.5–5.0 step 0.5),wick_min_pct(50–85 step 5),opposite_wick_max_pct(0–30 step 5),body_zone_pct(20–50 step 5),min_range_pct(0.02–1.00 step 0.01) | output 1/0

F056 | pin_bar_bear_flag_1m | PINBEAR_ALLOW | CANDLE_PATTERNS | wick_body_ratio(1.5–5.0 step 0.5),wick_min_pct(50–85 step 5),opposite_wick_max_pct(0–30 step 5),body_zone_pct(20–50 step 5),min_range_pct(0.02–1.00 step 0.01) | output 1/0

F057 | hammer_flag_1m | HAMMER_ALLOW | CANDLE_PATTERNS | wick_body_ratio(1.5–5.0 step 0.5),lower_wick_min_pct(50–85 step 5),upper_wick_max_pct(0–25 step 5),body_zone_pct(20–50 step 5),trend_lookback_bars(3–20 step 1),trend_min_drop_pct(0.05–2.00 step 0.05) | output 1/0

F058 | shooting_star_flag_1m | SHOOTINGSTAR_ALLOW | CANDLE_PATTERNS | wick_body_ratio(1.5–5.0 step 0.5),upper_wick_min_pct(50–85 step 5),lower_wick_max_pct(0–25 step 5),body_zone_pct(20–50 step 5),trend_lookback_bars(3–20 step 1),trend_min_rise_pct(0.05–2.00 step 0.05) | output 1/0

F059 | engulf_bull_flag_1m | ENGULFBULL_ALLOW | CANDLE_PATTERNS | engulf_mode(BODY/FULL_RANGE),min_engulf_ratio(1.0–2.0 step 0.1),min_body_pct(10–70 step 5),trend_lookback_bars(2–20 step 1),trend_min_drop_pct(0.00–2.00 step 0.05) | output 1/0

F060 | engulf_bear_flag_1m | ENGULFBEAR_ALLOW | CANDLE_PATTERNS | engulf_mode(BODY/FULL_RANGE),min_engulf_ratio(1.0–2.0 step 0.1),min_body_pct(10–70 step 5),trend_lookback_bars(2–20 step 1),trend_min_rise_pct(0.00–2.00 step 0.05) | output 1/0
```
