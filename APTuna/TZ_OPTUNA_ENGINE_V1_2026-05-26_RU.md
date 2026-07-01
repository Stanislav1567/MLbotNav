# APTuna TZ: Optuna-движок калибровки (v1)

Дата: 2026-05-26  
Статус: DRAFT_FOR_APPROVAL  
Контур: только калибровка (без изменения execution-parity правил)

## 1. Цель
1. Ускорить калибровку фич/гипотез и убрать "вечный перебор" сеткой.
2. Делать калибровку условно:
1. включать/выключать блоки;
2. тюнить параметры только внутри включенных блоков.
3. Работать раздельно:
1. long контур отдельно;
2. short контур отдельно.

## 2. Что выбираем как движок
1. Движок: `Optuna` поверх текущего пайплайна (не переписывать весь ML-контур).
2. Sampler: `TPESampler(multivariate=True, group=True, seed=fixed)`.
3. Pruner: `MedianPruner` для раннего отсечения слабых trial.
4. Storage:
1. основной: Postgres `RDBStorage` (для resume и истории);
2. fallback локально: SQLite только для `n_jobs=1`.
5. Обязательная воспроизводимость:
1. фиксированный seed;
2. лог trial params + score + gate reasons + hashes артефактов.

## 3. Почему именно так
1. Сейчас в проекте тяжелый cartesian-перебор в `search_gate_candidate.py`; Optuna снимает комбинаторный взрыв.
2. В проекте уже есть матрица параметров с min/max/step и toggle:
1. `configs/calibration_full_matrix_v1.yaml`.
3. Можно внедрить поэтапно без ломки существующих раннеров.

## 4. Жесткие ограничения (MUST)
1. Минимум 1 блок всегда включен.
2. Long/short не смешивать.
3. Trial без сделок или с провалом gate получает сильный штраф.
4. Штраф за сложность:
1. за избыточное число включенных блоков;
2. за избыточное число включенных гипотез.
5. Победитель выбирается по OOS-устойчивости, а не по одному пику.

## 5. Поэтапный контур запуска
### Этап A (быстрый): long, 1d/1d
1. Train: день `D-1`, Test: день `D`.
2. Только `long_only`.
3. Небольшой бюджет trial (например 120-200) + pruning.
4. Цель: быстро отсеять мусор и получить top-K.

### Этап B (быстрый): short, 1d/1d
1. Аналогично этапу A, но только `short_only`.
2. Свой отдельный study и отдельные артефакты.

### Этап C (устойчивость): long/short отдельно на длинных окнах
1. Top-K из 1d/1d догоняется на 30/60 дней.
2. Итоговый выбор по median/p10/DD/gate pass rate.

## 6. Что интегрируем в код
1. Новый search-mode в оркестраторе:
1. `--search-engine grid|optuna`.
2. Новый runtime-слой:
1. `src/mlbotnav/optuna_space.py` (компиляция search space из YAML);
2. `src/mlbotnav/optuna_objective.py` (objective и штрафы);
3. `src/mlbotnav/optuna_engine.py` (study lifecycle, storage, resume, export).
3. Встраивание в текущий контур:
1. `src/mlbotnav/adaptive_auto_train.py` вызывает optuna-ветку вместо grid при `--search-engine optuna`.

## 7. Контракт search space (из текущего YAML)
1. Источник: `configs/calibration_full_matrix_v1.yaml`.
2. Используются:
1. `optuna_switches.block_switches`;
2. `feature_rows[].optuna_toggle`;
3. `hypothesis_rows[].optuna_toggle`;
4. `parameter_profiles` с `min/max/step/count/axis`.
3. Логика:
1. `use_block_<name>` -> true/false;
2. если true -> предлагаются параметры блока;
3. если false -> блок зануляется.

## 8. Objective (v1)
1. База: OOS `net_return_pct`.
2. Риск-компонента: штраф за drawdown.
3. Устойчивость: бонус за gate pass и наличие сделок.
4. Complexity penalty:
1. `lambda_block * active_blocks`;
2. `lambda_hyp * active_hypotheses`.
5. Final score:
1. `score = oos_net - a*abs(mdd) + b*gate_pass - c*complexity`.

## 9. Артефакты после каждого запуска
1. `reports/optuna/<mode>/study_summary_*.json`
2. `reports/optuna/<mode>/best_trials_topk_*.json`
3. `reports/optuna/<mode>/trial_history_*.csv`
4. Запись в:
1. `docs/ACTIVE_WORK_ITEMS_RU.md`
2. `docs/CHANGELOG_CHRONOLOGY_RU.md`

## 10. Границы v1 (что не делаем сразу)
1. Не переписываем весь backtest-контур.
2. Не объединяем long и short в один study.
3. Не запускаем длинные окна до прохождения 1d/1d sanity.

## 11. Критерий готовности v1
1. Long и short получают стабильные top-K на 1d/1d в разумное время.
2. Есть возможность resume study после остановки.
3. Все trial и решения воспроизводимы по артефактам.

## 12. Контракт с ML-контуром
1. Optuna не является частью боевого инференса ML.
2. Optuna работает как отдельный офлайн-контур и публикует профиль `strategy_profile_vN`.
3. ML-контур:
1. обучается на утвержденном `active_strategy_profile`;
2. в runtime не запускает Optuna-поиск.
4. Переключение профиля:
1. `candidate_profile` -> OOS/gate/parity -> `active_profile`;
2. без PASS переключение запрещено.

## 13. CPU-памятка для калибровки (обязательная)
1. Целевой потолок загрузки CPU для Optuna/калибровки: `85%`.
2. Если калибровка недогружает CPU (например 40-50%), разрешен контролируемый разгон:
1. увеличивать `search_workers` и/или `threads` ступенчато;
2. добавлять мощность до примерно `+30..35%` от текущего уровня, не переходя `85%` устойчиво.
3. Разгон делается только с наблюдением:
1. оператор смотрит фактическую загрузку CPU;
2. после каждого шага разгона проверяется время итерации и стабильность.
4. При признаках деградации (thrash, рост ошибок, нестабильные времена) откат к предыдущему стабильному профилю ресурсов обязателен.
5. Все изменения ресурcного профиля фиксируются:
1. `threads/search_workers/cpu_max_pct`;
2. дата/время;
3. эффект на длительность прогона.

## 14. SKV/Excel and MATB/Bot Navi Schema Contract (MUST)
1. Any new Optuna autocalibration parameter/column is valid only after synchronized update of all layers:
1. SKV tables/contour;
2. Excel outputs and formulas;
3. MATB/Bot Navi parser/field contract.
2. Strict update order:
1. declare field in schema contract;
2. add field to SKV generation;
3. add field to Excel headers/formulas;
4. update MATB parser/validator;
5. record step in `docs/ACTIVE_WORK_ITEMS_RU.md` and `docs/CHANGELOG_CHRONOLOGY_RU.md`.
3. Forbidden:
1. adding a field only in one layer;
2. reordering columns without contract-version note;
3. running calibration before schema-sync is complete.
4. Minimal audit after each column change:
1. Excel opens without errors;
2. required column exists in CSV/XLSX;
3. no name/type drift between SKV and MATB.
