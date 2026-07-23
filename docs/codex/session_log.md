# Session Log

## 2026-07-23 SOL Event Contract and Dry-Run Pipeline

По явному ТЗ пользователя создан безопасный документальный event-контур
`SOLUSDT 1m` только на `data/core/bybit_ohlcv`. Исходный слой прочитан
потоково без записи: `126` CSV, `181440` строк, одна схема из `16` полей,
уникальная минутная шкала без дублей и разрывов.

Созданы `MARKET_KNOWLEDGE/EVENT_SCHEMA_RU.md`,
`MARKET_KNOWLEDGE/EVENTS/SOL/README_RU.md` и
`REPORTS/SOL_EVENT_PIPELINE_DESIGN_RU.md`. Зафиксированы девять event types,
причинная граница признаков, отдельные future outcome/label и lineage.

In-memory dry-run проверил source root, identity, обязательные поля, enum,
event ID, timestamp mapping, feature causality и отсутствие YAML events.
Итог `PASS_DRY_RUN_NO_EVENT_RECORDS`; событий `0`, datasets `0`.

Metadata fingerprints `STAS5_ML_CORE`, `data/core/bybit_ohlcv`, всего `data`
и `models` совпали до/после. Обучение, Optuna, forward, модели, STAS5/STAS8,
live trading, удаления и переносы не затрагивались. Финальный режим:
`SAFE / READ_ONLY`.

## 2026-07-23 STAS9 VS Code On-Demand Workflow

По явному ТЗ пользователя основной рабочий интерфейс STAS9 закреплён как
`MLbotNav_STAS9.code-workspace -> VS Code -> Codex`. Создан новый ярлык
`🤖 STAS9 Workspace`; два существующих ярлыка сохранены.

В конфигурациях зафиксированы `CODEX_ROLE`, `ON_DEMAND`,
`USER_COMMAND_ONLY`, `SAFE + READ_ONLY`, idle `NONE`; автозапуск агентов,
watcher и автоматическое сканирование отключены. Добавлены
`CODEX_WORKFLOW_RU.md`, `START/README_RU.md` и итоговый отчёт. Console
launcher оставлен как технический диагностический резерв.

Проверки: YAML/JSON `PASS`, ярлык содержит `Code.exe`, `--new-window` и
`MLbotNav_STAS9.code-workspace`; фоновые STAS9/Python/Optuna/rg процессы,
автозагрузка, служба и планировщик не найдены. Metadata fingerprints
`STAS5_ML_CORE`, `data` и `models` до/после совпали. Обучение, Optuna,
изменение моделей, удаление и торговые операции не выполнялись. Итоговый
режим: `SAFE / READ_ONLY`.

## 2026-07-23 STAS9 Agent Roles and SOL ML Preparation

По подробному ТЗ пользователя работа была распределена между независимыми
исполнителями: отдельно подготовлены роли и новый агент, SOL-база
знаний/dataset pipeline, а также маршрутизатор и память обязанностей. Sentinel
выполнил только интеграцию конфигураций, контроль и итоговый отчёт.

Созданы семь документов ролей, `STAS9_MARKET_RESEARCH`, `TASK_ROUTER_RU.md`,
`AGENT_RESPONSIBILITIES.yaml`, пять разделов `MARKET_KNOWLEDGE`, шаблон
события, `DATASET_BUILDER` и `STAS9_AGENT_SETUP_REPORT_RU.md`.

Проверки: YAML `31/31 PASS`, агенты `8x4 PASS`, registry `8/8 PASS`,
delegation `7/7 PASS`, routes `11/11 PASS`, roles `7/7 PASS`, SOL contracts
`PASS`. Metadata fingerprint `6196` файлов STAS5/STAS8 совпал до и после:
`40ceeb41c5562eb8b64d31dae1f2abb91caad9da40be6e294715c161d51d1445`.

Обучение, Optuna, forward, модели, STAS5/STAS8 и live trading не затрагивались.
Удалений и переносов не было. Итоговый режим: `SAFE / READ_ONLY`.

## 2026-07-23 STAS9 Persistent Control-Plane Memory

Пользователь попросил проверить текущую архитектуру STAS9 и закрепить
`STAS9_CONTROL_PLANE` как постоянную память управляющей роли внутри Codex.

Подтверждена схема `Codex -> STAS9_SENTINEL -> STAS9_CONTROL_PLANE`. Созданы
`MEMORY/STAS9_STATE.md` с текущим состоянием, агентами, правилами и последними
действиями, а также `START_HERE_RU.md` со стартовым prompt для нового чата.

Проверки: оба файла существуют, читаются как UTF-8, настроено `7` агентов.
STAS5–STAS8 не изменялись; обучение, Optuna, forward и live trading не
запускались. После задачи режим возвращён в `SAFE`.

## 2026-07-23 STAS9 VS Code/Codex Interface

Статус: `PASS_STAS9_VSCODE_CODEX_INTERACTIVE_ASSISTANT_READY_PROTECTED_UNCHANGED`.

Создан `MLbotNav_STAS9.code-workspace` с `chatgpt.openOnStartup=true` и рекомендацией установленного расширения `openai.chatgpt`. Созданы интерфейс, voice/STT-инструкция, command router, response template, три режима, Codex guidance и журнал диалогов. На рабочем столе создан ярлык `🤖 STAS9 Assistant`, напрямую открывающий workspace в `Code.exe`; консоль не используется.

Старые `start_STAS9.bat` и `🤖 STAS9 Главный агент.lnk` сохранены как технический режим.

Проверки: VS Code `1.117.0`, Codex extension `26.715.31925`, workspace JSON `PASS`, YAML `23`, structure/policy `PASS`, shortcut target `PASS`, реальный Sentinel response smoke `PASS`.

STAS5/STAS8 неизменны: `6196` файлов, content-tree SHA256 `e2b12f074d2a658582e85d671d0a4758c6f98875521a2da9f3849a51d1b56543`.

## 2026-07-23 STAS9 Codex CLI Update

Статус: `PASS_CODEX_CLI_0_145_0_STAS9_MODEL_READY_PROTECTED_UNCHANGED`.

По разрешению пользователя глобальный npm-CLI Codex обновлён с `0.142.5` до `0.145.0`. `codex doctor` завершился с exit `0`; install, auth, network и connectivity исправны.

Launcher `start_STAS9.bat --check` прошёл. Реальный одноразовый read-only запрос `gpt-5.6-sol` с reasoning `xhigh` вернул `STAS9_MODEL_OK`; исходная ошибка 400 больше не воспроизводится.

Защищённое дерево `STAS5_ML_CORE`, включая STAS8, не изменилось: `6196` файлов, SHA256 `e2b12f074d2a658582e85d671d0a4758c6f98875521a2da9f3849a51d1b56543`.

## 2026-07-23 STAS9 Multi-Agent Control Layer

Статус: `PASS_STAS9_MULTI_AGENT_CONTROL_LAYER_READY_PROTECTED_VERSIONS_UNCHANGED`.

По ТЗ пользователя реализован безопасный управляющий слой с одним главным и шестью специализированными агентами. Созданы `36` файлов STAS9: `28` файлов агентов, общая конфигурация, глобальная политика, память, три журнала, launcher и setup-отчёт. На рабочем столе создан один ярлык на launcher.

Проверки: YAML `19/19 PASS`, agent files `28/28 PASS`, logs `3/3 PASS`, launcher `--check PASS`, shortcut target `PASS`, root STAS6/STAS7 отсутствуют. Полный content-tree SHA256 `6196` файлов `STAS5_ML_CORE` до и после совпал: `e2b12f074d2a658582e85d671d0a4758c6f98875521a2da9f3849a51d1b56543`.

Обучение, Optuna, forward и торговые операции не запускались; модели, legacy и `BROKEN_POINTER` не изменялись.

## 2026-07-23 STAS9 Multi-Agent Structure

Статус: `PASS_STAS9_DIRECTORY_STRUCTURE_READY_LEGACY_UNCHANGED`.

В существующем `STAS9_CONTROL_PLANE/` созданы `STAS9_AGENTS/` с семью каталогами агентов и служебные каталоги `MEMORY/`, `LOGS/`, `REPORTS/`, `RUNTIME/`, `CONFIG/`, `PERMISSIONS/`, `START/`.

Проверено: ожидается `15` каталогов, найдено `15`, пропусков `0`, лишних `0`. Корневые `STAS6` и `STAS7` не создавались. Контрольный отпечаток `6196` файлов `STAS5_ML_CORE` до и после совпал.

## 2026-07-23 STAS9 Control Plane

Статус: `PASS_STAS9_CONTROL_PLANE_REGISTRIES_READY_NO_TRAINING_NO_FORWARD_STAS5_STAS8_UNCHANGED`.

По запросу пользователя проведен read-only аудит STAS1–STAS8 и создан `STAS9_CONTROL_PLANE/`.

Созданы карта проекта, model registry, feature registry, полный реестр `142` ТЗ, архивная политика и предложение архитектуры. Зарегистрированы `6043` legacy pipeline joblib коллекциями и все `37` STAS5 joblib поштучно.

Выявлены: broken active/champion pointer, `193` уникальные отсутствующие legacy model references, `260` повторных registry records, отсутствие самостоятельных STAS6/STAS7 и вложенный preview-only STAS8.

Проверки PASS: YAML, model path coverage, legacy collection counts, task count, mojibake scan. STAS5–STAS8 не изменены: metadata fingerprint `367301aa69b966a588fb078f8ff3ee4fd6fa109b688bc848fdeb6154d2f6a506` до/после совпал.

## 2026-07-23 Codex Project CPU Relief

Пользователь попросил устранить нагрузку CPU проекта. Проверка показала: Python/ML не запущен; Codex Desktop циклически запускал Git diff/hash по `258` generated-файлам `STAS4_FEATURE_HYPOTHESIS_REVIEW`, а Defender повторно проверял эти файлы.

В `.gitignore` добавлены точечные правила для подпапок и PNG STAS4 review, в `.vscode/settings.json` папка исключена из watcher/search/Pylance. Верхние Markdown-документы оставлены видимыми Git. Удалений, обучения и forward не было. Текущим процессам Codex/ChatGPT выставлен `Idle`.

Контроль: STAS4 Git-хвост `258 -> 2`, `codex.exe` около `9% -> 0.03%`, общий CPU `10.0..13.6%`, среднее `12.3%`, Python отсутствует, `.git/index.lock` отсутствует. Отчет: `docs/codex/CODEX_PROJECT_CPU_RELIEF_20260723_RU.md`.

## 2026-07-22 STAS5 V5 Base R2-Style Review Gallery

Пользователь попросил сделать базовые `2026-01-27..2026-02-27` графики в обычном формате как R2/R3/R4, чтобы пересмотреть базу глазами. Добавлен builder `stas5_v5_base_review_gallery.py` и wrapper `run_stas5_v5_base_review_gallery.ps1`.

Результат:

```text
STAS5_ML_CORE/artifacts/v5c/review/_BASE_R2_STYLE_VISUAL_REVIEW_20260127_20260227
```

Контроль: `PASS_V5_BASE_R2_STYLE_REVIEW_GALLERY_READY_NO_TRAINING_NO_FORWARD`, `days=32`, `rows=2596`, `GOOD=290`, `BAD=2306`. Тесты: `py_compile` PASS, `tests/test_stas5_v5_forward_visual_review.py` PASS после установки `PYTHONPATH=src`.

## 2026-07-22 STAS5 V5C Entry Visual Check Pack

Пользователь попросил подготовить графики на ручную проверку всех входов с базового `2026-01-27` плюс `R2/R3/R4`. Пересобрана штатная review-витрина для R2/R3/R4, затем собран единый пакет:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ENTRY_VISUAL_CHECK_CURRENT_20260127_20260320
```

Итог: `PASS_ENTRY_VISUAL_CHECK_PACKAGE_READY_NO_TRAINING_NO_FORWARD`, `BASE=32`, `R2=7`, `R3=7`, `R4=7`, всего `53` дневных PNG. Созданы contact sheets, manifest, Markdown/CSV index. Обучение и forward не запускались.

## 2026-07-22 STAS5 V5C R4BB Table/ML Audit

Пользователь спросил, мог ли бардак в таблицах и визуальные баги быть причиной плохого обучения. Проведен read-only аудит с двумя active subagents. Файлы моделей/CSV не менялись, обучение и forward не запускались.

Итог: R2/R3/R4 ручные правки применились в ENTRY и RiskGate datasets, mismatch `0`; ENTRY train `rows=3285`, `GOOD=517`, `BAD=2768`, `features=463`; RiskGate train `rows=627`, `risk_bad_y=400`, `risk_ok=227`, `features=463`. В allowlist/joblib нет target/manual/future/STAS8 preview columns. Причина плохого результата сейчас не похожа на table corruption: слабый ENTRY OOF, two-block не выбран, RiskGate threshold слишком широкий, STAS8/move-capacity еще preview.

Отчет: `STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5C_R4BB_TABLE_ML_AUDIT_20260722_RU.md`.

## 2026-07-22 STAS8 Soft V2 Visual Semantics Fix

Пользователь указал, что STAS8 Soft V2 графики визуально вводят в заблуждение. Проверка глазами и по CSV подтвердила проблему: зеленый круг смешивал final live `ENTER`, `WATCH protect` и offline `SKIP->RECALL_WATCH`. Это было неверно для принятия торгового решения.

Исправлено: зеленый круг теперь рисуется только для финального live `ENTER` после STAS8; красный квадрат - исходный `ENTER`, пониженный в `WATCH`; красный круг - hard block. `SKIP->RECALL_WATCH` остается только в CSV/отчете как hidden offline-аудит и не рисуется зеленым кругом на цене.

R5 Soft V2 пересобран без обучения и без нового forward. Guard: `PASS_V5C_STAS8_SOFT_CAPACITY_V2_PREVIEW_READY_NO_TRAINING_NO_FORWARD_NO_DECISION_CHANGE`, `18/18`, `failed_count=0`, `soft_v2_visual_markers_match_live_semantics=PASS`. Predictions SHA unchanged: `cd7bc6f7a2855a116d6973ef0a827b160c2843cf9df04c432db4b95b2acfd579`.

Новые marker counts: `strict green=2/red_square=6/red_circle=107`; `balanced green=15/red_square=11/red_circle=60/hidden_recall=48`; `wide green=36/red_square=6/red_circle=30/hidden_recall=48`.

Глазами проверены 2026-03-26/2026-03-27. Визуальная путаница снята, но логика еще требует tuning: `balanced` оставляет 1 live `ENTER` на 2026-03-26 в падающем канале, `wide` оставляет 9. Следующий шаг - донастроить down-channel/no-long и post-knife rebound, а не запускать новое обучение.

## 2026-07-22 STAS8 Soft Capacity V2 Preview R5

По OK пользователя и с проверкой старых субагентов собран `STAS8_SOFT_CAPACITY_V2` для R5 `2026-03-21..2026-03-27`. Это read-only preview поверх `stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1`: обучение не запускалось, forward не перезапускался, predictions CSV не менялся.

Добавлены режимы `strict/balanced/wide`, guard на no-future/immutability, запрет SKIP->ENTER, контроль hard-block для исходных ENTER/WATCH, дневные PNG без Bollinger и contact sheets по всем 7 дням.

Результат: status PASS, rows=564, checks=17, failed_count=0. До STAS8 было `ENTER=61/WATCH=166/SKIP=337`; V2 дает `strict ENTER=2`, `balanced ENTER=15`, `wide ENTER=36`. Главный кандидат для ручного просмотра - `balanced`, второй для сравнения - `wide`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/soft_capacity_v2
```

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5c_stas8_move_capacity_audit.py -q` = `6 passed`.

## 2026-07-22 STAS8 R5 Entry/Move Audit

Проведен read-only аудит R5 `2026-03-21..2026-03-27` по актуальному run `stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1`. Обучение и новый forward не запускались; исходный predictions CSV не менялся.

Сохранен отчет:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1/STAS5_V5C_STAS8_R5_ENTRY_MOVE_AUDIT_20260321_20260327_RU.md
```

Короткий вывод: STAS8 V1 слишком жесткий (`ENTER/WATCH 227 -> 21`), блокирует `40` хороших исходных ENTER/WATCH с `hit_1p2` и оставляет `15` плохих WATCH. Следующий шаг - только read-only `STAS8_SOFT_CAPACITY_V2` preview, без включения в train/forward до отдельного OK.

## 2026-07-22 STAS8 R5 Visuals Without Bollinger

Пользователь попросил убрать Bollinger-полосы с текущих STAS8-графиков, чтобы не путать визуальный Bollinger с STAS8/RiskGate-блокировкой. В STAS8 renderer отключен `bollinger_preview`, R5 `2026-03-21..2026-03-27` пересобран.

Результат: guard PASS, `png_count=7`, `visual_bollinger_preview=false`, counts unchanged: before `ENTER=61/WATCH=166/SKIP=337`, after preview `ENTER=1/WATCH=20/SKIP=543`.

## 2026-07-22 STAS8 Move Capacity Audit Preview R5

По OK пользователя собран первый рабочий контур `STAS8_MOVE_CAPACITY_AUDIT_V1` без обучения и без изменения forward. Использован актуальный R5 no-risk X463 run:

```text
stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1
```

Добавлены модуль `src/mlbotnav/stas5_v5c_stas8_move_capacity_audit.py`, wrapper `STAS5_ML_CORE/run_stas5_v5c_stas8_move_capacity_audit.ps1`, тесты и маленькое расширение renderer для названия панели overlay.

Результат: guard PASS, rows=564, X=463, teacher grid rows=40608, PNG=7. До STAS8 было `ENTER=61`, `WATCH=166`, `SKIP=337`; preview после STAS8 дает `ENTER=1`, `WATCH=20`, `SKIP=543`. Predictions CSV не изменен. Вывод: слой полезен для подсветки down-channel/no-long, но текущие пороги слишком жесткие для боевого включения; следующий шаг - визуально настроить STAS8 по PNG, особенно 2026-03-26/2026-03-27.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1
```

## 2026-07-22 STAS8 Live Wave + Move Capacity Plan Locked

Пользователь уточнил, что для long нельзя просто смотреть, был ли future-ход `1.1-1.2%` после точки. Сначала рынок должен уже показать живой long-режим: волны вверх-вниз, диапазон, откат/retest/base/reclaim, отсутствие one-way dump. После обсуждения с субагентами обновлены STAS8 ТЗ и config.

Итоговая рельса: `STAS8_LIVE_MOVE_CONTEXT_V1` решает, можно ли искать long; `STAS8_TEACHER_MOVE_GRID_V1` offline считает future-сетку как teacher/audit; R2/R3/R4 используются как train material, R5 `2026-03-21..2026-03-27` остается blind-forward/audit-preview до ручного review. Код STAS8, обучение и forward не запускались.

## 2026-07-22 STAS5 V5C R4BB Fast Train Audit

Пользователь сообщил, что обучение `stas5_v5c_r4bb_train_20260127_20260320` прошло слишком быстро и попросил аудит с субагентами без правок логики. Проверены run manifest, dataset guards, post-train guards, latest pointer и `.joblib` packages.

Итог после фикса: `PASS_V5C_R4BB_FAST_TRAIN_AUDIT_CONFIG_FIXED_NO_IGNORED_FEATURES_FOUND`. ENTRY использовал `STAS5_V5C_BATCH_20260127_20260320_ML_READY_463F_TARGETS_V1.csv`; RiskGate использовал `STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X463_RISK_BAD_Y_V1.csv`. Во всех основных model packages присутствуют `24` `bb20_*` признака; forbidden target/review/future columns в model feature lists не найдены. Быстрое обучение объясняется малым объемом данных и легкими sklearn-моделями. Управляющий config теперь указывает на R4BB/X463, старые check names в текущем R4BB-контуре переименованы.

Аудит сохранен:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5C_R4BB_FAST_TRAIN_AUDIT_RU.md
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5C_R4BB_FAST_TRAIN_AUDIT_V1.json
```

## 2026-07-22 STAS5 V5C Bollinger Visual Preview

Собрана preview-неделя `2026-03-21..2026-03-27` с Bollinger `20/2` поверх сценария `DOWN_CHANNEL_NO_LONG_V1`.

Папка:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1/safety_pulse_preview/down_channel_no_long_v1/
```

Код: в `src/mlbotnav/stas5_v5_forward_visual_review.py` добавлен optional `bollinger_preview`, выключенный по умолчанию; в `src/mlbotnav/stas5_v5c_safety_pulse_preview.py` и `STAS5_ML_CORE/run_stas5_v5c_safety_pulse_preview.ps1` добавлен ключ `--bollinger-preview` / `-BollingerPreview`. Train/forward/predictions не менялись. Итог preview недели: `ENTER=40`, `WATCH=136`, `SKIP=388`. Проверки: `.venv` `py_compile PASS`; `.venv` `pytest tests/test_stas5_v5_forward_visual_review.py tests/test_stas5_v5c_safety_pulse_preview.py -q` = `8 passed`.

## 2026-07-22 STAS5 V5C ENTRY-Only Wide R5

Добавлены явные ключи для R5 ENTRY-only режима: `-SkipRiskGateML` в train и `-DisableRiskGateML` в forward. Цель - переобучить/просмотреть ENTRY на базе `2026-01-27..2026-03-20` с R2/R3/R4 правками без RiskGate enforce и с `WideReview`, чтобы входы не были задушены раньше анализа high/short-channel/move-capacity.

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5_continuous_ml.py -q` = `3 passed`; help показывает оба новых ключа. Train/Forward не запускались.

## 2026-07-22 STAS8 Move Capacity Grid TZ

Зафиксировано отложенное ТЗ `STAS8 MOVE CAPACITY GRID V1`: будущий слой оценки емкости движения цены, который отделяет `volatility` от `edge`.

Файлы:

```text
STAS5_ML_CORE/10_STAS8_MOVE_CAPACITY_GRID_TZ_RU.md
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
```

Решение: `ENTRY_BASELINE_ML` ищет возможность входа, RiskGate блокирует смертельные режимы, а будущий STAS8 должен проверять, может ли рынок реально дать движение `1.0..1.5%` в нашу сторону. На этом шаге код, обучение и forward не запускались.

## 2026-07-21 STAS5 V5C Down-Channel Safety Pulse Preview

Сделан и проверен preview-only пульс `DOWN_CHANNEL_NO_LONG_V1` поверх R4 forward `2026-03-21..2026-03-27`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1/safety_pulse_preview/down_channel_no_long_v1
```

Цифры: до RiskGate `ENTER=70`, старый финал с `RISKGATE_ML` `ENTER=34`, новый preview `ENTER=40`, `WATCH=136`, `SKIP=388`. Для `2026-03-26` стало `ENTER=4`; для `2026-03-27` стало `ENTER=7`.

Логика: baseline ENTRY ищет возможность, `DOWN_CHANNEL_NO_LONG_V1` блокирует только нисходящий канал со слабым отскоком и без хода под 1-1.5%; старые taxonomy/ML mass-demote в этой policy не применяются. Train/forward не запускались.

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5c_safety_pulse_preview.py -q` = `7 passed`; YAML config parse PASS.

## 2026-07-21 STAS5 V5C RiskGate ML Train Wiring

Добавлен обучаемый `RISKGATE_ML` поверх готового RiskGate dataset. Он не заменяет ENTRY: ENTRY ищет возможность, RiskGate проверяет опасность и после будущего Train может понизить/заблокировать финальное решение.

Изменения:

```text
src/mlbotnav/stas5_v5c_riskgate_ml.py
src/mlbotnav/stas5_v5_continuous_ml.py
tests/test_stas5_v5c_riskgate_ml.py
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml/json/RU.md
```

Реальный RiskGate TrainingGuard: `PASS_V5C_RISKGATE_ML_TRAINING_GUARD_READY_FOR_TRAINING`, `627 rows`, `risk_bad_y=1=400`, `risk_bad_y=0=227`, `features=439`.

Forward-логика после будущего Train: `ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE` хранит исходный ENTRY-вердикт, `RISKGATE_ML_LIVE_SCORE/DECISION/ACTION` показывают safety-слой, а `ENTRY_ML_LIVE_DECISION` становится финальным решением после RiskGate.

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5c_riskgate_ml.py tests/test_stas5_v5c_train_dataset_builder.py tests/test_stas5_v5_continuous_ml.py tests/test_stas5_v5_two_block_ml.py -q` = `9 passed`; ENTRY TrainingGuard PASS. Обучение и forward не запускались.

## 2026-07-21 STAS5 V5C Review-Supervised Dataset Builder

Собран новый builder `src/mlbotnav/stas5_v5c_train_dataset_builder.py` и wrapper `STAS5_ML_CORE/run_stas5_v5c_train_dataset_builder.ps1`.

Реальные артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_ML_READY_439F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X439_RISK_BAD_Y_V1.csv
```

Цифры: ENTRY `3285 rows`, `GOOD=517`, `BAD=2768`, `features=439`; RiskGate `627 rows`, `risk_bad_y=1=400`, `risk_bad_y=0 explicit safe=227`.

Guards: ENTRY `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING`; RiskGate `PASS_V5C_RISKGATE_TRAIN_DATASET_GUARD_READY_NO_TRAINING`; TrainingGuard `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`.

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5c_train_dataset_builder.py tests/test_stas5_v5c_review_pack.py tests/test_stas5_v5c_review_ladder.py tests/test_stas5_v5c_riskgate_audit.py -q` = `24 passed`.

Обучение и forward не запускались. Следующий шаг - пользователь вручную запускает `-Mode Train` для `stas5_v5c_r4_train_20260127_20260320`.

## 2026-07-21 STAS5 V5C Review Pack R2/R3/R4

Собран отдельный approved review-pack по пользовательской разметке `R2/R3/R4` за `2026-02-28..2026-03-20`.

Артефакт:

```text
STAS5_ML_CORE/artifacts/v5c/review/_APPROVED_REVIEW_PACKS/STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1/
```

Цифры: `days=21`, `ENTRY rows=689`, `GOOD=227`, `BAD=462`, `RISK BAD=400`.

Guard: `PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING`. Обучение, forward и пересборка дневных паспортов не запускались.

Изменения кода:

```text
src/mlbotnav/stas5_v5c_review_pack.py
STAS5_ML_CORE/run_stas5_v5c_review_pack.ps1
tests/test_stas5_v5c_review_pack.py
```

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5c_review_pack.py tests/test_stas5_v5c_review_ladder.py tests/test_stas5_v5_forward_visual_review.py tests/test_stas5_v5c_riskgate_audit.py -q` = `24 passed`.

## 2026-07-20 STAS5 V5C Current Review Cleanup

По замечанию пользователя наведена связка “один рабочий график + цифры для ML”. В `src/mlbotnav/stas5_v5c_review_ladder.py` добавлен `CURRENT_REVIEW.png`, `_visual_archive` и `CURRENT_VISUAL_MANIFEST_V1.json`. В `src/mlbotnav/stas5_v5c_review_gallery.py` та же логика применена к общей витрине.

Пересохранен `R2 / 2026-03-01` без training/forward/day rebuild. В корне `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260301/` остался один PNG `STAS5_V5C_R2_USER_REVIEW_20260301_CURRENT_REVIEW.png`; старые/preview PNG перенесены в `_visual_archive`. Manifest фиксирует `ENTRY GOOD=10`, `ENTRY BAD=26`, `RISK BAD=21`.

R2 gallery обновлена: `STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/R2/20260301/` теперь содержит один `STAS5_V5C_R2_20260301_CURRENT_REVIEW.png` плюс CSV и `_visual_archive`.

## 2026-07-20 STAS5 V5C Review LA Labels Above Markers

По замечанию пользователя поправлен renderer review-графиков: `LAxxx` больше не перекрывается красными/зелеными кругами и квадратами. Раскладка оставлена почти как раньше, но для review-точек подпись получает небольшой дополнительный подъем, а все `LAxxx` рисуются после review-маркеров верхним слоем.

После пользовательского OK пересобраны R2/R3/R4 gallery в `STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/`: R2 `7` дней, R3 `7` дней, R4 пока `2026-03-18`. Контрольный файл: `STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/R2/20260301/STAS5_V5C_R2_20260301_ANNOTATED_ENTRY_RISK.png`. Training/forward/day passport rebuild не запускались.

## 2026-07-20 STAS5 V5C Review Contract: Cross Good And Risk Bad

Пользователь уточнил рельсу: `крестик хорошо` должен попадать в хорошее обучение как `entry_y=1`, а `риск плохо` должен одновременно становиться ENTRY BAD и RiskGate BAD. Код `src/mlbotnav/stas5_v5c_review_ladder.py` обновлен: risk-only фраза теперь автоматически пишет ENTRY-строку `entry_y=0`, `entry_from_risk_bad=1`, а RiskGate-строку `risk_bad_y=1`. Для графика `RISK BAD` остается красным кругом, без лишнего красного квадрата поверх той же точки.

Новый контракт: `хорошо/вход/крестик хорошо/ромбик хорошо -> entry_y=1`; `плохо -> entry_y=0`; `риск плохо -> entry_y=0 + risk_bad_y=1`. Training/forward не запускались.

## 2026-07-20 STAS5 V5C R2 Review Update 2026-03-01

По пользовательской диктовке пересохранен R2 review для `2026-03-01` через `run_stas5_v5c_review_ladder.ps1 -Stage SaveReview -Approve -Force`, без training/forward/day passport rebuild.

Итог после уточнения контракта: ENTRY GOOD `9` (`LA002,LA005,LA034,LA044,LA048,LA055,LA071,LA075,LA077`), ENTRY BAD `22` (`21` из Risk BAD + обычный `LA032`), Risk BAD `21` (`LA011,LA018,LA019,LA020,LA021,LA022,LA024,LA025,LA028,LA029,LA050,LA053,LA057,LA062,LA063,LA065,LA066,LA068,LA069,LA070,LA074`). R2 gallery обновлена.

## 2026-07-20 STAS5 V5C Review Gallery R2/R3/R4

Создан сборщик общей визуальной витрины review-графиков:

```text
src/mlbotnav/stas5_v5c_review_gallery.py
STAS5_ML_CORE/run_stas5_v5c_review_gallery.ps1
```

Собраны R2/R3/R4 в `STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/`. Итог: `15` review-дней, `30` PNG. R2: `7` дней и `14` PNG; R3: `7` дней и `14` PNG; R4: пока `2026-03-18`, `2` PNG. Один R2-график визуально проверен: overlay `GOOD/BAD`, нижние полосы `Fon/LONG/SHORT/WAVE` сохранены, стрелочного шума нет.

Сборщик не запускал training, forward и day passport rebuild.

## 2026-07-20 STAS5 V5C ENTRY/RiskGate Two Targets Fixed

Пользователь подтвердил контракт: ENTRY и RiskGate обучаются поверх одних и тех же candidate rows и causal `X439`, но цели разные. ENTRY использует `entry_y`; RiskGate использует отдельный `risk_bad_y`.

В `src/mlbotnav/stas5_v5c_review_ladder.py` добавлена явная колонка `risk_bad_y=1` и round-колонка вида `r4_risk_bad_y=1` для строк `риск плохо`. Старый `risk_bad_target` оставлен для совместимости. В result/risk JSON добавлен `risk_bad_y_count`.

Отдельно зафиксировано: отсутствие `риск плохо` не является автоматическим `risk_bad_y=0`; будущий RiskGate dataset builder должен осознанно выбирать негативные/safe-примеры.

Обновлен YAML-контракт `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml` и docs/codex. Training/forward не запускались.

Текущий `2026-03-18` approved review пересохранен только как review-artifact: `STAS5_ML_CORE/artifacts/v5c/review/r4_user_review/20260318/STAS5_V5C_R4_USER_RISKGATE_REVIEW_20260318_APPROVED.csv`; `risk_bad_y_count=9`, Risk BAD ids: `LA040,LA042,LA043,LA046,LA047,LA049,LA054,LA055,LA058`.

## 2026-07-20 STAS5 V5C Quick Review Ladder

Статус: `PASS_V5C_QUICK_REVIEW_LADDER_READY_NO_TRAINING`.

Пользователь утвердил простую рельсу ручной диктовки: обычные `хорошо/плохо` идут в ENTRY teacher layer, а только `риск плохо` идет в отдельный RiskGate teacher layer. `риск хорошо` запрещен, чтобы не путать хороший rebound-вход с risk-меткой.

Добавлены `src/mlbotnav/stas5_v5c_review_ladder.py`, `STAS5_ML_CORE/run_stas5_v5c_review_ladder.ps1`, `tests/test_stas5_v5c_review_ladder.py`. Команда умеет `Parse`, `SaveReview`, `BuildEntryDay`, `RiskGate`, `All`, `Open`; при `-Stage All` в старую day-ladder передаются только ENTRY GOOD ids.

Проверки: `py_compile PASS`; после корректного `PYTHONPATH=src` профильный pytest `21 passed`; PowerShell `-Stage Parse` smoke PASS.

## 2026-07-20 STAS5 V5C RiskGate Taxonomy V1

По решению пользователя RiskGate докручен до полной таксономии режимов: `PRE_DUMP_RISK`, `ACTIVE_DUMP`, `FALLING_KNIFE`, `STRONG_SHORT_PRESSURE`, `SHORT_CONTINUATION`, `PULLBACK_THEN_SHORT`, `SUPPORT_BREAKDOWN`, `CHANNEL_BREAKDOWN`, `POST_PUMP_DUMP`, `LIQUIDATION_CASCADE`.

Изменены `src/mlbotnav/stas5_v5c_riskgate_audit.py`, `tests/test_stas5_v5c_riskgate_audit.py`, `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml` и docs/codex. RiskGate остается `audit_only`: `ENTRY_ML_LIVE_DECISION` не меняется, training/forward не запускались.

Контрольный audit пересобран для `2026-03-18` в `STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_audit/20260318/`. Итог ENTER: `BLOCK_HARD=6`, `BLOCK_RISK=3`, `WARN_RISK=3`, `PASS_USER_REBOUND=3`; user-pass `LA059,LA067,LA078`; `RISK_NO_FUTURE_OK=True`.

Проверки: `py_compile PASS`; `.venv python -m pytest tests/test_stas5_v5c_riskgate_audit.py -q` = `16 passed`; YAML read PASS; text audit PASS.

## 2026-07-20 STAS5 V5C ENTRY_ML_TWO_BLOCK Frozen

По решению пользователя `ENTRY_ML_TWO_BLOCK` заморожен в главном YAML config: `enabled=false`, `mode=frozen_not_selected`, `selection_status=FROZEN_NOT_SELECTED_BY_R3_QUALITY_GATE`. Причина: блок обучается технически нормально, но не проходит quality gate и не доказал преимущество над `ENTRY_BASELINE_ML`. Код, training, forward и predictions не менялись.

## 2026-07-20 STAS5 V5C YAML Config Russian Comments

Главный config `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml` дополнен русскими комментариями по каждому ML-блоку и guard-разделу. Комментарии описывают текущую главную ML `ENTRY_BASELINE_ML`, support `MARKET_PHASE_STATE_ML`, not-selected `ENTRY_ML_TWO_BLOCK`, будущий `RISK_GATE_RULE_V0 audit_only`, `DUMP_AVOID_ML` и `REBOUND_ALLOW_ML`. YAML validation после правки: `PASS`. Код, training, forward и predictions не менялись.

## 2026-07-20 STAS5 V5C Main YAML ML Control Config

По согласованию с пользователем главный ML-control config переведен в один YAML:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

JSON и RU.md оставлены как reference snapshot/readme и помечены не source-of-truth. В YAML зафиксированы active R3 train/forward context, `X439` no-future контракт, active `ENTRY_BASELINE_ML`, support `MARKET_PHASE_STATE_ML`, not-selected `ENTRY_ML_TWO_BLOCK`, planned `RISK_GATE_RULE_V0` в режиме `audit_only`, planned disabled `DUMP_AVOID_ML` и `REBOUND_ALLOW_ML`. Код раннеров не менялся, обучение и forward не запускались, predictions не менялись.

## 2026-07-19 STAS5 V5C ML Control Config

Создан единый управляющий паспорт ML-блоков:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
```

Зафиксировано: текущий active entry alpha = `ENTRY_BASELINE_ML`; `MARKET_PHASE_STATE_ML` обучен как support; `ENTRY_ML_TWO_BLOCK` обучен, но не выбран R3 quality gate; `RISK_GATE_RULE_V0`, `DUMP_AVOID_ML`, `REBOUND_ALLOW_ML` пока выключены и описаны как следующие safety-блоки. Обучение и forward не запускались, predictions не менялись. JSON validation: `PASS`.

## 2026-07-18 STAS5 V5C R3 Training Guard PASS

Пользователь запустил R3 `TrainingGuard` на диапазоне `2026-01-27..2026-03-13` с `TrainRunId=stas5_v5c_r3_train_20260127_20260313`. Результат подтвержден по файлам: `status=PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`, `rows=3726`, `days=46`, `entry_y 1=432`, `entry_y 0=3294`, `features=439`.

В run dir `STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r3_train_20260127_20260313/` пока только guard JSON/RU.md; model/joblib/train manifest нет. Обучение еще не запускалось. Следующий шаг - пользователь запускает `-Mode Train` с тем же run_id.

## 2026-07-18 STAS5 V5C R3 Train PASS

Пользователь запустил R3 `Train`; результат подтвержден по артефактам. Созданы baseline, phase/state и entry_ml модели, train manifest и metrics. Post-train guard: `PASS_V5_TWO_BLOCK_POST_TRAIN_GUARD_READY_FOR_FORWARD`.

Контроль: dataset `2026-01-27..2026-03-13`, `rows=3726`, `days=46`, `entry_y 1=432`, `entry_y 0=3294`, `features=439`; OOF predictions `3726/3726`, null `0`.

Production selector выбрал `entry_baseline`: baseline PR-AUC `0.253024`, two-block PR-AUC `0.250156`; baseline walk PR-AUC `0.298295`, two-block walk PR-AUC `0.272692`; baseline top 1pct precision `0.421053`, two-block `0.394737`.

Проверены свечи для следующего blind-forward `2026-03-14..2026-03-20`: все `part-final.csv` существуют. Следующий шаг - пользователь запускает forward week3 с R3 train manifest.

## 2026-07-17 STAS5 V5C R3 Review Draft Week2 Completed

Пользователь завершил черновую ручную разметку week2 `2026-03-07..2026-03-13` по run `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`. Все 7 дней сохранены в `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/YYYYMMDD/` как `DRAFT_WAIT_USER_CONFIRM_CLOSE_DAY`; дневные passports и обучение пока не запускались.

Последний день `2026-03-13` сохранен: `GOOD=9`, `BAD=13`; плохая серия `LA046..LA053` после пампа/дампа и просадки около `6%` зафиксирована как важный будущий фильтр `памп-скат/нож`. Следующий шаг: пользователь подтверждает закрытие дней или дает правки; затем approved-ledger и пересборка дневных V5 passports.

## 2026-07-17 STAS5 V5C R3 Review Draft 2026-03-07

Пользователь продиктовал разметку `2026-03-07` по wide-review графикам. Сохранен draft без пересборки passport: `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/20260307/STAS5_V5C_R3_USER_REVIEW_20260307_DRAFT.csv`.

Итог: `13` строк, `GOOD=9`, `BAD=4`. GOOD ids: `LA006`, `LA011`, `LA021`, `LA027`, `LA046`, `LA051`, `LA054`, `LA063`, `LA064`. BAD ids: `LA005`, `LA044`, `LA057`, `LA062`. `LA057` зафиксирован как BAD после пользовательского исправления. UTF-8 audit по новой папке чистый, `???/mojibake` не найдено.

## 2026-07-17 STAS5 V5C R2Q WideReview V2 Control Point

Зафиксирован рабочий review-прогон `stas5_v5c_r2q_forward_20260307_20260313_wide_v2` как материал для пользовательской разметки и будущего R3. Диапазон `2026-03-07..2026-03-13`, train source `stas5_v5c_r2q_train_20260127_20260306`, selected model `entry_baseline`, policy `wide_review`.

Фактические цифры: `rows=554`, `ENTER=64`, `WATCH=167`, `SKIP=323`, `visual_review_png_count=14`, forward/visual PASS. Контрольный отчет: `STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r2q_forward_20260307_20260313_wide_v2/STAS5_V5C_R2Q_WIDE_V2_REVIEW_CONTROL_POINT_RU.md`. Следующий шаг: пользователь размечает графики по дням, Codex сохраняет R3 teacher labels и после закрытия недели готовит R3 batch `2026-01-27..2026-03-13`.

## 2026-07-17 STAS5 V5C R2Q Forward Decision Threshold Fix

Пользователь сообщил, что после `-EntryDecisionPolicy Normal` входов стало слишком мало. Аудит готового run `stas5_v5c_r2q_forward_20260307_20260313_normal` показал `ENTER=5`, `WATCH=54`, `SKIP=495`; причина была в старом `Normal=p96.5/p81.5`, который оказался слишком высоким для forward score distribution.

Исправлено в `src/mlbotnav/stas5_v5_continuous_ml.py`: `Normal=p90/p60`, `WideReview=p80/p50`. По тем же forward score ожидается `Normal ENTER=25/WATCH=148`, `WideReview ENTER=64/WATCH=167`. Пороги считаются только по train OOF predictions, без forward labels. Проверки: `py_compile PASS`; PowerShell syntax `PASS`; `pytest tests/test_stas5_v5_continuous_ml.py tests/test_stas5_v5_two_block_ml.py` = `7 passed`. Следующее действие пользователя: запустить `WideReview` командой из `docs/codex/commands.md`.

## 2026-07-17 STAS5 V5C R2Q Train Multiclass Fix

Пользователь запустил `TrainingGuard` и затем `Train` для `stas5_v5c_r2q_train_20260127_20260306`. Guard прошел PASS, но Train упал на `phase_y/state_y` с ошибкой `liblinear` multiclass. Причина была в коде: phase/state использовали binary-oriented `logistic_balanced` pipeline.

Исправлено `src/mlbotnav/stas5_v5_two_block_ml.py`: добавлен `PHASE_STATE_MODEL_KIND = "extra_trees_balanced"` и применен в phase/state LODO, walk-forward audit и финальной phase/state модели. Добавлен тест на multiclass LODO. Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5_two_block_ml.py tests/test_stas5_v5_continuous_ml.py` = `5 passed`.

Следующее действие пользователя: повторить `-Mode Train` с тем же run_id. Forward не запускать до post-train guard PASS.

## 2026-07-17 STAS5 V5C R2 ML Quality Audit/Fix

Пользователь сообщил, что R2/R2-week2 дает примерно 50/50 и выглядит так, будто не учится на ручных lows. Подключены агенты для lineage/metrics/code-аудита. Вывод: старый R1 не подмешан, R2 batch/train/forward связаны правильно; review-неделя `2026-02-28..2026-03-06` вошла в train как `576` строк и `69` GOOD.

Найдена ML-причина качества: свежие labels были с обычным весом, p90 threshold принудительно давал много ENTER, phase/state SGD давал warnings и слабый signal, two-block шел в forward даже когда baseline лучше. Исправлены `src/mlbotnav/stas5_v5_two_block_ml.py` и `src/mlbotnav/stas5_v5_continuous_ml.py`: sample weights от `2026-02-28`, stable phase/state без SGD, raw-proba guard без тихой NaN/inf-очистки, ENTRY candidates `logistic_balanced/extra_trees_balanced`, precision/Wilson threshold, baseline/two-block selector, forward использует `selected_entry_model`.

Проверки: `python -m py_compile src\mlbotnav\stas5_v5_two_block_ml.py src\mlbotnav\stas5_v5_continuous_ml.py`; `.\.venv\Scripts\python.exe -m pytest tests\test_stas5_v5_two_block_ml.py tests\test_stas5_v5_continuous_ml.py` = `4 passed`; temp smoke train PASS. Новое боевое обучение и forward не запускались. Отчет: `STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_R2_ML_QUALITY_AUDIT_AND_FIX_20260717_RU.md`.

## 2026-07-17 STAS5 V5C R2 Batch Guard Ready

Подготовлена R2-рельса для walk-forward цикла без запуска обучения и без нового forward. Исправлены параметрические даты/counts в `src/mlbotnav/stas5_v5_continuous_ml.py`, `src/mlbotnav/stas5_v5_two_block_ml.py`, `src/mlbotnav/stas5_v5_batch_dataset_builder.py` и `STAS5_ML_CORE/run_stas5_v5c_continuous_train_forward.ps1`: `TrainingGuard`/`Train` теперь берут тот же диапазон, что и `BuildBatch`.

Собран R2 batch `2026-01-27..2026-03-06`:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260306_GUARD_V1.json
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
days=39
rows=3172
entry_y 1=359 / 0=2813
features=439
```

Проверки: `py_compile` для трех ML-модулей, direct smoke tests `test_stas5_v5_batch_dataset_builder.py` и `test_stas5_v5_two_block_ml.py` прошли; OHLCV для `2026-03-07..2026-03-13` существует. Следующий шаг отдан пользователю командами: R2 `TrainingGuard`, затем R2 `Train`, затем blind forward week2.

## 2026-07-16 STAS5 V5 Forward Visual Review Label Order Fix

По замечанию пользователя исправлена хаотичная раскладка `LAxxx` на overview-графиках. Теперь подписи сортируются по номеру кандидата (`LA001`, `LA002`, ...), ставятся структурно над своей точкой и соединяются с точкой тонкой желтой линией. Текущий forward run `stas5_v5_forward_20260228_20260306_20260716` перерендерен, manifest остался `PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES`, `png_count=14`.

## 2026-07-16 STAS5 V5 Forward Visual Review Style Fix

По уточнению пользователя изменен стиль дневных V5 overview-графиков. Длинные зеленые стрелки и боксы `ENTER LAxxx score` убраны. Теперь все кандидаты подписаны желтым `LAxxx`; `SKIP` показан желтым X, `WATCH` - маленьким желтым ромбом, `ENTER` - зеленым треугольником. Closeup-листы оставлены для отдельного просмотра входов.

Текущий run перерендерен:

```text
STAS5_ML_CORE/artifacts/v5/forward/runs/stas5_v5_forward_20260228_20260306_20260716/visual_review/
```

Manifest: `PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES`, `png_count=14`. Проверены `py_compile`, `pytest tests/test_stas5_v5_forward_visual_review.py -q` и визуально открыты PNG `20260228`/`20260304`.

## 2026-07-16 STAS5 V5 Forward Visual Review With ENTER Arrows

Пользователь указал, что на графиках forward должны быть зеленые стрелки входов, чтобы визуально видеть решения ML. Добавлен `src/mlbotnav/stas5_v5_forward_visual_review.py`: он читает готовый `STAS5_V5_FORWARD_PREDICTIONS_20260228_20260306_V1.csv`, берет OHLCV только для координат графика и рисует обзорные PNG с крупными зелеными стрелками `ENTER`, желтыми `WATCH` и серыми остальными кандидатами. Также создаются closeup-листы по каждому `ENTER`.

Текущий run `stas5_v5_forward_20260228_20260306_20260716` отрендерен без повторного обучения:

```text
STAS5_ML_CORE/artifacts/v5/forward/runs/stas5_v5_forward_20260228_20260306_20260716/visual_review/
```

Manifest: `PASS_V5_FORWARD_VISUAL_REVIEW_READY_ENTER_ARROWS`, `png_count=14`. Проверены `py_compile` и `pytest tests/test_stas5_v5_forward_visual_review.py tests/test_stas5_v5_two_block_ml.py -q`: `3 passed`.

## 2026-07-16 STAS5 V5 two-block training + blind forward

Выполнен end-to-end проход V5 two-block ML.

Создано:

```text
src/mlbotnav/stas5_v5_two_block_ml.py
STAS5_ML_CORE/run_stas5_v5_two_block_ml.ps1
tests/test_stas5_v5_two_block_ml.py
STAS5_ML_CORE/artifacts/v5/STAS5_V5_TWO_BLOCK_TRAIN_FORWARD_20260716_RU.md
```

Training run:

```text
STAS5_ML_CORE/artifacts/v5/model/runs/stas5_v5_two_block_train_20260716_32d/
```

Training guard `PASS`, post-train guard `PASS`.

Forward run:

```text
STAS5_ML_CORE/artifacts/v5/forward/runs/stas5_v5_forward_20260228_20260306_20260716/
```

Forward guard `PASS_V5_TWO_BLOCK_FORWARD_20260228_20260306_BLIND_NO_FUTURE`. Итог: `576` rows, `ENTER=20`, `WATCH=120`, `SKIP=436`.

OOF-метрики показали, что baseline сильнее two-block: `ROC-AUC 0.6564 / PR-AUC 0.1813` против `ROC-AUC 0.6377 / PR-AUC 0.1561`. Следующий шаг: review 20 `ENTER` и baseline-forward сравнение.

## 2026-07-16 STAS5 V5 Two-Block ML TZ

По просьбе пользователя вместе с агентом Hume расписано ТЗ следующего ML-этапа V5. Файлы обучения и forward не запускались.

Создан документ:

```text
STAS5_ML_CORE/09_STAS5_V5_TWO_BLOCK_ML_TZ_RU.md
```

Зафиксировано: обязательный baseline `ENTRY_BASELINE_ML`, первый блок `MARKET_PHASE_STATE_ML`, OOF phase/state predictions для train `ENTRY_ML`, live phase/state predictions для forward, training guard до обучения и post-train guard до forward.

Следующий практический шаг: реализовать `STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1`.

## 2026-07-16 STAS5 V5 batch dataset + guard

Реализован и запущен V5 batch dataset builder для диапазона `2026-01-27..2026-02-27`.

Создан код:

```text
src/mlbotnav/stas5_v5_batch_dataset_builder.py
STAS5_ML_CORE/run_stas5_v5_batch_dataset_builder.ps1
tests/test_stas5_v5_batch_dataset_builder.py
```

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_ML_READY_439F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_FEATURE_ALLOWLIST_439F_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_MANIFEST_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_AUDIT_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_GUARD_V1.json
```

Результат guard: `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING`, `32` дня, `2596` строк, `entry_y 1=290 / 0=2306`, `439` features (`274 + 81 cs_* + 84 fcs_*`). `entry_y/phase_y/state_y/reason_y` и manual teacher поля не входят в `X`. `cs_max_source_time_utc` и `fcs_max_source_time_utc` не позже `entry_time_utc`. Дублей нет. Model/forward V5 не запускались.

Проверки: `py_compile` для нового модуля и теста прошел, прямой smoke-test `test_v5_batch_dataset_builds_guard_and_fills_feature_gaps` прошел, реальный builder завершился с `PASS`.

Следующий шаг: training guard и подготовка two-block ML `MARKET_PHASE_STATE_ML -> ENTRY_ML` с OOF predictions первого блока, без настоящих `phase_y/state_y` как features.

## 2026-07-16 STAS5 V5 range audit 2026-01-27..2026-02-27

Проведен аудит диапазона `2026-01-27..2026-02-27`.

Первичная проверка нашла missing день `2026-02-07`: был FULL274 run, но не было V5 market passport. День дозаполнен по ранее утвержденным GOOD ids `LA004`, `LA007`, `LA010`, `LA012`, `LA020`, `LA023`, `LA030`, `LA034`, `LA035`, `LA041`, `LA044`, `LA046`, `LA050`, `LA052`, `LA058`; затем пересобран full causal layer и карта дня.

Финальный результат: `PASS_V5_RANGE_AUDIT_READY_FOR_BATCH_DATASET`, `32/32` full-ready дня, `2596` строк, `entry_y 1=290 / 0=2306`, feature contract `274 -> 355 -> 439`, problem count `0`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_RANGE_AUDIT_20260127_20260227_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_RANGE_AUDIT_20260127_20260227.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715.json
```

Обучение и forward V5 не запускались. Следующий правильный шаг: batch dataset + batch leakage/no-future guard, затем two-block training `MARKET_PHASE_STATE_ML -> ENTRY_ML`.

## 2026-07-15 STAS5 V5 audit 2026-02-01 and six full-ready days

Проведен аудит V5-пакета `2026-02-01` и общего состояния `artifacts/v5`.

Результат `2026-02-01`: `PASS`, `rows=89`, `entry_y 1=14 / 0=75`, `features=439`, `levels=34`, `channels=89`, `regimes=64`, `events=3402`. GOOD ids совпадают с пользовательской разметкой: `LA007`, `LA014`, `LA026`, `LA040`, `LA041`, `LA045`, `LA053`, `LA058`, `LA060`, `LA066`, `LA079`, `LA082`, `LA084`, `LA087`.

Общий V5 folder audit: `PASS_V5_FOLDER_AUDIT_NO_TRAINING`, `full-ready=6`, `partial/not-ready=27`, `model=False`, `forward=False`.

Финальный отчет дня:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260201/STAS5_V5_MARKET_PASSPORT_20260201_AUDIT_RU.md
```

Подтверждена схема двух будущих ML-блоков: `MARKET_PHASE_STATE_ML` и `ENTRY_ML`. На этом этапе обучение и forward не запускались.

## 2026-07-15 STAS5 V5 2026-01-28 Approved GoodIds Full Package

Пользователь дал GOOD ids для `2026-01-28`: `LA020`, `LA037`, `LA042`, `LA045`, `LA051`, `LA059`, `LA069`, `LA078`, `LA084`.

Добавлен builder approved-passport из списка GOOD ids:

```text
src/mlbotnav/stas5_v5_approved_passport_builder.py
STAS5_ML_CORE/run_stas5_v5_approved_passport_builder.ps1
```

`STAS5_ML_CORE/run_stas5_v5_day_ladder.ps1` получил параметр `-GoodIds` и теперь может собрать день одной командой.

Проверочный запуск:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage All -GoodIds LA020,LA037,LA042,LA045,LA051,LA059,LA069,LA078,LA084
```

Результат: baseline guard `PASS`, `cs_*` guard `PASS`, `fcs_*` guard `PASS`. Итог: `93` строки, `entry_y 1=9 / 0=84`, `439` feature columns, `levels=16`, `channels=93`, `regimes=66`, `events=3181`.

V5 folder audit обновлен: `full-ready=2`, `partial/not-ready=31`, `model=False`, `forward=False`.

Обучение и forward не запускались.

## 2026-07-15 STAS5 V5 навигация по пакету 2026-01-27

В папку `STAS5_ML_CORE/artifacts/v5/market_passports/20260127/` добавлен файл-указатель:

```text
00_OPEN_FIRST_RU.md
```

Назначение: открыть первым в проводнике и быстро понять, какие файлы являются текущими рабочими (`ENTRY_PHASE_STATE_REASON ... V2`), какие файлы являются историей, где лежит главный ML-ready CSV, ledger, phase segments, allowlist и guard. Данные и разметка не менялись.

## 2026-07-15 STAS5 V5 entry/phase/state/reason targets 2026-01-27

По пользовательской команде "делаем до результата" для дня `2026-01-27` создан новый target-слой V2: `entry_y`, `phase_y`, `state_y`, `reason_y`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_ENTRY_PHASE_STATE_REASON_LEDGER_USER_APPROVED_V2.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_PHASE_STATE_REASON_GUARD_V2.json
```

Проверка: `PASS_NO_TRAINING_PHASE_STATE_REASON_READY`, `rows=75`, `feature_count=274`, `entry_y 1=11 / 0=64`, forbidden feature columns `[]`. Обучение не запускалось.

## 2026-07-15 STAS5 V5 market passport 2026-01-27 user approved V3

Пользователь проверил `GOOD_ALT` и `REVIEW_ONLY` по графику `2026-01-27` и подтвердил: оставить только его `11` good-входов, остальные кандидаты хуже.

Создан финальный approved V3 ledger: `GOOD_APPROVED=11`, `BAD_IN_GROUP=50`, `NO_TRADE_ZONE=14`, `TOTAL=75`. `GOOD_ALT` и `REVIEW_ONLY` для этого дня удалены из активной разметки и переведены в negative.

Артефакты:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_LEDGER_20260127_USER_APPROVED_V3.csv
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_USER_APPROVED_RU.md
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_USER_APPROVED_V3_ANNOTATED_TOP.png
```

Обучение, API, TP/Stas3, threshold tuning не запускались.

Дополнительно создана отдельная пакетная папка дня:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/
```

Пакет содержит ML-ready таблицу `274F + labels`, allowlist `274` признаков, numeric market-structure table, context table и manifest. Проверка: `PASS_NO_TRAINING`, `rows=75`, `feature_count=274`, target `1=11 / 0=64`, forbidden feature columns `[]`.

После уточнения пользователя убрана двусмысленная старая формулировка про вспомогательный контекст. Актуальная схема: ручной паспорт рынка - это `TEACHER / PASSPORT`, который формирует правильный ответ `y`; прямые входные признаки `X` сейчас causal `274`, а структура рынка станет прямыми feature только после causal builder без будущего.

## 2026-07-15 STAS5 V5 market passport 2026-01-27 V2

Пользователь уточнил, что текущая работа идет по январю, не по апрелю. Для `2026-01-27` принят пользовательский GOOD-список: `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062`.

После read-only агентского разбора создан V2 draft ledger на все `75` кандидатов: `GOOD_APPROVED=11`, `GOOD_ALT=8`, `REVIEW_ONLY=7`, `BAD_IN_GROUP=35`, `NO_TRADE_ZONE=14`.

Артефакты:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_LEDGER_20260127_DRAFT_V2.csv
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_RU.md
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_LABELS_DRAFT_V2_ANNOTATED_TOP.png
```

Обучение, API, TP/Stas3, threshold tuning не запускались. Следующий шаг - пользовательская проверка `GOOD_ALT` и `REVIEW_ONLY`.

## 2026-07-15 STAS5 V5 market passport trial 2026-01-27

Создан пробный рыночный паспорт для `2026-01-27` по run `STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857`.

Результат: `DRAFT_VISUAL_REVIEW_ONLY_NO_TRAINING`. Проверено: `75` кандидатов, `274` causal-признака, labels `UNLABELED_VISUAL_ONLY`, обучение/API/TP/Stas3 не запускались.

Артефакты:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_ANNOTATED_TOP.png
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_DRAFT_ZONES.csv
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_RU.md
```

Следующий шаг: ручная сверка пользователем; после подтверждения draft можно переводить в approved label ledger.

## 2026-07-14 STAS5 V4 current truth note

Для текущего состояния V4 использовать верхние свежие записи и guard/unified ledger. Нижние записи session log являются хронологией промежуточных шагов и могут содержать устаревшие счетчики, которые были верны на момент конкретной правки, но не являются финальным состоянием.

Текущий факт: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение, features, Optuna, API, TP/Stas3/exit не запускались после ручной проверки.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-25

Проверен пользовательский скрин `2026-05-25` с двумя красными кругами. Первый круг попал в pre-London pullback на серый/skip-кандидат `LA020`; текущий V4 ledger уже держит его как `BEST_GOOD`, а `LA019` рядом оставлен `GOOD_ALT`. Второй круг попал в late-London retest `LA038`, который уже `BEST_GOOD`.

CSV day25 не менялся: актуальные winners `LA014`, `LA020`, `LA038`, `LA059`, `LA066`. Counts: `68` строк, `BEST_GOOD=5`, `GOOD_ALT=4`, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=19`.

Создан проверочный отчет `STAS5_V4_GROUP_RANK_REVIEW_20260525_USER_CHECKED_V1_RU.md`. Unified ledger и risk audit не пересчитывались, потому что CSV не менялся. Общий актуальный ledger остается после day23: `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-24

Проверен пользовательский скрин `2026-05-24`. Видимые круги совпали с текущими winners: левый pre-London круг соответствует `LA015`, overlap crash круг соответствует `LA042`, поздняя deep-low зона соответствует `LA065`.

CSV day24 не менялся: `LA015`, `LA042`, `LA065` уже `BEST_GOOD`; `LA067` остается `GOOD_ALT`, потому что это поздний pullback после V-отскока, а не главный нижний вход группы.

Создан проверочный отчет `STAS5_V4_GROUP_RANK_REVIEW_20260524_USER_CHECKED_V1_RU.md`. Day24 остается: `70` строк, `BEST_GOOD=5`, `GOOD_ALT=5`, `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=6`; winners `LA009`, `LA015`, `LA024`, `LA042`, `LA065`.

Unified ledger и risk audit не пересчитывались, потому что CSV не менялся. Общий актуальный ledger остается после day23: `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-23

Проверен пользовательский скрин `2026-05-23` с красными кругами справа от утреннего падения. В day23 draft была широкая recovery-группа `LA034..LA042`, из-за чего отдельные пользовательские входы `LA034` и `LA042` были задавлены одним winner `LA036`.

Исправлено: группа `LA034..LA042` разделена на три micro-groups. `LA034` повышен из `BAD_IN_GROUP` в `BEST_GOOD`, `LA036` оставлен `BEST_GOOD`, `LA042` повышен из `GOOD_ALT` в `BEST_GOOD`. Поздняя continuation-группа `LA043..LA051` оставлена с winner `LA051`.

Создан `STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V1.csv`. Day23 теперь: `63` строки, `BEST_GOOD=7`, `GOOD_ALT=4`, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=12`; winners `LA007`, `LA022`, `LA033`, `LA034`, `LA036`, `LA042`, `LA051`.

Unified ledger пересчитан: `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit обновлен: `GOOD_ALT_MAY_NEED_MICRO_GROUP=39`, `BEST_GOOD_FROM_OLD_NON_ENTER=28`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`. Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-22

Проверен свежий пользовательский скрин `2026-05-22`. В day22 draft была одна точечная ошибка: в группе `05:36-09:01` главным winner был `LA022`, но пользовательский круг показывает поздний ретест `LA024`.

Исправлено: `LA022` переведен из `BEST_GOOD` в `GOOD_ALT`; `LA024` повышен из `GOOD_ALT` в `BEST_GOOD`. Остальные видимые целевые зоны day22 совпали с таблицей: `LA007`, `LA036`, `LA047`, `LA061` остаются winners.

Создан `STAS5_V4_GROUP_RANK_LEDGER_20260522_USER_CORRECTED_V1.csv`. Day22 теперь: `75` строк, `BEST_GOOD=5`, `GOOD_ALT=4`, `BAD_IN_GROUP=55`, `NO_TRADE_GROUP=11`; winners `LA007`, `LA024`, `LA036`, `LA047`, `LA061`.

Unified ledger пересчитан без изменения totals: `BEST_GOOD=62`, `GOOD_ALT=43`, `BAD_IN_GROUP=434`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit totals не изменились: `GOOD_ALT_MAY_NEED_MICRO_GROUP=40`, `BEST_GOOD_FROM_OLD_NON_ENTER=26`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`. Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-21

Проверен пользовательский скрин `2026-05-21` с четырьмя красными кругами. `LA006` уже совпадал с текущим winner. `LA039` и `LA050` были `BAD_IN_GROUP` внутри слишком широкой sell-wave группы, а `LA057` был `GOOD_ALT` внутри слишком широкой pre-breakout группы.

Исправлено: sell-wave группа `LA022..LA050` разделена на три micro-groups с winners `LA039`, `LA045`, `LA050`. Pre-breakout группа `LA051..LA060` разделена на две micro-groups с winners `LA057` и `LA059`.

Создан `STAS5_V4_GROUP_RANK_LEDGER_20260521_USER_CORRECTED_V1.csv`. Day21 теперь: `81` строка, `BEST_GOOD=8`, `GOOD_ALT=4`, `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=15`; winners `LA006`, `LA019`, `LA039`, `LA045`, `LA050`, `LA057`, `LA059`, `LA066`.

Unified ledger пересчитан: `BEST_GOOD=62`, `GOOD_ALT=43`, `BAD_IN_GROUP=434`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit обновлен: `GOOD_ALT_MAY_NEED_MICRO_GROUP=40`, `BEST_GOOD_FROM_OLD_NON_ENTER=26`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`. Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-20

Проверен пользовательский скрин `2026-05-20` с двумя красными кругами в зоне `13:19-14:26`. Нижний круг совпал с уже выбранным `LA037`. Верхний круг оказался отдельным серым/skip-кандидатом `LA038`, который draft ошибочно держал как плохой вход внутри той же crash-low группы.

Исправлено: группа `G20260520_003_1319_1426` разделена на `G20260520_003A_1319_1413` с winner `LA037` и `G20260520_003B_1426_1507` с winner `LA038` и плохим соседом `LA039`. `LA035` остался `GOOD_ALT`, `LA036` остался `BAD_IN_GROUP`.

Создан `STAS5_V4_GROUP_RANK_LEDGER_20260520_USER_CORRECTED_V1.csv`. Day20 теперь: `68` строк, `BEST_GOOD=6`, `GOOD_ALT=4`, `BAD_IN_GROUP=27`, `NO_TRADE_GROUP=31`; winners `LA011`, `LA037`, `LA038`, `LA045`, `LA053`, `LA057`.

Unified ledger пересчитан: `BEST_GOOD=59`, `GOOD_ALT=44`, `BAD_IN_GROUP=436`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit обновлен: `BEST_GOOD_FROM_OLD_NON_ENTER=24`. Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-19

Проверен пользовательский скрин `2026-05-19` с красной обводкой в overlap/retest зоне. Старая draft-разметка держала `LA046` как `GOOD_ALT` внутри широкой группы `LA034..LA047`, но по пользовательскому скрину это отдельный retest/base вход после `LA042`.

Исправлено: группа разделена на `G20260519_005A_1308_1449` с winner `LA042` и `G20260519_005B_1525_1610` с winner `LA046`. `LA047` оставлен `GOOD_ALT`, `LA045` оставлен `BAD_IN_GROUP`.

Создан `STAS5_V4_GROUP_RANK_LEDGER_20260519_USER_CORRECTED_V1.csv`. Day19 теперь: `65` строк, `BEST_GOOD=6`, `GOOD_ALT=3`, `BAD_IN_GROUP=39`, `NO_TRADE_GROUP=17`; winners `LA005`, `LA016`, `LA032`, `LA042`, `LA046`, `LA063`.

Unified ledger пересчитан: `BEST_GOOD=58`, `GOOD_ALT=44`, `BAD_IN_GROUP=437`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-18

Проверен пользовательский скрин `2026-05-18` с красными обводками. Исправлены две зоны: `LA036` повышен до `BEST_GOOD` как отдельный pullback/retest после импульса вверх; `LA066` повышен до `BEST_GOOD` как late NY retest после вертикального движения. `LA065` стал `GOOD_ALT`.

Создан `STAS5_V4_GROUP_RANK_LEDGER_20260518_USER_CORRECTED_V1.csv`. Day18 теперь: `73` строки, `BEST_GOOD=7`, `GOOD_ALT=7`, `BAD_IN_GROUP=52`, `NO_TRADE_GROUP=7`; winners `LA006`, `LA019`, `LA034`, `LA036`, `LA049`, `LA061`, `LA066`.

Unified ledger пересчитан: `BEST_GOOD=57`, `GOOD_ALT=44`, `BAD_IN_GROUP=438`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit обновлен: `GOOD_ALT_MAY_NEED_MICRO_GROUP=41`, `BEST_GOOD_FROM_OLD_NON_ENTER=23`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`.

Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-17

Проверен пользовательский скрин `2026-05-17` против текущего V4 draft ledger. Сверка совпала: winners `LA004`, `LA006`, `LA036`, `LA046`, `LA063`; `GOOD_ALT` рядом с ними `LA003`, `LA005`, `LA044`. CSV не менялся, создан только отчет сверки.

Артефакт:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_REVIEW_20260517_USER_CHECKED_V1_RU.md
```

Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 screenshot check 2026-05-16

По пользовательскому скрину `2026-05-16` проверена текущая V4-разметка. Старый draft содержал 5 winners: `LA016`, `LA027`, `LA038`, `LA041`, `LA049`. На скрине красные отметки видны под первыми четырьмя зонами, а `LA049` отдельно не подчеркнут.

Сделано: создан `STAS5_V4_GROUP_RANK_LEDGER_20260516_USER_CORRECTED_V1.csv`; `LA049` и группа `LA043..LA049` переведены в `NO_TRADE_GROUP`; unified ledger пересчитан до `BEST_GOOD=55`, guard `PASS`. Обучение, features, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 micro-group correction 2026-05-15

Пользователь указал, что на скрине `2026-05-15` целевых входов шесть, и часть из них показана не зелеными `ENTER`, а желтыми ромбиками или серыми крестиками старого ML. Зафиксирована методическая правка: старый marker status не решает label; человечески подчеркнутая нижняя точка может быть `BEST_GOOD`.

Сделано:

1. Создан `STAS5_V4_GROUP_RANK_LEDGER_20260515_USER_CORRECTED_V2.csv`.
2. `LA004` повышен до отдельного `BEST_GOOD` в micro-group `G20260515_001A_0122_0203`.
3. `LA007` оставлен `BEST_GOOD` в micro-group `G20260515_001B_0222_0235`.
4. Unified ledger `2026-05-15..25` обновлен: `BEST_GOOD=56`, `GOOD_ALT=43`, guard `PASS`.
5. Создан risk audit для `2026-05-16..25`: `GOOD_ALT_MAY_NEED_MICRO_GROUP=40`, `BEST_GOOD_FROM_OLD_NON_ENTER=22`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`.

Обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 screenshot artifact inventory 2026-05-01..2026-05-25

По запросу пользователя найдены и проверены рабочие PNG-артефакты для `2026-05-01..2026-05-14` и `2026-05-15..2026-05-25`.

Создана папка навигации:

```text
STAS5_ML_CORE/artifacts/v4/review_navigation/20260714_artifact_inventory
```

Собраны контакт-листы train visual approval `01..14`, forward source `15..25` и V4 group-rank annotated blocks `15..25`. Индекс записан в CSV/JSON. Проверка `missing=[]`. Обучение, признаки, ledger и threshold не менялись.

## 2026-07-14 STAS5 V4 unified forward review 2026-05-15..2026-05-25

По пользовательскому уточнению исправлена рамка V4: `2026-05-15` входит в общий forward-review блок `2026-05-15..2026-05-25`, а не остается отдельным карантинным/approved днем. База обучения остается `2026-05-01..2026-05-14`.

Создан unified ledger `FORWARD_REVIEW_11_DRAFT_NO_TRAINING`: `738` строк, `55` `BEST_GOOD`, `55` winners. Главный `STAS5_V4_GROUP_RANK_LEDGER.csv` обновлен этим unified содержимым; старый 15-only файл сохранен как superseded-копия. Guard по ledger-структуре PASS. V4 обучение, threshold/Optuna/API/TP/Stas3/exit не запускались.

Дополнительно уточнен дневной ориентир: `2..5` входов - это не hard cap, а антишумовой ориентир. В разные режимы дня допустимо разное число лучших входов, включая больше `5`, если каждый вход является winner/alt своей группы и имеет reason-code. Метрика `ENTER_per_day` остается диагностикой overtrade/noise, а не фиксированным потолком.

## 2026-07-14 STAS5 V4 2026-05-15 Quarantine Removed

Пользователь снял `2026-05-15` с карантина. На базе `USER_CORRECTED_V1` создан approved ledger: `41` строка, `BAD_IN_GROUP=26`, `NO_TRADE_GROUP=6`, `BEST_GOOD=5`, `GOOD_ALT=4`; winners `LA007`, `LA021`, `LA024`, `LA054`, `LA061`; good-alt `LA004`, `LA005`, `LA053`, `LA060`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_APPROVED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_APPROVED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Guard approved-ledger: PASS. Все строки `label_status=APPROVED`, winner count по группам корректный, старые `ML_KEEP_SCORE/ML_DECISION`, postfact/future/TP/Stas3/exit в approved ledger не попали. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-25 Draft Group Review

По пользовательскому V3 forward-скриншоту `2026-05-25` создан V4 draft-разбор по группам выбора. Получилось `7` групп и `68` строк: `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=19`, `BEST_GOOD=5`, `GOOD_ALT=4`. Winners: `LA014`, `LA020`, `LA038`, `LA059`, `LA066`; good-alt: `LA006`, `LA015`, `LA019`, `LA067`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_REVIEW_20260525_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_LEDGER_20260525_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_REVIEW_20260525_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный, старые `ML_KEEP_SCORE/ML_DECISION` в V4-ledger не попали. Markdown проверен на кодировку; файл чистый UTF-8. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-24 Draft Group Review

По пользовательскому V3 forward-скриншоту `2026-05-24` создан V4 draft-разбор по группам выбора. Получилось `6` групп и `70` строк: `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=6`, `GOOD_ALT=5`, `BEST_GOOD=5`. Winners: `LA009`, `LA015`, `LA024`, `LA042`, `LA065`; good-alt: `LA005`, `LA008`, `LA014`, `LA023`, `LA067`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_REVIEW_20260524_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_LEDGER_20260524_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_REVIEW_20260524_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный, старые `ML_KEEP_SCORE/ML_DECISION` в V4-ledger не попали. Markdown проверен на кодировку; файл чистый UTF-8. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-23 Draft Group Review

По пользовательскому V3 forward-скриншоту `2026-05-23` создан V4 draft-разбор по группам выбора. Получилось `6` групп и `63` строки: `BAD_IN_GROUP=41`, `NO_TRADE_GROUP=12`, `GOOD_ALT=5`, `BEST_GOOD=5`. Winners: `LA007`, `LA022`, `LA033`, `LA036`, `LA051`; good-alt: `LA002`, `LA014`, `LA025`, `LA042`, `LA046`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_REVIEW_20260523_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_REVIEW_20260523_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный, старые `ML_KEEP_SCORE/ML_DECISION` в V4-ledger не попали. Markdown проверен на кодировку; файл чистый UTF-8. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-22 Draft Group Review

По пользовательскому V3 forward-скриншоту `2026-05-22` создан V4 draft-разбор по группам выбора. Получилось `6` групп и `75` строк: `BAD_IN_GROUP=55`, `NO_TRADE_GROUP=11`, `BEST_GOOD=5`, `GOOD_ALT=4`. Winners: `LA007`, `LA022`, `LA036`, `LA047`, `LA061`; good-alt: `LA005`, `LA024`, `LA043`, `LA062`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_REVIEW_20260522_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_LEDGER_20260522_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_REVIEW_20260522_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный, старые `ML_KEEP_SCORE/ML_DECISION` в V4-ledger не попали. Markdown проверен на кодировку; файл чистый UTF-8. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-21 Draft Group Review

По пользовательскому V3 forward-скриншоту `2026-05-21` создан V4 draft-разбор по группам выбора. Получилось `6` групп и `81` строка: `BAD_IN_GROUP=56`, `NO_TRADE_GROUP=15`, `GOOD_ALT=5`, `BEST_GOOD=5`. Winners: `LA006`, `LA019`, `LA045`, `LA059`, `LA066`; good-alt: `LA004`, `LA021`, `LA040`, `LA048`, `LA057`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_REVIEW_20260521_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_LEDGER_20260521_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_REVIEW_20260521_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный, старые `ML_KEEP_SCORE/ML_DECISION` в V4-ledger не попали. Markdown проверен на кодировку; файл чистый UTF-8. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-20 Draft Group Review

По пользовательскому скриншоту `2026-05-20` создан V4 draft-разбор по группам выбора. Получилось `7` групп и `68` строк: `NO_TRADE_GROUP=31`, `BAD_IN_GROUP=28`, `BEST_GOOD=5`, `GOOD_ALT=4`. Winners: `LA011`, `LA037`, `LA045`, `LA053`, `LA057`; good-alt: `LA002`, `LA035`, `LA040`, `LA052`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_REVIEW_20260520_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_LEDGER_20260520_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_REVIEW_20260520_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный, старые `ML_KEEP_SCORE/ML_DECISION` в V4-ledger не попали. Markdown проверен на кодировку; файл чистый UTF-8. Временные crop-файлы удалены, в папке дня оставлены только три рабочих артефакта. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-19 Draft Group Review

По пользовательскому скриншоту `2026-05-19` создан V4 draft-разбор по группам выбора с учетом красного нисходящего канала. Получилось `7` групп и `65` строк: `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=17`, `BEST_GOOD=5`, `GOOD_ALT=3`. Winners: `LA005`, `LA016`, `LA032`, `LA042`, `LA063`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_REVIEW_20260519_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_LEDGER_20260519_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_REVIEW_20260519_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный. Markdown проверен на кодировку; финальный файл чистый UTF-8. Временные crop-файлы удалены, в папке дня оставлены только три рабочих артефакта. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-18 Draft Group Review

По пользовательскому скриншоту `2026-05-18` создан V4 draft-разбор по группам выбора. Получилось `6` групп и `73` строки: `BAD_IN_GROUP=51`, `NO_TRADE_GROUP=11`, `GOOD_ALT=6`, `BEST_GOOD=5`. Winners: `LA006`, `LA019`, `LA034`, `LA049`, `LA061`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_REVIEW_20260518_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_LEDGER_20260518_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_REVIEW_20260518_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный. Markdown проверен на кодировку; финальный файл чистый UTF-8. Временные crop-файлы удалены, в папке дня оставлены только три рабочих артефакта. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-17 Draft Group Review

По пользовательскому скриншоту `2026-05-17` создан V4 draft-разбор по группам выбора. Получилось `8` групп и `63` строки: `NO_TRADE_GROUP=30`, `BAD_IN_GROUP=25`, `BEST_GOOD=5`, `GOOD_ALT=3`. Winners: `LA004`, `LA006`, `LA036`, `LA046`, `LA063`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_REVIEW_20260517_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_LEDGER_20260517_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_REVIEW_20260517_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный. Markdown проверен на кодировку после первичной ошибки записи через PowerShell; финальный файл чистый UTF-8. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 Review Encoding Fix

По замечанию пользователя про кракозябры проверены V4 review Markdown-файлы для `2026-05-15` и `2026-05-16`. Скан по `STAS5_ML_CORE/artifacts/v4/group_rank_review` проверил `3` Markdown-файла и нашел `0` проблем по длинным цепочкам вопросительных знаков, `U+FFFD` и CJK-мусору. В `docs/codex/commands.md` один литеральный `U+FFFD` из старой команды заменен на escape `\x{FFFD}`. Содержательные CSV/PNG и V4-разметка не менялись; обучение не запускалось.

## 2026-07-14 STAS5 V4 2026-05-16 Draft Group Review

По пользовательскому скриншоту `2026-05-16` создан V4 draft-разбор по группам выбора. Получилось `9` групп и `71` строка: `NO_TRADE_GROUP=38`, `BAD_IN_GROUP=27`, `BEST_GOOD=5`, `GOOD_ALT=1`. Winners: `LA016`, `LA027`, `LA038`, `LA041`, `LA049`.

Созданы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_REVIEW_20260516_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_LEDGER_20260516_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_REVIEW_20260516_ANNOTATED_DRAFT.png
```

Контроль CSV: reason-code покрыты схемой, неизвестных labels/reasons нет, group winner count корректный. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 2026-05-15 User-Corrected V1

Пользователь уточнил разбор графика `2026-05-15`: день нужно разметить как группы выбора, а не как отдельные строки. Зафиксирована версия `USER_CORRECTED_V1` с `6` группами и `41` строкой: `BAD_IN_GROUP=26`, `NO_TRADE_GROUP=6`, `BEST_GOOD=5`, `GOOD_ALT=4`; winners `LA007`, `LA021`, `LA024`, `LA054`, `LA061`. `LA004` оставлен как `GOOD_ALT`, чтобы в группе 1 был один winner; группа 4 оформлена как no-trade. Позже эта версия стала источником для `APPROVED_V1`.

Созданы/актуализированы артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_USER_CORRECTED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_ANNOTATED.png
```

Обновлен V4-ТЗ список reason-code и group features под пользовательскую правку. Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## 2026-07-14 STAS5 V4 Human-Style Group Ranker TZ

Статус: `STAS5_V4_20260515_SCREENSHOT_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому решению создан V4-контур: group ranker вместо построчного `KEEP/CUT`. Зафиксированы базовые `24` дня без `2026-05-15`, карантин для `2026-05-15`, обязательный будущий `STAS5_V4_GROUP_RANK_LEDGER.csv`, labels/reason-codes, group features, forbidden features и guard перед любым обучением.

Артефакты: `STAS5_ML_CORE/07_STAS5_V4_HUMAN_STYLE_GROUP_RANKER_TZ_RU.md`, `STAS5_ML_CORE/v4/README_RU.md`, `STAS5_ML_CORE/schemas/STAS5_V4_GROUP_RANK_LEDGER.schema.json`.

Обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

Дополнение по скриншоту пользователя `2026-05-15`: создан draft group-review и annotated PNG. Draft CSV содержит `41` строку по красным зонам и ложным старым `ENTER`: `BEST_GOOD=5`, `GOOD_ALT=3`, `BAD_IN_GROUP=22`, `NO_TRADE_GROUP=11`. Черновые winners: `LA004`, `LA007`, `LA021`, `LA054`, `LA061`; жесткий набор для `2..3` входов: `LA021`, `LA054`, `LA061`. Артефакты лежат в `STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/`. День `2026-05-15` остается `DRAFT`/карантин, не train.

## 2026-07-14 STAS5 V3 Review Train Forward

Статус: `STAS5_V3_REVIEW_TRAIN_FORWARD_21_25_READY`.

Собран отдельный V3-контур: user-review ledger `2026-05-16..2026-05-20`, V3 train dataset `2026-05-01..2026-05-14 + 2026-05-16..2026-05-20`, leakage guard, full274 model, blind-forward `2026-05-21..2026-05-25`.

Проверенный run: `stas5_v3_wrapper_smoke2_20260714`.

Ключевые результаты: ledger `34 KEEP_APPROVED / 100 CUT_APPROVED`, dataset `1106` rows / `274` features, guard `PASS`, forward `5/5` PNG READY, totals `ENTER=79`, `UNSURE=31`, `SKIP=247`.

Главный отчет: `STAS5_ML_CORE/06_STAS5_V3_REVIEW_TRAIN_FORWARD_RESULT_RU.md`.

Команда: `STAS5_ML_CORE/run_stas5_v3_review_train_forward_21_25.ps1`.

Проверки: `py_compile` PASS; V3/V2 targeted pytest PASS; PowerShell parse PASS; wrapper full smoke PASS.

### [2026-07-13T00:00:00Z] STAS5 | V2 FULL274 RUN CHECK | PASS TECHNICAL
1. Request:
   пользователь попросил проверить последний прогон, все ли там сошлось.
2. Checked:
   latest model pointer, latest forward pointer, model manifest, forward manifest, all-predictions CSV, day CSV и PNG.
3. Result:
   `stas5_v2_full274_20260713_203703` технически валиден: `model_feature_set=full_v2_all_274`, `feature_count=274`, guard `PASS`, forward `435` строк, `ENTER=77`, `UNSURE=24`, `SKIP=334`, `6/6` PNG READY.
4. Artifacts:
   `STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_FULL274_RUN_CHECK_20260713_203703_RU.md`; `STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_full274_run_check_20260713_203703_v0.json`.
5. Boundary:
   технический PASS не означает замену baseline: full274 AUC `0.649292`, baseline `v1_plus_risk_gate` AUC `0.684988`; нужен visual review.

### [2026-07-13T00:00:00Z] STAS5 | V2 FULL 274 WRAPPER | READY
1. Request:
   пользователь попросил подготовить полный прогон: добавить все `274` признака в модель, переобучить и выдать forward-графики `2026-05-15..2026-05-20`.
2. Code:
   создан `STAS5_ML_CORE/run_stas5_v2_full_274_train_forward.ps1`.
3. Result:
   wrapper пересобирает V2 train/forward признаки, запускает leakage guard/pre-ML/numeric audit, обучает `full_v2_all_274`, строит blind-forward и проверяет manifests на `model_feature_set=full_v2_all_274`, `feature_count=274`.
4. Validation:
   PowerShell syntax PASS; `py_compile` по V2-модулям PASS.
5. Boundary:
   сам тяжелый full 274 прогон не запускался; пользователь запускает команду вручную.

### [2026-07-13T00:00:00Z] STAS5 | V2 GRAPH TO FEATURE AUDIT | READY
1. Request:
   пользователь попросил проверить train-график `2026-05-04`: все ли индикаторы/стратегии/панели из красной области совпадают с цифрами для ML.
2. Audit:
   сверены visual manifest, V2 feature snapshot manifest/CSV и latest model manifest. Подключен read-only агент; локальная проверка выполнена без изменения model/training.
3. Result:
   `GRAPH_TO_FULL_SNAPSHOT=PASS`: `74` строки дня совпадают, `9 KEEP`, `65 CUT`, full snapshot `274` feature columns. `FULL_SNAPSHOT_TO_LATEST_MODEL=PARTIAL`: latest model `v1_plus_risk_gate` использует `126` признаков и не берет combo/density/structure/STAS4 blocks/pattern/short-wave/divergence.
4. Artifacts:
   `STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_GRAPH_TO_FEATURE_AUDIT_20260504_RU.md`; `STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_graph_to_feature_audit_20260504_v0.json`.
5. Boundary:
   новое обучение, threshold tuning, TP/Stas3/API/Optuna не запускались.

### [2026-07-13T00:00:00Z] STAS5 | V2 TRAIN VISUAL BATCH | READY
1. Request:
   пользователь указал, что если ML train покрывает `01..14`, то и обновленные train-графики должны быть за все 14 дней, а не один `20260504`.
2. Code:
   создан `src/mlbotnav/stas5_v2_train_visual_batch.py`.
3. Result:
   batch-render `stas5_v2_train_visual_20260713_14d` создал `14/14` PNG из `stas5_v2_feature_snapshot_20260501_20260514_v0.csv`.
4. Artifacts:
   `STAS5_ML_CORE/artifacts/v2/visual_approval/runs/stas5_v2_train_visual_20260713_14d/`.
5. Validation:
   PNG count `14`, rows `972`, KEEP `115`, CUT `857`, image size `4960x4557`, visual smoke opened `20260501`, full STAS5 tests `34 passed`.
6. Boundary:
   это visual/audit only; model training, forward tuning, TP/Stas3/API/Optuna не запускались.

### [2026-07-13T00:00:00Z] STAS5 | V2 RUN ISOLATION | READY
1. Request:
   пользователь указал, что повторные прогоны нужно различать папками, а не писать поверх старых `forward/20260515..20260520`.
2. Code:
   обновлены `src/mlbotnav/stas5_v2_entry_ranker_train.py` и `src/mlbotnav/stas5_v2_forward_entry_review.py`. Добавлен `--run-id`, `--run-root`, run-specific output paths и latest pointers.
3. Result:
   обучение пишет в `STAS5_ML_CORE/artifacts/v2/model/runs/<run_id>/`, forward пишет в `STAS5_ML_CORE/artifacts/v2/forward/runs/<run_id>/`.
4. Smoke:
   выполнен isolated run `stas5_v2_run_20260713_190743`; созданы model artifacts и forward PNG за `20260515..20260520`.
5. Validation:
   `py_compile` PASS; focused tests `4 passed`; full STAS5 tests `34 passed`.
6. Boundary:
   TP/Stas3/API/Optuna не запускались; изменение только про раскладку артефактов по run folders.

### [2026-07-13T00:00:00Z] STAS5 | V2 CONTROLLED MODEL + FORWARD | READY
1. Request:
   пользователь подтвердил идти после numeric coverage до результата: ablation, controlled train, forward `15..20`, графики с ML-входами, без остановки на середине.
2. Agents:
   подключены два read-only агента. Первый подтвердил безопасный train route: V1 не трогать, V2 output отдельно, feature groups для ablation, no leakage/yellow/forward tuning. Второй подтвердил, что старый V1 forward scorer нельзя использовать как есть: нужен V2 scorer с join forward Stas2 + V2 combo features.
3. Code:
   созданы `src/mlbotnav/stas5_v2_entry_ranker_train.py`, `src/mlbotnav/stas5_v2_forward_entry_review.py`, `tests/test_stas5_v2_entry_ranker_train.py`, `tests/test_stas5_v2_forward_entry_review.py`.
4. Ablation:
   лучший train LOO набор `v1_plus_risk_gate`: `126` features, AUC `0.684988`; `full_v2_all_274` дал AUC `0.649292`, поэтому не выбран как controlled model.
5. Model:
   trained model `STAS5_ML_CORE/artifacts/v2/model/stas5_v2_entry_ranker_20260501_20260514_v0.joblib`; train LOO decisions `ENTER=201`, `UNSURE=114`, `SKIP=657`; KEEP->ENTER/UNSURE `0.583`.
6. Forward:
   blind-forward `2026-05-15..2026-05-20`: `ENTER=106`, `UNSURE=45`, `SKIP=284`; PNG по 6 дням готовы в `STAS5_ML_CORE/artifacts/v2/forward/`.
7. Validation:
   `py_compile` PASS; новые tests `4 passed`; V2 leakage guard `PASS`; full STAS5 tests `34 passed`; PNG check `6/6`, `4640x3987`.
8. Boundary:
   forward postfact audit-only; threshold не подбирался по forward; TP/Stas3/API/Optuna/scorer/target-lock не запускались.

### [2026-07-13T00:00:00Z] STAS5 | V2 NUMERIC COVERAGE AUDIT | READY
1. Request:
   пользователь уточнил важный принцип: ML видит не красоту графика, а числа, поэтому нужно с агентами сопоставить, какие индикаторы, фичи, стратегии и блоки реально передаются в ML numerically, а что отсутствует.
2. Agents:
   подключены два read-only агента. Оба подтвердили gap: четыре STAS4 strategy-блока были visual/audit-only, pattern слой был частичным, SHORT/WAVE контекст не был полноценно представлен causal feature-группой.
3. Code:
   обновлены `src/mlbotnav/stas5_common.py`, `src/mlbotnav/stas5_v2_combo_feature_exporter.py`, `src/mlbotnav/stas5_v2_pre_ml_audit.py`; добавлен `src/mlbotnav/stas5_v2_numeric_coverage_audit.py`; обновлены тесты V2 exporter/leakage guard и добавлен numeric coverage test.
4. Features:
   добавлены `stas4_v2_block_*`, `stas4_v2_pattern_*`, `stas5_v2_short_wave_*`. Они являются context features, не hard-filter и не strategy vote target.
5. Artifacts:
   пересобраны train/forward combo features, V2 train snapshot, leakage guard, forward error ledger, pre-ML audit и coverage audit за `2026-05-04`.
6. Result:
   V2 combo features `103 -> 163`, полный train snapshot `214 -> 274`; train rows `972`, forward rows `435`; forbidden feature columns `{}`; `KEEP_DRAFT + yellow_x = 30`; guard `PASS`.
7. Validation:
   `py_compile` PASS; V2 tests `23 passed`; STAS5 tests `30 passed`. Попытка wildcard `pytest tests\test_stas5_v2_*.py -q` через PowerShell не раскрыла маску, затем тесты были переданы списком файлов и прошли.
8. Boundary:
   обучение, ablation, threshold tuning, Optuna/scorer/target-lock/API, Stas3/TP/exit не запускались. Следующий шаг - пользователь принимает numeric coverage, затем можно идти к V2 ablation baseline.

### [2026-07-13T00:00:00Z] STAS5 | V2 STRATEGY AUDIT STRIP | READY
1. Request:
   пользователь уточнил, что перед следующим пунктом нужно видеть на графике 4 выбранных STAS4-блока: `density_profile+structure_ta`, `pattern+structure_ta`, `structure_ta+volume_flow`, `structure_ta+trend_momentum`.
2. Agent:
   подключен read-only агент. Он подтвердил, что `_family_marks(...)` можно использовать для `2026-05-04`, но прямой пересчет четырех combo слишком тяжелый из-за повторного `structure_ta`.
3. Code:
   обновлен `src/mlbotnav/stas5_v2_feature_visual_approval.py`: добавлен `STAS4 Audit` strip, кэш базовых family payloads и сбор combo-пересечений из кэша. Обновлен `tests/test_stas5_v2_feature_visual_approval.py`.
4. Artifacts:
   пересобраны `STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png` и manifest.
5. Result:
   strategy audit counts: `density_profile+structure_ta X=22/UP=2`, `pattern+structure_ta X=38/UP=1`, `structure_ta+volume_flow X=52/UP=1`, `structure_ta+trend_momentum X=59/UP=4`. Основные human-маркеры не изменены: `KEEP=9`, `CUT=65`, `yellow_x_cut=18`, `KEEP+yellow_conflict=4`.
6. Validation:
   `py_compile` PASS; `pytest tests/test_stas5_v2_feature_visual_approval.py -q` PASS (`5 passed`); render command PASS. Пробный прямой рендер упал по timeout, хвостовые python-процессы остановлены; после кэша полный рендер прошел за ~75 секунд.
7. Boundary:
   новая полоса audit-only. Она не запускает ablation/training, не является hard-filter, ML-target, threshold или trading permission. Следующий шаг - пользователь смотрит PNG и дает `норм / править`.

### [2026-07-13T00:00:00Z] STAS5 | V2 FORWARD USER REVIEW | PAGES READY
1. Request:
   пользователь посмотрел V2 quicklook `2026-05-15` и сказал, что видит только около 3 реальных входов, остальное шум; попросил продолжать по плану.
2. Code:
   создан `src/mlbotnav/stas5_v2_forward_user_review.py`. Renderer строит крупные страницы по 3 часа с OHLCV-свечами, LA-id, `knife_risk`, `short_pressure`, `long_recovery`, RSI/MACD/Stoch combo-панелью и risk buckets.
3. Artifacts:
   созданы `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_FULL.png`, `PAGE_01_0000_0300.png` ... `PAGE_08_2100_0000.png`, `STAS5_V2_USER_REVIEW_TEMPLATE_20260515.csv`, manifest.
4. Result:
   command `PASS 90`; buckets: `54 HIGH_RISK`, `30 CAUTION`, `5 LOW_RISK`, `1 BLOCKED`. CSV template содержит `90` строк и поля `user_review_label`, `user_note`, risk/combo/structure/density признаки.
5. Validation:
   `py_compile` PASS; renderer command PASS. Первая, вторая и пятая страницы открыты визуально и читаемы. Первая попытка упала из-за несброшенного индекса свечей в окне; исправлено через `reset_index(drop=True)`.
6. Update:
   обновлены `STAS5_ML_CORE/README_RU.md`, `docs/codex/current_state.md`, `handoff.md`, `todo.md`, `commands.md`, `session_log.md`.
7. Boundary:
   это forward audit-only для ручного выбора LA-id. `2026-05-15` не используется для обучения, threshold tuning или финального trading permission. Optuna/scorer/target-lock/API/Stas3/TP/exit не запускались.

### [2026-07-13T00:00:00Z] STAS5 | V2 COMBO FEATURE EXPORTER | READY
1. Request:
   пользователь подтвердил следующий шаг V2: начинать с `stas5_v2_combo_feature_exporter.py`, чтобы превратить нижний combo-индикатор STAS4 в реальные causal ML-признаки, и попросил взять агентов.
2. Agents:
   подключены два read-only агента. Первый разобрал STAS4 combo/density/structure/divergence функции и подтвердил, что snapshot надо делать на `anchor_time_utc`, не на entry-свече. Второй подтвердил train/forward row universe, join keys `day,candidate_id,record_id`, forward source `435` строк и guardrails.
3. Code:
   создан `src/mlbotnav/stas5_v2_combo_feature_exporter.py`. Он пересчитывает RSI/MACD/Stoch/ATR, confirmed divergence, density profile, structure votes, volume flow и первые risk/gate признаки из OHLCV. PNG не используется как источник данных.
4. Artifacts:
   созданы `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.csv`, `.manifest.json`, `stas5_v2_combo_features_20260515_20260520_forward_v0.csv`, `.manifest.json`.
5. Result:
   train export `PASS 972 103`; forward export `PASS 435 103`; manifests: row parity true, missing OHLCV none, forbidden columns `{}`, `feature_available_before_entry_false=0`.
6. Validation:
   `py_compile` PASS; `pytest tests/test_stas5_v2_combo_feature_exporter.py -q` PASS (`4 passed`); explicit STAS5 test pack PASS (`11 passed`). Команда `pytest tests\test_stas5_*.py -q` через PowerShell не сработала из-за wildcard, затем файлы были переданы явно.
7. Update:
   обновлены `STAS5_ML_CORE/README_RU.md`, `05_STAS5_V2_CONTOUR2_TZ_RU.md`, `docs/codex/current_state.md`, `handoff.md`, `todo.md`, `known_errors.md`, `commands.md`.
8. Boundary:
   это готовый V2 feature-layer, не финальная модель и не trading permission. Следующий шаг - V2 feature snapshot, leakage guard, pre-ML audit и forward error ledger. Optuna/scorer/target-lock/API/мост Bybit/Stas3/TP/exit не запускались.

### [2026-07-13T00:00:00Z] STAS5 | V1 HARD AUDIT | V2 CONTOUR 2 TZ READY
1. Request:
   пользователь попросил подключить несколько агентов, жестко проверить работоспособность STAS5 ML v1, что было подключено и не подключено, почему появились неправильные зеленые входы, найти combo-индикаторный блок и собрать новое ТЗ для STAS5 V2 / контур 2.
2. Agents:
   запущены три read-only агента: аудит STAS5 v1 pipeline, аудит STAS4 combo-spectrum, аудит forward-ошибок. Файлы агенты не меняли, ML/training/Optuna/scorer/API не запускали.
3. Findings:
   v1 pipeline технически согласован: ledger `972`, `115 KEEP_DRAFT`, `857 CUT_DRAFT`, `30 KEEP_DRAFT + yellow_x`, feature count `111`, leakage guard `PASS`, model `CONTROLLED_BASELINE_READY`. Но combo/STAS4 features в v1 model matrix отсутствуют: `combo/spectrum=0`, `density/structure/stoch/atr/divergence=0`.
4. Combo:
   найден STAS4 combo-spectrum: `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum`; код `src/mlbotnav/visual_entry_stas4_family_overlay.py`; JSON guardrail: `combo_spectrum_is_visual_feature_layer_not_ml_training`.
5. Forward:
   по `2026-05-15..2026-05-20` `ENTER` имеет `103` rows, `hit0.5=74.8%`, `hit1.0=46.6%`, median `max_up=0.951%`, median drawdown `-1.453%`. Проблема пользователя подтверждена на `2026-05-15`: `14 ENTER`, `hit1.0=14.3%`, median drawdown `-2.834%`.
6. Update:
   созданы `STAS5_ML_CORE/04_STAS5_V1_HARD_AUDIT_RU.md` и `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`; обновлены `STAS5_ML_CORE/README_RU.md`, `docs/codex/current_state.md`, `handoff.md`, `todo.md`, `known_errors.md`, `commands.md`.
7. Decision:
   STAS5 v1 оставить как `CONTROLLED_BASELINE / AUDIT_REFERENCE`, но не использовать как production entry permission. Следующий правильный этап - V2 contour 2: combo feature exporter, phase gate, long permission gate, risk/noise filter, forward error ledger, ablation/calibration/permutation audit.
8. Boundary:
   не подбирать threshold по forward `15+`; не превращать yellow X в hard-cut; не использовать postfact как feature; Stas3/TP/exit, Optuna, scorer, target-lock, API и мост Bybit не запускались.

### [2026-07-10T16:45:00Z] STAS5 | ENTRY ML PIPELINE | READY
1. Request:
   пользователь попросил идти по `STAS5_ML_CORE/03_STAS5_CURRENT_EXECUTION_INSTRUCTION_RU.md` от начала до конца, подключить агента, собрать STAS5 ML-проект полностью и не останавливаться на полпути при мелких поломках.
2. Agent:
   подключенный read-only агент подтвердил, что forward `2026-05-15+` нужно строить из локального `data/core/bybit_ohlcv`, через генерацию Stas1-кандидатов и Stas2 pre-entry context; готовых canonical Stas1/Stas2 runs на `2026-05-15+` нет. API, мост Bybit, Optuna и Stas3 не нужны для текущего entry-only контура.
3. Code:
   созданы модули `src/mlbotnav/stas5_common.py`, `stas5_ml_ledger_builder.py`, `stas5_feature_snapshot_builder.py`, `stas5_leakage_guard.py`, `stas5_pre_ml_audit.py`, `stas5_entry_ranker_train.py`, `stas5_forward_entry_review.py`.
4. Artifacts:
   собраны `STAS5_ML_CORE/artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.csv`, `artifacts/features/stas5_feature_snapshot_20260501_20260514_v0.csv`, `artifacts/guard/stas5_leakage_guard_20260501_20260514_v0.json`, `artifacts/audit/STAS5_PRE_ML_AUDIT_20260501_20260514_RU.md`, `artifacts/model/stas5_entry_ranker_20260501_20260514_v0.joblib`, train predictions и forward CSV/PNG за `2026-05-15..2026-05-20`.
5. Result:
   ledger `972` rows, `115 KEEP_DRAFT`, `857 CUT_DRAFT`, `30 KEEP_DRAFT + yellow_x`; feature snapshot `111` model features; leakage guard `PASS`; audit `READY_FOR_CONTROLLED_BASELINE`; baseline `CONTROLLED_BASELINE_READY`; forward `FORWARD_ENTRY_REVIEW_READY`. Baseline metrics: AUC `0.6828`, KEEP recall `ENTER` `0.4087`, KEEP recall `ENTER+UNSURE` `0.5652`, CUT precision `SKIP` `0.9226`.
6. Forward:
   `2026-05-15`: `90` rows, `14 ENTER`, `12 UNSURE`, `64 SKIP`; `2026-05-16`: `76`, `12/6/58`; `2026-05-17`: `63`, `18/8/37`; `2026-05-18`: `73`, `21/8/44`; `2026-05-19`: `65`, `20/12/33`; `2026-05-20`: `68`, `18/9/41`.
7. Validation:
   `py_compile` PASS; `pytest tests/test_stas5_*.py -q` PASS (`7 passed`); real ledger/features/guard/audit/train/forward commands PASS; final artifact validation PASS. `git diff --check` не показал новых whitespace-ошибок, только старые CRLF warnings по документам.
8. Boundary:
   это controlled baseline entry-ranker, не production trading permission. Labels пока `DRAFT`; yellow X остается `AUDIT_ONLY`; forward `15+` нельзя использовать для обучения или threshold tuning. Stas3/TP/exit, Optuna, scorer, target-lock, API и мост Bybit не запускались.

### [2026-07-10T14:25:00Z] STAS5 | TZ DRY UPDATE | TRAIN 1-14 FORWARD 15+
1. Request:
   пользователь уточнил, что STAS-5 должен учиться на `2026-05-01..2026-05-14`, а затем показывать ML-точки входа на `2026-05-15+` в CSV/PNG; TP/Stas3 не участвуют.
2. Update:
   `STAS5_ML_CORE/03_STAS5_CURRENT_EXECUTION_INSTRUCTION_RU.md` переписан как сухое рабочее ТЗ: train/manual label window `2026-05-01..2026-05-14`, forward/blind check window `2026-05-15+`, каждая кандидатная точка на PNG получает `ENTER/UNSURE/SKIP`.
3. Guard:
   forward `2026-05-15+` запрещено использовать для обучения, подбора threshold или ручной доводки. Future outcome запрещен как feature/target/filter/threshold input и разрешен только post-fact audit/backtest.
4. Boundary:
   код ML, training, Optuna, scorer, target-lock, API, мост Bybit и Stas3/TP/exit не запускались.

### [2026-07-10T14:05:00Z] STAS5 | CURRENT EXECUTION INSTRUCTION | READY
1. Request:
   пользователь попросил подключить агента и структурировать, где мы сейчас, где ТЗ, чего не хватает и что конкретно делаем, чтобы правильно подготовить данные для ML.
2. Update:
   создана текущая инструкция `STAS5_ML_CORE/03_STAS5_CURRENT_EXECUTION_INSTRUCTION_RU.md`. В ней зафиксировано: старый `MLbotNav` остается `LAB/ARCHIVE`; перенос в новый `MLbotNav_CORE` пока не делаем; текущий пункт - собрать STAS5 ML-ledger по `972` входам, затем feature snapshot, leakage guard и pre-ML audit.
3. Result:
   агент `Mill` сделал read-only аудит и подтвердил: manual labels/Stas1/Stas2 дают `972` строк, старый ML-каркас пригоден только как инфраструктура, но не как STAS5 target. Следующий практический шаг: создать `src/mlbotnav/stas5_ml_ledger_builder.py`, собрать `STAS5_ML_CORE/artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.csv`, проверить `972` rows, `115` KEEP, `857` CUT, `30` KEEP с yellow X, row parity с `STAS2_RECORDS.csv`.
4. Boundary:
   ML/export/training, Optuna, scorer, target-lock, API, мост Bybit и Stas3 TP/exit не запускались.

### [2026-07-10T13:40:00Z] STAS5 | MEMORY REFRESH | CURRENT NEXT
1. Request:
   пользователь попросил обновить память: что именно сейчас делаем по STAS-5.
2. Update:
   в `STAS5_ML_CORE/README_RU.md` и верхних блоках `docs/codex/handoff.md`, `docs/codex/current_state.md`, `docs/codex/todo.md`, `docs/codex/known_errors.md`, `docs/codex/commands.md` зафиксирован текущий next step.
3. Result:
   рабочий маршрут STAS-5: сначала ML-ledger по `972` входам `2026-05-01..2026-05-14`, затем pre-entry feature snapshot, затем audit `KEEP_DRAFT` против `CUT_DRAFT` без обучения. Yellow X остается `AUDIT_ONLY`; `KEEP + yellow_x` нельзя терять.
4. Boundary:
   ML/export/training, Optuna, scorer, target-lock, API, мост Bybit и Stas3 TP/exit не запускались.

### [2026-07-10T13:35:00Z] STAS4 | MOVE TO ROOT | READY
1. Request:
   пользователь указал, что STAS4 не виден в корне рядом со STAS1/STAS2/STAS3/STAS5, и попросил перенести правильно в корень.
2. Update:
   папка `reports/final_review/stas4_feature_hypothesis_screen_v0` перенесена в `STAS4_FEATURE_HYPOTHESIS_REVIEW`; добавлен `STAS4_FEATURE_HYPOTHESIS_REVIEW/README_RU.md`; дефолтный `--out-dir` в `src/mlbotnav/visual_entry_stas4_family_overlay.py` обновлен на новый корневой путь; текстовые ссылки в документах/отчетах обновлены.
3. Result:
   STAS4 теперь находится в корне проекта. В `reports/final_review/STAS4_MOVED_TO_ROOT_RU.md` добавлен указатель на новый путь. Часть старых пустых директорий `20260504..20260514` осталась в старом месте из-за Windows-lock со стороны просмотрщика/проводника; это не источник правды.
4. Boundary:
   это перенос артефактов и ссылок, не пересчет стратегий. Stas1/Stas2/Stas4 логика не менялась. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T13:25:00Z] STAS5 | ML ENTRY ARCHITECTURE | DRAFT SOURCE-OF-TRUTH
1. Request:
   пользователь дал целевую архитектуру `STAS-5: ML по входам`, где ML должен учиться по `candidate entry + pre-entry features -> human KEEP/CUT`, а не по желтому `X` или стратегии.
2. Update:
   создана видимая корневая папка `STAS5_ML_CORE/` с README, архитектурным ТЗ, контрактом ML-ledger/feature snapshot и YAML-схемами `stas5_ml_ledger_v0.yaml`, `stas5_feature_snapshot_v0.yaml`.
3. Result:
   зафиксировано правило `human KEEP > strategy vote`; yellow X является `AUDIT_ONLY`; первый baseline должен исключать `yellow_x`, `would_cut`, `strategy_cut`, `strategy_vote`. Следующий шаг - ML-ledger по `972` входам и audit признаков без запуска ML.
4. Boundary:
   Stas1/Stas2/Stas4 логика не менялась. Stas3 не входит в STAS-5 по входам. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T13:05:00Z] STAS4 | YELLOW X AUDIT ONLY RULE | FIXED
1. Request:
   пользователь попросил зафиксировать решение, чтобы желтый `X` не мог резать хорошие пользовательские сделки и не испортил будущую ML-разметку.
2. Update:
   принято правило `YELLOW_X_AUDIT_ONLY_FIXED_RULE_NO_ML_NO_OPTUNA`: yellow X хранится только как audit/vote-флаг, не является label, hard-filter, запретом входа или причиной закрытия. Создан файл `YELLOW_X_AUDIT_ONLY_RULE_RU.md`.
3. Result:
   проверка CSV по `2026-05-01..2026-05-14` показала `972` total, `115` KEEP_DRAFT, `857` CUT_DRAFT, `287` yellow X всего и `30` KEEP_DRAFT с yellow X. Поэтому hard-cut по `yellow_x = 1` запрещен.
4. Boundary:
   это архитектурный guard для будущей ML-подготовки. Stas1/Stas2/Stas4 логика не менялась. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T12:45:00Z] STAS4 | MANUAL LABELS 20260514 | DRAFT COMPLETE 14D
1. Request:
   пользователь прислал скрин `2026-05-14` как финальный день ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260514_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260514_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260514_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260514_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA014`, `LA015`, `LA032`, `LA039`, `LA046`, `LA047`, `LA048`, `LA049`, `LA053`, `LA055`, `LA056`.
3. Result:
   `11` KEEP_DRAFT, `66` CUT_DRAFT, всего `77` входов дня. Итог пачки `2026-05-01..2026-05-14`: `972` total, `115` KEEP_DRAFT, `857` CUT_DRAFT. Желтый `X` среди выбранных за `2026-05-14`: `LA047`, `LA053`. `LA014` и `LA015` оставлены как две отдельные ранние отметки double-bottom.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. Stas1/Stas2/Stas4 логика не менялась. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T12:25:00Z] STAS4 | MANUAL LABELS 20260513 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-13` как продолжение ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260513_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260513_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260513_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260513_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA002`, `LA043`, `LA058`, `LA072`.
3. Result:
   `4` KEEP_DRAFT, `82` CUT_DRAFT, всего `86` входов дня. Желтый `X` среди выбранных: только `LA058`. Первая отметка была разбита курсором и объединена в `LA002`; `LA043` и `LA072` выбраны как более нижние локальные входы в близких кластерах.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T12:15:00Z] STAS4 | MANUAL LABELS 20260512 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-12` как продолжение ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260512_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260512_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260512_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260512_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA006`, `LA012`, `LA036`, `LA038`, `LA051`, `LA055`.
3. Result:
   `6` KEEP_DRAFT, `70` CUT_DRAFT, всего `76` входов дня. Желтый `X` среди выбранных: только `LA036`. `LA051` выбран по прямому времени пользовательского подчеркивания, несмотря на близкие более поздние `LA052/LA053`.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T12:05:00Z] STAS4 | MANUAL LABELS 20260511 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-11` как продолжение ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260511_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260511_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260511_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260511_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA014`, `LA016`, `LA029`, `LA041`, `LA045`, `LA046`, `LA048`, `LA052`, `LA053`, `LA060`.
3. Result:
   `10` KEEP_DRAFT, `66` CUT_DRAFT, всего `76` входов дня. Желтый `X` среди выбранных: только `LA016`. Для скрина применена отдельная X-калибровка из-за другой ширины PNG.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T11:55:00Z] STAS4 | MANUAL LABELS 20260510 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-10` как продолжение ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260510_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260510_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260510_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260510_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA006`, `LA030`, `LA035`, `LA041`, `LA045`, `LA046`, `LA051`, `LA056`, `LA057`, `LA059`.
3. Result:
   `10` KEEP_DRAFT, `52` CUT_DRAFT, всего `62` входа дня. Желтый `X` среди выбранных: `LA030`, `LA035`, `LA041`, `LA045`, `LA046`, `LA051`.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T11:45:00Z] STAS4 | MANUAL LABELS 20260509 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-09` как продолжение ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260509_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260509_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260509_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260509_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA001`, `LA002`, `LA013`, `LA018`, `LA028`, `LA043`, `LA047`.
3. Result:
   `7` KEEP_DRAFT, `60` CUT_DRAFT, всего `67` входов дня. Среди выбранных входов нет желтых `X` стратегии `density_profile+structure_ta`; `LA043` и `LA047` выбраны как нижние локальные входы в близких кластерах.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## 2026-07-10 STAS2/STAS4 Compact Strips

Пользователь попросил не менять логику, а только сделать нижние блоки `ФОН/LONG/SHORT/WAVE` в 2 раза ниже и вернуть читаемую нижнюю ось времени `00:00 ... 00:00`.

Сделано:

- в Stas2 добавлены общие компактные `OVERVIEW_HEIGHT_RATIOS`;
- в Stas4 overlay подключены те же размеры, чтобы скрин `STAS4 overlay ... on STAS2` совпадал с Stas2;
- добавлен helper `_set_day_time_axis`, который явно ставит тики `00:00, 02:00, ..., 22:00, 00:00`;
- добавлен тест `_day_time_ticks`.

Проверки прошли: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py -q`, smoke Stas2 `2026-05-11`, smoke Stas4 `pattern+structure_ta`. PNG непустые.

### [2026-07-09T12:36:22Z] STAS3 | V2 CLEAN REBUILD | READY
1. Request:
   пользователь остановил работу и указал, что предыдущий V2 был сделан неправильно: нельзя было брать старый Stas3 как базу, нужно было собрать Stas3 V2 с нуля по Stas2-графикам/таблицам.
2. Correction:
   run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925` помечен как `INVALID_OLD_STAS3_BASE_DRAFT`; добавлен файл `STAS3_V2_OLD_BASE_DRAFT_INVALID_RU.md`.
3. Code:
   создан новый clean-модуль `src/mlbotnav/visual_entry_stas3_v2_clean_review.py`. Он не импортирует и не наследует старый Stas3. Источники: `STAS2_RECORDS.csv`, `STAS2_HOURLY_PHASES.csv`, `STAS2_MACRO_WAVES.csv`, `STAS2_CONTINUOUS_WAVES.csv` и исходные 1m свечи.
4. Commands:
   добавлены `STAS3_PERCENT_LADDER_REVIEW/run_clean_v2.ps1` и `STAS3_PERCENT_LADDER_REVIEW/open_clean_v2_last_run.ps1`.
5. Final clean run:
   `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_clean_20260510_20260512_long_only_20260709_123622`.
6. Result:
   `214` входов, `214` обработано, `0` skipped, row parity PASS, `157` hit 1%, `79` clean medium TP `>=1%`, `111` wrong 1% TP, `38` good-entry-but-wrong-1% TP, `99` noise, `41` phase ladder rows, `66` PNG, пустых PNG нет.
7. Artifacts:
   `STAS3_V2_CLEAN_ENTRY_CONTEXT.csv`, `STAS3_V2_CLEAN_TP_PATH.csv`, `STAS3_V2_CLEAN_TP_DECISION.csv`, `STAS3_V2_CLEAN_PHASE_LADDER.csv`, `STAS3_V2_CLEAN_WRONG_TP.csv`, `STAS3_V2_CLEAN_NOISE.csv`, `STAS3_V2_CLEAN_REPORT_RU.md`, `STAS3_V2_CLEAN_TABLES.xlsx`.
8. Validation:
   `py_compile PASS`; `pytest tests/test_visual_entry_stas3_v2_clean_review.py -q` PASS (`2 passed`); `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q` PASS (`4 passed`); full clean run PASS; acceptance CSV/XLSX/PNG PASS; визуально проверены `STAS3_V2_CLEAN_DAY_OVERVIEW_20260511.png` и `STAS3_V2_CLEAN_ENTRY_PAGE_01.png`.
9. Boundary:
   clean V2 остается post-entry audit/review, не стратегией. `SHORT` только risk-context. `WAVE/GAP/continuous` только hindsight-review. `clean_review_tp_pct` не является live TP, scorer, target-lock или ML-label. ML/export/training, Optuna и API не запускались.

### [2026-07-09T11:29:25Z] STAS3 | V2 LONG ONLY IMPLEMENTATION | READY
1. Request:
   пользователь попросил запустить агента и довести Stas3 V2 до рабочего результата до конца; старый Stas3 должен остаться архивным/замороженным, short-сделки не используются.
2. Agent:
   подключен subagent `Kepler`; он сделал read-only аудит acceptance checks, файлы не менял, старые runs не трогал, ML/Optuna/API/training/export не запускал.
3. Code:
   в `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py` реализован V2-контракт: LONG-only, `entry_price_for_calc = entry_price_5bps`, без fallback на `entry_open`, V2-сетка `0.3..0.9` шаг `0.1`, `1.0..2.0` шаг `0.1`, `2.2..20.0` шаг `0.2`, `2.0` без дубля. Добавлен join Stas2-context bundle: session/background/LONG/SHORT-risk/WAVE/GAP/continuous/volume. `MFE MAX` оставлен только как diagnostic, не как TP/exit.
4. Outputs:
   добавлены V2-файлы `STAS3_V2_ENTRY_TP_AUDIT.csv`, `STAS3_V2_CONTEXT_BUNDLE.csv`, `STAS3_V2_TP_LADDER_BY_PHASE.csv`, `STAS3_V2_WRONG_TP_REVIEW.csv`, `STAS3_V2_SKIPPED_ROWS.csv`, `STAS3_V2_REPORT_RU.md`, `STAS3_V2_TP_LADDER_RU.md`; Excel получил листы `V2 Entry TP Audit`, `V2 Context Bundle`, `V2 Wrong TP Review`, `V2 TP by phase`.
5. Final run:
   `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925`.
6. Source:
   `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`, дни `2026-05-10`, `2026-05-11`, `2026-05-12`.
7. Result:
   `214` input rows, `214` entry rows, `0` skipped, row parity PASS, `157` hit `1%`, `93` rows with reasonable TP, `76` wrong 1% TP, `46` noise entries, `122` rows in wrong TP review, `55` PNG, empty PNG `0`.
8. Validation:
   `py_compile PASS`; `pytest tests/test_visual_entry_stas3_percent_ladder_review.py tests/test_visual_entry_low_anchor_suggester.py -q` PASS (`3 passed`); `pytest tests/test_visual_entry_stas2_market_phase_review.py -q` PASS (`3 passed`); full V2 run PASS; contract audit PASS: no `0.2` ladder level, `20.0` present, `entry_price_for_calc == entry_price_5bps`, `direction_scope=LONG_ONLY`, `short_context_only_flag=True`, required V2 files and Excel sheets present.
9. Boundary:
   Stas3 V2 остается post-entry audit/review, не торговой стратегией. `SHORT` только risk-context. `WAVE/GAP/continuous` - hindsight-review, не causal feature. `ideal_review_tp_pct` - review-вывод, не команда в рынок, не scorer, не target-lock и не ML-label. ML/export/training, Optuna и API не запускались.

### [2026-07-09T09:20:00Z] STAS3 | V2 RESET TZ | DRAFT READY
1. Request:
   пользователь сказал, что Stas3 сейчас кривой, нужно обнулить и собрать новое ТЗ.
2. Decision:
   безопасное обнуление без удаления старых runs: текущий Stas3 V1 заморожен как `STAS3_V1_ARCHIVE_REVIEW_ONLY`.
3. Artifact:
   создано новое ТЗ `STAS3_PERCENT_LADDER_REVIEW/TZ_STAS3_V2_RESET_RU.md`.
4. Content:
   V2 запрещает трактовать `MFE MAX` как TP, запрещает рисовать идеальную сделку до максимума как основной выход, разделяет causal/review/hindsight context, требует таблицы `STAS3_V2_ENTRY_TP_AUDIT.csv`, `STAS3_V2_TP_LADDER_BY_PHASE.csv`, `STAS3_V2_WRONG_TP_REVIEW.csv` и `STAS3_V2_REPORT_RU.md`.
5. Boundary:
   код Stas3 V2 еще не реализован; ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-09T08:47:30Z] STAS3 | REBUILD FROM LATEST STAS2 | READY
1. Request:
   пользователь обновил Stas2-графики и попросил логично пересобрать Stas3 поверх нового Stas2.
2. Source:
   `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138`.
3. Command:
   `.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-08 -EndDay 2026-05-12 -RunLabel stas3_20260508_20260512_from_stas2_short_labels_v1 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260508_20260512_short_labels_v1_20260709_083138 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50`.
4. Final run:
   `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260508_20260512_from_stas2_short_labels_v1_20260709_084730`.
5. Result:
   `214` rows, `0` skipped, days with entries `2026-05-10..2026-05-12`, `157` hit 1%, `93` reasonable TP, `89` mismatch к 1% TP, `46` noise, `9` fast clean, `68` late-pump dependent, `53` PNG, пустых PNG нет.
6. Validation:
   `py_compile PASS`, focused pytest `2/2 PASS`, workbook load PASS, source Stas2 path in all `214` rows matches latest run, `open_last_run.ps1 -Open browse -NoOpen` points to new browse folder, no lingering project `python.exe`.
7. Note:
   Stas2 `WAVE/SHORT` ledger tables are not yet joined into per-entry Stas3 columns. Current rebuild uses latest `STAS2_RECORDS.csv`; WAVE-context join is a possible next review-only step.
8. Boundary:
   post-entry audit only. ML/export/training, Optuna, scorer, target-lock and API were not launched.

## 2026-07-09 STAS2 Short Strong Wave Labels

Сделано: исправлен визуальный пропуск процента в коротких сильных WAVE-блоках. Теперь confirmed WAVE с видимым ходом `>= 1%` и длительностью `>= 5m` получает компактную подпись процента, даже если блок короче обычного порога `15m`.

Артефакты: финальный run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138`. Проверочный пример: `W38 LONG 2026-05-12 12:32-12:40`, `8m`, `1.336303%`.

Проверки: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный run `2026-05-08..2026-05-12`, `openpyxl` load workbook, проверка PNG non-empty.

Ограничение: менялась только подпись на PNG. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## 2026-07-09 STAS2 Continuous Wave Ledger

Сделано: `WAVE` отвязана от UTC-дня. Добавлен глобальный ledger волн `STAS2_CONTINUOUS_WAVES.csv`, а `STAS2_MACRO_WAVES.csv` теперь хранит дневные срезы этих волн для overview. Если волна идет через `00:00`, на первом дне ставится `carry_to_next`, на следующем `carry_from_prev`, общий ключ `continuous_wave_id` сохраняет связь.

Артефакты: финальный run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`; новый CSV `STAS2_CONTINUOUS_WAVES.csv`; Excel-лист `Continuous waves`; обновленный лист `Macro waves`.

Итог: `214` entry rows, `29` continuous rows = `27` waves + `2` gaps, `31` day-slice rows = `29` wave slices + `2` gap slices, `4` carry-среза через день, `80` PNG, `0` пустых PNG, `0` missing sources.

Проверки: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный run `2026-05-10..2026-05-12`, `openpyxl` load workbook, проверка PNG non-empty.

Ограничение: continuous-wave остается review/hindsight слоем. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## 2026-07-09 STAS2 Macro Wave GAP Segments

Сделано: по замечанию пользователя исправлены пропуски в строке `WAVE` на дневном overview. Добавлены серые `GAP`-сегменты с процентом диапазона для непокрытых участков дня; подтвержденные WAVE-блоки и Stas1-точки не изменялись.

Артефакты: финальный run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_gap_segments_v1_20260709_073810`; обновленный `STAS2_MACRO_WAVES.csv`; Excel-лист `Macro waves`; дневные `*_STAS2_MACRO_WAVES.csv`.

Итог: `214` entry rows, `34` macro-wave review rows = `28` WAVE + `6` GAP, `80` PNG, `0` пустых PNG, `0` missing sources. Для `2026-05-10` добавлены `GAP01 0.78%` и `GAP02 0.57%`.

Проверки: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный run `2026-05-10..2026-05-12`, `openpyxl` load workbook, проверка PNG non-empty.

Ограничение: `GAP/WAVE` остается review/hindsight слоем. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## 2026-07-09 STAS2 SHORT And Macro Wave Review

Сделано: в `src/mlbotnav/visual_entry_stas2_market_phase_review.py` добавлены `SHORT` по закрытым часам и `WAVE` по переменным дневным swing-блокам. Stas1 не изменялся. В overview теперь есть строки `Фон`, `LONG`, `SHORT`, `WAVE`, затем объем; входные точки остаются как в Stas1 без текстового шума.

Артефакты: финальный run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_short_macro_wave_v1_20260709_064759`; новый CSV `STAS2_MACRO_WAVES.csv`; Excel-лист `Macro waves`; дневные `*_STAS2_MACRO_WAVES.csv`.

Итог: `417` entry rows, `144` hourly rows, `34` macro-wave rows, `6` дневных overview, `156` PNG, `0` пустых PNG, `0` missing sources. Для `2026-05-04` найдено `6` macro-wave блоков.

Проверки: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный run `2026-05-04..2026-05-09`, `openpyxl` load workbook, проверка PNG non-empty.

Ограничение: `macro_wave_*` является review/hindsight слоем. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## 2026-07-06 STAS3 Percent Ladder Review

Сделано: по новому прямому запросу `Стас3` реализован отдельный post-entry audit-контур `STAS3_PERCENT_LADDER_REVIEW`. Добавлены wrapper-команды, README, движок `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py` и тест `tests/test_visual_entry_stas3_percent_ladder_review.py`.

Контрольный run: `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260502_20260503_percent_ladder_v0_20260706_180559`.

Итог: `110` строк, `110` hit 1% в `48h`, `2` fast clean, `90` late-pump dependent, `0` missing OHLCV, workbook читается, CSV с BOM, `24` PNG и `0` пустых PNG.

Проверки: `py_compile`, `pytest tests/test_visual_entry_stas3_percent_ladder_review.py -q`, полный Stas3 run, `openpyxl` load workbook, CSV BOM, PNG non-empty, `open_last_run.ps1 -Open browse -NoOpen`, повторная проверка хвостов `python.exe` чистая.

Ограничение: Stas3 является post-entry audit. ML/export/training, Optuna, scorer, target-lock и API не запускались и запрещены без отдельного approval.

## 2026-07-06 STAS3 Separate Chat Decision

Сделано: зафиксировано решение пользователя делать Stas3 в другом чате. Текущий чат оставляет Stas2 закрытым и не начинает percent ladder / entry-TP validation.

Ограничение: в этом чате не запускать Stas3 post-entry расчеты, ML/export/training, Optuna, scorer, target-lock или API без нового прямого запроса.

## 2026-07-06 STAS2 Closed For STAS3

Сделано: после сверки с ТЗ и пользовательского подтверждения Stas2 зафиксирован как закрытый этап `STAS2_CLOSED_FOR_STAS3_NO_ML_NO_OPTUNA`. Stas2 принят как pre-entry слой фаз, сессий, day_type, `Фон`, `LONG`, `SETUP`, no-lookahead проверки и визуального no-label overview.

Артефакты: финальный visual-run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535`; широкий audit-run фаз/сессий `reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942`.

Следующий шаг: начинать Stas3 отдельным слоем percent ladder / entry-TP validation: MFE/MAE, достижимый процент, time-to-target, drawdown и 5m post-entry blocks. Не переносить эти post-entry поля обратно в Stas2.

Ограничение: ML/export/training, Optuna, scorer, target-lock и API не запускались и остаются запрещены без отдельного approval.

## 2026-07-01 Git Remote Push MLbotNav

Сделано: настроен локальный Git author `Stanislav1567 <Stanislav1567@users.noreply.github.com>`, добавлен remote `origin=https://github.com/Stanislav1567/MLbotNav.git`, создан initial commit `e178c49` и выполнен `git push -u origin main`.

Проверки: `git status --short --branch` после push показал чистое состояние `main...origin/main`; `git remote -v` показывает fetch/push на GitHub URL.

Ограничение: `gh` CLI не установлен, push выполнен обычным Git через доступный Git Credential Manager.

## 2026-07-01 Git Init MLbotNav

Сделано: создан локальный Git-репозиторий в `C:\Users\007\Desktop\MLbotNav`, ветка переименована в `main`. Расширен `.gitignore`, чтобы исключить секреты, окружение, данные, модели, отчеты, логи, packs, tmp, offload/locked tmp и backup-файлы. `.env.example` очищен от локального пользовательского пути.

Проверки: `git check-ignore` подтвердил игнор `.env`, `.venv`, `data`, `reports`, `models`, `packs`, `_codex_offload_20260530` и backup-файлов; после staging в индексе `646` файлов / `11.12 MB`; backup-файлы не staged; поиск явных токенов форматов `sk-*`, `ghp_*`, `github_pat_*`, `AIza*` в неигнорируемой части ничего не нашел.

Ограничение: коммит и push не выполнены, потому что не заданы `user.name`/`user.email` и нет remote URL.

## 2026-07-01 Codex Agent Launch Kit MLbotNav

Сделано: добавлены прямые launcher-файлы для `C:\Users\007\Desktop\MLbotNav` в `C:\Users\007\Desktop\Codex Agent`: `Start MLbotNav Codex Agent.cmd`, `Start-MLbotNav-Codex-Agent.ps1`, `Resume MLbotNav Codex Agent.cmd`, `Resume-MLbotNav-Codex-Agent.ps1`; обновлен `README.txt` лаунчера. Проектный `AGENTS.md` уже был на месте и не менялся.

Проверки: `codex --version` показал `codex-cli 0.142.5`; `codex login status` показал вход через ChatGPT; PowerShell-парсер подтвердил синтаксис новых `.ps1`; `codex resume --help` подтвердил наличие `-C`; `codex doctor` завершился без fail, с предупреждениями по старой истории Codex и отсутствию `.git` в проекте.

Ограничение: проект не является Git-репозиторием. `git init` не запускался, требуется отдельное решение пользователя.

## 2026-06-02
1. Restored active launch truth after forward validation:
   current status is `NO_GO`, freeze remains ON.
2. Created global launch audit:
   `docs/OPTUNA_GLOBAL_LAUNCH_AUDIT_2026-06-02_RU.md`.
3. Fixed V3 Checkpoint A:
   windows `W1-W3`, hypotheses `A-H1/A-H2/A-H3`.
4. Added repeatable runner:
   `run_optuna_v3_package_a.ps1`.
5. Ran V3 `Package A long_only`:
   `9/9` slot-window runs, `candidate_count=0`.
6. Ran V3 `Package A short_only`:
   `9/9` slot-window runs, `candidate_count=0`.
7. Published unified `Package A triage`:
   `NO_CANDIDATE`.
8. Published package-level post-audit:
   `PASS`.
9. User requested managed project memory so new chats can continue without relying on chat history.
10. Created `AGENTS.md` and `docs/codex/*` memory files.

Next step:
Define exact `Package B` slots under V3, then run final bounded package.

## 2026-06-02 Full Catalog Scope Update
1. User clarified that Optuna work must continue even when no launch candidate appears.
2. Active scope expanded to full calibration catalog:
   block -> feature -> hypothesis, with parameter ranges walked from `min` to `max`.
3. Created catalog TZ:
   `docs/TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md`.
4. Created checkpoint:
   `reports/qa_gate/p2026_optuna_full_calibration_catalog_checkpoint_20260602T083509Z.json`.
5. Created catalog directories:
   `reports/optuna_catalog/positive`,
   `reports/optuna_catalog/negative`,
   `reports/optuna_catalog/neutral`,
   `reports/optuna_catalog/infra_fail`,
   `reports/optuna_catalog/top`,
   `reports/optuna_catalog/index`.

Next step:
Extend Package B runner into `3x3` catalog mode and emit positive/negative/neutral/infra_fail index records.

Post-sync checks:
1. JSON checkpoint parse: `PASS`.
2. Catalog directories exist.
3. `text_guard`: `PASS`, `reports/qa_gate/recovery_r5_text_guard_20260602T083823Z.json`.
4. `readiness`: `PASS`, freeze preserved, `reports/readiness/readiness_check_20260602T083822Z.json`.
5. `pip check`: `No broken requirements found.`
6. Audit artifact:
   `reports/qa_gate/p2027_optuna_full_calibration_catalog_post_sync_audit_20260602T083823Z.json`.

## 2026-06-02 1d-to-1d Smoke Strategy
1. User fixed the first practical catalog task:
   calibrate parameters on one closed 1d train window, then apply those calibrated parameters on the next closed 1d test window.
2. Purpose:
   quickly verify that the Optuna/APTuna calibration contour works штатно before broader medium/wide catalog execution.
3. Scope:
   feature/hypothesis wiring, min/max profile handling, parameter transfer, result classification, catalog index emission, and 9-worker/`3x3` readiness.
4. No runtime run was launched and readiness/freeze state was not changed.
5. Checkpoint:
   `reports/qa_gate/p2028_optuna_1d_to_1d_smoke_strategy_checkpoint_20260602T090943Z.json`.

Next step:
Prepare the read-only wiring inventory and the exact `1d -> 1d` smoke matrix/command set.

## 2026-06-02 Ordered Execution Roadmap
1. User requested the work to be written in strict order and fixed so the project does not drift.
2. Created roadmap checkpoint:
   `reports/qa_gate/p2029_optuna_ordered_execution_roadmap_checkpoint_20260602T091412Z.json`.
3. Current pointer:
   Step 1 - read-only wiring inventory.
4. Fixed route:
   Step 1 inventory -> Step 2 smoke matrix -> Step 3 preflight -> Step 4 long_only smoke -> Step 5 short_only smoke -> Step 6 smoke triage -> Step 7 medium -> Step 8 wide -> Step 9 ranking -> Step 10 forward -> Step 11 production decision boundary.
5. No runtime run was launched and readiness/freeze state was not changed.

## 2026-06-02 Step 1 Wiring Inventory
1. Completed Step 1 read-only wiring inventory.
2. Status: `PASS`.
3. Artifacts:
   1. `reports/optuna_catalog/index/p2030_step1_wiring_inventory_20260602T092159Z.json`
   2. `reports/qa_gate/p2030_step1_wiring_inventory_checkpoint_20260602T092159Z.json`
4. Summary:
   1. enabled blocks: `6`;
   2. matrix feature rows: `68`;
   3. tunable feature rows: `56`;
   4. tunable hypotheses: `20`;
   5. linked profiles: `27/27`;
   6. profile issues: `0`.
5. Long/short hypothesis eligibility:
   1. `both=16`;
   2. `long_only=3`;
   3. `short_only=1`.
6. Current pointer moved to Step 2:
   exact `1d -> 1d` smoke matrix and command set.

Post-sync checks:
1. inventory JSON parse: `PASS`.
2. checkpoint JSON parse: `PASS`.
3. `text_guard`: `PASS`, `reports/qa_gate/recovery_r5_text_guard_20260602T092502Z.json`.
4. `readiness`: `PASS`, freeze preserved, `reports/readiness/readiness_check_20260602T092500Z.json`.
5. `pip check`: `No broken requirements found.`
6. Audit artifact:
   `reports/qa_gate/p2031_step1_wiring_inventory_post_sync_audit_20260602T092502Z.json`.

## 2026-06-02 Step 2 1d-to-1d Smoke Command Set
1. Completed Step 2 exact smoke matrix and command set.
2. Status: `PASS`.
3. Artifacts:
   1. `reports/optuna_catalog/index/p2032_step2_1d1d_smoke_command_set_20260602T092710Z.json`
   2. `reports/qa_gate/p2032_step2_1d1d_smoke_command_set_checkpoint_20260602T092710Z.json`
4. Fixed smoke window:
   train `2026-05-31`, test `2026-06-01`.
5. Fixed matrix/preset:
   `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=narrow`, `ForceProfileEdgeCoverage=on`.
6. Fixed resource profile:
   `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`, `OptunaTrials=60`, `OptunaTimeoutSec=300`.
7. Added CLI forwarding for calibration preset/edge coverage through:
   1. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`
   2. `APTuna/run_optuna_1d1d_stagec.ps1`
   3. `src/mlbotnav/adaptive_auto_train.py`
8. Verification:
   1. Python compileall for `adaptive_auto_train.py`: `PASS`.
   2. long_only dry-run: `PASS`, child command includes `--calibration-grid-preset narrow`.
   3. short_only dry-run: `PASS`, child command includes `--calibration-grid-preset narrow`.
9. Current pointer moved to Step 3:
   smoke preflight.

Post-sync checks:
1. command set JSON parse: `PASS`.
2. checkpoint JSON parse: `PASS`.
3. `text_guard`: `PASS`, `reports/qa_gate/recovery_r5_text_guard_20260602T093017Z.json`.
4. `readiness`: `PASS`, freeze preserved, `reports/readiness/readiness_check_20260602T093016Z.json`.
5. `pip check`: `No broken requirements found.`
6. Audit artifact:
   `reports/qa_gate/p2033_step2_smoke_command_set_post_sync_audit_20260602T093017Z.json`.

## 2026-06-02 Step 3 Smoke Preflight
1. Completed Step 3 smoke preflight.
2. Status: `PASS`.
3. Artifact:
   `reports/qa_gate/p2034_step3_smoke_preflight_20260602T093214Z.json`.
4. Checks: Python venv, matrix compile, long/short narrow compile, catalog dirs, storage resolution, readiness boundary.
5. Current pointer moved to Step 4: long_only `1d -> 1d` smoke.

## 2026-06-02 Step 4 Long-only Smoke
1. Ran long_only `1d -> 1d` smoke using P2032 command set.
2. Runtime status: `OK`, workers `3/3` exit_code `0`.
3. Result classification: `NEUTRAL_NO_TRADE`.
4. Result: best worker `w3`, `oos_net_return_pct=0.0`, `oos_trades=0`.
5. Artifacts:
   1. `reports/optuna_catalog/neutral/p2035_step4_long_only_1d1d_smoke_neutral_20260602T093324Z.json`
   2. `reports/qa_gate/p2035_step4_long_only_1d1d_smoke_checkpoint_20260602T093324Z.json`
6. Readiness freeze preserved.

## 2026-06-02 Step 5 Short-only Smoke
1. Ran short_only `1d -> 1d` smoke using P2032 command set.
2. Runtime status: `OK`, workers `3/3` exit_code `0`.
3. Result classification: `PROVISIONAL_PLUS_GOAL_FAIL`, stored under neutral.
4. Result: best worker `w2`, `oos_net_return_pct=+0.2544418318741748`, `oos_trades=1`, but `goal_pass=false`.
5. Artifacts:
   1. `reports/optuna_catalog/neutral/p2036_step5_short_only_1d1d_smoke_provisional_plus_goal_fail_20260602T093604Z.json`
   2. `reports/qa_gate/p2036_step5_short_only_1d1d_smoke_checkpoint_20260602T093604Z.json`
6. Readiness freeze preserved.

## 2026-06-02 Step 6 Smoke Triage
1. Completed smoke triage.
2. Decision: `GO_TO_MEDIUM_WORK`.
3. Accepted positive candidates: `0`.
4. Provisional positive OOS branches: `1` (`short_only`, w2, `+0.2544%`, 1 trade, `goal_pass=false`).
5. Artifact:
   `reports/qa_gate/p2037_step6_1d1d_smoke_triage_20260602T093704Z.json`.
6. Current pointer moved to Step 7: medium work pass.

Post-sync checks:
1. P2034/P2035/P2036/P2037 JSON parse: `PASS`.
2. Python compileall for `adaptive_auto_train.py`: `PASS`.
3. `text_guard`: `PASS`, `reports/qa_gate/recovery_r5_text_guard_20260602T094006Z.json`.
4. `readiness`: `PASS`, freeze preserved, `reports/readiness/readiness_check_20260602T094005Z.json`.
5. `pip check`: `No broken requirements found.`
6. Audit artifact:
   `reports/qa_gate/p2038_step6_smoke_triage_post_sync_audit_20260602T094006Z.json`.

## 2026-06-02 Step 7 Medium Command Set
1. Completed Step 7 medium command set before runtime.
2. Status: `PASS`.
3. Artifacts:
   1. `reports/optuna_catalog/index/p2039_step7_medium_command_set_20260602T095335Z.json`
   2. `reports/qa_gate/p2039_step7_medium_command_set_checkpoint_20260602T095335Z.json`
4. Fixed profile:
   train `2026-05-31`, test `2026-06-01`, matrix `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=medium`, `ForceProfileEdgeCoverage=on`.
5. Resource profile:
   `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`, `OptunaTrials=120`, `OptunaTimeoutSec=600`.
6. Compile/dry-run:
   long_only `PASS`, short_only `PASS`; each child process receives 40 trials, 600 sec timeout, 3 threads, and 3 search workers.
7. Current pointer:
   Step 7 runtime - run medium long_only, then medium short_only, then triage.

## 2026-06-02 Step 7 Medium Runtime And Triage
1. Completed Step 7 medium runtime for long_only and short_only.
2. long_only:
   1. runtime status `OK`, workers `3/3`;
   2. result `NEGATIVE_GOAL_FAIL`;
   3. best OOS `-6.9497%`, trades `1`, `goal_pass=false`;
   4. artifact `reports/optuna_catalog/negative/p2040_step7_medium_long_only_negative_20260602T095814Z.json`.
3. short_only:
   1. runtime status `OK`, workers `3/3`;
   2. result `NEGATIVE_GOAL_FAIL`;
   3. best OOS `-0.6217%`, trades `1`, `goal_pass=false`;
   4. artifact `reports/optuna_catalog/negative/p2041_step7_medium_short_only_negative_20260602T100012Z.json`.
4. Step 7 triage:
   1. accepted positive candidates `0`;
   2. negative catalog entries `2`;
   3. decision `GO_TO_WIDE_BATTLE`;
   4. artifact `reports/qa_gate/p2042_step7_medium_triage_20260602T100020Z.json`.
5. Current pointer:
   Step 8 - wide battle pass.

Post-sync checks:
1. P2039/P2040/P2041/P2042 JSON parse: `PASS`.
2. Python compileall: `PASS`.
3. `text_guard`: `PASS`, `reports/qa_gate/recovery_r5_text_guard_20260602T100235Z.json`.
4. `readiness`: `PASS`, freeze preserved, `reports/readiness/readiness_check_20260602T100234Z.json`.
5. `pip check`: `No broken requirements found.`
6. Audit artifact:
   `reports/qa_gate/p2043_step7_medium_post_sync_audit_20260602T100235Z.json`.

## 2026-06-02 Step 8 Wide Command Set
1. Completed Step 8 wide command set before runtime.
2. Status: `PASS`.
3. Artifacts:
   1. `reports/optuna_catalog/index/p2044_step8_wide_command_set_20260602T100351Z.json`
   2. `reports/qa_gate/p2044_step8_wide_command_set_checkpoint_20260602T100351Z.json`
4. Fixed profile:
   train `2026-05-31`, test `2026-06-01`, matrix `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=wide`, `ForceProfileEdgeCoverage=on`.
5. Resource profile:
   `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`, `OptunaTrials=180`, `OptunaTimeoutSec=900`.
6. Compile/dry-run:
   long_only `PASS`, short_only `PASS`; each child process receives 60 trials, 900 sec timeout, 3 threads, and 3 search workers.
7. Current pointer:
   Step 8 runtime - run wide long_only, then wide short_only, then triage.

## 2026-06-02 Step 8 Wide Runtime, Step 9 Ranking, Step 10/11 Boundary
1. Step 8 wide runtime completed for long_only and short_only.
2. long_only:
   1. runtime status `OK`, workers `3/3`;
   2. result `NEGATIVE_GOAL_FAIL`;
   3. best OOS `-4.9783%`, trades `1`, `goal_pass=false`;
   4. artifact `reports/optuna_catalog/negative/p2045_step8_wide_long_only_negative_20260602T100559Z.json`.
3. short_only:
   1. runtime status `OK`, workers `3/3`;
   2. result `NEGATIVE_GOAL_FAIL`;
   3. best OOS `-0.2663%`, trades `2`, `goal_pass=false`;
   4. artifact `reports/optuna_catalog/negative/p2046_step8_wide_short_only_negative_20260602T100718Z.json`.
4. Step 8 triage:
   `GO_TO_CATALOG_RANKING`, artifact `reports/qa_gate/p2047_step8_wide_triage_20260602T100725Z.json`.
5. Step 9 ranking:
   positive `0`, neutral `2`, negative `4`, infra_fail `0`; decision `NO_FORWARD_CANDIDATE`.
   Artifact: `reports/optuna_catalog/index/p2048_step9_catalog_ranking_20260602T100735Z.json`.
6. Step 10/11 boundary:
   forward stability not runnable because `candidate_for_forward=0`; production/unfreeze blocked.
   Artifact: `reports/qa_gate/p2049_full_catalog_no_forward_boundary_20260602T100745Z.json`.

Post-sync checks:
1. P2044/P2045/P2046/P2047/P2048/P2049 JSON parse: `PASS`.
2. Python compileall: `PASS`.
3. `text_guard`: `PASS`, `reports/qa_gate/recovery_r5_text_guard_20260602T101019Z.json`.
4. `readiness`: `PASS`, freeze preserved, `reports/readiness/readiness_check_20260602T101018Z.json`.
5. `pip check`: `No broken requirements found.`
6. Audit artifact:
   `reports/qa_gate/p2050_full_catalog_closeout_post_sync_audit_20260602T101019Z.json`.

## 2026-06-02 Block-Level Catalog Cycle Setup
1. Opened new block-level catalog cycle after no forward candidate in full-matrix pass.
2. Generated 6 block-isolated matrices under:
   `configs/calibration_matrices/catalog_blocks/`.
3. Setup artifact:
   `reports/optuna_catalog/index/p2051_block_level_catalog_cycle_setup_20260602T101240Z.json`.
4. First executable block:
   block01 `price_volatility`.
5. Block01 narrow command set:
   1. status `PASS`;
   2. artifact `reports/optuna_catalog/index/p2052_block01_price_volatility_narrow_command_set_20260602T101347Z.json`;
   3. profile: 3x3 workers, total trials `60`, timeout `300`, grid `narrow`.
6. Current pointer:
   run block01 narrow long_only, then short_only, then triage.

## 2026-06-02 Block01 Price Volatility Closeout
1. Block01 `price_volatility` completed across narrow, medium, and wide grids.
2. Runtime status:
   all 6 runs completed `OK` with 3/3 workers.
3. Catalog totals:
   positive `0`, neutral `3`, negative `3`, infra_fail `0`.
4. Decision:
   `GO_TO_BLOCK02_TREND_MOMENTUM`.
5. Artifacts:
   1. `reports/qa_gate/p2063_block01_price_volatility_full_triage_20260602T102218Z.json`
   2. `reports/qa_gate/p2064_block01_price_volatility_post_sync_audit_20260602T102259Z.json`
6. Post-sync:
   JSON parse, compileall, text_guard, readiness, and pip check all `PASS`; freeze preserved.

## 2026-06-02 Block02 Trend Momentum Narrow
1. Block02 `trend_momentum` narrow command set completed:
   `reports/optuna_catalog/index/p2065_block02_trend_momentum_narrow_command_set_20260602T102420Z.json`.
2. Runtime:
   1. long_only `OK`, neutral no-trade, negative tradeful branch `-15.3557%`;
   2. short_only `OK`, negative best OOS `-41.4626%`, trades `15`.
3. Triage:
   positive `0`, neutral `1`, negative `1`, infra_fail `0`.
4. Decision:
   `GO_TO_BLOCK02_MEDIUM`.
5. Artifact:
   `reports/qa_gate/p2068_block02_trend_momentum_narrow_triage_20260602T102600Z.json`.

## 2026-06-02 Block02 Trend Momentum Closeout
1. Block02 `trend_momentum` completed across narrow, medium, and wide grids.
2. Runtime status:
   all 6 runs completed `OK` with 3/3 workers.
3. Catalog totals:
   positive `0`, neutral `3`, negative `3`, infra_fail `0`.
4. Decision:
   `GO_TO_BLOCK03_VOLUME_FLOW`.
5. Artifacts:
   1. `reports/qa_gate/p2076_block02_trend_momentum_full_triage_20260602T103215Z.json`
   2. `reports/qa_gate/p2077_block02_trend_momentum_post_sync_audit_20260602T103526Z.json`
6. Post-sync:
   JSON parse, compileall, text_guard, readiness, and pip check all `PASS`; freeze preserved.

## 2026-06-02 Block03 Volume Flow Narrow
1. Block03 `volume_flow` narrow command set completed:
   `reports/optuna_catalog/index/p2078_block03_volume_flow_narrow_command_set_20260602T103918Z.json`.
2. Runtime:
   1. long_only `OK`, positive candidate_for_forward, best OOS `+1.9186%`, trades `1`;
   2. short_only `OK`, negative, best OOS `-13.3138%`, trades `4`.
3. Triage totals:
   positive `1`, neutral `0`, negative `1`, infra_fail `0`, candidate_for_forward `1`.
4. Artifact:
   `reports/qa_gate/p2081_block03_volume_flow_narrow_triage_20260602T104055Z.json`.
5. Current pointer:
   block03 `volume_flow` medium command set.

## 2026-06-02 Block03 Volume Flow Closeout
1. Block03 `volume_flow` completed across narrow, medium, and wide grids.
2. Runtime status:
   all 6 runs completed `OK` with 3/3 workers.
3. Catalog totals:
   positive `1`, neutral `2`, negative `3`, infra_fail `0`, candidate_for_forward `1`.
4. Preserved positive candidate:
   `reports/optuna_catalog/positive/p2079_block03_volume_flow_narrow_long_only_positive_20260602T103932Z.json`.
5. Full triage:
   `reports/qa_gate/p2089_block03_volume_flow_full_triage_20260602T104655Z.json`.
6. Post-sync:
   `reports/qa_gate/p2090_block03_volume_flow_post_sync_audit_20260602T104830Z.json`, status `PASS`, freeze preserved.
7. Current pointer:
   block04 `density_profile` narrow command set.

## 2026-06-02 Block04 Density Profile Closeout
1. Block04 `density_profile` completed across narrow, medium, and wide grids.
2. Runtime status:
   all 6 runs completed `OK` with 3/3 workers.
3. Catalog totals:
   positive `0`, neutral `4`, negative `2`, infra_fail `0`, candidate_for_forward `0`.
4. Prior positive candidate preserved:
   `reports/optuna_catalog/positive/p2079_block03_volume_flow_narrow_long_only_positive_20260602T103932Z.json`.
5. Full triage:
   `reports/qa_gate/p2102_block04_density_profile_full_triage_20260602T105800Z.json`.
6. Post-sync:
   `reports/qa_gate/p2103_block04_density_profile_post_sync_audit_20260602T105853Z.json`, status `PASS`, freeze preserved.
7. Current pointer:
   block05 `structure_ta` narrow command set.

## 2026-06-02 Block05 Structure TA Closeout
1. Block05 `structure_ta` completed across narrow, medium, and wide grids.
2. Runtime status:
   all 6 runs completed `OK` with 3/3 workers.
3. Catalog totals:
   positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
4. Prior positive candidate preserved:
   `reports/optuna_catalog/positive/p2079_block03_volume_flow_narrow_long_only_positive_20260602T103932Z.json`.
5. Full triage:
   `reports/qa_gate/p2115_block05_structure_ta_full_triage_20260602T110710Z.json`.
6. Post-sync:
   `reports/qa_gate/p2116_block05_structure_ta_post_sync_audit_20260602T110808Z.json`, status `PASS`, freeze preserved.
7. Current pointer:
   block06 `pattern` narrow command set.

## 2026-06-02 Block06 Pattern And Block-Level Catalog Closeout
1. Block06 `pattern` completed across narrow, medium, and wide grids.
2. Block06 totals:
   positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
3. Full block-level ranking:
   positive `1`, neutral `18`, negative `17`, infra_fail `0`, candidate_for_forward `1`.
4. Accepted candidate:
   block03 `volume_flow`, `P2079`, `long_only`, narrow, OOS `+1.9186%`, trades `1`.
5. Artifacts:
   1. `reports/qa_gate/p2128_block06_pattern_full_triage_20260602T111625Z.json`
   2. `reports/optuna_catalog/index/p2130_block_level_catalog_ranking_20260602T111745Z.json`
   3. `reports/qa_gate/p2131_block_level_forward_boundary_20260602T111745Z.json`
   4. `reports/qa_gate/p2132_block_level_catalog_closeout_post_sync_audit_20260602T111822Z.json`
6. Boundary:
   production/unfreeze remains blocked; next step is exact F1/F2 forward stability command set.

## 2026-06-02 P2079 Forward Stability Command Set
1. P2133 command set prepared for block03 `volume_flow` candidate `P2079`.
2. Artifact:
   `reports/optuna_catalog/index/p2133_p2079_forward_stability_command_set_20260602T112708Z.json`.
3. Primary execution path:
   fixed-parameter replay using singleton grids from P2079 (`horizon=1`, `p_long=0.65`, `p_short=0.38`, `min_move=0.002`, `trend_filter=min_max_range_revert`).
4. Secondary execution path:
   block03 narrow Optuna contour with 3x3 process-pool profile.
5. Status:
   `BLOCKED_BY_DATA`; command syntax dry-run for 3x3 contour `PASS`.
6. Preflight:
   F1 `2026-06-01 -> 2026-06-02` failed because `2026-06-02` raw test data is absent and `2026-06-01` train is partial for WF rows.
   F2 `2026-06-02 -> 2026-06-03` failed because `2026-06-02` and `2026-06-03` raw data is absent.
7. Current pointer:
   `P2134` repeat F1/F2 preflight after closed raw days are available; production/unfreeze remains blocked.

## 2026-06-02 P2079 Forward Preflight Data Gate
1. P2134 repeated data/preflight check for candidate `P2079`.
2. Checkpoint:
   `reports/qa_gate/p2134_p2079_forward_preflight_data_gate_20260602T113136Z.json`.
3. Current UTC at check:
   `2026-06-02T11:31:36Z`.
4. Data snapshot:
   core max day `2026-05-31`, raw max day `2026-06-01`.
5. F1 preflight:
   `reports/qa_gate/preflight_window_20260602T113056Z.json`, `FAIL`.
6. F2 preflight:
   `reports/qa_gate/preflight_window_20260602T113105Z.json`, `FAIL`.
7. Current pointer:
   wait for closed raw `2026-06-02`, then repeat F1 preflight; F2 waits for closed raw `2026-06-03`. No runtime or production action is allowed before preflight `PASS`.

## 2026-06-02 P2079 Forward Data Ingest Route
1. P2135 fixed the safe data route after UTC close; no ingestion or runtime was launched.
2. Checkpoint:
   `reports/qa_gate/p2135_p2079_forward_data_ingest_route_20260602T113532Z.json`.
3. F1 route after `2026-06-03T00:00:00Z`:
   `$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ingest_day --date 2026-06-02 --symbol SOLUSDT --timeframes 1`.
4. After F1 ingest:
   repeat F1 preflight from `docs/codex/commands.md`.
5. F2 route waits until after `2026-06-04T00:00:00Z` for closed raw `2026-06-03`.

## 2026-06-02 P2079 Post-Close Heartbeat
1. P2136 fixed the app heartbeat for the next data gate continuation.
2. Automation id:
   `p2079-f1-data-gate-check`.
3. Scheduled time:
   `2026-06-03 05:05` Asia/Yekaterinburg, after `2026-06-03T00:00:00Z`.
4. Scope:
   verify UTC close, ingest closed raw `2026-06-02` only if needed, run F1 preflight only.
5. Explicit blocks:
   no fixed replay, no Optuna runtime, no production, no unfreeze unless F1 preflight returns `PASS`.

## 2026-06-02 P2137 Previous V3 TZ Pointer Recovery
1. User corrected the route: the previous TZ step was skipped.
2. Previous TZ found:
   `docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md`.
3. Required unclosed step from V3:
   after `Package A NO_CANDIDATE`, define exact `Package B` slot composition, then run bounded `Package B`.
4. Catalog overlay found:
   `docs/TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md`.
   It expands result preservation and min-to-max cataloging, but does not cancel V3 Package B.
5. Checkpoint:
   `reports/qa_gate/p2137_previous_tz_recovery_package_b_pointer_20260602T123736Z.json`.
6. Automation:
   heartbeat `p2079-f1-data-gate-check` paused so P2079 forward path does not auto-advance.
7. Current manual pointer:
   define exact V3 `Package B` slots/catalog command set before runtime.

## 2026-06-02 P2138 Previous V3 TZ Recovery Post-Sync Audit
1. Post-sync audit after pointer recovery passed.
2. Checkpoint:
   `reports/qa_gate/p2138_previous_tz_recovery_post_sync_audit_20260602T123949Z.json`.
3. Checks:
   1. `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260602T123937Z.json`;
   2. readiness `PASS`, freeze preserved, artifact `reports/readiness/readiness_check_20260602T123936Z.json`;
   3. `pip check PASS`.
4. Current manual pointer remains:
   exact V3 `Package B` slot definition.

## 2026-06-02 P2139 Timed Package B Step Chain
1. User requested date/time on every step and date/time in the TZ source.
2. Chain timestamp:
   UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`.
3. From TZ:
   `docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md`, section 7, `2026-06-02T06:52:50Z`.
4. Checkpoint:
   `reports/qa_gate/p2139_package_b_timed_step_chain_20260602T124520Z.json`.
5. Current step:
   Step 1 inventory of V3 Package A and old Package B artifacts; expected next artifact `P2140`.

## 2026-06-02 P2139 Independent Agent/Audit Cross-Check
1. User requested independent agent verification against audit because route looked suspect.
2. Agent:
   `Bernoulli / 019e8861-bdad-7a53-9e73-c9b313c518a2`.
3. Checkpoint:
   `reports/qa_gate/p2139_independent_agent_crosscheck_20260602T125117Z.json`.
4. Conclusion:
   route is correct with boundary: next step is read-only `P2140 inventory`, not Package B runtime or P2079 forward.
5. Risk:
   P2130/P2131/P2133 forward path exists from before recovery and can confuse the route, but P2137 later restored Package B pointer and demoted P2079 to preserved `candidate_for_forward`.

## 2026-06-02 P2140 V3 Package B Inventory
1. Step:
   P2140, Step 1.
2. Time:
   started UTC `2026-06-02T12:45:20Z`, completed UTC `2026-06-02T12:59:00Z`; local completed `2026-06-02 17:59:00 +05:00`.
3. Artifact:
   `reports/qa_gate/p2140_v3_package_b_inventory_20260602T125900Z.json`.
4. Result:
   `PASS`.
5. Findings:
   current V3 Package A is closed as `NO_CANDIDATE`; old Package B artifacts `P1995/P1996` and `P2005-P2007` are historical V2/strict references only; current V3 Package B exact slots/matrices/command set are not defined yet.
6. Next number:
   `P2141` exact V3 Package B slot definition. Runtime remains blocked.

## 2026-06-02 P2141 V3 Package B Exact Slots
1. Step:
   P2141, Step 2.
2. Time:
   started UTC `2026-06-02T12:59:47Z`, completed UTC `2026-06-02T13:00:00Z`; local completed `2026-06-02 18:00:00 +05:00`.
3. Artifact:
   `reports/qa_gate/p2141_v3_package_b_exact_slots_20260602T130000Z.json`.
4. Result:
   `PASS`.
5. Exact slots:
   B-H1 trend/momentum (`ema_stack_bull` long, `ema_cross_20_200` short), B-H2 range/reversion (`min_max_range_revert` both), B-H3 flow/absorption (`spread_pressure_and_delta_absorption` both).
6. Next number:
   `P2142` matrix slices and command-set/dry-run artifact only; runtime remains blocked.

## 2026-06-02 P2142 V3 Package B Matrix Slices And Command Set
1. Step:
   P2142, Step 3.
2. Time:
   started UTC `2026-06-02T13:02:00Z`, completed UTC `2026-06-02T13:05:59Z`; local completed `2026-06-02 18:05:59 +05:00`.
3. Artifact:
   `reports/qa_gate/p2142_v3_package_b_command_set_20260602T130559Z.json`.
4. Result:
   `PASS`.
5. Matrix slices:
   `configs/calibration_matrices/optuna_v3_package_b_bh1_long.yaml`, `configs/calibration_matrices/optuna_v3_package_b_bh1_short.yaml`, `configs/calibration_matrices/optuna_v3_package_b_bh2.yaml`, `configs/calibration_matrices/optuna_v3_package_b_bh3.yaml`.
6. Dry-run/preflight:
   18 exact commands emitted; `18/18 PASS`; no runtime launched in this step.
7. Next number:
   `P2143` Package B `long_only` runtime only; `short_only`, P2079 forward, production, and unfreeze remain blocked.

## 2026-06-02 P2142 Post-Sync Checks
1. Artifact:
   `reports/qa_gate/p2142_v3_package_b_post_sync_audit_20260602T130840Z.json`.
2. Checks:
   `text_guard PASS`, readiness freeze preserved (`project_ready=false`, `enforce_freeze=true`), `pip check PASS`, P2142 JSON/YAML parse `PASS`.
3. Boundary:
   next number remains `P2143` Package B `long_only` runtime only.

## 2026-06-02 P2143 V3 Package B Long Only Runtime
1. Step:
   P2143, Step 4.
2. Time:
   started UTC `2026-06-02T13:10:35Z`, completed UTC `2026-06-02T13:15:35Z`; local completed `2026-06-02 18:15:35 +05:00`.
3. Runtime artifact:
   `reports/qa_gate/p2143_v3_package_b_long_only_summary_20260602T131035Z.json`.
4. Runs:
   `reports/qa_gate/p2143_v3_package_b_long_only_runs_20260602T131035Z.jsonl`.
5. Catalog artifact:
   `reports/optuna_catalog/neutral/p2143_v3_package_b_long_only_neutral_20260602T131535Z.json`.
6. Result:
   runtime `9/9 PASS`; catalog class `neutral`; accepted positive candidates `0`; best tradeful OOS `-1.6687%`.
7. Next number:
   `P2144` Package B `short_only` runtime only.

## 2026-06-02 P2143 Post-Sync Checks
1. Artifact:
   `reports/qa_gate/p2143_v3_package_b_post_sync_audit_20260602T131847Z.json`.
2. Checks:
   `text_guard PASS`, readiness freeze preserved (`project_ready=false`, `enforce_freeze=true`), `pip check PASS`, P2143 JSON/JSONL parse `PASS`.
3. Boundary:
   next number remains `P2144` Package B `short_only` runtime only.

## 2026-06-02 P2144 V3 Package B Short Only Runtime
1. Step:
   P2144, Step 5.
2. Time:
   started UTC `2026-06-02T13:20:20Z`, completed UTC `2026-06-02T13:24:20Z`; local completed `2026-06-02 18:24:20 +05:00`.
3. Runtime artifact:
   `reports/qa_gate/p2144_v3_package_b_short_only_summary_20260602T132020Z.json`.
4. Runs:
   `reports/qa_gate/p2144_v3_package_b_short_only_runs_20260602T132020Z.jsonl`.
5. Catalog artifact:
   `reports/optuna_catalog/neutral/p2144_v3_package_b_short_only_neutral_20260602T132420Z.json`.
6. Result:
   runtime `9/9 PASS`; catalog class `neutral`; accepted positive candidates `0`; best tradeful OOS `-1.6689%`.
7. Next number:
   `P2145` unified Package B triage only.

## 2026-06-02 P2144 Post-Sync Checks
1. Artifact:
   `reports/qa_gate/p2144_v3_package_b_post_sync_audit_20260602T132701Z.json`.
2. Checks:
   `text_guard PASS`, readiness freeze preserved (`project_ready=false`, `enforce_freeze=true`), `pip check PASS`, P2144 JSON/JSONL parse `PASS`.
3. Boundary:
   next number remains `P2145` unified Package B triage only.

## 2026-06-02 P2145 V3 Package B Unified Triage
1. Step:
   P2145, Step 6.
2. Time:
   started UTC `2026-06-02T13:28:00Z`, completed UTC `2026-06-02T13:28:30Z`; local completed `2026-06-02 18:28:30 +05:00`.
3. Artifact:
   `reports/qa_gate/p2145_v3_package_b_unified_triage_20260602T132830Z.json`.
4. Result:
   `NO_CANDIDATE`; positive `0`, neutral `18`, negative `0`, infra_fail `0`, candidate_for_forward `0`.
5. Next number:
   `P2146` Package B post-sync audit/docs sync only.

## 2026-06-02 P2146 V3 Package B Post-Sync Audit
1. Step:
   P2146, Step 7.
2. Time:
   started UTC `2026-06-02T13:30:00Z`, completed UTC `2026-06-02T13:30:21Z`; local completed `2026-06-02 18:30:21 +05:00`.
3. Artifact:
   `reports/qa_gate/p2146_v3_package_b_post_sync_audit_20260602T133021Z.json`.
4. Checks:
   `text_guard PASS`, readiness freeze preserved (`project_ready=false`, `enforce_freeze=true`), `pip check PASS`, P2145 artifact parse `PASS`.
5. Next number:
   `P2147` transition decision after Package B closeout.

## 2026-06-02 P2147 V3 Package B Closeout Transition
1. Step:
   P2147, Step 8.
2. Time:
   started UTC `2026-06-02T13:33:00Z`, completed UTC `2026-06-02T13:33:30Z`; local completed `2026-06-02 18:33:30 +05:00`.
3. Artifact:
   `reports/qa_gate/p2147_v3_package_b_closeout_transition_20260602T133330Z.json`.
4. Decision:
   `GO_TO_FINAL_V3_NO_GO_DECISION_PACKAGE`.
5. Boundary:
   no Package B runtime remains; P2079 forward, production, and unfreeze remain blocked.

## 2026-06-02 P2148 V3 Final NO_GO Decision
1. Step:
   P2148.
2. Time:
   started UTC `2026-06-02T13:35:30Z`, completed UTC `2026-06-02T13:36:00Z`; local completed `2026-06-02 18:36:00 +05:00`.
3. Artifact:
   `reports/qa_gate/p2148_v3_final_no_go_decision_20260602T133600Z.json`.
4. Decision:
   final launch `NO_GO`; no production-ready candidate; launch and unfreeze blocked.
5. Next number:
   `P2149` final V3 `NO_GO` post-sync audit.

## 2026-06-02 P2149 V3 Final NO_GO Post-Sync Audit
1. Step:
   P2149.
2. Time:
   started UTC `2026-06-02T13:38:20Z`, completed UTC `2026-06-02T13:38:45Z`; local completed `2026-06-02 18:38:45 +05:00`.
3. Artifact:
   `reports/qa_gate/p2149_v3_final_no_go_post_sync_audit_20260602T133845Z.json`.
4. Checks:
   `text_guard PASS`, readiness freeze preserved (`project_ready=false`, `enforce_freeze=true`), `pip check PASS`, P2148 artifact parse `PASS`.
5. Boundary:
   V3 chain closed as `NO_GO`; no runtime, forward, production, or unfreeze is allowed from this chain.

## 2026-06-02 P2150 Post-V3 Catalog/Forward Boundary
1. Step:
   P2150.
2. Time:
   started UTC `2026-06-02T13:41:20Z`, completed UTC `2026-06-02T13:41:50Z`; local completed `2026-06-02 18:41:50 +05:00`.
3. Artifact:
   `reports/qa_gate/p2150_post_v3_catalog_forward_boundary_20260602T134150Z.json`.
4. Result:
   `ROUTE_SELECTED_WAIT_UTC_CLOSE`; route selected to P2079 F1 data gate after `2026-06-03T00:00:00Z`.
5. Boundary:
   no ingest, preflight, runtime, production, or unfreeze now; next number `P2151` is time-blocked.

## 2026-06-02 P2151 P2079 F1 Data Gate Pre-Close Check
1. Step:
   P2151.
2. Time:
   started UTC `2026-06-02T14:17:00Z`, completed UTC `2026-06-02T14:17:11Z`; local completed `2026-06-02 19:17:11 +05:00`.
3. Artifact:
   `reports/qa_gate/p2151_p2079_f1_data_gate_preclose_check_20260602T141711Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2152` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.

## 2026-06-02 P2152 P2079 F1 UTC-Close Recheck
1. Step:
   P2152.
2. Time:
   started UTC `2026-06-02T14:20:30Z`, completed UTC `2026-06-02T14:20:42Z`; local completed `2026-06-02 19:20:42 +05:00`.
3. Artifact:
   `reports/qa_gate/p2152_p2079_f1_data_gate_utc_close_recheck_20260602T142042Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2153` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.

## 2026-06-02 P2153 P2079 F1 UTC-Close Recheck
1. Step:
   P2153.
2. Time:
   started UTC `2026-06-02T14:23:10Z`, completed UTC `2026-06-02T14:23:19Z`; local completed `2026-06-02 19:23:19 +05:00`.
3. Artifact:
   `reports/qa_gate/p2153_p2079_f1_data_gate_utc_close_recheck_20260602T142319Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2154` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.

## 2026-06-02 P2154 P2079 F1 UTC-Close Recheck
1. Step:
   P2154.
2. Time:
   started UTC `2026-06-02T14:25:45Z`, completed UTC `2026-06-02T14:25:53Z`; local completed `2026-06-02 19:25:53 +05:00`.
3. Artifact:
   `reports/qa_gate/p2154_p2079_f1_data_gate_utc_close_recheck_20260602T142553Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2155` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.

## 2026-06-02 P2155 P2079 F1 UTC-Close Recheck
1. Step:
   P2155.
2. Time:
   started UTC `2026-06-02T14:29:02Z`, completed UTC `2026-06-02T14:29:20Z`; local completed `2026-06-02 19:29:20 +05:00`.
3. Artifact:
   `reports/qa_gate/p2155_p2079_f1_data_gate_utc_close_recheck_20260602T142920Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2156` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143136Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T143136Z.json`), `pip check PASS`, P2155 artifact parse `PASS`.

## 2026-06-02 P2156 P2079 F1 UTC-Close Recheck
1. Step:
   P2156.
2. Time:
   started UTC `2026-06-02T14:33:00Z`, completed UTC `2026-06-02T14:33:08Z`; local completed `2026-06-02 19:33:08 +05:00`.
3. Artifact:
   `reports/qa_gate/p2156_p2079_f1_data_gate_utc_close_recheck_20260602T143308Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2157` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143445Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T143445Z.json`), `pip check PASS`, P2156 artifact parse `PASS`.

## 2026-06-02 P2157 P2079 F1 UTC-Close Recheck
1. Step:
   P2157.
2. Time:
   started UTC `2026-06-02T14:36:20Z`, completed UTC `2026-06-02T14:36:25Z`; local completed `2026-06-02 19:36:25 +05:00`.
3. Artifact:
   `reports/qa_gate/p2157_p2079_f1_data_gate_utc_close_recheck_20260602T143625Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2158` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143926Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T143925Z.json`), `pip check PASS`, P2157 artifact parse `PASS`.

## 2026-06-02 P2158 P2079 F1 UTC-Close Recheck
1. Step:
   P2158.
2. Time:
   started UTC `2026-06-02T14:40:23Z`, completed UTC `2026-06-02T14:40:30Z`; local completed `2026-06-02 19:40:30 +05:00`.
3. Artifact:
   `reports/qa_gate/p2158_p2079_f1_data_gate_utc_close_recheck_20260602T144030Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2159` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144209Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T144207Z.json`), `pip check PASS`, P2158 artifact parse `PASS`.

## 2026-06-02 P2159 P2079 F1 UTC-Close Recheck
1. Step:
   P2159.
2. Time:
   started UTC `2026-06-02T14:43:10Z`, completed UTC `2026-06-02T14:43:17Z`; local completed `2026-06-02 19:43:17 +05:00`.
3. Artifact:
   `reports/qa_gate/p2159_p2079_f1_data_gate_utc_close_recheck_20260602T144317Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2160` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144457Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T144456Z.json`), `pip check PASS`, P2159 artifact parse `PASS`.

## 2026-06-02 P2160 P2079 F1 UTC-Close Recheck
1. Step:
   P2160.
2. Time:
   started UTC `2026-06-02T14:46:00Z`, completed UTC `2026-06-02T14:46:07Z`; local completed `2026-06-02 19:46:07 +05:00`.
3. Artifact:
   `reports/qa_gate/p2160_p2079_f1_data_gate_utc_close_recheck_20260602T144607Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2161` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144742Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T144742Z.json`), `pip check PASS`, P2160 artifact parse `PASS`.

## 2026-06-02 P2161 P2079 F1 UTC-Close Recheck
1. Step:
   P2161.
2. Time:
   started UTC `2026-06-02T14:49:38Z`, completed UTC `2026-06-02T14:49:43Z`; local completed `2026-06-02 19:49:43 +05:00`.
3. Artifact:
   `reports/qa_gate/p2161_p2079_f1_data_gate_utc_close_recheck_20260602T144943Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2162` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145122Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T145121Z.json`), `pip check PASS`, P2161 artifact parse `PASS`.

## 2026-06-02 P2162 P2079 F1 UTC-Close Recheck
1. Step:
   P2162.
2. Time:
   started UTC `2026-06-02T14:52:21Z`, completed UTC `2026-06-02T14:52:28Z`; local completed `2026-06-02 19:52:28 +05:00`.
3. Artifact:
   `reports/qa_gate/p2162_p2079_f1_data_gate_utc_close_recheck_20260602T145228Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2163` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145406Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T145405Z.json`), `pip check PASS`, P2162 artifact parse `PASS`.

## 2026-06-02 P2163 P2079 F1 UTC-Close Recheck
1. Step:
   P2163.
2. Time:
   started UTC `2026-06-02T14:55:15Z`, completed UTC `2026-06-02T14:55:22Z`; local completed `2026-06-02 19:55:22 +05:00`.
3. Artifact:
   `reports/qa_gate/p2163_p2079_f1_data_gate_utc_close_recheck_20260602T145522Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2164` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145702Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T145701Z.json`), `pip check PASS`, P2163 artifact parse `PASS`.

## 2026-06-02 P2164 P2079 F1 UTC-Close Recheck
1. Step:
   P2164.
2. Time:
   started UTC `2026-06-02T15:00:19Z`, completed UTC `2026-06-02T15:00:19Z`; local completed `2026-06-02 20:00:19 +05:00`.
3. Artifact:
   `reports/qa_gate/p2164_p2079_f1_data_gate_utc_close_recheck_20260602T150019Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2165` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150225Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T150225Z.json`), `pip check PASS`, P2164 artifact parse `PASS`.

## 2026-06-02 P2165 P2079 F1 UTC-Close Recheck
1. Step:
   P2165.
2. Time:
   started UTC `2026-06-02T15:04:36Z`, completed UTC `2026-06-02T15:04:36Z`; local completed `2026-06-02 20:04:36 +05:00`.
3. Artifact:
   `reports/qa_gate/p2165_p2079_f1_data_gate_utc_close_recheck_20260602T150436Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2166` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150617Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T150617Z.json`), `pip check PASS`, P2165 artifact parse `PASS`.

## 2026-06-02 P2166 P2079 F1 UTC-Close Recheck
1. Step:
   P2166.
2. Time:
   started UTC `2026-06-02T15:07:32Z`, completed UTC `2026-06-02T15:07:32Z`; local completed `2026-06-02 20:07:32 +05:00`.
3. Artifact:
   `reports/qa_gate/p2166_p2079_f1_data_gate_utc_close_recheck_20260602T150732Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2167` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150915Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T150915Z.json`), `pip check PASS`, P2166 artifact parse `PASS`.

## 2026-06-02 P2167 P2079 F1 UTC-Close Recheck
1. Step:
   P2167.
2. Time:
   started UTC `2026-06-02T15:10:30Z`, completed UTC `2026-06-02T15:10:30Z`; local completed `2026-06-02 20:10:30 +05:00`.
3. Artifact:
   `reports/qa_gate/p2167_p2079_f1_data_gate_utc_close_recheck_20260602T151030Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2168` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151314Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T151314Z.json`), `pip check PASS`, P2167 artifact parse `PASS`.

## 2026-06-02 P2168 P2079 F1 UTC-Close Recheck
1. Step:
   P2168.
2. Time:
   started UTC `2026-06-02T15:15:32Z`, completed UTC `2026-06-02T15:15:32Z`; local completed `2026-06-02 20:15:32 +05:00`.
3. Artifact:
   `reports/qa_gate/p2168_p2079_f1_data_gate_utc_close_recheck_20260602T151532Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2169` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151714Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T151713Z.json`), `pip check PASS`, P2168 artifact parse `PASS`.

## 2026-06-02 P2169 P2079 F1 UTC-Close Recheck
1. Step:
   P2169.
2. Time:
   started UTC `2026-06-02T15:18:26Z`, completed UTC `2026-06-02T15:18:26Z`; local completed `2026-06-02 20:18:26 +05:00`.
3. Artifact:
   `reports/qa_gate/p2169_p2079_f1_data_gate_utc_close_recheck_20260602T151826Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2170` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152005Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T152004Z.json`), `pip check PASS`, P2169 artifact parse `PASS`.

## 2026-06-02 P2170 P2079 F1 UTC-Close Recheck
1. Step:
   P2170.
2. Time:
   started UTC `2026-06-02T15:21:20Z`, completed UTC `2026-06-02T15:21:20Z`; local completed `2026-06-02 20:21:20 +05:00`.
3. Artifact:
   `reports/qa_gate/p2170_p2079_f1_data_gate_utc_close_recheck_20260602T152120Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2171` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152306Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T152305Z.json`), `pip check PASS`, P2170 artifact parse `PASS`.

## 2026-06-02 P2171 P2079 F1 UTC-Close Recheck
1. Step:
   P2171.
2. Time:
   started UTC `2026-06-02T15:25:59Z`, completed UTC `2026-06-02T15:25:59Z`; local completed `2026-06-02 20:25:59 +05:00`.
3. Artifact:
   `reports/qa_gate/p2171_p2079_f1_data_gate_utc_close_recheck_20260602T152559Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2172` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152826Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T152825Z.json`), `pip check PASS`, P2171 artifact parse `PASS`.

## 2026-06-02 P2172 P2079 F1 UTC-Close Recheck
1. Step:
   P2172.
2. Time:
   started UTC `2026-06-02T15:29:40Z`, completed UTC `2026-06-02T15:29:40Z`; local completed `2026-06-02 20:29:40 +05:00`.
3. Artifact:
   `reports/qa_gate/p2172_p2079_f1_data_gate_utc_close_recheck_20260602T152940Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2173` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153127Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T153126Z.json`), `pip check PASS`, P2172 artifact parse `PASS`.

## 2026-06-02 P2173 P2079 F1 UTC-Close Recheck
1. Step:
   P2173.
2. Time:
   started UTC `2026-06-02T15:32:42Z`, completed UTC `2026-06-02T15:32:42Z`; local completed `2026-06-02 20:32:42 +05:00`.
3. Artifact:
   `reports/qa_gate/p2173_p2079_f1_data_gate_utc_close_recheck_20260602T153242Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2174` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153429Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T153428Z.json`), `pip check PASS`, P2173 artifact parse `PASS`.

## 2026-06-02 P2174 P2079 F1 UTC-Close Recheck
1. Step:
   P2174.
2. Time:
   started UTC `2026-06-02T15:35:32Z`, completed UTC `2026-06-02T15:35:32Z`; local completed `2026-06-02 20:35:32 +05:00`.
3. Artifact:
   `reports/qa_gate/p2174_p2079_f1_data_gate_utc_close_recheck_20260602T153532Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2175` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153717Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T153716Z.json`), `pip check PASS`, P2174 artifact parse `PASS`.

## 2026-06-02 P2175 P2079 F1 UTC-Close Recheck
1. Step:
   P2175.
2. Time:
   started UTC `2026-06-02T15:38:21Z`, completed UTC `2026-06-02T15:38:21Z`; local completed `2026-06-02 20:38:21 +05:00`.
3. Artifact:
   `reports/qa_gate/p2175_p2079_f1_data_gate_utc_close_recheck_20260602T153821Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2176` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154009Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T154008Z.json`), `pip check PASS`, P2175 artifact parse `PASS`.

## 2026-06-02 P2176 P2079 F1 UTC-Close Recheck
1. Step:
   P2176.
2. Time:
   started UTC `2026-06-02T15:41:14Z`, completed UTC `2026-06-02T15:41:14Z`; local completed `2026-06-02 20:41:14 +05:00`.
3. Artifact:
   `reports/qa_gate/p2176_p2079_f1_data_gate_utc_close_recheck_20260602T154114Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2177` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154333Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T154333Z.json`), `pip check PASS`, P2176 artifact parse `PASS`.

## 2026-06-02 P2177 P2079 F1 UTC-Close Recheck
1. Step:
   P2177.
2. Time:
   started UTC `2026-06-02T15:44:46Z`, completed UTC `2026-06-02T15:44:46Z`; local completed `2026-06-02 20:44:46 +05:00`.
3. Artifact:
   `reports/qa_gate/p2177_p2079_f1_data_gate_utc_close_recheck_20260602T154446Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2178` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154634Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T154633Z.json`), `pip check PASS`, P2177 artifact parse `PASS`.

## 2026-06-02 P2178 P2079 F1 UTC-Close Recheck
1. Step:
   P2178.
2. Time:
   started UTC `2026-06-02T15:48:06Z`, completed UTC `2026-06-02T15:48:06Z`; local completed `2026-06-02 20:48:06 +05:00`.
3. Artifact:
   `reports/qa_gate/p2178_p2079_f1_data_gate_utc_close_recheck_20260602T154806Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2179` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155005Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T155004Z.json`), `pip check PASS`, P2178 artifact parse `PASS`.

## 2026-06-02 P2179 P2079 F1 UTC-Close Recheck
1. Step:
   P2179.
2. Time:
   started UTC `2026-06-02T15:51:19Z`, completed UTC `2026-06-02T15:51:19Z`; local completed `2026-06-02 20:51:19 +05:00`.
3. Artifact:
   `reports/qa_gate/p2179_p2079_f1_data_gate_utc_close_recheck_20260602T155119Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2180` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155304Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T155304Z.json`), `pip check PASS`, P2179 artifact parse `PASS`.

## 2026-06-02 P2180 P2079 F1 UTC-Close Recheck
1. Step:
   P2180.
2. Time:
   started UTC `2026-06-02T15:54:33Z`, completed UTC `2026-06-02T15:54:33Z`; local completed `2026-06-02 20:54:33 +05:00`.
3. Artifact:
   `reports/qa_gate/p2180_p2079_f1_data_gate_utc_close_recheck_20260602T155433Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2181` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155722Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T155722Z.json`), `pip check PASS`, P2180 artifact parse `PASS`.

## 2026-06-02 P2181 P2079 F1 UTC-Close Recheck
1. Step:
   P2181.
2. Time:
   started UTC `2026-06-02T15:58:51Z`, completed UTC `2026-06-02T15:58:51Z`; local completed `2026-06-02 20:58:51 +05:00`.
3. Artifact:
   `reports/qa_gate/p2181_p2079_f1_data_gate_utc_close_recheck_20260602T155851Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2182` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160102Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T160101Z.json`), `pip check PASS`, P2181 artifact parse `PASS`.

## 2026-06-02 P2182 P2079 F1 UTC-Close Recheck
1. Step:
   P2182.
2. Time:
   started UTC `2026-06-02T16:02:18Z`, completed UTC `2026-06-02T16:02:18Z`; local completed `2026-06-02 21:02:18 +05:00`.
3. Artifact:
   `reports/qa_gate/p2182_p2079_f1_data_gate_utc_close_recheck_20260602T160218Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2183` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160404Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T160403Z.json`), `pip check PASS`, P2182 artifact parse `PASS`.

## 2026-06-02 P2183 P2079 F1 UTC-Close Recheck
1. Step:
   P2183.
2. Time:
   started UTC `2026-06-02T16:05:16Z`, completed UTC `2026-06-02T16:05:16Z`; local completed `2026-06-02 21:05:16 +05:00`.
3. Artifact:
   `reports/qa_gate/p2183_p2079_f1_data_gate_utc_close_recheck_20260602T160516Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2184` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160705Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T160704Z.json`), `pip check PASS`, P2183 artifact parse `PASS`.

## 2026-06-02 P2184 P2079 F1 UTC-Close Recheck
1. Step:
   P2184.
2. Time:
   started UTC `2026-06-02T16:08:48Z`, completed UTC `2026-06-02T16:08:48Z`; local completed `2026-06-02 21:08:48 +05:00`.
3. Artifact:
   `reports/qa_gate/p2184_p2079_f1_data_gate_utc_close_recheck_20260602T160848Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2185` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161033Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161033Z.json`), `pip check PASS`, P2184 artifact parse `PASS`.

## 2026-06-02 P2185 P2079 F1 UTC-Close Recheck
1. Step:
   P2185.
2. Time:
   started UTC `2026-06-02T16:11:50Z`, completed UTC `2026-06-02T16:11:50Z`; local completed `2026-06-02 21:11:50 +05:00`.
3. Artifact:
   `reports/qa_gate/p2185_p2079_f1_data_gate_utc_close_recheck_20260602T161150Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2186` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161336Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161335Z.json`), `pip check PASS`, P2185 artifact parse `PASS`.

## 2026-06-02 P2186 P2079 F1 UTC-Close Recheck
1. Step:
   P2186.
2. Time:
   started UTC `2026-06-02T16:15:30Z`, completed UTC `2026-06-02T16:15:30Z`; local completed `2026-06-02 21:15:30 +05:00`.
3. Artifact:
   `reports/qa_gate/p2186_p2079_f1_data_gate_utc_close_recheck_20260602T161530Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2187` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161633Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161632Z.json`), `pip check PASS`, P2186 artifact parse `PASS`.

## 2026-06-02 P2187 P2079 F1 UTC-Close Recheck
1. Step:
   P2187.
2. Time:
   started UTC `2026-06-02T16:19:09Z`, completed UTC `2026-06-02T16:19:09Z`; local completed `2026-06-02 21:19:09 +05:00`.
3. Artifact:
   `reports/qa_gate/p2187_p2079_f1_data_gate_utc_close_recheck_20260602T161909Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2188` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161942Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161941Z.json`), `pip check PASS`, P2187 artifact parse `PASS`.

## 2026-06-02 P2188 P2079 F1 UTC-Close Recheck
1. Step:
   P2188.
2. Time:
   started UTC `2026-06-02T16:22:57Z`, completed UTC `2026-06-02T16:22:57Z`; local completed `2026-06-02 21:22:57 +05:00`.
3. Artifact:
   `reports/qa_gate/p2188_p2079_f1_data_gate_utc_close_recheck_20260602T162257Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2189` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162331Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T162331Z.json`), `pip check PASS`, P2188 artifact parse `PASS`.

## 2026-06-02 P2189 P2079 F1 UTC-Close Recheck
1. Step:
   P2189.
2. Time:
   started UTC `2026-06-02T16:25:48Z`, completed UTC `2026-06-02T16:25:48Z`; local completed `2026-06-02 21:25:48 +05:00`.
3. Artifact:
   `reports/qa_gate/p2189_p2079_f1_data_gate_utc_close_recheck_20260602T162548Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2190` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162627Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T162626Z.json`), `pip check PASS`, P2189 artifact parse `PASS`.

## 2026-06-02 P2190 P2079 F1 UTC-Close Recheck
1. Step:
   P2190.
2. Time:
   started UTC `2026-06-02T16:30:21Z`, completed UTC `2026-06-02T16:30:21Z`; local completed `2026-06-02 21:30:21 +05:00`.
3. Artifact:
   `reports/qa_gate/p2190_p2079_f1_data_gate_utc_close_recheck_20260602T163021Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2191` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163046Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163046Z.json`), `pip check PASS`, P2190 artifact parse `PASS`.

## 2026-06-02 P2191 P2079 F1 UTC-Close Recheck
1. Step:
   P2191.
2. Time:
   started UTC `2026-06-02T16:33:25Z`, completed UTC `2026-06-02T16:33:25Z`; local completed `2026-06-02 21:33:25 +05:00`.
3. Artifact:
   `reports/qa_gate/p2191_p2079_f1_data_gate_utc_close_recheck_20260602T163325Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2192` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163350Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163349Z.json`), `pip check PASS`, P2191 artifact parse `PASS`.

## 2026-06-02 P2192 P2079 F1 UTC-Close Recheck
1. Step:
   P2192.
2. Time:
   started UTC `2026-06-02T16:36:04Z`, completed UTC `2026-06-02T16:36:04Z`; local completed `2026-06-02 21:36:04 +05:00`.
3. Artifact:
   `reports/qa_gate/p2192_p2079_f1_data_gate_utc_close_recheck_20260602T163604Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2193` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163630Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163629Z.json`), `pip check PASS`, P2192 artifact parse `PASS`.

## 2026-06-02 P2193 P2079 F1 UTC-Close Recheck
1. Step:
   P2193.
2. Time:
   started UTC `2026-06-02T16:38:39Z`, completed UTC `2026-06-02T16:38:39Z`; local completed `2026-06-02 21:38:39 +05:00`.
3. Artifact:
   `reports/qa_gate/p2193_p2079_f1_data_gate_utc_close_recheck_20260602T163839Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2194` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163903Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163902Z.json`), `pip check PASS`, P2193 artifact parse `PASS`.

## 2026-06-02 P2194 P2079 F1 UTC-Close Recheck
1. Step:
   P2194.
2. Time:
   started UTC `2026-06-02T16:41:09Z`, completed UTC `2026-06-02T16:41:09Z`; local completed `2026-06-02 21:41:09 +05:00`.
3. Artifact:
   `reports/qa_gate/p2194_p2079_f1_data_gate_utc_close_recheck_20260602T164109Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2195` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164133Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T164132Z.json`), `pip check PASS`, P2194 artifact parse `PASS`.

## 2026-06-02 P2195 P2079 F1 UTC-Close Recheck
1. Step:
   P2195.
2. Time:
   started UTC `2026-06-02T16:45:02Z`, completed UTC `2026-06-02T16:45:02Z`; local completed `2026-06-02 21:45:02 +05:00`.
3. Artifact:
   `reports/qa_gate/p2195_p2079_f1_data_gate_utc_close_recheck_20260602T164502Z.json`.
4. Result:
   `BLOCKED_BY_UTC_CLOSE`.
5. Boundary:
   next number `P2196` after `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
6. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164527Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T164526Z.json`), `pip check PASS`, P2195 artifact parse `PASS`.

## 2026-06-02 Quick Structural Audit
1. Time:
   completed UTC `2026-06-02T18:27:15Z`; local completed `2026-06-02 23:27:15 +05:00`.
2. Artifact:
   `reports/qa_gate/quick_structural_audit_framework_20260602T182715Z.json`.
3. Result:
   `PASS_WITH_ROUTE_CORRECTION`.
4. Conclusion:
   P2079 UTC-close gate blocks forward/production only. Framework/catalog validation is already assembled enough to open a separate structural big-window command-set/dry-run chain on closed historical data.
5. Facts:
   68 feature rows, 6 blocks, 27 linked profiles, narrow/medium/wide presets, 3x3/9-worker launcher support, block catalog `36/36 runtime OK`, positive `1`, neutral `18`, negative `17`, infra_fail `0`.
6. Runtime:
   no ingest, Optuna runtime, production action, or unfreeze command was launched in this audit.

### [2026-06-02T19:16:09Z] AUDIT | HARD STRUCTURAL FEATURES/HYPOTHESES | PASS_WITH_FINDINGS
1. Artifact:
   `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md`.
2. Structural facts:
   68 feature rows across 6 blocks, 20 hypotheses, 27/27 profiles linked, narrow/medium/wide anchors preserved, block catalog `36/36 runtime OK`.
3. Finding:
   block matrices isolate feature rows, but hypotheses/trend filters are global unless filtered; P2079 `volume_flow` candidate uses `min_max_range_revert`, which requires `structure_ta` columns.
4. Boundary:
   P2079 remains candidate_for_forward only; production remains `NO_GO`.
5. Next decision:
   choose mixed semantics or strict block purity; recommended strict block purity before battle calibration.

## 2026-06-02 Structural Big-Window Command Set And User Stop
1. Command-set:
   `reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json`.
2. Command-set result:
   `PASS`; raw policy preflight `PASS`; compile/dry-run `36/36 PASS`; runtime was not started in that artifact.
3. Runtime started:
   structural narrow only, historical window train `2026-05-29..2026-05-31`, test `2026-06-01`, 3x3/9 workers.
4. User stop:
   user requested `стопни свой прогон`; active ML process tree was killed.
5. Stop artifact:
   `reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`.
6. Result:
   `STOPPED_BY_USER_AND_FREEZE_RESTORED`; completed launcher commands `3`, stopped launcher commands `1`, positive candidates `0`.
7. Safety:
   restored stale temporary unlock from backup, removed pool marker, readiness freeze preserved (`reports/readiness/readiness_check_20260602T192156Z.json`), text_guard `PASS`, `pip check PASS`.

### [2026-06-03T06:09:19Z] AUDIT | P2196A OPTUNA BATTLE READINESS | STRICT PURITY NEXT
1. Artifact:
   `reports/qa_gate/p2196a_optuna_battle_readiness_audit_20260603T060919Z.md`.
2. Result:
   `NO_GO_FOR_PRODUCTION / GO_TO_STRICT_BLOCK_PURITY_FIX_BEFORE_BATTLE`.
3. Facts:
   Optuna/APTuna contour works structurally, 3x3/9 workers are supported, historical block catalog was `36/36 runtime OK`, and structural big-window command-set dry-run was `36/36 PASS`.
4. Finding:
   block matrices isolate feature rows, but hypotheses/trend filters are global unless filtered; P2079 is a mixed-semantics candidate until strict filtering is added.
5. Data gate:
   current UTC is after 2026-06-03T00:00:00Z, but raw/core forward files for 2026-06-02 and 2026-06-03 are absent in the workspace.
6. Next:
   `P2196B` strict block-purity compatibility map and filtering before battle runtime.
7. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T061526Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T061522Z.json`), `pip check PASS`.

### [2026-06-03T06:58:21Z] P2196B | VOLUME/VOLATILITY CONTEXT WIRING | PASS_CONTEXT_WIRING
1. Artifact:
   `reports/qa_gate/p2196b_volume_context_wiring_audit_20260603T065821Z.json`.
2. Code/config:
   added always-on `context_blocks` for `volume_flow` and `price_volatility` to full matrix and all 6 catalog block matrices; compile/runtime/profile/report path now carries context blocks.
3. Signal:
   raw `volume` remains market input; derived volume context is calibrated through `volume_flow`. Rule-only signal now uses `mfi14`, `vwap_distance`, and `delta_volume` when present.
4. Validation:
   unittest `tests.test_optuna_space_constraints tests.test_optuna_search_runtime` -> `69/69 OK`; 7 matrix compile audit -> `PASS`.
5. Post-sync checks:
   text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T070000Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T065959Z.json`), `pip check PASS`.
6. Boundary:
   no ingest/runtime/production/unfreeze launched; strict hypothesis/trend compatibility filtering remains next before battle runtime.

### [2026-06-03T10:04:04Z] P2196B | STRICT HYPOTHESIS FILTERING | PASS
1. Artifact:
   `reports/qa_gate/p2196b_strict_hypothesis_filter_full_audit_20260603T100404Z.json`.
2. Result:
   full/catalog matrices across long/short and narrow/medium/wide compile `42/42 PASS` with strict hypothesis filtering.
3. Code:
   `compile_optuna_space` filters hypotheses by required columns inside primary block plus always-on context; `none` remains always allowed; incompatible fallback trend is no longer re-added.
4. Tests:
   focused tests `tests.test_optuna_space_constraints tests.test_optuna_search_runtime tests.test_backtest_fields` -> `77/77 OK`.

### [2026-06-03T10:05:04Z] P2196C | STRICT COMMAND SET DRY-RUN | PASS
1. Artifact:
   `reports/optuna_catalog/index/p2196c_strict_command_set_20260603T100504Z.json`.
2. Result:
   strict battle command-set dry-run `36/36 PASS`.
3. Data:
   raw preflight `PASS`, artifact `reports/qa_gate/preflight_window_20260603T100432Z.json`.
4. Boundary:
   no Optuna runtime launched; next is P2196D strict P2079-equivalent runtime if user proceeds.
5. Residual:
   full `unittest discover` residuals recorded separately in `reports/qa_gate/p2196c_unittest_discover_residuals_20260603T100559Z.json`.

### [2026-06-03T10:08:56Z] POST-SYNC | P2196C HEALTH CHECKS | PASS
1. text_guard:
   `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T100856Z.json`.
2. readiness:
   freeze preserved, project production remains `NO_GO`, calibration remains allowed only through APTuna temporary unlock path; artifact `reports/readiness/readiness_check_20260603T100856Z.json`.
3. pip:
   `pip check PASS`.
4. Next:
   `P2196D` strict P2079-equivalent runtime check, then `P2196E` strict battle calibration narrow -> medium -> wide.

### [2026-06-03T10:14:50Z] P2196D | STRICT RUNTIME CALIBRATION START | PASS_RUNTIME_OK
1. Command:
   block03 `volume_flow`, grid `narrow`, mode `long_only`, train `2026-05-29..2026-05-31`, test `2026-06-01`, 3x3/9 workers, temporary calibration unlock.
2. Result:
   launcher `OK`; best worker `w3`; best OOS `+1.5266529420731034%`; trades `1`; goal `1.0%` passed by `w2/w3`.
3. Artifacts:
   best summary `reports/adaptive/long_only_pool_20260603t101450z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T101454Z.json`; top experimental card `reports/top_strategy/long_only_pool_20260603t101450z_w3/top_SOLUSDT_1m_2026-06-01_20260603T101522Z_MODE-LONG_ONLY_TF-1M_RET-+1.5267pct/top_strategy_card.json`.
4. Boundary:
   train gate failed, therefore no production/latest publication; result is experimental positive and proves runtime calibration contour works.
5. Next:
   `P2196E` continue strict battle calibration sequence.

### [2026-06-03T10:21:58Z] P2196E | VOLUME_FLOW NARROW SHORT | PASS_RUNTIME_OK
1. First attempt:
   `2026-06-03T10:18:59Z` returned `PARTIAL_FAIL`; worker `w1` crashed on empty/unreadable search report JSON.
2. Fix:
   added `_read_json_report_with_retry` in `src/mlbotnav/adaptive_auto_train.py`; unreadable report now becomes `search_report_read_failed` iteration status.
3. Tests:
   focused tests `tests.test_adaptive_candidate_pick tests.test_optuna_space_constraints tests.test_optuna_search_runtime tests.test_backtest_fields` -> `83/83 OK`.
4. Retest:
   block03 `volume_flow`, grid `narrow`, mode `short_only`, 3x3/9 workers -> launcher `OK`, all 3 workers exit `0`.
5. Result:
   best OOS `0%`, trades `0`, no candidate; summary `reports/adaptive/short_only_pool_20260603t102158z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T102202Z.json`.

### [2026-07-06T18:30:11Z] STAS3 | PERCENT LADDER AND TP REVIEW | READY
1. Scope:
   По прямому запросу пользователя доведен Stas3 от начала до результата: post-entry анализ входов Stas1 поверх фаз Stas2, без ML/Optuna/scorer/target-lock/API.
2. Code:
   обновлен `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py`, `tests/test_visual_entry_stas3_percent_ladder_review.py`, `STAS3_PERCENT_LADDER_REVIEW/README_RU.md`, wrapper-команды `run_day.ps1`, `run_range.ps1`, `open_last_run.ps1`.
3. Final run:
   `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260502_20260503_tp_ladder_v0_20260706_183011`.
4. Result:
   `110` Stas2 rows input, `110` entry rows, `0` skipped, row-count parity `True`, full ladder `0.2..7%`, `65` rows with reasonable TP, `73` mismatch к механическому 1% TP, `27` noise entry, `2` fast clean, `90` late-pump dependent, `24` PNG.
5. Artifacts:
   `STAS3_ENTRY_PHASE_TABLE.csv`, `STAS3_ACTUAL_MOVEMENT.csv`, `STAS3_REASONABLE_TP.csv`, `STAS3_TP_LADDER_BY_PHASE.csv`, `STAS3_TP_LADDER_BY_PROFILE.csv`, `STAS3_TP_LADDER_V0_RU.md`, `STAS3_PERCENT_LADDER_TABLES.xlsx`, `STAS3_REPORT_RU.md`.
6. Checks:
   `py_compile PASS`, focused pytest `2/2 PASS`, final run PASS, `openpyxl` workbook load PASS, CSV BOM PASS, PNG non-empty PASS, Russian report UTF-8 PASS, `open_last_run.ps1 -Open tp -NoOpen` PASS.
7. Boundary:
   Stas3 остается post-entry audit/review. `STAS3_TP_LADDER_V0_RU.md` не является торговой стратегией и не является approved ML label.

### [2026-07-07T05:59:29Z] STAS3 | EXTENDED RANGE 2026-05-04..2026-05-09 | READY
1. Source:
   найден последний Stas2 run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_setup_quality_v0_20260707_043734`, `417` строк, дни `2026-05-04..2026-05-09`.
2. Command:
   `.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-04 -EndDay 2026-05-09 -RunLabel stas3_20260504_20260509_tp_ladder_v0 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260504_20260509_setup_quality_v0_20260707_043734 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50`.
3. Final run:
   `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_tp_ladder_v0_20260707_055929`.
4. Result:
   `417` Stas2 rows input, `417` entry rows, `0` skipped, row-count parity `True`, `410` hit 1%, `283` rows with reasonable TP, `285` mismatch к 1% TP, `84` noise entry, `13` fast clean, `238` late-pump dependent, `83` PNG.
5. Validation:
   core CSV counts `417/417/417/417`, ladder phase rows `6`, profile rows `89`, workbook sheets load PASS, CSV BOM PASS, PNG non-empty PASS, Russian report UTF-8 PASS, `open_last_run.ps1 -Open tp -NoOpen` points to this run.
6. Boundary:
   Stas3 остается post-entry audit. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-07T07:22:26Z] STAS3 | TP EXIT OVERLAY | READY
1. Request:
   пользователь указал, что на графике не видно выхода/тейк-профита, и попросил сделать простой визуальный слой для понимания отработки сделок.
2. Code:
   в `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py` добавлен TP/EXIT overlay: entry-треугольник, TP-линия, звезда `EXIT`, подпись времени до TP. Желтый `TP v0` показывает фазовый TP; серый пунктир `TP 1%` используется как fallback, если фазовый TP не рассчитан.
3. Final run:
   `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_tp_exit_overlay_v0_20260707_072226`.
4. Validation:
   `py_compile PASS`, focused pytest `2/2 PASS`, run PASS, core CSV counts `417/417/417/417`, workbook load PASS, CSV BOM PASS, `83` PNG, пустых PNG нет. Визуально проверены `STAS3_ENTRY_LADDER_PAGE_01.png` и `STAS3_DAY_OVERVIEW_20260504.png`.
5. Boundary:
   расчет TP не превращался в стратегию; это визуальный слой Stas3 post-entry audit. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-07T07:39:15Z] STAS3 | SIGNAL ENTRY EXIT OVERLAY | READY
1. Problem:
   пользователь указал, что точки входа выглядят съехавшими: Stas2 показывал прежний low/anchor-сигнал, а Stas3 показывал уже исполнение входа на следующей свече без явной цены входа.
2. Code:
   в `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py` добавлен раздельный visual layer: оранжевый `SIGNAL` на `anchor_time_utc/anchor_low_price`, голубой `ENTRY` на `entry_time_utc/entry_price_5bps`, пунктир `SIGNAL -> ENTRY`, TP-линия и звезда `EXIT`. В Stas3 CSV/XLSX протянуты `anchor_low_price`, `entry_open_price`, `entry_price_5bps`.
3. Final run:
   `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_signal_entry_exit_overlay_v0_20260707_073915`.
4. Validation:
   `py_compile PASS`, focused pytest `2/2 PASS`, run PASS, core CSV counts `417/417/417/417`, workbook load PASS, CSV BOM PASS, `83` PNG, пустых PNG нет. Визуально проверен `STAS3_ENTRY_LADDER_PAGE_01.png`; первая строка показывает `SIGNAL 83.5900 -> ENTRY 83.7218 -> EXIT`.
5. Boundary:
   исправлен только visual/review слой Stas3. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-07T08:02:53Z] STAS3 | TP MOVE ARROWS | READY
1. Problem:
   горизонтальная TP-линия показывала уровень цены, но визуально не показывала, как сделка отработала от входа к тейк-профиту; пользователь показал ожидаемый вид красными стрелками.
2. Code:
   в `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py` добавлены красные диагональные стрелки `ENTRY -> EXIT` на дневном обзоре и closeup-страницах. Горизонтальная TP-линия оставлена как уровень цены цели.
3. Final run:
   `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_signal_entry_tp_move_v0_20260707_080253`.
4. Validation:
   `py_compile PASS`, focused pytest `2/2 PASS`, run PASS, core CSV counts `417/417/417/417`, workbook load PASS, CSV BOM PASS, `83` PNG, пустых PNG нет. Визуально проверены `STAS3_ENTRY_LADDER_PAGE_01.png` и `STAS3_DAY_OVERVIEW_20260504.png`.
5. Boundary:
   изменен только визуальный слой Stas3 post-entry audit. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-07T09:02:46Z] STAS3 | BIG MOVE REVIEW | READY
1. Request:
   пользователь уточнил, что цель - организовать обучение сделкам больше `0.2%`: видеть, где можно тянуть от low/entry до большого движения, с учетом фазы, волатильности, setup и раннего поведения цены.
2. Agent:
   подключен subagent `Lovelace`; он проверил точки встройки и формулы, файлы не менял, ML/Optuna/API/training/export не запускал.
3. Code:
   в `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py` добавлены post-entry review-поля `SIGNAL/ENTRY -> MFE MAX`, `ENTRY -> 0.2/0.5/1.0%`, extra после ранних TP, `mae_before_mfe_pct`, review-only `exit_review_bucket`, а также отдельные `STAS3_BIG_MOVE_REVIEW_PAGE_*.png`. Тест `tests/test_visual_entry_stas3_percent_ladder_review.py` расширен проверками новых формул.
4. Final run:
   `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_big_move_review_v2_20260707_090246`.
5. Result:
   `417` rows, `0` skipped, `141` `EARLY_1PCT_TRAIL_REVIEW`, `218` `BIG_MFE_BUT_DEEP_MAE_REVIEW`, `51` `LATE_MFE_PUMP_REVIEW`, `12` big-move pages, `95` PNG.
6. Artifacts:
   `STAS3_LOW_SIGNAL_TO_MFE_MAX.csv`, `STAS3_ENTRY_TO_TP_PATH.csv`, `STAS3_EXIT_REVIEW_BUCKETS.csv`, `STAS3_EXIT_REVIEW_SUMMARY.csv`, Excel sheets `Low to MFE max`, `Entry to TP path`, `Exit review`, `Exit review summary`.
7. Validation:
   `py_compile PASS`, focused pytest `2/2 PASS`, full run PASS, workbook load PASS, core new CSV counts `417/417/417`, `95` PNG, пустых PNG нет, визуально проверены `STAS3_ENTRY_LADDER_PAGE_01.png`, `STAS3_DAY_OVERVIEW_20260504.png`, `STAS3_BIG_MOVE_REVIEW_PAGE_01.png`.
8. Boundary:
   это только Stas3 post-entry audit/review. `MFE MAX` и `exit_review_bucket` не являются стратегией, scorer, target-lock или ML-label. ML/export/training, Optuna и API не запускались.

### [2026-07-07T09:40:00Z] CODEX | VSCODE LOAD AUDIT | LOCAL FIX APPLIED
1. Request:
   пользователь отложил Stas3 и попросил разобраться, почему после перезагрузки VS Code/Codex постоянно грузит CPU/RAM/disk.
2. Findings:
   найдены активные `git add -A` процессы от Codex; вложенных `.git` внутри `C:\Users\007\Desktop\MLbotNav` нет. Тяжелые локальные артефакты: `_codex_offload_20260530` около `5912 MB`, `models` около `1517 MB`, `reports` около `1070 MB`, STAS `runs` около `629 MB` суммарно.
3. Fix:
   остановлены зависшие `git add -A`; `.git/index.lock` отсутствует. В `.gitignore` добавлены STAS `runs`. В `.vscode/settings.json` добавлены excludes для watcher/search/Pylance по тяжелым папкам.
4. Validation:
   `.vscode/settings.json` проходит `ConvertFrom-Json`; `git check-ignore -v` подтверждает `STAS1/2/3 .../runs`; `git status --short --untracked-files=normal` выполняется примерно за `0.03s`.
5. Boundary:
   данные, отчеты, модели, кэши и run-артефакты не удалялись. ML/export/training, Optuna и API не запускались.

### [2026-07-07T09:55:00Z] CODEX | VSCODE RELOAD CHECK | OK
1. Request:
   пользователь перезагрузил VS Code и попросил проверить состояние.
2. Result:
   тяжелых Git-процессов нет; `git add -A` не появился снова. Старый нулевой `git status --porcelain` без живого родителя остановлен.
3. Validation:
   `git status --short --untracked-files=normal` около `0.03s`, `git check-ignore` по STAS `runs` остается валидным. VS Code почти idle; заметная CPU-активность остается только у активного Codex-приложения во время чата и tool-проверок.

### [2026-07-09T00:00:00Z] STAS3 | V2 TZ GRID CORRECTION | READY
1. Request:
   пользователь уточнил ТЗ Stas3: сначала корректируем только ТЗ, работаем по LONG, берем актуальный Stas2-график с LONG/SHORT/WAVE/GAP, не ограничиваем сделку календарными `24h`.
2. Update:
   в `STAS3_PERCENT_LADDER_REVIEW/TZ_STAS3_V2_RESET_RU.md` зафиксировано: минимальная сетка `0.3..1.0%`, расширенная `1.2, 1.5, 1.7, 1.9, 2.0, 2.1, 2.3, 2.5, 2.6, 2.8, 3.0%`, дальний хвост `3.2..10.0%` с шагом `0.2%`.
3. Boundary:
   `0.2%` не является рабочим TP-уровнем V2; оно осталось только как историческая проблема V1 и как шаг генерации хвоста. Код, прогоны, ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-09T00:10:00Z] STAS3 | V2 TZ ENTRY CONTRACT AND MEDIUM MOVES | READY
1. Request:
   пользователь уточнил, что в новом Stas2 run уже есть low-точки и точки входа; Stas3 не должен ничего придумывать, нужно закрепить цену входа и пока разбирать LONG: быстрые TP и средние ходы от `1.0%`, без оформления swing-стратегии.
2. Source checked:
   `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`. В `STAS2_RECORDS.csv` проверено `214` строк за `2026-05-10..2026-05-12`; пустых `anchor_low_price`, `entry_open_price`, `entry_price_5bps` нет; `context_before_entry_check != True` равно `0`.
3. Update:
   в ТЗ Stas3 V2 добавлен жесткий контракт входа: брать `anchor_time_utc`, `anchor_low_price`, `entry_time_utc`, `entry_open_price`, `entry_price_5bps`; расчетная цена `entry_price_for_calc = entry_price_5bps`. Быстрые TP: `0.3-0.9%`; средние LONG-ходы: от `1.0%`; хвост после `3.0%` до `10.0%`, до `20.0%` только отдельная диагностика.
4. Boundary:
   код и прогоны не запускались. Swing пока не размещается как стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-09T00:20:00Z] STAS3 | V2 MEDIUM GRID STEP CORRECTION | READY
1. Request:
   пользователь уточнил сетку средних LONG-ходов: от `1.0%` до `2.0%` шаг `0.1%`, с `2.0%` до `20.0%` шаг `0.2%`.
2. Update:
   в `STAS3_PERCENT_LADDER_REVIEW/TZ_STAS3_V2_RESET_RU.md` изменена процентная лестница: быстрые TP `0.3-0.9%`, средняя сетка `1.0, 1.1, ... 2.0%`, продолжение `2.0, 2.2, ... 20.0%` с дедубликацией `2.0%`. `hit_20p0_rate` теперь входит в рабочую V2-сетку, а не optional.
3. Boundary:
   код и прогоны не запускались. Это только корректировка ТЗ. Swing по-прежнему не оформляется как стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-09T00:30:00Z] STAS3 | V2 STAS2 CONTEXT BUNDLE FIXED | READY
1. Request:
   пользователь зафиксировал рабочий Stas2 source `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330` и дни `2026-05-10`, `2026-05-11`, `2026-05-12`; на скрине выделены сессии, фон, LONG/SHORT, WAVE, волатильность/процентные блоки и объем.
2. Update:
   в ТЗ Stas3 V2 добавлен обязательный context bundle по каждой сделке: session, background, LONG, SHORT as risk, WAVE, volatility/path/range percent blocks, volume-context. Добавлены review-поля `max_feasible_review_tp_pct`, `ideal_review_tp_pct`, `ideal_review_tp_reason`, `ideal_review_tp_warning`.
3. Boundary:
   `ideal_review_tp_pct` - hindsight-review вывод по уже заданной сделке, не торговая команда, не scorer, не target-lock и не ML-label. Код и прогоны не запускались.

### [2026-07-09T00:40:00Z] STAS3 | V2 SHORT RISK CONTEXT ONLY | READY
1. Request:
   пользователь уточнил, что `SHORT` можно учитывать только как процентный риск-фон/противоход для LONG; short-точек входа нет, поэтому short-сделки в Stas3 V2 не используются.
2. Update:
   в `STAS3_PERCENT_LADDER_REVIEW/TZ_STAS3_V2_RESET_RU.md`, README и `docs/codex/*` зафиксировано: Stas3 V2 работает только с LONG-входами; `SHORT` остается только `SHORT-risk%` контекстом. Добавлен guard `short_context_only_flag`.
3. Boundary:
   запрещены short-входы, short-TP, short-ladder, short-статистика и смешивание LONG/SHORT TP. Код и прогоны не запускались. ML/export/training, Optuna, scorer, target-lock и API не запускались.
### [2026-07-09T12:20:00Z] STAS4 | COMBO 4 STRATEGIES 3 DAYS | READY
1. Request:
   пользователь попросил прогнать 4 комбинированные стратегии Stas4 на трех днях поверх рабочего Stas2 run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_short_macro_wave_review_20260709_071233`.
2. Result:
   созданы 12 PNG-оверлеев с зелеными галочками старых входов-шумов и синими стрелками новых кандидатов. Сводка: `structure_ta+trend_momentum` = `172` / `5`, `structure_ta+volume_flow` = `158` / `2`, `pattern+structure_ta` = `106` / `6`, `density_profile+structure_ta` = `72` / `11`.
3. Artifacts:
   главный отчет `STAS4_FEATURE_HYPOTHESIS_REVIEW/STAS4_COMBO_4_STRATEGIES_3D_SUMMARY_20260709_RU.md`; все графики лежат в `STAS4_FEATURE_HYPOTHESIS_REVIEW`.
4. Validation:
   `python -m py_compile src\mlbotnav\visual_entry_stas4_family_overlay.py` прошел; проверены 12 PNG, все непустые.
5. Boundary:
   старая логика Stas1/Stas2 не менялась. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T10:55:00Z] STAS4 | MANUAL LABELS 20260504 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-04` и уточнил: `тут 9`.
2. Update:
   в `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels` созданы draft-файлы `KEEP_20260504_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260504_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260504_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260504_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA002`, `LA004`, `LA020`, `LA032`, `LA038`, `LA042`, `LA045`, `LA049`, `LA065`.
3. Result:
   `9` KEEP_DRAFT, `65` CUT_DRAFT, всего `74` входа дня. `LA020`, `LA032`, `LA042`, `LA045` одновременно имеют желтый `X` стратегии `density_profile+structure_ta`.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T11:35:00Z] STAS4 | MANUAL LABELS 20260508 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-08` как продолжение ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260508_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260508_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260508_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260508_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA009`, `LA010`, `LA021`, `LA041`, `LA045`, `LA048`, `LA060`, `LA069`.
3. Result:
   `8` KEEP_DRAFT, `61` CUT_DRAFT, всего `69` входов дня. Из выбранных только `LA060` одновременно имеет желтый `X` стратегии `density_profile+structure_ta`. `LA009` и `LA010` имеют одинаковый low, но зафиксированы как две отдельные пользовательские отметки.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T11:05:00Z] STAS4 | MANUAL LABELS 20260505 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-05` без отдельного текста, как продолжение ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260505_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260505_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260505_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260505_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA001`, `LA005`, `LA013`, `LA026`, `LA028`, `LA036`, `LA041`, `LA044`.
3. Result:
   `8` KEEP_DRAFT, `51` CUT_DRAFT, всего `59` входов дня. Из выбранных только `LA013` одновременно имеет желтый `X` стратегии `density_profile+structure_ta`.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T11:15:00Z] STAS4 | MANUAL LABELS 20260506 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-06` как продолжение ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260506_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260506_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260506_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260506_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA001`, `LA008`, `LA016`, `LA021`, `LA039`, `LA052`, `LA061`.
3. Result:
   `7` KEEP_DRAFT, `62` CUT_DRAFT, всего `69` входов дня. Из выбранных `LA021`, `LA039`, `LA061` одновременно имеют желтый `X` стратегии `density_profile+structure_ta`.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.

### [2026-07-10T11:25:00Z] STAS4 | MANUAL LABELS 20260507 | DRAFT
1. Request:
   пользователь прислал скрин `2026-05-07` как продолжение ручной разметки 14-дневной пачки.
2. Update:
   созданы draft-файлы `KEEP_20260507_FROM_RED_UNDERLINES_DRAFT.csv`, `LABELS_20260507_ALL_ENTRIES_DRAFT.csv`, `KEEP_20260507_FROM_RED_UNDERLINES_DRAFT.json`, `ANNOTATED_20260507_KEEP_DRAFT.png`. Зафиксированы KEEP: `LA014`, `LA017`, `LA019`, `LA023`, `LA024`, `LA036`, `LA050`, `LA053`, `LA060`, `LA073`, `LA075`.
3. Result:
   `11` KEEP_DRAFT, `68` CUT_DRAFT, всего `79` входов дня. Из выбранных `LA036`, `LA050`, `LA060` одновременно имеют желтый `X` стратегии `density_profile+structure_ta`.
4. Boundary:
   это черновая ручная разметка для review, не финальный ML-label и не стратегия. ML/export/training, Optuna, scorer, target-lock и API не запускались.
## Session 2026-07-11 Codex Startup Disk Load Audit

Проведен аудит жалобы на минутную нагрузку диска после перезагрузки и запуска Codex. Код не менялся, файлы не удалялись.

Итоги: активной Git-проблемы сейчас нет; `git status` быстрый, зависшего `git add -A` нет. Основной вес найден в `C:\Users\007\.codex` около `13.2 GB` и в проектном `_codex_offload_20260530` около `5.9 GB`. Подробности записаны в `docs/codex/CODEX_STARTUP_DISK_LOAD_AUDIT_20260711_RU.md`.

Следующий шаг только после подтверждения пользователя: перенос `_codex_offload_20260530` из рабочей папки в архив вне проекта и отдельное решение по старым `.codex` backup/archived-сессиям.

### [2026-07-13T00:00:00Z] STAS5 V2 | FEATURE SNAPSHOT | READY
1. Request:
   пользователь после замечания о перескоках подтвердил продолжение работы строго по `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`, раздел 14.
2. Update:
   закрыт раздел 14, пункт 4: создан `src/mlbotnav/stas5_v2_feature_snapshot_builder.py`. Он объединяет v1 feature snapshot `111` признаков, V2 combo feature layer `103` признака и ledger/labels по ключам `day,candidate_id,record_id`.
3. Artifacts:
   созданы `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.csv` и `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.manifest.json`.
4. Result:
   manifest status `PASS`; `972` строк; `214` feature columns; `lost_after_combo_join=0`; `lost_after_ledger_check=0`; `entry_time_mismatch=0`; `anchor_time_mismatch=0`; `v2_combo_feature_available_before_entry_false=0`; forbidden columns `{}`; `KEEP_DRAFT + yellow_x = 30` сохранены.
5. Validation:
   `py_compile` прошел; `tests/test_stas5_v2_feature_snapshot_builder.py` прошел `3 passed`; явный STAS5 test pack прошел `14 passed`.
6. Boundary:
   обучение V2, threshold tuning, forward labels, Optuna/scorer/target-lock/API и Stas3/TP не запускались. Следующий пункт строго по ТЗ: раздел 14, пункт 5 - создать `stas5_v2_leakage_guard.py`.

### [2026-07-13T00:00:00Z] STAS5 V2 | LEAKAGE GUARD | READY
1. Request:
   пользователь подтвердил продолжение по текущему пункту: `stas5_v2_leakage_guard.py`.
2. Update:
   закрыт раздел 14, пункт 5 `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`: создан `src/mlbotnav/stas5_v2_leakage_guard.py` и тесты `tests/test_stas5_v2_leakage_guard.py`.
3. Guard checks:
   проверяются feature columns из manifest, no future/postfact/outcome/Stas3/TP/exit/yellow/strategy in features, `v2_combo_feature_time_utc < entry_time_utc`, row parity, duplicate keys, train range, отсутствие forward-дней и сохранение `KEEP_DRAFT + yellow_x`.
4. Artifact:
   создан `STAS5_ML_CORE/artifacts/v2/guard/stas5_v2_leakage_guard_20260501_20260514_v0.json`.
5. Result:
   `PASS`; `972` строк; `214` feature columns; forbidden feature columns `{}`; label/metadata columns in features `[]`; missing required metadata `[]`; duplicate keys `0`; feature time not before entry `0`; forward days present `0`; `KEEP_DRAFT=115`; `CUT_DRAFT=857`; `KEEP_DRAFT + yellow_x = 30`.
6. Validation:
   `py_compile` прошел; `tests/test_stas5_v2_leakage_guard.py` прошел `4 passed`; явный STAS5 test pack прошел `18 passed`.
7. Boundary:
   обучение V2, threshold tuning, forward labels как train, Optuna/scorer/target-lock/API, V2 PNG и Stas3/TP не запускались. Следующий пункт строго по ТЗ: раздел 14, пункт 6 - создать `stas5_v2_forward_error_ledger.py`.

### [2026-07-13T00:00:00Z] STAS5 V2 | FORWARD ERROR LEDGER | READY
1. Request:
   пользователь дал команду "далее" после выделенного `stas5_v2_forward_error_ledger.py`.
2. Update:
   закрыт раздел 14, пункт 6 `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`: создан `src/mlbotnav/stas5_v2_forward_error_ledger.py` и тесты `tests/test_stas5_v2_forward_error_ledger.py`.
3. Ledger logic:
   таблица соединяет V1 forward `ML_DECISION/ML_KEEP_SCORE/postfact`, V2 combo/risk/gate features и optional user-review labels. Добавлены классы `GREEN_GOOD`, `GREEN_BAD_FALLING_KNIFE`, `GREEN_BAD_TOO_HIGH`, `GREEN_BAD_NO_REVERSAL`, `YELLOW_GOOD`, `YELLOW_BAD`, `SKIP_MISSED_GOOD`, `SKIP_CORRECT`.
4. Artifacts:
   созданы `STAS5_ML_CORE/artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.csv` и `.manifest.json`.
5. Result:
   `PASS`; `435` строк; source V1 rows `435`; source V2 rows `435`; missing V2 rows `0`; duplicate keys `0`; V1 decisions `ENTER=103`, `UNSURE=55`, `SKIP=277`; error classes `GREEN_BAD_FALLING_KNIFE=46`, `GREEN_BAD_NO_REVERSAL=9`, `GREEN_GOOD=48`, `YELLOW_BAD=34`, `YELLOW_GOOD=21`, `SKIP_CORRECT=212`, `SKIP_MISSED_GOOD=65`.
6. Validation:
   `py_compile` прошел; `tests/test_stas5_v2_forward_error_ledger.py` прошел `3 passed`; явный STAS5 test pack прошел `21 passed`.
7. Boundary:
   ledger audit-only. Postfact/user-review поля не использованы как features, train labels или threshold input. Обучение V2, threshold tuning, Optuna/scorer/target-lock/API, V2 PNG и Stas3/TP не запускались. Следующий пункт строго по ТЗ: раздел 14, пункт 7 - V2 pre-ML audit.

### [2026-07-13T00:00:00Z] STAS5 V2 | PRE-ML AUDIT | READY
1. Request:
   пользователь дал команду перейти к пункту 7.
2. Update:
   закрыт раздел 14, пункт 7 `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`: создан `src/mlbotnav/stas5_v2_pre_ml_audit.py` и тесты `tests/test_stas5_v2_pre_ml_audit.py`.
3. Audit logic:
   отчет сравнивает train `KEEP/CUT` по `214` V2 feature columns, считает coverage, numeric effect, categorical KEEP/CUT, group summary и forward error classes. Forward `2026-05-15..2026-05-20` используется только audit-only.
4. Artifacts:
   созданы `STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_PRE_ML_AUDIT_20260501_20260520_RU.md` и `STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_pre_ml_audit_20260501_20260520_v0.json`.
5. Result:
   `READY_FOR_V2_ABLATION_BASELINE`; train rows `972`; `KEEP_DRAFT=115`; `CUT_DRAFT=857`; `KEEP_DRAFT + yellow_x=30`; feature count `214`; guard `PASS`; forward error ledger `PASS`; forbidden feature columns `{}`. Forward audit: bad green `55`, good green `48`, missed good SKIP `65`.
6. Validation:
   `py_compile` прошел; `tests/test_stas5_v2_pre_ml_audit.py` прошел `3 passed`; явный STAS5 test pack прошел `24 passed`.
7. Boundary:
   обучение V2, threshold tuning, production permission, Optuna/scorer/target-lock/API, V2 PNG и Stas3/TP не запускались. Следующий пункт строго по ТЗ: раздел 14, пункт 8 - ablation baseline.

### [2026-07-13T00:00:00Z] STAS5 V2 | FEATURE VISUAL APPROVAL | READY
1. Request:
   Пользователь остановил переход к пункту 8 и попросил сначала показать один train-день со всеми признаками на графике, похожем на старый STAS4 overlay. Выбран день `2026-05-04`.
2. Update:
   Создан `src/mlbotnav/stas5_v2_feature_visual_approval.py` и тесты `tests/test_stas5_v2_feature_visual_approval.py`. Renderer переиспользует старые свечи, session shading, полосы `FON/LONG/SHORT/WAVE` и `COMBO SPECTRUM`, а сверху добавляет V2 labels/features.
3. Artifacts:
   Созданы `STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png` и `.manifest.json`.
4. Result:
   `74` кандидата дня; labels `KEEP_DRAFT=9`, `CUT_DRAFT=65`; visual markers `human_keep_green_markers=9`, `keep_yellow_conflict_cyan_overlay_markers=4`, `yellow_x_cut_overlay_markers=18`; approval buckets for audit table `KEEP=5`, `CONFLICT=4`, `YELLOW_X=18`, `CUT=47`; risk buckets `HIGH_RISK=38`, `CAUTION=21`, `LOW_RISK=13`, `BLOCKED=2`; KEEP ids `LA002`, `LA004`, `LA020`, `LA032`, `LA038`, `LA042`, `LA045`, `LA049`, `LA065`; PNG `4960x4262`, не пустой.
5. Validation:
   `py_compile` прошел; `tests/test_stas5_v2_feature_visual_approval.py` прошел `3 passed`; render command прошел без предупреждений.
6. Boundary:
   Это visual approval only. Ablation baseline, обучение V2, threshold tuning, Optuna/scorer/target-lock/API, Stas3/TP и production permission не запускались. Следующий шаг - пользователь смотрит PNG и дает добро или правки.

### [2026-07-14T16:45:00Z] STAS5 V4 | GROUP RANK TRAIN + FORWARD 26..30 | READY
1. Request:
   Пользователь попросил подготовить обучение на `2026-05-01..2026-05-14` и исправленных `2026-05-15..2026-05-25`, снять `2026-05-15` с карантина, перепроверить цифры, запустить обучение и forward на следующие дни.
2. Update:
   Созданы `src/mlbotnav/stas5_v4_group_rank_dataset.py`, `src/mlbotnav/stas5_v4_group_rank_train.py`, `src/mlbotnav/stas5_v4_forward_group_rank_review.py`, тесты `tests/test_stas5_v4_group_rank_dataset.py`, `tests/test_stas5_v4_group_rank_train.py`; renderer forward PNG теперь распознает `STAS5 V4`.
3. Dataset:
   `STAS5_ML_CORE/artifacts/v4/features/STAS5_V4_GROUP_RANK_TRAIN_DATASET_20260501_20260525.csv`; manifest `PASS`; rows `1710`; source rows `972` legacy `01..14` + `738` corrected V4 review `15..25`; corrected ledger join `738/738`; winners `103`; features `287`.
4. Guard:
   old `ML_KEEP_SCORE/ML_DECISION`, postfact/future/TP/Stas3/exit не попали в model features; V4 group features обязательны; `distance_to_best_low` и `minutes_to_best_low` сохранены только как audit label columns, не model features.
5. Training:
   model `STAS5_ML_CORE/artifacts/v4/model/runs/stas5_v4_train_20260714_163911/stas5_v4_group_ranker_20260501_20260525_v0.joblib`; OOF group metrics: `top1_group_accuracy=0.679612`, `winner_in_top2=0.834951`, `MRR=0.797006`, `NDCG@3=0.805523`, `BAD top1=15`; train-fit `top1=0.961165`.
6. Forward:
   run `STAS5_ML_CORE/artifacts/v4/forward/runs/stas5_v4_forward_20260526_20260530_20260714_164144`; totals `363` rows, `25` auto-groups, `ENTER=24`, `UNSURE=16`, `SKIP=323`; day ENTER counts: `4,5,5,5,5`.
7. Validation:
   `py_compile` passed for new V4 modules and modified renderer; dataset command `PASS`; training command completed; forward command completed; direct V4 smoke tests `3 PASS`; `pytest` unavailable in both Python environments; PNG `20260526` opened and visually nonblank.

### [2026-07-14T17:25:00Z] STAS5 V4 | NO-FUTURE AUDIT + V4L PLAN | DESIGN LOCKED

1. Пользователь зафиксировал правило: будущий состав группы тоже является future leakage. Модель на `entry_time_utc` может знать только прошлые свечи/признаки и уже появившихся кандидатов.
2. Текущий V4 train/forward помечен как `OFFLINE_GROUP_REVIEW_NOT_LIVE_SAFE`: он полезен как teacher/audit layer, но не как live/production model.
3. Обновлен `STAS5_ML_CORE/07_STAS5_V4_HUMAN_STYLE_GROUP_RANKER_TZ_RU.md`: добавлены `No-Future / Live-Safe`, live-safe vs audit-only features, guard `prefix invariance`.
4. Создан `STAS5_ML_CORE/08_STAS5_V4L_LIVE_SAFE_GROUP_RANKER_PLAN_RU.md`: live group state, `v4l_*_so_far` features, forbidden columns, adaptive micro-groups, decision policy, metrics and implementation steps.
5. Следующий шаг: V4L replay dataset и leakage guard до любого нового live-safe обучения.
8. Boundary:
   Forward `26..30` использует auto-groups for review. Следующий шаг - пользовательская визуальная проверка PNG и фиксация good/bad top1 внутри групп, если auto-group policy промахнулась.

## Session Log 2026-07-15 STAS5 V5 Day Ladder And Folder Audit

Сделана главная лесенка дня:

```text
STAS5_ML_CORE/run_stas5_v5_day_ladder.ps1
```

Режимы: `Collect`, `BuildApproved`, `Audit`, `Open`, `All`.

Проверки:

```text
2026-01-27 Stage All -NoPlot: PASS, rows=75, features=439, fcs=84
2026-01-28 Stage All: FULL274 найден, approved passport отсутствует, команда остановилась на ручном этапе
```

Сделан полный аудит V5-папки:

```text
src/mlbotnav/stas5_v5_folder_audit.py
STAS5_ML_CORE/run_stas5_v5_folder_audit.ps1
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715.json
```

Аудит: `PASS_V5_FOLDER_AUDIT_NO_TRAINING`, `full-ready=1`, `partial/not-ready=32`, `full274 runs=33`, `model=False`, `forward=False`.

Обучение и forward не запускались.

## Session Log 2026-07-15 STAS5 V5 Full Causal Market-Structure Builder

Сделан полный causal market-structure builder для V5:

```text
src/mlbotnav/stas5_v5_full_causal_structure_builder.py
STAS5_ML_CORE/run_stas5_v5_full_causal_structure_builder.ps1
```

Для дня `2026-01-27` создан текущий главный ML-ready пакет:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Счетчики: `75` строк, `439` feature columns всего: `355` признаков до full-слоя (`274 + cs_*`) и `84` новых `fcs_*` признака, `entry_y 1=11 / 0=64`.

Новые структурные артефакты:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_FULL_STRUCTURE_CANDIDATE_FEATURES_CAUSAL_V1.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_LEVELS_CAUSAL_V1.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_CHANNELS_CAUSAL_V1.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_REGIMES_CAUSAL_V1.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_EVENTS_CAUSAL_V1.csv
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/DAY_MARKET_PASSPORT_20260127_FULL_CAUSAL_STRUCTURE_MAP_V1.png
```

Guard:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_FULL_CAUSAL_STRUCTURE_GUARD_V1.json
```

Статус guard: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`. Обучение и forward не запускались.

Правило закреплено: ручной паспорт = `y`, causal builders = `X`; ручные фазы/причины/targets не входят в feature allowlist.

## 2026-07-14 STAS5 V4L live-safe implementation

1. Создан отдельный live-safe контур V4L: dataset/train/forward модули и wrapper `STAS5_ML_CORE/run_stas5_v4l_live_safe_train_forward.ps1`.
2. Dataset `2026-05-01..2026-05-25` собран с user-corrected `15..25`, включая `2026-05-15`: `1710` rows, `103` winners, `289` features.
3. Guard прошел: forbidden feature columns `{}`, prefix-invariance `1710/1710`, failures `0`.
4. Последний проверенный train run: `STAS5_ML_CORE/artifacts/v4l/model/runs/stas5_v4l_train_20260714_181635`.
5. Последний проверенный blind forward `2026-05-26..2026-05-30`: `STAS5_ML_CORE/artifacts/v4l/forward/runs/stas5_v4l_forward_20260526_20260530_20260714_181635`; totals `ENTER=23`, `UNSURE=80`, `SKIP=260`.
6. Зафиксировано: V4L не использует full-group low/rank/size, lower future candidate exists, day-end top-N и retroactive decision rewrite.

## 2026-07-15 STAS5 Day23 Pre-Knife Correction / V5 Pivot

1. Пользователь показал новый скрин `2026-05-23`: верхний красный прямоугольник перед ножом означает "тут покупать нельзя", нижняя зона после сброса означает "тут можно покупать".
2. Разбор сделан по оригинальным данным, не по пикселям скрина: V3 entries CSV, original PNG и OHLCV `data/core/bybit_ohlcv/dt=2026-05-23/tf=1m/symbol=SOLUSDT/part-final.csv`.
3. По свечам найден flush low: `2026-05-23T07:50:00Z`, `low=81.35`.
4. Создан новый ledger `STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V2_PRE_KNIFE.csv`; старый V1 не перезаписан.
5. В day23 V2 верхняя группа `LA001..LA016` переведена в `NO_TRADE_GROUP`; `LA007` больше не `BEST_GOOD`, `LA002/LA014` больше не `GOOD_ALT`; `LA022` остается `BEST_GOOD`, `LA025` остается `GOOD_ALT`, `LA033` остается `BEST_GOOD`.
6. Итог day23 V2: `63` rows, `BEST_GOOD=6`, `GOOD_ALT=2`, `BAD_IN_GROUP=27`, `NO_TRADE_GROUP=28`.
7. Создан V5 label-source `STAS5_ML_CORE/artifacts/v5/labels/STAS5_V5_ROW_LABEL_SOURCE_20260515_20260525_WITH_DAY23_PRE_KNIFE_V1.csv`; guard `PASS`, `738` rows, `11` days, duplicates `0`, counts `BEST_GOOD=63`, `GOOD_ALT=40`, `BAD_IN_GROUP=420`, `NO_TRADE_GROUP=215`.
8. Пользовательский архитектурный поворот зафиксирован: V4/V4L не использовать как финальную стратегию; следующий контур - V5 row-level ML по исправленным good/bad меткам без group-rank policy как торгового ограничения.
# Session 2026-07-15 STAS5 FULL274 Feature Collect Wrapper

Сделан отдельный запуск в `STAS5_ML_CORE`:

```text
STAS5_ML_CORE/run_stas5_full274_feature_collect.ps1
```

Проверка на `2026-04-01` прошла:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260401_20260715_084509/
rows=81
features=274
v1_features=111
v2_features=163
training_started=false
```

Также в `src/mlbotnav/stas5_v2_feature_visual_approval.py` CUT-маркеры и подписи LAxxx сделаны ярко-желтыми для читаемости. Обучение, API, TP/Stas3 не запускались.
## Session 2026-07-15 Codex CPU Load Check

Проверена жалоба на CPU-нагрузку Codex. Процессы не останавливались, файлы не удалялись, код не менялся.

Результат: Codex действительно является заметным участником нагрузки (`5.3%..9.2% CPU` по группе), но не единственным источником общего CPU. Найден повторяющийся `git diff --find-renames --numstat -z` от `Codex.exe`, а также краткие `git add -u`/`git add -A`; `git status` быстрый, `.git/index.lock` нет, `git diff --cached --name-only` пустой. Dirty worktree вырос до `1574` untracked files / `424.8 MB`, основной источник `STAS5_ML_CORE`.

Отчет: `docs/codex/CODEX_CPU_LOAD_CHECK_20260715_RU.md`.
# Session Log 2026-07-15 STAS5 V5 Causal Market-Structure Builder

Сделан отдельный causal market-structure builder для V5:

```text
src/mlbotnav/stas5_v5_causal_structure_builder.py
```

Для дня `2026-01-27` создан текущий ML-ready пакет:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Счетчики: `75` строк, `274` старых causal-признака, `81` новый `cs_*` признак, `355` feature columns всего, `entry_y 1=11 / 0=64`.

Guard:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_GUARD_V1.json
```

Статус guard: `PASS_NO_TRAINING_CAUSAL_STRUCTURE_READY`. Обучение и forward не запускались.

Обновлены навигация и аудит:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/00_OPEN_FIRST_RU.md
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/README_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_PROJECT_AUDIT_20260715_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_PROJECT_AUDIT_20260715.json
```

Правило закреплено: ручной паспорт = `y`, causal builder = `X`; ручные фазы/причины/targets не входят в feature allowlist.
## Session 2026-07-16 Codex Unload Applied

Пользователь попросил разгрузить Codex/CPU/память без удаления. Удалений не было, Codex не закрывался.

Сделано: приоритет `Codex`/`codex` понижен до `BelowNormal`; в `.gitignore` и `.vscode/settings.json` добавлены исключения для `STAS5_ML_CORE/artifacts/` и `STAS5_ML_CORE/runs/`. Untracked снизился с `1574` файлов / `424.8 MB` до `381` файла / `41.6 MB`. После финального контроля активных `git.exe` нет, `.git/index.lock` нет.

Отчет: `docs/codex/CODEX_UNLOAD_ACTION_20260716_RU.md`.

## Session 2026-07-16 Codex Idle Relief

Пользователь сообщил, что диск/память/CPU все еще двигаются в простое, и отдельно запретил трогать `STAS*`, особенно `STAS5` и `STAS6`. Удалений не было, `STAS*` не изменялись.

Сделано: остановлены read-only `git status --porcelain` и внутренний `git diff --find-renames --numstat -z`, подтверждено отсутствие `.git/index.lock` и активных `git.exe`; приоритет `Codex`/`codex`/`Code` понижен до `Idle`; остановлен отдельный VS Code OpenAI/Codex extension server `openai.chatgpt...\codex.exe app-server`.

Итог: опасного зависшего Git нет. Главный дисковый всплеск по процессным счетчикам дал `MsMpEng` (Microsoft Defender); Defender не отключался и настройки безопасности не менялись. Отчет: `docs/codex/CODEX_IDLE_RELIEF_20260716_RU.md`.
# Session Log 2026-07-17 STAS5 V5C Forward Charts Approved

Статус: `USER_APPROVED_V5C_FORWARD_VISUAL_REVIEW_CHARTS_OK`.

Пользователь подтвердил, что текущие V5C forward графики выглядят нормально. Зафиксировано: visual-standard принят для дальнейшей ручной оценки входов.

Текущий утвержденный набор:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343/visual_review/
```

Границы утверждения: подтвержден именно формат графиков и WAVE-перенос. Обучение, forward predictions, scores, decisions и X439 не менялись. Следующий смысловой шаг: ручной review `62 ENTER` на утвержденных графиках.

# Session Log 2026-07-16 STAS5 V5C WAVE Strip Cumulative Carry Fix

Статус: `PASS_V5C_FORWARD_VISUAL_REVIEW_WAVE_CUMULATIVE_CARRY_NO_BLACK_TAIL`.

По запросу пользователя доработан V5C forward visual review: WAVE-полоса больше не оставляет черный хвост перед следующим днем. Последняя active `LONG/SHORT` волна растягивается до `available_end_utc`, а cross-day подписи используют cumulative percent от настоящего старта волны.

Изменения:

```text
src/mlbotnav/stas5_v5_forward_visual_review.py
tests/test_stas5_v5_forward_visual_review.py
```

Результат текущего run:

```text
run=STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343
png_count=14
tail_gap_rows_filled_total=7
tail_gap_minutes_filled_total=298.0
rendered_gap_rows_total=0
cross_day_wave_rows_total=13
max_visible_to_cumulative_pct_delta=1.941868
```

Проверки:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v5_forward_visual_review.py tests\test_stas5_v5_forward_visual_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v5_forward_visual_review.py -q
# 1 passed

$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas2_market_phase_review.py -q
# 4 passed

.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode RenderForward -ForwardRunId stas5_v5c_continuous_forward_20260228_20260306_20260716_155343 -ForwardStartDay 2026-02-28 -ForwardEndDay 2026-03-06
# PASS, png_count=14
```

SHA256 predictions CSV до/после render совпал: обучение, scores, decisions и forward predictions не менялись.

# Session Log 2026-07-16 STAS5 V5C Forward Visual Review Continuous Strip

Статус: `PASS_V5C_FORWARD_VISUAL_REVIEW_WITH_CONTINUOUS_STRENGTH_STRIP`.

По запросу пользователя доработан текущий V5C forward visual review: в overview добавлен блок `Fon / LONG / SHORT / WAVE` между price и score. Существующие подписи и маркеры сохранены: `LAxxx`, желтые X, желтые ромбы, зеленые треугольники. Длинные ENTER-боксы/стрелки на overview не возвращались.

Изменения:

```text
src/mlbotnav/stas5_v5_forward_visual_review.py
tests/test_stas5_v5_forward_visual_review.py
```

Контроль непрерывности: renderer ищет `run_dir/ohlcv_contexts` и для 7/7 forward-дней использует `CONTINUOUS_CONTEXT_OHLCV` по `2160` строк на день. Служебные `GAP`-сегменты в WAVE фильтруются до отрисовки: `filtered_gap_rows_total=7`, `rendered_gap_rows_total=0`; направления WAVE только `LONG/SHORT`.

Проверки:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v5_forward_visual_review.py tests\test_stas5_v5_forward_visual_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v5_forward_visual_review.py -q
# 1 passed

.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode RenderForward -ForwardRunId stas5_v5c_continuous_forward_20260228_20260306_20260716_155343 -ForwardStartDay 2026-02-28 -ForwardEndDay 2026-03-06
# PASS, png_count=14
```

Дополнительно проверен SHA256 predictions CSV до/после render: hash совпал, значит `ENTRY_ML_LIVE_SCORE` и `ENTRY_ML_LIVE_DECISION` не менялись. Обучение и новый forward не запускались.

# Session Log 2026-07-16 STAS5 V5C Continuous Train + Blind Forward

Статус: `PASS_V5C_CONTINUOUS_TWO_BLOCK_FORWARD_20260228_20260306_BLIND_NO_FUTURE`.

По запросу пользователя реализован отдельный непрерывный контур `V5C_CONTINUOUS`, чтобы обучение и forward не сбрасывали структуру рынка на границе дня. Старый дневной V5 не перезаписан.

Изменения:

```text
src/mlbotnav/stas5_v5_continuous_ml.py
STAS5_ML_CORE/run_stas5_v5c_continuous_train_forward.ps1
tests/test_stas5_v5_continuous_ml.py
src/mlbotnav/stas5_v5_batch_dataset_builder.py
src/mlbotnav/stas5_v5_two_block_ml.py
```

Контекст: rolling continuous warmup `720` минут. Контроль midnight-reset: первый forward-кандидат `2026-02-28 LA001` имеет `cs_context_rows=748`, `cs_rows_240m=240`, `fcs_context_before_entry=1`.

Результаты:

```text
V5C batch: rows=2596, entry_y 1=290 / 0=2306, features=439, guard PASS
V5C train: stas5_v5c_continuous_train_20260716_154826, post-train guard PASS
OOF baseline ROC-AUC=0.6569167389418907 PR-AUC=0.17950987215851025
OOF two-block ROC-AUC=0.6597878099111762 PR-AUC=0.18064179174496617
V5C forward: stas5_v5c_continuous_forward_20260228_20260306_20260716_155343
forward rows=576, ENTER=62 / WATCH=121 / SKIP=393
visual review PASS, png_count=14
```

Проверки:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests/test_stas5_v5_batch_dataset_builder.py tests/test_stas5_v5_two_block_ml.py tests/test_stas5_v5_forward_visual_review.py tests/test_stas5_v5_continuous_ml.py -q
# 5 passed

.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode BuildBatch -ContextWarmupMinutes 720
# PASS

.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode Train -ContextWarmupMinutes 720
# PASS

.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode Forward -ContextWarmupMinutes 720
# PASS
```

Предупреждения: pandas `PerformanceWarning` при сборке широких таблиц и sklearn `ConvergenceWarning`/runtime warnings для быстрого `SGDClassifier`, как и в дневном V5. Это не сломало guards; вероятности нормализуются. Следующий шаг: визуально проверить `62 ENTER` и сравнить V5C с дневным V5.

## 2026-07-17 STAS5 V5C R2 Review 2026-02-28 Closed

Пользователь подтвердил финальную разметку `2026-02-28`. Сохранены review-ledger файлы в `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260228/`.

GOOD ids: `LA022, LA023, LA032, LA035, LA043, LA047, LA052, LA062, LA067, LA068`. Явные BAD для аудита: `LA014`, `LA024`, `LA039`, `LA076`.

Запущена команда без training и без нового forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-02-28 -Stage All -GoodIds LA022,LA023,LA032,LA035,LA043,LA047,LA052,LA062,LA067,LA068
```

Итог дневного package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260228/
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=81
entry_y 1=10 / 0=71
features=439
cs/fcs source-time violations=0
duplicates=0
```

Граница: R2 training не запускался. День `2026-02-28` теперь является teacher-разметкой для будущего R2 и не должен использоваться как независимый blind-proof после переобучения.

## 2026-07-17 STAS5 V5C R2 Review 2026-03-01 Closed

Пользователь дал разметку `2026-03-01`. Сохранены review-ledger файлы в `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260301/`.

GOOD ids: `LA002, LA005, LA012, LA033, LA044, LA048, LA055, LA071, LA075`. Явные BAD для аудита: `LA011`, `LA029`, `LA050`, `LA053`, `LA065`, `LA066`, `LA068`, `LA069`.

Запущена команда без training и без нового forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-01 -Stage All -GoodIds LA002,LA005,LA012,LA033,LA044,LA048,LA055,LA071,LA075
```

Итог дневного package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260301/
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=81
entry_y 1=9 / 0=72
features=439
cs/fcs source-time violations=0
duplicates=0
```

Граница: R2 training не запускался. Закрытые teacher-дни для будущего R2: `2026-02-28`, `2026-03-01`.

## 2026-07-17 STAS5 V5C R2 Review 2026-03-02 Closed

Пользователь дал разметку `2026-03-02`. Сохранены review-ledger файлы в `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260302/`.

GOOD ids: `LA006, LA025, LA027, LA028, LA049, LA051, LA052, LA053, LA057, LA063, LA067, LA070`. Явный BAD для аудита: `LA010`.

Запущена команда без training и без нового forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-02 -Stage All -GoodIds LA006,LA025,LA027,LA028,LA049,LA051,LA052,LA053,LA057,LA063,LA067,LA070
```

Итог дневного package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260302/
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=81
entry_y 1=12 / 0=69
features=439
cs/fcs source-time violations=0
duplicates=0
```

Граница: R2 training не запускался. Закрытые teacher-дни для будущего R2: `2026-02-28`, `2026-03-01`, `2026-03-02`.

## 2026-07-17 STAS5 V5C R2 Review 2026-03-03 Closed

Пользователь дал разметку `2026-03-03`. Сохранены review-ledger файлы в `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260303/`.

GOOD ids: `LA006, LA007, LA043, LA045, LA055, LA060, LA062, LA066, LA067, LA072, LA082, LA083`. Явные BAD для аудита: `LA005`, `LA009`, `LA023`, `LA028`, `LA035`, `LA054`, `LA057`, `LA059`, `LA080`.

Запущена команда без training и без нового forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-03 -Stage All -GoodIds LA006,LA007,LA043,LA045,LA055,LA060,LA062,LA066,LA067,LA072,LA082,LA083
```

Итог дневного package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260303/
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=89
entry_y 1=12 / 0=77
features=439
cs/fcs source-time violations=0
duplicates=0
```

Граница: R2 training не запускался. Закрытые teacher-дни для будущего R2: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`.

## 2026-07-17 STAS5 V5C R2 Review 2026-03-04 Closed

Пользователь дал разметку `2026-03-04`. Сохранены review-ledger файлы в `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260304/`.

GOOD ids: `LA014, LA019, LA020, LA022, LA034, LA040, LA047, LA051, LA071`. Явные BAD для аудита: `LA006`, `LA009`, `LA026`.

Запущена команда без training и без нового forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-04 -Stage All -GoodIds LA014,LA019,LA020,LA022,LA034,LA040,LA047,LA051,LA071
```

Итог дневного package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260304/
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=72
entry_y 1=9 / 0=63
features=439
cs/fcs source-time violations=0
duplicates=0
```

Граница: R2 training не запускался. Закрытые teacher-дни для будущего R2: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`, `2026-03-04`.

## 2026-07-17 STAS5 V5C R2 Review 2026-03-05 Closed

Пользователь дал разметку `2026-03-05`. Сохранены review-ledger файлы в `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260305/`.

GOOD ids: `LA008, LA023, LA030, LA035, LA049, LA053, LA054, LA059, LA064, LA065, LA067`. Явные BAD для аудита: `LA055`, `LA058`, `LA081`.

Запущена команда без training и без нового forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-05 -Stage All -GoodIds LA008,LA023,LA030,LA035,LA049,LA053,LA054,LA059,LA064,LA065,LA067
```

Итог дневного package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260305/
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=85
entry_y 1=11 / 0=74
features=439
cs/fcs source-time violations=0
duplicates=0
```

Граница: R2 training не запускался. Закрытые teacher-дни для будущего R2: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`, `2026-03-04`, `2026-03-05`.

## 2026-07-17 STAS5 V5C R2 Review 2026-03-06 Closed

Пользователь дал разметку `2026-03-06`. Сохранены review-ledger файлы в `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260306/`.

GOOD ids: `LA006, LA023, LA028, LA047, LA055, LA066`. Явные BAD для аудита: `LA019`, `LA050`, `LA051`, `LA053`, `LA054`, `LA059`, `LA062`, `LA072`, `LA078`.

Спорное место `72/73` проверено по source predictions: `LA072=ENTER`, `LA073=WATCH`; как плохой зеленый треугольник зафиксирован `LA072`.

Запущена команда без training и без нового forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-06 -Stage All -GoodIds LA006,LA023,LA028,LA047,LA055,LA066
```

Итог дневного package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260306/
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=87
entry_y 1=6 / 0=81
features=439
cs/fcs source-time violations=0
duplicates=0
```

Граница: R2 training не запускался. Закрыта вся teacher-неделя `2026-02-28..2026-03-06`; следующий шаг - R2 batch dataset и отдельный R2 batch guard, не обучение напрямую.

## 2026-07-17 STAS5 V5C R2 Text Encoding Fix

Пользователь попросил исправить кракозябы во всех днях. Проведен аудит R2 review-слоя. Реальные повреждения найдены в `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260302..20260306/`: в `user_reason_ru` и RU-md отчетах были question-mark placeholders.

Перезаписаны UTF-8 review-ledger файлы для всех закрытых дней `2026-02-28..2026-03-06`: CSV, JSON и RU.md. Метки не менялись.

Контроль:

```text
review text audit=PASS, total_hits=0
label audit=PASS
days=7
training=false
forward=false
```

Отчет: `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/STAS5_V5C_R2_TEXT_ENCODING_AUDIT_20260717_RU.md`.

## 2026-07-17 STAS5 V5C R3 Batch Guard Ready

Пользователь подтвердил, что продиктованные правки за `2026-03-07..2026-03-13` нужно внедрять без повторного переспроса. Approved review-ledger уже создан в `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/`, дневные V5 passports пересобраны по GoodIds.

Контроль дневных пакетов:

```text
20260307 rows=74 GOOD=9
20260308 rows=78 GOOD=10
20260309 rows=86 GOOD=12
20260310 rows=74 GOOD=9
20260311 rows=77 GOOD=12
20260312 rows=88 GOOD=12
20260313 rows=77 GOOD=9
```

Собран непрерывный R3 batch без training и без forward:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_ML_READY_439F_TARGETS_V1.csv
rows=3726
entry_y 1=432
entry_y 0=3294
days=46
features=439
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
```

Дополнительный контроль: все GoodIds за `2026-03-07..2026-03-13` совпали с дневными CSV; кракозяб в `r3_user_review` не найдено; markers training/forward в новых daily packages не найдены. Следующий шаг - пользователь запускает R3 `TrainingGuard`, затем после PASS отдельно `Train`.
# 2026-07-20 STAS5 V5C RiskGate Audit-Only Implemented

По подтверждению пользователя RiskGate зафиксирован как отдельный audit-only режим. Добавлен модуль `src/mlbotnav/stas5_v5c_riskgate_audit.py`, тест `tests/test_stas5_v5c_riskgate_audit.py`, PowerShell mode `RiskGate` в `STAS5_ML_CORE/run_stas5_v5c_continuous_train_forward.ps1`.

Главный YAML обновлен: `RISK_GATE_RULE_V0.enabled=true`, `mode=audit_only`, `implementation_status=IMPLEMENTED_AUDIT_ONLY`, enforce запрещен без отдельного guard.

Проверка на `2026-03-18` с `LA059,LA067,LA078`:

```text
status=PASS_V5C_RISKGATE_AUDIT_ONLY_READY
ENTER=15
BLOCK_HARD=6
BLOCK_RISK=3
WARN_RISK=3
PASS_USER_REBOUND=3
```

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5c_riskgate_audit.py tests/test_stas5_v5_forward_visual_review.py` = `4 passed`; контрольный RiskGate command `PASS`, `RISK_NO_FUTURE_OK=True`; UTF-8 audit `PASS`.

# 2026-07-20 STAS5 V5C RiskGate Preview 2026-03-18

Создан отдельный audit-only preview RiskGate V0 для R3 forward day `2026-03-18`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_V0.png
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_V0.csv
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_RU.md
```

Итог по `ENTER`: `15`, из них `BLOCK_HARD=8`, `BLOCK_RISK=3`, `WARN_RISK=4`, `PASS_RISK=0`. Predictions/model/train не менялись, enforce не включался.

Пользователь отметил три проходящих входа на PNG: `LA059`, `LA067`, `LA078`. Создана V1-копия:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_V1_USER_PASS.png
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_V1_USER_PASS.csv
```

V1 adjusted: `BLOCK_HARD=6`, `BLOCK_RISK=3`, `WARN_RISK=3`, `PASS_USER_REBOUND=3`. Вывод: будущий RiskGate должен иметь исключения `GOOD_REBOUND/GROUNDING/RETEST`, иначе он будет душить хорошие входы после дампа.
## 2026-07-20 STAS5 V5C Review Overlay Fix

По замечанию пользователя `*_ALL_ENTRIES.png` оказался чистой копией без видимых пометок команды. Добавлен и пересобран `*_ANNOTATED.png`: основной V5C-график сохраняет все LA, score/volume и полосы `Fon/LONG/SHORT/WAVE`, а поверх цены подсвечивает `GOOD/BAD/RISK BAD`.

Контрольный пример пересобран для `2026-03-18`: `STAS5_ML_CORE/artifacts/v5c/review/r4_user_review/20260318/STAS5_V5C_R4_USER_REVIEW_20260318_APPROVED_ANNOTATED.png`. Визуально проверено: видны `LA014 BAD`, `LA022 GOOD`, `LA047 GOOD`, `LA040 RISK BAD`. Training/forward не запускались.

Дополнительная правка по шуму: из `*_ANNOTATED.png` убраны индивидуальные стрелки и плашки возле точек. Новый стиль: `GOOD` зеленый круг, `RISK BAD` ярко-красный круг, обычный `BAD` красный квадрат; справа сверху только компактная легенда-счетчик. `2026-03-18` пересобран по текущей R4-разметке: GOOD `LA002,LA023,LA059,LA060,LA067,LA078`; BAD `LA016,LA019`; RISK BAD `LA040,LA042,LA043,LA047,LA049,LA054,LA055,LA058`.
## 2026-07-21 STAS5 V5C Dataset Rails Locked

Зафиксирован config/doc stage `REVIEW_PACK_DATASET_RAILS_LOCKED_NO_TRAINING`.

Обновлены:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
docs/codex/handoff.md
docs/codex/current_state.md
docs/codex/todo.md
docs/codex/known_errors.md
docs/codex/commands.md
```

Суть фиксации: base `2026-01-27..2026-02-27` + approved review-pack `2026-02-28..2026-03-20` должны идти в следующий builder как `X439_SOURCE`, `ENTRY_TRAIN_DATASET`, `RISKGATE_TRAIN_DATASET`. Training/forward не запускались.

## 2026-07-21 STAS5 V5C Safety Pulse Preview

Сделан быстрый test-drive safety pulse поверх готового forward `2026-03-21..2026-03-27`, без обучения и без пересборки forward. Добавлен модуль `src/mlbotnav/stas5_v5c_safety_pulse_preview.py` и wrapper `STAS5_ML_CORE/run_stas5_v5c_safety_pulse_preview.ps1`.

Результат сравнения: текущий `RISKGATE_ML` дает `ENTER=34`, но пропускает опасные taxonomy-режимы; `BALANCED_SAFETY_V1` слишком жесткий (`ENTER=3`); `HARD_BLOCK_ONLY_V1` выглядит как следующий кандидат для визуального согласования (`ENTER=27`, `WATCH=138`, `SKIP=399`).

Проверки: `py_compile` PASS, профильные pytest `20 passed`.
# 2026-07-22 STAS5 V5C Bollinger Layer V1 X463

Статус: `PASS_V5C_BOLLINGER_LAYER_V1_X463_DATASETS_AND_REVIEW_GALLERY_READY_NO_TRAINING`.

Сделано:

- добавлен общий causal-модуль `src/mlbotnav/stas5_v5c_bollinger_layer.py`;
- `run_stas5_v5c_train_dataset_builder.ps1 -EnableBollingerLayer -Force` собрал ENTRY/RiskGate train datasets с `463` features;
- ENTRY: `rows=3285`, `GOOD=517`, `BAD=2768`, guard PASS;
- RiskGate: `rows=627`, `risk_bad_y=1=400`, `risk_bad_y=0=227`, guard PASS;
- ENTRY TrainingGuard PASS: `STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/`;
- RiskGate ML TrainingGuard PASS в том же run;
- R2/R3/R4 Bollinger gallery собрана в `STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA/`;
- обучение и forward не запускались.

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5c_bollinger_layer.py tests/test_stas5_v5c_train_dataset_builder.py -q` = `2 passed`; JSON config valid.

## Session 2026-07-22 Codex Update Load Audit

Пользователь попросил проверить и разгрузить Codex после обновления. Удалений не было, папки проекта и `STAS*` не изменялись.

Подтвержден пакет `OpenAI.Codex_26.715.10079.0`. Найдено ключевое отличие: основная оболочка Codex теперь идет как `ChatGPT.exe`, поэтому прежняя разгрузка только `Codex`/`codex` пропускала renderer/gpu. Найден и остановлен отдельный VS Code OpenAI/Codex extension server `openai.chatgpt-26.715.31925...\codex.exe app-server`.

Приоритеты `ChatGPT`/`codex`/`Code`/`node_repl` понижены до `Idle`. Финальный контроль: активных `git.exe` нет, `.git/index.lock` нет, VS Code extension server не активен, системный CPU `3.9..9.7%`, Disk Time `0.8..10.4%`, чтение диска `0`, свободная память `13.5..13.7 GB`. Отчет: `docs/codex/CODEX_UPDATE_LOAD_AUDIT_20260722_RU.md`.

## Session 2026-07-23 Codex VS Code Fix

Пользователь показал ошибку панели VS Code `Работа Codex неожиданно остановлена` и попросил аккуратно починить Codex в VS Code.

Проверено: основной Desktop Codex работал через `OpenAI.Codex_26.715.10079.0`, но VS Code extension server `openai.chatgpt-26.715.31925...\codex.exe app-server` отсутствовал. Через UI Automation нажата штатная кнопка `Перезапустить`; сервер расширения поднялся. Приоритеты `ChatGPT`/`codex` выставлены в `Idle`. После короткой стартовой прогрузки VS Code Codex server успокоился до `0% CPU` и `0` I/O ops/s. Удалений не было, `STAS*` и `config.toml` не изменялись. Отчет: `docs/codex/CODEX_VSCODE_FIX_20260723_RU.md`.

## Session 2026-07-23 STAS9 Shortcut And CPU Fix

Пользователь сообщил, что ярлык STAS9 снова открыл отдельный терминал, и показал повышенную нагрузку CPU.

Диагностика выявила два похожих ярлыка: новый `STAS9 Assistant` вёл в VS Code, старый `STAS9 Главный агент` — в `start_STAS9.bat`. Точное дерево старого терминального запуска остановлено. Оба ярлыка перенаправлены на `Code.exe` с открытием `MLbotNav_STAS9.code-workspace`. Контроль старого по имени ярлыка открыл VS Code и не создал terminal launcher.

Добавлена лёгкая активация STAS9 и усилены фоновые исключения Git/Pylance. Чистый десятисекундный замер после запуска: `Code ~1.56% CPU`, все процессы `codex ~0.10% CPU`. На исходном снимке основная нагрузка приходилась на Defender и WMI; системные службы не отключались. STAS5–STAS8 не изменялись. Отчёт: `STAS9_CONTROL_PLANE/REPORTS/STAS9_SHORTCUT_CPU_FIX_REPORT_RU.md`.
