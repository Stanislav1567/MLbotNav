# STOCHASTIC FAMILY — COMBINED STRICT PASSPORT F017-F018

```text
ID_GROUP: F017_F018
COMPONENTS:
    F017: stoch_k14_1m
    F018: stoch_d14_1m
FEATURE: stochastic_14_1m
ACTION: STOCH14_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

## 1. PURPOSE

```text
STOCH14_ALLOW разрешает или запрещает вход по Stochastic(14) на 1m.
Внутри одного паспорта используются две линии:
F017 = %K
F018 = %D
```

## 2. VELES_MAPPING

```text
FILTER: Stochastic
VARIANTS:
    Stochastic %K
    Stochastic %D
FILTER_TYPES:
    Пересечение линий
    Уровни перекупленности/перепроданности
INTERVAL: 1 минута
TYPE: На закрытии бара
SHIFT: 0
```

## 3. FIXED_COMMON

```text
TF: 1m
CALC_METHOD: CLOSE_BAR
CANDLE: closed
PRICE_SOURCE: high_low_close
STOCH_PERIOD: 14
SMOOTH_K: 1
SMOOTH_D: 3
SHIFT: 0
RANGE: 0..100
UNIT: stoch_points
```

## 4. FORMULA_COMMON

```text
raw_k14 = 100 * (Close[1] - LowestLow(14)) / (HighestHigh(14) - LowestLow(14))

stoch_k14 = SMA(raw_k14, SMOOTH_K)
stoch_d14 = SMA(stoch_k14, SMOOTH_D)
```

## 5. SIGNAL_MODE

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| signal_mode | enum | - | - | - | LEVEL / KD_CROSS | mode | yes |

---

# MODE 1 — LEVEL

## 6. LEVEL_CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| line | enum | - | - | - | K / D | stoch_line | yes |
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| level | int | 10 | 90 | 1 | - | stoch_points | yes |

## 7. LEVEL_SIGNAL_RULE

```text
IF signal_mode = LEVEL AND line = K AND cmp = GREATER AND stoch_k14 >= level:
    STOCH14_ALLOW = 1
ELSE IF signal_mode = LEVEL AND line = K AND cmp = LESS AND stoch_k14 <= level:
    STOCH14_ALLOW = 1
ELSE IF signal_mode = LEVEL AND line = D AND cmp = GREATER AND stoch_d14 >= level:
    STOCH14_ALLOW = 1
ELSE IF signal_mode = LEVEL AND line = D AND cmp = LESS AND stoch_d14 <= level:
    STOCH14_ALLOW = 1
ELSE:
    STOCH14_ALLOW = 0
```

---

# MODE 2 — KD_CROSS

## 8. KD_CROSS_CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cross_dir | enum | - | - | - | UP / DOWN | cross_direction | yes |
| zone_filter | enum | - | - | - | NONE / LOW / HIGH | zone_mode | yes |
| low_level | int | 10 | 40 | 1 | - | stoch_points | conditional |
| high_level | int | 60 | 90 | 1 | - | stoch_points | conditional |
| gap | int | 0 | 10 | 1 | - | stoch_points | yes |

## 9. KD_CROSS_BASE_RULE

```text
CROSS_UP:
    stoch_k14[2] <= stoch_d14[2]
    AND stoch_k14[1] >= stoch_d14[1] + gap

CROSS_DOWN:
    stoch_k14[2] >= stoch_d14[2]
    AND stoch_k14[1] <= stoch_d14[1] - gap
```

## 10. KD_CROSS_ZONE_RULE

```text
zone_filter = NONE:
    no zone condition

zone_filter = LOW:
    stoch_k14[2] <= low_level
    AND stoch_d14[2] <= low_level

zone_filter = HIGH:
    stoch_k14[2] >= high_level
    AND stoch_d14[2] >= high_level
```

## 11. KD_CROSS_SIGNAL_RULE

```text
IF signal_mode = KD_CROSS AND cross_dir = UP AND CROSS_UP AND zone_condition = TRUE:
    STOCH14_ALLOW = 1
ELSE IF signal_mode = KD_CROSS AND cross_dir = DOWN AND CROSS_DOWN AND zone_condition = TRUE:
    STOCH14_ALLOW = 1
ELSE:
    STOCH14_ALLOW = 0
```

---

## 12. OUTPUT_MEANING

```text
STOCH14_ALLOW = 1: вход разрешён
STOCH14_ALLOW = 0: вход запрещён
```

## 13. CALIBRATION_OUTPUT_TO_RUNTIME

После калибровки передаются только параметры выбранного режима.

```text
F017_F018_signal_mode
```

Если выбран LEVEL:

```text
F017_F018_line
F017_F018_cmp
F017_F018_level
```

Если выбран KD_CROSS:

```text
F017_F018_cross_dir
F017_F018_zone_filter
F017_F018_low_level
F017_F018_high_level
F017_F018_gap
```

В runtime рассчитывается:

```text
F017_F018_STOCH14_ALLOW
```

## 14. SIDE_MODE

```text
LONG и SHORT калибруются отдельно внешним режимом Оптумно.
Внутри F017_F018 сторона сделки не калибруется.
```

Для LONG-профиля сохраняются:

```text
F017_F018_LONG_signal_mode
F017_F018_LONG_line
F017_F018_LONG_cmp
F017_F018_LONG_level
F017_F018_LONG_cross_dir
F017_F018_LONG_zone_filter
F017_F018_LONG_low_level
F017_F018_LONG_high_level
F017_F018_LONG_gap
```

Для SHORT-профиля сохраняются:

```text
F017_F018_SHORT_signal_mode
F017_F018_SHORT_line
F017_F018_SHORT_cmp
F017_F018_SHORT_level
F017_F018_SHORT_cross_dir
F017_F018_SHORT_zone_filter
F017_F018_SHORT_low_level
F017_F018_SHORT_high_level
F017_F018_SHORT_gap
```

## 15. NOT_CALIBRATED

```text
side
tf
stoch_period
smooth_k
smooth_d
shift
calc_method
price_source
entry_exit
order_size
stop_loss
take_profit
```

## 16. REGISTRY_ROW

```text
F017_F018 | stochastic_14_1m | STOCH14_ALLOW | ENTRY_FILTER | signal_mode(LEVEL/KD_CROSS); LEVEL: line(K/D),cmp(GREATER/LESS),level(min=10,max=90,step=1); KD_CROSS: cross_dir(UP/DOWN),zone_filter(NONE/LOW/HIGH),low_level(min=10,max=40,step=1),high_level(min=60,max=90,step=1),gap(min=0,max=10,step=1) | fixed: TF=1m,STOCH_PERIOD=14,SMOOTH_K=1,SMOOTH_D=3,CALC_METHOD=CLOSE_BAR | output: 1=ALLOW,0=BLOCK
```
