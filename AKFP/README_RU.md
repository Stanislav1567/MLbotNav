# AKFP — Отдельный Блок Автокалибровки

Эта папка фиксирует новый блок `AKFP` как sidecar-оркестратор над текущим ML-контуром.

## Что сделано
1. Добавлен toggle включения/выключения:
   - `configs/akfp_policy.yaml` -> `akfp.enabled: true|false`
2. Добавлен bridge-оркестратор:
   - `src/mlbotnav/akfp_bridge.py`
3. Добавлен удобный runner:
   - `run_akfp_bridge.ps1`

## Режимы
1. `enabled: false` -> AKFP не запускается, пишет `SKIPPED` отчет.
2. `enabled: true` + `mode: shadow` -> dry-run/проверка маршрутов.
3. `enabled: true` + `--execute` -> реальный запуск bridge-цепочки.

## Мосты (автоматическая связка)
1. `run_p23_operator_unified.ps1` (long/short/combined по policy)
2. `run_p24_latest_pass_report.ps1`

## Как запускать
1. Проверка (без исполнения):
```powershell
powershell -ExecutionPolicy Bypass -File .\run_akfp_bridge.ps1
```
2. Реальный запуск:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_akfp_bridge.ps1 -Execute
```

## Где отчеты
1. `reports/qa_gate/akfp_bridge_*.json`

## Правило безопасности
1. AKFP не переписывает ядро ML.
2. AKFP управляет только порядком запуска через существующие мосты.
3. Контуры long/short остаются раздельными по policy.

