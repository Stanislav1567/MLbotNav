# Hard audit Optuna contour (A -> I), 2026-05-31

## 1) Locked scope (no deviation)
- Working contour only: `C:\Users\007\Desktop\MLbotNav`, modules `APTuna`, `src/mlbotnav`, `configs`.
- ML contour is not used for Optuna calibration: `OptunaMlSignalBackend=off` in task, launcher, runtime.
- Current stage goal: finish contour engineering quality (coverage/correctness/auditability), not strategy alpha proof on short `1d/1d 1m`.

## 2) Calibration inventory (confirmed)
- Features: `68` total, `56` calibratable, `12` non-calibratable.
- Hypotheses: `20` total, `20` calibratable.
- Search-grid parameters: `5`.
- Parameter profiles: `27`.
- Source: `reports/qa_gate/p1370_independent_audit2_calibration_coverage_20260531T043322Z.json`.

## 3) Pipeline A -> I status
1. `A` (VS Code task): `READY`.
2. `B` (APTuna launcher): `READY`.
3. `C` (adaptive orchestration): `READY`.
4. `D` (Optuna search runtime): `PARTIAL`.
5. `E` (backtest/gate): `READY`.
6. `I` (artifacts/registries): `PARTIAL`.

## 4) Done today
1. Two independent experts connected and both independent audits completed (pipeline + coverage).
2. Runtime activation of all 6 blocks confirmed on latest long/short runs.
3. Sampling of `param_profile__*` linked profiles confirmed; no broken `min/max` ranges found.
4. Fresh text/mojibake audit executed: `PASS`, `suspect_files=0` (`reports/qa_gate/recovery_r5_text_guard_20260531T043615Z.json`).
5. Fresh readiness check executed: freeze preserved (`project_ready=false`, `enforce_freeze=true`) (`reports/readiness/readiness_check_20260531T043614Z.json`).
6. Fresh dependencies health check executed: `pip check` -> `No broken requirements found`.

## 5) Critical open gaps before contour go-live
1. True trial-level `3x9` throughput is blocked by sqlite guard: `effective_n_jobs=1` per process.
2. Mandatory full `min -> max` sweep for base 5 search-grid params is not yet evidenced in latest strict chain.
3. No explicit runtime taxonomy for `wide/medium/narrow` named presets across all calibratable params.
4. No single mandatory PASS/FAIL report proving `min_hit/max_hit` for each calibratable parameter.
5. short-only gate override mismatch exists between `configs/optuna_engine.yaml` and `configs/thresholds.yaml`; needs single source of truth.

## 6) Priority order (strictly for contour completion)
1. `P0`: migrate Optuna storage `sqlite -> postgres` to unlock real internal parallelism.
2. `P0`: introduce named presets `wide/medium/narrow` for all calibratable modules/features/hypotheses.
3. `P0`: run mandatory coverage-cycle with per-parameter `min_hit/max_hit` evidence.
4. `P1`: add unified PASS/FAIL gate report for base search-grid quintet.
5. `P1`: unify short-only gate overrides in one config source + consistency test.
6. `P1`: automate chronology/registry logging to reduce manual ops risk.

## 7) ETA to contour go-live (engineering-ready, not alpha-ready)
- P0 minimum to technical go-live: `~12-18` engineering hours.
- P0 + P1 hardening envelope: `~20-28` engineering hours.

## 8) VS Code vs PowerShell clarification
- VS Code priority is preserved: starts from `.vscode/tasks.json`.
- PowerShell is used only as task launcher wrapper in the same contour.
- Configured `3x9` exists in task settings, but internal `n_jobs` stays restricted until storage migration from sqlite.
