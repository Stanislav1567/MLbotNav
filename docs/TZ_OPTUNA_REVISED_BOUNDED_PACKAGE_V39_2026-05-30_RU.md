# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V39_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V38 sequence completed with `NO_GO` at `V38-S4`.
2. Observed pattern after V38:
1. long mode remained non-viable (`search_failed` pattern),
2. short mode regressed into no-trade collapse after V38-S3 risk micro-change.

## 2. V39 objective
1. Recover long viability from persistent search failure.
2. Restore short tradefulness from no-trade collapse while constraining tails.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V39 (strict)
1. V39-S1: long tradefulness unlock continuation.
2. V39-S2: short entry re-anchor continuation.
3. V39-S3: short risk/move micro-correction.
4. V39-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. `short_only` and `long_only` strictly separated.
2. fixed 1d/1d window, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`.
3. one strict change per step.
4. after every step: `pip check`, `text_guard`, `readiness --show`, `ACTIVE/CHANGELOG` sync.

## 5. Acceptance unchanged
1. `all_tradeful=true` per mode.
2. `mean OOS >= -2.5%` per mode.
3. `worst branch OOS >= -10%` per mode.

## 6. DoD for V39 package task
1. V39 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
