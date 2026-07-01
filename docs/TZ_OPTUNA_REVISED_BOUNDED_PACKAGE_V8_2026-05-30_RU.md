# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V8_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V7 sequence completed under strict split and single-change protocol.
2. Key observations:
1. V7-S1 long improved reproducibility (`2/3 goal_pass`, best `+3.7097%`, trades 4), but one no-trade branch remains.
2. V7-S2 short avoided full no-trade collapse but stayed deeply negative.
3. V7-S3 cross-mode replay: long retained only partial-positive branch, short remained below gate.
4. V7-S4 micro-gate rehearsal => `NO_GO`; V7 package exhausted/not viable.

## 2. V8 objective
1. Complete long reproducibility to all-tradeful profile (remove no-trade branch).
2. Reduce short drawdown while preserving tradeful execution.
3. Keep all changes bounded, reversible, and isolated from ML runtime.

## 3. Bounded Package V8 (strict)
1. V8-S1: long all-tradeful completion
1. replay around V7-S1 positive zone with minimal bounded spread,
2. enforce tradeful output on every worker.
2. V8-S2: short drawdown compression
1. shift short threshold/move floor to reduce deep-loss tails,
2. reject no-trade domination and reject overtrade collapse.
3. V8-S3: cross-mode stability replay
1. run locked V8 pair short/long,
2. verify both modes remain tradeful and no branch collapses below risk floor.
4. V8-S4: micro-gate rehearsal
1. evaluate all_tradeful, mean OOS, worst-branch OOS,
2. decide GO-forward or preserve freeze.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed 1d/1d window, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. single-change protocol for each strict step.
4. mandatory checks after every step:
1. pip check,
2. text_guard,
3. readiness --show,
4. ACTIVE + CHANGELOG sync.

## 5. Acceptance unchanged
1. all_tradeful=true per mode,
2. mean OOS >= -2.5% per mode,
3. worst branch OOS >= -10% per mode.
4. on fail: checkpoint + freeze preserved.

## 6. DoD for V8 package task
1. V8 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
