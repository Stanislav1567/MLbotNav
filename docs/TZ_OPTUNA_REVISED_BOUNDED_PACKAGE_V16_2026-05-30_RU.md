# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V16_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V15 sequence completed with `NO_GO` at `V15-S4`.
2. Observed pattern after V15:
1. long mode still unstable with no-trade branch under selected grids,
2. short mode can improve best branch, but mean/worst remain below acceptance gates and regress under stricter move filters.

## 2. V16 objective
1. Eliminate no-trade branch on long mode with bounded entry rebalance.
2. Keep short mode tradeful while clipping negative tail without over-tightening into no-trade.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V16 (strict)
1. V16-S1: long branch rebalance
1. single change in `PLongGrid`,
2. keep risk/move settings unchanged.
2. V16-S2: short tail clipping via entry threshold
1. single change in `PShortGrid`,
2. preserve V15 risk profile.
3. V16-S3: short risk-floor micro-adjustment
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V16-S2 entry profile.
4. V16-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V16 package task
1. V16 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
