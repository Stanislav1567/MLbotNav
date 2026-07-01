# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V14_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V13 sequence completed with `NO_GO` at `V13-S4`.
2. Current pattern:
1. long can leave full no-trade, but remains unstable with one weak/no-trade branch,
2. short can improve best branch, but one deep tail still collapses mode-level gates.

## 2. V14 objective
1. Stabilize long after partial unlock (remove no-trade branch).
2. Reduce short tail variance while preserving tradefulness.
3. Keep strict single-change reversibility.

## 3. Bounded Package V14 (strict)
1. V14-S1: long branch stabilization
1. single change in `PLongGrid` around V13-S1 neighborhood,
2. keep risk/move settings unchanged.
2. V14-S2: short tail guard via entry pressure
1. single change in `PShortGrid`,
2. keep `MinExpectedMoveGrid` and risk block unchanged.
3. V14-S3: short risk-floor correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V14-S2 entry profile.
4. V14-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V14 package task
1. V14 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
