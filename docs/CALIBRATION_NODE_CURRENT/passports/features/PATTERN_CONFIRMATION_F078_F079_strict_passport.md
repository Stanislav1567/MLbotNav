# PATTERN CONFIRMATION — STRICT PASSPORT F078-F079 — V1

```text
FAMILY: PATTERN_CONFIRMATION
FEATURES: F078-F079
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F078-F079 подтверждают уже найденный pattern_event.

F078 = подтверждение паттерна объёмом
F079 = подтверждение паттерна уровнем

Блок НЕ ищет паттерн с нуля.
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
PATTERN_MEMORY = ON
CUSTOM_CALC = YES
```

## COMMENT_COMMON_FIXED

```text
Блок работает только если есть активный pattern_event.

pattern_event может прийти из:
F053-F060 = CANDLE_PATTERNS
F061-F066 = DIVERGENCE_PATTERNS
F069-F077 = CHART_PATTERNS

Если активного pattern_event нет:
F078 = 0
F079 = 0
```

---

# 2. PATTERN_EVENT_FIELDS

```text
pattern_id
pattern_family
pattern_direction
pattern_bar
pattern_price
source_feature_id
pattern_breakout_level
pattern_neckline
pattern_support_level
pattern_resistance_level
pattern_start_bar
pattern_end_bar
```

## PATTERN_DIRECTION

```text
BULLISH
BEARISH
NEUTRAL
```

---

# 3. F078 — pattern_volume_confirm_flag

```text
ID: F078
FEATURE: pattern_volume_confirm_flag_1m
ACTION: PATTERNVOLCONF_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если активный паттерн подтверждён объёмом.
```

## FIXED_VOLUME_ENGINE

```text
VOLUME_SOURCE = base_volume
VOLUME_MA_WINDOW = 20
VOLUME_Z_WINDOW = 20
VOLUME_METHOD = closed_bar_volume
```

## FORMULAS

```text
pattern_volume = Volume[pattern_bar]

avg_volume_20 = SMA(Volume, 20)

vol_ratio = pattern_volume / avg_volume_20

vol_z = (pattern_volume - SMA(Volume, 20)) / STD(Volume, 20)
```

## DATA_GUARD

```text
IF no active pattern_event:
    PATTERNVOLCONF_ALLOW = 0

IF avg_volume_20 <= 0:
    PATTERNVOLCONF_ALLOW = 0

IF STD(Volume, 20) <= 0 AND confirm_mode = Z_SCORE:
    PATTERNVOLCONF_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| confirm_mode | enum | - | - | - | RATIO / Z_SCORE / BOTH | volume_confirm_mode | yes |
| ratio_thr | float | 1.0 | 5.0 | 0.1 | - | ratio | conditional |
| z_thr | float | 0.0 | 5.0 | 0.1 | - | z_score | conditional |
| confirm_bar_mode | enum | - | - | - | PATTERN_BAR / NEXT_BAR / BREAKOUT_BAR | bar_mode | yes |
| direction_filter | enum | - | - | - | ANY / MATCH_PATTERN | direction_filter | yes |

## PARAM_MEANING

```text
confirm_mode = RATIO:
    подтверждение по отношению Volume к среднему объёму

confirm_mode = Z_SCORE:
    подтверждение по Z-score объёма

confirm_mode = BOTH:
    должны выполниться оба условия

confirm_bar_mode = PATTERN_BAR:
    объём проверяется на свече паттерна

confirm_bar_mode = NEXT_BAR:
    объём проверяется на следующей закрытой свече после паттерна

confirm_bar_mode = BREAKOUT_BAR:
    объём проверяется на свече пробоя/подтверждения паттерна

direction_filter = ANY:
    направление свечи не проверяется

direction_filter = MATCH_PATTERN:
    bullish pattern требует bullish candle,
    bearish pattern требует bearish candle
```

## SIGNAL_RULE

```text
VOLUME_RATIO_OK:
    vol_ratio >= ratio_thr

VOLUME_Z_OK:
    vol_z >= z_thr

DIRECTION_OK:
    direction_filter = ANY
    OR pattern_direction = BULLISH AND Close[confirm_bar] > Open[confirm_bar]
    OR pattern_direction = BEARISH AND Close[confirm_bar] < Open[confirm_bar]
    OR pattern_direction = NEUTRAL

IF confirm_mode = RATIO
   AND VOLUME_RATIO_OK
   AND DIRECTION_OK:
    PATTERNVOLCONF_ALLOW = 1

ELSE IF confirm_mode = Z_SCORE
   AND VOLUME_Z_OK
   AND DIRECTION_OK:
    PATTERNVOLCONF_ALLOW = 1

ELSE IF confirm_mode = BOTH
   AND VOLUME_RATIO_OK
   AND VOLUME_Z_OK
   AND DIRECTION_OK:
    PATTERNVOLCONF_ALLOW = 1

ELSE:
    PATTERNVOLCONF_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F078_confirm_mode
F078_ratio_thr
F078_z_thr
F078_confirm_bar_mode
F078_direction_filter
F078_PATTERNVOLCONF_ALLOW
```

## REGISTRY_ROW

```text
F078 | pattern_volume_confirm_flag_1m | PATTERNVOLCONF_ALLOW | PATTERN_CONFIRMATION | confirm_mode(RATIO/Z_SCORE/BOTH),ratio_thr(1.0–5.0 step 0.1),z_thr(0.0–5.0 step 0.1),confirm_bar_mode(PATTERN_BAR/NEXT_BAR/BREAKOUT_BAR),direction_filter(ANY/MATCH_PATTERN) | output 1/0
```

---

# 4. F079 — pattern_level_confirm_flag

```text
ID: F079
FEATURE: pattern_level_confirm_flag_1m
ACTION: PATTERNLEVELCONF_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход, если активный паттерн подтверждён уровнем.
```

## LEVEL_SOURCE_MODE

```text
SWING_LEVELS
DENSITY_VPOC
FIBONACCI_GRID
VWAP
ANY_LEVEL
```

## FIXED_LEVEL_ENGINES

```text
SWING_LEVELS_SOURCE = F035-F039
DENSITY_VPOC_SOURCE = F025-F034
FIBONACCI_GRID_SOURCE = F040-F041
VWAP_SOURCE = F024
```

## COMMENT_FIXED_LEVEL_ENGINES

```text
Движки уровней не калибруются внутри F079.
Они должны совпадать с уже созданными паспортами.
F079 калибрует только источник уровня, близость и тип подтверждения.
```

## FORMULAS

```text
pattern_price = price of pattern_event

nearest_level = nearest active level from selected LEVEL_SOURCE_MODE

level_distance_pct = abs(pattern_price / nearest_level - 1) * 100
```

## DATA_GUARD

```text
IF no active pattern_event:
    PATTERNLEVELCONF_ALLOW = 0

IF no nearest_level:
    PATTERNLEVELCONF_ALLOW = 0

IF nearest_level <= 0:
    PATTERNLEVELCONF_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| level_source_mode | enum | - | - | - | SWING_LEVELS / DENSITY_VPOC / FIBONACCI_GRID / VWAP / ANY_LEVEL | source | yes |
| confirm_type | enum | - | - | - | NEAR_LEVEL / REJECTION / BREAKOUT | level_confirm_type | yes |
| dist_thr_pct | float | 0.00 | 2.00 | 0.01 | - | percent | yes |
| reaction_confirm_pct | float | 0.00 | 1.00 | 0.01 | - | percent | conditional |
| direction_filter | enum | - | - | - | ANY / MATCH_PATTERN | direction_filter | yes |

## PARAM_MEANING

```text
confirm_type = NEAR_LEVEL:
    паттерн должен появиться рядом с уровнем

confirm_type = REJECTION:
    паттерн должен показать отбой от уровня

confirm_type = BREAKOUT:
    паттерн должен подтвердить пробой уровня

direction_filter = ANY:
    направление паттерна не проверяется

direction_filter = MATCH_PATTERN:
    bullish pattern должен подтверждаться bullish-реакцией,
    bearish pattern должен подтверждаться bearish-реакцией
```

## SIGNAL_RULE

```text
NEAR_LEVEL_OK:
    level_distance_pct <= dist_thr_pct

BULLISH_REJECTION:
    pattern_direction = BULLISH
    AND Low[pattern_bar] <= nearest_level * (1 + dist_thr_pct / 100)
    AND Close[1] >= nearest_level * (1 + reaction_confirm_pct / 100)

BEARISH_REJECTION:
    pattern_direction = BEARISH
    AND High[pattern_bar] >= nearest_level * (1 - dist_thr_pct / 100)
    AND Close[1] <= nearest_level * (1 - reaction_confirm_pct / 100)

BULLISH_BREAKOUT:
    pattern_direction = BULLISH
    AND Close[1] >= nearest_level * (1 + reaction_confirm_pct / 100)

BEARISH_BREAKOUT:
    pattern_direction = BEARISH
    AND Close[1] <= nearest_level * (1 - reaction_confirm_pct / 100)

DIRECTION_OK:
    direction_filter = ANY
    OR pattern_direction = BULLISH
    OR pattern_direction = BEARISH
    OR pattern_direction = NEUTRAL

IF confirm_type = NEAR_LEVEL
   AND NEAR_LEVEL_OK
   AND DIRECTION_OK:
    PATTERNLEVELCONF_ALLOW = 1

ELSE IF confirm_type = REJECTION
   AND (BULLISH_REJECTION OR BEARISH_REJECTION):
    PATTERNLEVELCONF_ALLOW = 1

ELSE IF confirm_type = BREAKOUT
   AND (BULLISH_BREAKOUT OR BEARISH_BREAKOUT):
    PATTERNLEVELCONF_ALLOW = 1

ELSE:
    PATTERNLEVELCONF_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F079_level_source_mode
F079_confirm_type
F079_dist_thr_pct
F079_reaction_confirm_pct
F079_direction_filter
F079_PATTERNLEVELCONF_ALLOW
```

## REGISTRY_ROW

```text
F079 | pattern_level_confirm_flag_1m | PATTERNLEVELCONF_ALLOW | PATTERN_CONFIRMATION | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID/VWAP/ANY_LEVEL),confirm_type(NEAR_LEVEL/REJECTION/BREAKOUT),dist_thr_pct(0.00–2.00 step 0.01),reaction_confirm_pct(0.00–1.00 step 0.01),direction_filter(ANY/MATCH_PATTERN) | output 1/0
```

---

# 5. CALIBRATION_ORDER

```text
1. F079 pattern_level_confirm_flag
2. F078 pattern_volume_confirm_flag
```

## COMMENT_CALIBRATION_ORDER

```text
Сначала калибровать подтверждение уровнем.
Потом подтверждение объёмом.

Причина:
уровневый контекст обычно важнее для паттерна,
а объём используется как дополнительный фильтр качества.
```

---

# 6. GLOBAL_NOT_CALIBRATED

```text
side
tf
calc_method
pattern_detection_engines
pattern_memory_fields
volume_ma_window
volume_z_window
level_engines
entry_exit
order_size
take_profit_order
stop_loss_order
```

---

# 7. REGISTRY_ROWS_SHORT

```text
F078 | pattern_volume_confirm_flag_1m | PATTERNVOLCONF_ALLOW | PATTERN_CONFIRMATION | confirm_mode(RATIO/Z_SCORE/BOTH),ratio_thr(1.0–5.0 step 0.1),z_thr(0.0–5.0 step 0.1),confirm_bar_mode(PATTERN_BAR/NEXT_BAR/BREAKOUT_BAR),direction_filter(ANY/MATCH_PATTERN) | output 1/0

F079 | pattern_level_confirm_flag_1m | PATTERNLEVELCONF_ALLOW | PATTERN_CONFIRMATION | level_source_mode(SWING_LEVELS/DENSITY_VPOC/FIBONACCI_GRID/VWAP/ANY_LEVEL),confirm_type(NEAR_LEVEL/REJECTION/BREAKOUT),dist_thr_pct(0.00–2.00 step 0.01),reaction_confirm_pct(0.00–1.00 step 0.01),direction_filter(ANY/MATCH_PATTERN) | output 1/0
```
