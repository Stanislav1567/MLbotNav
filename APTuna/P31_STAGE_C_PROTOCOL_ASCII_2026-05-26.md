# P31 Stage C Protocol (ASCII Mirror)

Date: 2026-05-26  
Scope: Optuna post-A/B candidate replay  
Rule: long_only and short_only must stay isolated

## Goal
1. Replay top candidates from stage A/B on longer OOS windows.
2. Keep long and short in separate contours.
3. Provide reusable templates for C30 and C60.

## Candidate Set
1. long_only (from P28):
   1. horizon_bars=3
   2. p_enter_long=0.54
   3. p_enter_short=0.46
   4. min_expected_move_pct=0.002
   5. trend_filter=min_max_range_revert
   6. min_abs_ema_gap=0.0
2. short_only (from P30):
   1. horizon_bars=3
   2. p_enter_long=0.52
   3. p_enter_short=0.48
   4. min_expected_move_pct=0.001
   5. trend_filter=swing_lh_ll_short
   6. min_abs_ema_gap=0.0

## Stage C Windows
1. C30:
   1. train: 2026-03-27..2026-04-25
   2. test: 2026-04-26..2026-05-25
2. C60:
   1. train: 2026-01-26..2026-03-26
   2. test: 2026-03-27..2026-05-25

## Execution Templates
1. Use commands from:
   1. `APTuna/P31_STAGE_C_PROTOCOL_2026-05-26_RU.md`
2. Keep required flags:
   1. `--window-policy multiday`
   2. `--disable-hypothesis-profile`
   3. `--disable-backlog-active-append`
   4. `--temporary-unlock-readiness` (only for controlled calibration runs)

## Logging Requirements
1. After each run, log into:
   1. `docs/ACTIVE_WORK_ITEMS_RU.md`
   2. `docs/CHANGELOG_CHRONOLOGY_RU.md`
2. Required metrics:
   1. status
   2. oos_net_return_pct
   3. trades
   4. pass_candidates / goal_candidates
   5. candidate_pool
