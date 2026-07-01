# Block 01: price_volatility - ТЗ-аудит ручек калибровки

Дата UTC: `2026-06-11T10:51:00Z`.

Статус: `BLOCK_01_AUDIT_DRAFT`.

Это не запуск Optuna/APTuna. Это разбор блока перед правкой конфигов и перед новой калибровкой.

## Блок

Техническое имя:
`price_volatility`.

Русское название:
`Цена и волатильность`.

Смысл блока:
понять, насколько цена уже сдвинулась, насколько широкий текущий диапазон, какая сейчас волатильность и какой ATR-режим у рынка.

## Источники проверки

1. `configs/calibration_full_matrix_v1.yaml`
2. `configs/calibration_matrices/catalog_blocks/catalog_block_01_price_volatility.yaml`
3. `configs/features_block.yaml`
4. `src/mlbotnav/dataset.py`
5. `src/mlbotnav/optuna_search_candidate.py`
6. `src/mlbotnav/search_gate_candidate.py`
7. `src/mlbotnav/backtest.py`

## Что входит в Block 01

1. `ret_1` - изменение цены за короткое окно.
2. `ret_3` - изменение цены за окно x3.
3. `ret_6` - изменение цены за окно x6.
4. `ret_12` - изменение цены за окно x12.
5. `ret_24` - изменение цены за окно x24.
6. `hl_spread` - диапазон свечи high-low относительно open.
7. `rolling_std_20` - скользящая волатильность доходности.
8. `atr14` - ATR относительно цены.

## Что сейчас калибруется

### 1. ret_1 / ret_3 / ret_6 / ret_12 / ret_24

Тип:
фича движения цены.

Текущий расчет:
`src/mlbotnav/dataset.py` считает:

```text
ret_1  = close.pct_change(return_lookback)
ret_3  = close.pct_change(return_lookback * 3)
ret_6  = close.pct_change(return_lookback * 6)
ret_12 = close.pct_change(return_lookback * 12)
ret_24 = close.pct_change(return_lookback * 24)
```

Текущий калибруемый параметр:

```text
return_lookback: min=3, max=30, step=3, count=10
```

Что это значит:
сейчас калибруется окно расчета движения цены, но не отдельный порог силы сигнала.

Чего не хватает для signal-level калибровки:

1. Минимальный порог движения для LONG.
2. Минимальный порог движения для SHORT.
3. Порог сильного импульса.
4. Порог экстремального движения для mean-reversion сценария.
5. Правило: торгуем продолжение движения или откат после перегиба.

Предлагаемые ручки на согласование:

```text
ret_signal_threshold_long:  min=0.0005, max=0.01, step=0.0005
ret_signal_threshold_short: min=0.0005, max=0.01, step=0.0005
ret_extreme_threshold:      min=0.0020, max=0.03, step=0.0010
ret_confirm_bars:           min=1, max=5, step=1
```

LONG смысл:
если движение вверх достаточно сильное и волатильность разрешает вход, блок может подтверждать LONG.

SHORT смысл:
если движение вниз достаточно сильное и волатильность разрешает вход, блок может подтверждать SHORT.

Вопрос перед фиксацией:
делаем в Block 01 только momentum-сигнал или сразу добавляем отдельный reversion-сценарий после экстремального движения?

### 2. hl_spread

Тип:
фича диапазона свечи.

Текущий расчет:

```text
hl_spread = (high - low) / open
```

Текущий статус:
derived formula, отдельно не калибруется.

Что это значит:
значение считается, но у него нет своей ручки порога: какой диапазон считать слабым, нормальным или слишком широким.

Чего не хватает для signal-level калибровки:

1. Минимальный диапазон свечи для допуска входа.
2. Максимальный диапазон свечи, выше которого вход считается опасным.
3. Порог "широкая свеча/импульс".
4. Порог "узкая свеча/нет движения".

Предлагаемые ручки на согласование:

```text
hl_spread_min_threshold: min=0.0005, max=0.01, step=0.0005
hl_spread_max_threshold: min=0.0050, max=0.05, step=0.0025
hl_spread_impulse_threshold: min=0.0020, max=0.03, step=0.0010
```

Решение пока:
не менять расчет, но рассмотреть добавление порогов как фильтра входа.

### 3. rolling_std_20

Тип:
фича текущей волатильности.

Текущий расчет:

```text
rolling_std_20 = close.pct_change().rolling(rolling_window).std()
```

Текущий калибруемый параметр:

```text
rolling_window: min=20, max=180, step=20, count=9
```

Что это значит:
сейчас калибруется окно расчета волатильности, но не калибруются зоны волатильности.

Чего не хватает для signal-level калибровки:

1. Минимальная волатильность, ниже которой рынок мертвый.
2. Максимальная волатильность, выше которой вход опасный.
3. Порог сжатия перед импульсом.
4. Порог расширения волатильности после импульса.

Предлагаемые ручки на согласование:

```text
volatility_min_threshold:         min=0.0005, max=0.01, step=0.0005
volatility_max_threshold:         min=0.0050, max=0.05, step=0.0025
volatility_compression_threshold: min=0.0003, max=0.005, step=0.00025
volatility_expansion_threshold:   min=0.0010, max=0.02, step=0.0010
```

LONG/SHORT смысл:
направление сделки блок сам не задает, но разрешает или запрещает вход по режиму волатильности.

### 4. atr14

Тип:
ATR-волатильность и риск-режим.

Текущий расчет:

```text
atr14 = ATR(period_standard) / close
```

Текущий калибруемый параметр:

```text
period_standard: min=7, max=35, step=2, count=15
```

Что это значит:
сейчас калибруется период ATR, но не калибруется ATR-зона и ATR-множители для риска.

Чего не хватает для signal-level калибровки:

1. ATR min regime: рынок достаточно живой или нет.
2. ATR max regime: рынок слишком широкий или нет.
3. ATR multiplier для SL.
4. ATR multiplier для TP.
5. ATR breakout/impulse threshold.

Предлагаемые ручки на согласование:

```text
atr_min_threshold:        min=0.0005, max=0.01, step=0.0005
atr_max_threshold:        min=0.0050, max=0.05, step=0.0025
atr_sl_multiplier:        min=0.5, max=5.0, step=0.25
atr_tp_multiplier:        min=0.5, max=8.0, step=0.25
atr_impulse_threshold:    min=0.0010, max=0.03, step=0.0010
```

LONG/SHORT смысл:
ATR общий для обоих направлений. Он не говорит "лонг" или "шорт", но задает режим рынка, допустимый риск, стоп и цель.

## Главное замечание по Block 01

Сейчас блок в матрице в основном калибрует расчетные окна:

```text
return_lookback
rolling_window
period_standard
```

Но по твоей логике нам нужны еще signal-level ручки:

```text
насколько сильное движение считать сигналом
какая волатильность допустима
какой ATR-режим разрешает вход
где рынок мертвый
где рынок слишком опасный
```

Без этих ручек Block 01 считает фичи, но не полностью управляет качеством входа.

## Предварительное решение по Block 01

1. Оставить текущие расчетные ручки:
   `return_lookback`, `rolling_window`, `period_standard`.
2. Не калибровать сам `hl_spread` как формулу.
3. Добавить на согласование signal-level ручки:
   `ret_*` threshold, `hl_spread` threshold, volatility regime, ATR regime, ATR risk multipliers.
4. LONG и SHORT держать отдельно:
   LONG использует положительное движение/пробой вверх, SHORT использует отрицательное движение/пробой вниз.
5. Перед правкой конфигов нужно согласовать: Block 01 остается только фильтром режима или становится еще и самостоятельным источником momentum/reversion сигнала.

## Что фиксируем перед переходом к Block 02

Нужно принять решение по четырем пунктам:

1. Добавляем ли `ret_signal_threshold_long/short`.
2. Добавляем ли `hl_spread_min/max/impulse_threshold`.
3. Добавляем ли `volatility_min/max/compression/expansion_threshold`.
4. Добавляем ли `atr_min/max`, `atr_sl_multiplier`, `atr_tp_multiplier`, `atr_impulse_threshold`.

После фиксации этих решений можно переходить к:
`Block 02: trend_momentum`.

## Живой пример на графике

Дата UTC: `2026-06-11T11:02:00Z`.

Артефакты:

1. PNG: `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.png`
2. Readable: `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z_RU.md`
3. Machine: `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.json`

Источник:
`data/raw/bybit_ohlcv/dt=2026-06-01/tf=1m/symbol=SOLUSDT/part-final.csv`.

Параметры расчета из C001 Block 01 wide:

```text
return_lookback=18
rolling_window=40
period_standard=19
```

Что показано на графике:

1. Верхняя панель: свечи SOLUSDT 1m.
2. Вторая панель: `ret_1` и пример LONG/SHORT порогов.
3. Третья панель: `rolling_std_20` и допустимая зона волатильности.
4. Четвертая панель: `atr14` и `hl_spread`.

Конкретное действие на примере:

1. Если `ret_1` выше LONG-порога, а `rolling_std_20` и `atr14` находятся в допустимой зоне, Block 01 может дать `LONG_ALLOWED`.
2. Если `ret_1` ниже SHORT-порога, а `rolling_std_20` и `atr14` находятся в допустимой зоне, Block 01 может дать `SHORT_ALLOWED`.
3. Если волатильность/ATR ниже минимума, действие: `NO_TRADE_LOW_VOL`.
4. Если волатильность/ATR/hl_spread выше максимума, действие: `NO_TRADE_HIGH_RISK`.

Важно:
пороги на картинке являются примером signal-level ручек для согласования, а не текущей production-логикой.

## Переделка Block 01 под SHORT

Дата UTC: `2026-06-11T11:34:00Z`.

Артефакты:

1. PNG: `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.png`
2. Readable: `reports/qa_gate/block01_short_rework_chart_20260611T113400Z_RU.md`
3. Machine: `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.json`

Проблема первой визуализации:
локальный `ret_1 > 0` был подписан как `LONG-кандидат`, но по графику общий уклон цены был вниз. Значит, такой локальный рост нельзя автоматически считать LONG.

Правильная трактовка для SHORT:
если старшие окна блока показывают нисходящий фон, локальный рост является не LONG-сигналом, а откатом вверх внутри SHORT-контекста.

Что крутим для SHORT:

```text
return_lookback
rolling_window
period_standard
ret_down_context_threshold
ret_pullback_up_threshold
ret_short_confirm_threshold
confirm_bars
vol_min / vol_max
atr_min / atr_max
hl_spread_max
```

Логика `SHORT_AFTER_PULLBACK`:

```text
1. ret_6 или ret_12 ниже ret_down_context_threshold -> фон вниз.
2. ret_1 выше ret_pullback_up_threshold -> это откат вверх, не LONG.
3. В течение confirm_bars ret_1 снова ниже ret_short_confirm_threshold -> SHORT_ALLOWED.
4. rolling_std_20, atr14 и hl_spread должны быть в допустимой зоне риска.
```

Отдельная логика `SHORT_MOMENTUM`:

```text
1. ret_1 ниже отрицательного порога.
2. rolling_std_20, atr14 и hl_spread в допустимой зоне.
3. Действие: SHORT_ALLOWED без ожидания отката.
```

Решение на согласование:
Block 01 должен различать минимум два SHORT-сценария:

1. `SHORT_MOMENTUM` - прямое движение вниз.
2. `SHORT_AFTER_PULLBACK` - нисходящий фон + локальный откат вверх + подтверждение вниз.

## Карта диапазонов Block 01

Дата UTC: `2026-06-11T11:48:00Z`.

Это рабочая карта того, что именно крутим в Block 01. Здесь фиксируем не только названия ручек, но и "откуда-куда".

### A. Расчетные окна, уже есть в текущей матрице

```text
return_lookback: min=3, max=30, step=3
rolling_window:  min=20, max=180, step=20
period_standard: min=7, max=35, step=2
```

Смысл:

1. `return_lookback` - от какой прошлой свечи считаем изменение цены к текущей свече.
2. `rolling_window` - сколько свечей берем для режима волатильности.
3. `period_standard` - сколько свечей берем для ATR.

### B. Фон вверх / фон вниз

Фон не должен браться только из `ret_1`. Для фона используем старшие окна Block 01:

```text
ret_6
ret_12
ret_24
```

Как считается:

```text
ret_6  = close_now / close_(return_lookback * 6 bars ago) - 1
ret_12 = close_now / close_(return_lookback * 12 bars ago) - 1
ret_24 = close_now / close_(return_lookback * 24 bars ago) - 1
```

Что крутим:

```text
ret_context_source:
  values=[ret_6, ret_12, ret_24, ret_6_and_ret_12, ret_12_and_ret_24]

ret_down_context_threshold:
  min=-0.0200, max=-0.0010, step=0.0010

ret_up_context_threshold:
  min=0.0010, max=0.0200, step=0.0010
```

Смысл:

1. `ret_down_context_threshold` - насколько старшее окно должно быть ниже нуля, чтобы сказать "фон вниз".
2. `ret_up_context_threshold` - насколько старшее окно должно быть выше нуля, чтобы сказать "фон вверх".
3. `ret_context_source` - какой старший срез отвечает за фон.

### C. Откат

Откат - это движение против текущего фона.

Для SHORT:

```text
фон вниз + ret_1 вверх = откат вверх, не LONG
```

Для LONG:

```text
фон вверх + ret_1 вниз = откат вниз, не SHORT
```

Что крутим:

```text
ret_pullback_up_threshold:
  min=0.0005, max=0.0100, step=0.0005

ret_pullback_down_threshold:
  min=-0.0100, max=-0.0005, step=0.0005

pullback_min_bars:
  min=0, max=5, step=1

pullback_max_bars:
  min=1, max=30, step=1
```

Смысл:

1. `ret_pullback_up_threshold` - насколько цена должна отскочить вверх в падающем фоне.
2. `ret_pullback_down_threshold` - насколько цена должна откатить вниз в растущем фоне.
3. `pullback_min_bars` - минимальная длина отката.
4. `pullback_max_bars` - максимальная длина отката; если откат слишком долгий, старый сигнал отменяется.

### D. Подтверждение входа

Подтверждение - это момент, когда откат закончился и цена снова идет по направлению фона.

Для SHORT:

```text
фон вниз -> откат вверх -> ret_1 снова вниз -> SHORT_ALLOWED
```

Для LONG:

```text
фон вверх -> откат вниз -> ret_1 снова вверх -> LONG_ALLOWED
```

Что крутим:

```text
ret_short_confirm_threshold:
  min=-0.0100, max=-0.0005, step=0.0005

ret_long_confirm_threshold:
  min=0.0005, max=0.0100, step=0.0005

confirm_bars:
  min=0, max=12, step=1
```

Смысл:

1. `ret_short_confirm_threshold` - насколько `ret_1` должен уйти вниз после отката, чтобы разрешить SHORT.
2. `ret_long_confirm_threshold` - насколько `ret_1` должен уйти вверх после отката, чтобы разрешить LONG.
3. `confirm_bars=0` - подтверждение нужно на текущей свече.
4. `confirm_bars>0` - ждем подтверждение указанное количество свечей.

### E. Активность рынка: vol / ATR / hl_spread

Эти ручки отвечают за то, можно ли вообще входить.

```text
vol_min_threshold:
  min=0.0002, max=0.0030, step=0.0002

vol_max_threshold:
  min=0.0010, max=0.0200, step=0.0010

atr_min_threshold:
  min=0.0002, max=0.0030, step=0.0002

atr_max_threshold:
  min=0.0010, max=0.0200, step=0.0010

hl_spread_min_threshold:
  min=0.0000, max=0.0050, step=0.0005

hl_spread_max_threshold:
  min=0.0010, max=0.0300, step=0.0010
```

Ограничения:

```text
vol_min_threshold < vol_max_threshold
atr_min_threshold < atr_max_threshold
hl_spread_min_threshold < hl_spread_max_threshold
```

Смысл:

1. Ниже `vol_min_threshold` / `atr_min_threshold` рынок слишком мертвый.
2. Выше `vol_max_threshold` / `atr_max_threshold` рынок слишком рваный.
3. Выше `hl_spread_max_threshold` свеча слишком широкая для нормального входа.

### F. Куда "приземляться"

Точную цену цели должен уточнять `structure_ta`, потому что там уровни, диапазоны, FIBO, поддержка/сопротивление.

Но Block 01 может дать первичную цель по движению и ATR:

```text
target_bars:
  min=1, max=30, step=1

target_move_threshold:
  min=0.0010, max=0.0300, step=0.0010

atr_tp_multiplier:
  min=0.5, max=8.0, step=0.25

atr_sl_multiplier:
  min=0.5, max=5.0, step=0.25
```

Смысл:

1. `target_bars` - за сколько свечей ожидаем движение.
2. `target_move_threshold` - какое минимальное движение считаем достаточным.
3. `atr_tp_multiplier` - первичная цель через ATR.
4. `atr_sl_multiplier` - первичный риск через ATR.

### G. Итоговое решение по Block 01

Block 01 оставляем как самостоятельный блок "цена и волатильность", но расширяем его с расчетных окон до signal-level логики:

```text
окно расчета -> фон -> откат -> подтверждение -> активность рынка -> первичная цель/риск
```

Для SHORT основной сценарий:

```text
ret_6/ret_12/ret_24 показывает фон вниз
ret_1 отскакивает вверх
это считается откатом, а не LONG
в течение confirm_bars ret_1 снова уходит вниз
vol/ATR/hl_spread в допустимой зоне
действие: SHORT_ALLOWED
```

Для LONG зеркально:

```text
ret_6/ret_12/ret_24 показывает фон вверх
ret_1 откатывает вниз
это считается откатом, а не SHORT
в течение confirm_bars ret_1 снова уходит вверх
vol/ATR/hl_spread в допустимой зоне
действие: LONG_ALLOWED
```
