# ТЗ: Канонизация Таблиц, Паритет Bybit и Порядок Артефактов
Дата: 2026-05-23
Проект: MLbotNav
Статус: в работе (P1-P4 закрыты, P5 приемка пройдена; дальше — развитие гипотез под strict-gate)

## 1) Цель
Навести строгий порядок в данных и таблицах до/после прогона, чтобы:
- свечи в проекте были идентичны Bybit по OHLCV и времени;
- все вычисления были понятны по столбцам (что за что отвечает);
- ML/симуляция/бэктест использовали единые правила причинности;
- артефакты прогона были собраны по полочкам (run-пакет), без поиска по десяткам папок.

## 2) Что выявлено аудитом (кратко)
1. Есть дубли и разрозненность слоёв:
- `data/raw/*` и `data/core/*` фактически дублируют OHLCV.
- `reports/*` хранит плоские наборы файлов без единого `run_id`.
2. Фичи считаются корректно в `dataset.py`, но единая материализованная таблица фич как артефакт run отсутствует.
3. Есть риск смешения режимов `research` и `exchange_like` в части запусков/отчётов.
4. Для пользователя таблицы после прогона читаются тяжело (CSV без человеко-ориентированной витрины).

## 3) Каноническая модель данных (обязательно)

### 3.1 Слои хранения
- `data/raw/` — только «как пришло с Bybit» (OHLCV/funding/OI).
- `data/curated/` — очищенные/дедуп/проверенные данные (канон для обучения).
- `data/features/` — материализованные фичи по `run_id`.
- `data/analytics/` — TA/pattern/signal вспомогательные таблицы.
- `data/meta/` — watermarks, статусы, контрольные хэши.
- `reports/runs/<run_id>/...` — все артефакты конкретного прогона.

### 3.2 Источник истины по столбцам
- Главный source-of-truth по фичам: `src/mlbotnav/dataset.py` (`FEATURE_COLUMNS`, `FEATURE_GROUPS`).
- `configs/features_block.yaml` — синхронный snapshot с русскими подписями, не ручной источник истины.

## 4) Канонический run-пакет (до и после прогона)

### 4.1 `run_id`
Формат:
`run_<UTC>_<symbol>_<tf>_<train_window>_<test_window>_<mode>_<rand6>`

Пример:
`run_20260523T113000Z_solusdt_1m_2026-05-17_2026-05-19_2026-05-20_2026-05-21_long_only_a1b2c3`

### 4.2 Структура
- `reports/runs/<run_id>/state/run_manifest.json`
- `reports/runs/<run_id>/state/params_snapshot.json`
- `reports/runs/<run_id>/state/status.json`
- `reports/runs/<run_id>/data/raw_snapshot_manifest.json`
- `reports/runs/<run_id>/data/feature_frame.parquet`
- `reports/runs/<run_id>/data/feature_frame.csv`
- `reports/runs/<run_id>/data/feature_dictionary_ru.csv`
- `reports/runs/<run_id>/pipeline/pipeline_report.json`
- `reports/runs/<run_id>/pipeline/oof.csv`
- `reports/runs/<run_id>/pipeline/backtest_trades.csv`
- `reports/runs/<run_id>/oos/oos_report.json`
- `reports/runs/<run_id>/oos/oos_backtest_trades.csv`
- `reports/runs/<run_id>/trade_simulation/trade_simulation.png`
- `reports/runs/<run_id>/trade_simulation/trade_simulation.json`
- `reports/runs/<run_id>/top_strategy/top_strategy_card.json`
- `reports/runs/<run_id>/top_strategy/TOP_STRATEGY_CARD.md`
- `reports/runs/<run_id>/index.json` (единый индекс всех файлов + sha256)

## 5) Табличный канон (что должно быть понятно пользователю)

### 5.1 Обязательные таблицы
1. `candles_canonical` (свечи Bybit 1:1)
- `symbol,timeframe,open_time_utc,close_time_utc,open,high,low,close,volume,turnover,source,ingest_run_id,row_hash`

2. `feature_frame` (ML-вход)
- Все 68 фич из `FEATURE_COLUMNS`.
- Плюс служебные: `symbol,timeframe,open_time_utc,close_time_utc,horizon_bars,target_up,future_return,run_id`.

3. `signal_frame`
- `open_time_utc,prob_up,signal_mode,side_raw,trend_filter,side_filtered,expected_move,ev,ev_usd,run_id`.

4. `execution_trace`
- `signal_time_utc,entry_time_utc,exit_time_utc,entry_price,exit_price,order_type,execution_mode,side,fee_usd,slippage_usd,net_pnl_usd,net_return,time_to_target_bars,exit_reason,run_id`

5. `strategy_summary`
- `run_id,net_return_pct,trades,hit_rate,max_drawdown_pct,sortino,cagr,no_trade_ratio_days,trades_per_day_avg,params_json`

### 5.2 Словарь столбцов (обязательно)
Для каждого столбца автоматически формируется словарь:
- `column_name_en`
- `column_name_ru`
- `block` (price_volatility/trend_momentum/...)
- `formula_text`
- `units`
- `computed_on` (`close(t)`)
- `used_in` (`signal/train/backtest/report`)
- `lookahead_safe` (`true/false`)
- `notes`

Выход словаря:
- `feature_dictionary_ru.csv` (машинный)
- `feature_dictionary_ru.xlsx` (человеко-читаемый для открытия вручную)

## 6) Единые правила причинности (без споров)
1. Анализ фич и сигнала выполняется только на закрытой свече `t`.
2. Сигнал формируется на `close(t)`.
3. Market-вход: `open(t+1)`.
4. Limit-вход: постановка от `close(t)`, исполнение только если диапазон следующей свечи реально задел цену.
5. Запрещён look-ahead в расчетах сигналов и TA, используемых для входа.
6. В отчётах всегда явно писать `execution_mode` и `order_type`.

## 7) Паритет с Bybit: что считаем «1 в 1»

### 7.1 По свечам (жестко)
- Совпадение OHLCV и UTC-меток: 100%.
- На 1m за день: ровно 1440 закрытых свечей (если день торговый и без остановок биржи).
- Нет дыр/дубликатов.

### 7.2 По исполнению (реалистичный допуск)
- Полного 100% совпадения с live matching engine недостижимо офлайн.
- Цель: `exchange_like` parity с зафиксированными допусками и прозрачной моделью комиссий/слиппеджа.

## 8) Разделение гипотез по блокам
- Базовая таблица свечей и фич — одна каноническая.
- Для каждой гипотезы создаётся отдельный «слой результатов»:
  `reports/runs/<run_id>/hypotheses/<hypothesis_id>/...`
- Числа OHLCV и базовых фич неизменны; меняются только фильтры/сигналы/сделки.

## 9) Пошаговый план внедрения (строго)

### Этап P0: Freeze и контракт
- Зафиксировать единый run-формат и структуру каталогов.
- Зафиксировать один активный режим для оценки: `execution_mode=exchange_like`.

### Этап P1: Канон свечей
- Ввести `candles_canonical` и daily parity-check.
- Сформировать отчет: дыры/дубли/расхождения OHLCV.

### Этап P2: Канон фич-таблицы
- Материализовать `feature_frame` в `reports/runs/<run_id>/data/`.
- Генерировать словарь столбцов RU/EN автоматически.

### Этап P3: Канон сигналов и исполнения
- Привести signal->execution trace к единому виду.
- Обязательные поля `entry/exit reason`, fee/slippage, mode/order_type.

### Этап P4: Канон артефактов
- Перевести плоские `reports/pipeline|final_review|adaptive` в per-run подпапки.
- Добавить `index.json` с хэшами и связями файлов.

### Этап P5: Приемка
- Проверка по чек-листу приемки (ниже).

## 10) Критерии приемки
1. Пользователь открывает один `feature_dictionary_ru.xlsx` и понимает все колонки.
2. Любой прогон имеет одну папку `reports/runs/<run_id>/...` со всеми артефактами.
3. По выбранному дню свечи Bybit и `candles_canonical` совпадают 1:1.
4. В каждом отчете явно указано: `signal on close(t)`, `entry on open(t+1)`.
5. Нет «случайного» графика: график всегда от того же `run_id`, что и top-стратегия.

## 11) Ограничения
- Ничего не удалять без архивирования.
- Не смешивать long/short-память: отдельные запуски и отдельные артефакты.
- CPU policy сохраняется: среднее до 85%, без сноса чужих процессов.
- После каждого фикса обязателен post-fix gate: сначала проверка шага, затем полный прогон контрольной цепочки ТЗ с отчетом PASS/FAIL.

## 12) Текущий прогресс и следующий шаг
Сделано на 2026-05-23:
- P1 закрыт: `candles_canonical` + `candles_parity_report.json` (без фейлов по текущему окну).
- P2 закрыт: `feature_frame`, `feature_frame_full`, `feature_dictionary_ru`, `targets_dictionary_ru`, `readable_tables_ru.xlsx`.
- P3 закрыт: `signal_frame`, `execution_trace`, `execution_trace_summary`, плюс цепочка аудита PASS.
- P4 закрыт: per-run артефакты в `reports/runs/<run_id>/` с `index.json` и `p4_pack_manifest.json`.
- P5 приемка: PASS (чек-лист в `reports/qa_gate/p5_acceptance_*.json`).

Следующий рабочий шаг:
- развивать стратегические гипотезы и функционал только через strict-gate после каждого фикса.

## Update 2026-05-23 (гипотезы: source-of-truth + gate)
- `adaptive_auto_train` переведен на чтение long-style гипотез из `configs/features_block.yaml`:
  - добавлены флаги `--features-config` и `--trend-hypothesis-profile`;
  - при `--long-style-1m` план берется из `hypotheses.<profile>`;
  - при недоступном конфиге включается безопасный fallback на прежний набор.
- После фикса выполнен строгий gate:
  - `reports/qa_gate/tz_gate_20260523T104941Z.json` -> `PASS`.
- Дополнительно подтверждена консистентность гипотез/контуров:
  - `reports/qa_gate/hypothesis_coverage_long_only_20260523T105000Z.json` -> `PASS`;
  - `reports/qa_gate/hypothesis_coverage_short_only_20260523T105000Z.json` -> `PASS`.
- Добавлен отдельный аудит блока фич/паттернов и вшит в strict-gate:
  - `src/mlbotnav/features_block_audit.py`;
  - проверка на дубли + полноту RU-меток для `technical_analysis` и `features.columns`.
  - `reports/qa_gate/features_block_audit_20260523T105228Z.json` -> `PASS`.
- Обновленный общий gate после вшивки аудита:
  - `reports/qa_gate/tz_gate_20260523T105238Z.json` -> `PASS`.

## Update 2026-05-23 (разделение гипотез long/short/both)
- В `adaptive_auto_train` добавлен профильный режим гипотез для раздельных контуров:
  - новый флаг `--use-hypothesis-profile`;
  - `--trend-hypothesis-profile auto` теперь выбирает профиль по `signal_mode`:
    - `long_only` -> `trend_filters_long_style_1m`
    - `short_only` -> `trend_filters_short_style_1m`
    - `both` -> `trend_filters_both_style_1m`
  - если профиль в конфиге отсутствует, применяется безопасный fallback по умолчанию (без падения пайплайна).
- В `summary` добавлены поля прозрачности:
  - `use_hypothesis_profile`,
  - `hypothesis_profile`,
  - `hypothesis_plan_source`,
  - `hypothesis_plan_config_path`.
- Обновлен аудит покрытия гипотез: теперь сверяет именно профиль из summary, а не hardcoded long-only.
- Проверки:
  - `reports/qa_gate/tz_gate_20260523T110257Z.json` -> `PASS`;
  - `reports/qa_gate/hypothesis_coverage_long_only_20260523T110316Z.json` -> `PASS`;
  - `reports/qa_gate/hypothesis_coverage_short_only_20260523T110316Z.json` -> `PASS`.

## Update 2026-05-23 (профили гипотез в конфиге)
- В `configs/features_block.yaml` добавлены явные профили:
  - `hypotheses.trend_filters_short_style_1m`
  - `hypotheses.trend_filters_both_style_1m`
- Усилен аудит `features_block_audit`:
  - теперь проверяет, что все 3 профиля (`long/short/both`) существуют и не пустые.
- Проверки:
  - `reports/qa_gate/features_block_audit_20260523T113029Z.json` -> `PASS`;
  - `reports/qa_gate/tz_gate_20260523T113041Z.json` -> `PASS`;
  - `reports/qa_gate/hypothesis_coverage_long_only_20260523T113100Z.json` -> `PASS`;
  - `reports/qa_gate/hypothesis_coverage_short_only_20260523T113100Z.json` -> `PASS`.

## Update 2026-05-23 (контрольный прогон + аудит причин)
- Выполнен контрольный прогон `long_only` + `short_only` в профильном режиме гипотез.
- Первичная попытка на окне `train=2026-05-21, test=2026-05-22` показала две причины:
  1) `search_failed` при слишком жестких параметрах walk-forward (`min_train_rows=1200`, `n_folds=3`, дальние горизонты) на 1-дневном train;
  2) `oos_failed` из-за отсутствия кэш-свечей за `2026-05-22` (`No part-final.csv`, в локальном кэше максимум `2026-05-21`).
- Повторный корректный контрольный прогон проведен на валидном окне кэша:
  - `train=2026-05-20`, `test=2026-05-21`
  - параметры WF смягчены: `min_train_rows=900`, `n_folds=2`, горизонты `1,2,3,4,6,8,12`.
- Результат повторного прогона:
  - `long_only`: сделки есть, best OOS `-7.6580%`, цель `+1%` не достигнута;
  - `short_only`: сделки есть, best OOS `-8.7796%`, цель `+1%` не достигнута.
- Артефакты:
  - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260523T115440Z.json`
  - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260523T115816Z.json`
- Проверки после прогона:
  - `reports/qa_gate/tz_gate_20260523T120150Z.json` -> `PASS`;
  - `reports/qa_gate/hypothesis_coverage_long_only_20260523T120150Z.json` -> `PASS`;
  - `reports/qa_gate/hypothesis_coverage_short_only_20260523T120150Z.json` -> `PASS`.

## Update 2026-05-23 (сходимость таблиц 5+)
- Выполнен усиленный аудит табличной цепочки на реальном OOS-ране со сделками:
  - `execution_trace_pack` построен по `oos_report_SOLUSDT_1m_2026-05-21_long_only_20260523T115647Z.json`;
  - получен непустой `execution_trace` (`3` сделки).
- Подтверждена сходимость ключевых таблиц:
  - `candles_canonical` rows = `2880`;
  - `feature_frame_full` rows = `2880` (1:1 к свечам);
  - `execution_trace` rows = `3`;
  - `execution_trace_summary.execution_rows = 3`;
  - все обязательные поля `signal/entry/exit/side/price` в `execution_trace` заполнены.
- Артефакт аудита:
  - `reports/table_canon_current/audit_chain_report.json` -> `PASS` (23 checks, failed=0).
- Финальный strict-gate после фиксации шага:
  - `reports/qa_gate/tz_gate_20260523T121515Z.json` -> `PASS`.

## Update 2026-05-23 (усиленный аудит сходимости: signal/execution time-contract)
- `audit_table_chain` расширен строгими проверками:
  - наличие/делимитер `signal_frame`;
  - `signal_frame` > 0 строк;
  - парсинг и диапазон `signal.open_time_utc` внутри `feature_frame_full`;
  - обязательные поля сигнала (`prob_up`, `side_raw`, `side_mode_filtered`, `side_executed`, `run_id`) заполнены;
  - опциональный режим `--require-trades` (боевой контроль: `execution_trace` не пустой);
  - временной контракт `signal_time <= entry_time <= exit_time`;
  - `entry/exit` внутри диапазона свечей.
- Боевой аудит на реальном OOS-ране со сделками:
  - `python -m mlbotnav.execution_trace_pack --oos-report ...115647Z.json`
  - `python -m mlbotnav.audit_table_chain --run-dir reports/table_canon_current --require-trades`
  - результат: `reports/table_canon_current/audit_chain_report.json` -> `PASS` (failed=0).
- Общий strict-gate после фикса:
  - `reports/qa_gate/tz_gate_20260523T124834Z.json` -> `PASS`.

## P5.3 Progress (нумерация подпунктов)
- `P5.3.4` Закрыт: единый оркестратор аудита `5+` (последовательный, без гонок):
  - модуль: `src/mlbotnav/table_convergence_5plus.py`
  - шаги внутри: `execution_trace_pack` -> `audit_table_chain --require-trades` -> optional `tz_gate_runner`.
- `P5.3.5` Закрыт: контрольный прогон + полный `5+` аудит на свежем OOS:
  - прогон: `adaptive_auto_train` (1 repeat, long_only, profile-mode);
  - OOS: `reports/final_review/oos_report_SOLUSDT_1m_2026-05-21_long_only_20260523T125258Z.json`;
  - итоговый отчет `5+`: `reports/qa_gate/table_convergence_5plus_20260523T125315Z.json` -> `PASS`.
- Дополнительные проверки после шага:
  - `reports/qa_gate/hypothesis_coverage_long_only_20260523T125336Z.json` -> `PASS`;
  - `reports/qa_gate/hypothesis_coverage_short_only_20260523T125336Z.json` -> `PASS`.

- `P5.3.6` Закрыт: симметричный контрольный цикл для `short_only` (прогон + 5+ аудит + gate):
  - прогон: `adaptive_auto_train` (`short_only`, `repeats=1`, профильный режим);
  - OOS: `reports/final_review/oos_report_SOLUSDT_1m_2026-05-21_short_only_20260523T125726Z.json`;
  - итоговый `5+` отчет: `reports/qa_gate/table_convergence_5plus_20260523T125746Z.json` -> `PASS`.
- Проверки консистентности профилей после `P5.3.6`:
  - `reports/qa_gate/hypothesis_coverage_short_only_20260523T125806Z.json` -> `PASS`;
  - `reports/qa_gate/hypothesis_coverage_long_only_20260523T125806Z.json` -> `PASS`.

- `P5.3.7` Закрыт:
  - реализован единый раннер ежедневного цикла `long/short`:
    - `src/mlbotnav/daily_long_short_cycle.py`
    - внутри на каждый контур: `adaptive_auto_train` -> `table_convergence_5plus --with-gate` -> `hypothesis_coverage_audit`.
  - контрольный запуск выполнен:
    - `reports/qa_gate/daily_long_short_cycle_20260523T130804Z.json` -> `PASS`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T131108Z.json` -> `PASS`.

- `P5.3.8` Закрыт: строгий single-contour раннер (без смешивания long/short в одном запуске):
  - модуль: `src/mlbotnav/contour_cycle.py`
  - обязательный флаг: `--mode long_only|short_only`;
  - цепочка внутри: `adaptive_auto_train` -> `table_convergence_5plus --with-gate` -> `hypothesis_coverage_audit`.
  - контрольный запуск:
    - `reports/qa_gate/contour_cycle_long_only_20260523T131724Z.json` -> `PASS`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T131909Z.json` -> `PASS`.

- `P5.3.9` Закрыт: симметричная приемка `short_only` на single-contour раннере:
  - контрольный запуск:
    - `reports/qa_gate/contour_cycle_short_only_20260523T132057Z.json` -> `PASS`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T132229Z.json` -> `PASS`.

- `P5.3.10` Закрыт: сводная dual-приемка двух контуров (`long+short`) одним отчетом:
  - модуль: `src/mlbotnav/p53_dual_acceptance.py`
  - проверяет одновременно:
    - PASS последних `contour_cycle_long_only` и `contour_cycle_short_only`;
    - совпадение параметров окна/символа/TF между long и short;
    - PASS шага `table_convergence_5plus` и `hypothesis_coverage_audit` в каждом контуре;
    - PASS последнего `tz_gate`.
  - отчет:
    - `reports/qa_gate/p53_dual_acceptance_20260523T132431Z.json` -> `PASS`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T132431Z.json` -> `PASS`.

- `P5.3.11` Закрыт: полный refresh-цикл + snapshot-сводка `5+`:
  - свежий daily-cycle двух контуров:
    - `reports/qa_gate/daily_long_short_cycle_20260523T132601Z.json` -> `PASS`;
  - повторная dual-приемка:
    - `reports/qa_gate/p53_dual_acceptance_20260523T132852Z.json` -> `PASS`;
  - новый snapshot-отчет с артефактами и ключевыми метриками сходимости:
    - модуль: `src/mlbotnav/p53_snapshot_report.py`
    - отчет: `reports/qa_gate/p53_snapshot_20260523T132852Z.json` -> `PASS`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T132900Z.json` -> `PASS`.

- `P5.3.12` Закрыт: preflight-защита окна/строк до запуска (чтобы исключить пустые прогоны и missing-day ошибки):
  - модуль: `src/mlbotnav/preflight_window.py`
  - проверяет до старта:
    - наличие train/test дней в локальных свечах;
    - загрузку train/test raw;
    - достаточность строк фич под walk-forward по каждому горизонту (`min_train_rows`, `n_folds`, `horizons-grid`).
  - интегрирован в раннеры:
    - `src/mlbotnav/contour_cycle.py` (task: `preflight_window`);
    - `src/mlbotnav/daily_long_short_cycle.py` (task: `preflight_window_<mode>`).
  - контрольные прогоны после вшивки:
    - `reports/qa_gate/contour_cycle_long_only_20260523T133144Z.json` -> `PASS`;
    - `reports/qa_gate/daily_long_short_cycle_20260523T133318Z.json` -> `PASS`.
  - сверки после шага:
    - `reports/qa_gate/p53_dual_acceptance_20260523T133612Z.json` -> `PASS`;
    - `reports/qa_gate/p53_snapshot_20260523T133612Z.json` -> `PASS`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T133612Z.json` -> `PASS`.

- `P5.3.13` Закрыт: release-bundle отчет «одним файлом» по всем ключевым PASS-артефактам P5.3:
  - модуль: `src/mlbotnav/p53_release_bundle.py`
  - формирует:
    - JSON: `reports/qa_gate/p53_release_bundle_*.json`
    - Markdown: `reports/qa_gate/p53_release_bundle_*.md`
  - свежий refresh-цикл и проверки:
    - `reports/qa_gate/daily_long_short_cycle_20260523T133741Z.json` -> `PASS`;
    - `reports/qa_gate/p53_dual_acceptance_20260523T134039Z.json` -> `PASS`;
    - `reports/qa_gate/p53_snapshot_20260523T134039Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T134039Z.json` -> `PASS`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T134055Z.json` -> `PASS`.

- `P5.3.14` Закрыт: freshness-guard (контроль «свежести» PASS-артефактов + 5+ quality-bar таблиц):
  - модуль: `src/mlbotnav/p53_freshness_guard.py`
  - проверяет:
    - что последние `daily_cycle/dual/snapshot/release_bundle/gate` имеют `status=PASS`;
    - что они свежие (`max_age_minutes`, сейчас 20);
    - что `table_canon_current/audit_chain_report.json` = `PASS`, `execution_trace_rows > 0`, и `execution_trace_rows_match_summary = true`.
  - свежий refresh-цикл и аудиты:
    - `reports/qa_gate/daily_long_short_cycle_20260523T134228Z.json` -> `PASS`;
    - `reports/qa_gate/p53_dual_acceptance_20260523T134524Z.json` -> `PASS`;
    - `reports/qa_gate/p53_snapshot_20260523T134524Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T134524Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T134524Z.json` -> `PASS`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T134540Z.json` -> `PASS`.

- `P5.3.15` Закрыт: consistency-matrix аудит (глубокая сходимость long/short до OOS-CSV):
  - модуль: `src/mlbotnav/p53_consistency_matrix.py`
  - проверяет:
    - совпадение окна/symbol/timeframe/repeats между контурами;
    - соответствие `signal_mode` в OOS (`long_only`/`short_only`);
    - наличие OOS backtest CSV и совпадение числа сделок с отчетом (`trades`) по `side != 0`;
    - PASS `table_convergence_5plus` в каждом contour-cycle.
  - исправление в шаге:
    - учет сделок в OOS CSV переведен с «числа строк» на `abs(side) > 0` (иначе завышалось из-за bar-by-bar формата).
  - отчеты:
    - `reports/qa_gate/p53_consistency_matrix_20260523T135225Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T135225Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T135225Z.json` -> `PASS`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T135225Z.json` -> `PASS`.

- `P5.3.16` Закрыт: фиксация Excel-совместимости таблиц внутри per-run пакета (без ручного импорта CSV):
  - модуль: `src/mlbotnav/run_artifact_pack.py`
  - добавлено:
    - автоматическая нормализация ключевых таблиц в `;` + `UTF-8 BOM` при упаковке:
      - `data/candles_canonical.csv`
      - `data/feature_frame.csv`
      - `data/feature_frame_full.csv`
      - `data/signal_frame.csv`
      - `data/execution_trace.csv`
    - запись результата нормализации в `state/p4_pack_manifest.json` (`normalized_csv`).
  - контрольный запуск упаковки:
    - `reports/runs/run_20260523T135225Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_a64a78/state/p4_pack_manifest.json` -> все `from_sep=';'`, `to_sep=';'`.
  - финальный strict-gate после шага:
    - `reports/qa_gate/tz_gate_20260523T135627Z.json` -> `PASS`.
  - дополнительные контрольные артефакты:
    - `reports/qa_gate/p53_release_bundle_20260523T135652Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T135652Z.json` -> `PASS`.

- `P5.3.17` Закрыт: отдельный guard упаковки CSV (контроль нормализации в latest run):
  - модуль: `src/mlbotnav/p53_pack_csv_guard.py`
  - проверяет:
    - наличие `state/p4_pack_manifest.json` в последнем `reports/runs/run_*`;
    - наличие блока `normalized_csv`;
    - что для каждой ключевой таблицы `exists=true` и `to_sep=';'`.
  - отчеты:
    - `reports/qa_gate/p53_pack_csv_guard_20260523T135754Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T135754Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T135807Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T135807Z.json` -> `PASS`.

- `P5.3.18` Закрыт: материализация `strategy_summary` + расширение аудита таблиц `5+`.
  - доработка:
    - `src/mlbotnav/execution_trace_pack.py`:
      - добавлен экспорт `data/strategy_summary.csv` и `data/strategy_summary.xlsx` с колонками:
        `run_id,net_return_pct,trades,hit_rate,max_drawdown_pct,sortino,cagr,no_trade_ratio_days,trades_per_day_avg,params_json`.
    - `src/mlbotnav/audit_table_chain.py`:
      - добавлена обязательная проверка `strategy_summary.csv`:
        - `sep=';'`,
        - наличие всех обязательных колонок,
        - непустой `run_id`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T155342Z.json` -> `PASS`;
    - `reports/qa_gate/daily_long_short_cycle_20260523T155434Z.json` -> `PASS`;
    - `reports/qa_gate/p53_dual_acceptance_20260523T155730Z.json` -> `PASS`;
    - `reports/qa_gate/p53_snapshot_20260523T155731Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T155731Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T155731Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T155731Z.json` -> `PASS`.

- `P5.3.19` Закрыт: включение `strategy_summary.csv` в per-run нормализацию и контроль пакета.
  - доработка:
    - `src/mlbotnav/run_artifact_pack.py`:
      - в блок `normalized_csv` добавлен `data/strategy_summary.csv`.
    - `src/mlbotnav/p53_pack_csv_guard.py`:
      - усилен контракт: теперь обязательно 6 файлов нормализации
        (`candles_canonical, feature_frame, feature_frame_full, signal_frame, execution_trace, strategy_summary`);
      - добавлена явная проверка `normalized_csv_required_files`.
  - PASS-артефакты:
    - `reports/qa_gate/p53_pack_csv_guard_20260523T155829Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T155829Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T155841Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T155841Z.json` -> `PASS`.

- `P5.3.20` Закрыт: проверка сходимости `CSV <-> XLSX` для ключевых таблиц (структура и строки).
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен:
      - обязательные артефакты `.xlsx` для:
        `candles_canonical`, `feature_frame`, `feature_frame_full`, `signal_frame`, `execution_trace`, `strategy_summary`;
      - проверки:
        - совпадение колонок `xlsx == csv`;
        - совпадение количества строк `xlsx == csv`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран на свежем OOS;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T160420Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T160441Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T160457Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T160457Z.json` -> `PASS`.

- `P5.3.21` Закрыт: строгая сходимость `feature_frame` и словарей (`feature_dictionary/targets_dictionary`) с source-of-truth.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `feature_frame_full` содержит все `FEATURE_COLUMNS`;
      - `feature_dictionary_ru.csv`:
        - без дублей `column_name_en`,
        - точное соответствие списку `FEATURE_COLUMNS` (без пропусков/лишних);
      - `targets_dictionary_ru.csv` содержит ровно `future_return` и `target_up`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T160921Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T160942Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T160958Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T160958Z.json` -> `PASS`.

- `P5.3.22` Закрыт: строгий причинно-временной контракт для market-входа (`signal -> entry`).
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверкой:
      - для `order_type=market` вход должен быть на открытии следующей свечи после сигнальной;
      - проверка формирует `bad_rows` и примеры расхождений (до 5).
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T161307Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T161327Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T161343Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T161343Z.json` -> `PASS`.

- `P5.3.23` Закрыт: консистентность `run_id` и метрик между `signal/execution/strategy_summary/OOS`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - единичный `run_id` в `signal_frame`, `execution_trace`, `strategy_summary`;
      - совпадение `run_id` между тремя таблицами;
      - `strategy_summary.trades == execution_trace rows`;
      - `strategy_summary.params_json` парсится и содержит `strategy` + `risk_policy`;
      - `strategy_summary.net_return_pct` совпадает с `oos_report.backtest.net_return_pct`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T161518Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T161539Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T161555Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T161555Z.json` -> `PASS`.

- `P5.3.24` Закрыт: проверка соответствия OOS-окну (`test_day..test_end_day`) для signal/execution таблиц.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен:
      - `signal_frame_within_oos_window`;
      - `execution_signal_time_utc_within_oos_window`;
      - `execution_entry_time_utc_within_oos_window`;
      - `execution_exit_time_utc_within_oos_window`.
    - окно берется из `source_oos_report` (`test_day`, `test_end_day`) и проверяется как
      `[test_day 00:00 UTC, test_end_day+1 00:00 UTC)`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T161728Z.json` -> `PASS`;
    - `reports/qa_gate/daily_long_short_cycle_20260523T161814Z.json` -> `PASS`;
    - `reports/qa_gate/p53_dual_acceptance_20260523T162110Z.json` -> `PASS`;
    - `reports/qa_gate/p53_snapshot_20260523T162110Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T162110Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T162110Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T162110Z.json` -> `PASS`.

- `P5.3.25` Закрыт: сверка `oos_backtest_trades.csv` с витринными таблицами исполнения.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен:
      - парсинг `source_backtest_csv` из `execution_trace`;
      - проверка наличия/парсинга `oos_backtest_trades.csv`;
      - проверка `executed rows (abs(side)>0)`:
        - `== execution_trace rows`;
        - `== strategy_summary.trades`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран на свежем OOS;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T162447Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T162507Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T162522Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T162522Z.json` -> `PASS`.

- `P5.3.26` Закрыт: финансовая сходимость `execution_trace` (PnL и cost balance).
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `execution_trace_cost_balance_gross_minus_costs_equals_net`
        (`gross_pnl_usd - fee_usd_est - slippage_usd_est == net_pnl_usd`);
      - `execution_trace_net_pnl_matches_net_return_times_notional`
        (сверка `net_pnl_usd` с `net_return * notional_usd` из `oos_report.risk_policy`).
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T163111Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T163133Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T163148Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T163148Z.json` -> `PASS`.

- `P5.3.27` Закрыт: сходимость `signal_frame` с источником `oos_backtest_trades.csv`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `signal_frame_rows_match_oos_backtest_rows`;
      - `signal_frame_time_range_match_oos_backtest`.
    - сверка выполняется по `source_backtest_csv` из `execution_trace`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T163327Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T163346Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T163401Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T163401Z.json` -> `PASS`.

- `P5.3.28` Закрыт: строгий таймфрейм-контракт свечей в `candles_canonical`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `candles_close_minus_open_equals_timeframe_step`;
      - `candles_open_time_step_equals_timeframe_step`.
    - шаг таймфрейма берется через `timeframe_delta(timeframe)` и проверяется на каждой строке.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T163554Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T163614Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T163630Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T163630Z.json` -> `PASS`.

- `P5.3.29` Закрыт: построчная сходимость `signal_frame` и `oos_backtest` по бару.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `signal_backtest_open_time_full_match` (полное совпадение множества `open_time_utc`);
      - `signal_backtest_prob_up_match` (побаровое совпадение `prob_up`, `atol=1e-12`);
      - `signal_backtest_side_match` (побаровое совпадение `side_executed` и `side`).
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T163821Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T163840Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T163855Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T163856Z.json` -> `PASS`.

- `P5.3.30` Закрыт: контроль чистоты числовых полей (NaN/Inf) в ключевых таблицах.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `candles_key_numeric_clean` (`open/high/low/close/volume/turnover`);
      - `signal_key_numeric_clean` (`prob_up/expected_move_pct/ev/ev_usd`);
      - `feature_full_price_numeric_clean` (OHLC в `feature_frame_full`);
      - `feature_train_indicator_numeric_clean` (EMA/ATR/RSI в train-ready `feature_frame`).
    - учтена warmup-логика: индикаторы проверяются на `feature_frame` (после dropna), а не на полном кадре.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T164213Z.json` -> `PASS`;
    - `reports/qa_gate/daily_long_short_cycle_20260523T164300Z.json` -> `PASS`;
    - `reports/qa_gate/p53_dual_acceptance_20260523T164603Z.json` -> `PASS`;
    - `reports/qa_gate/p53_snapshot_20260523T164603Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T164603Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T164603Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T164603Z.json` -> `PASS`.

- `P5.3.31` Закрыт: строгий UTC-контракт временных полей в таблицах.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `candles_open_time_utc_suffix` и `candles_close_time_utc_suffix`;
      - `signal_open_time_utc_suffix`;
      - `execution_signal_time_utc_suffix`, `execution_entry_time_utc_suffix`, `execution_exit_time_utc_suffix`.
    - проверка требует суффикс `+00:00` (UTC) в строковых временных полях.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T164739Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T164759Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T164815Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T164815Z.json` -> `PASS`.

- `P5.3.32` Закрыт: сходимость параметров `strategy_summary.params_json` с `oos_report`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `strategy_summary_params_mode_match_oos`
        (`signal_mode`, `execution_mode`, `order_type`);
      - `strategy_summary_params_numeric_match_oos`
        (`leverage`, `notional_usd`, `fee_bps`, `slippage_bps`).
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T165740Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T165800Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T165815Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T165815Z.json` -> `PASS`.

- `P5.3.33` Закрыт: денежная и агрегатная сверка итогов `execution_trace` с OOS backtest.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `execution_trace_net_pnl_total_matches_oos_backtest`
        (сумма `net_pnl_usd` по trace = `backtest.net_pnl_total_usd`);
      - `strategy_summary_trades_per_day_avg_matches_oos_backtest`
        (`strategy_summary.trades_per_day_avg` = `backtest.trades_per_day_avg`).
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T170131Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T170152Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T170208Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T170208Z.json` -> `PASS`.

- `P5.3.34` Закрыт: качество сделок `execution_trace` (ID/порядок/цены).
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `execution_trade_id_non_empty`;
      - `execution_trade_id_unique`;
      - `execution_prices_positive`;
      - `execution_signal_time_monotonic`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - примечание по post-fix freshness:
    - для восстановления «свежего» PASS-контра был выполнен `daily_long_short_cycle` в режиме `short_only` (последний успешный daily-артефакт).
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T171041Z.json` -> `PASS`;
    - `reports/qa_gate/daily_long_short_cycle_20260523T171322Z.json` -> `PASS`;
    - `reports/qa_gate/p53_dual_acceptance_20260523T171452Z.json` -> `PASS`;
    - `reports/qa_gate/p53_snapshot_20260523T171452Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T171452Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T171452Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T171452Z.json` -> `PASS`.

- `P5.3.35` Закрыт: доменные ограничения `side` для сигналов и сделок.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `signal_side_raw_in_domain_minus1_0_1`;
      - `signal_side_mode_filtered_in_domain_minus1_0_1`;
      - `signal_side_executed_in_domain_minus1_0_1`;
      - `execution_side_in_domain_minus1_plus1`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T172121Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T172142Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T172159Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T172159Z.json` -> `PASS`.

- `P5.3.36` Закрыт: доменные ограничения вероятностей и издержек.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `signal_prob_up_in_0_1`;
      - `signal_expected_move_pct_non_negative`;
      - `execution_fee_usd_est_non_negative`;
      - `execution_slippage_usd_est_non_negative`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T172411Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T172432Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T172449Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T172449Z.json` -> `PASS`.

- `P5.3.37` Закрыт: связность `signal_frame -> execution_trace` на уровне сделки.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверкой:
      - `execution_rows_link_to_signal_frame_by_time_and_side`;
    - каждая строка `execution_trace` должна иметь соответствие в `signal_frame`
      по `(signal_time_utc == open_time_utc, side == side_executed)`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T172620Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T172641Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T172658Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T172658Z.json` -> `PASS`.

- `P5.3.38` Закрыт: построчный паритет `execution_trace` с executed-строками `oos_backtest`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `oos_backtest_exec_key_unique`;
      - `execution_trace_key_unique`;
      - `execution_trace_rows_match_oos_backtest_exec_keys`;
      - `execution_entry_time_match_oos_backtest`;
      - `execution_exit_time_match_oos_backtest`;
      - `execution_entry_price_match_oos_backtest`;
      - `execution_exit_price_match_oos_backtest`;
      - `execution_net_pnl_match_oos_backtest`;
      - `execution_exit_reason_match_oos_backtest`.
    - сверка выполняется по ключу сделки `(signal_time_utc/open_time_utc, side)`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T172852Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T172913Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T172931Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T172931Z.json` -> `PASS`.

- `P5.3.39` Закрыт: валидация правил формирования сигнала по порогам.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `signal_p_enter_long_in_0_1`;
      - `signal_p_enter_short_in_0_1`;
      - `signal_p_enter_long_gt_p_enter_short`;
      - `signal_side_raw_matches_prob_threshold_rule`;
      - `signal_side_mode_filtered_respects_signal_mode`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T173111Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T173133Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T173150Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T173150Z.json` -> `PASS`.

- `P5.3.40` Закрыт: временная целостность `signal_frame` по таймфрейму.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `signal_open_time_unique`;
      - `signal_open_time_monotonic`;
      - `signal_open_time_step_is_positive_and_multiple_of_timeframe_step`.
    - шаг сигнала проверяется как положительный и кратный шагу таймфрейма (без ложных фейлов на sparse-сигналы).
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - примечание по post-fix freshness:
    - для актуализации свежих PASS-артефактов выполнен `daily_long_short_cycle` в режиме `short_only`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T175356Z.json` -> `PASS`;
    - `reports/qa_gate/daily_long_short_cycle_20260523T175443Z.json` -> `PASS`;
    - `reports/qa_gate/p53_dual_acceptance_20260523T175616Z.json` -> `PASS`;
    - `reports/qa_gate/p53_snapshot_20260523T175616Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T175616Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T175616Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T175616Z.json` -> `PASS`.

- `P5.3.41` Закрыт: соответствие направлений сделок режиму сигнала (`signal_mode`).
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверкой:
      - `execution_side_respects_oos_signal_mode`.
    - правило:
      - при `long_only` в `execution_trace.side` допускается только `+1`;
      - при `short_only` допускается только `-1`;
      - при `both` допускаются только `-1` и `+1`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T180112Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T180133Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T180150Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T180150Z.json` -> `PASS`.

- `P5.3.42` Закрыт: соответствие metadata исполнения (`execution_mode/order_type`) OOS-контракту.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `execution_trace_execution_mode_matches_oos`;
      - `execution_trace_order_type_matches_oos`.
    - значения в каждой строке `execution_trace` сверяются с `oos_report.risk_policy`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T180926Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T180947Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T181003Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T181004Z.json` -> `PASS`.

- `P5.3.43` Закрыт: расширенная сверка метрик `strategy_summary` с `oos.backtest`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `strategy_summary_hit_rate_matches_oos_backtest`;
      - `strategy_summary_max_drawdown_matches_oos_backtest`;
      - `strategy_summary_sortino_matches_oos_backtest`;
      - `strategy_summary_cagr_matches_oos_backtest`;
      - `strategy_summary_no_trade_ratio_days_matches_oos_backtest`.
    - добавлен helper `_float_equal` (корректная обработка `NaN`/чисел с `atol`).
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T181233Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T181256Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T181313Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T181313Z.json` -> `PASS`.

- `P5.3.44` Закрыт: финансовый контракт доходностей/плеча в `execution_trace`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `execution_net_return_matches_unlevered_times_leverage`;
      - `execution_gross_pnl_matches_gross_return_times_notional_and_leverage`.
    - параметры `notional_usd` и `leverage` берутся из `oos_report.risk_policy`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T181446Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T181508Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T181525Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T181525Z.json` -> `PASS`.

- `P5.3.45` Закрыт: контракт длительности сделки и `time_to_target`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `execution_duration_non_negative`;
      - `execution_duration_multiple_of_timeframe_step`;
      - `execution_time_to_target_sec_within_trade_duration` (если поле заполнено).
    - длительность сделки проверяется как `(exit_time_utc - entry_time_utc)` в секундах.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - примечание по post-fix freshness:
    - для актуализации «свежих» PASS-артефактов выполнен `daily_long_short_cycle` в режиме `short_only`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T181647Z.json` -> `PASS`;
    - `reports/qa_gate/daily_long_short_cycle_20260523T181745Z.json` -> `PASS`;
    - `reports/qa_gate/p53_dual_acceptance_20260523T181922Z.json` -> `PASS`;
    - `reports/qa_gate/p53_snapshot_20260523T181922Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T181922Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T181922Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T181922Z.json` -> `PASS`.

- `P5.3.46` Закрыт: расширенный паритет параметров risk/strategy между `params_json` и `oos_report`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен:
      - helper `_scalar_equal` для корректного сравнения чисел/булевых/строк;
      - проверка `strategy_summary_params_extended_match_oos` по полям:
        - `risk_policy`: `stop_loss_pct`, `take_profit_pct`, `min_expected_move_pct`, `tp_min_factor`, `cooldown_bars`, `trend_filter`, `min_abs_ema_gap`, `dynamic_tp_enabled`;
        - `strategy`: `horizon_bars`, `p_enter_long`, `p_enter_short`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T182115Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T182137Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T182153Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T182154Z.json` -> `PASS`.

- `P5.3.47` Закрыт: контракт `run_id` и источников артефактов в `execution_trace`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `execution_trace_run_id_non_empty`;
      - `execution_trace_run_id_single`;
      - `execution_trace_run_id_format_trace_prefix`;
      - `execution_trace_run_id_matches_summary`;
      - `execution_trace_source_oos_report_consistent_and_exists`;
      - `execution_trace_source_backtest_csv_consistent_and_exists`.
    - проверяется единый `run_id` во всех строках trace + совпадение с `execution_trace_summary.json`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T182320Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T182340Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T182356Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T182357Z.json` -> `PASS`.

- `P5.3.48` Закрыт: константность и паритет конфигурации `signal_frame` с OOS.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `signal_frame_signal_mode_single`, `signal_frame_signal_mode_matches_oos`;
      - `signal_frame_p_enter_long_single`, `signal_frame_p_enter_long_matches_oos`;
      - `signal_frame_p_enter_short_single`, `signal_frame_p_enter_short_matches_oos`;
      - `signal_frame_trend_filter_single`, `signal_frame_trend_filter_matches_oos`;
      - `signal_frame_min_abs_ema_gap_single`, `signal_frame_min_abs_ema_gap_matches_oos`;
      - `signal_frame_min_expected_move_pct_single`, `signal_frame_min_expected_move_pct_matches_oos`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T182759Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T182822Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T182839Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T182839Z.json` -> `PASS`.

- `P5.3.49` Закрыт: расширенный паритет `signal_frame` с `oos_backtest` по EV-полям.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `signal_backtest_expected_move_pct_match`;
      - `signal_backtest_ev_match`;
      - `signal_backtest_ev_usd_match`.
    - сверка выполняется построчно на общем ключе `open_time_utc` (в рамках блока `signal_backtest_*`).
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T183338Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T183401Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T183418Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T183418Z.json` -> `PASS`.

- `P5.3.50` Закрыт: полнота и валидность словаря фич (`feature_dictionary_ru`).
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `feature_dict_required_columns_present`;
      - `feature_dict_column_name_ru_non_empty`;
      - `feature_dict_formula_text_non_empty`;
      - `feature_dict_computed_on_non_empty`;
      - `feature_dict_used_in_non_empty`;
      - `feature_dict_computed_on_domain_valid` (`close(t)` / `post_close_label`);
      - `feature_dict_lookahead_safe_boolean_like`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T183551Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T183612Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T183628Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T183628Z.json` -> `PASS`.

- `P5.3.51` Закрыт: сходимость словарей между `CSV` и `XLSX`.
  - доработка:
    - `src/mlbotnav/audit_table_chain.py` расширен проверками:
      - `feature_dictionary_xlsx_columns_match_csv`;
      - `feature_dictionary_xlsx_rows_match_csv`;
      - `targets_dictionary_xlsx_columns_match_csv`;
      - `targets_dictionary_xlsx_rows_match_csv`.
    - сверяются листы `features_dictionary` и `targets_dictionary` в `feature_dictionary_ru.xlsx`.
  - контрольный прогон шага:
    - `execution_trace_pack` пересобран;
    - `audit_table_chain --require-trades` -> `PASS`;
    - `table_convergence_5plus` -> `PASS`;
    - strict gate -> `PASS`.
  - PASS-артефакты:
    - `reports/qa_gate/table_convergence_5plus_20260523T183756Z.json` -> `PASS`;
    - `reports/qa_gate/tz_gate_20260523T183818Z.json` -> `PASS`;
    - `reports/qa_gate/p53_release_bundle_20260523T183834Z.json` -> `PASS`;
    - `reports/qa_gate/p53_freshness_guard_20260523T183834Z.json` -> `PASS`.
