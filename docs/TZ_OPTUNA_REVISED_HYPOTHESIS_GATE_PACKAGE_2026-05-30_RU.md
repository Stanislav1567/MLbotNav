# TZ_OPTUNA_REVISED_HYPOTHESIS_GATE_PACKAGE_2026-05-30_RU

Дата: 2026-05-30  
Контур: только Optuna/APTuna (ML runtime не изменяем)

## 1. Основание
1. По итогам `P491` и `P492` текущий decoupled Optuna-контур находится в `NO_GO freeze`.
2. Новые variant-runs в текущем контуре запрещены до пересборки гипотез/gate.
3. Текущий документ фиксирует минимальный пакет изменений для controlled unfreeze.

## 2. Инвентаризация калибровки (канон)
1. Активные блоки Optuna: `6`.
2. Feature rows в runtime-наборе: `68`.
3. Калибруемые feature rows: `56/68`.
4. Некалибруемые feature rows: `12/68` (derived/rule-based), но они остаются в runtime feature set.
5. Калибруемые hypothesis rows: `20/20` (для `contour=both`).
6. Калибруемые linked profiles: `22`.
7. `68` - это количество feature rows/columns, а не количество параметров-профилей.

## 3. Корневые проблемы цикла P486
1. Нет воспроизводимого quality-профиля одновременно для `short_only` и `long_only`.
2. Частая деградация в один из анти-паттернов:
1. `no-trade` (selector 0 сделок),
2. `overtrade` с глубоко отрицательным OOS,
3. нестабильный singleton (`trades=1`) без подтверждения на соседних ветках.
3. Критерий `3 reproducible runs per mode + mean OOS>=0` не достигнут.

## 4. Revised Hypothesis Package (что меняем до unfreeze)
1. Не расширять пространство сразу; сначала сузить его до контролируемого набора.
2. В unfreeze-пакете разрешать только bounded family changes:
1. `entry thresholds`: `p_enter_long`, `p_enter_short`,
2. `move/quality thresholds`: `min_expected_move`,
3. `risk cadence`: `cooldown_bars`,
4. `execution risk`: `stop_loss_pct`, `take_profit_pct`,
5. `tp-reach guard`: `min_tp_reach_prob`, `tp_min_factor`.
3. Блоки/фичи/hypotheses не отключать массово; менять только одну family за шаг (single-change protocol сохраняется).
4. Некалибруемые фичи не исключать из runtime (они участвуют как фиксированный контекст признаков).

## 5. Revised Gate Package (новый порядок допусков)
1. Stage U0 (текущий): freeze.
1. Разрешены только docs/audit/governance обновления.
2. Stage U1 (controlled unfreeze pilot):
1. 3 прогона на режим (`short_only`, `long_only`) в идентичном конфиге.
2. `all_tradeful=true` в каждом режиме.
3. `mean OOS >= -2.5%` в каждом режиме.
4. `worst branch OOS >= -10%` в каждом режиме.
5. Если любой пункт не выполнен -> возврат в freeze без расширения пространства.
3. Stage U2 (battle readiness):
1. 3 дополнительных прогона на режим после U1 PASS.
2. `mean OOS >= 0%` в каждом режиме.
3. `all_tradeful=true` в каждом режиме.
4. Только после U2 PASS допускается новый battle-review.

## 6. Изменения в governance
1. Любой unfreeze-шаг заводится отдельным task_id (без перезаписи старых P486 run-строк).
2. Для каждого шага обязательны артефакты:
1. run summary,
2. reproducibility summary,
3. `pip check`,
4. `text_guard`,
5. `readiness --show`.
3. В реестре не держать одновременно umbrella-`IN_PROGRESS`, если цикл уже закрыт `NO_GO freeze`.

## 7. Definition of Done для P494
1. Пакет гипотез/gate пересобран и зафиксирован в отдельном TZ.
2. Приоритетный Optuna-TZ переведен на ссылку к этому пакету как next mandatory step.
3. ACTIVE/CHANGELOG синхронизированы.
4. Обязательные проверки PASS (`pip check`, `text_guard`, `readiness --show`).
