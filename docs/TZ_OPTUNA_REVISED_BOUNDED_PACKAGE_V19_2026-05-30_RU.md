# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V19_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V18 sequence completed with `NO_GO` at `V18-S4`.
2. Observed pattern after V18:
1. long mode still has persistent no-trade branches under entry-only rebalance,
2. short mode became fully tradeful in S3 and narrowed dispersion, but mean/worst remain below unchanged gates.

## 2. V19 objective
1. Reduce long no-trade persistence while preserving near-neutral branch.
2. Continue short tail compression from V18-S3 baseline.
3. Keep strict one-change-per-step reversibility.

## 3. Bounded Package V19 (strict)
1. V19-S1: long tradefulness unlock retry
1. single change in `PLongGrid`,
2. keep risk/move settings unchanged.
2. V19-S2: short tail trim continuation
1. single change in `PShortGrid`,
2. preserve V18-S3 risk profile.
3. V19-S3: short risk/move micro-correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V19-S2 entry profile.
4. V19-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V19 package task
1. V19 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
