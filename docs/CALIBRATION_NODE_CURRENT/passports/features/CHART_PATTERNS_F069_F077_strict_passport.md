# CHART PATTERNS — STRICT PASSPORT F069-F077 — V1

```text
FAMILY: CHART_PATTERNS
FEATURES: F069-F077
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F069-F077 ищут графические паттерны на 1m и возвращают разрешение/запрет входа.

Блок НЕ открывает сделку сам.
Блок НЕ закрывает сделку.
Блок НЕ ставит TP/SL.

Output:
1 = вход разрешён
0 = вход запрещён
```

---

# 1. COMMON_FIXED

```text
TF = 1m
CALC_METHOD = CLOSE_BAR
CANDLE = closed
PRICE_SOURCE = Close
HIGH_LOW_SOURCE = High/Low
REPAINT_POLICY = no_unconfirmed_pivot
CUSTOM_CALC = YES
```

---

# 2. FIXED_PATTERN_ENGINE

```text
PATTERN_ENGINE = confirmed_swing_geometry
SWING_LOOKBACK = 240
PIVOT_LEFT = 5
PIVOT_RIGHT = 5
MIN_SWING_PCT = 0.20
MAX_PATTERN_AGE_BARS = 240
PATTERN_CONFIRMATION = close_bar
```

```text
COMMENT:
Движок паттернов не калибруется.
Калибруются только правила паттерна, пороги, подтверждение и допуски.
```

---

# 3. BLOCK STRUCTURE

```text
BLOCK_A_REVERSAL:
    F069 double_bottom_flag
    F070 double_top_flag
    F071 head_shoulders_flag
    F072 inverse_head_shoulders_flag

BLOCK_B_COMPRESSION:
    F073 triangle_flag
    F074 pennant_flag
    F075 wedge_rising_flag
    F076 wedge_falling_flag

BLOCK_C_RANGE:
    F077 range_flag
```

---

# 4. COMMON RUNTIME MEMORY

```text
pattern_event fields:

pattern_id
pattern_family
pattern_direction
pattern_bar
pattern_price
pattern_quality_score
pattern_neckline
pattern_breakout_level
pattern_start_bar
pattern_end_bar
```

---

# 5. F069 — double_bottom_flag

```text
ID: F069
FEATURE: double_bottom_flag_1m
ACTION: DOUBLEBOTTOM_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
DIRECTION: BULLISH
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit |
|---|---:|---:|---:|---:|---|---|
| bottom_tolerance_pct | float | 0.05 | 1.00 | 0.05 | - | percent |
| min_separation_bars | int | 5 | 60 | 5 | - | bars |
| neckline_break_required | enum | - | - | - | YES / NO | bool |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent |
| max_pattern_age_bars | int | 20 | 240 | 10 | - | bars |

## SIGNAL_RULE

```text
BOTTOMS_MATCH:
    abs(bottom_2 / bottom_1 - 1) * 100 <= bottom_tolerance_pct

SEPARATION_OK:
    bars_between_bottoms >= min_separation_bars

NECKLINE:
    high between bottom_1 and bottom_2

BREAK_OK:
    neckline_break_required = NO
    OR Close[1] >= neckline * (1 + break_buffer_pct / 100)

IF BOTTOMS_MATCH AND SEPARATION_OK AND BREAK_OK:
    DOUBLEBOTTOM_ALLOW = 1
ELSE:
    DOUBLEBOTTOM_ALLOW = 0
```

---

# 6. F070 — double_top_flag

```text
ID: F070
FEATURE: double_top_flag_1m
ACTION: DOUBLETOP_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
DIRECTION: BEARISH
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit |
|---|---:|---:|---:|---:|---|---|
| top_tolerance_pct | float | 0.05 | 1.00 | 0.05 | - | percent |
| min_separation_bars | int | 5 | 60 | 5 | - | bars |
| neckline_break_required | enum | - | - | - | YES / NO | bool |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent |
| max_pattern_age_bars | int | 20 | 240 | 10 | - | bars |

## SIGNAL_RULE

```text
TOPS_MATCH:
    abs(top_2 / top_1 - 1) * 100 <= top_tolerance_pct

SEPARATION_OK:
    bars_between_tops >= min_separation_bars

NECKLINE:
    low between top_1 and top_2

BREAK_OK:
    neckline_break_required = NO
    OR Close[1] <= neckline * (1 - break_buffer_pct / 100)

IF TOPS_MATCH AND SEPARATION_OK AND BREAK_OK:
    DOUBLETOP_ALLOW = 1
ELSE:
    DOUBLETOP_ALLOW = 0
```

---

# 7. F071 — head_shoulders_flag

```text
ID: F071
FEATURE: head_shoulders_flag_1m
ACTION: HEADSHOULDERS_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
DIRECTION: BEARISH
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit |
|---|---:|---:|---:|---:|---|---|
| shoulder_tolerance_pct | float | 0.05 | 1.50 | 0.05 | - | percent |
| head_min_excess_pct | float | 0.10 | 3.00 | 0.10 | - | percent |
| neckline_break_required | enum | - | - | - | YES / NO | bool |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent |
| max_pattern_age_bars | int | 30 | 240 | 10 | - | bars |

## SIGNAL_RULE

```text
SHOULDERS_MATCH:
    abs(right_shoulder / left_shoulder - 1) * 100 <= shoulder_tolerance_pct

HEAD_ABOVE_SHOULDERS:
    head >= max(left_shoulder, right_shoulder) * (1 + head_min_excess_pct / 100)

NECKLINE:
    line through two lows between shoulders and head

BREAK_OK:
    neckline_break_required = NO
    OR Close[1] <= neckline[1] * (1 - break_buffer_pct / 100)

IF SHOULDERS_MATCH AND HEAD_ABOVE_SHOULDERS AND BREAK_OK:
    HEADSHOULDERS_ALLOW = 1
ELSE:
    HEADSHOULDERS_ALLOW = 0
```

---

# 8. F072 — inverse_head_shoulders_flag

```text
ID: F072
FEATURE: inverse_head_shoulders_flag_1m
ACTION: INVHEADSHOULDERS_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
DIRECTION: BULLISH
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit |
|---|---:|---:|---:|---:|---|---|
| shoulder_tolerance_pct | float | 0.05 | 1.50 | 0.05 | - | percent |
| head_min_excess_pct | float | 0.10 | 3.00 | 0.10 | - | percent |
| neckline_break_required | enum | - | - | - | YES / NO | bool |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent |
| max_pattern_age_bars | int | 30 | 240 | 10 | - | bars |

## SIGNAL_RULE

```text
SHOULDERS_MATCH:
    abs(right_shoulder / left_shoulder - 1) * 100 <= shoulder_tolerance_pct

HEAD_BELOW_SHOULDERS:
    head <= min(left_shoulder, right_shoulder) * (1 - head_min_excess_pct / 100)

NECKLINE:
    line through two highs between shoulders and head

BREAK_OK:
    neckline_break_required = NO
    OR Close[1] >= neckline[1] * (1 + break_buffer_pct / 100)

IF SHOULDERS_MATCH AND HEAD_BELOW_SHOULDERS AND BREAK_OK:
    INVHEADSHOULDERS_ALLOW = 1
ELSE:
    INVHEADSHOULDERS_ALLOW = 0
```

---

# 9. F073 — triangle_flag

```text
ID: F073
FEATURE: triangle_flag_1m
ACTION: TRIANGLE_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit |
|---|---:|---:|---:|---:|---|---|
| triangle_type | enum | - | - | - | SYMMETRIC / ASCENDING / DESCENDING | type |
| min_touches | int | 2 | 5 | 1 | - | touches |
| convergence_min_pct | float | 5 | 60 | 5 | - | percent |
| breakout_required | enum | - | - | - | YES / NO | bool |
| break_dir | enum | - | - | - | UP / DOWN / ANY | direction |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent |

## SIGNAL_RULE

```text
TRIANGLE_GEOMETRY:
    upper_boundary from falling/flat highs
    lower_boundary from rising/flat lows
    boundaries converge by at least convergence_min_pct
    touches >= min_touches

BREAK_OK:
    breakout_required = NO
    OR break_dir = UP AND Close[1] >= upper_boundary[1] * (1 + break_buffer_pct / 100)
    OR break_dir = DOWN AND Close[1] <= lower_boundary[1] * (1 - break_buffer_pct / 100)
    OR break_dir = ANY AND breakout either side

IF TRIANGLE_GEOMETRY AND BREAK_OK:
    TRIANGLE_ALLOW = 1
ELSE:
    TRIANGLE_ALLOW = 0
```

---

# 10. F074 — pennant_flag

```text
ID: F074
FEATURE: pennant_flag_1m
ACTION: PENNANT_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit |
|---|---:|---:|---:|---:|---|---|
| impulse_dir | enum | - | - | - | UP / DOWN | direction |
| impulse_min_pct | float | 0.30 | 5.00 | 0.10 | - | percent |
| consolidation_bars | int | 3 | 60 | 1 | - | bars |
| compression_min_pct | float | 5 | 70 | 5 | - | percent |
| breakout_required | enum | - | - | - | YES / NO | bool |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent |

## SIGNAL_RULE

```text
IMPULSE_OK:
    impulse move before consolidation >= impulse_min_pct

PENNANT_COMPRESSION:
    consolidation range compresses by compression_min_pct

BREAK_OK:
    breakout_required = NO
    OR impulse_dir = UP AND Close[1] >= pennant_upper[1] * (1 + break_buffer_pct / 100)
    OR impulse_dir = DOWN AND Close[1] <= pennant_lower[1] * (1 - break_buffer_pct / 100)

IF IMPULSE_OK AND PENNANT_COMPRESSION AND BREAK_OK:
    PENNANT_ALLOW = 1
ELSE:
    PENNANT_ALLOW = 0
```

---

# 11. F075 — wedge_rising_flag

```text
ID: F075
FEATURE: wedge_rising_flag_1m
ACTION: WEDGERISING_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit |
|---|---:|---:|---:|---:|---|---|
| min_touches | int | 2 | 5 | 1 | - | touches |
| convergence_min_pct | float | 5 | 60 | 5 | - | percent |
| breakout_required | enum | - | - | - | YES / NO | bool |
| break_dir | enum | - | - | - | DOWN / UP / ANY | direction |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent |

## SIGNAL_RULE

```text
RISING_WEDGE_GEOMETRY:
    upper_boundary rising
    lower_boundary rising
    lower_boundary slope > upper_boundary slope
    boundaries converge by convergence_min_pct
    touches >= min_touches

BREAK_OK:
    breakout_required = NO
    OR break_dir = DOWN AND Close[1] <= lower_boundary[1] * (1 - break_buffer_pct / 100)
    OR break_dir = UP AND Close[1] >= upper_boundary[1] * (1 + break_buffer_pct / 100)
    OR break_dir = ANY AND breakout either side

IF RISING_WEDGE_GEOMETRY AND BREAK_OK:
    WEDGERISING_ALLOW = 1
ELSE:
    WEDGERISING_ALLOW = 0
```

---

# 12. F076 — wedge_falling_flag

```text
ID: F076
FEATURE: wedge_falling_flag_1m
ACTION: WEDGEFALLING_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit |
|---|---:|---:|---:|---:|---|---|
| min_touches | int | 2 | 5 | 1 | - | touches |
| convergence_min_pct | float | 5 | 60 | 5 | - | percent |
| breakout_required | enum | - | - | - | YES / NO | bool |
| break_dir | enum | - | - | - | UP / DOWN / ANY | direction |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent |

## SIGNAL_RULE

```text
FALLING_WEDGE_GEOMETRY:
    upper_boundary falling
    lower_boundary falling
    upper_boundary slope < lower_boundary slope
    boundaries converge by convergence_min_pct
    touches >= min_touches

BREAK_OK:
    breakout_required = NO
    OR break_dir = UP AND Close[1] >= upper_boundary[1] * (1 + break_buffer_pct / 100)
    OR break_dir = DOWN AND Close[1] <= lower_boundary[1] * (1 - break_buffer_pct / 100)
    OR break_dir = ANY AND breakout either side

IF FALLING_WEDGE_GEOMETRY AND BREAK_OK:
    WEDGEFALLING_ALLOW = 1
ELSE:
    WEDGEFALLING_ALLOW = 0
```

---

# 13. F077 — range_flag

```text
ID: F077
FEATURE: range_flag_1m
ACTION: RANGEFLAG_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit |
|---|---:|---:|---:|---:|---|---|
| range_lookback | int | 20 | 240 | 10 | - | bars |
| max_range_pct | float | 0.10 | 5.00 | 0.10 | - | percent |
| min_touches_high | int | 1 | 5 | 1 | - | touches |
| min_touches_low | int | 1 | 5 | 1 | - | touches |
| range_pos_mode | enum | - | - | - | ANY / LOW / HIGH / MID | position |
| range_pos_level | int | 10 | 90 | 5 | - | percent_position |

## SIGNAL_RULE

```text
range_high = highest(High, range_lookback)
range_low = lowest(Low, range_lookback)
range_size_pct = (range_high / range_low - 1) * 100
range_position = ((Close[1] - range_low) / (range_high - range_low)) * 100

RANGE_GEOMETRY:
    range_size_pct <= max_range_pct
    touches near high >= min_touches_high
    touches near low >= min_touches_low

POSITION_OK:
    range_pos_mode = ANY
    OR range_pos_mode = LOW AND range_position <= range_pos_level
    OR range_pos_mode = HIGH AND range_position >= range_pos_level
    OR range_pos_mode = MID AND abs(range_position - 50) <= range_pos_level

IF RANGE_GEOMETRY AND POSITION_OK:
    RANGEFLAG_ALLOW = 1
ELSE:
    RANGEFLAG_ALLOW = 0
```

---

# 14. CALIBRATION_ORDER

```text
1. F077 range_flag
2. F073 triangle_flag
3. F074 pennant_flag
4. F075 wedge_rising_flag
5. F076 wedge_falling_flag
6. F069 double_bottom_flag
7. F070 double_top_flag
8. F071 head_shoulders_flag
9. F072 inverse_head_shoulders_flag
```

---

# 15. GLOBAL_NOT_CALIBRATED

```text
side
tf
calc_method
price_source
high_low_source
unconfirmed_pivots
pattern_engine
swing_lookback
pivot_left
pivot_right
entry_exit
order_size
take_profit_order
stop_loss_order
```

---

# 16. REGISTRY_ROWS_SHORT

```text
F069 | double_bottom_flag_1m | DOUBLEBOTTOM_ALLOW | CHART_PATTERNS | bottom_tolerance_pct(0.05–1.00 step 0.05),min_separation_bars(5–60 step 5),neckline_break_required(YES/NO),break_buffer_pct(0.00–1.00 step 0.01),max_pattern_age_bars(20–240 step 10) | output 1/0

F070 | double_top_flag_1m | DOUBLETOP_ALLOW | CHART_PATTERNS | top_tolerance_pct(0.05–1.00 step 0.05),min_separation_bars(5–60 step 5),neckline_break_required(YES/NO),break_buffer_pct(0.00–1.00 step 0.01),max_pattern_age_bars(20–240 step 10) | output 1/0

F071 | head_shoulders_flag_1m | HEADSHOULDERS_ALLOW | CHART_PATTERNS | shoulder_tolerance_pct(0.05–1.50 step 0.05),head_min_excess_pct(0.10–3.00 step 0.10),neckline_break_required(YES/NO),break_buffer_pct(0.00–1.00 step 0.01),max_pattern_age_bars(30–240 step 10) | output 1/0

F072 | inverse_head_shoulders_flag_1m | INVHEADSHOULDERS_ALLOW | CHART_PATTERNS | shoulder_tolerance_pct(0.05–1.50 step 0.05),head_min_excess_pct(0.10–3.00 step 0.10),neckline_break_required(YES/NO),break_buffer_pct(0.00–1.00 step 0.01),max_pattern_age_bars(30–240 step 10) | output 1/0

F073 | triangle_flag_1m | TRIANGLE_ALLOW | CHART_PATTERNS | triangle_type(SYMMETRIC/ASCENDING/DESCENDING),min_touches(2–5 step 1),convergence_min_pct(5–60 step 5),breakout_required(YES/NO),break_dir(UP/DOWN/ANY),break_buffer_pct(0.00–1.00 step 0.01) | output 1/0

F074 | pennant_flag_1m | PENNANT_ALLOW | CHART_PATTERNS | impulse_dir(UP/DOWN),impulse_min_pct(0.30–5.00 step 0.10),consolidation_bars(3–60 step 1),compression_min_pct(5–70 step 5),breakout_required(YES/NO),break_buffer_pct(0.00–1.00 step 0.01) | output 1/0

F075 | wedge_rising_flag_1m | WEDGERISING_ALLOW | CHART_PATTERNS | min_touches(2–5 step 1),convergence_min_pct(5–60 step 5),breakout_required(YES/NO),break_dir(DOWN/UP/ANY),break_buffer_pct(0.00–1.00 step 0.01) | output 1/0

F076 | wedge_falling_flag_1m | WEDGEFALLING_ALLOW | CHART_PATTERNS | min_touches(2–5 step 1),convergence_min_pct(5–60 step 5),breakout_required(YES/NO),break_dir(UP/DOWN/ANY),break_buffer_pct(0.00–1.00 step 0.01) | output 1/0

F077 | range_flag_1m | RANGEFLAG_ALLOW | CHART_PATTERNS | range_lookback(20–240 step 10),max_range_pct(0.10–5.00 step 0.10),min_touches_high(1–5 step 1),min_touches_low(1–5 step 1),range_pos_mode(ANY/LOW/HIGH/MID),range_pos_level(10–90 step 5) | output 1/0
```
