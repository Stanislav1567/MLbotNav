# Аудит производительности автокалибровки (MLbotNav)

Дата: 2026-05-25  
Проект: `C:\Users\007\Desktop\MLbotNav`

## 1) Что именно аудировано

- Контуры:
  - `run_hypotheses_full_coverage_1d1d.ps1`
  - `run_p23_operator_unified.ps1`
  - `src/mlbotnav/daily_long_short_cycle.py`
  - `src/mlbotnav/adaptive_auto_train.py`
- Связанные тяжёлые модули:
  - `src/mlbotnav/search_gate_candidate.py`
  - `src/mlbotnav/pipeline_train_eval.py`
  - `src/mlbotnav/oos_evaluate.py`
  - `src/mlbotnav/backtest.py`
  - `src/mlbotnav/table_canon_pack.py`
  - `src/mlbotnav/cpu_budget.py`

## 2) Фактические замеры (по логам/артефактам)

1. По `adaptive_progress` (30 repeats): среднее время одного repeat ~`65.33s` (p50 `65s`, max `67s`).  
   Источник: `reports/adaptive/long_only/adaptive_progress_SOLUSDT_1m_2026-05-19_20260525T140409Z.log`.

2. По `p23_operator_unified` (последние 40 логов):
   - step `01` (daily cycle): avg `134.81s`, max `216.68s`
   - step `02` (table_canon_pack): avg `5.58s`
   - step `03S/03L` (table_convergence): avg `3.36s / 2.84s`
   - step `04` (audit_table_chain): avg `2.08s`
   - step `05` (feature/orderbook/tz/freeze): avg `10.36s`

## 3) Топ-10 самых дорогих участков

1. `adaptive_auto_train`: цикл repeats, 3 тяжёлых subprocess на каждый repeat (`search` + `train` + `oos`)  
   Файл: `src/mlbotnav/adaptive_auto_train.py:924-1293`

2. `adaptive_auto_train`: 3 вызова `_next_threads()` на repeat (search/train/oos), каждый берёт окно CPU  
   Файл: `src/mlbotnav/adaptive_auto_train.py:948-960`, `1090-1102`, `1193-1205`

3. `cpu_budget.sample_cpu_window`: активный опрос CPU по окну (по умолчанию 10 сек)  
   Файл: `src/mlbotnav/cpu_budget.py:60-87`

4. `adaptive_auto_train._run` -> `wait_for_cpu_budget` перед каждым subprocess  
   Файл: `src/mlbotnav/adaptive_auto_train.py:237-243`, `src/mlbotnav/cpu_budget.py:181-207`

5. `search_gate_candidate`: полный перебор сетки параметров внутри горизонта (nested loops)  
   Файл: `src/mlbotnav/search_gate_candidate.py:135-141`, `163-185`

6. `backtest.run_prob_backtest`: основной симулятор в Python-циклах `while + for` на каждый кандидат  
   Файл: `src/mlbotnav/backtest.py:667-806`

7. `search_gate_candidate`: при multiprocess копируется `raw_rows`, внутри воркера заново `DataFrame` и `build_feature_frame`  
   Файл: `src/mlbotnav/search_gate_candidate.py:90-101`, `267-305`

8. `pipeline_train_eval` и `oos_evaluate`: в каждом repeat заново грузят свечи и строят фичи  
   Файлы:
   - `src/mlbotnav/pipeline_train_eval.py:338-346`
   - `src/mlbotnav/oos_evaluate.py:51-59`

9. `table_canon_pack`: очень много файловых экспортов (CSV+CSV_std+CSV_excel+Parquet+несколько XLSX)  
   Файл: `src/mlbotnav/table_canon_pack.py:540-669`

10. `daily_long_short_cycle`: одинаковая подготовка `table_canon_pack` повторяется в цикле по mode  
   Файл: `src/mlbotnav/daily_long_short_cycle.py:245-254`, `249-251`

## 4) Где дублируется работа

1. Дублирование `table_convergence`:
   - уже вызывается в `daily_long_short_cycle` (`src/mlbotnav/daily_long_short_cycle.py:315-333`)
   - потом снова вызывается в `run_p23_operator_unified` (`run_p23_operator_unified.ps1:244-250`)

2. Дублирование подготовки таблиц:
   - `table_canon_pack` на каждый mode в daily-цикле (`src/mlbotnav/daily_long_short_cycle.py:245-254`)
   - и отдельно в `run_p23_operator_unified` step `02` (`run_p23_operator_unified.ps1:129-166`, `254`)

3. В `run_hypotheses_full_coverage_1d1d.ps1` шаг `table_canon_pack` вызывается на каждую гипотезу  
   Файл: `run_hypotheses_full_coverage_1d1d.ps1:207`, `263-274`  
   При этом при `SKIP_NO_OOS` часть работы уже потрачена впустую.

4. Пересборка фичей минимум в 3 местах на repeat:
   `search_gate_candidate` + `pipeline_train_eval` + `oos_evaluate`.

## 5) Почему “долго” (корень проблемы)

Главный оверхед — не только ML, а orchestration:

- На 1 repeat в adaptive есть минимум:
  - ~3 CPU-window измерения (`_next_threads`)  
  - + 3 pre-run budget wait (`wait_for_cpu_budget`)
- При текущих дефолтах это даёт большой фиксированный тайм даже до основного расчёта.

Отсюда эффект: длительные серии repeats крутятся часами, даже когда “полезный” расчёт сравнительно небольшой.

## 6) Что можно ускорить без изменения бизнес-логики

### P0 (сразу, минимальный риск)

1. В калибровочном контуре уменьшить CPU-window:
   - `--cpu-control-window-sec` 10.0 -> 2.0
   - `--cpu-sample-interval-sec` 1.0 -> 0.5
   (те же правила, только быстрее реакция)

2. Для калибровочного режима разрешить один “ok-check” в budget wait (параметризовать `consecutive_ok`), вместо жёсткого 2.  
   Кодовая точка: `src/mlbotnav/cpu_budget.py:186-201`.

3. В `daily_long_short_cycle` делать `table_canon_pack` 1 раз до цикла mode (если train/test окно одинаковое для long/short).  
   Кодовая точка: `src/mlbotnav/daily_long_short_cycle.py:245-254`.

### P1 (средний риск, большой выигрыш)

4. В `run_hypotheses_full_coverage_1d1d.ps1`:
   - вынести `table_canon_pack` из цикла гипотез;
   - выполнять его один раз на mode/date.  
   Кодовая точка: `run_hypotheses_full_coverage_1d1d.ps1:263-274`.

5. В `run_p23_operator_unified.ps1` убрать повтор `table_convergence` если уже есть PASS от `daily_long_short_cycle` для того же pinned OOS (reuse готового отчёта).

6. В `search_gate_candidate` добавить ранний prune по статистике proxy до полного backtest-цикла по всем порогам (частично уже есть, но только по `grid_min > proxy_max`).

### P2 (архитектурный слой)

7. Перейти с subprocess-цепочки `search -> train -> oos` на in-process orchestration API (один Python-процесс на repeat).  
   Эквивалентная бизнес-логика, меньше старт/парсинг/IO.

8. Кэш `raw/frame` между шагами repeat:
   - единый `raw_df` для окна
   - reuse базовых фичей по horizon
   - без изменения формул.

9. В `table_canon_pack` добавить профили экспорта:
   - `stable_full` (как сейчас)
   - `stable_fast` (без XLSX, только csv/parquet/json для прогона)
   Это ускоряет прогон, не меняя торговую логику.

10. Для AKFP-контура ввести scheduler-приоритет:
   - сначала cheap-stage (search only / preflight / proxy sanity),
   - потом full-stage (train+oos) только для shortlisted кандидатов.

## 7) Конкретный приоритет до “боевого прогона”

1. P0.1/P0.2 (CPU-window + budget wait параметризация).  
2. P0.3 (table_canon 1 раз на daily-cycle).  
3. P1.4 (table_canon 1 раз на full-coverage mode).  
4. P1.5 (не дублировать convergence в p23).  
5. Контрольный прогон `1d train -> next 1d test` long и short раздельно, с фиксацией времени каждого шага.

## 8) Проверка “битых строк / символов”

Проверены рабочие каталоги `docs`, `AKFP`, `src/mlbotnav`, `configs` на replacement-char `U+FFFD`:  
результат `NO_UFFFD_FOUND` (в рабочей логике битых UTF-символов не обнаружено).

