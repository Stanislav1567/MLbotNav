# ТЗ: Visual Entry Calibration

Дата UTC: `2026-06-25`.

Статус: `DRAFT_FOR_USER_REVIEW`.

## 1. Назначение

`Visual Entry Calibration` - отдельный контур для подбора паспортов и комбинаций паспортов под ручную визуальную разметку входов на графике.

Цель контура: не подогнать один параметр под один скриншот, а построить повторяемую схему:

1. пользователь размечает желаемые входы на графиках;
2. разметка переводится в машинный `manual_entries.json`;
3. backtest/Optuna проверяют паспорта и комбинации паспортов против этой разметки;
4. результат оценивается по попаданию в ручные входы, лишним входам, лагу входа и финансовому итогу;
5. только устойчивые и проверенные варианты могут стать кандидатами для ручного `APPROVED_FOR_ML`.

## 2. Главный инвариант данных

Все контуры должны смотреть на один и тот же набор свечей.

Обязательное правило:

1. график для разметки строится из `data_layer=core`;
2. backtest/Optuna используют тот же `data_layer=core`;
3. будущий ML-контур использует тот же `data_layer=core`;
4. для каждого дня фиксируется `source_csv_sha256`;
5. если `source_csv_sha256` графика и прогона не совпадают, результат считается `DATA_PARITY_FAIL`.

Для текущей первой партии seed-графиков источник зафиксирован в:

`reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_manifest.json`

Seed-дни:

1. `SOLUSDT 1m 2026-05-12 UTC`;
2. `SOLUSDT 1m 2026-05-13 UTC`;
3. `SOLUSDT 1m 2026-05-14 UTC`.

Каждый seed-день содержит `1440` минутных свечей от `00:00` до `23:59 UTC`.

## 3. Артефакты ручной разметки

После того как пользователь нарисовал стрелки на PNG, по каждому дню создается машинный файл:

`reports/manual_entries/<run_id>/manual_entries.json`

Минимальная структура:

```json
{
  "schema_version": 1,
  "run_id": "manual_entries_SOLUSDT_1m_2026-05-12_2026-05-14_v1",
  "symbol": "SOLUSDT",
  "timeframe": "1m",
  "data_layer": "core",
  "source_images": [
    {
      "date_utc": "2026-05-12",
      "image_path": "reports/manual_entries/.../manual_markup_seed_SOLUSDT_1m_2026-05-12_CORE_marked.png",
      "source_csv": "data/core/bybit_ohlcv/dt=2026-05-12/tf=1m/symbol=SOLUSDT/part-final.csv",
      "source_csv_sha256": "<sha256>",
      "rows": 1440
    }
  ],
  "entries": [
    {
      "entry_id": "ME_20260512_0925_LONG_001",
      "date_utc": "2026-05-12",
      "side": "long",
      "target_entry_time_utc": "2026-05-12T09:25:00Z",
      "tolerance_bars_before": 2,
      "tolerance_bars_after": 2,
      "label_type": "manual_visual_arrow",
      "setup_type_hint": "unknown",
      "comment": "ручная стрелка пользователя"
    }
  ]
}
```

Разметка должна хранить именно время входа, а не только картинку. PNG остается доказательством, но расчет идет по `target_entry_time_utc`.

## 4. Правило времени входа

Для `1m` market-entry текущий runtime использует разделение:

1. `entry_signal_time_utc` - сигнальная свеча;
2. `entry_time_utc` - свеча фактического входа;
3. обычно `entry_time_utc = entry_signal_time_utc + 1 бар`.

Если пользователь ставит стрелку на свечу, где должен быть вход, scorer сравнивает ее с `entry_time_utc`.

Если нужно анализировать причину входа, scorer дополнительно смотрит предыдущую сигнальную свечу:

`entry_signal_time_utc = target_entry_time_utc - 1 бар`.

## 5. Метрики visual-hit scorer

Для каждого прогона scorer должен считать:

1. `targets_total` - всего ручных входов;
2. `target_hits` - сколько ручных входов поймано;
3. `missed_targets` - сколько ручных входов пропущено;
4. `false_entries` - сколько входов вне ручных окон;
5. `entries_total` - всего сделок/входов;
6. `precision` - `target_hits / entries_total`;
7. `recall` - `target_hits / targets_total`;
8. `f1_visual` - гармоническое среднее precision/recall;
9. `entry_lag_bars_avg` - среднее отклонение входа от цели;
10. `entry_lag_bars_abs_max` - максимальное абсолютное отклонение;
11. `duplicate_hits` - несколько сделок в одно ручное окно;
12. `net_return_pct` - итог backtest/OOS;
13. `trades` - число сделок;
14. `mae_pct`, `mfe_pct` - если доступны в trade log;
15. `visual_status` - итоговая классификация.

Базовые классы:

1. `VISUAL_PASS_TRADEFUL_POSITIVE`;
2. `VISUAL_PASS_TRADEFUL_NEGATIVE`;
3. `VISUAL_HITS_WITH_TOO_MANY_FALSE_ENTRIES`;
4. `VISUAL_MISS`;
5. `VISUAL_OVERFIT_DEV_ONLY`;
6. `DATA_PARITY_FAIL`;
7. `NO_ML_PROMOTION`.

## 6. Окна попадания

Стандарт для `1m`:

1. `tolerance_bars_before = 2`;
2. `tolerance_bars_after = 2`.

Пример: ручной вход `09:25` считается пойманным, если `entry_time_utc` попал в диапазон `09:23..09:27`.

Если несколько сделок попали в одно окно, одна считается `hit`, остальные считаются `duplicate_hits` или `false_entries_inside_hit_window`, в зависимости от режима scorer.

## 7. Порядок работ

### Этап 1. Seed-графики

Статус: `DONE`.

Созданы графики:

1. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-12_CORE.png`;
2. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.png`;
3. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.png`.

### Этап 2. Ручная разметка

Статус: `WAITING_FOR_USER_MARKUP`.

Пользователь рисует стрелки входов на трех PNG.

После возврата размеченных PNG нужно:

1. восстановить `target_entry_time_utc`;
2. создать `manual_entries.json`;
3. проверить, что каждая стрелка попадает в существующую свечу `core`;
4. записать аудит `manual_entries_audit_*.md`.

### Этап 3. Visual scorer

Создать CLI-инструмент:

`python -m mlbotnav.visual_entry_score --manual-entries <manual_entries.json> --trades-csv <oos_backtest_trades.csv> --out-dir reports/qa_gate`

Выходы:

1. `visual_entry_score_*.json`;
2. `visual_entry_score_*.md`;
3. опционально PNG с наложением ручных стрелок и фактических входов.

### Этап 4. Solo-passport sweep

Сначала проверяются одиночные паспорта, без комбо.

Цель: понять, какие паспорта вообще объясняют ручные входы.

Порядок:

1. запускать только паспорта, которые технически активны и имеют матрицу;
2. каждый паспорт проверять отдельно;
3. сохранять `visual_score` рядом с обычным OOS report;
4. не выбирать победителя только по прибыли;
5. не выбирать победителя только по попаданию в стрелки.

Минимальное правило кандидата:

1. `recall > 0`;
2. `precision` не ниже порога;
3. `false_entries` ограничены;
4. `net_return_pct` не отрицательный или отдельно помечен как diagnostic-only;
5. нет `DATA_PARITY_FAIL`.

### Этап 5. Block sweep

После solo-passport sweep проверяются блоки:

1. `B001` momentum;
2. volume/flow passports;
3. structure/level passports;
4. pattern/candle/chart passports;
5. будущая `REVERSAL_DIP_BUY_LONG`.

Цель: понять, какие семейства дают контекст, триггер и подтверждение.

### Этап 6. Combo sweep

Комбо строится только из паспортов, которые показали смысловой вклад.

Запрещено делать полный взрывной перебор всех паспортов со всеми.

Разрешенные типы комбо:

1. `context AND trigger`;
2. `context AND trigger AND confirm`;
3. `N из M`, но только с лимитом `false_entries`;
4. side-specific LONG/SHORT комбо.

Пример для входов около дна:

1. `dip_context`: падение `ret_12/ret_24`, близость к локальному low, нижняя часть диапазона;
2. `reversal_trigger`: первая зеленая свеча, engulf/pin/hammer, возврат над EMA;
3. `confirm`: volume z-score, OBV/MFI, BOS/CHOCH, уровень/поддержка.

## 8. Защита от overfit

Текущие три дня - это начальный `DEV_SET`.

Нельзя делать `APPROVED_FOR_ML` только по этим дням.

Минимальная схема допуска:

1. `DEV_SET` - дни, где подбираем и проектируем;
2. `VALIDATION_SET` - новые размеченные дни, которые не использовались при подборе;
3. `HOLDOUT_SET` - финальная проверка без изменения параметров.

Если комбо ловит стрелки только на `DEV_SET`, оно получает статус:

`VISUAL_OVERFIT_DEV_ONLY`.

## 9. Граница перед ML

В ML ничего не передается автоматически.

Для ручного review нужен пакет:

1. `manual_entries.json`;
2. `passport_combo_manifest.json`;
3. `visual_entry_score.json`;
4. `trade_log.csv`;
5. `oos_report.json`;
6. `data_parity_audit.json`;
7. `audit.md`;
8. PNG overlay: ручные входы против фактических входов.

До ручного решения статус пакета:

`READY_FOR_MANUAL_REVIEW`.

Только после отдельного решения пользователя пакет может попасть в:

`configs/ml_approved_calibration_packages.yaml`

со статусом:

`APPROVED_FOR_ML`.

Запрещено передавать в ML:

1. `NO_GO`;
2. `VALIDATION_FAIL`;
3. `VISUAL_OVERFIT_DEV_ONLY`;
4. отрицательные diagnostic-only результаты;
5. результаты с `DATA_PARITY_FAIL`;
6. результаты без `manual_entries.json`;
7. результаты без visual scorer.

## 10. Требования к отчетности

Каждый этап должен давать короткий русский аудит:

1. что проверено;
2. какие входы пойманы;
3. какие входы пропущены;
4. сколько лишних входов;
5. какие паспорта/комбо участвовали;
6. какой финансовый результат;
7. можно ли двигаться дальше;
8. почему нельзя или можно передавать в ML.

Большие CSV/JSON не вставлять в чат; хранить в `reports/`.

## 11. Первый практический маршрут

После получения размеченных пользователем PNG:

1. создать `manual_entries.json` для трех дней;
2. сделать `manual_entries_audit`;
3. реализовать `visual_entry_score`;
4. прогнать scorer на уже существующих B001 diagnostic trades;
5. выбрать первые группы паспортов для solo-passport sweep;
6. отдельно спроектировать черновую family `REVERSAL_DIP_BUY_LONG`;
7. после первых результатов сделать таблицу: паспорт/комбо, hits, misses, false entries, OOS, решение.

## 12. Definition Of Done для этого ТЗ

ТЗ считается готовым к реализации, когда:

1. пользователь подтвердил структуру `manual_entries.json`;
2. пользователь подтвердил метрики scorer;
3. пользователь вернул размеченные PNG или список времен входов;
4. создан первый `manual_entries.json`;
5. первый scorer report успешно посчитал попадания хотя бы по одному существующему backtest CSV.

До этого момента `Visual Entry Calibration` остается в статусе:

`DESIGN_READY_WAITING_FOR_MARKUP`.
