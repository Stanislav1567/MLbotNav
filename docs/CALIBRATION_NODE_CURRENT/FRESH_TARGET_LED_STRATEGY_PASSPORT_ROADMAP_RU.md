# Fresh Target-Led Strategy Passport Roadmap

Дата фиксации: `2026-07-01`.

Статус: `ACTIVE_EXISTING_PASSPORT_RECONCILIATION_AND_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA`.

## Главная фиксация

Паспорта уже собраны по полочкам. Сейчас задача не создавать их заново, а сверить существующие связки и наложить активные паспортные стратегии на два ручных эталона.

Текущий путь:

```text
сверка существующего registry manifest
-> контроль связок Bxxx -> Fxxx -> passport MD -> matrix YAML -> runtime action
-> два эталона входов 19 + 7
-> full-day strategy/passport overlay
-> локальные strategy squares внутри дня
-> визуальный разбор, какие паспорта объясняют входы
-> summary matrix по входам и блокам
-> только потом выбор рабочего кластера/паспорта
-> scorer/target-lock только после user review
-> Optuna/ML только после отдельных разрешений
```

Старые V7/V8/V9/V10/V11, старые Optuna-переборы и старая хронология не являются очередью задач.

## Агентский аудит

Подключенный агент: `Lorentz`.

Результат аудита только чтением:

1. В `configs/calibration_action_passports.yaml` есть `26` блоков `B001..B026`.
2. Активных не отключенных `Fxxx`-паспортов: `82`.
3. Активных matrix YAML в `configs/calibration_matrices/passport_actions`: `82`.
4. У всех активных связок `passport_path` и `active_matrix_path` файл найден.
5. `B001_RET_N_TOURNAMENT` есть в реестре, но имеет статус `diagnostic_only_disabled_for_baseline`; в overlay его не брать.

Manifest-сверка:

```text
docs/CALIBRATION_NODE_CURRENT/PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md
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

Эти `26` входов являются текущей ручной базой для strategy/passport overlay. Их не двигаем и не заменяем без нового решения пользователя.

## Что уже выяснено

`INDICATOR_HYPOTHESIS_REVIEW_V1` визуально норм как evidence-layer, но не является стратегическим паспортным слоем.

Проблема V1:

1. `Fibo` на V1 рисуется по локальному zoom min/max, а не по strict passport anchors.
2. `BOS/Swing` на V1 являются rolling-подсказками, а не `F045-F052_ALLOW`.
3. `RSI/MACD/Volume` видны линиями, но не как паспортные `ALLOW 1/0`.
4. Нет таблицы `target_id -> какие паспорта поддержали вход`.
5. Нет локальных strategy squares: где конкретная стратегия должна работать, а где весь день не трогать.

Аудит пропуска:

```text
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_STRATEGY_PASSPORT_GAP_AUDIT_20260701_RU.md
```

## Пункт 1. V2A0 Registry Reconciliation

Название шага:

```text
V2A0_REGISTRY_RECONCILIATION_NO_SCORER_NO_ML_NO_OPTUNA
```

Смысл: сверить уже существующие паспорта, а не создавать новые.

Источники:

```text
configs/calibration_action_passports.yaml
docs/CALIBRATION_NODE_CURRENT/passports/features/*.md
configs/calibration_matrices/passport_actions/*.yaml
```

Что фиксируем:

1. `Bxxx` block id.
2. `Fxxx` passport id.
3. `action_id`.
4. `passport_path`.
5. `active_matrix_path`.
6. `runtime action column` или способ расчета `ALLOW`.
7. статус для overlay: `active`, `muted/context`, `deferred`, `unsafe_for_entry`.

Паспорт нельзя применять в overlay, если неясно, как он считается без будущих данных.

## Блоки паспортов по реестру

| block | group | active F/action count | overlay role |
|---|---|---:|---|
| `B001-B004` | price/volatility | `8` | контекст волатильности, не первый active layer |
| `B005` | EMA | `3` | reference/deferred, не active condition |
| `B006-B009` | momentum | `6` | momentum layer после структуры и flow |
| `B010-B013`, `B026` | volume/density/VWAP | `16` | flow/density layer |
| `B014-B018` | structure/Fibo/retest/BOS | `18` | первый active strategy layer; `B016` muted/context-only |
| `B019-B024` | candle/divergence/chart patterns | `29` | pattern layer позже, после no-lookahead проверки events |
| `B025` | pattern trade context | `2` | unsafe/context-only из-за SL/TP риска |

Детальная таблица:

```text
docs/CALIBRATION_NODE_CURRENT/PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md
```

## Пункт 2. Strategy/passport overlay на два эталона

Следующий рабочий артефакт:

```text
INDICATOR_HYPOTHESIS_REVIEW_V2_STRATEGY_PASSPORT_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA
```

Цель V2: не найти новую стратегию по доходности, а посмотреть, какие уже созданные паспорта объясняют ручные входы `19+7`.

V2 должен дать:

1. full-day PNG по `2026-05-14` и `2026-05-15`;
2. локальные zoom/sheet по входам;
3. CSV/JSON matrix `target_id -> passport hits`;
4. RU-аудит: какие блоки реально помогают, какие шумят, какие пока не готовы.

## Что значит "квадрат стратегии"

Full-day график остается картой дня. Стратегия не должна гореть весь день сплошным фоном.

Квадрат стратегии = локальный рабочий участок внутри full-day:

```text
left_context до signal
-> signal close
-> entry next open
-> правая зона только для визуальной проверки
```

Правила квадрата:

1. условия считаются только слева, до закрытой signal-свечи включительно;
2. entry-свеча не используется для выбора;
3. правый участок нужен только для visual review, не как feature;
4. каждый паспорт использует свое паспортное окно:
   - `B013` VPOC: 60/240;
   - `B014` levels/range/channel: 120/240;
   - `B015` Fibo: `last_confirmed_alternating_pivot_pair`, а не zoom min/max;
   - `B017` breakout/retest: breakout event memory + retest window;
   - `B018` BOS/CHOCH: internal/external structure scope;
   - `B019-B024` pattern: отдельное pattern event window;
5. на full-day графике показываем карту участков, а подробности смотрим в zoom/sheet.

Если паспорт светится по всему дню, это не подтверждение стратегии, а шумовой флаг.

## Порядок V2, чтобы не сделать кашу

### V2A0. Registry Reconciliation

```text
B001..B026
F001..F083 active/non-disabled = 82
```

Выход: manifest-таблица и список overlay roles.

### V2A. Structure Layer

Первый активный visual overlay:

```text
B014 LEVEL/RANGE/CHANNEL
B015 FIBONACCI_GRID
B017 BREAKOUT_RETEST
B018 MARKET_STRUCTURE BOS/CHOCH
```

`B016 ENTRY_QUALITY_CONTEXT` можно показывать только muted/context-only, потому что там есть TP/SL/RR-риск.

Что показать:

1. support/resistance/range/channel;
2. strict Fibo anchors и уровни `0.382/0.618`;
3. breakout/retest/swing event;
4. BOS/CHOCH;
5. по каждому ручному входу: `support / conflict / silent`.

### V2B. Flow And Density Layer

После V2A:

```text
B010 VOLUME
B013 DENSITY/VPOC
B026 VWAP
```

Позже при необходимости:

```text
B011 OBV
B012 MFI
```

Что показать:

1. volume spike/low;
2. volume z-score;
3. VPOC 60/240;
4. distance/share/drift/cluster ratio;
5. VWAP distance;
6. где вход стоит около ликвидной зоны, а где нет.

### V2C. Momentum Layer

После V2B:

```text
B006 RSI
B007 MACD
```

`B005 EMA` пока reference/deferred и не является active condition.

`B008 ADX` и `B009 Stochastic` не первый слой; можно добавить позже, если структура/flow не дают достаточного объяснения.

### V2D. Pattern Layer

После no-lookahead проверки pattern events:

```text
B019 Candle patterns
B020 Divergence patterns
B021 Pattern quality
B022 Chart patterns
B023 Pattern confirmation
B024 Pattern composite entry
```

`B025 Pattern trade context` не брать как active entry layer без отдельного решения из-за SL/TP-context риска.

### V2E. Summary Matrix

После V2A/V2B/V2C/V2D:

```text
target_id
-> entry type
-> structure support/conflict/silent
-> flow support/conflict/silent
-> momentum support/conflict/silent
-> pattern support/conflict/silent
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

1. стратегия горит весь день, а не локальными участками;
2. стратегия объясняет хорошие входы, но так же объясняет весь шум;
3. strict Fibo/BOS/retest не совпадают с ручными входами;
4. overlay потерял ручные входы или сдвинул их без решения пользователя;
5. в один слой смешаны unrelated blocks.

## Что считаем хорошим результатом

Хороший результат V2:

1. видно, какие паспорта реально поддерживают `M01..M19` и 7 T15;
2. видно, какие паспорта не работают на этих входах;
3. видно, какие стратегии должны работать только локальными squares;
4. появился список 2-4 похожих входов под первый рабочий паспорт;
5. стало понятно, что можно отдавать в паспорт-контракт, а что нет.

## Следующий конкретный шаг

Сначала закрыть:

```text
V2A0_REGISTRY_RECONCILIATION_NO_SCORER_NO_ML_NO_OPTUNA
```

Потом собрать:

```text
V2A_STRUCTURE_LAYER
```

Только после просмотра V2A пользователем двигаться к V2B/V2C/V2D.
