# Commands: калибровочный узел

## Fresh Target-Led V2A Structure Overlay 14 May 2026-07-01

Статус: `V2A_STRUCTURE_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Проверить и собрать 14 мая:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_strategy_passport_overlay_v2a.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_strategy_passport_overlay_v2a --day 2026-05-14
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_FULL_DAY_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_01_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_ZOOM_PAGE_02_20260514.png
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514.json
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514.csv
reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514_RU.md
```

Граница: visual overlay only. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## Fresh Target-Led Existing Passport Reconciliation 2026-07-01

Статус: `V2A_STRUCTURE_LAYER_20260514_READY_WAIT_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Текущий шаг не запускает scorer, Optuna или ML. Паспорта уже собраны; нужно сверять существующий manifest и готовить визуальный overlay.

Прочитать рабочие рельсы:

```powershell
Get-Content -Encoding UTF8 docs\CALIBRATION_NODE_CURRENT\FRESH_TARGET_LED_STRATEGY_PASSPORT_ROADMAP_RU.md
Get-Content -Encoding UTF8 docs\CALIBRATION_NODE_CURRENT\PASSPORT_REGISTRY_RECONCILIATION_V0_RU.md
Get-Content -Encoding UTF8 docs\CALIBRATION_NODE_CURRENT\FRESH_TARGET_LED_RAILS_RU.md
```

Проверить реестр:

```powershell
Get-Content -Encoding UTF8 configs\calibration_action_passports.yaml
```

Следующий разрешенный рабочий слой:

```text
V2A_STRUCTURE_LAYER
B014 LEVEL/RANGE/CHANNEL
B015 FIBONACCI_GRID
B017 BREAKOUT_RETEST
B018 MARKET_STRUCTURE BOS/CHOCH
B016 muted/context-only
```

Запрещено: scorer, target-lock, Optuna, ML/export/promotion.

## Fresh Target-Led Indicator/Hypothesis Review V1 19+7

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

## Fresh Target-Led T15 Draft Ledger / Cluster Discussion V1 Red Arrow Fix

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

Граница: draft-ledger/cluster discussion only. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## Fresh Target-Led T15 Draft Ledger / Cluster Discussion V0

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

Граница: draft-ledger/cluster discussion only. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## Fresh Target-Led Indicator/Hypothesis Visual Review V0

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_indicator_hypothesis_review.py
```

Команда:

```powershell
$env:PYTHONPATH='src'
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

Граница: visual evidence only. No scorer, no target-lock, no ML/export/promotion, no Optuna.

## Fresh Target-Led T15 Priority Zoom Review V0

Статус: `T15_PRIORITY_ZOOM_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_priority_zoom_review.py
```

Команда:

```powershell
$env:PYTHONPATH='src'
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

## Fresh Target-Led T15 User Verdict V1

Статус: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_t15_user_verdict.py
```

Команда:

```powershell
$env:PYTHONPATH='src'
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

## Fresh Target-Led Low Anchor Transfer User Feedback 2026-05-15 V2

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V2_FIXED_NO_ML_NO_OPTUNA`.

Команда:

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

## Fresh Target-Led Low Anchor Transfer User Feedback 2026-05-15 V1

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V1_FIXED_NO_ML_NO_OPTUNA`.

Команда:

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

## Fresh Target-Led Low Anchor Transfer User Feedback 2026-05-15 V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Команда:

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

## Fresh Target-Led Low Anchor Transfer Review 2026-05-15 Compact V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_DAY_20260515_READY_NO_ML_NO_OPTUNA`.

Команда:

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

Граница: visual transfer review only. No ML/export/promotion. No Optuna. EMA не active condition.

## Fresh Target-Led Feature Policy EMA Deferred 2026-07-01

Статус: `LOW_ANCHOR_FEATURE_POLICY_EMA_DEFERRED_NO_ML_NO_OPTUNA`.

Правило:

```text
EMA пока не является рабочим условием входа.
Шаблоны, паспорта и будущие checklist/scorer draft делать без EMA как active condition.
EMA-колонки из feature audit остаются только справочными и не используются для отбора.
```

Граница:

```text
No ML/export/promotion.
No Optuna.
No entry-candle OHLCV/future outcome.
```

## Fresh Target-Led Low Anchor No-Lookahead Feature Audit V0 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_READY_NO_ML_NO_OPTUNA`.

Команда:

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

Граница: feature audit only. No ML/export/promotion.

## Fresh Target-Led Low Anchor Extra Auto Feedback Summary 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_COMPLETE_NO_ML_NO_OPTUNA`.

Команда:

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

## Fresh Target-Led Low Anchor Extra Auto Page06 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Команда:

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

Граница: all-reject page `06`, countertrend. No ML/export/promotion.

## Fresh Target-Led Low Anchor Extra Auto Page05 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Команда:

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
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/USER_RED_FEEDBACK_SOURCE_PAGE05_20260701.png
```

Граница: all-reject page `05`, no ML/export/promotion.

## Fresh Target-Led Low Anchor Extra Auto Page04 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Команда:

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
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/USER_RED_FEEDBACK_SOURCE_PAGE04_20260701.png
```

Граница: current auto-entry not gold. Новые ручные точки требуют отдельного zoom-review.

## Fresh Target-Led Low Anchor Extra Auto Page03 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Команда:

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

Граница: all-reject page `03`, `bad_noise_weak_context`. No ML/export/promotion.

## Fresh Target-Led Low Anchor Extra Auto Page02 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Команда:

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

Граница: `LA018/LA020/LA026` оставлены как `possible_entry`, не gold. Остальные page `02` rejected как `bad_noise_shallow_bounce`.

## Fresh Target-Led Low Anchor Extra Auto Page01 Feedback 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Команда:

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

Граница: page 01 `LA001..LA012` rejected как `bad_noise_shallow_bounce`. Это feedback layer, не ML/export.

## Fresh Target-Led Low Anchor Extra Auto Review V1 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_READY_NO_ML_NO_OPTUNA`.

Команда:

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
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_02_20260701.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_03_20260701.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_04_20260701.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_05_20260701.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_06_20260701.png
```

Граница: эти кандидаты не negative labels автоматически. Разметка только после visual verdict пользователя.

## Fresh Target-Led Low Anchor Label Ledger V1 Resolved 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_BY_USER_NO_ML_NO_OPTUNA`.

Команда:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_label_ledger --ledger-version V1 --accept-pending-as-user-ok --out-dir reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701_RU.md
```

Граница: no ML/export/promotion. Следующий шаг: anti-review extra auto candidates.

## Fresh Target-Led Low Anchor Label Ledger V0 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_READY_NO_ML_NO_OPTUNA`.

Команда:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_label_ledger
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_label_ledger.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_PENDING_SHIFT_REVIEW_20260701.png
```

Граница: pending shift review не является ML label. Optuna/ML/export/promotion не запускать.

## Fresh Target-Led Low Anchor User Feedback M03/M09/M10/M11 2026-07-01

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_NO_ML_NO_OPTUNA`.

Команда:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_low_anchor_feedback --source-feedback-png 'C:\Users\007\AppData\Local\Temp\codex-clipboard-cd47c54e-a7a2-4324-ad34-8fbe17b226fe.png'
```

Проверка:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_low_anchor_feedback.py
```

Артефакты:

```text
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701_RU.md
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.png
reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.svg
```

Граница: это feedback-only слой. `hit_within_3m` не считать gold без visual verdict. Optuna/ML/export/promotion не запускать.

## Fresh Target-Led C02 Good/Bad Audit 2026-06-30

Статус: `C02_GOOD_BAD_AUDIT_V0_COMPLETE_NO_ML_NO_OPTUNA`.

Проверка аудита:

```powershell
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$p = "reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630.json"
Get-Content -Encoding UTF8 $p -Raw | ConvertFrom-Json | Select-Object status,next_step
```

PNG:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_FULL_DAY_AUDIT_V0_20260630.png
```

Следующий подпункт: `C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`. Scorer, Optuna, ML/export/promotion и multi-day пока не запускать.

## Fresh Target-Led C02 User Review 2026-06-30

Статус: `C02_CANDIDATE_REVIEW_V0_USER_LABELS_COMPLETE_NO_ML_NO_OPTUNA`.

Проверка текущей ручной разметки C02:

```powershell
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$p = "reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_LEDGER_V0_20260630.json"
$j = Get-Content -Encoding UTF8 $p -Raw | ConvertFrom-Json
$j.status
$j.user_review_summary
```

Контрольный PNG:

```text
reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_USER_LABELED_GOOD_BAD_SHEET_20260630.png
```

Следующий подпункт: разобрать good/bad признаки C02. Scorer, Optuna, ML/export/promotion и multi-day пока не запускать.
## Visual Entry v3 DEEP_CAPITULATION_RECLAIM 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY_NO_ML`.

Запуск deep-capitulation/reclaim diagnostic:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_deep_capitulation_reclaim_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\deep_capitulation_reclaim --render-top 8
```

Отчеты:
1. `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_20260512_DEV.json`
2. `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_20260512_DEV_RU.md`
3. `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_audit_20260625_RU.md`

Top PNG:

`reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_family_overlay_2026-05-12_deep_reclaim_01_dq01_eq01_plus_deep_reclaim_20260625T142559Z.png`

High-recall PNG:

`reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_family_overlay_2026-05-12_deep_reclaim_03_dq03_eq03_high_recall_plus_deep_20260625T142607Z.png`

Решение: diagnostic-only, в ML ничего не передавать.

После любого visual-entry прогона проверять хвосты процессов:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*MLbotNav*' -or $_.CommandLine -like '*mlbotnav*' -or $_.CommandLine -like '*APTuna*' -or $_.CommandLine -like '*visual_entry*' } | Select-Object ProcessId,CommandLine
```

## Visual Entry v3 EARLY_FLUSH_REVERSAL commands 2026-06-25
Запуск diagnostic-only слоя:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_early_flush_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\early_flush_reversal --render-top 6
```

Отчет:

```text
reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_20260512_DEV_RU.md
```

Аудит:

```text
reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_audit_20260625_RU.md
```

Решение: diagnostic-only; лучший результат все еще шумный, в ML ничего не передавать.

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

## Visual Entry v3 no-lookahead diagnostic 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY_NO_ML`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_no_lookahead_candidates --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\no_lookahead_candidates_rerun --render-top 5
```

Отчет: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`.

Правило: это DEV diagnostic-only; в ML ничего не передавать.

Updated UTC: `2026-06-25T06:37:00Z`.

## B001 marked-entry fixed diagnostic 2026-06-25
Статус: `DONE_NEGATIVE_NO_PROMOTION`.

Аудит: `reports/qa_gate/b001_marked_entry_fixed_backtest_audit_20260625T073900Z_RU.md`.

Матрица: `reports/qa_gate/b001_marked_entry_fixed_long_20260625T071500Z/B001_F001_F005_MARKED_ENTRY_FIXED_long_3OF5.yaml`.

Команда diagnostic-only с `min_expected_move_pct=0.001`:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 1 -ProcessWorkers 1 -SearchWorkersPerProcess 1 -OptunaTrials 8 -OptunaTimeoutSec 300 -CalibrationMatrixPath reports\qa_gate\b001_marked_entry_fixed_long_20260625T071500Z\B001_F001_F005_MARKED_ENTRY_FIXED_long_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage off -MinCandidateTrades 1 -HorizonsGrid 4 -PLongGrid 0.60 -PShortGrid 0.42 -MinExpectedMoveGrid 0.001 -NotionalUsdGrid 10 -StopLossPct 0.008 -TakeProfitPct 0.012 -TpMinFactor 0.7 -MinTpReachProb 0.58 -UseTemporaryUnlock
```

Итог выполненного прогона: `18` сделок, OOS `-47.05387771496912%`, точные попадания `09:25` и `12:36`, в ML не передавать.

Команда diagnostic-only без min-move:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 1 -ProcessWorkers 1 -SearchWorkersPerProcess 1 -OptunaTrials 8 -OptunaTimeoutSec 300 -CalibrationMatrixPath reports\qa_gate\b001_marked_entry_fixed_long_20260625T071500Z\B001_F001_F005_MARKED_ENTRY_FIXED_long_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage off -MinCandidateTrades 1 -HorizonsGrid 4 -PLongGrid 0.60 -PShortGrid 0.42 -MinExpectedMoveGrid 0.0 -NotionalUsdGrid 10 -StopLossPct 0.008 -TakeProfitPct 0.012 -TpMinFactor 0.7 -MinTpReachProb 0.58 -UseTemporaryUnlock
```

Итог выполненного прогона: `30` сделок, OOS `-67.41968770852606%`, шум увеличился, в ML не передавать.

## Visual Entry solo passport runner 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY`.

Команда:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_solo_passport_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v1\manual_entries.json --out-dir reports\final_review --render-top 6
```

Отчет:
`reports/final_review/visual_entry_solo_passport_runner_20260512_DEV_RU.md`.

Лучшие diagnostic-only результаты:
1. `F009_EMAGAP_DOWN`: `2/6` hits, `6` false, `8` entries, `f1_visual=0.2857`;
2. `F059_ENGULFBULL`: `1/6` hits, `0` false, `1` entry, `f1_visual=0.2857`;
3. `F010_EMASLOPE_DOWN`: `2/6` hits, `16` false, `18` entries, `f1_visual=0.1667`.

Решение: одиночные паспорта не кандидаты; использовать как входные детали для combo/family `REVERSAL_DIP_BUY_LONG v0`. В ML ничего не передавать.

## Shared-study control smoke after profile-edge fix

Статус: `DONE_CONFIRMED`.

Аудит фикса: `reports/qa_gate/shared_study_profile_edge_coverage_fix_20260625T063700Z_RU.md`.

Контрольный LONG smoke для проверки полного profile edge coverage:

```powershell
$RUN_ID = "b001_3of5_long_shared_edgefix_$(Get-Date -Format yyyyMMdd_HHmmss)"
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath reports\qa_gate\b001_family_unified_long_3of5_shared_20260625T005102\B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId $RUN_ID -UseTemporaryUnlock
```

Подтвержденный запуск: `b001_3of5_long_shared_edgefix3_20260625_115056`.

Финальный отчет: `reports/pipeline/optuna_search_candidate_SOLUSDT_1m_20260625T065106Z_long_only_pool_20260625t065056z_w3.json`.

Итог coverage: terminal `42/42`, core `5/5 PASS`, profile `7/7 PASS`, forced min/max полный `7/7`.

Итог доходности: OOS `0`, сделок `0`; это не кандидат, в ML не передавать.

## B001 family-unified 3/5 shared-study diagnostic

Статус LONG: `DONE_TRADEFUL_NEGATIVE_NO_PROMOTION_WITH_EDGE_COVERAGE_WARN`.

Аудит LONG: `reports/qa_gate/b001_family_unified_3of5_long_shared_audit_20260624T195200Z_RU.md`.

Выполненная матрица LONG:

`reports/qa_gate/b001_family_unified_long_3of5_shared_20260625T005102/B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml`

Выполненный LONG запуск:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath reports\qa_gate\b001_family_unified_long_3of5_shared_20260625T005102\B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId b001_3of5_long_shared_20260625T005102 -UseTemporaryUnlock
```

Результат LONG: launcher `OK`, best worker `w3`, OOS `-2.0302055441506761%`, сделок `1`, ML не трогать.

Предупреждение: при бюджете `42` core edge coverage прошел, но profile edge coverage неполный (`F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`). Если следующий запуск нужен как clean edge-proof, сначала закрыть этот вопрос или увеличить/исправить edge coverage; если нужен только runtime diagnostic, можно запускать SHORT с явной пометкой warning.

Сгенерировать свежую SHORT matrix `3/5`:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.b001_ret_n_ladder_tournament --family-unified --family-move -1 --strict-confirmations 3 --output-dir reports\qa_gate\b001_family_unified_short_3of5_NEXT
```

Шаблон SHORT diagnostic после генерации matrix:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath reports\qa_gate\b001_family_unified_short_3of5_NEXT\B001_F001_F005_FAMILY_UNIFIED_short_3OF5.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId b001_3of5_short_shared_NEXT -UseTemporaryUnlock
```

В ML ничего не передавать.

## Optuna shared-study process-pool 3x3/9

Статус: `OPTUNA_SHARED_STUDY_3X3_9_READY`.

Назначение: рабочий профиль с тремя Python-процессами, но с одной общей Optuna study. Использовать, когда нужно "единое целое": общий поиск по одной истории trials, без трех раздельных Optuna-историй.

Профиль:
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=3`;
4. `SearchWorkersPerProcess=3`;
5. `OptunaTrials=42`;
6. `-SharedOptunaStudy`;
7. `-SharedStudyId <уникальный_понятный_id>`.

Важное правило: shared-study режим требует не-`sqlite` storage. Текущий проверенный storage: `postgresql`. Если preflight видит `sqlite`, запуск должен остановиться до старта worker.

Шаблон process-pool LONG:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath <matrix> -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId <RUN_ID> -UseTemporaryUnlock
```

Шаблон process-pool SHORT:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath <matrix> -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId <RUN_ID> -UseTemporaryUnlock
```

Шаблон block-family LONG:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId B001_LONG_SHARED -UseTemporaryUnlock
```

Шаблон block-family SHORT:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId B001_SHORT_SHARED -UseTemporaryUnlock
```

Проверенный smoke-аудит: `reports/qa_gate/optuna_shared_study_process_pool_audit_20260624T190435Z_RU.md`.

## Optuna рабочий профиль 3x3/9

Профиль:
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=3`;
4. `SearchWorkersPerProcess=3`;
5. `OptunaTrials=42`.

Назначение: рабочий нагрузочный профиль. Он запускает три отдельных Python-процесса `w1/w2/w3`, каждый с `3` search-workers. Профиль `1x9/9` не считать физическим эквивалентом; он нужен только как отдельная диагностика одной Optuna-истории.

Шаблон LONG:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath <matrix> -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Шаблон SHORT:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath <matrix> -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Диагностический single-worker `1x9/9`, только когда нужна одна Optuna-история:

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

Артефакты:
1. `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.png`.
2. `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.png`.

## Диагностика 2026-06-24: B001_COMBO_DIAG N-of-M

Статус: `B001_COMBO_DIAG_N_OF_M_SMOKE_DONE_NO_CANDIDATE`.

Аудит: `reports/qa_gate/b001_combo_diag_n_of_m_audit_20260624T125500Z_RU.md`.

Матрицы: `reports/qa_gate/b001_combo_diag_matrices_20260624Tmanual`.

Полная combo-матрица `F001..F005`:

`reports/qa_gate/b001_combo_diag_matrices_20260624Tmanual/31_B001_RET_N_F001_F002_F003_F004_F005.yaml`

Выполненные smoke-команды 1д/1д:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath reports\qa_gate\b001_combo_diag_matrices_20260624Tmanual\31_B001_RET_N_F001_F002_F003_F004_F005.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath reports\qa_gate\b001_combo_diag_matrices_20260624Tmanual\31_B001_RET_N_F001_F002_F003_F004_F005.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Результат smoke:
1. LONG full-combo: OOS `-8.498538882812346%`, сделок `4`, `n_of_m`, `N=1`.
2. SHORT full-combo: tradeful worker OOS `-6.055628696458093%`, сделок `2`, `n_of_m`, `N=1`.
3. Решение: `DIAG_WORKS_NO_CANDIDATE`, в ML ничего не передавать.

Следующая безопасная диагностическая команда LONG для 31 комбинации smoke 1д/1д:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -MatrixManifestPath reports\qa_gate\b001_combo_diag_matrices_20260624Tmanual\manifest.json -StartIndex 1 -EndIndex 31 -EnableCombinationTournament -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Следующая безопасная диагностическая команда SHORT для 31 комбинации smoke 1д/1д:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -MatrixManifestPath reports\qa_gate\b001_combo_diag_matrices_20260624Tmanual\manifest.json -StartIndex 1 -EndIndex 31 -EnableCombinationTournament -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Правило: diagnostic-only, не заменяет `B001.6`, не передавать в ML.

## Текущий маршрут 2026-06-24: B003.1 large LONG

Статус: `NEXT_B003_1_LARGE_LONG`.

Закрыто:
1. `B001.1` smoke LONG 1д/1д.
2. `B001.2` smoke SHORT 1д/1д.
3. `B001.3` smoke-аудит.
4. `B001.4` large LONG 2н/1н: `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.
5. `B001.5` large SHORT 2н/1н: `reports/qa_gate/b001_large_short_b001_5_audit_20260624T094057Z_RU.md`.
6. `B001.6` итог блока: `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.
7. `B002.1` large LONG 2н/1н: `reports/qa_gate/b002_large_long_b002_1_audit_20260624T100300Z_RU.md`.
8. `B002.2` large SHORT 2н/1н: `reports/qa_gate/b002_large_short_b002_2_audit_20260624T100700Z_RU.md`.
9. `B002.3` итог блока: `reports/qa_gate/b002_block_summary_b002_3_20260624T100800Z_RU.md`.

Следующий блок: `B003`, одиночный паспорт `F007 / F007_RSTD20_ALLOW`.

Активный worker-профиль: `3x3/9`.
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=3`;
4. `SearchWorkersPerProcess=3`.

Откат на `2x3/6` разрешен только при устойчивой перегрузке CPU/памяти или падении workers, с обязательной записью причины в аудите.

Следующий строгий номер: `B003.1 large LONG 2н/1н`.

Команда B003.1 LONG:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B003 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

После B003.1 сделать проверку отчета. Если runner/воркеры/логика корректны, следующий номер `B003.2 large SHORT 2н/1н`.

Команда B003.2 SHORT:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B003 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

В ML ничего не передавать.

## Архив 2026-06-24: B002.2 large SHORT

Статус: `CLOSED_B002_2_SUPERSEDED_BY_B002_3`.

Аудит: `reports/qa_gate/b002_large_short_b002_2_audit_20260624T100700Z_RU.md`.

## Архив 2026-06-24: B001.6 итог блока

Статус: `CLOSED_B001_6_NEXT_B002`.

Итог: `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.

## Архив команды 2026-06-24: B001.5 large SHORT

Статус: `CLOSED_B001_5_SUPERSEDED_BY_B001_6`.

Аудит B001.4: `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.

Закрыто:
1. `B001.1` smoke LONG 1д/1д.
2. `B001.2` smoke SHORT 1д/1д.
3. `B001.3` smoke-аудит.
4. `B001.4` large LONG 2н/1н.

Номер `B001.5 large SHORT 2н/1н` уже закрыт. Актуальный следующий номер указан сверху: `B001.6 итог блока LONG+SHORT`.

Команда:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

После `B001.5` аудит выполнен. Актуальный шаг: итог `B001.6`. В ML ничего не передавать.

## Текущий маршрут 2026-06-24: B001.4 large LONG

Статус: `NEXT_B001_4_LARGE_LONG`.

Аудит B001.3: `reports/qa_gate/b001_smoke_1d1d_audit_20260624T075006Z_RU.md`.

Закрыто:
1. `B001.1` smoke LONG 1д/1д.
2. `B001.2` smoke SHORT 1д/1д.
3. `B001.3` smoke-аудит.

Следующий строгий номер: `B001.4 large LONG 2н/1н`.

Команда:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

После `B001.4` сделать аудит. Если есть стоп-условие, фикс и повтор нужного номера. Если все корректно, следующий номер `B001.5 large SHORT 2н/1н`.

В ML ничего не передавать.

## Текущий маршрут 2026-06-24: B001 smoke 1д/1д перед large

Статус: `READY_FOR_B001_1D1D_SMOKE`.

Протокол: `reports/qa_gate/b001_block_route_protocol_20260624T072600Z_RU.md`.

Правило: сначала проверяем блок `B001` на `1m`, калибровка `1` день, входы/OOS следующий `1` день. LONG и SHORT запускать отдельно и последовательно. Если smoke неверный, останавливаемся, делаем аудит, фикс и повторяем smoke. Large 2н/1н не запускать до успешного smoke-аудита.

Порядок:
1. `B001.1` smoke LONG 1д/1д.
2. `B001.2` smoke SHORT 1д/1д.
3. `B001.3` smoke-аудит и решение.
4. `B001.4` large LONG 2н/1н, только после успешного `B001.3`.
5. `B001.5` large SHORT 2н/1н, только после `B001.4`.
6. `B001.6` итог блока.

B001.1 smoke LONG 1д/1д:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

B001.2 smoke SHORT 1д/1д:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

B001.4 large LONG 2н/1н, запускать только после успешного `B001.3`:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

B001.5 large SHORT 2н/1н, запускать только после `B001.4`:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

## Current Route 2026-06-24: block-family calibration

Status: `READY_FOR_BLOCK_ROUTE_1_B001`.

Audit: `reports/qa_gate/block_family_passport_route_audit_20260624T064900Z.md`.

Route summary: old F-by-F continuation to `F068` is superseded. Work now proceeds by B-block. For a family block, run all solo F-passports inside the block for LONG and SHORT, then fix one block winner or `NO_BLOCK_WINNER`. Do not send anything to ML until all block winners are manually reviewed and explicitly approved.

Min-move fix remains active: `MIN_MOVE_UNREACHABLE` is diagnosed in backtest/OOS, penalized and fail-keyed in Optuna, skipped by adaptive selection when reachable alternatives exist, and the default 1m min-move grid is `0.0,0.001,0.002,0.003`.

Next strict task: `BLOCK_ROUTE_1 Run B001 family solo-selection after min-move fix`.

Use B001 solo rows only by default: F001, F002, F003, F004, F005. Do not enable combination tournament unless explicitly requested.

Do not use the old B001 1d/1d tournament command as the main route. Use the new generic block-family runner:
`APTuna/run_block_family_selection.ps1`.

The active large-window route uses:
1. train/calibration: `2026-05-11..2026-05-24`;
2. test/OOS: `2026-05-25..2026-05-31`;
3. LONG and SHORT sequentially;
4. one block report that selects the best F/side inside B001.

B001 LONG block command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

B001 SHORT block command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_block_family_selection.ps1 -BlockId B001 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Run LONG and SHORT sequentially because `-UseTemporaryUnlock` process-pool jobs must not overlap.

## Current Active Command 2026-06-23: stage 8.2.18 F067 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_18_f067_audit_20260623T225700Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F067_patternstrength_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F067_patternstrength_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F067_require_confirmation=0.0`, `F067_require_context=1.0`, `F067_strength_state=1.0`, `F067_strength_thr=3.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F067_require_confirmation=1.0`, `F067_require_context=0.0`, `F067_strength_state=2.0`, `F067_strength_thr=2.0`.
3. decision: `NO_GO_FOR_ML`.

Historical next WBS pointer before block-route correction:

`8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate`

This pointer is superseded by `Current Route 2026-06-24: block-family calibration` at the top of this file.

## Current Active Command 2026-06-23: stage 8.2.17 F066 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_17_f066_audit_20260623T224200Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F066_obvbeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F066_obvbeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F066_confirm_mode=1.0`, `F066_div_type=2.0`, `F066_max_pivot_gap_bars=85.0`, `F066_obv_delta_min_norm=4.5`, `F066_pivot_scope=1.0`, `F066_price_delta_min_pct=1.9`, `F066_reaction_confirm_pct=0.15`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F066_confirm_mode=1.0`, `F066_div_type=1.0`, `F066_max_pivot_gap_bars=60.0`, `F066_obv_delta_min_norm=10.5`, `F066_pivot_scope=1.0`, `F066_price_delta_min_pct=1.25`, `F066_reaction_confirm_pct=0.45`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.16 F065 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_16_f065_audit_20260623T223100Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F065_obvbulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F065_obvbulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F065_confirm_mode=2.0`, `F065_div_type=1.0`, `F065_max_pivot_gap_bars=55.0`, `F065_obv_delta_min_norm=13.0`, `F065_pivot_scope=2.0`, `F065_price_delta_min_pct=1.8`, `F065_reaction_confirm_pct=0.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F065_confirm_mode=2.0`, `F065_div_type=2.0`, `F065_max_pivot_gap_bars=65.0`, `F065_obv_delta_min_norm=20.0`, `F065_pivot_scope=2.0`, `F065_price_delta_min_pct=0.5`, `F065_reaction_confirm_pct=0.85`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.15 F064 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_15_f064_audit_20260623T222100Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F064_macdbeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F064_macdbeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F064_confirm_mode=1.0`, `F064_div_type=2.0`, `F064_macd_component=2.0`, `F064_macd_delta_min_pct=0.02`, `F064_max_pivot_gap_bars=65.0`, `F064_pivot_scope=2.0`, `F064_price_delta_min_pct=1.3`, `F064_reaction_confirm_pct=1.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F064_confirm_mode=2.0`, `F064_div_type=2.0`, `F064_macd_component=1.0`, `F064_macd_delta_min_pct=0.38`, `F064_max_pivot_gap_bars=75.0`, `F064_pivot_scope=1.0`, `F064_price_delta_min_pct=0.55`, `F064_reaction_confirm_pct=0.95`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.14 F063 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_14_f063_audit_20260623T221200Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F063_macdbulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F063_macdbulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F063_confirm_mode=2.0`, `F063_div_type=2.0`, `F063_macd_component=2.0`, `F063_macd_delta_min_pct=0.42`, `F063_max_pivot_gap_bars=35.0`, `F063_pivot_scope=1.0`, `F063_price_delta_min_pct=2.75`, `F063_reaction_confirm_pct=0.65`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F063_confirm_mode=2.0`, `F063_div_type=2.0`, `F063_macd_component=2.0`, `F063_macd_delta_min_pct=0.32`, `F063_max_pivot_gap_bars=35.0`, `F063_pivot_scope=2.0`, `F063_price_delta_min_pct=1.15`, `F063_reaction_confirm_pct=0.8`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.13 F062 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_13_f062_audit_20260623T220200Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F062_rsibeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F062_rsibeardiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F062_confirm_mode=1.0`, `F062_div_type=2.0`, `F062_max_pivot_gap_bars=10.0`, `F062_pivot_scope=1.0`, `F062_price_delta_min_pct=2.5`, `F062_reaction_confirm_pct=0.85`, `F062_rsi_delta_min=3.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F062_confirm_mode=2.0`, `F062_div_type=2.0`, `F062_max_pivot_gap_bars=5.0`, `F062_pivot_scope=1.0`, `F062_price_delta_min_pct=2.1`, `F062_reaction_confirm_pct=0.0`, `F062_rsi_delta_min=18.0`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.12 F061 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_12_f061_audit_20260623T215100Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F061_rsibulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F061_rsibulldiv_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F061_confirm_mode=1.0`, `F061_div_type=2.0`, `F061_max_pivot_gap_bars=30.0`, `F061_pivot_scope=1.0`, `F061_price_delta_min_pct=0.5`, `F061_reaction_confirm_pct=0.2`, `F061_rsi_delta_min=9.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F061_confirm_mode=1.0`, `F061_div_type=1.0`, `F061_max_pivot_gap_bars=120.0`, `F061_pivot_scope=2.0`, `F061_price_delta_min_pct=0.25`, `F061_reaction_confirm_pct=0.85`, `F061_rsi_delta_min=14.0`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.11 F060 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.11 Run F060_ENGULFBEAR_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_11_f060_audit_20260623T213900Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F060_engulfbear_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F060_engulfbear_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F060_engulf_mode=2.0`, `F060_min_body_pct=65.0`, `F060_min_engulf_ratio=1.9`, `F060_trend_lookback_bars=20.0`, `F060_trend_min_rise_pct=1.15`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F060_engulf_mode=2.0`, `F060_min_body_pct=55.0`, `F060_min_engulf_ratio=2.0`, `F060_trend_lookback_bars=19.0`, `F060_trend_min_rise_pct=0.55`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.10 F059 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.10 Run F059_ENGULFBULL_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_10_f059_audit_20260623T213000Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F059_engulfbull_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F059_engulfbull_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F059_engulf_mode=2.0`, `F059_min_body_pct=35.0`, `F059_min_engulf_ratio=1.8`, `F059_trend_lookback_bars=8.0`, `F059_trend_min_drop_pct=0.4`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F059_engulf_mode=2.0`, `F059_min_body_pct=50.0`, `F059_min_engulf_ratio=1.5`, `F059_trend_lookback_bars=15.0`, `F059_trend_min_drop_pct=0.75`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.11 Run F060_ENGULFBEAR_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.9 F058 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_9_f058_audit_20260623T211900Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F058_shootingstar_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F058_shootingstar_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F058_body_zone_pct=45.0`, `F058_lower_wick_max_pct=20.0`, `F058_trend_lookback_bars=20.0`, `F058_trend_min_rise_pct=0.45`, `F058_upper_wick_min_pct=85.0`, `F058_wick_body_ratio=5.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F058_body_zone_pct=40.0`, `F058_lower_wick_max_pct=5.0`, `F058_trend_lookback_bars=13.0`, `F058_trend_min_rise_pct=0.15`, `F058_upper_wick_min_pct=80.0`, `F058_wick_body_ratio=4.5`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.10 Run F059_ENGULFBULL_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.8 F057 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.8 Run F057_HAMMER_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_8_f057_audit_20260623T205000Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F057_hammer_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F057_hammer_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F057_body_zone_pct=20.0`, `F057_lower_wick_min_pct=70.0`, `F057_trend_lookback_bars=10.0`, `F057_trend_min_drop_pct=1.35`, `F057_upper_wick_max_pct=25.0`, `F057_wick_body_ratio=5.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F057_body_zone_pct=20.0`, `F057_lower_wick_min_pct=50.0`, `F057_trend_lookback_bars=11.0`, `F057_trend_min_drop_pct=0.45`, `F057_upper_wick_max_pct=10.0`, `F057_wick_body_ratio=3.5`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.7 F056 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_7_f056_audit_20260623T203800Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F056_pinbear_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F056_pinbear_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F056_body_zone_pct=40.0`, `F056_min_range_pct=0.37`, `F056_opposite_wick_max_pct=20.0`, `F056_wick_body_ratio=1.5`, `F056_wick_min_pct=55.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F056_body_zone_pct=20.0`, `F056_min_range_pct=0.17`, `F056_opposite_wick_max_pct=15.0`, `F056_wick_body_ratio=4.5`, `F056_wick_min_pct=55.0`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.8 Run F057_HAMMER_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.6 F055 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.6 Run F055_PINBULL_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_6_f055_audit_20260623T202700Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F055_pinbull_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F055_pinbull_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F055_body_zone_pct=40.0`, `F055_min_range_pct=0.19`, `F055_opposite_wick_max_pct=15.0`, `F055_wick_body_ratio=4.5`, `F055_wick_min_pct=85.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F055_body_zone_pct=50.0`, `F055_min_range_pct=0.69`, `F055_opposite_wick_max_pct=0.0`, `F055_wick_body_ratio=3.0`, `F055_wick_min_pct=75.0`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.5 F054 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_5_f054_audit_20260623T201700Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F054_insidebar_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F054_insidebar_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F054_containment_mode=2.0`, `F054_max_inside_range_ratio=0.7`, `F054_mother_min_range_pct=1.46`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F054_containment_mode=1.0`, `F054_max_inside_range_ratio=0.55`, `F054_mother_min_range_pct=1.22`.
3. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.6 Run F055_PINBULL_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.4 F053 calibration closed

Status: `CLOSED_NO_GO_FIX_APPLIED`.
Closed: `8.2.4 Run F053_DOJI_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.

Final LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F053_doji_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F053_doji_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: OOS `0.0`, trades `0`, selected params `F053_max_body_pct=15.0`, `F053_min_range_pct=0.37`, `F053_wick_balance_max_pct=45.0`, `F053_wick_mode=2.0`.
2. SHORT: OOS `0.0`, trades `0`, selected params `F053_max_body_pct=10.0`, `F053_min_range_pct=0.31`, `F053_wick_balance_max_pct=55.0`, `F053_wick_mode=1.0`.
3. decision: `NO_GO_FOR_ML`.
4. readiness freeze restored after parallel temporary-unlock race.

Important command rule:
1. Do not run two `-UseTemporaryUnlock` process-pool jobs in parallel.
2. The launcher now rejects a second live temporary unlock before worker start.
3. Run LONG and SHORT sequentially when `-UseTemporaryUnlock` is required.

Next strict WBS item:

`8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`

## Current Active Command 2026-06-23: stage 8.2.3 F052 validation closed

Status: `CLOSED_VALIDATION_FAIL_NO_ML_GO`.
Closed: `8.2.3 Validate F052_CHOCH_ALLOW LONG on adjacent/rolling window`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_3_f052_fixed_validation_audit_20260623T194700Z.md`.

Fixed params:

```powershell
$params = '{\"F052_break_buffer_pct\":0.29,\"F052_choch_dir\":1.0,\"F052_confirm_bars\":2.0,\"F052_require_opposite_bias\":1.0,\"F052_structure_scope\":1.0}'
```

Validation window preflight:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m mlbotnav.preflight_window --symbol SOLUSDT --timeframe 1m --train-start 2026-05-04 --train-end 2026-05-17 --test-day 2026-05-18 --test-end-day 2026-05-24 --min-train-rows 900 --n-folds 2 --horizons-grid 1,2,3,4,5,6,8,12,16 --layer core
```

Final validation artifacts:
1. pipeline report: `reports/pipeline/pipeline_report_SOLUSDT_1m_20260623T194439Z.json`.
2. OOS report: `reports/final_review/oos_report_SOLUSDT_1m_2026-05-18_to_2026-05-24_long_only_20260623T194451Z.json`.
3. OOS CSV: `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-18_to_2026-05-24_long_only_20260623T194451Z.csv`.

Contract command:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path reports\final_review\oos_backtest_trades_SOLUSDT_1m_2026-05-18_to_2026-05-24_long_only_20260623T194451Z.csv --out-dir reports\qa_gate
```

Result:
1. train gate: `false`.
2. OOS net return: `-5.696708101293968`.
3. OOS trades: `1`.
4. OOS goal pass: `false`.
5. decision: `VALIDATION_FAIL_NO_ML_GO`.
6. final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T195125Z.json`.

Do not build an ML package from this F052 validation. Do not add it to approved registry. Do not ingest it into ML.

Next strict WBS item: continue with the next user-selected passport/action discovery, or define a new validation idea with its own audit boundary.

## Current Active Command 2026-06-23: stage 8.2.2 F052 calibration closed

Status: `CLOSED_POSITIVE_TEST_CANDIDATE_NEEDS_VALIDATION`.
Closed: `8.2.2 Run F052_CHOCH_ALLOW large-window candidate`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_2_f052_audit_20260623T193700Z.md`.

Final valid LONG command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F052_choch_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Final valid SHORT command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F052_choch_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. LONG: `goal_pass`, OOS `+5.3486475132039635`, trades `1`.
2. LONG caveat: `train_gate_pass=false`, only `1` OOS trade, exit reason `timeout`.
3. SHORT: `goal_fail`, OOS `0.0`, trades `0`.
4. final data layer: `core` in search/train/OOS.

Do not build an ML package automatically from this run. Do not start ML training.

Next strict WBS item: manual decision: validate F052 LONG, explicitly approve draft package build, or continue next passport/action discovery.

## Current Active Command 2026-06-23: stage 8.2.1 F050 calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2.1 Run next passport/action candidate after F051 no-go`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_1_f050_audit_20260623T192700Z.md`.

Final valid command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F050_bosup_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. process pool status: `OK`.
2. final data layer: `core` in search/train/OOS.
3. best OOS net return: `0.0`.
4. best OOS trades: `0`.
5. decision: `NO_GO_FOR_ML`.

Next strict WBS item:

`8.2.2 Run F052_CHOCH_ALLOW large-window candidate`

Prepared next command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F052_choch_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Do not build an ML package from F050. Do not start ML training from F050.

## Current Active Command 2026-06-23: stage 8.2 Optuna calibration closed

Status: `CLOSED_NO_GO`.
Closed: `8.2 Run Optuna calibration`.
Audit: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_audit_20260623T191900Z.md`.

Final valid command:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-24 -TestStart 2026-05-25 -TestEnd 2026-05-31 -WindowPolicy multiday -GoalNetReturnPct 1 -Threads 6 -SearchWorkers 6 -ProcessWorkers 2 -SearchWorkersPerProcess 3 -OptunaTrials 40 -OptunaTimeoutSec 900 -CalibrationMatrixPath configs\calibration_matrices\passport_actions\F051_bosdown_entry_filter.yaml -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -UseTemporaryUnlock
```

Result:
1. process pool status: `OK`.
2. final data layer: `core` in search/train/OOS.
3. best OOS net return: `0.0`.
4. best OOS trades: `0`.
5. decision: `NO_GO_FOR_ML`.

Validation commands:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m py_compile src\mlbotnav\adaptive_auto_train.py src\mlbotnav\optuna_search_candidate.py src\mlbotnav\search_gate_candidate.py src\mlbotnav\oos_evaluate.py
```

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest tests\test_cycle_preflight_integration.py tests\test_optuna_search_runtime.py tests\test_ml_alignment_data_windows_audit.py tests\test_ml_trade_dataset_contract.py -q
```

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_large_clean_window_manifest_audit --manifest-path configs\ml_large_clean_window_manifest.yaml --out-dir reports\qa_gate
```

Do not build an ML package from this run. Do not start ML training from this run.

Next strict WBS item: manual decision for next passport/action calibration target or revised `8.2` candidate run.

## Current Active Command 2026-06-23: stage 8.1 large clean window closed

Status: `CLOSED_PASS`.
Closed: `8.1 Fix large clean window`.
Audit: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.
Manifest: `configs/ml_large_clean_window_manifest.yaml`.

Window:
1. train/calibration: `2026-05-11..2026-05-24`.
2. test/OOS: `2026-05-25..2026-05-31`.
3. data layer: `core`.

Audit command:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_large_clean_window_manifest_audit --manifest-path configs\ml_large_clean_window_manifest.yaml --out-dir reports\qa_gate
```

Final checks:
1. Large clean window audit: `PASS`.
2. Missing core OHLCV files: `0`.
3. New tests: `4/4 OK`.
4. Focused smoke/ingest tests: `22/22 OK`.

Next strict WBS item:

`8.2 Run Optuna calibration`

Do not run ML training yet. Optuna calibration is the next separate WBS item.

## Current Active Command 2026-06-23: stage 7 closeout

Status: `STAGE_7_CLOSED_PASS`.
Closed: `7.6 Stage 7 closeout`.
Audit: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.

Closed bridge:
`window -> package -> approved registry -> ML ingest dataset`.

Dataset:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.

Final checks:
1. Smoke window audit: `PASS`.
2. Approved registry: `PASS`, approved count `1`.
3. ML ingest dataset builder: `PASS`, rows `1177`.
4. Dataset contract: `PASS`.
5. Focused Stage 7 tests: `67/67 OK`.

Next strict WBS item:

`8.1 Fix large clean window`

Do not run ML training yet. Stage 8 starts with fixing the larger clean window.

## Current Active Command 2026-06-23: stage 7.5 ML ingest closed

Status: `CLOSED_PASS`.
Closed: `7.5 Run ML ingest`.
Audit: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.
Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.
Dataset manifest: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`.

Dataset builder command:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_approved_trade_dataset_builder --registry-path configs\ml_approved_calibration_packages.yaml --out-dir reports\ml_datasets --dataset-name smoke_stage_7_5_SOLUSDT_1m_20260527_short_only --report-dir reports\qa_gate
```

Dataset contract command:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path reports\ml_datasets\smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv --out-dir reports\qa_gate
```

Final checks:
1. Dataset builder: `PASS`, packages total `1`, rows total `1177`.
2. Dataset contract: `PASS`, rows `1177`.
3. Registry validator/reader/admission status: `PASS`.
4. Focused ingest tests: `24/24 OK`.

Next strict WBS item:

`7.6 Stage 7 closeout`

Do not run ML training yet.

## Current Active Command 2026-06-23: stage 7.4 approved registry closed

Status: `CLOSED_PASS`.
Closed: `7.4 Add package to approved registry`.
Audit: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.
Approved package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Registry validator command:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_approval_registry_validator --registry-path configs\ml_approved_calibration_packages.yaml --out-dir reports\qa_gate
```

Admission status command:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_alignment_admission_status_audit --registry-path configs\ml_approved_calibration_packages.yaml --out-dir reports\qa_gate
```

Final checks:
1. Registry validator: `PASS`, approved count `1`.
2. Admission status: `PASS`, packages total `1`.
3. Registry reader: `PASS`, approved count `1`.
4. Package contract and alignment audits: `PASS`.
5. Focused tests: `42/42 OK`.

Next strict WBS item:

`7.5 Run ML ingest`

Do not run ML training yet. Dataset builder / ML ingest is the next separate WBS item.

## Current Active Command 2026-06-23: stage 7.3 package contract closed

Status: `CLOSED_PASS`.
Closed: `7.3 Run package contract audit`.
Audit: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.
Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Package status: `DRAFT`.
Package ML decision: `NO_GO_FOR_ML`.

Contract command:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path reports\ml_candidates\smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z\trade_log.csv --out-dir reports\qa_gate
```

Final checks:
1. Contract audit: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T183343Z.json`.
2. Package alignment audits: `PASS`.
3. Registry validator/reader: `PASS`.
4. Dataset builder: `PASS / NO_APPROVED_PACKAGES`.
5. Focused tests: `48/48 OK`.
6. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T183955Z.json`.

Next strict WBS item:

`7.4 Add package to approved registry`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training yet.

## Current Active Command 2026-06-23: stage 7.2 smoke package closed

Status: `CLOSED_PASS`.
Closed: `7.2 Build test package`.
Audit: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.
Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Package status: `DRAFT`.
Package ML decision: `NO_GO_FOR_ML`.

Package contract command:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path reports\ml_candidates\smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z\trade_log.csv --out-dir reports\qa_gate
```

Checks:
1. Contract audit: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T182844Z.json`.
2. Alignment audits: `PASS`.
3. Focused tests: `42/42 OK`.
4. Registry remains empty and valid.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T182902Z.json`.

Next strict WBS item:

`7.3 Run package contract audit`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training yet.

## Current Active Command 2026-06-23: stage 7.1 smoke window closed

Status: `CLOSED_PASS`.
Closed: `7.1 Smoke run`.
Audit: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.
Manifest: `configs/ml_smoke_run_manifest.yaml`.

Selected clean smoke window:
1. `SOLUSDT`, `1m`, `core`.
2. Train: `2026-05-25..2026-05-26`.
3. Test: `2026-05-27..2026-05-27`.

Validation command:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_smoke_window_manifest_audit --manifest-path configs\ml_smoke_run_manifest.yaml --out-dir reports\qa_gate
```

Checks:
1. Smoke manifest audit: `PASS`, report `reports/qa_gate/ml_smoke_window_manifest_audit_20260623T182159845644Z.json`.
2. New tests: `5/5 OK`.
3. Focused ML smoke/alignment tests: `78/78 OK`.
4. Registry remains empty and valid.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T182218Z.json`.

Next strict WBS item:

`7.2 Build test package`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training yet.





## Current Active Command 2026-06-23: stage 6 closeout

Status: `STAGE_6_CLOSED_PASS`.
Closed: `6.6 Stage 6 closeout`.
Audit: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.

Closed Stage 6 items:
1. `6.1`
2. `6.2`
3. `6.3`
4. `6.4`
5. `6.5`
6. `6.6`

Checks:
1. Focused ML tests: `121/121 OK`.
2. All five alignment audits: `PASS / NO_APPROVED_PACKAGES`.
3. Registry validator: `PASS`.
4. Registry reader: `PASS`.
5. Dataset builder: `PASS / NO_APPROVED_PACKAGES`.
6. Reject-log builder: `PASS / NO_REJECTIONS`.

Next strict WBS item:

`7.1 Smoke run`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training before smoke-run plan says so.


## Current Active Command 2026-06-23: stage 6.5 admission status closed

Status: `CLOSED_PASS`.
Closed: `6.5 Check admission status`.
Audit: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.

Created:
1. `src/mlbotnav/ml_alignment_admission_status_audit.py`
2. `tests/test_ml_alignment_admission_status_audit.py`

Checks:
1. New tests: `6/6 OK`.
2. Focused ML tests: `121/121 OK`.
3. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_admission_status_audit_20260623T180909527952Z.json`.

Next strict WBS item:

`6.6 Stage 6 closeout`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training; Stage 6 closeout is next.


## Current Active Command 2026-06-23: stage 6.4 data windows alignment closed

Status: `CLOSED_PASS`.
Closed: `6.4 Check data windows`.
Audit: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.

Created:
1. `src/mlbotnav/ml_alignment_data_windows_audit.py`
2. `tests/test_ml_alignment_data_windows_audit.py`

Checks:
1. New tests: `8/8 OK`.
2. Focused ML tests: `115/115 OK`.
3. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_data_windows_audit_20260623T154607261155Z.json`.

Next strict WBS item:

`6.5 Check admission status`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training; Stage 6 alignment audit continues first.


## Current Active Command 2026-06-23: stage 6.3 calibration params alignment closed

Status: `CLOSED_PASS`.
Closed: `6.3 Check calibration params`.
Audit: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.

Created:
1. `src/mlbotnav/ml_alignment_calibration_params_audit.py`
2. `tests/test_ml_alignment_calibration_params_audit.py`

Checks:
1. New tests: `7/7 OK`.
2. Focused ML tests: `107/107 OK`.
3. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_calibration_params_audit_20260623T154050444104Z.json`.

Next strict WBS item:

`6.4 Check data windows`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training; Stage 6 alignment audit continues first.


## Current Active Command 2026-06-23: stage 6.2 passport context alignment closed

Status: `CLOSED_PASS`.
Closed: `6.2 Check passport context`.
Audit: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.

Created:
1. `src/mlbotnav/ml_alignment_passport_context_audit.py`
2. `tests/test_ml_alignment_passport_context_audit.py`

Checks:
1. New tests: `6/6 OK`.
2. Focused ML tests: `100/100 OK`.
3. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_passport_context_audit_20260623T153553932585Z.json`.

Next strict WBS item:

`6.3 Check calibration params`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training; Stage 6 alignment audit continues first.

## Current Active Command 2026-06-23: stage 6.1 run_id alignment closed

Status: `CLOSED_PASS`.
Closed: `6.1 Check run_id alignment`.
Audit: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.

Created:
1. `src/mlbotnav/ml_alignment_run_id_audit.py`
2. `tests/test_ml_alignment_run_id_audit.py`

Checks:
1. New tests: `5/5 OK`.
2. Focused ML tests: `94/94 OK`.
3. Real registry run: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_alignment_run_id_audit_20260623T152715670875Z.json`.

Next strict WBS item:

`6.2 Check passport context`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training; Stage 6 alignment audit continues first.

## Current Active Command 2026-06-23: stage 5 closeout

Status: `STAGE_5_CLOSED_PASS`.
Closed: `5.6 Stage 5 closeout`.
Audit: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.

Closed Stage 5 items:
1. `5.1`
2. `5.2`
3. `5.3`
4. `5.4`
5. `5.5`
6. `5.6`

Checks:
1. Focused tests: `89/89 OK`.
2. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T152045Z.json`.
3. Registry reader: `PASS`, report `reports/qa_gate/ml_approved_package_registry_reader_20260623T152045217551Z.json`.
4. Dataset builder: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T152111078301Z.json`.
5. Reject-log builder: `PASS / NO_REJECTIONS`, report `reports/qa_gate/ml_rejection_reason_log_20260623T152111079049Z.json`.
6. Old root `reports/optuna` denied: expected `FAIL`, report `reports/qa_gate/ml_ingest_source_policy_20260623T152122738533Z.json`.
7. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.

Next strict WBS item:

`6.1 Check run_id alignment`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training; Stage 6 alignment audit comes first.

## Current Active Command 2026-06-23: rejection reasons step 5.5 closed

Status: `CLOSED_PASS`.
Closed: `5.5 Add rejection reasons`.
Audit: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.

Created:
1. `src/mlbotnav/ml_rejection_reason_log.py`
2. `tests/test_ml_rejection_reason_log.py`

Real reject-log smoke:
1. Status: `PASS`.
2. Reason: `NO_REJECTIONS`.
3. Report: `reports/qa_gate/ml_rejection_reason_log_20260623T151618705623Z.json`.
4. Log: `reports/ml_rejections/ml_rejection_reasons_20260623T151618703912Z.json`.
5. Rejections total: `0`.

Checks:
1. New rejection reason tests: `4/4 OK`.
2. Focused tests: `89/89 OK`.
3. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T151814Z.json`.
4. Reject-log smoke: `PASS / NO_REJECTIONS`, report `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`.
5. Reject log: `reports/ml_rejections/ml_rejection_reasons_20260623T151814360422Z.json`.
6. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.

Next strict WBS item:

`5.6 Stage 5 closeout`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training until Stage 5 is closed and audited.

## Current Active Command 2026-06-23: ML trade dataset assembly step 5.4 closed

Status: `CLOSED_PASS`.
Closed: `5.4 Implement ML dataset assembly`.
Audit: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.

Created:
1. `src/mlbotnav/ml_approved_trade_dataset_builder.py`
2. `tests/test_ml_approved_trade_dataset_builder.py`

Real builder smoke:
1. Status: `PASS`.
2. Reason: `NO_APPROVED_PACKAGES`.
3. Report: `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T150934741093Z.json`.
4. Rows total: `0`.

Checks:
1. New builder tests: `3/3 OK`.
2. Focused tests: `85/85 OK`.
3. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T151131Z.json`.
4. Builder smoke: `PASS / NO_APPROVED_PACKAGES`, report `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.

Next strict WBS item:

`5.5 Add rejection reasons`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML training until Stage 5 is closed and audited.

## Current Active Command 2026-06-23: approved package registry reader step 5.3 closed

Status: `CLOSED_PASS`.
Closed: `5.3 Implement registry reading`.
Audit: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.

Created:
1. `src/mlbotnav/ml_approved_package_registry_reader.py`
2. `tests/test_ml_approved_package_registry_reader.py`

Real registry reader:
1. Status: `PASS`.
2. Report: `reports/qa_gate/ml_approved_package_registry_reader_20260623T145755674743Z.json`.
3. Approved count: `0`.

Checks:
1. New reader tests: `3/3 OK`.
2. Focused tests: `82/82 OK`.
3. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T150239Z.json`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.

Next strict WBS item:

`5.4 Implement ML dataset assembly`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML ingest/training until dataset assembly is implemented and audited.

## Current Active Command 2026-06-23: ML ingest source policy step 5.2 closed

Status: `CLOSED_PASS`.
Closed: `5.2 Block direct Optuna/report reading for ML ingest`.
Audit: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.

Created:
1. `src/mlbotnav/ml_ingest_source_policy.py`
2. `tests/test_ml_ingest_source_policy.py`

Forbidden direct roots:
1. `reports/optuna`
2. `reports/pipeline`
3. `reports/final_review`

Allowed source smoke: `PASS`, report `reports/qa_gate/ml_ingest_source_policy_20260623T145309955779Z.json`.
Forbidden source smoke: expected `FAIL`, report `reports/qa_gate/ml_ingest_source_policy_20260623T145318504657Z.json`.

Checks:
1. Focused tests: `79/79 OK`.
2. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T145329Z.json`.
3. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T145330Z.json`.

Next strict WBS item:

`5.3 Implement registry reading`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML ingest/training until Stage 5 route is implemented and audited.

## Current Active Command 2026-06-23: ML ingest entry point step 5.1 closed

Status: `CLOSED_PASS`.
Closed: `5.1 Find current ML ingest entry point`.
Audit: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.

Current primary ML training ingest entry point:

`src/mlbotnav/pipeline_train_eval.py`

Current orchestrators:
1. `src/mlbotnav/prod_cycle.py`
2. `src/mlbotnav/stage_ladder.py`
3. `src/mlbotnav/adaptive_auto_train.py`

Current gap:
1. ML training route does not read `configs/ml_approved_calibration_packages.yaml`.
2. ML training route does not assemble from `reports/ml_candidates/<run_id>/trade_log.csv`.

Next strict WBS item:

`5.2 Block direct Optuna/report reading for ML ingest`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML ingest/training until Stage 5 route is implemented and audited.

## Current Active Command 2026-06-23: ML approval registry stage 4 closed

Status: `STAGE_4_CLOSED_PASS`.
Closed: `4.5 Stage 4 closeout`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.

Registry:
1. `configs/ml_approved_calibration_packages.yaml`
2. `approved_packages: []`
3. Approved count: `0`
4. Deny result: `ML_ADMISSION_DENY`

Checks:
1. `py_compile PASS`.
2. Registry validator: `PASS`, report `reports/qa_gate/ml_approval_registry_validator_20260623T143952Z.json`.
3. Focused tests: `74/74 OK`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T144002Z.json`.

Next strict WBS item:

`5.1 Find current ML ingest entry point`

Do not add packages to `approved_packages` without separate manual approval. Do not run ML ingest before Stage 5 route is implemented.

## Current Active Command 2026-06-23: ML approval registry step 4.4 closed

Статус: `CLOSED_PASS`.
Закрыто: `4.4 Сделать validator registry`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.

Созданы файлы:
1. `src/mlbotnav/ml_approval_registry_validator.py`
2. `tests/test_ml_approval_registry_validator.py`

Real registry validation:
1. Report: `reports/qa_gate/ml_approval_registry_validator_20260623T143704Z.json`.
2. Status: `PASS`.
3. Approved count: `0`.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `74/74 OK`.
3. Registry validator: `PASS`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T143705Z.json`.

Следующий строгий WBS-пункт:

`4.5 Закрытие этапа 4`

Не добавлять package в `approved_packages` без отдельного ручного approval.

## Current Active Command 2026-06-23: ML approval registry step 4.3 closed

Статус: `CLOSED_PASS`.
Закрыто: `4.3 Добавить запреты registry`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.

Обновлен файл:
`configs/ml_approved_calibration_packages.yaml`

Запреты:
1. Deny result: `ML_ADMISSION_DENY`.
2. Forbidden statuses: `DRAFT`, `NEEDS_AUDIT`, `NO_GO`, `VALIDATION_FAIL`, `REJECTED`, `UNKNOWN`.
3. Contract audit must be `PASS`.
4. Manifest must be valid.
5. `raw/quarantine` is banned as clean ML input.

Проверки:
1. YAML parse: `PASS`.
2. Registry bans parse/check: `PASS`.
3. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T143132Z.json`.

Следующий строгий WBS-пункт:

`4.4 Сделать validator registry`

Не добавлять package в `approved_packages` без отдельного ручного approval.

## Current Active Command 2026-06-23: ML approval registry step 4.2 closed

Статус: `CLOSED_PASS`.
Закрыто: `4.2 Описать формат registry`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.

Обновлен файл:
`configs/ml_approved_calibration_packages.yaml`

Формат описан в комментариях:
1. `run_id`
2. `status`
3. `package_path`
4. `approved_by`
5. `approved_utc`
6. `comment`

Проверки:
1. YAML parse: `PASS`.
2. Approved packages count: `0`.
3. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T142740Z.json`.

Следующий строгий WBS-пункт:

`4.3 Добавить запреты registry`

Не добавлять package в `approved_packages` без отдельного ручного approval.

## Current Active Command 2026-06-23: ML approval registry step 4.1 closed

Статус: `CLOSED_PASS`.
Закрыто: `4.1 Создать registry файл`.
Audit: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.

Создан файл:
`configs/ml_approved_calibration_packages.yaml`

Текущее содержимое:
1. `schema_version: 1`
2. `registry_status: EMPTY_NO_APPROVED_PACKAGES`
3. `manual_approval_required: true`
4. `approved_packages: []`

Проверки:
1. YAML parse: `PASS`.
2. Approved packages count: `0`.
3. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T142350Z.json`.

Следующий строгий WBS-пункт:

`4.2 Описать формат registry`

Не добавлять package в `approved_packages` без отдельного ручного approval.

## Current Active Command 2026-06-23: ML candidate package stage 3 closed

Статус: `STAGE_3_CLOSED_PASS`.
Закрыто: `3.7 Закрытие этапа 3`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.

Candidate package:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Проверки:
1. Required files: `PASS`.
2. Manifest: `PASS`.
3. Trade log contract: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T141708Z.json`.
4. Focused tests: `71/71 OK`.
5. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T141945Z.json`.

Следующий строгий WBS-пункт:

`4.1 Создать registry файл`

Не делать `APPROVED_FOR_ML` автоматически: Stage 4 начинается с ручного registry.

## Current Active Command 2026-06-23: ML candidate package step 3.6 closed

Статус: `CLOSED_PASS`.
Закрыто: `3.6 Добавить audit.md`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.

Создан файл:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/audit.md`

Содержимое:
1. ML decision: `NO_GO_FOR_ML`.
2. Review state: `READY_FOR_MANUAL_REVIEW`.
3. Reason: package is `DRAFT` and requires manual approval.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `71/71 OK`.
3. Package audit content check: `PASS`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T141517Z.json`.

Следующий строгий WBS-пункт:

`3.7 Закрытие этапа 3`

Не делать `APPROVED_FOR_ML` в этом пункте: это отдельный ручной этап.

## Current Active Command 2026-06-23: ML candidate package step 3.5 closed

Статус: `CLOSED_PASS`.
Закрыто: `3.5 Добавить manifest.json`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.

Создан файл:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/manifest.json`

Проверки:
1. `py_compile PASS`.
2. Focused tests: `69/69 OK`.
3. Manifest JSON parse/content audit: `PASS`.
4. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T140937Z.json`.

Следующий строгий WBS-пункт:

`3.6 Добавить audit.md`

Не делать `APPROVED_FOR_ML` в этом пункте: это отдельный ручной этап.

## Current Active Command 2026-06-23: ML candidate package step 3.4 closed

Статус: `CLOSED_PASS`.
Закрыто: `3.4 Добавить исходные отчеты`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.

Созданы файлы:
1. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports.json`
2. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/oos_report.json`
3. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/pipeline_report.json`

Опциональный `optuna_report.json`: `NOT_PROVIDED`.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `67/67 OK`.
3. `text_guard PASS`: `reports/qa_gate/recovery_r5_text_guard_20260623T140326Z.json`.

Следующий строгий WBS-пункт:

`3.5 Добавить manifest.json`

Не создавать `audit.md` пакета и не делать `APPROVED_FOR_ML` в этом пункте: они идут отдельными шагами.

## Current Active Command 2026-06-23: ML candidate package step 3.3 closed

Статус: `CLOSED_PASS`.
Закрыто: `3.3 Добавить trade_log.csv`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.

Создан файл:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/trade_log.csv`

Contract validation:
1. Status: `PASS`.
2. Rows total: `1177`.
3. Failed rows: `0`.
4. Missing columns: `0`.
5. Report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T134753Z.json`.

Проверки:
1. `py_compile PASS`.
2. Focused tests: `65/65 OK`.

Следующий строгий WBS-пункт:

`3.4 Добавить исходные отчеты`

Не создавать `manifest.json`, `audit.md` и не делать `APPROVED_FOR_ML` в этом пункте: они идут отдельными шагами.

## Closed Historical Command 2026-06-23: ML candidate package step 3.2 closed

Статус: `CLOSED_PASS`.
Закрыто: `3.2 Добавить calibration_package.json`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.

Следующий строгий WBS-пункт: `3.3 Добавить trade_log.csv`.

## Closed Historical Command 2026-06-23: ML candidate package step 3.1 closed

Статус: `CLOSED_PASS`.
Закрыто: `3.1 Создать структуру пакета`.
Audit: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.

Следующий строгий WBS-пункт: `3.2 Добавить calibration_package.json`.

## Closed Historical Command 2026-06-23: ML contract stage 2 closed

Статус: `STAGE_2_CLOSED_PASS`.
Закрыто: `2.9 Закрытие этапа 2`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.

Следующий строгий WBS-пункт: `3.1 Создать структуру пакета`.

## Closed Historical Command 2026-06-23: ML contract step 2.8 closed

Статус: `CLOSED_PASS`.
Закрыто: `2.8 Проверить OOS CSV`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.

Следующий строгий WBS-пункт: `2.9 Закрытие этапа 2`.

## Closed Historical Command 2026-06-23: ML contract step 2.7 closed

Статус: `CLOSED_PASS_AFTER_CONTROLLED_TEMP_UNLOCK`.
Закрыто: `2.7 Проверить pipeline CSV`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.

Следующий строгий WBS-пункт: `2.8 Проверить OOS CSV`.

## Closed Historical Command 2026-06-23: ML contract step 2.6 closed

Закрыто: `2.6 Добавить MAE/MFE`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.

Следующий строгий WBS-пункт: `2.7 Проверить pipeline CSV`.

## Closed Historical Command 2026-06-23: ML contract step 2.5 closed

Закрыто: `2.5 Добавить hit labels`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.

Следующий строгий WBS-пункт: `2.6 Добавить MAE/MFE`.

## Closed Historical Command 2026-06-23: ML contract step 2.3 closed

Закрыто: `2.3 Добавить trade identity`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.

Следующий строгий WBS-пункт: `2.4 Добавить duration labels`.

## Closed Historical Command 2026-06-23: ML contract step 2.2 closed

Закрыто: `2.2 Добавить passport context`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.

Следующий строгий WBS-пункт: `2.3 Добавить trade identity`.

## Closed Historical Command 2026-06-23: ML contract step 2.1 closed

Закрыто: `2.1 Добавить run-level context`.
Audit: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.

Следующий строгий WBS-пункт:

`2.2 Добавить passport context`

Не запускать большой calibration/OOS прогон: Stage 2 еще не закрыт, passport context и trade labels еще не добавлены.

## Closed Historical Command 2026-06-23: ML contract stage 1 closed

Закрыто: `1.7 Закрытие этапа 1`.
Closeout artifact: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.

Следующий строгий WBS-пункт:

`2.1 Добавить run-level context`

Не запускать большой calibration/OOS прогон до закрытия Stage 2: реальные `backtest_trades_*.csv` и `oos_backtest_trades_*.csv` еще должны получить поля контракта.

Текущая проверка контракта:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.ml_trade_dataset_contract --csv-path <trade_log.csv> --out-dir reports\qa_gate
```

## Базовое окружение
```powershell
Set-Location C:\Users\007\Desktop\MLbotNav
$env:PYTHONPATH='src'
```

## Health checks
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.text_guard --out-dir reports/qa_gate
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.readiness --show --write-report true
.\.venv\Scripts\python.exe -m pip check
```

## Current Active Command 2026-06-22: F001 passport-action baseline

Правило:
использовать только паспортную матрицу. Старые full/catalog/feature_sweep матрицы считать `legacy/frozen` для новых baseline-прогонов.

Активный реестр:
```powershell
Get-Content .\configs\calibration_action_passports.yaml
```

Активная F001 matrix:
```powershell
$matrix = 'configs\calibration_matrices\passport_actions\F001_ret1_entry_filter.yaml'
```

Compile-check:
```powershell
$env:PYTHONPATH='src'
@'
from pathlib import Path
from mlbotnav.optuna_space import load_calibration_matrix, compile_optuna_space
root = Path.cwd()
m = load_calibration_matrix(root, rel_path='configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml')
for mode in ['long_only','short_only']:
    s = compile_optuna_space(m, contour_id=mode, min_enabled_blocks=1, grid_preset='wide')
    print(mode, sorted(s['profiles'].keys()), s['passport_mode'])
'@ | .\.venv\Scripts\python.exe -
```

Baseline LONG command:
```powershell
$env:PYTHONPATH='src'
$matrix = 'configs\calibration_matrices\passport_actions\F001_ret1_entry_filter.yaml'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Важно:
не добавлять `-DisableTimeoutExit` для baseline. Выходы остаются `TP / SL / timeout`.

## Последняя выполненная команда: H002 short_only stack
```powershell
$matrix = 'configs\calibration_matrices\feature_sweep\h002_price_volatility_ret_3.yaml'
$steps = @(
    @{ Grid = 'narrow'; Trials = 60; Timeout = 300 },
    @{ Grid = 'medium'; Trials = 120; Timeout = 600 },
    @{ Grid = 'wide'; Trials = 180; Timeout = 900 }
)
foreach ($step in $steps) {
    $grid = $step.Grid
    $trials = $step.Trials
    $timeout = $step.Timeout
    powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode short_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials $trials -OptunaTimeoutSec $timeout -CalibrationMatrixPath $matrix -CalibrationGridPreset $grid -ForceProfileEdgeCoverage on -UseTemporaryUnlock
}
```

Результат:
1. `narrow short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w3`, best OOS `-0.2662724500743341%`, trades `2`, class `negative_runtime_ok`.
2. `medium short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w2`, best OOS `-0.2662724500743341%`, trades `2`, class `negative_runtime_ok`.
3. `wide short_only`: launcher `OK`, workers `3/3 exit_code=0`, best worker `w3`, best OOS `-5.42444158059765%`, trades `2`, class `negative_runtime_ok`.
4. Best short stack: `narrow/medium short_only`, `-0.2662724500743341%`, no candidate.
5. Artifact: `reports/qa_gate/h002_short_stack_complete_20260603T154133Z.json`.
6. Sweep table updated: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`.

## Закрытие H002
Artifact: `reports/qa_gate/h002_slot_closeout_20260603T154133Z.json`.

Итог: H002 прошел `long_only` и `short_only` по `narrow/medium/wide` без worker crash. Candidate: `NO_CANDIDATE`. Следующий номер: `H003`.

## Следующая команда: H003 matrix compile
```powershell
$env:PYTHONPATH='src'
# Создать H003 matrix по строке таблицы: block=price_volatility, feature=ret_6, params=return_lookback.
## Visual Entry v3 no-lookahead diagnostic 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY_NO_ML`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_no_lookahead_candidates --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\no_lookahead_candidates_rerun --render-top 5
```

Отчет: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`.

Правило: это DEV diagnostic-only; в ML ничего не передавать.
# Затем compile-check long_only/short_only и записать artifact в reports/qa_gate.
## Visual Entry v3 no-lookahead diagnostic 2026-06-25
Статус: `READY_DIAGNOSTIC_ONLY_NO_ML`.

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_no_lookahead_candidates --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\no_lookahead_candidates_rerun --render-top 5
```

Отчет: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`.

Правило: это DEV diagnostic-only; в ML ничего не передавать.
```

После него: запустить `H003 long_only` полным стеком `narrow -> medium -> wide`.

## Следующая команда: C001 Block 01 LONG wide по CASCADE_BLOCK_CALIBRATION

Назначение:
1. Первый пробный шаг нового каскадного режима.
2. Блок: `price_volatility` / `Цена и волатильность`.
3. Сторона: `LONG`.
4. Сетка: `wide`.
5. После результата нельзя запускать `medium/narrow` вслепую: сначала выбрать лучший `tradeful` кандидат из `wide`.

Команда:
```powershell
$matrix = 'configs\calibration_matrices\catalog_blocks\catalog_block_01_price_volatility.yaml'
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationMatrixPath $matrix -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

Что проверить после запуска:
1. launcher status.
2. workers `3/3`.
3. best OOS и trades.
4. `grid_edge_coverage_audit`: profile coverage и core coverage.
5. Наличие `selected_calibration_params`.
6. Есть ли `tradeful` кандидат для перехода к `medium around best`.
## Visual Entry signal-entry overlay 2026-06-25
Статус: `READY_NEEDS_USER_VISUAL_CONFIRM`.

Команда построения v2-контракта:

```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_signal_entry_overlay --seed-json reports\manual_entries\SOLUSDT_1m_visual_seed_20260625\manual_markup_seed_SOLUSDT_1m_2026-05-12_CORE.json --marked-png reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v1\manual_markup_SOLUSDT_1m_2026-05-12_DEV_marked.png --out-dir reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry --slippage-bps 5
```

Правило: красная `S#` = закрытая сигнальная свеча, зеленая `ENTRY #` = вход на open следующей свечи. Для LONG slippage-aware цена: `entry_open_price * (1 + slippage_bps / 10000)`.

В ML ничего не передавать до ручного подтверждения v2.

