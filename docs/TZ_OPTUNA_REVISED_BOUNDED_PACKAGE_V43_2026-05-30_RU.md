# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V43_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V42 sequence completed with `NO_GO` at `V42-S4`.
2. Observed pattern after V42:
1. long mode remained non-viable (`search_failed` persistence),
2. short mode improved tails vs prior packages but still below acceptance floors.

## 2. V43 objective
1. Recover long viability from persistent search failure.
2. Preserve short tradefulness and continue tightening mean/worst OOS.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V43 (strict)
1. V43-S1: long tradefulness unlock continuation.
2. V43-S2: short entry re-anchor continuation.
3. V43-S3: short risk/move micro-correction.
4. V43-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. `short_only` and `long_only` strictly separated.
2. fixed 1d/1d window, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`.
3. one strict change per step.
4. after every step: `pip check`, `text_guard`, `readiness --show`, `ACTIVE/CHANGELOG` sync.

## 5. Acceptance unchanged
1. `all_tradeful=true` per mode.
2. `mean OOS >= -2.5%` per mode.
3. `worst branch OOS >= -10%` per mode.

## 6. DoD for V43 package task
1. V43 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
