# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V64_2026-05-31_RU

Date: 2026-05-31  
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V63 sequence exhausted with `NO_GO` at S4.
2. V63-S2 reached tradeful execution but produced deep downside tail.
3. V63-S3 reduced tail but returned no-trade on 2/3 branches.
4. Long technical blocker (`search_failed` by cross-threshold pruning) is removed; long side is now quality problem, not runtime-crash problem.

## 2. V64 objective
1. Keep long-side runtime alive and improve quality floor.
2. Stabilize short-side tradefulness without deep tails.
3. Preserve strict auditability and single-change reversibility.

## 3. Bounded Package V64 (strict)
1. V64-S1: long quality re-anchor (post-unblock).
`PLongGrid=0.11,0.10,0.09`; `MinExpectedMoveGrid=0.0022,0.0024,0.0026`; `MinCandidateTrades=3`.
2. V64-S2: short entry tighten continuation.
`PShortGrid=0.055,0.050,0.045`; `StopLossPct=0.0020` preserved.
3. V64-S3: short risk micro-correction.
`StopLossPct=0.0005`; V64-S2 entry profile preserved.
4. V64-S4: cross-mode confirmation + micro-gate.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed 1d/1d window, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. one strict change per step.
4. after every step: pip check, text_guard, readiness --show, ACTIVE/CHANGELOG sync.

## 5. Acceptance unchanged
1. all_tradeful=true per mode.
2. mean OOS >= -2.5% per mode.
3. worst branch OOS >= -10% per mode.
