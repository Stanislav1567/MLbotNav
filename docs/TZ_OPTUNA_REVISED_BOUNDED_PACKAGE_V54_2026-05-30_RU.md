# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V54_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V53 sequence completed with NO_GO at V53-S4.
2. Observed pattern after V53:
1. long mode remains non-viable (search_failed persistence),
2. short mode remains below acceptance and unstable under deep stop-loss tightening.

## 2. V54 objective
1. Continue long viability recovery with bounded entry shift.
2. Continue short stabilization with strict one-change protocol.
3. Preserve reversibility and full audit trace.

## 3. Bounded Package V54 (strict)
1. V54-S1: long tradefulness unlock continuation.
`PLongGrid=0.18,0.17,0.16`; `MinExpectedMoveGrid=0.0020,0.0022,0.0024`; `MinCandidateTrades=3`.
2. V54-S2: short entry re-anchor continuation.
`PShortGrid=0.15,0.14,0.13`; `StopLossPct=0.0020` preserved.
3. V54-S3: short risk/move micro-correction.
`StopLossPct=0.0004`; V54-S2 entry profile preserved.
4. V54-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed 1d/1d window, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. one strict change per step.
4. after every step: pip check, text_guard, readiness --show, ACTIVE/CHANGELOG sync.

## 5. Acceptance unchanged
1. all_tradeful=true per mode.
2. mean OOS >= -2.5% per mode.
3. worst branch OOS >= -10% per mode.

## 6. DoD for V54 package task
1. V54 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
