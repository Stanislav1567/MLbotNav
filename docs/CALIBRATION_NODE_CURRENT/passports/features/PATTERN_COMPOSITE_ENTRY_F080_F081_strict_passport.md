# PATTERN COMPOSITE ENTRY — STRICT PASSPORT F080-F081 — V1

```text
FAMILY: PATTERN_COMPOSITE_ENTRY
FEATURES: F080-F081
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F080-F081 собирают композитный вход из уже готовых паттерн-блоков.

F080 = композитный вход для LONG-профиля
F081 = композитный вход для SHORT-профиля

Блок НЕ ищет паттерны заново.
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
PATTERN_MEMORY = ON
COMPOSITE_MODE = pattern + quality + confirmation + structure + breakout
CUSTOM_CALC = YES
```

## COMMENT_COMMON_FIXED

```text
Этот блок работает только после предыдущих pattern-блоков.

Он использует готовые сигналы:
CANDLE_PATTERNS
DIVERGENCE_PATTERNS
CHART_PATTERNS
PATTERN_QUALITY
PATTERN_CONFIRMATION
MARKET_STRUCTURE
BREAKOUT_RETEST

Внутри F080-F081 не пересчитываются формулы свечей, дивергенций, фигур, BOS/CHOCH, объёма и уровней.
```

---

# 2. INPUT_BLOCKS

```text
PATTERN_DETECTION:
    F053-F060 = CANDLE_PATTERNS
    F061-F066 = DIVERGENCE_PATTERNS
    F069-F077 = CHART_PATTERNS

PATTERN_QUALITY:
    F067 = pattern_strength
    F068 = pattern_age_bars

PATTERN_CONFIRMATION:
    F078 = pattern_volume_confirm
    F079 = pattern_level_confirm

STRUCTURE:
    F050 = BOS_UP
    F051 = BOS_DOWN
    F052 = CHOCH

BREAKOUT_RETEST:
    F045 = breakout_flag
    F046 = false_breakout_flag
    F047 = retest_flag
    F048 = swing_high_break
    F049 = swing_low_break
```

---

# 3. PATTERN_EVENT_REQUIREMENT

```text
IF no active pattern_event:
    F080_PATTERNLONG_ALLOW = 0
    F081_PATTERNSHORT_ALLOW = 0
```

## PATTERN_EVENT_FIELDS

```text
pattern_id
pattern_family
pattern_direction
pattern_bar
pattern_price
source_feature_id
pattern_strength_score
pattern_age_bars
```

## PATTERN_FAMILY

```text
CANDLE
DIVERGENCE
CHART
```

## PATTERN_DIRECTION

```text
BULLISH
BEARISH
NEUTRAL
```

---

# 4. COMPOSITE SCORE MODEL

```text
pattern_exists_score = 1

strength_score = 1 if F067_ALLOW = 1 else 0
age_score = 1 if F068_ALLOW = 1 else 0
volume_score = 1 if F078_ALLOW = 1 else 0
level_score = 1 if F079_ALLOW = 1 else 0
structure_score = 1 if selected structure condition is true else 0
breakout_score = 1 if selected breakout condition is true else 0

composite_score =
    pattern_exists_score
    + strength_score
    + age_score
    + volume_score
    + level_score
    + structure_score
    + breakout_score
```

```text
SCORE_RANGE = 1..7
```

---

# 5. COMMON_CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| pattern_family_filter | enum | - | - | - | ANY / CANDLE / DIVERGENCE / CHART | family | yes |
| direction_mode | enum | - | - | - | DIRECT_ONLY / ALLOW_NEUTRAL_WITH_CONTEXT | direction_mode | yes |
| logic_mode | enum | - | - | - | STRICT / SCORE | logic | yes |
| use_strength | enum | - | - | - | YES / NO | bool | yes |
| use_age | enum | - | - | - | YES / NO | bool | yes |
| use_volume_confirm | enum | - | - | - | YES / NO | bool | yes |
| use_level_confirm | enum | - | - | - | YES / NO | bool | yes |
| min_score | int | 2 | 7 | 1 | - | score | conditional |
| block_opposite_pattern | enum | - | - | - | YES / NO | bool | yes |

---

# 6. COMMON_PARAM_MEANING

```text
pattern_family_filter:
    какие семейства паттернов разрешены для композита

direction_mode = DIRECT_ONLY:
    LONG берёт только BULLISH
    SHORT берёт только BEARISH

direction_mode = ALLOW_NEUTRAL_WITH_CONTEXT:
    LONG берёт BULLISH и NEUTRAL, если есть подтверждения
    SHORT берёт BEARISH и NEUTRAL, если есть подтверждения

logic_mode = STRICT:
    все включённые use_* условия должны быть выполнены

logic_mode = SCORE:
    условия дают баллы, вход разрешён при composite_score >= min_score

block_opposite_pattern = YES:
    LONG блокируется при активном BEARISH паттерне
    SHORT блокируется при активном BULLISH паттерне
```

---

# 7. F080 — pattern_structure_volume_entry_long

```text
ID: F080
FEATURE: pattern_structure_volume_entry_long_1m
ACTION: PATTERNLONG_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
COMPOSITE_SIDE = LONG
```

## LONG_SPECIFIC_CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| structure_filter | enum | - | - | - | NONE / BULLISH_BIAS / BOS_UP / BULLISH_CHOCH / ANY_BULLISH_STRUCTURE | structure | yes |
| breakout_filter | enum | - | - | - | NONE / BREAKOUT_UP / RETEST_UP / SWING_HIGH_BREAK / ANY_UP_BREAK | breakout | yes |

## LONG_DIRECTION_RULE

```text
DIRECT_LONG_OK:
    pattern_direction = BULLISH

NEUTRAL_LONG_OK:
    direction_mode = ALLOW_NEUTRAL_WITH_CONTEXT
    AND pattern_direction = NEUTRAL
    AND composite_score >= min_score

OPPOSITE_BLOCK_LONG:
    block_opposite_pattern = YES
    AND pattern_direction = BEARISH
```

## LONG_STRUCTURE_RULE

```text
structure_filter = NONE:
    structure_condition = TRUE

structure_filter = BULLISH_BIAS:
    structure_condition = current_structure_bias = BULLISH

structure_filter = BOS_UP:
    structure_condition = F050_BOSUP_ALLOW = 1

structure_filter = BULLISH_CHOCH:
    structure_condition = F052_CHOCH_ALLOW = 1 AND choch_dir = BULLISH

structure_filter = ANY_BULLISH_STRUCTURE:
    structure_condition =
        current_structure_bias = BULLISH
        OR F050_BOSUP_ALLOW = 1
        OR bullish CHOCH = true
```

## LONG_BREAKOUT_RULE

```text
breakout_filter = NONE:
    breakout_condition = TRUE

breakout_filter = BREAKOUT_UP:
    breakout_condition = F045_BREAKOUT_ALLOW = 1 AND break_dir = UP

breakout_filter = RETEST_UP:
    breakout_condition = F047_RETEST_ALLOW = 1 AND break_dir = UP

breakout_filter = SWING_HIGH_BREAK:
    breakout_condition = F048_SWINGHIGHBREAK_ALLOW = 1

breakout_filter = ANY_UP_BREAK:
    breakout_condition =
        BREAKOUT_UP
        OR RETEST_UP
        OR SWING_HIGH_BREAK
```

## LONG_STRICT_RULE

```text
STRICT_OK:
    pattern_family_filter matches pattern_family
    AND DIRECT_OR_NEUTRAL_LONG_OK
    AND NOT OPPOSITE_BLOCK_LONG
    AND structure_condition = TRUE
    AND breakout_condition = TRUE
    AND (use_strength = NO OR F067_PATTERNSTRENGTH_ALLOW = 1)
    AND (use_age = NO OR F068_PATTERNAGE_ALLOW = 1)
    AND (use_volume_confirm = NO OR F078_PATTERNVOLCONF_ALLOW = 1)
    AND (use_level_confirm = NO OR F079_PATTERNLEVELCONF_ALLOW = 1)

IF logic_mode = STRICT AND STRICT_OK:
    PATTERNLONG_ALLOW = 1
ELSE:
    PATTERNLONG_ALLOW = 0
```

## LONG_SCORE_RULE

```text
SCORE_OK:
    pattern_family_filter matches pattern_family
    AND DIRECT_OR_NEUTRAL_LONG_OK
    AND NOT OPPOSITE_BLOCK_LONG
    AND composite_score >= min_score

IF logic_mode = SCORE AND SCORE_OK:
    PATTERNLONG_ALLOW = 1
ELSE:
    PATTERNLONG_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F080_pattern_family_filter
F080_direction_mode
F080_logic_mode
F080_use_strength
F080_use_age
F080_use_volume_confirm
F080_use_level_confirm
F080_structure_filter
F080_breakout_filter
F080_min_score
F080_block_opposite_pattern
F080_PATTERNLONG_ALLOW
```

## REGISTRY_ROW

```text
F080 | pattern_structure_volume_entry_long_1m | PATTERNLONG_ALLOW | PATTERN_COMPOSITE_ENTRY | pattern_family_filter(ANY/CANDLE/DIVERGENCE/CHART),direction_mode(DIRECT_ONLY/ALLOW_NEUTRAL_WITH_CONTEXT),logic_mode(STRICT/SCORE),use_strength(YES/NO),use_age(YES/NO),use_volume_confirm(YES/NO),use_level_confirm(YES/NO),structure_filter(NONE/BULLISH_BIAS/BOS_UP/BULLISH_CHOCH/ANY_BULLISH_STRUCTURE),breakout_filter(NONE/BREAKOUT_UP/RETEST_UP/SWING_HIGH_BREAK/ANY_UP_BREAK),min_score(2–7 step 1),block_opposite_pattern(YES/NO) | output 1/0
```

---

# 8. F081 — pattern_structure_volume_entry_short

```text
ID: F081
FEATURE: pattern_structure_volume_entry_short_1m
ACTION: PATTERNSHORT_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
COMPOSITE_SIDE = SHORT
```

## SHORT_SPECIFIC_CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| structure_filter | enum | - | - | - | NONE / BEARISH_BIAS / BOS_DOWN / BEARISH_CHOCH / ANY_BEARISH_STRUCTURE | structure | yes |
| breakout_filter | enum | - | - | - | NONE / BREAKOUT_DOWN / RETEST_DOWN / SWING_LOW_BREAK / ANY_DOWN_BREAK | breakout | yes |

## SHORT_DIRECTION_RULE

```text
DIRECT_SHORT_OK:
    pattern_direction = BEARISH

NEUTRAL_SHORT_OK:
    direction_mode = ALLOW_NEUTRAL_WITH_CONTEXT
    AND pattern_direction = NEUTRAL
    AND composite_score >= min_score

OPPOSITE_BLOCK_SHORT:
    block_opposite_pattern = YES
    AND pattern_direction = BULLISH
```

## SHORT_STRUCTURE_RULE

```text
structure_filter = NONE:
    structure_condition = TRUE

structure_filter = BEARISH_BIAS:
    structure_condition = current_structure_bias = BEARISH

structure_filter = BOS_DOWN:
    structure_condition = F051_BOSDOWN_ALLOW = 1

structure_filter = BEARISH_CHOCH:
    structure_condition = F052_CHOCH_ALLOW = 1 AND choch_dir = BEARISH

structure_filter = ANY_BEARISH_STRUCTURE:
    structure_condition =
        current_structure_bias = BEARISH
        OR F051_BOSDOWN_ALLOW = 1
        OR bearish CHOCH = true
```

## SHORT_BREAKOUT_RULE

```text
breakout_filter = NONE:
    breakout_condition = TRUE

breakout_filter = BREAKOUT_DOWN:
    breakout_condition = F045_BREAKOUT_ALLOW = 1 AND break_dir = DOWN

breakout_filter = RETEST_DOWN:
    breakout_condition = F047_RETEST_ALLOW = 1 AND break_dir = DOWN

breakout_filter = SWING_LOW_BREAK:
    breakout_condition = F049_SWINGLOWBREAK_ALLOW = 1

breakout_filter = ANY_DOWN_BREAK:
    breakout_condition =
        BREAKOUT_DOWN
        OR RETEST_DOWN
        OR SWING_LOW_BREAK
```

## SHORT_STRICT_RULE

```text
STRICT_OK:
    pattern_family_filter matches pattern_family
    AND DIRECT_OR_NEUTRAL_SHORT_OK
    AND NOT OPPOSITE_BLOCK_SHORT
    AND structure_condition = TRUE
    AND breakout_condition = TRUE
    AND (use_strength = NO OR F067_PATTERNSTRENGTH_ALLOW = 1)
    AND (use_age = NO OR F068_PATTERNAGE_ALLOW = 1)
    AND (use_volume_confirm = NO OR F078_PATTERNVOLCONF_ALLOW = 1)
    AND (use_level_confirm = NO OR F079_PATTERNLEVELCONF_ALLOW = 1)

IF logic_mode = STRICT AND STRICT_OK:
    PATTERNSHORT_ALLOW = 1
ELSE:
    PATTERNSHORT_ALLOW = 0
```

## SHORT_SCORE_RULE

```text
SCORE_OK:
    pattern_family_filter matches pattern_family
    AND DIRECT_OR_NEUTRAL_SHORT_OK
    AND NOT OPPOSITE_BLOCK_SHORT
    AND composite_score >= min_score

IF logic_mode = SCORE AND SCORE_OK:
    PATTERNSHORT_ALLOW = 1
ELSE:
    PATTERNSHORT_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F081_pattern_family_filter
F081_direction_mode
F081_logic_mode
F081_use_strength
F081_use_age
F081_use_volume_confirm
F081_use_level_confirm
F081_structure_filter
F081_breakout_filter
F081_min_score
F081_block_opposite_pattern
F081_PATTERNSHORT_ALLOW
```

## REGISTRY_ROW

```text
F081 | pattern_structure_volume_entry_short_1m | PATTERNSHORT_ALLOW | PATTERN_COMPOSITE_ENTRY | pattern_family_filter(ANY/CANDLE/DIVERGENCE/CHART),direction_mode(DIRECT_ONLY/ALLOW_NEUTRAL_WITH_CONTEXT),logic_mode(STRICT/SCORE),use_strength(YES/NO),use_age(YES/NO),use_volume_confirm(YES/NO),use_level_confirm(YES/NO),structure_filter(NONE/BEARISH_BIAS/BOS_DOWN/BEARISH_CHOCH/ANY_BEARISH_STRUCTURE),breakout_filter(NONE/BREAKOUT_DOWN/RETEST_DOWN/SWING_LOW_BREAK/ANY_DOWN_BREAK),min_score(2–7 step 1),block_opposite_pattern(YES/NO) | output 1/0
```

---

# 9. CALIBRATION_EVALUATION_FIELDS

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
long_short_profile
```

## COMMENT_CALIBRATION_EVALUATION

```text
Этот блок нужно оценивать не только по accuracy/ALLOW count,
а по торговому результату в backtest.

Минимально контролировать:
profit_factor
net_profit
max_drawdown
trade_count

Если trade_count слишком маленький, результат не считать устойчивым.
```

---

# 10. CALIBRATION_OUTPUT_TO_RUNTIME

```text
После калибровки передаются только выбранные параметры:

F080_* for LONG profile
F081_* for SHORT profile
```

```text
Runtime outputs:
F080_PATTERNLONG_ALLOW = 1/0
F081_PATTERNSHORT_ALLOW = 1/0
```

---

# 11. GLOBAL_NOT_CALIBRATED

```text
tf
calc_method
pattern_detection_formulas
divergence_formulas
chart_pattern_formulas
pattern_strength_formula
pattern_age_formula
pattern_volume_confirm_formula
pattern_level_confirm_formula
market_structure_formula
breakout_retest_formula
take_profit_order
stop_loss_order
exit_rules
order_size
```

---

# 12. FUTURE_BLOCK_NOTE

```text
После завершения всех pattern-блоков нужен отдельный будущий блок:

GLOBAL_PATTERN_STRATEGY_ASSEMBLER

Он будет объединять:
entry filters
exit filters
TP/SL logic
profit evaluation
drawdown limits
portfolio/session constraints

F080-F081 сейчас остаются только ENTRY_FILTER.
```

---

# 13. REGISTRY_ROWS_SHORT

```text
F080 | pattern_structure_volume_entry_long_1m | PATTERNLONG_ALLOW | PATTERN_COMPOSITE_ENTRY | family(ANY/CANDLE/DIVERGENCE/CHART),direction(DIRECT_ONLY/ALLOW_NEUTRAL),logic(STRICT/SCORE),use_strength(YES/NO),use_age(YES/NO),use_volume(YES/NO),use_level(YES/NO),structure_filter,bk_filter,min_score(2–7),block_opposite(YES/NO) | output 1/0

F081 | pattern_structure_volume_entry_short_1m | PATTERNSHORT_ALLOW | PATTERN_COMPOSITE_ENTRY | family(ANY/CANDLE/DIVERGENCE/CHART),direction(DIRECT_ONLY/ALLOW_NEUTRAL),logic(STRICT/SCORE),use_strength(YES/NO),use_age(YES/NO),use_volume(YES/NO),use_level(YES/NO),structure_filter,bk_filter,min_score(2–7),block_opposite(YES/NO) | output 1/0
```
