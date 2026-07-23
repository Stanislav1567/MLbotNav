# События SOLUSDT 1m

Статус: `EMPTY_READY_FOR_FUTURE_VALIDATED_EVENTS`.

Этот каталог зарезервирован для будущих отдельных карточек событий
`SOLUSDT`, построенных только по каноническому источнику:

```text
C:\Users\007\Desktop\MLbotNav\data\core\bybit_ohlcv
```

Текущий этап не создаёт реальных событий. Наличие только этого README
означает, что каталог подготовлен, но наблюдения ещё не записывались.

## Допуск карточки

Будущий YAML допускается в каталог только после:

1. проверки source root, `symbol=SOLUSDT`, `timeframe=1m` и
   `contract_version=ohlcv_v1`;
2. формирования события по версионированному detector contract;
3. проверки по `MARKET_KNOWLEDGE/EVENT_SCHEMA_RU.md`;
4. подтверждения отсутствия future leakage в `context_before` и
   `features_snapshot`;
5. заполнения lineage;
6. сохранения outcome как `UNKNOWN` и label как `UNLABELED`, пока отдельные
   правила результата и разметки не утверждены.

## Имя файла

```text
<event_id>.yaml
```

Пример формата идентификатора:

```text
EVENT_SOLUSDT_1M_20260126T000000Z_LOCAL_MINIMUM_A1B2C3
```

Один файл содержит ровно одно событие. Файлы исходных свечей не копируются.

## Запреты

- не сохранять proposal как наблюдение;
- не переносить будущие значения в признаки;
- не создавать dataset из непроверенных карточек;
- не использовать BTC или другой source root;
- не менять исходные CSV;
- не запускать обучение, Optuna, forward или live trading.

Родительский `EVENTS/EVENT_SOL_000001.yaml` остаётся старым
`TEMPLATE_NOT_OBSERVED` и не является карточкой нового контракта.
