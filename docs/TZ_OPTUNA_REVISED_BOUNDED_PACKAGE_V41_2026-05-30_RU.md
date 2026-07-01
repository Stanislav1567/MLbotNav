# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V41_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V40 sequence completed with `NO_GO` at `V40-S4`.
2. Observed pattern after V40:
1. long mode remained non-viable (`search_failed` persistence),
2. short mode improved in V40-S3 but still missed quality floors.

## 2. V41 objective
1. Recover long viability from persistent search failure.
2. Preserve short tradefulness and push mean/worst OOS to acceptance zone.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V41 (strict)
1. V41-S1: long tradefulness unlock continuation.
2. V41-S2: short entry re-anchor continuation.
3. V41-S3: short risk/move micro-correction.
4. V41-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. `short_only` and `long_only` strictly separated.
2. fixed 1d/1d window, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`.
3. one strict change per step.
4. after every step: `pip check`, `text_guard`, `readiness --show`, `ACTIVE/CHANGELOG` sync.

## 5. Acceptance unchanged
1. `all_tradeful=true` per mode.
2. `mean OOS >= -2.5%` per mode.
3. `worst branch OOS >= -10%` per mode.

## 6. DoD for V41 package task
1. V41 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
