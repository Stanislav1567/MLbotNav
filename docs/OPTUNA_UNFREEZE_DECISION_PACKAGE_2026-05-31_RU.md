# Optuna unfreeze decision package (2026-05-31)

## 1) Decision status
1. Current decision: `GO_FOR_CONTROLLED_UNFREEZE_CLOSEOUT_COMPLETE`.
2. Decision artifact:
1. `reports/qa_gate/p1783_controlled_unfreeze_final_governance_decision_20260601T110359Z.json`.

## 2) Preconditions check
1. Profile min/max strict coverage:
1. long_only: PASS
2. short_only: PASS
2. Search-grid quintet min/max coverage:
1. long_only: PASS
2. short_only: PASS
3. Readiness governance state:
1. `project_ready=false`
2. `enforce_freeze=true`

## 3) Governance meaning
1. This package approves only a controlled run window.
2. Persistent freeze state remains active by policy until explicit operator action.
3. Temporary unlock model remains mandatory for execution windows.

## 4) Operator actions (if launch window approved)
1. Use runbook:
1. `docs/OPTUNA_CONTROLLED_UNFREEZE_RUNBOOK_2026-05-31_RU.md`
2. Keep `-UseTemporaryUnlock` only.
3. After run window, execute mandatory audits and registry append.

## 5) Pause/Fix rules + Stop-on-success
1. On first FAIL do not terminate the whole series immediately:
1. pause current window,
2. apply targeted fix in same scope,
3. rerun failed scope,
4. execute full post-run audits again.
2. Mark window `FAIL` only if issue remains unresolved after fix loop.
3. Hard-stop current window when:
1. readiness drift (`project_ready` / `enforce_freeze` mismatch),
2. unresolved worker/search technical failure,
3. repeated coverage fail after fix loop.
4. STOP_ON_SUCCESS:
1. `K=5` consecutive windows with status `PASS` (without fix),
2. freeze unchanged in each window (`project_ready=false`, `enforce_freeze=true`),
3. paired post-window decision `GO_FOR_NEXT_CONTROLLED_WINDOW`.


## 6) Post-window update (2026-05-31)
1. `RUN_WINDOW_1` executed with technical PASS.
2. Post-window decision snapshot:
1. `reports/qa_gate/p1528_controlled_unfreeze_post_window_decision_20260531T144652Z.json`
3. Updated decision state:
1. `GO_FOR_NEXT_CONTROLLED_WINDOW` (only temporary unlock model, freeze governance unchanged).
4. `RUN_WINDOW_2` executed with `PASS_AFTER_FIX`.
5. Fix note:
1. Initial short-only profile coverage FAIL resolved by increasing short trials (`220 -> 300`) and rerun.
6. Consolidated evidence:
1. `reports/qa_gate/p1529_controlled_unfreeze_run_window_2_20260531T145119Z.json`
7. Post-window #2 decision snapshot:
1. `reports/qa_gate/p1530_controlled_unfreeze_post_window2_decision_20260531T145208Z.json`
8. Decision state remains:
1. `GO_FOR_NEXT_CONTROLLED_WINDOW` (temporary unlock only, freeze unchanged).
9. `RUN_WINDOW_3` executed with `PASS`.
10. Consolidated evidence:
1. `reports/qa_gate/p1531_controlled_unfreeze_run_window_3_20260531T145642Z.json`
11. Post-window #3 decision snapshot:
1. `reports/qa_gate/p1532_controlled_unfreeze_post_window3_decision_20260531T145650Z.json`
12. Decision state remains:
1. `GO_FOR_NEXT_CONTROLLED_WINDOW` (temporary unlock only, freeze unchanged).
13. RUN_WINDOW_4 executed with PASS.
14. Consolidated evidence:
1. reports/qa_gate/p1534_controlled_unfreeze_run_window_4_20260531T150308Z.json
15. Post-window #4 decision snapshot:
1. reports/qa_gate/p1535_controlled_unfreeze_post_window4_decision_20260531T150315Z.json
16. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
17. RUN_WINDOW_5 executed with PASS.
18. Consolidated evidence:
1. reports/qa_gate/p1536_controlled_unfreeze_run_window_5_20260531T150725Z.json
19. Post-window #5 decision snapshot:
1. reports/qa_gate/p1537_controlled_unfreeze_post_window5_decision_20260531T150733Z.json
20. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
21. RUN_WINDOW_6 executed with PASS.
22. Consolidated evidence:
1. reports/qa_gate/p1538_controlled_unfreeze_run_window_6_20260531T151102Z.json
23. Post-window #6 decision snapshot:
1. reports/qa_gate/p1539_controlled_unfreeze_post_window6_decision_20260531T151113Z.json
24. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
25. RUN_WINDOW_7 executed with PASS.
26. Consolidated evidence:
1. reports/qa_gate/p1540_controlled_unfreeze_run_window_7_20260531T181511Z.json
27. Post-window #7 decision snapshot:
1. reports/qa_gate/p1541_controlled_unfreeze_post_window7_decision_20260531T181521Z.json
28. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
29. RUN_WINDOW_8 executed with PASS.
30. Consolidated evidence:
1. reports/qa_gate/p1542_controlled_unfreeze_run_window_8_20260531T181921Z.json
31. Post-window #8 decision snapshot:
1. reports/qa_gate/p1543_controlled_unfreeze_post_window8_decision_20260531T181937Z.json
32. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
33. RUN_WINDOW_9 executed with PASS.
34. Consolidated evidence:
1. reports/qa_gate/p1544_controlled_unfreeze_run_window_9_20260531T182328Z.json
35. Post-window #9 decision snapshot:
1. reports/qa_gate/p1545_controlled_unfreeze_post_window9_decision_20260531T182336Z.json
36. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
37. RUN_WINDOW_10 executed with PASS.
38. Consolidated evidence:
1. reports/qa_gate/p1546_controlled_unfreeze_run_window_10_20260531T182943Z.json
39. Post-window #10 decision snapshot:
1. reports/qa_gate/p1547_controlled_unfreeze_post_window10_decision_20260531T182943Z.json
40. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
41. RUN_WINDOW_11 executed with PASS.
42. Consolidated evidence:
1. reports/qa_gate/p1548_controlled_unfreeze_run_window_11_20260531T183311Z.json
43. Post-window #11 decision snapshot:
1. reports/qa_gate/p1549_controlled_unfreeze_post_window11_decision_20260531T183311Z.json
44. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
45. RUN_WINDOW_12 executed with PASS_AFTER_FIX.
46. Consolidated evidence:
1. reports/qa_gate/p1550_controlled_unfreeze_run_window_12_20260531T183748Z.json
47. Post-window #12 decision snapshot:
1. reports/qa_gate/p1551_controlled_unfreeze_post_window12_decision_20260531T183748Z.json
48. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
49. RUN_WINDOW_13 executed with PASS.
50. Consolidated evidence:
1. reports/qa_gate/p1552_controlled_unfreeze_run_window_13_20260531T184110Z.json
51. Post-window #13 decision snapshot:
1. reports/qa_gate/p1553_controlled_unfreeze_post_window13_decision_20260531T184110Z.json
52. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
53. RUN_WINDOW_14 executed with PASS.
54. Consolidated evidence:
1. reports/qa_gate/p1554_controlled_unfreeze_run_window_14_20260531T184501Z.json
55. Post-window #14 decision snapshot:
1. reports/qa_gate/p1555_controlled_unfreeze_post_window14_decision_20260531T184501Z.json
56. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
57. RUN_WINDOW_15 executed with PASS.
58. Consolidated evidence:
1. reports/qa_gate/p1556_controlled_unfreeze_run_window_15_20260531T184827Z.json
59. Post-window #15 decision snapshot:
1. reports/qa_gate/p1557_controlled_unfreeze_post_window15_decision_20260531T184827Z.json
60. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
61. RUN_WINDOW_16 executed with PASS_AFTER_FIX.
62. Consolidated evidence:
1. reports/qa_gate/p1558_controlled_unfreeze_run_window_16_20260531T185436Z.json
63. Post-window #16 decision snapshot:
1. reports/qa_gate/p1559_controlled_unfreeze_post_window16_decision_20260531T185436Z.json
64. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
65. RUN_WINDOW_17 executed with PASS_AFTER_FIX.
66. Consolidated evidence:
1. reports/qa_gate/p1560_controlled_unfreeze_run_window_17_20260531T190050Z.json
67. Post-window #17 decision snapshot:
1. reports/qa_gate/p1561_controlled_unfreeze_post_window17_decision_20260531T190050Z.json
68. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
69. RUN_WINDOW_18 executed with PASS.
70. Consolidated evidence:
1. reports/qa_gate/p1562_controlled_unfreeze_run_window_18_20260531T190428Z.json
71. Post-window #18 decision snapshot:
1. reports/qa_gate/p1563_controlled_unfreeze_post_window18_decision_20260531T190428Z.json
72. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
73. RUN_WINDOW_19 executed with PASS_AFTER_FIX.
74. Consolidated evidence:
1. reports/qa_gate/p1564_controlled_unfreeze_run_window_19_20260531T191036Z.json
75. Post-window #19 decision snapshot:
1. reports/qa_gate/p1565_controlled_unfreeze_post_window19_decision_20260531T191036Z.json
76. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
77. RUN_WINDOW_20 executed with PASS_AFTER_FIX.
78. Consolidated evidence:
1. reports/qa_gate/p1566_controlled_unfreeze_run_window_20_20260531T191523Z.json
79. Post-window #20 decision snapshot:
1. reports/qa_gate/p1567_controlled_unfreeze_post_window20_decision_20260531T191523Z.json
80. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
81. RUN_WINDOW_21 executed with PASS.
82. Consolidated evidence:
1. reports/qa_gate/p1568_controlled_unfreeze_run_window_21_20260531T191847Z.json
83. Post-window #21 decision snapshot:
1. reports/qa_gate/p1569_controlled_unfreeze_post_window21_decision_20260531T191847Z.json
84. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
85. RUN_WINDOW_22 executed with PASS.
86. Consolidated evidence:
1. reports/qa_gate/p1570_controlled_unfreeze_run_window_22_20260531T192208Z.json
87. Post-window #22 decision snapshot:
1. reports/qa_gate/p1571_controlled_unfreeze_post_window22_decision_20260531T192208Z.json
88. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
89. RUN_WINDOW_23 executed with PASS_AFTER_FIX.
90. Consolidated evidence:
1. reports/qa_gate/p1572_controlled_unfreeze_run_window_23_20260531T192641Z.json
91. Post-window #23 decision snapshot:
1. reports/qa_gate/p1573_controlled_unfreeze_post_window23_decision_20260531T192641Z.json
92. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
93. RUN_WINDOW_24 executed with PASS_AFTER_FIX.
94. Consolidated evidence:
1. reports/qa_gate/p1574_controlled_unfreeze_run_window_24_20260531T193247Z.json
95. Post-window #24 decision snapshot:
1. reports/qa_gate/p1575_controlled_unfreeze_post_window24_decision_20260531T193247Z.json
96. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
97. RUN_WINDOW_25 executed with PASS.
98. Consolidated evidence:
1. reports/qa_gate/p1576_controlled_unfreeze_run_window_25_20260531T193655Z.json
99. Post-window #25 decision snapshot:
1. reports/qa_gate/p1577_controlled_unfreeze_post_window25_decision_20260531T193655Z.json
100. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
101. RUN_WINDOW_26 executed with PASS.
102. Consolidated evidence:
1. reports/qa_gate/p1578_controlled_unfreeze_run_window_26_20260531T194201Z.json
103. Post-window #26 decision snapshot:
1. reports/qa_gate/p1579_controlled_unfreeze_post_window26_decision_20260531T194201Z.json
104. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
105. RUN_WINDOW_27 executed with PASS.
106. Consolidated evidence:
1. reports/qa_gate/p1580_controlled_unfreeze_run_window_27_20260531T194552Z.json
107. Post-window #27 decision snapshot:
1. reports/qa_gate/p1581_controlled_unfreeze_post_window27_decision_20260531T194552Z.json
108. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
109. RUN_WINDOW_28 executed with PASS_AFTER_FIX.
110. Consolidated evidence:
1. reports/qa_gate/p1582_controlled_unfreeze_run_window_28_20260601T024714Z.json
111. Post-window #28 decision snapshot:
1. reports/qa_gate/p1583_controlled_unfreeze_post_window28_decision_20260601T024714Z.json
112. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
113. RUN_WINDOW_29 executed with PASS.
114. Consolidated evidence:
1. reports/qa_gate/p1584_controlled_unfreeze_run_window_29_20260601T025107Z.json
115. Post-window #29 decision snapshot:
1. reports/qa_gate/p1585_controlled_unfreeze_post_window29_decision_20260601T025107Z.json
116. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
117. RUN_WINDOW_30 executed with PASS.
118. Consolidated evidence:
1. reports/qa_gate/p1586_controlled_unfreeze_run_window_30_20260601T025448Z.json
119. Post-window #30 decision snapshot:
1. reports/qa_gate/p1587_controlled_unfreeze_post_window30_decision_20260601T025448Z.json
120. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
121. RUN_WINDOW_31 executed with PASS.
122. Consolidated evidence:
1. reports/qa_gate/p1588_controlled_unfreeze_run_window_31_20260601T025816Z.json
123. Post-window #31 decision snapshot:
1. reports/qa_gate/p1589_controlled_unfreeze_post_window31_decision_20260601T025816Z.json
124. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
125. RUN_WINDOW_32 executed with PASS.
126. Consolidated evidence:
1. reports/qa_gate/p1590_controlled_unfreeze_run_window_32_20260601T030128Z.json
127. Post-window #32 decision snapshot:
1. reports/qa_gate/p1591_controlled_unfreeze_post_window32_decision_20260601T030128Z.json
128. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
129. RUN_WINDOW_33 executed with PASS_AFTER_FIX.
130. Consolidated evidence:
1. reports/qa_gate/p1592_controlled_unfreeze_run_window_33_20260601T030607Z.json
131. Post-window #33 decision snapshot:
1. reports/qa_gate/p1593_controlled_unfreeze_post_window33_decision_20260601T030607Z.json
132. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
133. RUN_WINDOW_34 executed with PASS.
134. Consolidated evidence:
1. reports/qa_gate/p1594_controlled_unfreeze_run_window_34_20260601T030942Z.json
135. Post-window #34 decision snapshot:
1. reports/qa_gate/p1595_controlled_unfreeze_post_window34_decision_20260601T030942Z.json
136. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
137. RUN_WINDOW_35 executed with PASS.
138. Consolidated evidence:
1. reports/qa_gate/p1596_controlled_unfreeze_run_window_35_20260601T031316Z.json
139. Post-window #35 decision snapshot:
1. reports/qa_gate/p1597_controlled_unfreeze_post_window35_decision_20260601T031316Z.json
140. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
141. RUN_WINDOW_36 executed with PASS.
142. Consolidated evidence:
1. reports/qa_gate/p1598_controlled_unfreeze_run_window_36_20260601T031645Z.json
143. Post-window #36 decision snapshot:
1. reports/qa_gate/p1599_controlled_unfreeze_post_window36_decision_20260601T031645Z.json
144. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
145. RUN_WINDOW_37 executed with PASS_AFTER_FIX.
146. Consolidated evidence:
1. reports/qa_gate/p1600_controlled_unfreeze_run_window_37_20260601T032139Z.json
147. Post-window #37 decision snapshot:
1. reports/qa_gate/p1601_controlled_unfreeze_post_window37_decision_20260601T032139Z.json
148. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
149. RUN_WINDOW_38 executed with PASS_AFTER_FIX.
150. Consolidated evidence:
1. reports/qa_gate/p1602_controlled_unfreeze_run_window_38_20260601T032646Z.json
151. Post-window #38 decision snapshot:
1. reports/qa_gate/p1603_controlled_unfreeze_post_window38_decision_20260601T032646Z.json
152. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
153. RUN_WINDOW_39 executed with PASS.
154. Consolidated evidence:
1. reports/qa_gate/p1604_controlled_unfreeze_run_window_39_20260601T033028Z.json
155. Post-window #39 decision snapshot:
1. reports/qa_gate/p1605_controlled_unfreeze_post_window39_decision_20260601T033028Z.json
156. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
157. RUN_WINDOW_40 executed with PASS.
158. Consolidated evidence:
1. reports/qa_gate/p1606_controlled_unfreeze_run_window_40_20260601T033419Z.json
159. Post-window #40 decision snapshot:
1. reports/qa_gate/p1607_controlled_unfreeze_post_window40_decision_20260601T033419Z.json
160. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
161. RUN_WINDOW_41 executed with PASS_AFTER_FIX.
162. Consolidated evidence:
1. reports/qa_gate/p1608_controlled_unfreeze_run_window_41_20260601T033900Z.json
163. Post-window #41 decision snapshot:
1. reports/qa_gate/p1609_controlled_unfreeze_post_window41_decision_20260601T033900Z.json
164. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
165. RUN_WINDOW_42 executed with PASS.
166. Consolidated evidence:
1. reports/qa_gate/p1610_controlled_unfreeze_run_window_42_20260601T034306Z.json
167. Post-window #42 decision snapshot:
1. reports/qa_gate/p1611_controlled_unfreeze_post_window42_decision_20260601T034306Z.json
168. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
169. RUN_WINDOW_43 executed with PASS_AFTER_FIX.
170. Consolidated evidence:
1. reports/qa_gate/p1612_controlled_unfreeze_run_window_43_20260601T034820Z.json
171. Post-window #43 decision snapshot:
1. reports/qa_gate/p1613_controlled_unfreeze_post_window43_decision_20260601T034820Z.json
172. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
173. RUN_WINDOW_44 executed with PASS_AFTER_FIX.
174. Consolidated evidence:
1. reports/qa_gate/p1614_controlled_unfreeze_run_window_44_20260601T040014Z.json
175. Post-window #44 decision snapshot:
1. reports/qa_gate/p1615_controlled_unfreeze_post_window44_decision_20260601T040014Z.json
176. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
177. RUN_WINDOW_45 executed with PASS.
178. Consolidated evidence:
1. reports/qa_gate/p1616_controlled_unfreeze_run_window_45_20260601T041155Z.json
179. Post-window #45 decision snapshot:
1. reports/qa_gate/p1617_controlled_unfreeze_post_window45_decision_20260601T041155Z.json
180. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
181. RUN_WINDOW_46 executed with PASS.
182. Consolidated evidence:
1. reports/qa_gate/p1618_controlled_unfreeze_run_window_46_20260601T041549Z.json
183. Post-window #46 decision snapshot:
1. reports/qa_gate/p1619_controlled_unfreeze_post_window46_decision_20260601T041549Z.json
184. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
185. RUN_WINDOW_47 executed with PASS.
186. Consolidated evidence:
1. reports/qa_gate/p1620_controlled_unfreeze_run_window_47_20260601T041949Z.json
187. Post-window #47 decision snapshot:
1. reports/qa_gate/p1621_controlled_unfreeze_post_window47_decision_20260601T041949Z.json
188. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
189. RUN_WINDOW_48 executed with PASS.
190. Consolidated evidence:
1. reports/qa_gate/p1622_controlled_unfreeze_run_window_48_20260601T042323Z.json
191. Post-window #48 decision snapshot:
1. reports/qa_gate/p1623_controlled_unfreeze_post_window48_decision_20260601T042323Z.json
192. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
193. RUN_WINDOW_49 executed with PASS_AFTER_FIX.
194. Consolidated evidence:
1. reports/qa_gate/p1624_controlled_unfreeze_run_window_49_20260601T042825Z.json
195. Post-window #49 decision snapshot:
1. reports/qa_gate/p1625_controlled_unfreeze_post_window49_decision_20260601T042825Z.json
196. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
197. RUN_WINDOW_50 executed with PASS.
198. Consolidated evidence:
1. reports/qa_gate/p1626_controlled_unfreeze_run_window_50_20260601T044217Z.json
199. Post-window #50 decision snapshot:
1. reports/qa_gate/p1627_controlled_unfreeze_post_window50_decision_20260601T044217Z.json
200. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
201. RUN_WINDOW_51 executed with PASS_AFTER_FIX.
202. Consolidated evidence:
1. reports/qa_gate/p1629_controlled_unfreeze_run_window_51_20260601T045038Z.json
203. Post-window #51 decision snapshot:
1. reports/qa_gate/p1630_controlled_unfreeze_post_window51_decision_20260601T045038Z.json
204. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
205. RUN_WINDOW_52 executed with PASS.
206. Consolidated evidence:
1. reports/qa_gate/p1631_controlled_unfreeze_run_window_52_20260601T045433Z.json
207. Post-window #52 decision snapshot:
1. reports/qa_gate/p1632_controlled_unfreeze_post_window52_decision_20260601T045433Z.json
208. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
209. RUN_WINDOW_53 executed with PASS.
210. Consolidated evidence:
1. reports/qa_gate/p1633_controlled_unfreeze_run_window_53_20260601T045810Z.json
211. Post-window #53 decision snapshot:
1. reports/qa_gate/p1634_controlled_unfreeze_post_window53_decision_20260601T045810Z.json
212. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
213. RUN_WINDOW_54 executed with PASS.
214. Consolidated evidence:
1. reports/qa_gate/p1635_controlled_unfreeze_run_window_54_20260601T050157Z.json
215. Post-window #54 decision snapshot:
1. reports/qa_gate/p1636_controlled_unfreeze_post_window54_decision_20260601T050157Z.json
216. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
217. RUN_WINDOW_55 executed with PASS_AFTER_FIX.
218. Consolidated evidence:
1. reports/qa_gate/p1637_controlled_unfreeze_run_window_55_20260601T050713Z.json
219. Post-window #55 decision snapshot:
1. reports/qa_gate/p1638_controlled_unfreeze_post_window55_decision_20260601T050713Z.json
220. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
221. RUN_WINDOW_56 executed with PASS.
222. Consolidated evidence:
1. reports/qa_gate/p1639_controlled_unfreeze_run_window_56_20260601T051105Z.json
223. Post-window #56 decision snapshot:
1. reports/qa_gate/p1640_controlled_unfreeze_post_window56_decision_20260601T051105Z.json
224. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
225. RUN_WINDOW_57 executed with PASS.
226. Consolidated evidence:
1. reports/qa_gate/p1641_controlled_unfreeze_run_window_57_20260601T051421Z.json
227. Post-window #57 decision snapshot:
1. reports/qa_gate/p1642_controlled_unfreeze_post_window57_decision_20260601T051421Z.json
228. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
229. RUN_WINDOW_58 executed with PASS.
230. Consolidated evidence:
1. reports/qa_gate/p1643_controlled_unfreeze_run_window_58_20260601T051742Z.json
231. Post-window #58 decision snapshot:
1. reports/qa_gate/p1644_controlled_unfreeze_post_window58_decision_20260601T051742Z.json
232. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
233. RUN_WINDOW_59 executed with PASS_AFTER_FIX.
234. Consolidated evidence:
1. reports/qa_gate/p1645_controlled_unfreeze_run_window_59_20260601T052252Z.json
235. Post-window #59 decision snapshot:
1. reports/qa_gate/p1646_controlled_unfreeze_post_window59_decision_20260601T052252Z.json
236. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
237. RUN_WINDOW_60 executed with PASS.
238. Consolidated evidence:
1. reports/qa_gate/p1647_controlled_unfreeze_run_window_60_20260601T052647Z.json
239. Post-window #60 decision snapshot:
1. reports/qa_gate/p1648_controlled_unfreeze_post_window60_decision_20260601T052647Z.json
240. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
241. RUN_WINDOW_61 executed with PASS_AFTER_FIX.
242. Consolidated evidence:
1. reports/qa_gate/p1649_controlled_unfreeze_run_window_61_20260601T053149Z.json
243. Post-window #61 decision snapshot:
1. reports/qa_gate/p1650_controlled_unfreeze_post_window61_decision_20260601T053149Z.json
244. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
245. RUN_WINDOW_62 executed with PASS.
246. Consolidated evidence:
1. reports/qa_gate/p1651_controlled_unfreeze_run_window_62_20260601T053522Z.json
247. Post-window #62 decision snapshot:
1. reports/qa_gate/p1652_controlled_unfreeze_post_window62_decision_20260601T053522Z.json
248. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
249. RUN_WINDOW_63 executed with PASS.
250. Consolidated evidence:
1. reports/qa_gate/p1653_controlled_unfreeze_run_window_63_20260601T053848Z.json
251. Post-window #63 decision snapshot:
1. reports/qa_gate/p1654_controlled_unfreeze_post_window63_decision_20260601T053848Z.json
252. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
253. RUN_WINDOW_64 executed with PASS_AFTER_FIX.
254. Consolidated evidence:
1. reports/qa_gate/p1655_controlled_unfreeze_run_window_64_20260601T054525Z.json
255. Post-window #64 decision snapshot:
1. reports/qa_gate/p1656_controlled_unfreeze_post_window64_decision_20260601T054525Z.json
256. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
257. RUN_WINDOW_65 executed with PASS.
258. Consolidated evidence:
1. reports/qa_gate/p1657_controlled_unfreeze_run_window_65_20260601T055122Z.json
259. Post-window #65 decision snapshot:
1. reports/qa_gate/p1658_controlled_unfreeze_post_window65_decision_20260601T055122Z.json
260. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
261. RUN_WINDOW_66 executed with PASS.
262. Consolidated evidence:
1. reports/qa_gate/p1660_controlled_unfreeze_run_window_66_20260601T055700Z.json
263. Post-window #66 decision snapshot:
1. reports/qa_gate/p1661_controlled_unfreeze_post_window66_decision_20260601T055700Z.json
264. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
265. RUN_WINDOW_67 executed with PASS.
266. Consolidated evidence:
1. reports/qa_gate/p1662_controlled_unfreeze_run_window_67_20260601T060025Z.json
267. Post-window #67 decision snapshot:
1. reports/qa_gate/p1663_controlled_unfreeze_post_window67_decision_20260601T060025Z.json
268. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
269. RUN_WINDOW_68 executed with PASS.
270. Consolidated evidence:
1. reports/qa_gate/p1664_controlled_unfreeze_run_window_68_20260601T060355Z.json
271. Post-window #68 decision snapshot:
1. reports/qa_gate/p1665_controlled_unfreeze_post_window68_decision_20260601T060355Z.json
272. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
273. RUN_WINDOW_69 executed with PASS_AFTER_FIX.
274. Consolidated evidence:
1. reports/qa_gate/p1666_controlled_unfreeze_run_window_69_20260601T061040Z.json
275. Post-window #69 decision snapshot:
1. reports/qa_gate/p1667_controlled_unfreeze_post_window69_decision_20260601T061040Z.json
276. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
277. RUN_WINDOW_70 executed with PASS.
278. Consolidated evidence:
1. reports/qa_gate/p1668_controlled_unfreeze_run_window_70_20260601T061425Z.json
279. Post-window #70 decision snapshot:
1. reports/qa_gate/p1669_controlled_unfreeze_post_window70_decision_20260601T061425Z.json
280. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
281. RUN_WINDOW_71 executed with PASS_AFTER_FIX.
282. Consolidated evidence:
1. reports/qa_gate/p1670_controlled_unfreeze_run_window_71_20260601T061958Z.json
283. Post-window #71 decision snapshot:
1. reports/qa_gate/p1671_controlled_unfreeze_post_window71_decision_20260601T061958Z.json
284. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
285. RUN_WINDOW_72 executed with PASS.
286. Consolidated evidence:
1. reports/qa_gate/p1672_controlled_unfreeze_run_window_72_20260601T062345Z.json
287. Post-window #72 decision snapshot:
1. reports/qa_gate/p1673_controlled_unfreeze_post_window72_decision_20260601T062345Z.json
288. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
289. RUN_WINDOW_73 executed with PASS_AFTER_FIX.
290. Consolidated evidence:
1. reports/qa_gate/p1674_controlled_unfreeze_run_window_73_20260601T062750Z.json
291. Post-window #73 decision snapshot:
1. reports/qa_gate/p1675_controlled_unfreeze_post_window73_decision_20260601T062750Z.json
292. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
293. RUN_WINDOW_74 executed with PASS.
294. Consolidated evidence:
1. reports/qa_gate/p1676_controlled_unfreeze_run_window_74_20260601T063120Z.json
295. Post-window #74 decision snapshot:
1. reports/qa_gate/p1677_controlled_unfreeze_post_window74_decision_20260601T063120Z.json
296. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
297. RUN_WINDOW_75 executed with PASS_AFTER_FIX.
298. Consolidated evidence:
1. reports/qa_gate/p1678_controlled_unfreeze_run_window_75_20260601T063638Z.json
299. Post-window #75 decision snapshot:
1. reports/qa_gate/p1679_controlled_unfreeze_post_window75_decision_20260601T063638Z.json
300. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
301. RUN_WINDOW_76 executed with PASS.
302. Consolidated evidence:
1. reports/qa_gate/p1680_controlled_unfreeze_run_window_76_20260601T064050Z.json
303. Post-window #76 decision snapshot:
1. reports/qa_gate/p1681_controlled_unfreeze_post_window76_decision_20260601T064050Z.json
304. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
305. RUN_WINDOW_77 executed with PASS_AFTER_FIX.
306. Consolidated evidence:
1. reports/qa_gate/p1682_controlled_unfreeze_run_window_77_20260601T064857Z.json
307. Post-window #77 decision snapshot:
1. reports/qa_gate/p1683_controlled_unfreeze_post_window77_decision_20260601T064857Z.json
308. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
309. RUN_WINDOW_78 executed with PASS.
310. Consolidated evidence:
1. reports/qa_gate/p1684_controlled_unfreeze_run_window_78_20260601T065207Z.json
311. Post-window #78 decision snapshot:
1. reports/qa_gate/p1685_controlled_unfreeze_post_window78_decision_20260601T065207Z.json
312. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
313. RUN_WINDOW_79 executed with PASS.
314. Consolidated evidence:
1. reports/qa_gate/p1686_controlled_unfreeze_run_window_79_20260601T065539Z.json
315. Post-window #79 decision snapshot:
1. reports/qa_gate/p1687_controlled_unfreeze_post_window79_decision_20260601T065539Z.json
316. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
317. RUN_WINDOW_80 executed with PASS.
318. Consolidated evidence:
1. reports/qa_gate/p1688_controlled_unfreeze_run_window_80_20260601T065822Z.json
319. Post-window #80 decision snapshot:
1. reports/qa_gate/p1689_controlled_unfreeze_post_window80_decision_20260601T065822Z.json
320. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
321. RUN_WINDOW_81 executed with PASS.
322. Consolidated evidence:
1. reports/qa_gate/p1690_controlled_unfreeze_run_window_81_20260601T070123Z.json
323. Post-window #81 decision snapshot:
1. reports/qa_gate/p1691_controlled_unfreeze_post_window81_decision_20260601T070123Z.json
324. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
325. RUN_WINDOW_82 executed with PASS.
326. Consolidated evidence:
1. reports/qa_gate/p1692_controlled_unfreeze_run_window_82_20260601T070429Z.json
327. Post-window #82 decision snapshot:
1. reports/qa_gate/p1693_controlled_unfreeze_post_window82_decision_20260601T070429Z.json
328. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
329. RUN_WINDOW_83 executed with PASS.
330. Consolidated evidence:
1. reports/qa_gate/p1694_controlled_unfreeze_run_window_83_20260601T070747Z.json
331. Post-window #83 decision snapshot:
1. reports/qa_gate/p1695_controlled_unfreeze_post_window83_decision_20260601T070747Z.json
332. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
333. RUN_WINDOW_84 executed with PASS.
334. Consolidated evidence:
1. reports/qa_gate/p1696_controlled_unfreeze_run_window_84_20260601T071051Z.json
335. Post-window #84 decision snapshot:
1. reports/qa_gate/p1697_controlled_unfreeze_post_window84_decision_20260601T071051Z.json
336. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
337. RUN_WINDOW_85 executed with PASS.
338. Consolidated evidence:
1. reports/qa_gate/p1698_controlled_unfreeze_run_window_85_20260601T071401Z.json
339. Post-window #85 decision snapshot:
1. reports/qa_gate/p1699_controlled_unfreeze_post_window85_decision_20260601T071401Z.json
340. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
341. RUN_WINDOW_86 executed with PASS.
342. Consolidated evidence:
1. reports/qa_gate/p1700_controlled_unfreeze_run_window_86_20260601T071659Z.json
343. Post-window #86 decision snapshot:
1. reports/qa_gate/p1701_controlled_unfreeze_post_window86_decision_20260601T071659Z.json
344. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
345. RUN_WINDOW_87 executed with PASS.
346. Consolidated evidence:
1. reports/qa_gate/p1702_controlled_unfreeze_run_window_87_20260601T071959Z.json
347. Post-window #87 decision snapshot:
1. reports/qa_gate/p1703_controlled_unfreeze_post_window87_decision_20260601T071959Z.json
348. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
349. RUN_WINDOW_88 executed with PASS.
350. Consolidated evidence:
1. reports/qa_gate/p1704_controlled_unfreeze_run_window_88_20260601T072302Z.json
351. Post-window #88 decision snapshot:
1. reports/qa_gate/p1705_controlled_unfreeze_post_window88_decision_20260601T072302Z.json
352. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
353. RUN_WINDOW_89 executed with PASS.
354. Consolidated evidence:
1. reports/qa_gate/p1706_controlled_unfreeze_run_window_89_20260601T072602Z.json
355. Post-window #89 decision snapshot:
1. reports/qa_gate/p1707_controlled_unfreeze_post_window89_decision_20260601T072602Z.json
356. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
357. RUN_WINDOW_90 executed with PASS.
358. Consolidated evidence:
1. reports/qa_gate/p1708_controlled_unfreeze_run_window_90_20260601T072912Z.json
359. Post-window #90 decision snapshot:
1. reports/qa_gate/p1709_controlled_unfreeze_post_window90_decision_20260601T072912Z.json
360. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
361. RUN_WINDOW_91 executed with PASS.
362. Consolidated evidence:
1. reports/qa_gate/p1710_controlled_unfreeze_run_window_91_20260601T073227Z.json
363. Post-window #91 decision snapshot:
1. reports/qa_gate/p1711_controlled_unfreeze_post_window91_decision_20260601T073227Z.json
364. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
365. RUN_WINDOW_92 executed with PASS.
366. Consolidated evidence:
1. reports/qa_gate/p1712_controlled_unfreeze_run_window_92_20260601T073530Z.json
367. Post-window #92 decision snapshot:
1. reports/qa_gate/p1713_controlled_unfreeze_post_window92_decision_20260601T073530Z.json
368. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
369. RUN_WINDOW_93 executed with PASS_AFTER_FIX.
370. Consolidated evidence:
1. reports/qa_gate/p1714_controlled_unfreeze_run_window_93_20260601T073937Z.json
371. Post-window #93 decision snapshot:
1. reports/qa_gate/p1715_controlled_unfreeze_post_window93_decision_20260601T073937Z.json
372. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
373. RUN_WINDOW_94 executed with PASS.
374. Consolidated evidence:
1. reports/qa_gate/p1716_controlled_unfreeze_run_window_94_20260601T074216Z.json
375. Post-window #94 decision snapshot:
1. reports/qa_gate/p1717_controlled_unfreeze_post_window94_decision_20260601T074216Z.json
376. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
377. RUN_WINDOW_95 executed with PASS.
378. Consolidated evidence:
1. reports/qa_gate/p1718_controlled_unfreeze_run_window_95_20260601T074452Z.json
379. Post-window #95 decision snapshot:
1. reports/qa_gate/p1719_controlled_unfreeze_post_window95_decision_20260601T074452Z.json
380. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
381. RUN_WINDOW_96 executed with PASS.
382. Consolidated evidence:
1. reports/qa_gate/p1720_controlled_unfreeze_run_window_96_20260601T074730Z.json
383. Post-window #96 decision snapshot:
1. reports/qa_gate/p1721_controlled_unfreeze_post_window96_decision_20260601T074730Z.json
384. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
385. RUN_WINDOW_97 executed with PASS.
386. Consolidated evidence:
1. reports/qa_gate/p1722_controlled_unfreeze_run_window_97_20260601T075037Z.json
387. Post-window #97 decision snapshot:
1. reports/qa_gate/p1723_controlled_unfreeze_post_window97_decision_20260601T075037Z.json
388. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
389. RUN_WINDOW_98 executed with PASS.
390. Consolidated evidence:
1. reports/qa_gate/p1724_controlled_unfreeze_run_window_98_20260601T075305Z.json
391. Post-window #98 decision snapshot:
1. reports/qa_gate/p1725_controlled_unfreeze_post_window98_decision_20260601T075305Z.json
392. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
393. RUN_WINDOW_99 executed with PASS.
394. Consolidated evidence:
1. reports/qa_gate/p1726_controlled_unfreeze_run_window_99_20260601T075542Z.json
395. Post-window #99 decision snapshot:
1. reports/qa_gate/p1727_controlled_unfreeze_post_window99_decision_20260601T075542Z.json
396. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
397. RUN_WINDOW_100 executed with PASS.
398. Consolidated evidence:
1. reports/qa_gate/p1728_controlled_unfreeze_run_window_100_20260601T075811Z.json
399. Post-window #100 decision snapshot:
1. reports/qa_gate/p1729_controlled_unfreeze_post_window100_decision_20260601T075811Z.json
400. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
401. RUN_WINDOW_101 executed with PASS_AFTER_FIX.
402. Consolidated evidence:
1. reports/qa_gate/p1730_controlled_unfreeze_run_window_101_20260601T080202Z.json
403. Post-window #101 decision snapshot:
1. reports/qa_gate/p1731_controlled_unfreeze_post_window101_decision_20260601T080202Z.json
404. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
405. RUN_WINDOW_102 executed with PASS.
406. Consolidated evidence:
1. reports/qa_gate/p1732_controlled_unfreeze_run_window_102_20260601T080647Z.json
407. Post-window #102 decision snapshot:
1. reports/qa_gate/p1733_controlled_unfreeze_post_window102_decision_20260601T080647Z.json
408. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
409. RUN_WINDOW_103 executed with PASS.
410. Consolidated evidence:
1. reports/qa_gate/p1734_controlled_unfreeze_run_window_103_20260601T081018Z.json
411. Post-window #103 decision snapshot:
1. reports/qa_gate/p1735_controlled_unfreeze_post_window103_decision_20260601T081018Z.json
412. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
413. RUN_WINDOW_104 executed with PASS.
414. Consolidated evidence:
1. reports/qa_gate/p1736_controlled_unfreeze_run_window_104_20260601T081344Z.json
415. Post-window #104 decision snapshot:
1. reports/qa_gate/p1737_controlled_unfreeze_post_window104_decision_20260601T081344Z.json
416. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
417. RUN_WINDOW_105 executed with PASS.
418. Consolidated evidence:
1. reports/qa_gate/p1738_controlled_unfreeze_run_window_105_20260601T081655Z.json
419. Post-window #105 decision snapshot:
1. reports/qa_gate/p1739_controlled_unfreeze_post_window105_decision_20260601T081655Z.json
420. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
421. RUN_WINDOW_106 executed with PASS.
422. Consolidated evidence:
1. reports/qa_gate/p1740_controlled_unfreeze_run_window_106_20260601T081959Z.json
423. Post-window #106 decision snapshot:
1. reports/qa_gate/p1741_controlled_unfreeze_post_window106_decision_20260601T081959Z.json
424. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
425. RUN_WINDOW_107 executed with PASS.
426. Consolidated evidence:
1. reports/qa_gate/p1742_controlled_unfreeze_run_window_107_20260601T082303Z.json
427. Post-window #107 decision snapshot:
1. reports/qa_gate/p1743_controlled_unfreeze_post_window107_decision_20260601T082303Z.json
428. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
429. RUN_WINDOW_108 executed with PASS.
430. Consolidated evidence:
1. reports/qa_gate/p1744_controlled_unfreeze_run_window_108_20260601T082607Z.json
431. Post-window #108 decision snapshot:
1. reports/qa_gate/p1745_controlled_unfreeze_post_window108_decision_20260601T082607Z.json
432. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
433. RUN_WINDOW_109 executed with PASS.
434. Consolidated evidence:
1. reports/qa_gate/p1746_controlled_unfreeze_run_window_109_20260601T082925Z.json
435. Post-window #109 decision snapshot:
1. reports/qa_gate/p1747_controlled_unfreeze_post_window109_decision_20260601T082925Z.json
436. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
437. RUN_WINDOW_110 executed with PASS.
438. Consolidated evidence:
1. reports/qa_gate/p1748_controlled_unfreeze_run_window_110_20260601T083306Z.json
439. Post-window #110 decision snapshot:
1. reports/qa_gate/p1749_controlled_unfreeze_post_window110_decision_20260601T083306Z.json
440. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
441. RUN_WINDOW_111 executed with PASS.
442. Consolidated evidence:
1. reports/qa_gate/p1750_controlled_unfreeze_run_window_111_20260601T083636Z.json
443. Post-window #111 decision snapshot:
1. reports/qa_gate/p1751_controlled_unfreeze_post_window111_decision_20260601T083636Z.json
444. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
445. RUN_WINDOW_112 executed with PASS.
446. Consolidated evidence:
1. reports/qa_gate/p1752_controlled_unfreeze_run_window_112_20260601T083956Z.json
447. Post-window #112 decision snapshot:
1. reports/qa_gate/p1753_controlled_unfreeze_post_window112_decision_20260601T083956Z.json
448. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
449. RUN_WINDOW_113 executed with PASS.
450. Consolidated evidence:
1. reports/qa_gate/p1754_controlled_unfreeze_run_window_113_20260601T084306Z.json
451. Post-window #113 decision snapshot:
1. reports/qa_gate/p1755_controlled_unfreeze_post_window113_decision_20260601T084306Z.json
452. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
453. RUN_WINDOW_114 executed with PASS.
454. Consolidated evidence:
1. reports/qa_gate/p1756_controlled_unfreeze_run_window_114_20260601T084610Z.json
455. Post-window #114 decision snapshot:
1. reports/qa_gate/p1757_controlled_unfreeze_post_window114_decision_20260601T084610Z.json
456. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
457. RUN_WINDOW_115 executed with PASS.
458. Consolidated evidence:
1. reports/qa_gate/p1758_controlled_unfreeze_run_window_115_20260601T084942Z.json
459. Post-window #115 decision snapshot:
1. reports/qa_gate/p1759_controlled_unfreeze_post_window115_decision_20260601T084942Z.json
460. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
461. RUN_WINDOW_116 executed with PASS.
462. Consolidated evidence:
1. reports/qa_gate/p1760_controlled_unfreeze_run_window_116_20260601T085330Z.json
463. Post-window #116 decision snapshot:
1. reports/qa_gate/p1761_controlled_unfreeze_post_window116_decision_20260601T085330Z.json
464. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
465. RUN_WINDOW_117 executed with PASS.
466. Consolidated evidence:
1. reports/qa_gate/p1762_controlled_unfreeze_run_window_117_20260601T085700Z.json
467. Post-window #117 decision snapshot:
1. reports/qa_gate/p1763_controlled_unfreeze_post_window117_decision_20260601T085700Z.json
468. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
469. RUN_WINDOW_118 executed with PASS.
470. Consolidated evidence:
1. reports/qa_gate/p1764_controlled_unfreeze_run_window_118_20260601T090017Z.json
471. Post-window #118 decision snapshot:
1. reports/qa_gate/p1765_controlled_unfreeze_post_window118_decision_20260601T090017Z.json
472. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
473. RUN_WINDOW_119 executed with PASS.
474. Consolidated evidence:
1. reports/qa_gate/p1766_controlled_unfreeze_run_window_119_20260601T090401Z.json
475. Post-window #119 decision snapshot:
1. reports/qa_gate/p1767_controlled_unfreeze_post_window119_decision_20260601T090401Z.json
476. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
477. RUN_WINDOW_120 executed with PASS_AFTER_FIX (audit env technical fix only).
478. Consolidated evidence:
1. reports/qa_gate/p1768_controlled_unfreeze_run_window_120_20260601T090852Z.json
479. Post-window #120 decision snapshot:
1. reports/qa_gate/p1769_controlled_unfreeze_post_window120_decision_20260601T090852Z.json
480. Decision state remains:
1. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
481. RUN_WINDOW_121 executed with PASS_AFTER_FIX (min/max coverage rerun fix).
482. Consolidated evidence:
483. reports/qa_gate/p1770_controlled_unfreeze_run_window_121_20260601T091605Z.json
484. Post-window #121 decision snapshot:
485. reports/qa_gate/p1771_controlled_unfreeze_post_window121_decision_20260601T091605Z.json
486. Decision state remains:
487. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
488. RUN_WINDOW_122 executed with PASS.
489. Consolidated evidence:
490. reports/qa_gate/p1772_controlled_unfreeze_run_window_122_20260601T091943Z.json
491. Post-window #122 decision snapshot:
492. reports/qa_gate/p1773_controlled_unfreeze_post_window122_decision_20260601T091943Z.json
493. Decision state remains:
494. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
495. RUN_WINDOW_123 executed with PASS.
496. Consolidated evidence:
497. reports/qa_gate/p1774_controlled_unfreeze_run_window_123_20260601T092307Z.json
498. Post-window #123 decision snapshot:
499. reports/qa_gate/p1775_controlled_unfreeze_post_window123_decision_20260601T092307Z.json
500. Decision state remains:
501. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
502. RUN_WINDOW_124 executed with PASS.
503. Consolidated evidence:
504. reports/qa_gate/p1776_controlled_unfreeze_run_window_124_20260601T092641Z.json
505. Post-window #124 decision snapshot:
506. reports/qa_gate/p1777_controlled_unfreeze_post_window124_decision_20260601T092641Z.json
507. Decision state remains:
508. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
509. RUN_WINDOW_125 executed with PASS.
510. Consolidated evidence:
511. reports/qa_gate/p1778_controlled_unfreeze_run_window_125_20260601T093015Z.json
512. Post-window #125 decision snapshot:
513. reports/qa_gate/p1779_controlled_unfreeze_post_window125_decision_20260601T093015Z.json
514. Decision state remains:
515. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).
516. RUN_WINDOW_126 executed with PASS.
517. Consolidated evidence:
518. reports/qa_gate/p1780_controlled_unfreeze_run_window_126_20260601T093342Z.json
519. Post-window #126 decision snapshot:
520. reports/qa_gate/p1781_controlled_unfreeze_post_window126_decision_20260601T093342Z.json
521. Decision state remains:
522. GO_FOR_NEXT_CONTROLLED_WINDOW (temporary unlock only, freeze unchanged).

## 7) Final governance closeout (2026-06-01)
1. STOP_ON_SUCCESS reached on windows `122..126`:
1. run artifacts: `P1772`, `P1774`, `P1776`, `P1778`, `P1780`,
2. post-window decisions: `P1773`, `P1775`, `P1777`, `P1779`, `P1781`,
3. all five windows are `PASS` with `fix.action=not_required`.
2. Final evidence bundle (single package):
1. `reports/qa_gate/p1782_controlled_unfreeze_final_acceptance_package_20260601T110359Z.json`.
3. Final GO/NO-GO decision record:
1. `reports/qa_gate/p1783_controlled_unfreeze_final_governance_decision_20260601T110359Z.json`.
4. Final docs-sync and encoding/readiness audit:
1. `reports/qa_gate/p1784_controlled_unfreeze_closeout_docs_sync_20260601T110831Z.json`.
5. Final decision:
1. `GO_FOR_CONTROLLED_UNFREEZE_CLOSEOUT_COMPLETE`.
6. Governance freeze state after closeout:
1. `project_ready=false`,
2. `enforce_freeze=true`.
7. Next stage (separate policy gate):
1. operator-level decision about production unfreeze timing.
2. policy-gate source: `docs/OPTUNA_PRODUCTION_UNFREEZE_POLICY_GATE_2026-06-01_RU.md`.

## 8) Production policy gate execution (2026-06-01)
1. Final GO decision-record: `reports/qa_gate/p1792_optuna_production_unfreeze_decision_record_final_20260601T120607Z.json`.
2. Step `13.4.2` execution artifact: `reports/qa_gate/p1793_optuna_production_unfreeze_step13_4_2_20260601T120855Z.json`.
3. Step `13.4.3` post-verification artifact: `reports/qa_gate/p1794_optuna_production_unfreeze_step13_4_3_20260601T120855Z.json`.
4. Step `13.4.4` rollback-check artifact: `reports/qa_gate/p1795_optuna_production_unfreeze_step13_4_4_20260601T120855Z.json`.
5. Final post-sync audit: `reports/qa_gate/p1796_optuna_production_unfreeze_execution_post_sync_audit_20260601T121019Z.json`.
6. Freeze state after execution remains unchanged:
1. `project_ready=false`,
2. `enforce_freeze=true`.


