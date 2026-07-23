# STAS5 V4L Live-Safe Group Ranker Plan

Статус: `DESIGN_LOCKED_NO_TRAINING`.

Дата фиксации: `2026-07-14`.

## 1. Главный закон

V4L не имеет права знать будущее относительно момента кандидата `entry_time_utc`.

Запрещено использовать не только TP/Stas3/future outcome, но и будущий состав группы. Если кандидат появился в `10:15`, модель может знать только свечи и кандидатов, которые уже существовали к `10:15`.

Текущий V4 run `stas5_v4_train_20260714_163911` и forward `stas5_v4_forward_20260526_20260530_20260714_164144` остаются полезным offline review, но не считаются live-safe production model, потому что full-group признаки считались по уже собранной группе.

## 2. Что остается ценным от текущего V4

Оставляем:

1. human-style ledger `STAS5_V4_GROUP_RANK_LEDGER.csv`;
2. labels `BEST_GOOD`, `GOOD_ALT`, `BAD_IN_GROUP`, `NO_TRADE_GROUP`;
3. reason-codes;
4. визуальную логику "локальная зона -> кандидаты рядом -> лучший вход -> плохие рядом";
5. старые `274` контекстных признака, если они доступны до `entry_time_utc`;
6. offline group review как teacher/audit слой.

Не оставляем как live model features:

1. full-group low;
2. final group size/duration/range;
3. future best low;
4. `post_candidate_lower_low_exists`;
5. признаки "до/после winner", если winner известен только из будущего.

## 3. Новый принцип V4L

V4L работает как последовательный replay:

```text
нет активной группы
-> пришел кандидат
-> открыть/обновить live-группу
-> посчитать только so_far признаки
-> дать score и решение сейчас
-> обновить состояние группы
-> будущий кандидат не переписывает прошлое решение
```

Решение для LA017 не может измениться после появления LA021. Если меняется, это future leakage.

## 4. Live-Состояние Группы

Для каждой active group хранится только уже произошедшее:

```text
group_id
status = ACTIVE / ENTERED_COOLDOWN / CLOSED
start_time_utc
last_candidate_time_utc
candidate_count_so_far
running_group_low_price
running_group_low_time_utc
running_group_high_price
running_price_range_so_far_pct
best_candidate_so_far_id
best_score_so_far
best_price_so_far
top2_score_so_far
same_basin_duplicate_count_so_far
running_lower_low_count
running_retest_count
running_bounce_from_low_pct
running_drop_from_group_high_pct
phase_at_start
last_phase_code
entries_so_far_in_day
```

## 5. Live-Safe Features

Новый prefix-префикс для признаков: `v4l_`.

Разрешенные model features:

```text
v4l_group_size_so_far
v4l_group_age_min_so_far
v4l_group_price_range_so_far_pct
v4l_candidate_rank_by_price_so_far
v4l_is_lowest_so_far
v4l_distance_to_running_group_low_pct
v4l_minutes_from_group_start
v4l_minutes_since_running_low
v4l_prior_candidate_better_low
v4l_same_basin_duplicate_count_so_far
v4l_running_lower_low_count
v4l_running_retest_count
v4l_running_bounce_from_low_pct
v4l_running_drop_from_group_high_pct
v4l_score_gap_to_best_so_far
v4l_price_delta_to_best_so_far_pct
v4l_minutes_since_best_so_far
```

Разрешенные старые контекстные признаки:

```text
session
day_so_far_*
session_so_far_*
pre_* только если окно строго до entry_time_utc
RSI/MACD/Stoch/ATR на закрытых свечах до входа
volume/density/structure/pattern до входа
short_pressure
knife_risk
long_recovery
support/resistance до входа
```

## 6. Audit-Only / Forbidden Features

Эти поля можно хранить для отчета и объяснения, но нельзя включать в `feature_columns` live-модели:

```text
group_size_final
group_duration_final_min
group_price_range_final_pct
candidate_rank_by_price_in_full_group
is_lowest_in_full_group
distance_to_final_group_low_pct
distance_to_best_low_pct
minutes_to_best_low
minutes_before_best_low
is_before_best_low
is_after_best_low
post_candidate_lower_low_exists
final_group_winner_candidate_id
rank_label
human_label
label_status
is_group_winner
target_v4_winner
primary_reason_code
secondary_reason_codes
source_review_file
notes
yellow*
review*
ML_KEEP_SCORE*
ML_DECISION*
V3_*
V4_DECISION
V4_GROUP_RANK_SCORE
V4_OOF*
V4_TRAIN_FIT*
future
postfact
post_entry
outcome
target*
hit_*
time_to_*
hold_minutes
mfe
mae
tp
sl
exit
stas3
```

## 7. Live Boundary Для Групп

Новая группа открывается, если:

1. нет active group;
2. gap от прошлого кандидата больше adaptive gap;
3. после running low был сильный bounce и начался новый retest/pullback;
4. сменилась phase/session/wave/structure после реакции;
5. group age слишком большой и уже была реакция.

Стартовые adaptive пороги:

```text
quiet/range: gap 75-120m, max_age 240-300m
normal: gap 45-75m, max_age 150-240m
volatile: gap 20-45m после реакции, max_age 60-150m
```

Количество входов в день появляется из числа live micro-groups, а не из жесткого дневного лимита.

## 8. Decision Policy

На каждом кандидате:

```text
assign_or_start_group(candidate)
compute v4l_so_far features
score_abs = качество входа по свечам/контексту
score_rank = преимущество против previous candidates in active group
score_live = blend(score_abs, score_rank)
decision = ENTER / UNSURE / SKIP_WAIT
update group state
```

`ENTER` по умолчанию разрешен, если кандидат:

1. top1-so-far внутри active group;
2. прошел score threshold;
3. не `after_bounce_too_high`;
4. не "falling knife still pending";
5. не дубль хуже уже выбранного входа в той же micro-group.

`GOOD_ALT_ENTER` можно вводить отдельным режимом только для сильного `rank2-so-far`, но без переписывания прошлого.

## 9. Режимы Дня И 2-12 Входов

Дневной счетчик не является жестким target.

```text
quiet/range: обычно 2-3 входа
normal: обычно 4-6 входов
volatile: обычно 6-9 входов
extreme volatile: возможно 9-12 входов
```

Режим дня считается только по live-safe признакам:

1. `day_so_far_range_pct`;
2. ATR/ADX до входа;
3. candidate rate за 60/180 минут;
4. `stas5_v2_short_wave_active_window_count`;
5. session;
6. macro/structure events, известные до входа.

## 10. Обязательные Guard-Тесты

Перед любым новым live-safe train должны пройти:

1. `LIVE_SAFE_FEATURE_ALLOWLIST`;
2. banned-column scan;
3. `feature_available_time_utc <= entry_time_utc`;
4. `prefix invariance`;
5. `retroactive_feature_change_count = 0`;
6. `retroactive_score_change_count = 0`;
7. `retroactive_decision_flip_count = 0`;
8. train/forward split check;
9. offline-vs-live comparison report.

`prefix invariance`:

```text
Для любого кандидата K:
score(K) и decision(K), посчитанные на prefix rows <= K,
должны совпадать со score(K) и decision(K), посчитанными на полном дне
при live-safe feature set.
```

## 11. Метрики

Offline review metrics остаются справочными:

```text
top1_group_accuracy
winner_in_top2
MRR
NDCG@3
BAD top1
GOOD_ALT top1
```

Live-safe metrics становятся главными:

```text
winner_covered_by_live_enter_or_unsure
bad_early_enter_count
duplicate_enter_count
enter_per_day_by_regime
GOOD_ALT_enter_count
missed_best_good_count
decision_flip_matrix_offline_vs_live
ENTER_set_jaccard_offline_vs_live
score_corr_offline_vs_live
prefix_invariance_pass
```

## 12. Реализация По Шагам

1. Зафиксировать этот документ и обновить V4-TZ.
2. Пометить текущий V4 train/forward как `OFFLINE_GROUP_REVIEW_NOT_LIVE_SAFE`.
3. Создать `stas5_v4l_live_group_state.py`.
4. Создать `stas5_v4l_live_safe_dataset.py`: replay `2026-05-01..2026-05-25` по времени, labels брать из V4 ledger, features считать только `v4l_*`.
5. Создать `stas5_v4l_leakage_guard.py`: allowlist, banned columns, prefix invariance.
6. Обучить V4L только после guard `PASS`.
7. Прогнать `2026-05-26..2026-05-30` в live replay режиме.
8. Сравнить текущий offline review и новый live-safe forward.
9. Только после визуальной проверки считать V4L рабочей боевой веткой.

## 13. Статус Реализации 2026-07-14

Сделан первый рабочий V4L-контур:

```text
src/mlbotnav/stas5_v4l_live_safe_dataset.py
src/mlbotnav/stas5_v4l_live_safe_train.py
src/mlbotnav/stas5_v4l_live_safe_forward.py
STAS5_ML_CORE/run_stas5_v4l_live_safe_train_forward.ps1
```

Контроль:

```text
dataset PASS
rows = 1710
days = 2026-05-01..2026-05-25
winners = 103
features = 289
v4l_so_far_group_features = 15
prefix_invariance = 1710/1710
forbidden_features = {}
```

Smoke forward:

```text
run = STAS5_ML_CORE/artifacts/v4l/forward/runs/stas5_v4l_forward_20260526_20260530_20260714_181635
rows = 363
ENTER = 23
UNSURE = 80
SKIP = 260
per_day_ENTER = 2026-05-26:4, 2026-05-27:5, 2026-05-28:5, 2026-05-29:5, 2026-05-30:4
```

Следующий шаг: визуально сравнить PNG forward `26..30` с offline V4 и калибровать только live-safe пороги/признаки/policy. Запрещено возвращать full-group low/rank/size, `post_candidate_lower_low_exists` и day-end top-N.
