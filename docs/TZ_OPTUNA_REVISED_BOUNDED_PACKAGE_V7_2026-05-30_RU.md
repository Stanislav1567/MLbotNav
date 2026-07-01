# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V7_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V6 sequence completed with strict split and single-change protocol.
2. Key observations:
1. V6-S1 short reduced overtrade tail but produced selector no-trade instability.
2. V6-S2 long produced one positive branch (`+1.2904%`, trades=1) while 2/3 workers remained no-trade.
3. V6-S3 cross-mode replay lost long partial recovery and returned both modes to unstable no-trade/negative mix.
4. V6-S4 micro-gate rehearsal => `NO_GO`; V6 package exhausted/not viable.

## 2. V7 objective
1. Preserve the V6-S2 long partial-positive branch and improve reproducibility.
2. Keep short mode out of catastrophic overtrade while avoiding selector no-trade dominance.
3. Maintain strict bounded reversibility.

## 3. Bounded Package V7 (strict)
1. V7-S1: long reproducibility micro-lock
1. replay long around V6-S2 positive branch with minimal bounded spread,
2. require at least 2/3 tradeful outcomes.
2. V7-S2: short anti-collapse guard
1. tighten short with moderate move floor (between V6-S1 and V6-S3 outcomes),
2. reject both extremes: no-trade domination and high-trade collapse.
3. V7-S3: cross-mode stability check
1. run locked V7 pair for short/long,
2. verify that long partial recovery survives and short does not collapse.
4. V7-S4: micro-gate rehearsal
1. evaluate all_tradeful, mean OOS, worst-branch OOS,
2. decide GO-forward to next package or preserve freeze.

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

## 6. DoD for V7 package task
1. V7 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
