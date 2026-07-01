# TZ_OPTUNA_U1_V2_EXECUTION_MANIFEST_2026-05-30_RU

Дата: 2026-05-30  
Контур: только Optuna/APTuna

## 1. Режим
1. `short_only` и `long_only` строго раздельно.
2. `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`.
3. `ml_signal_backend=off`, fixed `1d/1d`.

## 2. Очередность v2 (без смешивания family)
1. V2-F1 `execution risk`:
1. шаг A: `stop_loss_pct` micro-band,
2. шаг B: `take_profit_pct` micro-band.
2. V2-F2 `tp-reach guard`:
1. шаг C: `min_tp_reach_prob` micro-band,
2. шаг D: `tp_min_factor` micro-band.
3. V2-F3 `move threshold`:
1. шаг E: `min_expected_move` narrow band.

## 3. Гейты после каждого шага
1. `pip check` PASS.
2. `text_guard` PASS.
3. `readiness --show` safe lock (`project_ready=false` в docs/gov шагах).
4. U1 критерии:
1. `all_tradeful=true`,
2. `mean OOS >= -2.5%`,
3. `worst branch OOS >= -10%`.

## 4. Стоп-условие
1. Если любая family дает системный `no-trade` или deep-negative drift в обоих режимах:
1. family закрывается чекпоинтом,
2. запускается следующий bounded family только после фиксации checkpoint-отчета.
