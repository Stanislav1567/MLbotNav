# Карта проекта STAS9

Статус: `AUDIT_COMPLETE_CONTROL_MAP_READY`.

Дата среза: `2026-07-23`.

## 1. Область аудита

Проверены корневые каталоги STAS, их README/ТЗ, текущие manifests и guards, модельные артефакты, feature allowlists, старый `models/registry` и документы калибровочного узла. Аудит был read-only: обучение, forward, Optuna и изменение STAS5–STAS8 не выполнялись.

На диске обнаружены отдельные корневые каталоги только для STAS1–STAS5:

| Контур | Файлов на дату аудита | Размер | Физический корень |
|---|---:|---:|---|
| STAS1 | 3 078 | 1 723 808 085 байт | `STAS1_GOOD_LOW_REVIEW/` |
| STAS2 | 4 606 | 2 057 859 236 байт | `STAS2_MARKET_PHASE_REVIEW/` |
| STAS3 | 1 408 | 603 939 816 байт | `STAS3_PERCENT_LADDER_REVIEW/` |
| STAS4 | 258 | 41 963 498 байт | `STAS4_FEATURE_HYPOTHESIS_REVIEW/` |
| STAS5 | 6 196 | 1 948 709 901 байт | `STAS5_ML_CORE/` |

STAS6 и STAS7 как самостоятельные проекты, документы или кодовые контуры не обнаружены. STAS8 находится внутри `STAS5_ML_CORE` и не имеет собственного корневого каталога.

## 2. Карта STAS1–STAS8

| Версия | Роль | Основной вход | Основной выход | Текущий статус аудита |
|---|---|---|---|---|
| STAS1 | Генерация и ручной разбор long low-кандидатов | OHLCV 1m | candidate pool, GOOD/BAD outcome-review, PNG/CSV | Рабочий review-baseline; не ML |
| STAS2 | Причинный pre-entry контекст рынка | STAS1 rows + OHLCV до входа | фазы, сессии, LONG/SHORT/WAVE context | Рабочий pre-entry review; не TP и не ML |
| STAS3 | Post-entry процентная лестница и TP-аудит | STAS2 rows + post-entry путь | TP path/decision/phase ladder | V2 CLEAN готов как hindsight-review; не стратегия |
| STAS4 | Визуальные гипотезы и ручная разметка признаков | STAS2 candidates + индикаторы/структура | combo spectrum, labels, review overlays | Исследовательский/teacher слой; не самостоятельный ML-dataset |
| STAS5 | ML-ядро выбора входов и риска | причинные признаки и approved labels | ENTRY, phase/state, RiskGate models | Много поколений; текущий проверенный контракт X463, но production-перевод не заявлен |
| STAS6 | Не определен | — | — | `MISSING_VERSION_DEFINITION` |
| STAS7 | Не определен | — | — | `MISSING_VERSION_DEFINITION` |
| STAS8 | Контекст long-режима и емкости движения | X439/X463 + causal move context | audit-preview demotion/blocks | Вложен в STAS5; preview слишком жесткий, выключен |

## 3. Аудит по версиям

### STAS1

Назначение: находить low-кандидаты, фиксировать исполнение `anchor low -> next candle open + 5bps` и строить визуальный outcome-review.

Подтверждено:

1. блок считается зафиксированным рабочим baseline;
2. `+0.5%` и `+1%` являются offline outcome labels;
3. поддерживается bounded lookahead для проверки результата после полуночи;
4. будущее не является признаком входа;
5. основной технический риск — шум, дубли и качество выбора значимого low.

Решение STAS9: `READ_ONLY_SOURCE / REVIEW_CANDIDATE_PROVIDER`.

### STAS2

Назначение: добавить к уже существующим STAS1-кандидатам только контекст, доступный до входа.

Подтверждено:

1. разделены фон, LONG-волна, SHORT-risk context, WAVE и GAP;
2. `context_before_entry_check=True` является ключевым causal guard;
3. WAVE может быть hindsight-review и не должна молча становиться live-признаком;
4. TP/MFE/MAE и post-entry расчеты запрещены внутри STAS2.

Решение STAS9: `READ_ONLY_CAUSAL_CONTEXT_PROVIDER`.

### STAS3

Назначение: разбирать фактическую достижимость процентных уровней после заданного входа.

Подтверждено:

1. V1 концептуально архивирован;
2. V2 CLEAN построен отдельным модулем и не использует старый V1 как основу;
3. `entry_price_for_calc = entry_price_5bps`;
4. MFE, ideal TP и future path являются только hindsight-review;
5. STAS3 не должен выдавать торговое разрешение и не должен попадать в live X.

Решение STAS9: `POST_ENTRY_AUDIT_ONLY / FORBIDDEN_AS_LIVE_FEATURE_SOURCE`.

### STAS4

Назначение: визуально сравнивать feature families, combo strategies и ручные решения.

Подтверждено:

1. 14-дневная разметка содержит 972 кандидата, `KEEP_DRAFT=115`, `CUT_DRAFT=857`;
2. yellow X имеет роль `AUDIT_ONLY`;
3. STAS4 подготовил indicator/density/structure/pattern контекст;
4. visual overlay не равен причинному feature exporter;
5. часть логики позже была перенесена в причинные STAS5 V2 features.

Решение STAS9: `TEACHER_AND_HYPOTHESIS_SOURCE / NOT_A_MODEL_REGISTRY`.

### STAS5

STAS5 содержит несколько самостоятельных поколений ML:

| Поколение | Признаки | Модельная идея | Итог аудита |
|---|---:|---|---|
| V1 | 111 | LogisticRegression по KEEP/CUT | Технически корректный baseline, архитектурно слеп к полному combo/risk; только audit reference |
| V2 selected | 126 | V1 + risk gate subset | Controlled forward готов, но контур superseded |
| V2 full | 274 | Полный causal feature snapshot | Полный набор оказался хуже выбранного subset на том прогоне |
| V3 | 274 | Повторное обучение с approved review 16–20 мая | Отдельный проверенный forward 21–25 мая; superseded |
| V4 | 287 | Offline human-style group ranker | Использует full-group контекст; не live-safe |
| V4L | 289 | Prefix/live-safe group ranker | Guard и prefix invariance PASS; не выбран как production |
| V5/V5C | 439 | ENTRY baseline + phase/state + two-block | Guard-driven train; baseline обычно сильнее two-block |
| V5C R4BB | 463 | X439 + 24 Bollinger features; отдельный RiskGate | Текущий latest run, guards PASS; baseline выбран, RiskGate требует настройки |

Ключевой текущий указатель:

```text
STAS5_ML_CORE/artifacts/v5c/model/STAS5_V5C_LATEST_TWO_BLOCK_MODEL_RUN.json
-> stas5_v5c_r4bb_train_20260127_20260320
```

Решение STAS9: `MODEL_SOURCE_WITH_EXPLICIT_GENERATION_AND_GUARD_STATUS`.

### STAS6

Поиск точного идентификатора `STAS6` вне старых журналов не дал отдельного проекта, ТЗ, модели или контракта.

Решение STAS9: не выдумывать назначение задним числом. Зафиксировать `MISSING_VERSION_DEFINITION`. Если STAS6 нужен, создать отдельное ТЗ с ролью, входом, выходом и миграцией.

### STAS7

Поиск точного идентификатора `STAS7` вне старых журналов не дал отдельного проекта, ТЗ, модели или контракта.

Решение STAS9: не считать номер автоматически закрытым. Статус `MISSING_VERSION_DEFINITION`.

### STAS8

Назначение: подтвердить живой long-режим и емкость хода до RiskGate.

Подтверждено:

1. код и ТЗ находятся внутри STAS5;
2. текущий контур — read-only audit-preview поверх R5;
3. source forward: `2026-03-21..2026-03-27`, 564 строки, X463;
4. preview изменяет распределение `61/166/337` в `1/20/543`, поэтому слишком жесткий;
5. STAS8 не имеет права повышать `SKIP` до `ENTER`;
6. teacher grid использует future только offline;
7. отдельная обученная `MOVE_EDGE_ML` пока отсутствует.

Решение STAS9: `DISABLED_AUDIT_PREVIEW / NOT_PRODUCTION / NOT_TRAIN_SOURCE_UNTIL_APPROVAL`.

## 4. Сквозная карта данных

```text
OHLCV
  -> STAS1 candidate/outcome review
  -> STAS2 causal pre-entry context
  -> STAS4 teacher/feature hypothesis layer
  -> STAS5 causal feature contracts and ML
  -> STAS8 disabled move-capacity preview

STAS2
  -> STAS3 post-entry percent/TP audit
     (отдельная ветка, запрещенная как live feature source)
```

## 5. Главные результаты аудита

1. Версионная нумерация неполна: STAS6 и STAS7 не существуют как самостоятельные контуры.
2. STAS8 физически и конфигурационно вложен в STAS5, что создает путаницу владения.
3. В старом `models/pipeline` находится 6 043 joblib-файла, но реестр содержит 6 496 записей и 193 уникальные ссылки на отсутствующие файлы.
4. `models/registry/active_model.json` и `champion.json` указывают на отсутствующий joblib от `2026-05-21`; старый active pointer нельзя считать рабочим.
5. Все 6 043 существующих legacy pipeline model-файла имеют хотя бы одну запись в старом candidates registry, но там есть 260 повторных записей.
6. Текущий STAS5 latest pointer внутренне указывает на существующий R4BB run; production pointer верхнего уровня проекта с ним не синхронизирован.
7. Контракты признаков эволюционировали от X111 к X463; без registry легко случайно смешать X439, X463 и audit-only поля.
8. Следующий безопасный шаг — не новое обучение, а внедрение STAS9 control plane с проверкой ссылок, lineage и approval gates.
