# PASSPORT CONTROL INDEX RU

Создано UTC: `2026-06-23T08:41:37Z`

Статус: `ACTIVE_CONTROL_INDEX`

Назначение: компактная панель управления для паспортной калибровки. Это не исполняемый Optuna-конфиг. Файл показывает, где лежит истина, как идти по шагам и что запрещено смешивать.

## 1. Главный Принцип

Не держим всю калибровочную логику в одном огромном конфиге.

Используем четыре слоя:

```text
Паспорт MD -> реестр YAML -> исполняемая Optuna-матрица -> прогон/аудит
```

Смысл:

1. Паспорт MD описывает смысл инструмента и его правила.
2. Реестр YAML хранит компактный контракт и индекс.
3. Матрица YAML является исполняемой проекцией для Optuna.
4. Отчеты фиксируют результат и решение аудита.

## 2. Источник Истины

Активный маршрут:

1. `docs/CALIBRATION_NODE_CURRENT/README_RU.md`
2. `docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md`
3. `docs/CALIBRATION_NODE_CURRENT/PASSPORT_CONTROL_INDEX_RU.md`

Паспорта:

1. `docs/CALIBRATION_NODE_CURRENT/passports/features/*.md`

Реестр:

1. `configs/calibration_action_passports.yaml`

Исполняемые матрицы:

1. `configs/calibration_matrices/passport_actions/*.yaml`

Runtime enforcement:

1. `src/mlbotnav/optuna_space.py`
2. `src/mlbotnav/optuna_search_candidate.py`
3. `src/mlbotnav/backtest.py`

Результаты и аудит:

1. `reports/qa_gate/*.md`
2. `reports/adaptive/*`
3. `reports/final_review/*`

## 3. Слой Паспорта

Паспорт описывает смысл действия.

В каждом паспорте должны быть:

1. Название фичи/индикатора.
2. Формула и тайминг свечи.
3. Ручки, которые калибруются.
4. `min / max / step` или enum-значения.
5. Что здесь не калибруется.
6. Выходной `action_id`.
7. Граница LONG/SHORT.
8. Тип: solo или явно combined.

Правило: новый сигнал начинается с паспорта, а не с прямой правки Optuna YAML.

## 4. Слой Реестра

Главный компактный реестр:

`configs/calibration_action_passports.yaml`

В реестре хранятся:

1. Номер блока: `B001`, `B002`, `B003`, ...
2. Номер паспорта: `F001`, `F002`, `F017_F018`, ...
3. Русское имя блока и технический `block_key`.
4. `passport_path`.
5. `active_matrix_path`.
6. `action_id`.
7. `allowed_calibration_params`.
8. `runtime_action_columns`.
9. `not_calibrated_here`.
10. Baseline exit subpassport.

Правило: если действия нет в реестре, Optuna не должна использовать его как активный паспорт.

## 5. Слой Матрицы

Исполняемые матрицы лежат здесь:

`configs/calibration_matrices/passport_actions/*.yaml`

Одна baseline-матрица должна соответствовать одному паспортному действию.

В матрице должны быть:

1. `passport_mode.enabled=true`.
2. `registry_block_id`.
3. `registry_passport_id`.
4. `action_id`.
5. Только разрешенные параметры паспорта.
6. Feature row для действия.
7. Граница baseline exit policy.

Правило: matrix YAML исполняет паспорт, а не придумывает новый смысл.

## 6. Политика Блоков

Блоки нужны для порядка:

```text
B001 - цена / волатильность RET_N
B002 - high-low spread
B003 - rolling volatility
B009 - stochastic K/D
B014 - levels/range/channel
```

Baseline-правило:

1. Сначала калибруем каждую фичу/действие отдельно.
2. Не смешиваем все фичи блока в один baseline-прогон.
3. Комбо допускается только через отдельный combination passport.
4. Combination passport обязан объяснить, почему эти сигналы являются одной грамматикой.

Разрешенный combined-пример:

`F017_F018_STOCH14_ALLOW`, потому что `%K` и `%D` - две линии одного Stochastic-инструмента, а `KD_CROSS` требует обе линии.

Запрещенный пример:

RSI + MACD + Volume в одном baseline-паспорте без отдельной явной combined-логики.

## 7. Политика LONG / SHORT

LONG и SHORT являются отдельными runtime-стеками.

Правила:

1. `long_only` запускается отдельно.
2. `short_only` запускается отдельно.
3. Результаты сохраняются отдельно.
4. Не делаем общий вывод из смешанного LONG/SHORT результата.
5. `BOTH` не является baseline-режимом для паспортной калибровки без отдельного утвержденного паспорта.

## 8. Граница Выходов И Риска

Фичевые паспорта не калибруют выходы.

Baseline exits:

1. TP.
2. SL.
3. Timeout.

Не калибруется внутри фичевых паспортов:

1. Stop loss.
2. Take profit.
3. Timeout.
4. Order size.
5. Leverage.
6. Side.

Если нужно калибровать выходы, создаем отдельные exit-паспорта.

## 9. Граница ML

ML не должен получать сырую калибровочную кашу.

Разрешенные входы в ML:

1. Аудированные паспортные action columns.
2. Подтвержденные паспортные кандидаты.
3. Явно записанные calibration params.
4. Отчеты с понятным LONG/SHORT и OOS-статусом.

Запрещено отдавать в ML:

1. Старые mixed full-matrix параметры.
2. Zero-trade кандидатов как production signals.
3. One-trade experimental result как production GO.
4. Неизвестные stale `F*_ALLOW` колонки.

## 10. Запрет На Кашу

Жесткие правила:

1. Не добавлять параметр прямо в Optuna YAML до паспорта и реестра.
2. Не смешивать feature knobs, exits, risk, order size и ML knobs в одном паспорте.
3. Не использовать старую хронологию как активную очередь задач.
4. Не калибровать неродственные инструменты как одно baseline-действие.
5. Не применять все найденные `F*_ALLOW` колонки; использовать только активное действие паспорта.
6. Не продвигать `NO_GO`, zero-trade или one-trade experimental результаты в production.
7. Не считать diagnostic tournament baseline-решением.

## 11. Стандартный Workflow

Для каждого нового паспорта:

1. Положить или скопировать паспорт в `docs/CALIBRATION_NODE_CURRENT/passports/features/`.
2. Добавить/обновить блок и паспорт в `configs/calibration_action_passports.yaml`.
3. Создать одну исполняемую матрицу в `configs/calibration_matrices/passport_actions/`.
4. Проверить matrix allowlist.
5. Добавить runtime/backtest action gate, если его еще нет.
6. Запустить LONG.
7. Запустить SHORT.
8. Записать audit artifact в `reports/qa_gate/`.
9. Обновить current status и handoff docs.
10. Зафиксировать решение: `NO_GO`, `ZERO_TRADES`, `POSITIVE_TEST_CANDIDATE` или follow-up validation.

## 12. Текущий Статус Маршрута

F001-F083 audit findings закрыты для текущего паспортного маршрута:

1. Planned/missing ids `F024/F026/F027/F028/F030/F031/F032/F038/F039` закрыты follow-up прогонами.
2. `F017/F018` combined-vs-split принято как один Stochastic K/D паспорт.
3. Stale action-column hardening реализован и проверен.

Это не означает production GO.

## 13. Следующий Практический Шаг

Перед следующим действием используем этот файл как панель управления.

Рекомендованный следующий порядок:

1. Собрать финальный компактный F001-F083 result register.
2. Отдельно провалидировать единственный положительный test-кандидат `F051 SHORT` на нескольких днях.
3. Не создавать новый combination или ML layer до результата validation по кандидату.
