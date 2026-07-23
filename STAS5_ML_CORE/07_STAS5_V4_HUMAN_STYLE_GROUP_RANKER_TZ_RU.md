# STAS5 V4 Human-Style Group Ranker

## 0A. Закон V4 No-Future / Live-Safe

Статус правила: `MANDATORY_FOREVER`.

V4 не имеет права знать будущее относительно момента кандидата `entry_time_utc`. Это касается не только TP/Stas3/future outcome, но и будущего состава группы. Если кандидат появился в `10:15`, модель в `10:15` может знать только:

1. свечи с временем `<= entry_time_utc`;
2. признаки, рассчитанные до `entry_time_utc`;
3. уже появившихся кандидатов этой локальной зоны;
4. текущее live-состояние группы на момент кандидата.

Модель не может знать:

1. сколько кандидатов еще появится в этой группе после `entry_time_utc`;
2. какой будущий кандидат станет самым низким;
3. будущий `final group low`;
4. будущий `BEST_GOOD`;
5. что позже появится `post_candidate_lower_low_exists`;
6. `minutes_to_best_low`, `distance_to_best_low`, `is_before_best_low`, если они рассчитаны по полному будущему дню;
7. любую ручную группу, построенную по уже видимому полному графику, как live-feature.

Ручной `STAS5_V4_GROUP_RANK_LEDGER.csv` остается разрешенным как label/audit source: он говорит, какой кандидат по факту человек считает лучшим внутри зоны. Но label не является feature. В обучение можно переносить только признаки, которые были доступны на момент каждого кандидата.

Текущие красивые offline-группы нужны как teacher/review layer, но боевой V4 обязан добиться похожего поведения без подсмотра: через live-safe признаки `*_so_far`, состояние открытой зоны и ранжирование кандидата относительно уже видимых соседей.

Любой train/forward, который использует полный состав группы для model features, должен иметь статус:

```text
OFFLINE_GROUP_REVIEW_NOT_LIVE_SAFE
```

и не может считаться production/live моделью.

## Поправка 2026-07-14: Micro-Groups И Старые Маркеры

Статус: `STAS5_V4_20260515_MICRO_GROUP_V2_FIXED_NO_TRAINING`.

После ручной проверки `2026-05-15` зафиксировано уточнение: старый статус маркера `ENTER/UNSURE/SKIP` не является label для V4. Если пользователь подчеркнул желтый ромбик или серый крестик как правильный нижний вход, он может быть `BEST_GOOD` внутри своей группы.

Один macro-move может содержать несколько человеческих точек входа. В таком случае создаются отдельные micro-groups, а не одна широкая группа с одним winner. Пример `2026-05-15`:

```text
G20260515_001A_0122_0203: LA004 BEST_GOOD
G20260515_001B_0222_0235: LA007 BEST_GOOD
```

Финальный дневной ориентир `2..5` не является жестким потолком. Если день волатильный и пользователь видит 6, 8 или больше разных понятных lower-entry zones, V4 должен хранить их как отдельные обоснованные groups/micro-groups, а не срезать число входов ради лимита. Запрещен не большой счетчик сам по себе, а шумные зеленые стрелки без group winner/reason.

Статус: `STAS5_V4_FORWARD_REVIEW_20260515_20260525_DRAFT_NO_TRAINING`.

Дата фиксации: `2026-07-14`.

## 0. Текущая коррекция календаря

Правильная рамка V4 теперь такая:

```text
train_base_14 = 2026-05-01..2026-05-14
forward_review_11 = 2026-05-15..2026-05-25
quarantine_days = none for 2026-05-15
```

`2026-05-15` больше не отдельный карантинный день и не отдельная approved-ветка. Он входит в тот же forward-review пакет, что и `2026-05-16..2026-05-25`.

Единый рабочий пакет:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Статус пакета: `DRAFT_NO_TRAINING`. Это ручной forward-review ledger на `11` дней: `738` строк, `55` `BEST_GOOD`, `55` winners. Это не train-approved база и не запуск обучения. Отдельный старый `2026-05-15 approved only` статус считается слишком узким и superseded текущим `forward_review_11`.

## 1. Главный разворот V4

V4 больше не должен учиться как построчный классификатор `KEEP/CUT`, где соседние кандидаты рассматриваются как независимые строки:

```text
LA020 = BAD
LA021 = GOOD
```

Правильная единица обучения V4 - локальная группа кандидатов внутри одной зоны/движения:

```text
GROUP_001:
  LA017 BAD_TOO_EARLY
  LA018 BAD_TOO_EARLY
  LA020 BAD_BEFORE_FINAL_LOW
  LA021 BEST_GOOD_DEEP_LOW_AFTER_KNIFE
```

Цель: не “ML ставит много ENTER”, а:

```text
локальная зона / движение -> группа кандидатов -> выбрать лучший вход -> объяснить плохие рядом
```

Финальный рабочий ориентир не является жестким лимитом по количеству. Цель V4 - адаптивно выбирать лучшие входы по режиму дня: в спокойный день это может быть `2..3` входа, в нормальный активный день `4..6`, в сильный волатильный день может быть и `8..12`, если каждая сделка является понятным winner/alt внутри своей группы. Запрещен не сам большой дневной счетчик, а `20+` зеленых шумных стрелок без локального преимущества и reason-code.

## 2. Календарь данных

Актуальный V4-календарь после исправления статуса `2026-05-15`:

```text
train_base_14 = 2026-05-01..2026-05-14
forward_review_11 = 2026-05-15..2026-05-25
quarantine_days = none for 2026-05-15
```

`2026-05-15` входит в общий forward-review блок вместе с `2026-05-16..2026-05-25`. Он не должен жить отдельной веткой и не должен автоматически смешиваться с train-base `2026-05-01..2026-05-14`.

Актуальный unified ledger:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Статус unified ledger: `DRAFT_NO_TRAINING`. Старый `2026-05-15 approved only` файл сохранен как исторический/superseded слой, но не является отдельной рабочей веткой V4.

## 3. Главная таблица V4

Новый источник истины:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Обязательные поля:

| Поле | Смысл |
|---|---|
| `day` | День кандидата, формат `YYYY-MM-DD` |
| `symbol` | Торговая пара, например `SOLUSDT` |
| `timeframe` | Таймфрейм, например `1m` |
| `group_id` | ID локальной группы внутри дня |
| `candidate_id` | Человеческий ID кандидата, например `LA021` |
| `record_id` | Машинный ID записи |
| `entry_time_utc` | Время входа |
| `entry_price_5bps` | Цена исполнения с `+5bps` |
| `rank_label` | Один из V4 labels |
| `is_group_winner` | `1`, если это winner группы, иначе `0` |
| `primary_reason_code` | Главная причина label |
| `secondary_reason_codes` | Список дополнительных причин через `;` |
| `label_status` | Статус разметки |
| `source_review_file` | PNG/CSV/скрин/ledger, откуда пришло решение |
| `notes` | Короткая ручная заметка |

## 4. Labels

Допустимые `rank_label`:

| Label | Смысл |
|---|---|
| `BEST_GOOD` | Лучший вход в группе |
| `GOOD_ALT` | Допустимый хороший вход, но не главный |
| `BAD_IN_GROUP` | Плохой рядом с хорошим |
| `NO_TRADE_GROUP` | Вся группа не нужна |
| `REVIEW_ONLY` | Только аудит, не train target |
| `EXCLUDED` | Не использовать |

В каждой обучающей группе должен быть ровно один `BEST_GOOD`, если группа торгуемая. Для группы без хорошего входа используется `NO_TRADE_GROUP`; такие группы нельзя молча превращать в набор случайных отрицательных строк без reason-code.

## 5. Reason Codes

Good reasons:

```text
GOOD_BEST_LOCAL_LOW
GOOD_DEEP_LOW_AFTER_KNIFE
GOOD_PULLBACK_LOW
GOOD_CHANNEL_LOWER_TOUCH
GOOD_SUPPORT_RETEST
GOOD_FIRST_LOW_AFTER_FLUSH
GOOD_RETEST_LOW_AFTER_BASE
GOOD_FIRST_LOCAL_LOW
GOOD_LOW_ZONE
GOOD_DEEPER_LOCAL_LOW
GOOD_BEST_DEEP_LOW_AFTER_KNIFE
GOOD_PULLBACK_LOW_AFTER_REACTION
GOOD_DEEP_LOW_AFTER_STRONG_SELL_IMPULSE
GOOD_FINAL_LOW
GOOD_SECOND_LOW_IN_SAME_ZONE
GOOD_BEST_RETEST_LOW_AFTER_BASE
```

Bad reasons:

```text
BAD_TOO_EARLY_BEFORE_LOW
BAD_TOO_HIGH_IN_DROP
BAD_BEFORE_FINAL_LOW
BAD_DUPLICATE_NOT_LOWEST
BAD_MID_CHANNEL
BAD_CHOP_NO_CLEAR_LOW
BAD_AFTER_BOUNCE_TOO_HIGH
BAD_FALLING_KNIFE
BAD_NO_REVERSAL
BAD_TOO_HIGH
BAD_TOO_EARLY
BAD_TOO_EARLY_BEFORE_DEEP_LOW
BAD_NOT_LOWEST
BAD_TOO_EARLY_BEFORE_BEST_LOW
BAD_AFTER_BOUNCE_NOT_BEST
BAD_NOT_SELECTED
BAD_HIGHER_THAN_NEEDED
BAD_CHOP_OR_TOO_LATE
BAD_TOO_EARLY_IN_KNIFE
BAD_NOT_BEST_LOW
BAD_SIDEWAYS_NO_EDGE
```

Для `BAD_IN_GROUP` `primary_reason_code` обязателен. Для `BEST_GOOD` или `GOOD_ALT` обязателен good reason. Пустой reason-code разрешен только для `REVIEW_ONLY`/`EXCLUDED`, если это явно отражено в `notes`.

## 6. Главные Group Features

Ядро V4 - признаки относительного положения кандидата внутри группы:

```text
group_size
group_duration_min
group_price_range_pct
candidate_rank_by_price_in_group
is_lowest_in_group
distance_to_group_low_pct
distance_to_best_low_pct
minutes_from_group_start
minutes_to_best_low
minutes_before_best_low
is_before_best_low
is_after_best_low
is_after_bounce_too_high
prior_candidate_better_low
post_candidate_lower_low_exists
same_basin_duplicate_count
```

Важно: список выше описывает человеческую offline-разметку, но не все эти поля разрешены как live model features.

Разрешенные live-safe group features должны считаться только на момент кандидата:

```text
group_size_so_far
group_age_min_so_far
group_price_range_so_far_pct
candidate_rank_by_price_so_far
is_lowest_so_far
distance_to_running_group_low_pct
minutes_from_group_start
prior_candidate_better_low
same_basin_duplicate_count_so_far
running_lower_low_count
running_retest_count
running_bounce_from_low_pct
running_drop_from_group_high_pct
```

Запрещенные model features, если они рассчитаны по полному будущему составу группы:

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
```

Эти final/full-group поля разрешены только как `label_audit` / `review_audit`, чтобы объяснить человеку, почему рядом был плохой вход. Если такие поля попали в `feature_columns`, обучение V4 live-safe запрещено.

## 7. Старые признаки остаются как контекст

Старые признаки не выбрасываются. Они должны объяснять, почему внутри одной группы один вход лучше, а соседние хуже:

```text
session
фон
LONG/SHORT проценты
WAVE
RSI/MACD/Stoch/ATR
volume
density
structure
pattern
short pressure
knife risk
long recovery
support/resistance
```

Запрещено использовать старые признаки как предварительный hard-cut до обучения. Плохой вход рядом с хорошим является ценным обучающим примером.

## 8. Запрещенные feature columns

В V4 features запрещены:

```text
ML_KEEP_SCORE_V2
ML_KEEP_SCORE_V3
ML_DECISION_V2
ML_DECISION_V3
current_ml_score
current_ml_decision
yellow_x
postfact
hit_*
future
TP
Stas3
exit
```

Также запрещено использовать любые готовые решения V2/V3 как признак V4. Их можно хранить только как audit metadata вне feature columns.

## 9. Правило “ничего не режем до обучения”

До обучения нельзя удалять кандидатов по индикаторам, strategy votes, yellow X, density/structure/pattern или старому ML score.

Разрешено отбрасывать только технический мусор:

1. нет свечей;
2. нет времени;
3. сломанный join;
4. дубликат машинного ключа;
5. future leakage;
6. невозможный `entry_time_utc` или `entry_price_5bps`.

## 10. Модель V4

Первый V4 - group ranker, а не обычный классификатор. Внутри `group_id` winner должен получить score выше loser.

Минимальные метрики:

```text
top1_group_accuracy
winner_in_top2
MRR
NDCG@3
ENTER_per_day
selected_entries_per_day_by_regime
overtrade_noise_count
bad_in_top1_count
```

`ENTER_per_day` - это диагностический контроль шума, а не фиксированный потолок. Оценка должна учитывать режим дня: quiet/range day естественно дает меньше входов, trend/volatile day может дать больше. Построчный AUC больше не главная метрика. Его можно считать как вспомогательную диагностику, но нельзя принимать решение о качестве V4 только по AUC.

## 11. Guard перед обучением

V4 train запрещен, если:

1. есть `BEST_GOOD`/`GOOD_ALT` без `group_id`;
2. есть `BAD_IN_GROUP` без `primary_reason_code`;
3. в обучающей торгуемой группе нет winner;
4. в группе больше одного `is_group_winner=1`;
5. `forward_review_11 = 2026-05-15..2026-05-25` не собран единым ledger или собран без `2026-05-15`;
6. `2026-05-15` используется отдельной 15-only веткой вместо общего `forward_review_11`;
7. `2026-05-01..2026-05-14` и `2026-05-15..2026-05-25` смешаны без явного train/review статуса;
8. старые ML score/decision попали в feature columns;
9. нет обязательных group features;
10. reason/group coverage не сходится с ledger;
11. в features попали postfact/future/TP/Stas3/exit поля.

## 11A. Live-Safe Guard Перед Любым Следующим Train

V4 live-safe train запрещен, если:

1. используются full-group/final group признаки;
2. решение раннего кандидата меняется после добавления будущих кандидатов в ту же группу;
3. `feature_available_time_utc > entry_time_utc`;
4. forward-policy сортирует все группы дня и выбирает дневной top задним числом;
5. manifest не разделяет `offline_review_features` и `live_safe_features`;
6. нет теста `prefix invariance`;
7. нет явного `LIVE_SAFE_FEATURE_ALLOWLIST`;
8. live model использует `group_size_final`, `is_lowest_in_full_group`, `post_candidate_lower_low_exists`, `distance_to_best_low`, `minutes_to_best_low`, `is_before_best_low` как features.

Обязательный тест `prefix invariance`:

```text
Для любого кандидата K:
score(K) и decision(K), посчитанные на prefix rows <= K,
должны совпадать со score(K) и decision(K), посчитанными на полном дне,
если из полного дня убрать все запрещенные future/full-group признаки.
```

Если добавление будущих строк меняет признаки или решение старого кандидата, это future leakage. Такой V4 можно хранить только как offline review, но нельзя использовать как live/production модель.

## 12. Рабочий план

1. Зафиксировать V4-ТЗ и guardrails: group ranker, не построчный `KEEP/CUT`.
2. Считать train-base отдельной рамкой: `2026-05-01..2026-05-14`.
3. Считать forward-review отдельной рамкой: `2026-05-15..2026-05-25`.
4. Использовать единый `STAS5_V4_GROUP_RANK_LEDGER.csv` для `forward_review_11`: `738` строк, `55` winners, `label_status=DRAFT`.
5. Построить group features: rank by price, distance to group low, before/after best low, duplicate basin.
6. Сделать визуальный график проверки: группа, winner, bad рядом, reason.
7. После финального guard/approval решить, как переносить review-ledger в train-approved пакет.
8. Только после этого обучать V4 group ranker.
9. Forward должен показывать top группы, а не все зеленые строки.

## 13. Граница текущего шага

На этом шаге создан unified forward-review ledger `2026-05-15..2026-05-25` и исправлена документационная рамка. Это не обучение и не train-approved dataset.

Не запускаются:

```text
training
threshold tuning
Optuna
API/bridge
TP/Stas3/exit
production decision controller
```
