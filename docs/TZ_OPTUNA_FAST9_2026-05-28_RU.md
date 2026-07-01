# TZ: Optuna FAST-9 на 1d калибровке (без перегруза CPU)

Дата: 2026-05-28
Контур: `APTuna` + `MLBotNav` (VS Code, `.venv`)

## 1. Цель
1. Обеспечить эффективные `9` воркеров в Optuna-контуре 1d/1d.
2. Ускорить перебор без выхода за целевой CPU-потолок `85%`.
3. Сохранить раздельный контур `short_only` и `long_only` (без смешивания).

## 2. Факт блокера (подтверждено)
1. `workers_used` ограничивается формулой:
   - `src/mlbotnav/optuna_search_candidate.py:1147`
   - `effective_n_jobs = min(requested_jobs, len(horizons))`
2. В policy было `7` горизонтов:
   - `configs/preflight_policy.yaml` (`horizons_grid`)
3. Поэтому при `SearchWorkers=9` фактически получалось `workers_used=7`.

## 3. Принятое решение
1. Без изменения логики движка (безопасный путь A).
2. Увеличить дефолтный `horizons_grid` до `9` значений:
   - `1,2,3,4,5,6,8,12,16`
3. Это дает возможность получить `workers_used=9` при `SearchWorkers=9`.

## 4. Правила запуска (только VS Code + venv)
1. Обязательная среда:
   - `\.venv\Scripts\Activate.ps1`
   - `\set_mlbotnav_env.ps1 -Threads 9`
2. Базовый ускоренный запуск:
   - `APTuna/run_optuna_1d1d_stagec.ps1`
   - `Threads=9`, `SearchWorkers=9`
3. CPU-контроль:
   - цель `<=85%` средняя загрузка,
   - при длительном >85% уменьшать `SearchWorkers` до `8`,
   - при стабильном недогрузе <55% расширять search-space (не threads).

## 5. Порядок проверки (DoD)
1. Инфра-проверка:
   - нет `search_failed`,
   - PostgreSQL/Optuna storage доступен.
2. Скорость:
   - в `reports/pipeline/optuna_search_candidate_*.json`:
   - `workers_requested=9`,
   - `workers_used=9`,
   - `horizons_count=9`.
3. Качество:
   - фиксируем `result_status`, `oos_net_return_pct`, `oos_trades`,
   - если `goal_fail` — это quality-ветка, не infra-блокер.

## 6. Что не делаем на этом шаге
1. Не отключаем cap по горизонтам в коде.
2. Не меняем execution-логику входа/выхода.
3. Не смешиваем long/short в одном запуске.

## 7. Следующий шаг после FAST-9
1. Короткий smoke-run 1d/1d для подтверждения `workers_used=9`.
2. После подтверждения — переход к quality-итерациям по short-only.

## 8. Обновленный профиль скорости (зафиксировано 2026-05-28)
1. Базовый рабочий профиль для локального ПК:
   - `Threads=9`
   - `SearchWorkers=9`
   - `storage=postgresql`
   - `horizons_count=9`
2. Контроль ускорения обязателен на каждом прогоне:
   - `workers_requested=9`
   - `workers_used=9`
   - `forced_single_worker=false`
3. CPU-политика:
   - целевой рабочий диапазон: `60-85%`
   - при длительном `<55%` расширяем search-space (trials/time window), а не увеличиваем threads выше 9
   - при длительном `>85%` уменьшаем `SearchWorkers` до `8`

## 9. Приоритеты до боевого запуска (строгий порядок)
1. Завершить активный heavy-run `P371` и снять финальный DoD-срез ускорения.
2. Подтвердить автозапуск `P375` после release lock и старт в профиле `9/9`.
3. Закрыть quality-ветку:
   - минимум один стабильный проход `short_only` и один `long_only` без infra-ошибок
   - валидация качества по `result_status/oos_net_return_pct/oos_trades`
4. Убрать policy-дрейф горизонтов:
   - синхронизировать `stage_plan.yaml` и `preflight_policy.yaml` как единый источник truth для grid горизонтов.
5. Финальный pre-release smoke:
   - 1d/1d quick check
   - multiday check
   - post-audits PASS (`ledger_audit`, `text_guard`)

## 10. Оценка времени до боевого запуска (as of 2026-05-28)
1. Завершение `P371` + автопереход и контроль старта `P375`: `~2-4 часа`.
2. Quality-итерации (short/long) до приемлемого кандидата: `~1-2 рабочих дня`.
3. Финальная стабилизация и pre-release smoke: `~0.5-1 рабочий день`.
4. Итого реалистичный коридор до боевого запуска:
   - оптимистично: `~2 дня`
   - реалистично: `~3-4 дня`
   - при повторных quality-fail: `~5+ дней`

## 11. Критерий «готово к бою»
1. Инфра:
   - `storage=postgresql`
   - `workers_used=9`
   - `forced_single_worker=false`
   - отсутствие `search_failed`
2. Качество:
   - стабильный положительный OOS на согласованном окне
   - приемлемая просадка и число сделок по ТЗ
3. Операционно:
   - без конфликтов runtime-lock
   - хронология и ACTIVE обновлены по каждому шагу

## 12. Стратегия X3 (ускорение прогонов в 3 раза)
1. Принцип:
   - ускоряем не только CPU, а уменьшаем число «пустых» вычислений;
   - тяжелые проверки запускаем только для кандидатов, прошедших быстрые ворота.
2. Запрещенный паттерн:
   - сразу запускать длинный `repeats=16` на всем поисковом пространстве.
3. Обязательный staged-пайплайн:
   1. `SCOUT` (быстрый отбор):
      - окно: `1d/1d` или `3d/3d`;
      - `repeats=1`;
      - `OptunaTrials=120..180`;
      - `OptunaTimeoutSec=300`;
      - цель: отсечь слабые зоны и оставить top-кандидаты.
   2. `WORK` (рабочий отбор):
      - окно: `3d/3d` или `7d/7d`;
      - `repeats=1..3`;
      - `OptunaTrials=240..360`;
      - `OptunaTimeoutSec=600..900`;
      - цель: стабилизировать shortlist.
   3. `BATTLE` (финальное подтверждение):
      - окно: multiday (`30d/30d` или согласованное);
      - `repeats=8..16` только для shortlisted;
      - `OptunaTrials=300..600`;
      - `OptunaTimeoutSec=1200+`.
4. Профиль параллелизма по умолчанию:
   - основной режим: `ProcessPool=3`, суммарно `Threads=9`, `SearchWorkers=9`;
   - один процесс (`UseProcessPool` off) разрешен только для быстрых smoke/debug.
5. Gate на остановку (timebox):
   - если за `N` минут нет улучшения score/OOS и нет роста trade-quality, текущий прогон останавливается;
   - следующий прогон стартует с новым single-change параметром.
6. Ожидаемый эффект X3:
   - за счет staged-ворот и timebox суммарное время до полезного кандидата снижается примерно в `~3x` относительно «длинных прогонов на всем пространстве».

## 13. Командные пресеты (стандарт)
1. SCOUT:
   - `ProcessPool=off`, `Threads=9`, `SearchWorkers=9`, `Trials=180`, `Timeout=300`, `repeats=1`.
2. WORK:
   - `UseProcessPool -ProcessWorkers 3 -SearchWorkersPerProcess 3`, `Threads=9`, `Trials=300`, `Timeout=900`, `repeats=1..3`.
3. BATTLE:
   - `UseProcessPool -ProcessWorkers 3 -SearchWorkersPerProcess 3`, `Threads=9`, `Trials=400..600`, `Timeout=1200..1800`, `repeats=8..16`.
