# Политика архива STAS9

Статус: `ACTIVE_FOR_STAS9_CONTROL_PLANE`.

Дата: `2026-07-23`.

## 1. Основной закон

Старый артефакт никогда не становится активным только потому, что он новее по времени или имеет слово `latest` в имени. Активность определяется одновременно:

1. источником истины;
2. manifest/guard;
3. feature contract;
4. датами train/forward;
5. явным approval;
6. существованием всех файлов по ссылкам.

## 2. Классы хранения

| Класс | Разрешено | Запрещено |
|---|---|---|
| `ACTIVE_SOURCE` | Читать, валидировать, использовать по назначению | Переписывать без отдельного ТЗ |
| `APPROVED_TRAIN_SOURCE` | Использовать как train только по allowlist и manifest | Добавлять blind/forward дни без approval |
| `AUDIT_REFERENCE` | Сравнивать, строить отчеты | Считать production или автоматически обучать |
| `BLIND_FORWARD_QUARANTINE` | Делать read-only оценку | Использовать для train/threshold tuning |
| `SUPERSEDED` | Читать ради истории и воспроизводимости | Делать latest по дате файла |
| `BROKEN_POINTER` | Диагностировать и фиксировать в отчете | Автоматически переключать на соседний файл |
| `FROZEN_HISTORY` | Хранить и ссылаться | Удалять, перезаписывать, использовать как очередь задач |

## 3. Приоритет источников

Для калибровочного узла:

1. `docs/CALIBRATION_NODE_CURRENT/README_RU.md`;
2. `docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`;
3. `docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md`;
4. `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.

Для STAS:

1. manifest/guard фактического run;
2. allowlist фактической модели;
3. текущий документ конкретной версии;
4. PROJECT_MAP и реестры STAS9;
5. старые handoff/chronology — только как справка.

## 4. Неизменность STAS5–STAS8

STAS9 по умолчанию имеет к STAS5–STAS8 только read-only доступ.

Без отдельного пользовательского разрешения запрещено:

1. менять код, конфиги, ТЗ, модели и артефакты STAS5–STAS8;
2. переписывать `LATEST` pointers;
3. переименовывать или переносить runs;
4. удалять дубли, старые модели, PNG, CSV, JSON или отчеты;
5. запускать новое обучение или forward;
6. включать STAS8 в decision pipeline.

## 5. Train/forward рельсы

1. Train, validation, blind forward и manual review должны иметь разные статусы.
2. Blind forward не становится train-материалом автоматически после просмотра.
3. R5 `2026-03-21..2026-03-27` остается `BLIND_FORWARD_QUARANTINE`, пока нет отдельного approved review.
4. Teacher/future колонки разрешены только как y/audit и запрещены в live X.
5. Путь к dataset, его SHA, allowlist SHA и model manifest должны фиксироваться вместе.

## 6. Версионность

Новая версия не заменяет старую перезаписью.

Обязательные поля новой сущности:

```text
version_id
created_utc
source_version
source_paths
feature_contract
train_window
validation_window
forward_window
status
approval
guard_status
artifact_hashes
```

Если файл большой и его нужно изменить, перед изменением создается локальная резервная копия рядом с ним.

## 7. Модельные указатели

Перед чтением `active`, `champion` или `latest` STAS9 проверяет:

1. существует ли target path;
2. существует ли manifest;
3. совпадает ли run_id;
4. совпадает ли feature count;
5. прошел ли post-train guard;
6. не находится ли модель в статусе `offline_only`, `rejected`, `preview` или `superseded`.

Найденный `BROKEN_POINTER` только регистрируется. Автоматический поиск «ближайшей» модели и переключение запрещены.

## 8. Политика удаления

Удаление истории, моделей, datasets, reports, caches, sessions, logs и generated artifacts возможно только по прямому разрешению пользователя с точным списком целей.

До такого разрешения STAS9 может:

1. считать файлы;
2. находить дубли;
3. оценивать размер;
4. строить manifest;
5. предлагать план архивации.

STAS9 не может сам удалять или сжимать старые данные.

## 9. Минимальный admission gate для старого артефакта

Старый артефакт можно повторно использовать только если:

1. понятна его версия и роль;
2. путь существует;
3. источник данных доступен;
4. contract и allowlist известны;
5. нет leakage;
6. даты не пересекают train и blind forward;
7. status не запрещает использование;
8. результат повторного использования будет записан в новый run, а не поверх старого.
