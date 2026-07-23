# Known Errors

## Codex Desktop Git Review Storm 2026-07-23

Статус: `LOCAL_WORKAROUND_EFFECTIVE_UPSTREAM_REGRESSION_REMAINS`.

После обновления `26.715.10079.0` Codex Desktop циклически запускал
Git snapshot/review над большим незакоммиченным состоянием. До ремонта:
`112 git.exe` и `86 taskkill.exe` за `8` секунд. Локальный обход выполнен:
репозиторий приведён к чистому checkpoint, включены Git performance caches,
workspace watcher/indexing ограничены.

Дополнительно найдены два повреждённых loose-объекта Git:
`293cbe267e6c17b6d19aba9d1ad964f380962566` и
`4dc706bd74e10812504051bfad490a64178ee125`. Они не входят ни в одну
ветку/тег/remote ref и перенесены без удаления в
`.git/corrupt-object-backup-20260723`. После этого полный `git fsck` проходит.

Финальный контроль: `0` новых Git и `0` taskkill за `15` секунд. Сам дефект
Codex Desktop остаётся внешним: при появлении большого незакоммиченного diff
он может проявиться снова. Практическое правило — небольшие тематические
коммиты и хранение generated artifacts только в уже игнорируемых каталогах.

## SOL Event Pipeline Design 2026-07-23

Статус: `NO_NEW_ERRORS_EXPECTED_DESIGN_GAPS_RECORDED`.

Source gate, EVENT contract и in-memory schema dry-run прошли. Реальные
события и datasets намеренно не создавались.

Ожидаемые незакрытые элементы, не являющиеся ошибкой текущего этапа:

1. detector thresholds и точные причинные окна не утверждены;
2. для local extrema, false breakout и reversal не утверждены правила
   confirmation и различие `timestamp/detected_at`;
3. feature, outcome, label и split contracts отсутствуют;
4. старый `EVENTS/EVENT_SOL_000001.yaml` остаётся
   `TEMPLATE_NOT_OBSERVED` и не соответствует новому контракту; он сохранён
   без изменения и не является событием.

До закрытия этих пунктов записывать реальные event YAML и строить dataset
нельзя.

## STAS9 VS Code On-Demand Workflow 2026-07-23

Статус: `NO_BLOCKING_ERRORS`.

На приложенном снимке текущая нагрузка приходилась главным образом на
`Antimalware Service Executable` и `WMI Provider Host`; `conhost.exe` имел
нулевую нагрузку, а `rg.exe` был кратковременным поиском. После настройки
постоянных STAS9/Python/Optuna/rg процессов, службы, задания планировщика и
записи автозагрузки не обнаружено.

Неблокирующая ручная проверка: один раз открыть `🤖 STAS9 Workspace` и
визуально подтвердить открытие панели Codex. Автоматически новый экземпляр VS
Code не запускался, чтобы не создавать дополнительную нагрузку и не менять
текущую пользовательскую сессию.

## STAS9 Agent Roles and SOL Preparation 2026-07-23

Статус: `NO_NEW_ERRORS`.

Новый агент, маршрутизаторы, память, event template и dataset pipeline прошли
структурную проверку. `EVENT_SOL_000001.yaml` — только шаблон
`TEMPLATE_NOT_OBSERVED`; его нельзя считать найденным событием или включать в
dataset.

Фактический путь и временной диапазон выгруженных свечей SOL в текущем ТЗ не
заданы, поэтому рыночный анализ намеренно не запускался. Это ожидаемая граница,
а не ошибка.

## STAS9 Persistent Memory 2026-07-23

Статус: `NO_NEW_ERRORS`.

Файлы `STAS9_CONTROL_PLANE/MEMORY/STAS9_STATE.md` и
`STAS9_CONTROL_PLANE/START_HERE_RU.md` созданы и читаются как UTF-8.

Архитектурная граница сохранена: текущий control plane готов, но
`schemas/adapters/gates/run_plans` ещё не реализованы. Старые
`BROKEN_POINTER`, отсутствующие определения STAS6/STAS7 и выключенный
STAS8-preview не исправлялись и остаются известными состояниями.

## STAS9 VS Code/Codex Interface 2026-07-23

Статус: `NO_BLOCKING_ERRORS`.

В расширении Codex для VS Code не обнаружена документированная встроенная команда диктовки. Голосовой ввод реализован без отдельного приложения через системную диктовку Windows `Win+H` в поле Codex.

Автоматически проверить физический микрофон и его разрешение Windows из setup-процесса нельзя. Workspace, Codex extension, формат ответа и текстовый маршрут проверены программно.

## STAS9 Codex Runtime 2026-07-23

Статус: `MODEL_VERSION_ERROR_RESOLVED`.

Ошибка `gpt-5.6-sol model requires a newer version of Codex` устранена обновлением CLI `0.142.5 -> 0.145.0`.

Неблокирующие предупреждения диагностики:

1. `codex doctor` видит две старые несогласованные записи thread/rollout;
2. shell snapshot для PowerShell пока не поддерживается;
3. два plugin icon path проигнорированы.

Они не препятствуют запуску `gpt-5.6-sol`; smoke-проверка завершилась `PASS`.

## STAS9 Multi-Agent Control Layer 2026-07-23

Статус: `NO_NEW_OPEN_ERRORS`.

Windows Script Host не смог напрямую создать `.lnk` с эмодзи в имени. Ярлык был безопасно создан под временным ASCII-именем в той же папке и переименован; после обратной проверки target и working directory совпали. Временный файл отсутствует.

Старый `BROKEN_POINTER` остаётся известной проблемой и намеренно не исправлялся.

## STAS9 Multi-Agent Structure 2026-07-23

Статус: `NO_NEW_ERRORS`.

Все `15` заданных каталогов созданы и подтверждены. Пропусков и лишних каталогов внутри созданного дерева нет. Изменений STAS5–STAS8 не обнаружено.

## STAS9 Audit Findings 2026-07-23

Статус: `KNOWN_GOVERNANCE_GAPS_REGISTERED_NO_AUTOFIX`.

1. `models/registry/active_model.json` и `models/registry/champion.json` указывают на отсутствующий файл:

```text
models/pipeline/champion_candidate_logreg_SOLUSDT_1m_20260521T131603Z.joblib
```

Класс: `BROKEN_POINTER`. Влияние: старый общий production/active pointer нельзя считать исполнимым. Автоматический fallback запрещен.

2. `models/registry/candidates.jsonl`: `6496` записей, `6236` уникальных model paths, `260` повторных записей, `193` уникальные ссылки на отсутствующие файлы. Все `6043` существующих legacy pipeline joblib зарегистрированы хотя бы одной записью.

3. STAS6 и STAS7 не имеют самостоятельных каталогов, ТЗ, контрактов и моделей. Класс: `MISSING_VERSION_DEFINITION`.

4. STAS8 вложен в STAS5 и текущим preview слишком жестко понижает решения. Класс: `DISABLED_AUDIT_PREVIEW_NOT_PRODUCTION`.

5. Одновременно существуют X439 и X463. Выбор модели по имени файла без manifest/allowlist может привести к несовместимости признаков.

Исправления не выполнялись, потому что текущая задача разрешала аудит и создание STAS9, но запрещала изменение STAS5–STAS8 и не разрешала production promotion.

## Fixed 2026-07-23 Codex Git Scan CPU Loop

Статус: `fixed_generated_stas4_scan_surface_reduced`.

Codex Desktop циклически запускал `git hash-object`/`git diff --no-index` по generated-файлам `STAS4_FEATURE_HYPOTHESIS_REVIEW`, из-за чего одновременно росла нагрузка `codex.exe` и Defender. Это не было обучением STAS5.

Исправлено точечными `.gitignore` и VS Code watcher/search/Pylance exclusions. Ничего не удалено. После перезапуска Windows приоритет `Idle` сбрасывается, но файловые исключения сохраняются. Не добавлять исключение Defender без отдельного разрешения пользователя.

## Visual Format Note 2026-07-22 Base R2-Style Gallery

Статус: `no_error_expected_visual_difference`.

Для базы `2026-01-27..2026-02-27` теперь есть новый R2-style visual слой. Он отличается от старого `FULL_CAUSAL_STRUCTURE_MAP_V1`: старый график показывал причинную структуру, новый показывает teacher-входы в формате review. Это не меняет CSV базы и не запускает ML. Если нужны менее шумные картинки, открывать `*_ALL_ENTRIES.png`; если нужно видеть teacher GOOD/BAD поверх входов, открывать `*_CURRENT_REVIEW.png`.

Папка:

```text
STAS5_ML_CORE/artifacts/v5c/review/_BASE_R2_STYLE_VISUAL_REVIEW_20260127_20260227
```

## Visual Check Note 2026-07-22 BASE/R2/R3/R4 Pack

Статус: `no_error_visual_pack_ready`.

Единый пакет графиков `BASE + R2/R3/R4` собран без ошибок и без запуска обучения/forward. Важное отличие форматов: базовые `2026-01-27..2026-02-27` используют старый `FULL_CAUSAL_STRUCTURE_MAP_V1` с teacher `entry_y`, а R2/R3/R4 используют текущую review-визуализацию с ENTRY/RiskGate кругами и CSV рядом. Это не баг, а различие источников визуализации.

Папка:

```text
STAS5_ML_CORE/artifacts/v5c/review/_ENTRY_VISUAL_CHECK_CURRENT_20260127_20260320
```

## Known Tuning Risk 2026-07-22 R4BB Tables PASS But ML Quality Still Weak

Статус: `guardrail_active_not_a_table_corruption`.

Аудит `stas5_v5c_r4bb_train_20260127_20260320` не нашел фатального table/target/feature bug: R2/R3/R4 approved review попал в ENTRY и RiskGate datasets, X463/Bollinger признаки есть в allowlist/joblib, target/manual/future/STAS8 preview поля в X не входят, guards PASS.

Оставшаяся проблема является качественной/tuning-проблемой, а не доказанной порчей таблиц: ENTRY OOF слабый, two-block обучен, но не выбран quality gate, RiskGate с `risk_bad_y=400` против `risk_ok=227` выбрал низкий block threshold `0.2274967503` и склонен блокировать широко. STAS8/move-capacity пока preview, его нельзя считать финальным фильтром или обученной моделью.

Мелкий нефатальный metadata-дефект: `2026-03-01/LA047` имеет `entry_from_risk_bad=0` в ENTRY metadata, хотя RiskGate review помечает `RISK_BAD`; targets корректные (`entry_y=0`, `risk_bad_y=1`). Это не ломает обучение, но можно почистить отдельно.

## Fixed Visual Error 2026-07-22 STAS8 Soft V2 Green Circles Mixed Audit And Live

Статус: `fixed_visual_semantics_2026_07_22`.

Пользователь справедливо указал, что STAS8 Soft V2 PNG были визуально неверными: зеленый круг означал одновременно live `ENTER`, защищенный `WATCH` и offline `SKIP->RECALL_WATCH`. Это смешивало торговый сигнал с подсказкой после факта.

Исправлено: зеленый круг на цене теперь означает только финальный live `ENTER` после STAS8. Красный квадрат означает исходный `ENTER`, пониженный в `WATCH`. Красный круг означает hard block. `RECALL_WATCH` для исходного `SKIP` остается в CSV/отчете как offline-аудит, но не рисуется зеленым кругом.

Guard усилен check `soft_v2_visual_markers_match_live_semantics`; пересборка R5 дала `failed_count=0`, `checks=18`.

## Known Tuning Risk 2026-07-22 STAS8 Soft V2 Needs Visual Selection

Статус: `guardrail_active_needs_down_channel_tuning`.

`STAS8_SOFT_CAPACITY_V2` прошел guard на R5 `2026-03-21..2026-03-27`, но это еще не production-фильтр. Режимы дают разную жесткость:

```text
strict:   ENTER=2,  WATCH=118, SKIP=444
balanced: ENTER=15, WATCH=152, SKIP=397
wide:     ENTER=36, WATCH=161, SKIP=367
```

Риск `strict`: снова задушить хорошие отскоки. Риск `wide`: пропустить лишние long-входы внутри down-channel. Текущий главный кандидат - `balanced`, но он требует ручного просмотра по PNG, особенно `2026-03-26` и `2026-03-27`.

После визуальной проверки 2026-03-26/2026-03-27: `balanced` читается честнее, но все еще оставляет 1 live `ENTER` на 2026-03-26 в падающем канале; `wide` оставляет 9 live `ENTER` на 2026-03-26 и потому слишком мягкий для down-channel. Следующий шаг - tuning down-channel/no-long и post-knife rebound, а не обучение.

Запрещено: брать `RECALL_WATCH`, `*_TEACHER_GOOD_*`, `hit_*`, `future_*`, `time_to_*`, `mae_*` как live-признаки или live-решение. Эти поля только для offline audit и разметки просмотра.

Техническая заметка: в папке могут оставаться старые пробные contact sheets с диапазоном в имени от ранней ручной сборки. Рабочий manifest ссылается на короткие файлы `STAS8_SOFT_V2_STRICT/BALANCED/WIDE_CONTACT_SHEET.png`; старые файлы не удалялись без прямого разрешения пользователя.

## Known Tuning Risk 2026-07-22 STAS8 V1 Blocks Good Rebounds

Статус: `guardrail_active_for_stas8_v2_before_train_or_enforce`.

Аудит R5 `2026-03-21..2026-03-27` показал, что текущий `STAS8_MOVE_CAPACITY_AUDIT_V1` нельзя включать как боевой фильтр:

```text
before STAS8: ENTER=61, WATCH=166, SKIP=337
after STAS8 preview: ENTER=1, WATCH=20, SKIP=543
all hit_1p2=119
original ENTER/WATCH hit_1p2=46
original SKIP hit_1p2=73
blocked good ENTER/WATCH hit_1p2=40
kept bad ENTER/WATCH without hit_1p2=15
```

Корень ошибки: V1 хорошо режет `NO_MOVE`, `LOW_MOVE_CHOP`, `NO_MOVE_DOWN_CHANNEL`, но слишком грубо режет `HIGH_VOL_DANGER`, `MOVE_OK_1P5`, `POST_KNIFE_RETEST_EDGE` и `SPIKE_EXTREME`. Это убивает низы после ножа и первые рабочие отскоки.

Запрещено до нового OK: запускать train/forward с STAS8 V1 как enforce, добавлять R5 в train без ручного review, использовать `future_* / hit_* / time_to_* / mae_*` как live X.

Разрешено: делать read-only preview `STAS8_SOFT_CAPACITY_V2` и сравнивать графики/CSV.

Отчет:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1/STAS5_V5C_STAS8_R5_ENTRY_MOVE_AUDIT_20260321_20260327_RU.md
```

## Known Visual Confusion 2026-07-22 STAS8 R5 Bollinger Overlay Removed

Статус: `fixed_visual_only_2026_07_22`.

Пользователь справедливо отметил, что Bollinger-полосы на STAS8-preview графиках мешали разбирать движение цены и могли путать STAS8 block с Bollinger/RiskGate. В `src/mlbotnav/stas5_v5c_stas8_move_capacity_audit.py` для STAS8-визуализации установлен `bollinger_preview=False`, а R5 PNG пересобраны.

Граница безопасности: это только визуальная правка. `bb20_*` признаки X463, train datasets и forward dataset не удалялись и не менялись; RiskGate не включался; predictions CSV не переписывался.

## Known Tuning Risk 2026-07-22 STAS8 Preview Too Strict

Статус: `guardrail_active_for_stas8_audit_preview`.

`STAS8_MOVE_CAPACITY_AUDIT_V1` на R5 `2026-03-21..2026-03-27` прошел guard, но текущие rule-пороги нельзя считать финальным production-фильтром:

```text
before STAS8: ENTER=61, WATCH=166, SKIP=337
preview after STAS8: ENTER=1, WATCH=20, SKIP=543
```

Это ожидаемый tuning-риск: слой хорошо подсвечивает down-channel/no-long и high-vol danger, но может задушить хорошие rebound/local-low входы. Запрещено включать STAS8 в train/forward/enforce без отдельной визуальной настройки и нового guard.

Обязательные границы остаются активными: исходный predictions CSV не перезаписывать, R5 не добавлять в train до ручного review, teacher `future_* / hit_* / time_to_* / mae_*` не использовать как live X.

## Fixed Cosmetic 2026-07-22 R4BB Guard Names No Longer Say X439

Статус: `fixed_2026_07_22`.

В run `stas5_v5c_r4bb_train_20260127_20260320` аудит показал, что фактические dataset paths, allowlists, manifests и `.joblib` используют X463 с `24` `bb20_*` признаками. Старые человекочитаемые/check names были переименованы:

```text
riskgate_features_x439
feature_count_439
market_phase_state_ml_uses_only_x439
entry_ml_uses_x439_plus_oof_predictions_only_on_train
```

Теперь в коде и текущих R4BB guard/manifests используются нейтральные имена `feature_count_expected`, `*_match_training_allowlist`, `*_causal_feature_allowlist*`. Это была косметическая проблема названий, не ошибка обучения.

## Fixed Config Risk 2026-07-22 Active Context Train Points To R4BB

Статус: `fixed_2026_07_22`.

После успешного train `stas5_v5c_r4bb_train_20260127_20260320` файл:

```text
STAS5_ML_CORE/artifacts/v5c/model/STAS5_V5C_LATEST_TWO_BLOCK_MODEL_RUN.json
```

указывает на новый `r4bb` / X463 run. Но в управляющем YAML:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

блок `active_context.train` теперь указывает на `stas5_v5c_r4bb_train_20260127_20260320` / X463. JSON snapshot пересобран из YAML. Старый R3/X439 больше не является active train.

Актуальный forward можно запускать с manifest:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r4bb_train_20260127_20260320/STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json
```

## Known Guardrail 2026-07-22 Bollinger Layer V1 Is Causal X463, Preview Columns Are Not X

Статус: `guardrail_active_for_bollinger_layer_v1`.

С 2026-07-22 есть два разных Bollinger-режима, их нельзя путать:

```text
старый R5 BB_BLOCK_V0 / BOLLINGER20_2SIGMA_PREVIEW = только PNG/audit preview
новый BOLLINGER_LAYER_V1 = причинные bb20_* features в train/forward contract X439_PLUS_BB24_V1
```

Новый ML-контракт при включенном `-EnableBollingerLayer`: `463` features. В X входят только `bb20_*` числовые causal признаки. Запрещено включать в X: `bb_preview_block`, `bb_preview_reason`, `bb_preview_block_score`, `bb_preview_blocked_manual_good`, `bb_preview_blocked_manual_bad`, `entry_y`, `risk_bad_y`, review/manual/future/MFE/MAE.

Guard обязан держать `bb_source_time_utc <= entry_time_utc`. Если training/forward использует модель с `X463`, forward dataset тоже должен собрать `bb20_*`; нельзя подавать модели старый `X439`.

## Known Guardrail 2026-07-22 Bollinger Preview Is Visual Only

Статус: `guardrail_active`.

Графики Bollinger `20/2` по `2026-03-21..2026-03-27` являются только визуальным preview поверх готового `DOWN_CHANNEL_NO_LONG_V1`. Нельзя считать их новым обучением, forward, RiskGate enforce или изменением X439.

Дополнение: `BB_BLOCK_V0` с красными кругами в R5 no-risk папке тоже является только visual-preview. Он помечает, какие `ENTER/WATCH` были бы заблокированы по Bollinger-условиям, но не переписывает `ENTRY_ML_LIVE_DECISION`, не меняет predictions CSV и не является обученной моделью.

Запрещено для старого preview: считать PNG самостоятельным обучением, использовать будущие свечи для расчета полос на момент входа, менять decisions по картинке, запускать новый train только из-за картинки. Bollinger-колонки разрешены только через новый `BOLLINGER_LAYER_V1` с отдельным `X463` allowlist и no-future guard.

Разрешено сейчас: смотреть PNG, обсуждать, помогает ли нижняя/средняя/верхняя полоса понять интересные входы, и отдельно проектировать causal STAS8/move-capacity слой.

## Known Guardrail 2026-07-22 ENTRY-Only Wide Is Not Final Safety

Статус: `guardrail_active`.

`ENTRY-only WideReview` нужен для раздушенного просмотра кандидатов, а не для production-входа. В этом режиме RiskGate намеренно отключен, поэтому нельзя считать результат финальным безопасным сигналом.

Правильный порядок: сначала получить больше ENTRY-кандидатов, затем глазами/аудитом понять, что режем: входы на хаях, short-channel, dead-flat/no move `1.2%`, down-channel. Только потом накладывать RiskGate / STAS8 / safety-layer.

## Known Guardrail 2026-07-22 STAS8 Is Deferred Only

Статус: `guardrail_active`.

`STAS8_MOVE_CAPACITY_GRID_V1` на `2026-07-22` является только отложенным ТЗ. Нельзя случайно включать его в train/forward, добавлять live признаки из будущего или менять текущий R4/R5 pipeline без отдельного OK.

Новая фиксированная трактовка: STAS8 сначала подтверждает live long-режим (`ALLOW_ENTRY_SEARCH / WAIT / BLOCK`), а не берет future `hit_1p2` как live-фильтр. R2/R3/R4 можно использовать для train после approved review; R5 `2026-03-21..2026-03-27` остается blind-forward/audit-preview до ручного review.

Разрешено: читать ТЗ, обсуждать сетку процентов, проектировать future offline teacher labels и live wave context. Запрещено без отдельного OK: писать боевой STAS8 код, пересобирать датасеты под него, запускать обучение или forward с этим блоком.

## Known Guardrail 2026-07-21 Down-Channel Safety Pulse Is Preview Only

Статус: `guardrail_active_for_down_channel_safety_pulse_preview`.

`DOWN_CHANNEL_NO_LONG_V1` сейчас является только preview/test-drive поверх готового forward `2026-03-21..2026-03-27`. Он не является боевым enforce и не является новым обучением.

Разрешено смотреть PNG/CSV в `safety_pulse_preview/down_channel_no_long_v1` и вручную отмечать, где пульс все еще пропускает плохой long или режет хороший rebound.

Запрещено до визуального OK: запускать новый Train как решение проблемы, встраивать `DOWN_CHANNEL_NO_LONG_V1` в боевой forward/enforce, считать future/MFE/MAE live features, смешивать `risk_bad_y/entry_y/review labels` с X439.

Текущий кандидат для просмотра: `DOWN_CHANNEL_NO_LONG_V1`, а не старый `HARD_BLOCK_ONLY_V1`. Последний preview дал `ENTER=40`, `WATCH=136`, `SKIP=388`; `2026-03-26` срезан до `ENTER=4`, `2026-03-27` до `ENTER=7`.

## Known Guardrail 2026-07-21 Do Not Retrain Before Safety Pulse Visual OK

Статус: `guardrail_active_for_safety_pulse_preview`.

После forward `2026-03-21..2026-03-27` нельзя сразу запускать новое долгое обучение только потому, что результат плохой. Сначала нужно визуально согласовать safety pulse на готовых PNG:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4_forward_20260321_20260327_wide_v1/safety_pulse_preview/
```

Текущий кандидат для просмотра: `HARD_BLOCK_ONLY_V1`. Он оставляет больше входов, чем `BALANCED_SAFETY_V1`, но hard-block режет смертельные taxonomy-режимы. До пользовательского OK запрещено встраивать этот пульс в боевой forward/enforce и запрещено запускать новый train как решение проблемы.

## Known Guardrail 2026-07-21 RiskGate ML Must Be Trained Before Forward Enforce

Статус: `guardrail_active_for_riskgate_ml_train_wiring`.

После текущей правки `RISKGATE_ML` подключен к `-Mode Train` и будущему forward, но до ручного запуска Train он еще не является сохраненной моделью. Нельзя запускать forward/enforce, пока в train manifest нет:

```text
riskgate_ml_status=PASS_V5C_RISKGATE_ML_TRAINED_POST_TRAIN_GUARD_READY_FOR_FORWARD
riskgate_ml_post_train_guard_status=PASS_V5C_RISKGATE_ML_POST_TRAIN_GUARD_READY_FOR_FORWARD
```

Обязательное правило forward: исходное ENTRY-решение сохранять в `ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE`, а финальное `ENTRY_ML_LIVE_DECISION` менять только после PASS RiskGate post-train guard. `risk_bad_y`, `entry_y`, review/manual/future/outcome не могут быть live features.

## Known Guardrail 2026-07-21 Train Only From 20260127-20260320 PASS Batch

Статус: `guardrail_active_after_dataset_build`.

Для следующего обучения нельзя использовать старые batch-диапазоны `20260127_20260306` или `20260127_20260313`, если цель - применить все правки R2/R3/R4. Нужен именно:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_ML_READY_439F_TARGETS_V1.csv
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260320_GUARD_V1.json
```

Guard должен быть `PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING`, а отдельный TrainingGuard - `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`.

RiskGate dataset лежит отдельно и не является feature для ENTRY:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_X439_RISK_BAD_Y_V1.csv
```

Запрещено считать `risk_bad_y=0` по всем строкам без слова риск. В V1 safe-негативы RiskGate только explicit ENTRY GOOD `227`.

## Known Guardrail 2026-07-21 Dataset Rails Before Training

Статус: `guardrail_active_for_v5c_dataset_rails`.

Нельзя запускать training сразу после approved review-pack. Сначала должны появиться и пройти guards:

```text
X439_SOURCE
ENTRY_TRAIN_DATASET
RISKGATE_TRAIN_DATASET
```

Нельзя брать ML-источник из PNG, `_ALL_ROUNDS_VISUAL_REVIEW`, loose review folders, draft-файлов или визуальных CSV-копий. Официальный teacher source для R2/R3/R4 только:

```text
STAS5_ML_CORE/artifacts/v5c/review/_APPROVED_REVIEW_PACKS/STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1/
```

`risk_bad_y` не является feature. `risk_bad_y=1` всегда должен одновременно давать `entry_y=0`; иначе ENTRY не научится, что этот вход плохой. Для RiskGate отрицательные примеры V1 брать только из явно безопасных/GOOD, а не из всех строк без слова `риск`.

## Known Guardrail 2026-07-21 Use Approved Review Pack, Not Loose Review Folders

Статус: `guardrail_active_for_v5c_review_pack_r2_r3_r4`.

После закрытия R2/R3/R4 нельзя вручную собирать обучение из разрозненных дневных PNG, `_ALL_ROUNDS_VISUAL_REVIEW` или случайных draft-файлов. Официальный пакет ручной разметки:

```text
STAS5_ML_CORE/artifacts/v5c/review/_APPROVED_REVIEW_PACKS/STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1/
```

Только эти два CSV являются сводным teacher/target-входом для следующей сборки:

```text
entry/STAS5_V5C_R2_R3_R4_ENTRY_REVIEW_APPROVED_ALL_V1.csv
riskgate/STAS5_V5C_R2_R3_R4_RISKGATE_REVIEW_APPROVED_ALL_V1.csv
```

Запрещено: считать `CURRENT_REVIEW.png` обучающим источником, пускать `entry_y`, `risk_bad_y`, `entry_review_label`, `risk_review_label`, `user_text_raw`, `phase_y`, `state_y`, `reason_y` в live `X439`, обучать без PASS guard.

Обязательное правило: `риск плохо` всегда должно оставаться двойной целью `entry_y=0 + risk_bad_y=1`. Если RiskGate BAD не является ENTRY BAD, это ошибка сборки.

## Known Guardrail 2026-07-20 PNG Is Not ML Source

Статус: `guardrail_active_for_current_review_cleanup`.

`*_CURRENT_REVIEW.png` нужен только для визуальной проверки. ML не должен учиться по PNG и не должен выбирать между несколькими картинками. Источник обучения/review-цифр: `*_USER_REVIEW_*_APPROVED.csv`, `*_USER_RISKGATE_REVIEW_*_APPROVED.csv`, `*_REVIEW_LADDER_*_APPROVED_RESULT.json` и `*_CURRENT_VISUAL_MANIFEST_V1.json`.

Если в `_visual_archive` есть старые preview PNG, это история для проверки, а не active source-of-truth.

## Known Guardrail 2026-07-20 Review Labels Are Visual Only

Статус: `guardrail_active_for_review_label_overlay`.

Подъем `LAxxx` над кругами/квадратами в review-графиках не меняет CSV, targets, модельные признаки, решения ENTRY или RiskGate. Это только порядок и смещение отрисовки в PNG.

Запрещено трактовать пересобранную `_ALL_ROUNDS_VISUAL_REVIEW` как новое обучение или новый forward. После пользовательских правок по конкретному дню все равно нужен отдельный `run_stas5_v5c_review_ladder.ps1` для сохранения review-ledger.

## Known Guardrail 2026-07-20 Review Gallery Is Visual Only

Статус: `guardrail_active_for_review_gallery`.

`STAS5_ML_CORE/artifacts/v5c/review/_ALL_ROUNDS_VISUAL_REVIEW/` нельзя считать новым обучением, новым forward или новым day passport. Это только общая витрина PNG/CSV для ручной проверки R2/R3/R4.

После правок пользователя нужно отдельно запускать review ladder для конкретного дня. Только после закрытия дня/недели и отдельного guard можно обсуждать пересборку batch/training.

## Known Guardrail 2026-07-20 ENTRY/RiskGate Targets Must Stay Separate

Статус: `guardrail_active_for_entry_riskgate_two_targets`.

Нельзя учить RiskGate через текстовые комментарии или подмешивать `риск плохо` в live `X439`. Нельзя превращать `risk_bad_y` в feature для ENTRY. Нельзя считать, что `risk_bad_y` заменяет `entry_y`.

Правильная схема: ENTRY получает `entry_y`; RiskGate получает отдельный `risk_bad_y`. Если пользователь говорит `риск плохо`, эта строка становится `entry_y=0 + risk_bad_y=1`. Оба слоя смотрят только причинные данные `X439`; ручные метки используются только как teacher/target/audit при обучении и проверке.

Если один и тот же LA опасный как риск, отдельная запись `LAxxx риск плохо` уже означает и плохой ENTRY-пример, и плохой RiskGate-пример. Не нужно дублировать `LAxxx плохо; LAxxx риск плохо`, если смысл именно один: опасный плохой вход.

Отсутствие `риск плохо` нельзя автоматически трактовать как `risk_bad_y=0` для всей таблицы. RiskGate builder должен отдельно определить, какие строки являются подтвержденными безопасными/негативными примерами, иначе можно обучить блок на ложной безопасности.

## Known Guardrail 2026-07-20 V5C Review Ladder ENTRY And RiskGate Split

Статус: `guardrail_active_for_v5c_quick_review_ladder`.

Нельзя смешивать обычную ENTRY-разметку и RiskGate-разметку в один target:

```text
хорошо / плохо без слова риск -> ENTRY teacher
риск плохо -> RiskGate teacher
риск хорошо -> запрещено
```

`риск плохо` должен автоматически становиться ENTRY BAD и RiskGate BAD: `entry_y=0 + risk_bad_y=1`. Ручные поля `user_text_raw`, `entry_review_label`, `risk_review_label`, `risk_user_hint`, маркеры и комментарии являются teacher/audit слоем и не могут попадать в live `X439`.

Approved review artifacts нельзя перезаписывать без `-Force`.

## Known Guardrail 2026-07-20 RiskGate Taxonomy Is Explanation Layer

Статус: `guardrail_active_for_v5c_riskgate_taxonomy_v1`.

`RISK_GATE_TAXONOMY_V1` не является новой entry-моделью и не должен подменять `RISK_GATE_STATUS`. Режимы `PRE_DUMP_RISK/ACTIVE_DUMP/FALLING_KNIFE/.../LIQUIDATION_CASCADE` объясняют, почему вход опасный, а действие по-прежнему задается отдельной лестницей:

```text
PASS_RISK
WARN_RISK
BLOCK_RISK
BLOCK_HARD
PASS_USER_REBOUND
```

Запрещено сейчас: переводить taxonomy напрямую в production enforce, менять `ENTRY_ML_LIVE_DECISION`, добавлять ручные review-метки или future outcome в live X. Разрешено сейчас: audit-only CSV/PNG/report поверх готового forward с проверкой `RISK_NO_FUTURE_OK`.

## Known Guardrail 2026-07-20 RiskGate Is Audit-Only

Статус: `guardrail_active_for_v5c_riskgate_audit_only`.

RiskGate V0 реализован, но только как `audit_only`. Нельзя считать его боевым фильтром и нельзя менять production `ENTRY_ML_LIVE_DECISION` без отдельного будущего этапа `enforce`.

Разрешено сейчас:

```text
ENTRY_BASELINE_ML predictions -> RiskGate audit CSV/PNG/RU.md
```

Запрещено сейчас:

```text
RiskGate меняет ENTRY_ML_LIVE_DECISION
RiskGate используется как training feature
ручные USER_PASS становятся live X
enforce без отдельного guard PASS
```

Пользовательские `USER_PASS` (`LA059`, `LA067`, `LA078`) являются review overlay/teacher material для будущего правила rebound/retest, а не live-признаками.

## Known Guardrail 2026-07-20 RiskGate Preview Is Not Enforce

Статус: `guardrail_active_for_riskgate_preview_20260318`.

RiskGate preview по `2026-03-18` является только audit-only визуализацией и таблицей. Нельзя считать, что `BLOCK_HARD/BLOCK_RISK/WARN_RISK` уже меняют реальные `ENTRY_ML_LIVE_DECISION` или production-сигналы.

Артефакт:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r3_forward_20260314_20260320_wide_v1/riskgate_preview/20260318/
```

Правило дальше: сначала пользователь проверяет RiskGate-вставки глазами, затем можно делать кодовый `audit_only` overlay и отдельный guard. Enforce запрещен без отдельного PASS и ручного подтверждения, что хорошие rebound/retest-входы не убиваются.

Уточнение после проверки V1: `LA059`, `LA067`, `LA078` пользователь отметил как проходящие входы. Поэтому будущий RiskGate обязан иметь исключения для rebound/retest/grounding после дампа. Нельзя делать боевой фильтр только по `knife=1` или `active_dump=1`, иначе он заблокирует хорошие входы после приземления.

## Known Guardrail 2026-07-20 V5C ENTRY_ML_TWO_BLOCK Is Frozen

Статус: `guardrail_active_for_v5c_entry_two_block_frozen`.

`ENTRY_ML_TWO_BLOCK` не удален, но заморожен в YAML: `enabled=false`, `mode=frozen_not_selected`. Не тратить время на его дообучение/подбор как следующий шаг и не считать его active entry model. Текущий active entry - `ENTRY_BASELINE_ML`; следующий safety-шаг - `RISK_GATE_RULE_V0 audit_only`.

## Known Guardrail 2026-07-20 V5C YAML Comments Are Documentation Only

Статус: `guardrail_active_for_v5c_yaml_comments`.

Русские комментарии в `STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml` помогают читать и управлять ML-блоками, но не являются executable logic. Нельзя считать, что RiskGate или другой блок включился только из-за комментария. До отдельного code wiring раннеры YAML автоматически не читают.

## Known Guardrail 2026-07-20 V5C YAML Is The Only Manual ML Control Source

Статус: `guardrail_active_for_v5c_yaml_control`.

После перехода на удобный управляемый config нельзя руками править разные источники параллельно. Главный source-of-truth:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

`STAS5_V5C_ML_CONTROL_CONFIG_V1.json` и `STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md` являются справочными файлами. Если дальше код начнет читать config, он должен читать YAML. Нельзя включать `RISK_GATE_RULE_V0.enforce` или менять active entry model через JSON/RU.md.

## Known Guardrail 2026-07-19 V5C RiskGate Must Start Audit Only

Статус: `guardrail_active_for_v5c_riskgate`.

После forward week3 пользователь указал опасную зону активного дампа, где текущий ENTRY может давать long-входы в сильный short/knife режим. Нельзя чинить это скрытым изменением ENTRY, подмешиванием future outcomes в X или немедленным боевым RiskGate.

Правильная рельса зафиксирована в:

```text
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json
STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
```

RiskGate V0 должен стартовать только как `audit_only` overlay: он помечает `PASS_RISK/WARN_RISK/BLOCK_RISK` и `WOULD_BLOCK/WOULD_DEMOTE`, но не затирает текущий `ENTRY_ML_LIVE_DECISION`. В X RiskGate можно брать только причинные risk columns из X439 и текущий alpha score/decision. `entry_y`, `phase_y`, `state_y`, `reason_y`, ручные комментарии, future/postfact/hit/MAE/MFE запрещены как live features.

Перевод в enforce разрешен только после отдельного RiskGate guard PASS и ручной проверки, что блокируются active-dump/knife входы, но не убиваются хорошие `GOOD_FLUSH_REBOUND` и `GOOD_RETEST_AFTER_KNIFE`.

## Known Guardrail 2026-07-17 V5C R3 Must Use 20260127..20260313 Batch

Статус: `guardrail_active_for_v5c_r3_retraining_training_guard_pass`.

R3 обучение должно брать batch `2026-01-27..2026-03-13`, где уже применены пользовательские правки за `2026-03-07..2026-03-13`. Нельзя случайно запускать R3 train на старом R2/R2Q batch `2026-01-27..2026-03-06`, иначе новая ручная неделя не попадет в обучение.

Правильный batch:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260313_ML_READY_439F_TARGETS_V1.csv
rows=3726
entry_y 1=432 / 0=3294
features=439
guard=PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
```

Ручные R3 поля `user_reason_ru`, `marker`, `model_decision`, `GoodIds`, `entry_y`, `phase_y`, `state_y`, `reason_y` остаются teacher/target/audit-слоем и не являются live X features. Следующий независимый proof не может быть на `2026-03-07..2026-03-13`, потому что эти дни уже вошли в train; нужен следующий невиденный forward-отрезок после `2026-03-13`.

Текущий контроль: R3 `TrainingGuard` для `TrainRunId=stas5_v5c_r3_train_20260127_20260313` уже вернул `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`. Дальше нельзя менять train range на старый `2026-03-06`.

Обновление после train: R3 обучение уже завершено и post-train guard `PASS`. Для следующего forward использовать manifest только из `stas5_v5c_r3_train_20260127_20260313`; не использовать старые `r2` или `r2q` manifests.

## Known Fix 2026-07-17 V5C R2Q Normal Policy Too Conservative

Статус: `resolved_in_code_wait_forward_rerun`.

Симптом: после запуска `-EntryDecisionPolicy Normal` для forward `2026-03-07..2026-03-13` пользователь увидел слишком мало входов. Manifest подтвердил `ENTER=5`, `WATCH=54`, `SKIP=495` на `554` кандидатах.

Причина: `Normal` был задан как train OOF quantile `enter=0.965 / watch=0.815`. Это формально шире trained threshold, но на новой forward-неделе score distribution оказался ниже train distribution, поэтому фактически режим остался слишком консервативным.

Исправление: `Normal` расширен до `enter=0.90 / watch=0.60`, `WideReview` до `enter=0.80 / watch=0.50`. Пороги остаются train-OOF-only, без forward outcome tuning. Ожидаемые counts на уже готовых score week2: `Normal ENTER=25`, `WideReview ENTER=64`.

Правило дальше: для ручного визуального отбора использовать `WideReview`; для более строгого боевого просмотра использовать новый `Normal`. Не возвращать `Normal` к `0.965`, иначе входы снова будут задушены.

## Known Fix 2026-07-17 V5C R2Q Train Liblinear Multiclass Failure

Статус: `resolved_in_code_wait_retry_train`.

Симптом: после `TrainingGuard PASS` команда `Train` для `stas5_v5c_r2q_train_20260127_20260306` падала на обучении `phase_y/state_y` с ошибкой `ValueError: The 'liblinear' solver does not support multiclass classification`.

Причина: `MARKET_PHASE_STATE_ML` использовал `logistic_balanced` pipeline, который внутри построен на `liblinear`. Этот solver подходит для binary ENTRY, но не для multiclass `phase_y/state_y`.

Исправление: для phase/state введен отдельный `PHASE_STATE_MODEL_KIND = "extra_trees_balanced"` и применен для LODO OOF, walk-forward audit и финального сохраненного phase/state model package. ENTRY-кандидаты остались отдельными: `logistic_balanced/extra_trees_balanced`.

Проверка: `py_compile PASS`; `pytest tests/test_stas5_v5_two_block_ml.py tests/test_stas5_v5_continuous_ml.py` = `5 passed`; добавлен multiclass LODO test на 3 класса. Правило дальше: не использовать binary-only `liblinear` pipeline для `phase_y/state_y`.

## Known Fix 2026-07-17 V5C R2 Labels Applied But Weakly Weighted

Статус: `resolved_in_code_wait_new_train`.

Симптом: пользовательская review-неделя `2026-02-28..2026-03-06` реально вошла в R2 train (`576` строк, `69` GOOD), но модель на week2 выглядела так, будто ручные lows почти не изменили поведение. Это не была подмена старым R1.

Причина: новые labels имели обычный вес внутри `3172` строк; ENTER-порог был квантильный `p90` и принудительно давал много ENTER; `MARKET_PHASE_STATE_ML` на `SGDClassifier(log_loss)` давал warnings и слабый state-сигнал; forward использовал two-block даже когда baseline был лучше.

Исправление: в `src/mlbotnav/stas5_v5_two_block_ml.py` и `src/mlbotnav/stas5_v5_continuous_ml.py` добавлены teacher-only sample weights от `2026-02-28`, stable phase/state без SGD, raw-proba guard без тихой NaN/inf-очистки, ENTRY candidates `logistic_balanced/extra_trees_balanced`, precision/Wilson OOF threshold и production selector baseline vs two-block. Следующее обучение должно идти новым run_id, например `stas5_v5c_r2q_train_20260127_20260306`.

Правило дальше: не считать two-block production-победителем автоматически. Forward обязан читать `selected_entry_model` из train manifest. P90 threshold больше не использовать как финальную ENTRY-политику для качества.

## Known Guardrail 2026-07-17 V5C R2 Must Not Fall Back To R1 Batch

Статус: `guardrail_active_for_v5c_walk_forward_r2`.

Симптом, которого нельзя допускать: собрать R2 batch `2026-01-27..2026-03-06`, а затем запустить `TrainingGuard` или `Train` так, что они молча возьмут старый R1 batch `2026-01-27..2026-02-27`. Это ломает смысл переобучения: пользовательская review-неделя `2026-02-28..2026-03-06` не попадет в train.

Исправление внесено в:

```text
src/mlbotnav/stas5_v5_continuous_ml.py
src/mlbotnav/stas5_v5_two_block_ml.py
src/mlbotnav/stas5_v5_batch_dataset_builder.py
STAS5_ML_CORE/run_stas5_v5c_continuous_train_forward.ps1
```

Правило дальше: для R2 всегда явно передавать `-TrainStartDay 2026-01-27 -TrainEndDay 2026-03-06`. Forward week2 запускать только на `2026-03-07..2026-03-13` и только после R2 post-train guard PASS. Дни `2026-02-28..2026-03-06` после включения в R2 train больше не являются blind proof для R2.

Старые R1 model/forward artifacts в `artifacts/v5c/model` и `artifacts/v5c/forward` не являются ошибкой для R2 batch. Для walk-forward guard проверяет качество нового batch и отсутствие leakage в X, а не требует, чтобы в проекте вообще никогда раньше не было модели.

## Known Fix 2026-07-17 R2 Review UTF-8 Text

Статус: `resolved_for_r2_review_week`.

Симптом: часть R2 review-ledger файлов за `2026-03-02..2026-03-06` содержала question-mark placeholders вместо русского текста в `user_reason_ru` и RU-md отчетах. Причина - запись русских строк через PowerShell/stdin без надежного UTF-8-контракта.

Исправление: review-ledger за все закрытые дни `2026-02-28..2026-03-06` перезаписан UTF-8 способом. Метки не менялись: `GoodIds`, `BAD`, `entry_y`, predictions, daily packages, training и forward остались прежними.

Правило дальше: при генерации русских отчетов из PowerShell не передавать кириллицу в Python через небезопасный stdin. Использовать UTF-8 файл/скрипт, Unicode escape или явно проверять результат аудитом на question-mark placeholders/mojibake.

## Known Guardrail 2026-07-17 R2 Review Labels Are Teacher Only

Статус: `guardrail_active_for_r2_retraining`.

Пользовательская разметка forward-дней, например `2026-02-28`, становится teacher/target-информацией для будущего R2. `GoodIds`, ручные BAD-комментарии, `model_decision`, `marker`, `user_reason_ru`, `phase_y/state_y/reason_y/entry_y` не являются live features и не должны попадать в X439.

После того как день из blind-forward недели будет включен в R2 training, этот же день больше нельзя использовать как независимое доказательство качества R2. Для проверки R2 нужен следующий невиденный forward-отрезок, например дни после закрытой review-недели.

Текущие закрытые R2 teacher-дни: `2026-02-28`, `2026-03-01`, `2026-03-02`, `2026-03-03`, `2026-03-04`, `2026-03-05`, `2026-03-06`. R2 training по ним пока не запускался.

## Known Guardrail 2026-07-16 V5C WAVE Strip No Black Tail

Статус: `guardrail_active_for_v5c_wave_visual_carry`.

В V5C forward visual review нельзя оставлять хвостовой `GAP after_last_confirmed_or_active_wave` как черный участок WAVE-полосы. Для visual review последний active `LONG/SHORT` должен тянуться до `available_end_utc = min(day_end, last_open_time + bar_step)`.

Для cross-day WAVE подпись процента должна использовать cumulative percent от настоящего старта волны: `strength_strip_label_pct_basis = cumulative_from_true_wave_start`. Нельзя возвращаться к дневному `visible_move_pct` как основному проценту на графике, потому что тогда перенос через сутки визуально снова выглядит как новый отдельный день.

Текущий контроль: `tail_gap_rows_filled_total=7`, `tail_gap_minutes_filled_total=298.0`, `rendered_gap_rows_total=0`, `cross_day_wave_rows_total=13`.

## Known Guardrail 2026-07-16 V5C Visual Strength Strip Is Review Only

Статус: `guardrail_active_for_v5c_visual_review`.

Блок `Fon / LONG / SHORT / WAVE` в текущем V5C forward overview нужен только для ручной визуальной проверки качества входов. Он не является live feature source, не входит в X439, не меняет `ENTRY_ML_LIVE_SCORE`, `ENTRY_ML_LIVE_DECISION`, thresholds, model manifest или predictions CSV.

Для V5C этот блок должен строиться из `run_dir/ohlcv_contexts`, чтобы WAVE переносил контекст через границу суток. Нельзя возвращать day-boxed WAVE из одного `dt=YYYY-MM-DD`, иначе снова появится 24-часовой сброс.

Служебные `macro_wave_segment_kind=GAP` не отдавать в renderer WAVE-полосы. Текущий контроль: `filtered_gap_rows_total=7`, `rendered_gap_rows_total=0`, направления WAVE только `LONG/SHORT`.

## Known Guardrail 2026-07-16 V5C Continuous Is Separate From Day-Boxed V5

Статус: `guardrail_active_for_v5c_continuous`.

Старый V5 forward был корректным no-future run, но его `cs_*`/`fcs_*` собирались day-boxed: в начале нового дня структура могла видеть только первые минуты текущего дня. Поэтому его нельзя называть непрерывным рыночным прогоном.

Исправление сделано отдельным контуром:

```text
STAS5_ML_CORE/artifacts/v5c/
src/mlbotnav/stas5_v5_continuous_ml.py
STAS5_ML_CORE/run_stas5_v5c_continuous_train_forward.ps1
```

Правильный текущий статус:

```text
PASS_V5C_CONTINUOUS_TWO_BLOCK_FORWARD_20260228_20260306_BLIND_NO_FUTURE
```

Контроль отсутствия midnight-reset: `2026-02-28 LA001` в V5C имеет `cs_context_rows=748` и `cs_rows_240m=240`, то есть видит хвост `2026-02-27`. В старом дневном режиме ранние кандидаты дня видели бы только строки текущего дня.

Важная граница: rolling continuous warmup `720` минут не дает модели будущие свечи. Каждая строка по-прежнему обязана проходить `cs_max_source_time_utc <= entry_time_utc` и `fcs_max_source_time_utc <= entry_time_utc`; teacher/target поля не входят в `X`.

Не считать `62 ENTER` production-сигналами без ручного visual review. Это blind/no-future прогон для проверки качества, а не финальная торговая схема.

## Known Fix 2026-07-16 V5 Forward Needs ENTER Arrow Visual Layer

Статус: `resolved_for_current_forward_run`.

Симптом: после V5 blind/no-future forward пользователь открывал старые FULL274/V2 visual approval PNG, где не было удобного review-слоя для сопоставления всех `LAxxx` с решениями `ENTER/WATCH/SKIP`. Первая версия V5 overlay имела длинные зеленые стрелки и боксы `ENTER`, которые мешали просмотру.

Исправление: добавлен отдельный V5 forward visual review:

```text
src/mlbotnav/stas5_v5_forward_visual_review.py
STAS5_ML_CORE/artifacts/v5/forward/runs/stas5_v5_forward_20260228_20260306_20260716/visual_review/
```

Текущий render: `PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES`, `png_count=14`. На overview все кандидаты подписаны желтым `LAxxx`; `SKIP` показан желтым X, `WATCH` - маленьким желтым ромбом, `ENTER` - зеленым треугольником. Длинные зеленые стрелки и боксы убраны.

Правило дальше: для просмотра V5 forward входов открывать `visual_review`, а не исходные FULL274 approval PNG. Этот слой review-only: он не меняет модель, не переобучает и не является feature source.

## Known Finding 2026-07-16 V5 Two-Block Worse Than Baseline On OOF

Статус: `review_required_before_production`.

V5 two-block training и blind forward выполнены, guard-ы `PASS`, но OOF-метрики показали, что простой baseline сильнее:

```text
ENTRY_BASELINE_ML ROC-AUC=0.6564150491969973 PR-AUC=0.181311573028207
ENTRY_ML two-block ROC-AUC=0.6377471064987889 PR-AUC=0.15605847999619604
```

Это не leakage-ошибка и не провал guard-а. Это важный ML-результат: phase/state слой пока не доказал пользу. Запрещено объявлять two-block production-победителем без ручного review 20 forward `ENTER` и отдельного baseline-forward сравнения.

Итоговый отчет:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_TWO_BLOCK_TRAIN_FORWARD_20260716_RU.md
```

## Known Guardrail 2026-07-16 V5 Two-Block OOF Is Mandatory

Статус: `guardrail_active_for_v5_two_block_ml`.

Для `ENTRY_ML` запрещено использовать настоящие `phase_y/state_y/reason_y` как features. Также запрещено использовать in-sample predictions первого блока, если `MARKET_PHASE_STATE_ML` обучалась на той же строке, которую потом предсказывает для `ENTRY_ML`.

Правильный контракт:

```text
MARKET_PHASE_STATE_ML train: X439 -> phase_y/state_y
ENTRY_ML train: X439 + OOF phase/state predictions -> entry_y
ENTRY_ML forward: X439 + live phase/state predictions -> entry score
```

ТЗ зафиксировано здесь:

```text
STAS5_ML_CORE/09_STAS5_V5_TWO_BLOCK_ML_TZ_RU.md
```

Training нельзя запускать до отдельного `STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1=PASS`. Forward нельзя запускать до post-train guard `PASS`.

## Known Guardrail 2026-07-16 V5 Batch Targets Are Not X

Статус: `guardrail_active_for_v5_batch_training`.

Batch CSV содержит рядом и признаки, и teacher/target поля. Нельзя брать все колонки CSV как model input. Единственный допустимый `X` контракт:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_FEATURE_ALLOWLIST_439F_V1.json
```

Запрещено добавлять в `X`: `entry_y`, `phase_y`, `state_y`, `reason_y`, `entry_label`, `rank_label`, manual passport/support/resistance/phase labels, future/postfact/hit_/TP/Stas3/exit, старые `ML_KEEP_SCORE/ML_DECISION`, full-group future признаки.

Для `ENTRY_ML` также запрещено давать настоящие `phase_y/state_y` как features. Разрешены только OOF predictions от `MARKET_PHASE_STATE_ML` на train и live predictions первого блока на forward.

Batch guard, который должен оставаться `PASS` перед training:

```text
STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_GUARD_V1.json
```

## Known Error To Avoid 2026-07-16 NoPlot Leaves V5 Day Partial

Статус: `guardrail_active_for_v5_full_ready_day`.

Во время range audit `2026-01-27..2026-02-27` день `2026-02-07` сначала остался `PARTIAL`, потому что был собран с `-NoPlot`: данные и guard были `PASS`, но отсутствовала обязательная карта:

```text
DAY_MARKET_PASSPORT_YYYYMMDD_FULL_CAUSAL_STRUCTURE_MAP_V1.png
```

Для full-ready дня нужен полный набор:

```text
ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json
FULL_CAUSAL_STRUCTURE_GUARD_V1.json
LEVELS/CHANNELS/REGIMES/EVENTS_CAUSAL_V1.csv
DAY_MARKET_PASSPORT_YYYYMMDD_FULL_CAUSAL_STRUCTURE_MAP_V1.png
```

Если день был собран с `-NoPlot`, перед batch training надо пересобрать full causal layer без `-NoPlot`.

## Known Guardrail 2026-07-15 Approved GoodIds Are Targets, Not Live Features

Статус: `guardrail_active_for_v5_approved_passport_builder`.

Новый builder:

```text
src/mlbotnav/stas5_v5_approved_passport_builder.py
```

принимает пользовательские GOOD ids и создает target-слой `entry_y/phase_y/state_y/reason_y`. Эти поля являются `y`, а не входными признаками `X`.

Правильная команда:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day YYYY-MM-DD -Stage All -GoodIds LA020,LA037,LA042
```

Нельзя трактовать `GoodIds` как live-логику входа или как ограничитель количества входов. Это только утвержденная разметка истории для конкретного дня. Прямые признаки рынка для модели после этого пересчитываются causal builders:

```text
274 old causal features + cs_* + fcs_*
```

Guard должен оставаться:

```text
targets_not_in_features = PASS
source_time_before_entry = PASS
forbidden_features_absent = PASS
```

## Known Error To Avoid 2026-07-15 Skipping V5 Approved Passport Stage

Статус: `guardrail_active_for_v5_day_ladder`.

Нельзя запускать `cs_*` и `fcs_*` builders для нового дня, пока в `artifacts/v5/market_passports/YYYYMMDD` нет approved passport/targets:

```text
ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv
FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json
PHASE_STATE_REASON_GUARD_V2.json
ENTRY_PHASE_STATE_REASON_LEDGER_USER_APPROVED_V2.csv
PHASE_SEGMENTS_USER_APPROVED_V1.csv
MARKET_STRUCTURE_NUMERIC_V1.csv
```

Правильная команда-лесенка:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day YYYY-MM-DD -Stage All
```

Если approved stage отсутствует, команда должна остановиться. Это не ошибка, а защита от fake labels.

## Known Error To Avoid 2026-07-15 Manual Structure As Direct Full V5 Feature

Статус: `guardrail_active_for_v5_full_causal_structure`.

Нельзя использовать ручные фазы, ручные зоны поддержки/сопротивления, ручные подписи пампа/дампа/ножа, `entry_y`, `phase_y`, `state_y`, `reason_y`, `market_phase_primary`, `entry_reason_primary` как прямые model features `X`.

Правильный контракт V5:

```text
ручной паспорт = teacher / targets y
causal builders = direct live-safe features X
```

Текущий разрешенный full feature set для `2026-01-27`:

```text
274 старых causal features + 81 cs_* features + 84 fcs_* features = 439 feature columns
```

Guard:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_FULL_CAUSAL_STRUCTURE_GUARD_V1.json
```

Должен оставаться `PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.

Если нужна новая структура рынка как признак, ее надо добавлять только через builder, который пересчитывает ее по прошлым свечам до `entry_time_utc`. Нельзя брать готовую ручную структуру полного дня как live-признак.

## Known Error To Avoid 2026-07-15 Manual Passport As Direct V5 Feature

Статус: `guardrail_active_for_v5_causal_structure`.

Нельзя использовать ручные фазы, ручные зоны поддержки/сопротивления, `entry_y`, `phase_y`, `state_y`, `reason_y`, `market_phase_primary`, `entry_reason_primary` как прямые model features `X`.

Правильный контракт V5:

```text
ручной паспорт = teacher / targets y
causal market-structure builder = direct features X
```

Предыдущий разрешенный feature set старого `cs_*` слоя для `2026-01-27`:

```text
274 старых causal features + 81 cs_* features = 355 feature columns
```

Guard:

```text
STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_GUARD_V1.json
```

Для старого `cs_*` слоя guard должен оставаться `PASS_NO_TRAINING_CAUSAL_STRUCTURE_READY`. Текущий главный full-guard описан в верхнем разделе этого файла.

Если нужна новая структура рынка как признак, ее надо добавлять только через builder, который пересчитывает ее по прошлым свечам до `entry_time_utc`. Нельзя брать готовую ручную структуру полного дня как live-признак.

## Known Non-Error 2026-07-15 V5 Has No Model Yet

Статус: `expected_current_state`.

В `STAS5_ML_CORE/artifacts/v5/` после текущей работы есть labels и market-passport package, но нет V5 `model` и нет V5 `forward`. Это не ошибка: обучение не запускалось специально, потому что утвержден только один январский день с causal-builder контрактом.

Следующий правильный шаг: повторить дневной пакет для следующих approved дней, затем собрать общий batch dataset и batch guard. Только после этого запускать V5 training/forward.

## Known Error To Avoid 2026-07-15 Teacher Targets As Live Features

Статус: `guardrail_active_for_v5_phase_state_reason`.

`entry_y`, `phase_y`, `state_y`, `reason_y`, `market_phase_primary`, `entry_reason_primary`, ручные support/resistance зоны и full-day phase segments разрешены как teacher-target/source-of-truth при разметке истории, но запрещены как live features.

Правильный контракт:

```text
X = 274 causal-признака из allowlist
y = entry_y/phase_y/state_y/reason_y из ручного паспорта
```

Если позже нужен прямой структурный feature, он должен называться отдельно, например `causal_phase_x`, и проходить guard `available_time <= entry_time_utc`.

## Known Error To Avoid 2026-07-15 Future Group Replacement In Live Logic

Статус: `guardrail_active_for_v5_market_passport`.

Запрещено строить live-вход так, будто будущая группа уже известна. В истории можно использовать будущее только для офлайн-разметки и объяснения, почему кандидат оказался плохим или хорошим. В реальном прогоне модель должна принимать решение только по данным, доступным до `entry_time_utc`.

Запрещенные признаки/поля для обучения и live: `future`, `postfact`, `hit_*`, `TP/Stas3/exit`, старые `ML_DECISION/ML_KEEP_SCORE`, любые full-group признаки, которые требуют знать более поздних кандидатов. Уже поставленный live-вход нельзя задним числом заменять более поздним кандидатом.

Текущий V2 паспорт `2026-01-27` остается `DRAFT_V2_NO_TRAINING`; `GOOD_ALT` и `REVIEW_ONLY` не являются train-positive без ручного подтверждения пользователя.

## Known Non-Error 2026-07-15 FULL274 Visual CUT In Unlabeled Trial

Статус: `checked_for_20260127 / no_training`.

В run `full274_feature_collect_20260127_20260715_090857` visual manifest показывает:

```text
label_counts: UNLABELED=75
approval_bucket_counts: CUT=75
```

Это не финальная negative-разметка и не означает, что все `75` кандидатов плохие. Для текущего one-day collect это служебное состояние `UNLABELED_VISUAL_ONLY`. При построении V5 market-passport/label-ledger нельзя превращать `visual CUT=75` в обучающие BAD-метки без ручного подтверждения.

## Known Error 2026-07-15 Partial 163 Feature Collect Instead Of FULL274

Статус: `resolved`.

Симптом: ранняя ручная команда для `2026-04-01` собрала только `163` V2 combo/STAS4/STAS5 признака вместо полного набора `274`.

Причина: запуск шел напрямую через `stas5_v2_combo_feature_exporter`, без V1/STAS1-STAS2 feature snapshot `111`. Дополнительно первый STAS2 smoke был пустым, потому что STAS1 wrapper добавил timestamp к папке, а STAS2 получил путь без этого суффикса.

Исправление:

```text
STAS5_ML_CORE/run_stas5_full274_feature_collect.ps1
```

Wrapper всегда берет фактические STAS1/STAS2 run folders по префиксу и собирает `111 + 163 = 274`. Контрольный run `full274_feature_collect_20260401_20260715_084509` дал `rows=81`, `features=274`, `PASS`.

## Known Non-Error 2026-07-14 Day25 User Circles Matched Existing Winners

Статус: `checked_for_20260525 / no_csv_change / no_training`.

На `2026-05-25` пользовательские круги не выявили новой ошибки group-rank разметки:

```text
первый круг = LA020, уже BEST_GOOD
LA019 остается GOOD_ALT, потому что выше LA020
второй круг = LA038, уже BEST_GOOD
```

Вывод: не делать механическую CSV-правку только из-за того, что первый круг стоит на сером/skip-кандидате без подписи. В текущем V4 ledger этот старый `SKIP` уже правильно повышен до `BEST_GOOD`.

Запрещено: запускать V4 training, group features, threshold tuning, Optuna, API, TP/Stas3/exit до финальной ручной проверки ledger.

## Known Non-Error 2026-07-14 Day24 User Circles Matched Existing Winners

Статус: `checked_for_20260524 / no_csv_change / no_training`.

На `2026-05-24` пользовательские круги не выявили новой ошибки group-rank разметки:

```text
LA015 уже BEST_GOOD
LA042 уже BEST_GOOD
LA065 уже BEST_GOOD
LA067 остается GOOD_ALT
```

Вывод: не делать механическую CSV-правку только из-за видимого красного подчеркивания. Если пользователь отдельно обведет `LA067`, тогда проверять его как возможную отдельную post-bounce micro-group; в текущем скрине главный late low/retest уже `LA065`.

Запрещено: запускать V4 training, group features, threshold tuning, Optuna, API, TP/Stas3/exit до финальной ручной проверки ledger.

## Known Error 2026-07-14 Day23 Recovery Group Was Too Wide

Статус: `resolved_for_20260523 / process_guard / no_training`.

Симптом: на `2026-05-23` draft-разметка держала `LA034..LA042` одной recovery-группой с winner `LA036`. Из-за этого пользовательские точки `LA034` и `LA042` были не самостоятельными входами: `LA034` был `BAD_IN_GROUP`, а `LA042` был только `GOOD_ALT`.

Причина: macro-group смешала три разные фазы движения:

```text
первый recovery pullback -> средний clean pullback -> pre-breakout retest
```

Исправление:

```text
LA034 -> BEST_GOOD в G20260523_004A_1337_1403
LA036 -> BEST_GOOD в G20260523_004B_1536_1626
LA042 -> BEST_GOOD в G20260523_004C_1700_1744
```

Правило дальше: если пользовательский круг стоит на отдельном pullback/retest внутри восстановления, не заставлять его проигрывать более позднему winner только потому, что они в одной длинной recovery-волне. Сначала делить движение на micro-groups по фазам.

Запрещено: запускать V4 training, group features, threshold tuning, Optuna, API, TP/Stas3/exit до финальной ручной проверки ledger.

## Known Error 2026-07-14 Day22 First Low Was Preferred Over User-Marked Retest

Статус: `resolved_for_20260522 / process_guard / no_training`.

Симптом: на `2026-05-22` draft-разметка выбрала `LA022` как `BEST_GOOD` в группе `05:36-09:01`, потому что это первый/чуть более низкий pre-London low. На свежем пользовательском скрине красный круг стоит на позднем ретесте `LA024`, где уже видна реакция и продолжение вверх.

Причина: правило "самый нижний внутри группы" было применено слишком механически. Для human-style ranker главный вход может быть не абсолютный первый low, а более чистый ретест после реакции.

Исправление:

```text
LA022 -> GOOD_ALT
LA024 -> BEST_GOOD
```

Правило дальше: если пользователь обводит ретест/подбор после первого low, не оставлять его вторичным только потому, что он на несколько bps выше. Сначала смотреть фазу: первый flush-low против подтвержденного retest-low.

Запрещено: запускать V4 training, group features, threshold tuning, Optuna, API, TP/Stas3/exit до финальной ручной проверки ledger.

## Known Error 2026-07-14 Day21 Wide Sell-Wave Group Hid Multiple User-Marked Markers

Статус: `resolved_for_20260521 / process_guard / no_training`.

Симптом: на `2026-05-21` draft-разметка держала длинную sell-wave группу `LA022..LA050` с одним winner `LA045`. Из-за этого пользовательски обведенные `LA039` и `LA050` были плохими/вторичными, хотя на скрине они отмечены как отдельные human-style входы. Аналогично pre-breakout группа `LA051..LA060` держала `LA057` как `GOOD_ALT`, хотя пользователь обвел его как отдельный вход.

Причина: macro-group была слишком широкой и смешала разные фазы:

```text
первый sell-wave basin -> overlap flush -> post-flush retest
первый pre-breakout pullback -> более поздний lower retest
```

Исправление:

```text
G20260521_003A_0823_1213: LA022..LA040, winner LA039
G20260521_003B_1231_1345: LA041..LA045, winner LA045
G20260521_003C_1408_1449: LA046..LA050, winner LA050
G20260521_004A_1508_1637: LA051..LA057, winner LA057
G20260521_004B_1642_1709: LA058..LA060, winner LA059
```

Правило дальше: если в одном long sell-wave пользователь обводит несколько желтых/серых/зеленых markers, сначала проверять смену фазы и разбивать на micro-groups. Не сводить все к одному самому низкому `BEST_GOOD`, если на графике есть отдельные человеческие точки входа.

Запрещено: запускать V4 training, group features, threshold tuning, Optuna, API, TP/Stas3/exit до финальной ручной проверки ledger.

## Known Error 2026-07-14 Day20 Rebound Pullback Was Hidden Inside Crash-Low Group

Статус: `resolved_for_20260520 / process_guard / no_training`.

Симптом: на `2026-05-20` draft-разметка держала `LA033..LA038` в одной crash-low группе. `LA037` был правильным winner нижней зоны, но пользователь отдельно обвел верхний серый/skip-кандидат после отскока. Draft считал `LA038` плохим `BAD_AFTER_BOUNCE_TOO_HIGH`.

Причина: macro-group закончилась слишком поздно и смешала две разные фазы: нижний crash-low retest (`LA037`) и последующий rebound/pullback вход (`LA038`).

Исправление:

```text
G20260520_003A_1319_1413: LA033..LA037, winner LA037
G20260520_003B_1426_1507: LA038..LA039, winner LA038
```

Правило дальше: серый/желтый старый marker нельзя автоматически понижать, если пользователь обводит его как отдельный вход после смены фазы. Сначала проверять, является ли это новой micro-group, а не проигравшим соседом старого low.

Запрещено: запускать V4 training, group features, threshold tuning, Optuna, API, TP/Stas3/exit до финальной ручной проверки ledger.

## Known Error 2026-07-14 Day19 Retest Was Hidden Inside Overlap Flush Group

Статус: `resolved_for_20260519 / process_guard / no_training`.

Симптом: на `2026-05-19` старая draft-разметка держала `LA034..LA047` в одной широкой группе. Из-за этого `LA042` был единственным winner, а `LA046` был понижен до `GOOD_ALT`, хотя пользователь на новом скрине обвел эту retest/base-зону как отдельный нужный вход.

Причина: macro-group была слишком широкой. `LA042` и `LA046` не должны конкурировать как один winner: `LA042` - deep low после overlap flush, `LA046` - отдельный retest/base вход после реакции от этого low.

Исправление:

```text
G20260519_005A_1308_1449: LA034..LA042, winner LA042
G20260519_005B_1525_1610: LA043..LA047, winner LA046
```

Важно: визуальная подпись со score `0.86` соответствует строке `LA046` в CSV. `LA045` остается плохим соседним примером, `LA047` остается `GOOD_ALT`.

Правило дальше: если пользователь обводит отдельный retest/base вход после уже выбранного deep-low, не оставлять его проигравшим в той же широкой flush-группе. Сначала проверять, не нужна ли отдельная micro-group.

Запрещено: запускать V4 training, group features, threshold tuning, Optuna, API, TP/Stas3/exit до финальной ручной проверки ledger.

## Known Error 2026-07-14 Wide Group Hid Separate Human Targets

Статус: `resolved_for_20260515 / process_guard_for_20260516_20260525 / no_training`.

Симптом: на `2026-05-15` старая V1-разметка собрала `LA002..LA007` в одну широкую группу и оставила только `LA007` winner. Из-за этого `LA004`, который пользователь отметил как отдельный нужный вход, был ошибочно понижен до `GOOD_ALT`.

Причина: group-rank логика была применена слишком крупно. Нельзя считать, что один macro-move всегда имеет только один winner. Если пользователь отметил несколько отдельных нижних зон, они должны стать отдельными micro-groups.

Правило V2:

```text
старый ENTER/UNSURE/SKIP = только контекст
человечески подчеркнутая нижняя точка = может быть BEST_GOOD
несколько пользовательских нижних точек в одном macro-move = несколько micro-groups
GOOD_ALT рядом с winner = первый кандидат на ручную проверку
```

Исправление применено к `2026-05-15`: winners стали `LA004`, `LA007`, `LA021`, `LA024`, `LA054`, `LA061`. Для `2026-05-16..2026-05-25` создан audit `STAS5_V4_MICRO_GROUP_RISK_AUDIT_20260516_20260525`, чтобы искать похожие случаи точечно.

Запрещено: запускать V4 training, group features, threshold tuning, Optuna, API, TP/Stas3/exit до ручной проверки этого риска.

## STAS5 V4 Screenshot Inventory Boundary 2026-05-01..2026-05-25

Статус: `process_guard / artifact_inventory_boundary / no_training`.

Риск: при просмотре артефактов можно перепутать `2026-05-01..2026-05-14` train visual approval PNG с полноценным V4 group-rank разбором.

Правильная трактовка после инвентаризации:

```text
2026-05-01..2026-05-14 = train visual approval screenshots, не V4 group-block ledger
2026-05-15..2026-05-25 = forward source screenshots + V4 group-rank annotated screenshots
```

Навигационная папка:

```text
STAS5_ML_CORE/artifacts/v4/review_navigation/20260714_artifact_inventory
```

Запрещено: считать эту инвентаризацию запуском обучения, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit или автоматическим approval `01..14` под V4 group-rank.

## STAS5 V4 2026-05-15 Only Approved Status Was Too Narrow

Статус: `resolved_process_guard / superseded_by_forward_review_11 / no_training`.

Симптом: `2026-05-15` был временно оформлен как отдельный `APPROVED_V1`, и главный `STAS5_V4_GROUP_RANK_LEDGER.csv` содержал только этот день. Это создавало неверную картину, будто `15` живет отдельно от `16..25`.

Правильная трактовка после пользовательского уточнения: `2026-05-15` входит в общий forward-review блок `2026-05-15..2026-05-25`. База обучения отдельно: `2026-05-01..2026-05-14`.

Актуальный источник:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Старый 15-only главный файл сохранен как superseded-копия:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER_20260515_ONLY_SUPERSEDED_20260714T124741Z.csv
```

Запрещено: использовать старый 15-only статус как отдельную рабочую ветку, смешивать `15..25` с train-base `01..14`, обучать V4 до group features и финального guard PASS.

## STAS5 V4 2026-05-15 User-Corrected Draft Superseded By Approved V1

Статус: `resolved_process_guard / stas5_v4_20260515_approved_v1 / no_training`.

Решение: `2026-05-15` снят с карантина по решению пользователя. Актуальный approved ledger:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_APPROVED_V1.csv
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
```

Остаточный риск: можно ошибочно использовать старый `SCREENSHOT_DRAFT` или `USER_CORRECTED_V1.csv` вместо `APPROVED_V1.csv`. Правильный источник для approved `2026-05-15` - только `APPROVED_V1` и общий `STAS5_V4_GROUP_RANK_LEDGER.csv`.

Запрещено: считать снятие карантина запуском обучения, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо автоматически добавлять draft-дни `2026-05-16..25` в approved ledger без отдельного подтверждения.

## STAS5 V4 2026-05-25 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260525_draft / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260525_DRAFT.csv` день `2026-05-25` можно ошибочно включить в V4 train как готовый approved ledger. Это особенно опасно, потому что `2026-05-21..25` по плану требуют ручной проверки.

Правильная трактовка: `20260525_DRAFT` является рабочим group-review draft по скриншоту. Перед включением в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` нужно явное подтверждение/правка пользователя и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо превращать группы `NO_TRADE_GROUP` в pre-training hard filter.

## STAS5 V4 2026-05-24 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260524_draft / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260524_DRAFT.csv` день `2026-05-24` можно ошибочно включить в V4 train как готовый approved ledger. Это особенно опасно, потому что `2026-05-21..25` по плану требуют ручной проверки.

Правильная трактовка: `20260524_DRAFT` является рабочим group-review draft по скриншоту. Перед включением в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` нужно явное подтверждение/правка пользователя и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо превращать группы `NO_TRADE_GROUP` в pre-training hard filter.

## STAS5 V4 2026-05-23 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260523_draft / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260523_DRAFT.csv` день `2026-05-23` можно ошибочно включить в V4 train как готовый approved ledger. Это особенно опасно, потому что `2026-05-21..25` по плану требуют ручной проверки.

Правильная трактовка: `20260523_DRAFT` является рабочим group-review draft по скриншоту. Перед включением в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` нужно явное подтверждение/правка пользователя и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо превращать группы `NO_TRADE_GROUP` в pre-training hard filter.

## STAS5 V4 2026-05-22 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260522_draft / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260522_DRAFT.csv` день `2026-05-22` можно ошибочно включить в V4 train как готовый approved ledger. Это особенно опасно, потому что `2026-05-21..25` по плану требуют ручной проверки.

Правильная трактовка: `20260522_DRAFT` является рабочим group-review draft по скриншоту. Перед включением в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` нужно явное подтверждение/правка пользователя и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо превращать группы `NO_TRADE_GROUP` в pre-training hard filter.

## STAS5 V4 2026-05-21 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260521_draft / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260521_DRAFT.csv` день `2026-05-21` можно ошибочно включить в V4 train как готовый approved ledger. Это особенно опасно, потому что `2026-05-21..25` по плану требуют ручной проверки.

Правильная трактовка: `20260521_DRAFT` является рабочим group-review draft по скриншоту. Перед включением в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` нужно явное подтверждение/правка пользователя и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо превращать группы `NO_TRADE_GROUP` в pre-training hard filter.

## STAS5 V4 2026-05-20 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260520_draft / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260520_DRAFT.csv` день `2026-05-20` можно ошибочно включить в V4 train как готовый approved ledger.

Правильная трактовка: `20260520_DRAFT` является рабочим group-review draft по скриншоту. Перед включением в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` нужно явное подтверждение/правка пользователя и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо превращать группы `NO_TRADE_GROUP` в pre-training hard filter. Эти строки остаются размеченным контекстом выбора внутри дня.

## STAS5 V4 2026-05-19 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260519_draft / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260519_DRAFT.csv` день `2026-05-19` можно ошибочно включить в V4 train как готовый approved ledger.

Правильная трактовка: `20260519_DRAFT` является рабочим group-review draft по скриншоту. Перед включением в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` нужно явное подтверждение/правка пользователя и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо превращать no-trade группы в pre-training hard filter. Они нужны как размеченный контекст выбора внутри дня.

## STAS5 V4 2026-05-18 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260518_user_corrected_v1 / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260518_DRAFT.csv` день `2026-05-18` можно ошибочно включить в V4 train как готовый approved ledger.

Правильная трактовка: `20260518_DRAFT` superseded после пользовательских обводок. Актуальный рабочий файл - `STAS5_V4_GROUP_RANK_LEDGER_20260518_USER_CORRECTED_V1.csv`, где `LA036` и `LA066` добавлены как отдельные `BEST_GOOD`. Это все еще не разрешение на V4 train: перед обучением нужны финальный approved-пакет и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо превращать no-trade группы в pre-training hard filter. Они нужны как размеченный контекст выбора внутри дня.

## STAS5 V4 2026-05-17 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260517_draft / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260517_DRAFT.csv` день `2026-05-17` можно ошибочно включить в V4 train как готовый approved ledger.

Правильная трактовка: `20260517_DRAFT` является рабочим group-review draft по скриншоту. Проверка `USER_CHECKED_V1` подтвердила, что winners `LA004/LA006/LA036/LA046/LA063` совпадают с пользовательским скрином, но это не является разрешением на обучение. Перед V4 train все еще нужны финальный approved-пакет и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо превращать no-trade группы в pre-training hard filter. Они нужны как размеченный контекст выбора внутри дня.

## Console Mojibake Is Not Always File Mojibake

Статус: `process_guard / encoding_check / python_utf8_source_of_truth`.

Риск: PowerShell в этом окружении может выводить русские UTF-8 Markdown-файлы как `РўРµ...`, хотя сами файлы читаются нормально через Python/UTF-8. Если ориентироваться только на вывод `Get-Content`, можно ошибочно чинить уже нормальный файл.

Правильная проверка: читать файл как `encoding='utf-8'` и сканировать на реальные признаки поломки: длинные цепочки вопросительных знаков, `U+FFFD`, CJK-мусор в русском Markdown. Для V4 review-файлов `2026-05-15` и `2026-05-16` такой скан дал `problems=0`.

## STAS5 V4 2026-05-16 Draft Is Not Approved Train Ledger

Статус: `process_guard / stas5_v4_20260516_draft / no_training`.

Риск: день `2026-05-16` входит в базовый календарь V4, поэтому после появления `STAS5_V4_GROUP_RANK_LEDGER_20260516_DRAFT.csv` его можно ошибочно считать готовым approved train ledger.

Правильная трактовка: файл `20260516_DRAFT` является рабочим group-review draft по скриншоту. Перед включением в общий `STAS5_V4_GROUP_RANK_LEDGER.csv` нужно явное подтверждение/правка пользователя и guard по group features.

Запрещено: обучать V4 на этом draft, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо считать late `NO_TRADE_GROUP` строками hard-filter до обучения. Они нужны как объясненный контекст no-trade.

## STAS5 V4 2026-05-15 User-Corrected Draft Is Not Approved Train Ledger

Статус: `superseded_by_approved_v1 / stas5_v4_20260515_user_corrected_draft / no_training`.

Риск: после появления `STAS5_V4_GROUP_RANK_LEDGER_20260515_USER_CORRECTED_V1.csv` можно ошибочно использовать именно draft-файл вместо approved-файла.

Правильная трактовка: `USER_CORRECTED_V1` является источником ручной правки, но актуальный approved-файл после снятия карантина - `STAS5_V4_GROUP_RANK_LEDGER_20260515_APPROVED_V1.csv`.

Запрещено: обучать V4 без отдельного train-go, подбирать threshold, запускать Optuna/API/TP/Stas3/exit, либо считать `SCREENSHOT_DRAFT` актуальной версией после пользовательской правки.

## STAS5 V4 Must Not Use Old Features As Pre-Training Hard Cuts

Статус: `process_guard / stas5_v4_group_ranker_tz / no_pretrain_cut`.

Риск: после V3 можно ошибочно взять старые признаки, strategy votes, yellow X или ML score и заранее удалить “плохие” кандидаты до обучения. Это ломает V4: плохой вход рядом с хорошим является ценным обучающим примером, потому что модель должна научиться ранжировать кандидатов внутри группы.

Правильная трактовка V4: старые признаки остаются как контекст и объяснение ранга внутри группы, но не режут входы заранее. Единица обучения - `group_id`, где winner должен получить score выше соседних losers.

Запрещено до обучения удалять кандидатов по:

```text
ML_KEEP_SCORE_V2/V3
ML_DECISION_V2/V3
yellow_x
density/structure/pattern votes
knife risk
old ENTER/SKIP
postfact/hit/future
```

Разрешено отбрасывать только технический мусор: нет свечей, нет времени, сломанный join, дубликат машинного ключа, future leakage, невозможный `entry_time_utc` или `entry_price_5bps`.

V4 train запрещен, если нет `group_id`, нет обязательных group features, есть BAD без reason-code, в группе нет winner, `2026-05-15` включен не из `APPROVED_V1`/общего approved ledger, `2026-05-16..2026-05-25` включены без отдельного approved ledger, либо старые ML/postfact/future/TP/Stas3/exit поля попали в feature columns.

## STAS5 V3 Must Not Train On 2026-05-15 Or 2026-05-21..2026-05-25

Статус: `process_guard / stas5_v3_review_train_forward_ready`.

Риск: после добавления пользовательского review `2026-05-16..2026-05-20` можно ошибочно добавить в train день `2026-05-15` или новые blind-forward дни `2026-05-21..2026-05-25`.

Правильная трактовка V3:

1. `2026-05-01..2026-05-14` - старая train-база.
2. `2026-05-16..2026-05-20` - user-review train labels.
3. `2026-05-15` - исключен, пока нет финального review.
4. `2026-05-21..2026-05-25` - blind-forward only.

Запрещено: использовать `current_ml_score/current_ml_decision`, user-review поля, postfact, TP/Stas3/exit/API как feature columns; подбирать threshold по `21..25`; считать `USER_NO_CANDIDATE_ZONE` train label.

Проверочный guard: `STAS5_ML_CORE/artifacts/v3/guard/STAS5_V3_LEAKAGE_GUARD_20260501_20260520.json`.

## STAS5 V2 Full Snapshot Is Not Equal Latest Model Feature Set 2026-07-13

Статус: `process_guard / graph_to_feature_audit / model_feature_set_partial`.

Риск: после numeric coverage и большого approval-графика можно ошибочно сказать, что все нарисованные слои уже использовались последней моделью. Это неверно.

Правильная трактовка: full snapshot содержит `274` feature columns и покрывает график `2026-05-04`, но latest controlled model `stas5_v2_run_20260713_191122` обучена на наборе `v1_plus_risk_gate` из `126` признаков. В latest model не входят `stas4_v2_combo_*`, `stas4_v2_density_*`, `stas4_v2_structure_*`, `stas4_v2_block_*`, `stas4_v2_pattern_*`, `stas5_v2_short_wave_*`, `stas4_v2_volume_*`, `stas4_v2_div_*`.

Запрещено: утверждать, что текущая модель уже использует весь график; превращать yellow X/strategy X/UP в feature; подбирать threshold по forward. Правильно: запускать отдельное сравнение feature-set'ов, например baseline `v1_plus_risk_gate` против `graph_context_v2`/`full_v2_all_274`.

## STAS5 V2 Forward Review Is Not Threshold Tuning 2026-07-13

Статус: `process_guard / stas5_v2_controlled_forward_ready / blind_forward_only`.

Риск: после появления forward hit/miss postfact-колонок можно ошибочно начать подбирать threshold или переобучать модель на `2026-05-15..2026-05-20`.

Правильная трактовка: V2 controlled model выбрана по train ablation внутри `2026-05-01..2026-05-14`. Forward `15..20` нужен только для визуального review. Postfact-поля в CSV помогают понять качество после прогноза, но не являются feature columns и не являются train labels.

Запрещено: использовать forward postfact для threshold tuning, тренировать на forward, подключать TP/Stas3/exit, запускать API/мост Bybit, Optuna/scorer/target-lock.

## STAS5 V2 Numeric Coverage Is Context, Not A Trading Signal 2026-07-13

Статус: `process_guard / stas5_v2_numeric_coverage_ready / no_hard_filter`.

Риск: новые признаки `stas4_v2_block_*`, `stas4_v2_pattern_*`, `stas5_v2_short_wave_*` можно ошибочно воспринять как готовое правило входа или запрета. Это неверно.

Правильная трактовка: эти признаки переводят визуальные слои графика в causal числа для ML/audit. Они объясняют контекст рынка до входа, но не заменяют human label, не являются `ENTER/SKIP`, не являются trading permission и не должны удалять `KEEP`.

Запрещено: использовать `X/UP`, yellow X/conflict, postfact outcome, TP/Stas3/exit, `old_removed`, `new_candidate`, `hard_filter`, `final_decision`, `trading_permission` как feature columns. Macro `WAVE` strip остается обзором; для ML используется только causal числовой SHORT/WAVE контекст.

## STAS5 V2 Strategy Audit Strip Is Not A Filter 2026-07-13

Статус: `process_guard / stas5_v2_strategy_audit_strip / audit_only`.

Риск: новая полоса `STAS4 Audit` на approval-графике может быть ошибочно воспринята как финальный фильтр входа. Это неверно. `X` в стратегической полосе означает только, что конкретный STAS4-блок считает старый вход шумным/рискованным. `UP` означает новый кандидат стратегии. Ни `X`, ни `UP` не являются human label, ML target, threshold или trading permission.

Правильная трактовка: четыре стратегии `density_profile+structure_ta`, `pattern+structure_ta`, `structure_ta+volume_flow`, `structure_ta+trend_momentum` используются для визуального аудита и будущей ablation-проверки. Human `KEEP` остается главнее strategy vote.

Запрещено: удалять `KEEP` из-за strategy `X`, превращать strategy `X` в hard-cut, использовать strategy `UP` как готовый вход, запускать ablation/training до пользовательского подтверждения approval PNG.

## STAS5 V2 Visual Approval Must Precede Ablation 2026-07-13

Статус: `process_guard / stas5_v2_feature_visual_approval_ready / wait_user_before_ablation`.

Риск: после V2 pre-ML audit статус `READY_FOR_V2_ABLATION_BASELINE` можно ошибочно прочитать как разрешение сразу запускать ablation/training. Пользователь отдельно попросил сначала увидеть один train-день с признаками на графике и подтвердить, что они стоят правильно.

Правильная трактовка: `STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png` является обязательным визуальным gate перед ablation. Он показывает train labels и V2 causal features на `2026-05-04`, но не создает ML model, threshold или trading permission.

Запрещено: запускать ablation baseline, V2 controlled model, threshold tuning, Optuna/scorer/target-lock/API, Stas3/TP или менять labels до пользовательского подтверждения approval PNG.

## STAS5 V2 Pre-ML Audit Is Not Production Permission 2026-07-13

Статус: `process_guard / stas5_v2_pre_ml_audit_ready / ablation_only_next`.

Риск: статус `READY_FOR_V2_ABLATION_BASELINE` можно ошибочно прочитать как разрешение на production model, threshold tuning или торговый вход.

Правильная трактовка: V2 pre-ML audit подтверждает, что данные чистые и информативные для следующего research шага. Следующий шаг - ablation baseline, где сравниваются группы признаков. Это еще не final model, не Decision Controller и не trading permission.

Запрещено: подбирать threshold по forward `2026-05-15+`, запускать Optuna/scorer/target-lock/API, подключать Stas3/TP/exit, считать forward postfact train-label или использовать audit expected decisions как торговую команду.

## STAS5 V2 Forward Error Ledger Is Audit Only 2026-07-13

Статус: `process_guard / stas5_v2_forward_error_ledger_ready / no_training_labels_from_forward`.

Риск: после появления классов `GREEN_BAD_*`, `YELLOW_*`, `SKIP_MISSED_GOOD` можно ошибочно использовать forward `2026-05-15..2026-05-20` как train labels, target tuning или готовое торговое разрешение.

Правильная трактовка: `stas5_forward_error_ledger_20260515_20260520_v0.csv` нужен для аудита ошибок, понимания риска и подготовки V2 pre-ML audit. Postfact-поля и user-review labels в нем не являются признаками модели и не являются approved train target без отдельного решения.

Запрещено: обучать V2 на этом ledger, подбирать threshold по нему, считать `v2_expected_decision` финальным trading permission, подключать Stas3/TP/exit или запускать API/Optuna/scorer/target-lock.

## STAS5 V2 Leakage Guard Is Not A Train Permission 2026-07-13

Статус: `process_guard / stas5_v2_leakage_guard_pass / no_training_before_error_ledger_and_audit`.

Риск: после `PASS` в `stas5_v2_leakage_guard_20260501_20260514_v0.json` можно ошибочно перейти сразу к V2 training, threshold tuning или V2 PNG.

Правильная трактовка: guard подтверждает только чистоту V2 feature matrix и causal time contract. Он не проверяет, какие признаки реально отделяют хорошие входы от шума, и не создает audit-target для плохих зеленых forward-входов.

Запрещено: запускать V2 training, ablation, threshold tuning, Optuna/scorer/target-lock/API, Stas3/TP/exit или финальный Decision Controller до `stas5_v2_forward_error_ledger.py` и V2 pre-ML audit.

## STAS5 V2 Feature Snapshot Is Not A Train Permission 2026-07-13

Статус: `process_guard / stas5_v2_feature_snapshot_ready / no_training_before_guard`.

Риск: после сборки `stas5_v2_feature_snapshot_20260501_20260514_v0.csv` можно ошибочно решить, что V2 уже готов к обучению или forward threshold tuning.

Правильная трактовка: snapshot только объединяет v1 Stas2/context features и V2 combo features с ledger по `day,candidate_id,record_id`. Он не является разрешением на обучение. Перед любым V2 train обязательны отдельные шаги: `stas5_v2_leakage_guard.py`, pre-ML audit и только потом controlled model/ablation.

Запрещено: запускать V2 training, Optuna/scorer/target-lock/API, подбирать threshold по `2026-05-15+`, подключать Stas3/TP/exit или превращать yellow X/strategy votes в hard-cut feature.

## STAS5 Forward User Review Must Stay Audit Only 2026-07-13

Статус: `process_guard / stas5_v2_forward_user_review / no_training_on_forward`.

Риск: после создания `STAS5_V2_USER_REVIEW_TEMPLATE_20260515.csv` можно ошибочно использовать выбранные пользователем 2-5 входов за `2026-05-15` как train labels или для подбора threshold.

Правильная трактовка: `2026-05-15` является blind forward audit. Пользовательские `USER_KEEP_FORWARD_AUDIT` нужны, чтобы понять, какие признаки отделяют реальные входы от шума, и спроектировать V2 gate/risk logic. Они не являются частью train `2026-05-01..2026-05-14`.

Запрещено: обучать V2 модель на `2026-05-15`, подбирать threshold по `2026-05-15`, считать `NOISE_FORWARD_AUDIT` финальным negative train label без отдельного решения.

## STAS5 V2 Combo Exporter Is Not A Final Model 2026-07-13

Статус: `process_guard / stas5_v2_combo_export_ready / no_final_training`.

Риск: после появления `stas5_v2_combo_features_*.csv` можно ошибочно решить, что V2 уже готов как торговое разрешение или что можно сразу обучать модель.

Правильная трактовка: `src/mlbotnav/stas5_v2_combo_feature_exporter.py` создает только causal feature-layer. Он уже прошел train/forward row parity и leakage checks по времени, но дальше обязательны `stas5_v2_feature_snapshot_builder.py`, V2 leakage guard, pre-ML audit и forward error ledger.

Запрещено: считать `stas5_v2_gate_long_allowed_final` финальным запретом входа без audit; подбирать threshold по forward `2026-05-15+`; использовать `postfact_*`, `ML_DECISION`, `yellow_x`, strategy votes, Stas3/TP/exit как признаки.

Разрешено: использовать V2 combo CSV как входной слой для следующего V2 snapshot/audit.

## STAS5 V1 Bad Green Entries Are Not Fixed By Threshold Only 2026-07-13

Статус: `process_guard / stas5_v1_audited / needs_v2_contour2`.

Симптом: на forward PNG `2026-05-15` часть зеленых `ENTER` стоит внутри падающего движения и дает только маленький отскок или сильную просадку. Аудит подтвердил: `2026-05-15` имел `14 ENTER`, `hit1.0=14.3%`, median drawdown `-2.834%`; `2026-05-16` имел `12 ENTER`, `hit1.0=16.7%`, median drawdown `-3.205%`.

Причина: STAS5 v1 технически корректен, но feature matrix неполная. Combo-spectrum/STAS4 indicator block существует, но был только `visual/audit layer`, не ML feature. Также нет отдельного `LONG_ALLOWED / NO_TRADE` gate и risk labels для `FALLING_KNIFE`, `TOO_HIGH_IN_DROP`, `WEAK_BOUNCE`.

Неправильное лечение: просто поднять `ENTER` threshold. Это не решает проблему, потому что bad `ENTER` имеют почти такие же `ML_KEEP_SCORE`, как good `ENTER`.

Правильное лечение: делать STAS5 V2 / contour 2 по `STAS5_ML_CORE/05_STAS5_V2_CONTOUR2_TZ_RU.md`: combo feature exporter, phase gate, long permission gate, risk/noise filter, forward error ledger и ablation.

Запрещено: использовать forward `2026-05-15+` для threshold tuning, превращать yellow X в hard-cut, использовать postfact fields как feature, подключать Stas3/TP/exit к entry ML.

## STAS5 Pipeline Must Not Bypass Guard/Audit 2026-07-10

Статус: `process_guard / stas5_entry_ml_pipeline_ready`.

Риск: после появления модели `stas5_entry_ranker_20260501_20260514_v0.joblib` можно ошибочно начать подбирать threshold по forward `2026-05-15+`, добавить yellow X как hard-filter, использовать Stas3/TP/exit или смешать postfact audit fields с feature matrix.

Правильная трактовка текущего этапа: controlled baseline уже разрешен и собран, но только после цепочки `ledger -> feature snapshot -> leakage guard -> pre-ML audit`. Любой следующий train должен снова проходить эту цепочку. Forward `2026-05-15..2026-05-20` служит blind визуальной проверкой и не является dev-набором для threshold tuning.

Запрещено:

1. использовать `postfact_*`, `hit_*`, `target_*`, MFE/MAE/TP/Stas3 как feature;
2. менять threshold по результату forward `15+`;
3. превращать `yellow_x` в hard-cut;
4. удалять `KEEP_DRAFT/KEEP_APPROVED + yellow_x = 1`;
5. запускать Optuna/scorer/target-lock/API/мост Bybit из STAS-5 entry ML.

Источник правды: `STAS5_ML_CORE/README_RU.md` и `STAS5_ML_CORE/artifacts/*`.

## STAS5 Memory Must Not Jump To Training 2026-07-10

Статус: `process_guard / stas5_memory_refresh / no_ml`.

Риск: после создания `STAS5_ML_CORE/` можно ошибочно сразу начать обучение, export, Optuna или заливку данных в старый ML-контур. Это преждевременно, потому что пока утвержден только draft-процесс: ledger -> pre-entry features -> audit.

Правильный следующий шаг: собрать ML-ledger по `972` входам `2026-05-01..2026-05-14`, сохранить `115` `KEEP_DRAFT`, `857` `CUT_DRAFT`, отдельно защитить `KEEP + yellow_x`, затем собрать causal feature snapshot и сделать audit без финального ML.

Запрещено: запускать training/export/scorer/target-lock/Optuna/API, использовать Stas3 post-entry TP как признак входа, превращать yellow X в hard-cut или считать `CUT_DRAFT` финальным negative без отдельного утверждения.

Source-of-truth: `STAS5_ML_CORE/README_RU.md`.

## STAS4 Old Reports Path Is Not Source Of Truth 2026-07-10

Статус: `process_guard / path_migration / no_ml`.

STAS4 перенесен в корень проекта: `STAS4_FEATURE_HYPOTHESIS_REVIEW`. Старый путь `reports/final_review/stas4_feature_hypothesis_screen_v0` не должен использоваться как рабочий источник.

При переносе Windows не смог удалить часть старых дневных директорий `20260504..20260514`, потому что они были заняты другим процессом. Эти директории являются остаточным хвостом после переноса. Не запускать новые STAS4-прогоны в старый путь и не считать его источником правды.

Правильный путь для новых STAS4-артефактов и ручной разметки:

```text
STAS4_FEATURE_HYPOTHESIS_REVIEW
```

## STAS5 Must Learn Human KEEP/CUT, Not Strategy X 2026-07-10

Статус: `process_guard / stas5_ml_entry / no_ml`.

Риск: можно ошибочно обучить STAS-5 на strategy vote или yellow X как на целевой разметке. Это превратит ML в копию старого фильтра и удалит часть хороших пользовательских входов.

Правильная трактовка: target для STAS-5 - это решение человека `KEEP/CUT` после утверждения. Strategy votes, включая желтый `X`, хранятся отдельно и используются только как контекст/audit. Первый baseline обязан исключать yellow-поля, `would_cut`, `strategy_cut`, `strategy_vote` из feature matrix.

Guard: `KEEP_APPROVED + yellow_x = 1` не может быть удален join-ом, фильтром или стратегией. `CUT_DRAFT` нельзя использовать как финальный negative без отдельного утверждения. Все признаки должны иметь `feature_available_at <= decision_time`.

Source-of-truth: `STAS5_ML_CORE/`.

## Yellow X Must Never Become Hard Cut 2026-07-10

Статус: `process_guard / yellow_x_audit_only / no_ml`.

Риск: желтый `X` стратегии `density_profile+structure_ta` можно ошибочно превратить в hard-filter, negative label или причину удаления кандидата перед ML. Это сломает обучение, потому что по текущей 14-дневной пачке `30` из `115` пользовательских KEEP_DRAFT имеют yellow X.

Правильная трактовка: `yellow_x = 1` означает только `strategy_vote/audit_flag`. Он не является `CUT`, не закрывает сделку, не запрещает вход и не участвует в первом target. При конфликте всегда побеждает human label: `human KEEP_APPROVED > strategy yellow X`.

Guard: будущий export/training должен падать, если строка `KEEP_APPROVED + yellow_x = 1` удалена после join или фильтрации. Feature matrix должна собираться через allowlist; yellow-поля по умолчанию исключены до отдельного ablation.

Формальное правило: `STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels/YELLOW_X_AUDIT_ONLY_RULE_RU.md`.

## STAS4 Manual Screenshot 20260514 Double-Bottom And Yellow-X Keeps 2026-07-10

Статус: `process_guard / stas4_manual_labels / no_ml`.

На скрине `2026-05-14` ранний double-bottom кластер около `03:50` содержит две отдельные красные пользовательские отметки. Их нужно трактовать как два KEEP: `LA014` и `LA015`, а не объединять в один вход. В плотном кластере после `14:00` зафиксированы KEEP `LA046`, `LA047`, `LA048`, `LA049`, а позже `LA053`, `LA055`, `LA056`; среди них `LA047` и `LA053` одновременно являются пользовательскими KEEP и желтыми `X` стратегии `density_profile+structure_ta`.

Граница: это ручная интерпретация конкретного PNG, не автоматическое правило фильтрации и не финальный ML-label.

## STAS4 Manual Screenshot 20260513 Cursor Split And Close Retests 2026-07-10

Статус: `process_guard / stas4_manual_labels / no_ml`.

На скрине `2026-05-13` первая красная отметка была разбита курсором на две маленькие красные части. Ее нужно трактовать как один пользовательский KEEP и сопоставлять с `LA002`, потому что `LA002` ниже ближайшего `LA001` и попадает в диапазон подчеркнутого места. В плотных участках этого же дня зафиксированы ручные решения: `LA043` вместо более раннего/высокого `LA042`, `LA072` вместо близкого `LA071`, а `LA058` одновременно является пользовательским KEEP и желтым `X` стратегии `density_profile+structure_ta`.

Граница: это ручная интерпретация конкретного PNG, не автоматическое правило фильтрации и не финальный ML-label.

## STAS4 Manual Screenshot X Calibration And Dense Clusters 2026-07-10

Статус: `process_guard / stas4_manual_labels / no_ml`.

При переносе красных подчеркиваний с PNG в LA-id нельзя слепо брать ближайший соседний маркер без просмотра кластера. Для скринов разной ширины нужна дневная X-калибровка по видимой ценовой панели. Пример: на `2026-05-12` PNG шириной `1502px` использована отдельная X-калибровка; `LA051` выбран по прямому времени подчеркивания перед близкими более поздними `LA052/LA053`, а `LA036` одновременно попал под желтый `X` стратегии `density_profile+structure_ta`.

Граница: эти корректировки являются human-review решением, не автоматическим фильтром и не финальным ML-label.

## STAS4 Manual Screenshot Labels Are Draft, Not ML Target 2026-07-10

Статус: `process_guard / stas4_manual_labels / no_ml`.

Симптом: при ручном подчеркивании входов на PNG легко начать считать `KEEP_DRAFT` и `CUT_DRAFT` готовой ML-разметкой или механическим правилом стратегии.

Правильная трактовка: текущие файлы `KEEP_YYYYMMDD_FROM_RED_UNDERLINES_DRAFT.csv` и `LABELS_YYYYMMDD_ALL_ENTRIES_DRAFT.csv` являются черновым human-review ledger. Они фиксируют мнение пользователя по конкретному визуальному дню и нужны для анализа, какие признаки могут объяснять выбор. Для финальной ML-выборки нужен отдельный утвержденный контракт: что является label, какие признаки causal до входа, какие hindsight-поля запрещены, как обрабатываются спорные кластеры.

Дополнительный guard: если красная отметка попадает рядом с несколькими LA-входами, выбирать ближайший нижний локальный вход и явно писать коррекцию в README разметки. Примеры: `2026-05-01 LA026` вместо `LA025`, `2026-05-04 LA032` в кластере и `LA049` вместо близкого `LA048`, `2026-05-05 LA026/LA036` как поздние ретесты при равном low с более ранними точками, `2026-05-06 LA021` как поздний ретест по прямому времени подчеркивания, `2026-05-07 LA014/LA017/LA019` как плотная первая группа, `2026-05-08 LA009/LA010` как два отдельных ретеста на одинаковом low, `2026-05-09 LA043/LA047` как нижние локальные входы в близких кластерах, `2026-05-10 LA045/LA051/LA056/LA059` как выбор нижнего визуального low вместо ближайшего соседнего LA, `2026-05-11 LA045/LA046` и `LA052/LA053` как отдельные пользовательские отметки в плотных кластерах.

Запрещено: запускать ML/export/training, scorer, target-lock, Optuna или превращать `CUT_DRAFT` в автоматический фильтр без отдельного утверждения.

## STAS2/STAS4 Tall Strips And Missing Right 00:00 2026-07-10

Статус: `fixed / visual_only / no_logic_change / no_ml`.

Симптом: на дневных Stas2/Stas4 графиках блок `ФОН/LONG/SHORT/WAVE` занимал слишком много вертикального места, из-за чего цена была менее крупной. Нижняя ось времени показывала шаги до `22:00`, но правая граница следующего `00:00` не была явной меткой.

Решение: в `src/mlbotnav/visual_entry_stas2_market_phase_review.py` добавлены общие компактные `OVERVIEW_HEIGHT_RATIOS` и helper `_set_day_time_axis`. `src/mlbotnav/visual_entry_stas4_family_overlay.py` использует те же размеры и ту же ось времени. Полосы стали примерно в 2 раза ниже, а ось времени теперь идет `00:00 ... 00:00`.

Граница: исправление только визуальное. Не менялись WAVE/GAP, LONG/SHORT, фазы, entry rows, CSV/XLSX, Stas1, Stas3, ML/export/training, scorer, target-lock или Optuna.

## STAS3 V2 Must Not Be Built On Old Stas3 2026-07-09

Статус: `fixed_guard / stas3_v2_clean / no_ml`.

Симптом: можно ошибочно взять старый `visual_entry_stas3_percent_ladder_review.py`, дописать туда V2-поля и назвать это новым Stas3 V2. Так уже был создан невалидный run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925`.

Правильная трактовка: принятый Stas3 V2 должен быть clean-проходом от Stas2 source и свечей, без наследования старых Stas3-таблиц, старых MFE/TP-решений и старой визуальной семантики.

Решение: актуальный clean-модуль `src/mlbotnav/visual_entry_stas3_v2_clean_review.py`, актуальный run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_clean_20260510_20260512_long_only_20260709_123622`. Старый old-base run помечен файлом `STAS3_V2_OLD_BASE_DRAFT_INVALID_RU.md`.

Запрещено: продолжать Stas3 V2 через старый Stas3-файл, открывать old-base run как финальный V2, переносить old-base reasonable TP/MFE-семантику в clean V2.

## STAS3 V2 Ideal TP Is Review Output, Not Live Exit 2026-07-09

Статус: `process_guard / stas3_v2_ready / no_ml`.

Симптом: после появления `ideal_review_tp_pct`, `max_feasible_review_tp_pct`, `tp_ladder_v2_decision` и V2-графиков можно ошибочно решить, что Stas3 V2 уже умеет в реальном времени выставлять take profit или закрывать сделку.

Правильная трактовка: Stas3 V2 разбирает уже найденные LONG-входы из Stas2 и показывает, что реально произошло после входа. `ideal_review_tp_pct` - это hindsight-review вывод по фактическому ходу цены, контексту и риску, а не live-сигнал. `MFE MAX` остается диагностическим максимумом после входа, не основной целью и не выходом.

Запрещено: использовать `ideal_review_tp_pct`, `max_feasible_review_tp_pct`, `hit_*`, `time_to_*`, `MFE MAX`, `WAVE/GAP/continuous` и `SHORT-risk` как готовую стратегию, scorer, target-lock, ML-label или causal feature без отдельной причинной разметки, где на каждый момент времени доступны только прошлые бары.

## STAS3 V2 SHORT Is Risk Context, Not Short Trade 2026-07-09

Статус: `process_guard / stas3_v2_long_only / no_ml`.

Симптом: в Stas2-графике есть строка `SHORT` и проценты противохода, поэтому следующий шаг может ошибочно начать строить short-входы, short-TP или общую LONG/SHORT статистику TP.

Правильная трактовка: в Stas3 V2 работаем только с LONG-входами. `SHORT` можно использовать только как процентный риск-фон/противоход для LONG, чтобы понимать давление против сделки. Для этого в таблицах должен быть явный маркер `short_context_only_flag`.

Запрещено: строить short-сделки, искать short-точки входа, считать short-TP, строить short-ladder, смешивать LONG и SHORT статистику TP или считать `SHORT`-волну отдельной стратегией выхода.

## STAS3 V2 Grid Must Not Reintroduce 0.2 As TP 2026-07-09

Статус: `process_guard / stas3_v2_tz / no_ml`.

Симптом: старый Stas3 V1 начинал процентную сетку с `0.2%`, из-за чего следующий агент может случайно вернуть `0.2%` как рабочий TP-уровень V2.

Правильная трактовка: в Stas3 V2 минимальная рабочая сетка начинается с `0.3%`. Значение `0.2%` допустимо только как шаг дальнего хвоста после `3.0%` или как историческое описание V1, но не как отдельный TP-уровень V2.

Запрещено: пересобирать Stas3 V2 с рабочим уровнем `0.2%`, смешивать LONG и SHORT статистику TP, использовать `MFE MAX` как выход или превращать ТЗ в стратегию/ML-label без отдельного утверждения.

## STAS3 V2 Must Not Invent Entry Points 2026-07-09

Статус: `process_guard / stas3_v2_entry_contract / no_ml`.

Симптом: после появления Stas2-графиков с low/entry легко снова начать выбирать вход глазами с PNG или двигать сделку к более красивому low.

Правильная трактовка: Stas3 V2 должен брать только готовые поля из выбранного `STAS2_RECORDS.csv`: `anchor_time_utc`, `anchor_low_price`, `entry_time_utc`, `entry_open_price`, `entry_price_5bps`. Основная цена расчета: `entry_price_for_calc = entry_price_5bps`.

Запрещено: искать новые low, переносить вход на более выгодную свечу, считать процент от `anchor_low_price` вместо цены входа, если это не отдельная диагностическая колонка. Если `entry_price_5bps` отсутствует, строка должна идти в skipped rows, а не считаться молча.

## STAS2 Short Strong Wave Percent Hidden 2026-07-09

Статус: `fixed / stas2_wave_visual_label / no_ml`.

Симптом: короткая, но сильная волна в строке `WAVE` могла остаться без подписи, потому что старое правило не рисовало текст для WAVE короче `15m`. Пример: `2026-05-12`, `W38 LONG 12:32-12:40`, длительность `8m`, ход `1.336303%`.

Решение: для confirmed WAVE с `visible_move_pct >= 1%` и длительностью `>= 5m` рисуется компактная подпись процента даже при длительности меньше `15m`. Расчет волн не менялся.

Контрольный run: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138`, `84` PNG, пустых PNG нет.

Запрещено: трактовать подпись как новый сигнал входа/TP или ML-label. Это только визуальная читаемость review-графика.

## STAS2 Day Boundary Must Not Close Wave 2026-07-09

Статус: `fixed / stas2_continuous_wave / no_ml`.

Симптом: если движение начиналось в конце UTC-дня и продолжалось на следующий день, старая дневная `WAVE`-логика могла резать его по `00:00` или превращать край дня в отдельный `GAP`. Это давало визуальную ошибку: цена идет одной волной, а график показывает два независимых дневных участка.

Решение: добавлен continuous-wave ledger без привязки к дню. `STAS2_CONTINUOUS_WAVES.csv` хранит полные волны, а `STAS2_MACRO_WAVES.csv` хранит только дневные срезы для PNG. Для перехода через день добавлены `macro_wave_carry_from_prev_day`, `macro_wave_carry_to_next_day`, `macro_wave_visible_move_pct`, `macro_wave_full_move_pct` и общий `continuous_wave_id`.

Контрольный run: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`, `29` continuous rows, `31` day slices, `4` carry-среза, `80` PNG, пустых PNG нет.

Запрещено: использовать полную будущую волну как causal feature на входе. Для ML потом нужна отдельная causal-разметка “что было известно в момент времени”, а не готовый hindsight full-wave.

## STAS2 Macro Wave GAP Is Coverage Segment, Not Signal 2026-07-09

Статус: `fixed / stas2_macro_wave_gap / no_ml`.

Симптом: на дневном overview строка `WAVE` могла иметь пустые участки без процента, особенно в начале/конце дня и вокруг коротких движений. Пользователь справедливо указал, что такие пропуски тоже надо учитывать, иначе визуально кажется, что часть движения не измерена.

Решение: в `STAS2_MACRO_WAVES.csv`, Excel-листе `Macro waves` и строке `WAVE` добавлены серые `GAP`-сегменты. Для них пишется `macro_wave_segment_kind=GAP`, `macro_wave_direction=GAP`, `macro_wave_move_basis=gap_range_pct`, а процент считается как диапазон внутри этого промежутка. Подтвержденные `WAVE`-блоки остаются отдельными строками с `macro_wave_segment_kind=WAVE`.

Контрольный run: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_gap_segments_v1_20260709_073810`, `34` macro-wave review rows = `28` WAVE + `6` GAP, `80` PNG, пустых PNG нет.

Запрещено: трактовать `GAP` как сигнал входа, фазу сделки, TP, short/long-разрешение или ML-label. Это только покрытие пропущенной области графика для ручного review. ML/Optuna/scorer/target-lock/API не запускать.

## STAS2 Macro Wave Is Hindsight Review, Not Entry Feature 2026-07-09

Статус: `process_guard / stas2_macro_wave / no_ml`.

Симптом: после появления строки `WAVE` на дневном overview легко ошибочно решить, что начало каждой macro-wave уже является готовым сигналом входа или готовой ML-меткой.

Правильная трактовка: `macro_wave_*` режет уже видимый дневной график на swing-блоки по развороту `1%`. Это нужно для ручного review больших движений и для обсуждения структуры будущей разметки, но это не causal feature для входа внутри этой же волны. Для ML такой слой можно использовать только после отдельной causal-разметки, где на каждый момент времени доступны только прошлые бары.

Контрольный run: `STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_short_macro_wave_v1_20260709_064759`, `34` macro-wave rows, `156` PNG, `0` пустых PNG.

Запрещено: использовать `macro_wave_direction`, `macro_wave_end_time_utc`, `macro_wave_move_pct` или границы будущей волны как pre-entry features, scorer, target-lock или ML-label без отдельного approved-ledger. ML/Optuna/API не запускать.

## STAS3 MFE Max Is Hindsight Review, Not Entry Signal 2026-07-07

Статус: `process_guard / stas3_big_move_review / no_ml`.

Симптом: после появления зеленой стрелки `SIGNAL/ENTRY -> MFE MAX` легко ошибочно решить, что максимум после входа можно использовать как доказательство правильного входа или как готовое правило удержания.

Правильная трактовка: `MFE MAX`, `entry_to_mfe_min`, `mfe_from_signal_pct`, `mfe_from_entry_pct`, `mae_before_mfe_pct`, `extra_after_0p2pct_pct`, `extra_after_1p0pct_pct` и `exit_review_bucket` являются post-entry review-полями. Они показывают, что реально произошло после входа, и нужны для ручного обучения: где `0.2%` было мало, где был ранний 1% с потенциалом трейла, где большой максимум пришел поздно, а где для максимума пришлось пережить глубокую просадку.

Контрольный run: `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_big_move_review_v2_20260707_090246`, `417` строк, `141` `EARLY_1PCT_TRAIL_REVIEW`, `218` `BIG_MFE_BUT_DEEP_MAE_REVIEW`, `51` `LATE_MFE_PUMP_REVIEW`, `95` PNG, пустых PNG нет.

Запрещено: переносить `MFE MAX` и `exit_review_bucket` обратно в Stas1/Stas2 как causal features, считать их approved ML-label, строить scorer/target-lock/стратегию или запускать ML/Optuna/API без отдельного ручного approved-ledger.

## STAS3 Horizontal TP Line Is Level, Not Trade Path 2026-07-07

Статус: `fixed / stas3_visual_review / no_ml`.

Симптом: на Stas3-графике желтая горизонтальная TP-линия визуально читалась как “отработка сделки”, хотя она показывала только уровень цены цели. Из-за этого было непонятно, почему TP не выглядит как движение цены от входа к тейку.

Решение: в `src/mlbotnav/visual_entry_stas3_percent_ladder_review.py` добавлена красная диагональная стрелка `ENTRY -> EXIT` на дневном обзоре и closeup-страницах. Красная стрелка показывает визуальный ход сделки от `entry_time_utc/entry_price_5bps` до точки TP/EXIT. Желтая `TP v0` и серая `TP 1%` горизонтали остаются только уровнями цены.

Контрольный run: `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_signal_entry_tp_move_v0_20260707_080253`, `417` строк, `83` PNG, пустых PNG нет.

Запрещено: трактовать этот визуальный слой как готовую торговую стратегию, scorer, target-lock или ML-label без отдельного ручного approved-ledger.

## STAS3 Percent Ladder Is Post-Entry Audit, Not Causal Feature 2026-07-06

Статус: `process_guard / stas3_post_entry / no_ml`.

Симптом: после появления Stas3 легко ошибочно взять `hit_1p0pct`, `time_to_1p0pct_min`, `actual_mfe_pct`, `actual_mae_pct`, `reasonable_tp_pct`, `tp_vs_1pct_label`, `mfe_hold_pct`, `mae_hold_pct` или `stas3_verdict` и подмешать их в Stas2/Stas1 как признаки входа.

Правильная трактовка: Stas3 специально смотрит свечи после `entry_time_utc`. Это слой ручного review сделки: percent ladder `0.2..7%`, фаза входа, фактическое движение, MFE/MAE, 5m/15m/30m/60m post-entry блоки, late-pump dependency, reasonable TP по фазовому профилю и первичная визуальная сортировка. Эти поля можно использовать для анализа качества уже найденных входов, но нельзя использовать как causal features, scorer, target-lock, ML-label или готовую торговую стратегию без отдельного approved-ledger.

Контрольный пример `2026-05-02..2026-05-03`: финальный run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260502_20260503_tp_ladder_v0_20260706_183011` имеет `110` строк, `0` skipped, все `110` достигают `1%` в окне `48h`, но только `2` попали в `FAST_CLEAN_1PCT`, `90` стали `LATE_PUMP_DEPENDENT`, `73` имеют mismatch к механическому 1% TP, `27` noise entry. Значит сам факт `+1% hit` остается грязным outcome и не является gold-разметкой.

Расширенный пример `2026-05-04..2026-05-09`: run `STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_tp_ladder_v0_20260707_055929` имеет `417` строк, `410` hit 1%, но только `13` `FAST_CLEAN_1PCT`, `238` `LATE_PUMP_DEPENDENT`, `285` mismatch к 1% TP и `84` noise entry. Это усиливает запрет превращать Stas3 напрямую в scorer или стратегию.

Запрещено: переносить Stas3-поля обратно в pre-entry logic, запускать ML/export/training, Optuna, scorer, target-lock или API по Stas3 CSV без отдельного ручного решения; считать `STAS3_TP_LADDER_V0_RU.md` готовой стратегией.

## STAS2 Is Closed Context, Not TP Engine 2026-07-06

Статус: `process_guard / stas2_closed / no_ml`.

Симптом: после принятия Stas2 легко ошибочно начать считать, что нижние полосы `Фон` и `LONG` уже дают готовый take profit или разрешают тянуть сделку до максимума.

Правильная трактовка: Stas2 закрыт только как pre-entry контекст. Он отвечает на вопросы: какой день, какая сессия, какой фон рынка, какая LONG-волна была до входа и насколько чистый setup у точки. Он не отвечает на вопрос, какой TP ставить после входа.

Следующий слой: Stas3 должен отдельно считать post-entry жизнь сделки: percent ladder, MFE/MAE, time-to-target, drawdown, 5m blocks, достижимый TP и validation вход/выход. Эти поля нельзя подмешивать в Stas2 как causal features.

Запрещено: запускать ML/export/training, Optuna, scorer, target-lock или API на основании одного факта закрытия Stas2; считать Stas2 setup готовым ML-label без ручного approved-ledger; использовать будущие свечи из Stas3 как признаки входа.

## STAS2 Strong LONG Context Was Read As Good Entry 2026-07-06

Статус: `fixed / stas2_visual_review / no_ml`.

Симптом: на дневном overview подписи рядом с точками вроде `bg Большая / long ...` визуально читались как “это хорошая точка входа”. Пользователь указал на участок `LA045-LA047` после резкого выноса: по факту такие точки планируется убирать, хотя Stas1 outcome мог закрыться в плюс.

Причина: Stas2 смешивал две разные вещи в одной подписи: фазу/амплитуду рынка до входа и качество конкретного low-входа.

Решение: добавлен отдельный слой `entry_setup_quality_*`. Теперь:

1. `Фон` показывает режим рынка.
2. `LONG` показывает pre-entry волну/ход вверх.
3. `SETUP` показывает чистоту конкретной точки: `CLEAN`, `OK`, `WARN`, `NOISE`.

Для `LA045-LA047` на `2026-05-02` новый run пишет в CSV/XLSX `NOISE: после выноса` / `NOISE: low слабый`. Это не меняет Stas1 outcome и не является ML-label; это review-фильтр для ручной чистки. На дневном overview текстовые названия возле точек не рисуются, чтобы график не шумел.

Запрещено: использовать setup как утвержденный ML-label без ручного approved-ledger, запускать ML/Optuna/scorer/target-lock/API, переносить сюда TP/exit/MFE/MAE.

## STAS2 Weak Background Does Not Mean No LONG Wave 2026-07-06

Статус: `fixed / stas2_visual_review / no_ml`.

Симптом: на Stas2 overview почти все часы могли выглядеть как `Слабая`, хотя на самом графике видны нормальные движения вверх. Это создавало ощущение, что Stas2 неправильно понимает рынок.

Причина: прежняя фаза была одной меткой для общего фона range/volatility/path и не отделяла направленную LONG-волну внутри часа или pre-entry окна.

Решение: `src/mlbotnav/visual_entry_stas2_market_phase_review.py` теперь разделяет:

1. `background_phase` / `Фон` - общий фон часа или окна;
2. `long_wave_phase` / `LONG` - направленная волна `low -> subsequent high`;
3. `pullback_from_high_pct` - откат от этой вершины к последнему закрытому close до входа.

Правило no-lookahead: для entry rows `long_wave` считается только по барам `open_time_utc < entry_time_utc`. Часовой `LONG` на дневном overview - audit закрытого часа и не является causal feature для входов внутри этого часа.

Запрещено: использовать Stas2 как TP/exit, MFE/MAE, time-to-target или percent ladder сделки; это Stas3. ML/Optuna/scorer/target-lock/API без отдельного решения не запускать.

## STAS2 Visual Review Must Stay Pre-Entry Only 2026-07-06

Статус: `process_guard / stas2_visual_review / no_ml`.

Симптом: после переноса фаз и сессий на графики легко начать использовать Stas2 как TP/exit-анализ или смотреть будущее движение сделки.

Правильная трактовка: `STAS2_MARKET_PHASE_REVIEW` показывает только контекст до входа. Entry context pages специально рисуют свечи только до `entry_time_utc`; в таблицах есть `context_max_open_time_utc` и `context_before_entry_check`. Если `context_before_entry_check` не `True`, такой ряд нельзя использовать как Stas2 pre-entry контекст.

Запрещено в Stas2: percent ladder сделки, TP validation, time-to-target, MFE/MAE, drawdown после входа, 5m post-entry blocks, best exit, scorer, target-lock, Optuna, ML/export/training/API.

Правильный следующий слой: Stas3 отдельно читает Stas2/Stas1 артефакты и уже после входа разбирает жизнь сделки по 5m-блокам.

## STAS2 CSV Opens As Mojibake Or Empty Excel 2026-07-06

Статус: `fixed / stas2_excel_export / no_ml`.

Симптом: Excel открывал Stas 2 CSV с русскими кракозябрами, а на диапазоне только выходных `STAS2_WEEKDAY_SESSION_SUMMARY.csv` получался почти пустым файлом и мог открываться как ошибка/пустой лист.

Причина: CSV писались в UTF-8 без BOM, а пустые summary rows не имели явного списка колонок.

Решение: `src/mlbotnav/visual_entry_stas2_market_phase_audit.py` теперь пишет CSV в `utf-8-sig`, сохраняет заголовки даже для пустых summary и создает `STAS2_MARKET_PHASE_TABLES.xlsx` для нормального просмотра в Excel.

Правило дальше: пользователю для просмотра давать `.xlsx`; CSV оставлять как машинные артефакты.

## STAS2 Phase Is Context Filter Not Future Label 2026-07-06

Статус: `process_guard / stas2_market_phase / no_ml`.

Симптом: после появления Stas 2 отчета можно ошибочно использовать фазу часа, посчитанную по всему закрытому часу, как признак для входа внутри этого же часа, либо считать `GOOD/BAD` Stas1 готовым ML-label.

Правильная трактовка: почасовая фаза в `STAS2_HOURLY_PHASES.csv` - audit состояния закрытого часа. Для конкретного входа использовать только `STAS2_STAS1_ENTRY_PHASE_CONTEXT.csv`, где `phase_before_entry` считается по свечам `open_time_utc < entry_time_utc`. Сессии хранить как `session_time_bucket` плюс отдельный `day_type`, а не как одну смешанную категорию; выходной `Лондон` не равен настоящей будней London-session. `hit_1pct`, target и future outcome не являются causal feature.

Запрещено: запускать ML/export/training, Optuna, scorer, target-lock или строить Stas 3/4/5 поверх Stas 2 без отдельного принятия схемы фаз/сессий.

## Do Not Treat Day Boundary As Forced Trade Close 2026-07-06

Статус: `process_guard / stas1_carry_outcome / no_ml`.

Симптом: если считать outcome только до `23:59` дня входа, хорошие late-day входы ошибочно становятся BAD, хотя `+1%` мог закрыться на следующем дне.

Правильная трактовка: в STAS1 `-Day .. -EndDay` ограничивает только создание входов. Для проверки target через ночь использовать `-OutcomeLookaheadHours`, например `48`. Запись остается в дне входа, а перенос фиксируется полями `hit_day_utc`, `hold_minutes_to_target`, `carried_overnight`, `outcome_status`.

Запрещено: подтягивать входы до стартового дня, создавать новые входы после `-EndDay`, использовать future outcome как causal feature или запускать ML/export/training/scorer/target-lock/Optuna/API без отдельного approval.

## Do Not Open Every STAS1 PNG As Separate Window 2026-07-06

Статус: `process_guard / stas1_browse_by_day / visual_review`.

Симптом: если открыть все `GOOD_1PCT_REVIEW_POOL_ALL_CLOSEUPS_PAGE_*.png` отдельными окнами, Windows/XnView забивается десятками окон, дни смешиваются, пользователь теряет связь между overview дня и closeup-страницами сделок.

Правильная трактовка: для ручного просмотра использовать `BROWSE_BY_DAY/`. Сначала открыть индекс или папку дня, затем открыть `00_YYYYMMDD_OVERVIEW.png` и листать стрелками только файлы этого дня.

Команды:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open index
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-04
```

## BAD Crosses Are Review Negatives, Not Short Signals 2026-07-06

Статус: `process_guard / stas1_all_closeups / no_ml`.

Симптом: после добавления BAD на closeup-страницы можно ошибочно решить, что красный крест является торговым сигналом, short-входом или причиной удалить строку из анализа.

Правильная трактовка: красный полупрозрачный крест в `GOOD_1PCT_REVIEW_POOL_ALL_CLOSEUPS_PAGE_*.png` означает только `BAD/no-hit/reject candidate` внутри визуального review. Эти строки нужны как отрицательные примеры и как материал для чистки шума. Их нельзя автоматически удалять из CSV/JSON и нельзя использовать как ML-label без отдельного approved-ledger.

Запрещено: считать BAD-крест short-сигналом, запускать ML/export/training/scorer/target-lock/Optuna/API или выкидывать BAD-строки без ручного решения пользователя.

## STAS1 GOOD Pool Is Main Review Tool, Not ML Dataset 2026-07-03

Статус: `process_guard / stas1 / no_ml`.

Симптом: после создания видной папки `STAS1_GOOD_LOW_REVIEW` можно ошибочно считать, что это новый ML-датасет или новая стратегия.

Правильная трактовка: `STAS1` - удобная обвязка вокруг уже существующего `src/mlbotnav/visual_entry_good_1pct_review_pool.py`. Он нужен для ручного review low-кандидатов и будущей калибровки шума в `src/mlbotnav/visual_entry_low_anchor_suggester.py`.

Запрещено: считать все `GOOD` строки gold-разметкой, использовать outcome `+1%/+0.5%` как causal feature, запускать ML/export/training/scorer/target-lock/Optuna/API без отдельного approval.

## Hedge Mode Is Risk Simulation Layer, Not Entry Signal 2026-07-02

Статус: `process_guard / hedge_mode / no_real_api / no_ml`.

Симптом: после обсуждения Bybit hedge mode можно ошибочно начать смешивать открытие противоположной SHORT-сделки с текущей логикой входов или считать это готовым способом спасать все DCA-перегрузы.

Правильная трактовка: hedge mode - это отдельный будущий risk-layer. Его можно проверять только после `DCA_RISK_AUDIT_V0` как `HEDGE_SIM_V0`: симуляция no-hedge против hedge, расчет маржи, комиссий, просадки, длительности и условий закрытия.

Запрещено: подключать реальные API-ключи, переключать настройки аккаунта, открывать боевые ордера, запускать ML/export/training/scorer/Optuna или использовать hedge как entry-сигнал без отдельного явного решения пользователя.

## Do Not Force 10 Trades Or Single 1pct Target 2026-07-02

Статус: `process_guard / daily_10_phase_ladder / no_ml`.

Симптом: цель `10` long-сделок в день можно ошибочно превратить в обязательство добирать до `10` любыми входами или мерить все дни только одним `+1%`.

Правильная трактовка: `10/day` - это верхний план/лимит качественных входов. Если день дает `1-3` качественных входа, не добирать мусор. Движение делить на фазы `0.3-0.5%`, `0.9-1.0%`, `1.5-2.0%`, `2.2-4.0%+` и изучать, какая фаза доступна в конкретный день/сессию.

Запрещено: считать `hit_1pct=true` автоматическим good, использовать достигнутую фазу как causal feature входа, подгонять входы под future outcome или запускать ML/export/training/scorer/Optuna без отдельного approval.

## Low Anchor 1pct V0 Is Superseded By Entry-Based V1 2026-07-02

Статус: `process_guard / superseded_v0 / no_ml`.

Симптом: старый слой `LOW_ANCHOR_1PCT_LABEL_REVIEW_V0` считал target от `anchor_low_price * 1.01`. После пользовательской правки это может дать неверное ощущение, что вход считается прямо от low.

Правильная трактовка: рабочим слоем считать `LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1`. В нем low-свеча является `signal`, вход строго на следующей свече, рабочая execution-цена `entry open + 5bps`, а target `+1%` считается от execution-цены.

Погрешность для обучения: только execution/slippage band `0bps/5bps/10bps`. Не двигать `signal_time_utc` и `entry_time_utc` ради попадания в outcome.

Запрещено: использовать V0 как текущую базу для gold/dataset, запускать scorer, target-lock, Optuna или ML/export/training без отдельного решения пользователя.

## Target 1pct Price Is Outcome Reference Not Entry Signal 2026-07-02

Статус: `known_boundary / target_1pct_price_fix / no_ml`.

Симптом: после фиксации цен `+1%` можно ошибочно начать использовать достижение цели, hit/no-hit или максимум дня как условие выбора входа.

Правильная трактовка: `target_1pct_price`, `hit_1pct`, `hit_time_utc` и `max_eod_pct` являются только outcome/reference полями для уже подтвержденных ручных входов.

Запрещено: использовать эти поля как causal feature, запускать scorer, target-lock, Optuna или ML/export/training без отдельного `APPROVED_FOR_ML`.

## Dataset Base Is Not APPROVED_FOR_ML 2026-07-01

Статус: `process_guard / dataset_base / no_ml`.

Симптом: создана единая база `TARGET_LED_DATASET_BASE_V0` с good/reject labels, и ее можно ошибочно принять за разрешение на ML.

Правильная трактовка: это только dataset base. В ней `ml_use_allowed_now=False`; `possible_entry` и `manual_shift_review` не имеют `ml_label`.

Запрещено: запускать обучение, ML-export, promotion, target-lock или Optuna без отдельного `APPROVED_FOR_ML`.

## BOS B018 Is Noisy As Standalone Long Signal 2026-07-01

Статус: `known_boundary / bos_repeat / no_ml`.

Симптом: отдельный повтор `B018_BOS` по `SOLUSDT 1m 2026-05-14` дал `41` `BOS_UP`, `42` `BOS_DOWN`, `8` `CHOCH-like` за день. Это слишком частые события для самостоятельной точки входа.

Правильная трактовка: `B018` не является одиночным `ALLOW` для лонга. Для лонга его можно использовать только как context/evidence: `down break -> reclaim/CHOCH -> локальный entry` или `BOS_UP` как подтверждение продолжения.

Запрещено: запускать scorer, target-lock, Optuna или ML по одному `B018`.

## V2E Broad Blocks Must Not Become Entry Filters 2026-07-01

Статус: `known_boundary / summary_matrix / no_ml`.

Симптом: в `V2E_SUMMARY_MATRIX` по `SOLUSDT 1m 2026-05-14 M01..M19` блоки `B014`, `B018`, `B009`, `B021`, `B022`, `B023` покрывают слишком много ручных входов.

Правильная трактовка: это context/evidence, а не самостоятельные `ALLOW`. Их можно держать как фоновые признаки для объяснения, но нельзя строить на них первый паспорт без более узкого локального правила.

Практический вывод: первый рабочий кандидат искать среди более выборочных блоков `B015`, `B017`, `B010`, `B013`, `B019`, `B020`, с обязательной проверкой локального движения и пользовательским visual review.

## Pattern V2D Has Broad Blocks 2026-07-01

Статус: `known_boundary / visual_audit / no_ml`.

Симптом: на `SOLUSDT 1m 2026-05-14 M01..M19` слой `B021_PATTERN_QUALITY` поддержал `19/19`, `B022_CHART_PATTERNS` поддержал `19/19`, `B023_PATTERN_CONFIRMATION` поддержал `17/19`, `B024_PATTERN_COMPOSITE_ENTRY` поддержал `16/19`.

Правильная трактовка: pattern-слой полезен как evidence/context, но `B021/B022` слишком широкие и не могут быть самостоятельным entry-фильтром. Их нельзя превращать в `ALLOW` без дополнительного локального правила: room/path, продолжение движения, трендовый контекст без EMA как active condition, и пользовательский visual review.

Запрещено: запускать scorer, target-lock, Optuna или ML по V2D без `V2E_SUMMARY_MATRIX` и отдельного решения пользователя.

## Stochastic V2C Is Too Broad As Entry Filter 2026-07-01

Статус: `known_boundary / visual_audit / no_ml`.

Симптом: на `SOLUSDT 1m 2026-05-14 M01..M19` слой `B009_STOCH14` поддержал `19/19` ручных входов.

Правильная трактовка: в текущем visual evidence режиме Stochastic слишком широкий и не может считаться самостоятельным entry-фильтром. Его можно оставить как контекст low/reclaim/cross, но нельзя по нему запускать scorer, target-lock, Optuna или ML.

Связанный вывод: `B008_ADX14` поддержал `16/19`, но ADX показывает силу движения, не направление. Это тоже контекст, а не самостоятельная стратегия.

## Do Not Jump From 14 May To T15 Before All Blocks 2026-07-01

Статус: `process_guard / fixed_current_rail`.

Симптом: после аудита `V2A_STRUCTURE_LAYER` был записан преждевременный следующий шаг “перенести V2A на `2026-05-15`”. Пользователь остановил это, потому что по 14 мая еще не применены все блоки.

Правильная трактовка: 14 мая является первым эталоном `M01..M19`. Его надо закрыть слоями `V2A -> V2B -> V2C -> V2D -> V2E`, и только после этого переносить выводы на `T15/2026-05-15`.

Запрет: не запускать scorer, target-lock, Optuna, ML/export/promotion и не считать `T15` следующим шагом, пока не готова summary matrix по 14 мая.

## V2A broad structure blocks are context, not signal 2026-07-01

Статус: `known_boundary / visual_audit / no_ml`.

Симптом: `B014_LEVEL_RANGE_CHANNEL` поддержал `18/19` ручных входов, а `B018_MARKET_STRUCTURE` поддержал `17/19`. Такой широкий охват может создать ложное ощущение, что эти блоки уже являются готовым `ALLOW`.

Правильная трактовка: `B014` и `B018` пока только structural context/evidence. Нельзя запускать по ним scorer, target-lock, Optuna или ML.

Эта прежняя строка superseded: не проверять `2026-05-15` как следующий шаг, пока 14 мая не закрыт по `V2B/V2C/V2D/V2E`.

## Fibo levels without anchor line are not enough 2026-07-01

Статус: `fixed_visual_artifact / context_note`.

Симптом: обычный zoom показывал горизонтальные Fibo-уровни, но не показывал, от какого pivot `A` до какого pivot `B` натянута сетка. В части входов один или оба anchor были за пределами локального entry-zoom, поэтому визуально Fibo выглядела непонятной.

Решение: добавлены отдельные Fibo-anchor страницы `V2A_FIBO_ANCHORS_PAGE_01_20260514.png` и `V2A_FIBO_ANCHORS_PAGE_02_20260514.png`, где видны `A -> B`, direction и уровни.

Процессный вывод: Fibo пока считать context/evidence. Перед превращением в active passport signal нужно правило свежести ноги, допустимого возраста anchor и расстояния от signal.

## V2A full-day zigzag lookahead risk fixed 2026-07-01

Статус: `fixed / visual_overlay / no_ml`.

Симптом: первый вариант `V2A_STRUCTURE_LAYER` строил `_zigzag_pivots()` по полному дню, а затем фильтровал pivots по `confirm_idx <= signal`. Это сохраняло риск, что Fibo/BOS будут косвенно зависеть от будущих pivot-замен в full-day zigzag.

Решение: `src/mlbotnav/visual_entry_strategy_passport_overlay_v2a.py` теперь пересобирает zigzag prefix-causal из подтвержденных pivot для каждого `signal/event`. Fibo и BOS/CHOCH больше не используют заранее собранный full-day zigzag.

Проверка: `M01..M19` сохранены, `entry_time = signal_time + 1m`, `entry_open_price` добавлен в CSV/zoom, scorer/target-lock/Optuna/ML не запускались.

## V2A structure overlay is visual only 2026-07-01

Статус: `known_boundary / visual_only / no_ml`.

Симптом: новый V2A overlay показывает паспортные блоки `B014/B015/B017/B018` рядом с ручными входами, поэтому его можно ошибочно принять за готовый `ALLOW`-scorer или торговый сигнал.

Правильная трактовка: это только visual review. `support/conflict/silent` в CSV означает визуальную поддержку блока, а не разрешение сделки. Entry price и `entry + 5 bps` являются execution/control only.

Запрещено по этому артефакту: запускать scorer, target-lock, Optuna, ML/export/promotion или считать, что паспорт уже выбран.

Если пользователь скажет, что картинка шумная, править визуальный слой и разнести `Fibo/BOS/retest` по отдельным страницам, а не менять ручные входы `M01..M19`.

## Do not recreate existing passports before overlay 2026-07-01

Статус: `KNOWN_PROCESS_RISK_FIXED_BY_RECONCILIATION`.

Симптом: после замечания пользователя можно ошибочно продолжить фразу “собрать паспорта по полочкам” как задачу заново создать/перенести паспорта.

Правильная трактовка: паспорта уже собраны. Текущий шаг — сверить существующие связки `Bxxx -> Fxxx -> passport MD -> matrix YAML -> runtime action` и наложить активные паспорта на два эталона `19+7`.

Зафиксировано:

1. `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_STRATEGY_PASSPORT_ROADMAP_RU.md`;
2. `docs/CALIBRATION_NODE_CURRENT/PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md`.

Агентский read-only аудит: `26` блоков, `82` активных не отключенных связки, `82` matrix YAML, все активные пути найдены. `B001_RET_N_TOURNAMENT` отключен как diagnostic и в overlay не берется.

Запрещено: создавать новые паспорта вместо сверки, запускать scorer/target-lock/Optuna/ML, смешивать все `B001-B026` в один общий сигнал.

## Do not skip passport inventory before strategy overlay 2026-07-01

Статус: `SUPERSEDED_BY_EXISTING_PASSPORT_RECONCILIATION`.

Риск: после V1 можно снова ошибочно прыгнуть сразу в один passport/scorer и потерять мысль пользователя. Пользователь уточнил порядок: не создавать паспорта заново, а сверить уже существующие блоки и потом делать strategy/passport overlay локальными участками на два эталона `19+7`.

Правильная рельса:
`docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_STRATEGY_PASSPORT_ROADMAP_RU.md`.

Manifest-сверка:
`docs/CALIBRATION_NODE_CURRENT/PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md`.

Запрещено до V2 visual review: scorer, target-lock, Optuna, ML/export/promotion.

## Initial Git commit needs explicit author and remote 2026-07-01

Статус: `resolved / git`.

Симптом: локальный репозиторий создан, но `git config user.name` и `git config user.email` не заданы, remote отсутствует.

Риск: коммит может получить неправильного автора, а push невозможен без URL пустого репозитория.

Решение: выполнено. Автор задан как `Stanislav1567 <Stanislav1567@users.noreply.github.com>`, `origin` добавлен на `https://github.com/Stanislav1567/MLbotNav.git`, initial commit `e178c49` отправлен в `origin/main`. Не коммитить тяжелые артефакты и секреты; они закрыты `.gitignore`.

## Indicator Hypothesis Review V1 lacks passport strategy overlay 2026-07-01

Статус: `KNOWN_GAP_NEXT_V2_STRATEGY_OVERLAY`.

`INDICATOR_HYPOTHESIS_REVIEW_V1` подписан как `RSI/MACD/Fibo/BOS/Volume`, но `Fibo/BOS/Swing` там являются визуальными подсказками, а не строгими паспортными расчетами. Нет `ALLOW 1/0` по `F012-F052`, нет матрицы `target_id -> passport hits`.

Правильное действие: не считать V1 стратегическим слоем. Следующий шаг — V2 strategy/passport overlay по тем же 26 ручным входам, без scorer/Optuna/ML.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_STRATEGY_PASSPORT_GAP_AUDIT_20260701_RU.md`.

## MLbotNav launch kit: project is not a Git repository 2026-07-01

Статус: `known_boundary / launcher_setup / no_code_change`.

Симптом: `C:\Users\007\Desktop\MLbotNav` сейчас не содержит `.git`, поэтому `git status` возвращает `not a git repository`.

Риск: агент может начать широкие правки без нормальной точки сравнения и без удобного diff-review.

Решение: запусковые скрипты предупреждают об отсутствии Git. `git init` не запускать автоматически; выполнять только после прямого согласия пользователя. До этого перед финалом опираться на список измененных файлов, проверки и ручной diff по конкретным файлам.

## Indicator hypothesis review V0 superseded by V1 for current 19+7 layer 2026-07-01

Статус: `known_process_note / artifact_scope / no_ml`.

Симптом: `INDICATOR_HYPOTHESIS_REVIEW_V0` был создан как feature/evidence слой, но до красных правок `T15 draft_ledger_v1`. Он включал старые `22` T15 candidates из feedback и старые времена `T15L02/T15L07/T15L08`.

Риск: если использовать V0 для текущего шага, можно сравнивать RSI/MACD/Fibo/BOS/volume не с финальными 7 входами, а со старым review pool.

Решение: текущим feature/evidence слоем считать `INDICATOR_HYPOTHESIS_REVIEW_V1_M01_M19_T15V1_READY_NO_SCORER_NO_ML_NO_OPTUNA`: `19` входов `M01..M19` плюс `7` входов `T15` из `draft_ledger_v1`. V0 оставить архивом. Scorer, target-lock, Optuna и ML/export запрещены.

## T15 draft-ledger v0 superseded by red-arrow v1 2026-07-01

Статус: `known_process_note / artifact_scope / no_ml`.

Симптом: `draft_ledger_v0` был собран до пользовательских красных стрелок и оставлял `T15L02`, `T15L07`, `T15L08` позднее нужного места.

Риск: если строить паспорт от v0, можно закрепить поздние входы и потерять ручную точность.

Решение: рабочим считать `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_RED_ARROW_FIX_READY_NO_SCORER_NO_ML_NO_OPTUNA`. В нем `T15L02` сдвинут на `02:34`, `T15L07` на `06:21`, `T15L08` на `08:31`. `draft_ledger_v0` не использовать для passport discussion.

## T15 draft-ledger is not target-lock 2026-07-01

Статус: `known_boundary / draft_only / no_ml`.

Симптом: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0` содержит 7 confirmed entries, цены входа и кластеры, поэтому его можно ошибочно принять за готовый паспорт или target-lock.

Риск: преждевременно запустить scorer, Optuna или ML/export до пользовательского review и до паспорта по одному кластеру.

Решение: считать слой только draft-ledger/discussion. Первый кандидат для следующего шага: `T15_C01_SUPPORT_RETEST_LOW`, но только после пользовательского `норм / фиксить`. `entry_open_price` и `entry + 5 bps` execution-only, не признак выбора входа.

## T15 user verdict v0 superseded by v1 2026-07-01

Статус: `known_process_note / artifact_scope / no_ml`.

Симптом: `user_verdict_v0` ошибочно сжал пользовательское “норм” до двух входов (`T15L06`, `T15L16`) и оставил остальные pending как weak/possible.

Риск: можно потерять хорошие ручные входы и нарушить правило “не считать улучшением версию, которая потеряла хорошие ручные входы”.

Решение: рабочим считать только `user_verdict_v1`, где подтверждены все 7 входов: `T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`. `user_verdict_v0` не использовать для draft-ledger/passport.

## Indicator hypothesis zoom price scale fixed 2026-07-01

Статус: `fixed_visual_artifact / no_ml`.

Симптом: первый вариант `INDICATOR_HYPOTHESIS_REVIEW_PENDING_ZOOM_20260515.png` получил неверную шкалу цены из-за volume-overlay на price-панели: объем был добавлен как абсолютная цена, а не как высота от нижней границы.

Риск: такой zoom выглядел размытым и не годился для ручного visual review.

Решение: исправлен расчет высоты overlay в `src/mlbotnav/visual_entry_indicator_hypothesis_review.py`, пакет пересобран. Использовать только актуальный PNG в `indicator_hypothesis_review_v0` с временем обновления после фикса.

## Indicator hypothesis review is not a scorer 2026-07-01

Статус: `known_boundary / visual_evidence_only / no_ml`.

Симптом: в одном пакете показаны RSI, MACD, volume, density, swing, BOS и Fibo, поэтому его можно ошибочно принять за готовую стратегию.

Риск: преждевременно передать признаки в scorer/Optuna/ML без ручного verdict пользователя.

Решение: считать пакет только visual evidence. Ручной verdict по 7 входам уже вынесен в `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`. Scorer, target-lock, Optuna и ML/export запрещены.

## Feedback v2 supersedes T15L feedback v1 2026-07-01

Статус: `known_process_note / artifact_scope / no_ml`.

Симптом: есть feedback слои `user_feedback_v0`, `user_feedback_v1`, `user_feedback_v2` для `2026-05-15`.

Риск: если открыть v1, можно считать `T15L10` pending, хотя пользователь уже добавил его в reject.

Решение: актуальным считать `user_feedback_v2`: `15` rejected, `7` pending. ML/export/Optuna запрещены.

## Feedback v1 supersedes T15L feedback v0 2026-07-01

Статус: `known_process_note / artifact_scope / no_ml`.

Симптом: есть два feedback слоя для `2026-05-15`: `user_feedback_v0` и `user_feedback_v1`.

Риск: если открыть v0, можно считать `T15L21` pending, хотя пользователь уже добавил его в reject.

Решение: актуальным считать `user_feedback_v1`: `14` rejected, `8` pending. ML/export/Optuna запрещены.

## Pending T15L candidates are not gold 2026-07-01

Статус: `superseded_by_T15_USER_VERDICT_V1 / no_ml`.

Симптом: после актуального feedback v2 по `2026-05-15` осталось `7` candidates без красного X: `T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Риск: можно ошибочно считать неперечеркнутые кандидаты хорошими входами. Это неверно: пользователь только отметил плохие, но не подтвердил good/shift.

Решение: эта заметка была верна до пользовательского уточнения “тут 7 должно входов”. Рабочим считать `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`, где все 7 неперечеркнутых кандидатов подтверждены как `user_confirmed_entry`. ML/export/Optuna запрещены.

## Transfer review T15L is not a label set yet 2026-07-01

Статус: `known_boundary / pending_visual_review / no_ml`.

Симптом: создан compact transfer review для `2026-05-15`: `22` кандидата `T15L01..T15L22`.

Риск: можно ошибочно считать эти кандидаты готовыми good/bad labels или новым scorer. Это только visual review proposal для пользователя.

Решение: до пользовательского verdict все `T15L##` имеют статус `pending_user_visual_review`. Разрешено только смотреть PNG и разметить: `норм`, `нет`, `сдвинуть`, `дубль`, `не тот тип`, `possible`. ML/export/Optuna запрещены.

## Use compact 2026-05-15 transfer folder, not broad scratch folder 2026-07-01

Статус: `known_process_note / artifact_scope / no_ml`.

Симптом: первый технический запуск `day_20260515` успел создать широкий набор PNG с `52` кандидатами и лишними страницами. После этого активный clean-пакет создан отдельно в `day_20260515_compact_v0`.

Риск: если открыть широкий scratch-пакет, можно принять лишние страницы за актуальный review.

Решение: активным источником для пользователя считать только `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/`. Scratch-папку не использовать для verdict.

## EMA is deferred, not an active filter 2026-07-01

Статус: `known_boundary / feature_policy / no_ml`.

Симптом: feature audit содержит EMA-колонки, и в кратком выводе могло прозвучать упоминание EMA рядом с рабочим контекстом.

Риск: можно преждевременно сделать EMA условием входа и замылить ранее выбранный template-led подход.

Решение: EMA пока reference-only. Следующие шаблоны/passport/checklist делать без EMA как active condition: структура, range-position, low/reclaim, volume/range/wick closed signal candle. EMA включать только после отдельного решения пользователя.

## Feature audit is not a model or scorer 2026-07-01

Статус: `known_boundary / audit_only / no_ml`.

Симптом: создан no-lookahead feature audit с признаками по `85` записям.

Риск: можно ошибочно считать этот audit готовым scorer или ML dataset. Это только сравнение групп и гипотезы признаков.

Решение: следующий шаг должен быть draft checklist/passport или zoom-lock, не ML/export. Любой scorer должен оставаться entry-only и не использовать entry-candle OHLCV/future outcome.

## Extra feedback summary is not ML dataset 2026-07-01

Статус: `known_boundary / summary_only / no_ml`.

Симптом: extra auto pool имеет полный feedback summary: `51 bad_noise`, `3 possible_entry`, `12 manual_shift_review`.

Риск: можно преждевременно превратить summary в ML dataset. Это опасно: `possible_entry` не gold, а `manual_shift_review` не является меткой входа.

Решение: следующий шаг только no-lookahead feature audit и/или отдельный zoom-review для manual shifts. ML/export запрещены без `APPROVED_FOR_ML`.

## Countertrend reject is manual anti-label 2026-07-01

Статус: `known_boundary / reject_label / no_ml`.

Симптом: page `06` rejected как `bad_noise_countertrend_entry`: входы не по рабочему тренду/направлению движения.

Риск: нельзя использовать результат после entry как future-looking правило. Нужно переводить countertrend-смысл в признаки, доступные до entry.

Решение: хранить как отдельную anti-label причину для будущего feature audit. ML/export запрещены.

## Entry mismatch reject is not manual shift 2026-07-01

Статус: `known_boundary / reject_label / no_ml`.

Симптом: page `05` имеет `bad_noise_weak_context_entry_mismatch`: пользователь отметил, что входы слабые/плохие, а часть стрелок auto-entry не совпадает с визуально нужной low/entry-зоной.

Риск: можно ошибочно трактовать это как `manual_shift_review` и начать создавать новые точки. Но пользователь здесь rejected страницу, а не просил переносить входы.

Решение: хранить page `05` как reject anti-label. Новые manual targets не создавать. ML/export запрещены.

## Manual shift review is not a label yet 2026-07-01

Статус: `known_boundary / manual_shift_pending / no_ml`.

Симптом: page `04` имеет `12` строк `manual_shift_review`: пользователь показал, что текущие auto-entry не gold и рядом нужны другие ручные точки.

Риск: если считать `manual_shift_review` positive или negative, dataset станет грязным. Это не готовый вход и не reject, а запрос на точную ручную фиксацию другой свечи.

Решение: хранить current auto-entry as not gold. Новые точки создавать только отдельным zoom-review с явным временем/ценой. ML/export запрещены.

## Weak context reject is a manual label, not a model rule 2026-07-01

Статус: `known_boundary / manual_feedback_label / no_ml`.

Симптом: page `03` получила all-reject verdict `bad_noise_weak_context`: low формально есть, но рабочий контекст слабый.

Риск: нельзя использовать слабость результата после entry как future-looking правило выбора. Нельзя также смешивать `weak_context` с `shallow_bounce`, если причины визуально разные.

Решение: хранить `bad_noise_weak_context` отдельной manual anti-label причиной. Для будущих признаков использовать только то, что видно до entry: структура до сигнала, положение в диапазоне, направление локальной структуры, близость сопротивления, качество reclaim. EMA пока не использовать как active condition. ML/export запрещены.

## Possible entry is not gold 2026-07-01

Статус: `known_boundary / possible_entry_not_gold / no_ml`.

Симптом: на page `02` пользователем выделены `LA018`, `LA020`, `LA026` как кандидаты, с которыми можно работать и где потенциально есть движение около одного процента.

Риск: нельзя автоматически переводить `possible_entry` в gold positive. Это не ручной эталон `Mxx`, а только кандидат на отдельный review.

Решение: хранить `possible_entry_one_percent_followthrough` отдельно от `manual_gold`. Для будущего scorer/ML сначала сравнить эти кандидаты с ручными good-входами и описать no-lookahead признаки. ML/export запрещены.

## Shallow bounce reject is a manual label, not a selection rule 2026-07-01

Статус: `known_boundary / manual_feedback_label / no_ml`.

Симптом: `LA001..LA012` получили reject-причину `bad_noise_shallow_bounce`, потому что пользователь визуально увидел короткий отскок/шум без нормального продолжения.

Риск: нельзя потом напрямую использовать future movement после entry как признак выбора входа. Иначе появится lookahead.

Решение: хранить `bad_noise_shallow_bounce` как manual anti-label. Для будущего scorer/ML переводить смысл в признаки, доступные до entry: структура движения до входа, расстояние до сопротивления, сила reclaim, структура диапазона, шумность до входа. EMA пока не использовать как active condition. ML/export пока запрещены.

## Extra auto review pack is pending user verdict 2026-07-01

Статус: `known_boundary / review_pack_created / no_ml`.

Симптом: visual review pack для `66` extra auto candidates создан, но пользователь еще не разметил страницы.

Риск: нельзя считать кандидаты из `extra_auto_review_v1` ни плохими, ни хорошими до visual verdict. Это только pending pool.

Решение: разбирать страницы по очереди. Для каждого кандидата использовать только явные ручные метки `bad_noise`, `duplicate`, `possible_entry`, `wrong_type`, `ignore_unclear`. ML/export запрещены.

## Extra auto candidates are unlabeled, not negatives 2026-07-01

Статус: `known_boundary / anti_review_needed / no_ml`.

Симптом: после resolved label-ledger V1 осталось `66` extra auto candidates, которые не являются ближайшими подтвержденными целями `M01..M19`.

Риск: нельзя автоматически считать эти `66` кандидатов плохими входами. Часть может быть полезными, часть дублями, часть шумом. Если пометить все как negative без review, будущий dataset будет испорчен.

Решение: следующий шаг должен быть `extra auto anti-review`: показать компактный PNG/таблицу и разметить `bad / duplicate / possible / wrong type / ignore`. ML/export запрещены.

## Pending shift review is not a label yet 2026-07-01

Статус: `known_boundary / labeling_not_complete / no_ml`.

Симптом: после feedback по `M03/M09/M10/M11` осталось `5` целей `M05/M14/M15/M16/M17`, где auto-кандидат рядом с ручным ledger, но имеет сдвиг `-1m..+3m`.

Риск: если передать эти pending-точки в event dataset как positive или negative без ручного решения, модель получит смешанные метки.

Решение: создан `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701.json`. Статус `manual_gold_pending_shift_review` не является обучающей меткой. Нужно ручное решение пользователя по PNG pending review.

## LOW_ANCHOR V0 +/-3m hit is not gold 2026-07-01

Статус: `known_process_risk / fixed_by_feedback_pack / no_ml`.

Симптом: `LOW_ANCHOR_ENTRY_SUGGESTER_V0` показывал `19/19 hits within +/-3m`, но пользователь красным отметил `M03`, `M09`, `M10`, `M11`, где авто-кандидат был рядом, но визуально не в нужной свечке или не в нужной low-anchor зоне.

Риск: если считать `±3m` золотым попаданием, будущий event dataset или ML выучит позднюю/неудобную свечу вместо ручного target-led эталона.

Решение: создан feedback-pack `user_feedback_v0`; правило обновлено: `hit_within_3m` = near-review, не gold. Gold берется только из ручного ledger и пользовательского visual verdict. Auto near-candidate может стать anti/near-not-gold примером.

## Low Anchor Suggester V0 is broad by design 2026-07-01

Статус: `known_boundary / review_helper_not_strategy / no_ml`.

Симптом: `LOW_ANCHOR_ENTRY_SUGGESTER_V0` на seed-дне поймал все `M01..M19` в пределах `±3m`, но оставил `85` кандидатов. Это много для стратегии.

Риск: если сразу ужать фильтр или запустить ML/Optuna, можно потерять хорошие ручные входы или обучить модель на шуме.

Решение: считать V0 только review-подсказчиком и источником positive/anti примеров. Следующий шаг только ручной visual verdict по zoom sheet: `норм / сдвинуть / нет / дубль / рано / поздно`.

## Monthly data-scope samples are local-data checks only 2026-07-01

Статус: `known_boundary / local_data_visual_audit / no_ml`.

Симптом: созданные full-day PNG по `2026-01-27`, `2026-02-28`, `2026-03-28`, `2026-04-28`, `2026-05-28` подтверждают полноту локальных `SOLUSDT 1m` CSV, но не являются внешней сверкой с интерфейсом биржи.

Риск: нельзя по этим PNG утверждать, что свечи совпали с внешним источником тиково/пиксельно. Можно утверждать только, что локальные файлы полные: `1440` строк, `00:00 UTC` до `00:00 UTC` следующего дня.

Решение: если нужна внешняя сверка, делать отдельный шаг `EXTERNAL_EXCHANGE_VISUAL_COMPARE`, без Optuna/ML/export.

## C01 multi-day source scope was underdocumented 2026-07-01

Статус: `known_process_gap / audited / no_ml`.

Симптом: фраза `126 дней` могла читаться как широкий multi-day/MTF прогон, хотя фактически это был scope `SOLUSDT 1m only`.

Факт аудита: локальные данные подтверждают `126` файлов `data/core/bybit_ohlcv/dt=*/tf=1m/symbol=SOLUSDT/part-final.csv`, `2026-01-26` .. `2026-05-31`, все по `1440` строк. C01 JSON/CSV сходятся по `25` кандидатам.

Ошибка процесса: `C01_MULTI_DAY_CHECK_V1_20260630.json` не содержит top-level `symbol`, `timeframe`, `source_csv_pattern`, диапазон дат и точную команду генерации.

Решение: будущий multi-day обязательно должен иметь source manifest в JSON до интерпретации результата. C01 V1 остается остановленным, Optuna/ML/export/promotion запрещены.

## C02A seed-lock is not multi-day 2026-07-01

Статус: `known_boundary / seed_lock_only / no_ml`.

Симптом: `M01/M02/M08` закреплены seed-lock на `2026-05-14`, но переносимость на другие дни еще не проверена.

Риск: нельзя считать C02A готовой стратегией и нельзя запускать Optuna/ML только на основании seed-lock.

Решение: следующий шаг только `9.1_MULTI_DAY_BENCH_OR_USER_DECISION_NEXT_PASSPORT_NO_ML_NO_OPTUNA`.

## C02A scorer is seed-day only 2026-06-30

Статус: `known_boundary / no_multiday_yet / no_ml`.

Симптом: `C02A_ENTRY_ONLY_SCORER_V0` чисто ловит `C02E03/M01`, `C02E04/M02`, `C02E10/M08` на `2026-05-14`, но это пока один seed-день.

Риск: нельзя считать scorer готовой стратегией или переносить в Optuna/ML до визуального review, target-lock и multi-day проверки.

Решение: следующий шаг только `7.1_USER_VISUAL_REVIEW_C02A_ENTRY_ONLY_SCORER_V0_BEFORE_TARGET_LOCK`. До пользовательского `норм` по PNG target-lock, multi-day, Optuna и ML/export запрещены.

## C02 is too broad for one scorer 2026-06-30

Статус: `known_boundary / split_required_before_scorer / no_ml`.

Симптом: C02 candidate layer имеет `10 GOOD_ENTRY / 6 BAD_ENTRY`, но good/bad аудит показал, что это не один чистый тип входа. Слой ловит общий low-event контекст и пересекается с `SUPPORT_RETEST_LOW`, `SWING_LOW_RECLAIM`, `HOT_RECLAIM_SUPPORT`.

Риск: если сразу сделать один scorer на весь C02, он смешает разные типы и будет плохо объясним на multi-day.

Решение: перед scorer выполнить `C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`.

## C02 review is labels-only, not a ready strategy 2026-06-30

Статус: `known_boundary / labels_complete_but_no_scorer_no_ml`.

Симптом: после ручной разметки `C02E01..C02E16` легко ошибочно принять `10 GOOD_ENTRY / 6 BAD_ENTRY` за готовый вход в сделку.

Факт: это только seed-day candidate review. Нет entry-only scorer, нет target-lock, нет multi-day pass, нет approval на Optuna/ML/export/promotion.

Решение: следующий шаг только `C02_AUDIT_GOOD_VS_BAD_AND_DECIDE_SCORER_RULES_NO_ML_NO_OPTUNA`. Любая версия C02 должна сохранять `M01/M02/M08` и не выбирать входы по future return, TP/SL, MFE/MAE или OHLCV entry-свечи.

## Only C01 passport was applied in fresh target-led stage 2026-06-30

Статус: `known_gap / passport_coverage_incomplete / no_ml`.

Симптом: после остановки `C01 V1` нельзя делать общий вывод, что весь fresh target-led подход плохой или хороший. Реально применен только один узкий паспорт `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0` по `M05/M06`.

Непокрытые типы: `DEEP_CAPITULATION_LOW`, `SUPPORT_RETEST_LOW`, `SWING_LOW_RECLAIM`, `TREND_DIP_CONTINUATION`. `M12` остается observe-only внутри hot-reclaim, но не целью C01 V1.

Mitigation started: создан `PASSPORT_COVERAGE_MATRIX_V0`, следующий паспорт `C02_DEEP_CAPITULATION_LOW` по `M01/M02/M08`.

Решение: следующий этап `PASSPORT_BENCH_V0`, начиная с `PASSPORT_COVERAGE_MATRIX_V0`, затем новый паспорт вне C01. Не запускать Optuna/ML/export/promotion.

Аудит: `reports/final_review/visual_entry_v3/fresh_target_led/process_audit/PASSPORT_BENCH_STAGE_AUDIT_20260630_RU.md`.

## C01 Entry-Only Scorer V0 is stale after M05 shift 2026-06-30

Статус: `known_risk / stale / no_ml`.

`C01_ENTRY_ONLY_SCORER_V0` был построен до ручного сдвига `M05`. Актуальная `M05`: signal `10:43 UTC` -> entry `10:44 UTC`; `M06` без изменений. Поэтому старый результат V0 нельзя считать текущим pass, target-lock, Optuna-кандидатом или ML/export/promotion-кандидатом.

Риск: если продолжить от старого V0, мы потеряем ручной фикс пользователя и снова смешаем рельсы. `M12` не включать автоматически: он остается observe-only до отдельного решения.

Mitigation: сделан `C01_ENTRY_ONLY_SCORER_V1` под актуальную `M05/M06`: на одном дне `2/2`, ложных `0`. После пользовательского `далее поехали по рельсам` создан seed target-lock для `M05/M06`. Это не production target-lock и не multi-day pass; следующий шаг должен быть multi-day C01 или следующий target-led паспорт. Не использовать future return, TP/SL, MFE/MAE и OHLCV entry-свечи для выбора входа.

## C01 V1 multi-day quality is mixed 2026-06-30

Статус: `known_risk / needs_visual_tuning / no_ml`.

Raw multi-day check V1 на 126 днях дал 25 кандидатов и максимум 2 в день, то есть частота не шумная. Но zoom contact sheet показывает смешанное качество: часть входов похожа на C01, часть возникает в продолжающемся снижении.

Решение: не считать V1 готовым входом в сделку. Сначала ручная оценка zoom-кандидатов, затем `C01_QUALITY_FILTER_V2` без Optuna и без ML.

## Visual Entry improvements lost good hits because there was no target-lock 2026-06-29
Статус: `ROOT_CAUSE_FIXED_BY_TZ_NOT_CODE_YET`.

Аудит и ТЗ: `reports/final_review/visual_entry_v3/target_locked_strategy_tz/visual_entry_target_locked_strategy_audit_and_tz_20260629_RU.md`.

Симптом: V10 уменьшил false относительно V9, но потерял хорошие входы V9: `03:24`, `10:49`, `15:19`, `18:50`, `20:50` на `2026-05-14`.

Причина: не было `target_lock_ledger` и regression-lock по ручным стрелкам. Поэтому новая версия могла улучшить общую чистоту, но ухудшить покрытие пользовательских входов.

Решение: перед V11 обязательно создать target-lock ledger и lock-файл. Любая версия, которая теряет locked target, получает `REGRESSION_LOST_LOCKED_TARGET_NO_ML`.

## V10 event rank reduces false but drops needed marked entries 2026-06-29
Статус: `DIAGNOSED_CLEANER_BUT_PARTIAL_NO_ML`.

Аудит: `reports/final_review/visual_entry_v3/event_ranked_bricks_v10/visual_entry_event_ranked_bricks_v10_audit_20260629T182810Z_RU.md`.

Симптом: V10 cluster-rank уменьшил количество ложных входов относительно V9, но вместе с шумом выбросил часть пользовательских целевых входов.

Факты по holdout `2026-05-14`:
1. Warm: V9 `5/17`, `16` false -> V10 `3/17`, `6` false.
2. Hot-first: V9 `4/17`, `20` false -> V10 `2/17`, `7` false.
3. Deep: V9 `4/17`, `33` false -> V10 `3/17`, `20` false.
4. Union: V9 `12/17`, `68` false -> V10 `7/17`, `33` false.

Решение: V10 не передавать в ML. Следующий слой должен быть `V11_RECOVER_RANKED_MISSES`, а не откат к широкому union. Нужно вернуть потерянные `10:48/20:49` warm, `15:19/18:50` hot-first и `03:25` deep отдельными подрежимами.

## V9 brick union still creates visual noise 2026-06-29
Статус: `DIAGNOSED_PARTIAL_NO_ML`.

Аудит: `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9/visual_entry_brick_by_brick_selector_v9_audit_20260629T180726Z_RU.md`.

Симптом: отдельные кирпичи V9 показывают полезные механики, но не дают стабильный чистый результат на двух днях. `V9_90_RESEARCH_UNION_ALL_BRICKS_DIAG` на holdout `2026-05-14` ловит `12/17`, но дает `68` false, то есть возвращает визуальную кашу.

Факты:
1. `V9_01_HOT_CHAIN_EVENT_LOW_BRICK`: validation `1/9`, `0` false; holdout `0` entries.
2. `V9_03_WARM_STRUCTURAL_RECLAIM_BRICK`: holdout `5/17`, `16` false; validation `0/9`, `23` false.
3. `V9_02_HOT_FIRST_STRONG_RECLAIM_BRICK`: holdout `4/17`, `20` false; validation `0/9`, `13` false.
4. `V9_04_DEEP_TERMINAL_RECLAIM_BRICK`: holdout `4/17`, `33` false; validation `0/9`, `25` false.

Решение: не передавать V9 в ML и не использовать broad/research union как стратегию. Следующий фикс качества: `V10_EVENT_RANKED_BRICKS`, где внутри каждого low-event выбирается один лучший сигнал, а `warm`, `hot-first`, `deep` ранжируются отдельно.

## CP06 does not generalize to marked 2026-05-13/2026-05-14 bottoms 2026-06-25
Статус: `EXPECTED_DIAGNOSTIC_GAP_NO_ML`.

Симптом: после создания ручных `manual_entries.json` для `2026-05-13` и `2026-05-14` слой `CP06_CP01_RECOVER_NOWICK_LATE_RETEST` был запущен без подкрутки и вернул пустой результат на обоих днях: `best=[]`, `rendered=[]`.

Классификация: это не зависание, не worker crash и не ошибка PNG-разметки. Это диагностический факт: механика, подобранная на DEV `2026-05-12`, не дала входов на новых пользовательских днах.

Решение: не передавать CP06 в ML и не считать `AK#` обучающими метками. Следующий слой должен быть новым `REVERSAL_BOTTOM_KNIFE_DROP_V0`, где отдельно проверяются контекст падения, зона дна, подтверждение остановки продажи и подавление повторных ложных входов.

## CP06 validation/holdout cannot run without manual labels 2026-06-25
Статус: `EXPECTED_BLOCKER_NOT_RUNTIME_ERROR`.

Симптом: после закрытия DEV `2026-05-12` слоем `CP06_CP01_RECOVER_NOWICK_LATE_RETEST` нельзя честно посчитать validation `2026-05-13` и holdout `2026-05-14`, потому что для этих дней нет `manual_entries.json` с `entries[].target_entry_time_utc`.

Решение: сначала получить пользовательские стрелки или список времен UTC по seed PNG, затем создать `manual_entries.json` с сохранением `source_csv` и `source_csv_sha256`, и только после этого запускать CP06 без изменения параметров.

Это не ошибка runner, не зависание и не повод подбирать параметры на validation/holdout. Аудит: `reports/final_review/visual_entry_v3/cp06_validation_holdout_readiness/cp06_validation_holdout_readiness_20260625_RU.md`.

## Visual Entry DEEP_CAPITULATION_RECLAIM raises recall but is still too noisy 2026-06-25
`DQ01_EQ01_PLUS_DEEP_RECLAIM` поднял попадания до `10/11`, но дал `73` ложных входа. `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP` поймал все `11/11`, но дал `95` ложных входов.

Решение: это не runtime bug и не ML-кандидат. Слой использовать как DEV-карту механик: `D01` для `12:33`, `D02` для `15:26`, `D03` для `17:00`. Следующий фикс качества: `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`, особенно кластерный приоритет и отдельная судьба high-risk `08:26` no-wick.

## Visual Entry EARLY_FLUSH_REVERSAL is useful but still too noisy 2026-06-25
`EQ01_Q09_SEVERE_SOFT45` поднял попадания до `7/11`, но дал `68` ложных входов. `EQ03_Q09_SEVERE_SOFT45_NOWICK` поймал `8/11`, включая все ранние `01:42`, `05:13`, `07:16`, `08:26`, но дал `90` ложных входов.

Решение: это не runtime bug и не ML-кандидат. Слой использовать как DEV-диагностику механик раннего дна. `E05_NO_WICK_LOW_CLOSE_CD15` держать как high-risk diagnostic: он может ловить `08:26`, но без entry-свечи легко превращается в ловлю падающего ножа.

Следующий фикс качества: отдельный `DEEP_CAPITULATION_RECLAIM` и затем более строгий ensemble/suppression.

## Visual Entry quality filter is still too noisy 2026-06-25
`Q09_ENSEMBLE_Q07_Q01` улучшил micro-bottom с `135` false до `53` false при тех же `4/11` попаданиях, но это все еще не кандидат. Не переводить в ML и не считать готовой стратегией.

Причина: один общий фильтр качества смешивает разные типы дна. Нужны отдельные подсемьи `EARLY_FLUSH_REVERSAL` и `DEEP_CAPITULATION_RECLAIM`, иначе ensemble либо теряет ранние стрелки, либо возвращает лишний шум.

## Visual Entry v3 micro-bottom limitations 2026-06-25
`VISUAL_MICRO_BOTTOM_SIGNATURE_V0` ловит форму пользовательского дна лучше паспортных семей, но дает чрезмерный шум: `4/11` hit при `135` false. Это не ошибка рантайма, а ограничение текущих признаков: local-low/нижняя зона range слишком широко срабатывают на обычные локальные минимумы.

Еще один зафиксированный риск: большие Markdown/JSON отчеты без UTF-8 проверки могут визуально выглядеть как mojibake в PowerShell. Проверять через Python UTF-8 или `text_guard`, финальные `_RU.md` должны быть читаемыми.
## Passport-family visual bottom layer is too weak 2026-06-25
Статус: `DIAGNOSED_COMBO_REQUIRED_NO_ML`.

Аудит: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_audit_20260625_RU.md`.

Симптом: честные no-lookahead семейства паспортов (`DEEP_CAPITULATION`, `SUPPORT_WICK_REVERSAL`, `DIVERGENCE_AT_SUPPORT`, `CHOCH_REENTRY`, `VPOC_RANGE_RECLAIM`) на v3 DEV-разметке ловят максимум `1/11` точек и дают много ложных входов.

Лучший результат: `DEEP_CAPITULATION_NEXT_OPEN`, `1/11` hits, `20` false, `21` entries, `f1=0.0625`.

Решение: это не ML-кандидат и не runtime-инфраструктурная ошибка. Не раздушивать текущие паспорта до шума. Следующий слой должен быть отдельным `VISUAL_MICRO_BOTTOM_SIGNATURE_V0` с обязательным exact scorer и PNG overlay. В ML ничего не передавать.

## Visual Entry lookahead combo is not tradable 2026-06-25
Статус: `DIAGNOSED_LOOKAHEAD_DIAGNOSTIC_ONLY`.

Старый `visual_entry_combo_search` использовал `green_entry_candle`, то есть знал закрытие входной свечи. Для логики входа на `open` следующей свечи это lookahead. Его отчеты можно использовать только как визуальную диагностику, не как торгового кандидата.

Честный no-lookahead runner: `src/mlbotnav/visual_entry_no_lookahead_candidates.py`. Лучший DEV v3 результат пока `3/11` и `34` false, поэтому в ML ничего не передавать.

## B001 visual score has too many false entries 2026-06-25
Статус: `DIAGNOSED_NOT_ML_CANDIDATE`.

Scorer report: `reports/qa_gate/visual_entry_score_SOLUSDT_1m_visual_dev_20260625_20260512_v1_oos_backtest_trades_SOLUSDT_1m_2026-05-12_long_only_20260625T073603Z.json`.

Симптом: по ручной DEV-разметке `2026-05-12` старый B001 diagnostic ловит `3/6` целей, но дает `15` лишних входов из `18` и отрицательный `net_return_pct=-62.229358575198916`.

Решение: это не инфраструктурная ошибка и не повод передавать в ML. B001 momentum family можно использовать только как диагностический источник части поздних входов; ранние входы у дна требуют отдельной reversal/dip-buy family и проверки через visual scorer.

## Simple reversal prefilter is too noisy 2026-06-25
Статус: `DIAGNOSED_NOT_CANDIDATE`.

Prefilter report: `reports/qa_gate/visual_entry_prefilter_search_20260512_DEV.json`.

Симптом: простой `REVERSAL_DIP_BUY_LONG_PREFILTER_V0` по RSI/Stoch/range/ret/cooldown ловит часть ручных стрелок, но дает слишком много лишних сигналов. Лучший вариант после cooldown `60` дал `2/6` попаданий и `19` лишних сигналов; лучший ранний вариант ловит `01:44`, `04:15`, `09:12`, но дает `36` лишних сигналов.

Решение: не продвигать prefilter в ML и не считать его торговым кандидатом. Нужна отдельная family с trigger/suppression/backtest и проверка через visual scorer.

## Solo visual passports are not enough as standalone strategy 2026-06-25
Статус: `DIAGNOSED_COMBO_REQUIRED_NO_ML`.

Отчет: `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV_RU.md`.

Симптом: одиночные паспорта либо ловят мало ручных стрелок, либо дают слишком много ложных входов. Лучшие диагностические примеры: `F009_EMAGAP_DOWN` ловит `2/6` при `6` ложных входах; `F059_ENGULFBULL` очень чистый (`0` ложных), но ловит только `1/6`; `B001_RET_N_FIXED` ловит `5/6`, но дает `142` ложных входа.

Решение: не продвигать solo-passport результат в ML и не считать одиночный паспорт стратегией. Следующий слой должен быть combo/family: контекст падения/растяжения + свечной reversal trigger + suppression частых ложных входов, затем обязательный PNG overlay и visual score.

## B001 marked-entry fixed backtest is negative, not infrastructure error 2026-06-25
Статус: `NO_INFRA_ERROR_DIAGNOSTIC_NEGATIVE`.

Аудит: `reports/qa_gate/b001_marked_entry_fixed_backtest_audit_20260625T073900Z_RU.md`.

Симптом: фиксированные параметры B001 по пользовательским стрелкам дают автоматические входы, включая точные попадания `09:25` и `12:36`, но общий OOS отрицательный.

Факты:
1. с `min_expected_move_pct=0.001`: `18` сделок, OOS `-47.05387771496912%`;
2. с `min_expected_move_pct=0.0`: `30` сделок, OOS `-67.41968770852606%`;
3. `17:15` не входит, потому что `prob_up=0.3748` ниже `p_enter_long=0.60`, хотя F-гейт дает `4/5`;
4. `08:15` и `15:48` не проходят семейный F-гейт.

Решение: это не зависание, не worker crash и не баг shared-study. Это отрицательная диагностическая гипотеза. В ML ничего не передавать. Для входов около дна проектировать отдельную reversal/dip-buy family.

## Shared-Study Small Budget Profile Edge Coverage Warning 2026-06-24
Статус: `FIXED_CONFIRMED_BY_RUNTIME_SMOKE`.

Фикс 2026-06-25: `reports/qa_gate/shared_study_profile_edge_coverage_fix_20260625T063700Z_RU.md`.

Причина: профильные edge-пробы использовали `run_trial_index + profile_edge_worker_offset`, затем обычный trial counter расходовал edge slots даже для trial, которые prune-ились до profile sampling. В shared-study process-pool это оставляло хвостовые max-задачи непокрытыми.

Исправление: profile edge forcing использует отдельный счетчик фактического profile sampling и распределяет min/max edge-задачи между process workers через `--process-workers-total`; `profile_edge_worker_offset` сохранен только как диагностический атрибут.

Проверки: `tests.test_optuna_search_runtime` PASS `73/73 OK`, `py_compile` PASS, `PSParser` PASS, `text_guard` PASS.

Runtime confirmation: `b001_3of5_long_shared_edgefix3_20260625_115056`, final snapshot `w3`: terminal `42/42`, core `5/5 PASS`, profile `7/7 PASS`, forced min/max полный `7/7`.

Симптом: shared-study process-pool на бюджете `OptunaTrials=42` завершает worker-ы штатно, core edge coverage закрывается, но часть profile edge coverage остается непокрытой.

Наблюдение на `B001 family-unified 3/5 LONG`: core coverage `5/5 PASS`, profile coverage `4/7 PASS`, failed profiles `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`. Аудит: `reports/qa_gate/b001_family_unified_3of5_long_shared_audit_20260624T195200Z_RU.md`.

Наблюдение на пользовательском повторе `B001 family-unified 4/5 LONG`: core coverage `5/5 PASS`, profile coverage `2/7 PASS`, failed profiles `F001_thr_pct`, `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`, `F005_thr_pct`. Аудит: `reports/qa_gate/b001_family_unified_4of5_long_shared_repeat_audit_20260624T195100Z_RU.md`.

Похожий pattern был виден и на shared `4/5 LONG`: core edges закрывались, часть profile edges оставалась непокрытой при том же бюджете.

Граница: это не зависание, не worker crash и не ML-кандидат. Результаты таких запусков можно использовать как runtime diagnostic, но не как clean proof полного edge coverage. Перед large-переходом или строгим coverage-закрытием нужно отдельно решить: увеличить бюджет/проверить edge forcing или явно принять diagnostic-only статус.

## Shared Optuna Study Requires Non-SQLite Storage 2026-06-24
Статус: `GUARDED`.

Симптом риска: если три process-pool worker писать в одну Optuna study через `sqlite`, возможны блокировки и нестабильный параллельный доступ.

Фикс: shared-study режим перед стартом worker проверяет Optuna storage. Если storage имеет схему `sqlite`, запуск должен остановиться. Проверенный рабочий storage: `postgresql`.

Аудит: `reports/qa_gate/optuna_shared_study_process_pool_audit_20260624T190435Z_RU.md`.

Правило: для `-SharedOptunaStudy` использовать только не-`sqlite` storage. Если нужен локальный одиночный режим без общей study, можно использовать обычный `3x3/9` без `-SharedOptunaStudy` или diagnostic `1x9/9`.

## Shared Study Worker Artifact Collision 2026-06-24
Статус: `FIXED`.

Симптом риска: при общей Optuna study несколько worker могли писать отчеты и artifact-файлы с одинаковыми именами, из-за чего последний worker мог перетереть результат предыдущего.

Фикс: pipeline reports, `study_summary`, `best_trials_topk`, `trial_history` и `grid_edge_coverage_audit` получили worker suffix. В trial-history добавлены `worker_contour_id`, `study_namespace`, `shared_study_id`, `shared_optuna_study`, `sampler_seed_effective`, `profile_edge_worker_offset`.

Проверка: runtime smoke B001 `4/5 LONG` создал отдельные отчеты для `w1`, `w2`, `w3`; full `tests.test_optuna_search_runtime` прошел `71/71 OK`.

## B001_COMBO_DIAG визуально выглядит как узкий участок 2026-06-24
Статус: `DIAGNOSED_NOT_RENDER_CROP`.

Симптом: на обычных скринах LONG и SHORT казалось, что сделки сработали в одном узком участке дня, хотя похожие свечи были и в других местах.

Проверка: `src/mlbotnav/render_gate_diagnostic.py` построил полный день и слои runtime. Сырой день содержит `1440` минутных свечей. LONG режется на `F-gate` (`621 -> 4`), SHORT режется на `min_expected_move_pct=0.001` (`240 -> 2` после F-gate).

Артефакты:
1. `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.png`.
2. `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.png`.

Правило: при споре "почему не вошли в похожую свечу" смотреть layered gate diagnostic, а не только финальные entry/exit markers.

## B001 old AND combo tournament can strangle entries 2026-06-24
Статус: `FIXED_FOR_DIAGNOSTIC_N_OF_M`.

Аудит: `reports/qa_gate/b001_combo_diag_n_of_m_audit_20260624T125500Z_RU.md`.

Симптом: старый `B001_RET_N_TOURNAMENT` объединял несколько `F001..F005` через жесткое `AND`, из-за чего исторически `28/31` комбинаций дали zero-trade. Это не подходит под новую задачу "раздушить" совместную калибровку.

Фикс:
1. добавлен `entry_action_min_confirmations`;
2. диагностическая combo-политика стала `N_OF_M_present_action_columns`;
3. runtime использует реальные gate-колонки `F001_RET1_ALLOW..F005_RET24_ALLOW`, а не несуществующую `B001_RET_N_ALLOW`;
4. process-pool больше не выбирает пустой `0 сделок / 0%` как лучший worker, если есть tradeful-ветка.

Правило: `B001_COMBO_DIAG` diagnostic-only, не заменяет solo-route и не передается в ML.

## Block Runner Terminal JSON Noise 2026-06-24
Статус: `FIXED_AFTER_B001_5`.

Аудит: `reports/qa_gate/b001_large_short_b001_5_audit_20260624T094057Z_RU.md`.

Симптом: после завершения `APTuna/run_block_family_selection.ps1` терминал получал полный `payload | ConvertTo-Json -Depth 30`, из-за чего вместо понятной строки по входу/выходу/profit появлялась большая JSON-каша.

Фикс: в `APTuna/run_block_family_selection.ps1` добавлена краткая терминальная сводка по F-ID: status, OOS net, trades, счетчики `raw/mode/gate/min/fill`, runtime-диагностика и первые строки сделок `вход -> выход -> profit`, если сделки есть.

Полный JSON по-прежнему сохраняется в `reports/qa_gate/block_family_selection_*.json`. Если нужен машинный stdout, использовать новый флаг `-EmitJson`.

Проверка: B001 SHORT `-DryRun` печатает краткую таблицу без полного JSON; focused pytest `47 passed`; text_guard `PASS`.

## B001 block runner false/missing winner risks 2026-06-24
Статус: `FIXED_IN_RUNNER_UPDATED_AFTER_B001_4`.

Аудиты:
1. `reports/qa_gate/b001_smoke_1d1d_audit_20260624T075006Z_RU.md`.
2. `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.

Найдено при B001 smoke:
1. родительский runner не разбирал многострочный JSON process-pool и мог оставлять пустые `process_pool_summary`, `adaptive_summary_path`, `best_oos`;
2. лучший доступный отрицательный или нулевой результат мог ошибочно стать `block_winner`;
3. dry-run мог получать общий статус `PARTIAL_OR_FAILED`.
4. B001.4 показал дополнительный отчетный риск: `runtime_diagnostic_status` был в `oos_report`, но мог не попадать в блоковый `best_oos`.

Фикс в `APTuna/run_block_family_selection.ps1`:
1. добавлен устойчивый разбор последнего JSON-объекта из stdout;
2. `block_best_available` отделен от `block_winner`;
3. `block_winner` допускается только для достижимого, tradeful и положительного OOS;
4. dry-run дает `OK`, если все строки имеют статус `dry_run`;
5. runtime-диагностика переносится из связанного `oos_report` в блоковый `best_oos`, если adaptive summary ее не содержит.

Проверка: manifest pytest `2 passed`, dry-run `status=OK`, text_guard `PASS` на `reports/qa_gate/recovery_r5_text_guard_20260624T075150Z.json`.

## Exchange-Like Min-Move Can Remove All Post-Gate Signals 2026-06-24
Status: `FIXED_WITH_RUNTIME_GUARD`.

Audit: `reports/qa_gate/ml_optuna_zero_trade_min_move_diagnostic_20260624T051535Z.md`.

Symptom: OOS reports show `0` trades and `0` profit even when action gates produced signals.

Confirmed case: F067 LONG OOS had `1415` signals after `F067_PATTERNSTRENGTH_ALLOW`, but selected `min_expected_move_pct=0.01` removed all entries. The max OOS proxy after gate was `0.005140`.

Risk before fix: continuing WBS unchanged could produce more misleading zero-trade NO_GO reports.

Fix: added `MIN_MOVE_UNREACHABLE` classification, backtest/OOS diagnostics, Optuna fail-key/penalty and grid-min retry, adaptive selection skip, safer default min-move grid, and regression tests.

Validation: focused pytest `124 passed`; final text_guard `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260624T063715Z.json`.

## Route Navigation Warning 2026-06-23
Status: `KNOWN_NAVIGATION_RISK_UPDATED_BLOCK_ROUTE`.

Current audit: `reports/qa_gate/block_family_passport_route_audit_20260624T064900Z.md`.

Previous audit: `reports/qa_gate/ml_optuna_route_memory_audit_20260623T205751Z.md`.

Some lower historical sections in current documents still mention old next-step pointers such as `5.3`, old grouped B019/B020 results, or `8.2.19 F068`. Use the top current override/status sections as authoritative.

Correct current route: block-family calibration. Next strict step is `BLOCK_ROUTE_1 Run B001 family solo-selection after min-move fix`, LONG then SHORT sequentially. Do not continue the old F-by-F route unless the user explicitly reopens it.

Last updated UTC: 2026-06-24T06:59:32Z

## No Trade Candidate In ML Optuna Calibration Stage 8.2.18 F067
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.18`.
2. Status: no runtime blocker.
3. Result: F067 Pattern Strength LONG OOS `0.0`, trades `0`.
4. Result: F067 Pattern Strength SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F067_PATTERNSTRENGTH_ALLOW`; ignored columns `[]`.
6. Gate result: LONG left `1415` signals after action gate but `0` eligible bars after min-move and `0` filled entries; SHORT left `0` signals after action gate.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_18_f067_audit_20260623T225700Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.17 F066
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.17`.
2. Status: no runtime blocker.
3. Result: F066 OBV Bearish Divergence LONG OOS `0.0`, trades `0`.
4. Result: F066 OBV Bearish Divergence SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F066_OBVBEARDIV_ALLOW`; ignored columns `[]`.
6. Gate result: LONG and SHORT both left `0` signals after action gate and `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_17_f066_audit_20260623T224200Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.16 F065
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.16`.
2. Status: no runtime blocker.
3. Result: F065 OBV Bullish Divergence LONG OOS `0.0`, trades `0`.
4. Result: F065 OBV Bullish Divergence SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F065_OBVBULLDIV_ALLOW`; ignored columns `[]`.
6. Gate result: LONG left `4` signals and SHORT left `11` after action gate; min-move then left `0` eligible bars and `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_16_f065_audit_20260623T223100Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.15 F064
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.15`.
2. Status: no runtime blocker.
3. Result: F064 MACD Bearish Divergence LONG OOS `0.0`, trades `0`.
4. Result: F064 MACD Bearish Divergence SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F064_MACDBEARDIV_ALLOW`; ignored columns `[]`.
6. Gate result: LONG and SHORT both left `0` signals after action gate and `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_15_f064_audit_20260623T222100Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.14 F063
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.14`.
2. Status: no runtime blocker.
3. Result: F063 MACD Bullish Divergence LONG OOS `0.0`, trades `0`.
4. Result: F063 MACD Bullish Divergence SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F063_MACDBULLDIV_ALLOW`; ignored columns `[]`.
6. Gate result: LONG and SHORT both left `0` signals after action gate and `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_14_f063_audit_20260623T221200Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.13 F062
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.13`.
2. Status: no runtime blocker.
3. Result: F062 RSI Bearish Divergence LONG OOS `0.0`, trades `0`.
4. Result: F062 RSI Bearish Divergence SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F062_RSIBEARDIV_ALLOW`; ignored columns `[]`.
6. Gate result: LONG and SHORT both left `0` signals after action gate and `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_13_f062_audit_20260623T220200Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.12 F061
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.12`.
2. Status: no runtime blocker.
3. Result: F061 RSI Bullish Divergence LONG OOS `0.0`, trades `0`.
4. Result: F061 RSI Bullish Divergence SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F061_RSIBULLDIV_ALLOW`; ignored columns `[]`.
6. Gate result: LONG left `0` signals after action gate; SHORT left `4` signals after action gate but `0` eligible bars after min-move and `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_12_f061_audit_20260623T215100Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.11 F060
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.11`.
2. Status: no runtime blocker.
3. Result: F060 Bearish Engulfing LONG OOS `0.0`, trades `0`.
4. Result: F060 Bearish Engulfing SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F060_ENGULFBEAR_ALLOW`; ignored columns `[]`.
6. Gate result: LONG left `0` signals after action gate; SHORT left `1` signal after action gate but `0` eligible bars after min-move and `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_11_f060_audit_20260623T213900Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.10 F059
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.10`.
2. Status: no runtime blocker.
3. Result: F059 Bullish Engulfing LONG OOS `0.0`, trades `0`.
4. Result: F059 Bullish Engulfing SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F059_ENGULFBULL_ALLOW`; ignored columns `[]`.
6. Gate result: LONG and SHORT both left `0` signals after action gate and `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_10_f059_audit_20260623T213000Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.9 F058
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.9`.
2. Status: no runtime blocker.
3. Result: F058 Shooting Star LONG OOS `0.0`, trades `0`.
4. Result: F058 Shooting Star SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F058_SHOOTINGSTAR_ALLOW`; ignored columns `[]`.
6. Gate result: LONG left `0` signals after action gate; SHORT left `1` signal after action gate but `0` eligible bars after min-move and `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_9_f058_audit_20260623T211900Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.8 F057
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.8`.
2. Status: no runtime blocker.
3. Result: F057 Hammer LONG OOS `0.0`, trades `0`.
4. Result: F057 Hammer SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F057_HAMMER_ALLOW`; ignored columns `[]`.
6. Gate result: LONG left `0` signals after action gate; SHORT left `8` signals but `0` filled entries.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_8_f057_audit_20260623T205000Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.7 F056
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.7`.
2. Status: no runtime blocker.
3. Result: F056 Bearish Pin Bar LONG OOS `0.0`, trades `0`.
4. Result: F056 Bearish Pin Bar SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F056_PINBEAR_ALLOW`; ignored columns `[]`.
6. Gate result: LONG and SHORT both left `0` signals after action gate.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_7_f056_audit_20260623T203800Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.6 F055
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.6`.
2. Status: no runtime blocker.
3. Result: F055 Bullish Pin Bar LONG OOS `0.0`, trades `0`.
4. Result: F055 Bullish Pin Bar SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F055_PINBULL_ALLOW`; ignored columns `[]`.
6. Gate result: LONG left `1` signal after action gate but `0` filled entries; SHORT left `0` signals.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_6_f055_audit_20260623T202700Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.5 F054
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.5`.
2. Status: no runtime blocker.
3. Result: F054 Inside Bar LONG OOS `0.0`, trades `0`.
4. Result: F054 Inside Bar SHORT OOS `0.0`, trades `0`.
5. Isolation: active gate only `F054_INSIDEBAR_ALLOW`; ignored columns `[]`.
6. Gate result: raw signals existed, but `signal_count_after_entry_action_gates=0` on both sides.
7. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_5_f054_audit_20260623T201700Z.md`.

## Fixed Process-Pool Temporary Unlock Race In Stage 8.2.4 F053
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.4`.
2. Issue: concurrent LONG and SHORT process-pool runs with `-UseTemporaryUnlock` could overwrite the shared unlock marker and back up already-unlocked readiness.
3. Impact: after the parallel F053 run, `configs/readiness.yaml` was left at `project_ready=true`.
4. Fix: restored readiness from `reports/logs/readiness_backup_pool_20260623T195401Z_long_only_dda35a46.yaml`.
5. Fix: saved bad state to `reports/logs/readiness_bad_after_parallel_stage_8_2_4_f053_20260623T195900Z.yaml`.
6. Fix: added live-marker guard in `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`.
7. Validation: simulated active marker exits before workers with `EXIT_CODE=1`; readiness remains frozen.
8. Rule: run `-UseTemporaryUnlock` process-pool jobs sequentially.
9. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.4 F053
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.4`.
2. Status: runtime OK after readiness-race fix.
3. Result: F053 Doji LONG OOS `0.0`, trades `0`.
4. Result: F053 Doji SHORT OOS `0.0`, trades `0`.
5. Decision: `NO_GO_FOR_ML`; do not build package, approve, or ingest into ML.
6. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.

## F052 Positive Candidate Failed Adjacent Validation
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.3`.
2. Status: no runtime blocker after command quoting was corrected.
3. Context: Stage `8.2.2` F052 LONG was positive on one OOS trade, but needed validation.
4. Validation window: train `2026-05-04..2026-05-17`, OOS `2026-05-18..2026-05-24`, data layer `core`.
5. Result: OOS `-5.696708101293968`, trades `1`, goal pass `false`, train gate `false`.
6. Exit reason: `timeout`.
7. Decision: `VALIDATION_FAIL_NO_ML_GO`; do not build package, approve, or ingest into ML.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_3_f052_fixed_validation_audit_20260623T194700Z.md`.
9. Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T195125Z.json`.

## Command Issues During F052 Validation Were Not Strategy Failures
1. When: 2026-06-23 Stage `8.2.3`.
2. First issue: local PowerShell did not have `ConvertFrom-Yaml`.
3. Second issue: PowerShell stripped JSON quotes in `--calibration-params-json`.
4. Fix: used controlled readiness backup/restore and escaped JSON quotes.
5. Final validation run completed and readiness freeze was restored.
6. These issues do not change the strategy decision: F052 failed validation on the final valid run.

## Positive But Not ML GO In Stage 8.2.2 F052
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.2`.
2. Status: no runtime blocker.
3. Result: F052 CHOCH LONG returned `goal_pass`, OOS trades `1`, OOS return `+5.3486475132039635`.
4. Caveat: train gate failed, trade count is only `1`, and the only OOS trade exited by timeout.
5. SHORT result: `goal_fail`, OOS trades `0`, OOS return `0.0`.
6. Data layer: final search/train/OOS all used `core`.
7. Decision: positive test candidate only; no automatic ML package or ML training.
8. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_2_f052_audit_20260623T193700Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2.1 F050
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2.1`.
2. Status: no runtime blocker.
3. Result: F050 BOSUP `long_only` final valid run returned `goal_fail`, OOS trades `0`, OOS return `0.0`.
4. Data layer: final search/train/OOS all used `core`.
5. Decision: `NO_GO_FOR_ML`; do not build package or train ML from this run.
6. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_1_f050_audit_20260623T192700Z.md`.

## Fixed In ML Optuna Calibration Stage 8.2
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2`.
2. Initial issue: process-pool launcher did not pass the Stage 8 clean `core` data layer into adaptive/search/train/OOS, so the first run was invalidated for decision use.
3. Fix: added `-DataLayer raw|core` to `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`.
4. Fix: added `--layer` propagation in `src/mlbotnav/adaptive_auto_train.py`.
5. Fix: added `--layer` to `src/mlbotnav/search_gate_candidate.py` and `src/mlbotnav/optuna_search_candidate.py`.
6. Second issue: OOS CSV had `data_layer=core`, but `oos_report.json` lacked top-level `data_layer` and window fields.
7. Fix: `src/mlbotnav/oos_evaluate.py` now writes `data_layer`, `date_range`, `train_start`, `train_end`, `test_start`, and `test_end`.
8. Result: final valid run uses `core` in search/train/OOS and passes OOS CSV contract.
9. Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_audit_20260623T191900Z.md`.

## No Trade Candidate In ML Optuna Calibration Stage 8.2
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.2`.
2. Status: no runtime blocker after fixes.
3. Result: F051 BOSDOWN `short_only` final valid run returned `goal_fail`, OOS trades `0`, OOS return `0.0`.
4. Decision: `NO_GO_FOR_ML`; do not build package or train ML from this run.

## No Error In ML Large Clean Window Stage 8.1
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `8.1`.
2. Status: large clean window fixed with no code/test blocker.
3. Manifest: `configs/ml_large_clean_window_manifest.yaml`.
4. Window: `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.
5. Audit: `PASS`, missing files `0`, errors `0`.
6. New tests: `4/4 OK`.
7. Focused smoke/ingest tests: `22/22 OK`.
8. Artifact: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.
9. Boundary: Optuna calibration not started, package not created, ML ingest not started, ML training not started.

## No Error In ML Smoke Bridge Stage 7 Closeout
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `7.6`.
2. Status: Stage 7 closed with no code/test blocker.
3. Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.
4. Rows total: `1177`.
5. Final checks: smoke window `PASS`, approved registry `PASS`, ML ingest builder `PASS`, dataset contract `PASS`.
6. Focused Stage 7 tests: `67/67 OK`.
7. Artifact: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.
8. Boundary: ML training not started, no direct Optuna report scan, no unapproved package ingested.

## No Error In ML Ingest Stage 7.5
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `7.5`.
2. Status: ML ingest dataset assembly closed with no code/test blocker.
3. Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.
4. Dataset manifest: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`.
5. Rows total: `1177`.
6. Builder report: `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T184833777713Z.json`.
7. Dataset contract: `PASS`.
8. Registry validator/reader/admission status: `PASS`.
9. Focused ingest tests: `24/24 OK`.
10. Artifact: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.
11. Boundary: no direct Optuna report scan; no unapproved package ingested; ML training not started.

## No Error In ML Approved Registry Stage 7.4
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `7.4`.
2. Status: package manually approved with no code/test blocker.
3. Registry: `configs/ml_approved_calibration_packages.yaml`.
4. Approved count: `1`.
5. Approved package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.
6. Admission consistency: registry, manifest, calibration package, and package audit all agree on ML approval.
7. Registry validator: `PASS`.
8. Admission status: `PASS`.
9. Registry reader: `PASS`.
10. Package contract/alignment audits: `PASS`.
11. Focused tests: `42/42 OK`.
12. Artifact: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.
13. Boundary: dataset builder / ML ingest was not run; ML training not started.

## No Error In ML Smoke Package Contract Stage 7.3
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `7.3`.
2. Status: package contract audit closed with no package fix required.
3. Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.
4. Package status: `DRAFT`.
5. Package ML decision: `NO_GO_FOR_ML`.
6. Contract audit: `PASS`, rows `1177`, failed rows `0`, missing columns `0`.
7. Direct contract API validation: `PASS` in `approved_mode=False` and `approved_mode=True`.
8. Package alignment audits: run_id/passport/calibration params/data windows all `PASS`.
9. Registry boundary: approved count remains `0`.
10. Focused tests: `48/48 OK`.
11. Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T183955Z.json`.
12. Artifact: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.
13. Boundary: no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

## Fixed In ML Smoke Package Stage 7.2
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `7.2`.
2. Initial issue: copied package-local `source_reports/oos_report.json` lacked `data_layer` and `date_range`.
3. Fix: added `data_layer=core`, `date_range.start=2026-05-25`, `date_range.end=2026-05-26`, `test_day=2026-05-27`, `test_end_day=2026-05-27` to the smoke package copy only.
4. Source Stage 3 package was not changed.
5. Result: data windows alignment rerun returned `PASS`.
6. Artifact: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.
7. Boundary: no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

## No Error In ML Smoke Package Stage 7.2
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `7.2`.
2. Status: package created and audited after the data-window fix.
3. Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.
4. Package status: `DRAFT`.
5. Package ML decision: `NO_GO_FOR_ML`.
6. Contract audit: `PASS`, rows `1177`.
7. Alignment audits: run_id/passport/calibration params/data windows all `PASS`.
8. Focused tests: `42/42 OK`.
9. Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T182902Z.json`.

## No Error In ML Smoke Window Stage 7.1
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `7.1`.
2. Status: no code/test blocker.
3. Result: smoke window manifest created at `configs/ml_smoke_run_manifest.yaml`.
4. Result: smoke auditor created at `src/mlbotnav/ml_smoke_window_manifest_audit.py`.
5. Selected window: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`.
6. New tests: `5/5 OK`.
7. Focused ML smoke/alignment tests: `78/78 OK`.
8. Real smoke audit: `PASS`, report `reports/qa_gate/ml_smoke_window_manifest_audit_20260623T182159845644Z.json`.
9. Artifact: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.
10. Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T182218Z.json`.
11. Boundary: no package created, no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

## No Error In ML Alignment Stage 6 Closeout
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `6.6`.
2. Status: Stage 6 closed with no code/test blocker.
3. Result: `6.1-6.6` closed.
4. Focused tests: `121/121 OK`.
5. Alignment audits: all five returned `PASS / NO_APPROVED_PACKAGES`.
6. Registry validator/reader: `PASS`.
7. Dataset builder: `PASS / NO_APPROVED_PACKAGES`.
8. Reject-log builder: `PASS / NO_REJECTIONS`.
9. Artifact: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.
10. Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181511Z.json`.
11. Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

## No Error In ML Alignment Admission Status Stage 6.5
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `6.5`.
2. Status: no code/test blocker.
3. Result: admission status auditor created at `src/mlbotnav/ml_alignment_admission_status_audit.py`.
4. Result: package audit fails unless registry, manifest, calibration package, and audit.md all approve ML admission.
5. New tests: `6/6 OK`.
6. Focused tests: `121/121 OK`.
7. Real registry result: `PASS / NO_APPROVED_PACKAGES`.
8. Artifact: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.
9. Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181123Z.json`.
10. Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

## No Error In ML Alignment Data Windows Stage 6.4
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `6.4`.
2. Status: no code/test blocker.
3. Result: data windows alignment auditor created at `src/mlbotnav/ml_alignment_data_windows_audit.py`.
4. Result: package audit fails when `manifest.json`, `trade_log.csv`, and package-local OOS report diverge on data window context.
5. New tests: `8/8 OK`.
6. Focused tests: `115/115 OK`.
7. Real registry result: `PASS / NO_APPROVED_PACKAGES`.
8. Artifact: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.
9. Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154759Z.json`.
10. Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

## No Error In ML Alignment Calibration Params Stage 6.3
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `6.3`.
2. Status: no code/test blocker.
3. Result: calibration params alignment auditor created at `src/mlbotnav/ml_alignment_calibration_params_audit.py`.
4. Result: package audit fails when `calibration_package.json`, `trade_log.csv`, and package-local OOS report calibration params diverge.
5. New tests: `7/7 OK`.
6. Focused tests: `107/107 OK`.
7. Real registry result: `PASS / NO_APPROVED_PACKAGES`.
8. Artifact: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.
9. Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154240Z.json`.
10. Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

## No Error In ML Alignment Passport Context Stage 6.2
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `6.2`.
2. Status: no code/test blocker.
3. Result: passport context alignment auditor created at `src/mlbotnav/ml_alignment_passport_context_audit.py`.
4. Result: package audit fails when `manifest.json`, `calibration_package.json`, and `trade_log.csv` diverge on `block_id`, `passport_id`, or `action_id`.
5. New tests: `6/6 OK`.
6. Focused tests: `100/100 OK`.
7. Real registry result: `PASS / NO_APPROVED_PACKAGES`.
8. Artifact: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.
9. Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153741Z.json`.
10. Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

## No Error In ML Alignment Run ID Stage 6.1
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `6.1`.
2. Status: no code/test blocker.
3. Result: run_id alignment auditor created at `src/mlbotnav/ml_alignment_run_id_audit.py`.
4. Result: package audit fails when `manifest.json`, `calibration_package.json`, and `trade_log.csv` run IDs diverge.
5. New tests: `5/5 OK`.
6. Focused tests: `94/94 OK`.
7. Real registry result: `PASS / NO_APPROVED_PACKAGES`.
8. Artifact: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.
9. Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153207Z.json`.
10. Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

## No Error In ML Stage 5 Closeout
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `5.6`.
2. Status: Stage 5 closed with no code/test blocker.
3. Result: `5.1-5.6` closed.
4. Focused tests: `89/89 OK`.
5. Artifact: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.
6. Final text_guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.
7. Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

## No Error In ML Rejection Reasons Stage 5.5
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `5.5`.
2. Status: no code/test blocker.
3. Result: rejection reason log builder created at `src/mlbotnav/ml_rejection_reason_log.py`.
4. Result: real reject-log run returns `PASS / NO_REJECTIONS`.
5. Focused tests: `89/89 OK`.
6. Artifact: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.
7. Final checks: registry validator `PASS`; reject-log smoke `PASS / NO_REJECTIONS` at `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.
8. Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

## No Error In ML Trade Dataset Assembly Stage 5.4
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `5.4`.
2. Status: no code/test blocker.
3. Result: dataset builder created at `src/mlbotnav/ml_approved_trade_dataset_builder.py`.
4. Result: real builder run returns `PASS / NO_APPROVED_PACKAGES`.
5. Focused tests: `85/85 OK`.
6. Artifact: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.
7. Final checks: registry validator `PASS`; builder smoke `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.
8. Boundary: no package is `APPROVED_FOR_ML`; no dataset was created from unapproved data; ML training not started.

## No Error In ML Approved Package Registry Reader Stage 5.3
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `5.3`.
2. Status: no code/test blocker.
3. Result: registry reader created at `src/mlbotnav/ml_approved_package_registry_reader.py`.
4. Result: real registry read returns `PASS` with approved count `0`.
5. Focused tests: `82/82 OK`.
6. Artifact: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.
7. Final checks: registry validator `PASS`, `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.
8. Boundary: no package is `APPROVED_FOR_ML`; ML dataset assembly and training not started.

## No Error In ML Ingest Source Policy Stage 5.2
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `5.2`.
2. Status: no code/test blocker.
3. Result: source-policy guard created at `src/mlbotnav/ml_ingest_source_policy.py`.
4. Result: direct roots `reports/optuna`, `reports/pipeline`, and `reports/final_review` are denied for ML ingest source policy.
5. Focused tests: `79/79 OK`.
6. Artifact: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.
7. Boundary: no package is `APPROVED_FOR_ML`; ML ingest/training not started.

## No Error In ML Ingest Entry Point Stage 5.1
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `5.1`.
2. Status: no code/test blocker; discovery step closed.
3. Result: current primary ML training ingest entry point found: `src/mlbotnav/pipeline_train_eval.py`.
4. Gap: training does not read `configs/ml_approved_calibration_packages.yaml`.
5. Gap: training does not assemble dataset from `reports/ml_candidates/<run_id>/trade_log.csv`.
6. Artifact: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.
7. Boundary: no package is `APPROVED_FOR_ML`; ML ingest/training not started.

## No Error In ML Approval Registry Stage 4 Closeout
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `4.5`.
2. Status: Stage 4 closed with no code/test blocker.
3. Result: manual approval registry, bans, and validator are in place.
4. Registry state: `approved_packages: []`, approved count `0`.
5. Validator report: `reports/qa_gate/ml_approval_registry_validator_20260623T143952Z.json`.
6. Artifact: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.
7. Boundary: no package is `APPROVED_FOR_ML`; ML ingest not started.

## No Error In ML Approval Registry Stage 4.4 Validator
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `4.4`.
2. Status: no code/test blocker.
3. Result: registry validator created and real registry validation returns `PASS`.
4. Validator report: `reports/qa_gate/ml_approval_registry_validator_20260623T143427Z.json`.
5. Artifact: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.
6. Boundary: approved count remains `0`.

## No Error In ML Approval Registry Stage 4.3 Bans
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `4.3`.
2. Status: no blocker.
3. Result: registry bans recorded in `configs/ml_approved_calibration_packages.yaml`.
4. Current registry state: `approved_packages: []`.
5. Artifact: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.
6. Boundary: validator CLI/module starts at `4.4`.

## No Error In ML Approval Registry Stage 4.2 Format
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `4.2`.
2. Status: no blocker.
3. Result: registry format documented in `configs/ml_approved_calibration_packages.yaml`.
4. Current registry state: `approved_packages: []`.
5. Artifact: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.
6. Boundary: validator bans are next at `4.3`.

## No Error In ML Approval Registry Stage 4.1 File
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `4.1`.
2. Status: no blocker.
3. Result: `configs/ml_approved_calibration_packages.yaml` created.
4. Current registry state: `approved_packages: []`.
5. Artifact: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.
6. Boundary: no package approved for ML.

## No Error In ML Candidate Package Stage 3 Closeout
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `3.7`.
2. Status: Stage 3 closed with no code/test blocker.
3. Result: candidate package required files, manifest, trade log contract, and text guard all pass.
4. Package: `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`.
5. Artifact: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.
6. Boundary: package remains `DRAFT`; approval registry starts at `4.1`.

## No Error In ML Candidate Package Stage 3.6 Package Audit
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `3.6`.
2. Status: no code/test blocker.
3. Result: package-local `audit.md` created and validated.
4. File: `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/audit.md`.
5. Artifact: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.
6. Boundary: package remains `DRAFT`; ML approval remains a later manual stage.

## No Error In ML Candidate Package Stage 3.5 Manifest
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `3.5`.
2. Status: no code/test blocker.
3. Result: package-local `manifest.json` created and validated.
4. File: `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/manifest.json`.
5. Artifact: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.
6. Boundary: package-level `audit.md` and ML approval remain later steps.

## No Error In ML Candidate Package Stage 3.4 Source Reports
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `3.4`.
2. Status: no code/test blocker.
3. Result: package-local source reports copied and indexed.
4. File: `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports.json`.
5. Optional `optuna_report.json` is `NOT_PROVIDED` for this candidate.
6. Artifact: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.
7. Boundary: manifest, package audit, and ML approval remain later steps.

## No Error In ML Candidate Package Stage 3.3 Trade Log
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `3.3`.
2. Status: no code/test blocker.
3. Result: package-local `trade_log.csv` created and validated.
4. Contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T134753Z.json`.
5. Artifact: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.
6. Boundary: source reports, manifest, audit, and ML approval remain later steps.

## No Error In ML Candidate Package Stage 3.2 Calibration Package
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `3.2`.
2. Status: no code/test blocker.
3. Result: `calibration_package.json` created and parsed.
4. File: `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/calibration_package.json`.
5. Status remains `DRAFT`; no ML approval was granted.
6. Artifact: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.

## No Error In ML Candidate Package Stage 3.1 Structure
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `3.1`.
2. Status: no code/test blocker.
3. Result: package directory structure created under `reports/ml_candidates/<run_id>/`.
4. Builder: `src/mlbotnav/ml_candidate_package_builder.py`.
5. Tests: `tests/test_ml_candidate_package_builder.py`.
6. Artifact: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.

## No Error In ML Trade Dataset Stage 2 Closeout
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `2.9`.
2. Status: Stage 2 closed with no remaining code/test blocker.
3. Pipeline contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133238Z.json`.
4. OOS contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133240Z.json`.
5. Closeout artifact: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.
6. Boundary: no automatic ML approval; Stage 3 package builder remains next.

## No Error In ML Trade Dataset Stage 2.8 OOS CSV
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `2.8`.
2. Status: no code/test blocker.
3. Result: fresh OOS CSV passed `ml_trade_dataset_contract`.
4. CSV: `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.csv`.
5. Contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T132804Z.json`.
6. Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.

## ML Trade Dataset Stage 2.7 Pipeline CSV Closed After Controlled Unlock
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `2.7`.
2. Status: code fix applied and runtime validation completed through controlled temporary unlock.
3. Fix: `pipeline_train_eval.py` now accepts `--layer`, reads that layer, and writes it to trade CSV run context instead of hardcoding `raw`.
4. Earlier blocker: `pipeline_train_eval` was blocked by readiness gate `project_not_ready_for_pipeline_train_eval`.
5. Closeout: fresh CSV `reports/pipeline/backtest_trades_SOLUSDT_1m_20260623T132424Z.csv` passed contract validation; readiness was restored to frozen state after the run.
6. Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.

## No Error In ML Trade Dataset Stage 2.6 MAE/MFE
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `2.6`.
2. Status: no code/test blocker.
3. Result boundary: MAE/MFE labels are added to trade CSV write paths, but the CSV is not fully ML-ready until pipeline/OOS contract checks and alignment audit are closed.
4. Validation: changed modules `py_compile PASS`; focused tests `59/59 OK`; `text_guard PASS`.
5. Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.

## No Error In ML Trade Dataset Stage 2.5 Hit Labels
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `2.5`.
2. Status: no code/test blocker.
3. Result boundary: hit labels are added to trade CSV write paths, but the CSV is not fully ML-ready until MAE/MFE and alignment audit are added.
4. Validation: changed modules `py_compile PASS`; focused tests `58/58 OK`; `text_guard PASS`.
5. Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.

## No Error In ML Trade Dataset Stage 2.4 Duration Labels
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `2.4`.
2. Status: code/test blocker found and fixed.
3. Fix: duration columns are created/cast as `object` before mixed blank/numeric writes.
4. Result boundary: duration labels are added to trade CSV write paths, but the CSV is not fully ML-ready until hit labels and MAE/MFE are added.
5. Validation: changed modules `py_compile PASS`; focused tests `57/57 OK`; `text_guard PASS`.
6. Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_4_duration_labels_audit_20260623T125816Z.md`.

## No Error In ML Trade Dataset Stage 2.1 Run Context
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `2.1`.
2. Status: no code/test blocker.
3. Result boundary: run-level context is added to trade CSV write paths, but the CSV is not fully ML-ready until later Stage 2 fields are added.
4. Validation: focused tests passed; initial `py_compile` hit a Windows `__pycache__` lock, then passed with isolated `PYTHONPYCACHEPREFIX=reports/qa_gate/pycache_step_2_1`.
5. Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.

## No Error In ML Trade Dataset Contract Stage 1 Closeout
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `1.7`.
2. Status: no closeout blocker.
3. Result boundary: Stage 1 contract/validator is closed; real CSV enrichment remains Stage 2 work.
4. Artifact: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.
5. Next strict step: `2.1 Добавить run-level context`.

## No Error In ML Trade Dataset Contract Validator Step 1.6
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `1.6`.
2. Status: no infrastructure or validator failure.
3. Result boundary: validator module, focused tests, and CLI smoke all passed.
4. Artifact: `reports/qa_gate/ml_trade_dataset_contract_step_1_6_audit_20260623T122406Z.md`.
5. Remaining work: step `1.7` stage-1 closeout, then implementation of actual row-level CSV emission/alignment in later WBS steps.

## ML Dataset Contract Gaps Before Big Window
1. When: 2026-06-23 Optuna/ML/entry/exit alignment audit.
2. Status: not an infrastructure error; this is a data-contract gap.
3. Finding: `calibration_params` propagate correctly through JSON reports and current F051 gate isolation works, but CSV trade/OOF outputs do not carry row-level `action_id`, `passport_id`, `block_id`, or `calibration_params_json`.
4. Missing for ML trade labels: `trade_id`, `bars_in_trade`, `tp_hit`, `sl_hit`, `timeout_hit`, `mae_pct`, `mfe_pct`.
5. Candle boundary: `data/core/bybit_ohlcv` ends at `2026-05-31`; `2026-06-01` is only raw/quarantine and incomplete to `15:03 UTC`.
6. Artifact: `reports/qa_gate/optuna_ml_entry_exit_alignment_audit_20260623T162411Z.md`.

## Core ML Bot TZ Partial Architecture Match
1. When: 2026-06-23 project audit against user-provided compact 1m ML trading bot TZ.
2. Status: not an infrastructure error; this is an architecture/coverage gap.
3. Finding: the project has a strong `src/mlbotnav` calibration/ML/backtest core, but it does not match the TZ module layout as separate `feature_engine`, `indicator_engine`, `entry_engine`, `exit_engine`, `risk_engine`, `ml_dataset`, and `backtest_engine` packages.
4. Missing/partial: CORE feature contract, Bollinger/Keltner/session features, entry/exit/risk decision contracts, MAE/MFE, trade outcome labels, full trade-log schema, and separate exit/risk passports.
5. Boundary: do not create a parallel root `trading_bot/` tree and do not reuse closed F001-F083 results as candidates.
6. Artifact: `reports/qa_gate/core_ml_bot_tz_audit_20260623_RU.md`.

## F001-F083 Audit Completeness Gaps
1. When: 2026-06-23 full passport-route audit.
2. Status: existing executable passport matrices are clean, but F001-F083 numeric coverage is incomplete.
3. Findings after F039 closure: planned-only gaps are closed; `F017/F018` combined-vs-split was accepted as one Stochastic K/D passport.
4. Artifact: `reports/qa_gate/f001_f083_passport_full_audit_20260623.md`.
5. Boundary: this is not a false production GO; the remaining hardening item is explicit active-action filtering against stale `F*_ALLOW` columns.

## F017/F018 Combined Stochastic Passport Accepted
1. When: 2026-06-23 F001-F083 completeness follow-up.
2. Status: closed by design decision.
3. Decision: keep `F017_F018` as one combined Stochastic K/D passport with runtime gate `F017_F018_STOCH14_ALLOW`.
4. Reason: `%K` and `%D` are two lines of the same Stochastic indicator, and `KD_CROSS` requires both lines in one signal grammar.
5. Artifact: `reports/qa_gate/f017_f018_combined_decision_audit_20260623T081000Z.md`.

## F024 VWAP Distance Passport Had No New Worker Error
1. When: 2026-06-23 F024 VWAP distance long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: both runs completed technically `OK`; action gates were isolated to `F024_VWAPDIST_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG was negative; SHORT had zero OOS trades.
5. Exit boundary: TP/SL/timeout were not calibrated inside F024; baseline timeout remained enabled.

## F026 Density Bin Share 60 Passport Had No New Worker Error
1. When: 2026-06-23 F026 bin-share 60 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: both runs completed technically `OK`; action gates were isolated to `F026_BINSHARE60_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG and SHORT were both negative.
5. Exit boundary: TP/SL/timeout were not calibrated inside F026; baseline timeout remained enabled.

## F027 Density Cluster Share 60 Passport Had No New Worker Error
1. When: 2026-06-23 F027 cluster-share 60 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: both runs completed technically `OK`; action gates were isolated to `F027_CLUSTERSHARE60_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG and SHORT were both negative.
5. Exit boundary: TP/SL/timeout were not calibrated inside F027; baseline timeout remained enabled.

## F028 Density VPOC Share 60 Passport Had No New Worker Error
1. When: 2026-06-23 F028 VPOC-share 60 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: both runs completed technically `OK`; action gates were isolated to `F028_VPOCSHARE60_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG and SHORT were both negative.
5. Exit boundary: TP/SL/timeout were not calibrated inside F028; baseline timeout remained enabled.

## F039 Trend Channel Position Passport Had No New Worker Error
1. When: 2026-06-23 F039 trend channel position long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: both runs completed technically `OK`; action gates were isolated to `F039_CHANNELPOS_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG `-17.392676%/3`, SHORT `0.000000%/0`.
5. Exit boundary: F039 LONG exited by `2 timeout` and `1 sl`; SHORT had zero OOS trades. TP/SL/timeout were not calibrated inside F039.

## Passport Backtest Stale Action Column Risk
1. When: 2026-06-23 runtime/backtest audit.
2. Status: fixed for passport route.
3. Fix: `run_prob_backtest` supports explicit `active_entry_action_columns`, Optuna passport search passes the current action id, and backtest infers active action columns from `Fxxx_*` calibration params when no explicit allowlist is passed.
4. Validation: stale-column regression test proves unrelated old action columns are ignored for an active F039 passport; project venv `tests.test_backtest_fields tests.test_optuna_search_runtime` returned `110/110 OK`.
5. Artifact: `reports/qa_gate/stale_action_column_hardening_20260623T082000Z.md`.

## No Runtime Error In B025 PATTERN_TRADE_CONTEXT
1. When: 2026-06-22 B025 `PATTERN_TRADE_CONTEXT` F082-F083 passport run.
2. Status: F082 and F083 LONG/SHORT all completed with launcher `OK`; strategy status was `goal_fail`, not infrastructure failure.
3. Result: F082 LONG `0%/0`, F082 SHORT `-25.094610%/7`, F083 LONG `-35.921536%/12`, F083 SHORT `-70.280106%/35`; final decision `NO_GO`.
4. Artifact: `reports/qa_gate/b025_pattern_trade_context_f082_f083_audit_20260622T211600Z.md`.
5. Note: focused dataset test emits pandas `PerformanceWarning` for fragmented DataFrame inserts; this is non-blocking and did not fail runtime/tests.

## No Error In Passport Registry Cleanup
1. When: 2026-06-22 passport-driven calibration route.
2. Status: registry cleanup only; no Optuna runtime, production action, unfreeze, delete, or destructive operation was launched.
3. Result: `configs/calibration_action_passports.yaml` validates as YAML and lists `B001-B006`; `B001` contains active solo passports `F001-F005`.
4. Boundary: this is a registry/organization step, not a profitable candidate decision.

## F006 Pool Artifact Collision Risk
1. When: 2026-06-22 F006 `hl_spread_1m` first `long_only` pool run with 3 process workers.
2. Symptom: launcher completed OK, but adaptive summary selected params did not match copied `final_review/top-card` calibration params for the same timestamped OOS artifact.
3. Boundary: strategy result is not promoted; the pool run is not used as the trusted F006 final.
4. Mitigation: reran F006 through a clean direct contour. Trusted result is `reports/qa_gate/f006_hl_spread_long_only_audit_20260622T131045Z.json`.
5. Follow-up: avoid using same-second global `final_review` artifact names as the sole source when multiple process workers finish simultaneously.

## F012 Parallel Release-Lock Warning
1. When: 2026-06-22 F012 `rsi14_1m` first attempt launched LONG and SHORT at the same time from this chat.
2. Symptom: LONG completed its trading calculation, but the wrapper exited with a release-lock warning because SHORT had already claimed/released the shared runtime owner.
3. Boundary: not a strategy result and not used for final F012 decision.
4. Mitigation: reran LONG sequentially; clean trusted result is `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-06-01_20260622T144550Z.json`.
5. Follow-up: run single-pass passport LONG/SHORT sequentially unless using the dedicated process-pool runner.

## Passport Registry Mojibake Encoding Repaired
1. When: 2026-06-22 after adding F012.
2. Symptom: `text_guard` flagged `configs/calibration_action_passports.yaml` after the file was saved as UTF-8 while old registry strings still contained mojibake text.
3. Fix: created a local backup next to the config, converted the registry text to normal UTF-8, and verified YAML parse.
4. Validation: `tests.test_optuna_space_constraints` passed and `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T145323Z.json`.

## Pattern Medium CPU Spike
1. When: 2026-06-04 `pattern long_only medium`.
2. Symptom: launcher/workers completed OK, but CPU monitor saw one sample at `97%`, above the user limit `85%`.
3. Artifact: `reports/qa_gate/pattern_long_only_medium_closeout_20260604T102010Z.json`.
4. Boundary: not a strategy/runtime crash; it is a machine-load limit issue.
5. Current action: pause before `pattern long_only wide` until CPU profile is confirmed or reduced.
6. Status update: user clarified that short spikes are acceptable; full pattern runtime continued and closed without sustained overload.

## Pattern Fallback Calibration Params Not Preserved
1. When: 2026-06-04 human-readable audit of `pattern` block06 runtime.
2. Symptom: search-level best candidates contain `calibration_params`, but final `best_oos` fallback selections record `selected_calibration_params={}`.
3. Artifact: `reports/qa_gate/pattern_block06_human_readable_20260604T103051Z_RU.md`.
4. Boundary: grids/runtime completed, but parameter-specific final replay is not trustworthy until fallback/no-pass candidate selection preserves params.
5. Fix: inspect and repair fallback candidate param propagation, then rerun/replay block06.

## Pattern Structure Volume Entry Gap Fixed
1. When: 2026-06-04 Optuma bridge current repair.
2. Symptom: `features_block.yaml` listed classic figure-pattern names, but runtime `dataset.py` mostly exposed candle patterns and divergences; the `pattern + structure_ta + volume_flow` entry bundle was TZ-only.
3. Fix: dataset now emits classic figure-pattern flags plus volume/level confirm and long/short entry flags; matrices include the new pattern profiles and rows; `vol_z` uses dedicated `vol_z_window`.
4. Validation: focused tests `97/97 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS`; `text_guard PASS`.
5. Remaining next step: dry command/compile gate for `catalog_block_06_pattern.yaml`, then runtime stacks.

## Runtime Param Formula Gaps Fixed
1. When: 2026-06-04 Optuma bridge Steps 2-5.
2. Symptom: several YAML-declared calibration params were present in matrices but not fully applied by runtime formulas.
3. Fix: `volume_flow` applies `return_lookback` for `vol_chg`, `delta_volume`, `obv_slope_5`; `density_profile` applies `div_lookback` for `density_vpoc_drift_20`; `structure_ta` applies `threshold_fine` for `retest_flag` and `false_breakout_flag`; FIBO now has `fib_window` and explicit `fib_level` values wired into matrices and dataset generation.
4. Validation: focused tests `95/95 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS` for 7 YAML matrices x 2 contours x 3 grid presets.
5. Remaining next issue: `pattern` / `pattern_structure_volume_entry` classic figure-pattern contour is the next current repair.

## Calibration Params Anchor Gap Fixed
1. When: 2026-06-04 Optuma bridge Step 1.
2. Symptom: Optuna search sampled `calibration_params`, but final `pipeline_train_eval` and `oos_evaluate` did not receive them.
3. Fix: `adaptive_auto_train.py` passes selected params as JSON to train; `pipeline_train_eval.py` applies/saves them; `oos_evaluate.py` loads/applies them in feature generation and final backtest.
4. Validation: changed-file `py_compile PASS`; focused tests `79/79 OK`.
5. Remaining next issue: `volume_flow` formulas still need repair for declared `return_lookback`.

## No Error In APTuna Block Alignment Audit
1. When: 2026-06-03 calibration block alignment check.
2. Status: read-only audit; no Optuna runtime, production action, unfreeze, delete, or destructive operation was launched.
3. Result: `PASS`, `issues=0`, `blockers=0`.
4. Artifact: `reports/qa_gate/aptuna_block_alignment_audit_20260603T164808Z.json`.
5. Boundary: only `H001` and `H002` feature_sweep matrices are generated so far; `H003` generation/compile is the next strict step, not an error.

## No Runtime Error In H002 Full Slot Closeout
1. When: 2026-06-03 sequential hypothesis/feature sweep, slot `H002`.
2. Status: matrix compile `PASS`; `long_only` and `short_only` both completed `narrow/medium/wide`; launcher `OK`, workers `3/3 exit_code=0`.
3. Result: best long `wide=-8.650246602184342%`, trades `4`; best short `narrow/medium=-0.2662724500743341%`, trades `2`; candidate `NO_CANDIDATE`.
4. Artifact: `reports/qa_gate/h002_slot_closeout_20260603T154133Z.json`.
5. Boundary: valid calibration/grid result, not an infrastructure failure.

## No Runtime Error In H001 Full Slot Closeout
1. When: 2026-06-03 sequential hypothesis/feature sweep, slot `H001`.
2. Status: `long_only` and `short_only` both completed `narrow/medium/wide`; launcher `OK`, workers `3/3 exit_code=0`.
3. Result: best long `medium=-8.650246602184342%`, trades `4`; best short `narrow=0%`, trades `0`; candidate `NO_CANDIDATE`.
4. Artifact: `reports/qa_gate/h001_slot_closeout_20260603T131659Z.json`.
5. Boundary: valid calibration/grid result, not an infrastructure failure.

## No Runtime Error In H001 Narrow Long Only
1. When: 2026-06-03 sequential hypothesis/feature sweep, slot `H001`.
2. Status: runtime launcher `OK`; workers `3/3 exit_code=0`.
3. Result: best OOS `-30.924389997582892%`, trades `13`, class `negative_runtime_ok`.
4. Artifact: `reports/qa_gate/h001_narrow_long_only_20260603T122520Z.json`.
5. Boundary: this is a valid negative calibration result, not an infra failure.

## No Runtime Error In H001 Feature Sweep Matrix Compile
1. When: 2026-06-03 under sequential hypothesis/feature sweep TZ.
2. Status: no runtime launched; only inventory, matrix generation, and compile check.
3. Inventory artifact: `reports/qa_gate/hypothesis_feature_sweep_inventory_20260603T121643Z.json`.
4. H001 matrix: `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`.
5. Compile report: `reports/qa_gate/h001_feature_sweep_matrix_compile_20260603T121833Z.json`.
6. Result: `PASS` for both `long_only` and `short_only`; next runtime is `H001 narrow long_only`.

## No Runtime Error In Current Pattern Closeout
1. When: 2026-06-03 under TZ `2026-06-03T10:25:00Z`.
2. Status: `pattern` completed `narrow/medium/wide` x `long_only/short_only`; every launcher returned `OK` and workers were `3/3 exit_code=0`.
3. Closeout artifact: `reports/qa_gate/calibration_node_pattern_closeout_20260603T112654Z.json`.
4. Best block result: `wide long_only`, OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production because `train_gate=false`.
5. Health after closeout: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T112958Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T112818Z.json`), `pip check PASS`.

## P2196E OOS Report Worker Crash
1. When: 2026-06-03 first `structure_ta wide short_only` runtime attempt at `2026-06-03T11:08:22Z`.
2. Symptom: launcher returned `PARTIAL_FAIL`; worker `w3` exited `-1` with `json.decoder.JSONDecodeError` while reading `parsed3["oos_report"]`.
3. Fix: `src/mlbotnav/adaptive_auto_train.py` now reads OOS reports through `_read_json_report_with_retry` and records `oos_report_read_failed` instead of crashing a worker.
4. Validation: focused tests `83/83 OK`; rerun at `2026-06-03T11:10:49Z` returned launcher `OK`, all 3 workers exit `0`.
5. Boundary: final `wide short_only` result is `NO_CANDIDATE` (`0%`, `0` trades), not infrastructure failure after the fix.

## Full Unittest Discover Residuals After P2196C
1. When: 2026-06-03 after strict filtering and command-set dry-run.
2. Artifact: `reports/qa_gate/p2196c_unittest_discover_residuals_20260603T100559Z.json`.
3. Status: focused strict readiness tests passed (`77/77 OK`), but full `python -m unittest discover -s tests` reported `5` failures and `2` errors.
4. Residuals are outside P2196B/P2196C strict filter scope: stale `_pick_candidate` test signature, model promotion gates blocked by current deployment/security policy, Optuna storage fallback expectation mismatch, and P24 temp PowerShell import path issue.
5. Boundary: do not treat full-discover as production release clean; for battle calibration readiness, strict focused tests and P2196C dry-run passed.

## No Runtime Error In P2196C Strict Command Set
1. When: 2026-06-03 P2196C.
2. Status: dry-run only; no Optuna runtime, production action, unfreeze, delete, or destructive operation was launched.
3. Artifact: `reports/optuna_catalog/index/p2196c_strict_command_set_20260603T100504Z.json`.
4. Result: 36/36 dry-run PASS.
5. Raw preflight: `reports/qa_gate/preflight_window_20260603T100432Z.json`, PASS.

## No Runtime Error In P2196B Volume/Volatility Context Wiring
1. When: 2026-06-03 P2196B substep.
2. Status: no ingest, Optuna runtime, production action, unfreeze, delete, or destructive operation was launched.
3. Artifact: `reports/qa_gate/p2196b_volume_context_wiring_audit_20260603T065821Z.json`.
4. Result: full matrix plus 6 catalog block matrices compile with `volume_flow` and `price_volatility` as always-on context blocks.
5. Tests: `python -m unittest tests.test_optuna_space_constraints tests.test_optuna_search_runtime` -> `69/69 OK`.
6. Post-sync checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T070000Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T065959Z.json`), `pip check PASS`.
7. Boundary: strict hypothesis/trend filtering is still pending before battle runtime.

## Structural Big-Window Runtime Stopped By User
1. When: 2026-06-02 structural big-window narrow runtime.
2. Status: user requested stop; active `run_optuna`/`adaptive_auto_train`/Optuna worker process tree was killed.
3. Artifact: `reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`.
4. Completed before stop: block01 `price_volatility` long/short and block02 `trend_momentum` long completed with launcher `OK`; block02 short was partial/stopped.
5. Safety fix: stale APTuna pool temporary unlock was restored from `reports/logs/readiness_backup_pool_20260602T192047Z_short_only_c7e04b1b.yaml`; marker removed; readiness is `project_ready=false`, `enforce_freeze=true`.
6. Checks after stop: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T192157Z.json`), readiness report `reports/readiness/readiness_check_20260602T192156Z.json`, `pip check PASS`.

## No Runtime Error In P2196A Battle Readiness Audit
1. When: 2026-06-03 P2196A.
2. Status: read-only audit/docs sync; no ingest, Optuna runtime, production action, unfreeze, delete, or destructive operation was launched.
3. Artifact: `reports/qa_gate/p2196a_optuna_battle_readiness_audit_20260603T060919Z.md`.
4. Finding: structural contour works, but strict block-hypothesis purity must be implemented or mixed semantics must be explicitly accepted before battle runtime.
5. Data note: raw/core forward files for 2026-06-02 and 2026-06-03 are absent in this workspace at audit time.

## No Runtime Error In Structural Big-Window Command Set
1. When: 2026-06-02 structural big-window command-set/dry-run.
2. Status: raw policy preflight `PASS`; compile/dry-run `36/36 PASS`; no runtime launched in command-set artifact.
3. Artifact: `reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json`.
4. Note: core observation failed for `2026-06-01` availability, but launcher policy uses raw layer for runtime preflight.

## No Runtime Error In Quick Structural Audit
1. When: 2026-06-02 quick structural audit after user correction.
2. Status: no ingest, Optuna runtime, production action, or unfreeze command was launched.
3. Note: audit corrected routing: UTC-close gate applies to P2079 forward/production only; structural catalog validation on closed historical data can proceed as a separate chain.
4. Artifact: `reports/qa_gate/quick_structural_audit_framework_20260602T182715Z.json`.

## No Runtime Error In P2195 F1 UTC-Close Recheck
1. When: 2026-06-02 P2195 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:45:02Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2194 F1 UTC-Close Recheck
1. When: 2026-06-02 P2194 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:41:09Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2193 F1 UTC-Close Recheck
1. When: 2026-06-02 P2193 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:38:39Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2192 F1 UTC-Close Recheck
1. When: 2026-06-02 P2192 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:36:04Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2191 F1 UTC-Close Recheck
1. When: 2026-06-02 P2191 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:33:25Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2190 F1 UTC-Close Recheck
1. When: 2026-06-02 P2190 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:30:21Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2189 F1 UTC-Close Recheck
1. When: 2026-06-02 P2189 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:25:48Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2188 F1 UTC-Close Recheck
1. When: 2026-06-02 P2188 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:22:57Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2187 F1 UTC-Close Recheck
1. When: 2026-06-02 P2187 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:19:09Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2186 F1 UTC-Close Recheck
1. When: 2026-06-02 P2186 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:15:30Z` was still before required close `2026-06-03T00:00:00Z`.

## Previous V3 Package B Pointer Was Skipped
1. When: 2026-06-02 P2137.
2. Symptom: current pointer had moved to P2079 forward handling while the previous V3 TZ still had an unclosed branch: define exact `Package B` slots after `Package A NO_CANDIDATE`.
3. Artifact: `reports/qa_gate/p2137_previous_tz_recovery_package_b_pointer_20260602T123736Z.json`.
4. Fix: restore manual pointer to V3 `Package B` slot definition; keep P2079 only as preserved `candidate_for_forward`.
5. Automation action: heartbeat `p2079-f1-data-gate-check` paused so forward path does not auto-advance before Package B is closed.
6. Timed chain fix: `P2139` added explicit date/time and TZ anchor. Current chain starts UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`.
7. P2140 inventory result: old Package B artifacts are historical V2/strict only; current V3 Package B exact slots are still not defined, so runtime remains blocked.

## Current V3 Package B Slots Not Defined Yet
1. When: 2026-06-02 P2140.
2. Status: `P2140` inventory `PASS`.
3. Artifact: `reports/qa_gate/p2140_v3_package_b_inventory_20260602T125900Z.json`.
4. Symptom: no current V3 Package B slot table, matrices, or command set exists yet.
5. Fix: next number `P2141` must define exact slots before any runtime; `P2142` must pass command-set/dry-run before Package B runtime.
6. Status update: fixed by `P2141`; exact slots are now defined, but matrices/command set are still missing until `P2142`.

## Current V3 Package B Command Set Not Defined Yet
1. When: 2026-06-02 P2141.
2. Status: exact slots `PASS`, but no matrix slices or command set exists yet.
3. Artifact: `reports/qa_gate/p2141_v3_package_b_exact_slots_20260602T130000Z.json`.
4. Fix: next number `P2142` must generate/select matrix slices and emit command set/dry-run artifact before any runtime.

## P2134 Forward Preflight Still Blocked By UTC Close/Data
1. When: 2026-06-02 P2134.
2. Status: repeated data gate remains blocked.
3. Current UTC at check: `2026-06-02T11:31:36Z`; day `2026-06-02` is not closed in UTC and `2026-06-03` is future.
4. Data snapshot: core max day `2026-05-31`; raw max day `2026-06-01`.
5. F1 report: `reports/qa_gate/preflight_window_20260602T113056Z.json`, `FAIL`.
6. F2 report: `reports/qa_gate/preflight_window_20260602T113105Z.json`, `FAIL`.
7. Checkpoint: `reports/qa_gate/p2134_p2079_forward_preflight_data_gate_20260602T113136Z.json`.
8. Fix: wait for closed raw `2026-06-02` before F1 preflight/runtime; wait for closed raw `2026-06-03` before F2 preflight/runtime.

## P2079 Forward Stability Blocked By Data
1. When: 2026-06-02 P2133.
2. Status: command set prepared, but runtime is blocked.
3. F1 window `2026-06-01 -> 2026-06-02`: preflight `FAIL`; raw test day `2026-06-02` absent, and `2026-06-01` train is partial for WF rows.
4. F2 window `2026-06-02 -> 2026-06-03`: preflight `FAIL`; raw train day `2026-06-02` and raw test day `2026-06-03` absent.
5. Artifacts:
   1. `reports/optuna_catalog/index/p2133_p2079_forward_stability_command_set_20260602T112708Z.json`
   2. `reports/qa_gate/preflight_window_20260602T112504Z.json`
   3. `reports/qa_gate/preflight_window_20260602T112532Z.json`
6. Fix: do not run F1/F2 runtime until closed raw days are available and preflight returns `PASS`.

## No Runtime Error In Full Block-Level Catalog Cycle
1. When: 2026-06-02 P2051-P2132.
2. Status: all 6 block-isolated cycles completed; runtime `36/36 OK`; post-sync closeout `PASS`.
3. Note: totals positive `1`, neutral `18`, negative `17`, infra_fail `0`; only accepted candidate is block03 `volume_flow` `P2079`. Production/unfreeze remains blocked until F1/F2 and new GO package.

## No Runtime Error In Block06 Pattern Full Cycle
1. When: 2026-06-02 P2117-P2129.
2. Status: narrow, medium, and wide runtime completed with launcher `status=OK` for long_only and short_only.
3. Note: block06 produced positive `0`, neutral `3`, negative `3`, infra_fail `0`; prior block03 candidate_for_forward remains preserved.

## No Runtime Error In Block05 Structure TA Full Cycle
1. When: 2026-06-02 P2104-P2116.
2. Status: narrow, medium, and wide runtime completed with launcher `status=OK` for long_only and short_only.
3. Note: block05 produced positive `0`, neutral `3`, negative `3`, infra_fail `0`; prior block03 candidate_for_forward remains preserved. Current pointer moved to block06 `pattern` narrow command set.

## No Runtime Error In P2144 Package B Short Only
1. When: 2026-06-02 P2144 Step 5.
2. Status: Package B `short_only` runtime completed with launcher `status=PASS` for all 9 external commands.
3. Note: catalog classification is `neutral`, accepted positive candidates `0`; best tradeful OOS was `-1.6689%`.
4. Artifacts:
   1. `reports/qa_gate/p2144_v3_package_b_short_only_summary_20260602T132020Z.json`
   2. `reports/optuna_catalog/neutral/p2144_v3_package_b_short_only_neutral_20260602T132420Z.json`

## No Runtime Error In P2143 Package B Long Only
1. When: 2026-06-02 P2143 Step 4.
2. Status: Package B `long_only` runtime completed with launcher `status=PASS` for all 9 external commands.
3. Note: catalog classification is `neutral`, accepted positive candidates `0`; best tradeful OOS was `-1.6687%`.
4. Artifacts:
   1. `reports/qa_gate/p2143_v3_package_b_long_only_summary_20260602T131035Z.json`
   2. `reports/optuna_catalog/neutral/p2143_v3_package_b_long_only_neutral_20260602T131535Z.json`

## No Runtime Error In P2142 Package B Command Set
1. When: 2026-06-02 P2142 Step 3.
2. Status: 4 matrix slices generated and 18 command dry-runs completed with `PASS`.
3. Note: no Optuna runtime was launched in P2142; next runtime is only `P2143 long_only`.
4. Artifact: `reports/qa_gate/p2142_v3_package_b_command_set_20260602T130559Z.json`.

## No Runtime Error In Block04 Density Profile Full Cycle
1. When: 2026-06-02 P2091-P2103.
2. Status: narrow, medium, and wide runtime completed with launcher `status=OK` for long_only and short_only.
3. Note: block04 produced positive `0`, neutral `4`, negative `2`, infra_fail `0`; prior block03 candidate_for_forward remains preserved. Current pointer moved to block05 `structure_ta` narrow command set.

## No Runtime Error In Block03 Volume Flow Full Cycle
1. When: 2026-06-02 P2078-P2090.
2. Status: narrow, medium, and wide runtime completed with launcher `status=OK` for long_only and short_only.
3. Note: block03 produced positive `1`, neutral `2`, negative `3`, infra_fail `0`; positive is candidate_for_forward only. Current pointer moved to block04 `density_profile` narrow command set.

## No Runtime Error In Block03 Volume Flow Narrow
1. When: 2026-06-02 P2078-P2081.
2. Status: narrow runtime completed with launcher `status=OK` for long_only and short_only.
3. Note: long_only produced a positive catalog candidate (`+1.9186%`, trades `1`); short_only was negative. Current pointer moved to block03 medium command set.

## No Runtime Error In Block02 Trend Momentum Full Cycle
1. When: 2026-06-02 P2065-P2077.
2. Status: narrow, medium, and wide runtime completed with launcher `status=OK` for long_only and short_only.
3. Note: block02 produced positive `0`, neutral `3`, negative `3`, infra_fail `0`; current pointer moved to block03 `volume_flow` narrow command set.

## No Runtime Error In Block02 Trend Momentum Narrow
1. When: 2026-06-02 P2065-P2068.
2. Status: narrow runtime completed with launcher `status=OK` for long_only and short_only.
3. Note: block02 narrow produced positive `0`, neutral `1`, negative `1`; current pointer moved to block02 medium command set.

## No Runtime Error In Block01 Price Volatility Cycle
1. When: 2026-06-02 P2053-P2064.
2. Status: narrow, medium, and wide runtime completed with launcher `status=OK` for long_only and short_only.
3. Note: block01 produced positive `0`, neutral `3`, negative `3`, infra_fail `0`; current pointer moved to block02.

## No Runtime Error In Step 8 Wide Runtime
1. When: 2026-06-02 P2045-P2047.
2. Status: long_only and short_only wide runtime completed with launcher `status=OK`; workers `3/3` exit_code `0` in both modes.
3. Note: both results were classified `negative`; accepted positive candidates remain `0`.

## No Runtime Error In Step 7 Medium Runtime
1. When: 2026-06-02 P2040-P2042.
2. Status: long_only and short_only medium runtime completed with launcher `status=OK`; workers `3/3` exit_code `0` in both modes.
3. Note: both results were classified `negative` because OOS was below zero and `goal_pass=false`; accepted positive candidates remain `0`.

## No Runtime Error In Step 7 Medium Command Set
1. When: 2026-06-02 P2039 Step 7 medium command set.
2. Status: command set `PASS`; only compile and dry-run launcher checks were executed.
3. Note: long_only and short_only dry-runs both propagated `--calibration-grid-preset medium`, `--force-profile-edge-coverage on`, `--search-workers 3`, `--max-threads 3`, and `--optuna-n-trials-override 40`.

## No Runtime Error In P2155 F1 UTC-Close Recheck
1. When: 2026-06-02 P2155 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T14:29:20Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2156 F1 UTC-Close Recheck
1. When: 2026-06-02 P2156 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T14:33:08Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2157 F1 UTC-Close Recheck
1. When: 2026-06-02 P2157 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T14:36:25Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2158 F1 UTC-Close Recheck
1. When: 2026-06-02 P2158 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T14:40:30Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2159 F1 UTC-Close Recheck
1. When: 2026-06-02 P2159 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T14:43:17Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2160 F1 UTC-Close Recheck
1. When: 2026-06-02 P2160 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T14:46:07Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2161 F1 UTC-Close Recheck
1. When: 2026-06-02 P2161 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T14:49:43Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2162 F1 UTC-Close Recheck
1. When: 2026-06-02 P2162 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T14:52:28Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2170 F1 UTC-Close Recheck
1. When: 2026-06-02 P2170 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:21:20Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2169 F1 UTC-Close Recheck
1. When: 2026-06-02 P2169 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:18:26Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2168 F1 UTC-Close Recheck
1. When: 2026-06-02 P2168 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:15:32Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2167 F1 UTC-Close Recheck
1. When: 2026-06-02 P2167 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:10:30Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2166 F1 UTC-Close Recheck
1. When: 2026-06-02 P2166 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:07:32Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2165 F1 UTC-Close Recheck
1. When: 2026-06-02 P2165 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:04:36Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2164 F1 UTC-Close Recheck
1. When: 2026-06-02 P2164 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:00:19Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2180 F1 UTC-Close Recheck
1. When: 2026-06-02 P2180 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:54:33Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2181 F1 UTC-Close Recheck
1. When: 2026-06-02 P2181 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:58:51Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2182 F1 UTC-Close Recheck
1. When: 2026-06-02 P2182 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:02:18Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2183 F1 UTC-Close Recheck
1. When: 2026-06-02 P2183 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:05:16Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2184 F1 UTC-Close Recheck
1. When: 2026-06-02 P2184 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:08:48Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2185 F1 UTC-Close Recheck
1. When: 2026-06-02 P2185 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T16:11:50Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2179 F1 UTC-Close Recheck
1. When: 2026-06-02 P2179 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:51:19Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2178 F1 UTC-Close Recheck
1. When: 2026-06-02 P2178 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:48:06Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2177 F1 UTC-Close Recheck
1. When: 2026-06-02 P2177 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:44:46Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2176 F1 UTC-Close Recheck
1. When: 2026-06-02 P2176 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:41:14Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2175 F1 UTC-Close Recheck
1. When: 2026-06-02 P2175 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:38:21Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2174 F1 UTC-Close Recheck
1. When: 2026-06-02 P2174 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:35:32Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2173 F1 UTC-Close Recheck
1. When: 2026-06-02 P2173 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:32:42Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2172 F1 UTC-Close Recheck
1. When: 2026-06-02 P2172 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:29:40Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2171 F1 UTC-Close Recheck
1. When: 2026-06-02 P2171 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T15:25:59Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In P2163 F1 UTC-Close Recheck
1. When: 2026-06-02 P2163 P2079 F1 UTC-close recheck.
2. Status: no ingest, preflight, Optuna runtime, production action, or unfreeze command was launched.
3. Note: step closed as `BLOCKED_BY_UTC_CLOSE` because current UTC `2026-06-02T14:55:22Z` was still before required close `2026-06-03T00:00:00Z`.

## No Runtime Error In 1d-to-1d Smoke Execution
1. When: 2026-06-02 P2034-P2038.
2. Status: long_only and short_only smoke runtime completed with launcher `status=OK`; readiness freeze restored/preserved.
3. Note: long_only classified `NEUTRAL_NO_TRADE`; short_only classified `PROVISIONAL_PLUS_GOAL_FAIL` and stored under neutral because `goal_pass=false`.

## No Runtime Error In Step 2 Smoke Command Set
1. When: 2026-06-02 P2032 Step 2 command set.
2. Status: command set `PASS`; only dry-run launcher checks were executed.
3. Note: CLI forwarding for `CalibrationGridPreset` and `ForceProfileEdgeCoverage` was added so `narrow` does not silently fall back to config `wide`.

## No Runtime Error In Step 1 Wiring Inventory
1. When: 2026-06-02 P2030 Step 1 wiring inventory.
2. Status: inventory `PASS`; no Optuna runtime command was launched; no readiness/unfreeze state changed.
3. Note: current pointer moved to Step 2 exact `1d -> 1d` smoke matrix and command set.

## No Runtime Error In Ordered Roadmap Checkpoint
1. When: 2026-06-02 P2029 planning checkpoint.
2. Status: no Optuna runtime command was launched; no readiness/unfreeze state changed.
3. Note: current pointer is Step 1 read-only wiring inventory; next steps require artifact/status before moving forward.

## No Runtime Error In 1d-to-1d Smoke Strategy Checkpoint
1. When: 2026-06-02 P2028 planning checkpoint.
2. Status: no Optuna runtime command was launched; no readiness/unfreeze state changed.
3. Note: first task is now to prove the contour by calibrating on one closed 1d train window and applying parameters on the next closed 1d test window.

## No New Error In Catalog Checkpoint
1. When: 2026-06-02 full calibration catalog scope update.
2. Status: no runtime command was launched; only docs/checkpoint/catalog directories were updated.
3. Note: next runner change must preserve robust multi-line JSON parsing and `PYTHONPATH='src'`.

## `rg.exe` Access Denied
1. When: 2026-06-02 during file searches.
2. Symptom: PowerShell reports `Program 'rg.exe' failed to run: Access is denied`.
3. Cause: local environment restriction on `rg.exe`.
4. Fix: use `Select-String` and `Get-ChildItem` fallback.
5. Artifacts: command output in chat only; no project artifact required.

## Python Module Not Found Without `PYTHONPATH`
1. When: running `.venv\Scripts\python.exe -m mlbotnav.text_guard` directly.
2. Symptom: `ModuleNotFoundError: No module named 'mlbotnav'`.
3. Cause: local package is under `src`.
4. Fix: set `$env:PYTHONPATH='src'` before module commands.
5. Works: `$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate`

## Multi-Line JSON Parser Bug In V3 Runner
1. When: first real `Package A long_only` run.
2. Symptom: pool launcher completed `OK`, but `run_optuna_v3_package_a.ps1` failed to parse terminal JSON.
3. Cause: terminal JSON was multi-line; parser expected one-line tail JSON.
4. Fix: updated `Parse-LastJsonObject` in `run_optuna_v3_package_a.ps1` to collect multi-line JSON from the end.
5. Status: fixed; rerun completed.

## Dry Run Wrote Empty Artifacts
1. When: initial dry-run of `run_optuna_v3_package_a.ps1`.
2. Symptom: dry-run printed future summary paths.
3. Cause: script reached artifact emission after dry-run loop.
4. Fix: added early `exit 0` after dry-run completion.
5. Status: fixed.

## Forward Stability Failed
1. When: cycle-2 candidate validation.
2. Symptom: `F1 FAIL` and `F2 FAIL`; F2 after UTC close produced `goal_fail`, `oos=0.0%`, `trades=0`.
3. Cause: local candidate was not portable to forward windows.
4. Fix: no direct fix; active decision became `NO_GO` and V3 bounded calibration was opened.
5. Artifacts:
   1. `reports/qa_gate/p2016_optuna_strict_exec_cycle2_forward_stability_final_fail_20260602T000048Z.json`
   2. `reports/qa_gate/p2017_optuna_strict_exec_cycle2_final_quality_decision_no_go_20260602T000048Z.json`

## Heartbeat Automation Confusion
1. When: after F2 UTC-close retry.
2. Symptom: user asked what was deleted.
3. Cause: a one-shot heartbeat automation was deleted after it completed; no project files were deleted.
4. Fix: clarify that only the automation `optuna-f2-retry-after-utc-close` was removed.
5. Status: no file/data deletion occurred.

## No Runtime Error In Hard Structural Audit
1. When: 2026-06-02 hard structural audit of Optuna/APTuna features, hypotheses, grids, and block catalog.
2. Status: read-only audit; no ingest, runtime, production action, unfreeze, or destructive file action was launched.
3. Artifact: `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md`.
4. Finding: block-level feature rows are isolated, but hypothesis/trend-filter semantics are global unless explicitly filtered.

## P2196D Train Gate Failed But Runtime Goal Passed
1. When: 2026-06-03 first strict runtime calibration start.
2. Status: tracked boundary, not infrastructure failure.
3. Artifact: `reports/adaptive/long_only_pool_20260603t101450z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T101454Z.json`.
4. Meaning: OOS goal passed (`+1.5266529420731034%`, `1` trade), but train gate failed (`auc`, low trades, sortino, train net return), so it must remain `TOP_EXPERIMENTAL` only.

## P2196E Empty Search Report Worker Crash
1. When: 2026-06-03 first `volume_flow narrow short_only` runtime attempt at `2026-06-03T10:18:59Z`.
2. Symptom: worker `w1` crashed with `json.decoder.JSONDecodeError` while reading `parsed["report_path"]`; launcher returned `PARTIAL_FAIL`.
3. Fix: `src/mlbotnav/adaptive_auto_train.py` now reads search reports through `_read_json_report_with_retry` and records `search_report_read_failed` instead of crashing the worker.
4. Validation: focused tests `83/83 OK`; rerun `2026-06-03T10:21:58Z` returned launcher `OK`, all 3 workers exit `0`.
5. Boundary: short result remains `NO_CANDIDATE` (`0%`, `0` trades), not infrastructure failure after the fix.

## H006 Pattern Fallback Candidate Lost Calibration Params
1. When: 2026-06-04 H006 `pattern` replay audit after block runtime.
2. Symptom: search-level `top_candidates` contained `calibration_params`, but final adaptive `best_oos.selected_calibration_params` was `{}` because fallback selection used `all_candidates_lite`.
3. Fix: `src/mlbotnav/adaptive_auto_train.py` now builds candidate pool with `_candidate_pool_from_search_report()` and prefers full `top_candidates` when they carry `calibration_params`.
4. Validation: focused tests `81/81 OK`; H006 replay artifact `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z.json` shows selected params present in `6/6` final results.

## H006 Pattern Train Failed On First Bad Candidate
1. When: 2026-06-04 control replay `pattern wide long_only`.
2. Symptom: some workers selected a current block candidate whose calibrated windows left too few rows for walk-forward train, causing `RuntimeError: No model candidates were successfully evaluated. skipped=[... Not enough rows for walk-forward ...]`.
3. Fix: candidate signature now includes `calibration_params`, and adaptive replay tries up to `8` candidates from the same search report before marking the repeat failed.
4. Validation: focused tests `81/81 OK`; rerun `pattern wide long_only` returned launcher `OK`, then full H006 replay returned `6/6` launcher `OK`.
5. Boundary: this does not weaken train gates; it only skips technically invalid parameter combinations from the same current block.

## H006 Edge Coverage Invisible For Pruned Trials
1. When: 2026-06-04 H006 min/max audit.
2. Symptom: `trial_history.csv` only contained completed/candidate rows, so forced min/max trials that were pruned could not be proven from the visible CSV.
3. Fix: `src/mlbotnav/optuna_search_candidate.py` now saves `calibration_params` immediately after sampling, records `calibration_forced_edges`, embeds `grid_edge_coverage_audit`, and writes `grid_edge_coverage_audit_*.json`.
4. Validation: focused tests `94/94 OK`; runtime smoke H006 `long_only narrow` produced `reports/optuna/long_only/grid_edge_coverage_audit_20260604T111552Z.json` with `completed=8`, `pruned=4`, `failed=0`.
5. Boundary: small smoke does not prove all min/max coverage; it proves the audit artifact works. Full-budget replay is still needed for final coverage proof.

## H006 Core Search Parameters Were Not Force-Seeded
1. When: 2026-06-04 follow-up after edge coverage audit.
2. Symptom: profile parameters had forced min/max audit, but core search parameters (`horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`) were only passively observed.
3. Fix: `src/mlbotnav/optuna_search_candidate.py` now force-seeds core min/max in the first 10 trials and records `core_params`, `core_params_suggested`, `core_forced_edges`.
4. Validation: focused tests `94/94 OK`; runtime smoke H006 `long_only narrow` produced `reports/optuna/long_only/grid_edge_coverage_audit_20260604T113102Z.json` with core coverage `5/5 PASS`.
5. Boundary: profile coverage still requires enough trial budget; for H006 profile coverage is not guaranteed by a 12-trial worker smoke.

## H006 Profile Edge Coverage Was Duplicated Per Worker
1. When: 2026-06-04 full H006 replay audit after core forcing.
2. Symptom: each worker started profile edge forcing from index zero, so `w1/w2/w3` duplicated the same early profile edges. Also core-like names appeared as profile failures.
3. Fix: core names are excluded from profile audit; when `ForceProfileEdgeCoverage=on`, profile sampling uses the full linked profile set; profile edge index is distributed across workers using the `_wN` suffix in `contour_id`.
4. Validation: focused tests `95/95 OK`; final H006 replay artifact `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z.json` shows every grid at profile `18/18` and core `5/5`.
5. Boundary: H006 still has no positive trading candidate; this fix proves calibration coverage, not profitability.

## Cascade Mode Not Yet Implemented
1. When: 2026-06-04 after H006 edge-coverage replay and Optuna trials audit.
2. Symptom: current battle replay proves `narrow/medium/wide` coverage separately, but does not yet implement a true cascade where `medium` is centered around the best `wide` candidate and `narrow` is centered around the best `medium` candidate.
3. Status: not an infrastructure crash; this is the next target mode.
4. Active rule: `CASCADE_BLOCK_CALIBRATION` fixed in `docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`.
5. Boundary: no code changes or runtime launches were made while fixing the rule.

## C001 Search Report Timestamp Collision
1. When: 2026-06-04 `C001 price_volatility long_only wide` runtime.
2. Symptom: worker `w1` and `w2` both point to `reports/pipeline/optuna_search_candidate_SOLUSDT_1m_20260604T144246Z.json`, and that report records `contour_id=w2`.
3. Status: launcher and all workers completed `OK`; this is an artifact traceability issue, not a worker crash.
4. Impact: per-worker search-report uniqueness is not clean for this run. Best OOS and adaptive summaries are still available, but cascade audit should avoid assuming one unique search report per worker until report naming is made unique.
5. Artifact: `reports/qa_gate/c001_block01_price_volatility_long_wide_20260604T144429Z_RU.md`.

## F001 Strict Passport Runtime Connection
1. When: 2026-06-22 F001 strict passport hookup.
2. Status: no new known runtime error.
3. Note: `F001_RET1_ALLOW` is intentionally a runtime-action column, not a model feature column, so `FEATURE_COLUMNS` and `features_block.yaml` parity remain unchanged.
4. Validation: `py_compile PASS`; focused tests `25/25 OK`; Optuna runtime tests `65/65 OK`; matrix compile check PASS; `text_guard PASS`.

## F001 OOS Runtime Action Column Missing
1. When: 2026-06-22 first F001 LONG 1d/1d runtime after passport hookup.
2. Symptom: selected F001 params reached train/search, but final OOS report showed `F001_RET1_ALLOW_gate_active=false`.
3. Cause: `src/mlbotnav/oos_evaluate.py` preserved `FEATURE_COLUMNS` but not `RUNTIME_ACTION_COLUMNS` before calling `run_prob_backtest`.
4. Fix: `oos_evaluate.py` now includes `RUNTIME_ACTION_COLUMNS` in OOS scoring/backtest frame.
5. Validation: `py_compile PASS`; `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_dataset_inference_mode`, `tests.test_backtest_fields`, `tests.test_optuna_search_runtime`: `84 tests OK`.
6. Final rerun: `F001_RET1_ALLOW_gate_active=true`; best LONG OOS `-5.352332468117016%`, `3` trades, `goal_fail`.

## F001 No-Timeout Runtime Is Trade Logic, Not Worker Failure
1. When: 2026-06-22 F001 LONG rerun after user requested timeout exit disabled.
2. Status: no new infrastructure error.
3. Change: `-DisableTimeoutExit` / `--disable-timeout-exit` disables time-based close; positions close only by TP/SL or `end_of_data`.
4. Validation: `py_compile PASS`; `tests.test_backtest_fields`, `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_optuna_search_runtime`: `78 tests OK`.
5. Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T094448Z.json`.
6. Runtime result: launcher `OK`, workers `3/3`, formal best worker had `0` trades and `0.0%`; best tradeful worker had `6` trades and `-47.79331627195255%`.
7. Boundary: the `0`-trade formal best is not a crash; it is the optimizer selecting a no-trade candidate under this risk policy. Tradeful outcome remains `NO_GO`.

## Legacy Optuna Matrices Mixed Action Layers
1. When: 2026-06-22 user correction after F001 timeout/exit discussion.
2. Symptom: old Optuna configs/proposals mixed feature calculation knobs, signal thresholds, hypotheses, runtime thresholds, risk controls, and exits in one calibration surface.
3. Status: architecture issue, not a worker crash.
4. Fix boundary: old matrices are not deleted, but are marked `legacy/frozen` for new baseline work.
5. New rule: each calibration/backtest action must have an action passport and explicit allowlist of tunable params.
6. New guard: `src/mlbotnav/optuna_space.py` enforces `passport_mode.allowed_calibration_params` when `passport_mode.enabled=true`.
7. Active F001 matrix: `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`, only `F001_move` and `F001_thr_pct`.
8. Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`: `13 tests OK`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; YAML parse PASS; F001 passport matrix compile PASS for `long_only` and `short_only`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T101720Z.json`.

## Local Passport Matrix Could Bypass Central Registry
1. When: 2026-06-22 after user requested one config with block-level passports.
2. Symptom/risk: a matrix with local `passport_mode.enabled=true` could be structurally clean but not proven to match the central passport registry.
3. Fix: `configs/calibration_action_passports.yaml` is now the single block/passport registry with `blocks.B001..B006`, Russian names, active/planned passports, and runtime/backtest subpassport slots.
4. Fix: `src/mlbotnav/optuna_space.py` now validates passport matrices against registry metadata: `registry_path`, `registry_block_id`, `registry_passport_id`, `action_id`, `allowed_calibration_params`, and `active_matrix_path`.
5. Active F001 registry location: `blocks.B001.active_passports.F001`.
6. Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `79 tests OK`; env override compile PASS for F001 passport matrix.

## F003 Passport Range Did Not Hit Max With Current Step
1. When: 2026-06-22 RET_N F001-F005 passport hookup.
2. Status: resolved grid-definition risk, not a runtime failure.
3. Symptom/risk: F003 passport says `F003_thr_pct` min `0.03`, max `1.20`, step `0.02`. The current profile expander starts at min and adds step, so the last generated value is `1.19`, not `1.20`.
4. Impact: F003 matrix compiles and is usable, but strict edge coverage would not prove the exact declared max until max-anchor behavior is added or the passport range is adjusted.
5. Fix: `src/mlbotnav/optuna_space.py` now appends/preserves the `max` anchor when step does not land on it exactly.
6. Boundary: no F003 runtime calibration was launched before this ambiguity was resolved.
7. Validation: `py_compile PASS`; focused tests `98/98 OK`; F003 matrix compile proof `60 0.03 [1.17, 1.19, 1.2] True`.

## Optuna Passport Studies Reused Trials Across Matrices
1. When: 2026-06-22 during first MACD F013-F015 audit.
2. Symptom: pre-fix MACD runs selected `calibration_params` from the wrong passport, for example F013/F015 runs could replay F012/F014 params because Optuna study identity did not include the executable passport matrix.
3. Cause: `run_signature` included dates, mode, grids, objective, and gates, but not the compiled passport space. Different passport matrices with the same dates/mode therefore shared the same effective study.
4. Fix: `src/mlbotnav/optuna_search_candidate.py` now builds `space_signature` from `passport_mode`, profile names, feature rows, and hypothesis rows, then includes it in `run_signature` and search-engine metadata.
5. Boundary: pre-fix MACD results were discarded. Final MACD audit uses clean reruns after the fix.
6. Validation: `py_compile PASS`; focused tests `112/112 OK`; clean MACD audit shows selected params isolation `PASS` for all F013-F015 LONG/SHORT runs.

## F016 ADX14 Passport Run Had No New Infrastructure Error
1. When: 2026-06-22 F016 ADX14 long/short passport run.
2. Status: no new known runtime/worker error.
3. Result boundary: both LONG and SHORT completed technically `OK`, `F016_ADX14_ALLOW` was active in OOS gate diagnostics, but OOS was negative.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure.
5. Validation: `py_compile PASS`; focused tests `114/114 OK`; matrix compile PASS for `long_only` and `short_only`.

## STOCH F017-F018 Passport Run Had No New Infrastructure Error
1. When: 2026-06-22 STOCH F017-F018 long/short passport run.
2. Status: no new known runtime/worker error.
3. Result boundary: both LONG and SHORT completed technically `OK`, `F017_F018_STOCH14_ALLOW` was active in OOS gate diagnostics, but OOS was negative.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure.
5. Validation: `py_compile PASS`; focused tests `116/116 OK`; matrix compile PASS for `long_only` and `short_only`.

## F021 TRUE_DELTA Was Falling Back To Proxy Without Side-Volume Data
1. When: 2026-06-22 during VOLUME F019-F021 audit.
2. Symptom: F021 runs could select `TRUE_DELTA` even though current OHLCV data has no `buy_volume`/`sell_volume`; runtime then silently used proxy delta.
3. Fix: `src/mlbotnav/dataset.py` now returns no F021 signal for `TRUE_DELTA` unless both side-volume columns are present. `PROXY_DELTA` remains explicit and separate.
4. Boundary: pre-fix F021 LONG/SHORT runs were discarded; final VOLUME audit uses post-fix F021 reruns only.
5. Validation: `py_compile PASS`; focused tests `118/118 OK`.

## VOLUME F019-F021 Passport Run Had No New Worker Error
1. When: 2026-06-22 VOLUME F019-F021 long/short passport run.
2. Status: no new launcher/worker infrastructure error after the F021 logic fix.
3. Result boundary: all F019-F021 LONG/SHORT runs completed technically `OK` and action gates were active, but no OOS non-negative tradeful candidate was found.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure.

## F022 OBV Slope 5 Passport Run Had No New Worker Error
1. When: 2026-06-22 F022 OBV slope 5 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: LONG and SHORT completed technically `OK`, and `F022_OBVSLOPE5_ALLOW` was active in OOS gate diagnostics.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG had zero OOS trades; SHORT was negative.

## F023 MFI14 Passport Run Had No New Worker Error
1. When: 2026-06-22 F023 MFI14 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: LONG and SHORT completed technically `OK`, and `F023_MFI14_ALLOW` was active in OOS gate diagnostics.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. Both LONG and SHORT were negative.

## DENSITY/VPOC Block A Passport Run Had No New Worker Error
1. When: 2026-06-22 DENSITY/VPOC Block A F025/F029/F033/F034 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all eight Block A runs completed technically `OK`, and each OOS report used the matching single action gate.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. Some runs had zero trades; all tradeful runs were negative.

## LEVEL/RANGE/CHANNEL Block A Passport Run Had No New Worker Error
1. When: 2026-06-22 LEVEL/RANGE/CHANNEL Block A F035/F036/F037 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all six Block A runs completed technically `OK`, and each OOS report used the matching single action gate.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. F037 LONG had zero trades; all tradeful runs were negative.

## FIBONACCI_GRID F040/F041 Passport Run Had No New Worker Error
1. When: 2026-06-22 FIBONACCI_GRID F040/F041 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all four runs completed technically `OK`; action gates were isolated to `F040_FIB0382DIST_ALLOW` or `F041_FIB0618DIST_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG runs had zero trades; SHORT runs were negative and exited by baseline timeout.

## ENTRY_QUALITY_CONTEXT F042-F044 Passport Run Had No New Worker Error
1. When: 2026-06-22 ENTRY_QUALITY_CONTEXT F042-F044 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all six runs completed technically `OK`; action gates were isolated to `F042_TPCONTEXT_ALLOW`, `F043_SLCONTEXT_ALLOW`, or `F044_RRCONTEXT_ALLOW`.
4. Fix/guard added: side-aware runtime columns `*_LONG` and `*_SHORT` prevent LONG from passing via SHORT context or the reverse.
5. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. Tradeful runs were negative; two runs had zero trades.

## BREAKOUT_RETEST F045-F049 Passport Run Had No New Worker Error
1. When: 2026-06-22 BREAKOUT_RETEST F045-F049 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all ten runs completed technically `OK`; action gates were isolated to one present passport action column per run.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. Several runs had zero trades; all tradeful runs were negative.
5. Note: targeted dataset test emits all five action columns, but pandas warns about DataFrame fragmentation from many column inserts. This is a performance warning only, not a blocking correctness error.

## MARKET_STRUCTURE F050-F052 Passport Run Had No New Worker Error
1. When: 2026-06-22 MARKET_STRUCTURE F050-F052 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all six runs completed technically `OK`; action gates were isolated to one present passport action column per run.
4. Final classification: F051 SHORT is a `POSITIVE_TEST_CANDIDATE`, not an infrastructure event and not a production GO. It has positive OOS `+2.810523%` but only one OOS trade.
5. F050 and F052 runs had zero OOS trades on this window.

## F051 SHORT Multi-Day Validation Had No New Worker Error
1. When: 2026-06-23 F051 BOS down SHORT validation.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all three adjacent validation windows completed technically `OK`; action gates were isolated to `F051_BOSDOWN_ALLOW`.
4. Final classification: validation result `VALIDATION_FAIL_NO_PROMOTION`, not infrastructure failure. The original one-day positive `+2.810523%/1 trade` did not reproduce; the three validation windows had `0%/0 trades`.

## F001-F083 Route Closeout Had No New Worker Error
1. When: 2026-06-23 route closeout after F051 validation.
2. Status: no new infrastructure error.
3. Result boundary: this was a control/audit closeout, not a new runtime.
4. Final classification: `CLOSED_NO_PRODUCTION_GO`; no feature from `F001-F083` is eligible for promotion without a new explicit validation route.

## CANDLE_PATTERNS F053-F060 Passport Run Had No New Worker Error
1. When: 2026-06-22 CANDLE_PATTERNS F053-F060 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all sixteen runs completed technically `OK`; action gates were isolated to one present candle-pattern action column per run.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. Tradeful runs were F059 LONG, F054 SHORT, and F053 LONG; all were negative.
5. Note: focused dataset test can emit pandas DataFrame fragmentation warnings from many action-column inserts. This is a performance warning only, not a blocking correctness error.

## DIVERGENCE_PATTERNS F061-F066 Passport Run Had No New Worker Error
1. When: 2026-06-22 DIVERGENCE_PATTERNS F061-F066 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all twelve runs completed technically `OK`; action gates were isolated to one present divergence action column per run.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. Tradeful runs were F061 LONG, F063 LONG, and F065 LONG; all were negative.
5. Note: focused dataset test can emit pandas DataFrame fragmentation warnings from many action-column inserts. This is a performance warning only, not a blocking correctness error.

## PATTERN_QUALITY F067-F068 Passport Run Had No New Worker Error
1. When: 2026-06-22 PATTERN_QUALITY F067-F068 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all four runs completed technically `OK`; action gates were isolated to `F067_PATTERNSTRENGTH_ALLOW` or `F068_PATTERNAGE_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. F067 LONG had zero OOS trades; all tradeful runs were negative.
5. Exit boundary: tradeful runs closed by baseline `timeout`; TP/SL/timeout were not calibrated inside B021.

## CHART_PATTERNS F069-F077 Passport Run Had No New Worker Error
1. When: 2026-06-22 CHART_PATTERNS F069-F077 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all eighteen runs completed technically `OK`; action gates were isolated to one present chart-pattern action column per run.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. Several runs had zero OOS trades; all tradeful runs were negative.
5. Exit boundary: tradeful runs mostly closed by baseline `timeout`; F069 LONG also had one `sl`. TP/SL/timeout were not calibrated inside B022.
6. Note: focused dataset test can emit pandas DataFrame fragmentation warnings from many action-column inserts. This is a performance warning only, not a blocking correctness error.

## PATTERN_COMPOSITE_ENTRY F080-F081 Passport Run Had No New Worker Error
1. When: 2026-06-22 PATTERN_COMPOSITE_ENTRY F080-F081 side-specific passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: F080 LONG and F081 SHORT completed technically `OK`; action gates were active and isolated to `F080_PATTERNLONG_ALLOW` or `F081_PATTERNSHORT_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. F080 LONG had zero OOS trades; F081 SHORT had one negative timeout trade.
5. Fix/guard added: `F080_PATTERNLONG_ALLOW` is LONG-only and `F081_PATTERNSHORT_ALLOW` is SHORT-only in backtest row/vector gating.
6. Exit boundary: TP/SL/timeout were not calibrated inside B024; baseline timeout remained enabled.

## PATTERN_CONFIRMATION F078-F079 Passport Run Had No New Worker Error
1. When: 2026-06-22 PATTERN_CONFIRMATION F078-F079 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: all four runs completed technically `OK`; action gates were isolated to `F079_PATTERNLEVELCONF_ALLOW` or `F078_PATTERNVOLCONF_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. F079 LONG/SHORT had zero OOS trades; F078 LONG/SHORT were negative.
5. Exit boundary: F078 LONG closed by `6 timeout` and `1 sl`; F078 SHORT closed by `4 timeout`. TP/SL/timeout were not calibrated inside B023.
6. Note: focused dataset test can emit pandas DataFrame fragmentation warnings from many action-column inserts. This is a performance warning only, not a blocking correctness error.

## F030 Density Bin Share 240 Passport Run Had No New Worker Error
1. When: 2026-06-23 F030 density_bin_share_240 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: both runs completed technically `OK`; action gates were isolated to `F030_BINSHARE240_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG `-13.432324%/3`, SHORT `-24.712835%/9`.
5. Exit boundary: all tradeful F030 exits were baseline `timeout`; TP/SL/timeout were not calibrated inside F030.

## F031 Density Cluster Share 240 Passport Run Had No New Worker Error
1. When: 2026-06-23 F031 density_cluster_share_240 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: both runs completed technically `OK`; action gates were isolated to `F031_CLUSTERSHARE240_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG `-6.153364%/2`, SHORT `-55.142239%/26`.
5. Exit boundary: all tradeful F031 exits were baseline `timeout`; TP/SL/timeout were not calibrated inside F031.

## F032 Density VPOC Share 240 Passport Run Had No New Worker Error
1. When: 2026-06-23 F032 density_vpoc_share_240 long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: both runs completed technically `OK`; action gates were isolated to `F032_VPOCSHARE240_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG `-6.153364%/2`, SHORT `-18.625751%/6`.
5. Exit boundary: all tradeful F032 exits were baseline `timeout`; TP/SL/timeout were not calibrated inside F032.

## F038 Position In Range Passport Run Had No New Worker Error
1. When: 2026-06-23 F038 position_in_range long/short passport run.
2. Status: no new launcher/worker infrastructure error.
3. Result boundary: both runs completed technically `OK`; action gates were isolated to `F038_RANGEPOSE_ALLOW`.
4. Final classification: strategy/passport result `NO_GO`, not infrastructure failure. LONG `-13.432324%/3`, SHORT `-4.489987%/1`.
5. Exit boundary: all tradeful F038 exits were baseline `timeout`; TP/SL/timeout were not calibrated inside F038.
## No Error In ML Trade Dataset Stage 2.2 Passport Context
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `2.2`.
2. Status: no code/test blocker.
3. Result boundary: passport context is added to trade CSV write paths, but the CSV is not fully ML-ready until trade identity, duration labels, hit labels, and MAE/MFE are added.
4. Validation: changed modules `py_compile PASS`; focused tests `55/55 OK`; `text_guard PASS`.
5. Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.
## No Error In ML Trade Dataset Stage 2.3 Trade Identity
1. When: 2026-06-23 ML/Optuna separated-contour WBS step `2.3`.
2. Status: no code/test blocker.
3. Result boundary: trade identity is added to trade CSV write paths, but the CSV is not fully ML-ready until duration labels, hit labels, and MAE/MFE are added.
4. Validation: changed modules `py_compile PASS`; focused tests `56/56 OK`; `text_guard PASS`.
5. Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.

## Not Worker Error In B001 Single-Worker Fast Finish
1. When: 2026-06-24 B001 family-unified `long_only` single-worker `1x9/9`.
2. Status: no worker/launcher failure found.
3. Evidence: `max_threads=9`, `search_workers=9`, `workers_used=9`, `n_trials_override=42`; trial errors `0`.
4. Result boundary: run finished fast because strict family gate `5/5` produced `EMPTY_ACTION_GATE`, `0` trades, `signal_count_after_entry_action_gates=0`.
5. Artifact: `reports/qa_gate/b001_single_worker_fast_finish_audit_20260624T180000Z_RU.md`.
6. Next diagnostic: test B001 family-unified `4/5`, then `3/5` if needed; do not treat this as lost CPU power.

## Optuna Single-Worker Is Not Equivalent To 3x3
1. When: 2026-06-24 worker-profile audit after switching from `ProcessWorkers=3` to `ProcessWorkers=1`.
2. Status: not a storage or worker-count bug, but a profile semantics mistake.
3. Evidence: `1x9/9` reports `workers_used=9`, but it is one Python process; `3x3/9` is three independent Python processes.
4. Result boundary: lower visible CPU/noise on `1x9/9` is expected, especially with strict `5/5` empty-gate trials.
5. Artifact: `reports/qa_gate/optuna_1x9_vs_3x3_worker_audit_20260624T183000Z_RU.md`.
6. Rule: use `3x3/9` for real load/runs; keep `1x9/9` only for one-study diagnostics.
## Visual v1 manual entries used arrow centers instead of signal-entry contract 2026-06-25
Статус: `SUPERSEDED_BY_V2_SIGNAL_ENTRY_CONTRACT`.

Симптом: v1-разметка восстанавливала времена по центрам красных стрелок и рисовала их как target entry. Это смешивало две разные сущности: свечу с фитилем/дном и реальный вход на следующей свече.

Фикс: создан v2-контракт `signal_candle_time_utc -> target_entry_time_utc`, где вход для LONG считается на open следующей свечи с slippage: `entry_open_price * (1 + slippage_bps / 10000)`.

Артефакты:
1. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/manual_entries.json`;
2. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_zoom_panels_20260625T102849Z.png`.

Граница: до визуального подтверждения пользователем v2 не считать финальной ML-разметкой.

## Visual Entry High Recall Is Not ML Candidate 2026-06-25
Статус: `EXPECTED_DEV_NOISE_NOT_PROMOTABLE`.

Симптом: `DQ01` ловит `10/11`, но дает `73` ложных входа; `DQ03` ловит `11/11`, но дает `95` ложных входов.

Классификация: это не ошибка инфраструктуры и не готовый ML-кандидат. Это high-recall карта дна для построения следующего слоя `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`.

Правило: не передавать `DQ01/DQ03` в ML, не считать production GO, не подбирать TP/SL до стабилизации входа. Следующий фикс должен уменьшать false через cluster priority и паспортные context/trigger/confirm/suppress признаки.

## Visual Entry CP01 Still Misses 08:26 And 17:00 2026-06-25
Статус: `DEV_KNOWN_GAP_NOT_ML_BLOCKER`.

Симптом: новый cluster-priority слой `CP01_DQ01_CLUSTER10_SCORE12` снизил false до `28`, но пропустил ручные входы `08:26` и `17:00`.

Классификация: это ожидаемый DEV-gap после подавления шума. Это не инфраструктурная ошибка и не повод возвращать весь high-recall `DQ03` в ML.

Правило: добирать `08:26` и `17:00` отдельными мягкими подслоями, сохраняя no-lookahead и контролируя false. Не использовать `F078/F079` как entry-row confirmation до отдельной проверки, потому что там есть риск entry-candle lookahead.

## Visual Entry CP06 Still Has 28 False Entries 2026-06-25
Статус: `DEV_RECALL_FIXED_FALSE_REMAINING`.

Симптом: `CP06_CP01_RECOVER_NOWICK_LATE_RETEST` закрыл `11/11` ручных входов, но оставил `28` false entries.

Классификация: recall-gap закрыт, но precision еще не production-ready. Это не ML-кандидат.

Правило: следующий слой должен уменьшать false entries, но не ломать `11/11`. Запрещено использовать entry-candle `high/low/close/volume`, `green_entry_candle`, будущие return/MAE/MFE и непроверенные `F078/F079` entry-row confirmations.

## Visual Entry RBKD V0 Too Noisy 2026-06-29
Status: `known_limit / no_ml`.

`REVERSAL_BOTTOM_KNIFE_DROP_V0` честно соблюдает вход на следующем open и `lookahead=NO`, но на новых днях оказался слишком шумным: `2026-05-13` дал `2/9` hits и `81` false, `2026-05-14` дал `1/17` hits и `83` false.

Причина: пользовательские входы не всегда выглядят как классическая перепроданность/нож. Значительная часть точек является support/retest/trend-dip continuation, где RSI/Stoch/MFI могут быть горячими.

Mitigation: не передавать V0 в ML и не крутить его как production-кандидат. Следующий слой должен быть online event-state `SWING_SUPPORT_RETEST_EVENT_V1`, а не offline cluster winner.

Также после таймаутного перебора 2026-06-29 были найдены и остановлены зависшие `python.exe -` PID `14996` и `228`. После каждого нового прогона обязательно повторять process-check.
## Visual Entry Event First Entry Is Too Early 2026-06-29
Status: `known_limit / no_ml`.

`SWING_SUPPORT_RETEST_EVENT_V1` режет ложные входы относительно `RBKD V0`, но часто входит раньше пользовательского главного low внутри той же зоны. Из-за этого ручная точка оказывается пропущенной по cooldown.

Mitigation: не использовать правило "первый вход в зоне" как финальную стратегию. Следующий слой должен выбирать значимую signal-low свечу: `SIGNIFICANT_LOW_SELECTOR_V1`.
## Visual Entry Significant Low Selector V1 Still Too Noisy 2026-06-29
Status: `known_limit / no_ml`.

`SIGNIFICANT_LOW_SELECTOR_V1` улучшил диагностическую карту входов, но не стал кандидатом. На пользовательском v2 holdout `2026-05-14`: `SLS06` дал `5/17` hits и `71` false, `SLS05` дал `2/17` hits и `20` false, `SLS10` дал `13/17` hits и `463` false.

Mitigation: не передавать V1 в ML и не запускать TP/SL/Optuna. Следующий слой должен быть `LOW_CLUSTER_RANKER_V2`: выбрать один главный signal-low внутри активной зоны по past-only признакам, а не брать все похожие свечи.

## Visual Entry Low Cluster Ranker V2 Has Low Recall 2026-06-29
Status: `known_limit / no_ml`.

`LOW_CLUSTER_RANKER_V2` резко снизил false, но потерял recall: `LCR04` дал `3/17` hits и `10` false, `LCR07` дал `2/17` hits и `4` false, `LCR06` дал `7/17` hits и `64` false.

Mitigation: не расширять один общий ranker до шума. Следующий шаг - разделить missed-входы по режимам: deep capitulation, hot reclaim/support, trend dip continuation, structure/BOS/FIBO/volume.
## Visual Entry Regime Split Ranker V1 Still Too Noisy 2026-06-29
Status: `known_limit / no_ml`.

`REGIME_SPLIT_RANKER_V1` подтвердил, что пользовательские low-входы принадлежат разным режимам, но текущие режимные фильтры все еще шумные: `STRUCTURE` `7/17` при `84` false, `TREND` `7/17` при `95` false, `HOT` `6/17` при `87` false. `DEEP` чище, но дает только `2/17`.

Mitigation: не передавать V1 в ML и не запускать TP/SL/Optuna. Следующий шаг - `REGIME_FALSE_SUPPRESSION_V2`, отдельно по шумным режимам, с сохранением контракта `signal close -> next open`, `lookahead=NO`, no future rewrite.

## Visual Entry Regime False Suppression V2 Still Too Noisy 2026-06-29
Status: `known_limit / no_ml`.

`REGIME_FALSE_SUPPRESSION_V2` снизил часть шума, но не стал кандидатом: лучший `FSV21_UNION_STRICT_FALSE_CONTROL` дал `7/17` hits и `41` false; `FSV05_TREND_DIP_EMA_RECLAIM` дал `6/17` hits и `40` false. Чистый deep `FSV02` дает только `2/17`, зато всего `4` false.

Причина: ручные low-входы смешивают несколько контекстов, а общие режимные фильтры не отличают хороший low от обычного бокового микролоя.

Mitigation: не передавать V2 в ML и не запускать TP/SL/Optuna. Следующий слой - `ONLINE_LOW_EVENT_QUALITY_V3`: online event-state по low/support-зоне, suppress горячих верхних полок и только past-only признаки, без future return и без entry-candle lookahead.

## Visual Entry Online Low Event Quality V3 Has Low Recall 2026-06-29
Status: `known_limit / no_ml`.

`ONLINE_LOW_EVENT_QUALITY_V3` резко снизил шум, но потерял recall: лучший `OLEV20_UNION_EVENT_QUALITY_BALANCED` дал `3/17` hits и `7` false. Это лучше по шуму, чем V2 (`41` false), но не достаточно для стратегии.

Причина: чистый event-quality слой слишком жестко оставляет только около-event-low сигналы и не покрывает много пользовательских hot/trend/deep recovery входов.

Mitigation: не расширять `OLEV20` обратно до шума. Следующий слой - `DEEP_RECOVERY_AND_HOT_RECALL_V4`: отдельные recovery-кирпичи для deep и hot/trend, плюс suppress ранних false.

## Visual Entry Hot Trend Recall Still Too Noisy 2026-06-29
Status: `known_limit / no_ml`.

`DEEP_RECOVERY_AND_HOT_RECALL_V4` улучшил общий баланс: основной `DRHR20` дал `5/17` hits и `13` false. Но hot/trend diagnostic дал `8/17` hits при `43` false, поэтому его нельзя включать в рабочий union.

Причина: hot/trend источники ловят нужные reclaim-входы, но одновременно цепляют длинные ложные серии в `01:xx`, `07:xx`, `09:xx`, `21-22:xx`.

Mitigation: не передавать V4 в ML и не включать hot/trend diagnostic в основной union. Следующий слой - `HOT_TREND_FALSE_SUPPRESSION_V5`.

## Visual Entry V5 Union Still Has Too Many False Entries 2026-06-29
Status: `known_limit / no_ml`.

`HOT_TREND_FALSE_SUPPRESSION_V5` подтвердил, что строгий `HTFS01` полезен как отдельный hot/trend-слой: `4/17` hits, `1` false, `5` entries. Но лучший union `HTFS20_UNION_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION` все еще дает `14` ложных входов при `9/17` hits.

Причина: основная часть ложных входов приходит из базовой V4-ветки, а не из нового `HTFS01`. Ложные union-входы: `01:15`, `02:57`, `03:09`, `03:52`, `06:11`, `07:14`, `07:25`, `09:06`, `13:37`, `17:23`, `18:47`, `19:30`, `21:57`, `23:50`.

Mitigation: не передавать V5 union в ML. Следующий слой должен подавлять false базовой V4-части отдельно и не ломать чистый `HTFS01`.

## Visual Entry V6 Is One-Day Clean But Not Yet Validated 2026-06-29
Status: `known_risk / no_ml`.

`BASE_FALSE_SUPPRESSION_V6` дал лучший текущий результат на `2026-05-14`: `9/17` hits, `1` false, `10` entries. Базовая V4-часть очищена с `13` false до `0` false.

Риск: результат получен на одном дне, а deep early exception для `03:23` может оказаться подогнанным. Единственный текущий false `18:47` приходит из `HTFS01`, а не из базы.

Mitigation: не передавать V6 в ML. Следующий обязательный шаг - прогон без изменения параметров на `2026-05-13` validation и только потом разбор `18:47`.

## Visual Entry V6 Fails Validation Day 2026-06-29
Status: `validation_fail / no_ml`.

`BASE_FALSE_SUPPRESSION_V6` дал хороший one-day результат на `2026-05-14`, но без изменения параметров на `2026-05-13` получил `0/9` hits и `1` false. Это означает, что V6 нельзя считать стратегией и нельзя передавать в ML.

Также первый validation-запуск упал из-за слишком длинного имени PNG на Windows. Исправлен только короткий label рендера, без изменения торговых условий.

Mitigation: не подкручивать V6 точечно под `2026-05-13`. Следующий слой должен быть `GENERALIZATION_V7`: разбор validation-missed режимов и проверка сразу на двух днях.

## Fresh target-led step pointer can become stale 2026-06-30

Статус: `PROCESS_RISK_FIXED_FOR_C02_8_3`.

Симптом: после ручной разметки C02 и good/bad audit рабочая лестница все еще показывала старый следующий подпункт `6.1`, хотя фактически нужно было идти в `8.3 split/router`. Это создало ощущение перепрыгивания пунктов.

Причина: новый подшаг `6.3 Good/Bad audit` был сделан после ручной разметки, но не был сразу внесен в `PASSPORT_BENCH_V0_STEP_PLAN_20260630_RU.md`.

Решение: план, C02 passport и `CURRENT_STATUS_RU.md` обновлены. Текущий следующий подпункт теперь только `8.3.1_DESIGN_C02A_TRUE_DEEP_CAPITULATION_CORE_RULES_FROM_PAST_ONLY_FEATURES_NO_SCORER_YET`.

Правило: после каждого содержательного подпункта обновлять рабочую лестницу сразу, включая `done/current_next/blocked`, чтобы не продолжить старый пункт и не перейти к scorer раньше времени.

## Fresh target-led visual can be too blurry or miss execution price 2026-06-30

Статус: `FIXED_FOR_C02_SPLIT_ROUTER_PRICE_CLARITY_V0`.

Симптом: full-day split/router PNG был обзорным, при увеличении размывался и не показывал цену входа. Пользователь справедливо указал, что такой скрин трудно использовать как рабочий график.

Решение: для C02 создан `price_clarity_fix_v0` с таблицей `entry_open_price`, zoom-sheet PNG, high-res full-day PNG и SVG-вариантами.

Правило: обзорный full-day без цены входа не считать достаточным рабочим визуалом. Для следующего подпункта показывать `signal`, `entry`, `entry_open_price`, `entry + 5 bps`; цена только execution-only, не scorer/Optuna/ML-признак.

## RU Markdown generated with broken encoding 2026-06-30

Статус: `FIXED_FOR_C02_SPLIT_ROUTER_RU_MD`.

Симптом: два новых RU-md файла C02 показывали битые знаки вопроса вместо русского текста:

1. `C02_SPLIT_ROUTER_DECISION_V0_20260630_RU.md`;
2. `C02_SPLIT_ROUTER_ENTRY_PRICE_TABLE_V0_20260630_RU.md`.

Решение: оба файла переписаны нормальным русским UTF-8 текстом. Проверка по C02 split/router и текущим статусным файлам больше не находит битых строк.

Правило: новые `_RU.md` отчеты проверять на битые знаки вопроса перед показом пользователю.
## Visual Entry V8 Union Still Too Noisy 2026-06-29

Status: `partial_brick / no_ml`.

`NEGATIVE_CONTEXT_SUPPRESSION_V8` улучшил шум относительно V7 и дал первый чистый кирпич:

1. `2026-05-13` `V8_02_HOT_CHAIN_EVENT_LOW_SUPPRESSION`: `1/9`, `0` false, `1` entry, пойман `08:48`.
2. `2026-05-14` `V8_01_HOT_FIRST_NEGATIVE_SUPPRESSION`: `4/17`, `29` false, `33` entries.

Но общий `V8_20_UNION_NEGATIVE_SUPPRESSION` все еще непригоден: на `2026-05-14` `11/17`, но `168` false. Это визуально снова каша, а не стратегия.

Mitigation: не передавать V8 union в ML и не запускать TP/SL/Optuna. Следующий шаг - `V9_BRICK_BY_BRICK_SELECTOR`: сначала отдельные чистые кирпичи, потом аккуратное объединение только тех режимов, которые сами выглядят чисто на PNG.

## Visual Entry GENERALIZATION_V7 Diagnostic Fail 2026-06-29

Status: `validation_fail / no_ml`.

`GENERALIZATION_V7` был построен как честная diagnostic-проверка hot-first, hot-chain, warm-retest и deep/event режимов после провала V6 на `2026-05-13`.

Результат:

1. Validation `2026-05-13`: best `G7_02_HOT_CHAIN_DIP_DIAG` = `1/9`, `22` false, `23` entries, f1 `0.0625`.
2. Holdout `2026-05-14`: best by f1 `G7_01_HOT_FIRST_RECLAIM_DIAG` = `4/17`, `43` false, `47` entries, f1 `0.1250`.
3. Union на `2026-05-14` дал `11/17`, но `203` false, поэтому это не стратегия.

Причина: простые режимные признаки находят нужные лои, но одновременно цепляют слишком много боковых микролоев, горячих верхних полок и повторных retest-серий.

Mitigation: не передавать V7 в ML и не запускать TP/SL/Optuna. Следующий слой - `NEGATIVE_CONTEXT_SUPPRESSION_V8`, где сначала режется шум, а не расширяется recall.
# Known Error 2026-06-30: старый контекст смешивает visual-entry задачи

Статус: `PROCESS_RISK_FIXED_BY_FRESH_TZ`.

Симптом: при продолжении в длинном чате агент может цеплять старые V7/V8/V9/V10/V11, старую хронологию или частичные Optuna-идеи как следующую задачу, хотя пользователь хочет новый чистый порядок работы от ручных входов.

Причина: не было отдельного свежего протокола, который жестко отделяет target-led процесс от старой очереди экспериментов.

Решение: создан `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_FRESH_PROCESS_TZ_RU.md`. Новый чат должен стартовать с него и не продолжать старые runner-версии без связи с `T01..T10`.

## Fresh target-led ledger is not visual lock yet 2026-06-30

Статус: `EXPECTED_MANUAL_CONFIRM_REQUIRED_NO_ML`.

Первый fresh ledger по `2026-05-14` создан из auto-detected пользовательской v2-разметки. Точки T01..T10 и типы входов имеют статус `candidate_needs_visual_confirm`.

Риск: если сразу строить стратегию по этим типам без визуального подтверждения, можно снова получить старую проблему: стратегия оптимизируется вокруг неточно снятых или неверно классифицированных входов.

Правило: `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10.json` не является target-lock. Перед паспортом нужно глазами подтвердить T01..T10 на чистом графике, особенно первый кластер `HOT_RECLAIM_SUPPORT` (`T04/T07/T08`). Optuna и ML запрещены.
# Known Guard 2026-07-01 Arrow Shift Pending Is Not Gold

При разборе `15` спорных кандидатов пользователь отметил красными стрелками места, где вход должен быть не в текущей авто-точке. Эти стрелки нельзя автоматически превращать в gold-разметку по одному обзорному скриншоту: нужна отдельная zoom/time фиксация.

Текущие авто-точки `LA026`, `LA048`, `LA057`, `LA059`, `LA062` в V1 отклонены как current-entry negative, а возможные новые точки остаются `arrow_shift_pending`.
# Known Guard 2026-07-01 Block Count Is Not Signal

По аудиту dataset V1 запрещено считать вход хорошим только потому, что совпало много блоков. `safe_core_hit_count=5/6` часто встречается в плохих точках.

`LOW_ANCHOR_RECLAIM` в текущем виде дал `0/16` positive и не должен использоваться как standalone allow. `B013_density_support`, `B020_divergence_support` и широкие формы `B015/B017` тоже нельзя отдавать как самостоятельный сигнал без узкого паспорта.
# Known Guard 2026-07-01 Do Not Jump From Dataset To ML

После фиксации `FRESH_TARGET_LED_ML_DATASET_LADDER_RU.md` запрещено перепрыгивать из базы `28/79` сразу в ML, Optuna, scorer или target-lock.

Текущий следующий подпункт только один: `2.1_SUPPORT_RETEST_LOW_REVIEW_SHEET_9_GOOD_16_BAD_NO_ML_NO_OPTUNA`. После него разрешен только draft-паспорт `SUPPORT_RETEST_LOW`.
# Known Guard 2026-07-02 SUPPORT_RETEST_LOW V0 Too Dirty For Lock

`SUPPORT_RETEST_LOW` entry-only scorer V0 сохранил `9/9` good, но пропустил `8/16` bad. Статус: `SEED_MUST_KEEP_PASS_FALSE_ENTRIES_TOO_MANY`.

Запрещено считать V0 готовым scorer/lock. Следующий шаг только `V1_REJECT_GUARDS` по оранжевым false-positive.

# Known Guard 2026-07-02 Outcome Miner Is Not A Signal

`OUTCOME_LOW_MINER_V0` использует будущий ход `+1.5%` только как offline outcome label для отбора кандидатов на ручной просмотр.

Нельзя:

1. использовать `hit_1p5pct`, `bars_to_hit`, `max_future_move_pct_in_window` как feature/scorer/Optuna-признак;
2. считать найденные hit-кандидаты готовыми good labels без user visual review;
3. передавать outcome-miner CSV в ML/export/training без отдельного `APPROVED_FOR_ML`.

Порог `+1.5%` показал себя строгим: на `2026-05-15` он оставил только `1` hit-кандидат, поэтому как единственный способ собрать все хорошие входы он неполный.

# Known Guard 2026-07-02 Cooldown Sweep Is Not Significant Level Logic

Широкий `outcome_low_miner_v0_wide_sweep_0p8pct` с `cooldown 5`, `min_score 0`, `max_anchor_age 12` является диагностикой, а не рабочей стратегией.

Причина: рельсы запрещают использовать `cooldown-сетки` как замену логике входа. Такой sweep перебирает много микролоев и поднимает шум.

Правильный путь: сначала определить значимый локальный low/уровень по left-context и структуре участка, затем считать entry next open и только потом offline outcome `+0.8%/+1.0%/+1.5%` для review. Outcome не является feature/scorer/ML-сигналом.
## Known Guard 2026-07-02 Good 1pct Pool Is Not ML Dataset Yet

`GOOD_1PCT_REVIEW_POOL` собирает кандидаты и outcome `+1%` для ускоренного визуального review. Это не готовый ML dataset.

Нельзя:

1. использовать `hit_1pct_*`, `hit_time_*`, `target_1pct_*` как causal feature входа;
2. считать все GOOD строки автоматически gold-разметкой без ручного просмотра PNG;
3. запускать ML/export/training/scorer/target-lock/Optuna по этому CSV без отдельного approved-ledger и `APPROVED_FOR_ML`;
4. заменять ручную логику значимых локальных low широкой cooldown-сеткой.

Правильное использование: скрипт быстро собирает run-папку, пользователь глазами подтверждает хорошие входы, затем подтвержденные строки отдельно переносятся в approved-ledger.
## Known Guard 2026-07-02 Do Not Jump From W18-W20 To Full History

Пользователь запретил сразу расширять текущий `+1% review-pool` на все `126` дней как рабочий процесс.

Причина: на коротком диапазоне уже видно, что часть `+1%` входов является ножами или DCA-перегрузом. Если сразу масштабировать это на full-history, получится большая, но грязная база.

Правило:

1. сначала `DCA_RISK_AUDIT_V0` на `W18-W20` (`2026-04-27..2026-05-17`);
2. затем ручная проверка классов/кластеров и исправление багов визуализации/логики;
3. только после этого `FULL_HISTORY_KNIFE_MAP_V0` на `126` дней;
4. `+1% hit` не считать gold-разметкой без risk-aware review.

## Known Guard 2026-07-02 1pct Hit Can Be Late Pump Dependency

`DCA_RISK_AUDIT_V0` показал, что `+1% hit` может быть достигнут только поздним пампом после долгого висения набора сделок.

Ключевой пример: `2026-05-02` в W18-W20 имеет `44` GOOD-сделки по outcome, но первые `10` GOOD/day классифицируются как `C_LATE_PUMP_DEPENDENT`. Это не чистые входы для ML.

Нельзя:

1. считать все `GOOD_1PCT` строки positive label;
2. обучать ML на late-pump/DCA-overload как на обычных clean long-входах;
3. расширять на full-history до ручного решения, какие классы риска разрешены.

Правильное использование: `A_FAST_CLEAN` и часть `B_DCA_SURVIVABLE` могут стать кандидатами positive после visual review; `C_LATE_PUMP_DEPENDENT`, `D_CLUSTER_OVERLOAD`, `E_FALLING_KNIFE_*`, `F_NO_1PCT_ROOM` должны идти в отдельный разбор/hard-negative/управление риском.
## 2026-07-02 GOOD_1PCT берет микролои подряд

Симптом: `GOOD_1PCT`/DCA обзор может давать десятки `+1%` hit за день, но многие точки являются микролоями, дублями одного basin, late-pump dependent входами или местами, где пользователь руками показал более правильный low ниже.

Решение V0: не считать `+1% hit` хорошим входом само по себе. Добавлен слой `SIGNIFICANT_LOW_CALIBRATION_V0`, который разделяет:

- `KEEP_SIGNIFICANT_LOW_V0`;
- `USER_SHIFT_PENDING_REANCHOR`;
- `USER_REJECT_CURRENT_ENTRY`;
- `REJECT_NOT_SIGNIFICANT_LOW_V0`;
- `REJECT_DUPLICATE_BASIN_LOW_V0`.

Пока не исправлено автоматически: точная новая свеча для `USER_SHIFT_PENDING_REANCHOR`. Ее нужно снимать отдельным zoom и подтверждать глазами.

## 2026-07-02 LA048 ложный keep после overview feedback

Симптом: после первого user actual overview слой оставлял `LA048` как green keep, хотя пользователь позже уточнил, что там нет нормальной точки входа. При удалении только `LA048` рядом мог всплыть соседний `LA049`.

Актуальное решение V1C3:

- `LA048` = `USER_REJECT_CURRENT_ENTRY`;
- `LA049` = `USER_REJECT_CURRENT_ENTRY`;
- `LA050` = `USER_APPROVE_CURRENT_ENTRY` и `KEEP_SIGNIFICANT_LOW_V0`;
- `LA051` = `REJECT_DUPLICATE_BASIN_LOW_V0`.

При следующих повторах `2026-05-02` использовать run `siglow_20260502_user_actual_v1c3_20260702_190227`, а не старый V1B.

## 2026-07-03 Не растягивать close-zoom до future target

Симптом: если на close-zoom рисовать `+1% target` и включать его в расчет `ylim`, свечи около входа становятся сжатыми, и пользователь плохо видит точную точку entry.

Решение: для ручного review делать отдельный close-zoom по локальному диапазону цен. В нем показывать:

- красную точку low свечи;
- зеленый треугольник `entry_open`;
- короткую белую черту `entry +5bps`.

Future target можно хранить в CSV/JSON как offline outcome/reference, но не растягивать им рабочую картинку для глаз.

## 2026-07-03 Reanchor Applied слои смешивали ручные точки и старые сделки

Симптом: после перезапуска/повтора пользователь увидел на графике не те сделки: старые DCA/GOOD outcome-строки и applied/reanchor точки визуально смешались, из-за чего входы выглядели уехавшими.

Причина: ручные точные reanchor-решения были зафиксированы в run-артефактах и статусах, но не имели отдельного JSON source-of-truth и отдельного renderer. Также `RA003` смешивал визуальный low marker и execution entry, если смотреть только одну колонку времени.

Решение V0:

1. создан `configs/visual_entry/manual_reanchors/SOLUSDT_1m_2026-05-02_SIGNIFICANT_LOW_MANUAL_REANCHORS_V0.json`;
2. создан `src/mlbotnav/visual_entry_manual_reanchor_review_v0.py`;
3. `signal_time_utc`/`entry_time_utc` теперь являются контрактом исполнения, а `visual_marker_*` только подсказкой для глаз;
4. pending `RA002` не попадает в clean confirmed overview;
5. renderer не читает DCA/GOOD_1PCT rows.

Правило дальше: после любой ручной правки двигать точку только в JSON source-of-truth и заново запускать `visual_entry_manual_reanchor_review_v0`. Не править старые run CSV как источник истины.

## 2026-07-03 GOOD_1PCT entry сдвигался от confirmation-свечи

Симптом: на closeup/overview `GOOD_1PCT_REVIEW_POOL` пользователь видел, что часть входов стоит выше low и иногда через свечку или несколько свечей. На старом run `2026-05-02` из `44` GOOD-сделок `12` имели `entry_time_utc != anchor_time_utc + 1 minute`.

Причина: `visual_entry_low_anchor_suggester.build_candidates()` находил фактический `anchor_idx`, но затем ставил `signal_time_utc` от текущей confirmation-свечи `idx`, а `entry_idx = idx + 1`. Поэтому контракт был `entry = confirmation + 1`, а не `entry = low + 1`.

Решение V0:

1. `signal_idx = anchor_idx`;
2. `entry_idx = anchor_idx + 1`;
3. `confirmation_idx` и `confirmation_time_utc` оставлены только как справочный контекст;
4. в `GOOD_1PCT` CSV добавлены индексы для аудита;
5. добавлен тест `tests/test_visual_entry_low_anchor_suggester.py`.

Контрольный run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034`.

Проверка: `52` строки, `42` GOOD, `10` BAD, нарушений `entry != anchor + 1m` нет.

## 2026-07-07 Codex/VS Code грузит CPU/RAM/disk из-за STAS run-артефактов

Симптом: после перезагрузки и открытия VS Code/Codex появляется постоянная нагрузка CPU/RAM/disk, а в процессах видны фоновые Git-команды.

Причина: тяжелые папки `STAS1_GOOD_LOW_REVIEW/runs`, `STAS2_MARKET_PHASE_REVIEW/runs`, `STAS3_PERCENT_LADDER_REVIEW/runs` не были исключены из Git и VS Code watcher/search/Pylance. При `git add -A` Codex/Git пытался пройти по PNG/CSV/XLSX артефактам. Вложенных `.git` в проекте не обнаружено.

Решение:

1. добавить STAS `runs` в `.gitignore`;
2. добавить тяжелые папки в `.vscode/settings.json` для `files.watcherExclude`, `search.exclude`, `python.analysis.exclude`;
3. если завис `git add -A`, остановить только этот процесс и проверить отсутствие `.git/index.lock`;
4. перезагрузить окно VS Code, чтобы watcher-настройки вступили в силу.
## 2026-07-09 STAS4 pattern pandas FutureWarning

Симптом: при прогонах Stas4 стратегий с `pattern` появляется предупреждение pandas из `src/mlbotnav/visual_entry_strategy_passport_overlay_v2d_patterns.py` по `.shift(...).fillna(False).astype(bool)`.

Статус: не блокирует прогон. PNG, CSV, JSON и RU-отчеты создаются. Для текущего review-слоя исправление не требуется, но перед стабилизацией Stas4-кода стоит заменить участок на явное приведение типов без silent downcasting.
## 2026-07-11 Codex Cold Start Disk Spike From Large Local History

Статус: `environment_guard / codex_startup_disk_load`.

Симптом: после перезагрузки компьютера и запуска Codex диск может около минуты показывать `100%`, затем возвращаться к нормальным `1..5%`.

Текущий аудит не подтвердил активную Git-проблему: `git status`, `git ls-files --others --exclude-standard` и `git write-tree` выполняются быстро; зависшего `git add -A` нет. Вероятная причина - холодное чтение локальной истории и кешей Codex плюс параллельная активность Windows/Defender/индексации.

Главные тяжелые места: `C:\Users\007\.codex` около `13.2 GB`, `sessions` около `7.5 GB`, backup/archived-сессии около `4.4 GB`, `logs_2.sqlite` около `724 MB`, а также `_codex_offload_20260530` внутри проекта около `5.9 GB`.

Правило: не удалять `.codex`, backup, archived sessions, `_codex_offload_*`, логи или историю без прямого подтверждения пользователя. Для облегчения сначала переносить архивы из рабочей папки и только затем отдельно решать очистку старых сессий.

## 2026-07-14 STAS5 V4 auto-group forward требует ручной визуальной проверки

Статус: `known_limitation / v4_auto_group_forward_review`.

V4 train dataset и модель готовы, но forward `2026-05-26..30` строит `group_id` автоматически по временным окнам кандидатов. Это рабочий review-режим, а не окончательная ручная разметка.

Симптом: auto-groups могут отличаться от того, как пользователь глазами обвел бы локальную зону. Поэтому `ENTER` на forward PNG нужно проверять именно по группам: лучший top1 внутри группы, плохие рядом, причина почему вход плохой/хороший.

Текущий результат forward: `363` rows, `25` auto-groups, `ENTER=24`, `UNSURE=16`, `SKIP=323`.

Правило: если на PNG `26..30` видны неверные группы или лишние ENTER, исправлять надо `group_id`/reason/group policy, а не возвращаться к построчному old ML KEEP/CUT. Старые `ML_KEEP_SCORE/ML_DECISION`, future/postfact/TP/Stas3/exit остаются запрещенными model features.

Отдельное замечание: `pytest` не установлен в доступных Python окружениях, поэтому V4 тестовые функции были проверены прямым smoke-run (`3 PASS`). Для полного pytest-runner нужен отдельный setup окружения.

## 2026-07-14 STAS5 V4 full-group признаки не live-safe

Статус: `architecture_guard / v4_future_group_leakage`.

Симптом: текущий V4 group-rank train/forward дает красивые входы, но часть group features рассчитана по уже собранной полной группе. Это не TP/Stas3 leakage, но это leakage будущего состава группы относительно момента раннего кандидата.

Причина: offline `_add_group_features()` знает final group size/duration/range, final group low, full-group rank and lower future candidate existence. В live на момент LA017 нельзя знать, что позже появится LA021.

Правило: текущий V4 run `stas5_v4_train_20260714_163911` и forward `stas5_v4_forward_20260526_20260530_20260714_164144` считать `OFFLINE_GROUP_REVIEW_NOT_LIVE_SAFE`. Не использовать как боевую live-модель.

Дальше нужен V4L:

1. только `v4l_*_so_far` признаки;
2. `LIVE_SAFE_FEATURE_ALLOWLIST`;
3. banned-column scan;
4. `feature_available_time_utc <= entry_time_utc`;
5. `prefix invariance`;
6. отсутствие retroactive feature/score/decision changes.

Главный план: `STAS5_ML_CORE/08_STAS5_V4L_LIVE_SAFE_GROUP_RANKER_PLAN_RU.md`.

## 2026-07-14 STAS5 V4L live-safe контур создан

Статус: `resolved_for_pipeline / still_needs_visual_quality_review`.

Старая проблема V4 full-group leakage закрыта для нового рабочего запуска через отдельный контур V4L. В model features теперь попадают только `v4l_*_so_far` признаки, а guard проверяет banned columns и prefix-invariance. Dataset `2026-05-01..2026-05-25` прошел `PASS`: `1710` строк, `103` winners, prefix-invariance failures `0`.

Ограничение остается качественное, не архитектурное: честный live-safe forward уже не может знать, что через несколько минут появится лучший low. Поэтому часть входов может быть раньше/хуже, чем в красивом offline V4. Исправлять это нужно калибровкой live-признаков, порогов и sequential policy, а не возвратом full-group future полей.

## 2026-07-15 STAS5 V4/V4L не использовать как финальную стратегию

Статус: `frozen_failed_strategy / pivot_to_v5_row_ml`.

Пользовательская проверка показала, что V4/V4L group-rank логика не решает главную задачу качества входов. Ограничение "один вход на группу" и sequential group behavior не должны становиться торговой стратегией. Это не надо чинить поверхностными policy/кулдаунами/лимитами входов.

Правило: следующий рабочий контур должен обучать ML по строкам кандидатов на исправленных good/bad метках. `group_id` и `reason_code` можно использовать как audit/label explanation, но не как торговое ограничение и не как future feature.

## 2026-07-15 Day23 V1 ledger конфликтовал с новой pre-knife пометкой

Статус: `resolved_by_new_artifact / use_V2_PRE_KNIFE`.

Для `2026-05-23` старый `USER_CORRECTED_V1` оставлял `LA007` как `BEST_GOOD`, а `LA002`/`LA014` как `GOOD_ALT`. Новая пользовательская пометка большим красным прямоугольником запрещает верхнюю pre-knife полку до flush. По свечам flush low: `2026-05-23T07:50:00Z`, `low=81.35`; аудит-просадка верхних entries до этого low около `-3.10..-3.55%`.

Исправление создано отдельным файлом, V1 не перезаписан:

`STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V2_PRE_KNIFE.csv`

Для будущей V5-сборки меток использовать day23 `USER_CORRECTED_V2_PRE_KNIFE`, иначе модель снова увидит верхнюю pre-knife зону как good.
## 2026-07-15 Codex CPU From Repeated Internal Git Diff On Dirty Worktree

Статус: `environment_guard / codex_cpu_load`.

Симптом: Codex может заметно грузить CPU без зависшего `git add -A`. Во время проверки группа `Codex` потребляла примерно `5.3%..9.2% CPU` и около `3.5..3.6 GB PrivateMB`, общий CPU прыгал `22.8%..44.4%`.

Причина: рабочее дерево сильно разрослось и стало грязным. Неигнорируемые файлы выросли до `1574` файлов на `424.8 MB`, основной источник `STAS5_ML_CORE` (`1220` файлов, около `389.8 MB`). Codex периодически запускает внутренний `git diff --find-renames --numstat -z` от `Codex.exe`, а также краткие `git add -u`/`git add -A`, чтобы пересчитать состояние изменений. В текущей проверке `git diff --cached --name-only` пустой и `.git/index.lock` отсутствует.

Правило: не считать это той же проблемой, что старый зависший `git add -A`, пока `git status` быстрый и нет долгого `git add`. Не убивать процессы без необходимости. Сначала уменьшать dirty worktree или исключать generated artifacts после решения по source-of-truth.
## 2026-07-16 Codex Git Scan Relief Applied

Статус: `environment_fix / codex_cpu_load / no_delete`.

Для снижения CPU-нагрузки Codex без удаления файлов добавлены ignore/exclude для generated/run-папок `STAS5_ML_CORE/artifacts/` и `STAS5_ML_CORE/runs/`. Это снизило неигнорируемый хвост с `1574` файлов / `424.8 MB` до `381` файла / `41.6 MB`.

Правило дальше: не возвращать STAS5 `artifacts` и `runs` в Git scan-поверхность без отдельного решения. Source-of-truth документы, схемы и run-скрипты STAS5 остаются видимыми.

## 2026-07-16 Idle Disk Spikes From Defender And UI Processes

Статус: `environment_guard / defender_io_spikes / no_delete`.

Симптом: после разгрузки Git/VS Code пользователь все еще видит движение диска/CPU в простое. В коротких замерах активных `git.exe` нет, `.git/index.lock` нет, процессы `Codex`/`codex`/`Code` стоят в `Idle`.

Причина по текущему замеру: главный дисковый всплеск в процессных счетчиках дал `MsMpEng` (Microsoft Defender), до примерно `10..21 MB/s` в коротком окне. Codex тоже может кратко появляться в I/O-счетчиках, но ниже. CPU дополнительно дают `explorer`, `Taskmgr`, `aida64`, Chrome и активный интерфейс Codex.

Правило: не отключать Defender и не добавлять исключения без отдельного разрешения пользователя. Не трогать папки `STAS*`, особенно `STAS5` и `STAS6`, без прямой команды.
## Known Note 2026-07-20 V5C Review Graphs ALL_ENTRIES vs ANNOTATED

`*_ALL_ENTRIES.png` является чистой копией исходного V5C `visual_review` и не обязан показывать продиктованные пользователем `GOOD/BAD/RISK BAD`. Для визуальной проверки review-команды нужно открывать `*_ANNOTATED.png`. Этот файл строится тем же V5C renderer-ом, сохраняет `Fon/LONG/SHORT/WAVE` и добавляет overlay поверх цены.

Важно: `*_ANNOTATED.png` не должен рисовать индивидуальные стрелки и текстовые плашки возле каждой review-точки, потому что они зашумляют цену. Правильный стиль: зеленый круг для `GOOD`, ярко-красный круг для `RISK BAD`, красный квадрат для обычного `BAD`, плюс компактная легенда-счетчик.

## 2026-07-22 Codex Update Uses ChatGPT.exe Process Name

Статус: `environment_guard / codex_update_process_name_change`.

Симптом: после обновления Codex снова грузит CPU, хотя старые процессы `Codex`/`codex` уже раньше прижимались.

Причина: пакет `OpenAI.Codex_26.715.10079.0` запускает главную оболочку как `ChatGPT.exe`. Старые команды, которые выставляли приоритет только для `Codex`/`codex`, не затрагивали основной renderer/gpu. Дополнительно VS Code-расширение `openai.chatgpt-26.715.31925` может поднимать отдельный `codex.exe app-server`.

Правило: при разгрузке после этого обновления учитывать `ChatGPT.exe`, `codex.exe`, `Code.exe`, `node_repl.exe` и VS Code extension server. Не удалять файлы, не отключать Defender и не трогать `STAS*` без отдельного разрешения.

## 2026-07-23 VS Code Codex Extension Server Can Be Needed

Статус: `environment_guard / vscode_codex_server_required`.

Симптом: в панели VS Code появляется `Работа Codex неожиданно остановлена`.

Причина: отдельный сервер расширения VS Code `openai.chatgpt-26.715.31925...\codex.exe app-server` не запущен. Если его остановить для разгрузки, панель VS Code Codex может перейти в аварийное состояние.

Правило: если пользователь хочет рабочий Codex в VS Code, не останавливать VS Code extension server. Для мягкой разгрузки выставлять `Idle`-приоритет и использовать watcher/search/Pylance исключения. Постоянное отключение расширения делать только отдельным решением пользователя.

## 2026-07-23 Duplicate STAS9 Shortcut Opened Terminal

Статус: `resolved / desktop_shortcut_target_mismatch`.

Симптом: ярлык с именем `🤖 STAS9 Главный агент` открывал отдельное окно терминального Codex вместо VS Code.

Причина: старый ярлык сохранял target на `STAS9_CONTROL_PLANE/START/start_STAS9.bat`, тогда как новый `🤖 STAS9 Assistant` уже указывал на VS Code. Похожие названия позволяли выбрать старую точку входа.

Исправление: оба ярлыка указывают на `Code.exe --new-window "...\\MLbotNav_STAS9.code-workspace"`. Технический `.bat` сохранён только внутри проекта. Правило: пользовательские ярлыки STAS9 не привязывать к terminal launcher.
