# TZ: Optuna Launch Recovery V3 (2026-06-02)

Дата: 2026-06-02
База: завершенный `TZ Optuna Launch Recovery V2 (2026-06-01)` с финалом `NO_GO`
Контур: только `Optuna/APTuna` в `MLbotNav`
Ограничение: `ML runtime` не трогаем, `OptunaMlSignalBackend=off`

## 1. Стартовое состояние
1. V2 закрыт, финальный артефакт: `reports/qa_gate/p1997_optuna_launch_recovery_v2_final_quality_decision_no_go_20260601T190300Z.json`.
2. `project_ready=false`, `enforce_freeze=true`.
3. Цель V3: новый гипотезный набор (feature/logic), без микросдвигов сетки.

## 2. Что обязательно делаем
1. Сформировать новый пакет гипотез `logic/feature` (не grid drift).
2. Выполнить 2 пакетных прогона максимум (`Package A` и `Package B`) по 3 окнам.
3. После каждого пакета: один triage + один post-audit.
4. Финальный шаг: `GO` или `NO_GO` decision package.

## 3. Что не делаем
1. Бесконечные remediation-циклы на одном окне.
2. Post-audit после каждого микрошага.
3. Расширение scope за пределы Optuna/APTuna.

## 4. Шаги V3
1. Шаг 1: Checkpoint A V3 (окна, гипотезы, лимиты).
2. Шаг 2: Package A -> triage -> post-audit.
3. Шаг 3: Checkpoint B (кандидат/нет).
4. Шаг 4: Package B (последний) -> triage -> post-audit.
5. Шаг 5: Финальный decision package и закрытие V3.

## 5. Definition of Done
1. Выпущено итоговое решение (`GO`/`NO_GO`) с доказательными артефактами.
2. Цикл V3 закрыт без обхода hard-stop.

## 6. Checkpoint A V3 (fixed 2026-06-02T06:03:58Z)
1. Активный truth-source для launch:
   `reports/qa_gate/p2017_optuna_strict_exec_cycle2_final_quality_decision_no_go_20260602T000048Z.json`.
2. Окна Package A:
   1. `W1`: train=`2026-05-29`, test=`2026-05-30`
   2. `W2`: train=`2026-05-30`, test=`2026-05-31`
   3. `W3`: train=`2026-05-31`, test=`2026-06-01`
3. Состав Package A (только `feature/logic`, не grid drift):
   1. `A-H1`: `swing_structure_pair`
      long=`swing_hl_hh_long`, short=`swing_lh_ll_short`
   2. `A-H2`: `value_area_rotation_vs_breakout`
   3. `A-H3`: `fib_extension_targets`
4. Жесткие запреты в этом checkpoint:
   1. не переиспользовать старый кандидат из `p2013`,
   2. не делать `+0.01` / микро-grid drift,
   3. не открывать `Package B` до triage `Package A`,
   4. не делать micro-audit между гипотезными тиками.
5. Следующий исполняемый шаг:
   запуск `Package A long_only` по окнам `W1-W3`, затем `Package A short_only` по тем же окнам.
6. Артефакт checkpoint:
   `reports/qa_gate/p2021_optuna_launch_recovery_v3_checkpoint_a_20260602T060358Z.json`.

## 7. Progress Update (2026-06-02T06:52:50Z)
1. `Package A long_only` завершен:
   `reports/qa_gate/p2022_optuna_v3_package_a_long_only_summary_20260602T064116Z.json`
2. `Package A short_only` завершен:
   `reports/qa_gate/p2023_optuna_v3_package_a_short_only_summary_20260602T064841Z.json`
3. Unified `Package A triage` завершен:
   `reports/qa_gate/p2024_optuna_v3_package_a_unified_triage_20260602T065019Z.json`
4. `Package A post-audit` завершен:
   `reports/qa_gate/p2025_optuna_v3_package_a_post_audit_20260602T065250Z.json`
5. Текущий результат по `Package A`:
   `NO_CANDIDATE`
6. Следующий шаг по V3:
   определить точный slot-состав `Package B`, затем выполнить последний пакетный прогон.

## 8. Catalog Scope Update (2026-06-02T08:35:09Z)
1. Пользователь уточнил, что отсутствие launch-кандидата не завершает работу Optuna-калибровки.
2. Активная рамка расширена:
   1. пройти блоки, фичи и гипотезы по диапазонам `min -> max`,
   2. фиксировать плюсовые, минусовые, нейтральные/no-trade и infra-fail результаты,
   3. хранить параметры каждой калибровки как каталог знаний,
   4. отдельно выделять `top` результаты для дальнейшего выбора гипотез.
3. Новый активный catalog-TZ:
   `docs/TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md`
4. Checkpoint artifact:
   `reports/qa_gate/p2026_optuna_full_calibration_catalog_checkpoint_20260602T083509Z.json`
5. Важная граница:
   плюсовой результат в каталоге является `candidate_for_forward`, но не production-ready до `F1/F2 = 2/2 PASS` и нового production decision package.

## 9. Pointer Recovery (2026-06-02T12:37:36Z)
1. Пользователь указал, что предыдущий ТЗ был перепрыгнут по шагам.
2. Восстановленный незакрытый пункт V3:
   после `Package A NO_CANDIDATE` определить точный slot-состав `Package B`, затем выполнить bounded `Package B`.
3. Catalog overlay не отменяет этот пункт; он добавляет сохранение результатов как catalog knowledge.
4. `P2079` остается сохраненным `candidate_for_forward`, но не текущим ручным шагом и не production-ready.
5. Heartbeat `p2079-f1-data-gate-check` поставлен на паузу.
6. Checkpoint:
   `reports/qa_gate/p2137_previous_tz_recovery_package_b_pointer_20260602T123736Z.json`.
7. Текущий ручной шаг:
   зафиксировать exact V3 `Package B` slots/catalog command set до любого runtime.

## 10. Timed Package B Chain (2026-06-02T12:45:20Z)
1. Локальное время фиксации:
   `2026-06-02 17:45:20 +05:00`.
2. Откуда идем по этому ТЗ:
   section 7 `Progress Update (2026-06-02T06:52:50Z)`, где `Package A = NO_CANDIDATE` и следующий шаг V3 - определить точный slot-состав `Package B`.
3. Checkpoint chain:
   `reports/qa_gate/p2139_package_b_timed_step_chain_20260602T124520Z.json`.
4. Правило движения:
   каждый шаг получает date/time start, date/time complete, status, artifact и next step до перехода дальше.
5. Текущий шаг:
   Step 1 started UTC `2026-06-02T12:45:20Z` / local `2026-06-02 17:45:20 +05:00` - inventory V3 Package A and old Package B artifacts.

## 11. P2140 Package B Inventory (2026-06-02T12:59:00Z)
1. Локальное время закрытия:
   `2026-06-02 17:59:00 +05:00`.
2. Artifact:
   `reports/qa_gate/p2140_v3_package_b_inventory_20260602T125900Z.json`.
3. Status:
   `PASS`.
4. Вывод:
   текущий V3 Package A закрыт как `NO_CANDIDATE`; старые Package B артефакты `P1995/P1996` и `P2005-P2007` являются historical V2/strict references only.
5. Текущий V3 Package B:
   exact slots not defined, matrices not found, command set not defined, runtime not allowed.
6. Следующий номер:
   `P2141` - exact V3 Package B slot definition.

## 12. P2141 Exact V3 Package B Slots (2026-06-02T13:00:00Z)
1. Локальное время закрытия:
   `2026-06-02 18:00:00 +05:00`.
2. Artifact:
   `reports/qa_gate/p2141_v3_package_b_exact_slots_20260602T130000Z.json`.
3. Status:
   `PASS`.
4. Slots:
   1. `B-H1`: `ema_stack_bull` long, `ema_cross_20_200` short.
   2. `B-H2`: `min_max_range_revert` long/short.
   3. `B-H3`: `spread_pressure_and_delta_absorption` long/short.
5. Windows:
   W1 `2026-05-29 -> 2026-05-30`, W2 `2026-05-30 -> 2026-05-31`, W3 `2026-05-31 -> 2026-06-01`.
6. Следующий номер:
   `P2142` - matrix slices and command-set/dry-run only.

## 13. P2142 Package B Matrix Slices And Command Set (2026-06-02T13:05:59Z)
1. Локальное время закрытия:
   `2026-06-02 18:05:59 +05:00`.
2. Artifact:
   `reports/qa_gate/p2142_v3_package_b_command_set_20260602T130559Z.json`.
3. Status:
   `PASS`.
4. Matrix slices:
   1. `configs/calibration_matrices/optuna_v3_package_b_bh1_long.yaml`
   2. `configs/calibration_matrices/optuna_v3_package_b_bh1_short.yaml`
   3. `configs/calibration_matrices/optuna_v3_package_b_bh2.yaml`
   4. `configs/calibration_matrices/optuna_v3_package_b_bh3.yaml`
5. Command set:
   18 exact commands emitted for B-H1/B-H2/B-H3 across W1-W3 and long/short modes.
6. Dry-run/preflight:
   `18/18 PASS`; runtime was not launched in this step.
7. Следующий номер:
   `P2143` - Package B `long_only` runtime only. `short_only`, P2079 forward, production, and unfreeze remain blocked.

## 14. P2143 Package B Long Only Runtime (2026-06-02T13:15:35Z)
1. Локальное время закрытия:
   `2026-06-02 18:15:35 +05:00`.
2. Runtime artifact:
   `reports/qa_gate/p2143_v3_package_b_long_only_summary_20260602T131035Z.json`.
3. Catalog artifact:
   `reports/optuna_catalog/neutral/p2143_v3_package_b_long_only_neutral_20260602T131535Z.json`.
4. Status:
   runtime `PASS`, 9/9 external commands completed.
5. Catalog result:
   class `neutral`, accepted positive candidates `0`, best tradeful OOS `-1.6687%`.
6. Следующий номер:
   `P2144` - Package B `short_only` runtime only. P2079 forward, production, and unfreeze remain blocked.

## 15. P2144 Package B Short Only Runtime (2026-06-02T13:24:20Z)
1. Локальное время закрытия:
   `2026-06-02 18:24:20 +05:00`.
2. Runtime artifact:
   `reports/qa_gate/p2144_v3_package_b_short_only_summary_20260602T132020Z.json`.
3. Catalog artifact:
   `reports/optuna_catalog/neutral/p2144_v3_package_b_short_only_neutral_20260602T132420Z.json`.
4. Status:
   runtime `PASS`, 9/9 external commands completed.
5. Catalog result:
   class `neutral`, accepted positive candidates `0`, best tradeful OOS `-1.6689%`.
6. Следующий номер:
   `P2145` - unified Package B triage only. P2079 forward, production, and unfreeze remain blocked.

## 16. P2145 Package B Unified Triage (2026-06-02T13:28:30Z)
1. Локальное время закрытия:
   `2026-06-02 18:28:30 +05:00`.
2. Artifact:
   `reports/qa_gate/p2145_v3_package_b_unified_triage_20260602T132830Z.json`.
3. Status:
   `NO_CANDIDATE`.
4. Package B totals:
   positive `0`, neutral `18`, negative `0`, infra_fail `0`, candidate_for_forward `0`.
5. Следующий номер:
   `P2146` - Package B post-sync audit/docs sync only. P2079 forward, production, and unfreeze remain blocked.

## 17. P2146 Package B Post-Sync Audit (2026-06-02T13:30:21Z)
1. Локальное время закрытия:
   `2026-06-02 18:30:21 +05:00`.
2. Artifact:
   `reports/qa_gate/p2146_v3_package_b_post_sync_audit_20260602T133021Z.json`.
3. Status:
   `PASS`.
4. Checks:
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2145 artifact parse `PASS`.
5. Следующий номер:
   `P2147` - transition decision after Package B closeout. P2079 forward, production, and unfreeze remain blocked.

## 18. P2147 Package B Closeout Transition (2026-06-02T13:33:30Z)
1. Локальное время закрытия:
   `2026-06-02 18:33:30 +05:00`.
2. Artifact:
   `reports/qa_gate/p2147_v3_package_b_closeout_transition_20260602T133330Z.json`.
3. Status:
   `PASS`.
4. Decision:
   `GO_TO_FINAL_V3_NO_GO_DECISION_PACKAGE`.
5. Boundary:
   Package B runtime is complete; Package A and Package B both closed with no accepted candidate. P2079 forward, production, and unfreeze remain blocked.

## 19. P2148 Final V3 NO_GO Decision (2026-06-02T13:36:00Z)
1. Локальное время закрытия:
   `2026-06-02 18:36:00 +05:00`.
2. Artifact:
   `reports/qa_gate/p2148_v3_final_no_go_decision_20260602T133600Z.json`.
3. Final launch decision:
   `NO_GO`.
4. Reason:
   bounded V3 Package A and Package B both closed without an accepted candidate.
5. Boundary:
   production-ready candidate absent; launch and unfreeze are blocked. Next number is `P2149` final post-sync audit.

## 20. P2149 Final V3 NO_GO Post-Sync Audit (2026-06-02T13:38:45Z)
1. Локальное время закрытия:
   `2026-06-02 18:38:45 +05:00`.
2. Artifact:
   `reports/qa_gate/p2149_v3_final_no_go_post_sync_audit_20260602T133845Z.json`.
3. Status:
   `PASS`.
4. Checks:
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2148 artifact parse `PASS`.
5. Final:
   V3 chain closed as `NO_GO`; runtime, forward, production, and unfreeze are blocked from this chain.
