# MARKET STRUCTURE — STRICT PASSPORT F050-F052 — V1

```text
FAMILY: MARKET_STRUCTURE
FEATURES: F050-F052
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F050-F052 проверяют состояние рыночной структуры перед входом.

F050 = BOS вверх
F051 = BOS вниз
F052 = CHOCH / смена характера структуры

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
CONFIRMATION_PRICE = Close
WICK_BREAK_POLICY = ignore_for_confirmation
TRADE_SIDE_SOURCE = external_profile
TRADE_SIDE = LONG / SHORT
```

## COMMENT_COMMON_FIXED

```text
BOS и CHOCH подтверждаются только закрытием свечи.
Прокол тенью без закрытия за уровнем не считается подтверждённой структурой.

TRADE_SIDE не калибруется внутри F050-F052.
Оптумно отдельно калибрует LONG и SHORT.
```

---

# 2. STRUCTURE_SCOPE

```text
STRUCTURE_SCOPE:
    INTERNAL
    EXTERNAL
```

## COMMENT_STRUCTURE_SCOPE

```text
INTERNAL = более чувствительная внутренняя структура.
EXTERNAL = более крупная структура, меньше шума.

STRUCTURE_SCOPE калибруется.
```

---

# 3. FIXED_STRUCTURE_ENGINES

## 3.1 INTERNAL_STRUCTURE_ENGINE

```text
INTERNAL_SWING_LOOKBACK = 120
INTERNAL_PIVOT_LEFT = 3
INTERNAL_PIVOT_RIGHT = 3
INTERNAL_MIN_SWING_PCT = 0.15
INTERNAL_MAX_SWING_AGE_BARS = 120
```

## 3.2 EXTERNAL_STRUCTURE_ENGINE

```text
EXTERNAL_SWING_LOOKBACK = 240
EXTERNAL_PIVOT_LEFT = 10
EXTERNAL_PIVOT_RIGHT = 10
EXTERNAL_MIN_SWING_PCT = 0.30
EXTERNAL_MAX_SWING_AGE_BARS = 240
```

## COMMENT_STRUCTURE_ENGINES

```text
Параметры движков не калибруются внутри F050-F052.
Калибруется только выбор STRUCTURE_SCOPE = INTERNAL / EXTERNAL.

INTERNAL быстрее, но шумнее.
EXTERNAL медленнее, но структурно надёжнее.
```

---

# 4. SWING AND STRUCTURE DEFINITIONS

## 4.1 CONFIRMED SWINGS

```text
swing_high:
    High[pivot] выше соседних High слева и справа по pivot-настройкам

swing_low:
    Low[pivot] ниже соседних Low слева и справа по pivot-настройкам

swing is confirmed only after PIVOT_RIGHT closed candles
```

## 4.2 SWING LABELS

```text
HH = higher high
HL = higher low
LH = lower high
LL = lower low
```

## 4.3 STRUCTURE BIAS

```text
BULLISH_BIAS:
    структура формирует HH + HL
    или последний подтверждённый BOS был вверх

BEARISH_BIAS:
    структура формирует LL + LH
    или последний подтверждённый BOS был вниз

NEUTRAL_BIAS:
    недостаточно подтверждённых swing-точек
```

---

# 5. STRUCTURE LEVELS

```text
last_structure_high = последний подтверждённый swing_high,
который является актуальным максимумом структуры

last_structure_low = последний подтверждённый swing_low,
который является актуальным минимумом структуры

protected_high = последний LH в bearish structure

protected_low = последний HL в bullish structure
```

## DATA_GUARD_STRUCTURE

```text
IF required structure level is missing:
    ALLOW = 0

IF structure level <= 0:
    ALLOW = 0
```

---

# 6. F050 — bos_up_flag

```text
ID: F050
FEATURE: bos_up_flag_1m
ACTION: BOSUP_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход при подтверждённом Break Of Structure вверх.
BOS_UP = продолжение/подтверждение бычьей структуры.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| structure_scope | enum | - | - | - | INTERNAL / EXTERNAL | scope | yes |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent | yes |
| confirm_bars | int | 1 | 3 | 1 | - | bars | yes |
| require_bias | enum | - | - | - | BULLISH / NOT_BEARISH | bias_rule | yes |

## PARAM_MEANING

```text
require_bias = BULLISH:
    BOS_UP разрешён только если до пробоя структура уже была bullish.

require_bias = NOT_BEARISH:
    BOS_UP разрешён если структура bullish или neutral.
```

## SIGNAL_RULE

```text
target_level = last_structure_high

BOS_UP_CLOSE:
    Close[1] >= target_level * (1 + break_buffer_pct / 100)

BOS_UP_CONFIRM:
    last confirm_bars closes are above target_level with buffer

IF require_bias = BULLISH:
    bias_condition = structure_bias = BULLISH_BIAS

IF require_bias = NOT_BEARISH:
    bias_condition = structure_bias = BULLISH_BIAS OR structure_bias = NEUTRAL_BIAS

IF BOS_UP_CONFIRM AND bias_condition:
    BOSUP_ALLOW = 1
    save last_structure_event = BOS_UP

ELSE:
    BOSUP_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F050_structure_scope
F050_break_buffer_pct
F050_confirm_bars
F050_require_bias
F050_BOSUP_ALLOW
```

## REGISTRY_ROW

```text
F050 | bos_up_flag_1m | BOSUP_ALLOW | MARKET_STRUCTURE | structure_scope(INTERNAL/EXTERNAL),break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1),require_bias(BULLISH/NOT_BEARISH) | output 1/0
```

---

# 7. F051 — bos_down_flag

```text
ID: F051
FEATURE: bos_down_flag_1m
ACTION: BOSDOWN_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход при подтверждённом Break Of Structure вниз.
BOS_DOWN = продолжение/подтверждение медвежьей структуры.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| structure_scope | enum | - | - | - | INTERNAL / EXTERNAL | scope | yes |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent | yes |
| confirm_bars | int | 1 | 3 | 1 | - | bars | yes |
| require_bias | enum | - | - | - | BEARISH / NOT_BULLISH | bias_rule | yes |

## PARAM_MEANING

```text
require_bias = BEARISH:
    BOS_DOWN разрешён только если до пробоя структура уже была bearish.

require_bias = NOT_BULLISH:
    BOS_DOWN разрешён если структура bearish или neutral.
```

## SIGNAL_RULE

```text
target_level = last_structure_low

BOS_DOWN_CLOSE:
    Close[1] <= target_level * (1 - break_buffer_pct / 100)

BOS_DOWN_CONFIRM:
    last confirm_bars closes are below target_level with buffer

IF require_bias = BEARISH:
    bias_condition = structure_bias = BEARISH_BIAS

IF require_bias = NOT_BULLISH:
    bias_condition = structure_bias = BEARISH_BIAS OR structure_bias = NEUTRAL_BIAS

IF BOS_DOWN_CONFIRM AND bias_condition:
    BOSDOWN_ALLOW = 1
    save last_structure_event = BOS_DOWN

ELSE:
    BOSDOWN_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F051_structure_scope
F051_break_buffer_pct
F051_confirm_bars
F051_require_bias
F051_BOSDOWN_ALLOW
```

## REGISTRY_ROW

```text
F051 | bos_down_flag_1m | BOSDOWN_ALLOW | MARKET_STRUCTURE | structure_scope(INTERNAL/EXTERNAL),break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1),require_bias(BEARISH/NOT_BULLISH) | output 1/0
```

---

# 8. F052 — choch_flag

```text
ID: F052
FEATURE: choch_flag_1m
ACTION: CHOCH_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## PURPOSE

```text
Разрешает вход при подтверждённой Change Of Character.
CHOCH = пробой структуры против текущего направления, потенциальная смена характера движения.
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| structure_scope | enum | - | - | - | INTERNAL / EXTERNAL | scope | yes |
| choch_dir | enum | - | - | - | BULLISH / BEARISH | direction | yes |
| break_buffer_pct | float | 0.00 | 1.00 | 0.01 | - | percent | yes |
| confirm_bars | int | 1 | 3 | 1 | - | bars | yes |
| require_opposite_bias | enum | - | - | - | YES / NO | bias_rule | yes |

## PARAM_MEANING

```text
choch_dir = BULLISH:
    смена характера вверх после bearish-структуры.

choch_dir = BEARISH:
    смена характера вниз после bullish-структуры.

require_opposite_bias = YES:
    CHOCH разрешён только если до события был противоположный тренд.

require_opposite_bias = NO:
    CHOCH разрешён как ранний structural shift даже из neutral state.
```

## SIGNAL_RULE

```text
BULLISH_CHOCH_TARGET:
    protected_high OR last_structure_high from bearish structure

BEARISH_CHOCH_TARGET:
    protected_low OR last_structure_low from bullish structure

BULLISH_CHOCH_CONFIRM:
    last confirm_bars closes >= BULLISH_CHOCH_TARGET * (1 + break_buffer_pct / 100)

BEARISH_CHOCH_CONFIRM:
    last confirm_bars closes <= BEARISH_CHOCH_TARGET * (1 - break_buffer_pct / 100)

IF choch_dir = BULLISH AND require_opposite_bias = YES:
    bias_condition = structure_bias = BEARISH_BIAS

IF choch_dir = BEARISH AND require_opposite_bias = YES:
    bias_condition = structure_bias = BULLISH_BIAS

IF require_opposite_bias = NO:
    bias_condition = TRUE

IF choch_dir = BULLISH AND BULLISH_CHOCH_CONFIRM AND bias_condition:
    CHOCH_ALLOW = 1
    save last_structure_event = BULLISH_CHOCH

ELSE IF choch_dir = BEARISH AND BEARISH_CHOCH_CONFIRM AND bias_condition:
    CHOCH_ALLOW = 1
    save last_structure_event = BEARISH_CHOCH

ELSE:
    CHOCH_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F052_structure_scope
F052_choch_dir
F052_break_buffer_pct
F052_confirm_bars
F052_require_opposite_bias
F052_CHOCH_ALLOW
```

## REGISTRY_ROW

```text
F052 | choch_flag_1m | CHOCH_ALLOW | MARKET_STRUCTURE | structure_scope(INTERNAL/EXTERNAL),choch_dir(BULLISH/BEARISH),break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1),require_opposite_bias(YES/NO) | output 1/0
```

---

# 9. EVENT MEMORY

```text
MARKET_STRUCTURE_MEMORY = ON

Runtime saves:
    current_structure_scope
    current_structure_bias
    last_structure_high
    last_structure_low
    protected_high
    protected_low
    last_structure_event
    last_structure_event_bar
```

## COMMENT_EVENT_MEMORY

```text
Без памяти структуры F052 CHOCH нельзя считать корректно.
CHOCH требует знания предыдущего направления структуры.
```

---

# 10. CALIBRATION_ORDER

```text
1. F050 bos_up_flag
2. F051 bos_down_flag
3. F052 choch_flag
```

## COMMENT_CALIBRATION_ORDER

```text
Сначала калибровать BOS_UP и BOS_DOWN.
Потом CHOCH, потому что CHOCH зависит от текущего structure_bias.
```

---

# 11. GLOBAL_NOT_CALIBRATED

```text
trade_side
tf
calc_method
price_source
high_low_source
confirmation_price
wick_break_policy
internal_engine_params
external_engine_params
swing_label_logic
structure_bias_logic
event_memory_fields
entry_exit
order_size
take_profit_order
stop_loss_order
```

---

# 12. REGISTRY_ROWS_SHORT

```text
F050 | bos_up_flag_1m | BOSUP_ALLOW | MARKET_STRUCTURE | structure_scope(INTERNAL/EXTERNAL),break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1),require_bias(BULLISH/NOT_BEARISH) | output 1/0

F051 | bos_down_flag_1m | BOSDOWN_ALLOW | MARKET_STRUCTURE | structure_scope(INTERNAL/EXTERNAL),break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1),require_bias(BEARISH/NOT_BULLISH) | output 1/0

F052 | choch_flag_1m | CHOCH_ALLOW | MARKET_STRUCTURE | structure_scope(INTERNAL/EXTERNAL),choch_dir(BULLISH/BEARISH),break_buffer_pct(0.00–1.00 step 0.01),confirm_bars(1–3 step 1),require_opposite_bias(YES/NO) | output 1/0
```
