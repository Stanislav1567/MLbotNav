# Optuna Production Unfreeze Policy Gate (2026-06-01)

Дата: 2026-06-01
Контур: только `Optuna/APTuna` в `MLbotNav`
Ограничение: `ML runtime` не трогаем, `OptunaMlSignalBackend=off`

## Update 2026-06-02
1. Раздел `13.4` ниже остается историей выполненной процедуры на дату `2026-06-01`.
2. Он не является текущим разрешением на запуск после recovery/strict-exec.
3. Актуальный операционный статус определяется последним evidence package:
   `reports/qa_gate/p2017_optuna_strict_exec_cycle2_final_quality_decision_no_go_20260602T000048Z.json`.
4. Пока действует `P2017`, production unfreeze запрещен, freeze должен оставаться включенным.

## 13. Цель этапа
1. Перевести контур из статуса governance-closeout в управляемое решение по боевому unfreeze.
2. Разделить техническую готовность и управленческое разрешение на боевой запуск.
3. Выполнить боевое включение только после формального GO и зафиксированных рисков.

## 13.1 Критерии снятия freeze (Policy Gate Criteria)
1. Контур имеет формальный closeout-статус `GO_FOR_CONTROLLED_UNFREEZE_CLOSEOUT_COMPLETE`.
2. Критерий `STOP_ON_SUCCESS` выполнен: 5 подряд окон PASS без фикса, freeze unchanged.
3. Последний acceptance-package и final decision-record опубликованы и доступны.
4. Последние обязательные проверки PASS:
1. profile coverage long/short,
2. search-grid coverage long/short,
3. `pip check`,
4. `text_guard`,
5. `readiness --show`.
5. Scope lock подтвержден:
1. только Optuna-контур,
2. `OptunaMlSignalBackend=off`,
3. без ML-combo/ML-signals.
6. План rollback готов и проверен документально.

## 13.2 Матрица согласования GO/NO-GO
1. Роли и зоны ответственности:
1. `Runtime Owner` - подтверждает техническую исполнимость runbook.
2. `Risk Owner` - подтверждает приемлемость residual risks.
3. `Release Owner` - выдает итоговый GO/NO-GO.
2. Правило решения:
1. GO только при `3/3` подтверждениях.
2. Любой NO => итоговое решение NO_GO.
3. Фиксация в decision-record обязательна:
1. кто согласовал,
2. время UTC,
3. версия документа,
4. перечень рисков и ограничений.

## 13.3 Decision-Record для production unfreeze
1. Обязательные поля:
1. `decision`: GO или NO_GO,
2. `scope_lock`: Optuna-only,
3. `freeze_before` и `freeze_after`,
4. `evidence_map` (ссылки на acceptance и проверки),
5. `residual_risks`,
6. `rollback_plan_ref`,
7. `approvals`,
8. `timestamp_utc`.
2. Формат: отдельный JSON-артефакт в `reports/qa_gate` + краткая запись в хронологии.

## 13.4 Исполняемый чеклист боевого включения
1. Шаг 13.4.1: выпустить final production decision-record (GO/NO_GO).
2. Шаг 13.4.2: при GO выполнить controlled production unfreeze по отдельному runbook.
3. Шаг 13.4.3: выполнить post-unfreeze проверки и зафиксировать итоговый статус.
4. Шаг 13.4.4: при деградации немедленно применить rollback и вернуть freeze.

## Текущий статус этапа 13
1. `13.1` DONE (критерии зафиксированы).
2. `13.2` DONE (матрица согласования зафиксирована).
3. `13.3` DONE (требования decision-record зафиксированы).
4. `13.4` EXECUTED (GO подтвержден, controlled production unfreeze выполнен, пост-проверки PASS, rollback не потребовался).

## Исполнение 13.4 (2026-06-01)
1. `13.4.1` FINAL GO decision-record: `reports/qa_gate/p1792_optuna_production_unfreeze_decision_record_final_20260601T120607Z.json`.
2. `13.4.2` Controlled production unfreeze execution: `reports/qa_gate/p1793_optuna_production_unfreeze_step13_4_2_20260601T120855Z.json`.
3. `13.4.3` Post-unfreeze verification PASS: `reports/qa_gate/p1794_optuna_production_unfreeze_step13_4_3_20260601T120855Z.json`.
4. `13.4.4` Rollback check: `PASS_NOT_REQUIRED` (деградация не обнаружена), `reports/qa_gate/p1795_optuna_production_unfreeze_step13_4_4_20260601T120855Z.json`.

## 14. Launch Recovery Plan (операционный режим после паузы P19xx)
1. Старт шагов: `ПУНКТ 1`.
2. Порядок выполнения:
1. Пауза повторяющегося gate-journal цикла (`P19xx`).
2. Тех-консилиум + фиксация актуальных блокеров запуска.
3. Hotfix launcher path:
1. рабочий `SearchWorkers`,
2. safer temporary-unlock recovery,
3. корректный fingerprint `configs/thresholds.yaml`.
4. Реальные прогоны short/long на закрытом окне (`train=T-2`, `test=T-1`).
5. Triage по критерию кандидата:
1. `goal_pass=true`,
2. `oos_net_return_pct>0`,
3. `oos_trades>0`.
6. Обязательный post-audit после triage.
7. Если кандидата нет: remediation-итерации (single-change) + повтор шагов 4-6.
8. Когда кандидат найден: forward-stability -> финальный quality decision package (`GO/NO-GO`).
3. Текущее состояние на `2026-06-01T16:26:03Z`:
1. Пункты `1-6` выполнены (`P1920`, `P1921`, `P1922`, `P1923`).
2. Пункт `7` активен.
3. Точка входа для следующего действия: `ПУНКТ 7`.
