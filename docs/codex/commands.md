# Commands

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
