# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V56_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V55 sequence completed with NO_GO at V55-S4.
2. Observed pattern after V55:
1. long mode remains non-viable (search_failed persistence),
2. short mode still fails acceptance and loses tradefulness under deeper stop-loss tightening.

## 2. V56 objective
1. Continue long viability recovery with bounded entry shift.
2. Continue short stabilization with strict one-change protocol.
3. Preserve reversibility and full audit trace.

## 3. Bounded Package V56 (strict)
1. V56-S1: long tradefulness unlock continuation.
`PLongGrid=0.16,0.15,0.14`; `MinExpectedMoveGrid=0.0020,0.0022,0.0024`; `MinCandidateTrades=3`.
2. V56-S2: short entry re-anchor continuation.
`PShortGrid=0.13,0.12,0.11`; `StopLossPct=0.0020` preserved.
3. V56-S3: short risk/move micro-correction.
`StopLossPct=0.0001`; V56-S2 entry profile preserved.
4. V56-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed 1d/1d window, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. one strict change per step.
4. after every step: pip check, text_guard, readiness --show, ACTIVE/CHANGELOG sync.

## 5. Acceptance unchanged
1. all_tradeful=true per mode.
2. mean OOS >= -2.5% per mode.
3. worst branch OOS >= -10% per mode.

## 6. DoD for V56 package task
1. V56 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
