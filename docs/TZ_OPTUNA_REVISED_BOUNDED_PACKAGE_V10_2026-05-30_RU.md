# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V10_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V9 sequence completed under strict split and single-change protocol.
2. Key observations:
1. V9-S2 short improved vs V9-S1 but remained below gate.
2. V9-S3 cross-mode caused dual instability:
1. short reverted to no-trade/negative mix,
2. long lost previously stable positive profile.
3. V9-S4 micro-gate rehearsal => `NO_GO`; V9 package exhausted/not viable.

## 2. V10 objective
1. Recover long stability first (return to all-tradeful positive regime seen in V8-S1).
2. Move short from mixed/no-trade to stable tradeful regime without deep tails.
3. Keep strict bounded reversibility and freeze discipline.

## 3. Bounded Package V10 (strict)
1. V10-S1: long stability restore lock
1. replay long around last stable V8-positive zone,
2. require all-tradeful with non-negative worst branch.
2. V10-S2: short tradeful unlock (narrow)
1. minimal short shift near best V9-S2 branch,
2. reject no-trade domination.
3. V10-S3: short risk-floor compression
1. improve short worst branch toward `>= -10%`,
2. keep all workers tradeful.
4. V10-S4: cross-mode confirmation + micro-gate
1. replay locked short/long pair,
2. evaluate all_tradeful, mean OOS, worst-branch OOS,
3. decide GO-forward or preserve freeze.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed 1d/1d window, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. single-change protocol for each strict step.
4. mandatory checks after every step:
1. pip check,
2. text_guard,
3. readiness --show,
4. ACTIVE + CHANGELOG sync.

## 5. Acceptance unchanged
1. all_tradeful=true per mode,
2. mean OOS >= -2.5% per mode,
3. worst branch OOS >= -10% per mode.
4. on fail: checkpoint + freeze preserved.

## 6. DoD for V10 package task
1. V10 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
