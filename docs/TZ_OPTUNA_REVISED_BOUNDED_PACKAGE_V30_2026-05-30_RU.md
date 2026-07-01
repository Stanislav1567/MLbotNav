# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V30_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V29 sequence completed with `NO_GO` at `V29-S4`.
2. Observed pattern after V29:
1. long mode stayed in full no-trade collapse on `PLongGrid=0.43,0.42,0.41`,
2. short mode stayed tradeful but with deep negative tails (`mean/worst` far below acceptance).

## 2. V30 objective
1. Break long no-trade collapse with one bounded unlock shift.
2. Keep short tradefulness while reducing worst-tail amplitude.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V30 (strict)
1. V30-S1: long tradefulness unlock continuation
1. single change in `PLongGrid`,
2. keep risk/move settings unchanged.
2. V30-S2: short entry re-anchor continuation
1. single change in `PShortGrid`,
2. preserve V29-S3 risk profile.
3. V30-S3: short risk/move micro-correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V30-S2 entry profile.
4. V30-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V30 package task
1. V30 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
