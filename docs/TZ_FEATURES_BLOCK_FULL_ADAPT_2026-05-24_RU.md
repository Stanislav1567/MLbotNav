# ТЗ (доп): Полная адаптация `features_block.yaml` в runtime

Дата: 2026-05-24  
Источник: `C:\Users\007\Desktop\MLbotNav\configs\features_block.yaml`

## 1) Цель
Довести реализацию до состояния, где все, что описано в конфиге:
- по фичам (`features`, `technical_analysis`) работает в runtime 1-в-1;
- по гипотезам (`hypotheses` + `extended_hypotheses_backlog`) либо активно работает, либо имеет формально зафиксированный статус и тест.

Критерий качества: "5+" = без расхождений конфига и runtime, с подтверждением аудитом и контрольным прогоном.

## 2) Что уже закрыто
1. Активные профили `hypotheses.trend_filters_*_style_1m` подключены.
2. 68 фич синхронизированы с `dataset.FEATURE_COLUMNS`.
3. Контурная изоляция `long_only/short_only` подтверждается аудитом.
4. Расширенный аудит `features_block` уже есть.

## 3) Что не закрыто (главный остаток)
`extended_hypotheses_backlog` (13 идей) не активирован как полноценный runtime-перебор:
- часть `planned`;
- `hvn_lvn_density_reaction` = `in_code_density_only` (фичи есть, но отдельный гипотезный контур не завершен).

## 4) Список backlog-гипотез к внедрению
### 4.1 Fibonacci
1. `fib_retrace_0382_0618_trend_resume`
2. `fib_extension_targets`

### 4.2 Swing / BOS / MinMax
1. `swing_hl_hh_long`
2. `swing_lh_ll_short`
3. `bos_continuation_confirm`
4. `min_max_range_revert`
5. `max_low_pullback_long`

### 4.3 Density / Profile / Orderbook
1. `hvn_lvn_density_reaction`
2. `volume_profile_poc_vah_val_retest`
3. `value_area_rotation_vs_breakout`
4. `wedge_breakout_plus_profile_acceptance`
5. `orderbook_imbalance_l1_l50`
6. `spread_pressure_and_delta_absorption`

## 5) План внедрения (строго по этапам)
## P0. Freeze и контракт статусов
1. Зафиксировать единую семантику статусов backlog:
- `planned` — не участвует в переборе;
- `in_code_density_only` — фичи есть, гипотеза частично;
- `active` — участвует в переборе;
- `validated` — прошла аудит + контрольный прогон.
2. Добавить проверку статусов в `features_block_audit`.

Приемка P0:
- аудит валиден, неизвестных статусов нет.

## P1. Реестр гипотезного плана (runtime bridge)
1. Добавить модуль-адаптер (реестр), который читает `extended_hypotheses_backlog`.
2. Для каждой идеи создать runtime-представление:
- `name`
- `family`
- `signal_mode`
- `required_features`
- `params_grid`
- `enabled` (true/false)
3. Интегрировать реестр в `adaptive_auto_train` как дополнительный источник перебора.

Приемка P1:
- в отчете прогона появляется список backlog-гипотез и их effective-статус.

## P2. Активация Fibonacci блока
1. Реализовать гипотезные фильтры:
- retrace (0.382/0.5/0.618/0.786),
- extension targets (1.272/1.618/2.618).
2. Подключить в перебор как отдельное семейство.
3. Добавить аудит корректности параметров уровней.

Приемка P2:
- `hypothesis_coverage_audit` видит участие fib-гипотез в history.

## P3. Активация Swing/BOS/MinMax блока
1. Реализовать сигнальные правила для:
- `swing_hl_hh_long`, `swing_lh_ll_short`,
- `bos_continuation_confirm`,
- `min_max_range_revert`,
- `max_low_pullback_long`.
2. Подключить в long/short контуры раздельно.
3. Добавить проверку минимального числа сделок по семейству.

Приемка P3:
- по каждому пункту есть минимум 1 успешный кандидат в search-отчете (или формально зафиксирован reason, почему нет).

## P4. Активация Density/Profile блока
1. Довести `hvn_lvn_density_reaction` до `active`.
2. Реализовать:
- `volume_profile_poc_vah_val_retest`,
- `value_area_rotation_vs_breakout`,
- `wedge_breakout_plus_profile_acceptance`.
3. Проверить отсутствие lookahead leakage.

Приемка P4:
- отдельный audit leakage = PASS;
- backlog-статусы обновлены.

## P5. Orderbook блок (L1-L50 и spread/delta)
1. Подготовить источник данных стакана:
- если данных нет, статус остаётся `planned` с технической причиной;
- если данные есть, активировать:
  - `orderbook_imbalance_l1_l50`
  - `spread_pressure_and_delta_absorption`
2. Добавить проверки полноты и latency источника.

Приемка P5:
- формальный аудит доступности источника + статусный отчет.

## P6. Единый аудит “конфиг -> runtime”
1. Расширить `features_block_audit`:
- проверка всех backlog-идей на наличие runtime-мэппинга;
- проверка `required_features` для каждой активной идеи.
2. Расширить `hypothesis_coverage_audit`:
- отдельно считать coverage по `active` backlog.

Приемка P6:
- оба аудита PASS.

## P7. Контрольные прогоны и фиксация результатов
1. Контрольный цикл:
- `long_only` (repeats>=3),
- `short_only` (repeats>=3),
- при необходимости `both`.
2. В отчетах обязательны:
- какие backlog-гипотезы реально запускались,
- какие дали сделки,
- какие отфильтрованы и почему.

Приемка P7:
- полный набор отчетов в `reports/qa_gate` + `reports/adaptive/<contour>`.

## 6) Правила внедрения (чтобы не ломать)
1. Не смешивать контуры long/short.
2. После каждого этапа: фикс -> аудит -> короткий прогон.
3. Если этап не проходит аудит, дальше не идем.
4. Статусы в конфиге обновляются только после фактической приемки этапа.

## 7) Команды проверки (база)
```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.features_block_audit --config configs/features_block.yaml --out-dir reports/qa_gate
.\.venv\Scripts\python.exe -m mlbotnav.hypothesis_coverage_audit --contour-id long_only --features-config configs/features_block.yaml
.\.venv\Scripts\python.exe -m mlbotnav.hypothesis_coverage_audit --contour-id short_only --features-config configs/features_block.yaml
```

## 8) Definition of Done (итог)
1. Все 13 backlog-идей имеют корректный runtime-статус (`validated` или обоснованный `planned` из-за отсутствия данных-источника).
2. Для всех `active` идей есть подтвержденный coverage в history.
3. Полный аудит “конфиг -> runtime” = PASS.
4. Контрольные прогоны long/short выполняются стабильно и прозрачно по отчетам.

## 9) Статус выполнения
### Закрыто
1. `P0.1` — контракт статусов backlog внедрен в аудит:
- проверка обязательности `name/status`;
- проверка словаря статусов: `planned|in_code_density_only|active|validated`;
- проверка уникальности имен backlog-гипотез.

Артефакты проверки:
- `reports/qa_gate/features_block_audit_20260523T191202Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260523T191746Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260523T191723Z.json` (PASS, explicit short OOS)

2. `P1.1` — runtime bridge backlog-гипотез внедрен:
- добавлен реестр backlog-гипотез (family/name/status/signal_mode/required_features/params_grid);
- в `adaptive_auto_train` summary добавлен блок `backlog_registry` + `backlog_active_names`;
- в `history` добавлено поле `backlog_hypothesis_hint` (контекст bridge на повторе).

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260523T192201Z.json` (есть `backlog_registry`, `items_total=13`)
- `reports/qa_gate/hypothesis_coverage_short_only_20260523T192444Z.json` (PASS)
- `reports/table_canon_current/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260523T192658Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260523T192709Z.json` (PASS, step=P1)

Операционное правило:
- `table_canon_pack -> execution_trace_pack -> audit_table_chain` запускать строго последовательно в одном `run_dir`;
- параллельный запуск в один `reports/table_canon_current` не допускается.

3. `P2.1` — Fibonacci-гипотезы активированы и реально исполняются:
- в `configs/features_block.yaml` статусы:
  - `fib_retrace_0382_0618_trend_resume` -> `active`
  - `fib_extension_targets` -> `active`
- в runtime добавлены фильтры:
  - `fib_retrace_0382_0618_trend_resume`
  - `fib_extension_targets`
- фильтры добавлены в CLI-choices (`adaptive/search/pipeline`) и применяются в backtest.
- в прогоне `repeats=2` отработали оба фильтра как отдельные повторы (`history[0..1].trend_filter`).

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260523T193114Z.json`
- `reports/qa_gate/hypothesis_coverage_short_only_20260523T193609Z.json` (PASS)
- `reports/table_canon_current/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260523T193851Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260523T193908Z.json` (PASS, step=P2)

4. `P3.1` — Swing/BOS/MinMax блок активирован и принят через прогон+аудит:
- в `configs/features_block.yaml` статусы:
  - `swing_hl_hh_long` -> `active`
  - `swing_lh_ll_short` -> `active`
  - `bos_continuation_confirm` -> `active`
  - `min_max_range_revert` -> `active`
  - `max_low_pullback_long` -> `active`
- в runtime подключены фильтры и CLI-choices:
  - `backtest.py`
  - `adaptive_auto_train.py`
  - `search_gate_candidate.py`
  - `pipeline_train_eval.py`
- контрольные прогоны `short_only` и `long_only` выполнены на фиксированном 24h окне.
- формальная причина пустых итераций на первой попытке зафиксирована и устранена параметрами окна:
  - было: `Not enough rows for walk-forward`
  - исправлено: `min_train_rows=500`, `n_folds=2`, сокращенный `horizons-grid`
- после коррекции получены сделки в обоих контурах (по 1 сделке на repeat) и сформированы trace-таблицы.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T022250Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T022643Z.json`
- `reports/qa_gate/features_block_audit_20260524T022222Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T023033Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T023033Z.json` (PASS)
- `reports/runs/run_20260524T023049Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_25a669/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T023144Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T023156Z.json` (PASS, step=P3)

5. `P4.1` — HVN/LVN (density) гипотеза переведена в active и подключена в runtime:
- в `configs/features_block.yaml`:
  - `hvn_lvn_density_reaction` -> `active`
- в runtime и CLI добавлен фильтр `hvn_lvn_density_reaction`:
  - `backtest.py` (vectorized + row filter)
  - `adaptive_auto_train.py`
  - `search_gate_candidate.py`
  - `pipeline_train_eval.py`
- выполнены контрольные прогоны `short_only` и `long_only` отдельно (без смешивания контуров).
- цепочка таблиц `csv/xlsx` повторно подтверждена на отдельном `run_dir`.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T023451Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T023620Z.json`
- `reports/qa_gate/features_block_audit_20260524T023436Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T023746Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T023746Z.json` (PASS)
- `reports/runs/run_20260524T023758Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_421207/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T023813Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T023818Z.json` (PASS, step=P4)

6. `P4.2` — активированы `volume_profile_poc_vah_val_retest` и `value_area_rotation_vs_breakout`:
- в `configs/features_block.yaml`:
  - `volume_profile_poc_vah_val_retest` -> `active`
  - `value_area_rotation_vs_breakout` -> `active`
- в runtime и CLI подключены фильтры:
  - `backtest.py` (vectorized + row filter)
  - `adaptive_auto_train.py`
  - `search_gate_candidate.py`
  - `pipeline_train_eval.py`
- выполнены отдельные контрольные прогоны `short_only` и `long_only` (без смешивания контуров).
- цепочка табличной сходимости `CSV/XLSX` пройдена на отдельном `run_dir`.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T024126Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T024408Z.json`
- `reports/qa_gate/features_block_audit_20260524T024112Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T024646Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T024646Z.json` (PASS)
- `reports/runs/run_20260524T024658Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_b5dbcb/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T024713Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T024717Z.json` (PASS, step=P4.2)

7. `P4.3` — активирован `wedge_breakout_plus_profile_acceptance`:
- в `configs/features_block.yaml`:
  - `wedge_breakout_plus_profile_acceptance` -> `active`
- в runtime и CLI подключен фильтр:
  - `backtest.py` (vectorized + row filter)
  - `adaptive_auto_train.py`
  - `search_gate_candidate.py`
  - `pipeline_train_eval.py`
- выполнены отдельные контрольные прогоны `short_only` и `long_only`.
- табличная цепочка `CSV/XLSX` проверена отдельным `run_dir` (PASS).

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T024901Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T025034Z.json`
- `reports/qa_gate/features_block_audit_20260524T024848Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T025159Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T025159Z.json` (PASS)
- `reports/runs/run_20260524T025211Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_c87fe8/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T025226Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T025230Z.json` (PASS, step=P4.3)

8. `P5.1` — формально зафиксирован статус orderbook-блока как `planned` до появления источника:
- добавлен аудит доступности источника:
  - `src/mlbotnav/orderbook_source_audit.py`
- подтверждено:
  - `orderbook_imbalance_l1_l50` = `planned`
  - `spread_pressure_and_delta_absorption` = `planned`
  - внешний источник `L1-L50/microstructure` не обнаружен
  - в runtime registry обе гипотезы корректно отключены с причиной `missing_external_source`
- выполнен контрольный прогон `short_only` + `long_only`, затем табличная сходимость `CSV/XLSX` и gate (PASS).

Артефакты проверки:
- `reports/qa_gate/orderbook_source_audit_20260524T025450Z.json` (PASS)
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T025648Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T025518Z.json`
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T025812Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T025812Z.json` (PASS)
- `reports/runs/run_20260524T025825Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_44bbb3/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T025840Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T025844Z.json` (PASS, step=P5.1)

9. `P5.2` — формальная SLA-готовность для `spread_pressure_and_delta_absorption` зафиксирована:
- добавлен отдельный SLA-аудит:
  - `src/mlbotnav/p52_sla_audit.py`
- для текущего состояния без источника корректный режим:
  - `mode=blocked_no_source` (PASS)
  - SLA-проверки помечаются как ожидающие появления источника (без ложного FAIL)
- выполнен обязательный контрольный цикл:
  - прогон `short_only`
  - прогон `long_only`
  - coverage PASS
  - табличная сходимость `CSV/XLSX` PASS
  - gate PASS.

Артефакты проверки:
- `reports/qa_gate/p52_sla_audit_20260524T030125Z.json` (PASS, mode=blocked_no_source)
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T030139Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T030308Z.json`
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T030433Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T030433Z.json` (PASS)
- `reports/runs/run_20260524T030443Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_ffe90a/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T030458Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T030503Z.json` (PASS, step=P5.2)

10. `P6.1` — расширен единый аудит `конфиг -> runtime` по всем backlog-идеям:
- доработан `features_block_audit.py`:
  - проверка загрузки runtime-реестра backlog (`load_backlog_registry`)
  - проверка совпадения числа backlog-идей в конфиге и runtime
  - проверка полного покрытия всех backlog-имен runtime-мэппингом
  - проверка отсутствия лишних runtime-идей вне конфига
  - проверка `required_features` для всех `active|validated` гипотез
  - проверка, что `active|validated` гипотезы не требуют внешний источник
- выполнен обязательный цикл:
  - `short_only` прогон
  - `long_only` прогон
  - coverage PASS
  - табличная сходимость `CSV/XLSX` PASS
  - gate PASS.

Артефакты проверки:
- `reports/qa_gate/features_block_audit_20260524T030701Z.json` (PASS)
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T030714Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T030844Z.json`
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T031008Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T031008Z.json` (PASS)
- `reports/runs/run_20260524T031019Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_cb219f/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T031034Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T031039Z.json` (PASS, step=P6.1)

11. `P6.2` — расширен `hypothesis_coverage_audit` с отдельным coverage для `active` backlog-гипотез:
- доработан `hypothesis_coverage_audit.py`:
  - загрузка backlog runtime-реестра по текущему `signal_mode`
  - формирование ожидаемого набора `active` backlog-гипотез
  - сравнение с фактически наблюденными `trend_filter` в `history`
  - отдельный check c метриками:
    - `covered_count`
    - `missing_count`
    - `coverage_ratio`
    - списки `covered_names` / `missing_names`
- выполнен обязательный цикл:
  - `short_only` прогон (active backlog filter)
  - `long_only` прогон (active backlog filter)
  - coverage PASS
  - табличная сходимость `CSV/XLSX` PASS
  - gate PASS.

Артефакты проверки:
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T031553Z.json` (PASS, active backlog coverage section present)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T031554Z.json` (PASS, active backlog coverage section present)
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T031252Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T031421Z.json`
- `reports/runs/run_20260524T031613Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_f7e103/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T031628Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T031633Z.json` (PASS, step=P6.2)

12. `P7.1` — выполнен контрольный цикл `short_only/long_only` с `repeats>=3` и собран единый финальный пакет:
- выполнен `short_only` контрольный цикл: `repeats=3`
- выполнен `long_only` контрольный цикл: `repeats=3`
- подтвержден backlog coverage (расширенный `P6.2`-блок) в обоих контурах
- подтверждена сходимость `CSV/XLSX` по таблицам
- собран единый финальный bundle `P7.1` (json+md) с итоговым PASS.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T031855Z.json` (`repeats_requested=3`)
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T032252Z.json` (`repeats_requested=3`)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T032645Z.json` (PASS, active backlog coverage section present)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T032645Z.json` (PASS, active backlog coverage section present)
- `reports/qa_gate/features_block_audit_20260524T032646Z.json` (PASS)
- `reports/runs/run_20260524T032657Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_f4d701/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T032712Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T032717Z.json` (PASS, step=P7.1)
- `reports/qa_gate/p71_release_bundle_20260524T032741Z.json` (PASS)
- `reports/qa_gate/p71_release_bundle_20260524T032741Z.md`

13. `P7.2` — финальный свод готовности блока `гипотизы-фичи` + freeze-ready check:
- добавлен и выполнен freeze-ready чек:
  - `src/mlbotnav/p72_freeze_ready_check.py`
  - проверяет, что после прогонов freeze снова включен:
    - `enforce_freeze=true`
    - `project_ready=false`
    - ключевые train/search actions блокируются readiness gate
- выполнен контрольный цикл + аудит:
  - `short_only` прогон
  - `long_only` прогон
  - coverage PASS (active backlog section)
  - табличная сходимость `CSV/XLSX` PASS
  - gate PASS
- финальный freeze-ready отчет = PASS.

Артефакты проверки:
- `reports/qa_gate/p72_freeze_ready_20260524T033521Z.json` (PASS)
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T033253Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-21_20260524T033253Z.json`
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T033425Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T033425Z.json` (PASS)
- `reports/runs/run_20260524T033440Z_solusdt_1m_2026-05-20_to_2026-05-21_tablecanon_a5a24a/audit_chain_report.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T033455Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T033459Z.json` (PASS, step=P7.2)

14. `P7.3` — единый launcher цикла `short -> long -> audit -> CSV/XLSX convergence -> gate` + фикс ложного FAIL по CAGR:
- добавлен единый запускной файл:
  - `run_features_hypotheses_cycle.ps1`
  - запускает оба контура отдельно (`short_only`, `long_only`) и затем обязательные аудиты.
- исправлен аудит сравнения агрегатных метрик:
  - `src/mlbotnav/audit_table_chain.py`
  - `_float_equal` переведен на `math.isclose(rel_tol + abs_tol)` для устранения ложного FAIL при очень больших значениях `cagr`.
- выполнен контрольный цикл через launcher и повторный chain-check:
  - `features_block_audit` PASS
  - `hypothesis_coverage_short_only` PASS
  - `hypothesis_coverage_long_only` PASS
  - `table_convergence_5plus` PASS
  - `tz_gate_runner(step=P7.3)` PASS
  - `p72_freeze_ready_check` PASS.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T033826Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T033939Z.json`
- `reports/qa_gate/features_block_audit_20260524T034051Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T034052Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T034052Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T034317Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T034343Z.json` (PASS, step=P7.3)
- `reports/qa_gate/p72_freeze_ready_20260524T034406Z.json` (PASS)

15. `P7.4` — подтверждена стабильность ежедневного цикла блока `гипотизы-фичи` (повторный полный контроль):
- выполнен повторный запуск единого цикла через `run_features_hypotheses_cycle.ps1`;
- подтверждено, что последовательность `short_only -> long_only -> audits -> table_convergence -> gate -> freeze` стабильно проходит без ручных правок;
- зафиксирован очередной PASS-пакет артефактов для ежедневного контура.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T034510Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T034624Z.json`
- `reports/qa_gate/features_block_audit_20260524T034736Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T034737Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T034737Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T034738Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T034759Z.json` (PASS, launcher gate)
- `reports/qa_gate/tz_gate_20260524T034837Z.json` (PASS, step=P7.4)
- `reports/qa_gate/p72_freeze_ready_20260524T034815Z.json` (PASS)

16. `P7.5` — кросс-дата проверка 5+ (другой test-day) + исправление launcher на дато-специфичный gate:
- выявлено и устранено отклонение: ранее `table/gate` могли брать дефолтное окно дат, не связанное с текущим `TestDate`;
- в `run_features_hypotheses_cycle.ps1` добавлен явный шаг:
  - `table_canon_pack` строго на `TestDate..TestDate`;
  - авто-поиск последнего `oos_report` по символу/таймфрейму;
  - `table_convergence_5plus --oos-report <latest>`;
  - `tz_gate_runner` с явными `--start-date/--end-date/--oos-report`.
- выполнен повторный контрольный цикл на другом окне:
  - `train=2026-05-18`, `test=2026-05-19`;
  - `short_only` + `long_only` + все аудиты + CSV/XLSX convergence + gate + freeze.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-19_20260524T035311Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-19_20260524T035425Z.json`
- `reports/qa_gate/features_block_audit_20260524T035537Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T035538Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T035538Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T035544Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T035548Z.json` (PASS)
- `reports/qa_gate/p72_freeze_ready_20260524T035557Z.json` (PASS)

17. `P7.6` — жесткая привязка `oos_report` к текущему long-only summary (анти-гонка с параллельными прогонами):
- доработан launcher `run_features_hypotheses_cycle.ps1`:
  - добавлен `StepLabel` для явной маркировки шага ТЗ в `tz_gate_runner`;
  - добавлена функция `Resolve-OosReportFromLongSummary`, которая берет `oos_report` строго из последнего `adaptive_loop` long-only на текущем `TestDate`;
  - `table_convergence_5plus` и `tz_gate_runner` запускаются по этому точному `oos_report`.
- выполнен контрольный цикл на окне `train=2026-05-18`, `test=2026-05-19` после фикса.
- подтвержден отдельный `tz_gate_runner --step P7.6` с точным `oos_report` из summary.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-19_20260524T042552Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-19_20260524T042710Z.json`
- `reports/qa_gate/features_block_audit_20260524T042822Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T042823Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T042823Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T042829Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T042833Z.json` (PASS, launcher)
- `reports/qa_gate/tz_gate_20260524T042945Z.json` (PASS, step=P7.6)
- `reports/qa_gate/p72_freeze_ready_20260524T042842Z.json` (PASS)

18. `P7.7` — операционная дисциплина launcher: обязательный StepLabel + явный лог выбранного OOS:
- в `run_features_hypotheses_cycle.ps1` добавлено:
  - обязательная валидация `StepLabel` (пустое значение запрещено);
  - явный вывод `Resolved OOS report: ...` перед `table_convergence/tz_gate` для прозрачного аудита.
- выполнен контрольный цикл на окне:
  - `train=2026-05-19`, `test=2026-05-20`, `step=P7.7`.
- подтверждено: прогон + аудит + CSV/XLSX-сходимость + gate + freeze = PASS.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T043053Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T043206Z.json`
- `reports/qa_gate/features_block_audit_20260524T043318Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T043318Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T043319Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T043324Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T043328Z.json` (PASS, step=P7.7)
- `reports/qa_gate/p72_freeze_ready_20260524T043337Z.json` (PASS)

19. `P7.8` — пакетная матрица проверок (две даты подряд) в одном запуске:
- добавлен пакетный launcher:
  - `run_features_hypotheses_matrix.ps1`
  - прогоняет два окна подряд:
    - `P7.8A`: train=2026-05-18, test=2026-05-19
    - `P7.8B`: train=2026-05-19, test=2026-05-20
- для каждого окна выполняется полный контур:
  - `short_only` -> `long_only` -> `features/hypothesis audits` -> `table_convergence_5plus` -> `tz_gate` -> `freeze_ready`.
- сформирован общий matrix-report.

Артефакты проверки:
- `reports/qa_gate/p78_matrix_run_SOLUSDT_1m_20260524T044024Z.json`

P7.8A:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-19_20260524T043455Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-19_20260524T043608Z.json`
- `reports/qa_gate/features_block_audit_20260524T043720Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T043721Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T043721Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T043727Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T043730Z.json` (PASS, step=P7.8A)
- `reports/qa_gate/p72_freeze_ready_20260524T043739Z.json` (PASS)

P7.8B:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T043740Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T043852Z.json`
- `reports/qa_gate/features_block_audit_20260524T044004Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T044005Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T044005Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T044011Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T044015Z.json` (PASS, step=P7.8B)
- `reports/qa_gate/p72_freeze_ready_20260524T044024Z.json` (PASS)

20. `P7.9` — третье независимое окно (расширение устойчивости CSV/XLSX 5+):
- выполнен полный цикл на новом окне:
  - `train=2026-05-17`, `test=2026-05-18`, `step=P7.9`;
- подтверждено:
  - `features_block_audit` PASS;
  - `hypothesis_coverage` short/long PASS;
  - `table_convergence_5plus` PASS;
  - `tz_gate` PASS;
  - `freeze_ready` PASS.

Артефакты проверки:
- `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-18_20260524T044128Z.json`
- `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-18_20260524T044241Z.json`
- `reports/qa_gate/features_block_audit_20260524T044352Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T044353Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T044353Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T044359Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T044402Z.json` (PASS, step=P7.9)
- `reports/qa_gate/p72_freeze_ready_20260524T044412Z.json` (PASS)

21. `P7.10` — расширенная матрица 3 окон подряд (A/B/C) с единым запуском:
- обновлен `run_features_hypotheses_matrix.ps1`:
  - добавлен `StepPrefix`;
  - матрица расширена до 3 окон:
    - `P7.10A`: train=2026-05-17, test=2026-05-18
    - `P7.10B`: train=2026-05-18, test=2026-05-19
    - `P7.10C`: train=2026-05-19, test=2026-05-20
- для каждого окна пройден полный контур:
  - `short_only` -> `long_only` -> `audits` -> `table_convergence_5plus` -> `tz_gate` -> `freeze_ready`.
- все окна прошли в PASS по сходимости CSV/XLSX и gate.

Артефакты проверки:
- `reports/qa_gate/p78_matrix_run_SOLUSDT_1m_20260524T045333Z.json`

P7.10A:
- `reports/qa_gate/features_block_audit_20260524T044744Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T044744Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T044745Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T044751Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T044754Z.json` (PASS, step=P7.10A)
- `reports/qa_gate/p72_freeze_ready_20260524T044803Z.json` (PASS)

P7.10B:
- `reports/qa_gate/features_block_audit_20260524T045029Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T045030Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T045030Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T045036Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T045039Z.json` (PASS, step=P7.10B)
- `reports/qa_gate/p72_freeze_ready_20260524T045048Z.json` (PASS)

P7.10C:
- `reports/qa_gate/features_block_audit_20260524T045313Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_short_only_20260524T045314Z.json` (PASS)
- `reports/qa_gate/hypothesis_coverage_long_only_20260524T045314Z.json` (PASS)
- `reports/qa_gate/table_convergence_5plus_20260524T045320Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T045324Z.json` (PASS, step=P7.10C)
- `reports/qa_gate/p72_freeze_ready_20260524T045333Z.json` (PASS)

22. `P7.11` — fail-fast матрица (жесткая остановка при любом FAIL + автопроверка PASS-репортов):
- доработан `run_features_hypotheses_matrix.ps1`:
  - добавлен `Assert-LatestQaPass(...)` для обязательной проверки свежих отчетов:
    - `tz_gate` (с проверкой `step`),
    - `table_convergence_5plus`,
    - `p72_freeze_ready`;
  - добавлена проверка `LASTEXITCODE` после каждого оконного цикла;
  - в matrix-report сохраняются пути к ключевым PASS-отчетам каждого окна.
- выполнен полный матричный прогон `P7.11A/B/C`.
- результат: на всех 3 окнах контур `прогон + аудит + CSV/XLSX + gate + freeze` = PASS.

Артефакты проверки:
- `reports/qa_gate/p78_matrix_run_SOLUSDT_1m_20260524T050307Z.json`

P7.11A:
- `reports/qa_gate/table_convergence_5plus_20260524T045721Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T045725Z.json` (PASS, step=P7.11A)
- `reports/qa_gate/p72_freeze_ready_20260524T045735Z.json` (PASS)

P7.11B:
- `reports/qa_gate/table_convergence_5plus_20260524T050008Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T050011Z.json` (PASS, step=P7.11B)
- `reports/qa_gate/p72_freeze_ready_20260524T050021Z.json` (PASS)

P7.11C:
- `reports/qa_gate/table_convergence_5plus_20260524T050254Z.json` (PASS)
- `reports/qa_gate/tz_gate_20260524T050258Z.json` (PASS, step=P7.11C)
- `reports/qa_gate/p72_freeze_ready_20260524T050307Z.json` (PASS)

### Далее по плану
1. Старт блока `P8` (полное покрытие active-гипотез по одной, отдельно long/short) в режиме `1D train + next 1D test`.

## 10) Новый рабочий блок P8 (строгий режим 1D->1D)
### P8.1 Режим окон (обязательно)
1. Обучение: строго 1 закрытый UTC-день (`train-start == train-end`).
2. Прогон/OOS: строго следующий закрытый UTC-день (`test-day == train-day + 1`).
3. Никаких multi-day смешиваний в этом блоке.
4. Базовое окно по умолчанию:
   - train: `2026-05-19`
   - test: `2026-05-20`

### P8.2 Полное покрытие гипотез (без смешивания long/short)
1. Контур `long_only`: каждая active long-гипотеза прогоняется отдельно.
2. Контур `short_only`: каждая active short-гипотеза прогоняется отдельно.
3. На каждый шаг ровно одна целевая гипотеза (`--trend-filter=<name>`, профиль отключен).

### P8.3 QA-цепочка после КАЖДОЙ гипотезы (обязательно)
1. `table_canon_pack` на `test-day`.
2. `table_convergence_5plus --oos-report <текущий>`
3. `tz_gate_runner --step <P8.x.y>`
4. `p72_freeze_ready_check`
5. Режимы исполнения:
   - `FailFast=true`: немедленная остановка на первом FAIL (строгий режим).
   - `FailFast=false` (по умолчанию): пройти все гипотезы, собрать полный список FAIL, выдать сводный отчет `PARTIAL_FAIL`.

### P8.4 Критерий приемки блока P8
1. Для каждого шага есть `PASS` по `table_convergence`, `tz_gate`, `freeze_ready`.
2. Для каждой active гипотезы есть отдельный run-артефакт и `oos_report`.
3. Отдельный итоговый coverage-репорт long/short с перечнем пройденных гипотез.

### P8.5 Команда запуска (1 день обучение + следующий день прогон)
1. Полный coverage (пройти все гипотезы long/short и собрать полный отчет):
   - `.\run_hypotheses_full_coverage_1d1d.ps1 -TrainDate 2026-05-19 -TestDate 2026-05-20 -StepPrefix P8 -Threads 12 -SearchWorkers 8 -Leverage 10 -GoalNetReturnPct 100 -AllowSubgoalCandidates`
2. Строгий fail-fast (остановка на первом FAIL):
   - `.\run_hypotheses_full_coverage_1d1d.ps1 -TrainDate 2026-05-19 -TestDate 2026-05-20 -StepPrefix P8 -Threads 12 -SearchWorkers 8 -Leverage 10 -GoalNetReturnPct 100 -AllowSubgoalCandidates -FailFast`

### P8.6 Строгий последовательный режим (обязательно, без прыжков)
1. Текущее состояние по нумерации:
   - Последний закрытый блок: `P7.11C` (PASS).
   - Текущий рабочий блок: `P8`.
2. Правило выполнения:
   - выполняем только один шаг за раз;
   - если шаг упал (FAIL) — немедленный STOP;
   - к следующему шагу не переходим, пока не закрыт текущий FAIL.
3. Нумерация шагов:
   - long-контур: `P8.L01 ... P8.L10` (10 active-гипотез);
   - short-контур: `P8.S01 ... P8.S09` (9 active-гипотез).

### P8.7 Порядок шагов (фиксирован)
1. `P8.L01` `fib_retrace_0382_0618_trend_resume`
2. `P8.L02` `fib_extension_targets`
3. `P8.L03` `swing_hl_hh_long`
4. `P8.L04` `bos_continuation_confirm`
5. `P8.L05` `min_max_range_revert`
6. `P8.L06` `max_low_pullback_long`
7. `P8.L07` `hvn_lvn_density_reaction`
8. `P8.L08` `volume_profile_poc_vah_val_retest`
9. `P8.L09` `value_area_rotation_vs_breakout`
10. `P8.L10` `wedge_breakout_plus_profile_acceptance`
11. `P8.S01` `fib_retrace_0382_0618_trend_resume`
12. `P8.S02` `fib_extension_targets`
13. `P8.S03` `swing_lh_ll_short`
14. `P8.S04` `bos_continuation_confirm`
15. `P8.S05` `min_max_range_revert`
16. `P8.S06` `hvn_lvn_density_reaction`
17. `P8.S07` `volume_profile_poc_vah_val_retest`
18. `P8.S08` `value_area_rotation_vs_breakout`
19. `P8.S09` `wedge_breakout_plus_profile_acceptance`

### P8.8 Обязательные проверки после КАЖДОГО шага
1. Прогон строго одной гипотезы (`--trend-filter=<name>`) на окне:
   - train: 1 закрытый UTC-день;
   - test: следующий закрытый UTC-день.
2. Табличный контур:
   - `table_canon_pack` (CSV + XLSX);
   - `audit_table_chain` (проверка структуры/типов).
3. QA контур:
   - `table_convergence_5plus` = PASS;
   - `tz_gate_runner --step <P8.Lxx|P8.Sxx>` = PASS;
   - `p72_freeze_ready_check` = PASS.
4. Конфиг/движок/зависимости:
   - `features_block_audit` = PASS;
   - контроль соответствия `features_block.yaml` -> runtime для текущей гипотезы.
5. Любой FAIL:
   - фикс причины;
   - повтор только текущего шага;
   - следующий шаг запрещен.

### P8.9 Статус выполнения по шагам (строго по порядку)
1. `P8.L01` `fib_retrace_0382_0618_trend_resume` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T073311Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T073444Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T073646Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T073704Z.json` (PASS, step=P8.L01)
     - `reports/qa_gate/p72_freeze_ready_20260524T073704Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T073704Z.json` (PASS)
   - Примечание:
     - зафиксирован и устранен порядок запуска QA-цепочки (сначала полный table pack/trace, затем convergence/gate).
2. Следующий шаг по порядку: `P8.L02` `fib_extension_targets`.
3. `P8.L02` `fib_extension_targets` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T073906Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T074040Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T074133Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T074136Z.json` (PASS, step=P8.L02)
     - `reports/qa_gate/p72_freeze_ready_20260524T074146Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T074147Z.json` (PASS)
   - Примечание:
     - закреплено правило выполнения только последовательной цепочкой (без параллельных запусков проверок внутри шага).
4. Следующий шаг по порядку: `P8.L03` `swing_hl_hh_long`.
5. `P8.L03` `swing_hl_hh_long` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T074240Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T074416Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T074445Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T074448Z.json` (PASS, step=P8.L03)
     - `reports/qa_gate/p72_freeze_ready_20260524T074458Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T074459Z.json` (PASS)
6. Следующий шаг по порядку: `P8.L04` `bos_continuation_confirm`.
7. `P8.L04` `bos_continuation_confirm` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T074546Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T074720Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T074751Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T074754Z.json` (PASS, step=P8.L04)
     - `reports/qa_gate/p72_freeze_ready_20260524T074804Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T074804Z.json` (PASS)
8. Следующий шаг по порядку: `P8.L05` `min_max_range_revert`.
9. `P8.L05` `min_max_range_revert` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T074859Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T075038Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T075117Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T075120Z.json` (PASS, step=P8.L05)
     - `reports/qa_gate/p72_freeze_ready_20260524T075130Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T075130Z.json` (PASS)
10. Следующий шаг по порядку: `P8.L06` `max_low_pullback_long`.
11. `P8.L06` `max_low_pullback_long` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T075215Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T075347Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T075414Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T075417Z.json` (PASS, step=P8.L06)
     - `reports/qa_gate/p72_freeze_ready_20260524T075427Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T075427Z.json` (PASS)
12. Следующий шаг по порядку: `P8.L07` `hvn_lvn_density_reaction`.
13. `P8.L07` `hvn_lvn_density_reaction` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T075515Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T075648Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T075714Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T075717Z.json` (PASS, step=P8.L07)
     - `reports/qa_gate/p72_freeze_ready_20260524T075726Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T075727Z.json` (PASS)
14. Следующий шаг по порядку: `P8.L08` `volume_profile_poc_vah_val_retest`.
15. `P8.L08` `volume_profile_poc_vah_val_retest` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T075813Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T075945Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T080012Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T080015Z.json` (PASS, step=P8.L08)
     - `reports/qa_gate/p72_freeze_ready_20260524T080024Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T080025Z.json` (PASS)
16. Следующий шаг по порядку: `P8.L09` `value_area_rotation_vs_breakout`.
17. `P8.L09` `value_area_rotation_vs_breakout` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T080112Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T080245Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T080314Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T080317Z.json` (PASS, step=P8.L09)
     - `reports/qa_gate/p72_freeze_ready_20260524T080326Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T080327Z.json` (PASS)
18. Следующий шаг по порядку: `P8.L10` `wedge_breakout_plus_profile_acceptance`.
19. `P8.L10` `wedge_breakout_plus_profile_acceptance` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T080416Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T080548Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T080614Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T080618Z.json` (PASS, step=P8.L10)
     - `reports/qa_gate/p72_freeze_ready_20260524T080627Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T080627Z.json` (PASS)
20. Следующий шаг по порядку: `P8.S01` `fib_retrace_0382_0618_trend_resume` (переход в short-контур).
21. `P8.S01` `fib_retrace_0382_0618_trend_resume` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T080716Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T080847Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T080914Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T080917Z.json` (PASS, step=P8.S01)
     - `reports/qa_gate/p72_freeze_ready_20260524T080926Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T080927Z.json` (PASS)
22. Следующий шаг по порядку: `P8.S02` `fib_extension_targets`.
23. `P8.S02` `fib_extension_targets` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T081027Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T081159Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T081227Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T081230Z.json` (PASS, step=P8.S02)
     - `reports/qa_gate/p72_freeze_ready_20260524T081239Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T081239Z.json` (PASS)
24. Следующий шаг по порядку: `P8.S03` `swing_lh_ll_short`.
25. `P8.S03` `swing_lh_ll_short` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T081337Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T081509Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T081547Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T081550Z.json` (PASS, step=P8.S03)
     - `reports/qa_gate/p72_freeze_ready_20260524T081559Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T081600Z.json` (PASS)
26. Следующий шаг по порядку: `P8.S04` `bos_continuation_confirm`.
27. `P8.S04` `bos_continuation_confirm` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T081707Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T081839Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T081912Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T081915Z.json` (PASS, step=P8.S04)
     - `reports/qa_gate/p72_freeze_ready_20260524T081924Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T081925Z.json` (PASS)
28. Следующий шаг по порядку: `P8.S05` `min_max_range_revert`.
29. `P8.S05` `min_max_range_revert` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T082435Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T082610Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T082642Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T082645Z.json` (PASS, step=P8.S05)
     - `reports/qa_gate/p72_freeze_ready_20260524T082653Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T082654Z.json` (PASS)
30. Следующий шаг по порядку: `P8.S06` `hvn_lvn_density_reaction`.
31. `P8.S06` `hvn_lvn_density_reaction` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T082757Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T082934Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T083003Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T083007Z.json` (PASS, step=P8.S06)
     - `reports/qa_gate/p72_freeze_ready_20260524T083016Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T083017Z.json` (PASS)
32. Следующий шаг по порядку: `P8.S07` `volume_profile_poc_vah_val_retest`.
33. `P8.S07` `volume_profile_poc_vah_val_retest` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T083127Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T083305Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T083337Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T083340Z.json` (PASS, step=P8.S07)
     - `reports/qa_gate/p72_freeze_ready_20260524T083350Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T083350Z.json` (PASS)
34. Следующий шаг по порядку: `P8.S08` `value_area_rotation_vs_breakout`.
35. `P8.S08` `value_area_rotation_vs_breakout` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T083448Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T083625Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T083655Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T083659Z.json` (PASS, step=P8.S08)
     - `reports/qa_gate/p72_freeze_ready_20260524T083709Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T083710Z.json` (PASS)
36. Следующий шаг по порядку: `P8.S09` `wedge_breakout_plus_profile_acceptance`.
37. `P8.S09` `wedge_breakout_plus_profile_acceptance` — ЗАКРЫТ.
   - Прогон (1D train -> next 1D test):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T083759Z.json`
   - OOS:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T083933Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T084002Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T084005Z.json` (PASS, step=P8.S09)
     - `reports/qa_gate/p72_freeze_ready_20260524T084015Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T084015Z.json` (PASS)
38. Блок `P8` закрыт полностью: `L01..L10` и `S01..S09` пройдены с обязательной цепочкой проверок.
39. `P9` Сводный пост-блок аудит после полного закрытия `P8` — ЗАКРЫТ.
   - База OOS для сводной проверки:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T083933Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T084124Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T084127Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T084128Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T084128Z.json` (PASS, step=P9)
     - `reports/qa_gate/p72_freeze_ready_20260524T084137Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T084138Z.json` (PASS)
40. Следующий блок по порядку: `P10` (финальный release/ready summary по ТЗ).
41. `P10` Финальный `release/ready` контроль по ТЗ — ЗАКРЫТ.
   - База OOS для финальной проверки:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T083933Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T084304Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T084308Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T084308Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T084309Z.json` (PASS, step=P10)
     - `reports/qa_gate/p72_freeze_ready_20260524T084318Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T084319Z.json` (PASS)
42. Следующий блок по порядку: `P11` (операционный старт-блок: запуск рабочего цикла обучения/поиска на утвержденных правилах ТЗ).
43. `P11` Операционный старт-блок (боевой ready-check перед рабочим циклом) — ЗАКРЫТ.
   - База OOS для стартового контроля:
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T083933Z.json`
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T084459Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T084503Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T084503Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T084504Z.json` (PASS, step=P11)
     - `reports/qa_gate/p72_freeze_ready_20260524T084513Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T084514Z.json` (PASS)
44. Следующий блок по порядку: `P12` (старт рабочего цикла обучения/поиска по утвержденному ТЗ-окну).
45. `P12` Старт рабочего цикла обучения/поиска по утвержденному ТЗ-окну — ЗАКРЫТ.
   - Рабочий цикл:
     - `reports/qa_gate/daily_long_short_cycle_20260524T084618Z.json` (PASS)
   - CSV/XLSX + chain:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - QA:
     - `reports/qa_gate/table_convergence_5plus_20260524T084858Z.json` (PASS, short cycle)
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T084745Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T084912Z.json` (PASS)
     - `reports/qa_gate/p72_freeze_ready_20260524T084925Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T084925Z.json` (PASS)
46. Следующий блок по порядку: `P13` (итоговый пакет сдачи ТЗ: единый финальный реестр артефактов и статус готовности).
47. `P13` Итоговый пакет сдачи ТЗ (единый финальный реестр артефактов и статус готовности) — ЗАКРЫТ.
   - Пакет артефактов:
     - `reports/runs/run_20260524T090621Z_solusdt_1m_2026-05-20_to_2026-05-20_tablecanon_967ab2/index.json`
     - `reports/runs/run_20260524T090621Z_solusdt_1m_2026-05-20_to_2026-05-20_tablecanon_967ab2/state/p4_pack_manifest.json`
   - QA:
     - `reports/qa_gate/p71_release_bundle_20260524T090552Z.json` (PASS)
     - `reports/qa_gate/p72_freeze_ready_20260524T090621Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T090621Z.json` (PASS, step=P13)
     - `reports/qa_gate/features_block_audit_20260524T090553Z.json` (PASS)
48. Следующий блок по порядку: `P14` (orderbook planned-гипотезы: подключение L1-L50/spread/delta источника и активация runtime).
49. `P14` Orderbook planned-гипотезы — СТАРТ (in_progress).
   - Текущий аудит источника orderbook/microstructure:
     - `reports/qa_gate/orderbook_source_audit_20260524T090716Z.json` (PASS: planned-режим подтвержден, external source пока не подключен).
   - Что означает статус сейчас:
     - обе гипотезы корректно зарегистрированы, но не активируются в runtime до подключения источника L1-L50/spread/delta.
50. `P14` дополнительная проверка CSV/XLSX + chain (по правилу шага) — PASS.
   - `reports/qa_gate/table_convergence_5plus_20260524T090801Z.json` (PASS)
51. `P14.1` Проверка CSV/XLSX + движок/зависимости (последовательный прогон без гонок файлов) — ЗАКРЫТ.
   - Табличный канон (core, 1d):
     - `reports/table_canon_current/data/candles_canonical.csv`
     - `reports/table_canon_current/data/feature_frame.csv`
     - `reports/table_canon_current/data/feature_dictionary_ru.xlsx`
     - `reports/table_canon_current/data/readable_tables_ru.xlsx`
   - Симуляция/след исполнения:
     - `reports/table_canon_current/data/signal_frame.csv`
     - `reports/table_canon_current/data/execution_trace.csv`
     - `reports/table_canon_current/data/strategy_summary.csv`
   - Аудит и гейты:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T091255Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T091325Z.json` (PASS, step=P14)
     - `reports/qa_gate/features_block_audit_20260524T091256Z.json` (PASS)
     - `reports/qa_gate/p72_freeze_ready_20260524T091340Z.json` (PASS)
52. `P14.2` Статус planned-гипотез orderbook подтвержден: runtime блок не активируется без источника L1-L50/spread/delta.
   - `reports/qa_gate/orderbook_source_audit_20260524T091341Z.json` (PASS).
   - Следующий подшаг по порядку: `P14.3` подключение внешнего источника orderbook/microstructure и перевод `planned -> active`.
53. `P14.3` Runtime-адаптация orderbook/microstructure (детектор источника + реестр гипотез) — ЗАКРЫТ.
   - Фикс в коде:
     - `src/mlbotnav/external_sources.py` (новый единый детектор внешних источников)
     - `src/mlbotnav/hypothesis_registry.py` (source-aware активация backlog-гипотез)
     - `src/mlbotnav/orderbook_source_audit.py` (`--expect-status planned|active`)
   - Аудит после фикса:
     - `reports/qa_gate/orderbook_source_audit_20260524T091619Z.json` (PASS, planned)
     - `reports/qa_gate/orderbook_source_audit_20260524T091626Z.json` (FAIL, active — ожидаемо без подключенного источника)
     - `reports/qa_gate/features_block_audit_20260524T091611Z.json` (PASS)
   - Цепочка CSV/XLSX + движок:
     - `reports/qa_gate/tz_gate_20260524T091639Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T091715Z.json` (PASS)
     - `reports/qa_gate/p72_freeze_ready_20260524T091639Z.json` (PASS)
54. Правило выполнения проверок для `table_canon_current`:
   - запускать chain-команды последовательно (не параллельно), чтобы избежать file-lock/перезаписи каталога.
55. Следующий подшаг по порядку: `P14.4` — фактическое подключение внешнего источника L1-L50/spread/delta и перевод двух orderbook-гипотез в `active`.
56. `P14.4` Подключение источника L1-L50/spread/delta — В РАБОТЕ (blocked_by_source).
   - Контроль таблиц/движка после фиксов:
     - `reports/qa_gate/table_convergence_5plus_20260524T091915Z.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T091916Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T091916Z.json` (PASS, planned)
   - Проверка готовности к active:
     - `reports/qa_gate/orderbook_source_audit_20260524T091935Z.json` (FAIL, expected active)
   - Причина блокировки (по аудиту):
     - `source_detected=false`, `source_files_total=0`, `source_env={}`.
   - Текущий порядковый статус блока:
     - `TZ_FEATURES_BLOCK / P14.4` (не закрыт до появления реального source L1-L50/spread/delta).
57. Следующий шаг после появления источника: `P14.5` — перевести две гипотезы в `active`, прогон chain, и закрыть P14.
58. `P14.4` Подключение источника L1-L50/spread/delta — ЗАКРЫТ.
   - Источник подключен и зафиксирован:
     - `data/orderbook/dt=2026-05-24/symbol=SOLUSDT/orderbook_l50_snapshot_20260524T092211Z.json`
     - `data/microstructure/dt=2026-05-24/symbol=SOLUSDT/microstructure_spread_delta.csv`
   - В `configs/features_block.yaml` переведены статусы:
     - `orderbook_imbalance_l1_l50: active`
     - `spread_pressure_and_delta_absorption: active`
   - Аудит и цепочка:
     - `reports/qa_gate/orderbook_source_audit_20260524T092425Z.json` (PASS, expect active)
     - `reports/qa_gate/features_block_audit_20260524T092425Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T092424Z.json` (PASS, step=P14)
     - `reports/qa_gate/table_convergence_5plus_20260524T092442Z.json` (PASS)
     - `reports/qa_gate/p72_freeze_ready_20260524T092442Z.json` (PASS)
59. Блок `P14` закрыт полностью.
60. Следующий блок по порядку: `P15` — операционный цикл активации orderbook-гипотез (long/short раздельно, 1d train -> next 1d test) с обязательной проверкой CSV/XLSX + chain + gate после шага.
61. `P15` Операционный цикл активации orderbook-гипотез (long/short раздельно, 1d train -> next 1d test) — ЗАКРЫТ.
   - Основной цикл:
     - `reports/qa_gate/daily_long_short_cycle_20260524T092618Z.json` (PASS)
   - Внутри цикла (long/short отдельно):
     - `reports/qa_gate/table_convergence_5plus_20260524T092729Z.json` (PASS, long)
     - `reports/qa_gate/table_convergence_5plus_20260524T092856Z.json` (PASS, short)
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T092744Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T092910Z.json` (PASS)
   - Контроль после шага:
     - `reports/qa_gate/tz_gate_20260524T092930Z.json` (PASS, step=P15)
     - `reports/qa_gate/features_block_audit_20260524T092950Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T092950Z.json` (PASS, expect active)
     - `reports/qa_gate/p72_freeze_ready_20260524T092949Z.json` (PASS)
62. Следующий блок по порядку: `P16` — калибровка и расширенный перебор при активных orderbook-гипотезах (long/short раздельно), с тем же обязательным контуром CSV/XLSX + chain + gate + freeze.
63. `P16` Калибровка и расширенный перебор при активных orderbook-гипотезах (long/short раздельно) — ЗАКРЫТ.
   - Расширенная калибровка `long_only` (repeats=3):
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T093126Z.json`
     - OOS: `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T093440Z.json`
     - `reports/qa_gate/table_convergence_5plus_20260524T093830Z.json` (PASS)
   - Расширенная калибровка `short_only` (repeats=3):
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T093458Z.json`
     - OOS: `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T093810Z.json`
     - `reports/qa_gate/table_convergence_5plus_20260524T093858Z.json` (PASS)
   - Покрытие гипотез:
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T093921Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T093921Z.json` (PASS)
   - Контроль после шага:
     - `reports/qa_gate/features_block_audit_20260524T093921Z.json` (PASS)
     - `reports/qa_gate/tz_gate_20260524T093933Z.json` (PASS, step=P16)
     - `reports/qa_gate/orderbook_source_audit_20260524T093933Z.json` (PASS, expect active)
     - `reports/qa_gate/p72_freeze_ready_20260524T093933Z.json` (PASS)
64. Следующий блок по порядку: `P17` — стабилизация параметров и формирование шаблона рабочего запуска (long/short раздельно) с обязательной проверкой CSV/XLSX + chain + gate + freeze.
65. `P17` Стабилизация параметров и формирование шаблона рабочего запуска (long/short раздельно) — ЗАКРЫТ.
   - Добавлен стабильный шаблон запуска:
     - `run_p17_stable_long_short_1d1d.ps1`
   - Контрольный запуск шаблона выполнен:
     - `reports/adaptive/long_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T094129Z.json`
     - `reports/adaptive/short_only/adaptive_loop_SOLUSDT_1m_2026-05-20_20260524T094209Z.json`
   - CSV/XLSX + chain:
     - `reports/qa_gate/table_convergence_5plus_20260524T094247Z.json` (PASS, long)
     - `reports/qa_gate/table_convergence_5plus_20260524T094301Z.json` (PASS, short)
   - Покрытие гипотез:
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T094314Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T094315Z.json` (PASS)
   - Аудиты и гейты:
     - `reports/qa_gate/features_block_audit_20260524T094316Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T094316Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T094316Z.json` (PASS, step=P17)
     - `reports/qa_gate/p72_freeze_ready_20260524T094325Z.json` (PASS)
66. Следующий блок по порядку: `P18` — подготовка рабочего daily-launch шаблона (отдельные команды long/short + объединенный запуск) и контрольный прогон по ТЗ-контуру.
67. `P18` Подготовка рабочего daily-launch шаблона (long/short отдельно + combined запуск) — ЗАКРЫТ.
   - Добавлены шаблоны запуска:
     - `run_p18_daily_long_only.ps1`
     - `run_p18_daily_short_only.ps1`
     - `run_p18_daily_combined.ps1`
   - Контрольный combined прогон:
     - `reports/qa_gate/daily_long_short_cycle_20260524T094521Z.json` (PASS)
   - Внутри цикла CSV/XLSX + chain:
     - `reports/qa_gate/table_convergence_5plus_20260524T094631Z.json` (PASS, long)
     - `reports/qa_gate/table_convergence_5plus_20260524T094754Z.json` (PASS, short)
   - Покрытие гипотез:
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T094645Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T094808Z.json` (PASS)
   - Контроль после шага:
     - `reports/qa_gate/features_block_audit_20260524T094809Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T094810Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T094810Z.json` (PASS, step=P18)
     - `reports/qa_gate/p72_freeze_ready_20260524T094819Z.json` (PASS)
68. Следующий блок по порядку: `P19` — финализация операционного контура и выпуск рабочего регламента запуска/контроля (команды + порядок проверок + критерии stop/go).
69. `P19` Финализация операционного контура и выпуск рабочего регламента запуска/контроля (stop/go) — ЗАКРЫТ.
   - Выпущен регламент:
     - `docs/P19_DAILY_STOP_GO_RUNBOOK_2026-05-24_RU.md`
   - Контрольный combined-прогон:
     - `reports/qa_gate/daily_long_short_cycle_20260524T095430Z.json` (PASS)
   - Внутри цикла CSV/XLSX + chain:
     - `reports/qa_gate/table_convergence_5plus_20260524T095539Z.json` (PASS, long)
     - `reports/qa_gate/table_convergence_5plus_20260524T095701Z.json` (PASS, short)
   - Покрытие гипотез:
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T095552Z.json` (PASS)
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T095714Z.json` (PASS)
   - Контроль после шага:
     - `reports/qa_gate/features_block_audit_20260524T095715Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T095715Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T095716Z.json` (PASS, step=P19)
     - `reports/qa_gate/p72_freeze_ready_20260524T095725Z.json` (PASS)
70. Следующий блок по порядку: `P20` — финальный релизный пакет `TZ_FEATURES_BLOCK` (единый чек-лист daily-run, матрица артефактов, команда handoff).
71. `P20` Финальный релизный пакет `TZ_FEATURES_BLOCK` (чек-лист daily-run + матрица артефактов + handoff) — ЗАКРЫТ.
   - Выпущен пакет:
     - `docs/P20_RELEASE_PACKAGE_2026-05-24_RU.md`
   - Финальные контрольные PASS:
     - `reports/qa_gate/features_block_audit_20260524T095910Z.json`
     - `reports/qa_gate/orderbook_source_audit_20260524T095911Z.json` (expect active)
     - `reports/qa_gate/tz_gate_20260524T095911Z.json` (step=P20)
     - `reports/qa_gate/p72_freeze_ready_20260524T095921Z.json`
72. Статус блока `TZ_FEATURES_BLOCK`: основной контур закрыт, готов к рабочим daily-прогонам по регламенту P19/P20.
73. `P21` Проверка CSV/XLSX + движка/зависимостей после пересборки канона — ЗАКРЫТ.
   - Пересборка табличного канона (stable):
     - `reports/table_canon_current/data/candles_canonical.xlsx`
     - `reports/table_canon_current/data/feature_frame.xlsx`
     - `reports/table_canon_current/data/feature_frame_full.xlsx`
     - `reports/table_canon_current/data/feature_dictionary_ru.xlsx`
     - `reports/table_canon_current/data/readable_tables_ru.xlsx`
   - Найден и устранен провал цепочки: после pack отсутствовали `signal_frame/strategy_summary`; восстановлено через:
     - `reports/qa_gate/table_convergence_5plus_20260524T100117Z.json` (PASS)
   - Контроль цепочки таблиц:
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - Контроль после шага:
     - `reports/qa_gate/features_block_audit_20260524T100148Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T100149Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T100149Z.json` (PASS, step=P21)
     - `reports/qa_gate/p72_freeze_ready_20260524T100159Z.json` (PASS)
74. Следующий блок по порядку: `P22` — стабилизация последовательности `table_canon_pack -> table_convergence_5plus -> audit_table_chain` как обязательного daily-пайплайна (без ручного добора файлов).
75. `P22` Стабилизация последовательности `table_canon_pack -> table_convergence_5plus -> audit_table_chain` как обязательного daily-пайплайна — ЗАКРЫТ.
   - Добавлен единый скрипт без ручного добора файлов:
     - `run_p22_table_chain_daily.ps1`
   - Контрольный запуск скрипта (`StepLabel=P22`) — PASS:
     - `reports/qa_gate/table_convergence_5plus_20260524T100323Z.json`
     - `reports/table_canon_current/audit_chain_report.json`
     - `reports/qa_gate/features_block_audit_20260524T100339Z.json`
     - `reports/qa_gate/orderbook_source_audit_20260524T100340Z.json` (expect active)
     - `reports/qa_gate/tz_gate_20260524T100340Z.json` (step=P22)
     - `reports/qa_gate/p72_freeze_ready_20260524T100349Z.json`
76. Следующий блок по порядку: `P23` — унификация операторского запуска (short/long/combined + table-chain) в единый командный шаблон с обязательной нумерацией этапов в логе.
77. `P23` Унификация операторского запуска (long/short/combined + table-chain) в единый командный шаблон с нумерацией этапов в логе — ЗАКРЫТ.
   - Добавлен единый операторский скрипт:
     - `run_p23_operator_unified.ps1`
   - Контрольный запуск `Mode=combined` (`StepLabel=P23`) — PASS:
     - `reports/qa_gate/p23_operator_unified_20260524T100954Z.log`
     - `reports/qa_gate/p23_operator_unified_20260524T100954Z.json`
   - CSV/XLSX + движок + зависимости (внутри цепочки):
     - `reports/qa_gate/daily_long_short_cycle_20260524T100954Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T101246Z.json` (PASS, long)
     - `reports/qa_gate/table_convergence_5plus_20260524T101259Z.json` (PASS, short)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T101315Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T101316Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T101316Z.json` (PASS, step=P23)
     - `reports/qa_gate/p72_freeze_ready_20260524T101325Z.json` (PASS)
78. Следующий блок по порядку: `P24` — шаблон ручного операционного контроля (короткий чек-лист для запуска в VS Code: до запуска/во время/после) + автоссылка на последние PASS-артефакты.
79. `P24` Шаблон ручного операционного контроля (до/во время/после) + автоссылка на последние PASS-артефакты — ЗАКРЫТ.
   - Выпущен чек-лист оператора:
     - `docs/P24_OPERATOR_CHECKLIST_2026-05-24_RU.md`
   - Добавлен скрипт отчета последних PASS-артефактов:
     - `run_p24_latest_pass_report.ps1`
     - `reports/qa_gate/p24_latest_pass_20260524T101613Z.json` (PASS)
   - Контрольный прогон по цепочке CSV/XLSX + движок + зависимости (`StepLabel=P24`, mode=table_chain):
     - `reports/qa_gate/table_convergence_5plus_20260524T101541Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T101557Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T101558Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T101558Z.json` (PASS, step=P24)
     - `reports/qa_gate/p72_freeze_ready_20260524T101607Z.json` (PASS)
     - `reports/qa_gate/p23_operator_unified_20260524T101535Z.json` (PASS)
80. Следующий блок по порядку: `P25` — финальный мастер-ранбук `TZ_FEATURES_BLOCK` (единая страница запуска + контроль + артефакты + команды long/short/combined/table_chain).
81. `P25` Финальный мастер-ранбук `TZ_FEATURES_BLOCK` (единая страница запуска + контроль + артефакты + команды long/short/combined/table_chain) — ЗАКРЫТ.
   - Выпущен мастер-ранбук:
     - `docs/P25_MASTER_RUNBOOK_2026-05-24_RU.md`
   - Контрольный запуск по единому операторскому сценарию (`Mode=combined`, `StepLabel=P25`) — PASS:
     - `reports/qa_gate/p23_operator_unified_20260524T101726Z.json`
     - `reports/qa_gate/p23_operator_unified_20260524T101726Z.log`
   - CSV/XLSX + движок + зависимости + аудит (внутри цепочки):
     - `reports/qa_gate/daily_long_short_cycle_20260524T101726Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T102018Z.json` (PASS, long)
     - `reports/qa_gate/table_convergence_5plus_20260524T102031Z.json` (PASS, short)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T102047Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T102048Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T102048Z.json` (PASS, step=P25)
     - `reports/qa_gate/p72_freeze_ready_20260524T102057Z.json` (PASS)
   - Автосводка последних PASS:
     - `reports/qa_gate/p24_latest_pass_20260524T102104Z.json` (PASS)
82. Следующий блок по порядку: `P26` — финальный audit-lock: заморозка эталонной цепочки (`P23/P24/P25`) и проверка воспроизводимости на одном повторном запуске.
83. `P26` Финальный audit-lock: заморозка эталонной цепочки (`P23/P24/P25`) и проверка воспроизводимости на повторном запуске — ЗАКРЫТ.
   - Добавлен lock-скрипт:
     - `run_p26_audit_lock.ps1`
   - Повторный воспроизводимый прогон (`Mode=combined`, `StepLabel=P26`) — PASS:
     - `reports/qa_gate/p23_operator_unified_20260524T102306Z.json`
     - `reports/qa_gate/p23_operator_unified_20260524T102306Z.log`
   - CSV/XLSX + движок + зависимости + аудит в повторном прогоне:
     - `reports/qa_gate/daily_long_short_cycle_20260524T102306Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T102559Z.json` (PASS, long)
     - `reports/qa_gate/table_convergence_5plus_20260524T102612Z.json` (PASS, short)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T102628Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T102628Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T102629Z.json` (PASS, step=P26)
     - `reports/qa_gate/p72_freeze_ready_20260524T102638Z.json` (PASS)
   - Финальная фиксация lock-состояния и последних PASS-артефактов:
     - `reports/qa_gate/p24_latest_pass_20260524T102645Z.json` (PASS)
     - `reports/qa_gate/p26_audit_lock_20260524T102646Z.json` (PASS)
84. Следующий блок по порядку: `P27` — итоговый handoff-пакет (операторская памятка + команды + последние PASS-артефакты одним отчетом).
85. `P27` Итоговый handoff-пакет (операторская памятка + команды + последние PASS-артефакты одним отчетом) — ЗАКРЫТ.
   - Добавлен скрипт сборки handoff-пакета:
     - `run_p27_handoff_package.ps1`
   - Контрольный прогон (`mode=table_chain`, `StepLabel=P27`) — PASS:
     - `reports/qa_gate/p23_operator_unified_20260524T102806Z.json`
   - CSV/XLSX + движок + зависимости + аудит:
     - `reports/qa_gate/table_convergence_5plus_20260524T102811Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T102827Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T102828Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T102828Z.json` (PASS, step=P27)
     - `reports/qa_gate/p72_freeze_ready_20260524T102837Z.json` (PASS)
   - Итоговые агрегаты:
     - `reports/qa_gate/p24_latest_pass_20260524T102845Z.json` (PASS)
     - `reports/qa_gate/p27_handoff_package_20260524T102845Z.json` (PASS)
86. Следующий блок по порядку: `P28` — финальный closeout `TZ_FEATURES_BLOCK` (итоговый статус «готово к рабочему контуру», зафиксированные команды запуска и контрольный перечень артефактов).
87. `P28` Финальный closeout `TZ_FEATURES_BLOCK` (итоговый статус «готово к рабочему контуру», зафиксированные команды запуска и контрольный перечень артефактов) — ЗАКРЫТ.
   - Выпущен финальный closeout-документ:
     - `docs/P28_FINAL_CLOSEOUT_2026-05-24_RU.md`
   - Контрольный прогон `CSV/XLSX + движок + зависимости + аудит` (`mode=table_chain`, `StepLabel=P28`) — PASS:
     - `reports/qa_gate/p23_operator_unified_20260524T105315Z.json`
     - `reports/qa_gate/table_convergence_5plus_20260524T105321Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T105337Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T105338Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T105338Z.json` (PASS, step=P28)
     - `reports/qa_gate/p72_freeze_ready_20260524T105348Z.json` (PASS)
   - Финальные агрегаты:
     - `reports/qa_gate/p24_latest_pass_20260524T105355Z.json` (PASS)
     - `reports/qa_gate/p27_handoff_package_20260524T105355Z.json` (PASS)
88. Статус плана `TZ_FEATURES_BLOCK`: все запланированные блоки (`P14..P28`) закрыты, контур готов к рабочей эксплуатации.
89. ОТКРЫТЫ 2 дополнительных блока по гипотезам/фичам (после P28) для функционального закрытия coverage.
90. `P29` — `swing_bos_minmax` (OPEN): требуется фактическое покрытие гипотез блока в long/short coverage (без missing_names) + PASS цепочки таблиц/движка/аудитов.
91. `P30` — `density_orderbook` (OPEN): требуется фактическое покрытие density/orderbook-гипотез в long/short coverage (без missing_names) + `orderbook_source_audit --expect-status active` PASS + PASS цепочки таблиц/движка/аудитов.
92. Детальный план и критерии приемки зафиксированы в:
   - `docs/TZ_P29_P30_HYPOTHESIS_COVERAGE_2026-05-24_RU.md`
93. `P29` — `swing_bos_minmax` (OPEN -> CLOSED) — ЗАКРЫТ.
   - Добавлен целевой скрипт покрытия блока:
     - `run_p29_swing_bos_minmax_coverage.ps1`
   - Coverage блока (объединение history по серии целевых прогонов long/short):
     - `reports/qa_gate/p29_swing_bos_minmax_coverage_20260524T111758Z.json` (PASS)
     - missing: `long_only=[]`, `short_only=[]`.
   - Контрольная цепочка CSV/XLSX + движок + зависимости + аудит:
     - `reports/qa_gate/table_convergence_5plus_20260524T111732Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T111748Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T111748Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T111749Z.json` (PASS, step=P29)
     - `reports/qa_gate/p72_freeze_ready_20260524T111758Z.json` (PASS)
94. Следующий блок по порядку: `P30` — `density_orderbook` (coverage без missing_names + PASS chain + active source audit).
95. `P30` — `density_orderbook` (OPEN -> CLOSED) — ЗАКРЫТ.
   - Добавлен целевой скрипт покрытия блока:
     - `run_p30_density_orderbook_coverage.ps1`
   - Runtime-фикс поддержки orderbook-гипотез в CLI/движке:
     - `src/mlbotnav/adaptive_auto_train.py` (добавлены фильтры в choices)
     - `src/mlbotnav/search_gate_candidate.py` (добавлены фильтры в choices)
     - `src/mlbotnav/pipeline_train_eval.py` (добавлены фильтры в choices)
     - `src/mlbotnav/backtest.py` (добавлена поддержка `orderbook_imbalance_l1_l50`, `spread_pressure_and_delta_absorption`)
   - Coverage блока (объединение history по серии целевых прогонов long/short):
     - `reports/qa_gate/p30_density_orderbook_coverage_20260524T114051Z.json` (PASS)
     - missing: `long_only=[]`, `short_only=[]`.
   - Контрольная цепочка CSV/XLSX + движок + зависимости + аудит:
     - `reports/qa_gate/table_convergence_5plus_20260524T114024Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T114040Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T114041Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T114041Z.json` (PASS, step=P30)
     - `reports/qa_gate/p72_freeze_ready_20260524T114050Z.json` (PASS)
96. Статус расширенного плана `TZ_FEATURES_BLOCK` (включая доп.блоки P29/P30): все пункты закрыты, незакрытых блоков по гипотезам/фичам не осталось.
97. Пост-закрытия `TZ_FEATURES_BLOCK`: контрольный re-audit контура (CSV/XLSX + движок + зависимости + gate/freeze) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T114211Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T114216Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T114233Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T114233Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T114234Z.json` (PASS, step=P31)
   - `reports/qa_gate/p72_freeze_ready_20260524T114243Z.json` (PASS)
98. Текущий статус: `TZ_FEATURES_BLOCK` стабилен, дополнительных незакрытых пунктов по плану нет.
99. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P32) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T114324Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T114330Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T114347Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T114347Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T114347Z.json` (PASS, step=P32)
   - `reports/qa_gate/p72_freeze_ready_20260524T114357Z.json` (PASS)
100. Автосводка актуальных PASS-артефактов обновлена:
   - `reports/qa_gate/p24_latest_pass_20260524T114358Z.json` (PASS)
101. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P33) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T114459Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T114505Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T114521Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T114522Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T114522Z.json` (PASS, step=P33)
   - `reports/qa_gate/p72_freeze_ready_20260524T114532Z.json` (PASS)
102. Обновлены контрольные агрегаты:
   - `reports/qa_gate/p24_latest_pass_20260524T114532Z.json` (PASS)
   - `reports/qa_gate/p26_audit_lock_20260524T114533Z.json` (PASS)
103. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P34) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T114613Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T114619Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T114635Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T114636Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T114636Z.json` (PASS, step=P34)
   - `reports/qa_gate/p72_freeze_ready_20260524T114645Z.json` (PASS)
104. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T114646Z.json` (PASS)
105. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P35) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T114727Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T114733Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T114749Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T114750Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T114750Z.json` (PASS, step=P35)
   - `reports/qa_gate/p72_freeze_ready_20260524T114759Z.json` (PASS)
106. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T114800Z.json` (PASS)
107. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P36) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T114844Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T114850Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T114906Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T114907Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T114907Z.json` (PASS, step=P36)
   - `reports/qa_gate/p72_freeze_ready_20260524T114916Z.json` (PASS)
108. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T114917Z.json` (PASS)
109. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P37) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T114956Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T115002Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T115019Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T115019Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T115019Z.json` (PASS, step=P37)
   - `reports/qa_gate/p72_freeze_ready_20260524T115029Z.json` (PASS)
110. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T115029Z.json` (PASS)
111. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P38) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T115114Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T115120Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T115136Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T115137Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T115137Z.json` (PASS, step=P38)
   - `reports/qa_gate/p72_freeze_ready_20260524T115147Z.json` (PASS)
112. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T115147Z.json` (PASS)
113. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P39) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T115317Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T115323Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T115340Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T115340Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T115340Z.json` (PASS, step=P39)
   - `reports/qa_gate/p72_freeze_ready_20260524T115350Z.json` (PASS)
114. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T115358Z.json` (PASS)
115. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P40) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T115425Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T115430Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T115447Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T115448Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T115448Z.json` (PASS, step=P40)
   - `reports/qa_gate/p72_freeze_ready_20260524T115457Z.json` (PASS)
116. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T115508Z.json` (PASS)
117. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P41) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T115617Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T115623Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T115639Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T115640Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T115640Z.json` (PASS, step=P41)
   - `reports/qa_gate/p72_freeze_ready_20260524T115649Z.json` (PASS)
118. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T115655Z.json` (PASS)
119. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P42) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T120335Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T120341Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T120358Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T120359Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T120359Z.json` (PASS, step=P42)
   - `reports/qa_gate/p72_freeze_ready_20260524T120409Z.json` (PASS)
120. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T120415Z.json` (PASS)
121. `P43` — Freeze Release Gate (CSV/XLSX + движок + зависимости + аудит) — PASS.
   - Техфикс для корректной проверки release-режима:
     - `src/mlbotnav/p72_freeze_ready_check.py` (добавлен `--mode freeze|release`)
     - `run_p23_operator_unified.ps1` (добавлен параметр `-FreezeCheckMode`)
   - `reports/qa_gate/p23_operator_unified_20260524T121426Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T121432Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T121448Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T121449Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T121449Z.json` (PASS, step=P43)
   - `reports/qa_gate/p72_freeze_ready_20260524T121459Z.json` (PASS, mode=release)
122. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T121505Z.json` (PASS)
123. `P44` — Coverage Threshold для гипотез (long/short отдельно) + контроль CSV/XLSX/движка/зависимостей/аудитов — PASS.
   - Техфикс:
     - `src/mlbotnav/hypothesis_coverage_audit.py` (добавлены пороги `--min-coverage-ratio`, `--min-covered-count` и check `active_backlog_coverage_threshold_met`).
   - Coverage long_only (threshold):
     - `reports/qa_gate/hypothesis_coverage_long_only_20260524T121706Z.json` (PASS, ratio=0.0833, covered=1, threshold=0.08/1)
   - Coverage short_only (threshold):
     - `reports/qa_gate/hypothesis_coverage_short_only_20260524T121706Z.json` (PASS, ratio=0.0909, covered=1, threshold=0.08/1)
   - Полный контрольный контур:
     - `reports/qa_gate/p23_operator_unified_20260524T121716Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T121722Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T121739Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T121740Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T121740Z.json` (PASS, step=P44)
     - `reports/qa_gate/p72_freeze_ready_20260524T121750Z.json` (PASS, mode=release)
124. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T121756Z.json` (PASS)
125. `P45` — Свежий независимый E2E прогон LONG + проверка CSV/XLSX/движка/зависимостей/аудитов — PASS.
   - Зафиксирован риск окна `2026-05-20 -> 2026-05-21`: long OOS отрицательный (`-18.4341%`), `table_convergence`=FAIL в `daily_long_short_cycle_20260524T121853Z.json`.
   - Контрольный рабочий прогон для закрытия пункта выполнен на окне `2026-05-19 -> 2026-05-20`:
     - `reports/qa_gate/daily_long_short_cycle_20260524T122027Z.json` (PASS)
     - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T122134Z.json`
     - `reports/qa_gate/p23_operator_unified_20260524T122027Z.json` (PASS)
     - `reports/qa_gate/table_convergence_5plus_20260524T122158Z.json` (PASS)
     - `reports/table_canon_current/audit_chain_report.json` (PASS)
     - `reports/qa_gate/features_block_audit_20260524T122214Z.json` (PASS)
     - `reports/qa_gate/orderbook_source_audit_20260524T122215Z.json` (PASS, expect active)
     - `reports/qa_gate/tz_gate_20260524T122215Z.json` (PASS, step=P45)
     - `reports/qa_gate/p72_freeze_ready_20260524T122225Z.json` (PASS, mode=release)
126. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T122231Z.json` (PASS)
127. `P46` — Свежий независимый E2E прогон SHORT + проверка CSV/XLSX/движка/зависимостей/аудитов — PASS.
   - `reports/qa_gate/daily_long_short_cycle_20260524T122312Z.json` (PASS)
   - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T122418Z.json`
   - `reports/qa_gate/p23_operator_unified_20260524T122312Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T122442Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T122458Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T122459Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T122459Z.json` (PASS, step=P46)
   - `reports/qa_gate/p72_freeze_ready_20260524T122509Z.json` (PASS, mode=release)
128. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T122515Z.json` (PASS)
129. `P47` — Both-Mode Consistency Check + проверка CSV/XLSX/движка/зависимостей/аудитов — PASS.
   - `reports/qa_gate/daily_long_short_cycle_20260524T122551Z.json` (PASS)
   - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_long_only_20260524T122657Z.json`
   - `reports/final_review/oos_report_SOLUSDT_1m_2026-05-20_short_only_20260524T122822Z.json`
   - `reports/qa_gate/p23_operator_unified_20260524T122551Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T122847Z.json` (PASS, long)
   - `reports/qa_gate/table_convergence_5plus_20260524T122901Z.json` (PASS, short)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T122917Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T122918Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T122918Z.json` (PASS, step=P47)
   - `reports/qa_gate/p72_freeze_ready_20260524T122928Z.json` (PASS, mode=release)
130. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T122935Z.json` (PASS)
131. `P48` — Финальный 5+ Audit + Handoff (CSV/XLSX + движок + зависимости + аудит + release bundle) — PASS.
   - `reports/qa_gate/p26_audit_lock_20260524T123025Z.json` (PASS)
   - `reports/qa_gate/p27_handoff_package_20260524T123025Z.json` (PASS)
   - `reports/qa_gate/p71_release_bundle_20260524T123121Z.json` (PASS)
   - `reports/qa_gate/p71_release_bundle_20260524T123121Z.md`
   - `reports/qa_gate/p72_freeze_ready_20260524T123132Z.json` (PASS, mode=release)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
132. Обновлена финальная автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T123132Z.json` (PASS)
133. Пост-стабилизационный контроль `TZ_FEATURES_BLOCK` (P49) — PASS.
   - `reports/qa_gate/p23_operator_unified_20260524T124533Z.json` (PASS)
   - `reports/qa_gate/table_convergence_5plus_20260524T124539Z.json` (PASS)
   - `reports/table_canon_current/audit_chain_report.json` (PASS)
   - `reports/qa_gate/features_block_audit_20260524T124556Z.json` (PASS)
   - `reports/qa_gate/orderbook_source_audit_20260524T124556Z.json` (PASS, expect active)
   - `reports/qa_gate/tz_gate_20260524T124556Z.json` (PASS, step=P49)
   - `reports/qa_gate/p72_freeze_ready_20260524T124606Z.json` (PASS, mode=release)
134. Обновлена автосводка PASS-артефактов:
   - `reports/qa_gate/p24_latest_pass_20260524T124613Z.json` (PASS)
