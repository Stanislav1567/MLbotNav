# Current State

## Codex Desktop CPU/Git Repair 2026-07-23

Статус: `stable_clean_local_branch`.

```text
Codex Desktop: 26.715.10079.0
active branch: codex/git-normalization-cpu-relief
checkpoint commit: 346cd3a
working tree: clean
origin push: NOT_PERFORMED
git fsck --full: PASS
core.fsmonitor: true / active
core.untrackedCache: true
feature.manyFiles: true
core.preloadIndex: true
final 15 s window: 0 new git.exe / 0 taskkill.exe
remaining git.exe: 1 fsmonitor daemon
training / Optuna / live trading: NOT_RUN
data / models: UNCHANGED
```

Два старых повреждённых, но не связанных с ветками loose-объекта сохранены
в `.git/corrupt-object-backup-20260723`. Это локальная резервная копия,
которая не отправляется в GitHub.

## SOL Event Pipeline Design 2026-07-23

Статус: `safe_schema_dry_run_ready`.

```text
source: data/core/bybit_ohlcv
exchange / market: Bybit / linear
symbol / timeframe: SOLUSDT / 1m
source contract: ohlcv_v1
event schema: STAS9_CONTROL_PLANE/MARKET_KNOWLEDGE/EVENT_SCHEMA_RU.md
event directory: STAS9_CONTROL_PLANE/MARKET_KNOWLEDGE/EVENTS/SOL
proposed event types: 9
dry-run: PASS_DRY_RUN_NO_EVENT_RECORDS
event YAML created: 0
datasets created: 0
active mode: SAFE
protected STAS5/STAS8/data/models: UNCHANGED
```

Detector thresholds, feature contract, outcome horizons и label contract ещё
не утверждены. Новый каталог событий содержит только README.

## STAS9 VS Code On-Demand Workflow 2026-07-23

Статус: `safe_ready`.

```text
primary interface: VS Code + Codex
workspace: MLbotNav_STAS9.code-workspace
desktop shortcut: 🤖 STAS9 Workspace
agent mode: CODEX_ROLE
execution: ON_DEMAND
trigger: USER_COMMAND_ONLY
idle action: NONE
background process / watcher / folder scan: disabled
default mode: SAFE
default access: READ_ONLY
terminal launcher: diagnostic fallback only
protected STAS5_ML_CORE / data / models: UNCHANGED
```

STAS9 не работает как отдельная служба. Содержательная работа начинается
только после обращения пользователя к `STAS9` или `STAS9_SENTINEL`.

## STAS9 Agent Routing and SOL Preparation 2026-07-23

Статус: `safe_ready`.

```text
primary role: STAS9_SENTINEL
registered agents: 8
on-demand specialists: 7
new specialist: STAS9_MARKET_RESEARCH
market scope: existing exported SOL candles only
task router: STAS9_CONTROL_PLANE/TASK_ROUTER_RU.md
responsibility memory: STAS9_CONTROL_PLANE/MEMORY/AGENT_RESPONSIBILITIES.yaml
pipeline stage: EVENTS -> FEATURES -> LABELS -> DATASET
training stage: NOT_STARTED
active mode: SAFE
default access: READ_ONLY
protected STAS5/STAS8: UNCHANGED
```

Шаблон `EVENT_SOL_000001.yaml` имеет статус `TEMPLATE_NOT_OBSERVED` и не
является фактическим рыночным событием. Данные SOL в этой задаче не
анализировались.

## STAS9 Persistent Memory 2026-07-23

Статус: `ready`.

```text
runtime role: Codex -> STAS9_SENTINEL
persistent layer: STAS9_CONTROL_PLANE
human-readable state: STAS9_CONTROL_PLANE/MEMORY/STAS9_STATE.md
new-chat guide: STAS9_CONTROL_PLANE/START_HERE_RU.md
active mode after task: SAFE
specialists: 6 ON_DEMAND
protected STAS5-STAS8: UNCHANGED
```

Текущая реализованная архитектура остаётся управляющим read-only слоем.
Исполняемые `schemas/adapters/gates/run_plans` по-прежнему являются
предложением и требуют отдельного ТЗ.

## STAS9 Interactive Assistant 2026-07-23

Статус: `ready`.

```text
primary interface: VS Code + Codex
workspace: MLbotNav_STAS9.code-workspace
desktop shortcut: 🤖 STAS9 Assistant
primary agent: STAS9_SENTINEL
default mode: SAFE
default access: READ_ONLY
voice input: Windows speech-to-text, Win+H, ru
text response: PASS
conversation logs: STAS9_CONTROL_PLANE/LOGS/conversations
terminal fallback: preserved
```

## STAS9 Codex Runtime 2026-07-23

Статус: `ready`.

```text
codex-cli: 0.145.0
model: gpt-5.6-sol
reasoning: xhigh
launcher: PASS
model smoke: STAS9_MODEL_OK
protected STAS5/STAS8: UNCHANGED
```

## STAS9 Multi-Agent Control Layer 2026-07-23

Статус: `safe_multi_agent_layer_ready`.

Текущая точка входа:

```text
C:\Users\007\Desktop\🤖 STAS9 Главный агент.lnk
-> STAS9_CONTROL_PLANE/START/start_STAS9.bat
-> STAS9_SENTINEL
```

Автоматически запускается только `STAS9_SENTINEL`; `AUDITOR`, `MODEL_MANAGER`, `FEATURE_MANAGER`, `LAB`, `VALIDATOR`, `GUARDIAN` используются `ON_DEMAND`. Все политики по умолчанию `READ_ONLY`; обучение, Optuna, изменение моделей, legacy, STAS5–STAS8, live trading и исправление `BROKEN_POINTER` запрещены.

Проверки: YAML `19/19`, файлы агентов `28/28`, журналы `3/3`, launcher `PASS`, защищённый content-tree SHA256 `UNCHANGED`.

## STAS9 Multi-Agent Structure 2026-07-23

Статус: `directory_skeleton_ready`.

В текущем корне проекта создана заданная структура `STAS9_CONTROL_PLANE/`:

```text
STAS9_AGENTS/
  STAS9_SENTINEL/
  STAS9_AUDITOR/
  STAS9_MODEL_MANAGER/
  STAS9_FEATURE_MANAGER/
  STAS9_LAB/
  STAS9_VALIDATOR/
  STAS9_GUARDIAN/
MEMORY/
LOGS/
REPORTS/
RUNTIME/
CONFIG/
PERMISSIONS/
START/
```

Существующие файлы `STAS9_CONTROL_PLANE` сохранены. `STAS5_ML_CORE` и вложенные в него артефакты STAS8 не изменены. Отсутствующие корневые `STAS6` и `STAS7` не создавались.

## STAS9 Control Plane 2026-07-23

Статус: `PASS_STAS9_CONTROL_PLANE_REGISTRIES_READY_NO_TRAINING_NO_FORWARD_STAS5_STAS8_UNCHANGED`.

Создан `STAS9_CONTROL_PLANE/` как read-only управляющий слой. Готовы:

```text
STAS9_CONTROL_PLANE/PROJECT_MAP.md
STAS9_CONTROL_PLANE/MODEL_REGISTRY.yaml
STAS9_CONTROL_PLANE/FEATURE_REGISTRY.yaml
STAS9_CONTROL_PLANE/TASK_REGISTRY.md
STAS9_CONTROL_PLANE/ARCHIVE_POLICY.md
STAS9_CONTROL_PLANE/STAS9_ARCHITECTURE_PROPOSAL_RU.md
```

Аудит зафиксировал неполную нумерацию: STAS6/STAS7 отсутствуют как самостоятельные версии; STAS8 находится внутри STAS5 и не выбран для production. Старый общий active/champion pointer сломан, потому что target joblib отсутствует. Исправление pointer не выполнялось.

Покрытие реестров: `6043` legacy pipeline joblib зарегистрированы тремя полными коллекциями; `37` STAS5 joblib зарегистрированы поштучно; `10` feature contracts/sets; `142` технических задания.

Контроль неизменности STAS5–STAS8: `6196` файлов, metadata SHA256 до/после `367301aa69b966a588fb078f8ff3ee4fd6fa109b688bc848fdeb6154d2f6a506`.

## Codex Project CPU Relief 2026-07-23

Статус: `PASS_CODEX_PROJECT_CPU_RELIEF_APPLIED_NO_DELETE_NO_TRAINING`.

STAS5/ML не грузил CPU: активных Python-процессов не было. Источник - циклический Git scan Codex по generated STAS4 review. Постоянные ignore/exclude применены, текущие процессы Codex переведены в `Idle`. STAS4 untracked scan уменьшен с `258` до `2` Markdown-файлов; общий CPU после стабилизации в среднем `12.3%`. Никакие данные, модели и артефакты не удалялись.

Отчет: `docs/codex/CODEX_PROJECT_CPU_RELIEF_20260723_RU.md`.

## STAS5 V5 Base R2-Style Review Gallery 2026-07-22

Статус: `PASS_V5_BASE_R2_STYLE_REVIEW_GALLERY_READY_NO_TRAINING_NO_FORWARD`.

Создан reusable builder для базовых teacher-графиков в стиле R2/R3/R4:

```text
src/mlbotnav/stas5_v5_base_review_gallery.py
STAS5_ML_CORE/run_stas5_v5_base_review_gallery.ps1
```

Готовая галерея:

```text
STAS5_ML_CORE/artifacts/v5c/review/_BASE_R2_STYLE_VISUAL_REVIEW_20260127_20260227
```

Контроль: `days=32`, `rows=2596`, `GOOD=290`, `BAD=2306`, `no_training=True`, `no_forward=True`. Renderer получил безопасный параметр `title_prefix`, чтобы базовые графики не назывались forward-графиками.

## STAS5 V5C Entry Visual Check Pack 2026-07-22

Статус: `PASS_ENTRY_VISUAL_CHECK_PACKAGE_READY_NO_TRAINING_NO_FORWARD`.

Подготовлена единая папка для ручной проверки всех входов: `BASE 2026-01-27..2026-02-27`, `R2 2026-02-28..2026-03-06`, `R3 2026-03-07..2026-03-13`, `R4 2026-03-14..2026-03-20`. Всего `53` дневных PNG. Это только визуальная подготовка: обучение и forward не запускались.

Пакет:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ENTRY_VISUAL_CHECK_CURRENT_20260127_20260320
```

Индекс:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ENTRY_VISUAL_CHECK_CURRENT_20260127_20260320/STAS5_V5C_ENTRY_VISUAL_CHECK_INDEX_RU.md
```

## STAS5 V5C R4BB Table/ML Audit 2026-07-22

Статус: `PASS_V5C_R4BB_TABLE_ML_AUDIT_NO_FATAL_TABLE_BUG_FOUND`.

Проведен аудит с двумя активными subagents по вопросу, мог ли бардак в таблицах/визуальных preview-баги испортить обучение. Фатальной проблемы в train CSV/allowlist/joblib не найдено: R2/R3/R4 review применились, ENTRY dataset `rows=3285`, `GOOD=517`, `BAD=2768`, `features=463`; RiskGate dataset `rows=627`, `risk_bad_y=400`, `risk_ok=227`, `features=463`. `bb20_*` признаки есть в X (`24`), target/manual/future/STAS8 preview поля в X не входят.

Главный вывод: плохое качество последнего результата сейчас не объясняется потерей ручных правок или старым X439. Причина вероятнее в текущей ML-логике: ENTRY OOF слабый, two-block обучен, но не выбран quality gate, RiskGate обучен слишком широко блокировать, а STAS8/move-capacity пока только preview и не финальный обученный слой.

Отчет:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5C_R4BB_TABLE_ML_AUDIT_20260722_RU.md
```

## STAS8 Soft Capacity V2 Preview R5

Статус: `PASS_V5C_STAS8_SOFT_CAPACITY_V2_PREVIEW_READY_NO_TRAINING_NO_FORWARD_NO_DECISION_CHANGE`.

Собран read-only preview `STAS8_SOFT_CAPACITY_V2` поверх готового R5 no-risk forward:

```text
run_id=stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1
range=2026-03-21..2026-03-27
rows=564
features=463
source_predictions_sha=cd7bc6f7a2855a116d6973ef0a827b160c2843cf9df04c432db4b95b2acfd579
```

Обучение не запускалось, новый forward не запускался, исходный predictions CSV не переписывался. Bollinger-полосы на этих PNG выключены, чтобы видеть только STAS8-маркеры:

```text
green circle = final live ENTER after STAS8
red square = original ENTER demoted to WATCH
red circle = hard risk block
hidden SKIP recall = offline audit only, not drawn as live entry
```

Сравнение режимов:

```text
before STAS8: ENTER=61, WATCH=166, SKIP=337
V1 hard preview: ENTER=1, WATCH=20, SKIP=543
strict:   ENTER=2,  WATCH=118, SKIP=444
balanced: ENTER=15, WATCH=152, SKIP=397
wide:     ENTER=36, WATCH=161, SKIP=367
```

Визуальная семантика исправлена 2026-07-22: раньше зеленые круги ошибочно смешивали финальный live `ENTER`, `WATCH protect` и `SKIP->RECALL_WATCH`. Теперь зеленый круг на цене означает только финальный live `ENTER`. `RECALL_WATCH` остается в CSV/отчете как подсказка для ручного разбора и не рисуется как торговый сигнал.

Маркерные цифры после исправления:

```text
strict:   green=2,  red_square=6,  red_circle=107, hidden_recall=0
balanced: green=15, red_square=11, red_circle=60,  hidden_recall=48
wide:     green=36, red_square=6,  red_circle=30,  hidden_recall=48
```

Главный вывод глазами: `balanced` уже читается честно, но 2026-03-26 все еще оставляет 1 live `ENTER` в падающем канале; `wide` оставляет 9 live `ENTER` на 2026-03-26 и поэтому слишком мягкий для down-channel. Следующий шаг - настраивать down-channel/no-long и post-knife rebound как логику, а не запускать новое обучение. R5 не добавлять в обучение до ручного review и отдельного OK.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/soft_capacity_v2
```

## STAS8 R5 Entry/Move Audit

Статус: `STAS8_R5_ENTRY_MOVE_AUDIT_READY_NO_TRAINING_NO_FORWARD_NO_DECISION_CHANGE`.

Актуальная диагностика R5 `2026-03-21..2026-03-27` показала, что проблема не решается одной настройкой процента `1.1/1.2`. Нужно одновременно чинить recall ENTRY и мягкость STAS8.

Ключевые цифры:

```text
rows=564
before STAS8: ENTER=61, WATCH=166, SKIP=337
after STAS8 preview: ENTER=1, WATCH=20, SKIP=543
all hit_1p2=119
original ENTER/WATCH hit_1p2=46
original SKIP hit_1p2=73
STAS8 blocked good ENTER/WATCH hit_1p2=40
STAS8 kept bad ENTER/WATCH without hit_1p2=15
```

Решение по рельсам: текущий `STAS8_MOVE_CAPACITY_AUDIT_V1` не включать как production-фильтр. Следующий технический шаг - read-only preview `STAS8_SOFT_CAPACITY_V2`: жестко резать `NO_MOVE/LOW_MOVE_CHOP/NO_MOVE_DOWN_CHANNEL`, но защищать `POST_KNIFE_RETEST_EDGE/LOCAL_LOW_REBOUND_EDGE/MOVE_OK_1P2/MOVE_OK_1P5`; `HIGH_VOL_DANGER` разделить на активный нож и отскок после ножа.

Отчет:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1/STAS5_V5C_STAS8_R5_ENTRY_MOVE_AUDIT_20260321_20260327_RU.md
```

## STAS8 R5 Visuals Without Bollinger

Статус: `PASS_STAS8_R5_VISUALS_REBUILT_WITHOUT_BOLLINGER_OVERLAY`.

Актуальные STAS8 audit-preview PNG за `2026-03-21..2026-03-27` теперь собраны без Bollinger-полос. На графиках оставлены свечи, LA-метки, исходные ENTER/WATCH/SKIP, STAS8 зеленые/красные круги и нижние панели силы.

Папка:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1/visual_review
```

Важно: это не новое обучение и не новый forward; decisions и guard-цифры не менялись. Manifest фиксирует `visual_bollinger_preview=false`.

## STAS8 Move Capacity Audit Preview R5

Статус: `PASS_V5C_STAS8_MOVE_CAPACITY_AUDIT_V1_READY_NO_TRAINING_NO_DECISION_CHANGE`.

STAS8 теперь реализован как audit-preview, но не включен в боевой ENTRY/RiskGate pipeline:

```text
enabled=false
selected_for_entry=false
mode=audit_preview_only_not_selected
source_forward_run_id=stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1
range=2026-03-21..2026-03-27
rows=564
features=463
```

Главные выходы:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1
```

Цифры preview: до STAS8 `ENTER=61`, `WATCH=166`, `SKIP=337`; после STAS8-preview `ENTER=1`, `WATCH=20`, `SKIP=543`. Это не финальный боевой режим: preview полезен как красная подсветка опасных long-зон, но текущие rule-пороги слишком жесткие и требуют настройки по PNG до обучения/включения.

No-future guard PASS: live-часть использует causal X463 и закрытые свечи до входа; teacher-grid `40608` строк с future/hit/time_to/mae хранится отдельно и не является live X.

## STAS8 Live Wave + Move Capacity

Статус: `STAS8_LIVE_WAVE_MOVE_CAPACITY_TZ_LOCKED_NO_CODE_NO_TRAINING`.

`STAS8_MOVE_CAPACITY_GRID_V1` в config обновлен, но остается выключенным: `enabled=false`, `mode=deferred_tz_only`. Новая формулировка: сначала live/no-future подтверждение long-режима, потом ENTRY, потом проверка емкости хода, потом RiskGate.

Ключевые правила:

```text
R2/R3/R4 = approved train material
2026-03-21..2026-03-27 = R5 blind-forward/audit-preview, не train до ручного review
1.1% = мягкий WATCH
1.2% = основной ENTER
teacher future/hit/MFE/MAE/time_to запрещены в live X
```

Актуальный документ:

```text
STAS5_ML_CORE/10_STAS8_MOVE_CAPACITY_GRID_TZ_RU.md
```

## STAS5 V5C R4BB Fast Train Audit

Статус: `PASS_V5C_R4BB_FAST_TRAIN_AUDIT_CONFIG_FIXED_NO_IGNORED_FEATURES_FOUND`.

Пользовательский train `stas5_v5c_r4bb_train_20260127_20260320` прошел и создал свежие модели, OOF, metrics, manifest и post-train guards. Аудит подтверждает, что run использовал новый X463/Bollinger contract:

```text
ENTRY: rows=3285, GOOD=517, BAD=2768, features=463, bb20_*=24
RiskGate: rows=627, risk_bad_y=1=400, risk_bad_y=0=227, features=463, bb20_*=24
```

`STAS5_ML_CORE/artifacts/v5c/model/STAS5_V5C_LATEST_TWO_BLOCK_MODEL_RUN.json` указывает на `stas5_v5c_r4bb_train_20260127_20260320`. ENTRY selected model остался `entry_baseline`, потому что two-block не прошел quality gate. Быстрое обучение нормально для текущего объема данных и sklearn-моделей; признаков/датасетов не проигнорировано.

Оговорка из аудита закрыта: в `STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml` блок `active_context.train` теперь указывает на `stas5_v5c_r4bb_train_20260127_20260320` / X463. JSON snapshot пересобран из YAML. Старые check names с привязкой к X439 в коде и текущих R4BB guard/manifests заменены на нейтральные имена.

Актуальный аудит:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5C_R4BB_FAST_TRAIN_AUDIT_RU.md
```

## STAS5 V5C Bollinger Layer V1 X463

Статус: `PASS_V5C_BOLLINGER_LAYER_V1_X463_DATASETS_AND_REVIEW_GALLERY_READY_NO_TRAINING`.

На `2026-07-22` Bollinger уже не только preview на PNG. В код добавлен общий causal-слой `BOLLINGER_LAYER_V1`: `24` новых `bb20_*` признака поверх базовых `439`, новый feature contract `X439_PLUS_BB24_V1`, итог `463` features.

Главные артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_ML_READY_463F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_FEATURE_ALLOWLIST_463F_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_GUARD_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X463_RISK_BAD_Y_V1.csv
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/
```

Контрольные цифры:

```text
ENTRY rows=3285, GOOD=517, BAD=2768, features=463, guard=PASS
RiskGate rows=627, risk_bad_y=1=400, risk_bad_y=0=227, features=463, guard=PASS
ENTRY TrainingGuard=PASS
RiskGate ML TrainingGuard=PASS
```

No-future: `bb_source_time_utc <= entry_time_utc` PASS для ENTRY `3285/3285` ready rows и RiskGate `627/627` ready rows. Audit-колонки `bb_preview_*` не входят в X.

Визуальная витрина R2/R3/R4 с полосами:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA/
```

Обучение и forward после X463 не запускались мной. Следующий шаг - пользователь визуально открывает R2/R3/R4 Bollinger gallery; затем при OK запускает train вручную.

## STAS5 V5C R5 Bollinger Block V0 Red Circles

Статус: `PASS_V5C_BOLLINGER_BLOCK_V0_VISUAL_PREVIEW_WEEK_READY_NO_TRAINING`.

Для R5 ENTRY-only/no-risk forward `2026-03-21..2026-03-27` поверх Bollinger `20/2` создан отдельный недельный preview `BB_BLOCK_V0`: красный круг ставится только на `ENTER/WATCH`, если вход выглядит опасным по положению относительно полос или по нисходящему наклону средней полосы. Это не меняет модель и не меняет решения, а только помогает глазами проверить идею блокировки плохих long-входов.

Правильная папка:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r5_entry_only_forward_20260321_20260327_wide_no_risk/visual_review
```

Итог: `blocked_total=131`, `ENTER=53`, `WATCH=78`. По дням: `7 / 24 / 14 / 23 / 12 / 32 / 19` за `2026-03-21..2026-03-27`. Открывать дневные PNG с именем `STAS5_V5_FORWARD_VISUAL_REVIEW_YYYYMMDD_ENTER_WATCH_BOLLINGER_BLOCK_V0_RED_CIRCLES.png`.

## STAS5 V5C R5 ENTRY-Only No-Risk Bollinger Visual Review

Статус: `PASS_V5C_R5_ENTRY_ONLY_NO_RISK_BOLLINGER_VISUAL_READY_NO_TRAINING`.

Актуальный правильный просмотр для пользователя сейчас находится не в safety-pulse, а в R5 no-risk forward:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r5_entry_only_forward_20260321_20260327_wide_no_risk/visual_review
```

Внутри каждого дня `20260321..20260327` добавлен PNG `*_ENTER_ARROWS_BOLLINGER20_2SIGMA_PREVIEW.png`. Это визуальный слой Bollinger `20/2` поверх обычных ENTRY-only/no-risk графиков. Train/forward/predictions и решения `ENTER/WATCH/SKIP` не менялись.

## STAS5 V5C Bollinger Visual Preview

Статус: `PASS_V5C_BOLLINGER_VISUAL_PREVIEW_READY_NO_TRAINING`.

Для `2026-03-21..2026-03-27` поверх готового `DOWN_CHANNEL_NO_LONG_V1` preview собраны отдельные графики с Bollinger `20/2`. Это визуальный слой для проверки идеи: где интересные входы стоят относительно нижней/средней/верхней полосы и насколько рынок реально расширяет диапазон.

Файл:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1/safety_pulse_preview/down_channel_no_long_v1/
```

Важно: Bollinger сейчас не входит в `X439`, не запускает train/forward и не меняет `ENTRY_ML_LIVE_DECISION`. Кодовый параметр `bollinger_preview` выключен по умолчанию.

## STAS5 V5C ENTRY-Only Wide R5

Статус: `ENTRY_ONLY_WIDE_R5_COMMANDS_READY_NO_TRAINING_STARTED_BY_CODEX`.

Текущая рабочая идея: сначала раздушить ENTRY baseline/wide на всех ручных правках R2/R3/R4 (`2026-02-28..2026-03-20`) поверх базы `2026-01-27..2026-02-27`, без RiskGate enforce. После этого смотреть графики как ENTRY-only: хорошие/плохие входы, входы на хаях, short-channel, отсутствие движения `1.2%`.

Добавлены ключи:

```text
-SkipRiskGateML     для Train: не обучать RiskGate ML в этом run
-DisableRiskGateML  для Forward: не применять RiskGate ML
-EntryDecisionPolicy WideReview  для большего числа кандидатов по train OOF
```

No-future остается прежним: live X = только `439` causal features; `entry_y`, `risk_bad_y`, review/manual/future/outcome не входят в X.

## STAS8 Move Capacity Grid TZ

Статус: `STAS8_DEFERRED_TZ_ONLY_NO_CODE_NO_TRAINING`.

На `2026-07-22` зафиксирована будущая рельса `STAS8`: сетка емкости движения цены. Смысл: не путать живую волатильность с полезным long-edge. Если рынок двигается, но идет active dump / falling knife / down-channel без отскока, long нельзя считать хорошим только из-за волатильности.

`STAS8` сейчас только в ТЗ и YAML-комментариях. Он выключен и не участвует в текущем R4/R5 обучении или forward без отдельного OK.

Документы:

```text
STAS5_ML_CORE/10_STAS8_MOVE_CAPACITY_GRID_TZ_RU.md
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

## STAS5 V5C Down-Channel Safety Pulse Preview

Статус: `PASS_V5C_SAFETY_PULSE_PREVIEW_READY_NO_TRAINING`.

Текущий активный шаг - визуальное согласование preview `DOWN_CHANNEL_NO_LONG_V1` по R4 forward `2026-03-21..2026-03-27`. Это не обучение и не новый forward: исходный predictions CSV сохранен, новые файлы лежат отдельно в `safety_pulse_preview/down_channel_no_long_v1`.

```text
До RiskGate: ENTER=70, WATCH=176, SKIP=318
Старый финал с RISKGATE_ML: ENTER=34, WATCH=37, SKIP=493
DOWN_CHANNEL_NO_LONG_V1 preview: ENTER=40, WATCH=136, SKIP=388
2026-03-26: ENTER=4, WATCH=16, SKIP=68
2026-03-27: ENTER=7, WATCH=18, SKIP=51
```

Пульс использует только causal X439 на момент entry: возвраты/амплитуда, short/long pressure, lower lows/highs, breakdown, knife/grounding/retest/exhaustion. Future/MFE/MAE использовались только для audit-понимания проблемы и не входят в live X.

## STAS5 V5C Safety Pulse Preview

Статус: `PASS_V5C_SAFETY_PULSE_PREVIEW_READY_NO_TRAINING`.

После R4 train/forward по неделе `2026-03-21..2026-03-27` выявлено: `RISKGATE_ML` как единственный safety-layer работает слабо и неровно. Он сильно режет входы, но часть опасных ENTER пропускает. Поэтому перед новым долгим обучением сделан быстрый test-drive без обучения и без пересборки forward:

```text
Forward run: STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1
Preview root: STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1/safety_pulse_preview/
```

Сравнение:

```text
До RiskGate: ENTER=70, WATCH=176, SKIP=318
Текущий финал с RISKGATE_ML: ENTER=34, WATCH=37, SKIP=493
BALANCED_SAFETY_V1 preview: ENTER=3, WATCH=162, SKIP=399
HARD_BLOCK_ONLY_V1 preview: ENTER=27, WATCH=138, SKIP=399
```

Вывод: `BALANCED_SAFETY_V1` слишком душит зеленые входы. Для визуального согласования сейчас правильнее смотреть `HARD_BLOCK_ONLY_V1`: hard-block смертельных режимов taxonomy, но без принудительного удушения всех WARN в WATCH. Это preview-only слой: модели, train, forward и исходный predictions CSV не изменялись.

## STAS5 V5C RiskGate ML Train Wiring Ready

Статус: `RISKGATE_ML_TRAIN_WIRING_READY_TRAINING_GUARDS_PASS_NO_TRAINING`.

Текущая готовая точка перед ручным обучением: `stas5_v5c_r4_train_20260127_20260320`. Обучение и forward не запускались.

Что готово:

```text
ENTRY batch: STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_ML_READY_439F_TARGETS_V1.csv
ENTRY rows=3285, GOOD=517, BAD=2768, features=439
ENTRY TrainingGuard=PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING

RiskGate dataset: STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X439_RISK_BAD_Y_V1.csv
RiskGate rows=627, risk_bad_y=1=400, risk_bad_y=0 explicit safe=227, features=439
RiskGate ML TrainingGuard=PASS_V5C_RISKGATE_ML_TRAINING_GUARD_READY_FOR_TRAINING
```

Новая кодовая рельса: `-Mode Train` теперь должен обучить ENTRY как раньше и затем отдельный `RISKGATE_ML`. Forward после такого Train применяет RiskGate поверх ENTRY, но сохраняет исходное ENTRY-решение для аудита.

## STAS5 V5C Review-Supervised Datasets Ready

Статус: `REVIEW_SUPERVISED_DATASETS_READY_TRAINING_GUARD_PASS_NO_TRAINING`.

Текущая готовая точка перед обучением: `stas5_v5c_r4_train_20260127_20260320`. Само обучение еще не запускалось, forward после него тоже не запускался.

Собран ENTRY train batch:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_ML_READY_439F_TARGETS_V1.csv
days=53
rows=3285
entry_y GOOD=517
entry_y BAD=2768
features=439
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
```

Собран RiskGate train dataset:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X439_RISK_BAD_Y_V1.csv
rows=627
risk_bad_y=1=400
risk_bad_y=0 explicit safe=227
features=439
guard=PASS_V5C_RISKGATE_TRAIN_DATASET_GUARD_READY_NO_TRAINING
```

TrainingGuard уже проверен: `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`.

Контракт не менялся: live X = только `439` causal features. `entry_y`, `risk_bad_y`, `phase_y`, `state_y`, `reason_y`, review-комментарии, PNG, future/postfact/outcome не являются features.

## STAS5 V5C Dataset Rails Locked

Статус: `REVIEW_PACK_DATASET_RAILS_LOCKED_NO_TRAINING`.

Текущий следующий этап: не training. Нужно собрать `X439_SOURCE`, затем `ENTRY_TRAIN_DATASET` и `RISKGATE_TRAIN_DATASET`, после этого прогнать dataset guards и только потом отдельный training guard.

Основа остается прежняя: `2026-01-27..2026-02-27`, `32` дня, `2596` rows, `entry_y GOOD=290`, `entry_y BAD=2306`, `features=439`.

Поверх нее идет approved review-pack: `2026-02-28..2026-03-20`, `R2/R3/R4`, `21` день, `ENTRY rows=689`, `GOOD=227`, `BAD=462`, `RISK BAD=400`, guard `PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING`.

Ожидаемый ENTRY train view: `days=53`, `rows=3285`, `GOOD=517`, `BAD=2768`. RiskGate V1: `risk_bad_y=1` positives `400`; negatives только явно безопасные (`explicit_safe_only`), минимум `227` из reviewed ENTRY GOOD. Неразмеченная тишина не является автоматическим safe.

Главный config: `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml`.

## STAS5 V5C Approved Review Pack R2/R3/R4

Статус: `PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING`.

Свежий source-of-truth для ручной разметки после R2/R3/R4:

```text
STAS5_ML_CORE/artifacts/v5c/review/_APPROVED_REVIEW_PACKS/STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1/
```

В pack вошли `21` день `2026-02-28..2026-03-20`: `ENTRY rows=689`, `GOOD=227`, `BAD=462`, `RISK BAD=400`. Это не обучение и не forward. Это чистый approved teacher/target-пакет для следующей сборки train-данных.

Правило разметки зафиксировано:

```text
хорошо / вход -> entry_y=1
плохо -> entry_y=0
риск плохо -> entry_y=0 + risk_bad_y=1
```

Guard PASS подтвердил: все 21 дня на месте, все LA найдены в source forward entries, дублей и конфликтов нет, каждый RiskGate BAD уже является ENTRY BAD, PNG не является ML source, ручные поля и target-поля не являются live X439.

Следующая рельса: не запускать training сразу. Сначала отдельным шагом собрать train dataset, который берет базу `2026-01-27..2026-02-27` и поверх нее применяет approved review-pack R2/R3/R4 к ENTRY/RiskGate targets, затем выполнить dataset/training guard.

## STAS5 V5C Current Review Cleanup

Статус: `PASS_V5C_CURRENT_REVIEW_CLEANUP_READY_NO_TRAINING`.

Текущий стандарт дневной review-папки: один PNG в корне для открытия глазами:

```text
STAS5_V5C_<ROUND>_USER_REVIEW_YYYYMMDD_CURRENT_REVIEW.png
```

Все прочие PNG (`ALL_ENTRIES`, `ANNOTATED`, preview, старые версии) лежат в `_visual_archive` и не считаются главным графиком. Официальные цифры для будущего ML находятся в `APPROVED.csv/json` и `CURRENT_VISUAL_MANIFEST_V1.json`; PNG не является источником обучения.

Контрольный пересобранный день: `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260301/`.

## STAS5 V5C Review LA Labels Above Markers

Статус: `PASS_V5C_REVIEW_LA_LABELS_ABOVE_MARKERS_FIXED_NO_TRAINING`.

В review-графиках сохранен привычный вид подписей `LAxxx`, но они теперь рисуются верхним слоем после review-маркеров. Для точек, которые попали в ручной review overlay (`GOOD`, обычный `BAD`, `RISK BAD`), подпись `LAxxx` чуть поднята, чтобы зеленые/красные круги и квадраты не закрывали номер сделки.

Пересобрана общая визуальная витрина R2/R3/R4:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/
```

Итог витрины: R2 `7` дней, R3 `7` дней, R4 пока `1` день (`2026-03-18`). Это только PNG/визуальный слой для ручной проверки; training, forward и day passport rebuild не запускались.

## STAS5 V5C Review Gallery R2/R3/R4

Готова общая визуальная папка для ручного review:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/
```

Внутри есть `R2`, `R3`, `R4`. Сейчас собрано `15` дней и `30` PNG: R2 `7` дней, R3 `7` дней, R4 пока `1` день (`2026-03-18`). Это только визуальная витрина, обучение/forward/day rebuild не запускались.

Для R2 открыта папка:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ALL_ROUNDS_VISUAL_REVIEW\R2
```

Для диктовки дальше: `крестик хорошо`/`ромбик хорошо`/`хорошо` идут в ENTRY GOOD (`entry_y=1`), обычное `плохо` идет в ENTRY BAD (`entry_y=0`), а `риск плохо` идет сразу в ENTRY BAD + RiskGate BAD (`entry_y=0 + risk_bad_y=1`).

## STAS5 V5C ENTRY/RiskGate Two Targets

Текущий контракт: одна строка кандидата = один causal набор `X439`, но цели разные. `ENTRY_BASELINE_ML` учится по `entry_y`; будущий обучаемый/guard-слой RiskGate должен учиться по отдельной цели `risk_bad_y`.

ENTRY-разметка: хорошая точка, пропущенный крестик/ромбик как хороший вход -> `entry_y=1`; обычное плохо и risk-плохо -> `entry_y=0`.

RiskGate-разметка: только `риск плохо` -> `risk_bad_y=1`. Значит `риск плохо` дает две цели: `entry_y=0` для ENTRY и `risk_bad_y=1` для RiskGate. Ручные review/risk поля, `entry_y`, `risk_bad_y`, `phase_y`, `state_y`, `reason_y` остаются teacher/target/audit-слоем и не входят в live `X439`.

Важно: отсутствие `риск плохо` не означает автоматически безопасный вход. Для будущего RiskGate dataset отрицательные примеры нужно формировать отдельным правилом, чтобы не считать неразмеченную тишину гарантированным `safe`.

Финальная логика после отдельного RiskGate guard: ENTRY ищет возможность, RiskGate запрещает опасный режим. До enforce RiskGate остается safety/audit/training-target слоем.

## STAS5 V5C Quick Review Ladder

Статус: `PASS_V5C_QUICK_REVIEW_LADDER_READY_NO_TRAINING`.

Текущая ручная рельса для новых review-дней:

```text
14 плохо
22 ромбик хорошо
47 крестик вход
40 риск плохо
47 треугольник риск плохо
```

Правило разделения:

```text
без слова риск -> ENTRY teacher layer
со словом риск -> RiskGate teacher layer
риск хорошо -> запрещено
```

Рабочая команда: `STAS5_ML_CORE/run_stas5_v5c_review_ladder.ps1`. Она пишет ENTRY-ledger и отдельный RiskGate-ledger, а при `-Stage All` передает только ENTRY GOOD ids в старую `run_stas5_v5_day_ladder.ps1`. Ручные review/risk поля не входят в live `X439`.

Для каждого сохраненного review-дня команда также кладет в эту же папку два контрольных PNG: `*_ALL_ENTRIES.png` - чистая копия готового V5C `visual_review`, и `*_ANNOTATED.png` - тот же V5C-график с полосами `Fon/LONG/SHORT/WAVE`, но с подсветкой продиктованных `GOOD/BAD/RISK BAD`. Новый стандарт overlay без стрелок и без индивидуальных плашек: `GOOD` = зеленый круг, `RISK BAD` = ярко-красный круг, обычный `BAD` = красный квадрат. Это только визуальный слой, predictions/training/forward не меняет.

## STAS5 V5C RiskGate Taxonomy V1

Статус: `PASS_V5C_RISKGATE_TAXONOMY_V1_AUDIT_ONLY_READY`.

RiskGate теперь имеет отдельную таксономию режимов: `PRE_DUMP_RISK`, `ACTIVE_DUMP`, `FALLING_KNIFE`, `STRONG_SHORT_PRESSURE`, `SHORT_CONTINUATION`, `PULLBACK_THEN_SHORT`, `SUPPORT_BREAKDOWN`, `CHANNEL_BREAKDOWN`, `POST_PUMP_DUMP`, `LIQUIDATION_CASCADE`.

Важно: это audit-only слой. `ENTRY_BASELINE_ML` продолжает давать входы, `RiskGate` только объясняет и помечает риск поверх готового forward. Production/enforce не включен, `ENTRY_ML_LIVE_DECISION` не меняется.

Официальный пересобранный график/CSV: `STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_audit/20260318/`.

Контроль `2026-03-18`: `ENTER=15`, `BLOCK_HARD=6`, `BLOCK_RISK=3`, `WARN_RISK=3`, `PASS_USER_REBOUND=3`; user-pass `LA059,LA067,LA078`; `RISK_NO_FUTURE_OK=True`.

## STAS5 V5C RiskGate Audit-Only Implemented

Статус: `PASS_V5C_RISKGATE_AUDIT_ONLY_READY`.

RiskGate V0 теперь реализован как отдельный кодовый режим `audit_only`. Он запускается поверх готового V5C forward run, использует только текущий ENTRY score/decision и causal X439 risk-признаки, сохраняет CSV/PNG/RU-отчет рядом с forward run и не меняет predictions.

Активная архитектура:

```text
ENTRY_BASELINE_ML = ищет возможность входа
RISK_GATE_RULE_V0 audit_only = помечает опасность входа
ENTRY_ML_TWO_BLOCK = frozen_not_selected
```

Проверенный контрольный день `2026-03-18`: `ENTER=15`, `BLOCK_HARD=6`, `BLOCK_RISK=3`, `WARN_RISK=3`, `PASS_USER_REBOUND=3`.

## STAS5 V5C RiskGate Preview 2026-03-18

Статус: `PASS_V5C_RISKGATE_PREVIEW_20260318_AUDIT_ONLY_READY`.

Для R3 forward day `2026-03-18` создан отдельный RiskGate V0 preview в режиме `audit_only`. Он показывает, как поверх `ENTRY_BASELINE_ML` выглядели бы `WARN_RISK`, `BLOCK_RISK`, `BLOCK_HARD` по causal X439 risk-признакам. Это не боевое включение и не изменение predictions.

Главный PNG:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_V0.png
```

Итог по `ENTER`: `15` входов, из них `8 BLOCK_HARD`, `3 BLOCK_RISK`, `4 WARN_RISK`, `0 PASS_RISK`.

После пользовательской разметки создана V1 user-pass версия. Пользователь подтвердил проходящие точки: `LA059`, `LA067`, `LA078`. Они сохранены как `PASS_USER_REBOUND`, без изменения модели/predictions.

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_V1_USER_PASS.png
```

Новый вывод для будущей логики: RiskGate нельзя строить только как жесткий `knife/dump=1` запрет; нужен слой исключений `GOOD_REBOUND / GOOD_RETEST_AFTER_KNIFE / GROUNDING_AFTER_DUMP`.

## STAS5 V5C ENTRY_ML_TWO_BLOCK Frozen

Статус: `V5C_ENTRY_TWO_BLOCK_FROZEN_BASELINE_RISKGATE_NEXT`.

В главном YAML `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml` блок `ENTRY_ML_TWO_BLOCK` заморожен: `enabled=false`, `mode=frozen_not_selected`. Активный entry остается `ENTRY_BASELINE_ML`. Следующий рабочий фокус - `RiskGate V0` только в режиме `audit_only`.

## STAS5 V5C YAML Config Commented

Статус: `V5C_YAML_CONTROL_CONFIG_COMMENTED_RU_NO_CODE_WIRING`.

Главный config `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml` теперь содержит русские комментарии по каждому ML-блоку и guard-разделу. Это только пояснения для ручного управления; значения config, код раннеров, training, forward и predictions не менялись.

## STAS5 V5C Main YAML ML Control Config

Статус: `V5C_MAIN_YAML_CONTROL_CONFIG_READY_NO_CODE_WIRING`.

Главный управляемый config:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

Руками управляем ML-блоками только через YAML. JSON и RU.md оставлены как справка/снимок и не являются source-of-truth. В YAML текущий active entry = `ENTRY_BASELINE_ML`, two-block обучен, но не выбран, RiskGate V0 выключен и задан как следующий `audit_only` overlay.

## STAS5 V5C ML Control Config Ready

Статус: `V5C_ML_CONTROL_CONFIG_READY_RISKGATE_NOT_IMPLEMENTED`.

Текущая управляющая точка по ML-блокам создана:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
```

Факт по R3: train `stas5_v5c_r3_train_20260127_20260313` завершен, post-train guard `PASS`, selected entry model = `entry_baseline`. Two-block обучен, но не выбран, потому что quality gate оставил baseline. Forward review week3 `2026-03-14..2026-03-20` существует в режиме `wide_review`; это не production.

Следующий правильный смысловой шаг: не ломать текущий ENTRY, а добавить `RISK_GATE_RULE_V0` сначала как `audit_only` overlay поверх текущих predictions, чтобы увидеть на графиках активные дампы/ножи и не потерять хорошие rebound-входы.

## STAS5 V5C R3 Train PASS

Статус: `PASS_V5_TWO_BLOCK_ML_TRAINED_POST_TRAIN_GUARD_READY_FOR_FORWARD`.

R3 обучение завершено для `TrainRunId=stas5_v5c_r3_train_20260127_20260313`. Train manifest: `STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r3_train_20260127_20260313/STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json`.

Контроль: `rows=3726`, `days=46`, `entry_y 1=432`, `entry_y 0=3294`, `features=439`, post-train guard `PASS`. Модели baseline, phase/state и entry_ml созданы; OOF rows `3726`, null `0`.

Селектор выбрал `entry_baseline`, потому что two-block не улучшил качество по gate. Следующая blind-неделя `2026-03-14..2026-03-20` имеет свечи и готова к forward-запуску пользователем.

## STAS5 V5C R3 Training Guard PASS

Статус: `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING_WAIT_USER_TRAIN`.

R3 `TrainingGuard` прошел PASS для `TrainRunId=stas5_v5c_r3_train_20260127_20260313`. Guard использует правильный R3 batch `2026-01-27..2026-03-13`, где уже применены пользовательские правки за `2026-03-07..2026-03-13`.

Проверенные цифры: `days=46`, `rows=3726`, `entry_y 1=432`, `entry_y 0=3294`, `features=439`. В run dir пока нет model/joblib/train manifest; обучение не запускалось. Следующий шаг - пользователь запускает R3 `Train` тем же run_id.

## STAS5 V5C R3 Batch Ready

Статус: `PASS_V5C_R3_BATCH_20260127_20260313_READY_NO_TRAINING_RUN`.

R3-правки пользователя за `2026-03-07..2026-03-13` внедрены. Все продиктованные GOOD/BAD сохранены в approved review-ledger, дневные V5 passports пересобраны, затем собран непрерывный V5C train batch `2026-01-27..2026-03-13`.

Итог batch:

```text
days=46
rows=3726
entry_y 1=432
entry_y 0=3294
features=439
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
```

Главные файлы:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_ML_READY_439F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_GUARD_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_MANIFEST_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_AUDIT_RU.md
```

Граница: R3 training не запускался, R3 forward не запускался. Следующий шаг - команда `TrainingGuard`; после PASS пользователь отдельно запускает `Train`.

## STAS5 V5C R3 Review Draft 2026-03-13

Статус: `R3_REVIEW_20260313_DRAFT_WAIT_USER_CONFIRM_CLOSE_DAY`.

Пользователь дал ручную разметку для `2026-03-13` по wide-review run `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`. Сохранен draft-ledger: `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/20260313/STAS5_V5C_R3_USER_REVIEW_20260313_DRAFT.csv`.

Итог draft: `22` отмеченных строки, `GOOD=9`, `BAD=13`. GOOD ids: `LA003`, `LA014`, `LA030`, `LA032`, `LA037`, `LA042`, `LA043`, `LA048`, `LA054`. BAD ids: `LA012`, `LA013`, `LA044`, `LA045`, `LA046`, `LA047`, `LA049`, `LA050`, `LA051`, `LA052`, `LA053`, `LA058`, `LA073`.

Ключевой вывод дня: пользователь отметил жесткий памп, затем дамп и просадку около `6%`; особенно плохая серия `LA046..LA053`, нужен будущий фильтр `памп-скат/нож`. `LA044` и `LA045` сохранены как явные BAD-контекстные кандидаты у хая перед дампом, хотя model_decision у них `SKIP`. Passport пока не пересобирался, обучение не запускалось.

По состоянию на сейчас draft-разметка сохранена за всю week2: `2026-03-07..2026-03-13`. Следующий шаг: пользователь подтверждает закрытие дней или дает правки; после подтверждения можно делать approved-ledger и пересборку дневных V5 passports.

## STAS5 V5C R3 Review Draft 2026-03-12

Статус: `R3_REVIEW_20260312_DRAFT_WAIT_USER_CONFIRM_CLOSE_DAY`.

Пользователь дал ручную разметку для `2026-03-12` по wide-review run `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`. Сохранен draft-ledger: `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/20260312/STAS5_V5C_R3_USER_REVIEW_20260312_DRAFT.csv`.

Итог draft: `16` отмеченных строк, `GOOD=12`, `BAD=4`. GOOD ids: `LA015`, `LA021`, `LA025`, `LA033`, `LA049`, `LA050`, `LA053`, `LA054`, `LA055`, `LA058`, `LA070`, `LA086`. BAD ids: `LA006`, `LA008`, `LA052`, `LA067`. `LA015` отмечен как лучший вход после ската; `LA055` сохранен как `yellow_x`/GOOD; `LA070` и `LA086` по predictions являются `WATCH`, поэтому сохранены как `yellow_diamond`/GOOD.

Passport пока не пересобирался, обучение не запускалось. Следующий шаг: пользователь подтверждает `12 марта день закрыт` или дает правки.

## STAS5 V5C R3 Review Draft 2026-03-11

Статус: `R3_REVIEW_20260311_DRAFT_WAIT_USER_CONFIRM_CLOSE_DAY`.

Пользователь дал ручную разметку для `2026-03-11` по wide-review run `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`. Сохранен draft-ledger: `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/20260311/STAS5_V5C_R3_USER_REVIEW_20260311_DRAFT.csv`.

Итог draft: `12` отмеченных строк, `GOOD=12`, `BAD=0`. GOOD ids: `LA008`, `LA014`, `LA034`, `LA040`, `LA042`, `LA044`, `LA045`, `LA046`, `LA051`, `LA052`, `LA053`, `LA055`. `LA044` и `LA053` сохранены как `yellow_x`/GOOD, то есть пропущенные хорошие входы. `LA058` проверен в predictions, но сохранен только как context note, не как training label, потому что пользователь указал его как границу, после которой входы неинтересны, без финальной оценки хорошо/плохо.

Passport пока не пересобирался, обучение не запускалось. Следующий шаг: пользователь подтверждает `11 марта день закрыт` или дает правки.

## STAS5 V5C R3 Review Draft 2026-03-10

Статус: `R3_REVIEW_20260310_DRAFT_WAIT_USER_CONFIRM_CLOSE_DAY`.

Пользователь дал ручную разметку для `2026-03-10` по wide-review run `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`. Сохранен draft-ledger: `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/20260310/STAS5_V5C_R3_USER_REVIEW_20260310_DRAFT.csv`.

Итог draft: `16` отмеченных строк, `GOOD=9`, `BAD=7`. GOOD ids: `LA005`, `LA013`, `LA022`, `LA029`, `LA039`, `LA043`, `LA044`, `LA046`, `LA071`. BAD ids: `LA041`, `LA042`, `LA055`, `LA057`, `LA058`, `LA059`, `LA068`. `LA052` проверен в predictions, но сохранен только как context note, не как training label, потому что пользователь упомянул его как хай/контекст без финальной оценки хорошо/плохо.

Passport пока не пересобирался, обучение не запускалось. Следующий шаг: пользователь подтверждает `10 марта день закрыт` или дает правки.

## STAS5 V5C R3 Review Draft 2026-03-09

Статус: `R3_REVIEW_20260309_DRAFT_WAIT_USER_CONFIRM_CLOSE_DAY`.

Пользователь дал ручную разметку для `2026-03-09` по wide-review run `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`. Сохранен draft-ledger: `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/20260309/STAS5_V5C_R3_USER_REVIEW_20260309_DRAFT.csv`.

Итог draft: `13` отмеченных строк, `GOOD=12`, `BAD=1`. GOOD ids: `LA006`, `LA007`, `LA011`, `LA014`, `LA024`, `LA025`, `LA039`, `LA042`, `LA048`, `LA055`, `LA063`, `LA067`. BAD ids: `LA047`. `LA067` пользователь назвал "треугольник, ромбик"; по predictions это `WATCH`, поэтому marker сохранен как `yellow_diamond`, итоговая метка GOOD.

Passport пока не пересобирался, обучение не запускалось. Следующий шаг: пользователь подтверждает `9 марта день закрыт` или дает правки.

## STAS5 V5C R3 Review Draft 2026-03-08

Статус: `R3_REVIEW_20260308_DRAFT_WAIT_USER_CONFIRM_CLOSE_DAY`.

Пользователь дал ручную разметку для `2026-03-08` по wide-review run `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`. Сохранен draft-ledger: `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/20260308/STAS5_V5C_R3_USER_REVIEW_20260308_DRAFT.csv`.

Итог draft: `15` отмеченных строк, `GOOD=10`, `BAD=5`. GOOD ids: `LA020`, `LA027`, `LA031`, `LA040`, `LA045`, `LA056`, `LA057`, `LA064`, `LA073`, `LA074`. BAD ids: `LA008`, `LA044`, `LA055`, `LA071`, `LA077`. Крестики `LA027`, `LA031`, `LA064` сохранены как GOOD/пропущенные входы.

Passport пока не пересобирался, обучение не запускалось. Следующий шаг: пользователь подтверждает `8 марта день закрыт` или дает правки.

## STAS5 V5C R3 Review Draft 2026-03-07

Статус: `R3_REVIEW_20260307_DRAFT_WAIT_USER_CONFIRM_CLOSE_DAY`.

Пользователь дал ручную разметку для `2026-03-07` по wide-review run `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`. Сохранен draft-ledger: `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/20260307/STAS5_V5C_R3_USER_REVIEW_20260307_DRAFT.csv`.

Итог draft: `13` отмеченных строк, `GOOD=9`, `BAD=4`. GOOD ids: `LA006`, `LA011`, `LA021`, `LA027`, `LA046`, `LA051`, `LA054`, `LA063`, `LA064`. BAD ids: `LA005`, `LA044`, `LA057`, `LA062`. Важное уточнение: `LA057` зафиксирован как BAD, потому что пользователь исправил первое "хорошо" на "057 плохо".

Passport пока не пересобирался, обучение не запускалось. Следующий шаг: пользователь подтверждает `7 марта день закрыт` или дает правки.

## STAS5 V5C R2Q WideReview V2 Fixed As R3 Review Source

Статус: `V5C_R2Q_WIDE_V2_READY_FOR_USER_REVIEW_AND_R3_LABELS`.

Последний рабочий прогон для ручного review зафиксирован как `6+ из 10` review-режим, не production: `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`. Диапазон forward `2026-03-07..2026-03-13`, train source `stas5_v5c_r2q_train_20260127_20260306`, selected ENTRY model `entry_baseline`, policy `wide_review`, пороги только по train OOF: `enter=0.3012377066`, `watch=0.1576703673`.

Итоги: `rows=554`, `ENTER=64`, `WATCH=167`, `SKIP=323`, visual PNG `14`, forward guard `PASS`, visual guard `PASS`. Контрольная точка сохранена: `STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r2q_forward_20260307_20260313_wide_v2/STAS5_V5C_R2Q_WIDE_V2_REVIEW_CONTROL_POINT_RU.md`.

Следующий шаг: пользователь размечает графики `2026-03-07..2026-03-13`; Codex сохраняет review-ledger по дням, пересобирает дневные passports с `GoodIds`, затем готовит R3 train range `2026-01-27..2026-03-13`.

## STAS5 V5C R2Q Decision Policy Fixed After Too Few Entries

Статус: `V5C_R2Q_DECISION_POLICY_WIDENED_WAIT_USER_FORWARD_RERUN`.

Пользователь проверил forward `2026-03-07..2026-03-13` с `-EntryDecisionPolicy Normal` и указал, что входов стало слишком мало. Аудит подтвердил: старый `Normal` использовал train OOF quantile `enter=0.965 / watch=0.815` и на forward-неделе дал только `ENTER=5`, `WATCH=54`, `SKIP=495`. Причина не в обучении и не в X439, а в слишком высоком decision threshold относительно просевшего forward score distribution.

Исправлено в коде: `Normal` теперь `enter=0.90 / watch=0.60`, ожидаемо на том же score даст около `ENTER=25`, `WATCH=148`, `SKIP=381`; `WideReview` теперь `enter=0.80 / watch=0.50`, ожидаемо около `ENTER=64`, `WATCH=167`, `SKIP=323`. Пороги по-прежнему считаются только по train OOF predictions, без forward outcome labels и без подсмотра в будущее.

Проверки: `py_compile PASS`; PowerShell wrapper syntax `PASS`; `pytest tests/test_stas5_v5_continuous_ml.py tests/test_stas5_v5_two_block_ml.py` = `7 passed`.

## STAS5 V5C R2Q Normal Forward Policy Ready

Статус: `V5C_R2Q_NORMAL_FORWARD_POLICY_READY_WAIT_USER_RUN`.

Добавлен режим `-EntryDecisionPolicy Normal` для V5C forward. Он не переобучает модель и не меняет X439/разметку; только берет более широкий порог решения из train OOF score distribution. Forward `2026-03-07..2026-03-13` не используется для threshold tuning.

Проверки: `py_compile PASS`; PowerShell wrapper syntax `PASS`; `pytest tests/test_stas5_v5_two_block_ml.py tests/test_stas5_v5_continuous_ml.py` = `6 passed`.

Следующий шаг: пользователь запускает forward с `-EntryDecisionPolicy Normal` и run_id `stas5_v5c_r2q_forward_20260307_20260313_normal`.

## STAS5 V5C R2Q Train Multiclass Fix Ready

Статус: `V5C_R2Q_TRAIN_MULTICLASS_SOLVER_FIX_READY_RETRY_TRAIN`.

`TrainingGuard` для `stas5_v5c_r2q_train_20260127_20260306` прошел PASS, но первый запуск `Train` упал на `phase_y/state_y` из-за `liblinear`, который не поддерживает multiclass. Это была ошибка выбора модели для `MARKET_PHASE_STATE_ML`, не ошибка batch/guard/разметки.

Исправлено: phase/state теперь используют `PHASE_STATE_MODEL_KIND = "extra_trees_balanced"` во всех местах обучения и аудита. ENTRY binary-кандидаты не изменены. Проверки прошли: `py_compile PASS`, профильный `pytest` = `5 passed`.

Текущий следующий шаг: повторить команду `Train` для того же run_id `stas5_v5c_r2q_train_20260127_20260306`. Forward запускать только после post-train guard PASS.

## STAS5 V5C R2 ML Quality Fix Ready

Статус: `V5C_R2_ML_QUALITY_AUDIT_FIX_READY_NO_NEW_TRAINING`.

R2 train/forward фактически уже существуют и lineage чистый: R2 train `stas5_v5c_r2_train_20260127_20260306` взял batch `2026-01-27..2026-03-06`, R2 forward `stas5_v5c_r2_forward_20260307_20260313` взял этот train manifest. Проблема качества была не в подмене старым R1, а в ML-логике: свежая review-неделя имела обычный вес, ENTER-порог был p90, phase/state SGD шумел, а two-block шел в forward даже когда baseline лучше.

Кодовая рельса исправлена без нового боевого обучения: добавлены sample weights от `2026-02-28`, ENTRY-кандидаты `logistic_balanced/extra_trees_balanced`, precision/Wilson threshold, стабильный phase/state без SGD, raw-proba guard без тихой NaN/inf-очистки и selector baseline vs two-block. Следующий рабочий шаг: пользователь запускает `TrainingGuard -> Train -> Forward` с run_id `stas5_v5c_r2q_train_20260127_20260306` по командам из `docs/codex/commands.md`.

Отчет: `STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_R2_ML_QUALITY_AUDIT_AND_FIX_20260717_RU.md`.

## STAS5 V5C R2 Batch Ready

Статус: `PASS_V5C_R2_BATCH_20260127_20260306_READY_NO_TRAINING_RUN`.

Активный следующий этап: R2 обучение должно идти на `2026-01-27..2026-03-06`, то есть старая база 32 дня плюс закрытая пользователем review-неделя `2026-02-28..2026-03-06`. R2 batch уже собран в `STAS5_ML_CORE/artifacts/v5c/`:

```text
STAS5_V5C_BATCH_20260127_20260306_ML_READY_439F_TARGETS_V1.csv
STAS5_V5C_BATCH_20260127_20260306_FEATURE_ALLOWLIST_439F_V1.json
STAS5_V5C_BATCH_20260127_20260306_MANIFEST_V1.json
STAS5_V5C_BATCH_20260127_20260306_GUARD_V1.json
STAS5_V5C_BATCH_20260127_20260306_AUDIT_RU.md
```

Цифры: `39` дней, `3172` строк, `entry_y 1=359`, `entry_y 0=2813`, `439` causal features. Guard `PASS`: target/manual не в X, forbidden/future/postfact/hit/TP/Stas3/exit/old ML leakage не в X, `cs/fcs` source-time не позже `entry_time_utc`, дублей нет.

Кодовая рельса исправлена: `TrainingGuard` и `Train` теперь принимают `TrainStartDay/TrainEndDay`, а общий two-block helper принимает динамические expected counts. Обучение и новый forward после этого изменения не запускались.

Следующий рабочий порядок:

```text
1. Пользователь запускает R2 TrainingGuard.
2. После PASS пользователь запускает R2 Train.
3. После post-train guard PASS пользователь запускает blind forward week2: 2026-03-07..2026-03-13.
```

## STAS5 V5C R2 Text Encoding Fixed

Статус: `UTF8_RUSSIAN_TEXT_RESTORED_NO_LABEL_CHANGE`.

Аудит кракозяб по R2 review-слою завершен. Реальные повреждения были в review-ledger файлах за `2026-03-02..2026-03-06`: вместо русских причин стояли question-mark placeholders.

Перезаписаны CSV/JSON/RU.md для всех закрытых дней `2026-02-28..2026-03-06` единым UTF-8 форматом. После фикса:

```text
review text audit=PASS
label audit=PASS
days=7
GoodIds/BAD/entry_y unchanged
training=false
forward=false
```

Отчет: `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/STAS5_V5C_R2_TEXT_ENCODING_AUDIT_20260717_RU.md`.

## STAS5 V5C R2 Review Week Closed

Статус: `USER_APPROVED_R2_REVIEW_WEEK_20260228_20260306_CLOSED_FULL_READY`.

День `2026-03-06` закрыт пользователем для R2-разметки. Сохранены review-ledger артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260306/STAS5_V5C_R2_USER_REVIEW_20260306_APPROVED.csv
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260306/STAS5_V5C_R2_USER_REVIEW_20260306_APPROVED.json
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260306/STAS5_V5C_R2_USER_REVIEW_20260306_APPROVED_RU.md
```

Дневной approved package собран через `run_stas5_v5_day_ladder.ps1`:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260306/
rows=87
entry_y 1=6 / 0=81
features=439
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

GOOD ids: `LA006`, `LA023`, `LA028`, `LA047`, `LA055`, `LA066`. Явные BAD для аудита: `LA019`, `LA050`, `LA051`, `LA053`, `LA054`, `LA059`, `LA062`, `LA072`, `LA078`. Спорное `72/73` разрешено по source predictions: `LA072=ENTER`, `LA073=WATCH`, поэтому зафиксирован `LA072`.

R2 training пока не запускался. Закрыта вся R2 teacher-неделя `2026-02-28..2026-03-06`. Ближайший шаг: собрать R2 batch dataset и отдельный R2 batch guard; не запускать обучение напрямую.

## STAS5 V5C R2 Review 2026-03-05 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260305_CLOSED_FULL_READY`.

День `2026-03-05` закрыт пользователем для R2-разметки. Сохранены review-ledger артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260305/STAS5_V5C_R2_USER_REVIEW_20260305_APPROVED.csv
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260305/STAS5_V5C_R2_USER_REVIEW_20260305_APPROVED.json
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260305/STAS5_V5C_R2_USER_REVIEW_20260305_APPROVED_RU.md
```

Дневной approved package собран через `run_stas5_v5_day_ladder.ps1`:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260305/
rows=85
entry_y 1=11 / 0=74
features=439
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

R2 training пока не запускался. Закрытые R2 teacher-дни: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`, `2026-03-04`, `2026-03-05`. Ближайший шаг: закрывать следующий forward-день `2026-03-06`.

## STAS5 V5C R2 Review 2026-03-04 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260304_CLOSED_FULL_READY`.

День `2026-03-04` закрыт пользователем для R2-разметки. Сохранены review-ledger артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260304/STAS5_V5C_R2_USER_REVIEW_20260304_APPROVED.csv
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260304/STAS5_V5C_R2_USER_REVIEW_20260304_APPROVED.json
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260304/STAS5_V5C_R2_USER_REVIEW_20260304_APPROVED_RU.md
```

Дневной approved package собран через `run_stas5_v5_day_ladder.ps1`:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260304/
rows=72
entry_y 1=9 / 0=63
features=439
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

R2 training пока не запускался. Закрытые R2 teacher-дни: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`, `2026-03-04`. Ближайший шаг: закрывать следующий forward-день `2026-03-05`.

## STAS5 V5C R2 Review 2026-03-03 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260303_CLOSED_FULL_READY`.

День `2026-03-03` закрыт пользователем для R2-разметки. Сохранены review-ledger артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260303/STAS5_V5C_R2_USER_REVIEW_20260303_APPROVED.csv
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260303/STAS5_V5C_R2_USER_REVIEW_20260303_APPROVED.json
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260303/STAS5_V5C_R2_USER_REVIEW_20260303_APPROVED_RU.md
```

Дневной approved package собран через `run_stas5_v5_day_ladder.ps1`:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260303/
rows=89
entry_y 1=12 / 0=77
features=439
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

R2 training пока не запускался. Закрытые R2 teacher-дни: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`. Ближайший шаг: закрывать следующий forward-день `2026-03-04`.

## STAS5 V5C R2 Review 2026-03-02 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260302_CLOSED_FULL_READY`.

День `2026-03-02` закрыт пользователем для R2-разметки. Сохранены review-ledger артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260302/STAS5_V5C_R2_USER_REVIEW_20260302_APPROVED.csv
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260302/STAS5_V5C_R2_USER_REVIEW_20260302_APPROVED.json
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260302/STAS5_V5C_R2_USER_REVIEW_20260302_APPROVED_RU.md
```

Дневной approved package собран через `run_stas5_v5_day_ladder.ps1`:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260302/
rows=81
entry_y 1=12 / 0=69
features=439
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

R2 training пока не запускался. Закрытые R2 teacher-дни: `2026-02-28`, `2026-03-01`, `2026-03-02`. Ближайший шаг: закрывать следующий forward-день `2026-03-03`.

## STAS5 V5C R2 Review 2026-03-01 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260301_CLOSED_FULL_READY`.

День `2026-03-01` закрыт пользователем для R2-разметки. Сохранены review-ledger артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260301/STAS5_V5C_R2_USER_REVIEW_20260301_APPROVED.csv
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260301/STAS5_V5C_R2_USER_REVIEW_20260301_APPROVED.json
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260301/STAS5_V5C_R2_USER_REVIEW_20260301_APPROVED_RU.md
```

Дневной approved package собран через `run_stas5_v5_day_ladder.ps1`:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260301/
rows=81
entry_y 1=9 / 0=72
features=439
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

R2 training пока не запускался. Закрытые R2 teacher-дни: `2026-02-28`, `2026-03-01`. Ближайший шаг: закрывать следующий forward-день `2026-03-02`.

## STAS5 V5C R2 Review 2026-02-28 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260228_CLOSED_FULL_READY`.

День `2026-02-28` закрыт пользователем для R2-разметки. Сохранены review-ledger артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260228/STAS5_V5C_R2_USER_REVIEW_20260228_APPROVED.csv
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260228/STAS5_V5C_R2_USER_REVIEW_20260228_APPROVED.json
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260228/STAS5_V5C_R2_USER_REVIEW_20260228_APPROVED_RU.md
```

Дневной approved package пересобран через `run_stas5_v5_day_ladder.ps1`:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260228/
rows=81
entry_y 1=10 / 0=71
features=439
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

R2 training пока не запускался. Ближайший шаг: закрывать следующий forward-день `2026-03-01` таким же review-ledger форматом.

## STAS5 V5C WAVE Strip Cumulative Carry Ready

Статус: `USER_APPROVED_V5C_FORWARD_VISUAL_REVIEW_CHARTS_OK`.

Пользователь 2026-07-17 подтвердил: текущие графики норм. Этот формат фиксируется как рабочий visual-standard для V5C forward review.

Текущие графики V5C forward `2026-02-28..2026-03-06` перерисованы. WAVE-полоса теперь покрывает доступный конец свечей каждого дня: `last_wave_end == available_end` для 7/7 дней. Серый/черный служебный хвост после active wave не остается.

Ключевые проверки manifest:

```text
macro_wave_strip_covers_available_candle_end=PASS
macro_wave_tail_gap_filled_without_rendering_gap=PASS
cross_day_wave_labels_use_cumulative_true_start_pct=PASS
tail_gap_rows_filled_total=7
tail_gap_minutes_filled_total=298.0
cross_day_wave_rows_total=13
rendered_gap_rows_total=0
```

Пример: `2026-03-02` в начале дня показывает carry из предыдущего дня с cumulative percent, а последняя `SHORT ACTIVE` тянется до `2026-03-03T00:00:00Z`.

## STAS5 V5C Forward Visual Review Updated

Статус: `PASS_V5C_FORWARD_VISUAL_REVIEW_WITH_CONTINUOUS_STRENGTH_STRIP`.

Текущий рабочий визуальный слой для проверки forward `2026-02-28..2026-03-06` теперь находится здесь:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343/visual_review/
```

В overview PNG добавлен блок `Fon / LONG / SHORT / WAVE` между ценой и score. Для V5C он берется из `ohlcv_contexts`, то есть имеет хвост предыдущего дня и не является 24-часовым сбросом. Серые служебные `GAP` в WAVE не рисуются: `rendered_gap_rows_total=0`.

Проверено: `png_count=14`, все 7 дней используют `CONTINUOUS_CONTEXT_OHLCV`, `context_rows=2160`; predictions CSV не изменился по SHA256 после render.

Граница: это review-only слой, не feature source для ML и не изменение решений модели.

## STAS5 V5C Continuous Train + Forward Done

Статус: `PASS_V5C_CONTINUOUS_TWO_BLOCK_FORWARD_20260228_20260306_BLIND_NO_FUTURE`.

Текущий рабочий контур теперь `V5C_CONTINUOUS`: обучение и blind forward собраны без сброса рыночной структуры на границе дня. Старый дневной V5 сохранен как контрольный run.

Контекстная политика:

```text
rolling_past_context
context_start_day=2026-01-27
context_warmup_minutes=720
feature_rule=FULL274 -> cs_* -> fcs_*; source_time <= entry_time_utc
```

V5C batch:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260227_ML_READY_439F_TARGETS_V1.csv
rows=2596
entry_y 1=290 / 0=2306
features=439
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
```

V5C train:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_continuous_train_20260716_154826
post-train guard=PASS_V5_TWO_BLOCK_POST_TRAIN_GUARD_READY_FOR_FORWARD
baseline ROC-AUC=0.6569167389418907 PR-AUC=0.17950987215851025
two-block ROC-AUC=0.6597878099111762 PR-AUC=0.18064179174496617
```

V5C forward:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343
rows=576
ENTER=62 / WATCH=121 / SKIP=393
visual PNG=14
```

Контроль midnight-reset: `2026-02-28 LA001` имеет `cs_context_rows=748`, `cs_rows_240m=240`, `fcs_context_before_entry=1`. Значит forward реально использует хвост прошлого дня и не стартует структуру с нуля в 00:00.

Главный отчет:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_CONTINUOUS_TRAIN_FORWARD_20260716_RU.md
```

Следующий шаг: открыть `visual_review` текущего V5C forward, глазами проверить `62 ENTER`, затем сравнить V5C continuous с дневным V5 run и baseline.

## STAS5 V5 Forward Visual Review With All LA Labels

Статус: `PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES`.

Для текущего V5 forward `2026-02-28..2026-03-06` создан визуальный review-слой:

```text
STAS5_ML_CORE/artifacts/v5/forward/runs/stas5_v5_forward_20260228_20260306_20260716/visual_review/
```

Итог: `14` PNG = `7` дневных overview с желтыми `LAxxx` по всем кандидатам + `7` closeup-листов по входам. День `2026-02-28` и `2026-03-04` визуально проверены: длинные зеленые стрелки/боксы убраны; `ENTER` виден зеленым треугольником, `WATCH` желтым ромбом, `SKIP` желтым X.

Последняя правка layout: подписи `LAxxx` отсортированы по номеру кандидата и соединены с точкой тонкой желтой линией, чтобы `LA001 -> LA002 -> ...` читались последовательно, а не хаотично.

Манифест:

```text
STAS5_ML_CORE/artifacts/v5/forward/runs/stas5_v5_forward_20260228_20260306_20260716/visual_review/STAS5_V5_FORWARD_VISUAL_REVIEW_MANIFEST_V1.json
```

Граница: это только отрисовка готовых predictions и OHLCV. Обучение не запускалось заново, решения модели не менялись.

## STAS5 V5 Two-Block Train + Forward Done

Статус: `PASS_TRAIN_AND_FORWARD_DONE_REVIEW_REQUIRED`.

Обучение V5 two-block выполнено на `2026-01-27..2026-02-27`: `2596` rows, `290` GOOD, `2306` BAD, `X439`.

Blind/no-future forward выполнен на `2026-02-28..2026-03-06`: `576` rows, `ENTER=20`, `WATCH=120`, `SKIP=436`.

Главный отчет:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_TWO_BLOCK_TRAIN_FORWARD_20260716_RU.md
```

Главный training run:

```text
STAS5_ML_CORE/artifacts/v5/model/runs/stas5_v5_two_block_train_20260716_32d/
```

Главный forward run:

```text
STAS5_ML_CORE/artifacts/v5/forward/runs/stas5_v5_forward_20260228_20260306_20260716/
```

Важный ML-вывод: по OOF baseline лучше two-block (`ROC-AUC 0.6564` против `0.6377`, `PR-AUC 0.1813` против `0.1561`). Two-block пока не production-победитель; нужен review forward ENTER и baseline-forward сравнение.

## STAS5 V5 Two-Block ML TZ Ready

Статус: `TZ_DRAFT_READY_FOR_USER_REVIEW_NO_TRAINING`.

Следующий этап V5 ML расписан в ТЗ:

```text
STAS5_ML_CORE/09_STAS5_V5_TWO_BLOCK_ML_TZ_RU.md
```

Текущая утвержденная база остается прежней: `2026-01-27..2026-02-27`, `32` дня, `2596` rows, `entry_y 1=290 / 0=2306`, `439` causal features, batch guard `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING`.

Архитектура следующего этапа:

```text
ENTRY_BASELINE_ML: X439 -> entry_y
MARKET_PHASE_STATE_ML: X439 -> phase_y/state_y
ENTRY_ML: X439 + OOF/live phase/state predictions -> entry_y
```

Training и forward еще не запускались. Следующий правильный шаг: не обучение, а реализация отдельного training guard `STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1`.

## STAS5 V5 Batch Dataset 2026-01-27..2026-02-27 Ready

Статус: `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING`.

Текущий главный batch-источник для будущего V5 training:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_ML_READY_439F_TARGETS_V1.csv
```

Счетчики batch: `32` дня, `2596` строк, `entry_y 1=290 / 0=2306`, `439` features = `274 old causal + 81 cs_* + 84 fcs_*`.

Контрольные файлы:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_FEATURE_ALLOWLIST_439F_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_MANIFEST_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_GUARD_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_AUDIT_RU.md
```

Guard подтвердил: allowlist одинаковый у всех дней; `entry_y/phase_y/state_y/reason_y/entry_label/rank_label/manual teacher` не входят в `X`; future/postfact/hit_/TP/Stas3/exit/old ML/full-group leakage в `X` нет; `cs_*` и `fcs_*` source time не позже `entry_time_utc`; дублей нет; model/forward V5 не стартовали.

Следующий правильный шаг: не forward и не прямой entry training, а отдельный training guard и two-block схема `MARKET_PHASE_STATE_ML` -> `ENTRY_ML` с OOF phase/state predictions на train и live predictions на forward.

## STAS5 V5 Range 2026-01-27..2026-02-27 Full-Ready

Статус: `PASS_V5_RANGE_AUDIT_READY_FOR_BATCH_DATASET`.

Текущая V5-база закрыта по диапазону:

```text
2026-01-27..2026-02-27
```

Итог диапазона: `32/32` full-ready дня, `2596` строк, `entry_y 1=290 / 0=2306`, feature-контракт `274 -> 355 -> 439`, problem count `0`.

Во время аудита была найдена и исправлена дырка: `2026-02-07` имел FULL274 run, но не имел V5 market passport. День дозаполнен по ранее утвержденным GOOD ids, пересобран full causal слой и карта. После исправления общий folder audit:

```text
PASS_V5_FOLDER_AUDIT_NO_TRAINING
full-ready=32
partial/not-ready=1
model=False
forward=False
```

Единственный `partial/not-ready` сейчас вне текущей базы: старый `2026-04-01` FULL274 run без V5 market passport.

Главный отчет диапазона:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_RANGE_AUDIT_20260127_20260227_RU.md
```

Следующий правильный шаг: собрать единый V5 batch dataset из 32 дневных `ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv`, затем сделать batch leakage/no-future guard. Training и forward V5 еще не запускались.

## STAS5 V5 2026-02-01 Audit And Six Full-Ready Days

Статус: `PASS_V5_FOLDER_AUDIT_NO_TRAINING`.

Текущий полный V5-пакет дня:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260201/
```

Главный CSV дня:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260201/STAS5_V5_MARKET_PASSPORT_20260201_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Счетчики `2026-02-01`: `89` кандидатов, `entry_y 1=14 / 0=75`, `GOOD_APPROVED=14`, `BAD_IN_GROUP=47`, `NO_TRADE_ZONE=28`, feature-контракт `274 -> 355 -> 439`.

GOOD ids в финальной таблице: `LA007`, `LA014`, `LA026`, `LA040`, `LA041`, `LA045`, `LA053`, `LA058`, `LA060`, `LA066`, `LA079`, `LA082`, `LA084`, `LA087`. Пользовательский порядок отличается только тем, что `LA026` был назван раньше `LA014`; CSV идет по времени.

Структурные артефакты дня: `levels=34`, `channels=89`, `regimes=64`, `events=3402`. Guard-и baseline/cs/full все `PASS`; `cs_max_source_time_utc` и `fcs_max_source_time_utc` не уходят за `entry_time_utc`.

V5 folder audit сейчас: `full-ready=6`, `partial/not-ready=27`, `model=False`, `forward=False`. Full-ready дни: `2026-01-27`, `2026-01-28`, `2026-01-29`, `2026-01-30`, `2026-01-31`, `2026-02-01`.

Два ML-блока пока не обучались. Это будущая схема: `MARKET_PHASE_STATE_ML` предсказывает фазу/состояние, `ENTRY_ML` предсказывает вход; второму блоку можно давать только OOF/live-предсказания первого блока, а не ручные `phase_y/state_y`.

## STAS5 V5 2026-01-28 Full-Ready

Статус: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

Текущая рабочая папка дня:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260128/
```

Пользователь утвердил GOOD ids:

```text
LA020, LA037, LA042, LA045, LA051, LA059, LA069, LA078, LA084
```

Собрано по той же V5-лестнице:

```text
FULL274 93 rows -> approved targets 274F -> cs_* 355 features -> fcs_* 439 features
```

Главный файл для будущего batch dataset:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260128/STAS5_V5_MARKET_PASSPORT_20260128_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Счетчики: `entry_y 1=9 / 0=84`, `levels=16`, `channels=93`, `regimes=66`, `events=3181`. Guard-и baseline/cs/full все `PASS`. V5 folder audit: `full-ready=2`, `partial/not-ready=31`, `model=False`, `forward=False`.

Обучение и forward V5 по-прежнему не запускались.

## STAS5 V5 Day Ladder And Folder Audit

Статус: `PASS_V5_FOLDER_AUDIT_NO_TRAINING`.

Добавлена главная лесенка для следующего дня:

```text
STAS5_ML_CORE/run_stas5_v5_day_ladder.ps1
```

Главная команда:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage All -OpenFolder
```

Контракт команды:

```text
FULL274 -> stop for manual approved passport -> cs_* -> fcs_* -> folder audit
```

Если approved passport/targets отсутствует, команда останавливается и показывает недостающие файлы. Она не создает fake GOOD/BAD и не запускает обучение.

Добавлен полный аудит V5-папки:

```text
src/mlbotnav/stas5_v5_folder_audit.py
STAS5_ML_CORE/run_stas5_v5_folder_audit.ps1
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715.json
```

Последний аудит: `full-ready=1`, `partial/not-ready=32`, `model=False`, `forward=False`. `2026-01-27` full-ready; `2026-01-28` имеет FULL274 run, но еще не имеет approved V5 passport.

## STAS5 V5 Full Causal Market-Structure Builder 2026-01-27

Статус: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

Текущий главный V5-пакет дня:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/
```

Открывать первым:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/00_OPEN_FIRST_RU.md
```

Главный CSV для будущего обучения теперь:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

В нем `75` строк, `439` разрешенных feature columns: `355` признаков до full-слоя (`274 + cs_*`) и `84` новых `fcs_*` признака. Targets: `entry_y 1=11 / 0=64`.

Новые full-causal артефакты:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_FULL_STRUCTURE_CANDIDATE_FEATURES_CAUSAL_V1.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_LEVELS_CAUSAL_V1.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_CHANNELS_CAUSAL_V1.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_REGIMES_CAUSAL_V1.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_EVENTS_CAUSAL_V1.csv
```

Главная карта:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/DAY_MARKET_PASSPORT_20260127_FULL_CAUSAL_STRUCTURE_MAP_V1.png
```

Builder:

```text
src/mlbotnav/stas5_v5_full_causal_structure_builder.py
STAS5_ML_CORE/run_stas5_v5_full_causal_structure_builder.ps1
```

Guard:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_FULL_CAUSAL_STRUCTURE_GUARD_V1.json
```

Guard `PASS`: `rows_match`, `merge_one_to_one`, `source_time_before_entry`, `forbidden_*_absent`, `targets_not_in_features`, `fcs_values_not_missing`, `events_known_inside_day`, `visual_sources_exist`.

Счетчики: `levels=19`, `channels=75`, `regimes=53`, `events=2833`.

Главное правило осталось тем же: ручной паспорт является учителем `y`, а не входным признаком `X`. В `X` разрешены только старые causal-признаки, `cs_*` и новые `fcs_*`, которые пересчитаны из прошлого до `entry_time_utc`. Обучение V5 и V5 forward не запускались.

## STAS5 V5 Structure Map 2026-01-27

Статус: `VISUAL_STRUCTURE_MAP_V4_READY_NO_TRAINING`.

Для дня `2026-01-27` добавлен главный график обсуждения структуры:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/DAY_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_MAP_V4_CLEAN.png
```

Он показывает полный каркас: manual support/resistance bands как teacher-context, causal S/R линии из `cs_nearest_support/resistance`, локальные trendlines, `KNIFE ACTIVE`, danger-down, bottom/base, pump-continuation, chop/no-edge, pressure/trend и target row. Таблица тегов:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_MAP_TAGS_V4.csv
```

Обучение не запускалось.

## STAS5 V5 Causal Market-Structure Builder 2026-01-27 Previous `cs_*` Layer

Статус: `PASS_NO_TRAINING_CAUSAL_STRUCTURE_READY`. Это предыдущий `cs_*` слой. Текущий главный слой находится выше: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

Текущий главный V5-пакет дня:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/
```

Открывать первым:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/00_OPEN_FIRST_RU.md
```

Предыдущий `cs_*` CSV, который используется как source/base для full-слоя:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

В нем `75` строк, `274` старых causal-признака, `81` новый `cs_*` market-structure признак, всего `355` feature columns. Targets: `entry_y 1=11 / 0=64`, `GOOD_APPROVED=11`, `BAD_IN_GROUP=50`, `NO_TRADE_ZONE=14`, `phase_y=5` фаз.

Добавлен builder:

```text
src/mlbotnav/stas5_v5_causal_structure_builder.py
STAS5_ML_CORE/run_stas5_v5_causal_structure_builder.ps1
```

Guard:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_GUARD_V1.json
```

Guard `PASS`: `rows_match`, `merge_one_to_one`, `source_time_before_entry`, `forbidden_*_absent`, `targets_not_in_features`, `causal_values_not_missing`.

Главное правило: ручной паспорт является учителем `y`, а не входным признаком `X`. В этом предыдущем слое `X` = старые `274` causal-признака + `cs_*`, которые builder пересчитывает из OHLCV только до `entry_time_utc`. Для текущей работы использовать full-слой `274 + cs_* + fcs_*`. Обучение V5 и V5 forward не запускались.

Проектный аудит:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_PROJECT_AUDIT_20260715_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_PROJECT_AUDIT_20260715.json
```

## STAS5 V5 Навигация По Пакету 2026-01-27

Чтобы не путаться в похожих файлах `V1/V2/V3`, в текущую папку дня добавлен файл:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/00_OPEN_FIRST_RU.md
```

Его нужно открывать первым. Текущая рабочая версия: `PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1`; старые `V1/V2/V3/V4` и промежуточные файлы оставлены как история/source/base.

## STAS5 V5 Market Passport 2026-01-27 Phase/State/Reason Ready

Статус: `PASS_NO_TRAINING_PHASE_STATE_REASON_READY`.

По дню `2026-01-27` поверх user-approved V3 создан финальный V5 target-слой для нового контура:

```text
entry_y  = good/bad для входа
phase_y  = 5 крупных ручных фаз дня
state_y  = детальное состояние рынка на кандидате
reason_y = причина good/bad/no-trade
```

Актуальный ML-ready файл:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv
```

Актуальный allowlist:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json
```

Проверка: `rows=75`, `feature_count=274`, `entry_y 1=11 / 0=64`, `phase_y=5` фаз, forbidden feature columns `[]`. GOOD ids: `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062`.

Ключевое правило: `entry_y/phase_y/state_y/reason_y` - это teacher-target, не live-feature. `X` для обучения остается строго `274` causal-признака из allowlist. Обучение не запускалось.

## STAS5 V5 Market Passport 2026-01-27 User Approved V3

Статус: `USER_APPROVED_V3_NO_TRAINING`.

Актуальный день для новой работы: `2026-01-27`, не апрель. Пользователь проверил график и подтвердил: оставить только его `11` входов, остальные кандидаты не лучше, а хуже.

GOOD-входы: `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062`.

По run `STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857` собран user-approved ledger на `75/75` кандидатов. Разметка V3: `GOOD_APPROVED=11`, `BAD_IN_GROUP=50`, `NO_TRADE_ZONE=14`. `GOOD_ALT` и `REVIEW_ONLY` больше не используются для этого дня; бывшие спорные точки переведены в negative.

Актуальные артефакты:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_LEDGER_20260127_USER_APPROVED_V3.csv
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_USER_APPROVED_RU.md
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_USER_APPROVED_V3_ANNOTATED_TOP.png
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_PHASE_STATS_USER_APPROVED_V3.csv
```

Важное правило: future используется только для офлайн-разметки истории. В обучение/live нельзя передавать `future`, `postfact`, `hit_*`, `TP/Stas3/exit`, старые `ML_DECISION/ML_KEEP_SCORE`; уже поставленный live-вход нельзя "заменять" более поздним кандидатом задним числом.

День дополнительно упакован в отдельную V5-папку, чтобы не путать `runs/...` с финальной числовой базой:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/
```

Главные файлы пакета:

```text
STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_LABELS_V1.csv
STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_V1.json
STAS5_V5_MARKET_PASSPORT_20260127_MARKET_STRUCTURE_NUMERIC_V1.csv
STAS5_V5_MARKET_PASSPORT_20260127_274F_LABELS_PLUS_STRUCTURE_CONTEXT_V1.csv
STAS5_V5_MARKET_PASSPORT_20260127_PACKAGE_MANIFEST.json
README_RU.md
```

Проверка пакета: `PASS_NO_TRAINING`, `rows=75`, `feature_count=274`, `train_label_binary: 1=11 / 0=64`, запрещенных future/TP/Stas3/old-ML feature columns в allowlist нет.

Уточнение по структуре рынка: ручные фазы/поддержки/сопротивления уже переведены в цифру и используются как teacher/source-of-truth для labels. Для прямого использования как feature в forward/live нужен отдельный causal market-structure builder, который строит такие же фазы и зоны только по данным до `entry_time_utc`. Это зафиксировано в:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/TRAINING_SCHEMA_RU.md
```

Следующий шаг: использовать пакет как approved numeric label source при сборке общей январской базы. Обучение в этом шаге не запускалось.

## STAS5 V5 Market Passport Trial 2026-01-27

Статус: `USER_DESIRED_V1_DRAFT_NO_TRAINING`.

По run `STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857` создан пробный паспорт рынка для `2026-01-27`, `SOLUSDT`, `1m`. Run подтвержден как `PASS`: `75` кандидатов, `274` causal-признака, `UNLABELED_VISUAL_ONLY`, обучение/API/TP/Stas3 не запускались.

Созданы артефакты:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_ANNOTATED_FULL.png
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_ANNOTATED_TOP.png
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_DRAFT_ZONES.csv
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_RU.md
```

Пользователь уточнил согласованный список желательных входов: `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062`. Предыдущий trial-слой с no-buy оценками оставлен только как черновая история; актуальный слой для согласования - `USER_DESIRED_V1`, без автоматической браковки соседей.

Новые артефакты:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_USER_DESIRED_V1.csv
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_USER_DESIRED_V1_ANNOTATED_TOP.png
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_USER_DESIRED_V1_RU.md
```

Следующий шаг - вокруг этих `11` желательных входов отдельно разобрать соседние плохие/альтернативные кандидаты. Обучение не запускалось.

## STAS5 FULL274 Feature Collect 2026-07-15

Статус: `PASS`.

Добавлен отдельный wrapper:

```text
STAS5_ML_CORE/run_stas5_full274_feature_collect.ps1
```

Назначение: собрать один день до обучения в отдельный `STAS5_ML_CORE/runs/...` без перезаписи старых прогонов.

Контрольный запуск:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260401_20260715_084509/
rows=81
features=274
v1_features=111
v2_features=163
training_started=false
```

График строится через `stas5_v2_feature_visual_approval.py`; CUT-маркеры и подписи LAxxx сделаны ярко-желтыми для читаемости. Обучение, API, TP/Stas3 не запускались.

## Актуальный источник правды STAS5 V4

Текущее состояние V4 group-rank брать из верхних свежих секций и из guard/unified ledger:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Актуальный unified ledger: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Старые секции ниже оставлены как журнал промежуточных шагов и могут иметь устаревшие счетчики.

## Current State 2026-07-14 STAS5 V4 2026-05-25 Checked

Текущий статус: `STAS5_V4_20260525_USER_CHECKED_PASS_NO_TRAINING`.

`2026-05-25` сверен с пользовательским скрином. Два красных круга совпали с текущей таблицей:

```text
LA020 = BEST_GOOD, pre-London нижний pullback; на старом графике был серый/skip-кандидат без подписи
LA019 = GOOD_ALT, хороший соседний вход, но выше LA020
LA038 = BEST_GOOD, late-London pullback/retest
```

CSV day25 не изменялся. Актуальные winners day25: `LA014`, `LA020`, `LA038`, `LA059`, `LA066`. Counts: `68` строк, `BEST_GOOD=5`, `GOOD_ALT=4`, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=19`.

Unified ledger остается после day23: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-24 Checked

Текущий статус: `STAS5_V4_20260524_USER_CHECKED_PASS_NO_TRAINING`.

`2026-05-24` сверен с пользовательским скрином. Два больших круга и поздняя нижняя зона совпали с текущей таблицей:

```text
LA015 = BEST_GOOD, pre-London lower entry
LA042 = BEST_GOOD, overlap crash deep low
LA065 = BEST_GOOD, late deep low/retest
LA067 = GOOD_ALT, хороший поздний pullback, но не главный low группы
```

CSV day24 не изменялся. Актуальные winners day24: `LA009`, `LA015`, `LA024`, `LA042`, `LA065`. Counts: `70` строк, `BEST_GOOD=5`, `GOOD_ALT=5`, `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=6`.

Unified ledger остается после day23: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-23 Checked

Текущий статус: `STAS5_V4_20260523_USER_CORRECTED_V1_NO_TRAINING`.

`2026-05-23` сверен с пользовательским скрином. Видимые красные круги показали, что draft слишком широко сгруппировал recovery-участок `LA034..LA042`: `LA034` и `LA042` были занижены относительно человеческой логики отдельных входов.

Исправление:

```text
LA034 = BEST_GOOD в отдельной первой recovery pullback micro-group
LA036 = BEST_GOOD, остается отдельным winner
LA042 = BEST_GOOD, повышен из GOOD_ALT как pre-breakout retest
LA051 = BEST_GOOD, остается поздним continuation-base winner
```

Актуальные winners day23: `LA007`, `LA022`, `LA033`, `LA034`, `LA036`, `LA042`, `LA051`. Counts day23: `63` строки, `BEST_GOOD=7`, `GOOD_ALT=4`, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=12`.

Unified ledger теперь: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit: `GOOD_ALT_MAY_NEED_MICRO_GROUP=39`, `BEST_GOOD_FROM_OLD_NON_ENTER=28`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-22 Checked

Текущий статус: `STAS5_V4_20260522_USER_CORRECTED_V1_NO_TRAINING`.

`2026-05-22` сверен со свежим пользовательским скрином. Видимая ошибка была не в количестве входов, а в выборе главного входа внутри pre-London группы: пользователь отметил поздний ретест `LA024`, а не ранний low `LA022`.

Исправление:

```text
LA022 = GOOD_ALT, первый low зоны
LA024 = BEST_GOOD, пользовательски отмеченный ретест/подбор перед продолжением вверх
```

Актуальные winners day22: `LA007`, `LA024`, `LA036`, `LA047`, `LA061`. Counts day22: `75` строк, `BEST_GOOD=5`, `GOOD_ALT=4`, `BAD_IN_GROUP=55`, `NO_TRADE_GROUP=11`.

Unified ledger остается: `738` строк, `BEST_GOOD=62`, `GOOD_ALT=43`, `BAD_IN_GROUP=434`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit totals не изменились. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-21 Checked

Текущий статус: `STAS5_V4_20260521_USER_CORRECTED_V1_NO_TRAINING`.

`2026-05-21` сверен с пользовательским скрином. Четыре круга означают: `LA006` уже совпадал с winner, а `LA039`, `LA050`, `LA057` были задавлены слишком широкими группами.

Исправление:

```text
LA039 = BEST_GOOD в первой sell-wave basin micro-group
LA045 = BEST_GOOD в отдельной overlap-flush micro-group
LA050 = BEST_GOOD в отдельной post-flush retest micro-group
LA057 = BEST_GOOD в первой pre-breakout pullback micro-group
LA059 = BEST_GOOD в следующей lower pre-breakout retest micro-group
```

Актуальные winners day21: `LA006`, `LA019`, `LA039`, `LA045`, `LA050`, `LA057`, `LA059`, `LA066`. Counts: `81` строка, `BEST_GOOD=8`, `GOOD_ALT=4`, `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=15`.

Unified ledger теперь: `738` строк, `BEST_GOOD=62`, `GOOD_ALT=43`, `BAD_IN_GROUP=434`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit: `GOOD_ALT_MAY_NEED_MICRO_GROUP=40`, `BEST_GOOD_FROM_OLD_NON_ENTER=26`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-20 Checked

Текущий статус: `STAS5_V4_20260520_USER_CORRECTED_V1_NO_TRAINING`.

`2026-05-20` сверен с новым пользовательским скрином. В зоне `13:19-14:26` было две отмеченные точки: нижняя уже совпадала с `LA037`, верхняя была серым/skip-кандидатом `LA038`, который draft ошибочно держал как `BAD_AFTER_BOUNCE_TOO_HIGH`.

Исправление:

```text
LA037 = BEST_GOOD в crash-low группе LA033..LA037
LA038 = BEST_GOOD в отдельной rebound/pullback micro-group LA038..LA039
LA035 = GOOD_ALT
LA036 = BAD_IN_GROUP
LA039 = BAD_IN_GROUP
```

Актуальные winners day20: `LA011`, `LA037`, `LA038`, `LA045`, `LA053`, `LA057`. Counts: `68` строк, `BEST_GOOD=6`, `GOOD_ALT=4`, `BAD_IN_GROUP=27`, `NO_TRADE_GROUP=31`.

Unified ledger теперь: `738` строк, `BEST_GOOD=59`, `GOOD_ALT=44`, `BAD_IN_GROUP=436`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit: `GOOD_ALT_MAY_NEED_MICRO_GROUP=41`, `BEST_GOOD_FROM_OLD_NON_ENTER=24`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-19 Checked

Текущий статус: `STAS5_V4_20260519_USER_CORRECTED_V1_NO_TRAINING`.

`2026-05-19` сверен с новым пользовательским скрином. Красная обводка в overlap/retest зоне означает отдельный retest/base вход после `LA042`. Старый draft ошибочно держал эту точку как `GOOD_ALT` внутри широкой группы `LA034..LA047`.

Исправление:

```text
LA042 = BEST_GOOD в отдельной flush-группе LA034..LA042
LA046 = BEST_GOOD в отдельной retest/base micro-group LA043..LA047
LA047 = GOOD_ALT
LA045 = BAD_IN_GROUP
```

Важно: подпись со старым score `0.86` на скрине соответствует строке `LA046` в CSV; `LA045` в CSV имеет старый score около `0.07`.

Актуальные winners day19: `LA005`, `LA016`, `LA032`, `LA042`, `LA046`, `LA063`. Counts: `65` строк, `BEST_GOOD=6`, `GOOD_ALT=3`, `BAD_IN_GROUP=39`, `NO_TRADE_GROUP=17`.

Unified ledger теперь: `738` строк, `BEST_GOOD=58`, `GOOD_ALT=44`, `BAD_IN_GROUP=437`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-18 Checked

Текущий статус: `STAS5_V4_20260518_USER_CORRECTED_V1_NO_TRAINING`.

`2026-05-18` сверен с пользовательским скрином с красными обводками. Исправлены две ошибки старого draft:

```text
LA036 = BEST_GOOD, отдельный pullback/retest после импульса вверх
LA066 = BEST_GOOD, отдельный late NY retest после вертикального движения
```

Актуальные winners day18: `LA006`, `LA019`, `LA034`, `LA036`, `LA049`, `LA061`, `LA066`. Counts: `73` строки, `BEST_GOOD=7`, `GOOD_ALT=7`, `BAD_IN_GROUP=52`, `NO_TRADE_GROUP=7`.

Unified ledger теперь: `738` строк, `BEST_GOOD=57`, `GOOD_ALT=44`, `BAD_IN_GROUP=438`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-17 Checked

Текущий статус: `STAS5_V4_20260517_USER_CHECKED_V1_NO_TRAINING`.

`2026-05-17` сверен с пользовательским скрином. Актуальные winners в таблице совпадают с красными нижними отметками на графике: `LA004`, `LA006`, `LA036`, `LA046`, `LA063`. Это пять отдельных human-style входов дня; `LA003`, `LA005`, `LA044` остаются `GOOD_ALT`, а не отдельными главными входами.

CSV не менялся: текущий `STAS5_V4_GROUP_RANK_LEDGER_20260517_DRAFT.csv` уже соответствует скрину. Создан только проверочный отчет `STAS5_V4_GROUP_RANK_REVIEW_20260517_USER_CHECKED_V1_RU.md`. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-16 Checked

Текущий статус: `STAS5_V4_20260516_USER_CORRECTED_V1_NO_TRAINING`.

`2026-05-16` сверен с пользовательским скрином. Актуальные winners: `LA016`, `LA027`, `LA038`, `LA041`. `LA049` снят из winners и переведен в no-trade context вместе с группой `LA043..LA049`, потому что на скрине нет отдельной красной отметки в этой зоне.

Unified ledger теперь: `BEST_GOOD=55`, `GOOD_ALT=43`, `BAD_IN_GROUP=437`, `NO_TRADE_GROUP=203`, guard `PASS`. Обучение и group features не запускались.

## Current State 2026-07-14 STAS5 V4 Micro-Group Correction

Текущий статус: `STAS5_V4_FORWARD_REVIEW_MICRO_GROUP_V2_NO_TRAINING`.

`2026-05-15` исправлен после пользовательского уточнения по скрину: целевой вход может быть старым `UNSURE` или `SKIP`, если он является человечески отмеченной нижней точкой выбора. V4 учится ранжировать внутри human-style group/micro-group, а не копировать старый цвет маркера.

Актуальная разметка `2026-05-15`: `LA004`, `LA007`, `LA021`, `LA024`, `LA054`, `LA061` являются `BEST_GOOD`. `LA004` и `LA007` больше не конкурируют в одной большой группе: они разделены на две micro-groups.

Unified ledger `2026-05-15..2026-05-25` обновлен и проходит guard:

```text
rows=738
BEST_GOOD=55
GOOD_ALT=43
BAD_IN_GROUP=437
NO_TRADE_GROUP=203
guard=PASS
```

Для `2026-05-16..2026-05-25` создан и обновлен risk audit. После правки `2026-05-18` следующий правильный шаг - смотреть оставшиеся `GOOD_ALT_MAY_NEED_MICRO_GROUP=41`, а не пересобирать все дни подряд. Обучение V4, group features, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 Screenshot Artifact Inventory

Текущий статус: `STAS5_V4_SCREENSHOT_ARTIFACT_INVENTORY_DONE_NO_TRAINING`.

Создана папка для ручного просмотра скриншотов и зафиксированных V4-блоков:

```text
STAS5_ML_CORE/artifacts/v4/review_navigation/20260714_artifact_inventory
```

Собраны три контакт-листа:

```text
CONTACT_SHEET_20260501_20260514_TRAIN_VISUAL_APPROVAL.png
CONTACT_SHEET_20260515_20260525_FORWARD_SOURCE.png
CONTACT_SHEET_20260515_20260525_V4_GROUP_BLOCKS.png
```

Индекс файлов:

```text
STAS5_SCREENSHOT_INDEX_20260501_20260525.csv
STAS5_SCREENSHOT_INDEX_20260501_20260525.json
```

Проверка наличия файлов прошла без пропусков. `2026-05-01..2026-05-14` сейчас представлены как train visual approval PNG. `2026-05-15..2026-05-25` имеют исходные forward PNG и V4 group-rank annotated PNG. Это только инвентаризация и визуальная навигация, без обучения и без изменения ledger.

## Current State 2026-07-14 STAS5 V4 Unified Forward Review 2026-05-15..2026-05-25

Текущий статус: `STAS5_V4_FORWARD_REVIEW_20260515_20260525_DRAFT_NO_TRAINING`.

`2026-05-15` включен в общий forward-review блок `2026-05-15..2026-05-25`, а не ведется отдельным карантинным/approved днем. База `2026-05-01..2026-05-14` остается отдельной train-base рамкой.

Уточнен дневной ориентир V4: `2..5` входов не является жестким потолком. Количество лучших входов должно быть адаптивным по режиму дня: спокойный день может дать `2..3`, активный `4..6`, сильный волатильный день может дать больше, вплоть до `8..12`, если это разные понятные winner/alt-группы. Запрещается не большое число само по себе, а шумные зеленые стрелки без group winner/reason-code.

Единый ledger:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Итог пакета после ручных правок `2026-05-16`, `2026-05-18`, `2026-05-19`, `2026-05-20` и `2026-05-21`: `738` строк, `BAD_IN_GROUP=434`, `GOOD_ALT=43`, `BEST_GOOD=62`, `NO_TRADE_GROUP=199`; `62` winners, guard по ledger-структуре `PASS`. Group/reason/winner coverage сходится, forbidden old-ML/future/TP/Stas3/exit columns отсутствуют. Group features еще не построены, поэтому обучение V4 остается заблокированным.

Старый 15-only главный ledger сохранен как superseded-копия и не является текущей рабочей точкой.

## Current State 2026-07-14 STAS5 V4 2026-05-15 Quarantine Removed

Текущий статус: `STAS5_V4_20260515_APPROVED_V1_NO_TRAINING`.

День `2026-05-15` снят с карантина по решению пользователя. На базе `USER_CORRECTED_V1` создан approved ledger: `41` строка, `BAD_IN_GROUP=26`, `NO_TRADE_GROUP=6`, `BEST_GOOD=5`, `GOOD_ALT=4`.

Approved winners: `LA007`, `LA021`, `LA024`, `LA054`, `LA061`. Good-alt: `LA004`, `LA005`, `LA053`, `LA060`.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_APPROVED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_APPROVED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Календарь V4 теперь `base_25_days = 2026-05-01..2026-05-25`. Общий approved ledger сейчас содержит только `2026-05-15`; draft-дни `2026-05-16..2026-05-25` не переведены в approved без отдельного подтверждения.

Граница: обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-25 Draft Group Review

Текущий статус: `STAS5_V4_20260525_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-25` создан V4 draft-разбор по группам выбора: `group_id -> winner -> bad neighbours with reason`. День разложен на `7` групп и `68` строк: `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=19`, `BEST_GOOD=5`, `GOOD_ALT=4`.

Актуальные winners: `LA014`, `LA020`, `LA038`, `LA059`, `LA066`. Good-alt: `LA006`, `LA015`, `LA019`, `LA067`. Важный смысл дня: старые V3 `ENTER` `LA012`, `LA030`, `LA053`, `LA057`, `LA068` не должны выигрывать у более нижних/поздних V4 winner-зон.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_REVIEW_20260525_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_LEDGER_20260525_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_REVIEW_20260525_ANNOTATED_DRAFT.png
```

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-24 Draft Group Review

Текущий статус: `STAS5_V4_20260524_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-24` создан V4 draft-разбор по группам выбора: `group_id -> winner -> bad neighbours with reason`. День разложен на `6` групп и `70` строк: `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=6`, `GOOD_ALT=5`, `BEST_GOOD=5`.

Актуальные winners: `LA009`, `LA015`, `LA024`, `LA042`, `LA065`. Good-alt: `LA005`, `LA008`, `LA014`, `LA023`, `LA067`. Важный смысл дня: старые V3 `ENTER` в середине лондонского движения и overlap/NY ножа не должны выигрывать у нижних ретестов `LA024`, `LA042`, `LA065`.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_REVIEW_20260524_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_LEDGER_20260524_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_REVIEW_20260524_ANNOTATED_DRAFT.png
```

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-23 Draft Group Review

Текущий статус: `STAS5_V4_20260523_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-23` создан V4 draft-разбор по группам выбора: `group_id -> winner -> bad neighbours with reason`. День разложен на `6` групп и `63` строки: `BAD_IN_GROUP=41`, `NO_TRADE_GROUP=12`, `GOOD_ALT=5`, `BEST_GOOD=5`.

Актуальные winners: `LA007`, `LA022`, `LA033`, `LA036`, `LA051`. Good-alt: `LA002`, `LA014`, `LA025`, `LA042`, `LA046`. Важный смысл дня: `LA017..LA021` не должны выигрывать у `LA022`, потому что это входы в падающий нож до финального low; поздняя post-spike зона `LA052..LA063` оставлена no-trade.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_REVIEW_20260523_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_REVIEW_20260523_ANNOTATED_DRAFT.png
```

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-22 Draft Group Review

Текущий статус: `STAS5_V4_20260522_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-22` создан V4 draft-разбор по группам выбора. День разложен на `6` групп и `75` строк: `BAD_IN_GROUP=55`, `NO_TRADE_GROUP=11`, `BEST_GOOD=5`, `GOOD_ALT=4`.

Актуальные winners: `LA007`, `LA022`, `LA036`, `LA047`, `LA061`. Good-alt: `LA005`, `LA024`, `LA043`, `LA062`. Важный смысл дня: старые V3 `ENTER` в зоне `LA056..LA058` не должны выигрывать у финального deep low `LA061`; поздний weak-hours low `LA075` оставлен no-trade.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_REVIEW_20260522_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_LEDGER_20260522_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_REVIEW_20260522_ANNOTATED_DRAFT.png
```

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-21 Draft Group Review

Текущий статус: `STAS5_V4_20260521_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-21` создан V4 draft-разбор по группам выбора: `group_id -> winner -> bad neighbours with reason`. День разложен на `6` групп и `81` строку: `BAD_IN_GROUP=56`, `NO_TRADE_GROUP=15`, `GOOD_ALT=5`, `BEST_GOOD=5`.

Актуальные winners: `LA006`, `LA019`, `LA045`, `LA059`, `LA066`. Good-alt: `LA004`, `LA021`, `LA040`, `LA048`, `LA057`. Важный смысл дня: старые V3 `ENTER` в середине падения и на вершине spike не должны выигрывать у нижних basin/retest-зон.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_REVIEW_20260521_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_LEDGER_20260521_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_REVIEW_20260521_ANNOTATED_DRAFT.png
```

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-20 Draft Group Review

Текущий статус: `STAS5_V4_20260520_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому скриншоту `2026-05-20` создан V4 draft-разбор по группам выбора: не построчный `KEEP/CUT`, а `group_id -> winner -> bad neighbours with reason`. День разложен на `7` групп и `68` строк: `NO_TRADE_GROUP=31`, `BAD_IN_GROUP=28`, `BEST_GOOD=5`, `GOOD_ALT=4`.

Актуальные winners: `LA011`, `LA037`, `LA045`, `LA053`, `LA057`. Good-alt: `LA002`, `LA035`, `LA040`, `LA052`. Важный смысл дня: раннюю базу брать через финальный ретест `LA011`, лондонскую середину не превращать в good из-за старого ML score, после NY-движения выбирать нижние pullback/retest-зоны.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_REVIEW_20260520_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_LEDGER_20260520_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_REVIEW_20260520_ANNOTATED_DRAFT.png
```

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-19 Draft Group Review

Текущий статус: `STAS5_V4_20260519_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому скриншоту `2026-05-19` создан V4 draft-разбор по группам выбора с учетом красного нисходящего канала. День разложен на `7` групп и `65` строк: `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=17`, `BEST_GOOD=5`, `GOOD_ALT=3`.

Актуальные winners: `LA005`, `LA016`, `LA032`, `LA042`, `LA063`. Good-alt: `LA046`, `LA061`, `LA062`. Важный смысл дня: не брать середину/верх нисходящего канала; хорошие входы должны быть у нижней границы канала или после deep low.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_REVIEW_20260519_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_LEDGER_20260519_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_REVIEW_20260519_ANNOTATED_DRAFT.png
```

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-18 Draft Group Review

Текущий статус: `SUPERSEDED_BY_20260518_USER_CORRECTED_V1_NO_TRAINING`.

Первый V4 draft-разбор по `2026-05-18` разложил день на `6` групп и `73` строки: `BAD_IN_GROUP=51`, `NO_TRADE_GROUP=11`, `GOOD_ALT=6`, `BEST_GOOD=5`. После пользовательских обводок он superseded актуальной версией `USER_CORRECTED_V1`, где добавлены `LA036` и `LA066` как отдельные micro-group winners.

Актуальные winners: `LA006`, `LA019`, `LA034`, `LA049`, `LA061`. Близкие хорошие, но не главные: `LA005`, `LA014`, `LA022`, `LA048`, `LA050`, `LA059`. Поздний участок `LA063..LA073` оставлен no-trade после V-отскока.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_REVIEW_20260518_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_LEDGER_20260518_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_REVIEW_20260518_ANNOTATED_DRAFT.png
```

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-17 Draft Group Review

Текущий статус: `STAS5_V4_20260517_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому скриншоту `2026-05-17` создан такой же V4 draft-разбор по группам выбора: не построчный `KEEP/CUT`, а `group_id -> winner -> bad neighbours with reason`. Красные зоны оформлены как draft winners: `LA004`, `LA006`, `LA036`, `LA046`, `LA063`; близкие хорошие, но не главные: `LA003`, `LA005`, `LA044`.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_REVIEW_20260517_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_LEDGER_20260517_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_REVIEW_20260517_ANNOTATED_DRAFT.png
```

CSV содержит `63` строки: `NO_TRADE_GROUP=30`, `BAD_IN_GROUP=25`, `BEST_GOOD=5`, `GOOD_ALT=3`. Ключевой V4-контраст дня: `LA056/LA062` старый ML зеленит до финального пролива, а правильный group winner - `LA063`.

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 Review Encoding Fix

Текущий статус: `STAS5_V4_REVIEW_ENCODING_FIX_DONE`.

После замечания пользователя про кракозябры проверены V4 Markdown-разборы `2026-05-15` и `2026-05-16` в папке `STAS5_ML_CORE/artifacts/v4/group_rank_review`. Файлы читаются как нормальный UTF-8: длинные цепочки вопросительных знаков, `U+FFFD` и CJK-мусор в трех review-файлах не найдены.

Граница: исправление касалось только читаемости Markdown/командной памятки. CSV-ledger, PNG-разметка, признаки, обучение, threshold tuning, Optuna, API, TP/Stas3/exit не менялись и не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-16 Draft Group Review

Текущий статус: `STAS5_V4_20260516_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому скриншоту `2026-05-16` создан V4 draft-разбор по группам выбора, по той же логике, что для `2026-05-15`: не построчный `KEEP/CUT`, а `group_id -> winner -> bad neighbours with reason`.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_REVIEW_20260516_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_LEDGER_20260516_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_REVIEW_20260516_ANNOTATED_DRAFT.png
```

CSV содержит `71` строку: `NO_TRADE_GROUP=38`, `BAD_IN_GROUP=27`, `BEST_GOOD=5`, `GOOD_ALT=1`. Winners: `LA016`, `LA027`, `LA038`, `LA041`, `LA049`. Ключевые обучающие контрасты: `LA034` плохой высокий вход в третьей волне, а `LA038` правильный lower missed-good; `LA021/LA024/LA025/LA026` плохие до более глубокого `LA027`.

Граница: это `DRAFT`, не approved train ledger. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Current State 2026-07-14 STAS5 V4 2026-05-15 User-Corrected V1

Текущий статус: `SUPERSEDED_BY_20260515_APPROVED_V1_NO_TRAINING`.

По уточнению пользователя первый разбор `2026-05-15` исправлен: день разложен не как `90` отдельных входов, а как `6` групп выбора, где красная линия означает хороший вход, а соседние кандидаты вокруг него становятся обучающими плохими примерами.

Актуальные артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_USER_CORRECTED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_ANNOTATED.png
```

CSV содержит `41` строку: `BAD_IN_GROUP=26`, `NO_TRADE_GROUP=6`, `BEST_GOOD=5`, `GOOD_ALT=4`. Winners: `LA007`, `LA021`, `LA024`, `LA054`, `LA061`; `LA004` сохранен как `GOOD_ALT`, потому что внутри группы 1 более глубокий winner - `LA007`. Группа 4 оформлена как `NO_TRADE_GROUP`, потому что это пила без выбранного хорошего входа. Предыдущий `SCREENSHOT_DRAFT` остается архивной черновой версией, но актуальная рабочая версия для 15 мая теперь `USER_CORRECTED_V1`.

Граница: эта user-corrected версия сохранена как источник истории и superseded by approved V1. Актуальный approved ledger: `STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_APPROVED_V1.csv`.

## Current State 2026-07-14 STAS5 V4 Human-Style Group Ranker TZ

Текущий статус: `STAS5_V4_20260515_SCREENSHOT_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По решению пользователя зафиксирован новый V4-контур: не построчный `KEEP/CUT` классификатор, а group ranker, который выбирает лучший вход внутри локальной группы кандидатов и объясняет, почему соседние входы хуже.

Главный документ:

```text
STAS5_ML_CORE/07_STAS5_V4_HUMAN_STYLE_GROUP_RANKER_TZ_RU.md
```

Создана V4-папка и схема будущего ledger:

```text
STAS5_ML_CORE/v4/README_RU.md
STAS5_ML_CORE/schemas/STAS5_V4_GROUP_RANK_LEDGER.schema.json
```

Новый источник истины будущей разметки:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Календарь: базовые `24` дня = `2026-05-01..2026-05-14 + 2026-05-16..2026-05-25`; день `2026-05-15` остается карантинным до approved group ledger. Если `2026-05-15` будет включен после утверждения, календарь станет `25` дней.

Граница: обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались. Следующий практический шаг - оформить групповой ledger, начиная с карантинного `2026-05-15` и перевода уже размеченных `2026-05-16..2026-05-20` в формат `group_id + reason_code + winner`.

По пользовательскому скриншоту `2026-05-15` с красными подчеркиваниями создан первый draft group-review:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_SCREENSHOT_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_ANNOTATED_DRAFT.png
```

Draft CSV содержит `41` строк: `BEST_GOOD=5`, `GOOD_ALT=3`, `BAD_IN_GROUP=22`, `NO_TRADE_GROUP=11`. Черновые winners: `LA004`, `LA007`, `LA021`, `LA054`, `LA061`; если нужен жесткий режим `2..3` входа в день, главный кандидатный набор: `LA021`, `LA054`, `LA061`. Этот слой остается `DRAFT`, день `2026-05-15` все еще не включен в train.

## Current State 2026-07-14 STAS5 V3 Review Train Forward 21-25

Текущий статус: `STAS5_V3_REVIEW_TRAIN_FORWARD_21_25_READY`.

Собран и проверен V3-контур:

```text
train = 2026-05-01..2026-05-14 + user review 2026-05-16..2026-05-20
excluded = 2026-05-15
holdout/blind-forward = 2026-05-21..2026-05-25
feature_set = full_v2_all_274
feature_count = 274
```

Факты: ledger `135` строк, train rows `134`; dataset `1106` строк; guard `PASS`; wrapper-run `stas5_v3_wrapper_smoke2_20260714` дал `5/5` PNG за `2026-05-21..2026-05-25`.

Forward totals:

```text
ENTER=79
UNSURE=31
SKIP=247
```

Рабочая папка графиков:

```text
STAS5_ML_CORE/artifacts/v3/forward/runs/stas5_v3_wrapper_smoke2_20260714/
```

Главный отчет и команда:

```text
STAS5_ML_CORE/06_STAS5_V3_REVIEW_TRAIN_FORWARD_RESULT_RU.md
STAS5_ML_CORE/run_stas5_v3_review_train_forward_21_25.ps1
```

Граница: TP/Stas3/API/Optuna/threshold tuning не запускались.

## Current State 2026-07-13 STAS5 V2 Full274 Run Check

Текущий статус: `STAS5_V2_FULL274_RUN_CHECK_PASS_TECHNICAL_REVIEW_REQUIRED`.

Последний full274 run:

```text
stas5_v2_full274_20260713_203703
```

Технически все сошлось: model/forward pointers совпадают, `model_feature_set=full_v2_all_274`, `feature_count=274`, guard `PASS`, forward `435` строк за `2026-05-15..2026-05-20`, все 6 PNG готовы.

Forward counts:

```text
ENTER=77, UNSURE=24, SKIP=334
```

Отчет:

```text
STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_FULL274_RUN_CHECK_20260713_203703_RU.md
```

Ограничение: full274 не является автоматически лучшим вариантом; train AUC `0.649292`, baseline `v1_plus_risk_gate` AUC `0.684988`. Следующий шаг - визуальный review PNG.

## Current State 2026-07-13 STAS5 V2 Full 274 Wrapper

Текущий статус: `STAS5_V2_FULL_274_WRAPPER_READY`.

Добавлен безопасный wrapper для полного прогона `full_v2_all_274`:

```text
STAS5_ML_CORE/run_stas5_v2_full_274_train_forward.ps1
```

Он делает один связанный запуск: пересборка train V2 combo features, train snapshot, leakage guard, pre-ML audit, numeric coverage audit, forward V2 combo features, обучение `full_v2_all_274`, затем blind-forward `2026-05-15..2026-05-20`. В конце wrapper проверяет, что model manifest реально имеет `model_feature_set=full_v2_all_274` и `feature_count=274`.

Сам тяжелый full-прогон не запускался. Проверены только PowerShell-синтаксис wrapper и `py_compile` нужных Python-модулей.

## Current State 2026-07-13 STAS5 V2 Graph To Feature Audit

Текущий статус: `STAS5_V2_GRAPH_TO_FEATURE_AUDIT_READY`.

Проверен train-график `2026-05-04` из batch:

```text
STAS5_ML_CORE/artifacts/v2/visual_approval/runs/stas5_v2_train_visual_20260713_14d/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png
```

Итог: график полностью состыкован с full snapshot (`74` строки, `9 KEEP`, `65 CUT`, feature columns `274`), но latest controlled model использует только `126` признаков набора `v1_plus_risk_gate`. В текущую модель не входят `stas4_v2_combo_*`, `stas4_v2_density_*`, `stas4_v2_structure_*`, `stas4_v2_block_*`, `stas4_v2_pattern_*`, `stas5_v2_short_wave_*`, `stas4_v2_volume_*`, `stas4_v2_div_*`.

Отчет:

```text
STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_GRAPH_TO_FEATURE_AUDIT_20260504_RU.md
```

Граница: это audit-only. Никакое новое обучение, TP/Stas3, API, Optuna или threshold tuning не запускались.

## Current State 2026-07-13 STAS5 V2 Train Visual Batch

Текущий статус: `STAS5_V2_TRAIN_VISUAL_BATCH_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Train-графики теперь покрывают все `14` дней обучения, а не только `2026-05-04`.

Путь:

```text
STAS5_ML_CORE/artifacts/v2/visual_approval/runs/stas5_v2_train_visual_20260713_14d/
```

Manifest:

```text
STAS5_ML_CORE/artifacts/v2/visual_approval/runs/stas5_v2_train_visual_20260713_14d/STAS5_V2_TRAIN_VISUAL_BATCH_MANIFEST.json
```

Проверенные факты: `14/14` PNG, rows `972`, `KEEP=115`, `CUT=857`, latest pointer создан. STAS5 tests `34 passed`.

## Current State 2026-07-13 STAS5 V2 Run Isolation

Текущий статус: `STAS5_V2_RUN_ISOLATION_READY`.

Повторные V2-прогоны больше не должны писаться поверх старых дневных папок. CLI запускается с общим `--run-id`; обучение пишет в `artifacts/v2/model/runs/<run_id>/`, forward пишет в `artifacts/v2/forward/runs/<run_id>/`.

Проверочный run:

```text
stas5_v2_run_20260713_190743
```

Latest pointers:

```text
STAS5_ML_CORE/artifacts/v2/model/STAS5_V2_LATEST_MODEL_RUN.json
STAS5_ML_CORE/artifacts/v2/forward/STAS5_V2_LATEST_FORWARD_RUN.json
```

Проверки: STAS5 tests `34 passed`.

## Current State 2026-07-13 STAS5 V2 Controlled Forward

Текущий статус: `STAS5_V2_CONTROLLED_FORWARD_READY_NO_TP_NO_API_NO_STAS3`.

V2 контур доведен до результата после numeric coverage:

1. ablation baseline готов;
2. selected controlled model обучена на `v1_plus_risk_gate`;
3. blind-forward `2026-05-15..2026-05-20` готов;
4. CSV/PNG по каждому forward-дню готовы.

Модель: `126` features, LOO AUC `0.684988`, train LOO decisions `ENTER=201`, `UNSURE=114`, `SKIP=657`.

Forward: `ENTER=106`, `UNSURE=45`, `SKIP=284`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2/model/STAS5_V2_CONTROLLED_MODEL_AND_FORWARD_REPORT_RU.md
STAS5_ML_CORE/artifacts/v2/model/stas5_v2_entry_ranker_20260501_20260514_v0.manifest.json
STAS5_ML_CORE/artifacts/v2/forward/STAS5_V2_FORWARD_ENTRY_REVIEW_MANIFEST.json
STAS5_ML_CORE/artifacts/v2/forward/20260515/STAS5_V2_FORWARD_ENTRY_REVIEW_20260515.png
```

Граница: forward postfact только audit-only. Forward не использован для обучения или threshold tuning. TP/Stas3/API/Optuna не запускались.

Следующий шаг: пользователь смотрит PNG и выбирает реальные/шумные входы для следующего улучшения.

## Current State 2026-07-13 STAS5 V2 Numeric Coverage

Текущий статус: `STAS5_V2_NUMERIC_COVERAGE_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Закрыт аудит вопроса пользователя: “ML видит только цифры, значит надо проверить, что все индикаторы/фичи/стратегии с графика передаются численно”. Проверка велась на train-дне `2026-05-04`.

Численно подключено:

1. STAS4 strategy blocks: `stas4_v2_block_density_structure_*`, `stas4_v2_block_pattern_structure_*`, `stas4_v2_block_structure_volume_*`, `stas4_v2_block_structure_trend_*`;
2. pattern layer: `stas4_v2_pattern_*`;
3. causal SHORT/WAVE layer: `stas5_v2_short_wave_*`.

Проверенные факты: V2 combo features `163`; полный train snapshot `274` feature columns; train rows `972`; forward rows `435`; forbidden feature columns `{}`; `KEEP_DRAFT + yellow_x = 30`; guard `PASS`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_NUMERIC_COVERAGE_AUDIT_20260504_RU.md
STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_numeric_coverage_audit_20260504_v0.json
```

Граница: это не обучение и не final decision. PNG, human labels, yellow X/conflict, postfact, TP/Stas3/exit не являются ML features. Следующий шаг после подтверждения пользователя - V2 ablation baseline.

## Current State 2026-07-13 STAS5 V2 Strategy Audit Strip

Текущий статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_WITH_STRATEGY_AUDIT_READY_WAIT_USER_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Approval-график `2026-05-04` обновлен: добавлена полоса `STAS4 Audit` с четырьмя стратегиями `density_profile+structure_ta`, `pattern+structure_ta`, `structure_ta+volume_flow`, `structure_ta+trend_momentum`. Это визуальный audit-only слой, не hard-filter и не ML-решение.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.manifest.json
```

Manifest фиксирует strategy audit counts: `22/2`, `38/1`, `52/1`, `59/4` по четырем стратегиям. Основные маркеры не изменены: `KEEP_DRAFT=9` зеленые, `CUT_DRAFT=65` красные, `yellow_x_cut=18`, `KEEP+yellow_conflict=4` голубая накладка поверх зеленого KEEP.

Граница: обучение, ablation, threshold tuning, Optuna/API и Stas3/TP не запускались. Следующий шаг - пользователь визуально проверяет PNG.

## Current State 2026-07-13 STAS5 V2 Feature Visual Approval

Текущий статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_READY_WAIT_USER_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Перед пунктом 8 V2 ТЗ добавлен обязательный визуальный контроль признаков: train-день `2026-05-04` отрисован в стиле старого STAS4 overlay, но с V2 feature snapshot и ручными labels.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.manifest.json
```

На графике есть свечи, volume, session shading, `FON/LONG/SHORT/WAVE`, все LA-кандидаты, human `KEEP/CUT`, yellow X, `KEEP + yellow_x`, density/structure, risk/gate, V2 combo snapshot и старый `COMBO SPECTRUM`. Visual rule: все `KEEP_DRAFT=9` рисуются зелеными, а `KEEP + yellow_x_conflict=4` получают голубую накладку поверх зеленого KEEP.

Проверенные факты: `74` кандидата, `KEEP_DRAFT=9`, `CUT_DRAFT=65`, yellow X `22`, conflicts `4`, PNG `4960x4262`, pixel-check не пустой.

Проверки: `py_compile` PASS; `tests/test_stas5_v2_feature_visual_approval.py` PASS `3 passed`; render command PASS.

Граница: это visual approval only. Обучение, ablation, threshold tuning, production permission, Optuna/API и Stas3/TP не запускались. Следующий шаг - пользователь смотрит PNG и дает добро или правки.

## Current State 2026-07-13 STAS5 V2 Pre-ML Audit

Текущий статус: `STAS5_V2_PRE_ML_AUDIT_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

По основному ТЗ V2 закрыт раздел 14, пункт 7: создан `src/mlbotnav/stas5_v2_pre_ml_audit.py`.

V2 pre-ML audit сравнивает:

1. train `KEEP/CUT` по `214` признакам из V2 feature snapshot;
2. группы признаков V1/V2;
3. forward error classes из `stas5_forward_error_ledger_20260515_20260520_v0.csv`;
4. guard/ledger статусы перед любым следующим modeling шагом.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_PRE_ML_AUDIT_20260501_20260520_RU.md
STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_pre_ml_audit_20260501_20260520_v0.json
```

Проверенные факты: status `READY_FOR_V2_ABLATION_BASELINE`, train rows `972`, `KEEP_DRAFT=115`, `CUT_DRAFT=857`, `KEEP_DRAFT + yellow_x = 30`, feature count `214`, guard `PASS`, forward error ledger `PASS`, forbidden feature columns `{}`. Forward audit: bad green `55`, good green `48`, missed good SKIP `65`. Сильные группы: `v1_stas1_candidate`, `v1_stas2_pre_windows`, `v2_combo_indicator`, `v2_structure`.

Проверки: `py_compile` PASS; `tests/test_stas5_v2_pre_ml_audit.py` PASS `3 passed`; явный STAS5 test pack PASS `24 passed`.

Граница: audit не обучает модель, не подбирает threshold, не делает trading permission и не использует Stas3/TP/exit. Следующий пункт строго по ТЗ: раздел 14, пункт 8 - ablation baseline.

## Current State 2026-07-13 STAS5 V2 Forward Error Ledger

Текущий статус: `STAS5_V2_FORWARD_ERROR_LEDGER_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

По основному ТЗ V2 закрыт раздел 14, пункт 6: создан `src/mlbotnav/stas5_v2_forward_error_ledger.py`.

Forward error ledger соединяет:

1. V1 forward decisions `ML_DECISION/ML_KEEP_SCORE` за `2026-05-15..2026-05-20`;
2. postfact audit поля `hit_0p5`, `hit_1p0`, `max_up`, `max_drawdown`;
3. V2 combo/risk/gate features;
4. опциональные `USER_KEEP_FORWARD_AUDIT` из user-review CSV, если пользователь их заполнит.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.csv
STAS5_ML_CORE/artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.manifest.json
```

Проверенные факты: `PASS`, `435` строк, join V1/V2 без потерь, duplicate keys `0`. V1 decisions: `ENTER=103`, `UNSURE=55`, `SKIP=277`. Error classes: `GREEN_BAD_FALLING_KNIFE=46`, `GREEN_BAD_NO_REVERSAL=9`, `GREEN_GOOD=48`, `YELLOW_BAD=34`, `YELLOW_GOOD=21`, `SKIP_CORRECT=212`, `SKIP_MISSED_GOOD=65`. V2 expected decisions: `ENTER=35`, `UNSURE=121`, `SKIP=279`.

Проверки: `py_compile` PASS; `tests/test_stas5_v2_forward_error_ledger.py` PASS `3 passed`; явный STAS5 test pack PASS `21 passed`.

Граница: ledger audit-only. Postfact и user-review поля не являются feature columns, train labels или threshold tuning input. Следующий пункт строго по ТЗ: раздел 14, пункт 7 - V2 pre-ML audit.

## Current State 2026-07-13 STAS5 V2 Leakage Guard

Текущий статус: `STAS5_V2_LEAKAGE_GUARD_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

По основному ТЗ V2 закрыт раздел 14, пункт 5: создан `src/mlbotnav/stas5_v2_leakage_guard.py`.

Guard проверяет V2 train snapshot `2026-05-01..2026-05-14`:

1. feature columns из manifest, не весь CSV;
2. отсутствие `future/postfact/outcome/Stas3/TP/exit/yellow/strategy` в feature columns;
3. `v2_combo_feature_time_utc < entry_time_utc`;
4. отсутствие forward-дней `2026-05-15+` в train snapshot;
5. сохранение `KEEP_DRAFT + yellow_x = 30`;
6. row parity с manifest и ledger.

Артефакт:

```text
STAS5_ML_CORE/artifacts/v2/guard/stas5_v2_leakage_guard_20260501_20260514_v0.json
```

Проверенные факты: `PASS`, `972` строк, `214` feature columns, forbidden feature columns `{}`, label/metadata columns in features `[]`, missing required metadata `[]`, duplicate keys `0`, feature time not before entry `0`, forward days present `0`, label counts `KEEP_DRAFT=115`, `CUT_DRAFT=857`.

Проверки: `py_compile` PASS; `tests/test_stas5_v2_leakage_guard.py` PASS `4 passed`; явный STAS5 test pack PASS `18 passed`.

Следующий пункт строго по ТЗ: раздел 14, пункт 6 - создать `stas5_v2_forward_error_ledger.py`. Не переходить к обучению, threshold tuning, Stas3/TP, API/Optuna или V2 PNG до закрытия forward error ledger и pre-ML audit.

## Current State 2026-07-13 STAS5 V2 Feature Snapshot

Текущий статус: `STAS5_V2_FEATURE_SNAPSHOT_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

По основному ТЗ V2 закрыт раздел 14, пункт 4: создан `src/mlbotnav/stas5_v2_feature_snapshot_builder.py`.

Snapshot объединяет:

1. v1 ledger/labels `2026-05-01..2026-05-14`;
2. v1 Stas2 feature snapshot `111` признаков;
3. V2 combo feature layer `103` признака.

Артефакты:

1. `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.csv`;
2. `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.manifest.json`.

Проверенные факты: `PASS`, `972` строк, `214` feature columns, `lost_after_combo_join=0`, `lost_after_ledger_check=0`, `entry_time_mismatch=0`, `anchor_time_mismatch=0`, `v2_combo_feature_available_before_entry_false=0`, forbidden columns `{}`, `KEEP_DRAFT + yellow_x = 30` сохранены.

Проверки: `py_compile` PASS; `tests/test_stas5_v2_feature_snapshot_builder.py` PASS; явный STAS5 test pack `14 passed`.

Следующий пункт строго по ТЗ: раздел 14, пункт 5 - создать `stas5_v2_leakage_guard.py`. Не переходить к user-review 15 мая, forward labels, обучению или threshold, пока leakage guard и pre-ML audit не закрыты.

## Current State 2026-07-13 STAS5 V2 Forward User Review

Текущий статус: `STAS5_V2_FORWARD_USER_REVIEW_READY_WAIT_USER_3_KEEP_IDS`.

После V2 combo exporter создан крупный review-renderer:

```text
src/mlbotnav/stas5_v2_forward_user_review.py
```

Он рисует `2026-05-15` страницами по 3 часа, с крупными свечами, LA-id, `knife_risk`, `short_pressure`, `long_recovery` и combo-панелью. Это нужно, чтобы пользователь выбрал примерно 3 реальных входа из 90 кандидатов дня.

Артефакты:

1. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_FULL.png`;
2. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_PAGE_01_0000_0300.png`;
3. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_PAGE_02_0300_0600.png`;
4. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_PAGE_05_1200_1500.png`;
5. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_TEMPLATE_20260515.csv`;
6. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515.manifest.json`.

Проверенные факты: `90` forward-кандидатов; buckets: `54 HIGH_RISK`, `30 CAUTION`, `5 LOW_RISK`, `1 BLOCKED`; command status `PASS`.

Следующий практический шаг: пользователь называет точные LA-id трех реальных входов. После этого заполнить `user_review_label`: выбранные как `USER_KEEP_FORWARD_AUDIT`, остальные как `NOISE_FORWARD_AUDIT`, затем сделать comparison audit `3 vs 87`.

Граница: это forward audit-only. Не использовать `2026-05-15` для обучения, threshold tuning или финального trading permission.

## Current State 2026-07-13 STAS5 V2 Combo Feature Exporter

Текущий статус: `STAS5_V2_COMBO_FEATURE_EXPORT_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Первый практический шаг STAS5 V2 / contour 2 выполнен: создан `src/mlbotnav/stas5_v2_combo_feature_exporter.py`, который превращает STAS4 combo-spectrum из визуального нижнего блока в реальные causal ML-признаки.

Главный контракт:

```text
feature_time_utc = anchor_time_utc < entry_time_utc
```

Экспортер берет OHLCV из `data/core/bybit_ohlcv`, пересчитывает STAS4 indicators/density/structure/divergence до сигнальной свечи и не использует PNG, future outcome, Stas3/TP/exit, yellow X или strategy votes как признаки.

Готовые артефакты:

1. train: `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.csv`;
2. train manifest: `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.manifest.json`;
3. forward: `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.csv`;
4. forward manifest: `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.manifest.json`.

Проверенные факты: train `972/972`, forward `435/435`, feature count `103`, forbidden columns `{}`, `feature_available_before_entry_false=0`, tests `11 passed`.

Следующий практический шаг: собрать V2 feature snapshot, который объединит v1 ledger/Stas2 context и новый combo feature layer, затем запустить V2 leakage guard и pre-ML audit. Финальную V2 ML-модель пока не обучать.

## Current State 2026-07-13 STAS5 V1 Hard Audit And V2 TZ

Текущий статус: `STAS5_V1_AUDITED_V2_CONTOUR2_TZ_READY_NO_OPTUNA_NO_API_NO_STAS3`.

Проведен жесткий аудит STAS5 v1 с тремя read-only агентами и локальными расчетами по forward CSV `2026-05-15..2026-05-20`.

Главный вывод: STAS5 v1 технически собран правильно, но не годится как финальный production entry permission. Причина не в поломке pipeline, а в неполном составе признаков и отсутствии permission/risk gate. Combo-spectrum/STAS4 indicator block был найден в `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum`, но в STAS5 v1 он был только `visual/audit layer`, не ML training feature.

Новые source-of-truth документы:

1. `STAS5_ML_CORE/04_STAS5_V1_HARD_AUDIT_RU.md`;
2. `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`.

Проверенные факты v1: ledger `972`, `115 KEEP_DRAFT`, `857 CUT_DRAFT`, `30 KEEP_DRAFT + yellow_x`, feature count `111`, combo/STAS4 features in model `0`, leakage guard `PASS`, model `CONTROLLED_BASELINE_READY`.

Forward audit: `ENTER` `103` rows, `hit0.5=74.8%`, `hit1.0=46.6%`, median `max_up=0.951%`, median drawdown `-1.453%`. Проблемные дни: `2026-05-15` и `2026-05-16`; по `2026-05-15` `ENTER hit1.0=14.3%`, median drawdown `-2.834%`.

Следующий практический шаг: реализовывать STAS5 V2 / contour 2 только после утверждения ТЗ. V2 должен добавить combo feature exporter, phase gate, long permission gate, risk/noise filter, forward error ledger, ablation и calibration audit.

Граница: не использовать v1 как торговое разрешение; не подбирать threshold по forward `15+`; не превращать yellow X в hard-cut; не запускать Optuna/scorer/target-lock/API/Stas3 в этом контуре.

## Current State 2026-07-10 STAS5 Entry ML Pipeline Ready

Текущий статус: `STAS5_ENTRY_ML_PIPELINE_READY_TRAIN_1_14_FORWARD_15_20_NO_OPTUNA_NO_API_NO_STAS3`.

STAS-5 по входам собран как отдельный контур внутри текущего проекта. Source-of-truth: `STAS5_ML_CORE/`.

Готово:

1. ML-ledger: `STAS5_ML_CORE/artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.csv`;
2. feature snapshot: `STAS5_ML_CORE/artifacts/features/stas5_feature_snapshot_20260501_20260514_v0.csv`;
3. leakage guard: `STAS5_ML_CORE/artifacts/guard/stas5_leakage_guard_20260501_20260514_v0.json`;
4. pre-ML audit: `STAS5_ML_CORE/artifacts/audit/STAS5_PRE_ML_AUDIT_20260501_20260514_RU.md`;
5. controlled baseline: `STAS5_ML_CORE/artifacts/model/stas5_entry_ranker_20260501_20260514_v0.joblib`;
6. forward CSV/PNG: `STAS5_ML_CORE/artifacts/forward/20260515..20260520/`.

Проверенные факты: ledger `972` rows, `115 KEEP_DRAFT`, `857 CUT_DRAFT`, `30 KEEP_DRAFT + yellow_x`; feature snapshot `111` model features; leakage guard `PASS`; audit `READY_FOR_CONTROLLED_BASELINE`; baseline `CONTROLLED_BASELINE_READY`; forward `FORWARD_ENTRY_REVIEW_READY`.

Baseline является черновым controlled ranker по entry-only задаче: `candidate + pre-entry features -> human KEEP/CUT -> ML_KEEP_SCORE -> ENTER/UNSURE/SKIP`. Train window только `2026-05-01..2026-05-14`. Forward `2026-05-15..2026-05-20` не использован для обучения или threshold tuning.

Метрики baseline из leave-one-day-out: AUC `0.6828`, KEEP recall по `ENTER` `0.4087`, KEEP recall по `ENTER+UNSURE` `0.5652`, CUT precision по `SKIP` `0.9226`, KEEP+yellow_x recall по `ENTER+UNSURE` `0.4667`.

Граница: Optuna, scorer, target-lock, API/мост Bybit и Stas3/TP/exit не запускались и не входят в STAS-5 entry ML. Postfact-поля в forward CSV являются audit-only, не feature и не threshold input.

## Current State 2026-07-10 STAS5 Current Work

Текущий статус: `STAS5_TZ_TRAIN_1_14_FORWARD_15_PLUS_NO_TP_NO_API`.

Рабочая папка STAS-5 находится в корне проекта: `STAS5_ML_CORE/`.

Новая текущая инструкция: `STAS5_ML_CORE/03_STAS5_CURRENT_EXECUTION_INSTRUCTION_RU.md`.

Что делаем сейчас: готовим supervised-контур для ML по входам. Train/manual label window: `2026-05-01..2026-05-14`. Forward/blind check window: `2026-05-15+`; эти дни не используются для обучения, подбора threshold или ручной доводки. Forward PNG должен помечать каждую кандидатную точку как `ENTER/UNSURE/SKIP`.

Что уже есть для базы: `115` `KEEP_DRAFT`, `857` `CUT_DRAFT`, `30` пользовательских `KEEP_DRAFT` с yellow X. Поэтому yellow X не может быть фильтром, target-меткой или причиной удаления строки.

Главная формула остается:

```text
candidate entry + pre-entry features -> human KEEP / CUT
```

Следующий практический шаг: создать `src/mlbotnav/stas5_ml_ledger_builder.py`, который соберет `STAS5_ML_CORE/artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.csv` из ручных labels и `STAS2_RECORDS.csv`, проверит `972` rows, `115/857`, `30` `KEEP_DRAFT + yellow_x`, row parity и совпадение `record_id/entry_time`. После ledger идут feature snapshot, leakage guard, controlled baseline и `stas5_forward_entry_review.py` для PNG на `2026-05-15+`.

Граница: Optuna, scorer, target-lock, API/мост Bybit и Stas3 TP/exit сейчас не запускать. Future outcome можно считать только после факта для audit/backtest, не как feature/target/filter/threshold input.

## Current State 2026-07-10 STAS4 Moved To Root

Текущий статус: `STAS4_ROOT_HOME_READY_NO_ML_NO_OPTUNA`.

STAS4 перенесен из старого скрытого пути `reports/final_review/stas4_feature_hypothesis_screen_v0` в корень проекта:

```text
STAS4_FEATURE_HYPOTHESIS_REVIEW
```

Новый источник правды для STAS4: `STAS4_FEATURE_HYPOTHESIS_REVIEW/README_RU.md`.

Главная ручная разметка: `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels`.

Генератор `src/mlbotnav/visual_entry_stas4_family_overlay.py` теперь по умолчанию пишет в `STAS4_FEATURE_HYPOTHESIS_REVIEW`.

В старом `reports/final_review` оставлен указатель `STAS4_MOVED_TO_ROOT_RU.md`. Если старый каталог `reports/final_review/stas4_feature_hypothesis_screen_v0` временно виден, это остаточные пустые директории, которые Windows не дал удалить из-за открытого просмотрщика/проводника. Источником правды они не являются.

Граница: перенос структуры и обновление ссылок. Stas1/Stas2/Stas4 логика, ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Current State 2026-07-10 STAS5 ML Entry Architecture Draft

Текущий статус: `STAS5_ML_ENTRY_ARCHITECTURE_DRAFT_NO_ML_NO_OPTUNA`.

Новый видимый source-of-truth для STAS-5 лежит в корне проекта: `STAS5_ML_CORE/`.

Смысл STAS-5: обучать ML выбирать хорошие входы из Stas1/Stas2-кандидатов `LAxxx` по pre-entry признакам Stas2/Stas4 и решению человека `KEEP/CUT`. Стратегии и желтый `X` являются контекстом/audit vote, но не label и не hard-filter.

Текущая база обсуждения: ручная разметка `2026-05-01..2026-05-14`, всего `972` входа, `115` `KEEP_DRAFT`, `857` `CUT_DRAFT`. `30` пользовательских `KEEP_DRAFT` имеют yellow X, поэтому hard-cut по yellow X запрещен.

Первый STAS-5 ML-ledger должен хранить отдельно: `human_label`, `label_status`, `strategy_votes`, `yellow_x_role=AUDIT_ONLY`, `yellow_x_conflict`. Первый baseline должен исключать yellow-поля из feature matrix.

Следующая работа: собрать единый ML-ledger, затем causal feature snapshot до входа и audit признаков без запуска ML.

Граница: Stas3, TP, exit, MFE/MAE и post-entry ladder не входят в STAS-5 entry ML. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Current State 2026-07-10 Yellow X Audit Only Rule

Текущий статус: `YELLOW_X_AUDIT_ONLY_FIXED_RULE_NO_ML_NO_OPTUNA`.

Зафиксировано правило для будущей ML-подготовки входов: желтый `X` стратегии `density_profile+structure_ta` не является плохой сделкой, запретом входа, причиной закрытия или ML-target. Его роль только `AUDIT_ONLY`.

Приоритет: `human KEEP_APPROVED` выше любого `strategy yellow X`. Если пользователь оставил вход, а стратегия поставила желтый `X`, строка остается положительным примером для ML с флагами `stas4_density_structure_yellow_x = 1` и `yellow_x_conflict = 1`.

По текущей 14-дневной пачке `2026-05-01..2026-05-14`: `115` KEEP_DRAFT, из них `30` имеют желтый `X`. Поэтому hard-cut по `yellow_x = 1` уже доказанно режет хорошие пользовательские входы и запрещен.

Правило записано в `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels/YELLOW_X_AUDIT_ONLY_RULE_RU.md`.

Граница: ML/export/training, Optuna, scorer, target-lock и API не запускались. Stas1/Stas2/Stas4 логика не менялась.

## Current State 2026-07-10 STAS4 Manual Labels Draft 20260501-20260514 Complete

Текущий статус: `STAS4_MANUAL_LABELS_20260501_20260514_DRAFT_COMPLETE_NO_ML_NO_OPTUNA`.

Пользователь вручную подчеркивал на PNG те Stas2/Stas4-входы, которые нужно оставить как `KEEP_DRAFT`; остальные входы дня в этом черновом проходе помечены `CUT_DRAFT`.

Готова вся 14-дневная пачка `2026-05-01..2026-05-14`: суммарно `972` входа, `115` KEEP_DRAFT и `857` CUT_DRAFT.

Последний обработанный день `2026-05-14`: `11` KEEP из `77` входов. KEEP: `LA014`, `LA015`, `LA032`, `LA039`, `LA046`, `LA047`, `LA048`, `LA049`, `LA053`, `LA055`, `LA056`. Желтый `X` среди выбранных: `LA047`, `LA053`.

Файлы дня:
- `KEEP_20260514_FROM_RED_UNDERLINES_DRAFT.csv`;
- `LABELS_20260514_ALL_ENTRIES_DRAFT.csv`;
- `KEEP_20260514_FROM_RED_UNDERLINES_DRAFT.json`;
- `ANNOTATED_20260514_KEEP_DRAFT.png`.

Граница: это не финальная ML-обучающая выборка, а черновой human-review ledger. Stas1/Stas2/Stas4 логика не менялась. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Current State 2026-07-10 STAS4 Manual Labels Draft 20260501-20260513

Текущий статус: `STAS4_MANUAL_LABELS_20260501_20260513_DRAFT_NO_ML_NO_OPTUNA`.

Пользователь вручную подчеркивает на PNG те Stas2/Stas4-входы, которые нужно оставить как `KEEP_DRAFT`; все остальные входы дня в этом черновом проходе помечаются `CUT_DRAFT`.

Готово `13` дней из текущей 14-дневной пачки `2026-05-01..2026-05-14`: всего `104` KEEP и `791` CUT по дням `2026-05-01..2026-05-13`, суммарно `895` входов.

Последний обработанный день `2026-05-13`: `4` KEEP из `86` входов. KEEP: `LA002`, `LA043`, `LA058`, `LA072`. Файлы дня:
- `KEEP_20260513_FROM_RED_UNDERLINES_DRAFT.csv`;
- `LABELS_20260513_ALL_ENTRIES_DRAFT.csv`;
- `KEEP_20260513_FROM_RED_UNDERLINES_DRAFT.json`;
- `ANNOTATED_20260513_KEEP_DRAFT.png`.

Граница: это не финальная ML-обучающая выборка, а черновой human-review ledger. Stas1/Stas2/Stas4 логика не менялась. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Current State 2026-07-10 STAS4 Manual Labels Draft 20260501-20260512

Текущий статус: `STAS4_MANUAL_LABELS_20260501_20260512_DRAFT_NO_ML_NO_OPTUNA`.

Пользователь вручную подчеркивает на PNG те Stas2/Stas4-входы, которые нужно оставить как `KEEP_DRAFT`; все остальные входы дня в этом черновом проходе помечаются `CUT_DRAFT`.

Готово `12` дней из текущей 14-дневной пачки `2026-05-01..2026-05-14`: всего `100` KEEP и `709` CUT по дням `2026-05-01..2026-05-12`, суммарно `809` входов.

Последний обработанный день `2026-05-12`: `6` KEEP из `76` входов. KEEP: `LA006`, `LA012`, `LA036`, `LA038`, `LA051`, `LA055`. Файлы дня:
- `KEEP_20260512_FROM_RED_UNDERLINES_DRAFT.csv`;
- `LABELS_20260512_ALL_ENTRIES_DRAFT.csv`;
- `KEEP_20260512_FROM_RED_UNDERLINES_DRAFT.json`;
- `ANNOTATED_20260512_KEEP_DRAFT.png`.

Граница: это не финальная ML-обучающая выборка, а черновой human-review ledger. Stas1/Stas2/Stas4 логика не менялась. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Current State 2026-07-10 STAS4 Manual Labels Draft

Текущий статус: `STAS4_MANUAL_LABELS_20260501_20260511_DRAFT_NO_ML_NO_OPTUNA`.

Пользователь вручную подчеркивает на PNG те Stas2/Stas4-входы, которые нужно оставить как `KEEP_DRAFT`; все остальные входы дня в этом черновом проходе помечаются `CUT_DRAFT`.

Готово `11` дней из текущей 14-дневной пачки `2026-05-01..2026-05-14`: всего `94` KEEP и `639` CUT по дням `2026-05-01..2026-05-11`.

Последний обработанный день `2026-05-11`: `10` KEEP из `76` входов. Файлы дня:
- `KEEP_20260511_FROM_RED_UNDERLINES_DRAFT.csv`;
- `LABELS_20260511_ALL_ENTRIES_DRAFT.csv`;
- `KEEP_20260511_FROM_RED_UNDERLINES_DRAFT.json`;
- `ANNOTATED_20260511_KEEP_DRAFT.png`.

Граница: это не финальная ML-обучающая выборка, а черновой human-review ledger. Stas1/Stas2/Stas4 логика не менялась.

## Current State 2026-07-10 STAS2/STAS4 Compact Strips

Текущий статус визуального слоя: `STAS2_STAS4_COMPACT_STRIPS_READY_NO_LOGIC_CHANGE_NO_ML_NO_OPTUNA`.

Дневные overview/overlay теперь рисуют строки `ФОН`, `LONG`, `SHORT`, `WAVE` компактнее: высоты полос уменьшены примерно в 2 раза через общие `OVERVIEW_HEIGHT_RATIOS`. Цена занимает больше вертикального пространства, объем остается снизу.

Ось времени снизу переведена на общий helper `_set_day_time_axis`: тики идут `00:00, 02:00, ..., 22:00, 00:00`, где последний `00:00` - правая граница следующего дня.

Контрольные картинки:

- Stas2: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260511_visual_half_strips_smoke_v1_20260710_073524/STAS2_DAY_OVERVIEW_20260511.png`
- Stas4: `STAS4_FEATURE_HYPOTHESIS_REVIEW/visual_half_strips_smoke_v1/STAS4_pattern+structure_ta_OVERLAY_20260511_20260710_073654.png`

Граница: расчеты фаз, волн, entry rows, CSV/XLSX, Stas1 и Stas3 не менялись.

## Current State 2026-07-09 STAS3 V2 Clean Ready

Текущий статус: `STAS3_V2_CLEAN_READY_NO_OLD_STAS3_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

Предыдущий V2 run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925` помечен как `INVALID_OLD_STAS3_BASE_DRAFT`, потому что был собран через доработку старого Stas3. Его не использовать как принятый V2.

Актуальный clean run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_clean_20260510_20260512_long_only_20260709_123622`

Источник: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`; дни `2026-05-10`, `2026-05-11`, `2026-05-12`.

Реализация: новый модуль `src/mlbotnav/visual_entry_stas3_v2_clean_review.py`, без импорта/наследования старого Stas3. Runner: `STAS3_PERCENT_LADDER_REVIEW/run_clean_v2.ps1`. Открытие: `STAS3_PERCENT_LADDER_REVIEW/open_clean_v2_last_run.ps1`.

Результат: `214` входов, `214` обработано, `0` skipped, row parity `true`, `157` hit 1%, `79` clean medium TP `>=1%`, `111` wrong 1% TP, `38` good-entry-but-wrong-1% TP, `99` noise, `41` строк phase ladder, `66` PNG, пустых PNG нет.

Главные артефакты: `STAS3_V2_CLEAN_ENTRY_CONTEXT.csv`, `STAS3_V2_CLEAN_TP_PATH.csv`, `STAS3_V2_CLEAN_TP_DECISION.csv`, `STAS3_V2_CLEAN_PHASE_LADDER.csv`, `STAS3_V2_CLEAN_WRONG_TP.csv`, `STAS3_V2_CLEAN_NOISE.csv`, `STAS3_V2_CLEAN_REPORT_RU.md`, `STAS3_V2_CLEAN_TABLES.xlsx`.

Проверено: `py_compile`, `pytest tests/test_visual_entry_stas3_v2_clean_review.py -q`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, full clean run, CSV/XLSX/PNG acceptance. Guardrails: `NO_OLD_STAS3_BASE`, `LONG_ONLY`, `SHORT_RISK_CONTEXT_ONLY`, `WAVE/GAP/continuous` только hindsight-review, без ML/Optuna/API/scorer/target-lock.

## Current State 2026-07-09 STAS3 V2 Ready

Текущий статус: `INVALID_OLD_STAS3_BASE_DRAFT`.

Этот блок является историей ошибки. Этот V2 run был собран через доработку старого Stas3, поэтому не является принятым Stas3 V2. Stas3 V1 не удалялся и остается архивным review-only слоем.

Финальный V2 run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925`

Источник Stas2: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`; дни `2026-05-10`, `2026-05-11`, `2026-05-12`.

Результат: `214` входов, `0` skipped, row parity `true`, `157` hit 1%, `93` reasonable TP, `76` wrong 1% TP, `46` noise, `122` wrong/noise review rows, `55` PNG, пустых PNG нет. Рабочая сетка V2: `0.3-0.9%`, `1.0-2.0%` шаг `0.1%`, `2.2-20.0%` шаг `0.2%`; `0.2%` отсутствует как TP-уровень.

Главные артефакты: `STAS3_V2_ENTRY_TP_AUDIT.csv`, `STAS3_V2_CONTEXT_BUNDLE.csv`, `STAS3_V2_TP_LADDER_BY_PHASE.csv`, `STAS3_V2_WRONG_TP_REVIEW.csv`, `STAS3_V2_SKIPPED_ROWS.csv`, `STAS3_V2_REPORT_RU.md`, `STAS3_PERCENT_LADDER_TABLES.xlsx`.

Проверено: `py_compile`, `pytest tests/test_visual_entry_stas3_percent_ladder_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, `pytest tests/test_visual_entry_stas2_market_phase_review.py -q`, полный V2 run, acceptance CSV/XLSX/PNG. Guardrails: `LONG_ONLY`, `SHORT_RISK_CONTEXT_ONLY`, без short-входов/short-TP/short-ladder, без ML/Optuna/API/scorer/target-lock. `MFE MAX` только diagnostic/hindsight fact, не TP/exit.

## Current State 2026-07-09 STAS3 V2 Reset TZ

Текущий статус: `STAS3_V1_ARCHIVED_STAS3_V2_TZ_DRAFT_READY_NO_ML_NO_OPTUNA`.

Stas3 V1 заморожен как архивный review-only слой. Причина: текущие `MFE MAX`, big-move pages и reasonable TP визуально/смыслово начали превращаться в псевдостратегию и вызывать путаницу с подсмотром будущего.

Новый source-of-truth для продолжения:

`STAS3_PERCENT_LADDER_REVIEW/TZ_STAS3_V2_RESET_RU.md`

ТЗ уточнено по новой правке пользователя: Stas3 V2 работает только по LONG, точки входа не придумываются, а берутся из `STAS2_RECORDS.csv`: `anchor_time_utc`, `anchor_low_price`, `entry_time_utc`, `entry_open_price`, `entry_price_5bps`. Расчетная цена входа: `entry_price_for_calc = entry_price_5bps`. Быстрые TP: `0.3-0.9%`. Средние LONG-ходы: `1.0-2.0%` с шагом `0.1%`, затем `2.0-20.0%` с шагом `0.2%` и дедубликацией `2.0%`. Источник первого V2-разбора: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`, рабочие дни `2026-05-10`, `2026-05-11`, `2026-05-12`. По каждой LONG-сделке нужно собрать единый context bundle: сессия, фон, LONG, `SHORT`-risk% как риск-фон, WAVE, волатильность/процентные блоки, volume-context. Short-входы, short-TP, short-ladder и short-статистика в Stas3 V2 запрещены. `ideal_review_tp_pct` и `max_feasible_review_tp_pct` являются hindsight-review полями, не стратегией. Сделку нельзя искусственно резать по `24h`, если LONG-волна продолжается на следующий день.

Следующая работа: не удалять старые runs, а реализовать Stas3 V2 как чистую процентную лестницу движения и TP-audit по фазам. ML/export/training, Optuna, scorer, target-lock и API запрещены.

## Current State 2026-07-09 STAS3 Rebuild From Latest STAS2

Текущий статус: `STAS3_REBUILT_FROM_STAS2_SHORT_LABELS_V1_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

Актуальный Stas3 run после обновления Stas2:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260508_20260512_from_stas2_short_labels_v1_20260709_084730`

Источник:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138`

Сводка: `214` entries, `0` skipped, `157` hit 1%, `93` reasonable TP, `89` mismatch к 1% TP, `46` noise, `9` fast clean, `68` late-pump dependent. `53` PNG, пустых PNG нет.

Открыть:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open browse
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open tp
```

Ограничение текущей версии: Stas3 использует новый `STAS2_RECORDS.csv`, но не делает join отдельных Stas2 wave-ledger таблиц. Поэтому `WAVE/SHORT` видны в Stas2-графиках, а в Stas3 пока остаются только обычные Stas2 entry-context поля. Следующий возможный шаг: добавить review-only WAVE-context join в Stas3.

## Current State 2026-07-09 STAS2 Short Strong Wave Labels

Текущий статус визуального слоя: `STAS2_SHORT_STRONG_WAVE_LABEL_READY_NO_ML_NO_OPTUNA_VISUAL_ONLY`.

В `WAVE`-строке теперь не теряются проценты у коротких, но сильных волн: если confirmed WAVE короче `15m`, но видимый ход `>= 1%` и длительность `>= 5m`, на квадрате выводится компактная подпись вида `1.34%`.

Актуальный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138`

Открыть:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-12
```

Проверено на `W38 LONG 12:32-12:40`: в CSV `1.336303%`, на PNG теперь есть компактная подпись. ML, Optuna, scorer, target-lock и API не запускались.

## Current State 2026-07-09 STAS2 Continuous Wave Ledger

Текущий статус Stas2-графика: `STAS2_MARKET_PHASE_REVIEW_CONTINUOUS_WAVE_READY_NO_ML_NO_OPTUNA_REVIEW_ONLY`.

Волны больше не привязаны к `day_utc`. Основной источник волн - `STAS2_CONTINUOUS_WAVES.csv`: глобальные `LONG/SHORT/GAP` сегменты с началом, концом, полным процентом и статусом. Дневной overview продолжает быть 24h-картинкой, но строка `WAVE` теперь берет срезы из continuous-ledger и показывает carry через полночь.

Актуальный run для просмотра:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`

Открыть:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-10
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-11
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
```

Что смотреть: на `2026-05-10` в конце дня `W08 SHORT >`, на `2026-05-11` в начале дня `< W08 SHORT`; это одна и та же волна, а не два независимых дневных блока. В таблице это связано общим `continuous_wave_id`.

Проверено: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный run `2026-05-10..2026-05-12`, `openpyxl` load workbook, `80` PNG без пустых файлов.

Граница: continuous-wave - это review/hindsight слой, не входной ML-признак и не TP-логика. ML, Optuna, scorer, target-lock и API не запускались.

## Current State 2026-07-09 STAS2 Macro Wave GAP Segments

Текущий статус Stas2-графика: `STAS2_MARKET_PHASE_REVIEW_WAVE_GAP_SEGMENTS_READY_NO_ML_NO_OPTUNA_REVIEW_ONLY`.

В `src/mlbotnav/visual_entry_stas2_market_phase_review.py` строка `WAVE` теперь показывает не только подтвержденные macro-wave блоки, но и серые `GAP`-сегменты там, где день не покрыт подтвержденной волной. Для `GAP` считается `range_pct` внутри промежутка, подпись выводится прямо в квадрате. Подтвержденные волны не пересчитаны и не переименованы.

Актуальный run для просмотра:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_gap_segments_v1_20260709_073810`

Открыть:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-10
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
```

Проверено: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный run `2026-05-10..2026-05-12`, `openpyxl` load workbook, `80` PNG без пустых файлов.

Граница: `GAP` - это учет/визуализация пропуска, не новая точка входа и не causal ML feature. ML, Optuna, scorer, target-lock и API не запускались.

## Current State 2026-07-09 STAS2 SHORT And Macro Wave Review

Текущий статус Stas2-графика: `STAS2_MARKET_PHASE_REVIEW_SHORT_MACRO_WAVE_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_PLUS_REVIEW_ONLY`.

В `src/mlbotnav/visual_entry_stas2_market_phase_review.py` добавлены:

1. `SHORT` по закрытым часам: `hour_short_wave_*`, движение `high -> subsequent low`.
2. `hour_direction_bias`: `LONG_DOMINANT`, `SHORT_DOMINANT`, `TWO_WAY_VOLATILE`, `FLAT`.
3. `WAVE` по дневным swing-блокам с порогом разворота `1%`: `macro_wave_*`.
4. Новый CSV `STAS2_MACRO_WAVES.csv`, дневные `*_STAS2_MACRO_WAVES.csv`, лист Excel `Macro waves`.
5. Дневной overview теперь рисует `Фон`, `LONG`, `SHORT`, `WAVE`, объем и Stas1-точки без текстового шума возле входов.

Актуальный run для просмотра:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_short_macro_wave_v1_20260709_064759`

Открыть:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-04
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
```

Проверено: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный run `2026-05-04..2026-05-09`, `openpyxl` load workbook, `156` PNG без пустых файлов.

Граница: `WAVE` использует уже сформированный дневной swing и является review/hindsight слоем. Не переносить `macro_wave_*` в causal ML features без отдельной causal-разметки/approved-ledger. ML, Optuna, scorer, target-lock и API не запускались.

## Current State 2026-07-06 STAS3 Percent Ladder Review

Текущий статус: `STAS3_PERCENT_LADDER_REVIEW_READY_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

По новому прямому запросу `Стас3` отдельный Stas3-контур реализован и проверен. Старая пометка о переносе Stas3 в другой чат больше не является текущим состоянием для этого рабочего дерева.

Созданы:

1. `STAS3_PERCENT_LADDER_REVIEW/README_RU.md`;
2. `STAS3_PERCENT_LADDER_REVIEW/run_day.ps1`;
3. `STAS3_PERCENT_LADDER_REVIEW/run_range.ps1`;
4. `STAS3_PERCENT_LADDER_REVIEW/open_last_run.ps1`;
5. `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py`;
6. `tests/test_visual_entry_stas3_percent_ladder_review.py`.

Stas3 читает финальный Stas2 visual-run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535` и считает post-entry percent ladder, фазу рынка на входе, фактическое движение, reasonable TP по фазовому профилю и mismatch к механическому 1% TP.

Финальный контрольный run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260502_20260503_tp_ladder_v0_20260706_183011`

Сводка: `110` Stas2 rows input, `110` entry rows, `0` skipped, row-count parity `True`, полная сетка `0.2..7%`, `110` hit 1% в окне `48h`, `65` строк с reasonable TP, `73` mismatch к механическому 1% TP, `27` noise entry, только `2` быстрых clean, `90` late-pump dependent. Это важный вывод: механический факт `+1% hit` почти весь держится на долгом удержании/позднем пампе и не является чистым positive label.

Ключевые артефакты: `STAS3_ENTRY_PHASE_TABLE.csv`, `STAS3_ACTUAL_MOVEMENT.csv`, `STAS3_REASONABLE_TP.csv`, `STAS3_TP_LADDER_BY_PHASE.csv`, `STAS3_TP_LADDER_BY_PROFILE.csv`, `STAS3_TP_LADDER_V0_RU.md`, `STAS3_PERCENT_LADDER_TABLES.xlsx`.

Последний расширенный Stas3 run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_tp_ladder_v0_20260707_055929`

Источник Stas2: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_setup_quality_v0_20260707_043734`. Диапазон `2026-05-04..2026-05-09`, `417` строк, `0` skipped, row-count parity `True`, `410` hit 1%, `283` reasonable TP, `285` mismatch к 1% TP, `84` noise entry, `13` fast clean, `238` late-pump dependent, `83` PNG.

Актуальный визуальный run с явным выходом на графике:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_tp_exit_overlay_v0_20260707_072226`

На `STAS3_ENTRY_LADDER_PAGE_*.png` теперь видно: entry-треугольник, TP-линия, звезда `EXIT` и подпись времени до TP. Желтый `TP v0` - фазовый TP, серый пунктир `TP 1%` - fallback для строк без рассчитанного фазового TP.

Актуальный исправленный run для проверки глазами:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_signal_entry_exit_overlay_v0_20260707_073915`

На closeup-графиках теперь разделены `SIGNAL` и `ENTRY`: оранжевый `SIGNAL` показывает `anchor_time_utc/anchor_low_price`, голубой `ENTRY` показывает `entry_time_utc/entry_price_5bps`, рядом подписана цена входа. Это исправляет визуальную путаницу, где Stas3 entry выглядел сдвинутым относительно Stas2 low-сигнала.

Актуальный визуальный run после правки TP-отработки:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_signal_entry_tp_move_v0_20260707_080253`

Теперь красная диагональная стрелка `ENTRY -> EXIT` показывает сам ход сделки от цены входа до TP. Желтая горизонталь `TP v0` и серая пунктирная `TP 1%` остаются уровнями цены, а не траекторией движения. Проверка run: `417` строк, `83` PNG, пустых PNG нет, workbook читается.

Актуальный run для анализа больших ходов и обучения удержанию:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_big_move_review_v2_20260707_090246`

Теперь Stas3 дополнительно считает путь `SIGNAL/ENTRY -> MFE MAX`, путь `ENTRY -> 0.2/0.5/1.0%`, остаток движения после ранних TP и review-only корзины выхода. Главная рабочая группа для ручного изучения удержания: `EARLY_1PCT_TRAIL_REVIEW` = `141` сделка. Также зафиксировано `218` `BIG_MFE_BUT_DEEP_MAE_REVIEW` и `51` `LATE_MFE_PUMP_REVIEW`. В run есть `12` страниц `STAS3_BIG_MOVE_REVIEW_PAGE_*.png` с зеленой стрелкой до `MFE MAX`.

Граница: Stas3 является audit/review-слоем после входа. Это анализ и проверка, не торговая стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались и остаются запрещены без отдельного approval.

## Current State 2026-07-06 STAS3 In Separate Chat

Текущий статус: `STAS2_CLOSED_STAS3_IN_SEPARATE_CHAT_NO_ML_NO_OPTUNA`.

Пользователь решил делать Stas3 в другом чате. Здесь активное состояние: Stas2 закрыт, дальнейшая реализация percent ladder / entry-TP validation не начинается.

Следующий чат должен брать Stas2 как готовый источник pre-entry контекста и отдельно строить Stas3. В этом чате не запускать TP/MFE/MAE, ML, Optuna, scorer, target-lock или API без нового прямого запроса.

## Current State 2026-07-06 STAS2 Closed For STAS3

Текущий статус: `STAS2_CLOSED_FOR_STAS3_NO_ML_NO_OPTUNA`.

Stas2 принят пользователем как закрытый этап для перехода к Stas3. Смысл этапа: дать контекст до входа, а не решать TP. На графиках и в таблицах теперь разделены:

1. `Фон` / `background_phase` - общий режим рынка до входа.
2. `LONG` / `long_wave` - наличие направленной волны вверх до входа.
3. `SETUP` / `entry_setup_quality_*` - чистота конкретной точки входа.

Финальный visual-run: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535`.

Финальный audit-run фаз/сессий: `reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942`.

Граница: Stas2 остается pre-entry/no-lookahead слоем. TP, percent ladder сделки, MFE/MAE, time-to-target, drawdown после входа и 5m post-entry blocks начинаются только в Stas3. ML/Optuna/scorer/target-lock/API не запускались и остаются запрещены без отдельного approval.

## Current State 2026-07-06 STAS2 Setup Quality Layer

Текущий статус: `STAS2_MARKET_PHASE_REVIEW_SETUP_QUALITY_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

Stas2 теперь разделяет три понятия:

1. `Фон` / `background_phase` - режим рынка и волатильность окна/часа.
2. `LONG` / `long_wave` - был ли ход вверх до входа.
3. `SETUP` / `entry_setup_quality_*` - качество конкретной точки входа: `CLEAN`, `OK`, `WARN`, `NOISE`.

Это сделано после замечания пользователя по участку `LA045-LA047`: сильная фаза/волна после резкого выноса не должна выглядеть как хорошая точка входа. В новом run эти строки получили `NOISE` в CSV/XLSX, потому что у них есть `anchor_without_clear_wick`, `wide_signal_range` или `low_volume_confirmation`. На дневном overview текстовые названия возле точек убраны, а сами точки входа оставлены как в Stas1.

Контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535`

Сводка: `110` entry rows, `110` Stas1 GOOD, `0` BAD, setup `clean=17`, `working=16`, `warn=50`, `noise=27`, `bad_context_before_entry=0`, `43` PNG, `0` пустых PNG.

Граница сохраняется: Stas2 не считает TP/exit/MFE/MAE, не запускает ML/Optuna/scorer/target-lock/API и использует только pre-entry данные.

## Current State 2026-07-06 STAS2 Background And LONG Wave Visual Fix

Текущий статус: `STAS2_MARKET_PHASE_REVIEW_BG_LONG_WAVE_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

Stas2 visual review теперь разделяет два разных понятия:

1. `background_phase` / `Фон` - общий range/volatility/path часа или pre-entry окна;
2. `long_wave_phase` / `LONG` - ход вверх `low -> subsequent high` внутри этого же часа или окна до входа.

Это исправляет ситуацию, где на overview почти везде было написано `Слабая`, хотя глазами видны рабочие волны вверх. `Слабая` теперь означает слабый общий фон, а не запрет на LONG-движение.

Новый полный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_bg_long_wave_v0_20260706_131201`

Сводка: `110` entry rows, `78` Stas1 GOOD, `32` Stas1 BAD, `43` PNG, `0` пустых PNG, `bad_context_before_entry=0`, Excel читается, CSV BOM `EF-BB-BF`, `pre15_long_wave_min_max=(0.023728, 0.687611)`.

Граница сохраняется: Stas2 pre-entry only. Stas1 не изменен. TP/exit/percent ladder/MFE/MAE/5m post-entry blocks - только Stas3. ML/Optuna/scorer/target-lock/API не запускались.

## Current State 2026-07-06 STAS2 Market Phase Visual Review

Текущий статус: `STAS2_MARKET_PHASE_REVIEW_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

Stas2 теперь оформлен как отдельный визуальный контур, не ломающий Stas1:

1. `STAS2_MARKET_PHASE_REVIEW/README_RU.md`;
2. `STAS2_MARKET_PHASE_REVIEW/run_day.ps1`;
3. `STAS2_MARKET_PHASE_REVIEW/run_range.ps1`;
4. `STAS2_MARKET_PHASE_REVIEW/open_last_run.ps1`;
5. `src/mlbotnav/visual_entry_stas2_market_phase_review.py`.

Что рисуется:

1. дневной overview с фоном UTC-сессий, phase strip и Stas1 входами;
2. entry context pages, где окно обрезано до `entry_time_utc`, без свечей после входа;
3. `BROWSE_BY_DAY/` по образцу Stas1;
4. Excel/CSV/JSON/RU-report.

Контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_market_phase_review_v0_20260706_124134`

Проверено: `110` entry rows, `78` Stas1 GOOD, `32` Stas1 BAD, `bad_context_before_entry=0`, `43` PNG без пустых файлов, Excel читается через `openpyxl`, CSV пишется с BOM `EF-BB-BF`, хвостов `python.exe` нет.

Граница: Stas2 только pre-entry context. TP/exit/percent ladder/MFE/MAE/5m post-entry blocks - только Stas3. ML/Optuna/scorer/target-lock/API не запускались.

## Current State 2026-07-06 STAS2 Excel Encoding Fix

Текущий статус: `STAS2_EXCEL_EXPORT_UTF8_BOM_XLSX_READY_NO_ML_NO_OPTUNA`.

Исправлен Stas 2 export для Excel:

1. CSV теперь пишутся как `utf-8-sig`, чтобы Excel не ломал русский текст в кракозябры.
2. Пустые summary CSV больше не создаются как файл на 2 байта: даже если строк нет, пишутся заголовки.
3. Для ручного просмотра в Excel добавлен нативный workbook `STAS2_MARKET_PHASE_TABLES.xlsx` с листами `Hourly phases`, `Session buckets`, `Effective sessions`, `Weekday sessions`, `Weekend buckets`, `Weekday weekend`, `Entry context`.

Проверочный run по `2026-05-02..2026-05-03`:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260503_excel_xlsx_fix_20260706_112616`

Главный Excel-файл:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260503_excel_xlsx_fix_20260706_112616/STAS2_MARKET_PHASE_TABLES.xlsx`

Проверки: `py_compile`, run audit, load workbook через `openpyxl`, проверка BOM `EF-BB-BF` у всех CSV. ML/Optuna/scorer/target-lock/API не запускались.

## Current State 2026-07-06 STAS2 Market Phase Session Audit

Текущий статус: `STAS2_MARKET_PHASE_SESSION_AUDIT_READY_NO_ML_NO_OPTUNA`.

Создан отдельный Stas 2 audit-скрипт:

`src/mlbotnav/visual_entry_stas2_market_phase_audit.py`

Он читает OHLCV `SOLUSDT 1m`, актуальные Stas1 CSV и считает:

1. фазы рынка по часам;
2. `6` внутридневных UTC-корзин `session_time_bucket`: `Азия/Pacific time`, `Перед Лондоном`, `Лондон без Нью-Йорка`, `Пересечение Лондон/Нью-Йорк`, `Нью-Йорк без Лондона`, `После Нью-Йорка/слабые часы`;
3. сравнение weekday/weekend;
4. `effective_session = day_type + session_time_bucket`, чтобы выходные окна не смешивались с настоящими будними сессиями;
5. `phase_before_entry` для Stas1 входов только по предыдущим 60 минутам, без свечей после входа;
6. heatmap PNG.

Финальные артефакты:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942`

Главный отчет:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942/STAS2_MARKET_PHASE_AUDIT_RU.md`

Проверки:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas2_market_phase_audit.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_audit --start-day 2026-05-02 --end-day 2026-05-08 --run-label stas2_20260502_20260508_session6_daytype_v4 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260503_all_closeups_bad_x_v0_20260706_060244 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260504_20260506_browse_by_day_v0_20260706_063954 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260507_20260508_carry48_v0_20260706_084057
```

Граница: отчетный слой, не ML/export/training, не Optuna, не scorer, не target-lock и не API.

## Current State 2026-07-06 STAS1 Block 1 Locked

Текущий статус: `STAS1_BLOCK_1_RUN_POOL_LOCKED_NO_ML_NO_OPTUNA`.

Блок 1 STAS1 зафиксирован как рабочий baseline. Он умеет запускать прогон по дню/диапазону, собирать все low-кандидаты входа, сохранять PNG/CSV/JSON/отчет и раскладывать просмотр через `BROWSE_BY_DAY/`.

Процент движения цены уже управляемый:

1. `run_day_1pct.ps1` - проверка `+1%`;
2. `run_day_0p5.ps1` - проверка `+0.5%`;
3. Python-ядро поддерживает `--target-pct` для других порогов;
4. `-OutcomeLookaheadHours` разрешает проверять закрытие после полуночи.

Вывод: этот блок больше не пересобирать заново. Следующий этап - ручная чистка шума, фиксация feedback и доработка фильтра значимого low.

## Current State 2026-07-06 STAS1 Carry Outcome

Текущий статус: `STAS1_CARRY_OUTCOME_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

STAS1 поддерживает перенос проверки цели через ночь. Кандидаты входа создаются только внутри выбранного диапазона `-Day .. -EndDay`, но outcome можно проверять дальше через `-OutcomeLookaheadHours`.

Контракт:

1. не подтягивать старые сделки до `-Day`;
2. не создавать новые входы после `-EndDay`;
3. future-свечи использовать только для offline outcome label;
4. запись остается в дне входа, даже если `+1%` достигнут на следующем дне.

Smoke-run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_smoke_carry48_20260507_20260508_v0_20260706_081637`.

Сводка: `148` кандидатов, `80` `GOOD_SAME_DAY`, `68` `GOOD_CARRIED_OVERNIGHT`, `0` missing outcome sources.

Команда проверки:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-07 -EndDay 2026-05-08 -OutcomeLookaheadHours 48 -RunLabel stas1_20260507_20260508_carry48_v0 -RenderGoodLimit 0
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
```

## Current State 2026-07-06 STAS1 Browse By Day

Текущий статус: `STAS1_BROWSE_BY_DAY_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

STAS1 теперь создает в каждом run папку `BROWSE_BY_DAY/`, чтобы пользователь не открывал десятки окон. Внутри есть `00_RUN_INDEX.png`, затем папки дней. В каждой папке дня файлы идут по порядку просмотра: `00_YYYYMMDD_OVERVIEW.png`, затем `01/02/..._ALL_CLOSEUPS_PAGE_*.png` строго по `entry_time_utc`.

Рабочий run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260504_20260506_browse_by_day_v0_20260706_063954`.

Сводка: `3` дня, `202` кандидата, `98` GOOD, `104` BAD. Дни: `2026-05-04`, `2026-05-05`, `2026-05-06`.

Команды просмотра:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open index
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-04
```

## Current State 2026-07-06 STAS1 ALL Closeups GOOD+BAD

Текущий статус: `STAS1_ALL_CLOSEUPS_BAD_X_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

В STAS1 добавлен отдельный слой `ALL closeups`: теперь можно смотреть GOOD и BAD кандидаты вместе. GOOD рисуется зеленым треугольником, BAD - красным полупрозрачным крестом. Это нужно для ручной чистки шума и будущих negative-label примеров, но не является ML/export/training/scorer/target-lock/Optuna/API.

Контрольный run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260503_all_closeups_bad_x_v0_20260706_060244`.

Сводка `2026-05-03`: `58` кандидатов, `36` GOOD, `22` BAD, `8` страниц `GOOD_1PCT_REVIEW_POOL_ALL_CLOSEUPS_PAGE_*.png`.

Открыть последние ALL closeups:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open allcloseups
```

## Current State 2026-07-03 STAS1 Good Low Review

Текущий статус: `STAS1_V0_BASELINE_MAIN_LOW_REVIEW_SCRIPT_NO_ML_NO_OPTUNA`.

Пользователь зафиксировал рабочее решение: основной скрипт для ближайшей ручной калибровки low-кандидатов - `src/mlbotnav/visual_entry_good_1pct_review_pool.py`. Не создавать новый скрипт с нуля и не откатываться вслепую.

Создана видная папка `STAS1_GOOD_LOW_REVIEW/` с README и PowerShell-командами:

1. `run_day_1pct.ps1`;
2. `run_day_0p5.ps1`;
3. `open_last_run.ps1`.

Новые runs будут сохраняться в `STAS1_GOOD_LOW_REVIEW/runs/`, ручной feedback - в `STAS1_GOOD_LOW_REVIEW/feedback/`, слепки рабочих версий - в `STAS1_GOOD_LOW_REVIEW/snapshots/`.

Следующий рабочий смысл: пользователь смотрит один день, затем 3-4 дня, отмечает шум/дубли/сдвиги, а затем калибруется `src/mlbotnav/visual_entry_low_anchor_suggester.py`. `+1%`/`+0.5%` остаются offline outcome label, не ML label и не feature.

## Current State 2026-07-02 Bybit Hedge Mode Note

Текущий статус: `HEDGE_MODE_API_NOTE_LOCKED_FUTURE_HEDGE_SIM_NO_REAL_API`.

Запомнено как отдельная risk-идея: Bybit V5 hedge/both-sides mode для `linear` USDT perpetual дает возможность держать LONG и SHORT одновременно по одному символу. В API это различается через `positionIdx`: `1` для long-side, `2` для short-side.

Это не меняет текущий следующий этап. Сначала остается `DCA_RISK_AUDIT_V0` на `W18-W20`: DCA-корзины, просадки, число одновременных входов, маржа и классы риска. Только после этого можно делать `HEDGE_SIM_V0` как симуляцию защиты, без реальных ордеров и без API-ключей.

Граница: hedge не является entry-сигналом, ML-фичей, scorer, Optuna или target-lock. Реальные Bybit API действия запрещены без отдельного явного решения пользователя.

## Current State 2026-07-02 Daily 10 Long Trades Phase Ladder

Текущий статус: `DAILY_10_LONG_TRADES_PHASE_LADDER_LOCKED_FOR_DCA_AUDIT_NO_ML_NO_OPTUNA`.

Пользователь уточнил дневную цель: не просто `+1%` как единственный target, а изучить фазы движения по рынку, дню и сессии. Рабочая лестница фаз:

- `0.3-0.5%` - короткая scalp-фаза;
- `0.9-1.0%` - базовая дневная фаза для одной сделки;
- `1.5-2.0%` - расширенная фаза;
- `2.2-4.0%+` - сильный импульс/трендовый день.

Цель `10` сделок в день теперь трактуется как верхний план/лимит качественных long-входов, а не обязанность добирать любые входы до `10`. Если день дает только `1-3` качественных входа, это отдельный режим дня, а не повод брать мусор.

Следующий `DCA_RISK_AUDIT_V0` должен считать фазовую разметку как offline outcome: достигнутая фаза, время до фазы, просадка до фазы, число открытых сделок, session/day context. Это не ML, не scorer и не Optuna.

## Current State 2026-07-02 DCA Risk And Knife Map Rails

Текущий статус: `SHORT_RANGE_DCA_RISK_RAILS_LOCKED_NO_ML_NO_OPTUNA`.

Зафиксировано решение пользователя: не переходить сразу на полный `126`-дневный прогон. Сначала доводим механику на коротком учебном диапазоне `W18-W20`, то есть `2026-04-27..2026-05-17` (`21` день), run `W18_W20_learning_20260702_082819`.

Причина: текущий `+1% review-pool` быстро находит много кандидатов, но среди них есть ножи, перегруженные DCA-кластеры и слабые `SOFT` входы. Если передать такие строки в ML как простой `GOOD`, модель научится покупать падающий нож.

Два направления зафиксированы так:

1. `DCA_RISK_AUDIT_V0` - текущий следующий этап на `21` дне. Он должен группировать входы в DCA-корзины, считать просадку, число докупок, среднюю цену, время в минусе, поддержку при `10x/20x/50x/100x` и присваивать risk-aware классы.
2. `FULL_HISTORY_KNIFE_MAP_V0` - отложенный этап на все доступные `126` дней. Запускать только после того, как на `21` дне понятны классы, кластеры, визуальные PNG, баги и ручная логика review.

Рабочие классы для следующего слоя:

- `GOOD_CLEAN_RECLAIM` - чистый low/reclaim, малая просадка, мало докупок.
- `GOOD_DCA_SURVIVABLE` - вход можно пережить как DCA-корзину с понятным запасом.
- `BORDERLINE_SOFT` - математически слабый плюс, обычно только при идеальном исполнении.
- `BAD_FALLING_KNIFE` - цена продолжила падать после входа, опасный нож.
- `BAD_CLUSTER_OVERLOAD` - слишком много докупок подряд, маржа раздувается.
- `BAD_NO_ROOM` - нет нормального хода/пространства до цели.
- `REJECT_VISUAL` - руками отклонено после просмотра.

Граница: `+1% hit` остается только review/outcome-слоем. Это не gold-разметка, не ML dataset, не scorer, не target-lock и не Optuna.

## Current State 2026-07-02 Low Anchor Entry 1pct Label Review V1 13 May

Текущий статус: `LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

По `SOLUSDT 1m 2026-05-13` построен правильный full-day review после пользовательской правки:

1. `signal_time_utc` = свеча значимого low;
2. `entry_time_utc` = следующая свеча;
3. рабочая execution-цена для графика = `entry_open + 5bps`;
4. offline target = `entry_price * 1.01`;
5. погрешность для обучения живет только в execution/slippage band `0bps/5bps/10bps`, а не во времени входа.

Итог: `87` кандидатов, `4` дошли до `+1%` даже при `10bps`, `0` только при `5bps`, `1` только при `0bps`, `82` не дошли даже при `0bps`.

Артефакты лежат в:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/`.

Главные PNG:

1. `LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_FULL_DAY_20260513.png`;
2. `LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_ZOOM_PAGE_01_20260513.png`.

Граница: это review/dataset-label слой. Outcome `+1%` используется только после causal low-кандидата как label/audit, не как feature выбора входа. Scorer, target-lock, Optuna и ML/export/training не запускать.

## Current State 2026-07-02 Low Anchor 1pct Label Review 13 May

Текущий статус: `LOW_ANCHOR_1PCT_LABEL_REVIEW_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

По `SOLUSDT 1m 2026-05-13` построен full-day review: значимый low-anchor кандидат -> entry next open + 5 bps -> offline label по цели `anchor_low_price * 1.01`.

Итог: `87` кандидатов, из них `8` дошли до `+1%` от low после entry, `79` не дошли.

Артефакты лежат в:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_1pct_label_review_v0_20260513/`.

Граница: outcome `+1%` является только label/audit, не feature выбора входа. Следующий шаг - пользовательский visual review зеленых/красных точек и возможная ручная правка.

## Current State 2026-07-02 Low Anchor Suggester 13 May

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260513_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

`visual_entry_low_anchor_suggester.py` применен к `SOLUSDT 1m 2026-05-13`. Скрипт обновлен так, чтобы:

1. имена артефактов строились по `--day`;
2. отсутствие ручного target-ledger не ломало прогон;
3. при отсутствии ручных целей строился zoom-sheet по top low-anchor candidates;
4. в CSV/JSON фиксировались `entry_price_plus_5bps` и `target_1pct_price`.

Результат: полный слой `87` кандидатов, strict-слой `18` кандидатов при `min_score=5.0`.

Граница: это только candidate review для глаз. Не gold-разметка, не scorer, не target-lock, не Optuna, не ML/export/training.

## Current State 2026-07-02 Target 1pct Price Fix V0

Текущий статус: `TARGET_1PCT_PRICE_FIX_V0_READY_NO_ML_NO_OPTUNA_NO_SCORER`.

По ручным эталонам `2026-05-14 M01..M19` и `2026-05-15 T15L confirmed 7` зафиксированы цены `+1%` от `entry + 5bps`.

Итог: всего `26` входов; `2026-05-14` дошли до `+1%` `13/19`; `2026-05-15` дошли до `+1%` `4/7`.

Артефакты лежат в:
`reports/final_review/visual_entry_v3/fresh_target_led/target_1pct_price_fix_v0/`.

Граница: это outcome/reference-слой, не ML, не scorer, не Optuna и не target-lock. Следующий рабочий шаг должен идти по рельсам поверх ручных эталонов и паспортных блоков, без cooldown-перебора.

## Current State 2026-07-01 Target-Led Dataset Base V0

Текущий статус: `TARGET_LED_DATASET_BASE_V0_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA`.

Собрана единая база по 14 и 15 мая:

1. `26` good entries;
2. `66` rejected bad entries;
3. `15` unlabeled review entries;
4. всего `107` строк.

Будущие supervised labels есть только для good/reject: `92` строки. `possible_entry` и `manual_shift_review` оставлены без `ml_label`, чтобы не загрязнять обучение.

Каждая строка содержит causal-фичи на закрытой signal-свече: price/range/room/wick/volume/VPOC/VWAP/RSI/MACD/ADX/Stoch/Fibo/retest/BOS/pattern primitives. Entry open и `+5 bps` сохранены только как execution/control.

Следующий рабочий подпункт: user review dataset summary, затем решить, нужно ли переносить выбранные core blocks на `2026-05-15` strategy overlay или сначала чистить `unlabeled_review`. ML/export/training запрещены без `APPROVED_FOR_ML`.

## Current State 2026-07-01 B018 BOS Repeat 14 May

Текущий статус: `B018_BOS_STRATEGY_REVIEW_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

BOS/CHOCH повторен отдельно по `SOLUSDT 1m 2026-05-14 M01..M19`.

Итог: `BOS_UP=41`, `BOS_DOWN=42`, `CHOCH-like=8`. Это подтверждает прежний вывод V2E: `B018` широкий и шумный как самостоятельный фильтр. Рабочая роль `B018` — structure-context/evidence.

Практическая интерпретация для лонга: искать не просто BOS, а сценарий `слом вниз -> reclaim/CHOCH -> локальный вход`, либо использовать `BOS_UP` как подтверждение продолжения после входа.

Следующий рабочий подпункт: user review BOS PNG, затем вернуться к выбору первого кластера/паспорта-кандидата из V2E. Scorer, target-lock, Optuna и ML/export/promotion запрещены.

## Current State 2026-07-01 V2E Summary Matrix 14 May

Текущий статус: `V2E_SUMMARY_MATRIX_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

14 мая закрыт по слоям `V2A/V2B/V2C/V2D` и сведен в `V2E_SUMMARY_MATRIX`.

Итог по блокам:

1. Слишком широкие context-блоки: `B014`, `B018`, `B009`, `B021`, `B022`, `B023`.
2. Evidence-кандидаты: `B015`, `B017`, `B010`, `B013`, `B019`, `B020`.
3. Конфликтный блок: `B026` с conflict `8/19`.

Следующий рабочий подпункт: user review V2E-скрина, затем выбрать первый кластер/паспорт-кандидат по 14 мая. Не переходить к scorer, target-lock, Optuna или ML/export/promotion без отдельного решения пользователя.

## Current State 2026-07-01 V2D Pattern 14 May

Текущий статус: `V2D_PATTERN_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

На 14 мая уже закрыто:

1. `V2A_STRUCTURE_LAYER`: `B014`, `B015`, `B017`, `B018`;
2. `V2B_FLOW_DENSITY_LAYER`: `B010`, `B013`, `B026`;
3. `V2C_ADX_STOCH_LAYER`: `B008`, `B009`;
4. `V2D_PATTERN_LAYER`: `B019`, `B020`, `B021`, `B022`, `B023`, `B024`.

V2D результат: `B019` поддержал `15/19`, `B020` поддержал `9/19`, `B021` и `B022` поддержали `19/19`, `B023` поддержал `17/19`, `B024` поддержал `16/19`. Интерпретация: pattern-слой полезен как evidence, но часть блоков слишком широкая и не является самостоятельным entry-фильтром.

Следующий рабочий подпункт: `V2E_SUMMARY_MATRIX` на 14 мая. Нужно свести `M01..M19` по слоям `V2A/V2B/V2C/V2D` и отдельно отметить, какие блоки являются контекстом, а какие потенциально могут попасть в паспорт. Scorer, target-lock, Optuna и ML/export/promotion запрещены.

## Current State 2026-07-01 V2C ADX/Stochastic 14 May

Текущий статус: `V2C_ADX_STOCH_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

На 14 мая уже закрыто:

1. `V2A_STRUCTURE_LAYER`: `B014`, `B015`, `B017`, `B018`;
2. `V2B_FLOW_DENSITY_LAYER`: `B010`, `B013`, `B026`;
3. `V2C_ADX_STOCH_LAYER`: `B008`, `B009`.

RSI/MACD/EMA не повторялись по пользовательской правке. Текущий аудит: `B008_ADX14` поддержал `16/19`, `B009_STOCH14` поддержал `19/19`. Это означает, что Stochastic в текущей визуальной трактовке слишком широкий; ADX является контекстом силы движения, а не направлением входа.

Следующий рабочий подпункт после user review: `V2D_PATTERN_LAYER` на 14 мая (`B019-B024`). `B025` оставить unsafe/context-only без отдельного решения. Scorer, target-lock, Optuna и ML/export/promotion запрещены.

## Current State 2026-07-01 V2B Flow/Density 14 May

Текущий статус: `V2B_FLOW_DENSITY_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Рабочая поправка: `T15/2026-05-15` отложен. Сначала закрываем `SOLUSDT 1m 2026-05-14 M01..M19` по всем применимым паспортным слоям.

Уже закрыто по 14 мая:

1. `V2A_STRUCTURE_LAYER`: `B014`, `B015`, `B017`, `B018`;
2. `V2B_FLOW_DENSITY_LAYER`: `B010`, `B013`, `B026`.

V2B результат: `B010_VOLUME_FLOW` поддержал `13/19`, `B013_DENSITY_VPOC` поддержал `12/19`, `B026_VWAP_DISTANCE` поддержал `8/19` и часто конфликтует. Интерпретация: это evidence/context, не самостоятельный сигнал.

Следующий рабочий подпункт: `V2C_MOMENTUM_LAYER` на 14 мая (`B006 RSI`, `B007 MACD`). `B005 EMA` пока не используем как active condition. Scorer, target-lock, Optuna и ML/export/promotion запрещены.

## Current State 2026-07-01 V2A Structure User Review Audit

Текущий статус: `V2A_STRUCTURE_20260514_VISUAL_AUDIT_DONE_NO_SCORER_NO_ML_NO_OPTUNA`.

Закрыт короткий visual-аудит V2A по `SOLUSDT 1m 2026-05-14 M01..M19`.

Audit:
`reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_USER_REVIEW_AUDIT_20260701_RU.md`.

Рабочее решение: `B014/B018` считать широким контекстом, `B017` оставить кандидатом для retest/reclaim evidence, `B015 Fibo` оставить `context_only` до правила свежести ноги. Эта строка про следующий переход на `2026-05-15` superseded: сначала закрываем `V2B/V2C/V2D/V2E` по 14 мая. Scorer/target-lock/Optuna/ML запрещены.

## Current State 2026-07-01 V2A Structure Overlay 14 May

Текущий статус: `V2A_STRUCTURE_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Собран первый passport/strategy overlay для `SOLUSDT 1m 2026-05-14` по ручным входам `M01..M19`.

Скрипт:
`src/mlbotnav/visual_entry_strategy_passport_overlay_v2a.py`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_FULL_DAY_20260514.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_01_20260514.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_02_20260514.png`.

JSON/CSV/RU:
`reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514.json`;
`reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514.csv`;
`reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514_RU.md`.

Наложенные блоки: `B014 LEVEL/RANGE/CHANNEL`, `B015 FIBONACCI_GRID`, `B017 BREAKOUT_RETEST`, `B018 MARKET_STRUCTURE`. `B016` не active, только muted/context-only позже.

Следующий шаг superseded пользовательской правкой: не идти на `2026-05-15`, пока 14 мая не закрыт по всем паспортным слоям. Scorer, target-lock, Optuna и ML не запускать.

## Current State 2026-07-01 Existing Passport Reconciliation

Текущий статус: `ACTIVE_EXISTING_PASSPORT_RECONCILIATION_AND_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA`.

Новый верхний рельс уточнен пользователем: паспорта уже собраны, сейчас нужна сверка существующих связок и strategy/passport overlay на два эталона `M01..M19` и 7 T15 входов. Full-day график остается картой дня, но каждая стратегия проверяется локальным участком внутри дня.

Агент `Lorentz` подтвердил read-only аудит: `26` блоков `B001..B026`, `82` активных не отключенных `Fxxx`, `82` активных matrix YAML, все активные `passport_path` и `active_matrix_path` существуют. `B001_RET_N_TOURNAMENT` отключен как diagnostic.

Главный документ:
`docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_STRATEGY_PASSPORT_ROADMAP_RU.md`.

Manifest-сверка:
`docs/CALIBRATION_NODE_CURRENT/PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md`.

Следующий шаг: `V2A_STRUCTURE_LAYER` по блокам `B014/B015/B017/B018`; `B016` только muted/context-only. После user review идти в `V2B_FLOW_DENSITY_LAYER`, затем `V2C_MOMENTUM_LAYER`, `V2D_PATTERN_LAYER`, `V2E_SUMMARY_MATRIX`.

Scorer, target-lock, Optuna и ML не запускать.

## Current State 2026-07-01 Git Remote Push MLbotNav

Текущий статус: `GIT_REMOTE_PUSH_DONE_MAIN_TRACKS_ORIGIN_MAIN`.

Git для проекта полностью включен: локальная ветка `main` отслеживает `origin/main`, remote `origin` указывает на `https://github.com/Stanislav1567/MLbotNav.git`.

Последний коммит: `e178c49 Initial commit`, уже на GitHub. Рабочая копия после push была чистой.

## Current State 2026-07-01 Git Init MLbotNav

Текущий статус: `SUPERSEDED_BY_GIT_REMOTE_PUSH_DONE`.

Локальный Git-репозиторий создан, активная ветка `main`. Первый коммит пока не сделан, потому что в Git не настроены `user.name`/`user.email`, а remote URL еще не задан.

Подготовлено к первому коммиту: source/config/docs/tests/scripts, `646` staged-файлов, около `11.12 MB`. Исключено из Git: `.env`, `.venv`, `.vscode`, `data/`, `models/`, `reports/`, `logs/`, `packs/`, `tmp/`, `_codex_offload_*`, `_locked_tmp_*`, backup-файлы `*.bak`, `*.bak_*`, `*.bak-*`. Добавлен `.gitattributes`, чтобы стабилизировать окончания строк.

## Current State 2026-07-01 Strategy Passport Gap Audit

Текущий статус: `STRATEGY_PASSPORT_GAP_AUDIT_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь принял визуальный V1 evidence layer по `19+7`, но указал, что на скрине не видны созданные стратегии/паспорта: `swing`, `BOS`, `Fibonacci` и т.д.

Вывод аудита: V1 показывает индикаторные панели и простые подсказки, но не исполняет строгие паспорта `F012-F052` как `ALLOW 1/0`. Не хватает strategy/passport overlay и матрицы `target_id -> какие паспорта поддержали вход`.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_STRATEGY_PASSPORT_GAP_AUDIT_20260701_RU.md`.

Следующий шаг: собрать `INDICATOR_HYPOTHESIS_REVIEW_V2_STRATEGY_PASSPORT_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA` по тем же ручным входам `M01..M19` и 7 T15.

## Current State 2026-07-01 Codex Agent Launch Kit MLbotNav

Текущий статус: `CODEX_AGENT_LAUNCH_KIT_MLBOTNAV_READY_NO_PROJECT_CODE_CHANGE`.

Для запуска нового агента именно в проекте `MLbotNav` использовать:

```powershell
C:\Users\007\Desktop\Codex Agent\Start MLbotNav Codex Agent.cmd
```

Для продолжения последней Codex-сессии с рабочей папкой `MLbotNav` использовать:

```powershell
C:\Users\007\Desktop\Codex Agent\Resume MLbotNav Codex Agent.cmd
```

Проверено: `codex-cli 0.142.5`, `codex login status` = вход через ChatGPT, проект есть в trusted-конфиге. `codex doctor` завершился без fail: авторизация, сеть, WebSocket, Git и конфиг в порядке. Остались предупреждения про старые записи истории Codex и отсутствие `.git` в проекте.

## Current State 2026-07-01 Indicator/Hypothesis Review V1 19+7

Текущий статус: `INDICATOR_HYPOTHESIS_REVIEW_V1_M01_M19_T15V1_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь поправил порядок: перед паспортом нужен отдельный feature/evidence слой по двум эталонам, а не переход сразу к passport. Создан `indicator_hypothesis_review_v1`.

Состав: `19` входов `M01..M19` за `2026-05-14` и `7` входов `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16` за `2026-05-15` из `draft_ledger_v1`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_M01_M19_20260514.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_T15_7_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_ZOOM_T15_7_20260515.png`.

Следующий шаг: показать пользователю V1 и получить `норм/фиксить`. Passport C01 отложен до review этого второго слоя. Scorer, target-lock, Optuna и ML/export запрещены.

## Current State 2026-07-01 T15 Draft Ledger V1 Confirmed

Текущий статус: `T15_DRAFT_LEDGER_V1_USER_CONFIRMED_NEXT_PASSPORT_C01_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь сказал `норм` по `draft_ledger_v1`. Старый `draft_ledger_v0` не использовать.

Рабочие 7 входов: `T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Следующий шаг по рельсам: собрать черновой паспорт-контракт только для `T15_C01_SUPPORT_RETEST_LOW` (`T15L02`, `T15L08`, `T15L16`) и показать PNG/таблицу пользователю. Scorer, target-lock, Optuna и ML/export запрещены.

## Current State 2026-07-01 T15 Draft Ledger V1 Red Arrow Fix

Текущий статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_RED_ARROW_FIX_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Актуальный рабочий слой T15 draft-ledger теперь `draft_ledger_v1`, потому что пользователь поправил три входа красными стрелками:

- `T15L02`: entry `02:35` -> `02:34`;
- `T15L07`: entry `06:23` -> `06:21`;
- `T15L08`: entry `08:32` -> `08:31`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.png`.

RU report:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701_RU.md`.

`draft_ledger_v0` больше не использовать для паспорта. Следующий шаг: дождаться `норм / фиксить` по v1.

## Current State 2026-07-01 T15 Draft Ledger / Cluster Discussion V0

Текущий статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Собран рабочий draft-ledger по 7 входам `SOLUSDT 1m 2026-05-15` из `T15_USER_VERDICT_V1`:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Разложение:

- `T15_C01_SUPPORT_RETEST_LOW`: `3` входа, `T15L02/T15L08/T15L16`; первый кандидат на паспортный разбор.
- `T15_C02_DEEP_CAPITULATION_LOW`: `2` входа, `T15L06/T15L13`; отдельный deep-кластер.
- `T15_C03_HOT_RECLAIM_CONTINUATION`: `2` входа, `T15L07/T15L11`; пока observe-only, не смешивать в первый паспорт.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.png`.

RU report:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701_RU.md`.

Граница: это не target-lock, не scorer, не ML dataset и не Optuna. `entry_open_price` и `entry + 5 bps` только execution/control. Следующий шаг: пользователь смотрит скрин и говорит `норм` или что фиксить.

## Current State 2026-07-01 T15 User Verdict V1

Текущий статус: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: “тут 7 должно входов”. Предыдущий `user_verdict_v0` больше не использовать как рабочий слой.

Актуально подтверждены 7 входов:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.json`.

Следующий шаг: draft-ledger/cluster discussion по всем 7 confirmed entries, без target-lock/scorer/ML/Optuna.

## Current State 2026-07-01 Indicator/Hypothesis Visual Review V0

Текущий статус: `INDICATOR_HYPOTHESIS_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Создан визуальный пакет для проверки гипотез по `SOLUSDT 1m` на `2026-05-14` и `2026-05-15`: price/volume, RSI14, MACD, density, trailing swing, BOS и Fibo на zoom. Это сделано как “лестница для глаз”, а не как scorer.

Состав: `19` manual gold на `2026-05-14`, `15` rejected на `2026-05-15`, `7` pending на `2026-05-15`.

Основные PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260514.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_PENDING_ZOOM_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_20260701.json`.

Следующий шаг: пользователь смотрит visual evidence и дает verdict по инструментам и 7 pending. ML/export/Optuna запрещены.

Ассистентский verdict:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_ASSISTANT_VERDICT_20260701_RU.md`.

Итог: RSI/MACD/volume/Fibo не являются готовым правилом. Нужна структура сначала: значимый low/reclaim, не микролой в шуме, room/path до плотной зоны, затем volume/RSI как подтверждение. Приоритет для следующего zoom: `T15L06`, `T15L13`, `T15L16`.

## Current State 2026-07-01 T15 Priority Zoom Review V0

Текущий статус: `T15_PRIORITY_ZOOM_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Создан priority zoom-review по `T15L06`, `T15L13`, `T15L16`.

Sheet PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_SHEET_20260515.png`.

Ассистентский verdict:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_ASSISTANT_VERDICT_20260701_RU.md`.

Итог: `T15L06` и `T15L16` выглядят как основные gold-кандидаты для пользовательского подтверждения. `T15L13` оставить possible, но не делать ядром паспорта.

## Current State 2026-07-01 T15 User Verdict V0

Текущий статус: `T15_USER_VERDICT_V0_FIXED_NO_ML_NO_OPTUNA` superseded.

Пользователь ответил “норм” после priority zoom. Зафиксировано:

- `T15L06`, `T15L16`: `gold_candidate_user_confirmed`;
- `T15L13`: `possible_not_primary`;
- `T15L02`, `T15L07`, `T15L08`, `T15L11`: `weak_not_promoted_after_priority_review`;
- feedback v2 rejected сохраняются как `bad_noise`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_20260701.json`.

Этот слой больше не использовать как рабочий: пользователь уточнил, что входов должно быть `7`. Рабочий слой: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

## Current State 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V2

Текущий статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V2_FIXED_NO_ML_NO_OPTUNA`.

Актуальный feedback по `T15L01..T15L22`: `15` rejected, `7` pending. Пользователь уточнил, что `T15L10` тоже крест.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L10`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Feedback PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json`.

Следующий шаг: разобрать 7 pending отдельно. Pending не gold, ML/export/Optuna запрещены.

## Current State 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V1

Текущий статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V1_FIXED_NO_ML_NO_OPTUNA`.

Актуальный feedback по `T15L01..T15L22`: `14` rejected, `8` pending. Пользователь дополнительным full-day screenshot показал, что `T15L21` тоже rejected.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`.

Feedback PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json`.

Следующий шаг: разобрать 8 pending отдельно. Pending не gold, ML/export/Optuna запрещены.

## Current State 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V0

Текущий статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь разметил screenshots по `T15L01..T15L22`: красные X/перечеркивания означают `не подходит`.

Итог: `13` rejected, `9` pending.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`, `T15L21`.

Feedback PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json`.

Следующий шаг: разобрать pending-кандидаты отдельно и не считать их gold без явного `норм`/`сдвинуть`. ML/export/Optuna запрещены.

## Current State 2026-07-01 Low Anchor Transfer Review 2026-05-15 Compact V0

Текущий статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_DAY_20260515_READY_NO_ML_NO_OPTUNA`.

Сделан новый out-of-sample visual transfer review для `SOLUSDT 1m 2026-05-15`: проверяем, переносится ли понимание ручных входов `M01..M19` с `2026-05-14` на соседний день.

Итог: broad-кандидатов `89`, compact review-кандидатов `22`, zoom-страниц `2`.

Активный пакет:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/`.

Главный full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_FULL_DAY_20260515.png`.

Zoom pages:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_01_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_02_20260515.png`.

Все `T15L##` пока `pending_user_visual_review`. Нельзя использовать как labels, scorer, ML dataset или Optuna objective. EMA не active condition.

## Current State 2026-07-01 Feature Policy EMA Deferred

Текущий статус: `LOW_ANCHOR_FEATURE_POLICY_EMA_DEFERRED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: EMA пока не трогаем. Следующие шаблоны/passport/checklist делаем без EMA как условия входа.

Правило дальше:

- EMA-колонки из audit остаются справочными;
- активные шаблоны строить через структуру движения, положение в диапазоне, low/reclaim, volume/range/wick closed signal candle;
- не добавлять EMA-фильтр в scorer/checklist без отдельного решения пользователя.

## Current State 2026-07-01 Low Anchor No-Lookahead Feature Audit V0

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_READY_NO_ML_NO_OPTUNA`.

Создан no-lookahead feature audit по `85` записям: `19 manual_gold`, `51 bad_noise`, `12 manual_shift_review`, `3 possible_entry`.

Audit использует только закрытую `signal`-свечу и прошлый контекст. Entry-candle OHLCV, future return, TP/SL, MFE/MAE не используются.

Главный вывод: локальный low сам по себе не является входом. Для будущего scorer/passport нужны фильтры контекста до entry: структура движения без EMA, положение в диапазоне, room до recent high, сила reclaim, volume/range/wick signal-свечи.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.png`.

RU report:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701_RU.md`.

Следующий безопасный шаг: zoom-lock для `manual_shift_review` или draft no-lookahead feature checklist/passport. ML/export/promotion запрещены.

## Current State 2026-07-01 Low Anchor Extra Auto Feedback Summary

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_COMPLETE_NO_ML_NO_OPTUNA`.

Extra auto pool закрыт: `66` кандидатов разобраны пользователем на `6` страницах.

Итог:

- `bad_noise`: `51`;
- `possible_entry`: `3`;
- `manual_shift_review`: `12`.

Summary:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701_RU.md`.

Следующий безопасный шаг: не ML, а аудит признаков: сравнить ручные good entries `M01..M19`, `3 possible_entry`, `12 manual_shift_review` и `51 bad_noise`, выписать no-lookahead признаки для будущего event dataset/scorer.

## Current State 2026-07-01 Low Anchor Extra Auto Page06 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь закрыл page `06`: все `6` кандидатов rejected как плохие входы не по тренду.

Итог:

- `bad_noise`: `6`;
- `bad_noise_countertrend_entry`: `6`;
- `possible_entry`: `0`;
- `manual_shift_review`: `0`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.png`.

## Current State 2026-07-01 Low Anchor Extra Auto Page05 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь разметил page `05`: все `12` кандидатов weak/bad и rejected. Дополнительная причина: часть auto-entry стрелок не совпадает с визуально нужной low/entry-зоной.

Итог:

- `bad_noise`: `12`;
- `bad_noise_weak_context_entry_mismatch`: `12`;
- `possible_entry`: `0`;
- `manual_shift_review`: `0`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.json`.

Следующий безопасный шаг: page `06` visual review, последняя страница extra auto pool.

## Current State 2026-07-01 Low Anchor Extra Auto Page04 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь прислал красный screenshot page `04`: текущие auto-entry не являются готовыми точками входа; рядом показаны более удобные места, которые нужно разбирать отдельно на zoom.

Итог:

- `manual_shift_review`: `12`;
- `auto_entry_not_gold_manual_shift_review`: `12`;
- `possible_entry`: `0`;
- `bad_noise`: `0`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.json`.

Следующий безопасный шаг: page `05` visual review. Отдельный возможный шаг после страниц: сделать zoom-review для page `04` manual shifts и превратить их в точные ручные target-led времена/цены.

## Current State 2026-07-01 Low Anchor Extra Auto Page03 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь сказал по page `03`: `тут все слабо`. Все `12` кандидатов страницы зафиксированы как `bad_noise / bad_noise_weak_context`.

Смысл: локальный low есть, но контекст не дает уверенного рабочего движения; такие входы визуально не похожи на сделки, в которые стоит заходить.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.json`.

Следующий безопасный шаг: page `04` visual review. Альтернатива перед page `04`: короткий audit первых трех страниц, где уже есть `24` rejected и `3` possible entries.

## Current State 2026-07-01 Low Anchor Extra Auto Page02 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь разметил page `02`: `LA018`, `LA020`, `LA026` можно оставить для работы как `possible_entry_one_percent_followthrough`; остальные `9` кандидатов page `02` rejected как `bad_noise_shallow_bounce`.

Итог:

- `possible_entry`: `3`;
- `bad_noise`: `9`;
- `ML/export`: запрещены.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.json`.

Следующий безопасный шаг: page `03` visual review или короткий промежуточный audit по первым двум страницам: какие признаки отличают `possible_entry` от `bad_noise_shallow_bounce` без lookahead.

## Current State 2026-07-01 Low Anchor Extra Auto Page01 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь подтвердил смысл reject для первой страницы extra auto review. `LA001..LA012` зафиксированы как `bad_noise` с причиной `bad_noise_shallow_bounce`.

Чистая формулировка: это мелкие локальные low без нормального продолжения; после входа цена дает короткий отскок или уходит в шум/стоп, часто без нужного трендового контекста. Для нашей системы это anti-example, а не рабочий вход.

PNG фиксации:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.json`.

Следующий безопасный шаг: показать page `02` extra auto review или сначала обобщить no-lookahead признаки, которыми отличать `bad_noise_shallow_bounce` от good manual entries.

## Current State 2026-07-01 Low Anchor Extra Auto Review V1

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_READY_NO_ML_NO_OPTUNA`.

Создан visual review pack для `66` extra auto candidates из resolved label-ledger V1. Это не минусы и не обучающий dataset: все строки имеют статус `pending_user_anti_review`.

Итог:

- `66` кандидатов;
- `6` PNG-страниц;
- `12` кандидатов на страницу;
- на каждом zoom показаны `entry_time_utc` и `entry_price_plus_5bps`;
- доступные ручные метки: `bad_noise`, `duplicate`, `possible_entry`, `wrong_type`, `ignore_unclear`.

Страница 01:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_01_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.json`.

Следующий безопасный шаг: пользователь смотрит страницу `01` и говорит, какие кандидаты плохие, дубли, возможные или непонятные. Optuna/ML/export запрещены.

## Current State 2026-07-01 Low Anchor Label Ledger V1 Resolved

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_BY_USER_NO_ML_NO_OPTUNA`.

Пользователь подтвердил pending review по `M05/M14/M15/M16/M17` словом `норм`. Создан resolved label-ledger V1: pending shift review закрыт, ручные времена ledger не переписаны.

Итог:

- `10` exact auto matches;
- `4` auto near not-gold по пользовательскому feedback `M03/M09/M10/M11`;
- `5` user-confirmed auto near-ok `M05/M14/M15/M16/M17`;
- `66` extra auto candidates остаются unlabeled pool.

Resolved JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701.json`.

Следующий безопасный шаг: anti-review/разбор `66` extra auto candidates или draft event dataset без ML/export.

## Current State 2026-07-01 Low Anchor Label Ledger V0

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_READY_NO_ML_NO_OPTUNA`.

Пользователь подтвердил feedback PNG по `M03/M09/M10/M11` словом `норм`. После этого создан label-ledger для `LOW_ANCHOR_ENTRY_SUGGESTER_V0`: `10` точных auto совпадений, `4` user-feedback near-not-gold, `5` pending shift review.

Следующий PNG для ручной проверки:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_PENDING_SHIFT_REVIEW_20260701.png`.

Оставшиеся цели: `M05`, `M14`, `M15`, `M16`, `M17`.

Label-ledger JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701.json`.

Граница: это не ML dataset и не scorer. До ручного решения по pending-точкам они не являются positive/negative labels.

## Current State 2026-07-01 Low Anchor User Feedback M03/M09/M10/M11

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_NO_ML_NO_OPTUNA`.

Пользователь дал visual feedback красными рамками/стрелками по `LOW_ANCHOR_ENTRY_SUGGESTER_V0`: `M03`, `M09`, `M10`, `M11` были рядом по метрике `±3m`, но не считаются gold для эталона.

Создан feedback-pack:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json`.

Правило дальше: `hit_within_3m` = near-review, не gold. Positive для event dataset брать из ручного ledger; auto near-candidate помечать `near-not-gold`, если пользователь показал другую свечу.

## Current State 2026-07-01 Low Anchor Suggester V0

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_SEED_DAY_REVIEW_NO_ML_NO_OPTUNA`.

Создан `LOW_ANCHOR_ENTRY_SUGGESTER_V0`: seed-day помощник поиска low-anchor входов на `SOLUSDT 1m 2026-05-14`. Он предлагает `anchor_low -> signal -> entry next open + 5 bps`, без использования future return, TP/SL, MFE/MAE или entry-candle OHLCV для выбора.

Результат: `85` авто-кандидатов после фильтра, `10/19` exact hits по ручным `M01..M19`, `19/19` hits в пределах `±3m`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_full_day_20260514.png`.

Zoom sheet для review:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_target_nearest_zoom_20260514.png`.

Следующее действие: показать пользователю zoom sheet и собрать verdict по ближайшим кандидатам: `норм / сдвинуть / нет / дубль / рано / поздно`. Это подготовка event dataset, не ML.

## Current State 2026-07-01 Data Scope Monthly Samples

Текущий статус: `SOLUSDT_1M_MONTHLY_FULL_DAY_SAMPLES_CREATED_NO_ML_NO_OPTUNA`.

Создан контрольный визуальный пакет по 126-дневному покрытию `SOLUSDT 1m`: по одному full-day PNG на месяц за `2026-01..2026-05`, плюс общий contact sheet.

Выбранные дни: `2026-01-27`, `2026-02-28`, `2026-03-28`, `2026-04-28`, `2026-05-28`. Все sample-дни имеют `1440` минутных строк и идут от `00:00 UTC` до `00:00 UTC` следующего дня.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701.png`.

Отчет:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701_RU.md`.

Граница: это только audit полноты данных и визуальной шкалы. Scorer/Optuna/ML не запускались.

## Current State 2026-07-01 C01 126 Days Source Audit

Текущий статус: `C01_126_DAYS_SOURCE_AUDIT_COMPLETE_NO_ML_NO_OPTUNA`.

Аудит подтвердил: `126 дней` было реальным числом локальных файлов `SOLUSDT 1m`, а не MTF-прогоном. Scope: `data/core/bybit_ohlcv/dt=*/tf=1m/symbol=SOLUSDT/part-final.csv`, `2026-01-26` .. `2026-05-31`, все файлы по `1440` строк.

Ошибка процесса: исторический `C01_MULTI_DAY_CHECK_V1_20260630.json` не закрепил top-level `symbol`, `timeframe`, `source_csv_pattern`, диапазон дат и команду воспроизведения. Это оформлено как недофиксация источника, не как доказательство ложного результата.

Артефакт:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_126_DAYS_SOURCE_AUDIT_20260701_RU.md`.

Граница: C01 V1 остается остановленным; Optuna/ML/export/promotion запрещены.

## Current State 2026-07-01 C02A Seed-Lock

Текущий статус: `C02A_TARGET_LOCK_SEED_V0_CREATED_NO_ML_NO_OPTUNA`.

C02A seed-lock создан для `M01/M02/M08`: `C02E03`, `C02E04`, `C02E10`. JSON-реестры и Markdown-статусы синхронизированы. Это seed-lock от регрессии, multi-day еще не запускался.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_FULL_DAY_ZOOMS_20260630.png`.

Следующее действие: `9.1_MULTI_DAY_BENCH_OR_USER_DECISION_NEXT_PASSPORT_NO_ML_NO_OPTUNA`.

## Current State 2026-06-30 C02A Entry-Only Scorer V0

Текущий статус: `C02A_ENTRY_ONLY_SCORER_V0_SEED_DAY_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Пункт рельсов `7.1` выполнен на seed-дне: C02A entry-only scorer ловит только `C02E03/M01`, `C02E04/M02`, `C02E10/M08`. Нарушений seed-аудита нет, `entry_open_price` записан только как цена исполнения и не используется для выбора входа.

Главный PNG для проверки глазами:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.png`.

Следующее действие: `7.1_USER_VISUAL_REVIEW_C02A_ENTRY_ONLY_SCORER_V0_BEFORE_TARGET_LOCK`.

До пользовательского `норм` по PNG не делать target-lock, multi-day, Optuna и ML/export.

## Current State 2026-06-30 C02 Good/Bad Audit

Текущий статус: `C02_GOOD_BAD_AUDIT_V0_COMPLETE_NO_ML_NO_OPTUNA`.

Выполнен good/bad аудит C02. Главный вывод: C02 нельзя сразу делать одним scorer, потому что это широкий low-event finder. Он поймал `M01/M02/M08`, но хорошие события также лежат около других типов ручных входов.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630_RU.md`.

Следующее действие: `C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`.

## Current State 2026-06-30 C02 User Labels Complete

Текущий статус: `C02_CANDIDATE_REVIEW_V0_USER_LABELS_COMPLETE_NO_ML_NO_OPTUNA`.

Пользователь завершил ручную разметку C02-кандидатов на seed-дне `SOLUSDT 1m 2026-05-14`: `C02E03..C02E12` помечены как `GOOD_ENTRY`, `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16` как `BAD_ENTRY`. Seed targets `M01/M02/M08` входят в хорошие кандидаты.

Контрольный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_USER_LABELED_GOOD_BAD_SHEET_20260630.png`.

Следующее действие: аудит отличий `GOOD_ENTRY` против `BAD_ENTRY` и решение, какие условия можно перенести в entry-only scorer. Scorer/Optuna/ML/export/promotion пока не запускать.

## Current State 2026-06-30 Passport Bench Step Plan

Текущий статус: `C02_CANDIDATE_REVIEW_PACK_READY_WAIT_USER_LABELS_NO_ML_NO_OPTUNA`.

Пользователь попросил расписать процесс по пунктам и подпунктам и начать выполнение. Создана рабочая лестница `Passport Bench V0`, выполнена матрица покрытия `M01..M19`, создана папка и паспорт-драфт `C02_DEEP_CAPITULATION_LOW` по `M01/M02/M08`, сделан seed visual C02, затем пользователь подтвердил `норм`. После подтверждения создан C02 candidate layer V0.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_BENCH_V0_STEP_PLAN_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630.json`.

Паспорт-драфт C02:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/passport_VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0_RU.md`.

Candidate layer V0: `96` raw, `16` event representatives, seed targets `M01/M02/M08` пойманы.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_full_day_review_20260630.png`.

Zoom review sheet:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_zoom_sheet_C02E01_C02E16_20260630.png`.

Следующее действие: пользовательский review `C02E01..C02E16`: `GOOD_ENTRY / BAD_ENTRY / WRONG_TYPE / LATE_DUPLICATE / NEEDS_SHIFT`. Scorer, Optuna и ML не запускать до разметки.

## Current State 2026-06-30 Fresh Target-Led Passport Bench V0

Текущий статус: `PASSPORT_BENCH_V0_STRUCTURED_NO_ML_NO_OPTUNA`.

Пользователь уточнил ключевой момент: не все паспорта применены к сделкам, поэтому нельзя говорить, что весь подход работает или не работает. Проверен только один узкий C01 по `M05/M06`, и он остановлен как слабый.

Покрытие сейчас: `HOT_RECLAIM_SUPPORT` частично покрыт C01; `DEEP_CAPITULATION_LOW`, `SUPPORT_RETEST_LOW`, `SWING_LOW_RECLAIM`, `TREND_DIP_CONTINUATION` паспортами не покрыты.

Следующее действие: `PASSPORT_COVERAGE_MATRIX_V0`, затем первый новый паспорт вне C01 — `C02_DEEP_CAPITULATION_LOW` по `M01/M02/M08`. Optuna/ML/export/promotion остаются запрещены.

Аудит этапа:
`reports/final_review/visual_entry_v3/fresh_target_led/process_audit/PASSPORT_BENCH_STAGE_AUDIT_20260630_RU.md`.

## Current State 2026-06-30 Fresh Target-Led C01 V1 Stopped

Текущий статус: `C01_V1_STOPPED_TOO_FEW_AND_LOW_QUALITY_NO_ML_NO_OPTUNA`.

Пользователь честно отклонил направление `C01 V1`: сделок мало, а большая часть найденных multi-day входов визуально плохая. Это решение принято как стоп ветки, а не как повод подкручивать Optuna.

Важно: в C01 V1 нет дневного лимита сделок. `max_candidates_per_day=2` является статистикой результата строгого фильтра на 126 днях, а не правилом `максимум 2 сделки в день`.

Следующее действие: перейти от узкого паспорта `M05/M06` к более широкому target-led кандидатному слою по всем `M01..M19`, с full-day PNG на реальной шкале времени и ручной разметкой качества. ML/export/promotion остаются запрещены без `APPROVED_FOR_ML`.

Аудит решения:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_V1_STOP_DECISION_20260630_RU.md`.

## Current State 2026-06-30 Fresh Target-Led C01 Multi-Day Check V1

Текущий статус: `C01_MULTI_DAY_CHECK_V1_RAW_NEEDS_VISUAL_TUNING_NO_ML`.

Активный свежий пункт: `C01_ENTRY_ONLY_SCORER_V0`.

Паспорт: `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0`.

Пользователь подтвердил `M05` после сдвига на одну свечу вправо: signal `10:43 UTC` -> entry `10:44 UTC`. `M06` без изменений: signal `12:00 UTC` -> entry `12:01 UTC`.

Старый scorer V0 больше не считается актуальным pass. Новый `C01_ENTRY_ONLY_SCORER_V1` на `SOLUSDT 1m 2026-05-14` поймал `M05/M06`, ложных кандидатов `0`, `M12` не включил. После пользовательского `далее поехали по рельсам` создан seed target-lock: `M05/M06` защищены от регрессии.

PNG для пользовательского решения:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_full_day_M05_M06_20260630.png`.

Raw multi-day check V1: 126 дней, 25 кандидатов, максимум 2 в день. Частота не шумная, но визуальное качество смешанное. Следующее действие: показать zoom contact sheet и руками отметить кандидаты для `C01_QUALITY_FILTER_V2`. Старые V7/V8/V9/V10/V11 не продолжать как очередь задач.

## Visual Entry EVENT_RANKED_BRICKS_V10 2026-06-29

Текущий статус: `EVENT_RANKED_BRICKS_V10_CLEANER_BUT_PARTIAL_NO_ML`.

Активный свежий слой: `src/mlbotnav/visual_entry_event_ranked_bricks_v10_runner.py`.

V10 решает проблему V9 с сериями похожих входов: внутри low-cluster оставляется один rank-winner. Ключ кластера: `low_event_start_idx:event_low_idx`.

Результат: шум снизился, но часть нужных пользовательских входов потеряна.

Validation `2026-05-13`: чистый только `HOT_CHAIN`, `1/9`, `0` false.

Holdout `2026-05-14`: `warm` = `3/17`, `6` false; `hot-first` = `2/17`, `7` false; `deep` = `3/17`, `20` false.

Текущее решение: это не ML-кандидат. Следующий рабочий слой `V11_RECOVER_RANKED_MISSES`: отдельные подрежимы для потерянных warm/hot/deep входов, без широкого union.

## Visual Entry BRICK_BY_BRICK_SELECTOR_V9 2026-06-29

Текущий статус: `BRICK_BY_BRICK_SELECTOR_V9_PARTIAL_DIAGNOSTIC_NO_ML`.

Активный свежий слой: `src/mlbotnav/visual_entry_brick_by_brick_selector_v9_runner.py`.

V9 проверяет не общий шумный union, а отдельные кирпичи входа у лоя:
1. `HOT_CHAIN_EVENT_LOW`
2. `HOT_FIRST_STRONG_RECLAIM`
3. `WARM_STRUCTURAL_RECLAIM`
4. `DEEP_TERMINAL_RECLAIM`

Validation `2026-05-13`: чистый результат есть только у `V9_01_HOT_CHAIN_EVENT_LOW_BRICK`: `1/9`, `0` false, вход `08:48`.

Holdout `2026-05-14`: `warm` ловит `5/17`, но дает `16` false; `hot-first` ловит `4/17`, но дает `20` false; `deep` ловит `4/17`, но дает `33` false.

Главный вывод: направление "кирпичами" правильное, но пока это не стратегия и не ML-кандидат. Общий research union ловит больше целей, но снова создает кашу на графике (`68` false).

Следующее рабочее действие: `V10_EVENT_RANKED_BRICKS`, где внутри каждого low-event выбирается один лучший сигнал. Без cooldown `30/45/60/90`, без будущего, без TP/SL/MFE/MAE, без ML-export.

## Visual Entry manual bottoms validation/holdout 2026-06-25
Текущий статус: `MANUAL_BOTTOMS_EXTRACTED_AUTO_KNIFE_SUGGESTED_CP06_EMPTY_NO_ML`.

Пользовательские красные метки на `2026-05-13` и `2026-05-14` переведены в `manual_entries.json` по правилу `signal candle -> next open entry`:
1. `2026-05-13`: `9` ручных входов, `reports/manual_entries/SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms/manual_entries.json`.
2. `2026-05-14`: `17` ручных входов, `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms/manual_entries.json`.

Авто-разметка `AK#` построена отдельно и не является целями ML. Контрольные PNG находятся рядом с manual entries и показывают красные `S#`, зеленые `E#`, голубые `AK#`.

CP06 на новых днях без подкрутки не дал ни одного candidate-entry. Это честный diagnostic результат: текущая DEV-12 механика не обобщилась на эти пользовательские входы. Следующий рабочий слой: `REVERSAL_BOTTOM_KNIFE_DROP_V0`.

## Visual Entry CP06 validation/holdout readiness 2026-06-25
Текущий статус: `NEEDS_MANUAL_LABELS_NO_VALIDATION_RUN`.

CP06 `CP06_CP01_RECOVER_NOWICK_LATE_RETEST` визуально закрывает DEV `2026-05-12`, но validation `2026-05-13` и holdout `2026-05-14` пока нельзя честно считать: для них отсутствуют `manual_entries.json`.

Готово:
1. seed PNG/JSON для `2026-05-13`;
2. seed PNG/JSON для `2026-05-14`;
3. core CSV по обоим дням с SHA256;
4. readiness-аудит `reports/final_review/visual_entry_v3/cp06_validation_holdout_readiness/cp06_validation_holdout_readiness_20260625_RU.md`.

Не готово: ручные `entries[].target_entry_time_utc` для validation/holdout.

Граница: не запускать подбор на `2026-05-13`/`2026-05-14`; они должны остаться честной проверкой после пользовательской разметки.

## Visual Entry v3 DEEP_CAPITULATION_RECLAIM 2026-06-25
Текущий активный visual-entry слой: `DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML`.

Runner: `src/mlbotnav/visual_entry_deep_capitulation_reclaim_runner.py`.

Лучший рабочий ensemble `DQ01_EQ01_PLUS_DEEP_RECLAIM`: `10/11` hit, `1` miss, `73` false, `83` entries, `precision=0.1205`, `recall=0.9091`, `f1=0.2128`.

High-recall diagnostic `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP`: `11/11`, но `95` false, поэтому это не ML-кандидат.

Главный аудит: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_audit_20260625_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_family_overlay_2026-05-12_deep_reclaim_01_dq01_eq01_plus_deep_reclaim_20260625T142559Z.png`.

Вывод: добрали глубокие пропуски `12:33`, `15:26`, `17:00`; `08:26` ловится только high-risk no-wick режимом. Дальше нужен `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`, в ML ничего не передавать.

## Visual Entry v3 EARLY_FLUSH_REVERSAL 2026-06-25
Текущий активный visual-entry слой: `DEV_EARLY_FLUSH_REVERSAL_DIAGNOSTIC_NO_ML`.

Runner: `src/mlbotnav/visual_entry_early_flush_runner.py`.

Лучший общий результат `EQ01_Q09_SEVERE_SOFT45`: `7/11` hit, `4` miss, `68` false, `75` entries, `precision=0.0933`, `recall=0.6364`, `f1=0.1628`.

Диагностический recall-вариант `EQ03_Q09_SEVERE_SOFT45_NOWICK`: `8/11`, но `90` false; он показывает, что `08:26` можно поймать отдельным no-wick режимом, но пока слишком шумно.

Главный свежий аудит: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_audit_20260625_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_family_overlay_2026-05-12_early_flush_01_eq01_q09_severe_soft45_20260625T134923Z.png`.

Вывод: ранние входы требуют отдельных подсемейств. Это не ML-кандидат; дальше добирать глубокие пропуски `12:33`, `15:26`, `17:00` через `DEEP_CAPITULATION_RECLAIM`.

## Visual Entry v3 quality filter diagnostic 2026-06-25
Текущий активный visual-entry слой: `DEV_QUALITY_FILTER_DIAGNOSTIC_NO_ML`.

Лучший результат `Q09_ENSEMBLE_Q07_Q01`: `4/11` hit, `7` miss, `53` false, `57` entries, `precision=0.0702`, `recall=0.3636`, `f1=0.1176`.

Главный свежий аудит: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_audit_20260625_RU.md`.

Вывод: слой качества улучшил шум относительно micro-bottom, но это не ML-кандидат. Дальше работать только на DEV-дне `2026-05-12`, без validation/holdout и без ML.

## Visual Entry v3 micro-bottom diagnostic 2026-06-25
Текущий активный статус visual-entry ветки: `DEV_MICRO_BOTTOM_SIGNATURE_DIAGNOSTIC_NO_ML`.

Контракт входа подтвержден: закрытая сигнальная свеча -> LONG на `open` следующей свечи, slippage `5 bps`, `lookahead=NO`.

Лучший micro-bottom результат: `4/11` hit, `7` miss, `135` false, `139` entries, `precision=0.0288`, `recall=0.3636`, `f1=0.0533`. Это диагностический результат, не ML-кандидат.

Главный свежий аудит: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_audit_20260625_RU.md`.
## Visual Entry v3 passport-family diagnostic 2026-06-25
Текущий статус: `DEV_PASSPORT_FAMILY_DIAGNOSTIC_DONE_NO_ML`.

Новый runner `src/mlbotnav/visual_entry_passport_family_runner.py` проверил no-lookahead семейства по v3-разметке `2026-05-12`: `DEEP_CAPITULATION_NEXT_OPEN`, `SUPPORT_WICK_REVERSAL_NEXT_OPEN`, `DIVERGENCE_AT_SUPPORT_NEXT_OPEN`, `CHOCH_REENTRY_AFTER_BOTTOM_NEXT_OPEN`, `VPOC_RANGE_RECLAIM_NEXT_OPEN`.

Новый overlay показывает `S/E` ручной разметки, `CS` кандидатного сигнала, `H` попадания и ярко-красный `FALSE/X` лишнего входа.

Главный аудит: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_audit_20260625_RU.md`.

Лучший результат: `DEEP_CAPITULATION_NEXT_OPEN`, `1/11` hits, `20` false, `21` entries, `f1=0.0625`. Это не кандидат. В ML ничего не передавать.

Следующий рабочий слой: `VISUAL_MICRO_BOTTOM_SIGNATURE_V0`, потому что текущие паспорта видят общую тему "дно/перепроданность", но не умеют отделить нужные ручные входы от частых локальных минимумов.

## Visual Entry v3 current state 2026-06-25
Текущий статус: `DEV_V3_ENTRY_ARROWS_READY_NO_CANDIDATE_NO_ML`.

Рабочая разметка v3 под пользовательский стиль создана на `2026-05-12`: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows/manual_entries.json`. Входы стоят на entry candle, сигнал считается предыдущей свечой, исполнение - следующий `open` + `5 bps`.

No-lookahead runner добавлен: `src/mlbotnav/visual_entry_no_lookahead_candidates.py`. Итоговый честный DEV результат слабый: лучший `UNION_ABC_NEXT_OPEN` дал `3/11`, `34` false. Это не кандидат и не ML.

## Visual Entry Calibration DEV-12 2026-06-25
Текущий статус: `DEV_DAY_MANUAL_ENTRIES_READY_SCORER_READY`.

Создан первый машинный `manual_entries.json` по пользовательскому PNG `2026-05-12`: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries.json`.

Восстановленные LONG-цели: `01:44`, `04:15`, `09:12`, `12:36`, `15:34`, `17:05` UTC. Это предварительная расшифровка стрелок из PNG; при необходимости можно поправить минуты вручную.

Добавлен visual scorer: `src/mlbotnav/visual_entry_score.py`. Проверка `tests.test_visual_entry_score` прошла.

Первый результат по старому B001 CSV: `3/6` попаданий, `15` лишних входов, `precision=0.16666666666666666`, `recall=0.5`, `f1_visual=0.25`, `net_return_pct=-62.229358575198916`, статус `VISUAL_HITS_WITH_TOO_MANY_FALSE_ENTRIES`. Это diagnostic-only, ML не трогать.

## Visual Entry feature/pre-filter diagnostic 2026-06-25
Текущий статус: `DEV_DIAGNOSTIC_DONE_NEXT_SOLO_SCORER_AND_REVERSAL_FAMILY`.

Feature-аудит и prefilter-поиск завершены. План: `reports/qa_gate/visual_entry_candidate_family_plan_20260512_DEV_RU.md`.

Главный вывод: простые условия reversal/dip сами по себе слишком шумные. Следующий рабочий слой: diagnostic runner по существующим паспортам и новая `REVERSAL_DIP_BUY_LONG v0`.

## Visual Entry solo-passport diagnostic 2026-06-25
Текущий статус: `DEV_SOLO_PASSPORT_DIAGNOSTIC_DONE_NO_ML`.

Solo runner готов: `src/mlbotnav/visual_entry_solo_passport_runner.py`.

Отчет: `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV_RU.md`.

Ключевые результаты DEV-дня `2026-05-12`:
1. `F009_EMAGAP_DOWN`: `2/6` hits, `6` false, `8` entries, `f1_visual=0.2857`;
2. `F059_ENGULFBULL`: `1/6` hits, `0` false, `1` entry, `f1_visual=0.2857`;
3. `F010_EMASLOPE_DOWN`: `2/6` hits, `16` false, `18` entries, `f1_visual=0.1667`;
4. `B001_RET_N_FIXED`: `5/6` hits, но `142` false, поэтому это шумный diagnostic, не кандидат.

Вывод: одиночные паспорта дают детали, но не готовую стратегию. Дальше нужен combo слой: контекст падения/растяжения (`F009`/EMA-down) + чистый reversal trigger (`F059` и родственные свечные признаки) + suppression от частых ложных входов. В ML ничего не передавать.

## Visual Entry Calibration TZ 2026-06-25
Текущий статус: `DESIGN_READY_WAITING_FOR_MARKUP`.

ТЗ: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_CALIBRATION_TZ_RU.md`.

Зафиксирован контур: три seed-графика уже готовы, дальше пользовательская разметка переводится в `manual_entries.json`, scorer считает попадания и ложные входы, затем паспорта и комбо проверяются сначала на DEV, потом на validation/holdout. В ML ничего не передавать без ручного review и `APPROVED_FOR_ML`.

## Visual Entry Calibration seed screenshots 2026-06-25
Текущий статус: `MANUAL_MARKUP_SEED_IMAGES_READY`.

Сгенерированы три скриншота для ручной разметки Visual Entry Calibration: `2026-05-12`, `2026-05-13`, `2026-05-14`, `SOLUSDT 1m`, `data_layer=core`.

Папка: `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625`.

Критичная граница: эти картинки построены из тех же `core` свечей, которые должны быть источником для последующего backtest/Optuna/ML сравнения. Manifest фиксирует SHA256 каждого исходного CSV.

## B001 marked-entry fixed backtest 2026-06-25
Текущий статус: `MARKED_ENTRY_FIXED_BACKTEST_DONE_NEGATIVE`.

Аудит: `reports/qa_gate/b001_marked_entry_fixed_backtest_audit_20260625T073900Z_RU.md`.

Фиксированные пороги B001 `0.02 / 0.04 / 0.10 / 0.95 / 0.35` при `3/5` подтверждениях реально ловят `09:25` и `12:36` на OOS `2026-05-12`, но общий результат отрицательный: `-47.05387771496912%` при `18` сделках с `min_expected_move_pct=0.001` и `-67.41968770852606%` при `30` сделках без min-move.

`17:15` не вошел не из-за F-гейта: на `17:14` есть `4/5`, но `prob_up=0.3748`, ниже `p_enter_long=0.60`. `08:15` и `15:48` не проходят семейный F-гейт. В ML ничего не передавать.

## B001 marked-entry screenshot audit 2026-06-25
Текущий статус: `MARKED_ENTRY_AUDIT_DONE_DIAGNOSTIC_ONLY`.

Аудит: `reports/qa_gate/b001_marked_entry_screenshot_audit_20260625T070500Z_RU.md`.

Результат: текущая B001 `RET_N LONG` family может ловить отмеченные точки только там, где уже есть положительный возврат за последние `1/3/6/12/24` минут. Для ранних "покупок у дна" нужна отдельная reversal/dip-buy family.

## Shared-study profile-edge coverage fix 2026-06-25
Текущий статус: `PROFILE_EDGE_FORCING_FIXED_CONFIRMED`.

Аудит: `reports/qa_gate/shared_study_profile_edge_coverage_fix_20260625T063700Z_RU.md`.

Причина старых coverage warning закрыта в коде: профильные edge-пробы больше не сдвигаются на `profile_edge_worker_offset`, не расходуют edge slot до фактического profile sampling и распределяют min/max edge-задачи между process workers.

Проверки прошли: `py_compile`, `PSParser`, `tests.test_optuna_search_runtime` `73/73 OK`, `text_guard` `PASS`.

Runtime confirmation: `b001_3of5_long_shared_edgefix3_20260625_115056`, final snapshot `w3`: terminal `42/42`, core `5/5 PASS`, profile `7/7 PASS`, forced min/max полный `7/7`.

Старые и новые B001 LONG smoke результаты отрицательные/нулевые, в ML не передавать. Вопрос profile-edge coverage закрыт.

## B001 family-unified 3/5 LONG shared-study 2026-06-24
Текущий статус: `B001_3OF5_LONG_SHARED_DONE_NEGATIVE_EDGE_WARN`.

Аудит: `reports/qa_gate/b001_family_unified_3of5_long_shared_audit_20260624T195200Z_RU.md`.

Диагностический запуск `B001 family-unified 3/5 LONG` прошел на shared-study профиле `3x3/9`.

Факты:
1. `SharedOptunaStudy=true`;
2. `SharedStudyId=b001_3of5_long_shared_20260625T005102`;
3. storage preflight `postgresql`;
4. матрица `reports/qa_gate/b001_family_unified_long_3of5_shared_20260625T005102/B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml`;
5. launcher `OK`;
6. best worker `w3`;
7. OOS `-2.0302055441506761`;
8. сделок `1`.

Решение: результат tradeful, но отрицательный. Это не кандидат, ML не трогать.

Ограничение результата: core edge coverage прошел `5/5`, profile edge coverage неполный `4/7`, failed profiles `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`. Поэтому результат считать runtime diagnostic с coverage warning.

## Optuna shared-study process-pool 2026-06-24
Текущий статус: `OPTUNA_SHARED_STUDY_3X3_9_READY_NO_PROMOTION`.

Аудит: `reports/qa_gate/optuna_shared_study_process_pool_audit_20260624T190435Z_RU.md`.

Собран режим, где `w1/w2/w3` остаются тремя отдельными Python-процессами для нагрузки, но Optuna study у них общая. Это текущий правильный ответ на задачу "один общий поиск, но мощность как у трех worker".

Ключевые факты:
1. `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`, `OptunaTrials=42`.
2. Включение: `-SharedOptunaStudy -SharedStudyId <RUN_ID>`.
3. Shared study разрешена только на не-`sqlite` storage; проверено на `postgresql`.
4. Worker reports и Optuna artifacts получили worker suffix и не перетираются.
5. Trial-history rows получили worker context.
6. ML выключен: `ml_backend=off`, `decoupled_ml=true`.

Финальный smoke B001 `4/5 LONG` завершился инфраструктурно корректно, но результат отрицательный: OOS `-10.009351008800071`, сделок `2`. В ML ничего не передавалось.

## Optuna single-worker профиль 1x9/9 2026-06-24
Текущий статус: `OPTUNA_SINGLE_WORKER_1X9_9_READY`.

Профиль для одного мощного worker:
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=1`;
4. `SearchWorkersPerProcess=9`;
5. `OptunaTrials=42`.

Dry-run прошел: один worker получает всю мощность и одну Optuna-историю. CPU-нагрузка примерно равна прежнему `3x3/9`, память должна быть спокойнее из-за одного Python-процесса.

## B001 family unified 5/5 2026-06-24
Текущий статус: `B001_FAMILY_UNIFIED_5OF5_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_unified_5of5_audit_20260624T154700Z_RU.md`.

Теперь B001 может калиброваться как одно семейное звено через `B001_family_move`:
1. LONG family: `B001_family_move=1`.
2. SHORT family: `B001_family_move=-1`.
3. Отдельные `F001_move..F005_move` в unified-матрицах отсутствуют.
4. Калибруются только пороги `F001_thr_pct..F005_thr_pct` и подтверждение `entry_action_min_confirmations`.

Smoke strict `5/5` на `2026-05-11 -> 2026-05-12`: LONG и SHORT дали `0` сделок. Причина уже не конфликт направлений, а слишком жесткое совпадение всех пяти горизонтов.

В ML ничего не передавалось. Основной маршрут остается `B003.1 large LONG 2н/1н`.

## B001 family strict 5/5 smoke 2026-06-24
Текущий статус: `B001_FAMILY_STRICT_5OF5_SMOKE_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_strict_5of5_smoke_audit_20260624T153100Z_RU.md`.

Проверено семейное правило `5 из 5`: все `F001..F005` должны одновременно дать `ALLOW` на одной сигнальной свече. Runtime применил `and_all`.

Результат:
1. LONG: `0` сделок, `EMPTY_ACTION_GATE`, `985 / 573 / 0 / 0 / 0`.
2. SHORT: `0` сделок, `EMPTY_ACTION_GATE`, best OOS `0.0`, сделок `0`.

В ML ничего не передавалось. Основной маршрут остается `B003.1 large LONG 2н/1н`.

## B001_COMBO_DIAG визуальный аудит входов 2026-06-24
Текущий статус: `B001_COMBO_DIAG_GATE_VISUAL_AUDIT_DONE`.

Построены диагностические графики полного дня `2026-05-12`:
1. LONG: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.png`.
2. SHORT: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.png`.

Счетчики совпадают с OOS runtime:
1. LONG: `mode=621`, `F-gate=4`, `min_move=4`, `trades=4`.
2. SHORT: `mode=637`, `F-gate=240`, `min_move=2`, `trades=2`.

Вывод: график не обрезан, сырой день полный. Узкая зона входов вызвана фильтрами, а не отсутствием свечей.

## B001_COMBO_DIAG N-of-M 2026-06-24
Текущий статус: `B001_COMBO_DIAG_N_OF_M_SMOKE_DONE_NO_CANDIDATE`.

Аудит: `reports/qa_gate/b001_combo_diag_n_of_m_audit_20260624T125500Z_RU.md`.

Зафиксировано правильное диагностическое действие: для совместной проверки `F001..F005` использовать `entry_action_min_confirmations` и политику `N из M`, а не старый жесткий `AND`.

Smoke 1д/1д на полной комбинации:
1. LONG: OOS `-8.498538882812346%`, `4` сделки, `N=1`.
2. SHORT: tradeful worker OOS `-6.055628696458093%`, `2` сделки, `N=1`.
3. Положительного кандидата нет, ML не тронут.

Основной маршрут остается `B003.1 large LONG 2н/1н`.

## B003 block route 2026-06-24
Текущий статус: `NEXT_B003_1_LARGE_LONG`.

Предыдущий блок `B002` закрыт итогом `B002.3`: `reports/qa_gate/b002_block_summary_b002_3_20260624T100800Z_RU.md`.

Решение по `B002`: LONG `NO_BLOCK_WINNER`; SHORT `NO_BLOCK_WINNER`; ML не тронут.

Следующий блок: `B003`, одиночный паспорт `F007 / F007_RSTD20_ALLOW`.

Активный worker-профиль: `3x3/9`.
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=3`;
4. `SearchWorkersPerProcess=3`.

Следующий строгий шаг: `B003.1 large LONG 2н/1н`, затем `B003.2 large SHORT 2н/1н`. В ML ничего не передавать.

## B002 block route 2026-06-24
Текущий статус: `B002_3_BLOCK_SUMMARY_CLOSED_NEXT_B003`.

Предыдущий блок `B001` закрыт итогом `B001.6`: `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.

Решение по `B001`: LONG `F001 / F001_RET1_ALLOW` фиксируется как ручной положительный кандидат; SHORT `NO_BLOCK_WINNER`; ML не тронут.

Следующий блок: `B002`, одиночный паспорт `F006 / F006_HLSPREAD_ALLOW`.

Активный worker-профиль: `3x3/9`.
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=3`;
4. `SearchWorkersPerProcess=3`.

Откат на `2x3/6` допустим только при устойчивой перегрузке CPU/памяти или падении worker-процессов, с записью причины в аудите.

Следующий строгий шаг: `B002.1 large LONG 2н/1н`, затем `B002.2 large SHORT 2н/1н`. В ML ничего не передавать.

## B001.5 large SHORT 2026-06-24
Текущий статус: `B001_5_LARGE_SHORT_CLOSED_NO_BLOCK_WINNER`.

Аудит: `reports/qa_gate/b001_large_short_b001_5_audit_20260624T094057Z_RU.md`.

B001 SHORT на окне `2026-05-11..2026-05-24 -> 2026-05-25..2026-05-31` завершился `OK`, но без победителя.

Итог SHORT: `block_winner=null`; лучший доступный fallback `F004 / F004_RET12_ALLOW`, OOS `0.0`, сделок `0`, runtime `EMPTY_ACTION_GATE`. По OOS у всех `F001..F005` сделок `0`.

Входов/выходов в OOS нет. Train-сделки были у `F002` и `F003`; они зафиксированы в аудите как строки вход/выход/profit и не дают положительного блока.

Фикс терминального вывода: `APTuna/run_block_family_selection.ps1` теперь по умолчанию печатает краткую сводку, а не полный JSON. Полный JSON остается в файле отчета; `-EmitJson` включает машинный stdout.

Следующий строгий номер: `B001.6 итог блока LONG+SHORT`. В ML ничего не передавать.

## B001.4 large LONG 2026-06-24
Текущий статус: `B001_4_LARGE_LONG_PASS_WITH_WINNER`.

Аудит: `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.

B001 LONG на окне `2026-05-11..2026-05-24 -> 2026-05-25..2026-05-31` завершился `OK`.

Победитель LONG: `F001 / F001_RET1_ALLOW`, OOS `+0.7322559143841945`, сделок `1`, runtime `TRADEFUL_POSITIVE`. Цель `1%` не достигнута, поэтому это положительный ручной кандидат блока, но не автоматический GO в ML.

Исторический следующий номер после этого раздела был `B001.5`; он уже закрыт. Актуальный следующий номер указан сверху: `B001.6 итог блока LONG+SHORT`.

## B001.3 smoke 1д/1д 2026-06-24
Текущий статус: `B001_3_SMOKE_AUDIT_PASS`.

Аудит: `reports/qa_gate/b001_smoke_1d1d_audit_20260624T075006Z_RU.md`.

Smoke проверил блок `B001` как семейство `F001..F005` на `SOLUSDT 1m core`, train `2026-05-11`, OOS `2026-05-12`.

Финальный LONG: `F001 / F001_RET1_ALLOW`, OOS `+2.404470760400401`, сделок `1`, `block_winner=F001`.

Финальный SHORT: лучший доступный `F002 / F002_RET3_ALLOW`, OOS `-0.3092010602366857`, сделок `1`, `block_winner=null`.

Технический smoke пройден. Следующий строгий номер: `B001.4 large LONG 2н/1н`. В ML ничего не передавать.

## Block-Family Route Correction 2026-06-24
Current status: `BLOCK_ROUTE_READY_FOR_B001`.

Audit: `reports/qa_gate/block_family_passport_route_audit_20260624T064900Z.md`.

Current route is block/family calibration, not a linear F-only route. Family blocks run all active solo F-passports in the block, then select one block winner or `NO_BLOCK_WINNER`. Single-passport blocks run through the same block runner with one passport.

Implemented runner: `APTuna/run_block_family_selection.ps1`, backed by `src/mlbotnav/block_family_manifest.py`.

Verified by dry-run: `B001` expands to `F001..F005` and writes block selection reports without ML promotion.

ML state: nothing from block calibration is passed into ML automatically. Final manual approval happens only after the full block route is complete and the user chooses positive blocks/candidates.

Next strict item: run `B001` block LONG, then `B001` block SHORT, sequentially.

## Min-Move Runtime Guard Fix 2026-06-24
Current status: `FIX_APPLIED_SUPERSEDED_BY_BLOCK_ROUTE`.

The route/runtime bug is fixed in code. `MIN_MOVE_UNREACHABLE` is now explicit in backtest/OOS diagnostics, fail-keyed and penalized in Optuna, skipped by adaptive selection when reachable alternatives exist, and the default 1m min-move grid is now `0.0,0.001,0.002,0.003`.

Validation before block-route correction: focused pytest `124 passed`; text_guard `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260624T063715Z.json`; readiness frozen as expected, report `reports/readiness/readiness_check_20260624T063714Z.json`.

Old next item `8.2.19 F068_PATTERNAGE_ALLOW` is superseded by the corrected block-family route.

## Zero-Trade Diagnostic 2026-06-24
Current status: `ROOT_CAUSE_FOUND`.
Artifact: `reports/qa_gate/ml_optuna_zero_trade_min_move_diagnostic_20260624T051535Z.md`.

The current Stage 8.2 zero-trade pattern has a confirmed common cause in non-empty-gate cases: `min_expected_move_pct` can be too high for the `exchange_like` proxy (`confidence * atr14 * sqrt(hold_bars)`) after action gates. F067 LONG is the clearest case: `1415` signals after gate, `0` after min-move because selected `0.01` is above the OOS proxy max `0.005140`.

Historical next pointer `8.2.19 F068_PATTERNAGE_ALLOW` is superseded by the corrected block-family route at the top of this file.

## Route Memory Audit 2026-06-23
Status: `ON_ROUTE`.

Audit: `reports/qa_gate/ml_optuna_route_memory_audit_20260623T205751Z.md`.

Current control audit after F067: `reports/qa_gate/ml_optuna_route_status_audit_after_f067_20260624T044311Z.md`.

Optuna/ML separation is intact. Current F050-F067 large-window results are not approved and must not be packaged, approved, or ingested into ML.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file.

Last updated UTC: 2026-06-23T22:57:00Z

## ML Optuna Calibration Stage 8.2.18 F067 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_18_f067_audit_20260623T225700Z.md`.

Stage 8.2.18 ran F067 Pattern Strength entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file.

## ML Optuna Calibration Stage 8.2.17 F066 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_17_f066_audit_20260623T224200Z.md`.

Stage 8.2.17 ran F066 OBV Bearish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.16 F065 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_16_f065_audit_20260623T223100Z.md`.

Stage 8.2.16 ran F065 OBV Bullish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.15 F064 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_15_f064_audit_20260623T222100Z.md`.

Stage 8.2.15 ran F064 MACD Bearish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.14 F063 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_14_f063_audit_20260623T221200Z.md`.

Stage 8.2.14 ran F063 MACD Bullish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.13 F062 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_13_f062_audit_20260623T220200Z.md`.

Stage 8.2.13 ran F062 RSI Bearish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.12 F061 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_12_f061_audit_20260623T215100Z.md`.

Stage 8.2.12 ran F061 RSI Bullish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.11 F060 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_11_f060_audit_20260623T213900Z.md`.

Stage 8.2.11 ran F060 Bearish Engulfing entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.10 F059 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_10_f059_audit_20260623T213000Z.md`.

Stage 8.2.10 ran F059 Bullish Engulfing entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.11 Run F060_ENGULFBEAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.9 F058 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_9_f058_audit_20260623T211900Z.md`.

Stage 8.2.9 ran F058 Shooting Star entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.10 Run F059_ENGULFBULL_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.8 F057 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_8_f057_audit_20260623T205000Z.md`.

Stage 8.2.8 ran F057 Hammer entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.7 F056 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_7_f056_audit_20260623T203800Z.md`.

Stage 8.2.7 ran F056 Bearish Pin Bar entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.8 Run F057_HAMMER_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.6 F055 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_6_f055_audit_20260623T202700Z.md`.

Stage 8.2.6 ran F055 Bullish Pin Bar entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.5 F054 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_5_f054_audit_20260623T201700Z.md`.

Stage 8.2.5 ran F054 Inside Bar entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.6 Run F055_PINBULL_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.4 F053 2026-06-23
Current status: `CLOSED_NO_GO_FIX_APPLIED`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.

Stage 8.2.4 ran F053 Doji entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Fix applied: restored readiness freeze after a parallel `-UseTemporaryUnlock` race and added a guard to reject a second live temporary-unlock process-pool run before workers start.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`.

## ML Optuna Validation Stage 8.2.3 F052 2026-06-23
Current status: `CLOSED_VALIDATION_FAIL_NO_ML_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_3_f052_fixed_validation_audit_20260623T194700Z.md`.

Stage 8.2.3 validated fixed F052 CHOCH LONG params from the positive Stage 8.2.2 run on the adjacent clean `core` window.

Window: train `2026-05-04..2026-05-17`, OOS `2026-05-18..2026-05-24`.

Final result: train gate `false`; OOS `-5.696708101293968`; OOS trades `1`; OOS goal pass `false`; exit reason `timeout`.

Decision: no candidate package should be built from this validation; do not approve or ingest it into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T195125Z.json`.

Next strict WBS step: continue with the next user-selected passport/action discovery, or define a new validation idea.

## ML Optuna Calibration Stage 8.2.2 F052 2026-06-23
Current status: `CLOSED_POSITIVE_TEST_CANDIDATE_NEEDS_VALIDATION`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_2_f052_audit_20260623T193700Z.md`.

Stage 8.2.2 ran F052 CHOCH on the large clean `core` window for both LONG and SHORT.

Final result: LONG produced `1` OOS trade and `+5.3486475132039635`; SHORT produced `0` trades.

Caveat: LONG train gate failed and the only OOS trade exited by timeout.

Decision: no candidate package should be built automatically; ML training remains not started.

Next strict WBS step: manual decision on validation, draft package approval, or next passport/action discovery.

## ML Optuna Calibration Stage 8.2.1 F050 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_1_f050_audit_20260623T192700Z.md`.

Stage 8.2.1 ran F050 BOSUP on the large clean `core` window.

Final valid run: `long_only`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`, process pool `OK`, OOS trades `0`, OOS return `0.0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.2 Run F052_CHOCH_ALLOW large-window candidate`, unless user overrides the target.

## ML Optuna Calibration Stage 8.2 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_audit_20260623T191900Z.md`.

Stage 8.2 ran F051 BOSDOWN on the large clean `core` window after fixing explicit data-layer propagation through launcher, adaptive runtime, Optuna/grid search, train, and OOS.

Final valid run: `short_only`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`, process pool `OK`, OOS trades `0`, OOS return `0.0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: manual decision for next passport/action calibration target or revised `8.2` candidate run.

## ML Large Clean Window Stage 8.1 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.

Stage 8.1 is closed: the large clean window is fixed in `configs/ml_large_clean_window_manifest.yaml`.

Window: `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Audit: `PASS`, missing files `0`.

Boundary: Optuna calibration and ML training were not started.

Next strict WBS step: `8.2 Run Optuna calibration`.

## ML Smoke Bridge Stage 7 Closeout 2026-06-23
Current status: `STAGE_7_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.

Stage 7 is closed: the smoke bridge from approved Optuna package into ML ingest dataset works end to end.

Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.

Rows total: `1177`.

Boundary: ML training was not started.

Next strict WBS step: `8.1 Fix large clean window`.

## ML Ingest Stage 7.5 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.

Stage 7.5 is closed: ML ingest assembled the approved smoke package into a dataset.

Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.

Dataset manifest: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`.

Rows total: `1177`.

Boundary: ML training was not started.

Next strict WBS step: `7.6 Stage 7 closeout`.

## ML Approved Registry Stage 7.4 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.

Stage 7.4 is closed: the smoke package is manually approved in `configs/ml_approved_calibration_packages.yaml`.

Registry approved count: `1`.

Approved package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Boundary: ML ingest/dataset builder was not run in this step, and ML training was not started.

Next strict WBS step: `7.5 Run ML ingest`.

## ML Smoke Package Contract Stage 7.3 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.

Stage 7.3 is closed: the smoke package trade log satisfies the ML trade dataset contract and package alignment checks.

Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Contract: `PASS`, rows `1177`, failed rows `0`, missing columns `0`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T183955Z.json`.

Registry remains empty: `approved_packages: []`.

Boundary: no ML training started, no ML ingest started, and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `7.4 Add package to approved registry`.

## ML Smoke Package Stage 7.2 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.

Stage 7.2 is closed: controlled smoke package exists at `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Package is `DRAFT` and `NO_GO_FOR_ML`; it is ready for `7.3` package contract audit, not ML ingest.

Registry remains empty: `approved_packages: []`.

Boundary: no ML training started, no ML ingest started, and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `7.3 Run package contract audit`.

## ML Smoke Window Stage 7.1 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.

Stage 7.1 is closed: the clean smoke window is selected and audited in `configs/ml_smoke_run_manifest.yaml`.

Window: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`.

Real audit: `PASS`, report `reports/qa_gate/ml_smoke_window_manifest_audit_20260623T182159845644Z.json`.

Registry remains empty: `approved_packages: []`.

Boundary: no ML training started, no ML ingest started, and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `7.2 Build test package`.

## ML Alignment Stage 6 Closeout 2026-06-23
Current status: `STAGE_6_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.

Stage 6 is closed: approved package alignment now has checks for run_id, passport context, calibration params, data windows, and admission status.

Current registry remains empty: `approved_packages: []`, approved count `0`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181511Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `7.1 Smoke run`.

## ML Alignment Admission Status Stage 6.5 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.

The admission status auditor exists at `src/mlbotnav/ml_alignment_admission_status_audit.py`.

It fails packages unless registry entry, manifest, calibration package, and audit.md all agree on ML admission.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `121/121 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181123Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.6 Stage 6 closeout`.

## ML Alignment Data Windows Stage 6.4 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.

The data windows alignment auditor exists at `src/mlbotnav/ml_alignment_data_windows_audit.py`.

It fails packages when `manifest.json`, `trade_log.csv`, and package-local `source_reports/oos_report.json` disagree on `data_layer`, `train_start`, `train_end`, `test_start`, or `test_end`.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `115/115 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154759Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.5 Check admission status`.

## ML Alignment Calibration Params Stage 6.3 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.

The calibration params alignment auditor exists at `src/mlbotnav/ml_alignment_calibration_params_audit.py`.

It fails packages when `calibration_package.json.calibration_params`, `trade_log.csv.calibration_params_json`, and package-local `source_reports/oos_report.json.calibration_params` diverge.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `107/107 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154240Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.4 Check data windows`.

## ML Alignment Passport Context Stage 6.2 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.

The passport context alignment auditor exists at `src/mlbotnav/ml_alignment_passport_context_audit.py`.

It fails packages when `manifest.json`, `calibration_package.json`, and `trade_log.csv` disagree on `block_id`, `passport_id`, or `action_id`.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `100/100 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153741Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.3 Check calibration params`.

## ML Alignment Run ID Stage 6.1 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.

The run_id alignment auditor exists at `src/mlbotnav/ml_alignment_run_id_audit.py`.

It fails packages when `manifest.json.run_id`, `calibration_package.json.run_id`, and `trade_log.csv.run_id` do not match.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `94/94 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153207Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.2 Check passport context`.

## ML Stage 5 Closeout 2026-06-23
Current status: `STAGE_5_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.

Stage 5 is closed: ML admission is separated from Optuna through manual registry, source policy, registry reader, dataset builder, and rejection reason log.

Current registry remains empty: `approved_packages: []`, approved count `0`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Final text_guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.

Next strict WBS step: `6.1 Check run_id alignment`.

## ML Rejection Reasons Stage 5.5 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.

The rejection reason log builder exists at `src/mlbotnav/ml_rejection_reason_log.py`.

It writes machine-readable rejection reasons for unsuitable ML admission packages.

Current real reject-log result: `PASS / NO_REJECTIONS`, registry entries `0`, rejections `0`.

Final checks: registry validator `PASS`; reject-log smoke `PASS / NO_REJECTIONS` at `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.

Next strict WBS step: `5.6 Stage 5 closeout`.

## ML Trade Dataset Assembly Stage 5.4 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.

The approved trade dataset builder exists at `src/mlbotnav/ml_approved_trade_dataset_builder.py`.

It builds a combined ML trade dataset only from packages exposed by `ml_approved_package_registry_reader`.

Current real builder result: `PASS / NO_APPROVED_PACKAGES`, approved packages `0`, rows total `0`, dataset path empty.

Final checks: registry validator `PASS`; builder smoke `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.

Next strict WBS step: `5.5 Add rejection reasons`.

## ML Approved Package Registry Reader Stage 5.3 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.

The registry reader exists at `src/mlbotnav/ml_approved_package_registry_reader.py`.

It reads `configs/ml_approved_calibration_packages.yaml`, runs the registry validator, applies source-policy checks, and exposes only approved package metadata for the future dataset assembly step.

Current registry reader result: `PASS`, approved count `0`, packages exposed to ML `0`.

Final checks: registry validator `PASS`, `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.

Next strict WBS step: `5.4 Реализовать сборку ML dataset`.

## ML Ingest Source Policy Stage 5.2 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.

The source-policy guard exists at `src/mlbotnav/ml_ingest_source_policy.py`.

Direct ML ingest from `reports/optuna`, `reports/pipeline`, and `reports/final_review` is denied by policy.

Allowed source classes are the approval registry and `reports/ml_candidates/<run_id>/...`.

Next strict WBS step: `5.3 Реализовать чтение registry`.

## ML Ingest Entry Point Stage 5.1 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.

The current primary ML training ingest entry point is `src/mlbotnav/pipeline_train_eval.py`.

The current orchestrators are `src/mlbotnav/prod_cycle.py`, `src/mlbotnav/stage_ladder.py`, and `src/mlbotnav/adaptive_auto_train.py`.

Current gap: approved registry is not read by training, and package trade logs are not assembled into an ML dataset yet.

Next strict WBS step: `5.2 Запретить прямое чтение Optuna reports`.

## ML Approval Registry Stage 4 Closeout 2026-06-23
Current status: `STAGE_4_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.

Stage 4 Manual ML Approval Registry is closed. The registry exists, the format and bans are recorded, and the validator returns `PASS` on the current empty registry.

Current registry state: `approved_packages: []`, approved count `0`.

No package has `APPROVED_FOR_ML`; ML ingest has not started.

Next strict WBS step: `5.1 Найти текущую точку ML ingest`.

## ML Approval Registry Stage 4.4 Validator 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.

Registry validator exists:
`src/mlbotnav/ml_approval_registry_validator.py`.

Real registry validation is `PASS` with approved count `0`.

Next strict WBS step: `4.5 Закрытие этапа 4`.

## ML Approval Registry Stage 4.3 Bans 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.

Registry bans are recorded in:
`configs/ml_approved_calibration_packages.yaml`.

The registry is still empty: `approved_packages: []`.

Next strict WBS step: `4.4 Сделать validator registry`.

## ML Approval Registry Stage 4.2 Format 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.

Registry format is documented in:
`configs/ml_approved_calibration_packages.yaml`.

The registry is still empty: `approved_packages: []`.

Next strict WBS step: `4.3 Добавить запреты registry`.

## ML Approval Registry Stage 4.1 File 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.

Registry file exists:
`configs/ml_approved_calibration_packages.yaml`.

The registry is intentionally empty: `approved_packages: []`.

Next strict WBS step: `4.2 Описать формат registry`.

## ML Candidate Package Stage 3 Closeout 2026-06-23
Current status: `STAGE_3_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.

Candidate package is complete as a Stage 3 artifact:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`.

The package remains `DRAFT`; `audit.md` says `NO_GO_FOR_ML` until manual registry approval.

Next strict WBS step: `4.1 Создать registry файл`.

## ML Candidate Package Stage 3.6 Package Audit 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.

Package-local audit exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/audit.md`.

Audit says `NO_GO_FOR_ML` because the package remains `DRAFT`; it is ready for manual review, not ML ingest.

Next strict WBS step: `3.7 Закрытие этапа 3`.

## ML Candidate Package Stage 3.5 Manifest 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.

Package-local manifest exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/manifest.json`.

Manifest is `DRAFT`; no ML approval has been granted.

Next strict WBS step: `3.6 Добавить audit.md`.

## ML Candidate Package Stage 3.4 Source Reports 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.

Package-local source report index exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports.json`.

Copied reports:
1. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/oos_report.json`.
2. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/pipeline_report.json`.

Optional `optuna_report.json`: `NOT_PROVIDED`.

Next strict WBS step: `3.5 Добавить manifest.json`.

## ML Candidate Package Stage 3.3 Trade Log 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.

Package-local trade log exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/trade_log.csv`.

Contract validation: `PASS`, `1177` rows, `0` failed rows, `0` missing columns.

Next strict WBS step: `3.4 Добавить исходные отчеты`.

## ML Candidate Package Stage 3.2 Calibration Package 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.

Package file exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/calibration_package.json`.

The package remains `DRAFT`; no ML approval has been granted.

Next strict WBS step: `3.3 Добавить trade_log.csv`.

## ML Candidate Package Stage 3.1 Structure 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.

Builder `src/mlbotnav/ml_candidate_package_builder.py` creates `reports/ml_candidates/<run_id>/` and validates safe `run_id` values.

Created package directory: `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`.

Next strict WBS step: `3.2 Добавить calibration_package.json`.

## ML Trade Dataset Stage 2 Closeout 2026-06-23
Current status: `STAGE_2_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.

Stage 2 is closed: pipeline trade CSV and OOS trade CSV pass `ml_trade_dataset_contract`.

Contract evidence:
1. Pipeline: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133238Z.json`.
2. OOS: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133240Z.json`.

Next strict WBS step: `3.1 Создать структуру пакета`.

## ML Trade Dataset Stage 2.8 OOS CSV 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.

Fresh OOS CSV `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.csv` passed contract validation with `1177` rows, `0` failed rows, and `0` missing columns.

OOS strategy result: `-0.9395906630311424%`, `3` trades, goal pass `false`.

Next strict WBS step: `2.9 Закрытие этапа 2`.

## ML Trade Dataset Stage 2.7 Pipeline CSV 2026-06-23
Current status: `CLOSED_PASS_AFTER_CONTROLLED_TEMP_UNLOCK`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.

Pipeline layer handling is fixed: `pipeline_train_eval.py` accepts `--layer`, uses it in `load_ohlcv_range`, and writes it into the ML run context.

Fresh runtime validation completed through controlled temporary unlock. `reports/pipeline/backtest_trades_SOLUSDT_1m_20260623T132424Z.csv` passed contract validation with `2072` rows, `0` failed rows, and `0` missing columns.

Checks passed: changed module `py_compile PASS`; focused tests `59/59 OK`.

Next strict WBS step: `2.8 Проверить OOS CSV`.

## ML Trade Dataset Stage 2.6 MAE/MFE 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.

MAE/MFE labels are now added to pipeline and OOS trade CSV outputs before write. The shared helper emits `mae_pct` and `mfe_pct` for rows where `side != 0`; non-trade rows stay blank.

Checks passed: changed modules `py_compile PASS`; focused tests `59/59 OK`; `text_guard PASS`.

Next strict WBS step: `2.7 Проверить pipeline CSV`.

## ML Trade Dataset Stage 2.5 Hit Labels 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.

Hit labels are now added to pipeline and OOS trade CSV outputs before write. Labels are derived from `exit_reason`.

Checks passed: changed modules `py_compile PASS`; focused tests `58/58 OK`; `text_guard PASS`.

Next strict WBS step: `2.6 Добавить MAE/MFE`.

## ML Trade Dataset Stage 2.4 Duration Labels 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_4_duration_labels_audit_20260623T125816Z.md`.

Duration labels are now added to pipeline and OOS trade CSV outputs before write. The shared helper emits `bars_in_trade` and `holding_seconds` for rows where `side != 0`.

Checks passed: changed modules `py_compile PASS`; focused tests `57/57 OK`; `text_guard PASS`.

Next strict WBS step: `2.5 Добавить hit labels`.

## ML Trade Dataset Stage 2.1 Run Context 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.

Run-level context is now added to pipeline and OOS trade CSV outputs before write. The shared helper is `src/mlbotnav/ml_trade_dataset_enrichment.py`.

Checks passed: changed modules `py_compile PASS`; focused ML contract/enrichment tests `5/5 OK`; pipeline/backtest focused tests `48/48 OK`.

Next strict WBS step: `2.2 Добавить passport context`.

## ML Trade Dataset Contract Stage 1 Closeout 2026-06-23
Current status: `STAGE_1_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.

Stage 1 is closed: the ML trade dataset contract exists, required columns are fixed, `APPROVED_FOR_ML` admission is documented, and the validator/test/CLI smoke path passes.

Current boundary: the contract is ready, but actual trade CSV enrichment starts next. No larger Optuna-to-ML calibration/OOS route should run before Stage 2 fields are emitted and audited.

Next strict WBS step: `2.1 Добавить run-level context`.

## ML Trade Dataset Contract Step 1.6 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_contract_step_1_6_audit_20260623T122406Z.md`.

The project now has an executable ML trade dataset contract validator at `src/mlbotnav/ml_trade_dataset_contract.py`.

It validates the current contract columns and row rules before a trade CSV can be treated as ML-ready. The validator writes JSON audit reports under `reports/qa_gate/ml_trade_dataset_contract_audit_*.json`.

Checks passed: `py_compile PASS`, focused unittest `4/4 OK`, CLI smoke `PASS`.

Next strict WBS step: `1.7 Закрытие этапа 1`.

## Optuna / ML / Entry / Exit Alignment Audit 2026-06-23
Current status: `PASS_WITH_ML_DATASET_GAPS`.
Artifact: `reports/qa_gate/optuna_ml_entry_exit_alignment_audit_20260623T162411Z.md`.
Action plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Budget: `10-14 hours` engineering work, excluding long runtime waiting.

The current code path correctly carries `calibration_params` from Optuna into train/OOS/backtest and isolates F051 through `F051_BOSDOWN_ALLOW`.

The current report contract is not ML-ready yet: CSV outputs need row-level `action_id`, `passport_id`, `block_id`, `calibration_params_json`, plus trade labels `trade_id`, `bars_in_trade`, `tp_hit`, `sl_hit`, `timeout_hit`, `mae_pct`, and `mfe_pct`.

Clean candle layer for the next larger test is `core` through `2026-05-31`; `2026-06-01` is raw/quarantine only and incomplete.

## Passport Block Registry 2026-06-22T12:57:27Z
`configs/calibration_action_passports.yaml` is the active registry for the new passport-driven calibration route.
Structure is fixed as block ids `B001`, `B002`, ... with Russian block names and technical `block_key`; feature/action passports live inside each block as `F001`, `F002`, ...
Current `B001` is the first passport block with active `RET_N` solo passports `F001-F005`.
Current `B002` is the second passport block `Диапазон свечи High-Low` with active passport `F006`.
`B001_RET_N_TOURNAMENT` remains diagnostic-only after the 2026-06-22 run; baseline mode is solo feature selection only.
Do not use old full/catalog/feature_sweep matrices for new baseline runs unless a passport explicitly migrates that action.

## F006 Passport Run 2026-06-22T13:10:45Z
F006 `hl_spread_1m` is implemented under `B002` with runtime column `F006_HLSPREAD_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `35/35 OK`, py_compile `PASS`.
Clean direct LONG contour result: selected `F006_cmp=-1` (`LESS`), `F006_thr_pct=0.75`; OOS `-6.153363933968025%`, trades `2`, wins `0`; decision `NO_GO`.
Audit artifact: `reports/qa_gate/f006_hl_spread_long_only_audit_20260622T131045Z.json`.
Note: the initial 3-worker pool run had a same-second final_review/top-card artifact mismatch, so use the clean direct contour artifact for the final F006 result.

## F007 Passport Run 2026-06-22T13:33:18Z
F007 `rolling_std_20_1m` is implemented under `B003` with runtime column `F007_RSTD20_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `37/37 OK`, py_compile `PASS`.
Clean direct LONG result: `F007_cmp=1` (`GREATER`), `F007_thr_pct=0.04`; OOS `-1.1459443803135683%`, trades `1`, wins `0`; decision `NO_GO`.
Clean direct SHORT result: `F007_cmp=-1` (`LESS`), `F007_thr_pct=0.34`; OOS `-5.744959575084807%`, trades `3`, wins `0`; decision `NO_GO`.
Audit artifact: `reports/qa_gate/f007_rolling_std20_long_short_audit_20260622T133318Z.json`.

## F008 Passport Run 2026-06-22T13:59:47Z
F008 `atr14_1m` is implemented under `B004` with runtime column `F008_ATR14_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `39/39 OK`, py_compile `PASS`.
Clean direct LONG result: `F008_cmp=-1` (`LESS`), `F008_thr_pct=0.28`; OOS `-1.1459443803135683%`, trades `1`, wins `0`; decision `NO_GO`.
Clean direct SHORT result: `F008_cmp=-1` (`LESS`), `F008_thr_pct=2.33`; OOS `-5.744959575084807%`, trades `3`, wins `0`; decision `NO_GO`.
Audit artifact: `reports/qa_gate/f008_atr14_long_short_audit_20260622T135947Z.json`.

## EMA F009-F011 Passport Run 2026-06-22T14:34:20Z
EMA family passports are implemented under `B005` with runtime columns `F009_EMAGAP_ALLOW`, `F010_EMASLOPE5_ALLOW`, and `F011_EMA200GAP_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `41/41 OK`, py_compile `PASS`.
Clean direct results: F009 LONG `0%/0 trades`; F009 SHORT `-18.167609882040235%/9 trades`; F010 LONG `-29.10662198785241%/10 trades`; F010 SHORT `-18.617757232213172%/5 trades`; F011 LONG `0%/0 trades`; F011 SHORT `0%/0 trades`.
Decision: `NO_GO`, no tradeful non-negative candidate.
Audit artifact: `reports/qa_gate/ema_f009_f011_long_short_audit_20260622T143420Z.json`.

## F012 RSI14 Passport Run 2026-06-22T14:47:50Z
F012 `rsi14_1m` is implemented under `B006` with runtime column `F012_RSI14_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `43/43 OK`, py_compile `PASS`, `text_guard PASS`.
Clean LONG result: `LEVEL/GREATER/level=88`, OOS `0%`, trades `0`, decision `NO_GO`.
SHORT result: `LEVEL/GREATER/level=30`, OOS `-47.5754123715459%`, trades `22`, wins/losses by net return `1/21`, all exits `timeout`, decision `NO_GO`.
Audit artifact: `reports/qa_gate/f012_rsi14_combined_long_short_audit_20260622T144750Z.json`.

## F017/F018 Combined Decision 2026-06-23T08:10:00Z
`F017/F018` split-vs-combined audit finding is closed.
Decision: keep one combined Stochastic K/D passport `F017_F018` with runtime gate `F017_F018_STOCH14_ALLOW`.
Reason: `%K` and `%D` are two lines of one Stochastic indicator; `KD_CROSS` requires both lines in one action grammar.
This is not old Optuna feature mixing and not a block-combo tournament.
Artifact: `reports/qa_gate/f017_f018_combined_decision_audit_20260623T081000Z.md`.
Next strict audit hardening item: explicit active-action filtering so stale `F*_ALLOW` columns cannot affect backtest/OOS.

## Stale Action Column Hardening 2026-06-23T08:20:00Z
Backtest/OOS stale action-column risk is fixed for the passport route.
`run_prob_backtest` now supports `active_entry_action_columns`; Optuna passport search passes the current `passport_mode.action_id`; if only calibration params are available, backtest infers the active action from `Fxxx_*` passport params.
Regression test confirms stale `F038_RANGEPOSE_ALLOW` is ignored when F039 params/action are active.
Validation: changed modules `py_compile PASS`; focused stale/F039 tests `2/2 OK`; project venv `tests.test_backtest_fields tests.test_optuna_search_runtime` `110/110 OK`; `text_guard PASS` `reports/qa_gate/recovery_r5_text_guard_20260623T081355Z.json`.
Artifact: `reports/qa_gate/stale_action_column_hardening_20260623T082000Z.md`.

## Passport Control Index 2026-06-23T08:41:37Z
Active control index created: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_CONTROL_INDEX_RU.md`.
It is a human control panel, not an executable Optuna config.
Accepted architecture: passport meaning docs, compact registry contract, separate executable matrices, and QA artifacts.
Next route proposal: `F051 SHORT` validation is complete and failed promotion; choose the next passport/feature route or define a new validation idea.
Audit: `reports/qa_gate/passport_control_index_audit_20260623T084500Z.md`.

## Active Calibration Source Override
Active calibration-node work now lives in `docs/CALIBRATION_NODE_CURRENT/`.
Use that folder as the next-task source. Do not derive current calibration tasks from old chronology, old journals, old TZ files, or old P20xx/P21xx chains.

## Optuma Bridge Current Step
`docs/CALIBRATION_NODE_CURRENT/TZ_OPTUMA_BRIDGE_CURRENT_2026-06-04_RU.md` is the active short rule for current Optuma repairs.
Completed Step 1: `calibration_params` selected by Optuna are now passed into train/OOS and saved in reports/model payload.
Completed Steps 2-5: `volume_flow`, `density_profile`, `structure_ta` thresholds, and FIBO profile wiring are repaired against the declared calibration params.
Completed pattern repair: `pattern_structure_volume_entry` adds classic figure-pattern runtime features and the `pattern + structure_ta + volume_flow` entry bundle.
Validation: focused tests `97/97 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS` for 7 YAML matrices x 2 contours x 3 grid presets; latest `text_guard PASS`.
Dry command gate passed, then `pattern long_only narrow` completed OK under CPU limit.
`pattern long_only medium` completed launcher/workers OK but exceeded the CPU limit once: max CPU `97%` vs limit `85%`.
User clarified CPU policy: short spikes are acceptable; sustained `>85%` for `2-5` minutes means reduce profile and continue.
`pattern` block full runtime is now closed through `long_only` and `short_only`, each `narrow/medium/wide`.
Result: `BLOCK_COMPLETE_RUNTIME_OK_NO_CANDIDATE`; best `long_only narrow`, `0%`, trades `0`; block artifact `reports/qa_gate/pattern_block06_full_closeout_20260604T103051Z.json`.
Readable report: `reports/qa_gate/pattern_block06_human_readable_20260604T103051Z_RU.md`.
New finding: search-level candidates include calibrated params, but final fallback `best_oos` records `selected_calibration_params={}`. Treat this as the next calibration-node repair before relying on parameter-specific block06 replay.
Repair completed UTC `2026-06-04T10:43:12Z`: `adaptive_auto_train.py` now prefers full `top_candidates` with `calibration_params` over lite candidates. Focused tests `80/80 OK`; artifact `reports/qa_gate/pattern_fallback_calibration_params_fix_20260604T104312Z_RU.md`. Next step is rerun/replay block06 so new runtime artifacts include `selected_calibration_params`.

## APTuna Block Alignment Audit 2026-06-03T16:48:08Z
Artifact: `reports/qa_gate/aptuna_block_alignment_audit_20260603T164808Z.json`.
Status: `PASS`, `issues=0`, `blockers=0`.
All 6 blocks match between calibrated blocks and APTuna matrices: `price_volatility`, `trend_momentum`, `volume_flow`, `density_profile`, `structure_ta`, `pattern`.
Full matrix contains `68` feature rows (`56` calibratable, `12` fixed) and `20/20` calibratable hypothesis rows.
Catalog block matrices compile for `long_only`/`short_only` and `narrow`/`medium`/`wide`; APTuna uses the matrix path through `MLBOTNAV_CALIBRATION_MATRIX_PATH`.
Next strict sequential step remains `H003` matrix generation/compile.

## Current Sweep State 2026-06-03T13:16:59Z
Active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_HYPOTHESIS_FEATURE_SWEEP_2026-06-03_RU.md`.
Slot `H001` is complete: `long_only` and `short_only` each ran `narrow/medium/wide` with launcher `OK`, workers `3/3 exit_code=0`, no infra failure.
H001 best long: `medium long_only`, `-8.650246602184342%`, trades `4`.
H001 best short: `narrow short_only`, `0%`, trades `0`.
Candidate decision: `NO_CANDIDATE`; runtime/grid coverage is OK.
Closeout artifact: `reports/qa_gate/h001_slot_closeout_20260603T131659Z.json`.
Sweep table: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`, H001 status `slot_complete_runtime_ok_no_candidate_next_H002`.
Next strict action: `H002` matrix compile, then `H002 long_only` full stack.

## Human-Readable Sweep Format 2026-06-03T13:30:00Z
Accepted format: one parent slot plus two child stack cards.
Example: `H001` is the parent feature slot, `H001-LONG` is the long-only stack, `H001-SHORT` is the short-only stack, and `H001-SLOT` is the closeout.
`H002` remains the next feature slot, not a short-side alias.
Readable reports should be in Russian and include block/tool meaning, technical name, calibrated params, ranges, all grid results, best long/short, decision, and artifact path.
Heading correction: each slot heading must be short and use exact RU names from `configs/features_block.yaml`, for example `H003 | Доходность за 6 баров`; H003 is `kind=feature_row`, not a hypothesis.
Full RU names catalog: `docs/CALIBRATION_NODE_CURRENT/RU_NAMES_CATALOG_2026-06-03.md`.
Post-format-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T160749Z.json`.
Current readable report file: `reports/optuna_catalog/index/hypothesis_feature_sweep_human_ru.md`.

## Current Sweep State 2026-06-03T15:41:33Z
Slot `H002` is complete: `long_only` and `short_only` each ran `narrow/medium/wide` with launcher `OK`, workers `3/3 exit_code=0`, no infra failure.
H002 best long: `wide long_only`, `-8.650246602184342%`, trades `4`.
H002 best short: `narrow/medium short_only`, `-0.2662724500743341%`, trades `2`.
Candidate decision: `NO_CANDIDATE`; runtime/grid coverage is OK.
Closeout artifact: `reports/qa_gate/h002_slot_closeout_20260603T154133Z.json`.
Sweep table: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`, H002 status `slot_complete_runtime_ok_no_candidate_next_H003`.
Next strict action: `H003` matrix compile, then `H003 long_only` full stack.

## Current Calibration Node Update 2026-06-03T11:28:24Z
`structure_ta` is closed as `CLOSED_RUNTIME_OK` in the active current folder.
Best block result: `structure_ta wide long_only`, OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production because train gate failed.
The failed first `wide short_only` attempt was infrastructure-only: one worker crashed on empty/unreadable OOS report JSON. The code now uses `_read_json_report_with_retry` for OOS report reads; retest returned launcher `OK`, workers `3/3 exit_code=0`, best OOS `0%`, trades `0`.
`pattern` is closed as `CLOSED_RUNTIME_OK`: `narrow/medium/wide` x `long_only/short_only` all returned launcher `OK` with workers `3/3 exit_code=0`.
Best `pattern` result: `wide long_only`, OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production because train gate failed.
Closeout artifact: `reports/qa_gate/calibration_node_pattern_closeout_20260603T112654Z.json`.
Checks after close: focused tests `83/83 OK`, text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T112958Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T112818Z.json`), `pip check PASS`.
Next active command is not production/unfreeze; it requires a separate new TZ or GO package.

## Current Sequential Sweep Update 2026-06-03T12:18:33Z
Current `TOP_EXPERIMENTAL` candidate is paused by user request.
Active work is now sequential min->max verification for every hypothesis/feature slot.
New active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_HYPOTHESIS_FEATURE_SWEEP_2026-06-03_RU.md`.
Inventory result: `69` logical slots (`H000` baseline/control plus `H001-H068` feature rows), `56` calibratable and `13` non-calibrated including control.
Artifacts:
1. `reports/qa_gate/hypothesis_feature_sweep_inventory_20260603T121643Z.json`
2. `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`
3. `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`
4. `reports/qa_gate/h001_feature_sweep_matrix_compile_20260603T121833Z.json`

`H001 narrow long_only` completed: launcher `OK`, workers `3/3 exit_code=0`, best OOS `-30.924389997582892%`, trades `13`, class `negative_runtime_ok`.
Artifact: `reports/qa_gate/h001_narrow_long_only_20260603T122520Z.json`.
TZ corrected: long and short are separate stacks; each stack runs `narrow -> medium -> wide`; standard profile is `3x3/9` with trials/timeouts `narrow=60/300`, `medium=120/600`, `wide=180/900`.
`H001 narrow short_only` completed: launcher `OK`, workers `3/3 exit_code=0`, best OOS `+0.2544418318741748%`, trades `1`, class `provisional_plus_goal_fail`, not candidate.
Artifact: `reports/qa_gate/h001_narrow_short_only_20260603T124931Z.json`.
Next active command: `H001 medium long_only` 1d->1d, then record the result and move to `H001 medium short_only`.

## Works
1. Optuna/APTuna runtime contour is usable.
2. Long/short split works.
3. Process-pool launcher works.
4. Temporary readiness unlock works for calibration.
5. Preflight and artifact emission work.
6. Package-level `text_guard`, readiness check, `pip check`, and encoding audit passed after `Package A`.
7. Existing Optuna coverage contour supports linked profile coverage audits.
8. Catalog folders exist under `reports/optuna_catalog/`.

## Does Not Work For Launch Yet
1. No portable launch candidate exists.
2. Prior cycle-2 local candidate failed mandatory forward stability.
3. `Package A` V3 found no candidate.
4. Production launch is blocked by current `NO_GO` and freeze.
5. Full catalog runner/index emission is not implemented yet for the new catalog workflow.
6. A positive catalog result still needs forward validation before production.

## Checked
1. `P2016`: forward stability final fail after UTC close.
2. `P2017`: final quality decision switched to `NO_GO`.
3. `P2022`: `Package A long_only` completed.
4. `P2023`: `Package A short_only` completed.
5. `P2024`: unified triage returned `NO_CANDIDATE`.
6. `P2025`: post-audit returned `PASS`.
7. `P2026`: full calibration catalog checkpoint created.
8. `P2028`: first catalog task fixed as `1d -> 1d` calibration smoke strategy; no runtime run was launched.
9. `P2029`: ordered execution roadmap fixed; current pointer is Step 1 read-only wiring inventory.
10. `P2030`: Step 1 wiring inventory completed with `PASS`; current pointer moved to Step 2.
11. `P2031`: Step 1 post-sync audit passed; readiness freeze preserved.
12. `P2032`: Step 2 1d->1d smoke command set completed with `PASS`; current pointer moved to Step 3.
13. `P2033`: Step 2 post-sync audit passed; readiness freeze preserved.
14. `P2034`: Step 3 smoke preflight completed with `PASS`.
15. `P2035`: Step 4 long_only smoke completed `NEUTRAL_NO_TRADE`.
16. `P2036`: Step 5 short_only smoke completed `PROVISIONAL_PLUS_GOAL_FAIL`.
17. `P2037`: Step 6 smoke triage returned `GO_TO_MEDIUM_WORK`; current pointer moved to Step 7.
18. `P2038`: Step 6 post-sync audit passed; readiness freeze preserved.
19. `P2039`: Step 7 medium command set completed with `PASS`; current pointer remains Step 7 runtime.
20. `P2040`: Step 7 medium long_only completed as `negative`.
21. `P2041`: Step 7 medium short_only completed as `negative`.
22. `P2042`: Step 7 medium triage returned `GO_TO_WIDE_BATTLE`; current pointer moved to Step 8.
23. `P2043`: Step 7 medium post-sync audit passed; readiness freeze preserved.
24. `P2044`: Step 8 wide command set completed with `PASS`; current pointer remains Step 8 runtime.
25. `P2045`: Step 8 wide long_only completed as `negative`.
26. `P2046`: Step 8 wide short_only completed as `negative`.
27. `P2047`: Step 8 wide triage returned `GO_TO_CATALOG_RANKING`.
28. `P2048`: Step 9 catalog ranking returned `NO_FORWARD_CANDIDATE`.
29. `P2049`: Step 10/11 boundary returned `NO_FORWARD_CANDIDATE_NO_PRODUCTION_GO`.
30. `P2050`: full catalog closeout post-sync audit passed; readiness freeze preserved.
31. `P2051`: block-level catalog cycle setup completed with `PASS`; 6 block-isolated matrices generated and compiled.
32. `P2052`: block01 `price_volatility` narrow command set completed with `PASS`; current pointer is block01 narrow runtime.
33. `P2055`: block01 narrow triage returned `GO_TO_BLOCK01_MEDIUM`.
34. `P2059`: block01 medium triage returned `GO_TO_BLOCK01_WIDE`.
35. `P2063`: block01 full triage returned `GO_TO_BLOCK02_TREND_MOMENTUM`.
36. `P2064`: block01 post-sync audit passed; readiness freeze preserved.
37. `P2065`: block02 `trend_momentum` narrow command set completed with `PASS`.
38. `P2068`: block02 narrow triage returned `GO_TO_BLOCK02_MEDIUM`.
39. `P2069`: block02 `trend_momentum` medium command set completed with `PASS`.
40. `P2072`: block02 medium triage returned `GO_TO_BLOCK02_WIDE`.
41. `P2073`: block02 `trend_momentum` wide command set completed with `PASS`.
42. `P2076`: block02 full triage returned `GO_TO_BLOCK03_VOLUME_FLOW`.
43. `P2077`: block02 post-sync audit passed; readiness freeze preserved.
44. `P2078`: block03 `volume_flow` narrow command set completed with `PASS`.
45. `P2081`: block03 narrow triage returned `GO_TO_BLOCK03_MEDIUM_WITH_FORWARD_CANDIDATE_OBSERVED`.
46. `P2082`: block03 `volume_flow` medium command set completed with `PASS`.
47. `P2085`: block03 medium triage returned `GO_TO_BLOCK03_WIDE_WITH_NARROW_FORWARD_CANDIDATE_PRESERVED`.
48. `P2086`: block03 `volume_flow` wide command set completed with `PASS`.
49. `P2089`: block03 full triage returned `GO_TO_BLOCK04_DENSITY_PROFILE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
50. `P2090`: block03 post-sync audit passed; readiness freeze preserved.
51. `P2091`: block04 `density_profile` narrow command set completed with `PASS`.
52. `P2094`: block04 narrow triage returned `GO_TO_BLOCK04_MEDIUM_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
53. `P2095`: block04 `density_profile` medium command set completed with `PASS`.
54. `P2098`: block04 medium triage returned `GO_TO_BLOCK04_WIDE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
55. `P2099`: block04 `density_profile` wide command set completed with `PASS`.
56. `P2102`: block04 full triage returned `GO_TO_BLOCK05_STRUCTURE_TA_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
57. `P2103`: block04 post-sync audit passed; readiness freeze preserved.
58. `P2104`: block05 `structure_ta` narrow command set completed with `PASS`.
59. `P2107`: block05 narrow triage returned `GO_TO_BLOCK05_MEDIUM_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
60. `P2108`: block05 `structure_ta` medium command set completed with `PASS`.
61. `P2111`: block05 medium triage returned `GO_TO_BLOCK05_WIDE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
62. `P2112`: block05 `structure_ta` wide command set completed with `PASS`.
63. `P2115`: block05 full triage returned `GO_TO_BLOCK06_PATTERN_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
64. `P2116`: block05 post-sync audit passed; readiness freeze preserved.
65. `P2117`: block06 `pattern` narrow command set completed with `PASS`.
66. `P2120`: block06 narrow triage returned `GO_TO_BLOCK06_MEDIUM_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
67. `P2121`: block06 `pattern` medium command set completed with `PASS`.
68. `P2124`: block06 medium triage returned `GO_TO_BLOCK06_WIDE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
69. `P2125`: block06 `pattern` wide command set completed with `PASS`.
70. `P2128`: block06 full triage returned `GO_TO_BLOCK_LEVEL_CATALOG_RANKING_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
71. `P2129`: block06 post-sync audit passed; readiness freeze preserved.
72. `P2130`: block-level catalog ranking returned `FORWARD_CANDIDATE_EXISTS_RUN_FORWARD_STABILITY`.
73. `P2131`: forward boundary confirms production is still blocked; F1/F2 required.
74. `P2132`: block-level catalog closeout post-sync audit passed; readiness freeze preserved.
75. `P2133`: exact F1/F2 command set prepared for candidate `P2079`; command syntax dry-run passed for 3x3 contour, but runtime is `BLOCKED_BY_DATA`.
76. `P2134`: repeated F1/F2 data preflight gate; status `BLOCKED_BY_UTC_CLOSE_AND_DATA`.
77. `P2137`: previous V3 TZ pointer restored. Exact V3 `Package B` slot definition is the unclosed manual branch; P2079 forward automation is paused.
78. `P2138`: previous TZ recovery post-sync audit passed; `text_guard`, readiness, and `pip check` are clean and freeze remains ON.
79. `P2139`: dated Package B step chain fixed. Chain starts UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`, from V3 TZ section 7 (`2026-06-02T06:52:50Z`).
80. `P2139 independent cross-check`: agent and local audit agree route is correct with boundary: next step is read-only `P2140 inventory`, not runtime or P2079 forward.
81. `P2140`: Step 1 inventory completed with `PASS`; current V3 Package B slots/matrices/command set are not defined, old Package B artifacts are historical V2/strict only.
82. `P2141`: Step 2 exact V3 Package B slots completed with `PASS`; slots B-H1 trend/momentum, B-H2 range/reversion, B-H3 flow/absorption are fixed; runtime still blocked.
83. `P2142`: Step 3 matrix slices and command-set/dry-run completed with `PASS`; 4 Package B matrix slices generated, 18 exact commands emitted, dry-run/preflight `18/18 PASS`; next is `P2143 long_only` runtime only.
84. `P2143`: Step 4 Package B `long_only` runtime completed with `PASS`; runtime `9/9 PASS`, catalog class `neutral`, accepted positive candidates `0`; next is `P2144 short_only` runtime only.
85. `P2144`: Step 5 Package B `short_only` runtime completed with `PASS`; runtime `9/9 PASS`, catalog class `neutral`, accepted positive candidates `0`; next is `P2145` unified Package B triage only.
86. `P2145`: Step 6 Package B unified triage completed as `NO_CANDIDATE`; totals positive `0`, neutral `18`, negative `0`, infra_fail `0`; next is `P2146` post-sync audit/docs sync.
87. `P2146`: Step 7 Package B post-sync audit completed with `PASS`; text_guard/readiness/pip/artifact parse clean, readiness freeze preserved; next is `P2147` transition decision.
88. `P2147`: Step 8 Package B closeout transition completed with `PASS`; decision `GO_TO_FINAL_V3_NO_GO_DECISION_PACKAGE`; no next runtime allowed from Package B.
89. `P2148`: final V3 `NO_GO` decision package completed; launch `NO_GO`, no production-ready candidate, launch/unfreeze blocked; next is `P2149` final post-sync audit.
90. `P2149`: final V3 `NO_GO` post-sync audit completed with `PASS`; V3 chain closed, readiness freeze preserved.
91. `P2150`: post-V3 catalog/forward boundary selected P2079 F1 data gate after UTC close; status `ROUTE_SELECTED_WAIT_UTC_CLOSE`; no ingest, preflight, runtime, production, or unfreeze allowed now.
92. `P2151`: P2079 F1 data gate pre-close check completed as `BLOCKED_BY_UTC_CLOSE`; next `P2152` waits until `2026-06-03T00:00:00Z`.
93. `P2152`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2153` waits until `2026-06-03T00:00:00Z`.
94. `P2153`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2154` waits until `2026-06-03T00:00:00Z`.
95. `P2154`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2155` waits until `2026-06-03T00:00:00Z`.
96. `P2155`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2156` waits until `2026-06-03T00:00:00Z`.
97. `P2155` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
98. `P2156`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2157` waits until `2026-06-03T00:00:00Z`.
99. `P2156` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
100. `P2157`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2158` waits until `2026-06-03T00:00:00Z`.
101. `P2157` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
102. `P2158`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2159` waits until `2026-06-03T00:00:00Z`.
103. `P2158` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
104. `P2159`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2160` waits until `2026-06-03T00:00:00Z`.
105. `P2159` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
106. `P2160`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2161` waits until `2026-06-03T00:00:00Z`.
107. `P2160` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
108. `P2161`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2162` waits until `2026-06-03T00:00:00Z`.
109. `P2161` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
110. `P2162`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2163` waits until `2026-06-03T00:00:00Z`.
111. `P2162` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
112. `P2163`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2164` waits until `2026-06-03T00:00:00Z`.
113. `P2163` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
114. `P2164`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2165` waits until `2026-06-03T00:00:00Z`.
115. `P2164` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
116. `P2165`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2166` waits until `2026-06-03T00:00:00Z`.
117. `P2165` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
118. `P2166`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2167` waits until `2026-06-03T00:00:00Z`.
119. `P2166` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
120. `P2167`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2168` waits until `2026-06-03T00:00:00Z`.
121. `P2167` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
122. `P2168`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2169` waits until `2026-06-03T00:00:00Z`.
123. `P2168` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
124. `P2169`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2170` waits until `2026-06-03T00:00:00Z`.
125. `P2169` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
126. `P2170`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2171` waits until `2026-06-03T00:00:00Z`.
127. `P2170` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
128. `P2171`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2172` waits until `2026-06-03T00:00:00Z`.
129. `P2171` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
130. `P2172`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2173` waits until `2026-06-03T00:00:00Z`.
131. `P2172` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
132. `P2173`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2174` waits until `2026-06-03T00:00:00Z`.
133. `P2173` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
134. `P2174`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2175` waits until `2026-06-03T00:00:00Z`.
135. `P2174` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
136. `P2175`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2176` waits until `2026-06-03T00:00:00Z`.
137. `P2175` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
138. `P2176`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2177` waits until `2026-06-03T00:00:00Z`.
139. `P2176` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
140. `P2177`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2178` waits until `2026-06-03T00:00:00Z`.
141. `P2177` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
142. `P2178`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2179` waits until `2026-06-03T00:00:00Z`.
143. `P2178` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
144. `P2179`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2180` waits until `2026-06-03T00:00:00Z`.
145. `P2179` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
146. `P2180`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2181` waits until `2026-06-03T00:00:00Z`.
147. `P2180` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
148. `P2181`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2182` waits until `2026-06-03T00:00:00Z`.
149. `P2181` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
150. `P2182`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2183` waits until `2026-06-03T00:00:00Z`.
151. `P2182` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
152. `P2183`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2184` waits until `2026-06-03T00:00:00Z`.
153. `P2183` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
154. `P2184`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2185` waits until `2026-06-03T00:00:00Z`.
155. `P2184` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
156. `P2185`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2186` waits until `2026-06-03T00:00:00Z`.
157. `P2185` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
158. `P2186`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2187` waits until `2026-06-03T00:00:00Z`.
159. `P2186` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
160. `P2187`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2188` waits until `2026-06-03T00:00:00Z`.
161. `P2187` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
162. `P2188`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2189` waits until `2026-06-03T00:00:00Z`.
163. `P2188` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
164. `P2189`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2190` waits until `2026-06-03T00:00:00Z`.
165. `P2189` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
166. `P2190`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2191` waits until `2026-06-03T00:00:00Z`.
167. `P2190` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
168. `P2191`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2192` waits until `2026-06-03T00:00:00Z`.
169. `P2191` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
170. `P2192`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2193` waits until `2026-06-03T00:00:00Z`.
171. `P2192` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
172. `P2193`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2194` waits until `2026-06-03T00:00:00Z`.
173. `P2193` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
174. `P2194`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2195` waits until `2026-06-03T00:00:00Z`.
175. `P2194` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
176. `P2195`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2196` waits until `2026-06-03T00:00:00Z`.
177. `P2195` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
178. Quick structural audit completed as `PASS_WITH_ROUTE_CORRECTION`: framework/catalog validation is not blocked by P2079 UTC-close gate; 68 feature rows, 6 blocks, 27 linked profiles, 3x3/9 support, and block catalog `36/36 runtime OK`.
179. Structural big-window command-set/dry-run completed as `PASS`: artifact `reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json`, raw policy preflight `PASS`, compile/dry-run `36/36 PASS`.
180. Structural big-window narrow runtime started, then stopped by user request: artifact `reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`, status `STOPPED_BY_USER_AND_FREEZE_RESTORED`; completed launcher commands `3`, stopped launcher commands `1`, positive candidates `0`.

## Recent Results
1. `Package A candidate_count=0`.
2. Best tradeful branch inside `Package A`: `short_only`, `W2`, `A-H1`, `oos=-4.4808%`, `trades=1`.
3. `readiness`: `project_ready=false`, `enforce_freeze=true`.
4. `pip check`: `No broken requirements found.`
5. New active catalog TZ:
   `docs/TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md`.
6. Post-sync audit after catalog checkpoint: `PASS`.
   Artifact: `reports/qa_gate/p2027_optuna_full_calibration_catalog_post_sync_audit_20260602T083823Z.json`.
7. Step 1 wiring inventory: `PASS`.
   Artifact: `reports/optuna_catalog/index/p2030_step1_wiring_inventory_20260602T092159Z.json`.
   Summary: 6 enabled blocks, 68 feature rows matched runtime columns, 56 tunable feature rows, 20 tunable hypothesis rows, 27/27 profiles linked, profile issues `0`.
   Long/short compiled hypothesis counts: long_only `19`, short_only `17`.
8. Step 2 smoke command set: `PASS`.
   Artifact: `reports/optuna_catalog/index/p2032_step2_1d1d_smoke_command_set_20260602T092710Z.json`.
   Fixed command profile: train `2026-05-31`, test `2026-06-01`, matrix `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=narrow`, `ForceProfileEdgeCoverage=on`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, total workers `9`, trials `60`, timeout `300`.
9. Step 3 smoke preflight: `PASS`.
   Artifact: `reports/qa_gate/p2034_step3_smoke_preflight_20260602T093214Z.json`.
10. Step 4 long_only smoke:
   Runtime `OK`, workers `3/3`, catalog class `neutral`, best OOS `0.0%`, trades `0`.
   Artifact: `reports/optuna_catalog/neutral/p2035_step4_long_only_1d1d_smoke_neutral_20260602T093324Z.json`.
11. Step 5 short_only smoke:
   Runtime `OK`, workers `3/3`, catalog class `neutral`, best OOS `+0.2544%`, trades `1`, but `goal_pass=false`.
   Artifact: `reports/optuna_catalog/neutral/p2036_step5_short_only_1d1d_smoke_provisional_plus_goal_fail_20260602T093604Z.json`.
12. Step 6 smoke triage:
   Decision `GO_TO_MEDIUM_WORK`, accepted positive candidates `0`, provisional positive OOS branches `1`.
   Artifact: `reports/qa_gate/p2037_step6_1d1d_smoke_triage_20260602T093704Z.json`.
13. Step 7 medium command set:
   Artifact: `reports/optuna_catalog/index/p2039_step7_medium_command_set_20260602T095335Z.json`.
   Fixed profile: train `2026-05-31`, test `2026-06-01`, matrix `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=medium`, `ForceProfileEdgeCoverage=on`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, total workers `9`, trials `120`, timeout `600`.
   Compile/dry-run: long_only and short_only `PASS`.
14. Step 7 medium runtime/triage:
   long_only catalog class `negative`, best OOS `-6.9497%`, trades `1`, `goal_pass=false`.
   short_only catalog class `negative`, best OOS `-0.6217%`, trades `1`, `goal_pass=false`.
   Accepted positive candidates `0`; decision `GO_TO_WIDE_BATTLE`.
   Triage artifact: `reports/qa_gate/p2042_step7_medium_triage_20260602T100020Z.json`.
15. Step 7 medium post-sync audit:
   Artifact: `reports/qa_gate/p2043_step7_medium_post_sync_audit_20260602T100235Z.json`.
   JSON parse, compileall, text_guard, readiness, and pip check all `PASS`; freeze preserved.
16. Step 8 wide command set:
   Artifact: `reports/optuna_catalog/index/p2044_step8_wide_command_set_20260602T100351Z.json`.
   Fixed profile: train `2026-05-31`, test `2026-06-01`, matrix `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=wide`, `ForceProfileEdgeCoverage=on`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, total workers `9`, trials `180`, timeout `900`.
   Compile/dry-run: long_only and short_only `PASS`.
17. Step 8-11 final catalog result:
   wide long_only `negative`, best OOS `-4.9783%`, trades `1`, `goal_pass=false`.
   wide short_only `negative`, best OOS `-0.2663%`, trades `2`, `goal_pass=false`.
   Catalog ranking totals: positive `0`, neutral `2`, negative `4`, infra_fail `0`.
   Forward stability is not runnable because `candidate_for_forward=0`.
   Production/unfreeze remains blocked.
18. Closeout post-sync audit:
   Artifact: `reports/qa_gate/p2050_full_catalog_closeout_post_sync_audit_20260602T101019Z.json`.
   JSON parse, compileall, text_guard, readiness, and pip check all `PASS`; freeze preserved.
19. New block-level catalog cycle:
   Generated 6 block-isolated matrices under `configs/calibration_matrices/catalog_blocks/`.
   First block: `price_volatility`.
   `P2052` command set fixed: narrow grid, 3x3 workers, total trials `60`, timeout `300`, long/short dry-run `PASS`.
20. Block01 `price_volatility` result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
   Decision: `GO_TO_BLOCK02_TREND_MOMENTUM`.
   Post-sync audit `P2064`: `PASS`, freeze preserved.
21. Block02 `trend_momentum` narrow result:
   long_only catalog class `neutral`, best OOS `0.0%`, trades `0`, with negative tradeful branch `-15.3557%`.
   short_only catalog class `negative`, best OOS `-41.4626%`, trades `15`.
   Accepted positive candidates `0`; decision `GO_TO_BLOCK02_MEDIUM`.
22. Block02 `trend_momentum` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
   Decision: `GO_TO_BLOCK03_VOLUME_FLOW`.
   Post-sync audit `P2077`: `PASS`, freeze preserved.
23. Block03 `volume_flow` narrow result:
   long_only catalog class `positive`, best OOS `+1.9186%`, trades `1`, `goal_pass=true`.
   short_only catalog class `negative`, best OOS `-13.3138%`, trades `4`, `goal_pass=false`.
   Totals: positive `1`, neutral `0`, negative `1`, infra_fail `0`, candidate_for_forward `1`.
24. V3 Package B command set:
   `P2142` completed UTC `2026-06-02T13:05:59Z`, local `2026-06-02 18:05:59 +05:00`.
   Artifact: `reports/qa_gate/p2142_v3_package_b_command_set_20260602T130559Z.json`.
   Matrix slices: `configs/calibration_matrices/optuna_v3_package_b_bh1_long.yaml`, `configs/calibration_matrices/optuna_v3_package_b_bh1_short.yaml`, `configs/calibration_matrices/optuna_v3_package_b_bh2.yaml`, `configs/calibration_matrices/optuna_v3_package_b_bh3.yaml`.
   Dry-run/preflight: `18/18 PASS`; runtime was not executed in `P2142`.
25. V3 Package B `long_only` runtime:
   `P2143` completed UTC `2026-06-02T13:15:35Z`, local `2026-06-02 18:15:35 +05:00`.
   Runtime summary: `reports/qa_gate/p2143_v3_package_b_long_only_summary_20260602T131035Z.json`.
   Catalog artifact: `reports/optuna_catalog/neutral/p2143_v3_package_b_long_only_neutral_20260602T131535Z.json`.
   Runtime `9/9 PASS`; catalog class `neutral`; accepted positive candidates `0`; best tradeful OOS `-1.6687%`.
26. V3 Package B `short_only` runtime:
   `P2144` completed UTC `2026-06-02T13:24:20Z`, local `2026-06-02 18:24:20 +05:00`.
   Runtime summary: `reports/qa_gate/p2144_v3_package_b_short_only_summary_20260602T132020Z.json`.
   Catalog artifact: `reports/optuna_catalog/neutral/p2144_v3_package_b_short_only_neutral_20260602T132420Z.json`.
   Runtime `9/9 PASS`; catalog class `neutral`; accepted positive candidates `0`; best tradeful OOS `-1.6689%`.
27. V3 Package B unified triage:
   `P2145` completed UTC `2026-06-02T13:28:30Z`, local `2026-06-02 18:28:30 +05:00`.
   Artifact: `reports/qa_gate/p2145_v3_package_b_unified_triage_20260602T132830Z.json`.
   Result: `NO_CANDIDATE`; totals positive `0`, neutral `18`, negative `0`, infra_fail `0`; best tradeful OOS `-1.6687%`.
28. V3 Package B post-sync audit:
   `P2146` completed UTC `2026-06-02T13:30:21Z`, local `2026-06-02 18:30:21 +05:00`.
   Artifact: `reports/qa_gate/p2146_v3_package_b_post_sync_audit_20260602T133021Z.json`.
   Checks: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2145 artifact parse `PASS`.
29. V3 Package B closeout transition:
   `P2147` completed UTC `2026-06-02T13:33:30Z`, local `2026-06-02 18:33:30 +05:00`.
   Artifact: `reports/qa_gate/p2147_v3_package_b_closeout_transition_20260602T133330Z.json`.
   Decision: `GO_TO_FINAL_V3_NO_GO_DECISION_PACKAGE`; Package A and Package B both closed with no accepted candidate.
30. V3 final decision:
   `P2148` completed UTC `2026-06-02T13:36:00Z`, local `2026-06-02 18:36:00 +05:00`.
   Artifact: `reports/qa_gate/p2148_v3_final_no_go_decision_20260602T133600Z.json`.
   Decision: final launch `NO_GO`; no production-ready candidate; launch and unfreeze blocked.
31. V3 final post-sync audit:
   `P2149` completed UTC `2026-06-02T13:38:45Z`, local `2026-06-02 18:38:45 +05:00`.
   Artifact: `reports/qa_gate/p2149_v3_final_no_go_post_sync_audit_20260602T133845Z.json`.
   Checks: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2148 artifact parse `PASS`; V3 chain closed.
32. Post-V3 catalog/forward boundary:
   `P2150` completed UTC `2026-06-02T13:41:50Z`, local `2026-06-02 18:41:50 +05:00`.
   Artifact: `reports/qa_gate/p2150_post_v3_catalog_forward_boundary_20260602T134150Z.json`.
   Result: route selected to P2079 F1 data gate after `2026-06-03T00:00:00Z`; runtime remains blocked.
33. P2079 F1 data gate pre-close check:
   `P2151` completed UTC `2026-06-02T14:17:11Z`, local `2026-06-02 19:17:11 +05:00`.
   Artifact: `reports/qa_gate/p2151_p2079_f1_data_gate_preclose_check_20260602T141711Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
34. P2079 F1 UTC-close recheck:
   `P2152` completed UTC `2026-06-02T14:20:42Z`, local `2026-06-02 19:20:42 +05:00`.
   Artifact: `reports/qa_gate/p2152_p2079_f1_data_gate_utc_close_recheck_20260602T142042Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
35. P2079 F1 UTC-close recheck:
   `P2153` completed UTC `2026-06-02T14:23:19Z`, local `2026-06-02 19:23:19 +05:00`.
   Artifact: `reports/qa_gate/p2153_p2079_f1_data_gate_utc_close_recheck_20260602T142319Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
36. P2079 F1 UTC-close recheck:
   `P2154` completed UTC `2026-06-02T14:25:53Z`, local `2026-06-02 19:25:53 +05:00`.
   Artifact: `reports/qa_gate/p2154_p2079_f1_data_gate_utc_close_recheck_20260602T142553Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
37. P2079 F1 UTC-close recheck:
   `P2155` completed UTC `2026-06-02T14:29:20Z`, local `2026-06-02 19:29:20 +05:00`.
   Artifact: `reports/qa_gate/p2155_p2079_f1_data_gate_utc_close_recheck_20260602T142920Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2156` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143136Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T143136Z.json`), `pip check PASS`, artifact parse `PASS`.
38. P2079 F1 UTC-close recheck:
   `P2156` completed UTC `2026-06-02T14:33:08Z`, local `2026-06-02 19:33:08 +05:00`.
   Artifact: `reports/qa_gate/p2156_p2079_f1_data_gate_utc_close_recheck_20260602T143308Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2157` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143445Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T143445Z.json`), `pip check PASS`, artifact parse `PASS`.
39. P2079 F1 UTC-close recheck:
   `P2157` completed UTC `2026-06-02T14:36:25Z`, local `2026-06-02 19:36:25 +05:00`.
   Artifact: `reports/qa_gate/p2157_p2079_f1_data_gate_utc_close_recheck_20260602T143625Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2158` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143926Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T143925Z.json`), `pip check PASS`, artifact parse `PASS`.
40. P2079 F1 UTC-close recheck:
   `P2158` completed UTC `2026-06-02T14:40:30Z`, local `2026-06-02 19:40:30 +05:00`.
   Artifact: `reports/qa_gate/p2158_p2079_f1_data_gate_utc_close_recheck_20260602T144030Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2159` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144209Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T144207Z.json`), `pip check PASS`, artifact parse `PASS`.
41. P2079 F1 UTC-close recheck:
   `P2159` completed UTC `2026-06-02T14:43:17Z`, local `2026-06-02 19:43:17 +05:00`.
   Artifact: `reports/qa_gate/p2159_p2079_f1_data_gate_utc_close_recheck_20260602T144317Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2160` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144457Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T144456Z.json`), `pip check PASS`, artifact parse `PASS`.
42. P2079 F1 UTC-close recheck:
   `P2160` completed UTC `2026-06-02T14:46:07Z`, local `2026-06-02 19:46:07 +05:00`.
   Artifact: `reports/qa_gate/p2160_p2079_f1_data_gate_utc_close_recheck_20260602T144607Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2161` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144742Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T144742Z.json`), `pip check PASS`, artifact parse `PASS`.
43. P2079 F1 UTC-close recheck:
   `P2161` completed UTC `2026-06-02T14:49:43Z`, local `2026-06-02 19:49:43 +05:00`.
   Artifact: `reports/qa_gate/p2161_p2079_f1_data_gate_utc_close_recheck_20260602T144943Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2162` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145122Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T145121Z.json`), `pip check PASS`, artifact parse `PASS`.
44. P2079 F1 UTC-close recheck:
   `P2162` completed UTC `2026-06-02T14:52:28Z`, local `2026-06-02 19:52:28 +05:00`.
   Artifact: `reports/qa_gate/p2162_p2079_f1_data_gate_utc_close_recheck_20260602T145228Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2163` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145406Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T145405Z.json`), `pip check PASS`, artifact parse `PASS`.
45. P2079 F1 UTC-close recheck:
   `P2163` completed UTC `2026-06-02T14:55:22Z`, local `2026-06-02 19:55:22 +05:00`.
   Artifact: `reports/qa_gate/p2163_p2079_f1_data_gate_utc_close_recheck_20260602T145522Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2164` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145702Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T145701Z.json`), `pip check PASS`, artifact parse `PASS`.
46. P2079 F1 UTC-close recheck:
   `P2164` completed UTC `2026-06-02T15:00:19Z`, local `2026-06-02 20:00:19 +05:00`.
   Artifact: `reports/qa_gate/p2164_p2079_f1_data_gate_utc_close_recheck_20260602T150019Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2165` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150225Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T150225Z.json`), `pip check PASS`, artifact parse `PASS`.
47. P2079 F1 UTC-close recheck:
   `P2165` completed UTC `2026-06-02T15:04:36Z`, local `2026-06-02 20:04:36 +05:00`.
   Artifact: `reports/qa_gate/p2165_p2079_f1_data_gate_utc_close_recheck_20260602T150436Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2166` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150617Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T150617Z.json`), `pip check PASS`, artifact parse `PASS`.
48. P2079 F1 UTC-close recheck:
   `P2166` completed UTC `2026-06-02T15:07:32Z`, local `2026-06-02 20:07:32 +05:00`.
   Artifact: `reports/qa_gate/p2166_p2079_f1_data_gate_utc_close_recheck_20260602T150732Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2167` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150915Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T150915Z.json`), `pip check PASS`, artifact parse `PASS`.
49. P2079 F1 UTC-close recheck:
   `P2167` completed UTC `2026-06-02T15:10:30Z`, local `2026-06-02 20:10:30 +05:00`.
   Artifact: `reports/qa_gate/p2167_p2079_f1_data_gate_utc_close_recheck_20260602T151030Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2168` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151314Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T151314Z.json`), `pip check PASS`, artifact parse `PASS`.
50. P2079 F1 UTC-close recheck:
   `P2168` completed UTC `2026-06-02T15:15:32Z`, local `2026-06-02 20:15:32 +05:00`.
   Artifact: `reports/qa_gate/p2168_p2079_f1_data_gate_utc_close_recheck_20260602T151532Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2169` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151714Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T151713Z.json`), `pip check PASS`, artifact parse `PASS`.
51. P2079 F1 UTC-close recheck:
   `P2169` completed UTC `2026-06-02T15:18:26Z`, local `2026-06-02 20:18:26 +05:00`.
   Artifact: `reports/qa_gate/p2169_p2079_f1_data_gate_utc_close_recheck_20260602T151826Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2170` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152005Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T152004Z.json`), `pip check PASS`, artifact parse `PASS`.
52. P2079 F1 UTC-close recheck:
   `P2170` completed UTC `2026-06-02T15:21:20Z`, local `2026-06-02 20:21:20 +05:00`.
   Artifact: `reports/qa_gate/p2170_p2079_f1_data_gate_utc_close_recheck_20260602T152120Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2171` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152306Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T152305Z.json`), `pip check PASS`, artifact parse `PASS`.
53. P2079 F1 UTC-close recheck:
   `P2171` completed UTC `2026-06-02T15:25:59Z`, local `2026-06-02 20:25:59 +05:00`.
   Artifact: `reports/qa_gate/p2171_p2079_f1_data_gate_utc_close_recheck_20260602T152559Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2172` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152826Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T152825Z.json`), `pip check PASS`, artifact parse `PASS`.
54. P2079 F1 UTC-close recheck:
   `P2172` completed UTC `2026-06-02T15:29:40Z`, local `2026-06-02 20:29:40 +05:00`.
   Artifact: `reports/qa_gate/p2172_p2079_f1_data_gate_utc_close_recheck_20260602T152940Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2173` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153127Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T153126Z.json`), `pip check PASS`, artifact parse `PASS`.
55. P2079 F1 UTC-close recheck:
   `P2173` completed UTC `2026-06-02T15:32:42Z`, local `2026-06-02 20:32:42 +05:00`.
   Artifact: `reports/qa_gate/p2173_p2079_f1_data_gate_utc_close_recheck_20260602T153242Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2174` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153429Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T153428Z.json`), `pip check PASS`, artifact parse `PASS`.
56. P2079 F1 UTC-close recheck:
   `P2174` completed UTC `2026-06-02T15:35:32Z`, local `2026-06-02 20:35:32 +05:00`.
   Artifact: `reports/qa_gate/p2174_p2079_f1_data_gate_utc_close_recheck_20260602T153532Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2175` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153717Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T153716Z.json`), `pip check PASS`, artifact parse `PASS`.
57. P2079 F1 UTC-close recheck:
   `P2175` completed UTC `2026-06-02T15:38:21Z`, local `2026-06-02 20:38:21 +05:00`.
   Artifact: `reports/qa_gate/p2175_p2079_f1_data_gate_utc_close_recheck_20260602T153821Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2176` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154009Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T154008Z.json`), `pip check PASS`, artifact parse `PASS`.
58. P2079 F1 UTC-close recheck:
   `P2176` completed UTC `2026-06-02T15:41:14Z`, local `2026-06-02 20:41:14 +05:00`.
   Artifact: `reports/qa_gate/p2176_p2079_f1_data_gate_utc_close_recheck_20260602T154114Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2177` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154333Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T154333Z.json`), `pip check PASS`, artifact parse `PASS`.
59. P2079 F1 UTC-close recheck:
   `P2177` completed UTC `2026-06-02T15:44:46Z`, local `2026-06-02 20:44:46 +05:00`.
   Artifact: `reports/qa_gate/p2177_p2079_f1_data_gate_utc_close_recheck_20260602T154446Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2178` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154634Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T154633Z.json`), `pip check PASS`, artifact parse `PASS`.
60. P2079 F1 UTC-close recheck:
   `P2178` completed UTC `2026-06-02T15:48:06Z`, local `2026-06-02 20:48:06 +05:00`.
   Artifact: `reports/qa_gate/p2178_p2079_f1_data_gate_utc_close_recheck_20260602T154806Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2179` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155005Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T155004Z.json`), `pip check PASS`, artifact parse `PASS`.
61. P2079 F1 UTC-close recheck:
   `P2179` completed UTC `2026-06-02T15:51:19Z`, local `2026-06-02 20:51:19 +05:00`.
   Artifact: `reports/qa_gate/p2179_p2079_f1_data_gate_utc_close_recheck_20260602T155119Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2180` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155304Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T155304Z.json`), `pip check PASS`, artifact parse `PASS`.
62. P2079 F1 UTC-close recheck:
   `P2180` completed UTC `2026-06-02T15:54:33Z`, local `2026-06-02 20:54:33 +05:00`.
   Artifact: `reports/qa_gate/p2180_p2079_f1_data_gate_utc_close_recheck_20260602T155433Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2181` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155722Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T155722Z.json`), `pip check PASS`, artifact parse `PASS`.
63. P2079 F1 UTC-close recheck:
   `P2181` completed UTC `2026-06-02T15:58:51Z`, local `2026-06-02 20:58:51 +05:00`.
   Artifact: `reports/qa_gate/p2181_p2079_f1_data_gate_utc_close_recheck_20260602T155851Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2182` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160102Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T160101Z.json`), `pip check PASS`, artifact parse `PASS`.
64. P2079 F1 UTC-close recheck:
   `P2182` completed UTC `2026-06-02T16:02:18Z`, local `2026-06-02 21:02:18 +05:00`.
   Artifact: `reports/qa_gate/p2182_p2079_f1_data_gate_utc_close_recheck_20260602T160218Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2183` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160404Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T160403Z.json`), `pip check PASS`, artifact parse `PASS`.
65. P2079 F1 UTC-close recheck:
   `P2183` completed UTC `2026-06-02T16:05:16Z`, local `2026-06-02 21:05:16 +05:00`.
   Artifact: `reports/qa_gate/p2183_p2079_f1_data_gate_utc_close_recheck_20260602T160516Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2184` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160705Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T160704Z.json`), `pip check PASS`, artifact parse `PASS`.
66. P2079 F1 UTC-close recheck:
   `P2184` completed UTC `2026-06-02T16:08:48Z`, local `2026-06-02 21:08:48 +05:00`.
   Artifact: `reports/qa_gate/p2184_p2079_f1_data_gate_utc_close_recheck_20260602T160848Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2185` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161033Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161033Z.json`), `pip check PASS`, artifact parse `PASS`.
67. P2079 F1 UTC-close recheck:
   `P2185` completed UTC `2026-06-02T16:11:50Z`, local `2026-06-02 21:11:50 +05:00`.
   Artifact: `reports/qa_gate/p2185_p2079_f1_data_gate_utc_close_recheck_20260602T161150Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2186` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161336Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161335Z.json`), `pip check PASS`, artifact parse `PASS`.
68. P2079 F1 UTC-close recheck:
   `P2186` completed UTC `2026-06-02T16:15:30Z`, local `2026-06-02 21:15:30 +05:00`.
   Artifact: `reports/qa_gate/p2186_p2079_f1_data_gate_utc_close_recheck_20260602T161530Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2187` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161633Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161632Z.json`), `pip check PASS`, artifact parse `PASS`.
69. P2079 F1 UTC-close recheck:
   `P2187` completed UTC `2026-06-02T16:19:09Z`, local `2026-06-02 21:19:09 +05:00`.
   Artifact: `reports/qa_gate/p2187_p2079_f1_data_gate_utc_close_recheck_20260602T161909Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2188` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161942Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161941Z.json`), `pip check PASS`, artifact parse `PASS`.
70. P2079 F1 UTC-close recheck:
   `P2188` completed UTC `2026-06-02T16:22:57Z`, local `2026-06-02 21:22:57 +05:00`.
   Artifact: `reports/qa_gate/p2188_p2079_f1_data_gate_utc_close_recheck_20260602T162257Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2189` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162331Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T162331Z.json`), `pip check PASS`, artifact parse `PASS`.
71. P2079 F1 UTC-close recheck:
   `P2189` completed UTC `2026-06-02T16:25:48Z`, local `2026-06-02 21:25:48 +05:00`.
   Artifact: `reports/qa_gate/p2189_p2079_f1_data_gate_utc_close_recheck_20260602T162548Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2190` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162627Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T162626Z.json`), `pip check PASS`, artifact parse `PASS`.
72. P2079 F1 UTC-close recheck:
   `P2190` completed UTC `2026-06-02T16:30:21Z`, local `2026-06-02 21:30:21 +05:00`.
   Artifact: `reports/qa_gate/p2190_p2079_f1_data_gate_utc_close_recheck_20260602T163021Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2191` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163046Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163046Z.json`), `pip check PASS`, artifact parse `PASS`.
73. P2079 F1 UTC-close recheck:
   `P2191` completed UTC `2026-06-02T16:33:25Z`, local `2026-06-02 21:33:25 +05:00`.
   Artifact: `reports/qa_gate/p2191_p2079_f1_data_gate_utc_close_recheck_20260602T163325Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2192` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163350Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163349Z.json`), `pip check PASS`, artifact parse `PASS`.
74. P2079 F1 UTC-close recheck:
   `P2192` completed UTC `2026-06-02T16:36:04Z`, local `2026-06-02 21:36:04 +05:00`.
   Artifact: `reports/qa_gate/p2192_p2079_f1_data_gate_utc_close_recheck_20260602T163604Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2193` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163630Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163629Z.json`), `pip check PASS`, artifact parse `PASS`.
75. P2079 F1 UTC-close recheck:
   `P2193` completed UTC `2026-06-02T16:38:39Z`, local `2026-06-02 21:38:39 +05:00`.
   Artifact: `reports/qa_gate/p2193_p2079_f1_data_gate_utc_close_recheck_20260602T163839Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2194` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163903Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163902Z.json`), `pip check PASS`, artifact parse `PASS`.
76. P2079 F1 UTC-close recheck:
   `P2194` completed UTC `2026-06-02T16:41:09Z`, local `2026-06-02 21:41:09 +05:00`.
   Artifact: `reports/qa_gate/p2194_p2079_f1_data_gate_utc_close_recheck_20260602T164109Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2195` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164133Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T164132Z.json`), `pip check PASS`, artifact parse `PASS`.
77. P2079 F1 UTC-close recheck:
   `P2195` completed UTC `2026-06-02T16:45:02Z`, local `2026-06-02 21:45:02 +05:00`.
   Artifact: `reports/qa_gate/p2195_p2079_f1_data_gate_utc_close_recheck_20260602T164502Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2196` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164527Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T164526Z.json`), `pip check PASS`, artifact parse `PASS`.
78. Quick structural audit:
   Artifact: `reports/qa_gate/quick_structural_audit_framework_20260602T182715Z.json`.
   Result: `PASS_WITH_ROUTE_CORRECTION`; UTC-close gate is only for P2079 forward/production. Structural big-window validation can be opened on already closed historical data.
   Framework facts: 68 feature rows across 6 blocks, narrow/medium/wide presets, 27 linked parameter profiles, 20 tunable hypotheses, 3x3/9 launcher support, block catalog `36/36 runtime OK`, positive `1`, neutral `18`, negative `17`, infra_fail `0`.
24. Block03 `volume_flow` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `1`, neutral `2`, negative `3`, infra_fail `0`, candidate_for_forward `1`.
   Positive artifact: `reports/optuna_catalog/positive/p2079_block03_volume_flow_narrow_long_only_positive_20260602T103932Z.json`.
   Decision: `GO_TO_BLOCK04_DENSITY_PROFILE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
   Post-sync audit `P2090`: `PASS`, freeze preserved.
25. Block04 `density_profile` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `4`, negative `2`, infra_fail `0`, candidate_for_forward `0`.
   Prior block03 positive candidate is preserved.
   Decision: `GO_TO_BLOCK05_STRUCTURE_TA_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
   Post-sync audit `P2103`: `PASS`, freeze preserved.
26. Block05 `structure_ta` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
   Prior block03 positive candidate is preserved.
   Decision: `GO_TO_BLOCK06_PATTERN_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
   Post-sync audit `P2116`: `PASS`, freeze preserved.
27. Block06 `pattern` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
   Prior block03 positive candidate is preserved.
   Decision: `GO_TO_BLOCK_LEVEL_CATALOG_RANKING_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
28. Block-level catalog ranking:
   All 6 blocks completed, runtime runs `36/36 OK`.
   Totals: positive `1`, neutral `18`, negative `17`, infra_fail `0`, candidate_for_forward `1`.
   Accepted candidate: block03 `volume_flow`, `P2079`, `long_only`, narrow, OOS `+1.9186%`, trades `1`.
   Boundary: forward F1/F2 required; production/unfreeze remains blocked.
29. P2133 forward command set:
   Artifact: `reports/optuna_catalog/index/p2133_p2079_forward_stability_command_set_20260602T112708Z.json`.
   Primary path: fixed-parameter replay of P2079 as singleton grids.
   Secondary path: same block03 narrow Optuna contour with fixed 3x3 profile.
   F1 window `2026-06-01 -> 2026-06-02` preflight `FAIL`: test raw `2026-06-02` absent; `2026-06-01` train is present but partial for WF rows.
   F2 window `2026-06-02 -> 2026-06-03` preflight `FAIL`: train raw `2026-06-02` and test raw `2026-06-03` absent.
30. P2134 forward data gate:
   Artifact: `reports/qa_gate/p2134_p2079_forward_preflight_data_gate_20260602T113136Z.json`.
   Current UTC at check: `2026-06-02T11:31:36Z`; `2026-06-02` is not closed in UTC and `2026-06-03` is future.
   Core max day: `2026-05-31`; raw max day: `2026-06-01`.
   F1 preflight report: `reports/qa_gate/preflight_window_20260602T113056Z.json`, `FAIL`.
   F2 preflight report: `reports/qa_gate/preflight_window_20260602T113105Z.json`, `FAIL`.
31. P2137 previous TZ recovery:
   Artifact: `reports/qa_gate/p2137_previous_tz_recovery_package_b_pointer_20260602T123736Z.json`.
   Previous active V3 requirement: after `Package A NO_CANDIDATE`, define exact `Package B` slots and then run bounded `Package B`.
   Catalog overlay does not cancel this; it requires preserving bounded Package B as catalog knowledge.
   Manual pointer restored to `Package B` definition. P2079 remains preserved only as `candidate_for_forward`; heartbeat is paused.
32. P2138 post-sync audit:
   Artifact: `reports/qa_gate/p2138_previous_tz_recovery_post_sync_audit_20260602T123949Z.json`.
   `text_guard`: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260602T123937Z.json`.
   `readiness`: `PASS`, freeze preserved, artifact `reports/readiness/readiness_check_20260602T123936Z.json`.
   `pip check`: `PASS`.
33. P2139 timed step chain:
   Artifact: `reports/qa_gate/p2139_package_b_timed_step_chain_20260602T124520Z.json`.
   Chain timestamp: UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`.
   From TZ: `docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md`, section 7, `2026-06-02T06:52:50Z`.
   Current step: Step 1 inventory of V3 Package A and old Package B artifacts.
34. P2139 independent agent cross-check:
   Artifact: `reports/qa_gate/p2139_independent_agent_crosscheck_20260602T125117Z.json`.
   Agent conclusion: current path is correct if next action is inventory only.
   Local conclusion: matches global audit Step 8 and V3 section 7; catalog overlay does not cancel Package B.
   Hard stop: no Package B runtime or P2079 forward before `P2140` inventory and Package B command-set/dry-run `PASS`.
35. P2140 V3 Package B inventory:
   Artifact: `reports/qa_gate/p2140_v3_package_b_inventory_20260602T125900Z.json`.
   Status: `PASS`.
   Current V3 Package A: closed `NO_CANDIDATE`, candidate_count `0`, best tradeful `short_only W2 A-H1`, OOS `-4.480772237153707`, trades `1`.
   Old Package B artifacts: `P1995/P1996` V2 and `P2005-P2007` strict execution are historical references only, not current V3 Package B.
   Current V3 Package B: exact slots not defined, matrices not found, command set not defined, runtime not allowed.
36. P2141 exact V3 Package B slots:
   Artifact: `reports/qa_gate/p2141_v3_package_b_exact_slots_20260602T130000Z.json`.
   Status: `PASS`.
   Windows: W1 `2026-05-29 -> 2026-05-30`, W2 `2026-05-30 -> 2026-05-31`, W3 `2026-05-31 -> 2026-06-01`.
   Slots: B-H1 `ema_stack_bull` long / `ema_cross_20_200` short; B-H2 `min_max_range_revert` both; B-H3 `spread_pressure_and_delta_absorption` both.
   Resource profile: `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`.
   Next: `P2142` matrix slices and command-set/dry-run only.

## Current Risks
1. `Package B` is required by V3 but its exact slot composition is not fixed yet.
2. Running `Package B` without a fixed slot table would reintroduce drift.
3. Old historical reports are numerous; always use active files listed in `handoff.md`.
4. The repository is not a git repo in this workspace, so local file backups matter.
5. Old V3 wording can be misread as stopping after `Package B NO_CANDIDATE`; active catalog overlay says to keep structured block/feature/hypothesis cataloging.
6. Running wider medium/wide catalog work before the `1d -> 1d` smoke check could hide wiring or parameter-transfer defects under a large search.
7. Skipping roadmap steps would reintroduce drift; every step now needs an exit artifact/status before moving forward.

## State Version
`V3-NO_GO-P2195-STRUCTURAL-AUDIT-PASS-WITH-ROUTE-CORRECTION-20260602T182715Z`

## Hard Structural Audit 2026-06-02T19:16:09Z
Artifact: `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md`.
Status: `PASS_WITH_FINDINGS`.
Facts: 68 features across 6 blocks, 56 tunable feature rows, 20 tunable hypotheses, 27/27 parameter profiles linked, 0 runtime feature misses, 0 feature-group mismatches, narrow/medium/wide min/max anchors preserved, 18/18 block command sets PASS, block catalog runtime `36/36 OK`.
Finding: block matrices isolate feature rows, but global hypothesis/trend-filter logic can still pull columns from another block. `P2079` is valid as a working catalog candidate, but not proven as pure `volume_flow` only.
Boundary: production remains `NO_GO`; P2079 remains `candidate_for_forward` only until F1/F2 forward validation is `2/2 PASS` and a new GO package exists.

## State Version
`V3-NO_GO-P2195-HARD-STRUCTURAL-AUDIT-PASS-WITH-FINDINGS-20260602T191609Z`

## Structural Big-Window Stop 2026-06-02T19:23:17Z
Command-set artifact: `reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json`, status `PASS`, compile/dry-run `36/36 PASS`.
Stop artifact: `reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`, status `STOPPED_BY_USER_AND_FREEZE_RESTORED`.
Runtime facts: block01 long/short and block02 long completed with launcher `OK`; block02 short was stopped by user; positive candidates `0`; no production/unfreeze touched.

## State Version
`V3-NO_GO-P2195-STRUCTURAL-RUNTIME-STOPPED-BY-USER-FREEZE-RESTORED-20260602T192317Z`

## P2196A Optuna Battle Readiness Audit 2026-06-03T06:09:19Z
Artifact: `reports/qa_gate/p2196a_optuna_battle_readiness_audit_20260603T060919Z.md`.
Status: `NO_GO_FOR_PRODUCTION / GO_TO_STRICT_BLOCK_PURITY_FIX_BEFORE_BATTLE`.
Current facts: structural Optuna contour works, 3x3/9 workers are supported, 36/36 historical block catalog runs were OK, and structural big-window command-set dry-run was 36/36 PASS. The blocking finding remains strict semantics: block matrices isolate feature rows, but hypotheses/trend filters are still global unless filtered by required columns.
Forward data gate: current UTC is after 2026-06-03T00:00:00Z, but raw/core 2026-06-02 and 2026-06-03 SOLUSDT 1m files are missing. P2079 F1 still needs ingest/preflight PASS; F2 waits for closed 2026-06-03.
Next state: `P2196B` strict block-hypothesis compatibility implementation/audit before battle runtime.
Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T061526Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T061522Z.json`), `pip check PASS`.

## State Version
`V3-NO_GO-P2196A-BATTLE-READINESS-AUDIT-STRICT-PURITY-NEXT-20260603T060919Z`

## P2196B Volume/Volatility Context Wiring
Artifact: `reports/qa_gate/p2196b_volume_context_wiring_audit_20260603T065821Z.json`.
Status: `PASS_CONTEXT_WIRING / STRICT_HYPOTHESIS_FILTER_PENDING`.
Current fact: volume/volatility context is now always included in Optuna feature/profile selection through `volume_flow` and `price_volatility` for full matrix and all 6 catalog block matrices. This does not make raw `volume` tunable; it makes derived volume features participate in calibration and reporting.
Tests: `tests.test_optuna_space_constraints` + `tests.test_optuna_search_runtime` -> `69/69 OK`.
Post-sync checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T070000Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T065959Z.json`), `pip check PASS`.

## State Version
`V3-NO_GO-P2196B-VOLUME-CONTEXT-PASS-STRICT-FILTER-PENDING-20260603T065821Z`

## P2196B Strict Hypothesis Filtering
Artifact: `reports/qa_gate/p2196b_strict_hypothesis_filter_full_audit_20260603T100404Z.json`.
Status: `PASS_STRICT_FILTERING`.
Current fact: block catalog matrices now filter hypotheses/trend filters by required columns within primary enabled block plus always-on context blocks. This closes the known P2079-style mixed-semantics issue where `volume_flow` could select `min_max_range_revert` from `structure_ta`.
Tests: focused strict set -> `77/77 OK`.

## P2196C Strict Command Set Dry-Run
Artifact: `reports/optuna_catalog/index/p2196c_strict_command_set_20260603T100504Z.json`.
Status: `PASS`, `36/36 dry-run PASS`.
Raw preflight: `reports/qa_gate/preflight_window_20260603T100432Z.json`, `PASS`.
Next executable step: `P2196D` strict P2079-equivalent check. Production/unfreeze remains `NO_GO`.
Post-sync checks 2026-06-03T10:08:56Z: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T100856Z.json`), readiness freeze preserved with calibration-only temporary unlock path (`reports/readiness/readiness_check_20260603T100856Z.json`), `pip check PASS`.

## State Version
`V3-NO_GO-P2196C-STRICT-COMMAND-SET-36-36-PASS-20260603T100504Z`

## P2196D Strict Runtime Calibration Start 2026-06-03T10:14:50Z
Artifact: `reports/adaptive/long_only_pool_20260603t101450z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T101454Z.json`.
Status: `PASS_RUNTIME_OK / EXPERIMENTAL_POSITIVE`.
Current fact: first real strict calibration runtime ran block03 `volume_flow` narrow `long_only` with 3x3/9 workers. Launcher returned `OK`; best OOS was `+1.5266529420731034%` with `1` trade; workers `w2` and `w3` passed the 1% goal.
Boundary: train gate failed, so the result is saved as `TOP_EXPERIMENTAL`, not production/latest. Production/unfreeze remains `NO_GO`.
Next practical action: continue calibration sequence from the next strict battle run; do not expand into old chronology.

## State Version
`V3-NO_GO-P2196D-STRICT-RUNTIME-STARTED-EXPERIMENTAL-POSITIVE-20260603T101450Z`

## P2196E Volume Flow Narrow Short Runtime 2026-06-03T10:21:58Z
Artifact: `reports/adaptive/short_only_pool_20260603t102158z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T102202Z.json`.
Status: `PASS_RUNTIME_OK / NO_CANDIDATE`.
Current fact: short side of block03 `volume_flow` narrow was rerun after fixing report-read robustness. Launcher returned `OK`, all 3 workers exited `0`, best OOS `0%`, trades `0`.
Code fix: `src/mlbotnav/adaptive_auto_train.py` now uses `_read_json_report_with_retry` so an empty/unreadable search report becomes a recorded iteration failure instead of crashing a worker.
Validation: focused tests `83/83 OK`.
Next practical action: continue volume_flow calibration to the next grid/profile, or move to the next block runtime if operator chooses block-first ordering.

## State Version
`V3-NO_GO-P2196E-VOLUME-FLOW-NARROW-BOTH-SIDES-CHECKED-20260603T102158Z`

## Calibration Current H006 Pattern Replay
Artifact: `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z_RU.md`.
Status: `BLOCK_COMPLETE_RUNTIME_OK_NO_CANDIDATE`.
Current fact: H006 `pattern` was replayed after fixing final parameter transfer and candidate retry. `long_only` and `short_only` each ran `narrow/medium/wide` with `ProcessWorkers=3`, `SearchWorkers=9`, `SearchWorkersPerProcess=3`; all 6 launchers returned `OK`.
Runtime result: no worker crash; every final `best_oos` contains `18` `selected_calibration_params`; no positive candidate. Best tradeful result is `short_only medium`, `-15.6997%`, `6` trades.
Code fix: `src/mlbotnav/adaptive_auto_train.py` preserves `calibration_params`, includes them in candidate signatures, and tries up to `8` current candidates before marking train replay failed.
Tests: focused suite `81/81 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T110352Z.json`.

## State Version
`CALIBRATION-CURRENT-H006-PATTERN-REPLAY-OK-NO-CANDIDATE-20260604T110012Z`

## H006 Grid Edge Coverage Audit Fix
Artifact: `reports/qa_gate/h006_grid_edge_coverage_audit_fix_20260604T111552Z_RU.md`.
Status: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.
Current fact: Optuna search reports now include `grid_edge_coverage_audit`, and a separate `grid_edge_coverage_audit_*.json` artifact is written beside `trial_history`. The audit counts all trials for the current `run_signature`, including pruned trials, so forced min/max coverage is no longer invisible.
Runtime smoke: H006 `pattern long_only narrow`, `2x6`, `24` total trials, launcher `OK`; new audit artifact `reports/optuna/long_only/grid_edge_coverage_audit_20260604T111552Z.json` saw `total=12`, `completed=8`, `pruned=4`, `failed=0` for the best worker search.
Tests: focused suite `94/94 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T111802Z.json`.
Next fact: cascade improvement is not implemented yet; next route is full replay with new edge audit or cascade mode implementation.

## State Version
`CALIBRATION-CURRENT-H006-EDGE-AUDIT-FIX-SMOKE-OK-20260604T111552Z`

## H006 Core Grid Edge Forcing Fix
Artifact: `reports/qa_gate/h006_core_grid_edge_forcing_fix_20260604T113102Z_RU.md`.
Status: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.
Current fact: core search parameters now have forced min/max seeding and audit fields. The first 5 trials force min for `horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`; the next 5 force max.
Runtime smoke: H006 `pattern long_only narrow`, `2x6`, `24` total trials, launcher `OK`. Audit `reports/optuna/long_only/grid_edge_coverage_audit_20260604T113102Z.json` reports core coverage `pass=5`, `fail=0`.
Tests: focused suite `94/94 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T113308Z.json`.
Next fact: profile coverage still needs full-budget replay for proof; cascade improvement is still pending.

## State Version
`CALIBRATION-CURRENT-H006-CORE-EDGE-FORCING-SMOKE-OK-20260604T113102Z`

## H006 Full Replay Edge Coverage Pass
Artifact: `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z_RU.md`.
Status: `BLOCK_COMPLETE_RUNTIME_OK_EDGE_COVERAGE_PASS_NO_CANDIDATE`.
Current fact: H006 `pattern` now has a full proof replay after distributed edge coverage. LONG and SHORT each ran `narrow/medium/wide`; every combined grid audit shows profile coverage `18/18` and core coverage `5/5`.
Runtime result: all 6 launchers `OK`, worker crash `0`, positive candidate `0`. Best LONG: `narrow -0.6074%`, `1` trade. Best tradeful SHORT: `wide -20.3243%`, `10` trades.
Tests: focused suite `95/95 OK`.
Next fact: the remaining open feature is cascade candidate improvement: `wide -> medium around best -> narrow around best`, LONG and SHORT separately.

## State Version
`CALIBRATION-CURRENT-H006-FULL-REPLAY-EDGE-PASS-NO-CANDIDATE-20260604T123958Z`

## CASCADE_BLOCK_CALIBRATION Rule Fixed
Artifact: `docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`.
Status: `RULE_FIXED_NO_CODE_CHANGES`.
Current fact: target battle calibration mode is now `CASCADE_BLOCK_CALIBRATION`: one block equals one cascade; LONG and SHORT are separate; `wide` runs first; `medium` narrows around the best tradeful `wide`; `narrow` narrows around the best tradeful `medium`.
Boundary: if `wide` finds no tradeful candidate, do not narrow blindly; record `NO_TRADEFUL_CANDIDATE` and move to the next block. If the best tradeful candidate is negative, continue the cascade to measure the best possible block result. Positive candidates go to positive/top candidates only, not production.
No code changed and no runtime launched for this rule fixation.

## State Version
`CALIBRATION-CURRENT-CASCADE-BLOCK-CALIBRATION-RULE-FIXED-20260604T141745Z`

## C001 Block 01 LONG Wide Runtime
Artifact: `reports/qa_gate/c001_block01_price_volatility_long_wide_20260604T144429Z_RU.md`.
Status: `RUNTIME_OK_TRADEFUL_NEGATIVE`.
Current fact: first cascade runtime step ran `price_volatility` / Block 01 `long_only wide` with `ProcessWorkers=3`, `SearchWorkers=9`, `SearchWorkersPerProcess=3`, `OptunaTrials=180`. Launcher returned `OK`, workers `3/3` exited `0`.
Runtime result: best OOS `-37.0372%` with `9` trades. Candidate is tradeful but negative; production remains `NO_GO`.
Best wide params: `min_abs_ema_gap=0.05`, `period_standard=19`, `return_lookback=18`, `rolling_window=40`, `vol_z_window=180`.
Coverage note: core coverage is `5/5`; profile coverage is `5/5` in one edge audit and `2/5` in another. `w1/w2` point at the same search report timestamp with `contour_id=w2`, likely an artifact naming collision.
Next fact: by `CASCADE_BLOCK_CALIBRATION`, next allowed step is `C001 LONG medium around best`; blind medium/narrow should not run.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T144630Z.json`.

## State Version
`CALIBRATION-CURRENT-C001-BLOCK01-LONG-WIDE-RUNTIME-OK-TRADEFUL-NEGATIVE-20260604T144429Z`

## Instrument Knobs Audit TZ
Artifact: `docs/CALIBRATION_NODE_CURRENT/TZ_INSTRUMENT_KNOBS_AUDIT_2026-06-11_RU.md`.
Status: `ACTIVE_READ_ONLY_AUDIT`.
Current fact: user clarified that the next step is not more runtime calibration. The next task is a block-by-block audit of every instrument/feature/indicator/hypothesis knob: what can be tuned, what is currently declared, what is actually used, and which signal-level thresholds/lines are missing.
Boundary: do not run `C001 medium`, Optuna/APTuna runtime, forward, or production actions until the instrument knobs audit is completed and agreed.
Next fact: start with `Block 01 price_volatility instrument knobs audit`, then move block-by-block through all 6 blocks.

## State Version
`CALIBRATION-CURRENT-INSTRUMENT-KNOBS-AUDIT-TZ-ACTIVE-20260611T104735Z`

## Block 01 Price Volatility Knobs Audit
Artifact: `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.
Status: `BLOCK_01_AUDIT_DRAFT`.
Current fact: Block 01 `price_volatility` has a separate mini-TZ now. It confirms the block currently calibrates calculation windows (`return_lookback`, `rolling_window`, `period_standard`), while explicit signal-level thresholds for price move strength, high-low spread regime, volatility regime, and ATR/risk regime are still pending agreement.
Boundary: no runtime launches and no config edits until Block 01 knobs are agreed.
Next fact: agree Block 01 knobs, then move to `Block 02 trend_momentum`.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T105438Z.json`.

## State Version
`CALIBRATION-CURRENT-BLOCK01-PRICE-VOLATILITY-KNOBS-AUDIT-DRAFT-20260611T105100Z`

## Block 01 Live Chart Example
Artifacts:
1. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.png`
2. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z_RU.md`
3. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.json`

Status: `VISUAL_AUDIT_EXAMPLE`.
Current fact: Block 01 was rendered on real SOLUSDT 1m data from `2026-06-01` using C001 wide calculation params (`return_lookback=18`, `rolling_window=40`, `period_standard=19`). The chart shows candles, `ret_1`, `rolling_std_20`, `atr14`, `hl_spread`, and example actions `LONG_ALLOWED`, `SHORT_ALLOWED`, `NO_TRADE_LOW_VOL`, `NO_TRADE_HIGH_RISK`.
Boundary: visual thresholds are examples for agreement, not production config and not an Optuna runtime.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T113003Z.json`.

## State Version
`CALIBRATION-CURRENT-BLOCK01-LIVE-CHART-EXAMPLE-20260611T110200Z`

## Block 01 Short Rework Visual
Artifacts:
1. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.png`
2. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z_RU.md`
3. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.json`

Status: `SHORT_REWORK_VISUAL_AUDIT`.
Current fact: the first visual showed why `ret_1 > 0` can be misleading: inside a falling context, local upside is a pullback, not a LONG entry. Block 01 now has a documented proposed SHORT interpretation: `SHORT_MOMENTUM` and `SHORT_AFTER_PULLBACK`.
Proposed knobs: `ret_down_context_threshold`, `ret_pullback_up_threshold`, `ret_short_confirm_threshold`, `confirm_bars`, `vol_min/max`, `atr_min/max`, `hl_spread_max`.
Boundary: no config edits and no Optuna/APTuna runtime were launched.

## State Version
`CALIBRATION-CURRENT-BLOCK01-SHORT-REWORK-VISUAL-20260611T113400Z`

## Block 01 Parameter Range Map
Artifact: `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.
Status: `PARAMETER_RANGE_MAP_DRAFT`.
Current fact: Block 01 now has a drafted min/max/step map for calculation windows, up/down context, pullback, confirmation, market activity filters, and primary ATR/target risk. This answers "from where to where" for `return_lookback`, `rolling_window`, `period_standard`, context thresholds, pullback thresholds, `confirm_bars`, `vol_min/max`, `atr_min/max`, and `hl_spread_min/max`.
Boundary: this is a TZ/range draft only. No config/code changes and no Optuna/APTuna runtime were launched.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T120336Z.json`.

## State Version
`CALIBRATION-CURRENT-BLOCK01-PARAMETER-RANGE-MAP-DRAFT-20260611T114800Z`

## New Chat Handoff
Artifact: `docs/CALIBRATION_NODE_CURRENT/HANDOFF_TO_NEW_CHAT_2026-06-19_RU.md`.
Status: `NEW_CHAT_HANDOFF_READY`.
Current fact: old chat is too large, so a clean handoff packet was created. It preserves the active source of truth, explains the 6-block route, captures Block 01 `PARAMETER_RANGE_MAP_DRAFT`, lists visual artifacts, and includes a startup prompt for the new chat.
Next fact: new chat should read the handoff and decide whether Block 01 becomes `AGREED/READY_FOR_CODE` or needs one more clarification before Block 02.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260619T184109Z.json`.

## State Version
`CALIBRATION-CURRENT-NEW-CHAT-HANDOFF-READY-20260619`

## F001 Strict Passport Runtime Connected
Artifact: `docs/CALIBRATION_NODE_CURRENT/passports/features/F001_ret_1_RU.md`.
Status: `F001_STRICT_PASSPORT_CONNECTED`.
Current fact: user-provided strict F001 passport is now connected to calibration/runtime. `F001_RET1_ALLOW` is calculated in `dataset.py`, preserved in OOF by validation/Optuna, and applied as an entry gate in `backtest.py`.
Calibration params: `F001_move` values `-1/1`; `F001_thr_pct` range `0.01..0.50`, step `0.01`.
Matrices updated: `configs/calibration_full_matrix_v1.yaml`, `configs/calibration_matrices/catalog_blocks/catalog_block_01_price_volatility.yaml`, `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`.
Validation: `py_compile PASS`; focused tests `25/25 OK`; Optuna runtime tests `65/65 OK`; matrix compile check PASS; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T091458Z.json`.
Next fact: wait for user decision to run F001/H001 or Block 01 with the new passport, or continue strictly to `F002 ret_3`.

## State Version
`CALIBRATION-CURRENT-F001-STRICT-PASSPORT-CONNECTED-20260622T091458Z`

## F001 Strict LONG 1d/1d Runtime
Artifact: `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`.
Status: `F001_LONG_1D1D_DONE_GOAL_FAIL`.
Current fact: ran F001 strict passport in `long_only` on train `2026-05-31`, OOS `2026-06-01`, matrix `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`, wide grid, 180 trials, 3 process workers.
Important fix: initial OOS showed `F001_RET1_ALLOW_gate_active=false`; `src/mlbotnav/oos_evaluate.py` was fixed to preserve `RUNTIME_ACTION_COLUMNS`. Focused validation after fix: `py_compile PASS`, `84 tests OK`.
Final launcher: `OK`, workers `3/3`, all `exit_code=0`.
Best worker: `w1`; selected params `F001_move=1.0`, `F001_thr_pct=0.19`, `min_abs_ema_gap=0.02`.
Final OOS: `net_return_pct=-5.352332468117016`, `trades=3`, `hit_rate=0.3333333333333333`, `max_drawdown_pct=-5.833320604926396`, `goal_pass=false`, `train_gate_pass=false`.
Gate diagnostics: `F001_RET1_ALLOW_gate_active=true`, raw signals `525`, after LONG mode `281`, after F001 gate `4`, entries filled `3`.
Next fact: F001 LONG on this 1d/1d window is `NO_GO`; user may choose SHORT F001 separately or move to next passport `F002 ret_3`.

## State Version
`CALIBRATION-CURRENT-F001-LONG-1D1D-GOAL-FAIL-20260622T092020Z`

## F001 Strict LONG Trade Map
Artifact: `reports/qa_gate/f001_strict_long_1d1d_trade_map_20260622T092020Z.png`.
Status: `F001_LONG_TRADE_MAP_READY`.
Current fact: generated a QA chart for the best F001 LONG OOS worker `w1`, showing the full OOS day plus three zoom panels. Each trade panel marks signal bar, entry, exit, TP `+1.20%`, and SL `-0.80%`.
Conclusion: all 3 trades exited by `timeout`; `target_reached=false`; TP and SL were not hit.

## State Version
`CALIBRATION-CURRENT-F001-LONG-TRADE-MAP-READY-20260622T092020Z`

## F001 Strict LONG No-Timeout Runtime
Artifact: `reports/qa_gate/f001_strict_long_no_timeout_1d1d_20260622T093702Z_RU.md`.
Chart: `reports/qa_gate/f001_strict_long_no_timeout_trade_map_20260622T093702Z.png`.
Status: `F001_LONG_NO_TIMEOUT_DONE_NO_GO`.
Current fact: timeout exit is now an explicit runtime switch. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` accepts `-DisableTimeoutExit`, and Python entrypoints accept `--disable-timeout-exit`; backtest closes positions only by TP/SL or `end_of_data` when timeout is disabled.
Validation: `py_compile PASS`; `tests.test_backtest_fields`, `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_optuna_search_runtime`: `78 tests OK`.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T094448Z.json`.
Runtime: F001 strict LONG rerun on train `2026-05-31`, OOS `2026-06-01`, H001 matrix, wide grid, 180 trials, `TimeoutExit=off`, launcher `OK`, workers `3/3`.
Formal best: worker `w1`, params `F001_move=1.0`, `F001_thr_pct=0.09`, `min_abs_ema_gap=0.07`, OOS `0.0%`, `0` trades, `goal_pass=false`.
Best tradeful: worker `w2/w3`, params `F001_move=1.0`, `F001_thr_pct=0.05`, `min_abs_ema_gap=0.08`, OOS `-47.79331627195255%`, `6` trades, `hit_rate=0.0`, `max_drawdown=-47.79331627195255%`, `goal_pass=false`.
Conclusion: timeout is disabled correctly, but F001 LONG remains `NO_GO`; without timeout, tradeful positions mostly sit until SL.

## State Version
`CALIBRATION-CURRENT-F001-LONG-NO-TIMEOUT-NO-GO-20260622T093702Z`

## F001 Exit Baseline Decision
Status: `EXIT_BASELINE_TIMEOUT_ON`.
Current fact: user decided to keep exits clean and as before for the active calibration baseline: TP, SL, and timeout by `hold_bars`.
Boundary: do not use `-DisableTimeoutExit` for baseline F001/Block 01 runs. The no-timeout mode remains available as a diagnostic switch only.
Active comparison artifact: `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`; timeout-on OOS was `-5.352332468117016%`, `3` trades, all exits by `timeout`.

## State Version
`CALIBRATION-CURRENT-F001-EXIT-BASELINE-TIMEOUT-ON-20260622`

## Action Passport Calibration Rule
Artifacts:
1. `docs/CALIBRATION_NODE_CURRENT/TZ_ACTION_PASSPORT_CALIBRATION_2026-06-22_RU.md`
2. `configs/calibration_action_passports.yaml`
3. `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`

Status: `ACTION_PASSPORT_CALIBRATION_ACTIVE`.
Current fact: user declared old Optuna calibration proposals/configs were structurally wrong because they mixed feature, hypothesis, runtime, risk, and exit knobs. New baseline rule is passport-first: every calibration/backtest action needs an action passport and an explicit allowlist of tunable params.
Legacy boundary: old `calibration_full_matrix`, `catalog_blocks`, and `feature_sweep` matrices are not deleted, but are `legacy/frozen` for new baseline runs.
Code guard: `src/mlbotnav/optuna_space.py` now supports `passport_mode.enabled=true`; any row/search param outside `allowed_calibration_params` fails compile.
Active F001 allowlist: `F001_move`, `F001_thr_pct`.
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`: `13 tests OK`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; YAML parse PASS; F001 passport matrix compile PASS for `long_only` and `short_only`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T101720Z.json`.
Next fact: future F001 baseline commands must use `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`; exit/dynamic-exit must wait for separate passports.

## State Version
`CALIBRATION-CURRENT-ACTION-PASSPORT-CALIBRATION-ACTIVE-20260622`

## F001 Passport-Action LONG Runtime
Artifact: `reports/qa_gate/f001_passport_action_long_1d1d_20260622T101953Z_RU.md`.
Status: `F001_PASSPORT_ACTION_LONG_DONE_NO_GO`.
Current fact: ran the clean F001 passport-action matrix `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml` in `long_only`, train `2026-05-31`, OOS `2026-06-01`, wide, 180 trials, timeout exit on.
Compile proof: `passport_mode.enabled=true`; compiled profiles only `F001_move`, `F001_thr_pct`.
Launcher: `OK`, workers `3/3`.
Formal best: `w3`, `0.0%`, `0` trades, not tradeful.
Best tradeful: `w1`, params `F001_move=1.0`, `F001_thr_pct=0.28`, OOS `-5.1298471326372%`, `1` trade, exit `timeout`.
Other tradeful: `w2`, `F001_thr_pct=0.10`, OOS `-28.876033596834784%`, `8` trades.
Conclusion: infrastructure/passport path works, F001 LONG remains `NO_GO`.
Residual cleanup: Optuna core runtime fields are still sampled from engine grids (`horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`); for full passport purity they need a runtime/backtest subpassport or fixed single-value grids.
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T102340Z.json`.

## State Version
`CALIBRATION-CURRENT-F001-PASSPORT-ACTION-LONG-NO-GO-20260622T101953Z`

## Block Passport Registry
Artifact: `configs/calibration_action_passports.yaml`.
Status: `BLOCK_PASSPORT_REGISTRY_CONNECTED`.
Current fact: user chose one main config for all passports. The registry now has blocks `B001..B006`, Russian names, active/planned passports inside each block, and runtime/backtest subpassport placeholders.
Active F001 location: `blocks.B001.active_passports.F001`; `B001` is `price_volatility` / `Цена и волатильность`.
Planned F002 location: `blocks.B001.planned_passports.F002`; do not use legacy H002 matrix as baseline.
Code guard: `src/mlbotnav/optuna_space.py` now validates passport matrices against the registry (`registry_path`, `registry_block_id`, `registry_passport_id`, `action_id`, allowlist, active matrix path).
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `79 tests OK`; env override compile PASS for F001 passport matrix.

## State Version
`CALIBRATION-CURRENT-BLOCK-PASSPORT-REGISTRY-CONNECTED-20260622`

## RET_N F001-F005 Strict Passport Family
Artifact: `docs/CALIBRATION_NODE_CURRENT/passports/features/RET_N_F001_F005_strict_passports.md`.
Status: `RET_N_F001_F005_PASSPORTS_CONNECTED`.
Current fact: user supplied `C:\Users\007\Downloads\RET_N_F001_F005_strict_passports.md`; the project now has active B001 passports for F001-F005 under `configs/calibration_action_passports.yaml`.
Active matrices: `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`, `F002_ret3_entry_filter.yaml`, `F003_ret6_entry_filter.yaml`, `F004_ret12_entry_filter.yaml`, `F005_ret24_entry_filter.yaml`.
Runtime fact: `src/mlbotnav/dataset.py` can compute `F001_RET1_ALLOW`, `F002_RET3_ALLOW`, `F003_RET6_ALLOW`, `F004_RET12_ALLOW`, `F005_RET24_ALLOW`; F002-F005 are emitted only when their own passport params are present.
Backtest fact: `src/mlbotnav/backtest.py` now applies present `ENTRY_ACTION_ALLOW` columns as an AND gate and reports `entry_action_gate_columns`.
Validation: `py_compile PASS`; focused tests `96/96 OK`; F001-F005 matrix compile PASS; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T112135Z.json`.
Resolved fix: `src/mlbotnav/optuna_space.py` now preserves the `max` anchor when `step` does not land on it exactly. F003 `F003_thr_pct` compiles to `60` values and includes `1.20`.
Validation after fix: `py_compile PASS`; focused tests `98/98 OK`; F003 matrix compile proof `60 0.03 [1.17, 1.19, 1.2] True`.

## State Version
`CALIBRATION-CURRENT-RET-N-F001-F005-PASSPORTS-CONNECTED-20260622T112135Z`

## State Version
`CALIBRATION-CURRENT-RET-N-MAX-ANCHOR-FIX-20260622`

## B001 RET_N Ladder Tournament
Status: `B001_RET_N_LADDER_READY_SMOKE_OK`.
Current fact: implemented a tournament path for one block `B001` with five RET_N passports F001-F005. It generates all `31` non-empty passport combinations and runs each combination as a clean passport matrix.
Registry: `configs/calibration_action_passports.yaml` now includes `blocks.B001.active_passports.B001_RET_N_TOURNAMENT`.
Generator: `src/mlbotnav/b001_ret_n_ladder_tournament.py`.
Runner: `APTuna/run_b001_ret_n_ladder_tournament.ps1`.
Manifest artifact: `reports/qa_gate/b001_ret_n_ladder_matrices_20260622T115638Z/manifest.json`.
Smoke artifact: `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115930Z.json`.
Runtime rule: every combo gates entry with `AND` over present runtime action columns. Example: `F002+F005` means both `F002_RET3_ALLOW` and `F005_RET24_ALLOW` must pass.
Smoke result: one-combo `B001_RET_N_F001` LONG smoke completed through APTuna process pool with exit code `0`; tournament report extracted `best_oos`. The smoke had `0` OOS trades and is not a candidate.
Validation: `py_compile PASS`; generator/space/dataset/backtest focused tests `35/35 OK`; extended focused tests including Optuna runtime `83/83 OK`.
Full run command: `powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock`.

## State Version
`CALIBRATION-CURRENT-B001-RET-N-LADDER-READY-SMOKE-OK-20260622T115930Z`

## B001 Solo Selection Decision
Status: `B001_RET_N_SOLO_SELECTION_ONLY`.
Current fact: after full LONG 31-combo run `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T120806Z.json`, user decided not to use expanded in-block combination calibration as baseline.
Reason: `31/31` combos were technically OK, but `28/31` had zero OOS trades. Best combo `F002+F004` had only `1` OOS trade, `+0.7845424236948562%` at `10x`, exit `timeout`, `target_reached=false`; it is `NO_CANDIDATE`.
Active rule: B001 baseline searches only solo features F001-F005; promote at most one best solo feature if tradeful and non-negative on OOS.
Technical guard: `APTuna/run_b001_ret_n_ladder_tournament.ps1` now defaults to `EndIndex=5`; `EndIndex > 5` is blocked unless `-EnableCombinationTournament` is passed explicitly for diagnostic-only runs.
Registry: `B001_RET_N_TOURNAMENT` is now `diagnostic_only_disabled_for_baseline`.
Validation: default dry-run selected 5 solo rows; `EndIndex=31` without diagnostic switch blocks; `py_compile PASS`; focused tests `35/35 OK`.

## State Version
`CALIBRATION-CURRENT-B001-RET-N-SOLO-SELECTION-ONLY-20260622`

## MACD F013-F015 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/macd_f013_f015_long_short_audit_20260622T151954Z_RU.md`.
Current fact: implemented `B007/MACD импульс` with solo passports F013/F014/F015 and ran clean LONG/SHORT on train `2026-05-31`, OOS `2026-06-01`, wide, 180 trials, timeout exit on.
Matrices: `configs/calibration_matrices/passport_actions/F013_macd_line_1m_entry_filter.yaml`, `F014_macd_signal_1m_entry_filter.yaml`, `F015_macd_hist_1m_entry_filter.yaml`.
Runtime/backtest: dataset emits `F013_MACDLINE_ALLOW`, `F014_MACDSIGNAL_ALLOW`, `F015_MACDHIST_ALLOW`; backtest gates entries by these present action columns.
Fix applied: Optuna `run_signature` now includes `space_signature` so different passport matrices cannot resume each other's stored trials. Pre-fix MACD runs were discarded and rerun.
Clean result: all six launches `OK`; selected params isolation `PASS`; no non-negative tradeful candidate.
Best tradeful by OOS: `F014 LONG`, `-2.9779083375433224%`, `3` trades, `0/3` wins/losses, all exits `timeout`.
Final status: `NO_GO`.
Validation: `py_compile PASS`; focused tests `112/112 OK`; YAML parse PASS; matrix compile PASS; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T152122Z.json`.

## State Version
`CALIBRATION-CURRENT-MACD-F013-F015-NO-GO-20260622T151954Z`

## F016 ADX14 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f016_adx14_long_short_audit_20260622T153403Z_RU.md`.
Current fact: implemented `B008/ADX14 сила тренда` with solo passport F016 `adx14_1m`; action output is `F016_ADX14_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F016_adx14_1m_entry_filter.yaml`.
Runtime/backtest: dataset emits `F016_ADX14_ALLOW` only when `F016_cmp`/`F016_level` are present; backtest gates entries by this present action column.
Clean result: LONG selected `LESS level=41`, OOS `-13.43232421418481%`, `3` trades, `0/3` wins/losses, all exits `timeout`; SHORT selected `LESS level=28`, OOS `-28.526707456698695%`, `13` trades, `1/12` wins/losses, all exits `timeout`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `114/114 OK`; YAML parse PASS; matrix compile PASS for LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-F016-ADX14-NO-GO-20260622T153403Z`

## STOCH F017-F018 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/stoch_f017_f018_long_short_audit_20260622T154340Z_RU.md`.
Current fact: implemented `B009/Stochastic 14 K/D` with combined passport F017_F018 `stochastic_14_1m`; action output is `F017_F018_STOCH14_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F017_F018_stoch14_combined_entry_filter.yaml`.
Runtime/backtest: dataset emits `F017_F018_STOCH14_ALLOW` only when `F017_F018_*` params are present; backtest gates entries by this present action column.
Clean result: LONG effective params `LEVEL K LESS level=72`, OOS `-84.05333161848922%`, `51` trades, wins/losses `2/49`, exits `timeout=50`, `sl=1`; SHORT effective params `KD_CROSS UP LOW low=40 high=60 gap=0`, OOS `-17.53680624691214%`, `6` trades, wins/losses `0/6`, exits `timeout=6`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `116/116 OK`; YAML parse PASS; matrix compile PASS for LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-STOCH-F017-F018-NO-GO-20260622T154340Z`

## VOLUME F019-F021 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/volume_f019_f021_long_short_audit_20260622T160207Z_RU.md`.
Current fact: implemented `B010/Объем и поток` with solo passports F019 `vol_chg_1m`, F020 `vol_z_20_1m`, F021 `delta_volume_1m`.
Matrices: `configs/calibration_matrices/passport_actions/F019_vol_chg_1m_entry_filter.yaml`, `F020_vol_z20_1m_entry_filter.yaml`, `F021_delta_volume_1m_entry_filter.yaml`.
Runtime/backtest: dataset emits `F019_VOLCHG_ALLOW`, `F020_VOLZ20_ALLOW`, `F021_DELTAVOL_ALLOW` only when matching params are present; backtest gates entries by present action columns.
Fix applied: F021 `TRUE_DELTA` now requires `buy_volume`/`sell_volume`; if absent, signal is `0`. Pre-fix F021 runs were discarded and F021 was rerun.
Clean result: F019 LONG `-57.151405%/26 trades`; F019 SHORT `-11.835584%/4 trades`; F020 LONG `0%/0 trades`; F020 SHORT `-25.290896%/9 trades`; F021 LONG post-fix `-77.699906%/37 trades`; F021 SHORT post-fix `0%/0 trades`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `118/118 OK`; YAML parse PASS; matrix compile PASS for all F019-F021 LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-VOLUME-F019-F021-NO-GO-20260622T160207Z`

## F022 OBV Slope 5 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f022_obv_slope5_long_short_audit_20260622T162356Z_RU.md`.
Current fact: implemented `B011/OBV slope 5` with solo passport F022 `obv_slope_5_1m`; action output is `F022_OBVSLOPE5_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F022_obv_slope5_1m_entry_filter.yaml`.
Runtime/backtest: dataset emits `F022_OBVSLOPE5_ALLOW` only when `F022_slope_dir`/`F022_slope_thr` are present; backtest gates entries by this present action column.
Clean result: LONG selected `UP thr=7.2`, OOS `0.000000%`, `0` trades; SHORT selected `DOWN thr=8.2`, OOS `-17.47906713400207%`, `3` trades, wins/losses `0/3`, exits `timeout=2`, `sl=1`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `120/120 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-F022-OBV-SLOPE5-NO-GO-20260622T162356Z`

## F023 MFI14 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f023_mfi14_long_short_audit_20260622T163809Z_RU.md`.
Current fact: implemented `B012/MFI14` with combined solo passport F023 `mfi14_1m`; action output is `F023_MFI14_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F023_mfi14_1m_combined_entry_filter.yaml`.
Runtime/backtest: dataset emits `F023_MFI14_ALLOW` only when `F023_*` params are present; backtest gates entries by this present action column.
Clean result: LONG selected `LEVEL GREATER level=88`, OOS `-4.474396882494847%`, `1` trade, exit `timeout`; SHORT selected `LEVEL LESS level=81`, OOS `-20.54653686623259%`, `6` trades, wins/losses `0/6`, exits `timeout=6`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `122/122 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-F023-MFI14-NO-GO-20260622T163809Z`

## DENSITY/VPOC Block A F025/F029/F033/F034 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/density_vpoc_block_a_f025_f029_f033_f034_audit_20260622T165812Z_RU.md`.
Current fact: implemented `B013/DENSITY_A_VPOC_CORE` with solo passports F025 `density_vpoc_distance_60_1m`, F029 `density_vpoc_distance_240_1m`, F033 `density_vpoc_drift_20_1m`, and F034 `density_cluster_ratio_60_240_1m`.
Matrix files: `F025_vpocdist60_entry_filter.yaml`, `F029_vpocdist240_entry_filter.yaml`, `F033_vpocdrift20_entry_filter.yaml`, `F034_clusterratio_entry_filter.yaml`.
Runtime/backtest: dataset emits `F025_VPOCDIST60_ALLOW`, `F029_VPOCDIST240_ALLOW`, `F033_VPOCDRIFT20_ALLOW`, `F034_CLUSTERRATIO_ALLOW` only when matching params are present; backtest gates entries by the present action column.
Clean result: F025 LONG `-60.069331%/20`, F025 SHORT `-6.778638%/3`; F029 LONG `0%/0`, F029 SHORT `-18.625751%/6`; F033 LONG `-14.115533%/4`, F033 SHORT `-3.624721%/1`; F034 LONG `0%/0`, F034 SHORT `-10.692022%/3`.
Final status: `NO_GO`; best tradeful was F033 SHORT but still negative.
Validation: `py_compile PASS`; focused tests `124/124 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.
Boundary: Block B (`F026/F027/F030/F031`) and Block C (`F028/F032`) from the same passport file are planned, not run yet.

## State Version
`CALIBRATION-CURRENT-DENSITY-VPOC-BLOCK-A-NO-GO-20260622T165812Z`

## LEVEL/RANGE/CHANNEL Block A F035-F037 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/level_range_channel_block_a_f035_f036_f037_audit_20260622T171500Z_RU.md`.
Current fact: implemented `B014/LEVEL_A уровни поддержки/сопротивления` with solo passports F035 `support_distance_1m`, F036 `resistance_distance_1m`, and F037 `level_strength_1m`.
Matrix files: `F035_supportdist_entry_filter.yaml`, `F036_resdist_entry_filter.yaml`, `F037_levelstrength_entry_filter.yaml`.
Runtime/backtest: dataset emits `F035_SUPPORTDIST_ALLOW`, `F036_RESDIST_ALLOW`, `F037_LEVELSTRENGTH_ALLOW` only when matching params are present; backtest gates entries by the present action column.
Clean result: F035 LONG `-6.153364%/2`, F035 SHORT `-18.625751%/6`; F036 LONG `-12.920893%/3`, F036 SHORT `-13.301553%/4`; F037 LONG `0%/0`, F037 SHORT `-18.104190%/7`.
Final status: `NO_GO`; best tradeful was F035 LONG but still negative.
Validation: `py_compile PASS`; focused tests `126/126 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.
Boundary: F038 `position_in_range_1m` and F039 `trend_channel_pos_1m` from the same passport file are planned, not run yet.

## State Version
`CALIBRATION-CURRENT-LEVEL-RANGE-CHANNEL-BLOCK-A-NO-GO-20260622T171500Z`

## FIBONACCI_GRID F040-F041 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/fibonacci_grid_f040_f041_long_short_audit_20260622T173112Z_RU.md`.
Current fact: implemented `B015/FIBONACCI_GRID anchor grid` with F040 `fib_0382_distance_1m` and F041 `fib_0618_distance_1m`.
Matrix files: `F040_fib0382dist_entry_filter.yaml`, `F041_fib0618dist_entry_filter.yaml`.
Runtime/backtest: dataset computes confirmed pivot fib grid and emits `F040_FIB0382DIST_ALLOW` / `F041_FIB0618DIST_ALLOW` only when matching params are present; backtest gates entries by the present action column.
Clean result: F040 LONG `0%/0`, F040 SHORT `-27.970937%/9`; F041 LONG `0%/0`, F041 SHORT `-9.615680%/4`.
Final status: `NO_GO`; best tradeful was F041 SHORT but still negative.
Validation: `py_compile PASS`; focused tests `128/128 OK`; matrix compile PASS for F040/F041 LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-FIBONACCI-GRID-F040-F041-NO-GO-20260622T173112Z`

## ENTRY_QUALITY_CONTEXT F042-F044 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/entry_quality_context_f042_f044_long_short_audit_20260622T175033Z_RU.md`.
Current fact: implemented `B016/ENTRY_QUALITY_CONTEXT контекст входа` with F044 `rr_context_estimate_1m`, F042 `tp_context_distance_1m`, and F043 `sl_context_distance_1m`.
Matrix files: `F044_rrcontext_entry_filter.yaml`, `F042_tpcontext_entry_filter.yaml`, `F043_slcontext_entry_filter.yaml`.
Runtime/backtest: dataset computes entry context from `SWING_LEVELS`, `DENSITY_VPOC`, or `FIBONACCI_GRID` and emits canonical plus side-aware action columns. Backtest uses side-aware columns by actual LONG/SHORT signal.
Clean result: F044 LONG `-1.145944%/1`, F044 SHORT `-19.784205%/8`; F042 LONG `-17.392676%/3`, F042 SHORT `0%/0`; F043 LONG `0%/0`, F043 SHORT `-30.313954%/10`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `130/130 OK`; matrix compile PASS for all F042-F044 LONG/SHORT; latest text_guard PASS.

## State Version
`CALIBRATION-CURRENT-ENTRY-QUALITY-CONTEXT-F042-F044-NO-GO-20260622T175033Z`

## BREAKOUT_RETEST F045-F049 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b017_breakout_retest_f045_f049_audit_20260622T181600Z.md`.
Current fact: user supplied `BREAKOUT_RETEST_F045_F049_strict_passport.md`; implemented B017 with isolated solo passports F048 `swing_high_break_flag_1m`, F049 `swing_low_break_flag_1m`, F045 `breakout_flag_1m`, F047 `retest_flag_1m`, and F046 `false_breakout_flag_1m`.
Matrix files: `F048_swinghighbreak_entry_filter.yaml`, `F049_swinglowbreak_entry_filter.yaml`, `F045_breakout_entry_filter.yaml`, `F047_retest_entry_filter.yaml`, `F046_falsebreak_entry_filter.yaml`.
Runtime/backtest: dataset computes confirmed swing levels and breakout/retest gates; backtest gates entries by the present single action column.
Clean result: F048 LONG `0%/0`, F048 SHORT `0%/0`; F049 LONG `-12.862590%/6`, F049 SHORT `-20.254568%/4`; F045 LONG `0%/0`, F045 SHORT `-3.482265%/2`; F047 LONG `-11.000000%/1`, F047 SHORT `-12.464525%/3`; F046 LONG `0%/0`, F046 SHORT `-5.366391%/1`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F045 SHORT, but still negative.
Validation: `py_compile PASS`; focused B017 tests `3/3 OK`; matrix compile PASS for F045-F049 LONG/SHORT; latest text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T181926Z.json`.

## State Version
`CALIBRATION-CURRENT-BREAKOUT-RETEST-F045-F049-NO-GO-20260622T181600Z`

## MARKET_STRUCTURE F050-F052 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_POSITIVE_TEST_CANDIDATE`.
Artifact: `reports/qa_gate/b018_market_structure_f050_f052_audit_20260622T183500Z.md`.
Current fact: user supplied `MARKET_STRUCTURE_F050_F052_strict_passport.md`; implemented B018 with isolated solo passports F050 `bos_up_flag_1m`, F051 `bos_down_flag_1m`, and F052 `choch_flag_1m`.
Matrix files: `F050_bosup_entry_filter.yaml`, `F051_bosdown_entry_filter.yaml`, `F052_choch_entry_filter.yaml`.
Runtime/backtest: dataset computes internal/external market structure state and emits `F050_BOSUP_ALLOW`, `F051_BOSDOWN_ALLOW`, `F052_CHOCH_ALLOW`; backtest gates entries by the present single action column.
Clean result: F050 LONG `0%/0`, F050 SHORT `0%/0`; F051 LONG `0%/0`, F051 SHORT `+2.810523%/1`; F052 LONG `0%/0`, F052 SHORT `0%/0`.
Final status: `POSITIVE_TEST_CANDIDATE`; F051 SHORT is positive but only one OOS trade, so no production GO.
Validation: `py_compile PASS`; focused B018 tests `3/3 OK`; matrix compile PASS for F050-F052 LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-MARKET-STRUCTURE-F050-F052-POSITIVE-TEST-CANDIDATE-20260622T183500Z`

## CANDLE_PATTERNS F053-F060 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b019_candle_patterns_f053_f060_audit_20260622T190530Z.md`.
Current fact: implemented `B019/CANDLE_PATTERNS свечные паттерны` with isolated solo passports F055 `pin_bar_bull_flag_1m`, F056 `pin_bar_bear_flag_1m`, F059 `engulf_bull_flag_1m`, F060 `engulf_bear_flag_1m`, F057 `hammer_flag_1m`, F058 `shooting_star_flag_1m`, F054 `inside_bar_flag_1m`, and F053 `doji_flag_1m`.
Runtime/backtest: dataset uses only closed candles via shift(1)/shift(2) and emits `F053_DOJI_ALLOW`, `F054_INSIDEBAR_ALLOW`, `F055_PINBULL_ALLOW`, `F056_PINBEAR_ALLOW`, `F057_HAMMER_ALLOW`, `F058_SHOOTINGSTAR_ALLOW`, `F059_ENGULFBULL_ALLOW`, `F060_ENGULFBEAR_ALLOW`; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. F059 LONG `-60.087983%/22`; F054 SHORT `-8.438667%/2`; F053 LONG `-11.213252%/3`; all other runs `0%/0`.
Validation: `py_compile PASS`; focused B019 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-CANDLE-PATTERNS-F053-F060-NO-GO-20260622T190530Z`

## DIVERGENCE_PATTERNS F061-F066 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b020_divergence_patterns_f061_f066_audit_20260622T193300Z.md`.
Current fact: implemented `B020/DIVERGENCE_PATTERNS дивергенции` with isolated solo passports F061 `rsi_bull_div_flag_1m`, F062 `rsi_bear_div_flag_1m`, F063 `macd_bull_div_flag_1m`, F064 `macd_bear_div_flag_1m`, F065 `obv_bull_div_flag_1m`, and F066 `obv_bear_div_flag_1m`.
Runtime/backtest: dataset computes confirmed no-repaint price pivot pairs and takes RSI/MACD/OBV values at the same price pivot bars; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. F061 LONG `-7.123789%/2`; F063 LONG `-37.837211%/12`; F065 LONG `-10.822526%/4`; all other runs `0%/0`.
Validation: `py_compile PASS`; focused B020 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-DIVERGENCE-PATTERNS-F061-F066-NO-GO-20260622T193300Z`

## PATTERN_QUALITY F067-F068 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b021_pattern_quality_f067_f068_audit_20260622T194700Z.md`.
Current fact: implemented `B021/PATTERN_QUALITY качество паттерна` with isolated solo passports F067 `pattern_strength_1m` and F068 `pattern_age_bars_1m`.
Runtime/backtest: dataset builds a closed-bar `pattern_event` from already computed pattern flags and emits `F067_PATTERNSTRENGTH_ALLOW` / `F068_PATTERNAGE_ALLOW`; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. F067 LONG `0%/0`; F067 SHORT `-18.202040%/6`; F068 LONG `-6.153364%/2`; F068 SHORT `-59.898861%/26`.
Validation: `py_compile PASS`; focused B021 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-PATTERN-QUALITY-F067-F068-NO-GO-20260622T194700Z`

## CHART_PATTERNS F069-F077 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b022_chart_patterns_f069_f077_audit_20260622T202100Z.md`.
Current fact: implemented `B022/CHART_PATTERNS графические паттерны` with isolated solo passports F069-F077.
Runtime/backtest: dataset computes closed-bar chart-pattern action gates `F069_DOUBLEBOTTOM_ALLOW`, `F070_DOUBLETOP_ALLOW`, `F071_HEADSHOULDERS_ALLOW`, `F072_INVHEADSHOULDERS_ALLOW`, `F073_TRIANGLE_ALLOW`, `F074_PENNANT_ALLOW`, `F075_WEDGERISING_ALLOW`, `F076_WEDGEFALLING_ALLOW`, and `F077_RANGEFLAG_ALLOW`; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. Zero-trade runs are neutral only; tradeful runs are all negative, with best tradeful F072 LONG `-6.837599%/1`.
Validation: `py_compile PASS`; focused B022 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-CHART-PATTERNS-F069-F077-NO-GO-20260622T202100Z`

## PATTERN_CONFIRMATION F078-F079 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b023_pattern_confirmation_f078_f079_audit_20260622T203700Z.md`.
Current fact: implemented `B023/PATTERN_CONFIRMATION confirmation of existing pattern_event` with isolated solo passports F079 `pattern_level_confirm_flag_1m` and F078 `pattern_volume_confirm_flag_1m`.
Runtime/backtest: dataset confirms existing pattern events and emits `F079_PATTERNLEVELCONF_ALLOW` / `F078_PATTERNVOLCONF_ALLOW`; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. F079 LONG/SHORT had zero OOS trades; F078 LONG `-27.682109%/7`; F078 SHORT `-7.323394%/4`.
Validation: `py_compile PASS`; focused B023 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-PATTERN-CONFIRMATION-F078-F079-NO-GO-20260622T203700Z`

## PATTERN_COMPOSITE_ENTRY F080-F081 Passport Run
Status: `IMPLEMENTED_SIDE_SPECIFIC_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b024_pattern_composite_entry_f080_f081_audit_20260622T205500Z.md`.
Current fact: implemented `B024/PATTERN_COMPOSITE_ENTRY kompozitnyy pattern entry` with side-specific passports F080 `pattern_structure_volume_entry_long_1m` and F081 `pattern_structure_volume_entry_short_1m`.
Runtime/backtest: dataset emits `F080_PATTERNLONG_ALLOW` and `F081_PATTERNSHORT_ALLOW`; backtest treats F080 as LONG-only and F081 as SHORT-only.
Clean result: F080 LONG `0.000000%/0`; F081 SHORT `-5.359455%/1`, exit `timeout=1`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B024 tests `3/3 OK`; YAML parse/matrix compile PASS; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T210111Z.json`.

## State Version
`CALIBRATION-CURRENT-PATTERN-COMPOSITE-ENTRY-F080-F081-NO-GO-20260622T205500Z`

## PATTERN_TRADE_CONTEXT F082-F083 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b025_pattern_trade_context_f082_f083_audit_20260622T211600Z.md`.
Current fact: implemented `B025/PATTERN_TRADE_CONTEXT SL/TP context` with isolated solo passports F082 and F083.
Runtime/backtest: dataset emits side-aware F082/F083 gates and backtest applies them as entry filters; baseline exits remain TP/SL/timeout.
Clean result: F082 LONG `0%/0`, F082 SHORT `-25.094610%/7`; F083 LONG `-35.921536%/12`; F083 SHORT `-70.280106%/35`.
Final status: `NO_GO`; no positive tradeful candidate.
Validation: `py_compile PASS`; focused B025 tests `3/3 OK`; matrix compile/passport allowlist PASS; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T211551Z.json`.

## State Version
`CALIBRATION-CURRENT-PATTERN-TRADE-CONTEXT-F082-F083-NO-GO-20260622T211600Z`

## F001-F083 Passport Route Full Audit
Status: `WARN_WITH_COMPLETENESS_GAPS`.
Artifact: `reports/qa_gate/f001_f083_passport_full_audit_20260623.md`.
Matrix purity: `PASS` for existing executable passport matrices (`73` entries, `146` compiled spaces).
Completeness in the pre-F024 audit snapshot: not full; F024 was open then and is closed below, `F026/F027/F028/F030/F031/F032/F038/F039` planned only, `F017/F018` combined.
Runtime/backtest: normal single-pass route isolated; hardening needed to ignore stale `F*_ALLOW` columns outside the active passport action.

## State Version
`CALIBRATION-CURRENT-F001-F083-FULL-AUDIT-WARN-WITH-COMPLETENESS-GAPS-20260623`

## F024 VWAP Distance Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f024_vwap_distance_long_short_audit_20260623T055200Z.md`.
Current fact: previously open `F024` is now implemented as `B026/F024` with isolated action `F024_VWAPDIST_ALLOW`.
Runtime/backtest: dataset computes the action from previous closed-bar VWAP distance; OOS diagnostics show only `F024_VWAPDIST_ALLOW` as entry action gate.
Clean result: F024 LONG `-17.894975%/8`; F024 SHORT `0%/0`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F026/F027/F028/F030/F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F024-VWAP-DISTANCE-NO-GO-20260623T055200Z`

## F026 Density Bin Share 60 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f026_binshare60_long_short_audit_20260623T060100Z.md`.
Current fact: `F026` is now implemented under `B013` with isolated action `F026_BINSHARE60_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_bin_share_60`; OOS diagnostics show only `F026_BINSHARE60_ALLOW` as entry action gate.
Clean result: F026 LONG `-1.145944%/1`; F026 SHORT `-24.712835%/9`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F027/F028/F030/F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F026-BINSHARE60-NO-GO-20260623T060100Z`

## F027 Density Cluster Share 60 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f027_clustershare60_long_short_audit_20260623T062300Z.md`.
Current fact: `F027` is now implemented under `B013` with isolated action `F027_CLUSTERSHARE60_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_cluster_share_60`; OOS diagnostics show only `F027_CLUSTERSHARE60_ALLOW` as entry action gate.
Clean result: F027 LONG `-6.153364%/2`; F027 SHORT `-18.625751%/6`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F028/F030/F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F027-CLUSTERSHARE60-NO-GO-20260623T062300Z`

## F028 Density VPOC Share 60 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f028_vpocshare60_long_short_audit_20260623T064000Z.md`.
Current fact: `F028` is now implemented under `B013` with isolated action `F028_VPOCSHARE60_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_vpoc_share_60`; OOS diagnostics show only `F028_VPOCSHARE60_ALLOW` as entry action gate.
Clean result: F028 LONG `-1.145944%/1`; F028 SHORT `-18.625751%/6`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F030/F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F028-VPOCSHARE60-NO-GO-20260623T064000Z`

## F030 Density Bin Share 240 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f030_binshare240_long_short_audit_20260623T070000Z.md`.
Current fact: `F030` is now implemented under `B013` with isolated action `F030_BINSHARE240_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_bin_share_240`; OOS diagnostics show only `F030_BINSHARE240_ALLOW` as entry action gate.
Clean result: F030 LONG `-13.432324%/3`; F030 SHORT `-24.712835%/9`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F030-BINSHARE240-NO-GO-20260623T070000Z`

## F031 Density Cluster Share 240 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f031_clustershare240_long_short_audit_20260623T071000Z.md`.
Current fact: `F031` is now implemented under `B013` with isolated action `F031_CLUSTERSHARE240_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_cluster_share_240`; OOS diagnostics show only `F031_CLUSTERSHARE240_ALLOW` as entry action gate.
Clean result: F031 LONG `-6.153364%/2`; F031 SHORT `-55.142239%/26`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F031-CLUSTERSHARE240-NO-GO-20260623T071000Z`

## F032 Density VPOC Share 240 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f032_vpocshare240_long_short_audit_20260623T072500Z.md`.
Current fact: `F032` is now implemented under `B013` with isolated action `F032_VPOCSHARE240_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_vpoc_share_240`; OOS diagnostics show only `F032_VPOCSHARE240_ALLOW` as entry action gate.
Clean result: F032 LONG `-6.153364%/2`; F032 SHORT `-18.625751%/6`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F032-VPOCSHARE240-NO-GO-20260623T072500Z`

## F038 Position In Range Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f038_rangepose_long_short_audit_20260623T074000Z.md`.
Current fact: `F038` is now implemented under `B014` with isolated action `F038_RANGEPOSE_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar 240-bar range position; OOS diagnostics show only `F038_RANGEPOSE_ALLOW` as entry action gate.
Clean result: F038 LONG `-13.432324%/3`; F038 SHORT `-4.489987%/1`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F038-RANGEPOSE-NO-GO-20260623T074000Z`

## F039 Trend Channel Position Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f039_channelpos_long_short_audit_20260623T080500Z.md`.
Current fact: `F039` is now implemented under `B014` with isolated action `F039_CHANNELPOS_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar linear regression channel position; OOS diagnostics show only `F039_CHANNELPOS_ALLOW` as entry action gate.
Clean result: F039 LONG `-17.392676%/3`; F039 SHORT `0.000000%/0`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route items: `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F039-CHANNELPOS-NO-GO-20260623T080500Z`

## Passport Result Register F001-F083
Status: `ACTIVE_RESULT_REGISTER`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_RESULT_REGISTER_RU.md`.
Audit: `reports/qa_gate/passport_result_register_audit_20260623T084702Z.md`.

Current fact: the F001-F083 passport route now has a compact result register. It records all feature ids, blocks, decisions, and promotion boundaries.

Important state:
1. Production GO: none.
2. Positive test candidate: `F051 BOS down SHORT`, `+2.810523%`, `1` OOS trade.
3. `F051 SHORT` validation is complete and failed promotion; no current F001-F083 candidate is ready for promotion.
4. Old broad matrices/chronology stay frozen references unless explicitly migrated through passport review.

Validation: id coverage PASS; text_guard PASS, report `reports/qa_gate/recovery_r5_text_guard_20260623T084932Z.json`.

## State Version
`CALIBRATION-CURRENT-F001-F083-RESULT-REGISTER-20260623T084702Z`

## F051 SHORT Multi-Day Validation
Status: `VALIDATION_FAIL_NO_PROMOTION`.
Artifact: `reports/qa_gate/f051_short_multiday_validation_audit_20260623T091000Z.md`.

Current fact: `F051 BOS down SHORT` did not reproduce outside the original one-day positive window.

Validation result:
1. Original baseline `2026-05-31 -> 2026-06-01`: `+2.810523%`, `1` trade.
2. New adjacent windows `2026-05-29`, `2026-05-30`, `2026-05-31`: all `0%`, `0` trades.
3. Gate isolation was clean: `F051_BOSDOWN_ALLOW` only.

State decision: no F001-F083 candidate is promotable after this check.

## State Version
`CALIBRATION-CURRENT-F051-SHORT-VALIDATION-FAIL-20260623T091000Z`

## F001-F083 Passport Route Closeout
Status: `CLOSED_NO_PRODUCTION_GO`.
Artifact: `reports/qa_gate/f001_f083_route_closeout_audit_20260623T091500Z.md`.

Current fact: `F001-F083` is closed for the current route. There is no promotable candidate after F051 validation failed.

Allowed next work:
1. new passport/feature/hypothesis route;
2. new validation idea with an explicit audit boundary;
3. separate exit/risk passports.

## State Version
`CALIBRATION-CURRENT-F001-F083-CLOSED-NO-PRODUCTION-GO-20260623T091500Z`

## Core ML Bot TZ Audit
Status: `PARTIAL_MATCH_WITH_STRONG_CALIBRATION_CORE`.
Artifact: `reports/qa_gate/core_ml_bot_tz_audit_20260623_RU.md`.

Current fact: audited the current project against the user-provided compact 1m ML trading bot core TZ.

Decision: do not create a second `trading_bot/` tree. Use `src/mlbotnav` as the implementation core, add thin contracts/facades, then close missing CORE features, trade-log schema, MAE/MFE, ML labels, and separate exit/risk passports.

## State Version
`CORE-ML-BOT-TZ-AUDIT-PARTIAL-MATCH-20260623T100126Z`
## ML Trade Dataset Stage 2.2 Passport Context 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.

Passport context is now added to pipeline and OOS trade CSV outputs before write. The shared helper resolves metadata from `configs/calibration_action_passports.yaml`.

Checks passed: changed modules `py_compile PASS`; focused tests `55/55 OK`; `text_guard PASS`.

Next strict WBS step: `2.3 Добавить trade identity`.
## ML Trade Dataset Stage 2.3 Trade Identity 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.

Trade identity is now added to pipeline and OOS trade CSV outputs before write. The shared helper emits deterministic `trade_id` values for rows where `side != 0` and fills `entry_signal_time_utc` from the signal bar.

Checks passed: changed modules `py_compile PASS`; focused tests `56/56 OK`; `text_guard PASS`.

Next strict WBS step: `2.4 Добавить duration labels`.

## B001 Single-Worker Fast Finish 2026-06-24
Status: `diagnosed_not_worker_failure`.
Artifact: `reports/qa_gate/b001_single_worker_fast_finish_audit_20260624T180000Z_RU.md`.

Проверенный запуск `long_only_pool_20260624t175647z_w1` получил профиль `max_threads=9`, `search_workers=9`, `workers_used=9`, `n_trials_override=42`.

Быстрое завершение связано не с недогрузом воркеров, а с пустым семейным входным гейтом B001 strict `5/5`: лучший кандидат `EMPTY_ACTION_GATE`, `0` сделок, `signal_count_after_entry_action_gates=0`.

Следующий диагностический шаг: single-worker `1x9/9`, но family-unified `4/5` на 1д/1д; если пусто, проверить `3/5`.

## Optuna Worker Profile Correction 2026-06-24
Status: `profile_rule_corrected`.
Artifact: `reports/qa_gate/optuna_1x9_vs_3x3_worker_audit_20260624T183000Z_RU.md`.

Факт: `1x9/9` не равен старому `3x3/9` по физической нагрузке. `3x3/9` создает три отдельных Python-процесса, а `1x9/9` один процесс с внутренним `n_jobs=9`.

Рабочий профиль для нагрузочных прогонов снова считать `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`. `1x9/9` использовать только как диагностику одной Optuna-истории.

## B001 Family-Unified 4/5 LONG 2026-06-24
Status: `done_tradeful_negative_no_promotion`.
Artifact: `reports/qa_gate/b001_family_unified_4of5_long_3x3_audit_20260624T184500Z_RU.md`.

Проверка `1д/1д` на рабочем профиле `3x3/9` завершена. Launcher `OK`, лучший worker `w3`, OOS `-5.071620930989562%`, `1` сделка. Семейный вход `4/5` сработал корректно: `F001..F004=1`, `F005=0`.

Следующий B001 diagnostic: `3/5 LONG` на `3x3/9`, если продолжаем раздушивать семейный вход.
## Visual Entry Signal-Entry Contract v2 2026-06-25
Текущий статус: `DEV_SIGNAL_ENTRY_CONTRACT_READY_NEEDS_USER_VISUAL_CONFIRM`.

Исправлена логика ручной разметки: свеча с фитилем/дном является сигналом после закрытия, а вход считается на open следующей свечи.

Рабочий v2-контракт: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/manual_entries.json`.

Zoom-проверка: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_zoom_panels_20260625T102849Z.png`.

Формула LONG slippage: `entry_price_with_slippage = entry_open_price * (1 + slippage_bps / 10000)`, сейчас `slippage_bps=5`.

До визуального подтверждения пользователем v2 нельзя передавать в ML и нельзя считать финальным scorer target.

## Visual Entry Instrument Stack Audit 2026-06-25
Текущий статус: `DEV_AUDIT_READY_NEXT_NOISE_SUPPRESSION_RUNNER`.

Аудит: `reports/final_review/visual_entry_v3/instrument_stack_audit/visual_entry_instrument_stack_audit_20260625_RU.md`.

Факт: следующий шаг по visual-entry - не ML и не большая Optuna, а diagnostic runner для кластерного подавления шума. `DQ01/DQ03` являются картой зон дна, но не кандидатом на promotion.

Рабочий следующий шаг: `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`, цель DEV - сохранить `>=9/11` попаданий и снизить false у `DQ01` с `73` хотя бы до `<=30`, затем сделать PNG-оверлеи.

Граница: ML/export/promotion запрещены до трехдневной проверки `2026-05-12` DEV, `2026-05-13` validation, `2026-05-14` holdout.

## Visual Entry Noise Suppression Runner 2026-06-25
Текущий статус: `DEV_RUNNER_DONE_NO_ML`.

Добавлен cluster-priority runner: `src/mlbotnav/visual_entry_noise_suppression_cluster_priority_runner.py`.

Лучший слой `CP01_DQ01_CLUSTER10_SCORE12` на `2026-05-12`: `9/11`, `28` false, `37` entries, precision `0.2432`, recall `0.8182`, f1 `0.3750`. Это улучшает шум относительно `DQ01` (`73` false), но теряет `08:26` и `17:00`.

Отчет: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_noise_suppression_cluster_priority_20260512_DEV_RU.md`.
PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp01_dq01_cluster10_score12_20260625T150100Z.png`.

В ML ничего не передавать. Следующее действие: добор пропущенных `08:26` и `17:00` с контролем false.

## Visual Entry CP06 Recover 2026-06-25
Текущий статус: `DEV_RECOVER_DONE_11_OF_11_NO_ML`.

`CP06_CP01_RECOVER_NOWICK_LATE_RETEST` закрыл оба пропуска `CP01`: `08:26` и `17:00`.

Итог DEV `2026-05-12`: `11/11`, `0` missed, `28` false, `39` entries, precision `0.2821`, recall `1.0000`, f1 `0.4400`.

PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp06_cp01_recover_nowick_late_retest_20260625T151725Z.png`.

Граница: это diagnostic-only visual layer. До validation/holdout и ручного `APPROVED_FOR_ML` в ML ничего не передавать.

## Visual Entry RBKD V0 2026-06-29
Current status: `DEV_RBKD_V0_BUILT_TOO_NOISY_NO_ML_NEXT_SWING_SUPPORT_EVENT`.

`REVERSAL_BOTTOM_KNIFE_DROP_V0` построен и проверен на `2026-05-13` validation и `2026-05-14` holdout. Он работает по честному контракту `next_bar_open_after_signal_close`, но дает слишком много ложных входов:

1. `2026-05-13`: `2/9` hits, `81` false.
2. `2026-05-14`: `1/17` hits, `83` false.

Decision: no ML export, no promotion, no production GO. Следующая механика должна быть `SWING_SUPPORT_RETEST_EVENT_V1`, потому что пользовательские ручные входы часто являются support/retest/trend-dip событиями, а не чистой перепроданностью.

Artifact: `reports/final_review/visual_entry_v3/reversal_bottom_knife_drop/visual_entry_reversal_bottom_knife_drop_audit_20260629T090101Z_RU.md`.
## Visual Entry SSRE V1 2026-06-29
Current status: `DEV_SSRE_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Entry-only runner `SWING_SUPPORT_RETEST_EVENT_V1` проверен. Он не тянет сделки и не использует будущую доходность: только совпадение входа на следующем open с ручными low-входами.

Результат слабый:

1. `2026-05-13`: `1/9` hits, `29` false.
2. `2026-05-14`: `1/17` hits, `26` false.

Decision: no ML export, no promotion. Следующий рабочий слой: `SIGNIFICANT_LOW_SELECTOR_V1`, потому что проблема не в выходе из сделки, а в выборе именно значимого low.

Artifact: `reports/final_review/visual_entry_v3/swing_support_retest_event/visual_entry_swing_support_retest_event_audit_20260629T092400Z_RU.md`.
## Fresh Strategy Overlay 2026-06-29
Current status: `DEV_FRESH_OVERLAY_DONE_ENTRY_ONLY_NO_CALIBRATION_NO_ML`.

Fresh clean overlays созданы для `2026-05-13` и `2026-05-14`. Это entry-only стенд без cooldown и без калибровки.

Artifact: `reports/final_review/visual_entry_v3/fresh_strategy_overlay/visual_entry_fresh_strategy_overlay_audit_20260629T113100Z_RU.md`.

Decision: использовать отдельные PNG по стратегиям, не combined. ML/export/promotion запрещены.
## User Red Arrows V2 Fixed 2026-06-29
Current status: `HOLDOUT_DAY_USER_RED_ARROWS_V2_FIXED_AUTO_DETECTED_NEEDS_VISUAL_CONFIRM`.

Новый пользовательский эталон low-входов сохранен:

`reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries.json`

Всего снято `17` входов. Предыдущая авторазметка на `18` входов была исправлена: один тонкий фрагмент красной линии удален как ложная стрелка. Это auto-detected разметка со скрина, поэтому перед использованием как строгого scorer target нужен визуальный confirm по PNG:

`reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries_v2_fixed_signal_entry_verify_20260629T115000Z.png`

## Significant Low Selector V1 2026-06-29
Current status: `DEV_SIGNIFICANT_LOW_SELECTOR_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Добавлен и прогнан `SIGNIFICANT_LOW_SELECTOR_V1` против `17` пользовательских low-входов `SOLUSDT 1m 2026-05-14`.

Аудит: `reports/final_review/visual_entry_v3/significant_low_selector/visual_entry_significant_low_selector_audit_20260629T125000Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/significant_low_selector/visual_entry_family_overlay_2026-05-14_sls_v1_01_sls06_hot_reclaim_strict_false_control_20260629T124723Z.png`.

Итог: лучший f1 у `SLS06` = `5/17` hits и `71` false; самый широкий `SLS10` = `13/17`, но `463` false. Это не кандидат, не ML, не promotion. Следующий слой: `LOW_CLUSTER_RANKER_V2`.

## Low Cluster Ranker V2 2026-06-29
Current status: `DEV_LOW_CLUSTER_RANKER_V2_ENTRY_ONLY_DONE_REDUCED_FALSE_LOW_RECALL_NO_ML`.

Добавлен кластерный V2: `src/mlbotnav/visual_entry_low_cluster_ranker_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/low_cluster_ranker/visual_entry_low_cluster_ranker_audit_20260629T133000Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/low_cluster_ranker/visual_entry_family_overlay_2026-05-14_lcr_v2_01_lcr04_late_low_with_reclaim_cluster_20260629T132833Z.png`.

Итог: `LCR04` = `3/17`, `10` false; `LCR07` = `2/17`, `4` false; `LCR06` = `7/17`, `64` false. V2 не кандидат и не ML; следующий шаг - режимное разделение missed-входов.
# Visual Entry Regime Split Ranker V1 2026-06-29
Current status: `DEV_REGIME_SPLIT_RANKER_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Добавлен режимный entry-only слой для пользовательских low-входов `SOLUSDT 1m 2026-05-14`: `src/mlbotnav/visual_entry_regime_split_ranker_runner.py`.

Режимы: `DEEP_CAPITULATION`, `HOT_RECLAIM_SUPPORT`, `TREND_DIP_CONTINUATION`, `STRUCTURE_BOS_FIBO_VOLUME`.

Результат: больше всего целей ловят `STRUCTURE` и `TREND` (`7/17`), но false слишком много (`84-95`). `DEEP` чище (`12` false), но ловит только `2/17`. Это diagnostic-only, в ML ничего не передавать.

Аудит: `reports/final_review/visual_entry_v3/regime_split_ranker/visual_entry_regime_split_ranker_audit_20260629T134600Z_RU.md`.

## Visual Entry Regime False Suppression V2 2026-06-29
Current status: `DEV_REGIME_FALSE_SUPPRESSION_V2_ENTRY_ONLY_DONE_STILL_TOO_NOISY_NO_ML`.

Добавлен suppress-слой по режимам: `src/mlbotnav/visual_entry_regime_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_regime_false_suppression_audit_20260629T135843Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_family_overlay_2026-05-14_regime_false_suppression_v2_01_fsv21_union_strict_false_control_20260629T135626Z.png`.

Итог: лучший `FSV21` = `7/17` hits и `41` false; `FSV02` deep = `2/17` hits и `4` false. V2 не кандидат, не ML, не promotion. Следующий слой: `ONLINE_LOW_EVENT_QUALITY_V3`.

## Visual Entry Online Low Event Quality V3 2026-06-29
Current status: `DEV_ONLINE_LOW_EVENT_QUALITY_V3_ENTRY_ONLY_DONE_CLEANER_LOW_RECALL_NO_ML`.

Добавлен event-quality слой: `src/mlbotnav/visual_entry_online_low_event_quality_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_online_low_event_quality_audit_20260629T141715Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_family_overlay_2026-05-14_online_low_event_quality_v3_01_olev20_union_event_quality_balanced_20260629T141647Z.png`.

Итог: `OLEV20` = `3/17` hits, `7` false, `10` entries. V3 не кандидат, не ML, не promotion. Следующий слой: `DEEP_RECOVERY_AND_HOT_RECALL_V4`.

## Visual Entry Deep Recovery And Hot Recall V4 2026-06-29
Current status: `DEV_DEEP_RECOVERY_AND_HOT_RECALL_V4_ENTRY_ONLY_DONE_BETTER_BALANCE_NO_ML`.

Добавлен V4 runner: `src/mlbotnav/visual_entry_deep_recovery_hot_recall_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_deep_recovery_hot_recall_audit_20260629T144050Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_family_overlay_2026-05-14_deep_recovery_hot_recall_v4_01_drhr20_olev20_plus_deep_recovery_20260629T144015Z.png`.

Итог: `DRHR20` = `5/17` hits, `13` false, `18` entries, f1 `0.2857`. V4 не кандидат, не ML, не promotion. Следующий слой: `HOT_TREND_FALSE_SUPPRESSION_V5`.

## Visual Entry Hot Trend False Suppression V5 2026-06-29
Рабочий статус: `DEV_HOT_TREND_FALSE_SUPPRESSION_V5_ENTRY_ONLY_DONE_RECALL_UP_FALSE_STILL_HIGH_NO_ML`.

V5 добавил строгий фильтр для hot/trend diagnostic из V4. Фильтр `HTFS01` оставляет pullback/reclaim рядом с event-low и режет широкую support-полку и перегретый MFI.

Итог:
1. `HTFS20_UNION_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `9/17` hits, `14` false, `23` entries, f1 `0.4500`.
2. `HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `4/17` hits, `1` false, `5` entries.
3. Сырой `HTFS09_BROAD_HOT_TREND_DIAGNOSTIC`: `4/17`, `35` false.

Артефакты:
1. Код: `src/mlbotnav/visual_entry_hot_trend_false_suppression_runner.py`.
2. Тест: `tests/test_visual_entry_hot_trend_false_suppression_runner.py`.
3. Аудит: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_hot_trend_false_suppression_audit_20260629T145900Z_RU.md`.
4. Главный PNG: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_family_overlay_2026-05-14_hot_trend_false_suppression_v5_01_htfs20_union_htfs01_hot_trend_strict_false_suppression_20260629T145736Z.png`.

Контракт сохранен: `signal close -> next open`, `slippage_bps=5`, `lookahead=NO`, без entry-candle OHLCV, без TP/SL/MFE/MAE/future return, без cooldown `30/45/60/90`, без ML.

Следующий шаг: `BASE_FALSE_SUPPRESSION_V6`, цель - уменьшить ложные входы базовой V4-части и не потерять чистые входы `HTFS01`.

## Visual Entry Base False Suppression V6 2026-06-29
Рабочий статус: `DEV_BASE_FALSE_SUPPRESSION_V6_ENTRY_ONLY_DONE_BEST_CURRENT_ONE_DAY_NO_ML`.

V6 разделил базовую V4-часть по источнику: `OLEV20` support-reclaim и `DEEP_RECOVERY` режутся разными past-only правилами. Чистый `HTFS01` из V5 подключен без изменения.

Итог:
1. `BFS20_UNION_BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION_PLUS_HTFS01`: `9/17` hits, `1` false, `10` entries, f1 `0.6667`.
2. `BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION`: `5/17` hits, `0` false.
3. `BFS90_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `4/17` hits, `1` false.

Попадания лучшего union: `03:23`, `06:41`, `10:48`, `12:06`, `14:13`, `15:18`, `15:45`, `16:54`, `17:34`.

Единственный false: `18:47`.

Артефакты:
1. Код: `src/mlbotnav/visual_entry_base_false_suppression_runner.py`.
2. Тест: `tests/test_visual_entry_base_false_suppression_runner.py`.
3. Аудит: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_base_false_suppression_audit_20260629T151215Z_RU.md`.
4. Главный PNG: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_family_overlay_2026-05-14_base_false_suppression_v6_01_bfs20_union_bfs01_base_source_split_strict_false_suppression_plus_htfs01_20260629T151147Z.png`.

Контракт сохранен: `signal close -> next open`, `slippage_bps=5`, `lookahead=NO`, без entry-candle OHLCV, без TP/SL/MFE/MAE/future return, без cooldown `30/45/60/90`, без ML.

Следующий шаг: validation `2026-05-13` без изменения параметров V6.

## Visual Entry V6 Validation Fail 2026-06-29
Рабочий статус: `VALIDATION_FAIL_V6_DOES_NOT_GENERALIZE_NO_ML`.

Проверка V6 на `2026-05-13` validation без изменения параметров провалилась:

1. `BFS20_UNION_BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION_PLUS_HTFS01`: `0/9` hits, `1` false, `1` entry.
2. `BFS90_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `0/9` hits, `1` false, `1` entry.
3. `BFS00_BASE_V4_RAW`: `0/9` hits, `17` false, `17` entries.

Validation targets: `00:18`, `01:08`, `03:30`, `07:45`, `08:48`, `12:54`, `16:16`, `19:44`, `22:31`.

Артефакты:
1. Аудит: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_base_false_suppression_validation_audit_20260629T155000Z_RU.md`.
2. JSON: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_base_false_suppression_v6_20260513_VALIDATION_DAY.json`.
3. Главный PNG: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_family_overlay_2026-05-13_bfs_v6_03_u_bfs01_bss_s_fs_h01_20260629T154949Z.png`.

Фикс инфраструктуры: укорочен label PNG в `src/mlbotnav/visual_entry_base_false_suppression_runner.py`, потому что Windows упал на слишком длинном имени файла. Логика сигналов не менялась.

Следующий шаг: `GENERALIZATION_V7`, не ML, не Optuna.
# Current State 2026-06-29 Visual Entry NEGATIVE_CONTEXT_SUPPRESSION_V8

Текущий статус: `NEGATIVE_CONTEXT_SUPPRESSION_V8_PARTIAL_BRICK_NO_ML`.

V8 готов как suppress diagnostic:

1. `src/mlbotnav/visual_entry_negative_context_suppression_v8_runner.py`;
2. `tests/test_visual_entry_negative_context_suppression_v8_runner.py`;
3. `reports/final_review/visual_entry_v3/negative_context_suppression_v8/visual_entry_negative_context_suppression_v8_audit_20260629T173500Z_RU.md`.

Главный результат: найден первый чистый кирпич `V8_02_HOT_CHAIN_EVENT_LOW_SUPPRESSION` на validation `2026-05-13`: `1/9`, `0` false, вход `08:48`. Но это не стратегия, потому что recall низкий.

На holdout `2026-05-14` лучший отдельный режим `V8_01_HOT_FIRST_NEGATIVE_SUPPRESSION` дал `4/17`, `29` false. Union все еще шумный: `11/17`, `168` false. В ML ничего не передавать.

Следующий шаг: `V9_BRICK_BY_BRICK_SELECTOR`: отдельный чистый кирпич для hot-chain оставить, затем строить отдельные селекторы для early-hot и deep-terminal без общего noisy union.

# Current State 2026-06-29 Visual Entry GENERALIZATION_V7

Текущий статус: `GENERALIZATION_V7_DIAGNOSTIC_FAIL_NO_ML`.

V7 diagnostic runner готов и проверен:

1. `src/mlbotnav/visual_entry_generalization_v7_runner.py`;
2. `tests/test_visual_entry_generalization_v7_runner.py`;
3. `reports/final_review/visual_entry_v3/generalization_v7/visual_entry_generalization_v7_audit_20260629T172000Z_RU.md`.

Главный итог: V7 не обобщился. На `2026-05-13` лучший режим дал только `1/9` при `22` false; на `2026-05-14` union поймал `11/17`, но дал `203` false. В ML ничего не передавать.

Практический вывод: проблема сейчас не в нехватке recall, а в отсутствии сильного отрицательного контекста. Следующий слой должен резать шум: боковые микролои, верхние горячие полки, повторные retest-серии и ранние сигналы до настоящего значимого low.

# Current State 2026-06-30 C02 Split/Router

Текущий статус: `C02_SPLIT_ROUTER_DECISION_V0_COMPLETE_NO_SCORER_NO_ML_NO_OPTUNA`.

Активный свежий процесс идет по `FRESH_TARGET_LED_WORKFLOW_READY_NO_ML`, а не по старым V7/V8/V9/V10/V11.

Пункт рельсов `8.3` завершен: C02 разделен на ядро, router-ветки и negative controls. Один широкий C02 scorer запрещен.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.png`.

Следующий подпункт: `8.3.1_DESIGN_C02A_TRUE_DEEP_CAPITULATION_CORE_RULES_FROM_PAST_ONLY_FEATURES_NO_SCORER_YET`.

# Current State 2026-06-30 C02 Price/Visual Fix

Текущий статус: `C02_SPLIT_ROUTER_PRICE_CLARITY_FIX_V0_COMPLETE_NO_SCORER_NO_ML_NO_OPTUNA`.

По замечанию пользователя исправлен рабочий визуал C02: добавлены цены входа `entry_open_price`, учетный `entry + 5 bps`, high-res full-day PNG и SVG/zoom-sheet без растрового размытия.

Основные артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_ENTRY_PRICE_TABLE_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_ZOOM_SHEET_V0_20260630.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_FULL_DAY_HIRES_V0_20260630.png`.

Цена входа нужна только для исполнения/учета/визуального контроля и запрещена как признак выбора входа.

# Current State 2026-06-30 C02A Rules Draft

Текущий статус: `C02A_TRUE_DEEP_CAPITULATION_RULES_V0_DRAFT_WAIT_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт `8.3.1` выполнен как draft без scorer. C02A rules V0 пропускают только `C02E03/M01`, `C02E04/M02`, `C02E10/M08` и отклоняют negative controls `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_VISUAL_V0_20260630.png`.

Следующий подпункт: `8.3.1_USER_VISUAL_REVIEW_C02A_RULES_V0_BEFORE_SCORER`.
# Current State 2026-06-30 Fresh Target-Led Visual Entry Workflow

Текущий статус: `FRESH_TARGET_LED_WORKFLOW_READY_NO_ML`.

Создан новый рабочий протокол: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_FRESH_PROCESS_TZ_RU.md`.

Рабочая линия меняется: старые visual-entry версии больше не являются очередью следующего действия. Новый порядок начинается с пользовательских `T01..T10` на чистом графике, затем идет классификация входов, стратегия под один тип, паспорт, entry-only проверка, target-lock, и только потом Optuna.

ML/export/promotion запрещены.

# Current State 2026-06-30 Fresh Target-Led Start

Текущий статус: `FRESH_TARGET_LED_DAY_SELECTED_LEDGER_READY_NO_ML`.

Первый свежий target-led шаг выполнен на одном дне: `2026-05-14`, `SOLUSDT`, `1m`, `core`.

Артефакты:
1. `src/mlbotnav/visual_entry_fresh_target_ledger.py`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/fresh_target_led_clean_chart_SOLUSDT_1m_2026-05-14_20260630T062202Z.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10.json`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10_RU.md`.

Ledger содержит T01..T10. После visual review `T04` отклонена, `T07` подтверждена с ручной правкой времени, остальные точки пока требуют подтверждения.

Первый кластер для ручной проверки после отклонения T04: `HOT_RECLAIM_SUPPORT`, `T07/T08`. Это не стратегия и не lock.

`T04` отклонена пользователем на visual review: не подходящая точка входа.

`T07` подтверждена с ручной правкой времени: signal `2026-05-14T10:42:00Z`, LONG entry `2026-05-14T10:43:00Z`. Старое автоположение `10:48 -> 10:49` не использовать.

`T08` исправлена по пользовательской нарисованной метке: предполагаемый signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`; статус требует короткого подтверждения.

ML/export/promotion и Optuna запрещены.

Активные рельсы процесса: `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_RAILS_RU.md`.
# Current State 2026-06-30 Fresh Target-Led User Marked Order

Текущий статус: `USER_MARKED_DEVELOPMENT_ORDER_NEEDS_ZOOM_CONFIRM_NO_ML`.

Пользователь дал новый порядок разработки входов на `SOLUSDT 1m 2026-05-14`: красные прямоугольники на full-day графике слева направо. Машинно снят ordered-ledger `M01..M15`; каждая точка остается `needs_zoom_confirm`, пока пользователь не подтвердит zoom.

`T08` подтверждена: signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`.

Первый zoom для ручного решения: `M01`, предполагаемый signal `2026-05-14T03:23:00Z`, LONG entry `2026-05-14T03:24:00Z`.

PNG: `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M01_user_marked_order_zoom_signal_0323_entry_0324.png`.

Это еще не стратегия и не target-lock. Optuna/ML/export запрещены.
# Current State 2026-06-30 M01 Confirmed

Текущий статус: `M01_GOLD_USER_VISUAL_CONFIRMED_NEXT_M02_NO_ML`.

`M01` подтвержден пользователем как подходящий: signal `2026-05-14T03:23:00Z`, LONG entry `2026-05-14T03:24:00Z`.

Следующий zoom-кандидат показан: `M02`, предполагаемый signal `2026-05-14T03:58:00Z`, LONG entry `2026-05-14T03:59:00Z`.

PNG: `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M02_user_marked_order_zoom_signal_0358_entry_0359.png`.
# Current State 2026-07-01 Dataset Base V1 After Unlabeled15 Feedback

Текущий статус: `TARGET_LED_DATASET_BASE_V1_AFTER_UNLABELED15_FEEDBACK_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA`.

Разбор `15` спорных кандидатов закрыт по текущим авто-точкам: `LA018` и `LA020` приняты как нормальные входы, остальные `13` текущих entry отклонены. Для `LA026`, `LA048`, `LA057`, `LA059`, `LA062` пользователь указал стрелками возможные другие места входа, но они пока не внесены как gold, потому что нужна точная минута через zoom/time.

Новая база V1: `107` строк, `28` positive, `79` negative, `0` unlabeled. Это не ML-export и не обучение.

Рабочий визуал: `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v1_after_unlabeled15_feedback_v1/TARGET_LED_UNLABELED15_USER_FEEDBACK_V1_ON_CHART_20260701.png`.
# Current State 2026-07-01 Dataset Quality Audit V0

Текущий статус: `TARGET_LED_DATASET_QUALITY_AUDIT_V0_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA`.

По базе `28/79` выполнен аудит качества блоков. Главный вывод: нельзя использовать простую сумму совпавших блоков как сигнал. `safe_core_hit_count=5/6` шумит.

Первый рабочий путь: строить узкий паспорт по `SUPPORT_RETEST_LOW` или `TREND_DIP_CONTINUATION`. `LOW_ANCHOR_RECLAIM` в текущем виде блокируется как standalone allow.

Рабочий отчет: `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_quality_audit_v0/TARGET_LED_DATASET_QUALITY_AUDIT_V0_20260701_RU.md`.
# Current State 2026-07-01 ML Dataset Ladder

Текущий статус: `FRESH_TARGET_LED_ML_DATASET_LADDER_LOCKED_NO_ML_NO_OPTUNA`.

Чтобы не перепрыгивать шаги, создана лестница: `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_ML_DATASET_LADDER_RU.md`.

Текущий следующий подпункт: `2.1_SUPPORT_RETEST_LOW_REVIEW_SHEET_9_GOOD_16_BAD_NO_ML_NO_OPTUNA`.

После этого разрешен только draft-паспорт `SUPPORT_RETEST_LOW`. ML/export/training/Optuna остаются запрещены.
# Current State 2026-07-01 SUPPORT_RETEST_LOW Review Sheet V0

Текущий статус: `SUPPORT_RETEST_LOW_REVIEW_SHEET_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Пункт `2.1_SUPPORT_RETEST_LOW_REVIEW_SHEET_9_GOOD_16_BAD_NO_ML_NO_OPTUNA` выполнен. Собран PNG по `25` примерам: `9` good, `16` bad.

Рабочий PNG: `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_review_sheet_v0/SUPPORT_RETEST_LOW_REVIEW_SHEET_V0_9GOOD_16BAD_20260701.png`.

Следующий шаг только после user review: если `норм`, делать draft-паспорт `SUPPORT_RETEST_LOW`; если `фиксить`, править разметку/точки.
# Current State 2026-07-01 SUPPORT_RETEST_LOW Passport Draft V0

Текущий статус: `SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Draft-паспорт `SUPPORT_RETEST_LOW` создан после user `норм` по review-sheet. Это contract draft, не scorer и не target-lock.

Рабочие артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_passport_draft_v0/SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_20260701_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_passport_draft_v0/SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_CARD_20260701.png`.

Следующий шаг только после user `норм / фиксить`: entry-only PNG/scorer seed-check по этому паспорту. ML/Optuna запрещены.
# Current State 2026-07-02 SUPPORT_RETEST_LOW Entry-Only Scorer V0

Текущий статус: `SUPPORT_RETEST_LOW_ENTRY_ONLY_SCORER_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_TARGET_LOCK`.

Entry-only seed-check V0 выполнен: good kept `9/9`, bad rejected `8/16`, false entries `8/16`. Статус результата: `SEED_MUST_KEEP_PASS_FALSE_ENTRIES_TOO_MANY`.

Рабочий PNG: `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_entry_only_scorer_v0/SUPPORT_RETEST_LOW_ENTRY_ONLY_SCORER_V0_SEED_CHECK_20260702.png`.

Следующий шаг: user review PNG, затем `V1_REJECT_GUARDS` по 8 оранжевым false-positive. Не делать lock, multi-day, Optuna или ML.

# Current State 2026-07-02 Outcome Low Miner V0

Текущий статус: `OUTCOME_LOW_MINER_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_SCORER`.

Создан отдельный тест по предложению пользователя: low-кандидат строится без future-признаков, entry считается на следующем `open` с `+5 bps`, затем offline проверяется, был ли ход `+1.5%` в течение `360` минут.

Результат на `SOLUSDT 1m`:

- `2026-05-14`: `14` кандидатов, `5` hit `+1.5%`;
- `2026-05-15`: `12` кандидатов, `1` hit `+1.5%`.

Главный вывод: тест полезен как быстрый сбор сильных примеров, но `+1.5%` слишком строгий, чтобы заменить ручную target-led разметку. Это не ML, не scorer, не target-lock и не Optuna.

Рабочие PNG для пользователя:

1. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260514_20260702.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260515_20260702.png`.

# Current State 2026-07-02 Outcome Low Miner 1pct Comparison

Текущий статус: `OUTCOME_LOW_MINER_V0_TARGET_1PCT_COMPARISON_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_SCORER`.

Сделан повтор того же теста с target `+1.0%`. Логика low-кандидата не менялась, изменена только offline outcome-метка.

Результат:

- `2026-05-14`: `14` кандидатов, `7` hit `+1.0%`;
- `2026-05-15`: `12` кандидатов, `3` hit `+1.0%`.

Рабочие PNG:

1. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260514_20260702.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260515_20260702.png`.

Вывод: `+1.0%` лучше подходит как mining/review threshold, чем `+1.5%`, но остается только outcome-layer.

# Current State 2026-07-02 Outcome Miner Correction

Текущий статус: `RETURN_TO_SIGNIFICANT_LOCAL_LEVELS_NO_ML_NO_OPTUNA`.

Пользователь указал, что широкий sweep является перебором и противоречит нашей текущей учебе по значимым локальным low/уровням. Рельсы перечитаны: `cooldown-сетки` запрещены как замена логике входа.

Широкий sweep остается только диагностикой. Рабочий следующий путь: `SIGNIFICANT_LEVEL_LOW_REVIEW_V0`, где сначала ищется значимый локальный уровень/low по left-context, а outcome `+0.8%/+1.0%` используется только после этого как метка проверки движения.
## Current State 2026-07-02 Good 1pct Review Pool

Текущий статус: `GOOD_1PCT_REVIEW_POOL_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Создан быстрый сборщик review-пула по диапазону дат: `src/mlbotnav/visual_entry_good_1pct_review_pool.py`.

Правило сохранено без подмены рельс: значимый low = `signal`, вход = `entry open` следующей свечи, расчетная цена исполнения = `entry open + 5bps`, цель = `+1%` от расчетной цены исполнения. Диапазон `0/5/10bps` сохраняется только как execution band для аудита.

Smoke-запуск на `2026-05-13`:

- run_id: `smoke_20260513_20260702_080455`;
- кандидатов: `87`;
- GOOD: `5` (`4` strong, `1` soft);
- BAD: `82`.

Артефакты smoke:

1. `reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/smoke_20260513_20260702_080455/GOOD_1PCT_REVIEW_POOL_RECORDS.csv`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/smoke_20260513_20260702_080455/GOOD_1PCT_REVIEW_POOL_PAYLOAD.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/smoke_20260513_20260702_080455/GOOD_1PCT_REVIEW_POOL_REPORT_RU.md`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/smoke_20260513_20260702_080455/GOOD_1PCT_REVIEW_POOL_DAY_OVERVIEW_20260513.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/smoke_20260513_20260702_080455/GOOD_1PCT_REVIEW_POOL_GOOD_CLOSEUPS_PAGE_01.png`.

Добавлена VS Code задача: `Visual Entry: Good 1pct Review Pool (NO ML/OPTUNA)`.

Дополнительный mini-run W20 `2026-05-13..2026-05-15` после фикса zoom-окна:

- run_id: `W20_mini_zoomfix_20260702_081003`;
- кандидатов: `261`;
- GOOD: `73`;
- BAD: `188`;
- по дням: `2026-05-13` = `5` GOOD / `82` BAD, `2026-05-14` = `55` GOOD / `30` BAD, `2026-05-15` = `13` GOOD / `76` BAD.

Вывод по W20 mini: механический `+1%` быстро находит много потенциальных сделок, но не является gold-разметкой. Его использовать как review-pool для глаз, затем руками переносить только подтвержденные входы в approved-ledger.

Граница: это не ML/export/training, не scorer, не target-lock и не Optuna. Future outcome хранится только как offline label после найденного low-кандидата.

## Current State 2026-07-02 DCA Risk Audit V0

Текущий статус: `DCA_RISK_AUDIT_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_API`.

Создан risk-audit для `GOOD_1PCT` learning pool W18-W20. Скрипт читает готовые кандидаты, считает `+0.5/+1.0/+1.5/+2.0/+4.0%` outcome-фазы, active open count, hold time, basket drawdown и классы риска.

Рабочий ранс: `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415`.

Итог:

- `573` GOOD из `1528` записей;
- all GOOD max active = `44`;
- first `10` GOOD/day max active = `10`;
- selected10: `41` fast clean, `52` survivable, `77` late-pump dependent, `17` falling-knife, `2` no-room.

Вывод: нельзя обучать ML просто на всех `+1%` hit. Сначала надо руками определить, какие risk classes разрешены как positive, а какие идут в hard-negative или отдельную DCA/hedge-политику.

Entry-marker fix: после замечания пользователя top-day PNG перегенерирован так, чтобы треугольник стоял на `entry_open_price`, а `entry +5bps` был отдельной белой execution-меткой. Новый run для просмотра: `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_entryopen_fix_20260702_161630`.

Closeup fix: для `2026-05-02` собраны отдельные страницы ручной проверки всех `44` GOOD-сделок, по `9` панелей на страницу. Run: `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260502_closeups_20260702_162715`.
## Current State 2026-07-02 Significant Low Calibration V0

Текущий статус: `SIGNIFICANT_LOW_CALIBRATION_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

После ручного feedback по `2026-05-02` создан слой калибровки значимого low: `src/mlbotnav/visual_entry_significant_low_calibration_v0.py`. Он не ищет новые сделки через ML/Optuna, а фильтрует уже собранные low-кандидаты:

- user reject остается hard reject;
- user shift становится `USER_SHIFT_PENDING_REANCHOR`, то есть требуется отдельный zoom и точный перенос anchor/entry;
- машинный keep требует новый low в 60/180m left-context и достаточное падение от prior high;
- дубли внутри одного basin отбрасываются.

Актуальный user-layer run после правок пользователя по `LA048/LA050`:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_20260502_user_actual_v1c3_20260702_190227`

Итог по `2026-05-02`: `6` keep (`LA002`, `LA015`, `LA018`, `LA021`, `LA040`, `LA050`), `2` shift-pending (`LA007`, `LA028`), `38` user-reject, `6` not-significant, `2` duplicate-basin. Контроль: `LA048` и `LA049` отклонены, `LA050` принят, `LA051` не good. Следующий шаг: визуально проверить актуальный overview V1C3 и затем решать параметры V1. ML/export/training/scorer/target-lock/Optuna/API запрещены.

После нового скриншота пользователя собран рабочий zoom для точных стрелок:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_zoom_v0_20260702_191450/SIGNIFICANT_LOW_REANCHOR_ZOOM_V0_20260502.png`

Текущий следующий шаг: дождаться стрелок пользователя по `RB01_LA007_REANCHOR`, `RB02_LA028_REANCHOR`, `RB03_LA050_AREA`, затем создать новый reanchor layer с точным `signal_time_utc` и `entry_time_utc = next open`.

Стрелки применены в run:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v0_20260702_192103`

Итог reanchor:

- `RA001_FROM_LA007`: signal `03:14`, entry `03:15`, `entry +5bps=83.76186000`;
- `RA002_PENDING_FROM_LA028`: новой стрелки нет, остается pending;
- `RA003_CONFIRM_LA050`: signal `22:25`, entry `22:26`, `entry +5bps=84.26211000`.

Текущий следующий шаг: показать пользователю `SIGNIFICANT_LOW_REANCHOR_APPLIED_V0_20260502_ZOOM.png` и `OVERVIEW.png`, получить `норм / фиксить / показать стрелку по LA028`.

Пользователь уточнил `LA050`: сдвинуть на одну свечу влево и поставить на самый низ. Создан актуальный V1:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v1_20260703_060258`

Изменение V1:

- `RA003_SHIFT_LEFT_LA050`: visual marker `22:25` на low `84.02000000`;
- execution сохранен отдельно: `entry_open=84.06000000`, `entry +5bps=84.10203000`;
- `LA028` по-прежнему pending.

Текущий следующий шаг: показать пользователю V1 zoom/overview и получить `норм / фиксить`.

## Current State 2026-07-03 Reanchor Applied V2 RA004

Текущий статус: `SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Стрелка пользователя применена как новая ручная точка `RA004_USER_ENTRY_2049`:

- signal `2026-05-02T20:48:00Z`;
- entry `2026-05-02T20:49:00Z`;
- low свечи `84.05000000`;
- `entry_open=84.09000000`;
- `entry +5bps=84.13204500`.

Run: `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904`.

Главный PNG для user review: `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502_CLOSE_ZOOM_RA004.png`.

Следующий шаг: пользователь смотрит close-zoom/overview и говорит `норм / фиксить`. ML/export/training/scorer/target-lock/Optuna/API не запускать.

## Current State 2026-07-03 Manual Reanchors V0 Source Of Truth

Текущий статус: `SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

После жалобы пользователя, что на графике снова появились другие сделки, ручные reanchor-точки вынесены в отдельный JSON source-of-truth:

`configs/visual_entry/manual_reanchors/SOLUSDT_1m_2026-05-02_SIGNIFICANT_LOW_MANUAL_REANCHORS_V0.json`.

Создан renderer `src/mlbotnav/visual_entry_manual_reanchor_review_v0.py`, который читает только этот JSON и не подтягивает старые DCA/GOOD_1PCT rows. В clean overview попадают только подтвержденные ручные строки: `RA001_FROM_LA007`, `RA003_SHIFT_LEFT_LA050`, `RA004_USER_ENTRY_2049`. `RA002_PENDING_FROM_LA028` остается в review sheet, но не считается confirmed.

Актуальный run:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936`.

Главный следующий шаг: пользователь проверяет `SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_20260502_REVIEW_SHEET.png` и close-zoom по `RA003/RA004`. Если фикс нужен, править только JSON source-of-truth и перегенерировать этот же слой. ML/export/training/scorer/target-lock/Optuna/API запрещены.

## Current State 2026-07-03 STAS1 anchor-next-open fix

Текущий статус: `STAS1_GOOD_1PCT_ANCHOR_NEXT_OPEN_FIX_V0_VERIFIED_NO_ML_NO_OPTUNA`.

По `2026-05-02` подтвержден баг старого `GOOD_1PCT_REVIEW_POOL`: часть сделок брала `entry` от confirmation-свечи, а не от фактического low. В старом run было `44` GOOD, из них `12` имели вход через 2-4 свечи после `anchor_time_utc`.

Исправлено:

- `src/mlbotnav/visual_entry_low_anchor_suggester.py`: `signal_idx = anchor_idx`, `entry_idx = anchor_idx + 1`;
- `confirmation_idx` и `confirmation_time_utc` сохранены отдельно как справочный контекст;
- `src/mlbotnav/visual_entry_good_1pct_review_pool.py`: в CSV добавлены индексы для аудита;
- добавлен тест `tests/test_visual_entry_low_anchor_suggester.py`.

Контрольный run:

`STAS1_GOOD_LOW_REVIEW/runs/stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034`

Итог: `52` строки, `42` GOOD, `10` BAD, нарушений `entry_time_utc != anchor_time_utc + 1 minute` нет. Хвостов `python.exe` после проверки нет.

Следующий шаг: пользователь смотрит новый overview/closeups из STAS1 run и отмечает шум/неправильные low уже поверх исправленного правила `low -> next open +5bps`. ML/export/training/scorer/target-lock/Optuna/API не запускать.

## Current State 2026-07-07 Codex/VS Code load audit

Текущий статус: `CODEX_VSCODE_LOAD_AUDIT_LOCAL_FIX_APPLIED`.

Причина нагрузки была локальная: Codex запустил `git add -A`, а проект содержал большие неигнорируемые STAS run-артефакты. Вложенных `.git` внутри проекта нет, отдельная проблема GitHub-веток не подтверждена.

Что применено:

- `.gitignore`: STAS `runs` исключены из Git;
- `.vscode/settings.json`: тяжелые папки исключены из file watcher, search и Pylance analysis;
- зависшие `git add -A` остановлены, `.git/index.lock` отсутствует.

Проверено: `git status` быстрый, `git check-ignore` подтверждает `STAS1/2/3 .../runs`.

Проверка после reload VS Code: тяжелых Git-процессов нет, старый хвост `git status --porcelain` остановлен, новых `git add -A` нет. `git status --short --untracked-files=normal` выполняется примерно за `0.03s`. VS Code почти idle; остаточная CPU-активность относится к активному Codex-приложению во время текущего чата/проверок, а не к сканированию проекта.

## Current State 2026-07-03 STAS1 EndDay wrapper fix

Текущий статус: `STAS1_WRAPPER_ENDDAY_FIX_VERIFIED_NO_ML_NO_OPTUNA`.

Исправлены `STAS1_GOOD_LOW_REVIEW/run_day_1pct.ps1` и `STAS1_GOOD_LOW_REVIEW/run_day_0p5.ps1`: теперь параметр `-EndDay` реально передается в `visual_entry_good_1pct_review_pool` как `--end-day`. Если `-EndDay` не задан, остается режим одного дня.

Smoke-run `2026-05-03 -> 2026-05-04` дал `days_requested=2`, `days_processed=2`, `records_total=132`, `bad_anchor_to_entry=0`.

Проверенный run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_smoke_20260503_20260504_endday_fix_v0_20260703_173534`.

Следующая команда на 7 дней теперь может идти через wrapper:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-03 -EndDay 2026-05-09 -RunLabel stas1_20260503_20260509_1pct_anchor_next_open_fix_v0
```
## Current State 2026-07-09 STAS4 combo strategies 3 days

Статус: `STAS4_COMBO_4_STRATEGIES_3D_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

По рабочему Stas2 run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_short_macro_wave_review_20260709_071233` прогнаны 4 комбинированные стратегии Stas4 на трех днях `2026-05-10..2026-05-12`: `structure_ta+trend_momentum`, `structure_ta+volume_flow`, `pattern+structure_ta`, `density_profile+structure_ta`.

Итоги: `structure_ta+trend_momentum` = `172` старых входа помечены как шум, `5` новых кандидатов; `structure_ta+volume_flow` = `158` / `2`; `pattern+structure_ta` = `106` / `6`; `density_profile+structure_ta` = `72` / `11`.

Главный отчет: `STAS4_FEATURE_HYPOTHESIS_REVIEW/STAS4_COMBO_4_STRATEGIES_3D_SUMMARY_20260709_RU.md`.

ML, Optuna, scorer, target-lock и API не запускались. Старая логика Stas1/Stas2 не менялась.
## Current State 2026-07-11 Codex Startup Disk Load Audit

Текущий статус: `CODEX_STARTUP_DISK_LOAD_AUDIT_READY_NO_DELETE_NO_CODE_CHANGE`.

Проверена жалоба на минутную нагрузку диска после перезагрузки и запуска Codex. Сейчас постоянной проблемы не найдено: диск во время аудита падал к нормальной нагрузке, `git status` и `git ls-files --others --exclude-standard` быстрые, зависшего `git add -A` нет, автозапуск Codex/VS Code/Git через `Win32_StartupCommand` не найден.

Главный найденный вес: `C:\Users\007\.codex` около `13.2 GB`, из них `sessions` около `7.5 GB`, backup/archived-сессии около `4.4 GB`, `logs_2.sqlite` около `724 MB`. Внутри проекта есть `_codex_offload_20260530` около `5.9 GB`, который уже игнорируется Git/VS Code, но физически остается в рабочей папке и может прогреваться Windows/Defender при холодном старте.

Подробный отчет: `docs/codex/CODEX_STARTUP_DISK_LOAD_AUDIT_20260711_RU.md`.

Граница: файлы, кеши, сессии, логи и артефакты не удалялись и не переносились. Любая очистка/перенос старой истории Codex требует отдельного подтверждения пользователя.

## Current State 2026-07-14 STAS5 V4 Group Ranker

Текущий статус: `STAS5_V4_OFFLINE_GROUP_REVIEW_DONE__V4L_LIVE_SAFE_REQUIRED`.

V4 больше не обучается как построчный KEEP/CUT. Рабочая единица теперь локальная группа кандидатов: старые `274` признака сохранены как контекст, а решение делается через `group_id`, V4 group features и ранжирование внутри группы.

Актуальный train:

- `2026-05-01..2026-05-14` - legacy база из V2 snapshot;
- `2026-05-15..2026-05-25` - пользовательские исправленные V4 group-rank правки, включая снятый с карантина `2026-05-15`;
- dataset `PASS`, `1710` строк, `103` winners, `287` features;
- corrected review join `738/738`, дублей `0`;
- запрещенные old ML/future/postfact/TP/Stas3/exit features не попали в модель.

Актуальная модель:

`STAS5_ML_CORE/artifacts/v4/model/runs/stas5_v4_train_20260714_163911/stas5_v4_group_ranker_20260501_20260525_v0.joblib`

OOF group metrics: `top1_group_accuracy=0.679612`, `winner_in_top2=0.834951`, `MRR=0.797006`, `NDCG@3=0.805523`, `BAD top1=15`.

Актуальный forward:

`STAS5_ML_CORE/artifacts/v4/forward/runs/stas5_v4_forward_20260526_20260530_20260714_164144`

Forward totals: `363` rows, `25` auto-groups, `ENTER=24`, `UNSURE=16`, `SKIP=323`. По дням: `2026-05-26` ENTER `4`, `2026-05-27` ENTER `5`, `2026-05-28` ENTER `5`, `2026-05-29` ENTER `5`, `2026-05-30` ENTER `5`.

Важная граница после no-future аудита: текущий V4 нельзя считать live-safe моделью. Он не использует TP/Stas3/future outcome, но использует full-group признаки, рассчитанные по уже собранной группе. Будущий состав группы тоже считается future leakage.

Текущий V4 run остается полезным как `OFFLINE_GROUP_REVIEW_NOT_LIVE_SAFE`: teacher/audit слой для понимания красивых human-style входов.

Следующий рабочий контур: `STAS5_ML_CORE/08_STAS5_V4L_LIVE_SAFE_GROUP_RANKER_PLAN_RU.md`.

V4L должен:

- считать только `v4l_*_so_far` признаки;
- хранить full-group/best-low поля только как audit/label;
- проходить `LIVE_SAFE_FEATURE_ALLOWLIST`;
- проходить `prefix invariance`;
- делать sequential forward replay, где score/decision доступны не позже `entry_time_utc`.

## Current State 2026-07-14 STAS5 V4L Live-Safe Group Ranker

Текущий статус: `STAS5_V4L_LIVE_SAFE_TRAIN_FORWARD_READY_20260501_20260530`.

Реализован отдельный live-safe контур V4L, чтобы не путать его со старым offline V4:

- dataset builder: `src/mlbotnav/stas5_v4l_live_safe_dataset.py`;
- trainer: `src/mlbotnav/stas5_v4l_live_safe_train.py`;
- blind forward: `src/mlbotnav/stas5_v4l_live_safe_forward.py`;
- единая команда: `STAS5_ML_CORE/run_stas5_v4l_live_safe_train_forward.ps1`.

Train окно зафиксировано как `2026-05-01..2026-05-25`: legacy `01..14` плюс исправленный user-review ledger `15..25`, включая `2026-05-15`. Dataset `PASS`: `1710` строк, `25` дней, `103` winners, `289` признаков = старый V2-контекст плюс `15` live-safe `v4l_*_so_far` признаков. Prefix-invariance guard: `1710/1710`, failures `0`. Запрещенные full-group/future/old-ML признаки в feature list: `0`.

Последний проверенный train run:

`STAS5_ML_CORE/artifacts/v4l/model/runs/stas5_v4l_train_20260714_181635`

Последний проверенный blind forward `2026-05-26..2026-05-30`:

`STAS5_ML_CORE/artifacts/v4l/forward/runs/stas5_v4l_forward_20260526_20260530_20260714_181635`

Forward totals: `363` rows, `ENTER=23`, `UNSURE=80`, `SKIP=260`. По дням: `2026-05-26` ENTER `4`, `2026-05-27` ENTER `5`, `2026-05-28` ENTER `5`, `2026-05-29` ENTER `5`, `2026-05-30` ENTER `4`.

Правило no-future теперь технически закреплено: V4L не использует final group low/rank/size, `post_candidate_lower_low_exists`, day-end top-N selection и не переписывает прошлые решения после появления будущих кандидатов. Postfact audit добавляется только после решения для визуальной проверки PNG.

## Current State 2026-07-15 STAS5 V5 Row-Label Pivot / Day23 Pre-Knife Correction

Текущий рабочий статус: `V4_V4L_FROZEN_AS_FAILED_STRATEGY__V5_ROW_LABEL_PREP`.

Пользователь отклонил V4/V4L как финальную торговую логику: стратегия с group-rank/sequential one-entry behavior дает слишком ранние или не те входы и не должна быть основой следующего обучения. Новый правильный контур: дорабатывать ML-обучение по строкам кандидатов, используя ручные good/bad правки `2026-05-15..2026-05-25` как эталонные метки. `group_id`, `reason_code` и визуальные блоки остаются объяснением/аудитом метки, но не должны навязывать ограничение "один ENTER на группу".

Разбор нового скрина `2026-05-23` выполнен по оригинальным данным, не по пикселям:

- forward CSV: `STAS5_ML_CORE/artifacts/v3/forward/runs/stas5_v3_wrapper_smoke2_20260714/20260523/STAS5_V3_FORWARD_ENTRIES_20260523.csv`;
- OHLCV: `data/core/bybit_ohlcv/dt=2026-05-23/tf=1m/symbol=SOLUSDT/part-final.csv`;
- исходный corrected ledger: `STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V1.csv`.

Новая пользовательская пометка: верхний широкий прямоугольник перед ножом - зона, где покупать нельзя; нижняя зона после flush - место для хороших входов. По свечам локальный flush low найден в `2026-05-23T07:50:00Z`, `low=81.35`.

Создана новая версия day23-разметки без перезаписи V1:

`STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V2_PRE_KNIFE.csv`

Сопроводительный отчет:

`STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_REVIEW_20260523_USER_CORRECTED_V2_PRE_KNIFE_RU.md`

Numeric audit:

`STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_REVIEW_20260523_PRE_KNIFE_NUMERIC_AUDIT.csv`

Главные изменения day23 V2:

- `LA001..LA016` / `G20260523_001_0032_0638` переведены в `NO_TRADE_GROUP`;
- `LA007` больше не `BEST_GOOD`, потому что попал в верхнюю pre-knife зону и до flush low имел аудит-просадку около `-3.42%`;
- `LA002` и `LA014` больше не `GOOD_ALT`;
- `LA017..LA021` остаются плохими immediate pre-knife входами, просадка до flush low около `-3.10..-3.43%`;
- `LA022` остается `BEST_GOOD / GOOD_BEST_DEEP_LOW_AFTER_KNIFE`;
- `LA025` остается `GOOD_ALT` как второй низ в нижней зоне;
- `LA033` остается `BEST_GOOD` как retest базы.

Итог day23 V2: `63` строк, `BEST_GOOD=6`, `GOOD_ALT=2`, `BAD_IN_GROUP=27`, `NO_TRADE_GROUP=28`, winners `LA022,LA033,LA034,LA036,LA042,LA051`.

Важно: drawdown/flush-low расчеты являются audit/label explanation only. Их нельзя отдавать в model features. В будущем V5 row-level обучении разрешены только признаки, доступные на момент `entry_time_utc`.

Создан общий V5 label-source для `2026-05-15..2026-05-25`, где day23 заменен на `USER_CORRECTED_V2_PRE_KNIFE`:

`STAS5_ML_CORE/artifacts/v5/labels/STAS5_V5_ROW_LABEL_SOURCE_20260515_20260525_WITH_DAY23_PRE_KNIFE_V1.csv`

Manifest:

`STAS5_ML_CORE/artifacts/v5/labels/STAS5_V5_ROW_LABEL_SOURCE_20260515_20260525_WITH_DAY23_PRE_KNIFE_V1.manifest.json`

Guard `PASS`: `738` строк, `11` дней, дублей `0`, day23 rows replaced `63 -> 63`. Counts: `BAD_IN_GROUP=420`, `NO_TRADE_GROUP=215`, `BEST_GOOD=63`, `GOOD_ALT=40`. Если для V5 считать `BEST_GOOD + GOOD_ALT` положительными row-level метками, получается `103` positive и `635` negative.
## Current State 2026-07-15 Codex CPU Load Check

Текущий статус: `CODEX_CPU_LOAD_CHECK_READY_NO_KILL_NO_DELETE_NO_CODE_CHANGE`.

Проверена жалоба, что Codex снова активно грузит CPU. Процессы не останавливались, файлы не удалялись. Текущий сценарий отличается от аудита диска 2026-07-11: диск во время проверки был умеренный (`3.5%..26.1%`), а CPU прыгал `22.8%..44.4%`.

Codex по замерам потреблял примерно `5.3%..9.2% CPU` суммарно по группе и около `3.5..3.6 GB PrivateMB`. От `Codex.exe` наблюдались повторяющиеся `git diff --find-renames --numstat -z` между внутренними состояниями, а также краткие `git add -u`/`git add -A`. `git status` остается быстрым, около `51 ms`; `git diff --cached --name-only` пустой, `.git/index.lock` нет, то есть реального staging в пользовательский индекс не обнаружено.

Главное изменение с 2026-07-11: неигнорируемый dirty worktree вырос с `393` файлов на `58.7 MB` до `1574` файлов на `424.8 MB`, из них `1220` файлов и около `389.8 MB` в `STAS5_ML_CORE`. Вероятная причина нагрузки - внутренний пересчет Git/diff Codex по большой пачке незакрытых изменений.

Подробный отчет: `docs/codex/CODEX_CPU_LOAD_CHECK_20260715_RU.md`.

Граница: ничего не убивать и не удалять без отдельного решения. Безопасная разгрузка - уменьшить dirty worktree: коммит/стейдж согласованных файлов, перенос generated artifacts или аккуратное расширение `.gitignore` только после решения, что является source-of-truth.
## Current State 2026-07-16 Codex Unload Applied

Текущий статус: `CODEX_UNLOAD_APPLIED_NO_DELETE_NO_PROCESS_KILL_CODEX`.

Codex разгружен без удаления файлов: процессы Codex не остановлены, приоритет `Codex`/`codex` понижен до `BelowNormal`, generated/run-папки `STAS5_ML_CORE/artifacts/` и `STAS5_ML_CORE/runs/` добавлены в `.gitignore` и локальные VS Code excludes.

Результат: неигнорируемые untracked снизились с `1574` файлов / `424.8 MB` до `381` файла / `41.6 MB`; `git status` около `51..79 ms`; `.git/index.lock` отсутствует; после финального контроля активных `git.exe` нет. CPU Codex на контрольном 10-секундном замере около `4.1%`, диск умеренный.

Отчет: `docs/codex/CODEX_UNLOAD_ACTION_20260716_RU.md`.

## Current State 2026-07-16 Codex Idle Relief

Текущий статус: `CODEX_IDLE_RELIEF_APPLIED_NO_DELETE_NO_STAS_TOUCH`.

После повторной жалобы на движение диска/памяти/CPU в простое выполнена мягкая разгрузка без удаления и без изменения `STAS*`: остановлены read-only `git status --porcelain` и внутренний `git diff --find-renames --numstat -z`, активных `git.exe` после контроля нет, `.git/index.lock` нет. Приоритет `Codex`/`codex`/`Code` установлен в `Idle`. Отдельный VS Code OpenAI/Codex extension server остановлен до следующего запуска VS Code.

Оставшийся источник коротких дисковых всплесков по процессным счетчикам - `MsMpEng` (Microsoft Defender). Defender не отключался. Свободная память оставалась около `13.3..13.8 GB`, то есть давления по RAM не найдено. Отчет: `docs/codex/CODEX_IDLE_RELIEF_20260716_RU.md`.

## Current State 2026-07-22 Codex Update Load Audit

Текущий статус: `CODEX_UPDATE_LOAD_AUDIT_RELIEF_APPLIED_NO_DELETE`.

После обновления Codex установлен как `OpenAI.Codex_26.715.10079.0`, но главная оболочка в процессах теперь `ChatGPT.exe`. Это объясняет, почему прежняя разгрузка `Codex`/`codex` не полностью работала: активный renderer/gpu Codex был под другим именем.

Мягкая разгрузка выполнена без удаления и без изменения `STAS*`: VS Code OpenAI/Codex extension server остановлен, `ChatGPT`/`codex`/`Code`/`node_repl` переведены в `Idle`. Активных `git.exe` нет, `.git/index.lock` нет, `git status` быстрый (`~52 ms`). Финальный системный диск не висит: чтение `0`, Disk Time `0.8..10.4%`, свободная память `13.5..13.7 GB`. Отчет: `docs/codex/CODEX_UPDATE_LOAD_AUDIT_20260722_RU.md`.

## Current State 2026-07-23 Codex VS Code Fix

Текущий статус: `CODEX_VSCODE_EXTENSION_RESTARTED_NO_DELETE`.

Панель Codex в VS Code восстановлена: штатная кнопка `Перезапустить` подняла сервер расширения `openai.chatgpt-26.715.31925...\codex.exe app-server`. Приоритеты `ChatGPT`/`codex` стоят в `Idle`. После краткого стартового чтения контрольный срез показал VS Code Codex server без CPU и без дискового I/O. Папки `STAS*` и `config.toml` не изменялись. Отчет: `docs/codex/CODEX_VSCODE_FIX_20260723_RU.md`.

## Current State 2026-07-23 STAS9 Shortcut And CPU Fix

Текущий статус: `STAS9_VSCODE_LAUNCH_READY_LIGHTWEIGHT`.

Оба ярлыка STAS9 на рабочем столе указывают на `Code.exe` с аргументом открытия `MLbotNav_STAS9.code-workspace`. Старый terminal launcher оставлен только как технический файл внутри проекта и после контрольного запуска ярлыка не активен. Простое открытие STAS9 больше не инициирует полный аудит или чтение больших журналов. Контрольный замер показал низкую постоянную нагрузку: `Code ~1.56%`, все `codex ~0.10%`. STAS5–STAS8 не изменялись.
