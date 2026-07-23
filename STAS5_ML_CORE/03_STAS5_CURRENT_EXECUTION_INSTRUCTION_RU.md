# STAS-5: рабочее ТЗ по ML-входам

Статус: `CURRENT_TZ_ENTRY_ML_TRAIN_1_14_FORWARD_15_PLUS_NO_TP_NO_API`.

Дата фиксации: `2026-07-10`.

## 1. Рабочее решение

STAS-5 обучает только входы.

```text
Train:   2026-05-01..2026-05-14, human KEEP/CUT
Forward: 2026-05-15 и дальше, ML показывает входы без ручных меток
Output:  CSV + PNG с ML-точками входа
No TP:   Stas3/TP/exit не участвуют
```

Forward window `2026-05-15+` не используется для обучения, подбора threshold или ручной доводки модели.

Цель модели:

```text
candidate LAxxx + признаки ДО входа -> ML_KEEP_SCORE -> ENTER / UNSURE / SKIP
```

## 2. Текущий пункт

Сейчас делаем подготовку к первому controlled ML:

```text
1. STAS5 ML-ledger
2. STAS5 feature snapshot
3. leakage guard
4. pre-ML audit
5. controlled baseline
6. forward entry review на 2026-05-15+
```

Текущий первый исполняемый шаг:

```text
создать src/mlbotnav/stas5_ml_ledger_builder.py
```

## 3. Что уже готово

| Блок | Путь | Статус |
|---|---|---|
| Human labels | `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels/LABELS_YYYYMMDD_ALL_ENTRIES_DRAFT.csv` | `972` rows, `115 KEEP_DRAFT`, `857 CUT_DRAFT` |
| Yellow X audit | те же labels | `287` yellow X, `30 KEEP_DRAFT + yellow_x` |
| Stas1 source | `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260501_20260514_carry48_for_stas2_v1_20260709_135847/GOOD_1PCT_REVIEW_POOL_RECORDS.csv` | `972` candidates |
| Stas2 source | `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260501_20260514_from_stas1_carry48_full_v1_20260709_142757/STAS2_RECORDS.csv` | `972` rows, pre-entry context |
| Stas4 source | `STAS4_FEATURE_HYPOTHESIS_REVIEW/` | strategy votes / density / structure / pattern / volume context |
| Старый ML | `src/mlbotnav/dataset.py`, `pipeline_train_eval.py`, `validation.py` | использовать идеи, не использовать старый target напрямую |

## 4. Главные правила

1. Human label главный:

```text
human KEEP > strategy vote
```

2. Yellow X не фильтр:

```text
yellow_x = AUDIT_ONLY
```

3. Stas3 не входит в STAS-5:

```text
Stas3/TP/exit/MFE/MAE = запрещено для entry ML
```

4. Future outcome запрещен как `feature`, `target`, `filter` и `threshold input`.

5. Будущее можно использовать после факта для forward-аудита:

```text
ML показала вход -> после этого проверяем, что было дальше
```

## 5. Что нельзя давать в feature matrix

Запрещены:

1. `future_return`;
2. `target_up`;
3. `review_label`;
4. `outcome_status`;
5. `is_good_stas1_review`;
6. `hit_*`;
7. `target_1pct_*`;
8. `time_to_*`;
9. `mfe*`;
10. `mae*`;
11. `post_entry_*`;
12. `ideal_review_tp_pct`;
13. `max_feasible_review_tp_pct`;
14. Stas3 TP/exit/ladder fields;
15. `yellow_x`, `strategy_vote`, `strategy_cut`, `would_cut` для первого baseline;
16. entry-candle `high/low/close/volume`, если решение принимается на `entry_open`.

## 6. Что можно давать в feature matrix

Разрешены только признаки, известные до входа:

1. `candidate_id`, `record_id`, `day`, `entry_time_utc` как идентификаторы/служебные поля;
2. `stas1_feature_*`;
3. `stas1_risk_flags`;
4. `session_*`, `effective_session_*`, `day_type`, `is_weekend`;
5. `pre_5m_*`, `pre_15m_*`, `pre_30m_*`, `pre_60m_*`;
6. `entry_setup_quality_*`, если рассчитано до входа;
7. `context_before_entry_check`;
8. Stas4 causal context после отдельной проверки времени доступности.

## 7. Артефакты, которые надо создать

### 7.1. Ledger

Скрипт:

```text
src/mlbotnav/stas5_ml_ledger_builder.py
```

Выход:

```text
STAS5_ML_CORE/artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.csv
STAS5_ML_CORE/artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.manifest.json
```

Обязательные проверки:

```text
rows = 972
KEEP_DRAFT = 115
CUT_DRAFT = 857
KEEP_DRAFT + yellow_x = 30
no lost rows after join with STAS2_RECORDS
entry_time_utc matches
record_id matches
entry_price_5bps exists
```

### 7.2. Feature snapshot

Скрипт:

```text
src/mlbotnav/stas5_feature_snapshot_builder.py
```

Выход:

```text
STAS5_ML_CORE/artifacts/features/stas5_feature_snapshot_20260501_20260514_v0.csv
STAS5_ML_CORE/artifacts/features/stas5_feature_snapshot_20260501_20260514_v0.manifest.json
```

### 7.3. Leakage guard

Скрипт:

```text
src/mlbotnav/stas5_leakage_guard.py
```

Задача: падать, если в features попали запрещенные поля.

### 7.4. Pre-ML audit

Скрипт:

```text
src/mlbotnav/stas5_pre_ml_audit.py
```

Выход:

```text
STAS5_ML_CORE/artifacts/audit/STAS5_PRE_ML_AUDIT_20260501_20260514_RU.md
```

Отчет должен показать:

1. row parity;
2. coverage по признакам;
3. KEEP vs CUT по фазам/сессиям/setup;
4. список `KEEP_DRAFT + yellow_x`;
5. список запрещенных колонок, если они найдены;
6. готовность к controlled baseline.

### 7.5. Controlled baseline

Скрипт:

```text
src/mlbotnav/stas5_entry_ranker_train.py
```

Train:

```text
2026-05-01..2026-05-14
```

Первый baseline:

```text
без yellow_x / strategy_vote / Stas3 / future outcome
```

Метрики:

1. `KEEP recall`;
2. `CUT precision`;
3. `KEEP_WITH_YELLOW_X recall`;
4. confusion по дням;
5. score distribution.

### 7.6. Forward entry review

Скрипт:

```text
src/mlbotnav/stas5_forward_entry_review.py
```

Forward days:

```text
2026-05-15+
```

Вход:

```text
Stas1/Stas2/Stas4 candidates без human labels
```

Выход:

```text
STAS5_ML_CORE/artifacts/forward/YYYYMMDD/STAS5_FORWARD_ENTRIES_YYYYMMDD.csv
STAS5_ML_CORE/artifacts/forward/YYYYMMDD/STAS5_FORWARD_ENTRY_REVIEW_YYYYMMDD.png
```

PNG должен показывать:

1. цену и свечи;
2. все кандидаты бледно;
3. `ENTER` ярко;
4. `UNSURE` отдельным цветом;
5. `SKIP` бледно;
6. без TP-линий;
7. без Stas3 exit/ladder.

Каждая кандидатная точка на PNG должна иметь ML-статус:

```text
ENTER / UNSURE / SKIP
```

### 7.7. Entry-only forward audit

Это не feature для ML, а проверка после факта.

Можно считать:

1. дошла ли цена после ML-входа до `+0.5%`;
2. дошла ли до `+1.0%`;
3. какая была просадка после входа;
4. сколько входов в день;
5. не дает ли ML кучу входов в одном кластере.

Нельзя подавать эти поля обратно в feature matrix.

Нельзя использовать forward-аудит для подбора threshold на `2026-05-15+`. Если threshold нужно менять, это отдельный новый train/dev протокол, не blind forward.

## 8. Минимальные тесты

1. `tests/test_stas5_ml_ledger_builder.py`;
2. `tests/test_stas5_feature_snapshot_contract.py`;
3. `tests/test_stas5_leakage_guard.py`;
4. `tests/test_stas5_forward_entry_review_contract.py`.

Проверки:

```text
ledger rows = 972
no lost KEEP + yellow_x
no forbidden feature columns
split/train days не смешаны с forward days
forward days не используются для threshold tuning
forward PNG/CSV создаются
Stas3 columns absent
```

## 9. Что считаем готовым результатом этапа

Этап готов, когда есть:

1. ledger на `972` строки;
2. feature snapshot без leakage;
3. pre-ML audit;
4. первый controlled baseline;
5. forward CSV/PNG на `2026-05-15+`;
6. на PNG видны только ML-точки входа;
7. TP/Stas3 не участвует;
8. модель не использует future outcome как feature.

## 10. Короткая формула

```text
1-14 мая: человек учит ML, какие входы KEEP/CUT.
15 мая и дальше: ML сама показывает входы на графиках.
TP не трогаем. Stas3 не трогаем. Future используем только для проверки после факта.
```
