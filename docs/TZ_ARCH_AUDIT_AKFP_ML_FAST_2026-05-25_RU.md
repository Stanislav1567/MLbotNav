# Архитектурный аудит ML-блока и AKFP-блока (ускорение к боевому прогону)

Дата: 2026-05-25  
Проект: `C:\Users\007\Desktop\MLbotNav`  
Фокус: контуры `ML` + `AKFP`, причины медленной/хрупкой калибровки, минимальный рефакторинг без ломки `CSV/XLSX/gates`.

## 1) Карта контуров и зависимостей

### 1.1 Верхний уровень (PowerShell -> Python)

- `C:\Users\007\Desktop\MLbotNav\run_p23_operator_unified.ps1`
  - вызывает: `mlbotnav.daily_long_short_cycle`, `mlbotnav.table_canon_pack`, `mlbotnav.table_convergence_5plus`, `mlbotnav.audit_table_chain`, `mlbotnav.features_block_audit`, `mlbotnav.orderbook_source_audit`, `mlbotnav.tz_gate_runner`, `mlbotnav.p72_freeze_ready_check`.

- `C:\Users\007\Desktop\MLbotNav\run_hypotheses_full_coverage_1d1d.ps1`
  - вызывает: `mlbotnav.adaptive_auto_train`, `mlbotnav.table_canon_pack`, `mlbotnav.table_convergence_5plus`, `mlbotnav.tz_gate_runner`, `mlbotnav.p72_freeze_ready_check`.

- `C:\Users\007\Desktop\MLbotNav\run_features_hypotheses_cycle.ps1`
  - вызывает: `mlbotnav.adaptive_auto_train` (short + long), затем chain/gates.

- `C:\Users\007\Desktop\MLbotNav\run_features_hypotheses_matrix.ps1`
  - вызывает `run_features_hypotheses_cycle.ps1` для 3 окон подряд.

- `C:\Users\007\Desktop\MLbotNav\run_akfp_bridge.ps1`
  - вызывает: `mlbotnav.akfp_bridge`.

### 1.2 Внутренний уровень (Python -> Python через subprocess)

- `C:\Users\007\Desktop\MLbotNav\src\mlbotnav\adaptive_auto_train.py`
  - вызывает: `mlbotnav.search_gate_candidate` -> `mlbotnav.pipeline_train_eval` -> `mlbotnav.oos_evaluate` (в каждом repeat).

- `C:\Users\007\Desktop\MLbotNav\src\mlbotnav\daily_long_short_cycle.py`
  - вызывает: `mlbotnav.adaptive_auto_train`, `mlbotnav.table_canon_pack`, `mlbotnav.preflight_window`, `mlbotnav.table_convergence_5plus`, `mlbotnav.hypothesis_coverage_audit`.

- AKFP-циклы:
  - `akfp_hyp_only_cycle.py`, `akfp_feat_only_cycle.py`, `akfp_hyp_plus_feat_cycle.py`, `akfp_combo_working_cycle.py`, `akfp_long_final_cycle.py`, `akfp_short_final_cycle.py`
  - все запускают `mlbotnav.adaptive_auto_train` (часть также `mlbotnav.hypothesis_coverage_audit`).

Итог: есть каскад `PS1 -> Python-оркестратор -> Python-оркестратор -> Python-исполнители`.

## 2) Где смешаны ответственности (и почему долго/хрупко)

### 2.1 Тяжелая упаковка таблиц смешана с калибровкой

Файл: `C:\Users\007\Desktop\MLbotNav\src\mlbotnav\table_canon_pack.py`  
Проблема: в каждом проходе создаются множественные `CSV/Parquet/XLSX` (включая `readable_tables_ru.xlsx`, `feature_frame_full.xlsx`, словари и др.).

Риск:
- I/O доминирует над ML-вычислением;
- lock Excel (`WinError 32`) роняет цепочку;
- лишние минуты на каждом шаге, особенно при многократных итерациях.

### 2.2 Калибровка и gate-проверки сцеплены в одном проходе

Файлы:
- `C:\Users\007\Desktop\MLbotNav\src\mlbotnav\daily_long_short_cycle.py`
- `C:\Users\007\Desktop\MLbotNav\run_p23_operator_unified.ps1`

Проблема: после поиска параметров сразу идет полный chain/gate. При AKFP это повторяется многократно.

Риск:
- каждый кандидат тащит полный QA-хвост;
- малейшая инфраструктурная проблема выглядит как "плохая стратегия".

### 2.3 Дублирование chain-шагов между контурами

Файлы:
- `run_features_hypotheses_cycle.ps1`
- `run_p23_operator_unified.ps1`
- `run_p22_table_chain_daily.ps1`

Проблема: одни и те же `table_canon/convergence/gates` запускаются из разных мест.

Риск:
- каскадный расход времени;
- разные скрипты могут брать разные "latest" артефакты;
- сложнее воспроизводить и дебажить.

### 2.4 AKFP COMBO масштабирется квадратично по времени

Файлы:
- `C:\Users\007\Desktop\MLbotNav\configs\akfp_policy.yaml`
- `C:\Users\007\Desktop\MLbotNav\src\mlbotnav\akfp_combo_working_cycle.py`

Факты:
- `execution.repeats=3`, `threads=8`, `search_workers=8`.
- `max_candidates_per_contour=128` (политика).
- На текущем наборе active-гипотез формируется ~`20` combo-кандидатов на контур, и каждый запускает `adaptive_auto_train`.

Риск:
- очень длинные "сутки" калибровки;
- при любой нестабильности тратятся часы без полезного сигнала.

### 2.5 Сканы "latest" по огромному `reports`

Файлы:
- `run_p24_latest_pass_report.ps1`
- `run_p26_audit_lock.ps1`

Факт: в `reports` > 35k файлов, wildcard-сканы делают `Get-ChildItem ... | Sort-Object LastWriteTimeUtc` многократно.

Риск:
- лишнее время на файловые операции;
- риск выбора не того артефакта при плотных/параллельных запусках.

## 3) Что разделить до боевого прогона (обязательно)

### 3.1 Разделить 3 стадии

1. `CALIBRATE` (только поиск/обучение/OOS, без XLSX/гейтов).  
2. `CHAIN_VALIDATE` (один раз на лучший кандидат окна).  
3. `PUBLISH` (top/card/пакет/чек-листы).

### 3.2 Разделить AKFP и operator-chain по роли

- AKFP не должен на каждом кандидате делать полный `P23`.
- `P23` запускать только после выбора лучшего кандидата (или top-K).

### 3.3 Разделить "рабочие" и "читаемые" артефакты

- Быстрый режим: `CSV+Parquet`.
- Читаемый режим (`XLSX`) — только финал шага/окна.

### 3.4 Зафиксировать контур long/short

- Сохранять строгую раздельность (`contour_id`, отдельный `negative_setup_memory.json`, отдельный top namespace).
- Не смешивать режимы в одном кэше и одном shortlist.

## 4) Минимальный план рефакторинга без ломки CSV/XLSX/gates

## R0. Контракт совместимости (без изменений форматов)
1. Не менять имена текущих финальных файлов (`candles_canonical.xlsx`, `feature_frame.xlsx`, `readable_tables_ru.xlsx`, `tz_gate_*.json`, `p72_*.json`).
2. Добавить новый "быстрый" режим, но оставить текущий default-режим как legacy-safe.

Риск: низкий.

## R1. Быстрый профиль table-canon (I/O split)
Файлы:
- `src/mlbotnav/table_canon_pack.py`
- `run_p23_operator_unified.ps1`

Изменение:
1. Добавить флаг `--artifact-profile fast|full`.
2. `fast`: только обязательные `CSV/Parquet` + `audit_chain_report` prerequisites.
3. `full`: текущее поведение с XLSX (как сейчас).

Риск: средний (важно не сломать ожидания `audit_table_chain`).

## R2. Отвязать калибровку от полного gate-хвоста
Файлы:
- `src/mlbotnav/daily_long_short_cycle.py`
- `run_p23_operator_unified.ps1`
- `src/mlbotnav/akfp_bridge.py`

Изменение:
1. `daily_long_short_cycle`: режим `--stage calibrate_only|with_chain`.
2. AKFP-кандидаты гонять в `calibrate_only`.
3. `with_chain` запускать только на best candidate (или top-2).

Риск: средний.

## R3. Стабилизировать выбор артефактов (убрать "latest-гонки")
Файлы:
- `run_p24_latest_pass_report.ps1`
- `run_p26_audit_lock.ps1`
- `run_p27_handoff_package.ps1`

Изменение:
1. Передавать везде `--source-p23-report-path`/явные pinned пути, не полагаться на wildcard latest.
2. Скан `reports` оставить только как fallback.

Риск: низкий.

## R4. Ограничить AKFP-combo бюджет
Файлы:
- `configs/akfp_policy.yaml`
- `src/mlbotnav/akfp_combo_working_cycle.py`

Изменение:
1. Ввести stage-бюджеты:
   - smoke: max 4 combo/contour;
   - tuning: max 8;
   - release: max 12.
2. Ранний prune по preflight + no-trade heuristics (до тяжелого train-eval).

Риск: низкий/средний (возможен пропуск редких комбинаций, но резкий выигрыш по времени).

## R5. Агентный слой в AKFP (без вмешательства в ML-ядро)
Файлы:
- `src/mlbotnav/akfp_bridge.py`
- `src/mlbotnav/akfp_profiles_audit.py`
- новый: `src/mlbotnav/akfp_agent_router.py` (sidecar)

Изменение:
1. Агент не торгует и не обучает модель напрямую.
2. Агент делает:
   - выбор окна,
   - выбор профиля (`smoke/tuning/release`),
   - бюджет кандидатов,
   - остановку по условиям качества/времени,
   - формирование "что запускать дальше".

Риск: средний (нужен строгий контракт вход/выход JSON).

## R6. Очистка кодировок RU (доки/labels)
Файлы:
- `docs/*.md` (актуальные)
- `AKFP/*.md`
- `configs/features_block.yaml` (`ru_labels`)

Изменение:
1. Зафиксировать UTF-8 без перекодировок.
2. Проверка pre-commit: отсутствуют mojibake-последовательности.

Риск: низкий, польза высокая (читаемость и отсутствие кракозябр).

## 5) Приоритет до боевого прогона

1. `R1` (быстрый профиль артефактов)  
2. `R2` (развязка calibrate vs chain)  
3. `R4` (бюджеты AKFP-combo)  
4. `R3` (pinned artifact selection)  
5. `R5` (агентный sidecar)  
6. `R6` (кодировки и чистка текстов)

## 6) Definition of Done перед боевым прогоном

1. Калибровка 1d->1d (`long` и `short` отдельно) завершается <= 20-30 минут на одном профиле tuning.
2. Полный chain/gate запускается 1 раз на выбранного кандидата, а не на каждый кандидат.
3. Все текущие `CSV/XLSX/gates` артефакты продолжают формироваться в режиме `full` без изменения имен.
4. Нет случайного выбора "latest" при наличии pinned пути.
5. Отчеты AKFP и ML однозначно разделены по namespace (`contour_id`, каталоги, memory).
