# FIBONACCI GRID — STRICT PASSPORT F040-F041 — V3 ANCHOR RULE

```text
FAMILY: FIBONACCI_GRID
FEATURES: F040-F041
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

---

# 1. FIXED_FIB_ANCHOR_ENGINE

```text
FIB_METHOD = auto_pivot_zigzag_retracement
ANCHOR_RULE = last_confirmed_alternating_pivot_pair
MAX_LOOKBACK_BARS = 240
DEPTH_BARS = 10
DEVIATION_PCT = 0.30
PIVOT_SOURCE = High/Low
UPDATE_RULE = update_only_after_new_confirmed_pivot
REPAINT_POLICY = no_unconfirmed_pivot
FIB_DIRECTION = AUTO
```

## COMMENT_ANCHOR_ENGINE

```text
FIXED_FIB_ANCHOR_ENGINE обязателен.
Он не калибруется.

Бот не должен натягивать Fibonacci по случайному максимуму/минимуму каждой минуты.
Бот должен брать последнюю подтверждённую swing-ногу.

DEPTH_BARS = минимальная глубина pivot-структуры.
DEVIATION_PCT = минимальное движение между pivot-точками.
MAX_LOOKBACK_BARS = максимальное окно поиска активной swing-ноги.

Если новый pivot ещё не подтверждён, сетка не меняется.
Рабочей остаётся предыдущая подтверждённая сетка.
```

---

# 2. FIXED_FIB_GRID

```text
FIB_GRID_LEVELS = 0.000 / 0.236 / 0.382 / 0.500 / 0.618 / 0.786 / 1.000
MAIN_LEVELS = 0.382 / 0.618
```

## COMMENT_FIB_GRID

```text
Сетка Fibonacci фиксированная.
В F040-F041 калибруются только дистанции до 0.382 и 0.618.
Остальные уровни передаются как контекст для ML/MQL.
```

---

# 3. ANCHOR_SELECTION_RULE

```text
1. На каждой закрытой 1m-свече обновить список подтверждённых pivots.

2. Pivot High:
   High[pivot] выше локальных High в зоне DEPTH_BARS.

3. Pivot Low:
   Low[pivot] ниже локальных Low в зоне DEPTH_BARS.

4. Новый pivot принимается только если расстояние от предыдущего противоположного pivot >= DEVIATION_PCT.

5. Взять две последние подтверждённые pivot-точки разного типа:
   LOW -> HIGH = up_leg
   HIGH -> LOW = down_leg

6. Если такой пары нет:
   FIB_ALLOW = 0
```

---

# 4. GRID_DIRECTION_RULE

## UP LEG

```text
ANCHOR_A = last_confirmed_swing_low
ANCHOR_B = last_confirmed_swing_high

Fibonacci натягивается:
LOW -> HIGH
```

## DOWN LEG

```text
ANCHOR_A = last_confirmed_swing_high
ANCHOR_B = last_confirmed_swing_low

Fibonacci натягивается:
HIGH -> LOW
```

---

# 5. FIB FORMULAS

## UP LEG

```text
swing_low = ANCHOR_A
swing_high = ANCHOR_B
range = swing_high - swing_low

fib_0000 = swing_high
fib_0236 = swing_high - range * 0.236
fib_0382 = swing_high - range * 0.382
fib_0500 = swing_high - range * 0.500
fib_0618 = swing_high - range * 0.618
fib_0786 = swing_high - range * 0.786
fib_1000 = swing_low
```

## DOWN LEG

```text
swing_high = ANCHOR_A
swing_low = ANCHOR_B
range = swing_high - swing_low

fib_0000 = swing_low
fib_0236 = swing_low + range * 0.236
fib_0382 = swing_low + range * 0.382
fib_0500 = swing_low + range * 0.500
fib_0618 = swing_low + range * 0.618
fib_0786 = swing_low + range * 0.786
fib_1000 = swing_high
```

---

# 6. DISTANCE FORMULAS

```text
fib_0382_distance_pct = (Close[1] / fib_0382 - 1) * 100
fib_0618_distance_pct = (Close[1] / fib_0618 - 1) * 100

fib_0382_abs_distance_pct = abs(fib_0382_distance_pct)
fib_0618_abs_distance_pct = abs(fib_0618_distance_pct)
```

---

# 7. DATA_GUARD

```text
IF no_confirmed_pivot_pair:
    FIB_ALLOW = 0

IF range <= 0:
    FIB_ALLOW = 0

IF fib_level <= 0:
    FIB_ALLOW = 0
```

---

# 8. F040 — fib_0382_distance

```text
ID: F040
FEATURE: fib_0382_distance_1m
ACTION: FIB0382DIST_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
FIB_LEVEL = 0.382
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| signal_mode | enum | - | - | - | SIDE / DISTANCE | mode | yes |
| side_state | enum | - | - | - | ABOVE / BELOW | position | conditional |
| distance_state | enum | - | - | - | NEAR / FAR | distance | conditional |
| dist_thr_pct | float | 0.00 | 3.00 | 0.01 | - | percent | yes |

## SIGNAL_RULE

```text
IF signal_mode = SIDE AND side_state = ABOVE AND fib_0382_distance_pct >= dist_thr_pct:
    FIB0382DIST_ALLOW = 1

ELSE IF signal_mode = SIDE AND side_state = BELOW AND fib_0382_distance_pct <= -dist_thr_pct:
    FIB0382DIST_ALLOW = 1

ELSE IF signal_mode = DISTANCE AND distance_state = NEAR AND fib_0382_abs_distance_pct <= dist_thr_pct:
    FIB0382DIST_ALLOW = 1

ELSE IF signal_mode = DISTANCE AND distance_state = FAR AND fib_0382_abs_distance_pct >= dist_thr_pct:
    FIB0382DIST_ALLOW = 1

ELSE:
    FIB0382DIST_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F040_signal_mode
F040_side_state
F040_distance_state
F040_dist_thr_pct
F040_FIB0382DIST_ALLOW
```

---

# 9. F041 — fib_0618_distance

```text
ID: F041
FEATURE: fib_0618_distance_1m
ACTION: FIB0618DIST_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
FIB_LEVEL = 0.618
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| signal_mode | enum | - | - | - | SIDE / DISTANCE | mode | yes |
| side_state | enum | - | - | - | ABOVE / BELOW | position | conditional |
| distance_state | enum | - | - | - | NEAR / FAR | distance | conditional |
| dist_thr_pct | float | 0.00 | 3.00 | 0.01 | - | percent | yes |

## SIGNAL_RULE

```text
IF signal_mode = SIDE AND side_state = ABOVE AND fib_0618_distance_pct >= dist_thr_pct:
    FIB0618DIST_ALLOW = 1

ELSE IF signal_mode = SIDE AND side_state = BELOW AND fib_0618_distance_pct <= -dist_thr_pct:
    FIB0618DIST_ALLOW = 1

ELSE IF signal_mode = DISTANCE AND distance_state = NEAR AND fib_0618_abs_distance_pct <= dist_thr_pct:
    FIB0618DIST_ALLOW = 1

ELSE IF signal_mode = DISTANCE AND distance_state = FAR AND fib_0618_abs_distance_pct >= dist_thr_pct:
    FIB0618DIST_ALLOW = 1

ELSE:
    FIB0618DIST_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F041_signal_mode
F041_side_state
F041_distance_state
F041_dist_thr_pct
F041_FIB0618DIST_ALLOW
```

---

# 10. OPTIONAL GRID CONTEXT FOR ML/MQL

```text
FIB_GRID_CONTEXT = ON
```

## RUNTIME_GRID_LEVELS

```text
fib_0000
fib_0236
fib_0382
fib_0500
fib_0618
fib_0786
fib_1000
fib_direction
anchor_a_price
anchor_b_price
anchor_a_bar
anchor_b_bar
```

---

# 11. CALIBRATION_OUTPUT_TO_RUNTIME

```text
F040_signal_mode
F040_side_state
F040_distance_state
F040_dist_thr_pct

F041_signal_mode
F041_side_state
F041_distance_state
F041_dist_thr_pct
```

---

# 12. GLOBAL_NOT_CALIBRATED

```text
side
tf
calc_method
price_source
high_low_source
fib_method
anchor_rule
max_lookback_bars
depth_bars
deviation_pct
pivot_source
update_rule
repaint_policy
fib_direction
fib_grid_levels
main_levels
entry_exit
order_size
stop_loss
take_profit
```

---

# 13. REGISTRY_ROWS_SHORT

```text
F040 | fib_0382_distance_1m | FIB0382DIST_ALLOW | FIBONACCI_GRID | signal_mode(SIDE/DISTANCE),side_state(ABOVE/BELOW),distance_state(NEAR/FAR),dist_thr_pct(0.00–3.00 step 0.01) | fixed: ANCHOR=last_confirmed_pivot_pair,LOOKBACK=240,DEPTH=10,DEVIATION=0.30,FIB_LEVEL=0.382,CLOSE_BAR | output 1/0

F041 | fib_0618_distance_1m | FIB0618DIST_ALLOW | FIBONACCI_GRID | signal_mode(SIDE/DISTANCE),side_state(ABOVE/BELOW),distance_state(NEAR/FAR),dist_thr_pct(0.00–3.00 step 0.01) | fixed: ANCHOR=last_confirmed_pivot_pair,LOOKBACK=240,DEPTH=10,DEVIATION=0.30,FIB_LEVEL=0.618,CLOSE_BAR | output 1/0
```
