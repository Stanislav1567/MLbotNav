# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V6_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V5 sequence completed under strict split and single-change protocol.
2. Key observations:
1. V5-S2 short compression initially reduced tail versus V4-S1 but was unstable on replay.
2. V5-S3 short collapsed to overtrade tail (`~ -77%`, `37-41 trades`).
3. V5-S3 long collapsed to no-trade (`0 trades` across all workers).
4. V5-S4 micro-gate rehearsal produced `NO_GO`; V5 package is exhausted/not viable.

## 2. V6 objective
1. For short mode: suppress overtrade tail while keeping tradeful behavior.
2. For long mode: remove no-trade domination while preserving bounded risk.
3. Keep execution fully reversible and bounded.

## 3. Bounded Package V6 (strict)
1. V6-S1: short de-overtrade guard
1. tighten short entry upward and raise move floor around latest tradeful branch,
2. keep tp-guard fixed,
3. require tradeful output with reduced trade count dispersion.
2. V6-S2: long anti-no-trade unlock
1. shift long entry and move floor slightly toward tradeful activation zone,
2. keep risk cadence fixed,
3. reject any all-no-trade result.
3. V6-S3: cross-mode stability check
1. run short/long with locked V6 pair,
2. verify that selector does not revert to no-trade in one mode while the other overtrades.
4. V6-S4: U1 micro-gate rehearsal
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

## 6. DoD for V6 package task
1. V6 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
