# TZ: Ускорение AKFP+ML до боевого прогона (без каши)

Дата: 2026-05-25
Статус: ACTIVE
Область: AKFP (калибровка) + ML (обучение/оценка), без ломки текущей бизнес-логики.

## 1. Цель
1. Сократить время калибровки (сейчас слишком долго).
2. Разделить быстрый цикл калибровки и полный цепочный контроль.
3. Сохранить строгую валидацию CSV/XLSX/движка/гейтов.
4. Подключить агентный узел в контур калибровки как ассистент выбора, не как замена ML-движка.

## 2. Роли и ответственность
1. Блок AKFP: подбор гипотез/фич и комбинаций, бюджет перебора, shortlist.
2. Блок ML: обучение/валидация/OOS и метрики результата.
3. Цепочный контроль: table_canon -> convergence -> audit_chain -> gates.
4. Агентный узел: ранжирование кандидатов и сужение пространства поиска между итерациями.

## 3. Приоритетный план (строго по порядку)
### P1. Скорость без изменения логики (выполнено)
1. Один `table_canon_pack` на окно в `daily_long_short_cycle`.
2. Ускоренный CPU-контроль в `adaptive_auto_train` (turbo-профиль).
3. Убран дубль `table_convergence` в P23 при reuse daily-артефактов.
4. Добавлен reuse артефактов daily в P23 (без повторного pack).

Критерий PASS:
1. P23 проходит PASS с reuse-режимом.
2. Нет каскадных FAIL из-за перезаписи run_dir.

### P2. Full-coverage оптимизация (выполнено)
1. В `run_hypotheses_full_coverage_1d1d.ps1` добавлен режим pack-once на mode.
2. Опция `-PackPerHypothesis` оставлена для обратной совместимости.

Критерий PASS:
1. По умолчанию pack не повторяется на каждую гипотезу.
2. Логика chain/gate не меняется.

### P3. Агентный узел AKFP (следующий)
1. Вводим агентный промежуточный отбор:
   1. FEAT_ONLY
   2. HYP_ONLY
   3. HYP_PLUS_FEAT
2. Агент отбрасывает заведомо слабые связки до тяжелого прогона.
3. На вход ML отправляется только shortlist.

Критерий PASS:
1. Меньше кандидатов в тяжелом цикле.
2. Нет потери воспроизводимости (все решения в JSON-аудите).

### P4. Боевой цикл 1d->1d (после P3)
1. long_only и short_only строго отдельно.
2. Для каждого режима:
   1. train day = D-1
   2. test day = D
   3. полный chain audit PASS
3. Сводка в едином отчете и хронологии.

Критерий PASS:
1. Цепочка 5+ по таблицам сходится.
2. Прогон воспроизводим.

## 4. Обязательные правила
1. Не смешивать long/short контуры.
2. Не запускать heavy-перебор до PASS по цепочке.
3. После каждого шага — запись в `docs/CHANGELOG_CHRONOLOGY_RU.md`.
4. Любой FAIL фиксировать с `failed_stage`, `exit_code`, `stderr_tail`, путями отчетов.

## 5. Контрольные артефакты
1. `reports/qa_gate/daily_long_short_cycle_*.json`
2. `reports/qa_gate/p23_operator_unified_*.json`
3. `reports/qa_gate/table_convergence_5plus_*.json`
4. `reports/table_canon_current/audit_chain_report.json`
5. `reports/qa_gate/features_block_audit_*.json`
6. `reports/qa_gate/orderbook_source_audit_*.json`
7. `reports/qa_gate/tz_gate_*.json`
8. `reports/qa_gate/p72_freeze_ready_*.json`

## 6. Следующий шаг
1. Реализовать P3 (агентный узел shortlist) и сделать контрольный 1d->1d прогон по long_only, потом отдельно short_only.

## 7. Статус выполнения на 2026-05-25
1. P1: выполнен (ускорение без смены бизнес-логики).
2. P2: выполнен (full-coverage pack-once).
3. P3: выполнен (agent shortlist-узел + интеграция в bridge и combo).
4. Следующий активный пункт: P4 (боевой раздельный цикл long_only -> short_only + полный chain audit).


## 8. Оперативный статус на 2026-05-26
1. P1-P4: CLOSED (PASS) с подтвержденной фиксацией в QA-артефактах.
2. P5-P9: закрыты в контуре AKFP bridge/post-control/full-coverage (PASS).
3. Следующий активный переход по рабочему плану: `Q5.5-LONG.2` -> `Q5.5-SHORT`.
4. Правило: после каждого шага обязательна запись факта в `docs/ACTIVE_WORK_ITEMS_RU.md` и `docs/CHANGELOG_CHRONOLOGY_RU.md`.
