# STAS4: 4 комбинированные стратегии на 3 днях

Дата фиксации: 2026-07-09.

Источник Stas2:
`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_short_macro_wave_review_20260709_071233`

Период:
`2026-05-10`, `2026-05-11`, `2026-05-12`.

Правила слоя:
- старая логика Stas1/Stas2 не менялась;
- зеленая галочка означает старый вход, который слой Stas4 пометил как шум;
- синяя стрелка означает новый вход-кандидат от слоя Stas4;
- сигнал считается на закрытой свече, вход идет следующей свечой;
- ML, Optuna, scorer, target-lock и API не запускались.

## Сводка

| Стратегия | 2026-05-10 галочки | 2026-05-10 стрелки | 2026-05-11 галочки | 2026-05-11 стрелки | 2026-05-12 галочки | 2026-05-12 стрелки | Итого галочки | Итого стрелки |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `structure_ta+trend_momentum` | 45 | 2 | 60 | 2 | 67 | 1 | 172 | 5 |
| `structure_ta+volume_flow` | 39 | 0 | 53 | 1 | 66 | 1 | 158 | 2 |
| `pattern+structure_ta` | 33 | 0 | 41 | 3 | 32 | 3 | 106 | 6 |
| `density_profile+structure_ta` | 20 | 2 | 26 | 4 | 26 | 5 | 72 | 11 |

## Вывод

`structure_ta+trend_momentum` сильнее всего режет старый шум: `172` старых входа помечены галочкой при `5` новых кандидатах. Это главный кандидат на строгий фильтр шума.

`structure_ta+volume_flow` почти не добавляет новые входы: `158` галочек и только `2` стрелки. Это хороший кандидат на жесткий запрещающий или подтверждающий слой.

`pattern+structure_ta` дает средний фильтр: `106` галочек и `6` стрелок. Его стоит смотреть глазами как дополнительный слой, особенно на местах свечных конфликтов.

`density_profile+structure_ta` мягче остальных: `72` галочки и `11` стрелок. Это скорее контекстный слой для поиска новых кандидатов, а не жесткий бан-фильтр.

## Артефакты

Все PNG, CSV, JSON и RU-отчеты лежат в:

`STAS4_FEATURE_HYPOTHESIS_REVIEW`

Папки прогонов:
- `combo_structure_trend_20260510`, `combo_structure_trend_20260511`, `combo_structure_trend_20260512`;
- `combo_structure_volume_20260510`, `combo_structure_volume_20260511`, `combo_structure_volume_20260512`;
- `combo_pattern_structure_20260510`, `combo_pattern_structure_20260511`, `combo_pattern_structure_20260512`;
- `combo_density_structure_20260510`, `combo_density_structure_20260511`, `combo_density_structure_20260512`.

## Проверки

Выполнено:

```powershell
$env:PYTHONPATH='src'
python -m py_compile src\mlbotnav\visual_entry_stas4_family_overlay.py
```

Также проверены `12` PNG: все имеют размер `4960x2697`, ненулевой вес и ненулевую дисперсию пикселей.

Замечание: при стратегиях с `pattern` остается `FutureWarning` из `visual_entry_strategy_passport_overlay_v2d_patterns.py` по pandas `.fillna()` после `.shift()`. Это предупреждение не остановило прогон и не влияет на факт создания графиков.
