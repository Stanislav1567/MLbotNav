# Commands

## STAS9 VS Code/Codex Interface 2026-07-23

Открыть основной интерфейс:

```powershell
code .\MLbotNav_STAS9.code-workspace
```

Открыть панель Codex вручную, если она не сфокусировалась:

```text
Ctrl+Shift+P -> Open Codex Sidebar
```

Голосовой ввод:

```text
курсор в поле Codex -> Win+H -> произнести команду -> проверить текст -> Enter
```

Технический terminal fallback:

```powershell
& ".\STAS9_CONTROL_PLANE\START\start_STAS9.bat"
```

Открыть отчёт:

```powershell
ii .\STAS9_CONTROL_PLANE\REPORTS\STAS9_VSCODE_INTERFACE_SETUP_RU.md
```

## STAS9 Codex Runtime 2026-07-23

Проверить версию:

```powershell
codex --version
```

Обновить глобальный npm-CLI:

```powershell
npm install -g @openai/codex@latest
```

Безопасная проверка модели:

```powershell
codex exec --ephemeral --model gpt-5.6-sol --config 'model_reasoning_effort="xhigh"' --sandbox read-only --cd . --color never "Ответь ровно одной строкой: STAS9_MODEL_OK"
```

## STAS9 Multi-Agent Control Layer 2026-07-23

Безопасно проверить launcher без запуска Codex:

```powershell
cmd.exe /d /c call ".\STAS9_CONTROL_PLANE\START\start_STAS9.bat" --check
```

Запустить главный агент:

```powershell
& ".\STAS9_CONTROL_PLANE\START\start_STAS9.bat"
```

Открыть итоговый отчёт:

```powershell
ii .\STAS9_CONTROL_PLANE\REPORTS\STAS9_SETUP_REPORT_RU.md
```

## STAS9 Multi-Agent Structure 2026-07-23

Показать созданное дерево каталогов:

```powershell
Get-ChildItem .\STAS9_CONTROL_PLANE -Directory -Recurse |
  ForEach-Object { $_.FullName.Substring((Resolve-Path .\STAS9_CONTROL_PLANE).Path.Length + 1) } |
  Sort-Object
```

Проверить, что отсутствующие корневые STAS6/STAS7 не появились:

```powershell
Test-Path .\STAS6
Test-Path .\STAS7
```

## STAS9 Control Plane Audit 2026-07-23

Открыть управляющий проект:

```powershell
ii .\STAS9_CONTROL_PLANE
```

Проверить YAML:

```powershell
@'
from pathlib import Path
import yaml
for path in [
    Path("STAS9_CONTROL_PLANE/MODEL_REGISTRY.yaml"),
    Path("STAS9_CONTROL_PLANE/FEATURE_REGISTRY.yaml"),
]:
    yaml.safe_load(path.read_text(encoding="utf-8"))
    print("PASS", path)
'@ | .\.venv\Scripts\python.exe -
```

Проверить число зарегистрированных STAS5 model paths:

```powershell
@'
from pathlib import Path
import yaml
registry = yaml.safe_load(Path("STAS9_CONTROL_PLANE/MODEL_REGISTRY.yaml").read_text(encoding="utf-8"))
models = registry["models"]
missing = [item["path"] for item in models if not Path(item["path"]).exists()]
print({"models": len(models), "missing": missing})
'@ | .\.venv\Scripts\python.exe -
```

Ожидаемо: `models=37`, `missing=[]`.

Открыть архитектуру:

```powershell
ii .\STAS9_CONTROL_PLANE\STAS9_ARCHITECTURE_PROPOSAL_RU.md
```

Граница: эти команды только читают и валидируют STAS9. Они не запускают обучение, forward, Optuna и не меняют STAS5–STAS8.

## Codex Project CPU Relief

Проверить, что обучение не запущено:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -match '^python(w)?\.exe$' -or $_.CommandLine -match 'stas5|mlbotnav' } |
  Select-Object ProcessId,ParentProcessId,Name,CommandLine |
  Format-List
```

Мягко понизить приоритет Codex/VS Code после перезапуска, не закрывая процессы:

```powershell
foreach($name in @('ChatGPT','codex','Code','node_repl','codex-code-mode-host')){
  Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object {
    $_.PriorityClass = 'Idle'
  }
}
```

Проверить постоянное исключение generated STAS4 review:

```powershell
git check-ignore -v STAS4_FEATURE_HYPOTHESIS_REVIEW\combo_spectrum_4strategies_3days_20260710
```

Отчет: `docs/codex/CODEX_PROJECT_CPU_RELIEF_20260723_RU.md`.

## Build/Open Base R2-Style Review Gallery

Пересобрать базу `2026-01-27..2026-02-27` в обычном формате как R2/R3/R4:

```powershell
cd C:\Users\007\Desktop\MLbotNav
.\STAS5_ML_CORE\run_stas5_v5_base_review_gallery.ps1 -StartDay 2026-01-27 -EndDay 2026-02-27 -OpenFolder
```

Открыть уже собранную папку:

```powershell
cd C:\Users\007\Desktop\MLbotNav
ii .\STAS5_ML_CORE\artifacts\v5c\review\_BASE_R2_STYLE_VISUAL_REVIEW_20260127_20260227
```

Открыть индекс:

```powershell
cd C:\Users\007\Desktop\MLbotNav
ii .\STAS5_ML_CORE\artifacts\v5c\review\_BASE_R2_STYLE_VISUAL_REVIEW_20260127_20260227\STAS5_V5_BASE_R2_STYLE_REVIEW_GALLERY_INDEX_RU.md
```

## Open Entry Visual Check Pack BASE/R2/R3/R4

Открыть единую папку графиков для ручной проверки входов:

```powershell
cd C:\Users\007\Desktop\MLbotNav
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ENTRY_VISUAL_CHECK_CURRENT_20260127_20260320
```

Открыть индекс:

```powershell
cd C:\Users\007\Desktop\MLbotNav
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ENTRY_VISUAL_CHECK_CURRENT_20260127_20260320\STAS5_V5C_ENTRY_VISUAL_CHECK_INDEX_RU.md
```

Пересобрать только R2/R3/R4 visual gallery без обучения и без forward:

```powershell
cd C:\Users\007\Desktop\MLbotNav
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R2
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R3
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R4
```

## R4BB Table/ML Audit Artifacts

Открыть отчет по аудиту train-таблиц и моделей R4BB:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r4bb_train_20260127_20260320\STAS5_V5C_R4BB_TABLE_ML_AUDIT_20260722_RU.md
```

Важно: это отчет аудита. Он не запускает обучение и не меняет forward.

## STAS8 Soft Capacity V2 Preview R5

Пересобрать `STAS8_SOFT_CAPACITY_V2` на R5 `2026-03-21..2026-03-27` без обучения и без нового forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_stas8_move_capacity_audit.ps1 `
  -ForwardRunId stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1 `
  -StartDay 2026-03-21 `
  -EndDay 2026-03-27 `
  -SoftV2Preview `
  -OpenFolder
```

Открыть папку `soft_capacity_v2`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\soft_capacity_v2
```

Открыть главный кандидат `balanced`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\soft_capacity_v2\STAS8_SOFT_V2_BALANCED_CONTACT_SHEET.png
```

Открыть раздушенный вариант `wide`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\soft_capacity_v2\STAS8_SOFT_V2_WIDE_CONTACT_SHEET.png
```

Открыть guard:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\soft_capacity_v2\STAS5_V5C_STAS8_SOFT_CAPACITY_V2_GUARD_20260321_20260327.json
```

Важно: зеленый круг на PNG теперь означает только финальный live `ENTER` после STAS8. `RECALL_WATCH` и teacher-hit поля в этом preview нужны только для ручного просмотра, не для live, и не рисуются как зеленые входы.

## Open STAS8 R5 Entry/Move Audit

Открыть свежий аудит по R5 `2026-03-21..2026-03-27`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\v1\STAS5_V5C_STAS8_R5_ENTRY_MOVE_AUDIT_20260321_20260327_RU.md
```

Открыть папку с CSV-срезами и графиками:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\v1
```

Открыть контактный лист 7 дней без Bollinger:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\v1\STAS5_V5C_STAS8_R5_VISUAL_CONTACT_SHEET_NO_BOLLINGER.png
```

## Open STAS8 R5 Clean Visuals Without Bollinger

Открыть актуальные STAS8-графики R5 без Bollinger-полос:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\v1\visual_review
```

Открыть 2026-03-26:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\v1\visual_review\20260326\STAS5_V5C_STAS8_MOVE_CAPACITY_AUDIT_20260326_V1.png
```

## STAS8 Move Capacity Audit Preview R5

Пересобрать STAS8 audit-preview на актуальном R5 no-risk X463 forward `2026-03-21..2026-03-27`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_stas8_move_capacity_audit.ps1 `
  -ForwardRunId stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1 `
  -StartDay 2026-03-21 `
  -EndDay 2026-03-27 `
  -OpenFolder
```

Открыть готовую папку:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\v1
```

Открыть проблемный день 2026-03-26:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\v1\visual_review\20260326\STAS5_V5C_STAS8_MOVE_CAPACITY_AUDIT_20260326_V1.png
```

Открыть guard:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4bb_forward_20260321_20260327_bollinger_no_risk_v1\stas8_move_capacity_audit\v1\STAS5_V5C_STAS8_MOVE_CAPACITY_GUARD_20260321_20260327_V1.json
```

Важно: это audit-preview. Команда не запускает обучение, не запускает новый forward и не меняет исходный predictions CSV.

## STAS5 V5C R4BB Fast Train Audit

Открыть аудит быстрого train `stas5_v5c_r4bb_train_20260127_20260320`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r4bb_train_20260127_20260320\STAS5_V5C_R4BB_FAST_TRAIN_AUDIT_RU.md
```

Открыть run-папку:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r4bb_train_20260127_20260320
```

Быстро проверить, что управляющий config смотрит на R4BB/X463:

```powershell
$env:PYTHONPATH='src'
@'
import json
from pathlib import Path
import yaml

root = Path(r"C:\Users\007\Desktop\MLbotNav")
cfg = yaml.safe_load((root / "STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml").read_text(encoding="utf-8-sig"))
snap = json.loads((root / "STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json").read_text(encoding="utf-8-sig"))
for name, data in [("yaml", cfg), ("json", snap)]:
    train = data["active_context"]["train"]
    print(name, train["run_id"], train["feature_count"], train["batch_path"], train["riskgate_dataset_path"])
'@ | .\.venv\Scripts\python.exe -
```

## STAS5 V5C Bollinger Layer V1 X463

Пересобрать train datasets `2026-01-27..2026-03-20` с Bollinger-признаками:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_train_dataset_builder.ps1 `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-20 `
  -EnableBollingerLayer `
  -Force `
  -OpenFolder
```

Проверить training guard без обучения:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode TrainingGuard `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-20 `
  -TrainRunId stas5_v5c_r4bb_train_20260127_20260320
```

Открыть R2/R3/R4 Bollinger gallery:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA\R2
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA\R3
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA\R4
```

Пересобрать эти галереи:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R2 -BollingerPreview -OpenFolder
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R3 -BollingerPreview -OpenFolder
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R4 -BollingerPreview -OpenFolder
```

После визуального OK пользователь запускает обучение сам:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Train `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-20 `
  -TrainRunId stas5_v5c_r4bb_train_20260127_20260320
```

Forward на следующую неделю после PASS train/post-train guards:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Forward `
  -TrainManifestPath .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r4bb_train_20260127_20260320\STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json `
  -ForwardStartDay 2026-03-21 `
  -ForwardEndDay 2026-03-27 `
  -ForwardRunId stas5_v5c_r4bb_forward_20260321_20260327_wide_v1 `
  -EntryDecisionPolicy WideReview `
  -BollingerPreview `
  -OpenFolder
```

## STAS5 V5C R5 ENTRY-Only No-Risk Bollinger Visual Review

Пересобрать обычные графики **без риска** из R5 `visual_review` с Bollinger `20/2`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.stas5_v5_forward_visual_review `
  --forward-run-dir .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r5_entry_only_forward_20260321_20260327_wide_no_risk `
  --start-day 2026-03-21 `
  --end-day 2026-03-27 `
  --bollinger-preview
```

Открыть правильную папку:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r5_entry_only_forward_20260321_20260327_wide_no_risk\visual_review
```

Готовые дневные PNG лежат внутри `visual_review\YYYYMMDD` и называются:

```text
STAS5_V5_FORWARD_VISUAL_REVIEW_YYYYMMDD_ENTER_ARROWS_BOLLINGER20_2SIGMA_PREVIEW.png
```

Это no-risk/ENTRY-only visual review. Safety-pulse/RiskGate папки здесь не используются.

Открыть готовые графики с красными кругами `BB_BLOCK_V0`, где Bollinger preview пометил опасные `ENTER/WATCH` за `2026-03-21..2026-03-27`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r5_entry_only_forward_20260321_20260327_wide_no_risk\visual_review
```

Имена дневных PNG:

```text
STAS5_V5_FORWARD_VISUAL_REVIEW_YYYYMMDD_ENTER_WATCH_BOLLINGER_BLOCK_V0_RED_CIRCLES.png
```

Week-manifest с цифрами:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r5_entry_only_forward_20260321_20260327_wide_no_risk\visual_review\STAS5_V5_FORWARD_VISUAL_REVIEW_20260321_20260327_BOLLINGER_BLOCK_V0_WEEK_MANIFEST.json
```

## STAS5 V5C Bollinger Visual Preview 2026-03-21..2026-03-27

Пересобрать все графики недели `DOWN_CHANNEL_NO_LONG_V1` с Bollinger `20/2`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_safety_pulse_preview.ps1 `
  -ForwardRunId stas5_v5c_r4_forward_20260321_20260327_wide_v1 `
  -StartDay 2026-03-21 `
  -EndDay 2026-03-27 `
  -Policy DOWN_CHANNEL_NO_LONG_V1 `
  -BollingerPreview `
  -OpenFolder
```

Открыть готовую папку:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4_forward_20260321_20260327_wide_v1\safety_pulse_preview\down_channel_no_long_v1
```

Открыть график `2026-03-23` напрямую:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4_forward_20260321_20260327_wide_v1\safety_pulse_preview\down_channel_no_long_v1\20260323\STAS5_V5C_BALANCED_SAFETY_PULSE_20260323_BOLLINGER20_2SIGMA_PREVIEW_V1.png
```

Это только открытие PNG. Train/forward/ML decisions не запускаются и не меняются.

## STAS5 V5C ENTRY-Only Wide R5

Команда обучения базовой ENTRY-цепочки по базе `2026-01-27..2026-03-20` с R2/R3/R4 ручными правками, но без обучения RiskGate ML в этом run:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Train `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-20 `
  -TrainRunId stas5_v5c_r5_entry_only_train_20260127_20260320 `
  -SkipRiskGateML
```

После PASS train раздушенный forward без RiskGate, через wide-review пороги:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Forward `
  -TrainManifestPath .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r5_entry_only_train_20260127_20260320\STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json `
  -ForwardStartDay 2026-03-21 `
  -ForwardEndDay 2026-03-27 `
  -ForwardRunId stas5_v5c_r5_entry_only_forward_20260321_20260327_wide_no_risk `
  -EntryDecisionPolicy WideReview `
  -DisableRiskGateML `
  -OpenFolder
```

Смысл: ENTRY учится на `entry_y` из base32 + approved R2/R3/R4, использует только X439 causal features. `risk_bad_y`, RiskGate labels, manual review, future/outcome не становятся feature. `WideReview` не обучает заново threshold на forward: он берет train OOF quantile и дает больше кандидатов для просмотра.

## STAS8 Live Wave + Move Capacity TZ

Дата фиксации: `2026-07-22`. Блок выключен, это только ТЗ и команды проверки.

Рельса:

```text
R2/R3/R4 = approved train material
R5 2026-03-21..2026-03-27 = blind-forward/audit-preview, не train до ручного review
STAS8_LIVE_MOVE_CONTEXT_V1 = no-future live long-search gate
STAS8_TEACHER_MOVE_GRID_V1 = offline teacher/audit future grid
```

Открыть отложенное ТЗ:

```powershell
ii .\STAS5_ML_CORE\10_STAS8_MOVE_CAPACITY_GRID_TZ_RU.md
```

Открыть управляющий YAML, где `STAS8_MOVE_CAPACITY_GRID_V1` записан как выключенный будущий блок:

```powershell
ii .\STAS5_ML_CORE\configs\STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

Проверить YAML/JSON без запуска ML:

```powershell
@'
from pathlib import Path
import json
import yaml
root = Path(r"C:\Users\007\Desktop\MLbotNav")
y = yaml.safe_load((root / "STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml").read_text(encoding="utf-8-sig"))
j = json.loads((root / "STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.json").read_text(encoding="utf-8-sig"))
for name, d in [("yaml", y), ("json", j)]:
    b = d["ml_blocks"]["STAS8_MOVE_CAPACITY_GRID_V1"]
    print(name, b["enabled"], b["type"], b["train_scope_rule"]["blind_forward_audit_range"], b["teacher_grid_layer"]["decision_thresholds_pct"]["enter_main"])
'@ | .\.venv\Scripts\python.exe -
```

## STAS5 V5C Safety Pulse Preview

Текущий рекомендуемый preview для просмотра после плохих входов `2026-03-26/2026-03-27`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_safety_pulse_preview.ps1 `
  -ForwardRunId stas5_v5c_r4_forward_20260321_20260327_wide_v1 `
  -StartDay 2026-03-21 `
  -EndDay 2026-03-27 `
  -Policy DOWN_CHANNEL_NO_LONG_V1 `
  -OpenFolder
```

Открыть готовую папку без пересборки:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4_forward_20260321_20260327_wide_v1\safety_pulse_preview\down_channel_no_long_v1
```

Контрольные цифры текущего preview:

```text
До RiskGate: ENTER=70, WATCH=176, SKIP=318
Старый финал с RISKGATE_ML: ENTER=34, WATCH=37, SKIP=493
DOWN_CHANNEL_NO_LONG_V1: ENTER=40, WATCH=136, SKIP=388
```

Быстрый test-drive без обучения и без пересборки forward. Использует готовый forward `2026-03-21..2026-03-27`, готовые predictions и RiskGate taxonomy audit, затем рисует отдельные PNG.

Рекомендуемый для просмотра пульс сейчас:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_safety_pulse_preview.ps1 `
  -ForwardRunId stas5_v5c_r4_forward_20260321_20260327_wide_v1 `
  -StartDay 2026-03-21 `
  -EndDay 2026-03-27 `
  -Policy HARD_BLOCK_ONLY_V1 `
  -OpenFolder
```

Открыть готовую папку:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r4_forward_20260321_20260327_wide_v1\safety_pulse_preview\hard_block_only_v1
```

Более строгий вариант для сравнения:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_safety_pulse_preview.ps1 `
  -ForwardRunId stas5_v5c_r4_forward_20260321_20260327_wide_v1 `
  -StartDay 2026-03-21 `
  -EndDay 2026-03-27 `
  -Policy BALANCED_SAFETY_V1 `
  -OpenFolder
```

Важно: это не запускает `Train`, не запускает новый `Forward`, не меняет исходный predictions CSV.

## STAS5 V5C R4 ENTRY + RiskGate ML Manual Train

Текущая команда ручного запуска обучения в VS Code. Она должна обучить ENTRY-цепочку и затем отдельный `RISKGATE_ML` в том же train run:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Train `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-20 `
  -TrainRunId stas5_v5c_r4_train_20260127_20260320
```

Перед Train уже проверено:

```text
ENTRY TrainingGuard: PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING
RiskGate ML TrainingGuard: PASS_V5C_RISKGATE_ML_TRAINING_GUARD_READY_FOR_TRAINING
```

После Train открыть run dir:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r4_train_20260127_20260320
```

Проверить, что появились RiskGate ML artifacts:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r4_train_20260127_20260320\STAS5_V5C_RISKGATE_ML_TRAIN_MANIFEST_V1.json
ii .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r4_train_20260127_20260320\STAS5_V5C_RISKGATE_ML_POST_TRAIN_GUARD_V1.json
```

Forward не запускать, пока ENTRY post-train guard и RiskGate post-train guard не PASS.

## STAS5 V5C R4 Build/Train Commands

Пересобрать ENTRY + RiskGate train datasets без обучения:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_train_dataset_builder.ps1 -Force
```

Открыть готовые guards:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\STAS5_V5C_BATCH_20260127_20260320_GUARD_V1.json
ii .\STAS5_ML_CORE\artifacts\v5c\STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260320_GUARD_V1.json
```

Проверить TrainingGuard без обучения:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode TrainingGuard `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-20 `
  -TrainRunId stas5_v5c_r4_train_20260127_20260320
```

Ручной запуск обучения в VS Code:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Train `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-20 `
  -TrainRunId stas5_v5c_r4_train_20260127_20260320
```

Forward не запускать до завершенного Train и post-train guard PASS.

## STAS5 V5C Open ML Control Config

Открыть главный управляющий YAML:

```powershell
ii .\STAS5_ML_CORE\configs\STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

Открыть справочные config-снимки:

```powershell
ii .\STAS5_ML_CORE\configs\STAS5_V5C_ML_CONTROL_CONFIG_V1.json
ii .\STAS5_ML_CORE\configs\STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
```

Текущий статус config: `REVIEW_PACK_DATASET_RAILS_LOCKED_NO_TRAINING`. Команды Train/Forward здесь специально не добавлены как следующий запуск: сначала нужен builder `X439_SOURCE`, `ENTRY_TRAIN_DATASET`, `RISKGATE_TRAIN_DATASET` и их guards.

Открыть approved review-pack, который должен использовать будущий dataset builder:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_APPROVED_REVIEW_PACKS\STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1
```

Ожидаемые цифры будущего ENTRY train view после builder guard:

```text
days=53
rows=3285
GOOD=517
BAD=2768
RISK_BAD=400
features=439
```

## STAS5 V5C Build Approved Review Pack R2/R3/R4

Собрать единый approved review-pack по `R2/R3/R4` без training и без forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_review_pack.ps1
```

Если pack уже существует и нужно пересобрать его поверх свежих `APPROVED` ledgers:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_review_pack.ps1 -Force
```

Открыть готовую папку:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_APPROVED_REVIEW_PACKS\STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1
```

Открыть guard:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_APPROVED_REVIEW_PACKS\STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1\STAS5_V5C_R2_R3_R4_REVIEW_PACK_GUARD_V1.json
```

Открыть сводные CSV:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_APPROVED_REVIEW_PACKS\STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1\entry\STAS5_V5C_R2_R3_R4_ENTRY_REVIEW_APPROVED_ALL_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5c\review\_APPROVED_REVIEW_PACKS\STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1\riskgate\STAS5_V5C_R2_R3_R4_RISKGATE_REVIEW_APPROVED_ALL_V1.csv
```

Ожидаемые цифры текущего PASS-пакета:

```text
days=21
ENTRY rows=689
ENTRY GOOD=227
ENTRY BAD=462
RISK BAD=400
guard=PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING
```

## STAS5 V5C Open Current Review Graph

Открыть официальный текущий график R2 `2026-03-01`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\r2_user_review\20260301\STAS5_V5C_R2_USER_REVIEW_20260301_CURRENT_REVIEW.png
```

Открыть manifest, где видно, какие цифры связаны с этим графиком:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\r2_user_review\20260301\STAS5_V5C_R2_USER_REVIEW_20260301_CURRENT_VISUAL_MANIFEST_V1.json
```

Открыть R2-витрину после cleanup:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ALL_ROUNDS_VISUAL_REVIEW\R2
```

В корне дня должен быть один `*_CURRENT_REVIEW.png`; старые/технические PNG лежат в `_visual_archive`.

## STAS5 V5C Open Updated Review Gallery

Открыть общую витрину с обновленными `LAxxx` над review-маркерами:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ALL_ROUNDS_VISUAL_REVIEW
```

Открыть контрольный R2-график `2026-03-01`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ALL_ROUNDS_VISUAL_REVIEW\R2\20260301\STAS5_V5C_R2_20260301_ANNOTATED_ENTRY_RISK.png
```

Пересобрать витрину после новых review-ledgers:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R2 -OpenFolder
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R3 -OpenFolder
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R4 -OpenFolder
```

Эти команды не запускают training, forward и day passport rebuild.

## STAS5 V5C Review Gallery R2/R3/R4

Собрать/обновить общую витрину review-графиков:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R2 -OpenFolder
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R3 -OpenFolder
.\STAS5_ML_CORE\run_stas5_v5c_review_gallery.ps1 -Round R4 -OpenFolder
```

Открыть общую папку:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ALL_ROUNDS_VISUAL_REVIEW
```

Открыть R2:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\_ALL_ROUNDS_VISUAL_REVIEW\R2
```

Витрина создает только PNG/CSV-копии для review: `ALL_ENTRIES` и `ANNOTATED_ENTRY_RISK`. Training, forward и пересборку дневных passports она не запускает.

## STAS5 V5C ENTRY/RiskGate Label Contract

Быстрая диктовка сохраняет две разные цели:

```text
обычное хорошо / вход / крестик хорошо / ромбик хорошо -> ENTRY -> entry_y=1
обычное плохо без слова риск -> ENTRY -> entry_y=0
риск плохо -> ENTRY BAD + RiskGate BAD -> entry_y=0 + risk_bad_y=1
```

`risk_bad_y` не является live feature. Это отдельный target для RiskGate, но сам LA одновременно остается плохим примером для ENTRY (`entry_y=0`). Команду `-Stage All -Approve` запускать одной цельной командой, не дописывать `-Stage` отдельной строкой после завершения команды PowerShell.

## STAS5 V5C Quick Review Ladder ENTRY + RiskGate

Проверить разбор без записи файлов:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_review_ladder.ps1 `
  -Day 2026-03-18 `
  -Round R4 `
  -ForwardRunId stas5_v5c_r3_forward_20260314_20260320_wide_v1 `
  -Review "14 плохо; 22 ромбик хорошо; 47 крестик вход; 40 риск плохо" `
  -Stage Parse
```

Сохранить draft-ledger, без пересборки дня:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_review_ladder.ps1 `
  -Day 2026-03-18 `
  -Round R4 `
  -ForwardRunId stas5_v5c_r3_forward_20260314_20260320_wide_v1 `
  -Review "14 плохо; 22 ромбик хорошо; 47 крестик вход; 40 риск плохо" `
  -Stage SaveReview `
  -OpenFolder
```

В папке дня должен появиться контрольный PNG со всеми входами:

```text
STAS5_V5C_R4_USER_REVIEW_YYYYMMDD_DRAFT_ALL_ENTRIES.png
STAS5_V5C_R4_USER_REVIEW_YYYYMMDD_DRAFT_ANNOTATED.png
```

`*_ALL_ENTRIES.png` - чистый график со всеми LA. `*_ANNOTATED.png` - рабочий график для проверки диктовки: поверх цены видны `GOOD/BAD/RISK BAD`, нижние полосы `Fon/LONG/SHORT/WAVE` сохранены. Overlay без стрелок: `GOOD` = зеленый круг, `RISK BAD` = ярко-красный круг, обычный `BAD` = красный квадрат.

Открыть проверочный PNG с подсветкой для примера `2026-03-18`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\r4_user_review\20260318\STAS5_V5C_R4_USER_REVIEW_20260318_APPROVED_ANNOTATED.png
```

Закрыть день и сразу пересобрать V5 day package по ENTRY GOOD ids:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_review_ladder.ps1 `
  -Day 2026-03-18 `
  -Round R4 `
  -ForwardRunId stas5_v5c_r3_forward_20260314_20260320_wide_v1 `
  -Review "14 плохо; 22 ромбик хорошо; 47 крестик вход; 40 риск плохо" `
  -Stage All `
  -Approve `
  -OpenFolder
```

Если `APPROVED` review уже успел записаться, но пересборка дня была прервана, повторить ту же команду с `-Force`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_review_ladder.ps1 `
  -Day 2026-03-18 `
  -Round R4 `
  -ForwardRunId stas5_v5c_r3_forward_20260314_20260320_wide_v1 `
  -Review "14 плохо; 22 ромбик хорошо; 47 крестик вход; 40 риск плохо" `
  -Stage All `
  -Approve `
  -Force `
  -OpenFolder
```

Правило диктовки:

```text
без слова риск -> ENTRY: хорошо/вход = GOOD, плохо = BAD
со словом риск -> RiskGate: только риск плохо = RISK_BAD
риск хорошо не использовать
```

Если нужно одновременно сказать, что вход плохой и зона рискованная:

```text
47 плохо; 47 риск плохо
```

## STAS5 V5C RiskGate Taxonomy V1

Пересобрать RiskGate audit-only на `2026-03-18` с полной таксономией режимов и user-pass `LA059,LA067,LA078`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode RiskGate `
  -ForwardStartDay 2026-03-18 `
  -ForwardEndDay 2026-03-18 `
  -ForwardRunId stas5_v5c_r3_forward_20260314_20260320_wide_v1 `
  -RiskGateUserPassIds LA059,LA067,LA078 `
  -OpenFolder
```

Открыть свежий PNG:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r3_forward_20260314_20260320_wide_v1\riskgate_audit\20260318\STAS5_V5C_RISKGATE_AUDIT_20260318_V1.png
```

Открыть свежий CSV с режимами:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r3_forward_20260314_20260320_wide_v1\riskgate_audit\20260318\STAS5_V5C_RISKGATE_AUDIT_20260318_V1.csv
```

Ключевые новые колонки: `RISK_GATE_TAXONOMY_VERSION`, `RISK_GATE_PRIMARY_REGIME`, `RISK_GATE_TAGS`, `RISK_MODE_*_SCORE`, `RISK_MODE_*_FLAG`.

## STAS5 V5C RiskGate Audit-Only

Запустить RiskGate audit-only на уже готовом R3 forward-дне `2026-03-18` с тремя проходящими входами пользователя:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode RiskGate `
  -ForwardStartDay 2026-03-18 `
  -ForwardEndDay 2026-03-18 `
  -ForwardRunId stas5_v5c_r3_forward_20260314_20260320_wide_v1 `
  -RiskGateUserPassIds LA059,LA067,LA078 `
  -OpenFolder
```

Открыть официальный RiskGate PNG:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r3_forward_20260314_20260320_wide_v1\riskgate_audit\20260318\STAS5_V5C_RISKGATE_AUDIT_20260318_V1.png
```

Открыть официальный RiskGate CSV:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r3_forward_20260314_20260320_wide_v1\riskgate_audit\20260318\STAS5_V5C_RISKGATE_AUDIT_20260318_V1.csv
```

Важно: это не training и не forward. Это audit-only слой поверх готовых predictions.

Если RiskGate запускается на диапазон больше одного дня, `USER_PASS` нужно указывать с датой, чтобы одинаковые `LAxxx` не применились к другим дням:

```powershell
-RiskGateUserPassIds 2026-03-18:LA059,2026-03-18:LA067,2026-03-18:LA078
```

## STAS5 V5C Open RiskGate Preview 2026-03-18

Открыть PNG-прототип RiskGate V0 для `2026-03-18`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r3_forward_20260314_20260320_wide_v1\riskgate_preview\20260318\STAS5_V5C_RISKGATE_PREVIEW_20260318_V0.png
```

Открыть отчет:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r3_forward_20260314_20260320_wide_v1\riskgate_preview\20260318\STAS5_V5C_RISKGATE_PREVIEW_20260318_RU.md
```

Открыть CSV с причинами:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r3_forward_20260314_20260320_wide_v1\riskgate_preview\20260318\STAS5_V5C_RISKGATE_PREVIEW_20260318_V0.csv
```

Открыть V1 user-pass версию, где `LA059`, `LA067`, `LA078` помечены как проходящие:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r3_forward_20260314_20260320_wide_v1\riskgate_preview\20260318\STAS5_V5C_RISKGATE_PREVIEW_20260318_V1_USER_PASS.png
```

Открыть V1 CSV:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r3_forward_20260314_20260320_wide_v1\riskgate_preview\20260318\STAS5_V5C_RISKGATE_PREVIEW_20260318_V1_USER_PASS.csv
```

## STAS5 V5C Check Frozen Two-Block

Проверить, что `ENTRY_ML_TWO_BLOCK` заморожен в главном YAML:

```powershell
@'
from pathlib import Path
import yaml
p = Path("STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml")
d = yaml.safe_load(p.read_text(encoding="utf-8"))
b = d["ml_blocks"]["ENTRY_ML_TWO_BLOCK"]
print("ENTRY_ML_TWO_BLOCK enabled=", b["enabled"])
print("ENTRY_ML_TWO_BLOCK mode=", b["mode"])
print("ENTRY_ML_TWO_BLOCK selection_status=", b["selection_status"])
'@ | python -X utf8 -
```

Ожидаемо:

```text
enabled=False
mode=frozen_not_selected
selection_status=FROZEN_NOT_SELECTED_BY_R3_QUALITY_GATE
```

## STAS5 V5C YAML Config With Russian Comments

Открыть главный YAML config с русскими комментариями по ML-блокам:

```powershell
ii .\STAS5_ML_CORE\configs\STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

Проверить, что YAML после комментариев валиден:

```powershell
@'
from pathlib import Path
import yaml
p = Path("STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml")
d = yaml.safe_load(p.read_text(encoding="utf-8"))
print("YAML_VALIDATE=PASS", d["status"])
'@ | python -X utf8 -
```

## STAS5 V5C Main YAML ML Control Config

Открыть главный управляемый YAML config по ML-блокам:

```powershell
ii .\STAS5_ML_CORE\configs\STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml
```

Проверить YAML:

```powershell
@'
from pathlib import Path
import yaml
p = Path("STAS5_ML_CORE/configs/STAS5_V5C_ML_CONTROL_CONFIG_V1.yaml")
d = yaml.safe_load(p.read_text(encoding="utf-8"))
print(d["config_id"], d["status"])
print("source_of_truth=", d["source_of_truth"])
print("selected_entry=", d["ml_blocks"]["ENTRY_BASELINE_ML"]["selected_for_entry"])
'@ | python -X utf8 -
```

Важно: с `2026-07-20` главным source-of-truth является YAML. JSON и RU.md являются справочными снимками.

## STAS5 V5C ML Control Config

Открыть старую человекочитаемую справку по ML-блокам:

```powershell
ii .\STAS5_ML_CORE\configs\STAS5_V5C_ML_CONTROL_CONFIG_V1_RU.md
```

Проверить машинный JSON config:

```powershell
python -m json.tool .\STAS5_ML_CORE\configs\STAS5_V5C_ML_CONTROL_CONFIG_V1.json > $env:TEMP\stas5_v5c_ml_control_config_v1.pretty.json
```

Важно: config V1 пока не запускает обучение и не включает RiskGate автоматически. Следующий кодовый шаг должен подключать `RISK_GATE_RULE_V0` только в режиме `audit_only`.

## STAS5 V5C R3 TrainingGuard, Train, Forward Week3

R3 batch уже собран и guard `PASS`. Эти команды используют пользовательские правки за `2026-03-07..2026-03-13`; не использовать старый R2/R2Q train range до `2026-03-06`.

Текущий статус: `TrainingGuard` и `Train` уже выполнены, post-train guard `PASS_V5_TWO_BLOCK_POST_TRAIN_GUARD_READY_FOR_FORWARD`. Следующая команда - blind-forward week3 `2026-03-14..2026-03-20`.

1. TrainingGuard, без обучения:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode TrainingGuard `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-13 `
  -TrainRunId stas5_v5c_r3_train_20260127_20260313
```

Ожидаемо: `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`.

2. Train, уже выполнено:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Train `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-13 `
  -TrainRunId stas5_v5c_r3_train_20260127_20260313
```

3. Blind-forward week3, запускать сейчас:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Forward `
  -ForwardStartDay 2026-03-14 `
  -ForwardEndDay 2026-03-20 `
  -ContextStartDay 2026-01-27 `
  -ContextWarmupMinutes 720 `
  -EntryDecisionPolicy WideReview `
  -TrainManifestPath .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r3_train_20260127_20260313\STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json `
  -ForwardRunId stas5_v5c_r3_forward_20260314_20260320_wide_v1 `
  -OpenFolder
```

`2026-03-07..2026-03-13` уже вошли в R3 train и не являются новым blind proof. Новый blind proof - `2026-03-14..2026-03-20`.

## STAS5 V5C R2Q Forward Rerun After Normal Threshold Fix

Старый `Normal` был слишком зажат: на `2026-03-07..2026-03-13` дал только `ENTER=5`. После фикса `Normal` ожидается около `25` ENTER; для ручного review можно сразу запускать `WideReview`, ожидается около `64` ENTER. Оба режима считают пороги только по train OOF, без forward outcome labels.

Рекомендуемый сейчас режим для визуального разбора: `WideReview`.

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Forward `
  -ForwardStartDay 2026-03-07 `
  -ForwardEndDay 2026-03-13 `
  -ContextStartDay 2026-01-27 `
  -ContextWarmupMinutes 720 `
  -EntryDecisionPolicy WideReview `
  -TrainManifestPath .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r2q_train_20260127_20260306\STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json `
  -ForwardRunId stas5_v5c_r2q_forward_20260307_20260313_wide_v2 `
  -OpenFolder
```

Более спокойный вариант:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Forward `
  -ForwardStartDay 2026-03-07 `
  -ForwardEndDay 2026-03-13 `
  -ContextStartDay 2026-01-27 `
  -ContextWarmupMinutes 720 `
  -EntryDecisionPolicy Normal `
  -TrainManifestPath .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r2q_train_20260127_20260306\STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json `
  -ForwardRunId stas5_v5c_r2q_forward_20260307_20260313_normal_v2 `
  -OpenFolder
```

## STAS5 V5C R2Q Normal Forward More Entries

После R2Q train PASS можно запустить повторный forward той же недели `2026-03-07..2026-03-13` с более широким порогом `Normal`. Модель, train и X439 не меняются; меняется только decision threshold, рассчитанный по train OOF quantiles без forward tuning.

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Forward `
  -ForwardStartDay 2026-03-07 `
  -ForwardEndDay 2026-03-13 `
  -ContextStartDay 2026-01-27 `
  -ContextWarmupMinutes 720 `
  -EntryDecisionPolicy Normal `
  -TrainManifestPath .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r2q_train_20260127_20260306\STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json `
  -ForwardRunId stas5_v5c_r2q_forward_20260307_20260313_normal `
  -OpenFolder
```

`WideReview` использовать только если `Normal` все равно слишком скупой:

```powershell
-EntryDecisionPolicy WideReview
```

## STAS5 V5C R2Q Train Retry After Multiclass Fix

Если `TrainingGuard` уже вернул `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`, а первый `Train` упал на `liblinear` multiclass для `phase_y/state_y`, после фикса кода команда не меняется. Повторить:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Train `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-06 `
  -TrainRunId stas5_v5c_r2q_train_20260127_20260306
```

Ожидаемый следующий PASS после успешного обучения: `PASS_V5_TWO_BLOCK_ML_TRAINED_POST_TRAIN_GUARD_READY_FOR_FORWARD`. Forward запускать только после него.

## STAS5 V5C R2Q Quality-Fix Train And Diagnostic Forward

Новая рельса после ML quality fix. Не использовать старый R2 run_id, чтобы не смешивать артефакты.

1. TrainingGuard:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode TrainingGuard `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-06 `
  -TrainRunId stas5_v5c_r2q_train_20260127_20260306
```

2. Train, только после guard PASS:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Train `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-06 `
  -TrainRunId stas5_v5c_r2q_train_20260127_20260306
```

3. Diagnostic forward week2, только после post-train guard PASS:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Forward `
  -ForwardStartDay 2026-03-07 `
  -ForwardEndDay 2026-03-13 `
  -ContextStartDay 2026-01-27 `
  -ContextWarmupMinutes 720 `
  -TrainManifestPath .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r2q_train_20260127_20260306\STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json `
  -ForwardRunId stas5_v5c_r2q_forward_20260307_20260313 `
  -OpenFolder
```

Открыть графики после forward:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r2q_forward_20260307_20260313\visual_review
```

Важно: week2 уже смотрели глазами, поэтому это diagnostic replay без future leakage в коде, но не новый human-blind proof. Для настоящего blind proof нужна следующая неразмеченная неделя.

## STAS5 V5C R2 Train And Blind Forward Week2

Текущий R2 batch уже собран и guard `PASS`:

```text
STAS5_ML_CORE/artifacts/v5c/STAS5_V5C_BATCH_20260127_20260306_GUARD_V1.json
rows=3172
entry_y 1=359 / 0=2813
features=439
```

Пользовательский порядок запуска: сначала training guard, потом train, потом blind forward week2. Не использовать `-NoStrict`.

1. Только R2 TrainingGuard, без обучения:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode TrainingGuard `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-06 `
  -TrainRunId stas5_v5c_r2_train_20260127_20260306
```

Ожидаемо: `PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING`.

2. R2 Train, запускать только после TrainingGuard PASS:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Train `
  -TrainStartDay 2026-01-27 `
  -TrainEndDay 2026-03-06 `
  -TrainRunId stas5_v5c_r2_train_20260127_20260306
```

Ожидаемый train manifest после успешного обучения:

```text
STAS5_ML_CORE/artifacts/v5c/model/runs/stas5_v5c_r2_train_20260127_20260306/STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json
```

3. Blind forward week2, запускать только после post-train guard PASS:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 `
  -Mode Forward `
  -ForwardStartDay 2026-03-07 `
  -ForwardEndDay 2026-03-13 `
  -ContextStartDay 2026-01-27 `
  -ContextWarmupMinutes 720 `
  -TrainManifestPath .\STAS5_ML_CORE\artifacts\v5c\model\runs\stas5_v5c_r2_train_20260127_20260306\STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json `
  -ForwardRunId stas5_v5c_r2_forward_20260307_20260313 `
  -OpenFolder
```

После forward открыть графики:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_r2_forward_20260307_20260313\visual_review
```

Граница no-future: `2026-03-07..2026-03-13` не должны участвовать в R2 train или threshold tuning. Дни `2026-02-28..2026-03-06` уже входят в R2 train как teacher-разметка и больше не являются blind proof для R2.

## STAS5 V5C R2 Text Encoding Audit

Проверить, что в R2 review-артефактах нет question-mark placeholders и типичных UTF-8/CP1251 кракозяб:

```powershell
$bad = [char]0xfffd; rg -n "\?\?\?|$bad|Ð|Ñ|Â|Ã|РЎ|Рџ|Рґ|Р»|Рѕ|РЅ|Рё|Р°|Рµ|СЃ|С‚|СЂ|СЏ|СЊ|С‹|С‡|С€" STAS5_ML_CORE/artifacts/v5c -g "*.md" -g "*.json" -g "*.csv"
```

Ожидаемый результат после фикса:

```text
no matches
```

Открыть отчет по фиксу:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\review\r2_user_review\STAS5_V5C_R2_TEXT_ENCODING_AUDIT_20260717_RU.md
```

## STAS5 V5C R2 Close Reviewed Day

Закрыть reviewed day как teacher-разметку для R2 без запуска training:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-02-28 -Stage All -GoodIds LA022,LA023,LA032,LA035,LA043,LA047,LA052,LA062,LA067,LA068
```

Проверить итоговый дневной пакет:

```powershell
@'
import pandas as pd
from pathlib import Path
p = Path("STAS5_ML_CORE/artifacts/v5/market_passports/20260228/STAS5_V5_MARKET_PASSPORT_20260228_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv")
df = pd.read_csv(p)
print(len(df), df["entry_y"].value_counts().sort_index().to_dict())
print(",".join(df.loc[df["entry_y"].astype(int).eq(1), "candidate_id"].tolist()))
'@ | .\.venv\Scripts\python.exe -X utf8 -
```

Ожидаемый итог для текущей закрытой версии `2026-02-28`:

```text
rows=81
entry_y 1=10 / 0=71
GOOD=LA022,LA023,LA032,LA035,LA043,LA047,LA052,LA062,LA067,LA068
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

Закрытая команда для `2026-03-01`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-01 -Stage All -GoodIds LA002,LA005,LA012,LA033,LA044,LA048,LA055,LA071,LA075
```

Ожидаемый итог для текущей закрытой версии `2026-03-01`:

```text
rows=81
entry_y 1=9 / 0=72
GOOD=LA002,LA005,LA012,LA033,LA044,LA048,LA055,LA071,LA075
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

Закрытая команда для `2026-03-02`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-02 -Stage All -GoodIds LA006,LA025,LA027,LA028,LA049,LA051,LA052,LA053,LA057,LA063,LA067,LA070
```

Ожидаемый итог для текущей закрытой версии `2026-03-02`:

```text
rows=81
entry_y 1=12 / 0=69
GOOD=LA006,LA025,LA027,LA028,LA049,LA051,LA052,LA053,LA057,LA063,LA067,LA070
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

Закрытая команда для `2026-03-03`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-03 -Stage All -GoodIds LA006,LA007,LA043,LA045,LA055,LA060,LA062,LA066,LA067,LA072,LA082,LA083
```

Ожидаемый итог для текущей закрытой версии `2026-03-03`:

```text
rows=89
entry_y 1=12 / 0=77
GOOD=LA006,LA007,LA043,LA045,LA055,LA060,LA062,LA066,LA067,LA072,LA082,LA083
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

Закрытая команда для `2026-03-04`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-04 -Stage All -GoodIds LA014,LA019,LA020,LA022,LA034,LA040,LA047,LA051,LA071
```

Ожидаемый итог для текущей закрытой версии `2026-03-04`:

```text
rows=72
entry_y 1=9 / 0=63
GOOD=LA014,LA019,LA020,LA022,LA034,LA040,LA047,LA051,LA071
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

Закрытая команда для `2026-03-05`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-05 -Stage All -GoodIds LA008,LA023,LA030,LA035,LA049,LA053,LA054,LA059,LA064,LA065,LA067
```

Ожидаемый итог для текущей закрытой версии `2026-03-05`:

```text
rows=85
entry_y 1=11 / 0=74
GOOD=LA008,LA023,LA030,LA035,LA049,LA053,LA054,LA059,LA064,LA065,LA067
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

Закрытая команда для `2026-03-06`:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-03-06 -Stage All -GoodIds LA006,LA023,LA028,LA047,LA055,LA066
```

Ожидаемый итог для текущей закрытой версии `2026-03-06`:

```text
rows=87
entry_y 1=6 / 0=81
GOOD=LA006,LA023,LA028,LA047,LA055,LA066
guard=PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY
```

## STAS5 V5C Continuous Train And Forward

Полный повтор непрерывного контура `V5C_CONTINUOUS`: пересобрать batch, обучить two-block, прогнать blind forward `2026-02-28..2026-03-06`, построить графики и открыть папку.

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode All -ContextWarmupMinutes 720 -OpenFolder
```

Только пересобрать V5C batch/guard без обучения:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode BuildBatch -ContextWarmupMinutes 720
```

Только обучить по уже готовому V5C batch:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode Train -ContextWarmupMinutes 720
```

Только blind forward по последней V5C модели:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode Forward -ContextWarmupMinutes 720
```

Открыть графики текущего V5C forward:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5c\forward\runs\stas5_v5c_continuous_forward_20260228_20260306_20260716_155343\visual_review
```

Перерисовать графики текущего V5C forward без обучения и без нового forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1 -Mode RenderForward -ForwardRunId stas5_v5c_continuous_forward_20260228_20260306_20260716_155343 -ForwardStartDay 2026-02-28 -ForwardEndDay 2026-03-06 -OpenFolder
```

Проверить, что новый visual review использует непрерывный блок `Fon / LONG / SHORT / WAVE`, а серый `GAP` в WAVE не рисуется:

```powershell
@'
import json
from pathlib import Path
p = Path("STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343/visual_review/STAS5_V5_FORWARD_VISUAL_REVIEW_MANIFEST_V1.json")
m = json.loads(p.read_text(encoding="utf-8"))
print(m["status"], m["png_count"])
for c in m["checks"]:
    if "strength" in c["check"] or "gap" in c["check"] or "macro_wave" in c["check"]:
        print(c["check"], c["status"], c.get("details", {}))
for item in m["day_outputs"]:
    print(item["day"], item["strength_strip_context_status"], item["strength_strip_context_rows"], item["strength_strip_gap_rows_rendered"], item["strength_strip_macro_wave_directions"])
'@ | .\.venv\Scripts\python.exe -X utf8 -
```

Проверить основные V5C счетчики:

```powershell
@'
import json
from pathlib import Path
root = Path("STAS5_ML_CORE/artifacts/v5c")
batch_guard = json.loads((root / "STAS5_V5C_BATCH_20260127_20260227_GUARD_V1.json").read_text(encoding="utf-8"))
latest_forward = json.loads((root / "forward/STAS5_V5C_LATEST_TWO_BLOCK_FORWARD_RUN.json").read_text(encoding="utf-8"))
forward_manifest = json.loads(Path(latest_forward["manifest_path"]).read_text(encoding="utf-8"))
print(batch_guard["status"], batch_guard["rows"], batch_guard["entry_y_counts"], batch_guard["feature_count"])
print(forward_manifest["status"], forward_manifest["rows"], forward_manifest["decision_counts_total"])
print(forward_manifest["visual_review_status"], forward_manifest["visual_review_png_count"])
'@ | .\.venv\Scripts\python.exe -X utf8 -
```

Ожидаемый результат:

```text
batch guard PASS, rows=2596, entry_y 1=290 / 0=2306, features=439
forward PASS, rows=576, ENTER=62 / WATCH=121 / SKIP=393
visual PASS, png_count=14
```

Проверить, что WAVE-полоса закрывает доступный конец свечей и использует cumulative percent от настоящего старта волны:

```powershell
@'
import json
from pathlib import Path
p = Path("STAS5_ML_CORE/artifacts/v5c/forward/runs/stas5_v5c_continuous_forward_20260228_20260306_20260716_155343/visual_review/STAS5_V5_FORWARD_VISUAL_REVIEW_MANIFEST_V1.json")
m = json.loads(p.read_text(encoding="utf-8"))
for c in m["checks"]:
    if "tail" in c["check"] or "available" in c["check"] or "cross_day" in c["check"] or "cumulative" in c["check"]:
        print(c["check"], c["status"], c.get("details", {}))
for item in m["day_outputs"]:
    print(
        item["day"],
        "available=", item["strength_strip_available_end_utc"],
        "last=", item["strength_strip_last_wave_end_utc"],
        "covered=", item["strength_strip_tail_covered_to_data_end"],
        "filled_min=", item["strength_strip_tail_gap_minutes_filled"],
        "basis=", item["strength_strip_label_pct_basis"],
    )
'@ | .\.venv\Scripts\python.exe -X utf8 -
```

## STAS5 V5 Forward Visual Review With All LA Labels

Перерендерить обзорные графики уже готового V5 forward run без обучения:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_two_block_ml.ps1 -Mode RenderForward -ForwardRunId stas5_v5_forward_20260228_20260306_20260716 -ForwardStartDay 2026-02-28 -ForwardEndDay 2026-03-06 -OpenFolder
```

Открыть папку со всеми V5-графиками:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\forward\runs\stas5_v5_forward_20260228_20260306_20260716\visual_review
```

Открыть пример overview с желтыми `LAxxx`, желтыми X/ромбами и зелеными треугольниками `ENTER`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\forward\runs\stas5_v5_forward_20260228_20260306_20260716\visual_review\20260304\STAS5_V5_FORWARD_VISUAL_REVIEW_20260304_ENTER_ARROWS.png
```

Открыть closeup-лист входов за день:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\forward\runs\stas5_v5_forward_20260228_20260306_20260716\visual_review\20260304\STAS5_V5_FORWARD_ENTER_CLOSEUPS_20260304.png
```

Проверить manifest:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\forward\runs\stas5_v5_forward_20260228_20260306_20260716\visual_review\STAS5_V5_FORWARD_VISUAL_REVIEW_MANIFEST_V1.json
```

Ожидаемый статус:

```text
PASS_V5_FORWARD_VISUAL_REVIEW_READY_ALL_LA_LABELS_ENTER_TRIANGLES
png_count=14
```

## STAS5 V5 Two-Block Train And Forward

Полный проход training + blind forward:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_two_block_ml.ps1 -Mode TrainForward -ForwardStartDay 2026-02-28 -ForwardEndDay 2026-03-06
```

Только training guard:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_two_block_ml.ps1 -Mode TrainingGuard
```

Только training:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_two_block_ml.ps1 -Mode Train
```

Только forward после сохраненной модели:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_two_block_ml.ps1 -Mode Forward -ForwardStartDay 2026-02-28 -ForwardEndDay 2026-03-06
```

Итоговый отчет текущего прохода:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\STAS5_V5_TWO_BLOCK_TRAIN_FORWARD_20260716_RU.md
```

Forward predictions:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\forward\runs\stas5_v5_forward_20260228_20260306_20260716\STAS5_V5_FORWARD_PREDICTIONS_20260228_20260306_V1.csv
```

Граница: two-block guard `PASS`, но OOF хуже baseline. Перед production нужен review forward `ENTER` и baseline-forward сравнение.

## STAS5 V5 Two-Block ML TZ

Открыть ТЗ следующего ML-этапа:

```powershell
ii .\STAS5_ML_CORE\09_STAS5_V5_TWO_BLOCK_ML_TZ_RU.md
```

Текущий статус этапа:

```text
TZ_DRAFT_READY_FOR_USER_REVIEW_NO_TRAINING
```

Следующая команда еще должна быть реализована: `STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1`. До ее `PASS` не запускать baseline/training. До post-train guard `PASS` не запускать forward.

## STAS5 V5 Batch Dataset And Guard

Собрать batch dataset и batch leakage/no-future guard по текущему approved диапазону:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_batch_dataset_builder.ps1
```

То же напрямую через Python:

```powershell
$env:PYTHONPATH='src'
python -m mlbotnav.stas5_v5_batch_dataset_builder --start-day 2026-01-27 --end-day 2026-02-27
```

Открыть RU-аудит после сборки:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_batch_dataset_builder.ps1 -OpenReport
```

Проверить итоговый guard:

```powershell
@'
import json
from pathlib import Path
p = Path("STAS5_ML_CORE/artifacts/v5/STAS5_V5_BATCH_20260127_20260227_GUARD_V1.json")
j = json.loads(p.read_text(encoding="utf-8"))
print(j["status"])
print(j["rows"], j["entry_y_counts"], j["feature_count"])
print({item["check"]: item["status"] for item in j["checks"]})
'@ | python -X utf8 -
```

Ожидаемый результат:

```text
PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING
rows=2596
entry_y 1=290 / 0=2306
features=439
```

Граница: эта команда не запускает training и forward. Следующий слой должен начинаться с отдельного training guard и two-block ML `MARKET_PHASE_STATE_ML -> ENTRY_ML`.

## STAS5 V5 Аудит Готовой Пачки

Полный аудит V5-папки:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_folder_audit.ps1 -OpenReport
```

Текущий отчет диапазона `2026-01-27..2026-02-27`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\STAS5_V5_RANGE_AUDIT_20260127_20260227_RU.md
```

Текущий результат диапазона:

```text
32/32 full-ready days
2596 rows
entry_y 1=290 / 0=2306
features=439
training=False
forward=False
```

Следующий командный слой еще нужно реализовать: `V5 batch dataset builder` и `batch leakage/no-future guard`.

## STAS5 V5 День По GOOD ids

Одна команда для дня, когда пользователь уже назвал хорошие входы `LAxxx`. Она не запускает обучение и не делает forward.

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage All -GoodIds LA020,LA037,LA042,LA045,LA051,LA059,LA069,LA078,LA084 -OpenFolder
```

Что делает команда:

```text
1. Находит или собирает FULL274.
2. По GoodIds создает approved passport/targets.
3. Проверяет baseline guard: 274 features, targets not in features.
4. Строит cs_*.
5. Строит fcs_* и карту дня.
6. Запускает V5 folder audit.
```

Отдельно создать только approved-passport слой из GOOD ids:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_approved_passport_builder.ps1 -Day 2026-01-28 -GoodIds LA020,LA037,LA042,LA045,LA051,LA059,LA069,LA078,LA084 -OpenFolder
```

Открыть готовую папку `2026-01-28`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260128
```

Открыть главный CSV дня:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260128\STAS5_V5_MARKET_PASSPORT_20260128_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Открыть главную карту дня:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260128\DAY_MARKET_PASSPORT_20260128_FULL_CAUSAL_STRUCTURE_MAP_V1.png
```

Проверить guard-и дня:

```powershell
@'
import json
import pandas as pd
from pathlib import Path
base = Path("STAS5_ML_CORE/artifacts/v5/market_passports/20260128")
for name in [
    "STAS5_V5_MARKET_PASSPORT_20260128_PHASE_STATE_REASON_GUARD_V2.json",
    "STAS5_V5_MARKET_PASSPORT_20260128_CAUSAL_STRUCTURE_GUARD_V1.json",
    "STAS5_V5_MARKET_PASSPORT_20260128_FULL_CAUSAL_STRUCTURE_GUARD_V1.json",
]:
    guard = json.load(open(base / name, encoding="utf-8"))
    print(name, guard["status"], "features=", guard.get("feature_count"))
df = pd.read_csv(base / "STAS5_V5_MARKET_PASSPORT_20260128_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv", encoding="utf-8-sig")
print("rows:", len(df))
print("entry_y:", df["entry_y"].value_counts().sort_index().to_dict())
print("good_ids:", df.loc[df["entry_y"].eq(1), "candidate_id"].tolist())
'@ | python -X utf8 -
```

Важно: `GoodIds` - это teacher-target разметка истории. В `X` они не попадают. Обучение запускать только после batch dataset и batch guard по нескольким full-ready дням.

## STAS5 V5 Главная Лесенка Дня

Одна команда для нового дня. Она не запускает обучение и не делает forward.

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage All -OpenFolder
```

Как она работает:

```text
1. Если FULL274 уже есть - использует его.
2. Если FULL274 нет - собирает FULL274.
3. Проверяет, есть ли approved V5 passport/targets.
4. Если approved нет - останавливается и показывает недостающие файлы.
5. Если approved есть - строит cs_*.
6. Потом строит fcs_*.
7. Потом запускает V5 folder audit.
```

Режимы:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage Collect
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage BuildApproved
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage Audit
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage Open
```

Пересобрать FULL274 даже если run уже есть:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1 -Day 2026-01-28 -Stage Collect -ForceCollect -OpenFolder
```

Полный аудит папки V5:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_folder_audit.ps1 -OpenReport
```

Текущий отчет аудита:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\STAS5_V5_FOLDER_AUDIT_20260715_RU.md
```

## STAS5 V5 Full Causal Market-Structure 2026-01-27

Пересобрать полный causal market-structure пакет дня:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_full_causal_structure_builder.ps1 -Day 2026-01-27
```

Открыть папку дня после сборки:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_full_causal_structure_builder.ps1 -Day 2026-01-27 -OpenFolder
```

Открыть главный файл-указатель:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\00_OPEN_FIRST_RU.md
```

Открыть главную ML-ready таблицу `274 + cs_* + fcs_* + targets`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Открыть новую полную карту структуры:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\DAY_MARKET_PASSPORT_20260127_FULL_CAUSAL_STRUCTURE_MAP_V1.png
```

Открыть новые full-causal артефакты:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_FULL_STRUCTURE_CANDIDATE_FEATURES_CAUSAL_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_LEVELS_CAUSAL_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_CHANNELS_CAUSAL_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_REGIMES_CAUSAL_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_EVENTS_CAUSAL_V1.csv
```

Проверить full guard:

```powershell
@'
import json
import pandas as pd
from pathlib import Path
base = Path("STAS5_ML_CORE/artifacts/v5/market_passports/20260127")
guard = json.load(open(base / "STAS5_V5_MARKET_PASSPORT_20260127_FULL_CAUSAL_STRUCTURE_GUARD_V1.json", encoding="utf-8"))
df = pd.read_csv(base / "STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv", encoding="utf-8-sig")
print(guard["status"])
print("rows:", len(df), "features:", guard["feature_count"])
print("base_before_fcs:", guard["base_feature_count"], "fcs:", guard["full_causal_feature_count"])
print("entry_y:", df["entry_y"].value_counts().sort_index().to_dict())
print("checks:", {c["check"]: c["status"] for c in guard["checks"]})
print("artifact_counts:", guard["artifact_counts"])
'@ | python -X utf8 -
```

Важно: это не обучение. Это подготовка одного approved дня с live-safe `X` признаками и teacher-target `y`.

## STAS5 V5 Causal Builder View 2026-01-27

Открыть главный расширенный график структуры V5:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\DAY_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_MAP_V4_CLEAN.png
```

Открыть таблицу тегов расширенной карты:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_MAP_TAGS_V4.csv
```

Открыть график, где causal-builder показан прямо на цене:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\DAY_MARKET_PASSPORT_20260127_CAUSAL_BUILDER_VIEW_V2.png
```

Открыть таблицу визуальных тегов builder'а:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_BUILDER_VISUAL_TAGS_V2.csv
```

## STAS5 V5 Causal Market-Structure 2026-01-27

Открыть главный навигационный файл дня:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\00_OPEN_FIRST_RU.md
```

Открыть главный CSV `274F + cs_* + targets`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv
```

Открыть causal features, allowlist и guard:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_FEATURES_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_PLUS_CAUSAL_STRUCTURE_V1.json
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_GUARD_V1.json
```

Пересобрать causal-structure пакет дня:

```powershell
.\STAS5_ML_CORE\run_stas5_v5_causal_structure_builder.ps1 -Day 2026-01-27
```

То же напрямую через Python:

```powershell
$env:PYTHONPATH='src'
python -m mlbotnav.stas5_v5_causal_structure_builder --day 2026-01-27
```

Проверить текущий guard и счетчики:

```powershell
@'
import json
import pandas as pd
base = "STAS5_ML_CORE/artifacts/v5/market_passports/20260127"
guard = json.load(open(base + "/STAS5_V5_MARKET_PASSPORT_20260127_CAUSAL_STRUCTURE_GUARD_V1.json", encoding="utf-8"))
df = pd.read_csv(base + "/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv", encoding="utf-8-sig")
print(guard["status"])
print("rows:", len(df))
print("features:", guard["feature_count"])
print("base:", guard["base_feature_count"], "causal:", guard["causal_structure_feature_count"])
print("entry_y:", df["entry_y"].value_counts().sort_index().to_dict())
print("checks:", {c["check"]: c["status"] for c in guard["checks"]})
'@ | python -X utf8 -
```

Открыть проектный аудит V5:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\STAS5_V5_PROJECT_AUDIT_20260715_RU.md
ii .\STAS5_ML_CORE\artifacts\v5\STAS5_V5_PROJECT_AUDIT_20260715.json
```

Важно: это не команда обучения. V5 training и V5 forward запускать только после batch dataset и batch guard по нескольким approved дням.

## STAS5 V5 Быстрый Вход В Папку 2026-01-27

Открыть файл-указатель, чтобы не путаться в `V1/V2/V3`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\00_OPEN_FIRST_RU.md
```

Открыть саму папку дня:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127
```

## STAS5 V5 Entry/Phase/State/Reason 2026-01-27

Открыть актуальную V2 ML-ready таблицу:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv
```

Открыть ledger, phase segments, allowlist и guard:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_ENTRY_PHASE_STATE_REASON_LEDGER_USER_APPROVED_V2.csv
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_PHASE_SEGMENTS_USER_APPROVED_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_PHASE_STATE_REASON_GUARD_V2.json
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\TRAINING_SCHEMA_ENTRY_PHASE_STATE_REASON_RU.md
```

Проверить актуальный V2 guard:

```powershell
@'
import json
import pandas as pd
base = "STAS5_ML_CORE/artifacts/v5/market_passports/20260127"
guard = json.load(open(base + "/STAS5_V5_MARKET_PASSPORT_20260127_PHASE_STATE_REASON_GUARD_V2.json", encoding="utf-8"))
df = pd.read_csv(base + "/STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv", encoding="utf-8-sig")
print(guard["status"])
print(df.shape)
print("entry_y:", df["entry_y"].value_counts().sort_index().to_dict())
print("phase_y:", df["phase_y"].value_counts().sort_index().to_dict())
print("forbidden:", guard["forbidden_feature_columns_detected"])
'@ | python -X utf8 -
```

## STAS5 V5 Market Passport Package 2026-01-27

Открыть отдельную упакованную папку дня:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127
```

Открыть ML-ready таблицу и allowlist 274 признаков:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_ML_READY_274F_LABELS_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_FEATURE_ALLOWLIST_274_V1.json
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\TRAINING_SCHEMA_RU.md
```

Открыть числовую структуру дня:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_MARKET_STRUCTURE_NUMERIC_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5\market_passports\20260127\STAS5_V5_MARKET_PASSPORT_20260127_274F_LABELS_PLUS_STRUCTURE_CONTEXT_V1.csv
```

Проверить пакет:

```powershell
@'
import json
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v5/market_passports/20260127/STAS5_V5_MARKET_PASSPORT_20260127_PACKAGE_MANIFEST.json"
j = json.load(open(p, encoding="utf-8"))
df = pd.read_csv(j["outputs"]["ml_ready_274f_labels"], encoding="utf-8-sig")
print(j["status"], j["rows"], j["feature_count"], j["label_counts"])
print(df["train_label_binary"].value_counts().sort_index().to_dict())
print(j["forbidden_feature_columns_detected"])
'@ | python -X utf8 -
```

## STAS5 V5 Market Passport 2026-01-27 User Approved V3

Открыть финальный approved overlay:

```powershell
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\DAY_MARKET_PASSPORT_20260127_USER_APPROVED_V3_ANNOTATED_TOP.png
```

Открыть финальный паспорт и ledger:

```powershell
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\DAY_MARKET_PASSPORT_20260127_USER_APPROVED_RU.md
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\DAY_MARKET_PASSPORT_LEDGER_20260127_USER_APPROVED_V3.csv
```

Проверить финальные счетчики:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_LEDGER_20260127_USER_APPROVED_V3.csv"
df = pd.read_csv(p, encoding="utf-8-sig")
print(len(df))
print(df["entry_label"].value_counts().to_dict())
print("GOOD:", ", ".join(df.loc[df.entry_label=="GOOD_APPROVED", "candidate_id"]))
'@ | python -X utf8 -
```

## STAS5 V5 Market Passport 2026-01-27 V2

Открыть актуальный V2 overlay:

```powershell
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\DAY_MARKET_PASSPORT_20260127_LABELS_DRAFT_V2_ANNOTATED_TOP.png
```

Открыть паспорт и ledger:

```powershell
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\DAY_MARKET_PASSPORT_20260127_RU.md
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\DAY_MARKET_PASSPORT_LEDGER_20260127_DRAFT_V2.csv
```

Проверить счетчики V2:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/DAY_MARKET_PASSPORT_LEDGER_20260127_DRAFT_V2.csv"
df = pd.read_csv(p, encoding="utf-8-sig")
print(len(df))
print(df["entry_label"].value_counts().to_dict())
print("GOOD_APPROVED:", ", ".join(df.loc[df.entry_label=="GOOD_APPROVED", "candidate_id"]))
print("GOOD_ALT:", ", ".join(df.loc[df.entry_label=="GOOD_ALT", "candidate_id"]))
print("REVIEW_ONLY:", ", ".join(df.loc[df.entry_label=="REVIEW_ONLY", "candidate_id"]))
'@ | python -X utf8 -
```

## STAS5 V5 Market Passport Trial 2026-01-27

Открыть актуальный слой согласованных пользовательских входов:

```powershell
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_USER_DESIRED_V1_ANNOTATED_TOP.png
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_USER_DESIRED_V1.csv
```

Открыть папку пробного паспорта:

```powershell
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127
```

Открыть быстрый crop верхнего графика:

```powershell
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_ANNOTATED_TOP.png
```

Открыть полный PNG:

```powershell
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_ANNOTATED_FULL.png
```

Открыть draft-зоны и отчет:

```powershell
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_DRAFT_ZONES.csv
ii .\STAS5_ML_CORE\runs\full274_feature_collect_20260127_20260715_090857\market_passport_trial_20260127\STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_RU.md
```

Проверить счетчики draft-зон:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/runs/full274_feature_collect_20260127_20260715_090857/market_passport_trial_20260127/STAS5_V5_MARKET_PASSPORT_TRIAL_20260127_DRAFT_ZONES.csv"
df = pd.read_csv(p)
print(len(df))
print(df["draft_label"].value_counts().to_dict())
print(df[["phase_id","candidate_id","entry_time_utc","entry_price_5bps","draft_label","draft_reason"]].to_string(index=False))
'@ | python -
```

## STAS5 FULL274 One-Day Feature Collect

Статус: `PASS`, команда добавлена `2026-07-15`.

Отдельный wrapper для проверки одного дня до обучения:

```powershell
.\STAS5_ML_CORE\run_stas5_full274_feature_collect.ps1 -Day 2026-04-01 -OpenFolder
```

Что делает команда:

```text
STAS1 candidates -> STAS2 context -> V1 111 features -> V2/STAS4/STAS5 163 features -> FULL274 snapshot -> visual approval PNG
```

Артефакты каждого запуска пишутся в отдельную папку:

```text
STAS5_ML_CORE/runs/full274_feature_collect_YYYYMMDD_YYYYMMDD_HHMMSS/
```

Контрольный запуск:

```text
STAS5_ML_CORE/runs/full274_feature_collect_20260401_20260715_084509/
rows=81
features=274
v1_features=111
v2_features=163
training_started=false
```

Главные файлы внутри run:

```text
STAS5_FULL274_FEATURE_SNAPSHOT_YYYYMMDD.csv
STAS5_FULL274_FEATURE_SNAPSHOT_YYYYMMDD.manifest.json
YYYYMMDD/STAS5_V2_FEATURE_VISUAL_APPROVAL_YYYYMMDD.png
STAS5_FULL274_FEATURE_COLLECT_SUMMARY.json
```

Обучение, API, TP/Stas3 этой командой не запускаются.

## Актуальный источник правды STAS5 V4

Перед любыми следующими командами по V4 проверять текущий guard/unified ledger, а не старые исторические ожидания из нижних секций:

```powershell
@'
import json
import pandas as pd
ledger = "STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv"
guard = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json"
df = pd.read_csv(ledger)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(int(df["is_group_winner"].astype(int).sum()))
print(json.load(open(guard, encoding="utf-8"))["status"])
'@ | python -
```

## STAS5 V5 Row-Level Pivot / Day23 Pre-Knife Artifacts

Статус: `V5_ROW_LABEL_PREP_NO_TRAINING_COMMAND_YET`.

Открыть новый отчет по `2026-05-23`, где верхняя pre-knife зона переведена из good в no-trade:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260523\STAS5_V4_GROUP_RANK_REVIEW_20260523_USER_CORRECTED_V2_PRE_KNIFE_RU.md
```

Открыть новый corrected ledger:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260523\STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V2_PRE_KNIFE.csv
```

Открыть числовой аудит по ножу:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260523\STAS5_V4_GROUP_RANK_REVIEW_20260523_PRE_KNIFE_NUMERIC_AUDIT.csv
```

Открыть общий V5 label-source `2026-05-15..2026-05-25` с замененным day23:

```powershell
ii .\STAS5_ML_CORE\artifacts\v5\labels\STAS5_V5_ROW_LABEL_SOURCE_20260515_20260525_WITH_DAY23_PRE_KNIFE_V1.csv
ii .\STAS5_ML_CORE\artifacts\v5\labels\STAS5_V5_ROW_LABEL_SOURCE_20260515_20260525_WITH_DAY23_PRE_KNIFE_V1.manifest.json
ii .\STAS5_ML_CORE\artifacts\v5\labels\STAS5_V5_ROW_LABEL_SOURCE_20260515_20260525_WITH_DAY23_PRE_KNIFE_V1_RU.md
```

Важная граница: V4/V4L команды выше оставлены только для воспроизведения старых артефактов. Следующая учеба должна быть отдельным V5 row-level ML-контуром по исправленным меткам; команды обучения V5 появятся только после реализации dataset/guard/train/forward.

## STAS5 V4L Live-Safe Full Cycle

Главная команда для нового честного обучения без подглядывания в будущее и слепого forward `2026-05-26..2026-05-30`:

```powershell
.\STAS5_ML_CORE\run_stas5_v4l_live_safe_train_forward.ps1
```

То же самое с явными параметрами:

```powershell
.\STAS5_ML_CORE\run_stas5_v4l_live_safe_train_forward.ps1 `
  -ForwardStartDay 2026-05-26 `
  -ForwardEndDay 2026-05-30 `
  -EnterThreshold 0.50 `
  -UnsureThreshold 0.35 `
  -Stas2RenderLimit 1
```

Что делает команда:

1. собирает live-safe train dataset `2026-05-01..2026-05-25`;
2. проверяет `prefix_invariance` и banned full-group/future/old-ML features;
3. обучает `STAS5_V4L_LIVE_SAFE_GROUP_RANKER_V0`;
4. делает blind forward `2026-05-26..2026-05-30`;
5. пишет CSV/PNG в `STAS5_ML_CORE/artifacts/v4l/forward/runs/...`.

Открыть последний V4L forward pointer:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4l\forward\STAS5_V4L_LATEST_FORWARD_RUN.json
```

Открыть последний проверенный V4L forward run:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4l\forward\runs\stas5_v4l_forward_20260526_20260530_20260714_181635
```

Ожидание на текущем состоянии: `738` строк, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, winners `64`, guard `PASS`.

## Commands 2026-07-14 STAS5 V4 2026-05-25 Screenshot Check

Статус: `STAS5_V4_20260525_USER_CHECKED_PASS_NO_TRAINING`.

Открыть проверочный отчет, draft CSV и кропы:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260525\STAS5_V4_GROUP_RANK_REVIEW_20260525_USER_CHECKED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260525\STAS5_V4_GROUP_RANK_LEDGER_20260525_DRAFT.csv
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260525\STAS5_V4_20260525_PRE_LONDON_LA019_LA020_WIDE_CROP.png
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260525\STAS5_V4_20260525_USER_CIRCLE_LA038_CROP.png
```

Проверить day25:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_LEDGER_20260525_DRAFT.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(df[df["is_group_winner"].astype(int).eq(1)]["candidate_id"].tolist())
print(df[df["candidate_id"].isin(["LA019","LA020","LA038","LA066","LA067"])][["candidate_id","group_id","rank_label","primary_reason_code"]].to_string(index=False))
'@ | python -
```

Ожидание: `68` строк, `BEST_GOOD=5`, `GOOD_ALT=4`, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=19`; winners `LA014`, `LA020`, `LA038`, `LA059`, `LA066`; `LA019=GOOD_ALT`, `LA020=BEST_GOOD`, `LA038=BEST_GOOD`.

## Commands 2026-07-14 STAS5 V4 2026-05-24 Screenshot Check

Статус: `STAS5_V4_20260524_USER_CHECKED_PASS_NO_TRAINING`.

Открыть проверочный отчет, draft CSV и кропы:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260524\STAS5_V4_GROUP_RANK_REVIEW_20260524_USER_CHECKED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260524\STAS5_V4_GROUP_RANK_LEDGER_20260524_DRAFT.csv
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260524\day24_user_circle_left_pre_london_x5.png
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260524\day24_user_circle_LA042_x5.png
```

Проверить day24:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_LEDGER_20260524_DRAFT.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(df[df["is_group_winner"].astype(int).eq(1)]["candidate_id"].tolist())
print(df[df["candidate_id"].isin(["LA015","LA042","LA065","LA067"])][["candidate_id","group_id","rank_label","primary_reason_code"]].to_string(index=False))
'@ | python -
```

Ожидание: `70` строк, `BEST_GOOD=5`, `GOOD_ALT=5`, `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=6`; winners `LA009`, `LA015`, `LA024`, `LA042`, `LA065`; `LA067=GOOD_ALT`.

## Commands 2026-07-14 STAS5 V4 2026-05-23 Screenshot Check

Статус: `STAS5_V4_20260523_USER_CORRECTED_V1_NO_TRAINING`.

Открыть исправленный отчет, CSV и общий кроп:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260523\STAS5_V4_GROUP_RANK_REVIEW_20260523_USER_CORRECTED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260523\STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V1.csv
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260523\day23_user_circles_all_wide.png
```

Проверить day23:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_USER_CORRECTED_V1.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(df[df["is_group_winner"].astype(int).eq(1)]["candidate_id"].tolist())
print(df[df["candidate_id"].isin(["LA034","LA035","LA036","LA042","LA051"])][["candidate_id","group_id","rank_label","primary_reason_code"]].to_string(index=False))
'@ | python -
```

Ожидание: `63` строки, `BEST_GOOD=7`, `GOOD_ALT=4`, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=12`; winners `LA007`, `LA022`, `LA033`, `LA034`, `LA036`, `LA042`, `LA051`.

Проверить unified ledger:

```powershell
@'
import json
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts().to_dict())
print("winners", int(df["is_group_winner"].astype(int).sum()))
g = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json"
print(json.load(open(g, encoding="utf-8"))["status"])
'@ | python -
```

Ожидание: `rows=738`, `BEST_GOOD=64`, `GOOD_ALT=42`, `BAD_IN_GROUP=433`, `NO_TRADE_GROUP=199`, guard `PASS`.

## Commands 2026-07-14 STAS5 V4 2026-05-22 Screenshot Check

Статус: `STAS5_V4_20260522_USER_CORRECTED_V1_NO_TRAINING`.

Открыть исправленный отчет, CSV и увеличенный кроп:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260522\STAS5_V4_GROUP_RANK_REVIEW_20260522_USER_CORRECTED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260522\STAS5_V4_GROUP_RANK_LEDGER_20260522_USER_CORRECTED_V1.csv
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260522\day22_circle_2_pre_london_x5.png
```

Проверить day22:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_LEDGER_20260522_USER_CORRECTED_V1.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(df[df["is_group_winner"].astype(int).eq(1)]["candidate_id"].tolist())
print(df[df["candidate_id"].isin(["LA022","LA024","LA036","LA047","LA061"])][["candidate_id","group_id","rank_label","primary_reason_code"]].to_string(index=False))
'@ | python -
```

Ожидание: `75` строк, `BEST_GOOD=5`, `GOOD_ALT=4`, `BAD_IN_GROUP=55`, `NO_TRADE_GROUP=11`; winners `LA007`, `LA024`, `LA036`, `LA047`, `LA061`; `LA022=GOOD_ALT`, `LA024=BEST_GOOD`.

Проверить unified ledger:

```powershell
@'
import json
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts().to_dict())
print("winners", int(df["is_group_winner"].astype(int).sum()))
g = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json"
print(json.load(open(g, encoding="utf-8"))["status"])
'@ | python -
```

Ожидание: `rows=738`, `BEST_GOOD=62`, `GOOD_ALT=43`, `BAD_IN_GROUP=434`, `NO_TRADE_GROUP=199`, `winners=62`, guard `PASS`.

Граница: команды только для просмотра/проверки. Не запускать V4 train, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit.

## Commands 2026-07-14 STAS5 V4 2026-05-21 Screenshot Check

Статус: `STAS5_V4_20260521_USER_CORRECTED_V1_NO_TRAINING`.

Открыть исправленный отчет, CSV и кроп:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260521\STAS5_V4_GROUP_RANK_REVIEW_20260521_USER_CORRECTED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260521\STAS5_V4_GROUP_RANK_LEDGER_20260521_USER_CORRECTED_V1.csv
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260521\day21_user_circles_all_wide_x3.png
```

Проверить day21:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_LEDGER_20260521_USER_CORRECTED_V1.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(df[df["is_group_winner"].astype(int).eq(1)]["candidate_id"].tolist())
print(df[df["candidate_id"].isin(["LA039","LA040","LA045","LA048","LA050","LA057","LA059"])][["candidate_id","group_id","rank_label","primary_reason_code"]].to_string(index=False))
'@ | python -
```

Ожидание: `81` строка, `BEST_GOOD=8`, `GOOD_ALT=4`, `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=15`; winners `LA006`, `LA019`, `LA039`, `LA045`, `LA050`, `LA057`, `LA059`, `LA066`.

Проверить unified ledger:

```powershell
@'
import json
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts().to_dict())
print("winners", int(df["is_group_winner"].astype(int).sum()))
g = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json"
print(json.load(open(g, encoding="utf-8"))["status"])
'@ | python -
```

Ожидание: `rows=738`, `BEST_GOOD=62`, `GOOD_ALT=43`, `BAD_IN_GROUP=434`, `NO_TRADE_GROUP=199`, `winners=62`, guard `PASS`.

Граница: команды только для просмотра/проверки. Не запускать V4 train, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit.

## Commands 2026-07-14 STAS5 V4 2026-05-20 Screenshot Check

Статус: `STAS5_V4_20260520_USER_CORRECTED_V1_NO_TRAINING`.

Открыть исправленный отчет, CSV и увеличенный кроп:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260520\STAS5_V4_GROUP_RANK_REVIEW_20260520_USER_CORRECTED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260520\STAS5_V4_GROUP_RANK_LEDGER_20260520_USER_CORRECTED_V1.csv
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260520\day20_user_circles_transition_wide_x4.png
```

Проверить day20:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_LEDGER_20260520_USER_CORRECTED_V1.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(df[df["is_group_winner"].astype(int).eq(1)]["candidate_id"].tolist())
print(df[df["candidate_id"].isin(["LA035","LA036","LA037","LA038","LA039"])][["candidate_id","group_id","rank_label","primary_reason_code"]].to_string(index=False))
'@ | python -
```

Ожидание: `68` строк, `BEST_GOOD=6`, `GOOD_ALT=4`, `BAD_IN_GROUP=27`, `NO_TRADE_GROUP=31`; winners `LA011`, `LA037`, `LA038`, `LA045`, `LA053`, `LA057`.

Проверить unified ledger:

```powershell
@'
import json
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts().to_dict())
print("winners", int(df["is_group_winner"].astype(int).sum()))
g = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json"
print(json.load(open(g, encoding="utf-8"))["status"])
'@ | python -
```

Ожидание для текущего unified ledger после day21: `rows=738`, `BEST_GOOD=62`, `GOOD_ALT=43`, `BAD_IN_GROUP=434`, `NO_TRADE_GROUP=199`, `winners=62`, guard `PASS`.

Граница: команды только для просмотра/проверки. Не запускать V4 train, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit.

## Commands 2026-07-14 STAS5 V4 2026-05-19 Screenshot Check

Статус: `STAS5_V4_20260519_USER_CORRECTED_V1_NO_TRAINING`.

Открыть исправленный отчет и CSV:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260519\STAS5_V4_GROUP_RANK_REVIEW_20260519_USER_CORRECTED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260519\STAS5_V4_GROUP_RANK_LEDGER_20260519_USER_CORRECTED_V1.csv
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260519\day19_user_circle_LA045_zone.png
```

Проверить day19:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_LEDGER_20260519_USER_CORRECTED_V1.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(df[df["is_group_winner"].astype(int).eq(1)]["candidate_id"].tolist())
'@ | python -
```

Ожидание: `65` строк, `BEST_GOOD=6`, `GOOD_ALT=3`, `BAD_IN_GROUP=39`, `NO_TRADE_GROUP=17`; winners `LA005`, `LA016`, `LA032`, `LA042`, `LA046`, `LA063`.

Проверить unified ledger:

```powershell
@'
import json
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts().to_dict())
print("winners", int(df["is_group_winner"].astype(int).sum()))
g = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json"
print(json.load(open(g, encoding="utf-8"))["status"])
'@ | python -
```

Ожидание: `rows=738`, `BEST_GOOD=58`, `GOOD_ALT=44`, `BAD_IN_GROUP=437`, `NO_TRADE_GROUP=199`, `winners=58`, guard `PASS`.

Граница: команды только для просмотра/проверки. Не запускать V4 train, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit.

## Commands 2026-07-14 STAS5 V4 2026-05-18 Screenshot Check

Статус: `STAS5_V4_20260518_USER_CORRECTED_V1_NO_TRAINING`.

Открыть исправленный отчет и CSV:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260518\STAS5_V4_GROUP_RANK_REVIEW_20260518_USER_CORRECTED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260518\STAS5_V4_GROUP_RANK_LEDGER_20260518_USER_CORRECTED_V1.csv
```

Проверить day18:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_LEDGER_20260518_USER_CORRECTED_V1.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(df[df["is_group_winner"].astype(int).eq(1)]["candidate_id"].tolist())
'@ | python -
```

Ожидание: `73` строки, `BEST_GOOD=7`, `GOOD_ALT=7`, `BAD_IN_GROUP=52`, `NO_TRADE_GROUP=7`; winners `LA006`, `LA019`, `LA034`, `LA036`, `LA049`, `LA061`, `LA066`.

## Commands 2026-07-14 STAS5 V4 2026-05-17 Screenshot Check

Статус: `STAS5_V4_20260517_USER_CHECKED_V1_NO_TRAINING`.

Открыть проверочный отчет:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260517\STAS5_V4_GROUP_RANK_REVIEW_20260517_USER_CHECKED_V1_RU.md
```

Проверить текущий day17 CSV:

```powershell
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_LEDGER_20260517_DRAFT.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts().to_dict())
print(df[df["is_group_winner"].astype(int).eq(1)]["candidate_id"].tolist())
'@ | python -
```

Ожидание: `63` строки, `BEST_GOOD=5`, `GOOD_ALT=3`, `BAD_IN_GROUP=25`, `NO_TRADE_GROUP=30`; winners `LA004`, `LA006`, `LA036`, `LA046`, `LA063`.

## Commands 2026-07-14 STAS5 V4 2026-05-16 Screenshot Check

Открыть исправленный day16:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260516\STAS5_V4_GROUP_RANK_REVIEW_20260516_USER_CORRECTED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260516\STAS5_V4_GROUP_RANK_LEDGER_20260516_USER_CORRECTED_V1.csv
```

Ожидание по day16: winners `LA016`, `LA027`, `LA038`, `LA041`; `LA049` не winner.

## Commands 2026-07-14 STAS5 V4 Micro-Group Correction

Открыть исправленный day15 V2:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515\STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V2_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515\STAS5_V4_GROUP_RANK_LEDGER_20260515_USER_CORRECTED_V2.csv
```

Проверить актуальный unified ledger и guard:

```powershell
@'
import json
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts().to_dict())
print("winners", int(df["is_group_winner"].astype(int).sum()))
g = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json"
d = json.load(open(g, encoding="utf-8"))
print(d["status"], d["source_winners"]["2026-05-15"])
'@ | python -
```

Открыть audit перед ручной проверкой `2026-05-16..25`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515_20260525\STAS5_V4_MICRO_GROUP_RISK_AUDIT_20260516_20260525_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515_20260525\STAS5_V4_MICRO_GROUP_RISK_AUDIT_20260516_20260525_SUMMARY.csv
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515_20260525\STAS5_V4_MICRO_GROUP_RISK_AUDIT_20260516_20260525.csv
```

Ожидание после правок day16/day18/day19/day20/day21: `rows=738`, `BEST_GOOD=62`, `GOOD_ALT=43`, guard `PASS`, day21 winners `LA006/LA019/LA039/LA045/LA050/LA057/LA059/LA066`.

Граница: команды только для проверки/просмотра. Не запускать V4 train, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 Screenshot Artifact Inventory 2026-05-01..2026-05-25

Статус: `STAS5_V4_SCREENSHOT_ARTIFACT_INVENTORY_DONE_NO_TRAINING`.

Открыть папку инвентаризации:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\review_navigation\20260714_artifact_inventory
```

Открыть контакт-листы:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\review_navigation\20260714_artifact_inventory\CONTACT_SHEET_20260501_20260514_TRAIN_VISUAL_APPROVAL.png
ii .\STAS5_ML_CORE\artifacts\v4\review_navigation\20260714_artifact_inventory\CONTACT_SHEET_20260515_20260525_FORWARD_SOURCE.png
ii .\STAS5_ML_CORE\artifacts\v4\review_navigation\20260714_artifact_inventory\CONTACT_SHEET_20260515_20260525_V4_GROUP_BLOCKS.png
```

Открыть индекс:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\review_navigation\20260714_artifact_inventory\STAS5_SCREENSHOT_INDEX_20260501_20260525.csv
ii .\STAS5_ML_CORE\artifacts\v4\review_navigation\20260714_artifact_inventory\README_RU.md
```

Граница: это команды просмотра. Не запускать V4 train, group feature builder, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Unified Forward Review Ledger 2026-05-15..2026-05-25

Статус: `STAS5_V4_FORWARD_REVIEW_20260515_20260525_DRAFT_NO_TRAINING`.

Открыть отчет:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515_20260525\STAS5_V4_GROUP_RANK_REVIEW_20260515_20260525_FORWARD_REVIEW_V1_RU.md
```

Проверить единый ledger:

```powershell
@'
import json
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv"
df = pd.read_csv(p)
print("rows", len(df))
print("days", df["day"].min(), df["day"].max(), df["day"].nunique())
print(df["label_status"].value_counts().to_dict())
print(df["rank_label"].value_counts().to_dict())
print("winners", int(df["is_group_winner"].astype(int).sum()))
g = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1_GUARD.json"
print(json.load(open(g, encoding="utf-8"))["status"])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `738` строк, `11` дней, все `label_status=DRAFT`, `BEST_GOOD=62`, winners `62`, guard `PASS`.

Граница: это review-ledger, не обучение. Не запускать V4 train, threshold tuning, Optuna, API, TP/Stas3/exit до group features и финального guard.

## STAS5 V4 Approved Group Ledger 2026-05-15

Статус: `STAS5_V4_20260515_APPROVED_V1_NO_TRAINING`.

Открыть approved-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515\STAS5_V4_GROUP_RANK_REVIEW_20260515_APPROVED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515\STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_ANNOTATED.png
```

Проверить approved CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_APPROVED_V1.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["label_status"].value_counts())
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"].astype(int) == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `41` строка, все `label_status=APPROVED`, `BAD_IN_GROUP=26`, `NO_TRADE_GROUP=6`, `BEST_GOOD=5`, `GOOD_ALT=4`; winners `LA007`, `LA021`, `LA024`, `LA054`, `LA061`.

Граница: approved ledger не означает запуск V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Draft Group Review 2026-05-25

Статус: `STAS5_V4_20260525_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260525\STAS5_V4_GROUP_RANK_REVIEW_20260525_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260525\STAS5_V4_GROUP_RANK_REVIEW_20260525_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260525/STAS5_V4_GROUP_RANK_LEDGER_20260525_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"].astype(int) == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `68` строк, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=19`, `BEST_GOOD=5`, `GOOD_ALT=4`; winners `LA014`, `LA020`, `LA038`, `LA059`, `LA066`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Draft Group Review 2026-05-24

Статус: `STAS5_V4_20260524_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260524\STAS5_V4_GROUP_RANK_REVIEW_20260524_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260524\STAS5_V4_GROUP_RANK_REVIEW_20260524_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260524/STAS5_V4_GROUP_RANK_LEDGER_20260524_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"].astype(int) == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `70` строк, `BAD_IN_GROUP=54`, `NO_TRADE_GROUP=6`, `GOOD_ALT=5`, `BEST_GOOD=5`; winners `LA009`, `LA015`, `LA024`, `LA042`, `LA065`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Draft Group Review 2026-05-23

Статус: `STAS5_V4_20260523_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260523\STAS5_V4_GROUP_RANK_REVIEW_20260523_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260523\STAS5_V4_GROUP_RANK_REVIEW_20260523_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260523/STAS5_V4_GROUP_RANK_LEDGER_20260523_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"].astype(int) == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `63` строки, `BAD_IN_GROUP=41`, `NO_TRADE_GROUP=12`, `GOOD_ALT=5`, `BEST_GOOD=5`; winners `LA007`, `LA022`, `LA033`, `LA036`, `LA051`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Draft Group Review 2026-05-22

Статус: `STAS5_V4_20260522_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260522\STAS5_V4_GROUP_RANK_REVIEW_20260522_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260522\STAS5_V4_GROUP_RANK_REVIEW_20260522_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260522/STAS5_V4_GROUP_RANK_LEDGER_20260522_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"].astype(int) == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `75` строк, `BAD_IN_GROUP=55`, `NO_TRADE_GROUP=11`, `BEST_GOOD=5`, `GOOD_ALT=4`; winners `LA007`, `LA022`, `LA036`, `LA047`, `LA061`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Draft Group Review 2026-05-21

Статус: `STAS5_V4_20260521_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260521\STAS5_V4_GROUP_RANK_REVIEW_20260521_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260521\STAS5_V4_GROUP_RANK_REVIEW_20260521_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260521/STAS5_V4_GROUP_RANK_LEDGER_20260521_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"].astype(int) == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `81` строка, `BAD_IN_GROUP=56`, `NO_TRADE_GROUP=15`, `GOOD_ALT=5`, `BEST_GOOD=5`; winners `LA006`, `LA019`, `LA045`, `LA059`, `LA066`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Draft Group Review 2026-05-20

Статус: `STAS5_V4_20260520_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260520\STAS5_V4_GROUP_RANK_REVIEW_20260520_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260520\STAS5_V4_GROUP_RANK_REVIEW_20260520_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260520/STAS5_V4_GROUP_RANK_LEDGER_20260520_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"].astype(int) == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `68` строк, `NO_TRADE_GROUP=31`, `BAD_IN_GROUP=28`, `BEST_GOOD=5`, `GOOD_ALT=4`; winners `LA011`, `LA037`, `LA045`, `LA053`, `LA057`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Draft Group Review 2026-05-19

Статус: `STAS5_V4_20260519_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260519\STAS5_V4_GROUP_RANK_REVIEW_20260519_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260519\STAS5_V4_GROUP_RANK_REVIEW_20260519_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260519/STAS5_V4_GROUP_RANK_LEDGER_20260519_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"] == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `65` строк, `BAD_IN_GROUP=40`, `NO_TRADE_GROUP=17`, `BEST_GOOD=5`, `GOOD_ALT=3`; winners `LA005`, `LA016`, `LA032`, `LA042`, `LA063`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Draft Group Review 2026-05-18

Статус: `SUPERSEDED_BY_20260518_USER_CORRECTED_V1_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260518\STAS5_V4_GROUP_RANK_REVIEW_20260518_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260518\STAS5_V4_GROUP_RANK_REVIEW_20260518_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260518/STAS5_V4_GROUP_RANK_LEDGER_20260518_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"] == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание для старого draft: `73` строки, `BAD_IN_GROUP=51`, `NO_TRADE_GROUP=11`, `GOOD_ALT=6`, `BEST_GOOD=5`; winners `LA006`, `LA019`, `LA034`, `LA049`, `LA061`. Этот draft superseded: актуальная проверка выше использует `USER_CORRECTED_V1`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Draft Group Review 2026-05-17

Статус: `STAS5_V4_20260517_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260517\STAS5_V4_GROUP_RANK_REVIEW_20260517_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260517\STAS5_V4_GROUP_RANK_REVIEW_20260517_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260517/STAS5_V4_GROUP_RANK_LEDGER_20260517_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"] == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `63` строки, `NO_TRADE_GROUP=30`, `BAD_IN_GROUP=25`, `BEST_GOOD=5`, `GOOD_ALT=3`; winners `LA004`, `LA006`, `LA036`, `LA046`, `LA063`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Review Encoding Check

Статус: `STAS5_V4_REVIEW_ENCODING_FIX_DONE`.

Проверить V4 review Markdown на кракозябры:

```powershell
@'
from pathlib import Path
root = Path(r"STAS5_ML_CORE/artifacts/v4/group_rank_review")
problems = []
for p in sorted(root.rglob("*.md")):
    s = p.read_text(encoding="utf-8", errors="replace")
    q = s.count("?" * 4)
    repl = s.count("\ufffd")
    cjk = sum(1 for ch in s if ("\u3000" <= ch <= "\u9fff") or ("\uf900" <= ch <= "\ufaff"))
    if q or repl or cjk:
        problems.append((str(p), q, repl, cjk))
print("checked_md", len(list(root.rglob("*.md"))))
print("problems", len(problems))
for item in problems:
    print(item)
'@ | python -
```

## STAS5 V4 Draft Group Review 2026-05-16

Статус: `STAS5_V4_20260516_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть draft-review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260516\STAS5_V4_GROUP_RANK_REVIEW_20260516_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260516\STAS5_V4_GROUP_RANK_REVIEW_20260516_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260516/STAS5_V4_GROUP_RANK_LEDGER_20260516_DRAFT.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"] == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `71` строка, `NO_TRADE_GROUP=38`, `BAD_IN_GROUP=27`, `BEST_GOOD=5`, `GOOD_ALT=1`; winners `LA016`, `LA027`, `LA038`, `LA041`, `LA049`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 User-Corrected Group Review 2026-05-15

Статус: `SUPERSEDED_BY_20260515_APPROVED_V1_NO_TRAINING`.

Открыть актуальный user-corrected review:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515\STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515\STAS5_V4_GROUP_RANK_REVIEW_20260515_USER_CORRECTED_V1_ANNOTATED.png
```

Проверить актуальный draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_USER_CORRECTED_V1.csv"
df = pd.read_csv(p)
print("rows", len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"] == 1][["group_id", "candidate_id", "primary_reason_code", "secondary_reason_codes"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `41` строка, `BAD_IN_GROUP=26`, `NO_TRADE_GROUP=6`, `BEST_GOOD=5`, `GOOD_ALT=4`; winners `LA007`, `LA021`, `LA024`, `LA054`, `LA061`.

Граница: это `DRAFT`, не approved train ledger. Не запускать V4 training, threshold tuning, Optuna, API, TP/Stas3/exit.

## STAS5 V4 Human-Style Group Ranker 2026-07-14

Статус: `STAS5_V4_20260515_SCREENSHOT_GROUP_REVIEW_DRAFT_NO_TRAINING`.

Открыть V4 ТЗ:

```powershell
ii .\STAS5_ML_CORE\07_STAS5_V4_HUMAN_STYLE_GROUP_RANKER_TZ_RU.md
```

Открыть V4 папку:

```powershell
ii .\STAS5_ML_CORE\v4
```

Проверить наличие схемы будущего group ledger:

```powershell
Test-Path .\STAS5_ML_CORE\schemas\STAS5_V4_GROUP_RANK_LEDGER.schema.json
```

Текущая граница: команды V4 пока только документальные. Не запускать обучение, threshold tuning, Optuna, API, TP/Stas3/exit. Первый рабочий runtime-шаг должен быть отдельным созданием/проверкой `STAS5_V4_GROUP_RANK_LEDGER.csv`, а не train.

Открыть draft-review по пользовательскому скриншоту `2026-05-15`:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515\STAS5_V4_GROUP_RANK_REVIEW_20260515_DRAFT_RU.md
ii .\STAS5_ML_CORE\artifacts\v4\group_rank_review\20260515\STAS5_V4_GROUP_RANK_REVIEW_20260515_ANNOTATED_DRAFT.png
```

Проверить draft CSV:

```powershell
$env:PYTHONPATH='src'
@'
import pandas as pd
p = "STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515/STAS5_V4_GROUP_RANK_LEDGER_20260515_SCREENSHOT_DRAFT.csv"
df = pd.read_csv(p)
print(len(df))
print(df["rank_label"].value_counts())
print(df[df["is_group_winner"] == 1][["group_id", "candidate_id", "primary_reason_code"]])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `41` строка, winners `LA004`, `LA007`, `LA021`, `LA054`, `LA061`. Это `DRAFT`, не approved train ledger.

## STAS5 V3 Review Train + Forward 21-25 2026-07-14

Статус: `STAS5_V3_REVIEW_TRAIN_FORWARD_21_25_READY`.

Одна команда: собрать V3 ledger, V3 dataset, guard, обучить `full_v2_all_274` и построить blind-forward графики `2026-05-21..2026-05-25`:

```powershell
cd C:\Users\007\Desktop\MLbotNav
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\STAS5_ML_CORE\run_stas5_v3_review_train_forward_21_25.ps1
```

Без открытия папки:

```powershell
.\STAS5_ML_CORE\run_stas5_v3_review_train_forward_21_25.ps1 -NoOpen
```

С ручным run id:

```powershell
.\STAS5_ML_CORE\run_stas5_v3_review_train_forward_21_25.ps1 -RunId stas5_v3_manual_01
```

Источник review-разметки `16..20` по умолчанию зафиксирован на root V2 forward CSV, который совпадает с пользовательскими скриншотами:

```powershell
.\STAS5_ML_CORE\run_stas5_v3_review_train_forward_21_25.ps1 -ReviewForwardPredictionsPath STAS5_ML_CORE\artifacts\v2\forward\STAS5_V2_FORWARD_ALL_PREDICTIONS_20260515_20260520.csv
```

Проверенный run:

```text
STAS5_ML_CORE/artifacts/v3/forward/runs/stas5_v3_wrapper_smoke2_20260714/
```

Открыть проверенный run:

```powershell
ii .\STAS5_ML_CORE\artifacts\v3\forward\runs\stas5_v3_wrapper_smoke2_20260714
```

Ожидание: `5/5` days READY, `feature_count=274`, guard `PASS`.

## STAS5 V2 Full274 Latest Run Check 2026-07-13

Статус: `STAS5_V2_FULL274_RUN_CHECK_PASS_TECHNICAL_REVIEW_REQUIRED`.

Открыть последний full274 forward run:

```powershell
ii .\STAS5_ML_CORE\artifacts\v2\forward\runs\stas5_v2_full274_20260713_203703
```

Открыть отчет проверки:

```powershell
ii .\STAS5_ML_CORE\artifacts\v2_audit\STAS5_V2_FULL274_RUN_CHECK_20260713_203703_RU.md
```

## STAS5 V2 Full 274 Train + Forward 2026-07-13

Статус: `STAS5_V2_FULL_274_WRAPPER_READY`.

Одна команда: пересобрать V2-признаки, проверить guard/audit, обучить модель на `full_v2_all_274` и построить blind-forward графики `2026-05-15..2026-05-20`:

```powershell
cd C:\Users\007\Desktop\MLbotNav
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\STAS5_ML_CORE\run_stas5_v2_full_274_train_forward.ps1
```

Результат будет в новой папке:

```text
STAS5_ML_CORE/artifacts/v2/model/runs/stas5_v2_full274_YYYYMMDD_HHMMSS/
STAS5_ML_CORE/artifacts/v2/forward/runs/stas5_v2_full274_YYYYMMDD_HHMMSS/
```

Запуск без автоматического открытия папки:

```powershell
.\STAS5_ML_CORE\run_stas5_v2_full_274_train_forward.ps1 -NoOpen
```

Запуск с ручным именем run:

```powershell
.\STAS5_ML_CORE\run_stas5_v2_full_274_train_forward.ps1 -RunId stas5_v2_full274_manual_01
```

Контроль после запуска:

```powershell
Get-Content -Encoding UTF8 .\STAS5_ML_CORE\artifacts\v2\model\STAS5_V2_LATEST_MODEL_RUN.json
Get-Content -Encoding UTF8 .\STAS5_ML_CORE\artifacts\v2\forward\STAS5_V2_LATEST_FORWARD_RUN.json
```

Ожидание: model manifest должен показать `model_feature_set=full_v2_all_274` и `feature_count=274`. Forward manifest должен показать тот же `model_feature_set`.

## STAS5 V2 Graph To Feature Audit 2026-07-13

Статус: `STAS5_V2_GRAPH_TO_FEATURE_AUDIT_READY`.

Открыть отчет:

```powershell
ii .\STAS5_ML_CORE\artifacts\v2_audit\STAS5_V2_GRAPH_TO_FEATURE_AUDIT_20260504_RU.md
```

Быстро перепроверить ключевой факт: full snapshot `274`, latest model `126`:

```powershell
@'
import json
from pathlib import Path
snap = json.loads(Path("STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.manifest.json").read_text(encoding="utf-8"))
latest = json.loads(Path("STAS5_ML_CORE/artifacts/v2/model/STAS5_V2_LATEST_MODEL_RUN.json").read_text(encoding="utf-8"))
model = json.loads(Path(latest["manifest_path"]).read_text(encoding="utf-8"))
print("snapshot_features", len(snap["feature_columns"]))
print("latest_model_feature_set", model["model_feature_set"])
print("latest_model_features", model["feature_count"])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `snapshot_features 274`, `latest_model_feature_set v1_plus_risk_gate`, `latest_model_features 126`.

## STAS5 V2 Train Visual Batch 2026-07-13

Статус: `STAS5_V2_TRAIN_VISUAL_BATCH_READY`.

Сгенерировать train-графики за все дни обучения:

```powershell
cd C:\Users\007\Desktop\MLbotNav
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_train_visual_batch --start-day 2026-05-01 --end-day 2026-05-14 --run-id stas5_v2_train_visual_YYYYMMDD_HHMMSS
```

Открыть текущий готовый batch:

```powershell
ii "C:\Users\007\Desktop\MLbotNav\STAS5_ML_CORE\artifacts\v2\visual_approval\runs\stas5_v2_train_visual_20260713_14d"
```

Открыть конкретный день:

```powershell
ii "C:\Users\007\Desktop\MLbotNav\STAS5_ML_CORE\artifacts\v2\visual_approval\runs\stas5_v2_train_visual_20260713_14d\20260501\STAS5_V2_FEATURE_VISUAL_APPROVAL_20260501.png"
```

## STAS5 V2 Isolated Train + Forward Run 2026-07-13

Статус: `STAS5_V2_RUN_ISOLATION_READY`.

Общая команда, чтобы каждый прогон был в отдельной папке:

```powershell
cd C:\Users\007\Desktop\MLbotNav
$env:PYTHONPATH='src'
$runId = 'stas5_v2_run_' + (Get-Date -Format 'yyyyMMdd_HHmmss')

.\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_entry_ranker_train --model-feature-set v1_plus_risk_gate --run-id $runId
.\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_forward_entry_review --run-id $runId

ii "C:\Users\007\Desktop\MLbotNav\STAS5_ML_CORE\artifacts\v2\forward\runs\$runId"
```

Результаты будут здесь:

```text
STAS5_ML_CORE/artifacts/v2/model/runs/<run_id>/
STAS5_ML_CORE/artifacts/v2/forward/runs/<run_id>/
```

Проверить последний run:

```powershell
Get-Content -Encoding UTF8 .\STAS5_ML_CORE\artifacts\v2\forward\STAS5_V2_LATEST_FORWARD_RUN.json
```

## STAS5 V2 Controlled Forward 2026-07-13

Статус: `STAS5_V2_CONTROLLED_FORWARD_READY`.

Проверить новые модули:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v2_entry_ranker_train.py src\mlbotnav\stas5_v2_forward_entry_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v2_entry_ranker_train.py tests\test_stas5_v2_forward_entry_review.py -q
```

Обучить selected V2 model после ablation:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_entry_ranker_train --model-feature-set v1_plus_risk_gate
```

Построить blind-forward PNG:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_forward_entry_review
```

Финальная проверка:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_leakage_guard
$files = Get-ChildItem tests\test_stas5_*.py | % FullName; $env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest $files -q
```

Ожидание: leakage guard `PASS`, STAS5 tests `34 passed`.

Граница: forward не использовать для threshold tuning; TP/Stas3/API/Optuna не запускать.

## STAS5 V2 Numeric Coverage 2026-07-13

Статус: `STAS5_V2_NUMERIC_COVERAGE_READY`.

Проверить измененные файлы:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_common.py src\mlbotnav\stas5_v2_combo_feature_exporter.py src\mlbotnav\stas5_v2_pre_ml_audit.py src\mlbotnav\stas5_v2_numeric_coverage_audit.py
```

Пересобрать train V2 combo features:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_combo_feature_exporter
```

Пересобрать forward V2 combo features:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_combo_feature_exporter --stas2-run-dir STAS5_ML_CORE\artifacts\forward_source\stas2_runs\stas5_forward_stas2_20260515_20260520_20260710_163714 --start-day 2026-05-15 --end-day 2026-05-20 --output-csv STAS5_ML_CORE\artifacts\v2\features\stas5_v2_combo_features_20260515_20260520_forward_v0.csv --manifest-path STAS5_ML_CORE\artifacts\v2\features\stas5_v2_combo_features_20260515_20260520_forward_v0.manifest.json
```

Пересобрать snapshot, guard, ledger, audit:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_feature_snapshot_builder
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_leakage_guard
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_forward_error_ledger
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_pre_ml_audit
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_numeric_coverage_audit --day 2026-05-04
```

Проверить тесты:

```powershell
$files = Get-ChildItem tests\test_stas5_v2_*.py | % FullName; $env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest $files -q
$files = Get-ChildItem tests\test_stas5_*.py | % FullName; $env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest $files -q
```

Ожидание: V2 tests `23 passed`; full STAS5 tests `30 passed`.

Граница: эти команды не запускают final training, threshold tuning, Optuna/scorer/target-lock/API/Stas3/TP.

## STAS5 V2 Strategy Audit Strip 2026-07-13

Статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_WITH_STRATEGY_AUDIT_READY_WAIT_USER`.

Проверить код и тест:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v2_feature_visual_approval.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v2_feature_visual_approval.py -q
```

Пересобрать график:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_feature_visual_approval --day 2026-05-04
```

Проверить strategy audit counts:

```powershell
@'
import json
from pathlib import Path
p = Path("STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.manifest.json")
m = json.loads(p.read_text(encoding="utf-8"))
print(m["strategy_audit_counts"])
'@ | .\.venv\Scripts\python.exe -
```

Ожидание: `density_profile+structure_ta X=22/UP=2`, `pattern+structure_ta X=38/UP=1`, `structure_ta+volume_flow X=52/UP=1`, `structure_ta+trend_momentum X=59/UP=4`.

Граница: это только visual approval. Не запускать ablation/training/threshold/Optuna/API/Stas3/TP до пользовательского подтверждения.

## STAS5 V2 Feature Visual Approval 2026-07-13

Статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_READY_WAIT_USER`.

Проверить код и тест:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v2_feature_visual_approval.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v2_feature_visual_approval.py -q
```

Пересобрать approval PNG за `2026-05-04`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_feature_visual_approval --day 2026-05-04
```

Открыть результат:

```powershell
ii .\STAS5_ML_CORE\artifacts\v2\visual_approval\20260504\STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png
```

Проверить manifest:

```powershell
@'
import json
from pathlib import Path
p = Path("STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.manifest.json")
m = json.loads(p.read_text(encoding="utf-8"))
print(m["status"], m["rows"])
print(m["label_counts"])
print(m["approval_bucket_counts"])
print(m["risk_bucket_counts"])
print(m["keep_ids"])
'@ | .\.venv\Scripts\python.exe -
```

Граница: команда делает только visual approval graph. Не запускать ablation/training/threshold/Optuna/API/Stas3/TP до пользовательского подтверждения.

## STAS5 V2 Pre-ML Audit 2026-07-13

Статус: `STAS5_V2_PRE_ML_AUDIT_READY`.

Проверить код и тесты:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v2_pre_ml_audit.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v2_pre_ml_audit.py -q
```

Пересобрать V2 pre-ML audit:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_pre_ml_audit
```

Ожидаемый результат:

```text
status READY_FOR_V2_ABLATION_BASELINE
feature_count 214
KEEP_DRAFT 115
CUT_DRAFT 857
KEEP_DRAFT + yellow_x 30
bad green 55
missed good SKIP 65
```

Открыть отчет:

```powershell
ii .\STAS5_ML_CORE\artifacts\v2_audit\STAS5_V2_PRE_ML_AUDIT_20260501_20260520_RU.md
```

Граница: это audit-only отчет. Не запускать production training, threshold tuning по forward `15+`, Optuna/scorer/target-lock/API/Stas3/TP.

## STAS5 V2 Forward Error Ledger 2026-07-13

Статус: `STAS5_V2_FORWARD_ERROR_LEDGER_READY`.

Проверить код и тесты:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v2_forward_error_ledger.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v2_forward_error_ledger.py -q
```

Пересобрать forward error ledger:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_forward_error_ledger
```

Ожидаемый результат:

```text
status PASS
rows 435
decision_counts_v1 ENTER=103 SKIP=277 UNSURE=55
GREEN_BAD_FALLING_KNIFE=46
GREEN_BAD_NO_REVERSAL=9
SKIP_MISSED_GOOD=65
```

Проверить manifest:

```powershell
@'
import json
from pathlib import Path
p = Path("STAS5_ML_CORE/artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.manifest.json")
m = json.loads(p.read_text(encoding="utf-8"))
print(m["status"], m["rows"])
print(m["decision_counts_v1"])
print(m["error_class_counts"])
print(m["v2_expected_decision_counts"])
'@ | .\.venv\Scripts\python.exe -
```

Граница: это audit-only ledger. Не использовать postfact/user-review поля как features, train labels или threshold tuning. Следующий пункт по ТЗ - V2 pre-ML audit.

## STAS5 V2 Leakage Guard 2026-07-13

Статус: `STAS5_V2_LEAKAGE_GUARD_READY`.

Проверить код и тесты:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v2_leakage_guard.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v2_leakage_guard.py -q
```

Запустить V2 leakage guard на train snapshot:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_leakage_guard
```

Ожидаемый результат:

```text
status PASS
rows 972
feature_count 214
forbidden_feature_columns {}
label_columns_in_features []
metadata_columns_in_features []
v2_combo_feature_time_not_before_entry 0
forward_days_present 0
KEEP_DRAFT + yellow_x 30
```

Проверить report:

```powershell
@'
import json
from pathlib import Path
p = Path("STAS5_ML_CORE/artifacts/v2/guard/stas5_v2_leakage_guard_20260501_20260514_v0.json")
r = json.loads(p.read_text(encoding="utf-8"))
print(r["status"], r["rows"], r["feature_count"])
print(r["checks"])
'@ | .\.venv\Scripts\python.exe -
```

Граница: guard не является разрешением на обучение. Следующий шаг по ТЗ - `stas5_v2_forward_error_ledger.py`, затем V2 pre-ML audit. Не запускать V2 training, threshold tuning, Optuna/scorer/target-lock/API/Stas3/TP.

## STAS5 V2 Feature Snapshot 2026-07-13

Статус: `STAS5_V2_FEATURE_SNAPSHOT_READY`.

Проверить код и тесты:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v2_feature_snapshot_builder.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v2_feature_snapshot_builder.py -q
```

Пересобрать V2 train snapshot:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_feature_snapshot_builder
```

Ожидаемый результат:

```text
status PASS
rows 972
feature_count 214
v1_feature_count 111
v2_feature_count 103
lost_after_combo_join 0
KEEP_DRAFT + yellow_x 30
```

Проверить manifest:

```powershell
@'
import json
from pathlib import Path
p = Path("STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.manifest.json")
m = json.loads(p.read_text(encoding="utf-8"))
print({k: m[k] for k in ["status", "rows", "feature_count", "v1_feature_count", "v2_feature_count"]})
print(m["checks"])
'@ | .\.venv\Scripts\python.exe -
```

Граница: это только сбор train snapshot `2026-05-01..2026-05-14`. Не запускать обучение, forward threshold, Optuna/scorer/target-lock/API/Stas3/TP.

## STAS5 V2 Forward User Review 2026-07-13

Статус: `STAS5_V2_FORWARD_USER_REVIEW_READY`.

Пересобрать крупные review-страницы за `2026-05-15`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_forward_user_review --day 2026-05-15 --window-hours 3
```

Ожидаемый результат:

```text
PASS 90 STAS5_ML_CORE/artifacts/v2/user_review/20260515
```

Открыть ключевые страницы:

```powershell
ii .\STAS5_ML_CORE\artifacts\v2\user_review\20260515\STAS5_V2_USER_REVIEW_20260515_FULL.png
ii .\STAS5_ML_CORE\artifacts\v2\user_review\20260515\STAS5_V2_USER_REVIEW_20260515_PAGE_01_0000_0300.png
ii .\STAS5_ML_CORE\artifacts\v2\user_review\20260515\STAS5_V2_USER_REVIEW_20260515_PAGE_02_0300_0600.png
ii .\STAS5_ML_CORE\artifacts\v2\user_review\20260515\STAS5_V2_USER_REVIEW_20260515_PAGE_05_1200_1500.png
ii .\STAS5_ML_CORE\artifacts\v2\user_review\20260515\STAS5_V2_USER_REVIEW_TEMPLATE_20260515.csv
```

Граница: это визуальный forward audit для выбора пользовательских `LAxxx`. Не использовать `2026-05-15` для обучения, threshold tuning или финального trading permission.

## STAS5 V2 Combo Feature Exporter 2026-07-13

Статус: `STAS5_V2_COMBO_FEATURE_EXPORT_READY`.

Проверить код и тесты:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_v2_combo_feature_exporter.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_v2_combo_feature_exporter.py -q
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_feature_snapshot_contract.py tests\test_stas5_forward_entry_review_contract.py tests\test_stas5_leakage_guard.py tests\test_stas5_ml_ledger_builder.py tests\test_stas5_v2_combo_feature_exporter.py -q
```

Пересобрать train V2 combo features:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_combo_feature_exporter
```

Ожидаемый результат:

```text
PASS 972 103 STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.csv
```

Пересобрать blind-forward V2 combo features:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_v2_combo_feature_exporter --stas2-run-dir STAS5_ML_CORE\artifacts\forward_source\stas2_runs\stas5_forward_stas2_20260515_20260520_20260710_163714 --start-day 2026-05-15 --end-day 2026-05-20 --output-csv STAS5_ML_CORE\artifacts\v2\features\stas5_v2_combo_features_20260515_20260520_forward_v0.csv --manifest-path STAS5_ML_CORE\artifacts\v2\features\stas5_v2_combo_features_20260515_20260520_forward_v0.manifest.json
```

Ожидаемый результат:

```text
PASS 435 103 STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.csv
```

Быстро проверить manifests:

```powershell
@'
import json
from pathlib import Path
for path in [
    Path("STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.manifest.json"),
    Path("STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.manifest.json"),
]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(path.as_posix(), payload["status"], payload["rows"], payload["feature_count"], payload["checks"])
'@ | .\.venv\Scripts\python.exe -
```

Граница: эти команды экспортируют только causal V2 feature-layer. Они не обучают финальную V2 модель, не запускают Optuna/scorer/target-lock/API/мост Bybit и не используют Stas3/TP/exit.

## STAS5 V1 Audit And V2 TZ 2026-07-13

Статус: `STAS5_V1_AUDITED_V2_CONTOUR2_TZ_READY`.

Открыть аудит и ТЗ V2:

```powershell
ii .\STAS5_ML_CORE\04_STAS5_V1_HARD_AUDIT_RU.md
ii .\STAS5_ML_CORE\05_STAS5_V2_CONTOUR2_TZ_RU.md
ii .\STAS5_ML_CORE\README_RU.md
```

Открыть найденный combo-spectrum слой:

```powershell
ii .\STAS4_FEATURE_HYPOTHESIS_REVIEW\density_structure_20260501_20260514_combo_spectrum\20260504\STAS4_density_profile+structure_ta_OVERLAY_COMBO_SPECTRUM_20260504_20260710_102322.png
ii .\STAS4_FEATURE_HYPOTHESIS_REVIEW\density_structure_20260501_20260514_combo_spectrum\SUMMARY_RU.md
```

Проверить, что combo/STAS4 не входил в v1 model features:

```powershell
rg -n "\"feature_columns\"|combo|stoch|atr|divergence|density|structure" .\STAS5_ML_CORE\artifacts\features\stas5_feature_snapshot_20260501_20260514_v0.manifest.json .\STAS5_ML_CORE\artifacts\model\stas5_entry_ranker_20260501_20260514_v0.manifest.json
```

Граница: эти команды только открывают/проверяют аудит. Не запускать новое обучение, Optuna, scorer, target-lock, API/мост Bybit или Stas3/TP.

## STAS5 Entry ML Pipeline Ready 2026-07-10

Статус: `STAS5_ENTRY_ML_PIPELINE_READY_TRAIN_1_14_FORWARD_15_20_NO_OPTUNA_NO_API_NO_STAS3`.

Открыть главный source-of-truth и свежие артефакты:

```powershell
ii .\STAS5_ML_CORE\README_RU.md
ii .\STAS5_ML_CORE\03_STAS5_CURRENT_EXECUTION_INSTRUCTION_RU.md
ii .\STAS5_ML_CORE\artifacts\audit\STAS5_PRE_ML_AUDIT_20260501_20260514_RU.md
ii .\STAS5_ML_CORE\artifacts\forward
```

Проверить код STAS5:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\stas5_common.py src\mlbotnav\stas5_ml_ledger_builder.py src\mlbotnav\stas5_feature_snapshot_builder.py src\mlbotnav\stas5_leakage_guard.py src\mlbotnav\stas5_pre_ml_audit.py src\mlbotnav\stas5_entry_ranker_train.py src\mlbotnav\stas5_forward_entry_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_stas5_*.py -q
```

Пересобрать train-часть `2026-05-01..2026-05-14`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_ml_ledger_builder
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_feature_snapshot_builder
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_leakage_guard
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_pre_ml_audit
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_entry_ranker_train
```

Пересобрать blind-forward review `2026-05-15..2026-05-20`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.stas5_forward_entry_review --start-day 2026-05-15 --end-day 2026-05-20
```

Ожидаемые контрольные факты: ledger `972` rows, `115 KEEP_DRAFT`, `857 CUT_DRAFT`, `30 KEEP_DRAFT + yellow_x`; feature snapshot `111` model features; leakage guard `PASS`; audit `READY_FOR_CONTROLLED_BASELINE`; model `CONTROLLED_BASELINE_READY`; forward `FORWARD_ENTRY_REVIEW_READY`.

Граница: эти команды не используют Optuna, scorer, target-lock, API/мост Bybit и Stas3/TP/exit. Forward `2026-05-15+` не использовать для обучения, подбора threshold или ручной доводки.

## STAS5 Current Memory 2026-07-10

Статус: `STAS5_MEMORY_REFRESH_CURRENT_NEXT_NO_ML_NO_OPTUNA`.

Открыть текущую рабочую папку STAS-5:

```powershell
ii .\STAS5_ML_CORE
ii .\STAS5_ML_CORE\README_RU.md
ii .\STAS5_ML_CORE\03_STAS5_CURRENT_EXECUTION_INSTRUCTION_RU.md
```

Проверить состав папки:

```powershell
Get-ChildItem .\STAS5_ML_CORE -Recurse | Select-Object FullName,Length,LastWriteTime
```

Проверить, что в памяти зафиксирован текущий next step:

```powershell
rg -n "STAS5_CURRENT_EXECUTION_INSTRUCTION|STAS5_MEMORY_REFRESH_CURRENT_NEXT|MEMORY_REFRESH_2026_07_10|ML-ledger|pre-entry feature snapshot|KEEP \+ yellow_x" STAS5_ML_CORE docs\codex
```

Граница: эти команды только открывают и проверяют документы. ML/export/training, Optuna, scorer, target-lock, API и мост Bybit не запускать.

## STAS4 Root Path Check 2026-07-10

Статус: `STAS4_ROOT_HOME_READY_NO_ML_NO_OPTUNA`.

Проверить, что STAS4 находится в корне:

```powershell
Get-ChildItem -LiteralPath . -Directory | Where-Object { $_.Name -like 'STAS*' } | Select-Object Name,FullName
```

Проверить главную ручную разметку:

```powershell
Test-Path .\STAS4_FEATURE_HYPOTHESIS_REVIEW\density_structure_20260501_20260514_combo_spectrum\manual_labels\YELLOW_X_AUDIT_ONLY_RULE_RU.md
```

Проверить, что в коде и STAS5 нет старого рабочего пути:

```powershell
rg -n "reports/final_review/stas4_feature_hypothesis_screen_v0|reports\\final_review\\stas4_feature_hypothesis_screen_v0" src scripts STAS5_ML_CORE
```

Граница: команды только проверяют структуру и ссылки. Они не запускают ML/export/training, Optuna, scorer, target-lock или API.

## STAS5 ML Core Docs 2026-07-10

Статус: `STAS5_ML_ENTRY_ARCHITECTURE_DRAFT_NO_ML_NO_OPTUNA`.

Открыть source-of-truth STAS-5:

```powershell
ii .\STAS5_ML_CORE\README_RU.md
ii .\STAS5_ML_CORE\01_STAS5_ML_ENTRY_ARCHITECTURE_RU.md
ii .\STAS5_ML_CORE\02_ML_LEDGER_AND_FEATURE_CONTRACT_RU.md
```

Проверить, что STAS-5 docs лежат отдельно и не являются run-артефактами:

```powershell
Get-ChildItem .\STAS5_ML_CORE -Recurse | Select-Object FullName,Length,LastWriteTime
```

Граница: эти команды только открывают/проверяют документы. ML/export/training, Optuna, scorer, target-lock и API не запускать.

## Yellow X Audit Only Check 2026-07-10

Статус: `YELLOW_X_AUDIT_ONLY_FIXED_RULE_NO_ML_NO_OPTUNA`.

Проверить, сколько пользовательских KEEP имеют yellow X:

```powershell
@'
from pathlib import Path
import csv
base = Path(r'STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels')
keep_total = yellow_keep = total = yellow_total = 0
conflicts = []
for day in ['20260501','20260502','20260503','20260504','20260505','20260506','20260507','20260508','20260509','20260510','20260511','20260512','20260513','20260514']:
    rows = list(csv.DictReader((base / f'LABELS_{day}_ALL_ENTRIES_DRAFT.csv').open('r', encoding='utf-8-sig', newline='')))
    for r in rows:
        total += 1
        is_yellow = r.get('stas4_density_structure_yellow_x') == '1'
        if is_yellow:
            yellow_total += 1
        if r['human_label'] == 'KEEP_DRAFT':
            keep_total += 1
            if is_yellow:
                yellow_keep += 1
                conflicts.append((day, r['candidate_id']))
print({'total': total, 'keep_total': keep_total, 'yellow_total': yellow_total, 'yellow_keep': yellow_keep})
print(conflicts)
'@ | .\.venv\Scripts\python.exe -
```

Ожидаемый результат: `{'total': 972, 'keep_total': 115, 'yellow_total': 287, 'yellow_keep': 30}`.

Граница: команда только читает ручные CSV и не запускает ML/export/training, Optuna, scorer, target-lock или API.

## STAS4 Manual Labels Draft 2026-07-10 20260501-20260514

Статус: `STAS4_MANUAL_LABELS_20260501_20260514_DRAFT_COMPLETE_NO_ML_NO_OPTUNA`.

Проверить текущие draft-метки:

```powershell
@'
from pathlib import Path
import csv
base = Path(r'STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels')
total = keep_total = cut_total = 0
days = ['20260501','20260502','20260503','20260504','20260505','20260506','20260507','20260508','20260509','20260510','20260511','20260512','20260513','20260514']
for day in days:
    rows = list(csv.DictReader((base / f'LABELS_{day}_ALL_ENTRIES_DRAFT.csv').open('r', encoding='utf-8-sig', newline='')))
    keep = sum(1 for r in rows if r['human_label'] == 'KEEP_DRAFT')
    cut = sum(1 for r in rows if r['human_label'] == 'CUT_DRAFT')
    total += len(rows); keep_total += keep; cut_total += cut
    print(day, {'total': len(rows), 'keep': keep, 'cut': cut})
print('TOTAL', {'total': total, 'keep': keep_total, 'cut': cut_total})
'@ | .\.venv\Scripts\python.exe -
```

Ожидаемый итог: `TOTAL {'total': 972, 'keep': 115, 'cut': 857}`.

Открыть последний проверочный скрин:

```powershell
ii .\STAS4_FEATURE_HYPOTHESIS_REVIEW\density_structure_20260501_20260514_combo_spectrum\manual_labels\ANNOTATED_20260514_KEEP_DRAFT.png
```

Граница: эти команды только проверяют CSV/PNG ручной разметки. Они не запускают ML, Optuna, scorer, target-lock или API.

## STAS4 Manual Labels Draft 2026-07-10 20260501-20260513

Статус: `STAS4_MANUAL_LABELS_20260501_20260513_DRAFT_NO_ML_NO_OPTUNA`.

Проверить текущие draft-метки:

```powershell
@'
from pathlib import Path
import csv
base = Path(r'STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels')
total = keep_total = cut_total = 0
for day in ['20260501','20260502','20260503','20260504','20260505','20260506','20260507','20260508','20260509','20260510','20260511','20260512','20260513']:
    rows = list(csv.DictReader((base / f'LABELS_{day}_ALL_ENTRIES_DRAFT.csv').open('r', encoding='utf-8-sig', newline='')))
    keep = sum(1 for r in rows if r['human_label'] == 'KEEP_DRAFT')
    cut = sum(1 for r in rows if r['human_label'] == 'CUT_DRAFT')
    total += len(rows); keep_total += keep; cut_total += cut
    print(day, {'total': len(rows), 'keep': keep, 'cut': cut})
print('TOTAL', {'total': total, 'keep': keep_total, 'cut': cut_total})
'@ | .\.venv\Scripts\python.exe -
```

Открыть последний проверочный скрин:

```powershell
ii .\STAS4_FEATURE_HYPOTHESIS_REVIEW\density_structure_20260501_20260514_combo_spectrum\manual_labels\ANNOTATED_20260513_KEEP_DRAFT.png
```

Граница: эти команды только проверяют CSV/PNG ручной разметки. Они не запускают ML, Optuna, scorer, target-lock или API.

## STAS4 Manual Labels Draft 2026-07-10 20260501-20260512

Статус: `STAS4_MANUAL_LABELS_20260501_20260512_DRAFT_NO_ML_NO_OPTUNA`.

Проверить текущие draft-метки:

```powershell
@'
from pathlib import Path
import csv
base = Path(r'STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels')
total = keep_total = cut_total = 0
for day in ['20260501','20260502','20260503','20260504','20260505','20260506','20260507','20260508','20260509','20260510','20260511','20260512']:
    rows = list(csv.DictReader((base / f'LABELS_{day}_ALL_ENTRIES_DRAFT.csv').open('r', encoding='utf-8-sig', newline='')))
    keep = sum(1 for r in rows if r['human_label'] == 'KEEP_DRAFT')
    cut = sum(1 for r in rows if r['human_label'] == 'CUT_DRAFT')
    total += len(rows); keep_total += keep; cut_total += cut
    print(day, {'total': len(rows), 'keep': keep, 'cut': cut})
print('TOTAL', {'total': total, 'keep': keep_total, 'cut': cut_total})
'@ | .\.venv\Scripts\python.exe -
```

Открыть последний проверочный скрин:

```powershell
ii .\STAS4_FEATURE_HYPOTHESIS_REVIEW\density_structure_20260501_20260514_combo_spectrum\manual_labels\ANNOTATED_20260512_KEEP_DRAFT.png
```

Граница: эти команды только проверяют CSV/PNG ручной разметки. Они не запускают ML, Optuna, scorer, target-lock или API.

## STAS4 Manual Labels Draft 2026-07-10

Статус: `STAS4_MANUAL_LABELS_20260501_20260511_DRAFT_NO_ML_NO_OPTUNA`.

Проверить текущие draft-метки:

```powershell
@'
from pathlib import Path
import csv
base = Path(r'STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels')
for day in ['20260501','20260502','20260503','20260504','20260505','20260506','20260507','20260508','20260509','20260510','20260511']:
    rows = list(csv.DictReader((base / f'LABELS_{day}_ALL_ENTRIES_DRAFT.csv').open('r', encoding='utf-8-sig', newline='')))
    keep = sum(1 for r in rows if r['human_label'] == 'KEEP_DRAFT')
    cut = sum(1 for r in rows if r['human_label'] == 'CUT_DRAFT')
    print(day, {'total': len(rows), 'keep': keep, 'cut': cut})
'@ | .\.venv\Scripts\python.exe -
```

Открыть последний проверочный скрин:

```powershell
ii .\STAS4_FEATURE_HYPOTHESIS_REVIEW\density_structure_20260501_20260514_combo_spectrum\manual_labels\ANNOTATED_20260511_KEEP_DRAFT.png
```

Граница: эти команды только проверяют CSV/PNG ручной разметки. Они не запускают ML, Optuna, scorer, target-lock или API.

## STAS2/STAS4 Compact Strips 2026-07-10

Статус: `STAS2_STAS4_COMPACT_STRIPS_READY_NO_LOGIC_CHANGE_NO_ML_NO_OPTUNA`.

Проверить код:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas2_market_phase_review.py src\mlbotnav\visual_entry_stas4_family_overlay.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas2_market_phase_review.py -q
```

Повторить smoke Stas2 на `2026-05-11`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_review --start-day 2026-05-11 --end-day 2026-05-11 --run-label stas2_20260511_visual_half_strips_smoke_v1 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260510_20260512_carry48_for_stas2_v0_20260709_070902 --render-limit 8
```

Повторить smoke Stas4 overlay:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas4_family_overlay --stas2-run-dir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260511_visual_half_strips_smoke_v1_20260710_073524 --day 2026-05-11 --family pattern+structure_ta --out-dir STAS4_FEATURE_HYPOTHESIS_REVIEW\visual_half_strips_smoke_v1
```

Открыть контрольные PNG:

```powershell
ii .\STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260511_visual_half_strips_smoke_v1_20260710_073524\STAS2_DAY_OVERVIEW_20260511.png
ii .\STAS4_FEATURE_HYPOTHESIS_REVIEW\visual_half_strips_smoke_v1\STAS4_pattern+structure_ta_OVERLAY_20260511_20260710_073654.png
```

## STAS3 V2 Clean Ready 2026-07-09

Статус: `STAS3_V2_CLEAN_READY_NO_OLD_STAS3_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

Открыть финальный clean V2:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open browse
.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open xlsx
.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open report
.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open entries
.\STAS3_PERCENT_LADDER_REVIEW\open_clean_v2_last_run.ps1 -Open medium
```

Финальный clean run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_clean_20260510_20260512_long_only_20260709_123622`

Повторить clean V2-прогон:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_clean_v2.ps1 -Day 2026-05-10 -EndDay 2026-05-12 -RunLabel stas3_v2_clean_20260510_20260512_long_only -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260510_20260512_continuous_wave_v2_20260709_081330 -HoldHours 48
```

Проверить clean V2:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas3_v2_clean_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas3_v2_clean_review.py -q
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas2_market_phase_review.py tests\test_visual_entry_low_anchor_suggester.py -q
```

Проверить контракт результата:

```powershell
@'
from pathlib import Path
import csv, json
from openpyxl import load_workbook
run = Path(r'STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_clean_20260510_20260512_long_only_20260709_123622')
payload = json.loads((run/'STAS3_V2_CLEAN_PAYLOAD.json').read_text(encoding='utf-8'))
context = list(csv.DictReader((run/'STAS3_V2_CLEAN_ENTRY_CONTEXT.csv').open('r',encoding='utf-8-sig',newline='')))
path = list(csv.DictReader((run/'STAS3_V2_CLEAN_TP_PATH.csv').open('r',encoding='utf-8-sig',newline='')))
decision = list(csv.DictReader((run/'STAS3_V2_CLEAN_TP_DECISION.csv').open('r',encoding='utf-8-sig',newline='')))
skipped = list(csv.DictReader((run/'STAS3_V2_CLEAN_SKIPPED_ROWS.csv').open('r',encoding='utf-8-sig',newline='')))
wb = load_workbook(run/'STAS3_V2_CLEAN_TABLES.xlsx', read_only=True)
pngs = list(run.rglob('*.png'))
empty = [p.as_posix() for p in pngs if p.stat().st_size <= 1024]
ladder = payload['percent_ladder']
print({
    'status': payload['status'],
    'summary': payload['summary'],
    'rows_match': len(context) == len(path) == len(decision) == 214,
    'skipped': len(skipped),
    'has_0p2': 0.2 in ladder,
    'ladder_first': ladder[:8],
    'ladder_last': ladder[-1],
    'entry_price_locked': all(abs(float(r['entry_price_for_calc']) - float(r['entry_price_5bps'])) < 1e-6 for r in context),
    'direction_scope': sorted(set(r['direction_scope'] for r in context)),
    'short_context_only': sorted(set(r['short_context_only_flag'] for r in context)),
    'sheets': wb.sheetnames,
    'png_count': len(pngs),
    'empty_png': len(empty),
})
'@ | .\.venv\Scripts\python.exe -
```

Граница: clean V2 не использует старый Stas3 как базу. Это LONG-only post-entry audit, не стратегия. `SHORT` только risk-context. `WAVE/GAP/continuous` только hindsight-review. `clean_review_tp_pct` не является live TP, scorer, target-lock или ML-label.

## STAS3 V2 Ready 2026-07-09

Статус: `INVALID_OLD_STAS3_BASE_DRAFT`.

Открыть финальный V2-результат:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open browse
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open tp
ii .\STAS3_PERCENT_LADDER_REVIEW\runs\stas3_v2_20260510_20260512_long_only_20260709_112925\STAS3_V2_REPORT_RU.md
```

Финальный run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925`

Источник Stas2:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`

Повторить V2-прогон:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-10 -EndDay 2026-05-12 -RunLabel stas3_v2_20260510_20260512_long_only -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260510_20260512_continuous_wave_v2_20260709_081330 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50
```

Проверить код и тесты Stas3 V2:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas3_percent_ladder_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas3_percent_ladder_review.py tests\test_visual_entry_low_anchor_suggester.py -q
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas2_market_phase_review.py -q
```

Проверить V2-контракт результата:

```powershell
@'
from pathlib import Path
import csv, json
from openpyxl import load_workbook

run = Path(r'STAS3_PERCENT_LADDER_REVIEW/runs/stas3_v2_20260510_20260512_long_only_20260709_112925')
payload = json.loads((run / 'STAS3_PAYLOAD.json').read_text(encoding='utf-8'))
audit = list(csv.DictReader((run / 'STAS3_V2_ENTRY_TP_AUDIT.csv').open('r', encoding='utf-8-sig', newline='')))
context = list(csv.DictReader((run / 'STAS3_V2_CONTEXT_BUNDLE.csv').open('r', encoding='utf-8-sig', newline='')))
skipped = list(csv.DictReader((run / 'STAS3_V2_SKIPPED_ROWS.csv').open('r', encoding='utf-8-sig', newline='')))
wb = load_workbook(run / 'STAS3_PERCENT_LADDER_TABLES.xlsx', read_only=True)
pngs = list(run.rglob('*.png'))
empty_png = [p.as_posix() for p in pngs if p.stat().st_size <= 1024]
ladder = payload['percent_ladder']
print({
    'status': payload['status'],
    'source_ok': payload['v2_contract']['source_stas2_run_required'].endswith('stas2_20260510_20260512_continuous_wave_v2_20260709_081330'),
    'row_count_parity_ok': payload['summary']['row_count_parity_ok'],
    'entry_rows': len(audit),
    'context_rows': len(context),
    'skipped_rows': len(skipped),
    'ladder_first': ladder[:8],
    'ladder_last': ladder[-1],
    'has_0p2': 0.2 in ladder,
    'has_20p0': 20.0 in ladder,
    'entry_price_locked': all(r['entry_price_for_calc'] == r['entry_price_5bps'] for r in audit),
    'direction_scope': sorted(set(r['direction_scope'] for r in audit)),
    'short_context_only': sorted(set(r['short_context_only_flag'] for r in audit)),
    'sheets': [s for s in wb.sheetnames if s.startswith('V2')],
    'png_count': len(pngs),
    'empty_png': len(empty_png),
})
'@ | .\.venv\Scripts\python.exe -
```

Граница: Stas3 V2 - только LONG post-entry audit. `SHORT` используется только как risk-context. `WAVE/GAP/continuous` - hindsight-review контекст. `MFE MAX` - диагностический факт, не TP/exit. ML/export/training, Optuna, scorer, target-lock и API не запускать без отдельного решения.

## STAS3 V2 Reset TZ 2026-07-09

Статус: `STAS3_V2_TZ_GRID_LONG_ONLY_UPDATED_NO_ML_NO_OPTUNA`.

Открыть новое ТЗ:

```powershell
ii .\STAS3_PERCENT_LADDER_REVIEW\TZ_STAS3_V2_RESET_RU.md
```

Проверить ключевые правки ТЗ:

```powershell
rg -n "entry_price_for_calc|entry_price_5bps|0\.3-0\.9|1\.0-2\.0|0\.1%|2\.0-20\.0|0\.2%|hit_20p0_rate|ideal_review_tp_pct|max_feasible_review_tp_pct|session_time_bucket|hour_background|hour_long_wave|hour_short_wave|short_context_only_flag|SHORT-risk|volume_context|2026-05-10|2026-05-11|2026-05-12|20260510_20260512_continuous_wave_v2" .\STAS3_PERCENT_LADDER_REVIEW\TZ_STAS3_V2_RESET_RU.md
```

Проверить контракт цены входа в выбранном Stas2 source:

```powershell
$run='.\STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260510_20260512_continuous_wave_v2_20260709_081330'
$rows=Import-Csv -Path (Join-Path $run 'STAS2_RECORDS.csv') -Encoding UTF8
[ordered]@{
  rows=$rows.Count
  missing_anchor_low=($rows|Where-Object { [string]::IsNullOrWhiteSpace($_.anchor_low_price)}).Count
  missing_entry_open=($rows|Where-Object { [string]::IsNullOrWhiteSpace($_.entry_open_price)}).Count
  missing_entry_5bps=($rows|Where-Object { [string]::IsNullOrWhiteSpace($_.entry_price_5bps)}).Count
  context_not_before=($rows|Where-Object { $_.context_before_entry_check -ne 'True'}).Count
} | ConvertTo-Json -Compress
```

Проверить, что старые Stas3 runs не удалены:

```powershell
Get-ChildItem .\STAS3_PERCENT_LADDER_REVIEW\runs -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 10 Name,LastWriteTime
```

## STAS3 Rebuild From Latest STAS2 2026-07-09

Статус: `STAS3_REBUILT_FROM_STAS2_SHORT_LABELS_V1_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

Повторить rebuild:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-08 -EndDay 2026-05-12 -RunLabel stas3_20260508_20260512_from_stas2_short_labels_v1 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260508_20260512_short_labels_v1_20260709_083138 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50
```

Открыть актуальный Stas3:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open browse
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open tp
```

Финальный run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260508_20260512_from_stas2_short_labels_v1_20260709_084730`

Проверка:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas3_percent_ladder_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas3_percent_ladder_review.py tests\test_visual_entry_low_anchor_suggester.py -q
```

## STAS2 Short Strong Wave Labels 2026-07-09

Статус: `STAS2_SHORT_STRONG_WAVE_LABEL_READY_NO_ML_NO_OPTUNA_VISUAL_ONLY`.

Повторить контрольный run `2026-05-08..2026-05-12`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_review --start-day 2026-05-08 --end-day 2026-05-12 --run-label stas2_20260508_20260512_short_labels_v1 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260510_20260512_carry48_for_stas2_v0_20260709_070902
```

Открыть `2026-05-12`:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-12
```

Финальный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138`

Проверка коротких сильных волн:

```powershell
@'
from pathlib import Path
import csv
run = Path(r'STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260508_20260512_short_labels_v1_20260709_083138')
with (run / 'STAS2_MACRO_WAVES.csv').open('r', encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
for r in rows:
    dur = float(r.get('macro_wave_duration_min') or 0)
    pct = float(r.get('macro_wave_visible_move_pct') or r.get('macro_wave_move_pct') or 0)
    if r.get('day_utc') == '2026-05-12' and dur < 15 and pct >= 1:
        print(r['macro_wave_no'], r['macro_wave_direction'], r['macro_wave_start_time_utc'], r['macro_wave_end_time_utc'], dur, pct)
'@ | .\.venv\Scripts\python.exe -
```

## STAS2 Continuous Wave Ledger 2026-07-09

Статус: `STAS2_MARKET_PHASE_REVIEW_CONTINUOUS_WAVE_READY_NO_ML_NO_OPTUNA_REVIEW_ONLY`.

Проверить код:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas2_market_phase_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas2_market_phase_review.py tests\test_visual_entry_low_anchor_suggester.py -q
```

Повторить финальный Stas2 run `2026-05-10..2026-05-12`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_review --start-day 2026-05-10 --end-day 2026-05-12 --run-label stas2_20260510_20260512_continuous_wave_v2 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260510_20260512_carry48_for_stas2_v0_20260709_070902
```

Открыть результат:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-10
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-11
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse
```

Финальный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330`

Проверить артефакты:

```powershell
@'
from pathlib import Path
import csv, json
from openpyxl import load_workbook
run = Path(r'STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_continuous_wave_v2_20260709_081330')
payload = json.loads((run / 'STAS2_PAYLOAD.json').read_text(encoding='utf-8'))
with (run / 'STAS2_CONTINUOUS_WAVES.csv').open('r', encoding='utf-8-sig', newline='') as f:
    continuous = list(csv.DictReader(f))
with (run / 'STAS2_MACRO_WAVES.csv').open('r', encoding='utf-8-sig', newline='') as f:
    macro = list(csv.DictReader(f))
wb = load_workbook(run / 'STAS2_MARKET_PHASE_TABLES.xlsx', read_only=True)
pngs = list(run.rglob('*.png'))
empty = [p.as_posix() for p in pngs if p.stat().st_size <= 1024]
carry = [r for r in macro if str(r.get('macro_wave_carry_from_prev_day')).lower() == 'true' or str(r.get('macro_wave_carry_to_next_day')).lower() == 'true']
print({'summary': payload['summary'], 'continuous': len(continuous), 'macro': len(macro), 'carry_slices': len(carry), 'sheets': wb.sheetnames, 'png_count': len(pngs), 'empty_png': len(empty)})
'@ | .\.venv\Scripts\python.exe -
```

Граница: `continuous_wave_*` и `macro_wave_*` являются visual/review слоями. Не использовать их как causal ML feature, scorer, target-lock или TP-логику без отдельного approval.

## STAS2 Macro Wave GAP Segments 2026-07-09

Статус: `STAS2_MARKET_PHASE_REVIEW_WAVE_GAP_SEGMENTS_READY_NO_ML_NO_OPTUNA_REVIEW_ONLY`.

Проверить код:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas2_market_phase_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas2_market_phase_review.py tests\test_visual_entry_low_anchor_suggester.py -q
```

Повторить контрольный Stas2 run `2026-05-10..2026-05-12`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_review --start-day 2026-05-10 --end-day 2026-05-12 --run-label stas2_20260510_20260512_gap_segments_v1 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260510_20260512_carry48_for_stas2_v0_20260709_070902
```

Открыть результат:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-10
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse
```

Финальный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_gap_segments_v1_20260709_073810`

Проверить артефакты:

```powershell
@'
from pathlib import Path
import csv, json
from openpyxl import load_workbook
run = Path(r'STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260510_20260512_gap_segments_v1_20260709_073810')
payload = json.loads((run / 'STAS2_PAYLOAD.json').read_text(encoding='utf-8'))
with (run / 'STAS2_MACRO_WAVES.csv').open('r', encoding='utf-8-sig', newline='') as f:
    waves = list(csv.DictReader(f))
wb = load_workbook(run / 'STAS2_MARKET_PHASE_TABLES.xlsx', read_only=True)
pngs = list(run.rglob('*.png'))
empty = [p.as_posix() for p in pngs if p.stat().st_size <= 1024]
print({'summary': payload['summary'], 'macro_rows': len(waves), 'sheets': wb.sheetnames, 'png_count': len(pngs), 'empty_png': len(empty)})
'@ | .\.venv\Scripts\python.exe -
```

Граница: `GAP` закрывает визуальные пропуски в строке `WAVE`, но не является входом, TP, ML-label или causal feature.

## STAS2 SHORT And Macro Wave Review 2026-07-09

Статус: `STAS2_MARKET_PHASE_REVIEW_SHORT_MACRO_WAVE_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_PLUS_REVIEW_ONLY`.

Проверить код:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas2_market_phase_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas2_market_phase_review.py tests\test_visual_entry_low_anchor_suggester.py -q
```

Повторить финальный Stas2 run `2026-05-04..2026-05-09`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_review --start-day 2026-05-04 --end-day 2026-05-09 --run-label stas2_20260504_20260509_short_macro_wave_v1 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260504_20260509_carry48_for_stas2_v0_20260707_042858
```

Открыть результат:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-04
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse
```

Финальный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_short_macro_wave_v1_20260709_064759`

Проверить артефакты:

```powershell
@'
from pathlib import Path
import csv, json
from openpyxl import load_workbook
run = Path(r'STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260504_20260509_short_macro_wave_v1_20260709_064759')
with (run / 'STAS2_HOURLY_PHASES.csv').open('r', encoding='utf-8-sig', newline='') as f:
    hourly = list(csv.DictReader(f))
with (run / 'STAS2_MACRO_WAVES.csv').open('r', encoding='utf-8-sig', newline='') as f:
    waves = list(csv.DictReader(f))
payload = json.loads((run / 'STAS2_PAYLOAD.json').read_text(encoding='utf-8'))
wb = load_workbook(run / 'STAS2_MARKET_PHASE_TABLES.xlsx', read_only=True)
pngs = list(run.rglob('*.png'))
empty = [p.as_posix() for p in pngs if p.stat().st_size <= 1024]
print({'status': payload['status'], 'hourly_rows': len(hourly), 'macro_waves': len(waves), 'sheets': wb.sheetnames, 'png_count': len(pngs), 'empty_png': len(empty)})
'@ | .\.venv\Scripts\python.exe -
```

Граница: `SHORT` по часам является закрытым часовым review-контекстом. `WAVE` является hindsight review по дневному swing. Не использовать как causal ML feature без отдельной causal-разметки.

## STAS3 Percent Ladder Review 2026-07-06

Статус: `STAS3_PERCENT_LADDER_REVIEW_READY_NO_ML_NO_OPTUNA_POST_ENTRY_AUDIT`.

Проверить код:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas3_percent_ladder_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_stas3_percent_ladder_review.py tests\test_visual_entry_low_anchor_suggester.py -q
```

Повторить контрольный Stas3 run по финальному Stas2:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas3_percent_ladder_review --start-day 2026-05-02 --end-day 2026-05-03 --run-label stas3_20260502_20260503_tp_ladder_v0 --stas2-run-dir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535 --hold-hours 48 --post-plot-minutes 360 --tp-fast-minutes 120 --tp-min-samples 5 --tp-hit-rate-min 0.60 --tp-fast-hit-rate-min 0.50
```

То же через wrapper:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-02 -EndDay 2026-05-03 -RunLabel stas3_20260502_20260503_tp_ladder_v0 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50
```

Повторить расширенный Stas3 run по последнему Stas2 `2026-05-04..2026-05-09`:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-04 -EndDay 2026-05-09 -RunLabel stas3_20260504_20260509_tp_ladder_v0 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260504_20260509_setup_quality_v0_20260707_043734 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50
```

Повторить Stas3 run с явным TP/EXIT overlay на графиках:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-04 -EndDay 2026-05-09 -RunLabel stas3_20260504_20260509_tp_exit_overlay_v0 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260504_20260509_setup_quality_v0_20260707_043734 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50
```

Повторить Stas3 run с раздельными `SIGNAL -> ENTRY -> EXIT`:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-04 -EndDay 2026-05-09 -RunLabel stas3_20260504_20260509_signal_entry_exit_overlay_v0 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260504_20260509_setup_quality_v0_20260707_043734 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50
```

Повторить Stas3 run с красной стрелкой визуальной отработки `ENTRY -> EXIT`:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-04 -EndDay 2026-05-09 -RunLabel stas3_20260504_20260509_signal_entry_tp_move_v0 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260504_20260509_setup_quality_v0_20260707_043734 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50
```

Повторить Stas3 run с анализом больших ходов `SIGNAL/ENTRY -> MFE MAX`:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 -Day 2026-05-04 -EndDay 2026-05-09 -RunLabel stas3_20260504_20260509_big_move_review_v2 -Stas2RunDir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260504_20260509_setup_quality_v0_20260707_043734 -HoldHours 48 -PostPlotMinutes 360 -TpFastMinutes 120 -TpMinSamples 5 -TpHitRateMin 0.60 -TpFastHitRateMin 0.50
```

Открыть последний результат:

```powershell
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open browse
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open tp
.\STAS3_PERCENT_LADDER_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
```

Контрольный run:

`STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260502_20260503_tp_ladder_v0_20260706_183011`

Проверить артефакты:

```powershell
@'
from pathlib import Path
import csv, json
from openpyxl import load_workbook
run = Path(r'STAS3_PERCENT_LADDER_REVIEW/runs/stas3_20260502_20260503_tp_ladder_v0_20260706_183011')
wb = load_workbook(run / 'STAS3_PERCENT_LADDER_TABLES.xlsx', read_only=True)
def read_rows(name):
    with (run / name).open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
payload = json.loads((run / 'STAS3_PAYLOAD.json').read_text(encoding='utf-8'))
pngs = list(run.rglob('*.png'))
empty = [p.as_posix() for p in pngs if p.stat().st_size <= 1024]
print({
    'records': len(read_rows('STAS3_RECORDS.csv')),
    'entry_phase': len(read_rows('STAS3_ENTRY_PHASE_TABLE.csv')),
    'actual_movement': len(read_rows('STAS3_ACTUAL_MOVEMENT.csv')),
    'reasonable_tp': len(read_rows('STAS3_REASONABLE_TP.csv')),
    'tp_by_phase': len(read_rows('STAS3_TP_LADDER_BY_PHASE.csv')),
    'summary': payload['summary'],
    'sheets': wb.sheetnames,
    'png_count': len(pngs),
    'empty_png': len(empty),
})
'@ | .\.venv\Scripts\python.exe -
```

Проверить хвосты Python:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*visual_entry*' -or $_.CommandLine -like '*Optuna*' -or $_.CommandLine -like '*APTuna*' } | Select-Object ProcessId,CommandLine
```

Граница: Stas3 смотрит будущее после входа. Не использовать его поля как pre-entry features, ML-label, scorer или target-lock без отдельного approved-ledger.

## STAS2 Closed For STAS3 2026-07-06

Статус: `STAS2_CLOSED_FOR_STAS3_NO_ML_NO_OPTUNA`.

Открыть финальный Stas2 visual-run:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
```

Финальный visual-run:

```text
STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535
```

Финальный audit-run фаз/сессий:

```text
reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942
```

Следующая работа по ТЗ: Stas3 percent ladder / entry-TP validation. Для Stas3 сначала писать отдельное ТЗ/отчет и не смешивать post-entry расчеты обратно в Stas2.

Запрет: не запускать ML/export/training, Optuna, scorer, target-lock или API без отдельного явного approval.

## STAS2 Setup Quality Layer 2026-07-06

Статус: `STAS2_MARKET_PHASE_REVIEW_SETUP_QUALITY_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

Проверка:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas2_market_phase_review.py
```

Полный контрольный run по `2026-05-02..2026-05-03`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_review --start-day 2026-05-02 --end-day 2026-05-03 --run-label stas2_20260502_20260503_setup_quality_no_labels_v0 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_20260503_carry48_for_stas2_v0_20260706_163543
```

Открыть последний результат:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
```

Контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535`

Короткая проверка LA045-LA047:

```powershell
Import-Csv .\STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260502_20260503_setup_quality_no_labels_v0_20260706_172535\STAS2_RECORDS.csv |
  Where-Object { $_.day_utc -eq '2026-05-02' -and $_.candidate_id -in @('LA045','LA046','LA047') } |
  Select-Object candidate_id,entry_time_utc,entry_setup_quality_label,entry_setup_quality_reason,stas1_risk_flags
```

Граница: это visual review/pre-entry слой. На overview текстовые названия возле точек не рисуются; сами точки входа остаются как в Stas1. Не запускать ML/export/training, Optuna, scorer, target-lock или API.

## STAS2 Background And LONG Wave Visual Fix 2026-07-06

Статус: `STAS2_MARKET_PHASE_REVIEW_BG_LONG_WAVE_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

Проверка:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas2_market_phase_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_low_anchor_suggester.py -q
```

Полный run по `2026-05-02..2026-05-03`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_review --start-day 2026-05-02 --end-day 2026-05-03 --run-label stas2_20260502_20260503_bg_long_wave_v0 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260503_all_closeups_bad_x_v0_20260706_060244
```

Открыть последний результат:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
```

Контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_bg_long_wave_v0_20260706_131201`

Проверка no-lookahead/Excel/PNG:

```powershell
@'
from pathlib import Path
import csv
from openpyxl import load_workbook
run = Path(r'STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_bg_long_wave_v0_20260706_131201')
with (run / 'STAS2_RECORDS.csv').open('r', encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
bad = [r for r in rows if str(r.get('context_before_entry_check')).lower() != 'true']
wb = load_workbook(run / 'STAS2_MARKET_PHASE_TABLES.xlsx', read_only=True)
pngs = list(run.rglob('*.png'))
empty = [p.as_posix() for p in pngs if p.stat().st_size <= 1024]
print({'rows': len(rows), 'bad_context_before_entry': len(bad), 'sheets': wb.sheetnames, 'png_count': len(pngs), 'empty_png': len(empty)})
'@ | .\.venv\Scripts\python.exe -
```

Граница: Stas2 показывает `Фон` и `LONG` до входа. TP/exit/percent ladder/MFE/MAE/5m post-entry blocks остаются для Stas3. Не запускать ML/export/training, Optuna, scorer, target-lock или API.

## STAS2 Market Phase Visual Review 2026-07-06

Статус: `STAS2_MARKET_PHASE_REVIEW_READY_NO_ML_NO_OPTUNA_PRE_ENTRY_ONLY`.

Проверка:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas2_market_phase_review.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_visual_entry_low_anchor_suggester.py -q
```

Полный run по `2026-05-02..2026-05-03`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_review --start-day 2026-05-02 --end-day 2026-05-03 --run-label stas2_20260502_20260503_market_phase_review_v0 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260503_all_closeups_bad_x_v0_20260706_060244
```

То же через wrapper:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\run_range.ps1 -Day 2026-05-02 -EndDay 2026-05-03 -RunLabel stas2_20260502_20260503_market_phase_review_v0 -Stas1RunDir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034,STAS1_GOOD_LOW_REVIEW\runs\stas1_20260503_all_closeups_bad_x_v0_20260706_060244
```

Открыть:

```powershell
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx
.\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-02
```

Контрольный run:

`STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_market_phase_review_v0_20260706_124134`

Проверка no-lookahead/Excel:

```powershell
@'
from pathlib import Path
import csv
from openpyxl import load_workbook
run = Path(r'STAS2_MARKET_PHASE_REVIEW/runs/stas2_20260502_20260503_market_phase_review_v0_20260706_124134')
wb = load_workbook(run / 'STAS2_MARKET_PHASE_TABLES.xlsx', read_only=True)
with (run / 'STAS2_RECORDS.csv').open('r', encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
bad = [r for r in rows if str(r.get('context_before_entry_check')).lower() != 'true']
print({'sheets': wb.sheetnames, 'csv_rows': len(rows), 'bad_context_before_entry': len(bad)})
'@ | .\.venv\Scripts\python.exe -
```

Граница: Stas2 pre-entry only. Не запускать ML/export/training, Optuna, scorer, target-lock или API.

## STAS2 Excel-Friendly Run 2026-07-06

Статус: `STAS2_EXCEL_EXPORT_UTF8_BOM_XLSX_READY_NO_ML_NO_OPTUNA`.

Прогон `2026-05-02..2026-05-03` с исправленным Excel-export:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_audit --start-day 2026-05-02 --end-day 2026-05-03 --run-label stas2_20260502_20260503_excel_xlsx_fix --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260503_all_closeups_bad_x_v0_20260706_060244
```

Открыть готовый Excel-файл:

```powershell
ii .\reports\final_review\visual_entry_v3\fresh_target_led\stas2_market_phase_percent_ladder\stas2_20260502_20260503_excel_xlsx_fix_20260706_112616\STAS2_MARKET_PHASE_TABLES.xlsx
```

Граница: это report/export fix, не ML/export/training, не Optuna, не scorer, не target-lock и не API.

## STAS2 Market Phase Session Audit 2026-07-06

Статус: `STAS2_MARKET_PHASE_SESSION_AUDIT_READY_NO_ML_NO_OPTUNA`.

Проверить скрипт:

```powershell
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_stas2_market_phase_audit.py
```

Воспроизвести финальный Stas 2 run по актуальным Stas1 runs:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas2_market_phase_audit --start-day 2026-05-02 --end-day 2026-05-08 --run-label stas2_20260502_20260508_session6_daytype_v4 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260503_all_closeups_bad_x_v0_20260706_060244 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260504_20260506_browse_by_day_v0_20260706_063954 --stas1-run-dir STAS1_GOOD_LOW_REVIEW\runs\stas1_20260507_20260508_carry48_v0_20260706_084057
```

Финальный отчет:

`reports/final_review/visual_entry_v3/fresh_target_led/stas2_market_phase_percent_ladder/stas2_20260502_20260508_session6_daytype_v4_20260706_110942/STAS2_MARKET_PHASE_AUDIT_RU.md`

Сессионная модель: `6` UTC-корзин времени плюс отдельный `day_type=weekday/weekend`; effective-сводка лежит в `STAS2_EFFECTIVE_SESSION_SUMMARY.csv`.

Граница: это отчетный audit-run, не ML/export/training, не Optuna, не scorer, не target-lock и не API.

## STAS1 Block 1 Locked 2026-07-06

Блок 1 уже рабочий: прогоняет день/диапазон, собирает low-кандидаты, сохраняет PNG/CSV/JSON и раскладывает просмотр в `BROWSE_BY_DAY/`.

`+1%`:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-07 -EndDay 2026-05-08 -OutcomeLookaheadHours 48 -RunLabel stas1_review_v0 -RenderGoodLimit 0
```

`+0.5%`:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_0p5.ps1 -Day 2026-05-07 -EndDay 2026-05-08 -OutcomeLookaheadHours 48 -RunLabel stas1_review_0p5_v0 -RenderGoodLimit 0
```

Открыть дневной просмотр:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
```

## STAS1 Carry Outcome 2026-07-06

Два дня с проверкой `+1%` до `48` часов после входа:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-07 -EndDay 2026-05-08 -OutcomeLookaheadHours 48 -RunLabel stas1_20260507_20260508_carry48_v0 -RenderGoodLimit 0
```

Открыть дневной просмотр последнего run:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
```

Открыть конкретный день:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-07
```

Проверить carry-счетчики последнего run:

```powershell
$run = Get-ChildItem STAS1_GOOD_LOW_REVIEW\runs -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Import-Csv (Join-Path $run.FullName 'GOOD_1PCT_REVIEW_POOL_RECORDS.csv') | Group-Object outcome_status | Select-Object Count,Name
```

Проверить хвосты Python:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*visual_entry*' -or $_.CommandLine -like '*Optuna*' -or $_.CommandLine -like '*APTuna*' } | Select-Object ProcessId,CommandLine
```

## STAS1 Browse By Day 2026-07-06

Открыть индекс последнего run:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open index
```

Открыть папку дневного просмотра последнего run:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
```

Открыть конкретный день последнего run:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-04
```

Рабочий прогон `2026-05-04..2026-05-06` без лимита closeup-страниц:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-04 -EndDay 2026-05-06 -RunLabel stas1_20260504_20260506_browse_by_day_v0 -RenderGoodLimit 0
```

## STAS1 ALL Closeups GOOD+BAD 2026-07-06

Открыть последние closeup-страницы, где вместе показаны GOOD и BAD кандидаты:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open allcloseups
```

Открыть весь последний визуальный набор: overview, GOOD-only closeups и ALL closeups:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open all
```

Контрольный запуск `2026-05-03`:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-03 -RunLabel stas1_20260503_all_closeups_bad_x_v0 -RenderGoodLimit 80
```

Проверка хвостов Python после запуска:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*visual_entry*' -or $_.CommandLine -like '*Optuna*' -or $_.CommandLine -like '*APTuna*' } | Select-Object ProcessId,CommandLine
```

## STAS1 Good Low Review 2026-07-03

Статус: `STAS1_V0_BASELINE_MAIN_LOW_REVIEW_SCRIPT_NO_ML_NO_OPTUNA`.

Один день `+1%`:

```powershell
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-02
```

Один день `+0.5%`:

```powershell
.\STAS1_GOOD_LOW_REVIEW\run_day_0p5.ps1 -Day 2026-05-02
```

Открыть последний результат:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1
```

Открыть closeup-страницы:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open closeups
```

Проверить open-script без открытия PNG:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -NoOpen
```

Граница: команды используют `src/mlbotnav/visual_entry_good_1pct_review_pool.py`; это review-pool, не ML/export/training, не scorer, не target-lock и не Optuna.

## Low Anchor Entry 1pct Label Review V1 13 May 2026-07-02

Статус: `LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Проверить и собрать V1:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_entry_1pct_label_review.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_entry_1pct_label_review --day 2026-05-13
```

Проверить счетчики:

```powershell
$csv=Import-Csv reports\final_review\visual_entry_v3\fresh_target_led\low_anchor_entry_1pct_label_review_v1_20260513\LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513.csv
$csv | Group-Object review_label | Sort-Object Count -Descending | Select-Object Count,Name
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_FULL_DAY_20260513.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_ZOOM_PAGE_01_20260513.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_1pct_label_review_v1_20260513/LOW_ANCHOR_ENTRY_1PCT_LABEL_REVIEW_V1_20260513_RU.md
```

Граница: V1 является review/dataset-label слоем. Future `+1%` только offline outcome label. No scorer, no target-lock, no ML/export/training, no Optuna.

## DCA Risk Audit V0 W18-W20 2026-07-02

Статус: `DCA_RISK_AUDIT_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_API`.

Проверить и собрать аудит:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_dca_risk_audit_v0.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_dca_risk_audit_v0 --pool-run-dir reports\final_review\visual_entry_v3\fresh_target_led\good_1pct_review_pool\W18_W20_learning_20260702_082819 --run-label W18_W20_dca_risk --selected-limit-per-day 10 --late-hold-minutes 360 --overload-open-count 10 --render-top-days 3
```

Проверить хвосты:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*visual_entry*' -or $_.CommandLine -like '*Optuna*' -or $_.CommandLine -like '*APTuna*' } | Select-Object ProcessId,CommandLine
```

Главный ранс:

```text
reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_REPORT_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_TRADES.csv
reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_DAYS.csv
reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_BASKETS.csv
reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_SUMMARY.png
reports/final_review/visual_entry_v3/fresh_target_led/dca_risk_audit_v0/W18_W20_dca_risk_20260702_154415/DCA_RISK_AUDIT_V0_TOP_DAY_20260502.png
```

Граница: audit only. No scorer, no target-lock, no ML/export/training, no Optuna, no API trading.

## Target 1pct Price Fix V0 2026-07-02

Статус: `TARGET_1PCT_PRICE_FIX_V0_READY_NO_ML_NO_OPTUNA_NO_SCORER`.

Проверить артефакты:

```powershell
Get-ChildItem reports\final_review\visual_entry_v3\fresh_target_led\target_1pct_price_fix_v0
Import-Csv reports\final_review\visual_entry_v3\fresh_target_led\target_1pct_price_fix_v0\TARGET_1PCT_PRICE_FIX_V0_20260702.csv | Measure-Object
```

Проверить русский отчет и хвосты процессов:

```powershell
rg -n "\?\?\?|\x{0420}\x{040E}|\x{0420}\x{045F}|\x{0421}\x{0453}|\x{0421}\x{201A}|\x{00D0}|\x{FFFD}" reports\final_review\visual_entry_v3\fresh_target_led\target_1pct_price_fix_v0\TARGET_1PCT_PRICE_FIX_V0_20260702_RU.md
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*visual_entry*' -or $_.CommandLine -like '*Optuna*' -or $_.CommandLine -like '*APTuna*' } | Select-Object ProcessId,CommandLine
```

Граница: это price/outcome reference. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## V2A Structure Overlay 14 May 2026-07-01

Статус: `V2A_STRUCTURE_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Проверить и собрать:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_strategy_passport_overlay_v2a.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_strategy_passport_overlay_v2a --day 2026-05-14
```

Проверить отчет:

```powershell
rg -n "\?\?\?" reports\final_review\visual_entry_v3\fresh_target_led\strategy_passport_overlay_v2a\V2A_STRUCTURE_OVERLAY_20260514_RU.md src\mlbotnav\visual_entry_strategy_passport_overlay_v2a.py
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Select-Object ProcessId,ParentProcessId,CommandLine,CreationDate
```

Главные PNG:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_FULL_DAY_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_01_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_02_20260514.png
```

Граница: visual overlay only. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## Existing Passport Reconciliation And Overlay 2026-07-01

Статус: `V2A_STRUCTURE_LAYER_20260514_READY_WAIT_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Текущий подпункт не запускает scorer, Optuna или ML. Паспорта уже собраны; разрешено только сверять реестр и готовить visual overlay.

Проверить manifest-сверку:

```powershell
Get-Content -Encoding UTF8 docs\CALIBRATION_NODE_CURRENT\PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md
Get-Content -Encoding UTF8 docs\CALIBRATION_NODE_CURRENT\FRESH_TARGET_LED_STRATEGY_PASSPORT_ROADMAP_RU.md
```

Проверить активный реестр:

```powershell
Get-Content -Encoding UTF8 configs\calibration_action_passports.yaml
```

Граница: следующий рабочий запуск должен быть только `V2A_STRUCTURE_LAYER` visual overlay по `B014/B015/B017/B018` на эталоны `M01..M19` и 7 T15. `B016` только muted/context-only. Scorer, target-lock, Optuna, ML/export/promotion запрещены.

## Git Remote Push MLbotNav 2026-07-01

Статус: `GIT_REMOTE_PUSH_DONE_MAIN_TRACKS_ORIGIN_MAIN`.

Проверка состояния:

```powershell
git status --short --branch
git remote -v
git log --oneline --decorate -3
```

Ожидаемо сейчас: `main...origin/main`, remote `origin=https://github.com/Stanislav1567/MLbotNav.git`, первый коммит `e178c49 Initial commit`.

## Git Init MLbotNav 2026-07-01

Статус: `SUPERSEDED_BY_GIT_REMOTE_PUSH_DONE`.

Уже выполнено:

```powershell
git init
git branch -M main
git check-ignore -v .env .venv data reports models packs _codex_offload_20260530 docs/codex/handoff.md.bak-20260701-183122
git add -A --dry-run
```

Следующий шаг после выбора имени/email и remote:

```powershell
git config user.name "YOUR_NAME"
git config user.email "YOUR_EMAIL"
git add -A
git commit -m "Initial commit"
git remote add origin https://github.com/USER/REPO.git
git push -u origin main
```

## Codex Agent Launch Kit MLbotNav 2026-07-01

Статус: `CODEX_AGENT_LAUNCH_KIT_MLBOTNAV_READY`.

Новый агент в проекте:

```powershell
C:\Users\007\Desktop\Codex Agent\Start MLbotNav Codex Agent.cmd
```

Продолжить последнюю Codex-сессию:

```powershell
C:\Users\007\Desktop\Codex Agent\Resume MLbotNav Codex Agent.cmd
```

Проверки настройки:

```powershell
codex --version
codex login status
codex doctor
```

Ожидаемая текущая база: `codex-cli 0.142.5`, вход через ChatGPT, профиль `agent` автономный, профиль `agent-safe` с подтверждениями рискованных действий. Проектный `AGENTS.md` уже есть. Git в проекте пока не инициализирован.

## Indicator/Hypothesis Review V1 19+7

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V1_M01_M19_T15V1_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Проверить и собрать второй feature/evidence слой по двум эталонам:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_indicator_hypothesis_review_v1.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_indicator_hypothesis_review_v1
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_M01_M19_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_T15_7_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_ZOOM_T15_7_20260515.png
```

Граница: второй слой перед паспортом. Только visual evidence по `RSI14`, `MACD`, `volume/density`, `swing`, `BOS`, `Fibo`. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## T15 Draft Ledger V1 Red Arrow Fix

Статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_RED_ARROW_FIX_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Проверить и собрать:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_t15_draft_ledger.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_t15_draft_ledger
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701_RU.md
```

Граница: draft-ledger only. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## T15 Draft Ledger / Cluster Discussion V0

Статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Проверить и собрать:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_t15_draft_ledger.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_t15_draft_ledger
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701_RU.md
```

Граница: draft-ledger only. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## Indicator/Hypothesis Visual Review V0

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Проверить и собрать:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_indicator_hypothesis_review.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_indicator_hypothesis_review
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_PENDING_ZOOM_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_20260701_RU.md
```

Граница: visual evidence only. No scorer, no ML/export/promotion, no Optuna.

## T15 Priority Zoom Review V0

Статус: `T15_PRIORITY_ZOOM_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Проверить и собрать:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_priority_zoom_review.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_priority_zoom_review
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_SHEET_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L06_PRIORITY_ZOOM_REVIEW_V0_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L13_PRIORITY_ZOOM_REVIEW_V0_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L16_PRIORITY_ZOOM_REVIEW_V0_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_ASSISTANT_VERDICT_20260701_RU.md
```

Граница: visual review only. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## T15 User Verdict V1

Статус: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

Проверить и собрать:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_t15_user_verdict.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_t15_user_verdict
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_FULL_DAY_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701_RU.md
```

Граница: manual verdict only. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## Low Anchor Transfer User Feedback 2026-05-15 V2

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V2_FIXED_NO_ML_NO_OPTUNA`.

Создать feedback v2:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_transfer_feedback --reject-ids T15L01 T15L03 T15L04 T15L05 T15L09 T15L10 T15L12 T15L14 T15L15 T15L17 T15L18 T15L19 T15L20 T15L21 T15L22 --out-dir reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.csv
```

Граница: user feedback only. No ML/export/promotion. No Optuna.

## Low Anchor Transfer User Feedback 2026-05-15 V1

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V1_FIXED_NO_ML_NO_OPTUNA`.

Создать feedback v1:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_transfer_feedback --reject-ids T15L01 T15L03 T15L04 T15L05 T15L09 T15L12 T15L14 T15L15 T15L17 T15L18 T15L19 T15L20 T15L21 T15L22 --source-feedback-png 'C:\Users\007\AppData\Local\Temp\codex-clipboard-102ecf17-d980-4425-bdb8-259e447a3264.png' --out-dir reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.csv
```

Граница: user feedback only. No ML/export/promotion. No Optuna.

## Low Anchor Transfer User Feedback 2026-05-15 V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Создать feedback layer:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_transfer_feedback --reject-ids T15L01 T15L03 T15L04 T15L05 T15L09 T15L12 T15L14 T15L15 T15L17 T15L18 T15L19 T15L20 T15L22 --source-feedback-png 'C:\Users\007\AppData\Local\Temp\codex-clipboard-f8d07a5b-81b3-49fe-935a-0866d140690e.png' --source-feedback-png 'C:\Users\007\AppData\Local\Temp\codex-clipboard-edeb5dc3-a61f-466b-b0ad-0e5c0e9934b1.png' --source-feedback-png 'C:\Users\007\AppData\Local\Temp\codex-clipboard-d14f9b44-edad-4e8c-9a48-e9b3cbe58c01.png'
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_transfer_feedback.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.csv
```

Граница: user feedback only. No ML/export/promotion. No Optuna.

## Low Anchor Transfer Review 2026-05-15 Compact V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_DAY_20260515_READY_NO_ML_NO_OPTUNA`.

Создать compact transfer review:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_transfer_review --day 2026-05-15 --symbol SOLUSDT --timeframe 1m --min-transfer-score 6 --review-cooldown-minutes 24 --out-dir reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_transfer_review.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_FULL_DAY_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_01_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_02_20260515.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_20260515.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_20260515_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_20260515.csv
```

Граница: visual review only. No ML/export/promotion. No Optuna.

## Feature Policy EMA Deferred 2026-07-01

Статус: `LOW_ANCHOR_FEATURE_POLICY_EMA_DEFERRED_NO_ML_NO_OPTUNA`.

Команды нет: это ручная фиксация политики рельсов.

Граница: EMA не использовать как active scorer/passport condition до отдельного решения пользователя. No ML/export/promotion.

## Low Anchor No-Lookahead Feature Audit V0 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_READY_NO_ML_NO_OPTUNA`.

Создать no-lookahead feature audit:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_feature_audit
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_feature_audit.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.png
```

Граница: audit only. No ML/export/promotion.

## Low Anchor Extra Auto Feedback Summary 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_COMPLETE_NO_ML_NO_OPTUNA`.

Собрать итог по page `01..06`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_extra_feedback_summary
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_extra_feedback_summary.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.csv
```

Граница: summary only. No ML/export/promotion.

## Low Anchor Extra Auto Page06 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Создать feedback layer для page `06`, где все кандидаты rejected как `bad_noise_countertrend_entry`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_extra_feedback --page 6 --reason bad_noise_countertrend_entry
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_extra_feedback.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.png
```

Граница: reject label. No ML/export/promotion.

## Low Anchor Extra Auto Page05 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Создать feedback layer для page `05`, где все кандидаты rejected как `bad_noise_weak_context_entry_mismatch`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_extra_feedback --page 5 --reason bad_noise_weak_context_entry_mismatch --source-feedback-png 'C:\Users\007\AppData\Local\Temp\codex-clipboard-1baf2f52-1305-4069-ab31-d096f7898a8c.png'
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_extra_feedback.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.png
```

Граница: reject label, not manual shift. No ML/export/promotion.

## Low Anchor Extra Auto Page04 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Создать feedback layer для page `04`, где все текущие auto-entry помечены `manual_shift_review`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_extra_feedback --page 4 --manual-shift-ids LA042 LA044 LA045 LA046 LA048 LA052 LA054 LA055 LA056 LA057 LA059 LA062 --source-feedback-png 'C:\Users\007\AppData\Local\Temp\codex-clipboard-b2a56dc2-cf24-4ef3-a42b-f08b3bb8a7c6.png'
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_extra_feedback.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.png
```

Граница: `manual_shift_review` не является обучающей меткой.

## Low Anchor Extra Auto Page03 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Создать feedback layer для page `03`, где все кандидаты rejected как `bad_noise_weak_context`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_extra_feedback --page 3 --reason bad_noise_weak_context
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_extra_feedback.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.png
```

Граница: manual anti-label only. No ML/export/promotion.

## Low Anchor Extra Auto Page02 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Создать feedback layer для page `02`, где `LA018/LA020/LA026` оставлены как `possible_entry`, остальные rejected:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_extra_feedback --page 2 --possible-ids LA018 LA020 LA026
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_extra_feedback.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.png
```

Граница: possible entries are not gold labels. No ML/export/promotion.

## Low Anchor Extra Auto Page01 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Создать feedback layer для page `01`, где `LA001..LA012` rejected как `bad_noise_shallow_bounce`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_extra_feedback
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_extra_feedback.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.png
```

Граница: это manual feedback layer. No ML/export/promotion.

## Low Anchor Extra Auto Review V1 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_READY_NO_ML_NO_OPTUNA`.

Создать пакет ручного review для `66` extra auto candidates:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_extra_review
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_extra_review.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_01_20260701.png
```

Граница: extra candidates остаются `pending_user_anti_review` до явного visual verdict.

## Low Anchor Label Ledger V1 Resolved 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_BY_USER_NO_ML_NO_OPTUNA`.

Создать resolved label-ledger после пользовательского `норм` по pending review:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_label_ledger --ledger-version V1 --accept-pending-as-user-ok --out-dir reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_label_ledger.py
@'
import json
from pathlib import Path
p = Path('reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701.json')
obj = json.loads(p.read_text(encoding='utf-8'))
print(obj['status'])
print(obj['target_label_counts'])
print(obj['pending_shift_review_targets'])
print(obj['candidate_label_counts'])
'@ | .\.venv\Scripts\python.exe -
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_TARGETS_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_CANDIDATES_20260701.csv
```

Граница: resolved labels are still no-ML/no-export until separate approval.

## Low Anchor Label Ledger V0 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_READY_NO_ML_NO_OPTUNA`.

Создать label-ledger:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_label_ledger
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_label_ledger.py
@'
import json
from pathlib import Path
p = Path('reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701.json')
obj = json.loads(p.read_text(encoding='utf-8'))
print(obj['status'])
print(obj['target_label_counts'])
print(obj['pending_shift_review_targets'])
'@ | .\.venv\Scripts\python.exe -
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_TARGETS_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_CANDIDATES_20260701.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_PENDING_SHIFT_REVIEW_20260701.png
```

Граница: label-ledger only. Pending labels нельзя отдавать в ML/export.

## Low Anchor User Feedback M03/M09/M10/M11 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_NO_ML_NO_OPTUNA`.

Создать feedback-pack по пользовательскому красному скрину:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_feedback --source-feedback-png 'C:\Users\007\AppData\Local\Temp\codex-clipboard-cd47c54e-a7a2-4324-ad34-8fbe17b226fe.png'
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_feedback.py
@'
import json
from pathlib import Path
p = Path('reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json')
obj = json.loads(p.read_text(encoding='utf-8'))
print(obj['status'])
print([(r['target_id'], r['user_verdict'], r['signal_diff_minutes_auto_minus_preferred']) for r in obj['records']])
'@ | .\.venv\Scripts\python.exe -
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.svg
```

Граница: feedback-only. Scorer, Optuna, ML/export/promotion не запускать.

## Low Anchor Entry Suggester V0 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_SEED_DAY_REVIEW_NO_ML_NO_OPTUNA`.

Запуск seed-day:

```powershell
$env:PYTHONPATH='src'
python -m mlbotnav.visual_entry_low_anchor_suggester --day 2026-05-14 --symbol SOLUSDT --timeframe 1m --slippage-bps 5 --anchor-lookback 12 --max-anchor-age 3 --cooldown-minutes 4 --min-score 2.5
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.csv
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_full_day_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_target_nearest_zoom_20260514.png
```

Проверка:

```powershell
$env:PYTHONPATH='src'
python -m py_compile src/mlbotnav/visual_entry_low_anchor_suggester.py
@'
import json
from pathlib import Path
p = Path("reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.json")
obj = json.loads(p.read_text(encoding="utf-8"))
print(obj["status"], obj["target_match_summary"]["hits_within_3m"], obj["target_match_summary"]["candidate_count"])
'@ | python -
```

Граница: не запускать Optuna/ML/export/promotion. Это review-helper.

## Data Scope Monthly Full-Day Samples 2026-07-01

Статус: `SOLUSDT_1M_MONTHLY_FULL_DAY_SAMPLES_CREATED_NO_ML_NO_OPTUNA`.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701.png
reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701_RU.md
```

Проверка manifest:

```powershell
@'
import json
from pathlib import Path
p = Path("reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701.json")
obj = json.loads(p.read_text(encoding="utf-8"))
print(obj["status"])
print([(r["day_utc"], r["rows"], r["complete_00_to_next_00"]) for r in obj["records"]])
'@ | python -
```

Граница: это проверка данных и графиков, не scorer/Optuna/ML.

## C01 126 Days Source Audit 2026-07-01

Статус: `C01_126_DAYS_SOURCE_AUDIT_COMPLETE_NO_ML_NO_OPTUNA`.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_126_DAYS_SOURCE_AUDIT_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_126_DAYS_SOURCE_AUDIT_20260701.json
```

Проверка источника `SOLUSDT 1m`:

```powershell
@'
import csv, json
from pathlib import Path
root = Path(r"C:\Users\007\Desktop\MLbotNav")
files = sorted((root / "data/core/bybit_ohlcv").glob("dt=*/tf=1m/symbol=SOLUSDT/part-final.csv"))
bad = []
for p in files:
    with p.open("r", encoding="utf-8", newline="") as f:
        rows = sum(1 for _ in f) - 1
    if rows != 1440:
        bad.append((str(p), rows))
result = {
    "files": len(files),
    "first": files[0].parts[-4] if files else None,
    "last": files[-1].parts[-4] if files else None,
    "bad_row_counts": bad,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
'@ | python -
```

Граница: это audit-only, C01 V1 не продвигать; Optuna/ML/export/promotion запрещены.

## C02A Seed-Lock V0 2026-07-01

Статус: `C02A_TARGET_LOCK_SEED_V0_CREATED_NO_ML_NO_OPTUNA`.

Актуальные артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_FULL_DAY_ZOOMS_20260630.png
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_FULL_DAY_ZOOMS_20260630.svg
```

Проверка JSON:

```powershell
@'
import json
from pathlib import Path
p = Path(r"reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_20260630.json")
data = json.loads(p.read_text(encoding="utf-8"))
print(data["status"])
print([x["target_id"] for x in data["locked_targets"]])
'@ | python -
```

## C02A Entry-Only Scorer V0 2026-06-30

Статус: `C02A_ENTRY_ONLY_SCORER_V0_SEED_DAY_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Актуальные артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_V0_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_V0_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_EVENT_MATRIX_V0_20260630.csv
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.png
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.svg
```

Проверка JSON:

```powershell
@'
import json
from pathlib import Path
p = Path(r"reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_V0_20260630.json")
data = json.loads(p.read_text(encoding="utf-8"))
print(data["status"])
print(data["counts"]["entry_signals"], data["counts"]["violations"])
'@ | python -
```

Проверка хвостов Python после запуска:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Select-Object ProcessId,CommandLine
```

## C02 Good/Bad Audit 2026-06-30

Статус: `C02_GOOD_BAD_AUDIT_V0_COMPLETE_NO_ML_NO_OPTUNA`.

Актуальные артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_EVENT_FEATURES_V0_20260630.csv
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_FULL_DAY_AUDIT_V0_20260630.png
```

Проверка:

```powershell
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$p = "reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630.json"
Get-Content -Encoding UTF8 $p -Raw | ConvertFrom-Json | Select-Object status,next_step
```

Следующий подпункт: `C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`.

## C02 User-Labeled Review 2026-06-30

Статус: `C02_CANDIDATE_REVIEW_V0_USER_LABELS_COMPLETE_NO_ML_NO_OPTUNA`.

Актуальные C02-артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_LEDGER_V0_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_LEDGER_V0_20260630.csv
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_USER_LABELED_GOOD_BAD_SHEET_20260630.png
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/passport_VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0.json
```

Проверка статуса:

```powershell
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$p = "reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_LEDGER_V0_20260630.json"
(Get-Content -Encoding UTF8 $p -Raw | ConvertFrom-Json).user_review_summary
```

Следующий подпункт: аудит `GOOD_ENTRY` против `BAD_ENTRY`; scorer/Optuna/ML/export/promotion не запускать.

## Passport Bench V0 Step Plan 2026-06-30

Статус: `C02_CANDIDATE_REVIEW_PACK_READY_WAIT_USER_LABELS_NO_ML_NO_OPTUNA`.

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_BENCH_V0_STEP_PLAN_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/passport_VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/passport_VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/seed_visual/C02_DEEP_CAPITULATION_LOW_SEED_VISUAL_M01_M02_M08_20260630_v2.png
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/seed_visual/C02_DEEP_CAPITULATION_LOW_SEED_VISUAL_M01_M02_M08_20260630_v2.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/seed_visual/C02_DEEP_CAPITULATION_LOW_SEED_VISUAL_AUDIT_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_full_day_review_20260630.png
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_event_representatives_20260630.csv
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_raw_candidates_20260630.csv
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_AUDIT_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_zoom_sheet_C02E01_C02E16_20260630.png
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_LEDGER_V0_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_LEDGER_V0_20260630.csv
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_AUDIT_20260630_RU.md
```

Проверка JSON:

```powershell
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$p = "reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630.json"
Get-Content -Encoding UTF8 $p -Raw | ConvertFrom-Json | Select-Object status,current_decision
```

Следующая рабочая папка:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW
```

Следующий подпункт: пользовательская разметка `C02E01..C02E16`, без scorer/Optuna/ML/export/promotion.

## Fresh Target-Led Passport Bench V0 2026-06-30

Статус: `PASSPORT_BENCH_V0_STRUCTURED_NO_ML_NO_OPTUNA`.

Основной аудит:

```text
reports/final_review/visual_entry_v3/fresh_target_led/process_audit/PASSPORT_BENCH_STAGE_AUDIT_20260630_RU.md
```

Полезная read-only проверка покрытия паспортами:

```powershell
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$j=Get-Content -Encoding UTF8 "reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json" -Raw | ConvertFrom-Json
$j.targets | Group-Object target_type | ForEach-Object {
  [pscustomobject]@{
    type=$_.Name
    count=$_.Count
    targets=($_.Group.target_id -join ',')
    linked_passports=(($_.Group.linked_passport | Where-Object { $_ }) -join ',')
  }
} | Format-Table -AutoSize
```

Запрещено в этом этапе: Optuna, ML/export/promotion, старые V7/V8/V9/V10/V11 как очередь задач.

## Fresh Target-Led C01 Multi-Day Check V1 2026-06-30

Статус: `C01_MULTI_DAY_CHECK_V1_RAW_NEEDS_VISUAL_TUNING_NO_ML`.

Основные артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_full_day_overlay_20260630.png
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_eye_check_M05_shift_right_full_day_M05_M06_zoom_20260630.png
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_AUDIT_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_full_day_M05_M06_zoom_20260630.png
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_AUDIT_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_20260630.json
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_full_day_M05_M06_20260630.png
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_ENTRY_INPUT_CONTRACT_V1_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_MULTI_DAY_CHECK_V1_AUDIT_20260630_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_MULTI_DAY_CHECK_V1_all_candidates_zoom_contact_20260630.png
```

Проверка JSON/кодировки и хвостов после работы:

```powershell
$env:PYTHONPATH='src'
@'
import json
from pathlib import Path
paths = [
    Path('reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_20260630.json'),
    Path('reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_eye_check_M05_shift_right_full_day_M05_M06_zoom_20260630.json'),
    Path('reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_20260630.json'),
    Path('reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_20260630.json'),
    Path('reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_ENTRY_INPUT_CONTRACT_V1_20260630.json'),
    Path('reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_MULTI_DAY_CHECK_V1_20260630.json'),
    Path('reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/passport_VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0.json'),
]
for path in paths:
    json.loads(path.read_text(encoding='utf-8'))
    print('JSON OK', path)
for path in [
    Path('reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v0/C01_ENTRY_ONLY_SCORER_V0_AUDIT_20260630_RU.md'),
    Path('docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md'),
]:
    text = path.read_text(encoding='utf-8')
    assert ('?' * 4) not in text and '\ufffd' not in text
    print('TEXT OK', path)
'@ | .\.venv\Scripts\python.exe -

Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Optuna/ML/export/promotion в этом пункте не запускать.

## Visual Entry EVENT_RANKED_BRICKS_V10 Commands 2026-06-29

Validation `2026-05-13`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_event_ranked_bricks_v10_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\event_ranked_bricks_v10_validation --render-top 5
```

Holdout `2026-05-14` user red arrows v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_event_ranked_bricks_v10_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\event_ranked_bricks_v10_holdout --render-top 5
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_event_ranked_bricks_v10_runner.py tests\test_visual_entry_event_ranked_bricks_v10_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_event_ranked_bricks_v10_runner tests.test_visual_entry_brick_by_brick_selector_v9_runner tests.test_visual_entry_negative_context_suppression_v8_runner tests.test_visual_entry_generalization_v7_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
```

Process-check after run:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Result 2026-06-29: `EVENT_RANKED_BRICKS_V10_CLEANER_BUT_PARTIAL_NO_ML`; validation `HOT_CHAIN` = `1/9`, `0` false; holdout `warm` = `3/17`, `6` false; `hot-first` = `2/17`, `7` false; `deep` = `3/17`, `20` false. Not ML-ready. Next: `V11_RECOVER_RANKED_MISSES`.

## Visual Entry BRICK_BY_BRICK_SELECTOR_V9 Commands 2026-06-29

Validation `2026-05-13`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_brick_by_brick_selector_v9_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\brick_by_brick_selector_v9_validation --render-top 6
```

Holdout `2026-05-14` user red arrows v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_brick_by_brick_selector_v9_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\brick_by_brick_selector_v9_holdout --render-top 6
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_brick_by_brick_selector_v9_runner.py tests\test_visual_entry_brick_by_brick_selector_v9_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_brick_by_brick_selector_v9_runner tests.test_visual_entry_negative_context_suppression_v8_runner tests.test_visual_entry_generalization_v7_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
```

Process-check after run:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Result 2026-06-29: `BRICK_BY_BRICK_SELECTOR_V9_PARTIAL_DIAGNOSTIC_NO_ML`; validation clean brick `V9_01` = `1/9`, `0` false; holdout best `V9_03` = `5/17`, `16` false; research union `12/17`, but `68` false. Not ML-ready. Next: `V10_EVENT_RANKED_BRICKS`.

## Visual Entry marked PNG to manual entries 2026-06-25
Статус: `READY_NO_ML`.

Создать `manual_entries.json`, авто-кандидаты `AK#` и контрольный PNG для `2026-05-13`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_marked_png_to_manual_entries --seed-json reports\manual_entries\SOLUSDT_1m_visual_seed_20260625\manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.json --marked-png C:\Users\007\AppData\Local\Temp\codex-clipboard-01755f5a-1a31-43fe-ad46-4dbda1dd20ab.png --out-dir reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms --dataset-role VALIDATION_DAY --x-utc-0000 159 --px-per-hour 52.625 --slippage-bps 5 --auto-knife-top-n 8 --auto-cooldown-bars 30
```

Создать `manual_entries.json`, авто-кандидаты `AK#` и контрольный PNG для `2026-05-14`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_marked_png_to_manual_entries --seed-json reports\manual_entries\SOLUSDT_1m_visual_seed_20260625\manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.json --marked-png C:\Users\007\AppData\Local\Temp\codex-clipboard-7f16d829-2703-4219-a31c-989fc8fcaf84.png --out-dir reports\manual_entries\SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms --dataset-role HOLDOUT_DAY --x-utc-0000 144 --px-per-hour 52.58 --slippage-bps 5 --auto-knife-top-n 10 --auto-cooldown-bars 30
```

Проверка CP06 без подкрутки:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_noise_suppression_cluster_priority_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\noise_suppression_cluster_priority_validation_holdout --render-top 8
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_noise_suppression_cluster_priority_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\noise_suppression_cluster_priority_validation_holdout --render-top 8
```

Результат текущего прогона: на обоих днях `best=[]`, `rendered=[]`. В ML ничего не передавать.

## Visual Entry CP06 validation/holdout readiness 2026-06-25
Статус: `WAIT_FOR_MANUAL_LABELS`.

Перед validation/holdout проверить, что для дня существует `manual_entries.json` с `entries[].target_entry_time_utc`. Сейчас готовы только seed PNG:

```powershell
Get-ChildItem -Path reports\manual_entries -Recurse -Filter manual_entries.json | Select-Object -ExpandProperty FullName
Get-Content -Encoding UTF8 reports\final_review\visual_entry_v3\cp06_validation_holdout_readiness\cp06_validation_holdout_readiness_20260625_RU.md
```

Seed PNG для ручной разметки:

```text
reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.png
reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.png
```

CP06 запускать на `2026-05-13`/`2026-05-14` только после создания manual labels и только без изменения параметров.

## Visual Entry v3 DEEP_CAPITULATION_RECLAIM 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY_NO_ML`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_deep_capitulation_reclaim_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\deep_capitulation_reclaim --render-top 8
```

Отчеты:
1. `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_20260512_DEV.json`;
2. `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_20260512_DEV_RU.md`;
3. `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_audit_20260625_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_family_overlay_2026-05-12_deep_reclaim_01_dq01_eq01_plus_deep_reclaim_20260625T142559Z.png`.

High-recall PNG: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_family_overlay_2026-05-12_deep_reclaim_03_dq03_eq03_high_recall_plus_deep_20260625T142607Z.png`.

Решение: diagnostic-only, в ML ничего не передавать.

Проверка хвостов процессов после visual-entry:

## Visual Entry NEGATIVE_CONTEXT_SUPPRESSION_V8 Commands 2026-06-29

Validation `2026-05-13`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_negative_context_suppression_v8_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\negative_context_suppression_v8_validation --render-top 6
```

Holdout `2026-05-14` user red arrows v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_negative_context_suppression_v8_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\negative_context_suppression_v8_holdout --render-top 6
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_negative_context_suppression_v8_runner.py src\mlbotnav\visual_entry_generalization_v7_runner.py tests\test_visual_entry_negative_context_suppression_v8_runner.py tests\test_visual_entry_generalization_v7_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_negative_context_suppression_v8_runner tests.test_visual_entry_generalization_v7_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
```

Process-check after run:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Result 2026-06-29: `NEGATIVE_CONTEXT_SUPPRESSION_V8_PARTIAL_BRICK_NO_ML`; validation clean brick `V8_02` = `1/9`, `0` false; holdout `V8_01` = `4/17`, `29` false; union still noisy `11/17`, `168` false. Not ML-ready.

## Visual Entry GENERALIZATION_V7 Commands 2026-06-29

Validation `2026-05-13`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_generalization_v7_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\generalization_v7_validation --render-top 6
```

Holdout `2026-05-14` user red arrows v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_generalization_v7_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\generalization_v7_holdout --render-top 6
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_generalization_v7_runner.py tests\test_visual_entry_generalization_v7_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_generalization_v7_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
```

Process-check after run:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Result 2026-06-29: `GENERALIZATION_V7_DIAGNOSTIC_FAIL_NO_ML`; validation best `1/9` with `22` false, holdout best f1 `4/17` with `43` false, noisy union `11/17` with `203` false. Not ML-ready.

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

## Visual Entry Deep Recovery And Hot Recall V4 Commands 2026-06-29

Run holdout `2026-05-14` user red arrows v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_deep_recovery_hot_recall_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\deep_recovery_hot_recall --render-top 8
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_deep_recovery_hot_recall_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
```

Syntax check without writing `pyc`, useful if `tests/__pycache__` is locked:

```powershell
$env:PYTHONPATH='src'; @'
from pathlib import Path
for path in [Path('src/mlbotnav/visual_entry_deep_recovery_hot_recall_runner.py'), Path('tests/test_visual_entry_deep_recovery_hot_recall_runner.py')]:
    compile(path.read_text(encoding='utf-8'), str(path), 'exec')
print('syntax OK')
'@ | .\.venv\Scripts\python.exe -
```

Process-check after run:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

## Visual Entry Online Low Event Quality V3 Commands 2026-06-29

Run holdout `2026-05-14` user red arrows v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_online_low_event_quality_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\online_low_event_quality --render-top 8
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_online_low_event_quality_runner.py tests\test_visual_entry_online_low_event_quality_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_online_low_event_quality_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
```

Process-check after run:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

## Visual Entry Regime False Suppression V2 Commands 2026-06-29

Run holdout `2026-05-14` user red arrows v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_regime_false_suppression_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\regime_false_suppression --render-top 8
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_regime_false_suppression_runner.py tests\test_visual_entry_regime_false_suppression_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_regime_false_suppression_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
```

Process-check after run:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

## Visual Entry Low Cluster Ranker V2 Commands 2026-06-29

Run holdout `2026-05-14` user v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_cluster_ranker_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\low_cluster_ranker --render-top 7
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_cluster_ranker_runner.py tests\test_visual_entry_low_cluster_ranker_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_low_cluster_ranker_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
```

## Visual Entry v3 EARLY_FLUSH_REVERSAL 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY_NO_ML`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_early_flush_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\early_flush_reversal --render-top 6
```

Отчеты:
1. `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_20260512_DEV.json`;
2. `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_20260512_DEV_RU.md`;
3. `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_audit_20260625_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_family_overlay_2026-05-12_early_flush_01_eq01_q09_severe_soft45_20260625T134923Z.png`.

Решение: diagnostic-only, в ML ничего не передавать.

## Visual Entry v3 quality filter commands 2026-06-25
Запуск quality/suppression diagnostic:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_quality_filter_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\quality_filter --render-top 6
```

Top audit:

```text
reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_audit_20260625_RU.md
```

## Visual Entry v3 micro-bottom commands 2026-06-25
Запуск micro-bottom diagnostic:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_micro_bottom_signature_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\micro_bottom_signature --render-top 6
```

После любого visual-entry прогона проверять хвосты процессов:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' } | Select-Object ProcessId,CommandLine
```
## Visual Entry v3 passport-family runner 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY_NO_ML`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_passport_family_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\passport_family_runner --render-top 6
```

Отчеты:
1. `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_runner_20260512_DEV.json`;
2. `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_runner_20260512_DEV_RU.md`;
3. `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_audit_20260625_RU.md`.

Решение текущего прогона: лучший результат `1/11` hits и `20` false, поэтому это diagnostic-only. В ML ничего не передавать.

## Visual Entry v3 no-lookahead 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_no_lookahead_candidates --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\no_lookahead_candidates_rerun --render-top 5
```

Проверенный отчет: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`. В ML ничего не передавать.

## Visual Entry Score DEV-12 2026-06-25
Статус: `READY`.

Создать отчет попаданий backtest-входов в ручные стрелки `2026-05-12`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_score --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v1\manual_entries.json --trades-csv reports\final_review\oos_backtest_trades_SOLUSDT_1m_2026-05-12_long_only_20260625T073603Z.csv --out-dir reports\qa_gate
```

Проверенный отчет:

`reports/qa_gate/visual_entry_score_SOLUSDT_1m_visual_dev_20260625_20260512_v1_oos_backtest_trades_SOLUSDT_1m_2026-05-12_long_only_20260625T073603Z.json`

Итог для старого B001 diagnostic: `3/6` попаданий, `15` лишних входов, `precision=0.16666666666666666`, `recall=0.5`, `f1_visual=0.25`, `net_return_pct=-62.229358575198916`. В ML не передавать.

## Visual Entry feature audit and prefilter 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY`.

Feature-аудит ручных входов:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_feature_audit --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v1\manual_entries.json --out-dir reports\qa_gate
```

Prefilter-поиск:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_prefilter_search --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v1\manual_entries.json --out-dir reports\qa_gate
```

Отчеты:
1. `reports/qa_gate/visual_entry_feature_audit_20260512_DEV.json`;
2. `reports/qa_gate/visual_entry_prefilter_search_20260512_DEV.json`;
3. `reports/qa_gate/visual_entry_candidate_family_plan_20260512_DEV_RU.md`.

Решение: prefilter diagnostic-only, в ML не передавать.

## Visual Entry overlay 2026-06-25
Статус: `READY`.

Показать ручные цели и B001 fixed diagnostic на одном PNG:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.render_visual_entry_overlay --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v1\manual_entries.json --trades-csv reports\final_review\oos_backtest_trades_SOLUSDT_1m_2026-05-12_long_only_20260625T073603Z.csv --label B001_FIXED_DEV12 --out-dir reports\final_review
```

Показать ручные цели и TOP1 prefilter diagnostic:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.render_visual_entry_overlay --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v1\manual_entries.json --prefilter-json reports\qa_gate\visual_entry_prefilter_search_20260512_DEV.json --top-index 0 --label PREFILTER_TOP1_DEV12 --out-dir reports\final_review
```

Свежие PNG:
1. `reports/final_review/visual_entry_overlay_2026-05-12_b001_fixed_dev12_20260625T095333Z.png`;
2. `reports/final_review/visual_entry_overlay_2026-05-12_prefilter_top1_dev12_20260625T095333Z.png`.

Обновленные PNG с ярко-красным `X` для ложных входов:
1. `reports/final_review/visual_entry_overlay_2026-05-12_b001_fixed_dev12_20260625T095623Z.png`;
2. `reports/final_review/visual_entry_overlay_2026-05-12_prefilter_top1_dev12_20260625T095623Z.png`.

## Visual Entry solo passport runner 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY`.

Запустить solo-passport visual diagnostic на DEV-дне `2026-05-12`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_solo_passport_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v1\manual_entries.json --out-dir reports\final_review --render-top 6
```

Отчеты:
1. `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV.json`;
2. `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV_RU.md`.

Top PNG:
1. `reports/final_review/visual_entry_overlay_2026-05-12_solo_01_f009_emagap_down_20260625T100953Z.png`;
2. `reports/final_review/visual_entry_overlay_2026-05-12_solo_02_f059_engulfbull_20260625T100955Z.png`;
3. `reports/final_review/visual_entry_overlay_2026-05-12_solo_03_f010_emaslope_down_20260625T100957Z.png`;
4. `reports/final_review/visual_entry_overlay_2026-05-12_solo_04_f035_supportdist_20260625T100959Z.png`;
5. `reports/final_review/visual_entry_overlay_2026-05-12_solo_05_f017_f018_stoch14_20260625T101002Z.png`;
6. `reports/final_review/visual_entry_overlay_2026-05-12_solo_06_f038_rangepose_20260625T101004Z.png`.

Решение: diagnostic-only, в ML не передавать.

## B001 marked-entry fixed diagnostic 2026-06-25
Статус: `DONE_NEGATIVE_NO_PROMOTION`.

Аудит: `reports/qa_gate/b001_marked_entry_fixed_backtest_audit_20260625T073900Z_RU.md`.

Матрица: `reports/qa_gate/b001_marked_entry_fixed_long_20260625T071500Z/B001_F001_F005_MARKED_ENTRY_FIXED_long_3OF5.yaml`.

Повторить diagnostic-only прогон с `min_expected_move_pct=0.001`:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 1 -ProcessWorkers 1 -SearchWorkersPerProcess 1 -OptunaTrials 8 -OptunaTimeoutSec 300 -CalibrationMatrixPath reports\qa_gate\b001_marked_entry_fixed_long_20260625T071500Z\B001_F001_F005_MARKED_ENTRY_FIXED_long_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage off -MinCandidateTrades 1 -HorizonsGrid 4 -PLongGrid 0.60 -PShortGrid 0.42 -MinExpectedMoveGrid 0.001 -NotionalUsdGrid 10 -StopLossPct 0.008 -TakeProfitPct 0.012 -TpMinFactor 0.7 -MinTpReachProb 0.58 -UseTemporaryUnlock
```

Итог выполненного прогона: `18` сделок, OOS `-47.05387771496912%`, точные попадания `09:25` и `12:36`, в ML не передавать.

Повторить diagnostic-only прогон без min-move:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 1 -ProcessWorkers 1 -SearchWorkersPerProcess 1 -OptunaTrials 8 -OptunaTimeoutSec 300 -CalibrationMatrixPath reports\qa_gate\b001_marked_entry_fixed_long_20260625T071500Z\B001_F001_F005_MARKED_ENTRY_FIXED_long_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage off -MinCandidateTrades 1 -HorizonsGrid 4 -PLongGrid 0.60 -PShortGrid 0.42 -MinExpectedMoveGrid 0.0 -NotionalUsdGrid 10 -StopLossPct 0.008 -TakeProfitPct 0.012 -TpMinFactor 0.7 -MinTpReachProb 0.58 -UseTemporaryUnlock
```

Итог выполненного прогона: `30` сделок, OOS `-67.41968770852606%`, шум увеличился, в ML не передавать.

## Shared-study control smoke after profile-edge fix 2026-06-25
Статус: `DONE_CONFIRMED`.

Аудит фикса: `reports/qa_gate/shared_study_profile_edge_coverage_fix_20260625T063700Z_RU.md`.

Контрольный LONG smoke для проверки profile edge coverage после фикса:

```powershell
$RUN_ID = "b001_3of5_long_shared_edgefix_$(Get-Date -Format yyyyMMdd_HHmmss)"
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath reports\qa_gate\b001_family_unified_long_3of5_shared_20260625T005102\B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId $RUN_ID -UseTemporaryUnlock
```

Подтвержденный запуск: `b001_3of5_long_shared_edgefix3_20260625_115056`.

Финальный отчет: `reports/pipeline/optuna_search_candidate_SOLUSDT_1m_20260625T065106Z_long_only_pool_20260625t065056z_w3.json`.

Итог coverage: terminal `42/42`, core `5/5 PASS`, profile `7/7 PASS`, forced min/max полный `7/7`.

Итог доходности: OOS `0`, сделок `0`; это не кандидат, в ML не передавать.

## B001 family-unified 3/5 shared-study diagnostic 2026-06-24
Статус LONG: `DONE_NEGATIVE_EDGE_WARN`.

Аудит LONG: `reports/qa_gate/b001_family_unified_3of5_long_shared_audit_20260624T195200Z_RU.md`.

Выполненная LONG-команда:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath reports\qa_gate\b001_family_unified_long_3of5_shared_20260625T005102\B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId b001_3of5_long_shared_20260625T005102 -UseTemporaryUnlock
```

Результат: launcher `OK`, best worker `w3`, OOS `-2.0302055441506761`, сделок `1`, ML не трогать.

Если нужен следующий B001 diagnostic SHORT:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.b001_ret_n_ladder_tournament --family-unified --family-move -1 --strict-confirmations 3 --output-dir reports\qa_gate\b001_family_unified_short_3of5_NEXT
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath reports\qa_gate\b001_family_unified_short_3of5_NEXT\B001_F001_F005_FAMILY_UNIFIED_short_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId b001_3of5_short_shared_NEXT -UseTemporaryUnlock
```

Предупреждение: у LONG core edge coverage прошел, но profile edge coverage неполный. Если следующий запуск нужен как clean coverage proof, сначала закрыть этот вопрос.

## Optuna рабочий профиль 3x3/9

Правило: для реальных прогонов и проверки нагрузки используем три process-workers. Профиль `1x9/9` не является физическим эквивалентом `3x3/9`; он остается только диагностикой одной Optuna-истории.

Шаблон LONG:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath <matrix> -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Dry-run: три worker-а `w1/w2/w3`, у каждого `Threads/proc=3`, `Search/proc=3`, `Trials/proc=14`.

Диагностический single-worker, если специально нужна одна Optuna-история:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 1 -SearchWorkersPerProcess 9 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath <matrix> -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

## Диагностика 2026-06-24: B001 family unified

Генерация unified LONG `5/5`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.b001_ret_n_ladder_tournament --family-unified --family-move 1 --strict-confirmations 5 --output-dir reports\qa_gate\b001_family_unified_long_20260624Tmanual
```

Генерация unified SHORT `5/5`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.b001_ret_n_ladder_tournament --family-unified --family-move -1 --strict-confirmations 5 --output-dir reports\qa_gate\b001_family_unified_short_20260624Tmanual
```

Следующий optional diagnostic для `4/5`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.b001_ret_n_ladder_tournament --family-unified --family-move 1 --strict-confirmations 4 --output-dir reports\qa_gate\b001_family_unified_long_4of5_NEXT
```

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.b001_ret_n_ladder_tournament --family-unified --family-move -1 --strict-confirmations 4 --output-dir reports\qa_gate\b001_family_unified_short_4of5_NEXT
```

Аудит unified `5/5`: `reports/qa_gate/b001_family_unified_5of5_audit_20260624T154700Z_RU.md`.

## Диагностика 2026-06-24: B001 family strict 5/5

Матрица:

`reports/qa_gate/b001_family_strict_5of5_20260624T152830Z/B001_F001_F005_STRICT_5OF5.yaml`

Повторить LONG smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath reports\qa_gate\b001_family_strict_5of5_20260624T152830Z\B001_F001_F005_STRICT_5OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Повторить SHORT smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath reports\qa_gate\b001_family_strict_5of5_20260624T152830Z\B001_F001_F005_STRICT_5OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Аудит: `reports/qa_gate/b001_family_strict_5of5_smoke_audit_20260624T153100Z_RU.md`.

## Диагностика 2026-06-24: B001_COMBO_DIAG gate visual

Повторить визуальный аудит LONG:

```powershell
$env:PYTHONPATH='src'; python -m mlbotnav.render_gate_diagnostic --oos-report reports\final_review\oos_report_SOLUSDT_1m_2026-05-12_long_only_20260624T124547Z.json
```

Повторить визуальный аудит SHORT:

```powershell
$env:PYTHONPATH='src'; python -m mlbotnav.render_gate_diagnostic --oos-report reports\final_review\oos_report_SOLUSDT_1m_2026-05-12_short_only_20260624T124628Z.json
```

Текущие артефакты:
1. `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.png`.
2. `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.png`.

## Диагностика 2026-06-24: B001_COMBO_DIAG N-of-M
Статус: `B001_COMBO_DIAG_N_OF_M_SMOKE_DONE_NO_CANDIDATE`.

Аудит: `reports/qa_gate/b001_combo_diag_n_of_m_audit_20260624T125500Z_RU.md`.

Матрицы: `reports/qa_gate/b001_combo_diag_matrices_20260624Tmanual`.

Следующая diagnostic-only команда LONG для 31 комбинации smoke 1д/1д:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -MatrixManifestPath reports\qa_gate\b001_combo_diag_matrices_20260624Tmanual\manifest.json -StartIndex 1 -EndIndex 31 -EnableCombinationTournament -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Следующая diagnostic-only команда SHORT для 31 комбинации smoke 1д/1д:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -MatrixManifestPath reports\qa_gate\b001_combo_diag_matrices_20260624Tmanual\manifest.json -StartIndex 1 -EndIndex 31 -EnableCombinationTournament -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

В ML ничего не передавать.

## Текущий маршрут 2026-06-24: B003.1 large LONG
Статус: `NEXT_B003_1_LARGE_LONG`.

Аудиты:
1. B001.4 LONG: `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.
2. B001.5 SHORT: `reports/qa_gate/b001_large_short_b001_5_audit_20260624T094057Z_RU.md`.
3. B001.6 итог: `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.
4. B002.1 LONG: `reports/qa_gate/b002_large_long_b002_1_audit_20260624T100300Z_RU.md`.
5. B002.2 SHORT: `reports/qa_gate/b002_large_short_b002_2_audit_20260624T100700Z_RU.md`.
6. B002.3 итог: `reports/qa_gate/b002_block_summary_b002_3_20260624T100800Z_RU.md`.

Закрыто:
1. `B001.1` smoke LONG 1д/1д.
2. `B001.2` smoke SHORT 1д/1д.
3. `B001.3` smoke-аудит.
4. `B001.4` large LONG 2н/1н.
5. `B001.5` large SHORT 2н/1н.
6. `B001.6` итог блока.
7. `B002.1` large LONG 2н/1н.
8. `B002.2` large SHORT 2н/1н.
9. `B002.3` итог блока.

Следующий блок: `B003`, одиночный паспорт `F007 / F007_RSTD20_ALLOW`.

Активный worker-профиль: `3x3/9` (`Threads=9`, `SearchWorkers=9`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`).

Команда B003.1 LONG:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B003 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

После B003.1 проверить отчет. Если все штатно, следующий шаг `B003.2 large SHORT`:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B003 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

В ML ничего не передавать.

Last diagnostic UTC: 2026-06-24T10:08:00Z

## Current Route 2026-06-24: block-family calibration
Status: `READY_FOR_B001_BLOCK`.
Audit: `reports/qa_gate/block_family_passport_route_audit_20260624T064900Z.md`.

Route: run calibration by block/family. For `B001`, the runner expands and runs active solo passports `F001..F005`, then writes a block selection report. No package, approval, or ML ingest is created from this step.

Runner: `APTuna/run_block_family_selection.ps1`.

Next exact step: run `B001` LONG, then `B001` SHORT, then audit the block reports.

Run LONG and SHORT sequentially.

B001 BLOCK LONG:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

B001 BLOCK SHORT:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Previous F068-only command pointer is superseded by this block route.

Last updated UTC: 2026-06-24T07:00:59Z

## Current ML Stage 8 Command 2026-06-23 Step 8.2.18 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_18_f067_audit_20260623T225700Z.md`.
Historical next WBS pointer before block-route correction: `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate`. This is superseded by the current block-family route above.

Final valid F067 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F067_patternstrength_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F067 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F067_patternstrength_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F067 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F067. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.17 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_17_f066_audit_20260623T224200Z.md`.
Next exact WBS step: `8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`.

Final valid F066 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F066_obvbeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F066 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F066_obvbeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F066 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F066. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.16 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_16_f065_audit_20260623T223100Z.md`.
Next exact WBS step: `8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`.

Final valid F065 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F065_obvbulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F065 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F065_obvbulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F065 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F065. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.15 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_15_f064_audit_20260623T222100Z.md`.
Next exact WBS step: `8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`.

Final valid F064 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F064_macdbeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F064 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F064_macdbeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F064 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F064. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.14 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_14_f063_audit_20260623T221200Z.md`.
Next exact WBS step: `8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`.

Final valid F063 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F063_macdbulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F063 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F063_macdbulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F063 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F063. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.13 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_13_f062_audit_20260623T220200Z.md`.
Next exact WBS step: `8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`.

Final valid F062 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F062_rsibeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F062 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F062_rsibeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F062 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F062. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.12 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_12_f061_audit_20260623T215100Z.md`.
Next exact WBS step: `8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`.

Final valid F061 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F061_rsibulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F061 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F061_rsibulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F061 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F061. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.8 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_8_f057_audit_20260623T205000Z.md`.
Next exact WBS step: `8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`.

Final valid F057 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F057_hammer_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F057 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F057_hammer_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F057 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F057. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.7 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_7_f056_audit_20260623T203800Z.md`.
Next exact WBS step: `8.2.8 Run F057_HAMMER_ALLOW large-window candidate`.

Final valid F056 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F056_pinbear_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F056 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F056_pinbear_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F056 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F056. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.6 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_6_f055_audit_20260623T202700Z.md`.
Next exact WBS step: `8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`.

Final valid F055 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F055_pinbull_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F055 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F055_pinbull_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F055 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F055. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.5 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_5_f054_audit_20260623T201700Z.md`.
Next exact WBS step: `8.2.6 Run F055_PINBULL_ALLOW large-window candidate`.

Final valid F054 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F054_insidebar_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F054 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F054_insidebar_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F054 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Do not build an ML package from F054. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.4 Closed
Status: `CLOSED_NO_GO_FIX_APPLIED`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.
Next exact WBS step: `8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`.

Final valid F053 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F053_doji_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F053 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F053_doji_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result: F053 LONG and SHORT both OOS `0.0`, trades `0`; decision `NO_GO_FOR_ML`.

Operational rule: run `-UseTemporaryUnlock` process-pool jobs sequentially. The launcher now rejects a second live temporary unlock before worker start.

Do not build an ML package from F053. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.3 Closed
Status: `CLOSED_VALIDATION_FAIL_NO_ML_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_3_f052_fixed_validation_audit_20260623T194700Z.md`.
Next exact WBS step: continue with the next user-selected passport/action discovery, or define a new validation idea.

Preflight command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.preflight_window --symbol SOLUSDT --timeframe 1m --train-start 2026-05-04 --train-end 2026-05-17 --test-day 2026-05-18 --test-end-day 2026-05-24 --min-train-rows 900 --n-folds 2 --horizons-grid 1,2,3,4,5,6,8,12,16 --layer core
```

OOS contract command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path reports\final_review\oos_backtest_trades_SOLUSDT_1m_2026-05-18_to_2026-05-24_long_only_20260623T194451Z.csv --out-dir reports\qa_gate
```

Result: F052 fixed LONG validation OOS `-5.696708101293968`, trades `1`, goal pass `false`, train gate `false`.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T195125Z.json`.

Do not build an ML package from this validation. Do not approve it for ML. Do not ingest it into ML.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.2 Closed
Status: `CLOSED_POSITIVE_TEST_CANDIDATE_NEEDS_VALIDATION`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_2_f052_audit_20260623T193700Z.md`.
Next exact WBS step: manual decision on validation, draft package approval, or next passport/action discovery.

Final valid F052 LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F052_choch_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid F052 SHORT command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F052_choch_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Do not build an ML package automatically from F052. Do not start ML training.

## Current ML Stage 8 Command 2026-06-23 Step 8.2.1 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_1_f050_audit_20260623T192700Z.md`.
Next exact WBS step: `8.2.2 Run F052_CHOCH_ALLOW large-window candidate`, unless user overrides the target.

Final valid F050 command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F050_bosup_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Prepared F052 command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F052_choch_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Do not build an ML package from F050. Do not start ML training.

## Current ML Stage 8 Command 2026-06-23 Step 8.2 Closed
Status: `CLOSED_NO_GO`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_audit_20260623T191900Z.md`.
Next exact WBS step: manual decision for next passport/action calibration target or revised `8.2` candidate run.

Final valid Optuna command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F051_bosdown_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_cycle_preflight_integration.py tests\test_optuna_search_runtime.py tests\test_ml_alignment_data_windows_audit.py tests\test_ml_trade_dataset_contract.py -q
```

Do not build an ML package from this run. Do not start ML training.

## Current ML Stage 8 Command 2026-06-23 Step 8.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.
Manifest: `configs/ml_large_clean_window_manifest.yaml`.
Next exact WBS step: `8.2 Run Optuna calibration`.

Audit command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_large_clean_window_manifest_audit --manifest-path configs\ml_large_clean_window_manifest.yaml --out-dir reports\qa_gate
```

Do not run ML training yet. Optuna calibration is next.

## Current ML Smoke Command 2026-06-23 Stage 7 Closed
Status: `STAGE_7_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.
Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.
Next exact WBS step: `8.1 Fix large clean window`.

Do not run ML training yet. Stage 8 starts with fixing the larger clean window.

## Current ML Smoke Command 2026-06-23 Step 7.5 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.
Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.
Next exact WBS step: `7.6 Stage 7 closeout`.

Dataset builder command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_approved_trade_dataset_builder --registry-path configs\ml_approved_calibration_packages.yaml --out-dir reports\ml_datasets --dataset-name smoke_stage_7_5_SOLUSDT_1m_20260527_short_only --report-dir reports\qa_gate
```

Dataset contract command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path reports\ml_datasets\smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv --out-dir reports\qa_gate
```

Do not run ML training yet. Stage 7 closeout is next.

## Current ML Smoke Command 2026-06-23 Step 7.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.
Approved package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.
Next exact WBS step: `7.5 Run ML ingest`.

Registry validator command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_approval_registry_validator --registry-path configs\ml_approved_calibration_packages.yaml --out-dir reports\qa_gate
```

Admission status command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_alignment_admission_status_audit --registry-path configs\ml_approved_calibration_packages.yaml --out-dir reports\qa_gate
```

Do not run ML training yet. Dataset builder / ML ingest is next.

## Current ML Smoke Command 2026-06-23 Step 7.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.
Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.
Next exact WBS step: `7.4 Add package to approved registry`.

Contract command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path reports\ml_candidates\smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z\trade_log.csv --out-dir reports\qa_gate
```

Do not run ML training yet. Do not add packages to `approved_packages` without explicit manual approval.

Last final guard: `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T183955Z.json`.

## Current ML Smoke Command 2026-06-23 Step 7.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.
Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.
Next exact WBS step: `7.3 Run package contract audit`.

Contract command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path reports\ml_candidates\smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z\trade_log.csv --out-dir reports\qa_gate
```

Do not run ML training yet. Do not add packages to `approved_packages` without explicit manual approval.

## Current ML Smoke Command 2026-06-23 Step 7.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.
Manifest: `configs/ml_smoke_run_manifest.yaml`.
Next exact WBS step: `7.2 Build test package`.

Validation command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_smoke_window_manifest_audit --manifest-path configs\ml_smoke_run_manifest.yaml --out-dir reports\qa_gate
```

Do not run ML training yet. Do not add packages to `approved_packages` without explicit manual approval.

## Current ML Alignment Command 2026-06-23 Stage 6 Closed
Status: `STAGE_6_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.
Next exact WBS step: `7.1 Smoke run`.

Final checks: focused ML tests `121/121 OK`; all five alignment audits `PASS / NO_APPROVED_PACKAGES`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; reject-log builder `PASS / NO_REJECTIONS`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181511Z.json`.

Do not run ML training yet; smoke run is next.

## Current ML Alignment Command 2026-06-23 Step 6.5 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.
Next exact WBS step: `6.6 Stage 6 closeout`.

Admission status auditor: `src/mlbotnav/ml_alignment_admission_status_audit.py`.

Final checks: new tests `6/6 OK`; focused ML tests `121/121 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_admission_status_audit_20260623T180909527952Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181123Z.json`.

Do not run ML training yet; Stage 6 closeout is next.

## Current ML Alignment Command 2026-06-23 Step 6.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.
Next exact WBS step: `6.5 Check admission status`.

Data windows alignment auditor: `src/mlbotnav/ml_alignment_data_windows_audit.py`.

Final checks: new tests `8/8 OK`; focused ML tests `115/115 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_data_windows_audit_20260623T154607261155Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154759Z.json`.

Do not run ML training yet; Stage 6 alignment audit continues first.

## Current ML Alignment Command 2026-06-23 Step 6.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.
Next exact WBS step: `6.4 Check data windows`.

Calibration params alignment auditor: `src/mlbotnav/ml_alignment_calibration_params_audit.py`.

Final checks: new tests `7/7 OK`; focused ML tests `107/107 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_calibration_params_audit_20260623T154050444104Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154240Z.json`.

Do not run ML training yet; Stage 6 alignment audit continues first.

## Current ML Alignment Command 2026-06-23 Step 6.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.
Next exact WBS step: `6.3 Check calibration params`.

Passport context alignment auditor: `src/mlbotnav/ml_alignment_passport_context_audit.py`.

Final checks: new tests `6/6 OK`; focused ML tests `100/100 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_passport_context_audit_20260623T153553932585Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153741Z.json`.

Do not run ML training yet; Stage 6 alignment audit continues first.

## Current ML Alignment Command 2026-06-23 Step 6.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.
Next exact WBS step: `6.2 Check passport context`.

Run ID alignment auditor: `src/mlbotnav/ml_alignment_run_id_audit.py`.

Final checks: new tests `5/5 OK`; focused ML tests `94/94 OK`; real registry run `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_alignment_run_id_audit_20260623T152715670875Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153207Z.json`.

Do not run ML training yet; Stage 6 alignment audit continues first.

## Current ML Ingest Command 2026-06-23 Stage 5 Closed
Status: `STAGE_5_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.
Next exact WBS step: `6.1 Check run_id alignment`.

Final text_guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.

Do not run ML training yet; Stage 6 alignment audit comes first.

## Current ML Ingest Command 2026-06-23 Step 5.5 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.
Next exact WBS step: `5.6 Stage 5 closeout`.

Reject reason log builder: `src/mlbotnav/ml_rejection_reason_log.py`.

Final checks: registry validator `PASS`; reject-log smoke `PASS / NO_REJECTIONS` at `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.

Do not run ML training yet; Stage 5 closeout is the next strict step.

## Current ML Ingest Command 2026-06-23 Step 5.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.
Next exact WBS step: `5.5 Add rejection reasons`.

Dataset builder: `src/mlbotnav/ml_approved_trade_dataset_builder.py`.

Final checks: registry validator `PASS`; builder smoke `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.

Do not run ML training yet; rejection reasons are the next strict step.

## Current ML Ingest Command 2026-06-23 Step 5.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.
Next exact WBS step: `5.4 Реализовать сборку ML dataset`.

Registry reader: `src/mlbotnav/ml_approved_package_registry_reader.py`.

Final checks: registry validator `PASS`, `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.

Do not run ML training yet; dataset assembly is the next strict step.

## Current ML Ingest Command 2026-06-23 Step 5.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.
Next exact WBS step: `5.3 Реализовать чтение registry`.

Source-policy guard: `src/mlbotnav/ml_ingest_source_policy.py`.

Do not run ML ingest/training yet; registry reading and dataset assembly are not implemented.

## Current ML Ingest Command 2026-06-23 Step 5.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.
Next exact WBS step: `5.2 Запретить прямое чтение Optuna reports`.

Current primary ML training ingest entry point: `src/mlbotnav/pipeline_train_eval.py`.

Do not run ML ingest/training yet; Stage 5 route is not implemented.

## Current ML Approval Registry Command 2026-06-23 Stage 4 Closed
Status: `STAGE_4_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.
Next exact WBS step: `5.1 Найти текущую точку ML ingest`.

Registry remains empty; do not auto-approve ML packages. Stage 5 starts by finding the current ML ingest entry point, not by training or ingesting.

## Current ML Approval Registry Command 2026-06-23 Step 4.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.
Next exact WBS step: `4.5 Закрытие этапа 4`.

Registry remains empty; do not auto-approve ML packages.

## Current ML Approval Registry Command 2026-06-23 Step 4.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.
Next exact WBS step: `4.4 Сделать validator registry`.

Registry remains empty; do not auto-approve ML packages.

## Current ML Approval Registry Command 2026-06-23 Step 4.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.
Next exact WBS step: `4.3 Добавить запреты registry`.

Registry remains empty; do not auto-approve ML packages.

## Current ML Approval Registry Command 2026-06-23 Step 4.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.
Next exact WBS step: `4.2 Описать формат registry`.

Registry remains empty; do not auto-approve ML packages.

## Current ML Candidate Package Command 2026-06-23 Stage 3 Closed
Status: `STAGE_3_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.
Next exact WBS step: `4.1 Создать registry файл`.

Package remains `DRAFT`; do not auto-approve ML packages.

## Current ML Candidate Package Command 2026-06-23 Step 3.6 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.
Next exact WBS step: `3.7 Закрытие этапа 3`.

Package remains `DRAFT`; do not auto-approve ML packages.

## Current ML Candidate Package Command 2026-06-23 Step 3.5 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.
Next exact WBS step: `3.6 Добавить audit.md`.

Package remains `DRAFT`; do not auto-approve ML packages.

## Current ML Candidate Package Command 2026-06-23 Step 3.4 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.
Next exact WBS step: `3.5 Добавить manifest.json`.

Package remains `DRAFT`; do not auto-approve ML packages.

## Current ML Candidate Package Command 2026-06-23 Step 3.3 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.
Next exact WBS step: `3.4 Добавить исходные отчеты`.

Package remains `DRAFT`; do not auto-approve ML packages.

## Current ML Candidate Package Command 2026-06-23 Step 3.2 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.
Next exact WBS step: `3.3 Добавить trade_log.csv`.

Package remains `DRAFT`; do not auto-approve ML packages.

## Current ML Candidate Package Command 2026-06-23 Step 3.1 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.
Next exact WBS step: `3.2 Добавить calibration_package.json`.

Keep package files split by WBS step; do not auto-approve ML packages.

## Current ML Contract Command 2026-06-23 Stage 2 Closed
Status: `STAGE_2_CLOSED_PASS`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.
Next exact WBS step: `3.1 Создать структуру пакета`.

Stage 3 starts package builder work. Do not auto-approve ML packages.

## Current ML Contract Command 2026-06-23 Step 2.8 Closed
Status: `CLOSED_PASS`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.
Next exact WBS step: `2.9 Закрытие этапа 2`.

Do not move to Stage 3 until `2.9` closes Stage 2.

## Current ML Contract Command 2026-06-23 Step 2.7 Closed
Status: `CLOSED_PASS_AFTER_CONTROLLED_TEMP_UNLOCK`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.
Next exact WBS step: `2.8 Проверить OOS CSV`.

Do not move to `2.9` until a fresh `reports/final_review/oos_backtest_trades_*.csv` passes `ml_trade_dataset_contract`.

## Current ML Contract Command 2026-06-23 Step 2.6 Closed
Closed: `2.6 Добавить MAE/MFE`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.
Next exact WBS step: `2.7 Проверить pipeline CSV`.
Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.

## Current ML Contract Command 2026-06-23 Step 2.5 Closed
Closed: `2.5 Добавить hit labels`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.
Next exact WBS step: `2.6 Добавить MAE/MFE`.
Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.

## Current ML Contract Command 2026-06-23 Step 2.4 Closed
Closed: `2.4 Добавить duration labels`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_4_duration_labels_audit_20260623T125816Z.md`.
Next exact WBS step: `2.5 Добавить hit labels`.
Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.

## Current ML Contract Command 2026-06-23 Step 2.1 Closed
Closed: `2.1 Добавить run-level context`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.
Next exact WBS step: `2.2 Добавить passport context`.
Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.

## Current ML Contract Command 2026-06-23 Stage 1 Closed
Closed: `1.7 Закрытие этапа 1`.
Closeout artifact: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.
Next exact WBS step: `2.1 Добавить run-level context`.
Do not start the larger calibration/OOS run yet; Stage 2 must enrich real trade CSV outputs first.

## Current ML Contract Command 2026-06-23 Step 1.6 Closed
Closed: `1.6 Сделать проверку контракта`.
Validator command:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path <trade_log.csv> --out-dir reports\qa_gate
```
Validation artifact: `reports/qa_gate/ml_trade_dataset_contract_step_1_6_audit_20260623T122406Z.md`.
CLI smoke report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T122406Z.json`.
Next exact WBS step: `1.7 Закрытие этапа 1`.

## Current ML Contract Command 2026-06-23
Do not start the 2-week calibration -> 1-week OOS run yet.

Current prerequisite: implement and audit the ML trade dataset contract from `reports/qa_gate/optuna_ml_entry_exit_alignment_audit_20260623T162411Z.md`.

Required before runtime:
1. Row-level CSV context: `action_id`, `passport_id`, `block_id`, `calibration_params_json`.
2. Trade labels: `trade_id`, `bars_in_trade`, `tp_hit`, `sl_hit`, `timeout_hit`, `mae_pct`, `mfe_pct`.
3. JSON-vs-CSV alignment audit.

Clean big-window candidate after those fixes:
```powershell
# conceptual window, use layer core
## Visual Entry v3 no-lookahead 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_no_lookahead_candidates --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\no_lookahead_candidates_rerun --render-top 5
```

Проверенный отчет: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`. В ML ничего не передавать.
# train/calibration: 2026-05-11..2026-05-24
## Visual Entry v3 no-lookahead 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_no_lookahead_candidates --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\no_lookahead_candidates_rerun --render-top 5
```

Проверенный отчет: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`. В ML ничего не передавать.
# test/OOS:          2026-05-25..2026-05-31
## Visual Entry v3 no-lookahead 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_no_lookahead_candidates --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\no_lookahead_candidates_rerun --render-top 5
```

Проверенный отчет: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`. В ML ничего не передавать.
```

## Current Passport Command 2026-06-22T21:16:00Z
Closed: `B025/PATTERN_TRADE_CONTEXT` F082-F083 LONG/SHORT.
Artifact: `reports/qa_gate/b025_pattern_trade_context_f082_f083_audit_20260622T211600Z.md`.
Result: `NO_GO`; no positive tradeful candidate.
Next command pattern: continue strict passport route with the next user-supplied passport as the next `Bxxx/Fxxx` registry block, create isolated passport-action matrix, run LONG and SHORT sequentially, then audit.

## Current Audit Command 2026-06-23
Closed: full F001-F083 passport route audit.
Artifact: `reports/qa_gate/f001_f083_passport_full_audit_20260623.md`.
Result: `WARN_WITH_COMPLETENESS_GAPS`.
Next command pattern: first close completeness gaps (`F024`, planned Density/VPOC `F026/F027/F028/F030/F031/F032`, Level/Range/Channel `F038/F039`) or explicitly mark them non-calibrated; then add active-action backtest hardening before relying on combined runs.

## Active Calibration Commands Override
For calibration-node work, use `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.
The old command sections below are historical unless the new command file explicitly references them.

## Current Active Command 2026-06-04T09:06:15Z
Use `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md` and the active short TZ `docs/CALIBRATION_NODE_CURRENT/TZ_OPTUMA_BRIDGE_CURRENT_2026-06-04_RU.md`.
Closed repairs: `calibration_params` anchor gap, `volume_flow`, `density_profile`, `structure_ta` threshold flags, and FIBO profiles.
Checks: focused tests `95/95 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS`.

## Current Active Command 2026-06-04T09:16:54Z
Use `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md` and the active short TZ `docs/CALIBRATION_NODE_CURRENT/TZ_OPTUMA_BRIDGE_CURRENT_2026-06-04_RU.md`.
Closed repair: `pattern_structure_volume_entry` runtime/matrix wiring.
Checks: focused tests `97/97 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS`; `text_guard PASS`.

## Current Active Command 2026-06-04T10:20:10Z
Do not start `pattern long_only wide` on autopilot.
Current status: dry gate and `long_only narrow` are closed; `long_only medium` completed but CPU max was `97%`.
Next command must first select CPU profile:
1. safer profile: `ProcessWorkers=2`, `SearchWorkers=6`, `SearchWorkersPerProcess=3`;
2. or current profile `3/9/3` with hard-stop on first CPU sample `>85%`;
3. or explicit user approval to tolerate short CPU spikes.

## Current Active Command 2026-06-04T10:30:51Z
Closed: `pattern` block runtime through `long_only` and `short_only`, each `narrow/medium/wide`.
Artifact: `reports/qa_gate/pattern_block06_full_closeout_20260604T103051Z.json`.
CPU policy now: tolerate short spikes; reduce profile only on sustained `>85%` for roughly `2-5` minutes.
Readable report: `reports/qa_gate/pattern_block06_human_readable_20260604T103051Z_RU.md`.
Next command/work item must first repair or verify fallback `calibration_params` propagation because final `best_oos` recorded `selected_calibration_params={}` while search-level candidates had params. After that, rerun/replay block06 from the active current folder, not old chronology.

## Current Active Command 2026-06-03T13:16:59Z
Use `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.
Closed command: `H001 short_only` stack; H001 slot closeout artifact `reports/qa_gate/h001_slot_closeout_20260603T131659Z.json`.
Next command source: `H002 matrix compile`, then `H002 long_only` full stack after compile PASS.
Do not use old chronology, old journals, or old P20xx/P21xx command blocks for the next calibration step.

## Current Active Command 2026-06-03T15:41:33Z
Use `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.
Closed command: `H002 short_only` stack; H002 slot closeout artifact `reports/qa_gate/h002_slot_closeout_20260603T154133Z.json`.
Next command source: `H003 matrix compile`, then `H003 long_only` full stack after compile PASS.
Do not use old chronology, old journals, or old P20xx/P21xx command blocks for the next calibration step.

## Current Active Command 2026-06-03T11:28:24Z
Use `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.
Current calibration runtime chain is closed through `pattern`: `narrow/medium/wide` x `long_only/short_only`, profile `3x3/9`, all launcher runs `OK`.
Closeout artifact: `reports/qa_gate/calibration_node_pattern_closeout_20260603T112654Z.json`.
Last health checks: text_guard `PASS`, readiness freeze preserved, `pip check PASS`.
No production/unfreeze command is active; require a separate new TZ or GO package before production steps.
Do not take the next runtime from old chronology or old P20xx/P21xx sections.

## Current Active Command 2026-06-03T12:18:33Z
Use `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.
Active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_HYPOTHESIS_FEATURE_SWEEP_2026-06-03_RU.md`.
Current slot: `H001`, block `price_volatility`, feature `ret_1`, params `return_lookback`.
Matrix: `configs\calibration_matrices\feature_sweep\h001_price_volatility_ret_1.yaml`.
Compile report: `reports/qa_gate/h001_feature_sweep_matrix_compile_20260603T121833Z.json`.
Next command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\feature_sweep\h001_price_volatility_ret_1.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```
After it, update `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv` and move to `H001 narrow short_only`.

## Current Active Command 2026-06-03T12:25:20Z
Use `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.
Last completed: `H001 narrow long_only`, artifact `reports/qa_gate/h001_narrow_long_only_20260603T122520Z.json`.
Next command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\feature_sweep\h001_price_volatility_ret_1.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```
After it, update the sweep table and move to `H001 medium long_only`.

## Environment
```powershell
Set-Location C:\Users\007\Desktop\MLbotNav
$env:PYTHONPATH='src'
```

## Health Checks
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.readiness --show --write-report true
.\.venv\Scripts\python.exe -m pip check
```

## V3 Package A Runner
```powershell
powershell -ExecutionPolicy Bypass -File .\run_optuna_v3_package_a.ps1 -Mode long_only
powershell -ExecutionPolicy Bypass -File .\run_optuna_v3_package_a.ps1 -Mode short_only
```

## APTuna Process Pool Launcher Pattern
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-29 -TestDate 2026-05-30 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 2 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\optuna_v3_package_a_ah1_long.yaml -UseTemporaryUnlock
```

## APTuna Catalog 3x3 Launcher Pattern
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-29 -TestDate 2026-05-30 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\<matrix>.yaml -UseTemporaryUnlock
```

## P2028 First Smoke Strategy
Use this pattern only after the wiring inventory and matrix slice are fixed:
calibrate on one closed `TrainDate` 1d window, apply/test on the next closed `TestDate` 1d window, first with a narrow grid, then expand to medium/wide after штатная confirmation.

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate <YYYY-MM-DD> -TestDate <YYYY-MM-DD_NEXT_CLOSED_DAY> -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials <SCOUT_OR_WORK_TRIALS> -OptunaTimeoutSec <SCOUT_OR_WORK_TIMEOUT> -CalibrationMatrixPath configs\calibration_matrices\<1d_to_1d_smoke_matrix>.yaml -UseTemporaryUnlock
```

## Catalog Paths
```powershell
Get-ChildItem .\reports\optuna_catalog
Get-ChildItem .\reports\optuna_catalog\index
Get-Content .\docs\TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md
```

## Project State Checks
```powershell
Get-Content .\configs\readiness.yaml
Get-Content .\docs\OPTUNA_GLOBAL_LAUNCH_AUDIT_2026-06-02_RU.md -TotalCount 180
Get-Content .\docs\codex\handoff.md
Get-Content .\docs\codex\todo.md
Get-Content .\reports\qa_gate\p2029_optuna_ordered_execution_roadmap_checkpoint_20260602T091412Z.json
Get-Content .\reports\qa_gate\p2030_step1_wiring_inventory_checkpoint_20260602T092159Z.json
Get-Content .\reports\optuna_catalog\index\p2030_step1_wiring_inventory_20260602T092159Z.json
Get-Content .\reports\qa_gate\p2032_step2_1d1d_smoke_command_set_checkpoint_20260602T092710Z.json
Get-Content .\reports\optuna_catalog\index\p2032_step2_1d1d_smoke_command_set_20260602T092710Z.json
Get-Content .\reports\qa_gate\p2037_step6_1d1d_smoke_triage_20260602T093704Z.json
Get-Content .\reports\qa_gate\p2038_step6_smoke_triage_post_sync_audit_20260602T094006Z.json
```

## P2032 Fixed Smoke Commands
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_full_matrix_v1.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_full_matrix_v1.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## P2039 Fixed Step 7 Medium Commands
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 120 -OptunaTimeoutSec 600 -CalibrationMatrixPath configs\calibration_full_matrix_v1.yaml -CalibrationGridPreset medium -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 120 -OptunaTimeoutSec 600 -CalibrationMatrixPath configs\calibration_full_matrix_v1.yaml -CalibrationGridPreset medium -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## P2044 Fixed Step 8 Wide Commands
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_full_matrix_v1.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_full_matrix_v1.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## P2052 Block01 Price Volatility Narrow Commands
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_01_price_volatility.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_01_price_volatility.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## P2078 Block03 Volume Flow Narrow Commands
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_03_volume_flow.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_03_volume_flow.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## P2091 Block04 Density Profile Narrow Commands
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_04_density_profile.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_04_density_profile.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## P2104 Block05 Structure TA Narrow Commands
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_05_structure_ta.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_05_structure_ta.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## P2117 Block06 Pattern Narrow Commands
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_06_pattern.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 60 -OptunaTimeoutSec 300 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_06_pattern.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## P2133 P2079 Forward Stability
Artifact:
```powershell
Get-Content .\reports\optuna_catalog\index\p2133_p2079_forward_stability_command_set_20260602T112708Z.json
```

Preflight must pass before runtime:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.preflight_window --symbol SOLUSDT --timeframe 1m --train-start 2026-06-01 --train-end 2026-06-01 --test-day 2026-06-02 --test-end-day 2026-06-02 --min-train-rows 900 --n-folds 2 --horizons-grid 1 --layer raw
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.preflight_window --symbol SOLUSDT --timeframe 1m --train-start 2026-06-02 --train-end 2026-06-02 --test-day 2026-06-03 --test-end-day 2026-06-03 --min-train-rows 900 --n-folds 2 --horizons-grid 1 --layer raw
```

Do not run the fixed replay or 3x3 contour commands until both preflights return `PASS`; production/unfreeze remains blocked.

## P2134 P2079 Forward Data Gate
Latest checkpoint:
```powershell
Get-Content .\reports\qa_gate\p2134_p2079_forward_preflight_data_gate_20260602T113136Z.json
```

Current status: `BLOCKED_BY_UTC_CLOSE_AND_DATA`. Do not run runtime until closed raw `2026-06-02` is available and F1 preflight returns `PASS`; F2 additionally requires closed raw `2026-06-03`.

## P2135 P2079 Forward Data Ingest Route
Do not run before `2026-06-03T00:00:00Z`.
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ingest_day --date 2026-06-02 --symbol SOLUSDT --timeframes 1
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.preflight_window --symbol SOLUSDT --timeframe 1m --train-start 2026-06-01 --train-end 2026-06-01 --test-day 2026-06-02 --test-end-day 2026-06-02 --min-train-rows 900 --n-folds 2 --horizons-grid 1 --layer raw
```

Do not run F2 ingest before `2026-06-04T00:00:00Z`.

## P2136 Heartbeat
Automation id: `p2079-f1-data-gate-check`.
Scheduled: `2026-06-03 05:05` Asia/Yekaterinburg.
Scope: verify UTC close, run P2135 F1 ingest route if needed, then F1 preflight only.
Status: `PAUSED` by `P2137` previous-TZ correction. Resume only after V3 Package B closeout or explicit user redirect.

## P2137 Previous V3 TZ Recovery
```powershell
Get-Content .\reports\qa_gate\p2137_previous_tz_recovery_package_b_pointer_20260602T123736Z.json
Get-Content .\docs\TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md
Get-Content .\docs\TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md
```

Current manual pointer: define exact V3 `Package B` slots/catalog command set before runtime. Preserve `3x3`/9-worker profile, bounded Package B, and catalog classification output.

## P2138 Previous TZ Recovery Post-Sync Audit
```powershell
Get-Content .\reports\qa_gate\p2138_previous_tz_recovery_post_sync_audit_20260602T123949Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T123937Z.json
Get-Content .\reports\readiness\readiness_check_20260602T123936Z.json
```

## P2139 Timed Package B Chain
```powershell
Get-Content .\reports\qa_gate\p2139_package_b_timed_step_chain_20260602T124520Z.json
Get-Content .\docs\codex\todo.md
Get-Content .\docs\TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md
```

Current chain starts UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`.
TZ anchor: V3 section 7, `2026-06-02T06:52:50Z`, Package A `NO_CANDIDATE` -> exact Package B slot definition.

## P2140 V3 Package B Inventory
```powershell
Get-Content .\reports\qa_gate\p2140_v3_package_b_inventory_20260602T125900Z.json
Get-Content .\reports\qa_gate\p2024_optuna_v3_package_a_unified_triage_20260602T065019Z.json
Get-Content .\reports\qa_gate\p2025_optuna_v3_package_a_post_audit_20260602T065250Z.json
Get-Content .\reports\qa_gate\p2006_optuna_strict_exec_package_b_triage_20260601T195056Z.json
```

Current next number: `P2141` exact V3 Package B slots. Do not run Package B runtime until `P2142` command-set/dry-run is `PASS`.

## P2141 V3 Package B Exact Slots
```powershell
Get-Content .\reports\qa_gate\p2141_v3_package_b_exact_slots_20260602T130000Z.json
```

Current next number: `P2142` matrix slices and command-set/dry-run artifact only. Runtime remains blocked.

## P2142 V3 Package B Command Set
```powershell
Get-Content .\reports\qa_gate\p2142_v3_package_b_command_set_20260602T130559Z.json
Get-Content .\reports\qa_gate\p2142_dryrun_results_20260602T130400Z.json
```

Matrix slices:
```powershell
Get-Content .\configs\calibration_matrices\optuna_v3_package_b_bh1_long.yaml
Get-Content .\configs\calibration_matrices\optuna_v3_package_b_bh1_short.yaml
Get-Content .\configs\calibration_matrices\optuna_v3_package_b_bh2.yaml
Get-Content .\configs\calibration_matrices\optuna_v3_package_b_bh3.yaml
```

Current next number: `P2143` Package B `long_only` runtime only. Use commands stored in the P2142 artifact. Do not start `short_only`, P2079 forward, production, or unfreeze before `P2143` has an artifact/status.

## P2143 V3 Package B Long Only Runtime
```powershell
Get-Content .\reports\qa_gate\p2143_v3_package_b_long_only_summary_20260602T131035Z.json
Get-Content .\reports\qa_gate\p2143_v3_package_b_long_only_runs_20260602T131035Z.jsonl
Get-Content .\reports\optuna_catalog\neutral\p2143_v3_package_b_long_only_neutral_20260602T131535Z.json
```

Current next number: `P2144` Package B `short_only` runtime only. Use only the `short_only` commands stored in the P2142 artifact, keep external commands sequential, and keep `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, total `3x3`/9 workers. Do not start P2079 forward, production, or unfreeze.

## P2144 V3 Package B Short Only Runtime
```powershell
Get-Content .\reports\qa_gate\p2144_v3_package_b_short_only_summary_20260602T132020Z.json
Get-Content .\reports\qa_gate\p2144_v3_package_b_short_only_runs_20260602T132020Z.jsonl
Get-Content .\reports\optuna_catalog\neutral\p2144_v3_package_b_short_only_neutral_20260602T132420Z.json
```

Current next number: `P2145` unified Package B triage only. Merge P2143 and P2144 results, classify Package B, and do not start P2079 forward, production, or unfreeze.

## P2145 V3 Package B Unified Triage
```powershell
Get-Content .\reports\qa_gate\p2145_v3_package_b_unified_triage_20260602T132830Z.json
```

Current next number: `P2146` Package B post-sync audit/docs sync only. Run text_guard, readiness, pip check, and artifact parse. Do not start P2079 forward, production, or unfreeze.

## P2146 V3 Package B Post-Sync Audit
```powershell
Get-Content .\reports\qa_gate\p2146_v3_package_b_post_sync_audit_20260602T133021Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T133021Z.json
Get-Content .\reports\readiness\readiness_check_20260602T133020Z.json
```

Current next number: `P2147` transition decision after Package B closeout. Do not start P2079 forward, production, or unfreeze.

## P2147 V3 Package B Closeout Transition
```powershell
Get-Content .\reports\qa_gate\p2147_v3_package_b_closeout_transition_20260602T133330Z.json
```

Current next item after this chain: final V3 `NO_GO` decision package / closeout note. No Package B runtime remains. Do not start P2079 forward, production, or unfreeze.

## P2148 V3 Final NO_GO Decision
```powershell
Get-Content .\reports\qa_gate\p2148_v3_final_no_go_decision_20260602T133600Z.json
```

Current next number: `P2149` final post-sync audit after V3 `NO_GO` decision. Do not start runtime, P2079 forward, production, or unfreeze.

## P2149 V3 Final NO_GO Post-Sync Audit
```powershell
Get-Content .\reports\qa_gate\p2149_v3_final_no_go_post_sync_audit_20260602T133845Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T133845Z.json
Get-Content .\reports\readiness\readiness_check_20260602T133844Z.json
```

Current pointer: V3 chain closed as `NO_GO`. Do not start runtime, P2079 forward, production, or unfreeze without an explicit new numbered task.

## P2150 Post-V3 Catalog/Forward Boundary
```powershell
Get-Content .\reports\qa_gate\p2150_post_v3_catalog_forward_boundary_20260602T134150Z.json
```

Current next number: `P2151` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2151 P2079 F1 Data Gate Pre-Close Check
```powershell
Get-Content .\reports\qa_gate\p2151_p2079_f1_data_gate_preclose_check_20260602T141711Z.json
```

Current next number: `P2152` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2152 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2152_p2079_f1_data_gate_utc_close_recheck_20260602T142042Z.json
```

Current next number: `P2153` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2153 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2153_p2079_f1_data_gate_utc_close_recheck_20260602T142319Z.json
```

Current next number: `P2154` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2154 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2154_p2079_f1_data_gate_utc_close_recheck_20260602T142553Z.json
```

Current next number: `P2155` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2155 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2155_p2079_f1_data_gate_utc_close_recheck_20260602T142920Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T143136Z.json
Get-Content .\reports\readiness\readiness_check_20260602T143136Z.json
```

Current next number: `P2156` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2156 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2156_p2079_f1_data_gate_utc_close_recheck_20260602T143308Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T143445Z.json
Get-Content .\reports\readiness\readiness_check_20260602T143445Z.json
```

Current next number: `P2157` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2157 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2157_p2079_f1_data_gate_utc_close_recheck_20260602T143625Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T143926Z.json
Get-Content .\reports\readiness\readiness_check_20260602T143925Z.json
```

Current next number: `P2158` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2158 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2158_p2079_f1_data_gate_utc_close_recheck_20260602T144030Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T144209Z.json
Get-Content .\reports\readiness\readiness_check_20260602T144207Z.json
```

Current next number: `P2159` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2159 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2159_p2079_f1_data_gate_utc_close_recheck_20260602T144317Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T144457Z.json
Get-Content .\reports\readiness\readiness_check_20260602T144456Z.json
```

Current next number: `P2160` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2160 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2160_p2079_f1_data_gate_utc_close_recheck_20260602T144607Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T144742Z.json
Get-Content .\reports\readiness\readiness_check_20260602T144742Z.json
```

Current next number: `P2161` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2161 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2161_p2079_f1_data_gate_utc_close_recheck_20260602T144943Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T145122Z.json
Get-Content .\reports\readiness\readiness_check_20260602T145121Z.json
```

Current next number: `P2162` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2162 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2162_p2079_f1_data_gate_utc_close_recheck_20260602T145228Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T145406Z.json
Get-Content .\reports\readiness\readiness_check_20260602T145405Z.json
```

Current next number: `P2163` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2163 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2163_p2079_f1_data_gate_utc_close_recheck_20260602T145522Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T145702Z.json
Get-Content .\reports\readiness\readiness_check_20260602T145701Z.json
```

Historical next number before closing this step was `P2164` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2164 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2164_p2079_f1_data_gate_utc_close_recheck_20260602T150019Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T150225Z.json
Get-Content .\reports\readiness\readiness_check_20260602T150225Z.json
```

Historical next number before closing this step was `P2165` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2165 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2165_p2079_f1_data_gate_utc_close_recheck_20260602T150436Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T150617Z.json
Get-Content .\reports\readiness\readiness_check_20260602T150617Z.json
```

Historical next number before closing this step was `P2166` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2166 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2166_p2079_f1_data_gate_utc_close_recheck_20260602T150732Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T150915Z.json
Get-Content .\reports\readiness\readiness_check_20260602T150915Z.json
```

Historical next number before closing this step was `P2167` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2167 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2167_p2079_f1_data_gate_utc_close_recheck_20260602T151030Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T151314Z.json
Get-Content .\reports\readiness\readiness_check_20260602T151314Z.json
```

Historical next number before closing this step was `P2168` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2168 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2168_p2079_f1_data_gate_utc_close_recheck_20260602T151532Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T151714Z.json
Get-Content .\reports\readiness\readiness_check_20260602T151713Z.json
```

Historical next number before closing this step was `P2169` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2169 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2169_p2079_f1_data_gate_utc_close_recheck_20260602T151826Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T152005Z.json
Get-Content .\reports\readiness\readiness_check_20260602T152004Z.json
```

Historical next number before closing this step was `P2170` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2170 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2170_p2079_f1_data_gate_utc_close_recheck_20260602T152120Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T152306Z.json
Get-Content .\reports\readiness\readiness_check_20260602T152305Z.json
```

Historical next number before closing this step was `P2171` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2171 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2171_p2079_f1_data_gate_utc_close_recheck_20260602T152559Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T152826Z.json
Get-Content .\reports\readiness\readiness_check_20260602T152825Z.json
```

Historical next number before closing this step was `P2172` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2172 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2172_p2079_f1_data_gate_utc_close_recheck_20260602T152940Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T153127Z.json
Get-Content .\reports\readiness\readiness_check_20260602T153126Z.json
```

Historical next number before closing this step was `P2173` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2173 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2173_p2079_f1_data_gate_utc_close_recheck_20260602T153242Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T153429Z.json
Get-Content .\reports\readiness\readiness_check_20260602T153428Z.json
```

Historical next number before closing this step was `P2174` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2174 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2174_p2079_f1_data_gate_utc_close_recheck_20260602T153532Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T153717Z.json
Get-Content .\reports\readiness\readiness_check_20260602T153716Z.json
```

Historical next number before closing this step was `P2175` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2175 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2175_p2079_f1_data_gate_utc_close_recheck_20260602T153821Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T154009Z.json
Get-Content .\reports\readiness\readiness_check_20260602T154008Z.json
```

Historical next number before closing this step was `P2176` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2176 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2176_p2079_f1_data_gate_utc_close_recheck_20260602T154114Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T154333Z.json
Get-Content .\reports\readiness\readiness_check_20260602T154333Z.json
```

Historical next number before closing this step was `P2177` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2177 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2177_p2079_f1_data_gate_utc_close_recheck_20260602T154446Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T154634Z.json
Get-Content .\reports\readiness\readiness_check_20260602T154633Z.json
```

Historical next number before closing this step was `P2178` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2178 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2178_p2079_f1_data_gate_utc_close_recheck_20260602T154806Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T155005Z.json
Get-Content .\reports\readiness\readiness_check_20260602T155004Z.json
```

Historical next number before closing this step was `P2179` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2179 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2179_p2079_f1_data_gate_utc_close_recheck_20260602T155119Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T155304Z.json
Get-Content .\reports\readiness\readiness_check_20260602T155304Z.json
```

Historical next number before closing this step was `P2180` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2180 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2180_p2079_f1_data_gate_utc_close_recheck_20260602T155433Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T155722Z.json
Get-Content .\reports\readiness\readiness_check_20260602T155722Z.json
```

Historical next number before closing this step was `P2181` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2181 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2181_p2079_f1_data_gate_utc_close_recheck_20260602T155851Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T160102Z.json
Get-Content .\reports\readiness\readiness_check_20260602T160101Z.json
```

Historical next number before closing this step was `P2182` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2182 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2182_p2079_f1_data_gate_utc_close_recheck_20260602T160218Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T160404Z.json
Get-Content .\reports\readiness\readiness_check_20260602T160403Z.json
```

Historical next number before closing this step was `P2183` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2183 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2183_p2079_f1_data_gate_utc_close_recheck_20260602T160516Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T160705Z.json
Get-Content .\reports\readiness\readiness_check_20260602T160704Z.json
```

Historical next number before closing this step was `P2184` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2184 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2184_p2079_f1_data_gate_utc_close_recheck_20260602T160848Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T161033Z.json
Get-Content .\reports\readiness\readiness_check_20260602T161033Z.json
```

Historical next number before closing this step was `P2185` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2185 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2185_p2079_f1_data_gate_utc_close_recheck_20260602T161150Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T161336Z.json
Get-Content .\reports\readiness\readiness_check_20260602T161335Z.json
```

Historical next number before closing this step was `P2186` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2186 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2186_p2079_f1_data_gate_utc_close_recheck_20260602T161530Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T161633Z.json
Get-Content .\reports\readiness\readiness_check_20260602T161632Z.json
```

Historical next number before closing this step was `P2187` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2187 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2187_p2079_f1_data_gate_utc_close_recheck_20260602T161909Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T161942Z.json
Get-Content .\reports\readiness\readiness_check_20260602T161941Z.json
```

Historical next number before closing this step was `P2188` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2188 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2188_p2079_f1_data_gate_utc_close_recheck_20260602T162257Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T162331Z.json
Get-Content .\reports\readiness\readiness_check_20260602T162331Z.json
```

Historical next number before closing this step was `P2189` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2189 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2189_p2079_f1_data_gate_utc_close_recheck_20260602T162548Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T162627Z.json
Get-Content .\reports\readiness\readiness_check_20260602T162626Z.json
```

Historical next number before closing this step was `P2190` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2190 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2190_p2079_f1_data_gate_utc_close_recheck_20260602T163021Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T163046Z.json
Get-Content .\reports\readiness\readiness_check_20260602T163046Z.json
```

Historical next number before closing this step was `P2191` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2191 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2191_p2079_f1_data_gate_utc_close_recheck_20260602T163325Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T163350Z.json
Get-Content .\reports\readiness\readiness_check_20260602T163349Z.json
```

Historical next number before closing this step was `P2192` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2192 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2192_p2079_f1_data_gate_utc_close_recheck_20260602T163604Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T163630Z.json
Get-Content .\reports\readiness\readiness_check_20260602T163629Z.json
```

Historical next number before closing this step was `P2193` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2193 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2193_p2079_f1_data_gate_utc_close_recheck_20260602T163839Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T163903Z.json
Get-Content .\reports\readiness\readiness_check_20260602T163902Z.json
```

Historical next number before closing this step was `P2194` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2194 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2194_p2079_f1_data_gate_utc_close_recheck_20260602T164109Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T164133Z.json
Get-Content .\reports\readiness\readiness_check_20260602T164132Z.json
```

Historical next number before closing this step was `P2195` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## P2195 P2079 F1 UTC-Close Recheck
```powershell
Get-Content .\reports\qa_gate\p2195_p2079_f1_data_gate_utc_close_recheck_20260602T164502Z.json
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260602T164527Z.json
Get-Content .\reports\readiness\readiness_check_20260602T164526Z.json
```

Current next number: `P2196` after `2026-06-03T00:00:00Z` only. Verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. Do not run P2079 runtime, F2, production, or unfreeze.

## Quick Structural Audit
```powershell
Get-Content .\reports\qa_gate\quick_structural_audit_framework_20260602T182715Z.json
```

Structural big-window catalog validation can be opened on already closed historical data as a separate command-set/dry-run chain. Keep P2079 forward, production, and unfreeze gates unchanged.

## Dangerous Commands
1. Do not run `git reset --hard`.
2. Do not run `git checkout --`.
3. Do not delete reports, logs, sessions, data, models, caches, or artifacts without direct user approval.
4. Do not move or clean project history without backup and approval.

## Successfully Run Recently
1. `run_optuna_v3_package_a.ps1 -Mode long_only`
2. `run_optuna_v3_package_a.ps1 -Mode short_only`
3. `mlbotnav.text_guard`
4. `mlbotnav.readiness --show --write-report true`
5. `pip check`
6. Created full calibration catalog checkpoint `P2026`
7. `mlbotnav.text_guard` after P2026 -> `PASS`
8. `mlbotnav.readiness --show --write-report true` after P2026 -> freeze preserved
9. `pip check` after P2026 -> `No broken requirements found.`

## Hard Structural Audit
```powershell
Get-Content .\reports\qa_gate\hard_structural_audit_features_hypotheses_20260602T191609Z.md
Get-Content .\reports\optuna_catalog\index\p2030_step1_wiring_inventory_20260602T092159Z.json
Get-Content .\reports\optuna_catalog\index\p2130_block_level_catalog_ranking_20260602T111745Z.json
Get-Content .\reports\qa_gate\p2131_block_level_forward_boundary_20260602T111745Z.json
```

Use this audit before writing the new TZ. Do not delete chronology; archive or supersede it instead.

## P2196A Optuna Battle Readiness Audit
```powershell
Get-Content .\reports\qa_gate\p2196a_optuna_battle_readiness_audit_20260603T060919Z.md
Get-Content .\reports\qa_gate\hard_structural_audit_features_hypotheses_20260602T191609Z.md
Get-Content .\reports\optuna_catalog\index\structural_big_window_command_set_20260602T191737Z.json
Get-Content .\reports\qa_gate\structural_big_window_runtime_stopped_20260602T192317Z.json
```

Current next number is `P2196B`: implement/audit strict block-hypothesis compatibility before battle runtime. Production/unfreeze remains blocked.

## P2196B Volume/Volatility Context Wiring
Artifact:
```powershell
Get-Content .\reports\qa_gate\p2196b_volume_context_wiring_audit_20260603T065821Z.json
```

Focused tests:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Current status: `PASS_CONTEXT_WIRING`; next P2196B work is strict hypothesis/trend compatibility filtering before battle runtime.

## P2196B/P2196C Strict Battle Readiness
Artifacts:
```powershell
Get-Content .\reports\qa_gate\p2196b_strict_hypothesis_filter_full_audit_20260603T100404Z.json
Get-Content .\reports\qa_gate\preflight_window_20260603T100432Z.json
Get-Content .\reports\optuna_catalog\index\p2196c_strict_command_set_20260603T100504Z.json
```

Focused tests:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_optuna_space_constraints tests.test_optuna_search_runtime tests.test_backtest_fields
```

Current next executable step:
strict P2079-equivalent check, block03 `volume_flow`, grid `narrow`, mode `long_only`, train `2026-05-29..2026-05-31`, test `2026-06-01`, profile `3x3/9`. Use the exact command row from the P2196C artifact and remove `-DryRun` only when intentionally starting runtime.

Post-sync checks:
```powershell
Get-Content .\reports\qa_gate\recovery_r5_text_guard_20260603T100856Z.json
Get-Content .\reports\readiness\readiness_check_20260603T100856Z.json
.\.venv\Scripts\python.exe -m pip check
```

Forward file check:
```powershell
Test-Path data\raw\bybit_ohlcv\dt=2026-06-02\tf=1m\symbol=SOLUSDT\part-final.csv
Test-Path data\core\bybit_ohlcv\dt=2026-06-02\tf=1m\symbol=SOLUSDT\part-final.csv
```

## P2196D Runtime Result
Best summary:
```powershell
Get-Content .\reports\adaptive\long_only_pool_20260603t101450z_w3\adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T101454Z.json
```

Result: launcher `OK`, best OOS `+1.5266529420731034%`, trades `1`, saved as `TOP_EXPERIMENTAL`; no production/latest publication because train gate failed.

## P2196E Volume Flow Narrow Short Result
Best summary:
```powershell
Get-Content .\reports\adaptive\short_only_pool_20260603t102158z_w3\adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T102202Z.json
```

Focused tests after runtime fix:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_adaptive_candidate_pick tests.test_optuna_space_constraints tests.test_optuna_search_runtime tests.test_backtest_fields
```

Result: first attempt `PARTIAL_FAIL` due empty/unreadable search report JSON; fixed in `src/mlbotnav/adaptive_auto_train.py`; rerun launcher `OK`, all 3 workers exit `0`, best OOS `0%`, trades `0`, no candidate.

## H006 Pattern Replay After Params/Retry Fix
Readable result:
```powershell
Get-Content .\reports\qa_gate\pattern_block06_replay_after_param_retry_fix_20260604T110012Z_RU.md
Get-Content .\reports\qa_gate\pattern_block06_replay_after_param_retry_fix_20260604T110012Z.json
```

Focused validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\adaptive_auto_train.py .\tests\test_adaptive_candidate_pick.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_adaptive_candidate_pick tests.test_pipeline_train_eval_gate_overrides tests.test_optuna_search_runtime tests.test_backtest_fields
```

Replay command shape:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_06_pattern.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: H006 `pattern` replay completed `long_only` and `short_only` across `narrow/medium/wide`; all 6 launchers `OK`; final params present `6/6`; no positive candidate.

## H006 Grid Edge Coverage Audit Fix
Readable result:
```powershell
Get-Content .\reports\qa_gate\h006_grid_edge_coverage_audit_fix_20260604T111552Z_RU.md
Get-Content .\reports\optuna\long_only\grid_edge_coverage_audit_20260604T111552Z.json
```

Focused validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\optuna_search_candidate.py .\src\mlbotnav\adaptive_auto_train.py .\tests\test_optuna_search_runtime.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_adaptive_candidate_pick tests.test_pipeline_train_eval_gate_overrides tests.test_optuna_search_runtime tests.test_optuna_space_constraints tests.test_backtest_fields
```

Runtime smoke command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 24 -OptunaTimeoutSec 180 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_06_pattern.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: launcher `OK`; new search report includes `optuna_artifacts.grid_edge_coverage_audit_path`; artifact counts pruned trials too.

## H006 Core Grid Edge Forcing Fix
Readable result:
```powershell
Get-Content .\reports\qa_gate\h006_core_grid_edge_forcing_fix_20260604T113102Z_RU.md
Get-Content .\reports\optuna\long_only\grid_edge_coverage_audit_20260604T113102Z.json
```

Runtime smoke command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 24 -OptunaTimeoutSec 180 -CalibrationMatrixPath configs\calibration_matrices\catalog_blocks\catalog_block_06_pattern.yaml -CalibrationGridPreset narrow -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_adaptive_candidate_pick tests.test_pipeline_train_eval_gate_overrides tests.test_optuna_search_runtime tests.test_optuna_space_constraints tests.test_backtest_fields
```

Result: launcher `OK`; core coverage in edge audit `5/5 PASS`; profile coverage remains budget-dependent and needs full replay for final proof.

## H006 Full Replay Edge Coverage Pass
Readable result:
```powershell
Get-Content .\reports\qa_gate\h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z_RU.md
Get-Content .\reports\qa_gate\h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z.json
```

Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_adaptive_candidate_pick tests.test_pipeline_train_eval_gate_overrides tests.test_optuna_search_runtime tests.test_optuna_space_constraints tests.test_backtest_fields
```

Result: H006 LONG/SHORT x `narrow/medium/wide` launchers `6/6 OK`; combined edge audit profile `18/18`, core `5/5` in every grid; no positive trading candidate.

## CASCADE_BLOCK_CALIBRATION Rule
No runtime command was launched for this step.

Active rule is documented here:
```powershell
Get-Content .\docs\CALIBRATION_NODE_CURRENT\TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md
Get-Content .\docs\CALIBRATION_NODE_CURRENT\CURRENT_STATUS_RU.md
```

Target command shape for future implementation/run planning:
```text
block -> LONG cascade: wide -> best tradeful -> medium around best -> best tradeful -> narrow around best
block -> SHORT cascade: wide -> best tradeful -> medium around best -> best tradeful -> narrow around best
```

## C001 Block 01 LONG Wide Runtime
Command executed:
```powershell
$env:PYTHONPATH='src'
$matrix = 'configs\calibration_matrices\catalog_blocks\catalog_block_01_price_volatility.yaml'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Readable result:
```powershell
Get-Content .\reports\qa_gate\c001_block01_price_volatility_long_wide_20260604T144429Z_RU.md
```

Result:
`OK`, workers `3/3`, best OOS `-37.0372%`, trades `9`, tradeful negative.

## F001 Strict Passport Validation
Commands executed:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\validation.py .\src\mlbotnav\optuna_search_candidate.py .\src\mlbotnav\backtest.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_structure_pattern_parity
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_optuna_search_runtime
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
```

Result:
`py_compile PASS`; focused tests `25/25 OK`; Optuna runtime tests `65/65 OK`; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T091458Z.json`.

## RET_N F001-F005 Passport Family Validation
Commands executed:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
```

Matrix compile check shape:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
    'configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml',
    'configs/calibration_matrices/passport_actions/F002_ret3_entry_filter.yaml',
    'configs/calibration_matrices/passport_actions/F003_ret6_entry_filter.yaml',
    'configs/calibration_matrices/passport_actions/F004_ret12_entry_filter.yaml',
    'configs/calibration_matrices/passport_actions/F005_ret24_entry_filter.yaml',
]:
    matrix = load_calibration_matrix(root, rel_path=rel)
    space = compile_optuna_space(matrix, contour_id='long_only', min_enabled_blocks=1, grid_preset='wide')
    print(rel, sorted(space['profiles'].keys()))
'@ | .\.venv\Scripts\python.exe -
```

Result:
`py_compile PASS`; focused tests `96/96 OK`; F001-F005 matrix compile `PASS`; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T112135Z.json`.

## RET_N Max Anchor Fix Validation
Commands executed:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_optuna_space_constraints tests.test_optuna_search_runtime tests.test_dataset_inference_mode tests.test_backtest_fields
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
m = load_calibration_matrix(Path.cwd(), rel_path='configs/calibration_matrices/passport_actions/F003_ret6_entry_filter.yaml')
s = compile_optuna_space(m, contour_id='long_only', min_enabled_blocks=1, grid_preset='wide')
vals = s['profiles']['F003_thr_pct']['values']
print(len(vals), vals[0], vals[-3:], 1.20 in vals)
'@ | .\.venv\Scripts\python.exe -
```

Result:
`py_compile PASS`; focused tests `98/98 OK`; F003 proof `60 0.03 [1.17, 1.19, 1.2] True`.

## B001 RET_N Ladder Tournament
Generate 31 clean combo matrices:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.b001_ret_n_ladder_tournament --grid-preset wide
```

Validate code/tests:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\optuna_space.py .\src\mlbotnav\b001_ret_n_ladder_tournament.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_b001_ret_n_ladder_tournament tests.test_optuna_space_constraints tests.test_dataset_inference_mode tests.test_backtest_fields
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_b001_ret_n_ladder_tournament tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

DryRun first 2 combos:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -OptunaTrials 12 -OptunaTimeoutSec 120 -MaxCombos 2 -DryRun
```

Smoke first combo:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -OptunaTrials 6 -OptunaTimeoutSec 120 -MaxCombos 1 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -UseTemporaryUnlock
```

Baseline B001 solo-selection LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result:
generated manifest `reports/qa_gate/b001_ret_n_ladder_matrices_20260622T115638Z/manifest.json`; DryRun report `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115811Z.json`; smoke report `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115930Z.json`; focused tests `35/35 OK`; extended focused tests `83/83 OK`.

## B001 Solo Selection Guard
Default runner now selects only solo rows `1..5`:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -OptunaTrials 12 -OptunaTimeoutSec 120 -DryRun
```

Diagnostic-only full combination run requires explicit flag:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -EndIndex 31 -EnableCombinationTournament -DryRun
```

Without `-EnableCombinationTournament`, `EndIndex 31` is blocked by design.

## F012 RSI14 Passport Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
m = load_calibration_matrix(root, rel_path='configs/calibration_matrices/passport_actions/F012_rsi14_combined_entry_filter.yaml')
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()))
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime commands:
```powershell
$env:PYTHONPATH='src'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F012_rsi14_combined_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F012_rsi14_combined_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: `LONG 0%/0 trades`, `SHORT -47.5754123715459%/22 trades`, final `NO_GO`; audit `reports/qa_gate/f012_rsi14_combined_long_short_audit_20260622T144750Z.json`.

## MACD F013-F015 Passport Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\optuna_search_candidate.py src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_optuna_search_runtime tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F013_macd_line_1m_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F014_macd_signal_1m_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F015_macd_hist_1m_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only', 'short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime commands:
```powershell
$env:PYTHONPATH='src'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F013_macd_line_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F013_macd_line_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F014_macd_signal_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F014_macd_signal_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F015_macd_hist_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F015_macd_hist_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: all launches `OK`; final `NO_GO`; audit `reports/qa_gate/macd_f013_f015_long_short_audit_20260622T151954Z.json`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T152122Z.json`.

## F016 ADX14 Passport Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
m = load_calibration_matrix(root, rel_path='configs/calibration_matrices/passport_actions/F016_adx14_1m_entry_filter.yaml')
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime commands:
```powershell
$env:PYTHONPATH='src'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F016_adx14_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F016_adx14_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: `LONG -13.43232421418481%/3 trades`, `SHORT -28.526707456698695%/13 trades`, final `NO_GO`; audit `reports/qa_gate/f016_adx14_long_short_audit_20260622T153403Z.json`.

## STOCH F017-F018 Passport Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
m = load_calibration_matrix(root, rel_path='configs/calibration_matrices/passport_actions/F017_F018_stoch14_combined_entry_filter.yaml')
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime commands:
```powershell
$env:PYTHONPATH='src'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F017_F018_stoch14_combined_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F017_F018_stoch14_combined_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: `LONG -84.05333161848922%/51 trades`, `SHORT -17.53680624691214%/6 trades`, final `NO_GO`; audit `reports/qa_gate/stoch_f017_f018_long_short_audit_20260622T154340Z.json`.

## VOLUME F019-F021 Passport Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Clean sequential runtime commands:
```powershell
$env:PYTHONPATH='src'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F019_vol_chg_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F019_vol_chg_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F020_vol_z20_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F020_vol_z20_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F021_delta_volume_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F021_delta_volume_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/volume_f019_f021_long_short_audit_20260622T160207Z.json`. F021 was rerun after TRUE_DELTA missing-side-volume fix.

## F001 Strict LONG 1d/1d Runtime
Command executed after OOS runtime-action bridge fix:
```powershell
$env:PYTHONPATH='src'
$matrix = 'configs\calibration_matrices\feature_sweep\h001_price_volatility_ret_1.yaml'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Validation before rerun:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\oos_evaluate.py .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\validation.py .\src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_pipeline_train_eval_gate_overrides tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_search_runtime
```

Result:
launcher `OK`, workers `3/3`, best worker `w1`, best OOS `-5.352332468117016%`, trades `3`, `F001_RET1_ALLOW_gate_active=true`, artifact `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`.

## F022 OBV Slope 5 Passport Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
m = load_calibration_matrix(root, rel_path='configs/calibration_matrices/passport_actions/F022_obv_slope5_1m_entry_filter.yaml')
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime commands:
```powershell
$env:PYTHONPATH='src'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F022_obv_slope5_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F022_obv_slope5_1m_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: `LONG 0.000000%/0 trades`, `SHORT -17.47906713400207%/3 trades`, final `NO_GO`; audit `reports/qa_gate/f022_obv_slope5_long_short_audit_20260622T162356Z.json`.

## F023 MFI14 Passport Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
m = load_calibration_matrix(root, rel_path='configs/calibration_matrices/passport_actions/F023_mfi14_1m_combined_entry_filter.yaml')
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime commands:
```powershell
$env:PYTHONPATH='src'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F023_mfi14_1m_combined_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F023_mfi14_1m_combined_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: `LONG -4.474396882494847%/1 trade`, `SHORT -20.54653686623259%/6 trades`, final `NO_GO`; audit `reports/qa_gate/f023_mfi14_long_short_audit_20260622T163809Z.json`.

## DENSITY/VPOC Block A F025/F029/F033/F034 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F025_vpocdist60_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F029_vpocdist240_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F033_vpocdrift20_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F034_clusterratio_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$env:PYTHONPATH='src'
$matrices = @(
  'configs\calibration_matrices\passport_actions\F025_vpocdist60_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F029_vpocdist240_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F033_vpocdrift20_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F034_clusterratio_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/density_vpoc_block_a_f025_f029_f033_f034_audit_20260622T165812Z.json`. Block B/C from the same passport file were not run yet.

## LEVEL/RANGE/CHANNEL Block A F035/F036/F037 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F035_supportdist_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F036_resdist_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F037_levelstrength_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$env:PYTHONPATH='src'
$matrices = @(
  'configs\calibration_matrices\passport_actions\F035_supportdist_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F036_resdist_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F037_levelstrength_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/level_range_channel_block_a_f035_f036_f037_audit_20260622T171500Z.json`. F038/F039 from the same passport file were not run yet.

## FIBONACCI_GRID F040/F041 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F040_fib0382dist_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F041_fib0618dist_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$env:PYTHONPATH='src'
$matrices = @(
  'configs\calibration_matrices\passport_actions\F040_fib0382dist_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F041_fib0618dist_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/fibonacci_grid_f040_f041_long_short_audit_20260622T173112Z.json`.

## ENTRY_QUALITY_CONTEXT F042-F044 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode tests.test_backtest_fields tests.test_optuna_space_constraints tests.test_optuna_search_runtime
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F044_rrcontext_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F042_tpcontext_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F043_slcontext_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$env:PYTHONPATH='src'
$matrices = @(
  'configs\calibration_matrices\passport_actions\F044_rrcontext_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F042_tpcontext_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F043_slcontext_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/entry_quality_context_f042_f044_long_short_audit_20260622T175033Z_RU.md`.

## BREAKOUT_RETEST F045-F049 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_engine.py src\mlbotnav\optuna_objective.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_breakout_retest_passport_actions_emit_runtime_gates tests.test_backtest_fields.BacktestFieldsTests.test_breakout_retest_gate_uses_passport_action_columns tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F048_swinghighbreak_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F049_swinglowbreak_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F045_breakout_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F047_retest_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F046_falsebreak_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$matrices = @(
  'configs/calibration_matrices/passport_actions/F048_swinghighbreak_entry_filter.yaml',
  'configs/calibration_matrices/passport_actions/F049_swinglowbreak_entry_filter.yaml',
  'configs/calibration_matrices/passport_actions/F045_breakout_entry_filter.yaml',
  'configs/calibration_matrices/passport_actions/F047_retest_entry_filter.yaml',
  'configs/calibration_matrices/passport_actions/F046_falsebreak_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/b017_breakout_retest_f045_f049_audit_20260622T181600Z.md`.

## MARKET_STRUCTURE F050-F052 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_engine.py src\mlbotnav\optuna_objective.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_market_structure_passport_actions_emit_runtime_gates tests.test_backtest_fields.BacktestFieldsTests.test_market_structure_gate_uses_passport_action_columns tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F050_bosup_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F051_bosdown_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F052_choch_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$matrices = @(
  'configs/calibration_matrices/passport_actions/F050_bosup_entry_filter.yaml',
  'configs/calibration_matrices/passport_actions/F051_bosdown_entry_filter.yaml',
  'configs/calibration_matrices/passport_actions/F052_choch_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: `F051 SHORT` is `POSITIVE_TEST_CANDIDATE`; audit `reports/qa_gate/b018_market_structure_f050_f052_audit_20260622T183500Z.md`.

## F051 SHORT Multi-Day Validation Runtime
Runtime:
```powershell
$windows = @(
  @{Train='2026-05-28'; Test='2026-05-29'},
  @{Train='2026-05-29'; Test='2026-05-30'},
  @{Train='2026-05-30'; Test='2026-05-31'}
)
foreach ($w in $windows) {
  powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate $w.Train -TestDate $w.Test -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F051_bosdown_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
}
```

Result: `F051 SHORT` failed multi-day validation; audit `reports/qa_gate/f051_short_multiday_validation_audit_20260623T091000Z.md`.

## CANDLE_PATTERNS F053-F060 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_engine.py src\mlbotnav\optuna_objective.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_candle_pattern_passport_actions_emit_runtime_gates tests.test_backtest_fields.BacktestFieldsTests.test_candle_pattern_gate_uses_passport_action_columns tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F055_pinbull_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F056_pinbear_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F059_engulfbull_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F060_engulfbear_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F057_hammer_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F058_shootingstar_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F054_insidebar_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F053_doji_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$matrices = @(
  'configs\calibration_matrices\passport_actions\F055_pinbull_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F056_pinbear_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F059_engulfbull_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F060_engulfbear_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F057_hammer_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F058_shootingstar_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F054_insidebar_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F053_doji_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/b019_candle_patterns_f053_f060_audit_20260622T190530Z.md`.

## DIVERGENCE_PATTERNS F061-F066 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_engine.py src\mlbotnav\optuna_objective.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_divergence_pattern_passport_actions_emit_runtime_gates tests.test_backtest_fields.BacktestFieldsTests.test_divergence_pattern_gate_uses_passport_action_columns tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F061_rsibulldiv_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F062_rsibeardiv_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F063_macdbulldiv_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F064_macdbeardiv_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F065_obvbulldiv_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F066_obvbeardiv_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$matrices = @(
  'configs\calibration_matrices\passport_actions\F061_rsibulldiv_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F062_rsibeardiv_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F063_macdbulldiv_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F064_macdbeardiv_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F065_obvbulldiv_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F066_obvbeardiv_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/b020_divergence_patterns_f061_f066_audit_20260622T193300Z.md`.

## PATTERN_QUALITY F067-F068 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_engine.py src\mlbotnav\optuna_objective.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_pattern_quality_passport_actions_emit_runtime_gates tests.test_backtest_fields.BacktestFieldsTests.test_pattern_quality_gate_uses_passport_action_columns tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F067_patternstrength_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F068_patternage_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$matrices = @(
  'configs\calibration_matrices\passport_actions\F067_patternstrength_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F068_patternage_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/b021_pattern_quality_f067_f068_audit_20260622T194700Z.md`.

## CHART_PATTERNS F069-F077 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_engine.py src\mlbotnav\optuna_objective.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_chart_pattern_passport_actions_emit_runtime_gates tests.test_backtest_fields.BacktestFieldsTests.test_chart_pattern_gate_uses_passport_action_columns tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F077_rangeflag_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F073_triangle_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F074_pennant_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F075_wedgerising_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F076_wedgefalling_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F069_doublebottom_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F070_doubletop_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F071_headshoulders_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F072_invheadshoulders_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$matrices = @(
  'configs\calibration_matrices\passport_actions\F077_rangeflag_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F073_triangle_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F074_pennant_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F075_wedgerising_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F076_wedgefalling_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F069_doublebottom_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F070_doubletop_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F071_headshoulders_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F072_invheadshoulders_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/b022_chart_patterns_f069_f077_audit_20260622T202100Z.md`.

## PATTERN_CONFIRMATION F078-F079 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_engine.py src\mlbotnav\optuna_objective.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_pattern_confirmation_passport_actions_emit_runtime_gates tests.test_backtest_fields.BacktestFieldsTests.test_pattern_confirmation_gate_uses_passport_action_columns tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F079_patternlevelconf_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F078_patternvolconf_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean sequential runtime command pattern:
```powershell
$matrices = @(
  'configs\calibration_matrices\passport_actions\F079_patternlevelconf_entry_filter.yaml',
  'configs\calibration_matrices\passport_actions\F078_patternvolconf_entry_filter.yaml'
)
foreach ($matrix in $matrices) {
  foreach ($mode in @('long_only','short_only')) {
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode $mode -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
  }
}
```

Result: final `NO_GO`; audit `reports/qa_gate/b023_pattern_confirmation_f078_f079_audit_20260622T203700Z.md`.

## PATTERN_COMPOSITE_ENTRY F080-F081 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\dataset.py src\mlbotnav\backtest.py src\mlbotnav\optuna_space.py src\mlbotnav\optuna_engine.py src\mlbotnav\optuna_objective.py src\mlbotnav\optuna_search_candidate.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_pattern_composite_entry_passport_actions_emit_runtime_gates tests.test_backtest_fields.BacktestFieldsTests.test_pattern_composite_entry_gate_uses_side_specific_action_columns tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
for rel in [
 'configs/calibration_matrices/passport_actions/F080_patternlong_entry_filter.yaml',
 'configs/calibration_matrices/passport_actions/F081_patternshort_entry_filter.yaml',
]:
    m = load_calibration_matrix(root, rel_path=rel)
    for mode in ['long_only','short_only']:
        s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
        print(rel, mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | .\.venv\Scripts\python.exe -
```

Clean side-specific runtime command pattern:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F080_patternlong_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F081_patternshort_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/b024_pattern_composite_entry_f080_f081_audit_20260622T205500Z.md`.

## F024 VWAP Distance Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; python -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; python -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_vwap_distance_action_column_uses_passport_params tests.test_backtest_fields.BacktestFieldsTests.test_entry_action_allow_gate_supports_f024_vwap_distance tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
rel = 'configs/calibration_matrices/passport_actions/F024_vwapdist_entry_filter.yaml'
m = load_calibration_matrix(root, rel_path=rel)
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | python -
```

Runtime:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F024_vwapdist_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F024_vwapdist_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/f024_vwap_distance_long_short_audit_20260623T055200Z.md`.

## F026 Density Bin Share 60 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; python -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; python -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_density_bin_share60_action_column_uses_passport_params tests.test_backtest_fields.BacktestFieldsTests.test_entry_action_allow_gate_supports_f026_bin_share60 tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
rel = 'configs/calibration_matrices/passport_actions/F026_binshare60_entry_filter.yaml'
m = load_calibration_matrix(root, rel_path=rel)
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | python -
```

Runtime:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F026_binshare60_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F026_binshare60_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/f026_binshare60_long_short_audit_20260623T060100Z.md`.

## F027 Density Cluster Share 60 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; python -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; python -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_density_cluster_share60_action_column_uses_passport_params tests.test_backtest_fields.BacktestFieldsTests.test_entry_action_allow_gate_supports_f027_cluster_share60 tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
rel = 'configs/calibration_matrices/passport_actions/F027_clustershare60_entry_filter.yaml'
m = load_calibration_matrix(root, rel_path=rel)
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | python -
```

Runtime:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F027_clustershare60_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F027_clustershare60_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/f027_clustershare60_long_short_audit_20260623T062300Z.md`.

## F028 Density VPOC Share 60 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; python -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; python -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_density_vpoc_share60_action_column_uses_passport_params tests.test_backtest_fields.BacktestFieldsTests.test_entry_action_allow_gate_supports_f028_vpoc_share60 tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
rel = 'configs/calibration_matrices/passport_actions/F028_vpocshare60_entry_filter.yaml'
m = load_calibration_matrix(root, rel_path=rel)
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | python -
```

Runtime:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F028_vpocshare60_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F028_vpocshare60_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/f028_vpocshare60_long_short_audit_20260623T064000Z.md`.

## F030 Density Bin Share 240 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; python -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; python -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_density_bin_share240_action_column_uses_passport_params tests.test_backtest_fields.BacktestFieldsTests.test_entry_action_allow_gate_supports_f030_bin_share240 tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
rel = 'configs/calibration_matrices/passport_actions/F030_binshare240_entry_filter.yaml'
m = load_calibration_matrix(root, rel_path=rel)
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | python -
```

Runtime:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F030_binshare240_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F030_binshare240_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/f030_binshare240_long_short_audit_20260623T070000Z.md`.

## F031 Density Cluster Share 240 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; python -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; python -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_density_cluster_share240_action_column_uses_passport_params tests.test_backtest_fields.BacktestFieldsTests.test_entry_action_allow_gate_supports_f031_cluster_share240 tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
rel = 'configs/calibration_matrices/passport_actions/F031_clustershare240_entry_filter.yaml'
m = load_calibration_matrix(root, rel_path=rel)
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | python -
```

Runtime:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F031_clustershare240_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F031_clustershare240_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/f031_clustershare240_long_short_audit_20260623T071000Z.md`.

## F032 Density VPOC Share 240 Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; python -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; python -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_density_vpoc_share240_action_column_uses_passport_params tests.test_backtest_fields.BacktestFieldsTests.test_entry_action_allow_gate_supports_f032_vpoc_share240 tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
rel = 'configs/calibration_matrices/passport_actions/F032_vpocshare240_entry_filter.yaml'
m = load_calibration_matrix(root, rel_path=rel)
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | python -
```

Runtime:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F032_vpocshare240_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F032_vpocshare240_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/f032_vpocshare240_long_short_audit_20260623T072500Z.md`.

## F038 Position In Range Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; python -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; python -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_position_in_range_action_column_uses_passport_params tests.test_backtest_fields.BacktestFieldsTests.test_entry_action_allow_gate_supports_f038_range_position tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
rel = 'configs/calibration_matrices/passport_actions/F038_rangepose_entry_filter.yaml'
m = load_calibration_matrix(root, rel_path=rel)
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | python -
```

Runtime:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F038_rangepose_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F038_rangepose_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/f038_rangepose_long_short_audit_20260623T074000Z.md`.

## F039 Trend Channel Position Validation And Runtime
Validation:
```powershell
$env:PYTHONPATH='src'; python -m py_compile .\src\mlbotnav\dataset.py .\src\mlbotnav\backtest.py .\src\mlbotnav\optuna_space.py
$env:PYTHONPATH='src'; python -m unittest tests.test_dataset_inference_mode.DatasetInferenceModeTests.test_trend_channel_pos_action_column_uses_passport_params tests.test_backtest_fields.BacktestFieldsTests.test_entry_action_allow_gate_supports_f039_channel_position tests.test_optuna_space_constraints.OptunaSpaceConstraintsTests.test_passport_action_matrix_allows_only_passport_params
```

Matrix compile:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
rel = 'configs/calibration_matrices/passport_actions/F039_channelpos_entry_filter.yaml'
m = load_calibration_matrix(root, rel_path=rel)
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode']['registry_block_id'], s['passport_mode']['registry_passport_id'])
'@ | python -
```

Runtime:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F039_channelpos_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F039_channelpos_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Result: final `NO_GO`; audit `reports/qa_gate/f039_channelpos_long_short_audit_20260623T080500Z.md`.
## Current ML Contract Command 2026-06-23 Step 2.2 Closed
Closed: `2.2 Добавить passport context`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.
Next exact WBS step: `2.3 Добавить trade identity`.
Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.
## Current ML Contract Command 2026-06-23 Step 2.3 Closed
Closed: `2.3 Добавить trade identity`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.
Next exact WBS step: `2.4 Добавить duration labels`.
Do not start the larger calibration/OOS run yet; Stage 2 is still incomplete.
## Visual Entry signal-entry overlay 2026-06-25
Статус: `READY_NEEDS_USER_VISUAL_CONFIRM`.

Построить v2-контракт "сигнальная свеча -> вход на open следующей свечи" с учетом slippage:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_signal_entry_overlay --seed-json reports\manual_entries\SOLUSDT_1m_visual_seed_20260625\manual_markup_seed_SOLUSDT_1m_2026-05-12_CORE.json --marked-png reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v1\manual_markup_SOLUSDT_1m_2026-05-12_DEV_marked.png --out-dir reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry --slippage-bps 5
```

После подтверждения пользователем запускать scorer/solo runner уже на v2 `manual_entries.json`.

## Visual Entry Instrument Stack Audit 2026-06-25
Статус: `AUDIT_READY_NEXT_RUNNER`.

Аудит:
```powershell
Get-Content -Encoding UTF8 reports\final_review\visual_entry_v3\instrument_stack_audit\visual_entry_instrument_stack_audit_20260625_RU.md
```

Следующая команда появится после добавления diagnostic runner `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`.

## Visual Entry Noise Suppression Cluster Priority 2026-06-25
Статус: `DEV_RUNNER_DONE_NO_ML`.

Запуск:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_noise_suppression_cluster_priority_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\noise_suppression_cluster_priority --render-top 8
```

Проверки:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\visual_entry_noise_suppression_cluster_priority_runner.py .\src\mlbotnav\render_visual_entry_overlay.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_noise_suppression_cluster_priority_runner tests.test_visual_entry_deep_capitulation_reclaim_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_render_visual_entry_overlay
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
```

Результат: `CP01_DQ01_CLUSTER10_SCORE12` = `9/11`, `28` false, `37` entries. Отчет: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_noise_suppression_cluster_priority_20260512_DEV_RU.md`.

## Visual Entry CP06 Recover 2026-06-25
Статус: `DEV_RECOVER_DONE_11_OF_11_NO_ML`.

Запуск тот же:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_noise_suppression_cluster_priority_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\noise_suppression_cluster_priority --render-top 8
```

Результат: `CP06_CP01_RECOVER_NOWICK_LATE_RETEST` = `11/11`, `28` false, `39` entries.

Главный PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp06_cp01_recover_nowick_late_retest_20260625T151725Z.png`.

Проверки:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile .\src\mlbotnav\visual_entry_noise_suppression_cluster_priority_runner.py .\tests\test_visual_entry_noise_suppression_cluster_priority_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_noise_suppression_cluster_priority_runner tests.test_visual_entry_deep_capitulation_reclaim_runner tests.test_render_visual_entry_overlay
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
```

## Visual Entry RBKD V0 Commands 2026-06-29

Validation `2026-05-13`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_reversal_bottom_knife_drop_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\reversal_bottom_knife_drop --render-top 4
```

Holdout `2026-05-14`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_reversal_bottom_knife_drop_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\reversal_bottom_knife_drop --render-top 4
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_reversal_bottom_knife_drop_runner.py tests\test_visual_entry_reversal_bottom_knife_drop_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_reversal_bottom_knife_drop_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_noise_suppression_cluster_priority_runner tests.test_visual_entry_deep_capitulation_reclaim_runner tests.test_render_visual_entry_overlay
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
```

Process-check после каждого прогона:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```
## Visual Entry SSRE V1 Commands 2026-06-29

Validation `2026-05-13`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_swing_support_retest_event_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\swing_support_retest_event --render-top 4
```

Holdout `2026-05-14`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_swing_support_retest_event_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\swing_support_retest_event --render-top 4
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_swing_support_retest_event_runner.py tests\test_visual_entry_swing_support_retest_event_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_swing_support_retest_event_runner
```
## Visual Entry Fresh Strategy Overlay Commands 2026-06-29

Validation `2026-05-13`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_strategy_fresh_overlay --manual-entries reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\fresh_strategy_overlay --label strict_default4_20260513
```

Holdout `2026-05-14`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_strategy_fresh_overlay --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\fresh_strategy_overlay --label strict_default4_20260514
```

Compile:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_strategy_fresh_overlay.py
```
## Visual Entry Significant Low Selector V1 Commands 2026-06-29

Run holdout `2026-05-14` user v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_significant_low_selector_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\significant_low_selector --render-top 8
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_significant_low_selector_runner.py tests\test_visual_entry_significant_low_selector_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_significant_low_selector_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
```

Process-check after each run:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```
## Visual Entry Regime Split Ranker V1 Commands 2026-06-29

Run holdout `2026-05-14` user red arrows v2:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_regime_split_ranker_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\regime_split_ranker --render-top 8
```

Focused checks:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_regime_split_ranker_runner.py tests\test_visual_entry_regime_split_ranker_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_regime_split_ranker_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
```

Process-check after run:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Run holdout `2026-05-14` user red arrows v2, Hot Trend False Suppression V5:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_hot_trend_false_suppression_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\hot_trend_false_suppression --render-top 8
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_hot_trend_false_suppression_runner tests.test_visual_entry_deep_recovery_hot_recall_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_hot_trend_false_suppression_runner.py tests\test_visual_entry_hot_trend_false_suppression_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Result 2026-06-29: `HTFS20_UNION_HTFS01` = `9/17` hits, `14` false, `23` entries, f1 `0.4500`; `HTFS01` = `4/17`, `1` false. Not ML-ready.

Run holdout `2026-05-14` user red arrows v2, Base False Suppression V6:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_base_false_suppression_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\base_false_suppression --render-top 8
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_base_false_suppression_runner tests.test_visual_entry_hot_trend_false_suppression_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_base_false_suppression_runner.py tests\test_visual_entry_base_false_suppression_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Result 2026-06-29: `BFS20_UNION_BFS01...PLUS_HTFS01` = `9/17` hits, `1` false, `10` entries, f1 `0.6667`; `BFS01` = `5/17`, `0` false. Not ML-ready until validation.

Run validation `2026-05-13`, Base False Suppression V6 without parameter changes:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_base_false_suppression_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms\manual_entries.json --out-dir reports\final_review\visual_entry_v3\base_false_suppression_validation --render-top 8
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m unittest tests.test_visual_entry_base_false_suppression_runner tests.test_visual_entry_hot_trend_false_suppression_runner
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_base_false_suppression_runner.py tests\test_visual_entry_base_false_suppression_runner.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Result 2026-06-29: validation fail, `BFS20_UNION_BFS01...PLUS_HTFS01` = `0/9` hits, `1` false, `1` entry. Not ML-ready.

## Visual Entry Fresh Target-Led Ledger Commands 2026-06-30

Статус: `FRESH_TARGET_LED_DAY_SELECTED_LEDGER_READY_NO_ML`.

Создать чистый график и target-led ledger T01..T10 без Optuna и без ML:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_fresh_target_ledger --manual-entries reports\manual_entries\SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2\manual_entries.json --out-dir reports\final_review\visual_entry_v3\fresh_target_led --limit 10
```

Проверки:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_fresh_target_ledger.py
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports\qa_gate
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Текущие артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/fresh_target_led_clean_chart_SOLUSDT_1m_2026-05-14_20260630T062202Z.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10_RU.md`.

Результат: первый кластер-кандидат `HOT_RECLAIM_SUPPORT`, точки `T04/T07/T08`. Это не lock и не стратегия; нужен визуальный confirm.

Рельсы работы:

```powershell
Get-Content -Encoding UTF8 docs\CALIBRATION_NODE_CURRENT\FRESH_TARGET_LED_RAILS_RU.md
```

## Fresh Target-Led Outcome Low Miner V0 2026-07-02

Статус: `OUTCOME_LOW_MINER_V0_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA_NO_SCORER`.

Проверка и запуск:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_outcome_low_miner_v0.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_outcome_low_miner_v0
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_20260702_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_CANDIDATES_20260702.csv
reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260514_20260702.png
reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_HIT_ZOOM_20260515_20260702.png
reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_FULL_DAY_20260514_20260702.png
reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0/OUTCOME_LOW_MINER_V0_FULL_DAY_20260515_20260702.png
```

Граница: future `+1.5%` только offline outcome label. No ML/export/training, no scorer, no target-lock, no Optuna.

Повтор с target `+1.0%`:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_outcome_low_miner_v0 --target-pct 1.0 --out-dir reports/final_review/visual_entry_v3/fresh_target_led/outcome_low_miner_v0_target_1pct
```
## Fresh Target-Led User Marked Order 2026-06-30

Показанный пользователю zoom-кандидат `M01`:

```powershell
# Артефакт уже создан:
reports\final_review\visual_entry_v3\fresh_target_led\visual_confirm\M01_user_marked_order_zoom_signal_0323_entry_0324.png
```

Текущая проверка хвостов после локальных запусков:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```
## Good 1pct Review Pool 2026-07-02

Статус: `GOOD_1PCT_REVIEW_POOL_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_good_1pct_review_pool.py
```

Smoke на один день:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_good_1pct_review_pool --start-day 2026-05-13 --end-day 2026-05-13 --run-label smoke_20260513
```

Рабочий запуск W18-W20:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_good_1pct_review_pool --start-day 2026-04-27 --end-day 2026-05-17 --run-label W18_W20_learning
```

VS Code task: `Visual Entry: Good 1pct Review Pool (NO ML/OPTUNA)`.

Проверка хвостов после запуска:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Граница: future `+1%` только offline outcome label для review-pool. Не ML, не export, не scorer, не target-lock, не Optuna.
## Significant Low Calibration V0

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_significant_low_calibration_v0 `
  --dca-run-dir reports\final_review\visual_entry_v3\fresh_target_led\dca_risk_audit_v0\W18_W20_dca_risk_20260502_userfix_v0_20260702_180352 `
  --feedback-csv reports\final_review\visual_entry_v3\fresh_target_led\dca_risk_audit_v0\W18_W20_dca_risk_20260502_closeups_20260702_162715\DCA_RISK_AUDIT_V0_20260502_USER_FEEDBACK_V0.csv `
  --day 2026-05-02 `
  --run-label siglow_20260502_v0
```

Последний результат:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_20260502_user_actual_v1c3_20260702_190227`

Актуальный повтор user-layer V1C3:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_significant_low_calibration_v0 `
  --dca-run-dir reports\final_review\visual_entry_v3\fresh_target_led\dca_risk_audit_v0\W18_W20_dca_risk_20260502_userfix_v0_20260702_180352 `
  --feedback-csv reports\final_review\visual_entry_v3\fresh_target_led\significant_low_calibration_v0\siglow_20260502_user_actual_v1b_20260702_185032\DCA_RISK_AUDIT_V0_20260502_USER_FEEDBACK_ACTUAL_OVERVIEW_V1C3.csv `
  --day 2026-05-02 `
  --run-label siglow_20260502_user_actual_v1c3
```

## Reanchor Applied V2 RA004 2026-07-03

Актуальный run после пользовательской стрелки на `20:49 UTC`:

```text
reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904
```

Главные файлы:

```text
reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502_CLOSE_ZOOM_RA004.png
reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502_OVERVIEW.png
reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502.csv
reports/final_review/visual_entry_v3/fresh_target_led/significant_low_calibration_v0/siglow_reanchor_applied_v2_20260703_081904/SIGNIFICANT_LOW_REANCHOR_APPLIED_V2_20260502.json
```

Проверки:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_significant_low_calibration_v0.py src\mlbotnav\visual_entry_low_anchor_suggester.py
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

Граница: NO_ML, NO_OPTUNA, NO_SCORER, NO_TARGET_LOCK, NO_API.

## Manual Reanchors V0 2026-05-02

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_manual_reanchor_review_v0.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_manual_reanchor_review_v0 `
  --config configs\visual_entry\manual_reanchors\SOLUSDT_1m_2026-05-02_SIGNIFICANT_LOW_MANUAL_REANCHORS_V0.json `
  --run-label siglow_manual_reanchors_v0
```

Последний результат:

`reports/final_review/visual_entry_v3/fresh_target_led/significant_low_manual_reanchors_v0/siglow_manual_reanchors_v0_20260703_083936`

Проверка хвостов после запуска:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*visual_entry*' -or $_.CommandLine -like '*Optuna*' -or $_.CommandLine -like '*APTuna*' } | Select-Object ProcessId,CommandLine
```

Граница: renderer читает только ручной JSON source-of-truth. Не ML, не Optuna, не scorer, не target-lock, не API.

## STAS1 GOOD_1PCT 2026-05-02 anchor-next-open

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-02 -RunLabel stas1_20260502_1pct_anchor_next_open_fix_v0
```

Проверка, что вход строго на следующей свече после low:

```powershell
@'
import pandas as pd
p = r'STAS1_GOOD_LOW_REVIEW\runs\stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034\GOOD_1PCT_REVIEW_POOL_RECORDS.csv'
df = pd.read_csv(p)
for c in ['anchor_time_utc', 'entry_time_utc']:
    df[c] = pd.to_datetime(df[c], utc=True)
bad = df[(df['entry_time_utc'] - df['anchor_time_utc']).dt.total_seconds() != 60]
print({'rows': len(df), 'bad_anchor_to_entry': len(bad)})
'@ | .\.venv\Scripts\python.exe -
```

Последний результат: `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034`.

Ожидание: `52` строки, `42` GOOD, `10` BAD, `bad_anchor_to_entry=0`.

## Codex/VS Code load audit

Проверить активные Git-процессы:

```powershell
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'git.exe' } | Select-Object ProcessId,ParentProcessId,Name,CommandLine | Format-List
```

Остановить только зависший `git add -A`, если он реально висит:

```powershell
$gitAdds = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'git.exe' -and $_.CommandLine -like '* add -A*' }
$gitAdds | Select-Object ProcessId,ParentProcessId,CommandLine
foreach ($p in $gitAdds) { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }
if (Test-Path .git/index.lock) { 'INDEX_LOCK_EXISTS' } else { 'NO_INDEX_LOCK' }
```

Проверить, что STAS run-артефакты игнорируются:

```powershell
git check-ignore -v STAS1_GOOD_LOW_REVIEW/runs STAS2_MARKET_PHASE_REVIEW/runs STAS3_PERCENT_LADDER_REVIEW/runs
```

Проверить скорость Git status:

```powershell
Measure-Command { git status --short --untracked-files=normal | Out-Null } | Select-Object TotalSeconds,TotalMilliseconds
```
## STAS4 combo strategies 3 days

Пример запуска одного слоя:

```powershell
$env:PYTHONPATH='src'
python -m mlbotnav.visual_entry_stas4_family_overlay `
  --stas2-run-dir STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260510_20260512_short_macro_wave_review_20260709_071233 `
  --day 2026-05-10 `
  --family structure_ta+trend_momentum `
  --out-dir STAS4_FEATURE_HYPOTHESIS_REVIEW\combo_structure_trend_20260510
```

Проверка скрипта:

```powershell
$env:PYTHONPATH='src'
python -m py_compile src\mlbotnav\visual_entry_stas4_family_overlay.py
```

Открыть папку с результатами:

```powershell
Start-Process "C:\Users\007\Desktop\MLbotNav\STAS4_FEATURE_HYPOTHESIS_REVIEW"
```
## Codex Startup Disk Load Audit 2026-07-11

Статус: `CODEX_STARTUP_DISK_LOAD_AUDIT_READY_NO_DELETE_NO_CODE_CHANGE`.

Главный отчет:

```powershell
ii .\docs\codex\CODEX_STARTUP_DISK_LOAD_AUDIT_20260711_RU.md
```

Проверить процессы Codex/Git после следующей перезагрузки:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -match '^(git|Codex|codex|node_repl|python)\.exe$' -or $_.CommandLine -match 'Codex|MLbotNav|git' } |
  Select-Object ProcessId,ParentProcessId,Name,CommandLine |
  Format-List
```

Проверить диск во время старта:

```powershell
Get-Counter '\PhysicalDisk(_Total)\% Disk Time','\PhysicalDisk(_Total)\Disk Bytes/sec' -SampleInterval 1 -MaxSamples 30
```

Проверить скорость Git:

```powershell
Measure-Command { git status --short --untracked-files=normal | Out-Null }
Measure-Command { git ls-files --others --exclude-standard | Out-Null }
```

Проверить размеры `.codex`:

```powershell
$results = foreach ($root in @('C:\Users\007\.codex','C:\Users\007\AppData\Local\OpenAI\Codex')) {
  if (Test-Path -LiteralPath $root) {
    foreach ($d in Get-ChildItem -LiteralPath $root -Force -Directory -ErrorAction SilentlyContinue) {
      $stats = Get-ChildItem -LiteralPath $d.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
      [pscustomobject]@{Root=$root; Name=$d.Name; MB=[math]::Round(($stats.Sum/1MB),1); Items=$stats.Count}
    }
  }
}
$results | Sort-Object MB -Descending | Format-Table -AutoSize
```

Граница: команды только диагностические. Не удалять и не переносить историю/кеши без отдельного подтверждения пользователя.

## STAS5 V4 Human-Style Group Ranker

Статус после no-future аудита: команды ниже оставлены для воспроизведения offline review. Не запускать новое обучение старого V4 как live/production, пока не реализован V4L live-safe контур.

Следующий рабочий план:

```powershell
ii .\STAS5_ML_CORE\08_STAS5_V4L_LIVE_SAFE_GROUP_RANKER_PLAN_RU.md
```

Обязательный guard перед будущим V4L train:

```text
LIVE_SAFE_FEATURE_ALLOWLIST
banned-column scan
feature_available_time_utc <= entry_time_utc
prefix invariance
retroactive_feature_change_count = 0
retroactive_score_change_count = 0
retroactive_decision_flip_count = 0
```

Собрать V4 train dataset `2026-05-01..2026-05-25`:

```powershell
$env:PYTHONPATH='src'
python -m mlbotnav.stas5_v4_group_rank_dataset
```

Обучить V4 group ranker:

```powershell
$env:PYTHONPATH='src'
python -m mlbotnav.stas5_v4_group_rank_train
```

Запустить blind forward `2026-05-26..2026-05-30`:

```powershell
$env:PYTHONPATH='src'
python -m mlbotnav.stas5_v4_forward_group_rank_review --start-day 2026-05-26 --end-day 2026-05-30
```

Актуальные артефакты текущего запуска:

```powershell
ii .\STAS5_ML_CORE\artifacts\v4\features\STAS5_V4_GROUP_RANK_TRAIN_DATASET_20260501_20260525.manifest.json
ii .\STAS5_ML_CORE\artifacts\v4\model\runs\stas5_v4_train_20260714_163911\stas5_v4_group_ranker_20260501_20260525_v0.manifest.json
ii .\STAS5_ML_CORE\artifacts\v4\forward\runs\stas5_v4_forward_20260526_20260530_20260714_164144\STAS5_V4_FORWARD_GROUP_RANK_REVIEW_MANIFEST.json
ii .\STAS5_ML_CORE\artifacts\v4\forward\runs\stas5_v4_forward_20260526_20260530_20260714_164144\20260526\STAS5_V4_FORWARD_GROUP_RANK_REVIEW_20260526.png
```

Smoke-проверка V4 тестовых функций без pytest-runner:

```powershell
$env:PYTHONPATH='src'
@'
import importlib.util
import inspect
import tempfile
from pathlib import Path
for test_path in [Path('tests/test_stas5_v4_group_rank_dataset.py'), Path('tests/test_stas5_v4_group_rank_train.py')]:
    spec = importlib.util.spec_from_file_location(test_path.stem, test_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, func in sorted(vars(module).items()):
        if name.startswith('test_') and callable(func):
            sig = inspect.signature(func)
            if 'tmp_path' in sig.parameters:
                with tempfile.TemporaryDirectory() as tmp:
                    func(Path(tmp))
            else:
                func()
            print('PASS', test_path.name, name)
'@ | python -
```
## Codex CPU Load Check 2026-07-15

Статус: `CODEX_CPU_LOAD_CHECK_READY_NO_KILL_NO_DELETE_NO_CODE_CHANGE`.

Открыть отчет:

```powershell
ii .\docs\codex\CODEX_CPU_LOAD_CHECK_20260715_RU.md
```

Проверить текущие Git-процессы Codex:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'git.exe'" |
  Select-Object ProcessId,ParentProcessId,CommandLine |
  Format-List
```

Проверить размер неигнорируемого dirty worktree:

```powershell
git ls-files --others --exclude-standard | Measure-Object
git ls-files --others --exclude-standard |
  ForEach-Object { if (Test-Path -LiteralPath $_ -PathType Leaf) { Get-Item -LiteralPath $_ } } |
  Measure-Object -Property Length -Sum
```

Проверить быстрый Git:

```powershell
Measure-Command { git status --short --untracked-files=normal | Out-Null }
Measure-Command { git diff --numstat | Out-Null }
```

Граница: команды диагностические. Не останавливать Codex/Git и не чистить файлы без отдельного решения.
## Codex Unload Check 2026-07-16

Статус: `CODEX_UNLOAD_APPLIED_NO_DELETE_NO_PROCESS_KILL_CODEX`.

Открыть отчет:

```powershell
ii .\docs\codex\CODEX_UNLOAD_ACTION_20260716_RU.md
```

Проверить, что STAS5 generated/run игнорируются:

```powershell
git check-ignore -v STAS5_ML_CORE/artifacts STAS5_ML_CORE/runs
```

Проверить размер оставшегося untracked:

```powershell
git ls-files --others --exclude-standard | Measure-Object
git ls-files --others --exclude-standard |
  ForEach-Object { if (Test-Path -LiteralPath $_ -PathType Leaf) { Get-Item -LiteralPath $_ } } |
  Measure-Object -Property Length -Sum
```

Проверить Git-процессы:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'git.exe'" |
  Select-Object ProcessId,ParentProcessId,CommandLine |
  Format-List
```

Граница: команды диагностические, без удаления.

## Codex Idle Relief Check 2026-07-16

Статус: `CODEX_IDLE_RELIEF_APPLIED_NO_DELETE_NO_STAS_TOUCH`.

Открыть отчет:

```powershell
ii .\docs\codex\CODEX_IDLE_RELIEF_20260716_RU.md
```

Проверить активные Git-процессы:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'git.exe'" |
  Select-Object ProcessId,ParentProcessId,CommandLine |
  Format-List
```

Проверить блокировку Git:

```powershell
Test-Path .\.git\index.lock
```

Проверить текущие процессы Codex/VS Code:

```powershell
Get-Process Codex,codex,Code -ErrorAction SilentlyContinue |
  Select-Object ProcessName,Id,PriorityClass,WorkingSet64 |
  Sort-Object ProcessName,Id |
  Format-Table -AutoSize
```

Поймать процессный I/O-всплеск:

```powershell
Get-Counter '\Process(*)\IO Read Bytes/sec','\Process(*)\IO Write Bytes/sec' -SampleInterval 1 -MaxSamples 5 |
  Select-Object -ExpandProperty CounterSamples |
  Where-Object { $_.CookedValue -gt 102400 } |
  Sort-Object CookedValue -Descending |
  Select-Object -First 30 Path,CookedValue
```

Граница: это диагностика и мягкая разгрузка, без удаления. Defender (`MsMpEng`) не отключать и исключения не добавлять без отдельного разрешения.

## Codex Update Load Audit 2026-07-22

Статус: `CODEX_UPDATE_LOAD_AUDIT_RELIEF_APPLIED_NO_DELETE`.

Открыть отчет:

```powershell
ii .\docs\codex\CODEX_UPDATE_LOAD_AUDIT_20260722_RU.md
```

Проверить версию Codex:

```powershell
Get-AppxPackage *Codex* | Select-Object Name,PackageFullName,Version,InstallLocation | Format-List
```

Проверить процессы Codex после обновления:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -in @('ChatGPT.exe','codex.exe','Code.exe') } |
  Select-Object Name,ProcessId,ParentProcessId,CommandLine |
  Format-Table -AutoSize
```

Мягко понизить приоритет текущей сессии:

```powershell
foreach($name in @('ChatGPT','codex','Code','node_repl','codex-code-mode-host')){
  Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object {
    $_.PriorityClass = 'Idle'
  }
}
```

Проверить Git и блокировку:

```powershell
Get-CimInstance Win32_Process -Filter "name='git.exe'" |
  Select-Object ProcessId,ParentProcessId,CommandLine |
  Format-List
Test-Path .\.git\index.lock
```

Граница: это диагностика и мягкая разгрузка, без удаления. VS Code OpenAI/Codex extension server можно останавливать как процесс, но глобально отключать расширение только отдельным решением пользователя.

## 2026-07-23 Codex VS Code Fix

Проверить сервер расширения VS Code Codex:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -in @('codex.exe','codex-code-mode-host.exe') -and $_.CommandLine -like '*openai.chatgpt*' } |
  Select-Object ProcessId,ParentProcessId,CommandLine |
  Format-List
```

Мягко прижать Codex без остановки:

```powershell
foreach($name in @('ChatGPT','codex','codex-code-mode-host')){
  Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object {
    $_.PriorityClass = 'Idle'
  }
}
```

Важно: если нужна рабочая панель Codex в VS Code, не останавливать процесс `openai.chatgpt...\codex.exe app-server`; при ошибке панели использовать кнопку `Перезапустить`.
