# Fresh Target-Led Strategy Passport Roadmap

Дата фиксации: `2026-07-01`.

Статус: `ACTIVE_STRATEGY_PASSPORT_ROADMAP_NO_SCORER_NO_ML_NO_OPTUNA`.

## Главная фиксация

Мы не продолжаем старую кашу из runner-цепочек, старых V7/V8/V9/V10/V11, старых Optuna-переборов и старой хронологии.

Текущий путь:

```text
инвентаризация паспортов по блокам
-> проверка, какие паспорта реально есть в MD/YAML/runtime
-> два эталона входов 19 + 7
-> strategy/passport overlay квадратами
-> визуальный разбор, какие стратегии объясняют входы
-> только потом выбор рабочего кластера/паспорта
-> scorer/target-lock только после user review
-> Optuna/ML только после отдельных разрешений
```

## Текущие эталоны

Эталон 1:

```text
SOLUSDT 1m 2026-05-14
ручные входы: M01..M19
```

Главный ledger:

```text
reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json
```

Эталон 2:

```text
SOLUSDT 1m 2026-05-15
ручные входы: T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16
```

Главный ledger:

```text
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.json
```

Эти 26 входов являются текущей ручной базой для strategy/passport overlay. Их не двигаем и не заменяем без нового решения пользователя.

## Что уже выяснено

`INDICATOR_HYPOTHESIS_REVIEW_V1` визуально норм как evidence-layer, но не является стратегическим паспортным слоем.

Проблема V1:

1. `Fibo` на V1 рисуется по локальному zoom min/max, а не по strict passport anchors.
2. `BOS/Swing` на V1 являются rolling-подсказками, а не `F045-F052_ALLOW`.
3. `RSI/MACD/Volume` видны линиями, но не как паспортные `ALLOW 1/0`.
4. Нет таблицы `target_id -> какие паспорта поддержали вход`.
5. Нет квадратов стратегии: где конкретная стратегия должна работать, а где весь день не трогать.

Аудит пропуска:

```text
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_STRATEGY_PASSPORT_GAP_AUDIT_20260701_RU.md
```

## Пункт 1. Разложить паспорта по полочкам

Источник реестра:

```text
configs/calibration_action_passports.yaml
```

Источник паспортов:

```text
docs/CALIBRATION_NODE_CURRENT/passports/features/*.md
```

Источник исполняемых матриц:

```text
configs/calibration_matrices/passport_actions/*.yaml
```

Текущие найденные количества:

| слой | count | смысл |
|---|---:|---|
| feature passport MD | 27 | человекочитаемые паспорта |
| action matrix YAML | 82 | исполняемые action-матрицы |

Задача инвентаризации:

1. составить таблицу `Bxxx -> Fxxx -> passport MD -> matrix YAML -> runtime action column`;
2. отдельно отметить, какие паспорта полностью готовы;
3. отдельно отметить, какие есть в матрицах, но требуют проверки MD/реестра/runtime;
4. не применять паспорт в overlay, если он не найден в реестре или неясно, как считать `ALLOW`.

## Блоки паспортов по реестру

| block | block_key | name_ru | что это для нас сейчас |
|---|---|---|---|
| `B001` | `price_volatility` | Цена и волатильность | архив/контекст, не первый слой V2 |
| `B002` | `price_volatility` | Диапазон свечи High-Low | контекст свечи |
| `B003` | `price_volatility` | Скользящая волатильность 20 | контекст волатильности |
| `B004` | `price_volatility` | ATR14 волатильность | контекст волатильности |
| `B005` | `trend_momentum` | EMA тренд и наклон | пока reference/deferred, не active condition |
| `B006` | `trend_momentum` | RSI14 impulse | momentum layer |
| `B007` | `trend_momentum` | MACD импульс | momentum layer |
| `B008` | `trend_momentum` | ADX14 сила тренда | позже, не первый проход |
| `B009` | `trend_momentum` | Stochastic 14 K/D | позже, не первый проход |
| `B010` | `volume_flow` | Объем и поток | flow layer |
| `B011` | `volume_flow` | OBV slope 5 | flow/context, позже |
| `B012` | `volume_flow` | MFI14 | flow/context, позже |
| `B013` | `density_profile` | DENSITY_A VPOC core | density/VPOC layer |
| `B014` | `structure_ta` | LEVEL_A уровни поддержки/сопротивления | structure layer |
| `B015` | `structure_ta` | FIBONACCI_GRID anchor grid | strict Fibo layer |
| `B016` | `structure_ta` | ENTRY_QUALITY_CONTEXT | context-only, не как входной сигнал |
| `B017` | `structure_ta` | BREAKOUT_RETEST пробой/ретест | retest/swing layer |
| `B018` | `structure_ta` | MARKET_STRUCTURE BOS/CHOCH | BOS/CHOCH layer |
| `B019` | `pattern` | CANDLE_PATTERNS свечные паттерны | позже, отдельный pattern layer |
| `B020` | `pattern` | DIVERGENCE_PATTERNS дивергенции | позже, отдельный pattern layer |
| `B021` | `pattern` | PATTERN_QUALITY качество паттерна | позже |
| `B022` | `pattern` | CHART_PATTERNS графические паттерны | позже |
| `B023` | `pattern` | PATTERN_CONFIRMATION | позже |
| `B024` | `pattern` | PATTERN_COMPOSITE_ENTRY | позже |
| `B025` | `pattern` | PATTERN_TRADE_CONTEXT | позже, осторожно из-за TP/SL контекста |
| `B026` | `volume_flow` | VWAP distance | flow/context, позже |

## Пункт 2. Strategy/passport overlay на два эталона

Следующий рабочий артефакт:

```text
INDICATOR_HYPOTHESIS_REVIEW_V2_STRATEGY_PASSPORT_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA
```

Цель V2: не найти новую стратегию по доходности, а посмотреть, какие уже созданные паспорта объясняют ручные входы.

V2 должен дать:

1. PNG для глаз по `2026-05-14` и `2026-05-15`;
2. zoom/sheet по входам;
3. CSV/JSON matrix `target_id -> passport hits`;
4. RU-аудит: какие блоки реально помогают, какие шумят, какие пока не готовы.

## Что значит "квадрат стратегии"

Стратегия не должна отрабатывать весь день сплошным фоном.

Квадрат стратегии = локальный рабочий участок вокруг ручного входа:

```text
left_context до signal
-> signal close
-> entry next open
-> визуальная зона проверки справа только для глаз
```

Правила квадрата:

1. условия считаются только слева, до закрытой signal-свечи включительно;
2. entry-свеча не используется для выбора;
3. правый участок нужен только для визуального review, не как feature;
4. каждый паспорт использует свое паспортное окно:
   - `B013` VPOC: 60/240;
   - `B014` levels/range/channel: 120/240;
   - `B015` Fibo: last confirmed alternating pivot pair, lookback до 240;
   - `B017` breakout/retest: event memory и retest window;
   - `B018` BOS/CHOCH: internal/external structure scope;
5. на full-day графике показываем только метки квадратов, а подробности смотрим в zoom/sheet.

## Порядок V2, чтобы не сделать кашу

### V2A. Structure Layer

Сначала делаем только структурные блоки:

```text
B014 LEVEL/RANGE/CHANNEL
B015 FIBONACCI_GRID
B017 BREAKOUT_RETEST
B018 MARKET_STRUCTURE BOS/CHOCH
```

Что показать:

1. support/resistance/range/channel;
2. strict Fibo anchors и уровни `0.382/0.618`;
3. retest/swing break event;
4. BOS/CHOCH;
5. по каждому ручному входу: поддержало / против / молчит.

### V2B. Flow Layer

После V2A:

```text
B010 VOLUME
B013 DENSITY/VPOC
```

Что показать:

1. volume spike/low;
2. volume z-score;
3. VPOC 60/240;
4. distance/share/drift/cluster ratio;
5. где вход стоит около ликвидной зоны, а где нет.

### V2C. Momentum Layer

После V2B:

```text
B006 RSI
B007 MACD
```

Что показать:

1. RSI как паспортный allow, не просто линию;
2. MACD line/signal/hist как passport allow;
3. где momentum помогает, а где вводит в шум.

### V2D. Summary Matrix

После V2A/V2B/V2C:

```text
target_id
-> entry type
-> structure hits
-> flow hits
-> momentum hits
-> conflict flags
-> preliminary cluster note
```

Это еще не scorer. Это карта совпадений стратегий с ручными входами.

## Что запрещено

До отдельного решения пользователя запрещено:

1. scorer;
2. target-lock;
3. Optuna;
4. ML/export/promotion;
5. future return;
6. TP/SL для выбора входа;
7. MFE/MAE для выбора входа;
8. OHLCV entry-свечи для выбора входа;
9. использовать entry price как feature;
10. смешивать все паспорта в один общий сигнал.

## Что считаем плохим результатом

Плохой результат V2:

1. стратегия горит весь день, а не квадратами;
2. стратегия объясняет хорошие входы, но так же объясняет весь шум;
3. strict Fibo/BOS/retest не совпадают с ручными входами;
4. overlay потерял ручные входы или сдвинул их без решения пользователя;
5. в один слой смешаны unrelated blocks.

## Что считаем хорошим результатом

Хороший результат V2:

1. видно, какие паспорта реально поддерживают `M01..M19` и 7 T15;
2. видно, какие паспорта не работают на этих входах;
3. видно, какие стратегии должны работать только квадратами;
4. появился список 2-4 похожих входов под первый рабочий паспорт;
5. стало понятно, что можно отдавать в паспорт-контракт, а что нет.

## Следующий конкретный шаг

Сначала сделать паспортную инвентаризацию:

```text
PASSPORT_BLOCK_INVENTORY_V0_NO_SCORER_NO_ML_NO_OPTUNA
```

Потом собрать:

```text
V2A_STRUCTURE_LAYER
```

Только после просмотра V2A пользователем двигаться к V2B/V2C.
