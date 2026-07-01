# TZ AKFP: Окна Калибровки (Строгий Стандарт)

Дата: 2026-05-24  
Статус: ACTIVE  
Блок: `AKFP` (без вмешательства в ML-ядро)

## 1) Цель
Зафиксировать единый стандарт окон калибровки, чтобы прогоны не путались по датам, и long/short всегда запускались раздельно.

## 2) Главные правила
1. Тест берем только по закрытому дню (ровные 24 часа UTC).
2. Текущий незакрытый день запрещен для теста.
3. Long и short калибруются отдельно, без смешивания кэша/шортлистов.
4. После временного unlock readiness всегда возвращается в исходное состояние.
5. После каждого шага обязателен аудит CSV/XLSX + движка + gate-цепочки.

## 3) Профили окон
1. `smoke_1d1d`: 1 день train + 1 день test, repeats=1.
2. `tuning_1d1d`: 1 день train + 1 день test, repeats=3.
3. `tuning_3d2d`: 3 дня train + 2 дня test, repeats=5.
4. `preprod_14d7d`: 14 дней train + 7 дней test, repeats=10.
5. `production_21d7d`: 21 день train + 7 дней test, repeats=10.

Текущий активный профиль: `tuning_1d1d`.

## 4) Где зафиксировано в коде
1. Политика: [configs/akfp_policy.yaml](C:/Users/007/Desktop/MLbotNav/configs/akfp_policy.yaml)
2. Финализатор P12: [src/mlbotnav/akfp_finalize.py](C:/Users/007/Desktop/MLbotNav/src/mlbotnav/akfp_finalize.py)
3. Финальные реестры: `reports/akfp/finalization/*.json`

## 5) Definition of Done
1. Все 6 реестров P12 созданы и согласованы.
2. `P23 + P24 + table/audit/gate` дают PASS.
3. Есть отдельный артефакт шага `akfp_p12_audit_*.json` со статусом PASS.
