# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V65_2026-05-31_RU

Date: 2026-05-31  
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V64 exhausted with `NO_GO`.
2. Long side remains unstable by tradefulness/quality (no-trade branch in S1).
3. Short side alternates between deep-tail overtrade and weak mean profile.

## 2. V65 objective
1. Reduce short-tail amplitude while preserving tradefulness.
2. Keep long-side runtime active with tighter quality bias.
3. Preserve strict one-change protocol and full audit trace.

## 3. Bounded Package V65 (strict)
1. V65-S1: long quality bias continuation.
`PLongGrid=0.10,0.09,0.08`; `MinExpectedMoveGrid=0.0024,0.0026,0.0028`; `MinCandidateTrades=3`.
2. V65-S2: short entry de-overtrade continuation.
`PShortGrid=0.065,0.060,0.055`; `StopLossPct=0.0020` preserved.
3. V65-S3: short risk micro-correction.
`StopLossPct=0.0010`; V65-S2 entry profile preserved.
4. V65-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed 1d/1d window, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. one strict change per step.
4. after every step: pip check, text_guard, readiness --show, ACTIVE/CHANGELOG sync.

## 5. Acceptance unchanged
1. all_tradeful=true per mode.
2. mean OOS >= -2.5% per mode.
3. worst branch OOS >= -10% per mode.
