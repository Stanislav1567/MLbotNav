# TZ_AKFP — Автокалибровка Фич/Гипотез Под Цель 300%/Мес

Дата: 2026-05-24  
Статус: ACTIVE  
Блок: `AKFP` (внешний оркестратор над ML-ядром, без ломки ядра)

## Источник ТЗ (Word)
1. Оригинал (как прислан): `C:\Users\007\Downloads\TZ_AKFP_avtokalibrator_agent.docx`
2. Рабочая извлеченная копия текста:
   - `reports/qa_gate/TZ_AKFP_avtokalibrator_agent_extracted.txt`
3. Текущий файл (`TZ_AKFP_300_MONTH_TARGET_2026-05-24_RU.md`) — структурированная и формализованная версия этого Word-ТЗ для внедрения в проект.

## 0. Цель и фиксация KPI
1. Основная цель: `NetReturn_30d >= 300%` (минимум), больше 300% — лучше.
2. Обязательное условие: long/short калибруются раздельно, затем объединяются.
3. Формула общего результата:
   - `R_total_30d = w_long * R_long_30d + w_short * R_short_30d`, где `w_long + w_short = 1`.
4. Важно:
   - `200% long + 200% short` при весах `50/50` дает `200%`, а не `300%`.
   - Чтобы получить `300%` при `50/50`, нужно примерно `400% + 200%` (или эквивалентная комбинация весов/доходностей).

## 1. Архитектура (два блока)
1. Блок 1 (`ML-Core`): существующий контур обучения/оценки/сигналов, не переписываем.
2. Блок 2 (`AKFP`): новый orchestration-sidecar:
   - управляет порядком калибровки;
   - выбирает кандидатов;
   - не меняет внутренние форматы отчетов текущего ядра.

## 2. Принципы калибровки (без full-grid)
1. Запрещено: полный сеточный перебор всех фич/гипотез/параметров.
2. Разрешено:
   - `ablation` (по одному блоку),
   - `random search`,
   - `successive halving`,
   - локальная доводка финалистов.
3. CPU политика:
   - hard limit `<=85%`,
   - контуры long/short выполняются последовательно в heavy-этапах.
4. Обязательное правило “без каши”:
   - отдельные прогоны по типам кандидатов,
   - раздельные артефакты long/short,
   - итоговый выбор только после повторной проверки, не по первому попавшемуся прогону.

## 2.1. Матрица перебора (обязательно)
1. Тип A: `HYP_ONLY` — только гипотезы (без доп. фич-блока).
2. Тип B: `FEAT_ONLY` — только фичи (без доп. гипотез-блока).
3. Тип C: `HYP_PLUS_FEAT` — гипотезы + фичи.
4. Тип D: `STRAT_BASELINE` — базовая стратегия без доп. блоков (контрольная точка).
5. Тип E: `COMBO_WORKING` — комбинации только из ранее подтвержденных рабочих элементов.

## 2.2. Анти-рандом правило выбора победителя (обязательно)
1. Запрещено выбирать победителя:
   - по одному случайному запуску,
   - по “первому положительному” результату.
2. Победитель выбирается только так:
   - кандидат проходит минимум `repeats=2` на одном окне,
   - затем проходит проверку на следующем holdout-окне,
   - затем сравнивается с incumbent по composite-score.
3. Если новый кандидат лучше только в одном запуске, но нестабилен в повторах — он уходит в `WEAK_TOOLS`, не в `FINAL_CONFIG`.

## 3. P1..P8 — План Внедрения AKFP

### P1. Contract Freeze
1. Зафиксировать вход/выход AKFP:
   - вход: symbol/timeframe/window/signal_mode/cpu budget.
   - выход: PASS/FAIL/RETRY + выбранный кандидат + причина.
2. Acceptance:
   - baseline регрессия PASS без изменения текущего ядра.

### P2. Budgeted Search Engine (без сетки)
1. Включить схему: `random -> halving -> local refine`.
2. Бюджет кандидатов на контур:
   - этап A (`HYP_ONLY`, `FEAT_ONLY`, `HYP_PLUS_FEAT`, `STRAT_BASELINE`): до 8 кандидатов (быстрый отсев),
   - этап B: 8 -> 4 -> 2,
   - этап C: топ-2 с `repeats=2` для подтверждения,
   - этап D: `COMBO_WORKING` только из подтвержденных рабочих блоков.
3. Acceptance:
   - минимум на 50% меньше дорогих прогонов vs full-grid.
   - в финале обязательно есть отчеты по всем типам A/B/C/D/E, ни один тип не пропущен.

### P3. CPU Governor Hardening
1. Рабочие лимиты:
   - `cpu_max_pct=85`,
   - `max_threads=6`,
   - `search_workers=4` (по умолчанию для AKFP).
2. Acceptance:
   - `CPU p95 <= 85%`,
   - нет sustained breach > 2 окон подряд.

### P4. Long/Short Isolation
1. Разделить контуры по артефактам/кэшу/negative memory:
   - `long_only` отдельно,
   - `short_only` отдельно.
2. Acceptance:
   - нет cross-contamination в отчетах и итоговых конфигурациях.

### P5. Anti-Overfit/Anti-Overfilter
1. Hard reject кандидата:
   - `gate.pass=false`,
   - `trades < 10`,
   - `abs(max_drawdown_pct) > 12`,
   - `no_trade_ratio_days > 0.70`.
2. Acceptance:
   - shortlist не деградирует по стабильности на holdout.

### P6. Risk Engine For Aggressive Target
1. Лимиты:
   - daily stop: `-2.0%`,
   - weekly stop: `-4.5%`,
   - monthly stop: `-9.0%`.
2. Profit lock:
   - после `+1.5%` за день риск на сделку снижается в 2 раза.
3. Acceptance:
   - риск-лимиты соблюдаются во всех контрольных прогонах.

### P7. Mandatory Gates Before Promote
1. Обязательные PASS:
   - `features_block_audit`,
   - `hypothesis_coverage_audit` (long/short),
   - `table_convergence_5plus`,
   - `audit_table_chain --require-trades`,
   - `orderbook_source_audit` (если active orderbook гипотезы),
   - `tz_gate_runner`,
   - `p72_freeze_ready_check --mode release`.
2. Acceptance:
   - 2 последовательных weekly цикла с полным PASS пакетом.

### P8. Rollout
1. Этапы:
   - shadow mode -> pilot long -> pilot short -> combined.
2. Acceptance:
   - rollback сценарий проверен,
   - production включение только после green-пакета P7.

## 4. Рабочий Алгоритм AKFP (операционный)
1. Baseline (без доп. блоков).
2. Отдельный проход `HYP_ONLY`.
3. Отдельный проход `FEAT_ONLY`.
4. Отдельный проход `HYP_PLUS_FEAT`.
5. Single-tool ablation внутри каждого типа.
6. Random sweep (12-24 точек на инструмент/тип).
7. Successive halving (отсев 65-88% слабых).
8. Local refine топ-5 кандидатов.
9. Сборка `COMBO_WORKING` только из подтвержденных рабочих элементов.
10. Финальный выбор по composite score:
   - доходность + стабильность + PF,
   - штраф за DD и overfilter.
11. Проверка победителя:
   - `repeats>=2` + holdout-pass + gate-pass.

## 5. KPI Pass/Fail
1. Главный KPI: `R_total_30d >= 300%`.
2. Side KPI:
   - `R_long_30d` и `R_short_30d` контролируются раздельно.
3. Risk KPI:
   - `MaxDD_30d` в лимите,
   - `NoTradeRatioDays` в лимите,
   - нет срыва CPU лимита.

## 6. Артефакты
1. `reports/akfp/*` — отдельный namespace AKFP.
2. Ссылки на текущие QA:
   - `reports/qa_gate/*`,
   - `reports/table_canon_current/*`.
3. Финальный результат:
   - `FINAL_CONFIG` + `BEST_COMBOS` + отчет по рискам.
4. Обязательные реестры AKFP:
   - `WORKING_TOOLS`,
   - `WEAK_TOOLS`,
   - `DANGEROUS_TOOLS`,
   - `DISABLED_TOOLS`.
5. Для каждого кандидата сохраняется карточка:
   - `candidate_id`, `candidate_type (A/B/C/D/E)`, `contour_id`,
   - параметры, метрики, причины pass/fail,
   - решение: `promote / hold / reject`.

## 7. Определение Готовности (Definition of Done)
1. Реализованы P1..P8 без изменения контрактов ML-ядра.
2. 2 последовательных weekly цикла прошли mandatory gates.
3. KPI 30d достигнут (`>=300%`) или документирован gap с планом корректировки.
4. Все решения воспроизводимы из артефактов.

## 8. Фиксация В Проекте (чтобы не потерялось)
1. Папка блока:
   - `AKFP/README_RU.md`
   - `AKFP/TZ_AKFP_IMPLEMENTATION_PLAN_RU.md`
2. Политика toggle:
   - `configs/akfp_policy.yaml`
3. Bridge-оркестратор:
   - `src/mlbotnav/akfp_bridge.py`
4. Runner:
   - `run_akfp_bridge.ps1`
5. Dry-run отчет:
   - `reports/qa_gate/akfp_bridge_*.json`
