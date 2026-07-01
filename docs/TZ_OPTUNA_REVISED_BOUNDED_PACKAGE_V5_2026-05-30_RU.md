# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V5_2026-05-30_RU

Date: 2026-05-30
Scope: Optuna/APTuna only (ML runtime untouched)

## 1. Basis
1. V4 sequence executed under strict split and single-change protocol.
2. Key observations:
1. long mode produced partial reproducible positive result under tradeful guard (`+2.9363%`, 2/3 goal_pass),
2. short mode remained negative under all tested stabilizations,
3. technical worker fragility observed once (JSONDecodeError) but recovered by strict replay.
3. V4 final checkpoint: bounded package currently not viable for U1 acceptance.

## 2. V5 objective
1. Preserve the only positive long trajectory while constraining selector drift.
2. Push short profile from deep-negative toward controllable near-threshold tradeful behavior.
3. Keep all changes bounded and reversible.

## 3. Bounded Package V5 (strict)
1. V5-S1: long reproducibility lock
1. repeat long setup from V4-S1 under tradeful guard,
2. confirm 3-run reproducibility for long.
2. V5-S2: short anti-overtrade compression
1. tighten short entry + min_expected_move around best tradeful sub-branch,
2. keep tp-guard fixed.
3. V5-S3: cross-mode alignment check
1. execute short/long with locked bounded pair,
2. verify no-trade selector does not dominate when tradeful branch exists.
4. V5-S4: U1 micro-gate rehearsal
1. evaluate all_tradeful, mean OOS, worst-branch OOS on latest bounded pair,
2. decide GO-forward to next package or freeze checkpoint.

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

## 6. DoD for V5 package task
1. V5 package doc created and linked from priorities.
2. ACTIVE/CHANGELOG synchronized.
3. mandatory audit PASS.
