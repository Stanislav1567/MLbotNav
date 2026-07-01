# Handoff в новый чат: калибровочные блоки Optuna/APTuna

Дата UTC: `2026-06-19T00:00:00Z`.

Статус: `NEW_CHAT_HANDOFF`.

Причина:
старый чат слишком большой. В нем смешались ранние прогоны, аудиты, Block 01, графики, SHORT-логика и обсуждение внедрения. Новый чат должен начинаться от активных файлов проекта, а не от старой хронологии.

## Главное Правило

Работать строго в проекте:

```text
C:\Users\007\Desktop\MLbotNav
```

Источник истины для текущей работы:

```text
docs/CALIBRATION_NODE_CURRENT/README_RU.md
docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md
docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md
docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md
docs/CALIBRATION_NODE_CURRENT/TZ_INSTRUMENT_KNOBS_AUDIT_2026-06-11_RU.md
docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md
```

Старую хронологию, старые журналы и старые ТЗ не использовать как источник следующего шага. Они только архив.

## Текущий Режим Работы

Сейчас не запускаем Optuna/APTuna runtime и не правим конфиги.

Текущий режим:

```text
INSTRUMENT_KNOBS_AUDIT
```

Задача:
идти по 6 блокам, для каждого блока сделать паспорт:

```text
что входит
что уже крутится
что можно крутить
что не калибруется
какие min/max/step
какая LONG/SHORT логика
какие действия являются метками, а какие параметры реально калибруются
```

## Почему Не Идем 83 Фичи Руками

В проекте есть несколько уровней:

```text
6 блоков              большие смысловые корзины
83 feature rows       фичи/колонки внутри блоков
20 hypothesis rows    торговые идеи/гипотезы
38 parameter profiles уникальные типы ручек
~308 связей           где эти ручки используются фичами/гипотезами
```

Правильная работа:

```text
не 83 фичи отдельно
не 308 связей руками
а 6 паспортов блоков
```

Для каждого блока фиксируем только те ручки, которые реально влияют на сигнал.

## Очередь Блоков

```text
Block 01 price_volatility   Цена и волатильность
Block 02 trend_momentum     Тренд и импульс
Block 03 volume_flow        Объем и поток
Block 04 density_profile    Профиль плотности
Block 05 structure_ta       Структура ТА
Block 06 pattern            Паттерны
```

## Статусы Блоков

Использовать такие статусы:

```text
DRAFT             разбираем
AGREED            утвердили ТЗ
READY_FOR_CODE    можно передавать во внедрение
IMPLEMENTED       внедрено
VERIFIED          проверено
CLOSED            блок закрыт
```

Сейчас:

```text
Block 01 price_volatility = PARAMETER_RANGE_MAP_DRAFT
Block 02 trend_momentum   = NEXT_NOT_STARTED
```

## Block 01: Что Уже Сделано

Документ:

```text
docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md
```

Блок:

```text
price_volatility / Цена и волатильность
```

Входит:

```text
ret_1
ret_3
ret_6
ret_12
ret_24
hl_spread
rolling_std_20
atr14
```

Уже есть в текущей матрице:

```text
return_lookback: min=3, max=30, step=3
rolling_window:  min=20, max=180, step=20
period_standard: min=7, max=35, step=2
```

Важно:
`hl_spread` как формула не калибруется, но его пороги можно калибровать как signal-level фильтр.

## Block 01: Главное Решение

Block 01 должен быть не только расчетом окон, но и signal-level логикой:

```text
окно расчета -> фон -> откат -> подтверждение -> активность рынка -> первичная цель/риск
```

Действия не калибруются:

```text
фон вверх
фон вниз
откат
подтверждение
LONG_ALLOWED
SHORT_ALLOWED
NO_TRADE_LOW_VOL
NO_TRADE_HIGH_RISK
```

Калибруются числовые параметры, по которым эти действия определяются.

## Block 01: Карта Ручек

### A. Фон

```text
ret_context_source:
  values=[ret_6, ret_12, ret_24, ret_6_and_ret_12, ret_12_and_ret_24]

ret_down_context_threshold:
  min=-0.0200, max=-0.0010, step=0.0010

ret_up_context_threshold:
  min=0.0010, max=0.0200, step=0.0010
```

### B. Откат

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

### C. Подтверждение

```text
ret_short_confirm_threshold:
  min=-0.0100, max=-0.0005, step=0.0005

ret_long_confirm_threshold:
  min=0.0005, max=0.0100, step=0.0005

confirm_bars:
  min=0, max=12, step=1
```

### D. Активность Рынка

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

### E. Первичная Цель/Риск

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

Примечание:
точную цель по уровням должен уточнять `Block 05 structure_ta`, но Block 01 может дать первичный ATR/движение-контекст.

## Block 01: SHORT Логика

Проблема:
локальный `ret_1 > 0` внутри падающего фона нельзя автоматически считать LONG.

Нужно два SHORT-сценария:

```text
SHORT_MOMENTUM
SHORT_AFTER_PULLBACK
```

`SHORT_MOMENTUM`:

```text
ret_1 ниже отрицательного порога
vol/ATR/hl_spread в допустимой зоне
действие: SHORT_ALLOWED
```

`SHORT_AFTER_PULLBACK`:

```text
ret_6/ret_12/ret_24 показывает фон вниз
ret_1 отскакивает вверх
это считается откатом, а не LONG
в течение confirm_bars ret_1 снова уходит вниз
vol/ATR/hl_spread в допустимой зоне
действие: SHORT_ALLOWED
```

LONG зеркально:

```text
ret_6/ret_12/ret_24 показывает фон вверх
ret_1 откатывает вниз
это считается откатом, а не SHORT
в течение confirm_bars ret_1 снова уходит вверх
vol/ATR/hl_spread в допустимой зоне
действие: LONG_ALLOWED
```

## Визуальные Артефакты Block 01

Живой пример:

```text
reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.png
reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z_RU.md
reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.json
```

SHORT rework:

```text
reports/qa_gate/block01_short_rework_chart_20260611T113400Z.png
reports/qa_gate/block01_short_rework_chart_20260611T113400Z_RU.md
reports/qa_gate/block01_short_rework_chart_20260611T113400Z.json
```

Источник визуализации:

```text
data/raw/bybit_ohlcv/dt=2026-06-01/tf=1m/symbol=SOLUSDT/part-final.csv
```

Параметры визуализации из C001 wide:

```text
return_lookback=18
rolling_window=40
period_standard=19
```

## Что НЕ Делать В Новом Чате

Не делать:

```text
не запускать Optuna/APTuna runtime
не запускать C001 medium
не править конфиги
не править код
не брать задачи из старой хронологии
не смешивать внедрение и ТЗ-аудит
```

Пока задача нового чата:

```text
1. Открыть активные документы.
2. Восстановить статус.
3. Решить: Block 01 переводим в AGREED/READY_FOR_CODE или еще уточняем.
4. Если Block 01 согласован, перейти к Block 02 trend_momentum и сделать такой же паспорт.
```

## Отдельный Кодовый Чат

Если нужно внедрять Block 01 в Optuna/APTuna код, лучше открыть отдельный чат:

```text
Optuna/APTuna implementation: Block 01 price_volatility
```

Туда передавать только утвержденный пакет Block 01, без обсуждений и визуальных споров.

## Стартовое Сообщение Для Нового Чата

```text
Работаем строго в C:\Users\007\Desktop\MLbotNav.
Источник истины: docs/CALIBRATION_NODE_CURRENT.
Старую хронологию и старые журналы не использовать как источник задач.

Продолжаем ТЗ-аудит калибровочных блоков Optuna/APTuna.
Текущий режим: INSTRUMENT_KNOBS_AUDIT.
Runtime, C001 medium, forward, production, правки кода и конфигов пока не запускать.

Открой и прочитай:
1. docs/CALIBRATION_NODE_CURRENT/HANDOFF_TO_NEW_CHAT_2026-06-19_RU.md
2. docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md
3. docs/CALIBRATION_NODE_CURRENT/TZ_INSTRUMENT_KNOBS_AUDIT_2026-06-11_RU.md
4. docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md

Нужно восстановить статус коротко и продолжить строго по цепочке:
Block 01 price_volatility сейчас PARAMETER_RANGE_MAP_DRAFT.
Сначала решить, переводим ли Block 01 в AGREED/READY_FOR_CODE.
Если да, следующий блок: Block 02 trend_momentum / Тренд и импульс.
```
