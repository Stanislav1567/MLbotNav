# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V27_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V26 sequence completed with `NO_GO` at `V26-S4`.
2. Observed pattern after V26:
1. long mode still keeps one no-trade branch,
2. short mode remains below quality floors and periodically falls back to no-trade in one branch.

## 2. V27 objective
1. Finish long mode tradefulness across all workers.
2. Stabilize short mode without no-trade relapse and compress worst tails.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V27 (strict)
1. V27-S1: long tradefulness unlock continuation
1. single change in `PLongGrid`,
2. keep risk/move settings unchanged.
2. V27-S2: short entry re-anchor continuation
1. single change in `PShortGrid`,
2. preserve V26-S3 risk profile.
3. V27-S3: short risk/move micro-correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V27-S2 entry profile.
4. V27-S4: cross-mode confirmation + micro-gate
1. evaluate both modes under unchanged acceptance gates,
2. lock `GO_FORWARD` or `NO_GO`.

## 4. Hard constraints
1. `short_only` and `long_only` strictly separated.
2. fixed 1d/1d window, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`.
3. one strict change per step.
4. after every step: `pip check`, `text_guard`, `readiness --show`, `ACTIVE/CHANGELOG` sync.

## 5. Acceptance unchanged
1. `all_tradeful=true` per mode.
2. `mean OOS >= -2.5%` per mode.
3. `worst branch OOS >= -10%` per mode.

## 6. DoD for V27 package task
1. V27 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
