# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V13_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V12 sequence completed with `NO_GO` at `V12-S4`.
2. Observed regime:
1. long side stuck in no-trade under current entry pressure,
2. short side alternates between no-trade and deep negative tails.

## 2. V13 objective
1. Break long no-trade lock with minimal reversible change.
2. Keep short tradeful while reducing extreme downside tails.
3. Preserve strict split/single-change execution discipline.

## 3. Bounded Package V13 (strict)
1. V13-S1: long unlock retry
1. single change in `PLongGrid` (one notch softer vs V12-S2),
2. keep move/risk block unchanged.
2. V13-S2: short unlock stabilization
1. single change in `PShortGrid` around latest tradeful branch,
2. keep `MinExpectedMoveGrid` unchanged.
3. V13-S3: short risk-floor correction
1. single change in risk or move block (`StopLossPct` or `MinExpectedMoveGrid`),
2. preserve entry profile from V13-S2.
4. V13-S4: cross-mode confirmation + micro-gate
1. evaluate both modes with unchanged acceptance gates,
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

## 6. DoD for V13 package task
1. V13 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
