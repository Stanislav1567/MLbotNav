# MLbotNav: Master-Checklist "5+" по ТЗ

Дата фиксации: 2026-05-21  
Источник истины: `TECH_SPEC_ML_PLATFORM_RU.md`

## Блок F (Фундамент до обучения/тестов)

1. `F1` Единый статус ТЗ и единый чеклист (этот файл)  
Статус: `DONE`

2. `F2` Версионированный Data Contract для OHLCV  
Статус: `DONE (v1)`  
Артефакты: `src/mlbotnav/data_contract.py`, `contract_version=ohlcv_v1`.

3. `F3` Quarantine + блокировка прохода в `core` при `DQ FAIL/contract FAIL`  
Статус: `DONE (ingest_day + ingest_incremental)`  
Артефакты: `data/raw`, `data/core`, `data/quarantine`.

4. `F4` Retry/backoff/jitter + `partial_success` по `symbol+timeframe`  
Статус: `DONE (v1)`  
Артефакты: `src/mlbotnav/ingest_policy.py`, `data/meta/ingest_pair_status.csv`.

5. `F5` Базовая storage-схема `raw/core/analytics/dq/meta` в локальном контуре  
Статус: `DONE (v1)`  
Артефакты: `src/mlbotnav/storage_registry.py`, `data/analytics/*.csv`, `data/meta/storage_partitions.csv|.parquet(optional)`.

## Блок M (ML-ядро)

6. `M1` Полный набор Structure/Pattern фич по ТЗ  
Статус: `IN PROGRESS`

7. `M2` Stage-engine `D1 -> D2 -> D3 -> D5 -> D30 -> D60 -> D90`  
Статус: `DONE (runtime v2)`

8. `M3` Negative Memory (fingerprint + cooldown + fail reasons)  
Статус: `DONE (runtime v2)`

9. `M4` Торговые инварианты (`TP>=1%`, `trades/day bounds`, строгий `NO_TRADE`)  
Статус: `IN PROGRESS`

10. `M5` Линейка моделей до уровня ТЗ (`LightGBM/XGBoost` + ablation)  
Статус: `DONE (v1)`

## Блок P (Prod/Monitoring/Governance)

11. `P1` Inference + paper trading контур  
Статус: `TODO`

12. `P2` Monitoring SLA (latency/error/perf) + алерты  
Статус: `IN PROGRESS`

13. `P3` Ранцы полного формата (`index.parquet`, xlsx/parquet exports, retention policies)  
Статус: `IN PROGRESS`

14. `P4` Security hardening (`RBAC`, `KMS/vault`, artifact signing, immutable audit`)  
Статус: `TODO`

## Правило исполнения

Блок `F` закрыт на уровне `v1` (инженерный фундамент).  
Текущий рабочий этап: переход в `M1` (расширение Structure/Pattern и торговых инвариантов по ТЗ).

## Progress Update (2026-05-21)
- Foundation block F1..F5 implemented at v1.
- M1/M4 implementation started: expanded Structure/Pattern features, removed future-leakage pattern flag logic, and enabled trades/day gate controls.

## Progress Update (TA, 2026-05-21)
- M1 (Structure/Pattern) upgraded with deterministic TA pipeline to `analytics.levels`, `analytics.pattern_events`, `analytics.signal_events`.
- M4 invariants enforced in TA signals: `TP>=1%`, `min_expected_move_pct`, explicit `NO_TRADE` reasons.
- Prod cycle now includes `technical_analysis` step (`prod.cycle.run_technical_analysis=true`).

## Progress Update (TA wave-2, 2026-05-21)
- Added H&S/inverse H&S/pennant detectors.
- Added ADX/MFI/Stochastic into signal decision context.
- Added fallback event log and parquet/xlsx TA exports.
- 30-day 1m TA rebuild completed with strict invariant gates and deduped fallback table.

## Progress Update (Stage/Backtest/Packs, 2026-05-21)
- `prod_cycle` now runs `stage_engine` automatically after pipeline step (`prod.cycle.run_stage_engine=true`).
- Added runtime stage state file: `data/meta/stage_runtime_state.json` with auto-advance on stage pass.
- Stage criteria expanded toward spec section 19.7: stability/no-trade/day-PnL checks and drawdown regression checks.
- Backtest trade logs now include `expected_move_pct`, `tp_reach_prob`, `sl_hit_prob`, `ev`.
- Packs index now exported to both `packs/index.csv` and `packs/index.parquet`.
- Promotion now checks candidate vs champion guardrails (return delta / drawdown regression / sharpe delta) before promote.

## Progress Update (P2 block-1 done, 2026-05-21)
- Rollback guard upgraded from recommendation-only to executable rollback action via champion history restore.
- Champion lifecycle now writes:
  - `models/registry/champion_history.jsonl`
  - `models/registry/active_model.json`
- Added SLA monitor (`latency/error/perf`) with artifacts:
  - `reports/monitoring/sla_report_*.json`
  - `reports/monitoring/sla_alert_*.json` when breached.
- `prod_cycle` now records per-step execution duration (`duration_ms`) and runs SLA monitoring automatically (`prod.cycle.run_sla_monitor=true`).

## Progress Update (M5 block done v1, 2026-05-21)
- `pipeline_train_eval` upgraded with model-family selection: `logreg`, `lightgbm`, `xgboost`, `auto`.
- Auto model-selection compares candidates on walk-forward + backtest and selects best score.
- Added ablation by feature groups (`price_volatility`, `trend_momentum`, `volume_flow`, `structure_ta`, `pattern`).
- Added ablation artifact export: `reports/pipeline/ablation_*.csv`.

## Progress Update (M2/M3 block done v2, 2026-05-21)
- Added full stage-ladder runtime `D1 -> ... -> D90` runner: `src/mlbotnav/stage_ladder.py`.
- D1 exhaustive search integrated before stage decision with coverage artifact (`total_candidates/pass_candidates`).
- Stage runtime state now stores active stage params and transition history with deterministic replay context.
- `prod_cycle` now passes real stage params/context to `stage_engine` (fixed empty-params fingerprint issue).
- Negative memory enriched with `reason_tags`, `param_signature`, `cooldown_remaining_hours`, and summary API.
