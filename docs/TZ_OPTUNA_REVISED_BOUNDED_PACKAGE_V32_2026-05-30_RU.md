# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V32_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V31 sequence completed with `NO_GO` at `V31-S4`.
2. Observed pattern after V31:
1. long mode reached partial unlock (`1/3` tradeful), but not full tradefulness,
2. short mode remained tradeful but below acceptance quality floors.

## 2. V32 objective
1. Convert long partial unlock into full tradefulness.
2. Keep short tradefulness and reduce downside tails.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V32 (strict)
1. V32-S1: long tradefulness unlock continuation
1. single change in `PLongGrid`,
2. keep risk/move settings unchanged.
2. V32-S2: short entry re-anchor continuation
1. single change in `PShortGrid`,
2. preserve V31-S3 risk profile.
3. V32-S3: short risk/move micro-correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V32-S2 entry profile.
4. V32-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V32 package task
1. V32 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
