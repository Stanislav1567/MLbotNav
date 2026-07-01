# ML TZ Gaps Queue (Non-Calibration)

Дата (UTC): 2026-05-27T06:54:26Z
Основание: `docs/TZ_STATUS_AGAINST_ORIGINAL.md` + текущий статус `P16` в `ACTIVE/CHANGELOG`.

## Scope
Только ML runtime без калибровки (`без AKFP/APTuna/optuna-контуров`).

## Очередь R7 (по убыванию риска)
1. `G1` Gate-pipeline обязательности перед promote (`DONE`).
   - Цель: подтвердить, что promote-path технически невозможен без полного `P23->P24->P26`.
   - Выход: проверка кода + regression-тест.

2. `G2` Единообразие обязательных торговых полей во всех runtime-отчетах (`DONE`).
   - Цель: сверить `signal/entry/exit/pnl/risk` поля между backtest/inference/final_review.
   - Выход: аудит-матрица + тест на обязательные ключи.

3. `G3` SLA inference как hard-gate (`DONE`).
   - Цель: формализовать и закрепить проверку SLA в gate-пакете.
   - Выход: исполняемая проверка и артефакт в `reports/qa_gate`.

4. `G4` DDL parity для runtime-хранилища (`DONE`).
   - Цель: зафиксировать, какие SQL-объекты из исходного ТЗ обязательны именно для ML runtime (без калибровки).
   - Выход: список разрывов + приоритизация для реализации.

5. `G5` Security runtime policy (`Vault/KMS`) (`DONE`).
   - Цель: отделить runtime-must от полной enterprise-реализации и зафиксировать минимально обязательный слой.
   - Выход: технический минимум + проверочный чек.

## Правило исполнения
Для каждого `G*` шага обязательны:
1. `что делаем / зачем / что сделали`;
2. `P24/P26` (если затронут runtime-контур) + `text_guard`;
3. запись в `ACTIVE` и `CHANGELOG`.

## Текущий прогресс
1. `G1` — DONE (`P144-G1-HANDOFF-GATE-HARDENING`).
2. `G2` — DONE (`P145-G2-RUNTIME-TRADING-FIELDS-CONTRACT`).
3. `G3` — DONE (`P146-G3-INFERENCE-SLA-HARD-GATE-DEFAULT`).
4. `G4` — DONE (`P147-G4-SQL-DDL-RUNTIME-PARITY-AUDIT`).
5. `G5` — DONE (`P148-G5-SECURITY-RUNTIME-POLICY-HARD-DEFAULT`).
6. `R8` — DONE (`P149-R8-DOD-CLOSEOUT-ML-NONCALIB`).
7. Следующий режим: поддержка консистентности `ACTIVE/CHANGELOG` и регрессионные проверки после новых изменений.
