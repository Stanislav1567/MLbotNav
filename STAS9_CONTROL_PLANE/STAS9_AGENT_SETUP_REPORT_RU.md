# Отчёт о настройке ролей агентов STAS9 и подготовке контура SOL

Статус:
`PASS_STAS9_AGENT_ROUTING_SOL_ML_PREPARATION_SAFE_NO_TRAINING`.

Дата: `2026-07-23`.

## 1. Результат

В `STAS9_CONTROL_PLANE` создана явная система распределения обязанностей.
`STAS9_SENTINEL` остаётся единственной пользовательской точкой входа и
руководителем процесса, но специализированную работу передаёт профильным
агентам.

Рабочая схема:

```text
Пользователь
  -> STAS9_SENTINEL
  -> TASK_ROUTER
     -> STAS9_AUDITOR
     -> STAS9_MARKET_RESEARCH
     -> STAS9_FEATURE_MANAGER
     -> STAS9_MODEL_MANAGER
     -> STAS9_VALIDATOR
     -> STAS9_GUARDIAN
     -> STAS9_LAB (только вспомогательные подтверждённые эксперименты)
  -> STAS9_CONTROL_PLANE
```

`STAS9_SENTINEL` теперь явно отвечает за классификацию, делегирование,
контроль, память и итоговый отчёт. Он не создаёт признаки, не исследует свечи
вместо профильного агента, не обучает модели и не меняет ML-ядро.

## 2. Существующие агенты

| Агент | Ответственность | Запуск и доступ |
|---|---|---|
| `STAS9_SENTINEL` | маршрутизация, контроль, память, итоговый отчёт | `PRIMARY_ONLY`, `SAFE` |
| `STAS9_AUDITOR` | структура, файлы, дубли, состояние данных | `ON_DEMAND`, `READ_ONLY` |
| `STAS9_MARKET_RESEARCH` | свечи, закономерности, движение и события SOL | `ON_DEMAND`, `READ_ONLY`, `SOL_ONLY` |
| `STAS9_FEATURE_MANAGER` | технические признаки, свечные паттерны, события в признаки, feature contracts | `ON_DEMAND`, `READ_ONLY` |
| `STAS9_MODEL_MANAGER` | версии, связь моделей и признаков, метрики, champion/candidate | `ON_DEMAND`, `READ_ONLY` |
| `STAS9_VALIDATOR` | качество, сравнение, переобучение, утечки и целостность | `ON_DEMAND`, `READ_ONLY` |
| `STAS9_GUARDIAN` | безопасность, режимы, доступы и блокировка опасных действий | `ON_DEMAND`, `READ_ONLY` |
| `STAS9_LAB` | планы и анализ только явно подтверждённых экспериментов | `ON_DEMAND`, требует `EXPERIMENT` |

`STAS9_LAB` сохранён для совместимости и не заменяет
`STAS9_MARKET_RESEARCH` при работе с SOL.

## 3. Документы ролей

Создан каталог `AGENT_ROLES/`:

```text
SENTINEL_ROLE_RU.md
AUDITOR_ROLE_RU.md
FEATURE_MANAGER_ROLE_RU.md
MARKET_RESEARCH_ROLE_RU.md
MODEL_MANAGER_ROLE_RU.md
VALIDATOR_ROLE_RU.md
GUARDIAN_ROLE_RU.md
```

Новый агент `STAS9_MARKET_RESEARCH` оформлен в стандартной структуре:

```text
STAS9_AGENTS/STAS9_MARKET_RESEARCH/
  README_RU.md
  ROLE_RU.md
  CONFIG.yaml
  PERMISSIONS.yaml
```

## 4. Маршрутизация задач

Человекочитаемый маршрутизатор:
`STAS9_CONTROL_PLANE/TASK_ROUTER_RU.md`.

Машинный маршрутизатор:
`STAS9_INTERFACE/COMMANDS/COMMAND_ROUTING.yaml`.

Основные маршруты:

| Задача | Исполнитель |
|---|---|
| Изучить свечи, закономерности и движение SOL | `STAS9_MARKET_RESEARCH` |
| Сохранить проверенное событие SOL | `STAS9_MARKET_RESEARCH`, затем `STAS9_VALIDATOR` |
| Создать признаки или feature contract | `STAS9_FEATURE_MANAGER`, затем `STAS9_VALIDATOR` |
| Проверить качество или переобучение | `STAS9_VALIDATOR` |
| Проверить структуру, файлы, дубли и данные | `STAS9_AUDITOR` |
| Проверить версии, метрики или champion/candidate | `STAS9_MODEL_MANAGER` |
| Проверить безопасность или опасное действие | `STAS9_GUARDIAN` |

Задачи выполняются последовательной цепочкой `ON_DEMAND`, а не запуском всех
агентов.

## 5. База знаний SOL

Создана структура:

```text
MARKET_KNOWLEDGE/
  SOL/
  EVENTS/
  PATTERNS/
  LABELS/
  DATASETS/
```

В каждом каталоге есть русскоязычная инструкция. Шаблон
`EVENTS/EVENT_SOL_000001.yaml` явно имеет статус
`TEMPLATE_NOT_OBSERVED`, не является фактическим рыночным наблюдением и не
может попадать в dataset.

Источник будущего исследования — только существующие выгруженные свечи SOL.
Внешняя загрузка данных и использование других инструментов не разрешены.

## 6. Подготовка ML dataset

Создан безопасный контур:

```text
SOL DATA
  -> EVENTS
  -> FEATURES
  -> LABELS
  -> ML DATASET
```

Документы:

```text
DATASET_BUILDER/README_RU.md
DATASET_BUILDER/SOL_DATASET_PIPELINE.yaml
```

Первый этап ограничен поиском ситуаций, фиксацией событий, проектированием
признаков, формализацией labels и проверкой будущего набора данных. Шаблоны,
непроверенные события и строки без происхождения данных исключаются.

Обучение в этом контуре не реализовано и не запускалось.

## 7. Память распределения задач

Создан файл `MEMORY/AGENT_RESPONSIBILITIES.yaml`. В нём зарегистрированы:

1. восемь существующих ролей;
2. режимы и области доступа;
3. обязанности и запреты;
4. текущая задача настройки;
5. участники, выполненные действия и результаты;
6. правила последующего обновления памяти.

## 8. Безопасность

После завершения активен режим:

```text
SAFE
READ_ONLY
```

Не выполнялись:

- обучение;
- Optuna;
- forward;
- изменение моделей или модельных указателей;
- изменение STAS5 или вложенного STAS8;
- live trading;
- удаление или перенос файлов.

Контрольная metadata-граница `STAS5_ML_CORE`, включая вложенный STAS8:

```text
до:    files=6196, sha256=40ceeb41c5562eb8b64d31dae1f2abb91caad9da40be6e294715c161d51d1445
после: files=6196, sha256=40ceeb41c5562eb8b64d31dae1f2abb91caad9da40be6e294715c161d51d1445
```

## 9. Проверки

```text
YAML parse: 31/31 PASS
agent directories and required files: 8 x 4 PASS
control-plane agent registry: 8/8 PASS
Sentinel delegation allowlist: 7/7 specialists PASS
machine routes: 11/11 PASS
role documents: 7/7 PASS
SOL event template: PASS
SOL dataset pipeline no-training contract: PASS
agent responsibility memory: 8/8 PASS
STAS5/STAS8 metadata boundary: UNCHANGED
```

## 10. Следующий безопасный шаг

Отдельной командой задать точный путь к существующим свечам SOL, таймфрейм и
интервал read-only анализа. После этого `STAS9_MARKET_RESEARCH` сможет найти
кандидаты событий, `STAS9_FEATURE_MANAGER` — подготовить контракты признаков,
а `STAS9_VALIDATOR` — проверить результат. Обучение остаётся заблокированным
до отдельного прямого технического задания.
