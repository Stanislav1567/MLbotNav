# STAS5 V5C ML Control Config V1

## Текущий Статус 2026-07-22: R4BB X463 Train Active

Статус: `ACTIVE_CONTROL_CONFIG_YAML_SOURCE_OF_TRUTH_R4BB_X463_TRAINED_READY_FOR_FORWARD`.

Активный train-контур:

```text
run_id=stas5_v5c_r4bb_train_20260127_20260320
range=2026-01-27..2026-03-20
rows=3285
entry_y GOOD=517
entry_y BAD=2768
features=463
feature_contract=X439_PLUS_BB24_V1
bb20_*=24
ENTRY post-train guard=PASS
RiskGate ML post-train guard=PASS
selected_entry_model=entry_baseline
```

Активные модели:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5_ENTRY_BASELINE_MODEL.joblib
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5_MARKET_PHASE_STATE_MODEL.joblib
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5_ENTRY_ML_MODEL.joblib
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5C_RISKGATE_ML_MODEL.joblib
```

Старые блоки ниже для R3/X439 оставлены как история и справка, но они больше не являются текущим active train.

## Текущий Статус 2026-07-22: STAS8 Soft Capacity V2 Preview

Статус: `PASS_V5C_STAS8_SOFT_CAPACITY_V2_PREVIEW_READY_NO_TRAINING_NO_FORWARD_NO_DECISION_CHANGE`.

В YAML добавлен неактивный блок `STAS8_SOFT_CAPACITY_V2`. Это мягкая настройка STAS8 после того, как V1 слишком сильно задушил входы. Блок сейчас только для просмотра графиков и сравнения режимов, не для боевого решения.

Источник:

```text
run_id=stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1
range=2026-03-21..2026-03-27
rows=564
features=463
RiskGate applied=false
predictions SHA unchanged=cd7bc6f7a2855a116d6973ef0a827b160c2843cf9df04c432db4b95b2acfd579
```

Режимы preview:

```text
strict:   ENTER=2,  WATCH=118, SKIP=444
balanced: ENTER=15, WATCH=152, SKIP=397
wide:     ENTER=36, WATCH=161, SKIP=367
```

Как читать PNG:

```text
зеленый круг = финальный live ENTER после STAS8
красный квадрат = исходный ENTER понижен в WATCH
красный круг = hard risk block
hidden SKIP recall = offline-аудит, не торговый сигнал
```

Важный fix 2026-07-22: старая картинка смешивала final `ENTER`, `WATCH protect` и `SKIP->RECALL_WATCH` одним зеленым кругом. Исправлено: green circle теперь только final live `ENTER`, а `RECALL_WATCH` остается в CSV/отчете и не рисуется на цене.

Маркерные цифры после исправления:

```text
strict:   green=2,  red_square=6,  red_circle=107, hidden_recall=0
balanced: green=15, red_square=11, red_circle=60,  hidden_recall=48
wide:     green=36, red_square=6,  red_circle=30,  hidden_recall=48
```

Главный кандидат для ручного просмотра - `balanced`, но перед train/enforce требуется донастройка down-channel: на 2026-03-26 `balanced` еще оставляет 1 live `ENTER`, а `wide` оставляет 9 live `ENTER` в плохом канале вниз. `strict` оставляем как нижнюю осторожную границу.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/soft_capacity_v2
```

Важно: `STAS8_SOFT_CAPACITY_V2.enabled=false`, `selected_for_entry=false`, `selected_for_safety=false`. `RECALL_WATCH`, `hit_*`, `future_*`, `time_to_*`, `mae_*`, `move_capacity_y`, `move_edge_y` являются только offline/audit полями и запрещены как live X.

## Текущий Статус 2026-07-22: STAS8 Audit-Preview

Статус: `PASS_V5C_STAS8_MOVE_CAPACITY_AUDIT_V1_READY_NO_TRAINING_NO_DECISION_CHANGE`.

В YAML обновлен неактивный блок `STAS8_MOVE_CAPACITY_GRID_V1`. Код audit-preview собран и прогнан на актуальном R5 no-risk X463 forward `2026-03-21..2026-03-27`. Это не обучение, не новый forward и не изменение исходных predictions.

Главные цифры R5:

```text
run_id=stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1
rows=564
features=463
до STAS8: ENTER=61, WATCH=166, SKIP=337
preview после STAS8: ENTER=1, WATCH=20, SKIP=543
teacher grid rows=40608
PNG=7
```

Важно: preview показывает, что текущие rule-пороги STAS8 слишком жесткие для боевого включения. Его нужно смотреть глазами и настраивать до обучения/включения.

STAS8 состоит из двух частей:

```text
STAS8_LIVE_MOVE_CONTEXT_V1
сначала подтверждает, что рынок уже живой для long: волны вверх-вниз, откат/retest/base/reclaim, не one-way dump

STAS8_TEACHER_MOVE_GRID_V1
offline/audit измеряет future-ход по LA-точкам: 0.4..5.0 шаг 0.1, 5.0..10.0 шаг 0.2
```

Главная рельса:

```text
R2/R3/R4 = approved train material
2026-03-21..2026-03-27 = R5 blind-forward/audit-preview, не обучение до ручного review
```

Рабочие пороги: `1.1%` мягкий WATCH, `1.2%` основной ENTER, `1.5%` сильный ход. Future/hit/MFE/MAE/time_to остаются только teacher/audit и запрещены в live X.

Документ ТЗ:

```text
STAS5_ML_CORE/10_STAS8_MOVE_CAPACITY_GRID_TZ_RU.md
```

Артефакты audit-preview:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1
```

Важно: STAS8 остается `enabled=false` и `selected_for_entry=false`. Live STAS8 работает только по causal `X463` и закрытым свечам до `entry_time_utc`; `future_*`, `hit_*`, `time_to_*`, `mae_*`, `move_capacity_y`, `move_edge_y` остаются только teacher/audit.

## Текущий Статус 2026-07-21: Safety Pulse Preview

Статус: `PASS_V5C_SAFETY_PULSE_PREVIEW_READY_NO_TRAINING`.

После R4 train/forward по `2026-03-21..2026-03-27` сделан быстрый preview-only пульс `DOWN_CHANNEL_NO_LONG_V1`. Он не запускает обучение, не пересобирает forward и не меняет исходный predictions CSV.

```text
До RiskGate: ENTER=70, WATCH=176, SKIP=318
Старый финал с RISKGATE_ML: ENTER=34, WATCH=37, SKIP=493
DOWN_CHANNEL_NO_LONG_V1 preview: ENTER=40, WATCH=136, SKIP=388

2026-03-26: ENTER=4, WATCH=16, SKIP=68, down_channel_blocks=26
2026-03-27: ENTER=7, WATCH=18, SKIP=51, down_channel_blocks=11
```

Папка просмотра:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1/safety_pulse_preview/down_channel_no_long_v1
```

Правило: ENTRY_BASELINE до RiskGate ищет возможность, а `DOWN_CHANNEL_NO_LONG_V1` отдельным safety-preview блокирует long в нисходящем канале со слабым отскоком и без хода под 1-1.5%. Старые taxonomy/ML mass-demote в этой policy не применяются. Следующий шаг - визуально проверить PNG; новый train/forward не запускать до OK.

## Текущий Статус 2026-07-21: RiskGate ML Подключен К Train/Forward

Статус: `ACTIVE_CONTROL_CONFIG_YAML_SOURCE_OF_TRUTH_RISKGATE_ML_TRAIN_WIRING_READY_NO_TRAINING`.

Готова рельса ручного запуска `stas5_v5c_r4_train_20260127_20260320`. Обучение и forward не запускались мной; пользователь запускает `-Mode Train` сам в VS Code.

```text
ENTRY batch: rows=3285, GOOD=517, BAD=2768, features=439
ENTRY guard: PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
ENTRY TrainingGuard: PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING

RiskGate dataset: rows=627, risk_bad_y=1=400, risk_bad_y=0 explicit safe=227, features=439
RiskGate dataset guard: PASS_V5C_RISKGATE_TRAIN_DATASET_GUARD_READY_NO_TRAINING
RiskGate ML TrainingGuard: PASS_V5C_RISKGATE_ML_TRAINING_GUARD_READY_FOR_TRAINING
```

Кодовая рельса теперь такая:

```text
Train:
  ENTRY_BASELINE_ML / MARKET_PHASE_STATE_ML / ENTRY_ML_TWO_BLOCK
  затем отдельный RISKGATE_ML по target risk_bad_y

Forward после такого train:
  X439 -> ENTRY score/decision
  X439 -> RISKGATE_ML score/decision
  ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE сохраняет исходное ENTRY-решение
  ENTRY_ML_LIVE_DECISION становится финальным решением после RiskGate
```

Ручные targets (`entry_y`, `risk_bad_y`, `phase_y`, `state_y`, `reason_y`, review-комментарии, PNG, future/postfact/outcome) не входят в live `X439`.

---
# STAS5 V5C ML Control Config V1

## Текущий Статус 2026-07-22: Bollinger Layer V1

Статус: `IMPLEMENTED_READY_FOR_DATASET_BUILD_NO_TRAINING`.

В YAML добавлен и в код подключен слой `bollinger_layer_v1`. Он добавляет к базовым `X439` еще `24` причинных `bb20_*` признака, если сборка запущена с `-EnableBollingerLayer`. Новый контракт: `X439_PLUS_BB24_V1`, ожидаемый feature count: `463`.

Главное правило: Bollinger не переписывает ручную разметку. `хорошо` остается `entry_y=1`, `плохо` остается `entry_y=0`, `риск плохо` остается `entry_y=0 + risk_bad_y=1`. `bb_preview_block/reason/score` - audit/visual, не live X.

No-future: `bb_*` считаются только по закрытым 1m свечам до `entry_time_utc`; guard проверяет `bb_source_time_utc <= entry_time_utc`.

Команды после сборки кода:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_train_dataset_builder.ps1 -TrainStartDay 2026-01-27 -TrainEndDay 2026-03-20 -EnableBollingerLayer -Force -OpenFolder
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R2 -BollingerPreview -OpenFolder
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R3 -BollingerPreview -OpenFolder
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R4 -BollingerPreview -OpenFolder
```

## Текущий Статус 2026-07-21

Статус: `REVIEW_SUPERVISED_DATASETS_READY_TRAINING_GUARD_PASS_NO_TRAINING`.

Собран новый train-кандидат `stas5_v5c_r4_train_20260127_20260320`, но обучение не запускалось. Запуск Train должен сделать пользователь вручную в VS Code.

ENTRY dataset готов:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_ML_READY_439F_TARGETS_V1.csv
rows=3285
entry_y GOOD=517
entry_y BAD=2768
features=439
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
training_guard=PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING
```

RiskGate dataset готов:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X439_RISK_BAD_Y_V1.csv
rows=627
risk_bad_y=1=400
risk_bad_y=0 explicit safe=227
features=439
guard=PASS_V5C_RISKGATE_TRAIN_DATASET_GUARD_READY_NO_TRAINING
```

Главное правило сохранено: `риск плохо -> entry_y=0 + risk_bad_y=1`; ручные поля и targets не входят в live `X439`.

Статус текущей фиксации: `REVIEW_PACK_DATASET_RAILS_LOCKED_NO_TRAINING`.

Главный источник правды для ручного управления остается:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

JSON и этот RU.md являются справкой/снимком. Если есть расхождение, править и читать как главный нужно YAML.

## Следующий Этап

Training и forward сейчас не запускаем. Следующий технический этап - подготовить ML-данные:

```text
X439_SOURCE
ENTRY_TRAIN_DATASET
RISKGATE_TRAIN_DATASET
```

База, которая остается базовым остовом обучения:

```text
2026-01-27..2026-02-27
days=32
rows=2596
entry_y GOOD=290
entry_y BAD=2306
features=439
```

Утвержденный review-pack поверх базы:

```text
2026-02-28..2026-03-20
rounds=R2/R3/R4
days=21
ENTRY rows=689
ENTRY GOOD=227
ENTRY BAD=462
RISK BAD=400
guard=PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING
```

Ожидаемый ENTRY train view после прямого объединения:

```text
days=53
rows=3285
entry_y GOOD=517
entry_y BAD=2768
```

Ожидаемый RiskGate train view V1:

```text
target=risk_bad_y
risk_bad_y=1 positives=400
negative policy=explicit_safe_only
minimum explicit safe negatives from reviewed ENTRY GOOD=227
base GOOD 290 = proxy/audit pool, not training negative without separate approval
unlabeled no-risk rows are NOT automatic safe
```

Правило двух целей:

```text
хорошо / вход / крестик хорошо / ромбик хорошо -> entry_y=1
плохо -> entry_y=0
риск плохо -> entry_y=0 + risk_bad_y=1
```

RiskGate не является feature для ENTRY. `entry_y`, `risk_bad_y`, `phase_y`, `state_y`, `reason_y`, ручные review-комментарии, PNG и future/postfact/outcome поля не входят в live `X439`.

До любой команды Train обязательно должны пройти:

```text
approved review-pack guard
X439_SOURCE guard
ENTRY_TRAIN_DATASET guard
RISKGATE_TRAIN_DATASET guard
training guard
```

Статус: `REFERENCE_RU_README_YAML_IS_SOURCE_OF_TRUTH_NO_CODE_WIRING`

Главный управляемый файл теперь:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

Этот RU.md оставлен как человекочитаемая справка. Руками управляем включением/выключением ML-блоков только через YAML, чтобы не было рассинхрона.

Дата фиксации: `2026-07-19`

Этот файл фиксирует управляющую схему ML-блоков STAS5 V5C. Он нужен, чтобы не путаться, какая ML сейчас реально участвует во входах, какая только обучена для сравнения, а какая еще только планируется как safety-слой. На этом шаге код обучения и forward не менялся, обучение не запускалось, predictions не перезаписывались.

## Текущий активный контекст

Активный train run:

```text
stas5_v5c_r3_train_20260127_20260313
```

Train range:

```text
2026-01-27..2026-03-13
days=46
rows=3726
entry_y GOOD=432
entry_y BAD=3294
features=439
```

Train manifest:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r3_train_20260127_20260313/STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json
```

Активный forward review run:

```text
stas5_v5c_r3_forward_20260314_20260320_wide_v1
```

Forward range:

```text
2026-03-14..2026-03-20
rows=569
ENTER=62
WATCH=162
SKIP=345
policy=wide_review
```

Важно: `WideReview` не production. Это широкий режим для ручного разбора, чтобы не пропустить материал для переобучения.

## Feature Contract

Live X для ML:

```text
439 causal features = 274 old causal + 81 cs_* + 84 fcs_*
```

Нельзя подавать в X:

```text
entry_y
phase_y
state_y
reason_y
entry_label
rank_label
manual phase/support/resistance labels
future
postfact
hit_
TP/Stas3/exit
old ML_KEEP_SCORE / ML_DECISION
full-group future признаки
любые признаки после entry_time_utc
```

Ручные GoodIds, BAD-комментарии, phase/state/reason и visual-review разметка являются teacher/target/audit слоем. Они используются для обучения как y или аудит, но не являются live features.

## ML-блоки

### 1. ENTRY_BASELINE_ML

Статус: `enabled`

Режим: `active_selected_entry_alpha`

Роль: главный текущий альфа-блок. Он берет только `X439` и предсказывает `entry_y`.

Артефакт:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r3_train_20260127_20260313/STAS5_V5_ENTRY_BASELINE_MODEL.joblib
```

Именно этот блок сейчас выбран R3 train manifest как активный entry scorer:

```text
selected_entry_model=entry_baseline
reason=baseline_kept_because_two_block_did_not_pass_quality_gate
```

### 2. MARKET_PHASE_STATE_ML

Статус: `enabled`

Режим: `trained_support_model_not_final_entry_selector`

Роль: учится понимать фазу и состояние рынка по `X439`.

Цели:

```text
phase_y
state_y
```

Модель:

```text
extra_trees_balanced
```

Важно: настоящие `phase_y/state_y` нельзя давать как features в ENTRY. На train разрешены только OOF predictions первого блока, на forward только live predictions.

### 3. ENTRY_ML_TWO_BLOCK

Статус: `disabled / frozen`

Режим: `frozen_not_selected`

Роль: замороженный второй entry-блок. Он проверял, улучшает ли добавление phase/state predictions качество входа, но на R3 не доказал пользу против baseline.

Решение от `2026-07-20`: блок не удаляем, но не тратим на него время. Текущий фокус:

```text
X439 -> ENTRY_BASELINE_ML -> RiskGate audit_only
```

Train X:

```text
X439 + OOF MARKET_PHASE_STATE_ML predictions
```

Forward X:

```text
X439 + live MARKET_PHASE_STATE_ML predictions
```

Почему сейчас не главный:

```text
baseline_pr_auc=0.253024
two_block_pr_auc=0.250156
baseline_walk_pr_auc=0.298295
two_block_walk_pr_auc=0.272692
baseline_top_1pct_precision=0.421053
two_block_top_1pct_precision=0.394737
```

Вывод: two-block обучен и сохранен, но пока не доказал преимущество. Сейчас он не должен считаться production-победителем.

### 4. RISK_GATE_RULE_V0

Статус: `disabled`

Планируемый первый режим: `planned_audit_only`

Роль: ремень безопасности поверх ENTRY. Он не ищет хорошие входы вместо ENTRY, а проверяет: не является ли высокий entry-score входом в активный дамп, падающий нож, пробой поддержки или сильный short-regime.

Планируемая цепочка:

```text
ENTRY_ALPHA_SCORE / ENTRY_ALPHA_DECISION
-> RISK_GATE_RULE_V0
-> ENTRY_FINAL_DECISION
```

Сначала RiskGate должен только помечать:

```text
PASS_RISK
WARN_RISK
BLOCK_RISK
WOULD_DEMOTE
WOULD_BLOCK
```

Он не должен сразу затирать текущий ENTRY. Сначала смотрим на графиках, сколько плохих long в дампе он поймал и сколько хороших rebound-входов случайно убил.

### 5. DUMP_AVOID_ML

Статус: `disabled`

План: будущая обучаемая safety-модель.

Роль: учиться на опасных зонах типа `BAD_ACTIVE_DUMP`, `BAD_PRE_KNIFE`, `BAD_SHORT_PRESSURE_NO_REVERSAL`.

Цель:

```text
safety_y_bad_dump
```

Будущие MAE/MFE/hit/order_of_hit можно использовать только как target/audit при обучении. В live X это запрещено.

### 6. REBOUND_ALLOW_ML

Статус: `disabled`

План: будущий анти-переблокировщик.

Роль: отличать хороший вход после flush/retest от падающего ножа, чтобы RiskGate не убивал хорошие входы.

Цель:

```text
safety_y_good_rebound
```

## Главная рабочая цепочка

Текущая R3 цепочка:

```text
continuous X439
-> selected_entry_model из train manifest
-> ENTRY_BASELINE_ML
-> ENTRY_ML_LIVE_SCORE
-> ENTRY_ML_LIVE_DECISION
-> visual_review
```

Планируемая цепочка с RiskGate:

```text
continuous X439
-> selected ENTRY alpha model
-> ENTRY_ALPHA_SCORE / ENTRY_ALPHA_DECISION
-> RISK_GATE audit_only
-> ENTRY_FINAL_DECISION
-> visual_review с отдельными risk-blocked маркерами
```

## Рельсы

1. Не ломаем текущий V5C train/forward.
2. Не меняем X439 без отдельного feature-contract guard.
3. Не включаем RiskGate сразу в боевой режим.
4. Сначала делаем `audit_only` overlay рядом с текущими predictions.
5. Смотрим на графиках опасные зоны вроде `2026-03-18`.
6. Проверяем, что RiskGate блокирует активный дамп, но не убивает хорошие rebound-входы.
7. Только после отдельного guard PASS можно обсуждать `enforce`.

Машинная версия этого паспорта:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json
```
