# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V63_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V62 sequence completed with NO_GO at V62-S4.
2. Observed pattern after V62:
1. long mode remains non-viable (search_failed persistence),
2. short mode still fails acceptance and alternates between no-trade and unstable micro-correction behavior.

## 2. V63 objective
1. Continue long viability recovery with bounded entry shift.
2. Continue short stabilization with strict one-change protocol.
3. Preserve reversibility and full audit trace.

## 3. Bounded Package V63 (strict)
1. V63-S1: long tradefulness unlock continuation.
`PLongGrid=0.09,0.08,0.07`; `MinExpectedMoveGrid=0.0020,0.0022,0.0024`; `MinCandidateTrades=3`.
2. V63-S2: short entry re-anchor continuation.
`PShortGrid=0.06,0.05,0.04`; `StopLossPct=0.0020` preserved.
3. V63-S3: short risk/move micro-correction.
`StopLossPct=0.00000078125`; V63-S2 entry profile preserved.
4. V63-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed 1d/1d window, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. one strict change per step.
4. after every step: pip check, text_guard, readiness --show, ACTIVE/CHANGELOG sync.

## 5. Acceptance unchanged
1. all_tradeful=true per mode.
2. mean OOS >= -2.5% per mode.
3. worst branch OOS >= -10% per mode.

## 6. DoD for V63 package task
1. V63 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
