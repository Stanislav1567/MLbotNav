# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V25_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V24 sequence completed with `NO_GO` at `V24-S4`.
2. Observed pattern after V24:
1. long mode remained non-tradeful (`all_tradeful=false`) with full no-trade branch collapse,
2. short mode kept deep negative tails and reintroduced no-trade branch in S3.

## 2. V25 objective
1. Restore long tradefulness without reopening catastrophic downside tails.
2. Re-stabilize short mode after S3 no-trade relapse.
3. Keep strict one-change-per-step reversibility.

## 3. Bounded Package V25 (strict)
1. V25-S1: long tradefulness unlock retry
1. single change in `PLongGrid` (lower thresholds versus V24-S1),
2. keep risk/move settings unchanged.
2. V25-S2: short entry re-anchor
1. single change in `PShortGrid`,
2. preserve risk profile from V24-S3.
3. V25-S3: short risk/move micro-correction
1. single change in `StopLossPct` or `MinExpectedMoveGrid`,
2. preserve V25-S2 entry profile.
4. V25-S4: cross-mode confirmation + micro-gate
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

## 6. DoD for V25 package task
1. V25 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
