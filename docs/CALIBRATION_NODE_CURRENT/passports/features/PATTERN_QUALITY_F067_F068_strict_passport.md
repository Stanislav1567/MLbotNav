# PATTERN QUALITY — STRICT PASSPORT F067-F068 — V1

```text
FAMILY: PATTERN_QUALITY
FEATURES: F067-F068
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F067-F068 оценивают качество уже найденного паттерна.

F067 = сила паттерна
F068 = возраст паттерна в барах

Блок НЕ ищет паттерн с нуля.
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
CUSTOM_CALC = YES
```

## COMMENT_COMMON_FIXED

```text
Pattern Quality работает только если ранее найден pattern_event.

pattern_event может прийти из блоков:
CANDLE_PATTERNS = F053-F060
DIVERGENCE_PATTERNS = F061-F066
CHART_PATTERNS = F069-F077

Если активного pattern_event нет:
F067 = 0
F068 = 0
```

---

# 2. PATTERN_EVENT_MEMORY

```text
pattern_event fields:

pattern_id
pattern_family
pattern_direction
pattern_bar
pattern_price
base_pattern_score
source_feature_id
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

## DATA_GUARD_PATTERN_MEMORY

```text
IF no active pattern_event:
    PATTERNSTRENGTH_ALLOW = 0
    PATTERNAGE_ALLOW = 0
```

---

# 3. FIXED_QUALITY_CONTEXT_ENGINES

## 3.1 LEVEL_CONTEXT

```text
LEVEL_CONTEXT_SOURCE = F035-F039
LEVEL_DISTANCE_MAX_PCT = 0.50
```

## 3.2 VOLUME_CONTEXT

```text
VOLUME_CONTEXT_SOURCE = F019-F021
VOLUME_Z_WINDOW = 20
```

## 3.3 STRUCTURE_CONTEXT

```text
STRUCTURE_CONTEXT_SOURCE = F050-F052
STRUCTURE_SCOPE = INTERNAL / EXTERNAL
```

## 3.4 BREAKOUT_CONTEXT

```text
BREAKOUT_CONTEXT_SOURCE = F045-F049
BREAKOUT_MEMORY = ON
```

## COMMENT_CONTEXT_ENGINES

```text
Контекстные движки не калибруются внутри F067-F068.
Они используют уже созданные блоки.

F067 калибрует только итоговый threshold силы паттерна и режим оценки.
```

---

# 4. PATTERN_STRENGTH_SCORE

```text
pattern_strength_score =
    base_pattern_score
    + level_bonus
    + volume_bonus
    + structure_bonus
    + confirmation_bonus
```

## 4.1 BASE_PATTERN_SCORE

```text
CANDLE simple pattern:
    base_pattern_score = 1.0

CANDLE directional pattern:
    base_pattern_score = 2.0

DIVERGENCE regular:
    base_pattern_score = 3.0

DIVERGENCE hidden:
    base_pattern_score = 2.5

CHART pattern:
    base_pattern_score = 3.0
```

## 4.2 LEVEL_BONUS

```text
IF pattern appears near valid support/resistance/VWAP/VPOC/Fibonacci level:
    level_bonus = 1.0
ELSE:
    level_bonus = 0.0
```

## 4.3 VOLUME_BONUS

```text
IF pattern has volume confirmation:
    volume_bonus = 1.0
ELSE:
    volume_bonus = 0.0
```

## 4.4 STRUCTURE_BONUS

```text
IF pattern direction agrees with market structure:
    structure_bonus = 1.0
ELSE:
    structure_bonus = 0.0
```

## 4.5 CONFIRMATION_BONUS

```text
IF pattern has price confirmation after pattern_bar:
    confirmation_bonus = 1.0
ELSE:
    confirmation_bonus = 0.0
```

## SCORE_RANGE

```text
pattern_strength_score range:
0.0 to 7.0
```

---

# 5. F067 — pattern_strength

```text
ID: F067
FEATURE: pattern_strength_1m
ACTION: PATTERNSTRENGTH_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если сила активного паттерна соответствует откалиброванному порогу.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| strength_state | enum | - | - | - | STRONG / WEAK | strength_mode | yes |
| strength_thr | float | 1.0 | 7.0 | 0.5 | - | score | yes |
| require_confirmation | enum | - | - | - | YES / NO | confirmation_filter | yes |
| require_context | enum | - | - | - | YES / NO | context_filter | yes |

## PARAM_MEANING

```text
strength_state = STRONG:
    вход разрешён, если сила паттерна не ниже порога

strength_state = WEAK:
    вход разрешён, если сила паттерна не выше порога

require_confirmation = YES:
    confirmation_bonus должен быть больше 0

require_context = YES:
    хотя бы один из бонусов level/volume/structure должен быть больше 0
```

## SIGNAL_RULE

```text
CONFIRMATION_OK:
    require_confirmation = NO
    OR confirmation_bonus > 0

CONTEXT_OK:
    require_context = NO
    OR level_bonus + volume_bonus + structure_bonus > 0

IF strength_state = STRONG
   AND pattern_strength_score >= strength_thr
   AND CONFIRMATION_OK
   AND CONTEXT_OK:
    PATTERNSTRENGTH_ALLOW = 1

ELSE IF strength_state = WEAK
   AND pattern_strength_score <= strength_thr
   AND CONFIRMATION_OK
   AND CONTEXT_OK:
    PATTERNSTRENGTH_ALLOW = 1

ELSE:
    PATTERNSTRENGTH_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F067_strength_state
F067_strength_thr
F067_require_confirmation
F067_require_context
F067_PATTERNSTRENGTH_ALLOW
```

## REGISTRY_ROW

```text
F067 | pattern_strength_1m | PATTERNSTRENGTH_ALLOW | PATTERN_QUALITY | strength_state(STRONG/WEAK),strength_thr(1.0–7.0 step 0.5),require_confirmation(YES/NO),require_context(YES/NO) | output 1/0
```

---

# 6. F068 — pattern_age_bars

```text
ID: F068
FEATURE: pattern_age_bars_1m
ACTION: PATTERNAGE_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если активный паттерн ещё не устарел или, наоборот, если требуется выдержка после паттерна.
```

## FORMULA

```text
pattern_age_bars = current_closed_bar_index - pattern_bar
```

## DATA_GUARD

```text
IF pattern_age_bars < 0:
    PATTERNAGE_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| age_mode | enum | - | - | - | FRESH / MATURE / EXPIRED | age_mode | yes |
| min_age_bars | int | 0 | 20 | 1 | - | bars | conditional |
| max_age_bars | int | 1 | 120 | 1 | - | bars | conditional |

## PARAM_MEANING

```text
age_mode = FRESH:
    вход разрешён, если паттерн не старше max_age_bars

age_mode = MATURE:
    вход разрешён, если паттерн уже выдержал min_age_bars,
    но ещё не старше max_age_bars

age_mode = EXPIRED:
    вход разрешён, если паттерн старше max_age_bars
```

## SIGNAL_RULE

```text
IF age_mode = FRESH
   AND pattern_age_bars <= max_age_bars:
    PATTERNAGE_ALLOW = 1

ELSE IF age_mode = MATURE
   AND pattern_age_bars >= min_age_bars
   AND pattern_age_bars <= max_age_bars:
    PATTERNAGE_ALLOW = 1

ELSE IF age_mode = EXPIRED
   AND pattern_age_bars > max_age_bars:
    PATTERNAGE_ALLOW = 1

ELSE:
    PATTERNAGE_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F068_age_mode
F068_min_age_bars
F068_max_age_bars
F068_PATTERNAGE_ALLOW
```

## REGISTRY_ROW

```text
F068 | pattern_age_bars_1m | PATTERNAGE_ALLOW | PATTERN_QUALITY | age_mode(FRESH/MATURE/EXPIRED),min_age_bars(0–20 step 1),max_age_bars(1–120 step 1) | output 1/0
```

---

# 7. CALIBRATION_ORDER

```text
1. F067 pattern_strength
2. F068 pattern_age_bars
```

## COMMENT_CALIBRATION_ORDER

```text
Сначала калибровать силу паттерна.
Потом возраст паттерна.

F067 отвечает за качество сигнала.
F068 отвечает за актуальность сигнала.
```

---

# 8. GLOBAL_NOT_CALIBRATED

```text
side
tf
calc_method
pattern_detection_engines
base_pattern_score_table
level_context_engine
volume_context_engine
structure_context_engine
breakout_context_engine
entry_exit
order_size
take_profit_order
stop_loss_order
```

---

# 9. REGISTRY_ROWS_SHORT

```text
F067 | pattern_strength_1m | PATTERNSTRENGTH_ALLOW | PATTERN_QUALITY | strength_state(STRONG/WEAK),strength_thr(1.0–7.0 step 0.5),require_confirmation(YES/NO),require_context(YES/NO) | output 1/0

F068 | pattern_age_bars_1m | PATTERNAGE_ALLOW | PATTERN_QUALITY | age_mode(FRESH/MATURE/EXPIRED),min_age_bars(0–20 step 1),max_age_bars(1–120 step 1) | output 1/0
```
