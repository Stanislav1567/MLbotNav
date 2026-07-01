# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V4_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V3 sequence completed end-to-end (S1..S4).
2. All V3 steps remained gate-fail under U1 thresholds.
3. Two useful signals discovered:
1. short tradeful branch reached near-threshold (`-3.8282%`, trades=4) in V3-S3,
2. long tradeful branch reached near-threshold (`-6.7611%`, trades=2) in V3-S4, but selector still chose no-trade branch.

## 2. Core V4 objective
1. Eliminate selector preference for no-trade outcomes when tradeful alternatives exist.
2. Preserve strict bounded and split-mode discipline.
3. Validate stability around near-threshold tradeful branches.

## 3. Bounded Package V4 (strict)
1. V4-S1: tradeful-first selector guard (bounded runtime policy step)
1. enforce tradeful-first candidate selection in bounded contour,
2. keep feature/hypothesis space unchanged.
2. V4-S2: short near-threshold stabilization
1. short min_expected_move narrow band around V3-S3 tradeful branch,
2. keep tp-guard fixed.
3. V4-S3: long near-threshold stabilization
1. long tp-guard micro-pair around V3-S4 tradeful branch,
2. keep entry and cooldown fixed.
4. V4-S4: reproducibility micro-cycle
1. 3 repeats per mode on selected best bounded setup,
2. no broad space expansion.

## 4. Hard constraints
1. short_only and long_only strictly separated.
2. fixed window 1d/1d, ProcessWorkers=3, SearchWorkersPerProcess=3, Threads=9.
3. single-change protocol for each V4 step.
4. Mandatory checks after every step:
1. pip check,
2. text_guard,
3. readiness --show,
4. ACTIVE + CHANGELOG sync.

## 5. Acceptance stays unchanged
1. all_tradeful=true per mode,
2. mean OOS >= -2.5% per mode,
3. worst branch OOS >= -10% per mode.
4. if fail: checkpoint and freeze remain active.

## 6. DoD for V4 package task
1. V4 package document created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. Mandatory audit PASS.
