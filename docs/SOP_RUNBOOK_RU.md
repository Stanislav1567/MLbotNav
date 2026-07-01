# SOP / Runbook (минимальный)

## Ежедневный цикл
1. `python -m mlbotnav.ingest_incremental --symbol SOLUSDT --timeframes 1,5,15,30,60,240,D --lookback-days 3`
2. `python -m mlbotnav.pipeline_train_eval ... --promote-if-pass`
3. `python -m mlbotnav.monitor_drift ...`
4. `python -m mlbotnav.rollback_guard --pipeline-report <latest_report>`
5. `python -m mlbotnav.build_pack --date YYYY-MM-DD --symbol SOLUSDT --timeframe 1m`

## Аварийный rollback (по guard)
1. Проверить `reports/registry/rollback_guard_*.json`.
2. Если `rollback_required=true`, промоут новой модели запрещен.
3. Активной остается текущая champion (если есть), цикл фиксируется в audit-log.

## Аудит
- Все ключевые действия пишутся в `logs/audit.log`.

## CPU policy (strict)
1. Maximum allowed host CPU for heavy runs: `85%`.
2. If current CPU is above limit, the pipeline must wait and retry.
3. Do not stop or kill any external/foreign processes.
4. Apply only local throttling (thread limits) and continue by schedule after CPU recovers.

## Adaptive Loop Policy (strict goal + readiness)
1. Default mode is strict: train only candidates with `net_return_pct >= goal_net_return_pct`.
2. If no goal candidate is found, iteration status must be `no_goal_candidate`, without train/OOS.
3. Auto loop must not bypass freeze/readiness automatically.
4. Temporary readiness unlock is allowed only by explicit operator flag and must restore original readiness state after run.
5. Negative memory must be segmented by run key: `symbol/timeframe/train-window/test-day/goal`.
