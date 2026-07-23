# STAS5 V5 Two-Block ML ТЗ

Статус: `TZ_DRAFT_READY_FOR_USER_REVIEW_NO_TRAINING`.

Дата фиксации: `2026-07-16`.

Диапазон базы: `2026-01-27..2026-02-27`.

Текущий batch guard: `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING`.

Обучение и forward по этому ТЗ еще не запускались.

## 1. Цель этапа

Сделать безопасный ML-контур V5, который учится на размеченной истории, но в рабочем режиме принимает решение только по данным, доступным на момент `entry_time_utc`.

Текущая база:

```text
days = 32/32 full-ready
rows = 2596
entry_y=1 GOOD = 290
entry_y=0 BAD/NO_TRADE = 2306
features = 439
feature contract = 274 old causal + 81 cs_* + 84 fcs_*
training = NOT_STARTED
forward = NOT_STARTED
```

Главная архитектура V5:

```text
X439 -> ENTRY_BASELINE_ML -> entry_y

X439 -> MARKET_PHASE_STATE_ML -> phase/state predictions

X439 + OOF/live phase/state predictions -> ENTRY_ML -> entry_y
```

`ENTRY_BASELINE_ML` обязателен. Он нужен, чтобы честно увидеть, улучшает ли второй блок результат, или просто усложняет систему.

## 2. Главный закон train/live

Историческая разметка может знать, чем закончился день. Это teacher/y:

```text
entry_y
phase_y
state_y
reason_y
manual passport decisions
GOOD ids
```

Но модельные входы `X` не имеют права знать будущее. Во всех training, OOF, validation и forward прямые признаки модели берутся только из causal allowlist:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_FEATURE_ALLOWLIST_439F_V1.json
```

Правильное разделение:

```text
teacher / targets = можно использовать как y и audit
causal X439 = можно использовать как live features
OOF predictions = можно использовать как stacking features на train
live predictions = можно использовать как stacking features на forward
```

Запрещенная подмена:

```text
phase_y/state_y как готовые признаки для ENTRY_ML
reason_y как готовый признак для ENTRY_ML
manual labels как готовые признаки
future/postfact/outcome как признаки
```

## 3. Source Of Truth

Основные входы этапа:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_ML_READY_439F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_FEATURE_ALLOWLIST_439F_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_MANIFEST_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_GUARD_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_AUDIT_RU.md
```

Batch CSV содержит рядом `X` и teacher/target columns. Это нормально. Нельзя брать все колонки CSV как model features. `X` всегда определяется только allowlist-файлом `439F`.

## 4. Почему не сразу одна большая ML

Одна модель `X439 -> entry_y` будет сделана как baseline. Это самый чистый контрольный вариант.

Две ML нужны, потому что пользовательская разметка описывает не только "вход хороший/плохой", но и рыночный контекст:

```text
рынок находится в фазе/состоянии
внутри этой фазы одни входы хорошие, другие плохие
ENTRY_ML может стать лучше, если получит не ручную фазу, а предсказанную моделью фазу
```

Но второй блок принимается в production только если он улучшает baseline на честной проверке. Если `ENTRY_BASELINE_ML` окажется не хуже, V5 может работать одной entry-моделью, а phase/state слой останется audit/explainability слоем.

## 5. Разрешенные и запрещенные признаки

Разрешено в прямом `X`:

```text
274 old causal features
81 cs_* causal market-structure features
84 fcs_* full causal structure features
```

Итого:

```text
X439 = 439 features
```

Разрешено дополнительно только для `ENTRY_ML`:

```text
OOF predictions от MARKET_PHASE_STATE_ML на train
live predictions от MARKET_PHASE_STATE_ML на forward/live
```

Запрещено в любых model features:

```text
entry_y
phase_y
state_y
reason_y
entry_label
rank_label
manual labels
manual passport fields
manual phase/support/resistance labels
market_phase_primary
entry_reason_primary
future*
postfact*
hit_*
TP*
Stas3*
exit*
old ML_KEEP_SCORE
old ML_DECISION
full-group future fields
day-end top-N/rank fields
post-entry price/outcome/drawdown fields
любые признаки после entry_time_utc
```

## 6. Training Guard

Перед любым обучением обязателен отдельный guard:

```text
STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1
```

Он должен блокировать training, если:

1. batch guard не `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING`;
2. batch rows не `2596`;
3. days не `32`;
4. `entry_y 1` не `290`;
5. `entry_y 0` не `2306`;
6. feature count не `439`;
7. allowlist отличается от batch allowlist `439F`;
8. есть дубли по `day+candidate_id`;
9. есть дубли по `day+record_id`, если `record_id` присутствует;
10. есть null/NaN/inf в `X439`;
11. target/manual columns попали в `X`;
12. forbidden columns попали в `X`;
13. `cs_max_source_time_utc > entry_time_utc`;
14. `fcs_max_source_time_utc > entry_time_utc`;
15. training/output path уже содержит forward-артефакты;
16. OOF/fold policy не описана до старта обучения.

Ожидаемые выходы guard:

```text
STAS5_ML_CORE/artifacts/v5/model/runs/<run_id>/STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1.json
STAS5_ML_CORE/artifacts/v5/model/runs/<run_id>/STAS5_V5_TWO_BLOCK_TRAINING_GUARD_RU.md
```

Только после `PASS` разрешается training.

## 7. Split и OOF политика

Нельзя делать случайный row split, потому что соседние кандидаты одного дня и одной рыночной ситуации слишком похожи. Минимальная единица split: день.

Нужны два разных вида проверки.

### 7.1 Day-group OOF для stacking

Цель: получить phase/state predictions для каждой train-строки так, чтобы модель первого блока не видела эту строку при обучении.

Правило:

```text
fold split по day
OOF coverage = 2596/2596
join только по стабильным ключам
in-sample predictions запрещены
```

Это защищает `ENTRY_ML` от прямого self-row leakage.

### 7.2 Walk-forward audit для честной оценки live-режима

Цель: проверить, как схема ведет себя, когда validation-дни идут после train-дней.

Принцип:

```text
train = более ранние дни
validation = более поздние дни
baseline и two-block получают одинаковые train/validation окна
```

С учетом маленькой базы `32` дня, exact окна можно выбрать в training guard manifest перед запуском. Главное требование: validation-день не должен попадать в train этого же fold.

Метрики для решения "baseline или two-block" должны смотреться прежде всего по walk-forward audit, а не по train-fit.

## 8. ENTRY_BASELINE_ML

Baseline-модель:

```text
ENTRY_BASELINE_ML: X439 -> entry_y
```

Требования:

1. вход только `X439`;
2. target только `entry_y`;
3. `phase_y/state_y/reason_y` не используются как features;
4. OOF phase/state predictions не используются;
5. split и validation окна совпадают с two-block проверкой;
6. сохраняются raw scores, metrics, feature list, manifest.

Baseline считается обязательным контрольным слоем, а не запасной мелочью. Если two-block не улучшит baseline, production может остаться на baseline.

## 9. MARKET_PHASE_STATE_ML

Первый блок:

```text
MARKET_PHASE_STATE_ML: X439 -> phase_y/state_y
```

Цель: научиться по causal признакам понимать рыночный контекст, который пользователь размечал вручную.

Требования:

1. вход только `X439`;
2. `phase_y/state_y` используются только как targets;
3. `reason_y` не является live feature, максимум audit/diagnostic target в отдельном отчете;
4. модель должна выдавать probability features, а не только hard label;
5. редкие классы phase/state фиксируются в manifest;
6. class imbalance фиксируется в metrics report;
7. все OOF predictions проходят отдельный OOF guard.

Рекомендуемые prediction columns:

```text
phase_pred_label
phase_pred_conf
phase_prob_<phase_class>
state_pred_label
state_pred_conf
state_prob_<state_class>
```

В OOF-файле эти поля могут иметь suffix `_oof`. В forward-файле эти же логические признаки должны иметь live-safe manifest и не должны называться `phase_y/state_y`.

## 10. OOF слой

OOF слой обязателен между `MARKET_PHASE_STATE_ML` и `ENTRY_ML`.

Запрещено:

```text
обучить MARKET_PHASE_STATE_ML на всех строках
сделать predictions на этих же строках
дать эти in-sample predictions в ENTRY_ML
```

Разрешено:

```text
обучить MARKET_PHASE_STATE_ML на fold train
сделать predictions на fold validation
собрать OOF predictions для всех rows
дать OOF predictions в ENTRY_ML
```

OOF guard должен проверить:

1. rows = `2596`;
2. OOF coverage = `2596/2596`;
3. нет строк без prediction;
4. нет дублей ключей;
5. prediction columns не пересекаются с target/manual names;
6. fold id заполнен;
7. каждая строка предсказана моделью, которая не обучалась на этой строке;
8. join с batch идет без изменения порядка и счетчиков.

Ожидаемые артефакты:

```text
STAS5_V5_MARKET_PHASE_STATE_OOF_PREDICTIONS_V1.csv
STAS5_V5_MARKET_PHASE_STATE_OOF_MANIFEST_V1.json
STAS5_V5_MARKET_PHASE_STATE_OOF_GUARD_V1.json
```

## 11. ENTRY_ML

Основной второй блок:

```text
ENTRY_ML: X439 + MARKET_PHASE_STATE predictions -> entry_y
```

На train:

```text
X439 + OOF phase/state prediction features -> entry_y
```

На forward/live:

```text
X439 + live phase/state prediction features -> entry score
```

Требования:

1. реальные `phase_y/state_y` запрещены как features;
2. `reason_y` запрещен как feature;
3. `entry_y` используется только как target;
4. feature list ENTRY_ML должен явно состоять из `439 + approved_prediction_columns`;
5. baseline и two-block сравниваются на одинаковых rows/folds;
6. threshold/policy выбирается только после просмотра raw metrics;
7. final model сохраняется только после post-train guard `PASS`.

## 12. Post-Train Guard

После обучения обязателен:

```text
STAS5_V5_TWO_BLOCK_POST_TRAIN_GUARD_V1
```

Проверки:

1. training guard был `PASS`;
2. сохраненные модели существуют и читаются;
3. manifests содержат input files, hashes, date range, rows, features, targets, split, seed, class counts;
4. baseline и two-block использовали одинаковую batch-базу;
5. `MARKET_PHASE_STATE_ML` feature list ровно `X439`;
6. `ENTRY_BASELINE_ML` feature list ровно `X439`;
7. `ENTRY_ML` feature list ровно `X439 + approved_prediction_columns`;
8. target/manual/forbidden columns отсутствуют в model feature lists;
9. OOF coverage `100%`;
10. метрики рассчитаны по OOF/walk-forward, а не только train-fit;
11. forward artifacts не создавались до post-train `PASS`;
12. production model pointer не обновлен без отдельного решения пользователя.

Forward разрешается только после `POST_TRAIN_GUARD=PASS`.

## 13. Live / Forward цепочка

Рабочий режим должен повторять реальную цепочку:

```text
новый кандидат появился в entry_time_utc
-> собрать X439 только из данных <= entry_time_utc
-> MARKET_PHASE_STATE_ML делает live prediction
-> добавить live phase/state prediction features
-> ENTRY_ML делает entry_score
-> policy принимает/отклоняет вход
-> решение фиксируется на entry_time_utc и не переписывается будущим
```

В live запрещено:

1. использовать финальный low/high дня;
2. использовать outcome после входа;
3. использовать TP/Stas3/exit;
4. использовать полный состав будущей группы;
5. использовать будущих кандидатов, которые еще не появились;
6. заменять live predictions на настоящие `phase_y/state_y`;
7. пересчитывать старое решение после появления новых свечей.

## 14. Метрики

Нужны не только стандартные ML-числа, но и human-style отчет.

Для `ENTRY_BASELINE_ML` и `ENTRY_ML`:

```text
ROC-AUC
PR-AUC
precision / recall / F1 по нескольким thresholds
top score buckets: top 1%, 5%, 10%, 20%
GOOD captured in top buckets
BAD admitted in top buckets
daily GOOD captured / BAD admitted
score distribution для GOOD и BAD
confusion matrix
calibration bins
baseline vs two-block delta
```

Для `MARKET_PHASE_STATE_ML`:

```text
phase accuracy
phase macro-F1
state accuracy
state macro-F1
phase confusion matrix
state confusion matrix
rare class report
confidence quality
```

Human-style вопросы отчета:

```text
Модель видит нижние хорошие входы?
Модель режет плохие верхние входы перед провалом?
Где MARKET_PHASE_STATE_ML путает фазу и ломает entry?
Улучшает ли phase/state слой ENTRY_ML относительно baseline?
В какие дни модель пропустила GOOD и почему?
В какие дни модель пустила слишком много BAD и почему?
```

## 15. Decision policy после обучения

После training нельзя сразу объявлять модель production только по красивому AUC.

Решение принимается по сравнительной таблице:

```text
ENTRY_BASELINE_ML
ENTRY_ML two-block
```

Two-block принимается как основной только если:

1. он улучшает baseline по walk-forward/human-style метрикам;
2. улучшение не держится на одном случайном дне;
3. количество BAD в верхних score buckets не растет опасно;
4. OOF и post-train guards `PASS`;
5. live/forward recipe полностью повторяет training feature contract.

Если two-block не улучшает baseline, правильный итог V5.0:

```text
production candidate = ENTRY_BASELINE_ML
MARKET_PHASE_STATE_ML = audit/explainability layer
two-block = rejected_or_deferred
```

Это не провал. Это честная защита от усложнения системы без пользы.

## 16. Артефакты training run

Рекомендуемая папка:

```text
STAS5_ML_CORE/artifacts/v5/model/runs/<run_id>/
```

Минимальный набор:

```text
STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1.json
STAS5_V5_TWO_BLOCK_TRAINING_GUARD_RU.md

STAS5_V5_ENTRY_BASELINE_MODEL.joblib
STAS5_V5_ENTRY_BASELINE_MANIFEST_V1.json
STAS5_V5_ENTRY_BASELINE_OOF_PREDICTIONS_V1.csv

STAS5_V5_MARKET_PHASE_STATE_MODEL.joblib
STAS5_V5_MARKET_PHASE_STATE_MANIFEST_V1.json
STAS5_V5_MARKET_PHASE_STATE_OOF_PREDICTIONS_V1.csv
STAS5_V5_MARKET_PHASE_STATE_OOF_GUARD_V1.json

STAS5_V5_ENTRY_ML_MODEL.joblib
STAS5_V5_ENTRY_ML_MANIFEST_V1.json
STAS5_V5_ENTRY_ML_FEATURE_ALLOWLIST_V1.json
STAS5_V5_ENTRY_ML_OOF_PREDICTIONS_V1.csv

STAS5_V5_TWO_BLOCK_METRICS_V1.json
STAS5_V5_TWO_BLOCK_METRICS_RU.md
STAS5_V5_TWO_BLOCK_POST_TRAIN_GUARD_V1.json
STAS5_V5_TWO_BLOCK_POST_TRAIN_GUARD_RU.md
```

Каждый manifest должен хранить:

```text
run_id
created_at
date_range
input dataset path
input dataset hash
allowlist path
allowlist hash
feature columns
target columns
fold policy
random seed
model type and params
class counts
metrics paths
guard paths
```

## 17. Что именно надо реализовать следующим шагом

Порядок разработки:

1. `stas5_v5_two_block_training_guard.py`
2. wrapper `run_stas5_v5_two_block_training_guard.ps1`
3. tests для training guard
4. training run folder builder без обучения
5. baseline `ENTRY_BASELINE_ML`
6. `MARKET_PHASE_STATE_ML`
7. OOF predictions и OOF guard
8. `ENTRY_ML`
9. metrics report
10. post-train guard
11. только потом отдельный forward guard и blind forward

На текущем этапе пункт 1 является следующим практическим шагом. Training не запускать, пока training guard не реализован и не дал `PASS`.

## 18. Что сейчас не делаем

Пока не делаем:

```text
Optuna
API / Bybit live execution
real money / paper execution
forward до сохраненной модели
threshold auto-tuning без raw metrics
TP/Stas3/exit logic
новые ручные признаки в X
multi-task neural model
production pointer update
```

Multi-task или одна большая модель может быть вариантом V5.1, но не V5.0. Сначала нужна прозрачная, guard-driven схема с baseline и two-block сравнением.

## 19. Acceptance Criteria

Этап `Two-block ML training preparation` считается готовым, если:

1. это ТЗ принято пользователем;
2. training guard реализован;
3. training guard `PASS`;
4. guard подтверждает `rows=2596`, `entry_y 1=290`, `entry_y 0=2306`, `features=439`;
5. guard подтверждает, что targets/manual/forbidden columns не входят в `X`;
6. OOF/fold policy зафиксирована до training;
7. forward still `NOT_STARTED`;
8. training still `NOT_STARTED` до отдельной команды на обучение.

Этап `Two-block ML training` считается готовым позже, если:

1. baseline обучен и имеет честные metrics;
2. MARKET_PHASE_STATE_ML обучен только на `X439`;
3. OOF predictions покрывают `2596/2596`;
4. ENTRY_ML обучен на `X439 + OOF predictions`;
5. post-train guard `PASS`;
6. metrics report показывает baseline vs two-block;
7. все artifacts сохранены;
8. forward не запускался до post-train `PASS`.

## 20. Короткий ответ на главный вопрос

Да, на обучении ML может учиться на закрытой размеченной истории: месяц уже известен, GOOD/BAD и phase/state уже размечены.

Нет, модель не может получать будущее как признаки. Будущее может быть только причиной, почему строка получила `entry_y/phase_y/state_y` в teacher-слое.

В live модель работает так:

```text
знания из прошлого уже зашиты в весах модели
новый день дает только causal X439 на текущий момент
первый блок предсказывает phase/state
второй блок решает entry
будущее не читается и старые решения не переписываются
```
