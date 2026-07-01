# TZ Q5.5: Ремедиация качества long_only (строгий контур)

Дата: 2026-05-25  
Контур: `Q5.5-LONG`

## 1. Цель
1. Получить **положительный tradeful OOS** для `long_only` на окнах `1d train -> next 1d test`.
2. Сохранить полную сходимость цепочки: `CSV/XLSX -> движок -> gate/freeze`.

## 2. Входные ограничения
1. Таймфрейм: `1m`.
2. Режим: строго `long_only` (без смешивания с short).
3. CPU-ограничение: до `85%`.
4. Перед каждым `table_canon_pack` закрывать Excel-файлы из `reports/table_canon_current/data`.

## 3. Пошаговый план (фиксированный)
1. `Q5.5-LONG.1` Базовый аудит текущего качества (baseline).  
Критерий: сформирован baseline-отчет по последним long-only OOS.

2. `Q5.5-LONG.2` Ремедиация фильтра входа (без изменения структуры таблиц).  
Что меняем: только runtime-параметры long-only (`trend_filter`, `min_expected_move`, `cooldown`, пороги входа).  
Критерий: есть минимум 1 tradeful OOS с `net_return_pct > 0`.

3. `Q5.5-LONG.3` Проверка табличной сходимости после ремедиации.  
Критерий: PASS по `table_convergence_5plus`, `audit_table_chain`, `features_block_audit`.

4. `Q5.5-LONG.4` Gate/freeze/операторский контур.  
Критерий: PASS по `tz_gate`, `p72_freeze_ready`, `p24_latest_pass`.

5. `Q5.5-LONG.5` Финальная фиксация результата long-only и handoff в short-only.  
Критерий: запись в `CHANGELOG_CHRONOLOGY_RU.md` + обновление `ACTIVE_WORK_ITEMS_RU.md`.

## 4. Запрещено
1. Пропуск шагов (`Q5.5-LONG.1 -> ... -> Q5.5-LONG.5` строго по порядку).
2. Смешивать long и short в одном запуске в этом контуре.
3. Менять формат канонических таблиц и словарей в середине шага.

## 5. Статус старта
1. `Q5.5-LONG.1` выполнен (baseline собран).
2. Следующий активный шаг: `Q5.5-LONG.2`.
