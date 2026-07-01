# F001: ret_1_1m - строгий паспорт калибровки

ID: `F001`
FEATURE: `ret_1_1m`
ACTION: `RET1_ALLOW`
ACTION_TYPE: `ENTRY_FILTER`
OUTPUT: `1/0`
STATUS: `ACTIVE`

## 1. Назначение

`RET1_ALLOW` разрешает или запрещает вход по движению последней закрытой минутной свечи.

Это не сторона сделки и не размер позиции. Это runtime-фильтр входа: если условие не выполнено, вход блокируется.

## 2. Фиксировано

| Поле | Значение |
|---|---|
| Таймфрейм | `1m` |
| Свеча | закрытая |
| Цена | `close` |
| Формула | `ret1_pct = (Close[1] / Close[2] - 1) * 100` |
| Единица | проценты |

## 3. Калибруется

| Параметр | Тип | Диапазон | Шаг | Значение |
|---|---|---:|---:|---|
| `F001_move` | enum/float | `-1, 1` | дискретно | направление движения |
| `F001_thr_pct` | float | `0.01..0.50` | `0.01` | минимальный процент движения |

`F001_move = 1` означает проверку движения вверх.

`F001_move = -1` означает проверку движения вниз.

## 4. Логика сигнала

```text
IF F001_move = 1 AND ret1_pct >= F001_thr_pct:
    F001_RET1_ALLOW = 1
ELSE IF F001_move = -1 AND ret1_pct <= -F001_thr_pct:
    F001_RET1_ALLOW = 1
ELSE:
    F001_RET1_ALLOW = 0
```

## 5. Стороны

Сторона не калибруется внутри F001.

LONG/SHORT режим задается внешним контуром Optuna/APTuna. Для отдельных профилей сохранять параметры так:

| Внешний режим | Параметры |
|---|---|
| LONG | `F001_LONG_move`, `F001_LONG_thr_pct` |
| SHORT | `F001_SHORT_move`, `F001_SHORT_thr_pct` |

В текущем runtime подключены базовые ключи `F001_move` и `F001_thr_pct`; разделение на LONG/SHORT происходит внешним запуском `-Mode long_only` / `-Mode short_only`.

## 6. Не калибруется

Не калибровать внутри F001:

1. `side`.
2. `tf`.
3. `vol_window`.
4. `price_source`.
5. `log_simple`.
6. `momentum_reversal`.
7. `entry_exit`.
8. `order_size`.
9. `stop_loss`.
10. `take_profit`.

## 7. Runtime-подключение

Код:

1. `src/mlbotnav/dataset.py` считает `F001_RET1_ALLOW`.
2. `src/mlbotnav/validation.py` и `src/mlbotnav/optuna_search_candidate.py` сохраняют runtime-action колонку в OOF.
3. `src/mlbotnav/backtest.py` применяет `F001_RET1_ALLOW` как entry-gate.

Активная паспортная матрица:

1. `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`.

Реестр паспортов:

1. `configs/calibration_action_passports.yaml`.

Legacy/frozen матрицы:

1. `configs/calibration_full_matrix_v1.yaml`.
2. `configs/calibration_matrices/catalog_blocks/catalog_block_01_price_volatility.yaml`.
3. `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`.

Legacy/frozen матрицы больше не являются чистым baseline для новых F001-прогонов. Они остаются только как исторический артефакт и материал для миграции.

## 8. Текущий вывод

F001 подключен как строгий паспортный фильтр входа.

В F001 калибруются только `F001_move` и `F001_thr_pct`.

`return_lookback` больше не является ручкой F001; он остается отдельной расчетной ручкой для других фич, где она реально используется.

## 9. Паспортный режим 2026-06-22

Новый активный режим:

```text
ACTION_PASSPORT_CALIBRATION
```

F001 можно калибровать только через паспортную матрицу `F001_ret1_entry_filter.yaml`.

В этой матрице включен `passport_mode.enabled=true`; любые параметры вне `F001_move` и `F001_thr_pct` должны падать на compile и не доходить до Optuna.

Backtest-подпаспорт F001:

1. `F001_RET1_ALLOW` используется только как `ENTRY_FILTER`.
2. Выходы не калибруются в F001.
3. Baseline выхода остается `TP / SL / timeout`.
4. Dynamic exit должен иметь отдельный паспорт и отдельную матрицу.
