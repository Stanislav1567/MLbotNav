# ТЗ STAS3 V2: процентная лестница движения и TP без превращения в стратегию

Статус: `DRAFT_FOR_USER_REVIEW_STAS3_V2_RESET_NO_ML_NO_OPTUNA_NO_SCORER`.

Дата фиксации: `2026-07-09`.

## 1. Зачем обнуляем Stas3

Текущий Stas3 V1 полезен как архивный post-entry audit, но его нельзя считать чистым этапом Stas3 по исходному смыслу.

Проблемы V1:

1. `MFE MAX` и зеленые стрелки визуально стали выглядеть как идеальная сделка до максимума.
2. `reasonable TP` начал читаться как готовое правило выхода, хотя он был рассчитан после входа по факту движения.
3. В V1 в одном слое смешались быстрые TP от `0.2%`, средние ходы `1-3%` и swing-движения `5-7%`; в V2 рабочая сетка начинается только с `0.3%`.
4. Big-move review начал тянуть Stas3 в сторону стратегии удержания, хотя по ТЗ Stas3 должен быть только анализом и проверкой.
5. После обновления Stas2 появились `SHORT`, `WAVE`, `GAP`, continuous wave ledger, но они пока не разведены в Stas3 на causal/review-only контекст.
6. Процентная сетка V1 начиналась с `0.2%`, хотя для текущего Stas3 пользователь зафиксировал минимальную рабочую сетку от `0.3%`.
7. Stas3 V1 не был жестко ограничен LONG-контуром, хотя текущая задача Stas3 V2 - разбирать только LONG-входы и LONG-движение.

Решение: старые Stas3 runs и код не удалять. Считать их `STAS3_V1_ARCHIVE_REVIEW_ONLY`. Новый Stas3 V2 проектировать заново по этому ТЗ.

## 2. Место Stas3 в цепочке

### Stas1

Stas1 дает кандидаты входов:

1. фактический low/anchor;
2. `signal_time_utc`;
3. `entry_time_utc = signal + next open`;
4. `entry_open_price`;
5. `entry_price_5bps`;
6. исходный outcome только как offline review label.

Stas1 не решает фазу рынка и не решает TP.

### Stas2

Stas2 дает контекст вокруг входа:

1. фон рынка;
2. LONG по закрытым часам и `SHORT`-процент только как риск-фон против LONG;
3. setup quality;
4. сессия/день;
5. pre-entry range/volatility/path;
6. визуальные WAVE/GAP/continuous-wave слои для ручного понимания структуры движения.

Критично: часть Stas2 `WAVE/GAP/continuous-wave` является hindsight/review слоем. В Stas3 V2 такие поля нельзя молча использовать как причину TP. Их нужно маркировать отдельно:

```text
context_scope = PRE_ENTRY_CAUSAL
context_scope = POST_ENTRY_REVIEW
context_scope = HINDSIGHT_WAVE_REVIEW
```

### Stas3

Stas3 отвечает только за жизнь сделки после входа:

1. какой процент цена реально прошла после входа;
2. какие уровни процентной лестницы были достигнуты;
3. сколько времени заняло достижение каждого процента;
4. какая была просадка до движения;
5. какой диапазон TP реалистично наблюдался для фазы/контекста;
6. где вход был шумом;
7. где вход был хороший, но TP был выбран неправильно.

Stas3 не открывает новые сделки и не превращает TP в стратегию.

## 2.1. Рабочий режим V2: только LONG

Stas3 V2 на первом этапе работает только с LONG.

Разрешено:

1. брать Stas1 LONG low-входы;
2. смотреть Stas2 `LONG`-контекст;
3. учитывать Stas2 `SHORT` только как процентный риск/фон против LONG, а не как сделку;
4. сравнивать LONG-вход с текущей/ближайшей `WAVE`, если контекст помечен корректным scope.

Запрещено в первом V2:

1. строить short-сделки;
2. искать short-точки входа;
3. считать short-TP;
4. смешивать LONG и SHORT статистику TP;
5. считать SHORT-волну отдельной стратегией выхода;
6. выводить общий TP ladder без разделения направления.

Если позже понадобится short-контур, он должен стать отдельным `STAS3_SHORT_V*`, а не смешиваться с текущим LONG Stas3.

## 3. Главный запрет V2

В Stas3 V2 запрещено:

1. называть `MFE MAX` тейк-профитом;
2. рисовать идеальную сделку `low -> максимум` как будто это реальный выход;
3. использовать будущий максимум как причину выбора TP;
4. переносить post-entry поля назад в Stas1/Stas2;
5. считать `reasonable_tp_pct` боевым правилом;
6. запускать ML/export/training;
7. запускать Optuna;
8. строить scorer;
9. строить target-lock;
10. обращаться к торговому API.

Разрешено:

1. считать post-entry факты;
2. группировать факты по pre-entry фазам;
3. строить статистику достижимости процентов;
4. делать ручной review шума и неправильного TP;
5. формировать первую процентную лестницу как аналитический отчет.

## 4. Процентная лестница

Быстрая сетка:

```text
0.3%, 0.4%, 0.5%, 0.6%, 0.7%, 0.8%, 0.9%
```

Средняя сетка `1.0-2.0%`:

```text
1.0%, 1.1%, 1.2%, 1.3%, 1.4%, 1.5%, 1.6%, 1.7%, 1.8%, 1.9%, 2.0%
```

Продолжение средней сетки `2.0-20.0%`:

```text
2.0%, 2.2%, 2.4%, 2.6%, 2.8%, 3.0%, 3.2%, ... до 20.0% с шагом 0.2%
```

В реализации уровни генерировать программно и дедублицировать границу `2.0%`, чтобы один и тот же уровень не появлялся дважды.

Рабочий максимум первого V2: считать до `20.0%`.

В отчете отдельно показывать зоны:

1. `0.3-0.9%` - быстрые TP;
2. `1.0-2.0%` - средние LONG-ходы с плотным шагом `0.1%`;
3. `2.2-20.0%` - продолжение среднего LONG-хода с шагом `0.2%`, без оформления в swing-стратегию.

Важно: swing-контур пока не размещать и не классифицировать как отдельную стратегию. На этом этапе нужно получить быстрые входы и средние LONG-ходы от `1.0%` и выше.

Если данных для высоких уровней `5.0-20.0%` мало, выводить `INSUFFICIENT_DATA_REVIEW_ONLY`, а не делать вывод о TP.

Для каждого процента считать:

1. `hit_X_pct`: достигнут или нет;
2. `time_to_X_pct_min`: время до достижения;
3. `mae_before_X_pct`: максимальная просадка до достижения;
4. `hit_before_mae_limit`: достигнут ли процент до недопустимой просадки;
5. `first_ladder_hit_pct`: первый достигнутый процент из сетки;
6. `max_ladder_hit_pct`: максимальный достигнутый процент из сетки;
7. `move_scale_bucket`: `FAST_TP`, `MEDIUM_MOVE`, `MEDIUM_EXTENSION_REVIEW`, `ABOVE_GRID_DIAGNOSTIC`.

## 5. Что значит "реалистичный TP"

В Stas3 V2 `разумный TP` не равен максимуму движения.

TP считается реалистичным только если:

1. этот процент часто достигается внутри похожей фазы;
2. он достигается не слишком поздно;
3. просадка до него не ломает сделку;
4. количество примеров в группе достаточно для review;
5. он не опирается на будущий `MFE MAX` конкретной сделки как причину.
6. он не требует, чтобы сделка искусственно закрывалась в рамках одного UTC-дня.

Результат должен быть диапазоном, а не одной магической цифрой:

```text
phase_tp_min_pct
phase_tp_base_pct
phase_tp_stretch_pct
phase_tp_forbidden_reason
```

Пример интерпретации:

1. мертвая фаза: вход запрещен или только наблюдение;
2. слабая: минимальный TP около нижней сетки `0.3%`;
3. средняя: малый/средний TP из зоны `0.3-0.6%`;
4. сильная: нормальный TP из зоны `0.7-1.0%`;
5. очень сильная: расширенный TP выше `1.0%` только если статистика подтверждает.

Границы не задавать руками. Их выводить из данных.

## 6. Входные данные V2

Обязательные входы:

1. `STAS2_RECORDS.csv` из выбранного Stas2 run;
2. OHLCV `1m`;
3. Stas1 поля входа, протянутые через Stas2;
4. pre-entry поля Stas2.

### 6.1. Жесткий контракт точки входа

Stas3 V2 не ищет новые low, не придумывает новые входы и не двигает точку сделки глазами по графику.

Для каждой строки входа использовать уже готовые поля из `STAS2_RECORDS.csv`:

```text
candidate_id
anchor_time_utc
anchor_low_price
entry_time_utc
entry_open_price
entry_price_5bps
context_before_entry_check
```

Правило цены:

1. `anchor_time_utc` / `anchor_low_price` - это точка low/сигнала;
2. `entry_time_utc` - фактическая свеча входа после сигнала;
3. `entry_open_price` - open свечи входа;
4. `entry_price_5bps` - расчетная цена входа с учетом 5 bps, основной `entry_price_for_calc`;
5. все проценты Stas3 V2 считать от `entry_price_for_calc = entry_price_5bps`;
6. если `entry_price_5bps` пустой, строку не считать молча: отправлять в `STAS3_V2_SKIPPED_ROWS.csv` с причиной `missing_entry_price_5bps`.

В отчете обязательно показывать цену входа рядом с каждой сделкой, чтобы было видно, откуда считается процент.

Первый рабочий Stas2 source для ТЗ V2:

```text
STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330
```

Проверка этого run перед правкой ТЗ:

```text
STAS2_RECORDS.csv: 214 строк
days: 2026-05-10, 2026-05-11, 2026-05-12
missing_anchor_low_price: 0
missing_entry_open_price: 0
missing_entry_price_5bps: 0
context_before_entry_check != True: 0
STAS2_CONTINUOUS_WAVES.csv: LONG 14, SHORT 13, GAP 2
```

Этот Stas2 уже содержит визуальный контекст `LONG`, `SHORT`, `WAVE`, `GAP`, continuous waves и перенос волн через `00:00`. Для Stas3 V2 брать только LONG-входы. `SHORT` использовать только как процентный риск-фон/противоход для LONG, без short-входов, short-TP и отдельной short-статистики. `GAP` использовать только как фон/контекст, а не как отдельные сделки.

Рабочие дни первого V2-разбора строго:

```text
2026-05-10
2026-05-11
2026-05-12
```

Другие дни в первый V2-разбор не подмешивать, чтобы не смешать выводы по разным Stas2-схемам.

Важно: Stas3 V2 не ограничивает сделку календарными `24h`. Если вход был в одном дне, а движение/волна продолжается на следующий день, post-entry audit должен уметь смотреть дальше в пределах заданного окна удержания.

Опциональные входы:

1. `STAS2_MACRO_WAVES.csv`;
2. `STAS2_CONTINUOUS_WAVES.csv`;
3. дневные `*_STAS2_MACRO_WAVES.csv`.

Опциональные wave-поля можно добавлять в Stas3 только с явным `context_scope`. Если поле знает будущий конец волны, оно должно быть `HINDSIGHT_WAVE_REVIEW`, а не `PRE_ENTRY_CAUSAL`.

Для волн через день:

1. использовать `continuous_wave_id`, чтобы понимать, что это одна волна, а не два независимых дневных блока;
2. хранить `wave_carry_from_prev_day` и `wave_carry_to_next_day`;
3. различать `visible_move_pct` внутри дня и `full_move_pct` всей continuous-волны;
4. не использовать будущий `full_move_pct` как причину выбора TP на входе.

### 6.2. Контекстные блоки Stas2, которые нужно собрать в единое целое

Stas3 V2 должен использовать не только цену входа, а полный контекст, который виден на Stas2-графике:

1. верхняя строка сессий;
2. строка `Фон`;
3. строка `LONG`;
4. строка `SHORT` только как процентный риск-фон/противоход для LONG, без short-входа;
5. строка `WAVE`;
6. процентные блоки волатильности/хода;
7. объем под графиком.

Табличные источники этих блоков:

```text
STAS2_RECORDS.csv
STAS2_HOURLY_PHASES.csv
STAS2_DAY_SUMMARY.csv
STAS2_ENTRY_SESSION_SUMMARY.csv
STAS2_ENTRY_LONG_WAVE_SUMMARY.csv
STAS2_MACRO_WAVES.csv
STAS2_CONTINUOUS_WAVES.csv
OHLCV 1m
```

Минимальные поля контекста, которые нужно протянуть в Stas3 V2:

```text
session_time_bucket_code
session_time_bucket_label
effective_session_code
effective_session_label
real_tradfi_session_open
hour_background_phase
hour_background_phase_rank
hour_range_pct
hour_path_pct
hour_close_move_pct
hour_long_wave_phase
hour_long_wave_up_from_low_pct
hour_long_wave_pullback_from_post_low_high_pct
hour_short_wave_phase
hour_short_wave_down_from_high_pct
short_context_only_flag
hour_direction_bias
pre_5m_range_pct
pre_15m_range_pct
pre_30m_range_pct
pre_60m_range_pct
pre_5m_path_pct
pre_15m_path_pct
pre_30m_path_pct
pre_60m_path_pct
pre_5m_long_wave_phase
pre_15m_long_wave_phase
pre_30m_long_wave_phase
pre_60m_long_wave_phase
macro_wave_direction
macro_wave_visible_move_pct
macro_wave_full_move_pct
continuous_wave_id
volume_context
```

`volume_context` в первом V2 можно собрать из OHLCV и уже протянутых Stas1/Stas2 volume-полей; если полного volume-блока еще нет, явно пометить `volume_context_status=PARTIAL`, а не делать вид, что объем полностью учтен.

Если в Stas3 V2 протягиваются поля `hour_short_wave_*`, рядом обязательно ставить `short_context_only_flag=True`. Это означает: `SHORT` учтен только как риск-фон для LONG и не может использоваться как short-сделка, short-TP или short-статистика.

### 6.3. Идеальный TP в Stas3 V2

Пользовательская цель для V2: для каждой уже заданной LONG-сделки собрать контекст входа и post-entry путь, затем показать, до какого процента TP сделка реально могла дойти.

В ТЗ это называется не боевым TP, а review-полями:

```text
max_feasible_review_tp_pct
ideal_review_tp_pct
ideal_review_tp_reason
ideal_review_tp_warning
```

Правила:

1. `max_feasible_review_tp_pct` - максимальный уровень сетки, который был достигнут после `entry_time_utc` от `entry_price_for_calc`;
2. `ideal_review_tp_pct` - лучший hindsight-TP для разбора конкретной LONG-сделки с учетом времени до цели, MAE, сессии, фона, LONG, `SHORT`-risk%, WAVE и волатильности;
3. если высокий TP достигался только после глубокой просадки, позднего пампа, сильного `SHORT`-risk% или WAVE-противохода, ставить предупреждение;
4. `ideal_review_tp_pct` нельзя использовать как готовую торговую команду, scorer, target-lock или ML-label без отдельного approved-ledger;
5. в отчете обязательно показывать, почему выбранный hindsight-TP был доступен: `session + фон + LONG + SHORT-risk% + WAVE + volatility + post-entry path`.

## 7. Выходные таблицы V2

### 7.1. Основная таблица входов

Файл:

```text
STAS3_V2_ENTRY_TP_AUDIT.csv
```

Минимальные колонки:

```text
candidate_id
day_utc
signal_time_utc
anchor_time_utc
entry_time_utc
anchor_low_price
entry_open_price
entry_price_5bps
entry_price_for_calc
entry_price_source
entry_price_locked_flag
entry_price_missing_flag
phase_at_entry
session
session_time_bucket_code
session_time_bucket_label
effective_session_code
effective_session_label
hour_background_phase
hour_range_pct
hour_path_pct
hour_long_wave_phase
hour_long_wave_up_from_low_pct
hour_short_wave_phase
hour_short_wave_down_from_high_pct
short_context_only_flag
hour_direction_bias
wave_context_scope
continuous_wave_id
macro_wave_direction
macro_wave_visible_move_pct
macro_wave_full_move_pct
volume_context_status
entry_setup_quality_label
context_scope
direction_scope
long_only_flag
actual_mfe_pct
actual_mae_pct
max_ladder_hit_pct
first_ladder_hit_pct
fast_tp_max_hit_pct
medium_move_max_hit_pct
move_scale_bucket
reasonable_tp_min_pct
reasonable_tp_base_pct
reasonable_tp_stretch_pct
max_feasible_review_tp_pct
ideal_review_tp_pct
ideal_review_tp_reason
ideal_review_tp_warning
tp_reason
tp_warning
noise_flag
wrong_tp_flag
review_bucket
```

### 7.2. Лестница по фазам

Файл:

```text
STAS3_V2_TP_LADDER_BY_PHASE.csv
```

Колонки:

```text
phase
rows
noise_rows
valid_rows
hit_0p3_rate
...
hit_1p0_rate
hit_2p0_rate
hit_3p0_rate
hit_10p0_rate
hit_20p0_rate
median_time_to_0p3
median_time_to_0p5
median_time_to_1p0
median_time_to_2p0
median_time_to_3p0
median_mae_before_base_tp
fast_tp_rows
medium_move_rows
medium_extension_rows
tp_min_pct
tp_base_pct
tp_stretch_pct
phase_decision
phase_decision_reason
```

`hit_20p0_rate` входит в рабочую V2-сетку. Если данных для таких уровней мало, значение не превращать в TP-вывод, а помечать решение как `INSUFFICIENT_DATA_REVIEW_ONLY`.

### 7.3. Пропущенные строки

Файл:

```text
STAS3_V2_SKIPPED_ROWS.csv
```

Назначение:

1. не терять строки, где нет цены входа;
2. явно видеть, если `context_before_entry_check` не `True`;
3. отделять технические пропуски от плохих входов.

### 7.4. Ошибки TP

Файл:

```text
STAS3_V2_WRONG_TP_REVIEW.csv
```

Назначение:

1. где механический `1%` был завышен;
2. где `0.3-0.5%` был слишком мал;
3. где вход был нормальный, но фазовый TP должен быть другим;
4. где вход был шумом и TP вообще нельзя обсуждать.

### 7.5. Отчет

Файл:

```text
STAS3_V2_REPORT_RU.md
```

В отчете должны быть:

1. таблица входов;
2. фаза рынка на момент входа;
3. фиксированная цена входа `entry_price_for_calc`;
4. фактическое движение в процентах от этой цены;
5. сессия, фон, LONG, `SHORT`-risk%, WAVE и волатильность рядом с каждой сделкой;
6. разделение быстрых TP и средних LONG-ходов;
7. `max_feasible_review_tp_pct` по каждой сделке;
8. `ideal_review_tp_pct` по каждой сделке как hindsight-review вывод;
9. какие проценты подходят для каких фаз;
10. первая версия процентной лестницы;
11. список запретов и ограничений.

## 8. Визуал V2

Нужны простые графики без иллюзии идеального выхода.

Разрешено рисовать:

1. `SIGNAL`;
2. `ENTRY` с подписью `entry_price_for_calc`;
3. горизонтальные уровни процентной сетки;
4. факт достижения TP как маленький маркер;
5. MAE как риск-маркер;
6. подпись `review-only`;
7. отдельные маркеры зон `FAST_TP` и `MEDIUM_MOVE`, если они не загромождают график.

Запрещено рисовать как основной слой:

1. зеленую стрелку до `MFE MAX`;
2. стрелку `low -> maximum`;
3. большую swing-сделку как будто она была заранее известна;
4. `MFE MAX` как `EXIT`.

Если `MFE MAX` нужен, он должен быть в отдельной диагностической вкладке/PNG с крупной пометкой:

```text
MFE MAX = hindsight fact, not TP
```

## 9. Критерии готовности Stas3 V2

Stas3 V2 готов, когда:

1. старые Stas3 V1 outputs не используются как source-of-truth;
2. новый run строится из выбранного Stas2 source;
3. все точки входа взяты из `STAS2_RECORDS.csv`, без поиска новых low;
4. для каждой строки есть `entry_price_for_calc` и источник цены;
5. все post-entry поля помечены как review;
6. быстрые TP и средние LONG-ходы разделены;
7. swing не оформлен как стратегия;
8. нет визуала, который продает максимум как выход;
9. есть таблица входов;
10. есть лестница по фазам;
11. есть wrong-TP/noise review;
12. есть русский отчет;
13. проверки проходят;
14. нет живых хвостов `python.exe`.

## 10. Следующий технический шаг

Не переписывать сразу торговую стратегию.

Следующий шаг только такой:

1. заморозить Stas3 V1 как архив;
2. создать новый скрипт/режим Stas3 V2 или отдельный флаг `--mode v2`;
3. сначала проверить контракт цены входа на выбранном Stas2 run;
4. убрать из основного V2-отчета `MFE MAX` как цель;
5. пересобрать таблицы вокруг фазовой достижимости процентов;
6. отдельно решить, нужен ли review-only join Stas2 `WAVE/GAP`.

После этого пользователь смотрит отчет и говорит:

```text
норм / фиксить / добавить WAVE-context / убрать лишнее
```
