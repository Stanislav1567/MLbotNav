# P31 Stage C Protocol (Long/Short Раздельно)

Дата: 2026-05-26  
Контур: Optuna / post-A,B кандидаты  
Режим: без смешивания `long_only` и `short_only`

## 1. Цель
1. Проверить top-кандидаты из stage A/B на длинном OOS-окне.
2. Фиксировать long и short в разных контурах.
3. Подготовить единый шаблон для C30 и C60.

## 2. Базовые кандидаты
1. `long_only` (из P28):
   1. `horizon_bars=3`
   2. `p_enter_long=0.54`
   3. `p_enter_short=0.46`
   4. `min_expected_move_pct=0.002`
   5. `trend_filter=min_max_range_revert`
   6. `min_abs_ema_gap=0.0`
2. `short_only` (из P30):
   1. `horizon_bars=3`
   2. `p_enter_long=0.52`
   3. `p_enter_short=0.48`
   4. `min_expected_move_pct=0.001`
   5. `trend_filter=swing_lh_ll_short`
   6. `min_abs_ema_gap=0.0`

## 3. Окна Stage C
1. C30:
   1. train: `2026-03-27 .. 2026-04-25`
   2. test: `2026-04-26 .. 2026-05-25`
2. C60:
   1. train: `2026-01-26 .. 2026-03-26`
   2. test: `2026-03-27 .. 2026-05-25`

## 4. Запуск (шаблон)
1. Long C30:
```powershell
python -m mlbotnav.adaptive_auto_train `
  --symbol SOLUSDT --timeframe 1m `
  --train-start 2026-03-27 --train-end 2026-04-25 `
  --test-day 2026-04-26 --test-end-day 2026-05-25 `
  --window-policy multiday `
  --signal-mode long_only --contour-id long_only_c30 `
  --search-engine grid `
  --horizons-grid 3 --p-long-grid 0.54 --p-short-grid 0.46 `
  --min-expected-move-grid 0.002 `
  --trend-filter min_max_range_revert --min-abs-ema-gap 0.0 `
  --execution-mode exchange_like --order-type market `
  --notional-usd 10 --leverage 10 `
  --repeats 1 --max-threads 8 --search-workers 8 `
  --min-train-rows 900 --n-folds 3 `
  --allow-subgoal-candidates `
  --disable-hypothesis-profile --disable-backlog-active-append `
  --temporary-unlock-readiness
```
2. Short C30:
```powershell
python -m mlbotnav.adaptive_auto_train `
  --symbol SOLUSDT --timeframe 1m `
  --train-start 2026-03-27 --train-end 2026-04-25 `
  --test-day 2026-04-26 --test-end-day 2026-05-25 `
  --window-policy multiday `
  --signal-mode short_only --contour-id short_only_c30 `
  --search-engine grid `
  --horizons-grid 3 --p-long-grid 0.52 --p-short-grid 0.48 `
  --min-expected-move-grid 0.001 `
  --trend-filter swing_lh_ll_short --min-abs-ema-gap 0.0 `
  --execution-mode exchange_like --order-type market `
  --notional-usd 10 --leverage 10 `
  --repeats 1 --max-threads 8 --search-workers 8 `
  --min-train-rows 900 --n-folds 3 `
  --allow-subgoal-candidates `
  --disable-hypothesis-profile --disable-backlog-active-append `
  --temporary-unlock-readiness
```
3. C60 запускается по тем же шаблонам, меняются только даты train/test.

## 5. Обязательная фиксация
1. После каждого запуска писать артефакты в:
   1. `docs/ACTIVE_WORK_ITEMS_RU.md`
   2. `docs/CHANGELOG_CHRONOLOGY_RU.md`
2. В запись включать:
   1. `status`
   2. `oos_net_return_pct`
   3. `trades`
   4. `pass_candidates/goal_candidates`
   5. `candidate_pool`
