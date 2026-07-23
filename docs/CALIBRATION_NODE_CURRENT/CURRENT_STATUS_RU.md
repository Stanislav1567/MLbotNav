# Current Status: калибровочный узел

## STAS3 V2 Reset TZ 2026-07-09

Статус: `STAS3_V1_ARCHIVED_STAS3_V2_TZ_DRAFT_READY_NO_ML_NO_OPTUNA`.

По решению пользователя текущий Stas3 обнулен концептуально: старые runs не удаляются, но Stas3 V1 больше не является чистым source-of-truth для следующей работы.

Новое ТЗ:

`STAS3_PERCENT_LADDER_REVIEW/TZ_STAS3_V2_RESET_RU.md`

Причина reset: `MFE MAX`, big-move pages и `reasonable TP` стали визуально/смыслово выглядеть как стратегия выхода и подсмотр будущего. Stas3 V2 должен вернуться к исходной задаче: процентная лестница движения и TP-audit по фазам, без превращения в торговую стратегию.

Граница: код V2 еще не реализован. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## STAS3 Rebuild From Latest STAS2 2026-07-09

Статус: `STAS3_REBUILT_FROM_STAS2_SHORT_LABELS_V1_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

После обновления Stas2-графиков Stas3 пересобран поверх актуального источника:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138`

Новый Stas3 run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260508_20260512_from_stas2_short_labels_v1_20260709_084730`

Итог: `214` rows, `0` skipped, `157` hit 1%, `93` reasonable TP, `89` mismatch к 1% TP, `46` noise, `9` fast clean, `68` late-pump dependent, `53` PNG, пустых PNG нет. Workbook читается, tests pass.

Ограничение: `STAS2_MACRO_WAVES.csv` и `STAS2_CONTINUOUS_WAVES.csv` пока не вшиты в `STAS2_RECORDS.csv`, поэтому Stas3 использует новый источник entry-context, но не показывает WAVE-context как отдельные entry-колонки. Возможный следующий шаг - review-only join WAVE/GAP по `entry_time_utc`.

Граница: Stas3 post-entry audit только для анализа TP/percent ladder. ML/export/training, Optuna, scorer, target-lock и API не запускались.

## STAS2 Background And LONG Wave Visual Fix 2026-07-06

Статус: `STAS2_MARKET_PHASE_REVIEW_BG_LONG_WAVE_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

В Stas2 исправлена визуальная каша между слабым фоном и реальным ходом цены вверх. Теперь на overview есть две отдельные полосы:

1. `Фон` - общий range/volatility/path закрытого часа;
2. `LONG` - направленная LONG-волна `low -> subsequent high` внутри часа.

В entry context добавлены pre-entry поля:

1. `pre_*_background_phase`;
2. `pre_*_long_wave_up_from_low_pct`;
3. `pre_*_long_wave_pullback_from_high_pct`;
4. `pre_*_window_low_time_utc`;
5. `pre_*_post_low_high_time_utc`.

Контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_bg_long_wave_v0_20260706_131201`

Итог: `110` entry rows, `78` Stas1 GOOD, `32` Stas1 BAD, `43` PNG, `0` пустых PNG, `bad_context_before_entry=0`, Excel читается, CSV BOM `EF-BB-BF`.

Граница: Stas2 остается pre-entry only. Stas1 не менялся. TP/exit/percent ladder/MFE/MAE/5m post-entry blocks не добавлялись; это Stas3. ML/Optuna/scorer/target-lock/API не запускались.

## STAS2 Market Phase Visual Review 2026-07-06

Статус: `STAS2_MARKET_PHASE_REVIEW_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

По текущему Stas 2-5 процессу создан отдельный Stas2 visual review-контур:

1. `STAS2_MARKET_PHASE_REVIEW/`;
2. `src/mlbotnav/visual_entry_stas2_market_phase_review.py`;
3. wrappers: `run_day.ps1`, `run_range.ps1`, `open_last_run.ps1`;
4. артефакты: PNG overview, PNG entry context, `BROWSE_BY_DAY/`, CSV, JSON, `.xlsx`, RU-report.

Полный контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_market_phase_review_v0_20260706_124134`

Сводка: `110` entry rows, `78` Stas1 GOOD, `32` Stas1 BAD, `43` PNG, `0` пустых PNG, Excel читается, `bad_context_before_entry=0`.

Важно: Stas2 рисует только pre-entry контекст. Все после входа, включая 5m-блоки, TP/exit, MFE/MAE и percent ladder, переносится в Stas3. ML/Optuna/scorer/target-lock/API не запускались.

## STAS2 Excel Export Fix 2026-07-06

Статус: `STAS2_EXCEL_EXPORT_UTF8_BOM_XLSX_READY_NO_ML_NO_OPTUNA`.

Исправлена проблема просмотра Stas 2 таблиц в Excel:

1. CSV теперь сохраняются в `utf-8-sig`, поэтому русский текст не должен превращаться в кракозябры.
2. Пустые summary CSV получают заголовки, а не пустой файл.
3. В каждый Stas2 run добавлен `STAS2_MARKET_PHASE_TABLES.xlsx` для нормального открытия в Excel.

Проверочный run:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260503_excel_xlsx_fix_20260706_112616`

Открывать в Excel:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260503_excel_xlsx_fix_20260706_112616/STAS2_MARKET_PHASE_TABLES.xlsx`

Граница: ML/Optuna/scorer/target-lock/API не запускались.

## STAS2 Market Phase Session Audit 2026-07-06

Статус: `STAS2_MARKET_PHASE_SESSION_AUDIT_READY_NO_ML_NO_OPTUNA`.

По ТЗ `STAS 2-5 MARKET PHASE / PERCENT LADDER / ML CONTROL` выполнены первые два этапа строгого порядка:

1. `STAS 1 inventory`: Stas 1 не переписан, зафиксирован как текущая база `STAS1_GOOD_LOW_REVIEW/`.
2. `STAS 2 market phases and sessions`: построены фазы рынка по часам, сессиям, weekday/weekend и контексту перед Stas1 entry.

Новый скрипт:

`src/mlbotnav/visual_entry_stas2_market_phase_audit.py`

Финальный run:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942`

Главный отчет:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942/STAS2_MARKET_PHASE_AUDIT_RU.md`

Сводка: принято делать не `7` смешанных сессий, а `6` UTC-корзин времени плюс отдельный `day_type=weekday/weekend`. Weekend слабее weekday (`avg_phase_rank 1.48` против `2.87`), самая активная будняя UTC-корзина на срезе - `Пересечение Лондон/Нью-Йорк` (`avg_phase_rank 4.30`). Для входов отдельный файл `STAS2_STAS1_ENTRY_PHASE_CONTEXT.csv` считает фазу только по свечам до входа.

Граница: ML/export/training/scorer/target-lock/Optuna/API не запускались. Следующий этап - только `STAS 3 percent ladder and entry/TP validation`, после принятия Stas 2.

## STAS1 Block 1 Locked 2026-07-06

Статус: `STAS1_BLOCK_1_RUN_POOL_LOCKED_NO_ML_NO_OPTUNA`.

Пользователь зафиксировал: первый рабочий блок STAS1 считается собранным и рабочим.

Что умеет Блок 1:

1. запускать прогон по одному дню или диапазону дней;
2. из прогона получать все low-кандидаты входа;
3. сохранять полный набор артефактов: overview PNG, closeup PNG, `BROWSE_BY_DAY/`, CSV, JSON, RU-отчет;
4. менять процент цели движения цены:
   - `+1%` через `run_day_1pct.ps1`;
   - `+0.5%` через `run_day_0p5.ps1`;
   - другое значение через Python-параметр `--target-pct`, если понадобится отдельный wrapper;
5. видеть, что при меньшем проценте обычно закрывается больше сделок и появляется больше кандидатов для review;
6. проверять outcome после полуночи через `-OutcomeLookaheadHours`, не создавая новых входов за пределами выбранного периода.

Граница: Блок 1 - это генератор visual review/outcome-пула. Это не ML/export/training, не scorer, не target-lock, не Optuna и не API.

Следующий чат должен не пересобирать Блок 1, а продолжать от него: чистка шума low, ручной feedback, настройка фильтра значимого low.

## STAS1 Carry Outcome 2026-07-06

Статус: `STAS1_CARRY_OUTCOME_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

STAS1 теперь умеет разделять период входов и период проверки outcome:

1. входы создаются только внутри выбранного `-Day .. -EndDay`;
2. сделки до стартового дня не подтягиваются;
3. новые входы после `-EndDay` не создаются;
4. достижение `+1%` можно проверять после полуночи через `-OutcomeLookaheadHours`;
5. future используется только как offline outcome label, не как сигнал и не как ML-фича.

В `GOOD_1PCT_REVIEW_POOL_RECORDS.csv` добавлены поля `outcome_lookahead_hours`, `outcome_check_end_time_utc`, `hit_day_utc`, `hold_minutes_to_target`, `carried_overnight`, `outcome_status`.

Smoke-run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_smoke_carry48_20260507_20260508_v0_20260706_081637`.

Сводка smoke-run: `2` дня, `148` кандидатов, `80` `GOOD_SAME_DAY`, `68` `GOOD_CARRIED_OVERNIGHT`, хвостов `python.exe` после запуска нет.

Команда для пользовательской проверки:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-07 -EndDay 2026-05-08 -OutcomeLookaheadHours 48 -RunLabel stas1_20260507_20260508_carry48_v0 -RenderGoodLimit 0
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
```

Граница: это review/outcome слой. ML/export/training/scorer/target-lock/Optuna/API не запускались.

## STAS1 Browse By Day 2026-07-06

Статус: `STAS1_BROWSE_BY_DAY_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

По запросу пользователя исправлен порядок просмотра STAS1 run: больше не нужно открывать десятки PNG отдельными окнами. Каждый новый run создает папку:

`BROWSE_BY_DAY/`

Внутри:

1. `00_RUN_INDEX.png` - краткий индекс run по дням;
2. `00_RUN_INDEX_RU.md` - текстовый индекс;
3. отдельная папка на каждый день, например `2026-05-04/`;
4. внутри дня `00_YYYYMMDD_OVERVIEW.png`, затем `01/02/..._ALL_CLOSEUPS_PAGE_*.png` строго по `entry_time_utc`;
5. дневной `YYYYMMDD_RECORDS.csv`.

Команды:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open index
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-04
```

Полный контрольный run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260504_20260506_browse_by_day_v0_20260706_063954`.

Сводка: `202` кандидата, `98` GOOD, `104` BAD, `3` дня обработано. Дневные папки: `2026-05-04`, `2026-05-05`, `2026-05-06`.

Граница: это только визуальный review/outcome слой. ML/export/training/scorer/target-lock/Optuna/API не запускались.

## STAS1 ALL Closeups GOOD+BAD 2026-07-06

Статус: `STAS1_ALL_CLOSEUPS_BAD_X_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

По запросу пользователя в STAS1 добавлен отдельный визуальный слой, где на closeup-страницы попадают все кандидаты, а не только GOOD:

1. `GOOD` остается зеленым треугольником;
2. `BAD` показывается красным полупрозрачным крестом;
3. старые `GOOD_1PCT_REVIEW_POOL_GOOD_CLOSEUPS_PAGE_*.png` сохранены и остаются страницами только хороших входов;
4. новые `GOOD_1PCT_REVIEW_POOL_ALL_CLOSEUPS_PAGE_*.png` нужны для ручной чистки шума и будущих отрицательных примеров;
5. это review-layer, не ML/export/training, не scorer, не target-lock, не Optuna и не API.

Контрольный run `2026-05-03`:

`STAS1_GOOD_LOW_REVIEW/runs/stas1_20260503_all_closeups_bad_x_v0_20260706_060244`

Сводка: `58` кандидатов, `36` GOOD, `22` BAD, `8` страниц ALL closeups.

Открыть последние ALL closeups:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open allcloseups
```

## STAS1 Good Low Review 2026-07-03

Статус: `STAS1_V0_BASELINE_MAIN_LOW_REVIEW_SCRIPT_NO_ML_NO_OPTUNA`.

По решению пользователя текущий основной рабочий контур поиска long low-кандидатов зафиксирован как `STAS1`.

Видная папка:

`STAS1_GOOD_LOW_REVIEW/`

Основной движок остается в исходном коде:

`src/mlbotnav/visual_entry_good_1pct_review_pool.py`

Главная будущая зона калибровки шума:

`src/mlbotnav/visual_entry_low_anchor_suggester.py`

Смысл: не создавать новый скрипт с нуля и не откатываться вслепую, а использовать уже рабочий `GOOD_1PCT_REVIEW_POOL` как baseline. Пользователь будет смотреть 1 день, затем 3-4 дня, отмечать плохие low/дубли/сдвиги, после чего будет калиброваться фильтр значимого low.

Созданы удобные команды:

1. `STAS1_GOOD_LOW_REVIEW/run_day_1pct.ps1`;
2. `STAS1_GOOD_LOW_REVIEW/run_day_0p5.ps1`;
3. `STAS1_GOOD_LOW_REVIEW/open_last_run.ps1`;
4. `STAS1_GOOD_LOW_REVIEW/README_RU.md`;
5. `STAS1_GOOD_LOW_REVIEW/feedback/README_RU.md`;
6. `STAS1_GOOD_LOW_REVIEW/snapshots/README_RU.md`.

Новые `STAS1` runs сохраняются ближе к корню проекта:

`STAS1_GOOD_LOW_REVIEW/runs/`

Граница: это review/outcome-контур. Не ML, не Optuna, не scorer, не target-lock и не API. `+1%`/`+0.5%` являются offline outcome label для глаз, а не causal feature.

## Bybit Hedge Mode Note 2026-07-02

Статус: `HEDGE_MODE_API_NOTE_LOCKED_FUTURE_HEDGE_SIM_NO_REAL_API`.

Зафиксировано для памяти процесса: на Bybit V5 hedge/both-sides режим позволяет держать LONG и SHORT одновременно по одному символу, если позиционный режим переключен в hedge. Для `linear` USDT perpetual рабочая логика API такая: `mode=3`, LONG-ордера идут с `positionIdx=1`, SHORT-ордера с `positionIdx=2`.

Граница: это не текущий торговый запуск, не ML, не scorer, не Optuna и не target-lock. Реальные API-ордера, ключи, изменение настроек аккаунта и боевое подключение не выполнять без отдельного явного решения пользователя.

Как использовать дальше: после `DCA_RISK_AUDIT_V0` можно сделать отдельный симуляционный слой `HEDGE_SIM_V0`, который сравнит перегруженные LONG DCA-корзины с вариантом защитного SHORT-хеджа. До этого hedge остается только risk-идеей, а не входным сигналом.

## Daily 10 Long Trades Target Phase Ladder 2026-07-02

Статус: `DAILY_10_LONG_TRADES_PHASE_LADDER_LOCKED_FOR_DCA_AUDIT_NO_ML_NO_OPTUNA`.

Зафиксировано уточнение пользователя: дневная идея не сводится к одному жесткому `+1%`. Цель процесса - изучить, какие фазы движения реально дает рынок в разные дни и сессии:

1. фаза `0.3-0.5%`;
2. фаза `0.9-1.0%`;
3. фаза `1.5-2.0%`;
4. фаза `2.2-4.0%+`;
5. дополнительные диапазоны добавляются после фактического аудита рынка, дня и сессии.

Рабочая трактовка: `10` сделок в день - это целевой лимит/план по качественным long-входам, но не приказ добирать плохие входы до числа `10`. Для каждого дня нужно отдельно понять, какую фазу он дает: короткий scalp, обычный `1%`, расширенный импульс или сильный трендовый/новостной ход.

Следующий этап `DCA_RISK_AUDIT_V0` должен считать не только hit `+1%`, а лестницу outcome-фаз, время до фазы, просадку, число одновременных входов, сессию и риск DCA-корзины. Это все остается offline outcome/audit, не causal feature для входа.

Граница: ML/export/training, Optuna, scorer, target-lock и реальные API-ордера запрещены.

## DCA Risk And Knife Map Rails 2026-07-02

Статус: `SHORT_RANGE_DCA_RISK_RAILS_LOCKED_NO_ML_NO_OPTUNA`.

Зафиксировано решение: сначала работаем только на коротком диапазоне `W18-W20` (`2026-04-27..2026-05-17`, `21` день), run `W18_W20_learning_20260702_082819`. Полный `126`-дневный прогон откладывается.

Причина: `+1% review-pool` полезен для поиска потенциальных входов, но в нем есть ножи, серии докупок, перегруз DCA-корзин и слабые `SOFT` входы. Эти строки нельзя напрямую считать ML-good.

Следующий этап: `DCA_RISK_AUDIT_V0` на `21` дне. Нужно посчитать DCA-корзины, просадку, число докупок, среднюю цену, время в минусе, поддержку при `10x/20x/50x/100x`, затем разложить входы на классы:

1. `GOOD_CLEAN_RECLAIM`;
2. `GOOD_DCA_SURVIVABLE`;
3. `BORDERLINE_SOFT`;
4. `BAD_FALLING_KNIFE`;
5. `BAD_CLUSTER_OVERLOAD`;
6. `BAD_NO_ROOM`;
7. `REJECT_VISUAL`.

`FULL_HISTORY_KNIFE_MAP_V0` на все доступные дни разрешен только после того, как на коротком диапазоне будут понятны классы, кластеры, визуальные отчеты и баги.

Граница: ML/export/training, Optuna, scorer и target-lock запрещены.

## Fresh Target-Led Low Anchor Entry 1pct Label Review V1 13 May 2026-07-02

Статус: `LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Пункт рельсов: по уточнению пользователя low-свеча считается signal, вход строго на следующей свече, а погрешность для обучения живет только в execution/slippage band: `0bps`, `5bps`, `10bps`.

Правило:

1. `signal_time_utc` = свеча со значимым low;
2. `entry_time_utc` = следующая свеча;
3. `entry_price_0bps` = next open;
4. `entry_price_5bps` = next open + `5bps`;
5. `entry_price_10bps` = next open + `10bps`;
6. target = `entry_price * 1.01`.

Сводка по `SOLUSDT 1m 2026-05-13`:

1. кандидатов: `87`;
2. `GOOD_STRONG_HIT_1PCT_AT_10BPS`: `4`;
3. `GOOD_NORMAL_HIT_1PCT_AT_5BPS`: `0`;
4. `GOOD_SOFT_HIT_1PCT_AT_0BPS`: `1`;
5. `BAD_NO_1PCT_EVEN_0BPS`: `82`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_FULL_DAY_20260513.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513.csv`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513.json`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513_RU.md`.

Граница: это review/dataset-label слой, не ML, не scorer, не target-lock и не Optuna. Future hit/no-hit не использовать как causal feature.

## Fresh Target-Led Low Anchor 1pct Label Review 13 May 2026-07-02

Статус: `LOW_ANCHOR_1PCT_LABEL_REVIEW_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Пункт рельсов: по запросу пользователя для `SOLUSDT 1m 2026-05-13` построен full-day review, где каждый значимый low-anchor кандидат получает offline outcome label по правилу `anchor_low_price * 1.01`.

Сводка:

1. кандидатов: `87`;
2. `GOOD_ANCHOR_1PCT_POTENTIAL`: `8`;
3. `BAD_NO_ANCHOR_1PCT`: `79`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_1pct_label_review_v0_20260513/LOW_ANCHOR_1PCT_LABEL_REVIEW_FULL_DAY_20260513.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_1pct_label_review_v0_20260513/LOW_ANCHOR_1PCT_LABEL_REVIEW_V0_20260513.csv`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_1pct_label_review_v0_20260513/LOW_ANCHOR_1PCT_LABEL_REVIEW_V0_20260513.json`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_1pct_label_review_v0_20260513/LOW_ANCHOR_1PCT_LABEL_REVIEW_V0_20260513_RU.md`.

Граница: future outcome `+1%` используется только как label/audit после low-кандидата. Это не ML, не scorer, не target-lock и не Optuna.

## Fresh Target-Led Low Anchor Suggester 13 May 2026-07-02

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260513_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Пункт рельсов: применен low-anchor suggester к `SOLUSDT 1m 2026-05-13`, чтобы автоматически предложить значимые локальные low для визуального отбора.

Сделано два слоя:

1. полный слой `min_score=2.5`: `87` кандидатов;
2. strict-слой `min_score=5.0`: `18` кандидатов для первого просмотра глазами.

В CSV/JSON для каждой точки зафиксированы `entry_price_plus_5bps` и `target_1pct_price`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0_20260513/`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0_20260513_strict_score5/`.

Граница: это candidate review, не ручной gold-ledger, не scorer, не target-lock, не Optuna и не ML.

## Fresh Target-Led Target 1pct Price Fix V0 2026-07-02

Статус: `TARGET_1PCT_PRICE_FIX_V0_READY_NO_ML_NO_OPTUNA_NO_SCORER`.

Пункт рельсов: для уже подтвержденных ручных эталонов `2026-05-14 M01..M19` и `2026-05-15 T15L confirmed 7` зафиксированы цены цели `+1%` от execution-цены `entry + 5bps`.

Правило: `target_1pct_price = entry_price_plus_5bps * 1.01`.

Сводка:

1. всего входов: `26`;
2. `2026-05-14`: `19` входов, до `+1%` дошли `13/19`;
3. `2026-05-15`: `7` входов, до `+1%` дошли `4/7`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/target_1pct_price_fix_v0/TARGET_1PCT_PRICE_FIX_V0_20260702.csv`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/target_1pct_price_fix_v0/TARGET_1PCT_PRICE_FIX_V0_20260702.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/target_1pct_price_fix_v0/TARGET_1PCT_PRICE_FIX_V0_20260702_RU.md`.

Граница: это не ML, не scorer, не Optuna и не target-lock. Цена `+1%` используется как outcome/reference для ручной базы, а не как признак выбора входа.

## Fresh Target-Led Dataset Base V0 2026-07-01

Статус: `TARGET_LED_DATASET_BASE_V0_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA`.

Пункт рельсов: собрать ручную базу good/reject из уже размеченных `SOLUSDT 1m` дней `2026-05-14` и `2026-05-15`, не запуская ML.

Собрано:

1. `2026-05-14`: `19` good `M01..M19`, `51` reject, `15` unlabeled review;
2. `2026-05-15`: `7` good `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16`, `15` reject;
3. всего строк: `107`;
4. размечено для будущего supervised ML: `92`;
5. good `ml_label=1`: `26`;
6. reject `ml_label=0`: `66`;
7. unlabeled review: `15`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v0/TARGET_LED_DATASET_BASE_V0_20260701.csv`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v0/TARGET_LED_DATASET_BASE_V0_20260701.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v0/TARGET_LED_DATASET_BASE_V0_20260701_RU.md`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v0/TARGET_LED_DATASET_BASE_V0_SUMMARY_20260701.png`.

Блоки для будущего ML:

1. core: `B015`, `B017`, `B010`, `B013`, `B019`, `B020`;
2. context-only: `B014`, `B018`, `B008`, `B024`;
3. blocked as standalone ALLOW: `B009`, `B021`, `B022`, `B023`, `B026`, `B016`, `B025`.

Граница: это dataset base, не ML-export и не обучение. Все признаки считаются на закрытой signal-свече или раньше; entry price сохранен только как execution/control.

## Fresh Target-Led B018 BOS Repeat 14 May 2026-07-01

Статус: `B018_BOS_STRATEGY_REVIEW_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт рельсов: по запросу пользователя отдельно повторен BOS/CHOCH-блок `B018`, без смешивания с остальными паспортами.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_FULL_DAY_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_01_20260514.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_02_20260514.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_03_20260514.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_04_20260514.png`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_ZOOM_PAGE_05_20260514.png`;
7. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_20260514.csv`;
8. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_20260514.json`;
9. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_b018_bos_review/B018_BOS_REVIEW_20260514_RU.md`.

Короткий аудит: за день найдено `41` `BOS_UP`, `42` `BOS_DOWN`, `8` `CHOCH-like`. Это слишком часто для самостоятельного entry-сигнала. Для лонга рабочая интерпретация: не `BOS_DOWN` как вход, а связка `down break -> reclaim/CHOCH -> локальный entry`, либо `BOS_UP` как подтверждение продолжения после уже найденного входа.

Вывод: `B018` оставить как structure-context/evidence. В первый паспорт не брать как одиночный `ALLOW`.

## Fresh Target-Led V2E Summary Matrix 14 May 2026-07-01

Статус: `V2E_SUMMARY_MATRIX_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт рельсов: свести все уже сделанные слои `V2A/V2B/V2C/V2D` по ручному эталону `SOLUSDT 1m 2026-05-14 M01..M19`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_SUMMARY_MATRIX_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_SUMMARY_MATRIX_20260514.csv`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_BLOCK_SUMMARY_20260514.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_SUMMARY_MATRIX_20260514.json`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_summary_v2e/V2E_SUMMARY_MATRIX_20260514_RU.md`.

Короткий аудит:

1. Слишком широкие context-блоки: `B014`, `B018`, `B009`, `B021`, `B022`, `B023`. Они объясняют слишком много входов и не могут быть самостоятельным entry-фильтром.
2. Кандидаты evidence для первого паспорта: `B015`, `B017`, `B010`, `B013`, `B019`, `B020`.
3. `B026_VWAP_DISTANCE` конфликтует `8/19`, поэтому его нельзя брать как простой allow-фильтр.

Следующий подпункт: user review по V2E-скрину, затем выбрать первый рабочий кластер/паспорт-кандидат на 14 мая. Scorer, target-lock, Optuna и ML/export/promotion не запускались и остаются запрещены.

## Fresh Target-Led V2D Pattern 14 May 2026-07-01

Статус: `V2D_PATTERN_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт рельсов: закрываем `SOLUSDT 1m 2026-05-14 M01..M19` по следующему паспортному слою, не переходя на `T15/2026-05-15`.

Сделан pattern-подслой:

1. `B019_CANDLE_PATTERNS`;
2. `B020_DIVERGENCE_PATTERNS`;
3. `B021_PATTERN_QUALITY`;
4. `B022_CHART_PATTERNS`;
5. `B023_PATTERN_CONFIRMATION`;
6. `B024_PATTERN_COMPOSITE_ENTRY`.

`B025_PATTERN_TRADE_CONTEXT` не использовался как active layer.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_FULL_DAY_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_ZOOM_PAGE_01_20260514.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_ZOOM_PAGE_02_20260514.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_ZOOM_PAGE_03_20260514.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_ZOOM_PAGE_04_20260514.png`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_OVERLAY_20260514.json`;
7. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_OVERLAY_20260514.csv`;
8. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns/V2D_PATTERN_OVERLAY_20260514_RU.md`.

Короткий аудит: `B019` support `15/19`, conflict `1/19`; `B020` support `9/19`; `B021` support `19/19`; `B022` support `19/19`; `B023` support `17/19`; `B024` support `16/19`. Значит pattern-слой полезен как evidence, но `B021/B022` слишком широкие и не могут быть самостоятельным фильтром входа.

Следующий подпункт: `V2E_SUMMARY_MATRIX` по 14 мая, где свести `M01..M19 -> V2A/V2B/V2C/V2D support/conflict/silent`. Scorer, target-lock, Optuna и ML/export/promotion не запускались и остаются запрещены.

## Fresh Target-Led V2C ADX/Stochastic 14 May 2026-07-01

Статус: `V2C_ADX_STOCH_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Коррекция пользователя: `RSI`, `MACD` и `EMA` уже смотрели раньше, поэтому на текущем проходе они не повторялись. Вместо них наложен momentum-подслой:

1. `B008_ADX14` / `F016_ADX14_ALLOW`;
2. `B009_STOCH14` / `F017_F018_STOCH14_ALLOW`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_FULL_DAY_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_ZOOM_PAGE_01_20260514.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_ZOOM_PAGE_02_20260514.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_ZOOM_PAGE_03_20260514.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_ZOOM_PAGE_04_20260514.png`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_OVERLAY_20260514.json`;
7. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_OVERLAY_20260514.csv`;
8. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_OVERLAY_20260514_RU.md`.

Короткий аудит: `B008_ADX14` поддержал `16/19`, conflict `1/19`; `B009_STOCH14` поддержал `19/19`, conflict `0/19`. Значит Stochastic в текущей трактовке слишком широкий и не может быть самостоятельным entry-фильтром. ADX тоже скорее режим/контекст силы движения, а не направление.

Правильный следующий подпункт после пользовательского visual review: `V2D_PATTERN_LAYER` на 14 мая (`B019-B024`). `B025` не брать active без отдельного решения. Scorer, target-lock, Optuna и ML/export/promotion не запускались и остаются запрещены.

## Fresh Target-Led V2B Flow/Density 14 May 2026-07-01

Статус: `V2B_FLOW_DENSITY_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Коррекция рельсов: пользователь справедливо остановил преждевременный переход к `T15/2026-05-15`. День `SOLUSDT 1m 2026-05-14 M01..M19` еще не закрыт по всем паспортным блокам, поэтому перенос на 15 мая временно отложен.

Сделан слой `V2B_FLOW_DENSITY_LAYER` для 14 мая:

1. `B010_VOLUME_FLOW`: volume change, volume z-score, delta volume;
2. `B013_DENSITY_VPOC`: VPOC 60/240, bin/share/cluster context, VPOC drift;
3. `B026_VWAP_DISTANCE`: session VWAP distance.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_FULL_DAY_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_ZOOM_PAGE_01_20260514.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_ZOOM_PAGE_02_20260514.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_OVERLAY_20260514.json`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_OVERLAY_20260514.csv`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_OVERLAY_20260514_RU.md`.

Короткий аудит по `M01..M19`: `B010` поддержал `13/19`, `B013` поддержал `12/19`, `B026` поддержал `8/19` и часто конфликтует. Это evidence/context слой, не готовый сигнал.

Правильный следующий подпункт: `V2C_MOMENTUM_LAYER` на 14 мая (`B006 RSI`, `B007 MACD`). `B005 EMA` пока не трогаем как active condition. Scorer, target-lock, Optuna и ML/export/promotion не запускались и остаются запрещены.

## Fresh Target-Led V2A Structure User Review Audit 2026-07-01

Статус: `V2A_STRUCTURE_20260514_VISUAL_AUDIT_DONE_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт рельсов: `V2A_STRUCTURE_LAYER`.

По текущему запросу пользователя “поехали” выполнен короткий visual-аудит уже собранного V2A-слоя по `SOLUSDT 1m 2026-05-14 M01..M19`.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_USER_REVIEW_AUDIT_20260701_RU.md`.

Вывод:

1. `B014_LEVEL_RANGE_CHANNEL` поддерживает `18/19`, поэтому это широкий structural context, не самостоятельный фильтр входа.
2. `B018_MARKET_STRUCTURE` поддерживает `17/19`, поэтому это тоже context/evidence, не `ALLOW`.
3. `B017_BREAKOUT_RETEST` выглядит полезнее для retest/reclaim, но требует локального окна.
4. `B015_FIBONACCI_GRID` полезен точечно, но остается `context_only`, пока нет правила свежести Fibo-ноги.

Эта прежняя строка superseded пользовательской правкой: не переносить `V2A_STRUCTURE_LAYER` на `2026-05-15` как следующий шаг. Сначала закрыть 14 мая по `V2B/V2C/V2D/V2E`. Scorer, target-lock, Optuna и ML/export/promotion остаются запрещены.

## Fresh Target-Led V2A Structure Overlay 14 May 2026-07-01

Статус: `V2A_STRUCTURE_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт рельсов: `V2A_STRUCTURE_LAYER`.

По запросу пользователя “накладывай на графики и показывай мне это 14 день сначала” создан первый strategy/passport overlay для эталона:

```text
SOLUSDT 1m 2026-05-14
ручные входы: M01..M19
```

Наложены только структурные паспортные блоки:

1. `B014 LEVEL/RANGE/CHANNEL`: support/resistance, range position, channel context;
2. `B015 FIBONACCI_GRID`: Fibo по `last_confirmed_alternating_pivot_pair`, не по zoom min/max;
3. `B017 BREAKOUT_RETEST`: breakout/retest event memory;
4. `B018 MARKET_STRUCTURE`: internal/external BOS/CHOCH-like.

`B016 ENTRY_QUALITY_CONTEXT` не включен как active signal, только остается muted/context-only для будущего слоя.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_FULL_DAY_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_01_20260514.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_02_20260514.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514.json`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514.csv`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514_RU.md`.

Скрипт:

```text
src/mlbotnav/visual_entry_strategy_passport_overlay_v2a.py
```

Граница no-lookahead: расчеты заканчиваются на закрытой signal-свече; pivot доступен только после `PIVOT_RIGHT`; entry open и `entry + 5 bps` только execution/control, не feature выбора. Scorer, target-lock, Optuna, ML/export/promotion не запускались.

Проверка с агентом после первого рендера выявила риск: Fibo/BOS могли зависеть от full-day zigzag, собранного до фильтра по `signal`. Исправлено: Fibo/BOS теперь пересобирают zigzag prefix-causal из подтвержденных pivot на момент `signal/event`; `entry_open_price` добавлен в CSV/zoom, заголовки zoom сокращены до `B014/B015/B017/B018`. После фикса 14 мая перерендерен.

После пользовательского замечания “Fibo непонятно откуда и до куда натянута” добавлены отдельные Fibo-anchor страницы:

1. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_FIBO_ANCHORS_PAGE_01_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_FIBO_ANCHORS_PAGE_02_20260514.png`.

На них видны pivot `A`, pivot `B`, линия `A -> B`, direction, signal, entry и уровни сетки. Предварительный вывод: Fibo полезен как контекст, но не должен быть главным сигналом без правила свежести/валидности ноги, потому что часть натяжек далеко от текущего входа.

Следующий шаг superseded: пользовательская правка зафиксировала, что после V2A надо закрывать остальные блоки 14 мая, а не переносить слой на `2026-05-15`.

## Fresh Target-Led Existing Passport Reconciliation 2026-07-01

Статус: `ACTIVE_EXISTING_PASSPORT_RECONCILIATION_AND_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь уточнил: паспорта уже собраны по полочкам, их не нужно создавать заново. Текущий этап — навести порядок в связках и наложить существующие паспорта/стратегии на два эталона.

Подключенный агент `Lorentz` провел read-only аудит:

1. `configs/calibration_action_passports.yaml` содержит `26` блоков `B001..B026`;
2. активных не отключенных `Fxxx` связок: `82`;
3. активных matrix YAML: `82`;
4. у всех активных связок найдены `passport_path` и `active_matrix_path`;
5. `B001_RET_N_TOURNAMENT` является `diagnostic_only_disabled_for_baseline`, в overlay его не брать.

Новый порядок:

1. `V2A0_REGISTRY_RECONCILIATION`: сверить `Bxxx -> Fxxx -> passport MD -> matrix YAML -> runtime action`;
2. `V2A_STRUCTURE_LAYER`: наложить `B014/B015/B017/B018`, а `B016` только muted/context;
3. `V2B_FLOW_DENSITY_LAYER`: `B010/B013/B026`, позже `B011/B012`;
4. `V2C_MOMENTUM_LAYER`: `B006/B007`; `B005` EMA остается reference/deferred;
5. `V2D_PATTERN_LAYER`: `B019-B024` после no-lookahead проверки pattern windows; `B025` не брать active из-за SL/TP риска;
6. `V2E_SUMMARY_MATRIX`: свести `19+7` входов против слоев `structure/flow/momentum/pattern`.

Главный roadmap:
`docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_STRATEGY_PASSPORT_ROADMAP_RU.md`.

Manifest-сверка:
`docs/CALIBRATION_NODE_CURRENT/PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md`.

Активные рельсы обновлены:
`docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_RAILS_RU.md`.

Следующий конкретный шаг superseded: сначала завершить паспортные слои по `M01..M19` за `2026-05-14`; `T15` остается справочным вторым эталоном на потом.

Граница: scorer, target-lock, Optuna, ML/export/promotion запрещены. Ручные входы `19+7` не менять без нового решения пользователя.

## Fresh Target-Led Strategy Passport Gap Audit 2026-07-01

Статус: `STRATEGY_PASSPORT_GAP_AUDIT_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь подтвердил, что `INDICATOR_HYPOTHESIS_REVIEW_V1` визуально норм, но на нем не видно полноценные стратегии и созданные паспорта: `swing`, `BOS`, `Fibonacci`, `volume`, `density/VPOC`, `range/support/retest`.

Аудит показал: текущий V1 является feature/evidence слоем, но не паспортным strategy overlay. В нем есть RSI/MACD/volume и простые визуальные `swing/BOS/Fibo` подсказки, но нет строгих `ALLOW 1/0` по паспортам `F012-F052`, нет matrix `target_id -> passport hits`, и нет читаемого слоя стратегий.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_STRATEGY_PASSPORT_GAP_AUDIT_20260701_RU.md`.

Следующий подпункт: `INDICATOR_HYPOTHESIS_REVIEW_V2_STRATEGY_PASSPORT_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA`.

Граница: те же `M01..M19` и `T15` 7 входов, ручные входы не менять, scorer/target-lock/Optuna/ML не запускать.

## Fresh Target-Led Indicator/Hypothesis Review V1 19+7 2026-07-01

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V1_M01_M19_T15V1_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь указал, что перед паспортом был пропущен отдельный второй слой с фичами/инструментами. Исправление: создан новый evidence-layer `indicator_hypothesis_review_v1`, не поверх эталонных скринов, а отдельным пакетом.

Что вошло:

1. `2026-05-14`: 19 подтвержденных входов `M01..M19`;
2. `2026-05-15`: 7 подтвержденных входов `T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16` из `draft_ledger_v1` с красными правками.

Наложены как evidence, не как готовый сигнал: `RSI14`, `MACD`, volume, volume profile/density, trailing swing low/high, `BOS up/down`, `Fibo` на zoom. EMA остается reference/deferred и не является active condition.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_M01_M19_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_T15_7_20260515.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_ZOOM_T15_7_20260515.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_20260701.json`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_20260701.csv`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_20260701_RU.md`.

`INDICATOR_HYPOTHESIS_REVIEW_V0` считать устаревшим для текущего шага 19+7, потому что он был создан до красных правок `T15` и включал старые `22` T15-кандидата из feedback, а не финальные 7 confirmed. Следующий шаг: пользователь смотрит V1 PNG и дает `норм/фиксить`; только после этого возвращаться к cluster/passport.

## Fresh Target-Led T15 Draft Ledger V1 User Confirmed 2026-07-01

Статус: `T15_DRAFT_LEDGER_V1_USER_CONFIRMED_NEXT_PASSPORT_C01_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь подтвердил `норм` по `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_RED_ARROW_FIX_READY_NO_SCORER_NO_ML_NO_OPTUNA`. Рабочим слоем считать только `draft_ledger_v1`.

Подтвержденные входы `SOLUSDT 1m 2026-05-15`: `T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Следующий пункт рельс: draft passport / паспорт-контракт только по одному кластеру `T15_C01_SUPPORT_RETEST_LOW`: `T15L02`, `T15L08`, `T15L16`.

Граница: это еще не scorer, не target-lock, не Optuna и не ML/export. Цена входа остается execution/control only. EMA не active condition.

## Fresh Target-Led T15 Draft Ledger / Cluster Discussion V1 Red Arrow Fix 2026-07-01

Статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_RED_ARROW_FIX_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт рельсов: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_RED_ARROW_FIX_BEFORE_PASSPORT_NO_ML_NO_OPTUNA`.

По пользовательскому скриншоту с красными стрелками уточнены 3 входа в T15 draft-ledger:

| id | было entry UTC | стало entry UTC |
|---|---:|---:|
| `T15L02` | `02:35` | `02:34` |
| `T15L07` | `06:23` | `06:21` |
| `T15L08` | `08:32` | `08:31` |

Остальные 4 входа без изменения: `T15L06`, `T15L11`, `T15L13`, `T15L16`.

Актуальные 7 входов после правки:

`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701_RU.md`.

`draft_ledger_v0` считать superseded для дальнейшего passport discussion. Граница прежняя: это не target-lock, не scorer, не ML dataset и не Optuna. Следующий шаг: показать пользователю v1 PNG и получить `норм / фиксить`.

## Fresh Target-Led T15 Draft Ledger / Cluster Discussion V0 2026-07-01

Статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт рельсов: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_BEFORE_PASSPORT_NO_ML_NO_OPTUNA`.

После исправленного пользовательского verdict `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA` собран рабочий draft-ledger по 7 входам `SOLUSDT 1m 2026-05-15`:

`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Разложение по черновым кластерам:

| cluster | count | entries | status |
|---|---:|---|---|
| `T15_C01_SUPPORT_RETEST_LOW` | `3` | `T15L02`, `T15L08`, `T15L16` | первый кандидат для passport discussion |
| `T15_C02_DEEP_CAPITULATION_LOW` | `2` | `T15L06`, `T15L13` | второй кандидат |
| `T15_C03_HOT_RECLAIM_CONTINUATION` | `2` | `T15L07`, `T15L11` | наблюдать, не смешивать в первый паспорт |

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701_RU.md`.

Граница: это draft-ledger и discussion-layer, не target-lock, не scorer, не ML dataset и не Optuna. `entry_open_price` и `entry + 5 bps` используются только как execution/control. EMA остается deferred/reference-only. Следующий безопасный шаг: пользователь смотрит PNG и подтверждает `норм / фиксить`; после этого можно делать draft-паспорт только по одному кластеру, первично `T15_C01_SUPPORT_RETEST_LOW`.

## Fresh Target-Led Indicator/Hypothesis Visual Review V0 2026-07-01

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Пункт рельсов: `VISUAL_INDICATOR_HYPOTHESIS_REVIEW_NO_ML_NO_OPTUNA`.

По запросу пользователя создана визуальная лестница проверки для `SOLUSDT 1m` на днях `2026-05-14` и `2026-05-15`: цена/volume, RSI14, MACD, price-density/volume profile, trailing swing low/high, BOS up/down и Fibo-зоны на zoom. Это нужно не для запуска стратегии, а чтобы глазами понять, какие инструменты реально объясняют хорошие входы и какие дают шум.

Итог пакета:

| group | count |
|---|---:|
| `2026-05-14 manual_gold` | `19` |
| `2026-05-15 bad_noise` | `15` |
| `2026-05-15 pending_user_visual_review` | `7` |

Лестница:

1. `L0_PRICE_VOLUME`: свечи, volume, ручные входы.
2. `L1_MOMENTUM`: RSI14 и MACD histogram.
3. `L2_DENSITY`: price-density/volume profile справа на price-панели.
4. `L3_STRUCTURE`: trailing swing low/high и BOS up/down по прошлым 60 барам.
5. `L4_FIBO`: Fibo-зоны на zoom по окну до signal.
6. `L5_DECISION`: ручной verdict пользователя по 7 pending.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260515.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_PENDING_ZOOM_20260515.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_20260701.json`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_20260701.csv`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_20260701_RU.md`.

Граница: это visual evidence pack, не scorer, не target-lock, не ML dataset и не Optuna. EMA остается reference/deferred, не active condition. Entry price только execution/control.

Следующий шаг: пользователь смотрит full-day `2026-05-14`, full-day `2026-05-15` и zoom по 7 pending, затем говорит, какие инструменты оставляем для будущего паспорта, а какие считаем шумом.

Ассистентский визуальный verdict зафиксирован:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_ASSISTANT_VERDICT_20260701_RU.md`.

Короткий итог verdict: RSI, MACD, volume, Fibo и простой local low не отделяют good от bad сами по себе. Основной фильтр должен начинаться со структуры движения, качества low/reclaim и room/path. Приоритет на следующий zoom без ML/Optuna: `T15L06`, `T15L13`, `T15L16`; `T15L02/T15L08` слабее possible, `T15L07` возможно secondary/duplicate, `T15L11` скорее weak/reject.

## Fresh Target-Led T15 Priority Zoom Review V0 2026-07-01

Статус: `T15_PRIORITY_ZOOM_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Пункт рельсов: `T15L06_T15L13_T15L16_PRIORITY_ZOOM_REVIEW_NO_ML_NO_OPTUNA`.

Создан крупный zoom-review по трем приоритетным pending-кандидатам `2026-05-15`: `T15L06`, `T15L13`, `T15L16`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_SHEET_20260515.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L06_PRIORITY_ZOOM_REVIEW_V0_20260515.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L13_PRIORITY_ZOOM_REVIEW_V0_20260515.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L16_PRIORITY_ZOOM_REVIEW_V0_20260515.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_20260701.json`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_20260701_RU.md`;
7. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_ASSISTANT_VERDICT_20260701_RU.md`.

Ассистентский итог: `T15L06` и `T15L16` выглядят как основные gold-кандидаты для пользовательского подтверждения. `T15L13` оставить как `possible_but_not_primary`: low красивый, но продолжение слабее.

Граница: это visual review only. Scorer, target-lock, Optuna и ML/export запрещены.

## Fresh Target-Led T15 User Verdict V1 2026-07-01

Статус: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `T15_USER_VERDICT_ALL_SEVEN_ENTRIES_NO_ML_NO_OPTUNA`.

Коррекция пользователя: “тут 7 должно входов”. Предыдущий `user_verdict_v0`, где было продвинуто только 2 входа, считается superseded и больше не является рабочим слоем.

Актуальная фиксация:

| group | ids |
|---|---|
| `user_confirmed_entry` | `T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16` |
| `bad_noise` | `15` rejected из feedback v2 |

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_FULL_DAY_20260515.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701_RU.md`.

Граница: это ручная фиксация 7 входов, не target-lock, не scorer, не ML dataset и не Optuna. Следующий безопасный шаг: draft-ledger/cluster discussion по всем 7 confirmed entries.

## Fresh Target-Led T15 User Verdict V0 2026-07-01

Статус: `T15_USER_VERDICT_V0_FIXED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `T15_USER_VERDICT_AFTER_PRIORITY_ZOOM_NO_ML_NO_OPTUNA`.

Пользователь подтвердил “норм” после priority zoom review. Зафиксирован отдельный ручной verdict-layer:

| group | ids |
|---|---|
| `gold_candidate_user_confirmed` | `T15L06`, `T15L16` |
| `possible_not_primary` | `T15L13` |
| `weak_not_promoted_after_priority_review` | `T15L02`, `T15L07`, `T15L08`, `T15L11` |
| `bad_noise` | `15` rejected из feedback v2 |

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_FULL_DAY_20260515.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_20260701.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_20260701_RU.md`.

Граница: слой superseded после уточнения пользователя “тут 7 должно входов”. Рабочим считать `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

## Fresh Target-Led Low Anchor Transfer User Feedback 2026-05-15 V2

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V2_FIXED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: `T15L10` тоже крест. Актуальный feedback layer теперь `user_feedback_v2`.

Итог:

| label | count |
|---|---:|
| `bad_noise / user_crossed_out_not_suitable` | `15` |
| `pending_user_visual_review` | `7` |

Rejected:

`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L10`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:

`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Активные артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515_RU.md`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.csv`.

Граница: `pending` не gold. Это актуальный feedback layer, не scorer и не ML dataset. ML/export/Optuna запрещены.

## Fresh Target-Led Low Anchor Transfer User Feedback 2026-05-15 V1

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V1_FIXED_NO_ML_NO_OPTUNA`.

Пользователь прислал дополнительный full-day screenshot и уточнил правый блок: `T15L21` тоже rejected. Актуальный feedback layer теперь `user_feedback_v1`.

Итог:

| label | count |
|---|---:|
| `bad_noise / user_crossed_out_not_suitable` | `14` |
| `pending_user_visual_review` | `8` |

Rejected:

`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:

`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`.

Активные артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515_RU.md`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.csv`.

Граница: `pending` не gold. Это актуальный слой feedback, но не scorer и не ML dataset. ML/export/Optuna запрещены.

## Fresh Target-Led Low Anchor Transfer User Feedback 2026-05-15 V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_TRANSFER_USER_FEEDBACK_NO_ML_NO_OPTUNA`.

Пользователь прислал три скриншота с красными перечеркиваниями по transfer review `T15L01..T15L22` на `SOLUSDT 1m 2026-05-15`.

Зафиксировано:

| label | count |
|---|---:|
| `bad_noise / user_crossed_out_not_suitable` | `13` |
| `pending_user_visual_review` | `9` |

Rejected:

`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L22`.

Pending:

`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`, `T15L21`.

Важно: pending не является gold. Это только неперечеркнутые в текущем feedback кандидаты, которые требуют следующего visual verdict: `норм`, `сдвинуть`, `possible`, `дубль`, `не тот тип` или `нет`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515_RU.md`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.csv`.

Граница: это feedback layer, не scorer и не dataset. ML/export/Optuna запрещены. EMA не active condition.

## Fresh Target-Led Low Anchor Transfer Review 2026-05-15 Compact V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_DAY_20260515_READY_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_TRANSFER_DAY_REVIEW_NO_ML_NO_OPTUNA`.

По запросу пользователя сделан перенос текущего понимания ручных low/reclaim long-входов с seed-day `2026-05-14` на новый день `SOLUSDT 1m 2026-05-15`.

Смысл: это проверка, проявилась ли "учеба" на новом дне. Это не стратегия, не scorer, не Optuna и не ML dataset.

Итог:

| item | value |
|---|---:|
| broad low-anchor candidates | `89` |
| compact transfer review candidates | `22` |
| zoom pages | `2` |

Граница:

- используется только закрытая `signal`-свеча и прошлый контекст;
- LONG entry считается на `open` следующей свечи + `5 bps` только как execution/control;
- `entry`-свеча не используется для выбора;
- future return, TP/SL, MFE/MAE не используются;
- EMA не используется как active condition;
- пользовательский verdict еще не получен, все `T15L##` имеют статус `pending_user_visual_review`.

Активные артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_FULL_DAY_20260515.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_01_20260515.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_02_20260515.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_20260515.json`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_20260515_RU.md`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_20260515.csv`.

Следующий шаг: пользователь смотрит full-day и zoom pages и дает verdict по `T15L##`: `норм`, `нет`, `сдвинуть на N свечей`, `дубль`, `не тот тип`, `оставить possible`.

## Fresh Target-Led Feature Policy EMA Deferred 2026-07-01

Статус: `LOW_ANCHOR_FEATURE_POLICY_EMA_DEFERRED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: EMA пока не трогаем. Рабочие шаблоны/passport/checklist делаем как ранее обсуждали, без EMA как условия входа.

Фиксация:

- `EMA` не использовать как active scorer/passport condition;
- `close_vs_ema20_bps` и `ema20_slope_10_bps` из audit остаются только справочными колонками;
- следующий draft checklist должен строиться на структуре, положении в диапазоне, low/reclaim, объеме, диапазоне и wick закрытой `signal`-свечи;
- отдельное включение EMA возможно только после нового явного решения пользователя.

Граница: это policy-fix, не новый scorer и не ML dataset. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led Low Anchor No-Lookahead Feature Audit V0 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_READY_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_NO_ML_NO_OPTUNA`.

После полного разбора extra auto pool создан audit признаков, видимых до входа. Сравнены:

| group | count |
|---|---:|
| `manual_gold` | `19` |
| `bad_noise` | `51` |
| `manual_shift_review` | `12` |
| `possible_entry` | `3` |

Граница no-lookahead:

- используется закрытая `signal`-свеча и прошлый контекст;
- `entry`-свеча не используется как признак выбора;
- future return, TP/SL, MFE/MAE не используются;
- `entry_price_plus_5bps` хранится только как execution/control;
- это audit, не ML dataset.

Ключевой вывод: локальный low сам по себе не является сигналом входа. Нужны no-lookahead фильтры контекста: структура движения до entry, положение в диапазоне, расстояние до recent high/resistance, качество reclaim, объем/диапазон closed signal candle. EMA после уточнения пользователя остается deferred/reference-only.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.png`.

Следующий безопасный шаг: либо zoom-lock для `manual_shift_review`, либо draft feature checklist/passport для no-lookahead scorer. ML/export/promotion запрещены.

## Fresh Target-Led Low Anchor Extra Auto Feedback Summary 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_COMPLETE_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_NO_ML_NO_OPTUNA`.

Extra auto pool полностью разобран пользователем на `6` страницах: `66` кандидатов больше не являются pending pool.

Итоговые метки:

| label | count |
|---|---:|
| `bad_noise` | `51` |
| `manual_shift_review` | `12` |
| `possible_entry` | `3` |

Итоговые причины:

| reason | count |
|---|---:|
| `bad_noise_shallow_bounce` | `21` |
| `bad_noise_weak_context` | `12` |
| `bad_noise_weak_context_entry_mismatch` | `12` |
| `bad_noise_countertrend_entry` | `6` |
| `auto_entry_not_gold_manual_shift_review` | `12` |
| `possible_entry_one_percent_followthrough` | `3` |

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.csv`.

Граница: summary не является ML dataset. `possible_entry` не gold; `manual_shift_review` не обучающая метка. Следующий безопасный шаг: аудит no-lookahead признаков good/manual vs reject/possible/shift или отдельный zoom-review для `manual_shift_review`.

## Fresh Target-Led Low Anchor Extra Auto Page06 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_ANTI_REVIEW_NO_ML_NO_OPTUNA`.

Пользователь дал verdict по page `06`: это плохие входы не по тренду/против рабочего направления движения.

Зафиксировано:

- `bad_noise`: `6`;
- `review_reason`: `bad_noise_countertrend_entry`;
- кандидаты: `LA080`, `LA081`, `LA082`, `LA083`, `LA084`, `LA085`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.png`.

Граница: countertrend reject является ручной anti-label причиной, не правилом ML/export.

## Fresh Target-Led Low Anchor Extra Auto Page05 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_ANTI_REVIEW_NO_ML_NO_OPTUNA`.

Пользователь дал verdict по page `05`: это слабые и вообще плохие входы; в части мест auto-стрелка входа не совпадает с тем low/свечой, где визуально можно было бы рассматривать вход.

Зафиксировано:

- `bad_noise`: `12`;
- `review_reason`: `bad_noise_weak_context_entry_mismatch`;
- `possible_entry`: `0`;
- `manual_shift_review`: `0`;
- кандидаты: `LA064`, `LA065`, `LA066`, `LA067`, `LA068`, `LA069`, `LA070`, `LA071`, `LA072`, `LA073`, `LA075`, `LA077`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/USER_RED_FEEDBACK_SOURCE_PAGE05_20260701.png`.

Граница: это reject-label, не manual shift. Пользователь назвал входы слабыми/плохими, поэтому новые точки не создавались и current auto-entry не переносились.

## Fresh Target-Led Low Anchor Extra Auto Page04 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_SHIFT_REVIEW_NO_ML_NO_OPTUNA`.

Пользователь красными X и стрелками показал, что текущие auto-entry page `04` не являются готовыми точками входа. Рядом могут быть более удобные ручные свечи/low, но их нужно выносить в отдельный zoom-review и не переписывать автоматически.

Зафиксировано:

- `manual_shift_review`: `12`;
- `review_reason`: `auto_entry_not_gold_manual_shift_review`;
- `possible_entry`: `0`;
- `bad_noise`: `0`;
- кандидаты: `LA042`, `LA044`, `LA045`, `LA046`, `LA048`, `LA052`, `LA054`, `LA055`, `LA056`, `LA057`, `LA059`, `LA062`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/USER_RED_FEEDBACK_SOURCE_PAGE04_20260701.png`.

Граница: `manual_shift_review` не является обучающей меткой и не gold. Это указание, что текущий auto-entry не подходит, а новая ручная точка требует отдельной точной фиксации времени/цены.

## Fresh Target-Led Low Anchor Extra Auto Page03 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_ANTI_REVIEW_NO_ML_NO_OPTUNA`.

Пользователь дал verdict по page `03`: `тут все слабо`.

Чистая формулировка: все входы на странице слабые; локальный low есть, но контекст не дает уверенного рабочего движения. Такие входы визуально не похожи на сделки, в которые стоит заходить.

Зафиксировано:

- `bad_noise`: `12`;
- `review_reason`: `bad_noise_weak_context`;
- `possible_entry`: `0`;
- кандидаты: `LA028`, `LA029`, `LA030`, `LA031`, `LA032`, `LA033`, `LA034`, `LA036`, `LA037`, `LA039`, `LA040`, `LA041`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.png`.

Граница: `bad_noise_weak_context` является manual anti-label, не future-return правилом. Для будущего scorer/ML этот смысл нужно переводить в признаки, доступные до entry.

## Fresh Target-Led Low Anchor Extra Auto Page02 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_ANTI_REVIEW_NO_ML_NO_OPTUNA`.

Пользователь красным выделил кандидаты page `02`, с которыми можно работать: там есть вход и потенциальное движение около одного процента. Остальные кандидаты на странице имеют формальный вход, но визуально не выглядят сделками, в которые стоит заходить.

Зафиксировано:

| label | count | candidates |
|---|---:|---|
| `possible_entry` | `3` | `LA018`, `LA020`, `LA026` |
| `bad_noise` | `9` | остальные кандидаты page `02` |

Причины:

- `possible_entry_one_percent_followthrough`: для `LA018`, `LA020`, `LA026`;
- `bad_noise_shallow_bounce`: для невыделенных кандидатов.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.png`.

Граница: `possible_entry` не является финальным gold-входом. Это кандидаты для отдельного сравнения с ручным эталоном и no-lookahead признаками. ML/export/promotion не запускались.

## Fresh Target-Led Low Anchor Extra Auto Page01 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_ANTI_LABEL_NO_ML_NO_OPTUNA`.

Пользователь подтвердил интерпретацию для первой страницы extra auto review: кандидаты `LA001..LA012` не подходят, потому что это мелкие локальные low без нормального продолжения. После входа цена дает короткий отскок или уходит в шум/стоп, часто без нужного трендового контекста.

Зафиксирован label:

- `review_label`: `bad_noise`;
- `review_reason`: `bad_noise_shallow_bounce`;
- `user_verdict`: `reject`;
- кандидатов: `12`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.png`.

Граница: это manual feedback layer, не ML dataset. Причину `shallow_bounce` нельзя применять как future-return правило выбора; для будущего обучения ее нужно переводить в признаки, видимые до entry.

## Fresh Target-Led Low Anchor Extra Auto Review V1 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_READY_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_ANTI_REVIEW_NO_ML_NO_OPTUNA`.

После resolved label-ledger V1 подготовлен visual review pack для `66` auto-кандидатов, которые не стали подтвержденными ручными `M01..M19`.

Важно: эти `66` кандидатов не являются negative автоматически. Они остаются `pending_user_anti_review` до ручной оценки пользователя.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_01_20260701.png`.

Итог: `66` кандидатов, `6` PNG-страниц по `12` кандидатов. На каждом zoom показаны `entry_time_utc` и `entry_price_plus_5bps` как execution/visual control.

Ручные метки для review: `bad_noise`, `duplicate`, `possible_entry`, `wrong_type`, `ignore_unclear`.

Граница: scorer, Optuna, ML/export/promotion не запускались. Следующий шаг: пользователь смотрит страницу `01` и дает visual verdict по кандидатам.

## Fresh Target-Led Low Anchor Label Ledger V1 Resolved 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_BY_USER_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_NO_ML_NO_OPTUNA`.

Пользователь подтвердил pending review PNG словом `норм`. Цели `M05/M14/M15/M16/M17` переведены из `manual_gold_pending_shift_review` в `manual_gold_user_confirmed_auto_near_ok`; ручные времена ledger не переписывались.

Итоговая разметка `M01..M19`:

| label | count |
|---|---:|
| `manual_gold_exact_auto` | `10` |
| `manual_gold_user_feedback_auto_not_gold` | `4` |
| `manual_gold_user_confirmed_auto_near_ok` | `5` |

Pending shift review: нет.

Candidate labels:

| label | count |
|---|---:|
| `positive_auto_exact_to_manual` | `10` |
| `auto_near_not_gold_user_feedback` | `4` |
| `positive_auto_near_user_confirmed` | `5` |
| `extra_auto_unlabeled_candidate` | `66` |

Resolved label-ledger:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_TARGETS_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_CANDIDATES_20260701.csv`.

Граница: это resolved label-ledger, не ML dataset и не scorer. Следующий безопасный шаг: разобрать `66` extra auto candidates как unlabeled pool для anti-review или подготовить event dataset draft без `APPROVED_FOR_ML`.

## Fresh Target-Led Low Anchor Label Ledger V0 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_READY_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_NO_ML_NO_OPTUNA`.

После пользовательского `норм` по feedback PNG `M03/M09/M10/M11` создан label-ledger для `LOW_ANCHOR_ENTRY_SUGGESTER_V0`.

Итог по `M01..M19`:

| label | count |
|---|---:|
| `manual_gold_exact_auto` | `10` |
| `manual_gold_user_feedback_auto_not_gold` | `4` |
| `manual_gold_pending_shift_review` | `5` |

Оставшиеся цели для ручной проверки сдвига: `M05`, `M14`, `M15`, `M16`, `M17`.

PNG для следующего visual review:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_PENDING_SHIFT_REVIEW_20260701.png`.

Label-ledger:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_TARGETS_20260701.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_CANDIDATES_20260701.csv`.

Граница: это разметочный ledger, не strategy/scorer. `pending_shift_review` нельзя передавать в ML как positive/negative до ручного решения. Optuna/ML/export/promotion не запускались.

## Fresh Target-Led Low Anchor User Feedback M03/M09/M10/M11 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_NO_ML_NO_OPTUNA`.

Пользователь красным отметил на zoom-sheet точки, где авто-кандидат был рядом, но визуально попал не в ту свечу для рабочего эталона: `M03`, `M09`, `M10`, `M11`.

Главная фиксация: `hit_within_3m` теперь считается только `near-review`, а не `gold`. Для будущего event dataset positive остается ручной target-led ledger, если пользователь глазами указал другую свечу.

Зафиксировано:

| target | verdict | auto diff |
|---|---|---:|
| `M03` | `AUTO_LATE_BY_2M_PREFER_LEDGER_SIGNAL_ENTRY` | `+2m` |
| `M09` | `AUTO_LATE_BY_2M_PREFER_LEDGER_SIGNAL_ENTRY` | `+2m` |
| `M10` | `AUTO_EARLY_BY_1M_PREFER_LEDGER_SIGNAL_ENTRY_ANCHOR_REVIEW` | `-1m` |
| `M11` | `AUTO_LATE_BY_2M_PREFER_LEDGER_SIGNAL_ENTRY` | `+2m` |

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.svg`;
5. исходный пользовательский скрин скопирован в `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/USER_RED_FEEDBACK_SOURCE_M03_M09_M10_M11_20260701.png`.

Граница: это visual feedback и подготовка labels для следующей версии/датасета. Scorer, Optuna, ML/export/promotion не запускались.

## Fresh Target-Led Low Anchor Entry Suggester V0 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_SEED_DAY_REVIEW_NO_ML_NO_OPTUNA`.

Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_NO_ML_NO_OPTUNA`.

По решению пользователя создан первый автоматический помощник разметки low-входов: ищет recent local-low anchor, ставит proposed LONG entry на `next open + 5 bps`, считает признаки только на `signal close` или раньше.

Seed-day: `SOLUSDT 1m 2026-05-14`.

Результат V0:

| metric | value |
|---|---:|
| candidates after filter | 85 |
| manual targets M01..M19 | 19 |
| exact signal hits | 10 |
| hits within +/-3m | 19 |
| missed within +/-3m | 0 |

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_full_day_20260514.png`.

Target-nearest zoom sheet:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_target_nearest_zoom_20260514.png`.

Отчет:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514_RU.md`.

Граница: это review-подсказчик и источник будущих positive/anti примеров, не стратегия, не Optuna, не ML/export. Следующий шаг: пользовательский visual review ближайших авто-кандидатов к `M01..M19`: `норм / сдвинуть / нет / дубль / рано / поздно`.

## Fresh Target-Led Data Scope Monthly Visual Samples 2026-07-01

Статус: `SOLUSDT_1M_MONTHLY_FULL_DAY_SAMPLES_CREATED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `DATA_SCOPE_MONTHLY_VISUAL_SAMPLE_126D_NO_ML_NO_OPTUNA`.

По просьбе пользователя сделана контрольная визуальная выгрузка одного full-day графика на каждый доступный месяц `2026` внутри 126-дневного покрытия `SOLUSDT 1m`.

Выбранные дни: `2026-01-27`, `2026-02-28`, `2026-03-28`, `2026-04-28`, `2026-05-28`.

Проверка границ: все выбранные дни имеют `1440` строк, первая свеча открывается в `00:00:00+00:00`, последняя свеча закрывается в `00:00:00+00:00` следующего дня.

Общий PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701.png`.

Отчет:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701_RU.md`.

Граница: это data-scope audit only. Scorer, Optuna, ML/export/promotion не запускались.

## Fresh Target-Led C01 126 Days Source Audit 2026-07-01

Статус: `C01_126_DAYS_SOURCE_AUDIT_COMPLETE_NO_ML_NO_OPTUNA`.

Пункт рельсов: `AUDIT_C01_126_DAYS_SOURCE_SCOPE_NO_ML_NO_OPTUNA`.

Проверено сомнение пользователя по формулировке `126 дней`. Вывод: число `126` реально подтверждается локальными файлами `data/core/bybit_ohlcv/dt=*/tf=1m/symbol=SOLUSDT/part-final.csv`, период `2026-01-26` .. `2026-05-31`, все файлы по `1440` минутных строк.

Важное уточнение: это не MTF и не все рынки. Корректная формулировка только такая: C01 V1 был проверен на `126` локальных днях `SOLUSDT 1m`.

Недофиксация найдена: `C01_MULTI_DAY_CHECK_V1_20260630.json` не содержит top-level `symbol`, `timeframe`, `source_csv_pattern`, диапазон дат и точную команду генерации. Поэтому будущие multi-day артефакты должны обязательно писать manifest источника прямо в JSON.

Артефакты аудита:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_126_DAYS_SOURCE_AUDIT_20260701_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_126_DAYS_SOURCE_AUDIT_20260701.json`.

Граница: C01 V1 остается остановленным, Optuna/ML/export/promotion запрещены.

## Fresh Target-Led C02A Seed-Lock 2026-07-01

Статус: `C02A_TARGET_LOCK_SEED_V0_CREATED_NO_ML_NO_OPTUNA`.

Пункт рельсов: `8.1_SEED_TARGET_LOCK_C02A_AFTER_USER_VISUAL_CONFIRM_NO_ML_NO_OPTUNA`.

Пользователь подтвердил scorer PNG: видим ровно 3 сделки, это нормально. Создан seed-lock для `M01/M02/M08` внутри паспорта `VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0`.

Locked targets:

| target | event | signal UTC | entry UTC | entry open |
|---|---|---:|---:|---:|
| `M01` | `C02E03` | 03:23 | 03:24 | 90.02000000 |
| `M02` | `C02E04` | 03:58 | 03:59 | 89.84000000 |
| `M08` | `C02E10` | 14:07 | 14:08 | 90.60000000 |

Lock-view PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_FULL_DAY_ZOOMS_20260630.png`.

Lock-ledger:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_20260630_RU.md`.

Следующий подпункт: `9.1_MULTI_DAY_BENCH_OR_USER_DECISION_NEXT_PASSPORT_NO_ML_NO_OPTUNA`.

Optuna и ML/export/promotion запрещены.

## Fresh Target-Led C02A Entry-Only Scorer V0 2026-06-30

Статус: `C02A_ENTRY_ONLY_SCORER_V0_SEED_DAY_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Пункт рельсов: `7.1_ENTRY_ONLY_SCORER_C02A_SEED_DAY_NO_ML_NO_OPTUNA`.

После пользовательского `глянул давай далее` по C02A rules V0 построен seed-day entry-only scorer только для ядра `C02A_TRUE_DEEP_CAPITULATION_CORE`. Scorer дал входы только по `C02E03/M01`, `C02E04/M02`, `C02E10/M08`; must-hit `3/3`, нарушений `0`, остальные `13` событий получили `NO_ENTRY`.

PNG для визуального review:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.png`.

Отчет:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_V0_20260630_RU.md`.

Следующий подпункт: `7.1_USER_VISUAL_REVIEW_C02A_ENTRY_ONLY_SCORER_V0_BEFORE_TARGET_LOCK`.

До пользовательского `норм` по PNG запрещены target-lock, multi-day, Optuna и ML/export/promotion.

## Fresh Target-Led C02 Good/Bad Audit 2026-06-30

Статус: `C02_GOOD_BAD_AUDIT_V0_COMPLETE_NO_ML_NO_OPTUNA`.

Выполнен подпункт `C02_AUDIT_GOOD_VS_BAD_AND_DECIDE_SCORER_RULES_NO_ML_NO_OPTUNA`.

Итог: `C02` является широким low-event finder, а не готовым чистым `DEEP_CAPITULATION_LOW` scorer. `c02_score` сам по себе не отделяет хорошие входы от плохих: среди `BAD_ENTRY` тоже есть высокий score. Хорошие события включают не только `M01/M02/M08`, но и точки около `SUPPORT_RETEST_LOW`, `SWING_LOW_RECLAIM`, `HOT_RECLAIM_SUPPORT`.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630_RU.md`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_FULL_DAY_AUDIT_V0_20260630.png`.

Следующий подпункт по рельсам: `C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`. Scorer, target-lock, multi-day, Optuna и ML/export/promotion пока запрещены.

## Fresh Target-Led C02 User Labels Complete 2026-06-30

Статус: `C02_CANDIDATE_REVIEW_V0_USER_LABELS_COMPLETE_NO_ML_NO_OPTUNA`.

Выполнен подпункт `6.1 USER_REVIEW_C02_CANDIDATE_LAYER_V0_FULL_DAY`: пользователь вручную разметил `C02E01..C02E16`.

Итог:

- `GOOD_ENTRY`: `C02E03`, `C02E04`, `C02E05`, `C02E06`, `C02E07`, `C02E08`, `C02E09`, `C02E10`, `C02E11`, `C02E12`;
- `BAD_ENTRY`: `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`;
- seed targets `M01/M02/M08` сохранены как хорошие C02-кандидаты.

Контрольный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_USER_LABELED_GOOD_BAD_SHEET_20260630.png`.

Следующий подпункт по рельсам: `C02_AUDIT_GOOD_VS_BAD_AND_DECIDE_SCORER_RULES_NO_ML_NO_OPTUNA`. Не запускать scorer, Optuna, ML/export/promotion и multi-day до аудита отличий good/bad.

## Fresh Target-Led Passport Bench V0 Step Plan 2026-06-30

Статус: `C02_CANDIDATE_REVIEW_PACK_READY_WAIT_USER_LABELS_NO_ML_NO_OPTUNA`.

Расписана рабочая лестница с подпунктами:
`матрица -> один тип -> паспорт -> no-lookahead кандидаты -> full-day скрин -> ручная target-led разметка -> scorer -> lock/stop/split`.

Созданы артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_BENCH_V0_STEP_PLAN_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630.json`.

Выполнены подпункты: `1.1 PASSPORT_COVERAGE_MATRIX_V0`, `2.2 Подготовить рабочую папку C02`, `3.1 Создать паспорт-драфт C02`, `4.1 Сделать широкий кандидатный слой C02`, `5.1 Сделать full-day seed PNG C02`, `5.2 Сделать zoom как доп-проверку`.

Создан паспорт-драфт:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/passport_VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0_RU.md`.

Candidate layer V0: `96` raw-кандидатов, `16` event representatives, `M01/M02/M08` пойманы как representatives.

Full-day PNG для review:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_full_day_review_20260630.png`.

Zoom review sheet:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_zoom_sheet_C02E01_C02E16_20260630.png`.

Следующий подпункт: `USER_LABEL_C02E01_C02E16`. Нужно разметить события `GOOD_ENTRY / BAD_ENTRY / WRONG_TYPE / LATE_DUPLICATE / NEEDS_SHIFT`. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led Passport Bench Stage 2026-06-30

Статус: `PASSPORT_BENCH_V0_STRUCTURED_NO_ML_NO_OPTUNA`.

После обсуждения последних решений и read-only проверки паспортов зафиксировано: общий вывод по всему fresh target-led подходу делать нельзя. Реально применен только один узкий паспорт `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0` по `M05/M06`; он остановлен как слабое направление, но остальные типы `M01..M19` паспортами еще не покрыты.

Новый правильный этап: `PASSPORT_BENCH_V0_NO_ML_NO_OPTUNA` — паспортный стенд по всем типам входа, без Optuna и без ML.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/process_audit/PASSPORT_BENCH_STAGE_AUDIT_20260630_RU.md`.

Следующий конкретный шаг: создать `PASSPORT_COVERAGE_MATRIX_V0` и начать новый паспорт `C02_DEEP_CAPITULATION_LOW` по `M01/M02/M08`; `C01_QUALITY_FILTER_V2` не считать главным следующим путем.

## Fresh Target-Led C01 V1 Stop Decision 2026-06-30

Статус: `C01_V1_STOPPED_TOO_FEW_AND_LOW_QUALITY_NO_ML_NO_OPTUNA`.

Пользовательский вывод после raw multi-day проверки: текущий `C01 V1` дает слишком мало сделок, а найденные входы визуально часто плохие. Ветку нельзя продвигать как рабочую стратегию.

Проверено: явного ограничения `max_trades_per_day`, `daily_cap`, `cooldown` или `top-N` в C01 V1 нет. `max_candidates_per_day=2` является статистикой результата на 126 локальных днях, а не лимитом.

Решение: `C01 V1` остановлен как направление для продвижения. Не запускать Optuna/ML/export/promotion. Не считать `2/2` на seed-дне достаточным успехом.

Аудит решения:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_V1_STOP_DECISION_20260630_RU.md`.

Следующий рабочий путь по рельсам: не дожимать узкий C01, а собрать более широкий target-led кандидатный слой по всем `M01..M19`, показать full-day PNG на реальной шкале времени и руками отметить `годится / не годится / отдельный тип`.

## Fresh Target-Led C01 Multi-Day Check V1 2026-06-30

Статус: `C01_MULTI_DAY_CHECK_V1_RAW_NEEDS_VISUAL_TUNING_NO_ML`.

Пункт по рельсам: собрать данные для входа в сделку по C01 V1 и проверить, попадаем ли так же красиво на других днях.

Создан контракт входных данных:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_ENTRY_INPUT_CONTRACT_V1_20260630_RU.md`.

Проверка без донастройки на доступных `SOLUSDT 1m` данных:

| metric | value |
|---|---:|
| days_checked | 126 |
| total_candidates | 25 |
| days_with_candidates | 23 |
| max_candidates_per_day | 2 |
| avg_candidates_per_day | 0.1984 |

Вывод: V1 не дает кашу по частоте, но визуальное качество смешанное. Часть кандидатов похожа на C01, часть стоит в продолжающемся снижении. До реального торгового входа нужен ручной `C01_QUALITY_FILTER_V2`.

Zoom contact sheet:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_MULTI_DAY_CHECK_V1_all_candidates_zoom_contact_20260630.png`.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_MULTI_DAY_CHECK_V1_AUDIT_20260630_RU.md`.

Граница: это не trade-ready, не production target-lock и не разрешение на Optuna/ML/export/promotion. Следующий пункт: показать пользователю zoom-кандидаты и руками отметить `годится / не годится / отдельный тип`.

## Fresh Target-Led C01 Target-Lock Seed V1 2026-06-30

Статус: `C01_TARGET_LOCK_SEED_V1_CREATED_NO_ML_NO_OPTUNA`.

Пользователь дал `далее поехали по рельсам` после PNG V1; это принято как визуальное подтверждение `C01_ENTRY_ONLY_SCORER_V1`.

Создан seed target-lock для `M05/M06`: следующие версии C01 не имеют права потерять или сдвинуть эти входы без отдельного решения пользователя.

Locked targets:

| target | signal UTC | entry UTC | branch V1 |
|---|---:|---:|---|
| M05 | 10:43 | 10:44 | red_absorption_low_volume |
| M06 | 12:00 | 12:01 | green_reclaim_volume_spike |

Lock-ledger:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_20260630_RU.md`.

PNG lock-view:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_full_day_M05_M06_20260630.png`.

Граница: это seed target-lock, не production target-lock, не multi-day pass и не разрешение на Optuna/ML/export/promotion. Следующий пункт по рельсам: multi-day проверка C01 или отдельное решение перейти к следующему target-led паспорту.

## Fresh Target-Led C01 Entry-Only Scorer V1 2026-06-30

Статус: `C01_ENTRY_ONLY_SCORER_V1_SAME_DAY_PASS_NOT_TARGET_LOCK_NO_ML`.

После пользовательского `норм` по скрину `M05` сдвинута и подтверждена как signal `10:43 UTC` -> entry `10:44 UTC`; `M06` без изменений: signal `12:00 UTC` -> entry `12:01 UTC`.

Пересчитан entry-only scorer V1 внутри паспорта `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0`.

Результат на `SOLUSDT 1m 2026-05-14`: `M05` и `M06` пойманы, обязательных пропусков `0`, ложных кандидатов `0`, `M12` не сработала и остается observe-only.

PNG V1:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_full_day_M05_M06_zoom_20260630.png`.

JSON V1:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_20260630.json`.

Аудит V1:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_AUDIT_20260630_RU.md`.

Граница: это same-day pass, не target-lock. Следующий пункт по рельсам: показать PNG V1 пользователю; если визуально норм, фиксировать `USER_VISUAL_CONFIRMED_SCORER_V1`, затем выбирать multi-day проверку или следующий target-led паспорт. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led C01 M05 Shift Right 2026-06-30

Статус: `C01_M05_SHIFTED_RIGHT_ONE_CANDLE_EYE_CHECK_READY_SCORER_NEEDS_RECHECK_NO_ML`.

Пользователь уточнил `M05`: сдвинуть на одну свечу вправо, остальное оставить без изменений.

Актуальная фиксация C01:

| target | signal UTC | entry UTC | entry open | entry + 5 bps |
|---|---:|---:|---:|---:|
| M05 | 10:43 | 10:44 | 90.66000000 | 90.70533000 |
| M06 | 12:00 | 12:01 | 90.60000000 | 90.64530000 |

Новый PNG для проверки глазами:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_eye_check_M05_shift_right_full_day_M05_M06_zoom_20260630.png`.

Новый manifest:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_eye_check_M05_shift_right_full_day_M05_M06_zoom_20260630.json`.

Старый `C01_ENTRY_ONLY_SCORER_V0` помечен как stale, потому что был построен до ручного сдвига `M05`. Следующий пункт по рельсам после визуального подтверждения: пересчитать entry-only scorer под актуальную `M05 10:43 -> 10:44` и `M06 12:00 -> 12:01`; Optuna/ML/export/promotion запрещены.

## Fresh Target-Led C01 Entry-Only Scorer V0 2026-06-30

Статус: `STALE_AFTER_USER_SHIFT_M05_RIGHT_ONE_CANDLE_NEEDS_RECHECK_NO_ML`.

Взят пункт по рельсам: `C01_ENTRY_ONLY_SCORER_V0`.

Собран entry-only scorer для первого паспорта `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0`, кластер `C01 HOT_RECLAIM_SUPPORT`, цели `M05/M06`, `M12` только observe-only.

PNG для пользователя:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_full_day_overlay_20260630.png`.

Точный eye-check PNG для решения глазами:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_eye_check_full_day_M05_M06_zoom_20260630.png`.

JSON scorer:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_20260630.json`.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_AUDIT_20260630_RU.md`.

Результат старого V0 больше не считается актуальным проходом после ручного сдвига `M05`; нужен пересчет.

Граница: Optuna/ML/export/promotion запрещены. Следующий шаг: показать PNG пользователю; если визуально норм, фиксировать пользовательское подтверждение и переходить к следующему target-led шагу без старых V7/V8/V9/V10/V11 как очереди задач.

## Fresh Target-Led Rails Package 2026-06-30

Статус: `FRESH_TARGET_LED_RAILS_PACKAGE_M01_M19_C01_READY_NO_ML`.

Собран чистый рабочий навигатор по текущим рельсам fresh target-led процесса:
`reports/final_review/visual_entry_v3/fresh_target_led/FRESH_TARGET_LED_RAILS_PACKAGE_20260630_RU.md`.

Главный эталон для дальнейшей работы:
`reports/final_review/visual_entry_v3/fresh_target_led/reference_visual/REFERENCE_M01_M19_CONFIRMED_ENTRIES_FULL_DAY_SOLUSDT_1m_2026-05-14.png`.

В навигаторе закреплены: день `SOLUSDT 1m 2026-05-14`, 19 ручных входов `M01..M19`, расклад по типам, контракт входа, запреты, первый кластер `C01 HOT_RECLAIM_SUPPORT`, паспорт `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0`.

Следующий практический шаг: работать только с `C01` (`M05`, `M06`) как первым паспортным типом, `M12` держать observe-only, Optuna/ML/export/promotion не запускать.

## Fresh Target-Led C01 Visual Audit 2026-06-30

Статус: `C01_VISUAL_POINT_AUDIT_DONE_NEEDS_USER_CLUSTER_CONFIRM_NO_ML`.

Взят пункт по рельсам: первый паспортный кластер `C01 HOT_RECLAIM_SUPPORT`, целевые входы `M05`, `M06`, `M12` только observe-only.

Контрольный PNG для пользователя:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/visual_audit/C01_M05_M06_control_full_day_and_zoom_20260630_v2.png`.

Аудит пункта:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/visual_audit/C01_M05_M06_POINT_AUDIT_20260630_RU.md`.

Итог: `M05/M06` визуально образуют первый маленький кластер `HOT_RECLAIM_SUPPORT`, но паспорт остается draft до короткого пользовательского подтверждения кластера. Optuna/ML/export/promotion не запускать.

## Fresh Target-Led C01 User Confirmed 2026-06-30

Статус: `C01_USER_CLUSTER_CONFIRMED_NO_ML_NO_OPTUNA`.

Пользователь подтвердил контрольный скрин `C01 HOT_RECLAIM_SUPPORT` с точками `M05`, `M06`. Паспорт `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0` обновлен до статуса `USER_CLUSTER_CONFIRMED_NO_ML_NO_OPTUNA`.

Граница: это подтверждение первого кластера, но еще не target-lock. `M12` остается observe-only. Следующий шаг по рельсам: формализовать entry-only scorer под `M05/M06`, не запускать Optuna/ML/export/promotion.

## Fresh Target-Led Execution Prices M01-M19 2026-06-30

Статус: `M01_M19_EXECUTION_PRICES_FILLED_NO_ML_NO_OPTUNA`.

Для всех ручных входов `M01..M19` добавлены цены исполнения по контракту: `entry_open_price` свечи `entry_time_utc` и `entry_price_with_slippage` для LONG с `5 bps`.

Таблица цен:
`reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19_EXECUTION_PRICES_RU.md`.

Target ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json`.

Граница: эти цены являются только исполнением после выбранного сигнала. Их запрещено использовать для выбора входа, scorer, Optuna или ML-признаков.

## Fresh Target-Led Execution Prices Coverage Fixed 2026-06-30

Статус: `M01_M19_EXECUTION_PRICE_COVERAGE_ALL_CURRENT_SOURCES_PASS_NO_ML`.

Исправлен недочет: цены исполнения были внесены не во все текущие M-источники. Теперь `execution_price` есть во всех 19 точках в:

1. `target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json`;
2. `user_marked_development_order_20260514.json`;
3. `REFERENCE_M01_M19_CONFIRMED_ENTRIES_FULL_DAY_SOLUSDT_1m_2026-05-14.json`.

QA coverage:
`reports/qa_gate/fresh_target_led_m01_m19_execution_price_coverage_20260630.json`.

Проверка: `19/19` в каждом текущем источнике, расхождений по `entry_open` нет. Цены остаются только механикой исполнения, не признаком для выбора входа.

## Fresh Target-Led Execution Price Visual 2026-06-30

Статус: `M01_M19_EXECUTION_PRICE_VISUAL_READY_NO_ML_NO_OPTUNA`.

Сделан full-day график, где для каждой точки `M01..M19` показан маркер входа, `entry open` и расчетная цена исполнения `entry open + 5 bps`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/execution_price_visual/M01_M19_execution_prices_full_day_20260630.png`.

Manifest:
`reports/final_review/visual_entry_v3/fresh_target_led/execution_price_visual/M01_M19_execution_prices_full_day_20260630.json`.

Граница: график показывает только цену исполнения после выбранного `entry_time_utc`; цена не используется как сигнал и не участвует в выборе входа.
## Visual Entry TARGET_LOCKED_STRATEGY_TZ 2026-06-29

Статус: `TARGET_LOCKED_STRATEGY_TZ_READY_NO_ML`.

Полный аудит и ТЗ: `reports/final_review/visual_entry_v3/target_locked_strategy_tz/visual_entry_target_locked_strategy_audit_and_tz_20260629_RU.md`.

Активное ТЗ: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_TARGET_LOCK_TZ_RU.md`.

Главный вывод: V9 ловил больше пользовательских стрелок, но давал шум; V10 стал чище, но потерял хорошие входы. Дальше нельзя улучшать слой без `target-lock`.

Следующий обязательный шаг: создать `target_lock_ledger` и lock-файл по целям `2026-05-13`/`2026-05-14`, затем делать `V11_RECOVER_RANKED_MISSES`.

Правило: если новая версия теряет locked target, это regression `REGRESSION_LOST_LOCKED_TARGET_NO_ML`, а не улучшение.

## Visual Entry EVENT_RANKED_BRICKS_V10 2026-06-29

Статус: `EVENT_RANKED_BRICKS_V10_CLEANER_BUT_PARTIAL_NO_ML`.

Добавлен runner: `src/mlbotnav/visual_entry_event_ranked_bricks_v10_runner.py`.

Тест: `tests/test_visual_entry_event_ranked_bricks_v10_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/event_ranked_bricks_v10/visual_entry_event_ranked_bricks_v10_audit_20260629T182810Z_RU.md`.

V10 добавил low-cluster rank поверх V9: внутри `low_event_start_idx` дополнительно учитывается `event_low_idx`, чтобы не схлопывать несколько реальных днов в одном большом событии.

Validation `2026-05-13`: `V10_01_HOT_CHAIN_EVENT_LOW_RANKED` дал `1/9`, `0` false, поймал `08:48`. Остальные ranked-кирпичи на validation остаются false-only.

Holdout `2026-05-14`: `V10_03_WARM_EVENT_RANKED` дал `3/17`, `6` false; `V10_02_HOT_FIRST_EVENT_RANKED` дал `2/17`, `7` false; `V10_04_DEEP_TERMINAL_EVENT_RANKED` дал `3/17`, `20` false. Ranked union дал `7/17`, `33` false.

Вывод: V10 стал чище V9, но потерял часть нужных входов. В ML ничего не передавать. Следующий шаг: `V11_RECOVER_RANKED_MISSES` - вернуть потерянные `warm/hot/deep` входы отдельными подрежимами без возврата шумного union.

## Visual Entry BRICK_BY_BRICK_SELECTOR_V9 2026-06-29

Статус: `BRICK_BY_BRICK_SELECTOR_V9_PARTIAL_DIAGNOSTIC_NO_ML`.

Добавлен runner: `src/mlbotnav/visual_entry_brick_by_brick_selector_v9_runner.py`.

Тест: `tests/test_visual_entry_brick_by_brick_selector_v9_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9/visual_entry_brick_by_brick_selector_v9_audit_20260629T180726Z_RU.md`.

Validation `2026-05-13`: `V9_01_HOT_CHAIN_EVENT_LOW_BRICK` дал `1/9`, `0` false, `1` entry, precision `1.0`, f1 `0.2000`; пойман вход `08:48`. Это чистый, но узкий кирпич.

Holdout `2026-05-14`: лучший отдельный слой `V9_03_WARM_STRUCTURAL_RECLAIM_BRICK` дал `5/17`, `16` false, `21` entry, f1 `0.2632`; `V9_02_HOT_FIRST_STRONG_RECLAIM_BRICK` дал `4/17`, `20` false; `V9_04_DEEP_TERMINAL_RECLAIM_BRICK` дал `4/17`, `33` false.

Диагностический union `V9_90_RESEARCH_UNION_ALL_BRICKS_DIAG` на holdout дал `12/17`, но `68` false. Его не использовать как стратегию.

Вывод: V9 подтвердил правильное направление "кирпичами", но готового ML-кандидата нет. В ML ничего не передавать. Следующий шаг: `V10_EVENT_RANKED_BRICKS` - внутри каждого low-event выбирать один лучший сигнал и отдельно разделить `warm`, `hot-first`, `deep`.

## Visual Entry NEGATIVE_CONTEXT_SUPPRESSION_V8 2026-06-29

Статус: `NEGATIVE_CONTEXT_SUPPRESSION_V8_PARTIAL_BRICK_NO_ML`.

Добавлен runner: `src/mlbotnav/visual_entry_negative_context_suppression_v8_runner.py`.

Тест: `tests/test_visual_entry_negative_context_suppression_v8_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/negative_context_suppression_v8/visual_entry_negative_context_suppression_v8_audit_20260629T173500Z_RU.md`.

Validation `2026-05-13`: `V8_02_HOT_CHAIN_EVENT_LOW_SUPPRESSION` дал `1/9`, `0` false, `1` entry, precision `1.0`, f1 `0.2000`. Это чистый кирпич для цели `08:48`, но не стратегия из-за низкого recall.

Holdout `2026-05-14`: `V8_01_HOT_FIRST_NEGATIVE_SUPPRESSION` дал `4/17`, `29` false, `33` entries, f1 `0.1600`; union дал `11/17`, но `168` false. Union не использовать.

Добавлены NCS-фильтры: `SIDEWAYS_MICRO_LOW`, `HOT_UPPER_SHELF`, `RETEST_SERIES_SATURATION`, `POST_IMPULSE_NO_PULLBACK`, `WEAK_RECLAIM_NO_LOCAL_LOW`.

Вывод: V8 улучшил шум и дал первый чистый кирпич, но в ML ничего не передавать. Следующий шаг: `V9_BRICK_BY_BRICK_SELECTOR`, то есть собирать отдельные чистые кирпичи, а не общий noisy union.

## Visual Entry GENERALIZATION_V7 2026-06-29

Статус: `GENERALIZATION_V7_DIAGNOSTIC_FAIL_NO_ML`.

Добавлен диагностический runner: `src/mlbotnav/visual_entry_generalization_v7_runner.py`.

Тест: `tests/test_visual_entry_generalization_v7_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/generalization_v7/visual_entry_generalization_v7_audit_20260629T172000Z_RU.md`.

Validation `2026-05-13`: лучший режим `G7_02_HOT_CHAIN_DIP_DIAG` дал `1/9` hit, `22` false, `23` entries, f1 `0.0625`. `G7_01_HOT_FIRST_RECLAIM_DIAG` поймал `00:18`, `G7_02` поймал `08:48`, но остальные цели не закрыты.

Holdout `2026-05-14`: лучший по f1 `G7_01_HOT_FIRST_RECLAIM_DIAG` дал `4/17` hits, `43` false, `47` entries, f1 `0.1250`; union дал `11/17`, но `203` false.

Вывод: V7 полезен как карта режимов, но не стратегия. В ML ничего не передавать. Следующий слой: `NEGATIVE_CONTEXT_SUPPRESSION_V8`, где цель не расширять recall, а подавить боковые микролои, горячие верхние полки и повторные ложные retest-серии.

## Visual Entry manual bottoms validation/holdout 2026-06-25
Статус: `MANUAL_BOTTOMS_EXTRACTED_AUTO_KNIFE_SUGGESTED_CP06_EMPTY_NO_ML`.

По пользовательским PNG созданы воспроизводимые разметки:
1. `2026-05-13` validation: `reports/manual_entries/SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms/manual_entries.json`, `9` ручных входов.
2. `2026-05-14` holdout: `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms/manual_entries.json`, `17` ручных входов.

Контрольные PNG:
1. `reports/manual_entries/SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms/visual_entry_manual_auto_overlay_2026-05-13_20260625T155345Z.png`.
2. `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms/visual_entry_manual_auto_overlay_2026-05-14_20260625T155345Z.png`.

Сводный аудит: `reports/final_review/visual_entry_v3/marked_validation_holdout_user_bottoms/visual_entry_marked_validation_holdout_audit_20260625_RU.md`.

Правило входа зафиксировано: ручная красная метка `S#` = закрытая сигнальная свеча дна/провала, зеленая `E#` = LONG на `open` следующей свечи с `5 bps` slippage. Голубые `AK#` являются только авто-подсказками по сильным knife-drop/провалам и не являются обучающими метками.

CP06 `CP06_CP01_RECOVER_NOWICK_LATE_RETEST` прогнан на `2026-05-13` и `2026-05-14` без подкрутки и дал пустой результат на обоих днях: `best=[]`, `rendered=[]`. Отчеты:
1. `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority_validation_holdout/visual_entry_noise_suppression_cluster_priority_20260513_VALIDATION_DAY_RU.md`.
2. `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority_validation_holdout/visual_entry_noise_suppression_cluster_priority_20260514_HOLDOUT_DAY_RU.md`.

Вывод: текущая DEV-12 механика CP06 не обобщилась на новые ручные дни. В ML ничего не передавать. Следующий шаг: строить новый слой `REVERSAL_BOTTOM_KNIFE_DROP_V0` по этим меткам, с разделением context/trigger/confirm/suppress и обязательными PNG.

Проверки: `py_compile PASS`; `tests.test_visual_entry_marked_png_to_manual_entries`, `tests.test_visual_entry_deep_capitulation_reclaim_runner`, `tests.test_visual_entry_noise_suppression_cluster_priority_runner` = `6/6 OK`; `text_guard PASS` `reports/qa_gate/recovery_r5_text_guard_20260625T155616Z.json`; живых `python.exe` процессов по `MLbotNav/mlbotnav/APTuna/visual_entry` не осталось.

## Visual Entry CP06 validation/holdout readiness 2026-06-25
Статус: `NEEDS_MANUAL_LABELS_NO_VALIDATION_RUN`.

CP06 `CP06_CP01_RECOVER_NOWICK_LATE_RETEST` остается закрытым только на DEV `2026-05-12`: `11/11`, `28` false, `39` entries, `precision=0.2821`, `recall=1.0000`, `f1=0.4400`.

Проверка `2026-05-13` validation и `2026-05-14` holdout без подкрутки пока не запускалась, потому что готовые `manual_entries.json` существуют только для `2026-05-12`. Для `2026-05-13` и `2026-05-14` есть seed PNG/JSON и core CSV, но нет ручных `entries[].target_entry_time_utc`.

Readiness-аудит: `reports/final_review/visual_entry_v3/cp06_validation_holdout_readiness/cp06_validation_holdout_readiness_20260625_RU.md`.

Seed PNG для ручной разметки:
1. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.png`;
2. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.png`.

Граница: не считать отсутствие validation/holdout прогоном ошибкой CP06. Не подбирать параметры на `2026-05-13`/`2026-05-14`, пока эти дни остаются validation/holdout. В ML ничего не передавать.

## Visual Entry v3 DEEP_CAPITULATION_RECLAIM diagnostic 2026-06-25
Статус: `DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML`.

Добавлен runner: `src/mlbotnav/visual_entry_deep_capitulation_reclaim_runner.py`.

Тест: `tests/test_visual_entry_deep_capitulation_reclaim_runner.py`.

Главный аудит: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_audit_20260625_RU.md`.

Главный отчет: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_20260512_DEV_RU.md`.

Лучший рабочий ensemble `DQ01_EQ01_PLUS_DEEP_RECLAIM`: `10/11` hit, `1` miss, `73` false, `83` entries, `precision=0.1205`, `recall=0.9091`, `f1=0.2128`. Поймал `01:42`, `05:13`, `07:16`, `09:30`, `11:38`, `12:33`, `15:26`, `15:47`, `16:01`, `17:00`; пропустил только `08:26`.

High-recall diagnostic `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP`: `11/11`, но `95` false, поэтому это не кандидат.

Новые подсемейства:
1. `D01_DEEP_CAPITULATION_ABSORB_CD20` ловит `12:33`.
2. `D02_TERMINAL_EXHAUSTION_STALL_CD20` ловит `15:26`.
3. `D03_LATE_RETEST_PROBE_CD15` ловит `17:00` без false на DEV-дне.

Решение: слой полезен как карта механик, но в ML ничего не передавать. Следующий шаг: `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`, чтобы резать ложные входы и не полагаться на high-recall no-wick режим для `08:26`.

## Visual Entry v3 EARLY_FLUSH_REVERSAL diagnostic 2026-06-25
Статус: `DEV_EARLY_FLUSH_REVERSAL_DIAGNOSTIC_NO_ML`.

Добавлен runner: `src/mlbotnav/visual_entry_early_flush_runner.py`.

Тест: `tests/test_visual_entry_early_flush_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_audit_20260625_RU.md`.

Отчеты:
1. `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_20260512_DEV.json`;
2. `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_20260512_DEV_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_family_overlay_2026-05-12_early_flush_01_eq01_q09_severe_soft45_20260625T134923Z.png`.

Лучший общий результат `EQ01_Q09_SEVERE_SOFT45`: `7/11` попаданий, `4` пропуска, `68` ложных входов, `75` входов всего, `precision=0.0933`, `recall=0.6364`, `f1=0.1628`. Пойманы `01:42`, `05:13`, `07:16`, `09:30`, `11:38`, `15:47`, `16:01`.

Отдельный `E01_SEVERE_FLUSH_LOCKOUT20` важен как чистый кирпич: `1/11` попадание при `2` ложных входах, поймал `01:42`.

`EQ03_Q09_SEVERE_SOFT45_NOWICK` поймал `8/11`, включая все ранние `01:42`, `05:13`, `07:16`, `08:26`, но дал `90` ложных входов. Это диагностический максимум recall, не кандидат.

Вывод: ранние входы подтверждены как отдельная группа механик, но шум все еще большой. В ML ничего не передавать. Следующий слой: `DEEP_CAPITULATION_RECLAIM` для `12:33`, `15:26`, `17:00`.

## Visual Entry v3 quality filter diagnostic 2026-06-25
Статус: `DEV_QUALITY_FILTER_DIAGNOSTIC_NO_ML`.

Добавлен runner: `src/mlbotnav/visual_entry_quality_filter_runner.py`.

Тест: `tests/test_visual_entry_quality_filter_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_audit_20260625_RU.md`.

Отчеты:
1. `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_20260512_DEV.json`;
2. `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_20260512_DEV_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_family_overlay_2026-05-12_quality_01_q09_ensemble_q07_q01_20260625T132748Z.png`.

Лучший результат `Q09_ENSEMBLE_Q07_Q01`: `4/11` попаданий, `7` пропусков, `53` ложных входа, `57` входов всего, `precision=0.0702`, `recall=0.3636`, `f1=0.1176`.

Сравнение: предыдущий `VISUAL_MICRO_BOTTOM_SIGNATURE_V0` давал `4/11` и `135` ложных входов. Quality layer снизил false на `82`, но все еще не кандидат. В ML ничего не передавать.

Следующий слой: разделить пропуски на `EARLY_FLUSH_REVERSAL` и `DEEP_CAPITULATION_RECLAIM`, проверять отдельно и затем собирать ensemble только при улучшении `false_entries`.

## Visual Entry v3 micro-bottom diagnostic 2026-06-25
Статус: `DEV_MICRO_BOTTOM_SIGNATURE_DIAGNOSTIC_NO_ML`.

Добавлен diagnostic runner: `src/mlbotnav/visual_entry_micro_bottom_signature_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_audit_20260625_RU.md`.

Отчеты:
1. `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_20260512_DEV.json`;
2. `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_20260512_DEV_RU.md`.

Свежий top PNG: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_family_overlay_2026-05-12_micro_bottom_01_20260625T130512Z.png`.

Лучший результат `VISUAL_MICRO_BOTTOM_SIGNATURE_V0`: `4/11` попаданий, `7` пропусков, `135` ложных входов, `139` входов всего, `precision=0.0288`, `recall=0.3636`, `f1=0.0533`.

Вывод: идея микро-дна подтверждена лучше, чем чистые паспортные семейства, но шум слишком большой. Это не кандидат, в ML ничего не передавать. Следующий слой: suppression/quality filters `anti_drift_down`, `reclaim_quality`, `support_confluence`, `capitulation_absorption`, `bottom_event_clustering`.
## Visual Entry v3 passport-family diagnostic 2026-06-25
Статус: `DEV_PASSPORT_FAMILY_DIAGNOSTIC_DONE_NO_ML`.

Добавлен честный passport-family runner: `src/mlbotnav/visual_entry_passport_family_runner.py`.

Добавлен расширенный PNG-оверлей: `render_family_candidate_overlay()` в `src/mlbotnav/render_visual_entry_overlay.py`.

Аудит: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_audit_20260625_RU.md`.

Отчеты:
1. `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_runner_20260512_DEV.json`;
2. `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_runner_20260512_DEV_RU.md`.

Свежие PNG overlay:
1. `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_family_overlay_2026-05-12_family_01_deep_capitulation_next_open_20260625T125241Z.png`;
2. `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_family_overlay_2026-05-12_family_04_support_wick_reversal_next_open_20260625T125250Z.png`.

Проверенные семейства: `DEEP_CAPITULATION_NEXT_OPEN`, `SUPPORT_WICK_REVERSAL_NEXT_OPEN`, `DIVERGENCE_AT_SUPPORT_NEXT_OPEN`, `CHOCH_REENTRY_AFTER_BOTTOM_NEXT_OPEN`, `VPOC_RANGE_RECLAIM_NEXT_OPEN`.

Лучший честный passport-family результат слабый: `DEEP_CAPITULATION_NEXT_OPEN` дал `1/11` попаданий, `20` ложных входов, `21` вход всего, `precision=0.0476`, `recall=0.0909`, `f1=0.0625`.

Вывод: текущие паспорта подтверждают часть логики "дно/перепроданность", но не выделяют пользовательские входы как редкий качественный сигнал. В ML ничего не передавать. Следующий DEV-слой: `VISUAL_MICRO_BOTTOM_SIGNATURE_V0` с отдельным признаком микро-дна, затем exact scorer и PNG overlay.

## Visual Entry v3 user-entry arrows 2026-06-25
Статус: `DEV_V3_ENTRY_ARROWS_READY_NO_CANDIDATE_NO_ML`.

Пользовательская логика входа зафиксирована: сигнальная свеча - закрытая свеча дна/фитиля, вход LONG - на `open` следующей свечи с формулой `entry_open_price * (1 + slippage_bps / 10000)`.

Актуальная DEV-разметка: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows/manual_entries.json`.

Контрольный PNG целей: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows/visual_entry_combo_simple_arrows_manual_v3_targets_20260625T112336Z.png`.

Стратегический аудит: `reports/final_review/visual_entry_v3/visual_entry_v3_strategy_audit_20260625_RU.md`.

Добавлен честный no-lookahead runner: `src/mlbotnav/visual_entry_no_lookahead_candidates.py`.

No-lookahead rerun: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`.

Итог: solo-паспорта не кандидаты; старый combo-search с `green_entry_candle` считать lookahead diagnostic-only; лучший честный no-lookahead exact пока `3/11` и `34` false, поэтому в ML ничего не передавать. Следующий шаг - подтвердить v3 точки глазами пользователя и строить структурные подсемьи `DEEP_CAPITULATION_NEXT_OPEN`, `SHALLOW_SUPPORT_PULLBACK_NEXT_OPEN`, `REENTRY_AFTER_SPIKE_NEXT_OPEN` с support/CHOCH/divergence/volume-profile фильтрами.

## Visual Entry Calibration DEV-12 manual entries 2026-06-25
Статус: `DEV_DAY_MANUAL_ENTRIES_READY_SCORER_READY`.

DEV-разметка: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries.json`.

Аудит разметки: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries_audit_20260512_DEV_RU.md`.

Оверлей проверки: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries_SOLUSDT_1m_2026-05-12_DEV_detected_overlay.png`.

По пользовательскому PNG на `2026-05-12` восстановлены 6 предварительных LONG-входов: `01:44`, `04:15`, `09:12`, `12:36`, `15:34`, `17:05` UTC. Это лабораторный `DEV_DAY`; `2026-05-13` пока остается validation, `2026-05-14` остается holdout.

Добавлен scorer: `src/mlbotnav/visual_entry_score.py`.

Тест: `tests.test_visual_entry_score` PASS.

Первый diagnostic по старому B001 trade CSV:
`reports/qa_gate/visual_entry_score_SOLUSDT_1m_visual_dev_20260625_20260512_v1_oos_backtest_trades_SOLUSDT_1m_2026-05-12_long_only_20260625T073603Z.json`.

Результат B001: `targets_total=6`, `target_hits=3`, `missed_targets=3`, `false_entries=15`, `entries_total=18`, `precision=0.16666666666666666`, `recall=0.5`, `f1_visual=0.25`, `net_return_pct=-62.229358575198916`, статус `VISUAL_HITS_WITH_TOO_MANY_FALSE_ENTRIES`. Попадания: `12:36`, `15:32` против цели `15:34`, `17:04` против цели `17:05`. Пропуски: `01:44`, `04:15`, `09:12`.

Вывод: текущий B001 diagnostic ловит часть поздних стрелок, но дает слишком много лишних входов и отрицательный итог. Это не кандидат, в ML ничего не передавать. Следующий шаг: строить visual-driven solo/passport диагностику и отдельную reversal/dip-buy family для ранних входов у дна.

## Visual Entry Feature Audit and Prefilter 2026-06-25
Статус: `DEV_DIAGNOSTIC_DONE_NEXT_SOLO_SCORER_AND_REVERSAL_FAMILY`.

Feature-аудит: `reports/qa_gate/visual_entry_feature_audit_20260512_DEV.json`.

Prefilter-поиск: `reports/qa_gate/visual_entry_prefilter_search_20260512_DEV.json`.

План family: `reports/qa_gate/visual_entry_candidate_family_plan_20260512_DEV_RU.md`.

Добавлены инструменты:
1. `src/mlbotnav/visual_entry_feature_audit.py`;
2. `src/mlbotnav/visual_entry_prefilter_search.py`;
3. `tests/test_visual_entry_feature_audit.py`;
4. `tests/test_visual_entry_prefilter_search.py`.

Feature-аудит по 6 ручным входам показал: `ema20_down_context=5/6`, `rsi_cold=3/6`, `green_target_candle=3/6`, `dip_ret12=2/6`, `dip_ret24=2/6`, `near_local_low_60=2/6`, `stoch_low=2/6`. Выделены family-кандидаты `REVERSAL_DIP_BUY_LONG` и `EMA_DOWN_PULLBACK_REVERSAL_LONG`.

Простой prefilter сам по себе не кандидат: лучший вариант после cooldown `60` дал `target_hits=2/6`, `false_entries=19`, `entries_total=21`, `precision=0.09523809523809523`, `recall=0.3333333333333333`, `f1_visual=0.14814814814814814`. Лучший ранний вариант ловит `01:44/04:15/09:12`, но дает `36` лишних сигналов. В ML ничего не передавать.

Следующий шаг: не продвигать prefilter, а сделать diagnostic runner для solo visual scorer по выбранным существующим паспортам (`F012`, `F017/F018`, `F038`, `F035`, `F055`, `F057`, `F059`, `F009/F010`, `F020`) и отдельно подготовить `REVERSAL_DIP_BUY_LONG v0`.

## Visual Entry Overlay Rule 2026-06-25
Статус: `VISUAL_OVERLAY_REQUIRED_FOR_EACH_TEST`.

Добавлен renderer: `src/mlbotnav/render_visual_entry_overlay.py`.

Правило: каждый visual-test должен отдавать не только JSON/MD scorer, но и PNG overlay, где на одном графике видны ручные цели и фактические входы теста.

Текущие overlay:
1. B001 fixed diagnostic: `reports/final_review/visual_entry_overlay_2026-05-12_b001_fixed_dev12_20260625T095333Z.png`;
2. Prefilter TOP1 diagnostic: `reports/final_review/visual_entry_overlay_2026-05-12_prefilter_top1_dev12_20260625T095333Z.png`.

Обозначения: красная подпись времени - ручная цель, зеленая цель/треугольник - попадание, оранжевый крест - лишний вход.

Обновление 2026-06-25: ложные входы теперь рисуются ярко-красным `X` с белой окантовкой, чтобы не сливаться со свечами и EMA. Свежие PNG:
1. `reports/final_review/visual_entry_overlay_2026-05-12_b001_fixed_dev12_20260625T095623Z.png`;
2. `reports/final_review/visual_entry_overlay_2026-05-12_prefilter_top1_dev12_20260625T095623Z.png`.

## Visual Entry Solo Passport Runner 2026-06-25
Статус: `DEV_SOLO_PASSPORT_DIAGNOSTIC_DONE_NO_ML`.

Добавлен runner: `src/mlbotnav/visual_entry_solo_passport_runner.py`.

Тест: `tests/test_visual_entry_solo_passport_runner.py`.

Отчет: `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV.json`.

Русская сводка: `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV_RU.md`.

PNG overlay с ярко-красными ложными входами:
1. `reports/final_review/visual_entry_overlay_2026-05-12_solo_01_f009_emagap_down_20260625T100953Z.png`;
2. `reports/final_review/visual_entry_overlay_2026-05-12_solo_02_f059_engulfbull_20260625T100955Z.png`;
3. `reports/final_review/visual_entry_overlay_2026-05-12_solo_03_f010_emaslope_down_20260625T100957Z.png`;
4. `reports/final_review/visual_entry_overlay_2026-05-12_solo_04_f035_supportdist_20260625T100959Z.png`;
5. `reports/final_review/visual_entry_overlay_2026-05-12_solo_05_f017_f018_stoch14_20260625T101002Z.png`;
6. `reports/final_review/visual_entry_overlay_2026-05-12_solo_06_f038_rangepose_20260625T101004Z.png`.

Лучшие одиночные диагностические паспорта на DEV-дне `2026-05-12`:
1. `F009_EMAGAP_DOWN`: `2/6` попаданий, `6` ложных входов, `8` входов всего, `precision=0.25`, `recall=0.3333`, `f1_visual=0.2857`.
2. `F059_ENGULFBULL`: `1/6` попаданий, `0` ложных входов, `1` вход всего, `precision=1.0`, `recall=0.1667`, `f1_visual=0.2857`.
3. `F010_EMASLOPE_DOWN`: `2/6` попаданий, `16` ложных входов, `18` входов всего, `precision=0.1111`, `recall=0.3333`, `f1_visual=0.1667`.
4. `F035_SUPPORTDIST`: `1/6` попаданий, `8` ложных входов, `9` входов всего, `precision=0.1111`, `recall=0.1667`, `f1_visual=0.1333`.

Вывод: одиночные паспорта сами по себе не кандидаты. `F009_EMAGAP_DOWN` полезен как контекст падения/растяжения, `F059_ENGULFBULL` полезен как чистый свечной trigger, но каждый отдельно слабый. Следующий шаг: строить combo/family `REVERSAL_DIP_BUY_LONG v0` из контекста + trigger + suppression и каждый прогон показывать пользователю PNG overlay. В ML ничего не передавать.

## Visual Entry Calibration TZ 2026-06-25
Статус: `DESIGN_READY_WAITING_FOR_MARKUP`.

ТЗ: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_CALIBRATION_TZ_RU.md`.

Зафиксирована правильная структура: seed-графики из `data_layer=core`, ручная разметка `manual_entries.json`, visual scorer с `target_hits/missed_targets/false_entries/precision/recall/entry_lag_bars`, затем solo-passport sweep, block sweep, combo sweep и только после validation/holdout ручной `APPROVED_FOR_ML`.

Главный инвариант: графики, backtest/Optuna и будущий ML должны ссылаться на один и тот же `source_csv_sha256`; иначе результат `DATA_PARITY_FAIL`.

Следующий шаг: пользователь возвращает размеченные PNG или список времен входов по трем seed-дням, затем создается первый `manual_entries.json`.

## Visual Entry Calibration seed screenshots 2026-06-25
Статус: `MANUAL_MARKUP_SEED_IMAGES_READY`.

Папка: `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625`.

Manifest: `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_manifest.json`.

Выгружены три PNG для ручной разметки входов:
1. `manual_markup_seed_SOLUSDT_1m_2026-05-12_CORE.png`;
2. `manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.png`;
3. `manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.png`.

Контракт источника: все картинки построены строго из `data/core/bybit_ohlcv/.../part-final.csv`; для каждого дня manifest фиксирует `source_csv_sha256`, `rows=1440`, первый/последний `open_time_utc`. Эти же core-свечи должны использоваться при последующей Visual Entry Calibration, backtest/Optuna и ML-контуре.

Следующий шаг: пользователь размечает желаемые LONG/SHORT входы красными стрелками на этих PNG; после получения размеченных картинок оформить ТЗ/контракт `manual_entries.json` и scorer попаданий.

## B001 marked-entry fixed backtest 2026-06-25
Статус: `DONE_DIAGNOSTIC_ONLY_NO_PROMOTION`.

Аудит: `reports/qa_gate/b001_marked_entry_fixed_backtest_audit_20260625T073900Z_RU.md`.

Создана фиксированная матрица: `reports/qa_gate/b001_marked_entry_fixed_long_20260625T071500Z/B001_F001_F005_MARKED_ENTRY_FIXED_long_3OF5.yaml`.

Параметры: `B001_family_move=1`, `entry_action_min_confirmations=3`, `F001=0.02`, `F002=0.04`, `F003=0.10`, `F004=0.95`, `F005=0.35`.

Проверка на OOS `SOLUSDT 1m 2026-05-12`: с `min_expected_move_pct=0.001` пойманы `09:25` и `12:36`, результат `-47.05387771496912%`, `18` сделок. Без min-move результат `-67.41968770852606%`, `30` сделок. Оба результата отрицательные, в ML ничего не передавать.

Вывод: B001 `RET_N LONG` family может ловить часть momentum-входов, но не должна раздушиваться ради всех красных стрелок. Для входов "у дна" нужна отдельная reversal/dip-buy family.

## B001 marked-entry screenshot audit 2026-06-25
Статус: `DONE_DIAGNOSTIC_ONLY`.

Аудит: `reports/qa_gate/b001_marked_entry_screenshot_audit_20260625T070500Z_RU.md`.

По пользовательскому скриншоту восстановлены примерные времена красных стрелок: `01:42`, `07:02`, `08:15`, `09:25`, `12:36`, `15:48`, `17:15` UTC.

Вывод: текущая B001 RET_N family может поймать `09:25`, `12:36`, `17:15` при более мягких порогах `F001/F002/F003`, но точки `01:42`, `07:02`, `08:15`, `15:48` не являются хорошими целями для momentum-family `RET_N LONG`, потому что перед ними последние `ret_N` отрицательные или дают меньше `3/5` голосов. Для покупки "у дна" нужен отдельный reversal/dip-buy family.

В ML ничего не передавать: это ручной диагностический аудит, не кандидат.

## Shared-study profile-edge coverage fix 2026-06-25
Статус: `FIXED_CONFIRMED_BY_RUNTIME_SMOKE`.

Аудит: `reports/qa_gate/shared_study_profile_edge_coverage_fix_20260625T063700Z_RU.md`.

Причина неполного profile edge coverage найдена: профильные edge-пробы использовали `run_trial_index + profile_edge_worker_offset`, поэтому в process-pool `w2/w3` могли уходить за первые две фазы принудительного min/max покрытия. Core edge coverage такого сдвига не имел, поэтому закрывался стабильнее.

Фикс: profile edge forcing больше не сдвигается через `profile_edge_worker_offset`; для shared-study process-pool edge-задачи min/max распределяются между worker-ами через `--process-workers-total`.

Проверки:
1. `py_compile` PASS;
2. `PSParser` PASS;
3. `tests.test_optuna_search_runtime` PASS, `73/73 OK`;
4. `text_guard` PASS: `reports/qa_gate/recovery_r5_text_guard_20260625T065332Z.json`.

Контрольный smoke `b001_3of5_long_shared_edgefix3_20260625_115056`: launcher `OK`, final worker snapshot `w3` показал terminal `42/42`, core edge coverage `5/5 PASS`, profile edge coverage `7/7 PASS`, forced min/max coverage полный `7/7`.

Результат smoke по доходности: OOS `0`, сделок `0`. Это не кандидат; в ML ничего не передавать. Вопрос profile-edge coverage закрыт, следующий route можно выбирать без старого coverage warning.

## B001 family-unified 4/5 LONG shared-study repeat 2026-06-24
Статус: `DONE_TRADEFUL_NEGATIVE_NO_PROMOTION_WITH_EDGE_COVERAGE_WARN`.

Аудит: `reports/qa_gate/b001_family_unified_4of5_long_shared_repeat_audit_20260624T195100Z_RU.md`.

Пользовательский повтор `4/5 LONG` на shared-study `3x3/9` завершился штатно: launcher `OK`, storage `postgresql`, best worker `w3`, OOS `-5.4889095203104477%`, сделок `1`.

Решение: результат отрицательный, не кандидат, в ML ничего не передавать.

Предупреждение: core edge coverage `5/5 PASS`, но profile edge coverage неполный `2/7 PASS`; failed profiles: `F001_thr_pct`, `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`, `F005_thr_pct`.

## B001 family-unified 3/5 LONG shared-study 2026-06-24
Статус: `DONE_TRADEFUL_NEGATIVE_NO_PROMOTION_WITH_EDGE_COVERAGE_WARN`.

Аудит: `reports/qa_gate/b001_family_unified_3of5_long_shared_audit_20260624T195200Z_RU.md`.

Матрица: `reports/qa_gate/b001_family_unified_long_3of5_shared_20260625T005102/B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml`.

Shared study id: `b001_3of5_long_shared_20260625T005102`.

Результат smoke `1д/1д`:
1. launcher `OK`;
2. shared-study включен, storage preflight `postgresql`;
3. `w1/w2/w3` завершились с `exit_code=0`;
4. best worker `w3`;
5. OOS `-2.0302055441506761%`;
6. сделок `1`;
7. train gate `false`.

Вывод: семейное `3/5 LONG` дало tradeful-ветку, но результат отрицательный. Это диагностический `NO_PROMOTION`; в ML ничего не передавать.

Предупреждение: core edge coverage прошел `5/5`, но profile edge coverage неполный `4/7`; failed profiles: `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`. Поэтому этот прогон считать runtime diagnostic, а не чистым доказательством полного edge coverage.

Следующий безопасный шаг, если продолжаем B001 diagnostic: либо сначала закрыть вопрос profile-edge coverage на shared-study бюджете `42`, либо отдельно прогнать `B001 family-unified 3/5 SHORT` как diagnostic-only с явным coverage warning. К large 2н/1н по этой ветке не переходить без неотрицательного tradeful результата и понятного coverage-аудита.

## Optuna shared-study process-pool включен 2026-06-24
Статус: `OPTUNA_SHARED_STUDY_3X3_9_READY_NO_PROMOTION`.

Аудит: `reports/qa_gate/optuna_shared_study_process_pool_audit_20260624T190435Z_RU.md`.

Суть: собран режим "три процесса как ускорители, одна общая Optuna study как единая история поиска".

Профиль:
1. `ProcessWorkers=3`;
2. `SearchWorkersPerProcess=3`;
3. `Threads=9`;
4. `SearchWorkers=9`;
5. `OptunaTrials=42`;
6. `-SharedOptunaStudy`;
7. `-SharedStudyId <понятный_id_запуска>`.

Что исправлено:
1. `run_block_family_selection.ps1` умеет пробрасывать shared-study режим в process-pool.
2. `adaptive_auto_train.py` пробрасывает shared id в Optuna search.
3. `optuna_search_candidate.py` использует общий `study_namespace` для shared study, но сохраняет отдельный `worker_contour_id`.
4. Worker-артефакты и pipeline reports больше не перетираются, потому что получили worker suffix.
5. Trial-history rows получили worker context.
6. Shared-study запуск запрещается на `sqlite`; проверенный storage `postgresql`.

Проверки:
1. `py_compile` PASS.
2. PowerShell parser для обоих runner PASS.
3. `tests.test_optuna_search_runtime` PASS, `71/71 OK`.
4. Dry-run PASS: `w1/w2/w3` получили один `--optuna-shared-study-id` и разные `--contour-id`.
5. Runtime smoke PASS по инфраструктуре: `reports/logs/b001_4of5_long_shared_fix_launcher_20260624T185929Z.log`.

Smoke B001 `4/5 LONG` на shared study:
1. launcher `OK`;
2. `shared_optuna_study=true`;
3. best worker `w2`;
4. OOS `-10.009351008800071`;
5. сделок `2`.

Вывод: инфраструктура общего Optuna-поиска закрыта, но конкретный smoke отрицательный. В ML ничего не передавать.

## Single-worker Optuna profile 1x9/9 включен 2026-06-24
Статус: `OPTUNA_SINGLE_WORKER_1X9_9_READY`.

Суть: для семейной калибровки B001 разрешен один мощный process-pool worker вместо трех отдельных worker.

Изменено:
1. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` теперь допускает `ProcessWorkers=1`.
2. `APTuna/run_optuna_1d1d_stagec.ps1` больше не поднимает `ProcessWorkers=1` обратно до `2`.

Проверка dry-run:
1. `ProcessWorkers=1`;
2. `Threads/proc=9`;
3. `Search/proc=9`;
4. `Trials/proc=42`;
5. создается один worker `w1`.

Правило профиля: использовать `Threads=9`, `SearchWorkers=9`, `ProcessWorkers=1`, `SearchWorkersPerProcess=9`, `OptunaTrials=42`. Это примерно та же CPU-нагрузка, что `3x3/9`, но Optuna ведет одну общую историю trials.

## B001 family unified 5/5 закрыт 2026-06-24
Статус: `B001_FAMILY_UNIFIED_5OF5_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_unified_5of5_audit_20260624T154700Z_RU.md`.

Суть: исправлен режим, где `F001..F005` калибровались как независимые направления. Теперь family-unified использует одну общую ручку `B001_family_move`:
1. LONG: `B001_family_move=1`;
2. SHORT: `B001_family_move=-1`;
3. `F001..F005` калибруют только свои `thr_pct`;
4. вход блока идет через общее семейное подтверждение.

Изменено:
1. `src/mlbotnav/dataset.py`;
2. `src/mlbotnav/b001_ret_n_ladder_tournament.py`;
3. `configs/calibration_action_passports.yaml`;
4. `tests/test_dataset_inference_mode.py`;
5. `tests/test_b001_ret_n_ladder_tournament.py`.

Проверки: focused pytest `4 passed`.

Smoke 1д/1д strict `5/5`:
1. LONG unified: `0` сделок, `EMPTY_ACTION_GATE`, примеры счетчиков `1041 / 613 / 0 / 0 / 0`, `1113 / 613 / 0 / 0 / 0`, `996 / 594 / 0 / 0 / 0`.
2. SHORT unified: `0` сделок, `EMPTY_ACTION_GATE`, примеры счетчиков `1048 / 205 / 0 / 0 / 0`, `894 / 338 / 0 / 0 / 0`, `977 / 326 / 0 / 0 / 0`.
3. В ML ничего не передавалось.

Вывод: family-unified теперь действительно является одним звеном, но strict `5/5` слишком жесткий на smoke-окне. Следующий диагностический шаг: unified `4/5`, затем `3/5`.

## B001 family strict 5/5 smoke закрыт 2026-06-24
Статус: `B001_FAMILY_STRICT_5OF5_SMOKE_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_strict_5of5_smoke_audit_20260624T153100Z_RU.md`.

Матрица: `reports/qa_gate/b001_family_strict_5of5_20260624T152830Z/B001_F001_F005_STRICT_5OF5.yaml`.

Проверенное правило: семейный блок `B001` дает разрешение только когда `F001`, `F002`, `F003`, `F004`, `F005` одновременно дают `ALLOW` на одной сигнальной свече. Runtime применил `entry_action_min_confirmations=5`, policy `and_all`.

Результат smoke 1д/1д:
1. LONG: `0` сделок, `EMPTY_ACTION_GATE`, счетчики `985 / 573 / 0 / 0 / 0`.
2. SHORT: `0` сделок, `EMPTY_ACTION_GATE`, worker-счетчики `997 / 346 / 0 / 0 / 0`, `1076 / 220 / 0 / 0 / 0`, `701 / 268 / 0 / 0 / 0`.
3. В ML ничего не передавалось.

Вывод: strict `5/5` технически работает, но на этом окне полностью душит входы. Для продолжения диагностики логично проверять сверху вниз `4/5`, затем `3/5`; основной маршрут `B003.1` не меняется.

## B001_COMBO_DIAG визуальный аудит входов 2026-06-24
Статус: `B001_COMBO_DIAG_GATE_VISUAL_AUDIT_DONE`.

Артефакты:
1. LONG-график: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.png`.
2. LONG-summary: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.json`.
3. SHORT-график: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.png`.
4. SHORT-summary: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.json`.

Вывод: сырой день полный (`1440` минутных свечей), картинка не обрезана. Концентрация входов в одном участке объясняется runtime-фильтрами:
1. LONG: `621 -> 4 -> 4 -> 4` (`mode -> F-gate -> min_move -> trades`), режет почти весь день именно `F-gate`.
2. SHORT: `637 -> 240 -> 2 -> 2`, `F-gate` дает много разрешений по дню, но `min_expected_move_pct=0.001` оставляет только 2 входа.

Добавлен повторяемый инструмент: `src/mlbotnav/render_gate_diagnostic.py`.

## B001_COMBO_DIAG N-of-M smoke закрыт 2026-06-24
Статус: `B001_COMBO_DIAG_N_OF_M_SMOKE_DONE_NO_CANDIDATE`.

Аудит: `reports/qa_gate/b001_combo_diag_n_of_m_audit_20260624T125500Z_RU.md`.

Суть: для диагностического режима `B001_RET_N_TOURNAMENT` добавлена мягкая политика входа `N из M` через параметр `entry_action_min_confirmations`. Старый официальный маршрут `B001` не заменяется: baseline остается `solo_feature_selection_only`.

Smoke 1д/1д на полной комбинации `F001..F005`:
1. LONG: `OK`, `n_of_m`, `N=1`, OOS `-8.498538882812346%`, сделок `4`; входы появились, но результат отрицательный.
2. SHORT: `OK`, tradeful worker при `N=1` дал OOS `-6.055628696458093%`, сделок `2`; пустой fallback больше не должен считаться лучшим после фикса ранжирования process-pool.
3. В ML ничего не передавалось.

Фиксы:
1. `src/mlbotnav/backtest.py` поддерживает `entry_action_min_confirmations`; без него поведение остается `AND`.
2. `src/mlbotnav/optuna_search_candidate.py` не выбирает несуществующую runtime-колонку `B001_RET_N_ALLOW`, а берет реальные `F001..F005` gate-колонки из `feature_rows`.
3. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` предпочитает tradeful worker в диагностическом `best_worker`.
4. `APTuna/run_b001_ret_n_ladder_tournament.ps1` обновлен на текущие параметры окон.

Проверки: `5 passed`, PowerShell parse `PASS`, dry-run tournament runner `PASS`.

Основной следующий строгий шаг не меняется: `B003.1 large LONG 2н/1н`.

Отдельный возможный следующий диагностический шаг: прогнать 31 комбинацию `B001_RET_N` на smoke 1д/1д LONG и SHORT, потом брать на large только tradeful/неотрицательные комбинации.

## B002.3 итог блока закрыт 2026-06-24
Статус: `B002_3_BLOCK_SUMMARY_CLOSED_NEXT_B003`.

Итоговый отчет: `reports/qa_gate/b002_block_summary_b002_3_20260624T100800Z_RU.md`.

Решение по `B002`:
1. LONG: `NO_BLOCK_WINNER`, OOS `0.0`, сделок `0`, runtime `EMPTY_ACTION_GATE`.
2. SHORT: `NO_BLOCK_WINNER`, OOS `0.0`, сделок `0`, runtime `MIN_MOVE_UNREACHABLE`; один worker нашел 1 OOS-сделку, но она отрицательная `-7.690052872230013%`.
3. В ML ничего не передавалось.

Следующий блок по порядку: `B003`.

`B003` является одиночным блоком:
1. паспорт `F007`;
2. action `F007_RSTD20_ALLOW`;
3. matrix `configs/calibration_matrices/passport_actions/F007_rolling_std20_1m_entry_filter.yaml`.

Активный worker-профиль сохраняется: `3x3/9`.
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=3`;
4. `SearchWorkersPerProcess=3`.

Следующий строгий номер: `B003.1 large LONG 2н/1н`.

## B002.2 large SHORT закрыт 2026-06-24
Статус: `B002_2_LARGE_SHORT_CLOSED_NO_BLOCK_WINNER`.

Аудит: `reports/qa_gate/b002_large_short_b002_2_audit_20260624T100700Z_RU.md`.

Финальный отчет: `reports/qa_gate/block_family_selection_B002_short_only_20260624T100350Z.json`.

Итог:
1. блок `B002`, паспорт `F006 / F006_HLSPREAD_ALLOW`;
2. режим `short_only`;
3. общий статус `OK`, строка `ok`;
4. worker-профиль `3x3/9` подтвержден: `process_workers=3`, `threads_total=9`, все `w1/w2/w3` завершились `exit_code=0`;
5. выбранный OOS `0.0`, сделок `0`, runtime `MIN_MOVE_UNREACHABLE`;
6. один worker имел `1` OOS-сделку, но результат отрицательный `-7.690052872230013%`;
7. `block_winner=null`;
8. В ML ничего не передавалось.

Исторический следующий номер после этого раздела: `B002.3 итог блока`, уже закрыт.

## B002.1 large LONG закрыт 2026-06-24
Статус: `B002_1_LARGE_LONG_CLOSED_NO_BLOCK_WINNER`.

Аудит: `reports/qa_gate/b002_large_long_b002_1_audit_20260624T100300Z_RU.md`.

Финальный отчет: `reports/qa_gate/block_family_selection_B002_long_only_20260624T095949Z.json`.

Итог:
1. блок `B002`, паспорт `F006 / F006_HLSPREAD_ALLOW`;
2. режим `long_only`;
3. общий статус `OK`, строка `ok`;
4. worker-профиль `3x3/9` подтвержден: `process_workers=3`, `threads_total=9`, все `w1/w2/w3` завершились `exit_code=0`;
5. OOS `0.0`, сделок `0`, runtime `EMPTY_ACTION_GATE`;
6. `block_winner=null`;
7. В ML ничего не передавалось.

Следующий строгий номер: `B002.2 large SHORT 2н/1н`.

## B001.6 итог блока закрыт 2026-06-24
Статус: `B001_6_BLOCK_SUMMARY_CLOSED_NEXT_B002`.

Итоговый отчет: `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.

Решение по `B001`:
1. LONG: ручной положительный кандидат `F001 / F001_RET1_ALLOW`, OOS `+0.7322559143841945`, сделок `1`.
2. SHORT: `NO_BLOCK_WINNER`, OOS сделок `0`.
3. В ML ничего не передавалось.

Следующий блок по порядку: `B002`.

`B002` является одиночным блоком:
1. паспорт `F006`;
2. action `F006_HLSPREAD_ALLOW`;
3. matrix `configs/calibration_matrices/passport_actions/F006_hl_spread_1m_entry_filter.yaml`.

Активный worker-профиль для следующих block-family запусков: `3x3/9`.
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=3`;
4. `SearchWorkersPerProcess=3`.

Откат на `2x3/6` допустим только при устойчивой перегрузке CPU/памяти или падении worker-процессов; если откат нужен, сначала зафиксировать причину в аудите.

Следующий строгий номер: `B002.1 large LONG 2н/1н`.

## B001.5 large SHORT закрыт 2026-06-24
Статус: `B001_5_LARGE_SHORT_CLOSED_NO_BLOCK_WINNER`.

Аудит: `reports/qa_gate/b001_large_short_b001_5_audit_20260624T094057Z_RU.md`.

Финальный отчет:

`reports/qa_gate/block_family_selection_B001_short_only_20260624T091433Z.json`

Окно:
1. train `2026-05-11..2026-05-24`;
2. test/OOS `2026-05-25..2026-05-31`;
3. mode `short_only`;
4. timeframe `1m`;
5. data layer `core`.

Итог B001 SHORT:
1. Все `F001..F005` присутствуют.
2. Общий статус `OK`, строки `ok`.
3. `block_winner=null`, потому что в OOS нет tradeful-положительного результата.
4. Лучший доступный fallback: `F004 / F004_RET12_ALLOW`, OOS `0.0`, сделок `0`, runtime `EMPTY_ACTION_GATE`.
5. В OOS по всем `F001..F005` сделок `0`; по train были сделки только у `F002` и `F003`, обе ветки отрицательные суммарно.
6. В ML ничего не передавалось.

Фикс UX после B001.5: `APTuna/run_block_family_selection.ps1` больше не печатает полный JSON payload в терминал по умолчанию. Терминал теперь показывает краткую сводку по F-ID и строки вход/выход/profit, если сделки есть. Полный JSON остается в файле отчета; машинный вывод включается явно через `-EmitJson`.

Проверки:
1. B001 SHORT `-DryRun` после фикса вывода -> терминал без JSON-каши, краткая таблица.
2. `PYTHONPATH=src .\.venv\Scripts\python.exe -m pytest tests\test_block_family_manifest.py tests\test_backtest_fields.py -q` -> `47 passed`.
3. `PYTHONPATH=src .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate` -> `PASS`, отчет `reports/qa_gate/recovery_r5_text_guard_20260624T094914Z.json`.

Следующий строгий номер: `B001.6 итог блока LONG+SHORT`.

## B001.4 large LONG закрыт 2026-06-24
Статус: `B001_4_LARGE_LONG_PASS_WITH_WINNER`.

Аудит: `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.

Финальный отчет:

`reports/qa_gate/block_family_selection_B001_long_only_20260624T080934Z.json`

Окно:
1. train `2026-05-11..2026-05-24`;
2. test/OOS `2026-05-25..2026-05-31`;
3. mode `long_only`;
4. timeframe `1m`;
5. data layer `core`.

Итог B001 LONG:
1. Все `F001..F005` присутствуют.
2. Общий статус `OK`, строки `ok`.
3. `block_winner=F001 / F001_RET1_ALLOW`.
4. OOS `+0.7322559143841945`, сделок `1`, runtime `TRADEFUL_POSITIVE`.
5. `goal_pass=false`, потому что цель `1%`, а результат `0.7322559143841945%`.
6. В ML ничего не передавалось.

Фикс перед финальным повтором: runner теперь переносит `runtime_diagnostic_status` и `runtime_diagnostics` из связанного `oos_report` в блоковый `best_oos`, если этих полей не было в adaptive summary.

Исторический следующий номер после этого раздела был `B001.5`; он уже закрыт. Актуальный следующий номер указан сверху: `B001.6 итог блока LONG+SHORT`.

## B001.3 smoke 1д/1д закрыт 2026-06-24
Статус: `B001_3_SMOKE_AUDIT_PASS`.

Аудит: `reports/qa_gate/b001_smoke_1d1d_audit_20260624T075006Z_RU.md`.

Проверенные прогоны:
1. LONG: `reports/qa_gate/block_family_selection_B001_long_only_20260624T074316Z.json`.
2. SHORT: `reports/qa_gate/block_family_selection_B001_short_only_20260624T074525Z.json`.

Итог:
1. Все `F001..F005` присутствуют в LONG и SHORT.
2. Оба финальных отчета имеют общий статус `OK`, строки имеют статус `ok`.
3. LONG smoke выбрал `F001 / F001_RET1_ALLOW`: OOS `+2.404470760400401`, сделок `1`.
4. SHORT smoke не имеет победителя: лучший доступный `F002 / F002_RET3_ALLOW` дал OOS `-0.3092010602366857`, сделок `1`, поэтому `block_winner=null`.
5. В ML ничего не передавалось.

Фиксы в runner:
1. устойчивый разбор многострочного JSON process-pool;
2. запрет выбирать отрицательный или нулевой результат как `block_winner`;
3. корректный `OK` для `-DryRun`, если все строки имеют статус `dry_run`.

Проверки после фикса:
1. `PYTHONPATH=src .\.venv\Scripts\python.exe -m pytest tests\test_block_family_manifest.py -q` -> `2 passed`.
2. B001 LONG `-DryRun` 1д/1д -> `status=OK`, все `F001..F005`.
3. `PYTHONPATH=src .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate` -> `PASS`, отчет `reports/qa_gate/recovery_r5_text_guard_20260624T075150Z.json`.

Следующий строгий номер: `B001.4 large LONG 2н/1н`.

## Block-Family Route Correction 2026-06-24
Status: `ACTIVE_ROUTE_RUNNER_READY`.

Audit: `reports/qa_gate/block_family_passport_route_audit_20260624T064900Z.md`.

Independent agent: `Arendt`.

Decision:
1. Stop the old F-by-F continuation pointer to `8.2.19 F068_PATTERNAGE_ALLOW`.
2. The active route is now block-family calibration/selection.
3. One block is one work item.
4. Family blocks run all solo F-passports inside the block for LONG and SHORT, then fix one block winner or `NO_BLOCK_WINNER`.
5. Single-passport blocks run their one F-passport for LONG and SHORT.
6. Default baseline is solo-F selection inside the family, not AND-combination; combination passports remain diagnostic-only unless explicitly approved.
7. Do not package, approve, or ingest anything into ML until all block results are manually reviewed and explicitly approved.

Implemented:
1. `src/mlbotnav/block_family_manifest.py` builds a B-block manifest from `configs/calibration_action_passports.yaml`.
2. `APTuna/run_block_family_selection.ps1` runs all solo F-passports inside one block as one block-family work item on the large-window route.
3. `tests/test_block_family_manifest.py` protects B001 and B021 membership/order.
4. B001 dry-run expanded to F001,F002,F003,F004,F005 with train `2026-05-11..2026-05-24` and OOS `2026-05-25..2026-05-31`.

Validation:
1. `py_compile src\mlbotnav\block_family_manifest.py` -> `PASS`.
2. focused pytest -> `126 passed, 4 warnings`.
3. text_guard -> `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260624T070209Z.json`.
4. readiness check -> `project_ready=false`, `enforce_freeze=true`, report `reports/readiness/readiness_check_20260624T070208Z.json`.

Block winner policy:
1. Exclude `MIN_MOVE_UNREACHABLE`.
2. Prefer reachable candidates.
3. Prefer tradeful candidates.
4. Prefer positive OOS net return.
5. Then compare OOS net return, trades, drawdown, and diagnostics.

Next strict task: `BLOCK_ROUTE_1 Run B001 family solo-selection after min-move fix`, LONG then SHORT sequentially.

## Min-Move Runtime Guard Fix 2026-06-24
Status: `FIX_APPLIED_SUPERSEDED_BY_BLOCK_ROUTE`.

Audit: `reports/qa_gate/ml_optuna_min_move_runtime_guard_fix_audit_20260624T063400Z.md`.

Reason: fixed the confirmed zero-trade route defect where `min_expected_move_pct` could be selected above the `exchange_like` move proxy after action gates, producing misleading `0` trades even when passport/action signals existed.

Changed:
1. Added shared runtime outcome classifier: `src/mlbotnav/runtime_diagnostics.py`.
2. Backtest now reports min-move reachability diagnostics and proxy quantiles in `trend_filter_diagnostics`.
3. Optuna now marks `MIN_MOVE_UNREACHABLE`, adds it to `fail_keys`, penalizes it, and can retry the grid minimum min-move before final scoring.
4. Adaptive candidate selection skips `MIN_MOVE_UNREACHABLE` candidates when any reachable alternative exists.
5. Default adaptive `--min-expected-move-grid` is now `0.0,0.001,0.002,0.003`.
6. OOS reports now include `runtime_diagnostic_status` and `runtime_diagnostics`.

Validation:
1. `PYTHONPATH=src .\.venv\Scripts\python.exe -m pytest tests\test_backtest_fields.py tests\test_adaptive_candidate_pick.py tests\test_optuna_search_runtime.py -q` -> `124 passed`.
2. `python -m py_compile` on changed runtime modules -> `PASS`.
3. final text_guard -> `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260624T063715Z.json`.
4. readiness check -> `project_ready=false`, `enforce_freeze=true`, report `reports/readiness/readiness_check_20260624T063110Z.json`.

Historical decision before block-route correction:
1. The blocking min-move runtime defect is fixed in code.
2. Keep F050-F067 decisions as `NO_GO_FOR_ML`; do not package, approve, or ingest them.
3. The old F-by-F resume pointer to `F068` is superseded by `Block-Family Route Correction 2026-06-24`.

## Zero-Trade Diagnostic 2026-06-24
Status: `ROOT_CAUSE_FOUND`.

Audit: `reports/qa_gate/ml_optuna_zero_trade_min_move_diagnostic_20260624T051535Z.md`.

Conclusion:
1. Stage 8.2 zero-trade results are not all empty-signal cases.
2. Several candidates have signals after action gate, then all are removed by `min_expected_move_pct`.
3. Strong sample: F067 LONG has `1415` signals after action gate, selected `min_expected_move_pct=0.01`, proxy max after gate only `0.005140`, so OOS entries become unreachable.
4. Replay on the same F067 LONG OOS CSV confirms trades reappear when only `min_expected_move_pct` is lowered.

Historical decision before fix:
1. Keep F050-F067 decisions as `NO_GO_FOR_ML`.
2. Do not package, approve, or ingest these results into ML.
3. The pause is resolved by the `Min-Move Runtime Guard Fix 2026-06-24` section above.

## Route Status Audit After F067 2026-06-24
Status: `ON_ROUTE`.

Audit: `reports/qa_gate/ml_optuna_route_status_audit_after_f067_20260624T044311Z.md`.

Independent agent: `Archimedes`.

Conclusion:
1. Segment `8.2.9..8.2.18` is complete.
2. F058-F067 are all `NO_GO_FOR_ML`.
3. No `NO_GO` or `VALIDATION_FAIL` result was packaged, approved, or ingested into ML.
4. Top override/status sections remain authoritative over older historical next-step pointers.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the active block-family route at the top of this file.

## Stage 8.2.18 F067 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_18_f067_audit_20260623T225700Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F067_patternstrength_entry_filter.yaml`.
2. action_id: `F067_PATTERNSTRENGTH_ALLOW`.
3. block/passport: `B021 / F067`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F067_require_confirmation=0.0`, `F067_require_context=1.0`, `F067_strength_state=1.0`, `F067_strength_thr=3.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T225547Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F067_require_confirmation=1.0`, `F067_require_context=0.0`, `F067_strength_state=2.0`, `F067_strength_thr=2.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T225550Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T225005464027Z.json`.
2. active gate isolation: only `F067_PATTERNSTRENGTH_ALLOW`, ignored columns `[]`.
3. LONG action gate left `1415` signals, then min-move left `0` eligible bars and `0` filled entries.
4. SHORT action gate left `0` signals after entry action gate.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. text_guard before document updates: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T225605Z.json`.

Decision:
1. `F067_PATTERNSTRENGTH_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the active block-family route at the top of this file.

## Stage 8.2.17 F066 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_17_f066_audit_20260623T224200Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F066_obvbeardiv_entry_filter.yaml`.
2. action_id: `F066_OBVBEARDIV_ALLOW`.
3. block/passport: `B020 / F066`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F066_confirm_mode=1.0`, `F066_div_type=2.0`, `F066_max_pivot_gap_bars=85.0`, `F066_obv_delta_min_norm=4.5`, `F066_pivot_scope=1.0`, `F066_price_delta_min_pct=1.9`, `F066_reaction_confirm_pct=0.15`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T224134Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F066_confirm_mode=1.0`, `F066_div_type=1.0`, `F066_max_pivot_gap_bars=60.0`, `F066_obv_delta_min_norm=10.5`, `F066_pivot_scope=1.0`, `F066_price_delta_min_pct=1.25`, `F066_reaction_confirm_pct=0.45`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T224137Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T223534928668Z.json`.
2. active gate isolation: only `F066_OBVBEARDIV_ALLOW`, ignored columns `[]`.
3. LONG action gate left `0` signals after entry action gate.
4. SHORT action gate left `0` signals after entry action gate.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. text_guard before document updates: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T224148Z.json`.

Decision:
1. `F066_OBVBEARDIV_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`.

## Stage 8.2.16 F065 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_16_f065_audit_20260623T223100Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F065_obvbulldiv_entry_filter.yaml`.
2. action_id: `F065_OBVBULLDIV_ALLOW`.
3. block/passport: `B020 / F065`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F065_confirm_mode=2.0`, `F065_div_type=1.0`, `F065_max_pivot_gap_bars=55.0`, `F065_obv_delta_min_norm=13.0`, `F065_pivot_scope=2.0`, `F065_price_delta_min_pct=1.8`, `F065_reaction_confirm_pct=0.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T223005Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F065_confirm_mode=2.0`, `F065_div_type=2.0`, `F065_max_pivot_gap_bars=65.0`, `F065_obv_delta_min_norm=20.0`, `F065_pivot_scope=2.0`, `F065_price_delta_min_pct=0.5`, `F065_reaction_confirm_pct=0.85`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T223007Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T222439833160Z.json`.
2. active gate isolation: only `F065_OBVBULLDIV_ALLOW`, ignored columns `[]`.
3. LONG action gate left `4` signals, then min-move gate left `0` eligible bars and `0` filled entries.
4. SHORT action gate left `11` signals, then min-move gate left `0` eligible bars and `0` filled entries.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T223247Z.json`.

Decision:
1. `F065_OBVBULLDIV_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`.

## Stage 8.2.15 F064 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_15_f064_audit_20260623T222100Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F064_macdbeardiv_entry_filter.yaml`.
2. action_id: `F064_MACDBEARDIV_ALLOW`.
3. block/passport: `B020 / F064`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F064_confirm_mode=1.0`, `F064_div_type=2.0`, `F064_macd_component=2.0`, `F064_macd_delta_min_pct=0.02`, `F064_max_pivot_gap_bars=65.0`, `F064_pivot_scope=2.0`, `F064_price_delta_min_pct=1.3`, `F064_reaction_confirm_pct=1.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T222039Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F064_confirm_mode=2.0`, `F064_div_type=2.0`, `F064_macd_component=1.0`, `F064_macd_delta_min_pct=0.38`, `F064_max_pivot_gap_bars=75.0`, `F064_pivot_scope=1.0`, `F064_price_delta_min_pct=0.55`, `F064_reaction_confirm_pct=0.95`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T222042Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T221459909426Z.json`.
2. active gate isolation: only `F064_MACDBEARDIV_ALLOW`, ignored columns `[]`.
3. LONG action gate left `0` signals.
4. SHORT action gate left `0` signals.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T222318Z.json`.

Decision:
1. `F064_MACDBEARDIV_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`.

## Stage 8.2.14 F063 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_14_f063_audit_20260623T221200Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F063_macdbulldiv_entry_filter.yaml`.
2. action_id: `F063_MACDBULLDIV_ALLOW`.
3. block/passport: `B020 / F063`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F063_confirm_mode=2.0`, `F063_div_type=2.0`, `F063_macd_component=2.0`, `F063_macd_delta_min_pct=0.42`, `F063_max_pivot_gap_bars=35.0`, `F063_pivot_scope=1.0`, `F063_price_delta_min_pct=2.75`, `F063_reaction_confirm_pct=0.65`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T221115Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F063_confirm_mode=2.0`, `F063_div_type=2.0`, `F063_macd_component=2.0`, `F063_macd_delta_min_pct=0.32`, `F063_max_pivot_gap_bars=35.0`, `F063_pivot_scope=2.0`, `F063_price_delta_min_pct=1.15`, `F063_reaction_confirm_pct=0.8`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T221117Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T220559771509Z.json`.
2. active gate isolation: only `F063_MACDBULLDIV_ALLOW`, ignored columns `[]`.
3. LONG action gate left `0` signals.
4. SHORT action gate left `0` signals.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T221352Z.json`.

Decision:
1. `F063_MACDBULLDIV_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`.

## Stage 8.2.13 F062 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_13_f062_audit_20260623T220200Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F062_rsibeardiv_entry_filter.yaml`.
2. action_id: `F062_RSIBEARDIV_ALLOW`.
3. block/passport: `B020 / F062`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F062_confirm_mode=1.0`, `F062_div_type=2.0`, `F062_max_pivot_gap_bars=10.0`, `F062_pivot_scope=1.0`, `F062_price_delta_min_pct=2.5`, `F062_reaction_confirm_pct=0.85`, `F062_rsi_delta_min=3.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T220146Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F062_confirm_mode=2.0`, `F062_div_type=2.0`, `F062_max_pivot_gap_bars=5.0`, `F062_pivot_scope=1.0`, `F062_price_delta_min_pct=2.1`, `F062_reaction_confirm_pct=0.0`, `F062_rsi_delta_min=18.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T220148Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T215625607772Z.json`.
2. active gate isolation: only `F062_RSIBEARDIV_ALLOW`, ignored columns `[]`.
3. LONG action gate left `0` signals.
4. SHORT action gate left `0` signals.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T220438Z.json`.

Decision:
1. `F062_RSIBEARDIV_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`.

## Stage 8.2.12 F061 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_12_f061_audit_20260623T215100Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F061_rsibulldiv_entry_filter.yaml`.
2. action_id: `F061_RSIBULLDIV_ALLOW`.
3. block/passport: `B020 / F061`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F061_confirm_mode=1.0`, `F061_div_type=2.0`, `F061_max_pivot_gap_bars=30.0`, `F061_pivot_scope=1.0`, `F061_price_delta_min_pct=0.5`, `F061_reaction_confirm_pct=0.2`, `F061_rsi_delta_min=9.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T215007Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F061_confirm_mode=1.0`, `F061_div_type=1.0`, `F061_max_pivot_gap_bars=120.0`, `F061_pivot_scope=2.0`, `F061_price_delta_min_pct=0.25`, `F061_reaction_confirm_pct=0.85`, `F061_rsi_delta_min=14.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T215010Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T214356119690Z.json`.
2. active gate isolation: only `F061_RSIBULLDIV_ALLOW`, ignored columns `[]`.
3. LONG action gate left `0` signals.
4. SHORT action gate left `4` signals, then min-move gate left `0` eligible bars and `0` filled entries.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T215016Z.json`.

Decision:
1. `F061_RSIBULLDIV_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`.

## Stage 8.2.11 F060 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.11 Run F060_ENGULFBEAR_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_11_f060_audit_20260623T213900Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F060_engulfbear_entry_filter.yaml`.
2. action_id: `F060_ENGULFBEAR_ALLOW`.
3. block/passport: `B019 / F060`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F060_engulf_mode=2.0`, `F060_min_body_pct=65.0`, `F060_min_engulf_ratio=1.9`, `F060_trend_lookback_bars=20.0`, `F060_trend_min_rise_pct=1.15`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T213846Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F060_engulf_mode=2.0`, `F060_min_body_pct=55.0`, `F060_min_engulf_ratio=2.0`, `F060_trend_lookback_bars=19.0`, `F060_trend_min_rise_pct=0.55`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T213848Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T213310845884Z.json`.
2. active gate isolation: only `F060_ENGULFBEAR_ALLOW`, ignored columns `[]`.
3. LONG action gate left `0` signals.
4. SHORT action gate left `1` signal, then min-move gate left `0` eligible bars and `0` filled entries.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T213857Z.json`.

Decision:
1. `F060_ENGULFBEAR_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`.

## Stage 8.2.10 F059 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.10 Run F059_ENGULFBULL_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_10_f059_audit_20260623T213000Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F059_engulfbull_entry_filter.yaml`.
2. action_id: `F059_ENGULFBULL_ALLOW`.
3. block/passport: `B019 / F059`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F059_engulf_mode=2.0`, `F059_min_body_pct=35.0`, `F059_min_engulf_ratio=1.8`, `F059_trend_lookback_bars=8.0`, `F059_trend_min_drop_pct=0.4`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T212916Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F059_engulf_mode=2.0`, `F059_min_body_pct=50.0`, `F059_min_engulf_ratio=1.5`, `F059_trend_lookback_bars=15.0`, `F059_trend_min_drop_pct=0.75`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T212918Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T212332220518Z.json`.
2. active gate isolation: only `F059_ENGULFBULL_ALLOW`, ignored columns `[]`.
3. LONG and SHORT action gates left `0` signals after entry action gate.
4. worker `.err` files: `0` bytes.
5. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
6. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T212931Z.json`.

Decision:
1. `F059_ENGULFBULL_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.11 Run F060_ENGULFBEAR_ALLOW large-window candidate`.

## Stage 8.2.9 F058 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_9_f058_audit_20260623T211900Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F058_shootingstar_entry_filter.yaml`.
2. action_id: `F058_SHOOTINGSTAR_ALLOW`.
3. block/passport: `B019 / F058`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F058_body_zone_pct=45.0`, `F058_lower_wick_max_pct=20.0`, `F058_trend_lookback_bars=20.0`, `F058_trend_min_rise_pct=0.45`, `F058_upper_wick_min_pct=85.0`, `F058_wick_body_ratio=5.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T211742Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F058_body_zone_pct=40.0`, `F058_lower_wick_max_pct=5.0`, `F058_trend_lookback_bars=13.0`, `F058_trend_min_rise_pct=0.15`, `F058_upper_wick_min_pct=80.0`, `F058_wick_body_ratio=4.5`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T211744Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T211045699274Z.json`.
2. active gate isolation: only `F058_SHOOTINGSTAR_ALLOW`, ignored columns `[]`.
3. LONG action gate left `0` signals.
4. SHORT action gate left `1` signal, then min-move gate left `0` eligible bars and `0` filled entries.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T211810Z.json`.

Decision:
1. `F058_SHOOTINGSTAR_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.10 Run F059_ENGULFBULL_ALLOW large-window candidate`.

## Route Memory Audit 2026-06-23
Status: `ON_ROUTE`.

Audit: `reports/qa_gate/ml_optuna_route_memory_audit_20260623T205751Z.md`.

Independent agent: `Averroes`, read-only check agrees with local audit.

Conclusion:
1. Optuna and ML contours remain separated.
2. Stages `1.7`, `2.9`, `3.7`, `4.5`, `5.6`, `6.6`, `7.6`, `8.1`, and `8.2..8.2.11` are closed.
3. Current F050-F060 large-window candidates are not approved for ML.
4. Next strict WBS item remains `8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`.
5. Historical lower sections may still mention old pointers such as `5.3`; use the top current override/status as authoritative.

Обновлено UTC: `2026-06-23T21:39:00Z`.

## Stage 8.2.8 F057 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.8 Run F057_HAMMER_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_8_f057_audit_20260623T205000Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F057_hammer_entry_filter.yaml`.
2. action_id: `F057_HAMMER_ALLOW`.
3. block/passport: `B019 / F057`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F057_body_zone_pct=20.0`, `F057_lower_wick_min_pct=70.0`, `F057_trend_lookback_bars=10.0`, `F057_trend_min_drop_pct=1.35`, `F057_upper_wick_max_pct=25.0`, `F057_wick_body_ratio=5.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T204845Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F057_body_zone_pct=20.0`, `F057_lower_wick_min_pct=50.0`, `F057_trend_lookback_bars=11.0`, `F057_trend_min_drop_pct=0.45`, `F057_upper_wick_max_pct=10.0`, `F057_wick_body_ratio=3.5`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T204847Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T204302084159Z.json`.
2. LONG/SHORT dry-run: `PASS`.
3. active gate isolation: only `F057_HAMMER_ALLOW`, ignored columns `[]`.
4. LONG action gate left `0` signals.
5. SHORT action gate left `8` signals but `0` filled entries.
6. worker `.err` files: `0` bytes.
7. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
8. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T205204Z.json`.

Decision:
1. `F057_HAMMER_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`.

## Stage 8.2.7 F056 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_7_f056_audit_20260623T203800Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F056_pinbear_entry_filter.yaml`.
2. action_id: `F056_PINBEAR_ALLOW`.
3. block/passport: `B019 / F056`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F056_body_zone_pct=40.0`, `F056_min_range_pct=0.37`, `F056_opposite_wick_max_pct=20.0`, `F056_wick_body_ratio=1.5`, `F056_wick_min_pct=55.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T203648Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F056_body_zone_pct=20.0`, `F056_min_range_pct=0.17`, `F056_opposite_wick_max_pct=15.0`, `F056_wick_body_ratio=4.5`, `F056_wick_min_pct=55.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T203651Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T203109710661Z.json`.
2. LONG/SHORT dry-run: `PASS`.
3. active gate isolation: only `F056_PINBEAR_ALLOW`, ignored columns `[]`.
4. LONG and SHORT action gate left `0` signals.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T204000Z.json`.

Decision:
1. `F056_PINBEAR_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.8 Run F057_HAMMER_ALLOW large-window candidate`.

## Stage 8.2.6 F055 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.6 Run F055_PINBULL_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_6_f055_audit_20260623T202700Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F055_pinbull_entry_filter.yaml`.
2. action_id: `F055_PINBULL_ALLOW`.
3. block/passport: `B019 / F055`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F055_body_zone_pct=40.0`, `F055_min_range_pct=0.19`, `F055_opposite_wick_max_pct=15.0`, `F055_wick_body_ratio=4.5`, `F055_wick_min_pct=85.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T202603Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F055_body_zone_pct=50.0`, `F055_min_range_pct=0.69`, `F055_opposite_wick_max_pct=0.0`, `F055_wick_body_ratio=3.0`, `F055_wick_min_pct=75.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T202605Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T202018034914Z.json`.
2. LONG/SHORT dry-run: `PASS`.
3. active gate isolation: only `F055_PINBULL_ALLOW`, ignored columns `[]`.
4. LONG action gate left `1` signal but `0` filled entries.
5. SHORT action gate left `0` signals.
6. worker `.err` files: `0` bytes.
7. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
8. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T202913Z.json`.

Decision:
1. `F055_PINBULL_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`.

## Stage 8.2.5 F054 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_5_f054_audit_20260623T201700Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F054_insidebar_entry_filter.yaml`.
2. action_id: `F054_INSIDEBAR_ALLOW`.
3. block/passport: `B019 / F054`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F054_containment_mode=2.0`, `F054_max_inside_range_ratio=0.7`, `F054_mother_min_range_pct=1.46`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T201428Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F054_containment_mode=1.0`, `F054_max_inside_range_ratio=0.55`, `F054_mother_min_range_pct=1.22`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T201431Z.json`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T200821697293Z.json`.
2. LONG/SHORT dry-run: `PASS`.
3. active gate isolation: only `F054_INSIDEBAR_ALLOW`, ignored columns `[]`.
4. action gate reduced raw signals to zero entries on both sides.
5. worker `.err` files: `0` bytes.
6. readiness freeze restored after sequential runs: `project_ready=false`, `enforce_freeze=true`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T201812Z.json`.

Decision:
1. `F054_INSIDEBAR_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: `8.2.6 Run F055_PINBULL_ALLOW large-window candidate`.

## Stage 8.2.4 F053 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO_FIX_APPLIED`.

Closed: `8.2.4 Run F053_DOJI_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F053_doji_entry_filter.yaml`.
2. action_id: `F053_DOJI_ALLOW`.
3. block/passport: `B019 / F053`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F053_max_body_pct=15.0`, `F053_min_range_pct=0.37`, `F053_wick_balance_max_pct=45.0`, `F053_wick_mode=2.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T195823Z.json`.

SHORT result:
1. process pool status: `OK`.
2. best worker: `w2`.
3. OOS net return: `0.0`.
4. OOS trades: `0`.
5. selected params: `F053_max_body_pct=10.0`, `F053_min_range_pct=0.31`, `F053_wick_balance_max_pct=55.0`, `F053_wick_mode=1.0`.
6. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T195825Z.json`.

Fix:
1. Found process-pool temporary-unlock race when LONG/SHORT were launched concurrently with `-UseTemporaryUnlock`.
2. Restored `configs/readiness.yaml` to freeze from `reports/logs/readiness_backup_pool_20260623T195401Z_long_only_dda35a46.yaml`.
3. Saved bad post-parallel state as `reports/logs/readiness_bad_after_parallel_stage_8_2_4_f053_20260623T195900Z.yaml`.
4. Added live-marker guard in `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`.

Checks:
1. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T195320571929Z.json`.
2. LONG/SHORT dry-run: `PASS`.
3. simulated active unlock marker: `PASS`, launcher exits before workers with `EXIT_CODE=1`.
4. readiness freeze restored: `project_ready=false`, `enforce_freeze=true`.
5. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T200628Z.json`.

Decision:
1. `F053_DOJI_ALLOW` is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.
5. Temporary-unlock process-pool jobs must be launched sequentially while the shared marker exists.

Next strict WBS item: `8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`.

## Stage 8.2.3 F052 Fixed Validation 2026-06-23
Status: `CLOSED_VALIDATION_FAIL_NO_ML_GO`.

Closed: `8.2.3 Validate F052_CHOCH_ALLOW LONG on adjacent/rolling window`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_3_f052_fixed_validation_audit_20260623T194700Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F052_choch_entry_filter.yaml`.
2. action_id: `F052_CHOCH_ALLOW`.
3. block/passport: `B018 / F052`.
4. mode: `long_only`.
5. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
6. fixed params from Stage `8.2.2` LONG winner.
7. validation train: `2026-05-04..2026-05-17`.
8. validation OOS: `2026-05-18..2026-05-24`.

Validation result:
1. train gate: `false`.
2. OOS net return: `-5.696708101293968`.
3. OOS trades: `1`.
4. OOS goal pass: `false`.
5. exit reason: `timeout`.
6. OOS report: `reports/final_review/oos_report_SOLUSDT_1m_2026-05-18_to_2026-05-24_long_only_20260623T194451Z.json`.
7. OOS CSV: `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-18_to_2026-05-24_long_only_20260623T194451Z.csv`.

Checks:
1. adjacent validation preflight: `PASS`, report `reports/qa_gate/preflight_window_20260623T194042Z.json`.
2. large clean window audit recheck: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T194041676146Z.json`.
3. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T194642Z.json`, rows `9568`, failed rows `0`, missing columns `0`.
4. readiness freeze restored: `project_ready=false`, `enforce_freeze=true`.
5. OOS report data layer: `core`.
6. OOS action gate: `F052_CHOCH_ALLOW`.
7. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T195125Z.json`.

Decision:
1. `F052_CHOCH_ALLOW LONG` failed adjacent-window validation.
2. Do not build an ML candidate package from this run.
3. Do not add it to the approved ML registry.
4. Do not ingest it into ML.

Next strict WBS item: continue with the next user-selected passport/action discovery, or define a new validation idea with its own audit boundary.

## Stage 8.2.2 F052 Optuna Calibration 2026-06-23
Status: `CLOSED_POSITIVE_TEST_CANDIDATE_NEEDS_VALIDATION`.

Closed: `8.2.2 Run F052_CHOCH_ALLOW large-window candidate`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_2_f052_audit_20260623T193700Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F052_choch_entry_filter.yaml`.
2. action_id: `F052_CHOCH_ALLOW`.
3. block: `B018 MARKET_STRUCTURE`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

LONG result:
1. process pool status: `OK`.
2. best worker: `w1`.
3. status: `goal_pass`.
4. OOS net return: `+5.3486475132039635`.
5. OOS trades: `1`.
6. selected params: `F052_break_buffer_pct=0.29`, `F052_choch_dir=1`, `F052_confirm_bars=2`, `F052_require_opposite_bias=1`, `F052_structure_scope=1`.
7. OOS report: `reports/final_review/oos_report_SOLUSDT_1m_2026-05-25_to_2026-05-31_long_only_20260623T193156Z.json`.
8. OOS CSV: `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-25_to_2026-05-31_long_only_20260623T193156Z.csv`.

LONG caveat:
1. `train_gate_pass=false`.
2. OOS has only `1` trade.
3. The only trade exited by `timeout`.

SHORT result:
1. process pool status: `OK`.
2. best OOS net return: `0.0`.
3. best OOS trades: `0`.
4. status: `NO_GO_FOR_ML`.

Checks:
1. LONG and SHORT dry-run: `PASS`.
2. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T193638492904Z.json`.
3. winning LONG OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T193311Z.json`, rows `9587`, failed rows `0`, missing columns `0`.
4. SHORT OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T193638Z.json`, rows `9598`, failed rows `0`, missing columns `0`.
5. final err files: `0` bytes.
6. final search/train/OOS reports: `data_layer = core`.

Decision:
1. `F052_CHOCH_ALLOW LONG` is a positive test candidate.
2. It is not approved for ML automatically because train gate failed and OOS has only `1` trade.
3. Do not build an ML candidate package automatically from this run.
4. Do not start ML training from this run.

Next strict WBS item: manual decision: validate F052 LONG on adjacent/rolling window, explicitly approve draft package build, or continue next passport/action discovery.

## Stage 8.2.1 F050 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2.1 Run next passport/action candidate after F051 no-go`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_1_f050_audit_20260623T192700Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F050_bosup_entry_filter.yaml`.
2. action_id: `F050_BOSUP_ALLOW`.
3. block: `B018 MARKET_STRUCTURE`.
4. mode: `long_only`.
5. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
6. train/calibration: `2026-05-11..2026-05-24`.
7. test/OOS: `2026-05-25..2026-05-31`.

Final run:
1. process pool status: `OK`.
2. worker `w1`: `goal_fail`, OOS net return `0.0`, OOS trades `0`.
3. worker `w2`: `goal_fail`, OOS net return `0.0`, OOS trades `0`.
4. final summaries:
   - `reports/adaptive/long_only_pool_20260623t192342z_w1/adaptive_loop_SOLUSDT_1m_2026-05-25_20260623T192343Z.json`.
   - `reports/adaptive/long_only_pool_20260623t192342z_w2/adaptive_loop_SOLUSDT_1m_2026-05-25_20260623T192344Z.json`.

Checks:
1. dry-run with `-DataLayer core`: `PASS`.
2. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T192613680739Z.json`.
3. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T192614Z.json`, rows `9591`, failed rows `0`, missing columns `0`.
4. final err files: `0` bytes.
5. final search/train/OOS reports: `data_layer = core`.

Decision:
1. `F050_BOSUP_ALLOW` on the large clean window is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not start ML training from this run.

Next strict WBS item: `8.2.2 Run F052_CHOCH_ALLOW large-window candidate`, unless user overrides the target.

## Stage 8.2 Optuna Calibration 2026-06-23
Status: `CLOSED_NO_GO`.

Closed: `8.2 Run Optuna calibration`.

Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_audit_20260623T191900Z.md`.

Scope:
1. action/passport matrix: `configs/calibration_matrices/passport_actions/F051_bosdown_entry_filter.yaml`.
2. action_id: `F051_BOSDOWN_ALLOW`.
3. mode: `short_only`.
4. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
5. train/calibration: `2026-05-11..2026-05-24`.
6. test/OOS: `2026-05-25..2026-05-31`.

Fixes:
1. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`: added `-DataLayer raw|core`.
2. `src/mlbotnav/adaptive_auto_train.py`: added `--layer` and passes it to preflight/search/train/OOS.
3. `src/mlbotnav/search_gate_candidate.py`: added `--layer`.
4. `src/mlbotnav/optuna_search_candidate.py`: added `--layer`.
5. `src/mlbotnav/oos_evaluate.py`: OOS report now exposes top-level `data_layer`, train window, and test window.

Final run:
1. process pool status: `OK`.
2. worker `w1`: `goal_fail`, OOS net return `0.0`, OOS trades `0`.
3. worker `w2`: `goal_fail`, OOS net return `0.0`, OOS trades `0`.
4. final summaries:
   - `reports/adaptive/short_only_pool_20260623t191521z_w1/adaptive_loop_SOLUSDT_1m_2026-05-25_20260623T191521Z.json`.
   - `reports/adaptive/short_only_pool_20260623t191521z_w2/adaptive_loop_SOLUSDT_1m_2026-05-25_20260623T191523Z.json`.

Checks:
1. dry-run with `-DataLayer core`: `PASS`.
2. `py_compile`: `PASS`.
3. focused tests: `96 passed`.
4. large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T191756602803Z.json`.
5. OOS CSV contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T191757Z.json`, rows `9597`, failed rows `0`, missing columns `0`.
6. final err files: `0` bytes.
7. final search/train/OOS reports: `data_layer = core`.

Decision:
1. `F051_BOSDOWN_ALLOW` on the large clean window is `NO_GO_FOR_ML`.
2. Do not build an ML candidate package from this run.
3. Do not start ML training from this run.

Next strict WBS item: manual decision for next passport/action calibration target or revised `8.2` candidate run.

## Stage 8.1 Large Clean Window 2026-06-23
Status: `CLOSED_PASS`.

Closed: `8.1 Fix large clean window`.

Created:
1. `configs/ml_large_clean_window_manifest.yaml`.
2. `src/mlbotnav/ml_large_clean_window_manifest_audit.py`.
3. `tests/test_ml_large_clean_window_manifest_audit.py`.

Window:
1. symbol/timeframe/data layer: `SOLUSDT / 1m / core`.
2. train/calibration: `2026-05-11..2026-05-24`.
3. test/OOS: `2026-05-25..2026-05-31`.
4. train days: `14`.
5. test days: `7`.

Checks:
1. Large clean window audit: `PASS`, report `reports/qa_gate/ml_large_clean_window_manifest_audit_20260623T185856714751Z.json`.
2. Missing core OHLCV files: `0`.
3. Audit errors: `0`.
4. New tests: `4/4 OK`.
5. Focused smoke/ingest tests: `22/22 OK`.
6. `py_compile PASS`.

Audit: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.

Boundary:
1. Optuna calibration was not started.
2. Package was not created.
3. Package was not approved for ML.
4. ML ingest was not started.
5. ML training was not started.

Next strict WBS item: `8.2 Run Optuna calibration`.

## Stage 7 Closeout 2026-06-23
Status: `STAGE_7_CLOSED_PASS`.

Closed: `7.6 Stage 7 closeout`.

Closed Stage 7 items:
1. `7.1 Smoke run`.
2. `7.2 Build test package`.
3. `7.3 Run package contract audit`.
4. `7.4 Add package to approved registry`.
5. `7.5 Run ML ingest`.
6. `7.6 Stage 7 closeout`.

Artifacts:
1. Smoke manifest: `configs/ml_smoke_run_manifest.yaml`.
2. Approved package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.
3. Approved registry: `configs/ml_approved_calibration_packages.yaml`.
4. ML dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.
5. ML dataset manifest: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`.

Final checks:
1. Smoke window audit: `PASS`, report `reports/qa_gate/ml_smoke_window_manifest_audit_20260623T185225809702Z.json`.
2. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T185225Z.json`, approved count `1`.
3. Admission status: `PASS`, report `reports/qa_gate/ml_alignment_admission_status_audit_20260623T185225900740Z.json`, packages total `1`.
4. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T185225907862Z.json`, approved count `1`.
5. ML ingest dataset builder: `PASS`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T185252215865Z.json`, packages total `1`, rows total `1177`.
6. Dataset contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T184850Z.json`, rows `1177`, failed rows `0`, missing columns `0`.
7. Focused Stage 7 tests: `67/67 OK`.

Audit: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.

Boundary:
1. ML training was not started.
2. No direct Optuna report scan was used.
3. No unapproved package was ingested.
4. Source Stage 3 package was not changed.

Next strict WBS item: `8.1 Fix large clean window`.

## Stage 7.5 ML Ingest 2026-06-23
Status: `CLOSED_PASS`.

Closed: `7.5 Run ML ingest`.

Input registry:
`configs/ml_approved_calibration_packages.yaml`.

Input approved package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Output dataset:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.

Output dataset manifest:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`.

Checks:
1. Dataset builder: `PASS`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T184833777713Z.json`, packages total `1`, rows total `1177`, failures `0`.
2. Dataset contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T184850Z.json`, rows `1177`, failed rows `0`, missing columns `0`.
3. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T184833Z.json`, approved count `1`.
4. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T184833541360Z.json`, approved count `1`.
5. Admission status: `PASS`, report `reports/qa_gate/ml_alignment_admission_status_audit_20260623T184833995861Z.json`, packages total `1`.
6. Focused ingest tests: `24/24 OK`.

Audit: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.

Boundary:
1. ML training was not started.
2. Dataset came only from approved registry.
3. No direct Optuna report scan was used.
4. No unapproved package was ingested.

Next strict WBS item: `7.6 Stage 7 closeout`.

## Stage 7.4 Approved Registry 2026-06-23
Status: `CLOSED_PASS`.

Closed: `7.4 Add package to approved registry`.

Approved package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Run ID:
`smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Changes:
1. Registry `configs/ml_approved_calibration_packages.yaml` now has `registry_status: HAS_APPROVED_PACKAGES`.
2. Registry contains one approved package with `status: APPROVED_FOR_ML`.
3. Package `manifest.json.status`: `APPROVED_FOR_ML`.
4. Package `calibration_package.json.status`: `APPROVED_FOR_ML`.
5. Package `audit.md`: `ML decision: GO_FOR_ML`.

Checks:
1. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T184310Z.json`, approved count `1`, failures `0`.
2. Admission status: `PASS`, report `reports/qa_gate/ml_alignment_admission_status_audit_20260623T184310594124Z.json`, packages total `1`, failed packages `0`.
3. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T184310619275Z.json`, approved count `1`, failures `0`.
4. Trade dataset contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T184310Z.json`, rows `1177`, failed rows `0`, missing columns `0`.
5. Run ID alignment: `PASS`, report `reports/qa_gate/ml_alignment_run_id_audit_20260623T184310528833Z.json`.
6. Passport context alignment: `PASS`, report `reports/qa_gate/ml_alignment_passport_context_audit_20260623T184310533973Z.json`.
7. Calibration params alignment: `PASS`, report `reports/qa_gate/ml_alignment_calibration_params_audit_20260623T184310545837Z.json`.
8. Data windows alignment: `PASS`, report `reports/qa_gate/ml_alignment_data_windows_audit_20260623T184310606562Z.json`.
9. Focused tests: `42/42 OK`.

Audit: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.

Boundary:
1. Only smoke package was approved.
2. Source Stage 3 package was not changed.
3. ML ingest was not started.
4. Dataset builder was not run; it is reserved for `7.5`.
5. ML training was not started.

Next strict WBS item: `7.5 Run ML ingest`.

## Stage 7.3 Package Contract Audit 2026-06-23
Status: `CLOSED_PASS`.

Closed: `7.3 Run package contract audit`.

Package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Package context:
1. `SOLUSDT`, `1m`, `core`.
2. train: `2026-05-25..2026-05-26`.
3. test: `2026-05-27..2026-05-27`.
4. block/passport/action: `B018 / F051 / F051_BOSDOWN_ALLOW`.
5. status: `DRAFT`.
6. package audit decision: `NO_GO_FOR_ML`.

Checks:
1. Trade dataset contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T183343Z.json`, rows `1177`, failed rows `0`, missing columns `0`.
2. Direct contract API: `PASS` in `approved_mode=False` and `approved_mode=True`.
3. Run ID alignment: `PASS`, report `reports/qa_gate/ml_alignment_run_id_audit_20260623T183343079459Z.json`.
4. Passport context alignment: `PASS`, report `reports/qa_gate/ml_alignment_passport_context_audit_20260623T183343074882Z.json`.
5. Calibration params alignment: `PASS`, report `reports/qa_gate/ml_alignment_calibration_params_audit_20260623T183343087870Z.json`.
6. Data windows alignment: `PASS`, report `reports/qa_gate/ml_alignment_data_windows_audit_20260623T183343170849Z.json`.
7. Admission status: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_admission_status_audit_20260623T183358611200Z.json`.
8. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T183358Z.json`.
9. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T183358612297Z.json`.
10. Dataset builder: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T183358639712Z.json`.
11. Focused tests: `48/48 OK`.
12. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T183955Z.json`.

Audit: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.

Boundary:
1. Registry was not mutated.
2. `APPROVED_FOR_ML` is not set.
3. ML ingest was not started.
4. ML training was not started.

Next strict WBS item: `7.4 Add package to approved registry`.

## Stage 7.2 Smoke Package 2026-06-23
Status: `CLOSED_PASS`.

Closed: `7.2 Build test package`.

Created package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Package context:
1. `SOLUSDT`, `1m`, `core`.
2. train: `2026-05-25..2026-05-26`.
3. test: `2026-05-27..2026-05-27`.
4. block/passport/action: `B018 / F051 / F051_BOSDOWN_ALLOW`.
5. status: `DRAFT`.
6. package audit decision: `NO_GO_FOR_ML`.

Fix applied:
1. package-local `source_reports/oos_report.json` was missing `data_layer` and `date_range`.
2. Fixed only the smoke package copy.
3. Source Stage 3 package was not changed.

Checks:
1. Trade dataset contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T182844Z.json`.
2. Run ID alignment: `PASS`, report `reports/qa_gate/ml_alignment_run_id_audit_20260623T182844876710Z.json`.
3. Passport context alignment: `PASS`, report `reports/qa_gate/ml_alignment_passport_context_audit_20260623T182844873108Z.json`.
4. Calibration params alignment: `PASS`, report `reports/qa_gate/ml_alignment_calibration_params_audit_20260623T182844895690Z.json`.
5. Data windows alignment: `PASS`, report `reports/qa_gate/ml_alignment_data_windows_audit_20260623T182844946419Z.json`.
6. Focused tests: `42/42 OK`.
7. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T182901Z.json`.
8. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T182901832869Z.json`.
9. Dataset builder: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T182901838594Z.json`.
10. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T182902Z.json`.

Audit: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.

Boundary:
1. Registry was not mutated.
2. `APPROVED_FOR_ML` is not set.
3. ML ingest was not started.
4. ML training was not started.

Next strict WBS item: `7.3 Run package contract audit`.

## Stage 7.1 Smoke Window 2026-06-23
Status: `CLOSED_PASS`.

Closed: `7.1 Smoke run`.

Created:
1. `configs/ml_smoke_run_manifest.yaml`.
2. `src/mlbotnav/ml_smoke_window_manifest_audit.py`.
3. `tests/test_ml_smoke_window_manifest_audit.py`.

Selected clean smoke window:
1. `SOLUSDT`, `1m`.
2. data layer: `core`.
3. train: `2026-05-25..2026-05-26`.
4. test: `2026-05-27..2026-05-27`.
5. forbidden date `2026-06-01` is not used.
6. `raw`, `quarantine`, and `raw/quarantine` are not used.

Checks:
1. Smoke manifest audit: `PASS`, report `reports/qa_gate/ml_smoke_window_manifest_audit_20260623T182159845644Z.json`.
2. New tests: `5/5 OK`.
3. Focused ML smoke/alignment tests: `78/78 OK`.
4. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T182159Z.json`.
5. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T182159828236Z.json`.
6. Dataset builder: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T182217683963Z.json`.
7. Rejection reason log: `PASS / NO_REJECTIONS`, report `reports/qa_gate/ml_rejection_reason_log_20260623T182217684902Z.json`.
8. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T182218Z.json`.

Audit: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.

Boundary:
1. No package was created in this step.
2. Registry was not mutated.
3. `APPROVED_FOR_ML` is not set.
4. ML ingest was not started.
5. ML training was not started.

Next strict WBS item: `7.2 Build test package`.

## Stage 6 Closeout 2026-06-23
Status: `STAGE_6_CLOSED_PASS`.

Closed:
1. `6.1` Run ID alignment.
2. `6.2` Passport context alignment.
3. `6.3` Calibration params alignment.
4. `6.4` Data windows alignment.
5. `6.5` Admission status.
6. `6.6` Stage 6 closeout.

Checks:
1. Alignment run ID: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_run_id_audit_20260623T181237828151Z.json`.
2. Alignment passport context: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_passport_context_audit_20260623T181237783963Z.json`.
3. Alignment calibration params: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_calibration_params_audit_20260623T181237770134Z.json`.
4. Alignment data windows: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_data_windows_audit_20260623T181237775261Z.json`.
5. Alignment admission status: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_admission_status_audit_20260623T181237875726Z.json`.
6. Focused ML tests: `121/121 OK`.
7. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T181258Z.json`.
8. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T181258674295Z.json`.
9. Dataset builder: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T181258689707Z.json`.
10. Reject-log builder: `PASS / NO_REJECTIONS`, report `reports/qa_gate/ml_rejection_reason_log_20260623T181258738325Z.json`.
11. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T181511Z.json`.

Audit: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. No ML dataset was created from unapproved data.
4. ML training was not started.

Next strict WBS item: `7.1 Smoke run`.

## Stage 6.5 Admission Status 2026-06-23
Status: `CLOSED_PASS`.

Closed: `6.5 Check admission status`.

Created:
1. `src/mlbotnav/ml_alignment_admission_status_audit.py`.
2. `tests/test_ml_alignment_admission_status_audit.py`.

What is checked:
1. registry entry `status = APPROVED_FOR_ML`.
2. `manifest.json.status = APPROVED_FOR_ML`.
3. `calibration_package.json.status = APPROVED_FOR_ML`.
4. `audit.md` contains `ML decision: GO_FOR_ML`.
5. Any mismatch returns `FAIL`.

Checks:
1. `py_compile PASS`.
2. New tests: `6/6 OK`.
3. Focused ML tests: `121/121 OK`.
4. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_admission_status_audit_20260623T180909527952Z.json`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T181123Z.json`.

Audit: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. No ML dataset was created from unapproved data.
4. ML training was not started.
5. Stage 6 closeout is reserved for `6.6`.

Next strict WBS item: `6.6 Stage 6 closeout`.

## Stage 6.4 Data Windows Alignment 2026-06-23
Status: `CLOSED_PASS`.

Closed: `6.4 Check data windows`.

Created:
1. `src/mlbotnav/ml_alignment_data_windows_audit.py`.
2. `tests/test_ml_alignment_data_windows_audit.py`.

What is checked:
1. `data_layer`.
2. `train_start`.
3. `train_end`.
4. `test_start`.
5. `test_end`.
6. Sources must match across `manifest.json`, `trade_log.csv`, and package-local `source_reports/oos_report.json` when OOS report exists.
7. Dates must be valid `YYYY-MM-DD`, windows must be ordered, and `data_layer` must be `core`.

Checks:
1. `py_compile PASS`.
2. New tests: `8/8 OK`.
3. Focused ML tests: `115/115 OK`.
4. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_data_windows_audit_20260623T154607261155Z.json`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T154759Z.json`.

Audit: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. No ML dataset was created from unapproved data.
4. ML training was not started.
5. Admission status is reserved for `6.5`.

Next strict WBS item: `6.5 Check admission status`.

## Stage 6.3 Calibration Params Alignment 2026-06-23
Status: `CLOSED_PASS`.

Closed: `6.3 Check calibration params`.

Created:
1. `src/mlbotnav/ml_alignment_calibration_params_audit.py`.
2. `tests/test_ml_alignment_calibration_params_audit.py`.

What is checked:
1. `calibration_package.json.calibration_params`.
2. `trade_log.csv.calibration_params_json`.
3. `source_reports/oos_report.json.calibration_params`, if the package has that OOS report.
4. Canonical JSON object equality.
5. Any mismatch returns `FAIL`.

Checks:
1. `py_compile PASS`.
2. New tests: `7/7 OK`.
3. Focused ML tests: `107/107 OK`.
4. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_calibration_params_audit_20260623T154050444104Z.json`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T154240Z.json`.

Audit: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. No ML dataset was created from unapproved data.
4. ML training was not started.
5. Data windows are reserved for `6.4`.

Next strict WBS item: `6.4 Check data windows`.

## Stage 6.2 Passport Context Alignment 2026-06-23
Status: `CLOSED_PASS`.

Closed: `6.2 Check passport context`.

Created:
1. `src/mlbotnav/ml_alignment_passport_context_audit.py`.
2. `tests/test_ml_alignment_passport_context_audit.py`.

What is checked:
1. `block_id`.
2. `passport_id`.
3. `action_id`.
4. Sources must match across `manifest.json`, `calibration_package.json`, and `trade_log.csv`.
5. Any mismatch returns `FAIL`.

Checks:
1. `py_compile PASS`.
2. New tests: `6/6 OK`.
3. Focused ML tests: `100/100 OK`.
4. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_passport_context_audit_20260623T153553932585Z.json`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T153741Z.json`.

Audit: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. No ML dataset was created from unapproved data.
4. ML training was not started.
5. Calibration params are reserved for `6.3`.

Next strict WBS item: `6.3 Check calibration params`.

## Stage 6.1 Run ID Alignment 2026-06-23
Status: `CLOSED_PASS`.

Closed: `6.1 Check run_id alignment`.

Created:
1. `src/mlbotnav/ml_alignment_run_id_audit.py`.
2. `tests/test_ml_alignment_run_id_audit.py`.

What is checked:
1. `manifest.json` field `run_id`.
2. `calibration_package.json` field `run_id`.
3. `trade_log.csv` column `run_id`.
4. Any mismatch returns `FAIL`.

Checks:
1. `py_compile PASS`.
2. New tests: `5/5 OK`.
3. Focused ML tests: `94/94 OK`.
4. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_run_id_audit_20260623T152715670875Z.json`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T153207Z.json`.

Audit: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. No ML dataset was created from unapproved data.
4. ML training was not started.

Next strict WBS item: `6.2 Check passport context`.

## Stage 5 Closeout 2026-06-23
Status: `STAGE_5_CLOSED_PASS`.

Closed:
1. `5.1` ML ingest entry point discovery.
2. `5.2` Source policy blocks direct old report roots.
3. `5.3` Approved package registry reader.
4. `5.4` Approved trade dataset builder.
5. `5.5` Rejection reason log.
6. `5.6` Stage 5 closeout.

Checks:
1. `py_compile PASS`.
2. Focused tests: `89/89 OK`.
3. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T152045Z.json`.
4. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T152045217551Z.json`.
5. Dataset builder: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T152111078301Z.json`.
6. Reject-log builder: `PASS / NO_REJECTIONS`, report `reports/qa_gate/ml_rejection_reason_log_20260623T152111079049Z.json`.
7. Source policy registry allowed: `PASS`, report `reports/qa_gate/ml_ingest_source_policy_20260623T152111050538Z.json`.
8. Source policy old root denied: expected `FAIL`, report `reports/qa_gate/ml_ingest_source_policy_20260623T152122738533Z.json`.
9. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.

Audit: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. No ML dataset was created from unapproved data.
4. ML training was not started.

Next strict WBS item: `6.1 Check run_id alignment`.

## Stage 5.5 Rejection Reasons 2026-06-23
Status: `CLOSED_PASS`.

What changed:
1. Added rejection reason log builder: `src/mlbotnav/ml_rejection_reason_log.py`.
2. Added tests: `tests/test_ml_rejection_reason_log.py`.
3. Rejection log now records `missing_required_columns`, `invalid_manifest`, `not_approved`, `bad_data_layer`, and `bad_status`.
4. Additional categories: `missing_package_file`, `missing_manual_metadata`, `invalid_package_path`, `contract_fail`, `invalid_registry_entry`.

Current real registry result:
1. Registry: `configs/ml_approved_calibration_packages.yaml`.
2. Reject-log report: `reports/qa_gate/ml_rejection_reason_log_20260623T151618705623Z.json`.
3. Reject log: `reports/ml_rejections/ml_rejection_reasons_20260623T151618703912Z.json`.
4. Status: `PASS`.
5. Reason: `NO_REJECTIONS`.
6. Rejections total: `0`.

Checks:
1. `py_compile PASS`.
2. New rejection reason tests: `4/4 OK`.
3. Focused tests: `89/89 OK`.
4. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T151814Z.json`.
5. Reject-log smoke: `PASS / NO_REJECTIONS`, report `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`.
6. Reject log: `reports/ml_rejections/ml_rejection_reasons_20260623T151814360422Z.json`.
7. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.

Audit: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. No ML dataset was created from unapproved data.
4. ML training was not started.

Next strict WBS item: `5.6 Stage 5 closeout`.

## Stage 5.4 ML Trade Dataset Assembly 2026-06-23
Status: `CLOSED_PASS`.

What changed:
1. Added approved trade dataset builder: `src/mlbotnav/ml_approved_trade_dataset_builder.py`.
2. Added tests: `tests/test_ml_approved_trade_dataset_builder.py`.
3. Builder assembles ML trade dataset only from packages exposed by approved registry reader.
4. Builder validates package trade logs and final dataset with `ml_trade_dataset_contract`.

Current real registry result:
1. Registry: `configs/ml_approved_calibration_packages.yaml`.
2. Builder report: `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T150934741093Z.json`.
3. Status: `PASS`.
4. Reason: `NO_APPROVED_PACKAGES`.
5. Dataset path: empty.
6. Rows total: `0`.

Checks:
1. `py_compile PASS`.
2. New builder tests: `3/3 OK`.
3. Focused tests: `85/85 OK`.
4. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T151131Z.json`.
5. Builder smoke: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`.
6. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.

Audit: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. No ML dataset was created from unapproved data.
4. ML training was not started.

Next strict WBS item: `5.5 Add rejection reasons`.

## Stage 5.3 Approved Package Registry Reader 2026-06-23
Status: `CLOSED_PASS`.

What changed:
1. Added registry reader: `src/mlbotnav/ml_approved_package_registry_reader.py`.
2. Added tests: `tests/test_ml_approved_package_registry_reader.py`.
3. Reader validates the registry before exposing packages to future ML dataset assembly.
4. Reader applies source-policy checks and accepts only approved registry/candidate package sources.

Current real registry result:
1. Registry: `configs/ml_approved_calibration_packages.yaml`.
2. Reader report: `reports/qa_gate/ml_approved_package_registry_reader_20260623T145755674743Z.json`.
3. Status: `PASS`.
4. Approved count: `0`.
5. Packages exposed to ML: `0`.

Checks:
1. `py_compile PASS`.
2. New reader tests: `3/3 OK`.
3. Focused tests: `82/82 OK`.
4. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T150239Z.json`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.

Audit: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. ML dataset assembly was not started.
4. ML ingest/training was not started.

Next strict WBS item: `5.4 Implement ML dataset assembly`.

## Stage 5.2 ML Ingest Source Policy 2026-06-23
Status: `CLOSED_PASS`.

What changed:
1. Added source-policy guard: `src/mlbotnav/ml_ingest_source_policy.py`.
2. Added tests: `tests/test_ml_ingest_source_policy.py`.
3. Added explicit forbidden direct ML ingest roots to `configs/ml_approved_calibration_packages.yaml`.

Forbidden direct roots:
1. `reports/optuna`
2. `reports/pipeline`
3. `reports/final_review`

Allowed source classes:
1. Approval registry: `configs/ml_approved_calibration_packages.yaml`.
2. Candidate packages: `reports/ml_candidates/<run_id>/...`.

Checks:
1. `py_compile PASS`.
2. New source policy tests: `5/5 OK`.
3. Allowed source smoke: `PASS`, report `reports/qa_gate/ml_ingest_source_policy_20260623T145309955779Z.json`.
4. Forbidden source smoke: expected `FAIL`, report `reports/qa_gate/ml_ingest_source_policy_20260623T145318504657Z.json`.
5. Focused tests: `79/79 OK`.
6. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T145329Z.json`.
7. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T145330Z.json`.

Audit: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. ML ingest/training was not started.
4. Registry reading for ML ingest starts at `5.3`.

Next strict WBS item: `5.3 Implement registry reading`.

## Stage 5.1 ML Ingest Entry Point 2026-06-23
Status: `CLOSED_PASS`.

Found current ML training ingest entry point:
1. Primary: `src/mlbotnav/pipeline_train_eval.py`.
2. Orchestrators: `src/mlbotnav/prod_cycle.py`, `src/mlbotnav/stage_ladder.py`, `src/mlbotnav/adaptive_auto_train.py`.
3. Legacy/simple baseline: `src/mlbotnav/train_baseline.py`.
4. Not training ingest: `src/mlbotnav/inference.py`.

Current gap:
1. Training route reads OHLCV through `load_ohlcv_range` and builds features directly.
2. Training route does not read `configs/ml_approved_calibration_packages.yaml`.
3. Training route does not assemble a dataset from `reports/ml_candidates/<run_id>/trade_log.csv`.

Audit: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.

Boundary:
1. No package was added to `approved_packages`.
2. `APPROVED_FOR_ML` is not set.
3. ML ingest/training was not started.
4. No code behavior was changed in this step.

Next strict WBS item: `5.2 Block direct Optuna/report reading for ML ingest`.

## Stage 4 Closeout 2026-06-23
Status: `STAGE_4_CLOSED_PASS`.

Closed:
1. `4.1` registry file.
2. `4.2` registry format.
3. `4.3` registry bans.
4. `4.4` registry validator.
5. `4.5` Stage 4 closeout.

Result:
1. Manual approval registry exists: `configs/ml_approved_calibration_packages.yaml`.
2. Registry validator exists: `src/mlbotnav/ml_approval_registry_validator.py`.
3. Registry remains empty: `approved_packages: []`.
4. Approved count: `0`.
5. Deny result: `ML_ADMISSION_DENY`.

Checks:
1. `py_compile PASS`.
2. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T143952Z.json`.
3. Focused tests: `74/74 OK`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T144002Z.json`.

Audit: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.

Boundary:
1. `APPROVED_FOR_ML` is not set.
2. ML ingest was not started.
3. Optuna results were not sent to ML automatically.

Next strict WBS item: `5.1 Find current ML ingest entry point`.

## Step 4.4 ML Approval Registry Validator 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. Создан validator module:
   `src/mlbotnav/ml_approval_registry_validator.py`.
2. Созданы тесты:
   `tests/test_ml_approval_registry_validator.py`.
3. Validator проверяет package path, `APPROVED_FOR_ML`, manifest, `trade_log.csv` contract.
4. Real registry validation прошел на пустом registry.

Real registry validation:
1. Report: `reports/qa_gate/ml_approval_registry_validator_20260623T143704Z.json`.
2. Status: `PASS`.
3. Approved count: `0`.
4. Failures: `0`.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `74/74 OK`.
3. Registry validator: `PASS`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T143705Z.json`.

Audit: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.

Граница:
1. `approved_packages` остается пустым.
2. `APPROVED_FOR_ML` не выставлен.
3. ML ingest не запускался.

Следующий строгий WBS-пункт: `4.5 Закрытие этапа 4`.

## Step 4.3 ML Approval Registry Bans 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. В `configs/ml_approved_calibration_packages.yaml` добавлена секция `approval_bans`.
2. Зафиксирован deny result: `ML_ADMISSION_DENY`.
3. Запрещены статусы `DRAFT`, `NEEDS_AUDIT`, `NO_GO`, `VALIDATION_FAIL`, `REJECTED`, `UNKNOWN`.
4. Зафиксировано требование contract audit `PASS`.
5. Зафиксировано требование valid manifest.
6. Запрещены `raw`, `quarantine`, `raw/quarantine` как clean ML input.
7. Зафиксированы обязательные package files: `manifest.json`, `trade_log.csv`, `audit.md`.

Текущее состояние registry:
1. `approved_packages`: `[]`.
2. Approved packages count: `0`.

Проверки:
1. YAML parse: `PASS`.
2. Registry bans parse/check: `PASS`.
3. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T143132Z.json`.

Audit: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.

Граница:
1. Validator CLI/module еще не создан.
2. `APPROVED_FOR_ML` не выставлен.
3. ML ingest не запускался.

Следующий строгий WBS-пункт: `4.4 Сделать validator registry`.

## Step 4.2 ML Approval Registry Format 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. Формат manual ML approval registry описан в комментариях файла:
   `configs/ml_approved_calibration_packages.yaml`.
2. Описаны поля `run_id`, `status`, `package_path`, `approved_by`, `approved_utc`, `comment`.
3. Описаны обязательные правила для `APPROVED_FOR_ML`.
4. `approved_packages` оставлен пустым.

Текущее состояние registry:
1. `approved_packages`: `[]`.
2. Approved packages count: `0`.
3. Ни один package не добавлен.

Проверки:
1. YAML parse: `PASS`.
2. `approved_packages` length: `0`.
3. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T142740Z.json`.

Audit: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.

Граница:
1. Validator еще не создан.
2. Запреты registry еще не реализованы как validator.
3. `APPROVED_FOR_ML` не выставлен.
4. ML ingest не запускался.

Следующий строгий WBS-пункт: `4.3 Добавить запреты registry`.

## Step 4.1 ML Approval Registry File 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. Создан файл ручного ML approval registry:
   `configs/ml_approved_calibration_packages.yaml`.
2. Registry создан пустым по approved packages.
3. Ни один package не добавлен в `approved_packages`.
4. `APPROVED_FOR_ML` не выставлен.

Содержимое:
1. `schema_version`: `1`.
2. `registry_status`: `EMPTY_NO_APPROVED_PACKAGES`.
3. `manual_approval_required`: `true`.
4. `approved_packages`: `[]`.

Проверки:
1. File exists: `PASS`.
2. YAML parse: `PASS`.
3. `approved_packages` length: `0`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T142350Z.json`.

Audit: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.

Граница:
1. Формат registry еще не описан.
2. Validator еще не создан.
3. ML ingest не запускался.

Следующий строгий WBS-пункт: `4.2 Описать формат registry`.

## Stage 3 Closeout 2026-06-23
Статус: `STAGE_3_CLOSED_PASS`.

Что закрыто:
1. `3.1` package structure.
2. `3.2` `calibration_package.json`.
3. `3.3` `trade_log.csv`.
4. `3.4` source reports.
5. `3.5` `manifest.json`.
6. `3.6` package `audit.md`.
7. `3.7` closeout.

Candidate package:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Итог:
1. Все обязательные package files есть.
2. `manifest.json` валиден.
3. `trade_log.csv` проходит contract.
4. Package audit говорит `NO_GO_FOR_ML`, потому что статус `DRAFT`.
5. Package готов только к ручному review, не к ML ingest.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `71/71 OK`.
3. `ml_trade_dataset_contract PASS`: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T141708Z.json`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T141945Z.json`.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.

Граница:
1. `APPROVED_FOR_ML` не выставлен.
2. ML ingest не запускался.

Следующий строгий WBS-пункт: `4.1 Создать registry файл`.

## Step 3.6 Package Audit 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. Builder `src/mlbotnav/ml_candidate_package_builder.py` умеет создавать package-local `audit.md`.
2. Создан файл:
   `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/audit.md`.
3. Audit создается только из package-local `manifest.json`.

Содержимое:
1. Summary: `PASS`.
2. ML decision: `NO_GO_FOR_ML`.
3. Review state: `READY_FOR_MANUAL_REVIEW`.
4. Decision reason: package is `DRAFT` and requires manual approval before ML ingest.
5. Artifact list: `PASS`.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `71/71 OK`.
3. Package audit content check: `PASS`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T141517Z.json`.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.

Граница:
1. `APPROVED_FOR_ML` не выставлен.
2. ML ingest не запускался.

Следующий строгий WBS-пункт: `3.7 Закрытие этапа 3`.

## Step 3.5 Manifest 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. Builder `src/mlbotnav/ml_candidate_package_builder.py` умеет создавать package-local `manifest.json`.
2. Создан файл:
   `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/manifest.json`.
3. Manifest собирается только из package-local артефактов: `calibration_package.json`, `trade_log.csv`, `source_reports.json`.
4. Статус пакета остается `DRAFT`.

Содержимое:
1. `run_id`: `oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`.
2. `symbol/timeframe/data_layer`: `SOLUSDT / 1m / core`.
3. `train_window`: `2026-05-25` to `2026-05-26`.
4. `test_window`: `2026-05-27` to `2026-05-27`.
5. `block_id/passport_id/action_id`: `B018 / F051 / F051_BOSDOWN_ALLOW`.
6. `source_reports`: `oos_report`, `pipeline_report`, `optuna_report`.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `69/69 OK`.
3. Manifest JSON parse/content audit: `PASS`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T140937Z.json`.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.

Граница:
1. Package-level `audit.md` еще не создан.
2. `APPROVED_FOR_ML` не выставлен.

Следующий строгий WBS-пункт: `3.6 Добавить audit.md`.

## Step 3.4 Source Reports 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. Builder `src/mlbotnav/ml_candidate_package_builder.py` умеет копировать исходные отчеты в package-local `source_reports/`.
2. Создан индекс:
   `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports.json`.
3. Скопирован OOS report:
   `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/oos_report.json`.
4. Скопирован pipeline report:
   `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/pipeline_report.json`.
5. `optuna_report.json` зафиксирован как `NOT_PROVIDED` для этого кандидата.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `67/67 OK`.
3. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T140326Z.json`.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.

Граница:
1. `manifest.json` еще не создан.
2. `audit.md` еще не создан.
3. `APPROVED_FOR_ML` не выставлен.

Следующий строгий WBS-пункт: `3.5 Добавить manifest.json`.

## Step 3.3 Trade Log 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. Builder `src/mlbotnav/ml_candidate_package_builder.py` умеет копировать enriched trade CSV в package-local `trade_log.csv`.
2. Создан файл:
   `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/trade_log.csv`.
3. `trade_log.csv` прошел `ml_trade_dataset_contract`.

Contract validation:
1. Status: `PASS`.
2. Rows total: `1177`.
3. Failed rows: `0`.
4. Missing columns: `0`.
5. Report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T134753Z.json`.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `65/65 OK`.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.

Граница:
1. Source reports еще не скопированы.
2. `manifest.json` еще не создан.
3. `audit.md` еще не создан.
4. `APPROVED_FOR_ML` не выставлен.

Следующий строгий WBS-пункт: `3.4 Добавить исходные отчеты`.

## Step 3.2 Calibration Package 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. Builder `src/mlbotnav/ml_candidate_package_builder.py` умеет создавать `calibration_package.json`.
2. Создан файл:
   `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/calibration_package.json`.
3. Файл парсится и содержит обязательные поля `3.2`.
4. Статус пакета установлен как `DRAFT`.

Содержимое:
1. `run_id`: `oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`.
2. `block_id`: `B018`.
3. `passport_id`: `F051`.
4. `action_id`: `F051_BOSDOWN_ALLOW`.
5. `signal_mode`: `short_only`.
6. `calibration_params`: `4` параметра.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `63/63 OK`.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.

Граница:
1. `trade_log.csv` еще не создан.
2. `manifest.json` еще не создан.
3. `audit.md` еще не создан.
4. `APPROVED_FOR_ML` не выставлен.

Следующий строгий WBS-пункт: `3.3 Добавить trade_log.csv`.

## Step 3.1 Candidate Package Structure 2026-06-23
Статус: `CLOSED_PASS`.

Что сделано:
1. Добавлен builder `src/mlbotnav/ml_candidate_package_builder.py`.
2. Добавлены тесты `tests/test_ml_candidate_package_builder.py`.
3. Создана папка candidate package:
   `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`.
4. Builder валидирует `run_id` и запрещает path traversal.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `61/61 OK`.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.

Граница:
1. `calibration_package.json` еще не создан.
2. `trade_log.csv` еще не создан.
3. `manifest.json` еще не создан.
4. `audit.md` еще не создан.
5. `APPROVED_FOR_ML` не выставлен.

Следующий строгий WBS-пункт: `3.2 Добавить calibration_package.json`.

## Step 2.9 Stage 2 Closeout 2026-06-23
Статус: `STAGE_2_CLOSED_PASS`.

Что закрыто:
1. Stage 2 `Trade Log CSV Enrichment` закрыт целиком.
2. Pipeline trade CSV содержит contract fields и проходит валидатор.
3. OOS trade CSV содержит contract fields и проходит валидатор.
4. Required columns audit `PASS`.
5. `text_guard PASS`.

Финальная проверка:
1. Pipeline CSV: `reports/pipeline/backtest_trades_SOLUSDT_1m_20260623T132424Z.csv`.
2. Pipeline validator report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133238Z.json`.
3. OOS CSV: `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.csv`.
4. OOS validator report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133240Z.json`.
5. Focused tests: `59/59 OK`.
6. Text guard: `reports/qa_gate/recovery_r5_text_guard_20260623T133249Z.json`.

Closeout audit: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.

Граница:
1. Stage 2 закрывает готовность trade CSV по контракту.
2. Stage 2 не означает автоматический `APPROVED_FOR_ML`.
3. Stage 3 должен собрать отдельный candidate package.

Следующий строгий WBS-пункт: `3.1 Создать структуру пакета`.

## Step 2.8 OOS CSV 2026-06-23
Статус: `CLOSED_PASS`.

Что закрыто:
1. Запущен свежий OOS на основе `reports/pipeline/pipeline_report_SOLUSDT_1m_20260623T132424Z.json`.
2. OOS использовал `--layer core`.
3. Создан свежий OOS trade CSV: `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.csv`.
4. CSV прошел `ml_trade_dataset_contract`.

Результат OOS:
1. Net return pct: `-0.9395906630311424`.
2. Trades: `3`.
3. Goal pass: `false`.

Contract validation:
1. Status: `PASS`.
2. Rows total: `1177`.
3. Failed rows: `0`.
4. Missing columns: `0`.

Audit: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.
Validator report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T132804Z.json`.
OOS log: `reports/logs/step2_8_oos_core_20260623T132801Z.log`.

Следующий строгий WBS-пункт: `2.9 Закрытие этапа 2`.

## Step 2.7 Pipeline CSV 2026-06-23
Статус: `CLOSED_PASS_AFTER_CONTROLLED_TEMP_UNLOCK`.

Что сделано:
1. В `pipeline_train_eval.py` добавлен параметр `--layer`.
2. Pipeline теперь читает выбранный слой через `load_ohlcv_range(..., layer=args.layer)`.
3. Pipeline trade CSV теперь пишет фактический `data_layer=args.layer`, а не hardcoded `raw`.
4. Старый последний pipeline CSV проверен контрактным валидатором и получил ожидаемый `FAIL`, потому что это stale artifact до enrichment.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `59/59 OK`.
3. Existing CSV contract check: `FAIL`, missing required columns `20`, failed rows `254/254`.

Финальное закрытие:
1. Controlled temporary unlock использован только для короткого validation-run.
2. Свежий pipeline CSV создан: `reports/pipeline/backtest_trades_SOLUSDT_1m_20260623T132424Z.csv`.
3. Contract validation: `PASS`.
4. Rows total: `2072`.
5. Failed rows: `0`.
6. Missing columns: `0`.
7. Readiness восстановлен обратно: `project_ready=false`, `enforce_freeze=true`.

Audit: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.
Validator report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T131723Z.json`.
Readiness report: `reports/readiness/readiness_check_20260623T131731Z.json`.
Final validator report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T132425Z.json`.
Final pipeline log: `reports/logs/step2_7_pipeline_core_20260623T132421Z.log`.

Следующий строгий WBS-пункт: `2.8 Проверить OOS CSV`.

## Step 2.6 MAE/MFE 2026-06-23
Статус: `CLOSED_PASS`.

Что закрыто:
1. В ML trade CSV enrichment добавлены `mae_pct` и `mfe_pct`.
2. Pipeline writer теперь добавляет MAE/MFE перед записью `reports/pipeline/backtest_trades_*.csv`.
3. OOS writer теперь добавляет MAE/MFE перед записью `reports/final_review/oos_backtest_trades_*.csv`.
4. LONG/SHORT считаются раздельно и зеркально.
5. Для строк без сделки MAE/MFE остаются пустыми.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `59/59 OK`.
3. `text_guard PASS`.

Audit: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.
Text guard: `reports/qa_gate/recovery_r5_text_guard_20260623T130950Z.json`.

Следующий строгий WBS-пункт: `2.7 Проверить pipeline CSV`.

## Паспортный реестр блоков 2026-06-22T12:57:27Z
Статус: `ACTIVE_BLOCK_PASSPORT_REGISTRY`.

Рабочее правило зафиксировано в `configs/calibration_action_passports.yaml`.

Принята структура:
1. `B001`, `B002`, `B003` и дальше - это блоки калибровки с русским названием и техническим `block_key`.
2. Внутри блока лежат паспорта фич/действий: `F001`, `F002`, `F003` и дальше.
3. Паспорт является смысловым источником правил: что калибруется, какие min/max/step, какие линии/пороги двигаются, что запрещено смешивать.
4. YAML-матрица под Optuna является исполняемой версией паспорта.
5. Optuna и backtest должны читать только параметры и runtime action columns, объявленные в реестре и паспорте.

Текущий `B001`:
1. Русское имя: `Цена и волатильность`.
2. Технический ключ: `price_volatility`.
3. Активные фичи: `F001` `ret_1`, `F002` `ret_3`, `F003` `ret_6`, `F004` `ret_12`, `F005` `ret_24`.
4. Комбинированный `B001_RET_N_TOURNAMENT` оставлен только как diagnostic-only; baseline-режим для B001 - solo feature selection.
5. Последний B001 LONG solo-run: технически OK, но кандидат `NO_GO`; лучший F002 дал `-0.2436%` OOS и `1` сделку.

Блоки в реестре:
1. `B001` - `Цена и волатильность / RET_N` / активные `F001-F005`.
2. `B002` - `Диапазон свечи High-Low` / активный `F006`.
3. `B003+` - следующие пользовательские паспортные блоки добавляются по очереди.

Следующее правило работы: когда пользователь дает новый паспорт, сначала определить блок `Bxxx`, записать русское имя/комментарий, затем добавить паспорт в реестр и только после этого создавать/обновлять исполняемую матрицу.

## F006 HL Spread 1m 2026-06-22T13:10:45Z
Статус: `IMPLEMENTED_RUN_AUDITED_NO_GO`.

Что сделано:
1. Добавлен паспорт `F006` в блок `B002` / `Диапазон свечи High-Low`.
2. Добавлена матрица `configs/calibration_matrices/passport_actions/F006_hl_spread_1m_entry_filter.yaml`.
3. Runtime теперь создает `F006_HLSPREAD_ALLOW` при наличии `F006_cmp` / `F006_thr_pct`.
4. Backtest entry gate учитывает `F006_HLSPREAD_ALLOW`.
5. Проверки: matrix compile `PASS`, focused tests `35/35 OK`, py_compile `PASS`.

Чистый LONG-прогон:
1. Train `2026-05-31`, test `2026-06-01`, grid `wide`, trials `180`.
2. Лучшие параметры: `F006_cmp=-1` (`LESS`), `F006_thr_pct=0.75`.
3. OOS `-6.153363933968025%`, trades `2`, wins `0`, losses `2`.
4. Train gate `FAIL`, goal `FAIL`, candidate `NO_CANDIDATE`.

Audit artifact: `reports/qa_gate/f006_hl_spread_long_only_audit_20260622T131045Z.json`.
Readable report: `reports/qa_gate/f006_hl_spread_long_only_audit_20260622T131045Z_RU.md`.

Важное замечание аудита: первый 3-worker pool-прогон технически завершился OK, но обнаружен риск same-second collision в `final_review/top-card` артефактах. Для финального вывода по F006 использован чистый direct contour прогон.

Коррекция 2026-06-22: F006 не относится к `B001`; по пользовательской нумерации это `B002/F006`. Реестр и матрица исправлены: `configs/calibration_action_passports.yaml`, `configs/calibration_matrices/passport_actions/F006_hl_spread_1m_entry_filter.yaml`.

## F007 Rolling Std20 1m 2026-06-22T13:33:18Z
Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Что сделано:
1. Добавлен паспорт `F007` в блок `B003` / `Скользящая волатильность 20`.
2. Добавлена матрица `configs/calibration_matrices/passport_actions/F007_rolling_std20_1m_entry_filter.yaml`.
3. Runtime теперь создает `F007_RSTD20_ALLOW` при наличии `F007_cmp` / `F007_thr_pct`.
4. Backtest entry gate учитывает `F007_RSTD20_ALLOW`.
5. Проверки: matrix compile `PASS`, focused tests `37/37 OK`, py_compile `PASS`.

LONG:
1. Train `2026-05-31`, test `2026-06-01`, grid `wide`, trials `180`.
2. Лучшие параметры: `F007_cmp=1` (`GREATER`), `F007_thr_pct=0.04`.
3. OOS `-1.1459443803135683%`, trades `1`, wins `0`, losses `1`.
4. Train gate `FAIL`, goal `FAIL`, candidate `NO_CANDIDATE`.

SHORT:
1. Train `2026-05-31`, test `2026-06-01`, grid `wide`, trials `180`.
2. Лучшие параметры: `F007_cmp=-1` (`LESS`), `F007_thr_pct=0.34`.
3. OOS `-5.744959575084807%`, trades `3`, wins `0`, losses `3`.
4. Train gate `FAIL`, goal `FAIL`, candidate `NO_CANDIDATE`.

Audit artifact: `reports/qa_gate/f007_rolling_std20_long_short_audit_20260622T133318Z.json`.
Readable report: `reports/qa_gate/f007_rolling_std20_long_short_audit_20260622T133318Z_RU.md`.

## F008 ATR14 1m 2026-06-22T13:59:47Z
Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Что сделано:
1. Добавлен паспорт `F008` в блок `B004` / `ATR14 волатильность`.
2. Добавлена матрица `configs/calibration_matrices/passport_actions/F008_atr14_1m_entry_filter.yaml`.
3. Runtime теперь создает `F008_ATR14_ALLOW` при наличии `F008_cmp` / `F008_thr_pct`.
4. Backtest entry gate учитывает `F008_ATR14_ALLOW`.
5. Проверки: matrix compile `PASS`, focused tests `39/39 OK`, py_compile `PASS`.

LONG:
1. Train `2026-05-31`, test `2026-06-01`, grid `wide`, trials `180`.
2. Лучшие параметры: `F008_cmp=-1` (`LESS`), `F008_thr_pct=0.28`.
3. OOS `-1.1459443803135683%`, trades `1`, wins `0`, losses `1`.
4. Train gate `FAIL`, goal `FAIL`, candidate `NO_CANDIDATE`.

SHORT:
1. Train `2026-05-31`, test `2026-06-01`, grid `wide`, trials `180`.
2. Лучшие параметры: `F008_cmp=-1` (`LESS`), `F008_thr_pct=2.33`.
3. OOS `-5.744959575084807%`, trades `3`, wins `0`, losses `3`.
4. Train gate `FAIL`, goal `FAIL`, candidate `NO_CANDIDATE`.

Audit artifact: `reports/qa_gate/f008_atr14_long_short_audit_20260622T135947Z.json`.
Readable report: `reports/qa_gate/f008_atr14_long_short_audit_20260622T135947Z_RU.md`.

## EMA F009-F011 2026-06-22T14:34:20Z
Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Что сделано:
1. Добавлен семейный паспорт `EMA_F009_F011` в блок `B005` / `EMA тренд и наклон`.
2. Добавлены матрицы:
   - `configs/calibration_matrices/passport_actions/F009_ema_gap_20_50_1m_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F010_ema20_slope_5_1m_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F011_ema200_gap_1m_entry_filter.yaml`.
3. Runtime теперь создает `F009_EMAGAP_ALLOW`, `F010_EMASLOPE5_ALLOW`, `F011_EMA200GAP_ALLOW` только при наличии параметров соответствующего паспорта.
4. Backtest entry gate учитывает все три EMA action columns.
5. Проверки: matrix compile `PASS`, focused tests `41/41 OK`, py_compile `PASS`.

Результаты:
1. `F009 LONG`: `ABOVE`, `thr=0.12%`, OOS `0.0000%`, trades `0`, candidate `NO_CANDIDATE`.
2. `F009 SHORT`: `BELOW`, `thr=0.12%`, OOS `-18.167609882040235%`, trades `9`, wins `2`, losses `7`, candidate `NO_CANDIDATE`.
3. `F010 LONG`: `DOWN`, `thr=0.01%`, OOS `-29.10662198785241%`, trades `10`, wins `1`, losses `9`, candidate `NO_CANDIDATE`.
4. `F010 SHORT`: `DOWN`, `thr=0.04%`, OOS `-18.617757232213172%`, trades `5`, wins `0`, losses `5`, candidate `NO_CANDIDATE`.
5. `F011 LONG`: `ABOVE`, `thr=0.75%`, OOS `0.0000%`, trades `0`, candidate `NO_CANDIDATE`.
6. `F011 SHORT`: `ABOVE`, `thr=0.65%`, OOS `0.0000%`, trades `0`, candidate `NO_CANDIDATE`.

Итог: tradeful результата нет; блок `B005/EMA F009-F011` закрыт как `NO_GO`.

Audit artifact: `reports/qa_gate/ema_f009_f011_long_short_audit_20260622T143420Z.json`.
Readable report: `reports/qa_gate/ema_f009_f011_long_short_audit_20260622T143420Z_RU.md`.

## F012 RSI14 combined 2026-06-22T14:47:50Z

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Что сделано:
1. Добавлен паспорт `F012` в блок `B006` / `RSI14 combined`.
2. Добавлена матрица `configs/calibration_matrices/passport_actions/F012_rsi14_combined_entry_filter.yaml`.
3. Runtime теперь создает `F012_RSI14_ALLOW` при наличии F012 params.
4. Backtest entry gate учитывает `F012_RSI14_ALLOW`.
5. Проверки: matrix compile `PASS`, focused tests `43/43 OK`, py_compile `PASS`.
6. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260622T145323Z.json`.

LONG:
1. Clean sequential run `OK`.
2. Лучшие параметры: `LEVEL`, `GREATER`, `level=88`.
3. OOS `0.0000%`, trades `0`, candidate `NO_CANDIDATE`.

SHORT:
1. Launcher `OK`.
2. Лучшие параметры: `LEVEL`, `GREATER`, `level=30`.
3. OOS `-47.5754123715459%`, trades `22`, wins/losses by net return `1/21`, exits `timeout=22`.
4. Candidate `NO_CANDIDATE`.

Итог: `B006/F012 RSI14` технически подключен, но tradeful non-negative результата нет. Статус `NO_GO`.

Audit artifact: `reports/qa_gate/f012_rsi14_combined_long_short_audit_20260622T144750Z.json`.
Readable report: `reports/qa_gate/f012_rsi14_combined_long_short_audit_20260622T144750Z_RU.md`.

## MACD F013-F015 2026-06-22T15:19:54Z

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Что сделано:
1. Добавлен семейный паспорт `MACD_F013_F015` в блок `B007` / `MACD импульс`.
2. Добавлены матрицы:
   - `configs/calibration_matrices/passport_actions/F013_macd_line_1m_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F014_macd_signal_1m_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F015_macd_hist_1m_entry_filter.yaml`.
3. Runtime теперь создает `F013_MACDLINE_ALLOW`, `F014_MACDSIGNAL_ALLOW`, `F015_MACDHIST_ALLOW` только при наличии параметров соответствующего паспорта.
4. Backtest entry gate учитывает все три MACD action columns.
5. Исправлен риск старых хвостов Optuna: `run_signature` теперь включает `space_signature` от исполняемой паспортной матрицы. Предварительные MACD-прогоны до фикса отброшены и перезапущены чисто.
6. Проверки: matrix compile `PASS`, focused tests `112/112 OK`, py_compile `PASS`, `text_guard PASS`.

Чистые результаты:
1. `F013 LONG`: `NEGATIVE`, `thr=0.00%`, OOS `0.000000%`, trades `0`, candidate `NO_CANDIDATE`.
2. `F013 SHORT`: `NEGATIVE`, `thr=0.00%`, OOS `-18.625751%`, trades `6`, wins/losses `0/6`, exits `timeout=6`, candidate `NO_CANDIDATE`.
3. `F014 LONG`: `NEGATIVE`, `thr=0.11%`, OOS `-2.977908%`, trades `3`, wins/losses `0/3`, exits `timeout=3`, candidate `NO_CANDIDATE`.
4. `F014 SHORT`: `NEGATIVE`, `thr=0.07%`, OOS `-20.546537%`, trades `6`, wins/losses `0/6`, exits `timeout=6`, candidate `NO_CANDIDATE`.
5. `F015 LONG`: `POSITIVE`, `thr=0.00%`, OOS `-4.992098%`, trades `1`, wins/losses `0/1`, exit `timeout=1`, candidate `NO_CANDIDATE`.
6. `F015 SHORT`: `NEGATIVE`, `thr=0.01%`, OOS `-5.883887%`, trades `1`, wins/losses `0/1`, exit `timeout=1`, candidate `NO_CANDIDATE`.

Итог: tradeful non-negative результата нет; блок `B007/MACD F013-F015` закрыт как `NO_GO`.

Audit artifact: `reports/qa_gate/macd_f013_f015_long_short_audit_20260622T151954Z.json`.
Readable report: `reports/qa_gate/macd_f013_f015_long_short_audit_20260622T151954Z_RU.md`.
Text guard: `reports/qa_gate/recovery_r5_text_guard_20260622T152122Z.json`.

## F016 ADX14 2026-06-22T15:34:03Z

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Что сделано:
1. Добавлен паспорт `F016` в блок `B008` / `ADX14 сила тренда`.
2. Добавлена матрица `configs/calibration_matrices/passport_actions/F016_adx14_1m_entry_filter.yaml`.
3. Runtime теперь создает `F016_ADX14_ALLOW` при наличии `F016_cmp` / `F016_level`.
4. Backtest entry gate учитывает `F016_ADX14_ALLOW`.
5. Проверки: matrix compile `PASS`, focused tests `114/114 OK`, py_compile `PASS`.

LONG:
1. Train `2026-05-31`, test `2026-06-01`, grid `wide`, trials `180`.
2. Лучшие параметры: `LESS`, `level=41`.
3. OOS `-13.43232421418481%`, trades `3`, wins/losses `0/3`, exits `timeout=3`.
4. Candidate `NO_CANDIDATE`.

SHORT:
1. Train `2026-05-31`, test `2026-06-01`, grid `wide`, trials `180`.
2. Лучшие параметры: `LESS`, `level=28`.
3. OOS `-28.526707456698695%`, trades `13`, wins/losses `1/12`, exits `timeout=13`.
4. Candidate `NO_CANDIDATE`.

Итог: `F016_ADX14_ALLOW` технически подключен и реально режет входы, но tradeful non-negative результата нет. Блок `B008/F016 ADX14` закрыт как `NO_GO`.

Audit artifact: `reports/qa_gate/f016_adx14_long_short_audit_20260622T153403Z.json`.
Readable report: `reports/qa_gate/f016_adx14_long_short_audit_20260622T153403Z_RU.md`.

## STOCH F017-F018 2026-06-22T15:43:40Z

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Что сделано:
1. Добавлен комбинированный паспорт `F017_F018` в блок `B009` / `Stochastic 14 K/D`.
2. Добавлена матрица `configs/calibration_matrices/passport_actions/F017_F018_stoch14_combined_entry_filter.yaml`.
3. Runtime теперь создает `F017_F018_STOCH14_ALLOW` при наличии параметров `F017_F018_*`.
4. Backtest entry gate учитывает `F017_F018_STOCH14_ALLOW`.
5. Проверки: matrix compile `PASS`, focused tests `116/116 OK`, py_compile `PASS`.

LONG:
1. Train `2026-05-31`, test `2026-06-01`, grid `wide`, trials `180`.
2. Эффективные параметры: `LEVEL`, line `K`, cmp `LESS`, level `72`.
3. OOS `-84.05333161848922%`, trades `51`, wins/losses `2/49`, exits `timeout=50`, `sl=1`.
4. Candidate `NO_CANDIDATE`.

SHORT:
1. Train `2026-05-31`, test `2026-06-01`, grid `wide`, trials `180`.
2. Эффективные параметры: `KD_CROSS`, cross `UP`, zone `LOW`, low `40`, high `60`, gap `0`.
3. OOS `-17.53680624691214%`, trades `6`, wins/losses `0/6`, exits `timeout=6`.
4. Candidate `NO_CANDIDATE`.

Итог: `F017_F018_STOCH14_ALLOW` технически подключен и реально режет входы, но tradeful non-negative результата нет. Блок `B009/STOCH F017-F018` закрыт как `NO_GO`.

Audit artifact: `reports/qa_gate/stoch_f017_f018_long_short_audit_20260622T154340Z.json`.
Readable report: `reports/qa_gate/stoch_f017_f018_long_short_audit_20260622T154340Z_RU.md`.

Дополнение 2026-06-23: решение по split-vs-combined закрыто.
`F017/F018` оставлены одним combined-паспортом `F017_F018`, потому что `%K` и `%D` - две линии одного Stochastic-инструмента, а режим `KD_CROSS` требует обе линии внутри одного action grammar.
Это не смешивание разных инструментов и не старый Optuna-комбо-блок.
Audit artifact: `reports/qa_gate/f017_f018_combined_decision_audit_20260623T081000Z.md`.

## Stale action-column hardening 2026-06-23T08:20:00Z

Статус: `FIXED_FOCUSED_TESTS_PASS`.

Что исправлено:
1. `run_prob_backtest` получил явный `active_entry_action_columns`.
2. Optuna passport search передает текущий `passport_mode.action_id` в backtest.
3. Если явный allowlist не передан, backtest выводит активное действие из `Fxxx_*` параметров паспорта.
4. Старые неродные `F*_ALLOW` колонки, случайно лежащие в DataFrame, больше не применяются как дополнительные gate в passport route.

Проверка:
1. stale/F039 focused tests: `2/2 OK`.
2. `tests.test_backtest_fields`: `43/43 OK`.
3. project venv `tests.test_backtest_fields tests.test_optuna_search_runtime`: `110/110 OK`.
4. py_compile измененных модулей: `PASS`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T081355Z.json`.

Audit artifact: `reports/qa_gate/stale_action_column_hardening_20260623T082000Z.md`.

## VOLUME F019-F021 2026-06-22T16:02:07Z

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Что сделано:
1. Добавлено семейство `F019-F021` в блок `B010` / `Объем и поток`.
2. Добавлены матрицы:
   - `configs/calibration_matrices/passport_actions/F019_vol_chg_1m_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F020_vol_z20_1m_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F021_delta_volume_1m_entry_filter.yaml`.
3. Runtime теперь создает `F019_VOLCHG_ALLOW`, `F020_VOLZ20_ALLOW`, `F021_DELTAVOL_ALLOW` только при наличии параметров соответствующего паспорта.
4. Backtest entry gate учитывает все три volume action columns.
5. Исправлен F021: `TRUE_DELTA` теперь требует `buy_volume`/`sell_volume`; если этих колонок нет, сигнал `0`. Старые pre-fix F021 прогоны отброшены и F021 перезапущен чисто.
6. Проверки: matrix compile `PASS`, focused tests `118/118 OK`, py_compile `PASS`.

Результаты:
1. `F019 LONG`: `UP`, `thr=105%`, OOS `-57.151405216570964%`, trades `26`, wins/losses `0/26`, exits `timeout=26`.
2. `F019 SHORT`: `DOWN`, `thr=10%`, OOS `-11.835583993372524%`, trades `4`, wins/losses `1/3`, exits `timeout=4`.
3. `F020 LONG`: `HIGH`, `z=3.6`, OOS `0.000000%`, trades `0`.
4. `F020 SHORT`: `HIGH`, `z=0.5`, OOS `-25.29089583299876%`, trades `9`, wins/losses `0/9`, exits `timeout=9`.
5. `F021 LONG`: `PROXY_DELTA`, `SELL`, `thr=50%`, OOS `-77.6999063229171%`, trades `37`, wins/losses `1/36`, exits `timeout=36`, `sl=1`.
6. `F021 SHORT`: `TRUE_DELTA`, `BUY`, `thr=5%`, OOS `0.000000%`, trades `0`; в текущих данных нет `buy_volume/sell_volume`, поэтому gate дал `0` сигналов.

Итог: tradeful non-negative результата нет; блок `B010/VOLUME F019-F021` закрыт как `NO_GO`.

Audit artifact: `reports/qa_gate/volume_f019_f021_long_short_audit_20260622T160207Z.json`.
Readable report: `reports/qa_gate/volume_f019_f021_long_short_audit_20260622T160207Z_RU.md`.

## Активный фокус
Доводим калибровочный узел по новому ТЗ `2026-06-03T10:25:00Z` и новому уточненному ТЗ последовательного перебора `2026-06-03T12:16:43Z`.

Текущий `TOP_EXPERIMENTAL` кандидат поставлен на паузу. Production/unfreeze/forward F1-F2 не запускаем.

Правило движения: берем следующий шаг только из `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`, запускаем, фиксируем результат, затем переключаем команду на следующий шаг.

## Optuma bridge current 2026-06-04T06:55:00Z
Активное короткое правило: `docs/CALIBRATION_NODE_CURRENT/TZ_OPTUMA_BRIDGE_CURRENT_2026-06-04_RU.md`.

Смысл: работаем через текущий калибровочный контур `Optuma`, старый конфиг `configs/calibration_feature_hypothesis_draft.yaml` используем как мост с min/max, а текущую матрицу `configs/calibration_full_matrix_v1.yaml` и runtime-аудит используем как active current.

Правило: перед прогоном блока сверяем параметры `min/max/step`, проверяем, что параметр реально подключен в коде, ремонтируем разрывы, затем калибруем `long_only` и `short_only` отдельно по `narrow / medium / wide`. Блок закрывается только после логов, artifacts и итоговой фиксации.

## Optuma bridge step 1: calibration_params anchor gap fixed 2026-06-04T08:56:24Z
Статус: `FIXED_FOCUSED_TESTS_PASS`.

Что сделано:
1. `src/mlbotnav/adaptive_auto_train.py`: выбранный Optuna candidate теперь сохраняет `calibration_params` в step и передает их в `pipeline_train_eval` через `--calibration-params-json`.
2. `src/mlbotnav/pipeline_train_eval.py`: добавлен прием `--calibration-params-json`; train-фичи строятся через `build_feature_frame(..., calibration_params=...)`; final train backtest получает те же параметры; параметры сохраняются в train report и model payload.
3. `src/mlbotnav/oos_evaluate.py`: OOS берет `calibration_params` из train report / risk policy / model payload и применяет их в `build_feature_frame` и финальном `run_prob_backtest`.
4. `tests/test_pipeline_train_eval_gate_overrides.py`: добавлены проверки парсинга/нормализации calibration params.

Проверка:
1. `py_compile` измененных файлов: `PASS`.
2. Focused tests: `79/79 OK`:
   `tests.test_pipeline_train_eval_gate_overrides`,
   `tests.test_adaptive_candidate_pick`,
   `tests.test_optuna_search_runtime`,
   `tests.test_backtest_fields`.

Итог: главный anchor gap закрыт на уровне кода и focused tests. Следующий ремонт по текущему списку: `volume_flow` формулы `vol_chg`, `delta_volume`, `obv_slope_5`.

## Принятое правило нумерации и читаемого отчета
1. `H001`, `H002`, `H003` и дальше — это номера слотов фич/гипотез.
2. Long и short не получают новые номера слотов.
3. Внутри слота используем читаемые дочерние карточки:
   - `H001-LONG` — long-стек слота `H001`;
   - `H001-SHORT` — short-стек слота `H001`;
   - `H001-SLOT` — общий итог слота.
4. `H002` — следующий слот по списку (`price_volatility.ret_3`), а не short от `H001`.
5. Для человека фиксируем результат в боевом читаемом формате: в заголовке карточки пишем только номер слота и короткое русское название инструмента/гипотезы из словаря `configs/features_block.yaml`, например `H003 | Доходность за 6 баров`; ниже оставляем тип, блок, техническое имя, параметры калибровки, диапазон min/max/step, результаты `narrow/medium/wide` по long и short, лучший long, лучший short, итог.
6. Читаемый отчет: `reports/optuna_catalog/index/hypothesis_feature_sweep_human_ru.md`.
7. Каталог русских названий фич и гипотез: `docs/CALIBRATION_NODE_CURRENT/RU_NAMES_CATALOG_2026-06-03.md`.

## Закрытые блоки
1. `volume_flow`: `CLOSED_RUNTIME_OK`, best `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, не production.
2. `density_profile`: `CLOSED_RUNTIME_OK`, best `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, не production.
3. `structure_ta`: `CLOSED_RUNTIME_OK`, best `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, не production.
4. `pattern`: `CLOSED_RUNTIME_OK`, best `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, не production.

## Текущий блок: pattern
Статус блока: `CLOSED_RUNTIME_OK`.

### pattern narrow
1. `long_only`: launcher `OK`, workers `3/3 exit_code=0`, best OOS `0%`, trades `0`, class `NO_CANDIDATE`, не candidate.
2. Long summary: `reports/adaptive/long_only_pool_20260603t111454z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T111457Z.json`.
3. `short_only`: launcher `OK`, workers `3/3 exit_code=0`, best OOS `0%`, trades `0`, class `NO_CANDIDATE`, не candidate.
4. Short summary: `reports/adaptive/short_only_pool_20260603t111643z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T111646Z.json`.

### pattern medium
1. `long_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w3`, best OOS `+1.5266529420731034%`, trades `1`, `goal_pass=true`, `train_gate=false`, class `TOP_EXPERIMENTAL`, не production.
2. Long negative history: worker `w2` дал `-9.6798036292287%`, trades `3`.
3. Long summary: `reports/adaptive/long_only_pool_20260603t111825z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T111828Z.json`.
4. Long top experimental card: `reports/top_strategy/long_only_pool_20260603t111825z_w3/top_SOLUSDT_1m_2026-06-01_20260603T111907Z_MODE-LONG_ONLY_TF-1M_RET-+1.5267pct/top_strategy_card.json`.
5. `short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w3`, best OOS `0%`, trades `0`, class `NO_CANDIDATE`, не candidate.
6. Short negative history: worker `w2` дал `-0.70181819597614492%`, trades `1`.
7. Short summary: `reports/adaptive/short_only_pool_20260603t112010z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T112014Z.json`.
8. Short top card: `reports/top_strategy/short_only_pool_20260603t112010z_w3/top_SOLUSDT_1m_2026-06-01_20260603T112053Z_MODE-SHORT_ONLY_TF-1M_RET-+0.0000pct/top_strategy_card.json`.

### pattern wide
1. `long_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w3`, best OOS `+1.5266529420731034%`, trades `1`, `goal_pass=true`, `train_gate=false`, class `TOP_EXPERIMENTAL`, не production.
2. Long negative history: worker `w2` дал `-9.6798036292287%`, trades `3`; worker `w1` дал `0%`, trades `0`.
3. Long summary: `reports/adaptive/long_only_pool_20260603t112335z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T112338Z.json`.
4. Long top experimental card: `reports/top_strategy/long_only_pool_20260603t112335z_w3/top_SOLUSDT_1m_2026-06-01_20260603T112433Z_MODE-LONG_ONLY_TF-1M_RET-+1.5267pct/top_strategy_card.json`.
5. `short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w3`, best OOS `0%`, trades `0`, class `NO_CANDIDATE`, не candidate.
6. Short negative history: worker `w2` дал `-2.1235297408523923%`, trades `1`.
7. Short summary: `reports/adaptive/short_only_pool_20260603t112536z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T112539Z.json`.
8. Short top card: `reports/top_strategy/short_only_pool_20260603t112536z_w3/top_SOLUSDT_1m_2026-06-01_20260603T112631Z_MODE-SHORT_ONLY_TF-1M_RET-+0.0000pct/top_strategy_card.json`.

## Closeout pattern
Artifact: `reports/qa_gate/calibration_node_pattern_closeout_20260603T112654Z.json`.

Итог: `pattern` прошел `narrow/medium/wide` x `long_only/short_only` без worker crash. Лучший результат блока: `wide long_only`, OOS `+1.5266529420731034%`, trades `1`, class `TOP_EXPERIMENTAL`, не production из-за `train_gate=false`.

## Лучший результат pattern на данный момент
`pattern medium long_only`: `+1.5266529420731034%`, trades `1`, class `TOP_EXPERIMENTAL`, не production.

## Исправленные дефекты
1. `src/mlbotnav/adaptive_auto_train.py`: безопасное чтение search report через `_read_json_report_with_retry`.
2. `src/mlbotnav/adaptive_auto_train.py`: безопасное чтение OOS report через `_read_json_report_with_retry`.

Проверка после фиксов: focused tests `83/83 OK`.

## Последние health checks
1. `text_guard`: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T113212Z.json`.
2. readiness: freeze preserved, `project_ready=false`, `enforce_freeze=true`, artifact `reports/readiness/readiness_check_20260603T112818Z.json`.
3. `pip check`: `PASS`.
4. Последний `text_guard` после нового ТЗ: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T122016Z.json`.
5. Последний `text_guard` после правки читаемых заголовков карточек и каталога RU-названий: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T160749Z.json`.
6. Последний `text_guard` после сверки блоков APTuna: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T165036Z.json`.
7. Последний `text_guard` после audit блокового режима: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T170046Z.json`.
8. Последний `text_guard` после замены JSON на ASCII-safe artifact: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T171710Z.json`.
9. Последний `text_guard` после сравнения старого конфига с текущей матрицей: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T172635Z.json`.
10. Последний `text_guard` после фиксации FIBO-решения: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T180424Z.json`.
11. Последний `text_guard` после дополнения ТЗ по фигурным паттернам: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T051213Z.json`.
12. Последний `text_guard` после жесткого runtime-аудита current-блоков: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T064803Z.json`.
13. Последний `text_guard` после Optuma bridge Step 1: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T085730Z.json`.

## Сверка блоков калибровки с APTuna 2026-06-03T16:48:08Z
Artifact: `reports/qa_gate/aptuna_block_alignment_audit_20260603T164808Z.json`.

Итог: `PASS`, `issues=0`, `blockers=0`.

Сошлись все 6/6 блоков:
1. `price_volatility` — Цена и волатильность.
2. `trend_momentum` — Тренд и импульс.
3. `volume_flow` — Объем и поток.
4. `density_profile` — Профиль плотности.
5. `structure_ta` — Структура и ТА.
6. `pattern` — Паттерны.

Проверено по источникам: `src/mlbotnav/dataset.py`, `configs/features_block.yaml`, `configs/calibration_feature_hypothesis_draft.yaml`, `configs/calibration_full_matrix_v1.yaml`, `configs/calibration_matrices/catalog_blocks/*.yaml`, APTuna runner через `MLBOTNAV_CALIBRATION_MATRIX_PATH`.

Факты аудита:
1. В полной матрице `68` feature rows: `56` калибруются, `12` фиксированные.
2. В полной матрице `20/20` hypothesis rows калибруются.
3. `volume_flow` и `price_volatility` включены как always-on context blocks.
4. Все 6 catalog block matrices компилируются для `long_only` и `short_only` на `narrow/medium/wide`.
5. Сгенерированные sequential feature_sweep matrices сейчас есть для `H001` и `H002`; `H003` еще не сгенерирован, потому что это следующий строгий шаг, а не ошибка сверки.

## Audit блокового режима vs одиночного feature sweep 2026-06-03T16:59:00Z
Artifact: `reports/qa_gate/aptuna_block_vs_feature_sweep_audit_20260603T170400Z.json`.

Читаемый документ: `docs/CALIBRATION_NODE_CURRENT/BLOCK_VS_FEATURE_SWEEP_AUDIT_2026-06-03_RU.md`.

Примечание: старый машинный artifact `reports/qa_gate/aptuna_block_vs_feature_sweep_audit_20260603T165900Z.json` заменен новым ASCII-safe JSON из-за риска кракозябр при открытии в Windows/PowerShell.

Итог: `PASS_WITH_MODE_BOUNDARY`.

Вывод:
1. `configs/calibration_matrices/catalog_blocks/*.yaml` - это блоковая калибровка. Берется целевой блок целиком, все его `feature_rows` и общий union-набор параметров блока.
2. `configs/calibration_matrices/feature_sweep/h*.yaml` - это одиночный feature-slot режим. `H001` и `H002` содержат по одной feature row и не являются полной калибровкой блока.
3. APTuna калибрует то, какую матрицу передали через `-CalibrationMatrixPath` / `MLBOTNAV_CALIBRATION_MATRIX_PATH`.
4. Если цель - калибровать блоки целиком, следующий рабочий маршрут нужно строить по `catalog_blocks`, а не продолжать `H003` как основной боевой путь.
5. `H001/H002/H003` можно оставить только как диагностический одиночный режим.

## Сравнение старого конфига с текущей матрицей 2026-06-03T17:32:00Z
Старый конфиг: `configs/calibration_feature_hypothesis_draft.yaml`.

Текущая матрица: `configs/calibration_full_matrix_v1.yaml`.

Читаемый документ: `docs/CALIBRATION_NODE_CURRENT/BLOCK_PARAM_MATRIX_OLD_VS_CURRENT_2026-06-03_RU.md`.

Машинный artifact: `reports/qa_gate/calibration_old_vs_current_block_params_20260603T173200Z.json`.

Итог: `PASS_WITH_ONE_NOTABLE_GAP`.

Вывод:
1. Старый конфиг действительно содержит `min/max/step/count` по каждому блоку.
2. В текущей матрице почти все диапазоны сохранены, но старые имена параметров нормализованы в канонические профили.
3. Единственный явный разрыв: старый `fib_level` (`min=0.236`, `max=0.786`, `step=0.146`, `count=5`) сейчас не представлен как отдельный текущий profile. В текущей матрице `fib_0382_distance` и `fib_0618_distance` калибруют `rolling_window`, а сами уровни 0.382/0.618 фиксированные.
4. Перед блоковым боевым маршрутом нужно решить: вернуть `fib_level` в матрицу или явно оставить уровни Фибо фиксированными.

## Решение по FIBO в `structure_ta` 2026-06-03T17:45:00Z
Документ: `docs/CALIBRATION_NODE_CURRENT/FIBO_STRUCTURE_TA_DECISION_2026-06-03_RU.md`.

Решение:
1. FIBO возвращаем в `structure_ta` как нормальный технический блок.
2. Алгоритм сам натягивает Фибо по окну: для `long_only` от low к high, для `short_only` зеркально от high к low.
3. Сам факт натягивания не калибруется; это расчетная процедура.
4. Калибруются `fib_window`, `fib_level`, `threshold_fine`, отдельно по long/short.
5. Уровни retracement: `0.236`, `0.382`, `0.500`, `0.618`, `0.786`.
6. Уровни extension: `1.272`, `1.618`, `2.618`.
7. До реализации этого пункта блок `structure_ta` считается неполным по FIBO-логике.

## Дополнение к ТЗ: фигурный паттерн + уровень + объем 2026-06-04T00:00:00Z
Активное ТЗ обновлено: `docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`.

Отдельное приложение: `docs/CALIBRATION_NODE_CURRENT/PATTERN_STRUCTURE_VOLUME_ENTRY_TZ_APPENDIX_2026-06-04_RU.md`.

Решение:
1. Фигурный паттерн не используем как одиночный сигнал.
2. Сигнал на вход строится связкой `pattern + structure_ta + volume_flow`.
3. Техническое имя контура: `pattern_structure_volume_entry`.
4. Русское имя: `Фигурный паттерн + уровень + объем для входа`.
5. В связку входят фигуры: двойная вершина, двойное дно, голова и плечи, перевернутая голова и плечи, треугольник, вымпел, восходящий клин, нисходящий клин, диапазон.
6. Калибруемые параметры будущего контура: `pattern_window`, `min_touches`, `breakout_threshold`, `retest_window`, `level_distance_threshold`, `volume_confirm_threshold`, `vol_z_window`, `sl_buffer`, `tp_ladder`.
7. Выход: `SL` за invalidation-точку; `TP` лесенкой через ближайший уровень, measured move, FIBO extension/следующий уровень/RR target.
8. До реализации этого контура блок `pattern` считается неполным по части классических фигурных паттернов.

## Жесткий runtime-аудит current-блоков 2026-06-04T06:45:55Z
Читаемый документ: `docs/CALIBRATION_NODE_CURRENT/CURRENT_BLOCK_PARAM_RUNTIME_AUDIT_2026-06-04_RU.md`.

Машинный artifact: `reports/qa_gate/current_block_param_runtime_audit_20260604T064555Z.json`.

Статус: `PASS_SEARCH_RUNTIME_WITH_CRITICAL_ANCHOR_GAP`.

Итог:
1. `catalog_blocks/*.yaml` подтверждены как блоковый режим: берется целый блок, его `feature_rows` и union параметров блока.
2. `narrow / medium / wide` реально компилируются в разные списки значений.
3. Optuna-search реально семплирует `profile__<param>` и передает `calibration_params` в `build_feature_frame` и `run_prob_backtest`.
4. Главный разрыв: после выбора кандидата финальный `pipeline_train_eval` и `oos_evaluate` сейчас не получают выбранные `calibration_params`, поэтому train/OOS может пересчитать фичи на дефолтных формулах.
5. Найдены формульные расхождения:
   - `volume_flow`: `vol_chg`, `delta_volume`, `obv_slope_5` заявляют `return_lookback`, но формулы используют фиксированные `1/1/5`;
   - `density_profile`: `density_vpoc_drift_20` заявляет `div_lookback`, но формула использует `return_lookback * 2`;
   - `structure_ta`: `retest_flag` жестко использует `0.002`, `false_breakout_flag` не использует заявленный threshold, FIBO уровни фиксированы `0.382/0.618`;
   - `pattern`: классические фигурные паттерны и `pattern_structure_volume_entry` пока не реализованы.

Практический вывод: каркас блоковой Optuna-калибровки подключен, но перед честным боевым прогоном всех блоков нужно закрыть anchor gap и исправить перечисленные параметры, которые записаны в YAML, но не применяются как заявлено.

## Следующий практический шаг
Новая активная цепочка: последовательный перебор 69 слотов `H000-H068`.

Коррекция правила:
1. `long_only` и `short_only` — два разных стека, не смешиваются.
2. Один стек проходит `narrow -> medium -> wide`.
3. Один слот закрывается только после `long_only complete`, `short_only complete`, `slot complete`.
4. Профиль `SWEEP_PROFILE_STANDARD`: `3x3/9`, `narrow=60/300`, `medium=120/600`, `wide=180/900`.

Инвентаризация закрыта:
1. slots total: `69`;
2. feature rows: `68`;
3. calibrate true: `56`;
4. calibrate false: `13`, включая `H000` baseline/control.

Artifacts:
1. `reports/qa_gate/hypothesis_feature_sweep_inventory_20260603T121643Z.json`;
2. `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`;
3. `docs/CALIBRATION_NODE_CURRENT/TZ_HYPOTHESIS_FEATURE_SWEEP_2026-06-03_RU.md`.
4. `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`;
5. `reports/qa_gate/h001_feature_sweep_matrix_compile_20260603T121833Z.json`.

`STEP-01`: инвентаризация `H000-H068` закрыта; `H001` matrix compile `PASS`.

Первый runtime-слот: `H001`, block `price_volatility`, feature `ret_1`, params `return_lookback`.

### H001 progress
1. `long_only` stack заново пройден полностью: `narrow -> medium -> wide`, 1d->1d, `TrainDate=2026-05-31`, `TestDate=2026-06-01`.
2. `narrow long_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w1`, best OOS `-21.073250965000014%`, trades `5`, class `negative_runtime_ok`.
3. `medium long_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w2`, best OOS `-8.650246602184342%`, trades `4`, class `negative_runtime_ok`; это лучший long-результат стека.
4. `wide long_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w2`, best OOS `-30.924389997582892%`, trades `13`, class `negative_runtime_ok`.
5. Long stack artifact: `reports/qa_gate/h001_long_stack_complete_20260603T131326Z.json`.
6. Long summaries:
   - `narrow`: `reports/adaptive/long_only_pool_20260603t130651z_w1/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T130652Z.json`;
   - `medium`: `reports/adaptive/long_only_pool_20260603t130727z_w2/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T130729Z.json`;
   - `wide`: `reports/adaptive/long_only_pool_20260603t130755z_w2/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T130757Z.json`.
7. `short_only` stack заново пройден полностью: `narrow -> medium -> wide`, 1d->1d, `TrainDate=2026-05-31`, `TestDate=2026-06-01`.
8. `narrow short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w2`, best OOS `0%`, trades `0`, class `no_candidate_runtime_ok`; это лучший short-результат стека.
9. `medium short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w1`, best OOS `-5.42444158059765%`, trades `2`, class `negative_runtime_ok`.
10. `wide short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w3`, best OOS `-16.721859329376898%`, trades `7`, class `negative_runtime_ok`.
11. Short stack artifact: `reports/qa_gate/h001_short_stack_complete_20260603T131659Z.json`.
12. Slot closeout artifact: `reports/qa_gate/h001_slot_closeout_20260603T131659Z.json`.
13. Sweep table updated: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`, status `slot_complete_runtime_ok_no_candidate_next_H002`.

Примененные сетки H001 long/short:
1. Целевая ось слота `return_lookback`: min `3`, max `30`, step `3`.
2. `narrow`: `[3, 9, 15, 24, 30]`.
3. `medium`: `[3, 9, 15, 21, 27, 30]`.
4. `wide`: `[3, 6, 9, 12, 15, 18, 21, 24, 27, 30]`.
5. Контекстная ось `min_abs_ema_gap`: min `0.0`, max `0.08`; `narrow/medium=[0.0, 0.02, 0.04, 0.06, 0.08]`, `wide=[0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]`.
6. Trials profile: `narrow=60 total / 20 per process / 300 sec`, `medium=120 total / 40 per process / 600 sec`, `wide=180 total / 60 per process / 900 sec`.

Итог H001:
1. `long_only complete`: лучший `medium`, `-8.650246602184342%`, trades `4`, не candidate.
2. `short_only complete`: лучший `narrow`, `0%`, trades `0`, не candidate.
3. `slot complete`: H001 прошел все 6 запусков (`long/short` x `narrow/medium/wide`) без worker crash.
4. Вывод: перебор сетки работает штатно, кандидата нет, идем дальше по номеру.

### H002 progress
1. `H002`, block `price_volatility`, feature `ret_3`, params `return_lookback`.
2. Matrix created: `configs/calibration_matrices/feature_sweep/h002_price_volatility_ret_3.yaml`.
3. Matrix compile `PASS`: `reports/qa_gate/h002_feature_sweep_matrix_compile_20260603T153704Z.json`.
4. `long_only` stack полностью пройден: `narrow -> medium -> wide`.
5. `narrow long_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w2`, best OOS `-12.695604106001769%`, trades `3`, class `negative_runtime_ok`.
6. `medium long_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w2`, best OOS `-12.695604106001769%`, trades `3`, class `negative_runtime_ok`.
7. `wide long_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w2`, best OOS `-8.650246602184342%`, trades `4`, class `negative_runtime_ok`; это лучший long-результат стека.
8. `short_only` stack полностью пройден: `narrow -> medium -> wide`.
9. `narrow short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w3`, best OOS `-0.2662724500743341%`, trades `2`, class `negative_runtime_ok`; это лучший short-результат стека.
10. `medium short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w2`, best OOS `-0.2662724500743341%`, trades `2`, class `negative_runtime_ok`; равный лучший short.
11. `wide short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w3`, best OOS `-5.42444158059765%`, trades `2`, class `negative_runtime_ok`.
12. Long stack artifact: `reports/qa_gate/h002_long_stack_complete_20260603T154133Z.json`.
13. Short stack artifact: `reports/qa_gate/h002_short_stack_complete_20260603T154133Z.json`.
14. Slot closeout artifact: `reports/qa_gate/h002_slot_closeout_20260603T154133Z.json`.
15. Sweep table updated: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`, status `slot_complete_runtime_ok_no_candidate_next_H003`.
16. Human-readable report updated: `reports/optuna_catalog/index/hypothesis_feature_sweep_human_ru.md`.

Итог H002:
1. `long_only complete`: лучший `wide`, `-8.650246602184342%`, trades `4`, не candidate.
2. `short_only complete`: лучший `narrow`/`medium`, `-0.2662724500743341%`, trades `2`, не candidate.
3. `slot complete`: H002 прошел все 6 запусков (`long/short` x `narrow/medium/wide`) без worker crash.
4. Вывод: перебор сетки работает штатно, кандидата нет, идем дальше по номеру.

Следующий строгий номер:
1. `H003`, block `price_volatility`, feature `ret_6`, params `return_lookback`.
2. Сначала собрать/проверить matrix compile для H003.
3. Затем запустить `H003 long_only` полным стеком `narrow -> medium -> wide`.

## Запрет
Не брать следующий шаг из `docs/CHANGELOG_CHRONOLOGY_RU.md`, `docs/codex/session_log.md` или старых TZ. Только из этой папки.

## Актуально 2026-06-04T09:06:15Z
Статус текущей цепочки `Optuma bridge`: `FIXED_FOCUSED_TESTS_PASS`.

Закрыто строго по плану:
1. Step 1 `calibration_params` anchor gap: выбранные Optuna-параметры доходят до train/OOS и сохраняются в отчетах/model payload.
2. Step 2 `volume_flow`: `vol_chg`, `delta_volume`, `obv_slope_5` используют калибруемый `return_lookback`.
3. Step 3 `density_profile`: `density_vpoc_drift_20` использует калибруемый `div_lookback`.
4. Step 4 `structure_ta`: `retest_flag` и `false_breakout_flag` используют калибруемый `threshold_fine`.
5. Step 5 `structure_ta` / FIBO: добавлены `fib_window`, `fib_level`; FIBO feature/hypothesis rows подключены к этим профилям. Явные уровни `fib_level`: `0.236`, `0.382`, `0.5`, `0.618`, `0.786`.

Проверка:
1. Focused tests: `95/95 OK`.
2. `py_compile` измененных модулей: `PASS`.
3. Compile-аудит матриц: `PASS`, проверено `7` YAML-матриц x `2` направления x `3` сетки; для `structure_ta` подтверждены `fib_window` и `fib_level`.
4. `text_guard`: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T090928Z.json`.

Следующий номер по цепочке: `pattern` / `pattern_structure_volume_entry` - классические фигурные паттерны в связке `pattern + structure_ta + volume_flow`.

## Актуально 2026-06-04T09:16:54Z
Статус номера `pattern_structure_volume_entry`: `FIXED_FOCUSED_TESTS_PASS`.

Что закрыто:
1. В `src/mlbotnav/dataset.py` добавлены runtime-признаки классических фигур: `double_bottom_flag`, `double_top_flag`, `head_shoulders_flag`, `inverse_head_shoulders_flag`, `triangle_flag`, `pennant_flag`, `wedge_rising_flag`, `wedge_falling_flag`, `range_flag`.
2. Добавлена связка входа `pattern + structure_ta + volume_flow`: `pattern_volume_confirm_flag`, `pattern_level_confirm_flag`, `pattern_structure_volume_entry_long`, `pattern_structure_volume_entry_short`.
3. Добавлены вспомогательные параметры выхода/оценки: `pattern_sl_buffer_distance`, `pattern_tp_ladder_score`.
4. В `configs/features_block.yaml` новые признаки добавлены в общий список, группу `pattern` и русские подписи.
5. В `configs/calibration_full_matrix_v1.yaml` и `configs/calibration_matrices/catalog_blocks/catalog_block_*.yaml` добавлены профили `pattern_window`, `min_touches`, `breakout_threshold`, `retest_window`, `level_distance_threshold`, `volume_confirm_threshold`, `vol_z_window`, `sl_buffer`, `tp_ladder`.
6. `vol_z` теперь калибруется через отдельный `vol_z_window`, а не через общий `rolling_window`.
7. В full matrix и `catalog_block_06_pattern.yaml` добавлены feature rows для фигурных паттернов и entry-связки.

Проверка:
1. Focused tests: `97/97 OK`.
2. `py_compile` измененных модулей: `PASS`.
3. Compile-аудит матриц: `PASS`, проверено `7` YAML-матриц x `2` направления x `3` сетки; для `pattern` подтверждены `9` новых профилей и entry rows.
4. `text_guard`: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T091818Z.json`.

Итог: блок `pattern` больше не ограничен только свечными паттернами и дивергенциями; классические фигуры и связка `фигура + уровень + объем` подключены как калибруемые признаки.

Следующий номер по цепочке: сухой command/compile gate для `catalog_block_06_pattern.yaml`, затем отдельные runtime-прогоны `long_only` и `short_only` по `narrow -> medium -> wide`.

## Актуально 2026-06-04T10:20:10Z
Статус `pattern` runtime: `PAUSED_BEFORE_WIDE_CPU_PROFILE_CONFIRMATION`.

Что сделано по шагам:
1. STEP-01 dry command/compile gate для `catalog_block_06_pattern.yaml`: `PASS`.
   Artifact: `reports/qa_gate/pattern_block06_command_gate_20260604T101700Z.json`.
2. STEP-02 `pattern long_only narrow`: runtime `OK`, workers `3/3`, candidate `NO_CANDIDATE`, CPU max `57%`.
   Artifact: `reports/qa_gate/pattern_long_only_narrow_closeout_20260604T101742Z.json`.
3. STEP-02 `pattern long_only medium`: launcher runtime `OK`, workers `3/3`, best OOS `-78.782906127645376%`, trades `35`, candidate `NO_CANDIDATE`, but CPU max `97%`.
   Artifact: `reports/qa_gate/pattern_long_only_medium_closeout_20260604T102010Z.json`.

Решение по лимиту CPU:
1. Пользовательский лимит: не грузить CPU выше `85%`.
2. На `medium` был spike до `97%`.
3. Поэтому `wide` не запускаем на текущем профиле `ProcessWorkers=3 / SearchWorkers=9 / SearchWorkersPerProcess=3`, пока не подтвержден или не снижен CPU-профиль.

Следующий номер: подтвердить CPU-профиль перед `pattern long_only wide`.
Варианты:
1. продолжить `3x9`, но с hard-stop при первом замере CPU `>85%`;
2. снизить профиль до `2` process workers / `6` search workers;
3. оставить `3x9`, но увеличить паузу/контроль и принять краткий spike как допустимый.

## Уточнение CPU-правила 2026-06-04
Краткие пики CPU до `100%` допустимы, если они быстро возвращаются примерно к `80-85%`.

Перегрузкой считаем не одиночный spike, а устойчивую нагрузку выше `85%` в течение примерно `2-5` минут.

Если такая устойчивая перегрузка появляется, прогоны полностью не бросаем: фиксируем событие, сбавляем профиль нагрузки и продолжаем тот же подпункт.

Текущий рабочий профиль:
1. штатно пробуем `ProcessWorkers=3`, `SearchWorkers=9`, `SearchWorkersPerProcess=3`;
2. при sustained-перегрузе снижаем до `ProcessWorkers=2`, `SearchWorkers=6`, `SearchWorkersPerProcess=3`.

## Pattern block06 full runtime closeout 2026-06-04T10:30:51Z
Статус: `BLOCK_COMPLETE_RUNTIME_OK_NO_CANDIDATE`.

Матрица: `configs/calibration_matrices/catalog_blocks/catalog_block_06_pattern.yaml`.

CPU-правило: краткие пики допустимы; sustained `>85%` 2-5 минут означает сбавить профиль и продолжить тот же подпункт.

Что пройдено:
1. Dry command gate: `PASS`, artifact `reports/qa_gate/pattern_block06_command_gate_20260604T101700Z.json`.
2. `long_only narrow`: runtime `OK`, workers `3/3`, best `0%`, trades `0`, CPU max `57%`.
3. `long_only medium`: runtime `OK`, workers `3/3`, best `-78.782906127645376%`, trades `35`, CPU spike max `97%`, sustained-перегруза нет.
4. `long_only wide`: runtime `OK`, workers `3/3`, best `-15.442967566235543%`, trades `2`, CPU max `65%`.
5. `short_only narrow`: runtime `OK`, workers `3/3`, best `-32.687771067388226%`, trades `14`, CPU max `73%`.
6. `short_only medium`: runtime `OK`, workers `3/3`, best `-32.687771067388226%`, trades `14`, CPU spike max `100%`, sustained-перегруза нет.
7. `short_only wide`: runtime `OK`, workers `3/3`, best `-32.687771067388226%`, trades `14`, CPU spike max `100%`, sustained-перегруза нет.

Итог блока:
1. Лучший результат блока: `long_only narrow`, `0%`, trades `0`.
2. Кандидата нет: `NO_CANDIDATE`.
3. Worker crash нет.
4. Sustained CPU overload нет.

Artifacts:
1. Long stack: `reports/qa_gate/pattern_long_only_stack_complete_20260604T102645Z.json`.
2. Short stack: `reports/qa_gate/pattern_short_only_stack_complete_20260604T103051Z.json`.
3. Block closeout: `reports/qa_gate/pattern_block06_full_closeout_20260604T103051Z.json`.

## Human report pattern block06 2026-06-04T10:30:51Z
Readable report: `reports/qa_gate/pattern_block06_human_readable_20260604T103051Z_RU.md`.

Короткий вывод:
1. Прогон `pattern` прошел `long_only` и `short_only`, каждый через `narrow/medium/wide`.
2. Worker crash нет; sustained CPU overload нет.
3. Кандидата нет: `NO_CANDIDATE`.
4. Формально лучший результат: `long_only narrow`, `0%`, trades `0`, но это не торговый кандидат.
5. Лучший торговый long: `wide`, `-15.4430%`, trades `2`.
6. Лучший торговый short: `narrow/medium/wide`, `-32.6878%`, trades `14`.
7. Важное замечание: search-level candidates содержат `calibration_params`, но final `best_oos` fallback-кандидатов сохранил `selected_calibration_params={}`. Следующий ремонтный шаг: проверить и исправить перенос `calibration_params` для fallback/no-pass candidate selection, затем повторить block06 replay.

## Fix fallback calibration params 2026-06-04T10:43:12Z
Статус: `FIXED_FOCUSED_TESTS_PASS`.

Artifact: `reports/qa_gate/pattern_fallback_calibration_params_fix_20260604T104312Z_RU.md`.

Что починено:
1. В `src/mlbotnav/adaptive_auto_train.py` добавлен выбор candidate-pool через `_candidate_pool_from_search_report`.
2. Если search report содержит `top_candidates` с `calibration_params`, adaptive-loop теперь берет полный список, а не облегченный `all_candidates_lite`.
3. Это сохраняет параметры для fallback/no-pass candidate selection и последующего train/OOS replay.
4. Добавлен тест `tests/test_adaptive_candidate_pick.py::test_candidate_pool_prefers_full_candidates_with_calibration_params`.

Проверка:
1. `py_compile`: `PASS`.
2. Focused tests: `80/80 OK`.
3. Проверка на старых search artifacts подтвердила, что long/short fallback теперь выбирает кандидатов с `18` calibration params.

Осталось: старые block06 runtime artifacts не переписаны. Следующий практический шаг - повторить affected `pattern` block06 replay/runtime, чтобы новый final `best_oos` физически содержал `selected_calibration_params`.

## Pattern block06 replay after params/retry fix 2026-06-04T11:00:12Z
Статус: `BLOCK_COMPLETE_RUNTIME_OK_NO_CANDIDATE`.

Активный readable artifact: `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z_RU.md`.

Машинный artifact: `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z.json`.

Что исправлено перед повтором:
1. `src/mlbotnav/adaptive_auto_train.py`: final replay теперь берет full `top_candidates` с `calibration_params`, а не lite-кандидатов без параметров.
2. `_sig()` теперь учитывает `calibration_params`, поэтому разные наборы параметров одного блока не схлопываются в одну подпись.
3. `candidate_replay_attempts` поднят до `8`: если текущий набор параметров ломает train по технической причине, adaptive-loop берет следующий кандидат из того же search-отчета.

Повтор блока `pattern` / H006:
1. `long_only narrow`: launcher `OK`, workers `3/3`, best OOS `-27.1741%`, trades `5`, params `18`.
2. `long_only medium`: launcher `OK`, workers `3/3`, best OOS `0.0000%`, trades `0`, params `18`.
3. `long_only wide`: launcher `OK`, workers `3/3`, best OOS `-43.3400%`, trades `14`, params `18`.
4. `short_only narrow`: launcher `OK`, workers `3/3`, best OOS `-16.5304%`, trades `7`, params `18`.
5. `short_only medium`: launcher `OK`, workers `3/3`, best OOS `-15.6997%`, trades `6`, params `18`.
6. `short_only wide`: launcher `OK`, workers `3/3`, best OOS `-28.0623%`, trades `11`, params `18`.

Итог:
1. Сетки `narrow/medium/wide` прошли отдельно для LONG и SHORT.
2. Worker crash нет.
3. Финальные `best_oos` содержат `selected_calibration_params` по `18` параметров.
4. Плюсового кандидата нет: `NO_CANDIDATE`.
5. Лучший торговый результат блока: `short_only medium`, `-15.6997%`, trades `6`.

Следующий номер по цепочке: переход к следующему блоку/слоту после фиксации статуса и health-check.

Health-check после фиксации:
1. `text_guard`: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T110352Z.json`.

## H006 grid/min-max runtime audit 2026-06-04T11:05:00Z
Artifact: `reports/qa_gate/pattern_h006_grid_runtime_audit_20260604T110500Z_RU.md`.

Короткий вывод:
1. Доказано по search-report: `long_only` и `short_only` запускались отдельно.
2. Доказано по search-report: сетки `narrow`, `medium`, `wide` запускались.
3. Доказано по search-report: `force_profile_edge_coverage=true` во всех проверенных запусках.
4. Доказано по final best: `selected_calibration_params` присутствуют, `18` параметров.
5. Не доказано текущими логами полностью: `trial_history.csv` не содержит pruned edge trials, поэтому по CSV нельзя глазами подтвердить min/max для каждого параметра во всех сетках.
6. Не закрыто как отдельный контур: каскадное улучшение кандидата `wide -> medium -> narrow around best`. Сейчас сетки запускаются отдельно и сравниваются результатом.

Следующий ремонтный пункт перед утверждением "полный min/max доказан": добавить в Optuna report явный `grid_edge_coverage_audit` по всем trials, включая pruned, и добавить/описать каскадный режим улучшения кандидата.

## H006 grid_edge_coverage_audit fix 2026-06-04T11:15:52Z
Статус: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.

Readable artifact: `reports/qa_gate/h006_grid_edge_coverage_audit_fix_20260604T111552Z_RU.md`.

Что сделано:
1. `src/mlbotnav/optuna_search_candidate.py`: `calibration_params` теперь сохраняются сразу после sampling, до возможного prune.
2. Добавлен `calibration_forced_edges` для forced min/max trials.
3. Добавлен `grid_edge_coverage_audit` в основной search-report.
4. Добавлен отдельный artifact `grid_edge_coverage_audit_*.json` в `reports/optuna/<mode>/`.
5. Audit строится по всем trials текущего `run_signature`, включая `COMPLETE`, `PRUNED`, `FAIL`.

Runtime-smoke:
1. Команда: H006 `pattern`, `long_only`, `narrow`, `ProcessWorkers=2`, `SearchWorkers=6`, `OptunaTrials=24`.
2. Launcher status: `OK`, workers `2/2`.
3. Новый search-report: `reports/pipeline/optuna_search_candidate_SOLUSDT_1m_20260604T111552Z.json`.
4. Новый edge-audit artifact: `reports/optuna/long_only/grid_edge_coverage_audit_20260604T111552Z.json`.
5. Audit увидел `total=12`, `completed=8`, `pruned=4`, `failed=0`.

Проверка:
1. `py_compile`: `PASS`.
2. Focused tests: `94/94 OK`.
3. `text_guard`: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T111802Z.json`.

Осталось по этой теме:
1. Повторить нужный блок на полном budget с новым audit, чтобы min/max был доказан уже по боевому replay.
2. Отдельным следующим номером внедрить/описать каскад улучшения кандидата `wide -> medium around best -> narrow around best`, LONG и SHORT отдельно.

## H006 core grid edge forcing fix 2026-06-04T11:31:02Z
Статус: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.

Readable artifact: `reports/qa_gate/h006_core_grid_edge_forcing_fix_20260604T113102Z_RU.md`.

Что сделано:
1. Добавлен forced min/max для core-параметров Optuna search.
2. Core-параметры: `horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`.
3. Первые `5` trials закрывают min по core-параметрам.
4. Следующие `5` trials закрывают max по core-параметрам.
5. В trial attrs пишутся `core_params`, `core_params_suggested`, `core_forced_edges`.
6. `grid_edge_coverage_audit` теперь показывает forced min/max и pass/fail по core-параметрам.

Runtime-smoke:
1. H006 `pattern`, `long_only`, `narrow`, `ProcessWorkers=2`, `SearchWorkers=6`, `OptunaTrials=24`.
2. Launcher status: `OK`, workers `2/2`.
3. Search-report: `reports/pipeline/optuna_search_candidate_SOLUSDT_1m_20260604T113102Z.json`.
4. Edge-audit: `reports/optuna/long_only/grid_edge_coverage_audit_20260604T113102Z.json`.
5. Core coverage: `pass=5`, `fail=0`.
6. Profile coverage на smoke: `pass=14`, `fail=9`; это ожидаемо для малого budget и не является ошибкой runtime.

Проверка:
1. `py_compile`: `PASS`.
2. Focused tests: `94/94 OK`.
3. `text_guard`: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T113308Z.json`.

Следующий номер:
1. Повторить полный replay выбранного блока с новым edge-audit, чтобы доказать profile min/max на полном budget.
2. Потом внедрить каскад улучшения кандидата `wide -> medium around best -> narrow around best`, LONG и SHORT отдельно.

## H006 full replay after distributed edge coverage 2026-06-04T12:39:58Z
Статус: `BLOCK_COMPLETE_RUNTIME_OK_EDGE_COVERAGE_PASS_NO_CANDIDATE`.

Readable artifact: `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z_RU.md`.

Machine artifact: `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z.json`.

Что было дополнительно исправлено перед финальным replay:
1. Core-параметры исключены из profile-аудита и проверяются отдельно.
2. При `ForceProfileEdgeCoverage=on` profile sampling берет весь linked profile set блока.
3. Profile edge coverage распределяется между `w1/w2/w3`, чтобы `narrow` тоже мог доказать min/max при `20` trials на worker.

Финальный replay:
1. `long_only narrow`: launcher `OK`, best `-0.6074%`, trades `1`, profile `18/18`, core `5/5`.
2. `long_only medium`: launcher `OK`, best `-34.5854%`, trades `12`, profile `18/18`, core `5/5`.
3. `long_only wide`: launcher `OK`, best `-18.1543%`, trades `5`, profile `18/18`, core `5/5`.
4. `short_only narrow`: launcher `OK`, best `-37.8151%`, trades `21`, profile `18/18`, core `5/5`.
5. `short_only medium`: launcher `OK`, best `0.0000%`, trades `0`, profile `18/18`, core `5/5`.
6. `short_only wide`: launcher `OK`, best `-20.3243%`, trades `10`, profile `18/18`, core `5/5`.

Итог:
1. LONG и SHORT прошли отдельно.
2. Все сетки `narrow/medium/wide` прошли.
3. Min/max доказан по логам: profile `18/18`, core `5/5` во всех сетках.
4. Worker crash нет.
5. Плюсового торгового кандидата нет.
6. H006 закрыт как проверенный блок калибровочного каркаса, но без production-кандидата.

Проверка:
1. `py_compile`: `PASS`.
2. Focused tests: `95/95 OK`.
3. `text_guard`: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T124257Z.json`.

Следующий номер: каскад улучшения кандидата `wide -> medium around best -> narrow around best`, LONG и SHORT отдельно.

## CASCADE_BLOCK_CALIBRATION rule fixed 2026-06-04T14:17:45Z

Статус: `RULE_FIXED_NO_CODE_CHANGES`.

Фиксируем новый рабочий режим калибровочного узла: `CASCADE_BLOCK_CALIBRATION`.

Правило:
1. Один блок = один каскад.
2. `LONG` и `SHORT` калибруются отдельно.
3. `wide` всегда первый.
4. `medium` запускается вокруг лучшего `tradeful` кандидата из `wide`.
5. `narrow` запускается вокруг лучшего `tradeful` кандидата из `medium`.
6. Если на `wide` нет `tradeful` кандидата, `medium/narrow` не сужаются вслепую: фиксируем `NO_TRADEFUL_CANDIDATE` и переходим к следующему блоку.
7. Если `tradeful` кандидат есть, но он минусовой, каскад продолжается, чтобы понять лучший возможный результат блока.
8. Если появляется плюсовой кандидат, он сохраняется в `positive/top candidates` как тестовый кандидат, без production-перевода.

Что это меняет по смыслу:
1. Старый режим `narrow/medium/wide отдельно и потом сравнить` больше не является целевым боевым режимом.
2. Целевой режим: `wide -> best tradeful -> medium around best -> best tradeful -> narrow around best -> final OOS`.
3. Все это выполняется блоками, а не всем списком 68-69 фичей сразу.

Код не менялся. Запусков не было. Это фиксация правила в активных документах.

## C001 Block 01 cascade start plan 2026-06-04T14:41:47Z

Статус: `PLAN_FIXED_BEFORE_RUNTIME`.

Первый блок для нового режима:
1. Номер: `C001`.
2. Блок: `price_volatility`.
3. Русское название: `Цена и волатильность`.
4. Матрица: `configs/calibration_matrices/catalog_blocks/catalog_block_01_price_volatility.yaml`.

Что входит в калибровку блока:
1. `ret_1`, `ret_3`, `ret_6`, `ret_12`, `ret_24` - доходность/изменение цены за окно.
2. `rolling_std_20` - скользящая волатильность.
3. `atr14` - ATR/средний истинный диапазон.
4. `hl_spread` - derived formula, отдельно не калибруется.

Профили блока:
1. `return_lookback`: min `3`, max `30`, step `3`.
2. `rolling_window`: min `20`, max `180`, step `20`.
3. `period_standard`: min `7`, max `35`, step `2`.

Core-параметры поиска:
1. `horizon_bars`.
2. `p_enter_long`.
3. `p_enter_short`.
4. `min_expected_move`.
5. `notional_usd`.

Порядок по `CASCADE_BLOCK_CALIBRATION`:
1. Запустить `C001 LONG wide`.
2. Проверить launcher/workers/logs/edge coverage/profile/core.
3. Если есть `tradeful` кандидат, выбрать лучший и только потом строить `medium around best`.
4. Если `tradeful` кандидата нет, зафиксировать `NO_TRADEFUL_CANDIDATE_LONG` и перейти к `C001 SHORT wide`.
5. `medium/narrow` не запускать вслепую.

## C001 Block 01 LONG wide runtime 2026-06-04T14:44:29Z

Статус: `RUNTIME_OK_TRADEFUL_NEGATIVE`.

Readable artifact:
`reports/qa_gate/c001_block01_price_volatility_long_wide_20260604T144429Z_RU.md`.

Блок:
`price_volatility` / `Цена и волатильность`.

Матрица:
`configs/calibration_matrices/catalog_blocks/catalog_block_01_price_volatility.yaml`.

Запуск:
1. Mode: `long_only`.
2. Grid: `wide`.
3. `ProcessWorkers=3`.
4. `SearchWorkers=9`.
5. `SearchWorkersPerProcess=3`.
6. `OptunaTrials=180`.
7. Train `2026-05-31`, OOS `2026-06-01`.

Результат:
1. Launcher `OK`.
2. Workers `3/3`, exit code `0`.
3. Best OOS `-37.0372%`.
4. Trades `9`.
5. Кандидат `tradeful`, но минусовой.
6. Production `NO_GO`.

Лучшие параметры `wide`:
1. `min_abs_ema_gap=0.05`.
2. `period_standard=19`.
3. `return_lookback=18`.
4. `rolling_window=40`.
5. `vol_z_window=180`.

Coverage:
1. Core coverage `5/5` в проверенных edge-аудитах.
2. Profile coverage: `5/5` в `20260604T144246Z`, `2/5` в `20260604T144248Z`.

Замечание:
`w1` и `w2` ссылаются на один search-report `20260604T144246Z` с `contour_id=w2`. Это похоже на timestamp collision/артефактную коллизию имени отчета, не на worker crash.

Следующий допустимый шаг по `CASCADE_BLOCK_CALIBRATION`:
`C001 LONG medium around best`, вокруг лучшего `wide` tradeful-кандидата. Blind `medium` не запускать.

Health-check:
`text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T144630Z.json`.

## Instrument knobs audit TZ 2026-06-11T10:47:35Z

Статус: `ACTIVE_READ_ONLY_AUDIT`.

Новый активный документ:
`docs/CALIBRATION_NODE_CURRENT/TZ_INSTRUMENT_KNOBS_AUDIT_2026-06-11_RU.md`.

Решение:
1. Приостанавливаем дальнейшие runtime-запуски и `C001 medium`.
2. Сначала делаем полный аудит калибруемых ручек всех инструментов.
3. Двигаемся строго по блокам: `price_volatility -> trend_momentum -> volume_flow -> density_profile -> structure_ta -> pattern`.
4. Для каждого блока пишем отдельное короткое ТЗ блока, разбираем инструменты, фиксируем что калибруется и чего не хватает.
5. Только после фиксации всех блоков возвращаемся к изменению конфигов и каскадным прогонам.

Следующий номер:
`Block 01 price_volatility instrument knobs audit`.

## Block 01 instrument knobs audit 2026-06-11T10:51:00Z

Статус: `BLOCK_01_AUDIT_DRAFT`.

Документ блока:
`docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.

Блок:
`price_volatility` / `Цена и волатильность`.

Что зафиксировано:
1. В блок входят `ret_1`, `ret_3`, `ret_6`, `ret_12`, `ret_24`, `hl_spread`, `rolling_std_20`, `atr14`.
2. Текущие расчетные ручки: `return_lookback`, `rolling_window`, `period_standard`.
3. `hl_spread` сейчас является derived formula и отдельно не калибруется.
4. Главный пробел блока: есть расчетные окна, но нет явных signal-level ручек для силы движения, режима волатильности, диапазона свечи и ATR-риск режима.

Следующее решение по Block 01:
согласовать, какие signal-level ручки добавляем перед переходом к `Block 02 trend_momentum`.

Health-check:
`text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T105438Z.json`.

## Block 01 live chart example 2026-06-11T11:02:00Z

Статус: `VISUAL_AUDIT_EXAMPLE`.

Артефакты:
1. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.png`
2. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z_RU.md`
3. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.json`

Что показано:
на реальных SOLUSDT 1m данных показано, как Block 01 выглядит на графике: свечи, `ret_1`, `rolling_std_20`, `atr14`, `hl_spread` и пример действия `LONG_ALLOWED / SHORT_ALLOWED / NO_TRADE_LOW_VOL / NO_TRADE_HIGH_RISK`.

Граница:
это визуальный пример для согласования signal-level ручек, не runtime-калибровка и не production-правило.

Health-check:
`text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T113003Z.json`.

## Block 01 SHORT rework visual 2026-06-11T11:34:00Z

Статус: `SHORT_REWORK_VISUAL_AUDIT`.

Артефакты:
1. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.png`
2. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z_RU.md`
3. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.json`

Вывод:
локальный рост `ret_1 > 0` внутри нисходящего фона не должен автоматически становиться LONG. Для Block 01 нужен отдельный SHORT-сценарий: `SHORT_AFTER_PULLBACK`.

Что предлагается крутить:
`ret_down_context_threshold`, `ret_pullback_up_threshold`, `ret_short_confirm_threshold`, `confirm_bars`, `vol_min/max`, `atr_min/max`, `hl_spread_max`.

Граница:
это визуальное ТЗ и логика на согласование. Конфиги и код пока не менялись, Optuna/APTuna runtime не запускался.

## Block 01 parameter range map 2026-06-11T11:48:00Z

Статус: `PARAMETER_RANGE_MAP_DRAFT`.

Где зафиксировано:
`docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.

Что добавлено:
1. Расчетные окна: `return_lookback`, `rolling_window`, `period_standard`.
2. Фон вверх/вниз: `ret_context_source`, `ret_down_context_threshold`, `ret_up_context_threshold`.
3. Откат: `ret_pullback_up_threshold`, `ret_pullback_down_threshold`, `pullback_min_bars`, `pullback_max_bars`.
4. Подтверждение: `ret_short_confirm_threshold`, `ret_long_confirm_threshold`, `confirm_bars`.
5. Активность рынка: `vol_min/max`, `atr_min/max`, `hl_spread_min/max`.
6. Первичная цель/риск: `target_bars`, `target_move_threshold`, `atr_tp_multiplier`, `atr_sl_multiplier`.

Граница:
это пока карта диапазонов для согласования. Конфиги и код не менялись, Optuna/APTuna runtime не запускался.

## New chat handoff 2026-06-19

Статус: `NEW_CHAT_HANDOFF_READY`.

Документ:
`docs/CALIBRATION_NODE_CURRENT/HANDOFF_TO_NEW_CHAT_2026-06-19_RU.md`.

Смысл:
старый чат слишком большой; для продолжения подготовлен короткий пакет переезда с актуальным источником истины, статусом Block 01, картой ручек, визуальными артефактами и стартовым сообщением для нового чата.

Следующий шаг:
в новом чате восстановить статус по handoff и решить, переводим ли `Block 01 price_volatility` из `PARAMETER_RANGE_MAP_DRAFT` в `AGREED/READY_FOR_CODE`, либо еще уточняем Block 01 перед `Block 02 trend_momentum`.

Health-check:
`text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260619T184109Z.json`.

## Passport audit TZ 2026-06-20

Статус: `ACTIVE_PASSPORT_AUDIT_TZ`.

Документ:
`docs/CALIBRATION_NODE_CURRENT/TZ_PASSPORT_AUDIT_2026-06-20_RU.md`.

Смысл:
переходим от общего обсуждения ручек к строгому паспортному аудиту. Сначала фиксируем очередь паспортов, затем идем по ней без прыжков.

Инвентарная база:
1. `feature_rows`: `83`.
2. `hypothesis_rows`: `20`.
3. `parameter_profiles`: `38`.
4. `search_grid_rows`: `5`.
5. Блоков фич: `6`.

Правило:
не запускать Optuna/APTuna runtime, `C001 medium`, forward, production, не править код и конфиги до завершения паспортного аудита и отдельного согласования.

Следующий шаг:
начать паспорт `F001 ret_1`. Пока `F001 ret_1` не закрыт, к `F002 ret_3`, RSI, гипотезам или parameter profiles не переходить.

Уточнение шаблона:
поле `BOTH-смысл` убрано как обязательное. В паспортах используем `LONG-логика`, `SHORT-логика`, `Общие фильтры / запреты`, `Action labels`.

## F001 ret_1 passport 2026-06-20

Статус: `DRAFT`.

Документ:
`docs/CALIBRATION_NODE_CURRENT/passports/features/F001_ret_1_RU.md`.

Факт:
начат первый паспорт строго по очереди `feature_rows`. `ret_1` зафиксирован как фича движения цены из блока `price_volatility`.

Текущая формула:
`ret_1 = close.pct_change(return_lookback)`.

Важное уточнение:
`ret_1` в текущей реализации означает `1 x return_lookback`, а не обязательно ровно один бар.

Уточнение 2026-06-20:
паспорт переведен в формат калибровочной поверхности: отдельно фиксируются калибруемые линии/зоны/операторы (`ret_1_long_threshold`, `ret_1_short_threshold`, `ret_1_dead_zone_abs`, `ret_1_extreme_abs`, `ret_1_cross_operator`, `ret_1_return_to_zone_mode`) и отдельно то, что не калибруется (`ret_1_zero_line`, action labels).

Следующий шаг:
согласовать паспорт `F001 ret_1`. До согласования не переходить к `F002 ret_3`.

## F001 strict passport runtime подключение 2026-06-22

Статус: `F001_STRICT_PASSPORT_CONNECTED`.

Документ:
`docs/CALIBRATION_NODE_CURRENT/passports/features/F001_ret_1_RU.md`.

Что подключено:
1. `F001_move`: значения `-1 / 1`.
2. `F001_thr_pct`: диапазон `0.01..0.50`, шаг `0.01`.
3. Runtime action `F001_RET1_ALLOW`: `1/0`.

Код:
1. `src/mlbotnav/dataset.py` считает `F001_RET1_ALLOW` по последней закрытой 1m свече.
2. `src/mlbotnav/validation.py` и `src/mlbotnav/optuna_search_candidate.py` сохраняют action-колонку в OOF.
3. `src/mlbotnav/backtest.py` применяет action-колонку как entry-gate.

Матрицы:
1. `configs/calibration_full_matrix_v1.yaml`.
2. `configs/calibration_matrices/catalog_blocks/catalog_block_01_price_volatility.yaml`.
3. `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`.

Решение:
`ret_1` / `F001` больше не калибрует `return_lookback`. Для F001 калибруются только `F001_move` и `F001_thr_pct`. `return_lookback` остается для других строк, где он реально используется.

Проверка:
1. `py_compile PASS`.
2. `tests.test_dataset_inference_mode`, `tests.test_backtest_fields`, `tests.test_optuna_space_constraints`, `tests.test_structure_pattern_parity`: `25 tests OK`.
3. `tests.test_optuna_search_runtime`: `65 tests OK`.
4. Матрицы compile `PASS`: во всех трех `ret_1_params = [F001_move, F001_thr_pct]`, `F001_thr_pct` имеет `50` значений.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260622T091458Z.json`.

Следующий шаг:
после подтверждения пользователя можно запускать F001/H001 или Block 01 по новой паспортной связке, либо переходить к паспорту `F002 ret_3` строго по списку.

## F001 strict LONG 1d/1d runtime 2026-06-22

Статус: `F001_LONG_1D1D_DONE_GOAL_FAIL`.

Отчет:
`reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`.

Исправление перед финальным результатом:
первый прогон показал, что финальный OOS evaluator не сохранял runtime-action колонку `F001_RET1_ALLOW`, поэтому `F001_RET1_ALLOW_gate_active=false`. Исправлено в `src/mlbotnav/oos_evaluate.py`: OOS теперь сохраняет `RUNTIME_ACTION_COLUMNS` перед backtest.

Проверка фикса:
`py_compile PASS`; `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_dataset_inference_mode`, `tests.test_backtest_fields`, `tests.test_optuna_search_runtime`: `84 tests OK`.

Честный прогон:
1. Режим: `long_only`.
2. Train/calibration day: `2026-05-31`.
3. OOS/test day: `2026-06-01`.
4. Matrix: `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`.
5. Launcher: `OK`, workers `3/3`, all `exit_code=0`.

Лучший worker:
`w1`.

Selected params:
`F001_move=1.0`, `F001_thr_pct=0.19`, `min_abs_ema_gap=0.02`.

OOS:
1. `net_return_pct=-5.352332468117016`.
2. `trades=3`.
3. `hit_rate=0.3333333333333333`.
4. `max_drawdown_pct=-5.833320604926396`.
5. `goal_pass=false`.
6. `train_gate_pass=false`.

Gate diagnostics:
1. `F001_RET1_ALLOW_gate_active=true`.
2. `signal_count_raw=525`.
3. `signal_count_after_mode=281`.
4. `signal_count_after_f001_ret1_gate=4`.
5. `entries_filled=3`.

Итог:
паспорт F001 в LONG работает и реально режет входы, но на окне `2026-05-31 -> 2026-06-01` результата нет: `NO_GO / goal_fail`.

## F001 strict LONG trade map 2026-06-22

Статус: `F001_LONG_TRADE_MAP_READY`.

График:
`reports/qa_gate/f001_strict_long_1d1d_trade_map_20260622T092020Z.png`.

Источник:
`reports/final_review/oos_report_SOLUSDT_1m_2026-06-01_long_only_20260622T092019Z.json`.

Что показано:
1. Весь OOS-день `2026-06-01`.
2. Три LONG-входа лучшего worker `w1`.
3. Сигнальная свеча F001.
4. Цена входа.
5. Цена выхода.
6. TP-линия `+1.20%`.
7. SL-линия `-0.80%`.

Факт по сделкам:
все 3 сделки закрылись по `timeout`; `target_reached=false`; TP не достигался, SL не срабатывал.

## F001 strict LONG no-timeout runtime 2026-06-22

Статус: `F001_LONG_NO_TIMEOUT_DONE_NO_GO`.

Отчет:
`reports/qa_gate/f001_strict_long_no_timeout_1d1d_20260622T093702Z_RU.md`.

График:
`reports/qa_gate/f001_strict_long_no_timeout_trade_map_20260622T093702Z.png`.

Изменение:
добавлен явный режим отключения временного выхода из сделки:
`-DisableTimeoutExit` в `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` и `--disable-timeout-exit` в Python-командах.

Смысл:
если режим выключает timeout, сделка больше не закрывается по `hold_bars`; она закрывается по TP/SL или в конце OOS-данных как `end_of_data`.

Проверка кода:
`py_compile PASS`; `tests.test_backtest_fields`, `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_optuna_search_runtime`: `78 tests OK`.

Health-check:
`text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T094448Z.json`.

Прогон:
1. Режим: `long_only`.
2. Train/calibration day: `2026-05-31`.
3. OOS/test day: `2026-06-01`.
4. Matrix: `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`.
5. Launcher: `OK`, workers `3/3`, `TimeoutExit=off`.

Формально лучший worker:
`w1`, params `F001_move=1.0`, `F001_thr_pct=0.09`, `min_abs_ema_gap=0.07`; OOS `net_return_pct=0.0`, `trades=0`, `goal_pass=false`.

Лучший tradeful worker:
`w2/w3`, params `F001_move=1.0`, `F001_thr_pct=0.05`, `min_abs_ema_gap=0.08`; OOS `net_return_pct=-47.79331627195255`, `trades=6`, `hit_rate=0.0`, `max_drawdown_pct=-47.79331627195255`, `goal_pass=false`.

Факт по сделкам tradeful worker:
5 сделок закрылись по `sl`; 1 сделка закрылась как `end_of_data`; TP не достигался.

Итог:
таймаут выключен технически корректно, но для F001 LONG на окне `2026-05-31 -> 2026-06-01` это не дает результата. Без timeout сделки дольше сидят в позиции и в основном доходят до SL. Статус F001 LONG остается `NO_GO`.

## F001 exit baseline decision 2026-06-22

Статус: `EXIT_BASELINE_TIMEOUT_ON`.

Решение пользователя:
для чистоты текущей калибровки оставить выходы как было:
1. `TP`.
2. `SL`.
3. `timeout` по `hold_bars`.

Текущий baseline:
использовать обычный запуск без `-DisableTimeoutExit`.

Граница:
режим `-DisableTimeoutExit` остается технически доступным как экспериментальный переключатель, но не является baseline для F001/Block 01 разборов. No-timeout прогон считать диагностикой, а не основной точкой сравнения.

Активный результат для сравнения F001 LONG:
`reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md` с timeout: `net_return_pct=-5.352332468117016`, `trades=3`, все 3 выхода по `timeout`.

## ACTION_PASSPORT_CALIBRATION 2026-06-22

Статус: `ACTIVE_RULE_CONNECTED`.

Новый TZ:
`docs/CALIBRATION_NODE_CURRENT/TZ_ACTION_PASSPORT_CALIBRATION_2026-06-22_RU.md`.

Новый реестр:
`configs/calibration_action_passports.yaml`.

Новая активная F001 matrix:
`configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`.

Решение:
старые Optuna-матрицы и старые калибруемые предложения больше не являются чистым baseline. Они остаются `legacy/frozen` как исторический артефакт и материал для миграции. Новая калибровка должна идти только через паспорт действия.

Новое правило:
1. Каждое действие должно иметь паспорт.
2. Каждое действие должно иметь список разрешенных calibration params.
3. Backtest должен использовать только output, который описан в паспорте действия.
4. Выходы из сделки не смешиваются с F001; для exit/dynamic exit нужен отдельный паспорт.
5. Baseline выхода сейчас остается `TP / SL / timeout`.

Технический фикс:
в `src/mlbotnav/optuna_space.py` добавлен `passport_mode`. Если матрица включает `passport_mode.enabled=true`, то любой параметр вне `allowed_calibration_params` вызывает ошибку compile и не доходит до Optuna.

F001 allowlist:
1. `F001_move`.
2. `F001_thr_pct`.

F001 legacy запрет:
`return_lookback`, `min_abs_ema_gap`, `trend_filter`, `stop_loss`, `take_profit`, `timeout`, `order_size` не являются ручками F001.

Проверка:
1. `py_compile PASS`: `src/mlbotnav/optuna_space.py`.
2. `tests.test_optuna_space_constraints`: `13 tests OK`.
3. `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`.
4. YAML parse `PASS`: `configs/calibration_action_passports.yaml`, `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`.
5. Passport matrix compile `PASS` для `long_only` и `short_only`: profiles только `F001_move`, `F001_thr_pct`.
6. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260622T101720Z.json`.

## F001 passport-action LONG runtime 2026-06-22

Статус: `F001_PASSPORT_ACTION_LONG_DONE_NO_GO`.

Отчет:
`reports/qa_gate/f001_passport_action_long_1d1d_20260622T101953Z_RU.md`.

Матрица:
`configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`.

Compile-check:
`PASS`; `long_only` и `short_only` имеют только profiles `F001_move`, `F001_thr_pct`; `passport_mode.enabled=true`.

Прогон:
1. Mode: `long_only`.
2. Train: `2026-05-31`.
3. OOS: `2026-06-01`.
4. Grid: `wide`.
5. Trials: `180`.
6. TimeoutExit: `on`.
7. Launcher: `OK`, workers `3/3`.

Workers:
1. `w1`: `F001_thr_pct=0.28`, OOS `-5.1298471326372%`, `1` trade.
2. `w2`: `F001_thr_pct=0.10`, OOS `-28.876033596834784%`, `8` trades.
3. `w3`: `F001_thr_pct=0.29`, OOS `0.0%`, `0` trades.

Формально лучший:
`w3`, `0 сделок / 0%`; не считать tradeful-кандидатом.

Лучший tradeful:
`w1`, `-5.1298471326372%`, `1` сделка, exit=`timeout`.

Gate:
`F001_RET1_ALLOW_gate_active=true`.

Итог:
новая паспортная F001-матрица работает технически корректно и не пропускает legacy feature/hypothesis ручки в F001 profiles. Торгового результата по LONG на этом окне нет: `NO_GO`.

Замечание:
core runtime поля (`horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`) пока еще подбираются engine default grid. Для полной чистоты их нужно вынести в отдельный runtime/backtest subpassport или зафиксировать single-value grids.

Проверка после прогона:
`py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T102340Z.json`.

## Единый block-passport registry 2026-06-22

Статус: `BLOCK_PASSPORT_REGISTRY_CONNECTED`.

Решение:
используем один главный конфиг:
`configs/calibration_action_passports.yaml`.

Структура:
1. `blocks.B001` = `price_volatility` / `Цена и волатильность`.
2. `blocks.B002` = `trend_momentum` / `Тренд и импульс`.
3. `blocks.B003` = `volume_flow` / `Объем и поток`.
4. `blocks.B004` = `density_profile` / `Плотность и профиль`.
5. `blocks.B005` = `structure_ta` / `Структура и уровни`.
6. `blocks.B006` = `pattern` / `Паттерны`.

F001 теперь находится внутри:
`blocks.B001.active_passports.F001`.

F002 находится как planned:
`blocks.B001.planned_passports.F002`.

Технический фикс:
`passport_mode` в matrix теперь сверяется с registry по:
1. `registry_path`.
2. `registry_block_id`.
3. `registry_passport_id`.
4. `action_id`.
5. `allowed_calibration_params`.
6. `active_matrix_path`.

F001 matrix:
`configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml` теперь указывает:
`registry_block_id=B001`, `registry_passport_id=F001`, `action_id=F001_RET1_ALLOW`.

Проверка:
1. `py_compile PASS`: `src/mlbotnav/optuna_space.py`.
2. `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `79 tests OK`.
3. Env override compile `PASS`: F001 matrix через `MLBOTNAV_CALIBRATION_MATRIX_PATH` компилируется с profiles `F001_move`, `F001_thr_pct` и registry metadata.

## RET_N strict passports F001-F005 2026-06-22

Статус: `RET_N_F001_F005_PASSPORTS_CONNECTED`.

Входной файл пользователя:
`C:\Users\007\Downloads\RET_N_F001_F005_strict_passports.md`.

Проектный паспорт:
`docs/CALIBRATION_NODE_CURRENT/passports/features/RET_N_F001_F005_strict_passports.md`.

Решение:
семейство `ret_N_1m` подключено как набор отдельных `ENTRY_FILTER` действий в `blocks.B001.active_passports`: `F001`, `F002`, `F003`, `F004`, `F005`.

Активные матрицы:
1. `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`.
2. `configs/calibration_matrices/passport_actions/F002_ret3_entry_filter.yaml`.
3. `configs/calibration_matrices/passport_actions/F003_ret6_entry_filter.yaml`.
4. `configs/calibration_matrices/passport_actions/F004_ret12_entry_filter.yaml`.
5. `configs/calibration_matrices/passport_actions/F005_ret24_entry_filter.yaml`.

Runtime:
`src/mlbotnav/dataset.py` считает `F002_RET3_ALLOW`, `F003_RET6_ALLOW`, `F004_RET12_ALLOW`, `F005_RET24_ALLOW` только когда в `calibration_params` присутствуют их паспортные ручки. Это не дает новым действиям молча фильтровать старые прогоны.

Backtest:
`src/mlbotnav/backtest.py` теперь применяет общий список `ENTRY_ACTION_ALLOW` колонок. Если в датафрейме присутствует несколько `*_ALLOW`, вход разрешается только когда все присутствующие action columns равны `1`.

Проверка:
1. `py_compile PASS`: `src/mlbotnav/dataset.py`, `src/mlbotnav/backtest.py`, `src/mlbotnav/optuna_space.py`.
2. Focused tests: `96/96 OK` (`tests.test_dataset_inference_mode`, `tests.test_backtest_fields`, `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`).
3. Matrix compile `PASS` для F001-F005: каждая матрица имеет только свои два profiles.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260622T112135Z.json`.

Max-anchor fix:
`src/mlbotnav/optuna_space.py` теперь сохраняет правый край диапазона `max` даже когда шаг не попадает в него ровно. Для F003 `F003_thr_pct` теперь компилируется как `60` значений: первый `0.03`, последние `[1.17, 1.19, 1.20]`.

Проверка после max-anchor fix:
1. `py_compile PASS`: `src/mlbotnav/optuna_space.py`.
2. Focused tests: `98/98 OK`.
3. F003 matrix compile proof: `60 0.03 [1.17, 1.19, 1.2] True`.

## B001 RET_N ladder tournament 2026-06-22

Статус: `B001_RET_N_LADDER_READY_SMOKE_OK`.

Решение:
для блока `B001 / price_volatility / Цена и волатильность` добавлен отдельный турнирный паспорт:
`blocks.B001.active_passports.B001_RET_N_TOURNAMENT`.

Смысл:
это не 5 отдельных блоков, а один блок B001 с 5 паспортами F001-F005. Турнир перебирает все непустые составы из F001-F005: `31` комбинацию.

Правило входа:
для каждого состава backtest применяет `AND` по всем присутствующим runtime action columns. Например, состав `F002+F005` разрешает вход только если `F002_RET3_ALLOW=1` и `F005_RET24_ALLOW=1`.

Код:
1. `src/mlbotnav/b001_ret_n_ladder_tournament.py` генерирует 31 чистую matrix и manifest.
2. `APTuna/run_b001_ret_n_ladder_tournament.ps1` запускает выбранные matrix через текущий APTuna process-pool и собирает общий JSON/MD отчет.
3. `src/mlbotnav/optuna_space.py` поддерживает `passport_mode.policy=subset_allowlist` для турнирных подмножеств; одиночные паспорта остаются строгими.

Manifest artifact:
`reports/qa_gate/b001_ret_n_ladder_matrices_20260622T115638Z/manifest.json`.

DryRun artifact:
`reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115811Z.json`.

Smoke artifact:
`reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115930Z.json`.

Smoke result:
1. Mode: `long_only`.
2. Train: `2026-05-31`.
3. OOS: `2026-06-01`.
4. Combos: `1/31` (`B001_RET_N_F001`).
5. Trials: `6` total, process workers `3`.
6. Runner status: `OK`.
7. APTuna child exit code: `0`.
8. `best_oos` extracted into tournament report; smoke result has `0` OOS trades and is not a candidate. Это только проверка runner path, не baseline.

Validation:
1. `py_compile PASS`: `src/mlbotnav/optuna_space.py`, `src/mlbotnav/b001_ret_n_ladder_tournament.py`.
2. Tests: `tests.test_b001_ret_n_ladder_tournament`, `tests.test_optuna_space_constraints`, `tests.test_dataset_inference_mode`, `tests.test_backtest_fields`: `35/35 OK`.
3. Extended focused tests with Optuna runtime: `83/83 OK`.

Full run command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## B001 solo-selection decision 2026-06-22

Статус: `B001_RET_N_SOLO_SELECTION_ONLY`.

Решение после полного 31-комбо прогона:
комбинационный tournament через `AND` больше не является baseline. Он остается только diagnostic-only.

Причина:
полный LONG-прогон `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T120806Z.json` дал `31/31 ok`, но `28/31` комбинаций имели `0` сделок. Лучший `F002+F004` дал только `1` сделку, `+0.7845%` с плечом `10x`, выход `timeout`, `target_reached=false`; это не кандидат.

Новое правило:
1. Внутри B001 калибруем только одиночные фичи F001-F005.
2. В следующий этап проходит только одна лучшая одиночная фича, если она tradeful и не минусовая на OOS.
3. Комбинации F001-F005 не запускать как baseline.
4. Комбинации разрешены только как явная diagnostic-команда с `-EnableCombinationTournament`.

Технический фикс:
`APTuna/run_b001_ret_n_ladder_tournament.ps1` теперь по умолчанию выбирает только `StartIndex=1..EndIndex=5`. Попытка запустить `EndIndex > 5` без `-EnableCombinationTournament` останавливается с ошибкой.

Baseline solo command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Проверка:
1. Default dry-run выбирает `5` одиночных фич.
2. `EndIndex=31` без `-EnableCombinationTournament` блокируется.
3. `py_compile PASS`: `src/mlbotnav/b001_ret_n_ladder_tournament.py`, `src/mlbotnav/optuna_space.py`.
4. Focused tests: `35/35 OK`.

## F022 OBV slope 5 passport run 2026-06-22

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Паспорт:
`docs/CALIBRATION_NODE_CURRENT/passports/features/F022_obv_slope5_1m_strict_passport.md`.

Блок/матрица:
1. Registry: `configs/calibration_action_passports.yaml`, `B011/F022`, block `volume_flow`, action `F022_OBVSLOPE5_ALLOW`.
2. Matrix: `configs/calibration_matrices/passport_actions/F022_obv_slope5_1m_entry_filter.yaml`.

Runtime/backtest:
`src/mlbotnav/dataset.py` считает `F022_OBVSLOPE5_ALLOW` по паспорту: `(OBV - OBV.shift(5)) / SMA(volume, 20)`.
`src/mlbotnav/backtest.py` применяет эту колонку как entry-action gate.

Clean LONG/SHORT result:
1. LONG params `F022_slope_dir=UP`, `F022_slope_thr=7.2`; OOS `0.000000%`, trades `0`.
2. SHORT params `F022_slope_dir=DOWN`, `F022_slope_thr=8.2`; OOS `-17.479067%`, trades `3`, wins/losses `0/3`, exits `timeout=2`, `sl=1`.

Gate fact:
final OOS reports show `entry_action_gate_active=true` and `entry_action_gate_columns=['F022_OBVSLOPE5_ALLOW']`.

Artifact:
`reports/qa_gate/f022_obv_slope5_long_short_audit_20260622T162356Z_RU.md`.

Final status:
`NO_GO`; no candidate promoted.

Validation:
1. `py_compile PASS`.
2. Focused tests: `120/120 OK`.
3. Matrix compile `PASS` for LONG/SHORT.
4. Launcher/manual post-audit `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260622T181926Z.json`.

## F023 MFI14 passport run 2026-06-22

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Паспорт:
`docs/CALIBRATION_NODE_CURRENT/passports/features/F023_mfi14_1m_combined_strict_passport.md`.

Блок/матрица:
1. Registry: `configs/calibration_action_passports.yaml`, `B012/F023`, block `volume_flow`, action `F023_MFI14_ALLOW`.
2. Matrix: `configs/calibration_matrices/passport_actions/F023_mfi14_1m_combined_entry_filter.yaml`.

Runtime/backtest:
`src/mlbotnav/dataset.py` считает `F023_MFI14_ALLOW` поверх MFI14 по режимам `LEVEL` и `CROSS_LEVEL`.
`src/mlbotnav/backtest.py` применяет эту колонку как entry-action gate.

Clean LONG/SHORT result:
1. LONG params `LEVEL GREATER level=88`; OOS `-4.474397%`, trades `1`, wins/losses `0/1`, exits `timeout=1`.
2. SHORT params `LEVEL LESS level=81`; OOS `-20.546537%`, trades `6`, wins/losses `0/6`, exits `timeout=6`.

Gate fact:
final OOS reports show `entry_action_gate_active=true` and `entry_action_gate_columns=['F023_MFI14_ALLOW']`.

Artifact:
`reports/qa_gate/f023_mfi14_long_short_audit_20260622T163809Z_RU.md`.

Final status:
`NO_GO`; no candidate promoted.

Validation:
1. `py_compile PASS`.
2. Focused tests: `122/122 OK`.
3. Matrix compile `PASS` for LONG/SHORT.
4. Launcher post-audit `text_guard PASS`.

## DENSITY/VPOC Block A F025/F029/F033/F034 passport run 2026-06-22

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Паспорт:
`docs/CALIBRATION_NODE_CURRENT/passports/features/DENSITY_VPOC_F025_F034_3BLOCK_FIXED_COMMENTS.md`.

Решение:
по правилу паспорта не запускали все F025-F034 одной кучей. Сейчас подключен и прогнан только `BLOCK A / VPOC_CORE`: `F025`, `F029`, `F033`, `F034`.
`BLOCK B / ZONE_DENSITY` (`F026`, `F027`, `F030`, `F031`) и `BLOCK C / VPOC_STRENGTH` (`F028`, `F032`) остаются planned.

Блок/матрицы:
1. Registry: `configs/calibration_action_passports.yaml`, `B013/DENSITY_A_VPOC_CORE`.
2. Matrices:
   - `configs/calibration_matrices/passport_actions/F025_vpocdist60_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F029_vpocdist240_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F033_vpocdrift20_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F034_clusterratio_entry_filter.yaml`.

Clean LONG/SHORT result:
1. F025 LONG `-60.069331%`, trades `20`; F025 SHORT `-6.778638%`, trades `3`.
2. F029 LONG `0.000000%`, trades `0`; F029 SHORT `-18.625751%`, trades `6`.
3. F033 LONG `-14.115533%`, trades `4`; F033 SHORT `-3.624721%`, trades `1`.
4. F034 LONG `0.000000%`, trades `0`; F034 SHORT `-10.692022%`, trades `3`.

Best tradeful:
`F033 SHORT`, OOS `-3.624721%`, trades `1`, exit `timeout=1`; still `NO_GO`.

Gate fact:
all final OOS reports show `entry_action_gate_active=true` and a single matching action column per passport.

Artifact:
`reports/qa_gate/density_vpoc_block_a_f025_f029_f033_f034_audit_20260622T165812Z_RU.md`.

Final status:
`NO_GO`; no candidate promoted.

Validation:
1. `py_compile PASS`.
2. Focused tests: `124/124 OK`.
3. Matrix compile `PASS` for F025/F029/F033/F034 LONG/SHORT.
4. Launcher post-audit `text_guard PASS`.

## LEVEL/RANGE/CHANNEL Block A F035/F036/F037 passport run 2026-06-22

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Паспорт:
`docs/CALIBRATION_NODE_CURRENT/passports/features/LEVEL_RANGE_CHANNEL_F035_F039_strict_passport.md`.

Решение:
по порядку паспорта сейчас подключен и прогнан только `BLOCK A / LEVEL_A`: `F035`, `F036`, `F037`.
`BLOCK B / RANGE` (`F038`) и `BLOCK C / CHANNEL` (`F039`) не запускались и остаются следующими шагами.

Блок/матрицы:
1. Registry: `configs/calibration_action_passports.yaml`, `B014/LEVEL_A уровни поддержки/сопротивления`.
2. Matrices:
   - `configs/calibration_matrices/passport_actions/F035_supportdist_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F036_resdist_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F037_levelstrength_entry_filter.yaml`.

Runtime/backtest:
`src/mlbotnav/dataset.py` считает `F035_SUPPORTDIST_ALLOW`, `F036_RESDIST_ALLOW`, `F037_LEVELSTRENGTH_ALLOW` только когда присутствуют параметры соответствующего паспорта.
`src/mlbotnav/backtest.py` применяет эти колонки как entry-action gates.

Clean LONG/SHORT result:
1. F035 LONG `NEAR thr=1.81%`, OOS `-6.153364%`, trades `2`, exits `timeout=2`; F035 SHORT `NEAR thr=1.54%`, OOS `-18.625751%`, trades `6`, exits `timeout=6`.
2. F036 LONG `FAR thr=0.22%`, OOS `-12.920893%`, trades `3`, exits `timeout=3`; F036 SHORT `NEAR thr=0.93%`, OOS `-13.301553%`, trades `4`, exits `timeout=4`.
3. F037 LONG `RESISTANCE STRONG thr=2.0`, OOS `0.000000%`, trades `0`; F037 SHORT `NEAREST STRONG thr=8.5`, OOS `-18.104190%`, trades `7`, exits `timeout=7`.

Best tradeful:
`F035 LONG`, OOS `-6.153364%`, trades `2`; still `NO_GO`.

Gate fact:
all final OOS reports show `entry_action_gate_active=true` and a single matching action column per passport.

Artifact:
`reports/qa_gate/level_range_channel_block_a_f035_f036_f037_audit_20260622T171500Z_RU.md`.

Final status:
`NO_GO`; no candidate promoted.

Validation:
1. `py_compile PASS`.
2. Focused tests: `126/126 OK`.
3. Matrix compile `PASS` for F035/F036/F037 LONG/SHORT.
4. Launcher post-audit `text_guard PASS`.

## FIBONACCI_GRID F040/F041 passport run 2026-06-22

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Паспорт:
`docs/CALIBRATION_NODE_CURRENT/passports/features/FIBONACCI_F040_F041_anchor_grid_strict_passport_v3.md`.

Блок/матрицы:
1. Registry: `configs/calibration_action_passports.yaml`, `B015/FIBONACCI_GRID anchor grid`.
2. Matrices:
   - `configs/calibration_matrices/passport_actions/F040_fib0382dist_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F041_fib0618dist_entry_filter.yaml`.

Runtime/backtest:
`src/mlbotnav/dataset.py` строит подтвержденную fib-сетку по последней подтвержденной паре alternating pivot и выпускает `F040_FIB0382DIST_ALLOW`, `F041_FIB0618DIST_ALLOW` только при наличии параметров соответствующего паспорта.
`src/mlbotnav/backtest.py` применяет эти колонки как entry-action gates.

Clean LONG/SHORT result:
1. F040 LONG `DISTANCE NEAR thr=0.38%`, OOS `0.000000%`, trades `0`; F040 SHORT `SIDE BELOW`, OOS `-27.970937%`, trades `9`, exits `timeout=9`.
2. F041 LONG `DISTANCE NEAR thr=0.17%`, OOS `0.000000%`, trades `0`; F041 SHORT `DISTANCE NEAR thr=0.33%`, OOS `-9.615680%`, trades `4`, exits `timeout=4`.

Best tradeful:
`F041 SHORT`, OOS `-9.615680%`, trades `4`; still `NO_GO`.

Artifact:
`reports/qa_gate/fibonacci_grid_f040_f041_long_short_audit_20260622T173112Z_RU.md`.

Final status:
`NO_GO`; no candidate promoted.

Validation:
1. `py_compile PASS`.
2. Focused tests: `128/128 OK`.
3. Matrix compile `PASS` for F040/F041 LONG/SHORT.

## ENTRY_QUALITY_CONTEXT F042-F044 passport run 2026-06-22

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Паспорт:
`docs/CALIBRATION_NODE_CURRENT/passports/features/ENTRY_QUALITY_CONTEXT_F042_F044_strict_passport_v2.md`.

Блок/матрицы:
1. Registry: `configs/calibration_action_passports.yaml`, `B016/ENTRY_QUALITY_CONTEXT контекст входа`.
2. Matrices:
   - `configs/calibration_matrices/passport_actions/F044_rrcontext_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F042_tpcontext_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F043_slcontext_entry_filter.yaml`.

Runtime/backtest:
`src/mlbotnav/dataset.py` считает контекст входа от `SWING_LEVELS`, `DENSITY_VPOC` или `FIBONACCI_GRID`.
Для F042-F044 выпускаются канонические action columns и side-aware columns `*_LONG` / `*_SHORT`.
`src/mlbotnav/backtest.py` показывает канонический gate в диагностике, но применяет LONG/SHORT колонку по фактической стороне сигнала.

Clean LONG/SHORT result:
1. F044 LONG `DENSITY_VPOC POOR rr=2.70`, OOS `-1.145944%`, trades `1`, exits `timeout=1`; F044 SHORT `FIBONACCI_GRID GOOD rr=3.10`, OOS `-19.784205%`, trades `8`, exits `timeout=8`.
2. F042 LONG `DENSITY_VPOC LESS tp_dist=1.70%`, OOS `-17.392676%`, trades `3`, exits `timeout=2`, `sl=1`; F042 SHORT `FIBONACCI_GRID LESS tp_dist=1.85%`, OOS `0.000000%`, trades `0`.
3. F043 LONG `DENSITY_VPOC GREATER sl_dist=0.30%`, OOS `0.000000%`, trades `0`; F043 SHORT `FIBONACCI_GRID LESS sl_dist=2.15%`, OOS `-30.313954%`, trades `10`, exits `timeout=10`.

Gate fact:
all final OOS reports show `entry_action_gate_active=true` and a single matching canonical action column:
`F044_RRCONTEXT_ALLOW`, `F042_TPCONTEXT_ALLOW`, or `F043_SLCONTEXT_ALLOW`.

Artifact:
`reports/qa_gate/entry_quality_context_f042_f044_long_short_audit_20260622T175033Z_RU.md`.

Final status:
`NO_GO`; no candidate promoted.

Validation:
1. `py_compile PASS`.
2. Focused tests: `130/130 OK`.
3. Matrix compile `PASS` for F044/F042/F043 LONG/SHORT.
4. Launcher post-audit `text_guard PASS`.

## BREAKOUT_RETEST F045-F049 passport run 2026-06-22

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.

Паспорт:
`docs/CALIBRATION_NODE_CURRENT/passports/features/BREAKOUT_RETEST_F045_F049_strict_passport.md`.

Блок/матрицы:
1. Registry: `configs/calibration_action_passports.yaml`, `B017/BREAKOUT_RETEST пробой/ретест`.
2. Matrices:
   - `configs/calibration_matrices/passport_actions/F048_swinghighbreak_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F049_swinglowbreak_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F045_breakout_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F047_retest_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F046_falsebreak_entry_filter.yaml`.

Runtime/backtest:
`src/mlbotnav/dataset.py` считает confirmed swing levels и action gates `F045_BREAKOUT_ALLOW`, `F046_FALSEBREAK_ALLOW`, `F047_RETEST_ALLOW`, `F048_SWINGHIGHBREAK_ALLOW`, `F049_SWINGLOWBREAK_ALLOW`.
`src/mlbotnav/backtest.py` применяет эти колонки как isolated entry-action gates.

Clean LONG/SHORT result:
1. F048 LONG `0.000000%/0 trades`; F048 SHORT `0.000000%/0 trades`.
2. F049 LONG `-12.862590%/6 trades`; F049 SHORT `-20.254568%/4 trades`.
3. F045 LONG `0.000000%/0 trades`; F045 SHORT `-3.482265%/2 trades`.
4. F047 LONG `-11.000000%/1 trade`; F047 SHORT `-12.464525%/3 trades`.
5. F046 LONG `0.000000%/0 trades`; F046 SHORT `-5.366391%/1 trade`.

Best tradeful:
`F045 SHORT`, OOS `-3.482265%`, trades `2`; still `NO_GO`.

Decision:
No B017 candidate is accepted. The only train-gate pass was `F049 SHORT`, but OOS was `-20.254568%`, so it is rejected.

Artifact:
`reports/qa_gate/b017_breakout_retest_f045_f049_audit_20260622T181600Z.md`.

Validation:
1. `py_compile PASS`.
2. Focused tests: `3/3 OK` for B017 dataset/backtest/Optuna constraints.
3. Matrix compile `PASS` for F045-F049 LONG/SHORT.
4. Launcher post-audit `text_guard PASS`.

## MARKET_STRUCTURE F050-F052 passport run 2026-06-22

Статус: `IMPLEMENTED_LONG_SHORT_AUDITED_POSITIVE_TEST_CANDIDATE`.

Паспорт:
`docs/CALIBRATION_NODE_CURRENT/passports/features/MARKET_STRUCTURE_F050_F052_strict_passport.md`.

Блок/матрицы:
1. Registry: `configs/calibration_action_passports.yaml`, `B018/MARKET_STRUCTURE BOS/CHOCH`.
2. Matrices:
   - `configs/calibration_matrices/passport_actions/F050_bosup_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F051_bosdown_entry_filter.yaml`.
   - `configs/calibration_matrices/passport_actions/F052_choch_entry_filter.yaml`.

Runtime/backtest:
`src/mlbotnav/dataset.py` считает internal/external market structure state и action gates `F050_BOSUP_ALLOW`, `F051_BOSDOWN_ALLOW`, `F052_CHOCH_ALLOW`.
`src/mlbotnav/backtest.py` применяет эти колонки как isolated entry-action gates.

Clean LONG/SHORT result:
1. F050 LONG `0.000000%/0 trades`; F050 SHORT `0.000000%/0 trades`.
2. F051 LONG `0.000000%/0 trades`; F051 SHORT `+2.810523%/1 trade`, `goal_pass`.
3. F052 LONG `0.000000%/0 trades`; F052 SHORT `0.000000%/0 trades`.

Best candidate:
`F051 SHORT`, OOS `+2.810523%`, trades `1`, params `INTERNAL`, `break_buffer_pct=0.07`, `confirm_bars=2`, `require_bias=NOT_BULLISH`.

Decision:
`F051 SHORT` is `POSITIVE_TEST_CANDIDATE`, not production GO. Reason: positive OOS but only one OOS trade on one 1d/1d window; needs follow-up validation.

Artifact:
`reports/qa_gate/b018_market_structure_f050_f052_audit_20260622T183500Z.md`.

Validation:
1. `py_compile PASS`.
2. Focused tests: `3/3 OK` for B018 dataset/backtest/Optuna constraints.
3. Matrix compile `PASS` for F050-F052 LONG/SHORT.
4. Launcher post-audit `text_guard PASS`.
## CANDLE_PATTERNS F053-F060 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b019_candle_patterns_f053_f060_audit_20260622T190530Z.md`.
Current fact: user supplied `CANDLE_PATTERNS_F053_F060_strict_passport.md`; implemented B019 `CANDLE_PATTERNS свечные паттерны`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/CANDLE_PATTERNS_F053_F060_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B019`.
Matrices: `F055_pinbull_entry_filter.yaml`, `F056_pinbear_entry_filter.yaml`, `F059_engulfbull_entry_filter.yaml`, `F060_engulfbear_entry_filter.yaml`, `F057_hammer_entry_filter.yaml`, `F058_shootingstar_entry_filter.yaml`, `F054_insidebar_entry_filter.yaml`, `F053_doji_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F055 LONG `0.000000%/0 trades`; F055 SHORT `0.000000%/0 trades`.
2. F056 LONG `0.000000%/0 trades`; F056 SHORT `0.000000%/0 trades`.
3. F059 LONG `-60.087983%/22 trades`; F059 SHORT `0.000000%/0 trades`.
4. F060 LONG `0.000000%/0 trades`; F060 SHORT `0.000000%/0 trades`.
5. F057 LONG `0.000000%/0 trades`; F057 SHORT `0.000000%/0 trades`.
6. F058 LONG `0.000000%/0 trades`; F058 SHORT `0.000000%/0 trades`.
7. F054 LONG `0.000000%/0 trades`; F054 SHORT `-8.438667%/2 trades`.
8. F053 LONG `-11.213252%/3 trades`; F053 SHORT `0.000000%/0 trades`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B019 tests `3/3 OK`; matrix compile PASS for F053-F060 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T190822Z.json`.

## DIVERGENCE_PATTERNS F061-F066 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b020_divergence_patterns_f061_f066_audit_20260622T193300Z.md`.
Current fact: user supplied `DIVERGENCE_PATTERNS_F061_F066_strict_passport.md`; implemented B020 `DIVERGENCE_PATTERNS дивергенции`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/DIVERGENCE_PATTERNS_F061_F066_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B020`.
Matrices: `F061_rsibulldiv_entry_filter.yaml`, `F062_rsibeardiv_entry_filter.yaml`, `F063_macdbulldiv_entry_filter.yaml`, `F064_macdbeardiv_entry_filter.yaml`, `F065_obvbulldiv_entry_filter.yaml`, `F066_obvbeardiv_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F061 LONG `-7.123789%/2 trades`; F061 SHORT `0.000000%/0 trades`.
2. F062 LONG `0.000000%/0 trades`; F062 SHORT `0.000000%/0 trades`.
3. F063 LONG `-37.837211%/12 trades`; F063 SHORT `0.000000%/0 trades`.
4. F064 LONG `0.000000%/0 trades`; F064 SHORT `0.000000%/0 trades`.
5. F065 LONG `-10.822526%/4 trades`; F065 SHORT `0.000000%/0 trades`.
6. F066 LONG `0.000000%/0 trades`; F066 SHORT `0.000000%/0 trades`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B020 tests `3/3 OK`; matrix compile PASS for F061-F066 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T193442Z.json`.

## PATTERN_QUALITY F067-F068 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b021_pattern_quality_f067_f068_audit_20260622T194700Z.md`.
Current fact: user supplied `PATTERN_QUALITY_F067_F068_strict_passport.md`; implemented B021 `PATTERN_QUALITY качество паттерна`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_QUALITY_F067_F068_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B021`.
Matrices: `F067_patternstrength_entry_filter.yaml`, `F068_patternage_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F067 LONG `0.000000%/0 trades`; F067 SHORT `-18.202040%/6 trades`.
2. F068 LONG `-6.153364%/2 trades`; F068 SHORT `-59.898861%/26 trades`.
Final status: `NO_GO`; no positive tradeful candidate. Best non-negative result is F067 LONG but it has zero OOS trades.
Validation: `py_compile PASS`; focused B021 tests `3/3 OK`; matrix compile PASS for F067/F068 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T194938Z.json`.

## CHART_PATTERNS F069-F077 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b022_chart_patterns_f069_f077_audit_20260622T202100Z.md`.
Current fact: user supplied `CHART_PATTERNS_F069_F077_strict_passport.md`; implemented B022 `CHART_PATTERNS графические паттерны`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/CHART_PATTERNS_F069_F077_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B022`.
Matrices: `F077_rangeflag_entry_filter.yaml`, `F073_triangle_entry_filter.yaml`, `F074_pennant_entry_filter.yaml`, `F075_wedgerising_entry_filter.yaml`, `F076_wedgefalling_entry_filter.yaml`, `F069_doublebottom_entry_filter.yaml`, `F070_doubletop_entry_filter.yaml`, `F071_headshoulders_entry_filter.yaml`, `F072_invheadshoulders_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F077 LONG `-19.434440%/7 trades`; F077 SHORT `-17.890148%/3 trades`.
2. F073 LONG/SHORT `0.000000%/0 trades`.
3. F074 LONG/SHORT `0.000000%/0 trades`.
4. F075 LONG/SHORT `0.000000%/0 trades`.
5. F076 LONG/SHORT `0.000000%/0 trades`.
6. F069 LONG `-49.737441%/21 trades`; F069 SHORT `-13.225011%/3 trades`.
7. F070 LONG `0.000000%/0 trades`; F070 SHORT `-21.410449%/7 trades`.
8. F071 LONG/SHORT `0.000000%/0 trades`.
9. F072 LONG `-6.837599%/1 trade`; F072 SHORT `-10.765093%/3 trades`.
Final status: `NO_GO`; no positive tradeful candidate. Best tradeful result is F072 LONG but still negative.
Validation: `py_compile PASS`; focused B022 tests `3/3 OK`; matrix compile PASS for F069-F077 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T202309Z.json`.

## PATTERN_CONFIRMATION F078-F079 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b023_pattern_confirmation_f078_f079_audit_20260622T203700Z.md`.
Current fact: user supplied `PATTERN_CONFIRMATION_F078_F079_strict_passport(1).md`; implemented B023 `PATTERN_CONFIRMATION confirmation of existing pattern_event`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_CONFIRMATION_F078_F079_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B023`.
Matrices: `F079_patternlevelconf_entry_filter.yaml`, `F078_patternvolconf_entry_filter.yaml`.
Runtime/backtest: dataset emits isolated gates `F079_PATTERNLEVELCONF_ALLOW` and `F078_PATTERNVOLCONF_ALLOW`; backtest gates entries by the present single action column.
Clean LONG/SHORT result:
1. F079 LONG `0.000000%/0 trades`; F079 SHORT `0.000000%/0 trades`.
2. F078 LONG `-27.682109%/7 trades`; exits `6 timeout`, `1 sl`.
3. F078 SHORT `-7.323394%/4 trades`; exits `4 timeout`.
Final status: `NO_GO`; no positive tradeful candidate. Best tradeful result is F078 SHORT but still negative.
Validation: `py_compile PASS`; focused B023 tests `3/3 OK`; matrix compile PASS for F079/F078 LONG/SHORT; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T204015Z.json`.

## PATTERN_COMPOSITE_ENTRY F080-F081 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b024_pattern_composite_entry_f080_f081_audit_20260622T205500Z.md`.
Current fact: user supplied `PATTERN_COMPOSITE_ENTRY_F080_F081_strict_passport.md`; implemented B024 `PATTERN_COMPOSITE_ENTRY kompozitnyy pattern entry`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_COMPOSITE_ENTRY_F080_F081_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B024`.
Matrices: `F080_patternlong_entry_filter.yaml`, `F081_patternshort_entry_filter.yaml`.
Runtime/backtest: dataset emits side-specific gates `F080_PATTERNLONG_ALLOW` and `F081_PATTERNSHORT_ALLOW`; backtest treats F080 as LONG-only and F081 as SHORT-only.
Clean side-specific result:
1. F080 LONG `0.000000%/0 trades`; gate active, but after `min_expected_move` no eligible OOS entries.
2. F081 SHORT `-5.359455%/1 trade`; exit `timeout=1`.
Final status: `NO_GO`; no positive tradeful candidate.
Validation: `py_compile PASS`; focused B024 tests `3/3 OK`; matrix compile PASS for F080/F081; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T210111Z.json`.

## PATTERN_TRADE_CONTEXT F082-F083 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b025_pattern_trade_context_f082_f083_audit_20260622T211600Z.md`.
Current fact: user supplied `PATTERN_TRADE_CONTEXT_F082_F083_strict_passport.md`; implemented B025 `PATTERN_TRADE_CONTEXT SL/TP context`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_TRADE_CONTEXT_F082_F083_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B025`.
Matrices: `F082_patternslbuf_entry_filter.yaml`, `F083_patterntpladder_entry_filter.yaml`.
Runtime/backtest: dataset emits side-aware gates `F082_PATTERNSLBUF_ALLOW_LONG/SHORT` and `F083_PATTERNTPLADDER_ALLOW_LONG/SHORT`; backtest applies side-aware action columns when present.
Clean LONG/SHORT result:
1. F082 LONG `0.000000%/0 trades`; F082 SHORT `-25.094610%/7 trades`, exits `timeout=7`.
2. F083 LONG `-35.921536%/12 trades`, exits `timeout=11`, `sl=1`; F083 SHORT `-70.280106%/35 trades`, exits `timeout=35`.
Final status: `NO_GO`; no positive tradeful candidate. Best non-negative result is F082 LONG but it has zero OOS trades.
Validation: `py_compile PASS`; focused B025 tests `3/3 OK`; matrix compile/passport allowlist PASS for F082/F083 LONG/SHORT; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T211551Z.json`.

## F001-F083 Passport Route Full Audit 2026-06-23
Status: `warn_with_completeness_gaps`.
Artifact: `reports/qa_gate/f001_f083_passport_full_audit_20260623.md`.
Machine artifacts:
1. `reports/qa_gate/f001_f083_passport_registry_matrix_machine_audit_20260623.json`.
2. `reports/qa_gate/f001_f083_runtime_backtest_machine_audit_20260623.json`.
3. `reports/qa_gate/f001_f083_passport_completeness_20260623.json`.

Summary:
Existing executable passport matrices are clean: `73` active/combined passport entries compile for `long_only` and `short_only` (`146` spaces), with passport-mode allowlists and no legacy params.
Full numeric coverage in this pre-F024 audit snapshot was incomplete: `72` strict active ids, `2` combined ids (`F017/F018` as `F017_F018`), `8` planned/not implemented ids (`F026/F027/F028/F030/F031/F032/F038/F039`), and one open F024 gap closed later in this document.
Runtime/backtest standard passport flow is isolated, but there is a latent stale-column risk because backtest applies every present `F*_ALLOW` column from its global list.

Decision:
Initial snapshot was `WARN_WITH_COMPLETENESS_GAPS`, not production GO. Follow-up closures later in this document closed F024, planned F026/F027/F028/F030/F031/F032/F038/F039, accepted F017/F018 as one Stochastic K/D passport, and hardened backtest against stale action columns.

## F024 VWAP Distance Passport Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f024_vwap_distance_long_short_audit_20260623T055200Z.md`.

Current fact: previously open `F024` is now closed as standalone `B026/F024` without renumbering already audited `B013-B025`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/F024_vwap_distance_1m_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B026`.
Matrix: `configs/calibration_matrices/passport_actions/F024_vwapdist_entry_filter.yaml`.
Runtime/backtest: dataset emits `F024_VWAPDIST_ALLOW`; backtest gates entries by this present single action column.

Clean LONG/SHORT result:
1. F024 LONG `-17.894975%/8 trades`; selected `DISTANCE NEAR`, `dist_thr_pct=2.35`; OOS gate columns `['F024_VWAPDIST_ALLOW']`.
2. F024 SHORT `0.000000%/0 trades`; selected `DISTANCE NEAR`, `dist_thr_pct=0.14`; OOS gate columns `['F024_VWAPDIST_ALLOW']`.

Final status: `NO_GO`; no candidate promoted. F024 is technically closed but not a standalone winner on this 1d/1d window.
Validation: `py_compile PASS`; focused tests `3/3 OK`; matrix compile PASS for LONG/SHORT; launcher ledger/text_guard PASS.

Updated completeness: `F024` is now closed. Remaining route gaps are `F026/F027/F028/F030/F031/F032`, `F038/F039`, the `F017/F018` combined-vs-split decision, and the stale action-column hardening task.

## F026 Density Bin Share 60 Passport Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f026_binshare60_long_short_audit_20260623T060100Z.md`.

Current fact: `F026 density_bin_share_60_1m` is now active under `B013/F026`.
Matrix: `configs/calibration_matrices/passport_actions/F026_binshare60_entry_filter.yaml`.
Runtime/backtest: dataset emits `F026_BINSHARE60_ALLOW`; OOS diagnostics show exactly `['F026_BINSHARE60_ALLOW']`.

Clean LONG/SHORT result:
1. F026 LONG `-1.145944%/1 trade`; selected `LESS`, `share_thr_pct=5`.
2. F026 SHORT `-24.712835%/9 trades`; selected `LESS`, `share_thr_pct=36`.

Final status: `NO_GO`; no candidate promoted. Baseline exits stayed TP/SL/timeout and were not calibrated inside F026.
Validation: `py_compile PASS`; focused tests `3/3 OK`; matrix compile PASS for LONG/SHORT; launcher ledger/text_guard PASS.

Updated completeness: `F026` is now closed. Remaining route gaps are `F027/F028/F030/F031/F032`, `F038/F039`, the `F017/F018` combined-vs-split decision, and the stale action-column hardening task.

## F027 Density Cluster Share 60 Passport Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f027_clustershare60_long_short_audit_20260623T062300Z.md`.

Current fact: `F027 density_cluster_share_60_1m` is now active under `B013/F027`.
Matrix: `configs/calibration_matrices/passport_actions/F027_clustershare60_entry_filter.yaml`.
Runtime/backtest: dataset emits `F027_CLUSTERSHARE60_ALLOW`; OOS diagnostics show exactly `['F027_CLUSTERSHARE60_ALLOW']`.

Clean LONG/SHORT result:
1. F027 LONG `-6.153364%/2 trades`; selected `LESS`, `share_thr_pct=30`.
2. F027 SHORT `-18.625751%/6 trades`; selected `LESS`, `share_thr_pct=36`.

Final status: `NO_GO`; no candidate promoted. Baseline exits stayed TP/SL/timeout and were not calibrated inside F027.
Validation: `py_compile PASS`; focused tests `3/3 OK`; matrix compile PASS for LONG/SHORT; launcher ledger/text_guard PASS.

Updated completeness: `F027` is now closed. Remaining route gaps are `F028/F030/F031/F032`, `F038/F039`, the `F017/F018` combined-vs-split decision, and the stale action-column hardening task.

## F028 Density VPOC Share 60 Passport Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f028_vpocshare60_long_short_audit_20260623T064000Z.md`.

Current fact: `F028 density_vpoc_share_60_1m` is now active under `B013/F028`.
Matrix: `configs/calibration_matrices/passport_actions/F028_vpocshare60_entry_filter.yaml`.
Runtime/backtest: dataset emits `F028_VPOCSHARE60_ALLOW`; OOS diagnostics show exactly `['F028_VPOCSHARE60_ALLOW']`.

Clean LONG/SHORT result:
1. F028 LONG `-1.145944%/1 trade`; selected `LESS`, `share_thr_pct=49`.
2. F028 SHORT `-18.625751%/6 trades`; selected `LESS`, `share_thr_pct=1`.

Final status: `NO_GO`; no candidate promoted. Baseline exits stayed TP/SL/timeout and were not calibrated inside F028.
Validation: `py_compile PASS`; focused tests `3/3 OK`; matrix compile PASS for LONG/SHORT; launcher ledger/text_guard PASS.

Updated completeness: `F028` is now closed. Remaining route gaps are `F030/F031/F032`, `F038/F039`, the `F017/F018` combined-vs-split decision, and the stale action-column hardening task.

## F030 Density Bin Share 240 Passport Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f030_binshare240_long_short_audit_20260623T070000Z.md`.

Current fact: `F030 density_bin_share_240_1m` is now active under `B013/F030`.
Matrix: `configs/calibration_matrices/passport_actions/F030_binshare240_entry_filter.yaml`.
Runtime/backtest: dataset emits `F030_BINSHARE240_ALLOW`; OOS diagnostics show exactly `['F030_BINSHARE240_ALLOW']`.

Clean LONG/SHORT result:
1. F030 LONG `-13.432324%/3 trades`; selected `LESS`, `share_thr_pct=4.0`; exits `timeout=3`.
2. F030 SHORT `-24.712835%/9 trades`; selected `LESS`, `share_thr_pct=19.0`; exits `timeout=9`.

Final status: `NO_GO`; no candidate promoted. Baseline exits stayed TP/SL/timeout and were not calibrated inside F030.
Validation: `py_compile PASS`; focused tests `3/3 OK`; matrix compile PASS for LONG/SHORT; launcher ledger/text_guard PASS.

Updated completeness: `F030` is now closed. Remaining route gaps are `F031/F032`, `F038/F039`, the `F017/F018` combined-vs-split decision, and the stale action-column hardening task.

## F031 Density Cluster Share 240 Passport Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f031_clustershare240_long_short_audit_20260623T071000Z.md`.

Current fact: `F031 density_cluster_share_240_1m` is now active under `B013/F031`.
Matrix: `configs/calibration_matrices/passport_actions/F031_clustershare240_entry_filter.yaml`.
Runtime/backtest: dataset emits `F031_CLUSTERSHARE240_ALLOW`; OOS diagnostics show exactly `['F031_CLUSTERSHARE240_ALLOW']`.

Clean LONG/SHORT result:
1. F031 LONG `-6.153364%/2 trades`; selected `LESS`, `share_thr_pct=27.0`; exits `timeout=2`.
2. F031 SHORT `-55.142239%/26 trades`; selected `LESS`, `share_thr_pct=40.0`; exits `timeout=26`.

Final status: `NO_GO`; no candidate promoted. Baseline exits stayed TP/SL/timeout and were not calibrated inside F031.
Validation: `py_compile PASS`; focused tests `3/3 OK`; matrix compile PASS for LONG/SHORT; launcher ledger/text_guard PASS.

Updated completeness: `F031` is now closed. Remaining route gaps are `F032`, `F038/F039`, the `F017/F018` combined-vs-split decision, and the stale action-column hardening task.

## F032 Density VPOC Share 240 Passport Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f032_vpocshare240_long_short_audit_20260623T072500Z.md`.

Current fact: `F032 density_vpoc_share_240_1m` is now active under `B013/F032`.
Matrix: `configs/calibration_matrices/passport_actions/F032_vpocshare240_entry_filter.yaml`.
Runtime/backtest: dataset emits `F032_VPOCSHARE240_ALLOW`; OOS diagnostics show exactly `['F032_VPOCSHARE240_ALLOW']`.

Clean LONG/SHORT result:
1. F032 LONG `-6.153364%/2 trades`; selected `LESS`, `share_thr_pct=20.5`; exits `timeout=2`.
2. F032 SHORT `-18.625751%/6 trades`; selected `LESS`, `share_thr_pct=15.5`; exits `timeout=6`.

Final status: `NO_GO`; no candidate promoted. Baseline exits stayed TP/SL/timeout and were not calibrated inside F032.
Validation: `py_compile PASS`; focused tests `3/3 OK`; matrix compile PASS for LONG/SHORT; launcher ledger/text_guard PASS.

Updated completeness: `F032` is now closed. Remaining route gaps are `F038/F039`, the `F017/F018` combined-vs-split decision, and the stale action-column hardening task.

## F038 Position In Range Passport Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f038_rangepose_long_short_audit_20260623T074000Z.md`.

Current fact: `F038 position_in_range_1m` is now active under `B014/F038`.
Matrix: `configs/calibration_matrices/passport_actions/F038_rangepose_entry_filter.yaml`.
Runtime/backtest: dataset emits `F038_RANGEPOSE_ALLOW`; OOS diagnostics show exactly `['F038_RANGEPOSE_ALLOW']`.

Clean LONG/SHORT result:
1. F038 LONG `-13.432324%/3 trades`; selected `LOW`, `level=70.0`; exits `timeout=3`.
2. F038 SHORT `-4.489987%/1 trade`; selected `HIGH`, `level=56.0`; exits `timeout=1`.

Final status: `NO_GO`; no candidate promoted. Baseline exits stayed TP/SL/timeout and were not calibrated inside F038.
Validation: `py_compile PASS`; focused tests `3/3 OK`; matrix compile PASS for LONG/SHORT; launcher ledger/text_guard PASS.

Updated completeness: `F038` is now closed. Remaining route gaps are `F039`, the `F017/F018` combined-vs-split decision, and the stale action-column hardening task.

## F039 Trend Channel Position Passport Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f039_channelpos_long_short_audit_20260623T080500Z.md`.

Current fact: `F039 trend_channel_pos_1m` is now active under `B014/F039`.
Matrix: `configs/calibration_matrices/passport_actions/F039_channelpos_entry_filter.yaml`.
Runtime/backtest: dataset emits `F039_CHANNELPOS_ALLOW`; OOS diagnostics show exactly `['F039_CHANNELPOS_ALLOW']`.

Clean LONG/SHORT result:
1. F039 LONG `-17.392676%/3 trades`; selected `LOWER`, `level=40.0`, `outside_thr=45.0`; exits `timeout=2`, `sl=1`.
2. F039 SHORT `0.000000%/0 trades`; selected `UPPER`, `level=85.0`, `outside_thr=0.0`.

Final status: `NO_GO`; no candidate promoted. Baseline exits stayed TP/SL/timeout and were not calibrated inside F039.
Validation: `py_compile PASS`; focused tests `3/3 OK`; matrix compile PASS for LONG/SHORT; launcher ledger/text_guard PASS.

Updated completeness: `F039` is now closed. Previously planned gap ids `F024/F026/F027/F028/F030/F031/F032/F038/F039` are closed. Follow-up decisions also closed `F017/F018` combined-vs-split and stale action-column hardening. F001-F083 audit findings are closed for the current passport route; no production GO is implied.

## Passport Control Index 2026-06-23
Status: `ACTIVE_CONTROL_INDEX`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_CONTROL_INDEX_RU.md`.
Audit: `reports/qa_gate/passport_control_index_audit_20260623T084500Z.md`.

Current fact: created a compact human control panel for the passport-driven calibration route.

Accepted management model:
1. Passport MD = meaning and calibration grammar.
2. `configs/calibration_action_passports.yaml` = compact registry/contract.
3. `configs/calibration_matrices/passport_actions/*.yaml` = executable Optuna projection.
4. `reports/qa_gate/*` = result and audit decision.

Key rule: do not create one huge executable config for everything. Keep a hybrid model: one compact registry plus separate passports and matrices.

No-mixing boundary:
1. New signal starts from passport and registry, not direct Optuna YAML edit.
2. One `action_id` equals one action passport for baseline solo calibration.
3. LONG and SHORT remain separate runs.
4. Exits/risk/ML need separate passports before calibration.
5. Old full/catalog/feature_sweep matrices remain frozen references unless explicitly migrated through passport review.

Recommended next work after this index:
1. Result register is built.
2. `F051 SHORT` validation is complete and failed promotion; choose the next passport/feature route or new validation idea.

## Passport Result Register F001-F083 2026-06-23
Status: `ACTIVE_RESULT_REGISTER`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_RESULT_REGISTER_RU.md`.
Audit: `reports/qa_gate/passport_result_register_audit_20260623T084702Z.md`.

Current fact: built the compact F001-F083 result register for the current passport-driven route.

Key decision:
1. No `F001-F083` feature is production GO.
2. `F051 BOS down SHORT` had one historical positive window: `+2.810523%`, `1` OOS trade.
3. `F051 SHORT` was validated on additional windows and failed promotion: all three adjacent OOS windows had `0` trades.
4. `F017/F018` remains an accepted combined Stochastic passport decision, not a performance promotion.
5. Old broad Optuna/chronology artifacts remain frozen references unless explicitly migrated through passport review.

Validation: explicit id coverage `F001-F083 PASS`; text_guard `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T084932Z.json`.

Recommended next work:
1. Pick the next passport/feature route or define a new validation idea. No current F001-F083 candidate is ready for promotion.

## F051 SHORT Multi-Day Validation 2026-06-23
Status: `VALIDATION_FAIL_NO_PROMOTION`.
Artifact: `reports/qa_gate/f051_short_multiday_validation_audit_20260623T091000Z.md`.

Current fact: ran the next strict validation point for the only previous positive test candidate, `F051 BOS down SHORT`.

Baseline positive window:
1. Train `2026-05-31`, test `2026-06-01`: `+2.810523%`, `1` OOS trade.

New validation windows:
1. Train `2026-05-28`, test `2026-05-29`: `0.000000%`, `0` trades.
2. Train `2026-05-29`, test `2026-05-30`: `0.000000%`, `0` trades.
3. Train `2026-05-30`, test `2026-05-31`: `0.000000%`, `0` trades.

Gate isolation: all new runs used only `F051_BOSDOWN_ALLOW`; no old/stale action gate was active.

Decision: `F051 SHORT` did not reproduce. It is not promoted, not exported to ML, and not allowed into combined blocks. `F001-F083` remains `NO_PRODUCTION_GO`.

Validation: py_compile `PASS`; focused tests `3/3 OK`; matrix compile `PASS`; launcher ledger audits `PASS`; recorded text_guard after docs update `reports/qa_gate/recovery_r5_text_guard_20260623T091217Z.json`.

Recommended next work:
1. Pick the next passport/feature route or define a new validation idea. No current F001-F083 candidate is ready for promotion.

## F001-F083 Passport Route Closeout 2026-06-23
Status: `CLOSED_NO_PRODUCTION_GO`.
Artifact: `reports/qa_gate/f001_f083_route_closeout_audit_20260623T091500Z.md`.

Current fact: closed the full `F001-F083` passport route after the `F051 SHORT` validation failed.

Decision:
1. No `F001-F083` feature is production GO.
2. No `F001-F083` feature may be exported to ML, combined into blocks, or used as a candidate pool item.
3. `F051 SHORT` is not promotable after adjacent-window validation.
4. Old broad Optuna matrices and old chronology remain frozen references only.

Allowed next work:
1. Add a new passport/feature/hypothesis route.
2. Define a new validation idea with its own audit boundary.
3. Start separate exit/risk passports for TP/SL/timeout/dynamic exits.

## Core ML Bot TZ Audit 2026-06-23
Status: `PARTIAL_MATCH_WITH_STRONG_CALIBRATION_CORE`.
Artifact: `reports/qa_gate/core_ml_bot_tz_audit_20260623_RU.md`.

Current fact: compared the project against the user-provided TZ for a compact 1m autonomous ML trading bot core.

Decision:
1. Do not create a parallel root `trading_bot/` project tree.
2. Keep `src/mlbotnav` as the real implementation core.
3. Add small contracts/facades first, then fill missing CORE columns and trade-result dataset gaps.
4. Keep F001-F083 closed as `NO_PRODUCTION_GO`; do not reuse those results as candidates.
5. Future exit/risk work must use separate passports, not entry-passport matrices.

Recommended next work:
1. Add CORE contracts for features, entry action, exit action, risk rule, trade log, and ML dataset.
2. Add missing CORE feature columns and contract tests.
3. Add MAE/MFE and trade outcome labels before any new ML promotion.

## Optuna / ML / Entry / Exit Alignment Audit 2026-06-23
Status: `PASS_WITH_ML_DATASET_GAPS`.
Artifact: `reports/qa_gate/optuna_ml_entry_exit_alignment_audit_20260623T162411Z.md`.

Current fact: checked the current Optuna -> adaptive -> train pipeline -> OOS -> backtest chain for calibration params, action gates, trade entry/exit logic, report tables, and available candle ranges.

Decision:
1. Optuna calibration params do propagate into train/OOS/backtest.
2. Current F051 action gate is isolated as `F051_BOSDOWN_ALLOW`; stale action columns are not active for that contour.
3. JSON reports preserve `calibration_params`, but CSV trade/OOF tables do not carry `action_id`, `passport_id`, `block_id`, or `calibration_params_json` as row-level context.
4. Trade CSV has entry/exit fields and `exit_reason`, but it does not yet have ML-ready trade outcome labels: `trade_id`, `bars_in_trade`, `tp_hit`, `sl_hit`, `timeout_hit`, `mae_pct`, `mfe_pct`.
5. Current clean candle layer is `data/core/bybit_ohlcv` from `2026-01-26` through `2026-05-31`. `2026-06-01` exists only in `raw/quarantine`, is incomplete to `15:03 UTC`, and must not be treated as clean ML/OOS input until DQ/core promotion.

Next strict work:
1. Define and implement `ML_TRADE_DATASET_CONTRACT`.
2. Add row-level passport context into trade/OOS CSV outputs.
3. Add MAE/MFE and trade outcome labels.
4. Add a JSON-vs-CSV alignment audit.
5. Only then run larger clean window: train/calibration `2026-05-11..2026-05-24`, test/OOS `2026-05-25..2026-05-31`, layer `core`.

Validation: `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T112704Z.json`.

## Optuna / ML Separate Contours Action Plan 2026-06-23
Status: `ACTION_PLAN_WBS_READY`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.

Current fact: accepted and rewrote the route where Optuna and ML stay as two separate contours into numbered WBS steps.

Decision:
1. Optuna calibrates passports/actions and emits a candidate package.
2. ML reads only manually approved packages.
3. No automatic on-go transfer from Optuna to ML yet.
4. A package must be explicitly marked `APPROVED_FOR_ML` in a manual registry before ML ingest can read it.

Planned work budget: `10-14 hours` of engineering work, excluding long runtime waiting.

Next strict step:
1. `1.1 Create ML trade dataset contract document`.
2. Then `1.2` required identifiers.
3. Continue strictly through `1.7`, then move to `2.1`.

Validation: `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T115519Z.json`.

## Step 1.1 ML Trade Dataset Contract Document 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_1_audit_20260623T170449Z.md`.

Current fact: created the ML trade dataset contract document for the separated Optuna/ML contour.

Closed scope:
1. Table purpose documented.
2. Writer/reader responsibilities documented.
3. `APPROVED_FOR_ML` admission rule documented.
4. Required field groups documented.
5. Non-ML-ready artifacts documented.
6. Step `1.1` Definition Of Done documented.

Fix needed: `NO`.

Validation: `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T120631Z.json`.

Next strict step: `1.2 Зафиксировать обязательные идентификаторы`.

## Step 1.2 Required Identifiers 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_2_audit_20260623T170721Z.md`.

Current fact: fixed required identifiers for ML trade dataset contract.

Closed scope:
1. Run context identifiers fixed: `run_id`, `symbol`, `timeframe`, `data_layer`, `train_start`, `train_end`, `test_start`, `test_end`.
2. Passport context identifiers fixed: `block_id`, `passport_id`, `action_id`, `side`, `calibration_params_json`.
3. Each identifier now has source, format, and validation rule.
4. Missing identifier means `CONTRACT_FAIL`.
5. `side` has canonical row-level mapping.
6. `calibration_params_json` has canonical JSON comparison rule.

Fix needed: `NO`.

Validation: `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T120927Z.json`.

Next strict step: `1.3 Зафиксировать поля входа и выхода`.

## Step 1.3 Entry/Exit Fields 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_3_audit_20260623T171023Z.md`.

Current fact: fixed required entry/exit fields for ML trade dataset contract.

Closed scope:
1. Required entry/exit fields fixed: `entry_signal_time_utc`, `entry_time_utc`, `exit_time_utc`, `entry_price`, `exit_price`, `exit_reason`, `net_return`, `net_pnl_usd`.
2. Each field now has source, format, and validation rule.
3. Allowed `exit_reason` values are fixed: `tp`, `sl`, `sl_ambiguous`, `timeout`, `end_of_data`, `manual_close`, `unknown`.
4. Signal time and execution time are separated.
5. Exit time ordering rule is fixed.
6. Positive price rule is fixed.
7. Numeric return/PnL rule is fixed.

Fix needed: `NO`.

Validation: `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T121225Z.json`.

Next strict step: `1.4 Зафиксировать trade outcome labels`.

## Step 1.4 Trade Outcome Labels 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_4_audit_20260623T171324Z.md`.

Current fact: fixed required trade outcome labels for ML trade dataset contract.

Closed scope:
1. Required outcome labels fixed: `trade_id`, `bars_in_trade`, `tp_hit`, `sl_hit`, `timeout_hit`, `mae_pct`, `mfe_pct`.
2. Each outcome label now has source, format, and validation rule.
3. `trade_id` uniqueness/stability rule is fixed.
4. `bars_in_trade` is separated from `time_to_target_bars`.
5. Hit label mapping from `exit_reason` is fixed.
6. `mae_pct` and `mfe_pct` rules are fixed.
7. Outcome labels are separated from `target_up`.

Fix needed: `NO`.

Validation: `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T121532Z.json`.

Next strict step: `1.5 Зафиксировать правило допуска в ML`.

## Step 1.5 ML Admission Rule 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_5_audit_20260623T171643Z.md`.

Current fact: fixed the manual admission rule for calibration packages into ML.

Closed scope:
1. Single admission source fixed: `configs/ml_approved_calibration_packages.yaml`.
2. Single allowed ML status fixed: `APPROVED_FOR_ML`.
3. Deny result fixed: `ML_ADMISSION_DENY`.
4. Forbidden statuses fixed: `DRAFT`, `NEEDS_AUDIT`, `REJECTED`, `VALIDATION_FAIL`, `NO_GO`, `UNKNOWN`, empty status.
5. Required package files fixed: `manifest.json`, `calibration_package.json`, `trade_log.csv`, `audit.md`, contract/alignment audit `PASS`.
6. Clean data layer rule fixed: `data_layer = core`.
7. `raw/quarantine` forbidden as clean ML input.
8. Manual approval metadata fixed: `approved_by`, `approved_at_utc`, `comment`.
9. Automatic Optuna-to-ML transfer is forbidden.

Fix needed: `NO`.

Validation: `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T121846Z.json`.

Next strict step: `1.6 Сделать проверку контракта`.

## Step 1.6 Contract Validator 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Contract: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Validator: `src/mlbotnav/ml_trade_dataset_contract.py`.
Tests: `tests/test_ml_trade_dataset_contract.py`.
Audit: `reports/qa_gate/ml_trade_dataset_contract_step_1_6_audit_20260623T122406Z.md`.
CLI report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T122406Z.json`.
Smoke CSV: `reports/qa_gate/ml_trade_dataset_contract_step_1_6_smoke_valid.csv`.

Current fact: created and verified the executable ML trade dataset contract validator.

Closed scope:
1. Validator checks required run/passport/entry/exit/outcome columns.
2. Validator enforces clean `data_layer = core`.
3. Validator checks train/test window dates.
4. Validator parses non-empty `calibration_params_json`.
5. Validator checks row-level side, trade time ordering, positive prices, numeric PnL/return.
6. Validator checks `exit_reason`, hit labels, `trade_id` uniqueness, MAE/MFE sign rules.
7. CLI writes JSON audit reports into `reports/qa_gate`.

Fix needed: `NO`.

Validation:
1. `py_compile` PASS.
2. `unittest tests.test_ml_trade_dataset_contract` PASS, `4/4 OK`.
3. CLI smoke PASS, rows `1`, failed rows `0`, missing columns `0`.
4. `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T122733Z.json`.

Next strict step: `1.7 Закрытие этапа 1`.

## Step 1.7 Stage 1 Closeout 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Contract: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Closeout audit: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.

Current fact: Stage 1 `ML Trade Dataset Contract` is closed.

Closed scope:
1. `1.1` contract document created.
2. `1.2` required identifiers fixed.
3. `1.3` entry/exit fields fixed.
4. `1.4` trade outcome labels fixed.
5. `1.5` ML admission rule fixed.
6. `1.6` executable validator created and verified.

Boundary:
1. Stage 1 defines the contract and validator.
2. Stage 1 does not yet enrich real trade CSV outputs.
3. Stage 1 does not yet implement JSON-vs-CSV alignment audit.
4. No big calibration/OOS run is allowed yet.

Fix needed: `NO`.

Validation:
1. Artifact existence check PASS.
2. `py_compile` PASS.
3. `unittest tests.test_ml_trade_dataset_contract` PASS, `4/4 OK`.
4. Latest `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T123232Z.json`.

Next strict step: `2.1 Добавить run-level context`.

## Step 2.1 Run-Level Context 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Contract: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.

Current fact: run-level context is now added before writing pipeline and OOS trade CSV outputs.

Closed scope:
1. Added helper `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. `reports/pipeline/backtest_trades_*.csv` now receives `run_id`, `symbol`, `timeframe`, `data_layer`, `train_start`, `train_end`, `test_start`, `test_end`.
3. `reports/final_review/oos_backtest_trades_*.csv` now receives the same run-level context fields.
4. Added focused test `tests/test_ml_trade_dataset_enrichment.py`.

Boundary:
1. `2.1` only adds run-level context.
2. Passport context starts at `2.2`.
3. Trade identity, duration labels, hit labels, and MAE/MFE remain later Stage 2 steps.
4. Real trade CSV is not fully ML-ready until Stage 2 closeout.

Fix needed: `NO`.

Validation:
1. `py_compile` PASS with isolated `PYTHONPYCACHEPREFIX=reports/qa_gate/pycache_step_2_1`.
2. `unittest tests.test_ml_trade_dataset_enrichment tests.test_ml_trade_dataset_contract` PASS, `5/5 OK`.
3. `unittest tests.test_pipeline_train_eval_gate_overrides tests.test_backtest_fields` PASS, `48/48 OK`.

Next strict step: `2.2 Добавить passport context`.

## Step 2.2 Passport Context 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Contract: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.

Current fact: passport context is now added before writing pipeline and OOS trade CSV outputs.

Closed scope:
1. Added passport context helper in `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. `reports/pipeline/backtest_trades_*.csv` now receives `block_id`, `passport_id`, `action_id`, `calibration_params_json`, `entry_action_gate_columns`.
3. `reports/final_review/oos_backtest_trades_*.csv` now receives the same passport context fields.
4. Passport metadata is resolved from `configs/calibration_action_passports.yaml`.
5. Resolution uses active action gate columns first, then allowed calibration params.

Boundary:
1. `2.2` only adds passport context.
2. Trade identity, duration labels, hit labels, and MAE/MFE remain later Stage 2 steps.
3. Real trade CSV is not fully ML-ready until Stage 2 closeout.

Fix needed: `NO`.

Validation:
1. `py_compile` PASS with isolated `PYTHONPYCACHEPREFIX=reports/qa_gate/pycache_step_2_2`.
2. Focused unittest PASS, `55/55 OK`.
3. `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T124407Z.json`.

Next strict step: `2.3 Добавить trade identity`.

## Step 2.3 Trade Identity 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Contract: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.

Current fact: trade identity is now added before writing pipeline and OOS trade CSV outputs.

Closed scope:
1. Added trade identity helper in `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. `reports/pipeline/backtest_trades_*.csv` now receives `trade_id` and `entry_signal_time_utc`.
3. `reports/final_review/oos_backtest_trades_*.csv` now receives the same trade identity fields.
4. Trade ids are deterministic inside a run and preserve existing non-empty ids.

Boundary:
1. `2.3` only adds trade identity.
2. Duration labels, hit labels, and MAE/MFE remain later Stage 2 steps.
3. Real trade CSV is not fully ML-ready until Stage 2 closeout.

Fix needed: `NO`.

Validation:
1. `py_compile` PASS with isolated `PYTHONPYCACHEPREFIX=reports/qa_gate/pycache_step_2_3`.
2. Focused unittest PASS, `56/56 OK`.
3. `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T125332Z.json`.

Next strict step: `2.4 Добавить duration labels`.

## Step 2.4 Duration Labels 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Contract: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_4_duration_labels_audit_20260623T125816Z.md`.

Current fact: duration labels are now added before writing pipeline and OOS trade CSV outputs.

Closed scope:
1. Added duration label helper in `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. `reports/pipeline/backtest_trades_*.csv` now receives `bars_in_trade` and `holding_seconds`.
3. `reports/final_review/oos_backtest_trades_*.csv` now receives the same duration label fields.
4. Duration is calculated from `entry_time_utc` to `exit_time_utc`, with fallback to target timing fields when available.

Boundary:
1. `2.4` only adds duration labels.
2. Hit labels and MAE/MFE remain later Stage 2 steps.
3. Real trade CSV is not fully ML-ready until Stage 2 closeout.

Fix needed: `YES_APPLIED`.

Fix:
1. Initial test found pandas string dtype rejection when assigning numeric duration to newly empty columns.
2. Fixed by creating/casting duration columns as `object`.

Validation:
1. `py_compile` PASS with isolated `PYTHONPYCACHEPREFIX=reports/qa_gate/pycache_step_2_4`.
2. Focused unittest PASS, `57/57 OK`.
3. `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T125816Z.json`.

Next strict step: `2.5 Добавить hit labels`.

## Step 2.5 Hit Labels 2026-06-23
Status: `CLOSED_PASS`.
Plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Contract: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.

Current fact: hit labels are now added before writing pipeline and OOS trade CSV outputs.

Closed scope:
1. Added hit label helper in `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. `reports/pipeline/backtest_trades_*.csv` now receives `tp_hit`, `sl_hit`, `timeout_hit`, `end_of_data_hit`, `sl_ambiguous_hit`.
3. `reports/final_review/oos_backtest_trades_*.csv` now receives the same hit label fields.
4. Labels are derived from `exit_reason`.

Boundary:
1. `2.5` only adds hit labels.
2. MAE/MFE remain later Stage 2 steps.
3. Real trade CSV is not fully ML-ready until Stage 2 closeout.

Fix needed: `NO`.

Validation:
1. `py_compile` PASS with isolated `PYTHONPYCACHEPREFIX=reports/qa_gate/pycache_step_2_5`.
2. Focused unittest PASS, `58/58 OK`.
3. `text_guard PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T130320Z.json`.

Next strict step: `2.6 Добавить MAE/MFE`.

## B001 Single-Worker Fast Finish Audit 2026-06-24
Status: `DIAGNOSED_NOT_WORKER_FAILURE`.
Artifact: `reports/qa_gate/b001_single_worker_fast_finish_audit_20260624T180000Z_RU.md`.

Проверенный запуск: `reports/logs/optuna_pool_long_only_20260624T175647Z_w1.log`.

Факт: single-worker профиль дошел до рантайма корректно: `max_threads=9`, `search_workers=9`, `workers_used=9`, `n_trials_override=42`.

Причина быстрого завершения: не потеря мощности, а пустой семейный гейт `B001 family-unified strict 5/5`. Optuna завершила `42` trial за `00:00:23`: `18 completed`, `24 pruned`, `0 failed`; лучший кандидат имеет `EMPTY_ACTION_GATE`, `0` сделок, `signal_count_after_entry_action_gates=0`.

Следующий правильный диагностический шаг: оставить single-worker `1x9/9`, но проверить семейный режим `4/5` на 1д/1д. Если `4/5` пустой, проверить `3/5`. К 2н/1н переходить только после появления tradeful-кандидатов.

## Optuna Worker Profile Correction 2026-06-24
Status: `PROFILE_RULE_CORRECTED`.
Artifact: `reports/qa_gate/optuna_1x9_vs_3x3_worker_audit_20260624T183000Z_RU.md`.

Уточнение: `1x9/9` не является полным физическим эквивалентом старого `3x3/9`. Старый режим запускал три отдельных Python-процесса: `w1/w2/w3`, каждый с `--max-threads 3`, `--search-workers 3`, `--optuna-n-trials-override 14` при общем бюджете `42`. Новый режим запускает один Python-процесс `w1` с `--max-threads 9`, `--search-workers 9`, `--optuna-n-trials-override 42`.

Правило исправлено: для рабочих прогонов и проверки реальной нагрузки использовать `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`. `1x9/9` оставить как отдельный диагностический режим, когда нужна одна Optuna-история и один процесс.

Для B001 следующий рабочий диагностический шаг: вернуть `3x3/9` и проверить family-unified `4/5`, затем `3/5` при пустом результате.

## B001 Family-Unified 4/5 LONG 3x3/9 Check 2026-06-24
Status: `DONE_TRADEFUL_NEGATIVE_NO_PROMOTION`.
Artifact: `reports/qa_gate/b001_family_unified_4of5_long_3x3_audit_20260624T184500Z_RU.md`.

Проверка выполнена на `1д/1д`, LONG, `SOLUSDT 1m`, рабочий профиль `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`, `OptunaTrials=42`.

Итог: launcher `OK`, лучший worker `w3`, OOS `-5.071620930989562%`, `1` сделка. `w1/w2` остались пустыми. Семейное правило `4/5` сработало корректно: на сделке `F001..F004 = 1`, `F005 = 0`.

Вывод: `4/5` частично раздушил B001, но результат отрицательный. В ML ничего не передавать. Следующий диагностический шаг при продолжении B001: `3/5 LONG` на том же профиле `3x3/9`.
## Visual Entry Signal-Entry Contract v2 2026-06-25
Статус: `DEV_SIGNAL_ENTRY_CONTRACT_READY_NEEDS_USER_VISUAL_CONFIRM`.

Старый `v1` manual entries больше не является рабочей целью: он был восстановлен по центрам красных стрелок и помечен как `SUPERSEDED_BY_V2_SIGNAL_ENTRY_CONTRACT`.

Новый v2-контракт: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/manual_entries.json`.

Правило: красная `S#` показывает закрытую сигнальную свечу с фитилем/дном (`signal_candle_time_utc`), зеленая `ENTRY #` показывает вход на open следующей свечи (`target_entry_time_utc`).

Формула LONG с учетом slippage: `entry_price_with_slippage = entry_open_price * (1 + slippage_bps / 10000)`. Текущий визуальный slippage: `5` bps.

Проверочные PNG:
1. full-day: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_overlay_2026-05-12_20260625T102817Z.png`;
2. zoom panels: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_zoom_panels_20260625T102849Z.png`.

Времена v2: `S1 01:43 -> ENTRY 01:44`, `S2 04:15 -> ENTRY 04:16`, `S3 09:15 -> ENTRY 09:16`, `S4 12:34 -> ENTRY 12:35`, `S5 15:29 -> ENTRY 15:30`, `S6 16:59 -> ENTRY 17:00`.

До пользовательского визуального подтверждения v2 не передавать в ML и не считать финальной разметкой для scorer/runner.

## Visual Entry Instrument Stack Audit 2026-06-25
Статус: `DEV_AUDIT_READY_NEXT_NOISE_SUPPRESSION_RUNNER`.

Аудит: `reports/final_review/visual_entry_v3/instrument_stack_audit/visual_entry_instrument_stack_audit_20260625_RU.md`.

Текущий вывод: `DQ01/DQ03` полезны как high-recall карта зон дна, но не как готовый входной сигнал. `DQ01` ловит `10/11`, но дает `73` ложных входа; `DQ03` ловит `11/11`, но дает `95` ложных входов.

Следующее правильное действие: собрать diagnostic runner `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`. Он должен брать кандидаты `DQ01/DQ03`, группировать их в кластеры одного падения/дна/reclaim, выбирать максимум один вход внутри кластера и проверять passport-инструменты по ролям: context, trigger, confirm, suppress.

Первый круг признаков: `F035/F038/F009/F010/F012/F017_F018/F023/F020/F055/F057/F059`. Второй круг: `F024/F025/F028/F032/F040/F041`. Третий круг: `F050/F052/F061/F063/F065`. Четвертый круг: `F069/F072/F076/F077/F078/F079/F080` только после no-lookahead проверки `pattern_event`.

Граница: пока это только DEV-diagnostic. ML export, promotion, production GO и TP/SL-оптимизация запрещены до стабилизации входов и проверки на `2026-05-13`/`2026-05-14` без подкрутки.

## Visual Entry Noise Suppression Cluster Priority 2026-06-25
Статус: `DEV_RUNNER_DONE_NO_ML`.

Код: `src/mlbotnav/visual_entry_noise_suppression_cluster_priority_runner.py`.
Тест: `tests/test_visual_entry_noise_suppression_cluster_priority_runner.py`.
Отчет: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_noise_suppression_cluster_priority_20260512_DEV_RU.md`.
JSON: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_noise_suppression_cluster_priority_20260512_DEV.json`.
Главный PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp01_dq01_cluster10_score12_20260625T150100Z.png`.

Лучший DEV-слой: `CP01_DQ01_CLUSTER10_SCORE12`.

Итог:
1. было у `DQ01`: `10/11`, `73` false, `83` entries;
2. стало у `CP01`: `9/11`, `28` false, `37` entries;
3. precision выросла до `0.2432`;
4. recall `0.8182`;
5. f1 `0.3750`;
6. пропущены `08:26` и `17:00`.

Смысл результата: кластерное подавление шума работает и режет false больше чем в два раза, но пока теряет два ручных входа. В ML ничего не передавать. Следующий DEV-шаг: добрать `08:26` и `17:00` отдельным мягким подслоем или вторым cluster-priority вариантом без возврата к `73+` false.

Проверки: `py_compile PASS`; `tests.test_visual_entry_noise_suppression_cluster_priority_runner` `2/2 OK`; совместно с deep runner `3/3 OK`; `tests.test_render_visual_entry_overlay` `1/1 OK`; `text_guard PASS`, `reports/qa_gate/recovery_r5_text_guard_20260625T150159Z.json`; после проверок живых `python.exe` процессов по `MLbotNav/mlbotnav/APTuna/visual_entry` не осталось.

## Visual Entry CP06 Recover 2026-06-25
Статус: `DEV_RECOVER_DONE_11_OF_11_NO_ML`.

Код обновлен: `src/mlbotnav/visual_entry_noise_suppression_cluster_priority_runner.py`.
Тест обновлен: `tests/test_visual_entry_noise_suppression_cluster_priority_runner.py`.

Новый лучший DEV-слой: `CP06_CP01_RECOVER_NOWICK_LATE_RETEST`.

Итог на `2026-05-12`:
1. manual hits: `11/11`;
2. missed: `0`;
3. false: `28`;
4. entries: `39`;
5. precision: `0.2821`;
6. recall: `1.0000`;
7. f1: `0.4400`.

Recover добавил ровно два входа к `CP01`:
1. `08:25 -> 08:26`, source `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP`, reason `RECOVER_NOWICK_SUPPORT_PULLBACK`;
2. `16:59 -> 17:00`, source `DQ01_EQ01_PLUS_DEEP_RECLAIM`, reason `RECOVER_D03_LATE_RETEST`.

Главный PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp06_cp01_recover_nowick_late_retest_20260625T151725Z.png`.
Отчет: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_noise_suppression_cluster_priority_20260512_DEV_RU.md`.

Граница: результат закрывает DEV-день визуально, но не является ML/prod-кандидатом. Следующий правильный шаг: без подкрутки прогнать эту же механику на `2026-05-13` validation и `2026-05-14` holdout после пользовательского визуального подтверждения PNG.

Проверки: `py_compile PASS`; `tests.test_visual_entry_noise_suppression_cluster_priority_runner` `3/3 OK`; совместно visual-entry tests `5/5 OK`; `text_guard PASS`, `reports/qa_gate/recovery_r5_text_guard_20260625T151851Z.json`; после проверок живых `python.exe` процессов по `MLbotNav/mlbotnav/APTuna/visual_entry` не осталось.

## Visual Entry REVERSAL_BOTTOM_KNIFE_DROP_V0 2026-06-29
Статус: `DEV_RBKD_V0_BUILT_TOO_NOISY_NO_ML_NEXT_SWING_SUPPORT_EVENT`.

Аудит: `reports/final_review/visual_entry_v3/reversal_bottom_knife_drop/visual_entry_reversal_bottom_knife_drop_audit_20260629T090101Z_RU.md`.

Код: `src/mlbotnav/visual_entry_reversal_bottom_knife_drop_runner.py`.
Тест: `tests/test_visual_entry_reversal_bottom_knife_drop_runner.py`.

Проверена логика входа по пользовательскому контракту: signal-свеча дна закрылась, LONG-вход ставится на `open` следующей свечи, `slippage_bps=5`, `lookahead=NO`.

Результат без передачи в ML:

1. `2026-05-13` validation: лучший `RBKD03_PULLBACK_AFTER_RECLAIM`, `2/9` hits, `81` false, `83` entries, f1 `0.0435`.
2. `2026-05-14` holdout: лучший `RBKD03_PULLBACK_AFTER_RECLAIM`, `1/17` hits, `83` false, `84` entries, f1 `0.0198`.

Вывод: слой иногда видит ручные входы, но слишком шумный. Это не кандидат, не GO, не ML export. Пользовательские входы часто являются support/retest/trend-dip продолжением, а не классической перепроданностью. Следующий правильный шаг: отдельный diagnostic runner `SWING_SUPPORT_RETEST_EVENT_V1` с online event-state: открыть событие дна/ретеста, взять первый валидный вход, закрыть событие и включить cooldown.

Проверки: `py_compile PASS`; `tests.test_visual_entry_reversal_bottom_knife_drop_runner` `2/2 OK`; совместные visual-entry regression tests `5/5 OK`; `text_guard PASS`, `reports/qa_gate/recovery_r5_text_guard_20260629T085954Z.json`. После таймаутного перебора остановлены зависшие PID `14996` и `228`; повторная проверка живых Python-процессов по `MLbotNav/mlbotnav/APTuna/visual_entry` пустая.
## Visual Entry SWING_SUPPORT_RETEST_EVENT_V1 2026-06-29
Статус: `DEV_SSRE_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Аудит: `reports/final_review/visual_entry_v3/swing_support_retest_event/visual_entry_swing_support_retest_event_audit_20260629T092400Z_RU.md`.

Код: `src/mlbotnav/visual_entry_swing_support_retest_event_runner.py`.
Тест: `tests/test_visual_entry_swing_support_retest_event_runner.py`.

Контракт уточнен: работаем только с входами у low/дна. Сделки не тянем, TP/SL не подбираем, прибыль после входа не используется как условие. Вход LONG ставится на `open` следующей свечи после закрытой signal-свечи, `slippage_bps=5`, `lookahead=NO`.

Результат:

1. `2026-05-13`: лучший `SSRE02_TREND_DIP_FIRST_LOW_ENTRY`, `1/9` hits, `29` false, `30` entries.
2. `2026-05-14`: лучший `SSRE01_SUPPORT_RETEST_FIRST_LOW_ENTRY`, `1/17` hits, `26` false, `27` entries.

Вывод: V1 режет шум относительно `RBKD V0`, но все еще не готов. Главная проблема: "первый вход в зоне" часто срабатывает раньше пользовательского главного low. Следующий шаг: `SIGNIFICANT_LOW_SELECTOR_V1`, который должен выбирать именно значимую signal-low свечу, а не любой ранний похожий микролой. ML/export/promotion запрещены.

Проверки: `py_compile PASS`; `tests.test_visual_entry_swing_support_retest_event_runner` `1/1 OK`; совместные visual-entry tests `4/4 OK`; `text_guard PASS`, `reports/qa_gate/recovery_r5_text_guard_20260629T092347Z.json`; финальный process-check пустой.
## Visual Entry Fresh Strategy Overlay 2026-06-29
Статус: `DEV_FRESH_OVERLAY_DONE_ENTRY_ONLY_NO_CALIBRATION_NO_ML`.

Аудит: `reports/final_review/visual_entry_v3/fresh_strategy_overlay/visual_entry_fresh_strategy_overlay_audit_20260629T113100Z_RU.md`.

Код: `src/mlbotnav/visual_entry_strategy_fresh_overlay.py`.

Сделан свежий чистый overlay-стенд: старые размеченные PNG не используются как основа, график заново рендерится из `source_csv`, поверх накладываются ручные low-входы и 4 стратегии: `S01_SUPPORT_RETEST_LOW`, `S02_TREND_DIP_LOW`, `S03_DEEP_KNIFE_LOW`, `S04_HOT_CONTINUATION_LOW`.

Контракт: entry-only, без TP/SL, без MFE/MAE, без future return, без ML, без cooldown, без калибровки стратегии. Вход считается на `open` следующей свечи после закрытой signal-low свечи.

Решение: общий combined overlay все еще плотный, поэтому рабочий визуальный формат - отдельные PNG по стратегиям. Дефолты не кандидат: `2026-05-13` combined `1/9` hits и `283` false; `2026-05-14` combined `2/17` hits и `263` false. Следующий шаг - смотреть отдельные PNG глазами и калибровать только визуально живые стратегии.
## Visual Entry User Red Arrows V2 Fixed 2026-06-29
Статус: `HOLDOUT_DAY_USER_RED_ARROWS_V2_FIXED_AUTO_DETECTED_NEEDS_VISUAL_CONFIRM`.

Сохранен новый пользовательский скрин с красными стрелками для `SOLUSDT 1m 2026-05-14`.

Артефакты:

1. source image: `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_markup_user_red_arrows_SOLUSDT_1m_2026-05-14_HOLDOUT_DAY_v2.png`;
2. manual entries: `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries.json`;
3. verification PNG: `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries_v2_fixed_signal_entry_verify_20260629T115000Z.png`;
4. audit: `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries_audit_20260629T114500Z_RU.md`.

## Visual Entry Significant Low Selector V1 2026-06-29
Статус: `DEV_SIGNIFICANT_LOW_SELECTOR_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Аудит: `reports/final_review/visual_entry_v3/significant_low_selector/visual_entry_significant_low_selector_audit_20260629T125000Z_RU.md`.

Код: `src/mlbotnav/visual_entry_significant_low_selector_runner.py`.
Тест: `tests/test_visual_entry_significant_low_selector_runner.py`.

Проверка выполнена на пользовательском эталоне `SOLUSDT 1m 2026-05-14`, `17` low-входов. Контракт соблюден: signal-свеча закрыта, вход LONG на `open` следующей свечи, `slippage_bps=5`, `lookahead=NO`, сделки не тянутся, TP/SL/MFE/MAE/future return не используются, cooldown-сетки `30/45/60/90` не используются.

Baseline fresh default4: `3/17` hits, `260` false, `265` entries.

Лучшие слои `SIGNIFICANT_LOW_SELECTOR_V1`:

1. `SLS06_HOT_RECLAIM_STRICT_FALSE_CONTROL`: `5/17` hits, `71` false, `77` entries, f1 `0.1064`;
2. `SLS05_DEEP_CAPITULATION_STRICT_FALSE_CONTROL`: `2/17` hits, `20` false, `22` entries, f1 `0.1026`;
3. `SLS11_COMBINED_BALANCED_FALSE_CONTROL`: `9/17` hits, `174` false, `185` entries;
4. `SLS10_COMBINED_SIGNIFICANT_LOW`: `13/17` hits, `463` false, `492` entries.

Главный PNG:

`reports/final_review/visual_entry_v3/significant_low_selector/visual_entry_family_overlay_2026-05-14_sls_v1_01_sls06_hot_reclaim_strict_false_control_20260629T124723Z.png`

Вывод: V1 полезен как карта признаков, но не кандидат. В ML ничего не передавать. Следующий слой: `LOW_CLUSTER_RANKER_V2`, который должен выбирать один главный signal-low внутри активной зоны по past-only признакам, а не брать все похожие свечи и не маскировать мусор cooldown-ом.

## Visual Entry Low Cluster Ranker V2 2026-06-29
Статус: `DEV_LOW_CLUSTER_RANKER_V2_ENTRY_ONLY_DONE_REDUCED_FALSE_LOW_RECALL_NO_ML`.

Аудит: `reports/final_review/visual_entry_v3/low_cluster_ranker/visual_entry_low_cluster_ranker_audit_20260629T133000Z_RU.md`.

Код: `src/mlbotnav/visual_entry_low_cluster_ranker_runner.py`.
Тест: `tests/test_visual_entry_low_cluster_ranker_runner.py`.

Проверка выполнена на `17` пользовательских low-входах `SOLUSDT 1m 2026-05-14`. V2 берет low-кандидаты, группирует их в кластеры и выбирает одного победителя внутри кластера. Это не cooldown-сетка `30/45/60/90`; сделки, TP/SL, MFE/MAE и future return не используются.

Итог:

1. `LCR04_LATE_LOW_WITH_RECLAIM_CLUSTER`: `3/17` hits, `10` false, `13` entries, f1 `0.2000`;
2. `LCR07_ULTRA_CLEAN_CLUSTER`: `2/17` hits, `4` false, `6` entries;
3. `LCR06_STRICT_HOT_DEEP_RECALL_CLUSTER`: `7/17` hits, `64` false, `71` entries.

Вывод: V2 резко режет false относительно V1, но recall остается низким. Это не кандидат и не ML-export. Следующий шаг - разделить оставшиеся miss на режимы `DEEP_CAPITULATION`, `HOT_RECLAIM_SUPPORT`, `TREND_DIP_CONTINUATION`, `STRUCTURE_BOS_FIBO_VOLUME` и строить отдельные PNG/метрики по каждому режиму.

После самопроверки снято `17` manual low-входов: один тонкий фрагмент красной линии был ошибочно распознан как отдельная стрелка и удален. Статус не финальный: разметка auto-detected со сжатого скрина, требуется визуальное подтверждение. До подтверждения не передавать в ML и не считать финальной калибровочной базой.
## Visual Entry Regime Split Ranker V1 2026-06-29
Current status: `DEV_REGIME_SPLIT_RANKER_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Добавлен режимный диагностический слой: `src/mlbotnav/visual_entry_regime_split_ranker_runner.py`.

Тест: `tests/test_visual_entry_regime_split_ranker_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/regime_split_ranker/visual_entry_regime_split_ranker_audit_20260629T134600Z_RU.md`.

Отчет: `reports/final_review/visual_entry_v3/regime_split_ranker/visual_entry_regime_split_ranker_v1_20260514_HOLDOUT_DAY_RU.md`.

PNG top: `reports/final_review/visual_entry_v3/regime_split_ranker/visual_entry_family_overlay_2026-05-14_regime_split_v1_01_rsr07_structure_bos_fibo_volume_cluster_20260629T134448Z.png`.

Контракт: entry-only, signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, `slippage_bps=5`, сделки/TP/SL/MFE/MAE/future return не используются, ML-export запрещен.

Важно: V1 использует online-style выбор `first_qualified_no_future_rewrite`; будущий более сильный low не переписывает уже выбранный вход. Это честнее для будущей автоматизации, но шумнее, чем offline cluster-winner.

Результат:
1. `DEEP_CAPITULATION`: лучший `RSR02`, `2/17`, `12` false, `14` entries.
2. `HOT_RECLAIM_SUPPORT`: лучший `RSR03`, `6/17`, `87` false, `93` entries.
3. `TREND_DIP_CONTINUATION`: лучший `RSR05`, `7/17`, `95` false, `102` entries.
4. `STRUCTURE_BOS_FIBO_VOLUME`: лучший `RSR07`, `7/17`, `84` false, `91` entries.

Вывод: режимное разделение подтвердило, что пользовательские low-входы смешивают разные рыночные режимы. Но V1 пока не кандидат: structural/trend/hot ловят больше целей, но дают слишком много false; deep чище, но ловит мало. В ML ничего не передавать.

Следующий шаг: `REGIME_FALSE_SUPPRESSION_V2` отдельно по шумным режимам, чтобы сохранять найденные попадания и резать false без сделок и без ML.

## Visual Entry Regime False Suppression V2 2026-06-29
Статус: `DEV_REGIME_FALSE_SUPPRESSION_V2_ENTRY_ONLY_DONE_STILL_TOO_NOISY_NO_ML`.

Добавлен слой подавления ложных сигналов по режимам: `src/mlbotnav/visual_entry_regime_false_suppression_runner.py`.

Тест: `tests/test_visual_entry_regime_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_regime_false_suppression_audit_20260629T135843Z_RU.md`.

Отчет: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_regime_false_suppression_v2_20260514_HOLDOUT_DAY_RU.md`.

PNG top: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_family_overlay_2026-05-14_regime_false_suppression_v2_01_fsv21_union_strict_false_control_20260629T135626Z.png`.

Контракт: entry-only, signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, `slippage_bps=5`, сделки/TP/SL/MFE/MAE/future return не используются, ML-export запрещен. `cooldown 30/45/60/90` не используется.

Результат:
1. `FSV21_UNION_STRICT_FALSE_CONTROL`: `7/17` hits, `41` false, `48` entries.
2. `FSV05_TREND_DIP_EMA_RECLAIM`: `6/17` hits, `40` false, `46` entries.
3. `FSV02_DEEP_CAPITULATION_SOFT_NOWICK`: `2/17` hits, `4` false, `6` entries.
4. `FSV03_HOT_SUPPORT_STRONG_RECLAIM`: `4/17` hits, `28` false, `32` entries.

Вывод: V2 подтвердил, что suppress-фильтры режут шум, но один режимный фильтр не решает задачу. Deep уже относительно чистый, но покрывает только явные капитуляции; trend/hot/structure все еще дают много ложных входов в боковике. В ML ничего не передавать.

Следующий шаг: `ONLINE_LOW_EVENT_QUALITY_V3` - состояние low/support-события, возраст события, порядок кандидата внутри события, расстояние до event-low, откат от недавнего high и suppress для горячих верхних полок. Только признаки signal-свечи и прошлого контекста.

## Visual Entry Online Low Event Quality V3 2026-06-29
Статус: `DEV_ONLINE_LOW_EVENT_QUALITY_V3_ENTRY_ONLY_DONE_CLEANER_LOW_RECALL_NO_ML`.

Добавлен event-quality слой: `src/mlbotnav/visual_entry_online_low_event_quality_runner.py`.

Тест: `tests/test_visual_entry_online_low_event_quality_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_online_low_event_quality_audit_20260629T141715Z_RU.md`.

Отчет: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_online_low_event_quality_v3_20260514_HOLDOUT_DAY_RU.md`.

PNG top: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_family_overlay_2026-05-14_online_low_event_quality_v3_01_olev20_union_event_quality_balanced_20260629T141647Z.png`.

Контракт: entry-only, signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, `slippage_bps=5`, сделки/TP/SL/MFE/MAE/future return не используются, entry-candle `high/low/close/volume` не используются, ML-export запрещен. `cooldown 30/45/60/90` не используется.

Результат:
1. `OLEV20_UNION_EVENT_QUALITY_BALANCED`: `3/17` hits, `7` false, `10` entries, f1 `0.2222`.
2. `OLEV21_UNION_EVENT_QUALITY_STRICT`: `2/17` hits, `5` false, `7` entries.
3. `OLEV03_TREND_PULLBACK_EVENT_FILTERED`: `1/17` hits, `1` false, `2` entries.

Вывод: V3 резко снизил шум относительно V2 (`41` false -> `7` false) и немного поднял F1, но recall низкий. Это не кандидат и не ML-export.

Следующий шаг: `DEEP_RECOVERY_AND_HOT_RECALL_V4` - отдельные recovery-кирпичи для deep и hot/trend входов, не расширяя чистый `OLEV20`.

## Visual Entry Deep Recovery And Hot Recall V4 2026-06-29
Статус: `DEV_DEEP_RECOVERY_AND_HOT_RECALL_V4_ENTRY_ONLY_DONE_BETTER_BALANCE_NO_ML`.

Добавлен V4 слой: `src/mlbotnav/visual_entry_deep_recovery_hot_recall_runner.py`.

Тест: `tests/test_visual_entry_deep_recovery_hot_recall_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_deep_recovery_hot_recall_audit_20260629T144050Z_RU.md`.

Отчет: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_deep_recovery_hot_recall_v4_20260514_HOLDOUT_DAY_RU.md`.

PNG top: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_family_overlay_2026-05-14_deep_recovery_hot_recall_v4_01_drhr20_olev20_plus_deep_recovery_20260629T144015Z.png`.

Контракт: entry-only, signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, `slippage_bps=5`, сделки/TP/SL/MFE/MAE/future return не используются, entry-candle `high/low/close/volume` не используются, ML-export запрещен. `cooldown 30/45/60/90` не используется.

Результат:
1. `DRHR20_OLEV20_PLUS_DEEP_RECOVERY`: `5/17` hits, `13` false, `18` entries, f1 `0.2857`.
2. `DRHR21_FULL_DIAGNOSTIC_WITH_HOT_TREND`: `8/17` hits, `43` false, `51` entries.
3. `DRHR00_BASE_OLEV20_EVENT_QUALITY`: `3/17` hits, `7` false, `10` entries.
4. `DRHR01_DEEP_RECOVERY_COLD_RECLAIM`: `3/17` hits, `8` false, `11` entries.

Вывод: V4 улучшил баланс относительно V2/V3. Основной слой `DRHR20` добрал `16:53` и `17:35`, но не кандидат для ML. Hot/trend diagnostic пока слишком шумный.

Следующий шаг: `HOT_TREND_FALSE_SUPPRESSION_V5` - взять hot/trend diagnostic как recall-source и подавить ложные серии без разлива false.

## Visual Entry Hot Trend False Suppression V5 2026-06-29
Статус: `DEV_HOT_TREND_FALSE_SUPPRESSION_V5_ENTRY_ONLY_DONE_RECALL_UP_FALSE_STILL_HIGH_NO_ML`.

Добавлен V5 слой: `src/mlbotnav/visual_entry_hot_trend_false_suppression_runner.py`.

Тест: `tests/test_visual_entry_hot_trend_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_hot_trend_false_suppression_audit_20260629T145900Z_RU.md`.

Отчет: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_hot_trend_false_suppression_v5_20260514_HOLDOUT_DAY_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_family_overlay_2026-05-14_hot_trend_false_suppression_v5_01_htfs20_union_htfs01_hot_trend_strict_false_suppression_20260629T145736Z.png`.

Чистый hot/trend PNG: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_family_overlay_2026-05-14_hot_trend_false_suppression_v5_04_htfs01_hot_trend_strict_false_suppression_20260629T145745Z.png`.

Контракт: entry-only, signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, `slippage_bps=5`, сделки/TP/SL/MFE/MAE/future return не используются, entry-candle `high/low/close/volume` не используются, ML-export запрещен. `cooldown 30/45/60/90` не используется.

Результат:
1. `HTFS20_UNION_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `9/17` hits, `14` false, `23` entries, f1 `0.4500`.
2. `HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `4/17` hits, `1` false, `5` entries, precision `0.8000`.
3. `HTFS00_BASE_DEEP_RECOVERY_V4`: `5/17` hits, `13` false, `18` entries.
4. `HTFS09_BROAD_HOT_TREND_DIAGNOSTIC`: `4/17` hits, `35` false, `39` entries.

Вывод: строгий hot/trend фильтр полезен как чистый дополнительный слой (`10:48`, `14:13`, `15:18`, `15:45`, один false `18:47`). Общий union улучшил recall с `5/17` до `9/17`, но `14` ложных входов все еще много. В ML ничего не передавать.

Следующий шаг: `BASE_FALSE_SUPPRESSION_V6` - подавить ложные входы базовой V4-части (`01:15`, `02:57`, `03:09`, `03:52`, `06:11`, `07:14`, `07:25`, `09:06`, `13:37`, `17:23`, `19:30`, `21:57`, `23:50`) и не ломать чистый `HTFS01`.

## Visual Entry Base False Suppression V6 2026-06-29
Статус: `DEV_BASE_FALSE_SUPPRESSION_V6_ENTRY_ONLY_DONE_BEST_CURRENT_ONE_DAY_NO_ML`.

Добавлен V6 слой: `src/mlbotnav/visual_entry_base_false_suppression_runner.py`.

Тест: `tests/test_visual_entry_base_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_base_false_suppression_audit_20260629T151215Z_RU.md`.

Отчет: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_base_false_suppression_v6_20260514_HOLDOUT_DAY_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_family_overlay_2026-05-14_base_false_suppression_v6_01_bfs20_union_bfs01_base_source_split_strict_false_suppression_plus_htfs01_20260629T151147Z.png`.

Контракт: entry-only, signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, `slippage_bps=5`, сделки/TP/SL/MFE/MAE/future return не используются, entry-candle `high/low/close/volume` не используются, ML-export запрещен. `cooldown 30/45/60/90` не используется.

Результат:
1. `BFS20_UNION_BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION_PLUS_HTFS01`: `9/17` hits, `1` false, `10` entries, f1 `0.6667`.
2. `BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION`: `5/17` hits, `0` false, `5` entries.
3. `BFS90_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `4/17` hits, `1` false, `5` entries.
4. `BFS00_BASE_V4_RAW`: `5/17` hits, `13` false, `18` entries.

Вывод: V6 резко очистил базовую V4-часть (`13` false -> `0` false) и оставил единственный false `18:47` из hot/trend `HTFS01`. Это лучший текущий entry-only результат на одном дне, но в ML ничего не передавать до проверки на следующих днях.

Следующий шаг: прогнать V6 без изменения параметров на `2026-05-13` validation и отдельно разобрать единственный false `18:47`.

## Visual Entry V6 Validation 2026-05-13 2026-06-29
Статус: `VALIDATION_FAIL_V6_DOES_NOT_GENERALIZE_NO_ML`.

V6 запущен на `2026-05-13` validation без изменения параметров.

Аудит: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_base_false_suppression_validation_audit_20260629T155000Z_RU.md`.

Отчет: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_base_false_suppression_v6_20260513_VALIDATION_DAY_RU.md`.

Главный PNG validation: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_family_overlay_2026-05-13_bfs_v6_03_u_bfs01_bss_s_fs_h01_20260629T154949Z.png`.

Результат:
1. `BFS20_UNION_BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION_PLUS_HTFS01`: `0/9` hits, `1` false, `1` entry.
2. `BFS90_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `0/9` hits, `1` false, `1` entry.
3. `BFS00_BASE_V4_RAW`: `0/9` hits, `17` false, `17` entries.

Вывод: V6 хорошо выглядел на `2026-05-14`, но не обобщился на `2026-05-13`. В ML ничего не передавать.

Дополнительный фикс: первый validation-запуск упал из-за слишком длинного имени PNG в Windows; исправлен только короткий label генерации PNG в `src/mlbotnav/visual_entry_base_false_suppression_runner.py`, торговые параметры не менялись.

Следующий шаг: `GENERALIZATION_V7` - разобрать missed validation-цели `00:18`, `01:08`, `03:30`, `07:45`, `08:48`, `12:54`, `16:16`, `19:44`, `22:31` и построить режимный слой, проверяемый сразу на `2026-05-13` и `2026-05-14`.
# Visual Entry Fresh Target-Led Workflow 2026-06-30

Статус: `FRESH_TARGET_LED_WORKFLOW_READY_NO_ML`.

Новый рабочий протокол зафиксирован: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_FRESH_PROCESS_TZ_RU.md`.

Решение: дальше visual-entry работа идет не от старых runner-версий и не от общего Optuna-перебора, а от пользовательских ручных целей `T01..T10` на чистом графике.

Старые V7/V8/V9/V10/V11, Optuna-паспорта и аудиты остаются архивом и источником идей, но не являются очередью задач без привязки к новой таблице целей.

Следующий практический шаг: в свежем чате выбрать один день, подготовить чистый график, подтвердить `T01..T10`, создать target-led ledger, разложить входы по типам и выбрать первый кластер из 2-4 похожих входов.

ML запрещен до отдельного `APPROVED_FOR_ML`.

## Visual Entry Fresh Target-Led Start 2026-06-30

Статус: `FRESH_TARGET_LED_DAY_SELECTED_LEDGER_READY_NO_ML`.

Выбран день чистого старта: `2026-05-14`, `SOLUSDT`, `1m`, `core`.

Создана fresh target-led утилита без Optuna и без ML-export:
`src/mlbotnav/visual_entry_fresh_target_ledger.py`.

Артефакты:
1. Чистый график без старых сигналов: `reports/final_review/visual_entry_v3/fresh_target_led/fresh_target_led_clean_chart_SOLUSDT_1m_2026-05-14_20260630T062202Z.png`.
2. Target-led ledger JSON: `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10.json`.
3. Target-led ledger RU: `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10_RU.md`.

Источник точек: `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries.json`.

T01..T10 созданы как `candidate_needs_visual_confirm`, не как lock. После визуального просмотра `T04` отклонена пользователем как неподходящая точка входа. `T07` исправлена и подтверждена пользователем: signal `2026-05-14T10:42:00Z`, LONG entry `2026-05-14T10:43:00Z`; старое автоположение `10:48 -> 10:49` не использовать. `T08` исправлена по пользовательской нарисованной метке: предполагаемый signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`, требуется короткое подтверждение. Первый кластер-кандидат теперь: `HOT_RECLAIM_SUPPORT`, точки `T07`, `T08`.

Следующий шаг: подтвердить или поправить inferred-время `T08 = 12:01`. Optuna/ML/export по-прежнему запрещены.

Рельсы работы зафиксированы отдельно: `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_RAILS_RU.md`.
## Fresh Target-Led M06 Confirmed Next M07 2026-06-30

Статус: `M06_GOLD_USER_VISUAL_CONFIRMED_NEXT_M07_NO_ML`.

`M06` подтверждена пользователем в сдвинутой версии: signal `2026-05-14T14:07:00Z`, LONG entry `2026-05-14T14:08:00Z`.

Следующий показанный zoom-кандидат: `M07`, предполагаемый signal `2026-05-14T15:11:00Z`, LONG entry `2026-05-14T15:12:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M07_user_marked_order_zoom_signal_1511_entry_1512.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M07_user_marked_order_full_day_signal_1511_entry_1512.png`.

`M07` пока `needs_zoom_confirm`. Optuna/ML/export запрещены.

## Fresh Target-Led Extra Inserts Confirmed 2026-06-30

Статус: `M04A_M04B_GOLD_USER_VISUAL_CONFIRMED_NO_ML`.

Пользователь подтвердил обе вставки между `M04` и `M05`:
1. `M04A`: signal `2026-05-14T10:42:00Z`, LONG entry `2026-05-14T10:43:00Z`;
2. `M04B`: signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`.

Следующий практический шаг: вернуться к `M05`, которая уже сдвинута на `signal 13:35 -> LONG entry 13:36` и пока имеет статус `shifted_left_needs_final_confirm`.

## Fresh Target-Led Extra Inserts 2026-06-30

Статус: `M04A_M04B_INSERTED_NEEDS_ZOOM_CONFIRM_NO_ML`.

Пользователь добавил две зоны между `M04` и `M05` по full-day скрину. Они вставлены без переименования существующих точек:
1. `M04A`: signal `2026-05-14T10:42:00Z`, LONG entry `2026-05-14T10:43:00Z`;
2. `M04B`: signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M04A_inserted_zoom_signal_1042_entry_1043.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M04B_inserted_zoom_signal_1200_entry_1201.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M04A_M04B_inserted_full_day_between_M04_M05.png`.

Обе вставки пока `inserted_needs_zoom_confirm`. `M05` остается `shifted_left_needs_final_confirm`.

## Fresh Target-Led M03 Shifted 2026-06-30

Статус: `M03_SHIFTED_LEFT_NEEDS_FINAL_CONFIRM_NO_ML`.

Пользователь попросил сдвинуть `M03` на одну свечу влево. Новое положение: signal `2026-05-14T08:05:00Z`, LONG entry `2026-05-14T08:06:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M03_user_marked_order_zoom_signal_0805_entry_0806_shift_left.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M03_user_marked_order_full_day_signal_0805_entry_0806_shift_left.png`.

`M03` пока не считать финально подтвержденной до ответа пользователя по новой картинке.

## Fresh Target-Led M01 Confirmed 2026-06-30

Статус: `M01_GOLD_USER_VISUAL_CONFIRMED_NEXT_M02_NO_ML`.

`M01` подтвержден пользователем как подходящий: signal `2026-05-14T03:23:00Z`, LONG entry `2026-05-14T03:24:00Z`.

Следующий показанный zoom-кандидат: `M02`, предполагаемый signal `2026-05-14T03:58:00Z`, LONG entry `2026-05-14T03:59:00Z`.

PNG: `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M02_user_marked_order_zoom_signal_0358_entry_0359.png`.

Граница: это ручное visual-confirm, не стратегия и не target-lock. Optuna/ML/export запрещены.

## Fresh Target-Led User Marked Order 2026-06-30

Статус: `USER_MARKED_DEVELOPMENT_ORDER_NEEDS_ZOOM_CONFIRM_NO_ML`.

Пользователь уточнил, что обязательных 10 точек нет. Новый рабочий порядок берется из его красных прямоугольников на full-day графике `SOLUSDT 1m 2026-05-14`: двигаться слева направо по `M01..M15`.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M01_user_marked_order_zoom_signal_0323_entry_0324.png`.

`T08` подтверждена пользователем после zoom-разметки: signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`, статус в ledger обновлен на `gold_user_visual_confirmed`.

Следующий практический шаг: показать пользователю `M01` zoom-кандидат `signal 03:23 -> LONG entry 03:24` и получить решение `подходит / не подходит / сдвинуть`. Это еще не target-lock и не стратегия.

Граница: Optuna, ML/export/promotion запрещены. Старые V7/V8/V9/V10/V11 не продолжать как очередь задач.
## Fresh Target-Led M06A Inserted 2026-06-30

Статус: `M06A_GOLD_USER_VISUAL_CONFIRMED_NEXT_M08_NO_ML`.

Пользователь указал пропущенную зону между `M06` и `M07` на full-day скрине. Точка добавлена без переименования существующих целей как `M06A`.

Первичный кандидат был signal `2026-05-14T14:35:00Z`, LONG entry `2026-05-14T14:36:00Z`. По просьбе пользователя `M06A` сдвинута на две свечи влево: signal `2026-05-14T14:33:00Z`, LONG entry `2026-05-14T14:34:00Z`.

Пользователь подтвердил сдвинутую версию `M06A`: signal `2026-05-14T14:33:00Z`, LONG entry `2026-05-14T14:34:00Z`. Следующий кандидат по порядку: `M08`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M06A_inserted_zoom_signal_1433_entry_1434_shift_left_2.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M06A_inserted_full_day_between_M06_M07_signal_1433_entry_1434_shift_left_2.png`.

Ledger обновлен: `reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

Граница: `M06A` подтверждена как ручная gold-точка, но это пока не target-lock и не стратегия. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M08 Preview 2026-06-30

Статус: `M08_SHOWN_NEEDS_USER_VISUAL_CONFIRM_NO_ML`.

После подтвержденной вставки `M06A` следующий кандидат по ручному порядку вынесен пользователю на визуальную проверку:
`M08`: signal `2026-05-14T15:39:00Z`, LONG entry `2026-05-14T15:40:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M08_user_marked_order_zoom_signal_1539_entry_1540.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M08_user_marked_order_full_day_signal_1539_entry_1540.png`.

Граница: `M08` пока не подтверждена и не является target-lock. Нужно решение пользователя: подходит / сдвинуть / пропустить. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M08 Shifted 2026-06-30

Статус: `M08_SHIFTED_LEFT_NEEDS_FINAL_CONFIRM_NO_ML`.

Пользователь попросил сдвинуть `M08` на одну свечу влево. Новое положение:
signal `2026-05-14T15:38:00Z`, LONG entry `2026-05-14T15:39:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M08_user_marked_order_zoom_signal_1538_entry_1539_shift_left.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M08_user_marked_order_full_day_signal_1538_entry_1539_shift_left.png`.

Граница: `M08` еще не подтверждена как gold-точка. Нужно короткое решение пользователя по новой версии. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M08 Confirmed 2026-06-30

Статус: `M08_GOLD_USER_VISUAL_CONFIRMED_NEXT_M09_NO_ML`.

Пользователь подтвердил сдвинутую версию `M08`: signal `2026-05-14T15:38:00Z`, LONG entry `2026-05-14T15:39:00Z`.

Ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

Следующий кандидат по ручному порядку: `M09`, текущая ledger-гипотеза signal `2026-05-14T17:25:00Z`, LONG entry `2026-05-14T17:26:00Z`. Нужен отдельный visual-confirm; Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M09 Preview 2026-06-30

Статус: `M09_SHOWN_NEEDS_USER_VISUAL_CONFIRM_NO_ML`.

Следующий кандидат по ручному порядку вынесен пользователю на визуальную проверку:
`M09`: signal `2026-05-14T17:25:00Z`, LONG entry `2026-05-14T17:26:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M09_user_marked_order_zoom_signal_1725_entry_1726.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M09_user_marked_order_full_day_signal_1725_entry_1726.png`.

Граница: `M09` пока не подтверждена как gold-точка и не является target-lock. Нужно решение пользователя: подходит / сдвинуть / пропустить. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M08A Inserted 2026-06-30

Статус: `M08A_INSERTED_NEEDS_USER_VISUAL_CONFIRM_NO_ML`.

Пользователь указал пропущенную зону между подтвержденной `M08` и кандидатом `M09`. Точка вставлена без переименования существующих целей как `M08A`.

Первичная версия для visual-confirm:
`M08A`: signal `2026-05-14T16:52:00Z`, LONG entry `2026-05-14T16:53:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M08A_inserted_zoom_signal_1652_entry_1653.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M08A_inserted_full_day_before_M09_signal_1652_entry_1653.png`.

Граница: `M08A` пока не подтверждена как gold-точка и не является target-lock. Нужно решение пользователя: подходит / сдвинуть / пропустить. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M08A M09 Confirmed 2026-06-30

Статус: `M08A_M09_GOLD_USER_VISUAL_CONFIRMED_NEXT_M10_NO_ML`.

Пользователь подтвердил обе последние показанные точки:
1. `M08A`: signal `2026-05-14T16:52:00Z`, LONG entry `2026-05-14T16:53:00Z`;
2. `M09`: signal `2026-05-14T17:25:00Z`, LONG entry `2026-05-14T17:26:00Z`.

Ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

Следующий кандидат по ручному порядку: `M10`, текущая ledger-гипотеза signal `2026-05-14T18:01:00Z`, LONG entry `2026-05-14T18:02:00Z`. Нужен отдельный visual-confirm; Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M10 Preview 2026-06-30

Статус: `M10_SHOWN_NEEDS_USER_VISUAL_CONFIRM_NO_ML`.

Следующий кандидат по ручному порядку вынесен пользователю на визуальную проверку:
`M10`: signal `2026-05-14T18:01:00Z`, LONG entry `2026-05-14T18:02:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M10_user_marked_order_zoom_signal_1801_entry_1802.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M10_user_marked_order_full_day_signal_1801_entry_1802.png`.

Граница: `M10` пока не подтверждена как gold-точка и не является target-lock. Нужно решение пользователя: подходит / сдвинуть / пропустить. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M10 Confirmed 2026-06-30

Статус: `M10_GOLD_USER_VISUAL_CONFIRMED_NEXT_M11_NO_ML`.

Пользователь подтвердил `M10` без сдвига: signal `2026-05-14T18:01:00Z`, LONG entry `2026-05-14T18:02:00Z`.

Ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

Следующий кандидат по ручному порядку: `M11`, текущая ledger-гипотеза signal `2026-05-14T18:41:00Z`, LONG entry `2026-05-14T18:42:00Z`. Нужен отдельный visual-confirm; Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M11 Preview 2026-06-30

Статус: `M11_SHOWN_NEEDS_USER_VISUAL_CONFIRM_NO_ML`.

Следующий кандидат по ручному порядку вынесен пользователю на визуальную проверку:
`M11`: signal `2026-05-14T18:41:00Z`, LONG entry `2026-05-14T18:42:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M11_user_marked_order_zoom_signal_1841_entry_1842.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M11_user_marked_order_full_day_signal_1841_entry_1842.png`.

Граница: `M11` пока не подтверждена как gold-точка и не является target-lock. Нужно решение пользователя: подходит / сдвинуть / пропустить. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M11 Confirmed 2026-06-30

Статус: `M11_GOLD_USER_VISUAL_CONFIRMED_NEXT_M12_NO_ML`.

Пользователь подтвердил `M11` без сдвига: signal `2026-05-14T18:41:00Z`, LONG entry `2026-05-14T18:42:00Z`.

Ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

Следующий кандидат по ручному порядку: `M12`, текущая ledger-гипотеза signal `2026-05-14T20:39:00Z`, LONG entry `2026-05-14T20:40:00Z`. Нужен отдельный visual-confirm; Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M12 Preview 2026-06-30

Статус: `M12_SHOWN_NEEDS_USER_VISUAL_CONFIRM_NO_ML`.

Следующий кандидат по ручному порядку вынесен пользователю на визуальную проверку:
`M12`: signal `2026-05-14T20:39:00Z`, LONG entry `2026-05-14T20:40:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M12_user_marked_order_zoom_signal_2039_entry_2040.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M12_user_marked_order_full_day_signal_2039_entry_2040.png`.

Граница: `M12` пока не подтверждена как gold-точка и не является target-lock. Нужно решение пользователя: подходит / сдвинуть / пропустить. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M12 Confirmed 2026-06-30

Статус: `M12_GOLD_USER_VISUAL_CONFIRMED_NEXT_M13_NO_ML`.

Пользователь подтвердил `M12` без сдвига: signal `2026-05-14T20:39:00Z`, LONG entry `2026-05-14T20:40:00Z`.

Ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

Следующий кандидат по ручному порядку: `M13`, текущая ledger-гипотеза signal `2026-05-14T21:18:00Z`, LONG entry `2026-05-14T21:19:00Z`. Нужен отдельный visual-confirm; Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M13 Preview 2026-06-30

Статус: `M13_SHOWN_NEEDS_USER_VISUAL_CONFIRM_NO_ML`.

Следующий кандидат по ручному порядку вынесен пользователю на визуальную проверку:
`M13`: signal `2026-05-14T21:18:00Z`, LONG entry `2026-05-14T21:19:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M13_user_marked_order_zoom_signal_2118_entry_2119.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M13_user_marked_order_full_day_signal_2118_entry_2119.png`.

Граница: `M13` пока не подтверждена как gold-точка и не является target-lock. Нужно решение пользователя: подходит / сдвинуть / пропустить. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M13 Confirmed 2026-06-30

Статус: `M13_GOLD_USER_VISUAL_CONFIRMED_NEXT_M14_NO_ML`.

Пользователь подтвердил `M13` без сдвига: signal `2026-05-14T21:18:00Z`, LONG entry `2026-05-14T21:19:00Z`.

Ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

Следующий кандидат по ручному порядку: `M14`, текущая ledger-гипотеза signal `2026-05-14T21:58:00Z`, LONG entry `2026-05-14T21:59:00Z`. Нужен отдельный visual-confirm; Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M14 Preview 2026-06-30

Статус: `M14_SHOWN_NEEDS_USER_VISUAL_CONFIRM_NO_ML`.

Следующий кандидат по ручному порядку вынесен пользователю на визуальную проверку:
`M14`: signal `2026-05-14T21:58:00Z`, LONG entry `2026-05-14T21:59:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M14_user_marked_order_zoom_signal_2158_entry_2159.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M14_user_marked_order_full_day_signal_2158_entry_2159.png`.

Граница: `M14` пока не подтверждена как gold-точка и не является target-lock. Нужно решение пользователя: подходит / сдвинуть / пропустить. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M14 Shifted By User Arrow 2026-06-30

Статус: `M14_SHIFTED_RIGHT_NEEDS_FINAL_CONFIRM_NO_ML`.

Пользователь стрелкой указал более позднюю зону для `M14`. Новая рабочая версия:
signal `2026-05-14T22:02:00Z`, LONG entry `2026-05-14T22:03:00Z`.

Предыдущая версия `M14` была signal `2026-05-14T21:58:00Z`, LONG entry `2026-05-14T21:59:00Z`; ее не считать подтвержденной.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M14_user_marked_order_zoom_signal_2202_entry_2203_shift_right_user_arrow.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M14_user_marked_order_full_day_signal_2202_entry_2203_shift_right_user_arrow.png`.

Граница: `M14` еще не подтверждена как gold-точка. Нужно короткое решение пользователя по новой версии. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M14 Confirmed 2026-06-30

Статус: `M14_GOLD_USER_VISUAL_CONFIRMED_NEXT_M15_NO_ML`.

Пользователь подтвердил сдвинутую версию `M14`: signal `2026-05-14T22:02:00Z`, LONG entry `2026-05-14T22:03:00Z`.

Ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

Следующий кандидат по ручному порядку: `M15`, текущая ledger-гипотеза signal `2026-05-14T22:18:00Z`, LONG entry `2026-05-14T22:19:00Z`. Нужен отдельный visual-confirm; Optuna/ML/export/promotion запрещены.

## Fresh Target-Led M15 Preview 2026-06-30

Статус: `M15_SHOWN_NEEDS_USER_VISUAL_CONFIRM_NO_ML`.

Следующий кандидат по ручному порядку вынесен пользователю на визуальную проверку:
`M15`: signal `2026-05-14T22:18:00Z`, LONG entry `2026-05-14T22:19:00Z`.

PNG:
1. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M15_user_marked_order_zoom_signal_2218_entry_2219.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M15_user_marked_order_full_day_signal_2218_entry_2219.png`.

Граница: `M15` пока не подтверждена как gold-точка и не является target-lock. Нужно решение пользователя: подходит / сдвинуть / пропустить. Optuna/ML/export/promotion запрещены.
## Fresh Target-Led M15 Confirmed 2026-06-30

Статус: `M15_GOLD_USER_VISUAL_CONFIRMED_VISUAL_PASS_COMPLETE_NO_ML`.

Пользователь подтвердил `M15` без сдвига: signal `2026-05-14T22:18:00Z`, LONG entry `2026-05-14T22:19:00Z`.

Ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

Ручной visual-confirm по текущему набору `M01..M15` с вставками `M04A`, `M04B`, `M06A`, `M08A` завершен. Следующий шаг: собрать/проверить `target_ledger`, разложить gold-точки по типам, выбрать первый кластер 2-4 похожих входов. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led Renumbered M01-M19 2026-06-30

Статус: `USER_MARKED_DEVELOPMENT_ORDER_M01_M19_RENUMBERED_GOLD_CONFIRMED_NO_ML`.

По просьбе пользователя убраны повторяющиеся и буквенные номера в ручном порядке. Рабочие точки теперь идут единым рядом `M01..M19`; старые идентификаторы сохранены только как `legacy_order_id` и в таблице перенумерации.

Ledger обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`.

RU-версия обновлена:
`reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514_RU.md`.

Следующий шаг без Optuna/ML: собрать/проверить `target_ledger`, разложить `M01..M19` по визуальным типам и выбрать первый кластер 2-4 похожих входов.

## Fresh Target-Led M01-M19 Target Ledger 2026-06-30

Статус: `TARGET_LEDGER_M01_M19_TYPED_FIRST_CLUSTER_C01_READY_NO_ML`.

Создан новый target-led ledger по рабочему порядку `M01..M19`, без старых T01..T10 как рабочей очереди. Точки разложены по первичным визуальным типам.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19_RU.md`.

Первый кластер-кандидат: `C01 HOT_RECLAIM_SUPPORT`, точки `M05`, `M06` (legacy `M04A`, `M04B`). Следующий шаг: визуально подтвердить кластер перед паспортом. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led Reference Visual Pinned 2026-06-30

Статус: `REFERENCE_VISUAL_PINNED_NO_ML`.

Закреплен эталонный full-day скриншот с пользовательскими красными зонами для текущего прохода `M01..M19`:
`reports/final_review/visual_entry_v3/fresh_target_led/reference_visual/REFERENCE_M01_M19_USER_MARKED_FULL_DAY_SOLUSDT_1m_2026-05-14.png`.

Manifest:
`reports/final_review/visual_entry_v3/fresh_target_led/reference_visual/REFERENCE_M01_M19_USER_MARKED_FULL_DAY_SOLUSDT_1m_2026-05-14.json`.

Правило: будущие паспорта и проверки должны ссылаться на этот эталон и на `target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json`; потеря хорошей ручной точки без явной замены считается регрессией. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led Passport Draft C01 2026-06-30

Статус: `DRAFT_NO_ML_NO_OPTUNA_NEEDS_USER_CLUSTER_CONFIRM`.

Создан первый подписанный паспорт-контракт: `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0`.

Файлы:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/passport_VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/passport_VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0_RU.md`.

Кластер: `C01 HOT_RECLAIM_SUPPORT`, targets `M05`, `M06`; `M12` только наблюдать, не смешивать в V0. Optuna/ML/export/promotion запрещены. Следующий шаг: показать/подтвердить пользователем C01 как первый паспортный тип.

## Fresh Target-Led Confirmed Entries Reference Fixed 2026-06-30

Статус: `REFERENCE_VISUAL_M01_M19_CONFIRMED_ENTRIES_PINNED_NO_ML`.

Исправление по замечанию пользователя: главным эталоном теперь является не исходный скрин с красными зонами, а full-day график с уже выставленными и подтвержденными 19 входами `M01..M19`:
`reports/final_review/visual_entry_v3/fresh_target_led/reference_visual/REFERENCE_M01_M19_CONFIRMED_ENTRIES_FULL_DAY_SOLUSDT_1m_2026-05-14.png`.

Manifest:
`reports/final_review/visual_entry_v3/fresh_target_led/reference_visual/REFERENCE_M01_M19_CONFIRMED_ENTRIES_FULL_DAY_SOLUSDT_1m_2026-05-14.json`.

SHA256: `11edef9fed318650b2c350c565807cc5f9761c93e815015b354f0cb9fbc2bd64`.

Скрин с красными пользовательскими зонами остается вспомогательным исходником, но не главным эталоном для паспортов. Паспорт `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0` обновлен на confirmed-entries эталон. Optuna/ML/export/promotion запрещены.

## Fresh Target-Led Rails Correction After C02 Good/Bad Audit 2026-06-30

Статус: `C02_RAILS_CORRECTED_SPLIT_CURRENT_NO_ML_NO_OPTUNA`.

Поправка по замечанию пользователя: после ручной разметки C02 был сделан `6.3 Good/Bad audit`, но этот подпункт не был заранее вынесен в рабочую лестницу. Жесткие запреты не нарушались: scorer, target-lock, multi-day, Optuna и ML не запускались.

Актуальная лестница:

1. `6.1` ручная GOOD/BAD разметка C02: `done`;
2. `6.2` scorer до ручной разметки не делался: `rule_satisfied`;
3. `6.3` good/bad audit C02: `done`;
4. `7.1` entry-only scorer C02: `blocked_before_split`;
5. `8.3` split/router decision: `current_next`.

Рабочий план обновлен:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_BENCH_V0_STEP_PLAN_20260630_RU.md`.

Следующий подпункт только после явного продолжения: `8.3 C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`.

## Fresh Target-Led C02 Split/Router Decision 2026-06-30

Статус: `C02_SPLIT_ROUTER_DECISION_V0_COMPLETE_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт рельсов `8.3` завершен. C02 не переводится в один общий scorer. Решение:

- ядро `C02A_TRUE_DEEP_CAPITULATION_CORE`: `C02E03/M01`, `C02E04/M02`, `C02E10/M08`;
- router `SUPPORT_RETEST_LOW`: `C02E05`, `C02E06`, `C02E07`;
- router `HOT_RECLAIM_SUPPORT`: `C02E08`, `C02E11`;
- router `SWING_LOW_RECLAIM`: `C02E09`, `C02E12`;
- negative controls: `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.png`.

Рабочая лестница и C02 passport обновлены. Следующий подпункт: `8.3.1_DESIGN_C02A_TRUE_DEEP_CAPITULATION_CORE_RULES_FROM_PAST_ONLY_FEATURES_NO_SCORER_YET`.

Запрещено до завершения `8.3.1`: scorer, target-lock, multi-day, Optuna, ML/export/promotion.

## Fresh Target-Led C02 Price And Visual Clarity Fix 2026-06-30

Статус: `C02_SPLIT_ROUTER_PRICE_CLARITY_FIX_V0_COMPLETE_NO_SCORER_NO_ML_NO_OPTUNA`.

Поправка по замечанию пользователя: первый split/router PNG был слишком обзорным, при увеличении размывался и не показывал цену входа. Такой скрин нельзя считать рабочим визуалом для глаз.

Цена входа не потеряна: для `M01..M19` она уже была записана в `target_ledger` и `M01_M19_EXECUTION_PRICES_RU.md`. Для `C02E01..C02E16` создана отдельная таблица цен.

Новые рабочие артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_ENTRY_PRICE_TABLE_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_ZOOM_SHEET_V0_20260630.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_ZOOM_SHEET_V0_20260630.svg`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_FULL_DAY_HIRES_V0_20260630.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_FULL_DAY_HIRES_V0_20260630.svg`.

Правило: `entry_open_price` и `entry + 5 bps` нужны только для исполнения, учета и визуального контроля. Они не являются сигналом и запрещены как scorer/Optuna/ML-признаки выбора входа.

Следующий подпункт остается: `8.3.1_DESIGN_C02A_TRUE_DEEP_CAPITULATION_CORE_RULES_FROM_PAST_ONLY_FEATURES_NO_SCORER_YET`.

## Fresh Target-Led C02 RU Encoding Fix 2026-06-30

Статус: `C02_RU_MARKDOWN_ENCODING_FIXED_NO_SCORER_NO_ML_NO_OPTUNA`.

Исправлены битые знаки вопроса вместо русского текста в новых RU-отчетах C02:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_ENTRY_PRICE_TABLE_V0_20260630_RU.md`.

Проверка по C02 split/router и текущим статусным файлам не нашла оставшихся битых строк.

## Fresh Target-Led C02A Rules Draft 2026-06-30

Статус: `C02A_TRUE_DEEP_CAPITULATION_RULES_V0_DRAFT_WAIT_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт рельсов `8.3.1` выполнен без scorer. Спроектирован draft-контракт C02A для чистого `DEEP_CAPITULATION_LOW`.

Цель C02A:

- pass: `C02E03/M01`, `C02E04/M02`, `C02E10/M08`;
- reject negative controls: `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`;
- route out: остальные хорошие C02 events, потому что они относятся к другим типам.

Draft rules V0:

- base gates: `event_raw_count <= 4`, `body_pct <= 0.10`, `vol_to_prior20 <= 6.0`, `close_vs_ema20_pct <= -0.20`, `range_pos_60 <= 0.14`;
- mode A: `ret_120m_pct <= -1.10 AND range_pos_60 <= 0.13`;
- mode B: `range_pos_60 <= 0.04 AND ret_60m_pct <= -0.55 AND close_vs_ema20_pct <= -0.30`.

Seed-аудит на `C02E01..C02E16`: проходят только `C02E03`, `C02E04`, `C02E10`; нарушений нет.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_VISUAL_V0_20260630.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_VISUAL_V0_20260630.svg`.

Следующий подпункт: `8.3.1_USER_VISUAL_REVIEW_C02A_RULES_V0_BEFORE_SCORER`.

До пользовательского visual review запрещены scorer, target-lock, multi-day, Optuna и ML/export/promotion.
## Fresh Target-Led Dataset Base V1 After Unlabeled15 Feedback 2026-07-01

Статус: `TARGET_LED_DATASET_BASE_V1_AFTER_UNLABELED15_FEEDBACK_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA`.

Пользователь проверил график `15 unlabeled review candidates` по `SOLUSDT 1m 2026-05-14` и уточнил разметку:

- `LA018`, `LA020` — нормальные входы, приняты как дополнительные positive/gold для будущего supervised-dataset;
- остальные `13` текущих авто-точек из этого листа — отклонены как слабые, некорректные или мимо;
- `LA026`, `LA048`, `LA057`, `LA059`, `LA062` имеют пользовательские красные стрелки: текущая авто-точка отклонена, а новая точка по стрелке остается `arrow_shift_pending` и не добавлена как gold без отдельного zoom/time.

Итог счетчиков V1 по текущим точкам: всего `107`, positive `28`, negative `79`, unlabeled `0`. Это только база разметки, не ML/export/training/scorer/Optuna.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v1_after_unlabeled15_feedback_v1/TARGET_LED_UNLABELED15_USER_FEEDBACK_V1_20260701.csv`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v1_after_unlabeled15_feedback_v1/TARGET_LED_DATASET_BASE_V1_AFTER_UNLABELED15_FEEDBACK_20260701.csv`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v1_after_unlabeled15_feedback_v1/TARGET_LED_DATASET_BASE_V1_AFTER_UNLABELED15_FEEDBACK_20260701_RU.md`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_base_v1_after_unlabeled15_feedback_v1/TARGET_LED_UNLABELED15_USER_FEEDBACK_V1_ON_CHART_20260701.png`.

Следующий шаг по рельсам: не запускать ML. Сначала разобрать `arrow_shift_pending` только через отдельный zoom/time или перейти к аудиту блоков/фичей по уже размеченным `28/79`.
## Fresh Target-Led Dataset Quality Audit V0 2026-07-01

Статус: `TARGET_LED_DATASET_QUALITY_AUDIT_V0_READY_NO_ML_EXPORT_NO_TRAINING_NO_OPTUNA`.

По базе V1 (`28` positive / `79` negative) выполнен no-ML аудит блоков и типов. Главный вывод: простая сумма совпавших блоков не работает как сигнал входа. `safe_core_hit_count=5/6` часто шумит, поэтому правило "больше блоков = лучше вход" запрещено.

Первые кандидаты для узкого паспорта: `SUPPORT_RETEST_LOW` и `TREND_DIP_CONTINUATION`. `LOW_ANCHOR_RECLAIM` в текущем виде блокируется как самостоятельный allow (`0/16` positive). `B013_density_support`, `B020_divergence_support`, `bull_divergence_recent8` и широкие формы `B015/B017` нельзя отдавать как standalone allow.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_quality_audit_v0/TARGET_LED_DATASET_QUALITY_AUDIT_V0_20260701_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_quality_audit_v0/TARGET_LED_DATASET_QUALITY_AUDIT_V0_20260701.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/target_led_dataset_quality_audit_v0/TARGET_LED_DATASET_QUALITY_AUDIT_V0_FEATURE_BLOCKS_20260701.csv`.

Следующий пункт: собрать `V1_RULE_CANDIDATE` не для ML, а для визуального паспорта первого узкого типа.
## Fresh Target-Led ML Dataset Ladder 2026-07-01

Статус: `FRESH_TARGET_LED_ML_DATASET_LADDER_LOCKED_NO_ML_NO_OPTUNA`.

Зафиксирована лестница работы от ручной разметки к будущему ML без перепрыгивания шагов:

`docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_ML_DATASET_LADDER_RU.md`.

Главное:

- текущая база V1: `28` good, `79` bad, `0` unlabeled;
- ML/export/training/Optuna запрещены без отдельных этапов;
- следующий подпункт строго один: `2.1_SUPPORT_RETEST_LOW_REVIEW_SHEET_9_GOOD_16_BAD_NO_ML_NO_OPTUNA`;
- после review-sheet идет только draft-паспорт `SUPPORT_RETEST_LOW`, не ML.
## Fresh Target-Led SUPPORT_RETEST_LOW Review Sheet V0 2026-07-01

Статус: `SUPPORT_RETEST_LOW_REVIEW_SHEET_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Выполнен пункт лестницы `2.1_SUPPORT_RETEST_LOW_REVIEW_SHEET_9_GOOD_16_BAD_NO_ML_NO_OPTUNA`.

Собран review-sheet по `SUPPORT_RETEST_LOW`: `25` примеров, из них `9` good и `16` bad. Это визуальный разбор и feature-audit, не ML и не scorer.

Первичный вывод: голый всплеск объема, простая сумма core-блоков, `retest_near_signal`, `bos_down_now` и `choch_like_near_signal` не отделяют good от bad как standalone allow. Для draft-паспорта нужно описывать структуру low/reclaim и запрет на вход в продолжающемся проливе.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_review_sheet_v0/SUPPORT_RETEST_LOW_REVIEW_SHEET_V0_20260701_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_review_sheet_v0/SUPPORT_RETEST_LOW_REVIEW_SHEET_V0_9GOOD_16BAD_20260701.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_review_sheet_v0/SUPPORT_RETEST_LOW_REVIEW_SHEET_V0_ROWS_20260701.csv`.

Следующий шаг только после user review `норм / фиксить`: draft-паспорт `SUPPORT_RETEST_LOW`.
## Fresh Target-Led SUPPORT_RETEST_LOW Passport Draft V0 2026-07-01

Статус: `SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Выполнен пункт лестницы `3.1_DRAFT_PASSPORT_SUPPORT_RETEST_LOW_AFTER_REVIEW_SHEET_NO_SCORER_NO_ML_NO_OPTUNA`.

Создан draft-паспорт для `SUPPORT_RETEST_LOW` после подтвержденного review-sheet `9 good / 16 bad`.

Ключевые решения паспорта:

- core logic: локальный low/support + reclaim/return после продавливания + entry next open;
- reject guards: продолжающийся пролив, запоздалый вход, volume-spike как единственная причина, middle-range noise, allow по простой сумме блоков;
- RSI/MACD/ADX/Stoch, BOS/CHOCH, Fibo, density/VPOC, candle/wick — context-only/evidence, не standalone allow;
- candidate guards: `volume_ratio20 < 4.5`, `range_pos_60 0.02..0.43`, `room_to_high_60_bps >= 28`, `dist_from_low_60_bps <= 24`;
- good, которые паспорт обязан сохранить: `M03`, `M04`, `M16`, `M17`, `M18`, `M19`, `T15L02`, `T15L08`, `T15L16`.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_passport_draft_v0/SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_20260701_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_passport_draft_v0/SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_20260701.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_passport_draft_v0/SUPPORT_RETEST_LOW_PASSPORT_DRAFT_V0_CARD_20260701.png`.

Следующий шаг только после user review `норм / фиксить`: entry-only PNG/scorer seed-check по `SUPPORT_RETEST_LOW`. ML/export/training/Optuna/target-lock запрещены.
## Fresh Target-Led SUPPORT_RETEST_LOW Entry-Only Scorer V0 2026-07-02

Статус: `SUPPORT_RETEST_LOW_ENTRY_ONLY_SCORER_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_TARGET_LOCK`.

Выполнен пункт `4.1_ENTRY_ONLY_SCORER_SEED_CHECK_SUPPORT_RETEST_LOW_NO_TARGET_LOCK_NO_ML_NO_OPTUNA` после user `ок` по draft-паспорту.

Seed-check применил candidate numeric guards паспорта к `25` размеченным примерам `SUPPORT_RETEST_LOW`.

Результат:

- good kept: `9/9`;
- good missed: `0`;
- bad rejected: `8/16`;
- bad accepted / false entries: `8/16`;
- visual status: `SEED_MUST_KEEP_PASS_FALSE_ENTRIES_TOO_MANY`.

Вывод: V0 не теряет хорошие входы, но слишком грязный для lock. Следующий шаг: `V1_REJECT_GUARDS` по 8 оранжевым false-positive (`LA033`, `LA034`, `LA041`, `LA048`, `LA065`, `T15L17`, `T15L18`, `T15L20`) без потери `9` good.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_entry_only_scorer_v0/SUPPORT_RETEST_LOW_ENTRY_ONLY_SCORER_V0_20260702_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_entry_only_scorer_v0/SUPPORT_RETEST_LOW_ENTRY_ONLY_SCORER_V0_SEED_CHECK_20260702.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_entry_only_scorer_v0/SUPPORT_RETEST_LOW_ENTRY_ONLY_SCORER_V0_RESULTS_20260702.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/support_retest_low_entry_only_scorer_v0/SUPPORT_RETEST_LOW_ENTRY_ONLY_SCORER_V0_20260702.json`.

Target-lock, multi-day, Optuna и ML/export/training запрещены.

## Fresh Target-Led Outcome Low Miner V0 2026-07-02

Статус: `OUTCOME_LOW_MINER_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_SCORER`.

По предложению пользователя сделан отдельный тестовый outcome-miner, не ломающий паспортную цепочку: искать low-кандидаты causal/past-only способом, вход считать на `open` следующей свечи с `+5 bps`, а будущий ход `+1.5%` использовать только как offline-метку исхода.

Границы:

- это не ML/export/training;
- это не scorer;
- это не target-lock;
- это не Optuna;
- future `+1.5%` запрещен как признак выбора входа и используется только как outcome-label для ручного review.

Параметры V0: `SOLUSDT 1m`, дни `2026-05-14` и `2026-05-15`, target `entry_price_plus_5bps * 1.015`, окно исхода `360` минут.

Счетчики:

- `2026-05-14`: `14` кандидатов, `5` дошли до `+1.5%`, `9` не дошли;
- `2026-05-15`: `12` кандидатов, `1` дошел до `+1.5%`, `11` не дошли.

Вывод: как ускоритель поиска сильных low-кандидатов идея полезна, но порог `+1.5%` слишком строгий как единственный способ собрать все хорошие ручные входы. После user review можно сделать соседний outcome-тест `+0.8%/+1.0%` или отдельный `room/path` label, не включая ML.

Артефакты:

1. `src/mlbotnav/visual_entry_outcome_low_miner_v0.py`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_20260702_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_CANDIDATES_20260702.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260514_20260702.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260515_20260702.png`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_FULL_DAY_20260514_20260702.png`;
7. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_FULL_DAY_20260515_20260702.png`.

Следующий шаг: показать пользователю hit zoom PNG и получить `норм / фиксить / нужен тест меньшего порога`. Паспортная цепочка `SUPPORT_RETEST_LOW V1_REJECT_GUARDS` остается не отмененной, но сейчас не продолжается автоматически.

## Fresh Target-Led Outcome Low Miner 1pct Comparison 2026-07-02

Статус: `OUTCOME_LOW_MINER_V0_TARGET_1PCT_COMPARISON_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_SCORER`.

По просьбе пользователя выполнен такой же outcome-miner тест, но с target `+1.0%` вместо `+1.5%`. Логика выбора low-кандидата не менялась; изменена только offline-метка исхода.

Счетчики `+1.0%`:

- `2026-05-14`: `14` кандидатов, `7` дошли до `+1.0%`, `7` не дошли;
- `2026-05-15`: `12` кандидатов, `3` дошли до `+1.0%`, `9` не дошли.

Сравнение с `+1.5%`: порог `+1.0%` дает больше рабочих кандидатов, особенно на слабом/падающем `2026-05-15`, и выглядит полезнее для ускоренного сбора review-примеров. Это все еще не ML/export/training/scorer/target-lock.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct/OUTCOME_LOW_MINER_V0_20260702_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct/OUTCOME_LOW_MINER_V0_CANDIDATES_20260702.csv`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260514_20260702.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260515_20260702.png`.

## Fresh Target-Led Outcome Miner Correction 2026-07-02

Статус: `OUTCOME_MINER_WIDE_SWEEP_MARKED_DIAGNOSTIC_ONLY_RETURN_TO_SIGNIFICANT_LEVELS_NO_ML_NO_OPTUNA`.

После замечания пользователя перечитаны рельсы. В `FRESH_TARGET_LED_RAILS_RU.md` явно зафиксировано, что `cooldown-сетки` запрещены как замена логике входа. Поэтому широкий sweep `cooldown 5 / min_score 0` нельзя считать рабочим путем.

Коррекция:

- широкий `outcome_low_miner_v0_wide_sweep_0p8pct` остается только диагностическим артефактом, показывающим, что узкий фильтр пропускал часть зон;
- рабочий путь возвращается к ручной target-led логике: значимый локальный low/уровень, left-context, signal close, entry next open;
- outcome `+0.8%/+1.0%/+1.5%` может быть только offline-меткой для review, не сигналом и не способом выбирать вход;
- cooldown можно использовать только как техническую дедупликацию после найденного значимого уровня, но не как главный инструмент поиска.

Следующий правильный шаг: построить не перебор микролоев, а `SIGNIFICANT_LEVEL_LOW_REVIEW_V0`: локальные значимые уровни/low по уже изученной логике, затем показать пользователю entry/target outcome на этих уровнях.
## 2026-07-02 Good 1pct Review Pool

Статус: `GOOD_1PCT_REVIEW_POOL_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Создан быстрый сборщик review-пула для значимых low-кандидатов: `src/mlbotnav/visual_entry_good_1pct_review_pool.py`.

Рабочее правило: low-кандидат ищется past-only, `signal` = свеча low, `entry` = следующая свеча `open`, execution-аудит = `0/5/10bps`, основной расчет = `entry open + 5bps`, цель = `+1%` от execution-цены.

Smoke-запуск на `2026-05-13` дал `87` кандидатов: `5` GOOD и `82` BAD. Артефакты лежат в `reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/smoke_20260513_20260702_080455`.

Mini-run W20 `2026-05-13..2026-05-15` дал `261` кандидат: `73` GOOD и `188` BAD. Артефакты лежат в `reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/W20_mini_zoomfix_20260702_081003`.

Вывод: `+1%` outcome полезен как ускоренный review-pool, но не является gold-разметкой без ручного просмотра.

Добавлена VS Code задача `Visual Entry: Good 1pct Review Pool (NO ML/OPTUNA)`.

Граница: это не ML/export/training, не scorer, не target-lock и не Optuna. Outcome `+1%` используется только как offline label для ручного review.

## Fresh Target-Led DCA Risk Audit V0 2026-07-02

Статус: `DCA_RISK_AUDIT_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_API`.

Выполнен следующий разрешенный шаг после обсуждения DCA/ножей/перегруза: поверх уже готового `GOOD_1PCT` learning pool `W18-W20` построен risk-audit, который не ищет новые входы и не запускает ML. Он считает, сколько long-сделок висит одновременно, сколько времени сделка ждет `+1%`, какая просадка до цели/конца дня и какие входы зависят от позднего пампа.

Команда:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_dca_risk_audit_v0 --pool-run-dir reports\final_review\visual_entry_v3\fresh_target_led\good_1pct_review_pool\W18_W20_learning_20260702_082819 --run-label W18_W20_dca_risk --selected-limit-per-day 10 --late-hold-minutes 360 --overload-open-count 10 --render-top-days 3
```

Результат:

- дней обработано: `21`;
- записей пула: `1528`;
- GOOD из пула: `573`;
- BAD из пула: `955`;
- если брать все GOOD, максимум одновременно открыто: `44`;
- если брать первые `10` GOOD-сигналов в день, максимум одновременно открыто: `10`;
- худшая basket-просадка по all GOOD: `-2.685835%`;
- selected10 классы: `A_FAST_CLEAN=41`, `B_DCA_SURVIVABLE=52`, `C_LATE_PUMP_DEPENDENT=77`, `E_FALLING_KNIFE_NO_1PCT=7`, `E_FALLING_KNIFE_DEEP_DD=10`, `F_NO_1PCT_ROOM=2`.

Главный вывод: `+1% hit` сам по себе не равен good-сделке для ML. Дни `2026-05-02`, `2026-05-14`, `2026-05-11`, `2026-05-08`, `2026-05-03` показывают перегруз: много сделок может висеть до позднего пампа. Эти режимы надо отделять как risk class / hard-negative / отдельную DCA-политику, а не отдавать в ML как чистый long-сигнал.

Артефакты:

1. `src/mlbotnav/visual_entry_dca_risk_audit_v0.py`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_REPORT_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_TRADES.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_DAYS.csv`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_BASKETS.csv`;
6. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_SUMMARY.png`;
7. `reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_TOP_DAY_20260502.png`.

Следующий шаг: пользователь смотрит summary/top-day PNG и подтверждает, какие классы считать допустимыми для будущего датасета. До этого запрещено расширяться на full-history, запускать ML/export/training/scorer/target-lock/Optuna/API.

### DCA Risk Audit V0 Entry Marker Visual Fix 2026-07-02

После замечания пользователя исправлена визуализация entry на top-day PNG: треугольник теперь рисуется на фактическом `entry_open_price`, а расчетное исполнение `entry +5bps` показывается отдельной короткой белой меткой. Метрики риска не изменились.

Исправленный run:

`reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_entryopen_fix_20260702_161630`.

Главный PNG для проверки:

`reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_entryopen_fix_20260702_161630/DCA_RISK_AUDIT_V0_TOP_DAY_20260502.png`.

### DCA Risk Audit V0 2026-05-02 Closeup Pages 2026-07-02

После замечания пользователя, что full-day обзор непригоден для ручной правки входов, добавлен closeup-режим: `--closeup-day 2026-05-02 --closeup-per-page 9`.

Новый run:

`reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260502_closeups_20260702_162715`.

Проверено: в closeup-листы попали все `44` GOOD-сделки дня `2026-05-02`, по `9` панелей на страницу. Треугольник = `entry_open_price`, белая черта = `entry +5bps`, красная точка/линия = low/signal.
## 2026-07-02 Significant Low Calibration V0

Статус: `SIGNIFICANT_LOW_CALIBRATION_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

По замечанию пользователя, что нельзя брать все low подряд, добавлен отдельный слой калибровки значимого low: `src/mlbotnav/visual_entry_significant_low_calibration_v0.py`.

Смысл слоя:

1. пользовательский крест = `USER_REJECT_CURRENT_ENTRY`;
2. пользовательская стрелка/сдвиг = `USER_SHIFT_PENDING_REANCHOR`, это не готовая сделка, а место для отдельного zoom-переякоря;
3. без ручного reject low должен быть новым low в 60/180m контексте и иметь достаточное падение от prior high;
4. повтор внутри одного basin режется как дубль, если нет свежего более низкого low;
5. outcome `+1%` остается offline label, не causal feature.

Run по `2026-05-02`:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_20260502_v0_20260702_181433`

Итог:

- строк дня: `54`;
- `KEEP_SIGNIFICANT_LOW_V0`: `10`;
- `USER_SHIFT_PENDING_REANCHOR`: `10`;
- `USER_REJECT_CURRENT_ENTRY`: `24`;
- `REJECT_NOT_SIGNIFICANT_LOW_V0`: `6`;
- `REJECT_DUPLICATE_BASIN_LOW_V0`: `4`.

Главный вывод: текущий `GOOD_1PCT` pool нельзя отдавать в ML как есть. Новый слой уже отделяет значимые low от микролоев, дублей, ручных rejects и мест, где нужно переякорить вход ниже. Следующий ручной шаг: посмотреть 10 зеленых `KEEP_SIGNIFICANT_LOW_V0` и 10 желтых `USER_SHIFT_PENDING_REANCHOR`, затем решить параметры V1.

Границы: ML/export/training/scorer/target-lock/Optuna/API не запускались и остаются запрещены без отдельного разрешения.

### 2026-07-02 User Actual Overview V1B

Пользователь прислал актуальную разметку поверх overview. Перечеркнутые `LA001`, `LA004`, `LA005`, `LA006`, `LA008`, `LA025`, `LA027`, `LA034`, `LA036`, `LA047`, `LA050`, `LA053`, `LA054` перенесены в `USER_REJECT_CURRENT_ENTRY`.

Актуальный run:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_20260502_user_actual_v1b_20260702_185032`

Итог актуального слоя:

- `KEEP_SIGNIFICANT_LOW_V0`: `7` (`LA002`, `LA015`, `LA018`, `LA021`, `LA040`, `LA048`, `LA051`);
- `USER_SHIFT_PENDING_REANCHOR`: `2` (`LA007`, `LA028`);
- `USER_REJECT_CURRENT_ENTRY`: `37`;
- `REJECT_NOT_SIGNIFICANT_LOW_V0`: `6`;
- `REJECT_DUPLICATE_BASIN_LOW_V0`: `2`.

Рабочий вывод: на этом дне после актуального ручного feedback остается `7` потенциально хороших значимых low и `2` точки для отдельного переякоря. Это еще не ML-датасет, а ручной review layer.

### 2026-07-02 User Actual Overview V1C3

Статус: `SIGNIFICANT_LOW_USER_ACTUAL_V1C3_READY_FOR_REVIEW_NO_ML_NO_OPTUNA`.

По уточнению пользователя после просмотра правого участка overview:

1. `LA048` не подходит и перенесен в `USER_REJECT_CURRENT_ENTRY`;
2. соседний автоматический `LA049` также принудительно отклонен, чтобы он не заменял ошибочный `LA048`;
3. хорошая нижняя точка `LA050` принята как `USER_APPROVE_CURRENT_ENTRY` и оставлена в `KEEP_SIGNIFICANT_LOW_V0`;
4. красные reject-кресты и линии сделаны менее агрессивными по прозрачности.

Актуальный run:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_20260502_user_actual_v1c3_20260702_190227`

Итог актуального слоя:

- `KEEP_SIGNIFICANT_LOW_V0`: `6` (`LA002`, `LA015`, `LA018`, `LA021`, `LA040`, `LA050`);
- `USER_SHIFT_PENDING_REANCHOR`: `2` (`LA007`, `LA028`);
- `USER_REJECT_CURRENT_ENTRY`: `38`;
- `REJECT_NOT_SIGNIFICANT_LOW_V0`: `6`;
- `REJECT_DUPLICATE_BASIN_LOW_V0`: `2`.

Контроль по спорному месту: `LA048` = reject, `LA049` = reject, `LA050` = keep/approve, `LA051` = duplicate-basin reject.

Граница: это только ручной significant-low review layer. ML/export/training/scorer/target-lock/Optuna/API не запускались.

### 2026-07-03 Reanchor Zoom V0 For User Arrows

Статус: `SIGNIFICANT_LOW_REANCHOR_ZOOM_V0_READY_FOR_USER_ARROWS_NO_ML_NO_OPTUNA`.

По новому скриншоту пользователя три красных блока вынесены в отдельный крупный zoom-лист для точного ручного указания low стрелкой:

1. `RB01_LA007_REANCHOR`: текущий `LA007` желтый, это только placeholder для переякоря;
2. `RB02_LA028_REANCHOR`: текущий `LA028` желтый, это только placeholder для переякоря;
3. `RB03_LA050_AREA`: `LA048/LA049` reject, `LA050` текущий keep; пользователь может подтвердить или показать точнее.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_zoom_v0_20260702_191450/SIGNIFICANT_LOW_REANCHOR_ZOOM_V0_20260502.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_zoom_v0_20260702_191450/SIGNIFICANT_LOW_REANCHOR_ZOOM_V0_20260502.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_zoom_v0_20260702_191450/SIGNIFICANT_LOW_REANCHOR_ZOOM_V0_20260502_RU.md`.

Граница: это не новая стратегия и не готовый ML-label. Это рабочий zoom для пользовательских стрелок и последующего точного переноса low/entry.

### 2026-07-03 Reanchor Applied V0

Статус: `SIGNIFICANT_LOW_REANCHOR_APPLIED_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

По скриншоту со стрелками применена ручная правка:

1. `RA001_FROM_LA007`: стрелка пользователя указывает low-свечу `2026-05-02T03:14:00Z`; вход по рельсам = next open `2026-05-02T03:15:00Z`, `entry_open=83.72000000`, `entry +5bps=83.76186000`;
2. `RA002_PENDING_FROM_LA028`: в последнем скриншоте нет новой стрелки, поэтому `LA028` остается `pending reanchor`, без самовольного переноса;
3. `RA003_CONFIRM_LA050`: стрелка пользователя подтверждает текущий `LA050`; signal `2026-05-02T22:25:00Z`, entry `2026-05-02T22:26:00Z`, `entry_open=84.22000000`, `entry +5bps=84.26211000`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v0_20260702_192103/SIGNIFICANT_LOW_REANCHOR_APPLIED_V0_20260502_OVERVIEW.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v0_20260702_192103/SIGNIFICANT_LOW_REANCHOR_APPLIED_V0_20260502_ZOOM.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v0_20260702_192103/SIGNIFICANT_LOW_REANCHOR_APPLIED_V0_20260502.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v0_20260702_192103/SIGNIFICANT_LOW_REANCHOR_APPLIED_V0_20260502.json`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v0_20260702_192103/SIGNIFICANT_LOW_REANCHOR_APPLIED_V0_20260502_RU.md`.

Граница: это ручной reanchor review layer. ML/export/training/scorer/target-lock/Optuna/API не запускались.

### 2026-07-03 Reanchor Applied V1

Статус: `SIGNIFICANT_LOW_REANCHOR_APPLIED_V1_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

По уточнению пользователя `LA050` сдвинут на одну свечу влево и визуальный маркер поставлен на low-зону:

1. `RA001_FROM_LA007` без изменений: signal `2026-05-02T03:14:00Z`, entry `2026-05-02T03:15:00Z`, `entry +5bps=83.76186000`;
2. `RA002_PENDING_FROM_LA028` остается pending: в последнем скрине нет новой стрелки по этому блоку;
3. `RA003_SHIFT_LEFT_LA050`: визуальный marker `2026-05-02T22:25:00Z` на low `84.02000000`; отдельно сохранены execution fields: `entry_open=84.06000000`, `entry +5bps=84.10203000`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v1_20260703_060258/SIGNIFICANT_LOW_REANCHOR_APPLIED_V1_20260502_OVERVIEW.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v1_20260703_060258/SIGNIFICANT_LOW_REANCHOR_APPLIED_V1_20260502_ZOOM.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v1_20260703_060258/SIGNIFICANT_LOW_REANCHOR_APPLIED_V1_20260502.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v1_20260703_060258/SIGNIFICANT_LOW_REANCHOR_APPLIED_V1_20260502.json`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v1_20260703_060258/SIGNIFICANT_LOW_REANCHOR_APPLIED_V1_20260502_RU.md`.

Важно: `RA003_SHIFT_LEFT_LA050` содержит визуальный low marker и отдельную execution-цену. Это сделано явно, чтобы не потерять различие между ручной визуальной точкой и боевым `entry +5bps`.

Граница: ML/export/training/scorer/target-lock/Optuna/API не запускались.

### 2026-07-03 User New Entry Zoom V0

Статус: `SIGNIFICANT_LOW_USER_NEW_ENTRY_ZOOM_V0_READY_FOR_USER_ARROW_NO_ML_NO_OPTUNA`.

По скриншоту пользователя подготовлен отдельный zoom участка перед вечерним импульсом, где пользователь хочет показать новую точку входа.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_user_new_entry_zoom_v0_20260703_060806/SIGNIFICANT_LOW_USER_NEW_ENTRY_ZOOM_V0_20260502_2045_2105.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_user_new_entry_zoom_v0_20260703_060806/SIGNIFICANT_LOW_USER_NEW_ENTRY_ZOOM_V0_20260502.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_user_new_entry_zoom_v0_20260703_060806/SIGNIFICANT_LOW_USER_NEW_ENTRY_ZOOM_V0_20260502_RU.md`.

Граница: это только zoom для ручной стрелки, не новая разметка. После стрелки нужно создать отдельный applied/reanchor layer.

### 2026-07-03 Reanchor Applied V2 User Entry 20:49

Статус: `SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

После стрелки пользователя на zoom-участке `20:45-21:05 UTC` добавлена новая ручная точка:

1. `RA004_USER_ENTRY_2049`: пользовательская стрелка трактуется как вход на свече `2026-05-02T20:49:00Z`;
2. signal по рельсам сохранен как предыдущая закрытая свеча `2026-05-02T20:48:00Z`;
3. low свечи: `84.05000000`;
4. `entry_open`: `84.09000000`;
5. `entry +5bps`: `84.13204500`.

Актуальный run:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904`

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502_CLOSE_ZOOM_RA004.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502_OVERVIEW.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502.json`.

Важно: close-zoom сделан без растягивания шкалы до `+1%` target, чтобы глазами было видно саму точку входа. Это ручной applied/reanchor слой, не ML-label. ML/export/training/scorer/target-lock/Optuna/API не запускались.

### 2026-07-03 Manual Reanchors V0 Source Of Truth

Статус: `SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

После сбоя/перезапуска зафиксирована причина каши: старые applied V1/V2 и DCA/GOOD-графики могли смешивать ручные точки, pending reanchor и старые outcome-сделки. Для точной добивки входов создан отдельный воспроизводимый источник правды:

`configs/visual_entry/manual_reanchors/SOLUSDT_1m_2026-05-02_SIGNIFICANT_LOW_MANUAL_REANCHORS_V0.json`

Правило нового слоя:

1. `signal_time_utc` и `entry_time_utc` - контракт исполнения;
2. `visual_marker_time_utc` и `visual_marker_price` - только визуальная точка для глаз;
3. pending-точки не попадают в clean overview;
4. старые `GOOD_1PCT`, DCA rows, rejected/soft и автоматические 44 сделки не подтягиваются.

Новый скрипт:

`src/mlbotnav/visual_entry_manual_reanchor_review_v0.py`

Актуальный run:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936`

Итог run:

1. всего строк: `4`;
2. clean confirmed overview: `3` (`RA001_FROM_LA007`, `RA003_SHIFT_LEFT_LA050`, `RA004_USER_ENTRY_2049`);
3. pending review: `1` (`RA002_PENDING_FROM_LA028`);
4. хвостов `python.exe` после запуска нет.

Главные артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936/SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_20260502_CONFIRMED_OVERVIEW.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936/SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_20260502_REVIEW_SHEET.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936/SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_20260502_RA003_SHIFT_LEFT_LA050_CLOSE_ZOOM.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936/SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_20260502_RA004_USER_ENTRY_2049_CLOSE_ZOOM.png`;
5. `reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936/SIGNIFICANT_LOW_MANUAL_REANCHORS_V0_20260502.csv`.

Текущий следующий шаг: пользователь смотрит новый `REVIEW_SHEET` и close-zoom по `RA003/RA004`. Если нужно двигать точку - править только JSON source-of-truth и заново запускать renderer. ML/export/training/scorer/target-lock/Optuna/API запрещены.

### 2026-07-03 STAS1 GOOD_1PCT anchor-next-open fix

Статус: `STAS1_GOOD_1PCT_ANCHOR_NEXT_OPEN_FIX_V0_VERIFIED_NO_ML_NO_OPTUNA`.

По просьбе пользователя перепроверены `44` GOOD-сделки старого прогона `2026-05-02`. Найдена причина смещения входов: `build_candidates()` искал фактический `anchor_idx` как low, но `signal_time_utc` и `entry_idx` ставил от более поздней confirmation-свечи. Из-за этого часть входов уходила через 2-4 свечи после low.

Старый контроль по `GOOD_1PCT_REVIEW_POOL_RECORDS.csv`:

1. всего строк: `54`;
2. GOOD: `44`;
3. нарушений `entry_time_utc != anchor_time_utc + 1 minute` среди GOOD: `12`.

Исправлено в `src/mlbotnav/visual_entry_low_anchor_suggester.py`:

1. `signal_idx = anchor_idx`;
2. `entry_idx = anchor_idx + 1`;
3. `entry_time_utc` теперь строго следующая свеча после low;
4. `confirmation_idx` и `confirmation_time_utc` сохранены отдельно как справочный контекст;
5. в CSV `GOOD_1PCT` добавлены индексы `anchor_idx`, `signal_idx`, `confirmation_idx`, `entry_idx`, `execution_delay_bars_from_anchor`.

Контрольный run:

`STAS1_GOOD_LOW_REVIEW/runs/stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034`

Итог нового run:

1. всего строк: `52`;
2. GOOD: `42`;
3. BAD: `10`;
4. нарушений `entry_time_utc != anchor_time_utc + 1 minute`: `0`;
5. хвостов `python.exe` после проверки нет.

Проверки:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_suggester.py src\mlbotnav\visual_entry_good_1pct_review_pool.py tests\test_visual_entry_low_anchor_suggester.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_low_anchor_suggester.py -q
$env:PYTHONPATH='src'; .\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-02 -RunLabel stas1_20260502_1pct_anchor_next_open_fix_v0
```

Граница: это только STAS1 visual review/candidate pool. ML/export/training/scorer/target-lock/Optuna/API не запускались.

### 2026-07-03 STAS1 EndDay wrapper fix

Статус: `STAS1_WRAPPER_ENDDAY_FIX_VERIFIED_NO_ML_NO_OPTUNA`.

После проверки пользователем обнаружено, что команда с `-EndDay` запускала только один день: `run_day_1pct.ps1` и `run_day_0p5.ps1` принимали только `-Day` и внутри передавали `--end-day $Day`.

Исправлено:

1. `STAS1_GOOD_LOW_REVIEW/run_day_1pct.ps1` поддерживает `-EndDay`;
2. `STAS1_GOOD_LOW_REVIEW/run_day_0p5.ps1` поддерживает `-EndDay`;
3. если `-EndDay` не задан, поведение прежнее: один день;
4. README STAS1 обновлен командами для диапазона дней.

Smoke-run:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-03 -EndDay 2026-05-04 -RunLabel stas1_smoke_20260503_20260504_endday_fix_v0 -RenderGoodLimit 0
```

Результат:

1. `days_requested=2`;
2. `days_processed=2`;
3. `records_total=132`;
4. `bad_anchor_to_entry=0`;
5. хвостов `python.exe` нет.

Run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_smoke_20260503_20260504_endday_fix_v0_20260703_173534`.
