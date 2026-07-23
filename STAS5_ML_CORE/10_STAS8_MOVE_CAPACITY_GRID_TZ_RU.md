# STAS8 MOVE CAPACITY GRID V1

Дата фиксации: `2026-07-22`.

Статус: `PASS_AUDIT_PREVIEW_R5_READY_NO_TRAINING_NO_DECISION_CHANGE`.

## Реализация 2026-07-22

Собран первый контур `STAS8_MOVE_CAPACITY_AUDIT_V1` как audit-preview поверх актуального R5 no-risk X463 forward. Обучение не запускалось, новый forward не запускался, исходный predictions CSV не изменялся.

```text
source_forward_run_id=stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1
range=2026-03-21..2026-03-27
rows=564
features=463
before STAS8: ENTER=61, WATCH=166, SKIP=337
preview after STAS8: ENTER=1, WATCH=20, SKIP=543
teacher_grid_rows=40608
png_count=7
guard=PASS_V5C_STAS8_MOVE_CAPACITY_AUDIT_V1_READY_NO_TRAINING_NO_DECISION_CHANGE
```

Артефакты:

```text
STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1/stas8_move_capacity_audit/v1
```

Вывод по качеству preview: текущие rule-пороги STAS8 слишком жесткие для боевого включения и требуют визуальной настройки. Это нормальный audit-результат, а не финальный фильтр.

## Назначение

`STAS8` фиксируется как будущий слой long-режима и емкости движения цены. Он не заменяет `ENTRY_BASELINE_ML` и не заменяет `RiskGate`.

Главная поправка:

```text
STAS8 не является фильтром "после точки потом был hit_1p2".
STAS8 сначала должен подтвердить, что рынок уже сейчас живой для long.
```

Для long-входа недостаточно увидеть будущий ход `1.1-1.2%` после LA-точки. Нужно, чтобы к моменту входа уже были видны волны вверх-вниз, диапазон, откат/retest/base/reclaim и отсутствие one-way dump.

## Train / Forward Рельса

Текущий порядок данных:

```text
Train после review:
2026-01-27..2026-03-20
= base32 2026-01-27..2026-02-27
+ R2 2026-02-28..2026-03-06
+ R3 2026-03-07..2026-03-13
+ R4 2026-03-14..2026-03-20

Blind forward / audit preview:
2026-03-21..2026-03-27
= R5, не обучение до ручного review пользователя
```

Правило: R2/R3/R4 можно использовать для обучения после approved review. R5 сначала только blind-forward/audit-preview. В обучение R5 попадает только после ручной проверки и approved review.

## Место В Цепочке

Будущая цепочка после отдельного согласования:

```text
STAS8_LIVE_MOVE_CONTEXT
   решает, можно ли вообще искать long

-> ENTRY_BASELINE_ML
   ищет local low / pullback

-> STAS8_MOVE_CAPACITY / MOVE_EDGE_ML
   проверяет потенциал хода 1.1-1.2%

-> RiskGate
   запрещает смертельно опасные режимы

-> будущий EXIT/TP слой
   решает, где закрываться
```

`STAS8` никогда не должен превращать `SKIP` в `ENTER`. Допустимые действия: оставить решение, понизить `ENTER` в `WATCH`, понизить `ENTER/WATCH` в `SKIP`, либо защитить хороший rebound.

## Два Слоя STAS8

### 1. STAS8_LIVE_MOVE_CONTEXT_V1

Live/no-future слой. Он отвечает на вопрос:

```text
Можно ли вообще искать long-входы сейчас?
```

Решения:

```text
ALLOW_ENTRY_SEARCH
WAIT_NO_MOVE
WAIT_WARMUP
BLOCK_DOWN_CHANNEL
BLOCK_WEAK_BOUNCE
BLOCK_HIGH_VOL_DANGER
```

Состояния long-search:

```text
LONG_SEARCH_OFF_NO_MOVE
LONG_SEARCH_OFF_DOWN_ONLY
LONG_SEARCH_OFF_WEAK_BOUNCE
LONG_SEARCH_WARMUP
LONG_SEARCH_ON_WAVES
LONG_SEARCH_ON_PULLBACK
LONG_SEARCH_ON_REBOUND
```

`ALLOW_ENTRY_SEARCH` разрешен только если одновременно:

```text
range_60m примерно >= 0.8..1.0%
или range_120m примерно >= 1.2..1.5%

есть движение вниз и затем живой отскок вверх
или есть несколько alternating swings вверх-вниз

bounce_from_recent_low_pct примерно >= 0.35..0.60%

есть grounding / retest / base_after_flush / reclaim

long_pressure уже не хуже short_pressure критически

точка не на позднем пампе и не у верхнего края без pullback

нет active_dump / falling_knife / support_breakdown hard-zone
```

`WAIT_WARMUP` ставится, если:

```text
диапазон начал расширяться, но есть только один импульс
после ножа появился первый отскок, но еще нет retest/base
short pressure еще высокий, но появились признаки exhaustion
цена улетела вверх, но не дала нормальный pullback
сигналы конфликтуют
```

`BLOCK_DOWN_CHANNEL` / `BLOCK_DOWN_ONLY` ставится, если:

```text
ret60/ret120/ret240 отрицательные в нескольких окнах
нисходящий канал или breakdown
много lower lows / lower highs
short_pressure >= 0.55 и заметно выше long_pressure
отскок слабый
нет grounding/retest/exhaustion/base_after_flush
```

`BLOCK_NO_VOLATILITY` ставится, если:

```text
range_60m примерно < 0.45..0.60%
range_120m примерно < 0.75..1.0%
нет swing-turns
нет нормального up-leg/down-leg
ATR/channel width сжаты
```

### 2. STAS8_TEACHER_MOVE_GRID_V1

Offline/audit teacher. Он отвечает на вопрос:

```text
Что реально случилось после LA-точки?
```

Тут можно смотреть future-свечи, но только для audit/target/обучения. Эти поля не являются live features.

## Процентная Сетка

Audit-grid:

```text
0.4% .. 5.0%  шаг 0.1
5.0% .. 10.0% шаг 0.2
```

Рабочие пороги для решений:

```text
1.1% = мягкий порог, WATCH / спорная зона
1.2% = основной минимальный ENTER-порог
1.5% = хороший ход
2.0%+ = сильный ход
5.0%+ = экстремальный spike/liquidation/news-like режим
```

Dense-сетка нужна как измерительный прибор. Ее нельзя превращать в десятки live-фичей `hit_*`.

## Offline Teacher Columns

Плановые teacher/audit поля:

```text
future_max_up_30m_pct
future_max_up_60m_pct
future_max_up_120m_pct
future_max_up_240m_pct

future_max_down_30m_pct
future_max_down_60m_pct
future_max_down_120m_pct
future_max_down_240m_pct

future_range_30m_pct
future_range_60m_pct
future_range_120m_pct
future_range_240m_pct

hit_0p5_y
hit_0p7_y
hit_1p0_y
hit_1p1_y
hit_1p2_y
hit_1p5_y
hit_2p0_y

time_to_1p0_min
time_to_1p1_min
time_to_1p2_min
time_to_1p5_min

mae_before_1p0_pct
mae_before_1p1_pct
mae_before_1p2_pct

first_post_entry_event
move_capacity_y
move_edge_y
move_capacity_bucket
move_capacity_reason
```

## Buckets

Плановые классы:

```text
NO_MOVE                 нет нормального хода
DEAD_FLAT               рынок почти стоит
LOW_MOVE_CHOP           мелкая пила, ход слабый
SMALL_EDGE_0P7          есть только слабый импульс
WORKING_EDGE_1P0        можно взять около 1%
MOVE_OK_1P1             мягкий рабочий ход
MOVE_OK_1P2             основной рабочий long-вход
STRONG_EDGE_1P5         хороший ход
HIGH_VOL_SAFE_PULLBACK  волатильность есть и откат рабочий
LOCAL_LOW_REBOUND_EDGE  локальный low + отскок, вход защищаем
POST_KNIFE_RETEST_EDGE  нож остановился, retest/отскок
HIGH_VOL_DANGER         волатильность есть, но это нож/слив
DOWN_WAVE_ACTIVE        активная волна вниз
DOWN_WAVE_EXHAUSTION    падение выдыхается, но вход еще рано
NO_MOVE_DOWN_CHANNEL    канал вниз без рабочего long-хода
DOWN_CHANNEL_WEAK_BOUNCE слабый отскок в шорте
LATE_PUMP_DEPENDENT     цель была слишком поздно
DANGER_THEN_LATE_RECOVERY сначала опасность, потом поздний recovery
SPIKE_EXTREME           свечи 5-10%, отдельный опасный режим
SPIKE_TRAP              вход на хаях/после пампа
```

## Planned Live Columns

Плановые live/no-future колонки:

```text
ENTRY_ML_LIVE_DECISION_BEFORE_STAS8
STAS8_LIVE_ACTION
STAS8_MOVE_CAPACITY_SCORE
STAS8_MOVE_EDGE_SCORE
STAS8_MOVE_CAPACITY_BUCKET
STAS8_MOVE_CAPACITY_DECISION
STAS8_MOVE_CAPACITY_ACTION
STAS8_MOVE_CAPACITY_REASON_TAGS
ENTRY_ML_LIVE_DECISION_AFTER_STAS8
RISKGATE_INPUT_DECISION
```

Действия:

```text
KEEP_ENTRY_DECISION
STAS8_WAIT_NO_MOVE
STAS8_WAIT_WARMUP
STAS8_WARN_DEMOTE_TO_WATCH
STAS8_BLOCK_TO_SKIP
STAS8_KEEP_REBOUND_PROTECTED
```

## Live No-Future Правило

В live нельзя знать будущий ход. `STAS8` в live может использовать только causal признаки, доступные не позже `entry_time_utc`.

Разрешенные группы X439/X463:

```text
cs_range_15m_pct
cs_range_60m_pct
cs_range_120m_pct
cs_return_60m_pct
cs_return_120m_pct
cs_atr_expansion_score
cs_last_candle_range_pct
session_so_far_range_pct
day_so_far_range_pct
fcs_channel_width_pct
fcs_channel_slope_pct_per_min
fcs_channel_position_0_1
cs_short_pressure_now
cs_long_pressure_now
cs_dump_acceleration_score
cs_pre_dump_risk_score
fcs_knife_risk_score
fcs_regime_score_active_dump
fcs_bounce_from_knife_low_pct
fcs_retest_after_knife_score
fcs_regime_changed_recently
bb20_width_pct
bb20_middle_slope_pct_per_min
bb20_position_0_1
```

Если используются phase/state, то только live prediction-колонки:

```text
phase_pred_label_live
phase_pred_conf_live
phase_prob_<class>_live
state_pred_label_live
state_pred_conf_live
```

Запрещено в live X:

```text
future_*
post_*
hit_*
mfe
mae
time_to_*
tp
exit
manual/review labels
entry_y
risk_bad_y
phase_y
state_y
reason_y
move_capacity_y
move_edge_y
любые свечи после entry_time_utc
```

Обязательный guard:

```text
stas8_live_source_max_time_utc <= entry_time_utc
teacher columns не входят в feature allowlist
STAS8 не превращает SKIP в ENTER
```

## Этапы От Начала До Конца

1. Зафиксировать это ТЗ и config.
2. Собрать `STAS8_MOVE_CAPACITY_AUDIT_V1` на готовом no-risk/no-Bollinger forward `2026-03-21..2026-03-27`, без обучения и без изменения decisions.
3. Нарисовать графики R5 с компактной полосой: `ALLOW`, `PAUSE`, `DOWN ONLY`, `NO VOL`, `MOVE 1.1`, `MOVE 1.2`, `MOVE 1.5`, `REBOUND OK`.
4. Визуально проверить дни `2026-03-26` и `2026-03-27`: убирает ли STAS8 мертвый down-channel и не убивает ли хорошие rebound/local low.
5. Настроить preview-пороги `range_60m`, `range_120m`, `bounce_from_low`, `short_pressure/long_pressure`, `channel_slope`, `wave turns`.
6. После visual OK сделать `STAS8_GUARD_V1`.
7. Собрать STAS8 train dataset только из base32 + approved R2/R3/R4.
8. Если preview доказал пользу, обучить отдельный `MOVE_EDGE_ML` с target из teacher grid и X только causal X439/X463 + live STAS8 context.
9. Встроить STAS8 между `ENTRY_BASELINE_ML` и `RiskGate`.
10. Сделать forward-сравнение: без STAS8, STAS8 preview, STAS8 enforce, STAS8 + RiskGate.
11. R5 добавлять в обучение только после ручного approved review.

## Граница

На `2026-07-22` это только ТЗ и config-закладка. Код STAS8, обучение, forward, датасеты и текущие predictions не меняются без отдельного OK пользователя.
