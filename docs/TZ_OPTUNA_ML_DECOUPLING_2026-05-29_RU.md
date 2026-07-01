# TZ: Разъединение контуров Optuna и ML (v1)

Дата: 2026-05-29  
Контур исполнения: `APTuna` (калибровка) отдельно от `ML runtime/training`.

## 1. Цель
1. Полностью разъединить калибровочный контур Optuna и ML-контур.
2. Запретить участие ML-сигнала в Optuna-калибровке.
3. Сохранить текущий ML-контур неизменным (read-only, без правок логики).
4. Вести калибровку на `1d/1d` как быстрый инженерный режим проверки качества кандидатов.

## 2. Текущее состояние (as-is)
1. Сейчас Optuna-контур использует ML-вероятности внутри objective/поиска.
2. Это смешивает роли:
   1. калибровка стратегии;
   2. ML-модель как источник сигналов в этом же цикле.
3. Для целевого режима требуется strict-decoupling.

## 3. Целевое состояние (to-be)
1. Optuna-контур:
   1. калибрует только параметры стратегии, фичей и гипотез;
   2. не использует ML-predict/predict_proba;
   3. работает в `signal_mode=long_only` или `short_only` (раздельно).
2. ML-контур:
   1. не меняется на этапе этой задачи;
   2. запускается только после утверждения калиброванного профиля.
3. Контракт передачи:
   1. Optuna публикует артефакт профиля стратегии;
   2. ML читает только утвержденный профиль;
   3. одновременный запуск "Optuna calibration + ML runtime decisions" запрещен.

## 4. Область работ
1. Разрешено менять:
   1. `APTuna/*`;
   2. `configs/calibration_full_matrix_v1.yaml`;
   3. `configs/optuna_engine.yaml`;
   4. файлы orchestration Optuna, относящиеся к калибровочному запуску.
2. Запрещено менять:
   1. `src/mlbotnav/pipeline_train_eval.py`;
   2. `src/mlbotnav/oos_evaluate.py`;
   3. production/runtime ML-ветку.

## 5. Режимы запуска
1. Calibration mode (обязательный для этого этапа):
   1. `search_engine=optuna`;
   2. ML signal backend = `off` (rule-only candidate scoring);
   3. `1d/1d`, `repeats=1`.
2. ML mode:
   1. Optuna `off`;
   2. используется только утвержденный профиль.

## 6. Обязательные параметры калибровки на этом этапе
1. Окно:
   1. train: `2026-05-19`;
   2. test: `2026-05-20`.
2. Ускоренный профиль:
   1. `ProcessWorkers=3`;
   2. `Threads=9`;
   3. `SearchWorkersPerProcess=3`.
3. Разделение режимов:
   1. отдельный прогон `long_only`;
   2. отдельный прогон `short_only`.

## 7. Гейты приемки
1. Infra gates:
   1. все workers завершаются `exit_code=0`;
   2. нет `search_failed`;
   3. `text_guard` = PASS.
2. Decoupling gates:
   1. в Optuna-run отсутствуют вызовы ML probability scoring;
   2. в логах/артефактах присутствует метка `ml_signal_backend=off`.
3. Quality gates:
   1. есть сделки (`oos_trades > 0`);
   2. нет деградации в "вечный no-trade";
   3. фиксируются метрики: `result_status`, `oos_net_return_pct`, `oos_trades`.

## 8. План внедрения (строгий порядок)
1. Шаг A: добавить флаг режима decoupling в Optuna-launcher и runtime (`ml_signal_backend=off`).
2. Шаг B: отключить ML probability path в objective при `ml_signal_backend=off`.
3. Шаг C: добавить telemetry-поля в отчет Optuna (`decoupled=true`, `ml_signal_backend=off`).
4. Шаг D: выполнить 1 smoke-run `short_only` и 1 smoke-run `long_only` на `1d/1d`.
5. Шаг E: зафиксировать результаты в `ACTIVE` и `CHANGELOG`.

## 9. Риски и контроль
1. Риск: резкое падение количества сделок после отключения ML-сигнала.
   1. Контроль: расширяем search-space только в Optuna-контуре (без правок ML).
2. Риск: скрытое смешение режимов.
   1. Контроль: жесткий guard `signal_mode != both` для Optuna.
3. Риск: поломка кодировки в документации.
   1. Контроль: обязательный `python -m mlbotnav.text_guard` после каждого шага.

## 10. Definition of Done
1. Контуры технически разъединены и подтверждены отчетами.
2. ML-контур не модифицирован.
3. Optuna-калибровка работает в `1d/1d` в ускоренном профиле `3x3`.
4. Хронология обновлена, `text_guard` PASS.
