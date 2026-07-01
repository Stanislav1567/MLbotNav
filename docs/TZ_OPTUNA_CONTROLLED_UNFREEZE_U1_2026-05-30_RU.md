# TZ_OPTUNA_CONTROLLED_UNFREEZE_U1_2026-05-30_RU

Дата: 2026-05-30  
Контур: только Optuna/APTuna (ML runtime не изменяем)

## 1. Назначение
1. Подготовить контролируемый unfreeze-пилот U1 после `P494`.
2. Запускать только bounded single-change шаги в строгом режиме `long_only`/`short_only` раздельно.
3. Не переходить к battle/совмещенным режимам до выполнения критериев U1.

## 2. Входные артефакты
1. `reports/qa_gate/optuna_no_go_freeze_20260530T070322Z.json`.
2. `docs/TZ_OPTUNA_REVISED_HYPOTHESIS_GATE_PACKAGE_2026-05-30_RU.md`.
3. `configs/optuna_frozen_candidates/frozen_short_only_20260529T184949Z.yaml`.
4. `configs/optuna_frozen_candidates/frozen_long_only_20260529T184949Z.yaml`.

## 3. Режим U1 (пилот)
1. Базовый профиль запуска:
1. `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`.
2. `ml_signal_backend=off`, fixed window `1d/1d`.
2. Разрешенные семейства изменений (по одному за шаг):
1. `p_enter_long`/`p_enter_short`,
2. `min_expected_move`,
3. `cooldown_bars`,
4. `stop_loss_pct`/`take_profit_pct`,
5. `min_tp_reach_prob`/`tp_min_factor`.
3. На каждом шаге менять только одну family.

## 4. U1 критерии PASS
1. Для каждого режима (`short_only`, `long_only`) выполнить 3 прогона в идентичном конфиге.
2. В каждом режиме:
1. `all_tradeful=true`,
2. `mean OOS >= -2.5%`,
3. `worst branch OOS >= -10%`.
3. При провале любого пункта:
1. вернуться в freeze,
2. не расширять пространство параметров,
3. фиксировать NO_GO под новым task_id.

## 5. Обязательные проверки на каждый шаг
1. `pip check`.
2. `python -m mlbotnav.text_guard --out-dir reports/qa_gate`.
3. `python -m mlbotnav.readiness --show`.
4. Фиксация шага в `ACTIVE` и `CHANGELOG`.

## 6. DoD для P495
1. Манифест U1 зафиксирован.
2. Активирован task `P495` в реестре как `IN_PROGRESS`.
3. Подготовлен стартовый шаг U1.1 (без выполнения run в этом документе).
