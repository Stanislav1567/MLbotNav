# Контракт рыночного события SOL

Версия контракта: `stas9_sol_event_v1`.

Статус: `DESIGN_READY_NO_EVENTS_WRITTEN`.

Режим подготовки: `SAFE / READ_ONLY` для исходных данных.

## 1. Назначение

Контракт описывает отдельное исследовательское событие рынка `SOLUSDT` на
таймфрейме `1m`. Единственный разрешённый источник свечей:

```text
C:\Users\007\Desktop\MLbotNav\data\core\bybit_ohlcv
```

Источник: Bybit, `market_type=linear`, `symbol=SOLUSDT`,
`timeframe=1m`, `contract_version=ohlcv_v1`.

Контракт отделяет три разные части:

1. причинный контекст и снимок признаков, доступные к моменту события;
2. будущее движение, вычисляемое только после события;
3. label, назначаемый только по отдельному утверждённому правилу.

Такое разделение обязательно для защиты от утечки будущего.

## 2. Обязательные технические поля

Помимо полей, заданных в ТЗ, каждая будущая карточка должна содержать:

| Поле | Тип | Правило |
|---|---|---|
| `schema_version` | string | Ровно `stas9_sol_event_v1` |
| `record_status` | enum | `CANDIDATE`, `SCHEMA_VALIDATED`, `OBSERVED`, `LABELED`, `REJECTED` |
| `event_type` | enum | Один из типов раздела 5 |

Шаблон или proposal не является наблюдением и не получает статус
`OBSERVED`.

## 3. Основные поля события

### `event_id`

Стабильный уникальный идентификатор.

Рекомендуемый формат:

```text
EVENT_SOLUSDT_1M_<YYYYMMDDTHHMMSSZ>_<EVENT_TYPE>_<SHORT_HASH>
```

`SHORT_HASH` формируется детерминированно из `symbol`, `timeframe`,
`timestamp`, `event_type` и версии detector contract. Повторный dry-run на
том же входе не должен создавать новый идентификатор.

### `symbol`

На текущем этапе допускается только:

```yaml
symbol: SOLUSDT
```

BTC и другие инструменты запрещены этим контрактом.

### `timeframe`

Строка, а не список:

```yaml
timeframe: 1m
```

### `timestamp`

Время открытия опорной свечи в UTC, соответствующее каноническому полю
`open_time_utc`.

Формат:

```text
YYYY-MM-DDTHH:MM:SSZ
```

### `context_before`

Описание причинного окна до события:

| Вложенное поле | Назначение |
|---|---|
| `unit` | Ровно `candles` |
| `count` | Число свечей в окне |
| `start_timestamp` | Время первой свечи окна |
| `end_timestamp` | Время последней свечи окна |
| `includes_anchor` | Включена ли опорная свеча |

Все свечи `context_before` должны иметь `open_time_utc <= timestamp`.

### `market_state`

Состояние рынка, вычисленное только на причинном окне:

| Вложенное поле | Пример допустимого значения |
|---|---|
| `trend_regime` | `UP`, `DOWN`, `FLAT`, `UNKNOWN` |
| `volatility_regime` | `LOW`, `NORMAL`, `HIGH`, `UNKNOWN` |
| `volume_regime` | `LOW`, `NORMAL`, `HIGH`, `UNKNOWN` |
| `structure_state` | `RANGE`, `TREND`, `TRANSITION`, `UNKNOWN` |
| `state_contract_version` | Версия правил состояния |

До утверждения формальных порогов значения остаются `UNKNOWN`.

### `features_snapshot`

Снимок признаков на момент события:

| Вложенное поле | Назначение |
|---|---|
| `as_of_timestamp` | Максимальное время данных, использованных в признаках |
| `feature_contract_version` | Версия feature contract или `PROPOSAL` |
| `values` | Словарь значений признаков |
| `missing_features` | Явный список отсутствующих значений |

`as_of_timestamp` не может быть позже `timestamp`. В `values` запрещено
помещать outcome, label или любые будущие свечи.

### `entry_type`

Исследовательская интерпретация события:

```text
OBSERVATION_ONLY
LONG_CANDIDATE
SHORT_CANDIDATE
NO_ENTRY
UNKNOWN
```

`entry_type` не является торговой командой и не разрешает live trading.

### `future_horizon`

Окно, на котором позднее оценивается исход:

| Вложенное поле | Назначение |
|---|---|
| `unit` | Ровно `candles` |
| `candles` | Число будущих минутных свечей |
| `starts_after_anchor` | Ровно `true` |
| `horizon_contract_version` | Версия правила горизонта |

Конкретные горизонты должны быть утверждены отдельным label/outcome
contract. На этапе proposal допускается `candles: null`.

### `outcome`

Результат будущего движения. Для нового кандидата:

```yaml
outcome:
  status: UNKNOWN
  future_return_pct: null
  max_favorable_excursion_pct: null
  max_adverse_excursion_pct: null
  resolved_at: null
  outcome_contract_version: PROPOSAL
```

Outcome вычисляется после фиксации события и никогда не переносится в
`features_snapshot`.

### `label`

Целевая метка. До утверждения label contract:

```yaml
label:
  status: UNLABELED
  value: null
  label_contract_version: PROPOSAL
  assigned_at: null
```

`UNKNOWN outcome` и `UNLABELED` являются нормальным состоянием кандидата.
Автоматически присваивать хороший/плохой вход запрещено.

### `lineage`

Происхождение события и версии правил:

| Вложенное поле | Назначение |
|---|---|
| `source_root` | Канонический разрешённый корень |
| `source_partition` | Относительный путь суточной партиции |
| `source_contract_version` | `ohlcv_v1` |
| `source_open_time_utc` | Исходный `open_time_utc` опорной свечи |
| `source_content_tree_sha256` | Отпечаток разрешённого source snapshot |
| `dq_status` | Результат проверки source gate |
| `detector_contract_version` | Версия правил detector |
| `detected_at` | Время, когда событие стало обнаружимым |
| `event_schema_version` | `stas9_sol_event_v1` |
| `created_by` | Профильная роль, например `STAS9_MARKET_RESEARCH` |

Для локальных экстремумов `detected_at` может быть позже `timestamp`, если
правило требует подтверждающих свечей. Эти свечи разрешены для подтверждения
факта события, но запрещены в `context_before` и `features_snapshot` на
момент `timestamp`.

## 4. Документальный шаблон

Ниже приведён только пример структуры. Он не является событием и не должен
сохраняться в `EVENTS/SOL` как наблюдение.

```yaml
schema_version: stas9_sol_event_v1
record_status: CANDIDATE
event_id: EVENT_SOLUSDT_1M_YYYYMMDDTHHMMSSZ_EVENT_TYPE_SHORT_HASH
event_type: EVENT_TYPE
symbol: SOLUSDT
timeframe: 1m
timestamp: YYYY-MM-DDTHH:MM:SSZ

context_before:
  unit: candles
  count: null
  start_timestamp: null
  end_timestamp: null
  includes_anchor: true

market_state:
  trend_regime: UNKNOWN
  volatility_regime: UNKNOWN
  volume_regime: UNKNOWN
  structure_state: UNKNOWN
  state_contract_version: PROPOSAL

features_snapshot:
  as_of_timestamp: YYYY-MM-DDTHH:MM:SSZ
  feature_contract_version: PROPOSAL
  values: {}
  missing_features: []

entry_type: UNKNOWN

future_horizon:
  unit: candles
  candles: null
  starts_after_anchor: true
  horizon_contract_version: PROPOSAL

outcome:
  status: UNKNOWN
  future_return_pct: null
  max_favorable_excursion_pct: null
  max_adverse_excursion_pct: null
  resolved_at: null
  outcome_contract_version: PROPOSAL

label:
  status: UNLABELED
  value: null
  label_contract_version: PROPOSAL
  assigned_at: null

lineage:
  source_root: C:/Users/007/Desktop/MLbotNav/data/core/bybit_ohlcv
  source_partition: null
  source_contract_version: ohlcv_v1
  source_open_time_utc: YYYY-MM-DDTHH:MM:SSZ
  source_content_tree_sha256: null
  dq_status: null
  detector_contract_version: PROPOSAL
  detected_at: null
  event_schema_version: stas9_sol_event_v1
  created_by: STAS9_MARKET_RESEARCH
```

## 5. Первые типы событий

| Русское название | `event_type` | Направление исследования |
|---|---|---|
| локальный минимум | `LOCAL_MINIMUM` | Опорный low относительно причинного окна; отдельно исследовать подтверждение |
| локальный максимум | `LOCAL_MAXIMUM` | Опорный high относительно причинного окна; отдельно исследовать подтверждение |
| импульс вверх | `UPWARD_IMPULSE` | Положительное движение за окно с расширением range/volume |
| импульс вниз | `DOWNWARD_IMPULSE` | Отрицательное движение за окно с расширением range/volume |
| пробой уровня | `LEVEL_BREAKOUT` | Закрепление цены за ранее сформированным уровнем |
| ложный пробой | `FALSE_BREAKOUT` | Выход за уровень с возвратом внутрь; требует будущего подтверждения |
| резкий рост объёма | `VOLUME_SPIKE` | Объём относительно только предыдущего причинного baseline |
| расширение волатильности | `VOLATILITY_EXPANSION` | Рост true range/realized volatility относительно прошлого режима |
| разворот | `REVERSAL` | Смена направления после экстремума/импульса с подтверждением структуры |

Пороговые значения намеренно не зафиксированы: сначала требуется
read-only исследование распределений на канонических данных SOL.

## 6. Правила валидации

Карточка проходит schema validation только если:

1. присутствуют все обязательные поля;
2. `symbol=SOLUSDT`, `timeframe=1m`, источник находится строго внутри
   разрешённого корня;
3. timestamp существует в каноническом OHLCV и совпадает с
   `source_open_time_utc`;
4. причинный контекст отсортирован, не содержит дублей и будущих свечей;
5. OHLCV исходного окна проходит базовые инварианты;
6. `features_snapshot.as_of_timestamp <= timestamp`;
7. outcome и label отделены от признаков;
8. `UNKNOWN/UNLABELED` не интерпретируются как отрицательный класс;
9. lineage содержит версии source, detector и event schema;
10. событие не записывается при ошибке source gate или schema validation.

## 7. Граница текущего этапа

Контракт создан, но detector thresholds, feature contract, outcome contract
и label contract ещё не утверждены. Реальные event YAML, dataset, split,
обучение и Optuna на этом этапе не создаются и не запускаются.
