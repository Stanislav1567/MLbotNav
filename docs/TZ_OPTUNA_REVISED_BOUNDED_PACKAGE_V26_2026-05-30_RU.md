# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V26_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V25 sequence completed with `NO_GO` at `V25-S4`.
2. Observed pattern after V25:
1. long mode improved from full collapse to mixed tradefulness, but still kept one no-trade branch and negative tail,
2. short mode remained deeply negative and in S3 reintroduced no-trade branch.

## 2. V26 objective
1. Push long mode to fully tradeful profile across all workers.
2. Compress short downside tails while preventing no-trade relapse.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V26 (strict)
1. V26-S1: long tradefulness unlock continuation
1. single change in `PLongGrid` (further threshold easing),
2. keep risk/move settings unchanged.
2. V26-S2: short entry re-anchor continuation
1. single change in `PShortGrid`,
2. preserve V25-S3 risk profile.
3. V26-S3: short risk/move micro-correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V26-S2 entry profile.
4. V26-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V26 package task
1. V26 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
