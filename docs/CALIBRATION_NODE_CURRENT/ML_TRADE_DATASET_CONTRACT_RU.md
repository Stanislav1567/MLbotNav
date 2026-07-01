# ML Trade Dataset Contract

Дата: 2026-06-23
Status: STAGE_8_1_CLOSED_PASS
План: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`
Current WBS item: 8.2 Run Optuna calibration
Status override: STAGE_8_1_CLOSED_PASS

## 58. Stage 8.1 Large Clean Window

Status: `CLOSED_PASS`.

Closed WBS item: `8.1 Fix large clean window`.
Audit: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.
Manifest: `configs/ml_large_clean_window_manifest.yaml`.

Window: train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`, data layer `core`.

Checks: large clean window audit `PASS`, missing files `0`, focused tests `22/22 OK`.

Boundary: Optuna calibration, package creation, ML ingest, and ML training were not started.

Next strict WBS item: `8.2 Run Optuna calibration`.

## 57. Stage 7 Closeout

Status: `STAGE_7_CLOSED_PASS`.

Closed WBS item: `7.6 Stage 7 closeout`.
Audit: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.
Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.
Dataset manifest: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`.

Closed bridge: `window -> package -> approved registry -> ML ingest dataset`.

Final checks: smoke window `PASS`, approved registry `PASS`, ML ingest `PASS`, dataset contract `PASS`, focused tests `67/67 OK`.

Boundary: ML training was not started.

Next strict WBS item: `8.1 Fix large clean window`.

## 56. Stage 7.5 ML Ingest

Status: `CLOSED_PASS`.

Closed WBS item: `7.5 Run ML ingest`.
Audit: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.
Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.
Dataset manifest: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`.

Dataset builder: `PASS`, packages total `1`, rows total `1177`.
Dataset contract: `PASS`, rows `1177`, failed rows `0`, missing columns `0`.
Focused ingest tests: `24/24 OK`.

Boundary: ML training was not started.

Next strict WBS item: `7.6 Stage 7 closeout`.

## 55. Stage 7.4 Approved Registry

Status: `CLOSED_PASS`.

Closed WBS item: `7.4 Add package to approved registry`.
Audit: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.
Approved package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Registry status: `HAS_APPROVED_PACKAGES`.
Approved count: `1`.
Package status: `APPROVED_FOR_ML`.
Audit decision: `GO_FOR_ML`.

Checks: registry validator `PASS`, admission status `PASS`, registry reader `PASS`, package contract/alignment `PASS`, focused tests `42/42 OK`.

Boundary: dataset builder was not run in this step; ML training was not started.

Next strict WBS item: `7.5 Run ML ingest`.

## 54. Stage 7.3 Package Contract Audit

Status: `CLOSED_PASS`.

Closed WBS item: `7.3 Run package contract audit`.
Audit: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.
Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Contract audit: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T183343Z.json`.
Rows: `1177`, failed rows: `0`, missing columns: `0`.
Direct API validation: `PASS` in `approved_mode=False` and `approved_mode=True`.
Package alignment audits: `PASS`.
Registry boundary checks: `PASS`, approved count `0`.
Focused tests: `48/48 OK`.
Text guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T183955Z.json`.

Boundary: no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

Next strict WBS item: `7.4 Add package to approved registry`.

## 53. Stage 7.2 Smoke Package

Status: `CLOSED_PASS`.

Closed WBS item: `7.2 Build test package`.
Audit: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.
Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Package status: `DRAFT`.
Package ML decision: `NO_GO_FOR_ML`.
Contract audit: `PASS`.
Alignment audits: `PASS`.

Boundary: no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

Next strict WBS item: `7.3 Run package contract audit`.

## 52. Stage 7.1 Smoke Window

Status: `CLOSED_PASS`.

Closed WBS item: `7.1 Smoke run`.
Audit: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.
Manifest: `configs/ml_smoke_run_manifest.yaml`.

Window: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`.

Boundary: no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

Next strict WBS item: `7.2 Build test package`.

## 51. Stage 6 Closeout

Status: `STAGE_6_CLOSED_PASS`.

Closed WBS item: `6.6 Stage 6 closeout`.

Closed:
1. `6.1 Check run_id alignment`
2. `6.2 Check passport context`
3. `6.3 Check calibration params`
4. `6.4 Check data windows`
5. `6.5 Check admission status`
6. `6.6 Stage 6 closeout`

Checks:
1. Focused ML tests: `121/121 OK`.
2. All five alignment audits: `PASS / NO_APPROVED_PACKAGES`.
3. Registry validator/reader: `PASS`.
4. Dataset builder: `PASS / NO_APPROVED_PACKAGES`.
5. Reject-log builder: `PASS / NO_REJECTIONS`.

Audit: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.

Next strict WBS item: `7.1 Smoke run`.


## 50. Stage 6.5 Admission Status

Status: `CLOSED_PASS`.

Closed WBS item: `6.5 Check admission status`.

Created:
1. `src/mlbotnav/ml_alignment_admission_status_audit.py`
2. `tests/test_ml_alignment_admission_status_audit.py`

Rule:
1. Registry entry status must be `APPROVED_FOR_ML`.
2. `manifest.json.status` must be `APPROVED_FOR_ML`.
3. `calibration_package.json.status` must be `APPROVED_FOR_ML`.
4. `audit.md` must contain `ML decision: GO_FOR_ML`.
5. Any mismatch returns `FAIL`.

Checks:
1. New tests: `6/6 OK`.
2. Focused ML tests: `121/121 OK`.
3. Real registry result: `PASS / NO_APPROVED_PACKAGES`.

Audit: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.

Next strict WBS item: `6.6 Stage 6 closeout`.


## 49. Stage 6.4 Data Windows Alignment

Status: `CLOSED_PASS`.

Closed WBS item: `6.4 Check data windows`.

Created:
1. `src/mlbotnav/ml_alignment_data_windows_audit.py`
2. `tests/test_ml_alignment_data_windows_audit.py`

Rule:
1. `manifest.json`, `trade_log.csv`, and package-local `source_reports/oos_report.json` must match on `data_layer`, `train_start`, `train_end`, `test_start`, and `test_end` when OOS report exposes those fields.
2. Missing, invalid, unordered, or different windows return `FAIL`.
3. Admission status is checked separately in WBS item `6.5`.

Checks:
1. New tests: `8/8 OK`.
2. Focused ML tests: `115/115 OK`.
3. Real registry result: `PASS / NO_APPROVED_PACKAGES`.

Audit: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.

Next strict WBS item: `6.5 Check admission status`.


## 48. Stage 6.3 Calibration Params Alignment

Status: `CLOSED_PASS`.

Closed WBS item: `6.3 Check calibration params`.

Created:
1. `src/mlbotnav/ml_alignment_calibration_params_audit.py`
2. `tests/test_ml_alignment_calibration_params_audit.py`

Rule:
1. `calibration_package.json.calibration_params`, `trade_log.csv.calibration_params_json`, and package-local `source_reports/oos_report.json.calibration_params` must match when OOS report exists.
2. Missing, invalid, empty, or different params return `FAIL`.
3. Data windows are checked separately in WBS item `6.4`.

Checks:
1. New tests: `7/7 OK`.
2. Focused ML tests: `107/107 OK`.
3. Real registry result: `PASS / NO_APPROVED_PACKAGES`.

Audit: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.

Next strict WBS item: `6.4 Check data windows`.


## 47. Stage 6.2 Passport Context Alignment

Status: `CLOSED_PASS`.

Closed WBS item: `6.2 Check passport context`.

Created:
1. `src/mlbotnav/ml_alignment_passport_context_audit.py`
2. `tests/test_ml_alignment_passport_context_audit.py`

Rule:
1. `manifest.json`, `calibration_package.json`, and `trade_log.csv` must match on `block_id`, `passport_id`, and `action_id`.
2. Missing context or any mismatch returns `FAIL`.
3. Calibration params are checked separately in WBS item `6.3`.

Checks:
1. New tests: `6/6 OK`.
2. Focused ML tests: `100/100 OK`.
3. Real registry result: `PASS / NO_APPROVED_PACKAGES`.

Audit: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.

Next strict WBS item: `6.3 Check calibration params`.


## 46. Stage 6.1 Run ID Alignment

Status: `CLOSED_PASS`.

Closed WBS item: `6.1 Check run_id alignment`.

Created:
1. `src/mlbotnav/ml_alignment_run_id_audit.py`
2. `tests/test_ml_alignment_run_id_audit.py`

Rule:
1. `manifest.json.run_id`, `calibration_package.json.run_id`, and every `trade_log.csv.run_id` must match.
2. Missing `run_id` or any mismatch returns `FAIL`.
3. The audit reads only approved registry packages, or one explicit package path when run manually.

Checks:
1. New tests: `5/5 OK`.
2. Focused ML tests: `94/94 OK`.
3. Real registry result: `PASS / NO_APPROVED_PACKAGES`.

Audit: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.

Next strict WBS item: `6.2 Check passport context`.


## 1. Назначение таблицы

ML trade dataset - это каноническая таблица сделок и сигналов, которую ML-контур имеет право читать после ручного допуска calibration package.

Таблица нужна не для хранения всех промежуточных Optuna экспериментов, а для обучения ML на утвержденных результатах:

1. откалиброванный паспорт;
2. action gate;
3. параметры калибровки;
4. сигнал входа;
5. факт сделки;
6. выход из сделки;
7. итог сделки;
8. outcome labels.

## 2. Кто пишет таблицу

Писатель таблицы:

1. backtest/OOS контур после применения конкретного passport action;
2. package builder, который собирает утверждаемый ML candidate package;
3. alignment/audit tooling, если нужно нормализовать row-level metadata.

Optuna напрямую не пишет финальный ML dataset. Optuna только создает исходные калибровочные артефакты, из которых потом собирается candidate package.

## 3. Кто читает таблицу

Читатель таблицы:

1. ML ingest;
2. ML training/evaluation контур;
3. audit tools, которые проверяют соответствие JSON и CSV.

ML не читает старые Optuna папки напрямую. ML читает только пакеты, внесенные в approved registry со статусом `APPROVED_FOR_ML`.

## 4. сточник допуска в ML

Единственный источник допуска:

`configs/ml_approved_calibration_packages.yaml`

Правило:

1. Если package отсутствует в registry, ML не читает package.
2. Если status не равен `APPROVED_FOR_ML`, ML не читает package.
3. Если contract audit не равен `PASS`, ML не читает package.
4. Если data layer не clean `core`, ML не читает package как clean training input.

Детализация `1.5`:

ML admission rule состоит из пяти обязательных условий.

| Условие | Обязательность | сточник | Проверка | При ошибке |
|---|---|---|---|---|
| package есть в approved registry | required | `configs/ml_approved_calibration_packages.yaml` | `run_id` найден | `ML_ADMISSION_DENY` |
| registry status = `APPROVED_FOR_ML` | required | approved registry | status exact match | `ML_ADMISSION_DENY` |
| package manifest валиден | required | `reports/ml_candidates/<run_id>/manifest.json` | JSON parse + required fields | `ML_ADMISSION_DENY` |
| contract audit = `PASS` | required | package audit / alignment audit | status exact match | `ML_ADMISSION_DENY` |
| data layer clean | required | manifest / package metadata | `data_layer = core` для clean ML input | `ML_ADMISSION_DENY` |

Правило `1.5`: ML ingest не имеет права читать пакет, если хотя бы одно admission condition не выполнено.

### 4.1. Approved registry format

Файл:

`configs/ml_approved_calibration_packages.yaml`

Минимальный формат:

```yaml
approved_packages:
  - run_id: example_run_id
    status: APPROVED_FOR_ML
    package_path: reports/ml_candidates/example_run_id
    approved_by: manual
    approved_at_utc: "2026-06-23T00:00:00Z"
    comment: "manual approval after OOS and contract audit"
```

Готово, когда: формат registry записан и не требует чтения старых Optuna папок напрямую.

### 4.2. Разрешенный статус для ML ingest

Единственный статус, который ML ingest имеет право читать:

`APPROVED_FOR_ML`

Все остальные статусы являются отказом.

Готово, когда: контракт явно запрещает ML ingest читать `DRAFT`, `NEEDS_AUDIT`, `REJECTED`, `VALIDATION_FAIL`, `NO_GO`.

### 4.3. Запрещенные статусы

ML ingest запрещено читать package со статусами:

1. `DRAFT`
2. `NEEDS_AUDIT`
3. `REJECTED`
4. `VALIDATION_FAIL`
5. `NO_GO`
6. `UNKNOWN`
7. пустой status

Если такой package найден, результат должен быть `ML_ADMISSION_DENY`, а не silent skip.

Готово, когда: validator/audit обязан писать причину отказа.

### 4.4. Required admission files

Для допуска в ML package должен иметь:

1. `manifest.json`
2. `calibration_package.json`
3. `trade_log.csv`
4. `audit.md`
5. contract/alignment audit со статусом `PASS`

Если любого файла нет, ML ingest не читает package.

Готово, когда: missing file дает `ML_ADMISSION_DENY`.

### 4.5. Data layer rule

Для clean ML training input допускается только:

`data_layer = core`

Запрещено как clean input:

1. `raw`
2. `quarantine`
3. пустой `data_layer`
4. неизвестный `data_layer`

сключение возможно только отдельным статусом будущего debug/research контура, но не через `APPROVED_FOR_ML`.

Готово, когда: `raw/quarantine` package не может пройти как `APPROVED_FOR_ML`.

### 4.6. Manual approval rule

Допуск в ML всегда ручной на этом этапе.

Обязательные поля registry:

1. `approved_by`
2. `approved_at_utc`
3. `comment`

Без этих полей package не считается вручную подтвержденным.

Готово, когда: registry без manual approval metadata дает `ML_ADMISSION_DENY`.

### 4.7. No automatic Optuna-to-ML rule

Optuna runtime не имеет права автоматически добавлять package в approved registry.

Разрешено:

1. Optuna создает калибровочные отчеты.
2. Package builder собирает candidate package.
3. Audit проверяет package.
4. Человек вручную добавляет запись в approved registry.
5. ML ingest читает только registry.

Запрещено:

1. ML ingest сканирует `reports/optuna/*` напрямую.
2. ML ingest сканирует `reports/pipeline/*` напрямую без package.
3. Optuna сама ставит `APPROVED_FOR_ML`.

Готово, когда: это правило зафиксировано до реализации ingest.

## 5. Обязательные группы полей

Required columns делятся на четыре группы.

### 5.1. Run context

Обязательные поля:

1. `run_id`
2. `symbol`
3. `timeframe`
4. `data_layer`
5. `train_start`
6. `train_end`
7. `test_start`
8. `test_end`

Детализация `1.2`:

| Поле | Обязательность | сточник | Формат | Проверка |
|---|---|---|---|---|
| `run_id` | required | package builder / run manifest | non-empty string | одинаковый во всех package файлах и CSV |
| `symbol` | required | pipeline/OOS report | string, пример `SOLUSDT` | не пустой, совпадает с report |
| `timeframe` | required | pipeline/OOS report | canonical string, пример `1m` | не пустой, совпадает с report |
| `data_layer` | required | command/manifest | string, для clean ML только `core` | `raw/quarantine` не допускается как clean input |
| `train_start` | required | command/manifest | `YYYY-MM-DD` | дата валидна, `train_start <= train_end` |
| `train_end` | required | command/manifest | `YYYY-MM-DD` | дата валидна, окно совпадает с report |
| `test_start` | required | command/manifest | `YYYY-MM-DD` | дата валидна, `test_start <= test_end` |
| `test_end` | required | command/manifest | `YYYY-MM-DD` | дата валидна, окно совпадает с report |

Правило `1.2`: если любое поле run context отсутствует или пустое, dataset получает статус `CONTRACT_FAIL`.

### 5.2. Passport context

Обязательные поля:

1. `block_id`
2. `passport_id`
3. `action_id`
4. `side`
5. `calibration_params_json`

Детализация `1.2`:

| Поле | Обязательность | сточник | Формат | Проверка |
|---|---|---|---|---|
| `block_id` | required | passport registry / package manifest | string, пример `B001` | не пустой, совпадает с manifest |
| `passport_id` | required | passport registry / package manifest | string, пример `F051` | не пустой, совпадает с manifest |
| `action_id` | required | passport registry / active action gate | string, пример `F051_BOSDOWN_ALLOW` | совпадает с active gate column |
| `side` | required | signal mode / trade row | enum: `LONG`, `SHORT`, `BOTH`, `long_only`, `short_only` or numeric side mapping | не пустой, согласован с signal mode |
| `calibration_params_json` | required | Optuna selected calibration params | canonical JSON string | парсится как JSON и совпадает с package/report params |

Правило `1.2`: если паспортный контекст отсутствует, ML не имеет права угадывать его по имени файла.

### 5.2.1. Canonical mapping для `side`

Для CSV допускается хранение numeric `side` из backtest, но ML contract должен иметь понятную сторону.

Mapping:

1. `1` -> `LONG`
2. `-1` -> `SHORT`
3. `0` -> `NO_TRADE`

Для package-level metadata допускается `long_only`, `short_only`, `both`, но row-level trade side должен быть приведен к `LONG`, `SHORT` или `NO_TRADE`.

Готово, когда: mapping записан и validator умеет отличать side mode от row-level trade side.

### 5.2.2. Canonical JSON для `calibration_params_json`

`calibration_params_json` должен быть:

1. валидным JSON object;
2. отсортированным по ключам при записи, если это делает package builder;
3. без пустого object для активного passport action;
4. одинаковым между `calibration_package.json`, `oos_report.json` и `trade_log.csv`.

Готово, когда: mismatch между JSON report и CSV дает `CONTRACT_FAIL`.

### 5.3. Entry/exit fields

Обязательные поля:

1. `entry_signal_time_utc`
2. `entry_time_utc`
3. `exit_time_utc`
4. `entry_price`
5. `exit_price`
6. `exit_reason`
7. `net_return`
8. `net_pnl_usd`

Детализация `1.3`:

| Поле | Обязательность | сточник | Формат | Проверка |
|---|---|---|---|---|
| `entry_signal_time_utc` | required | signal row / backtest row | UTC ISO timestamp | не пустой для trade row; для `NO_TRADE` допускается пустой только если row не используется как trade sample |
| `entry_time_utc` | required | backtest execution | UTC ISO timestamp | не пустой для trade row; `entry_time_utc >= entry_signal_time_utc` |
| `exit_time_utc` | required | backtest execution | UTC ISO timestamp | не пустой для trade row; `exit_time_utc >= entry_time_utc` |
| `entry_price` | required | backtest execution | positive float | `> 0` для trade row |
| `exit_price` | required | backtest execution | positive float | `> 0` для trade row |
| `exit_reason` | required | backtest execution | enum string | один из разрешенных exit reasons |
| `net_return` | required | backtest summary row | float | число, может быть отрицательным, нулевым или положительным |
| `net_pnl_usd` | required | backtest summary row | float | число, может быть отрицательным, нулевым или положительным |

Правило `1.3`: если строка является сделкой (`side = LONG` или `side = SHORT`), все entry/exit поля обязательны и не могут быть пустыми.

### 5.3.1. Разрешенные `exit_reason`

Разрешенные значения:

1. `tp`
2. `sl`
3. `sl_ambiguous`
4. `timeout`
5. `end_of_data`
6. `manual_close`, зарезервировано для будущего live/paper контура
7. `unknown`, допускается только для legacy/debug rows и не допускается для `APPROVED_FOR_ML`

Готово, когда: validator не пропускает trade row с пустым или неизвестным `exit_reason`.

### 5.3.2. Entry signal time vs entry execution time

Разница:

1. `entry_signal_time_utc` - время свечи/строки, где появился сигнал.
2. `entry_time_utc` - фактическое время исполнения входа.

Для текущего exchange-like backtest вход исполняется на следующей свече, поэтому `entry_time_utc` обычно позже `entry_signal_time_utc`.

Готово, когда: контракт запрещает путать signal time и execution time.

### 5.3.3. Exit time rule

`exit_time_utc` должен быть не раньше `entry_time_utc`.

Если `exit_reason = timeout`, выход соответствует time-based закрытию.

Если `exit_reason = end_of_data`, выход соответствует закрытию на последней доступной свече окна.

Готово, когда: validator проверяет порядок времени.

### 5.3.4. Price rule

Для trade row:

1. `entry_price > 0`
2. `exit_price > 0`

Если цена отсутствует, равна нулю или не является числом, строка получает `CONTRACT_FAIL`.

Готово, когда: validator проверяет цены как positive float.

### 5.3.5. Return / PnL rule

`net_return` и `net_pnl_usd` являются итогом сделки после комиссии, slippage и плеча, если плечо применено в backtest.

Правило:

1. поля должны быть числами;
2. отрицательные значения допустимы;
3. нулевые значения допустимы;
4. пустые значения не допустимы для trade row.

Готово, когда: validator отличает пустое значение от валидного `0`.

### 5.4. Trade outcome labels

Обязательные поля:

1. `trade_id`
2. `bars_in_trade`
3. `tp_hit`
4. `sl_hit`
5. `timeout_hit`
6. `mae_pct`
7. `mfe_pct`

Детализация `1.4`:

| Поле | Обязательность | сточник | Формат | Проверка |
|---|---|---|---|---|
| `trade_id` | required | package builder / backtest row | stable non-empty string | уникален внутри `run_id` |
| `bars_in_trade` | required | backtest execution | integer >= 1 для trade row | равен числу баров от entry до exit включительно или согласованному holding count |
| `tp_hit` | required | derived from `exit_reason` | boolean | `true` только если `exit_reason = tp` |
| `sl_hit` | required | derived from `exit_reason` | boolean | `true` если `exit_reason = sl` или `sl_ambiguous` |
| `timeout_hit` | required | derived from `exit_reason` | boolean | `true` только если `exit_reason = timeout` |
| `mae_pct` | required | backtest holding window | float <= 0 или 0 | максимальный неблагоприятный ход сделки в процентах |
| `mfe_pct` | required | backtest holding window | float >= 0 или 0 | максимальный благоприятный ход сделки в процентах |

Правило `1.4`: если строка является сделкой (`side = LONG` или `side = SHORT`), все trade outcome labels обязательны и не могут быть пустыми.

### 5.4.1. `trade_id` rule

`trade_id` должен быть стабильным идентификатором сделки внутри `run_id`.

Рекомендуемый формат:

`<run_id>:<row_index>:<side>:<entry_time_utc>`

Минимальные требования:

1. не пустой;
2. уникален внутри одного `run_id`;
3. не меняется между повторной сборкой package из тех же исходных строк.

Готово, когда: validator ловит пустой или повторяющийся `trade_id`.

### 5.4.2. `bars_in_trade` rule

`bars_in_trade` описывает длительность сделки в барах.

Правило:

1. для trade row значение `>= 1`;
2. значение является integer;
3. значение не является `time_to_target_bars`;
4. если сделка закрылась по TP, `time_to_target_bars` может совпадать с `bars_in_trade`, но это разные поля.

Готово, когда: validator отличает длительность сделки от времени до цели.

### 5.4.3. Hit label rules

`tp_hit`, `sl_hit`, `timeout_hit` выводятся из `exit_reason`.

Mapping:

| `exit_reason` | `tp_hit` | `sl_hit` | `timeout_hit` |
|---|---:|---:|---:|
| `tp` | true | false | false |
| `sl` | false | true | false |
| `sl_ambiguous` | false | true | false |
| `timeout` | false | false | true |
| `end_of_data` | false | false | false |
| `manual_close` | false | false | false |

`unknown` не допускается для `APPROVED_FOR_ML`.

Готово, когда: validator сверяет hit labels с `exit_reason`.

### 5.4.4. MAE rule

`mae_pct` - максимальный неблагоприятный ход сделки внутри holding window.

Правило:

1. Для LONG неблагоприятный ход считается вниз от `entry_price`.
2. Для SHORT неблагоприятный ход считается вверх от `entry_price`.
3. Значение записывается в процентах.
4. Значение должно быть `<= 0` или равно `0`, если неблагоприятного хода не было.
5. Пустое значение для trade row дает `CONTRACT_FAIL`.

Готово, когда: validator проверяет, что `mae_pct` является числом и не пустой для trade row.

### 5.4.5. MFE rule

`mfe_pct` - максимальный благоприятный ход сделки внутри holding window.

Правило:

1. Для LONG благоприятный ход считается вверх от `entry_price`.
2. Для SHORT благоприятный ход считается вниз от `entry_price`.
3. Значение записывается в процентах.
4. Значение должно быть `>= 0` или равно `0`, если благоприятного хода не было.
5. Пустое значение для trade row дает `CONTRACT_FAIL`.

Готово, когда: validator проверяет, что `mfe_pct` является числом и не пустой для trade row.

### 5.4.6. Outcome labels vs ML target

Outcome labels не заменяют текущий `target_up`.

Разница:

1. `target_up` - direction label по будущей цене.
2. `tp_hit/sl_hit/timeout_hit` - результат торговой сделки.
3. `mae_pct/mfe_pct` - качество пути сделки после входа.
4. `net_return/net_pnl_usd` - итог сделки после costs/leverage policy.

ML trade dataset должен иметь trade outcome labels, потому что ML должен учиться не только направлению, но и качеству сделки.

Готово, когда: контракт явно разделяет market direction target и trade outcome labels.

## 6. Что запрещено пропускать

Запрещено пропускать:

1. идентификаторы пакета и запуска;
2. паспортный контекст;
3. `action_id`;
4. параметры калибровки;
5. сторону сделки;
6. времена входа и выхода;
7. цену входа и выхода;
8. причину выхода;
9. итоговую доходность;
10. outcome labels.

Если хотя бы одно required поле отсутствует, таблица не является ML-ready.

## 7. Что не является ML-ready

Не является ML-ready:

1. `reports/optuna/*` без package manifest;
2. `reports/pipeline/backtest_trades_*.csv` без row-level passport context;
3. `reports/final_review/oos_backtest_trades_*.csv` без row-level passport context;
4. CSV без `calibration_params_json`;
5. CSV без outcome labels;
6. `NO_GO` package;
7. `VALIDATION_FAIL` package;
8. package на `raw/quarantine`, если он выдается за clean training input.

## 8. Минимальные статусы

Разрешенные статусы package:

1. `DRAFT`
2. `NEEDS_AUDIT`
3. `APPROVED_FOR_ML`
4. `REJECTED`
5. `VALIDATION_FAIL`
6. `NO_GO`

ML ingest читает только `APPROVED_FOR_ML`.

## 9. Проверки

Проверки будут закрываться отдельными подпунктами:

1. `1.2` - required identifiers, fixed in this document.
2. `1.3` - entry/exit required fields, fixed in this document.
3. `1.4` - trade outcome labels, fixed in this document.
4. `1.5` - approval rule, fixed in this document.
5. `1.6` - contract validation command/test/audit.

Пункт `1.1` закрывает создание документа и базовую структуру контракта.
Пункт `1.2` закрывает обязательные идентификаторы и их правила проверки.
Пункт `1.3` закрывает поля входа/выхода и их правила проверки.
Пункт `1.4` закрывает trade outcome labels и их правила проверки.
Пункт `1.5` закрывает правило допуска в ML и запрет автоматического Optuna-to-ML.

## 10. Definition Of Done для 1.1

Пункт `1.1` считается закрытым, когда:

1. файл `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md` создан;
2. описано назначение таблицы;
3. описано, кто пишет таблицу;
4. описано, кто читает таблицу;
5. описаны группы required fields;
6. описано, что запрещено пропускать;
7. описан статус допуска `APPROVED_FOR_ML`;
8. создан audit по пункту `1.1`;
9. `text_guard PASS`.

## 11. Следующий пункт

После закрытия `1.5` следующий пункт:

`1.6 Сделать проверку контракта`

## 12. Definition Of Done для 1.2

Пункт `1.2` считается закрытым, когда:

1. `run_id` зафиксирован как required.
2. `symbol` зафиксирован как required.
3. `timeframe` зафиксирован как required.
4. `data_layer` зафиксирован как required.
5. `train_start` и `train_end` зафиксированы как required.
6. `test_start` и `test_end` зафиксированы как required.
7. `block_id` зафиксирован как required.
8. `passport_id` зафиксирован как required.
9. `action_id` зафиксирован как required.
10. `side` зафиксирован как required и имеет canonical mapping.
11. `calibration_params_json` зафиксирован как required и имеет JSON rule.
12. Отсутствие любого identifier дает `CONTRACT_FAIL`.
13. Создан audit по пункту `1.2`.
14. `text_guard PASS`.

## 13. Definition Of Done для 1.3

Пункт `1.3` считается закрытым, когда:

1. `entry_signal_time_utc` зафиксирован как required.
2. `entry_time_utc` зафиксирован как required.
3. `exit_time_utc` зафиксирован как required.
4. `entry_price` зафиксирован как required.
5. `exit_price` зафиксирован как required.
6. `exit_reason` зафиксирован как required.
7. `net_return` зафиксирован как required.
8. `net_pnl_usd` зафиксирован как required.
9. Разрешенные `exit_reason` перечислены.
10. Разница между signal time и execution time описана.
11. Правило `exit_time_utc >= entry_time_utc` описано.
12. Правило positive prices описано.
13. Правило numeric return/PnL описано.
14. Отсутствие любого entry/exit field для trade row дает `CONTRACT_FAIL`.
15. Создан audit по пункту `1.3`.
16. `text_guard PASS`.

## 14. Definition Of Done для 1.4

Пункт `1.4` считается закрытым, когда:

1. `trade_id` зафиксирован как required.
2. `bars_in_trade` зафиксирован как required.
3. `tp_hit` зафиксирован как required.
4. `sl_hit` зафиксирован как required.
5. `timeout_hit` зафиксирован как required.
6. `mae_pct` зафиксирован как required.
7. `mfe_pct` зафиксирован как required.
8. `trade_id` имеет uniqueness/stability rule.
9. `bars_in_trade` отделен от `time_to_target_bars`.
10. Hit labels mapping из `exit_reason` описан.
11. `mae_pct` rule описан.
12. `mfe_pct` rule описан.
13. Outcome labels отделены от `target_up`.
14. Отсутствие любого outcome label для trade row дает `CONTRACT_FAIL`.
15. Создан audit по пункту `1.4`.
16. `text_guard PASS`.

## 15. Definition Of Done для 1.5

Пункт `1.5` считается закрытым, когда:

1. Единственный источник допуска `configs/ml_approved_calibration_packages.yaml` зафиксирован.
2. Единственный разрешенный ML статус `APPROVED_FOR_ML` зафиксирован.
3. Запрещенные статусы перечислены.
4. Required admission files перечислены.
5. Clean `data_layer = core` rule зафиксирован.
6. `raw/quarantine` запрещены как clean ML input.
7. Manual approval metadata зафиксированы: `approved_by`, `approved_at_utc`, `comment`.
8. Запрет automatic Optuna-to-ML зафиксирован.
9. Ошибка допуска дает `ML_ADMISSION_DENY`.
10. Создан audit по пункту `1.5`.
11. `text_guard PASS`.

## 16. Contract validation command для 1.6

Пункт `1.6` добавляет исполняемую проверку ML trade dataset contract.

Команда:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path <trade_log.csv> --out-dir reports\qa_gate
```

Выход:

1. JSON audit report: `reports/qa_gate/ml_trade_dataset_contract_audit_*.json`.
2. Exit code `0`, если contract status = `PASS`.
3. Exit code `1`, если contract status = `FAIL`.

Проверяется:

1. required run context;
2. required passport context;
3. required entry/exit fields;
4. required trade outcome labels;
5. clean `data_layer = core`;
6. валидные train/test окна;
7. непустой JSON object в `calibration_params_json`;
8. canonical row-level `side`;
9. порядок времени signal -> entry -> exit;
10. positive `entry_price` и `exit_price`;
11. numeric `net_return` и `net_pnl_usd`;
12. allowed `exit_reason`;
13. hit labels consistency;
14. `trade_id` uniqueness внутри `run_id`;
15. `mae_pct <= 0` и `mfe_pct >= 0`.

## 17. Definition Of Done для 1.6

Пункт `1.6` считается закрытым, когда:

1. Создан validator module `src/mlbotnav/ml_trade_dataset_contract.py`.
2. Созданы tests `tests/test_ml_trade_dataset_contract.py`.
3. `py_compile` прошел `PASS`.
4. Unit tests прошли `PASS`, `4/4 OK`.
5. CLI smoke прошел `PASS`.
6. Создан CLI audit report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T122406Z.json`.
7. Создан step audit `reports/qa_gate/ml_trade_dataset_contract_step_1_6_audit_20260623T122406Z.md`.
8. `text_guard PASS`.

Пункт `1.6` закрыт; stage closeout фиксируется ниже.

## 18. Stage 1 Closeout для 1.7

Пункт `1.7` закрывает весь этап `1. ML Trade Dataset Contract`.

Этап 1 закрыт как `CLOSED_PASS`, потому что:

1. Контракт создан: `docs/CALIBRATION_NODE_CURRENT/ML_TRADE_DATASET_CONTRACT_RU.md`.
2. Required columns перечислены.
3. Правило `APPROVED_FOR_ML` записано.
4. Проверка required columns и row-level правил существует.
5. Validator module создан: `src/mlbotnav/ml_trade_dataset_contract.py`.
6. Tests созданы: `tests/test_ml_trade_dataset_contract.py`.
7. CLI smoke report создан: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T122406Z.json`.
8. Stage closeout audit создан: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.
9. `text_guard PASS`.

Граница этапа 1: реальные `backtest_trades_*.csv` и `oos_backtest_trades_*.csv` еще не обогащены contract fields. Это начинается на этапе 2.

Stage 1 закрыт; Stage 2 фиксируется ниже.

## 19. Stage 2.1 Run-Level Context

Пункт `2.1` добавляет run-level context в trade CSV outputs.

Поля:

1. `run_id`
2. `symbol`
3. `timeframe`
4. `data_layer`
5. `train_start`
6. `train_end`
7. `test_start`
8. `test_end`

Реализация:

1. Общий helper: `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. Pipeline trade CSV: `reports/pipeline/backtest_trades_*.csv`.
3. OOS trade CSV: `reports/final_review/oos_backtest_trades_*.csv`.

Готово, когда:

1. `pipeline_train_eval.py` добавляет run context перед записью `backtest_trades_*.csv`.
2. `oos_evaluate.py` добавляет run context перед записью `oos_backtest_trades_*.csv`.
3. Focused tests проходят.
4. Audit создан: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.

Граница: пункт `2.1` не добавляет passport context, `trade_id`, duration labels, hit labels и MAE/MFE. Они идут отдельными пунктами `2.2-2.6`.

Следующий строгий пункт: `2.2 Добавить passport context`.

## 20. Stage 2.2 Passport Context

Пункт `2.2` добавляет passport context в trade CSV outputs.

Поля:

1. `block_id`
2. `passport_id`
3. `action_id`
4. `calibration_params_json`
5. `entry_action_gate_columns`

Реализация:

1. Общий helper: `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. Pipeline trade CSV: `reports/pipeline/backtest_trades_*.csv`.
3. OOS trade CSV: `reports/final_review/oos_backtest_trades_*.csv`.
4. сточник passport metadata: `configs/calibration_action_passports.yaml`.

Правило разрешения passport context:

1. Сначала сопоставляется активный `entry_action_gate_columns` с `action_id`.
2. Затем сопоставляется активный `entry_action_gate_columns` с `runtime_action_columns`.
3. Затем сопоставляются ключи `calibration_params` с `allowed_calibration_params`.
4. Последний fallback: префикс passport id, например `F006_*`.

Готово, когда:

1. `pipeline_train_eval.py` добавляет passport context перед записью `backtest_trades_*.csv`.
2. `oos_evaluate.py` добавляет passport context перед записью `oos_backtest_trades_*.csv`.
3. Focused tests проходят.
4. Audit создан: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.

Граница: пункт `2.2` не добавляет `trade_id`, `entry_signal_time_utc`, duration labels, hit labels и MAE/MFE. Они идут отдельными пунктами `2.3-2.6`.

Следующий строгий пункт: `2.3 Добавить trade identity`.

## 21. Stage 2.3 Trade Identity

Пункт `2.3` добавляет trade identity в trade CSV outputs.

Поля:

1. `trade_id`
2. `entry_signal_time_utc`

Реализация:

1. Общий helper: `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. Pipeline trade CSV: `reports/pipeline/backtest_trades_*.csv`.
3. OOS trade CSV: `reports/final_review/oos_backtest_trades_*.csv`.

Правило:

1. Сделочные строки определяются как `side != 0`.
2. Для сделочных строк `entry_signal_time_utc` берется из существующего значения или из `open_time_utc` сигнального бара.
3. Для сделочных строк `trade_id` строится детерминированно из `run_id`, `action_id`, signal time, entry time, side и row index.
4. Для строк без сделки `trade_id` и `entry_signal_time_utc` остаются пустыми.
5. Существующий непустой `trade_id` не перезаписывается.

Готово, когда:

1. `pipeline_train_eval.py` добавляет trade identity перед записью `backtest_trades_*.csv`.
2. `oos_evaluate.py` добавляет trade identity перед записью `oos_backtest_trades_*.csv`.
3. Focused tests проходят.
4. Audit создан: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.

Граница: пункт `2.3` не добавляет duration labels, hit labels и MAE/MFE. Они идут отдельными пунктами `2.4-2.6`.

Следующий строгий пункт: `2.4 Добавить duration labels`.

## 22. Stage 2.4 Duration Labels

Пункт `2.4` добавляет duration labels в trade CSV outputs.

Поля:

1. `bars_in_trade`
2. `holding_seconds`

Реализация:

1. Общий helper: `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. Pipeline trade CSV: `reports/pipeline/backtest_trades_*.csv`.
3. OOS trade CSV: `reports/final_review/oos_backtest_trades_*.csv`.

Правило:

1. Сделочные строки определяются как `side != 0`.
2. Для сделочных строк `holding_seconds` считается от `entry_time_utc` до `exit_time_utc`.
3. Для сделочных строк `bars_in_trade` считается из `holding_seconds` и inferred bar interval.
4. Если timing недоступен, используются fallback fields `time_to_target_bars` / `time_to_target_sec`, когда они есть.
5. Для строк без сделки `bars_in_trade` и `holding_seconds` остаются пустыми.

Готово, когда:

1. `pipeline_train_eval.py` добавляет duration labels перед записью `backtest_trades_*.csv`.
2. `oos_evaluate.py` добавляет duration labels перед записью `oos_backtest_trades_*.csv`.
3. Focused tests проходят.
4. Audit создан: `reports/qa_gate/ml_trade_dataset_stage_2_4_duration_labels_audit_20260623T125816Z.md`.

Граница: пункт `2.4` не добавляет hit labels и MAE/MFE. Они идут отдельными пунктами `2.5-2.6`.

Следующий строгий пункт: `2.5 Добавить hit labels`.

## 23. Stage 2.5 Hit Labels

Пункт `2.5` добавляет hit labels в trade CSV outputs.

Поля:

1. `tp_hit`
2. `sl_hit`
3. `timeout_hit`
4. `end_of_data_hit`
5. `sl_ambiguous_hit`

Реализация:

1. Общий helper: `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. Pipeline trade CSV: `reports/pipeline/backtest_trades_*.csv`.
3. OOS trade CSV: `reports/final_review/oos_backtest_trades_*.csv`.

Правило:

1. Сделочные строки определяются как `side != 0`.
2. Labels выводятся из `exit_reason`.
3. `tp` -> `tp_hit=true`.
4. `sl` -> `sl_hit=true`.
5. `sl_ambiguous` -> `sl_hit=true` и `sl_ambiguous_hit=true`.
6. `timeout` -> `timeout_hit=true`.
7. `end_of_data` -> `end_of_data_hit=true`.
8. Для строк без сделки hit labels остаются пустыми.

Готово, когда:

1. `pipeline_train_eval.py` добавляет hit labels перед записью `backtest_trades_*.csv`.
2. `oos_evaluate.py` добавляет hit labels перед записью `oos_backtest_trades_*.csv`.
3. Focused tests проходят.
4. Audit создан: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.

Граница: пункт `2.5` не добавляет MAE/MFE. Они идут отдельным пунктом `2.6`.

Следующий строгий пункт: `2.6 Добавить MAE/MFE`.

## 24. Stage 2.6 MAE/MFE

Пункт `2.6` добавляет MAE/MFE labels в trade CSV outputs.

Поля:

1. `mae_pct`
2. `mfe_pct`

Реализация:

1. Общий helper: `src/mlbotnav/ml_trade_dataset_enrichment.py`.
2. Pipeline trade CSV: `reports/pipeline/backtest_trades_*.csv`.
3. OOS trade CSV: `reports/final_review/oos_backtest_trades_*.csv`.

Правило:

1. Сделочные строки определяются как `side != 0`.
2. Для LONG `mae_pct` считается от минимального `low` внутри holding window, `mfe_pct` - от максимального `high`.
3. Для SHORT расчет зеркальный: неблагоприятный ход идет через `high`, благоприятный ход идет через `low`.
4. `mae_pct` всегда `<= 0`.
5. `mfe_pct` всегда `>= 0`.
6. Для строк без сделки `mae_pct` и `mfe_pct` остаются пустыми.
7. Если holding window нельзя восстановить по timestamp/OHLC, используется fallback по return columns только для сохранения контрактных знаков.

Готово, когда:

1. `pipeline_train_eval.py` добавляет MAE/MFE перед записью `backtest_trades_*.csv`.
2. `oos_evaluate.py` добавляет MAE/MFE перед записью `oos_backtest_trades_*.csv`.
3. Focused tests проходят.
4. Audit создан: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.

Граница: пункт `2.6` не запускает большой calibration/OOS прогон и не передает артефакты в ML автоматически. Следующий шаг проверяет реальные CSV outputs по контракту.

Следующий строгий пункт: `2.7 Проверить pipeline CSV`.

## 25. Stage 2.7 Pipeline CSV Check

Пункт `2.7` проверяет `reports/pipeline/backtest_trades_*.csv` по ML trade dataset contract.

Статус: `CLOSED_PASS_AFTER_CONTROLLED_TEMP_UNLOCK`.

Что сделано:

1. `pipeline_train_eval.py` получил параметр `--layer`.
2. `load_ohlcv_range(..., layer=args.layer)` теперь читает выбранный слой.
3. CSV run context теперь пишет фактический `data_layer`, а не hardcoded `raw`.
4. Это нужно, потому что ML clean input допускает только `data_layer = core`.

Проверка:

1. Свежий pipeline run на `--layer core` был запущен как короткая validation-команда.
2. Run остановлен readiness-gate до выполнения pipeline.
3. Причина: `project_not_ready_for_pipeline_train_eval;open_blockers=0;freeze_reason=P2017 final NO_GO after forward fail; calibration only via APTuna temporary unlock`.
4. Readiness report: `reports/readiness/readiness_check_20260623T131731Z.json`.

Существующий последний `reports/pipeline/backtest_trades_SOLUSDT_1m_20260623T090929Z.csv` проверен контрактным валидатором:

1. Status: `FAIL`.
2. Rows total: `254`.
3. Failed rows: `254`.
4. Missing required columns: `20`.
5. Validator report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T131723Z.json`.

Вывод: существующий pipeline CSV является stale artifact до Stage 2 enrichment и не может закрыть `2.7`.

Audit: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.

Финальное закрытие:

1. Controlled temporary unlock использован только для короткого validation-run.
2. Свежий pipeline CSV: `reports/pipeline/backtest_trades_SOLUSDT_1m_20260623T132424Z.csv`.
3. Contract validation: `PASS`.
4. Rows total: `2072`.
5. Failed rows: `0`.
6. Missing columns: `0`.
7. Validator report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T132425Z.json`.
8. Readiness восстановлен обратно в frozen state.

Следующий строгий пункт: `2.8 Проверить OOS CSV`.

## 26. Stage 2.8 OOS CSV Check

Пункт `2.8` проверяет `reports/final_review/oos_backtest_trades_*.csv` по ML trade dataset contract.

Статус: `CLOSED_PASS`.

Входной pipeline report:

`reports/pipeline/pipeline_report_SOLUSDT_1m_20260623T132424Z.json`

Свежий OOS CSV:

`reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.csv`

Contract validation:

1. Status: `PASS`.
2. Rows total: `1177`.
3. Failed rows: `0`.
4. Missing columns: `0`.
5. Validator report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T132804Z.json`.

OOS run result:

1. Net return pct: `-0.9395906630311424`.
2. Trades: `3`.
3. Goal pass: `false`.

Граница: strategy quality не является gate для `2.8`; этот пункт закрывает именно contract readiness OOS CSV.

Audit: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.

Следующий строгий пункт: `2.9 Закрытие этапа 2`.

## 27. Stage 2 Closeout

Пункт `2.9` закрывает Stage 2 целиком.

Статус: `STAGE_2_CLOSED_PASS`.

Закрытые пункты:

1. `2.1 Добавить run-level context`
2. `2.2 Добавить passport context`
3. `2.3 Добавить trade identity`
4. `2.4 Добавить duration labels`
5. `2.5 Добавить hit labels`
6. `2.6 Добавить MAE/MFE`
7. `2.7 Проверить pipeline CSV`
8. `2.8 Проверить OOS CSV`

Финальная проверка:

1. Pipeline CSV contract: `PASS`.
2. Pipeline report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133238Z.json`.
3. OOS CSV contract: `PASS`.
4. OOS report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133240Z.json`.
5. Focused tests: `59/59 OK`.
6. `text_guard PASS`.

Closeout audit: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.

Граница: Stage 2 закрывает готовность trade CSV по контракту. Он не означает автоматический допуск в ML и не отменяет ручной `APPROVED_FOR_ML` registry.

Следующий строгий пункт: `3.1 Создать структуру пакета`.

## 28. Stage 3.1 Package Structure

Пункт `3.1` создает корневую структуру candidate package.

Статус: `CLOSED_PASS`.

Builder:

`src/mlbotnav/ml_candidate_package_builder.py`

Созданная папка:

`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Правило:

1. Package root всегда находится под `reports/ml_candidates/<run_id>/`.
2. `run_id` валидируется.
3. Path traversal и path separators запрещены.

Граница:

1. `3.1` не создает `calibration_package.json`.
2. `3.1` не создает `trade_log.csv`.
3. `3.1` не создает `manifest.json`.
4. `3.1` не создает `audit.md`.
5. `3.1` не делает `APPROVED_FOR_ML`.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.

Следующий строгий пункт: `3.2 Добавить calibration_package.json`.

## 29. Stage 3.2 Calibration Package

Пункт `3.2` создает `calibration_package.json`.

Статус: `CLOSED_PASS`.

Файл:

`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/calibration_package.json`

Содержимое:

1. `run_id`: `oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`
2. `block_id`: `B018`
3. `passport_id`: `F051`
4. `action_id`: `F051_BOSDOWN_ALLOW`
5. `calibration_params`: `4` параметра
6. `signal_mode`: `short_only`
7. `status`: `DRAFT`

Граница:

1. Статус намеренно `DRAFT`.
2. `trade_log.csv` еще не создан.
3. `manifest.json` еще не создан.
4. `audit.md` еще не создан.
5. `APPROVED_FOR_ML` не выставлен.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.

Следующий строгий пункт: `3.3 Добавить trade_log.csv`.

## 30. Stage 3.3 Trade Log

Пункт `3.3` добавляет package-local `trade_log.csv`.

Статус: `CLOSED_PASS`.

Файл:

`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/trade_log.csv`

сточник:

`reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.csv`

Contract validation:

1. Status: `PASS`.
2. Rows total: `1177`.
3. Failed rows: `0`.
4. Missing columns: `0`.
5. Report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T134753Z.json`.

Граница:

1. Source reports еще не скопированы.
2. `manifest.json` еще не создан.
3. `audit.md` еще не создан.
4. `APPROVED_FOR_ML` не выставлен.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.

Следующий строгий пункт: `3.4 Добавить исходные отчеты`.
## 31. Stage 3.4 Source Reports

Пункт `3.4` добавляет package-local исходные отчеты.

Статус: `CLOSED_PASS`.

Файлы:

1. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports.json`
2. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/oos_report.json`
3. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/pipeline_report.json`

сточники:

1. `reports/final_review/oos_report_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.json`
2. `reports/pipeline/pipeline_report_SOLUSDT_1m_20260623T132424Z.json`

Опциональный отчет:

1. `optuna_report.json`: `NOT_PROVIDED`.

Граница:

1. `manifest.json` еще не создан.
2. `audit.md` еще не создан.
3. `APPROVED_FOR_ML` не выставлен.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.

Следующий строгий пункт: `3.5 Добавить manifest.json`.

## 32. Stage 3.5 Manifest

Пункт `3.5` добавляет package-local `manifest.json`.

Статус: `CLOSED_PASS`.

Файл:

`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/manifest.json`

Manifest содержит:

1. `run_id`: `oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`
2. `symbol`: `SOLUSDT`
3. `timeframe`: `1m`
4. `data_layer`: `core`
5. `train_window`: `2026-05-25` to `2026-05-26`
6. `test_window`: `2026-05-27` to `2026-05-27`
7. `block_id`: `B018`
8. `passport_id`: `F051`
9. `action_id`: `F051_BOSDOWN_ALLOW`
10. `source_reports`
11. `status`: `DRAFT`

Проверка:

1. Required fields: `PASS`
2. JSON parse: `PASS`
3. `run_id` alignment across package artifacts: `PASS`

Граница:

1. Package-level `audit.md` еще не создан.
2. `APPROVED_FOR_ML` не выставлен.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.

Следующий строгий пункт: `3.6 Добавить audit.md`.

## 33. Stage 3.6 Package Audit

Пункт `3.6` добавляет package-local `audit.md`.

Статус: `CLOSED_PASS`.

Файл:

`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/audit.md`

Содержимое:

1. Summary: `PASS`
2. ML decision: `NO_GO_FOR_ML`
3. Review state: `READY_FOR_MANUAL_REVIEW`
4. Decision reason: package is `DRAFT` and requires manual approval before ML ingest.
5. Artifact list: `PASS`

Граница:

1. `APPROVED_FOR_ML` не выставлен.
2. ML ingest не запускался.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.

Следующий строгий пункт: `3.7 Закрытие этапа 3`.

## 34. Stage 3 Closeout

Пункт `3.7` закрывает Stage 3.

Статус: `STAGE_3_CLOSED_PASS`.

Package:

`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Проверки:

1. Required package files: `PASS`
2. `manifest.json`: `PASS`
3. `trade_log.csv` contract: `PASS`
4. Focused tests: `71/71 OK`
5. `text_guard PASS`

Граница:

1. Package remains `DRAFT`.
2. `APPROVED_FOR_ML` не выставлен.
3. ML ingest не запускался.

Audit: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.

Следующий строгий пункт: `4.1 Создать registry файл`.

## 35. Stage 4.1 Registry File

Пункт `4.1` создает manual ML approval registry.

Статус: `CLOSED_PASS`.

Файл:

`configs/ml_approved_calibration_packages.yaml`

Текущее состояние:

1. `schema_version`: `1`
2. `registry_status`: `EMPTY_NO_APPROVED_PACKAGES`
3. `manual_approval_required`: `true`
4. `approved_packages`: `[]`

Граница:

1. Ни один package не добавлен в `approved_packages`.
2. `APPROVED_FOR_ML` не выставлен.
3. ML ingest не запускался.

Audit: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.

Следующий строгий пункт: `4.2 Описать формат registry`.

## 36. Stage 4.2 Registry Format

Пункт `4.2` описывает формат manual ML approval registry.

Статус: `CLOSED_PASS`.

Файл:

`configs/ml_approved_calibration_packages.yaml`

Описанные поля:

1. `run_id`
2. `status`
3. `package_path`
4. `approved_by`
5. `approved_utc`
6. `comment`

Текущее состояние:

1. `approved_packages`: `[]`
2. No package approved for ML.

Audit: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.

Следующий строгий пункт: `4.3 Добавить запреты registry`.

## 37. Stage 4.3 Registry Bans

Пункт `4.3` добавляет явные запреты registry.

Статус: `CLOSED_PASS`.

Файл:

`configs/ml_approved_calibration_packages.yaml`

Запреты:

1. Deny result: `ML_ADMISSION_DENY`
2. Forbidden statuses: `DRAFT`, `NEEDS_AUDIT`, `NO_GO`, `VALIDATION_FAIL`, `REJECTED`, `UNKNOWN`
3. Contract audit must be `PASS`
4. Manifest must be valid
5. `raw`, `quarantine`, `raw/quarantine` cannot be clean ML input
6. Required package files: `manifest.json`, `trade_log.csv`, `audit.md`

Текущее состояние:

1. `approved_packages`: `[]`
2. No package approved for ML.

Audit: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.

Следующий строгий пункт: `4.4 Сделать validator registry`.

## 38. Stage 4.4 Registry Validator

Пункт `4.4` создает validator registry.

Статус: `CLOSED_PASS`.

Файлы:

1. `src/mlbotnav/ml_approval_registry_validator.py`
2. `tests/test_ml_approval_registry_validator.py`

Validator проверяет:

1. Package path exists.
2. Status is exactly `APPROVED_FOR_ML`.
3. Manifest is valid.
4. `trade_log.csv` passes `ml_trade_dataset_contract`.

Real registry validation:

1. Report: `reports/qa_gate/ml_approval_registry_validator_20260623T143952Z.json`
2. Status: `PASS`
3. Approved count: `0`
4. Failures: `0`

Audit: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.

Следующий строгий пункт: `4.5 Закрытие этапа 4`.

## 39. Stage 4 Closeout

WBS item `4.5` closes Stage 4 Manual ML Approval Registry.

Status: `STAGE_4_CLOSED_PASS`.

Closed items:

1. `4.1` registry file.
2. `4.2` registry format.
3. `4.3` registry bans.
4. `4.4` registry validator.
5. `4.5` closeout.

Registry state:

1. `approved_packages`: `[]`.
2. Approved count: `0`.
3. Deny result: `ML_ADMISSION_DENY`.

Checks:

1. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T143952Z.json`.
2. Focused tests: `74/74 OK`.
3. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T144002Z.json`.

Audit: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.

Boundary:

1. `APPROVED_FOR_ML` is not set.
2. ML ingest was not started.
3. There is no automatic Optuna -> ML transfer.

Next strict WBS item: `5.1 Find current ML ingest entry point`.

## 40. Stage 5.1 ML Ingest Entry Point

WBS item `5.1` found the current ML training ingest entry point.

Status: `CLOSED_PASS`.

Current primary entry point:

`src/mlbotnav/pipeline_train_eval.py`

Current orchestrators:

1. `src/mlbotnav/prod_cycle.py`
2. `src/mlbotnav/stage_ladder.py`
3. `src/mlbotnav/adaptive_auto_train.py`

Legacy/simple baseline:

`src/mlbotnav/train_baseline.py`

Not the Stage 5 training ingest target:

`src/mlbotnav/inference.py`

Current gap:

1. Training route reads OHLCV directly through `load_ohlcv_range`.
2. Training route does not read `configs/ml_approved_calibration_packages.yaml`.
3. Training route does not assemble an ML dataset from approved `reports/ml_candidates/<run_id>/trade_log.csv` files.

Audit: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.

Boundary:

1. No package was approved.
2. ML ingest/training was not started.
3. No code behavior was changed.

Next strict WBS item: `5.2 Block direct Optuna/report reading for ML ingest`.

## 41. Stage 5.2 ML Ingest Source Policy

WBS item `5.2` blocks direct ML ingest from old report roots.

Status: `CLOSED_PASS`.

Created:

1. `src/mlbotnav/ml_ingest_source_policy.py`
2. `tests/test_ml_ingest_source_policy.py`

Updated:

`configs/ml_approved_calibration_packages.yaml`

Forbidden direct roots:

1. `reports/optuna`
2. `reports/pipeline`
3. `reports/final_review`

Allowed source classes:

1. Approval registry: `configs/ml_approved_calibration_packages.yaml`.
2. Candidate packages: `reports/ml_candidates/<run_id>/...`.

Checks:

1. New source policy tests: `5/5 OK`.
2. Focused tests: `79/79 OK`.
3. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T145329Z.json`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T145330Z.json`.

Audit: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.

Boundary:

1. No package was approved.
2. ML ingest/training was not started.
3. Registry reading for ML ingest is not implemented here.

Next strict WBS item: `5.3 Implement registry reading`.

## 42. Stage 5.3 Approved Package Registry Reader

WBS item `5.3` implements the read-only registry reader for ML-side admission.

Status: `CLOSED_PASS`.

Created:

1. `src/mlbotnav/ml_approved_package_registry_reader.py`
2. `tests/test_ml_approved_package_registry_reader.py`

Reader behavior:

1. Reads `configs/ml_approved_calibration_packages.yaml`.
2. Runs `ml_approval_registry_validator` first.
3. Applies `ml_ingest_source_policy` to registry and package paths.
4. Exposes approved package metadata to the next dataset assembly step.
5. Returns `PASS` with `approved_count=0` for the current empty registry.

Real registry reader report:

`reports/qa_gate/ml_approved_package_registry_reader_20260623T145755674743Z.json`

Checks:

1. New reader tests: `3/3 OK`.
2. Focused tests: `82/82 OK`.
3. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T150239Z.json`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.

Audit: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.

Boundary:

1. No package was approved.
2. No package was added to `approved_packages`.
3. ML dataset assembly was not started.
4. ML ingest/training was not started.

Next strict WBS item: `5.4 Implement ML dataset assembly`.

## 43. Stage 5.4 ML Trade Dataset Assembly

WBS item `5.4` implements read-only ML trade dataset assembly from approved packages.

Status: `CLOSED_PASS`.

Created:

1. `src/mlbotnav/ml_approved_trade_dataset_builder.py`
2. `tests/test_ml_approved_trade_dataset_builder.py`

Builder behavior:

1. Reads packages only through `ml_approved_package_registry_reader`.
2. Stops if the registry reader fails.
3. Validates each package `trade_log.csv`.
4. Assembles a combined CSV under `reports/ml_datasets/` only when at least one approved package exists.
5. Writes a dataset manifest next to the assembled CSV.
6. Treats the current empty registry as `PASS / NO_APPROVED_PACKAGES`.

Real builder report:

`reports/qa_gate/ml_approved_trade_dataset_builder_20260623T150934741093Z.json`

Checks:

1. New builder tests: `3/3 OK`.
2. Focused tests: `85/85 OK`.
3. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T151131Z.json`.
4. Builder smoke: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.

Audit: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.

Boundary:

1. No package was approved.
2. No dataset was created from unapproved data.
3. ML training was not started.

Next strict WBS item: `5.5 Add rejection reasons`.

## 44. Stage 5.5 Rejection Reasons

WBS item `5.5` implements rejection reason logging for ML admission.

Status: `CLOSED_PASS`.

Created:

1. `src/mlbotnav/ml_rejection_reason_log.py`
2. `tests/test_ml_rejection_reason_log.py`

Reject log categories:

1. `missing_required_columns`
2. `invalid_manifest`
3. `not_approved`
4. `bad_data_layer`
5. `bad_status`
6. `missing_package_file`
7. `missing_manual_metadata`
8. `invalid_package_path`
9. `contract_fail`
10. `invalid_registry_entry`

Real reject-log report:

`reports/qa_gate/ml_rejection_reason_log_20260623T151618705623Z.json`

Reject log:

`reports/ml_rejections/ml_rejection_reasons_20260623T151618703912Z.json`

Checks:

1. New rejection reason tests: `4/4 OK`.
2. Focused tests: `89/89 OK`.
3. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T151814Z.json`.
4. Reject-log smoke: `PASS / NO_REJECTIONS`, report `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`.
5. Reject log: `reports/ml_rejections/ml_rejection_reasons_20260623T151814360422Z.json`.
6. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.

Audit: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.

Boundary:

1. No package was approved.
2. No registry mutation happened.
3. ML training was not started.

Next strict WBS item: `5.6 Stage 5 closeout`.

## 45. Stage 5 Closeout

WBS item `5.6` closes Stage 5: ML ingest only from approved registry.

Status: `STAGE_5_CLOSED_PASS`.

Closed:

1. `5.1` ML ingest entry point discovery.
2. `5.2` source policy blocks direct old report roots.
3. `5.3` approved package registry reader.
4. `5.4` approved trade dataset builder.
5. `5.5` rejection reason log.
6. `5.6` closeout.

Closeout checks:

1. Focused tests: `89/89 OK`.
2. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T152045Z.json`.
3. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T152045217551Z.json`.
4. Dataset builder: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T152111078301Z.json`.
5. Reject-log builder: `PASS / NO_REJECTIONS`, report `reports/qa_gate/ml_rejection_reason_log_20260623T152111079049Z.json`.
6. Old root `reports/optuna` denied: expected `FAIL`, report `reports/qa_gate/ml_ingest_source_policy_20260623T152122738533Z.json`.
7. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.

Audit: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.

Boundary:

1. No package was approved.
2. No registry mutation happened.
3. No dataset was created from unapproved data.
4. ML training was not started.

Next strict WBS item: `6.1 Check run_id alignment`.
