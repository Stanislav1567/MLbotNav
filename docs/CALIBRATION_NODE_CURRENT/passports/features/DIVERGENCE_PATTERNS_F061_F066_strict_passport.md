# DIVERGENCE PATTERNS — STRICT PASSPORT F061-F066 — V1

```text
FAMILY: DIVERGENCE_PATTERNS
FEATURES: F061-F066
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
NOT_EXIT_BLOCK: YES
```

---

# 0. PURPOSE

```text
F061-F066 проверяют дивергенции между ценой и индикатором.

F061 = bullish RSI divergence
F062 = bearish RSI divergence
F063 = bullish MACD divergence
F064 = bearish MACD divergence
F065 = bullish OBV divergence
F066 = bearish OBV divergence

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
REPAINT_POLICY = no_unconfirmed_pivot
CUSTOM_CALC = YES
```

## COMMENT_COMMON_FIXED

```text
Все дивергенции считаются только по закрытым свечам.
Текущая незакрытая свеча не используется.
Pivot считается подтверждённым только после закрытия PIVOT_RIGHT свечей.
```

---

# 2. PIVOT_SCOPE

```text
PIVOT_SCOPE:
    INTERNAL
    EXTERNAL
```

## INTERNAL_PIVOT_ENGINE

```text
INTERNAL_LOOKBACK = 120
INTERNAL_PIVOT_LEFT = 3
INTERNAL_PIVOT_RIGHT = 3
INTERNAL_MIN_PRICE_SWING_PCT = 0.10
```

## EXTERNAL_PIVOT_ENGINE

```text
EXTERNAL_LOOKBACK = 240
EXTERNAL_PIVOT_LEFT = 10
EXTERNAL_PIVOT_RIGHT = 10
EXTERNAL_MIN_PRICE_SWING_PCT = 0.30
```

## COMMENT_PIVOT_SCOPE

```text
PIVOT_SCOPE калибруется.
INTERNAL даёт больше сигналов, но больше шума.
EXTERNAL даёт меньше сигналов, но структура надёжнее.

Параметры pivot-движков не калибруются внутри F061-F066.
```

---

# 3. COMMON PIVOT DEFINITIONS

```text
price_pivot_low:
    Low[pivot] ниже соседних Low слева и справа по PIVOT_LEFT/PIVOT_RIGHT

price_pivot_high:
    High[pivot] выше соседних High слева и справа по PIVOT_LEFT/PIVOT_RIGHT

indicator_pivot_low:
    indicator[pivot] ниже соседних значений индикатора

indicator_pivot_high:
    indicator[pivot] выше соседних значений индикатора
```

## PIVOT_PAIR_RULE

```text
Для bullish divergence используются две последние подтверждённые price_pivot_low:
    price_low_A
    price_low_B

Для bearish divergence используются две последние подтверждённые price_pivot_high:
    price_high_A
    price_high_B

Индикатор берётся в тех же pivot-барах, что и цена.
```

## PIVOT_PAIR_DATA_GUARD

```text
IF no valid pivot pair:
    DIVERGENCE_ALLOW = 0

IF pivot_pair_gap_bars > max_pivot_gap_bars:
    DIVERGENCE_ALLOW = 0
```

---

# 4. DIVERGENCE TYPES

## REGULAR BULLISH

```text
price makes lower low
indicator makes higher low
```

## REGULAR BEARISH

```text
price makes higher high
indicator makes lower high
```

## HIDDEN BULLISH

```text
price makes higher low
indicator makes lower low
```

## HIDDEN BEARISH

```text
price makes lower high
indicator makes higher high
```

## COMMENT_DIVERGENCE_TYPES

```text
REGULAR дивергенция = возможный разворот.
HIDDEN дивергенция = возможное продолжение тренда.

div_type калибруется.
```

---

# 5. CONFIRMATION_MODE

```text
confirm_mode:
    NONE
    PRICE_REACTION
```

## PRICE_REACTION_CONFIRMATION

```text
Bullish confirmation:
    Close[1] >= pivot_B_close * (1 + reaction_confirm_pct / 100)

Bearish confirmation:
    Close[1] <= pivot_B_close * (1 - reaction_confirm_pct / 100)
```

## COMMENT_CONFIRMATION

```text
confirm_mode = NONE:
    ALLOW появляется сразу после подтверждённой pivot-дивергенции.

confirm_mode = PRICE_REACTION:
    ALLOW появляется только после реакции цены от второго pivot.
```

---

# 6. INDICATOR_FIXED

## RSI

```text
RSI_PERIOD = 14
RSI_SOURCE = Close
RSI_RANGE = 0..100
UNIT = rsi_points
```

## MACD

```text
MACD_FAST_EMA = 12
MACD_SLOW_EMA = 26
MACD_SIGNAL_EMA = 9
MACD_COMPONENTS = LINE / HIST
UNIT = percent_of_close

macd_line = EMA(Close,12) - EMA(Close,26)
macd_signal = EMA(macd_line,9)
macd_hist = macd_line - macd_signal

macd_line_pct = macd_line / Close[1] * 100
macd_hist_pct = macd_hist / Close[1] * 100
```

## OBV

```text
OBV_SOURCE = Close + Volume
OBV_NORM_WINDOW = 20
UNIT = avg_volume_units

IF Close[i] > Close[i+1]:
    OBV[i] = OBV[i+1] + Volume[i]

IF Close[i] < Close[i+1]:
    OBV[i] = OBV[i+1] - Volume[i]

IF Close[i] = Close[i+1]:
    OBV[i] = OBV[i+1]

obv_norm = OBV / SMA(Volume,20)
```

---

# 7. F061 — rsi_bull_div_flag

```text
ID: F061
FEATURE: rsi_bull_div_flag_1m
ACTION: RSIBULLDIV_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| pivot_scope | enum | - | - | - | INTERNAL / EXTERNAL | scope | yes |
| div_type | enum | - | - | - | REGULAR / HIDDEN | divergence_type | yes |
| price_delta_min_pct | float | 0.05 | 3.00 | 0.05 | - | percent | yes |
| rsi_delta_min | int | 1 | 30 | 1 | - | rsi_points | yes |
| max_pivot_gap_bars | int | 5 | 120 | 5 | - | bars | yes |
| confirm_mode | enum | - | - | - | NONE / PRICE_REACTION | confirmation | yes |
| reaction_confirm_pct | float | 0.00 | 1.00 | 0.05 | - | percent | conditional |

## SIGNAL_RULE

```text
REGULAR_BULLISH:
    price_low_B <= price_low_A * (1 - price_delta_min_pct / 100)
    AND rsi_B >= rsi_A + rsi_delta_min

HIDDEN_BULLISH:
    price_low_B >= price_low_A * (1 + price_delta_min_pct / 100)
    AND rsi_B <= rsi_A - rsi_delta_min

CONFIRM_OK:
    confirm_mode = NONE
    OR Close[1] >= pivot_B_close * (1 + reaction_confirm_pct / 100)

IF div_type = REGULAR AND REGULAR_BULLISH AND CONFIRM_OK:
    RSIBULLDIV_ALLOW = 1

ELSE IF div_type = HIDDEN AND HIDDEN_BULLISH AND CONFIRM_OK:
    RSIBULLDIV_ALLOW = 1

ELSE:
    RSIBULLDIV_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F061_pivot_scope
F061_div_type
F061_price_delta_min_pct
F061_rsi_delta_min
F061_max_pivot_gap_bars
F061_confirm_mode
F061_reaction_confirm_pct
F061_RSIBULLDIV_ALLOW
```

## REGISTRY_ROW

```text
F061 | rsi_bull_div_flag_1m | RSIBULLDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),price_delta_min_pct(0.05–3.00 step 0.05),rsi_delta_min(1–30 step 1),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0
```

---

# 8. F062 — rsi_bear_div_flag

```text
ID: F062
FEATURE: rsi_bear_div_flag_1m
ACTION: RSIBEARDIV_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| pivot_scope | enum | - | - | - | INTERNAL / EXTERNAL | scope | yes |
| div_type | enum | - | - | - | REGULAR / HIDDEN | divergence_type | yes |
| price_delta_min_pct | float | 0.05 | 3.00 | 0.05 | - | percent | yes |
| rsi_delta_min | int | 1 | 30 | 1 | - | rsi_points | yes |
| max_pivot_gap_bars | int | 5 | 120 | 5 | - | bars | yes |
| confirm_mode | enum | - | - | - | NONE / PRICE_REACTION | confirmation | yes |
| reaction_confirm_pct | float | 0.00 | 1.00 | 0.05 | - | percent | conditional |

## SIGNAL_RULE

```text
REGULAR_BEARISH:
    price_high_B >= price_high_A * (1 + price_delta_min_pct / 100)
    AND rsi_B <= rsi_A - rsi_delta_min

HIDDEN_BEARISH:
    price_high_B <= price_high_A * (1 - price_delta_min_pct / 100)
    AND rsi_B >= rsi_A + rsi_delta_min

CONFIRM_OK:
    confirm_mode = NONE
    OR Close[1] <= pivot_B_close * (1 - reaction_confirm_pct / 100)

IF div_type = REGULAR AND REGULAR_BEARISH AND CONFIRM_OK:
    RSIBEARDIV_ALLOW = 1

ELSE IF div_type = HIDDEN AND HIDDEN_BEARISH AND CONFIRM_OK:
    RSIBEARDIV_ALLOW = 1

ELSE:
    RSIBEARDIV_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F062_pivot_scope
F062_div_type
F062_price_delta_min_pct
F062_rsi_delta_min
F062_max_pivot_gap_bars
F062_confirm_mode
F062_reaction_confirm_pct
F062_RSIBEARDIV_ALLOW
```

## REGISTRY_ROW

```text
F062 | rsi_bear_div_flag_1m | RSIBEARDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),price_delta_min_pct(0.05–3.00 step 0.05),rsi_delta_min(1–30 step 1),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0
```

---

# 9. F063 — macd_bull_div_flag

```text
ID: F063
FEATURE: macd_bull_div_flag_1m
ACTION: MACDBULLDIV_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| pivot_scope | enum | - | - | - | INTERNAL / EXTERNAL | scope | yes |
| div_type | enum | - | - | - | REGULAR / HIDDEN | divergence_type | yes |
| macd_component | enum | - | - | - | LINE / HIST | macd_component | yes |
| price_delta_min_pct | float | 0.05 | 3.00 | 0.05 | - | percent | yes |
| macd_delta_min_pct | float | 0.00 | 0.50 | 0.01 | - | percent_of_close | yes |
| max_pivot_gap_bars | int | 5 | 120 | 5 | - | bars | yes |
| confirm_mode | enum | - | - | - | NONE / PRICE_REACTION | confirmation | yes |
| reaction_confirm_pct | float | 0.00 | 1.00 | 0.05 | - | percent | conditional |

## SIGNAL_RULE

```text
macd_value = macd_line_pct IF macd_component = LINE
macd_value = macd_hist_pct IF macd_component = HIST

REGULAR_BULLISH:
    price_low_B <= price_low_A * (1 - price_delta_min_pct / 100)
    AND macd_B >= macd_A + macd_delta_min_pct

HIDDEN_BULLISH:
    price_low_B >= price_low_A * (1 + price_delta_min_pct / 100)
    AND macd_B <= macd_A - macd_delta_min_pct

CONFIRM_OK:
    confirm_mode = NONE
    OR Close[1] >= pivot_B_close * (1 + reaction_confirm_pct / 100)

IF div_type = REGULAR AND REGULAR_BULLISH AND CONFIRM_OK:
    MACDBULLDIV_ALLOW = 1

ELSE IF div_type = HIDDEN AND HIDDEN_BULLISH AND CONFIRM_OK:
    MACDBULLDIV_ALLOW = 1

ELSE:
    MACDBULLDIV_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F063_pivot_scope
F063_div_type
F063_macd_component
F063_price_delta_min_pct
F063_macd_delta_min_pct
F063_max_pivot_gap_bars
F063_confirm_mode
F063_reaction_confirm_pct
F063_MACDBULLDIV_ALLOW
```

## REGISTRY_ROW

```text
F063 | macd_bull_div_flag_1m | MACDBULLDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),macd_component(LINE/HIST),price_delta_min_pct(0.05–3.00 step 0.05),macd_delta_min_pct(0.00–0.50 step 0.01),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0
```

---

# 10. F064 — macd_bear_div_flag

```text
ID: F064
FEATURE: macd_bear_div_flag_1m
ACTION: MACDBEARDIV_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| pivot_scope | enum | - | - | - | INTERNAL / EXTERNAL | scope | yes |
| div_type | enum | - | - | - | REGULAR / HIDDEN | divergence_type | yes |
| macd_component | enum | - | - | - | LINE / HIST | macd_component | yes |
| price_delta_min_pct | float | 0.05 | 3.00 | 0.05 | - | percent | yes |
| macd_delta_min_pct | float | 0.00 | 0.50 | 0.01 | - | percent_of_close | yes |
| max_pivot_gap_bars | int | 5 | 120 | 5 | - | bars | yes |
| confirm_mode | enum | - | - | - | NONE / PRICE_REACTION | confirmation | yes |
| reaction_confirm_pct | float | 0.00 | 1.00 | 0.05 | - | percent | conditional |

## SIGNAL_RULE

```text
macd_value = macd_line_pct IF macd_component = LINE
macd_value = macd_hist_pct IF macd_component = HIST

REGULAR_BEARISH:
    price_high_B >= price_high_A * (1 + price_delta_min_pct / 100)
    AND macd_B <= macd_A - macd_delta_min_pct

HIDDEN_BEARISH:
    price_high_B <= price_high_A * (1 - price_delta_min_pct / 100)
    AND macd_B >= macd_A + macd_delta_min_pct

CONFIRM_OK:
    confirm_mode = NONE
    OR Close[1] <= pivot_B_close * (1 - reaction_confirm_pct / 100)

IF div_type = REGULAR AND REGULAR_BEARISH AND CONFIRM_OK:
    MACDBEARDIV_ALLOW = 1

ELSE IF div_type = HIDDEN AND HIDDEN_BEARISH AND CONFIRM_OK:
    MACDBEARDIV_ALLOW = 1

ELSE:
    MACDBEARDIV_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F064_pivot_scope
F064_div_type
F064_macd_component
F064_price_delta_min_pct
F064_macd_delta_min_pct
F064_max_pivot_gap_bars
F064_confirm_mode
F064_reaction_confirm_pct
F064_MACDBEARDIV_ALLOW
```

## REGISTRY_ROW

```text
F064 | macd_bear_div_flag_1m | MACDBEARDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),macd_component(LINE/HIST),price_delta_min_pct(0.05–3.00 step 0.05),macd_delta_min_pct(0.00–0.50 step 0.01),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0
```

---

# 11. F065 — obv_bull_div_flag

```text
ID: F065
FEATURE: obv_bull_div_flag_1m
ACTION: OBVBULLDIV_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## DATA_GUARD

```text
IF SMA(Volume,20) <= 0:
    OBVBULLDIV_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| pivot_scope | enum | - | - | - | INTERNAL / EXTERNAL | scope | yes |
| div_type | enum | - | - | - | REGULAR / HIDDEN | divergence_type | yes |
| price_delta_min_pct | float | 0.05 | 3.00 | 0.05 | - | percent | yes |
| obv_delta_min_norm | float | 0.5 | 20.0 | 0.5 | - | avg_volume_units | yes |
| max_pivot_gap_bars | int | 5 | 120 | 5 | - | bars | yes |
| confirm_mode | enum | - | - | - | NONE / PRICE_REACTION | confirmation | yes |
| reaction_confirm_pct | float | 0.00 | 1.00 | 0.05 | - | percent | conditional |

## SIGNAL_RULE

```text
REGULAR_BULLISH:
    price_low_B <= price_low_A * (1 - price_delta_min_pct / 100)
    AND obv_norm_B >= obv_norm_A + obv_delta_min_norm

HIDDEN_BULLISH:
    price_low_B >= price_low_A * (1 + price_delta_min_pct / 100)
    AND obv_norm_B <= obv_norm_A - obv_delta_min_norm

CONFIRM_OK:
    confirm_mode = NONE
    OR Close[1] >= pivot_B_close * (1 + reaction_confirm_pct / 100)

IF div_type = REGULAR AND REGULAR_BULLISH AND CONFIRM_OK:
    OBVBULLDIV_ALLOW = 1

ELSE IF div_type = HIDDEN AND HIDDEN_BULLISH AND CONFIRM_OK:
    OBVBULLDIV_ALLOW = 1

ELSE:
    OBVBULLDIV_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F065_pivot_scope
F065_div_type
F065_price_delta_min_pct
F065_obv_delta_min_norm
F065_max_pivot_gap_bars
F065_confirm_mode
F065_reaction_confirm_pct
F065_OBVBULLDIV_ALLOW
```

## REGISTRY_ROW

```text
F065 | obv_bull_div_flag_1m | OBVBULLDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),price_delta_min_pct(0.05–3.00 step 0.05),obv_delta_min_norm(0.5–20.0 step 0.5),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0
```

---

# 12. F066 — obv_bear_div_flag

```text
ID: F066
FEATURE: obv_bear_div_flag_1m
ACTION: OBVBEARDIV_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
```

## DATA_GUARD

```text
IF SMA(Volume,20) <= 0:
    OBVBEARDIV_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| pivot_scope | enum | - | - | - | INTERNAL / EXTERNAL | scope | yes |
| div_type | enum | - | - | - | REGULAR / HIDDEN | divergence_type | yes |
| price_delta_min_pct | float | 0.05 | 3.00 | 0.05 | - | percent | yes |
| obv_delta_min_norm | float | 0.5 | 20.0 | 0.5 | - | avg_volume_units | yes |
| max_pivot_gap_bars | int | 5 | 120 | 5 | - | bars | yes |
| confirm_mode | enum | - | - | - | NONE / PRICE_REACTION | confirmation | yes |
| reaction_confirm_pct | float | 0.00 | 1.00 | 0.05 | - | percent | conditional |

## SIGNAL_RULE

```text
REGULAR_BEARISH:
    price_high_B >= price_high_A * (1 + price_delta_min_pct / 100)
    AND obv_norm_B <= obv_norm_A - obv_delta_min_norm

HIDDEN_BEARISH:
    price_high_B <= price_high_A * (1 - price_delta_min_pct / 100)
    AND obv_norm_B >= obv_norm_A + obv_delta_min_norm

CONFIRM_OK:
    confirm_mode = NONE
    OR Close[1] <= pivot_B_close * (1 - reaction_confirm_pct / 100)

IF div_type = REGULAR AND REGULAR_BEARISH AND CONFIRM_OK:
    OBVBEARDIV_ALLOW = 1

ELSE IF div_type = HIDDEN AND HIDDEN_BEARISH AND CONFIRM_OK:
    OBVBEARDIV_ALLOW = 1

ELSE:
    OBVBEARDIV_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F066_pivot_scope
F066_div_type
F066_price_delta_min_pct
F066_obv_delta_min_norm
F066_max_pivot_gap_bars
F066_confirm_mode
F066_reaction_confirm_pct
F066_OBVBEARDIV_ALLOW
```

## REGISTRY_ROW

```text
F066 | obv_bear_div_flag_1m | OBVBEARDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),price_delta_min_pct(0.05–3.00 step 0.05),obv_delta_min_norm(0.5–20.0 step 0.5),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0
```

---

# 13. CALIBRATION_ORDER

```text
1. F061 rsi_bull_div_flag
2. F062 rsi_bear_div_flag
3. F063 macd_bull_div_flag
4. F064 macd_bear_div_flag
5. F065 obv_bull_div_flag
6. F066 obv_bear_div_flag
```

## COMMENT_CALIBRATION_ORDER

```text
Сначала калибровать RSI-дивергенции.
Потом MACD-дивергенции.
Потом OBV-дивергенции.

RSI и MACD обычно проще валидировать визуально.
OBV зависит от качества данных по объёму и требует нормализации.
```

---

# 14. GLOBAL_NOT_CALIBRATED

```text
side
tf
calc_method
price_source
high_low_source
unconfirmed_pivots
rsi_period
macd_fast_ema
macd_slow_ema
macd_signal_ema
obv_formula
obv_norm_window
pivot_engine_params
entry_exit
order_size
take_profit_order
stop_loss_order
```

---

# 15. REGISTRY_ROWS_SHORT

```text
F061 | rsi_bull_div_flag_1m | RSIBULLDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),price_delta_min_pct(0.05–3.00 step 0.05),rsi_delta_min(1–30 step 1),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0

F062 | rsi_bear_div_flag_1m | RSIBEARDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),price_delta_min_pct(0.05–3.00 step 0.05),rsi_delta_min(1–30 step 1),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0

F063 | macd_bull_div_flag_1m | MACDBULLDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),macd_component(LINE/HIST),price_delta_min_pct(0.05–3.00 step 0.05),macd_delta_min_pct(0.00–0.50 step 0.01),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0

F064 | macd_bear_div_flag_1m | MACDBEARDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),macd_component(LINE/HIST),price_delta_min_pct(0.05–3.00 step 0.05),macd_delta_min_pct(0.00–0.50 step 0.01),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0

F065 | obv_bull_div_flag_1m | OBVBULLDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),price_delta_min_pct(0.05–3.00 step 0.05),obv_delta_min_norm(0.5–20.0 step 0.5),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0

F066 | obv_bear_div_flag_1m | OBVBEARDIV_ALLOW | DIVERGENCE_PATTERNS | pivot_scope(INTERNAL/EXTERNAL),div_type(REGULAR/HIDDEN),price_delta_min_pct(0.05–3.00 step 0.05),obv_delta_min_norm(0.5–20.0 step 0.5),max_pivot_gap_bars(5–120 step 5),confirm_mode(NONE/PRICE_REACTION),reaction_confirm_pct(0.00–1.00 step 0.05) | output 1/0
```
