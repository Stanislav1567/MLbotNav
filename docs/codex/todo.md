# Todo

## 2026-07-23 Codex Desktop CPU/Git Repair

Статус: `local_fix_done_remote_pending`.

| Задача | Статус | Следующее действие |
|---|---|---|
| Остановить Git/taskkill storm | done | Сохранять рабочее дерево небольшим и чистым |
| Проверить секреты и тяжёлые артефакты | done, совпадений `0` | Не добавлять `.env`, data/models/reports/runs |
| Зафиксировать накопленные рабочие файлы | done, `346cd3a` | Работать в `codex/git-normalization-cpu-relief` |
| Проверить целостность Git | done, full fsck `PASS` | Хранить карантин до отдельного решения |
| Проверить CPU после ремонта | done, `0` новых Git/taskkill за `15 s` | Повторить визуальный контроль после следующего перезапуска приложения |
| Отправить ветку в GitHub | pending_user_confirmation | Push выполнять только после отдельного подтверждения |

## 2026-07-23 SOL Event Pipeline Design

Статус: `schema_dry_run_done`.

| Задача | Статус | Следующее действие |
|---|---|---|
| Закрепить канонический source SOLUSDT 1m | done | Не добавлять другие физические копии |
| Создать EVENT-контракт | done | Использовать `stas9_sol_event_v1` |
| Создать `EVENTS/SOL` | done, YAML events `0` | Принимать только schema-validated события |
| Зафиксировать первые event types | done, `9` | Исследовать распределения без произвольных порогов |
| Выполнить pipeline dry-run без записи | done, `PASS` | Сохранить no-write gate |
| Утвердить detector contract | pending_explicit_tz | Окна, пороги и confirmation semantics |
| Утвердить feature/outcome/label contracts | pending_explicit_tz | До dataset builder |
| Создать реальные события | blocked_until_contracts | Не создавать на текущем этапе |
| Создать dataset или обучить модель | blocked | Только отдельное прямое ТЗ |

## 2026-07-23 STAS9 VS Code On-Demand Workflow

Статус: `done`.

| Задача | Статус | Следующее действие |
|---|---|---|
| Закрепить VS Code + Codex как основной интерфейс | done | Открывать `🤖 STAS9 Workspace` |
| Перевести Sentinel на роль Codex `ON_DEMAND` | done | Активировать только обращением пользователя |
| Отключить фоновый процесс и сканирование | done | Сохранять idle `NONE` |
| Сохранить console launcher | done | Использовать только для диагностики |
| Проверить процессы и автозапуск | done, совпадений `0` | Повторять только при симптомах |
| Проверить STAS5, data и models | done, fingerprints unchanged | Не изменять без отдельного ТЗ |
| Проверить открытие ярлыка в интерфейсе | manual_optional | Один раз открыть ярлык пользователем |

## 2026-07-23 STAS9 Agent Roles and SOL ML Preparation

Статус: `setup_done_training_blocked`.

| Задача | Статус | Следующее действие |
|---|---|---|
| Создать документы ролей | done, `7/7` | Использовать через Sentinel |
| Создать `STAS9_MARKET_RESEARCH` | done | Передавать только SOL read-only задачи |
| Создать маршрутизатор и память обязанностей | done | Обновлять после важных задач |
| Создать `MARKET_KNOWLEDGE` и event template | done | Не считать template наблюдением |
| Создать безопасный dataset pipeline | done | Сначала события, признаки и labels |
| Проанализировать реальные свечи SOL | pending_user_scope | Нужны точный путь, таймфрейм и интервал |
| Запустить обучение или Optuna | blocked | Только по отдельному прямому ТЗ |

## 2026-07-23 STAS9 Persistent Memory

Статус: `done`.

| Задача | Статус | Следующее действие |
|---|---|---|
| Проверить текущую архитектуру STAS9 | done | Сохранять схему `Codex -> Sentinel -> Control Plane` |
| Создать краткую постоянную память | done | Обновлять после важной работы |
| Создать инструкцию нового чата | done | Начинать через `START_HERE_RU.md` |
| Сохранить `SAFE` и границу STAS5–STAS8 | done | Повышать режим только явной ограниченной командой |
| Реализовать `schemas/adapters/gates/run_plans` | proposed | Только по отдельному ТЗ |

## 2026-07-23 STAS9 VS Code/Codex Interface

Статус: `done`.

| Задача | Статус | Следующее действие |
|---|---|---|
| Создать workspace | done | Открывать через ярлык |
| Автоматически фокусировать Codex | done | `chatgpt.openOnStartup=true` |
| Создать STAS9_INTERFACE | done | Нет |
| Настроить голосовой ввод | done | Пользователь нажимает `Win+H` в composer |
| Настроить SAFE/DEVELOPMENT/EXPERIMENT | done | Подтверждать повышение режима |
| Создать журнал общения | done | Sentinel ведёт YAML audit trail |
| Сохранить terminal launcher | done | Использовать только как технический резерв |
| Проверить STAS5/STAS8 | done | SHA256 сохранён |

Необязательная ручная проверка: открыть новый ярлык и проверить фактический доступ Windows к микрофону.

## 2026-07-23 STAS9 Codex Runtime

Статус: `done`.

| Задача | Статус | Следующее действие |
|---|---|---|
| Обновить Codex CLI | done, `0.145.0` | Использовать ярлык STAS9 |
| Проверить launcher | done | Нет |
| Проверить `gpt-5.6-sol` | done, `STAS9_MODEL_OK` | Нет |
| Подтвердить неизменность STAS5/STAS8 | done | Сохранять SHA-грань |

## 2026-07-23 STAS9 Multi-Agent Control Layer

Статус: `done`.

| Задача | Статус | Следующее действие |
|---|---|---|
| Создать главного и специализированных агентов | done | Использовать через Sentinel |
| Добавить память, журналы и глобальную политику | done | Сохранять append-only историю |
| Создать launcher только для Sentinel | done | Рабочий запуск выполняет пользователь |
| Создать ярлык на рабочем столе | done | Ручная проверка интерфейса по желанию |
| Проверить Git, YAML, структуру и SHA256 | done | Сохранять SHA-грань перед следующими работами |

## 2026-07-23 STAS9 Multi-Agent Structure

Статус: `done`.

| Задача | Статус | Следующее действие |
|---|---|---|
| Создать `STAS9_AGENTS` и семь каталогов агентов | done | Наполнять только по отдельному ТЗ |
| Создать служебные каталоги control plane | done | Наполнять только по отдельному ТЗ |
| Не создавать отсутствующие `STAS6`/`STAS7` | done | Сохранять границу |
| Не изменять STAS5–STAS8 | done | Контролировать отпечатком перед следующими изменениями |

## 2026-07-23 STAS9 Control Plane

Статус: `audit_and_registry_baseline_done`.

| Задача | Статус | Следующее действие | Зависимость |
|---|---|---|---|
| Создать STAS9 без изменения STAS5–STAS8 | done | Сохранить read-only границу | metadata fingerprint |
| Составить карту STAS1–STAS8 | done | Утвердить роли и пробелы STAS6/STAS7 | `PROJECT_MAP.md` |
| Зарегистрировать модели | done | Не исправлять broken pointer без отдельного разрешения | `MODEL_REGISTRY.yaml` |
| Зарегистрировать признаки | done | При реализации добавить schema/hash validator | `FEATURE_REGISTRY.yaml` |
| Зарегистрировать ТЗ | done | Активировать legacy ТЗ только отдельным action_id | `TASK_REGISTRY.md` |
| Зафиксировать архивную политику | done | Применять admission gate к старым артефактам | `ARCHIVE_POLICY.md` |
| Реализовать STAS9 schemas/adapters/gates | proposed | Сначала получить архитектурное подтверждение | отдельное ТЗ |
| Определить судьбу STAS6/STAS7 | blocked_by_product_decision | Не выдумывать роли автоматически | решение пользователя |
| Исправить старый active/champion pointer | blocked_by_explicit_authorization | Выбрать модель и провести promotion audit | отдельное разрешение |

## 2026-07-23 Codex Project CPU Relief

Статус: `done_cpu_stabilized`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Найти источник CPU | done | Codex Git scan по generated STAS4, не ML | process audit |
| Уменьшить Git/VS Code scan | done | STAS4 generated подпапки игнорируются, верхние Markdown остаются видимыми | `.gitignore`, `.vscode/settings.json` |
| Проверить ML-процессы | done | Активных Python/обучения нет | process audit |
| Проверить итоговую нагрузку | done | `10.0..13.6%`, среднее `12.3%` | 5-second CPU sample |
| После перезапуска Codex | optional | Если приоритет сбросился и CPU снова высокий, применить команду мягкого `Idle` | user observation |

## 2026-07-22 STAS5 V5 Base R2-Style Review Gallery

Статус: `ready_for_user_visual_review`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сделать обычные графики базы как R2/R3/R4 | done | Пользователь проходит глазами `CURRENT_REVIEW` PNG | base ML_READY CSV |
| Проверить контрольные цифры базы | done | PASS: `32/32`, `rows=2596`, `GOOD=290`, `BAD=2306` | manifest |
| Дать команду повторной пересборки | done | `run_stas5_v5_base_review_gallery.ps1` | builder |
| Пересобирать ML-базу по новым ручным правкам | blocked | Только после ручного review и отдельной команды/OK | user labels |

## 2026-07-22 STAS5 V5C Entry Visual Check Pack

Статус: `ready_for_user_visual_review`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Пересобрать R2/R3/R4 review-графики без нового train/forward | done | PASS: `R2=7`, `R3=7`, `R4=7` | review ledgers |
| Собрать единый пакет BASE+R2/R3/R4 | done | Открыть папку и пройти глазами входы | visual artifacts |
| Проверить количество дней и no-training/no-forward флаги | done | `total_png_days=53`, `no_training=True`, `no_forward=True` | manifest |
| Следующее обучение | blocked | Только после ручного visual OK и согласованной правки входов/риска/STAS8 | user review |

## 2026-07-22 STAS5 V5C R4BB Table/ML Audit

Статус: `done_no_fatal_table_bug_found`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить, применились ли R2/R3/R4 ручные правки в train datasets | done | PASS: mismatch `0`, `risk плохо -> entry_y=0 + risk_bad_y=1` | approved review pack |
| Проверить X463/joblib/allowlist на старый X439 и leakage | done | PASS: `463` features, `24` `bb20_*`, forbidden hits `0` | R4BB train run |
| Проверить, попал ли STAS8 Soft V2 visual bug в обучение | done | PASS: `STAS8_SOFT/RECALL_WATCH/marker` не входят в X | R5 preview |
| Зафиксировать причину качества | done | Не table bug; дальше настраивать ENTRY recall, RiskGate threshold и STAS8/move-capacity preview | audit |
| Делать новое обучение | blocked | Только после визуального OK по следующему preview/согласованной логике | no-future rails |

## 2026-07-22 STAS8 Soft Capacity V2 Preview R5

Статус: `preview_visual_semantics_fixed_needs_down_channel_tuning`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать `STAS8_SOFT_CAPACITY_V2` с режимами `strict/balanced/wide` | done | Смотреть contact sheets и дневные PNG | STAS8 V1 audit |
| Пересобрать R5 `2026-03-21..2026-03-27` без нового train/forward | done | Guard PASS, predictions SHA unchanged | R5 no-risk forward |
| Добавить сводные contact sheets | done | `STRICT/BALANCED/WIDE_CONTACT_SHEET.png` лежат в `soft_capacity_v2` | visual outputs |
| Исправить визуальную семантику маркеров | done | Зеленый круг теперь только final live `ENTER`; `SKIP->RECALL_WATCH` скрыт с цены | user visual audit |
| Проверить no-future/immutability guard | done | `18` checks PASS, failed_count=0 | guard |
| Выбрать рабочий preset | blocked | Сначала подстроить down-channel: `balanced` еще оставляет 1 live ENTER на 2026-03-26, `wide` оставляет 9 | visual review |
| Настроить down-channel/no-long без убийства rebound | current_next | Сделать следующий preview, где long в монотонном канале вниз режется жестче, а post-knife/local-low отскок не душится | R5 26/27 visual |
| Включать V2 в обучение или боевой forward | blocked | Только после ручного OK и отдельного training/forward guard | no-future rails |

## 2026-07-22 STAS8 R5 Entry/Move Audit

Статус: `audit_done_next_soft_capacity_v2_preview`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Посчитать R5 `2026-03-21..2026-03-27` по ENTRY/STAS8/future move audit | done | Отчет и CSV-срезы сохранены в `stas8_move_capacity_audit/v1` | R5 no-risk X463 forward |
| Подтвердить, что текущий STAS8 V1 слишком жесткий | done | Не включать V1 в production/enforce | audit |
| Разделить рабочие и опасные buckets | done | `NO_MOVE/LOW_MOVE_CHOP/NO_MOVE_DOWN_CHANNEL` резать; `POST_KNIFE_RETEST_EDGE/MOVE_OK_*` защищать | audit |
| Спроектировать `STAS8_SOFT_CAPACITY_V2` | next | Сделать read-only preview с режимами `strict/balanced/wide` без train/forward | user OK |
| Добавлять R5 в обучение | blocked | Только после ручного review R5 и отдельного approved review pack | no-future rails |

## 2026-07-22 STAS8 R5 Visuals Without Bollinger

Статус: `done`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Убрать Bollinger-полосы со STAS8 R5 PNG | done | Смотреть чистые графики без фиолетовых полос | user request |
| Проверить, что это не поменяло ML/forward | done | Guard PASS, counts unchanged, `visual_bollinger_preview=false` | STAS8 audit |
| Настраивать STAS8 по 26/27 марта | user_next | Разобрать, где down-channel блок верный, а где нужен post-knife rebound allow | visual review |

## 2026-07-22 STAS8 Move Capacity Audit Preview R5

Статус: `audit_preview_done_needs_visual_tuning_before_train_or_enforce`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать `STAS8_MOVE_CAPACITY_AUDIT_V1` | done | Код и wrapper готовы | user OK |
| Прогнать R5 `2026-03-21..2026-03-27` | done | Guard PASS, 564 rows, 7 PNG | актуальный no-risk X463 forward |
| Проверить no-future/immutability guard | done | predictions SHA unchanged, teacher-grid отдельно | guard |
| Посмотреть PNG `2026-03-26/2026-03-27` | user_next | Настроить пороги, потому что preview сейчас слишком жесткий | visual review |
| Включать STAS8 в train/forward | blocked | Только после визуального OK и отдельного dataset/training guard | user approval |

## 2026-07-22 STAS8 Live Wave + Move Capacity

Статус: `tz_locked_no_code_no_training`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Обновить ТЗ STAS8 под live wave context | done | ТЗ и config зафиксированы | user correction |
| Разделить teacher grid и live context | done | `STAS8_TEACHER_MOVE_GRID_V1` и `STAS8_LIVE_MOVE_CONTEXT_V1` записаны | no-future rule |
| Зафиксировать train/forward рельсу | done | R2/R3/R4 = train material; R5 `2026-03-21..2026-03-27` = blind audit до review | review protocol |
| Реализовывать STAS8 audit preview | blocked | Только после отдельного OK пользователя | TZ locked |
| Обучать MOVE_EDGE_ML | blocked | Только после audit-preview, visual OK и STAS8 guard PASS | future step |

## 2026-07-22 STAS5 V5C R4BB Fast Train Audit

Статус: `done`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить, не проигнорировался ли X463/Bollinger в быстром train | done | Аудит PASS: manifest/joblib используют `463` features и `24` `bb20_*` | user train |
| Проверить ENTRY/RiskGate post-train guards | done | ENTRY PASS, RiskGate PASS, non-pass checks `0` | train artifacts |
| Исправить stale X439/invalid wording | done | Код и текущие R4BB guard/manifests используют нейтральные имена без старых X439-меток | guard text |
| Исправить `active_context.train` в управляющем config | done | YAML/JSON теперь указывают на `stas5_v5c_r4bb_train_20260127_20260320`, `feature_count=463` | audit PASS |
| Дальше запускать forward | user_next | Только если пользователь хочет прогон по сохраненной модели; использовать manifest `stas5_v5c_r4bb_train_20260127_20260320` | config fixed |

## 2026-07-22 STAS5 V5C Bollinger Layer V1 X463

Статус: `ready_for_user_visual_review_then_manual_train`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать общий causal расчет `bb20_*` | done | Использовать один модуль в train/forward/visual | OHLCV 1m |
| Собрать ENTRY dataset `X463` по base32 + approved R2/R3/R4 | done | `rows=3285`, `GOOD=517`, `BAD=2768`, guard PASS | review pack |
| Собрать RiskGate dataset `X463` | done | `rows=627`, `risk_bad=400`, `safe=227`, guard PASS | review pack |
| Прогнать ENTRY TrainingGuard | done | `stas5_v5c_r4bb_train_20260127_20260320`, features `463`, PASS | X463 batch |
| Прогнать RiskGate ML TrainingGuard | done | features `463`, PASS | X463 risk dataset |
| Собрать R2/R3/R4 gallery с Bollinger | done | Открыть `_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA` и сверить визуально | approved ledgers |
| Запускать обучение | user_next | Пользователь вручную запускает train после визуального OK | guards PASS |
| Запускать forward `2026-03-21..2026-03-27` | blocked | Только после train + post-train guards PASS | manual Train |

## 2026-07-22 STAS5 V5C R5 ENTRY-Only No-Risk Bollinger

Статус: `visual_review`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать Bollinger `20/2` в правильной R5 no-risk папке `visual_review` | done | Пользователь смотрит дневные `*_BOLLINGER20_2SIGMA_PREVIEW.png` | R5 ENTRY-only forward |
| Наложить `BB_BLOCK_V0` красными кругами на опасные `ENTER/WATCH` за `2026-03-21..2026-03-27` | done | Смотреть `*_ENTER_WATCH_BOLLINGER_BLOCK_V0_RED_CIRCLES.png`, особенно `2026-03-26/2026-03-27` | Bollinger preview |
| Проверить, не душит ли `BB_BLOCK_V0` хорошие отскоки | user_next | Пользователь глазами отмечает, какие красные круги верные, а какие режут хорошие входы | red-circle PNG |
| Не путать с `safety_pulse_preview/down_channel_no_long_v1` | guard | Для no-risk графиков использовать `mlbotnav.stas5_v5_forward_visual_review --bollinger-preview` | текущая папка пользователя |

## 2026-07-22 STAS5 V5C Bollinger Visual Preview

Статус: `visual_review`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Наложить Bollinger `20/2` на все графики недели `2026-03-21..2026-03-27` | done | Пользователь смотрит PNG и решает, помогает ли слой для отбора интересных входов | готовый `DOWN_CHANNEL_NO_LONG_V1` preview |
| Не превращать Bollinger в feature/фильтр без отдельного OK | guard | Пока только визуальный анализ | user OK |
| Если слой полезен | user_next | Обсудить отдельный STAS8/move-capacity или volatility-band признак через causal/no-future guard | визуальное OK |

## 2026-07-22 STAS5 V5C ENTRY-Only Wide R5

Статус: `user_next`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `-SkipRiskGateML` для ENTRY-only train | done | Пользователь может запускать train-команду | R2/R3/R4 batch |
| Добавить `-DisableRiskGateML` для ENTRY-only forward | done | Пользователь может запускать forward без RiskGate | saved train manifest |
| Использовать `WideReview` для раздушенных входов | ready | Смотреть больше кандидатов на графике | Train PASS |
| Накладывать RiskGate / short-channel / move 1.2% | later | Только после визуального анализа ENTRY-only | графики R5 |

## 2026-07-22 STAS8 Move Capacity Grid TZ

Статус: `deferred`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать ТЗ `STAS8 MOVE CAPACITY GRID V1` | done | Документ сохранен | идея volatility vs edge |
| Записать STAS8 в управляющий YAML | done | Блок выключен: `enabled=false`, `mode=deferred_tz_only` | ML config |
| Реализовывать код/датасет/обучение STAS8 | blocked | Только после отдельного OK пользователя | визуальное согласование |
| Следить за no-future | guard | Future/MFE/MAE/hit/time_to только offline teacher/audit, не X | будущая реализация |

## 2026-07-21 STAS5 V5C Down-Channel Safety Pulse Preview

Статус: `current_visual_review`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `DOWN_CHANNEL_NO_LONG_V1` в safety pulse preview | done | Код и ps1 готовы | R4 forward |
| Использовать causal X439 для down-channel/no-edge blocker | done | `source_x439_exists PASS`, join `564/564` | X439 forward dataset |
| Пересобрать preview PNG/CSV за `2026-03-21..2026-03-27` | done | `ENTER=40`, `WATCH=136`, `SKIP=388` | готовый forward |
| Проверить 26/27 марта | done | `2026-03-26 ENTER=4`; `2026-03-27 ENTER=7` | PNG preview |
| Визуально согласовать с пользователем | user_next | Смотреть папку `down_channel_no_long_v1`, особенно `20260326/20260327` | preview PASS |
| Встраивать в боевой forward или запускать новый train | blocked | Только после визуального OK и отдельного guard/решения | user OK |

## 2026-07-21 STAS5 V5C Safety Pulse Preview Before Retrain

Статус: `current_visual_review`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать preview без обучения поверх `2026-03-21..2026-03-27` | done | Смотреть PNG в `safety_pulse_preview` | R4 forward |
| Проверить `BALANCED_SAFETY_V1` | done | Слишком жестко: `ENTER=3`, использовать только как нижнюю границу безопасности | taxonomy audit |
| Проверить `HARD_BLOCK_ONLY_V1` | done | Кандидат на следующий пульс: `ENTER=27`, `WATCH=138`, `SKIP=399` | taxonomy audit |
| Визуально согласовать с пользователем | user_next | Пользователь смотрит графики и говорит, какой пульс брать дальше | preview PNG |
| Встраивать в боевой forward | blocked | Только после визуального OK и отдельного guard | user OK |
| Переобучать заново | blocked | Только после согласованного пульса и новой разметки/guard | visual OK |

## 2026-07-21 STAS5 V5C RiskGate ML Train Wiring Ready

Статус: `current_next_train_manual`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Подключить `RISKGATE_ML` к `-Mode Train` | done | Train будет учить RiskGate после ENTRY/two-block | ENTRY batch + RiskGate dataset |
| Подключить `RISKGATE_ML` к будущему forward | done | Forward сохранит `ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE` и выдаст финальный `ENTRY_ML_LIVE_DECISION` после safety-фильтра | saved RiskGate model |
| Прогнать RiskGate ML TrainingGuard | done | `PASS_V5C_RISKGATE_ML_TRAINING_GUARD_READY_FOR_TRAINING` | RiskGate dataset guard PASS |
| Запустить обучение | user_next | Пользователь вручную запускает `-Mode Train` для `stas5_v5c_r4_train_20260127_20260320` | все guards PASS |
| Запустить forward | blocked | Только после Train и PASS post-train guards ENTRY + RiskGate | manual Train |

## 2026-07-21 STAS5 V5C Review-Supervised Datasets Ready

Статус: `current_next_train_manual`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать `X439_SOURCE` из base32 + approved R2/R3/R4 | done | `PASS_BUILT_FROM_BASE32_AND_APPROVED_REVIEW_PACK` | approved review-pack |
| Собрать `ENTRY_TRAIN_DATASET` | done | `3285 rows`, `GOOD=517`, `BAD=2768` | X439_SOURCE |
| Собрать `RISKGATE_TRAIN_DATASET` | done | `627 rows`, `risk_bad_y=1=400`, explicit safe `227` | X439_SOURCE |
| Прогнать dataset guards | done | ENTRY guard PASS, RiskGate guard PASS | оба dataset |
| Прогнать training guard | done | `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING` | ENTRY batch |
| Запустить обучение | user_next | Пользователь запускает `-Mode Train` вручную в VS Code | training guard PASS |
| Запустить forward | blocked | Только после сохраненной модели и post-train guard PASS | Train |

## 2026-07-21 STAS5 V5C Dataset Rails Locked

Статус: `current_next`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать dataset rails в YAML/JSON/RU config | done | `REVIEW_PACK_DATASET_RAILS_LOCKED_NO_TRAINING` | approved review-pack |
| Собрать `X439_SOURCE` | pending | Единый causal X439 слой по base 32d + reviewed 21d, без review/manual/future в X | dataset builder |
| Собрать `ENTRY_TRAIN_DATASET` | pending | Ожидаемо `3285 rows`, `GOOD=517`, `BAD=2768` | X439_SOURCE + approved pack |
| Собрать `RISKGATE_TRAIN_DATASET` | pending | `risk_bad_y=1` positives `400`, negatives только explicit safe | X439_SOURCE + approved pack |
| Прогнать dataset guards | pending | Проверить allowlist 439, join labels, no future, no duplicates, `risk_bad_y=1 -> entry_y=0` | оба dataset |
| Запускать training | blocked | Только после dataset guards + training guard PASS | user command after guards |

## 2026-07-21 STAS5 V5C Review Pack R2/R3/R4

Статус: `done`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать единый approved review-pack по R2/R3/R4 | done | `STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1` | approved review ledgers |
| Проверить 21 день и связь PNG с CSV/JSON | done | `21/21`, `21` current PNG, `21` visual manifest | review folders |
| Проверить ENTRY/RiskGate targets | done | `ENTRY rows=689`, `GOOD=227`, `BAD=462`, `RISK BAD=400` | review pack guard |
| Проверить, что каждый risk BAD является ENTRY BAD | done | `risk_bad_also_entry_bad PASS`, конфликтов нет | two-target contract |
| Запустить обучение | blocked | Сначала собрать train dataset с применением review-pack и пройти отдельный dataset/training guard | user approval + next builder |
| Следующий технический шаг | current_next | Сделать builder, который применит pack к базовой train-цепочке и сформирует ENTRY/RiskGate train targets без ручных полей в X439 | review pack PASS |

## 2026-07-20 STAS5 V5C Current Review Cleanup

Статус: `done`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сделать один официальный PNG в корне дня | done | `*_CURRENT_REVIEW.png` | review ladder |
| Убрать старые/preview PNG из корня без удаления | done | `_visual_archive/` | review ladder/gallery |
| Связать current PNG с цифрами | done | `*_CURRENT_VISUAL_MANIFEST_V1.json` | approved ledgers |
| Пересобрать контрольный R2 `2026-03-01` | done | `ENTRY GOOD=10`, `ENTRY BAD=26`, `RISK BAD=21` | user review |
| Обновить R2 gallery | done | В day folder витрины тоже один `CURRENT_REVIEW.png` | review gallery |

## 2026-07-20 STAS5 V5C Review LA Labels Above Markers

Статус: `done`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Поднять `LAxxx` над review-кругами/квадратами | done | Renderer рисует review overlay раньше, затем `LAxxx` верхним слоем | user OK |
| Сохранить старую компактную раскладку подписей | done | Для review-точек добавлен только небольшой подъем подписи | visual renderer |
| Пересобрать R2/R3/R4 gallery | done | `STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/` | review gallery |
| Проверить код и профильные тесты | done | `py_compile PASS`, `pytest 6 passed` | local checks |

## 2026-07-20 STAS5 V5C Review Gallery

Статус: `done`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сделать общую папку R2/R3/R4 review-графиков | done | `STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/` | review artifacts |
| Пересобрать R2 визуально | done | `7` дней, `14` PNG | R2 approved ledgers |
| Пересобрать R3 визуально | done | `7` дней, `14` PNG | R3 approved ledgers |
| Пересобрать текущий R4 визуально | done | `2026-03-18`, `2` PNG | R4 approved ledger |
| Диктовать новые правки по R2/R3/R4 | user_next | Использовать review ladder, затем обновлять gallery round | user review |

## 2026-07-20 STAS5 V5C ENTRY/RiskGate Two Targets

Статус: `done`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать отдельные цели `entry_y` и `risk_bad_y` поверх одних строк `X439` | done | Использовать этот контракт при следующей сборке RiskGate/обучении | user OK |
| Зафиксировать `риск плохо` как ENTRY BAD + RiskGate BAD | done | `риск плохо` пишет `entry_y=0 + risk_bad_y=1` | review ladder |
| Не пускать ручные review/risk поля в live features | done | Guard должен держать `entry_y/risk_bad_y/phase_y/state_y/reason_y` вне `X439` | no-future contract |

## STAS5 V5C Quick Review Ladder

Статус: `READY_FOR_USER_R4_REVIEW_LABELS`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать диктовку ENTRY vs RiskGate | done | `риск хорошо` запрещен, `риск плохо` отдельный слой | user decision |
| Сделать быстрый parser/ledger | done | `stas5_v5c_review_ladder.py` | code |
| Сделать PowerShell wrapper | done | `run_stas5_v5c_review_ladder.ps1` | code |
| Проверить parser/smoke | done | `21 passed`, `-Stage Parse` PASS | tests |
| Размечать R4/RiskGate дни `2026-03-14..2026-03-20` | user_next | Пользователь диктует фразы по графикам, команда сохраняет ledgers | visual review |
| Пересобрать день в V5 package | manual_next | Только после закрытия дня, `-Stage All -Approve` | approved review |
| Делать training | blocked | Только после закрытия review-недели и отдельного batch/training guard PASS | review week |

## STAS5 V5C RiskGate Taxonomy V1

Статус: `IMPLEMENTED_AUDIT_ONLY_NEXT_MULTI_DAY_REVIEW`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Завести полный список режимов RiskGate | done | `RISK_GATE_TAXONOMY_V1` в коде и YAML | user OK |
| Добавить audit-колонки `RISK_GATE_PRIMARY_REGIME` и `RISK_GATE_TAGS` | done | Смотреть CSV/PNG в `riskgate_audit` | code |
| Добавить флаги/score по каждому режиму | done | `RISK_MODE_*_SCORE/FLAG` в CSV | code |
| Сохранить старую лестницу действий | done | `BLOCK_HARD/BLOCK_RISK/WARN_RISK/PASS_*` не заменены режимами | guardrail |
| Пересобрать `2026-03-18` | done | PASS; `BLOCK_HARD=6`, `BLOCK_RISK=3`, `WARN_RISK=3`, `PASS_USER_REBOUND=3` | R3 forward |
| Прогнать RiskGate Taxonomy V1 по всей неделе `2026-03-14..2026-03-20` | current_next | Только `-Mode RiskGate`, без training/forward | user command |
| Переводить RiskGate в enforce | blocked | Только после multi-day audit, guard PASS и ручного подтверждения | user review |

## STAS5 V5C RiskGate Audit-Only

Статус: `IMPLEMENTED_AUDIT_ONLY_NEXT_MULTI_DAY_REVIEW`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать RiskGate как отдельный audit-only режим | done | Использовать `-Mode RiskGate` | user approval |
| Подключить PowerShell-команду | done | `run_stas5_v5c_continuous_train_forward.ps1 -Mode RiskGate` | module |
| Проверить на `2026-03-18` | done | PASS, user pass ids `LA059,LA067,LA078` | R3 forward |
| Прогнать RiskGate audit по всей неделе `2026-03-14..2026-03-20` | current_next | После команды пользователя, без training/forward | implemented audit |
| Переводить RiskGate в enforce | blocked | Только после multi-day audit, guard PASS и ручного подтверждения | user review |

## STAS5 V5C RiskGate Preview 2026-03-18

Статус: `V1_USER_PASS_DONE_NEXT_RISKGATE_EXCEPTION_RULES`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать RiskGate V0 preview для `2026-03-18` | done | Смотреть PNG/CSV в `riskgate_preview/20260318` | R3 forward week3 |
| Зафиксировать три проходящих входа пользователя | done | `LA059`, `LA067`, `LA078` сохранены как `PASS_USER_REBOUND` в V1 preview | user screenshot |
| Сформировать правило исключений rebound/retest | current_next | Вывести признаки, которые отличают `LA059/LA067/LA078` от плохих `BLOCK_HARD` | V1 user-pass |
| Перенести RiskGate из preview в кодовый `audit_only` overlay | pending | Сначала с учетом исключений `GOOD_REBOUND/GROUNDING/RETEST`, без enforce | user OK |
| Включать RiskGate enforce | blocked | Только после отдельного guard PASS и review нескольких дней | audit_only results |

## STAS5 V5C Freeze Two-Block

Статус: `ENTRY_TWO_BLOCK_FROZEN_DONE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Заморозить `ENTRY_ML_TWO_BLOCK` | done | В YAML стоит `enabled=false`, `mode=frozen_not_selected` | user decision |
| Не тратить время на Block 3 | done | Оставить артефакт для истории, не считать active entry | YAML |
| Сфокусироваться на baseline + RiskGate | current_next | Подключать `RISK_GATE_RULE_V0` только как `audit_only` overlay | user OK |

## STAS5 V5C YAML Comments

Статус: `YAML_COMMENTS_DONE_NEXT_RISKGATE_AUDIT_ONLY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Расписать русские комментарии в YAML по каждому ML-блоку | done | Комментарии добавлены в `STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml`; YAML validation PASS | YAML config |
| Подключить код к YAML | pending | Отдельным шагом, без запуска training | user OK |
| Подключить RiskGate V0 | current_next | Только `audit_only` overlay | YAML + user OK |

## STAS5 V5C YAML Control Config

Статус: `YAML_CONFIG_READY_NEXT_RISKGATE_AUDIT_ONLY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Перевести ML control config в один YAML | done | Главный файл: `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml` | user approval |
| Пометить JSON/RU как reference | done | JSON/RU оставлены как справка, не source-of-truth | YAML |
| Подключить код к YAML | pending | Отдельным шагом добавить чтение YAML в раннеры/guard, без запуска training | YAML |
| Подключить RiskGate V0 | current_next | Только `audit_only` overlay рядом с текущими predictions | YAML + user OK |

## STAS5 V5C ML Control Config / RiskGate Rails

Статус: `CONFIG_READY_NEXT_RISKGATE_AUDIT_ONLY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать единый config ML-блоков | done | `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json` и `_RU.md` созданы | R3 train/forward manifests |
| Зафиксировать активную ML | done | `ENTRY_BASELINE_ML` выбран как текущий entry alpha; `ENTRY_ML_TWO_BLOCK` обучен, но не выбран | R3 train manifest |
| Зафиксировать будущий safety-контур | done | `RISK_GATE_RULE_V0` описан как `planned_audit_only`; `DUMP_AVOID_ML` и `REBOUND_ALLOW_ML` выключены | user risk discussion |
| Подключить RiskGate V0 overlay | current_next | Делать отдельным артефактом рядом с forward predictions, не перезаписывая текущий CSV | config V1 |
| Сделать RiskGate guard | pending | Проверить only X439 causal risk columns, `RISK_SOURCE_MAX_TIME_UTC <= entry_time_utc`, no future/manual target leakage | RiskGate V0 |
| Переводить RiskGate в enforce | blocked | Только после audit-only PASS и ручной проверки, что плохие дампы блокируются, а хорошие rebound-входы сохраняются | user review |

## STAS5 V5C R3 Train / Next Blind Forward

Статус: `R3_TRAIN_PASS_WAIT_USER_RUN_FORWARD_WEEK3`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать R3 user review `2026-03-07..2026-03-13` | done | Approved-ledger создан, `GOOD=73`, `BAD=34` в review-слое | user labels |
| Пересобрать дневные V5 passports `2026-03-07..2026-03-13` | done | В дневных CSV `GOOD=73`, `BAD=481`, features `439`, guards PASS | approved GoodIds |
| Собрать R3 batch `2026-01-27..2026-03-13` | done | `rows=3726`, `entry_y 1=432`, `entry_y 0=3294`, `features=439` | day packages |
| Проверить R3 batch guard | done | `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING` | batch |
| Запустить R3 TrainingGuard | done | `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING` | R3 batch PASS |
| Запустить R3 Train | done | Post-train guard `PASS_V5_TWO_BLOCK_POST_TRAIN_GUARD_READY_FOR_FORWARD` | training guard |
| Проверить/подготовить следующую неделю свечей | done | `2026-03-14..2026-03-20` OHLCV `part-final.csv` существуют | trained R3 model |
| Запустить следующий blind-forward | user_next | Пользователь запускает forward week3 командой из `docs/codex/commands.md` | trained R3 model |

## STAS5 V5C R2Q WideReview Week2 User Review For R3

Статус: `R3_REVIEW_20260307_DRAFT_WAIT_USER_CONFIRM_CLOSE_DAY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать wide-review прогон `2026-03-07..2026-03-13` | done | Контрольный файл создан рядом с run | wide_v2 manifest |
| Проверить фактические counts | done | `ENTER=64`, `WATCH=167`, `SKIP=323`, visual PNG `14` | predictions CSV |
| Принять ручную разметку пользователя по `2026-03-07` | done | Draft сохранен: `GOOD=9`, `BAD=4`, `LA057=BAD` | visual review |
| Подтвердить закрытие `2026-03-07` | user_next | Пользователь говорит `7 марта день закрыт` или дает правки | draft review |
| Принять ручную разметку пользователя по `2026-03-08` | done | Draft сохранен: `GOOD=10`, `BAD=5`; `LA027/LA031/LA064` как пропущенные GOOD | visual review |
| Подтвердить закрытие `2026-03-08` | user_next | Пользователь говорит `8 марта день закрыт` или дает правки | draft review |
| Принять ручную разметку пользователя по `2026-03-09` | done | Draft сохранен: `GOOD=12`, `BAD=1`; `LA067` marker=`yellow_diamond`/GOOD | visual review |
| Подтвердить закрытие `2026-03-09` | user_next | Пользователь говорит `9 марта день закрыт` или дает правки | draft review |
| Принять ручную разметку пользователя по `2026-03-10` | done | Draft сохранен: `GOOD=9`, `BAD=7`; `LA052` только context note, не label | visual review |
| Подтвердить закрытие `2026-03-10` | user_next | Пользователь говорит `10 марта день закрыт` или дает правки | draft review |
| Принять ручную разметку пользователя по `2026-03-11` | done | Draft сохранен: `GOOD=12`, `BAD=0`; `LA058` только context note, не label | visual review |
| Подтвердить закрытие `2026-03-11` | user_next | Пользователь говорит `11 марта день закрыт` или дает правки | draft review |
| Принять ручную разметку пользователя по `2026-03-12` | done | Draft сохранен: `GOOD=12`, `BAD=4`; `LA055` крестик GOOD, `LA070/LA086` ромбики GOOD | visual review |
| Подтвердить закрытие `2026-03-12` | user_next | Пользователь говорит `12 марта день закрыт` или дает правки | draft review |
| Принять ручную разметку пользователя по `2026-03-13` | done | Draft сохранен: `GOOD=9`, `BAD=13`; плохая серия `LA046..LA053`, context pump-dump | visual review |
| Подтвердить закрытие `2026-03-13` | user_next | Пользователь говорит `13 марта день закрыт` или дает правки | draft review |
| Сохранять R3 review-ledger по каждому дню | in_progress | Не терять BAD для плохих зеленых входов; GOOD ids собрать отдельно | user labels |
| Пересобрать дневной V5 passport `2026-03-07` с GoodIds | blocked | Только после подтверждения закрытия дня | approved review-ledger |
| Собрать R3 batch `2026-01-27..2026-03-13` | blocked | Только после закрытия всех 7 дней `2026-03-07..2026-03-13` | approved day packages |
| R3 training | blocked | Только после R3 batch guard PASS | R3 batch |
| Следующий blind-forward | blocked | Только на новой неделе после `2026-03-13`, не на уже размеченной week2 | R3 model |

## STAS5 V5C R2Q Forward Threshold Rerun

Статус: `CODE_FIXED_WAIT_USER_FORWARD_RERUN`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Найти причину малого числа ENTER в `Normal` | done | Старый `Normal` был `p96.5/p81.5`, на week2 дал только `ENTER=5` | user feedback |
| Расширить `Normal` и `WideReview` без forward-label tuning | done | `Normal=p90/p60`, `WideReview=p80/p50`; пороги считаются только по train OOF | code |
| Проверить ожидаемые counts на готовом week2 score | done | `Normal ENTER=25/WATCH=148`, `WideReview ENTER=64/WATCH=167` | existing forward scores |
| Проверить код | done | `py_compile PASS`; PS syntax `PASS`; pytest `7 passed` | code |
| Запустить новый forward-график | user_next | Команда в `docs/codex/commands.md`, рекомендован `-EntryDecisionPolicy WideReview` и run_id `stas5_v5c_r2q_forward_20260307_20260313_wide_v2` | user |

## STAS5 V5C R2Q Train Retry After Multiclass Fix

Статус: `CODE_FIXED_WAIT_USER_RETRY_TRAIN`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| R2Q TrainingGuard `stas5_v5c_r2q_train_20260127_20260306` | done | Guard PASS: `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING` | R2Q batch |
| Исправить падение Train на multiclass phase/state | done | `MARKET_PHASE_STATE_ML` переведен на `PHASE_STATE_MODEL_KIND=extra_trees_balanced` | train traceback |
| Проверить код | done | `py_compile PASS`; `pytest tests/test_stas5_v5_two_block_ml.py tests/test_stas5_v5_continuous_ml.py` = `5 passed` | code fix |
| Повторить R2Q Train | user_next | Запустить ту же `-Mode Train` команду с run_id `stas5_v5c_r2q_train_20260127_20260306` | user |
| Запустить diagnostic forward week2 | blocked | Только после post-train guard PASS | trained model |

## STAS5 V5C R2Q Quality-Fix Train / Forward

Статус: `CODE_FIXED_WAIT_USER_RUN_TRAINING_GUARD`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Аудит R2 lineage с агентами | done | Старый R1 не подмешан; R2 labels вошли в train | R2 artifacts |
| Найти причину слабого качества | done | Причина: слабый вес свежих labels, p90 threshold, SGD phase/state warnings, two-block без selector | metrics audit |
| Исправить ML-рельсу | done | Sample weights, precision/Wilson threshold, ExtraTrees candidate, stable phase/state, raw-proba guard, baseline/two-block selector | code |
| Проверить код | done | `py_compile PASS`, targeted pytest `4 passed`, temp smoke train PASS | tests |
| Запустить R2Q TrainingGuard | user_next | Команда в `docs/codex/commands.md`, run_id `stas5_v5c_r2q_train_20260127_20260306` | user |
| Запустить R2Q Train | blocked | Только после TrainingGuard PASS; запускает пользователь | training guard |
| Запустить R2Q diagnostic forward week2 | blocked | Только после post-train guard PASS; это диагностический повтор, не новый human-blind proof | trained model |

## STAS5 V5C R2 Train / Forward Week2

Статус: `R2_BATCH_PASS_WAIT_USER_RUN_TRAINING_GUARD`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Параметризовать V5C train range для R2 | done | `BuildBatch`, `TrainingGuard`, `Train` используют `TrainStartDay/TrainEndDay` | code |
| Собрать R2 continuous batch `2026-01-27..2026-03-06` | done | Guard `PASS`, rows `3172`, GOOD `359`, BAD `2813`, features `439` | reviewed week1 |
| Проверить свечи week2 `2026-03-07..2026-03-13` | done | Все 7 OHLCV `part-final.csv` существуют | data |
| Запустить R2 TrainingGuard | user_next | Пользователь запускает команду из `docs/codex/commands.md`; Codex не запускал обучение | R2 batch PASS |
| Запустить R2 Train | blocked | Только после `TrainingGuard PASS`; запуск делает пользователь | training guard |
| Запустить blind forward week2 | blocked | Только после сохраненной R2 модели и post-train guard PASS; forward range `2026-03-07..2026-03-13` | trained R2 model |
| Review week2 графиков | pending | После forward открыть `visual_review`, отметить GOOD/BAD для R3 teacher | forward week2 |

## STAS5 V5C R2 User Review Week

Статус: `R2_REVIEW_WEEK_20260228_20260306_CLOSED_READY_FOR_R2_BATCH_GUARD`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Исправить кракозябы в R2 review-ledger за все закрытые дни | done | UTF-8 audit `PASS`, `GoodIds/BAD/entry_y` не менялись | text encoding audit |
| Зафиксировать пользовательскую разметку `2026-02-28` | done | Review-ledger сохранен в `artifacts/v5c/review/r2_user_review/20260228/` | user approval |
| Собрать approved day package `2026-02-28` | done | Guard `PASS`, `rows=81`, `entry_y 1=10 / 0=71`, `features=439` | GoodIds |
| Зафиксировать пользовательскую разметку `2026-03-01` | done | Review-ledger сохранен в `artifacts/v5c/review/r2_user_review/20260301/` | user approval |
| Собрать approved day package `2026-03-01` | done | Guard `PASS`, `rows=81`, `entry_y 1=9 / 0=72`, `features=439` | GoodIds |
| Зафиксировать пользовательскую разметку `2026-03-02` | done | Review-ledger сохранен в `artifacts/v5c/review/r2_user_review/20260302/` | user approval |
| Собрать approved day package `2026-03-02` | done | Guard `PASS`, `rows=81`, `entry_y 1=12 / 0=69`, `features=439` | GoodIds |
| Зафиксировать пользовательскую разметку `2026-03-03` | done | Review-ledger сохранен в `artifacts/v5c/review/r2_user_review/20260303/` | user approval |
| Собрать approved day package `2026-03-03` | done | Guard `PASS`, `rows=89`, `entry_y 1=12 / 0=77`, `features=439` | GoodIds |
| Зафиксировать пользовательскую разметку `2026-03-04` | done | Review-ledger сохранен в `artifacts/v5c/review/r2_user_review/20260304/` | user approval |
| Собрать approved day package `2026-03-04` | done | Guard `PASS`, `rows=72`, `entry_y 1=9 / 0=63`, `features=439` | GoodIds |
| Зафиксировать пользовательскую разметку `2026-03-05` | done | Review-ledger сохранен в `artifacts/v5c/review/r2_user_review/20260305/` | user approval |
| Собрать approved day package `2026-03-05` | done | Guard `PASS`, `rows=85`, `entry_y 1=11 / 0=74`, `features=439` | GoodIds |
| Зафиксировать пользовательскую разметку `2026-03-06` | done | Review-ledger сохранен в `artifacts/v5c/review/r2_user_review/20260306/` | user approval |
| Собрать approved day package `2026-03-06` | done | Guard `PASS`, `rows=87`, `entry_y 1=6 / 0=81`, `features=439` | GoodIds |
| Собрать R2 train dataset | current_next | Объединить закрытую teacher-неделю `2026-02-28..2026-03-06` с базой по утвержденному R2-правилу и проверить отдельным R2 batch guard | reviewed days |
| Запустить R2 training | blocked | Только после R2 batch guard PASS; `2026-02-28..2026-03-06` после включения в train уже не считать blind proof | R2 dataset |

## STAS5 V5C WAVE Strip Cumulative Carry

Статус: `USER_APPROVED_VISUAL_STANDARD_DONE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Растянуть active WAVE до конца доступных свечей дня | done | Смотреть новые overview PNG | V5C visual renderer |
| Убрать черный хвост после active LONG/SHORT | done | Manifest: `macro_wave_strip_covers_available_candle_end=PASS` | WAVE rows |
| Перевести подписи WAVE на cumulative percent от настоящего старта волны | done | Читать `cum start->end%` на cross-day кусках | ohlcv_contexts |
| Не менять ML predictions | done | SHA256 predictions до/после render совпал | no-future contract |
| Утвердить формат графиков | done | Пользователь подтвердил 2026-07-17: графики норм | user approval |
| Ручной review входов | current_next | Проверить `62 ENTER` на утвержденных графиках с корректной WAVE-полосой | user review |

## STAS5 V5C Forward Visual Review Continuous Strip

Статус: `USER_APPROVED_VISUAL_STANDARD_DONE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить в V5C forward overview блок `Fon / LONG / SHORT / WAVE` | done | Использовать новые PNG в `visual_review` | V5C forward predictions |
| Сохранить текущие маркеры `LAxxx / SKIP X / WATCH diamond / ENTER triangle` | done | Визуально проверять входы на обновленных графиках | renderer |
| Убрать серый дневной `GAP` в WAVE | done | Manifest: `rendered_gap_rows_total=0` | ohlcv_contexts |
| Не менять обучение и predictions | done | SHA256 predictions до/после render совпал | no-future contract |
| Ручная оценка `62 ENTER` | current_next | Отметить хорошие/плохие входы по новым графикам с блоком силы | user review |

## STAS5 V5C Continuous Train + Forward

Статус: `V5C_CONTINUOUS_FORWARD_READY_USER_REVIEW_NEXT`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сделать отдельный V5C continuous-контур без перезаписи дневного V5 | done | Использовать `STAS5_ML_CORE/artifacts/v5c/` | V5 дневной PASS |
| Пересобрать train X439 с rolling continuous warmup | done | Batch guard `PASS`, `rows=2596`, `features=439` | daily V5 approved 274 |
| Проверить отсутствие midnight-reset | done | `2026-02-28 LA001: cs_context_rows=748, cs_rows_240m=240` | V5C forward dataset |
| Обучить V5C two-block ML | done | Run `stas5_v5c_continuous_train_20260716_154826`, post-train guard PASS | V5C batch guard |
| Прогнать blind forward `2026-02-28..2026-03-06` | done | Run `stas5_v5c_continuous_forward_20260228_20260306_20260716_155343`, guard PASS | V5C trained model |
| Построить forward visual review | done | `14` PNG, все LA labels, ENTER triangles | V5C forward predictions |
| Визуально проверить `62 ENTER` | current_next | Открыть `visual_review` и отметить хорошие/плохие входы | user review |
| Сравнить V5C continuous с дневным V5 и baseline | current_next | Дневной V5: `ENTER=20`; V5C: `ENTER=62`; OOF two-block чуть лучше baseline, но нужна проверка глазами | review |
| Выбирать production-схему | blocked | Только после ручного review и сравнения | review |

## STAS5 V5 Forward Visual Review With All LA Labels

Статус: `VISUAL_REVIEW_PNG_READY_USER_REVIEW_NEXT`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить V5 forward-графики со всеми желтыми `LAxxx` и без длинных `ENTER`-стрелок | done | Использовать `visual_review/*/*_ENTER_ARROWS.png`; имя файла старое, внутри новый стиль | V5 forward predictions |
| Добавить closeup-листы по каждому `ENTER` | done | Использовать `visual_review/*/*_ENTER_CLOSEUPS_YYYYMMDD.png` | V5 forward predictions |
| Подключить рендер к будущему V5 forward | done | `Forward` строит visual review автоматически; `RenderForward` дорисовывает уже готовый run | wrapper |
| Проверить текущий run `2026-02-28..2026-03-06` | done | Manifest `PASS`, `png_count=14` | OHLCV |
| Ручной visual review 20 `ENTER` | current_next | Смотреть обзорные PNG и closeups, помечать хорошие/плохие входы | user review |

## STAS5 V5 Two-Block Train + Forward Done

Статус: `REVIEW_REQUIRED_AFTER_FORWARD`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать V5 two-block training/forward module | done | Использовать `src/mlbotnav/stas5_v5_two_block_ml.py` | TZ + batch guard |
| Реализовать wrapper `run_stas5_v5_two_block_ml.ps1` | done | Запускать `TrainingGuard`, `Train`, `Forward`, `TrainForward` | module |
| Запустить training guard на 32 днях | done | Guard `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING` | batch guard PASS |
| Обучить `ENTRY_BASELINE_ML`, `MARKET_PHASE_STATE_ML`, `ENTRY_ML` | done | Run `stas5_v5_two_block_train_20260716_32d` | training guard |
| Post-train guard | done | Guard `PASS_V5_TWO_BLOCK_POST_TRAIN_GUARD_READY_FOR_FORWARD` | trained models |
| Собрать FULL274/X439 forward `2026-02-28..2026-03-06` | done | 7 дней, `576` rows, all day full guards PASS | OHLCV |
| Запустить blind/no-future forward | done | `ENTER=20`, `WATCH=120`, `SKIP=436` | post-train guard |
| Проверить 20 `ENTER` глазами | current_next | Открыть forward predictions/report и разметить качество входов | forward done |
| Сравнить two-block с baseline-forward | current_next | Baseline сильнее по OOF, нужен baseline forward для честного выбора | trained baseline |
| Назначить production-схему | blocked | Только после review; two-block пока не доказал преимущество | review |

## STAS5 V5 Two-Block ML TZ Ready

Статус: `TZ_READY_NEXT_TRAINING_GUARD_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Расписать ТЗ `STAS5 V5 Two-Block ML` вместе с агентом | done | Читать `STAS5_ML_CORE/09_STAS5_V5_TWO_BLOCK_ML_TZ_RU.md` | batch guard PASS |
| Зафиксировать baseline как обязательный контроль | done | `ENTRY_BASELINE_ML: X439 -> entry_y` сравнивается с two-block | TZ |
| Зафиксировать OOF-правило для `ENTRY_ML` | done | На train только OOF phase/state predictions, на forward только live predictions | TZ |
| Реализовать `STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1` | current_next | Проверить batch guard, `X439`, forbidden columns, OOF policy, split, no model/forward artifacts | TZ + batch guard PASS |
| Запускать baseline/training | blocked | Только после training guard `PASS` и отдельной команды пользователя | training guard |
| Запускать forward | blocked | Только после сохраненной модели и post-train guard `PASS` | trained model |

## STAS5 V5 Batch Dataset And Guard Done

Статус: `BATCH_GUARD_PASS_NEXT_TRAINING_GUARD`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать единый V5 batch dataset `2026-01-27..2026-02-27` | done | Использовать `STAS5_V5_BATCH_20260127_20260227_ML_READY_439F_TARGETS_V1.csv` | range audit PASS |
| Создать batch feature allowlist `439F` | done | Использовать только `FEATURE_ALLOWLIST_439F_V1.json` как `X` контракт | daily allowlists |
| Сделать batch leakage/no-future guard | done | Guard `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING` | batch dataset |
| Нормализовать пустые feature values | done | В batch `feature_nulls=0`; заполнение только в `X`, targets не тронуты | batch builder |
| Реализовать training guard | current_next | Проверить `X=439`, targets не в `X`, OOF-схему, split, model output paths, no forward before model | batch guard PASS |
| Реализовать `MARKET_PHASE_STATE_ML` | pending | Учить `phase_y/state_y` только по 439 causal features | training guard |
| Сформировать OOF phase/state predictions | pending | Для train `ENTRY_ML` использовать только OOF predictions первого блока | phase/state model |
| Реализовать `ENTRY_ML` | pending | Учить `entry_y` по 439 causal features + OOF/live predictions, без настоящих `phase_y/state_y` в `X` | OOF predictions |
| Запустить forward | blocked | Только после сохраненной модели и guard `PASS` | trained V5 |

## STAS5 V5 Batch Dataset And Guard After 32 Full-Ready Days

Статус: `CURRENT_NEXT`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Закрыть диапазон `2026-01-27..2026-02-27` | done | `32/32` full-ready, `rows=2596`, `entry_y 1=290 / 0=2306` | daily packages |
| Исправить missing `2026-02-07` | done | День пересобран по GOOD ids, full guard `PASS`, карта создана | existing FULL274 + user ids |
| Сделать range audit | done | Читать `STAS5_ML_CORE/artifacts/v5/STAS5_V5_RANGE_AUDIT_20260127_20260227_RU.md` | full-ready range |
| Собрать единый V5 batch dataset | current_next | Новый builder должен объединить 32 дневных `ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv` | range audit PASS |
| Сделать batch leakage/no-future guard | pending | Проверить одинаковый allowlist `439`, targets не в X, forbidden/future/source-time leakage отсутствуют | batch dataset |
| Реализовать `MARKET_PHASE_STATE_ML` | pending | Учить `phase_y/state_y` только по causal X | batch guard PASS |
| Сделать OOF phase/state predictions | pending | Для train `ENTRY_ML` использовать только OOF, не истинные `phase_y/state_y` | phase model |
| Реализовать `ENTRY_ML` | pending | Учить `entry_y` по causal X + OOF/live phase preds | phase OOF |
| Запустить blind forward | blocked | Только после training guard и сохраненной модели | trained V5 |

## STAS5 V5 Six Full-Ready Days Before Batch Training

Статус: `AUDIT_PASS_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить `2026-02-01` по V5 full-causal контракту | done | Audit report: `STAS5_ML_CORE/artifacts/v5/market_passports/20260201/STAS5_V5_MARKET_PASSPORT_20260201_AUDIT_RU.md` | daily package |
| Сверить GOOD ids `2026-02-01` | done | В CSV `entry_y=1` есть `14` GOOD; порядок по времени | user ids |
| Проверить no-future для `cs_*` и `fcs_*` | done | Нарушений `0` | guards |
| Проверить общий V5 folder audit | done | `full-ready=6`, `partial/not-ready=27`, `model=False`, `forward=False` | daily packages |
| Зафиксировать два будущих ML-блока | done | `MARKET_PHASE_STATE_ML` -> `ENTRY_ML`; пока не обучались | training schema |
| Собрать batch dataset по full-ready дням | current_next | Делать отдельной командой и отдельным batch guard | 6 full-ready days |
| Запустить V5 training / forward | blocked | Не запускать до batch dataset и batch leakage guard | batch guard |

## STAS5 V5 Approved Day Flow 2026-01-28

Статус: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать builder approved-passport из списка GOOD ids | done | Использовать `STAS5_ML_CORE/run_stas5_v5_approved_passport_builder.ps1` | FULL274 run + user GOOD ids |
| Подключить `-GoodIds` к day ladder | done | Запускать одну команду `run_stas5_v5_day_ladder.ps1 -Stage All -GoodIds ...` | approved builder |
| Собрать approved baseline для `2026-01-28` | done | `rows=93`, `entry_y 1=9 / 0=84`, `feature_count=274` | user ids |
| Собрать `cs_*` для `2026-01-28` | done | `feature_count=355`, guard `PASS` | approved baseline |
| Собрать `fcs_*` для `2026-01-28` | done | `feature_count=439`, guard `PASS`; карта создана | cs layer |
| Обновить V5 folder audit | done | `full-ready=2`, `partial/not-ready=31`, `model=False`, `forward=False` | full day package |
| Следующий день | current_next | Пользователь дает новый день и GOOD ids; запускать ту же лестницу с `-GoodIds` | next screenshot/review |
| Batch dataset / training / forward | blocked | Не запускать, пока не будет пачки full-ready дней и отдельного batch guard | multiple approved days |

## STAS5 V5 Day Ladder And Folder Audit

Статус: `PASS_V5_FOLDER_AUDIT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать главную лесенку дня | done | Использовать `STAS5_ML_CORE/run_stas5_v5_day_ladder.ps1` | V5 daily flow |
| Создать аудит V5-папки | done | Использовать `STAS5_ML_CORE/run_stas5_v5_folder_audit.ps1` | V5 artifacts |
| Проверить лесенку на готовом дне | done | `2026-01-27 Stage All -NoPlot` прошел: `features=439`, guard `PASS` | approved day |
| Проверить stop-guard на неготовом дне | done | `2026-01-28 Stage All` остановился на missing approved passport, FULL274 найден | no approved passport |
| Сделать approved passport для следующего дня | current_next | Пользователь выбирает день, мы разбираем график и создаем approved targets; после этого `Stage BuildApproved` | manual review |
| Batch dataset / training / forward | blocked | Не запускать, пока нет нескольких full-ready days и batch guard | batch guard |

## STAS5 V5 Full Causal Market-Structure Builder

Статус: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать full causal market-structure builder | done | Использовать `src/mlbotnav/stas5_v5_full_causal_structure_builder.py` или wrapper `STAS5_ML_CORE/run_stas5_v5_full_causal_structure_builder.ps1` | approved market passport + cs builder |
| Собрать `fcs_*` признаки для `2026-01-27` | done | Главный output: `STAS5_V5_MARKET_PASSPORT_20260127_FULL_STRUCTURE_CANDIDATE_FEATURES_CAUSAL_V1.csv` | OHLCV + `274F_PLUS_CAUSAL` |
| Собрать уровни/каналы/режимы/события | done | Outputs: `LEVELS_CAUSAL_V1`, `CHANNELS_CAUSAL_V1`, `REGIMES_CAUSAL_V1`, `EVENTS_CAUSAL_V1` | full builder |
| Собрать ML-ready `274F + cs_* + fcs_* + targets` | done | Использовать `STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv` как текущий главный CSV дня | full causal builder |
| Создать allowlist `274 + cs_* + fcs_*` | done | Использовать `STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json` | guard |
| Проверить no-future guard | done | Guard `PASS`: targets не в X, forbidden features отсутствуют, `fcs_max_source_time_utc < entry_time_utc` | full causal guard |
| Создать полную карту структуры | done | Открывать `DAY_MARKET_PASSPORT_20260127_FULL_CAUSAL_STRUCTURE_MAP_V1.png` | plot |
| Обновить навигацию дня | done | Открывать первым `00_OPEN_FIRST_RU.md`; текущая версия = `PLUS_FULL_CAUSAL_STRUCTURE` | docs |
| Собрать такие же full-пакеты на следующие январские дни | next | Для каждого дня: FULL274 -> ручной паспорт -> targets -> causal builder -> full causal builder -> guard PASS | user-approved days |
| Собрать общий batch dataset | pending | Только после нескольких approved дней; нужен отдельный batch guard | daily packages |
| Запустить V5 training / forward | blocked | Не запускать на одном дне; сначала batch dataset и batch no-future guard | batch guard |

## STAS5 V5 Causal Market-Structure Builder Previous `cs_*` Layer

Статус: `PASS_NO_TRAINING_CAUSAL_STRUCTURE_READY`. Это предыдущий слой; текущий главный слой выше: `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать causal market-structure builder | done | Использовать `src/mlbotnav/stas5_v5_causal_structure_builder.py` или wrapper `STAS5_ML_CORE/run_stas5_v5_causal_structure_builder.ps1` для дневных V5-пакетов | approved market passport |
| Собрать `cs_*` признаки для `2026-01-27` | done | Главный output: `STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_FEATURES_V1.csv` | OHLCV + ML-ready V2 |
| Собрать ML-ready `274F + cs_* + targets` | done | Использовать `STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv` как source/base для full-слоя | causal builder |
| Создать allowlist `274 + cs_*` | done | Использовать `STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_PLUS_CAUSAL_STRUCTURE_V1.json` | guard |
| Проверить no-future guard | done | Guard `PASS`: targets не в X, forbidden features отсутствуют, `source_time_before_entry=PASS` | causal guard |
| Обновить навигацию дня | done | Открывать первым `00_OPEN_FIRST_RU.md`; старый `ENTRY_PHASE...V2` считать baseline без `cs_*` | docs |
| Сделать аудит V5 по проекту | done | Читать `STAS5_ML_CORE/artifacts/v5/STAS5_V5_PROJECT_AUDIT_20260715_RU.md` | local audit |
| Собрать такие же пакеты на следующие январские дни | next | Для каждого дня: FULL274 -> ручной паспорт -> targets -> causal builder -> guard PASS | user-approved days |
| Собрать общий batch dataset | pending | Только после нескольких approved дней; нужен отдельный batch guard | daily packages |
| Запустить V5 training / forward | blocked | Не запускать на одном дне; сначала batch dataset и batch no-future guard | batch guard |

## STAS5 V5 Market Passport 2026-01-27 Phase/State/Reason Ready

Статус: `PASS_NO_TRAINING_PHASE_STATE_REASON_READY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `entry_y/phase_y/state_y/reason_y` target-слой | done | Использовать `ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv` как актуальный ML-ready source для этого дня | approved V3 |
| Зафиксировать 5 фаз `phase_y` | done | `P1_RANGE_CHOP=15`, `P2_SLOW_DRIFT_SHORT_PRESSURE=26`, `P3_FLUSH_BASE=6`, `P4_PUMP_PULLBACK_DUMP=7`, `P5_LATE_CONTINUATION_HIGH_RANGE=21` | phase passport |
| Проверить feature allowlist | done | `274` causal-признака, forbidden feature columns `[]`; targets не входят в `X` | guard V2 |
| Проверить good ids | done | `LA002, LA018, LA026, LA042, LA044, LA047, LA049, LA054, LA055, LA058, LA062` | user approval |
| Обучение ML | blocked | Не запускать на одном дне; сначала собрать пачку approved-дней этим же шаблоном и отдельный leakage guard | batch approval |

## STAS5 V5 Market Passport 2026-01-27 User Approved V3

Статус: `USER_APPROVED_V3_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать финальное решение по `GOOD_ALT` и `REVIEW_ONLY` | done | Бывшие `GOOD_ALT/REVIEW_ONLY` переведены в negative, потому что пользователь подтвердил: остальные входы хуже | user review |
| Создать approved V3 ledger | done | Использовать `DAY_MARKET_PASSPORT_LEDGER_20260127_USER_APPROVED_V3.csv` как source для этого дня | approved V3 |
| Проверить счетчики V3 | done | `GOOD_APPROVED=11`, `BAD_IN_GROUP=50`, `NO_TRADE_ZONE=14`, `TOTAL=75` | local assert |
| Упаковать день в отдельную V5 numeric-папку | done | Использовать `STAS5_ML_CORE/artifacts/v5/market_passports/20260127/` | V3 + FULL274 |
| Создать ML-ready таблицу `274F + labels` | done | `STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_LABELS_V1.csv`, `rows=75`, `feature_count=274` | package |
| Создать числовую структуру дня | done | `MARKET_STRUCTURE_NUMERIC_V1.csv` и context table; это teacher/source-of-truth для labels, а прямым live-feature станет только после causal-engine | package |
| Добавить день в общую январскую базу | current_next | Делать, когда будут готовы остальные январские паспорта | batch plan |
| Обучение ML | blocked | Не запускать на одном дне; запускать только после сборки общей approved базы и leakage guard | guardrail |

## STAS5 V5 Market Passport 2026-01-27 V2

Статус: `DRAFT_V2_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать, что работаем с январем `2026-01-27`, не апрелем | done | Не возвращаться к апрельской базе без отдельной команды пользователя | user correction |
| Принять `11` пользовательских GOOD-входов | done | GOOD список: `LA002`, `LA018`, `LA026`, `LA042`, `LA044`, `LA047`, `LA049`, `LA054`, `LA055`, `LA058`, `LA062` | user approval |
| Разобрать все остальные кандидаты дня | done | Покрытие `75/75`: `GOOD_APPROVED=11`, `GOOD_ALT=8`, `REVIEW_ONLY=7`, `BAD_IN_GROUP=35`, `NO_TRADE_ZONE=14` | FULL274 CSV + agent review |
| Сверить `GOOD_ALT` и `REVIEW_ONLY` глазами пользователя | current_next | Проверить `LA001`, `LA017`, `LA025`, `LA041`, `LA043`, `LA053`, `LA057`, `LA059`, а также `LA014`, `LA015`, `LA056`, `LA066`, `LA067`, `LA068`, `LA070` | V2 draft |
| Перевести день в approved numeric ledger | pending | Делать только после ручного подтверждения V2 | user approval |
| Обучение ML | blocked | Не запускать на этом дне, пока паспорт `2026-01-27` не станет approved | guardrail |

## STAS5 V5 Market Passport Trial 2026-01-27

Статус: `DRAFT_VISUAL_REVIEW_ONLY_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Найти и проверить run `full274_feature_collect_20260127_20260715_090857` | done | Использовать как source для пробного паспорта | user request |
| Создать overlay на оригинальном PNG | done | Открыть `STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_ANNOTATED_TOP.png` и сверить глазами | FULL274 PNG |
| Создать draft CSV зон | done | Сверить `19` строк: target/review/bad зоны | FULL274 CSV |
| Утвердить зоны пользователем | current_next | Пользователь правит/подтверждает target/no-buy/review зоны | visual review |
| Превратить draft в approved label ledger | pending | Делать только после ручного подтверждения | user approval |
| Обучение ML | blocked | Не запускать на trial-паспорте до approved label ledger | guardrail |

## STAS5 FULL274 Feature Collect 2026-07-15

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сделать отдельный wrapper для FULL274 one-day collect | done | Использовать `STAS5_ML_CORE/run_stas5_full274_feature_collect.ps1` | user request |
| Проверить wrapper на `2026-04-01` | done | Контрольный run `full274_feature_collect_20260401_20260715_084509`, `features=274` | local smoke |
| Не собирать 274 руками через отдельные команды | current_rule | Для новых дней запускать wrapper, чтобы STAS1/STAS2/V1/V2/FULL274/PNG были в одном run | wrapper |
| Обучение ML | blocked | Не запускать этой командой; это только предобучающий сбор и визуальная проверка | manual approval |

## Актуальный источник правды STAS5 V4

Текущий рабочий статус V4: ручной forward-review `2026-05-15..2026-05-25` проверен по пользовательским кругам, unified guard `PASS`.

```text
rows=738
BEST_GOOD=64
GOOD_ALT=42
BAD_IN_GROUP=433
NO_TRADE_GROUP=199
```

Старые todo-секции ниже являются историей промежуточных правок; для следующего действия смотреть верхний `2026-05-25` блок и актуальный guard.

## Todo 2026-07-14 STAS5 V4 2026-05-25 Screenshot Check

Статус: `STAS5_V4_20260525_USER_CHECKED_PASS_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить свежий скрин `2026-05-25` | done | Круги совпали с `LA020` и `LA038` | user screenshot |
| Проверить, нужна ли CSV-правка | done | CSV не менять: `LA020/LA038` уже `BEST_GOOD`, `LA019` остается `GOOD_ALT` | visual check |
| Создать checked day25 report | done | Использовать `STAS5_V4_GROUP_RANK_REVIEW_20260525_USER_CHECKED_V1_RU.md` | user check |
| Unified ledger, guard и risk audit | done | Не пересчитывались, потому что CSV не менялся; guard остается `PASS` после day23 | no CSV change |
| Ручная сверка `2026-05-15..25` | current_next | Финальный sanity-check перед group features только по отдельной команде пользователя | user review |
| V4 training/features/threshold/Optuna/API | blocked | Не запускать до финального ручного ledger и отдельного решения по group features | guardrails |

## Todo 2026-07-14 STAS5 V4 2026-05-24 Screenshot Check

Статус: `STAS5_V4_20260524_USER_CHECKED_PASS_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить свежий скрин `2026-05-24` | done | Круги совпали с `LA015` и `LA042`; поздняя нижняя зона совпала с `LA065` | user screenshot |
| Проверить, нужна ли CSV-правка | done | CSV не менять: `LA015/LA042/LA065` уже `BEST_GOOD`, `LA067` остается `GOOD_ALT` | visual check |
| Создать checked day24 report | done | Использовать `STAS5_V4_GROUP_RANK_REVIEW_20260524_USER_CHECKED_V1_RU.md` | user check |
| Unified ledger, guard и risk audit | done | Не пересчитывались, потому что CSV не менялся; guard остается `PASS` после day23 | no CSV change |
| Следующий день/зона | current_next | Продолжать точечно по пользовательским кругам, дальше `2026-05-25` | user review |
| V4 training/features/threshold/Optuna/API | blocked | Не запускать до финального ручного ledger и отдельного решения по group features | guardrails |

## Todo 2026-07-14 STAS5 V4 2026-05-23 Screenshot Check

Статус: `STAS5_V4_20260523_USER_CORRECTED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить свежий скрин `2026-05-23` | done | Красные круги справа подтверждают отдельные входы `LA034`, `LA036`, `LA042`, `LA051` | user screenshot |
| Исправить широкую группу `LA034..LA042` | done | Разбита на `004A`, `004B`, `004C`; `LA034` и `LA042` стали отдельными `BEST_GOOD` | visual check |
| Создать corrected day23 CSV | done | Использовать `STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V1.csv` | group correction |
| Обновить unified ledger, guard и risk audit | done | Guard `PASS`; unified totals `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199` | day23 correction |
| Следующий день/зона | current_next | Продолжать точечно по пользовательским кругам, дальше `2026-05-24/25` | user review |
| V4 training/features/threshold/Optuna/API | blocked | Не запускать до финального ручного ledger и отдельного решения по group features | guardrails |

## Todo 2026-07-14 STAS5 V4 2026-05-22 Screenshot Check

Статус: `STAS5_V4_20260522_USER_CORRECTED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить свежий скрин `2026-05-22` | done | Видимый конфликт найден в pre-London зоне: `LA024`, не `LA022`, является главным отмеченным входом | user screenshot |
| Исправить группу `05:36-09:01` | done | `LA022` переведен в `GOOD_ALT`, `LA024` повышен до `BEST_GOOD` | visual check |
| Создать corrected day22 CSV | done | Использовать `STAS5_V4_GROUP_RANK_LEDGER_20260522_USER_CORRECTED_V1.csv` | group correction |
| Обновить unified ledger, guard и risk audit | done | Guard `PASS`, totals без изменения: `BEST_GOOD=62`, `GOOD_ALT=43` | day22 correction |
| Следующий день/зона | current_next | Продолжать точечно по пользовательским кругам, дальше `2026-05-23/24/25` | user review |
| V4 training/features/threshold/Optuna/API | blocked | Не запускать до финального ручного ledger и отдельного решения по group features | guardrails |

## Todo 2026-07-14 STAS5 V4 2026-05-21 Screenshot Check

Статус: `STAS5_V4_20260521_USER_CORRECTED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить четыре красных круга `2026-05-21` | done | `LA006` совпал, `LA039/LA050/LA057` требовали micro-group повышения | user screenshot |
| Разбить sell-wave группу `LA022..LA050` | done | `LA039`, `LA045`, `LA050` теперь winners в отдельных micro-groups | visual check |
| Разбить pre-breakout группу `LA051..LA060` | done | `LA057` и `LA059` теперь отдельные winners | visual check |
| Создать corrected day21 CSV | done | Использовать `STAS5_V4_GROUP_RANK_LEDGER_20260521_USER_CORRECTED_V1.csv` | group correction |
| Обновить unified ledger, guard и risk audit | done | Guard `PASS`, totals `BEST_GOOD=62`, `GOOD_ALT=43` | day21 correction |
| Следующий день/зона | current_next | Продолжать точечно по пользовательским кругам/risk audit, особенно `2026-05-23/24` | user review |
| V4 training/features/threshold/Optuna/API | blocked | Не запускать до финального ручного ledger и group features | guardrails |

## Todo 2026-07-14 STAS5 V4 2026-05-20 Screenshot Check

Статус: `STAS5_V4_20260520_USER_CORRECTED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить два красных круга `2026-05-20` | done | Нижний круг = `LA037`, верхний круг = `LA038` | user screenshot |
| Разбить crash-low группу | done | `LA037` и `LA038` теперь winners в отдельных micro-groups | visual check |
| Создать corrected day20 CSV | done | Использовать `STAS5_V4_GROUP_RANK_LEDGER_20260520_USER_CORRECTED_V1.csv` | group correction |
| Обновить unified ledger, guard и risk audit | done | Guard `PASS`, totals `BEST_GOOD=59`, `BAD_IN_GROUP=436` | day20 correction |
| Следующий день/зона | current_next | Продолжать точечно по пользовательским кругам/risk audit, без массовой пересборки | user review |
| V4 training/features/threshold/Optuna/API | blocked | Не запускать до финального ручного ledger и group features | guardrails |

## Todo 2026-07-14 STAS5 V4 2026-05-19 Screenshot Check

Статус: `STAS5_V4_20260519_USER_CORRECTED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить красную обводку `2026-05-19` | done | Обведенная зона `0.86` соответствует `LA046`, а не `LA045` в CSV | user screenshot |
| Разбить широкую группу `LA034..LA047` | done | `LA042` и `LA046` теперь winners в отдельных micro-groups | visual check |
| Создать corrected day19 CSV | done | Использовать `STAS5_V4_GROUP_RANK_LEDGER_20260519_USER_CORRECTED_V1.csv` | group correction |
| Обновить unified ledger и guard | done | Guard `PASS`, totals `BEST_GOOD=58`, `GOOD_ALT=44` | day19 correction |
| V4 training/features/threshold/Optuna/API | blocked | Не запускать до финального ручного ledger и group features | guardrails |

## Todo 2026-07-14 STAS5 V4 2026-05-18 Screenshot Check

Статус: `STAS5_V4_20260518_USER_CORRECTED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить красные обводки `2026-05-18` | done | `LA036` и `LA066` оказались отдельными micro-group winners | user screenshot |
| Создать corrected day18 CSV | done | Использовать `STAS5_V4_GROUP_RANK_LEDGER_20260518_USER_CORRECTED_V1.csv` | visual check |
| Обновить unified ledger и guard | done | Guard `PASS`, totals `BEST_GOOD=57`, `GOOD_ALT=44` | day18 correction |
| Обновить risk audit | done | `GOOD_ALT_MAY_NEED_MICRO_GROUP=41`, `BEST_GOOD_FROM_OLD_NON_ENTER=23` | audit refresh |
| V4 training/features/threshold/Optuna/API | blocked | Не запускать до финального ручного ledger и group features | guardrails |

## Todo 2026-07-14 STAS5 V4 2026-05-17 Screenshot Check

Статус: `STAS5_V4_20260517_USER_CHECKED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить `2026-05-17` с пользовательским скрином | done | Расхождений нет: winners `LA004/LA006/LA036/LA046/LA063` | visual check |
| Создать проверочный отчет | done | Использовать `STAS5_V4_GROUP_RANK_REVIEW_20260517_USER_CHECKED_V1_RU.md` как отметку сверки | audit trail |
| Менять day17 CSV | not_needed | `STAS5_V4_GROUP_RANK_LEDGER_20260517_DRAFT.csv` уже совпадает со скрином | visual check |
| V4 training/features/threshold/Optuna/API | blocked | Не запускать до завершения ручной сверки и отдельного решения по group features | guardrails |

## Todo 2026-07-14 STAS5 V4 2026-05-16 Screenshot Check

Статус: `STAS5_V4_20260516_USER_CORRECTED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить `2026-05-16` с пользовательским скрином | done | Winners `LA016/LA027/LA038/LA041` | user screenshot |
| Убрать неподчеркнутый `LA049` из winners | done | Группа `LA043..LA049` стала `NO_TRADE_GROUP` | visual check |
| Пересчитать unified ledger и guard | done | Guard `PASS`, totals `BEST_GOOD=55` | day16 correction |
| Следующий день/зона | current_next | Проверять по скрину и risk audit, без массовой пересборки | user review |

## Todo 2026-07-14 STAS5 V4 Micro-Group Correction

Статус: `STAS5_V4_20260515_MICRO_GROUP_V2_FIXED_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Исправить `2026-05-15` под 6 человеческих целевых входов | done | Использовать `USER_CORRECTED_V2`, а не V1 | user screenshot correction |
| Разбить старую широкую группу `01:22-02:35` | done | `LA004` winner в `001A`, `LA007` winner в `001B` | micro-group rule |
| Обновить unified ledger `2026-05-15..25` | done | Guard `PASS`, totals `BEST_GOOD=56`, `GOOD_ALT=43` | day15 V2 |
| Проверить `2026-05-16..25` на похожую ошибку | current_next | После day21 продолжить по audit/скринам, особенно `2026-05-23/24`; `GOOD_ALT_MAY_NEED_MICRO_GROUP=40` | risk audit |
| Пересобирать все 10 дней целиком | blocked | Не делать без точечной ручной причины по audit | avoid churn |
| V4 train/group features/Optuna/API/TP/Stas3/exit | blocked | Только после финального ручного ledger и guard | V4 rails |

## Todo 2026-07-14 STAS5 Screenshot Artifact Inventory

Статус: `STAS5_V4_SCREENSHOT_ARTIFACT_INVENTORY_DONE_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Найти рабочие PNG `2026-05-01..2026-05-14` | done | Использовать контакт-лист train visual approval | artifact inventory |
| Найти рабочие forward PNG `2026-05-15..2026-05-25` | done | Использовать контакт-лист forward source | artifact inventory |
| Найти V4 group-block PNG `2026-05-15..2026-05-25` | done | Использовать контакт-лист V4 group blocks | artifact inventory |
| Проверить пропуски | done | `missing=[]` | index |
| Пролистать картинки глазами с пользователем | current_next | Открыть `STAS5_ML_CORE/artifacts/v4/review_navigation/20260714_artifact_inventory` и смотреть контакт-листы | user review |
| V4 group-block разбор `2026-05-01..2026-05-14` | pending | Делать отдельной задачей, если пользователь решит переводить train-base в group ledger | user decision |
| V4 train/group features | blocked | Не запускать в рамках инвентаризации скринов | V4 guard |

## Todo 2026-07-14 STAS5 V4 Unified Forward Review 2026-05-15..2026-05-25

Статус: `STAS5_V4_FORWARD_REVIEW_20260515_20260525_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Исправить календарь V4 | done | `2026-05-15` входит в `forward_review_11`, а не в отдельную карантинную/approved ветку | user correction |
| Единый ledger `2026-05-15..25` | done | `738` строк, `62` winners, все `label_status=DRAFT` | day ledgers |
| Supersede старый 15-only главный ledger | done | Сохранена копия `STAS5_V4_GROUP_RANK_LEDGER_20260515_ONLY_SUPERSEDED_20260714T124741Z.csv` | unified ledger |
| Group features | pending | Построить обязательные признаки группы: rank by price, distance to group low, before/after best low, duplicate basin | unified ledger |
| Visual group-check | pending | Показать по группам winner, bad рядом и reason-code на графике | group features |
| Адаптивный дневной счетчик | done | `2..5` не hard cap; число входов зависит от режима дня, но каждый вход должен иметь group edge/reason | user correction |
| V4 group ranker train | blocked | Только после final approval, group features и guard PASS | no training yet |
| Threshold/Optuna/API/TP/Stas3/exit | blocked | Не запускать в текущем шаге | rails |

## Todo 2026-07-14 STAS5 V4 2026-05-15 Quarantine Removed

Статус: `STAS5_V4_20260515_APPROVED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Снять карантин с `2026-05-15` | done | Approved V1 создан из user-corrected V1 | user approval |
| Approved CSV `2026-05-15` | done | `41` строка, winners `LA007/LA021/LA024/LA054/LA061` | guard pass |
| Общий approved ledger | done | `STAS5_V4_GROUP_RANK_LEDGER.csv` содержит approved `2026-05-15` | approved day |
| Draft days `2026-05-16..25` | pending | Переводить в approved только по отдельному подтверждению | user approval |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-25 Draft Group Review

Статус: `STAS5_V4_20260525_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-25` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260525_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-25` | done | `68` строк, winners `LA014/LA020/LA038/LA059/LA066`; не использовать как train до approval | group review |
| Approved ledger `2026-05-25` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-25`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-24 Draft Group Review

Статус: `STAS5_V4_20260524_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-24` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260524_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-24` | done | `70` строк, winners `LA009/LA015/LA024/LA042/LA065`; не использовать как train до approval | group review |
| Approved ledger `2026-05-24` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-24`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-23 Draft Group Review

Статус: `STAS5_V4_20260523_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-23` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260523_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-23` | done | `63` строки, winners `LA007/LA022/LA033/LA036/LA051`; не использовать как train до approval | group review |
| Approved ledger `2026-05-23` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-23`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-22 Draft Group Review

Статус: `STAS5_V4_20260522_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-22` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260522_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-22` | done | `75` строк, winners `LA007/LA022/LA036/LA047/LA061`; не использовать как train до approval | group review |
| Approved ledger `2026-05-22` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-22`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-21 Draft Group Review

Статус: `STAS5_V4_20260521_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-21` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260521_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-21` | done | `81` строка, winners `LA006/LA019/LA045/LA059/LA066`; не использовать как train до approval | group review |
| Approved ledger `2026-05-21` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-21`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-20 Draft Group Review

Статус: `STAS5_V4_20260520_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-20` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260520_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-20` | done | `68` строк, winners `LA011/LA037/LA045/LA053/LA057`; не использовать как train до approval | group review |
| Approved ledger `2026-05-20` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-20`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-19 Draft Group Review

Статус: `STAS5_V4_20260519_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-19` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260519_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-19` | done | `65` строк, winners `LA005/LA016/LA032/LA042/LA063`; не использовать как train до approval | group review |
| Approved ledger `2026-05-19` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-19`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-18 Draft Group Review

Статус: `SUPERSEDED_BY_20260518_USER_CORRECTED_V1_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-18` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260518_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-18` | superseded | Использовать `USER_CORRECTED_V1`: winners `LA006/LA019/LA034/LA036/LA049/LA061/LA066` | user correction |
| Approved ledger `2026-05-18` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-18`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-17 Draft Group Review

Статус: `STAS5_V4_20260517_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-17` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260517_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-17` | done | `63` строки, winners `LA004/LA006/LA036/LA046/LA063`; не использовать как train до approval | group review |
| Approved ledger `2026-05-17` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-17`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 Review Encoding Fix

Статус: `STAS5_V4_REVIEW_ENCODING_FIX_DONE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить V4 review Markdown на кракозябры | done | Скан показал `problems=0` по трем `.md` в `group_rank_review` | user report |
| Убрать ложный `U+FFFD` из `docs/codex/commands.md` | done | Литеральный символ заменен на regex escape `\x{FFFD}` | commands hygiene |
| Менять CSV/PNG/обучение | blocked | Не делать в рамках encoding fix | V4 approval rails |

## Todo 2026-07-14 STAS5 V4 2026-05-16 Draft Group Review

Статус: `STAS5_V4_20260516_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft group review `2026-05-16` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260516_DRAFT_RU.md` и annotated PNG глазами | user screenshot |
| Draft CSV `2026-05-16` | superseded | Использовать `USER_CORRECTED_V1`: winners `LA016/LA027/LA038/LA041`, `LA049` не winner | user correction |
| Approved ledger `2026-05-16` | pending | После подтверждения перенести в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| Group feature builder | pending | Считать group-rank признаки для `2026-05-16`: rank by price, distance to group low, before/after best low | approved/draft decision |
| V4 train | blocked | Только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 2026-05-15 User-Corrected V1

Статус: `STAS5_V4_20260515_USER_CORRECTED_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| User-corrected group review `2026-05-15` | done | Использовать `STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_RU.md` как актуальный ручной разбор по скрину | user correction |
| User-corrected draft CSV `2026-05-15` | done | Проверен CSV на `41` строку: `BEST_GOOD=5`, `GOOD_ALT=4`, `BAD_IN_GROUP=26`, `NO_TRADE_GROUP=6`; не использовать как train до approval | group review |
| Предыдущий `SCREENSHOT_DRAFT` | superseded | Оставить как архив черновика; не считать актуальным разбором 15 мая | user correction |
| Approved ledger `2026-05-15` | pending | После финального подтверждения перенести `USER_CORRECTED_V1` в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` | user approval |
| V4 train | blocked | Запускать только после approved ledger, group features и guard PASS | V4 guard |

## Todo 2026-07-14 STAS5 V4 Human-Style Group Ranker

Статус: `STAS5_V4_20260515_SCREENSHOT_GROUP_REVIEW_DRAFT_NO_TRAINING`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| V4 ТЗ и папка | done | Использовать `STAS5_ML_CORE/07_STAS5_V4_HUMAN_STYLE_GROUP_RANKER_TZ_RU.md` | user decision |
| Схема `STAS5_V4_GROUP_RANK_LEDGER` | done | Использовать `STAS5_ML_CORE/schemas/STAS5_V4_GROUP_RANK_LEDGER.schema.json` как контракт будущего CSV | V4 TZ |
| Карантинный день `2026-05-15` | in_progress | Первый screenshot draft создан; нужен user review/правки перед approved ledger | manual group review |
| Screenshot group-review `2026-05-15` | done | Проверить `STAS5_V4_GROUP_RANK_REVIEW_20260515_DRAFT_RU.md` и annotated PNG | user screenshot |
| Partial draft CSV `2026-05-15` | done | `41` строк, winners `LA004/LA007/LA021/LA054/LA061`; не использовать как train до approval | screenshot review |
| Перевод `2026-05-16..2026-05-20` | pending | Перенести текущие GOOD/BAD в `group_id + rank_label + reason_code + winner` | V3 review labels |
| Разметка `2026-05-21..2026-05-25` | pending | После visual review перевести blind-forward V3 в group ledger | user visual review |
| Base 24-day dataset | pending | Собирать только после group ledger coverage; без `2026-05-15` | approved group ledger |
| Base 25-day dataset | blocked | Только после approved ledger для `2026-05-15` | quarantine approval |
| Group features | pending | Построить обязательные признаки группы: rank by price, distance to group low, before/after best low, duplicate basin | group ledger |
| Visual group review graph | pending | Показать группу, winner, bad рядом и reason-code | group features |
| V4 group ranker train | blocked | Только после guard PASS; не построчный KEEP/CUT | ledger + features + guard |
| TP/Stas3/API/Optuna/threshold tuning | blocked | Не запускать в текущем V4 TZ шаге | rails |

## Todo 2026-07-14 STAS5 V3 Review Train Forward 21-25

Статус: `STAS5_V3_REVIEW_TRAIN_FORWARD_21_25_READY_WAIT_USER_VISUAL_REVIEW`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| V3 user-review ledger `2026-05-16..2026-05-20` | done | Использовать `STAS5_V3_USER_REVIEW_LEDGER_20260516_20260520.csv` | user screenshots |
| V3 train dataset `1-14 + 16-20` | done | Dataset `1106` rows, `274` features | ledger |
| V3 leakage guard | done | Guard `PASS` | dataset |
| V3 train `full_v2_all_274` | done | Wrapper-run `stas5_v3_wrapper_smoke2_20260714` | guard |
| V3 blind-forward `2026-05-21..2026-05-25` | done | Смотреть PNG в `artifacts/v3/forward/runs/stas5_v3_wrapper_smoke2_20260714` | model |
| User visual review новых PNG | current_next | Пользователь отмечает хорошие/плохие входы на `21..25` | forward PNG |
| Следующий контур/улучшение | pending | После visual review: добавить новые user labels или править candidate detector/gate | user review |
| TP/Stas3/API/Optuna/threshold tuning | blocked | Не запускать в этом entry-only контуре | rails |

## Todo 2026-07-13 STAS5 V2 Full274 Run Check

Статус: `STAS5_V2_FULL274_RUN_CHECK_PASS_TECHNICAL_REVIEW_REQUIRED`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить последний full274 run | done | Использовать отчет `STAS5_V2_FULL274_RUN_CHECK_20260713_203703_RU.md` | full274 run |
| Проверить model/forward pointers и manifests | done | `run_id` совпал, `feature_count=274` | latest pointers |
| Проверить forward PNG/CSV | done | `6/6` PNG READY, row parity PASS | forward artifacts |
| Визуально сравнить входы full274 | current_next | Открыть PNG `20260515..20260520`, особенно 15-17 мая | user review |
| Решить, заменять ли baseline | pending | Не заменять без визуального review, так как AUC full274 ниже baseline | user review |

## Todo 2026-07-13 STAS5 V2 Full 274 Wrapper

Статус: `STAS5_V2_FULL_274_WRAPPER_READY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить одну команду для full `274` train + forward | done | Запустить `STAS5_ML_CORE/run_stas5_v2_full_274_train_forward.ps1` | graph-to-feature audit |
| Проверить wrapper без тяжелого прогона | done | PowerShell syntax PASS, py_compile PASS | local checks |
| Выполнить full 274 прогон | current_next | Пользователь запускает команду и смотрит forward папку | wrapper |
| Сравнить full 274 с baseline `v1_plus_risk_gate` | pending | После появления PNG/CSV full 274 | full run |

## Todo 2026-07-13 STAS5 V2 Graph To Feature Audit

Статус: `STAS5_V2_GRAPH_TO_FEATURE_AUDIT_READY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сверить график `2026-05-04` с full feature snapshot | done | Использовать отчет `STAS5_V2_GRAPH_TO_FEATURE_AUDIT_20260504_RU.md` | train visual batch + V2 snapshot |
| Сверить full snapshot с latest model feature set | done | Учитывать, что latest model `v1_plus_risk_gate` взяла `126/274` признаков | model manifest |
| Решить следующий model-set | current_next | Выбрать отдельный прогон `graph_context_v2` или `full_v2_all_274` для сравнения с baseline | user decision |
| TP/Stas3/API/Optuna/threshold tuning | blocked | Не запускать в рамках этого аудита | rails |

## Todo 2026-07-13 STAS5 V2 Train Visual Batch

Статус: `STAS5_V2_TRAIN_VISUAL_BATCH_READY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сгенерировать train-графики `2026-05-01..2026-05-14` | done | Смотреть `visual_approval/runs/stas5_v2_train_visual_20260713_14d` | V2 snapshot |
| Проверить соответствие train CSV и PNG | done | Manifest rows `972`, KEEP `115`, CUT `857` | batch render |
| Пользовательский визуальный review train | current_next | Проверить, что ручные входы и слои на графиках совпадают с ожиданием | train PNG |

## Todo 2026-07-13 STAS5 V2 Run Isolation

Статус: `STAS5_V2_RUN_ISOLATION_READY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Не перезаписывать forward folders при повторном запуске | done | Использовать `$runId` и `runs/<run_id>` | user feedback |
| Добавить latest pointers | done | Читать `STAS5_V2_LATEST_MODEL_RUN.json` и `STAS5_V2_LATEST_FORWARD_RUN.json` | run isolation |
| Проверить новый isolated run | done | `stas5_v2_run_20260713_190743` создан | CLI |
| Пользовательский visual review | current_next | Открывать PNG внутри `forward/runs/<run_id>/20260515..20260520` | isolated forward |

## Todo 2026-07-13 STAS5 V2 Controlled Forward

Статус: `STAS5_V2_CONTROLLED_FORWARD_READY_WAIT_USER_REVIEW`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| V2 ablation baseline | done | Использовать `STAS5_V2_ABLATION_BASELINE_20260501_20260514_RU.md` | numeric coverage |
| V2 controlled model | done | Selected feature set `v1_plus_risk_gate` | ablation |
| V2 blind-forward `2026-05-15..2026-05-20` | done | Смотреть PNG/CSV в `artifacts/v2/forward/` | controlled model |
| Пользовательский visual review forward PNG | current_next | Отметить реальные/шумные `ENTER/UNSURE`, особенно 15-17 мая | forward PNG |
| Следующее улучшение модели | pending | Делать после user review; не подбирать threshold по forward автоматически | user review |
| TP/Stas3/API/Optuna/scorer/target-lock | blocked | Только отдельным решением | rails |

## Todo 2026-07-13 STAS5 V2 Numeric Coverage

Статус: `STAS5_V2_NUMERIC_COVERAGE_READY_WAIT_USER`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить, что важные слои approval-графика передаются в ML как числа | done | Использовать coverage audit за `2026-05-04` | visual approval + agents |
| Добавить STAS4 block numeric features | done | Использовать `stas4_v2_block_*` как context, не hard-filter | V2 combo exporter |
| Добавить pattern numeric features | done | Использовать `stas4_v2_pattern_*` | STAS4 pattern logic |
| Добавить SHORT/WAVE causal context | done | Использовать `stas5_v2_short_wave_*` | OHLCV до входа |
| Leakage/tests после расширения feature matrix | done | Guard `PASS`, STAS5 tests `30 passed` | rebuilt snapshot |
| V2 ablation baseline | current_next | Запускать только после подтверждения пользователя, что numeric coverage понятен и принят | user approval |
| V2 controlled model/training | blocked | Только после ablation baseline и отдельного решения | rails |
| Optuna/scorer/target-lock/API/Stas3 TP | blocked | Не запускать в STAS5 entry numeric coverage | rails |

## Todo 2026-07-13 STAS5 V2 Strategy Audit Strip

Статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_WITH_STRATEGY_AUDIT_READY_WAIT_USER`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить 4 STAS4 strategy audit layers на approval PNG `2026-05-04` | done | Пользователь открывает обновленный PNG и проверяет глазами | V2 visual approval |
| Зафиксировать, что стратегии audit-only | done | Не превращать `X` в hard-cut и не брать `UP` как финальный вход | guardrails |
| V2 ablation baseline | blocked | Запускать только после визуального `норм` от пользователя | user approval |
| V2 controlled model/training | blocked | Только после approval + ablation | rails |
| Optuna/scorer/target-lock/API/Stas3 TP | blocked | Не запускать в STAS5 visual approval | rails |

## Todo 2026-07-13 STAS5 V2 Feature Visual Approval

Статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_READY_WAIT_USER`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| V2 feature visual approval graph за `2026-05-04` | done | Открыть `STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png` | V2 snapshot + STAS2/STAS4 renderers |
| Пользователь проверяет признаки глазами | current_next | Подтвердить, что график похож на нужный STAS4 overlay и признаки стоят правильно, либо назвать правки | visual graph |
| V2 ablation baseline | blocked | Не запускать до визуального подтверждения | user approval |
| V2 controlled model/training | blocked | Только после approval + ablation | rails |
| Optuna/scorer/target-lock/API/Stas3 TP | blocked | Не запускать в STAS5 entry visual approval | rails |

## Todo 2026-07-13 STAS5 V2 Main TZ After Pre-ML Audit

Статус: `STAS5_V2_PRE_ML_AUDIT_READY_CURRENT_NEXT_ABLATION_BASELINE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| V2 combo feature exporter | done | Использовать `stas5_v2_combo_features_20260501_20260514_v0.csv` | STAS4 combo |
| V2 feature snapshot builder | done | Использовать `stas5_v2_feature_snapshot_20260501_20260514_v0.csv` | v1 snapshot + V2 combo |
| V2 leakage guard | done | Использовать `stas5_v2_leakage_guard_20260501_20260514_v0.json` | V2 snapshot |
| Forward error ledger | done | Использовать `stas5_forward_error_ledger_20260515_20260520_v0.csv` строго audit-only | V2 guard |
| V2 pre-ML audit | done | Использовать `STAS5_V2_PRE_ML_AUDIT_20260501_20260520_RU.md` | V2 guard + error ledger |
| V2 ablation baseline | current_next | Сравнить feature groups без production training и без threshold tuning по forward `15+` | pre-ML audit |
| V2 controlled model | blocked | Только после ablation baseline и отдельного решения | rails |
| Optuna/scorer/target-lock/API/Stas3 TP | blocked | Не запускать в STAS5 entry research без отдельного решения | rails |

## Todo 2026-07-13 STAS5 V2 Forward User Review

Статус: `STAS5_V2_FORWARD_USER_REVIEW_READY_WAIT_USER_SELECTION`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сделать крупный review-график `2026-05-15` | done | Открыть страницы из `STAS5_ML_CORE/artifacts/v2/user_review/20260515/` | V2 combo features |
| Создать CSV-шаблон ручной forward-разметки | done | Использовать `STAS5_V2_USER_REVIEW_TEMPLATE_20260515.csv` | review renderer |
| Пользователь выбирает реальные входы | current_next | Назвать точные `LAxxx` из PNG; ожидается около 3 входов | visual review |
| Заполнить forward audit labels | pending | `USER_KEEP_FORWARD_AUDIT` для выбранных, `NOISE_FORWARD_AUDIT` для остальных | user selection |
| Сравнить признаки `USER_KEEP` против `NOISE` | pending | Найти правила/признаки, отделяющие 3 от 87 | labeled forward audit |
| V2 model/training/threshold | blocked | Не запускать до train snapshot + guard + audit | rails |

## Todo 2026-07-13 STAS5 V2 After Combo Exporter

Статус: `STAS5_V2_COMBO_FEATURE_EXPORT_READY_CURRENT_NEXT_V2_SNAPSHOT`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать `stas5_v2_combo_feature_exporter.py` | done | Использовать готовый exporter | STAS4 combo code |
| Экспортировать V2 combo train features `2026-05-01..2026-05-14` | done | Использовать `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.csv` | exporter |
| Экспортировать V2 combo forward features `2026-05-15..2026-05-20` | done | Использовать `STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.csv` только для blind audit | exporter |
| V2 feature snapshot builder | current_next | Создать `stas5_v2_feature_snapshot_builder.py`: join ledger/Stas2/v2 combo по `day,candidate_id,record_id`, без потери `KEEP + yellow_x` | combo features |
| V2 leakage guard | pending | Проверить no future/postfact/yellow/strategy/Stas3/TP/exit, `feature_time_utc < entry_time_utc` | V2 snapshot |
| V2 pre-ML audit | pending | Сравнить KEEP/CUT по combo/density/structure/risk/gate признакам до обучения | V2 guard |
| Forward error ledger | pending | Разметить bad green / missed good на `2026-05-15..2026-05-20` как audit-only | v1 forward + V2 features |
| V2 controlled model / ablation | blocked | Только после snapshot + guard + audit | audit |
| Optuna/scorer/target-lock/API/Stas3 TP | blocked | Не запускать в STAS5 entry research без отдельного решения | rails |

## Todo 2026-07-13 STAS5 V2 Contour 2

Статус: `STAS5_V2_CONTOUR2_TZ_READY_PENDING_IMPLEMENTATION`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Провести hard audit STAS5 v1 | done | Использовать `STAS5_ML_CORE/04_STAS5_V1_HARD_AUDIT_RU.md` | v1 artifacts + agents |
| Составить ТЗ STAS5 V2 / контур 2 | done | Использовать `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md` | hard audit |
| Подключить combo-spectrum к ML как causal features | current_next | Создать `stas5_v2_combo_feature_exporter.py`, не брать PNG/JSON как готовую feature matrix | STAS4 code |
| Добавить phase/permission gate | pending | Считать `LONG_ALLOWED/NO_TRADE/short_pressure` до входа | combo exporter |
| Добавить risk/noise features | pending | `knife_risk_pre_entry`, `weak_bounce_inside_drop`, `too_high_in_drop`, `asia_weekend_risk` | feature exporter |
| Сделать forward error ledger | pending | Разметить `GREEN_BAD`, `YELLOW_GOOD`, `SKIP_MISSED_GOOD` по `2026-05-15..2026-05-20` | v1 forward CSV |
| Собрать V2 leakage guard | pending | Проверить `feature_available_at <= entry_time`, no future/postfact/Stas3/TP | V2 snapshot |
| V2 ablation/calibration/permutation audit | pending | Сравнить V1, combo-only, risk-only, full V2 | V2 model |
| Optuna/scorer/target-lock/API/Stas3 TP | blocked | Не запускать в V2 entry research без отдельного решения | rails |

## Todo 2026-07-10 STAS5 Entry ML Pipeline Ready

Статус: `STAS5_ENTRY_ML_PIPELINE_READY_TRAIN_1_14_FORWARD_15_20_NO_OPTUNA_NO_API_NO_STAS3`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать ML-ledger по `972` входам | done | Использовать `STAS5_ML_CORE/artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.csv` | manual labels + Stas2 records |
| Собрать pre-entry feature snapshot | done | Использовать `STAS5_ML_CORE/artifacts/features/stas5_feature_snapshot_20260501_20260514_v0.csv` | ledger |
| Сделать leakage guard | done | Guard `PASS`, feature columns `111`, forbidden columns `0` | feature snapshot |
| Сделать pre-ML audit | done | Audit `READY_FOR_CONTROLLED_BASELINE` | guard |
| Controlled baseline ML без yellow-полей | done | Модель `STAS5_ML_CORE/artifacts/model/stas5_entry_ranker_20260501_20260514_v0.joblib` | clean dataset |
| Forward entry review `2026-05-15..2026-05-20` | done | Смотреть PNG/CSV в `STAS5_ML_CORE/artifacts/forward/` | controlled baseline |
| Визуальный review forward PNG | current_next | Открыть дни `20260515..20260520`, проверить глазами `ENTER/UNSURE/SKIP` и выписать шум/попадания | user visual review |
| Улучшение модели/ablation | pending | Только после визуального review; forward threshold не подбирать по `15+` | forward review |
| Optuna/scorer/target-lock/API/мост Bybit/Stas3 TP | blocked | Не запускать в STAS-5 entry ML без отдельного решения | rails |

## Todo 2026-07-10 STAS5 Memory Refresh

Статус: `STAS5_TZ_TRAIN_1_14_FORWARD_15_PLUS_NO_TP_NO_API`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Обновить рабочую память STAS-5 | done | Читать `STAS5_ML_CORE/README_RU.md` и верхние блоки `docs/codex/*` | user request |
| Создать сухое рабочее ТЗ STAS-5 | done | Использовать `STAS5_ML_CORE/03_STAS5_CURRENT_EXECUTION_INSTRUCTION_RU.md`: train `1-14`, forward `15+`, PNG с ML-входами | user request |
| Собрать ML-ledger по `972` входам | current_next | Создать `src/mlbotnav/stas5_ml_ledger_builder.py` и артефакты `STAS5_ML_CORE/artifacts/ledger/*` | manual labels + Stas2 records |
| Собрать pre-entry feature snapshot | pending | Брать только признаки, известные до входа; Stas2/Stas4 использовать как context/features | ML-ledger |
| Сделать leakage guard и pre-ML audit | pending | Проверить no future fields, no Stas3, no yellow hard-cut | feature snapshot |
| Controlled baseline ML без yellow-полей | blocked | Только после audit и leakage guard | clean dataset |
| Forward entry review `2026-05-15+` | blocked | CSV/PNG: каждая кандидатная точка имеет ML `ENTER/UNSURE/SKIP`; forward не использовать для threshold tuning | controlled baseline |
| ML/export/training/scorer/target-lock/Optuna/API/мост Bybit | blocked | Не запускать в этом этапе | rails |

## Todo 2026-07-10 STAS4 Root Home

Статус: `STAS4_ROOT_HOME_READY_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Вынести STAS4 в корень проекта | done | Использовать `STAS4_FEATURE_HYPOTHESIS_REVIEW` как рабочую папку STAS4 | user request |
| Обновить default out-dir генератора STAS4 | done | Новые STAS4-прогоны писать в `STAS4_FEATURE_HYPOTHESIS_REVIEW` | source update |
| Обновить ссылки в документах/отчетах | done | Старый путь не использовать как источник правды | path rewrite |
| Удалить старые пустые директории из `reports/final_review/stas4_feature_hypothesis_screen_v0` | blocked | Не трогать процессы; можно удалить позже вручную после закрытия просмотрщика/проводника | Windows lock |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать в этом этапе | rails |

## Todo 2026-07-10 STAS5 ML Entry Architecture

Статус: `STAS5_ML_ENTRY_ARCHITECTURE_DRAFT_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать source-of-truth `STAS5_ML_CORE` | done | Использовать как главный документ STAS-5 по ML-входам | user STAS-5 spec |
| Зафиксировать `human KEEP > strategy vote` | done | Yellow X хранить только как `AUDIT_ONLY`; конфликт сохранять как `yellow_x_conflict=1` | manual labels |
| Собрать ML-ledger по `972` входам | pending | Объединить day/candidate/entry/human_label/yellow flags без потери строк | 14d draft labels |
| Собрать pre-entry feature snapshot | pending | Только признаки, доступные до входа; Stas2/Stas4 как context/features | ML-ledger |
| Сделать audit признаков без ML | pending | Сравнить признаки `KEEP_DRAFT` против `CUT_DRAFT`, отдельно yellow-X conflicts | feature snapshot |
| Первый controlled baseline без yellow-полей | blocked | Только после audit и утверждения label/feature contract | approved ledger |
| Stas3 TP/exit | blocked | Не включать в STAS-5 входы; отдельный будущий контур | STAS5 entry ML |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать в этом этапе | rails |

## Todo 2026-07-10 Yellow X Audit Only Rule

Статус: `YELLOW_X_AUDIT_ONLY_FIXED_RULE_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать `yellow X` как `AUDIT_ONLY` | done | Использовать `YELLOW_X_AUDIT_ONLY_RULE_RU.md` как правило для будущих dataset/export/training | user decision |
| Запретить hard-cut по `yellow_x = 1` | done | Любой будущий export/training должен падать, если удален `KEEP_APPROVED + yellow_x = 1` | ML guardrails |
| Первую ML-модель строить без yellow-полей в feature matrix | current_next | Feature allowlist должен исключать `stas4_*yellow*`, `would_cut*`, `strategy_vote*` до отдельного ablation | approved labels |
| Проверить yellow X как passive feature | blocked | Только позже, через ablation и без hard veto | baseline model |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать в этом этапе | rails |

## Todo 2026-07-10 STAS4 Manual Labels Draft 20260514 Complete

Статус: `STAS4_MANUAL_LABELS_14D_DRAFT_COMPLETE_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разметить `2026-05-14` | done | Использовать `11` KEEP: `LA014`, `LA015`, `LA032`, `LA039`, `LA046`, `LA047`, `LA048`, `LA049`, `LA053`, `LA055`, `LA056` | user screenshot |
| Закрыть 14-дневную пачку `2026-05-01..2026-05-14` | done | Сверять итоговый ledger: `972` total, `115` KEEP_DRAFT, `857` CUT_DRAFT | manual labels |
| Подготовить следующий этап анализа признаков | current_next | Разбирать, какие Stas4/индикаторные признаки объясняют пользовательский KEEP, без превращения `CUT_DRAFT` в автоматический фильтр | approved discussion |
| Превращать draft-разметку в финальный ML-label | blocked | Делать только после отдельного утверждения схемы label/feature leakage guard | approved ledger |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать | rails |

## Todo 2026-07-10 STAS4 Manual Labels Draft 20260513

Статус: `STAS4_MANUAL_LABELS_IN_PROGRESS_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разметить `2026-05-13` | done | Использовать `4` KEEP: `LA002`, `LA043`, `LA058`, `LA072` | user screenshot |
| Продолжить 14-дневную пачку | current_next | Ждать следующий скрин пользователя за `2026-05-14` и сопоставить красные подчеркивания с LA-входами | user visual review |
| Превращать draft-разметку в финальный ML-label | blocked | Делать только после отдельного утверждения схемы label/feature leakage guard | approved ledger |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать | rails |

## Todo 2026-07-10 STAS4 Manual Labels Draft 20260512

Статус: `STAS4_MANUAL_LABELS_IN_PROGRESS_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разметить `2026-05-12` | done | Использовать `6` KEEP: `LA006`, `LA012`, `LA036`, `LA038`, `LA051`, `LA055` | user screenshot |
| Продолжить 14-дневную пачку | current_next | Ждать следующий скрин пользователя за `2026-05-13` и сопоставить красные подчеркивания с LA-входами | user visual review |
| Превращать draft-разметку в финальный ML-label | blocked | Делать только после отдельного утверждения схемы label/feature leakage guard | approved ledger |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать | rails |

## Todo 2026-07-10 STAS4 Manual Labels Draft

Статус: `STAS4_MANUAL_LABELS_IN_PROGRESS_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разметить `2026-05-01` красными подчеркиваниями пользователя | done | Использовать `KEEP_20260501_FROM_RED_UNDERLINES_DRAFT.csv` как draft | user screenshot |
| Разметить `2026-05-02` | done | Использовать `KEEP_20260502_FROM_RED_UNDERLINES_DRAFT.csv` как draft | user screenshot |
| Разметить `2026-05-03` | done | Пользователь уточнил, что входов `6`; использовать исправленную версию | user correction |
| Разметить `2026-05-04` | done | Использовать `9` KEEP: `LA002`, `LA004`, `LA020`, `LA032`, `LA038`, `LA042`, `LA045`, `LA049`, `LA065` | user screenshot |
| Разметить `2026-05-05` | done | Использовать `8` KEEP: `LA001`, `LA005`, `LA013`, `LA026`, `LA028`, `LA036`, `LA041`, `LA044` | user screenshot |
| Разметить `2026-05-06` | done | Использовать `7` KEEP: `LA001`, `LA008`, `LA016`, `LA021`, `LA039`, `LA052`, `LA061` | user screenshot |
| Разметить `2026-05-07` | done | Использовать `11` KEEP: `LA014`, `LA017`, `LA019`, `LA023`, `LA024`, `LA036`, `LA050`, `LA053`, `LA060`, `LA073`, `LA075` | user screenshot |
| Разметить `2026-05-08` | done | Использовать `8` KEEP: `LA009`, `LA010`, `LA021`, `LA041`, `LA045`, `LA048`, `LA060`, `LA069` | user screenshot |
| Разметить `2026-05-09` | done | Использовать `7` KEEP: `LA001`, `LA002`, `LA013`, `LA018`, `LA028`, `LA043`, `LA047` | user screenshot |
| Разметить `2026-05-10` | done | Использовать `10` KEEP: `LA006`, `LA030`, `LA035`, `LA041`, `LA045`, `LA046`, `LA051`, `LA056`, `LA057`, `LA059` | user screenshot |
| Разметить `2026-05-11` | done | Использовать `10` KEEP: `LA014`, `LA016`, `LA029`, `LA041`, `LA045`, `LA046`, `LA048`, `LA052`, `LA053`, `LA060` | user screenshot |
| Продолжить 14-дневную пачку | current_next | Ждать следующий скрин пользователя за `2026-05-12` и сопоставить красные подчеркивания с LA-входами | user visual review |
| Превращать draft-разметку в финальный ML-label | blocked | Делать только после отдельного утверждения схемы label/feature leakage guard | approved ledger |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать | rails |

## Todo 2026-07-10 STAS2/STAS4 Compact Strips

Статус: `STAS2_STAS4_COMPACT_STRIPS_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сжать визуальные полосы `ФОН/LONG/SHORT/WAVE` примерно в 2 раза | done | Пользователю открыть smoke PNG и глазами подтвердить читаемость | Stas2/Stas4 visual |
| Показать нижнюю ось времени от `00:00` до `00:00` | done | Проверить на разных днях, что правый `00:00` не обрезан | day overview |
| Изменить расчет фаз/волн/entry | blocked | Не делать в этой задаче | no logic change |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного прямого approval | rails |

## Todo 2026-07-09 STAS3 V2 Clean

Статус: `STAS3_V2_CLEAN_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Пометить old-base V2 как невалидный | done | Не использовать `stas3_v2_20260510_20260512_long_only_20260709_112925` как принятый V2 | user correction |
| Создать clean-модуль без старого Stas3 | done | Использовать `src/mlbotnav/visual_entry_stas3_v2_clean_review.py` | clean reset |
| Сделать отдельный runner/open для clean V2 | done | `run_clean_v2.ps1`, `open_clean_v2_last_run.ps1` | clean module |
| Прогнать clean V2 за `2026-05-10..2026-05-12` | done | Финальный run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_clean_20260510_20260512_long_only_20260709_123622` | Stas2 source |
| Проверить таблицы/Excel/PNG | done | Acceptance PASS: `214` rows, `0` skipped, `66` PNG, пустых PNG нет | clean run |
| Визуальная сверка пользователем | current_next | Открыть browse/entries/medium и проверить, что TP читается глазами и не похож на старый Stas3 | final clean run |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать | rails |

## Todo 2026-07-09 STAS3 V2 Reset TZ

Статус: `OLD_BASE_V2_INVALID_REPLACED_BY_CLEAN_V2`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Заморозить Stas3 V1 как архив | done | Не удалять runs, не использовать V1 как source-of-truth | user reset |
| Создать новое ТЗ Stas3 V2 | done | Читать `STAS3_PERCENT_LADDER_REVIEW/TZ_STAS3_V2_RESET_RU.md`; учтены LONG-only, входы из `STAS2_RECORDS.csv`, `entry_price_for_calc = entry_price_5bps`, быстрые TP `0.3-0.9%`, средние ходы `1.0-2.0%` шаг `0.1%`, далее `2.0-20.0%` шаг `0.2%`, рабочие дни `2026-05-10..2026-05-12`, context bundle session/bg/LONG/SHORT-risk/WAVE/volatility/volume; short-входы и short-TP запрещены | reset + user grid/source/context correction |
| Реализовать Stas3 V2 | done | Финальный run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925` | user start |
| Перепроектировать таблицы Stas3 V2 | done | Смотреть `STAS3_V2_ENTRY_TP_AUDIT.csv`, `STAS3_V2_CONTEXT_BUNDLE.csv`, `STAS3_V2_TP_LADDER_BY_PHASE.csv`, `STAS3_V2_WRONG_TP_REVIEW.csv` | V2 implementation |
| Убрать MFE MAX из основного визуала TP | done | В основном визуале MFE только diagnostic point; отдельные big-move pages также diagnostic/hindsight | V2 implementation |
| Решить WAVE-context join | done | `WAVE/GAP/continuous` протянуты с `wave_context_scope=HINDSIGHT_WAVE_REVIEW`, не causal feature | V2 implementation |
| Визуальная сверка пользователем | current_next | Открыть browse/xlsx/tp и проверить, читаются ли entry price и review TP | final run |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать | rails |

## Todo 2026-07-09 STAS3 Rebuild From Latest STAS2

Статус: `STAS3_REBUILD_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Пересобрать Stas3 поверх актуального Stas2 short labels v1 | done | Использовать `stas3_20260508_20260512_from_stas2_short_labels_v1_20260709_084730` | Stas2 latest |
| Проверить Stas3 артефакты | done | Workbook/CSV/PNG прошли контроль | run output |
| Открыть результат пользователю | current_next | `.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open browse` | user review |
| Протянуть Stas2 WAVE/SHORT ledger в Stas3 entry rows | pending | Делать только если пользователь хочет видеть WAVE-контекст в Stas3-таблицах/PNG | user decision |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного approval | rails |

## Todo 2026-07-09 STAS2 Short Strong Wave Labels

Статус: `STAS2_SHORT_STRONG_WAVE_LABEL_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Подписывать короткие сильные WAVE | done | Проверить `2026-05-12`, участок `W38 LONG 12:32-12:40` | PNG |
| Контрольный run `2026-05-08..2026-05-12` | done | Использовать `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138` | Stas1 carry48 |
| Визуальная сверка пользователем | current_next | Посмотреть, не слишком ли мелко/шумно выглядит компактный `%` в узком блоке | user review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного approval | rails |

## Todo 2026-07-09 STAS2 Continuous Wave Ledger

Статус: `STAS2_CONTINUOUS_WAVE_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Убрать жесткую привязку WAVE к UTC-дню | done | Смотреть `STAS2_CONTINUOUS_WAVES.csv` как главный ledger волн | Stas2 graph |
| Сделать дневные срезы continuous-волн | done | Смотреть `STAS2_MACRO_WAVES.csv`, поля `visible/full/carry` | continuous ledger |
| Показать carry через 00:00 на графике | done | Проверить `W08 SHORT` на `2026-05-10` и `2026-05-11` | PNG |
| Контрольный run `2026-05-10..2026-05-12` | done | Использовать `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330` | Stas1 carry48 |
| Визуальная сверка пользователем | current_next | Проверить дни `2026-05-10`, `2026-05-11`, `2026-05-12`: не мешают ли `<`/`>` и `vis/full` | PNG/XLSX |
| Перенос continuous-wave в ML | blocked | Не делать без отдельной causal-разметки; сейчас это hindsight/review | user approval |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного прямого approval | rails |

## Todo 2026-07-09 STAS2 Macro Wave GAP Segments

Статус: `STAS2_WAVE_GAP_SEGMENTS_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Учесть пропуски в строке `WAVE` | done | Смотреть серые `GAP`-квадраты с процентом на overview | Stas2 graph |
| Сохранить GAP в таблицах | done | Проверять `STAS2_MACRO_WAVES.csv` и лист `Macro waves`: `macro_wave_segment_kind=GAP` | run output |
| Контрольный run `2026-05-10..2026-05-12` | done | Использовать `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_gap_segments_v1_20260709_073810` | Stas1 carry48 |
| Визуальная сверка пользователем | current_next | Открыть `2026-05-10`, затем `2026-05-11` и `2026-05-12`, проверить что GAP не мешает чтению волн | PNG/XLSX |
| Перенос `GAP/WAVE` в ML | blocked | Не делать без отдельной causal-разметки; сейчас это hindsight/review | user approval |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного прямого approval | rails |

## Todo 2026-07-09 STAS2 SHORT And Macro Wave Review

Статус: `STAS2_SHORT_MACRO_WAVE_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `SHORT` по закрытым часам | done | Смотреть `STAS2_HOURLY_PHASES.csv` и строку `SHORT` на overview | Stas2 graph |
| Добавить переменные `WAVE` swing-блоки | done | Смотреть `STAS2_MACRO_WAVES.csv`, лист `Macro waves` и строку `WAVE` на overview | OHLCV day |
| Контрольный run `2026-05-04..2026-05-09` | done | Использовать `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_short_macro_wave_v1_20260709_064759` | Stas1 carry48 |
| Визуальная сверка пользователем | current_next | Открыть `2026-05-04`, затем остальные дни, глазами проверить, устраивает ли порог `1%` для `WAVE` | PNG/XLSX |
| Перенос `macro_wave_*` в ML | blocked | Не делать без отдельного causal-approved ledger; сейчас это hindsight review | user approval |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного прямого approval | rails |

## Todo 2026-07-06 STAS3 Percent Ladder Review

Статус: `STAS3_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать отдельный Stas3 post-entry контур | done | Использовать `STAS3_PERCENT_LADDER_REVIEW/` | user `Стас3` |
| Percent ladder `0.2..7.0%` | done | Смотреть `STAS3_RECORDS.csv` и Excel | Stas2 records |
| Фаза входа Stas1/Stas2 | done | Смотреть `STAS3_ENTRY_PHASE_TABLE.csv` | Stas2 pre-entry fields |
| Фактическое движение после входа | done | Смотреть `STAS3_ACTUAL_MOVEMENT.csv` | OHLCV |
| Reasonable TP и mismatch к 1% | done | Смотреть `STAS3_REASONABLE_TP.csv` и `STAS3_TP_LADDER_V0_RU.md` | phase profile |
| Лестница TP по фазам/profile/setup/session | done | Смотреть `STAS3_TP_LADDER_BY_PHASE.csv`, `STAS3_TP_LADDER_BY_PROFILE.csv` и workbook | Stas3 records |
| Контрольный run `2026-05-02..2026-05-03` | done | Финальный run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260502_20260503_tp_ladder_v0_20260706_183011` | run output |
| Расширенный run `2026-05-04..2026-05-09` | done | Финальный run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_tp_ladder_v0_20260707_055929` | latest Stas2 `20260504..20260509` |
| Визуальный слой `SIGNAL -> ENTRY -> EXIT` | done | Актуальный run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_signal_entry_tp_move_v0_20260707_080253` показывает цену входа и красную стрелку TP-отработки | user visual bugs |
| Анализ больших ходов `SIGNAL/ENTRY -> MFE MAX` | done | Актуальный run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_big_move_review_v2_20260707_090246`; смотреть `STAS3_BIG_MOVE_REVIEW_PAGE_*.png` и листы `Low to MFE max`, `Entry to TP path`, `Exit review` | user request: учиться тянуть больше 0.2% |
| User visual review Stas3 | current_next | Открыть browse/xlsx/big move pages, глазами сверить `EARLY_1PCT_TRAIL_REVIEW`, `BIG_MFE_BUT_DEEP_MAE_REVIEW`, `LATE_MFE_PUMP_REVIEW` | PNG/XLSX/MD |
| Approved-ledger для будущего ML | blocked | Только после ручного review и отдельного `APPROVED_FOR_ML` | user decision |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного явного approval | rails |

## Todo 2026-07-06 STAS3 Separate Chat Handoff

Статус: `STAS2_CLOSED_STAS3_IN_SEPARATE_CHAT_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Stas2 closure | done | Использовать как закрытую базу для следующего чата | user ok |
| Stas3 в текущем чате | blocked | Не начинать здесь, пользователь делает в другом чате | user decision |
| Handoff для Stas3 | done | В новом чате читать `docs/codex/*`, затем брать финальные Stas2 artifacts | Stas2 closed |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного явного approval | rails |

## Todo 2026-07-06 STAS2 Closed For STAS3

Статус: `STAS2_CLOSED_FOR_STAS3_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| STAS 1 inventory | done | Использовать `STAS1_GOOD_LOW_REVIEW/` как базу входов, Stas1 не переписывать | Stas1 runs |
| STAS 2 market phases and sessions | done | Использовать Stas2 как pre-entry контекст фаз/сессий/дня | Stas2 reports |
| Визуальный Stas2 слой на графике | done | Использовать финальный no-label overview с точками как в Stas1 | `STAS2_MARKET_PHASE_REVIEW` |
| No-lookahead контроль Stas2 | done | Для входов использовать только `context_before_entry_check=True` | Stas2 records |
| STAS 3 percent ladder and entry/TP validation | current_next | Составить ТЗ и отдельный слой, который после входа считает MFE/MAE, достижимый процент, время до цели, просадку и реалистичный TP | закрытый Stas2 |
| STAS 4 features/hypotheses/indicators with phases for ML | blocked | Не начинать до отчета Stas3 | Stas3 |
| STAS 5 ML architecture and responsibility map | blocked | Не начинать до отчета Stas4 | Stas4 |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного явного approval | guardrails |

## Todo 2026-07-06 STAS2 Setup Quality Layer

Статус: `STAS2_SETUP_QUALITY_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разделить фон/LONG и качество конкретного входа | done | Смотреть подписи `SETUP` рядом с точками на overview | Stas2 review |
| Подтянуть `stas1_risk_flags` и `stas1_feature_*` в Stas2 CSV/XLSX | done | Использовать `STAS2_RECORDS.csv` и лист `Entry context` | Stas1 carry48 run |
| Добавить `STAS2_ENTRY_SETUP_QUALITY_SUMMARY.csv` | done | Смотреть clean/ok/warn/noise-сводку перед ручной чисткой | setup fields |
| Проверить LA045-LA047 после выноса | done | В CSV/XLSX они должны читаться как `NOISE`; на overview названия возле точек не рисуются | visual review |
| Пользовательский visual review нового графика | current_next | Открыть `2026-05-02` и глазами подтвердить/поправить пороги setup | PNG |
| Stas3 percent ladder / TP validation | blocked | Начинать только после принятия Stas2 setup-схемы | user review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного решения | rails |

## Todo 2026-07-06 STAS2 Background And LONG Wave Visual Fix

Статус: `STAS2_BG_LONG_WAVE_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разделить `Слабая` как фон и направленную LONG-волну | done | Смотреть две полосы `Фон` и `LONG` на overview | Stas2 script |
| Добавить pre-entry `long_wave` поля | done | Использовать `pre_*_long_wave_up_from_low_pct` и `pre_*_long_wave_pullback_from_high_pct` в Stas2 review | entry rows |
| Добавить отдельную summary-таблицу LONG-волн | done | Смотреть `STAS2_ENTRY_LONG_WAVE_SUMMARY.csv` и лист `Long wave summary` | run output |
| Проверить no-lookahead | done | `context_before_entry_check=True`, long-wave окна используют только `open_time_utc < entry_time_utc` | records |
| Пользовательский visual review | current_next | Открыть `.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse` и глазами сравнить `Фон` против `LONG` | PNG |
| Stas3 percent ladder / TP validation | blocked | Начинать только после принятия визуальной схемы Stas2 | user review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного решения | rails |

## Todo 2026-07-06 STAS2 Market Phase Visual Review

Статус: `STAS2_REVIEW_READY_WAIT_USER_VISUAL_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать отдельный Stas2 review-контур | done | Использовать `STAS2_MARKET_PHASE_REVIEW/`, Stas1 не трогать | Stas1 runs |
| Перенести сессии/фазы на график | done | Смотреть `STAS2_DAY_OVERVIEW_YYYYMMDD.png` и `BROWSE_BY_DAY/` | Stas2 script |
| Добавить pre-entry окна `5m/15m/30m/60m` | done | Анализировать `STAS2_RECORDS.csv` и entry context pages | Stas1 entries |
| No-lookahead guard | done | Проверять `context_before_entry_check=True` | Stas2 records |
| Пользовательский visual review | current_next | Открыть `.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse` и глазами отметить, какие сессии/фазы дают шум | PNG |
| Stas3 percent ladder / TP validation | blocked | Начинать только после принятия Stas2 review-схемы | user review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного решения | rails |

## Todo 2026-07-06 STAS2 Market Phase Session Audit

Статус: `STAS2_DONE_WAIT_STAS3_DECISION_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| STAS 1 inventory | done | Использовать `STAS1_GOOD_LOW_REVIEW/` как базу, не переписывать Stas 1 | текущие Stas1 runs |
| STAS 2 market phases and sessions | done | Использовать схему `6 UTC-корзин + day_type`; пользователь принимает/правит ladder фаз перед Stas 3 | `STAS2_MARKET_PHASE_AUDIT_RU.md` |
| STAS 3 percent ladder and entry/TP validation | pending | После принятия Stas 2 построить percent ladder `0.3-0.5 / 0.9-1.0 / 1.5-2.0 / 2.2-4.0+` по фазам/сессиям | Stas 2 report |
| STAS 4 features/hypotheses/indicators with phases for ML | blocked | Не начинать до Stas 3 отчета | Stas 3 |
| STAS 5 ML architecture and responsibility map | blocked | Не начинать до Stas 4 отчета | Stas 4 |

## Todo 2026-07-06 STAS1 Block 1 Locked

Статус: `STAS1_BLOCK_1_DONE_NEXT_CHAT_CONTINUE_FROM_REVIEW_POOL`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Блок 1: прогон low-кандидатов | done | Использовать как baseline | STAS1 |
| Сохранение всех входов из прогона | done | Смотреть CSV/JSON и `BROWSE_BY_DAY/` | run output |
| Управление процентом цели `+1%/+0.5%/target-pct` | done | Подбирать порог для review, не как ML-фичу | outcome label |
| Проверка закрытия после полуночи | done | Использовать `-OutcomeLookaheadHours` | carry outcome |
| Дневной просмотр без шума окон | done | Открывать `open_last_run.ps1 -Open browse` | BROWSE_BY_DAY |
| Следующий чат | current_next | Продолжить с чистки шума low-кандидатов и ручного feedback | user review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного approval | rails |

## Todo 2026-07-06 STAS1 Carry Outcome

Статус: `WAIT_USER_REVIEW_STAS1_CARRY_OUTCOME_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разделить период входов и период outcome | done | Использовать `-OutcomeLookaheadHours` | user decision |
| Не подтягивать сделки до стартового дня | done | Проверять только entry period `-Day .. -EndDay` | guardrail |
| Разрешить `+1%` после полуночи | done | Смотреть `hit_day_utc`, `carried_overnight`, `hold_minutes_to_target` | outcome window |
| Добавить поля carry в CSV/JSON | done | Использовать для DCA/risk review | records |
| Smoke-run `2026-05-07..2026-05-08` с `48h` | done | Пользователь смотрит browse-by-day глазами | PNG/CSV |
| Полный пользовательский run с `-RenderGoodLimit 0` | current_next | Запустить команду из `docs/codex/commands.md` и открыть `-Open browse` | user review |
| Калибровка шума low | pending | После ручных пометок по дневным папкам | visual feedback |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать без отдельного approval | rails |

## Todo 2026-07-06 STAS1 Browse By Day

Статус: `WAIT_USER_REVIEW_STAS1_BROWSE_BY_DAY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сделать дневную структуру просмотра run | done | Использовать `BROWSE_BY_DAY/` | user request |
| Остановить открытие десятков PNG окон | done | `-Open all` и `-Open allcloseups` открывают один стартовый файл | open_last_run |
| Сортировать сделки внутри дня по времени | done | Проверено по `2026-05-04`: CSV monotonic by `entry_time_utc` | renderer |
| Полный run `2026-05-04..2026-05-06` | done | Пользователь смотрит дневные папки глазами | browse run |
| User visual review | current_next | Открыть `-Open browse` или `-Open day -Day ...`, отметить шум/дубли/кривые low | PNG |
| Калибровка low selector | pending | Только после user feedback | review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать | guardrails |

## Todo 2026-07-06 STAS1 ALL Closeups GOOD+BAD

Статус: `WAIT_USER_REVIEW_STAS1_ALL_CLOSEUPS_BAD_X_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить BAD на визуальные closeup-страницы | done | Использовать `GOOD_1PCT_REVIEW_POOL_ALL_CLOSEUPS_PAGE_*.png` | user request |
| Сделать BAD отличимыми от GOOD | done | BAD = красный полупрозрачный крест, GOOD = зеленый треугольник | renderer |
| Сохранить старые GOOD-only страницы | done | Не ломать прежний режим просмотра хороших входов | compatibility |
| User review ALL closeups | current_next | Пользователь смотрит GOOD+BAD вместе и отмечает шум, дубли, неверные low и полезные negative-примеры | PNG |
| Калибровка `visual_entry_low_anchor_suggester.py` | pending | Только после ручного feedback по ALL-страницам | user review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать | guardrails |

## Todo 2026-07-03 STAS1 Good Low Review

Статус: `STAS1_BASELINE_FIXED_NEXT_USER_VISUAL_NOISE_REVIEW`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать основной скрипт `GOOD_1PCT_REVIEW_POOL` как `STAS1` | done | Использовать `src/mlbotnav/visual_entry_good_1pct_review_pool.py` как baseline | user decision |
| Создать видную папку `STAS1_GOOD_LOW_REVIEW` | done | Пользователь запускает команды из корня проекта | project root |
| Команда одного дня `+1%` | done | `.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-02` | STAS1 folder |
| Команда одного дня `+0.5%` | done | `.\STAS1_GOOD_LOW_REVIEW\run_day_0p5.ps1 -Day 2026-05-02` | STAS1 folder |
| Открыть последний run | done | `.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1` | STAS1 runs |
| User visual noise review | current_next | Пользователь отмечает шум/дубли/сдвиги на 1 дне, затем на 3-4 днях | PNG |
| Калибровать `visual_entry_low_anchor_suggester.py` | pending | Делать после ручного feedback, не раньше | user review |
| Snapshot/zip рабочей версии | pending | После принятого результата глазами | calibrated version |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать в STAS1 baseline | approval required |

## Todo 2026-07-02 DCA Risk And Knife Map Rails

Статус: `NEXT_DCA_RISK_AUDIT_V0_ON_W18_W20_NO_ML`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать короткий полигон `W18-W20` | done | Работать только с `2026-04-27..2026-05-17`, run `W18_W20_learning_20260702_082819` | user decision |
| Зафиксировать, что `+1% hit` не gold | done | Использовать `+1%` только как review/outcome, не как ML label | risk audit |
| Зафиксировать цель `10` long-сделок в день | done | Трактовать как верхний лимит качественных входов, не как обязанность добирать мусор | user clarification |
| Лестница фаз `0.3-0.5 / 0.9-1 / 1.5-2 / 2.2-4+` | done | Включить в DCA-аудит как offline outcome-фазы | user clarification |
| `DCA_RISK_AUDIT_V0` | current_next | Считать DCA-корзины, просадку, докупки, поддержку, risk-aware классы и PNG | W18-W20 pool |
| Phase outcome audit | current_next | Для каждой сделки считать достигнутую фазу, время до фазы, просадку и сессию | DCA_RISK_AUDIT_V0 |
| Классы `GOOD_CLEAN_RECLAIM / GOOD_DCA_SURVIVABLE / BORDERLINE_SOFT / BAD_FALLING_KNIFE / BAD_CLUSTER_OVERLOAD` | pending | Уточнить пороги на 21 дне глазами | DCA audit |
| `HEDGE_SIM_V0` | future_after_dca_audit | После DCA-аудита смоделировать защитный SHORT-хедж против перегруза LONG DCA-корзин, без реального API | DCA_RISK_AUDIT_V0 |
| `FULL_HISTORY_KNIFE_MAP_V0` на `126` дней | blocked | Запускать только после стабильной механики на 21 дне | approved short-range process |
| ML/export/training/Optuna | blocked | Только после ручного approved-ledger и отдельного `APPROVED_FOR_ML` | future approval |

## Todo 2026-07-02 Low Anchor Entry 1pct Label Review V1 13 May

Статус: `WAIT_USER_REVIEW_LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Пересобрать 13 мая по правилу `low signal -> next candle entry -> entry + 5bps -> +1%` | done | Использовать V1, не V0 от `anchor_low_price` | user correction |
| Добавить execution band `0bps/5bps/10bps` | done | Считать погрешность только в slippage/execution | entry rails |
| Пометить outcome labels | done | `4` strong, `0` normal, `1` soft, `82` bad | V1 CSV |
| Показать full-day и zoom page 01 пользователю | current_next | Пользователь смотрит, где попали/не попали и что фиксить | PNG |
| Запись в gold/dataset | blocked | Только после ручного visual review и точной фиксации good/bad | user decision |
| Scorer / target-lock / Optuna / ML | blocked | Не запускать на V1 без отдельных этапов и approvals | rails |

## Todo 2026-07-02 Low Anchor 1pct Label Review 13 May

Статус: `WAIT_USER_REVIEW_LOW_ANCHOR_1PCT_LABEL_REVIEW_20260513`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Построить full-day `LOW_ANCHOR_1PCT_LABEL_REVIEW` по `2026-05-13` | done | Показать пользователю full-day и zoom pages | user request |
| Пометить good/bad по `anchor_low_price * 1.01` | done | `8` good, `79` bad | candidate review |
| User visual review | current_next | Пользователь отмечает, какие зеленые реально хорошие и какие красные/сдвиги спорные | PNG |
| ML dataset запись | blocked | Только после ручного подтверждения; outcome label отдельно от causal features | rails |
| Scorer / target-lock / Optuna / ML | blocked | Не запускать без отдельного approval | rails |

## Todo 2026-07-02 Low Anchor Suggester 13 May

Статус: `WAIT_USER_REVIEW_LOW_ANCHOR_20260513_STRICT_SCORE5`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Применить low-anchor suggester к `2026-05-13` | done | Использовать full/strict PNG для visual review | user request |
| Зафиксировать `target_1pct_price` в кандидатах | done | Проверять цены в CSV/JSON | +1% rails |
| Strict-лист `min_score=5.0` | done | Пользователь смотрит `18` кандидатов: норм / крест / сдвиг | PNG |
| Gold-ledger по 13 мая | blocked | Только после ручного visual review | user decision |
| Scorer / target-lock / Optuna / ML | blocked | Не запускать на этих кандидатах без отдельного approval | rails |

## Todo 2026-07-02 Target 1pct Price Fix V0

Статус: `TARGET_1PCT_PRICE_FIX_V0_DONE_NEXT_VISUAL_PASSPORT_STEP`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать `+1%` price target для `2026-05-14 M01..M19` и `2026-05-15 T15L confirmed 7` | done | Использовать как outcome/reference, не как selection feature | manual эталоны |
| Проверить сводку достижений `+1%` | done | `14 день: 13/19`, `15 день: 4/7` | price fix |
| Scorer / target-lock / Optuna / ML | blocked | Только после отдельного решения пользователя и `APPROVED_FOR_ML` | rails |
| Следующий рабочий пункт | current_next | Продолжать по ручным эталонам и паспортным блокам, без cooldown-перебора и без ML | user direction |

## Todo 2026-07-01 Complete 14 May Passport Layers Before T15

Статус: `CURRENT_WAIT_USER_REVIEW_DATASET_BASE_V0_THEN_NEXT_DATASET_STEP`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Не переходить на `T15/2026-05-15`, пока 14 мая не закрыт | done | Держать это как верхнюю рельсу | user correction |
| `V2A_STRUCTURE_LAYER` на `2026-05-14 M01..M19` | done | Использовать как первый слой evidence | V2A artifacts |
| `V2B_FLOW_DENSITY_LAYER` на `2026-05-14 M01..M19` | done | Показать пользователю full-day/zoom PNG | V2B artifacts |
| `V2C_ADX_STOCH_LAYER` на `2026-05-14 M01..M19` | done | Показать full-day/zoom PNG пользователю | user correction: skip repeated RSI/MACD/EMA |
| `V2D_PATTERN_LAYER` на `2026-05-14 M01..M19` | done | Показать full-day/zoom PNG пользователю | V2C |
| `V2E_SUMMARY_MATRIX` по 14 мая | done | Показать V2E PNG пользователю | V2A-V2D |
| Повторить `B018_BOS` отдельно | done | Показать BOS-only PNG пользователю | user request |
| Собрать target-led dataset base 14+15 | done | Показать dataset summary пользователю | user request |
| Выбрать первый рабочий кластер/паспорт-кандидат по 14 мая | current_next_after_review | Брать только после visual review V2E | V2E |
| Решить судьбу `unlabeled_review` | pending | Не включать в `ml_label`, пока пользователь не подтвердит good/reject | dataset base |
| Перенос на `2026-05-15` | blocked | Только после выбора/фиксации первого кластера по 14 мая | completed 14 May |
| Scorer / target-lock / Optuna / ML | blocked | Только после отдельного решения пользователя | rails |

## Todo 2026-07-01 V2A Structure User Review Audit

Статус: `SUPERSEDED_BY_COMPLETE_14_MAY_PASSPORT_LAYERS_BEFORE_T15`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Просмотреть V2A full-day/zoom/Fibo anchors по 14 мая | done | Использовать выводы audit-файла | V2A artifacts |
| Зафиксировать, что `B014/B018` не являются сигналом | done | Держать как context/evidence | audit |
| Зафиксировать Fibo как `context_only` | done | Перед active signal нужен freshness rule | Fibo anchors |
| Перенести V2A на `2026-05-15` по 7 T15 входам | superseded | Не выполнять сейчас: сначала закрыть `V2C/V2D/V2E` по 14 мая | user correction |
| Scorer / target-lock / Optuna / ML | blocked | Только после visual review и отдельного решения | rails |

## Todo 2026-07-01 V2A Structure Overlay 14 May

Статус: `V2A_STRUCTURE_LAYER_20260514_READY_WAIT_USER_REVIEW`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать renderer V2A | done | Использовать `src/mlbotnav/visual_entry_strategy_passport_overlay_v2a.py` | roadmap |
| Наложить `B014/B015/B017/B018` на `2026-05-14 M01..M19` | done | Показать full-day и zoom PNG пользователю | manual ledger |
| Проверить no-lookahead границу | done | Entry price только execution/control | rails |
| Исправить агентский causal-audit по Fibo/BOS | done | Full-day zigzag заменен на prefix-causal zigzag per signal/event | agent audit |
| Сделать Fibo понятным откуда-куда | done | Добавлены `V2A_FIBO_ANCHORS_PAGE_01/02_20260514.png` с `A -> B` | user feedback |
| Проверить кодировку и хвосты python | done | Новые RU-файлы читаются нормально, хвостов после рендера нет | verification |
| Получить user review по 14 мая | done | Пользователь остановил переход на 15 мая: надо закрыть остальные блоки 14 дня | PNG |
| Наложить V2A на `2026-05-15` 7 T15 | blocked | Только после review 14 мая | user decision |
| V2B flow/density | done | Использовать `V2B_FLOW_DENSITY_*_20260514` как evidence/context | V2A |
| V2C ADX/Stochastic | done | `B008/B009` наложены на 14 мая; RSI/MACD/EMA не повторяли | user correction |
| V2D pattern | done | Использовать `V2D_PATTERN_*_20260514` как pattern evidence | V2C |
| V2E summary matrix | done | Использовать `V2E_SUMMARY_MATRIX_20260514` для выбора первого кластера | V2A-V2D |
| First cluster/passport candidate | current_next_after_review | Предложить кластер по V2E после user review PNG | V2E |
| Scorer / target-lock / Optuna / ML | blocked | Только после отдельных решений | rails |

## Todo 2026-07-01 Existing Passport Reconciliation And Overlay

Статус: `V2A_STRUCTURE_LAYER_20260514_READY_WAIT_USER_REVIEW`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать верхний roadmap | done | Использовать `FRESH_TARGET_LED_STRATEGY_PASSPORT_ROADMAP_RU.md` | user direction |
| Подключить агента для read-only аудита | done | `Lorentz`: `26` блоков, `82` активных связки, `82` matrix, пути найдены | user request |
| V2A0 registry reconciliation | done | Использовать `PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md` | registry YAML |
| V2A structure overlay | done | `2026-05-14 M01..M19` использовать как первый слой | V2A0 |
| V2B flow/density overlay | done | `B010/B013/B026` наложены на 14 мая; `B011/B012` позже при необходимости | V2A user review |
| V2C ADX/Stochastic overlay | done | `B008/B009` наложены после пользовательской правки | V2B user review |
| V2D pattern overlay | done | `B019-B024` наложены; `B025` не active | V2C |
| V2E summary matrix | done | Матрица готова, нужен visual review пользователя | V2A-V2D |
| First cluster/passport candidate | current_next_after_review | Выбрать первый кластер/паспорт-кандидат по 14 мая | V2E |
| Scorer / target-lock | blocked | Только после user visual review strategy overlay | user decision |
| Optuna / ML/export/promotion | blocked | Только после отдельных approvals | user approval |

Главный roadmap: `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_STRATEGY_PASSPORT_ROADMAP_RU.md`.

Manifest-сверка: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md`.

## Todo 2026-07-01 Git Remote Push MLbotNav

Статус: `GIT_REMOTE_PUSH_DONE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Настроить автора коммита | done | `Stanislav1567 <Stanislav1567@users.noreply.github.com>` | user GitHub repo |
| Добавить remote | done | `origin=https://github.com/Stanislav1567/MLbotNav.git` | GitHub URL |
| Initial commit | done | `e178c49 Initial commit` | staged source |
| Push main | done | `main` tracks `origin/main` | origin |
| Дальше работать через обычные commits | current_next | Перед изменениями смотреть `git status`, после проверок коммитить осмысленно | Git hygiene |

## Todo 2026-07-01 Git Init MLbotNav

Статус: `SUPERSEDED_BY_GIT_REMOTE_PUSH_DONE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать локальный Git-репозиторий | done | Ветка `main` | user approval |
| Защитить тяжелые/секретные файлы через `.gitignore` | done | Не добавлять `.env`, data/models/reports/logs/packs/tmp/offload/bak | artifact policy |
| Очистить `.env.example` от локального пути | done | Использовать placeholder `C:\path\to\external\project\.env` | privacy |
| Настроить автора коммита | done | `Stanislav1567 <Stanislav1567@users.noreply.github.com>` | Git |
| Добавить remote | done | `https://github.com/Stanislav1567/MLbotNav.git` | GitHub |
| Initial commit + push | done | `e178c49` отправлен в `origin/main` | remote |

## Todo 2026-07-01 Strategy Passport Overlay V2

Статус: `NEXT_BUILD_V2_STRATEGY_PASSPORT_OVERLAY`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Аудит пропуска стратегий в V1 | done | Использовать gap-аудит как стартовую точку V2 | user remark |
| V2A structure layer | pending | Наложить `F035-F041` + `F045-F052`: support/range/channel, strict Fibo, retest/swing, BOS/CHOCH | same 19+7 targets |
| V2B flow layer | pending | Наложить `F019-F034`: volume + density/VPOC | V2A |
| V2C momentum layer | pending | Наложить `F012-F015`: RSI/MACD passport allows | V2B |
| V2D summary matrix | pending | Таблица `target_id -> passport hits / neutral / against` | V2A-V2C |
| Scorer / target-lock | blocked | Только после user visual review V2 | user decision |
| Optuna / ML/export/promotion | blocked | Только после отдельного approval | user approval |

Аудит: `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_STRATEGY_PASSPORT_GAP_AUDIT_20260701_RU.md`.

## Todo 2026-07-01 Codex Agent Launch Kit MLbotNav

Статус: `LAUNCH_KIT_READY_NEXT_OPTIONAL_GIT_INIT_BY_USER`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить наличие проектного `AGENTS.md` | done | Не перезаписывать: файл уже содержит рабочие правила проекта | проектная папка |
| Проверить профили Codex `agent` и `agent-safe` | done | Использовать существующие `C:\Users\007\.codex\agent.config.toml` и `agent-safe.config.toml` | глобальный Codex |
| Создать прямой запуск `MLbotNav` | done | Использовать `Start MLbotNav Codex Agent.cmd` | launcher folder |
| Создать resume для `MLbotNav` | done | Использовать `Resume MLbotNav Codex Agent.cmd` | launcher folder |
| Инициализировать Git | pending_user | Только если пользователь явно попросит `git init` | проект сейчас без `.git` |
| `codex doctor` | done | Зафиксировано: без fail, есть предупреждения по старой истории Codex и отсутствию `.git` | Codex CLI |

## Todo 2026-07-01 Indicator/Hypothesis Review V1 19+7

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V1_READY_WAIT_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Найти пропущенный шаг feature/evidence layer | done | V0 найден, но устарел для текущего 19+7 слоя | user correction |
| Создать V1 по `M01..M19` и 7 `T15` confirmed | done | Использовать `draft_ledger_v1`, не старые 22 candidates | T15 red-arrow fix |
| Наложить RSI/MACD/Fibo/BOS/volume/density/swing | done | Считать только evidence, не сигналом | no-lookahead |
| Показать V1 PNG пользователю | current_next | Получить `норм/фиксить` | generated PNG |
| Draft passport C01 | blocked | Только после review V1 | user decision |
| Scorer / target-lock / Optuna / ML | blocked | Запрещено на этом шаге | rails |

## Todo 2026-07-01 T15 Draft Ledger V1 Confirmed

Статус: `T15_DRAFT_LEDGER_V1_CONFIRMED_NEXT_DRAFT_PASSPORT_C01_NO_SCORER_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Подтвердить `draft_ledger_v1` глазами пользователя | done | Рабочий слой `draft_ledger_v1` | user `норм` |
| Не использовать `draft_ledger_v0` | done | Дальше только v1 | red-arrow fix |
| Выбрать первый кластер для паспорта | done | `T15_C01_SUPPORT_RETEST_LOW`: `T15L02/T15L08/T15L16` | v1 cluster split |
| Создать draft passport C01 | current_next | Описать contract: что ловим, must-have, invalidates, execution price, no-lookahead границы | confirmed v1 |
| Показать passport visual/summary пользователю | pending | После сборки паспорта показать скрин/таблицу и получить `норм/фиксить` | draft passport |
| Entry-only scorer / target-lock | blocked | Только после passport review | rails |
| Optuna / ML/export/promotion | blocked | Только после target-lock и отдельного approval | no approval |

## Todo 2026-07-01 T15 Draft Ledger V1 Red Arrow Fix

Статус: `T15_DRAFT_LEDGER_V1_READY_WAIT_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Принять красные стрелки пользователя | done | Сдвинуты `T15L02/T15L07/T15L08` | user screenshot |
| Собрать `draft_ledger_v1` | done | Использовать v1 как рабочий слой | red arrows |
| Пометить `draft_ledger_v0` superseded | done | Не использовать v0 для паспорта | v1 |
| Показать v1 PNG пользователю | current_next | Получить `норм / фиксить` | v1 PNG |
| Draft passport по одному кластеру | blocked | Только после user review | user decision |
| Scorer/target-lock/Optuna/ML | blocked | Запрещено на этом шаге | rails |

## Todo 2026-07-01 T15 Draft Ledger / Cluster Discussion V0

Статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_READY_WAIT_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать draft-ledger по 7 T15 входам | done | Использовать `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16` | user verdict v1 |
| Добавить entry open и `entry + 5 bps` | done | Цена только execution/control | source CSV |
| Разложить по кластерам | done | `C01=3`, `C02=2`, `C03=2` | visual/types |
| Показать PNG пользователю | current_next | Получить `норм / фиксить` | draft PNG |
| Draft passport по одному кластеру | blocked | Только после user review, первый кандидат `T15_C01_SUPPORT_RETEST_LOW` | user decision |
| Scorer/target-lock | blocked | Только после паспорта и ручного review | rails |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 T15 User Verdict V1

Статус: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NEXT_DRAFT_LEDGER_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Исправить слой с 2 входов на 7 входов | done | `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16` confirmed | user correction |
| Пометить `user_verdict_v0` как superseded | done | Не использовать v0 как рабочий слой | v1 |
| Создать draft-ledger/cluster discussion по 7 входам | current_next | Разложить 7 входов по типам/веткам | v1 |
| Scorer/target-lock | blocked | Только после draft-ledger и user review | target-led rails |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Indicator/Hypothesis Visual Review V0

Статус: `INDICATOR_HYPOTHESIS_REVIEW_READY_NEXT_USER_VISUAL_VERDICT_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать визуальную лестницу RSI/MACD/volume/density/swing/BOS/Fibo | done | Показать PNG пользователю | current script |
| Проверить `2026-05-14` manual gold на инструментах | pending_user | Пользователь смотрит full-day | visual PNG |
| Проверить `2026-05-15` rejected/pending на инструментах | pending_user | Пользователь смотрит full-day и zoom | visual PNG |
| Зафиксировать ассистентский visual verdict | done | RSI/MACD/volume/Fibo не брать как самостоятельный сигнал | visual review |
| Приоритетный zoom `T15L06/T15L13/T15L16` | done | `T15L06/T15L16` strong, `T15L13` possible | priority zoom script |
| Получить пользовательский verdict по `T15L06/T15L16` | done | `T15L06/T15L16` зафиксированы как gold candidates | user "норм" |
| Решить судьбу `T15L13` | done | `possible_not_primary` | user "норм" |
| Создать draft-ledger/cluster discussion `T15L06/T15L16` | current_next | Не target-lock, только подготовка к паспорту | user verdict v0 |
| Зафиксировать, какие инструменты помогает оставить после user verdict | pending_user | Составить manual evidence notes | user verdict |
| Делать scorer/passport/target-lock | blocked | Только после ручного verdict и выбора признаков | target-led rails |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V2

Статус: `USER_FEEDBACK_V2_REJECTS_FIXED_NEXT_PENDING_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `T15L10` в reject | done | `15 bad_noise` total | user text verdict |
| Сохранить feedback v2 | done | Использовать `user_feedback_v2` как актуальный слой | feedback script |
| Разобрать pending `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16` | current_next | Получить `норм/сдвиг/possible/нет` | user visual verdict |
| Создать target-led ledger для 2026-05-15 | blocked | Только после явных good/shift решений | pending unresolved |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V1

Статус: `USER_FEEDBACK_V1_REJECTS_FIXED_NEXT_PENDING_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `T15L21` в reject | done | `14 bad_noise` total | user full-day screenshot |
| Сохранить feedback v1 | done | Использовать `user_feedback_v1` как актуальный слой | feedback script |
| Разобрать pending `T15L02/T15L06/T15L07/T15L08/T15L10/T15L11/T15L13/T15L16` | current_next | Получить `норм/сдвиг/possible/нет` | user visual verdict |
| Создать target-led ledger для 2026-05-15 | blocked | Только после явных good/shift решений | pending unresolved |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V0

Статус: `USER_FEEDBACK_REJECTS_FIXED_NEXT_PENDING_REVIEW_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать красные X пользователя | done | `13 bad_noise` | user screenshots |
| Сохранить screenshots как provenance | done | `3` source PNG copied | user screenshots |
| Создать feedback JSON/CSV/RU/PNG | done | Использовать `user_feedback_v0` | feedback script |
| Разобрать pending `T15L02/T15L06/T15L07/T15L08/T15L10/T15L11/T15L13/T15L16/T15L21` | current_next | Получить `норм/сдвиг/possible/нет` | user visual verdict |
| Создать target-led ledger для 2026-05-15 | blocked | Только после явных good/shift решений | pending unresolved |
| Scorer/passport | blocked | Нужен ledger и правила | target-led rails |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Transfer Review 2026-05-15 Compact V0

Статус: `WAIT_USER_VISUAL_REVIEW_T15L01_T15L22_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать transfer review для `2026-05-15` | done | `22` compact candidates | seed-day learning |
| Сгенерировать full-day PNG | done | Показать пользователю общий план | transfer review |
| Сгенерировать zoom pages | done | Показать page `01..02` | transfer review |
| Получить verdict пользователя | pending_user | `норм` / `нет` / `сдвинуть` / `дубль` / `не тот тип` / `possible` | visual review |
| Создать target-led ledger `T15L` | blocked | Только после verdict | user labels |
| Scorer/passport | blocked | Сначала review и ledger | target-led rails |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Feature Policy EMA Deferred

Статус: `EMA_DEFERRED_NEXT_TEMPLATE_CHECKLIST_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать EMA deferred | done | Не использовать EMA как active condition | user correction |
| Обновить audit wording | done | EMA только reference-only | feature audit |
| Draft no-lookahead scorer checklist | current_next | Делать без EMA: структура/range/low/reclaim/volume/wick | feature policy |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor No-Lookahead Feature Audit V0

Статус: `FEATURE_AUDIT_READY_NEXT_ZOOM_LOCK_OR_SCORER_CHECKLIST_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать группы `manual_gold/bad/possible/shift` | done | `85` записей | extra feedback summary |
| Посчитать no-lookahead признаки | done | Закрытая signal-свеча + прошлый контекст | OHLCV source |
| Сформировать JSON/CSV/RU/PNG | done | Использовать `feature_audit_v0` | feature audit script |
| Проверить no-lookahead boundary | done | Entry-candle OHLCV/future outcome excluded | audit |
| Zoom-lock `manual_shift_review` | pending | Точно проставить новые ручные точки, если выбираем этот путь | user decision |
| Draft no-lookahead scorer checklist | current_next | Описать фильтры good vs bad до entry, без EMA | audit + EMA deferred |
| Event dataset draft | blocked | Только после label policy и/или zoom-lock | no approval |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Extra Auto Feedback Summary

Статус: `EXTRA_AUTO_POOL_REVIEW_COMPLETE_NEXT_FEATURE_AUDIT_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Page `01..06` visual review | done | Все `66` extra candidates разобраны | user verdicts |
| Summary JSON/CSV/RU | done | Использовать как текущий итог extra pool | page feedback |
| Bad noise pool | done | `51` anti-label candidates | summary |
| Possible entries | pending_review | `3` кандидата не gold, сравнить с good entries | feature audit |
| Manual shift review | pending_review | `12` кандидатов требуют отдельного zoom-review | feature audit / user choice |
| No-lookahead feature audit | current_next | Выписать признаки good vs bad/possible/shift до entry | summary |
| Event dataset draft | blocked | Только после feature audit и explicit label policy | no approval |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Extra Auto Page06 Feedback

Статус: `PAGE06_REJECTED_EXTRA_POOL_COMPLETE_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разметить page `06` | done | `6 bad_noise` | user verdict |
| Зафиксировать причину | done | `bad_noise_countertrend_entry` | page 06 |
| Закрыть extra pool | done | Собран summary `66` кандидатов | page 01-06 |
| Следующий шаг | current_next | No-lookahead feature audit | summary |

## Todo 2026-07-01 Low Anchor Extra Auto Page05 Feedback

Статус: `PAGE05_REJECTED_NEXT_PAGE06_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сохранить красный screenshot пользователя | done | Использовать как provenance | user screenshot |
| Разметить page `05` | done | `12 bad_noise` | user verdict |
| Зафиксировать причину | done | `bad_noise_weak_context_entry_mismatch` | page 05 |
| Не создавать manual shift | done | Пользователь назвал входы слабыми/плохими | target-led rails |
| Page `06` review | current_next | Показать последнюю страницу extra candidates | page 05 done |
| Event dataset draft | blocked | Только после завершения review pool и явного решения | labels incomplete |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Extra Auto Page04 Feedback

Статус: `PAGE04_SHIFT_REVIEW_FIXED_NEXT_PAGE05_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сохранить красный screenshot пользователя | done | Использовать как provenance | user screenshot |
| Разметить current auto entries page `04` | done | `12 manual_shift_review` | user verdict |
| Не переписывать времена автоматически | done | Нужен отдельный zoom-review | target-led rails |
| Page `05` review | current_next | Показать следующую страницу extra candidates | page 04 done |
| Zoom-review manual shifts page `04` | pending | Точно проставить новые ручные точки, если пользователь попросит | separate approval |
| Event dataset draft | blocked | `manual_shift_review` не является обучающей меткой | labels incomplete |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Extra Auto Page03 Feedback

Статус: `PAGE03_FIXED_NEXT_PAGE04_OR_INTERIM_FEATURE_AUDIT_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разметить page `03` | done | Все `12` кандидатов rejected | user verdict |
| Зафиксировать причину | done | `bad_noise_weak_context` | page 03 |
| Сделать PNG фиксации | done | Использовать как visual provenance | feedback script |
| Обновить JSON/CSV/RU | done | `12 bad_noise`, `0 possible_entry` | page 03 |
| Page `04` review | current_next | Показать следующую страницу extra candidates | page 03 done |
| Interim feature audit | optional_next | Сравнить первые `3` страницы: `24` reject, `3` possible | page 01-03 labels |
| Event dataset draft | blocked | Только после достаточного набора explicit labels | anti-review |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Extra Auto Page02 Feedback

Статус: `PAGE02_FIXED_NEXT_PAGE03_OR_FEATURE_AUDIT_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Разметить page `02` | done | `LA018/LA020/LA026` possible, остальные reject | user screenshot |
| Сделать PNG фиксации | done | Использовать как visual provenance | feedback script |
| Обновить JSON/CSV/RU | done | `3 possible_entry`, `9 bad_noise` | page 02 |
| Page `03` review | current_next | Показать следующую страницу extra candidates | page 02 done |
| Feature audit possible vs bad | optional_next | Сформулировать no-lookahead признаки отличия | page 01-02 labels |
| Event dataset draft | blocked | Только после достаточного набора explicit labels | anti-review |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Extra Auto Page01 Feedback

Статус: `PAGE01_REJECTED_NEXT_PAGE02_OR_FEATURE_SUMMARY_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Интерпретировать фразу пользователя | done | Зафиксирована чистая формулировка без лишней воды | user verdict |
| Разметить `LA001..LA012` | done | `bad_noise / bad_noise_shallow_bounce / reject` | page 01 |
| Сделать PNG фиксации | done | Показать пользователю для контроля | feedback script |
| Обновить рельсы | done | Использовать как актуальный feedback layer | docs |
| Page 02 review | current_next | Показать `LA013..` следующей страницей или собрать признаки отличия good/bad | page 01 done |
| Event dataset draft | blocked | Только после достаточного набора explicit labels | anti-review |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Extra Auto Review V1

Статус: `WAIT_USER_VISUAL_REVIEW_EXTRA_AUTO_PAGE_01_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать extra auto review pack | done | Использовать `extra_auto_review_v1` | resolved label-ledger V1 |
| Сгенерировать PNG-страницы | done | Показать страницу `01` пользователю | 66 candidates |
| Проверить JSON/CSV/RU | done | JSON: `66/66`, страниц: `6` | generation |
| Разметить page 01 | pending_user | `bad_noise` / `duplicate` / `possible_entry` / `wrong_type` / `ignore_unclear` | user visual verdict |
| Разметить page 02-06 | pending | Делать после page 01, чтобы не замылить обзор | page 01 verdict |
| Event dataset draft | blocked | Только после anti-review labels | extra review |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Label Ledger V1 Resolved

Статус: `NEXT_EXTRA_AUTO_ANTI_REVIEW_OR_EVENT_DATASET_DRAFT_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| User review pending `M05/M14/M15/M16/M17` | done | Пользователь сказал `норм` | pending PNG |
| Resolved label-ledger V1 | done | Использовать как актуальный label ledger | user verdict |
| Pending shift review | done | Pending targets: `0` | V1 |
| Extra auto candidates | current_next | Разобрать `66` unlabeled candidates как anti-review pool | V1 |
| Event dataset draft | pending | Можно готовить только как draft/no-ML, с explicit labels | extra review |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Label Ledger V0

Статус: `WAIT_USER_REVIEW_PENDING_SHIFT_M05_M14_M15_M16_M17_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Подтвердить feedback M03/M09/M10/M11 | done | Пользователь сказал `норм` | feedback PNG |
| Создать label-ledger V0 | done | Использовать JSON/CSV/RU как рабочий слой меток | feedback confirmed |
| Разделить target labels | done | `10 exact`, `4 user-feedback not-gold`, `5 pending` | V0 + feedback |
| Сделать PNG pending review | done | Показать пользователю `M05/M14/M15/M16/M17` | label ledger |
| Ручное решение по pending | pending_user | Для каждой точки: норм / сдвинуть / auto not-gold / оставить ledger | pending PNG |
| Event dataset V0 | blocked | Только после решения по pending-точкам | manual review |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor User Feedback M03/M09/M10/M11

Статус: `DONE_FEEDBACK_PACK_NEXT_REVIEW_OR_V1_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать красный feedback пользователя | done | Использовать JSON/MD/PNG из `user_feedback_v0` | user screenshot |
| Скопировать исходный скрин | done | Хранить как provenance для правок | temp screenshot |
| Перевести `±3m` из gold в near-review | done | В следующем V1/датасете не считать near auto золотым попаданием | feedback |
| M03/M09/M11 | done | `auto_late`, positive брать из ledger | feedback |
| M10 | done | `early anchor-zone-review`, не делать молчаливый сдвиг ledger | feedback |
| Следующий шаг | pending_user | Пользователь смотрит feedback PNG: норм / что фиксить | feedback PNG |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Low Anchor Suggester V0

Статус: `WAIT_USER_VISUAL_REVIEW_LOW_ANCHOR_V0_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать low-anchor suggester V0 | done | Использовать как review-подсказчик, не стратегию | M01..M19 ledger |
| Seed-day JSON/CSV/PNG | done | Показать пользователю zoom sheet | SOLUSDT 1m 2026-05-14 |
| Target-nearest review `M01..M19` | pending_user | Получить verdict: норм/сдвиг/нет/дубль/рано/поздно | user visual review |
| Уменьшить лишние 85 кандидатов | pending | Делать после пользовательского verdict, чтобы не потерять хорошие low | review labels |
| Event dataset V0 | blocked | Сначала разметить positives/anti на seed-day | review labels |
| Optuna/ML/export/promotion | blocked | Запрещено без отдельного approval | approval missing |

## Todo 2026-07-01 Data Scope Monthly Samples

Статус: `DONE_DATA_SCOPE_MONTHLY_VISUAL_SAMPLE_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить sample-дни по месяцам | done | `2026-01-27`, `2026-02-28`, `2026-03-28`, `2026-04-28`, `2026-05-28` | C01 126-day source audit |
| Full-day PNG по каждому sample-дню | done | Показать пользователю общий contact sheet и отдельные PNG | local SOLUSDT 1m data |
| Проверка `00:00 -> next 00:00` | done | Все sample-дни `1440` строк, границы корректны | manifest |
| Сверка с внешней биржей | not_started | Делать только отдельным шагом, если пользователь попросит | user decision |
| Optuna/ML/export/promotion | blocked | Не относится к data-scope audit | approval missing |

## Todo 2026-07-01 C01 126 Days Source Audit

Статус: `AUDIT_DONE_C01_SCOPE_FIXED_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить источник `126 дней` | done | Подтверждено: `SOLUSDT 1m only`, 126 файлов, 1440 строк каждый | local data |
| Проверить C01 result artifacts | done | JSON/CSV сходятся: 126 дней, 25 кандидатов, 23 дня с кандидатами | C01 multi-day |
| Зафиксировать недофиксацию manifest | done | Будущие multi-day должны писать `symbol/timeframe/source glob/date range/command` | process rule |
| Продвигать C01 V1 | blocked | Остановлен: мало сделок и смешанное визуальное качество | user decision |
| Optuna/ML/export/promotion | blocked | Нужен отдельный путь и approval; по C01 V1 запрещено | approval missing |

## Todo 2026-07-01 C02A Seed-Lock Created

Статус: `NEXT_MULTI_DAY_OR_NEXT_PASSPORT_DECISION_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| C02A scorer PNG review | done | Пользователь подтвердил 3 сделки | user review |
| C02A seed-lock `8.1` | done | `M01/M02/M08` защищены от регрессии | scorer review |
| Multi-day C02A | pending_decision | Решить, проверяем ли C02A на других днях сейчас | seed-lock |
| Следующий паспорт другого типа | pending_decision | Альтернатива multi-day: перейти к следующему target-led типу | seed-lock |
| Optuna | blocked | Только после готового паспорта, lock/multi-day и отдельного approval | approval missing |
| ML/export/promotion | blocked | Только после `APPROVED_FOR_ML` | approval missing |

## Todo 2026-06-30 C02A Entry-Only Scorer V0

Статус: `WAIT_USER_VISUAL_REVIEW_C02A_ENTRY_ONLY_SCORER_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| C02A rules visual review | done | Пользователь сказал продолжать | C02A rules PNG |
| Entry-only scorer C02A `7.1` | done | Показать PNG scorer пользователю | C02A rules accepted |
| User visual review scorer PNG | current_next | Получить `норм / фикс` по `C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.png` | scorer PNG |
| Target-lock C02A | blocked | Только после пользовательского `норм` по scorer PNG | user review |
| Multi-day C02A | blocked | Только после target-lock/решения по seed-day | target-lock |
| Optuna | blocked | Только после готового паспорта, lock/multi-day и отдельного approval | approval missing |
| ML/export/promotion | blocked | Только после `APPROVED_FOR_ML` | approval missing |

## Todo 2026-06-30 C02 Good/Bad Audit Done

Статус: `NEXT_C02_SPLIT_OR_ROUTER_DECISION_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Аудит good vs bad | done | `C02` признан широким low-event finder | user labels |
| Full-day audit PNG | done | Использовать для визуального контроля | audit |
| Split/router decision | pending | Решить: чистый `C02A_TRUE_DEEP_CAPITULATION` или low-event router | audit |
| Entry-only scorer C02 | blocked | Не запускать до split/router decision | split/router |
| Multi-day C02 | blocked | Не запускать до scorer-review на seed-дне | scorer not ready |
| Optuna | blocked | Только после готового паспорта и отдельного approval | approval missing |
| ML/export/promotion | blocked | Только после `APPROVED_FOR_ML` | approval missing |

## Todo 2026-06-30 C02 User Review Complete

Статус: `NEXT_C02_AUDIT_GOOD_VS_BAD_NO_ML_NO_OPTUNA`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Ручная разметка `C02E01..C02E16` | done | `10 GOOD_ENTRY`, `6 BAD_ENTRY` зафиксированы | user screenshots |
| Контрольный PNG good/bad | done | Показать пользователю для проверки глазами | review ledger |
| Синхронизация C02 ledger/layer/passport/matrix | done | Использовать эти файлы как текущий источник C02 | manual labels |
| Аудит good vs bad | pending | Найти, чем `C02E03..C02E12` отличаются от `C02E01/E02/E13..E16` без future data | review complete |
| Entry-only scorer C02 | blocked | Не запускать до аудита правил | good/bad audit |
| Multi-day C02 | blocked | Не запускать до scorer-review на seed-дне | scorer not ready |
| Optuna | blocked | Нужен отдельный approval после готового паспорта | approval missing |
| ML/export/promotion | blocked | Нужен отдельный `APPROVED_FOR_ML` | approval missing |

## Todo 2026-06-30 Passport Bench Step Plan

Статус: `WAIT_USER_LABEL_C02E01_C02E16`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Расписать лестницу Passport Bench V0 | done | Использовать как порядок работ | user request |
| `PASSPORT_COVERAGE_MATRIX_V0` | done | Матрица создана | target ledger |
| Рабочая папка C02 | done | Папка создана | coverage matrix |
| Паспорт-драфт C02 | done | Описаны `must_have/invalidates/inputs/forbidden` | C02 folder |
| Seed full-day PNG C02 | done | Показать пользователю `v2` | passport draft |
| Zoom C02 | done | Включен в seed visual `v2` | seed full-day |
| User review seed visual C02 | done | Пользователь сказал `норм` | seed visual |
| No-lookahead candidate layer C02 | done | `96` raw, `16` events, seed `3/3` | seed visual |
| Review pack C02 | done | Zoom sheet и ledger готовы | candidate layer |
| Ручная разметка кандидатов | pending | Разметить `C02E01..C02E16` | review pack |
| Optuna | blocked | Не запускать | approval missing |
| ML/export/promotion | blocked | Не запускать | `APPROVED_FOR_ML` missing |

## Todo 2026-06-30 Fresh Target-Led Passport Bench V0

Статус: `NEXT_BUILD_PASSPORT_COVERAGE_MATRIX_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Аудит последних решений и паспортов | done | Использовать как новый рельс | user request |
| `C01 V1` | stopped | Не продвигать в Optuna/ML, не считать общим выводом | multi-day visual reject |
| `PASSPORT_COVERAGE_MATRIX_V0` | pending | Создать матрицу покрытия `M01..M19` паспортами | target ledger |
| Синхронизировать ledger metadata | pending | Отразить C01 stop/seed-lock без production-lock | C01 artifacts |
| `C02_DEEP_CAPITULATION_LOW` | pending | Подготовить паспорт по `M01/M02/M08` | coverage matrix |
| Full-day PNG на реальной шкале | pending | Для каждого нового паспорта показывать пользователю | candidate layer |
| Ручная разметка good/bad/wrong/late | pending | Делать до ML и Optuna | full-day PNG |
| Optuna | blocked | Только после готового паспорта и отдельного approval | user approval |
| ML/export/promotion | blocked | Только после `APPROVED_FOR_ML` | user approval |

## Todo 2026-06-30 Fresh Target-Led C01 Multi-Day Check V1

Статус: `WAIT_USER_REVIEW_C01_MULTI_DAY_ZOOMS`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сдвинуть `M05` на одну свечу вправо | done | Актуально `10:43 -> 10:44` | user fix |
| Оставить `M06` без изменений | done | Актуально `12:00 -> 12:01` | user fix |
| Собрать новый eye-check PNG | done | Показать пользователю | M05 shift |
| Старый scorer V0 | stale | Пересчитать только после visual confirm | M05 shift |
| Пересчитать entry-only scorer V1 | done | `2/2`, ложных `0` на `2026-05-14` | user decision |
| Зафиксировать user confirm V1 | done | Принято по `далее поехали по рельсам` | PNG V1 |
| Создать seed target-lock | done | `M05/M06` защищены от регрессии | scorer V1 |
| Создать входной контракт V1 | done | Данные для signal/entry описаны | seed lock |
| Raw multi-day check V1 | done | 126 дней, 25 кандидатов, частота нормальная | contract V1 |
| Показать zoom contact sheet | pending | Разметить `годится / не годится / отдельный тип` | multi-day PNG |
| C01_QUALITY_FILTER_V2 | pending | Делать только после ручной оценки кандидатов | user review |
| Optuna | blocked | Запрещена до target-lock и готового паспорта | user approval |
| ML/export/promotion | blocked | Только после отдельного `APPROVED_FOR_ML` | user approval |

## Visual Entry next after TARGET_LOCKED_STRATEGY_TZ 2026-06-29

Статус: `NEXT_BUILD_TARGET_LOCK_LEDGER_THEN_V11`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сделать аудит потерь хороших входов | done | Использовать как источник правил | V9/V10 |
| Создать активное ТЗ target-lock | done | `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_TARGET_LOCK_TZ_RU.md` | audit |
| Создать `target_lock_ledger` | pending | JSON/MD target-by-target coverage | manual entries + V9/V10 |
| Создать lock-файл целей | pending | Зафиксировать V9/V10 good hits | ledger |
| Реализовать `V11_RECOVER_RANKED_MISSES` | pending | Разные стратегии для разных входов | locks |
| Передача в ML | blocked | Только после multi-day stable + `APPROVED_FOR_ML` | user approval |

Главное правило: новая версия не считается улучшением, если она потеряла locked target.

## Visual Entry next after EVENT_RANKED_BRICKS_V10 2026-06-29

Статус: `NEXT_BUILD_V11_RECOVER_RANKED_MISSES`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать `V10_EVENT_RANKED_BRICKS` | done | Использовать как cleaner/rank diagnostic | V9 |
| Проверить V10 на `2026-05-13` | done | `HOT_CHAIN` чистый `1/9`, остальные false-only | Manual 13 |
| Проверить V10 на `2026-05-14` | done | Шум ниже V9, но потеряны нужные входы | Manual 14 v2 |
| Передача в ML | blocked | Нельзя: V10 partial diagnostic | User approval + stable result |
| Построить `V11_RECOVER_RANKED_MISSES` | pending | Отдельно вернуть потерянные `warm/hot/deep` входы без noisy union | V10 audit |

Граница V11: не расширять общий union. Каждый новый подрежим должен иметь отдельный PNG и scorer. Не использовать cooldown `30/45/60/90`, future return, TP/SL, MFE/MAE или entry-candle OHLCV.

## Visual Entry next after BRICK_BY_BRICK_SELECTOR_V9 2026-06-29

Статус: `NEXT_BUILD_V10_EVENT_RANKED_BRICKS`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать `V9_BRICK_BY_BRICK_SELECTOR` | done | Использовать как карту кирпичей, не как ML-кандидат | V8 |
| Проверить V9 на `2026-05-13` | done | Чистый `HOT_CHAIN_EVENT_LOW` = `1/9`, `0` false | Manual 13 |
| Проверить V9 на `2026-05-14` | done | `warm/hot/deep` ловят цели, но шумят | Manual 14 v2 |
| Передача в ML | blocked | Нельзя: нет стабильного multi-day clean result | User approval + stable result |
| Построить `V10_EVENT_RANKED_BRICKS` | pending | Внутри каждого low-event выбрать один лучший сигнал; разделить `warm`, `hot-first`, `deep` | V9 audit |

Граница V10: не использовать cooldown `30/45/60/90`; не использовать TP/SL, MFE/MAE, future return, entry-candle OHLCV. Каждый слой должен давать PNG и scorer отдельно.

## Visual Entry next after NEGATIVE_CONTEXT_SUPPRESSION_V8 2026-06-29

Статус: `NEXT_BUILD_V9_BRICK_BY_BRICK_SELECTOR`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать V8 negative suppress | done | Использовать как suppress diagnostic | V7 |
| Проверить V8 на `2026-05-13` | done | Зафиксирован чистый кирпич `08:48`, `0` false | Manual 13 |
| Проверить V8 на `2026-05-14` | done | `HOT_FIRST` улучшен, но noisy | Manual 14 v2 |
| Передача в ML | blocked | Нельзя: V8 не стратегия | User approval + stable multi-day result |
| Построить `V9_BRICK_BY_BRICK_SELECTOR` | pending | Не union; отдельные чистые кирпичи: hot-chain, early-hot, deep-terminal | V8 audit |

Граница V9: сначала визуально чистый отдельный режим на PNG, потом scorer. Не собирать общий union, пока режимы сами по себе шумные.

## Visual Entry next after GENERALIZATION_V7 2026-06-29

Статус: `NEXT_BUILD_NEGATIVE_CONTEXT_SUPPRESSION_V8`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Реализовать `GENERALIZATION_V7` | done | Использовать только как diagnostic fail / feature map | V6 validation fail |
| Прогнать V7 на `2026-05-13` | done | Зафиксировано `1/9`, много false | Manual 13 |
| Прогнать V7 на `2026-05-14` | done | Зафиксировано `4/17` best f1 и `11/17` noisy union | Manual 14 v2 |
| Передача в ML | blocked | Нельзя: `GENERALIZATION_V7_DIAGNOSTIC_FAIL_NO_ML` | User approval + stable validation |
| Построить `NEGATIVE_CONTEXT_SUPPRESSION_V8` | pending | Резать боковые микролои, hot upper shelf, повторные false retest-серии | V7 audit |

Граница для V8: контракт `signal close -> next open`, `lookahead=NO`, slippage `5 bps`; без TP/SL/MFE/MAE/future return/entry-candle OHLCV и без cooldown `30/45/60/90`.

## Visual Entry next after manual bottoms 13/14 2026-06-25
Статус: `NEXT_BUILD_REVERSAL_BOTTOM_KNIFE_DROP_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Перевести PNG `2026-05-13` в manual entries | done | Использовать как validation labels | Пользовательская разметка |
| Перевести PNG `2026-05-14` в manual entries | done | Использовать как holdout labels | Пользовательская разметка |
| Отдельно отметить авто-ножи `AK#` | done | Не считать ML labels без подтверждения | OHLCV auto scan |
| Прогнать CP06 без подкрутки | done | Зафиксировано `best=[]` на обоих днях | CP06 DEV-12 |
| Построить новый слой `REVERSAL_BOTTOM_KNIFE_DROP_V0` | pending | Context/trigger/confirm/suppress + PNG overlay | Manual 13/14 |
| Передача в ML | blocked | Только после нового слоя, validation/holdout и ручного `APPROVED_FOR_ML` | User review |

## Visual Entry CP06 validation/holdout next 2026-06-25
Статус: `WAIT_FOR_MANUAL_LABELS_13_14`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить наличие labels для `2026-05-13` | done | Нужен новый `manual_entries.json` | Пользовательская разметка |
| Проверить наличие labels для `2026-05-14` | done | Нужен новый `manual_entries.json` | Пользовательская разметка |
| Зафиксировать readiness-аудит | done | Использовать как стоппер перед validation | `cp06_validation_holdout_readiness_20260625_RU.md` |
| Запустить CP06 на `2026-05-13` | pending | Только без подкрутки после labels | Manual labels 13 |
| Запустить CP06 на `2026-05-14` | pending | Только без подкрутки после validation | Manual labels 14 |

Seed PNG для разметки:
1. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.png`;
2. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.png`.

В ML ничего не передавать.

## Visual Entry v3 next after DEEP_CAPITULATION_RECLAIM 2026-06-25
1. Не передавать `DQ01_EQ01_PLUS_DEEP_RECLAIM` или `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP` в ML: recall высокий, но ложных входов `73-95`.
2. Построить следующий слой `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`.
3. В suppression проверить: кластерный приоритет последнего/лучшего сигнала, запрет ранних сигналов внутри одного падения, отдельный cooldown после severe flush, score-ranking по `mfi/rsi/stoch/low_zone/ret/body/wick/vol_z`.
4. Отдельно решить `08:26`: либо оставить high-risk no-wick как diagnostic-only, либо добавить строгий confirmation без entry-candle lookahead.
5. Каждый новый слой проверять exact next-open scorer, PNG overlay и список живых `python.exe`.

## Visual Entry v3 next after EARLY_FLUSH_REVERSAL 2026-06-25
1. Не передавать `EQ01_Q09_SEVERE_SOFT45`, `EQ03_Q09_SEVERE_SOFT45_NOWICK` или отдельные early-варианты в ML: ложных входов все еще слишком много.
2. Построить `DEEP_CAPITULATION_RECLAIM` для пропусков `12:33`, `15:26`, `17:00`.
3. Проверить, можно ли затем собрать более строгий ensemble: `quality baseline` + `severe flush` + `deep capitulation reclaim`, без рискованного no-wick режима, если он не пройдет suppression.
4. Каждый новый слой проверять exact next-open scorer и PNG overlay.
5. После каждого прогона проверять живые `python.exe` процессы MLbotNav/APTuna/visual-entry.

## Visual Entry v3 next after quality filter 2026-06-25
1. Не передавать `Q09_ENSEMBLE_Q07_Q01` в ML: `53` ложных входа на DEV-день все еще много.
2. Построить `EARLY_FLUSH_REVERSAL` для пропущенных `01:42`, `05:13`, `07:16`, `08:26`.
3. Построить `DEEP_CAPITULATION_RECLAIM` для пропущенных `12:33`, `15:26`, `17:00`.
4. Каждый новый слой проверять exact next-open scorer и PNG overlay.
5. После каждого прогона проверять живые `python.exe` процессы MLbotNav/APTuna/visual-entry.

## Visual Entry v3 next steps 2026-06-25
1. Не передавать `VISUAL_MICRO_BOTTOM_SIGNATURE_V0` в ML: слишком много ложных входов.
2. Добавить следующий diagnostic слой suppression/quality filters: `anti_drift_down`, `reclaim_quality`, `support_confluence`, `capitulation_absorption`, `bottom_event_clustering`.
3. После каждого нового варианта считать `target_hits/missed_targets/false_entries/precision/recall/f1_visual` и прикладывать PNG overlay.
4. Проверять, что после прогонов не остались живые `python.exe` процессы MLbotNav/APTuna/visual-entry.
## Visual Entry v3 next after passport-family 2026-06-25
Статус: `NEXT_BUILD_VISUAL_MICRO_BOTTOM_SIGNATURE_V0`.

Закрыто: честный passport-family runner и расширенный PNG overlay готовы. Лучший passport-family результат `1/11` hits и `20` false, поэтому это не кандидат.

Следующий шаг:
1. сделать `VISUAL_MICRO_BOTTOM_SIGNATURE_V0` как отдельный DEV diagnostic layer;
2. использовать признаки `local_low_5/10`, `range_pos_60`, `low_range_pos_60`, `MFI/RSI/Stoch`, `EMA gap/slope`, wick/reclaim, volume spike;
3. scorer только exact next-open по v3 `manual_entries.json`;
4. строить PNG overlay для каждого top-кандидата;
5. не переходить на `2026-05-13` validation, пока DEV не даст осмысленное улучшение без сотен ложных входов.

Граница: в ML ничего не передавать.

## Visual Entry v3 next 2026-06-25
Статус: `NEXT_CONFIRM_V3_THEN_STRUCTURAL_FAMILIES`.

1. Визуально подтвердить v3 PNG: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows/visual_entry_combo_simple_arrows_manual_v3_targets_20260625T112336Z.png`.
2. Если пользователь сдвинет стрелки, обновить `manual_entries.json` до v3.1.
3. Не крутить solo RSI/Stoch/EMA/volume как самостоятельные входы.
4. Строить no-lookahead подсемьи: `DEEP_CAPITULATION_NEXT_OPEN`, `SHALLOW_SUPPORT_PULLBACK_NEXT_OPEN`, `REENTRY_AFTER_SPIKE_NEXT_OPEN`.
5. Добавлять структурные фильтры support/CHOCH/divergence/volume-profile, потом только exact scorer, затем validation `2026-05-13` без подкрутки.

## Visual Entry Calibration DEV-12 next 2026-06-25
Статус: `NEXT_BUILD_VISUAL_DRIVEN_PASSPORT_DIAGNOSTIC`.

Закрыто: первый `manual_entries.json` по `2026-05-12` создан, `visual_entry_score` реализован и проверен на старом B001 trade CSV.

Артефакты:
1. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries.json`;
2. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries_audit_20260512_DEV_RU.md`;
3. `reports/qa_gate/visual_entry_score_SOLUSDT_1m_visual_dev_20260625_20260512_v1_oos_backtest_trades_SOLUSDT_1m_2026-05-12_long_only_20260625T073603Z.json`.

Следующий практический шаг: составить список solo-passport / family-кандидатов для visual scorer, отдельно спроектировать reversal/dip-buy LONG family для входов `01:44`, `04:15`, `09:12`, затем проверять candidate на `2026-05-13` без подкрутки.

## Visual Entry next implementation 2026-06-25
Статус: `DONE_SOLO_RUNNER_NEXT_COMBO_REVERSAL`.

Закрыто: diagnostic runner для выбранных существующих паспортов готов и выдал таблицу `passport_id / hits / misses / false_entries / precision / recall / f1_visual`.

Артефакты:
1. `src/mlbotnav/visual_entry_solo_passport_runner.py`;
2. `tests/test_visual_entry_solo_passport_runner.py`;
3. `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV.json`;
4. `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV_RU.md`.

Следующий инженерный шаг: собрать `REVERSAL_DIP_BUY_LONG v0` как combo/family, где контекст падения/растяжения (`F009`, EMA-down) отделен от trigger (`F059`/свечной reversal) и suppression-фильтров против ложных входов.

Граница: это diagnostic-only; не ML-кандидат до validation/holdout.

## Visual Entry overlay requirement 2026-06-25
Статус: `ALWAYS_DO_WITH_VISUAL_TESTS`.

Для каждого следующего visual-test:
1. посчитать `visual_entry_score`;
2. построить PNG через `render_visual_entry_overlay`;
3. показать PNG пользователю;
4. только потом делать вывод о качестве паспорта/комбо.

## Visual Entry Calibration TZ follow-up 2026-06-25
Статус: `PARTIAL_DONE_DEV_2026_05_12_READY`.

ТЗ готово: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_CALIBRATION_TZ_RU.md`.

По `2026-05-12` первый `manual_entries.json` создан и `visual_entry_score` запущен. Для `2026-05-13` и `2026-05-14` разметка пока хранится как validation/holdout-контекст и не используется для подбора параметров.

## Visual Entry Calibration next step 2026-06-25
Статус: `DEV_2026_05_12_MARKUP_PROCESSED_KEEP_13_14_LOCKED`.

Папка seed-скриншотов: `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625`.

Пользователь вернул разметку по трем PNG. Обработан только DEV-день `2026-05-12`; `2026-05-13` и `2026-05-14` пока не использовать для подбора, чтобы сохранить validation/holdout.

## B001 marked-entry fixed backtest follow-up 2026-06-25
Статус: `DONE_NEGATIVE_OPTIONAL_REVERSAL_FAMILY_NEXT`.

Аудит: `reports/qa_gate/b001_marked_entry_fixed_backtest_audit_20260625T073900Z_RU.md`.

Закрыто: фиксированные B001 параметры проверены на бэктесте. Они ловят только часть отмеченных momentum-входов (`09:25`, `12:36`) и дают отрицательный OOS.

Следующий шаг, если пользователь хочет ловить именно красные стрелки "у дна": проектировать отдельную reversal/dip-buy family, а не снижать `p_enter_long` и не размягчать B001 momentum-family до шума.

## B001 marked-entry screenshot follow-up 2026-06-25
Статус: `OPTIONAL_NEXT_REVERSAL_FAMILY_DESIGN`.

Аудит: `reports/qa_gate/b001_marked_entry_screenshot_audit_20260625T070500Z_RU.md`.

Если пользователь хочет именно входы "у дна" по красным стрелкам, следующий шаг не раздушивать старую momentum-family до шума, а спроектировать отдельную reversal/dip-buy family: падение `ret_12/ret_24 <= -X`, локальная стабилизация, объем/EMA/первый разворотный бар.

## Shared-study profile-edge coverage follow-up 2026-06-25
Статус: `DONE_FIXED_CONFIRMED`.

Аудит фикса: `reports/qa_gate/shared_study_profile_edge_coverage_fix_20260625T063700Z_RU.md`.

Закрыто: найден и исправлен сдвиг профильного forcing через `profile_edge_worker_offset`, раннее расходование edge slots до profile sampling и отсутствие распределения edge-задач между worker-ами.

Контрольный smoke `b001_3of5_long_shared_edgefix3_20260625_115056` подтвердил: final snapshot `w3` terminal `42/42`, core `5/5 PASS`, profile `7/7 PASS`, forced min/max полный `7/7`.

Ограничение: старые и новые B001 LONG smoke отрицательные/нулевые, не кандидаты; в ML ничего не передавать. Следующий route выбирать уже без старого coverage warning.

## B001 family-unified 4/5 LONG repeat 2026-06-24
Статус: `DONE_NEGATIVE_NEXT_KEEP_3OF5_DECISION`.

Аудит: `reports/qa_gate/b001_family_unified_4of5_long_shared_repeat_audit_20260624T195100Z_RU.md`.

Пользовательский повтор `4/5 LONG` на shared-study завершился `OK`, но OOS `-5.4889095203104477`, сделок `1`. Это отрицательный diagnostic, не кандидат; в ML ничего не передавать.

Coverage warning: core `5/5 PASS`, profile `2/7 PASS`. Следующий актуальный decision остается из более свежего `3/5 LONG`: либо закрыть вопрос profile-edge coverage, либо запускать `3/5 SHORT` как diagnostic-only.

## B001 family-unified shared-study next diagnostic 2026-06-24
Статус: `B001_3OF5_LONG_DONE_NEXT_DECISION`.

Закрыто: `B001 family-unified 3/5 LONG` на shared-study `3x3/9`.

Аудит: `reports/qa_gate/b001_family_unified_3of5_long_shared_audit_20260624T195200Z_RU.md`.

Результат: launcher `OK`, best worker `w3`, OOS `-2.0302055441506761`, сделок `1`. Это отрицательный diagnostic, не кандидат; в ML ничего не передавать.

Перед следующим запуском учесть warning: profile edge coverage неполный (`F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`) при core coverage `5/5`. Если нужен чистый coverage proof, сначала закрыть этот вопрос. Если нужен только runtime diagnostic, следующий возможный шаг: сгенерировать и прогнать `B001 family-unified 3/5 SHORT` как diagnostic-only.

## Optuna shared-study process-pool next use 2026-06-24
Статус: `READY_FOR_NEXT_SHARED_STUDY_RUN_WITH_EDGE_WARNING`.

Инфраструктура закрыта: `reports/qa_gate/optuna_shared_study_process_pool_audit_20260624T190435Z_RU.md`.

Для следующего диагностического прогона, если продолжаем B001 family-unified, использовать:
1. `ProcessWorkers=3`;
2. `SearchWorkersPerProcess=3`;
3. `Threads=9`;
4. `SearchWorkers=9`;
5. `OptunaTrials=42`;
6. `-SharedOptunaStudy`;
7. уникальный `-SharedStudyId`.

Следующий возможный B001 diagnostic: `3/5 LONG` на shared-study профиле, затем отдельно `SHORT`, если пользователь подтверждает продолжение B001. Отрицательные, пустые, `NO_GO` и `VALIDATION_FAIL` результаты в ML не передавать.

## Optuna single-worker next use 2026-06-24
Статус: `USE_1X9_9_FOR_NEXT_B001_DIAG`.

Для следующего B001 family-unified diagnostic использовать профиль `1x9/9`: `Threads=9`, `SearchWorkers=9`, `ProcessWorkers=1`, `SearchWorkersPerProcess=9`, `OptunaTrials=42`.

Цель: одна общая Optuna-история вместо трех раздельных worker.

## B001 family unified follow-up 2026-06-24
Статус: `UNIFIED_5OF5_DONE_OPTIONAL_4OF5_NEXT`.

Закрыто: реализован и проверен режим одного семейного звена `B001_family_move`. Strict `5/5` LONG/SHORT дал `0` OOS-сделок.

Если пользователь продолжает диагностическую ветку B001, следующий шаг: сгенерировать unified `4/5` LONG/SHORT и прогнать smoke. Если снова ноль, проверить unified `3/5`.

Если пользователь возвращается в основной маршрут, следующий строгий шаг остается `B003.1 large LONG 2н/1н`. В ML ничего не передавать.

## B001 family strict follow-up 2026-06-24
Статус: `STRICT_5OF5_DONE_OPTIONAL_4OF5_NEXT`.

Закрыто: strict `5/5` smoke LONG/SHORT на B001. Оба направления дали `0` OOS-сделок из-за `EMPTY_ACTION_GATE`.

Если пользователь продолжает диагностическую ветку семейного блока, следующий логичный шаг: сделать такую же проверку `4/5`, затем при нуле `3/5`. Приоритет качества сверху вниз: `5/5` идеал, `4/5` запасной, `3/5` минимальный диагностический компромисс.

Если пользователь возвращается в основной маршрут, следующий строгий шаг остается `B003.1 large LONG 2н/1н`. В ML ничего не передавать.

## B001_COMBO_DIAG visual follow-up 2026-06-24
Статус: `DONE_GATE_VISUAL_AUDIT`.

Закрыто: проверено, почему LONG/SHORT сделки визуально концентрируются в узком участке дня. День полный, причина в runtime-фильтрах:
1. LONG режется на `F-gate`.
2. SHORT режется на `min_expected_move_pct=0.001`.

Следующий рабочий маршрут не меняется: либо продолжать optional diagnostic 31 combos smoke, либо вернуться к основному `B003.1 large LONG 2н/1н`. В ML ничего не передавать.

## B001_COMBO_DIAG follow-up 2026-06-24
Статус: `OPTIONAL_DIAG_NEXT_31_COMBOS_SMOKE`.

Аудит текущего smoke: `reports/qa_gate/b001_combo_diag_n_of_m_audit_20260624T125500Z_RU.md`.

Если пользователь продолжает диагностическую ветку, следующий безопасный шаг:
1. прогнать 31 комбинацию `B001_RET_N` на smoke 1д/1д LONG;
2. затем отдельно SHORT;
3. в large 2н/1н брать только tradeful/неотрицательные комбинации.

Если пользователь возвращается в основной маршрут, следующий строгий шаг остается `B003.1 large LONG 2н/1н`.

В ML ничего не передавать.

## B003 block route 2026-06-24
Статус: `NEXT_B003_1_LARGE_LONG`.

Предыдущие блоки:
1. `B001` закрыт итогом `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.
2. `B002` закрыт итогом `reports/qa_gate/b002_block_summary_b002_3_20260624T100800Z_RU.md`.

Следующий точный шаг: `B003.1 large LONG 2н/1н`.

Команда находится в `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.

Правило: запускать только один `-UseTemporaryUnlock` job за раз. Активный worker-профиль: `3x3/9` (`Threads=9`, `SearchWorkers=9`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`). В ML ничего не передавать.

## B001/B002 block route 2026-06-24
Статус: `CLOSED_THROUGH_B002_3_NEXT_B003`.

Закрыто:
1. `B001.1` smoke LONG 1д/1д.
2. `B001.2` smoke SHORT 1д/1д.
3. `B001.3` smoke-аудит: `reports/qa_gate/b001_smoke_1d1d_audit_20260624T075006Z_RU.md`.
4. `B001.4` large LONG 2н/1н: `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.
5. `B001.5` large SHORT 2н/1н: `reports/qa_gate/b001_large_short_b001_5_audit_20260624T094057Z_RU.md`.
6. `B001.6` итог блока: `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.
7. `B002.1` large LONG 2н/1н: `reports/qa_gate/b002_large_long_b002_1_audit_20260624T100300Z_RU.md`.
8. `B002.2` large SHORT 2н/1н: `reports/qa_gate/b002_large_short_b002_2_audit_20260624T100700Z_RU.md`.
9. `B002.3` итог блока: `reports/qa_gate/b002_block_summary_b002_3_20260624T100800Z_RU.md`.

Следующий точный шаг: `B003.1 large LONG 2н/1н`.

Команда находится в `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.

Правило: запускать только один `-UseTemporaryUnlock` job за раз. Новый активный worker-профиль: `3x3/9` (`Threads=9`, `SearchWorkers=9`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`). В ML ничего не передавать.

## Block-Family Route 2026-06-24
Status: `READY_FOR_B001_BLOCK`.

Audit: `reports/qa_gate/block_family_passport_route_audit_20260624T064900Z.md`.

Completed:
1. Confirmed with independent agent audit that the intended route is block/family calibration.
2. Added `src/mlbotnav/block_family_manifest.py`.
3. Added `APTuna/run_block_family_selection.ps1`.
4. Added `tests/test_block_family_manifest.py`.
5. Dry-run checked `B001` expands to `F001..F005`.

Rules:
1. Run one block/family as one work item.
2. For family blocks, run all active solo F-passports in that block and choose one block winner or `NO_BLOCK_WINNER`.
3. Run LONG and SHORT separately and sequentially when `-UseTemporaryUnlock` is used.
4. Do not package, approve, or ingest block results into ML during this route.

Next exact step: run `B001` block LONG, then `B001` block SHORT, then audit the two block reports and fix if needed.

## Min-Move Runtime Guard Follow-Up 2026-06-24
Status: `FIX_APPLIED_SUPERSEDED_BY_BLOCK_ROUTE`.

Audit: `reports/qa_gate/ml_optuna_zero_trade_min_move_diagnostic_20260624T051535Z.md`.

Completed:
1. Added guard/status so selected min-move cannot silently stay unreachable after action gate in `exchange_like` mode.
2. Adjusted default 1m `min_expected_move_grid` to `0.0,0.001,0.002,0.003`.
3. Added report diagnostics for action-gate count, min-move count, entries, and proxy quantiles.
4. Added regression tests; focused pytest passed with `124 passed`.

Old F068 next-step pointer is superseded by the block-family route.

## Route Memory Audit 2026-06-23
Status: `ON_ROUTE`.

Audit: `reports/qa_gate/ml_optuna_route_memory_audit_20260623T205751Z.md`.

Current control audit after F067: `reports/qa_gate/ml_optuna_route_status_audit_after_f067_20260624T044311Z.md`.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file.

Do not start package creation, approval registry update, or ML ingest until a large-window candidate passes and then passes validation.

Last updated UTC: 2026-06-23T22:57:00Z

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.18 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_18_f067_audit_20260623T225700Z.md`.

Final result: F067 Pattern Strength LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.17 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_17_f066_audit_20260623T224200Z.md`.

Final result: F066 OBV Bearish Divergence LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.16 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_16_f065_audit_20260623T223100Z.md`.

Final result: F065 OBV Bullish Divergence LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.15 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_15_f064_audit_20260623T222100Z.md`.

Final result: F064 MACD Bearish Divergence LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.14 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_14_f063_audit_20260623T221200Z.md`.

Final result: F063 MACD Bullish Divergence LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.13 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_13_f062_audit_20260623T220200Z.md`.

Final result: F062 RSI Bearish Divergence LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.12 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_12_f061_audit_20260623T215100Z.md`.

Final result: F061 RSI Bullish Divergence LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.11 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_11_f060_audit_20260623T213900Z.md`.

Final result: F060 Bearish Engulfing LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.10 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_10_f059_audit_20260623T213000Z.md`.

Final result: F059 Bullish Engulfing LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.11 Run F060_ENGULFBEAR_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.9 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_9_f058_audit_20260623T211900Z.md`.

Final result: F058 Shooting Star LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.10 Run F059_ENGULFBULL_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.8 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_8_f057_audit_20260623T205000Z.md`.

Final result: F057 Hammer LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.7 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_7_f056_audit_20260623T203800Z.md`.

Final result: F056 Bearish Pin Bar LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.8 Run F057_HAMMER_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.6 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_6_f055_audit_20260623T202700Z.md`.

Final result: F055 Bullish Pin Bar LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.5 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_5_f054_audit_20260623T201700Z.md`.

Final result: F054 Inside Bar LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Next exact step: `8.2.6 Run F055_PINBULL_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.4 Closed
Status: `CLOSED_NO_GO_FIX_APPLIED`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.

Final result: F053 Doji LONG and SHORT both returned OOS `0.0` with `0` trades on the large clean `core` window.

Do not build an ML package from this run. Do not add it to approved registry. Do not ingest it into ML.

Operational rule: do not launch two `-UseTemporaryUnlock` process-pool jobs in parallel; the launcher now rejects the second live unlock.

Next exact step: `8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.3 Closed
Status: `CLOSED_VALIDATION_FAIL_NO_ML_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_3_f052_fixed_validation_audit_20260623T194700Z.md`.

Final result: fixed F052 CHOCH LONG params validated on adjacent clean `core` window returned OOS `-5.696708101293968` with `1` trade and `goal_pass=false`.

Do not build an ML package from this validation. Do not add it to approved registry. Do not ingest it into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T195125Z.json`.

Next exact step: continue with the next user-selected passport/action discovery, or define a new validation idea with its own audit boundary.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.2 Closed
Status: `CLOSED_POSITIVE_TEST_CANDIDATE_NEEDS_VALIDATION`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_2_f052_audit_20260623T193700Z.md`.

Final result: F052 CHOCH LONG on the large clean `core` window produced `1` OOS trade and `+5.3486475132039635`; F052 SHORT produced `0` trades.

Do not build an ML package automatically from this run. Do not start ML training.

Next exact step: manual decision: validate F052 LONG, explicitly approve draft package build, or continue next passport/action discovery.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2.1 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_1_f050_audit_20260623T192700Z.md`.

Final result: F050 BOSUP `long_only` on the large clean `core` window produced `0` OOS trades and `0.0` OOS return.

Do not build an ML package from this run. Do not start ML training.

Next exact step: `8.2.2 Run F052_CHOCH_ALLOW large-window candidate`, unless user overrides the target.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.2 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_audit_20260623T191900Z.md`.

Final result: F051 BOSDOWN `short_only` on the large clean `core` window produced `0` OOS trades and `0.0` OOS return.

Do not build an ML package from this run. Do not start ML training.

Next exact step: manual decision for the next passport/action calibration target or revised `8.2` candidate run.

## Current ML Stage 8 Pointer 2026-06-23 Step 8.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.

Next exact step: `8.2 Run Optuna calibration`.

Final checks: large clean window audit `PASS`; missing files `0`; new tests `4/4 OK`; focused smoke/ingest tests `22/22 OK`.

Do not start ML training. Optuna calibration is next.

## Current ML Smoke Pointer 2026-06-23 Stage 7 Closed
Status: `STAGE_7_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.

Next exact step: `8.1 Fix large clean window`.

Final checks: smoke window `PASS`; approved registry `PASS`; ML ingest builder `PASS`; dataset contract `PASS`; focused Stage 7 tests `67/67 OK`.

Do not start ML training. Stage 8 starts with the larger clean window.

## Current ML Smoke Pointer 2026-06-23 Step 7.5 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.

Next exact step: `7.6 Stage 7 closeout`.

Final checks: dataset builder `PASS`; dataset contract `PASS`; registry validator/reader/admission status `PASS`; focused ingest tests `24/24 OK`.

Do not start ML training. Stage 7 closeout is next.

## Current ML Smoke Pointer 2026-06-23 Step 7.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.

Next exact step: `7.5 Run ML ingest`.

Final checks: registry validator `PASS`; admission status `PASS`; registry reader `PASS`; package contract/alignment audits `PASS`; focused tests `42/42 OK`.

Do not start ML training. Dataset builder / ML ingest is the next separate WBS item.

## Current ML Smoke Pointer 2026-06-23 Step 7.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.

Next exact step: `7.4 Add package to approved registry`.

Final checks: contract `PASS`; direct contract API `PASS` in both modes; all package alignment audits `PASS`; registry boundary checks `PASS`; focused tests `48/48 OK`; text_guard `PASS`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training.

## Current ML Smoke Pointer 2026-06-23 Step 7.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.

Next exact step: `7.3 Run package contract audit`.

Final checks: contract `PASS`; all package alignment audits `PASS`; focused tests `42/42 OK`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; text_guard `PASS`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training.

## Current ML Smoke Pointer 2026-06-23 Step 7.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.

Next exact step: `7.2 Build test package`.

Final checks: smoke manifest audit `PASS`; new tests `5/5 OK`; focused ML smoke/alignment tests `78/78 OK`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; reject-log builder `PASS / NO_REJECTIONS`; text_guard `PASS`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training.

## Current ML Alignment Pointer 2026-06-23 Stage 6 Closed
Status: `STAGE_6_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.

Next exact step: `7.1 Smoke run`.

Final checks: focused ML tests `121/121 OK`; all five alignment audits `PASS / NO_APPROVED_PACKAGES`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; reject-log builder `PASS / NO_REJECTIONS`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181511Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before smoke-run plan says so.

## Current ML Alignment Pointer 2026-06-23 Step 6.5 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.

Next exact step: `6.6 Stage 6 closeout`.

Final checks: new tests `6/6 OK`; focused ML tests `121/121 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_admission_status_audit_20260623T180909527952Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181123Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before Stage 6 closeout.

## Current ML Alignment Pointer 2026-06-23 Step 6.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.

Next exact step: `6.5 Check admission status`.

Final checks: new tests `8/8 OK`; focused ML tests `115/115 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_data_windows_audit_20260623T154607261155Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154759Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before Stage 6 alignment audit is closed.

## Current ML Alignment Pointer 2026-06-23 Step 6.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.

Next exact step: `6.4 Check data windows`.

Final checks: new tests `7/7 OK`; focused ML tests `107/107 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_calibration_params_audit_20260623T154050444104Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154240Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before Stage 6 alignment audit is closed.

## Current ML Alignment Pointer 2026-06-23 Step 6.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.

Next exact step: `6.3 Check calibration params`.

Final checks: new tests `6/6 OK`; focused ML tests `100/100 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_passport_context_audit_20260623T153553932585Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153741Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before Stage 6 alignment audit is closed.

## Current ML Alignment Pointer 2026-06-23 Step 6.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.

Next exact step: `6.2 Check passport context`.

Final checks: new tests `5/5 OK`; focused ML tests `94/94 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_run_id_audit_20260623T152715670875Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153207Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before Stage 6 alignment audit is closed.

## Current ML Ingest Pointer 2026-06-23 Stage 5 Closed
Status: `STAGE_5_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.

Next exact step: `6.1 Check run_id alignment`.

Final text_guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before Stage 6 alignment audit.

## Current ML Ingest Pointer 2026-06-23 Step 5.5 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.

Next exact step: `5.6 Stage 5 closeout`.

Final checks: registry validator `PASS`; reject-log smoke `PASS / NO_REJECTIONS` at `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before Stage 5 is closed and audited.

## Current ML Ingest Pointer 2026-06-23 Step 5.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.

Next exact step: `5.5 Add rejection reasons`.

Final checks: registry validator `PASS`; builder smoke `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before Stage 5 is closed and audited.

## Current ML Ingest Pointer 2026-06-23 Step 5.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.

Next exact step: `5.4 Реализовать сборку ML dataset`.

Final checks: registry validator `PASS`, `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML training before dataset assembly is implemented and audited.

## Current ML Ingest Pointer 2026-06-23 Step 5.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.

Next exact step: `5.3 Реализовать чтение registry`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML ingest/training before registry reading and dataset assembly are implemented.

## Current ML Ingest Pointer 2026-06-23 Step 5.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.

Next exact step: `5.2 Запретить прямое чтение Optuna reports`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML ingest/training before Stage 5 route is implemented.

## Current ML Approval Registry Pointer 2026-06-23 Stage 4 Closed
Status: `STAGE_4_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.

Next exact step: `5.1 Найти текущую точку ML ingest`.

Do not add packages to `approved_packages` without explicit manual approval. Do not start ML ingest before Stage 5 route is implemented.

## Current ML Approval Registry Pointer 2026-06-23 Step 4.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.

Next exact step: `4.5 Закрытие этапа 4`.

Do not add packages to `approved_packages` without explicit manual approval.

## Current ML Approval Registry Pointer 2026-06-23 Step 4.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.

Next exact step: `4.4 Сделать validator registry`.

Do not add packages to `approved_packages` without explicit manual approval.

## Current ML Approval Registry Pointer 2026-06-23 Step 4.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.

Next exact step: `4.3 Добавить запреты registry`.

Do not add packages to `approved_packages` without explicit manual approval.

## Current ML Approval Registry Pointer 2026-06-23 Step 4.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.

Next exact step: `4.2 Описать формат registry`.

Do not add packages to `approved_packages` without explicit manual approval.

## Current ML Candidate Package Pointer 2026-06-23 Stage 3 Closed
Status: `STAGE_3_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.

Next exact step: `4.1 Создать registry файл`.

Do not auto-approve the package; Stage 4 begins the manual approval registry workflow.

## Current ML Candidate Package Pointer 2026-06-23 Step 3.6 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.

Next exact step: `3.7 Закрытие этапа 3`.

Do not skip to ML approval; package approval is a separate manual stage.

## Current ML Candidate Package Pointer 2026-06-23 Step 3.5 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.

Next exact step: `3.6 Добавить audit.md`.

Do not skip to ML approval; package approval is a separate manual stage.

## Current ML Candidate Package Pointer 2026-06-23 Step 3.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.

Next exact step: `3.5 Добавить manifest.json`.

Do not skip to package audit or ML approval; they are separate Stage 3 steps.

## Current ML Candidate Package Pointer 2026-06-23 Step 3.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.

Next exact step: `3.4 Добавить исходные отчеты`.

Do not skip to manifest/audit files; they are separate Stage 3 steps.

## Current ML Candidate Package Pointer 2026-06-23 Step 3.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.

Next exact step: `3.3 Добавить trade_log.csv`.

Do not skip to manifest/audit files; they are separate Stage 3 steps.

## Current ML Candidate Package Pointer 2026-06-23 Step 3.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.

Next exact step: `3.2 Добавить calibration_package.json`.

Do not skip to manifest/trade_log/audit files; they are separate Stage 3 steps.

## Current ML Contract Pointer 2026-06-23 Stage 2 Closed
Status: `STAGE_2_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.

Next exact step: `3.1 Создать структуру пакета`.

Do not auto-approve anything for ML. Stage 3 must build candidate package artifacts first.

## Current ML Contract Pointer 2026-06-23 Step 2.8 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.

Next exact step: `2.9 Закрытие этапа 2`.

Do not move to Stage 3 until Stage 2 closeout confirms pipeline CSV PASS, OOS CSV PASS, required columns audit PASS, and text_guard PASS.

## Current ML Contract Pointer 2026-06-23 Step 2.7 Closed
Status: `CLOSED_PASS_AFTER_CONTROLLED_TEMP_UNLOCK`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.

Next exact step: `2.8 Проверить OOS CSV`.

Do not move to `2.9` until a fresh OOS CSV passes `ml_trade_dataset_contract`.

## Current ML Contract Pointer 2026-06-23 Step 2.6 Closed
Closed: `2.6 Добавить MAE/MFE`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.

Next exact step: `2.7 Проверить pipeline CSV`.

Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.

## B001 Family-Unified Diagnostic 2026-06-24
Status: `pending`.
Artifact from last audit: `reports/qa_gate/b001_single_worker_fast_finish_audit_20260624T180000Z_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Confirm single-worker power profile | done | Keep `1 процесс / 9 search-workers` | Latest run audit |
| Explain fast finish | done | Treat strict `5/5` as empty-gate diagnostic, not worker failure | Optuna report |
| Test B001 family-unified `4/5` 1д/1д LONG | pending | Generate/run matrix with `entry_action_min_confirmations=4` | User approval/current route |
| Test B001 family-unified `4/5` 1д/1д SHORT | pending | Run only after LONG confirms tradeful behavior or as paired diagnostic | LONG/route decision |
| Escalate to `3/5` | pending | Only if `4/5` remains empty | `4/5` audit |

## Optuna Worker Profile Correction 2026-06-24
Status: `pending_next_run`.
Artifact: `reports/qa_gate/optuna_1x9_vs_3x3_worker_audit_20260624T183000Z_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Compare `1x9/9` and `3x3/9` dry-run | done | Treat profiles as non-equivalent physically | Launcher dry-run |
| Restore working load profile | done | Use `3x3/9` for real B001 diagnostics | Audit |
| Run B001 family-unified `4/5` LONG 1д/1д | done | Result tradeful negative, no promotion | Audit |
| Run B001 family-unified `4/5` SHORT 1д/1д | pending | Use same `3x3/9` profile | LONG/route decision |

## B001 Family-Unified 4/5 LONG Result 2026-06-24
Status: `done_tradeful_negative`.
Artifact: `reports/qa_gate/b001_family_unified_4of5_long_3x3_audit_20260624T184500Z_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Run B001 family-unified `4/5` LONG 1д/1д on `3x3/9` | done | Do not promote, result negative | Audit |
| Decide next B001 softness check | pending | Run `3/5 LONG` on `3x3/9` if continuing B001 | User route |
| Run B001 family-unified `4/5` SHORT | pending | Optional paired diagnostic | User route |

## Current ML Contract Pointer 2026-06-23 Step 2.5 Closed
Closed: `2.5 Добавить hit labels`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.

Next exact step: `2.6 Добавить MAE/MFE`.

Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.

## Current ML Contract Pointer 2026-06-23 Step 2.4 Closed
Closed: `2.4 Добавить duration labels`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_4_duration_labels_audit_20260623T125816Z.md`.

Next exact step: `2.5 Добавить hit labels`.

Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.

## Current ML Contract Pointer 2026-06-23
Next strict work is not a new Optuna run.

Accepted plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Budget: `10-14 hours` engineering work, excluding long runtime waiting.
Plan format: WBS numbered steps `1.1`, `1.2`, ..., with stage closeout points like `1.7`, `2.9`, `3.7`.
Closed: `1.1 Create ML trade dataset contract document`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_1_audit_20260623T170449Z.md`.
Closed: `1.2 Зафиксировать обязательные идентификаторы`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_2_audit_20260623T170721Z.md`.
Closed: `1.3 Зафиксировать поля входа и выхода`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_3_audit_20260623T171023Z.md`.
Closed: `1.4 Зафиксировать trade outcome labels`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_4_audit_20260623T171324Z.md`.
Closed: `1.5 Зафиксировать правило допуска в ML`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_5_audit_20260623T171643Z.md`.
Closed: `1.6 Сделать проверку контракта`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_6_audit_20260623T122406Z.md`.
Closed: `1.7 Закрытие этапа 1`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.
Closed: `2.1 Добавить run-level context`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.
Next exact step: `2.2 Добавить passport context`.

Implement the ML trade dataset contract first:
1. Add row-level passport context to trade/OOF outputs: `action_id`, `passport_id`, `block_id`, `calibration_params_json`.
2. Add trade outcome labels: `trade_id`, `bars_in_trade`, `tp_hit`, `sl_hit`, `timeout_hit`, `mae_pct`, `mfe_pct`.
3. Add JSON-vs-CSV alignment audit so Optuna params, pipeline report, OOS report, and CSV rows cannot drift.
4. After this, use clean `core` window train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Artifact: `reports/qa_gate/optuna_ml_entry_exit_alignment_audit_20260623T162411Z.md`.

## Current Passport Registry Pointer 2026-06-22T12:57:27Z
Next user-provided passport must first be assigned to the correct `Bxxx` block in `configs/calibration_action_passports.yaml`.
After registry entry: create/update one executable matrix under `configs/calibration_matrices/passport_actions`, then run solo passport calibration.
Do not revive old full/catalog/feature_sweep matrices for baseline work without an approved passport migration.

## Active Calibration Source Override
For calibration-node work, do not use this long historical todo as the active queue.
The active queue is `docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md` and `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.

## Current Active Pointer 2026-06-04T08:56:24Z
Closed: Optuma bridge Step 1 `calibration_params` anchor gap.
Result: selected Optuna calibration params now propagate into final train/OOS path and are saved in train report/model payload.
Checks: changed-file `py_compile PASS`; focused tests `79/79 OK`.

## Current Active Pointer 2026-06-04T09:06:15Z
Closed: Optuma bridge Steps 2-5.
Result: `volume_flow`, `density_profile`, `structure_ta` threshold flags, and FIBO matrix/runtime wiring now use the declared calibration params.
Checks: focused tests `95/95 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS` for 7 YAML matrices x 2 contours x 3 grid presets.

## Current Active Pointer 2026-06-04T09:16:54Z
Closed: `pattern_structure_volume_entry` repair.
Result: classic figure patterns and the `pattern + structure_ta + volume_flow` entry bundle are now runtime features and calibrated matrix rows.
Checks: focused tests `97/97 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS`; `text_guard PASS`.

## Current Active Pointer 2026-06-04T10:20:10Z
Closed: dry command gate and `pattern long_only narrow`.
Observed: `pattern long_only medium` runtime OK, but CPU max `97%` exceeded user limit `85%`.
Current pointer: pause before `pattern long_only wide`; confirm CPU profile first.
Recommended next action: rerun/continue with safer profile `ProcessWorkers=2`, `SearchWorkers=6`, `SearchWorkersPerProcess=3`, or explicitly allow current `3x9` with hard-stop.

## CPU Rule Update 2026-06-04
Short CPU spikes up to `100%` are allowed if they quickly return near `80-85%`.
Treat overload as sustained CPU `>85%` for roughly `2-5` minutes.
Do not abandon the whole run chain on overload; record the event, reduce the profile, and continue the same substep.
Current plan: try `3/9/3`; if sustained overload appears, reduce to `2/6/3`.

## Current Active Pointer 2026-06-04T10:30:51Z
Closed: `pattern` block full runtime after CPU rule update.
Result: `long_only` and `short_only` both completed `narrow/medium/wide`; workers `3/3`; candidate `NO_CANDIDATE`; best `long_only narrow`, `0%`, trades `0`.
Artifact: `reports/qa_gate/pattern_block06_full_closeout_20260604T103051Z.json`.
Readable report: `reports/qa_gate/pattern_block06_human_readable_20260604T103051Z_RU.md`.
Next active step: fix/verify fallback candidate `calibration_params` propagation because final `best_oos` currently records `selected_calibration_params={}` even when search-level candidates have params; then rerun/replay block06. Do not use old chronology.

## Current Active Pointer 2026-06-03T16:48:08Z
Closed: APTuna block alignment audit.
Result: `PASS`, `issues=0`, `blockers=0`; all 6 calibrated blocks match APTuna block matrices and compile across `long_only`/`short_only` plus `narrow`/`medium`/`wide`.
Artifact: `reports/qa_gate/aptuna_block_alignment_audit_20260603T164808Z.json`.
Next active task: continue strict sequential sweep with `H003` matrix generation/compile, then `H003 long_only` full stack.

## Current Active Pointer 2026-06-03T13:16:59Z
Closed: `H001` (`price_volatility` / `ret_1` / `return_lookback`).
Completed runtime shape: `long_only` x `narrow/medium/wide` and `short_only` x `narrow/medium/wide`, profile `3x3/9`.
Result: runtime/grid coverage OK, candidate `NO_CANDIDATE`.
Closeout artifact: `reports/qa_gate/h001_slot_closeout_20260603T131659Z.json`.
Next active task: `H002` (`price_volatility` / `ret_3` / `return_lookback`) matrix compile; after PASS, run `H002 long_only` full stack.

Readable report format fixed: parent slot `Hxxx`, child stack cards `Hxxx-LONG` and `Hxxx-SHORT`, closeout `Hxxx-SLOT`. Do not treat `H002` as short from `H001`; `H002` is the next feature/hypothesis slot.

## Current Active Pointer 2026-06-03T15:41:33Z
Closed: `H002` (`price_volatility` / `ret_3` / `return_lookback`).
Completed runtime shape: `long_only` x `narrow/medium/wide` and `short_only` x `narrow/medium/wide`, profile `3x3/9`.
Result: runtime/grid coverage OK, candidate `NO_CANDIDATE`.
Closeout artifact: `reports/qa_gate/h002_slot_closeout_20260603T154133Z.json`.
Human-readable report updated: `reports/optuna_catalog/index/hypothesis_feature_sweep_human_ru.md`.
Readable heading format corrected: use `Hxxx | <точное русское название из configs/features_block.yaml>`.
Full RU names catalog created: `docs/CALIBRATION_NODE_CURRENT/RU_NAMES_CATALOG_2026-06-03.md`.
Next active task: `H003` (`price_volatility` / `ret_6` / `return_lookback`) matrix compile; after PASS, run `H003 long_only` full stack.

## Current Active Pointer 2026-06-03T11:28:24Z
Closed: `structure_ta` and `pattern` `narrow/medium/wide` x `long_only/short_only`, runtime OK after OOS-report robustness fix.
Best `structure_ta`: `wide long_only`, OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production.
Best `pattern`: `wide long_only`, OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production.
Pattern closeout artifact: `reports/qa_gate/calibration_node_pattern_closeout_20260603T112654Z.json`.
Health after closeout: text_guard `PASS`, readiness freeze preserved, `pip check PASS`.
Next active task: no production/unfreeze; define a separate new TZ or GO package before any production step.
Do not use this historical todo as the task queue.

## Current Active Pointer 2026-06-03T12:18:33Z
User paused the current `TOP_EXPERIMENTAL` candidate.
New task queue is the sequential hypothesis/feature sweep in `docs/CALIBRATION_NODE_CURRENT/`.
Active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_HYPOTHESIS_FEATURE_SWEEP_2026-06-03_RU.md`.
Inventory is closed: `69` slots total, `56` calibratable, `13` non-calibrated including `H000` control.
Table: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`.
`H001` compile passed: `reports/qa_gate/h001_feature_sweep_matrix_compile_20260603T121833Z.json`.
`H001 narrow long_only` completed with launcher `OK`, workers `3/3`, best OOS `-30.924389997582892%`, trades `13`, class `negative_runtime_ok`; artifact `reports/qa_gate/h001_narrow_long_only_20260603T122520Z.json`.
TZ corrected: long and short are separate stacks; each stack runs `narrow -> medium -> wide`; standard profile is `3x3/9`, trials/timeouts `60/300`, `120/600`, `180/900`.
`H001 narrow short_only` completed with launcher `OK`, workers `3/3`, best OOS `+0.2544418318741748%`, trades `1`, class `provisional_plus_goal_fail`; artifact `reports/qa_gate/h001_narrow_short_only_20260603T124931Z.json`.
Next active task: run `H001 medium long_only` from `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`, then update the sweep table and move strictly to `H001 medium short_only`.

## Current Pointer
Previous V3 TZ pointer is restored by `P2137`, post-sync checked by `P2138`, and dated chain fixed by `P2139`.
We go from `docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md`, section 7, timestamp `2026-06-02T06:52:50Z`: `Package A = NO_CANDIDATE`, next V3 branch is exact `Package B` slot definition.
Current chain start: UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`.
`P2079` remains preserved as `candidate_for_forward`, but forward heartbeat `p2079-f1-data-gate-check` is paused and no manual forward runtime should start before Package B is closed or the user explicitly redirects.
Independent agent/audit cross-check completed UTC `2026-06-02T12:51:17Z`, local `2026-06-02 17:51:17 +05:00`: route is correct with boundary.
`P2140` inventory completed UTC `2026-06-02T12:59:00Z`, local `2026-06-02 17:59:00 +05:00`: old Package B is historical only; current V3 Package B exact slots are not defined yet.
`P2141` exact slots completed UTC `2026-06-02T13:00:00Z`, local `2026-06-02 18:00:00 +05:00`.
`P2142` matrix slices and command-set/dry-run completed UTC `2026-06-02T13:05:59Z`, local `2026-06-02 18:05:59 +05:00`: 4 matrix slices generated, 18 commands emitted, dry-run/preflight `18/18 PASS`.
`P2142` post-sync checks completed UTC `2026-06-02T13:08:40Z`, local `2026-06-02 18:08:40 +05:00`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`.
`P2143` Package B `long_only` runtime completed UTC `2026-06-02T13:15:35Z`, local `2026-06-02 18:15:35 +05:00`: runtime `9/9 PASS`, catalog class `neutral`, accepted positive candidates `0`.
`P2143` post-sync checks completed UTC `2026-06-02T13:18:47Z`, local `2026-06-02 18:18:47 +05:00`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`.
`P2144` Package B `short_only` runtime completed UTC `2026-06-02T13:24:20Z`, local `2026-06-02 18:24:20 +05:00`: runtime `9/9 PASS`, catalog class `neutral`, accepted positive candidates `0`.
`P2144` post-sync checks completed UTC `2026-06-02T13:27:01Z`, local `2026-06-02 18:27:01 +05:00`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`.
`P2145` Package B unified triage completed UTC `2026-06-02T13:28:30Z`, local `2026-06-02 18:28:30 +05:00`: `NO_CANDIDATE`, totals positive `0`, neutral `18`, negative `0`, infra_fail `0`.
`P2146` Package B post-sync audit completed UTC `2026-06-02T13:30:21Z`, local `2026-06-02 18:30:21 +05:00`: `PASS`, text_guard/readiness/pip/artifact parse clean, freeze preserved.
`P2147` Package B closeout transition completed UTC `2026-06-02T13:33:30Z`, local `2026-06-02 18:33:30 +05:00`: decision `GO_TO_FINAL_V3_NO_GO_DECISION_PACKAGE`.
`P2148` final V3 `NO_GO` decision package completed UTC `2026-06-02T13:36:00Z`, local `2026-06-02 18:36:00 +05:00`: launch `NO_GO`, no production candidate, unfreeze blocked.
`P2149` final V3 `NO_GO` post-sync audit completed UTC `2026-06-02T13:38:45Z`, local `2026-06-02 18:38:45 +05:00`: `PASS`, V3 chain closed.
`P2150` post-V3 catalog/forward boundary completed UTC `2026-06-02T13:41:50Z`, local `2026-06-02 18:41:50 +05:00`: route selected to P2079 F1 data gate after UTC close; runtime blocked now.
`P2151` P2079 F1 data gate pre-close check completed UTC `2026-06-02T14:17:11Z`, local `2026-06-02 19:17:11 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2152` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:20:42Z`, local `2026-06-02 19:20:42 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2153` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:23:19Z`, local `2026-06-02 19:23:19 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2154` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:25:53Z`, local `2026-06-02 19:25:53 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2155` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:29:20Z`, local `2026-06-02 19:29:20 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2155` post-sync checks completed UTC `2026-06-02T14:31:36Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2156` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:33:08Z`, local `2026-06-02 19:33:08 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2156` post-sync checks completed UTC `2026-06-02T14:34:45Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2157` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:36:25Z`, local `2026-06-02 19:36:25 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2157` post-sync checks completed UTC `2026-06-02T14:39:26Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2158` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:40:30Z`, local `2026-06-02 19:40:30 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2158` post-sync checks completed UTC `2026-06-02T14:42:09Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2159` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:43:17Z`, local `2026-06-02 19:43:17 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2159` post-sync checks completed UTC `2026-06-02T14:44:57Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2160` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:46:07Z`, local `2026-06-02 19:46:07 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2160` post-sync checks completed UTC `2026-06-02T14:47:42Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2161` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:49:43Z`, local `2026-06-02 19:49:43 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2161` post-sync checks completed UTC `2026-06-02T14:51:22Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2162` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:52:28Z`, local `2026-06-02 19:52:28 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2162` post-sync checks completed UTC `2026-06-02T14:54:06Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2163` P2079 F1 UTC-close recheck completed UTC `2026-06-02T14:55:22Z`, local `2026-06-02 19:55:22 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2163` post-sync checks completed UTC `2026-06-02T14:57:02Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2164` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:00:19Z`, local `2026-06-02 20:00:19 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2164` post-sync checks completed UTC `2026-06-02T15:02:25Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2165` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:04:36Z`, local `2026-06-02 20:04:36 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2165` post-sync checks completed UTC `2026-06-02T15:06:17Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2166` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:07:32Z`, local `2026-06-02 20:07:32 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2166` post-sync checks completed UTC `2026-06-02T15:09:15Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2167` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:10:30Z`, local `2026-06-02 20:10:30 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2167` post-sync checks completed UTC `2026-06-02T15:13:14Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2168` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:15:32Z`, local `2026-06-02 20:15:32 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2168` post-sync checks completed UTC `2026-06-02T15:17:14Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2169` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:18:26Z`, local `2026-06-02 20:18:26 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2169` post-sync checks completed UTC `2026-06-02T15:20:05Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2170` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:21:20Z`, local `2026-06-02 20:21:20 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2170` post-sync checks completed UTC `2026-06-02T15:23:06Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2171` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:25:59Z`, local `2026-06-02 20:25:59 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2171` post-sync checks completed UTC `2026-06-02T15:28:26Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2172` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:29:40Z`, local `2026-06-02 20:29:40 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2172` post-sync checks completed UTC `2026-06-02T15:31:27Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2173` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:32:42Z`, local `2026-06-02 20:32:42 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2173` post-sync checks completed UTC `2026-06-02T15:34:29Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2174` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:35:32Z`, local `2026-06-02 20:35:32 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2174` post-sync checks completed UTC `2026-06-02T15:37:17Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2175` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:38:21Z`, local `2026-06-02 20:38:21 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2175` post-sync checks completed UTC `2026-06-02T15:40:09Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2176` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:41:14Z`, local `2026-06-02 20:41:14 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2176` post-sync checks completed UTC `2026-06-02T15:43:33Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2177` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:44:46Z`, local `2026-06-02 20:44:46 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2177` post-sync checks completed UTC `2026-06-02T15:46:34Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2178` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:48:06Z`, local `2026-06-02 20:48:06 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2178` post-sync checks completed UTC `2026-06-02T15:50:05Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2179` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:51:19Z`, local `2026-06-02 20:51:19 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2179` post-sync checks completed UTC `2026-06-02T15:53:04Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2180` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:54:33Z`, local `2026-06-02 20:54:33 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2180` post-sync checks completed UTC `2026-06-02T15:57:22Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2181` P2079 F1 UTC-close recheck completed UTC `2026-06-02T15:58:51Z`, local `2026-06-02 20:58:51 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2181` post-sync checks completed UTC `2026-06-02T16:01:02Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2182` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:02:18Z`, local `2026-06-02 21:02:18 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2182` post-sync checks completed UTC `2026-06-02T16:04:04Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2183` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:05:16Z`, local `2026-06-02 21:05:16 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2183` post-sync checks completed UTC `2026-06-02T16:07:05Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2184` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:08:48Z`, local `2026-06-02 21:08:48 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2184` post-sync checks completed UTC `2026-06-02T16:10:33Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2185` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:11:50Z`, local `2026-06-02 21:11:50 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2185` post-sync checks completed UTC `2026-06-02T16:13:36Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2186` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:15:30Z`, local `2026-06-02 21:15:30 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2186` post-sync checks completed UTC `2026-06-02T16:16:33Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2187` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:19:09Z`, local `2026-06-02 21:19:09 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2187` post-sync checks completed UTC `2026-06-02T16:19:42Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2188` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:22:57Z`, local `2026-06-02 21:22:57 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2188` post-sync checks completed UTC `2026-06-02T16:23:31Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2189` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:25:48Z`, local `2026-06-02 21:25:48 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2189` post-sync checks completed UTC `2026-06-02T16:26:27Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2190` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:30:21Z`, local `2026-06-02 21:30:21 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2190` post-sync checks completed UTC `2026-06-02T16:30:46Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2191` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:33:25Z`, local `2026-06-02 21:33:25 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2191` post-sync checks completed UTC `2026-06-02T16:33:50Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2192` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:36:04Z`, local `2026-06-02 21:36:04 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2192` post-sync checks completed UTC `2026-06-02T16:36:30Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2193` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:38:39Z`, local `2026-06-02 21:38:39 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2193` post-sync checks completed UTC `2026-06-02T16:39:03Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2194` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:41:09Z`, local `2026-06-02 21:41:09 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2194` post-sync checks completed UTC `2026-06-02T16:41:33Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
`P2195` P2079 F1 UTC-close recheck completed UTC `2026-06-02T16:45:02Z`, local `2026-06-02 21:45:02 +05:00`: `BLOCKED_BY_UTC_CLOSE`.
`P2195` post-sync checks completed UTC `2026-06-02T16:45:27Z`: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
Quick structural audit completed UTC `2026-06-02T18:27:15Z`, local `2026-06-02 23:27:15 +05:00`: `PASS_WITH_ROUTE_CORRECTION`.
Artifact: `reports/qa_gate/quick_structural_audit_framework_20260602T182715Z.json`.
Conclusion: P2079 UTC-close gate blocks forward/production only; structural/big-window catalog validation on already closed historical data can be opened now as a separate chain.
Current pointer: `P2195` closed as `BLOCKED_BY_UTC_CLOSE`. Next number `P2196` is blocked until `2026-06-03T00:00:00Z` / local `2026-06-03 05:00:00 +05:00`; P2079 runtime, production, and unfreeze remain blocked.
Structural big-window command-set is closed as `PASS` (`reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json`).
Structural narrow runtime is paused by explicit user stop (`reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`); do not resume unless the user explicitly asks.

Do not move to the next step until the current step has an artifact or explicit status.

## Timed Package B Chain
Rule: every step must record start date/time, completion date/time, status, artifact, and next step before advancing.

| Step | Time | Status | Action | Artifact |
|---|---|---|---|---|
| Step 1 | started UTC `2026-06-02T12:45:20Z`; completed UTC `2026-06-02T12:59:00Z`; local completed `2026-06-02 17:59:00 +05:00` | done | Inventory V3 Package A and old Package B artifacts; separate current V3 from old strict/V2 | `reports/qa_gate/p2140_v3_package_b_inventory_20260602T125900Z.json` |
| Step 2 | started UTC `2026-06-02T12:59:47Z`; completed UTC `2026-06-02T13:00:00Z`; local completed `2026-06-02 18:00:00 +05:00` | done | Define exact V3 Package B slots: B-H1/B-H2/B-H3, W1-W3, `3x3`/9 workers | `reports/qa_gate/p2141_v3_package_b_exact_slots_20260602T130000Z.json` |
| Step 3 | started UTC `2026-06-02T13:02:00Z`; completed UTC `2026-06-02T13:05:59Z`; local completed `2026-06-02 18:05:59 +05:00` | done | Emit Package B matrix slices, command set and dry-run/preflight artifact, no runtime | `reports/qa_gate/p2142_v3_package_b_command_set_20260602T130559Z.json` |
| Step 4 | started UTC `2026-06-02T13:10:35Z`; completed UTC `2026-06-02T13:15:35Z`; local completed `2026-06-02 18:15:35 +05:00` | done | Run Package B `long_only` after command set `PASS` | `reports/qa_gate/p2143_v3_package_b_long_only_summary_20260602T131035Z.json`; `reports/optuna_catalog/neutral/p2143_v3_package_b_long_only_neutral_20260602T131535Z.json` |
| Step 5 | started UTC `2026-06-02T13:20:20Z`; completed UTC `2026-06-02T13:24:20Z`; local completed `2026-06-02 18:24:20 +05:00` | done | Run Package B `short_only` after long_only artifact/status | `reports/qa_gate/p2144_v3_package_b_short_only_summary_20260602T132020Z.json`; `reports/optuna_catalog/neutral/p2144_v3_package_b_short_only_neutral_20260602T132420Z.json` |
| Step 6 | started UTC `2026-06-02T13:28:00Z`; completed UTC `2026-06-02T13:28:30Z`; local completed `2026-06-02 18:28:30 +05:00` | done | Unified Package B triage and catalog classification | `reports/qa_gate/p2145_v3_package_b_unified_triage_20260602T132830Z.json` |
| Step 7 | started UTC `2026-06-02T13:30:00Z`; completed UTC `2026-06-02T13:30:21Z`; local completed `2026-06-02 18:30:21 +05:00` | done | Package B post-sync audit and docs update | `reports/qa_gate/p2146_v3_package_b_post_sync_audit_20260602T133021Z.json` |
| Step 8 | started UTC `2026-06-02T13:33:00Z`; completed UTC `2026-06-02T13:33:30Z`; local completed `2026-06-02 18:33:30 +05:00` | done | Decide next transition after Package B closeout | `reports/qa_gate/p2147_v3_package_b_closeout_transition_20260602T133330Z.json` |

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Create project memory files | done | Keep updated after important work | Codex |
| Keep active truth synced | done | Read `P2017`, V3 TZ, global audit first | Codex |
| V3 Package A long_only | done | None | Completed `P2022` |
| V3 Package A short_only | done | None | Completed `P2023` |
| V3 Package A unified triage | done | None | Completed `P2024` |
| V3 Package A post-audit | done | None | Completed `P2025` |
| Full calibration catalog checkpoint | done | Use new TZ as active catalog overlay | `P2026` |
| Full calibration catalog post-sync audit | done | None | `P2027` |
| 1d->1d calibration smoke strategy | done | Completed through narrow/medium/wide catalog pass; no forward candidate emerged | `P2028`-`P2050` |
| Ordered execution roadmap | done | Follow this roadmap strictly as the step pointer | `P2029` |
| Step 1: wiring inventory | done | PASS; inventory artifact written | `P2030` |
| Step 2: 1d->1d smoke matrix | done | PASS; exact matrix path and long/short command set fixed | `P2032` |
| Step 3: smoke preflight | done | PASS; env/readiness/storage/matrix/output dirs checked | `P2034` |
| Step 4: long_only smoke | done | NEUTRAL_NO_TRADE; runtime OK; catalog entry written | `P2035` |
| Step 5: short_only smoke | done | PROVISIONAL_PLUS_GOAL_FAIL; runtime OK; catalog entry written | `P2036` |
| Step 6: smoke triage | done | GO_TO_MEDIUM_WORK; no accepted positive yet | `P2037` |
| Step 7: medium command set | done | PASS; exact medium long/short commands fixed | `P2039` |
| Step 7: medium work pass | done | GO_TO_WIDE_BATTLE; no accepted positive; negative entries preserved; post-sync PASS | `P2040`, `P2041`, `P2042`, `P2043` |
| Step 8: wide command set | done | PASS; exact wide long/short commands fixed | `P2044` |
| Step 8: wide battle pass | done | GO_TO_CATALOG_RANKING; no accepted positive; negative entries preserved | `P2045`, `P2046`, `P2047` |
| Step 9: catalog ranking | done | NO_FORWARD_CANDIDATE; positive=0, neutral=2, negative=4, infra_fail=0 | `P2048` |
| Step 10: forward stability | blocked | Not runnable because candidate_for_forward=0 | `P2049` |
| Step 11: production GO/unfreeze | blocked | NO_GO; requires new candidate + F1/F2 2/2 PASS + new GO package; closeout audit PASS | `P2049`, `P2050` |
| Block cycle setup | done | PASS; 6 block matrices generated and compiled | `P2051` |
| Block01 price_volatility narrow command set | done | PASS; long/short exact commands fixed | `P2052` |
| Block01 price_volatility narrow runtime | done | neutral 2/2; no accepted positive | `P2053`, `P2054`, `P2055` |
| Block01 price_volatility medium runtime | done | neutral 1, negative 1; no accepted positive | `P2056`, `P2057`, `P2058`, `P2059` |
| Block01 price_volatility wide runtime | done | negative 2/2; no accepted positive | `P2060`, `P2061`, `P2062`, `P2063` |
| Block01 price_volatility post-sync audit | done | PASS; freeze preserved | `P2064` |
| Block02 trend_momentum narrow command set | done | PASS; exact long/short commands fixed | `P2065` |
| Block02 trend_momentum narrow runtime | done | neutral 1, negative 1; no accepted positive | `P2066`, `P2067`, `P2068` |
| Block02 trend_momentum medium command set | done | PASS; exact long/short commands fixed | `P2069` |
| Block02 trend_momentum medium runtime | done | neutral 1, negative 1; no accepted positive | `P2070`, `P2071`, `P2072` |
| Block02 trend_momentum wide command set | done | PASS; exact long/short commands fixed | `P2073` |
| Block02 trend_momentum wide runtime | done | neutral 1, negative 1; no accepted positive; full triage -> block03 | `P2074`, `P2075`, `P2076` |
| Block02 trend_momentum post-sync audit | done | PASS; freeze preserved | `P2077` |
| Block03 volume_flow narrow command set | done | PASS; exact long/short commands fixed | `P2078` |
| Block03 volume_flow narrow runtime | done | positive 1, negative 1; candidate_for_forward observed | `P2079`, `P2080`, `P2081` |
| Block03 volume_flow medium command set | done | PASS; exact long/short commands fixed | `P2082` |
| Block03 volume_flow medium runtime | done | neutral 1, negative 1; narrow candidate preserved | `P2083`, `P2084`, `P2085` |
| Block03 volume_flow wide command set | done | PASS; exact long/short commands fixed | `P2086` |
| Block03 volume_flow wide runtime | done | neutral 1, negative 1; full triage -> block04 | `P2087`, `P2088`, `P2089` |
| Block03 volume_flow post-sync audit | done | PASS; freeze preserved; candidate_for_forward 1 | `P2090` |
| Block04 density_profile narrow command set | done | PASS; exact long/short commands fixed | `P2091` |
| Block04 density_profile narrow runtime | done | neutral 1, negative 1; no new candidate | `P2092`, `P2093`, `P2094` |
| Block04 density_profile medium command set | done | PASS; exact long/short commands fixed | `P2095` |
| Block04 density_profile medium runtime | done | neutral 1, negative 1; no new candidate | `P2096`, `P2097`, `P2098` |
| Block04 density_profile wide command set | done | PASS; exact long/short commands fixed | `P2099` |
| Block04 density_profile wide runtime | done | neutral 2; full triage -> block05 | `P2100`, `P2101`, `P2102` |
| Block04 density_profile post-sync audit | done | PASS; freeze preserved; block03 candidate still preserved | `P2103` |
| Block05 structure_ta narrow command set | done | PASS; exact long/short commands fixed | `P2104` |
| Block05 structure_ta narrow runtime | done | neutral 1, negative 1; no new candidate | `P2105`, `P2106`, `P2107` |
| Block05 structure_ta medium command set | done | PASS; exact long/short commands fixed | `P2108` |
| Block05 structure_ta medium runtime | done | neutral 1, negative 1; no new candidate | `P2109`, `P2110`, `P2111` |
| Block05 structure_ta wide command set | done | PASS; exact long/short commands fixed | `P2112` |
| Block05 structure_ta wide runtime | done | neutral 1, negative 1; full triage -> block06 | `P2113`, `P2114`, `P2115` |
| Block05 structure_ta post-sync audit | done | PASS; freeze preserved; block03 candidate still preserved | `P2116` |
| Block06 pattern narrow command set | done | PASS; exact long/short commands fixed | `P2117` |
| Block06 pattern narrow runtime | done | neutral 1, negative 1; no new candidate | `P2118`, `P2119`, `P2120` |
| Block06 pattern medium command set | done | PASS; exact long/short commands fixed | `P2121` |
| Block06 pattern medium runtime | done | neutral 1, negative 1; no new candidate | `P2122`, `P2123`, `P2124` |
| Block06 pattern wide command set | done | PASS; exact long/short commands fixed | `P2125` |
| Block06 pattern wide runtime | done | neutral 1, negative 1; full triage -> ranking | `P2126`, `P2127`, `P2128` |
| Block06 pattern post-sync audit | done | PASS; freeze preserved | `P2129` |
| Block-level catalog ranking | done | positive 1, neutral 18, negative 17, infra_fail 0, candidate_for_forward 1 | `P2130` |
| Block-level forward boundary | done | F1/F2 required; production/unfreeze blocked | `P2131` |
| Block-level catalog closeout post-sync audit | done | PASS; freeze preserved | `P2132` |
| Forward stability command set for P2079 | done | Commands fixed; status BLOCKED_BY_DATA; do not run production | `P2132`, `P2133` |
| P2079 F1/F2 preflight after data availability | blocked | P2134 confirms raw max day `2026-06-01`; wait for closed raw `2026-06-02` then repeat F1 preflight; wait for closed raw `2026-06-03` before F2 | `P2133`, `P2134` |
| P2079 forward data ingest route | done | Route fixed; do not ingest before UTC close; next command after `2026-06-03T00:00:00Z` is `mlbotnav.ingest_day --date 2026-06-02 --symbol SOLUSDT --timeframes 1` | `P2135` |
| P2079 post-close heartbeat | paused | Heartbeat `p2079-f1-data-gate-check` paused after previous-TZ correction; resume only after Package B closeout or explicit user redirect | `P2136`, `P2137` |
| Previous V3 TZ recovery | done | `P2137` restored current manual pointer to exact V3 Package B slot definition | User correction |
| Previous V3 TZ recovery post-sync audit | done | PASS; text_guard/readiness/pip check clean, freeze preserved | `P2138` |
| Timed Package B step chain | done | `P2139` fixed date/time chain and TZ anchor; next is Step 1 inventory | `P2139` |
| Independent audit/agent path cross-check | done | Correct with boundary: do `P2140` inventory only; do not run runtime/forward | `reports/qa_gate/p2139_independent_agent_crosscheck_20260602T125117Z.json` |
| P2140 V3 Package B inventory | done | PASS; old Package B artifacts are historical V2/strict only; current V3 Package B slots/matrices are not defined | `reports/qa_gate/p2140_v3_package_b_inventory_20260602T125900Z.json` |
| V3 Package B exact slot definition | done | PASS; B-H1/B-H2/B-H3 fixed; runtime blocked | `reports/qa_gate/p2141_v3_package_b_exact_slots_20260602T130000Z.json` |
| P2142 Package B matrix/command set | done | PASS; 4 matrix slices generated, 18 exact commands emitted, dry-run/preflight `18/18 PASS` | `reports/qa_gate/p2142_v3_package_b_command_set_20260602T130559Z.json` |
| P2143 Package B long_only runtime | done | Runtime `9/9 PASS`; catalog class `neutral`; accepted positive candidates `0`; best tradeful OOS `-1.6687%` | `reports/optuna_catalog/neutral/p2143_v3_package_b_long_only_neutral_20260602T131535Z.json` |
| P2144 Package B short_only runtime | done | Runtime `9/9 PASS`; catalog class `neutral`; accepted positive candidates `0`; best tradeful OOS `-1.6689%` | `reports/optuna_catalog/neutral/p2144_v3_package_b_short_only_neutral_20260602T132420Z.json` |
| P2145 Package B unified triage | done | `NO_CANDIDATE`; positive 0, neutral 18, negative 0, infra_fail 0; next post-sync audit | `reports/qa_gate/p2145_v3_package_b_unified_triage_20260602T132830Z.json` |
| P2146 Package B post-sync audit | done | PASS; text_guard/readiness/pip/artifact parse clean; freeze preserved | `reports/qa_gate/p2146_v3_package_b_post_sync_audit_20260602T133021Z.json` |
| P2147 Package B closeout transition | done | PASS; bounded V3 Package A and B both no-candidate; next required item is final V3 `NO_GO` decision package / closeout note | `reports/qa_gate/p2147_v3_package_b_closeout_transition_20260602T133330Z.json` |
| P2148 final V3 NO_GO decision | done | Final launch decision `NO_GO`; no production-ready candidate; launch/unfreeze blocked | `reports/qa_gate/p2148_v3_final_no_go_decision_20260602T133600Z.json` |
| P2149 final V3 NO_GO post-sync audit | done | PASS; text_guard/readiness/pip/artifact parse clean; freeze preserved; V3 chain closed | `reports/qa_gate/p2149_v3_final_no_go_post_sync_audit_20260602T133845Z.json` |
| P2150 post-V3 catalog/forward boundary | done | Route selected: P2079 F1 data gate only after UTC close; no ingest/preflight/runtime now | `reports/qa_gate/p2150_post_v3_catalog_forward_boundary_20260602T134150Z.json` |
| P2151 P2079 F1 data gate pre-close check | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2151_p2079_f1_data_gate_preclose_check_20260602T141711Z.json` |
| P2152 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2152_p2079_f1_data_gate_utc_close_recheck_20260602T142042Z.json` |
| P2153 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2153_p2079_f1_data_gate_utc_close_recheck_20260602T142319Z.json` |
| P2154 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2154_p2079_f1_data_gate_utc_close_recheck_20260602T142553Z.json` |
| P2155 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2155_p2079_f1_data_gate_utc_close_recheck_20260602T142920Z.json` |
| P2156 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2156_p2079_f1_data_gate_utc_close_recheck_20260602T143308Z.json` |
| P2157 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2157_p2079_f1_data_gate_utc_close_recheck_20260602T143625Z.json` |
| P2158 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2158_p2079_f1_data_gate_utc_close_recheck_20260602T144030Z.json` |
| P2159 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2159_p2079_f1_data_gate_utc_close_recheck_20260602T144317Z.json` |
| P2160 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2160_p2079_f1_data_gate_utc_close_recheck_20260602T144607Z.json` |
| P2161 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2161_p2079_f1_data_gate_utc_close_recheck_20260602T144943Z.json` |
| P2162 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2162_p2079_f1_data_gate_utc_close_recheck_20260602T145228Z.json` |
| P2163 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z` | `reports/qa_gate/p2163_p2079_f1_data_gate_utc_close_recheck_20260602T145522Z.json` |
| P2164 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2164_p2079_f1_data_gate_utc_close_recheck_20260602T150019Z.json` |
| P2165 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2165_p2079_f1_data_gate_utc_close_recheck_20260602T150436Z.json` |
| P2166 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2166_p2079_f1_data_gate_utc_close_recheck_20260602T150732Z.json` |
| P2167 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2167_p2079_f1_data_gate_utc_close_recheck_20260602T151030Z.json` |
| P2168 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2168_p2079_f1_data_gate_utc_close_recheck_20260602T151532Z.json` |
| P2169 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2169_p2079_f1_data_gate_utc_close_recheck_20260602T151826Z.json` |
| P2170 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2170_p2079_f1_data_gate_utc_close_recheck_20260602T152120Z.json` |
| P2171 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2171_p2079_f1_data_gate_utc_close_recheck_20260602T152559Z.json` |
| P2172 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2172_p2079_f1_data_gate_utc_close_recheck_20260602T152940Z.json` |
| P2173 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2173_p2079_f1_data_gate_utc_close_recheck_20260602T153242Z.json` |
| P2174 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2174_p2079_f1_data_gate_utc_close_recheck_20260602T153532Z.json` |
| P2175 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2175_p2079_f1_data_gate_utc_close_recheck_20260602T153821Z.json` |
| P2176 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2176_p2079_f1_data_gate_utc_close_recheck_20260602T154114Z.json` |
| P2177 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2177_p2079_f1_data_gate_utc_close_recheck_20260602T154446Z.json` |
| P2178 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2178_p2079_f1_data_gate_utc_close_recheck_20260602T154806Z.json` |
| P2179 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2179_p2079_f1_data_gate_utc_close_recheck_20260602T155119Z.json` |
| P2180 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2180_p2079_f1_data_gate_utc_close_recheck_20260602T155433Z.json` |
| P2181 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2181_p2079_f1_data_gate_utc_close_recheck_20260602T155851Z.json` |
| P2182 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2182_p2079_f1_data_gate_utc_close_recheck_20260602T160218Z.json` |
| P2183 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2183_p2079_f1_data_gate_utc_close_recheck_20260602T160516Z.json` |
| P2184 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2184_p2079_f1_data_gate_utc_close_recheck_20260602T160848Z.json` |
| P2185 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2185_p2079_f1_data_gate_utc_close_recheck_20260602T161150Z.json` |
| P2186 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2186_p2079_f1_data_gate_utc_close_recheck_20260602T161530Z.json` |
| P2187 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2187_p2079_f1_data_gate_utc_close_recheck_20260602T161909Z.json` |
| P2188 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2188_p2079_f1_data_gate_utc_close_recheck_20260602T162257Z.json` |
| P2189 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2189_p2079_f1_data_gate_utc_close_recheck_20260602T162548Z.json` |
| P2190 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2190_p2079_f1_data_gate_utc_close_recheck_20260602T163021Z.json` |
| P2191 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2191_p2079_f1_data_gate_utc_close_recheck_20260602T163325Z.json` |
| P2192 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2192_p2079_f1_data_gate_utc_close_recheck_20260602T163604Z.json` |
| P2193 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2193_p2079_f1_data_gate_utc_close_recheck_20260602T163839Z.json` |
| P2194 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2194_p2079_f1_data_gate_utc_close_recheck_20260602T164109Z.json` |
| P2195 P2079 F1 UTC-close recheck | done | BLOCKED_BY_UTC_CLOSE; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`; checks PASS | `reports/qa_gate/p2195_p2079_f1_data_gate_utc_close_recheck_20260602T164502Z.json` |
| P2196 P2079 F1 data gate after UTC close | blocked | After `2026-06-03T00:00:00Z`, verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only | `P2195` |
| Structural big-window catalog command set | done | PASS; compile/dry-run `36/36`; raw policy preflight PASS | `reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json` |
| Structural big-window narrow runtime | paused_by_user | Stop requested; do not resume unless explicitly asked; freeze restored | `reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json` |

## User-Dependent
1. User fixed the first task as a 1d calibration -> next 1d apply smoke/proof contour before broader Package B/catalog execution.
2. User requested the path to be written and fixed step by step so we do not drift.
3. User must explicitly approve destructive deletes, cleanup, or moving artifacts.
4. User can choose how aggressive the full catalog pass should be after the first smoke/proof contour.
5. User corrected the path: restore previous V3 TZ step before further forward work.

## External Dependencies
1. Market/candle data availability for closed windows.
2. Optuna storage configuration and local runtime environment.

## Hard Structural Audit Pointer
Completed UTC `2026-06-02T19:16:09Z`, local `2026-06-03 00:16:09 +05:00`.
Artifact: `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md`.
Status: `PASS_WITH_FINDINGS`.
Next required decision: choose Policy A mixed semantics or Policy B strict block purity. Recommended Policy B: filter hypothesis/trend-filter rows by active-block required columns before big-window battle calibration.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Hard structural audit of features/hypotheses/grids | done | Use as current structural reference before new TZ | `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md` |
| Block purity policy decision | next | Recommended: enforce strict block purity, regenerate command set, then run big-window dry-run | `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md` |

## P2196A Current Battle Route
Completed UTC `2026-06-03T06:09:19Z`, local `2026-06-03 11:09:19 +05:00`.
Artifact: `reports/qa_gate/p2196a_optuna_battle_readiness_audit_20260603T060919Z.md`.
Status: `NO_GO_FOR_PRODUCTION / GO_TO_STRICT_BLOCK_PURITY_FIX_BEFORE_BATTLE`.
Next numbered task: `P2196B` strict block-purity compatibility map and filtering.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| P2196A Optuna battle readiness audit | done | Use as current route decision | `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md` |
| P2196B Strict block-purity compatibility | done | `PASS_STRICT_FILTERING`; trend_filter required columns must fit primary block + context; `none` always allowed | `reports/qa_gate/p2196b_strict_hypothesis_filter_full_audit_20260603T100404Z.json` |
| P2196C Strict command-set regeneration | done | Rebuilt strict battle command-set; dry-run `36/36 PASS` | `reports/optuna_catalog/index/p2196c_strict_command_set_20260603T100504Z.json` |
| P2196D Strict P2079-equivalent check | done | Runtime `OK`; block03 volume_flow narrow long_only best OOS `+1.5266529420731034%`, `1` trade; saved as TOP_EXPERIMENTAL because train gate failed | `reports/adaptive/long_only_pool_20260603t101450z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T101454Z.json` |
| P2196E Strict battle calibration | in_progress | volume_flow narrow long/short checked; continue runtime calibration sequence; store best positive/negative/neutral/infra_fail per run | `reports/adaptive/short_only_pool_20260603t102158z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T102202Z.json` |
| P2196F Strict catalog ranking | pending | Rank candidates; positive only goes to forward queue | `P2196E` |
| P2196G Forward data gate | pending | Ingest/verify closed data and run F1/F2 preflights before any forward runtime | `P2196F` |
| P2196H Production decision | pending | Only after F1/F2 2/2 PASS and a new GO package | `P2196G` |

## P2196B Substep: Volume/Volatility Context Wiring
Completed UTC `2026-06-03T06:58:21Z`, local `2026-06-03 11:58:21 +05:00`.
Artifact: `reports/qa_gate/p2196b_volume_context_wiring_audit_20260603T065821Z.json`.
Status: `PASS_CONTEXT_WIRING`.
Done: `volume_flow` and `price_volatility` are always-on context blocks in full/catalog matrices; compile/runtime/profile/report path is wired; unit tests `69/69 OK`; 7-matrix compile audit `PASS`.
Post-sync checks: text_guard `PASS`, readiness freeze preserved, `pip check PASS`.
Next action remains inside `P2196B`: implement strict hypothesis/trend compatibility filtering before any battle runtime.

## P2196B/P2196C Strict Readiness Update
Completed UTC `2026-06-03T10:05:59Z`, local `2026-06-03 15:05:59 +05:00`.
P2196B strict filtering artifact: `reports/qa_gate/p2196b_strict_hypothesis_filter_full_audit_20260603T100404Z.json`, status `PASS`, compile rows `42/42 PASS`.
P2196C dry-run artifact: `reports/optuna_catalog/index/p2196c_strict_command_set_20260603T100504Z.json`, status `PASS`, rows `36/36 PASS`.
Raw preflight artifact: `reports/qa_gate/preflight_window_20260603T100432Z.json`, status `PASS`.
Post-sync health checks 2026-06-03T10:08:56Z: text_guard `PASS`, readiness freeze preserved, `pip check PASS`.
Next action: `P2196D` strict P2079-equivalent check, no production/unfreeze.

## P2196D Strict Runtime Calibration Start
Completed UTC `2026-06-03T10:14:50Z`, local `2026-06-03 15:14:50 +05:00`.
Status: `PASS_RUNTIME_OK / EXPERIMENTAL_POSITIVE`.
Result: block03 `volume_flow`, grid `narrow`, mode `long_only`, 3x3/9 workers, best OOS `+1.5266529420731034%`, OOS trades `1`, goal `1.0%` passed by `w2/w3`.
Best summary: `reports/adaptive/long_only_pool_20260603t101450z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T101454Z.json`.
Top experimental card: `reports/top_strategy/long_only_pool_20260603t101450z_w3/top_SOLUSDT_1m_2026-06-01_20260603T101522Z_MODE-LONG_ONLY_TF-1M_RET-+1.5267pct/top_strategy_card.json`.
Boundary: train gate did not pass; no production/latest publication.
Next action: `P2196E` continue strict calibration sequence.

## P2196E Volume Flow Narrow Short Runtime
Completed UTC `2026-06-03T10:21:58Z`, local `2026-06-03 15:21:58 +05:00`.
Status: `PASS_RUNTIME_OK / NO_CANDIDATE`.
Result: first short attempt exposed a worker crash on empty/unreadable search report JSON; fixed in `src/mlbotnav/adaptive_auto_train.py`; focused tests `83/83 OK`; rerun launcher `OK`, all 3 workers exit `0`, best OOS `0%`, trades `0`.
Best summary: `reports/adaptive/short_only_pool_20260603t102158z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T102202Z.json`.
Next action: continue strict battle calibration from the next runtime grid/profile.

## Calibration Current H006 Pattern Replay
Completed UTC `2026-06-04T11:00:12Z`, local `2026-06-04 16:00:12 +05:00`.
Status: `done`.
Result: H006 `pattern` replay after params/retry fix completed `long_only` and `short_only` across `narrow/medium/wide`; launchers `6/6 OK`; final params present `6/6`; worker crash `0`; positive candidate `0`.
Readable report: `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| H006 pattern params/retry fix | done | Keep fix; do not use old pattern closeout for selected params | `src/mlbotnav/adaptive_auto_train.py` |
| H006 pattern replay | done | Use new replay artifact as current H006 result | `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z.json` |
| Health-check after H006 replay | done | `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260604T110352Z.json` | H006 replay |
| Next calibration block/slot | pending | Move only by active current plan, not old chronology/session journals | Health-check |

## H006 Grid Edge Coverage Audit Fix
Completed UTC `2026-06-04T11:15:52Z`, local `2026-06-04 16:15:52 +05:00`.
Status: `done`.
Result: Optuna now writes `grid_edge_coverage_audit_*.json` and records sampled params/forced min-max edges before prune, so pruned edge trials are visible.
Readable report: `reports/qa_gate/h006_grid_edge_coverage_audit_fix_20260604T111552Z_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add edge coverage audit artifact | done | Use `grid_edge_coverage_audit_path` in search reports | `src/mlbotnav/optuna_search_candidate.py` |
| Runtime smoke for edge audit | done | H006 `long_only narrow`, `2x6`, launcher `OK` | `reports/optuna/long_only/grid_edge_coverage_audit_20260604T111552Z.json` |
| Full-budget proof with new audit | pending | Rerun selected full block/grid and verify profile/core coverage pass/fail by artifact | Edge audit fix |
| Cascade candidate improvement | pending | Implement/describe `wide -> medium around best -> narrow around best`, LONG/SHORT separately | Full-budget proof or direct implementation decision |

## H006 Core Grid Edge Forcing Fix
Completed UTC `2026-06-04T11:31:02Z`, local `2026-06-04 16:31:02 +05:00`.
Status: `done`.
Result: core parameters now have forced min/max and audit visibility; smoke audit core coverage `5/5 PASS`.
Readable report: `reports/qa_gate/h006_core_grid_edge_forcing_fix_20260604T113102Z_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Force core min/max | done | Keep `core_forced_edges` in audit | `src/mlbotnav/optuna_search_candidate.py` |
| Runtime smoke for core edge forcing | done | H006 `long_only narrow`, `2x6`, launcher `OK`, core coverage `5/5 PASS` | `reports/optuna/long_only/grid_edge_coverage_audit_20260604T113102Z.json` |
| Full-budget profile proof | next | Rerun full selected block and confirm profile/core coverage from `grid_edge_coverage_audit` | Core edge forcing |
| Cascade candidate improvement | pending | Implement/describe `wide -> medium around best -> narrow around best`, LONG/SHORT separately | Full-budget profile proof |

## H006 Full Replay Edge Coverage Pass
Completed UTC `2026-06-04T12:39:58Z`, local `2026-06-04 17:39:58 +05:00`.
Status: `done`.
Result: H006 `pattern` full replay completed LONG/SHORT x `narrow/medium/wide`; all launchers `OK`; profile coverage `18/18`; core coverage `5/5`; no positive trading candidate.
Readable report: `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Full-budget profile proof | done | Use H006 final replay artifact as proof for min/max сетки | `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z.json` |
| H006 production candidate | done | No positive trading candidate; do not publish to production | H006 replay |
| Cascade candidate improvement | next | Implement/describe `wide -> medium around best -> narrow around best`, LONG/SHORT separately | H006 replay proof |

## CASCADE_BLOCK_CALIBRATION Rule
Completed UTC `2026-06-04T14:17:45Z`, local `2026-06-04 19:17:45 +05:00`.
Status: `fixed in active TZ/status docs`.
Result: target calibration mode is fixed as `CASCADE_BLOCK_CALIBRATION`: block-by-block, LONG/SHORT separate, `wide -> best tradeful -> medium around best -> best tradeful -> narrow around best`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Fix cascade rule in active TZ | done | Use this rule as source of truth for next implementation/run planning | `docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md` |
| Fix cascade rule in current status | done | Continue from this status, not old chronology | `docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md` |
| Implement cascade runner | next | Build/run no-code plan first if requested; then implement `wide -> medium -> narrow` around tradeful best | Cascade rule |

## C001 Block 01 Cascade Start Plan
Completed UTC `2026-06-04T14:41:47Z`, local `2026-06-04 19:41:47 +05:00`.
Status: `plan fixed before runtime`.
Result: next runtime target is `C001 price_volatility LONG wide` using `CASCADE_BLOCK_CALIBRATION`. `medium/narrow` must not run until the best `tradeful` `wide` candidate is selected.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Identify first cascade block | done | Use `catalog_block_01_price_volatility.yaml` | Active current docs |
| Fix first runtime command | done | Run `C001 LONG wide` | Command in `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md` |
| Analyze C001 LONG wide logs | next | Check workers, coverage, best tradeful candidate | C001 LONG wide runtime |

## C001 Block 01 LONG Wide Runtime
Completed UTC `2026-06-04T14:44:29Z`, local `2026-06-04 19:44:29 +05:00`.
Status: `done / tradeful negative`.
Result: launcher `OK`, workers `3/3`, best OOS `-37.0372%`, trades `9`, best wide params captured.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Run C001 LONG wide | done | Use readable report as current result | `reports/qa_gate/c001_block01_price_volatility_long_wide_20260604T144429Z_RU.md` |
| Check edge coverage | done_with_note | Core `5/5`; profile mixed because one report `5/5`, another `2/5`; note artifact collision | C001 LONG wide reports |
| C001 LONG medium around best | next | Build actual narrowed medium around wide params; do not run blind medium | Best wide params |

## Instrument Knobs Audit TZ
Completed UTC `2026-06-11T10:47:35Z`, local `2026-06-11 15:47:35 +05:00`.
Status: `new active read-only audit`.
Result: created `docs/CALIBRATION_NODE_CURRENT/TZ_INSTRUMENT_KNOBS_AUDIT_2026-06-11_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Create instrument knobs audit TZ | done | Use as active audit plan | User clarification |
| Pause C001 medium runtime | done | Do not run until audit is complete and agreed | Instrument audit |
| Block 01 knobs audit | next | Write Block 01 mini-TZ and classify all price/volatility knobs | New TZ |

## Block 01 Price Volatility Knobs Audit
Completed UTC `2026-06-11T10:51:00Z`, local `2026-06-11 15:51:00 +05:00`.
Status: `draft fixed`.
Result: created `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Write Block 01 mini-TZ | done | Use document as Block 01 source for knob decisions | Instrument audit TZ |
| Classify current Block 01 params | done | Current knobs are calculation windows: `return_lookback`, `rolling_window`, `period_standard` | Matrix/code audit |
| Identify missing signal-level knobs | done | Agree whether to add ret thresholds, hl_spread thresholds, volatility regime, ATR/risk knobs | User decision |
| Move to Block 02 | pending | Only after Block 01 knobs are fixed/agreed | Block 01 decision |

Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T105438Z.json`.

## Block 01 Live Chart Example
Completed UTC `2026-06-11T11:02:00Z`, local `2026-06-11 16:02:00 +05:00`.
Status: `done / visual audit example`.
Result: generated readable visual artifacts for Block 01 on real SOLUSDT 1m data.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Render Block 01 chart | done | Use PNG/MD/JSON as visual basis for knob agreement | Block 01 mini-TZ |
| Explain concrete actions | done | Actions shown: `LONG_ALLOWED`, `SHORT_ALLOWED`, `NO_TRADE_LOW_VOL`, `NO_TRADE_HIGH_RISK` | Visual thresholds |
| Agree production thresholds | pending | Decide which signal-level knobs become real config params | User decision |

Artifacts:
1. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.png`
2. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z_RU.md`
3. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.json`

Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T113003Z.json`.

## Block 01 Short Rework Visual
Completed UTC `2026-06-11T11:34:00Z`, local `2026-06-11 16:34:00 +05:00`.
Status: `done / visual audit example`.
Result: generated SHORT-specific visual explaining why local `ret_1 > 0` can be a pullback, not LONG.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Render SHORT rework chart | done | Use it to agree Block 01 SHORT knobs | User observation |
| Document `SHORT_AFTER_PULLBACK` | done | Decide whether to add knobs to config | Block 01 agreement |
| Document `SHORT_MOMENTUM` | done | Decide whether direct short momentum is separate profile | Block 01 agreement |

Artifacts:
1. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.png`
2. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z_RU.md`
3. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.json`

## Block 01 Parameter Range Map
Completed UTC `2026-06-11T11:48:00Z`, local `2026-06-11 16:48:00 +05:00`.
Status: `draft fixed`.
Result: added range map to `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Define calculation ranges | done | Keep existing matrix ranges for `return_lookback`, `rolling_window`, `period_standard` | Current matrix |
| Define context/pullback/confirm ranges | done | Agree whether these become config params | Block 01 agreement |
| Define activity/risk ranges | done | Agree vol/ATR/HL constraints before implementation | Block 01 agreement |
| Move to implementation or Block 02 | pending | User decision: implement Block 01 knobs or continue audit to Block 02 | Range map |

Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T120336Z.json`.

## New Chat Handoff
Completed UTC `2026-06-19T00:00:00Z`, local `2026-06-19 05:00:00 +05:00`.
Status: `done`.
Result: created `docs/CALIBRATION_NODE_CURRENT/HANDOFF_TO_NEW_CHAT_2026-06-19_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Prepare clean handoff for new chat | done | Start new chat from handoff | Current chat too large |
| Preserve active source of truth | done | New chat reads `docs/CALIBRATION_NODE_CURRENT` only | Handoff |
| Continue block audit | pending | Decide Block 01 `AGREED/READY_FOR_CODE` or move to Block 02 after final clarification | User decision |

Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260619T184109Z.json`.

## F001 Strict Passport Runtime Connected
Completed UTC `2026-06-22T09:13:32Z`, local `2026-06-22 14:13:32 +05:00`.
Status: `done`.
Result: applied the user strict F001 passport to calibration/runtime.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Replace F001 passport with strict version | done | Use as active F001 source | User passport |
| Add `F001_move` and `F001_thr_pct` profiles | done | Run matrix compile / Optuna when approved | F001 passport |
| Compute `F001_RET1_ALLOW` runtime action | done | Use as OOF/backtest gate | Dataset runtime |
| Preserve runtime action in OOF | done | Keep model feature list unchanged | Validation/Optuna |
| Apply F001 gate in backtest | done | Run F001/H001 or Block 01 when user confirms | Backtest runtime |
| Continue strict passport list | pending | Next passport is `F002 ret_3` after user decision | F001 confirmation |

Validation: `py_compile PASS`; focused tests `25/25 OK`; Optuna runtime tests `65/65 OK`; matrix compile check PASS; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T091458Z.json`.

## F001 Strict LONG 1d/1d Runtime
Completed UTC `2026-06-22T09:20:20Z`, local `2026-06-22 14:20:20 +05:00`.
Status: `done / goal_fail`.
Result: F001 strict LONG was calibrated on `2026-05-31` and tested on `2026-06-01`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Fix OOS runtime-action bridge | done | Keep `RUNTIME_ACTION_COLUMNS` in OOS evaluator | F001 gate inactive finding |
| Validate bridge | done | `84 tests OK` | Code fix |
| Run F001 LONG 1d/1d | done | Record result as `NO_GO` for this window | User request |
| Decide next route | pending | Run SHORT separately or move to `F002 ret_3` | User decision |

Artifact: `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`.

## F001 Strict LONG Trade Map
Completed UTC `2026-06-22T09:20:20Z`, local `2026-06-22 14:20:20 +05:00`.
Status: `done`.
Result: generated trade-map PNG for best F001 LONG OOS worker.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Show entries on chart | done | Use PNG for visual review | F001 LONG OOS |
| Show TP/SL percent levels | done | TP `+1.20%`, SL `-0.80%` shown per trade | OOS risk policy |
| Explain exits | done | All exits are `timeout`, no TP/SL hit | OOS trade CSV |

Artifact: `reports/qa_gate/f001_strict_long_1d1d_trade_map_20260622T092020Z.png`.

## F001 Strict LONG No-Timeout Runtime
Completed UTC `2026-06-22T09:37:02Z`, local `2026-06-22 14:37:02 +05:00`.
Status: `done / no_go`.
Result: timeout exit was disabled as an explicit switch and F001 strict LONG was rerun on the same 1d/1d window.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add timeout disable switch | done | Use `-DisableTimeoutExit` only when no time-based exit is intended | User request |
| Propagate switch through search/train/OOS | done | Keep risk policy flag `timeout_exit_enabled=false` in reports | Runtime entrypoints |
| Validate timeout-off behavior | done | Test expects `end_of_data` if TP/SL do not hit | Backtest test |
| Run F001 LONG without timeout | done | Record result as `NO_GO` for this window | F001 strict passport |
| Decide next route | pending | Run SHORT separately or move to `F002 ret_3` | User decision |

Artifacts:
1. `reports/qa_gate/f001_strict_long_no_timeout_1d1d_20260622T093702Z_RU.md`
2. `reports/qa_gate/f001_strict_long_no_timeout_trade_map_20260622T093702Z.png`

Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T094448Z.json`.

## F001 Exit Baseline Decision
Completed UTC `2026-06-22`, local `2026-06-22 +05:00`.
Status: `done`.
Result: user chose to keep the active calibration baseline with timeout exits enabled.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Decide timeout baseline | done | Run future baseline commands without `-DisableTimeoutExit` | User decision |
| Treat no-timeout run | done | Keep as diagnostic artifact, not baseline comparison | F001 no-timeout result |
| Continue passport route | pending | Use TP/SL/timeout while thinking separately about future exit passports | User decision |

## Action Passport Calibration Rule
Completed UTC `2026-06-22`, local `2026-06-22 +05:00`.
Status: `done`.
Result: created the new passport-first calibration rule and first clean F001 passport-action matrix.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Freeze old calibration proposals as legacy | done | Do not delete; use only as migration reference | User correction |
| Add action passport registry | done | Keep active passports in `configs/calibration_action_passports.yaml` | Passport rule |
| Add F001 passport-action matrix | done | Use it for next F001 baseline run | F001 passport |
| Add compile guard for passport params | done | Reject params outside passport allowlist | `passport_mode` |
| Validate guard | done | Keep test coverage before expanding to F002 | Tests |
| Create F002 passport | pending | Do before any F002 calibration | Strict list route |
| Create exit/dynamic-exit passports | pending | Do before calibrating sell/exit logic | Separate exit layer |

Artifacts:
1. `docs/CALIBRATION_NODE_CURRENT/TZ_ACTION_PASSPORT_CALIBRATION_2026-06-22_RU.md`
2. `configs/calibration_action_passports.yaml`
3. `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`

Validation: `py_compile PASS`; focused tests `78/78 OK`; YAML parse PASS; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T101720Z.json`.

## F001 Passport-Action LONG Runtime
Completed UTC `2026-06-22T10:19:53Z`, local `2026-06-22 15:19:53 +05:00`.
Status: `done / no_go`.
Result: ran clean F001 passport-action matrix in LONG baseline with timeout exit on.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Compile F001 passport-action matrix | done | Keep compiled profiles limited to F001 params | Passport matrix |
| Run LONG baseline | done | Record result as `NO_GO` | User request |
| Separate formal best from tradeful best | done | Do not treat `0 trades / 0%` as candidate | Result triage |
| Decide core runtime purity | pending | Create runtime/backtest subpassport or rerun with fixed single-value grids | Core fields still sampled |
| Continue strict passport route | pending | Create F002 passport before any F002 calibration | User direction |

Artifact: `reports/qa_gate/f001_passport_action_long_1d1d_20260622T101953Z_RU.md`.

Validation: `py_compile PASS`; focused tests `78/78 OK`; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T102340Z.json`.

## Block Passport Registry
Completed UTC `2026-06-22`, local `2026-06-22 +05:00`.
Status: `done`.
Result: converted `configs/calibration_action_passports.yaml` into the single block/passport registry and connected registry-match guard.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Make one passport registry | done | Add all future passports under `blocks.Bxxx` | User decision |
| Add Russian block names | done | Keep `name_ru` for every block | Registry |
| Put F001 under B001 | done | Use `blocks.B001.active_passports.F001` | F001 passport |
| Keep F002 planned | done | Create passport before calibration | Strict route |
| Add registry-match guard | done | Reject matrix/registry mismatch at compile | `optuna_space.py` |
| Continue cleanup | pending | Add PassportModeRequired launcher/OOS/core-runtime subpassport | Audit findings |

Validation: `py_compile PASS`; focused tests `79/79 OK`; env override compile PASS.

## RET_N F001-F005 Strict Passport Family
Completed UTC `2026-06-22T11:21:35Z`, local `2026-06-22 16:21:35 +05:00`.
Status: `done / ready_for_next_passport_run`.
Result: connected user-provided RET_N passports F001-F005 into B001 registry, matrices, runtime actions, and backtest gate.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import RET_N family passport into project docs | done | Use project copy as source for F002-F005 | User file |
| Promote F002-F005 from planned to active B001 passports | done | Keep one matrix per action | Registry |
| Add F002-F005 passport matrices | done | Use strict allowlist profiles only | Passport mode |
| Add runtime action columns | done | Preserve only present action outputs in OOF/OOS | Dataset/runtime bridge |
| Generalize backtest entry gate | done | Report `entry_action_gate_columns` | Backtest |
| Decide F003 max anchor | done | `F003_thr_pct` now includes `1.20` | F003 min/max/step mismatch |
| Run next strict calibration | pending | Start with F002 by list order | User decision |

Validation: `py_compile PASS`; focused tests `96/96 OK`; F001-F005 matrix compile PASS; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T112135Z.json`.

Max-anchor follow-up validation: `py_compile PASS`; focused tests `98/98 OK`; F003 matrix compile proof `60 0.03 [1.17, 1.19, 1.2] True`.

## B001 RET_N Ladder Tournament
Completed UTC `2026-06-22T11:59:30Z`, local `2026-06-22 16:59:30 +05:00`.
Status: `done / ready_for_full_run`.
Result: implemented the B001 RET_N tournament generator and runner, then validated one real APTuna smoke.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add B001 tournament registry passport | done | Keep as block-level selector passport | B001 RET_N family |
| Support subset allowlist policy | done | Use only for tournament subset matrices | `optuna_space.py` |
| Generate 31 combo matrices | done | Use manifest for full run | Generator |
| Add tournament runner | done | Run full 31-combo LONG when ready | APTuna process pool |
| Validate runner with DryRun | done | Artifact written | Runner |
| Validate runner with one real combo smoke | done | Smoke is not baseline candidate | APTuna |
| Full LONG tournament | pending | Run 31 combos with production budget | User/runtime decision |
| SHORT tournament | pending | Run separately after LONG or on request | Separate mode |

Artifacts:
1. `reports/qa_gate/b001_ret_n_ladder_matrices_20260622T115638Z/manifest.json`.
2. `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115811Z.json`.
3. `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115930Z.json`.

Validation: `py_compile PASS`; focused tests `35/35 OK`; extended focused tests `83/83 OK`.

## B001 Solo Selection Decision
Completed UTC `2026-06-22`, local `2026-06-22 +05:00`.
Status: `done / baseline_changed`.
Result: disabled expanded 31-combo B001 tournament as baseline; keep it diagnostic-only.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Review 31-combo LONG result | done | Treat `F002+F004` as `NO_CANDIDATE` | Full tournament report |
| Disable combination baseline | done | Use solo F001-F005 only | User decision |
| Guard accidental 31-combo run | done | Require `-EnableCombinationTournament` for diagnostic combos | Runner |
| Fix markdown metric fields | done | Read `oos_net_return_pct`/`oos_trades` | Runner report |
| Run B001 solo selection | pending | Run default runner over indexes 1..5 with production budget | Next step |

Validation: default dry-run selected `5` solo rows; `EndIndex=31` blocked without diagnostic switch; `py_compile PASS`; focused tests `35/35 OK`.

## F008 ATR14 Passport Run
Completed UTC `2026-06-22T13:59:47Z`, local `2026-06-22 18:59:47 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B004/F008 atr14_1m` as a solo passport action in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import F008 passport into project docs | done | Use project copy as source | User file |
| Add F008 registry/matrix/runtime/backtest gate | done | Keep `F008_cmp`, `F008_thr_pct` as only action params | Passport mode |
| Run LONG | done | Record as `NO_GO` | F008 matrix |
| Run SHORT | done | Record as `NO_GO` | F008 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/f008_atr14_long_short_audit_20260622T135947Z.json`.

Validation: matrix compile `PASS`; focused tests `39/39 OK`; py_compile `PASS`.

## EMA F009-F011 Passport Run
Completed UTC `2026-06-22T14:34:20Z`, local `2026-06-22 19:34:20 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B005/EMA F009-F011` as separate solo passport actions in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import EMA family passport into project docs | done | Use project copy as source | User file |
| Add F009-F011 registry/matrices/runtime/backtest gate | done | Keep each passport isolated | Passport mode |
| Run F009 LONG/SHORT | done | Record as `NO_GO` | F009 matrix |
| Run F010 LONG/SHORT | done | Record as `NO_GO` | F010 matrix |
| Run F011 LONG/SHORT | done | Record as `NO_GO` | F011 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/ema_f009_f011_long_short_audit_20260622T143420Z.json`.

Validation: matrix compile `PASS`; focused tests `41/41 OK`; py_compile `PASS`.

## F012 RSI14 Passport Run
Completed UTC `2026-06-22T14:47:50Z`, local `2026-06-22 19:47:50 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B006/F012 rsi14_1m` as a solo passport action in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import F012 passport into project docs | done | Use project copy as source | User file |
| Add F012 registry/matrix/runtime/backtest gate | done | Keep F012 params as only action params | Passport mode |
| Run LONG | done | Record as `NO_GO` / zero trades | F012 matrix |
| Run SHORT | done | Record as `NO_GO` / negative | F012 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/f012_rsi14_combined_long_short_audit_20260622T144750Z.json`.

Validation: matrix compile `PASS`; focused tests `43/43 OK`; py_compile `PASS`; `text_guard PASS`.

## MACD F013-F015 Passport Run
Completed UTC `2026-06-22T15:19:54Z`, local `2026-06-22 20:19:54 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B007/MACD F013-F015` as separate solo passport actions in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import MACD family passport into project docs | done | Use project copy as source | User file |
| Add F013-F015 registry/matrices/runtime/backtest gate | done | Keep each passport isolated | Passport mode |
| Fix Optuna cross-passport study reuse | done | Keep `space_signature` in `run_signature` | Audit finding |
| Rerun clean F013-F015 LONG/SHORT | done | Record as `NO_GO` | Fix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/macd_f013_f015_long_short_audit_20260622T151954Z.json`.

Validation: matrix compile `PASS`; focused tests `112/112 OK`; py_compile `PASS`; selected params isolation `PASS`; `text_guard PASS`.

## F016 ADX14 Passport Run
Completed UTC `2026-06-22T15:34:03Z`, local `2026-06-22 20:34:03 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B008/F016 adx14_1m` as a solo passport action in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import F016 passport into project docs | done | Use project copy as source | User file |
| Add F016 registry/matrix/runtime/backtest gate | done | Keep `F016_cmp`, `F016_level` as only action params | Passport mode |
| Run LONG | done | Record as `NO_GO` / negative | F016 matrix |
| Run SHORT | done | Record as `NO_GO` / negative | F016 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/f016_adx14_long_short_audit_20260622T153403Z.json`.

Validation: matrix compile `PASS`; focused tests `114/114 OK`; py_compile `PASS`.

## STOCH F017-F018 Passport Run
Completed UTC `2026-06-22T15:43:40Z`, local `2026-06-22 20:43:40 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B009/F017_F018 stochastic_14_1m` as a combined solo passport action in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import STOCH passport into project docs | done | Use project copy as source | User file |
| Add F017_F018 registry/matrix/runtime/backtest gate | done | Keep `F017_F018_*` as only action params | Passport mode |
| Run LONG | done | Record as `NO_GO` / negative | F017_F018 matrix |
| Run SHORT | done | Record as `NO_GO` / negative | F017_F018 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/stoch_f017_f018_long_short_audit_20260622T154340Z.json`.

Validation: matrix compile `PASS`; focused tests `116/116 OK`; py_compile `PASS`.

## VOLUME F019-F021 Passport Run
Completed UTC `2026-06-22T16:02:07Z`, local `2026-06-22 21:02:07 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B010/VOLUME F019-F021` as separate solo passport actions in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import VOLUME passport into project docs | done | Use project copy as source | User file |
| Add F019-F021 registry/matrices/runtime/backtest gates | done | Keep each passport isolated | Passport mode |
| Fix F021 TRUE_DELTA missing side-volume fallback | done | Use post-fix F021 runs only | Audit finding |
| Run F019 LONG/SHORT | done | Record as `NO_GO` | F019 matrix |
| Run F020 LONG/SHORT | done | Record as `NO_GO` | F020 matrix |
| Run F021 LONG/SHORT post-fix | done | Record as `NO_GO` | F021 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/volume_f019_f021_long_short_audit_20260622T160207Z.json`.

Validation: matrix compile `PASS`; focused tests `118/118 OK`; py_compile `PASS`.

## F022 OBV Slope 5 Passport Run
Completed UTC `2026-06-22T16:23:56Z`, local `2026-06-22 21:23:56 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B011/F022 obv_slope_5_1m` as a solo passport action in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import F022 passport into project docs | done | Use project copy as source | User file |
| Add F022 registry/matrix/runtime/backtest gate | done | Keep `F022_slope_dir`, `F022_slope_thr` as only action params | Passport mode |
| Run LONG | done | Record as `NO_GO` / zero trades | F022 matrix |
| Run SHORT | done | Record as `NO_GO` / negative | F022 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/f022_obv_slope5_long_short_audit_20260622T162356Z.json`.

Validation: matrix compile `PASS`; focused tests `120/120 OK`; py_compile `PASS`.

## F023 MFI14 Passport Run
Completed UTC `2026-06-22T16:38:09Z`, local `2026-06-22 21:38:09 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B012/F023 mfi14_1m` as a combined solo passport action in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import F023 passport into project docs | done | Use project copy as source | User file |
| Add F023 registry/matrix/runtime/backtest gate | done | Keep `F023_*` as only action params | Passport mode |
| Run LONG | done | Record as `NO_GO` / negative | F023 matrix |
| Run SHORT | done | Record as `NO_GO` / negative | F023 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/f023_mfi14_long_short_audit_20260622T163809Z.json`.

Validation: matrix compile `PASS`; focused tests `122/122 OK`; py_compile `PASS`.

## DENSITY/VPOC Block A Passport Run
Completed UTC `2026-06-22T16:58:12Z`, local `2026-06-22 21:58:12 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B013/DENSITY_A_VPOC_CORE` Block A only: F025, F029, F033, F034.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import DENSITY/VPOC passport into project docs | done | Use project copy as source | User file |
| Add Block A registry/matrices/runtime/backtest gates | done | Keep each passport isolated | Passport mode |
| Run F025 LONG/SHORT | done | Record as `NO_GO` | F025 matrix |
| Run F029 LONG/SHORT | done | Record as `NO_GO` | F029 matrix |
| Run F033 LONG/SHORT | done | Record as `NO_GO` | F033 matrix |
| Run F034 LONG/SHORT | done | Record as `NO_GO` | F034 matrix |
| Continue same passport route | pending | Implement/run Block B F026/F027/F030/F031, then Block C F028/F032 | User direction |

Artifact: `reports/qa_gate/density_vpoc_block_a_f025_f029_f033_f034_audit_20260622T165812Z.json`.

Validation: matrix compile `PASS`; focused tests `124/124 OK`; py_compile `PASS`.

## LEVEL/RANGE/CHANNEL Block A Passport Run
Completed UTC `2026-06-22T17:15:00Z`, local `2026-06-22 22:15:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B014/LEVEL_A` Block A only: F035, F036, F037.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import LEVEL/RANGE/CHANNEL passport into project docs | done | Use project copy as source | User file |
| Add Block A registry/matrices/runtime/backtest gates | done | Keep each passport isolated | Passport mode |
| Run F035 LONG/SHORT | done | Record as `NO_GO` | F035 matrix |
| Run F036 LONG/SHORT | done | Record as `NO_GO` | F036 matrix |
| Run F037 LONG/SHORT | done | Record as `NO_GO` | F037 matrix |
| Continue same passport route | pending | Implement/run Block B F038, then Block C F039 | Passport order |

Artifact: `reports/qa_gate/level_range_channel_block_a_f035_f036_f037_audit_20260622T171500Z.json`.

Validation: matrix compile `PASS`; focused tests `126/126 OK`; py_compile `PASS`.

## FIBONACCI_GRID F040/F041 Passport Run
Completed UTC `2026-06-22T17:31:12Z`, local `2026-06-22 22:31:12 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B015/FIBONACCI_GRID anchor grid` with F040 and F041 in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import FIBONACCI passport into project docs | done | Use project copy as source | User file |
| Add registry/matrices/runtime/backtest gates | done | Keep F040/F041 isolated by passport | Passport mode |
| Run F040 LONG/SHORT | done | Record as `NO_GO` | F040 matrix |
| Run F041 LONG/SHORT | done | Record as `NO_GO` | F041 matrix |
| Continue strict passport route | pending | Add/run next user passport or return to pending F038/F039 if requested | User direction |

Artifact: `reports/qa_gate/fibonacci_grid_f040_f041_long_short_audit_20260622T173112Z.json`.

Validation: matrix compile `PASS`; focused tests `128/128 OK`; py_compile `PASS`.

## ENTRY_QUALITY_CONTEXT F042-F044 Passport Run
Completed UTC `2026-06-22T17:50:33Z`, local `2026-06-22 22:50:33 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B016/ENTRY_QUALITY_CONTEXT` with F044, F042, and F043 in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import ENTRY_QUALITY_CONTEXT passport into project docs | done | Use project copy as source | User file |
| Add B016 registry and three matrices | done | Keep F044/F042/F043 isolated by passport | Passport mode |
| Add side-aware runtime/backtest gates | done | Preserve LONG/SHORT context separation | F042-F044 side logic |
| Run F044 LONG/SHORT | done | Record as `NO_GO` | F044 matrix |
| Run F042 LONG/SHORT | done | Record as `NO_GO` | F042 matrix |
| Run F043 LONG/SHORT | done | Record as `NO_GO` | F043 matrix |
| Continue strict passport route | pending | Add/run next user passport or return to pending F038/F039 / Density Block B if requested | User direction |

Artifact: `reports/qa_gate/entry_quality_context_f042_f044_long_short_audit_20260622T175033Z_RU.md`.

Validation: matrix compile `PASS`; focused tests `130/130 OK`; py_compile `PASS`; launcher/text_guard `PASS`.

## BREAKOUT_RETEST F045-F049 Passport Run
Completed UTC `2026-06-22T18:16:00Z`, local `2026-06-22 23:16:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B017/BREAKOUT_RETEST` with F048, F049, F045, F047, and F046 in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import BREAKOUT_RETEST passport into project docs | done | Use project copy as source | User file |
| Add B017 registry and five matrices | done | Keep each passport isolated by action | Passport mode |
| Add runtime/backtest gates | done | Use single present action column per run | Dataset/backtest |
| Run F048 LONG/SHORT | done | Record as `NO_GO` / zero trades | F048 matrix |
| Run F049 LONG/SHORT | done | Record as `NO_GO` / negative | F049 matrix |
| Run F045 LONG/SHORT | done | Record as `NO_GO`; best tradeful still negative | F045 matrix |
| Run F047 LONG/SHORT | done | Record as `NO_GO` / negative | F047 matrix |
| Run F046 LONG/SHORT | done | Record as `NO_GO` / zero or negative | F046 matrix |
| Continue strict passport route | pending | Add/run next user passport, or return to pending F038/F039 / Density Block B if requested | User direction |

Artifact: `reports/qa_gate/b017_breakout_retest_f045_f049_audit_20260622T181600Z.md`.

Validation: matrix compile `PASS`; focused B017 tests `3/3 OK`; py_compile `PASS`; launcher/text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260622T181926Z.json`).

## MARKET_STRUCTURE F050-F052 Passport Run
Completed UTC `2026-06-22T18:35:00Z`, local `2026-06-22 23:35:00 +05:00`.
Status: `done / positive_test_candidate`.
Result: implemented and ran `B018/MARKET_STRUCTURE` with F050, F051, and F052 in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import MARKET_STRUCTURE passport into project docs | done | Use project copy as source | User file |
| Add B018 registry and three matrices | done | Keep each passport isolated by action | Passport mode |
| Add runtime/backtest gates | done | Use single present action column per run | Dataset/backtest |
| Run F050 LONG/SHORT | done | Record as `NO_GO` / zero trades | F050 matrix |
| Run F051 LONG/SHORT | done | Keep F051 SHORT as `POSITIVE_TEST_CANDIDATE`; validate further before any GO | F051 matrix |
| Run F052 LONG/SHORT | done | Record as `NO_GO` / zero trades | F052 matrix |
| Continue strict passport route | pending | Add/run next user passport, or run follow-up validation for F051 SHORT if user asks | User direction |

Artifact: `reports/qa_gate/b018_market_structure_f050_f052_audit_20260622T183500Z.md`.

Validation: matrix compile `PASS`; focused B018 tests `3/3 OK`; py_compile `PASS`; launcher/text_guard `PASS`.

## CANDLE_PATTERNS F053-F060 Passport Run
Completed UTC `2026-06-22T19:05:30Z`, local `2026-06-23 00:05:30 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B019/CANDLE_PATTERNS` with F055, F056, F059, F060, F057, F058, F054, and F053 in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import CANDLE_PATTERNS passport into project docs | done | Use project copy as source | User file |
| Add B019 registry and eight matrices | done | Keep each passport isolated by action | Passport mode |
| Add closed-candle runtime/backtest gates | done | Use shift(1)/shift(2), no current candle | Dataset/backtest |
| Run F055 LONG/SHORT | done | Record as `NO_GO` / zero trades | F055 matrix |
| Run F056 LONG/SHORT | done | Record as `NO_GO` / zero trades | F056 matrix |
| Run F059 LONG/SHORT | done | Record as `NO_GO`; LONG negative, SHORT zero trades | F059 matrix |
| Run F060 LONG/SHORT | done | Record as `NO_GO` / zero trades | F060 matrix |
| Run F057 LONG/SHORT | done | Record as `NO_GO` / zero trades | F057 matrix |
| Run F058 LONG/SHORT | done | Record as `NO_GO` / zero trades | F058 matrix |
| Run F054 LONG/SHORT | done | Record as `NO_GO`; SHORT negative | F054 matrix |
| Run F053 LONG/SHORT | done | Record as `NO_GO`; LONG negative | F053 matrix |
| Continue strict passport route | pending | Add/run next user passport, or validate earlier F051 SHORT candidate if requested | User direction |

Artifact: `reports/qa_gate/b019_candle_patterns_f053_f060_audit_20260622T190530Z.md`.

Validation: matrix compile `PASS`; focused B019 tests `3/3 OK`; py_compile `PASS`; text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260622T190822Z.json`).

## DIVERGENCE_PATTERNS F061-F066 Passport Run
Completed UTC `2026-06-22T19:33:00Z`, local `2026-06-23 00:33:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B020/DIVERGENCE_PATTERNS` with F061, F062, F063, F064, F065, and F066 in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import DIVERGENCE_PATTERNS passport into project docs | done | Use project copy as source | User file |
| Add B020 registry and six matrices | done | Keep each passport isolated by action | Passport mode |
| Add confirmed-pivot runtime/backtest gates | done | Use no-unconfirmed-pivot helper | Dataset/backtest |
| Run F061 LONG/SHORT | done | Record as `NO_GO`; LONG negative, SHORT zero trades | F061 matrix |
| Run F062 LONG/SHORT | done | Record as `NO_GO` / zero trades | F062 matrix |
| Run F063 LONG/SHORT | done | Record as `NO_GO`; LONG negative, SHORT zero trades | F063 matrix |
| Run F064 LONG/SHORT | done | Record as `NO_GO` / zero trades | F064 matrix |
| Run F065 LONG/SHORT | done | Record as `NO_GO`; LONG negative, SHORT zero trades | F065 matrix |
| Run F066 LONG/SHORT | done | Record as `NO_GO` / zero trades | F066 matrix |
| Continue strict passport route | pending | Add/run next user passport, or validate earlier F051 SHORT candidate if requested | User direction |

Artifact: `reports/qa_gate/b020_divergence_patterns_f061_f066_audit_20260622T193300Z.md`.

Validation: matrix compile `PASS`; focused B020 tests `3/3 OK`; py_compile `PASS`; text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260622T193442Z.json`).

## PATTERN_QUALITY F067-F068 Passport Run
Completed UTC `2026-06-22T19:47:00Z`, local `2026-06-23 00:47:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B021/PATTERN_QUALITY` with F067 and F068 in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import PATTERN_QUALITY passport into project docs | done | Use project copy as source | User file |
| Add B021 registry and two matrices | done | Keep each passport isolated by action | Passport mode |
| Add pattern-quality runtime/backtest gates | done | Use single present action column per run | Dataset/backtest |
| Run F067 LONG/SHORT | done | Record as `NO_GO`; LONG zero trades, SHORT negative | F067 matrix |
| Run F068 LONG/SHORT | done | Record as `NO_GO`; LONG/SHORT negative | F068 matrix |
| Continue strict passport route | pending | Add/run next user passport, or validate earlier F051 SHORT candidate if requested | User direction |

Artifact: `reports/qa_gate/b021_pattern_quality_f067_f068_audit_20260622T194700Z.md`.

Validation: matrix compile `PASS`; focused B021 tests `3/3 OK`; py_compile `PASS`; text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260622T194938Z.json`).

## CHART_PATTERNS F069-F077 Passport Run
Completed UTC `2026-06-22T20:21:00Z`, local `2026-06-23 01:21:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B022/CHART_PATTERNS` with F069-F077 in LONG and SHORT, using passport order F077, F073, F074, F075, F076, F069, F070, F071, F072.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import CHART_PATTERNS passport into project docs | done | Use project copy as source | User file |
| Add B022 registry and nine matrices | done | Keep each passport isolated by action | Passport mode |
| Add chart-pattern runtime/backtest gates | done | Use single present action column per run | Dataset/backtest |
| Run F077/F073/F074/F075/F076/F069/F070/F071/F072 LONG/SHORT | done | Record as `NO_GO`; no positive tradeful candidate | B022 matrices |
| Continue strict passport route | pending | Add/run next user passport, or validate earlier F051 SHORT candidate if requested | User direction |

Artifact: `reports/qa_gate/b022_chart_patterns_f069_f077_audit_20260622T202100Z.md`.

Validation: matrix compile `PASS`; focused B022 tests `3/3 OK`; py_compile `PASS`; text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260622T202309Z.json`).

## PATTERN_CONFIRMATION F078-F079 Passport Run
Completed UTC `2026-06-22T20:37:00Z`, local `2026-06-23 01:37:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B023/PATTERN_CONFIRMATION` with F079 and F078 in LONG and SHORT, using passport order F079 then F078.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import PATTERN_CONFIRMATION passport into project docs | done | Use project copy as source | User file |
| Add B023 registry and two matrices | done | Keep each passport isolated by action | Passport mode |
| Add confirmation runtime/backtest gates | done | Use single present action column per run | Dataset/backtest |
| Run F079 LONG/SHORT | done | Record as `NO_GO` / zero trades | F079 matrix |
| Run F078 LONG/SHORT | done | Record as `NO_GO`; LONG/SHORT negative | F078 matrix |
| Continue strict passport route | pending | Add/run next user passport, or validate earlier F051 SHORT candidate if requested | User direction |

Artifact: `reports/qa_gate/b023_pattern_confirmation_f078_f079_audit_20260622T203700Z.md`.

Validation: matrix compile `PASS`; focused B023 tests `3/3 OK`; py_compile `PASS`; text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260622T204015Z.json`).

## PATTERN_COMPOSITE_ENTRY F080-F081 Passport Run
Completed UTC `2026-06-22T20:55:00Z`, local `2026-06-23 01:55:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B024/PATTERN_COMPOSITE_ENTRY` side-specific passports F080 LONG and F081 SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import PATTERN_COMPOSITE_ENTRY passport into project docs | done | Use project copy as source | User file |
| Add B024 registry and two matrices | done | Keep F080 LONG and F081 SHORT isolated by action | Passport mode |
| Add side-specific runtime/backtest gates | done | F080 applies to LONG, F081 applies to SHORT | Dataset/backtest |
| Run F080 LONG | done | Record as `NO_GO` / zero trades | F080 matrix |
| Run F081 SHORT | done | Record as `NO_GO` / negative one timeout trade | F081 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/b024_pattern_composite_entry_f080_f081_audit_20260622T205500Z.md`.

Validation: matrix compile `PASS`; focused B024 tests `3/3 OK`; py_compile `PASS`; runtime launcher `OK`; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T210111Z.json`.

## PATTERN_TRADE_CONTEXT F082-F083 Passport Run
Completed UTC `2026-06-22T21:16:00Z`, local `2026-06-23 02:16:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `B025/PATTERN_TRADE_CONTEXT` with F082 and F083 in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Import PATTERN_TRADE_CONTEXT passport into project docs | done | Use project copy as source | User file |
| Add B025 registry and two matrices | done | Keep each passport isolated by action | Passport mode |
| Add side-aware runtime/backtest gates | done | Apply LONG/SHORT columns when present | Dataset/backtest |
| Run F082 LONG/SHORT | done | Record as `NO_GO`; LONG zero trades, SHORT negative | F082 matrix |
| Run F083 LONG/SHORT | done | Record as `NO_GO`; LONG/SHORT negative | F083 matrix |
| Continue strict passport route | pending | Add/run next user passport as next `Bxxx/Fxxx` block | User direction |

Artifact: `reports/qa_gate/b025_pattern_trade_context_f082_f083_audit_20260622T211600Z.md`.

Validation: matrix compile/passport allowlist `PASS`; focused B025 tests `3/3 OK`; py_compile `PASS`; runtime launcher `OK`; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T211551Z.json`.

## F001-F083 Passport Route Full Audit
Completed UTC `2026-06-23`, local `2026-06-23 +05:00`.
Status: `warn_with_completeness_gaps`, resolved by follow-up closures.
Artifact: `reports/qa_gate/f001_f083_passport_full_audit_20260623.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Audit active passport registry/matrices | done | Keep existing matrix allowlists; no legacy params found | Registry/matrices |
| Audit runtime/backtest isolation | done | Active-action hardening added against stale `F*_ALLOW` columns | `reports/qa_gate/stale_action_column_hardening_20260623T082000Z.md` |
| Audit F001-F083 completeness | done | Missing/planned ids closed; F017/F018 combined accepted | Follow-up closures |
| F024 | done | Closed as `B026/F024`; result `NO_GO`, do not promote standalone | `reports/qa_gate/f024_vwap_distance_long_short_audit_20260623T055200Z.md` |
| F026 | done | Closed as `B013/F026`; result `NO_GO`, do not promote standalone | `reports/qa_gate/f026_binshare60_long_short_audit_20260623T060100Z.md` |
| F027 | done | Closed as `B013/F027`; result `NO_GO`, do not promote standalone | `reports/qa_gate/f027_clustershare60_long_short_audit_20260623T062300Z.md` |
| F028 | done | Closed as `B013/F028`; result `NO_GO`, do not promote standalone | `reports/qa_gate/f028_vpocshare60_long_short_audit_20260623T064000Z.md` |
| F030 | done | Closed as `B013/F030`; result `NO_GO`, do not promote standalone | `reports/qa_gate/f030_binshare240_long_short_audit_20260623T070000Z.md` |
| F031 | done | Closed as `B013/F031`; result `NO_GO`, do not promote standalone | `reports/qa_gate/f031_clustershare240_long_short_audit_20260623T071000Z.md` |
| F032 | done | Closed as `B013/F032`; result `NO_GO`, do not promote standalone | `reports/qa_gate/f032_vpocshare240_long_short_audit_20260623T072500Z.md` |
| F038 | done | Closed as `B014/F038`; result `NO_GO`, do not promote standalone | `reports/qa_gate/f038_rangepose_long_short_audit_20260623T074000Z.md` |
| F039 | done | Closed as `B014/F039`; result `NO_GO`, do not promote standalone | `reports/qa_gate/f039_channelpos_long_short_audit_20260623T080500Z.md` |
| F017/F018 | done | Accepted as one combined Stochastic K/D passport; do not split unless the Stochastic grammar changes | `reports/qa_gate/f017_f018_combined_decision_audit_20260623T081000Z.md` |

## F024 VWAP Distance Gap Closure
Completed UTC `2026-06-23T05:52:00Z`, local `2026-06-23 10:52:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran previously open `F024` in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Create F024 strict passport | done | Use project copy as source | VWAP distance formula |
| Add B026 registry and F024 matrix | done | Keep B013-B025 numbering unchanged | Passport mode |
| Add runtime/backtest gate | done | Gate by `F024_VWAPDIST_ALLOW` only | Dataset/backtest |
| Run F024 LONG | done | Record as `NO_GO` / negative | F024 matrix |
| Run F024 SHORT | done | Record as `NO_GO` / zero trades | F024 matrix |
| Continue strict route | pending | Implement planned Density/VPOC gap passports next | User direction |

Artifact: `reports/qa_gate/f024_vwap_distance_long_short_audit_20260623T055200Z.md`.

## F026 Density Bin Share 60 Gap Closure
Completed UTC `2026-06-23T06:01:00Z`, local `2026-06-23 11:01:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `F026 density_bin_share_60_1m` in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add F026 active registry and matrix | done | Keep F026 isolated from F027/F030 | Passport mode |
| Add runtime/backtest gate | done | Gate by `F026_BINSHARE60_ALLOW` only | Dataset/backtest |
| Run F026 LONG | done | Record as `NO_GO` / negative one trade | F026 matrix |
| Run F026 SHORT | done | Record as `NO_GO` / negative | F026 matrix |
| Continue strict route | pending | Implement F027 next | User direction |

Artifact: `reports/qa_gate/f026_binshare60_long_short_audit_20260623T060100Z.md`.

## F027 Density Cluster Share 60 Gap Closure
Completed UTC `2026-06-23T06:23:00Z`, local `2026-06-23 11:23:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `F027 density_cluster_share_60_1m` in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add F027 active registry and matrix | done | Keep F027 isolated from F028/F030 | Passport mode |
| Add runtime/backtest gate | done | Gate by `F027_CLUSTERSHARE60_ALLOW` only | Dataset/backtest |
| Run F027 LONG | done | Record as `NO_GO` / negative | F027 matrix |
| Run F027 SHORT | done | Record as `NO_GO` / negative | F027 matrix |
| Continue strict route | pending | Implement F028 next | User direction |

Artifact: `reports/qa_gate/f027_clustershare60_long_short_audit_20260623T062300Z.md`.

## F028 Density VPOC Share 60 Gap Closure
Completed UTC `2026-06-23T06:40:00Z`, local `2026-06-23 11:40:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `F028 density_vpoc_share_60_1m` in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add F028 active registry and matrix | done | Keep F028 isolated from F030/F032 | Passport mode |
| Add runtime/backtest gate | done | Gate by `F028_VPOCSHARE60_ALLOW` only | Dataset/backtest |
| Run F028 LONG | done | Record as `NO_GO` / negative one trade | F028 matrix |
| Run F028 SHORT | done | Record as `NO_GO` / negative | F028 matrix |
| Continue strict route | pending | Implement F030 next | User direction |

Artifact: `reports/qa_gate/f028_vpocshare60_long_short_audit_20260623T064000Z.md`.

## F030 Density Bin Share 240 Gap Closure
Completed UTC `2026-06-23T07:00:00Z`, local `2026-06-23 12:00:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `F030 density_bin_share_240_1m` in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add F030 active registry and matrix | done | Keep F030 isolated from F026/F031/F032 | Passport mode |
| Add runtime/backtest gate | done | Gate by `F030_BINSHARE240_ALLOW` only | Dataset/backtest |
| Run F030 LONG | done | Record as `NO_GO` / negative three timeout trades | F030 matrix |
| Run F030 SHORT | done | Record as `NO_GO` / negative nine timeout trades | F030 matrix |
| Continue strict route | pending | Implement F031 next | User direction |

Artifact: `reports/qa_gate/f030_binshare240_long_short_audit_20260623T070000Z.md`.

## F031 Density Cluster Share 240 Gap Closure
Completed UTC `2026-06-23T07:10:00Z`, local `2026-06-23 12:10:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `F031 density_cluster_share_240_1m` in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add F031 active registry and matrix | done | Keep F031 isolated from F027/F030/F032 | Passport mode |
| Add runtime/backtest gate | done | Gate by `F031_CLUSTERSHARE240_ALLOW` only | Dataset/backtest |
| Run F031 LONG | done | Record as `NO_GO` / negative two timeout trades | F031 matrix |
| Run F031 SHORT | done | Record as `NO_GO` / negative twenty-six timeout trades | F031 matrix |
| Continue strict route | pending | Implement F032 next | User direction |

Artifact: `reports/qa_gate/f031_clustershare240_long_short_audit_20260623T071000Z.md`.

## F032 Density VPOC Share 240 Gap Closure
Completed UTC `2026-06-23T07:25:00Z`, local `2026-06-23 12:25:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `F032 density_vpoc_share_240_1m` in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add F032 active registry and matrix | done | Keep F032 isolated from F028/F030/F031 | Passport mode |
| Add runtime/backtest gate | done | Gate by `F032_VPOCSHARE240_ALLOW` only | Dataset/backtest |
| Run F032 LONG | done | Record as `NO_GO` / negative two timeout trades | F032 matrix |
| Run F032 SHORT | done | Record as `NO_GO` / negative six timeout trades | F032 matrix |
| Continue strict route | pending | Implement F038 next | User direction |

Artifact: `reports/qa_gate/f032_vpocshare240_long_short_audit_20260623T072500Z.md`.

## F038 Position In Range Gap Closure
Completed UTC `2026-06-23T07:40:00Z`, local `2026-06-23 12:40:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `F038 position_in_range_1m` in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add F038 active registry and matrix | done | Keep F038 isolated from F035/F036/F037/F039 | Passport mode |
| Add runtime/backtest gate | done | Gate by `F038_RANGEPOSE_ALLOW` only | Dataset/backtest |
| Run F038 LONG | done | Record as `NO_GO` / negative three timeout trades | F038 matrix |
| Run F038 SHORT | done | Record as `NO_GO` / negative one timeout trade | F038 matrix |
| Continue strict route | pending | Implement F039 next | User direction |

Artifact: `reports/qa_gate/f038_rangepose_long_short_audit_20260623T074000Z.md`.

## F039 Trend Channel Position Gap Closure
Completed UTC `2026-06-23T08:05:00Z`, local `2026-06-23 13:05:00 +05:00`.
Status: `done / no_go`.
Result: implemented and ran `F039 trend_channel_pos_1m` in LONG and SHORT.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add F039 active registry and matrix | done | Keep F039 isolated from F035/F036/F037/F038 | Passport mode |
| Add runtime/backtest gate | done | Gate by `F039_CHANNELPOS_ALLOW` only | Dataset/backtest |
| Run F039 LONG | done | Record as `NO_GO` / negative with one SL and two timeout exits | F039 matrix |
| Run F039 SHORT | done | Record as `NO_GO` / zero trades | F039 matrix |
| Continue strict route | done | F001-F083 passport audit findings are closed; next work is new user-selected calibration/passport task | User direction |

Artifact: `reports/qa_gate/f039_channelpos_long_short_audit_20260623T080500Z.md`.

## F017/F018 Combined Passport Decision
Completed UTC `2026-06-23T08:10:00Z`, local `2026-06-23 13:10:00 +05:00`.
Status: `done / accept_combined`.
Result: `F017/F018` remains one combined Stochastic passport because `%K` and `%D` are two lines of the same indicator, and `KD_CROSS` requires both lines inside one action grammar.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Review combined passport source | done | Keep `F017_F018` registry id | Stochastic passport |
| Check runtime/backtest action | done | Keep `F017_F018_STOCH14_ALLOW` as one gate | Dataset/backtest |
| Close split-vs-combined audit finding | done | Move to stale action-column hardening | F001-F083 audit |

Artifact: `reports/qa_gate/f017_f018_combined_decision_audit_20260623T081000Z.md`.

## Stale Action Column Hardening
Completed UTC `2026-06-23T08:20:00Z`, local `2026-06-23 13:20:00 +05:00`.
Status: `done / fixed_focused_tests_pass`.
Result: `run_prob_backtest` now supports explicit `active_entry_action_columns`; Optuna passport search passes the current matrix action id; backtest also infers the active action from `Fxxx_*` calibration params and ignores stale unrelated `F*_ALLOW` columns.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Add active action allowlist to backtest | done | Keep diagnostics in summaries | Backtest |
| Pass passport action id from Optuna search | done | Use `passport_mode.action_id` | Optuna space |
| Add stale-column regression test | done | Keep in focused checks | Tests |
| Close F001-F083 audit hardening item | done | Wait for next user-selected task | Audit |

Artifact: `reports/qa_gate/stale_action_column_hardening_20260623T082000Z.md`.

## Passport Control Index
Completed UTC `2026-06-23T08:41:37Z`, local `2026-06-23 13:41:37 +05:00`.
Status: `done / active_control_index`.
Result: created a compact human control panel for the passport-driven calibration route.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Create control index | done | Use before next passport/calibration decision | Passport route |
| Fix architecture decision | done | Keep hybrid model, not one huge config | Agent + local audit |
| Record no-mixing rules | done | Enforce by passport/registry/matrix workflow | Registry |
| Link next route | done | Build F001-F083 result register, then validate F051 SHORT | User decision |

Artifact: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_CONTROL_INDEX_RU.md`.
Audit: `reports/qa_gate/passport_control_index_audit_20260623T084500Z.md`.

## Passport Result Register F001-F083
Completed UTC `2026-06-23T08:47:02Z`, local `2026-06-23 13:47:02 +05:00`.
Status: `done / active_result_register`.
Result: created a compact result register for all `F001-F083` passport route decisions.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Create F001-F083 result register | done | Use as control map before next validation | Passport control index |
| Verify explicit id coverage | done | Keep all ids visible in register | Register audit |
| Lock production decision | done | No production GO from F001-F083 | Audit |
| Mark candidate exception | done | Validate `F051 SHORT` on more days | B018 audit |
| Continue strict route | pending | Run `F051 SHORT` multi-day validation | User direction |

Artifact: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_RESULT_REGISTER_RU.md`.
Audit: `reports/qa_gate/passport_result_register_audit_20260623T084702Z.md`.

## F051 SHORT Multi-Day Validation
Completed UTC `2026-06-23T09:10:00Z`, local `2026-06-23 14:10:00 +05:00`.
Status: `done / validation_fail_no_promotion`.
Result: ran three adjacent `short_only` F051 validation windows; all produced `0% / 0 trades`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Validate `F051 SHORT` on `2026-05-29` OOS | done | Record as no-trade | F051 matrix |
| Validate `F051 SHORT` on `2026-05-30` OOS | done | Record as no-trade | F051 matrix |
| Validate `F051 SHORT` on `2026-05-31` OOS | done | Record as no-trade | F051 matrix |
| Promotion decision | done | Do not promote, do not export to ML, do not combine | Audit |
| Continue strict route | pending | Pick next passport/feature route or new validation idea | User direction |

Artifact: `reports/qa_gate/f051_short_multiday_validation_audit_20260623T091000Z.md`.

## F001-F083 Passport Route Closeout
Completed UTC `2026-06-23T09:15:00Z`, local `2026-06-23 14:15:00 +05:00`.
Status: `done / closed_no_production_go`.
Result: closed the full `F001-F083` route after the only historical positive candidate failed validation.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Close F001-F083 route | done | Do not promote any F001-F083 feature | F051 validation |
| Freeze old candidate reuse | done | Keep old broad matrices as references only | Control index |
| Set next-entry options | done | Pick new passport/feature route, new validation idea, or exit/risk passport | User direction |

Artifact: `reports/qa_gate/f001_f083_route_closeout_audit_20260623T091500Z.md`.

## Core ML Bot TZ Audit
Completed UTC `2026-06-23T10:01:26Z`, local `2026-06-23 15:01:26 +05:00`.
Status: `done / audit_only`.
Artifact: `reports/qa_gate/core_ml_bot_tz_audit_20260623_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Compare project with user CORE ML bot TZ | done | Use audit as planning boundary | User pasted TZ |
| Decide anti-mess architecture | done | Keep `src/mlbotnav`; do not create parallel `trading_bot/` | Current project shape |
| Identify missing CORE contracts | done | Add small contracts/facades before refactor | Audit |
| Identify next implementation route | pending | Add feature/action/exit/risk/trade-log/ML dataset contracts, then fill CORE gaps | User direction |
## Current ML Contract Pointer 2026-06-23 Step 2.2 Closed
Closed: `2.2 Добавить passport context`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.

Next exact step: `2.3 Добавить trade identity`.

Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.
## Current ML Contract Pointer 2026-06-23 Step 2.3 Closed
Closed: `2.3 Добавить trade identity`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.

Next exact step: `2.4 Добавить duration labels`.

Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.
## Visual Entry Signal-Entry v2 next 2026-06-25
Статус: `NEXT_USER_CONFIRM_SIGNAL_ENTRY_V2_THEN_RERUN_SCORERS`.

Закрыто: создан v2-контракт `signal candle -> next open entry` со slippage-aware ценой входа.

Артефакты:
1. `src/mlbotnav/visual_entry_signal_entry_overlay.py`;
2. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/manual_entries.json`;
3. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_zoom_panels_20260625T102849Z.png`.

Следующий шаг: пользователь подтверждает или правит `S# -> ENTRY #`. После подтверждения заново прогнать visual scorer, solo-passport runner и combo diagnostic против v2.

## Visual Entry Instrument Stack Next 2026-06-25
Статус: `next / build_noise_suppression_cluster_priority_runner`.

Аудит: `reports/final_review/visual_entry_v3/instrument_stack_audit/visual_entry_instrument_stack_audit_20260625_RU.md`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать роли паспортов для visual-entry | done | Использовать аудит как карту | Instrument stack audit |
| Заморозить `DQ01/DQ03` как карту кандидатов | done | Не передавать в ML | Deep reclaim report |
| Собрать diagnostic table manual-hit vs false-entry | pending | Добавить runner | Manual v3 + DQ01/DQ03 |
| Добавить cluster priority/noise suppression | pending | Выбирать максимум один вход на кластер | Diagnostic table |
| Отрендерить PNG входов | pending | Показать пользователю визуально | Runner result |
| Проверить `2026-05-13`/`2026-05-14` без подкрутки | pending | Только после DEV результата | Stable DEV rule |

Первый круг признаков: `F035/F038/F009/F010/F012/F017_F018/F023/F020/F055/F057/F059`.

## Visual Entry Noise Suppression Follow-up 2026-06-25
Статус: `next / recover_0826_1700_without_false_explosion`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить cluster-priority runner | done | Использовать как базу | `CP01` |
| Прогнать DEV `2026-05-12` | done | Проверить PNG глазами | Runner |
| Зафиксировать лучший слой `CP01` | done | Не передавать в ML | Report |
| Добрать `08:26` | pending | Проверить мягкий no-wick/soft reclaim без lookahead | DQ03 diagnostics |
| Добрать `17:00` | pending | Проверить late retest/reclaim подслой | D03 diagnostics |
| Удержать false | pending | Цель: не возвращаться выше `<=35` false | CP01 baseline |
| Validation `2026-05-13`/holdout `2026-05-14` | pending | Только после DEV-стабилизации | User visual check |

Текущий baseline: `CP01_DQ01_CLUSTER10_SCORE12` = `9/11`, `28` false, `37` entries.

## Visual Entry CP06 Validation Next 2026-06-25
Статус: `next / validate_cp06_without_tuning`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добрать `08:26` | done | Зафиксировано через `RECOVER_NOWICK_SUPPORT_PULLBACK` | DQ03/E05 |
| Добрать `17:00` | done | Зафиксировано через `RECOVER_D03_LATE_RETEST` | D03 |
| Удержать false | done | `28` false, не выше CP01 | CP06 |
| Добавить regression test на recover | done | Поддерживать в тестах | Unit tests |
| Визуально согласовать PNG | pending | Пользователь смотрит главный PNG | CP06 report |
| Validation `2026-05-13` без подкрутки | pending | Сначала подготовить/подтвердить manual labels дня | User visual workflow |
| Holdout `2026-05-14` без подкрутки | pending | После validation | User visual workflow |

Текущий лучший DEV-слой: `CP06_CP01_RECOVER_NOWICK_LATE_RETEST` = `11/11`, `28` false, `39` entries.

## Visual Entry Swing/Support Event Next 2026-06-29
Статус: `next / build_swing_support_retest_event_v1`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать `REVERSAL_BOTTOM_KNIFE_DROP_V0` | done | Использовать как отрицательный диагностический baseline | RBKD audit |
| Проверить validation `2026-05-13` | done | Не продвигать: `2/9`, `81` false | Manual entries |
| Проверить holdout `2026-05-14` | done | Не продвигать: `1/17`, `83` false | Manual entries |
| Зафиксировать запрет ML | done | ML/export/promotion запрещены | Too many false |
| Спроектировать event-state | pending | `SWING_SUPPORT_RETEST_EVENT_V1`: открыть событие дна/ретеста, взять первый вход, закрыть событие, cooldown | RBKD audit |
| Разделить режимы | pending | `DEEP_KNIFE`, `SUPPORT_RETEST`, `TREND_DIP_CONTINUATION` | Manual diagnostics |
| Рендер PNG для V1 | pending | Показать hit/false/miss на `2026-05-13` и `2026-05-14` | V1 runner |

Нельзя использовать: entry-свечу как feature, будущие high/low/close/volume, future return, MFE/MAE, target labels, offline cluster-winner.
## Visual Entry Significant Low Selector Next 2026-06-29
Статус: `next / build_significant_low_selector_v1`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать entry-only контракт | done | Не тянуть сделки, не использовать TP/SL | User correction |
| Собрать `SWING_SUPPORT_RETEST_EVENT_V1` | done | Использовать как baseline | SSRE audit |
| Проверить `2026-05-13` | done | Не продвигать: `1/9`, `29` false | Manual labels |
| Проверить `2026-05-14` | done | Не продвигать: `1/17`, `26` false | Manual labels |
| Построить `SIGNIFICANT_LOW_SELECTOR_V1` | pending | Выбирать значимый signal-low, а не первый микролой в зоне | SSRE miss reason |
| Сделать PNG overlay V1/V2 | pending | Показать ручные S/E и автоматические входы | Renderer |

Запрещено для selector: будущий рост, MFE/MAE, TP/SL, entry-свеча как feature, target label как feature.
## Fresh Strategy Overlay Next 2026-06-29
Статус: `next / visual_review_separate_strategy_png`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сделать fresh clean overlay runner | done | Использовать отдельные PNG по стратегиям | Manual entries |
| Наложить 4 default strategies | done | Не считать кандидатом | Fresh overlay audit |
| Убрать кашу общего слоя | done | Смотреть отдельные PNG | Separate overlays |
| Визуально выбрать живые стратегии | pending | Пользователь и Codex смотрят PNG глазами | Fresh PNG |
| Грубая калибровка живых | pending | Крутить только стратегии, которые визуально рядом с low | Visual review |
## User Red Arrows V2 Confirm Next 2026-06-29
Статус: `next / visual_confirm_manual_entries_v2`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Сохранить пользовательский скрин v2 | done | Использовать как source image | User screenshot |
| Автоматически снять стрелки | done | `17` entries saved, один ложный фрагмент удален | Red pixel detection |
| Создать verification PNG | done | Пользователь проверяет глазами | Manual entries |
| Подтвердить времена | pending | При необходимости поправить `manual_entries.json` | Visual confirm |
| Использовать v2 как scorer target | pending | Только после confirm | Confirmed labels |
## Significant Low Selector V1 Follow-up 2026-06-29
Статус: `next / build_low_cluster_ranker_v2`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Прогнать fresh default4 на v2 holdout | done | Не продвигать: `3/17`, `260` false | Manual v2 |
| Добавить `SIGNIFICANT_LOW_SELECTOR_V1` | done | Использовать как diagnostic-only карту признаков | Manual v2 |
| Проверить `SLS06` | done | Не продвигать: `5/17`, `71` false | SLS V1 |
| Проверить `SLS05` | done | Не продвигать: `2/17`, `20` false | SLS V1 |
| Проверить широкий `SLS10` | done | Не продвигать: `13/17`, `463` false | SLS V1 |
| Построить `LOW_CLUSTER_RANKER_V2` | pending | Выбирать один главный signal-low внутри active low-zone без future return и без cooldown-сеток | SLS audit |

## Low Cluster Ranker V2 Follow-up 2026-06-29
Статус: `next / split_missed_entries_by_regime`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `LOW_CLUSTER_RANKER_V2` | done | Использовать как noise-control diagnostic | SLS V1 |
| Проверить `LCR04` | done | Не продвигать: `3/17`, `10` false | LCR V2 |
| Проверить `LCR07` | done | Не продвигать: `2/17`, `4` false | LCR V2 |
| Проверить `LCR06` | done | Не продвигать: `7/17`, `64` false | LCR V2 |
| Разделить missed entries по режимам | pending | `DEEP`, `HOT_RECLAIM`, `TREND_DIP`, `STRUCTURE_BOS_FIBO_VOLUME` | LCR audit |
# Regime Split Ranker V1 Follow-up 2026-06-29
Статус: `next / build_regime_false_suppression_v2`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `REGIME_SPLIT_RANKER_V1` | done | Использовать как карту режимов | SLS/LCR |
| Проверить 4 режима | done | Не продвигать: false слишком много | V1 report |
| Зафиксировать online-style no future rewrite | done | Держать как обязательный контракт | Agent review |
| Снизить false в `STRUCTURE/TREND/HOT` | pending | Сделать `REGIME_FALSE_SUPPRESSION_V2` | V1 audit |
| Передача в ML | blocked | Только после visual confirm, validation/holdout и `APPROVED_FOR_ML` | User review |

# Regime False Suppression V2 Follow-up 2026-06-29
Статус: `next / build_online_low_event_quality_v3`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `REGIME_FALSE_SUPPRESSION_V2` | done | Использовать как suppress-диагностику | Regime Split V1 |
| Проверить лучший union `FSV21` | done | Не продвигать: `7/17`, `41` false | V2 report |
| Проверить чистый deep `FSV02` | done | Оставить как отдельный deep-кирпич: `2/17`, `4` false | V2 report |
| Проверить trend/hot | done | Не продвигать: false слишком много | V2 report |
| Построить `ONLINE_LOW_EVENT_QUALITY_V3` | pending | Event-state low/support-зоны + suppress горячих верхних полок, только past-only признаки | V2 audit + agent review |
| Передача в ML | blocked | Только после visual confirm, validation/holdout и `APPROVED_FOR_ML` | User review |

# Online Low Event Quality V3 Follow-up 2026-06-29
Статус: `next / build_deep_recovery_and_hot_recall_v4`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `ONLINE_LOW_EVENT_QUALITY_V3` | done | Использовать как чистый event-quality baseline | V2 audit |
| Проверить `OLEV20` | done | Не продвигать: `3/17`, `7` false | V3 report |
| Зафиксировать запрет ML | done | ML/export/promotion запрещены | Low recall |
| Добрать deep miss | pending | `DEEP_RECOVERY_AND_HOT_RECALL_V4`: `09:46`, `16:53`, `17:35` | V3 miss list |
| Добрать hot/trend miss | pending | Отдельный recall-кирпич для `07:40`, `08:15`, `10:49`, `14:14`, `15:46`, `18:10`, `18:50`, `20:50` | V3 miss list |
| Срезать ранние false | pending | Отдельные suppress против `03:09`, `03:52`, `09:06`, `09:13` | V3 false list |
| Передача в ML | blocked | Только после visual confirm, validation/holdout и `APPROVED_FOR_ML` | User review |

# Deep Recovery And Hot Recall V4 Follow-up 2026-06-29
Статус: `next / build_hot_trend_false_suppression_v5`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `DEEP_RECOVERY_AND_HOT_RECALL_V4` | done | Использовать как лучший текущий diagnostic baseline | V3 |
| Проверить `DRHR20` | done | Не продвигать: `5/17`, `13` false | V4 report |
| Проверить hot/trend diagnostic | done | Не включать в union: `8/17`, `43` false | V4 report |
| Построить `HOT_TREND_FALSE_SUPPRESSION_V5` | pending | Подавить ложные серии hot/trend, сохранив дополнительные hits `10:49`, `14:14`, `15:19`, `15:46` | V4 diagnostic |
| Передача в ML | blocked | Только после visual confirm, validation/holdout и `APPROVED_FOR_ML` | User review |

# Hot Trend False Suppression V5 Follow-up 2026-06-29
Статус: `next / build_base_false_suppression_v6`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `HOT_TREND_FALSE_SUPPRESSION_V5` | done | Использовать как чистый hot/trend diagnostic-кирпич | V4 diagnostic |
| Проверить `HTFS01` | done | Оставить как полезный слой: `4/17`, `1` false | V5 report |
| Проверить union `HTFS20_UNION_HTFS01` | done | Не передавать в ML: `9/17`, но `14` false | V5 report |
| Подавить ложные входы базовой V4-части | pending | Сделать `BASE_FALSE_SUPPRESSION_V6` по false `01:15`, `02:57`, `03:09`, `03:52`, `06:11`, `07:14`, `07:25`, `09:06`, `13:37`, `17:23`, `19:30`, `21:57`, `23:50` | V5 audit |
| Передача в ML | blocked | Только после visual confirm, проверки на следующих днях и `APPROVED_FOR_ML` | User review |

# Base False Suppression V6 Follow-up 2026-06-29
Статус: `next / run_v6_validation_20260513`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Добавить `BASE_FALSE_SUPPRESSION_V6` | done | Использовать как лучший текущий one-day слой | V5 audit |
| Проверить `BFS01` | done | База очищена: `5/17`, `0` false | V6 report |
| Проверить union `BFS20_UNION_BFS01...PLUS_HTFS01` | done | One-day результат `9/17`, `1` false | V6 report |
| Прогнать V6 на `2026-05-13` validation | pending | Запуск без изменения параметров, сравнить с `9` ручными входами validation | Manual validation labels |
| Разобрать false `18:47` | pending | Отдельный hot/trend suppress, если validation не сломается | V6 audit |
| Передача в ML | blocked | Только после validation/следующих дней и `APPROVED_FOR_ML` | User review |

# Todo 2026-06-30 C02 Split/Router

Статус: `NEXT_8_3_1_C02A_RULES_NO_SCORER_NO_ML`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| C02 good/bad audit | done | Использовать только как разметку, не как scorer | user labels |
| C02 split/router decision `8.3` | done | Не строить один общий C02 scorer | good/bad audit |
| C02A true deep-capitulation core | done | Draft rules V0 создан; ждать user visual review | split/router |
| Entry-only scorer C02/C02A | blocked | Только после `8.3.1` и визуального подтверждения правил | C02A rules |
| Multi-day / target-lock | blocked | Только после чистого seed-day scorer | scorer |
| Optuna / ML/export/promotion | blocked | Только после отдельного approval | user approval |

Требование к следующим скринам: показывать `signal`, `entry`, `entry_open_price`, `entry + 5 bps`; для работы глазами делать zoom/high-res/SVG, а не только размытый full-day обзор.

## Todo 2026-06-30 C02A Rules Draft

Статус: `WAIT_USER_VISUAL_REVIEW_C02A_RULES_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| C02A rules draft `8.3.1` | done | Показать пользователю PNG и получить `норм / фиксить` | split/router |
| User visual review C02A rules | current_next | Проверить глазами, не потеряли ли хорошие входы и не приняли ли плохие | C02A visual |
| Entry-only scorer C02A | blocked | Только после user visual review | user decision |
| Target-lock / multi-day | blocked | Только после scorer seed-day | scorer |
| Optuna / ML/export/promotion | blocked | Только после отдельного approval | user approval |

# V6 Validation Follow-up 2026-06-29
Статус: `next / build_generalization_v7`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Прогнать V6 на `2026-05-13` validation | done | Зафиксировано: `0/9`, `1` false | V6 validation report |
| Исправить падение длинного PNG имени | done | Короткий render label, без изменения сигналов | Windows path limit |
| Разобрать missed validation targets | pending | `00:18`, `01:08`, `03:30`, `07:45`, `08:48`, `12:54`, `16:16`, `19:44`, `22:31` | Validation audit |
| Построить `GENERALIZATION_V7` | pending | Новый режимный слой, проверка сразу на `2026-05-13` и `2026-05-14` | V6 fail |
| Передача в ML | blocked | Запрещено до устойчивой multi-day проверки и `APPROVED_FOR_ML` | User review |
# Todo 2026-06-30 Fresh Target-Led Visual Entry Workflow

Статус: `NEXT_START_FRESH_TARGET_LED_CHAT`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать новый рабочий протокол | done | Использовать `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_FRESH_PROCESS_TZ_RU.md` как стартовый файл свежего чата | user decision |
| Создать свежий чат | pending | Передать в prompt только новый порядок и запрет на старую очередь задач | protocol |
| Выбрать один день для чистого старта | pending | Подготовить чистый график без старых сигналов | fresh chat |
| Подтвердить `T01..T10` | pending | Ручные цели пользователя, signal candle -> next open | clean chart |
| Создать `target_ledger` | pending | Карточка на каждую цель, тип входа, status, lock_status | T01..T10 |
| Выбрать первый кластер | pending | 2-4 похожие точки одного типа | target_ledger |
| Строить стратегию под кластер | pending | Entry-only, PNG/scorer, no ML/no Optuna | cluster |
| Передача в ML | blocked | Только после multi-day stable и `APPROVED_FOR_ML` | user approval |

Рельсы до результата: `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_RAILS_RU.md`.

# Todo 2026-06-30 Fresh Target-Led Start

Статус: `NEXT_VISUAL_CONFIRM_HOT_RECLAIM_CLUSTER`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Выбрать один день для чистого старта | done | Использовать `2026-05-14` как первый fresh target-led день | fresh protocol |
| Подготовить чистый график без старых сигналов | done | Смотреть PNG глазами | source CSV |
| Создать `target_ledger` T01..T10 | done | Использовать JSON/MD как рабочий ledger | manual entries v2 |
| Разложить точки по типам | done | Проверить классификацию глазами | clean chart |
| Выбрать первый кластер | done | `HOT_RECLAIM_SUPPORT`: `T07/T08`; `T04` отклонена пользователем | target_ledger + visual review |
| Подтвердить T01..T10 | pending | Визуально подтвердить/поправить времена и типы | clean chart |
| Показать T07 | done | Исправлено пользователем: signal `10:42`, entry `10:43` | visual review |
| Показать T08 | done | По пользовательской метке inferred: signal `12:00`, entry `12:01` | visual review |
| Подтвердить T08 | pending | Пользователь должен коротко подтвердить `12:01` или поправить | inferred time |
| Создать паспорт-контракт под первый кластер | pending | Только после визуального подтверждения `HOT_RECLAIM_SUPPORT` | confirmed cluster |
| Optuna | blocked | Только внутри готового паспорта после entry-only PNG/scorer | passport |
| Передача в ML | blocked | Только после multi-day stable и `APPROVED_FOR_ML` | user approval |
# Todo 2026-06-30 Fresh Target-Led User Marked Order

Статус: `NEXT_CONFIRM_M01_FROM_USER_MARKED_ORDER`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Принять, что обязательных 10 точек нет | done | Работать по `M01..M15` слева направо | user full-day red boxes |
| Снять ordered-ledger по красным прямоугольникам | done | Использовать как порядок разработки, не как lock | screenshot detection |
| Подтвердить T08 | done | `signal 12:00 -> LONG entry 12:01`, статус `gold_user_visual_confirmed` | user "да" |
| Показать M01 zoom | done | Спросить `подходит / не подходит / сдвинуть` | M01 inferred |
| Зафиксировать решение по M01 | pending | Если подходит, перевести M01 в confirmed; если нет, reject/shift | user visual decision |
| Перейти к M02 | pending | Только после решения по M01 | M01 decision |
| Optuna | blocked | Только после паспорта и entry-only PNG/scorer | confirmed cluster |
| ML/export/promotion | blocked | Только после `APPROVED_FOR_ML` | user approval |
# Todo 2026-06-30 M02 Visual Confirm

Статус: `WAIT_USER_DECISION_M02`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать M01 | done | `signal 03:23 -> LONG entry 03:24`, подходит | user confirm |
| Показать M02 zoom | done | `signal 03:58 -> LONG entry 03:59` | M01 confirmed |
| Зафиксировать решение по M02 | pending | `подходит / не подходит / сдвинуть` | user visual decision |
| Перейти к M03 | pending | Только после решения по M02 | M02 decision |
# Todo 2026-07-01 Dataset Base V1 Next Rails

Статус: `NEXT_DATASET_QUALITY_AUDIT_OR_ARROW_SHIFT_ZOOM_NO_ML`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Закрыть 15 спорных текущих авто-точек | done | Использовать V1 как актуальную supervised-базу по текущим точкам | user feedback |
| Две принятые точки `LA018`, `LA020` | done | Считать positive/gold в dataset V1 | user red rectangle |
| Отклонить 13 текущих авто-точек | done | Считать negative по текущему entry | user feedback |
| Стрелочные альтернативы `LA026/LA048/LA057/LA059/LA062` | pending | Делать только отдельным zoom/time, не вытаскивать точную минуту из скрина | user arrows |
| Аудит блоков/фичей по `28/79` | next | Сравнить хорошие и плохие входы по causal-блокам без future return и без entry-candle OHLCV | dataset V1 |
| ML/export/training/Optuna | blocked | Только после отдельного `APPROVED_FOR_ML` | user approval |
# Todo 2026-07-01 Dataset Quality Audit Next

Статус: `NEXT_BUILD_NARROW_RULE_CANDIDATE_NO_ML`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Аудит блоков по базе `28/79` | done | Использовать выводы V0, не простую сумму блоков | dataset V1 |
| Выбрать первый узкий тип | current_next | Начать с `SUPPORT_RETEST_LOW` или `TREND_DIP_CONTINUATION` | quality audit |
| `LOW_ANCHOR_RECLAIM` standalone | blocked | Не использовать как allow в текущем виде | `0/16` positive |
| `B013/B020/divergence` standalone | blocked | Оставлять только как context/evidence после дополнительной проверки | audit V0 |
| ML/export/training/Optuna | blocked | Только после отдельного `APPROVED_FOR_ML` | user approval |
# Todo 2026-07-01 ML Dataset Ladder

Статус: `NEXT_SUPPORT_RETEST_LOW_REVIEW_SHEET_NO_ML`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Зафиксировать лестницу до ML | done | Использовать `FRESH_TARGET_LED_ML_DATASET_LADDER_RU.md` | user request |
| `2.1_SUPPORT_RETEST_LOW_REVIEW_SHEET_9_GOOD_16_BAD` | current_next | Собрать PNG review-sheet и короткий аудит признаков | dataset V1 |
| Draft-паспорт `SUPPORT_RETEST_LOW` | blocked | Только после review-sheet и user `норм / фиксить` | 2.1 |
| Scorer/target-lock | blocked | Только после draft-паспорта | passport |
| Optuna | blocked | Только внутри готового паспорта после visual/scorer | passport |
| ML/export/training | blocked | Только после отдельного `APPROVED_FOR_ML` | user approval |
# Todo 2026-07-01 SUPPORT_RETEST_LOW Review Sheet V0

Статус: `WAIT_USER_REVIEW_SUPPORT_RETEST_LOW_SHEET`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| `2.1_SUPPORT_RETEST_LOW_REVIEW_SHEET_9_GOOD_16_BAD` | done | Показать PNG пользователю | dataset V1 |
| User visual review | current_next | Получить `норм / фиксить` и список панелей для сдвига, если есть | review-sheet |
| Draft-паспорт `SUPPORT_RETEST_LOW` | blocked | Только после user `норм` | user review |
| Scorer/target-lock | blocked | Только после draft-паспорта | passport |
| ML/export/training/Optuna | blocked | Только после отдельных этапов и `APPROVED_FOR_ML` | approval |
# Todo 2026-07-01 SUPPORT_RETEST_LOW Passport Draft V0

Статус: `WAIT_USER_REVIEW_SUPPORT_RETEST_LOW_PASSPORT_DRAFT`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Draft-паспорт `SUPPORT_RETEST_LOW` | done | Показать пользователю паспорт/card | review-sheet норм |
| User review passport draft | current_next | Получить `норм / фиксить` | draft passport |
| Entry-only PNG/scorer seed-check | blocked | Только после user `норм` по паспорту | user review |
| Target-lock / multi-day | blocked | Только после seed scorer и visual review | scorer |
| Optuna | blocked | Только внутри готового паспорта после scorer | passport |
| ML/export/training | blocked | Только после отдельного `APPROVED_FOR_ML` | approval |

# Todo 2026-07-02 Outcome Low Miner V0

Статус: `WAIT_USER_REVIEW_OUTCOME_LOW_MINER_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Outcome low miner V0 | done | Показать hit zoom PNG пользователю | user proposal |
| User visual review | current_next | Получить `норм / фиксить / нужен меньший порог` | V0 PNG |
| Соседний outcome threshold `+0.8%/+1.0%` | optional | Делать только после user review, как offline outcome label | V0 review |
| Запись в ML dataset | blocked | Только после отдельного ручного подтверждения точек и `APPROVED_FOR_ML` | future approval |
| Scorer/target-lock/Optuna | blocked | Outcome miner сам по себе не дает права на scorer/lock/Optuna | passport chain |

# Todo 2026-07-02 Outcome Low Miner 1pct Comparison

Статус: `WAIT_USER_REVIEW_OUTCOME_LOW_MINER_1PCT`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Outcome low miner `+1.0%` | done | Показать PNG пользователю | user request |
| User visual review `+1.0%` | current_next | Получить `норм / слабые / нужны другие пороги` | hit zoom PNG |
| Сравнить `+1.0%` против `+1.5%` | current_next | Решить, какой threshold использовать для ускоренного review pool | user review |
| ML/export/training | blocked | Только после ручного approved-ledger и `APPROVED_FOR_ML` | future approval |
# Todo 2026-07-02 SUPPORT_RETEST_LOW Entry-Only Scorer V0

Статус: `WAIT_USER_REVIEW_SUPPORT_RETEST_LOW_SCORER_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Entry-only scorer seed-check V0 | done | Показать PNG пользователю | passport draft ok |
| User review scorer V0 | current_next | Получить `норм / фиксить` по оранжевым false-positive | scorer PNG |
| `V1_REJECT_GUARDS` | blocked | Разобрать `LA033/LA034/LA041/LA048/LA065/T15L17/T15L18/T15L20`, не потеряв 9 good | user review |
| Target-lock / multi-day | blocked | Запрещено, пока false entries too many | scorer V0 |
| Optuna | blocked | Только после чистого паспорта/scorer | later |
| ML/export/training | blocked | Только после отдельного `APPROVED_FOR_ML` | approval |
## Todo 2026-07-02 Good 1pct Review Pool

Статус: `WAIT_USER_REVIEW_GOOD_1PCT_POOL_SMOKE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Multi-day review pool script | done | Использовать VS Code задачу или CLI для диапазона дат | user request |
| Smoke `2026-05-13` | done | Показать пользователю PNG/CSV/JSON run-папку | script |
| W18-W20 learning run | current_next | Запустить диапазон `2026-04-27..2026-05-17`, затем смотреть PNG глазами | user approval |
| W21 blind check | blocked | Только после ручного review W18-W20, без донастройки по W21 | review pool |
| W22 final blind check | blocked | Только после W21 | review pool |
| ML/export/training | blocked | Только после ручного approved-ledger и отдельного `APPROVED_FOR_ML` | future approval |

## Todo 2026-07-02 DCA Risk Audit V0

Статус: `WAIT_USER_REVIEW_DCA_RISK_AUDIT_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| `DCA_RISK_AUDIT_V0` script | done | Использовать для W18-W20 risk review | `GOOD_1PCT` pool |
| W18-W20 run | done | Показать summary/top-day PNG и таблицу классов | script |
| User review risk classes | current_next | Решить, что допускаем в будущий датасет: `A_FAST_CLEAN`, часть `B_DCA_SURVIVABLE`, или что-то еще | PNG/CSV |
| Full-history knife map | blocked | Только после фикса правил на W18-W20 | user review |
| ML/export/training | blocked | Только после approved-ledger и отдельного `APPROVED_FOR_ML` | future approval |
| Optuna/scorer/target-lock/API | blocked | DCA audit не дает права запускать эти этапы | risk review |
## Todo 2026-07-02 Significant Low Calibration V0

Статус: `WAIT_USER_REVIEW_SIGNIFICANT_LOW_CALIBRATION_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| `SIGNIFICANT_LOW_CALIBRATION_V0` script | done | Использовать для отсечения микролоев и дублей | DCA closeup feedback |
| Run `2026-05-02` | done | Показать пользователю PNG/CSV run | script |
| Зеленые `KEEP_SIGNIFICANT_LOW_V0` | current_next | Проверить глазами: оставить как positive или ослабить/ужесточить фильтр | user review |
| Желтые `USER_SHIFT_PENDING_REANCHOR` | current_next | Делать отдельный zoom и точный перенос anchor/entry, не считать готовой сделкой | user review |
| V1 параметры significant-low | blocked | Только после ручного review V0 | green/yellow review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Только после approved-ledger и отдельного `APPROVED_FOR_ML` | future approval |

### Актуальный user layer 2026-05-02

Статус: `WAIT_USER_REVIEW_SIGNIFICANT_LOW_USER_ACTUAL_V1C3`.

Актуальный run: `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_20260502_user_actual_v1c3_20260702_190227`.

Следующий шаг:

- проверить `6` green keep: `LA002`, `LA015`, `LA018`, `LA021`, `LA040`, `LA050`;
- отдельно решить `2` yellow reanchor: `LA007`, `LA028`;
- считать `LA048` и соседний `LA049` отклоненными; `LA051` не брать как good, он отфильтрован как duplicate-basin;
- не возвращаться к полному списку `54` как к списку хороших входов.

### Reanchor zoom для стрелок пользователя

Статус: `WAIT_USER_REVIEW_REANCHOR_APPLIED_V1`.

Рабочий PNG: `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_zoom_v0_20260702_191450/SIGNIFICANT_LOW_REANCHOR_ZOOM_V0_20260502.png`.

Примененный run: `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v1_20260703_060258`.

Сделано:

- `RA001_FROM_LA007`: signal `03:14`, entry `03:15`;
- `RA003_SHIFT_LEFT_LA050`: visual marker `22:25` на low, execution `entry_open=84.06000000`, `entry +5bps=84.10203000`;
- `LA028` оставлен pending, потому что на последнем скрине нет отдельной новой стрелки.

Следующий шаг:

- получить user review по `SIGNIFICANT_LOW_REANCHOR_APPLIED_V1_20260502_ZOOM.png`;
- если `LA028` тоже надо двигать, попросить отдельную стрелку/подтверждение;
- после `норм` собрать следующий слой significant-low V1 без ML/Optuna/scorer/API.

### User new entry zoom 20:45-21:05

Статус: `WAIT_USER_ARROW_ON_USER_NEW_ENTRY_ZOOM_V0`.

Рабочий PNG: `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_user_new_entry_zoom_v0_20260703_060806/SIGNIFICANT_LOW_USER_NEW_ENTRY_ZOOM_V0_20260502_2045_2105.png`.

Следующий шаг:

- пользователь ставит стрелку на точный low/entry в этом zoom;
- после стрелки создать новый applied layer с `signal_time_utc`, `entry_time_utc`, `entry_open`, `entry +5bps`;
- не считать этот zoom ML-label до ручного подтверждения.

### Reanchor Applied V2 RA004

Статус: `WAIT_USER_REVIEW_REANCHOR_APPLIED_V2_RA004`.

Сделано:

- добавлена ручная точка `RA004_USER_ENTRY_2049`;
- signal `20:48`, entry `20:49`;
- `entry_open=84.09000000`, `entry +5bps=84.13204500`;
- создан close-zoom без растягивания шкалы до `+1%`.

Следующий шаг:

- показать пользователю `SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502_CLOSE_ZOOM_RA004.png`;
- если `норм`, оставить `RA004` в applied V2;
- если фикс, двигать только `RA004`, не трогая старые `RA001/RA003`;
- `RA002/LA028` остается pending до отдельной стрелки.

Запрещено: ML/export/training/scorer/target-lock/Optuna/API.

### Manual Reanchors V0 Source Of Truth

Статус: `WAIT_USER_REVIEW_MANUAL_REANCHORS_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| JSON source-of-truth для ручных reanchor-точек | done | Использовать как единственный источник при перерисовке | user arrows |
| Renderer `visual_entry_manual_reanchor_review_v0.py` | done | Перегенерировать PNG после каждой правки JSON | config |
| Clean confirmed overview | done | Показать пользователю без старых DCA/GOOD сделок | renderer |
| Review sheet + close zoom RA003/RA004 | done | Получить `норм / фиксить` | user review |
| `RA002_PENDING_FROM_LA028` | pending | Нужна отдельная стрелка/подтверждение, пока не good | user arrow |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Запрещено без отдельного решения | guardrails |

Актуальный run: `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936`.

### STAS1 GOOD_1PCT anchor-next-open V0

Статус: `WAIT_USER_REVIEW_STAS1_20260502_ANCHOR_NEXT_OPEN_FIX_V0`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Исправить `entry` строго на следующую свечу после low | done | Использовать этот контракт как базовый для STAS1 | code fix |
| Регрессионный тест на `anchor_idx + 1` | done | Запускать при следующих правках low selector | pytest |
| Новый run `2026-05-02` | done | Пользователь смотрит overview/closeups | STAS1 |
| Ручная чистка шума после фикса entry | pending | Отметить слабые/дубли/неправильные low на новых PNG | user review |
| Дальнейшая настройка значимости low | pending | Менять фильтры только после user feedback по новому run | user review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать | guardrails |

Актуальный run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034`.

### Codex/VS Code load audit 2026-07-07

Статус: `LOCAL_FIX_APPLIED_WAIT_UI_RELOAD`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Найти источник нагрузки CPU/RAM/disk | done | Не считать это проблемой GitHub-веток без новых признаков | process audit |
| Остановить зависший `git add -A` | done | Следить, чтобы он не появлялся снова на тяжелых папках | process audit |
| Исключить STAS run-артефакты из Git | done | Не добавлять `runs` вручную | `.gitignore` |
| Исключить тяжелые папки из VS Code watcher/search/Pylance | done | Перезагрузить окно VS Code для применения | `.vscode/settings.json` |
| Проверить нагрузку после reload VS Code | done | Git-процессов нет, VS Code почти idle, остаточная нагрузка идет от активного Codex-чата | user machine |
### STAS4 combo strategies 2026-05-10..2026-05-12

Статус: `WAIT_USER_REVIEW_STAS4_COMBO_4_STRATEGIES_3D`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Прогнать `structure_ta+trend_momentum` на 3 днях | done | Пользователь смотрит PNG глазами | STAS2 run |
| Прогнать `structure_ta+volume_flow` на 3 днях | done | Пользователь смотрит PNG глазами | STAS2 run |
| Прогнать `pattern+structure_ta` на 3 днях | done | Пользователь смотрит PNG глазами | STAS2 run |
| Прогнать `density_profile+structure_ta` на 3 днях | done | Пользователь смотрит PNG глазами | STAS2 run |
| Выбрать слой для первого рабочего фильтра шума | pending | Сравнить глазами: жесткий бан `structure_ta+volume_flow` против сильного фильтра `structure_ta+trend_momentum` | user review |
| ML/export/training/scorer/target-lock/Optuna/API | blocked | Не запускать до согласования признаков и архитектуры | STAS4 ТЗ |

Главный отчет: `STAS4_FEATURE_HYPOTHESIS_REVIEW/STAS4_COMBO_4_STRATEGIES_3D_SUMMARY_20260709_RU.md`.
## Todo 2026-07-11 Codex Startup Disk Load Audit

Статус: `CODEX_STARTUP_DISK_LOAD_AUDIT_READY_NO_DELETE_NO_CODE_CHANGE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить текущие процессы Codex/Git/VS Code | done | Зависшего `git add -A` нет; краткие Git-команды быстрые | process audit |
| Проверить размеры проекта и `.codex` | done | Использовать отчет `docs/codex/CODEX_STARTUP_DISK_LOAD_AUDIT_20260711_RU.md` | size audit |
| Перенести `_codex_offload_20260530` из рабочей папки | pending | Только после подтверждения пользователя; лучше в отдельный архив вне `MLbotNav` | user approval |
| Разобрать старые `.codex` backup/archived-сессии | pending | Только после отдельного решения пользователя; без ручного удаления вслепую | user approval |
| Проверить поведение после следующей перезагрузки | pending | Сразу после старта снять процессы и `Get-Counter` по диску | next reboot |

## Todo 2026-07-14 STAS5 V4 Group Ranker

Статус: `V4_OFFLINE_REVIEW_DONE__V4L_LIVE_SAFE_NEXT`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Собрать V4 train dataset `2026-05-01..25` | done | Использовать manifest `STAS5_ML_CORE/artifacts/v4/features/STAS5_V4_GROUP_RANK_TRAIN_DATASET_20260501_20260525.manifest.json` как контроль | V2 snapshot + V4 ledger |
| Подтвердить, что `2026-05-15` входит в train/review | done | Больше не считать 15 мая карантинным днем в V4 train `01..25` | user correction |
| Проверить join исправленного ledger `15..25` | done | `738/738`, missing `0`, duplicate keys `0` | forward CSV |
| Обучить V4 group ranker | done | Модель `STAS5_ML_CORE/artifacts/v4/model/runs/stas5_v4_train_20260714_163911/stas5_v4_group_ranker_20260501_20260525_v0.joblib` | dataset PASS |
| Прогнать blind forward `2026-05-26..30` | done | Смотреть PNG/CSV в `STAS5_ML_CORE/artifacts/v4/forward/runs/stas5_v4_forward_20260526_20260530_20260714_164144` | V4 model |
| Пометить текущий V4 как offline review, не live-safe | done | Не использовать `stas5_v4_train_20260714_163911` как production/live model | no-future audit |
| Зафиксировать V4L live-safe план | done | Использовать `STAS5_ML_CORE/08_STAS5_V4L_LIVE_SAFE_GROUP_RANKER_PLAN_RU.md` | agents audit |
| Создать V4L live replay dataset builder | pending | Считать только `v4l_*_so_far`, labels брать из V4 ledger, future/full-group признаки audit-only | V4L plan |
| Создать V4L leakage guard | pending | `LIVE_SAFE_FEATURE_ALLOWLIST`, banned columns, `feature_available_time_utc <= entry_time_utc`, `prefix invariance` | V4L plan |
| Обучить V4L live-safe model | pending | Только после V4L guard `PASS`; старый full-group V4 не переиспользовать как live | V4L dataset |
| Прогнать V4L forward `2026-05-26..30` | pending | Sequential replay, решение доступно не позже `entry_time_utc`; сравнить с offline review | V4L model |
| Сравнить offline V4 и live-safe V4L | pending | `ENTER_set_jaccard`, decision flip matrix, missed winners, bad early enters, entries per day by regime | V4L forward |

## Todo 2026-07-14 STAS5 V4L Live-Safe Group Ranker

Статус: `V4L_LIVE_SAFE_TRAIN_FORWARD_READY__USER_REVIEW_NEXT`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Создать V4L live replay dataset builder | done | Использовать `STAS5_ML_CORE/artifacts/v4l/features/STAS5_V4L_LIVE_SAFE_TRAIN_DATASET_20260501_20260525.manifest.json` как guard source | V4 ledger |
| Создать V4L leakage guard | done | Prefix-invariance `1710/1710`, forbidden features `{}`; full-group V4 columns отсутствуют в dataset | V4L dataset |
| Обучить V4L live-safe model | done | Model `STAS5_ML_CORE/artifacts/v4l/model/runs/stas5_v4l_train_20260714_181635` | dataset PASS |
| Прогнать V4L forward `2026-05-26..30` | done | Смотреть PNG/CSV в `STAS5_ML_CORE/artifacts/v4l/forward/runs/stas5_v4l_forward_20260526_20260530_20260714_181635` | V4L model |
| Дать пользователю одну команду на повтор полного цикла | done | `.\STAS5_ML_CORE\run_stas5_v4l_live_safe_train_forward.ps1` | wrapper |
| Сравнить offline V4 и live-safe V4L глазами на PNG | pending | Проверить, какие красивые offline-входы потерялись без будущего, и какие live-входы слишком ранние | user review |
| Калибровать V4L thresholds/decision policy | pending | Менять только после просмотра forward PNG; не возвращать day-end top-N и full-group признаки | user review |

## Todo 2026-07-15 STAS5 V5 Row-Level Corrected Labels

Статус: `V5_ROW_LABEL_PREP_AFTER_V4_V4L_REJECTION`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Заморозить V4/V4L как нерабочую финальную стратегию | done | Не использовать group-rank/one-entry-group как следующий production-контур | user decision |
| Разобрать новый day23 pre-knife скрин по оригинальным CSV/OHLCV | done | Использовать отчет `STAS5_V4_GROUP_RANK_REVIEW_20260523_USER_CORRECTED_V2_PRE_KNIFE_RU.md` | 2026-05-23 artifacts |
| Создать day23 corrected V2 pre-knife ledger | done | Для следующей сборки labels брать `USER_CORRECTED_V2_PRE_KNIFE`, а не day23 `V1` | user red rectangle |
| Собрать V5 row-level label-source `2026-05-15..25` | done | Использовать `STAS5_ML_CORE/artifacts/v5/labels/STAS5_V5_ROW_LABEL_SOURCE_20260515_20260525_WITH_DAY23_PRE_KNIFE_V1.csv`; day23 уже заменен на V2 | corrected ledgers |
| Собрать V5 row-level training dataset `2026-05-01..25` | pending | `01..14` legacy labels + V5 label-source `15..25`; `BEST_GOOD` и пользовательские `GOOD_ALT` считать positive, `BAD_IN_GROUP/NO_TRADE_GROUP` negative | V5 label-source |
| Проверить no-future feature list для V5 | pending | Запретить postfact/future/TP/Stas3/exit/old ML decision/score/group winner/full-group future columns; разрешить только causal признаки на `entry_time_utc` | leakage guard |
| Обучить V5 row-level ML без поверхностного group policy | pending | Модель должна сама давать высокий score нужным входам и низкий score верхним/ранним bad examples | V5 dataset PASS |
| Сделать blind forward `2026-05-26..30` | pending | Без ручного подсмотра, без ограничений min/max входов в день; оценить графики глазами | V5 model |
## Todo 2026-07-15 Codex CPU Load Check

Статус: `CODEX_CPU_LOAD_CHECK_READY_NO_KILL_NO_DELETE_NO_CODE_CHANGE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить текущий CPU по процессам | done | Codex суммарно `5.3%..9.2% CPU`; общий CPU `22.8%..44.4%` | process sample |
| Проверить Git-процессы | done | Найден повторяющийся `git diff --find-renames --numstat -z` от `Codex.exe`; `git add -A` нет | process audit |
| Проверить размер dirty worktree | done | `1574` untracked files, `424.8 MB`; основной источник `STAS5_ML_CORE` | git ls-files |
| Уменьшить dirty worktree | pending | Отдельным решением: коммит/стейдж source files или `.gitignore` для generated artifacts | user decision |
| Перезагрузить Codex/VS Code после стабилизации файлов | optional | Только когда нет важного незавершенного действия | user timing |
## Todo 2026-07-16 Codex Unload Applied

Статус: `CODEX_UNLOAD_APPLIED_NO_DELETE_NO_PROCESS_KILL_CODEX`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Понизить приоритет Codex | done | Процессы `Codex`/`codex` выставлены в `BelowNormal` | user request |
| Убрать STAS5 generated/run из Git scan-поверхности | done | `.gitignore`: `STAS5_ML_CORE/artifacts/`, `STAS5_ML_CORE/runs/` | source/run split |
| Убрать STAS5 generated/run из VS Code watcher/search/Pylance | done | `.vscode/settings.json` валиден, добавлены excludes | local UI |
| Проверить эффект | done | Untracked: `1574/424.8 MB` -> `381/41.6 MB`; активных `git.exe` нет | diagnostics |
| Дополнительно разгрузить STAS4/STAS5 | pending | Только после решения, какие оставшиеся файлы source-of-truth, а какие generated | user decision |

## Todo 2026-07-16 Codex Idle Relief

Статус: `CODEX_IDLE_RELIEF_APPLIED_NO_DELETE_NO_STAS_TOUCH`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Остановить фоновый read-only Git | done | `git status --porcelain` остановлен; активных `git.exe` нет | user request |
| Понизить приоритет Codex/VS Code | done | `Codex`/`codex`/`Code` выставлены в `Idle` | current session |
| Остановить лишний VS Code Codex extension server | done | Остановлен `openai.chatgpt...\codex.exe app-server`; расширение не удалялось | VS Code |
| Проверить источник дискового всплеска | done | Главный источник в коротком окне - `MsMpEng` (Microsoft Defender) | process counters |
| Решить вопрос с Defender exclusion | optional | Только отдельным решением пользователя; это системная настройка безопасности | user approval |
| Проверить после перезагрузки | pending | Снять I/O-счетчики в первые 1-2 минуты после старта | next reboot |
## 2026-07-20 STAS5 V5C Review Overlay

Статус: `done`.

`*_ANNOTATED.png` теперь является рабочим графиком для проверки продиктованной review-команды: поверх цены видны `GOOD/BAD/RISK BAD`, а нижние полосы `Fon/LONG/SHORT/WAVE` сохранены. `*_ALL_ENTRIES.png` остается чистой копией V5C visual review без overlay.

## Todo 2026-07-22 Codex Update Load Audit

Статус: `CODEX_UPDATE_LOAD_AUDIT_RELIEF_APPLIED_NO_DELETE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Проверить версию Codex после обновления | done | `OpenAI.Codex_26.715.10079.0` | appx audit |
| Учесть новое имя UI-процессов | done | Главный UI теперь `ChatGPT.exe`, его тоже нужно прижимать | process audit |
| Остановить VS Code Codex extension server | done | Текущий `openai.chatgpt-26.715.31925...\codex.exe app-server` остановлен; расширение не удалялось | VS Code |
| Понизить приоритет Codex/ChatGPT/VS Code | done | `ChatGPT`/`codex`/`Code`/`node_repl` выставлены в `Idle` | current session |
| Проверить Git | done | Активных `git.exe` нет, `.git/index.lock` нет, `git status ~52 ms` | repo state |
| Сделать постоянное отключение VS Code OpenAI extension | optional | Только отдельным решением пользователя, без удаления файлов | user approval |

## Todo 2026-07-23 Codex VS Code Fix

Статус: `CODEX_VSCODE_EXTENSION_RESTARTED_NO_DELETE`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Восстановить панель Codex в VS Code | done | Сервер расширения перезапущен штатной кнопкой | VS Code UI |
| Не ломать VS Code Codex разгрузкой | done | Не останавливать extension server, если панель нужна рабочей | process policy |
| Держать Codex легким | done | `ChatGPT`/`codex` выставлены в `Idle`; watcher/search/Pylance исключения уже есть | current session |
| Проверить после следующей перезагрузки | pending | Снять срез CPU/I/O в первые 1-2 минуты после старта | next reboot |

## Todo 2026-07-23 STAS9 Shortcut And CPU Fix

Статус: `STAS9_VSCODE_SHORTCUT_FIXED`.

| Task | Status | Next Action | Depends On |
|---|---|---|---|
| Убрать терминал из пользовательского запуска STAS9 | done | Оба ярлыка ведут в VS Code workspace | desktop shortcuts |
| Остановить ошибочный terminal launcher | done | Точное дерево процессов остановлено | current session |
| Снизить фоновое чтение при открытии | done | Лёгкая активация и исключения Git/Pylance включены | workspace settings |
| Проверить старый по имени ярлык | done | Открылось окно VS Code, терминал отсутствует | smoke test |
| Контроль после перезагрузки Windows | optional | Если шум вернётся, проверить первые 1–2 минуты без AIDA64 и Диспетчера задач | next reboot |
