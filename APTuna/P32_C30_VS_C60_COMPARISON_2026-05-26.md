# P32 Comparison: C30 vs C60 (Long/Short Split)

Date: 2026-05-26  
Symbol/TF: SOLUSDT 1m  
Method: fixed top-candidate replay from P28/P30

## Data Availability
1. Initial state (before backfill): raw 1m range covered only 2026-04-21..2026-05-21.
2. Missing C60 train window (2026-01-26..2026-03-26) was loaded by backfill.
3. Backfill artifact: `reports/ingestion/backfill_SOLUSDT_2026-01-26_2026-03-26_20260526T143114Z.json`.
4. Backfill status: `days_success=60`, `days_failed=0`.

## C30 Results
| contour | train window | test window | status | OOS net % | trades |
|---|---|---|---|---:|---:|
| long_only_c30 | 2026-03-27..2026-04-25 | 2026-04-26..2026-05-25 | goal_fail | -18.6645 | 13 |
| short_only_c30 | 2026-03-27..2026-04-25 | 2026-04-26..2026-05-25 | goal_fail | -70.9191 | 35 |

Note:
1. Status/metrics are taken from `history[0]` in adaptive loop summary files.

Sources:
1. reports/adaptive/long_only_c30/adaptive_loop_SOLUSDT_1m_2026-04-26_20260526T140138Z.json
2. reports/adaptive/short_only_c30/adaptive_loop_SOLUSDT_1m_2026-04-26_20260526T140311Z.json

## C60 Attempts (Before Backfill)
| contour | requested train window | requested test window | status | blocker |
|---|---|---|---|---|
| long_only_c60 | 2026-01-26..2026-03-26 | 2026-03-27..2026-05-25 | search_failed | missing raw 1m files |
| short_only_c60 | 2026-01-26..2026-03-26 | 2026-03-27..2026-05-25 | search_failed | missing raw 1m files |

Blocker signature:
1. `FileNotFoundError: No part-final.csv ... range=(2026-01-26, 2026-03-26)`.

Sources:
1. `reports/adaptive/long_only_c60/adaptive_loop_SOLUSDT_1m_2026-03-27_20260526T140959Z.json`
2. `reports/adaptive/short_only_c60/adaptive_loop_SOLUSDT_1m_2026-03-27_20260526T141046Z.json`

## C60 Replay (After Backfill)
| contour | train window | test window | status | OOS net % | trades | pass_candidates | goal_candidates | candidate_pool |
|---|---|---|---|---:|---:|---:|---:|---:|
| long_only_c60_r1 | 2026-01-26..2026-03-26 | 2026-03-27..2026-05-25 | goal_fail | -0.3188 | 5 | 0 | 0 | 1 |
| short_only_c60_r1 | 2026-01-26..2026-03-26 | 2026-03-27..2026-05-25 | goal_fail | -90.6664 | 66 | 0 | 0 | 1 |

Notes:
1. Metrics are taken from `history[0]` in adaptive loop summary files.
2. Runs were executed with isolated contours (`long_only_c60_r1` and `short_only_c60_r1`) to avoid stale negative memory carry-over from blocked attempts.

Sources:
1. `reports/adaptive/long_only_c60_r1/adaptive_loop_SOLUSDT_1m_2026-03-27_20260526T143126Z.json`
2. `reports/adaptive/short_only_c60_r1/adaptive_loop_SOLUSDT_1m_2026-03-27_20260526T143524Z.json`

## Decision
1. C30 execution remains complete and reproducible for both contours.
2. C60 is now executable after backfill; blocker is removed.
3. Quality remains below target in both contours (`goal_fail`), with severe degradation on `short_only_c60_r1`.
4. Next strict step by TZ order: move from replay diagnostics to targeted space/policy remediation for short branch before any wider stage expansion.

## P50 Strict Remediation Note
1. A strict short C60 remediation run was executed without fallback candidate selection (`allow_subgoal` disabled, `goal=0.0`).
2. First attempt was blocked by preflight due incomplete raw test-day markers; missing raw range was backfilled (`2026-03-27..2026-05-25`, `60/60` success).
3. Re-run result:
   1. contour: `short_only_c60_p50_r1`
   2. `candidate_pool=72`
   3. `status=no_goal_candidate` (no weak candidate accepted)
4. Artifacts:
   1. `reports/qa_gate/preflight_window_20260526T144449Z.json`
   2. `reports/ingestion/backfill_SOLUSDT_2026-03-27_2026-05-25_20260526T145716Z.json`
   3. `reports/adaptive/short_only_c60_p50_r1/adaptive_loop_SOLUSDT_1m_2026-03-27_20260526T145740Z.json`
   4. `reports/pipeline/search_gate_candidate_SOLUSDT_1m_20260526T150733Z.json`
