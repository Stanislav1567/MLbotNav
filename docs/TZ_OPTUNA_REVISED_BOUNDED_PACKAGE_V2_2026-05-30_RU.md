# TZ_OPTUNA_REVISED_BOUNDED_PACKAGE_V2_2026-05-30_RU

Дата: 2026-05-30  
Контур: только Optuna/APTuna (ML runtime не изменяем)

## 1. Основание
1. `P495` (U1.1..U1.4) завершен без достижения U1-критериев.
2. `P496` зафиксировал паузу U1 и возврат в freeze.
3. Перед новыми unfreeze-прогонами нужен новый bounded package v2.

## 2. Факты из U1 (вход в v2)
1. Entry-threshold family (`PShortGrid`/`PLongGrid`) дала нестабильность:
1. сочетания `no-trade` и `overtrade`,
2. локальные `goal_pass` не воспроизводятся по всем веткам.
2. Risk-cadence family (`CooldownBars`) не выровняла оба режима:
1. short стал tradeful, но глубоко отрицательный OOS,
2. long ушел в no-trade.
3. Главный блокер: `all_tradeful=true` не удерживается одновременно для обоих режимов.

## 3. Bounded Package v2 (разрешенные семейства и порядок)
1. V2-F1: execution risk micro-band
1. Параметры: `stop_loss_pct`, `take_profit_pct`.
2. Цель: уменьшить хвосты убытков без ухода в no-trade.
3. Single-change: только эта family на шаг.
2. V2-F2: tp-reach guard micro-band
1. Параметры: `min_tp_reach_prob`, `tp_min_factor`.
2. Цель: убрать ложные проходы и стабилизировать tradeful-ветки.
3. Single-change: только эта family на шаг.
3. V2-F3: move-threshold narrow band
1. Параметры: `min_expected_move`.
2. Цель: сжать зону no-trade/overtrade в обоих режимах.
3. Single-change: только эта family на шаг.

## 4. Ограничения v2
1. Не возвращаться к entry-threshold family в первом v2 цикле.
2. Не расширять пространство beyond micro-band.
3. Каждый шаг строго раздельно: `short_only` и `long_only`.
4. После каждого шага обязательны:
1. `pip check`,
2. `text_guard`,
3. `readiness --show`,
4. фиксация в `ACTIVE` и `CHANGELOG`.

## 5. U1 acceptance rules (без ослабления)
1. Для каждого режима:
1. `all_tradeful=true`,
2. `mean OOS >= -2.5%`,
3. `worst branch OOS >= -10%`.
2. Если критерии не выполнены:
1. остановка семейства,
2. формальный checkpoint,
3. freeze сохраняется.

## 6. DoD для P499
1. Пакет v2 зафиксирован отдельным TZ.
2. Приоритетный Optuna-TZ переведен на этот пакет как следующий strict шаг.
3. Реестр/хронология синхронизированы.
4. Обязательные проверки PASS.
