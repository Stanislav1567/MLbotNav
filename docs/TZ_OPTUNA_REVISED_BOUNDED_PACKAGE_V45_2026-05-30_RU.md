# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V45_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V44 sequence completed with `NO_GO` at `V44-S4`.
2. Observed pattern after V44:
1. long mode remained non-viable (`search_failed` persistence),
2. short mode still below acceptance floors and unstable tails across S2/S3.

## 2. V45 objective
1. Recover long viability from persistent search failure.
2. Preserve short tradefulness and stabilize mean/worst OOS.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V45 (strict)
1. V45-S1: long tradefulness unlock continuation.
2. V45-S2: short entry re-anchor continuation.
3. V45-S3: short risk/move micro-correction.
4. V45-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. `short_only` and `long_only` strictly separated.
2. fixed 1d/1d window, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`.
3. one strict change per step.
4. after every step: `pip check`, `text_guard`, `readiness --show`, `ACTIVE/CHANGELOG` sync.

## 5. Acceptance unchanged
1. `all_tradeful=true` per mode.
2. `mean OOS >= -2.5%` per mode.
3. `worst branch OOS >= -10%` per mode.

## 6. DoD for V45 package task
1. V45 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
