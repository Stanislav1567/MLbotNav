# LEVEL / RANGE / CHANNEL — STRICT PASSPORT F035-F039

```text
FAMILY: LEVEL_RANGE_CHANNEL
FEATURES: F035-F039
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
```

---

# 0. COMMON_FIXED

```text
TF = 1m
CALC_METHOD = CLOSE_BAR
CANDLE = closed
PRICE_SOURCE = Close
HIGH_LOW_SOURCE = High/Low
```

## COMMENT_COMMON_FIXED

```text
COMMON_FIXED обязателен.
Все уровни, диапазоны и каналы считаются только по закрытым 1m-свечам.
Вход в runtime/MQL получает только ALLOW = 1/0.
```

---

# 1. BLOCK STRUCTURE

```text
BLOCK_A_LEVELS:
    F035 support_distance
    F036 resistance_distance
    F037 level_strength

BLOCK_B_RANGE:
    F038 position_in_range

BLOCK_C_CHANNEL:
    F039 trend_channel_pos
```

---

# 2. BLOCK A — LEVELS

```text
BLOCK_ID: LEVEL_A
BLOCK_NAME: SUPPORT_RESISTANCE_LEVELS
FEATURES: F035,F036,F037
PURPOSE: дистанция до поддержки/сопротивления и сила ближайшего уровня
CALIBRATION_PRIORITY: 1
```

## FIXED_LEVEL_ENGINE

```text
LEVEL_METHOD = swing_pivot_levels
LEVEL_LOOKBACK = 240
PIVOT_LEFT = 3
PIVOT_RIGHT = 3
MERGE_TOLERANCE_PCT = 0.15
MIN_TOUCHES = 2
TOUCH_TOLERANCE_PCT = 0.10
LEVEL_SOURCE = High/Low
LEVEL_UPDATE = every_closed_bar
```

## COMMENT_LEVEL_ENGINE

```text
FIXED_LEVEL_ENGINE не калибруется.
Он нужен, чтобы Оптумно, ML и MQL одинаково находили уровни.

Support = объединённые swing-low уровни ниже или рядом с текущей ценой.
Resistance = объединённые swing-high уровни выше или рядом с текущей ценой.

MERGE_TOLERANCE_PCT объединяет близкие уровни в один.
TOUCH_TOLERANCE_PCT считает касание уровня.
```

## LEVEL_DATA_GUARD

```text
IF no_support_level:
    F035_SUPPORTDIST_ALLOW = 0

IF no_resistance_level:
    F036_RESDIST_ALLOW = 0

IF no_level:
    F037_LEVELSTRENGTH_ALLOW = 0
```

---

## F035 — support_distance

```text
ID: F035
FEATURE: support_distance_1m
ACTION: SUPPORTDIST_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

### FORMULA

```text
nearest_support = nearest_active_support_level

support_distance_pct = (Close[1] / nearest_support - 1) * 100

support_abs_distance_pct = abs(support_distance_pct)
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| distance_state | enum | - | - | - | NEAR / FAR | distance | yes |
| dist_thr_pct | float | 0.00 | 3.00 | 0.01 | - | percent | yes |

### SIGNAL_RULE

```text
IF distance_state = NEAR AND support_abs_distance_pct <= dist_thr_pct:
    SUPPORTDIST_ALLOW = 1

ELSE IF distance_state = FAR AND support_abs_distance_pct >= dist_thr_pct:
    SUPPORTDIST_ALLOW = 1

ELSE:
    SUPPORTDIST_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F035_distance_state
F035_dist_thr_pct
F035_SUPPORTDIST_ALLOW
```

### REGISTRY_ROW

```text
F035 | support_distance_1m | SUPPORTDIST_ALLOW | LEVEL_A | distance_state(NEAR/FAR),dist_thr_pct(min=0.00,max=3.00,step=0.01) | fixed: LEVEL_LOOKBACK=240,PIVOT=3/3,MERGE_TOLERANCE=0.15,TOUCH_TOLERANCE=0.10,CALC_METHOD=CLOSE_BAR | output: 1=ALLOW,0=BLOCK
```

---

## F036 — resistance_distance

```text
ID: F036
FEATURE: resistance_distance_1m
ACTION: RESDIST_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

### FORMULA

```text
nearest_resistance = nearest_active_resistance_level

resistance_distance_pct = (nearest_resistance / Close[1] - 1) * 100

resistance_abs_distance_pct = abs(resistance_distance_pct)
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| distance_state | enum | - | - | - | NEAR / FAR | distance | yes |
| dist_thr_pct | float | 0.00 | 3.00 | 0.01 | - | percent | yes |

### SIGNAL_RULE

```text
IF distance_state = NEAR AND resistance_abs_distance_pct <= dist_thr_pct:
    RESDIST_ALLOW = 1

ELSE IF distance_state = FAR AND resistance_abs_distance_pct >= dist_thr_pct:
    RESDIST_ALLOW = 1

ELSE:
    RESDIST_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F036_distance_state
F036_dist_thr_pct
F036_RESDIST_ALLOW
```

### REGISTRY_ROW

```text
F036 | resistance_distance_1m | RESDIST_ALLOW | LEVEL_A | distance_state(NEAR/FAR),dist_thr_pct(min=0.00,max=3.00,step=0.01) | fixed: LEVEL_LOOKBACK=240,PIVOT=3/3,MERGE_TOLERANCE=0.15,TOUCH_TOLERANCE=0.10,CALC_METHOD=CLOSE_BAR | output: 1=ALLOW,0=BLOCK
```

---

## F037 — level_strength

```text
ID: F037
FEATURE: level_strength_1m
ACTION: LEVELSTRENGTH_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

### FORMULA

```text
selected_level_type:
    SUPPORT
    RESISTANCE
    NEAREST

touch_count = number_of_touches_within_TOUCH_TOLERANCE

recency_score = max(0, 1 - bars_since_last_touch / LEVEL_LOOKBACK)

volume_score = level_touch_volume / avg_volume_20

level_strength_score = touch_count + recency_score + min(volume_score, 3)
```

### FIXED_FOR_STRENGTH

```text
AVG_VOLUME_WINDOW = 20
MAX_VOLUME_SCORE = 3
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| level_type | enum | - | - | - | SUPPORT / RESISTANCE / NEAREST | level_type | yes |
| strength_state | enum | - | - | - | STRONG / WEAK | strength | yes |
| strength_thr | float | 2.0 | 10.0 | 0.5 | - | score | yes |

### SIGNAL_RULE

```text
IF strength_state = STRONG AND level_strength_score >= strength_thr:
    LEVELSTRENGTH_ALLOW = 1

ELSE IF strength_state = WEAK AND level_strength_score <= strength_thr:
    LEVELSTRENGTH_ALLOW = 1

ELSE:
    LEVELSTRENGTH_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F037_level_type
F037_strength_state
F037_strength_thr
F037_LEVELSTRENGTH_ALLOW
```

### REGISTRY_ROW

```text
F037 | level_strength_1m | LEVELSTRENGTH_ALLOW | LEVEL_A | level_type(SUPPORT/RESISTANCE/NEAREST),strength_state(STRONG/WEAK),strength_thr(min=2.0,max=10.0,step=0.5) | fixed: LEVEL_LOOKBACK=240,PIVOT=3/3,TOUCH_TOLERANCE=0.10,AVG_VOLUME_WINDOW=20 | output: 1=ALLOW,0=BLOCK
```

---

# 3. BLOCK B — RANGE

```text
BLOCK_ID: LEVEL_B
BLOCK_NAME: POSITION_IN_RANGE
FEATURES: F038
PURPOSE: положение цены внутри rolling high-low диапазона
CALIBRATION_PRIORITY: 2
```

## FIXED_RANGE_ENGINE

```text
RANGE_METHOD = rolling_high_low
RANGE_LOOKBACK = 240
RANGE_HIGH = highest(High, RANGE_LOOKBACK)
RANGE_LOW = lowest(Low, RANGE_LOOKBACK)
```

## COMMENT_RANGE_ENGINE

```text
F038 показывает, где находится текущая цена внутри диапазона.
0 = нижняя граница диапазона.
100 = верхняя граница диапазона.
```

---

## F038 — position_in_range

```text
ID: F038
FEATURE: position_in_range_1m
ACTION: RANGEPOSE_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

### FORMULA

```text
range_size = RANGE_HIGH - RANGE_LOW

position_in_range = ((Close[1] - RANGE_LOW) / range_size) * 100
```

### DATA_GUARD

```text
IF range_size <= 0:
    RANGEPOSE_ALLOW = 0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| zone | enum | - | - | - | LOW / HIGH | range_zone | yes |
| level | int | 5 | 95 | 1 | - | percent_position | yes |

### SIGNAL_RULE

```text
IF zone = LOW AND position_in_range <= level:
    RANGEPOSE_ALLOW = 1

ELSE IF zone = HIGH AND position_in_range >= level:
    RANGEPOSE_ALLOW = 1

ELSE:
    RANGEPOSE_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F038_zone
F038_level
F038_RANGEPOSE_ALLOW
```

### REGISTRY_ROW

```text
F038 | position_in_range_1m | RANGEPOSE_ALLOW | LEVEL_B | zone(LOW/HIGH),level(min=5,max=95,step=1) | fixed: RANGE_LOOKBACK=240,CALC_METHOD=CLOSE_BAR | output: 1=ALLOW,0=BLOCK
```

---

# 4. BLOCK C — TREND CHANNEL

```text
BLOCK_ID: LEVEL_C
BLOCK_NAME: TREND_CHANNEL_POSITION
FEATURES: F039
PURPOSE: положение цены внутри линейного трендового канала
CALIBRATION_PRIORITY: 3
```

## FIXED_CHANNEL_ENGINE

```text
CHANNEL_METHOD = linear_regression_channel
CHANNEL_LOOKBACK = 120
CHANNEL_WIDTH_METHOD = residual_std
CHANNEL_K = 2.0
CHANNEL_SOURCE = Close
```

## COMMENT_CHANNEL_ENGINE

```text
F039 показывает положение цены внутри трендового канала.
0 = нижняя граница канала.
50 = середина канала.
100 = верхняя граница канала.
Значение может быть ниже 0 или выше 100, если цена вышла за канал.
```

---

## F039 — trend_channel_pos

```text
ID: F039
FEATURE: trend_channel_pos_1m
ACTION: CHANNELPOS_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

### FORMULA

```text
channel_mid = linear_regression(Close, CHANNEL_LOOKBACK)

channel_width = std(residuals, CHANNEL_LOOKBACK) * CHANNEL_K

channel_upper = channel_mid + channel_width

channel_lower = channel_mid - channel_width

channel_pos = ((Close[1] - channel_lower) / (channel_upper - channel_lower)) * 100
```

### DATA_GUARD

```text
IF channel_upper <= channel_lower:
    CHANNELPOS_ALLOW = 0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| zone | enum | - | - | - | LOWER / UPPER / OUTSIDE_UP / OUTSIDE_DOWN | channel_zone | yes |
| level | int | 0 | 100 | 1 | - | percent_position | conditional |
| outside_thr | int | 0 | 50 | 1 | - | percent_outside | conditional |

### SIGNAL_RULE

```text
IF zone = LOWER AND channel_pos <= level:
    CHANNELPOS_ALLOW = 1

ELSE IF zone = UPPER AND channel_pos >= level:
    CHANNELPOS_ALLOW = 1

ELSE IF zone = OUTSIDE_UP AND channel_pos >= 100 + outside_thr:
    CHANNELPOS_ALLOW = 1

ELSE IF zone = OUTSIDE_DOWN AND channel_pos <= 0 - outside_thr:
    CHANNELPOS_ALLOW = 1

ELSE:
    CHANNELPOS_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F039_zone
F039_level
F039_outside_thr
F039_CHANNELPOS_ALLOW
```

### REGISTRY_ROW

```text
F039 | trend_channel_pos_1m | CHANNELPOS_ALLOW | LEVEL_C | zone(LOWER/UPPER/OUTSIDE_UP/OUTSIDE_DOWN),level(min=0,max=100,step=1),outside_thr(min=0,max=50,step=1) | fixed: CHANNEL_LOOKBACK=120,CHANNEL_K=2.0,CALC_METHOD=CLOSE_BAR | output: 1=ALLOW,0=BLOCK
```

---

# 5. CALIBRATION_ORDER

```text
1. BLOCK_A_LEVELS: F035,F036,F037
2. BLOCK_B_RANGE: F038
3. BLOCK_C_CHANNEL: F039
```

## COMMENT_CALIBRATION_ORDER

```text
Сначала проверять уровни поддержки/сопротивления.
Потом положение в диапазоне.
Потом положение в трендовом канале.
```

---

# 6. GLOBAL_NOT_CALIBRATED

```text
side
tf
calc_method
price_source
high_low_source
level_method
level_lookback
pivot_left
pivot_right
merge_tolerance_pct
touch_tolerance_pct
range_method
range_lookback
channel_method
channel_lookback
channel_k
entry_exit
order_size
stop_loss
take_profit
```

---

# 7. REGISTRY_ROWS_SHORT

```text
F035 | support_distance_1m | SUPPORTDIST_ALLOW | LEVEL_A | distance_state(NEAR/FAR),dist_thr_pct(0.00–3.00 step 0.01) | output 1/0

F036 | resistance_distance_1m | RESDIST_ALLOW | LEVEL_A | distance_state(NEAR/FAR),dist_thr_pct(0.00–3.00 step 0.01) | output 1/0

F037 | level_strength_1m | LEVELSTRENGTH_ALLOW | LEVEL_A | level_type(SUPPORT/RESISTANCE/NEAREST),strength_state(STRONG/WEAK),strength_thr(2.0–10.0 step 0.5) | output 1/0

F038 | position_in_range_1m | RANGEPOSE_ALLOW | LEVEL_B | zone(LOW/HIGH),level(5–95 step 1) | output 1/0

F039 | trend_channel_pos_1m | CHANNELPOS_ALLOW | LEVEL_C | zone(LOWER/UPPER/OUTSIDE_UP/OUTSIDE_DOWN),level(0–100 step 1),outside_thr(0–50 step 1) | output 1/0
```
