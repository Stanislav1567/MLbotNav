# F022 — STRICT PASSPORT

```text
ID: F022
FEATURE: obv_slope_5_1m
ACTION: OBVSLOPE5_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

## 1. PURPOSE

```text
OBVSLOPE5_ALLOW разрешает или запрещает вход по направлению и силе наклона OBV за 5 закрытых 1m-свечей.
```

## 2. VELES_MAPPING

```text
FILTER_ANALOG: NONE
CUSTOM_CALC: YES
INTERVAL: 1 минута
TYPE: На закрытии бара
```

## 3. FIXED

```text
TF: 1m
CALC_METHOD: CLOSE_BAR
CANDLE: closed
PRICE_SOURCE: close
VOLUME_SOURCE: base_volume
SLOPE_BARS: 5
NORM_WINDOW: 20
UNIT: avg_volume_units
```

## 4. FORMULA

```text
IF Close[i] > Close[i + 1]:
    OBV[i] = OBV[i + 1] + Volume[i]

IF Close[i] < Close[i + 1]:
    OBV[i] = OBV[i + 1] - Volume[i]

IF Close[i] = Close[i + 1]:
    OBV[i] = OBV[i + 1]

obv_slope_5_raw = OBV[1] - OBV[6]

avg_volume_20 = SMA(Volume, 20)

obv_slope_5_norm = obv_slope_5_raw / avg_volume_20
```

## 5. DATA_GUARD

```text
IF avg_volume_20 <= 0:
    OBVSLOPE5_ALLOW = 0
```

## 6. CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| slope_dir | enum | - | - | - | UP / DOWN | direction | yes |
| slope_thr | float | 0.0 | 10.0 | 0.1 | - | avg_volume_units | yes |

## 7. PARAM_MEANING

```text
slope_dir = UP: разрешение при положительном наклоне OBV
slope_dir = DOWN: разрешение при отрицательном наклоне OBV

slope_thr: минимальная сила наклона OBV за 5 баров, выраженная в средних объёмах
```

## 8. SIGNAL_RULE

```text
IF slope_dir = UP AND obv_slope_5_norm >= slope_thr:
    OBVSLOPE5_ALLOW = 1
ELSE IF slope_dir = DOWN AND obv_slope_5_norm <= -slope_thr:
    OBVSLOPE5_ALLOW = 1
ELSE:
    OBVSLOPE5_ALLOW = 0
```

## 9. OUTPUT_MEANING

```text
OBVSLOPE5_ALLOW = 1: вход разрешён
OBVSLOPE5_ALLOW = 0: вход запрещён
```

## 10. CALIBRATION_OUTPUT_TO_RUNTIME

После калибровки передаются только откалиброванные параметры:

```text
F022_slope_dir
F022_slope_thr
```

В runtime рассчитывается:

```text
F022_OBVSLOPE5_ALLOW
```

## 11. SIDE_MODE

```text
LONG и SHORT калибруются отдельно внешним режимом Оптумно.
Внутри F022 сторона сделки не калибруется.
```

Для LONG-профиля сохраняются:

```text
F022_LONG_slope_dir
F022_LONG_slope_thr
```

Для SHORT-профиля сохраняются:

```text
F022_SHORT_slope_dir
F022_SHORT_slope_thr
```

## 12. NOT_CALIBRATED

```text
side
tf
calc_method
price_source
volume_source
slope_bars
norm_window
obv_start_value
entry_exit
order_size
stop_loss
take_profit
```

## 13. REGISTRY_ROW

```text
F022 | obv_slope_5_1m | OBVSLOPE5_ALLOW | ENTRY_FILTER | slope_dir(UP/DOWN),slope_thr(min=0.0,max=10.0,step=0.1) | fixed: TF=1m,SLOPE_BARS=5,NORM_WINDOW=20,CALC_METHOD=CLOSE_BAR,CUSTOM_CALC=YES | output: 1=ALLOW,0=BLOCK
```
