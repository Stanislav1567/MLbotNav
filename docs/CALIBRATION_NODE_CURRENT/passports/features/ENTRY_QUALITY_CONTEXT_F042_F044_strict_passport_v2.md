# ENTRY QUALITY CONTEXT — STRICT PASSPORT F042-F044 — V2

```text
FAMILY: ENTRY_QUALITY_CONTEXT
FEATURES: F042-F044
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F042-F044 проверяют качество входа ДО открытия сделки.

Этот блок НЕ закрывает сделку.
Этот блок НЕ ставит TP.
Этот блок НЕ ставит SL.

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
ENTRY_REF_PRICE = Close[1]
TRADE_SIDE_SOURCE = external_profile
TRADE_SIDE = LONG / SHORT
```

## COMMENT_COMMON_FIXED

```text
TRADE_SIDE не калибруется внутри F042-F044.

Оптумно отдельно калибрует LONG и SHORT:
LONG-profile  -> TRADE_SIDE = LONG
SHORT-profile -> TRADE_SIDE = SHORT
```

---

# 2. CONTEXT_LEVEL_SOURCE_MODE

```text
LEVEL_SOURCE_MODE:
    SWING_LEVELS
    DENSITY_VPOC
    FIBONACCI_GRID
```

## COMMENT_LEVEL_SOURCE_MODE

```text
LEVEL_SOURCE_MODE выбирает, от каких уровней считать TP/SL-контекст.

SWING_LEVELS:
    уровни поддержки/сопротивления из swing-pivot engine.

DENSITY_VPOC:
    уровни объёмной плотности / VPOC из блока F025-F034.

FIBONACCI_GRID:
    уровни Fibonacci из блока F040-F041.

LEVEL_SOURCE_MODE калибруется.
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
Движки уровней не калибруются внутри F042-F044.
Они должны совпадать с уже созданными паспортами:
F025-F034 = Density/VPOC
F035-F039 = Levels/Range/Channel
F040-F041 = Fibonacci
```

---

# 4. TP_SL_LEVEL_SELECTION

## 4.1 CANDIDATE_LEVELS

```text
IF LEVEL_SOURCE_MODE = SWING_LEVELS:
    candidate_levels = active_support_levels + active_resistance_levels

IF LEVEL_SOURCE_MODE = DENSITY_VPOC:
    candidate_levels = vpoc_60 + vpoc_240

IF LEVEL_SOURCE_MODE = FIBONACCI_GRID:
    candidate_levels = fib_0236 + fib_0382 + fib_0500 + fib_0618 + fib_0786
```

## 4.2 LONG

```text
IF TRADE_SIDE = LONG:
    tp_level = nearest candidate_level above ENTRY_REF_PRICE
    sl_level = nearest candidate_level below ENTRY_REF_PRICE
```

## 4.3 SHORT

```text
IF TRADE_SIDE = SHORT:
    tp_level = nearest candidate_level below ENTRY_REF_PRICE
    sl_level = nearest candidate_level above ENTRY_REF_PRICE
```

## 4.4 FALLBACK

```text
IF no tp_level:
    TPCONTEXT_ALLOW = 0

IF no sl_level:
    SLCONTEXT_ALLOW = 0

IF no tp_level OR no sl_level:
    RRCONTEXT_ALLOW = 0
```

---

# 5. CONTEXT_FORMULAS

## LONG

```text
IF TRADE_SIDE = LONG:
    tp_context_distance_pct = (tp_level / ENTRY_REF_PRICE - 1) * 100
    sl_context_distance_pct = (ENTRY_REF_PRICE / sl_level - 1) * 100
```

## SHORT

```text
IF TRADE_SIDE = SHORT:
    tp_context_distance_pct = (ENTRY_REF_PRICE / tp_level - 1) * 100
    sl_context_distance_pct = (sl_level / ENTRY_REF_PRICE - 1) * 100
```

## RR

```text
rr_context_estimate = tp_context_distance_pct / sl_context_distance_pct
```

---

# 6. DATA_GUARD

```text
IF ENTRY_REF_PRICE <= 0:
    ALL_ALLOW = 0

IF tp_level <= 0:
    TPCONTEXT_ALLOW = 0

IF sl_level <= 0:
    SLCONTEXT_ALLOW = 0

IF tp_context_distance_pct <= 0:
    TPCONTEXT_ALLOW = 0

IF sl_context_distance_pct <= 0:
    SLCONTEXT_ALLOW = 0

IF sl_context_distance_pct <= 0:
    RRCONTEXT_ALLOW = 0
```

---

# 7. F042 — tp_context_distance

```text
ID: F042
FEATURE: tp_context_distance_1m
ACTION: TPCONTEXT_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Проверяет, есть ли достаточно места до потенциальной цели перед входом.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| level_source_mode | enum | - | - | - | SWING_LEVELS / DENSITY_VPOC / FIBONACCI_GRID | source | yes |
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| tp_dist_thr_pct | float | 0.05 | 5.00 | 0.05 | - | percent | yes |

## PARAM_MEANING

```text
cmp = GREATER:
    вход разрешён, если до TP достаточно места

cmp = LESS:
    вход разрешён, если TP близко
```

## SIGNAL_RULE

```text
IF cmp = GREATER AND tp_context_distance_pct >= tp_dist_thr_pct:
    TPCONTEXT_ALLOW = 1

ELSE IF cmp = LESS AND tp_context_distance_pct <= tp_dist_thr_pct:
    TPCONTEXT_ALLOW = 1

ELSE:
    TPCONTEXT_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F042_level_source_mode
F042_cmp
F042_tp_dist_thr_pct
F042_TPCONTEXT_ALLOW
```

## REGISTRY_ROW

```text
F042 | tp_context_distance_1m | TPCONTEXT_ALLOW | ENTRY_QUALITY_CONTEXT | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),cmp(GREATER/LESS),tp_dist_thr_pct(0.05–5.00 step 0.05) | output 1/0
```

---

# 8. F043 — sl_context_distance

```text
ID: F043
FEATURE: sl_context_distance_1m
ACTION: SLCONTEXT_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Проверяет расстояние до зоны риска / инвалидирования идеи перед входом.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| level_source_mode | enum | - | - | - | SWING_LEVELS / DENSITY_VPOC / FIBONACCI_GRID | source | yes |
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| sl_dist_thr_pct | float | 0.05 | 5.00 | 0.05 | - | percent | yes |

## PARAM_MEANING

```text
cmp = GREATER:
    вход разрешён, если стоп-зона далеко

cmp = LESS:
    вход разрешён, если риск до стоп-зоны не больше заданного порога
```

## SIGNAL_RULE

```text
IF cmp = GREATER AND sl_context_distance_pct >= sl_dist_thr_pct:
    SLCONTEXT_ALLOW = 1

ELSE IF cmp = LESS AND sl_context_distance_pct <= sl_dist_thr_pct:
    SLCONTEXT_ALLOW = 1

ELSE:
    SLCONTEXT_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F043_level_source_mode
F043_cmp
F043_sl_dist_thr_pct
F043_SLCONTEXT_ALLOW
```

## REGISTRY_ROW

```text
F043 | sl_context_distance_1m | SLCONTEXT_ALLOW | ENTRY_QUALITY_CONTEXT | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),cmp(GREATER/LESS),sl_dist_thr_pct(0.05–5.00 step 0.05) | output 1/0
```

---

# 9. F044 — rr_context_estimate

```text
ID: F044
FEATURE: rr_context_estimate_1m
ACTION: RRCONTEXT_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Проверяет предварительное соотношение потенциальной цели к потенциальному риску.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| level_source_mode | enum | - | - | - | SWING_LEVELS / DENSITY_VPOC / FIBONACCI_GRID | source | yes |
| rr_state | enum | - | - | - | GOOD / POOR | rr_state | yes |
| rr_level | float | 0.50 | 5.00 | 0.10 | - | ratio | yes |

## PARAM_MEANING

```text
rr_state = GOOD:
    вход разрешён, если RR не ниже порога

rr_state = POOR:
    вход разрешён, если RR не выше порога
```

## SIGNAL_RULE

```text
IF rr_state = GOOD AND rr_context_estimate >= rr_level:
    RRCONTEXT_ALLOW = 1

ELSE IF rr_state = POOR AND rr_context_estimate <= rr_level:
    RRCONTEXT_ALLOW = 1

ELSE:
    RRCONTEXT_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F044_level_source_mode
F044_rr_state
F044_rr_level
F044_RRCONTEXT_ALLOW
```

## REGISTRY_ROW

```text
F044 | rr_context_estimate_1m | RRCONTEXT_ALLOW | ENTRY_QUALITY_CONTEXT | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),rr_state(GOOD/POOR),rr_level(0.50–5.00 step 0.10) | output 1/0
```

---

# 10. CALIBRATION_ORDER

```text
1. F044 rr_context_estimate
2. F042 tp_context_distance
3. F043 sl_context_distance
```

## COMMENT_CALIBRATION_ORDER

```text
Начинать лучше с F044, потому что RR сразу объединяет потенциальную цель и риск.
Потом отдельно тестировать F042 и F043.
```

---

# 11. GLOBAL_NOT_CALIBRATED

```text
trade_side
tf
calc_method
entry_ref_price
level_engines
swing_level_engine_params
density_vpoc_engine_params
fibonacci_grid_engine_params
entry_exit
order_size
take_profit_order
stop_loss_order
```

---

# 12. REGISTRY_ROWS_SHORT

```text
F042 | tp_context_distance_1m | TPCONTEXT_ALLOW | ENTRY_QUALITY_CONTEXT | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),cmp(GREATER/LESS),tp_dist_thr_pct(0.05–5.00 step 0.05) | output 1/0

F043 | sl_context_distance_1m | SLCONTEXT_ALLOW | ENTRY_QUALITY_CONTEXT | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),cmp(GREATER/LESS),sl_dist_thr_pct(0.05–5.00 step 0.05) | output 1/0

F044 | rr_context_estimate_1m | RRCONTEXT_ALLOW | ENTRY_QUALITY_CONTEXT | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID),rr_state(GOOD/POOR),rr_level(0.50–5.00 step 0.10) | output 1/0
```
