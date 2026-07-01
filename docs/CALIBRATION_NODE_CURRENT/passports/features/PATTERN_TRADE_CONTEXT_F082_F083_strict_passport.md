# PATTERN TRADE CONTEXT — STRICT PASSPORT F082-F083 — V1

```text
FAMILY: PATTERN_TRADE_CONTEXT
FEATURES: F082-F083
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F082-F083 проверяют торговый контекст уже найденного pattern_event.

F082 = проверка SL-зоны паттерна с буфером
F083 = проверка TP-лесенки паттерна

Блок НЕ открывает сделку сам.
Блок НЕ закрывает сделку.
Блок НЕ выставляет реальный SL.
Блок НЕ выставляет реальный TP.

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
PATTERN_MEMORY = ON
TRADE_SIDE_SOURCE = external_profile
TRADE_SIDE = LONG / SHORT
CUSTOM_CALC = YES
```

## COMMENT_COMMON_FIXED

```text
TRADE_SIDE не калибруется внутри F082-F083.

Оптумно отдельно калибрует LONG и SHORT:
LONG-profile  -> TRADE_SIDE = LONG
SHORT-profile -> TRADE_SIDE = SHORT

F082-F083 используют уже найденный pattern_event.
Если pattern_event нет:
F082 = 0
F083 = 0
```

---

# 2. INPUT_BLOCKS

```text
PATTERN_DETECTION:
    F053-F060 = CANDLE_PATTERNS
    F061-F066 = DIVERGENCE_PATTERNS
    F069-F077 = CHART_PATTERNS

PATTERN_QUALITY:
    F067-F068

PATTERN_CONFIRMATION:
    F078-F079

ENTRY_CONTEXT:
    F042-F044

LEVELS:
    F025-F034 = DENSITY/VPOC
    F035-F039 = LEVEL/RANGE/CHANNEL
    F040-F041 = FIBONACCI
    F024 = VWAP
```

---

# 3. PATTERN_EVENT_FIELDS

```text
pattern_id
pattern_family
pattern_direction
pattern_bar
pattern_price
pattern_high
pattern_low
pattern_mid
pattern_range_pct
pattern_neckline
pattern_breakout_level
pattern_target_level
pattern_invalid_level
source_feature_id
```

## DATA_GUARD_PATTERN_EVENT

```text
IF no active pattern_event:
    PATTERNSLBUF_ALLOW = 0
    PATTERNTPLADDER_ALLOW = 0

IF ENTRY_REF_PRICE <= 0:
    PATTERNSLBUF_ALLOW = 0
    PATTERNTPLADDER_ALLOW = 0
```

---

# 4. PATTERN INVALIDATION ENGINE

```text
INVALIDATION_ENGINE = pattern_based_invalidation
```

## LONG INVALIDATION

```text
IF TRADE_SIDE = LONG:
    PATTERN_EXTREME_INVALID = pattern_low
    STRUCTURE_INVALID = nearest_support_below_ENTRY_REF_PRICE
    LEVEL_INVALID = nearest_valid_level_below_ENTRY_REF_PRICE
```

## SHORT INVALIDATION

```text
IF TRADE_SIDE = SHORT:
    PATTERN_EXTREME_INVALID = pattern_high
    STRUCTURE_INVALID = nearest_resistance_above_ENTRY_REF_PRICE
    LEVEL_INVALID = nearest_valid_level_above_ENTRY_REF_PRICE
```

## INVALIDATION SOURCE OPTIONS

```text
sl_anchor_mode:
    PATTERN_EXTREME
    STRUCTURE_LEVEL
    NEAREST_VALID_LEVEL
```

## DATA_GUARD_INVALIDATION

```text
IF selected invalidation_level <= 0:
    PATTERNSLBUF_ALLOW = 0
```

---

# 5. SL BUFFER ENGINE

```text
buffer_mode:
    PCT
    ATR14
    PATTERN_RANGE
```

## BUFFER FORMULAS

```text
IF buffer_mode = PCT:
    sl_buffer_pct = buffer_pct

IF buffer_mode = ATR14:
    sl_buffer_pct = atr14_pct * atr_mult

IF buffer_mode = PATTERN_RANGE:
    sl_buffer_pct = pattern_range_pct * range_mult
```

## LONG SL WITH BUFFER

```text
IF TRADE_SIDE = LONG:
    sl_with_buffer = invalidation_level * (1 - sl_buffer_pct / 100)
    sl_buffer_distance_pct = (ENTRY_REF_PRICE / sl_with_buffer - 1) * 100
```

## SHORT SL WITH BUFFER

```text
IF TRADE_SIDE = SHORT:
    sl_with_buffer = invalidation_level * (1 + sl_buffer_pct / 100)
    sl_buffer_distance_pct = (sl_with_buffer / ENTRY_REF_PRICE - 1) * 100
```

## DATA_GUARD_SL_BUFFER

```text
IF sl_with_buffer <= 0:
    PATTERNSLBUF_ALLOW = 0

IF sl_buffer_distance_pct <= 0:
    PATTERNSLBUF_ALLOW = 0
```

---

# 6. F082 — pattern_sl_buffer_distance

```text
ID: F082
FEATURE: pattern_sl_buffer_distance_1m
ACTION: PATTERNSLBUF_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Проверяет, подходит ли расстояние до SL-зоны паттерна с буфером перед входом.
Это проверка качества входа, а не выставление реального stop loss.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| sl_anchor_mode | enum | - | - | - | PATTERN_EXTREME / STRUCTURE_LEVEL / NEAREST_VALID_LEVEL | anchor | yes |
| buffer_mode | enum | - | - | - | PCT / ATR14 / PATTERN_RANGE | buffer | yes |
| buffer_pct | float | 0.00 | 1.00 | 0.02 | - | percent | conditional |
| atr_mult | float | 0.2 | 3.0 | 0.1 | - | multiplier | conditional |
| range_mult | float | 0.1 | 1.0 | 0.1 | - | multiplier | conditional |
| sl_distance_mode | enum | - | - | - | MAX_RISK / MIN_DISTANCE / BAND | mode | yes |
| min_sl_dist_pct | float | 0.02 | 2.00 | 0.02 | - | percent | conditional |
| max_sl_dist_pct | float | 0.05 | 5.00 | 0.05 | - | percent | conditional |

## PARAM_MEANING

```text
sl_anchor_mode:
    от какой точки считать зону инвалидирования паттерна

buffer_mode:
    каким способом добавлять запас к SL-зоне

sl_distance_mode = MAX_RISK:
    вход разрешён, если риск до SL не больше max_sl_dist_pct

sl_distance_mode = MIN_DISTANCE:
    вход разрешён, если SL не слишком близко, то есть distance >= min_sl_dist_pct

sl_distance_mode = BAND:
    вход разрешён, если distance находится между min_sl_dist_pct и max_sl_dist_pct
```

## SIGNAL_RULE

```text
IF sl_distance_mode = MAX_RISK
   AND sl_buffer_distance_pct <= max_sl_dist_pct:
    PATTERNSLBUF_ALLOW = 1

ELSE IF sl_distance_mode = MIN_DISTANCE
   AND sl_buffer_distance_pct >= min_sl_dist_pct:
    PATTERNSLBUF_ALLOW = 1

ELSE IF sl_distance_mode = BAND
   AND sl_buffer_distance_pct >= min_sl_dist_pct
   AND sl_buffer_distance_pct <= max_sl_dist_pct:
    PATTERNSLBUF_ALLOW = 1

ELSE:
    PATTERNSLBUF_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F082_sl_anchor_mode
F082_buffer_mode
F082_buffer_pct
F082_atr_mult
F082_range_mult
F082_sl_distance_mode
F082_min_sl_dist_pct
F082_max_sl_dist_pct
F082_PATTERNSLBUF_ALLOW
```

## REGISTRY_ROW

```text
F082 | pattern_sl_buffer_distance_1m | PATTERNSLBUF_ALLOW | PATTERN_TRADE_CONTEXT | sl_anchor_mode(PATTERN_EXTREME/STRUCTURE_LEVEL/NEAREST_VALID_LEVEL),buffer_mode(PCT/ATR14/PATTERN_RANGE),buffer_pct(0.00–1.00 step 0.02),atr_mult(0.2–3.0 step 0.1),range_mult(0.1–1.0 step 0.1),sl_distance_mode(MAX_RISK/MIN_DISTANCE/BAND),min_sl_dist_pct(0.02–2.00 step 0.02),max_sl_dist_pct(0.05–5.00 step 0.05) | output 1/0
```

---

# 7. TP LADDER ENGINE

```text
TP_LADDER_ENGINE = multi_target_context
```

## TARGET SOURCES

```text
target_source_mode:
    PATTERN_TARGET
    SWING_LEVELS
    DENSITY_VPOC
    FIBONACCI_GRID
    VWAP
    MIXED
```

## LONG TARGET CANDIDATES

```text
IF TRADE_SIDE = LONG:
    candidate_targets = valid levels above ENTRY_REF_PRICE
```

## SHORT TARGET CANDIDATES

```text
IF TRADE_SIDE = SHORT:
    candidate_targets = valid levels below ENTRY_REF_PRICE
```

## PATTERN TARGET

```text
PATTERN_TARGET:
    uses pattern_target_level if available

If pattern_target_level is missing:
    use measured move from pattern height when possible
```

## LADDER DISTANCE

```text
target_distance_pct[i] =
    LONG:  (target[i] / ENTRY_REF_PRICE - 1) * 100
    SHORT: (ENTRY_REF_PRICE / target[i] - 1) * 100
```

## LADDER RR

```text
target_rr[i] = target_distance_pct[i] / sl_buffer_distance_pct
```

## LADDER SCORE COMPONENTS

```text
valid_target_count_score = number of targets with target_distance_pct > 0
rr_score = number of targets with target_rr >= min_rr_to_target
spacing_score = number of adjacent targets with spacing >= target_spacing_min_pct
clear_path_score = 1 if no blocking level before first target else 0
```

## LADDER SCORE

```text
tp_ladder_score =
    valid_target_count_score
    + rr_score
    + spacing_score
    + clear_path_score
```

---

# 8. F083 — pattern_tp_ladder_score

```text
ID: F083
FEATURE: pattern_tp_ladder_score_1m
ACTION: PATTERNTPLADDER_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Проверяет, есть ли у паттерна нормальная TP-лесенка перед входом.
Это проверка качества входа, а не выставление реальных take profit ордеров.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| target_source_mode | enum | - | - | - | PATTERN_TARGET / SWING_LEVELS / DENSITY_VPOC / FIBONACCI_GRID / VWAP / MIXED | source | yes |
| min_targets | int | 1 | 5 | 1 | - | count | yes |
| min_rr_to_target | float | 0.50 | 5.00 | 0.10 | - | ratio | yes |
| target_spacing_min_pct | float | 0.05 | 2.00 | 0.05 | - | percent | yes |
| require_clear_path | enum | - | - | - | YES / NO | bool | yes |
| ladder_state | enum | - | - | - | GOOD / POOR | state | yes |
| ladder_score_thr | float | 1.0 | 10.0 | 0.5 | - | score | yes |

## PARAM_MEANING

```text
target_source_mode:
    откуда брать потенциальные цели

min_targets:
    минимальное количество доступных целей

min_rr_to_target:
    минимальный RR до цели

target_spacing_min_pct:
    минимальная дистанция между целями

require_clear_path:
    требовать отсутствие блокирующего уровня до первой цели

ladder_state = GOOD:
    вход разрешён, если TP-лесенка достаточно сильная

ladder_state = POOR:
    вход разрешён, если TP-лесенка слабая
```

## SIGNAL_RULE

```text
TARGET_COUNT_OK:
    number_of_valid_targets >= min_targets

CLEAR_PATH_OK:
    require_clear_path = NO
    OR clear_path_score = 1

LADDER_BASE_OK:
    TARGET_COUNT_OK
    AND CLEAR_PATH_OK

IF ladder_state = GOOD
   AND LADDER_BASE_OK
   AND tp_ladder_score >= ladder_score_thr:
    PATTERNTPLADDER_ALLOW = 1

ELSE IF ladder_state = POOR
   AND tp_ladder_score <= ladder_score_thr:
    PATTERNTPLADDER_ALLOW = 1

ELSE:
    PATTERNTPLADDER_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F083_target_source_mode
F083_min_targets
F083_min_rr_to_target
F083_target_spacing_min_pct
F083_require_clear_path
F083_ladder_state
F083_ladder_score_thr
F083_PATTERNTPLADDER_ALLOW
```

## REGISTRY_ROW

```text
F083 | pattern_tp_ladder_score_1m | PATTERNTPLADDER_ALLOW | PATTERN_TRADE_CONTEXT | target_source_mode(PATTERN_TARGET/SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID/VWAP/MIXED),min_targets(1–5 step 1),min_rr_to_target(0.50–5.00 step 0.10),target_spacing_min_pct(0.05–2.00 step 0.05),require_clear_path(YES/NO),ladder_state(GOOD/POOR),ladder_score_thr(1.0–10.0 step 0.5) | output 1/0
```

---

# 9. CALIBRATION_ORDER

```text
1. F082 pattern_sl_buffer_distance
2. F083 pattern_tp_ladder_score
```

## COMMENT_CALIBRATION_ORDER

```text
Сначала калибровать SL-контекст паттерна.
Потом TP-лесенку.

Причина:
TP ladder зависит от допустимого риска до SL.
```

---

# 10. CALIBRATION_EVALUATION_FIELDS

```text
These fields are NOT runtime parameters.
They are used only by calibration/backtest report.

net_profit
profit_factor
max_drawdown
winrate
avg_trade
expectancy
trade_count
avg_rr
median_rr
```

---

# 11. GLOBAL_NOT_CALIBRATED

```text
tf
calc_method
trade_side
pattern_detection_formulas
pattern_event_fields
real_stop_loss_order
real_take_profit_order
exit_rules
order_size
risk_per_trade
```

---

# 12. FUTURE_BLOCK_NOTE

```text
F082-F083 are ENTRY_FILTER context features.

Future block required:
GLOBAL_PATTERN_STRATEGY_ASSEMBLER

It will combine:
entry
exit
real TP/SL
profit evaluation
drawdown limits
session filters
position management
```

---

# 13. REGISTRY_ROWS_SHORT

```text
F082 | pattern_sl_buffer_distance_1m | PATTERNSLBUF_ALLOW | PATTERN_TRADE_CONTEXT | sl_anchor_mode(PATTERN_EXTREME/STRUCTURE_LEVEL/NEAREST_VALID_LEVEL),buffer_mode(PCT/ATR14/PATTERN_RANGE),sl_distance_mode(MAX_RISK/MIN_DISTANCE/BAND),min_sl_dist_pct(0.02–2.00),max_sl_dist_pct(0.05–5.00) | output 1/0

F083 | pattern_tp_ladder_score_1m | PATTERNTPLADDER_ALLOW | PATTERN_TRADE_CONTEXT | target_source_mode(PATTERN_TARGET/SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID/VWAP/MIXED),min_targets(1–5),min_rr_to_target(0.50–5.00),target_spacing_min_pct(0.05–2.00),require_clear_path(YES/NO),ladder_state(GOOD/POOR),ladder_score_thr(1.0–10.0) | output 1/0
```
