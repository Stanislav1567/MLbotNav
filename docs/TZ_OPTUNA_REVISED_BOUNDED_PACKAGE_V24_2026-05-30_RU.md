# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V24_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V23 sequence completed with `NO_GO` at `V23-S4`.
2. Observed pattern after V23:
1. long mode collapsed to full no-trade in S1,
2. short mode improved best branch to `-6.1219%`, but mean/worst still far below gate.

## 2. V24 objective
1. Recover long tradefulness from no-trade collapse.
2. Continue short tail compression without reintroducing no-trade branches.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V24 (strict)
1. V24-S1: long anti-collapse unlock
1. single change in `PLongGrid`,
2. keep risk/move settings unchanged.
2. V24-S2: short tail stabilization continuation
1. single change in `PShortGrid`,
2. preserve V23-S3 risk profile.
3. V24-S3: short risk/move micro-correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V24-S2 entry profile.
4. V24-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V24 package task
1. V24 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
