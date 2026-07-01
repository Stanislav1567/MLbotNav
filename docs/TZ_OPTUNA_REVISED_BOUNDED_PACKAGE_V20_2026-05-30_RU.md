# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V20_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V19 sequence completed with `NO_GO` at `V19-S4`.
2. Observed pattern after V19:
1. long mode collapsed into full no-trade profile (`0/0` on all workers),
2. short mode removed no-trade in S3 but remained deeply negative (`mean=-29.0991%`, `worst=-30.4731%`).

## 2. V20 objective
1. Force long mode out of zero-trade collapse with entry unlock shift.
2. Continue short stabilization from V19-S3 with stricter entry profile before risk micro-step.
3. Keep strict one-change-per-step reversibility.

## 3. Bounded Package V20 (strict)
1. V20-S1: long anti-collapse unlock
1. single change in `PLongGrid`,
2. keep risk/move settings unchanged.
2. V20-S2: short entry-risk balance reset
1. single change in `PShortGrid`,
2. preserve V19-S3 risk profile.
3. V20-S3: short risk/move micro-correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V20-S2 entry profile.
4. V20-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V20 package task
1. V20 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
