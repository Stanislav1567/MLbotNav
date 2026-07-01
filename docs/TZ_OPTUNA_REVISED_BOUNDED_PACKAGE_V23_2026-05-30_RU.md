# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V23_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V22 sequence completed with `NO_GO` at `V22-S4`.
2. Observed pattern after V22:
1. long mode still fails `all_tradeful` due to persistent no-trade branches,
2. short mode remains unstable: one branch can improve, but heavy tail branch keeps collapsing.

## 2. V23 objective
1. Force long mode out of no-trade lock with bounded entry unlock.
2. Stabilize short distribution and reduce worst-branch downside.
3. Keep strict one-change-per-step reversibility.

## 3. Bounded Package V23 (strict)
1. V23-S1: long tradefulness unlock retry
1. single change in `PLongGrid`,
2. keep risk/move settings unchanged.
2. V23-S2: short tail stabilization continuation
1. single change in `PShortGrid`,
2. preserve V22-S3 risk profile.
3. V23-S3: short risk/move micro-correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V23-S2 entry profile.
4. V23-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V23 package task
1. V23 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
