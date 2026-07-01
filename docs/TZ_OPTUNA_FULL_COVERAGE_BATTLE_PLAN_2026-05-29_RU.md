# TZ_OPTUNA_FULL_COVERAGE_BATTLE_PLAN_2026-05-29_RU

Дата: 2026-05-29  
Контур: только Optuna-калибровка (ML-контур не трогаем)

## 1) Цель
1. Подключить и реально перебирать все калибруемые фичи и гипотезы в полном диапазоне `min..max` по `step/count`.
2. Убрать пропуски runtime-перебора (чтобы параметры не оставались «формально в YAML, но не в реальном поиске»).
3. Подготовить боевой режим калибровки по блокам: сначала блоки отдельно, потом комбо блоков.

## 2) Обязательные правила (MUST)
1. ML-контур изолирован: `ml_signal_backend=off`.
2. Режимы строго раздельно: `long_only` отдельно, `short_only` отдельно.
3. После каждого шага: `pip check`, `python -m mlbotnav.text_guard`, `python -m mlbotnav.readiness --show`.
4. Любой шаг фиксируется в `ACTIVE_WORK_ITEMS_RU.md` и `CHANGELOG_CHRONOLOGY_RU.md`.

## 3) Что уже есть (факт)
1. В конфиге и space подключено `68/68` фич и `20/20` гипотез.
2. Профили параметров `min/max/step/count` заполнены без пропусков.
3. Есть ускоренный профиль `3x3` (ProcessWorkers=3, Threads=9, Search/proc=3).

## 4) Что осталось доделать до полного боевого перебора
1. Runtime-условность профилей:
   1. Перебирать профили только для реально включенных блоков/гипотез/фич в trial.
   2. Убрать «раздувание» поиска параметрами выключенных сущностей.
2. Переключение фич на уровне feature-row:
   1. Сейчас часть выбора идет блочно.
   2. Нужно довести до строгого поведения: выключенная фича не попадает в расчет даже внутри включенного блока.
3. Явная матрица coverage-аудита:
   1. Отчет по каждому параметру: был ли выбран хотя бы раз, min-hit, max-hit, coverage-rate.
   2. Отдельно по фичам и гипотезам.
4. Блочная калибровка (stage battle):
   1. Stage B1: один блок за прогон (все остальные off).
   2. Stage B2: пары блоков.
   3. Stage B3: тройки блоков.
   4. Stage B4: финальный joint-search по shortlist блоков.
5. Фильтр качества кандидата:
   1. Не принимать `trades=0`.
   2. Не принимать кандидата с отрицательным OOS при наличии лучшего неотрицательного.
   3. Ввести штраф за «слишком сложный» профиль (чтобы не включалось все подряд без пользы).

## 5) План выполнения (строго по порядку)
1. P477: Runtime conditional-profile fix.
2. P478: Feature-level toggle enforcement fix.
3. P479: Coverage audit report (param hit-map + min/max reach).
4. P480: Stage B1 block-only runs (long/short).
5. P481: Stage B2 pair-block runs.
6. P482: Stage B3 triple-block runs.
7. P483: Stage B4 shortlist joint-search.
8. P484: Freeze best candidates + reproducibility rerun.
9. P485: Gate review + решение о боевой калибровке.

## 6) Оценка времени
1. До готовности «боевого калибрования» (то есть можно стартовать полноценный battle-run):
   1. 8-14 часов чистой работы.
2. До первого устойчивого рабочего baseline (не гарантия профита, но стабильный tradeful pipeline):
   1. 16-28 часов.
3. До статуса «условно боевой кандидат» (положительный/около нуля OOS на серии окон, без no-trade):
   1. 2-4 календарных дня итераций.

## 7) Критерии готовности к боевому этапу
1. Coverage-аудит показывает, что все калибруемые параметры реально участвовали в поиске.
2. Нет технических `search_failed`.
3. Нет битых кодировок и text guard всегда PASS.
4. Есть shortlist кандидатов с `trades>0` и без деградации в no-trade.

## 8) Команды запуска (ускоренный профиль)
```powershell
.\set_mlbotnav_env.ps1 -Threads 9
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 `
  -Mode short_only -WindowPolicy fixed_1d `
  -TrainDate 2026-05-19 -TestDate 2026-05-20 `
  -Threads 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 `
  -OptunaTrials 180 -OptunaTimeoutSec 420 -OptunaStage C -UseTemporaryUnlock
```

## 9) Запреты
1. Не смешивать ML-контур и Optuna-контур в одном запуске.
2. Не переходить к long/short joint mode.
3. Не трогать production-ветку до закрытия P485.
