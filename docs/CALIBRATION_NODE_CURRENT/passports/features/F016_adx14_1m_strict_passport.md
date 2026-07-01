# F016 — STRICT PASSPORT

```text
ID: F016
FEATURE: adx14_1m
ACTION: ADX14_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

## 1. PURPOSE

```text
ADX14_ALLOW разрешает или запрещает вход по силе тренда ADX(14) на 1m.
ADX не определяет направление сделки.
```

## 2. VELES_MAPPING

```text
FILTER: ADX
INTERVAL: 1 минута
PERIOD: 14
SMOOTHING: 14
CONDITION: Больше / Меньше
VALUE_UNIT: adx_points
TYPE: На закрытии бара
SHIFT: 0
```

## 3. FIXED

```text
TF: 1m
CALC_METHOD: CLOSE_BAR
CANDLE: closed
PRICE_SOURCE: high_low_close
ADX_PERIOD: 14
ADX_SMOOTHING: 14
SHIFT: 0
ADX_RANGE: 0..100
UNIT: adx_points
```

## 4. CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| level | int | 5 | 60 | 1 | - | adx_points | yes |

## 5. PARAM_MEANING

```text
cmp = GREATER: разрешение при сильном тренде
cmp = LESS: разрешение при слабом тренде / флэте

level: порог ADX(14)
```

## 6. SIGNAL_RULE

```text
IF cmp = GREATER AND adx14 >= level:
    ADX14_ALLOW = 1
ELSE IF cmp = LESS AND adx14 <= level:
    ADX14_ALLOW = 1
ELSE:
    ADX14_ALLOW = 0
```

## 7. OUTPUT_MEANING

```text
ADX14_ALLOW = 1: вход разрешён
ADX14_ALLOW = 0: вход запрещён
```

## 8. CALIBRATION_OUTPUT_TO_RUNTIME

После калибровки передаются только откалиброванные параметры:

```text
F016_cmp
F016_level
```

В runtime рассчитывается:

```text
F016_ADX14_ALLOW
```

## 9. SIDE_MODE

```text
LONG и SHORT калибруются отдельно внешним режимом Оптумно.
Внутри F016 сторона сделки не калибруется.
```

Для LONG-профиля сохраняются:

```text
F016_LONG_cmp
F016_LONG_level
```

Для SHORT-профиля сохраняются:

```text
F016_SHORT_cmp
F016_SHORT_level
```

## 10. NOT_CALIBRATED

```text
side
tf
adx_period
adx_smoothing
shift
calc_method
price_source
plus_di
minus_di
trend_direction
entry_exit
order_size
stop_loss
take_profit
```

## 11. REGISTRY_ROW

```text
F016 | adx14_1m | ADX14_ALLOW | ENTRY_FILTER | cmp(GREATER/LESS), level(min=5,max=60,step=1) | fixed: TF=1m,ADX_PERIOD=14,SMOOTHING=14,CALC_METHOD=CLOSE_BAR,SHIFT=0 | output: 1=ALLOW,0=BLOCK
```
