# TZ_OPTUNA_STRICT_EXECUTION_2026-05-31_RU

Дата: 2026-05-31  
Контур: только `C:\Users\007\Desktop\MLbotNav` (Optuna/APTuna), ML runtime не трогаем.

## 1. Цель
1. Довести текущий пакет V63 до финального checkpoint (`S2 -> S3 -> S4`) строго в базе `3x9`.
2. Закрыть цикл не отчетами, а измеримым результатом по quality-gate.

## 2. Что уже подтверждено
1. Технический long-блокер снят: поиск больше не падает тотально в `search_failed` по кросс-порогу.
2. Scope-lock закреплен: ML-сигналы не используются, `OptunaMlSignalBackend=off`.
3. Канонический runtime-режим: `Threads=9`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`.

## 3. Приоритеты (сверху вниз)
1. P0: Выполнить V63-S2 (`short_only`) по пакету без отклонений.
2. P1: Выполнить V63-S3 (`short_only`) только если S2 не прошел gate.
3. P2: Выполнить V63-S4 cross-mode checkpoint и зафиксировать решение GO/NO_GO.
4. P3: После каждого шага обязательный аудит и синхронизация реестров.

## 4. Строгие параметры исполнения
1. Запуски только раздельно по режимам (`long_only`/`short_only`).
2. Окно: `fixed_1d`, train `2026-05-19`, test `2026-05-20`.
3. База мощности: `3x9`.
4. `OptunaMlSignalBackend=off`.
5. Single-change protocol: в шаге меняется только то, что указано в V63.

## 5. Пошаговый план исполнения
1. Шаг A (V63-S2):
1. `PShortGrid=0.06,0.05,0.04`
2. `StopLossPct=0.0020` (preserved)
2. Шаг B (V63-S3, условный):
1. `StopLossPct=0.00000078125`
2. профиль S2 сохраняется
3. Шаг C (V63-S4):
1. cross-mode confirmation
2. micro-gate decision

## 6. Критерии приемки (без изменений)
1. `all_tradeful=true` по каждому режиму.
2. `mean OOS >= -2.5%` по каждому режиму.
3. `worst branch OOS >= -10%` по каждому режиму.

## 7. Обязательные артефакты после каждого шага
1. checkpoint report (`reports/qa_gate/...checkpoint...json`).
2. логи воркеров (`reports/logs/optuna_pool_...`).
3. `pip check`, `text_guard`, `readiness --show`.
4. обновление `docs/ACTIVE_WORK_ITEMS_RU.md` и `docs/CHANGELOG_CHRONOLOGY_RU.md`.
