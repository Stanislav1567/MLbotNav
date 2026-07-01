# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V3_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V2 bounded sequence completed end-to-end:
1. V2-F1-A stop_loss_pct,
2. V2-F1-B take_profit_pct,
3. V2-F2-C min_tp_reach_prob,
4. V2-F2-D tp_min_factor,
5. V2-F3-E min_expected_move.
2. All five bounded families rejected under U1 criteria.
3. Current strict state: freeze lock preserved, no immediate uncontrolled variant runs.

## 2. V2 factual outcomes
1. Short mode stayed tradeful but deeply negative across families.
2. Long mode repeatedly drifted into no-trade or remained strongly negative when tradeful.
3. Best V2-F3-E long branch improved tradefulness (`trades=6`) but still below gate (`oos=-15.1061%`).
4. U1 acceptance not reached:
1. all_tradeful=true not stable across both modes,
2. mean OOS threshold not met,
3. worst-branch threshold not met.

## 3. Bounded Package V3 (strict)
1. V3-S1: controlled entry band rebalance (narrow only)
1. p_short narrow raise band,
2. p_long narrow lower band,
3. no simultaneous risk-family changes.
2. V3-S2: micro risk-cadence retune (cooldown only)
1. cooldown narrow 3-point band per mode.
3. V3-S3: conditional min_expected_move + tp-reach coupling
1. short: min_expected_move narrow high side,
2. long: min_expected_move narrow low side,
3. tp reach guard remains fixed during this step.
4. V3-S4: tp guard micro-pair confirmation
1. min_tp_reach_prob and tp_min_factor tested in paired but still bounded 3-point grids,
2. only after V3-S1..S3 checkpoints.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed window 1d/1d, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. single-change protocol per strict step.
4. After each step mandatory checks:
1. pip check,
2. text_guard,
3. readiness --show,
4. ACTIVE + CHANGELOG sync.

## 5. U1/U2 acceptance remains unchanged
1. all_tradeful=true per mode,
2. mean OOS >= -2.5% per mode,
3. worst branch OOS >= -10% per mode.
4. If fail: checkpoint + freeze preserved.

## 6. Definition of Done for V3 package task
1. V3 package document created and referenced from execution priorities.
2. ACTIVE/CHANGELOG synchronized.
3. Mandatory audits PASS.
