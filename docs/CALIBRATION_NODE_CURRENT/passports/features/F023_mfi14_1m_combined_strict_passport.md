# F023 — MFI14 COMBINED STRICT PASSPORT

```text
ID: F023
FEATURE: mfi14_1m
ACTION: MFI14_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

## 1. PURPOSE

```text
MFI14_ALLOW разрешает или запрещает вход по Money Flow Index MFI(14) на 1m.
MFI учитывает цену и объём.
```

## 2. VELES_MAPPING

```text
FILTER: MFI
INTERVAL: 1 минута
PERIOD: 14
CONDITION: Больше / Меньше
VALUE_UNIT: mfi_points
TYPE: На закрытии бара
SHIFT: 0
```

## 3. FIXED_COMMON

```text
TF: 1m
CALC_METHOD: CLOSE_BAR
CANDLE: closed
PRICE_SOURCE: typical_price
VOLUME_SOURCE: base_volume
MFI_PERIOD: 14
SHIFT: 0
MFI_RANGE: 0..100
UNIT: mfi_points
```

## 4. FORMULA

```text
typical_price[i] = (High[i] + Low[i] + Close[i]) / 3

raw_money_flow[i] = typical_price[i] * Volume[i]

positive_flow[i] = raw_money_flow[i], IF typical_price[i] > typical_price[i + 1]
negative_flow[i] = raw_money_flow[i], IF typical_price[i] < typical_price[i + 1]

positive_sum_14 = SUM(positive_flow, 14)
negative_sum_14 = SUM(negative_flow, 14)

money_flow_ratio = positive_sum_14 / negative_sum_14

mfi14 = 100 - (100 / (1 + money_flow_ratio))
```

## 5. DATA_GUARD

```text
IF positive_sum_14 = 0 AND negative_sum_14 = 0:
    mfi14 = 50

IF positive_sum_14 > 0 AND negative_sum_14 = 0:
    mfi14 = 100

IF positive_sum_14 = 0 AND negative_sum_14 > 0:
    mfi14 = 0
```

## 6. SIGNAL_MODE

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| signal_mode | enum | - | - | - | LEVEL / CROSS_LEVEL | mode | yes |

---

# MODE 1 — LEVEL

## 7. LEVEL_CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| level | int | 10 | 90 | 1 | - | mfi_points | yes |

## 8. LEVEL_SIGNAL_RULE

```text
IF signal_mode = LEVEL AND cmp = GREATER AND mfi14 >= level:
    MFI14_ALLOW = 1
ELSE IF signal_mode = LEVEL AND cmp = LESS AND mfi14 <= level:
    MFI14_ALLOW = 1
ELSE:
    MFI14_ALLOW = 0
```

---

# MODE 2 — CROSS_LEVEL

## 9. CROSS_LEVEL_CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cross_dir | enum | - | - | - | UP / DOWN | cross_direction | yes |
| cross_level | int | 10 | 90 | 1 | - | mfi_points | yes |

## 10. CROSS_LEVEL_SIGNAL_RULE

```text
IF signal_mode = CROSS_LEVEL AND cross_dir = UP AND mfi14[2] < cross_level AND mfi14[1] >= cross_level:
    MFI14_ALLOW = 1
ELSE IF signal_mode = CROSS_LEVEL AND cross_dir = DOWN AND mfi14[2] > cross_level AND mfi14[1] <= cross_level:
    MFI14_ALLOW = 1
ELSE:
    MFI14_ALLOW = 0
```

---

## 11. OUTPUT_MEANING

```text
MFI14_ALLOW = 1: вход разрешён
MFI14_ALLOW = 0: вход запрещён
```

## 12. CALIBRATION_OUTPUT_TO_RUNTIME

После калибровки передаются только параметры выбранного режима.

```text
F023_signal_mode
```

Если выбран LEVEL:

```text
F023_cmp
F023_level
```

Если выбран CROSS_LEVEL:

```text
F023_cross_dir
F023_cross_level
```

В runtime рассчитывается:

```text
F023_MFI14_ALLOW
```

## 13. SIDE_MODE

```text
LONG и SHORT калибруются отдельно внешним режимом Оптумно.
Внутри F023 сторона сделки не калибруется.
```

Для LONG-профиля сохраняются:

```text
F023_LONG_signal_mode
F023_LONG_cmp
F023_LONG_level
F023_LONG_cross_dir
F023_LONG_cross_level
```

Для SHORT-профиля сохраняются:

```text
F023_SHORT_signal_mode
F023_SHORT_cmp
F023_SHORT_level
F023_SHORT_cross_dir
F023_SHORT_cross_level
```

## 14. NOT_CALIBRATED

```text
side
tf
mfi_period
shift
calc_method
price_source
volume_source
entry_exit
order_size
stop_loss
take_profit
```

## 15. REGISTRY_ROW

```text
F023 | mfi14_1m | MFI14_ALLOW | ENTRY_FILTER | signal_mode(LEVEL/CROSS_LEVEL); LEVEL: cmp(GREATER/LESS),level(min=10,max=90,step=1); CROSS_LEVEL: cross_dir(UP/DOWN),cross_level(min=10,max=90,step=1) | fixed: TF=1m,MFI_PERIOD=14,CALC_METHOD=CLOSE_BAR,SHIFT=0 | output: 1=ALLOW,0=BLOCK
```
