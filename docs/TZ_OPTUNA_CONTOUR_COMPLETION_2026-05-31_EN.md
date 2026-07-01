# TZ: Optuna Calibration Contour Completion (2026-05-31)

Date: 2026-05-31  
Contour: only `Optuna/APTuna` inside `MLbotNav`  
Constraint: do not touch `ML runtime`; do not use ML signals in the Optuna contour

## 1. Stage Goal
1. Bring the calibration contour to a technically stable, bug-free operational state.
2. Confirm that all calibratable parameters are actually included in the search process.
3. Ensure verifiability and reproducibility: every step is backed by artifacts and audit logs.
4. Under `1d train / 1d test` and `1m` mode, do not require stable profitability as the main criterion of this stage.

## 2. Hard Scope (MUST)
1. Work only in `C:\Users\007\Desktop\MLbotNav`.
2. Active contour scope: `APTuna`, `src/mlbotnav`, `configs`, `docs`, `reports`.
3. ML isolation: `OptunaMlSignalBackend=off`.
4. No ML combos and no ML signals in the current Optuna contour.

## 3. Execution Mode
1. Window: one day for calibration + one day for run.
2. Timeframe: `1m`.
3. Compute mode: strict `3x9`.
4. Runs must be separated by mode: `long_only` and `short_only`.
5. Every step follows `single-change` (one intentional change per step).

## 4. Mandatory Calibration Requirements
1. Each module is calibrated separately: all calibratable module parameters from minimum to maximum.
2. Each feature is calibrated separately: all calibratable feature parameters from minimum to maximum.
3. Each hypothesis is calibrated separately: all calibratable hypothesis parameters from minimum to maximum.
4. Non-calibratable features are not removed from contour: they stay in runtime and are validated in integrated runs.
5. Grid taxonomy must exist and be maintained at three levels: `wide`, `medium`, `narrow`.

## 5. Definition of Done ("Contour Assembled" Stage)
1. Chain `S1 -> S2 -> S3 -> S4` runs without technical failures.
2. For all calibratable parameters, min and max hits are explicitly evidenced.
3. All active blocks/features/hypotheses participate in runtime.
4. Each step has the full artifact pack: checkpoint, worker logs, coverage report, `pip check`, `text_guard`, `readiness --show`, synchronized `ACTIVE_WORK_ITEMS` and `CHANGELOG`.
5. No mojibake/encoding corruption in active documents.

## 6. Audit Status as of 2026-05-31 (updated)
1. Confirmed inventory: `68` features (`56` calibratable, `12` non-calibratable), `20` calibratable hypotheses, `5` search-grid parameters, `27` profiles.
2. Confirmed runtime activation of 6 blocks.
3. `P0` is technically closed:
4. storage runs in postgres mode with no silent sqlite fallback;
5. `wide/medium/narrow` taxonomy is locked in runtime;
6. PASS artifacts exist for `min_hit/max_hit` on profile and search-grid coverage for both `long_only` and `short_only`.
7. `P1` for contour-assembly stage is closed:
8. base search-grid quintet PASS/FAIL report is present;
9. short-only gate override is unified in `thresholds.yaml`;
10. automatic append to registry/chronology is provided by `mlbotnav.docs_registry_append`.
11. Operational state: `READY_FOR_CONTROLLED_UNFREEZE` with governance freeze still active (`project_ready=false`, `enforce_freeze=true`).

## 7. Execution Priorities (strict order)
1. `P0-CLOSEOUT.1` Verify and package final contour artifacts into a single evidence bundle.
2. `P0-CLOSEOUT.2` Run acceptance passes for `long_only` and `short_only` under `1d train / 1d test`, `1m`, strict `3x9`.
3. `P0-CLOSEOUT.3` Perform mandatory post-run audit: chain, coverage, readiness, and mojibake checks.
4. `P0-CLOSEOUT.4` If deviations are found: immediate fix -> re-check -> re-freeze artifacts.
5. `P0-CLOSEOUT.5` Record each step in `ACTIVE_WORK_ITEMS_RU.md` and `CHANGELOG_CHRONOLOGY_RU.md` (append-only).
6. `P0-CLOSEOUT.6` After PASS: update final TZ status and prepare controlled-unfreeze execution window.

## 8. Readiness Criteria for Contour Go-Live
1. All `P0-CLOSEOUT` steps are closed with artifacts and post-fix rechecks where needed.
2. Mandatory technical audit has no critical findings: `S1 -> S2 -> S3 -> S4` PASS, coverage PASS, readiness checkpoint PASS.
3. ML contour isolation is confirmed across full A->I path (`OptunaMlSignalBackend=off`, no ML combos/signals).
4. No encoding corruption/mojibake in active documents.

## 9. Per-Step Execution Protocol (mandatory)
1. Audit/verification of the current step.
2. Mojibake/encoding check in touched files.
3. If issue found: immediate fix.
4. Re-verification after fix.
5. Append evidence into `ACTIVE + CHANGELOG`.

## 10. P0-CLOSEOUT Execution Progress (2026-05-31)
1. `P0-CLOSEOUT.1` DONE: artifact bundle verified, report `reports/qa_gate/p1524_p0_closeout_step1_artifact_bundle_audit_20260531T143007Z.json`.
2. `P0-CLOSEOUT.2` DONE: acceptance long/short completed, summary `reports/qa_gate/p1525_p0_closeout_step2_acceptance_audit_20260531T143713Z.json`.
3. `P0-CLOSEOUT.3` DONE: mandatory post-run audit PASS (`profile/search-grid coverage`, `pip check`, `text_guard`, `readiness --show`).
4. `P0-CLOSEOUT.4` DONE: profile coverage deviation fixed by increasing trials budget (`132 -> 220`), re-check PASS.
5. `P0-CLOSEOUT.5` DONE: entries appended to `ACTIVE_WORK_ITEMS_RU.md` (P1524, P1525) and `CHANGELOG_CHRONOLOGY_RU.md`.
6. `P0-CLOSEOUT.6` DONE: final status synchronized, report `reports/qa_gate/p1526_p0_closeout_step6_final_status_sync_20260531T143834Z.json`.

## 11. Controlled Unfreeze (window execution)
1. Stage RUN_WINDOW_1 completed.
2. Result: technical PASS (long/short launcher OK, all 4 coverage audits PASS, pip check PASS, text_guard PASS).
3. Freeze governance remained intact after the window: project_ready=false, enforce_freeze=true.
4. Consolidated artifact: reports/qa_gate/p1527_controlled_unfreeze_run_window_1_20260531T144558Z.json.
5. Stage RUN_WINDOW_2 completed with fix.
6. Initial audit: profile_coverage_short_only FAIL (missing max-hit on macd_signal_period), all other mandatory checks PASS.
7. Fix: increased short-only trials budget 220 -> 300 and reran short-only window.
8. Final RUN_WINDOW_2 status: PASS_AFTER_FIX, freeze governance preserved (project_ready=false, enforce_freeze=true).
9. Consolidated artifact: reports/qa_gate/p1529_controlled_unfreeze_run_window_2_20260531T145119Z.json.
10. Stage RUN_WINDOW_3 completed with no fix required.
11. Final RUN_WINDOW_3 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
12. Freeze governance preserved (project_ready=false, enforce_freeze=true).
13. Consolidated artifact: reports/qa_gate/p1531_controlled_unfreeze_run_window_3_20260531T145642Z.json.
14. Stage RUN_WINDOW_4 completed with no fix required.
15. Final RUN_WINDOW_4 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
16. Freeze governance preserved (project_ready=false, enforce_freeze=true).
17. Consolidated artifact: reports/qa_gate/p1534_controlled_unfreeze_run_window_4_20260531T150308Z.json.
18. Stage RUN_WINDOW_5 completed with no fix required.
19. Final RUN_WINDOW_5 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
20. Freeze governance preserved (project_ready=false, enforce_freeze=true).
21. Consolidated artifact: reports/qa_gate/p1536_controlled_unfreeze_run_window_5_20260531T150725Z.json.
22. Stage RUN_WINDOW_6 completed with no fix required.
23. Final RUN_WINDOW_6 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
24. Freeze governance preserved (project_ready=false, enforce_freeze=true).
25. Consolidated artifact: reports/qa_gate/p1538_controlled_unfreeze_run_window_6_20260531T151102Z.json.
26. Stage RUN_WINDOW_7 completed with no fix required.
27. Final RUN_WINDOW_7 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
28. Freeze governance preserved (project_ready=false, enforce_freeze=true).
29. Consolidated artifact: reports/qa_gate/p1540_controlled_unfreeze_run_window_7_20260531T181511Z.json.
30. Stage RUN_WINDOW_8 completed with no fix required.
31. Final RUN_WINDOW_8 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
32. Freeze governance preserved (project_ready=false, enforce_freeze=true).
33. Consolidated artifact: reports/qa_gate/p1542_controlled_unfreeze_run_window_8_20260531T181921Z.json.
34. Stage RUN_WINDOW_9 completed with no fix required.
35. Final RUN_WINDOW_9 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
36. Freeze governance preserved (project_ready=false, enforce_freeze=true).
37. Consolidated artifact: reports/qa_gate/p1544_controlled_unfreeze_run_window_9_20260531T182328Z.json.
38. Stage RUN_WINDOW_10 completed with no fix required.
39. Final RUN_WINDOW_10 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
40. Freeze governance preserved (project_ready=false, enforce_freeze=true).
41. Consolidated artifact: reports/qa_gate/p1546_controlled_unfreeze_run_window_10_20260531T182943Z.json.
42. Stage RUN_WINDOW_11 completed with no fix required.
43. Final RUN_WINDOW_11 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
44. Freeze governance preserved (project_ready=false, enforce_freeze=true).
45. Consolidated artifact: reports/qa_gate/p1548_controlled_unfreeze_run_window_11_20260531T183311Z.json.
46. Stage RUN_WINDOW_12 completed with fix.
47. Initial audit: profile_coverage_long_only FAIL (missing max-hit on threshold_fine); other mandatory checks were clean.
48. Fix: increased long_only trials budget 220 -> 300 and reran long_only; repeated audits PASS.
49. Final RUN_WINDOW_12 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
50. Consolidated artifact: reports/qa_gate/p1550_controlled_unfreeze_run_window_12_20260531T183748Z.json.
51. Stage RUN_WINDOW_13 completed with no fix required.
52. Final RUN_WINDOW_13 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
53. Freeze governance preserved (project_ready=false, enforce_freeze=true).
54. Consolidated artifact: reports/qa_gate/p1552_controlled_unfreeze_run_window_13_20260531T184110Z.json.
55. Stage RUN_WINDOW_14 completed with no fix required.
56. Final RUN_WINDOW_14 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
57. Freeze governance preserved (project_ready=false, enforce_freeze=true).
58. Consolidated artifact: reports/qa_gate/p1554_controlled_unfreeze_run_window_14_20260531T184501Z.json.
59. Stage RUN_WINDOW_15 completed with no fix required.
60. Final RUN_WINDOW_15 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
61. Freeze governance preserved (project_ready=false, enforce_freeze=true).
62. Consolidated artifact: reports/qa_gate/p1556_controlled_unfreeze_run_window_15_20260531T184827Z.json.
63. Stage RUN_WINDOW_16 completed with fix.
64. Initial audit: profile_coverage_short_only FAIL (missing max-hit on pattern_age_cap).
65. Fix #1: short_only trials 220 -> 300; repeated audit produced a new FAIL (ratio_pattern max-hit).
66. Fix #2: short_only trials 300 -> 400; repeated audit PASS.
67. Final RUN_WINDOW_16 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
68. Consolidated artifact: reports/qa_gate/p1558_controlled_unfreeze_run_window_16_20260531T185436Z.json.
69. Stage RUN_WINDOW_17 completed with fix.
70. Initial short_only run returned PARTIAL_FAIL (worker_failed) with empty error log; technical short_only rerun executed.
71. After rerun, short_only profile coverage still FAILed (pattern_age_cap min/max hit coverage).
72. Fix: increased short_only trials 220 -> 400; repeated audit PASS.
73. Final RUN_WINDOW_17 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
74. Consolidated artifact: reports/qa_gate/p1560_controlled_unfreeze_run_window_17_20260531T190050Z.json.
75. Stage RUN_WINDOW_18 completed with no fix required.
76. Final RUN_WINDOW_18 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
77. Freeze governance preserved (project_ready=false, enforce_freeze=true).
78. Consolidated artifact: reports/qa_gate/p1562_controlled_unfreeze_run_window_18_20260531T190428Z.json.
79. Stage RUN_WINDOW_19 completed with fix.
80. Initial short_only run returned PARTIAL_FAIL (worker_failed/JSONDecodeError); technical short_only rerun executed.
81. After rerun, short_only profile coverage FAILed (pattern_age_cap max-hit coverage).
82. Fix: increased short_only trials 220 -> 300; repeated audit PASS.
83. Final RUN_WINDOW_19 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
84. Consolidated artifact: reports/qa_gate/p1564_controlled_unfreeze_run_window_19_20260531T191036Z.json.
85. Stage RUN_WINDOW_20 completed with fix.
86. Initial audit: profile_coverage_short_only FAIL (missing max-hit on macd_slow_period).
87. Fix: increased short_only trials 220 -> 300; repeated audit PASS.
88. Final RUN_WINDOW_20 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
89. Consolidated artifact: reports/qa_gate/p1566_controlled_unfreeze_run_window_20_20260531T191523Z.json.
90. Stage RUN_WINDOW_21 completed with no fix required.
91. Final RUN_WINDOW_21 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
92. Freeze governance preserved (project_ready=false, enforce_freeze=true).
93. Consolidated artifact: reports/qa_gate/p1568_controlled_unfreeze_run_window_21_20260531T191847Z.json.
94. Stage RUN_WINDOW_22 completed with no fix required.
95. Final RUN_WINDOW_22 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS).
96. Freeze governance preserved (project_ready=false, enforce_freeze=true).
97. Consolidated artifact: reports/qa_gate/p1570_controlled_unfreeze_run_window_22_20260531T192208Z.json.
98. Stage RUN_WINDOW_23 completed with fix.
99. Initial audit: profile_coverage_short_only FAIL (missing min-hit on doji_threshold).
100. Fix: increased short_only trials 220 -> 300; repeated audit PASS.
101. Final RUN_WINDOW_23 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
102. Consolidated artifact: reports/qa_gate/p1572_controlled_unfreeze_run_window_23_20260531T192641Z.json.
103. Stage RUN_WINDOW_24 completed with fix.
104. Initial audit: profile_coverage_short_only FAIL (missing min-hit on doji_threshold).
105. Fix #1: short_only trials 220 -> 300; repeated audit produced new FAIL (macd_slow_period max-hit).
106. Fix #2: short_only trials 300 -> 400; repeated audit PASS.
107. Final RUN_WINDOW_24 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
108. Consolidated artifact: reports/qa_gate/p1574_controlled_unfreeze_run_window_24_20260531T193247Z.json.
109. Stage RUN_WINDOW_25 completed with no fix required.
110. Final RUN_WINDOW_25 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
111. Consolidated artifact: reports/qa_gate/p1576_controlled_unfreeze_run_window_25_20260531T193655Z.json.
112. Stage RUN_WINDOW_26 completed with no fix required.
113. Final RUN_WINDOW_26 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
114. Consolidated artifact: reports/qa_gate/p1578_controlled_unfreeze_run_window_26_20260531T194201Z.json.
115. Stage RUN_WINDOW_27 completed with no fix required.
116. Final RUN_WINDOW_27 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
117. Consolidated artifact: reports/qa_gate/p1580_controlled_unfreeze_run_window_27_20260531T194552Z.json.
118. Stage RUN_WINDOW_28 completed with fix.
119. Initial audit: profile_coverage_long_only FAIL (missing max-hit on macd_slow_period).
120. Fix: increased long_only trials 220 -> 300; repeated audit PASS.
121. Final RUN_WINDOW_28 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
122. Consolidated artifact: reports/qa_gate/p1582_controlled_unfreeze_run_window_28_20260601T024714Z.json.
123. Stage RUN_WINDOW_29 completed with no fix required.
124. Final RUN_WINDOW_29 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
125. Consolidated artifact: reports/qa_gate/p1584_controlled_unfreeze_run_window_29_20260601T025107Z.json.
126. Stage RUN_WINDOW_30 completed with no fix required.
127. Final RUN_WINDOW_30 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
128. Consolidated artifact: reports/qa_gate/p1586_controlled_unfreeze_run_window_30_20260601T025448Z.json.
129. Stage RUN_WINDOW_31 completed with no fix required.
130. Final RUN_WINDOW_31 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
131. Consolidated artifact: reports/qa_gate/p1588_controlled_unfreeze_run_window_31_20260601T025816Z.json.
132. Stage RUN_WINDOW_32 completed with no fix required.
133. Final RUN_WINDOW_32 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
134. Consolidated artifact: reports/qa_gate/p1590_controlled_unfreeze_run_window_32_20260601T030128Z.json.
135. Stage RUN_WINDOW_33 completed with fix.
136. Initial audit: profile_coverage_long_only FAIL (missing max-hit on threshold_fine).
137. Fix: increased long_only trials 220 -> 300; repeated audit PASS.
138. Final RUN_WINDOW_33 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
139. Consolidated artifact: reports/qa_gate/p1592_controlled_unfreeze_run_window_33_20260601T030607Z.json.
140. Stage RUN_WINDOW_34 completed with no fix required.
141. Final RUN_WINDOW_34 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
142. Consolidated artifact: reports/qa_gate/p1594_controlled_unfreeze_run_window_34_20260601T030942Z.json.
143. Stage RUN_WINDOW_35 completed with no fix required.
144. Final RUN_WINDOW_35 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
145. Consolidated artifact: reports/qa_gate/p1596_controlled_unfreeze_run_window_35_20260601T031316Z.json.
146. Stage RUN_WINDOW_36 completed with no fix required.
147. Final RUN_WINDOW_36 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
148. Consolidated artifact: reports/qa_gate/p1598_controlled_unfreeze_run_window_36_20260601T031645Z.json.
149. Stage RUN_WINDOW_37 completed with fix.
150. Initial audit: profile_coverage_short_only FAIL (missing max-hit on threshold_fine).
151. Fix: increased short_only trials 220 -> 300; repeated audit PASS.
152. Final RUN_WINDOW_37 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
153. Consolidated artifact: reports/qa_gate/p1600_controlled_unfreeze_run_window_37_20260601T032139Z.json.
154. Stage RUN_WINDOW_38 completed with fix.
155. Initial long_only run returned PARTIAL_FAIL (worker_failed); technical long_only rerun executed.
156. Recheck after rerun: all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS.
157. Final RUN_WINDOW_38 status: PASS_AFTER_FIX, freeze governance preserved.
158. Consolidated artifact: reports/qa_gate/p1602_controlled_unfreeze_run_window_38_20260601T032646Z.json.
159. Stage RUN_WINDOW_39 completed with no fix required.
160. Final RUN_WINDOW_39 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
161. Consolidated artifact: reports/qa_gate/p1604_controlled_unfreeze_run_window_39_20260601T033028Z.json.
162. Stage RUN_WINDOW_40 completed with no fix required.
163. Final RUN_WINDOW_40 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
164. Consolidated artifact: reports/qa_gate/p1606_controlled_unfreeze_run_window_40_20260601T033419Z.json.
165. Stage RUN_WINDOW_41 completed with fix.
166. Initial short_only run returned PARTIAL_FAIL (worker_failed); technical short_only rerun executed.
167. Recheck after rerun: all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS.
168. Final RUN_WINDOW_41 status: PASS_AFTER_FIX, freeze governance preserved.
169. Consolidated artifact: reports/qa_gate/p1608_controlled_unfreeze_run_window_41_20260601T033900Z.json.
170. Stage RUN_WINDOW_42 completed with no fix required.
171. Final RUN_WINDOW_42 status: PASS (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
172. Consolidated artifact: reports/qa_gate/p1610_controlled_unfreeze_run_window_42_20260601T034306Z.json.
173. Stage RUN_WINDOW_43 completed with fix.
174. Initial audit: profile_coverage_short_only FAIL (missing max-hit on macd_slow_period).
175. Fix: increased short_only trials 220 -> 300; repeated audit PASS.
176. Final RUN_WINDOW_43 status: PASS_AFTER_FIX (all 4 coverage audits PASS, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
177. Consolidated artifact: reports/qa_gate/p1612_controlled_unfreeze_run_window_43_20260601T034820Z.json.
178. Stage RUN_WINDOW_44 completed with a two-step fix.
179. Initial audits: profile_coverage_long_only FAIL (`pattern_age_cap`), profile_coverage_short_only FAIL (`return_lookback`), search_grid_coverage_short_only FAIL.
180. Fix #1: trials 220 -> 300 for both long_only and short_only; profile audits turned PASS, but search_grid_coverage long/short remained FAIL.
181. Fix #2: enforced canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) and reran long/short.
182. Final RUN_WINDOW_44 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T040000Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
183. Consolidated artifact: reports/qa_gate/p1614_controlled_unfreeze_run_window_44_20260601T040014Z.json.
184. Stage RUN_WINDOW_45 completed with no fix required.
185. Run executed with canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) and trials=220.
186. Final RUN_WINDOW_45 status: PASS (all 4 coverage audits PASS @20260601T041149Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
187. Consolidated artifact: reports/qa_gate/p1616_controlled_unfreeze_run_window_45_20260601T041155Z.json.
188. Stage RUN_WINDOW_46 completed with no fix required.
189. Run executed with canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) and trials=220.
190. Final RUN_WINDOW_46 status: PASS (all 4 coverage audits PASS @20260601T041542Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
191. Consolidated artifact: reports/qa_gate/p1618_controlled_unfreeze_run_window_46_20260601T041549Z.json.
192. Stage RUN_WINDOW_47 completed with no fix required.
193. Run executed with canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) and trials=220.
194. Final RUN_WINDOW_47 status: PASS (all 4 coverage audits PASS @20260601T041942Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
195. Consolidated artifact: reports/qa_gate/p1620_controlled_unfreeze_run_window_47_20260601T041949Z.json.
196. Stage RUN_WINDOW_48 completed with no fix required.
197. Run executed with canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) and trials=220.
198. Final RUN_WINDOW_48 status: PASS (all 4 coverage audits PASS @20260601T042315Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
199. Consolidated artifact: reports/qa_gate/p1622_controlled_unfreeze_run_window_48_20260601T042323Z.json.
200. Stage RUN_WINDOW_49 completed with fix.
201. Initial audit: profile_coverage_short_only FAIL (missing min/max hits on `pattern_age_cap`, `period_standard`, `threshold_fine`).
202. Fix: reran short_only with trials 220 -> 300; repeated full coverage block PASS.
203. Final RUN_WINDOW_49 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T042818Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
204. Consolidated artifact: reports/qa_gate/p1624_controlled_unfreeze_run_window_49_20260601T042825Z.json.
205. Stage RUN_WINDOW_50 completed with no fix required.
206. Run executed with canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) and trials=220.
207. Final RUN_WINDOW_50 status: PASS (all 4 coverage audits PASS @20260601T044209Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
208. Consolidated artifact: reports/qa_gate/p1626_controlled_unfreeze_run_window_50_20260601T044217Z.json.
209. Decision package sync for RUN_WINDOW_50 completed (`docs/OPTUNA_UNFREEZE_DECISION_PACKAGE_2026-05-31_RU.md`).
210. Mandatory post-fix re-audit after doc update: `text_guard PASS` (`reports/qa_gate/recovery_r5_text_guard_20260601T044448Z.json`), `readiness --show PASS` (`reports/readiness/readiness_check_20260601T044448Z.json`), `pip check PASS`.
211. Final P1628 step status: PASS, freeze governance preserved (`project_ready=false`, `enforce_freeze=true`).
212. Consolidated P1628 artifact: reports/qa_gate/p1628_post_window50_docsync_audit_20260601T044518Z.json.
213. Stage RUN_WINDOW_51 completed with fix.
214. Initial audit: `profile_coverage_long_only FAIL` (missing min-hit on `density_bin_pct`).
215. Fix: reran `long_only` with trials `220 -> 300`; repeated audit PASS.
216. Final RUN_WINDOW_51 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T045037Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
217. Consolidated artifact: reports/qa_gate/p1629_controlled_unfreeze_run_window_51_20260601T045038Z.json.
218. Stage RUN_WINDOW_52 completed with no fix required.
219. Run executed with canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) and trials=220.
220. Final RUN_WINDOW_52 status: PASS (all 4 coverage audits PASS @20260601T045432Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
221. Consolidated artifact: reports/qa_gate/p1631_controlled_unfreeze_run_window_52_20260601T045433Z.json.
222. Stage RUN_WINDOW_53 completed with no fix required.
223. Run executed with canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) and trials=220.
224. Final RUN_WINDOW_53 status: PASS (all 4 coverage audits PASS @20260601T045810Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
225. Consolidated artifact: reports/qa_gate/p1633_controlled_unfreeze_run_window_53_20260601T045810Z.json.
226. Stage RUN_WINDOW_54 completed with no fix required.
227. Run executed with canonical min/max quintet (`HorizonsGrid=1,20`, `PLongGrid=0.52,0.80`, `PShortGrid=0.20,0.48`, `MinExpectedMoveGrid=0.0005,0.01`, `NotionalUsdGrid=5,100`) and trials=220.
228. Final RUN_WINDOW_54 status: PASS (all 4 coverage audits PASS @20260601T050156Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
229. Consolidated artifact: reports/qa_gate/p1635_controlled_unfreeze_run_window_54_20260601T050157Z.json.
230. Stage RUN_WINDOW_55 completed with fix.
231. Initial audit: `profile_coverage_short_only FAIL` (missing max-hit on `pattern_age_cap`).
232. Fix: reran `short_only` with trials `220 -> 300`; repeated audit PASS.
233. Final RUN_WINDOW_55 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T050712Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
234. Consolidated artifact: reports/qa_gate/p1637_controlled_unfreeze_run_window_55_20260601T050713Z.json.
235. Stage RUN_WINDOW_56 completed with no fix required.
236. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
237. Final RUN_WINDOW_56 status: PASS (all 4 coverage audits PASS @20260601T051105Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
238. Consolidated artifact: reports/qa_gate/p1639_controlled_unfreeze_run_window_56_20260601T051105Z.json.
239. Stage RUN_WINDOW_57 completed with no fix required.
240. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
241. Final RUN_WINDOW_57 status: PASS (all 4 coverage audits PASS @20260601T051420Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
242. Consolidated artifact: reports/qa_gate/p1641_controlled_unfreeze_run_window_57_20260601T051421Z.json.
243. Stage RUN_WINDOW_58 completed with no fix required.
244. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
245. Final RUN_WINDOW_58 status: PASS (all 4 coverage audits PASS @20260601T051741Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
246. Consolidated artifact: reports/qa_gate/p1643_controlled_unfreeze_run_window_58_20260601T051742Z.json.
247. Stage RUN_WINDOW_59 completed with fix.
248. Initial audit: profile_coverage_long_only FAIL (missing max-hit on atio_pattern).
249. Fix: reran long_only with trials 220 -> 300; repeated audit PASS.
250. Final RUN_WINDOW_59 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T052252Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
251. Consolidated artifact: reports/qa_gate/p1645_controlled_unfreeze_run_window_59_20260601T052252Z.json.
252. Stage RUN_WINDOW_60 completed with no fix required.
253. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
254. Final RUN_WINDOW_60 status: PASS (all 4 coverage audits PASS @20260601T052646Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
255. Consolidated artifact: reports/qa_gate/p1647_controlled_unfreeze_run_window_60_20260601T052647Z.json.
256. Stage RUN_WINDOW_61 completed with fix.
257. Initial audit: profile_coverage_short_only FAIL (missing min-hit on density_window_long).
258. Fix: reran short_only with trials 220 -> 300; repeated audit PASS.
259. Final RUN_WINDOW_61 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T053148Z/20260601T053149Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
260. Consolidated artifact: reports/qa_gate/p1649_controlled_unfreeze_run_window_61_20260601T053149Z.json.
261. Stage RUN_WINDOW_62 completed with no fix required.
262. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
263. Final RUN_WINDOW_62 status: PASS (all 4 coverage audits PASS @20260601T053522Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
264. Consolidated artifact: reports/qa_gate/p1651_controlled_unfreeze_run_window_62_20260601T053522Z.json.
265. Stage RUN_WINDOW_63 completed with no fix required.
266. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
267. Final RUN_WINDOW_63 status: PASS (all 4 coverage audits PASS @20260601T053848Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
268. Consolidated artifact: reports/qa_gate/p1653_controlled_unfreeze_run_window_63_20260601T053848Z.json.
269. Stage RUN_WINDOW_64 completed with two-step fix.
270. Initial audit: profile_coverage_long_only FAIL (missing max-hit on threshold_fine).
271. Fix #1: reran long_only with trials 220 -> 300; repeated audit produced new FAIL (macd_slow_period max-hit).
272. Fix #2: reran long_only with trials 300 -> 400; repeated audit PASS.
273. Final RUN_WINDOW_64 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T054524Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
274. Consolidated artifact: reports/qa_gate/p1655_controlled_unfreeze_run_window_64_20260601T054525Z.json.
275. Stage RUN_WINDOW_65 completed with no fix required.
276. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
277. Final RUN_WINDOW_65 status: PASS (all 4 coverage audits PASS @20260601T055059Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
278. Consolidated artifact: reports/qa_gate/p1657_controlled_unfreeze_run_window_65_20260601T055122Z.json.

279. Stage RUN_WINDOW_66 completed with no fix required.
280. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
281. Final RUN_WINDOW_66 status: PASS (all 4 coverage audits PASS @20260601T055648Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
282. Consolidated artifact: reports/qa_gate/p1660_controlled_unfreeze_run_window_66_20260601T055700Z.json.
283. Stage RUN_WINDOW_67 completed with no fix required.
284. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
285. Final RUN_WINDOW_67 status: PASS (all 4 coverage audits PASS @20260601T060014Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
286. Consolidated artifact: reports/qa_gate/p1662_controlled_unfreeze_run_window_67_20260601T060025Z.json.
287. Stage RUN_WINDOW_68 completed with no fix required.
288. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
289. Final RUN_WINDOW_68 status: PASS (all 4 coverage audits PASS @20260601T060342Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
290. Consolidated artifact: reports/qa_gate/p1664_controlled_unfreeze_run_window_68_20260601T060355Z.json.
291. Stage RUN_WINDOW_69 completed with two-step fix.
292. Initial audit: profile_coverage_long_only FAIL (missing max-hit on macd_slow_period).
293. Fix #1: reran long_only with trials 220 -> 300; repeated long profile coverage audit remained FAIL.
294. Fix #2: reran long_only with trials 300 -> 400; repeated audit PASS.
295. Final RUN_WINDOW_69 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T061030Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
296. Consolidated artifact: reports/qa_gate/p1666_controlled_unfreeze_run_window_69_20260601T061040Z.json.
297. Stage RUN_WINDOW_70 completed with no fix required.
298. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
299. Final RUN_WINDOW_70 status: PASS (all 4 coverage audits PASS @20260601T061416Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
300. Consolidated artifact: reports/qa_gate/p1668_controlled_unfreeze_run_window_70_20260601T061425Z.json.
301. Stage RUN_WINDOW_71 completed with fix.
302. Initial audit: profile_coverage_long_only FAIL (missing max-hit on pattern_age_cap).
303. Fix: reran long_only with trials 220 -> 300; repeated audit PASS.
304. Final RUN_WINDOW_71 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T061945Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
305. Consolidated artifact: reports/qa_gate/p1670_controlled_unfreeze_run_window_71_20260601T061958Z.json.
306. Stage RUN_WINDOW_72 completed with no fix required.
307. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
308. Final RUN_WINDOW_72 status: PASS (all 4 coverage audits PASS @20260601T062333Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
309. Consolidated artifact: reports/qa_gate/p1672_controlled_unfreeze_run_window_72_20260601T062345Z.json.
310. Stage RUN_WINDOW_73 completed with technical fix.
311. Initial long_only launcher status: PARTIAL_FAIL (worker_failed).
312. Fix: technical long_only rerun without parameter changes; launcher status OK.
313. Final RUN_WINDOW_73 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T062740Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
314. Consolidated artifact: reports/qa_gate/p1674_controlled_unfreeze_run_window_73_20260601T062750Z.json.
315. Stage RUN_WINDOW_74 completed with no fix required.
316. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
317. Final RUN_WINDOW_74 status: PASS (all 4 coverage audits PASS @20260601T063107Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
318. Consolidated artifact: reports/qa_gate/p1676_controlled_unfreeze_run_window_74_20260601T063120Z.json.
319. Stage RUN_WINDOW_75 completed with fix.
320. Initial audit: profile_coverage_long_only FAIL (missing max-hit on pattern_age_cap).
321. Fix: reran long_only with trials 220 -> 300; repeated audit PASS.
322. Final RUN_WINDOW_75 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T063624Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
323. Consolidated artifact: reports/qa_gate/p1678_controlled_unfreeze_run_window_75_20260601T063638Z.json.
324. Stage RUN_WINDOW_76 completed with no fix required.
325. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
326. Final RUN_WINDOW_76 status: PASS (all 4 coverage audits PASS @20260601T064039Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved.
327. Consolidated artifact: reports/qa_gate/p1680_controlled_unfreeze_run_window_76_20260601T064050Z.json.
328. Stage RUN_WINDOW_77 completed with fix.
329. Initial audit: profile_coverage_long_only FAIL (missing max-hit on threshold_fine); fix: long_only rerun with correctly quoted grid parameters and trials increase 220 -> 300; repeated audit PASS.
330. Final RUN_WINDOW_77 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T064724Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1682_controlled_unfreeze_run_window_77_20260601T064857Z.json.
331. Stage RUN_WINDOW_78 completed with no fix required.
332. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
333. Final RUN_WINDOW_78 status: PASS (all 4 coverage audits PASS @20260601T065115Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1684_controlled_unfreeze_run_window_78_20260601T065207Z.json.
334. Stage RUN_WINDOW_79 completed with no fix required.
335. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
336. Final RUN_WINDOW_79 status: PASS (all 4 coverage audits PASS @20260601T065449Z/20260601T065450Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1686_controlled_unfreeze_run_window_79_20260601T065539Z.json.
337. Stage RUN_WINDOW_80 completed with no fix required.
338. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
339. Final RUN_WINDOW_80 status: PASS (all 4 coverage audits PASS @20260601T065730Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1688_controlled_unfreeze_run_window_80_20260601T065822Z.json.
340. Stage RUN_WINDOW_81 completed with no fix required.
341. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
342. Final RUN_WINDOW_81 status: PASS (all 4 coverage audits PASS @20260601T070035Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1690_controlled_unfreeze_run_window_81_20260601T070123Z.json.
343. Stage RUN_WINDOW_82 completed with no fix required.
344. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
345. Final RUN_WINDOW_82 status: PASS (all 4 coverage audits PASS @20260601T070341Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1692_controlled_unfreeze_run_window_82_20260601T070429Z.json.
346. Stage RUN_WINDOW_83 completed with no fix required.
347. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
348. Final RUN_WINDOW_83 status: PASS (all 4 coverage audits PASS @20260601T070659Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1694_controlled_unfreeze_run_window_83_20260601T070747Z.json.
349. Stage RUN_WINDOW_84 completed with no fix required.
350. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
351. Final RUN_WINDOW_84 status: PASS (all 4 coverage audits PASS @20260601T071003Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1696_controlled_unfreeze_run_window_84_20260601T071051Z.json.
352. Stage RUN_WINDOW_85 completed with no fix required.
353. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
354. Final RUN_WINDOW_85 status: PASS (all 4 coverage audits PASS @20260601T071312Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1698_controlled_unfreeze_run_window_85_20260601T071401Z.json.
355. Stage RUN_WINDOW_86 completed with no fix required.
356. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
357. Final RUN_WINDOW_86 status: PASS (all 4 coverage audits PASS @20260601T071610Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1700_controlled_unfreeze_run_window_86_20260601T071659Z.json.
358. Stage RUN_WINDOW_87 completed with no fix required.
359. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
360. Final RUN_WINDOW_87 status: PASS (all 4 coverage audits PASS @20260601T071910Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1702_controlled_unfreeze_run_window_87_20260601T071959Z.json.
361. Stage RUN_WINDOW_88 completed with no fix required.
362. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
363. Final RUN_WINDOW_88 status: PASS (all 4 coverage audits PASS @20260601T072213Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1704_controlled_unfreeze_run_window_88_20260601T072302Z.json.
364. Stage RUN_WINDOW_89 completed with no fix required.
365. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
366. Final RUN_WINDOW_89 status: PASS (all 4 coverage audits PASS @20260601T072511Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1706_controlled_unfreeze_run_window_89_20260601T072602Z.json.
367. Stage RUN_WINDOW_90 completed with no fix required.
368. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
369. Final RUN_WINDOW_90 status: PASS (all 4 coverage audits PASS @20260601T072821Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1708_controlled_unfreeze_run_window_90_20260601T072912Z.json.
370. Stage RUN_WINDOW_91 completed with no fix required.
371. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
372. Final RUN_WINDOW_91 status: PASS (all 4 coverage audits PASS @20260601T073134Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1710_controlled_unfreeze_run_window_91_20260601T073227Z.json.
373. Stage RUN_WINDOW_92 completed with no fix required.
374. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
375. Final RUN_WINDOW_92 status: PASS (all 4 coverage audits PASS @20260601T073439Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1712_controlled_unfreeze_run_window_92_20260601T073530Z.json.
376. Stage RUN_WINDOW_93 completed with technical fix.
377. Initial short_only run: PARTIAL_FAIL (worker_failed; JSONDecodeError Extra data), fix: technical short_only rerun with unchanged parameters; rerun OK.
378. Final RUN_WINDOW_93 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T073844Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1714_controlled_unfreeze_run_window_93_20260601T073937Z.json.
379. Stage RUN_WINDOW_94 completed with no fix required.
380. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
381. Final RUN_WINDOW_94 status: PASS (all 4 coverage audits PASS @20260601T074122Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1716_controlled_unfreeze_run_window_94_20260601T074216Z.json.
382. Stage RUN_WINDOW_95 completed with no fix required.
383. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
384. Final RUN_WINDOW_95 status: PASS (all 4 coverage audits PASS @20260601T074400Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1718_controlled_unfreeze_run_window_95_20260601T074452Z.json.
385. Stage RUN_WINDOW_96 completed with no fix required.
386. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
387. Final RUN_WINDOW_96 status: PASS (all 4 coverage audits PASS @20260601T074631Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1720_controlled_unfreeze_run_window_96_20260601T074730Z.json.
388. Stage RUN_WINDOW_97 completed with no fix required.
389. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
390. Final RUN_WINDOW_97 status: PASS (all 4 coverage audits PASS @20260601T074948Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1722_controlled_unfreeze_run_window_97_20260601T075037Z.json.
391. Stage RUN_WINDOW_98 completed with no fix required.
392. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
393. Final RUN_WINDOW_98 status: PASS (all 4 coverage audits PASS @20260601T075214Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1724_controlled_unfreeze_run_window_98_20260601T075305Z.json.
394. Stage RUN_WINDOW_99 completed with no fix required.
395. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
396. Final RUN_WINDOW_99 status: PASS (all 4 coverage audits PASS @20260601T075451Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1726_controlled_unfreeze_run_window_99_20260601T075542Z.json.
397. Stage RUN_WINDOW_100 completed with no fix required.
398. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
399. Final RUN_WINDOW_100 status: PASS (all 4 coverage audits PASS @20260601T075721Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1728_controlled_unfreeze_run_window_100_20260601T075811Z.json.
400. Stage RUN_WINDOW_101 completed with launch fix.
401. Initial launch returned PARTIAL_FAIL (blocked_readiness): resolved by rerun with `-UseTemporaryUnlock`; after fix, canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220 were preserved.
402. Final RUN_WINDOW_101 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T080201Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1730_controlled_unfreeze_run_window_101_20260601T080202Z.json.
403. Stage RUN_WINDOW_102 completed with no fix required.
404. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
405. Final RUN_WINDOW_102 status: PASS (all 4 coverage audits PASS @20260601T080645Z/20260601T080646Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1732_controlled_unfreeze_run_window_102_20260601T080647Z.json.
406. Stage RUN_WINDOW_103 completed with no fix required.
407. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
408. Final RUN_WINDOW_103 status: PASS (all 4 coverage audits PASS @20260601T081017Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1734_controlled_unfreeze_run_window_103_20260601T081018Z.json.
409. Stage RUN_WINDOW_104 completed with no fix required.
410. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
411. Final RUN_WINDOW_104 status: PASS (all 4 coverage audits PASS @20260601T081342Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1736_controlled_unfreeze_run_window_104_20260601T081344Z.json.
412. Stage RUN_WINDOW_105 completed with no fix required.
413. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
414. Final RUN_WINDOW_105 status: PASS (all 4 coverage audits PASS @20260601T081654Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1738_controlled_unfreeze_run_window_105_20260601T081655Z.json.
415. Stage RUN_WINDOW_106 completed with no fix required.
416. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
417. Final RUN_WINDOW_106 status: PASS (all 4 coverage audits PASS @20260601T081958Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1740_controlled_unfreeze_run_window_106_20260601T081959Z.json.
418. Stage RUN_WINDOW_107 completed with no fix required.
419. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
420. Final RUN_WINDOW_107 status: PASS (all 4 coverage audits PASS @20260601T082301Z/20260601T082302Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1742_controlled_unfreeze_run_window_107_20260601T082303Z.json.
421. Stage RUN_WINDOW_108 completed with no fix required.
422. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
423. Final RUN_WINDOW_108 status: PASS (all 4 coverage audits PASS @20260601T082605Z/20260601T082606Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1744_controlled_unfreeze_run_window_108_20260601T082607Z.json.
424. Stage RUN_WINDOW_109 completed with no fix required.
425. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
426. Final RUN_WINDOW_109 status: PASS (all 4 coverage audits PASS @20260601T082924Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1746_controlled_unfreeze_run_window_109_20260601T082925Z.json.
427. Stage RUN_WINDOW_110 completed with no fix required.
428. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
429. Final RUN_WINDOW_110 status: PASS (all 4 coverage audits PASS @20260601T083303Z/20260601T083304Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1748_controlled_unfreeze_run_window_110_20260601T083306Z.json.
430. Stage RUN_WINDOW_111 completed with no fix required.
431. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
432. Final RUN_WINDOW_111 status: PASS (all 4 coverage audits PASS @20260601T083634Z/20260601T083635Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1750_controlled_unfreeze_run_window_111_20260601T083636Z.json.
433. Stage RUN_WINDOW_112 completed with no fix required.
434. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
435. Final RUN_WINDOW_112 status: PASS (all 4 coverage audits PASS @20260601T083954Z/20260601T083955Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1752_controlled_unfreeze_run_window_112_20260601T083956Z.json.
436. Stage RUN_WINDOW_113 completed with no fix required.
437. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
438. Final RUN_WINDOW_113 status: PASS (all 4 coverage audits PASS @20260601T084305Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1754_controlled_unfreeze_run_window_113_20260601T084306Z.json.
439. Stage RUN_WINDOW_114 completed with no fix required.
440. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
441. Final RUN_WINDOW_114 status: PASS (all 4 coverage audits PASS @20260601T084609Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1756_controlled_unfreeze_run_window_114_20260601T084610Z.json.
442. Stage RUN_WINDOW_115 completed with no fix required.
443. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
444. Final RUN_WINDOW_115 status: PASS (all 4 coverage audits PASS @20260601T084941Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1758_controlled_unfreeze_run_window_115_20260601T084942Z.json.
445. Stage RUN_WINDOW_116 completed with no fix required.
446. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
447. Final RUN_WINDOW_116 status: PASS (all 4 coverage audits PASS @20260601T085328Z/20260601T085329Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1760_controlled_unfreeze_run_window_116_20260601T085330Z.json.
448. Stage RUN_WINDOW_117 completed with no fix required.
449. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
450. Final RUN_WINDOW_117 status: PASS (all 4 coverage audits PASS @20260601T085658Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1762_controlled_unfreeze_run_window_117_20260601T085700Z.json.
451. Stage RUN_WINDOW_118 completed with no fix required.
452. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
453. Final RUN_WINDOW_118 status: PASS (all 4 coverage audits PASS @20260601T090015Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1764_controlled_unfreeze_run_window_118_20260601T090017Z.json.
454. Stage RUN_WINDOW_119 completed with no fix required.
455. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
456. Final RUN_WINDOW_119 status: PASS (all 4 coverage audits PASS @20260601T090359Z/20260601T090400Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1766_controlled_unfreeze_run_window_119_20260601T090401Z.json.
457. Stage RUN_WINDOW_120 completed with an audit environment technical fix (PYTHONPATH=src) and no contour logic changes.
458. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
459. Final RUN_WINDOW_120 status: PASS_AFTER_FIX (all 4 coverage audits PASS @20260601T090845Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1768_controlled_unfreeze_run_window_120_20260601T090852Z.json.
460. Stage RUN_WINDOW_121 completed with min/max coverage fix (technical long_only rerun) and no contour logic changes.
461. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
462. Final RUN_WINDOW_121 status: PASS_AFTER_FIX (initial long_only profile coverage FAIL on pattern_age_cap max-hit; after long_only rerun all 4 coverage audits PASS @20260601T091558Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1770_controlled_unfreeze_run_window_121_20260601T091605Z.json.
463. Stage RUN_WINDOW_122 completed with no fix required.
464. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
465. Final RUN_WINDOW_122 status: PASS (all 4 coverage audits PASS @20260601T091936Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1772_controlled_unfreeze_run_window_122_20260601T091943Z.json.
466. Stage RUN_WINDOW_123 completed with no fix required.
467. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
468. Final RUN_WINDOW_123 status: PASS (all 4 coverage audits PASS @20260601T092301Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1774_controlled_unfreeze_run_window_123_20260601T092307Z.json.
469. Stage RUN_WINDOW_124 completed with no fix required.
470. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
471. Final RUN_WINDOW_124 status: PASS (all 4 coverage audits PASS @20260601T092635Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1776_controlled_unfreeze_run_window_124_20260601T092641Z.json.
472. Stage RUN_WINDOW_125 completed with no fix required.
473. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
474. Final RUN_WINDOW_125 status: PASS (all 4 coverage audits PASS @20260601T093009Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1778_controlled_unfreeze_run_window_125_20260601T093015Z.json.
475. Stage RUN_WINDOW_126 completed with no fix required.
476. Run executed with canonical min/max quintet (HorizonsGrid=1,20, PLongGrid=0.52,0.80, PShortGrid=0.20,0.48, MinExpectedMoveGrid=0.0005,0.01, NotionalUsdGrid=5,100) and trials=220.
477. Final RUN_WINDOW_126 status: PASS (all 4 coverage audits PASS @20260601T093336Z, pip check PASS, text_guard PASS, readiness --show PASS), freeze governance preserved. Consolidated artifact: reports/qa_gate/p1780_controlled_unfreeze_run_window_126_20260601T093342Z.json.
