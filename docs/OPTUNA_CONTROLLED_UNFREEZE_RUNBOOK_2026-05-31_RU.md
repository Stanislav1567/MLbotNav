# Controlled unfreeze runbook (Optuna contour, 2026-05-31)

## 1) Preconditions
1. Scope: tolko `MLbotNav` Optuna/APTuna contour.
2. ML backend: `off`.
3. Last audits must be PASS:
1. strict profile min/max (long + short),
2. search-grid quintet min/max (long + short),
3. text_guard PASS.

## 2) Unfreeze execution model
1. Persistent readiness flags ne menyat.
2. Ispolzovat tolko temporary unlock v launcher (`-UseTemporaryUnlock`).
3. Posle kazhdogo run freeze dolzhen byt avtomaticheski vosstanovlen.

## 3) Canonical commands
1. Long-only validation:
```powershell
powershell -ExecutionPolicy Bypass -File APTuna\run_optuna_1d1d_stagec_process_pool.ps1 `
  -Mode long_only -TrainDate 2026-05-19 -TestDate 2026-05-20 `
  -Threads 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 `
  -OptunaTrials 220 -OptunaTimeoutSec 2100 `
  -UseTemporaryUnlock -OptunaMlSignalBackend off `
  -HorizonsGrid "1,20" -PLongGrid "0.52,0.80" -PShortGrid "0.20,0.48" `
  -MinExpectedMoveGrid "0.0005,0.01" -NotionalUsdGrid "5,100"
```
2. Short-only validation:
```powershell
powershell -ExecutionPolicy Bypass -File APTuna\run_optuna_1d1d_stagec_process_pool.ps1 `
  -Mode short_only -TrainDate 2026-05-19 -TestDate 2026-05-20 `
  -Threads 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 `
  -OptunaTrials 220 -OptunaTimeoutSec 2100 `
  -UseTemporaryUnlock -OptunaMlSignalBackend off `
  -HorizonsGrid "1,20" -PLongGrid "0.52,0.80" -PShortGrid "0.20,0.48" `
  -MinExpectedMoveGrid "0.0005,0.01" -NotionalUsdGrid "5,100"
```

## 4) Mandatory preflight before each window
1. Set runtime env:
```powershell
$env:PYTHONPATH = "src"
$env:OptunaMlSignalBackend = "off"
```
2. Verify freeze baseline before run:
```powershell
python -m mlbotnav.readiness --show
```
3. Preflight PASS only if:
1. `project_ready=false`,
2. `enforce_freeze=true`,
3. launcher still uses `-UseTemporaryUnlock`.

## 5) Mandatory post-run audits
1. Profile coverage:
```powershell
python -m mlbotnav.optuna_profile_coverage_audit --mode long_only --strict-linked-coverage --min-linked-coverage-ratio 1.0 --require-min-max-hits --min-linked-minmax-ratio 1.0
python -m mlbotnav.optuna_profile_coverage_audit --mode short_only --strict-linked-coverage --min-linked-coverage-ratio 1.0 --require-min-max-hits --min-linked-minmax-ratio 1.0
```
2. Search-grid quintet coverage:
```powershell
python -m mlbotnav.optuna_search_grid_coverage_audit --mode long_only
python -m mlbotnav.optuna_search_grid_coverage_audit --mode short_only
```
3. Hygiene checks:
```powershell
pip check
python -m mlbotnav.text_guard
python -m mlbotnav.readiness --show
```

## 6) Status model
1. Allowed window statuses:
1. `PASS` - all checks PASS, fix not required,
2. `PASS_AFTER_FIX` - initial failure fixed inside same window, then full re-audit PASS,
3. `FAIL` - unresolved issue after fix loop.
2. `fix.result` values:
1. `PASS`,
2. `FAIL`,
3. `N/A` (if `fix.action=not_required`).

## 7) PASS / PAUSE+FIX LOOP / STOP_ON_SUCCESS
1. PASS only if:
1. all four coverage audits PASS,
2. launcher status `OK` for both modes,
3. readiness after runs remains `project_ready=false` and `enforce_freeze=true`.
2. If check FAIL:
1. pause window,
2. apply targeted fix in same scope,
3. rerun failed scope,
4. run full post-run audits again.
3. Mark as `FAIL` only if issue remains unresolved after fix loop.
4. STOP_ON_SUCCESS criterion:
1. `K=5` consecutive windows with status `PASS` (no fix),
2. freeze unchanged in all `K` windows (`project_ready=false`, `enforce_freeze=true`),
3. post-window decision for each window is `GO_FOR_NEXT_CONTROLLED_WINDOW`.
5. After STOP_ON_SUCCESS reached:
1. stop new `RUN_WINDOW_N`,
2. move to final governance closeout package.

## 8) Immediate hard-stop cases
1. Stop current window immediately if:
1. any coverage audit FAIL,
2. any unexpected worker/search technical error,
3. readiness state drift detected.
2. Continue series only after fix + full re-audit PASS.

## 9) Log order contract
1. For each window keep strict append order:
1. `RUN_WINDOW_N`,
2. `POST_WINDOW_N_DECISION`.
2. Publishing post-window before run-window is not allowed.

## 10) Registry discipline
1. Every run/audit/fix must be appended to:
1. `docs/ACTIVE_WORK_ITEMS_RU.md`
2. `docs/CHANGELOG_CHRONOLOGY_RU.md`
2. Preferred tool: `python -m mlbotnav.docs_registry_append`.
