# STAS3 PERCENT LADDER REVIEW

Статус: `STAS3_V2_CLEAN_READY_NO_OLD_STAS3_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

## Готовый Stas3 V2 CLEAN 2026-07-09

Stas3 V2 пересобран с нуля отдельным clean-модулем. Старый `visual_entry_stas3_percent_ladder_review.py` не использовался как основа.

Финальный clean run:

```text
STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_clean_20260510_20260512_long_only_20260709_123622
```

Источник Stas2:

```text
STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330
```

Итог: `214` входов, `214` обработано, `0` skipped, row parity `true`, `157` hit 1%, `79` clean medium TP `>=1%`, `111` wrong 1% TP, `38` good-entry-but-wrong-1% TP, `99` noise, `41` строк phase ladder, `66` PNG, пустых PNG нет.

Ключевые clean-артефакты:

```text
STAS3_V2_CLEAN_ENTRY_CONTEXT.csv
STAS3_V2_CLEAN_TP_PATH.csv
STAS3_V2_CLEAN_TP_DECISION.csv
STAS3_V2_CLEAN_PHASE_LADDER.csv
STAS3_V2_CLEAN_WRONG_TP.csv
STAS3_V2_CLEAN_NOISE.csv
STAS3_V2_CLEAN_REPORT_RU.md
STAS3_V2_CLEAN_TABLES.xlsx
```

Открыть clean V2:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open browse
.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open xlsx
.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open report
.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open entries
```

Границы clean V2: `NO_OLD_STAS3_BASE`, `LONG_ONLY`, `SHORT_RISK_CONTEXT_ONLY`, `WAVE/GAP/continuous` только hindsight-review, `entry_price_for_calc = entry_price_5bps`, без short-входов, short-TP, ML/export/training, Optuna, scorer, target-lock и API.

## Готовый Stas3 V2 2026-07-09

Статус: `INVALID_OLD_STAS3_BASE_DRAFT`.

Этот блок оставлен как история ошибки. Этот run не считать принятым Stas3 V2: он был собран через доработку старого Stas3-файла, а не с нуля.

Старые Stas3 V1 runs не удалялись и остаются архивом.

Финальный V2 run:

```text
STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925
```

Источник Stas2:

```text
STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330
```

Итог: `214` входов, `0` skipped, row parity `true`, `157` hit 1%, `93` строк с фазовым reasonable TP, `76` wrong 1% TP, `46` noise, `122` строк в `STAS3_V2_WRONG_TP_REVIEW.csv`, `55` PNG, пустых PNG нет.

Ключевые V2-артефакты:

```text
STAS3_V2_ENTRY_TP_AUDIT.csv
STAS3_V2_CONTEXT_BUNDLE.csv
STAS3_V2_TP_LADDER_BY_PHASE.csv
STAS3_V2_WRONG_TP_REVIEW.csv
STAS3_V2_SKIPPED_ROWS.csv
STAS3_V2_REPORT_RU.md
STAS3_V2_TP_LADDER_RU.md
STAS3_PERCENT_LADDER_TABLES.xlsx
```

Границы V2: `LONG_ONLY`, `SHORT_RISK_CONTEXT_ONLY`, без short-входов, short-TP, short-ladder, ML/export/training, Optuna, scorer, target-lock и API. `MFE MAX` остается только diagnostic/hindsight fact, не TP/exit.

## Обнуление Stas3 2026-07-09

Текущая реализация Stas3 V1 заморожена как архивный review-only слой. Старые runs не удаляются, но больше не считаются чистым source-of-truth для следующей работы.

Новый источник для продолжения:

```text
STAS3_PERCENT_LADDER_REVIEW/TZ_STAS3_V2_RESET_RU.md
```

Ключевые правки V2:

1. первый проход только `LONG`;
2. минимальная рабочая сетка начинается с `0.3%`;
3. быстрые TP: `0.3-0.9%`;
4. средние LONG-ходы: от `1.0%` до `2.0%` с шагом `0.1%`;
5. продолжение среднего LONG-хода: от `2.0%` до `20.0%` с шагом `0.2%`;
6. swing пока не оформляется как стратегия;
7. сделка не закрывается искусственно по границе `24h`, если LONG-волна продолжается на следующий день;
8. точки входа не придумываются: брать `anchor_time_utc`, `anchor_low_price`, `entry_time_utc`, `entry_open_price`, `entry_price_5bps` из выбранного Stas2 run.
9. в одну таблицу по каждой LONG-сделке собрать сессию, фон, LONG, `SHORT`-risk% как риск-фон, WAVE, волатильность/процентные блоки и volume-context.
10. `ideal_review_tp_pct` и `max_feasible_review_tp_pct` являются hindsight-review полями, а не готовой стратегией.

Актуальный source для корректировки ТЗ V2:

```text
STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330
```

Рабочие дни первого V2-разбора: `2026-05-10`, `2026-05-11`, `2026-05-12`.

Смысл reset: собрать Stas3 заново как процентную лестницу и TP-audit по фазам, без визуального превращения `MFE MAX` в выход сделки и без смешивания быстрых TP, средних ходов и swing-движений в одну псевдостратегию.

## Архивный rebuild V1 2026-07-09

Этот rebuild относится к старой реализации Stas3 V1 и не является source-of-truth для V2. Он оставлен только как архивный review-only артефакт.

Stas3 был пересобран поверх Stas2 с `SHORT`, continuous `WAVE/GAP` и компактными подписями коротких сильных волн.

Источник Stas2:

```text
STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138
```

Актуальный Stas3 run:

```text
STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260508_20260512_from_stas2_short_labels_v1_20260709_084730
```

Итог: `214` rows, `0` skipped, `157` hit 1%, `93` reasonable TP, `89` mismatch к 1% TP, `46` noise, `9` fast clean, `68` late-pump dependent, `53` PNG, пустых PNG нет.

Ограничение: Stas3 пока читает `STAS2_RECORDS.csv`. Stas2 wave-ledger таблицы `STAS2_MACRO_WAVES.csv` и `STAS2_CONTINUOUS_WAVES.csv` еще не join-ятся в каждую Stas3 entry-строку. Если нужно видеть WAVE-контекст прямо в Stas3, это отдельный review-only join, не causal feature.

## Что это в старой реализации V1

Этот раздел описывает архивную реализацию V1. Для новой работы использовать ТЗ V2 выше, а не старую сетку V1.

`STAS3` - отдельный post-entry audit поверх текущих `STAS1` и `STAS2`.

Он не ищет новые входы и не меняет Stas1/Stas2. Он читает готовый `STAS2_RECORDS.csv`, берет фазу рынка до входа из Stas2 и считает после `entry_time_utc`:

1. архивную V1 percent ladder `0.2 / 0.3 / 0.4 / 0.5 / 0.6 / 0.7 / 0.8 / 0.9 / 1.0 / 1.2 / 1.5 / 1.7 / 1.9 / 2.0 / 3.0 / 5.0 / 7.0%`;
2. время до каждой достигнутой фазы;
3. фактическое движение после входа: `actual_mfe_pct`, `actual_mae_pct`, время MFE/MAE и порядок события;
4. post-entry блоки `5m / 15m / 30m / 60m`;
5. разумный TP по phase profile: fast TP, hold TP, цена TP, причина и источник;
6. где вход был шумом, а где вход мог быть рабочим, но 1% TP был неверной целью;
7. сводки по фазе, LONG-волне, setup-quality, сессии и verdict.

## Главная граница

Stas3 смотрит свечи после входа. Поэтому его поля нельзя использовать как causal features входа, scorer, target-lock или ML-label без отдельного ручного approved-ledger.

Запрещено внутри Stas3:

1. запускать ML/export/training;
2. запускать Optuna;
3. создавать scorer или target-lock;
4. обращаться к торговому API;
5. считать `stas3_verdict` утвержденной разметкой без ручного review.

## Рабочий движок

```text
src/mlbotnav/visual_entry_stas3_percent_ladder_review.py
```

## Запуск диапазона

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-02 -EndDay 2026-05-03 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535
```

Если `-Stas2RunDir` не указан, будет использован последний run из `STAS2_MARKET_PHASE_REVIEW/runs/`.

Параметры TP-вывода по умолчанию:

```text
TpFastMinutes = 120
TpMinSamples = 5
TpHitRateMin = 0.60
TpFastHitRateMin = 0.50
```

## Открыть последний результат

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open browse
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open tp
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
```

## Где результаты

```text
STAS3_PERCENT_LADDER_REVIEW/runs/
```

Внутри каждого run:

1. `STAS3_RECORDS.csv` - основная таблица сделок и post-entry метрик.
2. `STAS3_ENTRY_PHASE_TABLE.csv` - входы Stas1 с фазой рынка на момент входа.
3. `STAS3_ACTUAL_MOVEMENT.csv` - фактическое движение после входа.
4. `STAS3_REASONABLE_TP.csv` - разумный TP по фазовому профилю и отметка ошибки 1% TP.
5. `STAS3_TP_LADDER_BY_PHASE.csv` / `STAS3_TP_LADDER_BY_PROFILE.csv` - процентные диапазоны по фазам.
6. `STAS3_TP_LADDER_V0_RU.md` - первая русская версия процентной лестницы.
7. `STAS3_PERCENT_LADDER_TABLES.xlsx` - Excel-friendly workbook со всеми таблицами.
8. `STAS3_DAY_OVERVIEW_YYYYMMDD.png` - день целиком с точками Stas3.
9. `STAS3_ENTRY_LADDER_PAGE_*.png` - closeup-страницы после входа с визуальным разбором сделки: `SIGNAL`, `ENTRY`, линия TP, звезда `EXIT`, подпись времени до TP.
10. `STAS3_LOW_SIGNAL_TO_MFE_MAX.csv` - путь от low-сигнала до максимального хода `MFE MAX`.
11. `STAS3_ENTRY_TO_TP_PATH.csv` - архивный V1 путь от `ENTRY` до 0.2/0.5/1.0% и остаток движения после ранних TP.
12. `STAS3_EXIT_REVIEW_BUCKETS.csv` - review-only корзины для ручного разбора удержания и раннего выхода.
13. `STAS3_BIG_MOVE_REVIEW_PAGE_*.png` - длинные графики `SIGNAL/ENTRY -> MFE MAX` для изучения больших ходов.
14. `BROWSE_BY_DAY/` - дневной просмотр.
15. `STAS3_REPORT_RU.md` - короткий русский отчет.

## Как читать TP на графике

1. Оранжевый кружок `SIGNAL` - исходная low/anchor-свеча сигнала.
2. Голубой треугольник `ENTRY` - свеча входа и цена `entry_price_5bps`.
3. Голубой пунктир `SIGNAL -> ENTRY` - переход от сигнала к исполнению.
4. Красная стрелка `ENTRY -> EXIT` - визуальная отработка сделки от цены входа до срабатывания TP.
5. Желтая горизонтальная линия - расчетный уровень цены `TP v0` по фазовому профилю.
6. Желтая звезда и подпись `EXIT Xm` - место и время срабатывания TP.
7. Серая пунктирная линия `TP 1%` - fallback для строк, где фазовый TP не рассчитан.
8. Зеленая стрелка и маркер `MFE MAX` на `STAS3_BIG_MOVE_REVIEW_PAGE_*.png` - максимальный ход после входа, только для review.
9. Фиолетовый маркер `MAE MIN` - минимальная цена/просадка в окне удержания.

Контрольный результат текущего этапа:

```text
STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260504_20260509_big_move_review_v2_20260707_090246
```

## Правило работы дальше

Stas3 нужен для ручной проверки, какие Stas1/Stas2 входы реально проходят ladder, какой TP соответствует фазе, а где рынок дает движение слишком поздно или вход был шумом. После review можно отдельно решать, какие классы попадут в будущий approved-ledger.
