# BREAKOUT / RETEST — STRICT PASSPORT F045-F049 — V1

```text
FAMILY: BREAKOUT_RETEST
FEATURES: F045-F049
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F045-F049 проверяют рыночные события перед входом:

F045 = подтверждённый пробой уровня
F046 = ложный пробой уровня
F047 = ретест пробитого уровня
F048 = пробой swing high
F049 = пробой swing low

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
PRICE_SOURCE = Close
HIGH_LOW_SOURCE = High/Low
TRADE_SIDE_SOURCE = external_profile
TRADE_SIDE = LONG / SHORT
```

## COMMENT_COMMON_FIXED

```text
Все события считаются только по закрытой 1m-свече.

TRADE_SIDE не калибруется внутри F045-F049.
Оптумно отдельно калибрует LONG и SHORT.
Внутри этого блока TRADE_SIDE приходит из внешнего режима.
```

---

# 2. LEVEL_SOURCE_MODE

```text
LEVEL_SOURCE_MODE:
    SWING_LEVELS
    DENSITY_VPOC
    FIBONACCI_GRID
```

## COMMENT_LEVEL_SOURCE_MODE

```text
LEVEL_SOURCE_MODE выбирает, какие уровни используются для пробоя/ретеста.

SWING_LEVELS:
    уровни поддержки/сопротивления из блока F035-F039.

DENSITY_VPOC:
    уровни объёмной плотности / VPOC из блока F025-F034.

FIBONACCI_GRID:
    уровни Fibonacci из блока F040-F041.
```

---

# 3. FIXED_LEVEL_ENGINES

## 3.1 SWING_LEVELS_ENGINE

```text
SWING_LEVEL_METHOD = swing_pivot_levels
LEVEL_LOOKBACK = 240
PIVOT_LEFT = 3
PIVOT_RIGHT = 3
MERGE_TOLERANCE_PCT = 0.15
TOUCH_TOLERANCE_PCT = 0.10
MIN_TOUCHES = 2
LEVEL_SOURCE = High/Low
LEVEL_UPDATE = every_closed_bar
```

## 3.2 DENSITY_VPOC_ENGINE

```text
DENSITY_SOURCE_BLOCK = F025-F034
PROFILE_METHOD = rolling_volume_by_price_bins
BIN_STEP_PCT = 0.05
CLUSTER_RADIUS_BINS = 1
VPOC_RULE = max_volume_bin
DENSITY_LEVELS = vpoc_60 / vpoc_240
```

## 3.3 FIBONACCI_GRID_ENGINE

```text
FIB_SOURCE_BLOCK = F040-F041
FIB_METHOD = auto_pivot_zigzag_retracement
ANCHOR_RULE = last_confirmed_alternating_pivot_pair
MAX_LOOKBACK_BARS = 240
DEPTH_BARS = 10
DEVIATION_PCT = 0.30
FIB_GRID_LEVELS = 0.236 / 0.382 / 0.500 / 0.618 / 0.786
```

## COMMENT_FIXED_LEVEL_ENGINES

```text
Движки уровней не калибруются внутри F045-F049.
Они должны совпадать с паспортами:
F025-F034 = Density/VPOC
F035-F039 = Levels/Range/Channel
F040-F041 = Fibonacci
```

---

# 4. EVENT_STATE_ENGINE

```text
EVENT_STATE = ON
BROKEN_LEVEL_MEMORY = ON
MAX_EVENT_AGE_BARS = 60
RETEST_EVENT_MEMORY = ON
```

## COMMENT_EVENT_STATE_ENGINE

```text
F047 retest_flag требует памяти события пробоя.

После F045 breakout_flag runtime сохраняет:
broken_level
break_dir
break_bar
level_source_mode

F047 ищет ретест этого broken_level в заданном окне.
Если пробоя в памяти нет, F047 = 0.
```

---

# 5. CANDIDATE LEVEL SELECTION

```text
IF LEVEL_SOURCE_MODE = SWING_LEVELS:
    candidate_levels = active_support_levels + active_resistance_levels

IF LEVEL_SOURCE_MODE = DENSITY_VPOC:
    candidate_levels = vpoc_60 + vpoc_240

IF LEVEL_SOURCE_MODE = FIBONACCI_GRID:
    candidate_levels = fib_0236 + fib_0382 + fib_0500 + fib_0618 + fib_0786
```

## LEVEL SELECTION FOR BREAK

```text
BREAK_UP:
    target_level = nearest candidate_level above or touched by Close[2]

BREAK_DOWN:
    target_level = nearest candidate_level below or touched by Close[2]
```

## DATA_GUARD_LEVEL

```text
IF no target_level:
    ALLOW = 0

IF target_level <= 0:
    ALLOW = 0
```

---

# 6. F045 — breakout_flag

```text
ID: F045
FEATURE: breakout_flag_1m
ACTION: BREAKOUT_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход при подтверждённом закрытии цены за уровнем.
```

## FIXED

```text
BREAK_CONFIRMATION_TYPE = close_beyond_level
WICK_ONLY_BREAK = not_allowed
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| level_source_mode | enum | - | - | - | SWING_LEVELS / DENSITY_VPOC / FIBONACCI_GRID | source | yes |
| break_dir | enum | - | - | - | UP / DOWN | direction | yes |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent | yes |
| confirm_bars | int | 1 | 3 | 1 | - | bars | yes |

## SIGNAL_RULE

```text
BREAK_UP_CONDITION:
    Close[1] >= target_level * (1 + break_buffer_pct / 100)

BREAK_DOWN_CONDITION:
    Close[1] <= target_level * (1 - break_buffer_pct / 100)

CONFIRM_UP:
    last confirm_bars closes are above target_level with buffer

CONFIRM_DOWN:
    last confirm_bars closes are below target_level with buffer

IF break_dir = UP AND CONFIRM_UP:
    BREAKOUT_ALLOW = 1
    save broken_level event

ELSE IF break_dir = DOWN AND CONFIRM_DOWN:
    BREAKOUT_ALLOW = 1
    save broken_level event

ELSE:
    BREAKOUT_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F045_level_source_mode
F045_break_dir
F045_break_buffer_pct
F045_confirm_bars
F045_BREAKOUT_ALLOW
```

## REGISTRY_ROW

```text
F045 | breakout_flag_1m | BREAKOUT_ALLOW | BREAKOUT_RETEST | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),break_dir(UP/DOWN),break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1) | output 1/0
```

---

# 7. F046 — false_breakout_flag

```text
ID: F046
FEATURE: false_breakout_flag_1m
ACTION: FALSEBREAK_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход при ложном пробое: цена пробила уровень, но вернулась обратно.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| level_source_mode | enum | - | - | - | SWING_LEVELS / DENSITY_VPOC / FIBONACCI_GRID | source | yes |
| break_dir | enum | - | - | - | UP / DOWN | direction | yes |
| false_mode | enum | - | - | - | WICK_REJECT / CLOSE_RETURN | false_type | yes |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent | yes |
| return_window_bars | int | 1 | 10 | 1 | - | bars | conditional |
| return_tolerance_pct | float | 0.00 | 0.30 | 0.01 | - | percent | yes |

## SIGNAL_RULE

```text
WICK_REJECT_UP:
    High[1] >= target_level * (1 + break_buffer_pct / 100)
    AND Close[1] <= target_level * (1 + return_tolerance_pct / 100)

WICK_REJECT_DOWN:
    Low[1] <= target_level * (1 - break_buffer_pct / 100)
    AND Close[1] >= target_level * (1 - return_tolerance_pct / 100)

CLOSE_RETURN_UP:
    price closed above target_level with buffer within return_window_bars
    AND Close[1] <= target_level * (1 + return_tolerance_pct / 100)

CLOSE_RETURN_DOWN:
    price closed below target_level with buffer within return_window_bars
    AND Close[1] >= target_level * (1 - return_tolerance_pct / 100)

IF break_dir = UP AND false_mode = WICK_REJECT AND WICK_REJECT_UP:
    FALSEBREAK_ALLOW = 1

ELSE IF break_dir = DOWN AND false_mode = WICK_REJECT AND WICK_REJECT_DOWN:
    FALSEBREAK_ALLOW = 1

ELSE IF break_dir = UP AND false_mode = CLOSE_RETURN AND CLOSE_RETURN_UP:
    FALSEBREAK_ALLOW = 1

ELSE IF break_dir = DOWN AND false_mode = CLOSE_RETURN AND CLOSE_RETURN_DOWN:
    FALSEBREAK_ALLOW = 1

ELSE:
    FALSEBREAK_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F046_level_source_mode
F046_break_dir
F046_false_mode
F046_break_buffer_pct
F046_return_window_bars
F046_return_tolerance_pct
F046_FALSEBREAK_ALLOW
```

## REGISTRY_ROW

```text
F046 | false_breakout_flag_1m | FALSEBREAK_ALLOW | BREAKOUT_RETEST | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),break_dir(UP/DOWN),false_mode(WICK_REJECT/CLOSE_RETURN),break_buffer_pct(0.00–1.00 step 0.01),return_window_bars(1–10 step 1),return_tolerance_pct(0.00–0.30 step 0.01) | output 1/0
```

---

# 8. F047 — retest_flag

```text
ID: F047
FEATURE: retest_flag_1m
ACTION: RETEST_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход после пробоя и возврата цены к пробитому уровню с подтверждением реакции.
```

## DEPENDENCY

```text
Requires recent breakout event from F045 or internal breakout memory.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| level_source_mode | enum | - | - | - | SWING_LEVELS / DENSITY_VPOC / FIBONACCI_GRID | source | yes |
| break_dir | enum | - | - | - | UP / DOWN | direction | yes |
| retest_window_bars | int | 1 | 30 | 1 | - | bars | yes |
| retest_tolerance_pct | float | 0.00 | 0.50 | 0.01 | - | percent | yes |
| reaction_confirm_pct | float | 0.00 | 1.00 | 0.01 | - | percent | yes |

## SIGNAL_RULE

```text
VALID_BREAK_MEMORY:
    broken_level exists
    AND broken_level age <= retest_window_bars
    AND saved break_dir = current break_dir
    AND saved level_source_mode = current level_source_mode

RETEST_UP:
    Low[1] <= broken_level * (1 + retest_tolerance_pct / 100)
    AND Close[1] >= broken_level * (1 + reaction_confirm_pct / 100)

RETEST_DOWN:
    High[1] >= broken_level * (1 - retest_tolerance_pct / 100)
    AND Close[1] <= broken_level * (1 - reaction_confirm_pct / 100)

IF break_dir = UP AND VALID_BREAK_MEMORY AND RETEST_UP:
    RETEST_ALLOW = 1

ELSE IF break_dir = DOWN AND VALID_BREAK_MEMORY AND RETEST_DOWN:
    RETEST_ALLOW = 1

ELSE:
    RETEST_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F047_level_source_mode
F047_break_dir
F047_retest_window_bars
F047_retest_tolerance_pct
F047_reaction_confirm_pct
F047_RETEST_ALLOW
```

## REGISTRY_ROW

```text
F047 | retest_flag_1m | RETEST_ALLOW | BREAKOUT_RETEST | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),break_dir(UP/DOWN),retest_window_bars(1–30 step 1),retest_tolerance_pct(0.00–0.50 step 0.01),reaction_confirm_pct(0.00–1.00 step 0.01) | output 1/0
```

---

# 9. F048 — swing_high_break_flag

```text
ID: F048
FEATURE: swing_high_break_flag_1m
ACTION: SWINGHIGHBREAK_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход при пробое последнего подтверждённого swing high.
```

## FIXED

```text
SWING_SOURCE = confirmed_pivots
SWING_LOOKBACK = 240
PIVOT_LEFT = 3
PIVOT_RIGHT = 3
BREAK_DIR = UP
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent | yes |
| confirm_bars | int | 1 | 3 | 1 | - | bars | yes |

## SIGNAL_RULE

```text
last_swing_high = last confirmed swing high

IF no last_swing_high:
    SWINGHIGHBREAK_ALLOW = 0

ELSE IF last confirm_bars closes >= last_swing_high * (1 + break_buffer_pct / 100):
    SWINGHIGHBREAK_ALLOW = 1

ELSE:
    SWINGHIGHBREAK_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F048_break_buffer_pct
F048_confirm_bars
F048_SWINGHIGHBREAK_ALLOW
```

## REGISTRY_ROW

```text
F048 | swing_high_break_flag_1m | SWINGHIGHBREAK_ALLOW | BREAKOUT_RETEST | break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1) | fixed: SWING_LOOKBACK=240,PIVOT=3/3,BREAK_DIR=UP,CLOSE_BAR | output 1/0
```

---

# 10. F049 — swing_low_break_flag

```text
ID: F049
FEATURE: swing_low_break_flag_1m
ACTION: SWINGLOWBREAK_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход при пробое последнего подтверждённого swing low.
```

## FIXED

```text
SWING_SOURCE = confirmed_pivots
SWING_LOOKBACK = 240
PIVOT_LEFT = 3
PIVOT_RIGHT = 3
BREAK_DIR = DOWN
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent | yes |
| confirm_bars | int | 1 | 3 | 1 | - | bars | yes |

## SIGNAL_RULE

```text
last_swing_low = last confirmed swing low

IF no last_swing_low:
    SWINGLOWBREAK_ALLOW = 0

ELSE IF last confirm_bars closes <= last_swing_low * (1 - break_buffer_pct / 100):
    SWINGLOWBREAK_ALLOW = 1

ELSE:
    SWINGLOWBREAK_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F049_break_buffer_pct
F049_confirm_bars
F049_SWINGLOWBREAK_ALLOW
```

## REGISTRY_ROW

```text
F049 | swing_low_break_flag_1m | SWINGLOWBREAK_ALLOW | BREAKOUT_RETEST | break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1) | fixed: SWING_LOOKBACK=240,PIVOT=3/3,BREAK_DIR=DOWN,CLOSE_BAR | output 1/0
```

---

# 11. CALIBRATION_ORDER

```text
1. F048 swing_high_break_flag
2. F049 swing_low_break_flag
3. F045 breakout_flag
4. F047 retest_flag
5. F046 false_breakout_flag
```

## COMMENT_CALIBRATION_ORDER

```text
Сначала проверять простые swing-break события F048/F049.
Потом общий breakout по разным источникам уровней F045.
Потом retest F047, потому что он зависит от события breakout.
Последним false_breakout F046, потому что это контртрендовая/отбойная логика.
```

---

# 12. GLOBAL_NOT_CALIBRATED

```text
trade_side
tf
calc_method
price_source
high_low_source
level_engines
swing_level_engine_params
density_vpoc_engine_params
fibonacci_grid_engine_params
event_memory_engine
entry_exit
order_size
take_profit_order
stop_loss_order
```

---

# 13. REGISTRY_ROWS_SHORT

```text
F045 | breakout_flag_1m | BREAKOUT_ALLOW | BREAKOUT_RETEST | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),break_dir(UP/DOWN),break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1) | output 1/0

F046 | false_breakout_flag_1m | FALSEBREAK_ALLOW | BREAKOUT_RETEST | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),break_dir(UP/DOWN),false_mode(WICK_REJECT/CLOSE_RETURN),break_buffer_pct(0.00–1.00 step 0.01),return_window_bars(1–10 step 1),return_tolerance_pct(0.00–0.30 step 0.01) | output 1/0

F047 | retest_flag_1m | RETEST_ALLOW | BREAKOUT_RETEST | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),break_dir(UP/DOWN),retest_window_bars(1–30 step 1),retest_tolerance_pct(0.00–0.50 step 0.01),reaction_confirm_pct(0.00–1.00 step 0.01) | output 1/0

F048 | swing_high_break_flag_1m | SWINGHIGHBREAK_ALLOW | BREAKOUT_RETEST | break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1) | fixed: BREAK_DIR=UP | output 1/0

F049 | swing_low_break_flag_1m | SWINGLOWBREAK_ALLOW | BREAKOUT_RETEST | break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1) | fixed: BREAK_DIR=DOWN | output 1/0
```
