# TZ: Environment Baseline for MLBotNav + APTuna

Date: 2026-05-28  
Status: ACTIVE

## 1. Goal
Keep one stable runtime environment and guarantee reproducible Optuna/grid launches.

## 2. Workspace Scope
1. Root: `C:\Users\007\Desktop\MLbotNav`
2. Runtime code: `src/mlbotnav/*`
3. Launchers: `run_*.ps1`, `APTuna/run_*.ps1`

## 3. Python Invariant (MUST)
1. Allowed interpreter: `.venv\Scripts\python.exe`
2. Required version: `Python 3.13.x`
3. Any run with another interpreter is forbidden.

## 4. Required Environment Variables (MUST)
1. `PYTHONPATH=src`
2. `POSTGRES_DSN=postgresql://postgres:<PASSWORD>@127.0.0.1:5432/mlbotnav`
3. `OPTUNA_STORAGE_URL=postgresql://postgres:<PASSWORD>@127.0.0.1:5432/mlbotnav`
4. Thread vars:
   1. `OMP_NUM_THREADS`
   2. `MKL_NUM_THREADS`
   3. `OPENBLAS_NUM_THREADS`
   4. `NUMEXPR_NUM_THREADS`

## 5. Bootstrap Rule (MUST)
Before any runtime command:
1. `.\set_mlbotnav_env.ps1 -Threads 9`

Script responsibilities:
1. Load `.env` into process env.
2. Set `PYTHONPATH=src`.
3. Set thread vars.
4. Run Python guard (`scripts/assert_python313_env.ps1`).

## 6. Pre-Run Database Check (MUST for Optuna)
1. Service check:
```powershell
Get-Service postgresql-x64-17
```
2. Port check:
```powershell
Test-NetConnection 127.0.0.1 -Port 5432
```
3. Auth check:
```powershell
.\set_mlbotnav_env.ps1 -Threads 9
.\.venv\Scripts\python.exe -c "import os, sqlalchemy as sa; sa.create_engine(os.environ['OPTUNA_STORAGE_URL']).connect().close(); print('pg ok')"
```

## 7. One-Minute Smoke Policy
1. If Postgres auth check passes -> run Optuna 60s smoke (`Threads=9`, `SearchWorkers=9`).
2. If Postgres auth check fails -> run grid 60s smoke to validate worker load, and mark Optuna as BLOCKED by DB auth.

## 8. PASS Criteria
1. Python guard PASS.
2. `text_guard` PASS.
3. Runtime lock released (`runtime_owner=null`).
4. For Optuna: no `search_failed` caused by DB connection/auth.

## 9. Current Known Blocker
If `fe_sendauth: no password supplied` appears, DSN must be updated with a valid password.

