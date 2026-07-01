# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V15_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V14 sequence completed with `NO_GO` at `V14-S4`.
2. Observed pattern after V14:
1. long mode still keeps no-trade instability in one or more branches,
2. short mode became tradeful but stayed deeply negative and failed mean/worst gates.

## 2. V15 objective
1. Force long mode into fully tradeful profile without introducing deep negative tails.
2. Compress short negative basin with guarded single-change adjustments.
3. Keep strict reversibility and one-change-per-step discipline.

## 3. Bounded Package V15 (strict)
1. V15-S1: long tradefulness unlock
1. single change in `PLongGrid` only,
2. keep risk/move settings unchanged.
2. V15-S2: short entry selectivity rebalance
1. single change in `PShortGrid`,
2. preserve V14-S3 risk profile.
3. V15-S3: short move/risk compression
1. single change in `MinExpectedMoveGrid` or `StopLossPct`,
2. preserve V15-S2 entry profile.
4. V15-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V15 package task
1. V15 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
