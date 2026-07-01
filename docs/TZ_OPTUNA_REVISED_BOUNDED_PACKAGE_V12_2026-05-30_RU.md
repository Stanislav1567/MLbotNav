# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V12_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V11 sequence completed with `NO_GO` at `V11-S4`.
2. Dominant failure mode:
1. long and short repeatedly converge to no-trade under tighter risk/entry shifts,
2. when tradeful branch appears, tails remain below acceptance floor.

## 2. V12 objective
1. Restore tradeful regime first, then compress tails.
2. Avoid full no-trade collapse from over-constrained profiles.
3. Preserve strict single-change and reversibility.

## 3. Bounded Package V12 (strict)
1. V12-S1: short de-collapse unlock
1. revert one notch from V11 over-tightened profile,
2. single change in `PShortGrid` only.
2. V12-S2: long de-collapse unlock
1. revert one notch from V11 long no-trade profile,
2. single change in `PLongGrid` only.
3. V12-S3: short tail-compression retry
1. keep tradeful unlock profile,
2. single change in `MinExpectedMoveGrid` or `StopLossPct`.
4. V12-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V12 package task
1. V12 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
