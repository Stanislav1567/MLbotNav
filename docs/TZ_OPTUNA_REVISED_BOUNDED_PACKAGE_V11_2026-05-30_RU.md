# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V11_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V10 sequence completed with `NO_GO` at `V10-S4`.
2. Main failure profile:
1. long remained unstable (one positive branch + deep negative tails),
2. short stayed tradeful but quality collapsed (`mean`/`worst` far below gates).

## 2. V11 objective
1. Compress short-side negative tails first while preserving tradefulness.
2. Re-lock long into non-degrading profile with bounded single-change steps.
3. Keep strict reversibility and freeze discipline.

## 3. Bounded Package V11 (strict)
1. V11-S1: short tail-compression (entry threshold shift)
1. keep `MinExpectedMoveGrid` from V10-S3,
2. single change: compress `PShortGrid` toward safer floor.
2. V11-S2: long stability correction
1. replay long around reduced entry pressure,
2. single change in `PLongGrid` only.
3. V11-S3: short execution-risk correction
1. keep V11-S1 entry profile,
2. single change in risk block (`StopLossPct` or `TakeProfitPct`).
4. V11-S4: cross-mode confirmation + micro-gate
1. evaluate both modes under unchanged acceptance rules,
2. fix `GO_FORWARD` or `NO_GO`.

## 4. Hard constraints
1. `short_only` and `long_only` strictly separated.
2. fixed 1d/1d window, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`.
3. single-change protocol for each strict step.
4. mandatory checks after every step:
1. `pip check`,
2. `text_guard`,
3. `readiness --show`,
4. `ACTIVE + CHANGELOG` sync.

## 5. Acceptance unchanged
1. `all_tradeful=true` per mode.
2. `mean OOS >= -2.5%` per mode.
3. `worst branch OOS >= -10%` per mode.
4. on fail: checkpoint + freeze preserved.

## 6. DoD for V11 package task
1. V11 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
