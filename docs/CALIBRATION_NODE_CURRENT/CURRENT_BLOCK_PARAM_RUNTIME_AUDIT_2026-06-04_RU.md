# Жесткий аудит current-блоков калибровки

Дата UTC: `2026-06-04T06:45:55Z`.

Машинный artifact: `reports/qa_gate/current_block_param_runtime_audit_20260604T064555Z.json`.

## Короткий итог

Статус: `PASS_SEARCH_RUNTIME_WITH_CRITICAL_ANCHOR_GAP`.

Что это значит по-русски:

1. Блоковые матрицы `configs/calibration_matrices/catalog_blocks/*.yaml` реально являются блоковой калибровкой. Они берут целый блок, его `feature_rows`, union параметров блока и always-on context `volume_flow + price_volatility`.
2. `narrow / medium / wide` реально компилируются в разные списки значений. `wide` идет по полному диапазону, `medium` прореживает, `narrow` компактнее, но сохраняет min/max anchors.
3. Внутри `optuna_search_candidate.py` параметры реально семплируются и передаются в `build_feature_frame(..., calibration_params=...)` и `run_prob_backtest(..., calibration_params=...)`.
4. Главный разрыв: после выбора кандидата `adaptive_auto_train.py` запускает финальный `pipeline_train_eval` и `oos_evaluate` без выбранных `calibration_params`. Значит Optuna-search видит калиброванные формулы, но финальная train/OOS-проверка может пересчитать фичи на дефолтах.
5. Есть параметры, которые записаны в YAML, но конкретная формула сейчас их не слушает. Такие места перечислены ниже.

Вывод: блоковый контур подключен и частично рабочий, но для честной боевой калибровки нужно сначала закрепить `calibration_params` после Optuna-search и закрыть формульные разрывы.

## Проверенный runtime-путь

1. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` принимает `-CalibrationMatrixPath`.
2. Runner пишет путь в `MLBOTNAV_CALIBRATION_MATRIX_PATH`.
3. `adaptive_auto_train.py` при `--search-engine optuna` запускает `mlbotnav.optuna_search_candidate`.
4. `optuna_search_candidate.py` читает YAML через `load_calibration_matrix()`.
5. `compile_optuna_space()` собирает блоки, context blocks, feature rows, hypothesis rows и profiles.
6. Optuna семплирует `profile__<param>`.
7. Эти параметры попадают в objective-search.
8. После выбора кандидата параметры пока не передаются в финальный train/OOS.

## Глобальные замечания

### 1. Блоком калибруется не `H001`, а `catalog_block`

`feature_sweep/H001-H068` - одиночная диагностика по строкам.

`catalog_blocks/catalog_block_01..06` - настоящая блоковая калибровка.

Если цель - калибровать блок целиком, боевой маршрут должен идти по `catalog_blocks`, а `H001/H002/H003` оставить как диагностический режим.

### 2. Search-сетки из YAML не являются главным runtime-источником

`search_grid_rows` в YAML описаны, но фактические runtime-сетки для:

1. `horizon_bars`;
2. `p_enter_long`;
3. `p_enter_short`;
4. `min_expected_move_pct`;
5. `notional_usd`;

приходят из CLI аргументов `adaptive_auto_train.py` и runner-команд.

Это нужно либо явно оставить как правило, либо доработать так, чтобы YAML был единым источником и для search-grid.

### 3. Параметры общие на trial

Если в блоке пять фич используют `return_lookback`, это один общий `return_lookback` на trial, а не отдельный параметр для каждой фичи.

Это нормально для блоковой калибровки, но важно понимать: блок калибруется связкой параметров, а не отдельной независимой осью на каждую строку.

## Блок 1: Цена и волатильность

Технический блок: `price_volatility`.

Статус: `SEARCH_OK_FINAL_ANCHOR_GAP`.

Калибруемые параметры:

1. `return_lookback`: min `3`, max `30`, step `3`.
2. `rolling_window`: min `20`, max `180`, step `20`.
3. `period_standard`: min `7`, max `35`, step `2`.

Что реально работает в Optuna-search:

1. `ret_1`, `ret_3`, `ret_6`, `ret_12`, `ret_24` используют `return_lookback`.
2. `rolling_std_20` использует `rolling_window`.
3. `atr14` использует `period_standard`.

Что фиксированное или частичное:

1. `hl_spread` фиксированный, не калибруется.
2. Названия `ret_1/3/6/12/24` остаются ярлыками: фактически окно считается как `return_lookback * множитель`.

Итог по блоку: в Optuna-search блок перебирается. Для полного боевого доверия нужно передавать выбранные `calibration_params` дальше в train/OOS.

## Блок 2: Тренд и импульс

Технический блок: `trend_momentum`.

Статус: `SEARCH_OK_FINAL_ANCHOR_GAP`.

Калибруемые параметры:

1. `period_standard`: min `7`, max `35`, step `2`.
2. `ema_slow_period`: min `20`, max `120`, step `10`.
3. `ema_ultra_period`: min `120`, max `300`, step `20`.
4. `macd_fast_period`: min `7`, max `21`, step `2`.
5. `macd_slow_period`: min `19`, max `43`, step `2`.
6. `macd_signal_period`: min `5`, max `17`, step `2`.
7. `stoch_d_period`: min `3`, max `15`, step `2`.
8. `return_lookback`: min `3`, max `30`, step `3`.

Что реально работает в Optuna-search:

1. EMA, RSI, ATR, ADX и Stoch берут свои периоды из `calibration_params`.
2. MACD берет `macd_fast_period`, `macd_slow_period`, `macd_signal_period`.
3. `ema_slope_5` использует `return_lookback`.
4. Гипотезы/trend filters калибруются и фильтруются strict block purity.

Что фиксированное или частичное:

1. Имена `ema20`, `ema50`, `ema200`, `rsi14`, `adx14`, `stoch_k14` исторические. После калибровки они не обязаны буквально означать 20/50/200/14.

Итог по блоку: в Optuna-search блок живой. Главный разрыв такой же: выбранные параметры не закрепляются в финальном train/OOS.

## Блок 3: Объем и поток

Технический блок: `volume_flow`.

Статус: `PARTIAL_FORMULA_GAPS_FINAL_ANCHOR_GAP`.

Калибруемые параметры:

1. `return_lookback`: min `3`, max `30`, step `3`.
2. `rolling_window`: min `20`, max `180`, step `20`.
3. `period_standard`: min `7`, max `35`, step `2`.

Что реально работает в Optuna-search:

1. `vol_z` использует `rolling_window`.
2. `mfi14` использует `period_standard`.
3. Блок включается как always-on context и как самостоятельный catalog block.

Что записано, но реально не слушается формулой:

1. `vol_chg` в YAML привязан к `return_lookback`, но в коде стоит `pct_change(1)`.
2. `delta_volume` в YAML привязан к `return_lookback`, но в коде стоит `diff(1)`.
3. `obv_slope_5` в YAML привязан к `return_lookback`, но в коде стоит `pct_change(5)`.

Что фиксированное:

1. `vwap_distance` фиксированный расчет.

Итог по блоку: объемный блок не пустой, но часть важных объемных фич не калибруется так, как написано в YAML. Перед боевым прогоном нужно решить: либо подвязать эти три формулы к `return_lookback`, либо явно пометить их как fixed.

## Блок 4: Профиль плотности

Технический блок: `density_profile`.

Статус: `MOSTLY_SEARCH_OK_ONE_FORMULA_GAP_FINAL_ANCHOR_GAP`.

Калибруемые параметры:

1. `density_window_short`: min `20`, max `120`, step `20`.
2. `density_window_long`: min `120`, max `360`, step `30`.
3. `density_bin_pct`: min `0.0003`, max `0.0012`, step `0.0001`.
4. `div_lookback`: min `3`, max `30`, step `3`.

Что реально работает в Optuna-search:

1. `density_*_60` используют `density_window_short`.
2. `density_*_240` используют `density_window_long`.
3. `density_cluster_ratio_60_240` зависит от short/long/bin.
4. `density_bin_pct` реально влияет на rolling volume-at-price proxy.

Что записано, но реально не слушается как указано:

1. `density_vpoc_drift_20` в YAML привязан к `div_lookback`.
2. В коде формула использует `return_lookback * 2`.

Итог по блоку: основной density-профиль калибруется. Нужно исправить или переименовать привязку `density_vpoc_drift_20`.

## Блок 5: Структура и ТА

Технический блок: `structure_ta`.

Статус: `PARTIAL_FORMULA_GAPS_FINAL_ANCHOR_GAP`.

Калибруемые параметры:

1. `rolling_window`: min `20`, max `180`, step `20`.
2. `threshold_fine`: min `0.0005`, max `0.01`, step `0.0005`.
3. `return_lookback`: min `3`, max `30`, step `3`.

Что реально работает в Optuna-search:

1. Support/resistance/range/breakout используют `rolling_window`.
2. `level_strength` использует `threshold_fine`.
3. Swing/BOS используют `return_lookback`.
4. `trend_channel_pos` и FIBO base используют channel window.

Что частично не соответствует YAML:

1. `retest_flag` заявляет `threshold_fine`, но в коде стоит жесткий порог `0.002`.
2. `false_breakout_flag` заявляет `threshold_fine`, но порог в формуле фактически не используется.
3. FIBO уровни `0.382` и `0.618` захардкожены.
4. Старый `fib_level` пока не возвращен в runtime как отдельный профиль.
5. `trend_channel_pos` и FIBO зависят от `channel_win = max(rolling_window, period_standard * 2)`, но строки YAML в основном показывают только `rolling_window`.

Итог по блоку: структура и ТА работают частично, но FIBO и retest/false-breakout требуют доработки перед честной боевой калибровкой всего блока.

## Блок 6: Паттерны

Технический блок: `pattern`.

Статус: `CANDLE_DIVERGENCE_SEARCH_OK_CLASSIC_FIGURES_MISSING_FINAL_ANCHOR_GAP`.

Калибруемые параметры:

1. `doji_threshold`: min `0.05`, max `0.20`, step `0.01`.
2. `ratio_pattern`: min `1.2`, max `3.4`, step `0.2`.
3. `ratio_opposite_wick_cap`: min `0.4`, max `1.2`, step `0.1`.
4. `div_lookback`: min `3`, max `30`, step `3`.
5. `pattern_age_cap`: min `5`, max `100`, step `5`.

Что реально работает в Optuna-search:

1. `doji_flag` использует `doji_threshold`.
2. Pin-bar, hammer, shooting star используют `ratio_pattern` и `ratio_opposite_wick_cap`.
3. RSI/MACD/OBV дивергенции используют `div_lookback`.
4. `pattern_age_bars` использует `pattern_age_cap`.

Что фиксированное:

1. `inside_bar_flag` фиксированный.
2. `engulf_bull_flag` и `engulf_bear_flag` фиксированные.
3. `pattern_strength` фиксированная агрегация.

Что отсутствует по новому ТЗ:

1. Двойная вершина.
2. Двойное дно.
3. Голова и плечи.
4. Перевернутая голова и плечи.
5. Треугольник.
6. Вымпел.
7. Восходящий/нисходящий клин.
8. Диапазон как фигура.
9. Связка `pattern_structure_volume_entry`: `pattern + structure_ta + volume_flow`.

Итог по блоку: текущий `pattern` - это свечные паттерны и дивергенции. Классические фигурные паттерны и связка с объемом/уровнями пока не реализованы.

## Что нужно сделать перед честной боевой калибровкой

1. Закрепить выбранные `calibration_params` после Optuna-search:
   - сохранить их в `adaptive_auto_train.py` step candidate;
   - передать в `pipeline_train_eval`;
   - записать в train report;
   - записать в model payload;
   - применить в `oos_evaluate`;
   - передать в финальный `run_prob_backtest`.
2. Исправить `volume_flow`:
   - `vol_chg` должен использовать `return_lookback` или быть fixed;
   - `delta_volume` должен использовать `return_lookback` или быть fixed;
   - `obv_slope_5` должен использовать `return_lookback` или быть fixed.
3. Исправить `density_profile`:
   - `density_vpoc_drift_20` должен использовать `div_lookback` или YAML должен быть исправлен на реальный `return_lookback`.
4. Исправить `structure_ta`:
   - `retest_flag` привязать к `threshold_fine`;
   - `false_breakout_flag` либо привязать к порогу, либо сделать fixed;
   - вернуть `fib_level` как профиль;
   - добавить нормальную FIBO-сетку по решению `FIBO_STRUCTURE_TA_DECISION_2026-06-03_RU.md`.
5. По `pattern`:
   - реализовать или явно отложить `pattern_structure_volume_entry`;
   - не считать classic figure contour рабочим, пока его нет в коде.
6. Решить по `search_grid_rows`:
   - либо сделать YAML единым источником search-сеток;
   - либо явно зафиксировать, что search-сетки идут из runner CLI.

## Практический вывод

Сейчас можно сказать так:

1. “Каркас блоковой калибровки подключен” - да.
2. “Сетки narrow/medium/wide реально применяются в Optuna-search” - да.
3. “Каждый блок целиком можно передать в APTuna через catalog block matrix” - да.
4. “Все записанные параметры реально влияют на формулы” - нет.
5. “Выбранная Optuna-калибровка полностью закрепляется в train/OOS” - нет.
6. “Можно честно идти в боевой полный прогон всех блоков без доработки” - нет, сначала закрыть anchor gap и формульные расхождения.

