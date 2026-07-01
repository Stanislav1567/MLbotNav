# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V9_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V8 sequence completed under strict split and single-change protocol.
2. Key observations:
1. V8-S1 long reached full mode pass (`3/3` tradeful, positive across workers).
2. V8-S2 short remained negative but became stable.
3. V8-S3 cross-mode showed short regime near transition: two no-trade branches and one moderate-loss tradeful branch (`-12.0432%`, trades=5).
4. V8-S4 micro-gate rehearsal => `NO_GO` due to short mode gates.

## 2. V9 objective
1. Preserve achieved long-mode stability from V8-S1/V8-S3.
2. Convert short mode from mixed no-trade/negative state into stable tradeful near-threshold profile.
3. Keep strict bounded reversibility and freeze discipline.

## 3. Bounded Package V9 (strict)
1. V9-S1: short tradeful-floor unlock
1. move short thresholds minimally toward trade activation,
2. target removal of no-trade branches,
3. prevent return to deep overtrade tails.
2. V9-S2: short risk-floor compression
1. compress worst-branch drawdown toward `>= -10%`,
2. keep tradeful output on all workers.
3. V9-S3: cross-mode confirmation
1. replay locked short (V9) + locked long (V8-stable),
2. verify short/long both satisfy mode-level stability.
4. V9-S4: micro-gate rehearsal
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

## 6. DoD for V9 package task
1. V9 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
