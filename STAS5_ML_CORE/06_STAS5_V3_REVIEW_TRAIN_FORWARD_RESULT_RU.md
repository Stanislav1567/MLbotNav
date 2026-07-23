# STAS5 V3 Review Train Forward Result

Статус: `STAS5_V3_REVIEW_TRAIN_FORWARD_21_25_READY`.

Дата фиксации: `2026-07-14`.

## Что Сделано

Собран отдельный V3-контур, не ломающий V2:

1. `2026-05-01..2026-05-14` оставлены как старая train-база.
2. `2026-05-16..2026-05-20` добавлены как пользовательский review-layer.
3. `2026-05-15` исключен из обучения, потому что день не был финально размечен.
4. `2026-05-21..2026-05-25` оставлены blind-forward holdout.
5. Feature set: `full_v2_all_274`.
6. TP/Stas3/API/Optuna/threshold tuning не использовались.

Источник review-графиков `2026-05-16..2026-05-20` зафиксирован явно:

```text
STAS5_ML_CORE/artifacts/v2/forward/STAS5_V2_FORWARD_ALL_PREDICTIONS_20260515_20260520.csv
```

Это тот V2 root-прогон `v1_plus_risk_gate`, который совпадает с пользовательскими скриншотами `16..20` по count-ам `ENTER/UNSURE/SKIP`. Latest full274 run не используется как источник этих labels.

## Данные

V3 user-review ledger:

```text
STAS5_ML_CORE/artifacts/v3/user_review/STAS5_V3_USER_REVIEW_LEDGER_20260516_20260520.csv
```

Итог ledger:

```text
rows=135
train_rows=134
KEEP_APPROVED=34
CUT_APPROVED=100
NO_CANDIDATE_AUDIT_ONLY=1
auto_bad_unmarked_enter_unsure=15
```

V3 train dataset:

```text
STAS5_ML_CORE/artifacts/v3/features/STAS5_V3_TRAIN_DATASET_20260501_20260520.csv
```

Итог dataset:

```text
rows=1106
old_train_rows=972
review_train_rows=134
feature_count=274
KEEP_DRAFT=115
CUT_DRAFT=857
KEEP_APPROVED=34
CUT_APPROVED=100
```

Guard:

```text
STAS5_ML_CORE/artifacts/v3/guard/STAS5_V3_LEAKAGE_GUARD_20260501_20260520.json
```

Guard status: `PASS`.

## Проверенный Run

Полная команда проверена на run:

```text
stas5_v3_wrapper_smoke2_20260714
```

Model:

```text
STAS5_ML_CORE/artifacts/v3/model/runs/stas5_v3_wrapper_smoke2_20260714/
```

Forward:

```text
STAS5_ML_CORE/artifacts/v3/forward/runs/stas5_v3_wrapper_smoke2_20260714/
```

Forward `2026-05-21..2026-05-25`:

```text
total rows=357
ENTER=79
UNSURE=31
SKIP=247
PNG days READY=5/5
```

По дням:

| Day | Rows | ENTER | UNSURE | SKIP |
|---|---:|---:|---:|---:|
| `2026-05-21` | 81 | 21 | 9 | 51 |
| `2026-05-22` | 75 | 17 | 4 | 54 |
| `2026-05-23` | 63 | 9 | 3 | 51 |
| `2026-05-24` | 70 | 25 | 5 | 40 |
| `2026-05-25` | 68 | 7 | 10 | 51 |

## Команда

```powershell
cd C:\Users\007\Desktop\MLbotNav
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\STAS5_ML_CORE\run_stas5_v3_review_train_forward_21_25.ps1
```

Без открытия папки:

```powershell
.\STAS5_ML_CORE\run_stas5_v3_review_train_forward_21_25.ps1 -NoOpen
```

С ручным именем run:

```powershell
.\STAS5_ML_CORE\run_stas5_v3_review_train_forward_21_25.ps1 -RunId stas5_v3_manual_01
```

Если нужно явно указать источник review-графиков:

```powershell
.\STAS5_ML_CORE\run_stas5_v3_review_train_forward_21_25.ps1 -ReviewForwardPredictionsPath STAS5_ML_CORE\artifacts\v2\forward\STAS5_V2_FORWARD_ALL_PREDICTIONS_20260515_20260520.csv
```

## Ограничения

1. Это entry ML, без TP/Stas3.
2. `2026-05-21..2026-05-25` не использованы для обучения и threshold tuning.
3. `current_ml_score/current_ml_decision`, user-review поля и postfact-поля являются metadata/audit, не ML features.
4. `USER_NO_CANDIDATE_ZONE` сохранен как detector-gap для Stas1/Stas2, не как train label.
