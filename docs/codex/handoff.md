# Handoff

## Handoff 2026-07-23 SOL Event Contract and Dry-Run Pipeline

Статус:
`PASS_SOL_EVENT_SCHEMA_DRY_RUN_NO_EVENTS_NO_DATASET_PROTECTED_UNCHANGED`.

Единственный source закреплён как
`data/core/bybit_ohlcv`: Bybit linear, `SOLUSDT`, `1m`, `ohlcv_v1`.
Повторная потоковая проверка: `126` CSV, `181440` уникальных минут,
`2026-01-26 00:00..2026-05-31 23:59 UTC`, дублей/разрывов/нарушений OHLCV
нет.

Созданы `MARKET_KNOWLEDGE/EVENT_SCHEMA_RU.md`,
`MARKET_KNOWLEDGE/EVENTS/SOL/README_RU.md` и отчёт
`REPORTS/SOL_EVENT_PIPELINE_DESIGN_RU.md`. Контракт разделяет причинные
context/features, future outcome, label и lineage. Подготовлены девять event
types.

In-memory pipeline `SOL_OHLCV_TO_EVENT_SCHEMA_DRY_RUN_V1` завершён
`PASS_DRY_RUN_NO_EVENT_RECORDS`: event YAML `0`, datasets `0`.
`STAS5_ML_CORE`, вложенный STAS8, source CSV, `data` и `models` не изменены.
Обучение, Optuna, forward и live trading не запускались. Финальный режим:
`SAFE / READ_ONLY`.

## Handoff 2026-07-23 STAS9 VS Code On-Demand Workflow

Статус:
`PASS_STAS9_VSCODE_CODEX_ON_DEMAND_SAFE_PROTECTED_UNCHANGED`.

STAS9 закреплён как управляющая роль внутри Codex, а не как постоянный
фоновый процесс. Основной вход:

```text
C:\Users\007\Desktop\🤖 STAS9 Workspace.lnk
-> MLbotNav_STAS9.code-workspace
-> VS Code + Codex
-> STAS9_SENTINEL по команде пользователя
```

Конфигурация: `CODEX_ROLE`, `ON_DEMAND`, `USER_COMMAND_ONLY`,
`SAFE + READ_ONLY`, idle `NONE`; автозапуск агентов, watcher и folder scan
отключены. Console launcher сохранён только как диагностический резерв.

Проверки: workspace JSON и YAML `PASS`; shortcut target/argument `PASS`;
постоянные STAS9/Python/Optuna/rg процессы, автозагрузка, службы и планировщик
не найдены. Metadata fingerprints `STAS5_ML_CORE` (`6196` файлов), `data`
(`1662`) и `models` (`6048`) совпали до/после.

Отчёт:
`STAS9_CONTROL_PLANE/REPORTS/STAS9_VSCODE_WORKFLOW_SETUP_RU.md`.

## Handoff 2026-07-23 STAS9 Agent Roles and SOL ML Preparation

Статус:
`PASS_STAS9_AGENT_ROUTING_SOL_ML_PREPARATION_SAFE_NO_TRAINING`.

В `STAS9_CONTROL_PLANE` создана явная система ролей и маршрутизации. Добавлен
новый `STAS9_MARKET_RESEARCH` для read-only исследования существующих свечей
SOL. Sentinel классифицирует и делегирует задачи, контролирует результат,
обновляет память и формирует итог, но не подменяет профильных агентов.

Созданы `AGENT_ROLES/`, `TASK_ROUTER_RU.md`,
`MEMORY/AGENT_RESPONSIBILITIES.yaml`, `MARKET_KNOWLEDGE/`,
`DATASET_BUILDER/` и `STAS9_AGENT_SETUP_REPORT_RU.md`. `STAS9_LAB` сохранён
как вспомогательный агент только для явно подтверждённых экспериментов.

Проверки: YAML `31/31`, агенты `8x4`, реестр `8/8`, делегирования `7/7`,
машинные маршруты `11/11`, документы ролей `7/7`, SOL event/dataset contracts
`PASS`.

STAS5 и вложенный STAS8 не изменены: metadata fingerprint до/после одинаков,
`6196` файлов,
SHA256 `40ceeb41c5562eb8b64d31dae1f2abb91caad9da40be6e294715c161d51d1445`.
Обучение, Optuna, forward, изменение моделей, live trading, удаления и
переносы не выполнялись.

Отчёт: `STAS9_CONTROL_PLANE/STAS9_AGENT_SETUP_REPORT_RU.md`.

## Handoff 2026-07-23 STAS9 Persistent Control-Plane Memory

Статус: `PASS_STAS9_PERSISTENT_MEMORY_AND_NEW_CHAT_ENTRY_READY_PROTECTED_UNCHANGED`.

Проверена текущая архитектура STAS9: Codex является исполняющей средой,
`STAS9_SENTINEL` — единой управляющей ролью, а `STAS9_CONTROL_PLANE` —
постоянным слоем состояния, правил, реестров и журналов.

Созданы:

```text
STAS9_CONTROL_PLANE/MEMORY/STAS9_STATE.md
STAS9_CONTROL_PLANE/START_HERE_RU.md
```

В памяти зафиксированы текущий статус, `SAFE`, семь агентов, правила,
известные ограничения и последние действия. Инструкция нового чата содержит
стартовый prompt и отдельные шаблоны для `SAFE`, `DEVELOPMENT` и
`EXPERIMENT`.

Проверки: оба Markdown-файла существуют и читаются как UTF-8, каталог агентов
содержит `7` конфигураций. STAS5–STAS8 не изменялись; обучение, Optuna,
forward и live trading не запускались.

## Handoff 2026-07-23 STAS9 VS Code/Codex Interface

Статус: `PASS_STAS9_VSCODE_CODEX_INTERACTIVE_ASSISTANT_READY_PROTECTED_UNCHANGED`.

Основной пользовательский вход STAS9 перенесён в VS Code/Codex без удаления технического terminal launcher:

```text
C:\Users\007\Desktop\🤖 STAS9 Assistant.lnk
-> MLbotNav_STAS9.code-workspace
-> VS Code + openai.chatgpt
-> STAS9_SENTINEL
```

Созданы `STAS9_INTERFACE`, `CODEX_INSTRUCTIONS_RU.md`, три режима `SAFE/DEVELOPMENT/EXPERIMENT`, формат ответа и журнал диалогов. Голосовой ввод в VS Code использует русскую системную диктовку Windows `Win+H`; Sentinel получает и журналирует отправленный текст, но не записывает аудио.

Проверки: workspace JSON `PASS`, YAML `23/23`, расширение `openai.chatgpt@26.715.31925`, shortcut target `PASS`, Sentinel response smoke `PASS`.

STAS5/STAS8 не изменены: `6196` файлов, SHA256 `e2b12f074d2a658582e85d671d0a4758c6f98875521a2da9f3849a51d1b56543`.

Отчёт: `STAS9_CONTROL_PLANE/REPORTS/STAS9_VSCODE_INTERFACE_SETUP_RU.md`.

## Handoff 2026-07-23 STAS9 Codex CLI Update

Статус: `PASS_CODEX_CLI_0_145_0_STAS9_MODEL_READY_PROTECTED_UNCHANGED`.

Глобальный npm-пакет `@openai/codex` обновлён с `0.142.5` до `0.145.0`. Эта версия совпадает с текущей версией npm registry.

Проверки:

1. `codex doctor --summary`: exit `0`, install/auth/network `PASS`, fail `0`;
2. `start_STAS9.bat --check`: exit `0`, `PRIMARY_ONLY_READ_ONLY`;
3. одноразовый `codex exec --ephemeral` для `gpt-5.6-sol`, `xhigh`, `read-only`: ответ `STAS9_MODEL_OK`;
4. `STAS5_ML_CORE`: `6196` файлов, content-tree SHA256 не изменился — `e2b12f074d2a658582e85d671d0a4758c6f98875521a2da9f3849a51d1b56543`.

## Handoff 2026-07-23 STAS9 Multi-Agent Control Layer

Статус: `PASS_STAS9_MULTI_AGENT_CONTROL_LAYER_READY_PROTECTED_VERSIONS_UNCHANGED`.

Созданы `STAS9_SENTINEL` и шесть специализированных агентов. Каждый агент имеет `README_RU.md`, `ROLE_RU.md`, `CONFIG.yaml`, `PERMISSIONS.yaml`; режим по умолчанию — `READ_ONLY`. Добавлены общая конфигурация, глобальная политика, память, три журнала, launcher и ярлык `C:\Users\007\Desktop\🤖 STAS9 Главный агент.lnk`.

Launcher стартует только `STAS9_SENTINEL`; остальные агенты имеют режим `ON_DEMAND`. Самопроверка launcher, YAML и структуры прошла.

Защищённое дерево `STAS5_ML_CORE`, включая вложенные артефакты STAS8, не изменилось: `6196` файлов, content-tree SHA256 до/после `e2b12f074d2a658582e85d671d0a4758c6f98875521a2da9f3849a51d1b56543`.

Отчёт: `STAS9_CONTROL_PLANE/REPORTS/STAS9_SETUP_REPORT_RU.md`.

## Handoff 2026-07-23 STAS9 Multi-Agent Structure

Статус: `PASS_STAS9_DIRECTORY_STRUCTURE_READY_LEGACY_UNCHANGED`.

В существующем `STAS9_CONTROL_PLANE/` создан каркас многоагентной управляющей системы:

1. `STAS9_AGENTS/` и семь каталогов агентов;
2. `MEMORY/`, `LOGS/`, `REPORTS/`, `RUNTIME/`, `CONFIG/`, `PERMISSIONS/`, `START/`.

Проверка структуры: `15/15` каталогов, пропусков и лишних каталогов нет. Корневые `STAS6` и `STAS7` отсутствовали и не создавались. `STAS5_ML_CORE` до и после операции содержит `6196` файлов; контрольный metadata SHA-256 совпал: `571e793ff2d6c6b3677ef2b8e9a07b7adf5d4ee1db300d4ea8a6ccf322e01cd9`.

## Handoff 2026-07-23 STAS9 Control Plane Audit Baseline

Статус: `PASS_STAS9_CONTROL_PLANE_REGISTRIES_READY_NO_TRAINING_NO_FORWARD_STAS5_STAS8_UNCHANGED`.

Создан новый управляющий каталог `STAS9_CONTROL_PLANE/` с картой STAS1–STAS8, реестром моделей, реестром feature contracts, полным реестром `142` технических заданий, архивной политикой и предложением архитектуры STAS9.

Ключевые выводы:

1. самостоятельные STAS6 и STAS7 в проекте не обнаружены;
2. STAS8 вложен в STAS5 и остается выключенным audit-preview;
3. в `models/pipeline` есть `6043` joblib: `4381` logreg, `775` lightgbm, `887` xgboost;
4. старый candidates registry содержит `6496` записей, `260` повторов и `193` уникальные ссылки на отсутствующие файлы;
5. `models/registry/active_model.json` и `champion.json` указывают на отсутствующий joblib и помечены в STAS9 как `BROKEN_POINTER`;
6. зарегистрированы все `37` физически существующих STAS5 joblib;
7. текущий внутренний STAS5 latest run — `stas5_v5c_r4bb_train_20260127_20260320`, X463;
8. STAS5–STAS8 не изменялись: metadata fingerprint до/после совпал, `6196` файлов, SHA256 `367301aa69b966a588fb078f8ff3ee4fd6fa109b688bc848fdeb6154d2f6a506`.

Проверки:

```text
YAML parse PASS
STAS5 model paths 37/37 exist
legacy model collection counts PASS
TASK_REGISTRY rows 142/142
mojibake scan PASS
STAS5 metadata fingerprint unchanged
```

Следующий рекомендуемый шаг: утвердить предложенную read-only архитектуру STAS9, затем отдельным ТЗ реализовать схемы реестров и проверки pointers/lineage. Старый champion pointer автоматически не исправлять.

## Handoff 2026-07-23 Codex Project CPU Relief

Статус: `PASS_CODEX_PROJECT_CPU_RELIEF_APPLIED_NO_DELETE_NO_TRAINING`.

Причина нагрузки найдена: Codex Desktop циклически считал Git diff/hash по `258` неигнорируемым generated-файлам `STAS4_FEATURE_HYPOTHESIS_REVIEW`; Defender повторно сканировал те же данные. Python/ML-процессов не было.

В `.gitignore` точечно исключены подпапки и PNG STAS4 review, а в `.vscode/settings.json` папка исключена из watcher/search/Pylance. Файлы не удалялись. После правки STAS4 Git-хвост сократился до двух верхних Markdown-файлов, `codex.exe` снизился примерно с `9%` до `0.03%`, общий CPU стабилизировался в диапазоне `10.0..13.6%`.

Отчет: `docs/codex/CODEX_PROJECT_CPU_RELIEF_20260723_RU.md`.

## Handoff 2026-07-22 STAS5 V5 Base R2-Style Review Gallery

Статус: `PASS_V5_BASE_R2_STYLE_REVIEW_GALLERY_READY_NO_TRAINING_NO_FORWARD`.

База `2026-01-27..2026-02-27` пересобрана в обычный визуальный формат, близкий к R2/R3/R4: свечи, все LA, `entry_y=1` как зеленый треугольник `ENTER`, `entry_y=0` как желтый `X/SKIP`, teacher overlay `GOOD` зеленым кругом и `BAD` красным квадратом. RiskGate в базовой галерее не рисуется. Обучение и forward не запускались.

Итог: `32` дня, `2596` rows, `GOOD=290`, `BAD=2306`, PNG всего `65` (`32` all_entries + `32` current_review + contact sheet).

Папка:

```text
STAS5_ML_CORE/artifacts/v5c/review/_BASE_R2_STYLE_VISUAL_REVIEW_20260127_20260227
```

Команда пересборки:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_base_review_gallery.ps1 -StartDay 2026-01-27 -EndDay 2026-02-27 -OpenFolder
```

## Handoff 2026-07-22 STAS5 V5C Entry Visual Check Pack

Статус: `PASS_ENTRY_VISUAL_CHECK_PACKAGE_READY_NO_TRAINING_NO_FORWARD`.

По просьбе пользователя подготовлен единый пакет графиков для ручной проверки входов: базовый диапазон `2026-01-27..2026-02-27` плюс review-раунды `R2/R3/R4` за `2026-02-28..2026-03-20`. Новый train и новый forward не запускались.

Состав пакета: `53` дневных PNG (`BASE=32`, `R2=7`, `R3=7`, `R4=7`), отдельные contact sheets по каждому блоку, индекс CSV/Markdown и manifest. R2/R3/R4 предварительно пересобраны штатным `run_stas5_v5c_review_gallery.ps1`, чтобы в общей витрине были все 7 дней каждого раунда, включая полный R4.

Папка:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ENTRY_VISUAL_CHECK_CURRENT_20260127_20260320
```

## Handoff 2026-07-22 STAS5 V5C R4BB Table/ML Audit

Статус: `PASS_V5C_R4BB_TABLE_ML_AUDIT_NO_FATAL_TABLE_BUG_FOUND`.

По просьбе пользователя проверено, не мог ли бардак в таблицах/визуальных preview-баг испортить обучение. Подключены два активных subagents: один проверил R2/R3/R4 ledgers и review pack, второй проверил, что STAS8 Soft V2 visual marker bug не попал в train datasets/model features.

Итог: train artifacts корректно используют R4BB/X463. ENTRY dataset `rows=3285`, `entry_y GOOD=517`, `BAD=2768`, `features=463`, `bb20_*=24`; RiskGate dataset `rows=627`, `risk_bad_y=400`, `risk_ok=227`, `features=463`, `bb20_*=24`. R2/R3/R4 approved review: `21` день, `GOOD=227`, `BAD=462`, `RISK_BAD=400`, mismatch `0`. Forbidden target/manual/future/STAS8 preview fields в X/joblib не найдены.

Вывод для следующего агента: не искать проблему в том, что ручные правки не применились. Они применились. Следующий шаг должен быть tuning/preview: ENTRY recall, RiskGate threshold/labels balance, STAS8/move-capacity down-channel vs post-knife rebound. Новое обучение не запускать без отдельного visual OK.

Отчет:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5C_R4BB_TABLE_ML_AUDIT_20260722_RU.md
```

## Handoff 2026-07-22 STAS8 Soft Capacity V2 Preview R5

Статус: `PASS_V5C_STAS8_SOFT_CAPACITY_V2_PREVIEW_READY_NO_TRAINING_NO_FORWARD_NO_DECISION_CHANGE`.

Собран `STAS8_SOFT_CAPACITY_V2` как read-only overlay поверх R5:

```text
run_id=stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1
range=2026-03-21..2026-03-27
rows=564
features=463
predictions_sha=cd7bc6f7a2855a116d6973ef0a827b160c2843cf9df04c432db4b95b2acfd579
```

No-future/immutability guard PASS: R5 начинается после train-end `2026-03-20`, RiskGate не применен, predictions SHA не изменился, `stas8_live_source_time_utc <= entry_time_utc`, teacher/future поля только audit/report, SKIP не повышается в ENTER, hard-block не оставляет исходный ENTER/WATCH живым.

Итог по режимам:

```text
strict:   ENTER=2,  WATCH=118, SKIP=444, green_final_enter=2,  enter_to_watch_square=6,  hard_block_circle=107, hidden_recall=0
balanced: ENTER=15, WATCH=152, SKIP=397, green_final_enter=15, enter_to_watch_square=11, hard_block_circle=60,  hidden_recall=48
wide:     ENTER=36, WATCH=161, SKIP=367, green_final_enter=36, enter_to_watch_square=6,  hard_block_circle=30,  hidden_recall=48
```

Важный visual fix: зеленый круг на PNG теперь означает только финальный live `ENTER` после STAS8. `SKIP->RECALL_WATCH` больше не рисуется зеленым кругом на цене и остается только в CSV/отчете как offline-аудит.

Глазами проверены 2026-03-26/2026-03-27: визуальная путаница снята, но логика все еще требует tuning. `balanced` оставляет 1 live `ENTER` на 2026-03-26 в падающем канале, `wide` оставляет 9; это следующий предмет настройки. Обучение и новый forward не запускались.

Папка:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/soft_capacity_v2
```

## Handoff 2026-07-22 STAS8 R5 Entry/Move Audit

Статус: `STAS8_R5_ENTRY_MOVE_AUDIT_READY_NO_TRAINING_NO_FORWARD_NO_DECISION_CHANGE`.

Проведен аудит актуальной R5 недели `2026-03-21..2026-03-27` по run:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1
```

Главный вывод: текущий `STAS8_MOVE_CAPACITY_AUDIT_V1` полезен как диагностика, но слишком жесткий для включения. До STAS8 было `ENTER=61`, `WATCH=166`, `SKIP=337`; после preview стало `ENTER=1`, `WATCH=20`, `SKIP=543`. За неделю `119` кандидатов дали `hit_1p2`; исходная ENTRY увидела только `46` из них, `73` остались SKIP. STAS8 заблокировал `40` хороших исходных ENTER/WATCH и оставил `15` плохих WATCH без `hit_1p2`.

Сильные отрицательные buckets: `NO_MOVE`, `LOW_MOVE_CHOP`, `NO_MOVE_DOWN_CHANNEL` - их можно резать/понижать. Сильные положительные buckets: `MOVE_OK_1P5`, `MOVE_OK_1P2`, `POST_KNIFE_RETEST_EDGE`, `LOCAL_LOW_REBOUND_EDGE`, `SPIKE_EXTREME` - их нельзя душить общим hard-block. `HIGH_VOL_DANGER` смешанный и должен быть разделен на active dump hard-block и post-knife rebound protect.

Новый отчет:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1/STAS5_V5C_STAS8_R5_ENTRY_MOVE_AUDIT_20260321_20260327_RU.md
```

Дополнительные CSV-срезы лежат рядом: per-day, buckets, missed SKIP HQ, blocked HQ, kept bad. Рекомендация: перед новым обучением собрать read-only `STAS8_SOFT_CAPACITY_V2` с режимами `strict/balanced/wide`; R5 не добавлять в train до ручного review.

## Handoff 2026-07-22 STAS8 R5 Visuals Without Bollinger

Статус: `PASS_STAS8_R5_VISUALS_REBUILT_WITHOUT_BOLLINGER_OVERLAY`.

По просьбе пользователя STAS8-графики audit-preview для R5 `2026-03-21..2026-03-27` пересобраны без визуальных полос Bollinger. Это только изменение PNG-рендера: обучение не запускалось, forward не запускался, исходный predictions CSV не менялся.

Актуальная папка:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1/visual_review
```

Guard остался `PASS_V5C_STAS8_MOVE_CAPACITY_AUDIT_V1_READY_NO_TRAINING_NO_DECISION_CHANGE`; цифры не изменились: до STAS8 `ENTER=61`, `WATCH=166`, `SKIP=337`; после STAS8-preview `ENTER=1`, `WATCH=20`, `SKIP=543`. В manifest добавлен флаг `visual_bollinger_preview=false`.

## Handoff 2026-07-22 STAS8 Move Capacity Audit Preview R5

Статус: `PASS_V5C_STAS8_MOVE_CAPACITY_AUDIT_V1_READY_NO_TRAINING_NO_DECISION_CHANGE`.

Собран первый рабочий контур `STAS8_MOVE_CAPACITY_AUDIT_V1` поверх актуального R5 no-risk X463 forward:

```text
run_id=stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1
range=2026-03-21..2026-03-27
rows=564
features=463
before STAS8: ENTER=61, WATCH=166, SKIP=337
preview after STAS8: ENTER=1, WATCH=20, SKIP=543
teacher_grid_rows=40608
png_count=7
```

Артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1
```

Код:

```text
src/mlbotnav/stas5_v5c_stas8_move_capacity_audit.py
STAS5_ML_CORE/run_stas5_v5c_stas8_move_capacity_audit.ps1
```

Guard PASS: исходный predictions CSV не изменен, R5 не добавлен в train, live STAS8 использует только causal X463 и закрытые свечи до `entry_time_utc`, teacher `future_* / hit_* / time_to_* / mae_* / move_capacity_y / move_edge_y` сохранен отдельно как offline audit.

Важный вывод: текущие rule-пороги STAS8 как preview слишком жесткие для боевого включения. Он хорошо подсвечивает 2026-03-26/2026-03-27 как down-channel/no-long, но перед train/enforce нужно визуально настроить пороги, чтобы не задушить хорошие rebound/local-low входы.

## Handoff 2026-07-22 STAS8 Live Wave + Move Capacity Plan Locked

Статус: `STAS8_LIVE_WAVE_MOVE_CAPACITY_TZ_LOCKED_NO_CODE_NO_TRAINING`.

По пользовательской корректировке обновлены ТЗ и управляющий config для `STAS8_MOVE_CAPACITY_GRID_V1`. Главная рельса: `STAS8` не является фильтром "потом был hit_1p2". Сначала live/no-future слой должен подтвердить, что рынок уже живой для long: есть волны вверх-вниз, диапазон, откат/retest/base/reclaim и нет one-way dump. Только после этого `ENTRY_BASELINE_ML` ищет local low/pullback, а STAS8 проверяет емкость движения `1.1-1.2%`.

Зафиксировано разделение:

```text
STAS8_LIVE_MOVE_CONTEXT_V1 = causal live context, решает ALLOW_ENTRY_SEARCH / WAIT / BLOCK
STAS8_TEACHER_MOVE_GRID_V1 = offline teacher/audit, считает future hit/range/MFE/MAE/time_to
```

Train/forward рельса: base32 + approved `R2/R3/R4` (`2026-01-27..2026-03-20`) можно использовать для обучения; `R5 2026-03-21..2026-03-27` остается blind-forward/audit-preview и не входит в train до ручного review пользователя. Процентная audit-сетка: `0.4..5.0` шаг `0.1`, затем `5.0..10.0` шаг `0.2`; рабочие пороги `1.1%` WATCH, `1.2%` ENTER, `1.5%` strong.

Обновлены:

```text
STAS5_ML_CORE/10_STAS8_MOVE_CAPACITY_GRID_TZ_RU.md
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
```

Код STAS8, обучение, forward, датасеты и predictions не запускались и не менялись.

## Handoff 2026-07-22 STAS5 V5C R4BB Fast Train Audit

Статус: `PASS_V5C_R4BB_FAST_TRAIN_AUDIT_CONFIG_FIXED_NO_IGNORED_FEATURES_FOUND`.

Пользователь вручную запустил train `stas5_v5c_r4bb_train_20260127_20260320`; аудит показал, что обучение не пропущено и не взяло старый X439 batch. ENTRY train manifest использует:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_ML_READY_463F_TARGETS_V1.csv
```

RiskGate train manifest использует:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X463_RISK_BAD_Y_V1.csv
```

Контрольные цифры: ENTRY `rows=3285`, `entry_y GOOD=517`, `BAD=2768`, `features=463`, `bb20_*=24`; RiskGate `rows=627`, `risk_bad_y=1=400`, `risk_bad_y=0=227`, `features=463`, `bb20_*=24`. `STAS5_V5C_LATEST_TWO_BLOCK_MODEL_RUN.json` указывает на этот run. ENTRY post-train guard и RiskGate post-train guard PASS.

Модельные пакеты `.joblib` проверены: phase/state, ENTRY baseline и RiskGate содержат `feature_columns=463` с `24` `bb20_*`; two-block ENTRY содержит `493` features, потому что это `X463 + 30` OOF/live phase-state prediction columns. Forbidden target/review/future columns в model feature lists не найдены.

Причина быстрого обучения: маленький объем (`3285` ENTRY rows и `627` RiskGate rows) и легкие sklearn-модели без Optuna/нейросети/API. Косметический риск из аудита закрыт: устаревшие check names в текущем R4BB-контуре переименованы, фактические значения и paths остаются X463.

Управляющий config тоже приведен в актуальное состояние: `active_context.train` теперь указывает на `stas5_v5c_r4bb_train_20260127_20260320`, `feature_count=463`; JSON snapshot пересобран из YAML.

Аудит сохранен:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5C_R4BB_FAST_TRAIN_AUDIT_RU.md
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5C_R4BB_FAST_TRAIN_AUDIT_V1.json
```

## Handoff 2026-07-22 STAS5 V5C Bollinger Layer V1 X463

Статус: `PASS_V5C_BOLLINGER_LAYER_V1_X463_DATASETS_AND_REVIEW_GALLERY_READY_NO_TRAINING`.

Реализован полноценный causal Bollinger Layer V1, а не только картинка. Новый модуль:

```text
src/mlbotnav/stas5_v5c_bollinger_layer.py
```

Слой добавляет `24` причинных `bb20_*` признака к базовому `X439`; новый контракт `X439_PLUS_BB24_V1`, итого `463` features. Расчет идет только по закрытым 1m свечам до `entry_time_utc`; guard проверил `bb_source_time_utc <= entry_time_utc`.

Собраны реальные train artifacts по базе `2026-01-27..2026-03-20` с approved R2/R3/R4:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_ML_READY_463F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_FEATURE_ALLOWLIST_463F_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_GUARD_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X463_RISK_BAD_Y_V1.csv
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_GUARD_V1.json
```

Контрольные цифры: ENTRY `rows=3285`, `GOOD=517`, `BAD=2768`, `features=463`; RiskGate `rows=627`, `risk_bad_y=1=400`, `risk_bad_y=0=227`, `features=463`. ENTRY TrainingGuard PASS в run `stas5_v5c_r4bb_train_20260127_20260320`; RiskGate ML TrainingGuard PASS там же. Обучение и forward не запускались.

Визуальная витрина R2/R3/R4 с Bollinger собрана отдельно:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA/R2
STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA/R3
STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA/R4
```

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5c_bollinger_layer.py tests/test_stas5_v5c_train_dataset_builder.py -q` = `2 passed`; JSON config valid.

## Handoff 2026-07-22 STAS5 V5C R5 Bollinger Block V0 Red Circles

Статус: `PASS_V5C_BOLLINGER_BLOCK_V0_VISUAL_PREVIEW_WEEK_READY_NO_TRAINING`.

Для правильной R5 no-risk папки `2026-03-21..2026-03-27` собраны отдельные графики, где Bollinger `20/2` показывает красными кругами, какие текущие `ENTER/WATCH` он бы заблокировал по preview-правилу `BB_BLOCK_V0`. Это только визуальная проверка: обучение, forward, predictions CSV и исходные решения `ENTER/WATCH/SKIP` не менялись.

Артефакт:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r5_entry_only_forward_20260321_20260327_wide_no_risk/visual_review/
```

Итог недели: `blocked_total=131`, из них `ENTER=53`, `WATCH=78`. По дням: `2026-03-21=7`, `2026-03-22=24`, `2026-03-23=14`, `2026-03-24=23`, `2026-03-25=12`, `2026-03-26=32`, `2026-03-27=19`. Главный week-manifest: `STAS5_V5_FORWARD_VISUAL_REVIEW_20260321_20260327_BOLLINGER_BLOCK_V0_WEEK_MANIFEST.json`.

Рельса: это не RiskGate enforce и не STAS8. Сейчас пользователь смотрит PNG `*_ENTER_WATCH_BOLLINGER_BLOCK_V0_RED_CIRCLES.png` и решает, помогает ли такой блокер убирать входы в down-channel/no-move зонах.

## Handoff 2026-07-22 STAS5 V5C R5 No-Risk Bollinger Visual Review

Статус: `PASS_V5C_R5_ENTRY_ONLY_NO_RISK_BOLLINGER_VISUAL_READY_NO_TRAINING`.

Правильная папка пользователя для просмотра без RiskGate/safety-pulse:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r5_entry_only_forward_20260321_20260327_wide_no_risk/visual_review
```

Собраны Bollinger-графики за `2026-03-21..2026-03-27` через `mlbotnav.stas5_v5_forward_visual_review --bollinger-preview`. Дневные файлы лежат внутри `visual_review/YYYYMMDD` с именем `*_ENTER_ARROWS_BOLLINGER20_2SIGMA_PREVIEW.png`. Это no-risk/ENTRY-only визуализация, решения не менялись: по manifest `png_count=14`, `bollinger_preview=true`, status PASS. Проверки: `py_compile PASS`, `pytest tests/test_stas5_v5_forward_visual_review.py -q` = `1 passed`.

## Handoff 2026-07-22 STAS5 V5C Bollinger Visual Preview

Статус: `PASS_V5C_BOLLINGER_VISUAL_PREVIEW_READY_NO_TRAINING`.

Для всей недели `2026-03-21..2026-03-27` из preview `DOWN_CHANNEL_NO_LONG_V1` добавлены отдельные визуальные PNG с полосами Bollinger `20/2`. Исходные safety-pulse PNG, predictions, train/forward и X439 не изменялись.

Артефакт:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1/safety_pulse_preview/down_channel_no_long_v1/
```

В `src/mlbotnav/stas5_v5_forward_visual_review.py` добавлен выключенный по умолчанию параметр `bollinger_preview`; в `src/mlbotnav/stas5_v5c_safety_pulse_preview.py` и `STAS5_ML_CORE/run_stas5_v5c_safety_pulse_preview.ps1` добавлен ключ `--bollinger-preview` / `-BollingerPreview`. Он нужен только для визуального анализа, не является ML feature и не участвует в обучении. Проверки: `py_compile PASS`, `pytest tests/test_stas5_v5_forward_visual_review.py tests/test_stas5_v5c_safety_pulse_preview.py -q` = `8 passed`.

## Handoff 2026-07-22 STAS5 V5C ENTRY-Only Wide R5

Статус: `ENTRY_ONLY_WIDE_R5_COMMANDS_READY_NO_TRAINING_STARTED_BY_CODEX`.

Добавлены явные ключи для раздушенного ENTRY-only режима:

```text
STAS5_ML_CORE/run_stas5_v5c_continuous_train_forward.ps1
src/mlbotnav/stas5_v5_continuous_ml.py
```

`-SkipRiskGateML` на `-Mode Train` обучает ENTRY по `2026-01-27..2026-03-20` и approved R2/R3/R4, но намеренно не обучает RiskGate ML в этом run. `-DisableRiskGateML` на `-Mode Forward` явно запрещает применять RiskGate даже если в manifest есть PASS RiskGate. `-EntryDecisionPolicy WideReview` раздушивает входы через train OOF quantile, без threshold tuning на forward.

Кодекс не запускал Train/Forward. Пользователь запускает команды вручную из `docs/codex/commands.md`.

## Handoff 2026-07-22 STAS8 Move Capacity Grid TZ

Статус: `STAS8_DEFERRED_TZ_ONLY_NO_CODE_NO_TRAINING`.

Зафиксировано отложенное ТЗ `STAS8 MOVE CAPACITY GRID V1` по идее пользователя: отдельно разделить `volatility` (цена вообще способна двигаться) и `edge` (после long-входа есть шанс получить движение в нашу сторону минимум `1.0..1.5%`). Это будущий слой между `ENTRY_BASELINE_ML` и safety/final decision, а не текущий боевой блок.

Главный документ:

```text
STAS5_ML_CORE/10_STAS8_MOVE_CAPACITY_GRID_TZ_RU.md
```

В управляющий YAML добавлен выключенный блок `STAS8_MOVE_CAPACITY_GRID_V1`: `enabled=false`, `mode=deferred_tz_only`, дата фиксации `2026-07-22`. Код, обучение и forward не запускались. Future/MFE/MAE/hit/time_to можно использовать только как offline teacher/audit, не как live X.

## Handoff 2026-07-21 STAS5 V5C Down-Channel Safety Pulse Preview

Статус: `PASS_V5C_SAFETY_PULSE_PREVIEW_READY_NO_TRAINING`.

Сделан финальный test-drive `DOWN_CHANNEL_NO_LONG_V1` поверх уже готового R4 forward `2026-03-21..2026-03-27`. Обучение, forward и исходный predictions CSV не изменялись.

Идея пульса: `ENTRY_BASELINE` до RiskGate оставляет возможности, а отдельный blocker запрещает long только в режиме `DOWN_CHANNEL_NO_LONG` - нисходящий канал, слабый отскок, нет хода под 1-1.5%. Старые taxonomy/ML mass-demote в этой policy не применяются.

```text
До RiskGate: ENTER=70, WATCH=176, SKIP=318
Старый финал с RISKGATE_ML: ENTER=34, WATCH=37, SKIP=493
DOWN_CHANNEL_NO_LONG_V1 preview: ENTER=40, WATCH=136, SKIP=388
2026-03-26: ENTER=4, WATCH=16, SKIP=68, down_channel_blocks=26
2026-03-27: ENTER=7, WATCH=18, SKIP=51, down_channel_blocks=11
```

Главная папка просмотра:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1/safety_pulse_preview/down_channel_no_long_v1
```

Проверки: `py_compile PASS`, `pytest tests/test_stas5_v5c_safety_pulse_preview.py -q` = `7 passed`, YAML config parse PASS. Следующий шаг - пользователь смотрит PNG; новый train/forward не запускать до визуального OK.

## Handoff 2026-07-21 STAS5 V5C Safety Pulse Preview

Статус: `PASS_V5C_SAFETY_PULSE_PREVIEW_READY_NO_TRAINING`.

После слабого результата R4 forward `2026-03-21..2026-03-27` сделан быстрый preview-инструмент без обучения и без изменения исходных predictions:

```text
src/mlbotnav/stas5_v5c_safety_pulse_preview.py
STAS5_ML_CORE/run_stas5_v5c_safety_pulse_preview.ps1
```

Собраны два варианта:

```text
BALANCED_SAFETY_V1: ENTER=3, WATCH=162, SKIP=399
HARD_BLOCK_ONLY_V1: ENTER=27, WATCH=138, SKIP=399
```

Рекомендуемый визуальный кандидат сейчас `HARD_BLOCK_ONLY_V1`, потому что `BALANCED_SAFETY_V1` слишком душит входы. Preview лежит здесь:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1/safety_pulse_preview/hard_block_only_v1
```

До визуального OK пользователя не встраивать pulse в боевой forward и не запускать новый долгий train.

## Handoff 2026-07-21 STAS5 V5C RiskGate ML Train Wiring Ready

Статус: `RISKGATE_ML_TRAIN_WIRING_READY_TRAINING_GUARDS_PASS_NO_TRAINING`.

К `-Mode Train` для `stas5_v5c_r4_train_20260127_20260320` подключен отдельный обучаемый `RISKGATE_ML`: после обычного ENTRY/two-block train он учится по `risk_bad_y` на отдельном RiskGate dataset и сохраняет `.joblib`, OOF, metrics, manifest и post-train guard в тот же run dir. Обучение и forward не запускались.

Готовые проверки:

```text
ENTRY TrainingGuard = PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING
RiskGate ML TrainingGuard = PASS_V5C_RISKGATE_ML_TRAINING_GUARD_READY_FOR_TRAINING
ENTRY dataset rows=3285 GOOD=517 BAD=2768 features=439
RiskGate dataset rows=627 risk_bad_y=1=400 risk_bad_y=0=227 features=439
```

Forward после будущего Train сохранит исходный ENTRY-вердикт в `ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE`, добавит `RISKGATE_ML_LIVE_SCORE`, `RISKGATE_ML_LIVE_DECISION`, `RISKGATE_ML_ACTION`, а `ENTRY_ML_LIVE_DECISION` станет финальным решением после safety-фильтра. Ручные targets/review/future не входят в live X439.

Следующий шаг: пользователь вручную запускает `-Mode Train` в VS Code. Forward запускать только после Train и PASS post-train guards.

## Handoff 2026-07-21 STAS5 V5C Review-Supervised Datasets Ready

Статус: `REVIEW_SUPERVISED_DATASETS_READY_TRAINING_GUARD_PASS_NO_TRAINING`.

Собраны train-датасеты из базы `2026-01-27..2026-02-27` + approved review-pack `R2/R3/R4` за `2026-02-28..2026-03-20`. Обучение и forward не запускались.

ENTRY dataset:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_ML_READY_439F_TARGETS_V1.csv
rows=3285
entry_y GOOD=517
entry_y BAD=2768
features=439
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
```

RiskGate dataset:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X439_RISK_BAD_Y_V1.csv
rows=627
risk_bad_y=1=400
risk_bad_y=0 explicit safe=227
features=439
guard=PASS_V5C_RISKGATE_TRAIN_DATASET_GUARD_READY_NO_TRAINING
```

TrainingGuard для будущего ручного запуска Train:

```text
run_id=stas5_v5c_r4_train_20260127_20260320
status=PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING
run_dir=STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4_train_20260127_20260320
```

Новая команда сборки датасетов: `STAS5_ML_CORE/run_stas5_v5c_train_dataset_builder.ps1`. Следующий шаг: пользователь вручную запускает `-Mode Train`; не запускать forward до сохраненной модели и post-train guard PASS.

## Handoff 2026-07-21 STAS5 V5C Dataset Rails Locked

Статус: `REVIEW_PACK_DATASET_RAILS_LOCKED_NO_TRAINING`.

Зафиксирован следующий этап после approved review-pack `R2/R3/R4`: сначала собрать `X439_SOURCE`, затем два отдельных train dataset - `ENTRY_TRAIN_DATASET` и `RISKGATE_TRAIN_DATASET`. Training и forward не запускались и остаются запрещены до dataset guards + training guard PASS.

Главный управляющий config обновлен:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

Справочные config-снимки также обновлены:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
```

Контрольные цифры будущего ENTRY train view: база `2026-01-27..2026-02-27` = `2596` rows, `GOOD=290`, `BAD=2306`, `features=439`; approved pack `2026-02-28..2026-03-20` = `689` rows, `GOOD=227`, `BAD=462`, `RISK BAD=400`. Ожидаемый ENTRY train view после прямого объединения: `days=53`, `rows=3285`, `GOOD=517`, `BAD=2768`.

RiskGate dataset V1: target `risk_bad_y`, positives `400`; negatives только `explicit_safe_only`, минимум из review ENTRY GOOD `227`. Legacy/base GOOD `290` пока только proxy/audit pool, не training-negative без отдельного разрешения. `risk_bad_y=1` всегда остается `entry_y=0`.

## Handoff 2026-07-21 STAS5 V5C Review Pack R2/R3/R4

Статус: `PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING`.

Собран отдельный утвержденный review-pack по всем ручным правкам `R2/R3/R4` за диапазон `2026-02-28..2026-03-20`. Это только сборка teacher/target-слоя, без обучения, без forward и без пересборки дневных паспортов.

Главная папка:

```text
STAS5_ML_CORE/artifacts/v5c/review/_APPROVED_REVIEW_PACKS/STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1/
```

Итоговые цифры pack:

```text
days=21
ENTRY rows=689
ENTRY GOOD=227
ENTRY BAD=462
RISK BAD=400
guard=PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING
```

Выходы:

```text
entry/STAS5_V5C_R2_R3_R4_ENTRY_REVIEW_APPROVED_ALL_V1.csv
riskgate/STAS5_V5C_R2_R3_R4_RISKGATE_REVIEW_APPROVED_ALL_V1.csv
STAS5_V5C_R2_R3_R4_REVIEW_PACK_MANIFEST_V1.json
STAS5_V5C_R2_R3_R4_REVIEW_PACK_GUARD_V1.json
STAS5_V5C_R2_R3_R4_REVIEW_PACK_AUDIT_RU.md
```

Guard подтвердил: `21/21` дней присутствуют, `APPROVED` ENTRY/RiskGate CSV/JSON присутствуют, `CURRENT_REVIEW.png` и `CURRENT_VISUAL_MANIFEST_V1.json` присутствуют, дублей `day+candidate_id` и `day+record_id` нет, конфликтов GOOD vs RISK нет, каждый `risk_bad_y=1` одновременно является `entry_y=0`, все LA найдены в source forward entries. PNG остается только визуальным слоем и не является ML source.

Код:

```text
src/mlbotnav/stas5_v5c_review_pack.py
STAS5_ML_CORE/run_stas5_v5c_review_pack.ps1
tests/test_stas5_v5c_review_pack.py
```

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5c_review_pack.py tests/test_stas5_v5c_review_ladder.py tests/test_stas5_v5_forward_visual_review.py tests/test_stas5_v5c_riskgate_audit.py -q` = `24 passed`.

## Handoff 2026-07-20 STAS5 V5C Current Review Cleanup

Статус: `PASS_V5C_CURRENT_REVIEW_CLEANUP_READY_NO_TRAINING`.

В review ladder и review gallery зафиксирован новый визуальный порядок: в корне дневной папки остается один рабочий PNG `*_CURRENT_REVIEW.png`. Технические/старые картинки `*_ALL_ENTRIES.png`, `*_ANNOTATED.png`, preview PNG и прежние версии переносятся без удаления в `_visual_archive`.

Для связи картинки с цифрами добавлен `*_CURRENT_VISUAL_MANIFEST_V1.json`: он хранит путь к current PNG, архиву, ENTRY/RiskGate CSV и контрольные counts/ids (`ENTRY GOOD`, `ENTRY BAD`, `RISK BAD`). ML source-of-truth остается CSV/JSON-ledger, не PNG.

Контрольный день пересохранен: `R2 / 2026-03-01`. Итог: `ENTRY GOOD=10`, `ENTRY BAD=26`, `RISK BAD=21`. Training, forward и day passport rebuild не запускались.

## Handoff 2026-07-20 STAS5 V5C Review LA Labels Fixed

Статус: `PASS_V5C_REVIEW_LA_LABELS_ABOVE_MARKERS_FIXED_NO_TRAINING`.

Пользователь утвердил визуальный стандарт: `LAxxx` должны оставаться как раньше по раскладке, но не перекрываться review-кругами/квадратами. Renderer `src/mlbotnav/stas5_v5_forward_visual_review.py` изменен: review markers рисуются раньше, затем `LAxxx` рисуются верхним слоем; для review-точек добавлен только небольшой подъем подписи.

Пересобрана общая gallery R2/R3/R4: `STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/`. Training/forward/day passport rebuild не запускались.

## Handoff 2026-07-20 STAS5 V5C Review Gallery R2/R3/R4

Статус: `PASS_V5C_ALL_ROUNDS_REVIEW_GALLERY_READY_NO_TRAINING`.

Создан общий сборщик review-графиков:

```text
src/mlbotnav/stas5_v5c_review_gallery.py
STAS5_ML_CORE/run_stas5_v5c_review_gallery.ps1
```

Общая папка:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/
```

Собрано: `15` review-дней и `30` PNG. R2: `2026-02-28..2026-03-06` = `7` дней, `14` PNG. R3: `2026-03-07..2026-03-13` = `7` дней, `14` PNG. R4: пока только `2026-03-18` = `1` день, `2` PNG.

Каждый день имеет `ALL_ENTRIES.png` и `ANNOTATED_ENTRY_RISK.png`. Overlay: `GOOD` = зеленый круг, обычный `BAD` = красный квадрат, `RISK BAD` = красный круг. Сборщик не запускает training, forward и day passport rebuild.

## Handoff 2026-07-20 STAS5 V5C ENTRY/RiskGate Two Targets Fixed

Статус: `V5C_ENTRY_RISKGATE_TWO_TARGETS_FIXED_NO_TRAINING`.

Зафиксирован контракт разметки: одна и та же строка кандидата использует causal `X439`, но поверх нее существуют две разные цели. ENTRY-цель: `entry_y`. RiskGate-цель: `risk_bad_y`.

Правило ENTRY: `хорошо`, `вход`, `крестик хорошо`, `ромбик хорошо` -> `entry_y=1`; обычное `плохо` -> `entry_y=0`; `риск плохо` тоже -> `entry_y=0`. Это учит `ENTRY_BASELINE_ML` искать возможность входа и не повторять плохие ромбики/треугольники.

Правило RiskGate: фраза со словом `риск плохо` -> `entry_y=0 + risk_bad_y=1`. `risk_bad_y` не является feature и не попадает в live `X439`; это safety-target. ENTRY при этом тоже получает плохой пример.

Важная граница: отсутствие `риск плохо` не является автоматическим доказательством safety. Отрицательные примеры для RiskGate должны быть сформированы отдельным правилом при сборке RiskGate dataset.

Финальная схема: `X439 -> ENTRY_BASELINE_ML -> opportunity`; параллельно `X439 -> RiskGate -> danger/no danger`; затем `ENTRY good + Risk safe = ENTER`, `ENTRY good + Risk bad = BLOCK`. Training/forward не запускались.

## Handoff 2026-07-20 STAS5 V5C Quick Review Ladder ENTRY + RiskGate

Статус: `PASS_V5C_QUICK_REVIEW_LADDER_READY_NO_TRAINING`.

По решению пользователя зафиксирована простая диктовка review:

```text
без слова риск -> ENTRY teacher:
  хорошо / вход / хотелось бы вход -> GOOD -> GoodIds -> entry_y=1
  плохо -> BAD -> entry_y=0

со словом риск -> только RiskGate teacher:
  риск плохо -> RISK_BAD
  риск хорошо -> запрещено, чтобы не путать ENTRY и safety
```

Добавлены:

```text
src/mlbotnav/stas5_v5c_review_ladder.py
STAS5_ML_CORE/run_stas5_v5c_review_ladder.ps1
tests/test_stas5_v5c_review_ladder.py
```

Новая команда читает V5C forward visual entries, парсит текст пользователя, нормализует `7/LA7/LA007/0.7` в `LA007`, пишет отдельные ENTRY и RiskGate review-ledgers. При `-Stage BuildEntryDay` или `-Stage All` команда автоматически передает только ENTRY GOOD ids в старую V5 day ladder. Risk labels остаются отдельным teacher/audit слоем и не являются live X439.

Проверки: `py_compile PASS`; `PYTHONPATH=src .venv python -m pytest tests/test_stas5_v5c_review_ladder.py tests/test_stas5_v5c_riskgate_audit.py tests/test_stas5_v5_forward_visual_review.py -q` = `21 passed`; PowerShell `-Stage Parse` smoke PASS.

Update after user smoke: первый `-Stage All` записал `APPROVED` review, но упал на внутреннем вызове старой day-ladder из-за PowerShell array-аргументов. Wrapper исправлен на строгий именованный вызов `run_stas5_v5_day_ladder.ps1 -Day ... -Stage All -GoodIds $goodIds`. Повтор после частичного сбоя делать с `-Force`.

Update 2: по требованию пользователя review ladder теперь сохраняет рядом с ledger контрольный график со всеми входами `*_ALL_ENTRIES.png`, копируя исходный V5C `visual_review` PNG. Это визуальный artifact only, predictions/training/forward не меняет.

Update 3: добавлен отдельный `*_ANNOTATED.png` для визуальной проверки продиктованной команды. Он строится основным V5C renderer-ом, сохраняет полосы `Fon/LONG/SHORT/WAVE`, все LA-маркеры и поверх подсвечивает `GOOD/BAD/RISK BAD`. Для примера `2026-03-18` файл пересобран: `STAS5_ML_CORE/artifacts/v5c/review/r4_user_review/20260318/STAS5_V5C_R4_USER_REVIEW_20260318_APPROVED_ANNOTATED.png`. `ALL_ENTRIES` остается чистой копией без overlay.

Update 4: по замечанию пользователя из `*_ANNOTATED.png` убраны индивидуальные стрелки и подписи возле review-точек. Новый стандарт overlay: `GOOD` = зеленый круг, `RISK BAD` = ярко-красный круг, обычный `BAD` = красный квадрат; справа сверху только компактная легенда-счетчик. Training/forward не менялись.

## Handoff 2026-07-20 STAS5 V5C RiskGate Taxonomy V1

Статус: `PASS_V5C_RISKGATE_TAXONOMY_V1_AUDIT_ONLY_READY`.

По решению пользователя RiskGate докручен до полной таксономии режимов рынка, без перевода в боевой enforce и без изменения `ENTRY_ML_LIVE_DECISION`. Старые статусы `PASS_RISK/WARN_RISK/BLOCK_RISK/BLOCK_HARD/PASS_USER_REBOUND` сохранены как лестница действия, а режимы рынка вынесены в отдельные audit-колонки.

Добавлены режимы:

```text
PRE_DUMP_RISK
ACTIVE_DUMP
FALLING_KNIFE
STRONG_SHORT_PRESSURE
SHORT_CONTINUATION
PULLBACK_THEN_SHORT
SUPPORT_BREAKDOWN
CHANNEL_BREAKDOWN
POST_PUMP_DUMP
LIQUIDATION_CASCADE
```

Код: `src/mlbotnav/stas5_v5c_riskgate_audit.py`.
Тесты: `tests/test_stas5_v5c_riskgate_audit.py`.
YAML source-of-truth: `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml`, статус `ACTIVE_CONTROL_CONFIG_YAML_SOURCE_OF_TRUTH_RISKGATE_TAXONOMY_V1_AUDIT_ONLY_IMPLEMENTED`.

Официальный audit-only прогон пересобран для `2026-03-18` поверх R3 forward `stas5_v5c_r3_forward_20260314_20260320_wide_v1` с user-pass `LA059,LA067,LA078`.

Итог по ENTER: `15`; `BLOCK_HARD=6`, `BLOCK_RISK=3`, `WARN_RISK=3`, `PASS_USER_REBOUND=3`. Primary-regime counts: `LIQUIDATION_CASCADE=7`, `USER_APPROVED_REBOUND_EXCEPTION=3`, `FALLING_KNIFE=2`, `CHANNEL_BREAKDOWN=1`, `SUPPORT_BREAKDOWN=1`, `PRE_DUMP_RISK=1`. `RISK_NO_FUTURE_OK=True` для всех строк.

Проверки: `py_compile PASS`, `pytest tests/test_stas5_v5c_riskgate_audit.py -q` = `16 passed`, YAML read PASS, text audit PASS. Training/forward не запускались.

## Handoff 2026-07-20 STAS5 V5C RiskGate Audit-Only Implemented

Статус: `PASS_V5C_RISKGATE_AUDIT_ONLY_READY`.

По решению пользователя RiskGate зафиксирован как рабочий safety-контур в режиме `audit_only`: `ENTRY_BASELINE_ML` продолжает искать входы, а RiskGate рядом считает `WARN_RISK`, `BLOCK_RISK`, `BLOCK_HARD`, `PASS_USER_REBOUND`. Боевой enforce не включался, текущие `ENTRY_ML_LIVE_SCORE` и `ENTRY_ML_LIVE_DECISION` не менялись.

Код:

```text
src/mlbotnav/stas5_v5c_riskgate_audit.py
STAS5_ML_CORE/run_stas5_v5c_continuous_train_forward.ps1
tests/test_stas5_v5c_riskgate_audit.py
```

Главный YAML обновлен: `RISK_GATE_RULE_V0.enabled=true`, `mode=audit_only`, `implementation_status=IMPLEMENTED_AUDIT_ONLY`, `can_enforce_without_guard=false`.

Контрольный прогон на `2026-03-18` с пользовательскими исключениями `LA059,LA067,LA078`:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_audit/
```

Итог: `PASS`, `ENTER=15`, `BLOCK_HARD=6`, `BLOCK_RISK=3`, `WARN_RISK=3`, `PASS_USER_REBOUND=3`. UTF-8 audit `PASS`.

## Handoff 2026-07-20 STAS5 V5C RiskGate Preview 2026-03-18

Статус: `PASS_V5C_RISKGATE_PREVIEW_20260318_AUDIT_ONLY_READY`.

Создан отдельный audit-only прототип RiskGate V0 для forward-дня `2026-03-18` из R3 week3 run:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/
```

Артефакты:

```text
STAS5_V5C_RISKGATE_PREVIEW_20260318_V0.png
STAS5_V5C_RISKGATE_PREVIEW_20260318_V0.csv
STAS5_V5C_RISKGATE_PREVIEW_20260318_V0.json
STAS5_V5C_RISKGATE_PREVIEW_20260318_RU.md
```

Это только визуальный/табличный preview: текущие `ENTRY_ML_LIVE_SCORE`, `ENTRY_ML_LIVE_DECISION`, модель, train manifest и forward predictions не изменялись. RiskGate enforce не включен. По строгому V0-прототипу на `2026-03-18`: `ENTER=15`, `BLOCK_HARD=8`, `BLOCK_RISK=3`, `WARN_RISK=4`, `PASS_RISK=0`.

Обновление после пользовательской проверки: пользователь отметил три проходящих входа `LA059`, `LA067`, `LA078`. Создана V1-копия preview с `PASS_USER_REBOUND`:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_V1_USER_PASS.png
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_V1_USER_PASS.csv
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/STAS5_V5C_RISKGATE_PREVIEW_20260318_V1_USER_PASS_RU.md
```

V1 adjusted counts: `ENTER=15`, `BLOCK_HARD=6`, `BLOCK_RISK=3`, `WARN_RISK=3`, `PASS_USER_REBOUND=3`. UTF-8 audit по riskgate preview artifacts: `PASS`, question-mark placeholders не осталось.

## Handoff 2026-07-20 STAS5 V5C ENTRY_ML_TWO_BLOCK Frozen

Статус: `V5C_ENTRY_TWO_BLOCK_FROZEN_BASELINE_RISKGATE_NEXT`.

По решению пользователя `ENTRY_ML_TWO_BLOCK` заморожен в главном YAML config:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

Теперь у блока `enabled=false`, `mode=frozen_not_selected`, `selection_status=FROZEN_NOT_SELECTED_BY_R3_QUALITY_GATE`. Причина: блок технически обучается, но не проходит отбор как главный и не доказал преимущество над `ENTRY_BASELINE_ML`. Текущая рельса: не тратить время на Block 3, фокусироваться на `ENTRY_BASELINE_ML + RISK_GATE_RULE_V0 audit_only`.

Код раннеров не менялся, training/forward не запускались, predictions не менялись.

## Handoff 2026-07-20 STAS5 V5C YAML Config Russian Comments

Статус: `V5C_YAML_CONTROL_CONFIG_COMMENTED_RU_NO_CODE_WIRING`.

Главный YAML config дополнен русскими комментариями по каждому разделу и ML-блоку:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

Комментарии поясняют роли `ENTRY_BASELINE_ML`, `MARKET_PHASE_STATE_ML`, `ENTRY_ML_TWO_BLOCK`, `RISK_GATE_RULE_V0`, `DUMP_AVOID_ML`, `REBOUND_ALLOW_ML`, а также no-future contract, guard-рельсы и порядок будущего RiskGate. Значения config не менялись, код раннеров не менялся, обучение/forward не запускались, predictions не менялись. YAML после комментариев валиден.

## Handoff 2026-07-20 STAS5 V5C Main YAML ML Control Config

Статус: `V5C_MAIN_YAML_CONTROL_CONFIG_READY_NO_CODE_WIRING`.

По решению пользователя главным управляемым config стал один YAML:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

В YAML зафиксированы active context R3, `X439` no-future контракт, статусы `ENTRY_BASELINE_ML`, `MARKET_PHASE_STATE_ML`, `ENTRY_ML_TWO_BLOCK`, `RISK_GATE_RULE_V0`, `DUMP_AVOID_ML`, `REBOUND_ALLOW_ML`, а также рельса RiskGate: сначала только `audit_only`, без enforce и без затирания текущего ENTRY.

Старые файлы `STAS5_V5C_ML_CONTROL_CONFIG_V1.json` и `STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md` оставлены как reference snapshot/readme и помечены не source-of-truth. Код раннеров пока YAML автоматически не читает, обучение/forward не запускались, predictions не менялись.

## Handoff 2026-07-19 STAS5 V5C ML Control Config V1

Статус: `V5C_ML_CONTROL_CONFIG_READY_RISKGATE_NOT_IMPLEMENTED`.

Создан единый управляющий паспорт ML-блоков:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
```

Конфиг фиксирует текущую R3 схему без запуска обучения и без изменения predictions: активный train `stas5_v5c_r3_train_20260127_20260313`, train range `2026-01-27..2026-03-13`, `days=46`, `rows=3726`, `entry_y GOOD=432`, `entry_y BAD=3294`, `features=439`; активный forward review `stas5_v5c_r3_forward_20260314_20260320_wide_v1`, `ENTER=62`, `WATCH=162`, `SKIP=345`.

Зафиксированы статусы ML-блоков: `ENTRY_BASELINE_ML` включен и выбран как текущий entry alpha; `MARKET_PHASE_STATE_ML` обучен как support; `ENTRY_ML_TWO_BLOCK` обучен, но не выбран quality gate; `RISK_GATE_RULE_V0`, `DUMP_AVOID_ML`, `REBOUND_ALLOW_ML` пока выключены и описаны как следующий safety-контур. RiskGate должен начинаться только как `audit_only` overlay поверх ENTRY, без затирания текущего решения.

Граница: config V1 пока documentation/control artifact, код раннеров его еще не читает. Следующий шаг, если пользователь подтвердит, - подключать RiskGate V0 audit-only и отдельный guard, сохраняя `X439` no-future контракт.

## Handoff 2026-07-18 STAS5 V5C R3 Train PASS Ready For Forward Week3

Статус: `PASS_V5_TWO_BLOCK_ML_TRAINED_POST_TRAIN_GUARD_READY_FOR_FORWARD`.

Пользователь запустил R3 `Train` для `TrainRunId=stas5_v5c_r3_train_20260127_20260313`. Обучение завершено на правильном R3 batch `2026-01-27..2026-03-13`: `days=46`, `rows=3726`, `entry_y 1=432`, `entry_y 0=3294`, `features=439`.

Созданы модели: `STAS5_V5_ENTRY_BASELINE_MODEL.joblib`, `STAS5_V5_MARKET_PHASE_STATE_MODEL.joblib`, `STAS5_V5_ENTRY_ML_MODEL.joblib`. OOF predictions покрывают `3726/3726` строк без null. Post-train guard: `PASS_V5_TWO_BLOCK_POST_TRAIN_GUARD_READY_FOR_FORWARD`.

Production selector выбрал `entry_baseline`, потому что two-block не прошел quality gate: baseline PR-AUC `0.253024`, two-block PR-AUC `0.250156`; baseline walk PR-AUC `0.298295`, two-block walk PR-AUC `0.272692`; baseline top 1pct precision `0.421053`, two-block `0.394737`. Phase/state модель обучена и сохранена, но для ENTRY production выбран baseline.

Свечи следующей blind-недели `2026-03-14..2026-03-20` проверены: все `data/core/bybit_ohlcv/dt=YYYY-MM-DD/tf=1m/symbol=SOLUSDT/part-final.csv` существуют. Следующий шаг: пользователь запускает R3 forward на `2026-03-14..2026-03-20` с manifest `STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r3_train_20260127_20260313/STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json`.

## Handoff 2026-07-18 STAS5 V5C R3 Training Guard PASS

Статус: `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING_WAIT_USER_TRAIN`.

Пользователь запустил R3 `TrainingGuard` для `TrainRunId=stas5_v5c_r3_train_20260127_20260313` с диапазоном `2026-01-27..2026-03-13`. Guard подтвердил правильный R3 batch: `days=46`, `rows=3726`, `entry_y 1=432`, `entry_y 0=3294`, `features=439`.

Guard-файлы лежат в `STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r3_train_20260127_20260313/`. В run dir пока только `STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1.json` и `STAS5_V5_TWO_BLOCK_TRAINING_GUARD_RU.md`; model/joblib/train manifest нет, training еще не запускался. Следующий шаг: пользователь запускает `-Mode Train` с тем же run_id.

## Handoff 2026-07-17 STAS5 V5C R3 Batch Guard Ready

Статус: `PASS_V5C_R3_BATCH_20260127_20260313_READY_NO_TRAINING_RUN`.

Пользовательская R3-разметка `2026-03-07..2026-03-13`, продиктованная онлайн по графикам, принята как финальная и применена. Не просить пользователя вспоминать или повторно подтверждать эти правки: они уже сохранены в `STAS5_ML_CORE/artifacts/v5c/review/r3_user_review/` как approved-ledger, а дневные V5 passports пересобраны с соответствующими `GoodIds`.

Итог новой R3 review-недели: `7` дней, `554` строк, `73 GOOD`, `481 BAD`. Суммарный R3 train batch собран без запуска обучения и без forward:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_ML_READY_439F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_FEATURE_ALLOWLIST_439F_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_MANIFEST_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_GUARD_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_AUDIT_RU.md
```

Контрольные цифры R3 batch:

```text
days=46
rows=3726
entry_y 1=432
entry_y 0=3294
features=439
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
```

Проверено отдельно: GoodIds за `2026-03-07..2026-03-13` в дневных CSV совпадают с пользовательской разметкой один в один; кракозяб в R3 review-артефактах не найдено; training и forward по R3 не запускались.

Следующий шаг: пользователь сам запускает `TrainingGuard` для `stas5_v5c_r3_train_20260127_20260313`. Обучение запускать только после `TrainingGuard PASS`, командой пользователя. Следующий blind-forward должен идти только на следующей неразмеченной неделе после `2026-03-13`.

## Handoff 2026-07-17 STAS5 V5C R2Q WideReview V2 Review Source

Статус: `V5C_R2Q_WIDE_V2_READY_FOR_USER_REVIEW_AND_R3_LABELS`.

Пользователь подтвердил, что текущий расширенный режим примерно `6+ из 10` подходит как материал для дальнейшей ручной разметки. Последний зафиксированный run: `STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r2q_forward_20260307_20260313_wide_v2/`. Это forward `2026-03-07..2026-03-13`, обученный на R2Q train `2026-01-27..2026-03-06`, без включения этой forward-недели в train.

Фактические цифры: `rows=554`, `ENTER=64`, `WATCH=167`, `SKIP=323`, `visual_review_png_count=14`, forward status `PASS_V5C_CONTINUOUS_TWO_BLOCK_FORWARD_20260307_20260313_BLIND_NO_FUTURE`, visual status `PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES`. Entry policy `wide_review`, thresholds `enter=0.3012377066`, `watch=0.1576703673`, source `ENTRY_BASELINE_OOF_SCORE`, selected model `entry_baseline`.

Контрольный отчет создан: `STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r2q_forward_20260307_20260313_wide_v2/STAS5_V5C_R2Q_WIDE_V2_REVIEW_CONTROL_POINT_RU.md`.

Дальше пользователь смотрит графики и диктует по дням `LA + маркер + хорошо/плохо/хочу вход`. Codex должен сохранять это как R3 teacher review-ledger, затем пересобрать дневные V5 passports с `GoodIds`, после закрытия всех 7 дней собрать R3 batch `2026-01-27..2026-03-13`. Ручные метки не являются X features.

## Handoff 2026-07-17 STAS5 V5C R2Q Decision Policy Widened

Статус: `V5C_R2Q_DECISION_POLICY_WIDENED_WAIT_USER_FORWARD_RERUN`.

Пользователь проверил forward `stas5_v5c_r2q_forward_20260307_20260313_normal` и сообщил, что входов стало ещё меньше/слишком мало. Аудит manifest и predictions подтвердил: старый `Normal` использовал `enter_quantile=0.965`, `watch_quantile=0.815`; на `554` forward-кандидатах это дало `ENTER=5`, `WATCH=54`, `SKIP=495`. Строгий trained-run ранее давал `ENTER=1`, но пользовательский смысл всё равно верный: режим задушен и непригоден для ручного review.

Исправлено в `src/mlbotnav/stas5_v5_continuous_ml.py`: `ENTRY_DECISION_POLICY_QUANTILES` теперь `normal: enter=0.90/watch=0.60`, `wide_review: enter=0.80/watch=0.50`. По фактическим score той же forward-недели ожидается: новый `Normal` примерно `ENTER=25`, `WATCH=148`, `SKIP=381`; `WideReview` примерно `ENTER=64`, `WATCH=167`, `SKIP=323`. Это не переобучение: модель, X439 и train manifest не менялись, только live decision threshold из train OOF.

Проверки: `py_compile src/mlbotnav/stas5_v5_continuous_ml.py PASS`; PowerShell wrapper syntax `PASS`; `pytest tests/test_stas5_v5_continuous_ml.py tests/test_stas5_v5_two_block_ml.py` = `7 passed`.

Следующий шаг: пользователь запускает команду из `docs/codex/commands.md` с `-EntryDecisionPolicy WideReview` и новым run_id `stas5_v5c_r2q_forward_20260307_20260313_wide_v2`, чтобы получить графики с нормальным количеством входов.

## Handoff 2026-07-17 STAS5 V5C R2Q Train Multiclass Fix

Статус: `V5C_R2Q_TRAIN_MULTICLASS_SOLVER_FIX_READY_RETRY_TRAIN`.

Пользователь запустил `TrainingGuard` для `stas5_v5c_r2q_train_20260127_20260306`; guard вернул `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`. Следующий `Train` упал до создания модели на `phase_y/state_y`: `ValueError: The 'liblinear' solver does not support multiclass classification`. Причина была в коде, а не в данных: ветка `MARKET_PHASE_STATE_ML` использовала `logistic_balanced` из entry-pipeline для multiclass phase/state.

Исправлено в `src/mlbotnav/stas5_v5_two_block_ml.py`: добавлен отдельный `PHASE_STATE_MODEL_KIND = "extra_trees_balanced"` и применен для LODO phase/state, walk-forward audit и финальной сохраняемой `STAS5_V5_MARKET_PHASE_STATE_MODEL.joblib`. ENTRY-кандидаты `logistic_balanced/extra_trees_balanced` не менялись. В manifest/metrics теперь сохраняется `market_phase_state_model_kind`.

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5_two_block_ml.py tests/test_stas5_v5_continuous_ml.py` = `5 passed`. Добавлен тест `test_phase_state_lodo_uses_multiclass_safe_model`, который проверяет multiclass LODO на 3 классах и фиксирует, что phase/state больше не идет через `liblinear`.

Следующий шаг: пользователь повторяет ту же команду `Train` с run_id `stas5_v5c_r2q_train_20260127_20260306`. После PASS post-train guard можно запускать diagnostic forward week2.

## Handoff 2026-07-17 STAS5 V5C R2 ML Quality Fix Ready

Статус: `V5C_R2_ML_QUALITY_AUDIT_FIX_READY_NO_NEW_TRAINING`.

Проведен аудит с агентами по жалобе пользователя, что R2/R2-week2 работает примерно 50/50 и будто не учится на ручных lows. Фактический lineage чистый: R2 train `stas5_v5c_r2_train_20260127_20260306` использовал R2 batch `2026-01-27..2026-03-06`, а forward `stas5_v5c_r2_forward_20260307_20260313` использовал именно R2 train manifest. Старый R1 на диске есть, но в R2 run не подмешан.

Причина качества: свежая review-неделя вошла в train (`576` строк, `69` GOOD), но не имела повышенного веса; ENTER-порог был квантильный `p90` и почти принудительно давал много ENTER; `MARKET_PHASE_STATE_ML` на SGD давал warnings и шум; two-block не доказал преимущество над baseline, но forward все равно шел through two-block.

Исправлено в коде без запуска нового боевого train/forward: `src/mlbotnav/stas5_v5_two_block_ml.py`, `src/mlbotnav/stas5_v5_continuous_ml.py`. Новая рельса: teacher-only sample weights с boost от `2026-02-28`; phase/state без SGD; raw `predict_proba` NaN/inf больше не маскируется; ENTRY-кандидаты `logistic_balanced` и `extra_trees_balanced`; precision/Wilson OOF threshold вместо p90; production selector baseline vs two-block; V5C forward использует `selected_entry_model`.

Проверки: `py_compile PASS`; `pytest tests/test_stas5_v5_two_block_ml.py tests/test_stas5_v5_continuous_ml.py` = `4 passed`; temp smoke train PASS. Новое обучение пользователь запускает сам командами из `docs/codex/commands.md` с run_id `stas5_v5c_r2q_train_20260127_20260306`.

Отчет: `STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_R2_ML_QUALITY_AUDIT_AND_FIX_20260717_RU.md`.

## Handoff 2026-07-17 STAS5 V5C R2 Batch Guard Ready

Статус: `PASS_V5C_R2_BATCH_20260127_20260306_READY_NO_TRAINING_RUN`.

Подготовлена активная R2-рельса после закрытия пользовательской review-недели `2026-02-28..2026-03-06`. Код V5C параметризован по train-диапазону: `BuildBatch`, `TrainingGuard` и `Train` теперь используют один и тот же `TrainStartDay/TrainEndDay`, а не старый R1 batch по умолчанию. Wrapper `STAS5_ML_CORE/run_stas5_v5c_continuous_train_forward.ps1` переведен на текущие default-даты R2: train `2026-01-27..2026-03-06`, forward `2026-03-07..2026-03-13`.

Собран R2 continuous batch без запуска обучения и без forward:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260306_ML_READY_439F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260306_FEATURE_ALLOWLIST_439F_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260306_MANIFEST_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260306_GUARD_V1.json
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260306_AUDIT_RU.md
```

Контрольные цифры R2 batch:

```text
days=39
rows=3172
entry_y 1=359
entry_y 0=2813
features=439 = 274 old causal + 81 cs_* + 84 fcs_*
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
```

Guard PASS: allowlist одинаковый, target/manual columns не входят в X, forbidden leakage columns отсутствуют, `cs_max_source_time_utc <= entry_time_utc`, `fcs_max_source_time_utc <= entry_time_utc`, дублей `day+candidate_id/record_id` нет, обязательные feature columns заполнены. Старые R1 model/forward artifacts разрешены только как прошлый walk-forward контекст; R2 training и week2 forward не запускались.

Следующая неделя для blind forward проверена по свечам: `2026-03-07..2026-03-13` OHLCV files существуют. Дальше пользователь должен сам запустить команды из `docs/codex/commands.md`: сначала `TrainingGuard`, потом `Train`, потом `Forward` с явным R2 train manifest.

## Handoff 2026-07-17 STAS5 V5C R2 Text Encoding Fix

Статус: `UTF8_RUSSIAN_TEXT_RESTORED_NO_LABEL_CHANGE`.

Проведен аудит кракозяб в R2 review-артефактах. Реальные повреждения найдены в `STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260302..20260306/`: поля `user_reason_ru` и RU-md отчеты содержали question-mark placeholders вместо русского текста.

Перезаписаны UTF-8 review-ledger файлы для всех закрытых дней `2026-02-28..2026-03-06`, чтобы формат был единый:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/YYYYMMDD/
STAS5_V5C_R2_USER_REVIEW_YYYYMMDD_APPROVED.csv
STAS5_V5C_R2_USER_REVIEW_YYYYMMDD_APPROVED.json
STAS5_V5C_R2_USER_REVIEW_YYYYMMDD_APPROVED_RU.md
```

Контроль после фикса:

```text
review text audit: PASS, total_hits=0
label audit: PASS
days checked=7
GoodIds/BAD/entry_y unchanged
training not started
forward not started
```

Отчет:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/STAS5_V5C_R2_TEXT_ENCODING_AUDIT_20260717_RU.md
```

Граница: исправлен только текст teacher/audit-слоя (`user_reason_ru`, RU-md). Predictions, daily packages, X439, модели, thresholds, training и forward не менялись.

## Handoff 2026-07-17 STAS5 V5C R2 Review 2026-03-06 Closed

Статус: `USER_APPROVED_R2_REVIEW_WEEK_20260228_20260306_CLOSED_FULL_READY`.

Пользователь дал разметку `2026-03-06` для R2. Review сохранен в:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260306/
```

GOOD ids:

```text
LA006, LA023, LA028, LA047, LA055, LA066
```

Явные BAD-комментарии сохранены для аудита: `LA019`, `LA050`, `LA051`, `LA053`, `LA054`, `LA059`, `LA062`, `LA072`, `LA078`.

Уточнение по спорному месту: пользователь сказал `73 или 72, наверное`; в source predictions `LA072=ENTER`, `LA073=WATCH`, поэтому как плохой зеленый треугольник зафиксирован `LA072`.

По этим `GoodIds` собран дневной V5 approved package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260306/
STAS5_V5_MARKET_PASSPORT_20260306_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Контроль:

```text
full guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=87
entry_y 1=6 / 0=81
features=439
fcs=84
duplicates day+candidate_id=0
duplicates record_id=0
cs/fcs source-time violations=0
forbidden target/future columns in X=0
```

Граница: R2 training не запускался, новый forward не запускался. Закрыта вся R2 teacher-неделя: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`, `2026-03-04`, `2026-03-05`, `2026-03-06`. Следующий правильный шаг: собрать отдельный R2 batch dataset и R2 batch leakage/no-future guard; обучение запускать только после `PASS`.

## Handoff 2026-07-17 STAS5 V5C R2 Review 2026-03-05 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260305_CLOSED_FULL_READY`.

Пользователь дал разметку `2026-03-05` для R2. Review сохранен в:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260305/
```

GOOD ids:

```text
LA008, LA023, LA030, LA035, LA049, LA053, LA054, LA059, LA064, LA065, LA067
```

Явные BAD-комментарии сохранены для аудита: `LA055`, `LA058`, `LA081`.

По этим `GoodIds` собран дневной V5 approved package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260305/
STAS5_V5_MARKET_PASSPORT_20260305_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Контроль:

```text
full guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=85
entry_y 1=11 / 0=74
features=439
fcs=84
duplicates day+candidate_id=0
duplicates record_id=0
cs/fcs source-time violations=0
forbidden target/future columns in X=0
```

Граница: R2 training не запускался, новый forward не запускался. Закрыты R2 teacher-дни: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`, `2026-03-04`, `2026-03-05`. Следующий ручной день для закрытия: `2026-03-06`.

## Handoff 2026-07-17 STAS5 V5C R2 Review 2026-03-04 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260304_CLOSED_FULL_READY`.

Пользователь дал разметку `2026-03-04` для R2. Review сохранен в:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260304/
```

GOOD ids:

```text
LA014, LA019, LA020, LA022, LA034, LA040, LA047, LA051, LA071
```

Явные BAD-комментарии сохранены для аудита: `LA006`, `LA009`, `LA026`.

По этим `GoodIds` собран дневной V5 approved package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260304/
STAS5_V5_MARKET_PASSPORT_20260304_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Контроль:

```text
full guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=72
entry_y 1=9 / 0=63
features=439
fcs=84
duplicates day+candidate_id=0
duplicates record_id=0
cs/fcs source-time violations=0
forbidden target/future columns in X=0
```

Граница: R2 training не запускался, новый forward не запускался. Закрыты R2 teacher-дни: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`, `2026-03-04`. Следующий ручной день для закрытия: `2026-03-05`.

## Handoff 2026-07-17 STAS5 V5C R2 Review 2026-03-03 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260303_CLOSED_FULL_READY`.

Пользователь дал разметку `2026-03-03` для R2. Review сохранен в:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260303/
```

GOOD ids:

```text
LA006, LA007, LA043, LA045, LA055, LA060, LA062, LA066, LA067, LA072, LA082, LA083
```

Явные BAD-комментарии сохранены для аудита: `LA005`, `LA009`, `LA023`, `LA028`, `LA035`, `LA054`, `LA057`, `LA059`, `LA080`.

По этим `GoodIds` собран дневной V5 approved package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260303/
STAS5_V5_MARKET_PASSPORT_20260303_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Контроль:

```text
full guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=89
entry_y 1=12 / 0=77
features=439
fcs=84
duplicates day+candidate_id=0
duplicates record_id=0
cs/fcs source-time violations=0
forbidden target/future columns in X=0
```

Граница: R2 training не запускался, новый forward не запускался. Закрыты R2 teacher-дни: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`. Следующий ручной день для закрытия: `2026-03-04`.

## Handoff 2026-07-17 STAS5 V5C R2 Review 2026-03-02 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260302_CLOSED_FULL_READY`.

Пользователь дал разметку `2026-03-02` для R2. Review сохранен в:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260302/
```

GOOD ids:

```text
LA006, LA025, LA027, LA028, LA049, LA051, LA052, LA053, LA057, LA063, LA067, LA070
```

Явный BAD-комментарий сохранен для аудита: `LA010`.

По этим `GoodIds` собран дневной V5 approved package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260302/
STAS5_V5_MARKET_PASSPORT_20260302_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Контроль:

```text
full guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=81
entry_y 1=12 / 0=69
features=439
fcs=84
duplicates day+candidate_id=0
duplicates record_id=0
cs/fcs source-time violations=0
forbidden target/future columns in X=0
```

Граница: R2 training не запускался, новый forward не запускался. Закрыты R2 teacher-дни: `2026-02-28`, `2026-03-01`, `2026-03-02`. Следующий ручной день для закрытия: `2026-03-03`.

## Handoff 2026-07-17 STAS5 V5C R2 Review 2026-03-01 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260301_CLOSED_FULL_READY`.

Пользователь дал и подтвердил разметку `2026-03-01` для R2. Review сохранен в:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260301/
```

GOOD ids:

```text
LA002, LA005, LA012, LA033, LA044, LA048, LA055, LA071, LA075
```

Явные BAD-комментарии сохранены для аудита: `LA011`, `LA029`, `LA050`, `LA053`, `LA065`, `LA066`, `LA068`, `LA069`.

По этим `GoodIds` собран дневной V5 approved package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260301/
STAS5_V5_MARKET_PASSPORT_20260301_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Контроль:

```text
full guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=81
entry_y 1=9 / 0=72
features=439
fcs=84
duplicates day+candidate_id=0
duplicates record_id=0
cs/fcs source-time violations=0
forbidden target/future columns in X=0
```

Граница: R2 training не запускался, новый forward не запускался. Закрыты R2 teacher-дни: `2026-02-28`, `2026-03-01`. Следующий ручной день для закрытия: `2026-03-02`.

## Handoff 2026-07-17 STAS5 V5C R2 Review 2026-02-28 Closed

Статус: `USER_APPROVED_R2_REVIEW_20260228_CLOSED_FULL_READY`.

Пользователь подтвердил финальную разметку `2026-02-28` для R2. Review сохранен в:

```text
STAS5_ML_CORE/artifacts/v5c/review/r2_user_review/20260228/
```

GOOD ids:

```text
LA022, LA023, LA032, LA035, LA043, LA047, LA052, LA062, LA067, LA068
```

Явные BAD-комментарии сохранены для аудита: `LA014`, `LA024`, `LA039`, `LA076`.

По этим `GoodIds` собран дневной V5 approved package:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260228/
STAS5_V5_MARKET_PASSPORT_20260228_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Контроль:

```text
full guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
rows=81
entry_y 1=10 / 0=71
features=439
fcs=84
duplicates day+candidate_id=0
duplicates record_id=0
cs/fcs source-time violations=0
forbidden target/future columns in X=0
```

Граница: R2 training не запускался, новый forward не запускался. Этот день теперь можно включать в будущий R2 train set как teacher-разметку, но нельзя использовать как независимое доказательство качества R2 после переобучения. Следующий ручной день для закрытия: `2026-03-01`.

## Handoff 2026-07-16 STAS5 V5C WAVE Strip Cumulative Carry Fix

Статус: `PASS_V5C_FORWARD_VISUAL_REVIEW_WAVE_CUMULATIVE_CARRY_NO_BLACK_TAIL`.

Подтверждение пользователя 2026-07-17: `USER_APPROVED_V5C_FORWARD_VISUAL_REVIEW_CHARTS_OK`. Текущий формат графиков принят как рабочий visual-standard для дальнейшего review.

Доработан текущий V5C `visual_review`: WAVE-полоса теперь не обрывается черным хвостом перед следующим днем. Последняя active `LONG/SHORT` волна растягивается до конца доступных свечей дня; если следующий день есть в render range, на подписи ставится перенос `>`, если это последний выгруженный день, волна просто упирается в конец графика.

Проценты в WAVE теперь подписываются как cumulative от настоящего старта волны, а не как отдельный дневной slice. Для cross-day волны видно формат вроде `< W15 SHORT cum 2.07->4.69%`.

Контроль текущего run:

```text
run=STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343
png_count=14
tail_gap_rows_filled_total=7
tail_gap_minutes_filled_total=298.0
rendered_gap_rows_total=0
cross_day_wave_rows_total=13
predictions SHA256 unchanged=true
```

Граница: это только visual review. Training, forward predictions, scores, decisions, thresholds и X439 не менялись.

## Handoff 2026-07-16 STAS5 V5C Forward Visual Review With Continuous Strength Strip

Статус: `PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES`.

Для текущего V5C blind/no-future forward run перерисован `visual_review` с блоком `Fon / LONG / SHORT / WAVE` между price и score. Все текущие маркеры сохранены: желтые `LAxxx`, желтые X для `SKIP`, желтые ромбы для `WATCH`, зеленые треугольники для `ENTER`; длинные ENTER-боксы/стрелки на overview не возвращались.

Run:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343
```

Итог render:

```text
png_count=14
visual manifest=STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343/visual_review/STAS5_V5_FORWARD_VISUAL_REVIEW_MANIFEST_V1.json
continuous strength strip: 7/7 дней через ohlcv_contexts, context_rows=2160 на день
macro WAVE GAP: filtered_gap_rows_total=7, rendered_gap_rows_total=0
predictions SHA256 unchanged=true
```

Граница: это только review-отрисовка. Обучение, forward predictions, `ENTRY_ML_LIVE_SCORE`, `ENTRY_ML_LIVE_DECISION`, X439 и thresholds не менялись.

Открыть графики:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_continuous_forward_20260228_20260306_20260716_155343\visual_review
```

## Handoff 2026-07-16 STAS5 V5C Continuous Train + Blind Forward

Статус: `PASS_V5C_CONTINUOUS_TWO_BLOCK_FORWARD_20260228_20260306_BLIND_NO_FUTURE`.

Собран отдельный непрерывный контур `V5C_CONTINUOUS`, старый дневной V5 не перезаписан. В `V5C` структура `cs_*` и `fcs_*` пересобирается с rolling continuous warmup `720` минут, чтобы midnight не обнулял рынок. При этом no-future правило сохранено: для каждой строки `cs_max_source_time_utc` и `fcs_max_source_time_utc` не позже `entry_time_utc`.

Главный отчет:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_CONTINUOUS_TRAIN_FORWARD_20260716_RU.md
```

Train:

```text
range=2026-01-27..2026-02-27
rows=2596
entry_y 1=290 / 0=2306
features=439
batch guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
train run=STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_continuous_train_20260716_154826
post-train guard=PASS_V5_TWO_BLOCK_POST_TRAIN_GUARD_READY_FOR_FORWARD
```

OOF:

```text
baseline ROC-AUC=0.6569167389418907 PR-AUC=0.17950987215851025
two-block ROC-AUC=0.6597878099111762 PR-AUC=0.18064179174496617
```

Forward:

```text
range=2026-02-28..2026-03-06
rows=576
ENTER=62 / WATCH=121 / SKIP=393
forward run=STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343
visual review=PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES
png_count=14
```

Контроль отсутствия дневного сброса: первый forward-кандидат `2026-02-28 LA001` имеет `cs_context_rows=748` и `cs_rows_240m=240`; значит он видит хвост `2026-02-27`, а не только первые 28 минут нового дня.

Главная команда повтора:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode All -ContextWarmupMinutes 720 -OpenFolder
```

Команда открыть графики текущего V5C forward:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_continuous_forward_20260228_20260306_20260716_155343\visual_review
```

Следующий смысловой шаг: визуально проверить `62 ENTER` на V5C forward и сравнить с дневным V5 (`20 ENTER`) и baseline. Two-block в `V5C` чуть лучше baseline по OOF, но разница маленькая, поэтому без ручного review production-выбор не делать.

## Handoff 2026-07-16 STAS5 V5 Forward Visual Review With All LA Labels

Статус: `PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES`.

Для текущего blind/no-future forward run добавлен и прогнан визуальный слой с полными `LAxxx`-подписями:

```text
STAS5_ML_CORE/artifacts/v5/forward/runs/stas5_v5_forward_20260228_20260306_20260716/visual_review/
```

Создан код:

```text
src/mlbotnav/stas5_v5_forward_visual_review.py
tests/test_stas5_v5_forward_visual_review.py
```

Обновлено:

```text
src/mlbotnav/stas5_v5_two_block_ml.py
STAS5_ML_CORE/run_stas5_v5_two_block_ml.ps1
```

Теперь V5 forward по умолчанию после predictions строит обзорные PNG и closeup-листы. Для уже готового прогона можно перерендерить визуальный слой без обучения:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_two_block_ml.ps1 -Mode RenderForward -ForwardRunId stas5_v5_forward_20260228_20260306_20260716 -ForwardStartDay 2026-02-28 -ForwardEndDay 2026-03-06 -OpenFolder
```

Результат текущего render: `png_count=14`, по каждому из 7 дней создан overview `*_ENTER_ARROWS.png` и closeups `*_ENTER_CLOSEUPS_YYYYMMDD.png`. На overview все кандидаты подписаны желтым `LAxxx`; `SKIP` показан желтым X, `WATCH` - маленьким желтым ромбом, `ENTER` - зеленым треугольником. Длинные зеленые стрелки и боксы `ENTER` убраны. Это визуальный слой review-only: он не переобучает модель, не меняет score/decision и не добавляет future в X.

Дополнительная правка по замечанию пользователя: подписи `LAxxx` больше не раскладываются случайными смещениями. Они сортируются по номеру кандидата (`LA001`, `LA002`, ...), ставятся структурно над своей точкой и соединяются с точкой тонкой желтой линией.

## Handoff 2026-07-16 STAS5 V5 Two-Block Train + Blind Forward

Статус: `PASS_TRAIN_AND_FORWARD_DONE_REVIEW_REQUIRED`.

Выполнен полный проход V5 two-block ML:

```text
train:   2026-01-27..2026-02-27, 32 days, 2596 rows, X439
forward: 2026-02-28..2026-03-06, 7 days, 576 rows, blind/no-future
```

Создан код:

```text
src/mlbotnav/stas5_v5_two_block_ml.py
STAS5_ML_CORE/run_stas5_v5_two_block_ml.ps1
tests/test_stas5_v5_two_block_ml.py
```

Training run:

```text
STAS5_ML_CORE/artifacts/v5/model/runs/stas5_v5_two_block_train_20260716_32d/
```

Training guard: `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`.
Post-train guard: `PASS_V5_TWO_BLOCK_POST_TRAIN_GUARD_READY_FOR_FORWARD`.

OOF metrics:

```text
ENTRY_BASELINE_ML ROC-AUC=0.6564150491969973 PR-AUC=0.181311573028207
ENTRY_ML two-block ROC-AUC=0.6377471064987889 PR-AUC=0.15605847999619604
phase accuracy=0.223421 macro-F1=0.110356
state accuracy=0.123267 macro-F1=0.031507
```

Вывод: two-block технически собран и guard-safe, но по OOF хуже baseline. Его нельзя считать production-победителем без review; baseline остается контрольным кандидатом.

Forward run:

```text
STAS5_ML_CORE/artifacts/v5/forward/runs/stas5_v5_forward_20260228_20260306_20260716/
```

Forward guard: `PASS_V5_TWO_BLOCK_FORWARD_20260228_20260306_BLIND_NO_FUTURE`.

Forward decisions:

```text
rows=576
ENTER=20
WATCH=120
SKIP=436
```

Итоговый отчет:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_TWO_BLOCK_TRAIN_FORWARD_20260716_RU.md
```

Следующий шаг: ручной/визуальный review 20 `ENTER` на forward и отдельное сравнение с baseline-forward, прежде чем выбирать production-схему.

## Handoff 2026-07-16 STAS5 V5 Two-Block ML TZ

Статус: `TZ_DRAFT_READY_FOR_USER_REVIEW_NO_TRAINING`.

По просьбе пользователя вместе с агентом Hume расписано ТЗ следующего этапа V5 ML:

```text
STAS5_ML_CORE/09_STAS5_V5_TWO_BLOCK_ML_TZ_RU.md
```

ТЗ фиксирует рабочую архитектуру:

```text
X439 -> ENTRY_BASELINE_ML -> entry_y
X439 -> MARKET_PHASE_STATE_ML -> phase_y/state_y predictions
X439 + OOF/live phase/state predictions -> ENTRY_ML -> entry_y
```

Главное правило: на закрытой истории можно учиться по teacher/targets, но в `X` модели входят только causal `439` features из batch allowlist. Настоящие `phase_y/state_y/reason_y/entry_y` не являются live features. Для `ENTRY_ML` разрешены только OOF predictions первого блока на train и live predictions первого блока на forward.

ТЗ отдельно требует baseline, day-group OOF для stacking, walk-forward audit для честной live-оценки, training guard до обучения и post-train guard до forward. Training и forward в рамках этой фиксации не запускались.

Следующий практический шаг: реализовать `STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1`, получить `PASS`, и только после этого отдельной командой переходить к baseline/training.

## Handoff 2026-07-16 STAS5 V5 Batch Dataset And Guard 2026-01-27..2026-02-27

Статус: `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING`.

Собран единый V5 batch dataset по диапазону:

```text
2026-01-27..2026-02-27
```

Итоговые счетчики: `32/32` дня присутствуют, `2596` строк, `entry_y 1=290 / 0=2306`, feature contract `274 old causal + 81 cs_* + 84 fcs_* = 439`. Allowlist одинаковый у всех 32 дней.

Создано:

```text
src/mlbotnav/stas5_v5_batch_dataset_builder.py
STAS5_ML_CORE/run_stas5_v5_batch_dataset_builder.ps1
tests/test_stas5_v5_batch_dataset_builder.py
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_ML_READY_439F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_FEATURE_ALLOWLIST_439F_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_MANIFEST_V1.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_AUDIT_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_GUARD_V1.json
```

Batch guard `PASS`: targets/manual columns не входят в `X`, forbidden future/postfact/hit_/TP/Stas3/exit/old ML/full-group признаки в allowlist отсутствуют, `cs_max_source_time_utc <= entry_time_utc`, `fcs_max_source_time_utc <= entry_time_utc`, дублей `day+candidate_id` и `day+record_id` нет, обязательные feature values после batch-нормализации не пустые.

В batch builder зафиксирована нормализация только для `X`: `398` числовых пропусков в исходных daily feature columns заполнены `0`, после этого `feature_nulls=0`. Targets и teacher-поля не используются как признаки.

Обучение и forward V5 не запускались. Следующий шаг: отдельный training guard и подготовка two-block ML `MARKET_PHASE_STATE_ML -> ENTRY_ML`, где `ENTRY_ML` получает только OOF/live predictions первого блока, не настоящие `phase_y/state_y`.

## Handoff 2026-07-16 STAS5 V5 Range Audit 2026-01-27..2026-02-27

Статус: `PASS_V5_RANGE_AUDIT_READY_FOR_BATCH_DATASET`.

Проверен и закрыт диапазон V5:

```text
2026-01-27..2026-02-27
```

Финальные счетчики: `32/32` full-ready дня, `2596` строк, `entry_y 1=290 / 0=2306`, feature contract `274 -> 355 -> 439`, problem count `0`.

Во время аудита исправлено: `2026-02-07` был missing/partial, потому что существовал только FULL274 run без V5 market passport/map. День пересобран по утвержденным GOOD ids:

```text
LA004, LA007, LA010, LA012, LA020, LA023, LA030, LA034, LA035, LA041, LA044, LA046, LA050, LA052, LA058
```

После исправления `2026-02-07`: `rows=69`, `entry_y 1=15 / 0=54`, `features=439`, guard `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

Главные отчеты:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_RANGE_AUDIT_20260127_20260227_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_RANGE_AUDIT_20260127_20260227.json
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715.json
```

Обучение V5 и forward V5 не запускались. Следующий шаг: реализовать/собрать `V5 batch dataset` и `batch leakage/no-future guard`; только после guard `PASS` переходить к двум ML-блокам `MARKET_PHASE_STATE_ML -> ENTRY_ML`.

## Handoff 2026-07-15 STAS5 V5 Audit 2026-02-01

Статус: `PASS_V5_FOLDER_AUDIT_NO_TRAINING`.

Проверен последний полный пакет:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260201/
```

Главный файл:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260201/STAS5_V5_MARKET_PASSPORT_20260201_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Итог по `2026-02-01`: `rows=89`, `entry_y 1=14 / 0=75`, `features=439`, `levels=34`, `channels=89`, `regimes=64`, `events=3402`.

GOOD ids совпадают с пользовательской разметкой: `LA007`, `LA014`, `LA026`, `LA040`, `LA041`, `LA045`, `LA053`, `LA058`, `LA060`, `LA066`, `LA079`, `LA082`, `LA084`, `LA087`.

Guard-и:

```text
PHASE_STATE_REASON_GUARD_V2 = PASS_NO_TRAINING_PHASE_STATE_REASON_READY
CAUSAL_STRUCTURE_GUARD_V1 = PASS_NO_TRAINING_CAUSAL_STRUCTURE_READY
FULL_CAUSAL_STRUCTURE_GUARD_V1 = PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

V5 folder audit показывает `full-ready=6`, `partial/not-ready=27`, `model=False`, `forward=False`. Обучение и forward V5 не запускались.

По архитектуре подтверждено два будущих ML-блока: `MARKET_PHASE_STATE_ML` и `ENTRY_ML`. Сейчас реализованы builders/guards/data packages, а не обученные модели.

## Handoff 2026-07-15 STAS5 V5 Approved Passport Builder And 2026-01-28 Ready

Статус: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

Добавлен универсальный builder, который превращает утвержденный пользователем список хороших входов дня в обязательный V5 approved-passport слой:

```text
src/mlbotnav/stas5_v5_approved_passport_builder.py
STAS5_ML_CORE/run_stas5_v5_approved_passport_builder.ps1
```

Главная команда для следующего дня теперь может идти одной лестницей:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage All -GoodIds LA020,LA037,LA042,LA045,LA051,LA059,LA069,LA078,LA084
```

По `2026-01-28` собран полный V5-пакет:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260128/
```

Счетчики: `93` кандидата, `entry_y 1=9 / 0=84`, baseline `274` признака, после `cs_*` - `355`, после `fcs_*` - `439`. GOOD ids: `LA020`, `LA037`, `LA042`, `LA045`, `LA051`, `LA059`, `LA069`, `LA078`, `LA084`.

Главный CSV дня:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260128/STAS5_V5_MARKET_PASSPORT_20260128_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Главная карта:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260128/DAY_MARKET_PASSPORT_20260128_FULL_CAUSAL_STRUCTURE_MAP_V1.png
```

Guard-и:

```text
PHASE_STATE_REASON_GUARD_V2 = PASS_NO_TRAINING_PHASE_STATE_REASON_READY
CAUSAL_STRUCTURE_GUARD_V1 = PASS_NO_TRAINING_CAUSAL_STRUCTURE_READY
FULL_CAUSAL_STRUCTURE_GUARD_V1 = PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

Аудит V5-папки теперь показывает `full-ready=2`, `partial/not-ready=31`, `model=False`, `forward=False`. Обучение и forward не запускались.

## Handoff 2026-07-15 STAS5 V5 Day Ladder And Folder Audit

Статус: `PASS_V5_FOLDER_AUDIT_NO_TRAINING`.

Добавлена главная лесенка для следующего дня:

```text
STAS5_ML_CORE/run_stas5_v5_day_ladder.ps1
```

Главная команда:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage All -OpenFolder
```

Режимы: `Collect`, `BuildApproved`, `Audit`, `Open`, `All`.

Поведение проверено:

```text
2026-01-27 Stage All - PASS, rows=75, features=439, fcs=84
2026-01-28 Stage All - FULL274 найден, approved passport отсутствует, команда остановилась на ручном этапе
```

Добавлен полный аудит V5-папки:

```text
src/mlbotnav/stas5_v5_folder_audit.py
STAS5_ML_CORE/run_stas5_v5_folder_audit.ps1
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_FOLDER_AUDIT_20260715.json
```

Аудит: `full-ready=1`, `partial/not-ready=32`, `full274 runs=33`, `model=False`, `forward=False`.

Граница: лесенка не создает ручные labels сама. Если нет approved `ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2` и связанных files, команда останавливается и сообщает, что нужен ручной approved passport.

## Handoff 2026-07-15 STAS5 V5 Full Causal Market-Structure Builder

Статус: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

По V5-пакету `2026-01-27` создан полный causal market-structure builder:

```text
src/mlbotnav/stas5_v5_full_causal_structure_builder.py
STAS5_ML_CORE/run_stas5_v5_full_causal_structure_builder.ps1
```

Команда сборки:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_full_causal_structure_builder.ps1 -Day 2026-01-27
```

Главный текущий CSV для будущего обучения:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Счетчики: `75` строк, `439` feature columns всего: `355` признаков до full-слоя (`274 + cs_*`) и `84` новых `fcs_*` признака. Targets: `entry_y 1=11 / 0=64`; хорошие входы `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062`.

Новые артефакты:

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

Guard `PASS`: нет forbidden features, targets не попали в feature allowlist, `fcs_max_source_time_utc < entry_time_utc`, merge one-to-one, missing `fcs_*` values `0`, события не выходят за день. Счетчики структуры: `levels=19`, `channels=75`, `regimes=53`, `events=2833`.

Обновлена навигация:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/00_OPEN_FIRST_RU.md
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/README_RU.md
```

Граница: ручной паспорт и `entry_y/phase_y/state_y/reason_y` являются teacher/targets `y`; прямые признаки `X` теперь `274 + cs_* + fcs_*`. Обучение V5 и V5 forward не запускались.

## Handoff 2026-07-15 STAS5 V5 Causal Market-Structure Builder Previous `cs_*` Layer

Статус: `PASS_NO_TRAINING_CAUSAL_STRUCTURE_READY`. Это предыдущий `cs_*` слой. Текущий главный слой находится выше: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

По V5-пакету `2026-01-27` создан отдельный causal market-structure builder:

```text
src/mlbotnav/stas5_v5_causal_structure_builder.py
STAS5_ML_CORE/run_stas5_v5_causal_structure_builder.ps1
```

Команда проверки/сборки:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_causal_structure_builder.ps1 -Day 2026-01-27
```

Прямой Python-вариант:

```powershell
$env:PYTHONPATH='src'
python -m mlbotnav.stas5_v5_causal_structure_builder --day 2026-01-27
```

Предыдущий `cs_*` CSV, который используется как source/base для full-слоя:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Счетчики: `75` строк, `274` старых causal-признака, `81` новый `cs_*` causal market-structure признак, всего `355` feature columns. Targets: `entry_y 1=11 / 0=64`; хорошие входы `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062`.

Guard:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_GUARD_V1.json
```

Guard `PASS`: нет forbidden features, targets не попали в feature allowlist, `cs_max_source_time_utc < entry_time_utc`, merge one-to-one, missing numeric values `0`.

Обновлена навигация:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/00_OPEN_FIRST_RU.md
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/README_RU.md
```

Проектный аудит V5:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_PROJECT_AUDIT_20260715_RU.md
STAS5_ML_CORE/artifacts/v5/STAS5_V5_PROJECT_AUDIT_20260715.json
```

Граница: ручной паспорт и `entry_y/phase_y/state_y/reason_y` являются teacher/targets `y`; в этом предыдущем слое прямые признаки `X` = `274 + cs_*`. Для текущей работы использовать full-слой `274 + cs_* + fcs_*`. Обучение V5 и V5 forward не запускались.

## Handoff 2026-07-15 STAS5 V5 Market Passport 2026-01-27 Phase/State/Reason Ready

Статус: `PASS_NO_TRAINING_PHASE_STATE_REASON_READY`.

В папке `STAS5_ML_CORE/artifacts/v5/market_passports/20260127/` создан актуальный V2-слой для обучения будущего V5:

```text
STAS5_V5_MARKET_PASSPORT_20260127_PHASE_SEGMENTS_USER_APPROVED_V1.csv
STAS5_V5_MARKET_PASSPORT_20260127_ENTRY_PHASE_STATE_REASON_LEDGER_USER_APPROVED_V2.csv
STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv
STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json
STAS5_V5_MARKET_PASSPORT_20260127_PHASE_STATE_REASON_GUARD_V2.json
TRAINING_SCHEMA_ENTRY_PHASE_STATE_REASON_RU.md
```

Счетчики: `75` строк, `274` feature, `entry_y 1=11 / 0=64`, `phase_y`: `P1=15`, `P2=26`, `P3=6`, `P4=7`, `P5=21`, forbidden features `[]`.

GOOD ids остались ровно пользовательские: `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062`.

Важно: `phase_y/state_y/reason_y` добавлены как target-ответы учителя. В `X` они не входят. Обучение, API, TP/Stas3, threshold tuning не запускались.

## Handoff 2026-07-15 STAS5 V5 Market Passport 2026-01-27 User Approved V3

Статус: `USER_APPROVED_V3_NO_TRAINING`.

Пользователь проверил график `2026-01-27` и подтвердил: оставить только его `11` входов, остальные кандидаты хуже. GOOD-входы: `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062`.

Финальные счетчики: `GOOD_APPROVED=11`, `BAD_IN_GROUP=50`, `NO_TRADE_ZONE=14`, `TOTAL=75`. `GOOD_ALT` и `REVIEW_ONLY` для этого дня больше не активны; бывшие спорные `LA001`, `LA014`, `LA015`, `LA017`, `LA025`, `LA041`, `LA043`, `LA053`, `LA056`, `LA057`, `LA059`, `LA066`, `LA067`, `LA068`, `LA070` переведены в отрицательные примеры.

Актуальные файлы:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_LEDGER_20260127_USER_APPROVED_V3.csv
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_USER_APPROVED_RU.md
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_USER_APPROVED_V3_ANNOTATED_TOP.png
```

Не запускалось: обучение, API, TP/Stas3, threshold tuning. Следующий шаг - добавлять этот день в общую январскую approved-базу, когда будут готовы остальные дни.

День упакован отдельно:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/
```

В пакете есть:

```text
STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_LABELS_V1.csv
STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_V1.json
STAS5_V5_MARKET_PASSPORT_20260127_MARKET_STRUCTURE_NUMERIC_V1.csv
STAS5_V5_MARKET_PASSPORT_20260127_274F_LABELS_PLUS_STRUCTURE_CONTEXT_V1.csv
STAS5_V5_MARKET_PASSPORT_20260127_PACKAGE_MANIFEST.json
```

Проверка пакета: `PASS_NO_TRAINING`, `rows=75`, `feature_count=274`, `train_label_binary 1=11 / 0=64`, forbidden feature columns `[]`.

Уточнение по схеме обучения: ручная структура рынка не выброшена и не является "отдельной ненужной таблицей". Она является `TEACHER / PASSPORT` и формирует правильный ответ `y` для обучения. Входные признаки `X` сейчас берутся из `274` causal-признаков; прямые структурные признаки можно добавлять в `X` только после causal market-structure builder, который строит фазы/поддержки/сопротивления без будущего.

## Handoff 2026-07-15 STAS5 V5 Market Passport 2026-01-27 V2

Статус: `DRAFT_V2_NO_TRAINING`.

Актуальная работа сейчас по январю: `2026-01-27`, run:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857
```

Пользователь утвердил `11` GOOD-входов: `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062`.

По агентскому read-only разбору и FULL274/OHLCV создан V2 draft ledger на все `75` кандидатов: `GOOD_APPROVED=11`, `GOOD_ALT=8`, `REVIEW_ONLY=7`, `BAD_IN_GROUP=35`, `NO_TRADE_ZONE=14`.

Актуальные файлы:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_LEDGER_20260127_DRAFT_V2.csv
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_RU.md
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_20260127_LABELS_DRAFT_V2_ANNOTATED_TOP.png
```

Не запускалось: обучение, API, TP/Stas3, threshold tuning. Следующий шаг - ручная проверка `GOOD_ALT` и `REVIEW_ONLY`, затем перевод дня в approved numeric ledger.

## Handoff 2026-07-15 STAS5 V5 Market Passport Trial 2026-01-27

Статус: `DRAFT_VISUAL_REVIEW_ONLY_NO_TRAINING`.

По пользовательской задаче создан пробный рыночный паспорт на оригинальном PNG из:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857
```

Проверено агентами и локально: `rows=75`, `features=274`, `labels=UNLABELED_VISUAL_ONLY`, `training_started=false`. `visual CUT=75` является служебным состоянием unlabeled-run и не должен использоваться как negative label.

Артефакты:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_ANNOTATED_TOP.png
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_DRAFT_ZONES.csv
STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_RU.md
```

Пробный смысл: `LA025/LA026`, `LA041/LA042`, `LA052-LA054` target-good draft; `LA048-LA051`, `LA069/LA075` no-buy/bad draft; остальные выделенные зоны review. Следующий шаг - пользовательская сверка картинки, затем approved label ledger.

## Handoff 2026-07-15 STAS5 FULL274 Feature Collect Wrapper

Статус: `PASS`.

Добавлен и проверен wrapper:

```text
STAS5_ML_CORE/run_stas5_full274_feature_collect.ps1
```

Команда:

```powershell
.\STAS5_ML_CORE\run_stas5_full274_feature_collect.ps1 -Day 2026-04-01 -OpenFolder
```

Собирает один день до обучения:

```text
STAS1 -> STAS2 -> V1 111 -> V2/STAS4/STAS5 163 -> FULL274 -> visual approval PNG
```

Контрольный run:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260401_20260715_084509/
rows=81
features=274
v1_features=111
v2_features=163
training_started=false
```

Важно: команда не запускает ML training, API, TP/Stas3. Рендерер `stas5_v2_feature_visual_approval.py` изменен визуально: CUT-крестики и подписи LAxxx ярко-желтые, без увеличения толщины.

## Актуальный источник правды STAS5 V4

Для текущего V4 group-rank состояния использовать верхние свежие секции этого файла и guard:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Текущий факт: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Старые append-only секции ниже могут содержать промежуточные счетчики прошлых шагов и являются историей, а не текущим состоянием.

## Handoff 2026-07-14 STAS5 V4 2026-05-25 Screenshot Check V1

Статус: `STAS5_V4_20260525_USER_CHECKED_PASS_NO_TRAINING`.

По пользовательскому скрину `2026-05-25` проверены два красных круга. CSV-правка не нужна: обе отмеченные зоны уже совпали с текущим day25 draft ledger.

Проверка:

```text
первый pre-London круг = серый/skip-низ LA020, уже BEST_GOOD
рядом LA019 = GOOD_ALT, потому что LA020 ниже
второй late-London круг = LA038, уже BEST_GOOD
```

Актуальные winners `2026-05-25` без изменений: `LA014`, `LA020`, `LA038`, `LA059`, `LA066`. Counts day25: `68` строк, `BEST_GOOD=5`, `GOOD_ALT=4`, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=19`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_REVIEW_20260525_USER_CHECKED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_LEDGER_20260525_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_20260525_PRE_LONDON_LA019_LA020_WIDE_CROP.png
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_20260525_USER_CIRCLE_LA038_CROP.png
```

Unified ledger не менялся после day23: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-24 Screenshot Check V1

Статус: `STAS5_V4_20260524_USER_CHECKED_PASS_NO_TRAINING`.

По пользовательскому скрину `2026-05-24` проверены красные круги. CSV-правка не нужна: отмеченные зоны уже совпали с day24 draft ledger.

Проверка:

```text
левый круг перед Лондоном = LA015, уже BEST_GOOD
overlap crash круг = LA042, уже BEST_GOOD
поздний deep-low справа = LA065, уже BEST_GOOD
LA067 = GOOD_ALT, не главный winner, потому что выше после V-отскока
```

Актуальные winners `2026-05-24` без изменений: `LA009`, `LA015`, `LA024`, `LA042`, `LA065`. Counts day24: `70` строк, `BEST_GOOD=5`, `GOOD_ALT=5`, `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=6`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_REVIEW_20260524_USER_CHECKED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_LEDGER_20260524_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/day24_user_circle_left_pre_london_x5.png
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/day24_user_circle_LA042_x5.png
```

Unified ledger не менялся после day23: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-23 Screenshot Check V1

Статус: `STAS5_V4_20260523_USER_CORRECTED_V1_NO_TRAINING`.

По пользовательскому скрину `2026-05-23` проверены красные круги справа от утреннего падения. Главная ошибка draft: recovery-группа `LA034..LA042` была слишком широкой и заставляла разные отмеченные входы конкурировать с одним winner `LA036`.

Исправление:

```text
G20260523_004A_1337_1403: LA034 BEST_GOOD, LA035 BAD_DUPLICATE_NOT_LOWEST
G20260523_004B_1536_1626: LA036 BEST_GOOD, LA037/LA038 BAD рядом
G20260523_004C_1700_1744: LA042 BEST_GOOD, LA039/LA040/LA041 BAD рядом
```

Актуальные winners `2026-05-23`: `LA007`, `LA022`, `LA033`, `LA034`, `LA036`, `LA042`, `LA051`. Counts day23: `63` строки, `BEST_GOOD=7`, `GOOD_ALT=4`, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=12`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_REVIEW_20260523_USER_CORRECTED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/day23_user_circles_all_wide.png
```

Unified `2026-05-15..2026-05-25` после правки day23: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit: `GOOD_ALT_MAY_NEED_MICRO_GROUP=39`, `BEST_GOOD_FROM_OLD_NON_ENTER=28`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`.

Граница: обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-22 Screenshot Check V1

Статус: `STAS5_V4_20260522_USER_CORRECTED_V1_NO_TRAINING`.

По свежему пользовательскому скрину `2026-05-22` проверены красные круги/подчеркивания. Главная правка точечная: в группе `05:36-09:01` старый draft выбрал ранний low `LA022` как `BEST_GOOD`, но пользовательский круг стоит на позднем ретесте `LA024`.

Исправление:

```text
LA022: BEST_GOOD -> GOOD_ALT
LA024: GOOD_ALT -> BEST_GOOD
```

Остальные видимые целевые зоны совпали с таблицей: `LA007`, `LA036`, `LA047`, `LA061` остаются `BEST_GOOD`.

Актуальные winners `2026-05-22`: `LA007`, `LA024`, `LA036`, `LA047`, `LA061`. Counts day22 не изменились: `75` строк, `BEST_GOOD=5`, `GOOD_ALT=4`, `BAD_IN_GROUP=55`, `NO_TRADE_GROUP=11`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_LEDGER_20260522_USER_CORRECTED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_REVIEW_20260522_USER_CORRECTED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/day22_circle_2_pre_london_x5.png
```

Unified `2026-05-15..2026-05-25` после правки day22: `738` строк, `BEST_GOOD=62`, `GOOD_ALT=43`, `BAD_IN_GROUP=434`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit totals не изменились: `GOOD_ALT_MAY_NEED_MICRO_GROUP=40`, `BEST_GOOD_FROM_OLD_NON_ENTER=26`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`; day22 summary теперь winners `LA007,LA024,LA036,LA047,LA061`, good-alt `LA005,LA022,LA043,LA062`.

Граница: обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-21 Screenshot Check V1

Статус: `STAS5_V4_20260521_USER_CORRECTED_V1_NO_TRAINING`.

По пользовательскому скрину `2026-05-21` с четырьмя красными кругами проверены отмеченные markers:

```text
LA006 = уже был BEST_GOOD, совпадает
LA039 = был BAD_IN_GROUP, стал отдельным BEST_GOOD
LA050 = был BAD_IN_GROUP, стал отдельным BEST_GOOD
LA057 = был GOOD_ALT, стал отдельным BEST_GOOD
```

Широкая sell-wave группа `LA022..LA050` разделена на три micro-groups:

```text
G20260521_003A_0823_1213: LA022..LA040, winner LA039, alt LA040
G20260521_003B_1231_1345: LA041..LA045, winner LA045
G20260521_003C_1408_1449: LA046..LA050, winner LA050, alt LA048
```

Pre-breakout группа `LA051..LA060` разделена на две micro-groups:

```text
G20260521_004A_1508_1637: LA051..LA057, winner LA057
G20260521_004B_1642_1709: LA058..LA060, winner LA059
```

Актуальные winners `2026-05-21`: `LA006`, `LA019`, `LA039`, `LA045`, `LA050`, `LA057`, `LA059`, `LA066`. Counts: `81` строка, `BEST_GOOD=8`, `GOOD_ALT=4`, `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=15`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_LEDGER_20260521_USER_CORRECTED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_REVIEW_20260521_USER_CORRECTED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/day21_user_circles_all_wide_x3.png
```

Unified `2026-05-15..2026-05-25` после правки day21: `738` строк, `BEST_GOOD=62`, `GOOD_ALT=43`, `BAD_IN_GROUP=434`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit обновлен: `GOOD_ALT_MAY_NEED_MICRO_GROUP=40`, `BEST_GOOD_FROM_OLD_NON_ENTER=26`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`.

Граница: обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-20 Screenshot Check V1

Статус: `STAS5_V4_20260520_USER_CORRECTED_V1_NO_TRAINING`.

По пользовательскому скрину `2026-05-20` с двумя красными кругами проверена зона `13:19-14:26`. Нижний круг совпал с уже выбранным `LA037` (`BEST_GOOD` crash-low retest). Верхний круг оказался серым/skip-кандидатом `LA038`, который draft ошибочно держал плохим соседом внутри той же crash-low группы.

Исправление:

```text
G20260520_003A_1319_1413: LA033..LA037, winner LA037, alt LA035
G20260520_003B_1426_1507: LA038..LA039, winner LA038
```

`LA038` стал `BEST_GOOD` с reason `GOOD_PULLBACK_LOW_AFTER_REACTION;GOOD_FIRST_LOW_AFTER_FLUSH`. `LA039` добавлен как плохой поздний/высокий сосед старого `ENTER`. Это отдельная micro-group продолжения после отскока, а не проигравший дубль `LA037`.

Актуальные winners `2026-05-20`: `LA011`, `LA037`, `LA038`, `LA045`, `LA053`, `LA057`. Counts: `68` строк, `BEST_GOOD=6`, `GOOD_ALT=4`, `BAD_IN_GROUP=27`, `NO_TRADE_GROUP=31`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_LEDGER_20260520_USER_CORRECTED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_REVIEW_20260520_USER_CORRECTED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/day20_user_circles_transition_wide_x4.png
```

Unified `2026-05-15..2026-05-25` после правки day20: `738` строк, `BEST_GOOD=59`, `GOOD_ALT=44`, `BAD_IN_GROUP=436`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit обновлен: `GOOD_ALT_MAY_NEED_MICRO_GROUP=41`, `BEST_GOOD_FROM_OLD_NON_ENTER=24`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`.

Граница: обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-19 Screenshot Check V1

Статус: `STAS5_V4_20260519_USER_CORRECTED_V1_NO_TRAINING`.

По пользовательскому скрину `2026-05-19` с красной обводкой в overlap/retest зоне исправлена слишком широкая V4 draft-группа. Старый draft держал `LA034..LA047` в одной группе и оставлял `LA046` только `GOOD_ALT`, потому что главным low был `LA042`. По новому скрину `LA046` является отдельным человеческим retest/base входом после `LA042`, поэтому группа разделена:

```text
G20260519_005A_1308_1449: LA034..LA042, winner LA042
G20260519_005B_1525_1610: LA043..LA047, winner LA046
```

Визуальная подпись с `0.86` соответствует строке `LA046` в CSV. `LA045` остается `BAD_IN_GROUP` как более ранний/высокий сосед, `LA047` оставлен `GOOD_ALT` как соседний нижний дубль той же retest-зоны.

Актуальные winners `2026-05-19`: `LA005`, `LA016`, `LA032`, `LA042`, `LA046`, `LA063`. Counts: `65` строк, `BEST_GOOD=6`, `GOOD_ALT=3`, `BAD_IN_GROUP=39`, `NO_TRADE_GROUP=17`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_LEDGER_20260519_USER_CORRECTED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_REVIEW_20260519_USER_CORRECTED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/day19_user_circle_LA045_zone.png
```

Unified `2026-05-15..2026-05-25` после правки day19: `738` строк, `BEST_GOOD=58`, `GOOD_ALT=44`, `BAD_IN_GROUP=437`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit обновлен; общий risk-count не изменился: `GOOD_ALT_MAY_NEED_MICRO_GROUP=41`, `BEST_GOOD_FROM_OLD_NON_ENTER=23`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`.

Граница: обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-18 Screenshot Check V1

Статус: `STAS5_V4_20260518_USER_CORRECTED_V1_NO_TRAINING`.

По пользовательскому скрину `2026-05-18` со свежими красными обводками исправлена старая V4 draft-разметка. Две зоны были ошибочно проглочены широкими/no-trade группами:

```text
LA036 -> BEST_GOOD, отдельный pullback/retest после импульса вверх
LA066 -> BEST_GOOD, отдельный late NY retest после вертикального движения
```

Ранний круг `LA005/LA006`, круг `LA034` и нижний круг `LA059/LA061` совпали с текущей логикой: `LA006`, `LA034`, `LA061` остаются winners; `LA005` и `LA059` остаются `GOOD_ALT`.

Актуальные winners `2026-05-18`: `LA006`, `LA019`, `LA034`, `LA036`, `LA049`, `LA061`, `LA066`. Counts: `73` строки, `BEST_GOOD=7`, `GOOD_ALT=7`, `BAD_IN_GROUP=52`, `NO_TRADE_GROUP=7`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_LEDGER_20260518_USER_CORRECTED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_REVIEW_20260518_USER_CORRECTED_V1_RU.md
```

Unified `2026-05-15..2026-05-25` после правки day18: `738` строк, `BEST_GOOD=57`, `GOOD_ALT=44`, `BAD_IN_GROUP=438`, `NO_TRADE_GROUP=199`, guard `PASS`. Risk audit обновлен: `GOOD_ALT_MAY_NEED_MICRO_GROUP=41`, `BEST_GOOD_FROM_OLD_NON_ENTER=23`, `OLD_ENTER_DEMOTED_TO_BAD_OR_NO_TRADE=118`.

Граница: обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-17 Screenshot Check V1

Статус: `STAS5_V4_20260517_USER_CHECKED_V1_NO_TRAINING`.

По пользовательскому скрину `2026-05-17` сверена текущая V4 draft-разметка. Красные нижние отметки совпадают с уже стоящими winners: `LA004`, `LA006`, `LA036`, `LA046`, `LA063`. Близкие, но не главные точки остаются `GOOD_ALT`: `LA003`, `LA005`, `LA044`. CSV за день не менялся, потому что расхождения со скрином не найдено.

Проверочный отчет:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_REVIEW_20260517_USER_CHECKED_V1_RU.md
```

Актуальный day17 CSV остается:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_LEDGER_20260517_DRAFT.csv
```

Итог day17: `63` строки, `BEST_GOOD=5`, `GOOD_ALT=3`, `BAD_IN_GROUP=25`, `NO_TRADE_GROUP=30`. Обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-16 Screenshot Check V1

Статус: `STAS5_V4_20260516_USER_CORRECTED_V1_NO_TRAINING`.

По пользовательскому скрину `2026-05-16` проверена draft-разметка. Красные рабочие зоны на скрине соответствуют `LA016`, `LA027`, `LA038`, `LA041`. Старый draft дополнительно держал `LA049` как `BEST_GOOD`, но на предоставленном скрине эта зона не подчеркнута. `LA049` снят из winners, группа `G20260516_007_1302_1413` переведена в `NO_TRADE_GROUP`.

Актуальный day16 CSV:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_LEDGER_20260516_USER_CORRECTED_V1.csv
```

Unified `2026-05-15..2026-05-25` после правки `2026-05-16`: `738` строк, `BEST_GOOD=55`, `GOOD_ALT=43`, `BAD_IN_GROUP=437`, `NO_TRADE_GROUP=203`, guard `PASS`. Аудит micro-group риска пересчитан: `BEST_GOOD_FROM_OLD_NON_ENTER=21`.

Граница: обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-15 Micro-Group Correction V2

Статус: `STAS5_V4_20260515_MICRO_GROUP_V2_FIXED_NO_TRAINING`.

Исправлена методическая ошибка в разметке `2026-05-15`: человечески подчеркнутые желтые ромбики и серые крестики не являются вторичными только потому, что старый ML не дал им `ENTER`. Старый статус `ENTER/UNSURE/SKIP` теперь считается только контекстом. Если пользователь отметил точку как отдельный нижний вход, она может быть `BEST_GOOD` внутри своей micro-group.

Старая V1-группа `G20260515_001_0122_0235` была слишком широкой и ошибочно понижала `LA004` до `GOOD_ALT`, потому что `LA007` ниже. В V2 она разбита:

```text
G20260515_001A_0122_0203: winner LA004
G20260515_001B_0222_0235: winner LA007
```

Актуальные winners `2026-05-15`: `LA004`, `LA007`, `LA021`, `LA024`, `LA054`, `LA061`. Day15 summary: `41` строка, `BEST_GOOD=6`, `GOOD_ALT=3`, `BAD_IN_GROUP=26`, `NO_TRADE_GROUP=6`.

Unified `2026-05-15..2026-05-25` после правки: `738` строк, `BEST_GOOD=56`, `GOOD_ALT=43`, `BAD_IN_GROUP=443`, `NO_TRADE_GROUP=196`, guard `PASS`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_USER_CORRECTED_V2.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V2_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json
```

Создан аудит риска для `2026-05-16..2026-05-25`, чтобы не пересобирать все 10 графиков вслепую:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_MICRO_GROUP_RISK_AUDIT_20260516_20260525_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_MICRO_GROUP_RISK_AUDIT_20260516_20260525.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_MICRO_GROUP_RISK_AUDIT_20260516_20260525_SUMMARY.csv
```

Главный следующий ручной шаг после исправления `2026-05-18`: проверять не все подряд, а оставшиеся `GOOD_ALT_MAY_NEED_MICRO_GROUP=41`, особенно дни `2026-05-21`, `2026-05-23`, `2026-05-24`. Обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 Screenshot Artifact Inventory 2026-05-01..2026-05-25

Статус: `STAS5_V4_SCREENSHOT_ARTIFACT_INVENTORY_DONE_NO_TRAINING`.

По запросу пользователя выполнена инвентаризация рабочих PNG-артефактов для ручного пролистывания:

```text
train_base_14 = 2026-05-01..2026-05-14
forward_review_11 = 2026-05-15..2026-05-25
```

Создана навигационная папка:

```text
STAS5_ML_CORE/artifacts/v4/review_navigation/20260714_artifact_inventory
```

В ней лежат контакт-листы и индекс:

```text
CONTACT_SHEET_20260501_20260514_TRAIN_VISUAL_APPROVAL.png
CONTACT_SHEET_20260515_20260525_FORWARD_SOURCE.png
CONTACT_SHEET_20260515_20260525_V4_GROUP_BLOCKS.png
STAS5_SCREENSHOT_INDEX_20260501_20260525.csv
STAS5_SCREENSHOT_INDEX_20260501_20260525.json
README_RU.md
```

Проверка показала `missing=[]`: найдены `14` train visual approval PNG для `01..14`, `11` исходных forward PNG для `15..25`, `11` V4 group-rank annotated PNG для `15..25`.

Важная граница: `01..14` сейчас найдены как train visual approval скрины, а не как V4 group-block ledger. V4 group-block слой зафиксирован для `15..25`. Обучение, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 Unified Forward Review 2026-05-15..2026-05-25

Статус: `STAS5_V4_FORWARD_REVIEW_20260515_20260525_DRAFT_NO_TRAINING`.

Исправлена календарная ошибка: `2026-05-15` не является отдельным карантинным или отдельным approved-днем. Правильная рамка:

```text
train_base_14 = 2026-05-01..2026-05-14
forward_review_11 = 2026-05-15..2026-05-25
```

Создан единый V4 group-rank ledger для forward-review `15..25`: `738` строк, `55` `BEST_GOOD`, `55` winners, `55` торгуемых групп, `19` no-trade групп. Все строки имеют `label_status=DRAFT`; это общий review-пакет, не train-approved база.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_REVIEW_20260515_20260525_FORWARD_REVIEW_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Старый главный ledger, который содержал только `2026-05-15`, сохранен как superseded-копия: `STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER_20260515_ONLY_SUPERSEDED_20260714T124741Z.csv`. Старый статус `20260515_APPROVED_V1` больше не должен использоваться как отдельная рабочая ветка; он стал историческим 15-only слоем внутри общего `forward_review_11`.

Граница: V4 training, group feature training dataset, threshold tuning, Optuna, API, TP/Stas3/exit не запускались. Следующий шаг - строить group features и визуальный group-check по этому unified ledger, затем делать отдельный guard перед обучением.

## Handoff 2026-07-14 STAS5 V4 2026-05-15 Quarantine Removed

Статус: `STAS5_V4_20260515_APPROVED_V1_NO_TRAINING`.

По решению пользователя день `2026-05-15` снят с карантина. Актуальный approved source - user-corrected V1: `41` строка, `BAD_IN_GROUP=26`, `NO_TRADE_GROUP=6`, `BEST_GOOD=5`, `GOOD_ALT=4`. Approved winners: `LA007`, `LA021`, `LA024`, `LA054`, `LA061`; good-alt: `LA004`, `LA005`, `LA053`, `LA060`.

Созданы approved-артефакты:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_APPROVED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_APPROVED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Календарь V4 обновлен: `base_25_days = 2026-05-01..2026-05-25`, `2026-05-15` больше не quarantine. Общий `STAS5_V4_GROUP_RANK_LEDGER.csv` сейчас содержит только approved-дни, то есть только `2026-05-15`; draft-дни `2026-05-16..2026-05-25` туда не добавлены автоматически.

Граница: снятие карантина не является запуском обучения. V4 training, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-25 Draft Group Review

Статус: `STAS5_V4_20260525_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-25` сделан V4-разбор по группам выбора. День разложен на `7` групп и `68` строк draft CSV: `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=19`, `BEST_GOOD=5`, `GOOD_ALT=4`. Winners: `LA014`, `LA020`, `LA038`, `LA059`, `LA066`; good-alt: `LA006`, `LA015`, `LA019`, `LA067`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_REVIEW_20260525_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_LEDGER_20260525_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_REVIEW_20260525_ANNOTATED_DRAFT.png
```

Суть разметки: `LA014` - финальный Asia basin/retest после раннего flush, `LA020` - pre-London pullback low, `LA038` - late-London support retest перед ростом, `LA059` - NY lower retest после fade, `LA066` - late weak-hours deep low. `LA012`, `LA030`, `LA053`, `LA057`, `LA068` оставлены как обучающие проигравшие рядом со своими группами.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-24 Draft Group Review

Статус: `STAS5_V4_20260524_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-24` сделан V4-разбор по группам выбора. День разложен на `6` групп и `70` строк draft CSV: `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=6`, `GOOD_ALT=5`, `BEST_GOOD=5`. Winners: `LA009`, `LA015`, `LA024`, `LA042`, `LA065`; good-alt: `LA005`, `LA008`, `LA014`, `LA023`, `LA067`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_REVIEW_20260524_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_LEDGER_20260524_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_REVIEW_20260524_ANNOTATED_DRAFT.png
```

Суть разметки: `LA009` и `LA015` - два нижних Asia/pre-London участка, `LA024` - лучший London support retest, `LA042` - главный overlap-crash deep low, `LA065` - поздний deep low/retest после NY selloff. `LA064` не назначен winner, хотя он чуть ниже по цене, потому что это falling knife/no reversal; `LA067` оставлен только `GOOD_ALT`.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-23 Draft Group Review

Статус: `STAS5_V4_20260523_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-23` сделан V4-разбор по группам выбора. День разложен на `6` групп и `63` строки draft CSV: `BAD_IN_GROUP=41`, `NO_TRADE_GROUP=12`, `GOOD_ALT=5`, `BEST_GOOD=5`. Winners: `LA007`, `LA022`, `LA033`, `LA036`, `LA051`; good-alt: `LA002`, `LA014`, `LA025`, `LA042`, `LA046`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_REVIEW_20260523_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_REVIEW_20260523_ANNOTATED_DRAFT.png
```

Суть разметки: `LA007` - лучший early Asia support retest, `LA022` - главный deep low после London flush, `LA033` - retest low после базы, `LA036` и `LA051` - pullback/retest lows на восстановлении. Поздняя зона `LA052..LA063` оформлена как `NO_TRADE_GROUP`: это уже post-spike/weak continuation, где входы слишком высоко или без нового нижнего преимущества.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-22 Draft Group Review

Статус: `STAS5_V4_20260522_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-22` сделан V4-разбор по группам выбора. День разложен на `6` групп и `75` строк draft CSV: `BAD_IN_GROUP=55`, `NO_TRADE_GROUP=11`, `BEST_GOOD=5`, `GOOD_ALT=4`. Winners: `LA007`, `LA022`, `LA036`, `LA047`, `LA061`; good-alt: `LA005`, `LA024`, `LA043`, `LA062`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_REVIEW_20260522_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_LEDGER_20260522_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_REVIEW_20260522_ANNOTATED_DRAFT.png
```

Суть разметки: `LA007` - early Asia basin low, `LA022` - pre-London support touch, `LA036` - midday pullback, `LA047` - overlap lower low, `LA061` - главный NY deep low после selloff. Поздний хвост `LA065..LA075` оформлен как `NO_TRADE_GROUP`, а `LA075` не назначен winner из-за weak-hours финального провала.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-21 Draft Group Review

Статус: `STAS5_V4_20260521_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому V3 forward-скриншоту `2026-05-21` сделан V4-разбор по группам выбора. День разложен на `6` групп и `81` строку draft CSV: `BAD_IN_GROUP=56`, `NO_TRADE_GROUP=15`, `GOOD_ALT=5`, `BEST_GOOD=5`. Winners: `LA006`, `LA019`, `LA045`, `LA059`, `LA066`; good-alt: `LA004`, `LA021`, `LA040`, `LA048`, `LA057`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_REVIEW_20260521_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_LEDGER_20260521_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_REVIEW_20260521_ANNOTATED_DRAFT.png
```

Суть разметки: `LA006` - лучший Asia basin low, `LA019` - pre-London deep low, `LA045` - главный overlap deep low после sell-wave, `LA059` - pre-breakout pullback, `LA066` - pullback после вертикального NY spike. Поздний участок `LA067..LA081` оформлен как `NO_TRADE_GROUP`.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-20 Draft Group Review

Статус: `STAS5_V4_20260520_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому скриншоту `2026-05-20` сделан V4-разбор по группам выбора. День разложен на `7` групп и `68` строк draft CSV: `NO_TRADE_GROUP=31`, `BAD_IN_GROUP=28`, `BEST_GOOD=5`, `GOOD_ALT=4`. Winners: `LA011`, `LA037`, `LA045`, `LA053`, `LA057`; good-alt: `LA002`, `LA035`, `LA040`, `LA052`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_REVIEW_20260520_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_LEDGER_20260520_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_REVIEW_20260520_ANNOTATED_DRAFT.png
```

Суть разметки: `LA011` - лучший ранний ретест базы, `LA037` - crash-zone lower retest, `LA045` - подтвержденный NY pullback, `LA053` - нижний ретест после NY-пика, `LA057` - поздний pullback перед хвостом. Группа `LA013..LA032` и поздний хвост `LA058..LA068` оформлены как no-trade-контекст.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-19 Draft Group Review

Статус: `STAS5_V4_20260519_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому скриншоту `2026-05-19` сделан V4-разбор по группам выбора с учетом красного нисходящего канала. День разложен на `7` групп и `65` строк draft CSV: `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=17`, `BEST_GOOD=5`, `GOOD_ALT=3`. Winners: `LA005`, `LA016`, `LA032`, `LA042`, `LA063`; good-alt: `LA046`, `LA061`, `LA062`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_REVIEW_20260519_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_LEDGER_20260519_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_REVIEW_20260519_ANNOTATED_DRAFT.png
```

Суть разметки: `LA005` и `LA016` - ранние lower-channel touches; `LA032` - mid-day lower-channel low; `LA042` - overlap deep low; `LA063` - поздний lower-channel low. Группы `LA017..LA024` и `LA048..LA056` оформлены no-trade как верх/середина канала.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-18 Draft Group Review

Статус: `SUPERSEDED_BY_20260518_USER_CORRECTED_V1_NO_TRAINING`.

Первый draft по `2026-05-18` разложил день на `6` групп и `73` строки: `BAD_IN_GROUP=51`, `NO_TRADE_GROUP=11`, `GOOD_ALT=6`, `BEST_GOOD=5`; winners были `LA006`, `LA019`, `LA034`, `LA049`, `LA061`. Этот draft superseded после пользовательских обводок: актуальная версия `USER_CORRECTED_V1` добавила winners `LA036` и `LA066`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_REVIEW_20260518_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_LEDGER_20260518_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_REVIEW_20260518_ANNOTATED_DRAFT.png
```

Суть разметки: ранний winner `LA006`; новая волна давления `LA019`; low перед импульсом вверх `LA034`; crash-zone winner `LA049` с alt `LA048/LA050`; NY deep low `LA061` с alt `LA059`. Поздний участок `LA063..LA073` после V-отскока оформлен как `NO_TRADE_GROUP`.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-17 Draft Group Review

Статус: `STAS5_V4_20260517_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому скриншоту `2026-05-17` сделан V4-разбор по группам выбора. День разложен на `8` групп и `63` строки draft CSV: `NO_TRADE_GROUP=30`, `BAD_IN_GROUP=25`, `BEST_GOOD=5`, `GOOD_ALT=3`. Winners: `LA004`, `LA006`, `LA036`, `LA046`, `LA063`; good-alt рядом с красными зонами: `LA003`, `LA005`, `LA044`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_REVIEW_20260517_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_LEDGER_20260517_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_REVIEW_20260517_ANNOTATED_DRAFT.png
```

Суть разметки: середина дня `LA009..LA030` и поздняя верхняя зона `LA048..LA055` оформлены как no-trade; локальные рабочие зоны - ранний low `LA004`, pullback `LA006`, дневной low `LA036`, ретест базы `LA046`, финальный knife low `LA063`. Важный bad-контраст: `LA056/LA062` до настоящего low `LA063`.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 Review Encoding Fix

Статус: `STAS5_V4_REVIEW_ENCODING_FIX_DONE`.

Пользователь указал на кракозябры в разборе. Проверены три V4 Markdown-разбора по `2026-05-15` и `2026-05-16`; они читаются как UTF-8, автоматический скан по длинным цепочкам вопросительных знаков, `U+FFFD` и CJK-мусору вернул `problems=0`. В `docs/codex/commands.md` один литеральный `U+FFFD` был частью старой команды поиска мусора, поэтому заменен на текстовый regex escape `\x{FFFD}`.

Важно: содержательная разметка V4 не менялась. Актуальные draft-ledger и annotated PNG остаются теми же; обучение и любые TP/Stas3/API/Optuna операции не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-16 Draft Group Review

Статус: `STAS5_V4_20260516_GROUP_REVIEW_DRAFT_NO_TRAINING`.

По пользовательскому скриншоту `2026-05-16` сделан такой же V4-разбор, как для `2026-05-15`: группы выбора, winner внутри группы и плохие соседние кандидаты с reason-code. Это переводит день из V3 row-label логики в V4 group-rank логику.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_REVIEW_20260516_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_LEDGER_20260516_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_REVIEW_20260516_ANNOTATED_DRAFT.png
```

Суть разметки: `9` групп, `71` строка, winners `LA016`, `LA027`, `LA038`, `LA041`, `LA049`. `LA016` и `LA027` - knife lows; `LA038` - lower missed-good после плохого высокого `LA034`; `LA041` и `LA049` - нижние ретесты/стабилизация после давления. Поздний участок после `16:30` оформлен как `NO_TRADE_GROUP`.

Граница: файл остается `DRAFT`, не approved train ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 2026-05-15 User-Corrected V1

Статус: `STAS5_V4_20260515_USER_CORRECTED_DRAFT_NO_TRAINING`.

Пользователь уточнил, что разбор `2026-05-15` нужно начинать именно с графика и красных подчеркиваний: красная линия = хороший вход, соседние LA вокруг нее = плохие обучающие примеры внутри той же группы. Я зафиксировал исправленную версию `USER_CORRECTED_V1`, которая supersede'ит первый `SCREENSHOT_DRAFT`.

Актуальные файлы:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_USER_CORRECTED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_ANNOTATED.png
```

Суть разметки: `6` групп выбора, `41` строка, winners `LA007`, `LA021`, `LA024`, `LA054`, `LA061`; `LA004` сохранен как `GOOD_ALT`, потому что в группе 1 winner должен быть один и более глубокий low - `LA007`. Группа 4 оформлена как `NO_TRADE_GROUP`, потому что там пила без выбранного хорошего входа. `LA017/LA018/LA020`, `LA048/LA050/LA051/LA052` и другие соседние кандидаты размечены как BAD с причиной, а не удалены. Это правильная V4-логика: учить модель выбирать лучший нижний вход внутри группы.

Граница: файл остается `DRAFT`, `2026-05-15` не включать в train до approved group ledger. V4 обучение, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

## Handoff 2026-07-14 STAS5 V4 Human-Style Group Ranker TZ

Статус: `STAS5_V4_20260515_SCREENSHOT_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Пользователь зафиксировал новый правильный план: V4 не должен выкидывать признаки и заранее резать входы. Признаки должны быть переставлены на правильное место - объяснять ранжирование внутри группы кандидатов.

Создано:

```text
STAS5_ML_CORE/07_STAS5_V4_HUMAN_STYLE_GROUP_RANKER_TZ_RU.md
STAS5_ML_CORE/v4/README_RU.md
STAS5_ML_CORE/schemas/STAS5_V4_GROUP_RANK_LEDGER.schema.json
```

Новый будущий ledger:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Главная логика: локальная зона/движение -> `group_id` -> candidates -> winner (`BEST_GOOD`) должен ранжироваться выше losers (`BAD_IN_GROUP`/`GOOD_ALT`) с обязательными reason-code. Старые session/fon/LONG/SHORT/WAVE/RSI/MACD/Stoch/ATR/volume/density/structure/pattern/knife/long-recovery/support-resistance признаки остаются как контекст. Старые `ML_KEEP_SCORE_V2/V3`, `ML_DECISION_V2/V3`, `yellow_x`, `postfact`, `hit_*`, `future`, `TP/Stas3/exit` запрещены как feature columns.

Календарь: `24` базовых дня = `2026-05-01..2026-05-14 + 2026-05-16..2026-05-25`; `2026-05-15` - карантин до approved group ledger. `2026-05-21..2026-05-25` нельзя использовать для V4 train без ручной групповой проверки.

Следующий шаг: оформить групповой ledger для `2026-05-15`, затем перевести `2026-05-16..2026-05-20` и `2026-05-21..2026-05-25` в `group_id + rank_label + reason_code + winner`. Обучение V4, threshold tuning, Optuna, API, TP/Stas3/exit не запускались.

После пользовательского скриншота `2026-05-15` с красными подчеркиваниями создан ручной draft-review:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_DRAFT_RU.md
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_SCREENSHOT_DRAFT.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_REVIEW_20260515_ANNOTATED_DRAFT.png
```

Смысл draft: `LA048/LA050/LA073` - примеры ложного старого `ENTER`; `LA021/LA054/LA061` - главный жесткий набор winners; `LA007` и `LA004` - ранние возможные winners/good-alt по красным подчеркиваниям. CSV частичный, `41` строка, `DRAFT`, не approved ledger. `2026-05-15` все еще карантинный и не train.

## Handoff 2026-07-14 STAS5 V3 Review Train Forward 21-25

Статус: `STAS5_V3_REVIEW_TRAIN_FORWARD_21_25_READY`.

Создан отдельный V3-контур для обучения на старых `2026-05-01..2026-05-14` плюс пользовательский review `2026-05-16..2026-05-20`. День `2026-05-15` исключен из обучения. Holdout `2026-05-21..2026-05-25` используется только как blind-forward.

Новые модули:

```text
src/mlbotnav/stas5_v3_user_review_ledger.py
src/mlbotnav/stas5_v3_training_dataset_builder.py
src/mlbotnav/stas5_v3_leakage_guard.py
src/mlbotnav/stas5_v3_entry_ranker_train.py
src/mlbotnav/stas5_v3_forward_entry_review.py
STAS5_ML_CORE/run_stas5_v3_review_train_forward_21_25.ps1
```

Результаты: V3 ledger `135` строк (`34 KEEP_APPROVED`, `100 CUT_APPROVED`, `1 NO_CANDIDATE_AUDIT_ONLY`), train dataset `1106` строк, `274` признака, guard `PASS`. Проверенный wrapper-run `stas5_v3_wrapper_smoke2_20260714` построил `5/5` forward PNG за `2026-05-21..2026-05-25`: total `ENTER=79`, `UNSURE=31`, `SKIP=247`.

Главный отчет:

```text
STAS5_ML_CORE/06_STAS5_V3_REVIEW_TRAIN_FORWARD_RESULT_RU.md
```

Команда:

```powershell
cd C:\Users\007\Desktop\MLbotNav
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\STAS5_ML_CORE\run_stas5_v3_review_train_forward_21_25.ps1
```

Граница: TP/Stas3/API/Optuna/threshold tuning не запускались. User-review/current-ML/postfact поля остаются metadata/audit, не feature columns.

## Handoff 2026-07-13 STAS5 V2 Full274 Run Check

Статус: `STAS5_V2_FULL274_RUN_CHECK_PASS_TECHNICAL_REVIEW_REQUIRED`.

Проверен последний прогон `stas5_v2_full274_20260713_203703`. Model latest pointer и forward latest pointer указывают на один run. Модель реально обучена на `full_v2_all_274`, `feature_count=274`; guard `PASS`; pre-ML audit `READY_FOR_V2_ABLATION_BASELINE`.

Forward `2026-05-15..2026-05-20`: `435` строк, `ENTER=77`, `UNSURE=24`, `SKIP=334`. Все 6 PNG созданы, непустые, `4640x3987`; row parity между manifest, общим CSV и дневными CSV проходит.

Артефакты проверки:

```text
STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_FULL274_RUN_CHECK_20260713_203703_RU.md
STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_full274_run_check_20260713_203703_v0.json
```

Важный вывод: технически прогон валиден, но full274 по train-ablation слабее baseline `v1_plus_risk_gate` (`AUC 0.649292` против `0.684988`). Нужен визуальный review PNG перед заменой baseline.

## Handoff 2026-07-13 STAS5 V2 Full 274 Wrapper Ready

Статус: `STAS5_V2_FULL_274_WRAPPER_READY`.

По просьбе пользователя подготовлен один командный запуск для полного переобучения STAS5 V2 на всех `274` признаках и forward-графиков `2026-05-15..2026-05-20`.

Новый wrapper:

```text
STAS5_ML_CORE/run_stas5_v2_full_274_train_forward.ps1
```

Команда:

```powershell
cd C:\Users\007\Desktop\MLbotNav
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\STAS5_ML_CORE\run_stas5_v2_full_274_train_forward.ps1
```

Wrapper пересобирает V2 train/forward признаки, запускает guard/audit, обучает `full_v2_all_274`, рендерит blind-forward и проверяет, что manifest реально содержит `model_feature_set=full_v2_all_274`, `feature_count=274`.

Проверено: PowerShell syntax PASS; `py_compile` нужных V2 модулей PASS. Сам тяжелый full-прогон не запускался.

## Handoff 2026-07-13 STAS5 V2 Graph To Feature Audit

Статус: `STAS5_V2_GRAPH_TO_FEATURE_AUDIT_READY`.

Пользователь попросил жестко проверить контрольный train-день `2026-05-04`: все ли, что видно на большом approval-графике, реально попадает в цифры для ML. Подключен read-only агент; локальная проверка выполнена по PNG/manifest, full snapshot manifest и latest model manifest.

Главный вывод: `GRAPH_TO_FULL_SNAPSHOT=PASS`, но `FULL_SNAPSHOT_TO_LATEST_MODEL=PARTIAL`. В full snapshot есть `274` feature columns и `74/74` строки дня совпадают с графиком (`9 KEEP`, `65 CUT`, `22 yellow X`, `4 conflict`). Но последняя модель `stas5_v2_run_20260713_191122` была обучена на `v1_plus_risk_gate`, то есть `126` признаков, и не использовала combo/density/structure/STAS4 blocks/pattern/short-wave/divergence.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_GRAPH_TO_FEATURE_AUDIT_20260504_RU.md
STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_graph_to_feature_audit_20260504_v0.json
```

Граница: обучение, threshold tuning, TP/Stas3, API/мост и Optuna не запускались. Следующий рабочий выбор - делать отдельный model-set `graph_context_v2`/`full_v2_all_274` как сравнение с текущим baseline, а не говорить, что текущая модель уже съела весь график.

## Handoff 2026-07-13 STAS5 V2 Train Visual Batch Ready

Статус: `STAS5_V2_TRAIN_VISUAL_BATCH_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Пользователь справедливо указал нечеткость: ML train table покрывает `2026-05-01..2026-05-14`, но train-график был создан только за `2026-05-04`. Это не ломало обучение, но ломало визуальную проверку покрытия.

Что сделано: создан `src/mlbotnav/stas5_v2_train_visual_batch.py`, который рендерит все train-дни из `stas5_v2_feature_snapshot_20260501_20260514_v0.csv`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2/visual_approval/runs/stas5_v2_train_visual_20260713_14d/
STAS5_ML_CORE/artifacts/v2/visual_approval/runs/stas5_v2_train_visual_20260713_14d/STAS5_V2_TRAIN_VISUAL_BATCH_MANIFEST.json
STAS5_ML_CORE/artifacts/v2/visual_approval/STAS5_V2_LATEST_TRAIN_VISUAL_RUN.json
```

Проверено: `14/14` PNG, `972` rows, `115 KEEP`, `857 CUT`; PNG `4960x4557`; full STAS5 tests `34 passed`.

Следующий шаг: пользователь может смотреть train-графики `01..14` и сравнивать с ручными входами.

## Handoff 2026-07-13 STAS5 V2 Run Isolation Ready

Статус: `STAS5_V2_RUN_ISOLATION_READY`.

Пользователь заметил, что повторный forward перезаписывает старые папки `20260515..20260520`, из-за чего трудно отличать прогоны. Исправлено: CLI `stas5_v2_entry_ranker_train` и `stas5_v2_forward_entry_review` теперь поддерживают общий `--run-id` и по умолчанию пишут в отдельные run-папки.

Новый путь:

```text
STAS5_ML_CORE/artifacts/v2/model/runs/<run_id>/
STAS5_ML_CORE/artifacts/v2/forward/runs/<run_id>/
```

Проверочный run: `stas5_v2_run_20260713_190743`. В нем созданы model artifacts и forward PNG за `20260515..20260520`.

Проверки: новые tests `4 passed`, полный STAS5 pack `34 passed`.

Следующая команда для пользователя должна использовать один `$runId` для обучения и forward.

## Handoff 2026-07-13 STAS5 V2 Controlled Forward Ready

Статус: `STAS5_V2_CONTROLLED_FORWARD_READY_NO_TP_NO_API_NO_STAS3`.

Пользователь подтвердил: идти после numeric coverage до конца - ablation, controlled train, blind-forward и графики. Подключены два read-only агента. Их выводы учтены: V1 модель не трогать; V2 training/forward делать отдельными модулями; старый V1 forward scorer нельзя использовать для V2, потому что он не join-ит V2 combo features.

Что создано:

1. `src/mlbotnav/stas5_v2_entry_ranker_train.py`;
2. `src/mlbotnav/stas5_v2_forward_entry_review.py`;
3. `tests/test_stas5_v2_entry_ranker_train.py`;
4. `tests/test_stas5_v2_forward_entry_review.py`.

Ablation: лучший train LOO набор `v1_plus_risk_gate`: `126` features, AUC `0.684988`. Полный `full_v2_all_274` слабее: AUC `0.649292`, поэтому controlled model выбрана не full, а по ablation.

Forward `2026-05-15..2026-05-20`: `106 ENTER`, `45 UNSURE`, `284 SKIP`. PNG по всем 6 дням готовы в `STAS5_ML_CORE/artifacts/v2/forward/`.

Главный отчет:

```text
STAS5_ML_CORE/artifacts/v2/model/STAS5_V2_CONTROLLED_MODEL_AND_FORWARD_REPORT_RU.md
```

Проверки: V2 leakage guard `PASS`; STAS5 tests `34 passed`; PNG check `6/6`, размер `4640x3987`.

Следующий шаг: пользователь смотрит forward PNG и отмечает реальные/шумные входы. Не запускать TP/Stas3/API/Optuna/threshold tuning без отдельного решения.

## Handoff 2026-07-13 STAS5 V2 Numeric Coverage Ready

Статус: `STAS5_V2_NUMERIC_COVERAGE_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

По просьбе пользователя проверено, все ли важные элементы approval-графика реально попадают в ML как числовые признаки. Подключены два read-only агента. Оба подтвердили главный gap: четыре STAS4 strategy-блока были видны на графике, но не имели полноценного числового слоя в feature matrix. Также pattern слой и SHORT/WAVE контекст были неполными.

Что изменено:

1. `src/mlbotnav/stas5_v2_combo_feature_exporter.py` теперь экспортирует `stas4_v2_block_*`, `stas4_v2_pattern_*`, `stas5_v2_short_wave_*`;
2. `src/mlbotnav/stas5_common.py` усилил forbidden feature patterns для старых/новых strategy vote/hard filter полей;
3. `src/mlbotnav/stas5_v2_pre_ml_audit.py` знает новые группы;
4. создан `src/mlbotnav/stas5_v2_numeric_coverage_audit.py`.

Результат: V2 combo features `103 -> 163`, полный train snapshot `214 -> 274` feature columns. Train `972` rows, forward `435` rows, `KEEP_DRAFT + yellow_x = 30` сохранены, leakage guard `PASS`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_NUMERIC_COVERAGE_AUDIT_20260504_RU.md
STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_numeric_coverage_audit_20260504_v0.json
STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.csv
```

Проверки: `py_compile` PASS; targeted V2 tests PASS `23 passed`; full STAS5 tests PASS `30 passed`.

Следующий шаг: пользователь смотрит numeric coverage audit. После подтверждения можно идти к V2 ablation baseline. Не запускать training/threshold/Optuna/API/Stas3/TP без отдельного решения.

## Handoff 2026-07-13 STAS5 V2 Strategy Audit Strip Ready

Статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_WITH_STRATEGY_AUDIT_READY_WAIT_USER_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

По просьбе пользователя последний визуальный пункт перед ablation расширен: в `src/mlbotnav/stas5_v2_feature_visual_approval.py` добавлена полоса `STAS4 Audit` с четырьмя выбранными стратегическими блоками. Полоса рисуется на train-дне `2026-05-04` между `WAVE` и density/structure и является строго audit-only.

Стратегические counts на `2026-05-04`:

1. `density_profile+structure_ta`: `X=22`, `UP=2`;
2. `pattern+structure_ta`: `X=38`, `UP=1`;
3. `structure_ta+volume_flow`: `X=52`, `UP=1`;
4. `structure_ta+trend_momentum`: `X=59`, `UP=4`.

Оптимизация: базовые STAS4 family считаются один раз и переиспользуются для combo-пересечений, иначе прямой пересчет четырех combo занимал несколько минут из-за тяжелого `structure_ta`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.manifest.json
```

Проверки: `py_compile` PASS; `tests/test_stas5_v2_feature_visual_approval.py` PASS `5 passed`; render command PASS за ~75 секунд. Хвостовые python-процессы от таймаутного пробного рендера остановлены.

Следующий шаг: пользователь смотрит PNG и дает `норм / править`. Не запускать ablation/training/threshold/Optuna/API/Stas3/TP до визуального подтверждения.

## Handoff 2026-07-13 STAS5 V2 Feature Visual Approval Ready

Статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_READY_WAIT_USER_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Пользователь попросил перед пунктом 8 не начинать ablation/training, а сначала показать один train-день со всеми признаками на графике. Выбран день `2026-05-04`, потому что он соответствует старому STAS4 reference overlay.

Что сделано:

1. создан `src/mlbotnav/stas5_v2_feature_visual_approval.py`;
2. переиспользованы старые renderer-блоки для свечей, сессий, полос `FON/LONG/SHORT/WAVE` и `COMBO SPECTRUM`;
3. на график добавлены все `74` LA-кандидата дня, human `KEEP/CUT`, yellow X и `KEEP + yellow_x` conflict;
4. добавлены панели density/structure, risk/gate, V2 combo snapshot и старый-style combo spectrum;
5. добавлены тесты `tests/test_stas5_v2_feature_visual_approval.py`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.manifest.json
```

Результат: `74` rows, `KEEP_DRAFT=9`, `CUT_DRAFT=65`. Visual markers: `human_keep_green_markers=9`, `keep_yellow_conflict_cyan_overlay_markers=4`, `yellow_x_cut_overlay_markers=18`. Approval buckets for audit table: `KEEP=5`, `CONFLICT=4`, `YELLOW_X=18`, `CUT=47`. Risk buckets `HIGH_RISK=38`, `CAUTION=21`, `LOW_RISK=13`, `BLOCKED=2`. KEEP ids: `LA002`, `LA004`, `LA020`, `LA032`, `LA038`, `LA042`, `LA045`, `LA049`, `LA065`. PNG `4960x4262`, pixel-check не пустой.

Проверки: `py_compile` PASS; `tests/test_stas5_v2_feature_visual_approval.py` PASS `3 passed`; render command PASS.

Следующий шаг: пользователь визуально смотрит PNG. Не запускать ablation baseline, V2 training, threshold tuning, Optuna/scorer/target-lock/API или Stas3/TP до подтверждения графика.

## Handoff 2026-07-13 STAS5 V2 Pre-ML Audit Ready

Статус: `STAS5_V2_PRE_ML_AUDIT_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Работа продолжена строго по `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`, раздел 14, пункт 7. Закрыт пункт 7: создан `src/mlbotnav/stas5_v2_pre_ml_audit.py`.

Что сделано:

1. audit сравнивает train `KEEP/CUT` по `214` признакам V2 feature snapshot;
2. считает coverage, numeric KEEP/CUT differences и group summary;
3. добавляет categorical KEEP/CUT по session/setup/combo/gate/risk полям;
4. агрегирует forward error classes из `stas5_forward_error_ledger_20260515_20260520_v0.csv`;
5. добавлены тесты `tests/test_stas5_v2_pre_ml_audit.py`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_PRE_ML_AUDIT_20260501_20260520_RU.md
STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_pre_ml_audit_20260501_20260520_v0.json
```

Результат: `READY_FOR_V2_ABLATION_BASELINE`, train rows `972`, `KEEP_DRAFT=115`, `CUT_DRAFT=857`, `KEEP_DRAFT + yellow_x=30`, feature count `214`, guard `PASS`, forward error ledger `PASS`, forbidden feature columns `{}`. Forward audit: bad green `55`, good green `48`, missed good SKIP `65`.

Проверки: `py_compile` PASS; pre-ML audit tests `3 passed`; явный STAS5 pack `24 passed`.

Следующий пункт по ТЗ: раздел 14, пункт 8 - ablation baseline. Не переходить к production trading permission, threshold tuning по forward `15+`, Optuna/scorer/target-lock/API или Stas3/TP.

## Handoff 2026-07-13 STAS5 V2 Forward Error Ledger Ready

Статус: `STAS5_V2_FORWARD_ERROR_LEDGER_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Работа продолжена строго по `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`, раздел 14, пункт 6. Закрыт пункт 6: создан `src/mlbotnav/stas5_v2_forward_error_ledger.py`.

Что сделано:

1. ledger соединяет V1 forward `ML_DECISION/ML_KEEP_SCORE/postfact` с V2 combo/risk/gate features;
2. optional user-review labels читаются из `STAS5_ML_CORE/artifacts/v2/user_review`, но остаются audit-only;
3. добавлены классы `GREEN_GOOD`, `GREEN_BAD_FALLING_KNIFE`, `GREEN_BAD_TOO_HIGH`, `GREEN_BAD_NO_REVERSAL`, `YELLOW_GOOD`, `YELLOW_BAD`, `SKIP_MISSED_GOOD`, `SKIP_CORRECT`;
4. добавлен `v2_expected_decision` как audit-подсказка, не trading permission;
5. добавлены тесты `tests/test_stas5_v2_forward_error_ledger.py`.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.csv
STAS5_ML_CORE/artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.manifest.json
```

Результат: `PASS`, `435` rows, source V1 rows `435`, source V2 rows `435`, missing V2 rows `0`, duplicate keys `0`. V1 decisions: `ENTER=103`, `UNSURE=55`, `SKIP=277`. Error classes: `GREEN_BAD_FALLING_KNIFE=46`, `GREEN_BAD_NO_REVERSAL=9`, `GREEN_GOOD=48`, `YELLOW_BAD=34`, `YELLOW_GOOD=21`, `SKIP_CORRECT=212`, `SKIP_MISSED_GOOD=65`.

Проверки: `py_compile` PASS; forward error ledger tests `3 passed`; явный STAS5 pack `21 passed`.

Следующий пункт по ТЗ: раздел 14, пункт 7 - V2 pre-ML audit. Не переходить к V2 training, threshold tuning, V2 PNG, Optuna/scorer/target-lock/API или Stas3/TP до pre-ML audit.

## Handoff 2026-07-13 STAS5 V2 Leakage Guard Ready

Статус: `STAS5_V2_LEAKAGE_GUARD_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

После подтверждения пользователя "поехали" работа продолжена строго по `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`, раздел 14, пункт 5. Закрыт пункт 5: создан `src/mlbotnav/stas5_v2_leakage_guard.py`.

Что сделано:

1. guard сканирует `feature_columns` из V2 snapshot manifest, а не все metadata-поля CSV;
2. проверяет запрет `future/postfact/outcome/Stas3/TP/exit/yellow/strategy` в feature matrix;
3. проверяет `v2_combo_feature_time_utc < entry_time_utc`;
4. проверяет отсутствие forward-дней `2026-05-15+` в train snapshot;
5. проверяет row parity, duplicate keys, label counts и сохранение `KEEP_DRAFT + yellow_x = 30`;
6. добавлены тесты `tests/test_stas5_v2_leakage_guard.py`.

Артефакт:

```text
STAS5_ML_CORE/artifacts/v2/guard/stas5_v2_leakage_guard_20260501_20260514_v0.json
```

Результат: `PASS`, `972` rows, `214` feature columns, forbidden feature columns `{}`, label/metadata columns in features `[]`, missing required metadata `[]`, duplicate keys `0`, feature time not before entry `0`, forward days present `0`, `KEEP_DRAFT=115`, `CUT_DRAFT=857`, `KEEP_DRAFT + yellow_x = 30`.

Проверки: `py_compile` PASS; V2 leakage guard tests `4 passed`; явный STAS5 pack `18 passed`.

Следующий пункт по ТЗ: раздел 14, пункт 6 - `stas5_v2_forward_error_ledger.py`. Не переходить к V2 training, threshold tuning, V2 PNG, Optuna/scorer/target-lock/API или Stas3/TP до forward error ledger и pre-ML audit.

## Handoff 2026-07-13 STAS5 V2 Feature Snapshot Ready

Статус: `STAS5_V2_FEATURE_SNAPSHOT_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

После замечания пользователя о перескоках работа возвращена строго к `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`, раздел 14. Закрыт пункт 4: создан `src/mlbotnav/stas5_v2_feature_snapshot_builder.py`.

Что сделано:

1. объединен v1 snapshot `111` Stas2/v1 features с V2 combo layer `103` features;
2. join строго по `day,candidate_id,record_id`;
3. `human_label`, `yellow_x`, `yellow_x_role`, `yellow_x_conflict` сохранены как metadata/labels, не feature columns;
4. добавлены invariant-checks по `entry_time_utc`, `anchor_time_utc`, `v2_combo_feature_available_before_entry`;
5. добавлены тесты `tests/test_stas5_v2_feature_snapshot_builder.py`.

Артефакты:

1. `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.csv`;
2. `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.manifest.json`.

Результат: `PASS`, `972` rows, `214` feature columns, `lost_after_combo_join=0`, `lost_after_ledger_check=0`, `entry_time_mismatch=0`, `anchor_time_mismatch=0`, forbidden columns `{}`, `KEEP_DRAFT + yellow_x = 30`.

Проверки: `py_compile` PASS; V2 snapshot tests `3 passed`; явный STAS5 pack `14 passed`.

Следующий пункт по ТЗ: раздел 14, пункт 5 - `stas5_v2_leakage_guard.py`. Не переходить к forward user review, обучению, threshold или Stas3/TP до guard и pre-ML audit.

## Handoff 2026-07-13 STAS5 V2 Forward User Review Pages Ready

Статус: `STAS5_V2_FORWARD_USER_REVIEW_READY_WAIT_USER_SELECTION_NO_TRAINING_NO_TP_NO_API`.

Пользователь посмотрел quicklook `2026-05-15` и сказал, что видит примерно 3 нужных входа, остальное шум. Следующий шаг выполнен: создан крупный renderer `src/mlbotnav/stas5_v2_forward_user_review.py`, который разбивает forward-день на страницы по 3 часа и показывает крупные свечи, `LAxxx`, `knife_risk`, `short_pressure`, `long_recovery` и combo-панель.

Артефакты:

1. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_FULL.png`;
2. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_PAGE_01_0000_0300.png` ... `PAGE_08_2100_0000.png`;
3. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_TEMPLATE_20260515.csv`;
4. `STAS5_ML_CORE/artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515.manifest.json`.

Результат: command `PASS 90`; buckets: `54 HIGH_RISK`, `30 CAUTION`, `5 LOW_RISK`, `1 BLOCKED`. Первая, вторая и пятая страницы визуально проверены и читаемы.

Следующий шаг: пользователь должен назвать точные `LAxxx` для 3 реальных входов. После этого заполнить шаблон: выбранные `USER_KEEP_FORWARD_AUDIT`, остальные `NOISE_FORWARD_AUDIT`, затем провести comparison audit `3 vs 87`.

Граница: это forward audit-only. Не обучать модель по `2026-05-15`, не подбирать threshold, не запускать Optuna/scorer/target-lock/API/Stas3/TP.

## Handoff 2026-07-13 STAS5 V2 Combo Feature Exporter Ready

Статус: `STAS5_V2_COMBO_FEATURE_EXPORT_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

По запросу пользователя начат V2 / контур 2 и реализован первый практический слой: `src/mlbotnav/stas5_v2_combo_feature_exporter.py`. Подключались два read-only агента: первый проверил, какие STAS4 combo/density/structure/divergence функции можно переиспользовать causal-образом; второй проверил STAS5 row universe, join keys, forward source и guardrails.

Что сделано:

1. exporter пересчитывает нижний combo-индикатор/STAS4 слой из OHLCV, а не читает PNG;
2. snapshot делается по `anchor_time_utc`, не по entry-свече;
3. экспортируются RSI/MACD/Stoch/ATR, confirmed divergence, density profile, structure votes, volume flow, первые risk/gate признаки;
4. forbidden поля `yellow`, `strategy_vote`, `postfact`, `future`, `target`, `mfe/mae`, `tp/stas3/exit` не входят в feature columns;
5. добавлены тесты `tests/test_stas5_v2_combo_feature_exporter.py`.

Артефакты:

1. `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.csv`;
2. `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.manifest.json`;
3. `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.csv`;
4. `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.manifest.json`.

Проверки: train `PASS 972 103`, forward `PASS 435 103`; manifest: row parity true, missing OHLCV none, `feature_available_before_entry_false=0`, forbidden columns `{}`. `py_compile` PASS; targeted V2 tests `4 passed`; весь STAS5 test pack `11 passed`.

Граница: это готовый feature-layer, но еще не финальная V2-модель и не trading permission. Следующий шаг: `stas5_v2_feature_snapshot_builder.py`, затем V2 leakage guard, pre-ML audit, forward error ledger. Forward `2026-05-15+` остается blind audit, не threshold tuning.

## Handoff 2026-07-13 STAS5 V1 Hard Audit And V2 Contour 2 TZ

Статус: `STAS5_V1_AUDITED_V2_CONTOUR2_TZ_READY_NO_OPTUNA_NO_API_NO_STAS3`.

Сделан жесткий аудит STAS5 v1. Три read-only агента проверили pipeline, combo-spectrum/STAS4 слой и forward-ошибки. Код ML не менялся, новое обучение не запускалось.

Главное решение: STAS5 v1 оставить как `CONTROLLED_BASELINE / AUDIT_REFERENCE`, но не использовать как финальный trading permission. Pipeline v1 корректен, но задача обучения неполная: combo-spectrum/STAS4 indicator block не был подключен к feature matrix, а отдельного `LONG_ALLOWED / NO_TRADE` gate не было.

Новые документы:

1. `STAS5_ML_CORE/04_STAS5_V1_HARD_AUDIT_RU.md`;
2. `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`.

Ключевые цифры: v1 train ledger `972`, `115 KEEP_DRAFT`, `857 CUT_DRAFT`, `30 KEEP_DRAFT + yellow_x`; feature count `111`; combo/STAS4 feature count in model `0`; forward `ENTER` `103`, `hit0.5=74.8%`, `hit1.0=46.6%`, median drawdown `-1.453%`. `2026-05-15` подтвердил проблему пользователя: `14 ENTER`, `hit1.0=14.3%`, median drawdown `-2.834%`.

STAS5 V2 должен включать:

1. `stas5_v2_combo_feature_exporter.py`;
2. STAS4 RSI/MACD/STOCH/ATR/divergence features;
3. density/structure features;
4. phase strength gate;
5. long permission gate;
6. falling knife / weak bounce / too high risk features;
7. forward error ledger;
8. ablation, calibration, permutation importance.

Граница: forward `2026-05-15+` остается blind audit и error ledger, не threshold tuning. Yellow X остается `AUDIT_ONLY`. Stas3/TP/exit, Optuna, scorer, target-lock, API/мост Bybit не запускать в STAS5 V2 research без отдельного решения.

## Handoff 2026-07-10 STAS5 Entry ML Pipeline Ready

Статус: `STAS5_ENTRY_ML_PIPELINE_READY_TRAIN_1_14_FORWARD_15_20_NO_OPTUNA_NO_API_NO_STAS3`.

STAS-5 entry ML создан end-to-end внутри текущего проекта. Старый ML-контур не переподключался как target; Stas1/Stas2/Stas4 логика не менялась; Stas3/TP/exit не использовались.

Главные файлы кода:

1. `src/mlbotnav/stas5_common.py`;
2. `src/mlbotnav/stas5_ml_ledger_builder.py`;
3. `src/mlbotnav/stas5_feature_snapshot_builder.py`;
4. `src/mlbotnav/stas5_leakage_guard.py`;
5. `src/mlbotnav/stas5_pre_ml_audit.py`;
6. `src/mlbotnav/stas5_entry_ranker_train.py`;
7. `src/mlbotnav/stas5_forward_entry_review.py`.

Главные артефакты:

1. `STAS5_ML_CORE/artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.csv`;
2. `STAS5_ML_CORE/artifacts/features/stas5_feature_snapshot_20260501_20260514_v0.csv`;
3. `STAS5_ML_CORE/artifacts/audit/STAS5_PRE_ML_AUDIT_20260501_20260514_RU.md`;
4. `STAS5_ML_CORE/artifacts/model/stas5_entry_ranker_20260501_20260514_v0.joblib`;
5. `STAS5_ML_CORE/artifacts/forward/STAS5_FORWARD_ENTRY_REVIEW_MANIFEST.json`;
6. `STAS5_ML_CORE/artifacts/forward/20260515..20260520/STAS5_FORWARD_ENTRY_REVIEW_YYYYMMDD.png`.

Проверки: `ledger=972`, `KEEP_DRAFT=115`, `CUT_DRAFT=857`, `KEEP_DRAFT+yellow_x=30`, `feature_count=111`, leakage guard `PASS`, pre-ML audit `READY_FOR_CONTROLLED_BASELINE`, controlled baseline `CONTROLLED_BASELINE_READY`, forward PNG/CSV на `2026-05-15..2026-05-20` созданы и не пустые.

Forward counts: `2026-05-15` `90` rows (`14 ENTER`, `12 UNSURE`, `64 SKIP`); `2026-05-16` `76` (`12/6/58`); `2026-05-17` `63` (`18/8/37`); `2026-05-18` `73` (`21/8/44`); `2026-05-19` `65` (`20/12/33`); `2026-05-20` `68` (`18/9/41`).

Граница для продолжения: forward `15+` не использовать для подбора threshold. Следующий разумный шаг - визуально открыть PNG 15-20 мая и руками оценить, где ML попадает/шумит; затем отдельным решением делать ablation/улучшение признаков. Optuna/API/Stas3/TP остаются вне текущего контура.

## Handoff 2026-07-10 STAS5 Memory Refresh

Статус: `STAS5_TZ_TRAIN_1_14_FORWARD_15_PLUS_NO_TP_NO_API`.

Текущий рабочий фокус зафиксирован в видимой корневой папке `STAS5_ML_CORE/`. STAS-5 строится как ML по входам: train/manual label window `2026-05-01..2026-05-14`, forward/blind check window `2026-05-15+`, output CSV/PNG с ML-точками входа `ENTER/UNSURE/SKIP`.

Текущая инструкция для продолжения: `STAS5_ML_CORE/03_STAS5_CURRENT_EXECUTION_INSTRUCTION_RU.md`. В ней закреплено: старый `MLbotNav` остается `LAB/ARCHIVE`, перенос в новый `MLbotNav_CORE` пока не делаем, сначала строим STAS5 adapter/datamart внутри текущего проекта.

Текущая база: `972` входа, `115` `KEEP_DRAFT`, `857` `CUT_DRAFT`, `30` `KEEP_DRAFT` с yellow X. Yellow X остается только `AUDIT_ONLY`; правило `human KEEP > strategy vote` обязательно.

Guardrails: не удалять `KEEP + yellow_x = 1`, не смешивать `human_label` и `strategy_vote`, не брать future/hindsight поля в признаки. Stas3/TP/exit не входят в STAS-5 по входам. Forward `2026-05-15+` не использовать для обучения, threshold tuning или ручной доводки. Future outcome можно считать только после факта для audit/backtest, не как feature/target/filter/threshold input.

Граница: ML/export/training, Optuna, scorer, target-lock, API и мост Bybit не запускать без отдельного прямого решения.

## Handoff 2026-07-10 STAS4 Root Home Ready

Статус: `STAS4_ROOT_HOME_READY_NO_ML_NO_OPTUNA`.

STAS4 вынесен в корень проекта:

```text
STAS4_FEATURE_HYPOTHESIS_REVIEW
```

Старый путь `reports/final_review/stas4_feature_hypothesis_screen_v0` больше не является рабочим источником. Все текстовые ссылки в `docs`, `src`, `scripts`, `STAS4_FEATURE_HYPOTHESIS_REVIEW`, `STAS5_ML_CORE` механически обновлены на новый корневой путь.

Ключевые файлы:
- `STAS4_FEATURE_HYPOTHESIS_REVIEW/README_RU.md`;
- `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels/README_RU.md`;
- `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels/YELLOW_X_AUDIT_ONLY_RULE_RU.md`;
- `reports/final_review/STAS4_MOVED_TO_ROOT_RU.md`.

Примечание: при переносе Windows не дал удалить часть старых пустых дневных директорий `20260504..20260514`, потому что они были заняты другим процессом. Это остаточный хвост, не источник правды. Не останавливать чужие процессы ради удаления.

Граница: перенос артефактов/путей. Stas1/Stas2/Stas4 логика, ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Handoff 2026-07-10 STAS5 ML Entry Architecture Draft

Статус: `STAS5_ML_ENTRY_ARCHITECTURE_DRAFT_NO_ML_NO_OPTUNA`.

Создан новый видимый source-of-truth для STAS-5 в корне проекта: `STAS5_ML_CORE/`.

Ключевое решение: STAS-5 строит не жесткий фильтр входов, а ML-ранжировщик входов Stas1/Stas2:

`candidate entry + pre-entry features -> human KEEP / CUT -> ML_KEEP_SCORE`.

Главный приоритет: `human KEEP > strategy vote`. Желтый `X` стратегии хранится только как `AUDIT_ONLY`; первая baseline-модель должна обучаться без yellow-полей, `would_cut`, `strategy_cut`, `strategy_vote`.

Зафиксированы документы:

1. `STAS5_ML_CORE/README_RU.md`;
2. `STAS5_ML_CORE/01_STAS5_ML_ENTRY_ARCHITECTURE_RU.md`;
3. `STAS5_ML_CORE/02_ML_LEDGER_AND_FEATURE_CONTRACT_RU.md`;
4. `STAS5_ML_CORE/schemas/stas5_ml_ledger_v0.yaml`;
5. `STAS5_ML_CORE/schemas/stas5_feature_snapshot_v0.yaml`.

Следующий шаг: собрать ML-ledger по `972` входам `2026-05-01..2026-05-14`, затем feature snapshot только до входа и audit признаков `KEEP_DRAFT` против `CUT_DRAFT`. Финальный ML пока не запускать.

Граница: Stas1/Stas2/Stas4 логика не менялась. Stas3 не входит в STAS-5 по входам. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Handoff 2026-07-10 Yellow X Audit Only Rule Fixed

Статус: `YELLOW_X_AUDIT_ONLY_FIXED_RULE_NO_ML_NO_OPTUNA`.

Принято и зафиксировано архитектурное правило: желтый `X` стратегии `density_profile+structure_ta` не имеет права резать пользовательские хорошие входы. Он хранится только как audit/vote-флаг `yellow_x_role = AUDIT_ONLY`.

Главный приоритет: `human KEEP_APPROVED > strategy yellow X`. Строки `KEEP + yellow_x = 1` должны оставаться положительными примерами и попадать в train window после отдельного утверждения ML-разметки; forward `2026-05-15+` не использовать для подбора threshold.

Факт по пачке `2026-05-01..2026-05-14`: `30` из `115` KEEP_DRAFT имеют yellow X. Поэтому hard-cut по yellow X запрещен и должен быть покрыт guardrails при будущем export/training.

Формальное правило: `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels/YELLOW_X_AUDIT_ONLY_RULE_RU.md`.

Граница: это решение по архитектуре dataset/ML-guardrails. Код стратегии, Stas1/Stas2/Stas4 логика, ML/export/training, Optuna, scorer, target-lock и API не запускались и не менялись.

## Handoff 2026-07-10 STAS4 Manual Labels 20260501-20260514 Draft Complete

Статус: `STAS4_MANUAL_LABELS_20260501_20260514_DRAFT_COMPLETE_NO_ML_NO_OPTUNA`.

Завершена ручная черновая разметка Stas4 review поверх стратегии `density_profile+structure_ta` и Stas2 run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260501_20260514_from_stas1_carry48_full_v1_20260709_142757`.

Источник PNG: `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum`.

Разметка хранится в `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels`.

Готовые дни:
- `2026-05-01`: `10` KEEP / `58` CUT;
- `2026-05-02`: `8` KEEP / `44` CUT;
- `2026-05-03`: `6` KEEP / `52` CUT;
- `2026-05-04`: `9` KEEP / `65` CUT;
- `2026-05-05`: `8` KEEP / `51` CUT;
- `2026-05-06`: `7` KEEP / `62` CUT;
- `2026-05-07`: `11` KEEP / `68` CUT;
- `2026-05-08`: `8` KEEP / `61` CUT;
- `2026-05-09`: `7` KEEP / `60` CUT;
- `2026-05-10`: `10` KEEP / `52` CUT;
- `2026-05-11`: `10` KEEP / `66` CUT;
- `2026-05-12`: `6` KEEP / `70` CUT;
- `2026-05-13`: `4` KEEP / `82` CUT;
- `2026-05-14`: `11` KEEP / `66` CUT.

Итог пачки `2026-05-01..2026-05-14`: всего `972` входа, `115` KEEP_DRAFT, `857` CUT_DRAFT.

Для `2026-05-14` зафиксированы KEEP: `LA014`, `LA015`, `LA032`, `LA039`, `LA046`, `LA047`, `LA048`, `LA049`, `LA053`, `LA055`, `LA056`. Желтый `X` среди выбранных: `LA047`, `LA053`. `LA014` и `LA015` трактуются как две отдельные ранние отметки в double-bottom кластере, а не как один разрезанный курсором вход.

Проверочный PNG: `ANNOTATED_20260514_KEEP_DRAFT.png`.

Граница: это `DRAFT` ручного ledger для обсуждения будущей ML-разметки. Stas1/Stas2/Stas4 логика не менялась. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Handoff 2026-07-10 STAS4 Manual Labels 20260501-20260513 Draft

Статус: `STAS4_MANUAL_LABELS_20260501_20260513_DRAFT_NO_ML_NO_OPTUNA`.

Идет ручная разметка Stas4 review поверх стратегии `density_profile+structure_ta` и Stas2 run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260501_20260514_from_stas1_carry48_full_v1_20260709_142757`.

Источник 14-дневных PNG: `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum`.

Разметка хранится в `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels`.

Готовые черновые дни:
- `2026-05-01`: `10` KEEP / `58` CUT;
- `2026-05-02`: `8` KEEP / `44` CUT;
- `2026-05-03`: `6` KEEP / `52` CUT;
- `2026-05-04`: `9` KEEP / `65` CUT;
- `2026-05-05`: `8` KEEP / `51` CUT;
- `2026-05-06`: `7` KEEP / `62` CUT;
- `2026-05-07`: `11` KEEP / `68` CUT;
- `2026-05-08`: `8` KEEP / `61` CUT;
- `2026-05-09`: `7` KEEP / `60` CUT;
- `2026-05-10`: `10` KEEP / `52` CUT;
- `2026-05-11`: `10` KEEP / `66` CUT;
- `2026-05-12`: `6` KEEP / `70` CUT;
- `2026-05-13`: `4` KEEP / `82` CUT.

Для `2026-05-13` зафиксированы `LA002`, `LA043`, `LA058`, `LA072`. Желтый `X` среди выбранных: только `LA058`. Первая отметка была разбита курсором на две красные части и объединена в один вход `LA002`; `LA043` выбран как нижний crash-low рядом с более ранним `LA042`; `LA072` выбран как нижний/поздний локальный ретест рядом с `LA071`. Проверочный PNG: `ANNOTATED_20260513_KEEP_DRAFT.png`.

Граница: это `DRAFT` ручной ledger для обсуждения будущей ML-разметки. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Handoff 2026-07-10 STAS4 Manual Labels 20260501-20260512 Draft

Статус: `STAS4_MANUAL_LABELS_20260501_20260512_DRAFT_NO_ML_NO_OPTUNA`.

Идет ручная разметка Stas4 review поверх стратегии `density_profile+structure_ta` и Stas2 run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260501_20260514_from_stas1_carry48_full_v1_20260709_142757`.

Источник 14-дневных PNG: `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum`.

Разметка хранится в `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels`.

Готовые черновые дни:
- `2026-05-01`: `10` KEEP / `58` CUT;
- `2026-05-02`: `8` KEEP / `44` CUT;
- `2026-05-03`: `6` KEEP / `52` CUT;
- `2026-05-04`: `9` KEEP / `65` CUT;
- `2026-05-05`: `8` KEEP / `51` CUT;
- `2026-05-06`: `7` KEEP / `62` CUT;
- `2026-05-07`: `11` KEEP / `68` CUT;
- `2026-05-08`: `8` KEEP / `61` CUT;
- `2026-05-09`: `7` KEEP / `60` CUT;
- `2026-05-10`: `10` KEEP / `52` CUT;
- `2026-05-11`: `10` KEEP / `66` CUT;
- `2026-05-12`: `6` KEEP / `70` CUT.

Для `2026-05-12` зафиксированы `LA006`, `LA012`, `LA036`, `LA038`, `LA051`, `LA055`. Желтый `X` среди выбранных: только `LA036`. `LA051` выбран по прямому времени пользовательского подчеркивания, хотя рядом есть более поздние `LA052/LA053`; это зафиксировано как ручное решение по конкретному скрину. Проверочный PNG: `ANNOTATED_20260512_KEEP_DRAFT.png`.

Граница: это `DRAFT` ручной ledger для обсуждения будущей ML-разметки. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Handoff 2026-07-10 STAS4 Manual Labels 20260501-20260511 Draft

Статус: `STAS4_MANUAL_LABELS_20260501_20260511_DRAFT_NO_ML_NO_OPTUNA`.

Идет ручная разметка Stas4 review поверх стратегии `density_profile+structure_ta` и Stas2 run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260501_20260514_from_stas1_carry48_full_v1_20260709_142757`.

Источник 14-дневных PNG: `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum`.

Разметка хранится в `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels`.

Готовые черновые дни:
- `2026-05-01`: `10` KEEP / `58` CUT;
- `2026-05-02`: `8` KEEP / `44` CUT;
- `2026-05-03`: `6` KEEP / `52` CUT;
- `2026-05-04`: `9` KEEP / `65` CUT;
- `2026-05-05`: `8` KEEP / `51` CUT;
- `2026-05-06`: `7` KEEP / `62` CUT;
- `2026-05-07`: `11` KEEP / `68` CUT;
- `2026-05-08`: `8` KEEP / `61` CUT;
- `2026-05-09`: `7` KEEP / `60` CUT;
- `2026-05-10`: `10` KEEP / `52` CUT;
- `2026-05-11`: `10` KEEP / `66` CUT.

Для `2026-05-04` пользователь указал `9` входов. Зафиксированы `LA002`, `LA004`, `LA020`, `LA032`, `LA038`, `LA042`, `LA045`, `LA049`, `LA065`; `LA032` и `LA049` выбраны как нижние локальные входы в близких кластерах. Проверочный PNG: `ANNOTATED_20260504_KEEP_DRAFT.png`.

Для `2026-05-05` зафиксированы `LA001`, `LA005`, `LA013`, `LA026`, `LA028`, `LA036`, `LA041`, `LA044`. Спорные ретесты: `LA026` выбран вместо более раннего `LA024` с тем же low, `LA036` выбран вместо более раннего `LA034` с тем же low. Проверочный PNG: `ANNOTATED_20260505_KEEP_DRAFT.png`.

Для `2026-05-06` зафиксированы `LA001`, `LA008`, `LA016`, `LA021`, `LA039`, `LA052`, `LA061`. Спорный ретест: `LA021` выбран по прямому времени подчеркивания, хотя `LA020` ниже раньше. Проверочный PNG: `ANNOTATED_20260506_KEEP_DRAFT.png`.

Для `2026-05-07` зафиксированы `LA014`, `LA017`, `LA019`, `LA023`, `LA024`, `LA036`, `LA050`, `LA053`, `LA060`, `LA073`, `LA075`. В плотной первой группе `LA014/LA017/LA019` выбраны по прямому времени подчеркиваний и локальным low. Проверочный PNG: `ANNOTATED_20260507_KEEP_DRAFT.png`.

Для `2026-05-08` зафиксированы `LA009`, `LA010`, `LA021`, `LA041`, `LA045`, `LA048`, `LA060`, `LA069`. `LA009` и `LA010` имеют одинаковый low, но отмечены как две отдельные пользовательские отметки: ранний low и более поздний ретест. Проверочный PNG: `ANNOTATED_20260508_KEEP_DRAFT.png`.

Для `2026-05-09` зафиксированы `LA001`, `LA002`, `LA013`, `LA018`, `LA028`, `LA043`, `LA047`. Среди выбранных входов нет желтых `X` стратегии `density_profile+structure_ta`; `LA043` и `LA047` выбраны как нижние локальные входы в близких кластерах. Проверочный PNG: `ANNOTATED_20260509_KEEP_DRAFT.png`.

Для `2026-05-10` зафиксированы `LA006`, `LA030`, `LA035`, `LA041`, `LA045`, `LA046`, `LA051`, `LA056`, `LA057`, `LA059`. Желтый `X` среди выбранных: `LA030`, `LA035`, `LA041`, `LA045`, `LA046`, `LA051`. Проверочный PNG: `ANNOTATED_20260510_KEEP_DRAFT.png`.

Для `2026-05-11` зафиксированы `LA014`, `LA016`, `LA029`, `LA041`, `LA045`, `LA046`, `LA048`, `LA052`, `LA053`, `LA060`. Желтый `X` среди выбранных: только `LA016`. Пары `LA045/LA046` и `LA052/LA053` оставлены как отдельные пользовательские отметки. Проверочный PNG: `ANNOTATED_20260511_KEEP_DRAFT.png`.

Граница: это `DRAFT` ручной ledger для обсуждения будущей ML-разметки. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Handoff 2026-07-10 STAS2/STAS4 Compact Strips

Статус: `STAS2_STAS4_COMPACT_STRIPS_READY_NO_LOGIC_CHANGE_NO_ML_NO_OPTUNA`.

По просьбе пользователя изменен только визуальный слой дневных графиков: полосы `ФОН/LONG/SHORT/WAVE` в Stas2 overview и Stas4 overlay сделаны примерно в 2 раза ниже. Логика расчета фаз, LONG/SHORT, WAVE/GAP, CSV/XLSX и Stas1/Stas2 контракты не менялись.

Также исправлена нижняя ось времени дневного графика: теперь тики идут от `00:00` до следующего `00:00`, включая правую границу дня.

Файлы:

- `src/mlbotnav/visual_entry_stas2_market_phase_review.py`
- `src/mlbotnav/visual_entry_stas4_family_overlay.py`
- `tests/test_visual_entry_stas2_market_phase_review.py`

Smoke artifacts:

- `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260511_visual_half_strips_smoke_v1_20260710_073524/STAS2_DAY_OVERVIEW_20260511.png`
- `STAS4_FEATURE_HYPOTHESIS_REVIEW/visual_half_strips_smoke_v1/STAS4_pattern+structure_ta_OVERLAY_20260511_20260710_073654.png`

Проверки: `py_compile` для Stas2/Stas4, `pytest tests/test_visual_entry_stas2_market_phase_review.py -q`, smoke Stas2 `2026-05-11`, smoke Stas4 `pattern+structure_ta`.

## Handoff 2026-07-09 STAS3 V2 Clean Ready

Статус: `STAS3_V2_CLEAN_READY_NO_OLD_STAS3_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

Важно: предыдущий run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925` помечен как `INVALID_OLD_STAS3_BASE_DRAFT`. Он не является принятым V2, потому что был сделан через старый Stas3.

Актуальная реализация: `src/mlbotnav/visual_entry_stas3_v2_clean_review.py`. Старый Stas3-файл не используется как основа.

Финальный clean run: `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_clean_20260510_20260512_long_only_20260709_123622`.

Источник: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`; дни `2026-05-10..2026-05-12`.

Что сделано: clean V2 берет входы только из `STAS2_RECORDS.csv`, считает от `entry_price_5bps`, собирает context bundle из `STAS2_HOURLY_PHASES.csv`, `STAS2_MACRO_WAVES.csv`, `STAS2_CONTINUOUS_WAVES.csv` и исходных свечей. Выходы: `STAS3_V2_CLEAN_ENTRY_CONTEXT.csv`, `STAS3_V2_CLEAN_TP_PATH.csv`, `STAS3_V2_CLEAN_TP_DECISION.csv`, `STAS3_V2_CLEAN_PHASE_LADDER.csv`, `STAS3_V2_CLEAN_WRONG_TP.csv`, `STAS3_V2_CLEAN_NOISE.csv`, `STAS3_V2_CLEAN_REPORT_RU.md`, `STAS3_V2_CLEAN_TABLES.xlsx`.

Итог: `214` rows, `0` skipped, parity `true`, `157` hit 1%, `79` clean medium TP `>=1%`, `111` wrong 1% TP, `38` good-entry-but-wrong-1% TP, `99` noise, `41` phase ladder rows, `66` PNG, пустых PNG нет.

Проверки: `py_compile`; `pytest tests/test_visual_entry_stas3_v2_clean_review.py -q` -> `2 passed`; `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q` -> `4 passed`; acceptance CSV/XLSX/PNG прошел.

Открыть: `.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open browse`, `-Open xlsx`, `-Open report`, `-Open entries`, `-Open medium`.

## Handoff 2026-07-09 STAS3 V2 Ready

Статус: `INVALID_OLD_STAS3_BASE_DRAFT`.

Этот блок является историей ошибки. Этот run не считать принятым V2. Старый Stas3 V1 не удалялся и остается архивом.

Финальный run: `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925`.

Источник: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`; дни `2026-05-10..2026-05-12`.

Что сделано: рабочая V2-сетка `0.3..20.0%` без `0.2%`; строгий `entry_price_for_calc = entry_price_5bps`; missing `entry_price_5bps` идет в skipped; `SHORT` протянут только как risk context с `short_context_only_flag=True`; `WAVE/GAP/continuous` помечены `HINDSIGHT_WAVE_REVIEW`; добавлены V2 CSV/XLSX/report; основной визуал больше не рисует `MFE MAX` как trade/exit, только diagnostic.

Итог: `214` rows, `0` skipped, parity `true`, `157` hit 1%, `93` reasonable TP, `76` wrong 1% TP, `46` noise, `122` wrong/noise review rows, `55` PNG, пустых PNG нет.

Проверки: `py_compile`; `pytest tests/test_visual_entry_stas3_percent_ladder_review.py tests/test_visual_entry_low_anchor_suggester.py -q` -> `3 passed`; `pytest tests/test_visual_entry_stas2_market_phase_review.py -q` -> `3 passed`; acceptance скрипт по финальному run прошел.

Открыть: `.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open browse`, `-Open xlsx`, `-Open tp`.

## Handoff 2026-07-09 STAS3 V2 Reset TZ

Статус: `STAS3_V1_ARCHIVED_STAS3_V2_TZ_DRAFT_READY_NO_ML_NO_OPTUNA`.

Пользователь указал, что текущий Stas3 кривой и его нужно обнулить. Принято безопасное обнуление: старые Stas3 runs и код не удалять, а заморозить как `STAS3_V1_ARCHIVE_REVIEW_ONLY`.

Создано новое ТЗ:

`STAS3_PERCENT_LADDER_REVIEW/TZ_STAS3_V2_RESET_RU.md`

После дополнительной правки пользователя ТЗ уточнено: V2 разбирает только LONG. Быстрые TP: `0.3-0.9%`. Средние LONG-ходы: `1.0-2.0%` с шагом `0.1%`, затем `2.0-20.0%` с шагом `0.2%` и дедубликацией `2.0%`. Точки входа не искать заново: брать `anchor_time_utc`, `anchor_low_price`, `entry_time_utc`, `entry_open_price`, `entry_price_5bps` из `STAS2_RECORDS.csv`; `entry_price_for_calc = entry_price_5bps`. Актуальный источник для первого V2-разбора: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`; рабочие дни `2026-05-10`, `2026-05-11`, `2026-05-12`. По каждой LONG-сделке собрать единый context bundle: сессия, фон, LONG, `SHORT`-risk% как риск-фон, WAVE, волатильность/процентные блоки, volume-context. Short-входы, short-TP, short-ladder и short-статистика в Stas3 V2 запрещены. `ideal_review_tp_pct` и `max_feasible_review_tp_pct` - hindsight-review поля, не стратегия. Сделку не закрывать искусственно по границе `24h`, если волна продолжается через день.

Суть V2:

1. Stas3 остается post-entry audit, не стратегией;
2. `MFE MAX` нельзя рисовать/читать как TP или реальный выход;
3. reasonable TP должен быть фазовой статистикой достижимости, а не красивой целью по будущему максимуму;
4. быстрые TP, средние ходы и swing `5-7%` не смешивать в одну механику;
5. Stas2 `WAVE/GAP/continuous-wave` можно добавить только как явно маркированный context scope: `PRE_ENTRY_CAUSAL`, `POST_ENTRY_REVIEW`, `HINDSIGHT_WAVE_REVIEW`;
6. следующий шаг - проектировать/реализовать Stas3 V2 по новому ТЗ, не запускать ML/Optuna/scorer/target-lock/API.

README Stas3 обновлен статусом `STAS3_V1_ARCHIVE_REVIEW_ONLY__STAS3_V2_TZ_DRAFT_NO_ML_NO_OPTUNA`.

## Handoff 2026-07-09 STAS3 Rebuild From Latest STAS2

Статус: `STAS3_REBUILT_FROM_STAS2_SHORT_LABELS_V1_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

По просьбе пользователя Stas3 пересобран поверх актуального Stas2-графика, где уже видны `SHORT`, continuous `WAVE/GAP` и компактные проценты коротких сильных волн.

Источник Stas2:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138`

Новый Stas3 run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260508_20260512_from_stas2_short_labels_v1_20260709_084730`

Итог: `214` Stas2 rows input, `214` entry rows, `0` skipped, дни в entry-таблице `2026-05-10..2026-05-12`, `157` hit 1%, `93` rows с reasonable TP, `89` mismatch к 1% TP, `46` noise entry, `9` fast clean, `68` late-pump dependent, `53` PNG, пустых PNG нет. Workbook читается.

Проверки: `py_compile`, `pytest tests/test_visual_entry_stas3_percent_ladder_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, workbook load через `openpyxl`, CSV counts, PNG non-empty, `open_last_run.ps1 -Open browse -NoOpen`.

Важное ограничение: новые Stas2 `WAVE/SHORT` ledger-таблицы существуют в `STAS2_MACRO_WAVES.csv` и `STAS2_CONTINUOUS_WAVES.csv`, но пока не вшиты в каждую строку `STAS2_RECORDS.csv`. Поэтому текущий Stas3 пересобран по новому Stas2 source, но `macro_wave_*` еще не являются колонками Stas3 entry/TP tables. Если пользователь захочет видеть WAVE-контекст прямо в Stas3, следующий технический шаг - сделать безопасный review-only join `entry_time_utc -> STAS2_MACRO_WAVES/STAS2_CONTINUOUS_WAVES`, не превращая это в causal feature.

Граница: это Stas3 post-entry audit/review, не стратегия, не ML-label, не scorer, не target-lock. ML/Optuna/API не запускались.

## Handoff 2026-07-09 STAS2 Short Strong Wave Labels

Статус: `STAS2_SHORT_STRONG_WAVE_LABEL_READY_NO_ML_NO_OPTUNA_VISUAL_ONLY`.

По замечанию пользователя исправлен визуальный пропуск процента в слишком узком `WAVE`-квадрате. Расчет волн не менялся: добавлено только правило отрисовки, что короткая confirmed WAVE с видимым ходом `>= 1%` и длительностью `>= 5m` получает компактную подпись процента (`1.34%`) даже если блок короче обычного порога подписи `15m`.

Контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138`

Проверка на `2026-05-12`: `W38 LONG 12:32-12:40`, длительность `8m`, `visible_move_pct=1.336303`; на overview теперь подписан компактный процент. Run: `42` continuous rows, `46` day-slice rows, `84` PNG, `0` пустых PNG.

Проверки: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный run `2026-05-08..2026-05-12`, `openpyxl` load workbook, PNG non-empty.

Граница: это только визуальная подпись сильной короткой волны, не изменение расчета волн и не ML/TP-логика. ML/Optuna/scorer/target-lock/API не запускались.

## Handoff 2026-07-09 STAS2 Continuous Wave Ledger

Статус: `STAS2_MARKET_PHASE_REVIEW_CONTINUOUS_WAVE_READY_NO_ML_NO_OPTUNA_REVIEW_ONLY`.

По решению пользователя убрана жесткая привязка `WAVE` к UTC-дню. Теперь волна живет как глобальное событие без разрезания по `00:00`, а дневной график показывает только видимый срез этой волны. Это сохраняет удобный 24h overview, но не теряет движение, начавшееся вечером и закончившееся утром следующего дня.

Реализация: `src/mlbotnav/visual_entry_stas2_market_phase_review.py`.

Новые/обновленные сущности:

1. `STAS2_CONTINUOUS_WAVES.csv` и Excel-лист `Continuous waves` - глобальный ledger волн: `continuous_wave_id`, direction `LONG/SHORT/GAP`, start/end, move_pct, duration, status `CONFIRMED/ACTIVE/UNCONFIRMED`.
2. `STAS2_MACRO_WAVES.csv` и дневные `*_STAS2_MACRO_WAVES.csv` - дневные срезы continuous-волн: `macro_wave_visible_move_pct`, `macro_wave_full_move_pct`, `macro_wave_carry_from_prev_day`, `macro_wave_carry_to_next_day`.
3. Строка `WAVE` на overview теперь показывает переносы через день: `W08 >` в конце дня и `< W08` в начале следующего дня, с `vis/full` для длинных carry-срезов.

Финальный контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`

Источник Stas1:

`STAS1_GOOD_LOW_REVIEW/runs/stas1_20260510_20260512_carry48_for_stas2_v0_20260709_070902`

Итог run: `214` entry rows, `160` Stas1 GOOD, `54` Stas1 BAD, `29` continuous rows = `27` waves + `2` gaps, `31` day-slice rows = `29` wave slices + `2` gap slices, `4` carry-sреза через день, `80` PNG, `0` пустых PNG, `0` missing sources.

Проверенный перенос: `W08 SHORT` начался `2026-05-10 23:38`, продолжился после полуночи и закончился `2026-05-11 00:53`; полный ход `1.63%`, дневные срезы `0.57%` и `1.22%`. Еще один перенос: `W22 SHORT` `2026-05-11 19:42` -> `2026-05-12 01:41`, полный ход `2.97%`.

Проверки: `py_compile`, `pytest tests/test_visual_entry_stas2_market_phase_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный run `2026-05-10..2026-05-12`, `openpyxl` load workbook, PNG non-empty.

Граница: continuous-wave и day-slice WAVE/GAP остаются review/hindsight слоем для ручного анализа структуры движения. Не использовать их как causal ML feature, scorer, target-lock, entry/TP rule или торговую стратегию без отдельной causal-разметки. ML/Optuna/scorer/target-lock/API не запускались.

## Handoff 2026-07-09 STAS2 Macro Wave GAP Segments

Статус: `STAS2_MARKET_PHASE_REVIEW_WAVE_GAP_SEGMENTS_READY_NO_ML_NO_OPTUNA_REVIEW_ONLY`.

По замечанию пользователя на `STAS2_DAY_OVERVIEW_20260510.png` исправлена визуальная и табличная потеря промежутков в строке `WAVE`: если подтвержденная swing-волна не покрывает начало/конец дня или промежуток между волнами, теперь добавляется серый `GAP`-сегмент с процентом диапазона. Это не ломает текущую логику волн: `WAVE` по-прежнему считается по развороту `1%`, а `GAP` только закрывает визуальные/учетные дырки.

Рабочий файл: `src/mlbotnav/visual_entry_stas2_market_phase_review.py`. Тест обновлен: `tests/test_visual_entry_stas2_market_phase_review.py`.

Контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_gap_segments_v1_20260709_073810`

Источник Stas1:

`STAS1_GOOD_LOW_REVIEW/runs/stas1_20260510_20260512_carry48_for_stas2_v0_20260709_070902`

Итог run: `214` entry rows, `160` Stas1 GOOD, `54` Stas1 BAD, `34` macro-wave review rows = `28` confirmed WAVE + `6` GAP, `80` PNG, `0` пустых PNG, `0` missing sources. Workbook `STAS2_MARKET_PHASE_TABLES.xlsx` читается, лист `Macro waves` содержит и WAVE, и GAP.

Для `2026-05-10`: `GAP01 00:00-01:28 0.78%`, затем `7` WAVE-блоков, затем `GAP02 23:38-00:00 0.57%`. Малые волны около `31m` теперь тоже подписываются на графике.

Граница: `GAP` и `WAVE` являются visual/review слоем по уже видимому дневному графику. Не использовать `macro_wave_*`, `macro_wave_segment_kind=GAP`, границы волн или проценты волн как causal ML features, scorer, target-lock или торговую стратегию без отдельной causal-разметки. ML/Optuna/scorer/target-lock/API не запускались.

## Handoff 2026-07-09 STAS2 SHORT And Macro Wave Review

Статус: `STAS2_MARKET_PHASE_REVIEW_SHORT_MACRO_WAVE_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_PLUS_REVIEW_ONLY`.

По запросу пользователя Stas2-график расширен без изменения Stas1 и без Stas3/ML: к часовым полосам `Фон` и `LONG` добавлена полоса `SHORT`, а ниже добавлена переменная полоса `WAVE` для дневных swing-волн. `SHORT` считается внутри закрытого часа как упорядоченный ход `high -> subsequent low`. `WAVE` режет дневной график на переменные блоки по развороту `1%`, поэтому волна может занимать несколько часов и не ломается на границе часового квадрата.

Рабочий файл: `src/mlbotnav/visual_entry_stas2_market_phase_review.py`. Добавлен тест: `tests/test_visual_entry_stas2_market_phase_review.py`.

Финальный контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_short_macro_wave_v1_20260709_064759`

Источник Stas1:

`STAS1_GOOD_LOW_REVIEW/runs/stas1_20260504_20260509_carry48_for_stas2_v0_20260707_042858`

Итог run: `417` entry rows, `410` Stas1 GOOD, `7` Stas1 BAD, `144` hourly rows, `34` macro-wave rows, `6` дневных overview, `156` PNG, `0` пустых PNG, `0` missing sources. Excel `STAS2_MARKET_PHASE_TABLES.xlsx` читается и содержит лист `Macro waves`.

Для `2026-05-04` macro-wave строки совпадают с визуальной логикой пользователя: `LONG +3.11%`, `SHORT 3.11%`, `LONG +2.49%`, `SHORT 1.62%`, `LONG +1.50%`, `SHORT 1.42%`.

Граница: `WAVE` является review/hindsight слоем для визуальной сверки больших движений, а не causal feature для входа и не ML-label. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## Handoff 2026-07-06 STAS3 Percent Ladder Review

Статус: `STAS3_PERCENT_LADDER_REVIEW_READY_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

По прямому запросу пользователя `Стас3` отдельный Stas3-контур доведен до результата. Это supersedes предыдущую пометку `STAS3 Separate Chat Decision`: Stas3 реализован в этом рабочем чате как отдельный post-entry audit, не внутри Stas2.

Создана видимая папка `STAS3_PERCENT_LADDER_REVIEW/` с командами `run_day.ps1`, `run_range.ps1`, `open_last_run.ps1` и README. Рабочий движок: `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py`. Тест: `tests/test_visual_entry_stas3_percent_ladder_review.py`.

Stas3 читает готовый `STAS2_RECORDS.csv`, берет pre-entry фазу Stas2 на момент входа, загружает OHLCV после `entry_time_utc` и считает полную percent ladder `0.2/0.3/0.4/0.5/0.6/0.7/0.8/0.9/1.0/1.2/1.5/1.7/1.9/2.0/3.0/5.0/7.0%`. Добавлены отдельные таблицы: фаза входа, фактическое движение, разумный TP, ladder по фазам/LONG/setup/session/profile, skipped rows и русская `STAS3_TP_LADDER_V0_RU.md`.

Финальный контрольный run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260502_20260503_tp_ladder_v0_20260706_183011`

Источник Stas2:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535`

Сводка run: `110` Stas2 rows input, `110` entry rows, `0` skipped, row-count parity `True`, `110` hit 1% в 48h, `65` строк с расчетным reasonable TP, `73` TP mismatch к механическому 1%, `27` noise entry, `2` `FAST_CLEAN_1PCT`, `90` `LATE_PUMP_DEPENDENT`, `0` missing OHLCV, `24` PNG, `0` пустых PNG. Workbook `STAS3_PERCENT_LADDER_TABLES.xlsx` открывается через `openpyxl`, CSV имеет BOM `EF-BB-BF`.

Ключевые файлы результата: `STAS3_RECORDS.csv`, `STAS3_ENTRY_PHASE_TABLE.csv`, `STAS3_ACTUAL_MOVEMENT.csv`, `STAS3_REASONABLE_TP.csv`, `STAS3_TP_LADDER_BY_PHASE.csv`, `STAS3_TP_LADDER_BY_PROFILE.csv`, `STAS3_TP_LADDER_V0_RU.md`, `STAS3_REPORT_RU.md`.

Расширенный Stas3 run по последнему Stas2 за `2026-05-04..2026-05-09`:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_tp_ladder_v0_20260707_055929`

Источник:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_setup_quality_v0_20260707_043734`

Сводка расширенного run: `417` Stas2 rows input, `417` entry rows, `0` skipped, row-count parity `True`, `410` hit 1% в 48h, `283` строк с reasonable TP, `285` TP mismatch к механическому 1%, `84` noise entry, `13` `FAST_CLEAN_1PCT`, `238` `LATE_PUMP_DEPENDENT`, `0` missing OHLCV, `83` PNG, `0` пустых PNG. Workbook читается через `openpyxl`, CSV имеет BOM `EF-BB-BF`, русский отчет UTF-8 валиден.

Новый визуальный run с явным TP/EXIT overlay:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_tp_exit_overlay_v0_20260707_072226`

Что добавлено на графиках: треугольник entry, горизонтальная TP-линия, звезда `EXIT`, подпись времени до TP. Желтый цвет означает расчетный `TP v0`; серый пунктир `TP 1%` означает fallback, если фазовый TP не рассчитан. Run проверен: `417` rows, `0` skipped, `83` PNG, пустых PNG нет, workbook читается.

Финальный визуальный run с раздельными `SIGNAL -> ENTRY -> EXIT`:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_signal_entry_exit_overlay_v0_20260707_073915`

Что исправлено: Stas2 показывал low/anchor-сигнал, а Stas3 показывал исполнение `entry_time_utc`, из-за чего визуально казалось, что точки входа съехали. Теперь на closeup-графиках оранжевый `SIGNAL` стоит на `anchor_time_utc/anchor_low_price`, голубой `ENTRY` стоит на `entry_time_utc/entry_price_5bps`, рядом пишется цена входа, далее показан TP/EXIT. CSV/XLSX также получили `anchor_low_price`, `entry_open_price`, `entry_price_5bps`.

Финальный визуальный run с красной стрелкой отработки `ENTRY -> EXIT`:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_signal_entry_tp_move_v0_20260707_080253`

Что исправлено по последнему замечанию: прежняя желтая горизонтальная линия показывала только уровень цены TP, а не путь сделки. Теперь красная диагональная стрелка идет от `entry_time_utc/entry_price_5bps` до точки TP/EXIT; желтая или серая горизонталь оставлена как уровень цели. Run проверен: `417` rows, `0` skipped, `83` PNG, пустых PNG нет, workbook читается.

Актуальный run следующего слоя для вопроса “как учиться тянуть сделки выше 0.2% до большого хода/MFE”:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_big_move_review_v2_20260707_090246`

Что добавлено: `STAS3_LOW_SIGNAL_TO_MFE_MAX.csv`, `STAS3_ENTRY_TO_TP_PATH.csv`, `STAS3_EXIT_REVIEW_BUCKETS.csv`, `STAS3_EXIT_REVIEW_SUMMARY.csv`, листы Excel `Low to MFE max`, `Entry to TP path`, `Exit review`, `Exit review summary`, а также `STAS3_BIG_MOVE_REVIEW_PAGE_*.png`. Зеленая стрелка показывает `SIGNAL/ENTRY -> MFE MAX`, красная остается `ENTRY -> TP/EXIT`, фиолетовый маркер показывает `MAE MIN`. Это review-only слой, не стратегия и не ML-label.

Сводка run: `417` rows, `0` skipped, `141` `EARLY_1PCT_TRAIL_REVIEW`, `218` `BIG_MFE_BUT_DEEP_MAE_REVIEW`, `51` `LATE_MFE_PUMP_REVIEW`, `95` PNG, пустых PNG нет, workbook читается.

Открыть:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open browse
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open tp
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
```

Проверки выполнены: `py_compile`, `pytest tests/test_visual_entry_stas3_percent_ladder_review.py tests/test_visual_entry_low_anchor_suggester.py -q`, полный Stas3 run `2026-05-02..2026-05-03`, `openpyxl` load workbook, CSV BOM, PNG non-empty, проверка русского UTF-8 отчета, `open_last_run.ps1 -Open tp -NoOpen`.

Граница: Stas3 смотрит свечи после входа. Это анализ и проверка, не торговая стратегия. Нельзя переносить его поля обратно в Stas2 как causal features; нельзя запускать ML/export/training, Optuna, scorer, target-lock или API без отдельного явного approval.

## Handoff 2026-07-06 STAS3 Moves To Separate Chat

Статус: `STAS2_CLOSED_STAS3_IN_SEPARATE_CHAT_NO_ML_NO_OPTUNA`.

Пользователь уточнил: Stas3 будет делаться в другом чате. В этом чате не начинать реализацию Stas3, не писать новый post-entry слой и не запускать расчеты TP/MFE/MAE без нового прямого запроса.

Для следующего чата стартовая точка: Stas2 закрыт, использовать финальный visual-run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535` и audit-run `reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942`.

Граница сохраняется: Stas3 должен быть отдельным этапом `percent ladder / entry-TP validation`, а Stas2 остается только pre-entry/no-lookahead контекстом.

## Handoff 2026-07-06 STAS2 Closed For STAS3

Статус: `STAS2_CLOSED_FOR_STAS3_NO_ML_NO_OPTUNA`.

Пользователь подтвердил закрытие Stas 2 после сверки с ТЗ. Stas 2 считается принятым как отдельный pre-entry слой: Stas1 остается базой входов, Stas2 добавляет фазы рынка, сессии, weekday/weekend, `Фон`, `LONG`, `SETUP`, no-lookahead контроль и визуальный дневной обзор без текстового шума возле точек.

Рабочий финальный visual-run для дальнейшего Stas3:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535`

Широкий session/phase audit-run для схемы фаз и сессий:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942`

Что зафиксировано по ТЗ: `STAS 1 inventory` сделан, дни разбиты по часам, фазы считаются по часам, сессии оформлены как `6` UTC-корзин плюс отдельный `day_type`, weekday/weekend разведены, графики/heatmap есть, фаза перед входом считается только по свечам до входа. Stas1 не переписывался.

Следующий этап строго по ТЗ: `STAS 3 percent ladder and entry/TP validation`. В Stas3 нужно считать жизнь сделки после входа: MFE/MAE, достижимый процент, время до цели, просадку, 5m post-entry блоки и реалистичный TP. Это не переносить обратно в Stas2.

Запрет сохраняется: не запускать ML/export/training, Optuna, scorer, target-lock и API без отдельного явного решения.

## Handoff 2026-07-06 STAS2 Setup Quality Layer

Статус: `STAS2_MARKET_PHASE_REVIEW_SETUP_QUALITY_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

Исправлена смысловая путаница на Stas2 overview: `Фон` и `LONG` больше не читаются как разрешение на вход. В `src/mlbotnav/visual_entry_stas2_market_phase_review.py` добавлен отдельный слой `entry_setup_quality_*`, который оценивает чистоту конкретного low-входа по pre-entry данным: `stas1_risk_flags`, `stas1_feature_*`, `pre_15m/pre_30m` фон, wave и pullback.

Новый контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535`

Главная проверка по замечанию пользователя: участок `2026-05-02` около `LA045-LA047` в таблицах теперь помечен как `NOISE: после выноса` / `NOISE: low слабый`, а не как хорошая LONG-точка. На дневном overview текстовые названия возле точек убраны полностью, а сами точки входа оставлены как в Stas1. Stas1 outcome не изменялся: `110` строк, `110` Stas1 GOOD, `0` BAD; setup-сводка: `clean=17`, `working=16`, `warn=50`, `noise=27`.

Проверки: `py_compile`, полный Stas2 run `2026-05-02..2026-05-03`, `openpyxl` load workbook, `bad_context_before_entry=0`, `43` PNG, `0` пустых PNG. ML/Optuna/scorer/target-lock/API не запускались.

Открыть:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
```

## Handoff 2026-07-06 STAS2 Background And LONG Wave Visual Fix

Статус: `STAS2_MARKET_PHASE_REVIEW_BG_LONG_WAVE_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

Исправлена визуальная путаница Stas2: прежняя `Слабая` фаза теперь явно трактуется как `фон часа/окна`, а не как отсутствие движения вверх. В `src/mlbotnav/visual_entry_stas2_market_phase_review.py` добавлен отдельный слой `LONG-волна`:

1. `pre_*_background_phase` - старый фон range/volatility/path до входа;
2. `pre_*_long_wave_up_from_low_pct` - ход low -> subsequent high внутри pre-entry окна;
3. `pre_*_long_wave_pullback_from_high_pct` - откат от этой вершины к последнему закрытому close до входа;
4. дневной overview теперь рисует две полосы: `Фон` и `LONG`;
5. Excel получил лист `Long wave summary` и CSV `STAS2_ENTRY_LONG_WAVE_SUMMARY.csv`.

Stas1 не изменялся. TP/exit, MFE/MAE, 5m post-entry blocks и percent ladder сделки не добавлялись и остаются для Stas3.

Полный контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_bg_long_wave_v0_20260706_131201`

Проверки: `py_compile`, `pytest tests/test_visual_entry_low_anchor_suggester.py -q`, smoke Stas2, полный run `2026-05-02..2026-05-03`, `openpyxl` load workbook, CSV BOM `EF-BB-BF`, `bad_context_before_entry=0`, `43` PNG, `0` пустых PNG, хвостов `python.exe` нет.

Открыть:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
```

## Handoff 2026-07-06 STAS2 Market Phase Visual Review

Статус: `STAS2_MARKET_PHASE_REVIEW_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

Создан отдельный Stas2-контур по образцу Stas1:

1. видная папка `STAS2_MARKET_PHASE_REVIEW/`;
2. wrapper-команды `run_day.ps1`, `run_range.ps1`, `open_last_run.ps1`;
3. рабочие зоны `runs/`, `feedback/`, `snapshots/`;
4. новый движок `src/mlbotnav/visual_entry_stas2_market_phase_review.py`.

Stas1 не изменялся и остается источником входов. Stas2 читает готовые Stas1 run CSV и переносит на графики сессии, `weekday/weekend`, `effective_session`, hourly phase strip и rolling pre-entry контекст `5m/15m/30m/60m`.

Главная граница: Stas2 использует только бары `open_time_utc < entry_time_utc`. В `STAS2_RECORDS.csv` добавлены `context_max_open_time_utc` и `context_before_entry_check`; в контрольном run нарушений нет. TP/exit, percent ladder сделки, MFE/MAE и 5m-блоки после входа остаются для Stas3.

Полный контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_market_phase_review_v0_20260706_124134`

Сводка run: `110` entry rows, `78` Stas1 GOOD, `32` Stas1 BAD, `43` PNG, `0` пустых PNG, `0` нарушений `context_before_entry_check`, Excel workbook открывается.

Открыть:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
```

Проверки выполнены: `py_compile`, `pytest tests/test_visual_entry_low_anchor_suggester.py -q`, smoke/full Stas2 run, `openpyxl` load workbook, CSV BOM, no-lookahead guard, PNG non-empty, open script `-NoOpen`, python tails check. ML/Optuna/scorer/target-lock/API не запускались.

## Handoff 2026-07-06 STAS2 Market Phase Session Audit

Статус: `STAS2_MARKET_PHASE_SESSION_AUDIT_READY_NO_ML_NO_OPTUNA`.

Выполнены этапы строгого порядка:

1. `STAS 1 inventory`: текущая база не переписана; зафиксировано, что рабочий Stas 1 находится в `STAS1_GOOD_LOW_REVIEW/`, движок `src/mlbotnav/visual_entry_good_1pct_review_pool.py`, low-кандидаты из `src/mlbotnav/visual_entry_low_anchor_suggester.py`, графики: day overview, GOOD closeups, ALL closeups, `BROWSE_BY_DAY/`.
2. `STAS 2 market phases and sessions`: добавлен отдельный audit-слой `src/mlbotnav/visual_entry_stas2_market_phase_audit.py`, построен отчет по `SOLUSDT 1m 2026-05-02..2026-05-08` на актуальных Stas1 runs.

Финальный run: `reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942`.

Главный отчет: `reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942/STAS2_MARKET_PHASE_AUDIT_RU.md`.

Ключевой вывод: сессионная модель теперь разделена на `6` UTC-корзин времени плюс отдельный `day_type=weekday/weekend`. Weekend `2026-05-02..2026-05-03` заметно слабее weekday (`avg_phase_rank 1.48` против `2.87`), а сильнейшее буднее окно на срезе - `Пересечение Лондон/Нью-Йорк` (`avg_phase_rank 4.30`, `4` strong+ часов из `10`). Фаза перед входом считается отдельно только по свечам до `entry_time_utc`.

Следующий этап по ТЗ: `STAS 3 percent ladder and entry/TP validation`, но только после принятия схемы фаз/сессий Stas 2. ML/export/training, Optuna, scorer, target-lock и API не запускать.

## Handoff 2026-07-06 STAS1 Block 1 Locked

Статус: `STAS1_BLOCK_1_RUN_POOL_LOCKED_NO_ML_NO_OPTUNA`.

Пользователь зафиксировал завершение первого блока STAS1. Блок 1 - это рабочий генератор review-пула low-кандидатов:

1. входы собираются прогоном по выбранному дню или диапазону;
2. результаты сохраняются в `STAS1_GOOD_LOW_REVIEW/runs/`;
3. для просмотра использовать `BROWSE_BY_DAY/`;
4. процент цели управляется через `run_day_1pct.ps1`, `run_day_0p5.ps1` или `--target-pct`;
5. перенос outcome через ночь управляется `-OutcomeLookaheadHours`.

В следующем чате не начинать новый скрипт и не откатываться к старым веткам. Брать STAS1 Block 1 как готовую основу и двигаться дальше по чистке шума/ручному feedback/калибровке значимого low.

Запрещено: ML/export/training/scorer/target-lock/Optuna/API без отдельного явного approval.

## Handoff 2026-07-06 STAS1 Carry Outcome

Статус: `STAS1_CARRY_OUTCOME_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

STAS1 получил bounded carry-outcome режим:

1. `-Day .. -EndDay` задает только период создания входов;
2. `-OutcomeLookaheadHours` задает, сколько часов после входа можно искать достижение цели;
3. запись кандидата остается в дне входа;
4. `hit_day_utc`, `hold_minutes_to_target`, `carried_overnight`, `outcome_status` записываются в CSV/JSON;
5. future outcome остается offline label, не входной фичей.

Smoke-run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_smoke_carry48_20260507_20260508_v0_20260706_081637`.

Сводка smoke-run: `148` кандидатов, `80` same-day, `68` carried overnight.

Команда для продолжения:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-07 -EndDay 2026-05-08 -OutcomeLookaheadHours 48 -RunLabel stas1_20260507_20260508_carry48_v0 -RenderGoodLimit 0
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
```

Не делать: ML/export/training/scorer/target-lock/Optuna/API. Следующий смысл - пользовательский visual review и чистка шума low-кандидатов.

## Handoff 2026-07-06 STAS1 Browse By Day

Статус: `STAS1_BROWSE_BY_DAY_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

STAS1 renderer теперь создает `BROWSE_BY_DAY/` внутри каждого нового run. Это основной способ просмотра глазами:

1. `00_RUN_INDEX.png` - индекс run;
2. `2026-05-04/00_20260504_OVERVIEW.png` - общий график дня;
3. `2026-05-04/01_20260504_ALL_CLOSEUPS_PAGE_01.png` и дальше - сделки дня по времени;
4. `YYYYMMDD_RECORDS.csv` - дневной CSV.

`open_last_run.ps1` получил режимы:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open index
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-04
```

`-Open all` и `-Open allcloseups` больше не должны открывать все PNG отдельными окнами.

Контрольный run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260504_20260506_browse_by_day_v0_20260706_063954`.

Граница: это визуальный review/outcome слой. Не запускать ML/export/training/scorer/target-lock/Optuna/API.

## Handoff 2026-07-06 STAS1 ALL Closeups GOOD+BAD

Статус: `STAS1_ALL_CLOSEUPS_BAD_X_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

В STAS1 добавлен новый визуальный режим для ручной чистки:

1. `GOOD_1PCT_REVIEW_POOL_GOOD_CLOSEUPS_PAGE_*.png` - старые страницы только GOOD;
2. `GOOD_1PCT_REVIEW_POOL_ALL_CLOSEUPS_PAGE_*.png` - новые страницы GOOD+BAD;
3. GOOD = зеленый треугольник;
4. BAD = красный полупрозрачный крест.

Контрольный run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260503_all_closeups_bad_x_v0_20260706_060244`.

Сводка: `58` кандидатов, `36` GOOD, `22` BAD, `8` ALL closeup pages.

Если пользователь просит открыть актуальный просмотр всех сделок, использовать:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open allcloseups
```

Граница: это визуальный review/outcome слой. Не запускать ML/export/training/scorer/target-lock/Optuna/API.

## Handoff 2026-07-03 STAS1 Good Low Review

Статус: `STAS1_V0_BASELINE_MAIN_LOW_REVIEW_SCRIPT_NO_ML_NO_OPTUNA`.

Пользователь решил зафиксировать текущий рабочий скрипт `GOOD_1PCT_REVIEW_POOL` как основной контур для ближайшей доработки low-кандидатов. Новый рабочий ярлык: `STAS1`.

Создана папка:

`STAS1_GOOD_LOW_REVIEW/`

В ней:

1. `README_RU.md`;
2. `run_day_1pct.ps1`;
3. `run_day_0p5.ps1`;
4. `open_last_run.ps1`;
5. `feedback/README_RU.md`;
6. `snapshots/README_RU.md`.

Движок остается:

`src/mlbotnav/visual_entry_good_1pct_review_pool.py`

Будущая зона правки шума:

`src/mlbotnav/visual_entry_low_anchor_suggester.py`

Не смешивать это с `manual_reanchors_v0`: manual reanchors - только чистый ручной ledger, а `STAS1/GOOD_1PCT` - генератор review-пула. ML/export/training/scorer/target-lock/Optuna/API запрещены.

## Handoff 2026-07-02 Bybit Hedge Mode Note

Статус: `HEDGE_MODE_API_NOTE_LOCKED_FUTURE_HEDGE_SIM_NO_REAL_API`.

Пользователь попросил запомнить возможность хеджирования на Bybit через API. Зафиксировано: для Bybit V5 `linear` USDT perpetual hedge/both-sides режим позволяет держать LONG и SHORT одновременно. Для API это означает `mode=3`, `positionIdx=1` для LONG и `positionIdx=2` для SHORT.

Важно: это не текущий боевой слой. Реальные API-ордера, ключи, смену настроек аккаунта и торговый запуск не делать без отдельного явного разрешения пользователя.

Следующий рабочий порядок не меняется: сначала `DCA_RISK_AUDIT_V0` по `W18-W20`. После него можно проектировать отдельный `HEDGE_SIM_V0`: симуляция защитного short hedge против DCA-перегруза, сравнение с no-hedge, расчет просадки/маржи/комиссий. Не смешивать hedge с ML, Optuna, scorer или target-lock.

## Handoff 2026-07-02 Daily 10 Long Trades Phase Ladder

Статус: `DAILY_10_LONG_TRADES_PHASE_LADDER_LOCKED_FOR_DCA_AUDIT_NO_ML_NO_OPTUNA`.

Пользователь уточнил цель: хочется изучить режим `10` long-сделок в день, но рынок нужно делить по фазам движения, а не мерить только одним `+1%`.

Лестница фаз для следующего аудита:

1. `0.3-0.5%`;
2. `0.9-1.0%`;
3. `1.5-2.0%`;
4. `2.2-4.0%+`.

Следующий исполнитель должен учитывать это в `DCA_RISK_AUDIT_V0`: для каждого low-entry считать, какую фазу рынок дал, сколько времени до нее шло, какая была просадка, сколько сделок висело одновременно, какая сессия/часть дня была активна. Не считать `10/day` обязательством добирать плохие сделки. Не передавать эти outcome-фазы в ML как causal feature.

## Handoff 2026-07-02 DCA Risk And Knife Map Rails

Статус: `SHORT_RANGE_DCA_RISK_RAILS_LOCKED_NO_ML_NO_OPTUNA`.

Пользователь сформулировал ключевую проблему: в `+1% review-pool` много серий входов подряд, которые сначала уходят в просадку. Если такую выборку дать ML как обычные good-входы, модель может научиться покупать ножи и перегружать DCA-корзину.

Решение процесса:

1. Не запускать полный `126`-дневный `FULL_HISTORY_KNIFE_MAP_V0` прямо сейчас.
2. Сначала разбирать короткий диапазон `W18-W20` (`2026-04-27..2026-05-17`, `21` день), run `W18_W20_learning_20260702_082819`.
3. На этом диапазоне сделать `DCA_RISK_AUDIT_V0`: DCA-корзины, max adverse move, число докупок, средняя цена, время в минусе, поддержка при плечах, PNG для глаз.
4. Довести классы/кластеры до понятного состояния: `GOOD_CLEAN_RECLAIM`, `GOOD_DCA_SURVIVABLE`, `BORDERLINE_SOFT`, `BAD_FALLING_KNIFE`, `BAD_CLUSTER_OVERLOAD`, `BAD_NO_ROOM`, `REJECT_VISUAL`.
5. Только после этого переходить к full-history на все доступные дни.

Следующий исполнитель должен брать именно `DCA_RISK_AUDIT_V0` по `W18-W20`. Не переходить к ML, Optuna, scorer, target-lock или full-history без отдельного решения пользователя.

## Handoff 2026-07-02 Low Anchor Entry 1pct Label Review V1 13 May

Статус: `LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Сделано: после пользовательской правки пересобран `SOLUSDT 1m 2026-05-13` по правильному execution-контракту:

```text
значимый low = signal
следующая свеча = entry
рабочая цена = entry open + 5bps
target = execution price * 1.01
slippage band = 0bps / 5bps / 10bps
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_FULL_DAY_20260513.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_ZOOM_PAGE_01_20260513.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513_RU.md
```

Счетчики: всего `87` candidates; `GOOD_STRONG_HIT_1PCT_AT_10BPS = 4`; `GOOD_NORMAL_HIT_1PCT_AT_5BPS = 0`; `GOOD_SOFT_HIT_1PCT_AT_0BPS = 1`; `BAD_NO_1PCT_EVEN_0BPS = 82`.

Следующий шаг: показать пользователю full-day и zoom page 01, получить визуальный вердикт `норм / фиксить / сдвиг`. Не запускать scorer, target-lock, Optuna, ML/export/training.

## Handoff 2026-07-02 Target 1pct Price Fix V0

Статус: `TARGET_1PCT_PRICE_FIX_V0_READY_NO_ML_NO_OPTUNA_NO_SCORER`.

Сделано: зафиксированы цены цели `+1%` для ручных эталонов `2026-05-14 M01..M19` и `2026-05-15 T15L confirmed 7`. Правило: `target_1pct_price = entry_price_plus_5bps * 1.01`.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/target_1pct_price_fix_v0/TARGET_1PCT_PRICE_FIX_V0_20260702.csv
reports/final_review/visual_entry_v3/fresh_target_led/target_1pct_price_fix_v0/TARGET_1PCT_PRICE_FIX_V0_20260702.json
reports/final_review/visual_entry_v3/fresh_target_led/target_1pct_price_fix_v0/TARGET_1PCT_PRICE_FIX_V0_20260702_RU.md
```

Итог: всего `26` входов; `2026-05-14` дошли до `+1%` `13/19`; `2026-05-15` дошли до `+1%` `4/7`.

Граница: это outcome/reference слой. Не использовать `+1%` как признак выбора входа. Не запускать scorer, target-lock, Optuna, ML/export/training без отдельного решения пользователя.

## Handoff 2026-07-01 Target-Led Dataset Base V0

Статус: `TARGET_LED_DATASET_BASE_V0_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA`.

Пользователь уточнил: плохие входы уже отклонялись вручную, нужно собрать всю базу/dataset по 14 и 15 мая. Сделано: добавлен и запущен `src/mlbotnav/visual_entry_target_led_dataset_base_v0.py`.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v0/TARGET_LED_DATASET_BASE_V0_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v0/TARGET_LED_DATASET_BASE_V0_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v0/TARGET_LED_DATASET_BASE_V0_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v0/TARGET_LED_DATASET_BASE_V0_SUMMARY_20260701.png
```

Состав: всего `107` строк; future supervised labels `92`; good `26`; reject `66`; unlabeled review `15`.

Разбивка: `2026-05-14` = `19` good, `51` reject, `15` unlabeled review; `2026-05-15` = `7` good, `15` reject.

ML-safe core blocks: `B015/B017/B010/B013/B019/B020`. Context-only: `B014/B018/B008/B024`. Нельзя как одиночный ALLOW: `B009/B021/B022/B023/B026/B016/B025`.

Граница: это база для будущего ML, но не `APPROVED_FOR_ML`, не ML-export и не обучение.

## Handoff 2026-07-01 B018 BOS Repeat 14 May

Статус: `B018_BOS_STRATEGY_REVIEW_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь попросил повторить BOS-стратегию. Сделано отдельно, без остальных блоков: добавлен и запущен `src/mlbotnav/visual_entry_bos_strategy_review_v2f.py`.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_FULL_DAY_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_01_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_02_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_03_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_04_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_05_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_20260514.csv
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_20260514.json
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_20260514_RU.md
```

Короткий вывод: `BOS_UP=41`, `BOS_DOWN=42`, `CHOCH-like=8` за день. Это шумно как самостоятельный сигнал. Для лонга `B018` годится как context/evidence: `down break -> reclaim/CHOCH -> entry` или `BOS_UP` как подтверждение продолжения, но не как одиночный `ALLOW`.

Следующий шаг: показать пользователю PNG. Если норм, вернуться к выбору первого кластера/паспорта-кандидата из V2E.

## Handoff 2026-07-01 V2E Summary Matrix 14 May

Статус: `V2E_SUMMARY_MATRIX_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Сделано: добавлен и запущен `src/mlbotnav/visual_entry_strategy_passport_summary_v2e.py`. Он сводит `V2A/V2B/V2C/V2D` CSV в одну матрицу по `SOLUSDT 1m 2026-05-14 M01..M19`.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_SUMMARY_MATRIX_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_SUMMARY_MATRIX_20260514.csv
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_BLOCK_SUMMARY_20260514.csv
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_SUMMARY_MATRIX_20260514.json
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_SUMMARY_MATRIX_20260514_RU.md
```

Короткий вывод: слишком широкие блоки `B014/B018/B009/B021/B022/B023`; кандидаты evidence `B015/B017/B010/B013/B019/B020`; `B026` конфликтует `8/19` и не годится как простой allow.

Следующий шаг: показать пользователю PNG. Если норм, выбрать первый рабочий кластер/паспорт-кандидат по 14 мая. Scorer, target-lock, Optuna и ML/export/promotion запрещены.

## Handoff 2026-07-01 V2D Pattern 14 May

Статус: `V2D_PATTERN_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Сделано: добавлен и запущен `src/mlbotnav/visual_entry_strategy_passport_overlay_v2d_patterns.py` для `SOLUSDT 1m 2026-05-14 M01..M19`.

Наложены pattern-блоки `B019-B024`. `B025` оставлен за бортом active-слоя как context/unsafe без отдельного решения.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_FULL_DAY_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_ZOOM_PAGE_01_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_ZOOM_PAGE_02_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_ZOOM_PAGE_03_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_ZOOM_PAGE_04_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_OVERLAY_20260514.json
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_OVERLAY_20260514.csv
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_OVERLAY_20260514_RU.md
```

Короткий вывод: `B019` = support `15/19`, conflict `1/19`; `B020` = support `9/19`; `B021` = support `19/19`; `B022` = support `19/19`; `B023` = support `17/19`; `B024` = support `16/19`. `B021/B022` слишком широкие как entry-filter, поэтому это visual evidence/context, не готовый сигнал.

Следующий шаг: показать пользователю PNG. Если норм, идти в `V2E_SUMMARY_MATRIX` по 14 мая: собрать таблицу `M01..M19 -> support/conflict/silent` по слоям `V2A/V2B/V2C/V2D`. Scorer, target-lock, Optuna и ML/export/promotion запрещены.

## Handoff 2026-07-01 V2C ADX/Stochastic 14 May

Статус: `V2C_ADX_STOCH_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь уточнил: `RSI`, `MACD` и `EMA` уже смотрели, поэтому вместо повторения взять `ADX` и `Stochastic`.

Сделано: добавлен и запущен `src/mlbotnav/visual_entry_strategy_passport_overlay_v2c_adx_stoch.py` для `SOLUSDT 1m 2026-05-14 M01..M19`.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_FULL_DAY_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_ZOOM_PAGE_01_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_ZOOM_PAGE_02_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_ZOOM_PAGE_03_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_ZOOM_PAGE_04_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_OVERLAY_20260514.json
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_OVERLAY_20260514.csv
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_OVERLAY_20260514_RU.md
```

Короткий вывод: `B008_ADX14` = support `16/19`, conflict `1/19`; `B009_STOCH14` = support `19/19`, conflict `0/19`. Stochastic слишком широкий как entry-filter; ADX только режим силы, не направление. Это visual evidence/context, не сигнал.

Следующий шаг: показать пользователю PNG. Если норм, идти в `V2D_PATTERN_LAYER` на 14 мая: `B019-B024`; `B025` не брать active.

## Handoff 2026-07-01 V2B Flow/Density 14 May

Статус: `V2B_FLOW_DENSITY_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Последний пользовательский разворот: “так мы с 14 днем мы не все применили блоки”. Это правильная коррекция. Не переходить на `T15/2026-05-15`, пока 14 мая не закрыт по слоям `V2A -> V2B -> V2C -> V2D -> V2E`.

Сделано: создан и запущен `src/mlbotnav/visual_entry_strategy_passport_overlay_v2b.py` для `SOLUSDT 1m 2026-05-14 M01..M19`.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_FULL_DAY_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_ZOOM_PAGE_01_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_ZOOM_PAGE_02_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_OVERLAY_20260514.json
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_OVERLAY_20260514.csv
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_OVERLAY_20260514_RU.md
```

Короткий вывод: `B010_VOLUME_FLOW` = `13/19`, `B013_DENSITY_VPOC` = `12/19`, `B026_VWAP_DISTANCE` = `8/19` support. Это не entry signal, только visual evidence/context.

Следующий шаг: показать пользователю V2B full-day и zoom pages. Если норм, делать `V2C_MOMENTUM_LAYER` на 14 мая: `B006 RSI`, `B007 MACD`; `B005 EMA` пока deferred/reference.

## Handoff 2026-07-01 V2A Structure User Review Audit

Статус: `V2A_STRUCTURE_20260514_VISUAL_AUDIT_DONE_NO_SCORER_NO_ML_NO_OPTUNA`.

Последний пользовательский запрос: “поехали” после обсуждения, как не уйти в кашу.

Сделано: просмотрены `V2A_STRUCTURE_FULL_DAY_20260514.png`, zoom pages и Fibo anchor pages. Добавлен короткий audit-файл:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_USER_REVIEW_AUDIT_20260701_RU.md
```

Главный вывод: V2A полезен как visual structure/evidence, но не является сигналом. `B014` и `B018` слишком широкие (`18/19` и `17/19`) и остаются контекстом. `B017` потенциально полезен для retest/reclaim. `B015 Fibo` остается `context_only`, пока нет правила свежести anchor-ноги.

Следующий безопасный шаг: тот же `V2A_STRUCTURE_LAYER` на `2026-05-15` по 7 T15 входам. Не запускать scorer, target-lock, Optuna, ML/export/promotion.

## Handoff 2026-07-01 V2A Structure Overlay 14 May

Статус: `V2A_STRUCTURE_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Последний пользовательский запрос: наложить стратегии/паспорта на графики и сначала показать `2026-05-14`.

Сделано: добавлен `src/mlbotnav/visual_entry_strategy_passport_overlay_v2a.py` и собран визуальный overlay по ручному эталону `SOLUSDT 1m 2026-05-14 M01..M19`.

Наложены блоки `B014/B015/B017/B018`:

1. support/resistance/range/channel;
2. Fibo по последней подтвержденной чередующейся pivot-ноге;
3. breakout/retest event memory;
4. internal/external BOS/CHOCH-like.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_FULL_DAY_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_01_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_02_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514.json
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514.csv
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514_RU.md
```

Граница: это visual evidence, не `ALLOW`-scorer и не готовый сигнал. Scorer, target-lock, Optuna и ML не запускались. Entry price и `+5 bps` показаны только для execution/control.

Follow-up аудит с агентом выявил и исправил риск lookahead: первый вариант строил Fibo/BOS через full-day zigzag до фильтра по signal. Текущий скрипт пересобирает zigzag prefix-causal из подтвержденных pivot на момент `signal/event`; старые переменные `zigzag_10/pivots_internal/pivots_external` удалены. CSV/zoom теперь показывают `entry_open_price` и `entry + 5 bps`.

Пользователь указал, что Fibo непонятно как натянута. Добавлены отдельные страницы:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_FIBO_ANCHORS_PAGE_01_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_FIBO_ANCHORS_PAGE_02_20260514.png
```

На них видны `A -> B` anchors, direction и уровни. Рабочий вывод: Fibo пока только context/evidence. Перед использованием как passport signal нужно отдельное правило свежести ноги и допустимого расстояния от signal.

Следующий шаг: показать PNG пользователю. Если пользователь скажет `норм`, следующий V2A-шаг — наложить тот же слой на `2026-05-15` по 7 входам T15. Если скажет `шумно/фиксить`, править читаемость/слои 14 мая, не меняя ручные входы.

## Handoff 2026-07-01 Existing Passport Reconciliation

Статус: `ACTIVE_EXISTING_PASSPORT_RECONCILIATION_AND_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь уточнил направление: паспорта уже собраны по полочкам, их не нужно создавать заново. Сейчас надо сверить существующие связки `Bxxx -> Fxxx -> passport MD -> matrix YAML -> runtime action`, затем наложить стратегии на два эталона `19+7` full-day с локальными strategy squares внутри дня.

Подключенный агент `Lorentz` провел read-only аудит: `26` блоков `B001..B026`, `82` активных не отключенных `Fxxx` связки, `82` активных matrix YAML; у всех активных связок найдены `passport_path` и `active_matrix_path`. `B001_RET_N_TOURNAMENT` отключен как diagnostic и в overlay не берется.

Главный roadmap:
`docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_STRATEGY_PASSPORT_ROADMAP_RU.md`.

Manifest-сверка:
`docs/CALIBRATION_NODE_CURRENT/PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md`.

Активные рельсы обновлены:
`docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_RAILS_RU.md`.

Следующий исполнительный шаг:

```text
V2A_STRUCTURE_LAYER
```

Порядок слоев:

```text
V2A0 registry reconciliation done -> V2A structure -> V2B flow/density -> V2C momentum -> V2D pattern -> V2E summary matrix
```

V2A берет структуру: `B014 LEVEL/RANGE/CHANNEL`, `B015 FIBONACCI_GRID`, `B017 BREAKOUT_RETEST`, `B018 MARKET_STRUCTURE BOS/CHOCH`; `B016 ENTRY_QUALITY_CONTEXT` только muted/context-only.

Граница: ручные входы `M01..M19` и 7 T15 не менять; scorer, target-lock, Optuna и ML не запускать.

## Handoff 2026-07-01 Git Remote Push MLbotNav

Статус: `GIT_REMOTE_PUSH_DONE_MAIN_TRACKS_ORIGIN_MAIN`.

Локальный репозиторий `C:\Users\007\Desktop\MLbotNav` подключен к `origin = https://github.com/Stanislav1567/MLbotNav.git`. Автор локального репозитория: `Stanislav1567 <Stanislav1567@users.noreply.github.com>`.

Первый коммит `e178c49 Initial commit` успешно отправлен в `origin/main`. Ветка `main` отслеживает `origin/main`. Проверено: `git status --short --branch` показывает чистое состояние `main...origin/main`.

Исключения Git сохранены: `.env`, `.venv`, `.vscode`, `data/`, `models/`, `reports/`, `logs/`, `packs/`, `tmp/`, `_codex_offload_*`, `_locked_tmp_*`, backup-файлы. `.gitattributes` добавлен для стабильных окончаний строк.

## Handoff 2026-07-01 Git Init MLbotNav

Статус: `SUPERSEDED_BY_GIT_REMOTE_PUSH_DONE`.

В `C:\Users\007\Desktop\MLbotNav` выполнен `git init`, ветка переименована в `main`. `.gitignore` расширен, чтобы не добавлять в историю `.env`, `.venv`, `.vscode`, `data/`, `models/`, `reports/`, `logs/`, `packs/`, `tmp/`, `_codex_offload_*`, `_locked_tmp_*`, `*.bak-*`. `.env.example` очищен от локального пользовательского пути и оставлен с placeholder.

Проверено: `git check-ignore` подтверждает игнор секретов/артефактов/бэкапов. После добавления `.gitattributes` и расширения backup-ignore в индексе `646` файлов, около `11.12 MB`; backup-файлы не staged. GitHub CLI `gh` не установлен, Git Credential Manager есть. Для коммита нужно настроить `user.name` и `user.email`; для push нужен URL пустого remote-репозитория.

## Handoff 2026-07-01 Strategy Passport Gap Audit

Статус: `STRATEGY_PASSPORT_GAP_AUDIT_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Последняя правка пользователя: V1 визуально норм, но не видно созданные стратегии и паспорта `swing`, `BOS`, `Fibonacci` и т.д.

Ответное действие: создан аудит пропуска. Текущий V1 не является passport overlay; он только рисует evidence-панели и простые подсказки. Не хватает строгого слоя `ALLOW 1/0` по паспортам `F012-F052`, а также матрицы совпадений по 26 ручным входам.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_STRATEGY_PASSPORT_GAP_AUDIT_20260701_RU.md`.

Следующий исполнительный шаг: собрать `INDICATOR_HYPOTHESIS_REVIEW_V2_STRATEGY_PASSPORT_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA` по тем же `M01..M19` и 7 T15. Ручные входы не менять. Scorer, target-lock, Optuna и ML не запускать.

## Handoff 2026-07-01 Codex Agent Launch Kit MLbotNav

Статус: `CODEX_AGENT_LAUNCH_KIT_MLBOTNAV_READY_NO_PROJECT_CODE_CHANGE`.

Для проекта `C:\Users\007\Desktop\MLbotNav` создан отдельный запуск Codex в папке рабочего стола `C:\Users\007\Desktop\Codex Agent`:

1. `Start MLbotNav Codex Agent.cmd`;
2. `Start-MLbotNav-Codex-Agent.ps1`;
3. `Resume MLbotNav Codex Agent.cmd`;
4. `Resume-MLbotNav-Codex-Agent.ps1`.

Проектный `AGENTS.md` уже существовал и не перезаписывался. Глобальный Codex уже содержит trusted-запись для `c:\users\007\desktop\mlbotnav`, профили `agent` и `agent-safe` существуют, авторизация идет через ChatGPT. Проект сейчас не является Git-репозиторием; перед широкими правками агент должен предупреждать и не запускать `git init` без явного согласия пользователя.

## Handoff 2026-07-01 Indicator/Hypothesis Review V1 19+7

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V1_M01_M19_T15V1_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь остановил переход к passport: перед ним нужен отдельный второй слой с RSI/MACD/Fibo/BOS/volume/density по двум эталонам. Создан новый пакет `indicator_hypothesis_review_v1`.

Использовать:

1. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_M01_M19_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_T15_7_20260515.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_ZOOM_T15_7_20260515.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_20260701_RU.md`.

`indicator_hypothesis_review_v0` не использовать как текущий слой для 19+7, потому что он собран до `T15 draft_ledger_v1` и содержит старые T15 времена/22 candidates. Следующий шаг: показать V1 пользователю и ждать `норм/фиксить`. Не запускать scorer, target-lock, Optuna, ML/export.

## Handoff 2026-07-01 T15 Draft Ledger V1 Confirmed

Статус: `T15_DRAFT_LEDGER_V1_USER_CONFIRMED_NEXT_PASSPORT_C01_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь подтвердил `норм` по `draft_ledger_v1`. Рабочий слой: `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/`.

Дальше идти по рельсам в draft passport по одному кластеру: `T15_C01_SUPPORT_RETEST_LOW`, входы `T15L02`, `T15L08`, `T15L16`.

Не запускать scorer, target-lock, Optuna или ML/export. Цена входа и `entry + 5 bps` остаются только execution/control. EMA не использовать как active condition.

## Handoff 2026-07-01 T15 Draft Ledger V1 Red Arrow Fix

Статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_RED_ARROW_FIX_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь прислал скрин с красными стрелками. Рабочий draft-ledger обновлен с тремя сдвигами:

- `T15L02`: entry `02:35` -> `02:34`;
- `T15L07`: entry `06:23` -> `06:21`;
- `T15L08`: entry `08:32` -> `08:31`.

Остальные входы без изменения. `draft_ledger_v0` superseded для дальнейшего passport discussion.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.json`.

Следующий шаг: показать v1 пользователю и получить `норм / фиксить`. Scorer, target-lock, Optuna и ML/export запрещены.

## Handoff 2026-07-01 T15 Draft Ledger / Cluster Discussion V0

Статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

После `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA` создан draft-ledger по 7 confirmed entries:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Кластеры:

1. `T15_C01_SUPPORT_RETEST_LOW`: `T15L02`, `T15L08`, `T15L16`; первый кандидат для passport discussion.
2. `T15_C02_DEEP_CAPITULATION_LOW`: `T15L06`, `T15L13`; второй кандидат.
3. `T15_C03_HOT_RECLAIM_CONTINUATION`: `T15L07`, `T15L11`; наблюдать, не смешивать в первый паспорт.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.json`.

Следующий шаг: показать пользователю PNG и получить `норм / фиксить`. После подтверждения можно делать draft-паспорт только по одному кластеру, первично `T15_C01_SUPPORT_RETEST_LOW`. Scorer, target-lock, Optuna и ML/export запрещены.

## Handoff 2026-07-01 T15 User Verdict V1

Статус: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: “тут 7 должно входов”. Исправлен слой verdict: все 7 неперечеркнутых кандидатов из feedback v2 теперь `user_confirmed_entry`.

Confirmed entries:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.json`.

`user_verdict_v0` superseded и не должен использоваться как рабочий слой. Следующий шаг: draft-ledger/cluster discussion по всем 7 entries. Не запускать target-lock/scorer/Optuna/ML.

## Handoff 2026-07-01 Indicator/Hypothesis Visual Review V0

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Добавлен модуль:
`src/mlbotnav/visual_entry_indicator_hypothesis_review.py`.

Назначение: визуально сравнить manual gold `2026-05-14` и актуальный feedback `2026-05-15` через RSI14, MACD, volume, density, trailing swing, BOS и Fibo. Это не scorer и не ML.

Команды:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_indicator_hypothesis_review.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_indicator_hypothesis_review
```

Главные PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260514.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_PENDING_ZOOM_20260515.png`.

Следующий шаг: показать пользователю эти PNG, получить ручной verdict по инструментам и pending `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16`. До этого не делать scorer/target-lock/ML/Optuna.

Ассистентский verdict сохранен:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_ASSISTANT_VERDICT_20260701_RU.md`.

Рабочий вывод: простые индикаторы не разделяют good/bad; следующий безопасный шаг - приоритетный zoom-review `T15L06`, `T15L13`, `T15L16`.

## Handoff 2026-07-01 T15 Priority Zoom Review V0

Статус: `T15_PRIORITY_ZOOM_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Добавлен модуль:
`src/mlbotnav/visual_entry_priority_zoom_review.py`.

Главный sheet:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_SHEET_20260515.png`.

Отдельные PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L06_PRIORITY_ZOOM_REVIEW_V0_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L13_PRIORITY_ZOOM_REVIEW_V0_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L16_PRIORITY_ZOOM_REVIEW_V0_20260515.png`.

Ассистентский verdict: `T15L06` и `T15L16` strong/gold-candidate; `T15L13` possible but not primary. Следующий шаг: получить пользовательское подтверждение. Не запускать scorer/target-lock/Optuna/ML.

## Handoff 2026-07-01 T15 User Verdict V0

Статус: `T15_USER_VERDICT_V0_FIXED_NO_ML_NO_OPTUNA` superseded.

Пользователь подтвердил “норм”. Добавлен модуль:
`src/mlbotnav/visual_entry_t15_user_verdict.py`.

Зафиксировано:
`T15L06`, `T15L16` = `gold_candidate_user_confirmed`;
`T15L13` = `possible_not_primary`;
`T15L02`, `T15L07`, `T15L08`, `T15L11` = `weak_not_promoted_after_priority_review`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_20260701.json`.

Этот слой больше не использовать как рабочий: пользователь уточнил, что входов должно быть `7`. Рабочий слой: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

## Handoff 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V2

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V2_FIXED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: `T15L10` тоже крест. Актуальный слой: `user_feedback_v2`.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L10`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

Следующий шаг: показать или разобрать 7 pending; не делать ledger/scorer/ML до явных good/shift решений.

## Handoff 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V1

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V1_FIXED_NO_ML_NO_OPTUNA`.

Пользователь прислал дополнительный full-day screenshot; `T15L21` добавлен в reject. Актуальный слой: `user_feedback_v1`.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

Следующий шаг: показать или разобрать 8 pending; не делать ledger/scorer/ML до явных good/shift решений.

## Handoff 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь прислал три скриншота с красными X. Зафиксирован feedback layer:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_transfer_feedback.py`.
2. `13` candidates помечены `bad_noise / user_crossed_out_not_suitable`.
3. `9` candidates оставлены `pending_user_visual_review`.
4. Исходные screenshots пользователя сохранены в `user_feedback_v0`.
5. Сгенерирован full-day feedback PNG с красными X и cyan pending.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`, `T15L21`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

Следующий шаг: получить точный verdict по pending, особенно по кандидатам со стрелками без X. Не делать ledger/ML/Optuna до явных good/shift решений.

## Handoff 2026-07-01 Low Anchor Transfer Review 2026-05-15 Compact V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_DAY_20260515_READY_NO_ML_NO_OPTUNA`.

По просьбе пользователя создан перенос текущей visual-learning логики с `2026-05-14` на `2026-05-15`.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_transfer_review.py`.
2. Первый широкий проход дал `89` broad low-anchor candidates и `52` после мягкого фильтра, что слишком много.
3. Добавлен compact cluster filter `review_cooldown_minutes=24`.
4. Активный пакет создан в `day_20260515_compact_v0`: `22` кандидата, `2` zoom pages, full-day PNG, JSON, CSV, RU report.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_FULL_DAY_20260515.png`.

Zoom pages:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_01_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_02_20260515.png`.

Следующий шаг: показать пользователю эти PNG и получить verdict по `T15L01..T15L22`. Не создавать ledger и не двигаться к scorer/ML до visual verdict.

## Handoff 2026-07-01 Feature Policy EMA Deferred

Статус: `LOW_ANCHOR_FEATURE_POLICY_EMA_DEFERRED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: EMA пока не трогаем. Не добавлять EMA в рабочие шаблоны, паспорта, scorer-checklist или правила входа.

Дальше активные признаки для шаблонов: структура движения, положение в диапазоне, low/reclaim, объем, диапазон и wick закрытой signal-свечи. EMA-колонки в feature audit считать reference-only.

## Handoff 2026-07-01 Low Anchor No-Lookahead Feature Audit V0

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_READY_NO_ML_NO_OPTUNA`.

Создан no-lookahead feature audit после полного разбора extra auto pool.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_feature_audit.py`.
2. Сравнены группы `manual_gold`, `bad_noise`, `manual_shift_review`, `possible_entry`.
3. Все признаки считаются на закрытой signal-свече и прошлом контексте.
4. Созданы JSON/CSV/RU/PNG артефакты.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.json`.

Следующий шаг: либо zoom-lock `manual_shift_review`, либо draft no-lookahead scorer checklist/passport. Не запускать ML/export/Optuna.

## Handoff 2026-07-01 Low Anchor Extra Auto Feedback Summary

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_COMPLETE_NO_ML_NO_OPTUNA`.

Extra auto pool полностью разобран: `66` кандидатов, `6` страниц.

Итог:

1. `bad_noise`: `51`;
2. `possible_entry`: `3`;
3. `manual_shift_review`: `12`.

Summary JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.json`.

Следующий шаг по рельсам: no-lookahead feature audit. Не строить ML/export. `possible_entry` не gold, `manual_shift_review` не label.

## Handoff 2026-07-01 Low Anchor Extra Auto Page06 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь сказал, что page `06` плохая: входы не по тренду. Все `6` кандидатов page `06` помечены `bad_noise / bad_noise_countertrend_entry`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.json`.

## Handoff 2026-07-01 Low Anchor Extra Auto Page05 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь сказал, что page `05` слабая и плохая; некоторые auto-entry стрелки не совпадают с визуально нужной low/entry-зоной.

Сделано:

1. Все `12` кандидатов page `05` помечены `bad_noise`.
2. Причина: `bad_noise_weak_context_entry_mismatch`.
3. Исходный screenshot пользователя сохранен рядом с артефактами.
4. Новые ручные точки не создавались, потому что это reject, не shift review.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.json`.

Следующий шаг: page `06` visual review. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Page04 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь показал красными X/стрелками, что page `04` надо трактовать не как готовые possible entries, а как current auto-entry not gold with manual shift needed.

Сделано:

1. `src/mlbotnav/visual_entry_low_anchor_extra_feedback.py` расширен меткой `manual_shift_review`.
2. Все `12` кандидатов page `04` помечены `manual_shift_review`.
3. Исходный screenshot пользователя сохранен рядом с артефактами.
4. Времена/цены новых ручных точек не переписывались.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.json`.

Следующий шаг: page `05` visual review или отдельный zoom-review page `04` manual shifts. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Page03 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь дал verdict по page `03`: все слабо. Зафиксировано:

1. Все `12` кандидатов page `03` = `bad_noise`.
2. Причина = `bad_noise_weak_context`.
3. `possible_entry` на page `03` нет.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.json`.

Следующий шаг: page `04` visual review или interim feature audit первых трех страниц. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Page02 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь прислал screenshot с красными рамками на page `02`. Зафиксировано:

1. `LA018`, `LA020`, `LA026` = `possible_entry` / `possible_entry_one_percent_followthrough`.
2. Остальные `9` кандидатов page `02` = `bad_noise` / `bad_noise_shallow_bounce`.
3. `possible_entry` не является gold-входом; это только кандидат для дальнейшего review.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.json`.

Следующий шаг: page `03` visual review или промежуточный feature audit. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Page01 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь подтвердил, что первая страница extra auto review не подходит: входы слишком мелкие, с коротким отскоком, без нужного продолжения и часто без правильного трендового контекста.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_extra_feedback.py`.
2. Создан feedback layer для page `01`.
3. `LA001..LA012` помечены как `bad_noise` / `bad_noise_shallow_bounce` / `reject`.
4. Созданы JSON/CSV/RU/PNG артефакты.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.json`.

Следующий шаг: продолжить page `02` или сформировать no-lookahead feature checklist для отличия `bad_noise_shallow_bounce` от ручных good entries. Optuna/ML/export запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Review V1

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_READY_NO_ML_NO_OPTUNA`.

После resolved label-ledger V1 создан пакет для ручного разбора `66` extra auto candidates. Они не являются negative labels автоматически.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_extra_review.py`.
2. Создан JSON/CSV/RU отчет.
3. Сгенерированы `6` PNG-страниц по `12` кандидатов.
4. На каждом zoom показаны время входа и цена `entry_price_plus_5bps`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.json`.

Страница 01:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_01_20260701.png`.

Следующий шаг: показать пользователю page 01 и получить visual verdict. Разрешенные ручные метки: `bad_noise`, `duplicate`, `possible_entry`, `wrong_type`, `ignore_unclear`. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Label Ledger V1 Resolved

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_BY_USER_NO_ML_NO_OPTUNA`.

Пользователь подтвердил pending review PNG: `норм`. `M05/M14/M15/M16/M17` закрыты как `manual_gold_user_confirmed_auto_near_ok`; `M03/M09/M10/M11` остаются `manual_gold_user_feedback_auto_not_gold`.

Итоговые target labels: `10 exact`, `4 auto near not-gold`, `5 auto near user-confirmed ok`, `0 pending`.

Resolved JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701.json`.

Следующий рабочий шаг по рельсам: не ML, а review `66` extra auto candidates как unlabeled/anti pool или draft event dataset с явным запретом export.

## Handoff 2026-07-01 Low Anchor Label Ledger V0

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_READY_NO_ML_NO_OPTUNA`.

Пользователь подтвердил feedback по `M03/M09/M10/M11`. Создан следующий слой разметки `label_ledger_v0`, чтобы не считать `±3m` gold.

Итог:

1. `manual_gold_exact_auto`: `10`;
2. `manual_gold_user_feedback_auto_not_gold`: `4`;
3. `manual_gold_pending_shift_review`: `5`.

Оставшиеся pending цели: `M05`, `M14`, `M15`, `M16`, `M17`.

Главный PNG для следующего review:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_PENDING_SHIFT_REVIEW_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701.json`.

Следующий шаг: пользователь должен дать решение по пяти pending-панелям. До этого не строить event dataset для ML, scorer, Optuna или export.

## Handoff 2026-07-01 Low Anchor User Feedback M03/M09/M10/M11

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_NO_ML_NO_OPTUNA`.

Пользователь красным отметил `M03/M09/M10/M11` на target-nearest zoom sheet: auto nearest candidate был рядом, но не в той свечке/зоне для рабочего эталона.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_feedback.py`.
2. Создан `user_feedback_v0` с JSON, RU-md, PNG, SVG.
3. Исходный пользовательский screenshot скопирован рядом как provenance.
4. Зафиксировано правило: `hit_within_3m` не является gold; это только near-review.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json`.

Следующий шаг: пользователь смотрит feedback PNG. Если норм, использовать этот feedback как label layer для V1/event dataset. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Entry Suggester V0

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_SEED_DAY_REVIEW_NO_ML_NO_OPTUNA`.

Пользователь решил ускорить ручную разметку: сначала сделать автоматический поиск low-anchor входов, а стратегии/BOS/Fibo/swing/ML подключать позже как объясняющие слои.

Сделано:

1. Добавлен скрипт `src/mlbotnav/visual_entry_low_anchor_suggester.py`.
2. Запущен seed-day пакет на `SOLUSDT 1m 2026-05-14`.
3. V0 выдал `85` кандидатов после фильтра.
4. По `M01..M19`: `10/19` exact hits, `19/19` hits в пределах `±3m`.
5. Созданы JSON, CSV, full-day PNG и target-nearest zoom sheet.

Главные артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_full_day_20260514.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_target_nearest_zoom_20260514.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514_RU.md`.

Следующий шаг: пользовательский visual review zoom sheet. Не уменьшать кандидаты и не обучать ML до verdict, чтобы не потерять хорошие ручные low-входы.

Граница: V0 не является стратегией, production target-lock, Optuna или ML/export.

## Handoff 2026-07-01 Data Scope Monthly Samples

Статус: `SOLUSDT_1M_MONTHLY_FULL_DAY_SAMPLES_CREATED_NO_ML_NO_OPTUNA`.

Пользователь попросил проверить, что 126 дней `SOLUSDT 1m` реально представлены полноценными UTC-днями, и сделать визуальную выгрузку по одному дню на месяц.

Сделано:

1. Проверены sample-дни `2026-01-27`, `2026-02-28`, `2026-03-28`, `2026-04-28`, `2026-05-28`.
2. Каждый sample-день имеет `1440` строк.
3. Первая свеча каждого дня открывается в `00:00:00+00:00`.
4. Последняя свеча каждого дня закрывается в `00:00:00+00:00` следующего дня.
5. Созданы отдельные full-day PNG и общий contact sheet.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701.png`.

Отчет:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701_RU.md`.

Граница: это data-scope/visual audit only. Не запускались scorer, Optuna, ML/export/promotion.

## Handoff 2026-07-01 C01 126 Days Source Audit

Статус: `C01_126_DAYS_SOURCE_AUDIT_COMPLETE_NO_ML_NO_OPTUNA`.

Пользователь усомнился, что `126 дней` были настоящим прогоном, и предположил, что это могло быть только `1m`. Аудит подтвердил: это именно `SOLUSDT 1m only`, не MTF.

Факты:

1. В `data/core/bybit_ohlcv` найдено `126` файлов `dt=*/tf=1m/symbol=SOLUSDT/part-final.csv`.
2. Диапазон: `2026-01-26` .. `2026-05-31`.
3. Все файлы имеют `1440` строк.
4. `C01_MULTI_DAY_CHECK_V1_20260630.json` и daily CSV сходятся: `126` дней, `25` кандидатов, `23` дня с кандидатами, максимум `2` кандидата в день.
5. Недофиксация: исторический C01 multi-day JSON не пишет top-level `symbol`, `timeframe`, `source_csv_pattern`, диапазон дат и точную команду.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_126_DAYS_SOURCE_AUDIT_20260701_RU.md`.

Не продолжать C01 V1 как рабочую стратегию. Это остановленная ветка; Optuna/ML/export/promotion запрещены.

## Handoff 2026-07-01 C02A Seed-Lock

Статус: `C02A_TARGET_LOCK_SEED_V0_CREATED_NO_ML_NO_OPTUNA`.

После пользовательского подтверждения `7.1` создан seed-lock C02A для `M01/M02/M08`. Это защита от регрессии, не production target-lock.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_FULL_DAY_ZOOMS_20260630.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_FULL_DAY_ZOOMS_20260630.svg`.

Следующий шаг: `9.1_MULTI_DAY_BENCH_OR_USER_DECISION_NEXT_PASSPORT_NO_ML_NO_OPTUNA`.

Optuna и ML/export/promotion запрещены.

## Handoff 2026-06-30 C02A Entry-Only Scorer V0

Статус: `C02A_ENTRY_ONLY_SCORER_V0_SEED_DAY_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Выполнен подпункт `7.1_ENTRY_ONLY_SCORER_C02A_SEED_DAY_NO_ML_NO_OPTUNA`: после пользовательского `глянул давай далее` по C02A rules создан seed-day entry-only scorer. Входы: `C02E03/M01`, `C02E04/M02`, `C02E10/M08`; must-hit `3/3`, violations `0`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.svg`.

Следующий шаг строго по рельсам: показать PNG пользователю и получить `норм / фикс` по `7.1_USER_VISUAL_REVIEW_C02A_ENTRY_ONLY_SCORER_V0_BEFORE_TARGET_LOCK`.

Запрещено до этого: target-lock, multi-day, Optuna, ML/export/promotion.

## Handoff 2026-06-30 C02 Good/Bad Audit

Статус: `C02_GOOD_BAD_AUDIT_V0_COMPLETE_NO_ML_NO_OPTUNA`.

Выполнен следующий пункт после ручной разметки: good/bad аудит. Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_EVENT_FEATURES_V0_20260630.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_FULL_DAY_AUDIT_V0_20260630.png`.

Вывод: не строить один широкий C02 scorer. Следующий безопасный шаг: `C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`.

## Handoff 2026-06-30 C02 User Labels Complete

Статус: `C02_CANDIDATE_REVIEW_V0_USER_LABELS_COMPLETE_NO_ML_NO_OPTUNA`.

C02 candidate review завершен на seed-дне. Пользователь сначала отклонил `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`, затем отдельным скрином отметил красными рамками “можно” для `C02E03..C02E12`. Это принято как:

- `GOOD_ENTRY`: `C02E03`, `C02E04`, `C02E05`, `C02E06`, `C02E07`, `C02E08`, `C02E09`, `C02E10`, `C02E11`, `C02E12`;
- `BAD_ENTRY`: `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`.

Обновлены ledger/layer/passport/matrix. Контрольный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_USER_LABELED_GOOD_BAD_SHEET_20260630.png`.

Следующий безопасный шаг: `C02_AUDIT_GOOD_VS_BAD_AND_DECIDE_SCORER_RULES_NO_ML_NO_OPTUNA`. Не запускать scorer, Optuna, ML/export/promotion, target-lock или multi-day, пока не разобраны признаки good/bad.

## Handoff 2026-06-30 Passport Bench Step Plan

Статус: `C02_CANDIDATE_REVIEW_PACK_READY_WAIT_USER_LABELS_NO_ML_NO_OPTUNA`.

По запросу пользователя процесс расписан по пунктам и подпунктам. Выполнены: матрица покрытия `M01..M19`, папка C02, паспорт-драфт `VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0`, seed visual C02. Пользователь подтвердил seed visual словом `норм`. После этого создан C02 candidate layer V0.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_BENCH_V0_STEP_PLAN_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630.json`.

Паспорт-драфт C02:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/passport_VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0_RU.md`.

Candidate layer V0:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_20260630.json`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_full_day_review_20260630.png`.

Zoom review sheet:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_zoom_sheet_C02E01_C02E16_20260630.png`.

Review ledger:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_LEDGER_V0_20260630.json`.

Следующий подпункт: пользовательский review `C02E01..C02E16`. C01 не продолжать как главный путь. Scorer/Optuna/ML/export/promotion запрещены до разметки.

## Handoff 2026-06-30 Fresh Target-Led Passport Bench V0

Статус: `PASSPORT_BENCH_V0_STRUCTURED_NO_ML_NO_OPTUNA`.

Пользователь попросил аудит последних сообщений, подключение агента и проверку всех паспортов. Read-only агент подтвердил: реально применен только один паспорт `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0` под `M05/M06`; C01 остановлен как слабое направление, но остальные типы `M01..M19` не покрыты паспортами.

Главный вывод: не делать общий вывод по системе на основании C01. Следующий рабочий этап — `PASSPORT_BENCH_V0`: матрица покрытия паспортами, затем новый паспорт вне C01, предпочтительно `C02_DEEP_CAPITULATION_LOW` по `M01/M02/M08`.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/process_audit/PASSPORT_BENCH_STAGE_AUDIT_20260630_RU.md`.

Граница: Optuna/ML/export/promotion запрещены. Старые V7/V8/V9/V10/V11 не продолжать как очередь задач.

## Handoff 2026-06-30 Fresh Target-Led C01 Multi-Day Check V1

Статус: `C01_MULTI_DAY_CHECK_V1_RAW_NEEDS_VISUAL_TUNING_NO_ML`.

Рабочий пункт по рельсам: `C01_ENTRY_ONLY_SCORER_V0` для паспорта `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0`.

Сделано: пользователь подтвердил скрин `M05` после сдвига на одну свечу вправо. Актуальная `M05`: signal `10:43 UTC` -> entry `10:44 UTC`, entry open `90.66000000`, entry + `5 bps` = `90.70533000`. `M06` без изменений: signal `12:00 UTC` -> entry `12:01 UTC`.

Старый scorer V0 помечен как stale. Пересчитан `C01_ENTRY_ONLY_SCORER_V1`: на `SOLUSDT 1m 2026-05-14` пойманы `M05/M06`, ложных кандидатов `0`, `M12` не сработала. Пользователь дал `далее поехали по рельсам`, принято как визуальное подтверждение V1.

Создан seed target-lock: `M05/M06` защищены от потери или сдвига без отдельного решения пользователя.

Затем собран контракт входных данных и сделан raw multi-day check V1 без донастройки: 126 дней, 25 кандидатов, максимум 2 в день. Частота нормальная, но визуальное качество смешанное; до сделки нужен ручной quality-filter V2.

Артефакты:
1. PNG V1: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_full_day_M05_M06_zoom_20260630.png`.
2. JSON V1: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_20260630.json`.
3. Аудит V1: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_AUDIT_20260630_RU.md`.
4. Lock-ledger: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_20260630_RU.md`.
5. Lock PNG: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_full_day_M05_M06_20260630.png`.
6. Entry contract: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_ENTRY_INPUT_CONTRACT_V1_20260630_RU.md`.
7. Multi-day audit: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_MULTI_DAY_CHECK_V1_AUDIT_20260630_RU.md`.
8. Zoom contact: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_MULTI_DAY_CHECK_V1_all_candidates_zoom_contact_20260630.png`.

Следующий шаг: показать zoom contact sheet пользователю и руками пометить кандидаты `годится / не годится / отдельный тип`, затем сделать `C01_QUALITY_FILTER_V2`. Optuna/ML/export/promotion запрещены.

## Visual Entry TARGET_LOCKED_STRATEGY_TZ 2026-06-29

Статус: `TARGET_LOCKED_STRATEGY_TZ_READY_NO_ML`.

Полный аудит и ТЗ: `reports/final_review/visual_entry_v3/target_locked_strategy_tz/visual_entry_target_locked_strategy_audit_and_tz_20260629_RU.md`.

Активное ТЗ: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_TARGET_LOCK_TZ_RU.md`.

Решение: следующие версии visual-entry должны идти через `target_lock_ledger`. Хорошие попадания V9/V10 нельзя терять молча. Нужна библиотека разных стратегий, а не одна стратегия на все входы.

Следующий шаг:
1. создать `src/mlbotnav/visual_entry_target_lock_ledger.py`;
2. создать lock-файл по `2026-05-13` и `2026-05-14`;
3. затем делать `V11_RECOVER_RANKED_MISSES`;
4. каждый подрежим проверять отдельным PNG;
5. ML export запрещен.

## Visual Entry EVENT_RANKED_BRICKS_V10 2026-06-29

Статус: `EVENT_RANKED_BRICKS_V10_CLEANER_BUT_PARTIAL_NO_ML`.

Добавлены:
1. `src/mlbotnav/visual_entry_event_ranked_bricks_v10_runner.py`
2. `tests/test_visual_entry_event_ranked_bricks_v10_runner.py`

Главный аудит: `reports/final_review/visual_entry_v3/event_ranked_bricks_v10/visual_entry_event_ranked_bricks_v10_audit_20260629T182810Z_RU.md`.

V10 делает cluster-rank поверх V9: один лучший сигнал внутри `low_event_start_idx:event_low_idx`, без cooldown `30/45/60/90` и без будущего.

Validation `2026-05-13`: `V10_01_HOT_CHAIN_EVENT_LOW_RANKED` = `1/9`, `0` false, пойман `08:48`.

Holdout `2026-05-14`: `V10_03_WARM_EVENT_RANKED` = `3/17`, `6` false; `V10_02_HOT_FIRST_EVENT_RANKED` = `2/17`, `7` false; `V10_04_DEEP_TERMINAL_EVENT_RANKED` = `3/17`, `20` false; ranked union = `7/17`, `33` false.

PNG для просмотра:
1. `reports/final_review/visual_entry_v3/event_ranked_bricks_v10_validation/visual_entry_family_overlay_2026-05-13_v10_01_hot_chain_ranked_20260629T182730Z.png`
2. `reports/final_review/visual_entry_v3/event_ranked_bricks_v10_holdout/visual_entry_family_overlay_2026-05-14_v10_02_warm_ranked_20260629T182734Z.png`
3. `reports/final_review/visual_entry_v3/event_ranked_bricks_v10_holdout/visual_entry_family_overlay_2026-05-14_v10_03_hot_first_ranked_20260629T182738Z.png`
4. `reports/final_review/visual_entry_v3/event_ranked_bricks_v10_holdout/visual_entry_family_overlay_2026-05-14_v10_04_deep_ranked_20260629T182741Z.png`

Решение: V10 чище V9, но не готов. В ML ничего не передавать. Следующий шаг: `V11_RECOVER_RANKED_MISSES` - вернуть потерянные `10:48/20:49` warm, `15:19/18:50` hot-first, `03:25` deep отдельными подрежимами.

## Visual Entry BRICK_BY_BRICK_SELECTOR_V9 2026-06-29

Статус: `BRICK_BY_BRICK_SELECTOR_V9_PARTIAL_DIAGNOSTIC_NO_ML`.

Добавлены:
1. `src/mlbotnav/visual_entry_brick_by_brick_selector_v9_runner.py`
2. `tests/test_visual_entry_brick_by_brick_selector_v9_runner.py`

Главный аудит: `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9/visual_entry_brick_by_brick_selector_v9_audit_20260629T180726Z_RU.md`.

Validation `2026-05-13`: `V9_01_HOT_CHAIN_EVENT_LOW_BRICK` = `1/9`, `0` false, пойман `08:48`. Это чистый, но очень узкий кирпич.

Holdout `2026-05-14`: `V9_03_WARM_STRUCTURAL_RECLAIM_BRICK` = `5/17`, `16` false; `V9_02_HOT_FIRST_STRONG_RECLAIM_BRICK` = `4/17`, `20` false; `V9_04_DEEP_TERMINAL_RECLAIM_BRICK` = `4/17`, `33` false.

PNG для просмотра:
1. `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9_validation/visual_entry_family_overlay_2026-05-13_v9_01_hot_chain_event_low_20260629T180636Z.png`
2. `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9_holdout/visual_entry_family_overlay_2026-05-14_v9_01_warm_structural_20260629T180637Z.png`
3. `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9_holdout/visual_entry_family_overlay_2026-05-14_v9_03_hot_first_strong_20260629T180644Z.png`
4. `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9_holdout/visual_entry_family_overlay_2026-05-14_v9_04_deep_terminal_20260629T180647Z.png`

Решение: `V9_90_RESEARCH_UNION_ALL_BRICKS_DIAG` не использовать как стратегию: `12/17`, но `68` false на holdout. В ML ничего не передавать. Следующий исполнитель должен делать `V10_EVENT_RANKED_BRICKS`: выбирать один лучший сигнал внутри low-event и отдельно дорабатывать `warm`, `hot-first`, `deep`.

## Visual Entry manual bottoms 13/14 2026-06-25
Статус: `MANUAL_BOTTOMS_EXTRACTED_AUTO_KNIFE_SUGGESTED_CP06_EMPTY_NO_ML`.

Создан инструмент `src/mlbotnav/visual_entry_marked_png_to_manual_entries.py` и тест `tests/test_visual_entry_marked_png_to_manual_entries.py`.

Новые ручные разметки:
1. `reports/manual_entries/SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms/manual_entries.json` - `9` входов.
2. `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms/manual_entries.json` - `17` входов.

Контрольные PNG:
1. `reports/manual_entries/SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms/visual_entry_manual_auto_overlay_2026-05-13_20260625T155345Z.png`.
2. `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms/visual_entry_manual_auto_overlay_2026-05-14_20260625T155345Z.png`.

Сводный аудит: `reports/final_review/visual_entry_v3/marked_validation_holdout_user_bottoms/visual_entry_marked_validation_holdout_audit_20260625_RU.md`.

Важно: `S# -> E#` = пользовательские цели, `AK#` = авто-подсказки по сильным провалам, не ML labels. CP06 без подкрутки на 13/14 дал `best=[]`, `rendered=[]`. Следующий исполнитель должен строить новый `REVERSAL_BOTTOM_KNIFE_DROP_V0`, а не передавать CP06/AK в ML.

Проверки закрыты: `py_compile PASS`; visual-entry focused tests `6/6 OK`; `text_guard PASS` `reports/qa_gate/recovery_r5_text_guard_20260625T155616Z.json`; хвостов `python.exe` нет.

## Visual Entry CP06 validation/holdout readiness 2026-06-25
Статус: `NEEDS_MANUAL_LABELS_NO_VALIDATION_RUN`.

CP06 на DEV `2026-05-12` закрыт: `11/11`, `28` false, `39` entries. Следующий честный шаг - не подкручивать параметры, а получить ручную разметку `2026-05-13` и `2026-05-14`.

Аудит: `reports/final_review/visual_entry_v3/cp06_validation_holdout_readiness/cp06_validation_holdout_readiness_20260625_RU.md`.

Для `2026-05-13` и `2026-05-14` есть seed PNG/JSON, но нет `manual_entries.json` с `target_entry_time_utc`. Два агента независимо подтвердили `NEEDS_MANUAL_LABELS`.

Следующий исполнитель должен сначала создать/получить manual-разметку:
1. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.png`;
2. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.png`.

После этого CP06 запускать на validation/holdout без изменения параметров. В ML ничего не передавать.

## Visual Entry v3 DEEP_CAPITULATION_RECLAIM 2026-06-25
Статус: `DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML`.

Добавлены `src/mlbotnav/visual_entry_deep_capitulation_reclaim_runner.py` и `tests/test_visual_entry_deep_capitulation_reclaim_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_20260512_DEV.json` и `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_20260512_DEV_RU.md`.

Лучший рабочий ensemble `DQ01_EQ01_PLUS_DEEP_RECLAIM`: `10/11`, `73` false, пропуск только `08:26`.

High-recall `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP`: `11/11`, но `95` false. Это diagnostic-only, не ML.

Новые одиночные кирпичи: `D01` ловит `12:33`, `D02` ловит `15:26`, `D03` ловит `17:00` без false на DEV-дне.

Следующий строгий шаг: `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY` - подавить ложные входы, добавить приоритет последней/лучшей свечи в кластере и отдельно решить риск `08:26` no-wick. В ML ничего не передавать.

## Visual Entry v3 EARLY_FLUSH_REVERSAL 2026-06-25
Статус: `DEV_EARLY_FLUSH_REVERSAL_DIAGNOSTIC_NO_ML`.

Добавлены `src/mlbotnav/visual_entry_early_flush_runner.py` и `tests/test_visual_entry_early_flush_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_20260512_DEV.json` и `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_20260512_DEV_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_family_overlay_2026-05-12_early_flush_01_eq01_q09_severe_soft45_20260625T134923Z.png`.

Итог: `EQ01_Q09_SEVERE_SOFT45` дал `7/11` hits и `68` false. `EQ03_Q09_SEVERE_SOFT45_NOWICK` дал `8/11`, но `90` false. `E01_SEVERE_FLUSH_LOCKOUT20` поймал `01:42` при `2` false. Это полезная DEV-диагностика, но не ML-кандидат.

Следующий шаг: строить `DEEP_CAPITULATION_RECLAIM` для пропусков `12:33`, `15:26`, `17:00`; после каждого visual-test обязательно PNG overlay и контроль живых `python.exe`.

## Visual Entry v3 quality filter diagnostic 2026-06-25
Статус: `DEV_QUALITY_FILTER_DIAGNOSTIC_NO_ML`.

Добавлены `src/mlbotnav/visual_entry_quality_filter_runner.py` и `tests/test_visual_entry_quality_filter_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_20260512_DEV.json` и `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_20260512_DEV_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_family_overlay_2026-05-12_quality_01_q09_ensemble_q07_q01_20260625T132748Z.png`.

Итог: лучший ensemble `Q09_ENSEMBLE_Q07_Q01` дал `4/11` попаданий и `53` ложных входа. Это лучше micro-bottom (`4/11`, `135` false), но все еще не кандидат. В ML ничего не передавать.

Следующий шаг: строить две отдельные подсемьи для пропусков: `EARLY_FLUSH_REVERSAL` и `DEEP_CAPITULATION_RECLAIM`.

## Visual Entry v3 micro-bottom diagnostic 2026-06-25
Статус: `DEV_MICRO_BOTTOM_SIGNATURE_DIAGNOSTIC_NO_ML`.

Добавлен runner `src/mlbotnav/visual_entry_micro_bottom_signature_runner.py`; аудит: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_20260512_DEV.json` и `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_20260512_DEV_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_family_overlay_2026-05-12_micro_bottom_01_20260625T130512Z.png`.

Итог: micro-bottom слой дал `4/11` попаданий, но `135` ложных входов из `139`; это подтверждает форму дна, но не является кандидатом. В ML ничего не передавать. Следующий шаг - слой подавления ложных входов: `anti_drift_down`, `reclaim_quality`, `support_confluence`, `capitulation_absorption`, `bottom_event_clustering`.
## Visual Entry v3 passport-family diagnostic 2026-06-25
Статус: `DEV_PASSPORT_FAMILY_DIAGNOSTIC_DONE_NO_ML`.

Добавлены:
1. `src/mlbotnav/visual_entry_passport_family_runner.py`;
2. `tests/test_visual_entry_passport_family_runner.py`;
3. `render_family_candidate_overlay()` в `src/mlbotnav/render_visual_entry_overlay.py`.

Аудит: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_runner_20260512_DEV.json` и `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_runner_20260512_DEV_RU.md`.

Свежий top PNG: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_family_overlay_2026-05-12_family_01_deep_capitulation_next_open_20260625T125241Z.png`.

Итог: лучший паспортный family-layer дал только `1/11` попаданий и `20` ложных входов. Это не кандидат, в ML ничего не передавать. Следующий шаг - отдельный `VISUAL_MICRO_BOTTOM_SIGNATURE_V0`, потому что широкая feature-проверка показывает: ручные точки похожи на micro-bottom, но текущие паспорта не отделяют их от сотен похожих локальных минимумов.

## Visual Entry v3 user-entry arrows 2026-06-25
Статус: `DEV_V3_ENTRY_ARROWS_READY_NO_CANDIDATE_NO_ML`.

Актуальная логика: сигнал = закрытая свеча дна/фитиля, вход LONG = `open` следующей свечи, slippage `5 bps`. Актуальная разметка: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows/manual_entries.json`. Контрольный PNG: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows/visual_entry_combo_simple_arrows_manual_v3_targets_20260625T112336Z.png`.

Стратегический аудит: `reports/final_review/visual_entry_v3/visual_entry_v3_strategy_audit_20260625_RU.md`. Добавлен runner `src/mlbotnav/visual_entry_no_lookahead_candidates.py`; rerun: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`.

Вывод: solo-паспорта и старый lookahead combo не кандидаты; лучший честный no-lookahead exact пока `3/11` и `34` false. В ML ничего не передавать. Следующий шаг - визуально подтвердить v3 точки и дальше строить структурные подсемьи с support/CHOCH/divergence/volume-profile фильтрами.

## Visual Entry Calibration DEV-12 2026-06-25
Статус: `dev_day_manual_entries_ready_scorer_ready`.

DEV-разметка: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries.json`.

Аудит разметки: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries_audit_20260512_DEV_RU.md`.

Оверлей: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries_SOLUSDT_1m_2026-05-12_DEV_detected_overlay.png`.

Времена ручных LONG-целей на `2026-05-12`: `01:44`, `04:15`, `09:12`, `12:36`, `15:34`, `17:05` UTC. `2026-05-12` используется как DEV-день; `2026-05-13` и `2026-05-14` пока не использовать для подбора параметров.

Добавлен `src/mlbotnav/visual_entry_score.py` и тест `tests/test_visual_entry_score.py`.

Первый scorer на старом B001 CSV: `reports/qa_gate/visual_entry_score_SOLUSDT_1m_visual_dev_20260625_20260512_v1_oos_backtest_trades_SOLUSDT_1m_2026-05-12_long_only_20260625T073603Z.json`.

Итог B001: `3/6` попаданий, `15` лишних входов из `18`, `precision=0.16666666666666666`, `recall=0.5`, `f1_visual=0.25`, `net_return_pct=-62.229358575198916`, статус `VISUAL_HITS_WITH_TOO_MANY_FALSE_ENTRIES`. В ML ничего не передавать.

Следующий шаг: использовать scorer как линейку для solo-passport / block / combo diagnostic; для ранних входов у дна проектировать reversal/dip-buy family, а не раздушивать B001 momentum до шума.

## Visual Entry feature/pre-filter diagnostic 2026-06-25
Статус: `dev_diagnostic_done_next_solo_scorer_and_reversal_family`.

Артефакты:
1. `reports/qa_gate/visual_entry_feature_audit_20260512_DEV.json`;
2. `reports/qa_gate/visual_entry_prefilter_search_20260512_DEV.json`;
3. `reports/qa_gate/visual_entry_candidate_family_plan_20260512_DEV_RU.md`.

Добавлены:
1. `src/mlbotnav/visual_entry_feature_audit.py`;
2. `src/mlbotnav/visual_entry_prefilter_search.py`;
3. тесты `tests/test_visual_entry_feature_audit.py`, `tests/test_visual_entry_prefilter_search.py`.

Вывод: простой reversal-prefilter слишком шумный и не является кандидатом. Нужны solo visual scorer по выбранным существующим паспортам и отдельная `REVERSAL_DIP_BUY_LONG v0` с trigger/suppression/backtest.

## Visual Entry overlay rule 2026-06-25
Статус: `visual_overlay_required_for_each_test`.

Добавлен `src/mlbotnav/render_visual_entry_overlay.py` и тест `tests/test_render_visual_entry_overlay.py`.

Для каждого следующего visual-test показывать PNG overlay. Текущие примеры:
1. `reports/final_review/visual_entry_overlay_2026-05-12_b001_fixed_dev12_20260625T095333Z.png`;
2. `reports/final_review/visual_entry_overlay_2026-05-12_prefilter_top1_dev12_20260625T095333Z.png`.

Перед финальным ответом проверять, что не осталось `python.exe` процессов от `MLbotNav/mlbotnav/APTuna/visual_entry/optuna`.

## Visual Entry solo passport runner 2026-06-25
Статус: `dev_solo_passport_diagnostic_done_no_ml`.

Добавлен `src/mlbotnav/visual_entry_solo_passport_runner.py` и тест `tests/test_visual_entry_solo_passport_runner.py`.

Отчеты:
1. `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV.json`;
2. `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV_RU.md`.

Top overlays:
1. `reports/final_review/visual_entry_overlay_2026-05-12_solo_01_f009_emagap_down_20260625T100953Z.png`;
2. `reports/final_review/visual_entry_overlay_2026-05-12_solo_02_f059_engulfbull_20260625T100955Z.png`;
3. `reports/final_review/visual_entry_overlay_2026-05-12_solo_03_f010_emaslope_down_20260625T100957Z.png`;
4. `reports/final_review/visual_entry_overlay_2026-05-12_solo_04_f035_supportdist_20260625T100959Z.png`;
5. `reports/final_review/visual_entry_overlay_2026-05-12_solo_05_f017_f018_stoch14_20260625T101002Z.png`;
6. `reports/final_review/visual_entry_overlay_2026-05-12_solo_06_f038_rangepose_20260625T101004Z.png`.

Лучшие solo-сигналы: `F009_EMAGAP_DOWN` дал `2/6` попаданий и `6` ложных; `F059_ENGULFBULL` дал `1/6` и `0` ложных; `F010_EMASLOPE_DOWN` дал `2/6`, но `16` ложных. Это не кандидаты и не ML-вход. Следующий шаг: собрать combo `REVERSAL_DIP_BUY_LONG v0`, где `F009`/EMA-down дают контекст, а `F059`/свечной reversal и дополнительные suppression-фильтры режут шум.

## Visual Entry Calibration TZ 2026-06-25
Статус: `design_ready_waiting_for_markup`.

ТЗ: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_CALIBRATION_TZ_RU.md`.

Суть: контур ручной визуальной разметки теперь оформлен как отдельная ветка. Порядок: `manual_entries.json` -> `visual_entry_score` -> solo-passport sweep -> block sweep -> combo sweep -> validation/holdout -> ручной `APPROVED_FOR_ML`.

Критичный контроль: любые картинки, backtest/Optuna и будущий ML должны сверяться по `source_csv_sha256` core-свечей. Несовпадение дает `DATA_PARITY_FAIL`.

Следующий шаг после пользовательских стрелок: восстановить `target_entry_time_utc`, создать `manual_entries.json` и первый scorer-аудит.

## Visual Entry Calibration seed screenshots 2026-06-25
Статус: `manual_markup_seed_images_ready`.

Папка: `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625`.

Manifest: `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_manifest.json`.

Сгенерированы три дневных PNG из `data_layer=core` для ручной разметки:
1. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-12_CORE.png`;
2. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.png`;
3. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.png`.

Каждый день имеет `1440` core-свечей и SHA256 исходного `part-final.csv` в per-day JSON. Следующий шаг после пользовательской разметки: создать ТЗ/контракт `manual_entries.json`, scorer попаданий `target_hits/missed_targets/false_entries/precision/recall/entry_lag_bars`, затем паспортный sweep.

## B001 marked-entry fixed backtest 2026-06-25
Статус: `done / diagnostic_only_no_promotion`.

Аудит: `reports/qa_gate/b001_marked_entry_fixed_backtest_audit_20260625T073900Z_RU.md`.

Фиксированная матрица: `reports/qa_gate/b001_marked_entry_fixed_long_20260625T071500Z/B001_F001_F005_MARKED_ENTRY_FIXED_long_3OF5.yaml`.

Параметры: `B001_family_move=1`, `entry_action_min_confirmations=3`, `F001_thr_pct=0.02`, `F002_thr_pct=0.04`, `F003_thr_pct=0.10`, `F004_thr_pct=0.95`, `F005_thr_pct=0.35`.

Результат с `min_expected_move_pct=0.001`: `18` сделок, OOS `-47.05387771496912%`; точные попадания в `09:25` и `12:36`, не кандидат.

Результат с `min_expected_move_pct=0.0`: `30` сделок, OOS `-67.41968770852606%`; шум увеличился, качество ухудшилось.

Причина непопадания `17:15`: на сигнальной свече `17:14` F-гейт дает `4/5`, но `prob_up=0.3748`, ниже `p_enter_long=0.60`. `08:15` имеет probability, но F-гейт `0/5`; `15:48` F-гейт `1/5`. Для входов у дна нужна отдельная reversal/dip-buy family. В ML ничего не передавать.

## B001 marked-entry screenshot audit 2026-06-25
Статус: `done / diagnostic_only`.

Аудит: `reports/qa_gate/b001_marked_entry_screenshot_audit_20260625T070500Z_RU.md`.

Пользователь отметил желаемые LONG-входы на скриншоте. Восстановленные времена: `01:42`, `07:02`, `08:15`, `09:25`, `12:36`, `15:48`, `17:15` UTC. Проверка показала: `09:25`, `12:36`, `17:15` можно поймать текущей B001 `RET_N LONG` family при более мягких `F001/F002/F003`; остальные точки требуют не momentum-family, а отдельную reversal/dip-buy family. ML не трогать.

## Shared-study profile-edge coverage fix 2026-06-25
Статус: `fixed / confirmed_by_runtime_smoke`.

Аудит: `reports/qa_gate/shared_study_profile_edge_coverage_fix_20260625T063700Z_RU.md`.

Найдена причина неполного profile edge coverage на shared-study process-pool: профильный forcing использовал `run_trial_index + profile_edge_worker_offset`, из-за чего `w2/w3` могли сразу уходить за первые две min/max фазы. Core forcing использовал локальный индекс и поэтому закрывался стабильнее.

Фикс: `src/mlbotnav/optuna_search_candidate.py` теперь расходует profile edge slots только при фактическом profile sampling и распределяет min/max edge-задачи между process workers. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` передает `--process-workers-total`, `adaptive_auto_train.py` пробрасывает его в Optuna search. `profile_edge_worker_offset` оставлен в отчетах как диагностика.

Проверки: `py_compile` PASS, `PSParser` PASS, `tests.test_optuna_search_runtime` PASS `73/73 OK`, `text_guard` PASS `reports/qa_gate/recovery_r5_text_guard_20260625T065332Z.json`.

Контрольный smoke `b001_3of5_long_shared_edgefix3_20260625_115056`: final worker snapshot `w3` terminal `42/42`, core `5/5 PASS`, profile `7/7 PASS`, forced profile min/max полный `7/7`. Сам результат OOS `0`, сделок `0`, не кандидат. ML не трогать.

## B001 family-unified 4/5 LONG shared-study repeat 2026-06-24
Статус: `done / tradeful_negative_no_promotion_with_edge_coverage_warn`.

Аудит: `reports/qa_gate/b001_family_unified_4of5_long_shared_repeat_audit_20260624T195100Z_RU.md`.

Пользовательский повтор `4/5 LONG` на shared-study `3x3/9`: launcher `OK`, storage `postgresql`, `w1/w2/w3 exit_code=0`, best worker `w3`, OOS `-5.4889095203104477`, сделок `1`, train gate `false`. Это отрицательный diagnostic, не кандидат. В ML ничего не передавалось.

Coverage warning: core edge coverage `5/5 PASS`, profile edge coverage `2/7 PASS`; failed profiles: `F001_thr_pct`, `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`, `F005_thr_pct`.

## B001 family-unified 3/5 LONG shared-study 2026-06-24
Статус: `done / tradeful_negative_no_promotion_with_edge_coverage_warn`.

Аудит: `reports/qa_gate/b001_family_unified_3of5_long_shared_audit_20260624T195200Z_RU.md`.

Запуск: `3x3/9`, `SharedOptunaStudy`, `SharedStudyId=b001_3of5_long_shared_20260625T005102`, matrix `reports/qa_gate/b001_family_unified_long_3of5_shared_20260625T005102/B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml`.

Итог: launcher `OK`, storage `postgresql`, `w1/w2/w3 exit_code=0`, best worker `w3`, OOS `-2.0302055441506761`, сделок `1`, train gate `false`. Это отрицательный diagnostic, не кандидат. В ML ничего не передавалось.

Важное предупреждение: core edge coverage `5/5 PASS`, но profile edge coverage `4/7 PASS`; failed profiles: `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`. Этот прогон годится как runtime diagnostic, но не как чистый proof полного profile-edge coverage.

Следующий безопасный шаг: если продолжаем B001 diagnostic, либо сначала закрыть вопрос profile-edge coverage на shared-study бюджете `42`, либо отдельно прогнать `3/5 SHORT` как diagnostic-only с явным coverage warning. К large 2н/1н по этой ветке не переходить без неотрицательного tradeful результата и понятного coverage-аудита.

## Optuna shared-study process-pool 2026-06-24
Статус: `done / infra_closed_no_promotion`.

Аудит: `reports/qa_gate/optuna_shared_study_process_pool_audit_20260624T190435Z_RU.md`.

Сделано: собран режим `3x3/9` с одной общей Optuna study. Это не старый `1x9/9` и не три полностью независимых поиска. Теперь `w1/w2/w3` остаются отдельными Python-процессами, но получают один `--optuna-shared-study-id`.

Измененные файлы:
1. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`;
2. `APTuna/run_block_family_selection.ps1`;
3. `src/mlbotnav/adaptive_auto_train.py`;
4. `src/mlbotnav/optuna_search_candidate.py`;
5. `tests/test_optuna_search_runtime.py`.

Проверки:
1. `py_compile` PASS;
2. PowerShell parser PASS;
3. `tests.test_optuna_search_runtime` PASS, `71/71 OK`;
4. dry-run PASS;
5. runtime smoke PASS по инфраструктуре.

Финальный smoke: `reports/logs/b001_4of5_long_shared_fix_launcher_20260624T185929Z.log`.

Итог smoke B001 `4/5 LONG`: launcher `OK`, shared-study включен, best worker `w2`, OOS `-10.009351008800071`, сделок `2`. Это отрицательный diagnostic, не кандидат. В ML ничего не передавалось.

Как запускать следующий shared-study diagnostic:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath <matrix> -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId <RUN_ID> -UseTemporaryUnlock
```

Граница: shared-study требует `postgresql` или другой не-`sqlite` storage. Если preflight видит `sqlite`, запуск должен остановиться.

## Optuna single-worker профиль 1x9/9 2026-06-24
Статус: `OPTUNA_SINGLE_WORKER_1X9_9_READY`.

Сделано: `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` теперь допускает `ProcessWorkers=1`, а `APTuna/run_optuna_1d1d_stagec.ps1` не поднимает такой запуск до `2`.

Проверка dry-run подтвердила: один `w1`, `Threads/proc=9`, `Search/proc=9`, `Trials/proc=42`.

Использовать для family-unified B001, когда нужна одна общая Optuna-история вместо трех отдельных worker.

## B001 family unified 5/5 2026-06-24
Статус: `B001_FAMILY_UNIFIED_5OF5_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_unified_5of5_audit_20260624T154700Z_RU.md`.

Сделано: добавлен режим "одно семейное звено" для B001. Новая ручка `B001_family_move` задает общее направление для всех `F001..F005`; независимые `F001_move..F005_move` в unified-матрицах не используются. Пороги `F001_thr_pct..F005_thr_pct` калибруются вместе.

Матрицы:
1. LONG: `reports/qa_gate/b001_family_unified_long_20260624Tmanual/B001_F001_F005_FAMILY_UNIFIED_long_5OF5.yaml`.
2. SHORT: `reports/qa_gate/b001_family_unified_short_20260624Tmanual/B001_F001_F005_FAMILY_UNIFIED_short_5OF5.yaml`.

Smoke strict `5/5`: LONG `0` сделок, SHORT `0` сделок, везде `EMPTY_ACTION_GATE`. В ML ничего не передавалось. Следующий диагностический шаг, если продолжать эту ветку: unified `4/5`, затем `3/5`.

## B001 family strict 5/5 smoke 2026-06-24
Статус: `B001_FAMILY_STRICT_5OF5_SMOKE_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_strict_5of5_smoke_audit_20260624T153100Z_RU.md`.

Проверено правило пользователя: `B001_ALLOW = F001 AND F002 AND F003 AND F004 AND F005` на одной сигнальной свече, вход на следующей свече. Матрица: `reports/qa_gate/b001_family_strict_5of5_20260624T152830Z/B001_F001_F005_STRICT_5OF5.yaml`.

Результат smoke 1д/1д: LONG `0` сделок, SHORT `0` сделок, везде `EMPTY_ACTION_GATE`. Runtime подтвердил `entry_action_min_confirmations=5`, policy `and_all`. В ML ничего не передавалось.

Вывод: strict `5/5` технически работает, но на этом окне полностью душит входы. Если продолжать diagnostic ветку, проверять `4/5`, затем `3/5` сверху вниз; основной маршрут `B003.1` не меняется.

## B001_COMBO_DIAG визуальный аудит входов 2026-06-24
Статус: `B001_COMBO_DIAG_GATE_VISUAL_AUDIT_DONE`.

Добавлен инструмент `src/mlbotnav/render_gate_diagnostic.py`, который рисует полный сырой день и слои runtime: `after mode`, `after F-gate`, `after min_move`, реальные входы и выходы.

Артефакты:
1. LONG: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.png`, summary `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.json`.
2. SHORT: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.png`, summary `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.json`.

Вывод: день полный (`1440` свечей). LONG сжимается на `F-gate`: `621 -> 4 -> 4 -> 4`. SHORT сжимается на `min_expected_move_pct=0.001`: `637 -> 240 -> 2 -> 2`. Это диагностическая ветка; ML не тронут.

## B001_COMBO_DIAG N-of-M smoke 2026-06-24
Статус: `B001_COMBO_DIAG_N_OF_M_SMOKE_DONE_NO_CANDIDATE`.

Аудит: `reports/qa_gate/b001_combo_diag_n_of_m_audit_20260624T125500Z_RU.md`.

Сделано:
1. Добавлен диагностический режим `N из M` для `B001_RET_N_TOURNAMENT` через `entry_action_min_confirmations`.
2. Полная combo-матрица `F001..F005` smoke 1д/1д LONG дала OOS `-8.498538882812346%`, `4` сделки, `N=1`.
3. SHORT tradeful worker дал OOS `-6.055628696458093%`, `2` сделки, `N=1`.
4. Результат отрицательный, поэтому это не кандидат и не `block_winner`.
5. В ML ничего не передавалось.

Важное правило: старый `AND`-турнир B001 не запускать как правильный ответ на текущую гипотезу. Для диагностики использовать `N_OF_M`; основной маршрут `B003.1` не меняется.

## B002.3 итог блока закрыт 2026-06-24
Статус: `B002_3_BLOCK_SUMMARY_CLOSED_NEXT_B003`.

Итоговый отчет: `reports/qa_gate/b002_block_summary_b002_3_20260624T100800Z_RU.md`.

Решение по `B002`: LONG `NO_BLOCK_WINNER` (`EMPTY_ACTION_GATE`), SHORT `NO_BLOCK_WINNER` (`MIN_MOVE_UNREACHABLE`); один SHORT worker нашел 1 OOS-сделку, но результат был отрицательный `-7.690052872230013%`. В ML ничего не передавалось.

Следующий блок: `B003`, одиночный паспорт `F007 / F007_RSTD20_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F007_rolling_std20_1m_entry_filter.yaml`.

Активный worker-профиль сохраняется: `3x3/9` (`Threads=9`, `SearchWorkers=9`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`).

Следующий строгий шаг: `B003.1 large LONG 2н/1н`, затем `B003.2 large SHORT 2н/1н`. В ML ничего не передавать.

## B001.6 итог блока закрыт 2026-06-24
Статус: `B001_6_BLOCK_SUMMARY_CLOSED_NEXT_B002`.

Итоговый отчет: `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.

Решение по `B001`: LONG фиксируется как ручной положительный кандидат `F001 / F001_RET1_ALLOW`, OOS `+0.7322559143841945`, сделок `1`; SHORT закрыт как `NO_BLOCK_WINNER`, OOS сделок `0`. В ML ничего не передавалось.

Следующий блок: `B002`, одиночный паспорт `F006 / F006_HLSPREAD_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F006_hl_spread_1m_entry_filter.yaml`.

Активный worker-профиль для следующих запусков: `3x3/9` (`Threads=9`, `SearchWorkers=9`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`). Откат на `2x3/6` только при устойчивой перегрузке CPU/памяти или падении workers, с записью причины в аудите.

Следующий строгий шаг: `B002.1 large LONG 2н/1н`, затем `B002.2 large SHORT 2н/1н`. В ML ничего не передавать.

## B001.5 large SHORT закрыт 2026-06-24
Статус: `B001_5_LARGE_SHORT_CLOSED_NO_BLOCK_WINNER`.

Аудит: `reports/qa_gate/b001_large_short_b001_5_audit_20260624T094057Z_RU.md`.

Финальный отчет: `reports/qa_gate/block_family_selection_B001_short_only_20260624T091433Z.json`.

Результат: `block_winner=null`; лучший доступный fallback `F004 / F004_RET12_ALLOW`, OOS `0.0`, сделок `0`, runtime `EMPTY_ACTION_GATE`.

Разбор по OOS: все `F001..F005` имеют `0` сделок. `F001..F003` остановились на `MIN_MOVE_UNREACHABLE`, `F004..F005` на `EMPTY_ACTION_GATE`. Входов/выходов в OOS нет; train-сделки есть только у `F002` и `F003`, обе ветки отрицательные суммарно.

Фикс после B001.5: `APTuna/run_block_family_selection.ps1` больше не печатает полный JSON в терминал по умолчанию. Теперь выводится краткая таблица по F-ID и, если сделки есть, строки `вход -> выход -> profit`. Полный JSON сохраняется в файл, машинный stdout доступен через `-EmitJson`.

Проверки: dry-run без JSON-каши; `pytest tests/test_block_family_manifest.py tests/test_backtest_fields.py -q` -> `47 passed`; text_guard -> `PASS`, `reports/qa_gate/recovery_r5_text_guard_20260624T094914Z.json`.

Следующий строгий шаг: `B001.6 итог блока LONG+SHORT`. В ML ничего не передавать.

## B001.4 large LONG закрыт 2026-06-24
Статус: `B001_4_LARGE_LONG_PASS_WITH_WINNER`.

Аудит: `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.

Финальный отчет: `reports/qa_gate/block_family_selection_B001_long_only_20260624T080934Z.json`.

Результат: `F001 / F001_RET1_ALLOW`, OOS `+0.7322559143841945`, сделок `1`, runtime `TRADEFUL_POSITIVE`, `goal_pass=false`.

Перед финальным повтором исправлен перенос runtime-диагностики из `oos_report` в блоковый `best_oos`.

Исторический следующий шаг после этого раздела был `B001.5`; он уже закрыт. Актуальный следующий шаг указан сверху: `B001.6 итог блока LONG+SHORT`. В ML ничего не передавать.

## B001.3 smoke 1д/1д закрыт 2026-06-24
Статус: `B001_3_SMOKE_AUDIT_PASS`.

Аудит: `reports/qa_gate/b001_smoke_1d1d_audit_20260624T075006Z_RU.md`.

Финальные чистые отчеты:
1. LONG: `reports/qa_gate/block_family_selection_B001_long_only_20260624T074316Z.json`.
2. SHORT: `reports/qa_gate/block_family_selection_B001_short_only_20260624T074525Z.json`.

Результат smoke:
1. даты `2026-05-11..2026-05-11 -> 2026-05-12..2026-05-12`;
2. `B001` развернулся в `F001,F002,F003,F004,F005`;
3. LONG победитель smoke: `F001 / F001_RET1_ALLOW`, OOS `+2.404470760400401`, сделок `1`;
4. SHORT победителя нет: лучший доступный `F002 / F002_RET3_ALLOW`, OOS `-0.3092010602366857`, сделок `1`;
5. ML не трогался.

Фиксы: runner теперь разбирает многострочный JSON process-pool, не выбирает отрицательный/нулевой `block_winner`, и корректно помечает dry-run как `OK`.

Следующий строгий шаг: `B001.4 large LONG 2н/1н`, затем аудит перед `B001.5`.

## Block-Family Route Correction 2026-06-24
Status: `block_route_ready_for_b001`.

Audit: `reports/qa_gate/block_family_passport_route_audit_20260624T064900Z.md`.

Corrected route: passports are calibrated by block/family. A multi-passport block such as `B001` runs all active solo F-passports in that family, then the block report selects the best available LONG/SHORT result for the block. Single-passport blocks run as one block with one passport.

Implemented:
1. Added `src/mlbotnav/block_family_manifest.py`.
2. Added generic runner `APTuna/run_block_family_selection.ps1`.
3. Added regression tests in `tests/test_block_family_manifest.py`.
4. Dry-run verified `B001` expands to `F001..F005` on the large-window route.

ML policy: no block result is packaged, approved, or ingested into ML during block calibration. `NO_GO`, `VALIDATION_FAIL`, and preliminary block results remain outside ML until the user manually approves a later final selection.

Next strict step: run `B001` as a block, first LONG then SHORT, through `APTuna/run_block_family_selection.ps1` with `-UseTemporaryUnlock` sequentially.

## Min-Move Runtime Guard Fix 2026-06-24
Status: `fix_applied_superseded_by_block_route`.

Root cause artifact: `reports/qa_gate/ml_optuna_zero_trade_min_move_diagnostic_20260624T051535Z.md`.

The runtime bug is fixed and remains part of the route: `MIN_MOVE_UNREACHABLE` is explicit, penalized/skipped in selection, and the default 1m min-move grid is `0.0,0.001,0.002,0.003`.

Validation before block-route correction: focused pytest `124 passed`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260624T063715Z.json`; readiness frozen at `reports/readiness/readiness_check_20260624T063714Z.json`.

Old F068 next-step pointer is superseded by the block-family route.

## Zero-Trade Diagnostic 2026-06-24
Status: `root_cause_found`.
Artifact: `reports/qa_gate/ml_optuna_zero_trade_min_move_diagnostic_20260624T051535Z.md`.

Root cause: selected `min_expected_move_pct` can be unreachable in `exchange_like` mode after action gates. F067 LONG had `1415` OOS signals after action gate, but selected `min_expected_move_pct=0.01`; proxy max after gate was only `0.005140`, so min-move removed every entry.

Replay on the same F067 LONG OOS CSV: `min_move=0.005` gives `2` trades and `+7.005540`; `min_move=0.003` gives `14` trades and `-16.554791`; `min_move=0.01` gives `0` trades.

Do not package, approve, or ingest F050-F067. The min-move guard/grid/reporting fix has been applied. Historical resume pointer `8.2.19 F068_PATTERNAGE_ALLOW` is superseded by the corrected block-family route at the top of this file.

## Route Memory Audit 2026-06-23
Status: `ON_ROUTE`.

Audit: `reports/qa_gate/ml_optuna_route_memory_audit_20260623T205751Z.md`.

Current control audit after F067: `reports/qa_gate/ml_optuna_route_status_audit_after_f067_20260624T044311Z.md`.

Independent agent `Averroes` confirmed the route through `8.2.8`; local follow-up closed `8.2.9 F058_SHOOTINGSTAR_ALLOW`, `8.2.10 F059_ENGULFBULL_ALLOW`, `8.2.11 F060_ENGULFBEAR_ALLOW`, `8.2.12 F061_RSIBULLDIV_ALLOW`, `8.2.13 F062_RSIBEARDIV_ALLOW`, `8.2.14 F063_MACDBULLDIV_ALLOW`, `8.2.15 F064_MACDBEARDIV_ALLOW`, `8.2.16 F065_OBVBULLDIV_ALLOW`, `8.2.17 F066_OBVBEARDIV_ALLOW`, and `8.2.18 F067_PATTERNSTRENGTH_ALLOW` as `CLOSED_NO_GO`.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file. Do not package, approve, or ingest current F050-F067 results into ML.

Last updated UTC: 2026-06-23T22:57:00Z

## ML Optuna Calibration Stage 8.2.18 F067 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_18_f067_audit_20260623T225700Z.md`.

Scope: F067 Pattern Strength entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F067_PATTERNSTRENGTH_ALLOW`, ignored columns `[]`. LONG reached `1415` signals after action gate but `0` after min-move; SHORT had `0` signals after action gate.

Decision: `F067_PATTERNSTRENGTH_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Text guard before document updates: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T225605Z.json`.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file.

## ML Optuna Calibration Stage 8.2.17 F066 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_17_f066_audit_20260623T224200Z.md`.

Scope: F066 OBV Bearish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F066_OBVBEARDIV_ALLOW`, ignored columns `[]`. LONG and SHORT both had `0` signals after action gate and `0` filled entries.

Decision: `F066_OBVBEARDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Text guard before document updates: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T224148Z.json`.

Next strict step: `8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.16 F065 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_16_f065_audit_20260623T223100Z.md`.

Scope: F065 OBV Bullish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F065_OBVBULLDIV_ALLOW`, ignored columns `[]`. LONG left `4` signals and SHORT left `11` after action gate, then both had `0` after min-move and `0` filled entries.

Decision: `F065_OBVBULLDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T223247Z.json`.

Next strict step: `8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.15 F064 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_15_f064_audit_20260623T222100Z.md`.

Scope: F064 MACD Bearish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F064_MACDBEARDIV_ALLOW`, ignored columns `[]`. LONG and SHORT both had `0` signals after action gate and `0` filled entries.

Decision: `F064_MACDBEARDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T222318Z.json`.

Next strict step: `8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.14 F063 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_14_f063_audit_20260623T221200Z.md`.

Scope: F063 MACD Bullish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F063_MACDBULLDIV_ALLOW`, ignored columns `[]`. LONG and SHORT both had `0` signals after action gate and `0` filled entries.

Decision: `F063_MACDBULLDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T221352Z.json`.

Next strict step: `8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.13 F062 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_13_f062_audit_20260623T220200Z.md`.

Scope: F062 RSI Bearish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F062_RSIBEARDIV_ALLOW`, ignored columns `[]`. LONG and SHORT both had `0` signals after action gate and `0` filled entries.

Decision: `F062_RSIBEARDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T220438Z.json`.

Next strict step: `8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.12 F061 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_12_f061_audit_20260623T215100Z.md`.

Scope: F061 RSI Bullish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F061_RSIBULLDIV_ALLOW`, ignored columns `[]`. LONG had `0` signals after action gate; SHORT had `4` signals after action gate, then `0` eligible bars after min-move and `0` filled entries.

Decision: `F061_RSIBULLDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T215016Z.json`.

Next strict step: `8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.11 F060 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_11_f060_audit_20260623T213900Z.md`.

Scope: F060 Bearish Engulfing entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F060_ENGULFBEAR_ALLOW`, ignored columns `[]`. LONG had `0` signals after action gate; SHORT had `1` signal after action gate, then `0` eligible bars after min-move and `0` filled entries.

Decision: `F060_ENGULFBEAR_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T213857Z.json`.

Next strict step: `8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.10 F059 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_10_f059_audit_20260623T213000Z.md`.

Scope: F059 Bullish Engulfing entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F059_ENGULFBULL_ALLOW`, ignored columns `[]`. LONG and SHORT had `0` signals after action gate and `0` filled entries.

Decision: `F059_ENGULFBULL_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T212931Z.json`.

Next strict step: `8.2.11 Run F060_ENGULFBEAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.9 F058 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_9_f058_audit_20260623T211900Z.md`.

Scope: F058 Shooting Star entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F058_SHOOTINGSTAR_ALLOW`, ignored columns `[]`. LONG had `0` signals after action gate; SHORT had `1` signal after action gate, then `0` eligible bars after min-move and `0` filled entries.

Decision: `F058_SHOOTINGSTAR_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T211810Z.json`.

Next strict step: `8.2.10 Run F059_ENGULFBULL_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.8 F057 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_8_f057_audit_20260623T205000Z.md`.

Scope: F057 Hammer entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F057_HAMMER_ALLOW`, ignored columns `[]`. LONG had `0` signals after action gate; SHORT had `8` signals after action gate but `0` filled entries.

Decision: `F057_HAMMER_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T205204Z.json`.

Next strict step: `8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.7 F056 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_7_f056_audit_20260623T203800Z.md`.

Scope: F056 Bearish Pin Bar entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F056_PINBEAR_ALLOW`, ignored columns `[]`; both sides had `0` signals after action gate.

Decision: `F056_PINBEAR_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T204000Z.json`.

Next strict step: `8.2.8 Run F057_HAMMER_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.6 F055 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_6_f055_audit_20260623T202700Z.md`.

Scope: F055 Bullish Pin Bar entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F055_PINBULL_ALLOW`, ignored columns `[]`. LONG had `1` signal after action gate but `0` filled entries; SHORT had `0` signals after action gate.

Decision: `F055_PINBULL_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T202913Z.json`.

Next strict step: `8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.5 F054 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_5_f054_audit_20260623T201700Z.md`.

Scope: F054 Inside Bar entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F054_INSIDEBAR_ALLOW`, ignored columns `[]`; the action gate reduced raw signals to zero entries.

Decision: `F054_INSIDEBAR_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T201812Z.json`.

Next strict step: `8.2.6 Run F055_PINBULL_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.4 F053 2026-06-23
Status: `closed_no_go_fix_applied`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.

Scope: F053 Doji entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Fix applied: restored readiness freeze and added a live-marker guard in `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` so a second `-UseTemporaryUnlock` process-pool run exits before starting workers.

Decision: `F053_DOJI_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T200628Z.json`.

Next strict step: `8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`.

## ML Optuna Validation Stage 8.2.3 F052 2026-06-23
Status: `closed_validation_fail_no_ml_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_3_f052_fixed_validation_audit_20260623T194700Z.md`.

Scope: fixed F052 CHOCH LONG params from Stage 8.2.2, `SOLUSDT 1m core`, train `2026-05-04..2026-05-17`, OOS `2026-05-18..2026-05-24`.

Result: OOS `-5.696708101293968`, trades `1`, train gate `false`, OOS goal pass `false`, exit reason `timeout`.

Decision: F052 LONG failed adjacent-window validation. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T195125Z.json`.

Next strict step: continue with the next user-selected passport/action discovery, or define a new validation idea with its own audit boundary.

## ML Optuna Calibration Stage 8.2.2 F052 2026-06-23
Status: `closed_positive_test_candidate_needs_validation`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_2_f052_audit_20260623T193700Z.md`.

Scope: F052 CHOCH action, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Result: LONG `goal_pass`, OOS `+5.3486475132039635`, trades `1`; SHORT `goal_fail`, OOS `0.0`, trades `0`.

Caveat: LONG train gate failed, OOS has only one trade, and the only trade exited by timeout.

Decision: not automatic ML GO. Do not build package or start ML training without explicit next decision.

Next strict step: manual decision: validate F052 LONG on adjacent/rolling window, explicitly approve draft package build, or continue next passport/action discovery.

## ML Optuna Calibration Stage 8.2.1 F050 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_1_f050_audit_20260623T192700Z.md`.

Scope: F050 BOSUP action, `long_only`, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Final valid run: process pool `OK`, both workers `goal_fail`, best OOS trades `0`, best OOS net return `0.0`.

Decision: `NO_GO_FOR_ML`. Do not build an ML package or start ML training from this run.

Next strict step: `8.2.2 Run F052_CHOCH_ALLOW large-window candidate`, unless user overrides the target.

## ML Optuna Calibration Stage 8.2 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_audit_20260623T191900Z.md`.

Scope: F051 BOSDOWN action, `short_only`, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Fixes made: process-pool runner now supports `-DataLayer raw|core`; adaptive/search/train/OOS path now passes `--layer`; OOS report now writes top-level `data_layer` and train/test window fields.

Final valid run: process pool `OK`, but both workers returned `goal_fail`; best OOS trades `0`, best OOS net return `0.0`.

Decision: `NO_GO_FOR_ML`. Do not build an ML package or start ML training from this run.

Next strict step: manual decision for next passport/action calibration target or revised `8.2` candidate run.

## ML Large Clean Window Stage 8.1 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.

Created:
1. `configs/ml_large_clean_window_manifest.yaml`.
2. `src/mlbotnav/ml_large_clean_window_manifest_audit.py`.
3. `tests/test_ml_large_clean_window_manifest_audit.py`.

Window: `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Checks: large clean window audit `PASS`, train days `14`, test days `7`, missing files `0`; new tests `4/4 OK`; focused smoke/ingest tests `22/22 OK`.

Boundary: Optuna calibration not started, package not created, ML ingest not started, ML training not started.

Next strict step: `8.2 Run Optuna calibration`.

## ML Smoke Bridge Stage 7 Closeout 2026-06-23
Status: `stage_7_closed_pass`.
Artifact: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.

Closed:
1. `7.1` smoke run.
2. `7.2` test package.
3. `7.3` package contract audit.
4. `7.4` approved registry.
5. `7.5` ML ingest dataset.
6. `7.6` closeout.

Dataset:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`

Dataset manifest:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`

Final checks: smoke window `PASS`; approved registry `PASS`; ML ingest builder `PASS`; dataset contract `PASS`; focused Stage 7 tests `67/67 OK`.

Boundary: ML training not started, no direct Optuna report scan, no unapproved package ingested.

Next strict step: `8.1 Fix large clean window`.

## ML Ingest Stage 7.5 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.

Dataset:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`

Dataset manifest:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`

Built from approved package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`

Checks: dataset builder `PASS`, rows `1177`; dataset contract `PASS`; registry validator/reader/admission status `PASS`; focused ingest tests `24/24 OK`.

Boundary: no direct Optuna report scan; no unapproved package ingested; ML training not started.

Next strict step: `7.6 Stage 7 closeout`.

## ML Approved Registry Stage 7.4 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.

Approved package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`

Registry now has one approved package: `smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`, status `APPROVED_FOR_ML`.

Package files now agree on admission: `manifest.json.status=APPROVED_FOR_ML`, `calibration_package.json.status=APPROVED_FOR_ML`, `audit.md` has `ML decision: GO_FOR_ML`.

Checks: registry validator `PASS`; admission status `PASS`; registry reader `PASS`; package contract/alignment audits `PASS`; focused tests `42/42 OK`.

Boundary: dataset builder / ML ingest not run; ML training not started.

Next strict step: `7.5 Run ML ingest`.

## ML Smoke Package Contract Stage 7.3 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.

Package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`

Context: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`, `B018/F051/F051_BOSDOWN_ALLOW`.

Package status: `DRAFT`. Package audit says `ML decision: NO_GO_FOR_ML`.

Contract audit: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T183343Z.json`, rows `1177`, failed rows `0`, missing columns `0`.

Alignment audits: run_id `PASS`, passport context `PASS`, calibration params `PASS`, data windows `PASS`.

Registry boundary: admission status `PASS / NO_APPROVED_PACKAGES`, registry validator `PASS`, registry reader `PASS`, dataset builder `PASS / NO_APPROVED_PACKAGES`.

Focused tests: `48/48 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T183955Z.json`.

Boundary: no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

Next strict step: `7.4 Add package to approved registry`.

## ML Smoke Package Stage 7.2 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.

Created smoke candidate package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`

Source package:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Context: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`, `B018/F051/F051_BOSDOWN_ALLOW`.

Package status: `DRAFT`. Package audit says `ML decision: NO_GO_FOR_ML`.

Fix applied: package-local `source_reports/oos_report.json` was missing `data_layer` and `date_range`; fixed only the smoke package copy. Source Stage 3 package was not changed.

Audits: contract `PASS`; run_id alignment `PASS`; passport context `PASS`; calibration params `PASS`; data windows `PASS`.

Checks: focused tests `42/42 OK`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; text_guard `PASS`.

Boundary: no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

Next strict step: `7.3 Run package contract audit`.

## ML Smoke Window Stage 7.1 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.

Created Stage 7.1 smoke window manifest:
`configs/ml_smoke_run_manifest.yaml`

Created smoke window auditor:
`src/mlbotnav/ml_smoke_window_manifest_audit.py`

Tests:
`tests/test_ml_smoke_window_manifest_audit.py`

Selected clean smoke window: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`.

Real audit: `PASS`, report `reports/qa_gate/ml_smoke_window_manifest_audit_20260623T182159845644Z.json`, selected dates `2026-05-25`, `2026-05-26`, `2026-05-27`, missing files `0`, errors `0`.

Checks: new tests `5/5 OK`; focused ML smoke/alignment tests `78/78 OK`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; reject-log builder `PASS / NO_REJECTIONS`; text_guard `PASS`.

Boundary: no package created, no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

Next strict step: `7.2 Build test package`.

## ML Alignment Stage 6 Closeout 2026-06-23
Status: `stage_6_closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.

Closed Stage 6:
1. `6.1` run_id alignment.
2. `6.2` passport context alignment.
3. `6.3` calibration params alignment.
4. `6.4` data windows alignment.
5. `6.5` admission status.
6. `6.6` closeout.

Closeout checks: focused tests `121/121 OK`; all five alignment audits `PASS / NO_APPROVED_PACKAGES`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; reject-log builder `PASS / NO_REJECTIONS`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181511Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started.

Next strict step: `7.1 Smoke run`.

## ML Alignment Admission Status Stage 6.5 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.

Created admission status auditor:
`src/mlbotnav/ml_alignment_admission_status_audit.py`

Tests:
`tests/test_ml_alignment_admission_status_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_admission_status_audit_20260623T180909527952Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `121/121 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181123Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started. Stage 6 closeout is reserved for `6.6`.

Next strict step: `6.6 Stage 6 closeout`.

## ML Alignment Data Windows Stage 6.4 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.

Created data windows alignment auditor:
`src/mlbotnav/ml_alignment_data_windows_audit.py`

Tests:
`tests/test_ml_alignment_data_windows_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_data_windows_audit_20260623T154607261155Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `115/115 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154759Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started. Admission status is reserved for `6.5`.

Next strict step: `6.5 Check admission status`.

## ML Alignment Calibration Params Stage 6.3 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.

Created calibration params alignment auditor:
`src/mlbotnav/ml_alignment_calibration_params_audit.py`

Tests:
`tests/test_ml_alignment_calibration_params_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_calibration_params_audit_20260623T154050444104Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `107/107 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154240Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started. Data windows are reserved for `6.4`.

Next strict step: `6.4 Check data windows`.

## ML Alignment Passport Context Stage 6.2 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.

Created passport context alignment auditor:
`src/mlbotnav/ml_alignment_passport_context_audit.py`

Tests:
`tests/test_ml_alignment_passport_context_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_passport_context_audit_20260623T153553932585Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `100/100 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153741Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started. Calibration params are reserved for `6.3`.

Next strict step: `6.3 Check calibration params`.

## ML Alignment Run ID Stage 6.1 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.

Created run_id alignment auditor:
`src/mlbotnav/ml_alignment_run_id_audit.py`

Tests:
`tests/test_ml_alignment_run_id_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_run_id_audit_20260623T152715670875Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `94/94 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153207Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started.

Next strict step: `6.2 Check passport context`.

## ML Stage 5 Closeout 2026-06-23
Status: `stage_5_closed_pass`.
Artifact: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.

Closed Stage 5:
1. `5.1` ML ingest entry point discovery.
2. `5.2` source policy blocks direct old report roots.
3. `5.3` approved package registry reader.
4. `5.4` approved trade dataset builder.
5. `5.5` rejection reason log.
6. `5.6` closeout.

Closeout checks: focused tests `89/89 OK`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; reject-log builder `PASS / NO_REJECTIONS`; old root `reports/optuna` denied as expected; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started.

Next strict step: `6.1 Check run_id alignment`.

## ML Rejection Reasons Stage 5.5 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.

Created rejection reason log builder:
`src/mlbotnav/ml_rejection_reason_log.py`

Tests:
`tests/test_ml_rejection_reason_log.py`

Real reject-log report:
`reports/qa_gate/ml_rejection_reason_log_20260623T151618705623Z.json`

Reject log:
`reports/ml_rejections/ml_rejection_reasons_20260623T151618703912Z.json`

Result: `PASS / NO_REJECTIONS`, registry entries `0`, rejections `0`.

Focused tests: `89/89 OK`.

Final checks: registry validator `PASS`; reject-log smoke `PASS / NO_REJECTIONS` at `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

Next strict step: `5.6 Stage 5 closeout`.

## ML Trade Dataset Assembly Stage 5.4 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.

Created dataset builder:
`src/mlbotnav/ml_approved_trade_dataset_builder.py`

Tests:
`tests/test_ml_approved_trade_dataset_builder.py`

Real builder report:
`reports/qa_gate/ml_approved_trade_dataset_builder_20260623T150934741093Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, approved packages `0`, rows total `0`, dataset path empty.

Focused tests: `85/85 OK`.

Final checks: registry validator `PASS`; builder smoke `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no ML dataset was created from unapproved data; ML training not started.

Next strict step: `5.5 Add rejection reasons`.

## ML Approved Package Registry Reader Stage 5.3 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.

Created registry reader:
`src/mlbotnav/ml_approved_package_registry_reader.py`

Tests:
`tests/test_ml_approved_package_registry_reader.py`

Real registry reader report:
`reports/qa_gate/ml_approved_package_registry_reader_20260623T145755674743Z.json`

Result: `PASS`, approved count `0`, packages exposed to ML `0`.

Focused tests: `82/82 OK`.

Final checks: registry validator `PASS`, `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; ML dataset assembly and ML training not started.

Next strict step: `5.4 Реализовать сборку ML dataset`.

## ML Ingest Source Policy Stage 5.2 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.

Created source-policy guard:
`src/mlbotnav/ml_ingest_source_policy.py`

Tests:
`tests/test_ml_ingest_source_policy.py`

Forbidden direct roots: `reports/optuna`, `reports/pipeline`, `reports/final_review`.

Allowed source classes: approval registry and `reports/ml_candidates/<run_id>/...`.

Focused tests: `79/79 OK`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest/training not started.

Next strict step: `5.3 Реализовать чтение registry`.

## ML Ingest Entry Point Stage 5.1 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.

Current primary ML training ingest entry point:
`src/mlbotnav/pipeline_train_eval.py`

Current orchestrators:
1. `src/mlbotnav/prod_cycle.py`
2. `src/mlbotnav/stage_ladder.py`
3. `src/mlbotnav/adaptive_auto_train.py`

Gap: training does not read `configs/ml_approved_calibration_packages.yaml` and does not assemble from `reports/ml_candidates/<run_id>/trade_log.csv`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest/training not started.

Next strict step: `5.2 Запретить прямое чтение Optuna reports`.

## ML Approval Registry Stage 4 Closeout 2026-06-23
Status: `stage_4_closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.

Current fact: Stage 4 Manual ML Approval Registry is closed.

Registry:
`configs/ml_approved_calibration_packages.yaml`

Validator:
`src/mlbotnav/ml_approval_registry_validator.py`

Real registry validation:
`reports/qa_gate/ml_approval_registry_validator_20260623T143952Z.json`

Result: `PASS`, approved count `0`, failures `0`.

Focused tests: `74/74 OK`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest not started.

Next strict step: `5.1 Найти текущую точку ML ingest`.

## ML Approval Registry Stage 4.4 Validator 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.

Current fact: registry validator exists:
`src/mlbotnav/ml_approval_registry_validator.py`

Tests:
`tests/test_ml_approval_registry_validator.py`

Real registry validation report:
`reports/qa_gate/ml_approval_registry_validator_20260623T143427Z.json`

Result: `PASS`, approved count `0`, failures `0`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest not started.

Next strict step: `4.5 Закрытие этапа 4`.

## ML Approval Registry Stage 4.3 Bans 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.

Current fact: registry bans are recorded in:
`configs/ml_approved_calibration_packages.yaml`

Bans include `NO_GO`, `VALIDATION_FAIL`, missing contract audit `PASS`, invalid manifest, missing package files, and `raw/quarantine` as clean ML input.

Current registry state: `approved_packages: []`.

Boundary: validator CLI/module starts at `4.4`; no package is `APPROVED_FOR_ML`.

Next strict step: `4.4 Сделать validator registry`.

## ML Approval Registry Stage 4.2 Format 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.

Current fact: registry format is documented in comments:
`configs/ml_approved_calibration_packages.yaml`

Current registry state: `approved_packages: []`.

Boundary: no package is `APPROVED_FOR_ML`; validator rules start at `4.3`/`4.4`.

Next strict step: `4.3 Добавить запреты registry`.

## ML Approval Registry Stage 4.1 File 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.

Current fact: manual approval registry file exists:
`configs/ml_approved_calibration_packages.yaml`

Current registry state: `approved_packages: []`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest not started.

Next strict step: `4.2 Описать формат registry`.

## ML Candidate Package Stage 3 Closeout 2026-06-23
Status: `stage_3_closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.

Current fact: Stage 3 is closed for candidate package:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Package contains required files: `calibration_package.json`, `trade_log.csv`, `source_reports.json`, `manifest.json`, `audit.md`, `source_reports/oos_report.json`, `source_reports/pipeline_report.json`.

Validation: required files `PASS`; manifest `PASS`; trade log contract `PASS` (`reports/qa_gate/ml_trade_dataset_contract_audit_20260623T141708Z.json`); focused tests `71/71 OK`; `text_guard PASS`.

Boundary: package remains `DRAFT`, `APPROVED_FOR_ML` not set, ML ingest not started.

Next strict step: `4.1 Создать registry файл`.

## ML Candidate Package Stage 3.6 Package Audit 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.

Current fact: package-local `audit.md` exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/audit.md`

ML decision in audit: `NO_GO_FOR_ML`.
Review state: `READY_FOR_MANUAL_REVIEW`.
Reason: package is `DRAFT` and requires manual approval before ML ingest.

Validation: `py_compile PASS`; focused tests `71/71 OK`; package audit content check `PASS`.

Next strict step: `3.7 Закрытие этапа 3`.

## ML Candidate Package Stage 3.5 Manifest 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.

Current fact: package-local `manifest.json` exists and parses:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/manifest.json`

Manifest fields: `SOLUSDT / 1m / core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`, `B018/F051/F051_BOSDOWN_ALLOW`, status `DRAFT`.

Validation: `py_compile PASS`; focused tests `69/69 OK`; manifest parse/content audit `PASS`.

Next strict step: `3.6 Добавить audit.md`.

## ML Candidate Package Stage 3.4 Source Reports 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.

Current fact: package-local source reports exist:
1. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports.json`
2. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/oos_report.json`
3. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/pipeline_report.json`

Optional `optuna_report.json` is `NOT_PROVIDED` for this candidate.

Validation: `py_compile PASS`; focused tests `67/67 OK`.

Next strict step: `3.5 Добавить manifest.json`.

## ML Candidate Package Stage 3.3 Trade Log 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.

Current fact: package-local `trade_log.csv` exists and passes `ml_trade_dataset_contract`:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/trade_log.csv`

Contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T134753Z.json`.

Validation: `py_compile PASS`; focused tests `65/65 OK`.

Next strict step: `3.4 Добавить исходные отчеты`.

## ML Candidate Package Stage 3.2 Calibration Package 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.

Current fact: `calibration_package.json` exists and parses:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/calibration_package.json`

Package fields: `B018/F051/F051_BOSDOWN_ALLOW`, signal mode `short_only`, status `DRAFT`, `4` calibration params.

Validation: `py_compile PASS`; focused tests `63/63 OK`.

Next strict step: `3.3 Добавить trade_log.csv`.

## ML Candidate Package Stage 3.1 Structure 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.

Current fact: package builder skeleton exists at `src/mlbotnav/ml_candidate_package_builder.py`.

Created package directory:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Validation: `py_compile PASS`; focused tests `61/61 OK`.

Boundary: no `calibration_package.json`, `trade_log.csv`, `manifest.json`, `audit.md`, or `APPROVED_FOR_ML` yet.

Next strict step: `3.2 Добавить calibration_package.json`.

## ML Trade Dataset Stage 2 Closeout 2026-06-23
Status: `stage_2_closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.

Current fact: Stage 2 `Trade Log CSV Enrichment` is closed. Pipeline and OOS trade CSV artifacts now pass `ml_trade_dataset_contract`.

Evidence:
1. Pipeline contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133238Z.json`.
2. OOS contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133240Z.json`.
3. Focused tests: `59/59 OK`.
4. Text guard: `reports/qa_gate/recovery_r5_text_guard_20260623T133249Z.json`.

Boundary: no automatic ML approval. Stage 3 starts candidate package builder work.

Next strict step: `3.1 Создать структуру пакета`.

## ML Trade Dataset Stage 2.8 OOS CSV 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.

Current fact: fresh OOS CSV `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.csv` passed `ml_trade_dataset_contract`.

Contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T132804Z.json`.

OOS result: net return pct `-0.9395906630311424`, trades `3`, goal pass `false`. Strategy quality is not the gate for WBS `2.8`.

Next strict step: `2.9 Закрытие этапа 2`.

## ML Trade Dataset Stage 2.7 Pipeline CSV 2026-06-23
Status: `done / closed_pass_after_controlled_temp_unlock`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.

Current fact: `pipeline_train_eval.py` now supports `--layer` and writes the selected layer into trade CSV run context. This fixes the hardcoded `data_layer=raw` issue for future clean `core` ML contract runs.

Runtime validation was completed through controlled temporary unlock. Fresh CSV `reports/pipeline/backtest_trades_SOLUSDT_1m_20260623T132424Z.csv` passed `ml_trade_dataset_contract`.

Contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T132425Z.json`.

Readiness was restored to frozen state after the run.

Next strict step: `2.8 Проверить OOS CSV`.

## ML Trade Dataset Stage 2.6 MAE/MFE 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive MAE/MFE labels before write: `mae_pct`, `mfe_pct`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Validation: `py_compile PASS`; focused tests `59/59 OK`; `text_guard PASS`.

Boundary: this is not full Stage 2 closeout yet; pipeline CSV contract verification starts at `2.7`.

Next strict step: `2.7 Проверить pipeline CSV`.

## ML Trade Dataset Stage 2.5 Hit Labels 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive hit labels before CSV write: `tp_hit`, `sl_hit`, `timeout_hit`, `end_of_data_hit`, `sl_ambiguous_hit`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Boundary: this is not full ML-ready CSV yet; MAE/MFE starts at `2.6`.

Next strict step: `2.6 Добавить MAE/MFE`.

## ML Trade Dataset Stage 2.4 Duration Labels 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_4_duration_labels_audit_20260623T125816Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive duration label columns before CSV write: `bars_in_trade`, `holding_seconds`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Fix applied: duration columns are created/cast as `object` before mixed blank/numeric writes.

Boundary: this is not full ML-ready CSV yet; hit labels start at `2.5`, then MAE/MFE follow.

Next strict step: `2.5 Добавить hit labels`.

## ML Trade Dataset Stage 2.1 Run Context 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive run-level context columns before CSV write: `run_id`, `symbol`, `timeframe`, `data_layer`, `train_start`, `train_end`, `test_start`, `test_end`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Boundary: this is not full ML-ready CSV yet; passport context starts at `2.2`, then trade identity/duration/hit labels/MAE-MFE follow.

Next strict step: `2.2 Добавить passport context`.

## ML Trade Dataset Contract Stage 1 Closeout 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.

Current fact: WBS Stage 1 `ML Trade Dataset Contract` is closed. Steps `1.1-1.6` are all `CLOSED_PASS`; the contract and executable validator exist and focused checks pass.

Boundary: real `backtest_trades_*.csv` / `oos_backtest_trades_*.csv` enrichment is not done yet and starts in Stage 2. Do not start the big calibration/OOS run yet.

Next strict step: `2.1 Добавить run-level context`.

## ML Trade Dataset Contract Step 1.6 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_contract_step_1_6_audit_20260623T122406Z.md`.
Validator: `src/mlbotnav/ml_trade_dataset_contract.py`.
Tests: `tests/test_ml_trade_dataset_contract.py`.
CLI report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T122406Z.json`.

Current fact: executable ML trade dataset contract validation is now in place. It checks required passport/run context, entry/exit fields, trade outcome labels, clean `data_layer=core`, hit-label consistency, `trade_id` uniqueness, and MAE/MFE sign rules.

Validation: `py_compile PASS`; focused unittest `4/4 OK`; CLI smoke `PASS`.

Next strict step: `1.7 Закрытие этапа 1`.

## Optuna / ML / Entry / Exit Alignment Audit 2026-06-23
Status: `done / pass_with_ml_dataset_gaps`.
Artifact: `reports/qa_gate/optuna_ml_entry_exit_alignment_audit_20260623T162411Z.md`.
Action plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Budget: `10-14 hours` engineering work, excluding long runtime waiting.

Current fact: read-only audit checked the current Optuna -> adaptive -> pipeline_train_eval -> oos_evaluate -> backtest chain.

Decision:
1. `calibration_params` propagate correctly from Optuna into train/OOS/backtest and are saved in JSON reports/model payload.
2. Current F051 action gate is isolated as `F051_BOSDOWN_ALLOW`; no old/stale action gate is active for that contour.
3. CSV trade/OOF outputs are not yet ML-ready alone because they do not carry `action_id`, `passport_id`, `block_id`, or `calibration_params_json`.
4. Trade CSV has baseline entry/exit fields and `exit_reason`, but is missing `trade_id`, `bars_in_trade`, `tp_hit`, `sl_hit`, `timeout_hit`, `mae_pct`, and `mfe_pct`.
5. Clean candle layer `core` covers `2026-01-26..2026-05-31`; `2026-06-01` is only raw/quarantine and incomplete to `15:03 UTC`.

Next strict step: implement the ML trade dataset contract and row-level passport/trade outcome fields before any 2-week calibration -> 1-week OOS run. Recommended clean window after contract: train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`, layer `core`.

## Passport Block Registry 2026-06-22T12:57:27Z
Active registry: `configs/calibration_action_passports.yaml`.
Rule: user passports are registered under `Bxxx` blocks before any executable Optuna matrix is used.
`B001` is `Цена и волатильность` / `price_volatility`; active solo passports are `F001-F005` (`ret_1`, `ret_3`, `ret_6`, `ret_12`, `ret_24`).
The B001 combination/tournament path is diagnostic-only; new baseline work should calibrate solo passports first and promote only a tradeful non-negative OOS feature.
Current ids: `B001` active RET_N (`F001-F005`), `B002` active HL spread (`F006`). Further user passport blocks should continue as the next `Bxxx` ids.

## F006 Passport Run 2026-06-22T13:10:45Z
Implemented `F006` (`hl_spread_1m`) in `B002`, matrix `configs/calibration_matrices/passport_actions/F006_hl_spread_1m_entry_filter.yaml`, runtime column `F006_HLSPREAD_ALLOW`, and backtest entry gate support.
Focused checks passed.
Clean direct LONG result: `NO_GO`, params `F006_cmp=-1` (`LESS`), `F006_thr_pct=0.75`, OOS `-6.153363933968025%`, trades `2`.
Audit: `reports/qa_gate/f006_hl_spread_long_only_audit_20260622T131045Z.json`.
Do not use the first 3-worker pool final_review/top-card params for F006 because audit found a same-second artifact mismatch; use the clean direct contour run.

## F007 Passport Run 2026-06-22T13:33:18Z
Implemented `F007` (`rolling_std_20_1m`) in `B003`, matrix `configs/calibration_matrices/passport_actions/F007_rolling_std20_1m_entry_filter.yaml`, runtime column `F007_RSTD20_ALLOW`, and backtest entry gate support.
Focused checks passed.
LONG result: `NO_GO`, params `F007_cmp=1` (`GREATER`), `F007_thr_pct=0.04`, OOS `-1.1459443803135683%`, trades `1`.
SHORT result: `NO_GO`, params `F007_cmp=-1` (`LESS`), `F007_thr_pct=0.34`, OOS `-5.744959575084807%`, trades `3`.
Audit: `reports/qa_gate/f007_rolling_std20_long_short_audit_20260622T133318Z.json`.

## F008 Passport Run 2026-06-22T13:59:47Z
Implemented `F008` (`atr14_1m`) in `B004`, matrix `configs/calibration_matrices/passport_actions/F008_atr14_1m_entry_filter.yaml`, runtime column `F008_ATR14_ALLOW`, and backtest entry gate support.
Focused checks passed.
LONG result: `NO_GO`, params `F008_cmp=-1` (`LESS`), `F008_thr_pct=0.28`, OOS `-1.1459443803135683%`, trades `1`.
SHORT result: `NO_GO`, params `F008_cmp=-1` (`LESS`), `F008_thr_pct=2.33`, OOS `-5.744959575084807%`, trades `3`.
Audit: `reports/qa_gate/f008_atr14_long_short_audit_20260622T135947Z.json`.

## EMA F009-F011 Passport Run 2026-06-22T14:34:20Z
Implemented EMA family in `B005`, matrices `F009_ema_gap_20_50_1m_entry_filter.yaml`, `F010_ema20_slope_5_1m_entry_filter.yaml`, `F011_ema200_gap_1m_entry_filter.yaml`, runtime columns `F009_EMAGAP_ALLOW`, `F010_EMASLOPE5_ALLOW`, `F011_EMA200GAP_ALLOW`, and backtest gate support.
Focused checks passed.
Results: F009 LONG `0%/0 trades`; F009 SHORT `-18.1676%/9 trades`; F010 LONG `-29.1066%/10 trades`; F010 SHORT `-18.6178%/5 trades`; F011 LONG `0%/0 trades`; F011 SHORT `0%/0 trades`.
Decision: `NO_GO`, no tradeful non-negative candidate.
Audit: `reports/qa_gate/ema_f009_f011_long_short_audit_20260622T143420Z.json`.

## F012 RSI14 Passport Run 2026-06-22T14:47:50Z
Implemented `F012` (`rsi14_1m`) in `B006`, matrix `configs/calibration_matrices/passport_actions/F012_rsi14_combined_entry_filter.yaml`, runtime column `F012_RSI14_ALLOW`, and backtest gate support.
Focused checks passed; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T145323Z.json`.
LONG result: `NO_GO`, params `F012_signal_mode=1` (`LEVEL`), `F012_cmp=1` (`GREATER`), `F012_level=88`, OOS `0%`, trades `0`.
SHORT result: `NO_GO`, params `F012_signal_mode=1` (`LEVEL`), `F012_cmp=1` (`GREATER`), `F012_level=30`, OOS `-47.5754123715459%`, trades `22`, wins/losses `1/21`, exits `timeout`.
Audit: `reports/qa_gate/f012_rsi14_combined_long_short_audit_20260622T144750Z.json`.

## F017/F018 Combined Decision 2026-06-23T08:10:00Z
Audit finding closed: `F017/F018` stays one combined Stochastic K/D passport, not two separated action passports.
Reason: `%K` and `%D` are two lines of the same Stochastic instrument, and `KD_CROSS` requires both lines inside one signal grammar.
Runtime/action boundary stays `F017_F018_STOCH14_ALLOW`; this is not old Optuna mixing and not a block-combo tournament.
Existing trusted run remains `NO_GO`: LONG `-84.05333161848922%/51 trades`, SHORT `-17.53680624691214%/6 trades`.
Audit: `reports/qa_gate/f017_f018_combined_decision_audit_20260623T081000Z.md`.

## Stale Action Column Hardening 2026-06-23T08:20:00Z
Fixed the remaining F001-F083 runtime/backtest audit item.
`run_prob_backtest` accepts `active_entry_action_columns`, Optuna passport search passes the current matrix action id, and backtest infers active gates from `Fxxx_*` passport params when needed.
Regression test confirms stale unrelated action columns are ignored for an active passport.
Validation: py_compile PASS; stale/F039 focused tests `2/2 OK`; project venv `tests.test_backtest_fields tests.test_optuna_search_runtime` `110/110 OK`; `text_guard PASS` `reports/qa_gate/recovery_r5_text_guard_20260623T081355Z.json`.
Audit: `reports/qa_gate/stale_action_column_hardening_20260623T082000Z.md`.
Current audit route status: planned gaps closed, F017/F018 combined decision closed, stale action-column hardening closed.

## Passport Control Index 2026-06-23T08:41:37Z
Created the active human control panel: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_CONTROL_INDEX_RU.md`.
Decision: use a hybrid management model, not one huge executable config.
Layers are fixed as: Passport MD -> `configs/calibration_action_passports.yaml` registry -> executable passport matrix -> run/audit artifact.
The index records source-of-truth files, no-mixing rules, block policy, LONG/SHORT policy, exit/ML boundaries, and the standard workflow for the next passports.
Recommended next work: result register is built; `F051 SHORT` validation is complete and failed promotion; choose the next passport/feature route or define a new validation idea.
Audit: `reports/qa_gate/passport_control_index_audit_20260623T084500Z.md`.

## Passport Result Register F001-F083 2026-06-23
Status: `done / active_result_register`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_RESULT_REGISTER_RU.md`.
Audit: `reports/qa_gate/passport_result_register_audit_20260623T084702Z.md`.

Current fact: added the compact F001-F083 result register so the next calibration decisions have one readable control map.

Decision:
1. No `F001-F083` feature is production GO.
2. Only `F051 BOS down SHORT` is a positive test candidate: `+2.810523%`, `1` OOS trade.
3. `F051 SHORT` failed multi-day validation and is not eligible for promotion, ML export, or combination.
4. `NO_GO` rows cannot be reused as active candidates.

Validation: explicit id coverage PASS; text_guard PASS, report `reports/qa_gate/recovery_r5_text_guard_20260623T084932Z.json`.

Next: `F051 SHORT` validation is complete and failed promotion; choose the next passport/feature route or define a new validation idea.

## F051 SHORT Multi-Day Validation 2026-06-23
Status: `done / validation_fail_no_promotion`.
Artifact: `reports/qa_gate/f051_short_multiday_validation_audit_20260623T091000Z.md`.

Current fact: validated the previous one-day positive `F051 BOS down SHORT` candidate on three adjacent OOS windows.

Result:
1. Original baseline `2026-05-31 -> 2026-06-01`: `+2.810523%`, `1` trade.
2. Validation `2026-05-28 -> 2026-05-29`: `0%`, `0` trades.
3. Validation `2026-05-29 -> 2026-05-30`: `0%`, `0` trades.
4. Validation `2026-05-30 -> 2026-05-31`: `0%`, `0` trades.

Decision: `F051 SHORT` failed multi-day validation and is not promotable. Do not export it to ML or combine it with other blocks.

## F001-F083 Passport Route Closeout 2026-06-23
Status: `done / closed_no_production_go`.
Artifact: `reports/qa_gate/f001_f083_route_closeout_audit_20260623T091500Z.md`.

Current fact: closed the full `F001-F083` passport route after `F051 SHORT` failed adjacent-window validation.

Decision:
1. No feature from `F001-F083` is production GO.
2. Nothing from `F001-F083` can move to ML, combination, candidate pool, or execution config.
3. Next work must be a new passport/feature/hypothesis route, a new validation idea, or separate exit/risk passports.

## Core ML Bot TZ Audit 2026-06-23
Status: `done / audit_only / partial_match_with_strong_calibration_core`.
Artifact: `reports/qa_gate/core_ml_bot_tz_audit_20260623_RU.md`.

Audited the project against the user-provided TZ for a compact 1m autonomous ML trading bot core.
Conclusion: the project already has a strong calibration/ML/backtest core in `src/mlbotnav`, but the TZ is only partially matched because modular contracts, complete CORE feature set, entry/exit/risk decision contracts, MAE/MFE, trade outcome labels, and ML dataset builder are not closed as separate layers.
Decision: do not create a parallel `trading_bot/` tree; add thin contracts/facades over `src/mlbotnav`, then fill missing CORE gaps.
Next safe route: feature/entry/exit/risk/trade-log/ML-dataset contracts first, then missing CORE columns, then separate exit/risk passports.

## Active Calibration Source Override
For calibration-node work, the active source of truth is now `docs/CALIBRATION_NODE_CURRENT/`.
Read `README_RU.md`, `TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`, `CURRENT_STATUS_RU.md`, and `COMMANDS_RU.md`.
Old chronology, old journals, old TZ files, and old P20xx/P21xx chains are `OLD/FROZEN` and must not be used as the next-task queue.

## Optuma Bridge Steps 2-5 2026-06-04T09:06:15Z
Active short TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_OPTUMA_BRIDGE_CURRENT_2026-06-04_RU.md`.
Closed current repairs after Step 1: `volume_flow` now applies calibrated `return_lookback` for `vol_chg`, `delta_volume`, `obv_slope_5`; `density_profile` now applies calibrated `div_lookback` for `density_vpoc_drift_20`; `structure_ta` now applies calibrated `threshold_fine` for `retest_flag` and `false_breakout_flag`; FIBO now has `fib_window` and explicit `fib_level` values `0.236/0.382/0.5/0.618/0.786` in the full and catalog block matrices.
Validation: focused tests `95/95 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS` for 7 YAML matrices x 2 contours x 3 grid presets; `text_guard PASS` (`reports/qa_gate/recovery_r5_text_guard_20260604T090928Z.json`).

## Pattern Structure Volume Entry 2026-06-04T09:16:54Z
Closed current repair: `pattern_structure_volume_entry` now has runtime features for classic figure patterns and the `pattern + structure_ta + volume_flow` entry bundle.
Added dataset features: double top/bottom, head-and-shoulders/inverse, triangle, pennant, rising/falling wedge, range, volume confirm, level confirm, long/short entry flags, SL buffer distance, TP ladder score.
Matrices updated: full matrix and catalog block matrices have the new pattern profiles; full matrix and `catalog_block_06_pattern.yaml` include the new pattern feature rows; `vol_z` now uses `vol_z_window`.
Validation: focused tests `97/97 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS`; `text_guard PASS` (`reports/qa_gate/recovery_r5_text_guard_20260604T091818Z.json`).

## Pattern Runtime CPU Pause 2026-06-04T10:20:10Z
Dry command gate passed: `reports/qa_gate/pattern_block06_command_gate_20260604T101700Z.json`.
`pattern long_only narrow` completed runtime OK, workers `3/3`, candidate `NO_CANDIDATE`, max CPU `57%`: `reports/qa_gate/pattern_long_only_narrow_closeout_20260604T101742Z.json`.
`pattern long_only medium` completed launcher OK/workers `3/3`, best OOS `-78.782906127645376%`, trades `35`, candidate `NO_CANDIDATE`, but monitor saw CPU spike `97%`: `reports/qa_gate/pattern_long_only_medium_closeout_20260604T102010Z.json`.
Next current step is paused before `pattern long_only wide`: confirm CPU profile. Options are hard-stop on first CPU sample `>85%`, reduce to `2` process workers / `6` search workers, or explicitly accept brief spikes.

## Pattern Block06 Full Runtime 2026-06-04T10:30:51Z
CPU rule updated by user: short spikes are allowed; sustained `>85%` for roughly `2-5` minutes means reduce profile and continue the same substep.
Completed `pattern` block runtime through `long_only` and `short_only`, each `narrow -> medium -> wide`, on `3/9/3`.
Result: runtime OK, workers `3/3` on all six runs, no worker crash, no sustained CPU overload, candidate `NO_CANDIDATE`.
Best block result: `long_only narrow`, `0%`, trades `0`.
Block artifact: `reports/qa_gate/pattern_block06_full_closeout_20260604T103051Z.json`.
Readable report: `reports/qa_gate/pattern_block06_human_readable_20260604T103051Z_RU.md`.
Important finding after report audit: search-level best candidates contain `calibration_params`, but final `best_oos` fallback selections have `selected_calibration_params={}`. Next repair should preserve calibration params for fallback/no-pass candidate selection, then rerun/replay block06 before calling it parametrically closed.

## Pattern Fallback Calibration Params Fix 2026-06-04T10:43:12Z
Artifact: `reports/qa_gate/pattern_fallback_calibration_params_fix_20260604T104312Z_RU.md`.
Fixed `src/mlbotnav/adaptive_auto_train.py`: adaptive-loop now uses `_candidate_pool_from_search_report` and prefers `top_candidates` when they contain `calibration_params`, instead of losing params through `all_candidates_lite`.
Test added in `tests/test_adaptive_candidate_pick.py`.
Validation: changed file `py_compile PASS`; focused tests `80/80 OK`; old pattern search reports now select fallback candidates with `18` calibration params.
Boundary: old block06 runtime artifacts are not rewritten; rerun/replay block06 to produce final `best_oos.selected_calibration_params` in new artifacts.

## Optuma Bridge Step 1 2026-06-04T08:56:24Z
Active short TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_OPTUMA_BRIDGE_CURRENT_2026-06-04_RU.md`.
Step 1 fixed the `calibration_params` anchor gap: selected Optuna params now move from `adaptive_auto_train.py` candidate selection into `pipeline_train_eval.py`, are saved in train report/model payload, and are applied by `oos_evaluate.py` in feature generation and final backtest.
Validation: changed files `py_compile PASS`; focused tests `79/79 OK` for `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_adaptive_candidate_pick`, `tests.test_optuna_search_runtime`, `tests.test_backtest_fields`.
Next current repair: `volume_flow` formula mismatches (`vol_chg`, `delta_volume`, `obv_slope_5`).

## APTuna Block Alignment Audit 2026-06-03T16:48:08Z
Artifact: `reports/qa_gate/aptuna_block_alignment_audit_20260603T164808Z.json`.
Status: `PASS`, `issues=0`, `blockers=0`.
All 6 calibration blocks align across dataset/features config/draft/full matrix/catalog block matrices/APTuna runner wiring: `price_volatility`, `trend_momentum`, `volume_flow`, `density_profile`, `structure_ta`, `pattern`.
Full matrix facts: `68` feature rows (`56` calibratable, `12` fixed), `20/20` hypothesis rows calibratable.
APTuna reads the active matrix through `MLBOTNAV_CALIBRATION_MATRIX_PATH`; catalog block matrices compile for `long_only` and `short_only` under `narrow/medium/wide`.
Boundary: only sequential feature_sweep matrices `H001` and `H002` are generated so far; `H003` generation/compile remains the next strict step, not an alignment issue.

## Block vs Feature Sweep Boundary 2026-06-03T16:59:00Z
Artifact: `reports/qa_gate/aptuna_block_vs_feature_sweep_audit_20260603T170400Z.json`.
Readable doc: `docs/CALIBRATION_NODE_CURRENT/BLOCK_VS_FEATURE_SWEEP_AUDIT_2026-06-03_RU.md`.
Status: `PASS_WITH_MODE_BOUNDARY`.
Conclusion: `catalog_blocks/*.yaml` is whole-block calibration; generated `feature_sweep/h*.yaml` is single feature-slot calibration. If the operator wants "calibrate the whole block", do not continue `H003` as the main battle path; switch the active queue to catalog block matrices.
Encoding note: older artifact `reports/qa_gate/aptuna_block_vs_feature_sweep_audit_20260603T165900Z.json` was superseded by ASCII-safe JSON because it could show mojibake in Windows/PowerShell.

## Active Sweep Status 2026-06-03T13:16:59Z
Slot `H001` (`price_volatility` / `ret_1` / `return_lookback`) is closed as `slot_complete_runtime_ok_no_candidate`.
Both stacks ran separately: `long_only` and `short_only`, each through `narrow -> medium -> wide` with profile `3x3/9`.
Best long stack result: `medium long_only`, OOS `-8.650246602184342%`, trades `4`, no candidate.
Best short stack result: `narrow short_only`, OOS `0%`, trades `0`, no candidate.
Artifacts: `reports/qa_gate/h001_long_stack_complete_20260603T131326Z.json`, `reports/qa_gate/h001_short_stack_complete_20260603T131659Z.json`, `reports/qa_gate/h001_slot_closeout_20260603T131659Z.json`.
Next strict slot: `H002` (`price_volatility` / `ret_3` / `return_lookback`); first create/compile the H002 matrix, then run `H002 long_only` full stack.

## Active Human-Readable Report Format 2026-06-03T13:30:00Z
Slot numbering rule is fixed: `H001`, `H002`, ... are feature/hypothesis slots. Long/short are child stacks inside the same slot, not separate slot numbers.
Use readable child ids such as `H001-LONG`, `H001-SHORT`, and `H001-SLOT`.
Human reports must show Russian block/tool names, technical name, calibrated params, min/max/step range, narrow/medium/wide results for long and short, best long, best short, final decision, and artifact path.
Example: `H001` is `price_volatility.ret_1`; `H001-LONG` and `H001-SHORT` are already complete. `H002` is the next slot `price_volatility.ret_3`.
Human-readable report file: `reports/optuna_catalog/index/hypothesis_feature_sweep_human_ru.md`.
Format correction 2026-06-03T16:02:12Z: slot card headings must stay short and use exact RU names from `configs/features_block.yaml`, for example `H003 | Доходность за 6 баров`; H003 is `kind=feature_row`, not a hypothesis.
Full RU names catalog: `docs/CALIBRATION_NODE_CURRENT/RU_NAMES_CATALOG_2026-06-03.md`.

## Active Sweep Status 2026-06-03T15:41:33Z
Slot `H002` (`price_volatility` / `ret_3` / `return_lookback`) is closed as `slot_complete_runtime_ok_no_candidate`.
Matrix: `configs/calibration_matrices/feature_sweep/h002_price_volatility_ret_3.yaml`; compile report `reports/qa_gate/h002_feature_sweep_matrix_compile_20260603T153704Z.json`.
Both stacks ran separately: `long_only` and `short_only`, each through `narrow -> medium -> wide` with profile `3x3/9`.
Best long stack result: `wide long_only`, OOS `-8.650246602184342%`, trades `4`, no candidate.
Best short stack result: `narrow/medium short_only`, OOS `-0.2662724500743341%`, trades `2`, no candidate.
Artifacts: `reports/qa_gate/h002_long_stack_complete_20260603T154133Z.json`, `reports/qa_gate/h002_short_stack_complete_20260603T154133Z.json`, `reports/qa_gate/h002_slot_closeout_20260603T154133Z.json`.
Next strict slot: `H003` (`price_volatility` / `ret_6` / `return_lookback`); first create/compile the H003 matrix, then run `H003 long_only` full stack.

## Project
`MLbotNav` is a trading/ML project with an Optuna/APTuna calibration contour for `SOLUSDT` on `1m` data. The current work is focused on launch-quality calibration, not on rebuilding the runtime contour from scratch.

## Current Goal
Build a full Optuna calibration catalog across blocks, features, and hypotheses:
walk active parameter ranges from `min` to `max`, classify every run as `positive`, `negative`, `neutral`, or `infra_fail`, and preserve all parameter/config artifacts. For each block, the block outcome is the best found result by the ranking/gate metrics, not a random run; negative/neutral runs are retained as calibration history, but only the best valid positive result can become `candidate_for_forward`. Production still requires `F1/F2 = 2/2 PASS` plus a new production `GO` decision package.

## Current Calibration Node Update 2026-06-03T11:28:24Z
Active source remains `docs/CALIBRATION_NODE_CURRENT/`.
Closed under the new TZ `2026-06-03T10:25:00Z`: `volume_flow`, `density_profile`, `structure_ta`, and `pattern`.
`structure_ta` completed `narrow/medium/wide` x `long_only/short_only` with runtime `OK` after rerun; best result is `wide long_only` OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production.
`pattern` completed `narrow/medium/wide` x `long_only/short_only` with runtime `OK`; best result is `wide long_only` OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production.
Pattern closeout artifact: `reports/qa_gate/calibration_node_pattern_closeout_20260603T112654Z.json`.
Fix added in `src/mlbotnav/adaptive_auto_train.py`: OOS report JSON is now read via `_read_json_report_with_retry`, so empty/unreadable OOS reports become recorded iteration failures instead of worker crashes.
Focused tests: `83/83 OK`. Health after pattern closeout: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T112958Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T112818Z.json`), `pip check PASS`.
Next active step is not production/unfreeze; it requires a separate new TZ or GO package.

## Current Sequential Sweep Update 2026-06-03T12:18:33Z
User paused the current `TOP_EXPERIMENTAL` candidate and redirected work to a sequential hypothesis/feature sweep.
New active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_HYPOTHESIS_FEATURE_SWEEP_2026-06-03_RU.md`.
Goal: verify that every hypothesis/feature slot walks min->max correctly and records results, not optimize for production profit.
Inventory artifact: `reports/qa_gate/hypothesis_feature_sweep_inventory_20260603T121643Z.json`.
Sweep table: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`.
Slot policy: `H000` baseline/control + `H001-H068` feature rows = `69` logical slots. Matrix has `68` feature rows: `56` calibratable, `12` non-calibratable; `H000` is non-calibrated control.
`H001` matrix created and compile passed: `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`, report `reports/qa_gate/h001_feature_sweep_matrix_compile_20260603T121833Z.json`.
`H001 narrow long_only` completed: launcher `OK`, workers `3/3 exit_code=0`, best OOS `-30.924389997582892%`, trades `13`, class `negative_runtime_ok`.
Artifact: `reports/qa_gate/h001_narrow_long_only_20260603T122520Z.json`.
TZ corrected: long and short are separate stacks; each stack runs `narrow -> medium -> wide`; standard profile is `3x3/9` with trials/timeouts `narrow=60/300`, `medium=120/600`, `wide=180/900`.
`H001 narrow short_only` completed: launcher `OK`, workers `3/3 exit_code=0`, best OOS `+0.2544418318741748%`, trades `1`, class `provisional_plus_goal_fail`, not candidate.
Artifact: `reports/qa_gate/h001_narrow_short_only_20260603T124931Z.json`.
Next command: `H001 medium long_only` 1d->1d from `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.

## Current Truth
1. Active launch decision is `NO_GO`.
2. Freeze is ON: `project_ready=false`, `enforce_freeze=true`.
3. Historical `GO` records are historical only and are not launch permission.
4. Active track is V3 bounded calibration using `feature/logic` hypotheses.
5. Active overlay is full calibration catalog, not early stop on `NO_CANDIDATE`.

## Done
1. Global launch audit created and synced.
2. V3 `Package A` defined and completed.
3. `Package A long_only`: `9/9` runs completed.
4. `Package A short_only`: `9/9` runs completed.
5. Unified `Package A triage`: `NO_CANDIDATE`.
6. Package-level `Package A post-audit`: `PASS`.
7. Full calibration catalog checkpoint created:
   `reports/qa_gate/p2026_optuna_full_calibration_catalog_checkpoint_20260602T083509Z.json`.
8. Catalog folders created under `reports/optuna_catalog/`.
9. Post-sync audit after catalog checkpoint passed:
   `reports/qa_gate/p2027_optuna_full_calibration_catalog_post_sync_audit_20260602T083823Z.json`.
10. Step 1 wiring inventory passed:
   `reports/optuna_catalog/index/p2030_step1_wiring_inventory_20260602T092159Z.json`.
11. Step 2 smoke command set passed:
   `reports/optuna_catalog/index/p2032_step2_1d1d_smoke_command_set_20260602T092710Z.json`.
12. Step 3 smoke preflight passed:
   `reports/qa_gate/p2034_step3_smoke_preflight_20260602T093214Z.json`.
13. Step 4 long_only smoke catalog entry:
   `reports/optuna_catalog/neutral/p2035_step4_long_only_1d1d_smoke_neutral_20260602T093324Z.json`.
14. Step 5 short_only smoke catalog entry:
   `reports/optuna_catalog/neutral/p2036_step5_short_only_1d1d_smoke_provisional_plus_goal_fail_20260602T093604Z.json`.
15. Step 6 triage:
   `reports/qa_gate/p2037_step6_1d1d_smoke_triage_20260602T093704Z.json`.
16. Step 7 medium command set passed:
   `reports/optuna_catalog/index/p2039_step7_medium_command_set_20260602T095335Z.json`.
17. Step 7 medium long_only catalog entry:
   `reports/optuna_catalog/negative/p2040_step7_medium_long_only_negative_20260602T095814Z.json`.
18. Step 7 medium short_only catalog entry:
   `reports/optuna_catalog/negative/p2041_step7_medium_short_only_negative_20260602T100012Z.json`.
19. Step 7 medium triage:
   `reports/qa_gate/p2042_step7_medium_triage_20260602T100020Z.json`.
20. Step 7 medium post-sync audit:
   `reports/qa_gate/p2043_step7_medium_post_sync_audit_20260602T100235Z.json`.
21. Step 8 wide command set passed:
   `reports/optuna_catalog/index/p2044_step8_wide_command_set_20260602T100351Z.json`.
22. Step 8 wide runtime and triage completed:
   `reports/qa_gate/p2047_step8_wide_triage_20260602T100725Z.json`.
23. Step 9 catalog ranking completed:
   `reports/optuna_catalog/index/p2048_step9_catalog_ranking_20260602T100735Z.json`.
24. Step 10/11 no-forward boundary completed:
   `reports/qa_gate/p2049_full_catalog_no_forward_boundary_20260602T100745Z.json`.
25. Full catalog closeout post-sync audit:
   `reports/qa_gate/p2050_full_catalog_closeout_post_sync_audit_20260602T101019Z.json`.
26. Block-level catalog cycle setup:
   `reports/optuna_catalog/index/p2051_block_level_catalog_cycle_setup_20260602T101240Z.json`.
27. Block01 `price_volatility` narrow command set:
   `reports/optuna_catalog/index/p2052_block01_price_volatility_narrow_command_set_20260602T101347Z.json`.
28. Block01 `price_volatility` full narrow/medium/wide triage:
   `reports/qa_gate/p2063_block01_price_volatility_full_triage_20260602T102218Z.json`.
29. Block01 post-sync audit:
   `reports/qa_gate/p2064_block01_price_volatility_post_sync_audit_20260602T102259Z.json`.
30. Block02 `trend_momentum` narrow triage:
   `reports/qa_gate/p2068_block02_trend_momentum_narrow_triage_20260602T102600Z.json`.
31. Block02 `trend_momentum` medium command set and triage:
   `reports/optuna_catalog/index/p2069_block02_trend_momentum_medium_command_set_20260602T102746Z.json`;
   `reports/qa_gate/p2072_block02_trend_momentum_medium_triage_20260602T102940Z.json`.
32. Block02 `trend_momentum` wide command set and triage:
   `reports/optuna_catalog/index/p2073_block02_trend_momentum_wide_command_set_20260602T103008Z.json`;
   `reports/qa_gate/p2076_block02_trend_momentum_full_triage_20260602T103215Z.json`.
33. Block02 post-sync audit:
   `reports/qa_gate/p2077_block02_trend_momentum_post_sync_audit_20260602T103526Z.json`.
34. Block03 `volume_flow` narrow command set:
   `reports/optuna_catalog/index/p2078_block03_volume_flow_narrow_command_set_20260602T103918Z.json`.
35. Block03 `volume_flow` narrow triage:
   `reports/qa_gate/p2081_block03_volume_flow_narrow_triage_20260602T104055Z.json`.
36. Block03 `volume_flow` medium triage:
   `reports/qa_gate/p2085_block03_volume_flow_medium_triage_20260602T104430Z.json`.
37. Block03 `volume_flow` full triage:
   `reports/qa_gate/p2089_block03_volume_flow_full_triage_20260602T104655Z.json`.
38. Block03 post-sync audit:
   `reports/qa_gate/p2090_block03_volume_flow_post_sync_audit_20260602T104830Z.json`.
39. Block04 `density_profile` narrow triage:
   `reports/qa_gate/p2094_block04_density_profile_narrow_triage_20260602T105240Z.json`.
40. Block04 `density_profile` medium triage:
   `reports/qa_gate/p2098_block04_density_profile_medium_triage_20260602T105530Z.json`.
41. Block04 `density_profile` full triage:
   `reports/qa_gate/p2102_block04_density_profile_full_triage_20260602T105800Z.json`.
42. Block04 post-sync audit:
   `reports/qa_gate/p2103_block04_density_profile_post_sync_audit_20260602T105853Z.json`.
43. Block05 `structure_ta` narrow triage:
   `reports/qa_gate/p2107_block05_structure_ta_narrow_triage_20260602T110220Z.json`.
44. Block05 `structure_ta` medium triage:
   `reports/qa_gate/p2111_block05_structure_ta_medium_triage_20260602T110445Z.json`.
45. Block05 `structure_ta` full triage:
   `reports/qa_gate/p2115_block05_structure_ta_full_triage_20260602T110710Z.json`.
46. Block05 post-sync audit:
   `reports/qa_gate/p2116_block05_structure_ta_post_sync_audit_20260602T110808Z.json`.
47. Block06 `pattern` full triage:
   `reports/qa_gate/p2128_block06_pattern_full_triage_20260602T111625Z.json`.
48. Block-level catalog ranking:
   `reports/optuna_catalog/index/p2130_block_level_catalog_ranking_20260602T111745Z.json`.
49. Block-level forward boundary:
   `reports/qa_gate/p2131_block_level_forward_boundary_20260602T111745Z.json`.
50. Block-level catalog closeout post-sync audit:
   `reports/qa_gate/p2132_block_level_catalog_closeout_post_sync_audit_20260602T111822Z.json`.
51. P2079 F1/F2 forward stability command set prepared:
   `reports/optuna_catalog/index/p2133_p2079_forward_stability_command_set_20260602T112708Z.json`.
   Status: `BLOCKED_BY_DATA`; command syntax `PASS`; production/unfreeze remains blocked.
52. P2079 F1/F2 forward preflight data gate repeated:
   `reports/qa_gate/p2134_p2079_forward_preflight_data_gate_20260602T113136Z.json`.
   Status: `BLOCKED_BY_UTC_CLOSE_AND_DATA`; raw max day `2026-06-01`, core max day `2026-05-31`.
53. P2079 forward data ingest route fixed:
   `reports/qa_gate/p2135_p2079_forward_data_ingest_route_20260602T113532Z.json`.
   Status: `ROUTE_READY_WAIT_UTC_CLOSE`; no ingestion/runtime launched.
54. P2079 post-close heartbeat scheduled:
   automation id `p2079-f1-data-gate-check`, scheduled `2026-06-03 05:05` Asia/Yekaterinburg.
   Scope: only verify UTC close, ingest closed raw `2026-06-02` if needed, then F1 preflight.
55. Previous V3 TZ pointer restored after user correction:
   `reports/qa_gate/p2137_previous_tz_recovery_package_b_pointer_20260602T123736Z.json`.
   Status: `PACKAGE_B_POINTER_RESTORED`; the skipped/unclosed item is exact V3 `Package B` slot definition.
   The P2079 heartbeat was paused so forward does not auto-advance before Package B is restored.
56. Previous TZ recovery post-sync audit passed:
   `reports/qa_gate/p2138_previous_tz_recovery_post_sync_audit_20260602T123949Z.json`.
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`.
57. Timed Package B step chain fixed:
   `reports/qa_gate/p2139_package_b_timed_step_chain_20260602T124520Z.json`.
   UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`.
   TZ anchor: V3 section 7, `2026-06-02T06:52:50Z`, Package A `NO_CANDIDATE` -> exact Package B slot definition.
58. Independent agent/audit cross-check completed:
   `reports/qa_gate/p2139_independent_agent_crosscheck_20260602T125117Z.json`.
   UTC `2026-06-02T12:51:17Z`, local `2026-06-02 17:51:17 +05:00`.
   Conclusion: route is `CORRECT_WITH_BOUNDARY`; next must be read-only `P2140 inventory`, not runtime or P2079 forward.
59. `P2140` Step 1 inventory completed:
   `reports/qa_gate/p2140_v3_package_b_inventory_20260602T125900Z.json`.
   Started UTC `2026-06-02T12:45:20Z`, completed UTC `2026-06-02T12:59:00Z`.
   Status: `PASS`; old Package B artifacts are historical V2/strict only; current V3 Package B exact slots/matrices are not defined yet.
60. `P2141` Step 2 exact V3 Package B slots completed:
   `reports/qa_gate/p2141_v3_package_b_exact_slots_20260602T130000Z.json`.
   Started UTC `2026-06-02T12:59:47Z`, completed UTC `2026-06-02T13:00:00Z`.
   Status: `PASS`; slots B-H1/B-H2/B-H3 fixed; next is `P2142` matrix slices + command set/dry-run only.
61. `P2142` Step 3 matrix slices and command-set/dry-run completed:
   `reports/qa_gate/p2142_v3_package_b_command_set_20260602T130559Z.json`.
   Started UTC `2026-06-02T13:02:00Z`, completed UTC `2026-06-02T13:05:59Z`; local completed `2026-06-02 18:05:59 +05:00`.
   Status: `PASS`; 4 matrix slices generated, 18 exact commands emitted, dry-run/preflight `18/18 PASS`; next is `P2143` Package B `long_only` runtime only.
62. `P2142` post-sync checks passed:
   `reports/qa_gate/p2142_v3_package_b_post_sync_audit_20260602T130840Z.json`.
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2142 JSON/YAML parse `PASS`.
63. `P2143` Step 4 Package B `long_only` runtime completed:
   `reports/qa_gate/p2143_v3_package_b_long_only_summary_20260602T131035Z.json`.
   Started UTC `2026-06-02T13:10:35Z`, completed UTC `2026-06-02T13:15:35Z`; local completed `2026-06-02 18:15:35 +05:00`.
   Runtime `9/9 PASS`; catalog class `neutral`, accepted positive candidates `0`.
   Catalog artifact: `reports/optuna_catalog/neutral/p2143_v3_package_b_long_only_neutral_20260602T131535Z.json`.
64. `P2143` post-sync checks passed:
   `reports/qa_gate/p2143_v3_package_b_post_sync_audit_20260602T131847Z.json`.
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2143 JSON/JSONL parse `PASS`.
65. `P2144` Step 5 Package B `short_only` runtime completed:
   `reports/qa_gate/p2144_v3_package_b_short_only_summary_20260602T132020Z.json`.
   Started UTC `2026-06-02T13:20:20Z`, completed UTC `2026-06-02T13:24:20Z`; local completed `2026-06-02 18:24:20 +05:00`.
   Runtime `9/9 PASS`; catalog class `neutral`, accepted positive candidates `0`.
   Catalog artifact: `reports/optuna_catalog/neutral/p2144_v3_package_b_short_only_neutral_20260602T132420Z.json`.
66. `P2144` post-sync checks passed:
   `reports/qa_gate/p2144_v3_package_b_post_sync_audit_20260602T132701Z.json`.
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2144 JSON/JSONL parse `PASS`.
67. `P2145` Step 6 Package B unified triage completed:
   `reports/qa_gate/p2145_v3_package_b_unified_triage_20260602T132830Z.json`.
   Started UTC `2026-06-02T13:28:00Z`, completed UTC `2026-06-02T13:28:30Z`; local completed `2026-06-02 18:28:30 +05:00`.
   Result: `NO_CANDIDATE`; totals positive `0`, neutral `18`, negative `0`, infra_fail `0`.
68. `P2146` Step 7 Package B post-sync audit completed:
   `reports/qa_gate/p2146_v3_package_b_post_sync_audit_20260602T133021Z.json`.
   Started UTC `2026-06-02T13:30:00Z`, completed UTC `2026-06-02T13:30:21Z`; local completed `2026-06-02 18:30:21 +05:00`.
   Status: `PASS`; text_guard/readiness/pip/artifact parse clean, readiness freeze preserved.
69. `P2147` Step 8 Package B closeout transition completed:
   `reports/qa_gate/p2147_v3_package_b_closeout_transition_20260602T133330Z.json`.
   Started UTC `2026-06-02T13:33:00Z`, completed UTC `2026-06-02T13:33:30Z`; local completed `2026-06-02 18:33:30 +05:00`.
   Decision: `GO_TO_FINAL_V3_NO_GO_DECISION_PACKAGE`; no next runtime allowed from Package B.
70. `P2148` final V3 `NO_GO` decision package completed:
   `reports/qa_gate/p2148_v3_final_no_go_decision_20260602T133600Z.json`.
   Started UTC `2026-06-02T13:35:30Z`, completed UTC `2026-06-02T13:36:00Z`; local completed `2026-06-02 18:36:00 +05:00`.
   Final launch decision: `NO_GO`; no production-ready candidate; launch/unfreeze blocked.
71. `P2149` final V3 `NO_GO` post-sync audit completed:
   `reports/qa_gate/p2149_v3_final_no_go_post_sync_audit_20260602T133845Z.json`.
   Started UTC `2026-06-02T13:38:20Z`, completed UTC `2026-06-02T13:38:45Z`; local completed `2026-06-02 18:38:45 +05:00`.
   Status: `PASS`; V3 chain closed, readiness freeze preserved.
72. `P2150` post-V3 catalog/forward boundary selection completed:
   `reports/qa_gate/p2150_post_v3_catalog_forward_boundary_20260602T134150Z.json`.
   Started UTC `2026-06-02T13:41:20Z`, completed UTC `2026-06-02T13:41:50Z`; local completed `2026-06-02 18:41:50 +05:00`.
   Status: `ROUTE_SELECTED_WAIT_UTC_CLOSE`; next number `P2151` is blocked until `2026-06-03T00:00:00Z`.
73. `P2151` P2079 F1 data gate pre-close check completed:
   `reports/qa_gate/p2151_p2079_f1_data_gate_preclose_check_20260602T141711Z.json`.
   Started UTC `2026-06-02T14:17:00Z`, completed UTC `2026-06-02T14:17:11Z`; local completed `2026-06-02 19:17:11 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; next number `P2152` is blocked until `2026-06-03T00:00:00Z`.
74. `P2152` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2152_p2079_f1_data_gate_utc_close_recheck_20260602T142042Z.json`.
   Started UTC `2026-06-02T14:20:30Z`, completed UTC `2026-06-02T14:20:42Z`; local completed `2026-06-02 19:20:42 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; next number `P2153` is blocked until `2026-06-03T00:00:00Z`.
75. `P2153` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2153_p2079_f1_data_gate_utc_close_recheck_20260602T142319Z.json`.
   Started UTC `2026-06-02T14:23:10Z`, completed UTC `2026-06-02T14:23:19Z`; local completed `2026-06-02 19:23:19 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; next number `P2154` is blocked until `2026-06-03T00:00:00Z`.
76. `P2154` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2154_p2079_f1_data_gate_utc_close_recheck_20260602T142553Z.json`.
   Started UTC `2026-06-02T14:25:45Z`, completed UTC `2026-06-02T14:25:53Z`; local completed `2026-06-02 19:25:53 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; next number `P2155` is blocked until `2026-06-03T00:00:00Z`.
77. `P2155` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2155_p2079_f1_data_gate_utc_close_recheck_20260602T142920Z.json`.
   Started UTC `2026-06-02T14:29:02Z`, completed UTC `2026-06-02T14:29:20Z`; local completed `2026-06-02 19:29:20 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143136Z.json`, `reports/readiness/readiness_check_20260602T143136Z.json`, `pip check`, artifact parse); next number `P2156` is blocked until `2026-06-03T00:00:00Z`.
78. `P2156` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2156_p2079_f1_data_gate_utc_close_recheck_20260602T143308Z.json`.
   Started UTC `2026-06-02T14:33:00Z`, completed UTC `2026-06-02T14:33:08Z`; local completed `2026-06-02 19:33:08 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143445Z.json`, `reports/readiness/readiness_check_20260602T143445Z.json`, `pip check`, artifact parse); next number `P2157` is blocked until `2026-06-03T00:00:00Z`.
79. `P2157` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2157_p2079_f1_data_gate_utc_close_recheck_20260602T143625Z.json`.
   Started UTC `2026-06-02T14:36:20Z`, completed UTC `2026-06-02T14:36:25Z`; local completed `2026-06-02 19:36:25 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143926Z.json`, `reports/readiness/readiness_check_20260602T143925Z.json`, `pip check`, artifact parse); next number `P2158` is blocked until `2026-06-03T00:00:00Z`.
80. `P2158` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2158_p2079_f1_data_gate_utc_close_recheck_20260602T144030Z.json`.
   Started UTC `2026-06-02T14:40:23Z`, completed UTC `2026-06-02T14:40:30Z`; local completed `2026-06-02 19:40:30 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144209Z.json`, `reports/readiness/readiness_check_20260602T144207Z.json`, `pip check`, artifact parse); next number `P2159` is blocked until `2026-06-03T00:00:00Z`.
81. `P2159` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2159_p2079_f1_data_gate_utc_close_recheck_20260602T144317Z.json`.
   Started UTC `2026-06-02T14:43:10Z`, completed UTC `2026-06-02T14:43:17Z`; local completed `2026-06-02 19:43:17 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144457Z.json`, `reports/readiness/readiness_check_20260602T144456Z.json`, `pip check`, artifact parse); next number `P2160` is blocked until `2026-06-03T00:00:00Z`.
82. `P2160` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2160_p2079_f1_data_gate_utc_close_recheck_20260602T144607Z.json`.
   Started UTC `2026-06-02T14:46:00Z`, completed UTC `2026-06-02T14:46:07Z`; local completed `2026-06-02 19:46:07 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144742Z.json`, `reports/readiness/readiness_check_20260602T144742Z.json`, `pip check`, artifact parse); next number `P2161` is blocked until `2026-06-03T00:00:00Z`.
83. `P2161` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2161_p2079_f1_data_gate_utc_close_recheck_20260602T144943Z.json`.
   Started UTC `2026-06-02T14:49:38Z`, completed UTC `2026-06-02T14:49:43Z`; local completed `2026-06-02 19:49:43 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145122Z.json`, `reports/readiness/readiness_check_20260602T145121Z.json`, `pip check`, artifact parse); next number `P2162` is blocked until `2026-06-03T00:00:00Z`.
84. `P2162` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2162_p2079_f1_data_gate_utc_close_recheck_20260602T145228Z.json`.
   Started UTC `2026-06-02T14:52:21Z`, completed UTC `2026-06-02T14:52:28Z`; local completed `2026-06-02 19:52:28 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145406Z.json`, `reports/readiness/readiness_check_20260602T145405Z.json`, `pip check`, artifact parse); next number `P2163` is blocked until `2026-06-03T00:00:00Z`.
85. `P2163` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2163_p2079_f1_data_gate_utc_close_recheck_20260602T145522Z.json`.
   Started UTC `2026-06-02T14:55:15Z`, completed UTC `2026-06-02T14:55:22Z`; local completed `2026-06-02 19:55:22 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145702Z.json`, `reports/readiness/readiness_check_20260602T145701Z.json`, `pip check`, artifact parse); next number `P2164` is blocked until `2026-06-03T00:00:00Z`.
86. `P2164` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2164_p2079_f1_data_gate_utc_close_recheck_20260602T150019Z.json`.
   Started UTC `2026-06-02T15:00:19Z`, completed UTC `2026-06-02T15:00:19Z`; local completed `2026-06-02 20:00:19 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150225Z.json`, `reports/readiness/readiness_check_20260602T150225Z.json`, `pip check`, artifact parse); next number `P2165` is blocked until `2026-06-03T00:00:00Z`.
87. `P2165` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2165_p2079_f1_data_gate_utc_close_recheck_20260602T150436Z.json`.
   Started UTC `2026-06-02T15:04:36Z`, completed UTC `2026-06-02T15:04:36Z`; local completed `2026-06-02 20:04:36 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150617Z.json`, `reports/readiness/readiness_check_20260602T150617Z.json`, `pip check`, artifact parse); next number `P2166` is blocked until `2026-06-03T00:00:00Z`.
88. `P2166` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2166_p2079_f1_data_gate_utc_close_recheck_20260602T150732Z.json`.
   Started UTC `2026-06-02T15:07:32Z`, completed UTC `2026-06-02T15:07:32Z`; local completed `2026-06-02 20:07:32 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150915Z.json`, `reports/readiness/readiness_check_20260602T150915Z.json`, `pip check`, artifact parse); next number `P2167` is blocked until `2026-06-03T00:00:00Z`.
89. `P2167` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2167_p2079_f1_data_gate_utc_close_recheck_20260602T151030Z.json`.
   Started UTC `2026-06-02T15:10:30Z`, completed UTC `2026-06-02T15:10:30Z`; local completed `2026-06-02 20:10:30 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151314Z.json`, `reports/readiness/readiness_check_20260602T151314Z.json`, `pip check`, artifact parse); next number `P2168` is blocked until `2026-06-03T00:00:00Z`.
90. `P2168` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2168_p2079_f1_data_gate_utc_close_recheck_20260602T151532Z.json`.
   Started UTC `2026-06-02T15:15:32Z`, completed UTC `2026-06-02T15:15:32Z`; local completed `2026-06-02 20:15:32 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151714Z.json`, `reports/readiness/readiness_check_20260602T151713Z.json`, `pip check`, artifact parse); next number `P2169` is blocked until `2026-06-03T00:00:00Z`.
91. `P2169` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2169_p2079_f1_data_gate_utc_close_recheck_20260602T151826Z.json`.
   Started UTC `2026-06-02T15:18:26Z`, completed UTC `2026-06-02T15:18:26Z`; local completed `2026-06-02 20:18:26 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152005Z.json`, `reports/readiness/readiness_check_20260602T152004Z.json`, `pip check`, artifact parse); next number `P2170` is blocked until `2026-06-03T00:00:00Z`.
92. `P2170` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2170_p2079_f1_data_gate_utc_close_recheck_20260602T152120Z.json`.
   Started UTC `2026-06-02T15:21:20Z`, completed UTC `2026-06-02T15:21:20Z`; local completed `2026-06-02 20:21:20 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152306Z.json`, `reports/readiness/readiness_check_20260602T152305Z.json`, `pip check`, artifact parse); next number `P2171` is blocked until `2026-06-03T00:00:00Z`.
93. `P2171` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2171_p2079_f1_data_gate_utc_close_recheck_20260602T152559Z.json`.
   Started UTC `2026-06-02T15:25:59Z`, completed UTC `2026-06-02T15:25:59Z`; local completed `2026-06-02 20:25:59 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152826Z.json`, `reports/readiness/readiness_check_20260602T152825Z.json`, `pip check`, artifact parse); next number `P2172` is blocked until `2026-06-03T00:00:00Z`.
94. `P2172` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2172_p2079_f1_data_gate_utc_close_recheck_20260602T152940Z.json`.
   Started UTC `2026-06-02T15:29:40Z`, completed UTC `2026-06-02T15:29:40Z`; local completed `2026-06-02 20:29:40 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153127Z.json`, `reports/readiness/readiness_check_20260602T153126Z.json`, `pip check`, artifact parse); next number `P2173` is blocked until `2026-06-03T00:00:00Z`.
95. `P2173` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2173_p2079_f1_data_gate_utc_close_recheck_20260602T153242Z.json`.
   Started UTC `2026-06-02T15:32:42Z`, completed UTC `2026-06-02T15:32:42Z`; local completed `2026-06-02 20:32:42 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153429Z.json`, `reports/readiness/readiness_check_20260602T153428Z.json`, `pip check`, artifact parse); next number `P2174` is blocked until `2026-06-03T00:00:00Z`.
96. `P2174` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2174_p2079_f1_data_gate_utc_close_recheck_20260602T153532Z.json`.
   Started UTC `2026-06-02T15:35:32Z`, completed UTC `2026-06-02T15:35:32Z`; local completed `2026-06-02 20:35:32 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153717Z.json`, `reports/readiness/readiness_check_20260602T153716Z.json`, `pip check`, artifact parse); next number `P2175` is blocked until `2026-06-03T00:00:00Z`.
97. `P2175` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2175_p2079_f1_data_gate_utc_close_recheck_20260602T153821Z.json`.
   Started UTC `2026-06-02T15:38:21Z`, completed UTC `2026-06-02T15:38:21Z`; local completed `2026-06-02 20:38:21 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154009Z.json`, `reports/readiness/readiness_check_20260602T154008Z.json`, `pip check`, artifact parse); next number `P2176` is blocked until `2026-06-03T00:00:00Z`.
98. `P2176` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2176_p2079_f1_data_gate_utc_close_recheck_20260602T154114Z.json`.
   Started UTC `2026-06-02T15:41:14Z`, completed UTC `2026-06-02T15:41:14Z`; local completed `2026-06-02 20:41:14 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154333Z.json`, `reports/readiness/readiness_check_20260602T154333Z.json`, `pip check`, artifact parse); next number `P2177` is blocked until `2026-06-03T00:00:00Z`.
99. `P2177` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2177_p2079_f1_data_gate_utc_close_recheck_20260602T154446Z.json`.
   Started UTC `2026-06-02T15:44:46Z`, completed UTC `2026-06-02T15:44:46Z`; local completed `2026-06-02 20:44:46 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154634Z.json`, `reports/readiness/readiness_check_20260602T154633Z.json`, `pip check`, artifact parse); next number `P2178` is blocked until `2026-06-03T00:00:00Z`.
100. `P2178` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2178_p2079_f1_data_gate_utc_close_recheck_20260602T154806Z.json`.
   Started UTC `2026-06-02T15:48:06Z`, completed UTC `2026-06-02T15:48:06Z`; local completed `2026-06-02 20:48:06 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155005Z.json`, `reports/readiness/readiness_check_20260602T155004Z.json`, `pip check`, artifact parse); next number `P2179` is blocked until `2026-06-03T00:00:00Z`.
101. `P2179` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2179_p2079_f1_data_gate_utc_close_recheck_20260602T155119Z.json`.
   Started UTC `2026-06-02T15:51:19Z`, completed UTC `2026-06-02T15:51:19Z`; local completed `2026-06-02 20:51:19 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155304Z.json`, `reports/readiness/readiness_check_20260602T155304Z.json`, `pip check`, artifact parse); next number `P2180` is blocked until `2026-06-03T00:00:00Z`.
102. `P2180` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2180_p2079_f1_data_gate_utc_close_recheck_20260602T155433Z.json`.
   Started UTC `2026-06-02T15:54:33Z`, completed UTC `2026-06-02T15:54:33Z`; local completed `2026-06-02 20:54:33 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155722Z.json`, `reports/readiness/readiness_check_20260602T155722Z.json`, `pip check`, artifact parse); next number `P2181` is blocked until `2026-06-03T00:00:00Z`.
103. `P2181` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2181_p2079_f1_data_gate_utc_close_recheck_20260602T155851Z.json`.
   Started UTC `2026-06-02T15:58:51Z`, completed UTC `2026-06-02T15:58:51Z`; local completed `2026-06-02 20:58:51 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160102Z.json`, `reports/readiness/readiness_check_20260602T160101Z.json`, `pip check`, artifact parse); next number `P2182` is blocked until `2026-06-03T00:00:00Z`.
104. `P2182` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2182_p2079_f1_data_gate_utc_close_recheck_20260602T160218Z.json`.
   Started UTC `2026-06-02T16:02:18Z`, completed UTC `2026-06-02T16:02:18Z`; local completed `2026-06-02 21:02:18 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160404Z.json`, `reports/readiness/readiness_check_20260602T160403Z.json`, `pip check`, artifact parse); next number `P2183` is blocked until `2026-06-03T00:00:00Z`.
105. `P2183` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2183_p2079_f1_data_gate_utc_close_recheck_20260602T160516Z.json`.
   Started UTC `2026-06-02T16:05:16Z`, completed UTC `2026-06-02T16:05:16Z`; local completed `2026-06-02 21:05:16 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160705Z.json`, `reports/readiness/readiness_check_20260602T160704Z.json`, `pip check`, artifact parse); next number `P2184` is blocked until `2026-06-03T00:00:00Z`.
106. `P2184` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2184_p2079_f1_data_gate_utc_close_recheck_20260602T160848Z.json`.
   Started UTC `2026-06-02T16:08:48Z`, completed UTC `2026-06-02T16:08:48Z`; local completed `2026-06-02 21:08:48 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161033Z.json`, `reports/readiness/readiness_check_20260602T161033Z.json`, `pip check`, artifact parse); next number `P2185` is blocked until `2026-06-03T00:00:00Z`.
107. `P2185` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2185_p2079_f1_data_gate_utc_close_recheck_20260602T161150Z.json`.
   Started UTC `2026-06-02T16:11:50Z`, completed UTC `2026-06-02T16:11:50Z`; local completed `2026-06-02 21:11:50 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161336Z.json`, `reports/readiness/readiness_check_20260602T161335Z.json`, `pip check`, artifact parse); next number `P2186` is blocked until `2026-06-03T00:00:00Z`.
108. `P2186` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2186_p2079_f1_data_gate_utc_close_recheck_20260602T161530Z.json`.
   Started UTC `2026-06-02T16:15:30Z`, completed UTC `2026-06-02T16:15:30Z`; local completed `2026-06-02 21:15:30 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161633Z.json`, `reports/readiness/readiness_check_20260602T161632Z.json`, `pip check`, artifact parse); next number `P2187` is blocked until `2026-06-03T00:00:00Z`.
109. `P2187` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2187_p2079_f1_data_gate_utc_close_recheck_20260602T161909Z.json`.
   Started UTC `2026-06-02T16:19:09Z`, completed UTC `2026-06-02T16:19:09Z`; local completed `2026-06-02 21:19:09 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161942Z.json`, `reports/readiness/readiness_check_20260602T161941Z.json`, `pip check`, artifact parse); next number `P2188` is blocked until `2026-06-03T00:00:00Z`.
110. `P2188` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2188_p2079_f1_data_gate_utc_close_recheck_20260602T162257Z.json`.
   Started UTC `2026-06-02T16:22:57Z`, completed UTC `2026-06-02T16:22:57Z`; local completed `2026-06-02 21:22:57 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162331Z.json`, `reports/readiness/readiness_check_20260602T162331Z.json`, `pip check`, artifact parse); next number `P2189` is blocked until `2026-06-03T00:00:00Z`.
111. `P2189` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2189_p2079_f1_data_gate_utc_close_recheck_20260602T162548Z.json`.
   Started UTC `2026-06-02T16:25:48Z`, completed UTC `2026-06-02T16:25:48Z`; local completed `2026-06-02 21:25:48 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162627Z.json`, `reports/readiness/readiness_check_20260602T162626Z.json`, `pip check`, artifact parse); next number `P2190` is blocked until `2026-06-03T00:00:00Z`.
112. `P2190` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2190_p2079_f1_data_gate_utc_close_recheck_20260602T163021Z.json`.
   Started UTC `2026-06-02T16:30:21Z`, completed UTC `2026-06-02T16:30:21Z`; local completed `2026-06-02 21:30:21 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163046Z.json`, `reports/readiness/readiness_check_20260602T163046Z.json`, `pip check`, artifact parse); next number `P2191` is blocked until `2026-06-03T00:00:00Z`.
113. `P2191` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2191_p2079_f1_data_gate_utc_close_recheck_20260602T163325Z.json`.
   Started UTC `2026-06-02T16:33:25Z`, completed UTC `2026-06-02T16:33:25Z`; local completed `2026-06-02 21:33:25 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163350Z.json`, `reports/readiness/readiness_check_20260602T163349Z.json`, `pip check`, artifact parse); next number `P2192` is blocked until `2026-06-03T00:00:00Z`.
114. `P2192` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2192_p2079_f1_data_gate_utc_close_recheck_20260602T163604Z.json`.
   Started UTC `2026-06-02T16:36:04Z`, completed UTC `2026-06-02T16:36:04Z`; local completed `2026-06-02 21:36:04 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163630Z.json`, `reports/readiness/readiness_check_20260602T163629Z.json`, `pip check`, artifact parse); next number `P2193` is blocked until `2026-06-03T00:00:00Z`.
115. `P2193` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2193_p2079_f1_data_gate_utc_close_recheck_20260602T163839Z.json`.
   Started UTC `2026-06-02T16:38:39Z`, completed UTC `2026-06-02T16:38:39Z`; local completed `2026-06-02 21:38:39 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163903Z.json`, `reports/readiness/readiness_check_20260602T163902Z.json`, `pip check`, artifact parse); next number `P2194` is blocked until `2026-06-03T00:00:00Z`.
116. `P2194` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2194_p2079_f1_data_gate_utc_close_recheck_20260602T164109Z.json`.
   Started UTC `2026-06-02T16:41:09Z`, completed UTC `2026-06-02T16:41:09Z`; local completed `2026-06-02 21:41:09 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164133Z.json`, `reports/readiness/readiness_check_20260602T164132Z.json`, `pip check`, artifact parse); next number `P2195` is blocked until `2026-06-03T00:00:00Z`.
117. `P2195` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2195_p2079_f1_data_gate_utc_close_recheck_20260602T164502Z.json`.
   Started UTC `2026-06-02T16:45:02Z`, completed UTC `2026-06-02T16:45:02Z`; local completed `2026-06-02 21:45:02 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164527Z.json`, `reports/readiness/readiness_check_20260602T164526Z.json`, `pip check`, artifact parse); next number `P2196` is blocked until `2026-06-03T00:00:00Z`.
118. Structural big-window command-set/dry-run completed:
   `reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json`.
   Status: `PASS`; raw policy preflight `PASS`; compile/dry-run `36/36 PASS`; no runtime started in command-set artifact.
119. Structural big-window narrow runtime started and then stopped by user request:
   `reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`.
   Status: `STOPPED_BY_USER_AND_FREEZE_RESTORED`; completed launcher commands `3`, stopped launcher commands `1`; positive candidates `0`; readiness restored to `project_ready=false`, `enforce_freeze=true`.

## In Work
First task is now a fast `1d -> 1d` calibration smoke/proof contour:
calibrate parameters on one closed 1d train window, apply those calibrated parameters on the next closed 1d test window, and verify wiring, parameter transfer, feature/hypothesis coverage, result classification, and 9-worker/`3x3` execution readiness before broader Package B/catalog execution.

The ordered roadmap is fixed in `P2029`.
Step 1 read-only wiring inventory completed as `P2030` with `PASS`.
Step 2 exact `1d -> 1d` smoke command set completed as `P2032` with `PASS`.
Step 3 smoke preflight completed as `P2034` with `PASS`.
Step 4 long_only smoke completed as `P2035`: `NEUTRAL_NO_TRADE`.
Step 5 short_only smoke completed as `P2036`: `PROVISIONAL_PLUS_GOAL_FAIL`.
Step 6 smoke triage completed as `P2037`: `GO_TO_MEDIUM_WORK`.
Step 7 medium command set completed as `P2039`: `PASS`.
Step 7 medium runtime completed as `P2040`/`P2041`: both `negative`.
Step 7 medium triage completed as `P2042`: `GO_TO_WIDE_BATTLE`.
Step 7 medium post-sync audit completed as `P2043`: `PASS`; freeze preserved.
Step 8 wide runtime completed as `P2045`/`P2046`: both `negative`.
Step 8 wide triage completed as `P2047`: `GO_TO_CATALOG_RANKING`.
Step 9 catalog ranking completed as `P2048`: `NO_FORWARD_CANDIDATE`.
Step 10/11 boundary completed as `P2049`: `NO_FORWARD_CANDIDATE_NO_PRODUCTION_GO`.
Current manual pointer: `P2195` is closed as `BLOCKED_BY_UTC_CLOSE`. Next number `P2196` is P2079 F1 data gate after UTC close; do not run ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
Final post-sync audit completed as `P2050`: `PASS`; freeze preserved.
Do not jump to Package B runtime, medium/wide expansion, or forward stability until the Package B slot definition and command set have an exit artifact/status.

Quick structural audit completed at UTC `2026-06-02T18:27:15Z`:
`reports/qa_gate/quick_structural_audit_framework_20260602T182715Z.json`.
Conclusion: the UTC-close block applies to P2079 forward/production only, not to structural catalog validation on already closed historical data. Framework status is `PASS_WITH_ROUTE_CORRECTION`: 68 feature rows, 6 blocks, 27 linked profiles, narrow/medium/wide grids, 3x3/9-worker launcher support, and block catalog `36/36 runtime OK`. Recommended next chain is a separate structural big-window command set/dry-run on closed history, while P2079 forward gate stays blocked until fresh data close.

Structural big-window command-set passed at UTC `2026-06-02T19:17:37Z`, then narrow runtime was stopped by explicit user request at UTC `2026-06-02T19:23:17Z`.
Do not resume structural runtime unless the user asks. Stop artifact:
`reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`.

After that, extend the Package B runner into the catalog workflow:
fixed slots, `3x3` process-pool profile, classification output, coverage output, and catalog index entries. `Package B` remains bounded, but results must be stored as catalog knowledge even if no launch candidate appears.

## Do Not Forget
1. Do not reopen old infinite remediation loops.
2. Do not treat old unfreeze `GO` as current permission.
3. Do not do micro-audits after every hypothesis tweak.
4. Do not open production actions while freeze is ON.
5. Use APTuna temporary unlock only for calibration runs.
6. Store run outputs as files and reference paths.
7. Do not call a positive catalog item production-ready before forward stability and decision package.
8. Negative results are not discarded; store them as calibration knowledge.

## Key Files
1. `docs/OPTUNA_GLOBAL_LAUNCH_AUDIT_2026-06-02_RU.md`
2. `docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md`
3. `docs/TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md`
4. `docs/ACTIVE_WORK_ITEMS_RU.md`
5. `docs/CHANGELOG_CHRONOLOGY_RU.md`
6. `configs/readiness.yaml`
7. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`
8. `run_optuna_v3_package_a.ps1`
9. `configs/calibration_full_matrix_v1.yaml`
10. `reports/optuna_catalog/`

## Nearest Next Step
Next allowed manual work: paused after user stop. Do not resume structural runtime unless explicitly requested. P2079 forward path remains `P2196` after `2026-06-03T00:00:00Z`, verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. P2079 runtime, F2, production, and unfreeze remain blocked.

## Previous Nearest Step
Step 7: prepare/run medium work pass only after fixing the exact medium command set. The smoke chain is штатно, but accepted positive candidates remain `0`.

## Hard Structural Audit 2026-06-02T19:16:09Z
Artifact: `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md`.
Status: `PASS_WITH_FINDINGS`.
Conclusion: Optuna/APTuna structure works, but block-level results are not proven as pure block-only strategy results. Feature rows are isolated by `optuna_switches.block_switches`, but hypotheses/trend filters remain global unless explicitly filtered. Example: `P2079` is labeled `volume_flow`, but its top strategy uses `min_max_range_revert`, which requires `structure_ta` columns `position_in_range` and `breakout_flag`.
Next decision before battle calibration: either accept current semantics as "block-feature matrix with global hypotheses" or enforce strict block purity by filtering hypothesis/trend-filter rows by active-block required columns. Recommended: strict block purity before big-window battle calibration.

## P2196A Optuna Battle Readiness Audit 2026-06-03T06:09:19Z
Artifact: `reports/qa_gate/p2196a_optuna_battle_readiness_audit_20260603T060919Z.md`.
Status: `NO_GO_FOR_PRODUCTION / GO_TO_STRICT_BLOCK_PURITY_FIX_BEFORE_BATTLE`.
Current truth: Optuna/APTuna can run structurally, 3x3/9 worker contour works, 36/36 historical block catalog runtime was OK, and 36/36 structural big-window command dry-runs passed. Production remains `NO_GO`, P2079 remains only `candidate_for_forward`, and strict block-hypothesis purity is not proven.
Data gate: UTC close for 2026-06-02 has passed, but raw/core files for `2026-06-02` and `2026-06-03` are absent in the workspace. F1 still needs ingest/preflight PASS; F2 waits for closed 2026-06-03 after `2026-06-04T00:00:00Z`.
Next number: `P2196B` strict block-purity compatibility map and filtering.

## P2196B Volume/Volatility Context Wiring 2026-06-03T06:58:21Z
Artifact: `reports/qa_gate/p2196b_volume_context_wiring_audit_20260603T065821Z.json`.
Status: `PASS_CONTEXT_WIRING / STRICT_HYPOTHESIS_FILTER_PENDING`.
Implemented: `volume_flow` and `price_volatility` are now configured as always-on market context blocks in `configs/calibration_full_matrix_v1.yaml` and all 6 catalog block matrices. `compile_optuna_space` returns `context_blocks` and `effective_feature_blocks`; runtime feature/profile selection includes context blocks; trial/report artifacts record `context_blocks`, `effective_feature_blocks`, and `feature_columns`.
Signal note: raw `volume` remains a market input, not a tunable parameter. Tunable/calibrated volume-derived context comes through `volume_flow` features such as `vol_chg`, `vol_z`, `delta_volume`, `obv_slope_5`, `mfi14`, and `vwap_distance`; rule-only signal now also uses `mfi14`, `vwap_distance`, and `delta_volume` when present.
Validation: `python -m unittest tests.test_optuna_space_constraints tests.test_optuna_search_runtime` -> `69/69 OK`; compile audit checked 7 matrices -> `PASS`.
Post-sync checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T070000Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T065959Z.json`), `pip check PASS`.
Next: continue P2196B strict block-purity compatibility by filtering hypothesis/trend rows by required columns before battle runtime.

## P2196B Strict Hypothesis Filtering 2026-06-03T10:04:04Z
Artifact: `reports/qa_gate/p2196b_strict_hypothesis_filter_full_audit_20260603T100404Z.json`.
Status: `PASS_STRICT_FILTERING`.
Implemented: `hypothesis_switches.strict_block_purity=true` in full matrix and all 6 catalog block matrices. `compile_optuna_space` now maps `trend_filter` required columns to feature blocks and allows a hypothesis only when required blocks are inside `enabled_blocks + context_blocks`; `none` remains always allowed. Runtime fallback no longer re-adds an incompatible CLI/default trend after compiled filtering.
Validation: focused tests `tests.test_optuna_space_constraints tests.test_optuna_search_runtime tests.test_backtest_fields` -> `77/77 OK`; strict compile audit full/catalog x long/short x narrow/medium/wide -> `42/42 PASS`.

## P2196C Strict Command Set Dry-Run 2026-06-03T10:05:04Z
Artifact: `reports/optuna_catalog/index/p2196c_strict_command_set_20260603T100504Z.json`.
Status: `PASS`; dry-run rows `36/36 PASS`.
Window: train `2026-05-29..2026-05-31`, test `2026-06-01`; raw preflight `PASS` at `reports/qa_gate/preflight_window_20260603T100432Z.json`.
Boundary: no Optuna runtime was launched. Next executable calibration step is `P2196D` strict P2079-equivalent `block03 volume_flow narrow long_only`, then strict battle runtime if that check is acceptable.
Residual note: full `unittest discover -s tests` has unrelated residual failures recorded in `reports/qa_gate/p2196c_unittest_discover_residuals_20260603T100559Z.json`; focused strict/battle readiness checks passed.

## P2196D Strict Runtime Calibration Start 2026-06-03T10:14:50Z
Status: `PASS_RUNTIME_OK / EXPERIMENTAL_POSITIVE`.
Command: block03 `volume_flow`, grid `narrow`, mode `long_only`, train `2026-05-29..2026-05-31`, test `2026-06-01`, 3x3/9 workers, temporary calibration unlock.
Result: launcher `OK`; best worker `w3`; best OOS `+1.5266529420731034%`; OOS trades `1`; goal `1.0%` passed by workers `w2` and `w3`.
Artifacts: best summary `reports/adaptive/long_only_pool_20260603t101450z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T101454Z.json`; top experimental card `reports/top_strategy/long_only_pool_20260603t101450z_w3/top_SOLUSDT_1m_2026-06-01_20260603T101522Z_MODE-LONG_ONLY_TF-1M_RET-+1.5267pct/top_strategy_card.json`.
Boundary: train gate did not pass, so it is `TOP_EXPERIMENTAL` only, not production/latest. For the current calibration-contour goal, this is acceptable: the block found a best positive OOS result, applied calibrated params on the next day, saved artifacts, and preserved production freeze.

## P2196E Volume Flow Narrow Short Runtime 2026-06-03T10:21:58Z
Status: `PASS_RUNTIME_OK / NO_CANDIDATE`.
Before fix: first short rerun at `2026-06-03T10:18:59Z` returned `PARTIAL_FAIL` because worker `w1` crashed on empty/unreadable search report JSON in `adaptive_auto_train.py`.
Fix: added safe `_read_json_report_with_retry` and converted unreadable search report into iteration status `search_report_read_failed` instead of worker crash. Focused tests `tests.test_adaptive_candidate_pick tests.test_optuna_space_constraints tests.test_optuna_search_runtime tests.test_backtest_fields` -> `83/83 OK`.
Retest command: block03 `volume_flow`, grid `narrow`, mode `short_only`, train `2026-05-29..2026-05-31`, test `2026-06-01`, 3x3/9 workers.
Retest result: launcher `OK`; all 3 workers exit `0`; best OOS `0%`; trades `0`; no candidate. Best summary `reports/adaptive/short_only_pool_20260603t102158z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T102202Z.json`.

## Calibration Current H006 Pattern Replay 2026-06-04T11:00:12Z
Status: `BLOCK_COMPLETE_RUNTIME_OK_NO_CANDIDATE`.
Active readable report: `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z_RU.md`.
Machine report: `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z.json`.
Fixes: `adaptive_auto_train.py` now preserves `calibration_params` by preferring full `top_candidates`, candidate signatures include `calibration_params`, and each repeat can try up to `8` current search candidates if train fails technically.
Validation: focused tests `81/81 OK`; full H006 runtime replay ran `long_only` and `short_only` through `narrow/medium/wide` on `3x9`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T110352Z.json`.
Result: all 6 launchers `OK`, all final `best_oos` have `18` selected calibration params, worker crash `0`, positive candidate `0`. Best tradeful block result: `short_only medium`, `-15.6997%`, `6` trades.
Next: move to the next block/slot by the active calibration plan only.

## H006 Grid Edge Coverage Audit Fix 2026-06-04T11:15:52Z
Status: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.
Readable report: `reports/qa_gate/h006_grid_edge_coverage_audit_fix_20260604T111552Z_RU.md`.
Fix: `optuna_search_candidate.py` now stores `calibration_params` immediately after sampling, records `calibration_forced_edges`, embeds `grid_edge_coverage_audit` into the search report, and writes `reports/optuna/<mode>/grid_edge_coverage_audit_*.json`.
Runtime smoke: H006 `pattern`, `long_only`, `narrow`, `ProcessWorkers=2`, `SearchWorkers=6`, `OptunaTrials=24`, launcher `OK`. New search report: `reports/pipeline/optuna_search_candidate_SOLUSDT_1m_20260604T111552Z.json`; edge audit: `reports/optuna/long_only/grid_edge_coverage_audit_20260604T111552Z.json`.
Validation: `py_compile PASS`; focused tests `94/94 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T111802Z.json`.
Next: either replay the required full block with the new edge audit to prove min/max on battle budget, or implement the cascade mode `wide -> medium around best -> narrow around best` for LONG and SHORT separately.

## H006 Core Grid Edge Forcing Fix 2026-06-04T11:31:02Z
Status: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.
Readable report: `reports/qa_gate/h006_core_grid_edge_forcing_fix_20260604T113102Z_RU.md`.
Fix: `optuna_search_candidate.py` now force-seeds core Optuna search parameters too: `horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`. First 5 trials force min, next 5 force max; trial attrs include `core_params`, `core_params_suggested`, `core_forced_edges`.
Runtime smoke: H006 `pattern long_only narrow`, `2x6`, `24` total trials, launcher `OK`; search report `reports/pipeline/optuna_search_candidate_SOLUSDT_1m_20260604T113102Z.json`; audit `reports/optuna/long_only/grid_edge_coverage_audit_20260604T113102Z.json`.
Result: core coverage `pass=5`, `fail=0`; profile coverage on the small smoke `pass=14`, `fail=9` as expected for low budget.
Validation: `py_compile PASS`; focused tests `94/94 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T113308Z.json`.
Next: full replay on battle budget with new audit to prove profile min/max, then cascade candidate improvement.

## H006 Full Replay Edge Coverage Pass 2026-06-04T12:39:58Z
Status: `BLOCK_COMPLETE_RUNTIME_OK_EDGE_COVERAGE_PASS_NO_CANDIDATE`.
Readable report: `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z_RU.md`.
Machine report: `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z.json`.
Final fix before replay: core names are excluded from profile audit, edge-on samples the full linked profile set, and profile edge indexing is distributed across `w1/w2/w3`.
Runtime result: H006 `pattern` replay ran LONG and SHORT separately through `narrow/medium/wide`, 3x9 profile. All six launchers returned `OK`; profile coverage `18/18` and core coverage `5/5` in every grid; worker crash `0`; positive candidate `0`.
Best results: LONG narrow `-0.6074%`, `1` trade; SHORT medium `0.0000%`, `0` trades; best tradeful SHORT wide `-20.3243%`, `10` trades.
Validation: `py_compile PASS`; focused tests `95/95 OK`.
Next: implement cascade candidate improvement `wide -> medium around best -> narrow around best`, LONG and SHORT separately.

## CASCADE_BLOCK_CALIBRATION Rule Fixed 2026-06-04T14:17:45Z
Status: `RULE_FIXED_NO_CODE_CHANGES`.
Active TZ updated: `docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`.
Active status updated: `docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md`.
Rule: one block equals one cascade; LONG and SHORT separately; `wide` first; `medium` around best tradeful `wide`; `narrow` around best tradeful `medium`.
Boundary: if `wide` has no tradeful candidate, record `NO_TRADEFUL_CANDIDATE` and move to next block. If the tradeful candidate is negative, continue cascade to measure the best available block result. Positive candidates go to positive/top candidates only, not production.
No code changes and no runtime launched.

## C001 Block 01 LONG Wide Runtime 2026-06-04T14:44:29Z
Status: `RUNTIME_OK_TRADEFUL_NEGATIVE`.
Readable report: `reports/qa_gate/c001_block01_price_volatility_long_wide_20260604T144429Z_RU.md`.
Command: `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`, `Mode=long_only`, `CalibrationGridPreset=wide`, matrix `configs/calibration_matrices/catalog_blocks/catalog_block_01_price_volatility.yaml`, `ProcessWorkers=3`, `SearchWorkers=9`, `OptunaTrials=180`.
Result: launcher `OK`, workers `3/3`, best OOS `-37.0372%`, trades `9`.
Best wide params: `min_abs_ema_gap=0.05`, `period_standard=19`, `return_lookback=18`, `rolling_window=40`, `vol_z_window=180`.
Boundary: candidate is tradeful but negative, so production remains `NO_GO`; per cascade rule continue to `medium around best`, not blind medium.
Note: `w1/w2` point to the same search report timestamp with `contour_id=w2`; likely artifact name collision. Track before relying on per-worker report uniqueness.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T144630Z.json`.

## Instrument Knobs Audit TZ 2026-06-11T10:47:35Z
Status: `ACTIVE_READ_ONLY_AUDIT`.
Active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_INSTRUMENT_KNOBS_AUDIT_2026-06-11_RU.md`.
User clarified the next route: pause runtime calibration and perform a block-by-block audit of all tunable knobs for features, indicators, hypotheses, and blocks. The audit must identify calculation parameters, signal-level lines/thresholds, LONG/SHORT logic, defaults, current config coverage, actual code usage, and missing knobs.
Boundary: do not run `C001 medium`, Optuna/APTuna runtime, forward, or production actions during this audit.
Next: start `Block 01 price_volatility instrument knobs audit`, then proceed through Blocks 02-06 only after each block is fixed/agreed.

## Block 01 Price Volatility Knobs Audit 2026-06-11T10:51:00Z
Status: `BLOCK_01_AUDIT_DRAFT`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.
Block: `price_volatility` / `Цена и волатильность`.
Current conclusion: Block 01 currently calibrates calculation windows (`return_lookback`, `rolling_window`, `period_standard`). It does not yet have explicit signal-level thresholds for price move strength, candle range, volatility regime, or ATR risk regime.
Next: agree which Block 01 signal-level knobs should be added, then proceed to `Block 02 trend_momentum`.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T105438Z.json`.

## Block 01 Live Chart Example 2026-06-11T11:02:00Z
Status: `VISUAL_AUDIT_EXAMPLE`.
Artifacts: `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.png`, `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z_RU.md`, `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.json`.
Current fact: rendered Block 01 on real SOLUSDT 1m data using C001 wide calculation params. The chart demonstrates how `ret_1`, `rolling_std_20`, `atr14`, and `hl_spread` can map to concrete actions: `LONG_ALLOWED`, `SHORT_ALLOWED`, `NO_TRADE_LOW_VOL`, `NO_TRADE_HIGH_RISK`.
Boundary: thresholds are illustrative only; no config edits and no Optuna runtime were launched.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T113003Z.json`.

## Block 01 Short Rework Visual 2026-06-11T11:34:00Z
Status: `SHORT_REWORK_VISUAL_AUDIT`.
Artifacts: `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.png`, `reports/qa_gate/block01_short_rework_chart_20260611T113400Z_RU.md`, `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.json`.
Current fact: user pointed out that the chart visually looked like a long signal while the actual price context was short. The answer is to split Block 01 SHORT logic into `SHORT_MOMENTUM` and `SHORT_AFTER_PULLBACK`.
Proposed knobs: `ret_down_context_threshold`, `ret_pullback_up_threshold`, `ret_short_confirm_threshold`, `confirm_bars`, `vol_min/max`, `atr_min/max`, `hl_spread_max`.
Boundary: no code/config changes and no runtime launches yet.

## Block 01 Parameter Range Map 2026-06-11T11:48:00Z
Status: `PARAMETER_RANGE_MAP_DRAFT`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.
Current fact: added concrete min/max/step ranges for Block 01 windows, up/down context, pullback, confirmation bars, vol/ATR/HL-spread filters, and primary ATR target/risk.
Boundary: TZ draft only; no config/code changes and no runtime launches.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T120336Z.json`.

## New Chat Handoff 2026-06-19
Status: `NEW_CHAT_HANDOFF_READY`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/HANDOFF_TO_NEW_CHAT_2026-06-19_RU.md`.
Current fact: prepared a clean packet for a new chat because this thread is too large. It says to use only `docs/CALIBRATION_NODE_CURRENT` as active source of truth, avoid old chronology, keep runtime/config/code changes paused, and continue from Block 01 `PARAMETER_RANGE_MAP_DRAFT`.
Next: in new chat, read the handoff and decide whether to mark Block 01 `AGREED/READY_FOR_CODE` or refine it, then proceed to Block 02.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260619T184109Z.json`.

## F001 Strict Passport Runtime Connected 2026-06-22T09:13:32Z
Status: `F001_STRICT_PASSPORT_CONNECTED`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/passports/features/F001_ret_1_RU.md`.
Current fact: user-provided strict F001 passport was applied to calibration/runtime. `F001_move` and `F001_thr_pct` are now linked to `ret_1` in the full matrix, Block 01 catalog matrix, and H001 feature-sweep matrix. Runtime action `F001_RET1_ALLOW` is calculated from the last closed 1m candle and blocks entries in backtest when false.
Validation: `py_compile PASS`; focused tests `25/25 OK`; Optuna runtime tests `65/65 OK`; matrix compile check PASS; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T091458Z.json`.
Next: user decision to run F001/H001 or Block 01 with this passport, or move strictly to `F002 ret_3`.

## F001 Strict LONG 1d/1d Runtime 2026-06-22T09:20:20Z
Status: `F001_LONG_1D1D_DONE_GOAL_FAIL`.
Artifact: `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`.
Current fact: ran the strict F001 passport in `long_only` using H001 feature-sweep matrix on train `2026-05-31`, OOS `2026-06-01`. Before final result, fixed `oos_evaluate.py` so final OOS preserves `RUNTIME_ACTION_COLUMNS`; validation `84 tests OK`.
Best worker: `w1`; params `F001_move=1.0`, `F001_thr_pct=0.19`, `min_abs_ema_gap=0.02`.
OOS result: `net_return_pct=-5.352332468117016`, `trades=3`, `hit_rate=0.3333333333333333`, `max_drawdown_pct=-5.833320604926396`, `goal_pass=false`.
Gate proof: `F001_RET1_ALLOW_gate_active=true`, raw `525`, after LONG mode `281`, after F001 gate `4`, entries filled `3`.
Conclusion: F001 LONG works technically but is `NO_GO` on this 1d/1d window.

## F001 Strict LONG Trade Map 2026-06-22
Status: `F001_LONG_TRADE_MAP_READY`.
Artifact: `reports/qa_gate/f001_strict_long_1d1d_trade_map_20260622T092020Z.png`.
Current fact: generated a visual QA chart for the best F001 LONG OOS worker. It shows the full day, all 3 entries, signal bars, exits, TP `+1.20%`, and SL `-0.80%`.
Conclusion: all trades closed by `timeout`; no TP/SL hit.

## F001 Strict LONG No-Timeout Runtime 2026-06-22
Status: `F001_LONG_NO_TIMEOUT_DONE_NO_GO`.
Artifact: `reports/qa_gate/f001_strict_long_no_timeout_1d1d_20260622T093702Z_RU.md`.
Chart: `reports/qa_gate/f001_strict_long_no_timeout_trade_map_20260622T093702Z.png`.
Current fact: user asked to turn off timeout. Implemented explicit switch `-DisableTimeoutExit` in the APTuna process-pool launcher and `--disable-timeout-exit` in Python search/train/OOS entrypoints. Backtest now supports `timeout_exit_enabled=false`; if TP/SL do not hit, exit reason becomes `end_of_data`.
Validation: `py_compile PASS`; `tests.test_backtest_fields`, `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_optuna_search_runtime`: `78 tests OK`.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T094448Z.json`.
Runtime: reran F001 strict LONG on train `2026-05-31`, OOS `2026-06-01`, H001 matrix, wide grid, 180 trials, `TimeoutExit=off`; launcher `OK`, workers `3/3`.
Formal best: worker `w1`, `0.0%`, `0` trades.
Best tradeful: worker `w2/w3`, `-47.79331627195255%`, `6` trades, `5` SL exits and `1` `end_of_data`.
Conclusion: timeout is off technically, but F001 LONG remains `NO_GO`; without timeout, tradeful entries mostly hold until SL.

## F001 Exit Baseline Decision 2026-06-22
Status: `EXIT_BASELINE_TIMEOUT_ON`.
Current fact: user decided to keep active calibration exits as before for cleanliness: TP, SL, and timeout by `hold_bars`.
Boundary: no-timeout mode remains available but is diagnostic only; do not pass `-DisableTimeoutExit` in baseline F001/Block 01 runs.
Active comparison artifact: `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`.

## Action Passport Calibration Rule 2026-06-22
Status: `ACTION_PASSPORT_CALIBRATION_ACTIVE`.
Artifacts: `docs/CALIBRATION_NODE_CURRENT/TZ_ACTION_PASSPORT_CALIBRATION_2026-06-22_RU.md`, `configs/calibration_action_passports.yaml`, `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`.
Current fact: user corrected the architecture: old Optuna configs/proposals mixed feature, hypothesis, runtime, risk, and exit knobs, so they are not a clean baseline. New rule is passport-first: every action must have a passport and explicit calibration/backtest subpassport.
Legacy boundary: old `calibration_full_matrix`, `catalog_blocks`, and `feature_sweep` matrices remain in repo but are `legacy/frozen` for new baseline runs.
Code guard: `src/mlbotnav/optuna_space.py` now enforces `passport_mode.allowed_calibration_params` for matrices with `passport_mode.enabled=true`.
Active F001 matrix: `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`; allowed params only `F001_move`, `F001_thr_pct`.
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`: `13 tests OK`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; YAML parse PASS; compile PASS for F001 passport matrix in `long_only` and `short_only`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T101720Z.json`.
Next: use the F001 passport-action matrix for the next F001 baseline run, then create F002 passport before any F002 calibration. Exit/dynamic-exit must get separate passports before calibration.

## F001 Passport-Action LONG Runtime 2026-06-22
Status: `F001_PASSPORT_ACTION_LONG_DONE_NO_GO`.
Artifact: `reports/qa_gate/f001_passport_action_long_1d1d_20260622T101953Z_RU.md`.
Current fact: ran clean F001 passport-action matrix `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml` in `long_only`, train `2026-05-31`, OOS `2026-06-01`, wide, 180 trials, timeout exit on.
Launcher: `OK`, workers `3/3`.
Formal best: `w3`, `0.0%`, `0` trades, not a tradeful candidate.
Best tradeful: `w1`, `F001_thr_pct=0.28`, OOS `-5.1298471326372%`, `1` trade, exit `timeout`.
Other tradeful: `w2`, `F001_thr_pct=0.10`, OOS `-28.876033596834784%`, `8` trades.
Conclusion: passport path works technically; F001 LONG remains `NO_GO`.
Open cleanup: core runtime fields are still sampled by engine defaults (`horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`). Decide whether to create a runtime/backtest subpassport or rerun with fixed single-value grids before expanding.
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T102340Z.json`.

## Block Passport Registry 2026-06-22
Status: `BLOCK_PASSPORT_REGISTRY_CONNECTED`.
Artifact: `configs/calibration_action_passports.yaml`.
Current fact: user decided to keep one main config and add passports into that config by block. Registry now has `blocks.B001..B006` with Russian names and active/planned passport slots.
Active F001: `blocks.B001.active_passports.F001`; `B001` is `price_volatility` / `Цена и волатильность`.
Planned F002: `blocks.B001.planned_passports.F002`; legacy `h002_price_volatility_ret_3.yaml` is not a baseline.
Code guard: `src/mlbotnav/optuna_space.py` validates passport matrix against registry metadata (`registry_path`, `registry_block_id`, `registry_passport_id`, `action_id`, `allowed_calibration_params`, `active_matrix_path`).
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `79 tests OK`; env override compile PASS for F001 passport matrix.
Next: add launcher `PassportModeRequired`, OOS legacy-param guard, fixed/runtime subpassport for core grids, and report fingerprint fix before expanding.

## RET_N F001-F005 Strict Passport Family 2026-06-22
Status: `RET_N_F001_F005_PASSPORTS_CONNECTED`.
User file: `C:\Users\007\Downloads\RET_N_F001_F005_strict_passports.md`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/RET_N_F001_F005_strict_passports.md`.
Current fact: B001 now has active passports F001-F005 in `configs/calibration_action_passports.yaml`; F002-F005 are no longer merely planned.
Active matrices:
1. `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`
2. `configs/calibration_matrices/passport_actions/F002_ret3_entry_filter.yaml`
3. `configs/calibration_matrices/passport_actions/F003_ret6_entry_filter.yaml`
4. `configs/calibration_matrices/passport_actions/F004_ret12_entry_filter.yaml`
5. `configs/calibration_matrices/passport_actions/F005_ret24_entry_filter.yaml`
Runtime: `dataset.py` emits F002-F005 action columns only when their own params are present, preventing accidental old-run filtering. `backtest.py` gates entries by all present `ENTRY_ACTION_ALLOW` columns and exposes `entry_action_gate_columns`.
Validation: `py_compile PASS`; focused tests `96/96 OK`; F001-F005 compile PASS; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T112135Z.json`.
Max-anchor fix: `src/mlbotnav/optuna_space.py` now preserves `max` when `step` does not land on it exactly; F003 `F003_thr_pct` compiles to `60` values and includes `1.20`. Follow-up validation: `py_compile PASS`; focused tests `98/98 OK`; F003 proof `60 0.03 [1.17, 1.19, 1.2] True`.
Next: run the next strict passport calibration by list order, likely F002 first.

## B001 RET_N Ladder Tournament 2026-06-22
Status: `B001_RET_N_LADDER_READY_SMOKE_OK`.
Current fact: user chose the ladder/tournament route for the one B001 block with five RET_N passports. Implemented `B001_RET_N_TOURNAMENT` in `configs/calibration_action_passports.yaml`.
Generator: `src/mlbotnav/b001_ret_n_ladder_tournament.py`; it creates all `31` non-empty combinations and compiles each matrix.
Runner: `APTuna/run_b001_ret_n_ladder_tournament.ps1`; it can run selected combos through existing APTuna process-pool and write a tournament JSON/MD.
Manifest artifact: `reports/qa_gate/b001_ret_n_ladder_matrices_20260622T115638Z/manifest.json`.
DryRun artifact: `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115811Z.json`.
Smoke artifact: `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115930Z.json`.
Smoke result: one LONG combo `B001_RET_N_F001`, tiny budget `6` trials, process-pool exit `0`, `best_oos` extracted. It had `0` OOS trades and is not a candidate; purpose was runner validation only.
Validation: `py_compile PASS`; focused tests `35/35 OK`; extended focused tests with Optuna runtime `83/83 OK`.
Full LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## B001 Solo Selection Decision 2026-06-22
Status: `B001_RET_N_SOLO_SELECTION_ONLY`.
Current fact: full 31-combo LONG run completed at `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T120806Z.json`; `31/31 ok`, but `28/31` zero OOS trades. Best combo `F002+F004` had only `1` trade, `+0.7845424236948562%` at `10x`, timeout exit, no TP hit, so `NO_CANDIDATE`.
Decision: do not use expanded in-block combination tournament as baseline. B001 baseline now means solo selection only: F001, F002, F003, F004, F005 separately, promote at most one best solo feature if tradeful/non-negative.
Runner guard: `APTuna/run_b001_ret_n_ladder_tournament.ps1` defaults to `EndIndex=5`; `EndIndex > 5` is blocked unless `-EnableCombinationTournament` is passed. Combination mode is diagnostic-only.
Validation: default dry-run selected `5` solo rows; `EndIndex=31` blocked without diagnostic flag; `py_compile PASS`; focused tests `35/35 OK`.

## MACD F013-F015 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/macd_f013_f015_long_short_audit_20260622T151954Z_RU.md`.
Current fact: added B007 `MACD импульс` with F013 `macd_line_1m`, F014 `macd_signal_1m`, F015 `macd_hist_1m`; each is a separate solo `ENTRY_FILTER` passport.
Important fix: before accepting results, fixed Optuna study contamination by adding `space_signature` into `run_signature`. Old pre-fix MACD runs reused stale trials from other passport matrices and were discarded.
Clean LONG/SHORT result:
1. F013 LONG `0.000000%`, trades `0`; F013 SHORT `-18.625751%`, trades `6`.
2. F014 LONG `-2.977908%`, trades `3`; F014 SHORT `-20.546537%`, trades `6`.
3. F015 LONG `-4.992098%`, trades `1`; F015 SHORT `-5.883887%`, trades `1`.
All tradeful exits were `timeout`, wins `0`; final `NO_GO`.
Validation: `py_compile PASS`; focused tests `112/112 OK`; YAML parse PASS; matrix compile PASS; selected params isolation PASS; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T152122Z.json`.

## F016 ADX14 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/f016_adx14_long_short_audit_20260622T153403Z_RU.md`.
Current fact: added B008 `ADX14 сила тренда` with F016 `adx14_1m`; action params are only `F016_cmp` and `F016_level`; output is `F016_ADX14_ALLOW`.
Clean LONG/SHORT result:
1. F016 LONG selected `LESS level=41`, OOS `-13.43232421418481%`, trades `3`, wins/losses `0/3`, exits `timeout=3`.
2. F016 SHORT selected `LESS level=28`, OOS `-28.526707456698695%`, trades `13`, wins/losses `1/12`, exits `timeout=13`.
Gate fact: final OOS reports show `entry_action_gate_active=true` and `entry_action_gate_columns=['F016_ADX14_ALLOW']`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `114/114 OK`; YAML parse PASS; matrix compile PASS for `long_only` and `short_only`.

## STOCH F017-F018 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/stoch_f017_f018_long_short_audit_20260622T154340Z_RU.md`.
Current fact: added B009 `Stochastic 14 K/D` with combined F017_F018 `stochastic_14_1m`; output is `F017_F018_STOCH14_ALLOW`.
Clean LONG/SHORT result:
1. F017_F018 LONG effective params `LEVEL K LESS level=72`, OOS `-84.05333161848922%`, trades `51`, wins/losses `2/49`, exits `timeout=50`, `sl=1`.
2. F017_F018 SHORT effective params `KD_CROSS UP LOW low=40 high=60 gap=0`, OOS `-17.53680624691214%`, trades `6`, wins/losses `0/6`, exits `timeout=6`.
Gate fact: final OOS reports show `entry_action_gate_active=true` and `entry_action_gate_columns=['F017_F018_STOCH14_ALLOW']`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `116/116 OK`; YAML parse PASS; matrix compile PASS for `long_only` and `short_only`.

## VOLUME F019-F021 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/volume_f019_f021_long_short_audit_20260622T160207Z_RU.md`.
Current fact: added B010 `Объем и поток` with F019 `vol_chg_1m`, F020 `vol_z_20_1m`, F021 `delta_volume_1m`; baseline selection remains solo feature only.
Fix applied: F021 `TRUE_DELTA` now requires `buy_volume`/`sell_volume`; absent side-volume columns produce no signal instead of falling back to proxy. Pre-fix F021 runs were discarded.
Clean LONG/SHORT result:
1. F019 LONG `UP thr=105%`, OOS `-57.151405%`, trades `26`; F019 SHORT `DOWN thr=10%`, OOS `-11.835584%`, trades `4`.
2. F020 LONG `HIGH z=3.6`, OOS `0%`, trades `0`; F020 SHORT `HIGH z=0.5`, OOS `-25.290896%`, trades `9`.
3. F021 LONG `PROXY_DELTA SELL thr=50%`, OOS `-77.699906%`, trades `37`; F021 SHORT `TRUE_DELTA BUY thr=5%`, OOS `0%`, trades `0`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `118/118 OK`; YAML parse PASS; matrix compile PASS for all F019-F021.

## F022 OBV Slope 5 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/f022_obv_slope5_long_short_audit_20260622T162356Z_RU.md`.
Current fact: added B011 `OBV slope 5` with solo passport F022 `obv_slope_5_1m`; output is `F022_OBVSLOPE5_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F022_obv_slope5_1m_entry_filter.yaml`.
Runtime/backtest: dataset computes F022 by passport formula `(OBV - OBV.shift(5)) / SMA(volume,20)` and backtest gates entries by the present `F022_OBVSLOPE5_ALLOW` column.
Clean LONG/SHORT result:
1. F022 LONG `UP thr=7.2`, OOS `0.000000%`, trades `0`.
2. F022 SHORT `DOWN thr=8.2`, OOS `-17.479067%`, trades `3`, wins/losses `0/3`, exits `timeout=2`, `sl=1`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `120/120 OK`; matrix compile PASS for LONG/SHORT; launcher post-audit `text_guard PASS`.

## F023 MFI14 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/f023_mfi14_long_short_audit_20260622T163809Z_RU.md`.
Current fact: added B012 `MFI14` with combined solo passport F023 `mfi14_1m`; output is `F023_MFI14_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F023_mfi14_1m_combined_entry_filter.yaml`.
Runtime/backtest: dataset computes F023 LEVEL/CROSS_LEVEL over MFI14 and backtest gates entries by the present `F023_MFI14_ALLOW` column.
Clean LONG/SHORT result:
1. F023 LONG `LEVEL GREATER level=88`, OOS `-4.474397%`, trades `1`, wins/losses `0/1`, exits `timeout=1`.
2. F023 SHORT `LEVEL LESS level=81`, OOS `-20.546537%`, trades `6`, wins/losses `0/6`, exits `timeout=6`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `122/122 OK`; matrix compile PASS for LONG/SHORT; launcher post-audit `text_guard PASS`.

## DENSITY/VPOC Block A F025/F029/F033/F034 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/density_vpoc_block_a_f025_f029_f033_f034_audit_20260622T165812Z_RU.md`.
Current fact: user supplied `DENSITY_VPOC_F025_F034_3BLOCK_FIXED_COMMENTS.md`; per passport rule, only Block A `VPOC_CORE` was run now.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/DENSITY_VPOC_F025_F034_3BLOCK_FIXED_COMMENTS.md`.
Registry: `configs/calibration_action_passports.yaml`, `B013`.
Active Block A matrices: `F025_vpocdist60_entry_filter.yaml`, `F029_vpocdist240_entry_filter.yaml`, `F033_vpocdrift20_entry_filter.yaml`, `F034_clusterratio_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F025 LONG `-60.069331%/20 trades`; F025 SHORT `-6.778638%/3 trades`.
2. F029 LONG `0.000000%/0 trades`; F029 SHORT `-18.625751%/6 trades`.
3. F033 LONG `-14.115533%/4 trades`; F033 SHORT `-3.624721%/1 trade`.
4. F034 LONG `0.000000%/0 trades`; F034 SHORT `-10.692022%/3 trades`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F033 SHORT but still negative.
Validation: `py_compile PASS`; focused tests `124/124 OK`; matrix compile PASS for Block A LONG/SHORT; launcher post-audit `text_guard PASS`.
Next from this passport file: Block B `ZONE_DENSITY` (`F026`, `F027`, `F030`, `F031`), then Block C `VPOC_STRENGTH` (`F028`, `F032`).

## LEVEL/RANGE/CHANNEL Block A F035/F036/F037 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/level_range_channel_block_a_f035_f036_f037_audit_20260622T171500Z_RU.md`.
Current fact: user supplied `LEVEL_RANGE_CHANNEL_F035_F039_strict_passport.md`; per passport order, only Block A `LEVEL_A` was run now.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/LEVEL_RANGE_CHANNEL_F035_F039_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B014`.
Active Block A matrices: `F035_supportdist_entry_filter.yaml`, `F036_resdist_entry_filter.yaml`, `F037_levelstrength_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F035 LONG `-6.153364%/2 trades`; F035 SHORT `-18.625751%/6 trades`.
2. F036 LONG `-12.920893%/3 trades`; F036 SHORT `-13.301553%/4 trades`.
3. F037 LONG `0.000000%/0 trades`; F037 SHORT `-18.104190%/7 trades`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F035 LONG but still negative.
Validation: `py_compile PASS`; focused tests `126/126 OK`; matrix compile PASS for Block A LONG/SHORT; launcher post-audit `text_guard PASS`.
Next from this passport file: Block B `F038 position_in_range_1m`, then Block C `F039 trend_channel_pos_1m`.

## FIBONACCI_GRID F040/F041 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/fibonacci_grid_f040_f041_long_short_audit_20260622T173112Z_RU.md`.
Current fact: user supplied `FIBONACCI_F040_F041_anchor_grid_strict_passport_v3.md`; implemented B015 with confirmed pivot fib grid and solo action gates.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/FIBONACCI_F040_F041_anchor_grid_strict_passport_v3.md`.
Registry: `configs/calibration_action_passports.yaml`, `B015`.
Matrices: `F040_fib0382dist_entry_filter.yaml`, `F041_fib0618dist_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F040 LONG `0.000000%/0 trades`; F040 SHORT `-27.970937%/9 trades`.
2. F041 LONG `0.000000%/0 trades`; F041 SHORT `-9.615680%/4 trades`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F041 SHORT but still negative.
Validation: `py_compile PASS`; focused tests `128/128 OK`; matrix compile PASS for F040/F041 LONG/SHORT.

## ENTRY_QUALITY_CONTEXT F042-F044 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/entry_quality_context_f042_f044_long_short_audit_20260622T175033Z_RU.md`.
Current fact: user supplied `ENTRY_QUALITY_CONTEXT_F042_F044_strict_passport_v2.md`; implemented B016 with F042 `tp_context_distance_1m`, F043 `sl_context_distance_1m`, and F044 `rr_context_estimate_1m`.
Runtime/backtest: dataset emits canonical action columns plus side-aware `*_LONG`/`*_SHORT`; backtest reports canonical gate columns and applies side-specific gates by actual signal side.
Clean LONG/SHORT result:
1. F044 LONG `-1.145944%/1 trade`; F044 SHORT `-19.784205%/8 trades`.
2. F042 LONG `-17.392676%/3 trades`; F042 SHORT `0.000000%/0 trades`.
3. F043 LONG `0.000000%/0 trades`; F043 SHORT `-30.313954%/10 trades`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `130/130 OK`; matrix compile PASS for F042/F043/F044 LONG/SHORT; launcher/text_guard PASS.

## BREAKOUT_RETEST F045-F049 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b017_breakout_retest_f045_f049_audit_20260622T181600Z.md`.
Current fact: user supplied `BREAKOUT_RETEST_F045_F049_strict_passport.md`; implemented B017 `BREAKOUT_RETEST пробой/ретест`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/BREAKOUT_RETEST_F045_F049_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B017`.
Matrices: `F048_swinghighbreak_entry_filter.yaml`, `F049_swinglowbreak_entry_filter.yaml`, `F045_breakout_entry_filter.yaml`, `F047_retest_entry_filter.yaml`, `F046_falsebreak_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F048 LONG `0.000000%/0 trades`; F048 SHORT `0.000000%/0 trades`.
2. F049 LONG `-12.862590%/6 trades`; F049 SHORT `-20.254568%/4 trades`.
3. F045 LONG `0.000000%/0 trades`; F045 SHORT `-3.482265%/2 trades`.
4. F047 LONG `-11.000000%/1 trade`; F047 SHORT `-12.464525%/3 trades`.
5. F046 LONG `0.000000%/0 trades`; F046 SHORT `-5.366391%/1 trade`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F045 SHORT but still negative.
Validation: `py_compile PASS`; focused B017 tests `3/3 OK`; matrix compile PASS for F045-F049 LONG/SHORT; launcher/text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T181926Z.json`.

## MARKET_STRUCTURE F050-F052 Passport Run 2026-06-22
Status: `done / positive_test_candidate`.
Artifact: `reports/qa_gate/b018_market_structure_f050_f052_audit_20260622T183500Z.md`.
Current fact: user supplied `MARKET_STRUCTURE_F050_F052_strict_passport.md`; implemented B018 `MARKET_STRUCTURE BOS/CHOCH`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/MARKET_STRUCTURE_F050_F052_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B018`.
Matrices: `F050_bosup_entry_filter.yaml`, `F051_bosdown_entry_filter.yaml`, `F052_choch_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F050 LONG `0.000000%/0 trades`; F050 SHORT `0.000000%/0 trades`.
2. F051 LONG `0.000000%/0 trades`; F051 SHORT `+2.810523%/1 trade`, `goal_pass`.
3. F052 LONG `0.000000%/0 trades`; F052 SHORT `0.000000%/0 trades`.
Final status: `POSITIVE_TEST_CANDIDATE`; F051 SHORT params `INTERNAL`, `break_buffer_pct=0.07`, `confirm_bars=2`, `require_bias=NOT_BULLISH`. Needs follow-up validation because OOS has only one trade.
Validation: `py_compile PASS`; focused B018 tests `3/3 OK`; matrix compile PASS for F050-F052 LONG/SHORT.

## CANDLE_PATTERNS F053-F060 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b019_candle_patterns_f053_f060_audit_20260622T190530Z.md`.
Current fact: user supplied `CANDLE_PATTERNS_F053_F060_strict_passport.md`; implemented B019 `CANDLE_PATTERNS свечные паттерны`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/CANDLE_PATTERNS_F053_F060_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B019`.
Matrices: `F055_pinbull_entry_filter.yaml`, `F056_pinbear_entry_filter.yaml`, `F059_engulfbull_entry_filter.yaml`, `F060_engulfbear_entry_filter.yaml`, `F057_hammer_entry_filter.yaml`, `F058_shootingstar_entry_filter.yaml`, `F054_insidebar_entry_filter.yaml`, `F053_doji_entry_filter.yaml`.
Clean result: F055 LONG/SHORT `0%/0`; F056 LONG/SHORT `0%/0`; F059 LONG `-60.087983%/22`, SHORT `0%/0`; F060 LONG/SHORT `0%/0`; F057 LONG/SHORT `0%/0`; F058 LONG/SHORT `0%/0`; F054 LONG `0%/0`, SHORT `-8.438667%/2`; F053 LONG `-11.213252%/3`, SHORT `0%/0`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B019 tests `3/3 OK`; matrix compile PASS for F053-F060 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T190822Z.json`.

## DIVERGENCE_PATTERNS F061-F066 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b020_divergence_patterns_f061_f066_audit_20260622T193300Z.md`.
Current fact: user supplied `DIVERGENCE_PATTERNS_F061_F066_strict_passport.md`; implemented B020 `DIVERGENCE_PATTERNS дивергенции`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/DIVERGENCE_PATTERNS_F061_F066_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B020`.
Matrices: `F061_rsibulldiv_entry_filter.yaml`, `F062_rsibeardiv_entry_filter.yaml`, `F063_macdbulldiv_entry_filter.yaml`, `F064_macdbeardiv_entry_filter.yaml`, `F065_obvbulldiv_entry_filter.yaml`, `F066_obvbeardiv_entry_filter.yaml`.
Clean result: F061 LONG `-7.123789%/2`, SHORT `0%/0`; F062 LONG/SHORT `0%/0`; F063 LONG `-37.837211%/12`, SHORT `0%/0`; F064 LONG/SHORT `0%/0`; F065 LONG `-10.822526%/4`, SHORT `0%/0`; F066 LONG/SHORT `0%/0`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B020 tests `3/3 OK`; matrix compile PASS for F061-F066 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T193442Z.json`.

## PATTERN_QUALITY F067-F068 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b021_pattern_quality_f067_f068_audit_20260622T194700Z.md`.
Current fact: user supplied `PATTERN_QUALITY_F067_F068_strict_passport.md`; implemented B021 `PATTERN_QUALITY качество паттерна`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_QUALITY_F067_F068_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B021`.
Matrices: `F067_patternstrength_entry_filter.yaml`, `F068_patternage_entry_filter.yaml`.
Clean result: F067 LONG `0%/0`, F067 SHORT `-18.202040%/6`; F068 LONG `-6.153364%/2`, F068 SHORT `-59.898861%/26`.
Final status: `NO_GO`; no candidate promoted. Best non-negative result was F067 LONG with zero OOS trades.
Validation: `py_compile PASS`; focused B021 tests `3/3 OK`; matrix compile PASS for F067/F068 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T194938Z.json`.

## CHART_PATTERNS F069-F077 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b022_chart_patterns_f069_f077_audit_20260622T202100Z.md`.
Current fact: user supplied `CHART_PATTERNS_F069_F077_strict_passport.md`; implemented B022 `CHART_PATTERNS графические паттерны`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/CHART_PATTERNS_F069_F077_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B022`.
Matrices: `F077_rangeflag_entry_filter.yaml`, `F073_triangle_entry_filter.yaml`, `F074_pennant_entry_filter.yaml`, `F075_wedgerising_entry_filter.yaml`, `F076_wedgefalling_entry_filter.yaml`, `F069_doublebottom_entry_filter.yaml`, `F070_doubletop_entry_filter.yaml`, `F071_headshoulders_entry_filter.yaml`, `F072_invheadshoulders_entry_filter.yaml`.
Clean result: F077 LONG `-19.434440%/7`, SHORT `-17.890148%/3`; F073/F074/F075/F076/F071 zero-trade on both sides; F069 LONG `-49.737441%/21`, SHORT `-13.225011%/3`; F070 LONG `0%/0`, SHORT `-21.410449%/7`; F072 LONG `-6.837599%/1`, SHORT `-10.765093%/3`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F072 LONG but still negative.
Validation: `py_compile PASS`; focused B022 tests `3/3 OK`; matrix compile PASS for F069-F077 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T202309Z.json`.

## PATTERN_CONFIRMATION F078-F079 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b023_pattern_confirmation_f078_f079_audit_20260622T203700Z.md`.
Current fact: user supplied `PATTERN_CONFIRMATION_F078_F079_strict_passport(1).md`; implemented B023 `PATTERN_CONFIRMATION confirmation of existing pattern_event`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_CONFIRMATION_F078_F079_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B023`.
Matrices: `F079_patternlevelconf_entry_filter.yaml`, `F078_patternvolconf_entry_filter.yaml`.
Clean result: F079 LONG `0%/0`, F079 SHORT `0%/0`; F078 LONG `-27.682109%/7`; F078 SHORT `-7.323394%/4`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F078 SHORT but still negative.
Validation: `py_compile PASS`; focused B023 tests `3/3 OK`; matrix compile PASS for F079/F078 LONG/SHORT; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T204015Z.json`.

## PATTERN_COMPOSITE_ENTRY F080-F081 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b024_pattern_composite_entry_f080_f081_audit_20260622T205500Z.md`.
Current fact: user supplied `PATTERN_COMPOSITE_ENTRY_F080_F081_strict_passport.md`; implemented B024 `PATTERN_COMPOSITE_ENTRY kompozitnyy pattern entry`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_COMPOSITE_ENTRY_F080_F081_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B024`.
Matrices: `F080_patternlong_entry_filter.yaml`, `F081_patternshort_entry_filter.yaml`.
Runtime/backtest: dataset emits `F080_PATTERNLONG_ALLOW` and `F081_PATTERNSHORT_ALLOW`; backtest treats F080 as LONG-only and F081 as SHORT-only if both columns are present.
Clean result: F080 LONG `0%/0`; F081 SHORT `-5.359455%/1`, exit `timeout=1`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B024 tests `3/3 OK`; matrix compile PASS; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T210111Z.json`.

## PATTERN_TRADE_CONTEXT F082-F083 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b025_pattern_trade_context_f082_f083_audit_20260622T211600Z.md`.
Current fact: user supplied `PATTERN_TRADE_CONTEXT_F082_F083_strict_passport.md`; implemented B025 `PATTERN_TRADE_CONTEXT SL/TP context`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_TRADE_CONTEXT_F082_F083_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B025`.
Matrices: `F082_patternslbuf_entry_filter.yaml`, `F083_patterntpladder_entry_filter.yaml`.
Runtime/backtest: dataset emits side-aware gates `F082_PATTERNSLBUF_ALLOW_LONG/SHORT` and `F083_PATTERNTPLADDER_ALLOW_LONG/SHORT`; backtest applies side-aware action columns when present.
Clean result: F082 LONG `0%/0`; F082 SHORT `-25.094610%/7`; F083 LONG `-35.921536%/12`; F083 SHORT `-70.280106%/35`.
Final status: `NO_GO`; no candidate promoted because only non-negative run has zero trades and all tradeful runs are negative.
Validation: `py_compile PASS`; focused B025 tests `3/3 OK`; matrix compile/passport allowlist PASS; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T211551Z.json`.

## F001-F083 Passport Route Full Audit 2026-06-23
Status: `WARN_WITH_COMPLETENESS_GAPS`.
Artifact: `reports/qa_gate/f001_f083_passport_full_audit_20260623.md`.
Existing executable passport matrices are clean and isolated: `73` active/combined entries compile x `long_only/short_only` = `146` spaces, no legacy params outside allowlists.
Completeness gaps in the pre-F024 audit snapshot: F024 was open then and is closed below; `F026/F027/F028/F030/F031/F032/F038/F039` planned only; `F017/F018` combined as `F017_F018`.
Runtime/backtest warning: normal passport flow is isolated, but stale pre-existing `F*_ALLOW` columns in a DataFrame would be applied by global backtest gate discovery.
Next: close planned passports, decide F017/F018 split vs combined, and harden active action-column selection.

## F024 VWAP Distance Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f024_vwap_distance_long_short_audit_20260623T055200Z.md`.
Current fact: implemented previously open `F024` as standalone late-closure block `B026/F024`, action `F024_VWAPDIST_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F024_vwapdist_entry_filter.yaml`.
Runtime/backtest: dataset emits `F024_VWAPDIST_ALLOW` from previous closed-bar VWAP distance; backtest gate columns in both OOS reports are exactly `['F024_VWAPDIST_ALLOW']`.
Clean result: LONG `-17.894975%/8`, SHORT `0%/0`; final `NO_GO`, but the F024 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed in order to planned Density/VPOC gaps `F026/F027/F028/F030/F031/F032`, then `F038/F039`, then decide/split `F017/F018`, plus stale-action-column hardening.

## F026 Density Bin Share 60 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f026_binshare60_long_short_audit_20260623T060100Z.md`.
Current fact: implemented `B013/F026`, action `F026_BINSHARE60_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F026_binshare60_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F026_BINSHARE60_ALLOW']`.
Clean result: LONG `-1.145944%/1`, SHORT `-24.712835%/9`; final `NO_GO`, but the F026 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F027 density_cluster_share_60_1m`.

## F027 Density Cluster Share 60 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f027_clustershare60_long_short_audit_20260623T062300Z.md`.
Current fact: implemented `B013/F027`, action `F027_CLUSTERSHARE60_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F027_clustershare60_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F027_CLUSTERSHARE60_ALLOW']`.
Clean result: LONG `-6.153364%/2`, SHORT `-18.625751%/6`; final `NO_GO`, but the F027 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F028 density_vpoc_share_60_1m`.

## F028 Density VPOC Share 60 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f028_vpocshare60_long_short_audit_20260623T064000Z.md`.
Current fact: implemented `B013/F028`, action `F028_VPOCSHARE60_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F028_vpocshare60_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F028_VPOCSHARE60_ALLOW']`.
Clean result: LONG `-1.145944%/1`, SHORT `-18.625751%/6`; final `NO_GO`, but the F028 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F030 density_bin_share_240_1m`.

## F030 Density Bin Share 240 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f030_binshare240_long_short_audit_20260623T070000Z.md`.
Current fact: implemented `B013/F030`, action `F030_BINSHARE240_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F030_binshare240_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F030_BINSHARE240_ALLOW']`.
Clean result: LONG `-13.432324%/3`, selected `LESS` with `share_thr_pct=4.0`; SHORT `-24.712835%/9`, selected `LESS` with `share_thr_pct=19.0`; final `NO_GO`, but the F030 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F031 density_cluster_share_240_1m`.

## F031 Density Cluster Share 240 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f031_clustershare240_long_short_audit_20260623T071000Z.md`.
Current fact: implemented `B013/F031`, action `F031_CLUSTERSHARE240_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F031_clustershare240_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F031_CLUSTERSHARE240_ALLOW']`.
Clean result: LONG `-6.153364%/2`, selected `LESS` with `share_thr_pct=27.0`; SHORT `-55.142239%/26`, selected `LESS` with `share_thr_pct=40.0`; final `NO_GO`, but the F031 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F032 density_vpoc_share_240_1m`.

## F032 Density VPOC Share 240 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f032_vpocshare240_long_short_audit_20260623T072500Z.md`.
Current fact: implemented `B013/F032`, action `F032_VPOCSHARE240_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F032_vpocshare240_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F032_VPOCSHARE240_ALLOW']`.
Clean result: LONG `-6.153364%/2`, selected `LESS` with `share_thr_pct=20.5`; SHORT `-18.625751%/6`, selected `LESS` with `share_thr_pct=15.5`; final `NO_GO`, but the F032 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F038 position_in_range_1m`.

## F038 Position In Range Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f038_rangepose_long_short_audit_20260623T074000Z.md`.
Current fact: implemented `B014/F038`, action `F038_RANGEPOSE_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F038_rangepose_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F038_RANGEPOSE_ALLOW']`.
Clean result: LONG `-13.432324%/3`, selected `LOW` with `level=70.0`; SHORT `-4.489987%/1`, selected `HIGH` with `level=56.0`; final `NO_GO`, but the F038 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F039 trend_channel_pos_1m`.

## F039 Trend Channel Position Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f039_channelpos_long_short_audit_20260623T080500Z.md`.
Current fact: implemented `B014/F039`, action `F039_CHANNELPOS_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F039_channelpos_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F039_CHANNELPOS_ALLOW']`.
Clean result: LONG `-17.392676%/3`, selected `LOWER` with `level=40.0`, `outside_thr=45.0`; SHORT `0.000000%/0`, selected `UPPER` with `level=85.0`, `outside_thr=0.0`; final `NO_GO`, but the F039 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: planned gaps are closed; remaining decisions are `F017/F018` combined-vs-split and stale action-column hardening.
## ML Trade Dataset Stage 2.2 Passport Context 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive passport context columns before CSV write: `block_id`, `passport_id`, `action_id`, `calibration_params_json`, `entry_action_gate_columns`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Boundary: this is not full ML-ready CSV yet; trade identity starts at `2.3`, then duration/hit labels/MAE-MFE follow.

Next strict step: `2.3 Добавить trade identity`.
## ML Trade Dataset Stage 2.3 Trade Identity 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive stable trade identity columns before CSV write: `trade_id`, `entry_signal_time_utc`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Boundary: this is not full ML-ready CSV yet; duration labels start at `2.4`, then hit labels/MAE-MFE follow.

Next strict step: `2.4 Добавить duration labels`.

## B001 Single-Worker Fast Finish 2026-06-24
Status: `diagnosed / not_worker_failure`.
Artifact: `reports/qa_gate/b001_single_worker_fast_finish_audit_20260624T180000Z_RU.md`.

Checked latest run `reports/logs/optuna_pool_long_only_20260624T175647Z_w1.log`.
The single-worker profile was applied correctly: `max_threads=9`, `search_workers=9`, `workers_used=9`, `n_trials_override=42`.

The run finished in `00:00:23` because B001 family-unified strict `5/5` leaves no candles after entry-action gate. Best candidate: `EMPTY_ACTION_GATE`, `0` trades, `signal_count_after_entry_action_gates=0`.

Next: keep single-worker `1x9/9`, generate/run B001 family-unified `4/5` 1д/1д; if empty, try `3/5`. Do not promote anything to ML.

## Optuna Worker Profile Correction 2026-06-24
Status: `profile_rule_corrected`.
Artifact: `reports/qa_gate/optuna_1x9_vs_3x3_worker_audit_20260624T183000Z_RU.md`.

Important correction: `1x9/9` is not physically equivalent to the old `3x3/9` mode. Old mode starts three Python processes, each with `--max-threads 3`, `--search-workers 3`; new single-worker mode starts one Python process with `--max-threads 9`, `--search-workers 9`.

For real B001 diagnostics, use `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`. Keep `1x9/9` only when one Optuna history is explicitly needed.
## Visual Entry Signal-Entry Contract v2 2026-06-25
Статус: `dev_signal_entry_contract_ready_needs_user_visual_confirm`.

Старый `v1` manual entries помечен как `SUPERSEDED_BY_V2_SIGNAL_ENTRY_CONTRACT`; он не должен быть целью для новых scorer/runner.

Новый v2-контракт: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/manual_entries.json`.

Правило: `signal_candle_time_utc` = закрытая свеча с фитилем/дном, `target_entry_time_utc` = open следующей свечи. LONG execution price: `entry_open_price * (1 + slippage_bps / 10000)`, сейчас `slippage_bps=5`.

PNG для согласования:
1. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_overlay_2026-05-12_20260625T102817Z.png`;
2. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_zoom_panels_20260625T102849Z.png`.

Времена v2: `01:43 -> 01:44`, `04:15 -> 04:16`, `09:15 -> 09:16`, `12:34 -> 12:35`, `15:29 -> 15:30`, `16:59 -> 17:00`.

Следующий шаг: пользователь визуально подтверждает или правит v2-точки; после этого заново гонять scorer/solo/combo уже по v2.

## Visual Entry Instrument Stack Audit 2026-06-25
Статус: `dev_audit_ready_next_noise_suppression_runner`.
Аудит: `reports/final_review/visual_entry_v3/instrument_stack_audit/visual_entry_instrument_stack_audit_20260625_RU.md`.

Решение: не расширять сразу Optuna/ML. `DQ01/DQ03` оставить как high-recall карту дна (`DQ01 10/11 + 73 false`, `DQ03 11/11 + 95 false`) и следующим шагом сделать diagnostic runner `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`.

Следующий runner должен взять manual v3 и результаты `DQ01/DQ03`, посчитать паспортные голоса для manual hit и false-entry, протестировать роли context/trigger/confirm/suppress, сгруппировать сигналы в кластеры падение -> дно -> reclaim, выбрать максимум один вход на кластер и отрендерить PNG с входами.

Первый круг признаков: `F035/F038/F009/F010/F012/F017_F018/F023/F020/F055/F057/F059`. Второй круг: `F024/F025/F028/F032/F040/F041`. Третий круг: `F050/F052/F061/F063/F065`. Четвертый круг: `F069/F072/F076/F077/F078/F079/F080`, только после проверки no-lookahead для `pattern_event`.

## Visual Entry Noise Suppression Runner 2026-06-25
Статус: `dev_runner_done_no_ml`.

Добавлено:
1. `src/mlbotnav/visual_entry_noise_suppression_cluster_priority_runner.py`;
2. `tests/test_visual_entry_noise_suppression_cluster_priority_runner.py`.

DEV-прогон:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_noise_suppression_cluster_priority_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\noise_suppression_cluster_priority --render-top 8
```

Лучший результат `CP01_DQ01_CLUSTER10_SCORE12`: `9/11`, `28` false, `37` entries, precision `0.2432`, recall `0.8182`, f1 `0.3750`. Пропущены `08:26` и `17:00`.

Главный PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp01_dq01_cluster10_score12_20260625T150100Z.png`.

Проверки: py_compile PASS; новый unittest `2/2 OK`; вместе с deep runner `3/3 OK`; render test `1/1 OK`; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260625T150159Z.json`; процесс-хвостов не осталось.

Следующий шаг: не ML. Добрать `08:26` и `17:00` отдельным мягким подслоем cluster priority, не возвращаясь к шуму `DQ01/DQ03`.

## Visual Entry CP06 Recover 2026-06-25
Статус: `dev_recover_done_11_of_11_no_ml`.

`CP06_CP01_RECOVER_NOWICK_LATE_RETEST` добавлен в `src/mlbotnav/visual_entry_noise_suppression_cluster_priority_runner.py`.

Результат DEV `2026-05-12`: `11/11`, `0` missed, `28` false, `39` entries, precision `0.2821`, recall `1.0000`, f1 `0.4400`.

Recover добавил:
1. `08:25 -> 08:26`: `RECOVER_NOWICK_SUPPORT_PULLBACK` из `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP`;
2. `16:59 -> 17:00`: `RECOVER_D03_LATE_RETEST` из `DQ01_EQ01_PLUS_DEEP_RECLAIM`.

Главный PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp06_cp01_recover_nowick_late_retest_20260625T151725Z.png`.
Отчет: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_noise_suppression_cluster_priority_20260512_DEV_RU.md`.

Проверки: py_compile PASS; новый recover regression включен; `tests.test_visual_entry_noise_suppression_cluster_priority_runner` `3/3 OK`; visual-entry set `5/5 OK`; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260625T151851Z.json`; процесс-хвостов нет.

Следующий шаг: визуально согласовать PNG с пользователем. Потом без подкрутки прогнать `2026-05-13` validation и `2026-05-14` holdout. В ML ничего не передавать.

## Handoff 2026-06-29 Visual Entry RBKD V0
Текущий статус: `DEV_RBKD_V0_BUILT_TOO_NOISY_NO_ML_NEXT_SWING_SUPPORT_EVENT`.

Сделано: добавлен diagnostic runner `src/mlbotnav/visual_entry_reversal_bottom_knife_drop_runner.py` и тест `tests/test_visual_entry_reversal_bottom_knife_drop_runner.py`. Runner соблюдает контракт `signal candle -> next candle open`, `slippage_bps=5`, `lookahead=NO`, `ml_transfer_allowed=false`.

Результаты:

1. `2026-05-13`: лучший `RBKD03_PULLBACK_AFTER_RECLAIM`, `2/9` hits, `81` false, `83` entries.
2. `2026-05-14`: лучший `RBKD03_PULLBACK_AFTER_RECLAIM`, `1/17` hits, `83` false, `84` entries.

Аудит: `reports/final_review/visual_entry_v3/reversal_bottom_knife_drop/visual_entry_reversal_bottom_knife_drop_audit_20260629T090101Z_RU.md`.

Важно: слой не кандидат и не передается в ML. Следующий рабочий шаг - `SWING_SUPPORT_RETEST_EVENT_V1`: online event-state, где событие дна/ретеста открывается по прошлым свечам, внутри события берется только первый валидный вход, затем cooldown. Не возвращаться к offline cluster-winner, потому что это дает lookahead-подобный выбор.

Проверки закрытия: `py_compile PASS`; focused unittest `2/2 OK`; совместные visual-entry tests `5/5 OK`; `text_guard PASS`; зависшие `python.exe -` PID `14996` и `228` остановлены, повторный process-check пустой.
## Handoff 2026-06-29 Visual Entry SSRE V1
Текущий статус: `DEV_SSRE_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Сделано: добавлен entry-only runner `src/mlbotnav/visual_entry_swing_support_retest_event_runner.py` и тест `tests/test_visual_entry_swing_support_retest_event_runner.py`.

Контракт: ищем только входы у low/дна. Signal-свеча закрылась, вход LONG на `open` следующей свечи, `slippage_bps=5`, `lookahead=NO`, `future_trade_outcome_used=false`, `ml_transfer_allowed=false`.

Результаты:

1. `2026-05-13`: `SSRE02_TREND_DIP_FIRST_LOW_ENTRY`, `1/9` hits, `29` false.
2. `2026-05-14`: `SSRE01_SUPPORT_RETEST_FIRST_LOW_ENTRY`, `1/17` hits, `26` false.

Аудит: `reports/final_review/visual_entry_v3/swing_support_retest_event/visual_entry_swing_support_retest_event_audit_20260629T092400Z_RU.md`.

Решение: не ML, не promotion. V1 стал менее шумным, но часто входит раньше нужного пользовательского low. Следующий шаг - `SIGNIFICANT_LOW_SELECTOR_V1`: выбрать именно значимую signal-low свечу, а не первый похожий микролой в зоне. Не использовать TP/SL, будущую доходность, MFE/MAE или entry-свечу как feature.
## Handoff 2026-06-29 Fresh Strategy Overlay
Текущий статус: `DEV_FRESH_OVERLAY_DONE_ENTRY_ONLY_NO_CALIBRATION_NO_ML`.

Добавлен свежий clean overlay runner: `src/mlbotnav/visual_entry_strategy_fresh_overlay.py`.

Он заново рендерит чистый график из `source_csv`, а не использует старые картинки с разметкой. Поверх кладет ручные low-входы и 4 default strategy layers: `Support Retest`, `Trend Dip`, `Deep Knife`, `Hot Continuation`.

Аудит: `reports/final_review/visual_entry_v3/fresh_strategy_overlay/visual_entry_fresh_strategy_overlay_audit_20260629T113100Z_RU.md`.

Важно: combined PNG плотный, для работы глазами использовать отдельные PNG по стратегиям. Дефолты не кандидат и не ML. Следующий шаг - визуально выбрать живые стратегии и только потом делать грубую калибровку.
## Handoff 2026-06-29 User Red Arrows V2 Fixed
Текущий статус: `HOLDOUT_DAY_USER_RED_ARROWS_V2_FIXED_AUTO_DETECTED_NEEDS_VISUAL_CONFIRM`.

Пользователь прислал новый скрин `SOLUSDT 1m 2026-05-14` с красными стрелками. Скрин сохранен и автоматически переведен в `manual_entries.json`.

Новая база сравнения:

`reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries.json`

Контрольный PNG:

`reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries_v2_fixed_signal_entry_verify_20260629T115000Z.png`

## Handoff 2026-06-29 Significant Low Selector V1
Текущий статус: `DEV_SIGNIFICANT_LOW_SELECTOR_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Сделано: добавлен runner `src/mlbotnav/visual_entry_significant_low_selector_runner.py`, тест `tests/test_visual_entry_significant_low_selector_runner.py`, PNG/JSON/MD в `reports/final_review/visual_entry_v3/significant_low_selector`, аудит `visual_entry_significant_low_selector_audit_20260629T125000Z_RU.md`.

Итог на `17` пользовательских входах `2026-05-14`: fresh default4 `3/17`, `260` false; `SLS06` `5/17`, `71` false; `SLS05` `2/17`, `20` false; `SLS11` `9/17`, `174` false; `SLS10` `13/17`, `463` false.

Главный PNG: `reports/final_review/visual_entry_v3/significant_low_selector/visual_entry_family_overlay_2026-05-14_sls_v1_01_sls06_hot_reclaim_strict_false_control_20260629T124723Z.png`.

Решение: V1 не кандидат и не ML. Следующее действие - `LOW_CLUSTER_RANKER_V2`: выбрать один главный low внутри активной зоны по past-only признакам, без TP/SL/future return и без cooldown-сеток `30/45/60/90`.

## Handoff 2026-06-29 Low Cluster Ranker V2
Текущий статус: `DEV_LOW_CLUSTER_RANKER_V2_ENTRY_ONLY_DONE_REDUCED_FALSE_LOW_RECALL_NO_ML`.

Добавлены `src/mlbotnav/visual_entry_low_cluster_ranker_runner.py` и `tests/test_visual_entry_low_cluster_ranker_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/low_cluster_ranker/visual_entry_low_cluster_ranker_audit_20260629T133000Z_RU.md`.

Итог на `17` пользовательских входах `2026-05-14`: `LCR04` = `3/17`, `10` false; `LCR07` = `2/17`, `4` false; `LCR06` = `7/17`, `64` false.

Главный PNG: `reports/final_review/visual_entry_v3/low_cluster_ranker/visual_entry_family_overlay_2026-05-14_lcr_v2_01_lcr04_late_low_with_reclaim_cluster_20260629T132833Z.png`.

Решение: V2 не кандидат и не ML. Он доказал, что кластерный выбор режет false, но один общий режим теряет много пользовательских входов. Следующий шаг - разложить miss по режимам и строить отдельные режимные слои.

Снято `17` входов. Предыдущая авторазметка на `18` входов была кривой: один тонкий фрагмент красной линии ошибочно попал как отдельная стрелка и удален. Время снято по красным стрелкам со скрина и имеет статус `NEEDS_VISUAL_CONFIRM`, допуск временно `±1` бар. До подтверждения не использовать для ML/export/promotion.
# Handoff 2026-06-29 Regime Split Ranker V1
Текущий статус: `DEV_REGIME_SPLIT_RANKER_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_regime_split_ranker_runner.py` и тест `tests/test_visual_entry_regime_split_ranker_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/regime_split_ranker/visual_entry_regime_split_ranker_audit_20260629T134600Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/regime_split_ranker/visual_entry_family_overlay_2026-05-14_regime_split_v1_01_rsr07_structure_bos_fibo_volume_cluster_20260629T134448Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: `STRUCTURE` лучший `7/17` при `84` false, `TREND` `7/17` при `95` false, `HOT` `6/17` при `87` false, `DEEP` `2/17` при `12` false. V1 не кандидат и не ML.

Важное решение: слой переведен в online-style `first_qualified_no_future_rewrite`, чтобы будущий более сильный low не переписывал уже выбранный вход.

Следующий шаг: `REGIME_FALSE_SUPPRESSION_V2` по отдельным шумным режимам, без сделок, без TP/SL/MFE/MAE/future return и без ML.

# Handoff 2026-06-29 Regime False Suppression V2
Текущий статус: `DEV_REGIME_FALSE_SUPPRESSION_V2_ENTRY_ONLY_DONE_STILL_TOO_NOISY_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_regime_false_suppression_runner.py` и тест `tests/test_visual_entry_regime_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_regime_false_suppression_audit_20260629T135843Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_family_overlay_2026-05-14_regime_false_suppression_v2_01_fsv21_union_strict_false_control_20260629T135626Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: лучший union `FSV21` = `7/17`, `41` false; trend `FSV05` = `6/17`, `40` false; чистый deep `FSV02` = `2/17`, `4` false.

Решение: V2 не кандидат и не ML. Он полезен как suppress-диагностика, но ложных входов все еще много. Следующий шаг - `ONLINE_LOW_EVENT_QUALITY_V3`: добавить состояние low/support-события, возраст события, порядок кандидата внутри события, расстояние до event-low и suppress горячих верхних полок, без будущих данных и без сделок.

# Handoff 2026-06-29 Online Low Event Quality V3
Текущий статус: `DEV_ONLINE_LOW_EVENT_QUALITY_V3_ENTRY_ONLY_DONE_CLEANER_LOW_RECALL_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_online_low_event_quality_runner.py` и тест `tests/test_visual_entry_online_low_event_quality_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_online_low_event_quality_audit_20260629T141715Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_family_overlay_2026-05-14_online_low_event_quality_v3_01_olev20_union_event_quality_balanced_20260629T141647Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: лучший `OLEV20` = `3/17`, `7` false, `10` entries, f1 `0.2222`. Это чище V2 (`41` false), но recall низкий.

Решение: V3 не кандидат и не ML. Следующий шаг - `DEEP_RECOVERY_AND_HOT_RECALL_V4`: добирать пропущенные deep/hot/trend входы отдельными кирпичами, не расширяя чистый event-quality union обратно в шум.

# Handoff 2026-06-29 Deep Recovery And Hot Recall V4
Текущий статус: `DEV_DEEP_RECOVERY_AND_HOT_RECALL_V4_ENTRY_ONLY_DONE_BETTER_BALANCE_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_deep_recovery_hot_recall_runner.py` и тест `tests/test_visual_entry_deep_recovery_hot_recall_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_deep_recovery_hot_recall_audit_20260629T144050Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_family_overlay_2026-05-14_deep_recovery_hot_recall_v4_01_drhr20_olev20_plus_deep_recovery_20260629T144015Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: основной `DRHR20` = `5/17`, `13` false, `18` entries, f1 `0.2857`. Он ловит `03:24`, `06:42`, `12:07`, `16:53`, `17:35`.

Решение: V4 не кандидат и не ML, но это лучший баланс текущей цепочки. Hot/trend diagnostic ловит `8/17`, но дает `43` false, поэтому не включен в рабочий union. Следующий шаг - `HOT_TREND_FALSE_SUPPRESSION_V5`.

# Handoff 2026-06-29 Hot Trend False Suppression V5
Текущий статус: `DEV_HOT_TREND_FALSE_SUPPRESSION_V5_ENTRY_ONLY_DONE_RECALL_UP_FALSE_STILL_HIGH_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_hot_trend_false_suppression_runner.py` и тест `tests/test_visual_entry_hot_trend_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_hot_trend_false_suppression_audit_20260629T145900Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_family_overlay_2026-05-14_hot_trend_false_suppression_v5_01_htfs20_union_htfs01_hot_trend_strict_false_suppression_20260629T145736Z.png`.

Чистый hot/trend PNG: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_family_overlay_2026-05-14_hot_trend_false_suppression_v5_04_htfs01_hot_trend_strict_false_suppression_20260629T145745Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: лучший union `HTFS20_UNION_HTFS01` = `9/17`, `14` false, `23` entries, f1 `0.4500`. Чистый `HTFS01` = `4/17`, `1` false, `5` entries, precision `0.8000`.

Решение: V5 не ML-кандидат, но `HTFS01` можно оставить как чистый hot/trend-кирпич. Следующий шаг - `BASE_FALSE_SUPPRESSION_V6`: резать ложные входы базовой V4-части, не ухудшая `HTFS01`.

# Handoff 2026-06-29 Base False Suppression V6
Текущий статус: `DEV_BASE_FALSE_SUPPRESSION_V6_ENTRY_ONLY_DONE_BEST_CURRENT_ONE_DAY_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_base_false_suppression_runner.py` и тест `tests/test_visual_entry_base_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_base_false_suppression_audit_20260629T151215Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_family_overlay_2026-05-14_base_false_suppression_v6_01_bfs20_union_bfs01_base_source_split_strict_false_suppression_plus_htfs01_20260629T151147Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: лучший union `BFS20_UNION_BFS01...PLUS_HTFS01` = `9/17`, `1` false, `10` entries, f1 `0.6667`. Базовая V4-часть очищена: `BFS01` = `5/17`, `0` false.

Решение: это лучший текущий слой, но он проверен только на одном holdout-дне, поэтому `NO_ML`. Следующий шаг - прогнать V6 без изменения параметров на `2026-05-13` validation и отдельно разобрать false `18:47`.

# Handoff 2026-06-29 V6 Validation Fail
Текущий статус: `VALIDATION_FAIL_V6_DOES_NOT_GENERALIZE_NO_ML`.

V6 запущен на `2026-05-13` validation без изменения параметров.

Аудит: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_base_false_suppression_validation_audit_20260629T155000Z_RU.md`.

Главный PNG validation: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_family_overlay_2026-05-13_bfs_v6_03_u_bfs01_bss_s_fs_h01_20260629T154949Z.png`.

Результат: лучший V6 union на `2026-05-13` = `0/9`, `1` false, `1` entry. Сырой base V4 = `0/9`, `17` false.

Решение: V6 не обобщился, не ML. Первый validation-запуск падал из-за длинного имени PNG; исправлен только короткий render label, параметры стратегии не менялись.

Следующий шаг: `GENERALIZATION_V7`, разбор missed validation-целей и новый режимный слой для проверки сразу на `2026-05-13` + `2026-05-14`.
# Handoff 2026-06-29 Visual Entry NEGATIVE_CONTEXT_SUPPRESSION_V8

Статус: `NEGATIVE_CONTEXT_SUPPRESSION_V8_PARTIAL_BRICK_NO_ML`.

Добавлено:

1. `src/mlbotnav/visual_entry_negative_context_suppression_v8_runner.py`;
2. `tests/test_visual_entry_negative_context_suppression_v8_runner.py`;
3. аудит `reports/final_review/visual_entry_v3/negative_context_suppression_v8/visual_entry_negative_context_suppression_v8_audit_20260629T173500Z_RU.md`.

V8 построен как suppress-слой поверх V7, не как новый recall-режим. После агентского аудита добавлены `NCS01_SIDEWAYS_MICRO_LOW`, `NCS02_HOT_UPPER_SHELF`, `NCS03_RETEST_SERIES_SATURATION`, `NCS04_POST_IMPULSE_NO_PULLBACK`, `NCS05_WEAK_RECLAIM_NO_LOCAL_LOW`.

Итог:

1. Validation `2026-05-13`: `V8_02_HOT_CHAIN_EVENT_LOW_SUPPRESSION` = `1/9`, `0` false, `1` entry. Чистый кирпич для `08:48`.
2. Holdout `2026-05-14`: `V8_01_HOT_FIRST_NEGATIVE_SUPPRESSION` = `4/17`, `29` false, `33` entries. Лучше V7, но все еще noisy.
3. `V8_20_UNION_NEGATIVE_SUPPRESSION` не использовать: на holdout `11/17`, но `168` false.

Решение: ничего в ML не передавать. Следующий шаг `V9_BRICK_BY_BRICK_SELECTOR`: закреплять отдельные чистые кирпичи и не собирать общий union, пока каждый режим сам не выглядит чисто на PNG.

# Handoff 2026-06-29 Visual Entry GENERALIZATION_V7

Статус: `GENERALIZATION_V7_DIAGNOSTIC_FAIL_NO_ML`.

Добавлено:

1. `src/mlbotnav/visual_entry_generalization_v7_runner.py`;
2. `tests/test_visual_entry_generalization_v7_runner.py`;
3. аудит `reports/final_review/visual_entry_v3/generalization_v7/visual_entry_generalization_v7_audit_20260629T172000Z_RU.md`.

Проверено на двух днях без разных параметров:

1. Validation `2026-05-13`: best `G7_02_HOT_CHAIN_DIP_DIAG` = `1/9`, `22` false, `23` entries, f1 `0.0625`.
2. Holdout `2026-05-14`: best by f1 `G7_01_HOT_FIRST_RECLAIM_DIAG` = `4/17`, `43` false, `47` entries, f1 `0.1250`; union = `11/17`, но `203` false.

Решение: V7 не стратегия и не ML-кандидат. Он только показал, что простые hot/warm/deep режимы ловят отдельные пользовательские входы, но дают слишком много ложных микролоев.

Следующий шаг: `NEGATIVE_CONTEXT_SUPPRESSION_V8` - не расширять recall, а подавлять боковые микролои, горячие верхние полки и повторные ложные retest-серии. Контракт прежний: `signal close -> next open`, `lookahead=NO`, `5 bps`, без TP/SL/MFE/MAE/future return/entry-candle OHLCV.
# Handoff 2026-06-30 Fresh Target-Led Visual Entry Workflow

Статус: `FRESH_TARGET_LED_WORKFLOW_READY_NO_ML`.

# Handoff 2026-06-30 C02 Split/Router Current

Статус: `C02_SPLIT_ROUTER_DECISION_V0_COMPLETE_NO_SCORER_NO_ML_NO_OPTUNA`.

Работать только по fresh target-led рельсам. Старые V7/V8/V9/V10/V11, старые Optuna-переборы и ML-export не продолжать как очередь.

Завершен пункт `8.3 C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`.

Итог:
- `C02A_TRUE_DEEP_CAPITULATION_CORE`: `C02E03/M01`, `C02E04/M02`, `C02E10/M08`;
- router `SUPPORT_RETEST_LOW`: `C02E05`, `C02E06`, `C02E07`;
- router `HOT_RECLAIM_SUPPORT`: `C02E08`, `C02E11`;
- router `SWING_LOW_RECLAIM`: `C02E09`, `C02E12`;
- negative controls: `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.png`.

Следующий подпункт: `8.3.1_DESIGN_C02A_TRUE_DEEP_CAPITULATION_CORE_RULES_FROM_PAST_ONLY_FEATURES_NO_SCORER_YET`.

До завершения `8.3.1` запрещены scorer, target-lock, multi-day, Optuna, ML/export/promotion.

Поправка визуала после замечания пользователя:
- цена входа не потеряна; для `M01..M19` она лежит в target ledger, для `C02E01..C02E16` создана отдельная таблица;
- рабочие C02 визуалы теперь должны использовать `price_clarity_fix_v0`, где есть zoom-sheet, high-res full-day и SVG;
- следующие скрины обязательно должны показывать `signal`, `entry`, `entry_open_price`, `entry + 5 bps`;
- цена входа остается execution-only и запрещена как признак выбора входа.

Главный рабочий визуал C02 после фикса:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_ZOOM_SHEET_V0_20260630.png`.

C02A rules draft `8.3.1` создан без scorer:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_V0_20260630_RU.md`.

Рабочий визуал для review:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_VISUAL_V0_20260630.png`.

Следующий подпункт: `8.3.1_USER_VISUAL_REVIEW_C02A_RULES_V0_BEFORE_SCORER`. До решения пользователя scorer, target-lock, multi-day, Optuna и ML/export/promotion запрещены.

Активный новый протокол: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_FRESH_PROCESS_TZ_RU.md`.

Следующий чат должен начинать не с продолжения старых V7/V8/V9/V10/V11, а с чистого target-led процесса:

1. чистый график;
2. ручные цели `T01..T10`;
3. тип входа для каждой цели;
4. стратегия под один тип;
5. паспорт-контракт;
6. entry-only PNG/scorer;
7. target-lock;
8. Optuna только внутри готового паспорта;
9. ML только после отдельного `APPROVED_FOR_ML`.

Старые слои и отчеты использовать только как архив идей и справочные артефакты. Не брать старую хронологию как очередь задач.

Первый практический шаг нового чата: выбрать один день, подтвердить `T01..T10`, создать `target_ledger`, разложить входы по типам и выбрать первый кластер из 2-4 похожих входов.

# Handoff 2026-06-30 Fresh Target-Led Start Done

Статус: `FRESH_TARGET_LED_DAY_SELECTED_LEDGER_READY_NO_ML`.

Выбран день чистого старта: `2026-05-14`, `SOLUSDT`, `1m`, `core`.

Сделано без Optuna и без ML:
1. добавлена утилита `src/mlbotnav/visual_entry_fresh_target_ledger.py`;
2. создан чистый график без старых сигналов: `reports/final_review/visual_entry_v3/fresh_target_led/fresh_target_led_clean_chart_SOLUSDT_1m_2026-05-14_20260630T062202Z.png`;
3. создан ledger: `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10.json`;
4. создан русский отчет: `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10_RU.md`.

T01..T10 взяты из `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries.json` и имеют статус `candidate_needs_visual_confirm`. Это еще не target-lock.

Первый кластер-кандидат после visual review: `HOT_RECLAIM_SUPPORT`, точки `T07`, `T08`.

`T04` была показана пользователю на полном графике и отклонена как неподходящая точка входа. В lock и паспорт ее не включать.

`T07` исправлена пользователем: правильный signal `2026-05-14T10:42:00Z`, правильный LONG entry `2026-05-14T10:43:00Z`; старое автоположение `10:48 -> 10:49` позднее и не подходит.

`T08` исправлена по пользовательской нарисованной метке: предполагаемый signal `2026-05-14T12:00:00Z`, предполагаемый LONG entry `2026-05-14T12:01:00Z`. Нужно коротко подтвердить точное время.

Следующий исполнитель должен получить confirm по `T08 = 12:01` или поправить ее. Старые V7/V8/V9/V10/V11 не продолжать как очередь задач.

Рельсы fresh target-led процесса зафиксированы: `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_RAILS_RU.md`. Работать до результата по ним: confirm целей -> один кластер -> паспорт -> entry-only PNG/scorer -> lock -> только потом Optuna/ML-gate.
# Handoff 2026-06-30 Fresh Target-Led User Marked Order

Статус: `USER_MARKED_DEVELOPMENT_ORDER_NEEDS_ZOOM_CONFIRM_NO_ML`.

Новый источник порядка разработки: пользовательский full-day скрин с красными прямоугольниками. Работать слева направо по `M01..M15`, а не пытаться добить ровно 10 точек из старого `T01..T10`.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M01_user_marked_order_zoom_signal_0323_entry_0324.png`.

`T08` подтверждена пользователем: signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`, статус `gold_user_visual_confirmed`.

Следующий шаг: показать `M01` zoom-кандидат `signal 03:23 -> LONG entry 03:24` и принять ручное решение `подходит / не подходит / сдвинуть`.

Запреты сохраняются: без Optuna до паспорта, без ML/export/promotion до `APPROVED_FOR_ML`, не продолжать старые V7/V8/V9/V10/V11 как очередь задач.
# Handoff 2026-07-01 Dataset Base V1 After Unlabeled15 Feedback

Статус: `TARGET_LED_DATASET_BASE_V1_AFTER_UNLABELED15_FEEDBACK_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA`.

Пользователь уточнил спорный лист из `15` кандидатов:

- `LA018`, `LA020` — принять как нормальные входы;
- остальные текущие авто-точки — слабые/некорректные/мимо и должны быть negative по текущему entry;
- где на пользовательском скрине были красные стрелки, новая точка не внесена автоматически, потому что нужна точная минута через отдельный zoom/time.

Актуальные артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v1_after_unlabeled15_feedback_v1/TARGET_LED_UNLABELED15_USER_FEEDBACK_V1_20260701.csv`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v1_after_unlabeled15_feedback_v1/TARGET_LED_DATASET_BASE_V1_AFTER_UNLABELED15_FEEDBACK_20260701.csv`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v1_after_unlabeled15_feedback_v1/TARGET_LED_UNLABELED15_USER_FEEDBACK_V1_ON_CHART_20260701.png`.

Счетчики V1: `107` всего, `28` positive, `79` negative, `0` unlabeled. Не запускались ML/export/training/scorer/Optuna.
# Handoff 2026-07-01 Dataset Quality Audit V0

Статус: `TARGET_LED_DATASET_QUALITY_AUDIT_V0_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA`.

Сделан аудит базы V1 (`28` positive / `79` negative). Вывод: не строить правило по количеству совпавших блоков. `safe_core_hit_count=5/6` шумит и часто попадает в bad.

Кандидаты на следующий узкий паспорт: `SUPPORT_RETEST_LOW` и `TREND_DIP_CONTINUATION`. `LOW_ANCHOR_RECLAIM` в текущем виде не использовать как standalone allow.

Актуальный отчет: `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_quality_audit_v0/TARGET_LED_DATASET_QUALITY_AUDIT_V0_20260701_RU.md`.
# Handoff 2026-07-01 ML Dataset Ladder

Статус: `FRESH_TARGET_LED_ML_DATASET_LADDER_LOCKED_NO_ML_NO_OPTUNA`.

Пользователь попросил расписать порядок, чтобы не перепрыгивать. Лестница зафиксирована в `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_ML_DATASET_LADDER_RU.md`.

Следующий строго разрешенный подпункт: `2.1_SUPPORT_RETEST_LOW_REVIEW_SHEET_9_GOOD_16_BAD_NO_ML_NO_OPTUNA`.

Не переходить к ML, Optuna, scorer или target-lock до соответствующих этапов. После review-sheet следующий шаг только draft-паспорт `SUPPORT_RETEST_LOW`.
# Handoff 2026-07-01 SUPPORT_RETEST_LOW Review Sheet V0

Статус: `SUPPORT_RETEST_LOW_REVIEW_SHEET_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Собран review-sheet по `SUPPORT_RETEST_LOW`: `9` good и `16` bad. Рабочий PNG:

`reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_review_sheet_v0/SUPPORT_RETEST_LOW_REVIEW_SHEET_V0_9GOOD_16BAD_20260701.png`.

Следующий исполнитель должен показать PNG пользователю и получить `норм / фиксить`. До этого не делать draft-паспорт, scorer, target-lock, Optuna или ML.
# Handoff 2026-07-01 SUPPORT_RETEST_LOW Passport Draft V0

Статус: `SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Создан draft-паспорт `SUPPORT_RETEST_LOW`. Пользователь уже сказал `норм` по review-sheet `9 good / 16 bad`; теперь нужно показать passport draft и получить `норм / фиксить`.

Главный файл: `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_passport_draft_v0/SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_20260701_RU.md`.

Карточка: `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_passport_draft_v0/SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_CARD_20260701.png`.

Не переходить к scorer, target-lock, Optuna или ML без user review этого паспорта.
# Handoff 2026-07-02 SUPPORT_RETEST_LOW Entry-Only Scorer V0

Статус: `SUPPORT_RETEST_LOW_ENTRY_ONLY_SCORER_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_TARGET_LOCK`.

Entry-only seed-check V0 построен. Метрики: `9/9` good kept, `0` good missed, `8/16` bad rejected, `8/16` false entries. Это не готово к lock.

Показать пользователю PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_entry_only_scorer_v0/SUPPORT_RETEST_LOW_ENTRY_ONLY_SCORER_V0_SEED_CHECK_20260702.png`.

Следующий шаг после review: `V1_REJECT_GUARDS` по false-positive `LA033`, `LA034`, `LA041`, `LA048`, `LA065`, `T15L17`, `T15L18`, `T15L20`. Не запускать target-lock, multi-day, Optuna или ML.

# Handoff 2026-07-02 Outcome Low Miner V0

Статус: `OUTCOME_LOW_MINER_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_SCORER`.

Пользователь предложил ускоритель ручной разметки: автоматически находить значимый low, считать entry на следующей свече и показывать, где цена дошла до `+1.5%` на `1x`. Реализован отдельный outcome-miner V0.

Важно для следующего исполнителя:

- future `+1.5%` используется только как offline outcome label;
- не считать эти точки ML-датасетом, scorer, target-lock или паспортом;
- не запускать ML/export/training/Optuna;
- не продолжать автоматически старые V7/V8/V9/V10/V11.

Артефакты:

1. `src/mlbotnav/visual_entry_outcome_low_miner_v0.py`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_20260702_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_CANDIDATES_20260702.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260514_20260702.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260515_20260702.png`.

Счетчики: `2026-05-14` = `14` candidates / `5` hit; `2026-05-15` = `12` candidates / `1` hit. Следующий шаг: показать PNG пользователю и решить, оставляем ли `+1.5%` или делаем соседний тест `+0.8%/+1.0%`.

# Handoff 2026-07-02 Outcome Low Miner 1pct Comparison

Пользователь попросил попробовать `+1%`. Запущен тот же `OUTCOME_LOW_MINER_V0`, но с `--target-pct 1.0` и отдельной папкой:

`reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct`.

Счетчики:

- `2026-05-14`: `14` candidates / `7` hit;
- `2026-05-15`: `12` candidates / `3` hit.

PNG для показа:

1. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260514_20260702.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260515_20260702.png`.

Граница та же: future outcome только label для review, не feature/scorer/ML.
## Handoff 2026-07-02 Good 1pct Review Pool

Статус: `GOOD_1PCT_REVIEW_POOL_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Пользователь попросил быстрый скрипт для VS Code, который собирает значимые low-кандидаты по диапазону дат, считает вход на следующем `open`, применяет `+5bps`, проверяет `+1%` и сохраняет все в отдельную run-папку для просмотра глазами.

Реализовано:

1. `src/mlbotnav/visual_entry_good_1pct_review_pool.py`;
2. VS Code task `Visual Entry: Good 1pct Review Pool (NO ML/OPTUNA)`;
3. smoke-запуск `2026-05-13` в `reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/smoke_20260513_20260702_080455`.

Smoke-метрики: `87` кандидатов, `5` GOOD, `82` BAD. GOOD = `4` strong hit даже при `10bps`, `1` soft hit только при `0bps`.

Дополнительно прогнан mini-run W20 `2026-05-13..2026-05-15`: run_id `W20_mini_zoomfix_20260702_081003`, всего `261` кандидат, `73` GOOD, `188` BAD. По дням: `2026-05-13` = `5/87` GOOD, `2026-05-14` = `55/85` GOOD, `2026-05-15` = `13/89` GOOD.

Важно: W20 mini показал, что `+1%` outcome сам по себе слишком широкий как gold. Использовать только как быстрый visual review pool: PNG глазами, затем ручное подтверждение.

Важная граница: этот скрипт не является ML, scorer, Optuna или target-lock. Он делает review-pool и offline outcome labels для ручного отбора. Нельзя передавать CSV в ML без отдельного approved-ledger и `APPROVED_FOR_ML`.

Следующий практический шаг: запустить W18-W20 как learning pool (`2026-04-27..2026-05-17`), показать пользователю `GOOD_1PCT_REVIEW_POOL_GOOD_CLOSEUPS_PAGE_*.png` и day overview PNG, затем руками подтвердить/отклонить хорошие входы.

# Handoff 2026-07-02 DCA Risk Audit V0

Статус: `DCA_RISK_AUDIT_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_API`.

Пользователь попросил расписать следующий этап `DCA_RISK_AUDIT_V0`: понять, что делать с днями, где много `+1%` сделок висит одновременно и закрывается только поздним пампом.

Реализовано:

1. `src/mlbotnav/visual_entry_dca_risk_audit_v0.py`;
2. VS Code task `Visual Entry: DCA Risk Audit V0 (NO ML/OPTUNA/API)`;
3. run `W18_W20_dca_risk_20260702_154415`.

Входной пул: `reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/W18_W20_learning_20260702_082819`.

Основной результат:

- `21` день, `1528` записей, `573` GOOD, `955` BAD;
- all GOOD max active = `44`;
- first `10` GOOD/day max active = `10`;
- worst basket DD all GOOD = `-2.685835%`;
- selected10 содержит много `C_LATE_PUMP_DEPENDENT` (`77`) и falling-knife классов (`17` суммарно).

Главный вывод: `+1% hit` не является самодостаточным good label. Нужна risk-aware разметка: быстрые чистые отскоки отдельно, late-pump/DCA-overload/knife отдельно.

Главные PNG:

1. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_SUMMARY.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_TOP_DAY_20260502.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_TOP_DAY_20260514.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_TOP_DAY_20260511.png`.

Следующий шаг: показать пользователю PNG/таблицу и зафиксировать правила допуска в будущий датасет. Не переходить на full-history, ML/export/training/scorer/target-lock/Optuna/API до ручного review.
## Handoff 2026-07-02 Significant Low Calibration V0

Свежий рабочий этап: `SIGNIFICANT_LOW_CALIBRATION_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Контекст: пользователь указал, что текущий low-miner/GOOD_1PCT берет слишком много low подряд. Нужно калибровать значимые low, а не отдавать все `+1% hit` в будущий датасет.

Сделано:

1. добавлен `src/mlbotnav/visual_entry_significant_low_calibration_v0.py`;
2. взят DCA/userfix run `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260502_userfix_v0_20260702_180352`;
3. применен ручной feedback `DCA_RISK_AUDIT_V0_20260502_USER_FEEDBACK_V0.csv`;
4. создан run `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_20260502_v0_20260702_181433`;
5. результат: `10` keep, `10` shift-pending, `24` user-reject, `6` not-significant, `4` duplicate-basin.

Важное правило: `USER_SHIFT_PENDING_REANCHOR` не является готовой хорошей сделкой. Это место, где текущий сигнал близко, но нужно снять отдельный zoom и переставить anchor/entry на более правильный low по пользовательской стрелке.

Актуальное продолжение после пользовательской правки overview: первичный run `siglow_20260502_v0_20260702_181433` superseded ручным слоем `siglow_20260502_user_actual_v1c3_20260702_190227`.

Текущий контрольный список:

1. green keep: `LA002`, `LA015`, `LA018`, `LA021`, `LA040`, `LA050`;
2. yellow reanchor: `LA007`, `LA028`;
3. `LA048` и `LA049` отклонены;
4. `LA051` не good, он duplicate-basin reject;
5. красные reject-кресты/линии на overview сделаны тише по прозрачности.

Следующий шаг: показать пользователю актуальный V1C3 overview, собрать финальные правки по 6 green/2 yellow, затем решать параметры V1. Не запускать ML/export/training/scorer/target-lock/Optuna/API.

## Handoff 2026-07-03 Reanchor Applied V2 RA004

Статус: `SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

После сбоя/перезапуска доделан applied-layer по новой стрелке пользователя на участке `20:45-21:05 UTC`.

Новая точка:

- `RA004_USER_ENTRY_2049`;
- signal `2026-05-02T20:48:00Z`;
- entry `2026-05-02T20:49:00Z`;
- low свечи `84.05000000`;
- `entry_open=84.09000000`;
- `entry +5bps=84.13204500`.

Run:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904`

Показывать пользователю прежде всего:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502_CLOSE_ZOOM_RA004.png`

Также есть overview:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502_OVERVIEW.png`

## Handoff 2026-07-03 Manual Reanchors V0 Source Of Truth

Статус: `SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

После замечания пользователя, что на новом графике появились не те сделки, ручные reanchor-входы вынесены в отдельный источник истины:

`configs/visual_entry/manual_reanchors/SOLUSDT_1m_2026-05-02_SIGNIFICANT_LOW_MANUAL_REANCHORS_V0.json`.

Использовать его вместо старых applied V1/V2 CSV как текущую правду по точным входам. Старые run-папки остаются архивом, но не являются рабочим источником для следующих перерисовок.

Создан renderer:

`src/mlbotnav/visual_entry_manual_reanchor_review_v0.py`.

Актуальный run:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936`.

Текущие ручные строки:

1. `RA001_FROM_LA007`: confirmed, signal `03:14`, entry `03:15`, `entry +5bps=83.76186000`;
2. `RA002_PENDING_FROM_LA028`: pending, не clean good;
3. `RA003_SHIFT_LEFT_LA050`: confirmed, signal `22:24`, entry `22:25`, `entry +5bps=84.10203000`, visual low marker `84.02000000`;
4. `RA004_USER_ENTRY_2049`: confirmed, signal `20:48`, entry `20:49`, `entry +5bps=84.13204500`.

Следующий исполнитель должен показать пользователю новый `REVIEW_SHEET` и close-zoom по `RA003/RA004`. Если будет правка, менять только JSON source-of-truth и перегенерировать `manual_reanchors_v0`. Не запускать ML/export/training/scorer/target-lock/Optuna/API.

Граница: это только ручной reanchor/applied слой. Не запускать ML/export/training/scorer/target-lock/Optuna/API.

## Handoff 2026-07-03 STAS1 GOOD_1PCT anchor-next-open fix

Статус: `STAS1_GOOD_1PCT_ANCHOR_NEXT_OPEN_FIX_V0_VERIFIED_NO_ML_NO_OPTUNA`.

Пользователь вернул фокус к основному STAS1-скрипту `GOOD_1PCT_REVIEW_POOL`: нужно не плодить новые слои, а починить текущий скрипт поиска low-кандидатов. Проверка старого run `2026-05-02` показала: из `44` GOOD-сделок `12` имели вход не на следующей свече после low, а через 2-4 свечи.

Исправлено:

1. `src/mlbotnav/visual_entry_low_anchor_suggester.py`: `signal_idx` теперь равен `anchor_idx`, `entry_idx = anchor_idx + 1`;
2. старая confirmation-свеча сохраняется в `confirmation_idx`/`confirmation_time_utc` только для справки;
3. `src/mlbotnav/visual_entry_good_1pct_review_pool.py`: в CSV добавлены индексы для аудита;
4. добавлен регрессионный тест `tests/test_visual_entry_low_anchor_suggester.py`.

Контрольный run:

`STAS1_GOOD_LOW_REVIEW/runs/stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034`

Итог: `52` строки, `42` GOOD, `10` BAD, все записи имеют `entry_time_utc = anchor_time_utc + 1 minute`.

Показывать пользователю:

1. `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034/GOOD_1PCT_REVIEW_POOL_DAY_OVERVIEW_20260502.png`;
2. closeups page 01-06 из той же папки.

Следующий шаг: пользователь отмечает шум/дубли/неправильные low на новых PNG. Дальше настраивать значимость low, но не менять контракт `low -> next open +5bps`. ML/export/training/scorer/target-lock/Optuna/API запрещены.

## Handoff 2026-07-07 Codex/VS Code load audit

Статус: `CODEX_VSCODE_LOAD_AUDIT_LOCAL_FIX_APPLIED`.

Пользователь после перезагрузки увидел постоянную нагрузку CPU/RAM/disk при открытом VS Code/Codex. Проверка процессов показала активные `git add -A` от Codex, которые пытались пройти по большим локальным артефактам. Вложенных Git-репозиториев не найдено: в проекте только корневой `C:\Users\007\Desktop\MLbotNav\.git`.

Найдены тяжелые папки: `_codex_offload_20260530` около `5912 MB`, `models` около `1517 MB`, `reports` около `1070 MB`, `STAS3_PERCENT_LADDER_REVIEW` около `364 MB`, `STAS1_GOOD_LOW_REVIEW` около `149 MB`, `STAS2_MARKET_PHASE_REVIEW` около `116 MB`. Тяжелая часть STAS находится именно в `runs`.

Исправлено:

1. в `.gitignore` добавлены `STAS1_GOOD_LOW_REVIEW/runs/`, `STAS2_MARKET_PHASE_REVIEW/runs/`, `STAS3_PERCENT_LADDER_REVIEW/runs/`;
2. в `.vscode/settings.json` добавлены `files.watcherExclude`, `search.exclude`, `python.analysis.exclude` для больших data/logs/models/reports/packs/tmp/offload/STAS runs;
3. остановлены зависшие `git add -A`; `.git/index.lock` не остался.

Проверка: `git check-ignore -v` подтверждает игнор всех трех STAS `runs`, `.vscode/settings.json` валидный JSON, `git status --short --untracked-files=normal` выполняется примерно за `0.03s`. Для применения watcher-настроек в UI желательно `Developer: Reload Window` в VS Code или перезапуск VS Code.
## Handoff 2026-07-09 STAS4 combo strategies 3 days

Статус: `STAS4_COMBO_4_STRATEGIES_3D_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Пользователь попросил прогнать 4 комбинированные стратегии Stas4 на трех днях поверх Stas2 run `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_short_macro_wave_review_20260709_071233`. Старые точки Stas1/Stas2 не менялись: зеленая галочка показывает старый вход, который слой считает шумом; синяя стрелка показывает новый вход-кандидат; вход по контракту идет следующей свечой после сигнала.

Готово: `structure_ta+trend_momentum`, `structure_ta+volume_flow`, `pattern+structure_ta`, `density_profile+structure_ta` на днях `2026-05-10`, `2026-05-11`, `2026-05-12`.

Итог по 3 дням: `structure_ta+trend_momentum` = `172` галочки / `5` стрелок; `structure_ta+volume_flow` = `158` / `2`; `pattern+structure_ta` = `106` / `6`; `density_profile+structure_ta` = `72` / `11`.

Главный отчет: `STAS4_FEATURE_HYPOTHESIS_REVIEW/STAS4_COMBO_4_STRATEGIES_3D_SUMMARY_20260709_RU.md`.

Следующий шаг: пользователь открывает папку `STAS4_FEATURE_HYPOTHESIS_REVIEW` и смотрит 12 PNG глазами. Предварительно сильнейшие кандидаты: `structure_ta+trend_momentum` как максимальный фильтр шума, `structure_ta+volume_flow` как более жесткий запретный слой почти без новых стрелок. ML, Optuna, scorer, target-lock и API не запускались.
## Handoff 2026-07-11 Codex Startup Disk Load Audit

Статус: `CODEX_STARTUP_DISK_LOAD_AUDIT_READY_NO_DELETE_NO_CODE_CHANGE`.

Пользователь сообщил, что после перезагрузки компьютера и запуска Codex диск около минуты держится на `100%`, затем падает к нормальным `1..5%`. Проведен локальный аудит без удаления и переноса файлов.

Главный отчет: `docs/codex/CODEX_STARTUP_DISK_LOAD_AUDIT_20260711_RU.md`.

Вывод: текущей аварии не видно. Диск `NVMe SSD`, `Healthy`, свободно около `353.9 GB`; `git status` быстрый (`0.04..0.07s`), зависшего `git add -A` нет. Вероятная причина минутного холодного прогрева - крупная локальная история Codex и кеши: `C:\Users\007\.codex` около `13.2 GB`, включая `sessions` около `7.5 GB`, backup/archived-сессии около `4.4 GB`, `logs_2.sqlite` около `724 MB`. В проекте также лежит `_codex_offload_20260530` около `5.9 GB`.

Ничего не удалялось. Следующий безопасный шаг только после подтверждения пользователя: перенести `_codex_offload_20260530` из рабочей папки в отдельный архив вне проекта; затем отдельно решить политику старых `.codex` backup/archived-сессий.

## Handoff 2026-07-14 STAS5 V4 Human-Style Group Ranker

Статус: `STAS5_V4_GROUP_RANKER_READY_20260501_20260525_AND_FORWARD_20260526_20260530_READY`.

По явному решению пользователя снят карантин с `2026-05-15`: он входит в исправленный V4 review window `2026-05-15..2026-05-25`. Train подготовлен как `2026-05-01..2026-05-14` legacy база плюс пользовательские group-rank правки `2026-05-15..2026-05-25`.

Создано:

1. `src/mlbotnav/stas5_v4_group_rank_dataset.py` - сборка V4 train dataset с group features и guard;
2. `src/mlbotnav/stas5_v4_group_rank_train.py` - обучение V4 scorer с метриками ранжирования внутри групп;
3. `src/mlbotnav/stas5_v4_forward_group_rank_review.py` - blind forward `2026-05-26..2026-05-30` с авто-группами и V4 decision policy;
4. `tests/test_stas5_v4_group_rank_dataset.py` и `tests/test_stas5_v4_group_rank_train.py`;
5. renderer `src/mlbotnav/stas5_v2_forward_entry_review.py` теперь корректно подписывает `STAS5 V4` и `V4_GROUP_RANK_SCORE`.

Главные артефакты:

- dataset: `STAS5_ML_CORE/artifacts/v4/features/STAS5_V4_GROUP_RANK_TRAIN_DATASET_20260501_20260525.csv`;
- dataset manifest: `STAS5_ML_CORE/artifacts/v4/features/STAS5_V4_GROUP_RANK_TRAIN_DATASET_20260501_20260525.manifest.json`;
- model: `STAS5_ML_CORE/artifacts/v4/model/runs/stas5_v4_train_20260714_163911/stas5_v4_group_ranker_20260501_20260525_v0.joblib`;
- model manifest: `STAS5_ML_CORE/artifacts/v4/model/runs/stas5_v4_train_20260714_163911/stas5_v4_group_ranker_20260501_20260525_v0.manifest.json`;
- forward run: `STAS5_ML_CORE/artifacts/v4/forward/runs/stas5_v4_forward_20260526_20260530_20260714_164144`;
- forward manifest: `STAS5_ML_CORE/artifacts/v4/forward/runs/stas5_v4_forward_20260526_20260530_20260714_164144/STAS5_V4_FORWARD_GROUP_RANK_REVIEW_MANIFEST.json`.

Контрольные цифры:

- dataset guard `PASS`;
- dataset rows `1710`: `972` legacy `2026-05-01..14` + `738` corrected group review `2026-05-15..25`;
- V4 corrected ledger join `738/738`, duplicate keys `0`;
- features `287`: старые `274` контекстные признаки + `13` V4 group features;
- old `ML_KEEP_SCORE/ML_DECISION`, postfact/future/TP/Stas3/exit не попали в model features;
- winners `103`;
- OOF group metrics: `top1_group_accuracy=0.679612`, `winner_in_top2=0.834951`, `MRR=0.797006`, `NDCG@3=0.805523`, `BAD top1=15`, `GOOD_ALT top1=18`;
- train-fit group metrics: `top1_group_accuracy=0.961165`, `winner_in_top2=1.0`, `BAD top1=0`;
- forward `2026-05-26..30`: `363` rows, `25` auto-groups, `ENTER=24`, `UNSURE=16`, `SKIP=323`.

Forward по дням:

- `2026-05-26`: rows `76`, groups `5`, `ENTER=4`, `UNSURE=3`;
- `2026-05-27`: rows `66`, groups `6`, `ENTER=5`, `UNSURE=3`;
- `2026-05-28`: rows `81`, groups `5`, `ENTER=5`, `UNSURE=5`;
- `2026-05-29`: rows `81`, groups `5`, `ENTER=5`, `UNSURE=1`;
- `2026-05-30`: rows `59`, groups `5`, `ENTER=5`, `UNSURE=4`.

Проверки:

- `python -m py_compile src\mlbotnav\stas5_v4_group_rank_dataset.py src\mlbotnav\stas5_v4_group_rank_train.py`;
- `python -m py_compile src\mlbotnav\stas5_v4_forward_group_rank_review.py src\mlbotnav\stas5_v2_forward_entry_review.py`;
- прямой smoke-test V4 test functions: `3 PASS`;
- `pytest` недоступен в обоих Python окружениях (`No module named pytest`);
- визуально открыт PNG `20260526/STAS5_V4_FORWARD_GROUP_RANK_REVIEW_20260526.png`, график не пустой, подписан как `STAS5 V4`.

Следующий правильный шаг: глазами проверить PNG `2026-05-26..30`, отметить ложные/хорошие V4 ENTER по группам и после этого решать, править auto-group policy или reason/group ledger для следующих дней.

## Handoff 2026-07-14 STAS5 V4 No-Future Audit / V4L

Статус: `STAS5_V4_OFFLINE_GROUP_REVIEW_DONE__V4L_LIVE_SAFE_REQUIRED`.

Пользователь зафиксировал обязательное правило: V4 не может знать будущего. Это включает не только TP/Stas3/future outcome, но и будущий состав группы. Если кандидат появился в момент `entry_time_utc`, модель может знать только прошлые свечи, прошлые признаки и уже появившихся кандидатов.

Текущий V4 train/forward остается полезным как offline group review, но не live-safe production model:

- train run: `STAS5_ML_CORE/artifacts/v4/model/runs/stas5_v4_train_20260714_163911`;
- forward run: `STAS5_ML_CORE/artifacts/v4/forward/runs/stas5_v4_forward_20260526_20260530_20260714_164144`;
- статус: `OFFLINE_GROUP_REVIEW_NOT_LIVE_SAFE`.

Новые документы:

- `STAS5_ML_CORE/07_STAS5_V4_HUMAN_STYLE_GROUP_RANKER_TZ_RU.md` - добавлен закон `No-Future / Live-Safe`, разделение live-safe vs audit-only features и guard `prefix invariance`;
- `STAS5_ML_CORE/08_STAS5_V4L_LIVE_SAFE_GROUP_RANKER_PLAN_RU.md` - план реализации V4L.

Следующий правильный шаг: не переобучать старый V4. Сначала создать V4L live replay dataset с `v4l_*_so_far` признаками и guard:

1. `LIVE_SAFE_FEATURE_ALLOWLIST`;
2. banned-column scan;
3. `feature_available_time_utc <= entry_time_utc`;
4. `prefix invariance`;
5. `retroactive_feature_change_count = 0`;
6. `retroactive_score_change_count = 0`;
7. `retroactive_decision_flip_count = 0`.

## Handoff 2026-07-14 STAS5 V4L Live-Safe Train/Forward

Текущий рабочий контур для нового запуска: `STAS5_V4L_LIVE_SAFE_TRAIN_FORWARD_READY_20260501_20260530`.

Что сделано:

1. Добавлены модули `src/mlbotnav/stas5_v4l_live_safe_dataset.py`, `src/mlbotnav/stas5_v4l_live_safe_train.py`, `src/mlbotnav/stas5_v4l_live_safe_forward.py`.
2. Добавлена единая команда `STAS5_ML_CORE/run_stas5_v4l_live_safe_train_forward.ps1`.
3. Dataset `2026-05-01..2026-05-25` собран с исправленным ledger `15..25`, включая `2026-05-15`: `1710` строк, `103` winners, `289` features.
4. Guard `PASS`: forbidden features `{}`, prefix-invariance `1710/1710`, full-group V4 columns в dataset отсутствуют.
5. Последний проверенный train: `STAS5_ML_CORE/artifacts/v4l/model/runs/stas5_v4l_train_20260714_181635`.
6. Последний проверенный forward `2026-05-26..2026-05-30`: `STAS5_ML_CORE/artifacts/v4l/forward/runs/stas5_v4l_forward_20260526_20260530_20260714_181635`, totals `ENTER=23`, `UNSURE=80`, `SKIP=260`.

Команда для пользователя:

```powershell
.\STAS5_ML_CORE\run_stas5_v4l_live_safe_train_forward.ps1
```

Следующий шаг: смотреть PNG forward `26..30`, отмечать слишком ранние live-входы и калибровать thresholds/policy только live-safe способом, без возврата full-group/day-end top-N.

## Handoff 2026-07-15 STAS5 V5 Row-Level Pivot + Day23 Pre-Knife Fix

Текущий рабочий статус: `V4_V4L_FROZEN_AS_FAILED_STRATEGY__V5_ROW_LABEL_PREP`.

Пользователь отверг V4/V4L как финальную стратегию. Не предлагать поверхностные policy, кулдауны, лимиты входов, "один ENTER на группу" или full-group/day-end selection. Следующий контур должен обучать ML напрямую на исправленных строковых good/bad метках: хорошие ручные/визуальные входы должны стать positive examples, неподчеркнутые и плохие рядом - negative examples. `group_id`/`reason_code` используются как объяснение метки и контроль качества, но не как production policy.

Новый разбор `2026-05-23` выполнен по оригиналам:

- PNG: `STAS5_ML_CORE/artifacts/v3/forward/runs/stas5_v3_wrapper_smoke2_20260714/20260523/STAS5_V3_FORWARD_ENTRY_REVIEW_20260523.png`;
- entries CSV: `STAS5_ML_CORE/artifacts/v3/forward/runs/stas5_v3_wrapper_smoke2_20260714/20260523/STAS5_V3_FORWARD_ENTRIES_20260523.csv`;
- OHLCV: `data/core/bybit_ohlcv/dt=2026-05-23/tf=1m/symbol=SOLUSDT/part-final.csv`.

Создан новый corrected ledger:

`STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V2_PRE_KNIFE.csv`

Ключевое исправление: `LA001..LA016` теперь `NO_TRADE_GROUP`, `LA007` больше не winner, `LA022` остается главным нижним `BEST_GOOD`, `LA025` остается `GOOD_ALT`. Счетчики: `rows=63`, `BEST_GOOD=6`, `GOOD_ALT=2`, `BAD_IN_GROUP=27`, `NO_TRADE_GROUP=28`.

Также создан общий V5 label-source `2026-05-15..2026-05-25` с заменой day23 на `USER_CORRECTED_V2_PRE_KNIFE`:

`STAS5_ML_CORE/artifacts/v5/labels/STAS5_V5_ROW_LABEL_SOURCE_20260515_20260525_WITH_DAY23_PRE_KNIFE_V1.csv`

Guard `PASS`: `738` строк, `11` дней, дублей `0`, `BEST_GOOD=63`, `GOOD_ALT=40`, `BAD_IN_GROUP=420`, `NO_TRADE_GROUP=215`; positive при маппинге `BEST_GOOD+GOOD_ALT=103`, negative `635`.

Следующий шаг: реализовать/собрать `STAS5 V5 row-level corrected-label` training dataset на `2026-05-01..2026-05-25`, где `01..14` берутся из legacy labels, `15..25` из V5 label-source, а future/audit drawdown columns не попадают в features.
## Handoff 2026-07-15 Codex CPU Load Check

Статус: `CODEX_CPU_LOAD_CHECK_READY_NO_KILL_NO_DELETE_NO_CODE_CHANGE`.

Пользователь сообщил, что Codex снова грузит CPU. Проведена аккуратная диагностика без остановки процессов и без удаления файлов. Подробный отчет: `docs/codex/CODEX_CPU_LOAD_CHECK_20260715_RU.md`.

Вывод: это не похоже на опасный зависший `git add -A` из старого случая. `git status` быстрый, около `51 ms`; `.git/index.lock` нет; `git diff --cached --name-only` пустой. Но Codex периодически запускает внутренний `git diff --find-renames --numstat -z` и краткие `git add -u`/`git add -A` от `Codex.exe`. На фоне разросшегося dirty worktree это дает заметную CPU-нагрузку: группа Codex около `5.3%..9.2% CPU`, около `3.5..3.6 GB PrivateMB`.

Главное изменение с 2026-07-11: untracked выросли с `393` файлов / `58.7 MB` до `1574` файлов / `424.8 MB`, основной источник `STAS5_ML_CORE` (`1220` файлов, около `389.8 MB`).

Следующий безопасный шаг: не убивать процессы, а уменьшить dirty worktree отдельным решением - коммит/стейдж source-of-truth файлов, перенос generated artifacts или `.gitignore` для generated artifacts после согласования.
## Handoff 2026-07-16 Codex Unload Applied

Статус: `CODEX_UNLOAD_APPLIED_NO_DELETE_NO_PROCESS_KILL_CODEX`.

Пользователь попросил разгрузить Codex/CPU/память без удаления. Выполнено без удаления файлов и без остановки Codex. Для процессов `Codex`/`codex` выставлен приоритет `BelowNormal`. В `.gitignore` и `.vscode/settings.json` добавлены исключения для generated/run-папок `STAS5_ML_CORE/artifacts/` и `STAS5_ML_CORE/runs/`.

Эффект: untracked Git-хвост снизился с `1574` файлов / `424.8 MB` до `381` файла / `41.6 MB`. `STAS5_ML_CORE/artifacts` и `STAS5_ML_CORE/runs` подтвержденно игнорируются. `.vscode/settings.json` валиден (`JSON_OK`). После финального контроля активных `git.exe` не осталось, `.git/index.lock` нет, `git status` около `51 ms`.

Отчет: `docs/codex/CODEX_UNLOAD_ACTION_20260716_RU.md`.

## Handoff 2026-07-16 Codex Idle Relief

Статус: `CODEX_IDLE_RELIEF_APPLIED_NO_DELETE_NO_STAS_TOUCH`.

Пользователь сообщил, что в простое все еще двигаются диск/память/CPU, и отдельно запретил трогать папки `STAS*`, особенно `STAS5` и `STAS6`. Удалений не было, папки `STAS*` не изменялись.

Сделано: остановлены read-only Git-процессы `git status --porcelain` и внутренний `git diff --find-renames --numstat -z`; подтверждено, что `.git/index.lock` нет и активных `git.exe` не осталось. Приоритет `Codex`/`codex`/`Code` понижен до `Idle`. Остановлен отдельный VS Code OpenAI/Codex extension server `openai.chatgpt...\codex.exe app-server`; Desktop Codex не закрывался.

Вывод: опасного зависшего Git-процесса нет. Главный оставшийся короткий дисковый всплеск по процессным счетчикам дал `MsMpEng` (Microsoft Defender), а не Git. Defender не отключался и его настройки не менялись. Отчет: `docs/codex/CODEX_IDLE_RELIEF_20260716_RU.md`.

## Handoff 2026-07-22 Codex Update Load Audit

Статус: `CODEX_UPDATE_LOAD_AUDIT_RELIEF_APPLIED_NO_DELETE`.

Пользователь сообщил, что после обновления Codex снова крутит CPU/диск. Удалений не было, папки проекта и `STAS*` не изменялись. Подтверждено обновление Codex до `OpenAI.Codex_26.715.10079.0`; после обновления главный UI-процесс называется `ChatGPT.exe`, поэтому старое понижение приоритета только для `Codex`/`codex` не прижимало основной renderer/gpu.

Сделано: остановлен отдельный VS Code OpenAI/Codex extension server `openai.chatgpt-26.715.31925...\codex.exe app-server`; приоритеты `ChatGPT`/`codex`/`Code`/`node_repl` понижены до `Idle`; активных `git.exe` после контроля нет, `.git/index.lock` нет, `git status` около `52 ms`.

Финальный контроль: системный CPU `3.9..9.7%`, Disk Time `0.8..10.4%`, чтение диска `0`, свободная память `13.5..13.7 GB`. Оставшийся CPU идет от активного окна Codex/ChatGPT (`renderer`/`gpu`), его нельзя безопасно убить без разрыва текущей сессии. Отчет: `docs/codex/CODEX_UPDATE_LOAD_AUDIT_20260722_RU.md`.

## Handoff 2026-07-23 Codex VS Code Fix

Статус: `CODEX_VSCODE_EXTENSION_RESTARTED_NO_DELETE`.

Пользователь показал ошибку в панели VS Code: `Работа Codex неожиданно остановлена`. Причина: отдельный сервер расширения VS Code `openai.chatgpt-26.715.31925...\codex.exe app-server` не был запущен после предыдущей разгрузки.

Сделано без удаления и без изменения `STAS*`: через UI Automation нажата штатная кнопка `Перезапустить`; сервер расширения поднялся как PID `12948`; приоритеты `ChatGPT`/`codex` выставлены в `Idle`. После краткой прогрузки контроль показал `codex#1` = `0% CPU`, `0` I/O ops/s, около `145 MB` памяти. Отчет: `docs/codex/CODEX_VSCODE_FIX_20260723_RU.md`.

## Handoff 2026-07-23 STAS9 Shortcut And CPU Fix

Статус: `STAS9_VSCODE_SHORTCUT_FIXED_TERMINAL_STOPPED`.

Старый ярлык `🤖 STAS9 Главный агент` открывал технический `start_STAS9.bat`, поэтому пользователь попадал в отдельный терминальный Codex. Точное дерево `cmd -> node -> codex` и его дочерние процессы остановлено без затрагивания Codex Desktop и сервера расширения VS Code.

Оба ярлыка STAS9 теперь открывают `MLbotNav_STAS9.code-workspace` через `Code.exe`. Контрольный запуск старого по имени ярлыка открыл окно `MLbotNav_STAS9 (рабочая область) - Visual Studio Code`; terminal launcher отсутствовал. Добавлена лёгкая активация без автоматического чтения больших журналов и усилены фоновые исключения Git/Pylance. Чистый замер: `Code ~1.56%`, все `codex ~0.10%`. Отчёт: `STAS9_CONTROL_PLANE/REPORTS/STAS9_SHORTCUT_CPU_FIX_REPORT_RU.md`.
