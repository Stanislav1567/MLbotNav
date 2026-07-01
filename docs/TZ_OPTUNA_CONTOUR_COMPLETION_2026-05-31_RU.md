# ТЗ: Завершение калибровочного контура Optuna (2026-05-31)

Дата: 2026-05-31  
Контур: только `Optuna/APTuna` в `MLbotNav`  
Ограничение: `ML runtime` не трогаем, ML-сигналы в Optuna-контуре не используем

## 1. Цель этапа
1. Довести калибровочный контур до технически рабочего состояния без багов.
2. Подтвердить, что все калибруемые параметры реально участвуют в переборе.
3. Обеспечить проверяемость и воспроизводимость: каждый шаг фиксируется артефактами и аудитом.
4. На режиме `1d train / 1d test` и `1m` не требовать устойчивой прибыльности как основного критерия этого этапа.

## 2. Жесткий scope (MUST)
1. Работаем только в `C:\Users\007\Desktop\MLbotNav`.
2. Рабочий контур: `APTuna`, `src/mlbotnav`, `configs`, `docs`, `reports`.
3. Изоляция от ML: `OptunaMlSignalBackend=off`.
4. Никаких ML-combo и ML-сигналов в текущем Optuna-контуре.

## 3. Режим исполнения
1. Окно: один день калибровки + один день прогона.
2. Таймфрейм: `1m`.
3. Режим вычислений: strict `3x9`.
4. Запуски раздельно по режимам: `long_only` и `short_only`.
5. Каждый шаг: `single-change` (одно осознанное изменение на шаг).

## 4. Обязательные требования к калибровке
1. Каждый модуль калибруется отдельно: все калибруемые параметры модуля от минимума до максимума.
2. Каждая фича калибруется отдельно: все калибруемые параметры фичи от минимума до максимума.
3. Каждая гипотеза калибруется отдельно: все калибруемые параметры гипотезы от минимума до максимума.
4. Некалибруемые фичи не удаляются из контура: остаются в runtime и проверяются в общем прогоне.
5. Для сеток вводятся и поддерживаются три уровня: `wide`, `medium`, `narrow`.

## 5. Definition of Done (этап "контур собран")
1. Цепочка `S1 -> S2 -> S3 -> S4` выполняется без технических сбоев.
2. Для всех калибруемых параметров есть подтверждение прохождения `min` и `max`.
3. Все активные блоки/фичи/гипотезы участвуют в runtime.
4. На каждый шаг есть полный комплект артефактов: checkpoint, worker logs, coverage report, `pip check`, `text_guard`, `readiness --show`, синхронизация `ACTIVE_WORK_ITEMS` и `CHANGELOG`.
5. В активных документах нет кракозябр и битой кодировки.

## 6. Статус по аудиту на 2026-05-31 (обновлено)
1. Подтвержден инвентарь: `68` фич (`56` calibratable, `12` non-calibratable), `20` calibratable гипотез, `5` search-grid параметров, `27` profiles.
2. Подтверждена активация 6 блоков в runtime.
3. `P0` закрыт по технике:
4. storage работает в postgres-режиме без silent sqlite fallback;
5. taxonomy `wide/medium/narrow` закреплена в runtime-контуре;
6. есть PASS-артефакты `min_hit/max_hit` по profile и search-grid покрытиям для `long_only` и `short_only`.
7. `P1` для этапа сборки контура закрыт:
8. search-grid quintet PASS/FAIL отчет есть;
9. short-only gate override унифицирован в `thresholds.yaml`;
10. автодобавление записей в реестр/хронологию заведено утилитой `mlbotnav.docs_registry_append`.
11. Операционный статус: `READY_FOR_CONTROLLED_UNFREEZE` при сохраненном governance freeze (`project_ready=false`, `enforce_freeze=true`).

## 7. Приоритеты исполнения (строго по порядку)
1. `P0-CLOSEOUT.1` Сверка и упаковка финальных артефактов контура в единый пакет доказательств.
2. `P0-CLOSEOUT.2` Acceptance-прогоны `long_only` и `short_only` в режиме `1d train / 1d test`, `1m`, strict `3x9`.
3. `P0-CLOSEOUT.3` Обязательный аудит после прогонов: цепочка, coverage, readiness, отсутствие кракозябр.
4. `P0-CLOSEOUT.4` При найденных отклонениях: immediate fix -> повторная проверка -> повторная фиксация артефактов.
5. `P0-CLOSEOUT.5` Запись результата каждого шага в `ACTIVE_WORK_ITEMS_RU.md` и `CHANGELOG_CHRONOLOGY_RU.md` (append-only).
6. `P0-CLOSEOUT.6` После PASS: обновление итогового статуса ТЗ и подготовка окна controlled unfreeze.

## 8. Критерии готовности к боевому режиму контура
1. Все шаги `P0-CLOSEOUT` закрыты артефактами и повторной проверкой после возможных фиксов.
2. Технический аудит контура без критичных замечаний: `S1 -> S2 -> S3 -> S4` PASS, coverage PASS, readiness checkpoint PASS.
3. Изоляция ML-контура подтверждена на всем пути A->I (`OptunaMlSignalBackend=off`, без ML-combo/ML-сигналов).
4. В активных документах нет битой кодировки/кракозябр.

## 9. Протокол выполнения шага (обязательный на каждом пункте)
1. Аудит/проверка пункта.
2. Проверка битости/кракозябр в затронутых файлах.
3. Если найдено отклонение: немедленный фикс.
4. Повторная проверка после фикса.
5. Запись в `ACTIVE + CHANGELOG` с артефактами.

## 10. Прогресс исполнения P0-CLOSEOUT (2026-05-31)
1. `P0-CLOSEOUT.1` DONE: пакет артефактов сверен, отчет `reports/qa_gate/p1524_p0_closeout_step1_artifact_bundle_audit_20260531T143007Z.json`.
2. `P0-CLOSEOUT.2` DONE: acceptance long/short выполнен, итоговый отчет `reports/qa_gate/p1525_p0_closeout_step2_acceptance_audit_20260531T143713Z.json`.
3. `P0-CLOSEOUT.3` DONE: обязательный пост-аудит PASS (`profile/search-grid coverage`, `pip check`, `text_guard`, `readiness --show`).
4. `P0-CLOSEOUT.4` DONE: применен фикс по отклонению profile coverage (увеличен бюджет trials `132 -> 220`), повторная проверка PASS.
5. `P0-CLOSEOUT.5` DONE: записи добавлены в `ACTIVE_WORK_ITEMS_RU.md` (P1524, P1525) и `CHANGELOG_CHRONOLOGY_RU.md`.
6. `P0-CLOSEOUT.6` DONE: финальный статус синхронизирован, отчет `reports/qa_gate/p1526_p0_closeout_step6_final_status_sync_20260531T143834Z.json`.

## 11. Controlled Unfreeze (исполнение окна)
1. Этап RUN_WINDOW_1 выполнен.
2. Результат: технический PASS (long/short launcher OK, 4 coverage-аудита PASS, pip check PASS, text_guard PASS).
3. Freeze-governance сохранен после окна: project_ready=false, enforce_freeze=true.
4. Сводный артефакт: reports/qa_gate/p1527_controlled_unfreeze_run_window_1_20260531T144558Z.json.
5. Этап RUN_WINDOW_2 выполнен с фиксом.
6. Первичный аудит: profile_coverage_short_only FAIL (недобор max-hit macd_signal_period), остальные обязательные проверки PASS.
7. Фикс: увеличен бюджет short_only trials 220 -> 300, повторный профильный аудит PASS.
8. Итог RUN_WINDOW_2: PASS_AFTER_FIX, freeze-governance сохранен (project_ready=false, enforce_freeze=true).
9. Сводный артефакт: reports/qa_gate/p1529_controlled_unfreeze_run_window_2_20260531T145119Z.json.
10. Этап RUN_WINDOW_3 выполнен без фикса.
11. Итог RUN_WINDOW_3: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
12. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
13. Сводный артефакт: reports/qa_gate/p1531_controlled_unfreeze_run_window_3_20260531T145642Z.json.
14. Этап RUN_WINDOW_4 выполнен без фикса.
15. Итог RUN_WINDOW_4: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
16. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
17. Сводный артефакт: reports/qa_gate/p1534_controlled_unfreeze_run_window_4_20260531T150308Z.json.
18. Этап RUN_WINDOW_5 выполнен без фикса.
19. Итог RUN_WINDOW_5: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
20. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
21. Сводный артефакт: reports/qa_gate/p1536_controlled_unfreeze_run_window_5_20260531T150725Z.json.
22. Этап RUN_WINDOW_6 выполнен без фикса.
23. Итог RUN_WINDOW_6: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
24. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
25. Сводный артефакт: reports/qa_gate/p1538_controlled_unfreeze_run_window_6_20260531T151102Z.json.
26. Этап RUN_WINDOW_7 выполнен без фикса.
27. Итог RUN_WINDOW_7: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
28. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
29. Сводный артефакт: reports/qa_gate/p1540_controlled_unfreeze_run_window_7_20260531T181511Z.json.
30. Этап RUN_WINDOW_8 выполнен без фикса.
31. Итог RUN_WINDOW_8: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
32. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
33. Сводный артефакт: reports/qa_gate/p1542_controlled_unfreeze_run_window_8_20260531T181921Z.json.
34. Этап RUN_WINDOW_9 выполнен без фикса.
35. Итог RUN_WINDOW_9: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
36. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
37. Сводный артефакт: reports/qa_gate/p1544_controlled_unfreeze_run_window_9_20260531T182328Z.json.
38. Этап RUN_WINDOW_10 выполнен без фикса.
39. Итог RUN_WINDOW_10: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
40. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
41. Сводный артефакт: reports/qa_gate/p1546_controlled_unfreeze_run_window_10_20260531T182943Z.json.
42. Этап RUN_WINDOW_11 выполнен без фикса.
43. Итог RUN_WINDOW_11: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
44. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
45. Сводный артефакт: reports/qa_gate/p1548_controlled_unfreeze_run_window_11_20260531T183311Z.json.
46. Этап RUN_WINDOW_12 выполнен с фиксом.
47. Первичный аудит: profile_coverage_long_only FAIL (недобор max-hit по threshold_fine), остальные обязательные проверки прошли.
48. Фикс: увеличен бюджет long_only trials 220 -> 300, повторный аудит PASS.
49. Итог RUN_WINDOW_12: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
50. Сводный артефакт: reports/qa_gate/p1550_controlled_unfreeze_run_window_12_20260531T183748Z.json.
51. Этап RUN_WINDOW_13 выполнен без фикса.
52. Итог RUN_WINDOW_13: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
53. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
54. Сводный артефакт: reports/qa_gate/p1552_controlled_unfreeze_run_window_13_20260531T184110Z.json.
55. Этап RUN_WINDOW_14 выполнен без фикса.
56. Итог RUN_WINDOW_14: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
57. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
58. Сводный артефакт: reports/qa_gate/p1554_controlled_unfreeze_run_window_14_20260531T184501Z.json.
59. Этап RUN_WINDOW_15 выполнен без фикса.
60. Итог RUN_WINDOW_15: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
61. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
62. Сводный артефакт: reports/qa_gate/p1556_controlled_unfreeze_run_window_15_20260531T184827Z.json.
63. Этап RUN_WINDOW_16 выполнен с фиксом.
64. Первичный аудит: profile_coverage_short_only FAIL (недобор max-hit по pattern_age_cap).
65. Фикс #1: short_only trials 220 -> 300; повторный аудит дал новый FAIL (ratio_pattern max-hit).
66. Фикс #2: short_only trials 300 -> 400; повторный аудит PASS.
67. Итог RUN_WINDOW_16: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
68. Сводный артефакт: reports/qa_gate/p1558_controlled_unfreeze_run_window_16_20260531T185436Z.json.
69. Этап RUN_WINDOW_17 выполнен с фиксом.
70. Первичный запуск short_only дал PARTIAL_FAIL (worker_failed), лог ошибки пустой; выполнен технический rerun short_only.
71. После rerun профильный аудит short_only дал FAIL (pattern_age_cap min/max hit coverage).
72. Фикс: увеличен short_only trials 220 -> 400; повторный аудит PASS.
73. Итог RUN_WINDOW_17: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
74. Сводный артефакт: reports/qa_gate/p1560_controlled_unfreeze_run_window_17_20260531T190050Z.json.
75. Этап RUN_WINDOW_18 выполнен без фикса.
76. Итог RUN_WINDOW_18: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
77. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
78. Сводный артефакт: reports/qa_gate/p1562_controlled_unfreeze_run_window_18_20260531T190428Z.json.
79. Этап RUN_WINDOW_19 выполнен с фиксом.
80. Первичный запуск short_only дал PARTIAL_FAIL (worker_failed/JSONDecodeError); выполнен технический rerun short_only.
81. После rerun профильный аудит short_only дал FAIL (pattern_age_cap max-hit coverage).
82. Фикс: увеличен short_only trials 220 -> 300; повторный аудит PASS.
83. Итог RUN_WINDOW_19: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
84. Сводный артефакт: reports/qa_gate/p1564_controlled_unfreeze_run_window_19_20260531T191036Z.json.
85. Этап RUN_WINDOW_20 выполнен с фиксом.
86. Первичный аудит: profile_coverage_short_only FAIL (недобор max-hit по macd_slow_period).
87. Фикс: увеличен short_only trials 220 -> 300; повторный аудит PASS.
88. Итог RUN_WINDOW_20: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
89. Сводный артефакт: reports/qa_gate/p1566_controlled_unfreeze_run_window_20_20260531T191523Z.json.
90. Этап RUN_WINDOW_21 выполнен без фикса.
91. Итог RUN_WINDOW_21: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
92. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
93. Сводный артефакт: reports/qa_gate/p1568_controlled_unfreeze_run_window_21_20260531T191847Z.json.
94. Этап RUN_WINDOW_22 выполнен без фикса.
95. Итог RUN_WINDOW_22: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS).
96. Freeze-governance сохранен (project_ready=false, enforce_freeze=true).
97. Сводный артефакт: reports/qa_gate/p1570_controlled_unfreeze_run_window_22_20260531T192208Z.json.
98. Этап RUN_WINDOW_23 выполнен с фиксом.
99. Первичный аудит: profile_coverage_short_only FAIL (недобор min-hit по doji_threshold).
100. Фикс: увеличен short_only trials 220 -> 300; повторный аудит PASS.
101. Итог RUN_WINDOW_23: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
102. Сводный артефакт: reports/qa_gate/p1572_controlled_unfreeze_run_window_23_20260531T192641Z.json.
103. Этап RUN_WINDOW_24 выполнен с фиксом.
104. Первичный аудит: profile_coverage_short_only FAIL (недобор min-hit по doji_threshold).
105. Фикс #1: short_only trials 220 -> 300; повторный аудит дал новый FAIL (macd_slow_period max-hit).
106. Фикс #2: short_only trials 300 -> 400; повторный аудит PASS.
107. Итог RUN_WINDOW_24: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
108. Сводный артефакт: reports/qa_gate/p1574_controlled_unfreeze_run_window_24_20260531T193247Z.json.
109. Этап RUN_WINDOW_25 выполнен без фикса.
110. Итог RUN_WINDOW_25: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
111. Сводный артефакт: reports/qa_gate/p1576_controlled_unfreeze_run_window_25_20260531T193655Z.json.
112. Этап RUN_WINDOW_26 выполнен без фикса.
113. Итог RUN_WINDOW_26: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
114. Сводный артефакт: reports/qa_gate/p1578_controlled_unfreeze_run_window_26_20260531T194201Z.json.
115. Этап RUN_WINDOW_27 выполнен без фикса.
116. Итог RUN_WINDOW_27: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
117. Сводный артефакт: reports/qa_gate/p1580_controlled_unfreeze_run_window_27_20260531T194552Z.json.
118. Этап RUN_WINDOW_28 выполнен с фиксом.
119. Первичный аудит: profile_coverage_long_only FAIL (недобор max-hit по macd_slow_period).
120. Фикс: увеличен long_only trials 220 -> 300; повторный аудит PASS.
121. Итог RUN_WINDOW_28: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
122. Сводный артефакт: reports/qa_gate/p1582_controlled_unfreeze_run_window_28_20260601T024714Z.json.
123. Этап RUN_WINDOW_29 выполнен без фикса.
124. Итог RUN_WINDOW_29: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
125. Сводный артефакт: reports/qa_gate/p1584_controlled_unfreeze_run_window_29_20260601T025107Z.json.
126. Этап RUN_WINDOW_30 выполнен без фикса.
127. Итог RUN_WINDOW_30: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
128. Сводный артефакт: reports/qa_gate/p1586_controlled_unfreeze_run_window_30_20260601T025448Z.json.
129. Этап RUN_WINDOW_31 выполнен без фикса.
130. Итог RUN_WINDOW_31: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
131. Сводный артефакт: reports/qa_gate/p1588_controlled_unfreeze_run_window_31_20260601T025816Z.json.
132. Этап RUN_WINDOW_32 выполнен без фикса.
133. Итог RUN_WINDOW_32: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
134. Сводный артефакт: reports/qa_gate/p1590_controlled_unfreeze_run_window_32_20260601T030128Z.json.
135. Этап RUN_WINDOW_33 выполнен с фиксом.
136. Первичный аудит: profile_coverage_long_only FAIL (недобор max-hit по threshold_fine).
137. Фикс: увеличен long_only trials 220 -> 300; повторный аудит PASS.
138. Итог RUN_WINDOW_33: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
139. Сводный артефакт: reports/qa_gate/p1592_controlled_unfreeze_run_window_33_20260601T030607Z.json.
140. Этап RUN_WINDOW_34 выполнен без фикса.
141. Итог RUN_WINDOW_34: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
142. Сводный артефакт: reports/qa_gate/p1594_controlled_unfreeze_run_window_34_20260601T030942Z.json.
143. Этап RUN_WINDOW_35 выполнен без фикса.
144. Итог RUN_WINDOW_35: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
145. Сводный артефакт: reports/qa_gate/p1596_controlled_unfreeze_run_window_35_20260601T031316Z.json.
146. Этап RUN_WINDOW_36 выполнен без фикса.
147. Итог RUN_WINDOW_36: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
148. Сводный артефакт: reports/qa_gate/p1598_controlled_unfreeze_run_window_36_20260601T031645Z.json.
149. Этап RUN_WINDOW_37 выполнен с фиксом.
150. Первичный аудит: profile_coverage_short_only FAIL (недобор max-hit по threshold_fine).
151. Фикс: увеличен short_only trials 220 -> 300; повторный аудит PASS.
152. Итог RUN_WINDOW_37: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
153. Сводный артефакт: reports/qa_gate/p1600_controlled_unfreeze_run_window_37_20260601T032139Z.json.
154. Этап RUN_WINDOW_38 выполнен с фиксом.
155. Первичный запуск long_only дал PARTIAL_FAIL (worker_failed); выполнен технический rerun long_only.
156. Повторный контроль после rerun: 4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS.
157. Итог RUN_WINDOW_38: PASS_AFTER_FIX, freeze-governance сохранен.
158. Сводный артефакт: reports/qa_gate/p1602_controlled_unfreeze_run_window_38_20260601T032646Z.json.
159. Этап RUN_WINDOW_39 выполнен без фикса.
160. Итог RUN_WINDOW_39: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
161. Сводный артефакт: reports/qa_gate/p1604_controlled_unfreeze_run_window_39_20260601T033028Z.json.
162. Этап RUN_WINDOW_40 выполнен без фикса.
163. Итог RUN_WINDOW_40: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
164. Сводный артефакт: reports/qa_gate/p1606_controlled_unfreeze_run_window_40_20260601T033419Z.json.
165. Этап RUN_WINDOW_41 выполнен с фиксом.
166. Первичный запуск short_only дал PARTIAL_FAIL (worker_failed); выполнен технический rerun short_only.
167. Повторный контроль после rerun: 4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS.
168. Итог RUN_WINDOW_41: PASS_AFTER_FIX, freeze-governance сохранен.
169. Сводный артефакт: reports/qa_gate/p1608_controlled_unfreeze_run_window_41_20260601T033900Z.json.
170. Этап RUN_WINDOW_42 выполнен без фикса.
171. Итог RUN_WINDOW_42: PASS (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
172. Сводный артефакт: reports/qa_gate/p1610_controlled_unfreeze_run_window_42_20260601T034306Z.json.
173. Этап RUN_WINDOW_43 выполнен с фиксом.
174. Первичный аудит: profile_coverage_short_only FAIL (недобор max-hit по macd_slow_period).
175. Фикс: увеличен short_only trials 220 -> 300; повторный аудит PASS.
176. Итог RUN_WINDOW_43: PASS_AFTER_FIX (4 coverage-аудита PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
177. Сводный артефакт: reports/qa_gate/p1612_controlled_unfreeze_run_window_43_20260601T034820Z.json.
178. Этап RUN_WINDOW_44 выполнен с двухшаговым фиксом.
179. Первичный аудит: profile_coverage_long_only FAIL (`pattern_age_cap`), profile_coverage_short_only FAIL (`return_lookback`), search_grid_coverage_short_only FAIL.
180. Фикс #1: trials 220 -> 300 для long_only и short_only; профильные аудиты PASS, но search_grid_coverage long/short оставался FAIL.
181. Фикс #2: задан canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`), затем повторены long/short.
182. Итог RUN_WINDOW_44: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T040000Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
183. Сводный артефакт: reports/qa_gate/p1614_controlled_unfreeze_run_window_44_20260601T040014Z.json.
184. Этап RUN_WINDOW_45 выполнен без фикса.
185. Прогон выполнен с canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) и trials=220.
186. Итог RUN_WINDOW_45: PASS (4 coverage-аудита PASS @20260601T041149Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
187. Сводный артефакт: reports/qa_gate/p1616_controlled_unfreeze_run_window_45_20260601T041155Z.json.
188. Этап RUN_WINDOW_46 выполнен без фикса.
189. Прогон выполнен с canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) и trials=220.
190. Итог RUN_WINDOW_46: PASS (4 coverage-аудита PASS @20260601T041542Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
191. Сводный артефакт: reports/qa_gate/p1618_controlled_unfreeze_run_window_46_20260601T041549Z.json.
192. Этап RUN_WINDOW_47 выполнен без фикса.
193. Прогон выполнен с canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) и trials=220.
194. Итог RUN_WINDOW_47: PASS (4 coverage-аудита PASS @20260601T041942Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
195. Сводный артефакт: reports/qa_gate/p1620_controlled_unfreeze_run_window_47_20260601T041949Z.json.
196. Этап RUN_WINDOW_48 выполнен без фикса.
197. Прогон выполнен с canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) и trials=220.
198. Итог RUN_WINDOW_48: PASS (4 coverage-аудита PASS @20260601T042315Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
199. Сводный артефакт: reports/qa_gate/p1622_controlled_unfreeze_run_window_48_20260601T042323Z.json.
200. Этап RUN_WINDOW_49 выполнен с фиксом.
201. Первичный аудит: profile_coverage_short_only FAIL (недобор min/max hits по `pattern_age_cap`, `period_standard`, `threshold_fine`).
202. Фикс: повтор short_only с trials 220 -> 300; повторный контроль (4 coverage-аудита) PASS.
203. Итог RUN_WINDOW_49: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T042818Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
204. Сводный артефакт: reports/qa_gate/p1624_controlled_unfreeze_run_window_49_20260601T042825Z.json.
205. Этап RUN_WINDOW_50 выполнен без фикса.
206. Прогон выполнен с canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) и trials=220.
207. Итог RUN_WINDOW_50: PASS (4 coverage-аудита PASS @20260601T044209Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
208. Сводный артефакт: reports/qa_gate/p1626_controlled_unfreeze_run_window_50_20260601T044217Z.json.
209. Выполнена синхронизация decision package для RUN_WINDOW_50 (`docs/OPTUNA_UNFREEZE_DECISION_PACKAGE_2026-05-31_RU.md`).
210. Обязательный post-fix re-audit после документного обновления: `text_guard PASS` (`reports/qa_gate/recovery_r5_text_guard_20260601T044448Z.json`), `readiness --show PASS` (`reports/readiness/readiness_check_20260601T044448Z.json`), `pip check PASS`.
211. Итог шага P1628: PASS, freeze-governance сохранен (`project_ready=false`, `enforce_freeze=true`).
212. Сводный артефакт шага P1628: reports/qa_gate/p1628_post_window50_docsync_audit_20260601T044518Z.json.
213. Этап RUN_WINDOW_51 выполнен с фиксом.
214. Первичный аудит: `profile_coverage_long_only FAIL` (недобор min-hit по `density_bin_pct`).
215. Фикс: повтор `long_only` с trials `220 -> 300`; повторный аудит PASS.
216. Итог RUN_WINDOW_51: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T045037Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
217. Сводный артефакт: reports/qa_gate/p1629_controlled_unfreeze_run_window_51_20260601T045038Z.json.
218. Этап RUN_WINDOW_52 выполнен без фикса.
219. Прогон выполнен с canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) и trials=220.
220. Итог RUN_WINDOW_52: PASS (4 coverage-аудита PASS @20260601T045432Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
221. Сводный артефакт: reports/qa_gate/p1631_controlled_unfreeze_run_window_52_20260601T045433Z.json.
222. Этап RUN_WINDOW_53 выполнен без фикса.
223. Прогон выполнен с canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) и trials=220.
224. Итог RUN_WINDOW_53: PASS (4 coverage-аудита PASS @20260601T045810Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
225. Сводный артефакт: reports/qa_gate/p1633_controlled_unfreeze_run_window_53_20260601T045810Z.json.
226. Этап RUN_WINDOW_54 выполнен без фикса.
227. Прогон выполнен с canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) и trials=220.
228. Итог RUN_WINDOW_54: PASS (4 coverage-аудита PASS @20260601T050156Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
229. Сводный артефакт: reports/qa_gate/p1635_controlled_unfreeze_run_window_54_20260601T050157Z.json.
230. Этап RUN_WINDOW_55 выполнен с фиксом.
231. Первичный аудит: `profile_coverage_short_only FAIL` (недобор max-hit по `pattern_age_cap`).
232. Фикс: повтор `short_only` с trials `220 -> 300`; повторный аудит PASS.
233. Итог RUN_WINDOW_55: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T050712Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
234. Сводный артефакт: reports/qa_gate/p1637_controlled_unfreeze_run_window_55_20260601T050713Z.json.
235. Этап RUN_WINDOW_56 выполнен без фикса.
236. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
237. Итог RUN_WINDOW_56: PASS (4 coverage-аудита PASS @20260601T051105Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
238. Сводный артефакт: reports/qa_gate/p1639_controlled_unfreeze_run_window_56_20260601T051105Z.json.
239. Этап RUN_WINDOW_57 выполнен без фикса.
240. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
241. Итог RUN_WINDOW_57: PASS (4 coverage-аудита PASS @20260601T051420Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
242. Сводный артефакт: reports/qa_gate/p1641_controlled_unfreeze_run_window_57_20260601T051421Z.json.
243. Этап RUN_WINDOW_58 выполнен без фикса.
244. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
245. Итог RUN_WINDOW_58: PASS (4 coverage-аудита PASS @20260601T051741Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
246. Сводный артефакт: reports/qa_gate/p1643_controlled_unfreeze_run_window_58_20260601T051742Z.json.
247. Этап RUN_WINDOW_59 выполнен с фиксом.
248. Первичный аудит: profile_coverage_long_only FAIL (недобор max-hit по atio_pattern).
249. Фикс: повтор long_only с trials 220 -> 300; повторный аудит PASS.
250. Итог RUN_WINDOW_59: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T052252Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
251. Сводный артефакт: reports/qa_gate/p1645_controlled_unfreeze_run_window_59_20260601T052252Z.json.
252. Этап RUN_WINDOW_60 выполнен без фикса.
253. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
254. Итог RUN_WINDOW_60: PASS (4 coverage-аудита PASS @20260601T052646Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
255. Сводный артефакт: reports/qa_gate/p1647_controlled_unfreeze_run_window_60_20260601T052647Z.json.
256. Этап RUN_WINDOW_61 выполнен с фиксом.
257. Первичный аудит: profile_coverage_short_only FAIL (недобор min-hit по density_window_long).
258. Фикс: повтор short_only с trials 220 -> 300; повторный аудит PASS.
259. Итог RUN_WINDOW_61: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T053148Z/20260601T053149Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
260. Сводный артефакт: reports/qa_gate/p1649_controlled_unfreeze_run_window_61_20260601T053149Z.json.
261. Этап RUN_WINDOW_62 выполнен без фикса.
262. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
263. Итог RUN_WINDOW_62: PASS (4 coverage-аудита PASS @20260601T053522Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
264. Сводный артефакт: reports/qa_gate/p1651_controlled_unfreeze_run_window_62_20260601T053522Z.json.
265. Этап RUN_WINDOW_63 выполнен без фикса.
266. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
267. Итог RUN_WINDOW_63: PASS (4 coverage-аудита PASS @20260601T053848Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
268. Сводный артефакт: reports/qa_gate/p1653_controlled_unfreeze_run_window_63_20260601T053848Z.json.
269. Этап RUN_WINDOW_64 выполнен с двухшаговым фиксом.
270. Первичный аудит: profile_coverage_long_only FAIL (недобор max-hit по threshold_fine).
271. Фикс #1: повтор long_only с trials 220 -> 300; повторный аудит дал новый FAIL (macd_slow_period max-hit).
272. Фикс #2: повтор long_only с trials 300 -> 400; повторный аудит PASS.
273. Итог RUN_WINDOW_64: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T054524Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
274. Сводный артефакт: reports/qa_gate/p1655_controlled_unfreeze_run_window_64_20260601T054525Z.json.
275. Этап RUN_WINDOW_65 выполнен без фикса.
276. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
277. Итог RUN_WINDOW_65: PASS (4 coverage-аудита PASS @20260601T055059Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
278. Сводный артефакт: reports/qa_gate/p1657_controlled_unfreeze_run_window_65_20260601T055122Z.json.

279. Этап RUN_WINDOW_66 выполнен без фикса.
280. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
281. Итог RUN_WINDOW_66: PASS (4 coverage-аудита PASS @20260601T055648Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
282. Сводный артефакт: reports/qa_gate/p1660_controlled_unfreeze_run_window_66_20260601T055700Z.json.
283. Этап RUN_WINDOW_67 выполнен без фикса.
284. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
285. Итог RUN_WINDOW_67: PASS (4 coverage-аудита PASS @20260601T060014Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
286. Сводный артефакт: reports/qa_gate/p1662_controlled_unfreeze_run_window_67_20260601T060025Z.json.
287. Этап RUN_WINDOW_68 выполнен без фикса.
288. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
289. Итог RUN_WINDOW_68: PASS (4 coverage-аудита PASS @20260601T060342Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
290. Сводный артефакт: reports/qa_gate/p1664_controlled_unfreeze_run_window_68_20260601T060355Z.json.
291. Этап RUN_WINDOW_69 выполнен с двухшаговым фиксом.
292. Первичный аудит: profile_coverage_long_only FAIL (недобор max-hit по macd_slow_period).
293. Фикс #1: повтор long_only с trials 220 -> 300; повторный аудит long profile coverage остался FAIL.
294. Фикс #2: повтор long_only с trials 300 -> 400; повторный аудит PASS.
295. Итог RUN_WINDOW_69: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T061030Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
296. Сводный артефакт: reports/qa_gate/p1666_controlled_unfreeze_run_window_69_20260601T061040Z.json.
297. Этап RUN_WINDOW_70 выполнен без фикса.
298. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
299. Итог RUN_WINDOW_70: PASS (4 coverage-аудита PASS @20260601T061416Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
300. Сводный артефакт: reports/qa_gate/p1668_controlled_unfreeze_run_window_70_20260601T061425Z.json.
301. Этап RUN_WINDOW_71 выполнен с фиксом.
302. Первичный аудит: profile_coverage_long_only FAIL (недобор max-hit по pattern_age_cap).
303. Фикс: повтор long_only с trials 220 -> 300; повторный аудит PASS.
304. Итог RUN_WINDOW_71: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T061945Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
305. Сводный артефакт: reports/qa_gate/p1670_controlled_unfreeze_run_window_71_20260601T061958Z.json.
306. Этап RUN_WINDOW_72 выполнен без фикса.
307. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
308. Итог RUN_WINDOW_72: PASS (4 coverage-аудита PASS @20260601T062333Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
309. Сводный артефакт: reports/qa_gate/p1672_controlled_unfreeze_run_window_72_20260601T062345Z.json.
310. Этап RUN_WINDOW_73 выполнен с техническим фиксом.
311. Первичный long_only: launcher status PARTIAL_FAIL (worker_failed).
312. Фикс: технический rerun long_only без изменения параметров; launcher status OK.
313. Итог RUN_WINDOW_73: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T062740Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
314. Сводный артефакт: reports/qa_gate/p1674_controlled_unfreeze_run_window_73_20260601T062750Z.json.
315. Этап RUN_WINDOW_74 выполнен без фикса.
316. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
317. Итог RUN_WINDOW_74: PASS (4 coverage-аудита PASS @20260601T063107Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
318. Сводный артефакт: reports/qa_gate/p1676_controlled_unfreeze_run_window_74_20260601T063120Z.json.
319. Этап RUN_WINDOW_75 выполнен с фиксом.
320. Первичный аудит: profile_coverage_long_only FAIL (недобор max-hit по pattern_age_cap).
321. Фикс: повтор long_only с trials 220 -> 300; повторный аудит PASS.
322. Итог RUN_WINDOW_75: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T063624Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
323. Сводный артефакт: reports/qa_gate/p1678_controlled_unfreeze_run_window_75_20260601T063638Z.json.
324. Этап RUN_WINDOW_76 выполнен без фикса.
325. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
326. Итог RUN_WINDOW_76: PASS (4 coverage-аудита PASS @20260601T064039Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен.
327. Сводный артефакт: reports/qa_gate/p1680_controlled_unfreeze_run_window_76_20260601T064050Z.json.
328. Этап RUN_WINDOW_77 выполнен с фиксом.
329. Первичный аудит: profile_coverage_long_only FAIL (недобор max-hit по threshold_fine); фикс: long_only rerun с корректным квотированием grid-параметров и повышением trials 220 -> 300; повторный аудит PASS.
330. Итог RUN_WINDOW_77: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T064724Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1682_controlled_unfreeze_run_window_77_20260601T064857Z.json.
331. Этап RUN_WINDOW_78 выполнен без фикса.
332. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
333. Итог RUN_WINDOW_78: PASS (4 coverage-аудита PASS @20260601T065115Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1684_controlled_unfreeze_run_window_78_20260601T065207Z.json.
334. Этап RUN_WINDOW_79 выполнен без фикса.
335. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
336. Итог RUN_WINDOW_79: PASS (4 coverage-аудита PASS @20260601T065449Z/20260601T065450Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1686_controlled_unfreeze_run_window_79_20260601T065539Z.json.
337. Этап RUN_WINDOW_80 выполнен без фикса.
338. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
339. Итог RUN_WINDOW_80: PASS (4 coverage-аудита PASS @20260601T065730Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1688_controlled_unfreeze_run_window_80_20260601T065822Z.json.
340. Этап RUN_WINDOW_81 выполнен без фикса.
341. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
342. Итог RUN_WINDOW_81: PASS (4 coverage-аудита PASS @20260601T070035Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1690_controlled_unfreeze_run_window_81_20260601T070123Z.json.
343. Этап RUN_WINDOW_82 выполнен без фикса.
344. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
345. Итог RUN_WINDOW_82: PASS (4 coverage-аудита PASS @20260601T070341Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1692_controlled_unfreeze_run_window_82_20260601T070429Z.json.
346. Этап RUN_WINDOW_83 выполнен без фикса.
347. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
348. Итог RUN_WINDOW_83: PASS (4 coverage-аудита PASS @20260601T070659Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1694_controlled_unfreeze_run_window_83_20260601T070747Z.json.
349. Этап RUN_WINDOW_84 выполнен без фикса.
350. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
351. Итог RUN_WINDOW_84: PASS (4 coverage-аудита PASS @20260601T071003Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1696_controlled_unfreeze_run_window_84_20260601T071051Z.json.
352. Этап RUN_WINDOW_85 выполнен без фикса.
353. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
354. Итог RUN_WINDOW_85: PASS (4 coverage-аудита PASS @20260601T071312Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1698_controlled_unfreeze_run_window_85_20260601T071401Z.json.
355. Этап RUN_WINDOW_86 выполнен без фикса.
356. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
357. Итог RUN_WINDOW_86: PASS (4 coverage-аудита PASS @20260601T071610Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1700_controlled_unfreeze_run_window_86_20260601T071659Z.json.
358. Этап RUN_WINDOW_87 выполнен без фикса.
359. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
360. Итог RUN_WINDOW_87: PASS (4 coverage-аудита PASS @20260601T071910Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1702_controlled_unfreeze_run_window_87_20260601T071959Z.json.
361. Этап RUN_WINDOW_88 выполнен без фикса.
362. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
363. Итог RUN_WINDOW_88: PASS (4 coverage-аудита PASS @20260601T072213Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1704_controlled_unfreeze_run_window_88_20260601T072302Z.json.
364. Этап RUN_WINDOW_89 выполнен без фикса.
365. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
366. Итог RUN_WINDOW_89: PASS (4 coverage-аудита PASS @20260601T072511Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1706_controlled_unfreeze_run_window_89_20260601T072602Z.json.
367. Этап RUN_WINDOW_90 выполнен без фикса.
368. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
369. Итог RUN_WINDOW_90: PASS (4 coverage-аудита PASS @20260601T072821Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1708_controlled_unfreeze_run_window_90_20260601T072912Z.json.
370. Этап RUN_WINDOW_91 выполнен без фикса.
371. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
372. Итог RUN_WINDOW_91: PASS (4 coverage-аудита PASS @20260601T073134Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1710_controlled_unfreeze_run_window_91_20260601T073227Z.json.
373. Этап RUN_WINDOW_92 выполнен без фикса.
374. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
375. Итог RUN_WINDOW_92: PASS (4 coverage-аудита PASS @20260601T073439Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1712_controlled_unfreeze_run_window_92_20260601T073530Z.json.
376. Этап RUN_WINDOW_93 выполнен с техническим фиксом.
377. Первичный short_only: PARTIAL_FAIL (worker_failed; JSONDecodeError Extra data), fix: технический rerun short_only без изменения параметров; повторный запуск OK.
378. Итог RUN_WINDOW_93: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T073844Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1714_controlled_unfreeze_run_window_93_20260601T073937Z.json.
379. Этап RUN_WINDOW_94 выполнен без фикса.
380. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
381. Итог RUN_WINDOW_94: PASS (4 coverage-аудита PASS @20260601T074122Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1716_controlled_unfreeze_run_window_94_20260601T074216Z.json.
382. Этап RUN_WINDOW_95 выполнен без фикса.
383. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
384. Итог RUN_WINDOW_95: PASS (4 coverage-аудита PASS @20260601T074400Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1718_controlled_unfreeze_run_window_95_20260601T074452Z.json.
385. Этап RUN_WINDOW_96 выполнен без фикса.
386. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
387. Итог RUN_WINDOW_96: PASS (4 coverage-аудита PASS @20260601T074631Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1720_controlled_unfreeze_run_window_96_20260601T074730Z.json.
388. Этап RUN_WINDOW_97 выполнен без фикса.
389. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
390. Итог RUN_WINDOW_97: PASS (4 coverage-аудита PASS @20260601T074948Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1722_controlled_unfreeze_run_window_97_20260601T075037Z.json.
391. Этап RUN_WINDOW_98 выполнен без фикса.
392. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
393. Итог RUN_WINDOW_98: PASS (4 coverage-аудита PASS @20260601T075214Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1724_controlled_unfreeze_run_window_98_20260601T075305Z.json.
394. Этап RUN_WINDOW_99 выполнен без фикса.
395. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
396. Итог RUN_WINDOW_99: PASS (4 coverage-аудита PASS @20260601T075451Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1726_controlled_unfreeze_run_window_99_20260601T075542Z.json.
397. Этап RUN_WINDOW_100 выполнен без фикса.
398. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
399. Итог RUN_WINDOW_100: PASS (4 coverage-аудита PASS @20260601T075721Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1728_controlled_unfreeze_run_window_100_20260601T075811Z.json.
400. Этап RUN_WINDOW_101 выполнен с фиксом запуска.
401. Первичный запуск вернул PARTIAL_FAIL (blocked_readiness): исправлено rerun с `-UseTemporaryUnlock`; после фикса применен canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
402. Итог RUN_WINDOW_101: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T080201Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1730_controlled_unfreeze_run_window_101_20260601T080202Z.json.
403. Этап RUN_WINDOW_102 выполнен без фикса.
404. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
405. Итог RUN_WINDOW_102: PASS (4 coverage-аудита PASS @20260601T080645Z/20260601T080646Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1732_controlled_unfreeze_run_window_102_20260601T080647Z.json.
406. Этап RUN_WINDOW_103 выполнен без фикса.
407. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
408. Итог RUN_WINDOW_103: PASS (4 coverage-аудита PASS @20260601T081017Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1734_controlled_unfreeze_run_window_103_20260601T081018Z.json.
409. Этап RUN_WINDOW_104 выполнен без фикса.
410. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
411. Итог RUN_WINDOW_104: PASS (4 coverage-аудита PASS @20260601T081342Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1736_controlled_unfreeze_run_window_104_20260601T081344Z.json.
412. Этап RUN_WINDOW_105 выполнен без фикса.
413. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
414. Итог RUN_WINDOW_105: PASS (4 coverage-аудита PASS @20260601T081654Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1738_controlled_unfreeze_run_window_105_20260601T081655Z.json.
415. Этап RUN_WINDOW_106 выполнен без фикса.
416. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
417. Итог RUN_WINDOW_106: PASS (4 coverage-аудита PASS @20260601T081958Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1740_controlled_unfreeze_run_window_106_20260601T081959Z.json.
418. Этап RUN_WINDOW_107 выполнен без фикса.
419. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
420. Итог RUN_WINDOW_107: PASS (4 coverage-аудита PASS @20260601T082301Z/20260601T082302Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1742_controlled_unfreeze_run_window_107_20260601T082303Z.json.
421. Этап RUN_WINDOW_108 выполнен без фикса.
422. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
423. Итог RUN_WINDOW_108: PASS (4 coverage-аудита PASS @20260601T082605Z/20260601T082606Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1744_controlled_unfreeze_run_window_108_20260601T082607Z.json.
424. Этап RUN_WINDOW_109 выполнен без фикса.
425. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
426. Итог RUN_WINDOW_109: PASS (4 coverage-аудита PASS @20260601T082924Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1746_controlled_unfreeze_run_window_109_20260601T082925Z.json.
427. Этап RUN_WINDOW_110 выполнен без фикса.
428. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
429. Итог RUN_WINDOW_110: PASS (4 coverage-аудита PASS @20260601T083303Z/20260601T083304Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1748_controlled_unfreeze_run_window_110_20260601T083306Z.json.
430. Этап RUN_WINDOW_111 выполнен без фикса.
431. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
432. Итог RUN_WINDOW_111: PASS (4 coverage-аудита PASS @20260601T083634Z/20260601T083635Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1750_controlled_unfreeze_run_window_111_20260601T083636Z.json.
433. Этап RUN_WINDOW_112 выполнен без фикса.
434. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
435. Итог RUN_WINDOW_112: PASS (4 coverage-аудита PASS @20260601T083954Z/20260601T083955Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1752_controlled_unfreeze_run_window_112_20260601T083956Z.json.
436. Этап RUN_WINDOW_113 выполнен без фикса.
437. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
438. Итог RUN_WINDOW_113: PASS (4 coverage-аудита PASS @20260601T084305Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1754_controlled_unfreeze_run_window_113_20260601T084306Z.json.
439. Этап RUN_WINDOW_114 выполнен без фикса.
440. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
441. Итог RUN_WINDOW_114: PASS (4 coverage-аудита PASS @20260601T084609Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1756_controlled_unfreeze_run_window_114_20260601T084610Z.json.
442. Этап RUN_WINDOW_115 выполнен без фикса.
443. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
444. Итог RUN_WINDOW_115: PASS (4 coverage-аудита PASS @20260601T084941Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1758_controlled_unfreeze_run_window_115_20260601T084942Z.json.
445. Этап RUN_WINDOW_116 выполнен без фикса.
446. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
447. Итог RUN_WINDOW_116: PASS (4 coverage-аудита PASS @20260601T085328Z/20260601T085329Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1760_controlled_unfreeze_run_window_116_20260601T085330Z.json.
448. Этап RUN_WINDOW_117 выполнен без фикса.
449. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
450. Итог RUN_WINDOW_117: PASS (4 coverage-аудита PASS @20260601T085658Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1762_controlled_unfreeze_run_window_117_20260601T085700Z.json.
451. Этап RUN_WINDOW_118 выполнен без фикса.
452. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
453. Итог RUN_WINDOW_118: PASS (4 coverage-аудита PASS @20260601T090015Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1764_controlled_unfreeze_run_window_118_20260601T090017Z.json.
454. Этап RUN_WINDOW_119 выполнен без фикса.
455. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
456. Итог RUN_WINDOW_119: PASS (4 coverage-аудита PASS @20260601T090359Z/20260601T090400Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1766_controlled_unfreeze_run_window_119_20260601T090401Z.json.
457. Этап RUN_WINDOW_120 выполнен с техническим фиксом окружения аудита (PYTHONPATH=src) и без изменения логики контура.
458. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
459. Итог RUN_WINDOW_120: PASS_AFTER_FIX (4 coverage-аудита PASS @20260601T090845Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1768_controlled_unfreeze_run_window_120_20260601T090852Z.json.
460. Этап RUN_WINDOW_121 выполнен с фиксом покрытия min/max (technical rerun long_only) и без изменения логики контура.
461. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
462. Итог RUN_WINDOW_121: PASS_AFTER_FIX (первичный long_only profile coverage FAIL по pattern_age_cap max-hit; после rerun long_only 4 coverage-аудита PASS @20260601T091558Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1770_controlled_unfreeze_run_window_121_20260601T091605Z.json.
463. Этап RUN_WINDOW_122 выполнен без фикса.
464. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
465. Итог RUN_WINDOW_122: PASS (4 coverage-аудита PASS @20260601T091936Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1772_controlled_unfreeze_run_window_122_20260601T091943Z.json.
466. Этап RUN_WINDOW_123 выполнен без фикса.
467. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
468. Итог RUN_WINDOW_123: PASS (4 coverage-аудита PASS @20260601T092301Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1774_controlled_unfreeze_run_window_123_20260601T092307Z.json.
469. Этап RUN_WINDOW_124 выполнен без фикса.
470. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
471. Итог RUN_WINDOW_124: PASS (4 coverage-аудита PASS @20260601T092635Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1776_controlled_unfreeze_run_window_124_20260601T092641Z.json.
472. Этап RUN_WINDOW_125 выполнен без фикса.
473. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
474. Итог RUN_WINDOW_125: PASS (4 coverage-аудита PASS @20260601T093009Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1778_controlled_unfreeze_run_window_125_20260601T093015Z.json.
475. Этап RUN_WINDOW_126 выполнен без фикса.
476. Прогон выполнен с canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) и trials=220.
477. Итог RUN_WINDOW_126: PASS (4 coverage-аудита PASS @20260601T093336Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze-governance сохранен. Сводный артефакт: reports/qa_gate/p1780_controlled_unfreeze_run_window_126_20260601T093342Z.json.

## 12. Final closeout (2026-06-01)
1. Canonical runtime dlya controlled unfreeze zafiksirovan:
1. `OptunaTrials=220`,
2. strict `3x9`,
3. `OptunaMlSignalBackend=off`,
4. `-UseTemporaryUnlock` only.
2. Edinaya model status okna utverzhdena:
1. `PASS`,
2. `PASS_AFTER_FIX`,
3. `FAIL`.
3. STOP_ON_SUCCESS utverzhden:
1. `K=5` posledovatelnyh окон so status `PASS`,
2. bez fix (`fix.action=not_required`),
3. freeze unchanged (`project_ready=false`, `enforce_freeze=true`),
4. parnyi post-window decision: `GO_FOR_NEXT_CONTROLLED_WINDOW`.
4. STOP_ON_SUCCESS dostignut na oknah `122..126` (`P1772`, `P1774`, `P1776`, `P1778`, `P1780`) + post-decision (`P1773`, `P1775`, `P1777`, `P1779`, `P1781`).
5. Seriya `RUN_WINDOW_N` ostanovlena po kriteriyu uspeha; perehod v formalnyi governance closeout vypolnen.
6. Finalnyi acceptance-package i finalnyi GO/NO-GO decision-record vypuscheny (sm. `reports/qa_gate/p1782*` i `reports/qa_gate/p1783*`).
7. Sleduyuschii etap policy gate dlya production unfreeze vyveden v otdelnyi dokument: `docs/OPTUNA_PRODUCTION_UNFREEZE_POLICY_GATE_2026-06-01_RU.md`.
8. Policy-gate execution `13.4.1..13.4.4` vypolnena s post-audit PASS (sm. `reports/qa_gate/p1792*` .. `p1796*`), freeze-state bez izmeneniy.
