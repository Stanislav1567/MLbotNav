# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V38_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V37 sequence completed with `NO_GO` at `V37-S4`.
2. Observed pattern after V37:
1. long mode remained non-viable (search_failed/no-trade),
2. short mode stayed tradeful but quality tails remained far below acceptance floors.

## 2. V38 objective
1. Recover long tradefulness/viability from persistent long collapse.
2. Keep short tradefulness and reduce downside tails.
3. Preserve strict one-change-per-step reversibility.

## 3. Bounded Package V38 (strict)
1. V38-S1: long tradefulness unlock continuation.
2. V38-S2: short entry re-anchor continuation.
3. V38-S3: short risk/move micro-correction.
4. V38-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. `short_only` and `long_only` strictly separated.
2. fixed 1d/1d window, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`.
3. one strict change per step.
4. after every step: `pip check`, `text_guard`, `readiness --show`, `ACTIVE/CHANGELOG` sync.

## 5. Acceptance unchanged
1. `all_tradeful=true` per mode.
2. `mean OOS >= -2.5%` per mode.
3. `worst branch OOS >= -10%` per mode.
