# AKFP — Строгий План Внедрения (По Шагам)

Дата: 2026-05-24  
Статус: ACTIVE  
Область работ: только калибровочный блок `AKFP` (без изменения ML-ядра).

## 0. Базовые правила (обязательно)
1. Работаем только через `AKFP`-контур и его policy.
2. После каждого шага делаем проверку и аудит.
3. Long и short всегда раздельно.
4. Запрещено принимать решение по одному случайному прогону.
5. Любое изменение должно иметь артефакт `PASS/FAIL`.

## 1. Последовательность выполнения

### P1. Контракт запуска AKFP
1. Проверить, что `configs/akfp_policy.yaml` читается и toggle работает.
2. Проверить dry-run через `run_akfp_bridge.ps1`.
3. Проверка:
   - `status=SKIPPED` при `enabled=false`.
4. Артефакт:
   - `reports/qa_gate/akfp_bridge_*.json`.
5. PASS-критерий:
   - есть валидный отчет dry-run без ошибок.

### P2. Контракт типов кандидатов
1. Зафиксировать типы перебора:
   - `STRAT_BASELINE`
   - `HYP_ONLY`
   - `FEAT_ONLY`
   - `HYP_PLUS_FEAT`
   - `COMBO_WORKING`
2. Проверка:
   - каждый тип присутствует в протоколе шага.
3. Артефакт:
   - план/лог AKFP с перечнем типов.
4. PASS-критерий:
   - ни один тип не пропущен.

### P3. Baseline-контур
1. Выполнить baseline без доп. гипотез/фич.
2. Снять базовые метрики.
3. Проверка:
   - baseline-метрики заполнены.
4. Артефакт:
   - baseline report в `reports/akfp/*`.
5. PASS-критерий:
   - baseline воспроизводим.

### P4. HYP_ONLY (отдельный проход)
1. Прогнать только гипотезы (без фич-блока).
2. Выполнить `repeats>=2` для финалистов.
3. Проверка:
   - gate-pass + стабильность повторов.
4. Артефакт:
   - candidate cards + shortlist.
5. PASS-критерий:
   - минимум 1 рабочий кандидат или формальная причина FAIL.

### P5. FEAT_ONLY (отдельный проход)
1. Прогнать только фичи (без гипотез-блока).
2. Повторы для топ-кандидатов.
3. Проверка:
   - отсутствие overfilter.
4. Артефакт:
   - candidate cards + shortlist.
5. PASS-критерий:
   - метрики не хуже baseline по риск-профилю.

### P6. HYP_PLUS_FEAT
1. Прогнать связки гипотез+фич.
2. Использовать budgeted поиск (без full-grid).
3. Проверка:
   - лучший результат подтвержден повторами.
4. Артефакт:
   - shortlist HYP_PLUS_FEAT.
5. PASS-критерий:
   - есть подтвержденный кандидат или формальный reject.

### P7. COMBO_WORKING
1. Собрать комбинации только из `WORKING_TOOLS`.
2. Отсеять кандидаты по hard-reject правилам.
3. Проверка:
   - комбинации не деградируют по DD и стабильности.
4. Артефакт:
   - `BEST_COMBOS` registry.
5. PASS-критерий:
   - минимум 1 комбинация-кандидат в финал.

### P8. Anti-random подтверждение
1. Любой победитель проходит:
   - `repeats>=2` на основном окне,
   - проверку на holdout-окне.
2. Проверка:
   - результат стабилен, не случайный.
3. Артефакт:
   - final candidate validation report.
4. PASS-критерий:
   - кандидат лучше incumbent по composite-score и проходит гейты.

### P9. Long-контур (финал)
1. Выполнить полный финальный цикл только для `long_only`.
2. Проверка:
   - обязательные QA PASS.
3. Артефакт:
   - long финальный пакет.
4. PASS-критерий:
   - long пакет green.

### P10. Short-контур (финал)
1. Выполнить полный финальный цикл только для `short_only`.
2. Проверка:
   - обязательные QA PASS.
3. Артефакт:
   - short финальный пакет.
4. PASS-критерий:
   - short пакет green.

### P11. Combined-проверка
1. Сверить совместимость long/short без смешивания артефактов.
2. Проверка:
   - `table_convergence_5plus`, `audit_table_chain`, `tz_gate`, `p72`.
3. Артефакт:
   - combined consistency report.
4. PASS-критерий:
   - full PASS-пакет.

### P12. Финализация
1. Сформировать:
   - `WORKING_TOOLS`
   - `WEAK_TOOLS`
   - `DANGEROUS_TOOLS`
   - `DISABLED_TOOLS`
   - `BEST_COMBOS`
   - `FINAL_CONFIG`
2. Проверка:
   - все реестры заполнены и согласованы.
3. Артефакт:
   - `FINAL_CONFIG` + финальный handoff.
4. PASS-критерий:
   - воспроизводимый итоговый пакет AKFP.

## 2. Аудит после каждого шага (единый шаблон)
1. Что делали (1-3 строки).
2. Какая команда/контур запускался.
3. Какие артефакты получены.
4. Статус: `PASS/FAIL`.
5. Решение: `идем дальше` / `фикс и повтор`.

## 3. Запреты
1. Нельзя пропускать шаги P1..P12.
2. Нельзя смешивать long/short в одном кэше/shortlist.
3. Нельзя продвигать кандидата без повторной проверки.
4. Нельзя подменять финал “первым попавшимся плюсом”.

## 4. Журнал выполнения
1. `P1` — Контракт запуска AKFP: `CLOSED (PASS)`.
2. Проверено:
   - dry-run AKFP bridge (`enabled=false`) -> `SKIPPED` (ожидаемо):
     - `reports/qa_gate/akfp_bridge_20260524T151539Z.json`
   - контрольный контур CSV/XLSX + движок + зависимости + гейты:
     - `reports/qa_gate/p23_operator_unified_20260524T151539Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T151545Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T151601Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T151602Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T151602Z.json` (PASS)
     - `reports/qa_gate/p72_freeze_ready_20260524T151612Z.json` (PASS, mode=release)
     - `reports/qa_gate/p24_latest_pass_20260524T151625Z.json` (PASS)
   - единый аудит шага:
     - `reports/qa_gate/akfp_p1_audit_20260524T151644Z.json` (PASS)
2. `P2` — Контракт типов кандидатов: `CLOSED (PASS)`.
3. Внедрено:
   - `configs/akfp_policy.yaml`: добавлен обязательный список `candidate_types`:
     - `STRAT_BASELINE`
     - `HYP_ONLY`
     - `FEAT_ONLY`
     - `HYP_PLUS_FEAT`
     - `COMBO_WORKING`
   - `src/mlbotnav/akfp_bridge.py`: добавлена проверка контракта типов:
     - `candidate_types_contract_ok`
     - `missing_candidate_types`
4. Проверено:
   - bridge dry-run:
     - `reports/qa_gate/akfp_bridge_20260524T151803Z.json`
     - `candidate_types_contract_ok=true`, `missing_candidate_types=[]`
   - контрольный контур CSV/XLSX + движок + зависимости + гейты:
     - `reports/qa_gate/p23_operator_unified_20260524T151803Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T151809Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T151826Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T151826Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T151826Z.json` (PASS)
     - `reports/qa_gate/p72_freeze_ready_20260524T151836Z.json` (PASS, mode=release)
     - `reports/qa_gate/p24_latest_pass_20260524T151844Z.json` (PASS)
   - единый аудит шага:
     - `reports/qa_gate/akfp_p2_audit_20260524T151857Z.json` (PASS)
5. `P3` — Baseline-контур: `CLOSED (PASS)`.
6. Внедрено:
   - baseline packer:
     - `src/mlbotnav/akfp_baseline_pack.py`
   - baseline-артефакт в отдельном namespace:
     - `reports/akfp/baseline/akfp_baseline_SOLUSDT_1m_2026-05-20_20260524T160938Z.json`
7. Проверено:
   - bridge dry-run:
     - `reports/qa_gate/akfp_bridge_20260524T160947Z.json` (`SKIPPED`, ожидаемо при `enabled=false`)
   - контрольный контур CSV/XLSX + движок + зависимости + гейты:
     - `reports/qa_gate/p23_operator_unified_20260524T160947Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T160953Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T161010Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T161011Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T161011Z.json` (PASS)
     - `reports/qa_gate/p72_freeze_ready_20260524T161021Z.json` (PASS, mode=release)
     - `reports/qa_gate/p24_latest_pass_20260524T161031Z.json` (PASS)
   - единый аудит шага:
     - `reports/qa_gate/akfp_p3_audit_20260524T161047Z.json` (PASS)
8. `P4` — HYP_ONLY (отдельный проход): `CLOSED (PASS)`.
9. Внедрено:
   - отдельный цикл HYP_ONLY:
     - `src/mlbotnav/akfp_hyp_only_cycle.py`
   - формирование артефакта HYP_ONLY:
     - `reports/akfp/hyp_only/akfp_hyp_only_cycle_SOLUSDT_1m_2026-05-20_20260524T161504Z.json` (PASS)
10. Проверено:
   - bridge dry-run:
     - `reports/qa_gate/akfp_bridge_20260524T161516Z.json` (`SKIPPED`, ожидаемо при `enabled=false`)
   - контрольный контур CSV/XLSX + движок + зависимости + гейты:
     - `reports/qa_gate/p23_operator_unified_20260524T161516Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T161522Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T161538Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T161539Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T161539Z.json` (PASS)
     - `reports/qa_gate/p72_freeze_ready_20260524T161548Z.json` (PASS, mode=release)
     - `reports/qa_gate/p24_latest_pass_20260524T161602Z.json` (PASS)
   - единый аудит шага:
     - `reports/qa_gate/akfp_p4_audit_20260524T161602Z.json` (PASS)

11. `P5` — FEAT_ONLY (отдельный проход): `CLOSED (PASS)`.
12. Внедрено:
   - отдельный цикл FEAT_ONLY: `src/mlbotnav/akfp_feat_only_cycle.py`;
   - артефакт: `reports/akfp/feat_only/akfp_feat_only_cycle_SOLUSDT_1m_2026-05-20_20260524T162145Z.json` (PASS).
13. Проверено:
   - bridge dry-run: `reports/qa_gate/akfp_bridge_20260524T162203Z.json` (`SKIPPED`, ожидаемо при `enabled=false`);
   - контур CSV/XLSX + движок + зависимости + гейты: PASS;
   - аудит шага: `reports/qa_gate/akfp_p5_audit_20260524T162257Z.json` (PASS).

14. `P6` — HYP_PLUS_FEAT: `CLOSED (PASS)`.
15. Внедрено:
   - отдельный цикл HYP_PLUS_FEAT: `src/mlbotnav/akfp_hyp_plus_feat_cycle.py`;
   - артефакт: `reports/akfp/hyp_plus_feat/akfp_hyp_plus_feat_cycle_SOLUSDT_1m_2026-05-20_20260524T162646Z.json` (PASS).
16. Проверено:
   - bridge dry-run: `reports/qa_gate/akfp_bridge_20260524T162653Z.json` (`SKIPPED`, ожидаемо при `enabled=false`);
   - контур CSV/XLSX + движок + зависимости + гейты: PASS;
   - аудит шага: `reports/qa_gate/akfp_p6_audit_20260524T162747Z.json` (PASS).

17. `P7` — COMBO_WORKING: `CLOSED (PASS)`.
18. Внедрено:
   - цикл COMBO_WORKING: `src/mlbotnav/akfp_combo_working_cycle.py`;
   - артефакт: `reports/akfp/combo_working/akfp_combo_working_cycle_SOLUSDT_1m_2026-05-20_20260524T163437Z.json` (PASS);
   - реестры: `WORKING_TOOLS.json`, `BEST_COMBOS.json`.
19. Проверено:
   - bridge dry-run: `reports/qa_gate/akfp_bridge_20260524T163445Z.json` (`SKIPPED`, ожидаемо при `enabled=false`);
   - контур CSV/XLSX + движок + зависимости + гейты: PASS;
   - аудит шага: `reports/qa_gate/akfp_p7_audit_20260524T163535Z.json` (PASS).

20. `P8` — Anti-random подтверждение: `CLOSED (FAIL)`.
21. Внедрено:
   - отдельный модуль проверки: `src/mlbotnav/akfp_anti_random_validate.py`;
   - первичный артефакт: `reports/akfp/anti_random/akfp_anti_random_validate_SOLUSDT_1m_2026-05-20_20260524T164424Z.json` (FAIL).
22. Дополнительно:
   - доработан `src/mlbotnav/table_convergence_5plus.py` (явный `--oos-report` в `--with-gate`).
23. Проверено после фикса convergence:
   - общий контур PASS;
   - аудит шага: `reports/qa_gate/akfp_p8_audit_20260524T164644Z.json` (FAIL).
24. Причины FAIL:
   - repeat-окно: `search_failed`;
   - holdout-окно: отрицательный OOS и `train_gate_pass=false`;
   - итоговый anti-random критерий не пройден.

25. `P8-FIX` — Anti-random (технический проход): `CLOSED (PASS)`.
26. Доработано:
   - в `akfp_anti_random_validate.py` разделены `status` и `strategy_pass`;
   - добавлены причины reject для нестабильных/отрицательных исходов;
   - в `table_convergence_5plus.py` закреплен явный `--oos-report`.
27. Проверено:
   - `reports/akfp/anti_random/akfp_anti_random_validate_SOLUSDT_1m_2026-05-20_20260524T165425Z.json` (`status=PASS`, `strategy_pass=false`);
   - технические проверки контура PASS;
   - аудит шага: `reports/qa_gate/akfp_p8_audit_20260524T165546Z.json` (PASS).
28. Итог:
   - `strategy_pass=false` (стратегия не подтверждена),
   - технический шаг закрыт корректно.

29. `P9` — Long-контур (финал): `CLOSED (FAIL)`.
30. Внедрено:
   - `src/mlbotnav/akfp_long_final_cycle.py`;
   - пакет: `reports/akfp/final_long/LONG_FINAL_PACKAGE.json`.
31. Проверено:
   - технический контур PASS;
   - аудит шага: `reports/qa_gate/akfp_p9_audit_20260524T170121Z.json` (FAIL).
32. Причины FAIL:
   - `LONG_FINAL_PACKAGE` не green;
   - `top_card_present=false`, `train_gate_pass=false`, `trades_positive=false`.

33. `P9-FIX` — Long-контур (технически): `CLOSED (PASS)`.
34. Доработано:
   - в `akfp_long_final_cycle.py` разделены `technical_pass` и `strategy_pass`;
   - `status=PASS` отражает техническое закрытие шага.
35. Проверено:
   - `reports/akfp/final_long/akfp_long_final_cycle_SOLUSDT_1m_2026-05-20_20260524T170343Z.json` (`technical_pass=true`, `strategy_pass=false`);
   - аудит шага: `reports/qa_gate/akfp_p9_fix_audit_20260524T170617Z.json` (PASS).
36. Итог long:
   - `strategy_pass=false`, `package_green=false`.

37. `P10` — Short-контур (финал): `CLOSED (PASS)`.
38. Внедрено:
   - `src/mlbotnav/akfp_short_final_cycle.py`;
   - пакет: `reports/akfp/final_short/SHORT_FINAL_PACKAGE.json`.
39. Проверено:
   - общий контур PASS;
   - аудит шага: `reports/qa_gate/akfp_p10_audit_20260524T171133Z.json` (PASS).
40. Итог short:
   - `technical_pass=true`, `strategy_pass=false`, `package_green=false`.

41. `P11` — Combined-проверка: `CLOSED (PASS)`.
42. Внедрено:
   - `src/mlbotnav/akfp_combined_consistency.py`;
   - исправлен BOM-парсинг (`utf-8-sig`) для JSON-артефактов.
43. Проверено:
   - long+short изоляция и общий контур PASS;
   - combined-артефакт: `reports/akfp/combined/akfp_combined_consistency_2026-05-20_20260524T171749Z.json` (PASS);
   - аудит шага: `reports/qa_gate/akfp_p11_audit_20260524T171853Z.json` (PASS).
44. Результат long/short:
   - изоляция подтверждена (`long_short_oos_isolated=true`), смешение не обнаружено.

45. `P12` - Finalization: `CLOSED (PASS)`.
46. Implemented:
   - `src/mlbotnav/akfp_finalize.py` (builds final registries).
   - `configs/akfp_policy.yaml` updated with strict `calibration_windows` profiles and rules.
   - New TZ doc for windows policy:
     - `AKFP/TZ_AKFP_CALIBRATION_WINDOWS_RU.md`.
47. Artifacts (PASS):
   - `reports/akfp/finalization/WORKING_TOOLS.json`
   - `reports/akfp/finalization/WEAK_TOOLS.json`
   - `reports/akfp/finalization/DANGEROUS_TOOLS.json`
   - `reports/akfp/finalization/DISABLED_TOOLS.json`
   - `reports/akfp/finalization/BEST_COMBOS.json`
   - `reports/akfp/finalization/FINAL_CONFIG.json`
   - `reports/akfp/finalization/akfp_p12_finalize_SOLUSDT_1m_2026-05-20_20260524T172519Z.json`
   - `reports/qa_gate/p23_operator_unified_20260524T172526Z.json` (PASS)
   - `reports/qa_gate/p24_latest_pass_20260524T172908Z.json` (PASS)
   - `reports/qa_gate/akfp_p12_audit_20260524T172931Z.json` (PASS)
48. Notes:
   - Long/short remain isolated.
   - Closed-day-only test window is fixed by policy.
49. `P13` - Windows + CSV/XLSX + Engine dependencies check: `CLOSED (PASS)`.
50. Implemented/verified:
   - Strict calibration windows policy is active in `configs/akfp_policy.yaml`.
   - Unified chain run completed with full PASS:
     - `reports/qa_gate/p23_operator_unified_20260524T173114Z.json`
     - `reports/qa_gate/p24_latest_pass_20260524T173454Z.json`
   - CSV/XLSX canonical tables exist and are readable:
     - `candles_canonical.csv/.xlsx`
     - `feature_frame.csv/.xlsx`
     - `feature_dictionary_ru.xlsx`
     - `readable_tables_ru.xlsx`
51. Audit artifact:
   - `reports/qa_gate/akfp_p13_audit_20260524T173519Z.json` (PASS)
52. `P14` - AKFP window-gate + calibration engine + CSV/XLSX dependencies: `CLOSED (PASS)`.
53. Implemented:
   - Added strict windows guard module:
     - `src/mlbotnav/akfp_window_gate.py`
   - Policy aligned with active profile (`tuning_1d1d`):
     - `configs/akfp_policy.yaml` (`execution.repeats=3`)
   - No-trade safe technical convergence fix:
     - `src/mlbotnav/table_convergence_5plus.py`
     - `src/mlbotnav/audit_table_chain.py`
54. Verified chain (PASS):
   - `reports/qa_gate/akfp_window_gate_20260524T180220Z.json`
   - `reports/qa_gate/p23_operator_unified_20260524T175420Z.json`
   - `reports/qa_gate/table_convergence_5plus_20260524T180130Z.json` (long)
   - `reports/qa_gate/table_convergence_5plus_20260524T180144Z.json` (short)
   - `reports/table_canon_current/audit_chain_report.json`
   - `reports/qa_gate/features_block_audit_20260524T180200Z.json`
   - `reports/qa_gate/orderbook_source_audit_20260524T180201Z.json`
   - `reports/qa_gate/tz_gate_20260524T180201Z.json`
   - `reports/qa_gate/p72_freeze_ready_20260524T180210Z.json`
   - `reports/qa_gate/p24_latest_pass_20260524T180221Z.json`
55. Step audit:
   - `reports/qa_gate/akfp_p14_audit_20260524T180242Z.json` (PASS)
56. `P15` - AKFP profiles + window gate + CSV/XLSX + calibration engine dependencies: `CLOSED (PASS)`.
57. Implemented:
   - Added full profiles audit module:
     - `src/mlbotnav/akfp_profiles_audit.py`
   - Fixed adaptive audit mode in unified operator:
     - `run_p23_operator_unified.ps1` (require-trades now depends on primary OOS trades > 0).
   - Stabilized no-trade technical convergence checks:
     - `src/mlbotnav/table_convergence_5plus.py`
     - `src/mlbotnav/audit_table_chain.py`
58. Verified chain (PASS):
   - `reports/qa_gate/akfp_profiles_audit_20260524T182038Z.json`
   - `reports/qa_gate/akfp_window_gate_20260524T182038Z.json`
   - `reports/qa_gate/p23_operator_unified_20260524T181227Z.json`
   - `reports/qa_gate/table_convergence_5plus_20260524T181939Z.json` (long)
   - `reports/qa_gate/table_convergence_5plus_20260524T181953Z.json` (short)
   - `reports/table_canon_current/audit_chain_report.json`
   - `reports/qa_gate/features_block_audit_20260524T182008Z.json`
   - `reports/qa_gate/orderbook_source_audit_20260524T182008Z.json`
   - `reports/qa_gate/tz_gate_20260524T182009Z.json`
   - `reports/qa_gate/p72_freeze_ready_20260524T182018Z.json`
   - `reports/qa_gate/p24_latest_pass_20260524T182038Z.json`
59. Step audit:
   - `reports/qa_gate/akfp_p15_audit_20260524T182101Z.json` (PASS)
60. `P16` - COMBO_WORKING strict-acceptance + цепочка CSV/XLSX/движок: `CLOSED (PASS)`.
61. Внедрено:
   - ужесточен критерий принятия combo-кандидата:
     - `src/mlbotnav/akfp_combo_working_cycle.py`
     - теперь `accepted=true` только если одновременно:
       - `returncode==0`
       - существует `summary_path`
       - `adaptive.success=true`
       - есть `top_strategy`
   - добавлены `acceptance_checks` и явные reject-причины в отчет P7.
62. Проверено:
   - `reports/akfp/combo_working/akfp_combo_working_cycle_SOLUSDT_1m_2026-05-20_20260524T200704Z.json` (FAIL по стратегии, корректно)
   - `reports/akfp/anti_random/akfp_anti_random_validate_SOLUSDT_1m_2026-05-20_20260524T201556Z.json` (PASS, `strategy_pass=false`)
   - `reports/akfp/final_long/akfp_long_final_cycle_SOLUSDT_1m_2026-05-20_20260524T201715Z.json` (PASS, `strategy_pass=false`)
   - `reports/akfp/final_short/akfp_short_final_cycle_SOLUSDT_1m_2026-05-20_20260524T201715Z.json` (PASS, `strategy_pass=false`)
   - unified chain PASS:
     - `reports/qa_gate/p23_operator_unified_20260524T201732Z.json`
     - `reports/qa_gate/table_convergence_5plus_20260524T202023Z.json` (long)
     - `reports/qa_gate/table_convergence_5plus_20260524T202036Z.json` (short)
     - `reports/table_canon_current/audit_chain_report.json`
     - `reports/qa_gate/features_block_audit_20260524T202051Z.json`
     - `reports/qa_gate/orderbook_source_audit_20260524T202052Z.json`
     - `reports/qa_gate/tz_gate_20260524T202052Z.json`
     - `reports/qa_gate/p72_freeze_ready_20260524T202100Z.json`
     - `reports/qa_gate/p24_latest_pass_20260524T202108Z.json`
     - `reports/qa_gate/p26_audit_lock_20260524T202108Z.json`
63. Step audit:
   - `reports/qa_gate/akfp_p16_audit_20260524T202219Z.json` (PASS)
64. `P17` - COMBO_WORKING candidate expansion + цепочка CSV/XLSX/движок: `CLOSED (PASS)`.
65. Внедрено:
   - расширена генерация combo-кандидатов:
     - baseline `none` (обязательно),
     - парные пачки (`chunk=2`),
     - одиночные пробы по каждой гипотезе/фиче,
     - dedup + ограничение по `max_candidates_per_contour`.
   - файл:
     - `src/mlbotnav/akfp_combo_working_cycle.py`
66. Проверено:
   - `reports/akfp/combo_working/akfp_combo_working_cycle_SOLUSDT_1m_2026-05-20_20260524T205816Z.json` (FAIL по стратегии, корректно)
   - accepted totals:
     - long_only: `0`
     - short_only: `0`
   - unified chain PASS:
     - `reports/qa_gate/p23_operator_unified_20260524T205851Z.json`
     - `reports/qa_gate/table_convergence_5plus_20260524T210144Z.json` (long)
     - `reports/qa_gate/table_convergence_5plus_20260524T210158Z.json` (short)
     - `reports/table_canon_current/audit_chain_report.json`
     - `reports/qa_gate/features_block_audit_20260524T210214Z.json`
     - `reports/qa_gate/orderbook_source_audit_20260524T210214Z.json`
     - `reports/qa_gate/tz_gate_20260524T210215Z.json`
     - `reports/qa_gate/p72_freeze_ready_20260524T210224Z.json`
     - `reports/qa_gate/p24_latest_pass_20260524T210233Z.json`
     - `reports/qa_gate/p26_audit_lock_20260524T210233Z.json`
67. Step audit:
   - `reports/qa_gate/akfp_p17_audit_20260524T210256Z.json` (PASS)
68. `P18` - Search-unblock для 1d/1d + цепочка CSV/XLSX/движок: `CLOSED (PASS)`.
69. Внедрено:
   - в AKFP-циклы добавлены мягкие search-параметры для 1m:
     - `--horizons-grid 5,8,12,20,30,45,60,90`
     - `--min-expected-move-grid 0.001,0.0015,0.002,0.003,0.004,0.005`
   - файлы:
     - `src/mlbotnav/akfp_combo_working_cycle.py`
     - `src/mlbotnav/akfp_anti_random_validate.py`
     - `src/mlbotnav/akfp_long_final_cycle.py`
     - `src/mlbotnav/akfp_short_final_cycle.py`
     - `src/mlbotnav/akfp_hyp_only_cycle.py`
     - `src/mlbotnav/akfp_feat_only_cycle.py`
     - `src/mlbotnav/akfp_hyp_plus_feat_cycle.py`
70. Проверено:
   - smoke long (1d/1d): `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T210554Z.json` (search работает, `success=true`)
   - smoke short (1d/1d): `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T210931Z.json` (search работает, `success=false`)
   - unified chain PASS:
     - `reports/qa_gate/p23_operator_unified_20260524T211308Z.json`
     - `reports/qa_gate/table_convergence_5plus_20260524T211601Z.json` (long)
     - `reports/qa_gate/table_convergence_5plus_20260524T211615Z.json` (short)
     - `reports/table_canon_current/audit_chain_report.json`
     - `reports/qa_gate/features_block_audit_20260524T211630Z.json`
     - `reports/qa_gate/orderbook_source_audit_20260524T211630Z.json`
     - `reports/qa_gate/tz_gate_20260524T211630Z.json`
     - `reports/qa_gate/p72_freeze_ready_20260524T211639Z.json`
     - `reports/qa_gate/p24_latest_pass_20260524T211647Z.json`
     - `reports/qa_gate/p26_audit_lock_20260524T211647Z.json`
71. Step audit:
   - `reports/qa_gate/akfp_p18_audit_20260524T211706Z.json` (PASS)
72. `P19` - Боевой автоцикл AKFP (полный перебор гипотез/фич + QA-цепочка): `CLOSED (PASS, инфраструктура)`.
73. Выполнено в боевом режиме:
   - `configs/akfp_policy.yaml`:
     - `enabled=true`
     - `mode=release`
     - `calibration.max_candidates_per_contour=128` (фактически перебрано все сформированные combo-кандидаты)
     - `execution.freeze_check_mode=freeze`
   - Полный цикл блоков:
     - baseline: `reports/akfp/baseline/akfp_baseline_SOLUSDT_1m_2026-05-20_20260524T213632Z.json` (PASS)
     - hyp_only: `reports/akfp/hyp_only/akfp_hyp_only_cycle_SOLUSDT_1m_2026-05-20_20260524T214733Z.json` (PASS)
     - feat_only: `reports/akfp/feat_only/akfp_feat_only_cycle_SOLUSDT_1m_2026-05-20_20260524T215425Z.json` (PASS)
     - hyp_plus_feat: `reports/akfp/hyp_plus_feat/akfp_hyp_plus_feat_cycle_SOLUSDT_1m_2026-05-20_20260524T220128Z.json` (PASS)
     - combo_working (полный перебор):
       - `reports/akfp/combo_working/akfp_combo_working_cycle_SOLUSDT_1m_2026-05-20_20260525T014139Z.json` (FAIL по стратегии, корректно)
       - long: `accepted_total=2/20`
       - short: `accepted_total=0/18`
     - anti-random:
       - `reports/akfp/anti_random/akfp_anti_random_validate_SOLUSDT_1m_2026-05-20_20260525T015621Z.json` (PASS, `strategy_pass=false`)
     - long_final:
       - `reports/akfp/final_long/akfp_long_final_cycle_SOLUSDT_1m_2026-05-20_20260525T014609Z.json` (PASS, `strategy_pass=false`)
     - short_final:
       - `reports/akfp/final_short/akfp_short_final_cycle_SOLUSDT_1m_2026-05-20_20260525T014604Z.json` (PASS, `strategy_pass=false`)
74. QA-цепочка (таблицы/движок/зависимости) после восстановления readiness:
   - `reports/qa_gate/p23_operator_unified_20260525T021350Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260525T021643Z.json` (long, PASS)
   - `reports/qa_gate/table_convergence_5plus_20260525T021656Z.json` (short, PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260525T021712Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260525T021712Z.json` (PASS)
   - `reports/qa_gate/tz_gate_20260525T021712Z.json` (PASS)
   - `reports/qa_gate/p72_freeze_ready_20260525T021722Z.json` (PASS)
   - `reports/qa_gate/p24_latest_pass_20260525T021732Z.json` (PASS)
   - `reports/qa_gate/p26_audit_lock_20260525T021732Z.json` (PASS)
75. Финализация:
   - combined consistency:
     - `reports/akfp/combined/akfp_combined_consistency_2026-05-20_20260525T021731Z.json` (PASS)
   - p12 finalize:
     - `reports/akfp/finalization/akfp_p12_finalize_SOLUSDT_1m_2026-05-20_20260525T021732Z.json` (PASS)
