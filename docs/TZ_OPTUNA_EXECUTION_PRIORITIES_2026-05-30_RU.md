# TZ_OPTUNA_EXECUTION_PRIORITIES_2026-05-30_RU

Дата: 2026-05-30  
Контур: только Optuna/APTuna (ML runtime не изменяем)

## 1. Цель цикла
1. Довести Optuna-контур до полного перебора и стабильного gate-решения.
2. Подтвердить, что фичи/гипотезы и связанные профили реально участвуют в runtime-поиске.
3. Получить воспроизводимый кандидат для перехода из `NO_GO` в `GO` без нарушения изоляции ML-контура.
4. Уточнение 2026-05-31: в режиме `1d train / 1d test` на `1m` основной фокус — корректное завершение калибровочного контура (сетки/переборы/цепочки/аудит), а не доказательство устойчивой прибыльности на коротком окне.

## 2. Жесткие ограничения (MUST)
1. Не менять ML runtime-контур вне optuna-ветки исполнения.
2. Запуски только раздельно: `long_only` и `short_only`.
3. После каждого шага: `pip check`, `python -m mlbotnav.text_guard`, `python -m mlbotnav.readiness --show`.
4. Любой шаг фиксировать в `docs/ACTIVE_WORK_ITEMS_RU.md` и `docs/CHANGELOG_CHRONOLOGY_RU.md`.

## 3. Факт-срез на 2026-05-30
1. Канонический статус верхнеуровневых задач после freeze:
1. `P452-OPTUNA-FULL-PROFILE-COVERAGE-TZ` - `IN_PROGRESS` (coverage governance остается открытым).
2. `P477-P485-OPTUNA-FULL-COVERAGE-BATTLE` - `DONE` (staged battle выполнен, gate-review проведен).
3. `P486-QUALITY-REMEDIATION-NEXT` - `DONE` (шаги 1..126 завершены, критерии качества не достигнуты).
4. `P491-OPTUNA-P2-NOGO-CHECKPOINT` - `DONE`.
5. `P492-OPTUNA-FINAL-NOGO-FREEZE` - `DONE` (`NO_GO` зафиксирован в текущем decoupled contour).
2. По качеству:
1. Финальный checkpoint `P491`: критерии (`3x reproducible per mode`, `all_tradeful=true`, `mean OOS>=0`) не выполнены.
2. Финальный пакет `P492`: новые variant-runs в текущем контуре запрещены до пересборки гипотез/gate.
3. По полноте профилей:
1. В матрице: 6 активных блоков, 56 активных feature rows, 20 hypothesis rows, 22 linked parameter profiles.
2. Глобально по истории trial_history (все файлы): для long/short есть покрытие `22/22`, включая попадание `min` и `max` по каждому linked profile.
3. На последнем единичном запуске strict coverage FAIL:
1. short_only: `13/22` (пропуски 9 профилей)
2. long_only: `18/22` (пропуски 4 профилей)
4. Вывод:
1. Полнота в контуре достигается на серии прогонов, но не гарантируется на одном последнем прогоне.
2. При текущем наборе гипотез/gate quality-стабилизация не достигнута; контур остается в `NO_GO freeze`.

## 4. Приоритеты исполнения (post-freeze)
1. P0 (срочно): Coverage Gate Normalization
1. Ввести единый критерий покрытия:
1. `single-run strict coverage` для целевого B5 прогона
2. `rolling aggregate coverage` по последним N запускам (например 10) как fallback-контур
2. Зафиксировать PASS/FAIL-порог:
1. linked profile coverage ratio = `1.0`
2. out-of-range profiles = `0`
3. Обязательный артефакт: `reports/qa_gate/optuna_profile_coverage_<mode>_<ts>.json` для обоих режимов.
2. P1 (обязательно до любого unfreeze): Revised Hypothesis/Gate Package
1. Подготовить новый bounded пакет гипотез: что меняем, зачем, ожидаемый эффект, риски.
2. В пакете явно определить новые guard-пороги отбора кандидата (tradeful + quality).
3. До утверждения пакета запрещены новые runtime-variant runs в текущем контуре.
3. P2: Управленческая консистентность реестра
1. Убрать двусмысленные пары `IN_PROGRESS` + `DONE` для одной стадии (B2/B3/B4/B5), оставить один канонический активный статус на этап.
2. Свести статусы к цепочке: `planned -> in_progress -> done -> verified`.

## 5. Definition of Done
1. `P452` закрыт:
1. strict coverage PASS для `short_only` и `long_only`
2. aggregate coverage PASS за rolling окно
2. `P477-P485` закрыт:
1. B5 all-block запуск подтвержден артефактами
2. gate-review переоценен на свежих данных
3. `P486` закрыт:
1. либо получен `GO` по quality-критериям
2. либо зафиксирован финальный `NO_GO` с freeze и closure report

## 6. Порядок действий в freeze-режиме
1. Поддерживать обязательные пост-проверки документов и реестра (`pip check`, `text_guard`, `readiness --show`).
2. Обновлять только governance-артефакты и ТЗ (без новых variant-run запусков).
3. Подготовить и утвердить `Revised Hypothesis/Gate Package`.
4. Только после утверждения пакета открыть отдельный шаг на controlled unfreeze.

## 7. Последняя фиксация цикла
1. `P492` freeze: `reports/qa_gate/optuna_no_go_freeze_20260530T070322Z.json`.
2. Post-freeze governance closeout: `reports/qa_gate/p493_post_freeze_governance_20260530T070804Z.json`.

## 8. Следующий обязательный шаг (strict)
1. P1366-OPTUNA-STRICT-EXECUTION-V65:
1. выполнить V65-S1 -> V65-S2 -> V65-S3 -> V65-S4 в strict `3x9`,
2. сохранить strict `3x9`, single-change и раздельные режимы,
3. фиксировать каждый шаг обязательными аудитами и синхронизацией реестров.
2. Источники:
1. docs/TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V65_2026-05-31_RU.md
2. docs/TZ_OPTUNA_STRICT_EXECUTION_2026-05-31_RU.md
3. docs/TZ_OPTUNA_CONTOUR_COMPLETION_2026-05-31_RU.md






