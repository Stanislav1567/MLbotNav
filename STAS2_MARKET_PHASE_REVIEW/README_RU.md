# STAS2 MARKET PHASE REVIEW

Статус: `STAS2_MARKET_PHASE_REVIEW_CONTINUOUS_WAVE_READY_NO_ML_NO_OPTUNA_REVIEW_ONLY`.

## Что это

`STAS2` - отдельный визуальный контур поверх текущего `STAS1`.

Он не ищет новые входы и не меняет Stas1. Он читает готовые Stas1 run CSV и переносит на графики:

1. торговую UTC-корзину времени;
2. `weekday/weekend`;
3. `effective_session`;
4. фон рынка отдельно от LONG-волны;
5. `SHORT`-волны закрытого часа;
6. непрерывные `WAVE` swing-блоки без жесткой привязки к дню;
7. дневные срезы `WAVE` с `carry_from_prev/carry_to_next`, если волна идет через `00:00`;
8. серые `GAP`-сегменты в строке `WAVE`, если часть графика не покрыта подтвержденной волной;
9. отдельную оценку `setup_quality` для конкретной точки входа;
10. движение цены до входа;
11. range до входа;
12. pre-entry контекст `5m / 15m / 30m / 60m`;
13. Stas1 входы как точки на графике.

## Главная граница

Stas2 работает только с тем, что видно до входа.

Запрещено внутри Stas2:

1. считать TP;
2. выбирать лучший выход;
3. смотреть 5m-блоки после входа;
4. считать MFE/MAE;
5. строить percent ladder сделки;
6. запускать ML, Optuna, scorer, target-lock или API.

Все после входа относится к `STAS3`.

## WAVE и GAP

`WAVE` - подтвержденные swing-блоки по развороту `1%` без привязки к календарному дню.

`STAS2_CONTINUOUS_WAVES.csv` - главный ledger волн. Волна имеет собственные `start_time`, `end_time`, направление, полный процент и статус.

`STAS2_MACRO_WAVES.csv` - дневные срезы continuous-волн для PNG. Если волна началась вчера и закончилась сегодня, в дневном срезе будут `carry_from_prev` и/или `carry_to_next`, а также `visible_move_pct` и `full_move_pct`.

`GAP` - серый учетный блок в строке `WAVE`, который закрывает пропуск между подтвержденными волнами или край дня. Для `GAP` показывается процент диапазона внутри этого промежутка. Это не точка входа, не TP и не ML-признак.

Короткая сильная `WAVE` тоже подписывается: если видимый ход `>= 1%` и длительность `>= 5m`, на узком квадрате выводится компактный процент без длинного текста.

## Рабочий движок

```text
src/mlbotnav/visual_entry_stas2_market_phase_review.py
```

## Быстрый запуск одного дня

```powershell
.\STAS2_MARKET_PHASE_REVIEW\run_day.ps1 -Day 2026-05-02 -Stas1RunDir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034
```

## Запуск диапазона

```powershell
.\STAS2_MARKET_PHASE_REVIEW\run_range.ps1 -Day 2026-05-02 -EndDay 2026-05-03 -Stas1RunDir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034,STAS1_GOOD_LOW_REVIEW\runs\stas1_20260503_all_closeups_bad_x_v0_20260706_060244
```

## Открыть последний результат

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
```

## Где результаты

```text
STAS2_MARKET_PHASE_REVIEW/runs/
```

Внутри каждого run:

1. `STAS2_DAY_OVERVIEW_YYYYMMDD.png` - день целиком с фоном сессий, полосами `Фон`, `LONG`, `SHORT`, `WAVE` и Stas1 входами. Точки входа рисуются как в Stas1; текстовые названия возле точек не рисуются. `setup_quality` смотреть в CSV/XLSX и closeup-тексте.
2. `STAS2_ENTRY_CONTEXT_PAGE_*.png` - closeup-страницы входов, где свечи после entry не рисуются.
3. `BROWSE_BY_DAY/` - дневной просмотр как в Stas1.
4. `STAS2_RECORDS.csv` - entry context с pre-entry полями.
5. `STAS2_MARKET_PHASE_TABLES.xlsx` - Excel-friendly таблицы.
6. `STAS2_CONTINUOUS_WAVES.csv` - глобальные волны без разрезания по дню.
7. `STAS2_MACRO_WAVES.csv` - дневные срезы continuous-волн для overview.
8. `STAS2_PAYLOAD.json` - полный payload.
9. `STAS2_REPORT_RU.md` - короткий русский отчет.

## Ключевые поля

```text
pre_5m_range_pct
pre_5m_close_move_pct
pre_5m_phase
pre_5m_background_phase
pre_5m_long_wave_up_from_low_pct
pre_5m_long_wave_pullback_from_high_pct
pre_15m_range_pct
pre_15m_close_move_pct
pre_15m_phase
pre_15m_background_phase
pre_15m_long_wave_up_from_low_pct
pre_15m_long_wave_pullback_from_high_pct
pre_30m_range_pct
pre_30m_close_move_pct
pre_30m_phase
pre_30m_background_phase
pre_30m_long_wave_up_from_low_pct
pre_30m_long_wave_pullback_from_high_pct
pre_60m_range_pct
pre_60m_close_move_pct
pre_60m_phase
pre_60m_background_phase
pre_60m_long_wave_up_from_low_pct
pre_60m_long_wave_pullback_from_high_pct
hour_short_wave_down_from_high_pct
hour_short_wave_rank
hour_direction_bias
macro_wave_direction
macro_wave_start_time_utc
macro_wave_end_time_utc
macro_wave_move_pct
macro_wave_boundary
entry_setup_quality_code
entry_setup_quality_rank
entry_setup_quality_label
entry_setup_quality_reason
stas1_risk_flags
stas1_feature_range_pos_10
stas1_feature_range_pos_20
stas1_feature_volume_ratio20
stas1_feature_lower_wick_to_body
session_so_far_range_pct
day_so_far_range_pct
context_max_open_time_utc
context_before_entry_check
```

`context_before_entry_check=True` означает, что последний использованный бар контекста строго раньше `entry_time_utc`.

`macro_wave_*` является review/hindsight слоем для визуальной сверки больших движений. Это не pre-entry feature и не ML-label без отдельной causal-разметки.

Важно: `background_phase` - это общий фон/range/волатильность окна. `long_wave` - это направленная LONG-волна внутри того же окна: low -> subsequent high и откат от этой вершины к последнему закрытому close до входа. Поэтому `Слабая` в фоне не означает, что на графике не было рабочей волны вверх.

`entry_setup_quality_*` - это отдельная оценка чистоты конкретной точки входа. Она нужна, чтобы сильный фон или большая pre-wave не выглядели как автоматическое разрешение на вход. Например, после резкого выноса точка может остаться Stas1 outcome GOOD, но получить `NOISE: после выноса` для ручного удаления/negative review.

## Правило работы дальше

Сначала смотрим Stas2 глазами и понимаем, в каких фазах/сессиях Stas1 входы выглядят нормально, а где это шум. Только после этого отдельно строим Stas3 для post-entry percent ladder и TP/exit validation.
