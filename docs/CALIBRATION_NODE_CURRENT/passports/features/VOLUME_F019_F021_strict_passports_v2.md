# VOLUME FAMILY — STRICT PASSPORTS F019-F021 — V2

## FAMILY

```text
FEATURE_FAMILY: VOLUME
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
TF: 1m
CALC_METHOD: CLOSE_BAR
CANDLE: closed
STATUS: ACTIVE
```

## OUTPUT_MEANING

```text
1 = вход разрешён
0 = вход запрещён
```

---

# F019 — vol_chg

```text
ID: F019
FEATURE: vol_chg_1m
ACTION: VOLCHG_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

## FIXED

```text
TF: 1m
CALC_METHOD: CLOSE_BAR
CANDLE: closed
VOLUME_SOURCE: base_volume
UNIT: percent
FORMULA: vol_chg_pct = (Volume[1] / Volume[2] - 1) * 100
```

## DATA_GUARD

```text
IF Volume[2] <= 0:
    VOLCHG_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| direction | enum | - | - | - | UP / DOWN | volume_direction | yes |
| thr_pct | float | 5 | 300 | 5 | - | percent | yes |

## SIGNAL_RULE

```text
IF direction = UP AND vol_chg_pct >= thr_pct:
    VOLCHG_ALLOW = 1
ELSE IF direction = DOWN AND vol_chg_pct <= -thr_pct:
    VOLCHG_ALLOW = 1
ELSE:
    VOLCHG_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F019_direction
F019_thr_pct
F019_VOLCHG_ALLOW
```

## REGISTRY_ROW

```text
F019 | vol_chg_1m | VOLCHG_ALLOW | ENTRY_FILTER | direction(UP/DOWN),thr_pct(min=5,max=300,step=5) | fixed: TF=1m,CALC_METHOD=CLOSE_BAR,VOLUME_SOURCE=base_volume | output: 1=ALLOW,0=BLOCK
```

---

# F020 — vol_z

```text
ID: F020
FEATURE: vol_z_20_1m
ACTION: VOLZ20_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

## FIXED

```text
TF: 1m
CALC_METHOD: CLOSE_BAR
CANDLE: closed
VOLUME_SOURCE: base_volume
Z_WINDOW: 20
STD_METHOD: population
UNIT: z_score
FORMULA: vol_z_20 = (Volume[1] - SMA(Volume,20)) / STD(Volume,20)
```

## DATA_GUARD

```text
IF STD(Volume,20) <= 0:
    VOLZ20_ALLOW = 0
```

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| state | enum | - | - | - | HIGH / LOW | volume_state | yes |
| z_level | float | 0.0 | 5.0 | 0.1 | - | z_score | yes |

## SIGNAL_RULE

```text
IF state = HIGH AND vol_z_20 >= z_level:
    VOLZ20_ALLOW = 1
ELSE IF state = LOW AND vol_z_20 <= -z_level:
    VOLZ20_ALLOW = 1
ELSE:
    VOLZ20_ALLOW = 0
```

## RUNTIME_PARAMS

```text
F020_state
F020_z_level
F020_VOLZ20_ALLOW
```

## REGISTRY_ROW

```text
F020 | vol_z_20_1m | VOLZ20_ALLOW | ENTRY_FILTER | state(HIGH/LOW),z_level(min=0.0,max=5.0,step=0.1) | fixed: TF=1m,Z_WINDOW=20,CALC_METHOD=CLOSE_BAR,VOLUME_SOURCE=base_volume | output: 1=ALLOW,0=BLOCK
```

---

# F021 — delta_volume

```text
ID: F021
FEATURE: delta_volume_1m
ACTION: DELTAVOL_ALLOW
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
```

## PURPOSE

```text
DELTAVOL_ALLOW разрешает или запрещает вход по дельте объёма последней закрытой 1m-свечи.
```

## FIXED_COMMON

```text
TF: 1m
CALC_METHOD: CLOSE_BAR
CANDLE: closed
UNIT: percent
```

## DELTA_MODE

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| delta_mode | enum | - | - | - | TRUE_DELTA / PROXY_DELTA | source_mode | yes |

---

## MODE 1 — TRUE_DELTA

### DATA_REQUIREMENT

```text
BuyVolume[1]
SellVolume[1]
```

### FORMULA

```text
total_side_volume = BuyVolume[1] + SellVolume[1]
delta_volume_pct = ((BuyVolume[1] - SellVolume[1]) / total_side_volume) * 100
```

### DATA_GUARD

```text
IF total_side_volume <= 0:
    DELTAVOL_ALLOW = 0
```

---

## MODE 2 — PROXY_DELTA

### DATA_REQUIREMENT

```text
Open[1]
High[1]
Low[1]
Close[1]
Volume[1]
```

### FORMULA

```text
range = High[1] - Low[1]

proxy_delta_pct = ((Close[1] - Open[1]) / range) * 100
```

### DATA_GUARD

```text
IF range <= 0:
    DELTAVOL_ALLOW = 0
```

### NOTE

```text
PROXY_DELTA не является настоящей биржевой дельтой.
PROXY_DELTA используется только если нет BuyVolume/SellVolume.
```

---

## CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| delta_mode | enum | - | - | - | TRUE_DELTA / PROXY_DELTA | source_mode | yes |
| pressure | enum | - | - | - | BUY / SELL | delta_direction | yes |
| delta_thr | int | 5 | 80 | 5 | - | percent | yes |

## SIGNAL_RULE

```text
IF delta_mode = TRUE_DELTA:
    delta_value = delta_volume_pct

IF delta_mode = PROXY_DELTA:
    delta_value = proxy_delta_pct

IF pressure = BUY AND delta_value >= delta_thr:
    DELTAVOL_ALLOW = 1
ELSE IF pressure = SELL AND delta_value <= -delta_thr:
    DELTAVOL_ALLOW = 1
ELSE:
    DELTAVOL_ALLOW = 0
```

## OUTPUT_MEANING

```text
DELTAVOL_ALLOW = 1: вход разрешён
DELTAVOL_ALLOW = 0: вход запрещён
```

## CALIBRATION_OUTPUT_TO_RUNTIME

После калибровки передаются только откалиброванные параметры:

```text
F021_delta_mode
F021_pressure
F021_delta_thr
```

В runtime рассчитывается:

```text
F021_DELTAVOL_ALLOW
```

## SIDE_MODE

```text
LONG и SHORT калибруются отдельно внешним режимом Оптумно.
Внутри F021 сторона сделки не калибруется.
```

Для LONG-профиля сохраняются:

```text
F021_LONG_delta_mode
F021_LONG_pressure
F021_LONG_delta_thr
```

Для SHORT-профиля сохраняются:

```text
F021_SHORT_delta_mode
F021_SHORT_pressure
F021_SHORT_delta_thr
```

## NOT_CALIBRATED

```text
side
tf
calc_method
entry_exit
order_size
stop_loss
take_profit
```

## REGISTRY_ROW

```text
F021 | delta_volume_1m | DELTAVOL_ALLOW | ENTRY_FILTER | delta_mode(TRUE_DELTA/PROXY_DELTA),pressure(BUY/SELL),delta_thr(min=5,max=80,step=5) | fixed: TF=1m,CALC_METHOD=CLOSE_BAR | output: 1=ALLOW,0=BLOCK
```
