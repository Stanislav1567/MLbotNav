# TZ Q5.5: Ремедиация качества short_only (боевой контур)

Дата: 2026-05-26  
Контур: `Q5.5-SHORT`

## 1. Цель
1. Достичь устойчивого **положительного tradeful OOS** в режиме `short_only` на схеме `1d train -> next 1d test`.
2. Сохранить строгий маршрут валидации: `CSV/XLSX -> таблицы -> gate/freeze`.

## 2. Ограничения
1. Таймфрейм: `1m`.
2. Режим: только `short_only` (без смешивания с long).
3. CPU: до `85%`.
4. После `table_canon_pack` обязательно формировать Excel-пакет в `reports/table_canon_current/data`.

## 3. Шаги
1. `Q5.5-SHORT.1` baseline short-only.
2. `Q5.5-SHORT.2` ремедиация runtime-параметров (`trend_filter`, `min_expected_move`, `cooldown`, профиль входа short).
3. `Q5.5-SHORT.3` проверка `table_convergence_5plus`, `audit_table_chain`, `features_block_audit`.
4. `Q5.5-SHORT.4` проверка `tz_gate`, `p72_freeze_ready`, `p24_latest_pass`.
5. `Q5.5-SHORT.5` финальная фиксация и handoff в операторский контур.

## 4. Текущий статус
1. Активный шаг: `Q5.5-SHORT.1`.
