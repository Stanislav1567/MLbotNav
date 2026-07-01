# TZ P29-P30 — Закрытие покрытий гипотез (swing_bos_minmax + density_orderbook)

Дата: 2026-05-24
Статус: CLOSED
Контур: TZ_FEATURES_BLOCK

## Финал закрытия
1. `P29` закрыт: `reports/qa_gate/p29_swing_bos_minmax_coverage_20260524T111758Z.json` (PASS).
2. `P30` закрыт: `reports/qa_gate/p30_density_orderbook_coverage_20260524T114051Z.json` (PASS).

## 0. Цель
Закрыть 2 незавершенных функциональных блока по гипотезам/фичам через фактическое coverage-срабатывание в long/short и зафиксировать PASS-аудитами.

## 1. Блок P29 — swing_bos_minmax
Название блока: `swing_bos_minmax`

### 1.1 Что делаем
1. Запуск long_only с целевым покрытием swing/BOS/minmax-гипотез.
2. Запуск short_only с целевым покрытием swing/BOS/minmax-гипотез.
3. Проверка coverage-отчетов на отсутствие `missing_names` по гипотезам блока.
4. Контрольный контур таблиц/движка/зависимостей.

### 1.2 Гипотезы блока (обязательные к покрытию)
1. `swing_hl_hh_long`
2. `swing_lh_ll_short`
3. `bos_continuation_confirm`
4. `min_max_range_revert`
5. `max_low_pullback_long`

### 1.3 Критерии закрытия P29
1. В coverage long/short перечисленные гипотезы появляются в observed history.
2. Нет их присутствия в `missing_names`.
3. PASS: `table_convergence_5plus`, `audit_chain_report`, `features_block_audit`, `tz_gate`, `p72_freeze_ready`.

## 2. Блок P30 — density_orderbook
Название блока: `density_orderbook`

### 2.1 Что делаем
1. Целевой long_only/short_only запуск с акцентом на density/orderbook-гипотезы.
2. Проверка фактических срабатываний в coverage.
3. Проверка доступности источника стакана/микроструктуры.
4. Контрольный контур таблиц/движка/зависимостей.

### 2.2 Гипотезы блока (обязательные к покрытию)
1. `hvn_lvn_density_reaction`
2. `volume_profile_poc_vah_val_retest`
3. `value_area_rotation_vs_breakout`
4. `wedge_breakout_plus_profile_acceptance`
5. `orderbook_imbalance_l1_l50`
6. `spread_pressure_and_delta_absorption`

### 2.3 Критерии закрытия P30
1. Перечисленные гипотезы присутствуют в observed history coverage.
2. Нет их в `missing_names`.
3. `orderbook_source_audit --expect-status active` = PASS.
4. PASS: `table_convergence_5plus`, `audit_chain_report`, `features_block_audit`, `tz_gate`, `p72_freeze_ready`.

## 3. Порядок выполнения (строго)
1. P29 полностью до статуса CLOSED.
2. Только после этого P30.
3. После закрытия каждого блока обновлять основной трекер TZ_FEATURES_BLOCK с номером, артефактами и статусом.

## 4. Нумерация в основном трекере
1. P29 — `swing_bos_minmax` (OPEN -> CLOSED)
2. P30 — `density_orderbook` (OPEN -> CLOSED)
3. Далее — финальный статус после двух закрытий.

## 5. Артефакты фиксации (для каждого блока)
1. `reports/qa_gate/hypothesis_coverage_long_only_*.json`
2. `reports/qa_gate/hypothesis_coverage_short_only_*.json`
3. `reports/qa_gate/table_convergence_5plus_*.json`
4. `reports/table_canon_current/audit_chain_report.json`
5. `reports/qa_gate/features_block_audit_*.json`
6. `reports/qa_gate/orderbook_source_audit_*.json` (для P30 обязательно)
7. `reports/qa_gate/tz_gate_*.json`
8. `reports/qa_gate/p72_freeze_ready_*.json`
