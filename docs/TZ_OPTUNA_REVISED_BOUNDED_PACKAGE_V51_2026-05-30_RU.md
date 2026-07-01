# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V51_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V50 sequence completed with NO_GO at V50-S4.
2. Observed pattern after V50:
1. long mode remains non-viable (search_failed persistence),
2. short mode remains below acceptance floors even when tradefulness is preserved.

## 2. V51 objective
1. Continue long viability recovery with next bounded entry-shift.
2. Continue short quality stabilization with one-change protocol.
3. Preserve strict reversibility and auditability of each step.

## 3. Bounded Package V51 (strict)
1. V51-S1: long tradefulness unlock continuation.
`PLongGrid=0.21,0.20,0.19`; `MinExpectedMoveGrid=0.0020,0.0022,0.0024`; `MinCandidateTrades=3`.
2. V51-S2: short entry re-anchor continuation.
`PShortGrid=0.18,0.17,0.16`; `StopLossPct=0.0020` preserved.
3. V51-S3: short risk/move micro-correction.
`StopLossPct=0.0016`; V51-S2 entry profile preserved.
4. V51-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed 1d/1d window, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. one strict change per step.
4. after every step: pip check, text_guard, readiness --show, ACTIVE/CHANGELOG sync.

## 5. Acceptance unchanged
1. all_tradeful=true per mode.
2. mean OOS >= -2.5% per mode.
3. worst branch OOS >= -10% per mode.

## 6. DoD for V51 package task
1. V51 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
