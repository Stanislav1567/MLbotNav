# ТЗ: Подключение всех фич и гипотез из `features_block.yaml` (2026-05-23)

## Цель
Подключить и зафиксировать работу всех **активных** фич/гипотез из конфига `configs/features_block.yaml` так, чтобы:
1. фичи 1-в-1 совпадали с runtime;
2. гипотезы реально шли в перебор;
3. long/short контуры не смешивались;
4. проверка выполнялась аудитом + контрольным прогоном.

## Границы
- Включаем активные блоки `features` и `hypotheses`.
- `extended_hypotheses_backlog` остаётся отдельным этапом (там `status: planned`).

## План внедрения
1. Сверка конфига с runtime:
   - `features.columns` == `FEATURE_COLUMNS` (порядок и состав).
   - `features.groups` == `FEATURE_GROUPS`.
2. Сверка гипотез с runtime:
   - профили `trend_filters_*_style_1m` непустые;
   - все `trend_filter` поддерживаются `backtest`.
3. Единая политика запуска:
   - профиль гипотез из `features_block.yaml` используется по умолчанию;
   - ручной single-filter режим только через явное отключение профиля.
4. Аудит на данных:
   - проверка, что `build_feature_frame` содержит все конфиг-фичи на реальном sample.
5. Контрольный прогон:
   - отдельный `long_only`;
   - отдельный `short_only`;
   - далее `hypothesis_coverage_audit` для обоих контуров.

## Команды проверки (эталон)
```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.features_block_audit --config configs/features_block.yaml --out-dir reports/qa_gate
.\.venv\Scripts\python.exe -m mlbotnav.hypothesis_coverage_audit --contour-id long_only --features-config configs/features_block.yaml
.\.venv\Scripts\python.exe -m mlbotnav.hypothesis_coverage_audit --contour-id short_only --features-config configs/features_block.yaml
```

## Критерии приемки (5+)
1. `features_block_audit` = `PASS`.
2. `hypothesis_coverage_audit` long_only = `PASS`.
3. `hypothesis_coverage_audit` short_only = `PASS`.
4. В отчётах есть подтверждение profile-based плана (`profile_plan_matches_config`).

