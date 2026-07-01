# Optuna contour closeout (2026-05-31)

## 1) Scope i granitsy
1. Kontur rabot: tolko `MLbotNav` (`APTuna`, `src/mlbotnav`, `configs`, `docs`, `reports`).
2. ML-kontur ne ispolzovan v Optuna-kalibrovke (`OptunaMlSignalBackend=off`).
3. Rezhim etapa: `1d train / 1d test`, `1m`, razdelno `long_only` i `short_only`.

## 2) Itog po kriteriyam TZ
1. `P0-1` storage: zakryto.
1. Postgres required + no silent sqlite fallback.
2. `P0-2` grid presets: zakryto.
1. V runtime vnedreny `wide/medium/narrow`.
3. `P0-3` min/max profile coverage: zakryto.
1. Strict linked `min_hit/max_hit` PASS v long i short.
4. `P1` search-grid quintet report: zakryto.
1. PASS po `horizon/p_long/p_short/min_move/notional` v long i short.
5. `P1` gate override source unification: zakryto.
1. Edinyi istochnik: `thresholds.yaml`.
6. `P1` registry/changelog automation: zakryto.
1. Vvedena utilita `mlbotnav.docs_registry_append`.

## 3) A->I control snapshot
1. A (VS Code task): READY.
2. B (APTuna launcher): READY.
3. C (adaptive orchestration): READY.
4. D (optuna search runtime): READY for contour-completion stage.
5. E (backtest/gate): READY.
6. I (artifacts/registry discipline): READY with automated append utility.

## 4) Final audit artifacts (key)
1. Profile min/max PASS:
1. `reports/qa_gate/optuna_profile_coverage_long_only_20260531T054958Z.json`
2. `reports/qa_gate/optuna_profile_coverage_short_only_20260531T054958Z.json`
2. Search-grid min/max PASS:
1. `reports/qa_gate/optuna_search_grid_coverage_long_only_20260531T054958Z.json`
2. `reports/qa_gate/optuna_search_grid_coverage_short_only_20260531T054958Z.json`
3. Readiness checkpoint:
1. `reports/qa_gate/p1385_contour_go_live_readiness_20260531T054608Z.json`
2. status: `READY_FOR_CONTROLLED_UNFREEZE`.

## 5) Tech risks and fixes applied
1. Fixed dynamic categorical edge-forcing bug (Optuna distribution compatibility).
2. Fixed notional grid passthrough gap (now full quintet min/max reachable).
3. Fixed readiness backup filename collision risk in concurrent launcher starts (mode + GUID suffix).

## 6) Governance state
1. `readiness` remains frozen by policy:
1. `project_ready=false`
2. `enforce_freeze=true`
2. This is expected governance lock, not technical readiness failure.

## 7) Decision
1. Tech contour objective for TZ 2026-05-31: **COMPLETED**.
2. Operational state: **READY_FOR_CONTROLLED_UNFREEZE**.
3. Next action by procedure: explicit controlled unfreeze decision and launch window approval.
