# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V49_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V48 sequence completed with NO_GO at V48-S4.
2. Observed pattern after V48:
1. long mode remains non-viable (search_failed persistence),
2. short mode remains below acceptance floors with unstable tails.

## 2. V49 objective
1. Recover long viability from persistent search failure.
2. Stabilize short mean/worst OOS while preserving tradefulness.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V49 (strict)
1. V49-S1: long tradefulness unlock continuation.
2. V49-S2: short entry re-anchor continuation.
3. V49-S3: short risk/move micro-correction.
4. V49-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed 1d/1d window, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. one strict change per step.
4. after every step: pip check, text_guard, readiness --show, ACTIVE/CHANGELOG sync.

## 5. Acceptance unchanged
1. all_tradeful=true per mode.
2. mean OOS >= -2.5% per mode.
3. worst branch OOS >= -10% per mode.

## 6. DoD for V49 package task
1. V49 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
