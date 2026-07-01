# R8 DoD Closeout: ML Runtime Без Калибровки

Дата (UTC): 2026-05-27T07:44:00Z  
Контур: только основной ML runtime, без `AKFP/APTuna/optuna_*`.

## Цель шага R8
Подтвердить финальное закрытие очереди `R7 (G1..G5)` и зафиксировать выполнение Definition of Done для ML non-calibration.

## Подтверждение очереди R7
1. `G1` DONE — `P144-G1-HANDOFF-GATE-HARDENING`.
2. `G2` DONE — `P145-G2-RUNTIME-TRADING-FIELDS-CONTRACT`.
3. `G3` DONE — `P146-G3-INFERENCE-SLA-HARD-GATE-DEFAULT`.
4. `G4` DONE — `P147-G4-SQL-DDL-RUNTIME-PARITY-AUDIT`.
5. `G5` DONE — `P148-G5-SECURITY-RUNTIME-POLICY-HARD-DEFAULT`.

## Доказательства
1. SQL DDL parity: `reports/qa_gate/sql_runtime_ddl_parity_20260527T073337Z.json` (`PASS`, `gap_count=0`).
2. Security hard-default и regression:
   - `tests.test_release_gate`
   - `tests.test_security_gate`
   - `tests.test_security_providers`
3. Кодировочный/текстовый аудит: `python -m mlbotnav.text_guard` (`PASS`).

## DoD (раздел 11 базового ТЗ)
1. Единый runtime-контракт сигналов: PASS.
2. Воспроизводимость `signal -> entry -> exit -> pnl`: PASS.
3. Long/short split без смешивания: PASS.
4. Promote без полного gate/stage PASS невозможен: PASS.
5. Релевантные `PARTIAL/TODO` по ML non-calibration закрыты очередью `R7`: PASS.

## Итог
`R8` закрыт. По этому ТЗ дальше ведется только поддержка консистентности (`ACTIVE/CHANGELOG`) и регрессионные проверки после новых изменений.
