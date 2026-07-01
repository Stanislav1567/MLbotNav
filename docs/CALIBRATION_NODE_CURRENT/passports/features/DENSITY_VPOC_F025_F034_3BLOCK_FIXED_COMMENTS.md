# DENSITY / VPOC — 3 BLOCK PASSPORT

```text
FAMILY: DENSITY_PROFILE_VPOC
FEATURES: F025-F034
ACTION_TYPE: ENTRY_FILTER
OUTPUT: 1/0
STATUS: ACTIVE
CUSTOM_CALC: YES
```

---

# 0. COMMON FIXED_PROFILE

```text
TF = 1m
CALC_METHOD = CLOSE_BAR
CANDLE = closed
PROFILE_METHOD = rolling_volume_by_price_bins
PRICE_SOURCE = Close
VOLUME_SOURCE = base_volume
BIN_SOURCE_PRICE = Close
BIN_SIZE_MODE = percent_of_price
BIN_STEP_PCT = 0.05
CLUSTER_RADIUS_BINS = 1
VPOC_RULE = max_volume_bin
```

## COMMENT_FIXED_PROFILE

```text
Этот блок обязателен.
Он не калибруется.
Он должен одинаково использоваться в Оптумно, ML и MQL.

Если изменить BIN_STEP_PCT, CLUSTER_RADIUS_BINS или VPOC_RULE,
то все значения F025-F034 будут другими.
```

---

# 1. COMMON PROFILE FORMULAS

```text
Для окна N:

bin_id[i] = price_bin(Close[i], BIN_STEP_PCT)

bin_volume_N[bin] = SUM(Volume[i] where bin_id[i] = bin), i = 1..N

total_volume_N = SUM(Volume[i]), i = 1..N

vpoc_N = bin with max(bin_volume_N)

current_bin_N = bin_id[1]

current_cluster_N = current_bin_N +/- CLUSTER_RADIUS_BINS

bin_share_N = bin_volume_N[current_bin_N] / total_volume_N * 100

cluster_share_N = SUM(bin_volume_N[current_cluster_N]) / total_volume_N * 100

vpoc_share_N = bin_volume_N[vpoc_N] / total_volume_N * 100

vpoc_distance_N_pct = (Close[1] / vpoc_N - 1) * 100

vpoc_abs_distance_N_pct = abs(vpoc_distance_N_pct)
```

## COMMON_DATA_GUARD

```text
IF total_volume_N <= 0:
    ALLOW = 0

IF vpoc_N <= 0:
    ALLOW = 0
```

---

# 2. BLOCK A — VPOC CORE

```text
BLOCK_ID: DENSITY_A
BLOCK_NAME: VPOC_CORE
CALIBRATION_PRIORITY: 1
FEATURES: F025,F029,F033,F034
PURPOSE: базовый VPOC-контекст цены, смещение VPOC, отношение локальной и старшей плотности
```

## COMMENT_BLOCK_A

```text
Этот блок калибруется первым.
Он отвечает за главный VPOC-контекст.
Если нужен быстрый старт, начинать только с этого блока.
```

---

## F025 — density_vpoc_distance_60

```text
ID: F025
FEATURE: density_vpoc_distance_60_1m
ACTION: VPOCDIST60_ALLOW
WINDOW = 60
OUTPUT = 1/0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| signal_mode | enum | - | - | - | SIDE / DISTANCE | mode | yes |
| side_state | enum | - | - | - | ABOVE / BELOW | position | conditional |
| distance_state | enum | - | - | - | NEAR / FAR | distance | conditional |
| dist_thr_pct | float | 0.00 | 3.00 | 0.01 | - | percent | yes |

### SIGNAL_RULE

```text
IF signal_mode = SIDE AND side_state = ABOVE AND vpoc_distance_60_pct >= dist_thr_pct:
    VPOCDIST60_ALLOW = 1

ELSE IF signal_mode = SIDE AND side_state = BELOW AND vpoc_distance_60_pct <= -dist_thr_pct:
    VPOCDIST60_ALLOW = 1

ELSE IF signal_mode = DISTANCE AND distance_state = NEAR AND vpoc_abs_distance_60_pct <= dist_thr_pct:
    VPOCDIST60_ALLOW = 1

ELSE IF signal_mode = DISTANCE AND distance_state = FAR AND vpoc_abs_distance_60_pct >= dist_thr_pct:
    VPOCDIST60_ALLOW = 1

ELSE:
    VPOCDIST60_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F025_signal_mode
F025_side_state
F025_distance_state
F025_dist_thr_pct
F025_VPOCDIST60_ALLOW
```

---

## F029 — density_vpoc_distance_240

```text
ID: F029
FEATURE: density_vpoc_distance_240_1m
ACTION: VPOCDIST240_ALLOW
WINDOW = 240
OUTPUT = 1/0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| signal_mode | enum | - | - | - | SIDE / DISTANCE | mode | yes |
| side_state | enum | - | - | - | ABOVE / BELOW | position | conditional |
| distance_state | enum | - | - | - | NEAR / FAR | distance | conditional |
| dist_thr_pct | float | 0.00 | 5.00 | 0.05 | - | percent | yes |

### SIGNAL_RULE

```text
IF signal_mode = SIDE AND side_state = ABOVE AND vpoc_distance_240_pct >= dist_thr_pct:
    VPOCDIST240_ALLOW = 1

ELSE IF signal_mode = SIDE AND side_state = BELOW AND vpoc_distance_240_pct <= -dist_thr_pct:
    VPOCDIST240_ALLOW = 1

ELSE IF signal_mode = DISTANCE AND distance_state = NEAR AND vpoc_abs_distance_240_pct <= dist_thr_pct:
    VPOCDIST240_ALLOW = 1

ELSE IF signal_mode = DISTANCE AND distance_state = FAR AND vpoc_abs_distance_240_pct >= dist_thr_pct:
    VPOCDIST240_ALLOW = 1

ELSE:
    VPOCDIST240_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F029_signal_mode
F029_side_state
F029_distance_state
F029_dist_thr_pct
F029_VPOCDIST240_ALLOW
```

---

## F033 — density_vpoc_drift_20

```text
ID: F033
FEATURE: density_vpoc_drift_20_1m
ACTION: VPOCDRIFT20_ALLOW
DRIFT_BARS = 20
VPOC_WINDOW = 60
OUTPUT = 1/0
```

### FORMULA

```text
vpoc_drift_20_pct = (vpoc_60[1] / vpoc_60[21] - 1) * 100
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| drift_dir | enum | - | - | - | UP / DOWN | direction | yes |
| drift_thr_pct | float | 0.00 | 2.00 | 0.01 | - | percent | yes |

### SIGNAL_RULE

```text
IF drift_dir = UP AND vpoc_drift_20_pct >= drift_thr_pct:
    VPOCDRIFT20_ALLOW = 1

ELSE IF drift_dir = DOWN AND vpoc_drift_20_pct <= -drift_thr_pct:
    VPOCDRIFT20_ALLOW = 1

ELSE:
    VPOCDRIFT20_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F033_drift_dir
F033_drift_thr_pct
F033_VPOCDRIFT20_ALLOW
```

---

## F034 — density_cluster_ratio_60_240

```text
ID: F034
FEATURE: density_cluster_ratio_60_240_1m
ACTION: CLUSTERRATIO_ALLOW
WINDOW_FAST = 60
WINDOW_SLOW = 240
OUTPUT = 1/0
```

### FORMULA

```text
cluster_ratio_60_240 = cluster_share_60 / cluster_share_240
```

### DATA_GUARD

```text
IF cluster_share_240 <= 0:
    CLUSTERRATIO_ALLOW = 0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| ratio_level | float | 0.50 | 2.50 | 0.05 | - | ratio | yes |

### SIGNAL_RULE

```text
IF cmp = GREATER AND cluster_ratio_60_240 >= ratio_level:
    CLUSTERRATIO_ALLOW = 1

ELSE IF cmp = LESS AND cluster_ratio_60_240 <= ratio_level:
    CLUSTERRATIO_ALLOW = 1

ELSE:
    CLUSTERRATIO_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F034_cmp
F034_ratio_level
F034_CLUSTERRATIO_ALLOW
```

---

# 3. BLOCK B — ZONE DENSITY

```text
BLOCK_ID: DENSITY_B
BLOCK_NAME: ZONE_DENSITY
CALIBRATION_PRIORITY: 2
FEATURES: F026,F027,F030,F031
PURPOSE: плотность текущего бина и кластера за окна 60 и 240
```

## COMMENT_BLOCK_B

```text
Этот блок калибруется вторым.
Он отвечает за плотная сейчас зона цены или пустая.
Не смешивать с силой самого VPOC.
```

---

## F026 — density_bin_share_60

```text
ID: F026
FEATURE: density_bin_share_60_1m
ACTION: BINSHARE60_ALLOW
WINDOW = 60
OUTPUT = 1/0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| share_thr_pct | float | 1 | 40 | 1 | - | percent | yes |

### SIGNAL_RULE

```text
IF cmp = GREATER AND bin_share_60 >= share_thr_pct:
    BINSHARE60_ALLOW = 1

ELSE IF cmp = LESS AND bin_share_60 <= share_thr_pct:
    BINSHARE60_ALLOW = 1

ELSE:
    BINSHARE60_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F026_cmp
F026_share_thr_pct
F026_BINSHARE60_ALLOW
```

---

## F027 — density_cluster_share_60

```text
ID: F027
FEATURE: density_cluster_share_60_1m
ACTION: CLUSTERSHARE60_ALLOW
WINDOW = 60
OUTPUT = 1/0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| share_thr_pct | float | 2 | 70 | 1 | - | percent | yes |

### SIGNAL_RULE

```text
IF cmp = GREATER AND cluster_share_60 >= share_thr_pct:
    CLUSTERSHARE60_ALLOW = 1

ELSE IF cmp = LESS AND cluster_share_60 <= share_thr_pct:
    CLUSTERSHARE60_ALLOW = 1

ELSE:
    CLUSTERSHARE60_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F027_cmp
F027_share_thr_pct
F027_CLUSTERSHARE60_ALLOW
```

---

## F030 — density_bin_share_240

```text
ID: F030
FEATURE: density_bin_share_240_1m
ACTION: BINSHARE240_ALLOW
WINDOW = 240
OUTPUT = 1/0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| share_thr_pct | float | 0.5 | 25.0 | 0.5 | - | percent | yes |

### SIGNAL_RULE

```text
IF cmp = GREATER AND bin_share_240 >= share_thr_pct:
    BINSHARE240_ALLOW = 1

ELSE IF cmp = LESS AND bin_share_240 <= share_thr_pct:
    BINSHARE240_ALLOW = 1

ELSE:
    BINSHARE240_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F030_cmp
F030_share_thr_pct
F030_BINSHARE240_ALLOW
```

---

## F031 — density_cluster_share_240

```text
ID: F031
FEATURE: density_cluster_share_240_1m
ACTION: CLUSTERSHARE240_ALLOW
WINDOW = 240
OUTPUT = 1/0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| share_thr_pct | float | 1 | 60 | 1 | - | percent | yes |

### SIGNAL_RULE

```text
IF cmp = GREATER AND cluster_share_240 >= share_thr_pct:
    CLUSTERSHARE240_ALLOW = 1

ELSE IF cmp = LESS AND cluster_share_240 <= share_thr_pct:
    CLUSTERSHARE240_ALLOW = 1

ELSE:
    CLUSTERSHARE240_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F031_cmp
F031_share_thr_pct
F031_CLUSTERSHARE240_ALLOW
```

---

# 4. BLOCK C — VPOC STRENGTH

```text
BLOCK_ID: DENSITY_C
BLOCK_NAME: VPOC_STRENGTH
CALIBRATION_PRIORITY: 3
FEATURES: F028,F032
PURPOSE: сила самого VPOC-бина за окна 60 и 240
```

## COMMENT_BLOCK_C

```text
Этот блок калибруется третьим.
Он вторичный.
Он показывает, насколько сам VPOC концентрированный или слабый.
```

---

## F028 — density_vpoc_share_60

```text
ID: F028
FEATURE: density_vpoc_share_60_1m
ACTION: VPOCSHARE60_ALLOW
WINDOW = 60
OUTPUT = 1/0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| share_thr_pct | float | 1 | 50 | 1 | - | percent | yes |

### SIGNAL_RULE

```text
IF cmp = GREATER AND vpoc_share_60 >= share_thr_pct:
    VPOCSHARE60_ALLOW = 1

ELSE IF cmp = LESS AND vpoc_share_60 <= share_thr_pct:
    VPOCSHARE60_ALLOW = 1

ELSE:
    VPOCSHARE60_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F028_cmp
F028_share_thr_pct
F028_VPOCSHARE60_ALLOW
```

---

## F032 — density_vpoc_share_240

```text
ID: F032
FEATURE: density_vpoc_share_240_1m
ACTION: VPOCSHARE240_ALLOW
WINDOW = 240
OUTPUT = 1/0
```

### CALIBRATION_PARAMS

| param | type | min | max | step | values | unit | required |
|---|---:|---:|---:|---:|---|---|---|
| cmp | enum | - | - | - | GREATER / LESS | compare | yes |
| share_thr_pct | float | 0.5 | 35.0 | 0.5 | - | percent | yes |

### SIGNAL_RULE

```text
IF cmp = GREATER AND vpoc_share_240 >= share_thr_pct:
    VPOCSHARE240_ALLOW = 1

ELSE IF cmp = LESS AND vpoc_share_240 <= share_thr_pct:
    VPOCSHARE240_ALLOW = 1

ELSE:
    VPOCSHARE240_ALLOW = 0
```

### RUNTIME_PARAMS

```text
F032_cmp
F032_share_thr_pct
F032_VPOCSHARE240_ALLOW
```

---

# 5. CALIBRATION ORDER

```text
1. BLOCK A — VPOC_CORE
2. BLOCK B — ZONE_DENSITY
3. BLOCK C — VPOC_STRENGTH
```

## COMMENT_CALIBRATION_ORDER

```text
Не запускать все F025-F034 одной кучей на первом проходе.
Сначала проверить VPOC_CORE.
Потом добавить ZONE_DENSITY.
Потом проверить VPOC_STRENGTH.
```

---

# 6. GLOBAL NOT_CALIBRATED

```text
side
tf
calc_method
price_source
volume_source
profile_method
bin_source_price
bin_size_mode
bin_step_pct
cluster_radius_bins
vpoc_rule
entry_exit
order_size
stop_loss
take_profit
```

---

# 7. REGISTRY_ROWS

```text
F025 | density_vpoc_distance_60_1m | VPOCDIST60_ALLOW | DENSITY_A_VPOC_CORE | signal_mode(SIDE/DISTANCE),side_state(ABOVE/BELOW),distance_state(NEAR/FAR),dist_thr_pct(0.00–3.00 step 0.01) | fixed: BIN_STEP_PCT=0.05,CLUSTER_RADIUS_BINS=1,VPOC_RULE=max_volume_bin | output 1/0

F029 | density_vpoc_distance_240_1m | VPOCDIST240_ALLOW | DENSITY_A_VPOC_CORE | signal_mode(SIDE/DISTANCE),side_state(ABOVE/BELOW),distance_state(NEAR/FAR),dist_thr_pct(0.00–5.00 step 0.05) | fixed: BIN_STEP_PCT=0.05,CLUSTER_RADIUS_BINS=1,VPOC_RULE=max_volume_bin | output 1/0

F033 | density_vpoc_drift_20_1m | VPOCDRIFT20_ALLOW | DENSITY_A_VPOC_CORE | drift_dir(UP/DOWN),drift_thr_pct(0.00–2.00 step 0.01) | fixed: VPOC_WINDOW=60,BIN_STEP_PCT=0.05 | output 1/0

F034 | density_cluster_ratio_60_240_1m | CLUSTERRATIO_ALLOW | DENSITY_A_VPOC_CORE | cmp(GREATER/LESS),ratio_level(0.50–2.50 step 0.05) | fixed: WINDOW_FAST=60,WINDOW_SLOW=240,CLUSTER_RADIUS_BINS=1 | output 1/0

F026 | density_bin_share_60_1m | BINSHARE60_ALLOW | DENSITY_B_ZONE_DENSITY | cmp(GREATER/LESS),share_thr_pct(1–40 step 1) | fixed: WINDOW=60,BIN_STEP_PCT=0.05 | output 1/0

F027 | density_cluster_share_60_1m | CLUSTERSHARE60_ALLOW | DENSITY_B_ZONE_DENSITY | cmp(GREATER/LESS),share_thr_pct(2–70 step 1) | fixed: WINDOW=60,CLUSTER_RADIUS_BINS=1 | output 1/0

F030 | density_bin_share_240_1m | BINSHARE240_ALLOW | DENSITY_B_ZONE_DENSITY | cmp(GREATER/LESS),share_thr_pct(0.5–25.0 step 0.5) | fixed: WINDOW=240,BIN_STEP_PCT=0.05 | output 1/0

F031 | density_cluster_share_240_1m | CLUSTERSHARE240_ALLOW | DENSITY_B_ZONE_DENSITY | cmp(GREATER/LESS),share_thr_pct(1–60 step 1) | fixed: WINDOW=240,CLUSTER_RADIUS_BINS=1 | output 1/0

F028 | density_vpoc_share_60_1m | VPOCSHARE60_ALLOW | DENSITY_C_VPOC_STRENGTH | cmp(GREATER/LESS),share_thr_pct(1–50 step 1) | fixed: WINDOW=60,BIN_STEP_PCT=0.05 | output 1/0

F032 | density_vpoc_share_240_1m | VPOCSHARE240_ALLOW | DENSITY_C_VPOC_STRENGTH | cmp(GREATER/LESS),share_thr_pct(0.5–35.0 step 0.5) | fixed: WINDOW=240,BIN_STEP_PCT=0.05 | output 1/0
```
