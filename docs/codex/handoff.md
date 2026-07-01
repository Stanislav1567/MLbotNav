# Handoff

## Handoff 2026-07-01 Git Remote Push MLbotNav

Статус: `GIT_REMOTE_PUSH_DONE_MAIN_TRACKS_ORIGIN_MAIN`.

Локальный репозиторий `C:\Users\007\Desktop\MLbotNav` подключен к `origin = https://github.com/Stanislav1567/MLbotNav.git`. Автор локального репозитория: `Stanislav1567 <Stanislav1567@users.noreply.github.com>`.

Первый коммит `e178c49 Initial commit` успешно отправлен в `origin/main`. Ветка `main` отслеживает `origin/main`. Проверено: `git status --short --branch` показывает чистое состояние `main...origin/main`.

Исключения Git сохранены: `.env`, `.venv`, `.vscode`, `data/`, `models/`, `reports/`, `logs/`, `packs/`, `tmp/`, `_codex_offload_*`, `_locked_tmp_*`, backup-файлы. `.gitattributes` добавлен для стабильных окончаний строк.

## Handoff 2026-07-01 Git Init MLbotNav

Статус: `SUPERSEDED_BY_GIT_REMOTE_PUSH_DONE`.

В `C:\Users\007\Desktop\MLbotNav` выполнен `git init`, ветка переименована в `main`. `.gitignore` расширен, чтобы не добавлять в историю `.env`, `.venv`, `.vscode`, `data/`, `models/`, `reports/`, `logs/`, `packs/`, `tmp/`, `_codex_offload_*`, `_locked_tmp_*`, `*.bak-*`. `.env.example` очищен от локального пользовательского пути и оставлен с placeholder.

Проверено: `git check-ignore` подтверждает игнор секретов/артефактов/бэкапов. После добавления `.gitattributes` и расширения backup-ignore в индексе `646` файлов, около `11.12 MB`; backup-файлы не staged. GitHub CLI `gh` не установлен, Git Credential Manager есть. Для коммита нужно настроить `user.name` и `user.email`; для push нужен URL пустого remote-репозитория.

## Handoff 2026-07-01 Strategy Passport Gap Audit

Статус: `STRATEGY_PASSPORT_GAP_AUDIT_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Последняя правка пользователя: V1 визуально норм, но не видно созданные стратегии и паспорта `swing`, `BOS`, `Fibonacci` и т.д.

Ответное действие: создан аудит пропуска. Текущий V1 не является passport overlay; он только рисует evidence-панели и простые подсказки. Не хватает строгого слоя `ALLOW 1/0` по паспортам `F012-F052`, а также матрицы совпадений по 26 ручным входам.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_STRATEGY_PASSPORT_GAP_AUDIT_20260701_RU.md`.

Следующий исполнительный шаг: собрать `INDICATOR_HYPOTHESIS_REVIEW_V2_STRATEGY_PASSPORT_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA` по тем же `M01..M19` и 7 T15. Ручные входы не менять. Scorer, target-lock, Optuna и ML не запускать.

## Handoff 2026-07-01 Codex Agent Launch Kit MLbotNav

Статус: `CODEX_AGENT_LAUNCH_KIT_MLBOTNAV_READY_NO_PROJECT_CODE_CHANGE`.

Для проекта `C:\Users\007\Desktop\MLbotNav` создан отдельный запуск Codex в папке рабочего стола `C:\Users\007\Desktop\Codex Agent`:

1. `Start MLbotNav Codex Agent.cmd`;
2. `Start-MLbotNav-Codex-Agent.ps1`;
3. `Resume MLbotNav Codex Agent.cmd`;
4. `Resume-MLbotNav-Codex-Agent.ps1`.

Проектный `AGENTS.md` уже существовал и не перезаписывался. Глобальный Codex уже содержит trusted-запись для `c:\users\007\desktop\mlbotnav`, профили `agent` и `agent-safe` существуют, авторизация идет через ChatGPT. Проект сейчас не является Git-репозиторием; перед широкими правками агент должен предупреждать и не запускать `git init` без явного согласия пользователя.

## Handoff 2026-07-01 Indicator/Hypothesis Review V1 19+7

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V1_M01_M19_T15V1_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь остановил переход к passport: перед ним нужен отдельный второй слой с RSI/MACD/Fibo/BOS/volume/density по двум эталонам. Создан новый пакет `indicator_hypothesis_review_v1`.

Использовать:

1. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_M01_M19_20260514.png`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_T15_7_20260515.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_ZOOM_T15_7_20260515.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_20260701_RU.md`.

`indicator_hypothesis_review_v0` не использовать как текущий слой для 19+7, потому что он собран до `T15 draft_ledger_v1` и содержит старые T15 времена/22 candidates. Следующий шаг: показать V1 пользователю и ждать `норм/фиксить`. Не запускать scorer, target-lock, Optuna, ML/export.

## Handoff 2026-07-01 T15 Draft Ledger V1 Confirmed

Статус: `T15_DRAFT_LEDGER_V1_USER_CONFIRMED_NEXT_PASSPORT_C01_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь подтвердил `норм` по `draft_ledger_v1`. Рабочий слой: `reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/`.

Дальше идти по рельсам в draft passport по одному кластеру: `T15_C01_SUPPORT_RETEST_LOW`, входы `T15L02`, `T15L08`, `T15L16`.

Не запускать scorer, target-lock, Optuna или ML/export. Цена входа и `entry + 5 bps` остаются только execution/control. EMA не использовать как active condition.

## Handoff 2026-07-01 T15 Draft Ledger V1 Red Arrow Fix

Статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_RED_ARROW_FIX_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь прислал скрин с красными стрелками. Рабочий draft-ledger обновлен с тремя сдвигами:

- `T15L02`: entry `02:35` -> `02:34`;
- `T15L07`: entry `06:23` -> `06:21`;
- `T15L08`: entry `08:32` -> `08:31`.

Остальные входы без изменения. `draft_ledger_v0` superseded для дальнейшего passport discussion.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.json`.

Следующий шаг: показать v1 пользователю и получить `норм / фиксить`. Scorer, target-lock, Optuna и ML/export запрещены.

## Handoff 2026-07-01 T15 Draft Ledger / Cluster Discussion V0

Статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

После `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA` создан draft-ledger по 7 confirmed entries:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Кластеры:

1. `T15_C01_SUPPORT_RETEST_LOW`: `T15L02`, `T15L08`, `T15L16`; первый кандидат для passport discussion.
2. `T15_C02_DEEP_CAPITULATION_LOW`: `T15L06`, `T15L13`; второй кандидат.
3. `T15_C03_HOT_RECLAIM_CONTINUATION`: `T15L07`, `T15L11`; наблюдать, не смешивать в первый паспорт.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.json`.

Следующий шаг: показать пользователю PNG и получить `норм / фиксить`. После подтверждения можно делать draft-паспорт только по одному кластеру, первично `T15_C01_SUPPORT_RETEST_LOW`. Scorer, target-lock, Optuna и ML/export запрещены.

## Handoff 2026-07-01 T15 User Verdict V1

Статус: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: “тут 7 должно входов”. Исправлен слой verdict: все 7 неперечеркнутых кандидатов из feedback v2 теперь `user_confirmed_entry`.

Confirmed entries:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.json`.

`user_verdict_v0` superseded и не должен использоваться как рабочий слой. Следующий шаг: draft-ledger/cluster discussion по всем 7 entries. Не запускать target-lock/scorer/Optuna/ML.

## Handoff 2026-07-01 Indicator/Hypothesis Visual Review V0

Статус: `INDICATOR_HYPOTHESIS_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Добавлен модуль:
`src/mlbotnav/visual_entry_indicator_hypothesis_review.py`.

Назначение: визуально сравнить manual gold `2026-05-14` и актуальный feedback `2026-05-15` через RSI14, MACD, volume, density, trailing swing, BOS и Fibo. Это не scorer и не ML.

Команды:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m py_compile src\mlbotnav\visual_entry_indicator_hypothesis_review.py
.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_indicator_hypothesis_review
```

Главные PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260514.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_PENDING_ZOOM_20260515.png`.

Следующий шаг: показать пользователю эти PNG, получить ручной verdict по инструментам и pending `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16`. До этого не делать scorer/target-lock/ML/Optuna.

Ассистентский verdict сохранен:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_ASSISTANT_VERDICT_20260701_RU.md`.

Рабочий вывод: простые индикаторы не разделяют good/bad; следующий безопасный шаг - приоритетный zoom-review `T15L06`, `T15L13`, `T15L16`.

## Handoff 2026-07-01 T15 Priority Zoom Review V0

Статус: `T15_PRIORITY_ZOOM_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Добавлен модуль:
`src/mlbotnav/visual_entry_priority_zoom_review.py`.

Главный sheet:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_SHEET_20260515.png`.

Отдельные PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L06_PRIORITY_ZOOM_REVIEW_V0_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L13_PRIORITY_ZOOM_REVIEW_V0_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15L16_PRIORITY_ZOOM_REVIEW_V0_20260515.png`.

Ассистентский verdict: `T15L06` и `T15L16` strong/gold-candidate; `T15L13` possible but not primary. Следующий шаг: получить пользовательское подтверждение. Не запускать scorer/target-lock/Optuna/ML.

## Handoff 2026-07-01 T15 User Verdict V0

Статус: `T15_USER_VERDICT_V0_FIXED_NO_ML_NO_OPTUNA` superseded.

Пользователь подтвердил “норм”. Добавлен модуль:
`src/mlbotnav/visual_entry_t15_user_verdict.py`.

Зафиксировано:
`T15L06`, `T15L16` = `gold_candidate_user_confirmed`;
`T15L13` = `possible_not_primary`;
`T15L02`, `T15L07`, `T15L08`, `T15L11` = `weak_not_promoted_after_priority_review`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_20260701.json`.

Этот слой больше не использовать как рабочий: пользователь уточнил, что входов должно быть `7`. Рабочий слой: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

## Handoff 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V2

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V2_FIXED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: `T15L10` тоже крест. Актуальный слой: `user_feedback_v2`.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L10`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

Следующий шаг: показать или разобрать 7 pending; не делать ledger/scorer/ML до явных good/shift решений.

## Handoff 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V1

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V1_FIXED_NO_ML_NO_OPTUNA`.

Пользователь прислал дополнительный full-day screenshot; `T15L21` добавлен в reject. Актуальный слой: `user_feedback_v1`.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

Следующий шаг: показать или разобрать 8 pending; не делать ledger/scorer/ML до явных good/shift решений.

## Handoff 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь прислал три скриншота с красными X. Зафиксирован feedback layer:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_transfer_feedback.py`.
2. `13` candidates помечены `bad_noise / user_crossed_out_not_suitable`.
3. `9` candidates оставлены `pending_user_visual_review`.
4. Исходные screenshots пользователя сохранены в `user_feedback_v0`.
5. Сгенерирован full-day feedback PNG с красными X и cyan pending.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`, `T15L21`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

Следующий шаг: получить точный verdict по pending, особенно по кандидатам со стрелками без X. Не делать ledger/ML/Optuna до явных good/shift решений.

## Handoff 2026-07-01 Low Anchor Transfer Review 2026-05-15 Compact V0

Статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_DAY_20260515_READY_NO_ML_NO_OPTUNA`.

По просьбе пользователя создан перенос текущей visual-learning логики с `2026-05-14` на `2026-05-15`.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_transfer_review.py`.
2. Первый широкий проход дал `89` broad low-anchor candidates и `52` после мягкого фильтра, что слишком много.
3. Добавлен compact cluster filter `review_cooldown_minutes=24`.
4. Активный пакет создан в `day_20260515_compact_v0`: `22` кандидата, `2` zoom pages, full-day PNG, JSON, CSV, RU report.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_FULL_DAY_20260515.png`.

Zoom pages:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_01_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_02_20260515.png`.

Следующий шаг: показать пользователю эти PNG и получить verdict по `T15L01..T15L22`. Не создавать ledger и не двигаться к scorer/ML до visual verdict.

## Handoff 2026-07-01 Feature Policy EMA Deferred

Статус: `LOW_ANCHOR_FEATURE_POLICY_EMA_DEFERRED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: EMA пока не трогаем. Не добавлять EMA в рабочие шаблоны, паспорта, scorer-checklist или правила входа.

Дальше активные признаки для шаблонов: структура движения, положение в диапазоне, low/reclaim, объем, диапазон и wick закрытой signal-свечи. EMA-колонки в feature audit считать reference-only.

## Handoff 2026-07-01 Low Anchor No-Lookahead Feature Audit V0

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_READY_NO_ML_NO_OPTUNA`.

Создан no-lookahead feature audit после полного разбора extra auto pool.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_feature_audit.py`.
2. Сравнены группы `manual_gold`, `bad_noise`, `manual_shift_review`, `possible_entry`.
3. Все признаки считаются на закрытой signal-свече и прошлом контексте.
4. Созданы JSON/CSV/RU/PNG артефакты.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.json`.

Следующий шаг: либо zoom-lock `manual_shift_review`, либо draft no-lookahead scorer checklist/passport. Не запускать ML/export/Optuna.

## Handoff 2026-07-01 Low Anchor Extra Auto Feedback Summary

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_COMPLETE_NO_ML_NO_OPTUNA`.

Extra auto pool полностью разобран: `66` кандидатов, `6` страниц.

Итог:

1. `bad_noise`: `51`;
2. `possible_entry`: `3`;
3. `manual_shift_review`: `12`.

Summary JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701.json`.

Следующий шаг по рельсам: no-lookahead feature audit. Не строить ML/export. `possible_entry` не gold, `manual_shift_review` не label.

## Handoff 2026-07-01 Low Anchor Extra Auto Page06 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь сказал, что page `06` плохая: входы не по тренду. Все `6` кандидатов page `06` помечены `bad_noise / bad_noise_countertrend_entry`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.json`.

## Handoff 2026-07-01 Low Anchor Extra Auto Page05 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь сказал, что page `05` слабая и плохая; некоторые auto-entry стрелки не совпадают с визуально нужной low/entry-зоной.

Сделано:

1. Все `12` кандидатов page `05` помечены `bad_noise`.
2. Причина: `bad_noise_weak_context_entry_mismatch`.
3. Исходный screenshot пользователя сохранен рядом с артефактами.
4. Новые ручные точки не создавались, потому что это reject, не shift review.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.json`.

Следующий шаг: page `06` visual review. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Page04 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь показал красными X/стрелками, что page `04` надо трактовать не как готовые possible entries, а как current auto-entry not gold with manual shift needed.

Сделано:

1. `src/mlbotnav/visual_entry_low_anchor_extra_feedback.py` расширен меткой `manual_shift_review`.
2. Все `12` кандидатов page `04` помечены `manual_shift_review`.
3. Исходный screenshot пользователя сохранен рядом с артефактами.
4. Времена/цены новых ручных точек не переписывались.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.json`.

Следующий шаг: page `05` visual review или отдельный zoom-review page `04` manual shifts. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Page03 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь дал verdict по page `03`: все слабо. Зафиксировано:

1. Все `12` кандидатов page `03` = `bad_noise`.
2. Причина = `bad_noise_weak_context`.
3. `possible_entry` на page `03` нет.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.json`.

Следующий шаг: page `04` visual review или interim feature audit первых трех страниц. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Page02 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь прислал screenshot с красными рамками на page `02`. Зафиксировано:

1. `LA018`, `LA020`, `LA026` = `possible_entry` / `possible_entry_one_percent_followthrough`.
2. Остальные `9` кандидатов page `02` = `bad_noise` / `bad_noise_shallow_bounce`.
3. `possible_entry` не является gold-входом; это только кандидат для дальнейшего review.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.json`.

Следующий шаг: page `03` visual review или промежуточный feature audit. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Page01 Feedback

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь подтвердил, что первая страница extra auto review не подходит: входы слишком мелкие, с коротким отскоком, без нужного продолжения и часто без правильного трендового контекста.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_extra_feedback.py`.
2. Создан feedback layer для page `01`.
3. `LA001..LA012` помечены как `bad_noise` / `bad_noise_shallow_bounce` / `reject`.
4. Созданы JSON/CSV/RU/PNG артефакты.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.json`.

Следующий шаг: продолжить page `02` или сформировать no-lookahead feature checklist для отличия `bad_noise_shallow_bounce` от ручных good entries. Optuna/ML/export запрещены.

## Handoff 2026-07-01 Low Anchor Extra Auto Review V1

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_READY_NO_ML_NO_OPTUNA`.

После resolved label-ledger V1 создан пакет для ручного разбора `66` extra auto candidates. Они не являются negative labels автоматически.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_extra_review.py`.
2. Создан JSON/CSV/RU отчет.
3. Сгенерированы `6` PNG-страниц по `12` кандидатов.
4. На каждом zoom показаны время входа и цена `entry_price_plus_5bps`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.json`.

Страница 01:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_01_20260701.png`.

Следующий шаг: показать пользователю page 01 и получить visual verdict. Разрешенные ручные метки: `bad_noise`, `duplicate`, `possible_entry`, `wrong_type`, `ignore_unclear`. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Label Ledger V1 Resolved

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_BY_USER_NO_ML_NO_OPTUNA`.

Пользователь подтвердил pending review PNG: `норм`. `M05/M14/M15/M16/M17` закрыты как `manual_gold_user_confirmed_auto_near_ok`; `M03/M09/M10/M11` остаются `manual_gold_user_feedback_auto_not_gold`.

Итоговые target labels: `10 exact`, `4 auto near not-gold`, `5 auto near user-confirmed ok`, `0 pending`.

Resolved JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701.json`.

Следующий рабочий шаг по рельсам: не ML, а review `66` extra auto candidates как unlabeled/anti pool или draft event dataset с явным запретом export.

## Handoff 2026-07-01 Low Anchor Label Ledger V0

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_READY_NO_ML_NO_OPTUNA`.

Пользователь подтвердил feedback по `M03/M09/M10/M11`. Создан следующий слой разметки `label_ledger_v0`, чтобы не считать `±3m` gold.

Итог:

1. `manual_gold_exact_auto`: `10`;
2. `manual_gold_user_feedback_auto_not_gold`: `4`;
3. `manual_gold_pending_shift_review`: `5`.

Оставшиеся pending цели: `M05`, `M14`, `M15`, `M16`, `M17`.

Главный PNG для следующего review:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_PENDING_SHIFT_REVIEW_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701.json`.

Следующий шаг: пользователь должен дать решение по пяти pending-панелям. До этого не строить event dataset для ML, scorer, Optuna или export.

## Handoff 2026-07-01 Low Anchor User Feedback M03/M09/M10/M11

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_NO_ML_NO_OPTUNA`.

Пользователь красным отметил `M03/M09/M10/M11` на target-nearest zoom sheet: auto nearest candidate был рядом, но не в той свечке/зоне для рабочего эталона.

Сделано:

1. Добавлен модуль `src/mlbotnav/visual_entry_low_anchor_feedback.py`.
2. Создан `user_feedback_v0` с JSON, RU-md, PNG, SVG.
3. Исходный пользовательский screenshot скопирован рядом как provenance.
4. Зафиксировано правило: `hit_within_3m` не является gold; это только near-review.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.png`.

Главный JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json`.

Следующий шаг: пользователь смотрит feedback PNG. Если норм, использовать этот feedback как label layer для V1/event dataset. Scorer, Optuna, ML/export/promotion запрещены.

## Handoff 2026-07-01 Low Anchor Entry Suggester V0

Статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_SEED_DAY_REVIEW_NO_ML_NO_OPTUNA`.

Пользователь решил ускорить ручную разметку: сначала сделать автоматический поиск low-anchor входов, а стратегии/BOS/Fibo/swing/ML подключать позже как объясняющие слои.

Сделано:

1. Добавлен скрипт `src/mlbotnav/visual_entry_low_anchor_suggester.py`.
2. Запущен seed-day пакет на `SOLUSDT 1m 2026-05-14`.
3. V0 выдал `85` кандидатов после фильтра.
4. По `M01..M19`: `10/19` exact hits, `19/19` hits в пределах `±3m`.
5. Созданы JSON, CSV, full-day PNG и target-nearest zoom sheet.

Главные артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_full_day_20260514.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_target_nearest_zoom_20260514.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514_RU.md`.

Следующий шаг: пользовательский visual review zoom sheet. Не уменьшать кандидаты и не обучать ML до verdict, чтобы не потерять хорошие ручные low-входы.

Граница: V0 не является стратегией, production target-lock, Optuna или ML/export.

## Handoff 2026-07-01 Data Scope Monthly Samples

Статус: `SOLUSDT_1M_MONTHLY_FULL_DAY_SAMPLES_CREATED_NO_ML_NO_OPTUNA`.

Пользователь попросил проверить, что 126 дней `SOLUSDT 1m` реально представлены полноценными UTC-днями, и сделать визуальную выгрузку по одному дню на месяц.

Сделано:

1. Проверены sample-дни `2026-01-27`, `2026-02-28`, `2026-03-28`, `2026-04-28`, `2026-05-28`.
2. Каждый sample-день имеет `1440` строк.
3. Первая свеча каждого дня открывается в `00:00:00+00:00`.
4. Последняя свеча каждого дня закрывается в `00:00:00+00:00` следующего дня.
5. Созданы отдельные full-day PNG и общий contact sheet.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701.png`.

Отчет:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701_RU.md`.

Граница: это data-scope/visual audit only. Не запускались scorer, Optuna, ML/export/promotion.

## Handoff 2026-07-01 C01 126 Days Source Audit

Статус: `C01_126_DAYS_SOURCE_AUDIT_COMPLETE_NO_ML_NO_OPTUNA`.

Пользователь усомнился, что `126 дней` были настоящим прогоном, и предположил, что это могло быть только `1m`. Аудит подтвердил: это именно `SOLUSDT 1m only`, не MTF.

Факты:

1. В `data/core/bybit_ohlcv` найдено `126` файлов `dt=*/tf=1m/symbol=SOLUSDT/part-final.csv`.
2. Диапазон: `2026-01-26` .. `2026-05-31`.
3. Все файлы имеют `1440` строк.
4. `C01_MULTI_DAY_CHECK_V1_20260630.json` и daily CSV сходятся: `126` дней, `25` кандидатов, `23` дня с кандидатами, максимум `2` кандидата в день.
5. Недофиксация: исторический C01 multi-day JSON не пишет top-level `symbol`, `timeframe`, `source_csv_pattern`, диапазон дат и точную команду.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_126_DAYS_SOURCE_AUDIT_20260701_RU.md`.

Не продолжать C01 V1 как рабочую стратегию. Это остановленная ветка; Optuna/ML/export/promotion запрещены.

## Handoff 2026-07-01 C02A Seed-Lock

Статус: `C02A_TARGET_LOCK_SEED_V0_CREATED_NO_ML_NO_OPTUNA`.

После пользовательского подтверждения `7.1` создан seed-lock C02A для `M01/M02/M08`. Это защита от регрессии, не production target-lock.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_FULL_DAY_ZOOMS_20260630.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_FULL_DAY_ZOOMS_20260630.svg`.

Следующий шаг: `9.1_MULTI_DAY_BENCH_OR_USER_DECISION_NEXT_PASSPORT_NO_ML_NO_OPTUNA`.

Optuna и ML/export/promotion запрещены.

## Handoff 2026-06-30 C02A Entry-Only Scorer V0

Статус: `C02A_ENTRY_ONLY_SCORER_V0_SEED_DAY_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Выполнен подпункт `7.1_ENTRY_ONLY_SCORER_C02A_SEED_DAY_NO_ML_NO_OPTUNA`: после пользовательского `глянул давай далее` по C02A rules создан seed-day entry-only scorer. Входы: `C02E03/M01`, `C02E04/M02`, `C02E10/M08`; must-hit `3/3`, violations `0`.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.png`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.svg`.

Следующий шаг строго по рельсам: показать PNG пользователю и получить `норм / фикс` по `7.1_USER_VISUAL_REVIEW_C02A_ENTRY_ONLY_SCORER_V0_BEFORE_TARGET_LOCK`.

Запрещено до этого: target-lock, multi-day, Optuna, ML/export/promotion.

## Handoff 2026-06-30 C02 Good/Bad Audit

Статус: `C02_GOOD_BAD_AUDIT_V0_COMPLETE_NO_ML_NO_OPTUNA`.

Выполнен следующий пункт после ручной разметки: good/bad аудит. Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_EVENT_FEATURES_V0_20260630.csv`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_FULL_DAY_AUDIT_V0_20260630.png`.

Вывод: не строить один широкий C02 scorer. Следующий безопасный шаг: `C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`.

## Handoff 2026-06-30 C02 User Labels Complete

Статус: `C02_CANDIDATE_REVIEW_V0_USER_LABELS_COMPLETE_NO_ML_NO_OPTUNA`.

C02 candidate review завершен на seed-дне. Пользователь сначала отклонил `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`, затем отдельным скрином отметил красными рамками “можно” для `C02E03..C02E12`. Это принято как:

- `GOOD_ENTRY`: `C02E03`, `C02E04`, `C02E05`, `C02E06`, `C02E07`, `C02E08`, `C02E09`, `C02E10`, `C02E11`, `C02E12`;
- `BAD_ENTRY`: `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`.

Обновлены ledger/layer/passport/matrix. Контрольный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_USER_LABELED_GOOD_BAD_SHEET_20260630.png`.

Следующий безопасный шаг: `C02_AUDIT_GOOD_VS_BAD_AND_DECIDE_SCORER_RULES_NO_ML_NO_OPTUNA`. Не запускать scorer, Optuna, ML/export/promotion, target-lock или multi-day, пока не разобраны признаки good/bad.

## Handoff 2026-06-30 Passport Bench Step Plan

Статус: `C02_CANDIDATE_REVIEW_PACK_READY_WAIT_USER_LABELS_NO_ML_NO_OPTUNA`.

По запросу пользователя процесс расписан по пунктам и подпунктам. Выполнены: матрица покрытия `M01..M19`, папка C02, паспорт-драфт `VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0`, seed visual C02. Пользователь подтвердил seed visual словом `норм`. После этого создан C02 candidate layer V0.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_BENCH_V0_STEP_PLAN_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630.json`.

Паспорт-драфт C02:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/passport_VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0_RU.md`.

Candidate layer V0:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_20260630.json`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_full_day_review_20260630.png`.

Zoom review sheet:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_zoom_sheet_C02E01_C02E16_20260630.png`.

Review ledger:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_LEDGER_V0_20260630.json`.

Следующий подпункт: пользовательский review `C02E01..C02E16`. C01 не продолжать как главный путь. Scorer/Optuna/ML/export/promotion запрещены до разметки.

## Handoff 2026-06-30 Fresh Target-Led Passport Bench V0

Статус: `PASSPORT_BENCH_V0_STRUCTURED_NO_ML_NO_OPTUNA`.

Пользователь попросил аудит последних сообщений, подключение агента и проверку всех паспортов. Read-only агент подтвердил: реально применен только один паспорт `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0` под `M05/M06`; C01 остановлен как слабое направление, но остальные типы `M01..M19` не покрыты паспортами.

Главный вывод: не делать общий вывод по системе на основании C01. Следующий рабочий этап — `PASSPORT_BENCH_V0`: матрица покрытия паспортами, затем новый паспорт вне C01, предпочтительно `C02_DEEP_CAPITULATION_LOW` по `M01/M02/M08`.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/process_audit/PASSPORT_BENCH_STAGE_AUDIT_20260630_RU.md`.

Граница: Optuna/ML/export/promotion запрещены. Старые V7/V8/V9/V10/V11 не продолжать как очередь задач.

## Handoff 2026-06-30 Fresh Target-Led C01 Multi-Day Check V1

Статус: `C01_MULTI_DAY_CHECK_V1_RAW_NEEDS_VISUAL_TUNING_NO_ML`.

Рабочий пункт по рельсам: `C01_ENTRY_ONLY_SCORER_V0` для паспорта `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0`.

Сделано: пользователь подтвердил скрин `M05` после сдвига на одну свечу вправо. Актуальная `M05`: signal `10:43 UTC` -> entry `10:44 UTC`, entry open `90.66000000`, entry + `5 bps` = `90.70533000`. `M06` без изменений: signal `12:00 UTC` -> entry `12:01 UTC`.

Старый scorer V0 помечен как stale. Пересчитан `C01_ENTRY_ONLY_SCORER_V1`: на `SOLUSDT 1m 2026-05-14` пойманы `M05/M06`, ложных кандидатов `0`, `M12` не сработала. Пользователь дал `далее поехали по рельсам`, принято как визуальное подтверждение V1.

Создан seed target-lock: `M05/M06` защищены от потери или сдвига без отдельного решения пользователя.

Затем собран контракт входных данных и сделан raw multi-day check V1 без донастройки: 126 дней, 25 кандидатов, максимум 2 в день. Частота нормальная, но визуальное качество смешанное; до сделки нужен ручной quality-filter V2.

Артефакты:
1. PNG V1: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_full_day_M05_M06_zoom_20260630.png`.
2. JSON V1: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_20260630.json`.
3. Аудит V1: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/entry_only_scorer_v1/C01_ENTRY_ONLY_SCORER_V1_AUDIT_20260630_RU.md`.
4. Lock-ledger: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_20260630_RU.md`.
5. Lock PNG: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_full_day_M05_M06_20260630.png`.
6. Entry contract: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_ENTRY_INPUT_CONTRACT_V1_20260630_RU.md`.
7. Multi-day audit: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_MULTI_DAY_CHECK_V1_AUDIT_20260630_RU.md`.
8. Zoom contact: `reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_MULTI_DAY_CHECK_V1_all_candidates_zoom_contact_20260630.png`.

Следующий шаг: показать zoom contact sheet пользователю и руками пометить кандидаты `годится / не годится / отдельный тип`, затем сделать `C01_QUALITY_FILTER_V2`. Optuna/ML/export/promotion запрещены.

## Visual Entry TARGET_LOCKED_STRATEGY_TZ 2026-06-29

Статус: `TARGET_LOCKED_STRATEGY_TZ_READY_NO_ML`.

Полный аудит и ТЗ: `reports/final_review/visual_entry_v3/target_locked_strategy_tz/visual_entry_target_locked_strategy_audit_and_tz_20260629_RU.md`.

Активное ТЗ: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_TARGET_LOCK_TZ_RU.md`.

Решение: следующие версии visual-entry должны идти через `target_lock_ledger`. Хорошие попадания V9/V10 нельзя терять молча. Нужна библиотека разных стратегий, а не одна стратегия на все входы.

Следующий шаг:
1. создать `src/mlbotnav/visual_entry_target_lock_ledger.py`;
2. создать lock-файл по `2026-05-13` и `2026-05-14`;
3. затем делать `V11_RECOVER_RANKED_MISSES`;
4. каждый подрежим проверять отдельным PNG;
5. ML export запрещен.

## Visual Entry EVENT_RANKED_BRICKS_V10 2026-06-29

Статус: `EVENT_RANKED_BRICKS_V10_CLEANER_BUT_PARTIAL_NO_ML`.

Добавлены:
1. `src/mlbotnav/visual_entry_event_ranked_bricks_v10_runner.py`
2. `tests/test_visual_entry_event_ranked_bricks_v10_runner.py`

Главный аудит: `reports/final_review/visual_entry_v3/event_ranked_bricks_v10/visual_entry_event_ranked_bricks_v10_audit_20260629T182810Z_RU.md`.

V10 делает cluster-rank поверх V9: один лучший сигнал внутри `low_event_start_idx:event_low_idx`, без cooldown `30/45/60/90` и без будущего.

Validation `2026-05-13`: `V10_01_HOT_CHAIN_EVENT_LOW_RANKED` = `1/9`, `0` false, пойман `08:48`.

Holdout `2026-05-14`: `V10_03_WARM_EVENT_RANKED` = `3/17`, `6` false; `V10_02_HOT_FIRST_EVENT_RANKED` = `2/17`, `7` false; `V10_04_DEEP_TERMINAL_EVENT_RANKED` = `3/17`, `20` false; ranked union = `7/17`, `33` false.

PNG для просмотра:
1. `reports/final_review/visual_entry_v3/event_ranked_bricks_v10_validation/visual_entry_family_overlay_2026-05-13_v10_01_hot_chain_ranked_20260629T182730Z.png`
2. `reports/final_review/visual_entry_v3/event_ranked_bricks_v10_holdout/visual_entry_family_overlay_2026-05-14_v10_02_warm_ranked_20260629T182734Z.png`
3. `reports/final_review/visual_entry_v3/event_ranked_bricks_v10_holdout/visual_entry_family_overlay_2026-05-14_v10_03_hot_first_ranked_20260629T182738Z.png`
4. `reports/final_review/visual_entry_v3/event_ranked_bricks_v10_holdout/visual_entry_family_overlay_2026-05-14_v10_04_deep_ranked_20260629T182741Z.png`

Решение: V10 чище V9, но не готов. В ML ничего не передавать. Следующий шаг: `V11_RECOVER_RANKED_MISSES` - вернуть потерянные `10:48/20:49` warm, `15:19/18:50` hot-first, `03:25` deep отдельными подрежимами.

## Visual Entry BRICK_BY_BRICK_SELECTOR_V9 2026-06-29

Статус: `BRICK_BY_BRICK_SELECTOR_V9_PARTIAL_DIAGNOSTIC_NO_ML`.

Добавлены:
1. `src/mlbotnav/visual_entry_brick_by_brick_selector_v9_runner.py`
2. `tests/test_visual_entry_brick_by_brick_selector_v9_runner.py`

Главный аудит: `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9/visual_entry_brick_by_brick_selector_v9_audit_20260629T180726Z_RU.md`.

Validation `2026-05-13`: `V9_01_HOT_CHAIN_EVENT_LOW_BRICK` = `1/9`, `0` false, пойман `08:48`. Это чистый, но очень узкий кирпич.

Holdout `2026-05-14`: `V9_03_WARM_STRUCTURAL_RECLAIM_BRICK` = `5/17`, `16` false; `V9_02_HOT_FIRST_STRONG_RECLAIM_BRICK` = `4/17`, `20` false; `V9_04_DEEP_TERMINAL_RECLAIM_BRICK` = `4/17`, `33` false.

PNG для просмотра:
1. `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9_validation/visual_entry_family_overlay_2026-05-13_v9_01_hot_chain_event_low_20260629T180636Z.png`
2. `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9_holdout/visual_entry_family_overlay_2026-05-14_v9_01_warm_structural_20260629T180637Z.png`
3. `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9_holdout/visual_entry_family_overlay_2026-05-14_v9_03_hot_first_strong_20260629T180644Z.png`
4. `reports/final_review/visual_entry_v3/brick_by_brick_selector_v9_holdout/visual_entry_family_overlay_2026-05-14_v9_04_deep_terminal_20260629T180647Z.png`

Решение: `V9_90_RESEARCH_UNION_ALL_BRICKS_DIAG` не использовать как стратегию: `12/17`, но `68` false на holdout. В ML ничего не передавать. Следующий исполнитель должен делать `V10_EVENT_RANKED_BRICKS`: выбирать один лучший сигнал внутри low-event и отдельно дорабатывать `warm`, `hot-first`, `deep`.

## Visual Entry manual bottoms 13/14 2026-06-25
Статус: `MANUAL_BOTTOMS_EXTRACTED_AUTO_KNIFE_SUGGESTED_CP06_EMPTY_NO_ML`.

Создан инструмент `src/mlbotnav/visual_entry_marked_png_to_manual_entries.py` и тест `tests/test_visual_entry_marked_png_to_manual_entries.py`.

Новые ручные разметки:
1. `reports/manual_entries/SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms/manual_entries.json` - `9` входов.
2. `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms/manual_entries.json` - `17` входов.

Контрольные PNG:
1. `reports/manual_entries/SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms/visual_entry_manual_auto_overlay_2026-05-13_20260625T155345Z.png`.
2. `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms/visual_entry_manual_auto_overlay_2026-05-14_20260625T155345Z.png`.

Сводный аудит: `reports/final_review/visual_entry_v3/marked_validation_holdout_user_bottoms/visual_entry_marked_validation_holdout_audit_20260625_RU.md`.

Важно: `S# -> E#` = пользовательские цели, `AK#` = авто-подсказки по сильным провалам, не ML labels. CP06 без подкрутки на 13/14 дал `best=[]`, `rendered=[]`. Следующий исполнитель должен строить новый `REVERSAL_BOTTOM_KNIFE_DROP_V0`, а не передавать CP06/AK в ML.

Проверки закрыты: `py_compile PASS`; visual-entry focused tests `6/6 OK`; `text_guard PASS` `reports/qa_gate/recovery_r5_text_guard_20260625T155616Z.json`; хвостов `python.exe` нет.

## Visual Entry CP06 validation/holdout readiness 2026-06-25
Статус: `NEEDS_MANUAL_LABELS_NO_VALIDATION_RUN`.

CP06 на DEV `2026-05-12` закрыт: `11/11`, `28` false, `39` entries. Следующий честный шаг - не подкручивать параметры, а получить ручную разметку `2026-05-13` и `2026-05-14`.

Аудит: `reports/final_review/visual_entry_v3/cp06_validation_holdout_readiness/cp06_validation_holdout_readiness_20260625_RU.md`.

Для `2026-05-13` и `2026-05-14` есть seed PNG/JSON, но нет `manual_entries.json` с `target_entry_time_utc`. Два агента независимо подтвердили `NEEDS_MANUAL_LABELS`.

Следующий исполнитель должен сначала создать/получить manual-разметку:
1. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.png`;
2. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.png`.

После этого CP06 запускать на validation/holdout без изменения параметров. В ML ничего не передавать.

## Visual Entry v3 DEEP_CAPITULATION_RECLAIM 2026-06-25
Статус: `DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML`.

Добавлены `src/mlbotnav/visual_entry_deep_capitulation_reclaim_runner.py` и `tests/test_visual_entry_deep_capitulation_reclaim_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_20260512_DEV.json` и `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_20260512_DEV_RU.md`.

Лучший рабочий ensemble `DQ01_EQ01_PLUS_DEEP_RECLAIM`: `10/11`, `73` false, пропуск только `08:26`.

High-recall `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP`: `11/11`, но `95` false. Это diagnostic-only, не ML.

Новые одиночные кирпичи: `D01` ловит `12:33`, `D02` ловит `15:26`, `D03` ловит `17:00` без false на DEV-дне.

Следующий строгий шаг: `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY` - подавить ложные входы, добавить приоритет последней/лучшей свечи в кластере и отдельно решить риск `08:26` no-wick. В ML ничего не передавать.

## Visual Entry v3 EARLY_FLUSH_REVERSAL 2026-06-25
Статус: `DEV_EARLY_FLUSH_REVERSAL_DIAGNOSTIC_NO_ML`.

Добавлены `src/mlbotnav/visual_entry_early_flush_runner.py` и `tests/test_visual_entry_early_flush_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_20260512_DEV.json` и `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_20260512_DEV_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_family_overlay_2026-05-12_early_flush_01_eq01_q09_severe_soft45_20260625T134923Z.png`.

Итог: `EQ01_Q09_SEVERE_SOFT45` дал `7/11` hits и `68` false. `EQ03_Q09_SEVERE_SOFT45_NOWICK` дал `8/11`, но `90` false. `E01_SEVERE_FLUSH_LOCKOUT20` поймал `01:42` при `2` false. Это полезная DEV-диагностика, но не ML-кандидат.

Следующий шаг: строить `DEEP_CAPITULATION_RECLAIM` для пропусков `12:33`, `15:26`, `17:00`; после каждого visual-test обязательно PNG overlay и контроль живых `python.exe`.

## Visual Entry v3 quality filter diagnostic 2026-06-25
Статус: `DEV_QUALITY_FILTER_DIAGNOSTIC_NO_ML`.

Добавлены `src/mlbotnav/visual_entry_quality_filter_runner.py` и `tests/test_visual_entry_quality_filter_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_20260512_DEV.json` и `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_20260512_DEV_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_family_overlay_2026-05-12_quality_01_q09_ensemble_q07_q01_20260625T132748Z.png`.

Итог: лучший ensemble `Q09_ENSEMBLE_Q07_Q01` дал `4/11` попаданий и `53` ложных входа. Это лучше micro-bottom (`4/11`, `135` false), но все еще не кандидат. В ML ничего не передавать.

Следующий шаг: строить две отдельные подсемьи для пропусков: `EARLY_FLUSH_REVERSAL` и `DEEP_CAPITULATION_RECLAIM`.

## Visual Entry v3 micro-bottom diagnostic 2026-06-25
Статус: `DEV_MICRO_BOTTOM_SIGNATURE_DIAGNOSTIC_NO_ML`.

Добавлен runner `src/mlbotnav/visual_entry_micro_bottom_signature_runner.py`; аудит: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_20260512_DEV.json` и `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_20260512_DEV_RU.md`.

Top PNG: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_family_overlay_2026-05-12_micro_bottom_01_20260625T130512Z.png`.

Итог: micro-bottom слой дал `4/11` попаданий, но `135` ложных входов из `139`; это подтверждает форму дна, но не является кандидатом. В ML ничего не передавать. Следующий шаг - слой подавления ложных входов: `anti_drift_down`, `reclaim_quality`, `support_confluence`, `capitulation_absorption`, `bottom_event_clustering`.
## Visual Entry v3 passport-family diagnostic 2026-06-25
Статус: `DEV_PASSPORT_FAMILY_DIAGNOSTIC_DONE_NO_ML`.

Добавлены:
1. `src/mlbotnav/visual_entry_passport_family_runner.py`;
2. `tests/test_visual_entry_passport_family_runner.py`;
3. `render_family_candidate_overlay()` в `src/mlbotnav/render_visual_entry_overlay.py`.

Аудит: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_audit_20260625_RU.md`.

Отчеты: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_runner_20260512_DEV.json` и `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_runner_20260512_DEV_RU.md`.

Свежий top PNG: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_family_overlay_2026-05-12_family_01_deep_capitulation_next_open_20260625T125241Z.png`.

Итог: лучший паспортный family-layer дал только `1/11` попаданий и `20` ложных входов. Это не кандидат, в ML ничего не передавать. Следующий шаг - отдельный `VISUAL_MICRO_BOTTOM_SIGNATURE_V0`, потому что широкая feature-проверка показывает: ручные точки похожи на micro-bottom, но текущие паспорта не отделяют их от сотен похожих локальных минимумов.

## Visual Entry v3 user-entry arrows 2026-06-25
Статус: `DEV_V3_ENTRY_ARROWS_READY_NO_CANDIDATE_NO_ML`.

Актуальная логика: сигнал = закрытая свеча дна/фитиля, вход LONG = `open` следующей свечи, slippage `5 bps`. Актуальная разметка: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows/manual_entries.json`. Контрольный PNG: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows/visual_entry_combo_simple_arrows_manual_v3_targets_20260625T112336Z.png`.

Стратегический аудит: `reports/final_review/visual_entry_v3/visual_entry_v3_strategy_audit_20260625_RU.md`. Добавлен runner `src/mlbotnav/visual_entry_no_lookahead_candidates.py`; rerun: `reports/final_review/visual_entry_v3/no_lookahead_candidates_rerun/visual_entry_no_lookahead_candidates_20260512_DEV_RU.md`.

Вывод: solo-паспорта и старый lookahead combo не кандидаты; лучший честный no-lookahead exact пока `3/11` и `34` false. В ML ничего не передавать. Следующий шаг - визуально подтвердить v3 точки и дальше строить структурные подсемьи с support/CHOCH/divergence/volume-profile фильтрами.

## Visual Entry Calibration DEV-12 2026-06-25
Статус: `dev_day_manual_entries_ready_scorer_ready`.

DEV-разметка: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries.json`.

Аудит разметки: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries_audit_20260512_DEV_RU.md`.

Оверлей: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries_SOLUSDT_1m_2026-05-12_DEV_detected_overlay.png`.

Времена ручных LONG-целей на `2026-05-12`: `01:44`, `04:15`, `09:12`, `12:36`, `15:34`, `17:05` UTC. `2026-05-12` используется как DEV-день; `2026-05-13` и `2026-05-14` пока не использовать для подбора параметров.

Добавлен `src/mlbotnav/visual_entry_score.py` и тест `tests/test_visual_entry_score.py`.

Первый scorer на старом B001 CSV: `reports/qa_gate/visual_entry_score_SOLUSDT_1m_visual_dev_20260625_20260512_v1_oos_backtest_trades_SOLUSDT_1m_2026-05-12_long_only_20260625T073603Z.json`.

Итог B001: `3/6` попаданий, `15` лишних входов из `18`, `precision=0.16666666666666666`, `recall=0.5`, `f1_visual=0.25`, `net_return_pct=-62.229358575198916`, статус `VISUAL_HITS_WITH_TOO_MANY_FALSE_ENTRIES`. В ML ничего не передавать.

Следующий шаг: использовать scorer как линейку для solo-passport / block / combo diagnostic; для ранних входов у дна проектировать reversal/dip-buy family, а не раздушивать B001 momentum до шума.

## Visual Entry feature/pre-filter diagnostic 2026-06-25
Статус: `dev_diagnostic_done_next_solo_scorer_and_reversal_family`.

Артефакты:
1. `reports/qa_gate/visual_entry_feature_audit_20260512_DEV.json`;
2. `reports/qa_gate/visual_entry_prefilter_search_20260512_DEV.json`;
3. `reports/qa_gate/visual_entry_candidate_family_plan_20260512_DEV_RU.md`.

Добавлены:
1. `src/mlbotnav/visual_entry_feature_audit.py`;
2. `src/mlbotnav/visual_entry_prefilter_search.py`;
3. тесты `tests/test_visual_entry_feature_audit.py`, `tests/test_visual_entry_prefilter_search.py`.

Вывод: простой reversal-prefilter слишком шумный и не является кандидатом. Нужны solo visual scorer по выбранным существующим паспортам и отдельная `REVERSAL_DIP_BUY_LONG v0` с trigger/suppression/backtest.

## Visual Entry overlay rule 2026-06-25
Статус: `visual_overlay_required_for_each_test`.

Добавлен `src/mlbotnav/render_visual_entry_overlay.py` и тест `tests/test_render_visual_entry_overlay.py`.

Для каждого следующего visual-test показывать PNG overlay. Текущие примеры:
1. `reports/final_review/visual_entry_overlay_2026-05-12_b001_fixed_dev12_20260625T095333Z.png`;
2. `reports/final_review/visual_entry_overlay_2026-05-12_prefilter_top1_dev12_20260625T095333Z.png`.

Перед финальным ответом проверять, что не осталось `python.exe` процессов от `MLbotNav/mlbotnav/APTuna/visual_entry/optuna`.

## Visual Entry solo passport runner 2026-06-25
Статус: `dev_solo_passport_diagnostic_done_no_ml`.

Добавлен `src/mlbotnav/visual_entry_solo_passport_runner.py` и тест `tests/test_visual_entry_solo_passport_runner.py`.

Отчеты:
1. `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV.json`;
2. `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV_RU.md`.

Top overlays:
1. `reports/final_review/visual_entry_overlay_2026-05-12_solo_01_f009_emagap_down_20260625T100953Z.png`;
2. `reports/final_review/visual_entry_overlay_2026-05-12_solo_02_f059_engulfbull_20260625T100955Z.png`;
3. `reports/final_review/visual_entry_overlay_2026-05-12_solo_03_f010_emaslope_down_20260625T100957Z.png`;
4. `reports/final_review/visual_entry_overlay_2026-05-12_solo_04_f035_supportdist_20260625T100959Z.png`;
5. `reports/final_review/visual_entry_overlay_2026-05-12_solo_05_f017_f018_stoch14_20260625T101002Z.png`;
6. `reports/final_review/visual_entry_overlay_2026-05-12_solo_06_f038_rangepose_20260625T101004Z.png`.

Лучшие solo-сигналы: `F009_EMAGAP_DOWN` дал `2/6` попаданий и `6` ложных; `F059_ENGULFBULL` дал `1/6` и `0` ложных; `F010_EMASLOPE_DOWN` дал `2/6`, но `16` ложных. Это не кандидаты и не ML-вход. Следующий шаг: собрать combo `REVERSAL_DIP_BUY_LONG v0`, где `F009`/EMA-down дают контекст, а `F059`/свечной reversal и дополнительные suppression-фильтры режут шум.

## Visual Entry Calibration TZ 2026-06-25
Статус: `design_ready_waiting_for_markup`.

ТЗ: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_CALIBRATION_TZ_RU.md`.

Суть: контур ручной визуальной разметки теперь оформлен как отдельная ветка. Порядок: `manual_entries.json` -> `visual_entry_score` -> solo-passport sweep -> block sweep -> combo sweep -> validation/holdout -> ручной `APPROVED_FOR_ML`.

Критичный контроль: любые картинки, backtest/Optuna и будущий ML должны сверяться по `source_csv_sha256` core-свечей. Несовпадение дает `DATA_PARITY_FAIL`.

Следующий шаг после пользовательских стрелок: восстановить `target_entry_time_utc`, создать `manual_entries.json` и первый scorer-аудит.

## Visual Entry Calibration seed screenshots 2026-06-25
Статус: `manual_markup_seed_images_ready`.

Папка: `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625`.

Manifest: `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_manifest.json`.

Сгенерированы три дневных PNG из `data_layer=core` для ручной разметки:
1. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-12_CORE.png`;
2. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-13_CORE.png`;
3. `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625/manual_markup_seed_SOLUSDT_1m_2026-05-14_CORE.png`.

Каждый день имеет `1440` core-свечей и SHA256 исходного `part-final.csv` в per-day JSON. Следующий шаг после пользовательской разметки: создать ТЗ/контракт `manual_entries.json`, scorer попаданий `target_hits/missed_targets/false_entries/precision/recall/entry_lag_bars`, затем паспортный sweep.

## B001 marked-entry fixed backtest 2026-06-25
Статус: `done / diagnostic_only_no_promotion`.

Аудит: `reports/qa_gate/b001_marked_entry_fixed_backtest_audit_20260625T073900Z_RU.md`.

Фиксированная матрица: `reports/qa_gate/b001_marked_entry_fixed_long_20260625T071500Z/B001_F001_F005_MARKED_ENTRY_FIXED_long_3OF5.yaml`.

Параметры: `B001_family_move=1`, `entry_action_min_confirmations=3`, `F001_thr_pct=0.02`, `F002_thr_pct=0.04`, `F003_thr_pct=0.10`, `F004_thr_pct=0.95`, `F005_thr_pct=0.35`.

Результат с `min_expected_move_pct=0.001`: `18` сделок, OOS `-47.05387771496912%`; точные попадания в `09:25` и `12:36`, не кандидат.

Результат с `min_expected_move_pct=0.0`: `30` сделок, OOS `-67.41968770852606%`; шум увеличился, качество ухудшилось.

Причина непопадания `17:15`: на сигнальной свече `17:14` F-гейт дает `4/5`, но `prob_up=0.3748`, ниже `p_enter_long=0.60`. `08:15` имеет probability, но F-гейт `0/5`; `15:48` F-гейт `1/5`. Для входов у дна нужна отдельная reversal/dip-buy family. В ML ничего не передавать.

## B001 marked-entry screenshot audit 2026-06-25
Статус: `done / diagnostic_only`.

Аудит: `reports/qa_gate/b001_marked_entry_screenshot_audit_20260625T070500Z_RU.md`.

Пользователь отметил желаемые LONG-входы на скриншоте. Восстановленные времена: `01:42`, `07:02`, `08:15`, `09:25`, `12:36`, `15:48`, `17:15` UTC. Проверка показала: `09:25`, `12:36`, `17:15` можно поймать текущей B001 `RET_N LONG` family при более мягких `F001/F002/F003`; остальные точки требуют не momentum-family, а отдельную reversal/dip-buy family. ML не трогать.

## Shared-study profile-edge coverage fix 2026-06-25
Статус: `fixed / confirmed_by_runtime_smoke`.

Аудит: `reports/qa_gate/shared_study_profile_edge_coverage_fix_20260625T063700Z_RU.md`.

Найдена причина неполного profile edge coverage на shared-study process-pool: профильный forcing использовал `run_trial_index + profile_edge_worker_offset`, из-за чего `w2/w3` могли сразу уходить за первые две min/max фазы. Core forcing использовал локальный индекс и поэтому закрывался стабильнее.

Фикс: `src/mlbotnav/optuna_search_candidate.py` теперь расходует profile edge slots только при фактическом profile sampling и распределяет min/max edge-задачи между process workers. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` передает `--process-workers-total`, `adaptive_auto_train.py` пробрасывает его в Optuna search. `profile_edge_worker_offset` оставлен в отчетах как диагностика.

Проверки: `py_compile` PASS, `PSParser` PASS, `tests.test_optuna_search_runtime` PASS `73/73 OK`, `text_guard` PASS `reports/qa_gate/recovery_r5_text_guard_20260625T065332Z.json`.

Контрольный smoke `b001_3of5_long_shared_edgefix3_20260625_115056`: final worker snapshot `w3` terminal `42/42`, core `5/5 PASS`, profile `7/7 PASS`, forced profile min/max полный `7/7`. Сам результат OOS `0`, сделок `0`, не кандидат. ML не трогать.

## B001 family-unified 4/5 LONG shared-study repeat 2026-06-24
Статус: `done / tradeful_negative_no_promotion_with_edge_coverage_warn`.

Аудит: `reports/qa_gate/b001_family_unified_4of5_long_shared_repeat_audit_20260624T195100Z_RU.md`.

Пользовательский повтор `4/5 LONG` на shared-study `3x3/9`: launcher `OK`, storage `postgresql`, `w1/w2/w3 exit_code=0`, best worker `w3`, OOS `-5.4889095203104477`, сделок `1`, train gate `false`. Это отрицательный diagnostic, не кандидат. В ML ничего не передавалось.

Coverage warning: core edge coverage `5/5 PASS`, profile edge coverage `2/7 PASS`; failed profiles: `F001_thr_pct`, `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`, `F005_thr_pct`.

## B001 family-unified 3/5 LONG shared-study 2026-06-24
Статус: `done / tradeful_negative_no_promotion_with_edge_coverage_warn`.

Аудит: `reports/qa_gate/b001_family_unified_3of5_long_shared_audit_20260624T195200Z_RU.md`.

Запуск: `3x3/9`, `SharedOptunaStudy`, `SharedStudyId=b001_3of5_long_shared_20260625T005102`, matrix `reports/qa_gate/b001_family_unified_long_3of5_shared_20260625T005102/B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml`.

Итог: launcher `OK`, storage `postgresql`, `w1/w2/w3 exit_code=0`, best worker `w3`, OOS `-2.0302055441506761`, сделок `1`, train gate `false`. Это отрицательный diagnostic, не кандидат. В ML ничего не передавалось.

Важное предупреждение: core edge coverage `5/5 PASS`, но profile edge coverage `4/7 PASS`; failed profiles: `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`. Этот прогон годится как runtime diagnostic, но не как чистый proof полного profile-edge coverage.

Следующий безопасный шаг: если продолжаем B001 diagnostic, либо сначала закрыть вопрос profile-edge coverage на shared-study бюджете `42`, либо отдельно прогнать `3/5 SHORT` как diagnostic-only с явным coverage warning. К large 2н/1н по этой ветке не переходить без неотрицательного tradeful результата и понятного coverage-аудита.

## Optuna shared-study process-pool 2026-06-24
Статус: `done / infra_closed_no_promotion`.

Аудит: `reports/qa_gate/optuna_shared_study_process_pool_audit_20260624T190435Z_RU.md`.

Сделано: собран режим `3x3/9` с одной общей Optuna study. Это не старый `1x9/9` и не три полностью независимых поиска. Теперь `w1/w2/w3` остаются отдельными Python-процессами, но получают один `--optuna-shared-study-id`.

Измененные файлы:
1. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`;
2. `APTuna/run_block_family_selection.ps1`;
3. `src/mlbotnav/adaptive_auto_train.py`;
4. `src/mlbotnav/optuna_search_candidate.py`;
5. `tests/test_optuna_search_runtime.py`.

Проверки:
1. `py_compile` PASS;
2. PowerShell parser PASS;
3. `tests.test_optuna_search_runtime` PASS, `71/71 OK`;
4. dry-run PASS;
5. runtime smoke PASS по инфраструктуре.

Финальный smoke: `reports/logs/b001_4of5_long_shared_fix_launcher_20260624T185929Z.log`.

Итог smoke B001 `4/5 LONG`: launcher `OK`, shared-study включен, best worker `w2`, OOS `-10.009351008800071`, сделок `2`. Это отрицательный diagnostic, не кандидат. В ML ничего не передавалось.

Как запускать следующий shared-study diagnostic:

```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_optuna_1d1d_stagec_process_pool.ps1 -Mode long_only -DataLayer core -Symbol SOLUSDT -Timeframe 1m -TrainStart 2026-05-11 -TrainEnd 2026-05-11 -TestStart 2026-05-12 -TestEnd 2026-05-12 -WindowPolicy fixed_1d -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 42 -OptunaTimeoutSec 1200 -CalibrationMatrixPath <matrix> -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -MinCandidateTrades 1 -SharedOptunaStudy -SharedStudyId <RUN_ID> -UseTemporaryUnlock
```

Граница: shared-study требует `postgresql` или другой не-`sqlite` storage. Если preflight видит `sqlite`, запуск должен остановиться.

## Optuna single-worker профиль 1x9/9 2026-06-24
Статус: `OPTUNA_SINGLE_WORKER_1X9_9_READY`.

Сделано: `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` теперь допускает `ProcessWorkers=1`, а `APTuna/run_optuna_1d1d_stagec.ps1` не поднимает такой запуск до `2`.

Проверка dry-run подтвердила: один `w1`, `Threads/proc=9`, `Search/proc=9`, `Trials/proc=42`.

Использовать для family-unified B001, когда нужна одна общая Optuna-история вместо трех отдельных worker.

## B001 family unified 5/5 2026-06-24
Статус: `B001_FAMILY_UNIFIED_5OF5_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_unified_5of5_audit_20260624T154700Z_RU.md`.

Сделано: добавлен режим "одно семейное звено" для B001. Новая ручка `B001_family_move` задает общее направление для всех `F001..F005`; независимые `F001_move..F005_move` в unified-матрицах не используются. Пороги `F001_thr_pct..F005_thr_pct` калибруются вместе.

Матрицы:
1. LONG: `reports/qa_gate/b001_family_unified_long_20260624Tmanual/B001_F001_F005_FAMILY_UNIFIED_long_5OF5.yaml`.
2. SHORT: `reports/qa_gate/b001_family_unified_short_20260624Tmanual/B001_F001_F005_FAMILY_UNIFIED_short_5OF5.yaml`.

Smoke strict `5/5`: LONG `0` сделок, SHORT `0` сделок, везде `EMPTY_ACTION_GATE`. В ML ничего не передавалось. Следующий диагностический шаг, если продолжать эту ветку: unified `4/5`, затем `3/5`.

## B001 family strict 5/5 smoke 2026-06-24
Статус: `B001_FAMILY_STRICT_5OF5_SMOKE_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_strict_5of5_smoke_audit_20260624T153100Z_RU.md`.

Проверено правило пользователя: `B001_ALLOW = F001 AND F002 AND F003 AND F004 AND F005` на одной сигнальной свече, вход на следующей свече. Матрица: `reports/qa_gate/b001_family_strict_5of5_20260624T152830Z/B001_F001_F005_STRICT_5OF5.yaml`.

Результат smoke 1д/1д: LONG `0` сделок, SHORT `0` сделок, везде `EMPTY_ACTION_GATE`. Runtime подтвердил `entry_action_min_confirmations=5`, policy `and_all`. В ML ничего не передавалось.

Вывод: strict `5/5` технически работает, но на этом окне полностью душит входы. Если продолжать diagnostic ветку, проверять `4/5`, затем `3/5` сверху вниз; основной маршрут `B003.1` не меняется.

## B001_COMBO_DIAG визуальный аудит входов 2026-06-24
Статус: `B001_COMBO_DIAG_GATE_VISUAL_AUDIT_DONE`.

Добавлен инструмент `src/mlbotnav/render_gate_diagnostic.py`, который рисует полный сырой день и слои runtime: `after mode`, `after F-gate`, `after min_move`, реальные входы и выходы.

Артефакты:
1. LONG: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.png`, summary `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.json`.
2. SHORT: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.png`, summary `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.json`.

Вывод: день полный (`1440` свечей). LONG сжимается на `F-gate`: `621 -> 4 -> 4 -> 4`. SHORT сжимается на `min_expected_move_pct=0.001`: `637 -> 240 -> 2 -> 2`. Это диагностическая ветка; ML не тронут.

## B001_COMBO_DIAG N-of-M smoke 2026-06-24
Статус: `B001_COMBO_DIAG_N_OF_M_SMOKE_DONE_NO_CANDIDATE`.

Аудит: `reports/qa_gate/b001_combo_diag_n_of_m_audit_20260624T125500Z_RU.md`.

Сделано:
1. Добавлен диагностический режим `N из M` для `B001_RET_N_TOURNAMENT` через `entry_action_min_confirmations`.
2. Полная combo-матрица `F001..F005` smoke 1д/1д LONG дала OOS `-8.498538882812346%`, `4` сделки, `N=1`.
3. SHORT tradeful worker дал OOS `-6.055628696458093%`, `2` сделки, `N=1`.
4. Результат отрицательный, поэтому это не кандидат и не `block_winner`.
5. В ML ничего не передавалось.

Важное правило: старый `AND`-турнир B001 не запускать как правильный ответ на текущую гипотезу. Для диагностики использовать `N_OF_M`; основной маршрут `B003.1` не меняется.

## B002.3 итог блока закрыт 2026-06-24
Статус: `B002_3_BLOCK_SUMMARY_CLOSED_NEXT_B003`.

Итоговый отчет: `reports/qa_gate/b002_block_summary_b002_3_20260624T100800Z_RU.md`.

Решение по `B002`: LONG `NO_BLOCK_WINNER` (`EMPTY_ACTION_GATE`), SHORT `NO_BLOCK_WINNER` (`MIN_MOVE_UNREACHABLE`); один SHORT worker нашел 1 OOS-сделку, но результат был отрицательный `-7.690052872230013%`. В ML ничего не передавалось.

Следующий блок: `B003`, одиночный паспорт `F007 / F007_RSTD20_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F007_rolling_std20_1m_entry_filter.yaml`.

Активный worker-профиль сохраняется: `3x3/9` (`Threads=9`, `SearchWorkers=9`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`).

Следующий строгий шаг: `B003.1 large LONG 2н/1н`, затем `B003.2 large SHORT 2н/1н`. В ML ничего не передавать.

## B001.6 итог блока закрыт 2026-06-24
Статус: `B001_6_BLOCK_SUMMARY_CLOSED_NEXT_B002`.

Итоговый отчет: `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.

Решение по `B001`: LONG фиксируется как ручной положительный кандидат `F001 / F001_RET1_ALLOW`, OOS `+0.7322559143841945`, сделок `1`; SHORT закрыт как `NO_BLOCK_WINNER`, OOS сделок `0`. В ML ничего не передавалось.

Следующий блок: `B002`, одиночный паспорт `F006 / F006_HLSPREAD_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F006_hl_spread_1m_entry_filter.yaml`.

Активный worker-профиль для следующих запусков: `3x3/9` (`Threads=9`, `SearchWorkers=9`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`). Откат на `2x3/6` только при устойчивой перегрузке CPU/памяти или падении workers, с записью причины в аудите.

Следующий строгий шаг: `B002.1 large LONG 2н/1н`, затем `B002.2 large SHORT 2н/1н`. В ML ничего не передавать.

## B001.5 large SHORT закрыт 2026-06-24
Статус: `B001_5_LARGE_SHORT_CLOSED_NO_BLOCK_WINNER`.

Аудит: `reports/qa_gate/b001_large_short_b001_5_audit_20260624T094057Z_RU.md`.

Финальный отчет: `reports/qa_gate/block_family_selection_B001_short_only_20260624T091433Z.json`.

Результат: `block_winner=null`; лучший доступный fallback `F004 / F004_RET12_ALLOW`, OOS `0.0`, сделок `0`, runtime `EMPTY_ACTION_GATE`.

Разбор по OOS: все `F001..F005` имеют `0` сделок. `F001..F003` остановились на `MIN_MOVE_UNREACHABLE`, `F004..F005` на `EMPTY_ACTION_GATE`. Входов/выходов в OOS нет; train-сделки есть только у `F002` и `F003`, обе ветки отрицательные суммарно.

Фикс после B001.5: `APTuna/run_block_family_selection.ps1` больше не печатает полный JSON в терминал по умолчанию. Теперь выводится краткая таблица по F-ID и, если сделки есть, строки `вход -> выход -> profit`. Полный JSON сохраняется в файл, машинный stdout доступен через `-EmitJson`.

Проверки: dry-run без JSON-каши; `pytest tests/test_block_family_manifest.py tests/test_backtest_fields.py -q` -> `47 passed`; text_guard -> `PASS`, `reports/qa_gate/recovery_r5_text_guard_20260624T094914Z.json`.

Следующий строгий шаг: `B001.6 итог блока LONG+SHORT`. В ML ничего не передавать.

## B001.4 large LONG закрыт 2026-06-24
Статус: `B001_4_LARGE_LONG_PASS_WITH_WINNER`.

Аудит: `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.

Финальный отчет: `reports/qa_gate/block_family_selection_B001_long_only_20260624T080934Z.json`.

Результат: `F001 / F001_RET1_ALLOW`, OOS `+0.7322559143841945`, сделок `1`, runtime `TRADEFUL_POSITIVE`, `goal_pass=false`.

Перед финальным повтором исправлен перенос runtime-диагностики из `oos_report` в блоковый `best_oos`.

Исторический следующий шаг после этого раздела был `B001.5`; он уже закрыт. Актуальный следующий шаг указан сверху: `B001.6 итог блока LONG+SHORT`. В ML ничего не передавать.

## B001.3 smoke 1д/1д закрыт 2026-06-24
Статус: `B001_3_SMOKE_AUDIT_PASS`.

Аудит: `reports/qa_gate/b001_smoke_1d1d_audit_20260624T075006Z_RU.md`.

Финальные чистые отчеты:
1. LONG: `reports/qa_gate/block_family_selection_B001_long_only_20260624T074316Z.json`.
2. SHORT: `reports/qa_gate/block_family_selection_B001_short_only_20260624T074525Z.json`.

Результат smoke:
1. даты `2026-05-11..2026-05-11 -> 2026-05-12..2026-05-12`;
2. `B001` развернулся в `F001,F002,F003,F004,F005`;
3. LONG победитель smoke: `F001 / F001_RET1_ALLOW`, OOS `+2.404470760400401`, сделок `1`;
4. SHORT победителя нет: лучший доступный `F002 / F002_RET3_ALLOW`, OOS `-0.3092010602366857`, сделок `1`;
5. ML не трогался.

Фиксы: runner теперь разбирает многострочный JSON process-pool, не выбирает отрицательный/нулевой `block_winner`, и корректно помечает dry-run как `OK`.

Следующий строгий шаг: `B001.4 large LONG 2н/1н`, затем аудит перед `B001.5`.

## Block-Family Route Correction 2026-06-24
Status: `block_route_ready_for_b001`.

Audit: `reports/qa_gate/block_family_passport_route_audit_20260624T064900Z.md`.

Corrected route: passports are calibrated by block/family. A multi-passport block such as `B001` runs all active solo F-passports in that family, then the block report selects the best available LONG/SHORT result for the block. Single-passport blocks run as one block with one passport.

Implemented:
1. Added `src/mlbotnav/block_family_manifest.py`.
2. Added generic runner `APTuna/run_block_family_selection.ps1`.
3. Added regression tests in `tests/test_block_family_manifest.py`.
4. Dry-run verified `B001` expands to `F001..F005` on the large-window route.

ML policy: no block result is packaged, approved, or ingested into ML during block calibration. `NO_GO`, `VALIDATION_FAIL`, and preliminary block results remain outside ML until the user manually approves a later final selection.

Next strict step: run `B001` as a block, first LONG then SHORT, through `APTuna/run_block_family_selection.ps1` with `-UseTemporaryUnlock` sequentially.

## Min-Move Runtime Guard Fix 2026-06-24
Status: `fix_applied_superseded_by_block_route`.

Root cause artifact: `reports/qa_gate/ml_optuna_zero_trade_min_move_diagnostic_20260624T051535Z.md`.

The runtime bug is fixed and remains part of the route: `MIN_MOVE_UNREACHABLE` is explicit, penalized/skipped in selection, and the default 1m min-move grid is `0.0,0.001,0.002,0.003`.

Validation before block-route correction: focused pytest `124 passed`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260624T063715Z.json`; readiness frozen at `reports/readiness/readiness_check_20260624T063714Z.json`.

Old F068 next-step pointer is superseded by the block-family route.

## Zero-Trade Diagnostic 2026-06-24
Status: `root_cause_found`.
Artifact: `reports/qa_gate/ml_optuna_zero_trade_min_move_diagnostic_20260624T051535Z.md`.

Root cause: selected `min_expected_move_pct` can be unreachable in `exchange_like` mode after action gates. F067 LONG had `1415` OOS signals after action gate, but selected `min_expected_move_pct=0.01`; proxy max after gate was only `0.005140`, so min-move removed every entry.

Replay on the same F067 LONG OOS CSV: `min_move=0.005` gives `2` trades and `+7.005540`; `min_move=0.003` gives `14` trades and `-16.554791`; `min_move=0.01` gives `0` trades.

Do not package, approve, or ingest F050-F067. The min-move guard/grid/reporting fix has been applied. Historical resume pointer `8.2.19 F068_PATTERNAGE_ALLOW` is superseded by the corrected block-family route at the top of this file.

## Route Memory Audit 2026-06-23
Status: `ON_ROUTE`.

Audit: `reports/qa_gate/ml_optuna_route_memory_audit_20260623T205751Z.md`.

Current control audit after F067: `reports/qa_gate/ml_optuna_route_status_audit_after_f067_20260624T044311Z.md`.

Independent agent `Averroes` confirmed the route through `8.2.8`; local follow-up closed `8.2.9 F058_SHOOTINGSTAR_ALLOW`, `8.2.10 F059_ENGULFBULL_ALLOW`, `8.2.11 F060_ENGULFBEAR_ALLOW`, `8.2.12 F061_RSIBULLDIV_ALLOW`, `8.2.13 F062_RSIBEARDIV_ALLOW`, `8.2.14 F063_MACDBULLDIV_ALLOW`, `8.2.15 F064_MACDBEARDIV_ALLOW`, `8.2.16 F065_OBVBULLDIV_ALLOW`, `8.2.17 F066_OBVBEARDIV_ALLOW`, and `8.2.18 F067_PATTERNSTRENGTH_ALLOW` as `CLOSED_NO_GO`.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file. Do not package, approve, or ingest current F050-F067 results into ML.

Last updated UTC: 2026-06-23T22:57:00Z

## ML Optuna Calibration Stage 8.2.18 F067 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_18_f067_audit_20260623T225700Z.md`.

Scope: F067 Pattern Strength entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F067_PATTERNSTRENGTH_ALLOW`, ignored columns `[]`. LONG reached `1415` signals after action gate but `0` after min-move; SHORT had `0` signals after action gate.

Decision: `F067_PATTERNSTRENGTH_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Text guard before document updates: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T225605Z.json`.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file.

## ML Optuna Calibration Stage 8.2.17 F066 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_17_f066_audit_20260623T224200Z.md`.

Scope: F066 OBV Bearish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F066_OBVBEARDIV_ALLOW`, ignored columns `[]`. LONG and SHORT both had `0` signals after action gate and `0` filled entries.

Decision: `F066_OBVBEARDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Text guard before document updates: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T224148Z.json`.

Next strict step: `8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.16 F065 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_16_f065_audit_20260623T223100Z.md`.

Scope: F065 OBV Bullish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F065_OBVBULLDIV_ALLOW`, ignored columns `[]`. LONG left `4` signals and SHORT left `11` after action gate, then both had `0` after min-move and `0` filled entries.

Decision: `F065_OBVBULLDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T223247Z.json`.

Next strict step: `8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.15 F064 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_15_f064_audit_20260623T222100Z.md`.

Scope: F064 MACD Bearish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F064_MACDBEARDIV_ALLOW`, ignored columns `[]`. LONG and SHORT both had `0` signals after action gate and `0` filled entries.

Decision: `F064_MACDBEARDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T222318Z.json`.

Next strict step: `8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.14 F063 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_14_f063_audit_20260623T221200Z.md`.

Scope: F063 MACD Bullish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F063_MACDBULLDIV_ALLOW`, ignored columns `[]`. LONG and SHORT both had `0` signals after action gate and `0` filled entries.

Decision: `F063_MACDBULLDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T221352Z.json`.

Next strict step: `8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.13 F062 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_13_f062_audit_20260623T220200Z.md`.

Scope: F062 RSI Bearish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F062_RSIBEARDIV_ALLOW`, ignored columns `[]`. LONG and SHORT both had `0` signals after action gate and `0` filled entries.

Decision: `F062_RSIBEARDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T220438Z.json`.

Next strict step: `8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.12 F061 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_12_f061_audit_20260623T215100Z.md`.

Scope: F061 RSI Bullish Divergence entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F061_RSIBULLDIV_ALLOW`, ignored columns `[]`. LONG had `0` signals after action gate; SHORT had `4` signals after action gate, then `0` eligible bars after min-move and `0` filled entries.

Decision: `F061_RSIBULLDIV_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T215016Z.json`.

Next strict step: `8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.11 F060 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_11_f060_audit_20260623T213900Z.md`.

Scope: F060 Bearish Engulfing entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F060_ENGULFBEAR_ALLOW`, ignored columns `[]`. LONG had `0` signals after action gate; SHORT had `1` signal after action gate, then `0` eligible bars after min-move and `0` filled entries.

Decision: `F060_ENGULFBEAR_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T213857Z.json`.

Next strict step: `8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.10 F059 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_10_f059_audit_20260623T213000Z.md`.

Scope: F059 Bullish Engulfing entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F059_ENGULFBULL_ALLOW`, ignored columns `[]`. LONG and SHORT had `0` signals after action gate and `0` filled entries.

Decision: `F059_ENGULFBULL_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T212931Z.json`.

Next strict step: `8.2.11 Run F060_ENGULFBEAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.9 F058 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_9_f058_audit_20260623T211900Z.md`.

Scope: F058 Shooting Star entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F058_SHOOTINGSTAR_ALLOW`, ignored columns `[]`. LONG had `0` signals after action gate; SHORT had `1` signal after action gate, then `0` eligible bars after min-move and `0` filled entries.

Decision: `F058_SHOOTINGSTAR_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T211810Z.json`.

Next strict step: `8.2.10 Run F059_ENGULFBULL_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.8 F057 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_8_f057_audit_20260623T205000Z.md`.

Scope: F057 Hammer entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F057_HAMMER_ALLOW`, ignored columns `[]`. LONG had `0` signals after action gate; SHORT had `8` signals after action gate but `0` filled entries.

Decision: `F057_HAMMER_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T205204Z.json`.

Next strict step: `8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.7 F056 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_7_f056_audit_20260623T203800Z.md`.

Scope: F056 Bearish Pin Bar entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F056_PINBEAR_ALLOW`, ignored columns `[]`; both sides had `0` signals after action gate.

Decision: `F056_PINBEAR_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T204000Z.json`.

Next strict step: `8.2.8 Run F057_HAMMER_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.6 F055 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_6_f055_audit_20260623T202700Z.md`.

Scope: F055 Bullish Pin Bar entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F055_PINBULL_ALLOW`, ignored columns `[]`. LONG had `1` signal after action gate but `0` filled entries; SHORT had `0` signals after action gate.

Decision: `F055_PINBULL_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T202913Z.json`.

Next strict step: `8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.5 F054 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_5_f054_audit_20260623T201700Z.md`.

Scope: F054 Inside Bar entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Isolation: active gate only `F054_INSIDEBAR_ALLOW`, ignored columns `[]`; the action gate reduced raw signals to zero entries.

Decision: `F054_INSIDEBAR_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T201812Z.json`.

Next strict step: `8.2.6 Run F055_PINBULL_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.4 F053 2026-06-23
Status: `closed_no_go_fix_applied`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.

Scope: F053 Doji entry filter, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, OOS `2026-05-25..2026-05-31`.

Result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`; both process-pool runs completed `OK`.

Fix applied: restored readiness freeze and added a live-marker guard in `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` so a second `-UseTemporaryUnlock` process-pool run exits before starting workers.

Decision: `F053_DOJI_ALLOW` is `NO_GO_FOR_ML`. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T200628Z.json`.

Next strict step: `8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`.

## ML Optuna Validation Stage 8.2.3 F052 2026-06-23
Status: `closed_validation_fail_no_ml_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_3_f052_fixed_validation_audit_20260623T194700Z.md`.

Scope: fixed F052 CHOCH LONG params from Stage 8.2.2, `SOLUSDT 1m core`, train `2026-05-04..2026-05-17`, OOS `2026-05-18..2026-05-24`.

Result: OOS `-5.696708101293968`, trades `1`, train gate `false`, OOS goal pass `false`, exit reason `timeout`.

Decision: F052 LONG failed adjacent-window validation. Do not build package, do not approve for ML, do not ingest into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T195125Z.json`.

Next strict step: continue with the next user-selected passport/action discovery, or define a new validation idea with its own audit boundary.

## ML Optuna Calibration Stage 8.2.2 F052 2026-06-23
Status: `closed_positive_test_candidate_needs_validation`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_2_f052_audit_20260623T193700Z.md`.

Scope: F052 CHOCH action, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Result: LONG `goal_pass`, OOS `+5.3486475132039635`, trades `1`; SHORT `goal_fail`, OOS `0.0`, trades `0`.

Caveat: LONG train gate failed, OOS has only one trade, and the only trade exited by timeout.

Decision: not automatic ML GO. Do not build package or start ML training without explicit next decision.

Next strict step: manual decision: validate F052 LONG on adjacent/rolling window, explicitly approve draft package build, or continue next passport/action discovery.

## ML Optuna Calibration Stage 8.2.1 F050 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_1_f050_audit_20260623T192700Z.md`.

Scope: F050 BOSUP action, `long_only`, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Final valid run: process pool `OK`, both workers `goal_fail`, best OOS trades `0`, best OOS net return `0.0`.

Decision: `NO_GO_FOR_ML`. Do not build an ML package or start ML training from this run.

Next strict step: `8.2.2 Run F052_CHOCH_ALLOW large-window candidate`, unless user overrides the target.

## ML Optuna Calibration Stage 8.2 2026-06-23
Status: `closed_no_go`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_audit_20260623T191900Z.md`.

Scope: F051 BOSDOWN action, `short_only`, `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Fixes made: process-pool runner now supports `-DataLayer raw|core`; adaptive/search/train/OOS path now passes `--layer`; OOS report now writes top-level `data_layer` and train/test window fields.

Final valid run: process pool `OK`, but both workers returned `goal_fail`; best OOS trades `0`, best OOS net return `0.0`.

Decision: `NO_GO_FOR_ML`. Do not build an ML package or start ML training from this run.

Next strict step: manual decision for next passport/action calibration target or revised `8.2` candidate run.

## ML Large Clean Window Stage 8.1 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.

Created:
1. `configs/ml_large_clean_window_manifest.yaml`.
2. `src/mlbotnav/ml_large_clean_window_manifest_audit.py`.
3. `tests/test_ml_large_clean_window_manifest_audit.py`.

Window: `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Checks: large clean window audit `PASS`, train days `14`, test days `7`, missing files `0`; new tests `4/4 OK`; focused smoke/ingest tests `22/22 OK`.

Boundary: Optuna calibration not started, package not created, ML ingest not started, ML training not started.

Next strict step: `8.2 Run Optuna calibration`.

## ML Smoke Bridge Stage 7 Closeout 2026-06-23
Status: `stage_7_closed_pass`.
Artifact: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.

Closed:
1. `7.1` smoke run.
2. `7.2` test package.
3. `7.3` package contract audit.
4. `7.4` approved registry.
5. `7.5` ML ingest dataset.
6. `7.6` closeout.

Dataset:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`

Dataset manifest:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`

Final checks: smoke window `PASS`; approved registry `PASS`; ML ingest builder `PASS`; dataset contract `PASS`; focused Stage 7 tests `67/67 OK`.

Boundary: ML training not started, no direct Optuna report scan, no unapproved package ingested.

Next strict step: `8.1 Fix large clean window`.

## ML Ingest Stage 7.5 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.

Dataset:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`

Dataset manifest:
`reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`

Built from approved package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`

Checks: dataset builder `PASS`, rows `1177`; dataset contract `PASS`; registry validator/reader/admission status `PASS`; focused ingest tests `24/24 OK`.

Boundary: no direct Optuna report scan; no unapproved package ingested; ML training not started.

Next strict step: `7.6 Stage 7 closeout`.

## ML Approved Registry Stage 7.4 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.

Approved package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`

Registry now has one approved package: `smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`, status `APPROVED_FOR_ML`.

Package files now agree on admission: `manifest.json.status=APPROVED_FOR_ML`, `calibration_package.json.status=APPROVED_FOR_ML`, `audit.md` has `ML decision: GO_FOR_ML`.

Checks: registry validator `PASS`; admission status `PASS`; registry reader `PASS`; package contract/alignment audits `PASS`; focused tests `42/42 OK`.

Boundary: dataset builder / ML ingest not run; ML training not started.

Next strict step: `7.5 Run ML ingest`.

## ML Smoke Package Contract Stage 7.3 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.

Package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`

Context: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`, `B018/F051/F051_BOSDOWN_ALLOW`.

Package status: `DRAFT`. Package audit says `ML decision: NO_GO_FOR_ML`.

Contract audit: `PASS`, report `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T183343Z.json`, rows `1177`, failed rows `0`, missing columns `0`.

Alignment audits: run_id `PASS`, passport context `PASS`, calibration params `PASS`, data windows `PASS`.

Registry boundary: admission status `PASS / NO_APPROVED_PACKAGES`, registry validator `PASS`, registry reader `PASS`, dataset builder `PASS / NO_APPROVED_PACKAGES`.

Focused tests: `48/48 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T183955Z.json`.

Boundary: no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

Next strict step: `7.4 Add package to approved registry`.

## ML Smoke Package Stage 7.2 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.

Created smoke candidate package:
`reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`

Source package:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Context: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`, `B018/F051/F051_BOSDOWN_ALLOW`.

Package status: `DRAFT`. Package audit says `ML decision: NO_GO_FOR_ML`.

Fix applied: package-local `source_reports/oos_report.json` was missing `data_layer` and `date_range`; fixed only the smoke package copy. Source Stage 3 package was not changed.

Audits: contract `PASS`; run_id alignment `PASS`; passport context `PASS`; calibration params `PASS`; data windows `PASS`.

Checks: focused tests `42/42 OK`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; text_guard `PASS`.

Boundary: no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

Next strict step: `7.3 Run package contract audit`.

## ML Smoke Window Stage 7.1 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.

Created Stage 7.1 smoke window manifest:
`configs/ml_smoke_run_manifest.yaml`

Created smoke window auditor:
`src/mlbotnav/ml_smoke_window_manifest_audit.py`

Tests:
`tests/test_ml_smoke_window_manifest_audit.py`

Selected clean smoke window: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`.

Real audit: `PASS`, report `reports/qa_gate/ml_smoke_window_manifest_audit_20260623T182159845644Z.json`, selected dates `2026-05-25`, `2026-05-26`, `2026-05-27`, missing files `0`, errors `0`.

Checks: new tests `5/5 OK`; focused ML smoke/alignment tests `78/78 OK`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; reject-log builder `PASS / NO_REJECTIONS`; text_guard `PASS`.

Boundary: no package created, no registry mutation, no `APPROVED_FOR_ML`, no ML ingest, no ML training.

Next strict step: `7.2 Build test package`.

## ML Alignment Stage 6 Closeout 2026-06-23
Status: `stage_6_closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.

Closed Stage 6:
1. `6.1` run_id alignment.
2. `6.2` passport context alignment.
3. `6.3` calibration params alignment.
4. `6.4` data windows alignment.
5. `6.5` admission status.
6. `6.6` closeout.

Closeout checks: focused tests `121/121 OK`; all five alignment audits `PASS / NO_APPROVED_PACKAGES`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; reject-log builder `PASS / NO_REJECTIONS`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181511Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started.

Next strict step: `7.1 Smoke run`.

## ML Alignment Admission Status Stage 6.5 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.

Created admission status auditor:
`src/mlbotnav/ml_alignment_admission_status_audit.py`

Tests:
`tests/test_ml_alignment_admission_status_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_admission_status_audit_20260623T180909527952Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `121/121 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181123Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started. Stage 6 closeout is reserved for `6.6`.

Next strict step: `6.6 Stage 6 closeout`.

## ML Alignment Data Windows Stage 6.4 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.

Created data windows alignment auditor:
`src/mlbotnav/ml_alignment_data_windows_audit.py`

Tests:
`tests/test_ml_alignment_data_windows_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_data_windows_audit_20260623T154607261155Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `115/115 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154759Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started. Admission status is reserved for `6.5`.

Next strict step: `6.5 Check admission status`.

## ML Alignment Calibration Params Stage 6.3 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.

Created calibration params alignment auditor:
`src/mlbotnav/ml_alignment_calibration_params_audit.py`

Tests:
`tests/test_ml_alignment_calibration_params_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_calibration_params_audit_20260623T154050444104Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `107/107 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154240Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started. Data windows are reserved for `6.4`.

Next strict step: `6.4 Check data windows`.

## ML Alignment Passport Context Stage 6.2 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.

Created passport context alignment auditor:
`src/mlbotnav/ml_alignment_passport_context_audit.py`

Tests:
`tests/test_ml_alignment_passport_context_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_passport_context_audit_20260623T153553932585Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `100/100 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153741Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started. Calibration params are reserved for `6.3`.

Next strict step: `6.3 Check calibration params`.

## ML Alignment Run ID Stage 6.1 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.

Created run_id alignment auditor:
`src/mlbotnav/ml_alignment_run_id_audit.py`

Tests:
`tests/test_ml_alignment_run_id_audit.py`

Real registry report:
`reports/qa_gate/ml_alignment_run_id_audit_20260623T152715670875Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Focused tests: `94/94 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153207Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started.

Next strict step: `6.2 Check passport context`.

## ML Stage 5 Closeout 2026-06-23
Status: `stage_5_closed_pass`.
Artifact: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.

Closed Stage 5:
1. `5.1` ML ingest entry point discovery.
2. `5.2` source policy blocks direct old report roots.
3. `5.3` approved package registry reader.
4. `5.4` approved trade dataset builder.
5. `5.5` rejection reason log.
6. `5.6` closeout.

Closeout checks: focused tests `89/89 OK`; registry validator `PASS`; registry reader `PASS`; dataset builder `PASS / NO_APPROVED_PACKAGES`; reject-log builder `PASS / NO_REJECTIONS`; old root `reports/optuna` denied as expected; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; no unapproved dataset; ML training not started.

Next strict step: `6.1 Check run_id alignment`.

## ML Rejection Reasons Stage 5.5 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.

Created rejection reason log builder:
`src/mlbotnav/ml_rejection_reason_log.py`

Tests:
`tests/test_ml_rejection_reason_log.py`

Real reject-log report:
`reports/qa_gate/ml_rejection_reason_log_20260623T151618705623Z.json`

Reject log:
`reports/ml_rejections/ml_rejection_reasons_20260623T151618703912Z.json`

Result: `PASS / NO_REJECTIONS`, registry entries `0`, rejections `0`.

Focused tests: `89/89 OK`.

Final checks: registry validator `PASS`; reject-log smoke `PASS / NO_REJECTIONS` at `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no registry mutation; ML training not started.

Next strict step: `5.6 Stage 5 closeout`.

## ML Trade Dataset Assembly Stage 5.4 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.

Created dataset builder:
`src/mlbotnav/ml_approved_trade_dataset_builder.py`

Tests:
`tests/test_ml_approved_trade_dataset_builder.py`

Real builder report:
`reports/qa_gate/ml_approved_trade_dataset_builder_20260623T150934741093Z.json`

Result: `PASS / NO_APPROVED_PACKAGES`, approved packages `0`, rows total `0`, dataset path empty.

Focused tests: `85/85 OK`.

Final checks: registry validator `PASS`; builder smoke `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; no ML dataset was created from unapproved data; ML training not started.

Next strict step: `5.5 Add rejection reasons`.

## ML Approved Package Registry Reader Stage 5.3 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.

Created registry reader:
`src/mlbotnav/ml_approved_package_registry_reader.py`

Tests:
`tests/test_ml_approved_package_registry_reader.py`

Real registry reader report:
`reports/qa_gate/ml_approved_package_registry_reader_20260623T145755674743Z.json`

Result: `PASS`, approved count `0`, packages exposed to ML `0`.

Focused tests: `82/82 OK`.

Final checks: registry validator `PASS`, `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.

Boundary: no package is `APPROVED_FOR_ML`; ML dataset assembly and ML training not started.

Next strict step: `5.4 Реализовать сборку ML dataset`.

## ML Ingest Source Policy Stage 5.2 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.

Created source-policy guard:
`src/mlbotnav/ml_ingest_source_policy.py`

Tests:
`tests/test_ml_ingest_source_policy.py`

Forbidden direct roots: `reports/optuna`, `reports/pipeline`, `reports/final_review`.

Allowed source classes: approval registry and `reports/ml_candidates/<run_id>/...`.

Focused tests: `79/79 OK`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest/training not started.

Next strict step: `5.3 Реализовать чтение registry`.

## ML Ingest Entry Point Stage 5.1 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.

Current primary ML training ingest entry point:
`src/mlbotnav/pipeline_train_eval.py`

Current orchestrators:
1. `src/mlbotnav/prod_cycle.py`
2. `src/mlbotnav/stage_ladder.py`
3. `src/mlbotnav/adaptive_auto_train.py`

Gap: training does not read `configs/ml_approved_calibration_packages.yaml` and does not assemble from `reports/ml_candidates/<run_id>/trade_log.csv`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest/training not started.

Next strict step: `5.2 Запретить прямое чтение Optuna reports`.

## ML Approval Registry Stage 4 Closeout 2026-06-23
Status: `stage_4_closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.

Current fact: Stage 4 Manual ML Approval Registry is closed.

Registry:
`configs/ml_approved_calibration_packages.yaml`

Validator:
`src/mlbotnav/ml_approval_registry_validator.py`

Real registry validation:
`reports/qa_gate/ml_approval_registry_validator_20260623T143952Z.json`

Result: `PASS`, approved count `0`, failures `0`.

Focused tests: `74/74 OK`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest not started.

Next strict step: `5.1 Найти текущую точку ML ingest`.

## ML Approval Registry Stage 4.4 Validator 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.

Current fact: registry validator exists:
`src/mlbotnav/ml_approval_registry_validator.py`

Tests:
`tests/test_ml_approval_registry_validator.py`

Real registry validation report:
`reports/qa_gate/ml_approval_registry_validator_20260623T143427Z.json`

Result: `PASS`, approved count `0`, failures `0`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest not started.

Next strict step: `4.5 Закрытие этапа 4`.

## ML Approval Registry Stage 4.3 Bans 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.

Current fact: registry bans are recorded in:
`configs/ml_approved_calibration_packages.yaml`

Bans include `NO_GO`, `VALIDATION_FAIL`, missing contract audit `PASS`, invalid manifest, missing package files, and `raw/quarantine` as clean ML input.

Current registry state: `approved_packages: []`.

Boundary: validator CLI/module starts at `4.4`; no package is `APPROVED_FOR_ML`.

Next strict step: `4.4 Сделать validator registry`.

## ML Approval Registry Stage 4.2 Format 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.

Current fact: registry format is documented in comments:
`configs/ml_approved_calibration_packages.yaml`

Current registry state: `approved_packages: []`.

Boundary: no package is `APPROVED_FOR_ML`; validator rules start at `4.3`/`4.4`.

Next strict step: `4.3 Добавить запреты registry`.

## ML Approval Registry Stage 4.1 File 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.

Current fact: manual approval registry file exists:
`configs/ml_approved_calibration_packages.yaml`

Current registry state: `approved_packages: []`.

Boundary: no package is `APPROVED_FOR_ML`; ML ingest not started.

Next strict step: `4.2 Описать формат registry`.

## ML Candidate Package Stage 3 Closeout 2026-06-23
Status: `stage_3_closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.

Current fact: Stage 3 is closed for candidate package:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Package contains required files: `calibration_package.json`, `trade_log.csv`, `source_reports.json`, `manifest.json`, `audit.md`, `source_reports/oos_report.json`, `source_reports/pipeline_report.json`.

Validation: required files `PASS`; manifest `PASS`; trade log contract `PASS` (`reports/qa_gate/ml_trade_dataset_contract_audit_20260623T141708Z.json`); focused tests `71/71 OK`; `text_guard PASS`.

Boundary: package remains `DRAFT`, `APPROVED_FOR_ML` not set, ML ingest not started.

Next strict step: `4.1 Создать registry файл`.

## ML Candidate Package Stage 3.6 Package Audit 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.

Current fact: package-local `audit.md` exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/audit.md`

ML decision in audit: `NO_GO_FOR_ML`.
Review state: `READY_FOR_MANUAL_REVIEW`.
Reason: package is `DRAFT` and requires manual approval before ML ingest.

Validation: `py_compile PASS`; focused tests `71/71 OK`; package audit content check `PASS`.

Next strict step: `3.7 Закрытие этапа 3`.

## ML Candidate Package Stage 3.5 Manifest 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.

Current fact: package-local `manifest.json` exists and parses:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/manifest.json`

Manifest fields: `SOLUSDT / 1m / core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`, `B018/F051/F051_BOSDOWN_ALLOW`, status `DRAFT`.

Validation: `py_compile PASS`; focused tests `69/69 OK`; manifest parse/content audit `PASS`.

Next strict step: `3.6 Добавить audit.md`.

## ML Candidate Package Stage 3.4 Source Reports 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.

Current fact: package-local source reports exist:
1. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports.json`
2. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/oos_report.json`
3. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/pipeline_report.json`

Optional `optuna_report.json` is `NOT_PROVIDED` for this candidate.

Validation: `py_compile PASS`; focused tests `67/67 OK`.

Next strict step: `3.5 Добавить manifest.json`.

## ML Candidate Package Stage 3.3 Trade Log 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.

Current fact: package-local `trade_log.csv` exists and passes `ml_trade_dataset_contract`:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/trade_log.csv`

Contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T134753Z.json`.

Validation: `py_compile PASS`; focused tests `65/65 OK`.

Next strict step: `3.4 Добавить исходные отчеты`.

## ML Candidate Package Stage 3.2 Calibration Package 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.

Current fact: `calibration_package.json` exists and parses:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/calibration_package.json`

Package fields: `B018/F051/F051_BOSDOWN_ALLOW`, signal mode `short_only`, status `DRAFT`, `4` calibration params.

Validation: `py_compile PASS`; focused tests `63/63 OK`.

Next strict step: `3.3 Добавить trade_log.csv`.

## ML Candidate Package Stage 3.1 Structure 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.

Current fact: package builder skeleton exists at `src/mlbotnav/ml_candidate_package_builder.py`.

Created package directory:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`

Validation: `py_compile PASS`; focused tests `61/61 OK`.

Boundary: no `calibration_package.json`, `trade_log.csv`, `manifest.json`, `audit.md`, or `APPROVED_FOR_ML` yet.

Next strict step: `3.2 Добавить calibration_package.json`.

## ML Trade Dataset Stage 2 Closeout 2026-06-23
Status: `stage_2_closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.

Current fact: Stage 2 `Trade Log CSV Enrichment` is closed. Pipeline and OOS trade CSV artifacts now pass `ml_trade_dataset_contract`.

Evidence:
1. Pipeline contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133238Z.json`.
2. OOS contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133240Z.json`.
3. Focused tests: `59/59 OK`.
4. Text guard: `reports/qa_gate/recovery_r5_text_guard_20260623T133249Z.json`.

Boundary: no automatic ML approval. Stage 3 starts candidate package builder work.

Next strict step: `3.1 Создать структуру пакета`.

## ML Trade Dataset Stage 2.8 OOS CSV 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.

Current fact: fresh OOS CSV `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.csv` passed `ml_trade_dataset_contract`.

Contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T132804Z.json`.

OOS result: net return pct `-0.9395906630311424`, trades `3`, goal pass `false`. Strategy quality is not the gate for WBS `2.8`.

Next strict step: `2.9 Закрытие этапа 2`.

## ML Trade Dataset Stage 2.7 Pipeline CSV 2026-06-23
Status: `done / closed_pass_after_controlled_temp_unlock`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.

Current fact: `pipeline_train_eval.py` now supports `--layer` and writes the selected layer into trade CSV run context. This fixes the hardcoded `data_layer=raw` issue for future clean `core` ML contract runs.

Runtime validation was completed through controlled temporary unlock. Fresh CSV `reports/pipeline/backtest_trades_SOLUSDT_1m_20260623T132424Z.csv` passed `ml_trade_dataset_contract`.

Contract report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T132425Z.json`.

Readiness was restored to frozen state after the run.

Next strict step: `2.8 Проверить OOS CSV`.

## ML Trade Dataset Stage 2.6 MAE/MFE 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive MAE/MFE labels before write: `mae_pct`, `mfe_pct`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Validation: `py_compile PASS`; focused tests `59/59 OK`; `text_guard PASS`.

Boundary: this is not full Stage 2 closeout yet; pipeline CSV contract verification starts at `2.7`.

Next strict step: `2.7 Проверить pipeline CSV`.

## ML Trade Dataset Stage 2.5 Hit Labels 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive hit labels before CSV write: `tp_hit`, `sl_hit`, `timeout_hit`, `end_of_data_hit`, `sl_ambiguous_hit`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Boundary: this is not full ML-ready CSV yet; MAE/MFE starts at `2.6`.

Next strict step: `2.6 Добавить MAE/MFE`.

## ML Trade Dataset Stage 2.4 Duration Labels 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_4_duration_labels_audit_20260623T125816Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive duration label columns before CSV write: `bars_in_trade`, `holding_seconds`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Fix applied: duration columns are created/cast as `object` before mixed blank/numeric writes.

Boundary: this is not full ML-ready CSV yet; hit labels start at `2.5`, then MAE/MFE follow.

Next strict step: `2.5 Добавить hit labels`.

## ML Trade Dataset Stage 2.1 Run Context 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive run-level context columns before CSV write: `run_id`, `symbol`, `timeframe`, `data_layer`, `train_start`, `train_end`, `test_start`, `test_end`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Boundary: this is not full ML-ready CSV yet; passport context starts at `2.2`, then trade identity/duration/hit labels/MAE-MFE follow.

Next strict step: `2.2 Добавить passport context`.

## ML Trade Dataset Contract Stage 1 Closeout 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.

Current fact: WBS Stage 1 `ML Trade Dataset Contract` is closed. Steps `1.1-1.6` are all `CLOSED_PASS`; the contract and executable validator exist and focused checks pass.

Boundary: real `backtest_trades_*.csv` / `oos_backtest_trades_*.csv` enrichment is not done yet and starts in Stage 2. Do not start the big calibration/OOS run yet.

Next strict step: `2.1 Добавить run-level context`.

## ML Trade Dataset Contract Step 1.6 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_contract_step_1_6_audit_20260623T122406Z.md`.
Validator: `src/mlbotnav/ml_trade_dataset_contract.py`.
Tests: `tests/test_ml_trade_dataset_contract.py`.
CLI report: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T122406Z.json`.

Current fact: executable ML trade dataset contract validation is now in place. It checks required passport/run context, entry/exit fields, trade outcome labels, clean `data_layer=core`, hit-label consistency, `trade_id` uniqueness, and MAE/MFE sign rules.

Validation: `py_compile PASS`; focused unittest `4/4 OK`; CLI smoke `PASS`.

Next strict step: `1.7 Закрытие этапа 1`.

## Optuna / ML / Entry / Exit Alignment Audit 2026-06-23
Status: `done / pass_with_ml_dataset_gaps`.
Artifact: `reports/qa_gate/optuna_ml_entry_exit_alignment_audit_20260623T162411Z.md`.
Action plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Budget: `10-14 hours` engineering work, excluding long runtime waiting.

Current fact: read-only audit checked the current Optuna -> adaptive -> pipeline_train_eval -> oos_evaluate -> backtest chain.

Decision:
1. `calibration_params` propagate correctly from Optuna into train/OOS/backtest and are saved in JSON reports/model payload.
2. Current F051 action gate is isolated as `F051_BOSDOWN_ALLOW`; no old/stale action gate is active for that contour.
3. CSV trade/OOF outputs are not yet ML-ready alone because they do not carry `action_id`, `passport_id`, `block_id`, or `calibration_params_json`.
4. Trade CSV has baseline entry/exit fields and `exit_reason`, but is missing `trade_id`, `bars_in_trade`, `tp_hit`, `sl_hit`, `timeout_hit`, `mae_pct`, and `mfe_pct`.
5. Clean candle layer `core` covers `2026-01-26..2026-05-31`; `2026-06-01` is only raw/quarantine and incomplete to `15:03 UTC`.

Next strict step: implement the ML trade dataset contract and row-level passport/trade outcome fields before any 2-week calibration -> 1-week OOS run. Recommended clean window after contract: train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`, layer `core`.

## Passport Block Registry 2026-06-22T12:57:27Z
Active registry: `configs/calibration_action_passports.yaml`.
Rule: user passports are registered under `Bxxx` blocks before any executable Optuna matrix is used.
`B001` is `Цена и волатильность` / `price_volatility`; active solo passports are `F001-F005` (`ret_1`, `ret_3`, `ret_6`, `ret_12`, `ret_24`).
The B001 combination/tournament path is diagnostic-only; new baseline work should calibrate solo passports first and promote only a tradeful non-negative OOS feature.
Current ids: `B001` active RET_N (`F001-F005`), `B002` active HL spread (`F006`). Further user passport blocks should continue as the next `Bxxx` ids.

## F006 Passport Run 2026-06-22T13:10:45Z
Implemented `F006` (`hl_spread_1m`) in `B002`, matrix `configs/calibration_matrices/passport_actions/F006_hl_spread_1m_entry_filter.yaml`, runtime column `F006_HLSPREAD_ALLOW`, and backtest entry gate support.
Focused checks passed.
Clean direct LONG result: `NO_GO`, params `F006_cmp=-1` (`LESS`), `F006_thr_pct=0.75`, OOS `-6.153363933968025%`, trades `2`.
Audit: `reports/qa_gate/f006_hl_spread_long_only_audit_20260622T131045Z.json`.
Do not use the first 3-worker pool final_review/top-card params for F006 because audit found a same-second artifact mismatch; use the clean direct contour run.

## F007 Passport Run 2026-06-22T13:33:18Z
Implemented `F007` (`rolling_std_20_1m`) in `B003`, matrix `configs/calibration_matrices/passport_actions/F007_rolling_std20_1m_entry_filter.yaml`, runtime column `F007_RSTD20_ALLOW`, and backtest entry gate support.
Focused checks passed.
LONG result: `NO_GO`, params `F007_cmp=1` (`GREATER`), `F007_thr_pct=0.04`, OOS `-1.1459443803135683%`, trades `1`.
SHORT result: `NO_GO`, params `F007_cmp=-1` (`LESS`), `F007_thr_pct=0.34`, OOS `-5.744959575084807%`, trades `3`.
Audit: `reports/qa_gate/f007_rolling_std20_long_short_audit_20260622T133318Z.json`.

## F008 Passport Run 2026-06-22T13:59:47Z
Implemented `F008` (`atr14_1m`) in `B004`, matrix `configs/calibration_matrices/passport_actions/F008_atr14_1m_entry_filter.yaml`, runtime column `F008_ATR14_ALLOW`, and backtest entry gate support.
Focused checks passed.
LONG result: `NO_GO`, params `F008_cmp=-1` (`LESS`), `F008_thr_pct=0.28`, OOS `-1.1459443803135683%`, trades `1`.
SHORT result: `NO_GO`, params `F008_cmp=-1` (`LESS`), `F008_thr_pct=2.33`, OOS `-5.744959575084807%`, trades `3`.
Audit: `reports/qa_gate/f008_atr14_long_short_audit_20260622T135947Z.json`.

## EMA F009-F011 Passport Run 2026-06-22T14:34:20Z
Implemented EMA family in `B005`, matrices `F009_ema_gap_20_50_1m_entry_filter.yaml`, `F010_ema20_slope_5_1m_entry_filter.yaml`, `F011_ema200_gap_1m_entry_filter.yaml`, runtime columns `F009_EMAGAP_ALLOW`, `F010_EMASLOPE5_ALLOW`, `F011_EMA200GAP_ALLOW`, and backtest gate support.
Focused checks passed.
Results: F009 LONG `0%/0 trades`; F009 SHORT `-18.1676%/9 trades`; F010 LONG `-29.1066%/10 trades`; F010 SHORT `-18.6178%/5 trades`; F011 LONG `0%/0 trades`; F011 SHORT `0%/0 trades`.
Decision: `NO_GO`, no tradeful non-negative candidate.
Audit: `reports/qa_gate/ema_f009_f011_long_short_audit_20260622T143420Z.json`.

## F012 RSI14 Passport Run 2026-06-22T14:47:50Z
Implemented `F012` (`rsi14_1m`) in `B006`, matrix `configs/calibration_matrices/passport_actions/F012_rsi14_combined_entry_filter.yaml`, runtime column `F012_RSI14_ALLOW`, and backtest gate support.
Focused checks passed; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T145323Z.json`.
LONG result: `NO_GO`, params `F012_signal_mode=1` (`LEVEL`), `F012_cmp=1` (`GREATER`), `F012_level=88`, OOS `0%`, trades `0`.
SHORT result: `NO_GO`, params `F012_signal_mode=1` (`LEVEL`), `F012_cmp=1` (`GREATER`), `F012_level=30`, OOS `-47.5754123715459%`, trades `22`, wins/losses `1/21`, exits `timeout`.
Audit: `reports/qa_gate/f012_rsi14_combined_long_short_audit_20260622T144750Z.json`.

## F017/F018 Combined Decision 2026-06-23T08:10:00Z
Audit finding closed: `F017/F018` stays one combined Stochastic K/D passport, not two separated action passports.
Reason: `%K` and `%D` are two lines of the same Stochastic instrument, and `KD_CROSS` requires both lines inside one signal grammar.
Runtime/action boundary stays `F017_F018_STOCH14_ALLOW`; this is not old Optuna mixing and not a block-combo tournament.
Existing trusted run remains `NO_GO`: LONG `-84.05333161848922%/51 trades`, SHORT `-17.53680624691214%/6 trades`.
Audit: `reports/qa_gate/f017_f018_combined_decision_audit_20260623T081000Z.md`.

## Stale Action Column Hardening 2026-06-23T08:20:00Z
Fixed the remaining F001-F083 runtime/backtest audit item.
`run_prob_backtest` accepts `active_entry_action_columns`, Optuna passport search passes the current matrix action id, and backtest infers active gates from `Fxxx_*` passport params when needed.
Regression test confirms stale unrelated action columns are ignored for an active passport.
Validation: py_compile PASS; stale/F039 focused tests `2/2 OK`; project venv `tests.test_backtest_fields tests.test_optuna_search_runtime` `110/110 OK`; `text_guard PASS` `reports/qa_gate/recovery_r5_text_guard_20260623T081355Z.json`.
Audit: `reports/qa_gate/stale_action_column_hardening_20260623T082000Z.md`.
Current audit route status: planned gaps closed, F017/F018 combined decision closed, stale action-column hardening closed.

## Passport Control Index 2026-06-23T08:41:37Z
Created the active human control panel: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_CONTROL_INDEX_RU.md`.
Decision: use a hybrid management model, not one huge executable config.
Layers are fixed as: Passport MD -> `configs/calibration_action_passports.yaml` registry -> executable passport matrix -> run/audit artifact.
The index records source-of-truth files, no-mixing rules, block policy, LONG/SHORT policy, exit/ML boundaries, and the standard workflow for the next passports.
Recommended next work: result register is built; `F051 SHORT` validation is complete and failed promotion; choose the next passport/feature route or define a new validation idea.
Audit: `reports/qa_gate/passport_control_index_audit_20260623T084500Z.md`.

## Passport Result Register F001-F083 2026-06-23
Status: `done / active_result_register`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_RESULT_REGISTER_RU.md`.
Audit: `reports/qa_gate/passport_result_register_audit_20260623T084702Z.md`.

Current fact: added the compact F001-F083 result register so the next calibration decisions have one readable control map.

Decision:
1. No `F001-F083` feature is production GO.
2. Only `F051 BOS down SHORT` is a positive test candidate: `+2.810523%`, `1` OOS trade.
3. `F051 SHORT` failed multi-day validation and is not eligible for promotion, ML export, or combination.
4. `NO_GO` rows cannot be reused as active candidates.

Validation: explicit id coverage PASS; text_guard PASS, report `reports/qa_gate/recovery_r5_text_guard_20260623T084932Z.json`.

Next: `F051 SHORT` validation is complete and failed promotion; choose the next passport/feature route or define a new validation idea.

## F051 SHORT Multi-Day Validation 2026-06-23
Status: `done / validation_fail_no_promotion`.
Artifact: `reports/qa_gate/f051_short_multiday_validation_audit_20260623T091000Z.md`.

Current fact: validated the previous one-day positive `F051 BOS down SHORT` candidate on three adjacent OOS windows.

Result:
1. Original baseline `2026-05-31 -> 2026-06-01`: `+2.810523%`, `1` trade.
2. Validation `2026-05-28 -> 2026-05-29`: `0%`, `0` trades.
3. Validation `2026-05-29 -> 2026-05-30`: `0%`, `0` trades.
4. Validation `2026-05-30 -> 2026-05-31`: `0%`, `0` trades.

Decision: `F051 SHORT` failed multi-day validation and is not promotable. Do not export it to ML or combine it with other blocks.

## F001-F083 Passport Route Closeout 2026-06-23
Status: `done / closed_no_production_go`.
Artifact: `reports/qa_gate/f001_f083_route_closeout_audit_20260623T091500Z.md`.

Current fact: closed the full `F001-F083` passport route after `F051 SHORT` failed adjacent-window validation.

Decision:
1. No feature from `F001-F083` is production GO.
2. Nothing from `F001-F083` can move to ML, combination, candidate pool, or execution config.
3. Next work must be a new passport/feature/hypothesis route, a new validation idea, or separate exit/risk passports.

## Core ML Bot TZ Audit 2026-06-23
Status: `done / audit_only / partial_match_with_strong_calibration_core`.
Artifact: `reports/qa_gate/core_ml_bot_tz_audit_20260623_RU.md`.

Audited the project against the user-provided TZ for a compact 1m autonomous ML trading bot core.
Conclusion: the project already has a strong calibration/ML/backtest core in `src/mlbotnav`, but the TZ is only partially matched because modular contracts, complete CORE feature set, entry/exit/risk decision contracts, MAE/MFE, trade outcome labels, and ML dataset builder are not closed as separate layers.
Decision: do not create a parallel `trading_bot/` tree; add thin contracts/facades over `src/mlbotnav`, then fill missing CORE gaps.
Next safe route: feature/entry/exit/risk/trade-log/ML-dataset contracts first, then missing CORE columns, then separate exit/risk passports.

## Active Calibration Source Override
For calibration-node work, the active source of truth is now `docs/CALIBRATION_NODE_CURRENT/`.
Read `README_RU.md`, `TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`, `CURRENT_STATUS_RU.md`, and `COMMANDS_RU.md`.
Old chronology, old journals, old TZ files, and old P20xx/P21xx chains are `OLD/FROZEN` and must not be used as the next-task queue.

## Optuma Bridge Steps 2-5 2026-06-04T09:06:15Z
Active short TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_OPTUMA_BRIDGE_CURRENT_2026-06-04_RU.md`.
Closed current repairs after Step 1: `volume_flow` now applies calibrated `return_lookback` for `vol_chg`, `delta_volume`, `obv_slope_5`; `density_profile` now applies calibrated `div_lookback` for `density_vpoc_drift_20`; `structure_ta` now applies calibrated `threshold_fine` for `retest_flag` and `false_breakout_flag`; FIBO now has `fib_window` and explicit `fib_level` values `0.236/0.382/0.5/0.618/0.786` in the full and catalog block matrices.
Validation: focused tests `95/95 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS` for 7 YAML matrices x 2 contours x 3 grid presets; `text_guard PASS` (`reports/qa_gate/recovery_r5_text_guard_20260604T090928Z.json`).

## Pattern Structure Volume Entry 2026-06-04T09:16:54Z
Closed current repair: `pattern_structure_volume_entry` now has runtime features for classic figure patterns and the `pattern + structure_ta + volume_flow` entry bundle.
Added dataset features: double top/bottom, head-and-shoulders/inverse, triangle, pennant, rising/falling wedge, range, volume confirm, level confirm, long/short entry flags, SL buffer distance, TP ladder score.
Matrices updated: full matrix and catalog block matrices have the new pattern profiles; full matrix and `catalog_block_06_pattern.yaml` include the new pattern feature rows; `vol_z` now uses `vol_z_window`.
Validation: focused tests `97/97 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS`; `text_guard PASS` (`reports/qa_gate/recovery_r5_text_guard_20260604T091818Z.json`).

## Pattern Runtime CPU Pause 2026-06-04T10:20:10Z
Dry command gate passed: `reports/qa_gate/pattern_block06_command_gate_20260604T101700Z.json`.
`pattern long_only narrow` completed runtime OK, workers `3/3`, candidate `NO_CANDIDATE`, max CPU `57%`: `reports/qa_gate/pattern_long_only_narrow_closeout_20260604T101742Z.json`.
`pattern long_only medium` completed launcher OK/workers `3/3`, best OOS `-78.782906127645376%`, trades `35`, candidate `NO_CANDIDATE`, but monitor saw CPU spike `97%`: `reports/qa_gate/pattern_long_only_medium_closeout_20260604T102010Z.json`.
Next current step is paused before `pattern long_only wide`: confirm CPU profile. Options are hard-stop on first CPU sample `>85%`, reduce to `2` process workers / `6` search workers, or explicitly accept brief spikes.

## Pattern Block06 Full Runtime 2026-06-04T10:30:51Z
CPU rule updated by user: short spikes are allowed; sustained `>85%` for roughly `2-5` minutes means reduce profile and continue the same substep.
Completed `pattern` block runtime through `long_only` and `short_only`, each `narrow -> medium -> wide`, on `3/9/3`.
Result: runtime OK, workers `3/3` on all six runs, no worker crash, no sustained CPU overload, candidate `NO_CANDIDATE`.
Best block result: `long_only narrow`, `0%`, trades `0`.
Block artifact: `reports/qa_gate/pattern_block06_full_closeout_20260604T103051Z.json`.
Readable report: `reports/qa_gate/pattern_block06_human_readable_20260604T103051Z_RU.md`.
Important finding after report audit: search-level best candidates contain `calibration_params`, but final `best_oos` fallback selections have `selected_calibration_params={}`. Next repair should preserve calibration params for fallback/no-pass candidate selection, then rerun/replay block06 before calling it parametrically closed.

## Pattern Fallback Calibration Params Fix 2026-06-04T10:43:12Z
Artifact: `reports/qa_gate/pattern_fallback_calibration_params_fix_20260604T104312Z_RU.md`.
Fixed `src/mlbotnav/adaptive_auto_train.py`: adaptive-loop now uses `_candidate_pool_from_search_report` and prefers `top_candidates` when they contain `calibration_params`, instead of losing params through `all_candidates_lite`.
Test added in `tests/test_adaptive_candidate_pick.py`.
Validation: changed file `py_compile PASS`; focused tests `80/80 OK`; old pattern search reports now select fallback candidates with `18` calibration params.
Boundary: old block06 runtime artifacts are not rewritten; rerun/replay block06 to produce final `best_oos.selected_calibration_params` in new artifacts.

## Optuma Bridge Step 1 2026-06-04T08:56:24Z
Active short TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_OPTUMA_BRIDGE_CURRENT_2026-06-04_RU.md`.
Step 1 fixed the `calibration_params` anchor gap: selected Optuna params now move from `adaptive_auto_train.py` candidate selection into `pipeline_train_eval.py`, are saved in train report/model payload, and are applied by `oos_evaluate.py` in feature generation and final backtest.
Validation: changed files `py_compile PASS`; focused tests `79/79 OK` for `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_adaptive_candidate_pick`, `tests.test_optuna_search_runtime`, `tests.test_backtest_fields`.
Next current repair: `volume_flow` formula mismatches (`vol_chg`, `delta_volume`, `obv_slope_5`).

## APTuna Block Alignment Audit 2026-06-03T16:48:08Z
Artifact: `reports/qa_gate/aptuna_block_alignment_audit_20260603T164808Z.json`.
Status: `PASS`, `issues=0`, `blockers=0`.
All 6 calibration blocks align across dataset/features config/draft/full matrix/catalog block matrices/APTuna runner wiring: `price_volatility`, `trend_momentum`, `volume_flow`, `density_profile`, `structure_ta`, `pattern`.
Full matrix facts: `68` feature rows (`56` calibratable, `12` fixed), `20/20` hypothesis rows calibratable.
APTuna reads the active matrix through `MLBOTNAV_CALIBRATION_MATRIX_PATH`; catalog block matrices compile for `long_only` and `short_only` under `narrow/medium/wide`.
Boundary: only sequential feature_sweep matrices `H001` and `H002` are generated so far; `H003` generation/compile remains the next strict step, not an alignment issue.

## Block vs Feature Sweep Boundary 2026-06-03T16:59:00Z
Artifact: `reports/qa_gate/aptuna_block_vs_feature_sweep_audit_20260603T170400Z.json`.
Readable doc: `docs/CALIBRATION_NODE_CURRENT/BLOCK_VS_FEATURE_SWEEP_AUDIT_2026-06-03_RU.md`.
Status: `PASS_WITH_MODE_BOUNDARY`.
Conclusion: `catalog_blocks/*.yaml` is whole-block calibration; generated `feature_sweep/h*.yaml` is single feature-slot calibration. If the operator wants "calibrate the whole block", do not continue `H003` as the main battle path; switch the active queue to catalog block matrices.
Encoding note: older artifact `reports/qa_gate/aptuna_block_vs_feature_sweep_audit_20260603T165900Z.json` was superseded by ASCII-safe JSON because it could show mojibake in Windows/PowerShell.

## Active Sweep Status 2026-06-03T13:16:59Z
Slot `H001` (`price_volatility` / `ret_1` / `return_lookback`) is closed as `slot_complete_runtime_ok_no_candidate`.
Both stacks ran separately: `long_only` and `short_only`, each through `narrow -> medium -> wide` with profile `3x3/9`.
Best long stack result: `medium long_only`, OOS `-8.650246602184342%`, trades `4`, no candidate.
Best short stack result: `narrow short_only`, OOS `0%`, trades `0`, no candidate.
Artifacts: `reports/qa_gate/h001_long_stack_complete_20260603T131326Z.json`, `reports/qa_gate/h001_short_stack_complete_20260603T131659Z.json`, `reports/qa_gate/h001_slot_closeout_20260603T131659Z.json`.
Next strict slot: `H002` (`price_volatility` / `ret_3` / `return_lookback`); first create/compile the H002 matrix, then run `H002 long_only` full stack.

## Active Human-Readable Report Format 2026-06-03T13:30:00Z
Slot numbering rule is fixed: `H001`, `H002`, ... are feature/hypothesis slots. Long/short are child stacks inside the same slot, not separate slot numbers.
Use readable child ids such as `H001-LONG`, `H001-SHORT`, and `H001-SLOT`.
Human reports must show Russian block/tool names, technical name, calibrated params, min/max/step range, narrow/medium/wide results for long and short, best long, best short, final decision, and artifact path.
Example: `H001` is `price_volatility.ret_1`; `H001-LONG` and `H001-SHORT` are already complete. `H002` is the next slot `price_volatility.ret_3`.
Human-readable report file: `reports/optuna_catalog/index/hypothesis_feature_sweep_human_ru.md`.
Format correction 2026-06-03T16:02:12Z: slot card headings must stay short and use exact RU names from `configs/features_block.yaml`, for example `H003 | Доходность за 6 баров`; H003 is `kind=feature_row`, not a hypothesis.
Full RU names catalog: `docs/CALIBRATION_NODE_CURRENT/RU_NAMES_CATALOG_2026-06-03.md`.

## Active Sweep Status 2026-06-03T15:41:33Z
Slot `H002` (`price_volatility` / `ret_3` / `return_lookback`) is closed as `slot_complete_runtime_ok_no_candidate`.
Matrix: `configs/calibration_matrices/feature_sweep/h002_price_volatility_ret_3.yaml`; compile report `reports/qa_gate/h002_feature_sweep_matrix_compile_20260603T153704Z.json`.
Both stacks ran separately: `long_only` and `short_only`, each through `narrow -> medium -> wide` with profile `3x3/9`.
Best long stack result: `wide long_only`, OOS `-8.650246602184342%`, trades `4`, no candidate.
Best short stack result: `narrow/medium short_only`, OOS `-0.2662724500743341%`, trades `2`, no candidate.
Artifacts: `reports/qa_gate/h002_long_stack_complete_20260603T154133Z.json`, `reports/qa_gate/h002_short_stack_complete_20260603T154133Z.json`, `reports/qa_gate/h002_slot_closeout_20260603T154133Z.json`.
Next strict slot: `H003` (`price_volatility` / `ret_6` / `return_lookback`); first create/compile the H003 matrix, then run `H003 long_only` full stack.

## Project
`MLbotNav` is a trading/ML project with an Optuna/APTuna calibration contour for `SOLUSDT` on `1m` data. The current work is focused on launch-quality calibration, not on rebuilding the runtime contour from scratch.

## Current Goal
Build a full Optuna calibration catalog across blocks, features, and hypotheses:
walk active parameter ranges from `min` to `max`, classify every run as `positive`, `negative`, `neutral`, or `infra_fail`, and preserve all parameter/config artifacts. For each block, the block outcome is the best found result by the ranking/gate metrics, not a random run; negative/neutral runs are retained as calibration history, but only the best valid positive result can become `candidate_for_forward`. Production still requires `F1/F2 = 2/2 PASS` plus a new production `GO` decision package.

## Current Calibration Node Update 2026-06-03T11:28:24Z
Active source remains `docs/CALIBRATION_NODE_CURRENT/`.
Closed under the new TZ `2026-06-03T10:25:00Z`: `volume_flow`, `density_profile`, `structure_ta`, and `pattern`.
`structure_ta` completed `narrow/medium/wide` x `long_only/short_only` with runtime `OK` after rerun; best result is `wide long_only` OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production.
`pattern` completed `narrow/medium/wide` x `long_only/short_only` with runtime `OK`; best result is `wide long_only` OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production.
Pattern closeout artifact: `reports/qa_gate/calibration_node_pattern_closeout_20260603T112654Z.json`.
Fix added in `src/mlbotnav/adaptive_auto_train.py`: OOS report JSON is now read via `_read_json_report_with_retry`, so empty/unreadable OOS reports become recorded iteration failures instead of worker crashes.
Focused tests: `83/83 OK`. Health after pattern closeout: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T112958Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T112818Z.json`), `pip check PASS`.
Next active step is not production/unfreeze; it requires a separate new TZ or GO package.

## Current Sequential Sweep Update 2026-06-03T12:18:33Z
User paused the current `TOP_EXPERIMENTAL` candidate and redirected work to a sequential hypothesis/feature sweep.
New active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_HYPOTHESIS_FEATURE_SWEEP_2026-06-03_RU.md`.
Goal: verify that every hypothesis/feature slot walks min->max correctly and records results, not optimize for production profit.
Inventory artifact: `reports/qa_gate/hypothesis_feature_sweep_inventory_20260603T121643Z.json`.
Sweep table: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`.
Slot policy: `H000` baseline/control + `H001-H068` feature rows = `69` logical slots. Matrix has `68` feature rows: `56` calibratable, `12` non-calibratable; `H000` is non-calibrated control.
`H001` matrix created and compile passed: `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`, report `reports/qa_gate/h001_feature_sweep_matrix_compile_20260603T121833Z.json`.
`H001 narrow long_only` completed: launcher `OK`, workers `3/3 exit_code=0`, best OOS `-30.924389997582892%`, trades `13`, class `negative_runtime_ok`.
Artifact: `reports/qa_gate/h001_narrow_long_only_20260603T122520Z.json`.
TZ corrected: long and short are separate stacks; each stack runs `narrow -> medium -> wide`; standard profile is `3x3/9` with trials/timeouts `narrow=60/300`, `medium=120/600`, `wide=180/900`.
`H001 narrow short_only` completed: launcher `OK`, workers `3/3 exit_code=0`, best OOS `+0.2544418318741748%`, trades `1`, class `provisional_plus_goal_fail`, not candidate.
Artifact: `reports/qa_gate/h001_narrow_short_only_20260603T124931Z.json`.
Next command: `H001 medium long_only` 1d->1d from `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`.

## Current Truth
1. Active launch decision is `NO_GO`.
2. Freeze is ON: `project_ready=false`, `enforce_freeze=true`.
3. Historical `GO` records are historical only and are not launch permission.
4. Active track is V3 bounded calibration using `feature/logic` hypotheses.
5. Active overlay is full calibration catalog, not early stop on `NO_CANDIDATE`.

## Done
1. Global launch audit created and synced.
2. V3 `Package A` defined and completed.
3. `Package A long_only`: `9/9` runs completed.
4. `Package A short_only`: `9/9` runs completed.
5. Unified `Package A triage`: `NO_CANDIDATE`.
6. Package-level `Package A post-audit`: `PASS`.
7. Full calibration catalog checkpoint created:
   `reports/qa_gate/p2026_optuna_full_calibration_catalog_checkpoint_20260602T083509Z.json`.
8. Catalog folders created under `reports/optuna_catalog/`.
9. Post-sync audit after catalog checkpoint passed:
   `reports/qa_gate/p2027_optuna_full_calibration_catalog_post_sync_audit_20260602T083823Z.json`.
10. Step 1 wiring inventory passed:
   `reports/optuna_catalog/index/p2030_step1_wiring_inventory_20260602T092159Z.json`.
11. Step 2 smoke command set passed:
   `reports/optuna_catalog/index/p2032_step2_1d1d_smoke_command_set_20260602T092710Z.json`.
12. Step 3 smoke preflight passed:
   `reports/qa_gate/p2034_step3_smoke_preflight_20260602T093214Z.json`.
13. Step 4 long_only smoke catalog entry:
   `reports/optuna_catalog/neutral/p2035_step4_long_only_1d1d_smoke_neutral_20260602T093324Z.json`.
14. Step 5 short_only smoke catalog entry:
   `reports/optuna_catalog/neutral/p2036_step5_short_only_1d1d_smoke_provisional_plus_goal_fail_20260602T093604Z.json`.
15. Step 6 triage:
   `reports/qa_gate/p2037_step6_1d1d_smoke_triage_20260602T093704Z.json`.
16. Step 7 medium command set passed:
   `reports/optuna_catalog/index/p2039_step7_medium_command_set_20260602T095335Z.json`.
17. Step 7 medium long_only catalog entry:
   `reports/optuna_catalog/negative/p2040_step7_medium_long_only_negative_20260602T095814Z.json`.
18. Step 7 medium short_only catalog entry:
   `reports/optuna_catalog/negative/p2041_step7_medium_short_only_negative_20260602T100012Z.json`.
19. Step 7 medium triage:
   `reports/qa_gate/p2042_step7_medium_triage_20260602T100020Z.json`.
20. Step 7 medium post-sync audit:
   `reports/qa_gate/p2043_step7_medium_post_sync_audit_20260602T100235Z.json`.
21. Step 8 wide command set passed:
   `reports/optuna_catalog/index/p2044_step8_wide_command_set_20260602T100351Z.json`.
22. Step 8 wide runtime and triage completed:
   `reports/qa_gate/p2047_step8_wide_triage_20260602T100725Z.json`.
23. Step 9 catalog ranking completed:
   `reports/optuna_catalog/index/p2048_step9_catalog_ranking_20260602T100735Z.json`.
24. Step 10/11 no-forward boundary completed:
   `reports/qa_gate/p2049_full_catalog_no_forward_boundary_20260602T100745Z.json`.
25. Full catalog closeout post-sync audit:
   `reports/qa_gate/p2050_full_catalog_closeout_post_sync_audit_20260602T101019Z.json`.
26. Block-level catalog cycle setup:
   `reports/optuna_catalog/index/p2051_block_level_catalog_cycle_setup_20260602T101240Z.json`.
27. Block01 `price_volatility` narrow command set:
   `reports/optuna_catalog/index/p2052_block01_price_volatility_narrow_command_set_20260602T101347Z.json`.
28. Block01 `price_volatility` full narrow/medium/wide triage:
   `reports/qa_gate/p2063_block01_price_volatility_full_triage_20260602T102218Z.json`.
29. Block01 post-sync audit:
   `reports/qa_gate/p2064_block01_price_volatility_post_sync_audit_20260602T102259Z.json`.
30. Block02 `trend_momentum` narrow triage:
   `reports/qa_gate/p2068_block02_trend_momentum_narrow_triage_20260602T102600Z.json`.
31. Block02 `trend_momentum` medium command set and triage:
   `reports/optuna_catalog/index/p2069_block02_trend_momentum_medium_command_set_20260602T102746Z.json`;
   `reports/qa_gate/p2072_block02_trend_momentum_medium_triage_20260602T102940Z.json`.
32. Block02 `trend_momentum` wide command set and triage:
   `reports/optuna_catalog/index/p2073_block02_trend_momentum_wide_command_set_20260602T103008Z.json`;
   `reports/qa_gate/p2076_block02_trend_momentum_full_triage_20260602T103215Z.json`.
33. Block02 post-sync audit:
   `reports/qa_gate/p2077_block02_trend_momentum_post_sync_audit_20260602T103526Z.json`.
34. Block03 `volume_flow` narrow command set:
   `reports/optuna_catalog/index/p2078_block03_volume_flow_narrow_command_set_20260602T103918Z.json`.
35. Block03 `volume_flow` narrow triage:
   `reports/qa_gate/p2081_block03_volume_flow_narrow_triage_20260602T104055Z.json`.
36. Block03 `volume_flow` medium triage:
   `reports/qa_gate/p2085_block03_volume_flow_medium_triage_20260602T104430Z.json`.
37. Block03 `volume_flow` full triage:
   `reports/qa_gate/p2089_block03_volume_flow_full_triage_20260602T104655Z.json`.
38. Block03 post-sync audit:
   `reports/qa_gate/p2090_block03_volume_flow_post_sync_audit_20260602T104830Z.json`.
39. Block04 `density_profile` narrow triage:
   `reports/qa_gate/p2094_block04_density_profile_narrow_triage_20260602T105240Z.json`.
40. Block04 `density_profile` medium triage:
   `reports/qa_gate/p2098_block04_density_profile_medium_triage_20260602T105530Z.json`.
41. Block04 `density_profile` full triage:
   `reports/qa_gate/p2102_block04_density_profile_full_triage_20260602T105800Z.json`.
42. Block04 post-sync audit:
   `reports/qa_gate/p2103_block04_density_profile_post_sync_audit_20260602T105853Z.json`.
43. Block05 `structure_ta` narrow triage:
   `reports/qa_gate/p2107_block05_structure_ta_narrow_triage_20260602T110220Z.json`.
44. Block05 `structure_ta` medium triage:
   `reports/qa_gate/p2111_block05_structure_ta_medium_triage_20260602T110445Z.json`.
45. Block05 `structure_ta` full triage:
   `reports/qa_gate/p2115_block05_structure_ta_full_triage_20260602T110710Z.json`.
46. Block05 post-sync audit:
   `reports/qa_gate/p2116_block05_structure_ta_post_sync_audit_20260602T110808Z.json`.
47. Block06 `pattern` full triage:
   `reports/qa_gate/p2128_block06_pattern_full_triage_20260602T111625Z.json`.
48. Block-level catalog ranking:
   `reports/optuna_catalog/index/p2130_block_level_catalog_ranking_20260602T111745Z.json`.
49. Block-level forward boundary:
   `reports/qa_gate/p2131_block_level_forward_boundary_20260602T111745Z.json`.
50. Block-level catalog closeout post-sync audit:
   `reports/qa_gate/p2132_block_level_catalog_closeout_post_sync_audit_20260602T111822Z.json`.
51. P2079 F1/F2 forward stability command set prepared:
   `reports/optuna_catalog/index/p2133_p2079_forward_stability_command_set_20260602T112708Z.json`.
   Status: `BLOCKED_BY_DATA`; command syntax `PASS`; production/unfreeze remains blocked.
52. P2079 F1/F2 forward preflight data gate repeated:
   `reports/qa_gate/p2134_p2079_forward_preflight_data_gate_20260602T113136Z.json`.
   Status: `BLOCKED_BY_UTC_CLOSE_AND_DATA`; raw max day `2026-06-01`, core max day `2026-05-31`.
53. P2079 forward data ingest route fixed:
   `reports/qa_gate/p2135_p2079_forward_data_ingest_route_20260602T113532Z.json`.
   Status: `ROUTE_READY_WAIT_UTC_CLOSE`; no ingestion/runtime launched.
54. P2079 post-close heartbeat scheduled:
   automation id `p2079-f1-data-gate-check`, scheduled `2026-06-03 05:05` Asia/Yekaterinburg.
   Scope: only verify UTC close, ingest closed raw `2026-06-02` if needed, then F1 preflight.
55. Previous V3 TZ pointer restored after user correction:
   `reports/qa_gate/p2137_previous_tz_recovery_package_b_pointer_20260602T123736Z.json`.
   Status: `PACKAGE_B_POINTER_RESTORED`; the skipped/unclosed item is exact V3 `Package B` slot definition.
   The P2079 heartbeat was paused so forward does not auto-advance before Package B is restored.
56. Previous TZ recovery post-sync audit passed:
   `reports/qa_gate/p2138_previous_tz_recovery_post_sync_audit_20260602T123949Z.json`.
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`.
57. Timed Package B step chain fixed:
   `reports/qa_gate/p2139_package_b_timed_step_chain_20260602T124520Z.json`.
   UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`.
   TZ anchor: V3 section 7, `2026-06-02T06:52:50Z`, Package A `NO_CANDIDATE` -> exact Package B slot definition.
58. Independent agent/audit cross-check completed:
   `reports/qa_gate/p2139_independent_agent_crosscheck_20260602T125117Z.json`.
   UTC `2026-06-02T12:51:17Z`, local `2026-06-02 17:51:17 +05:00`.
   Conclusion: route is `CORRECT_WITH_BOUNDARY`; next must be read-only `P2140 inventory`, not runtime or P2079 forward.
59. `P2140` Step 1 inventory completed:
   `reports/qa_gate/p2140_v3_package_b_inventory_20260602T125900Z.json`.
   Started UTC `2026-06-02T12:45:20Z`, completed UTC `2026-06-02T12:59:00Z`.
   Status: `PASS`; old Package B artifacts are historical V2/strict only; current V3 Package B exact slots/matrices are not defined yet.
60. `P2141` Step 2 exact V3 Package B slots completed:
   `reports/qa_gate/p2141_v3_package_b_exact_slots_20260602T130000Z.json`.
   Started UTC `2026-06-02T12:59:47Z`, completed UTC `2026-06-02T13:00:00Z`.
   Status: `PASS`; slots B-H1/B-H2/B-H3 fixed; next is `P2142` matrix slices + command set/dry-run only.
61. `P2142` Step 3 matrix slices and command-set/dry-run completed:
   `reports/qa_gate/p2142_v3_package_b_command_set_20260602T130559Z.json`.
   Started UTC `2026-06-02T13:02:00Z`, completed UTC `2026-06-02T13:05:59Z`; local completed `2026-06-02 18:05:59 +05:00`.
   Status: `PASS`; 4 matrix slices generated, 18 exact commands emitted, dry-run/preflight `18/18 PASS`; next is `P2143` Package B `long_only` runtime only.
62. `P2142` post-sync checks passed:
   `reports/qa_gate/p2142_v3_package_b_post_sync_audit_20260602T130840Z.json`.
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2142 JSON/YAML parse `PASS`.
63. `P2143` Step 4 Package B `long_only` runtime completed:
   `reports/qa_gate/p2143_v3_package_b_long_only_summary_20260602T131035Z.json`.
   Started UTC `2026-06-02T13:10:35Z`, completed UTC `2026-06-02T13:15:35Z`; local completed `2026-06-02 18:15:35 +05:00`.
   Runtime `9/9 PASS`; catalog class `neutral`, accepted positive candidates `0`.
   Catalog artifact: `reports/optuna_catalog/neutral/p2143_v3_package_b_long_only_neutral_20260602T131535Z.json`.
64. `P2143` post-sync checks passed:
   `reports/qa_gate/p2143_v3_package_b_post_sync_audit_20260602T131847Z.json`.
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2143 JSON/JSONL parse `PASS`.
65. `P2144` Step 5 Package B `short_only` runtime completed:
   `reports/qa_gate/p2144_v3_package_b_short_only_summary_20260602T132020Z.json`.
   Started UTC `2026-06-02T13:20:20Z`, completed UTC `2026-06-02T13:24:20Z`; local completed `2026-06-02 18:24:20 +05:00`.
   Runtime `9/9 PASS`; catalog class `neutral`, accepted positive candidates `0`.
   Catalog artifact: `reports/optuna_catalog/neutral/p2144_v3_package_b_short_only_neutral_20260602T132420Z.json`.
66. `P2144` post-sync checks passed:
   `reports/qa_gate/p2144_v3_package_b_post_sync_audit_20260602T132701Z.json`.
   `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2144 JSON/JSONL parse `PASS`.
67. `P2145` Step 6 Package B unified triage completed:
   `reports/qa_gate/p2145_v3_package_b_unified_triage_20260602T132830Z.json`.
   Started UTC `2026-06-02T13:28:00Z`, completed UTC `2026-06-02T13:28:30Z`; local completed `2026-06-02 18:28:30 +05:00`.
   Result: `NO_CANDIDATE`; totals positive `0`, neutral `18`, negative `0`, infra_fail `0`.
68. `P2146` Step 7 Package B post-sync audit completed:
   `reports/qa_gate/p2146_v3_package_b_post_sync_audit_20260602T133021Z.json`.
   Started UTC `2026-06-02T13:30:00Z`, completed UTC `2026-06-02T13:30:21Z`; local completed `2026-06-02 18:30:21 +05:00`.
   Status: `PASS`; text_guard/readiness/pip/artifact parse clean, readiness freeze preserved.
69. `P2147` Step 8 Package B closeout transition completed:
   `reports/qa_gate/p2147_v3_package_b_closeout_transition_20260602T133330Z.json`.
   Started UTC `2026-06-02T13:33:00Z`, completed UTC `2026-06-02T13:33:30Z`; local completed `2026-06-02 18:33:30 +05:00`.
   Decision: `GO_TO_FINAL_V3_NO_GO_DECISION_PACKAGE`; no next runtime allowed from Package B.
70. `P2148` final V3 `NO_GO` decision package completed:
   `reports/qa_gate/p2148_v3_final_no_go_decision_20260602T133600Z.json`.
   Started UTC `2026-06-02T13:35:30Z`, completed UTC `2026-06-02T13:36:00Z`; local completed `2026-06-02 18:36:00 +05:00`.
   Final launch decision: `NO_GO`; no production-ready candidate; launch/unfreeze blocked.
71. `P2149` final V3 `NO_GO` post-sync audit completed:
   `reports/qa_gate/p2149_v3_final_no_go_post_sync_audit_20260602T133845Z.json`.
   Started UTC `2026-06-02T13:38:20Z`, completed UTC `2026-06-02T13:38:45Z`; local completed `2026-06-02 18:38:45 +05:00`.
   Status: `PASS`; V3 chain closed, readiness freeze preserved.
72. `P2150` post-V3 catalog/forward boundary selection completed:
   `reports/qa_gate/p2150_post_v3_catalog_forward_boundary_20260602T134150Z.json`.
   Started UTC `2026-06-02T13:41:20Z`, completed UTC `2026-06-02T13:41:50Z`; local completed `2026-06-02 18:41:50 +05:00`.
   Status: `ROUTE_SELECTED_WAIT_UTC_CLOSE`; next number `P2151` is blocked until `2026-06-03T00:00:00Z`.
73. `P2151` P2079 F1 data gate pre-close check completed:
   `reports/qa_gate/p2151_p2079_f1_data_gate_preclose_check_20260602T141711Z.json`.
   Started UTC `2026-06-02T14:17:00Z`, completed UTC `2026-06-02T14:17:11Z`; local completed `2026-06-02 19:17:11 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; next number `P2152` is blocked until `2026-06-03T00:00:00Z`.
74. `P2152` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2152_p2079_f1_data_gate_utc_close_recheck_20260602T142042Z.json`.
   Started UTC `2026-06-02T14:20:30Z`, completed UTC `2026-06-02T14:20:42Z`; local completed `2026-06-02 19:20:42 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; next number `P2153` is blocked until `2026-06-03T00:00:00Z`.
75. `P2153` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2153_p2079_f1_data_gate_utc_close_recheck_20260602T142319Z.json`.
   Started UTC `2026-06-02T14:23:10Z`, completed UTC `2026-06-02T14:23:19Z`; local completed `2026-06-02 19:23:19 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; next number `P2154` is blocked until `2026-06-03T00:00:00Z`.
76. `P2154` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2154_p2079_f1_data_gate_utc_close_recheck_20260602T142553Z.json`.
   Started UTC `2026-06-02T14:25:45Z`, completed UTC `2026-06-02T14:25:53Z`; local completed `2026-06-02 19:25:53 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; next number `P2155` is blocked until `2026-06-03T00:00:00Z`.
77. `P2155` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2155_p2079_f1_data_gate_utc_close_recheck_20260602T142920Z.json`.
   Started UTC `2026-06-02T14:29:02Z`, completed UTC `2026-06-02T14:29:20Z`; local completed `2026-06-02 19:29:20 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143136Z.json`, `reports/readiness/readiness_check_20260602T143136Z.json`, `pip check`, artifact parse); next number `P2156` is blocked until `2026-06-03T00:00:00Z`.
78. `P2156` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2156_p2079_f1_data_gate_utc_close_recheck_20260602T143308Z.json`.
   Started UTC `2026-06-02T14:33:00Z`, completed UTC `2026-06-02T14:33:08Z`; local completed `2026-06-02 19:33:08 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143445Z.json`, `reports/readiness/readiness_check_20260602T143445Z.json`, `pip check`, artifact parse); next number `P2157` is blocked until `2026-06-03T00:00:00Z`.
79. `P2157` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2157_p2079_f1_data_gate_utc_close_recheck_20260602T143625Z.json`.
   Started UTC `2026-06-02T14:36:20Z`, completed UTC `2026-06-02T14:36:25Z`; local completed `2026-06-02 19:36:25 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143926Z.json`, `reports/readiness/readiness_check_20260602T143925Z.json`, `pip check`, artifact parse); next number `P2158` is blocked until `2026-06-03T00:00:00Z`.
80. `P2158` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2158_p2079_f1_data_gate_utc_close_recheck_20260602T144030Z.json`.
   Started UTC `2026-06-02T14:40:23Z`, completed UTC `2026-06-02T14:40:30Z`; local completed `2026-06-02 19:40:30 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144209Z.json`, `reports/readiness/readiness_check_20260602T144207Z.json`, `pip check`, artifact parse); next number `P2159` is blocked until `2026-06-03T00:00:00Z`.
81. `P2159` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2159_p2079_f1_data_gate_utc_close_recheck_20260602T144317Z.json`.
   Started UTC `2026-06-02T14:43:10Z`, completed UTC `2026-06-02T14:43:17Z`; local completed `2026-06-02 19:43:17 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144457Z.json`, `reports/readiness/readiness_check_20260602T144456Z.json`, `pip check`, artifact parse); next number `P2160` is blocked until `2026-06-03T00:00:00Z`.
82. `P2160` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2160_p2079_f1_data_gate_utc_close_recheck_20260602T144607Z.json`.
   Started UTC `2026-06-02T14:46:00Z`, completed UTC `2026-06-02T14:46:07Z`; local completed `2026-06-02 19:46:07 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144742Z.json`, `reports/readiness/readiness_check_20260602T144742Z.json`, `pip check`, artifact parse); next number `P2161` is blocked until `2026-06-03T00:00:00Z`.
83. `P2161` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2161_p2079_f1_data_gate_utc_close_recheck_20260602T144943Z.json`.
   Started UTC `2026-06-02T14:49:38Z`, completed UTC `2026-06-02T14:49:43Z`; local completed `2026-06-02 19:49:43 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145122Z.json`, `reports/readiness/readiness_check_20260602T145121Z.json`, `pip check`, artifact parse); next number `P2162` is blocked until `2026-06-03T00:00:00Z`.
84. `P2162` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2162_p2079_f1_data_gate_utc_close_recheck_20260602T145228Z.json`.
   Started UTC `2026-06-02T14:52:21Z`, completed UTC `2026-06-02T14:52:28Z`; local completed `2026-06-02 19:52:28 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145406Z.json`, `reports/readiness/readiness_check_20260602T145405Z.json`, `pip check`, artifact parse); next number `P2163` is blocked until `2026-06-03T00:00:00Z`.
85. `P2163` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2163_p2079_f1_data_gate_utc_close_recheck_20260602T145522Z.json`.
   Started UTC `2026-06-02T14:55:15Z`, completed UTC `2026-06-02T14:55:22Z`; local completed `2026-06-02 19:55:22 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145702Z.json`, `reports/readiness/readiness_check_20260602T145701Z.json`, `pip check`, artifact parse); next number `P2164` is blocked until `2026-06-03T00:00:00Z`.
86. `P2164` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2164_p2079_f1_data_gate_utc_close_recheck_20260602T150019Z.json`.
   Started UTC `2026-06-02T15:00:19Z`, completed UTC `2026-06-02T15:00:19Z`; local completed `2026-06-02 20:00:19 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150225Z.json`, `reports/readiness/readiness_check_20260602T150225Z.json`, `pip check`, artifact parse); next number `P2165` is blocked until `2026-06-03T00:00:00Z`.
87. `P2165` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2165_p2079_f1_data_gate_utc_close_recheck_20260602T150436Z.json`.
   Started UTC `2026-06-02T15:04:36Z`, completed UTC `2026-06-02T15:04:36Z`; local completed `2026-06-02 20:04:36 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150617Z.json`, `reports/readiness/readiness_check_20260602T150617Z.json`, `pip check`, artifact parse); next number `P2166` is blocked until `2026-06-03T00:00:00Z`.
88. `P2166` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2166_p2079_f1_data_gate_utc_close_recheck_20260602T150732Z.json`.
   Started UTC `2026-06-02T15:07:32Z`, completed UTC `2026-06-02T15:07:32Z`; local completed `2026-06-02 20:07:32 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150915Z.json`, `reports/readiness/readiness_check_20260602T150915Z.json`, `pip check`, artifact parse); next number `P2167` is blocked until `2026-06-03T00:00:00Z`.
89. `P2167` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2167_p2079_f1_data_gate_utc_close_recheck_20260602T151030Z.json`.
   Started UTC `2026-06-02T15:10:30Z`, completed UTC `2026-06-02T15:10:30Z`; local completed `2026-06-02 20:10:30 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151314Z.json`, `reports/readiness/readiness_check_20260602T151314Z.json`, `pip check`, artifact parse); next number `P2168` is blocked until `2026-06-03T00:00:00Z`.
90. `P2168` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2168_p2079_f1_data_gate_utc_close_recheck_20260602T151532Z.json`.
   Started UTC `2026-06-02T15:15:32Z`, completed UTC `2026-06-02T15:15:32Z`; local completed `2026-06-02 20:15:32 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151714Z.json`, `reports/readiness/readiness_check_20260602T151713Z.json`, `pip check`, artifact parse); next number `P2169` is blocked until `2026-06-03T00:00:00Z`.
91. `P2169` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2169_p2079_f1_data_gate_utc_close_recheck_20260602T151826Z.json`.
   Started UTC `2026-06-02T15:18:26Z`, completed UTC `2026-06-02T15:18:26Z`; local completed `2026-06-02 20:18:26 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152005Z.json`, `reports/readiness/readiness_check_20260602T152004Z.json`, `pip check`, artifact parse); next number `P2170` is blocked until `2026-06-03T00:00:00Z`.
92. `P2170` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2170_p2079_f1_data_gate_utc_close_recheck_20260602T152120Z.json`.
   Started UTC `2026-06-02T15:21:20Z`, completed UTC `2026-06-02T15:21:20Z`; local completed `2026-06-02 20:21:20 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152306Z.json`, `reports/readiness/readiness_check_20260602T152305Z.json`, `pip check`, artifact parse); next number `P2171` is blocked until `2026-06-03T00:00:00Z`.
93. `P2171` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2171_p2079_f1_data_gate_utc_close_recheck_20260602T152559Z.json`.
   Started UTC `2026-06-02T15:25:59Z`, completed UTC `2026-06-02T15:25:59Z`; local completed `2026-06-02 20:25:59 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152826Z.json`, `reports/readiness/readiness_check_20260602T152825Z.json`, `pip check`, artifact parse); next number `P2172` is blocked until `2026-06-03T00:00:00Z`.
94. `P2172` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2172_p2079_f1_data_gate_utc_close_recheck_20260602T152940Z.json`.
   Started UTC `2026-06-02T15:29:40Z`, completed UTC `2026-06-02T15:29:40Z`; local completed `2026-06-02 20:29:40 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153127Z.json`, `reports/readiness/readiness_check_20260602T153126Z.json`, `pip check`, artifact parse); next number `P2173` is blocked until `2026-06-03T00:00:00Z`.
95. `P2173` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2173_p2079_f1_data_gate_utc_close_recheck_20260602T153242Z.json`.
   Started UTC `2026-06-02T15:32:42Z`, completed UTC `2026-06-02T15:32:42Z`; local completed `2026-06-02 20:32:42 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153429Z.json`, `reports/readiness/readiness_check_20260602T153428Z.json`, `pip check`, artifact parse); next number `P2174` is blocked until `2026-06-03T00:00:00Z`.
96. `P2174` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2174_p2079_f1_data_gate_utc_close_recheck_20260602T153532Z.json`.
   Started UTC `2026-06-02T15:35:32Z`, completed UTC `2026-06-02T15:35:32Z`; local completed `2026-06-02 20:35:32 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153717Z.json`, `reports/readiness/readiness_check_20260602T153716Z.json`, `pip check`, artifact parse); next number `P2175` is blocked until `2026-06-03T00:00:00Z`.
97. `P2175` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2175_p2079_f1_data_gate_utc_close_recheck_20260602T153821Z.json`.
   Started UTC `2026-06-02T15:38:21Z`, completed UTC `2026-06-02T15:38:21Z`; local completed `2026-06-02 20:38:21 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154009Z.json`, `reports/readiness/readiness_check_20260602T154008Z.json`, `pip check`, artifact parse); next number `P2176` is blocked until `2026-06-03T00:00:00Z`.
98. `P2176` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2176_p2079_f1_data_gate_utc_close_recheck_20260602T154114Z.json`.
   Started UTC `2026-06-02T15:41:14Z`, completed UTC `2026-06-02T15:41:14Z`; local completed `2026-06-02 20:41:14 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154333Z.json`, `reports/readiness/readiness_check_20260602T154333Z.json`, `pip check`, artifact parse); next number `P2177` is blocked until `2026-06-03T00:00:00Z`.
99. `P2177` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2177_p2079_f1_data_gate_utc_close_recheck_20260602T154446Z.json`.
   Started UTC `2026-06-02T15:44:46Z`, completed UTC `2026-06-02T15:44:46Z`; local completed `2026-06-02 20:44:46 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154634Z.json`, `reports/readiness/readiness_check_20260602T154633Z.json`, `pip check`, artifact parse); next number `P2178` is blocked until `2026-06-03T00:00:00Z`.
100. `P2178` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2178_p2079_f1_data_gate_utc_close_recheck_20260602T154806Z.json`.
   Started UTC `2026-06-02T15:48:06Z`, completed UTC `2026-06-02T15:48:06Z`; local completed `2026-06-02 20:48:06 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155005Z.json`, `reports/readiness/readiness_check_20260602T155004Z.json`, `pip check`, artifact parse); next number `P2179` is blocked until `2026-06-03T00:00:00Z`.
101. `P2179` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2179_p2079_f1_data_gate_utc_close_recheck_20260602T155119Z.json`.
   Started UTC `2026-06-02T15:51:19Z`, completed UTC `2026-06-02T15:51:19Z`; local completed `2026-06-02 20:51:19 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155304Z.json`, `reports/readiness/readiness_check_20260602T155304Z.json`, `pip check`, artifact parse); next number `P2180` is blocked until `2026-06-03T00:00:00Z`.
102. `P2180` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2180_p2079_f1_data_gate_utc_close_recheck_20260602T155433Z.json`.
   Started UTC `2026-06-02T15:54:33Z`, completed UTC `2026-06-02T15:54:33Z`; local completed `2026-06-02 20:54:33 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155722Z.json`, `reports/readiness/readiness_check_20260602T155722Z.json`, `pip check`, artifact parse); next number `P2181` is blocked until `2026-06-03T00:00:00Z`.
103. `P2181` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2181_p2079_f1_data_gate_utc_close_recheck_20260602T155851Z.json`.
   Started UTC `2026-06-02T15:58:51Z`, completed UTC `2026-06-02T15:58:51Z`; local completed `2026-06-02 20:58:51 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160102Z.json`, `reports/readiness/readiness_check_20260602T160101Z.json`, `pip check`, artifact parse); next number `P2182` is blocked until `2026-06-03T00:00:00Z`.
104. `P2182` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2182_p2079_f1_data_gate_utc_close_recheck_20260602T160218Z.json`.
   Started UTC `2026-06-02T16:02:18Z`, completed UTC `2026-06-02T16:02:18Z`; local completed `2026-06-02 21:02:18 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160404Z.json`, `reports/readiness/readiness_check_20260602T160403Z.json`, `pip check`, artifact parse); next number `P2183` is blocked until `2026-06-03T00:00:00Z`.
105. `P2183` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2183_p2079_f1_data_gate_utc_close_recheck_20260602T160516Z.json`.
   Started UTC `2026-06-02T16:05:16Z`, completed UTC `2026-06-02T16:05:16Z`; local completed `2026-06-02 21:05:16 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160705Z.json`, `reports/readiness/readiness_check_20260602T160704Z.json`, `pip check`, artifact parse); next number `P2184` is blocked until `2026-06-03T00:00:00Z`.
106. `P2184` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2184_p2079_f1_data_gate_utc_close_recheck_20260602T160848Z.json`.
   Started UTC `2026-06-02T16:08:48Z`, completed UTC `2026-06-02T16:08:48Z`; local completed `2026-06-02 21:08:48 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161033Z.json`, `reports/readiness/readiness_check_20260602T161033Z.json`, `pip check`, artifact parse); next number `P2185` is blocked until `2026-06-03T00:00:00Z`.
107. `P2185` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2185_p2079_f1_data_gate_utc_close_recheck_20260602T161150Z.json`.
   Started UTC `2026-06-02T16:11:50Z`, completed UTC `2026-06-02T16:11:50Z`; local completed `2026-06-02 21:11:50 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161336Z.json`, `reports/readiness/readiness_check_20260602T161335Z.json`, `pip check`, artifact parse); next number `P2186` is blocked until `2026-06-03T00:00:00Z`.
108. `P2186` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2186_p2079_f1_data_gate_utc_close_recheck_20260602T161530Z.json`.
   Started UTC `2026-06-02T16:15:30Z`, completed UTC `2026-06-02T16:15:30Z`; local completed `2026-06-02 21:15:30 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161633Z.json`, `reports/readiness/readiness_check_20260602T161632Z.json`, `pip check`, artifact parse); next number `P2187` is blocked until `2026-06-03T00:00:00Z`.
109. `P2187` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2187_p2079_f1_data_gate_utc_close_recheck_20260602T161909Z.json`.
   Started UTC `2026-06-02T16:19:09Z`, completed UTC `2026-06-02T16:19:09Z`; local completed `2026-06-02 21:19:09 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161942Z.json`, `reports/readiness/readiness_check_20260602T161941Z.json`, `pip check`, artifact parse); next number `P2188` is blocked until `2026-06-03T00:00:00Z`.
110. `P2188` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2188_p2079_f1_data_gate_utc_close_recheck_20260602T162257Z.json`.
   Started UTC `2026-06-02T16:22:57Z`, completed UTC `2026-06-02T16:22:57Z`; local completed `2026-06-02 21:22:57 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162331Z.json`, `reports/readiness/readiness_check_20260602T162331Z.json`, `pip check`, artifact parse); next number `P2189` is blocked until `2026-06-03T00:00:00Z`.
111. `P2189` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2189_p2079_f1_data_gate_utc_close_recheck_20260602T162548Z.json`.
   Started UTC `2026-06-02T16:25:48Z`, completed UTC `2026-06-02T16:25:48Z`; local completed `2026-06-02 21:25:48 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162627Z.json`, `reports/readiness/readiness_check_20260602T162626Z.json`, `pip check`, artifact parse); next number `P2190` is blocked until `2026-06-03T00:00:00Z`.
112. `P2190` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2190_p2079_f1_data_gate_utc_close_recheck_20260602T163021Z.json`.
   Started UTC `2026-06-02T16:30:21Z`, completed UTC `2026-06-02T16:30:21Z`; local completed `2026-06-02 21:30:21 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163046Z.json`, `reports/readiness/readiness_check_20260602T163046Z.json`, `pip check`, artifact parse); next number `P2191` is blocked until `2026-06-03T00:00:00Z`.
113. `P2191` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2191_p2079_f1_data_gate_utc_close_recheck_20260602T163325Z.json`.
   Started UTC `2026-06-02T16:33:25Z`, completed UTC `2026-06-02T16:33:25Z`; local completed `2026-06-02 21:33:25 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163350Z.json`, `reports/readiness/readiness_check_20260602T163349Z.json`, `pip check`, artifact parse); next number `P2192` is blocked until `2026-06-03T00:00:00Z`.
114. `P2192` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2192_p2079_f1_data_gate_utc_close_recheck_20260602T163604Z.json`.
   Started UTC `2026-06-02T16:36:04Z`, completed UTC `2026-06-02T16:36:04Z`; local completed `2026-06-02 21:36:04 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163630Z.json`, `reports/readiness/readiness_check_20260602T163629Z.json`, `pip check`, artifact parse); next number `P2193` is blocked until `2026-06-03T00:00:00Z`.
115. `P2193` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2193_p2079_f1_data_gate_utc_close_recheck_20260602T163839Z.json`.
   Started UTC `2026-06-02T16:38:39Z`, completed UTC `2026-06-02T16:38:39Z`; local completed `2026-06-02 21:38:39 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163903Z.json`, `reports/readiness/readiness_check_20260602T163902Z.json`, `pip check`, artifact parse); next number `P2194` is blocked until `2026-06-03T00:00:00Z`.
116. `P2194` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2194_p2079_f1_data_gate_utc_close_recheck_20260602T164109Z.json`.
   Started UTC `2026-06-02T16:41:09Z`, completed UTC `2026-06-02T16:41:09Z`; local completed `2026-06-02 21:41:09 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164133Z.json`, `reports/readiness/readiness_check_20260602T164132Z.json`, `pip check`, artifact parse); next number `P2195` is blocked until `2026-06-03T00:00:00Z`.
117. `P2195` P2079 F1 UTC-close recheck completed:
   `reports/qa_gate/p2195_p2079_f1_data_gate_utc_close_recheck_20260602T164502Z.json`.
   Started UTC `2026-06-02T16:45:02Z`, completed UTC `2026-06-02T16:45:02Z`; local completed `2026-06-02 21:45:02 +05:00`.
   Status: `BLOCKED_BY_UTC_CLOSE`; checks `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164527Z.json`, `reports/readiness/readiness_check_20260602T164526Z.json`, `pip check`, artifact parse); next number `P2196` is blocked until `2026-06-03T00:00:00Z`.
118. Structural big-window command-set/dry-run completed:
   `reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json`.
   Status: `PASS`; raw policy preflight `PASS`; compile/dry-run `36/36 PASS`; no runtime started in command-set artifact.
119. Structural big-window narrow runtime started and then stopped by user request:
   `reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`.
   Status: `STOPPED_BY_USER_AND_FREEZE_RESTORED`; completed launcher commands `3`, stopped launcher commands `1`; positive candidates `0`; readiness restored to `project_ready=false`, `enforce_freeze=true`.

## In Work
First task is now a fast `1d -> 1d` calibration smoke/proof contour:
calibrate parameters on one closed 1d train window, apply those calibrated parameters on the next closed 1d test window, and verify wiring, parameter transfer, feature/hypothesis coverage, result classification, and 9-worker/`3x3` execution readiness before broader Package B/catalog execution.

The ordered roadmap is fixed in `P2029`.
Step 1 read-only wiring inventory completed as `P2030` with `PASS`.
Step 2 exact `1d -> 1d` smoke command set completed as `P2032` with `PASS`.
Step 3 smoke preflight completed as `P2034` with `PASS`.
Step 4 long_only smoke completed as `P2035`: `NEUTRAL_NO_TRADE`.
Step 5 short_only smoke completed as `P2036`: `PROVISIONAL_PLUS_GOAL_FAIL`.
Step 6 smoke triage completed as `P2037`: `GO_TO_MEDIUM_WORK`.
Step 7 medium command set completed as `P2039`: `PASS`.
Step 7 medium runtime completed as `P2040`/`P2041`: both `negative`.
Step 7 medium triage completed as `P2042`: `GO_TO_WIDE_BATTLE`.
Step 7 medium post-sync audit completed as `P2043`: `PASS`; freeze preserved.
Step 8 wide runtime completed as `P2045`/`P2046`: both `negative`.
Step 8 wide triage completed as `P2047`: `GO_TO_CATALOG_RANKING`.
Step 9 catalog ranking completed as `P2048`: `NO_FORWARD_CANDIDATE`.
Step 10/11 boundary completed as `P2049`: `NO_FORWARD_CANDIDATE_NO_PRODUCTION_GO`.
Current manual pointer: `P2195` is closed as `BLOCKED_BY_UTC_CLOSE`. Next number `P2196` is P2079 F1 data gate after UTC close; do not run ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
Final post-sync audit completed as `P2050`: `PASS`; freeze preserved.
Do not jump to Package B runtime, medium/wide expansion, or forward stability until the Package B slot definition and command set have an exit artifact/status.

Quick structural audit completed at UTC `2026-06-02T18:27:15Z`:
`reports/qa_gate/quick_structural_audit_framework_20260602T182715Z.json`.
Conclusion: the UTC-close block applies to P2079 forward/production only, not to structural catalog validation on already closed historical data. Framework status is `PASS_WITH_ROUTE_CORRECTION`: 68 feature rows, 6 blocks, 27 linked profiles, narrow/medium/wide grids, 3x3/9-worker launcher support, and block catalog `36/36 runtime OK`. Recommended next chain is a separate structural big-window command set/dry-run on closed history, while P2079 forward gate stays blocked until fresh data close.

Structural big-window command-set passed at UTC `2026-06-02T19:17:37Z`, then narrow runtime was stopped by explicit user request at UTC `2026-06-02T19:23:17Z`.
Do not resume structural runtime unless the user asks. Stop artifact:
`reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`.

After that, extend the Package B runner into the catalog workflow:
fixed slots, `3x3` process-pool profile, classification output, coverage output, and catalog index entries. `Package B` remains bounded, but results must be stored as catalog knowledge even if no launch candidate appears.

## Do Not Forget
1. Do not reopen old infinite remediation loops.
2. Do not treat old unfreeze `GO` as current permission.
3. Do not do micro-audits after every hypothesis tweak.
4. Do not open production actions while freeze is ON.
5. Use APTuna temporary unlock only for calibration runs.
6. Store run outputs as files and reference paths.
7. Do not call a positive catalog item production-ready before forward stability and decision package.
8. Negative results are not discarded; store them as calibration knowledge.

## Key Files
1. `docs/OPTUNA_GLOBAL_LAUNCH_AUDIT_2026-06-02_RU.md`
2. `docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md`
3. `docs/TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md`
4. `docs/ACTIVE_WORK_ITEMS_RU.md`
5. `docs/CHANGELOG_CHRONOLOGY_RU.md`
6. `configs/readiness.yaml`
7. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`
8. `run_optuna_v3_package_a.ps1`
9. `configs/calibration_full_matrix_v1.yaml`
10. `reports/optuna_catalog/`

## Nearest Next Step
Next allowed manual work: paused after user stop. Do not resume structural runtime unless explicitly requested. P2079 forward path remains `P2196` after `2026-06-03T00:00:00Z`, verify/ingest closed raw `2026-06-02` if needed, then repeat F1 preflight only. P2079 runtime, F2, production, and unfreeze remain blocked.

## Previous Nearest Step
Step 7: prepare/run medium work pass only after fixing the exact medium command set. The smoke chain is штатно, but accepted positive candidates remain `0`.

## Hard Structural Audit 2026-06-02T19:16:09Z
Artifact: `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md`.
Status: `PASS_WITH_FINDINGS`.
Conclusion: Optuna/APTuna structure works, but block-level results are not proven as pure block-only strategy results. Feature rows are isolated by `optuna_switches.block_switches`, but hypotheses/trend filters remain global unless explicitly filtered. Example: `P2079` is labeled `volume_flow`, but its top strategy uses `min_max_range_revert`, which requires `structure_ta` columns `position_in_range` and `breakout_flag`.
Next decision before battle calibration: either accept current semantics as "block-feature matrix with global hypotheses" or enforce strict block purity by filtering hypothesis/trend-filter rows by active-block required columns. Recommended: strict block purity before big-window battle calibration.

## P2196A Optuna Battle Readiness Audit 2026-06-03T06:09:19Z
Artifact: `reports/qa_gate/p2196a_optuna_battle_readiness_audit_20260603T060919Z.md`.
Status: `NO_GO_FOR_PRODUCTION / GO_TO_STRICT_BLOCK_PURITY_FIX_BEFORE_BATTLE`.
Current truth: Optuna/APTuna can run structurally, 3x3/9 worker contour works, 36/36 historical block catalog runtime was OK, and 36/36 structural big-window command dry-runs passed. Production remains `NO_GO`, P2079 remains only `candidate_for_forward`, and strict block-hypothesis purity is not proven.
Data gate: UTC close for 2026-06-02 has passed, but raw/core files for `2026-06-02` and `2026-06-03` are absent in the workspace. F1 still needs ingest/preflight PASS; F2 waits for closed 2026-06-03 after `2026-06-04T00:00:00Z`.
Next number: `P2196B` strict block-purity compatibility map and filtering.

## P2196B Volume/Volatility Context Wiring 2026-06-03T06:58:21Z
Artifact: `reports/qa_gate/p2196b_volume_context_wiring_audit_20260603T065821Z.json`.
Status: `PASS_CONTEXT_WIRING / STRICT_HYPOTHESIS_FILTER_PENDING`.
Implemented: `volume_flow` and `price_volatility` are now configured as always-on market context blocks in `configs/calibration_full_matrix_v1.yaml` and all 6 catalog block matrices. `compile_optuna_space` returns `context_blocks` and `effective_feature_blocks`; runtime feature/profile selection includes context blocks; trial/report artifacts record `context_blocks`, `effective_feature_blocks`, and `feature_columns`.
Signal note: raw `volume` remains a market input, not a tunable parameter. Tunable/calibrated volume-derived context comes through `volume_flow` features such as `vol_chg`, `vol_z`, `delta_volume`, `obv_slope_5`, `mfi14`, and `vwap_distance`; rule-only signal now also uses `mfi14`, `vwap_distance`, and `delta_volume` when present.
Validation: `python -m unittest tests.test_optuna_space_constraints tests.test_optuna_search_runtime` -> `69/69 OK`; compile audit checked 7 matrices -> `PASS`.
Post-sync checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T070000Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T065959Z.json`), `pip check PASS`.
Next: continue P2196B strict block-purity compatibility by filtering hypothesis/trend rows by required columns before battle runtime.

## P2196B Strict Hypothesis Filtering 2026-06-03T10:04:04Z
Artifact: `reports/qa_gate/p2196b_strict_hypothesis_filter_full_audit_20260603T100404Z.json`.
Status: `PASS_STRICT_FILTERING`.
Implemented: `hypothesis_switches.strict_block_purity=true` in full matrix and all 6 catalog block matrices. `compile_optuna_space` now maps `trend_filter` required columns to feature blocks and allows a hypothesis only when required blocks are inside `enabled_blocks + context_blocks`; `none` remains always allowed. Runtime fallback no longer re-adds an incompatible CLI/default trend after compiled filtering.
Validation: focused tests `tests.test_optuna_space_constraints tests.test_optuna_search_runtime tests.test_backtest_fields` -> `77/77 OK`; strict compile audit full/catalog x long/short x narrow/medium/wide -> `42/42 PASS`.

## P2196C Strict Command Set Dry-Run 2026-06-03T10:05:04Z
Artifact: `reports/optuna_catalog/index/p2196c_strict_command_set_20260603T100504Z.json`.
Status: `PASS`; dry-run rows `36/36 PASS`.
Window: train `2026-05-29..2026-05-31`, test `2026-06-01`; raw preflight `PASS` at `reports/qa_gate/preflight_window_20260603T100432Z.json`.
Boundary: no Optuna runtime was launched. Next executable calibration step is `P2196D` strict P2079-equivalent `block03 volume_flow narrow long_only`, then strict battle runtime if that check is acceptable.
Residual note: full `unittest discover -s tests` has unrelated residual failures recorded in `reports/qa_gate/p2196c_unittest_discover_residuals_20260603T100559Z.json`; focused strict/battle readiness checks passed.

## P2196D Strict Runtime Calibration Start 2026-06-03T10:14:50Z
Status: `PASS_RUNTIME_OK / EXPERIMENTAL_POSITIVE`.
Command: block03 `volume_flow`, grid `narrow`, mode `long_only`, train `2026-05-29..2026-05-31`, test `2026-06-01`, 3x3/9 workers, temporary calibration unlock.
Result: launcher `OK`; best worker `w3`; best OOS `+1.5266529420731034%`; OOS trades `1`; goal `1.0%` passed by workers `w2` and `w3`.
Artifacts: best summary `reports/adaptive/long_only_pool_20260603t101450z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T101454Z.json`; top experimental card `reports/top_strategy/long_only_pool_20260603t101450z_w3/top_SOLUSDT_1m_2026-06-01_20260603T101522Z_MODE-LONG_ONLY_TF-1M_RET-+1.5267pct/top_strategy_card.json`.
Boundary: train gate did not pass, so it is `TOP_EXPERIMENTAL` only, not production/latest. For the current calibration-contour goal, this is acceptable: the block found a best positive OOS result, applied calibrated params on the next day, saved artifacts, and preserved production freeze.

## P2196E Volume Flow Narrow Short Runtime 2026-06-03T10:21:58Z
Status: `PASS_RUNTIME_OK / NO_CANDIDATE`.
Before fix: first short rerun at `2026-06-03T10:18:59Z` returned `PARTIAL_FAIL` because worker `w1` crashed on empty/unreadable search report JSON in `adaptive_auto_train.py`.
Fix: added safe `_read_json_report_with_retry` and converted unreadable search report into iteration status `search_report_read_failed` instead of worker crash. Focused tests `tests.test_adaptive_candidate_pick tests.test_optuna_space_constraints tests.test_optuna_search_runtime tests.test_backtest_fields` -> `83/83 OK`.
Retest command: block03 `volume_flow`, grid `narrow`, mode `short_only`, train `2026-05-29..2026-05-31`, test `2026-06-01`, 3x3/9 workers.
Retest result: launcher `OK`; all 3 workers exit `0`; best OOS `0%`; trades `0`; no candidate. Best summary `reports/adaptive/short_only_pool_20260603t102158z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T102202Z.json`.

## Calibration Current H006 Pattern Replay 2026-06-04T11:00:12Z
Status: `BLOCK_COMPLETE_RUNTIME_OK_NO_CANDIDATE`.
Active readable report: `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z_RU.md`.
Machine report: `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z.json`.
Fixes: `adaptive_auto_train.py` now preserves `calibration_params` by preferring full `top_candidates`, candidate signatures include `calibration_params`, and each repeat can try up to `8` current search candidates if train fails technically.
Validation: focused tests `81/81 OK`; full H006 runtime replay ran `long_only` and `short_only` through `narrow/medium/wide` on `3x9`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T110352Z.json`.
Result: all 6 launchers `OK`, all final `best_oos` have `18` selected calibration params, worker crash `0`, positive candidate `0`. Best tradeful block result: `short_only medium`, `-15.6997%`, `6` trades.
Next: move to the next block/slot by the active calibration plan only.

## H006 Grid Edge Coverage Audit Fix 2026-06-04T11:15:52Z
Status: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.
Readable report: `reports/qa_gate/h006_grid_edge_coverage_audit_fix_20260604T111552Z_RU.md`.
Fix: `optuna_search_candidate.py` now stores `calibration_params` immediately after sampling, records `calibration_forced_edges`, embeds `grid_edge_coverage_audit` into the search report, and writes `reports/optuna/<mode>/grid_edge_coverage_audit_*.json`.
Runtime smoke: H006 `pattern`, `long_only`, `narrow`, `ProcessWorkers=2`, `SearchWorkers=6`, `OptunaTrials=24`, launcher `OK`. New search report: `reports/pipeline/optuna_search_candidate_SOLUSDT_1m_20260604T111552Z.json`; edge audit: `reports/optuna/long_only/grid_edge_coverage_audit_20260604T111552Z.json`.
Validation: `py_compile PASS`; focused tests `94/94 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T111802Z.json`.
Next: either replay the required full block with the new edge audit to prove min/max on battle budget, or implement the cascade mode `wide -> medium around best -> narrow around best` for LONG and SHORT separately.

## H006 Core Grid Edge Forcing Fix 2026-06-04T11:31:02Z
Status: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.
Readable report: `reports/qa_gate/h006_core_grid_edge_forcing_fix_20260604T113102Z_RU.md`.
Fix: `optuna_search_candidate.py` now force-seeds core Optuna search parameters too: `horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`. First 5 trials force min, next 5 force max; trial attrs include `core_params`, `core_params_suggested`, `core_forced_edges`.
Runtime smoke: H006 `pattern long_only narrow`, `2x6`, `24` total trials, launcher `OK`; search report `reports/pipeline/optuna_search_candidate_SOLUSDT_1m_20260604T113102Z.json`; audit `reports/optuna/long_only/grid_edge_coverage_audit_20260604T113102Z.json`.
Result: core coverage `pass=5`, `fail=0`; profile coverage on the small smoke `pass=14`, `fail=9` as expected for low budget.
Validation: `py_compile PASS`; focused tests `94/94 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T113308Z.json`.
Next: full replay on battle budget with new audit to prove profile min/max, then cascade candidate improvement.

## H006 Full Replay Edge Coverage Pass 2026-06-04T12:39:58Z
Status: `BLOCK_COMPLETE_RUNTIME_OK_EDGE_COVERAGE_PASS_NO_CANDIDATE`.
Readable report: `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z_RU.md`.
Machine report: `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z.json`.
Final fix before replay: core names are excluded from profile audit, edge-on samples the full linked profile set, and profile edge indexing is distributed across `w1/w2/w3`.
Runtime result: H006 `pattern` replay ran LONG and SHORT separately through `narrow/medium/wide`, 3x9 profile. All six launchers returned `OK`; profile coverage `18/18` and core coverage `5/5` in every grid; worker crash `0`; positive candidate `0`.
Best results: LONG narrow `-0.6074%`, `1` trade; SHORT medium `0.0000%`, `0` trades; best tradeful SHORT wide `-20.3243%`, `10` trades.
Validation: `py_compile PASS`; focused tests `95/95 OK`.
Next: implement cascade candidate improvement `wide -> medium around best -> narrow around best`, LONG and SHORT separately.

## CASCADE_BLOCK_CALIBRATION Rule Fixed 2026-06-04T14:17:45Z
Status: `RULE_FIXED_NO_CODE_CHANGES`.
Active TZ updated: `docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`.
Active status updated: `docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md`.
Rule: one block equals one cascade; LONG and SHORT separately; `wide` first; `medium` around best tradeful `wide`; `narrow` around best tradeful `medium`.
Boundary: if `wide` has no tradeful candidate, record `NO_TRADEFUL_CANDIDATE` and move to next block. If the tradeful candidate is negative, continue cascade to measure the best available block result. Positive candidates go to positive/top candidates only, not production.
No code changes and no runtime launched.

## C001 Block 01 LONG Wide Runtime 2026-06-04T14:44:29Z
Status: `RUNTIME_OK_TRADEFUL_NEGATIVE`.
Readable report: `reports/qa_gate/c001_block01_price_volatility_long_wide_20260604T144429Z_RU.md`.
Command: `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`, `Mode=long_only`, `CalibrationGridPreset=wide`, matrix `configs/calibration_matrices/catalog_blocks/catalog_block_01_price_volatility.yaml`, `ProcessWorkers=3`, `SearchWorkers=9`, `OptunaTrials=180`.
Result: launcher `OK`, workers `3/3`, best OOS `-37.0372%`, trades `9`.
Best wide params: `min_abs_ema_gap=0.05`, `period_standard=19`, `return_lookback=18`, `rolling_window=40`, `vol_z_window=180`.
Boundary: candidate is tradeful but negative, so production remains `NO_GO`; per cascade rule continue to `medium around best`, not blind medium.
Note: `w1/w2` point to the same search report timestamp with `contour_id=w2`; likely artifact name collision. Track before relying on per-worker report uniqueness.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T144630Z.json`.

## Instrument Knobs Audit TZ 2026-06-11T10:47:35Z
Status: `ACTIVE_READ_ONLY_AUDIT`.
Active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_INSTRUMENT_KNOBS_AUDIT_2026-06-11_RU.md`.
User clarified the next route: pause runtime calibration and perform a block-by-block audit of all tunable knobs for features, indicators, hypotheses, and blocks. The audit must identify calculation parameters, signal-level lines/thresholds, LONG/SHORT logic, defaults, current config coverage, actual code usage, and missing knobs.
Boundary: do not run `C001 medium`, Optuna/APTuna runtime, forward, or production actions during this audit.
Next: start `Block 01 price_volatility instrument knobs audit`, then proceed through Blocks 02-06 only after each block is fixed/agreed.

## Block 01 Price Volatility Knobs Audit 2026-06-11T10:51:00Z
Status: `BLOCK_01_AUDIT_DRAFT`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.
Block: `price_volatility` / `Цена и волатильность`.
Current conclusion: Block 01 currently calibrates calculation windows (`return_lookback`, `rolling_window`, `period_standard`). It does not yet have explicit signal-level thresholds for price move strength, candle range, volatility regime, or ATR risk regime.
Next: agree which Block 01 signal-level knobs should be added, then proceed to `Block 02 trend_momentum`.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T105438Z.json`.

## Block 01 Live Chart Example 2026-06-11T11:02:00Z
Status: `VISUAL_AUDIT_EXAMPLE`.
Artifacts: `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.png`, `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z_RU.md`, `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.json`.
Current fact: rendered Block 01 on real SOLUSDT 1m data using C001 wide calculation params. The chart demonstrates how `ret_1`, `rolling_std_20`, `atr14`, and `hl_spread` can map to concrete actions: `LONG_ALLOWED`, `SHORT_ALLOWED`, `NO_TRADE_LOW_VOL`, `NO_TRADE_HIGH_RISK`.
Boundary: thresholds are illustrative only; no config edits and no Optuna runtime were launched.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T113003Z.json`.

## Block 01 Short Rework Visual 2026-06-11T11:34:00Z
Status: `SHORT_REWORK_VISUAL_AUDIT`.
Artifacts: `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.png`, `reports/qa_gate/block01_short_rework_chart_20260611T113400Z_RU.md`, `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.json`.
Current fact: user pointed out that the chart visually looked like a long signal while the actual price context was short. The answer is to split Block 01 SHORT logic into `SHORT_MOMENTUM` and `SHORT_AFTER_PULLBACK`.
Proposed knobs: `ret_down_context_threshold`, `ret_pullback_up_threshold`, `ret_short_confirm_threshold`, `confirm_bars`, `vol_min/max`, `atr_min/max`, `hl_spread_max`.
Boundary: no code/config changes and no runtime launches yet.

## Block 01 Parameter Range Map 2026-06-11T11:48:00Z
Status: `PARAMETER_RANGE_MAP_DRAFT`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.
Current fact: added concrete min/max/step ranges for Block 01 windows, up/down context, pullback, confirmation bars, vol/ATR/HL-spread filters, and primary ATR target/risk.
Boundary: TZ draft only; no config/code changes and no runtime launches.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T120336Z.json`.

## New Chat Handoff 2026-06-19
Status: `NEW_CHAT_HANDOFF_READY`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/HANDOFF_TO_NEW_CHAT_2026-06-19_RU.md`.
Current fact: prepared a clean packet for a new chat because this thread is too large. It says to use only `docs/CALIBRATION_NODE_CURRENT` as active source of truth, avoid old chronology, keep runtime/config/code changes paused, and continue from Block 01 `PARAMETER_RANGE_MAP_DRAFT`.
Next: in new chat, read the handoff and decide whether to mark Block 01 `AGREED/READY_FOR_CODE` or refine it, then proceed to Block 02.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260619T184109Z.json`.

## F001 Strict Passport Runtime Connected 2026-06-22T09:13:32Z
Status: `F001_STRICT_PASSPORT_CONNECTED`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/passports/features/F001_ret_1_RU.md`.
Current fact: user-provided strict F001 passport was applied to calibration/runtime. `F001_move` and `F001_thr_pct` are now linked to `ret_1` in the full matrix, Block 01 catalog matrix, and H001 feature-sweep matrix. Runtime action `F001_RET1_ALLOW` is calculated from the last closed 1m candle and blocks entries in backtest when false.
Validation: `py_compile PASS`; focused tests `25/25 OK`; Optuna runtime tests `65/65 OK`; matrix compile check PASS; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T091458Z.json`.
Next: user decision to run F001/H001 or Block 01 with this passport, or move strictly to `F002 ret_3`.

## F001 Strict LONG 1d/1d Runtime 2026-06-22T09:20:20Z
Status: `F001_LONG_1D1D_DONE_GOAL_FAIL`.
Artifact: `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`.
Current fact: ran the strict F001 passport in `long_only` using H001 feature-sweep matrix on train `2026-05-31`, OOS `2026-06-01`. Before final result, fixed `oos_evaluate.py` so final OOS preserves `RUNTIME_ACTION_COLUMNS`; validation `84 tests OK`.
Best worker: `w1`; params `F001_move=1.0`, `F001_thr_pct=0.19`, `min_abs_ema_gap=0.02`.
OOS result: `net_return_pct=-5.352332468117016`, `trades=3`, `hit_rate=0.3333333333333333`, `max_drawdown_pct=-5.833320604926396`, `goal_pass=false`.
Gate proof: `F001_RET1_ALLOW_gate_active=true`, raw `525`, after LONG mode `281`, after F001 gate `4`, entries filled `3`.
Conclusion: F001 LONG works technically but is `NO_GO` on this 1d/1d window.

## F001 Strict LONG Trade Map 2026-06-22
Status: `F001_LONG_TRADE_MAP_READY`.
Artifact: `reports/qa_gate/f001_strict_long_1d1d_trade_map_20260622T092020Z.png`.
Current fact: generated a visual QA chart for the best F001 LONG OOS worker. It shows the full day, all 3 entries, signal bars, exits, TP `+1.20%`, and SL `-0.80%`.
Conclusion: all trades closed by `timeout`; no TP/SL hit.

## F001 Strict LONG No-Timeout Runtime 2026-06-22
Status: `F001_LONG_NO_TIMEOUT_DONE_NO_GO`.
Artifact: `reports/qa_gate/f001_strict_long_no_timeout_1d1d_20260622T093702Z_RU.md`.
Chart: `reports/qa_gate/f001_strict_long_no_timeout_trade_map_20260622T093702Z.png`.
Current fact: user asked to turn off timeout. Implemented explicit switch `-DisableTimeoutExit` in the APTuna process-pool launcher and `--disable-timeout-exit` in Python search/train/OOS entrypoints. Backtest now supports `timeout_exit_enabled=false`; if TP/SL do not hit, exit reason becomes `end_of_data`.
Validation: `py_compile PASS`; `tests.test_backtest_fields`, `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_optuna_search_runtime`: `78 tests OK`.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T094448Z.json`.
Runtime: reran F001 strict LONG on train `2026-05-31`, OOS `2026-06-01`, H001 matrix, wide grid, 180 trials, `TimeoutExit=off`; launcher `OK`, workers `3/3`.
Formal best: worker `w1`, `0.0%`, `0` trades.
Best tradeful: worker `w2/w3`, `-47.79331627195255%`, `6` trades, `5` SL exits and `1` `end_of_data`.
Conclusion: timeout is off technically, but F001 LONG remains `NO_GO`; without timeout, tradeful entries mostly hold until SL.

## F001 Exit Baseline Decision 2026-06-22
Status: `EXIT_BASELINE_TIMEOUT_ON`.
Current fact: user decided to keep active calibration exits as before for cleanliness: TP, SL, and timeout by `hold_bars`.
Boundary: no-timeout mode remains available but is diagnostic only; do not pass `-DisableTimeoutExit` in baseline F001/Block 01 runs.
Active comparison artifact: `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`.

## Action Passport Calibration Rule 2026-06-22
Status: `ACTION_PASSPORT_CALIBRATION_ACTIVE`.
Artifacts: `docs/CALIBRATION_NODE_CURRENT/TZ_ACTION_PASSPORT_CALIBRATION_2026-06-22_RU.md`, `configs/calibration_action_passports.yaml`, `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`.
Current fact: user corrected the architecture: old Optuna configs/proposals mixed feature, hypothesis, runtime, risk, and exit knobs, so they are not a clean baseline. New rule is passport-first: every action must have a passport and explicit calibration/backtest subpassport.
Legacy boundary: old `calibration_full_matrix`, `catalog_blocks`, and `feature_sweep` matrices remain in repo but are `legacy/frozen` for new baseline runs.
Code guard: `src/mlbotnav/optuna_space.py` now enforces `passport_mode.allowed_calibration_params` for matrices with `passport_mode.enabled=true`.
Active F001 matrix: `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`; allowed params only `F001_move`, `F001_thr_pct`.
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`: `13 tests OK`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; YAML parse PASS; compile PASS for F001 passport matrix in `long_only` and `short_only`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T101720Z.json`.
Next: use the F001 passport-action matrix for the next F001 baseline run, then create F002 passport before any F002 calibration. Exit/dynamic-exit must get separate passports before calibration.

## F001 Passport-Action LONG Runtime 2026-06-22
Status: `F001_PASSPORT_ACTION_LONG_DONE_NO_GO`.
Artifact: `reports/qa_gate/f001_passport_action_long_1d1d_20260622T101953Z_RU.md`.
Current fact: ran clean F001 passport-action matrix `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml` in `long_only`, train `2026-05-31`, OOS `2026-06-01`, wide, 180 trials, timeout exit on.
Launcher: `OK`, workers `3/3`.
Formal best: `w3`, `0.0%`, `0` trades, not a tradeful candidate.
Best tradeful: `w1`, `F001_thr_pct=0.28`, OOS `-5.1298471326372%`, `1` trade, exit `timeout`.
Other tradeful: `w2`, `F001_thr_pct=0.10`, OOS `-28.876033596834784%`, `8` trades.
Conclusion: passport path works technically; F001 LONG remains `NO_GO`.
Open cleanup: core runtime fields are still sampled by engine defaults (`horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`). Decide whether to create a runtime/backtest subpassport or rerun with fixed single-value grids before expanding.
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T102340Z.json`.

## Block Passport Registry 2026-06-22
Status: `BLOCK_PASSPORT_REGISTRY_CONNECTED`.
Artifact: `configs/calibration_action_passports.yaml`.
Current fact: user decided to keep one main config and add passports into that config by block. Registry now has `blocks.B001..B006` with Russian names and active/planned passport slots.
Active F001: `blocks.B001.active_passports.F001`; `B001` is `price_volatility` / `Цена и волатильность`.
Planned F002: `blocks.B001.planned_passports.F002`; legacy `h002_price_volatility_ret_3.yaml` is not a baseline.
Code guard: `src/mlbotnav/optuna_space.py` validates passport matrix against registry metadata (`registry_path`, `registry_block_id`, `registry_passport_id`, `action_id`, `allowed_calibration_params`, `active_matrix_path`).
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `79 tests OK`; env override compile PASS for F001 passport matrix.
Next: add launcher `PassportModeRequired`, OOS legacy-param guard, fixed/runtime subpassport for core grids, and report fingerprint fix before expanding.

## RET_N F001-F005 Strict Passport Family 2026-06-22
Status: `RET_N_F001_F005_PASSPORTS_CONNECTED`.
User file: `C:\Users\007\Downloads\RET_N_F001_F005_strict_passports.md`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/RET_N_F001_F005_strict_passports.md`.
Current fact: B001 now has active passports F001-F005 in `configs/calibration_action_passports.yaml`; F002-F005 are no longer merely planned.
Active matrices:
1. `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`
2. `configs/calibration_matrices/passport_actions/F002_ret3_entry_filter.yaml`
3. `configs/calibration_matrices/passport_actions/F003_ret6_entry_filter.yaml`
4. `configs/calibration_matrices/passport_actions/F004_ret12_entry_filter.yaml`
5. `configs/calibration_matrices/passport_actions/F005_ret24_entry_filter.yaml`
Runtime: `dataset.py` emits F002-F005 action columns only when their own params are present, preventing accidental old-run filtering. `backtest.py` gates entries by all present `ENTRY_ACTION_ALLOW` columns and exposes `entry_action_gate_columns`.
Validation: `py_compile PASS`; focused tests `96/96 OK`; F001-F005 compile PASS; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T112135Z.json`.
Max-anchor fix: `src/mlbotnav/optuna_space.py` now preserves `max` when `step` does not land on it exactly; F003 `F003_thr_pct` compiles to `60` values and includes `1.20`. Follow-up validation: `py_compile PASS`; focused tests `98/98 OK`; F003 proof `60 0.03 [1.17, 1.19, 1.2] True`.
Next: run the next strict passport calibration by list order, likely F002 first.

## B001 RET_N Ladder Tournament 2026-06-22
Status: `B001_RET_N_LADDER_READY_SMOKE_OK`.
Current fact: user chose the ladder/tournament route for the one B001 block with five RET_N passports. Implemented `B001_RET_N_TOURNAMENT` in `configs/calibration_action_passports.yaml`.
Generator: `src/mlbotnav/b001_ret_n_ladder_tournament.py`; it creates all `31` non-empty combinations and compiles each matrix.
Runner: `APTuna/run_b001_ret_n_ladder_tournament.ps1`; it can run selected combos through existing APTuna process-pool and write a tournament JSON/MD.
Manifest artifact: `reports/qa_gate/b001_ret_n_ladder_matrices_20260622T115638Z/manifest.json`.
DryRun artifact: `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115811Z.json`.
Smoke artifact: `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115930Z.json`.
Smoke result: one LONG combo `B001_RET_N_F001`, tiny budget `6` trials, process-pool exit `0`, `best_oos` extracted. It had `0` OOS trades and is not a candidate; purpose was runner validation only.
Validation: `py_compile PASS`; focused tests `35/35 OK`; extended focused tests with Optuna runtime `83/83 OK`.
Full LONG command:
```powershell
powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock
```

## B001 Solo Selection Decision 2026-06-22
Status: `B001_RET_N_SOLO_SELECTION_ONLY`.
Current fact: full 31-combo LONG run completed at `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T120806Z.json`; `31/31 ok`, but `28/31` zero OOS trades. Best combo `F002+F004` had only `1` trade, `+0.7845424236948562%` at `10x`, timeout exit, no TP hit, so `NO_CANDIDATE`.
Decision: do not use expanded in-block combination tournament as baseline. B001 baseline now means solo selection only: F001, F002, F003, F004, F005 separately, promote at most one best solo feature if tradeful/non-negative.
Runner guard: `APTuna/run_b001_ret_n_ladder_tournament.ps1` defaults to `EndIndex=5`; `EndIndex > 5` is blocked unless `-EnableCombinationTournament` is passed. Combination mode is diagnostic-only.
Validation: default dry-run selected `5` solo rows; `EndIndex=31` blocked without diagnostic flag; `py_compile PASS`; focused tests `35/35 OK`.

## MACD F013-F015 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/macd_f013_f015_long_short_audit_20260622T151954Z_RU.md`.
Current fact: added B007 `MACD импульс` with F013 `macd_line_1m`, F014 `macd_signal_1m`, F015 `macd_hist_1m`; each is a separate solo `ENTRY_FILTER` passport.
Important fix: before accepting results, fixed Optuna study contamination by adding `space_signature` into `run_signature`. Old pre-fix MACD runs reused stale trials from other passport matrices and were discarded.
Clean LONG/SHORT result:
1. F013 LONG `0.000000%`, trades `0`; F013 SHORT `-18.625751%`, trades `6`.
2. F014 LONG `-2.977908%`, trades `3`; F014 SHORT `-20.546537%`, trades `6`.
3. F015 LONG `-4.992098%`, trades `1`; F015 SHORT `-5.883887%`, trades `1`.
All tradeful exits were `timeout`, wins `0`; final `NO_GO`.
Validation: `py_compile PASS`; focused tests `112/112 OK`; YAML parse PASS; matrix compile PASS; selected params isolation PASS; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T152122Z.json`.

## F016 ADX14 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/f016_adx14_long_short_audit_20260622T153403Z_RU.md`.
Current fact: added B008 `ADX14 сила тренда` with F016 `adx14_1m`; action params are only `F016_cmp` and `F016_level`; output is `F016_ADX14_ALLOW`.
Clean LONG/SHORT result:
1. F016 LONG selected `LESS level=41`, OOS `-13.43232421418481%`, trades `3`, wins/losses `0/3`, exits `timeout=3`.
2. F016 SHORT selected `LESS level=28`, OOS `-28.526707456698695%`, trades `13`, wins/losses `1/12`, exits `timeout=13`.
Gate fact: final OOS reports show `entry_action_gate_active=true` and `entry_action_gate_columns=['F016_ADX14_ALLOW']`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `114/114 OK`; YAML parse PASS; matrix compile PASS for `long_only` and `short_only`.

## STOCH F017-F018 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/stoch_f017_f018_long_short_audit_20260622T154340Z_RU.md`.
Current fact: added B009 `Stochastic 14 K/D` with combined F017_F018 `stochastic_14_1m`; output is `F017_F018_STOCH14_ALLOW`.
Clean LONG/SHORT result:
1. F017_F018 LONG effective params `LEVEL K LESS level=72`, OOS `-84.05333161848922%`, trades `51`, wins/losses `2/49`, exits `timeout=50`, `sl=1`.
2. F017_F018 SHORT effective params `KD_CROSS UP LOW low=40 high=60 gap=0`, OOS `-17.53680624691214%`, trades `6`, wins/losses `0/6`, exits `timeout=6`.
Gate fact: final OOS reports show `entry_action_gate_active=true` and `entry_action_gate_columns=['F017_F018_STOCH14_ALLOW']`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `116/116 OK`; YAML parse PASS; matrix compile PASS for `long_only` and `short_only`.

## VOLUME F019-F021 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/volume_f019_f021_long_short_audit_20260622T160207Z_RU.md`.
Current fact: added B010 `Объем и поток` with F019 `vol_chg_1m`, F020 `vol_z_20_1m`, F021 `delta_volume_1m`; baseline selection remains solo feature only.
Fix applied: F021 `TRUE_DELTA` now requires `buy_volume`/`sell_volume`; absent side-volume columns produce no signal instead of falling back to proxy. Pre-fix F021 runs were discarded.
Clean LONG/SHORT result:
1. F019 LONG `UP thr=105%`, OOS `-57.151405%`, trades `26`; F019 SHORT `DOWN thr=10%`, OOS `-11.835584%`, trades `4`.
2. F020 LONG `HIGH z=3.6`, OOS `0%`, trades `0`; F020 SHORT `HIGH z=0.5`, OOS `-25.290896%`, trades `9`.
3. F021 LONG `PROXY_DELTA SELL thr=50%`, OOS `-77.699906%`, trades `37`; F021 SHORT `TRUE_DELTA BUY thr=5%`, OOS `0%`, trades `0`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `118/118 OK`; YAML parse PASS; matrix compile PASS for all F019-F021.

## F022 OBV Slope 5 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/f022_obv_slope5_long_short_audit_20260622T162356Z_RU.md`.
Current fact: added B011 `OBV slope 5` with solo passport F022 `obv_slope_5_1m`; output is `F022_OBVSLOPE5_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F022_obv_slope5_1m_entry_filter.yaml`.
Runtime/backtest: dataset computes F022 by passport formula `(OBV - OBV.shift(5)) / SMA(volume,20)` and backtest gates entries by the present `F022_OBVSLOPE5_ALLOW` column.
Clean LONG/SHORT result:
1. F022 LONG `UP thr=7.2`, OOS `0.000000%`, trades `0`.
2. F022 SHORT `DOWN thr=8.2`, OOS `-17.479067%`, trades `3`, wins/losses `0/3`, exits `timeout=2`, `sl=1`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `120/120 OK`; matrix compile PASS for LONG/SHORT; launcher post-audit `text_guard PASS`.

## F023 MFI14 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/f023_mfi14_long_short_audit_20260622T163809Z_RU.md`.
Current fact: added B012 `MFI14` with combined solo passport F023 `mfi14_1m`; output is `F023_MFI14_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F023_mfi14_1m_combined_entry_filter.yaml`.
Runtime/backtest: dataset computes F023 LEVEL/CROSS_LEVEL over MFI14 and backtest gates entries by the present `F023_MFI14_ALLOW` column.
Clean LONG/SHORT result:
1. F023 LONG `LEVEL GREATER level=88`, OOS `-4.474397%`, trades `1`, wins/losses `0/1`, exits `timeout=1`.
2. F023 SHORT `LEVEL LESS level=81`, OOS `-20.546537%`, trades `6`, wins/losses `0/6`, exits `timeout=6`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `122/122 OK`; matrix compile PASS for LONG/SHORT; launcher post-audit `text_guard PASS`.

## DENSITY/VPOC Block A F025/F029/F033/F034 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/density_vpoc_block_a_f025_f029_f033_f034_audit_20260622T165812Z_RU.md`.
Current fact: user supplied `DENSITY_VPOC_F025_F034_3BLOCK_FIXED_COMMENTS.md`; per passport rule, only Block A `VPOC_CORE` was run now.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/DENSITY_VPOC_F025_F034_3BLOCK_FIXED_COMMENTS.md`.
Registry: `configs/calibration_action_passports.yaml`, `B013`.
Active Block A matrices: `F025_vpocdist60_entry_filter.yaml`, `F029_vpocdist240_entry_filter.yaml`, `F033_vpocdrift20_entry_filter.yaml`, `F034_clusterratio_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F025 LONG `-60.069331%/20 trades`; F025 SHORT `-6.778638%/3 trades`.
2. F029 LONG `0.000000%/0 trades`; F029 SHORT `-18.625751%/6 trades`.
3. F033 LONG `-14.115533%/4 trades`; F033 SHORT `-3.624721%/1 trade`.
4. F034 LONG `0.000000%/0 trades`; F034 SHORT `-10.692022%/3 trades`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F033 SHORT but still negative.
Validation: `py_compile PASS`; focused tests `124/124 OK`; matrix compile PASS for Block A LONG/SHORT; launcher post-audit `text_guard PASS`.
Next from this passport file: Block B `ZONE_DENSITY` (`F026`, `F027`, `F030`, `F031`), then Block C `VPOC_STRENGTH` (`F028`, `F032`).

## LEVEL/RANGE/CHANNEL Block A F035/F036/F037 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/level_range_channel_block_a_f035_f036_f037_audit_20260622T171500Z_RU.md`.
Current fact: user supplied `LEVEL_RANGE_CHANNEL_F035_F039_strict_passport.md`; per passport order, only Block A `LEVEL_A` was run now.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/LEVEL_RANGE_CHANNEL_F035_F039_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B014`.
Active Block A matrices: `F035_supportdist_entry_filter.yaml`, `F036_resdist_entry_filter.yaml`, `F037_levelstrength_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F035 LONG `-6.153364%/2 trades`; F035 SHORT `-18.625751%/6 trades`.
2. F036 LONG `-12.920893%/3 trades`; F036 SHORT `-13.301553%/4 trades`.
3. F037 LONG `0.000000%/0 trades`; F037 SHORT `-18.104190%/7 trades`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F035 LONG but still negative.
Validation: `py_compile PASS`; focused tests `126/126 OK`; matrix compile PASS for Block A LONG/SHORT; launcher post-audit `text_guard PASS`.
Next from this passport file: Block B `F038 position_in_range_1m`, then Block C `F039 trend_channel_pos_1m`.

## FIBONACCI_GRID F040/F041 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/fibonacci_grid_f040_f041_long_short_audit_20260622T173112Z_RU.md`.
Current fact: user supplied `FIBONACCI_F040_F041_anchor_grid_strict_passport_v3.md`; implemented B015 with confirmed pivot fib grid and solo action gates.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/FIBONACCI_F040_F041_anchor_grid_strict_passport_v3.md`.
Registry: `configs/calibration_action_passports.yaml`, `B015`.
Matrices: `F040_fib0382dist_entry_filter.yaml`, `F041_fib0618dist_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F040 LONG `0.000000%/0 trades`; F040 SHORT `-27.970937%/9 trades`.
2. F041 LONG `0.000000%/0 trades`; F041 SHORT `-9.615680%/4 trades`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F041 SHORT but still negative.
Validation: `py_compile PASS`; focused tests `128/128 OK`; matrix compile PASS for F040/F041 LONG/SHORT.

## ENTRY_QUALITY_CONTEXT F042-F044 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/entry_quality_context_f042_f044_long_short_audit_20260622T175033Z_RU.md`.
Current fact: user supplied `ENTRY_QUALITY_CONTEXT_F042_F044_strict_passport_v2.md`; implemented B016 with F042 `tp_context_distance_1m`, F043 `sl_context_distance_1m`, and F044 `rr_context_estimate_1m`.
Runtime/backtest: dataset emits canonical action columns plus side-aware `*_LONG`/`*_SHORT`; backtest reports canonical gate columns and applies side-specific gates by actual signal side.
Clean LONG/SHORT result:
1. F044 LONG `-1.145944%/1 trade`; F044 SHORT `-19.784205%/8 trades`.
2. F042 LONG `-17.392676%/3 trades`; F042 SHORT `0.000000%/0 trades`.
3. F043 LONG `0.000000%/0 trades`; F043 SHORT `-30.313954%/10 trades`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `130/130 OK`; matrix compile PASS for F042/F043/F044 LONG/SHORT; launcher/text_guard PASS.

## BREAKOUT_RETEST F045-F049 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b017_breakout_retest_f045_f049_audit_20260622T181600Z.md`.
Current fact: user supplied `BREAKOUT_RETEST_F045_F049_strict_passport.md`; implemented B017 `BREAKOUT_RETEST пробой/ретест`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/BREAKOUT_RETEST_F045_F049_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B017`.
Matrices: `F048_swinghighbreak_entry_filter.yaml`, `F049_swinglowbreak_entry_filter.yaml`, `F045_breakout_entry_filter.yaml`, `F047_retest_entry_filter.yaml`, `F046_falsebreak_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F048 LONG `0.000000%/0 trades`; F048 SHORT `0.000000%/0 trades`.
2. F049 LONG `-12.862590%/6 trades`; F049 SHORT `-20.254568%/4 trades`.
3. F045 LONG `0.000000%/0 trades`; F045 SHORT `-3.482265%/2 trades`.
4. F047 LONG `-11.000000%/1 trade`; F047 SHORT `-12.464525%/3 trades`.
5. F046 LONG `0.000000%/0 trades`; F046 SHORT `-5.366391%/1 trade`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F045 SHORT but still negative.
Validation: `py_compile PASS`; focused B017 tests `3/3 OK`; matrix compile PASS for F045-F049 LONG/SHORT; launcher/text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T181926Z.json`.

## MARKET_STRUCTURE F050-F052 Passport Run 2026-06-22
Status: `done / positive_test_candidate`.
Artifact: `reports/qa_gate/b018_market_structure_f050_f052_audit_20260622T183500Z.md`.
Current fact: user supplied `MARKET_STRUCTURE_F050_F052_strict_passport.md`; implemented B018 `MARKET_STRUCTURE BOS/CHOCH`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/MARKET_STRUCTURE_F050_F052_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B018`.
Matrices: `F050_bosup_entry_filter.yaml`, `F051_bosdown_entry_filter.yaml`, `F052_choch_entry_filter.yaml`.
Clean LONG/SHORT result:
1. F050 LONG `0.000000%/0 trades`; F050 SHORT `0.000000%/0 trades`.
2. F051 LONG `0.000000%/0 trades`; F051 SHORT `+2.810523%/1 trade`, `goal_pass`.
3. F052 LONG `0.000000%/0 trades`; F052 SHORT `0.000000%/0 trades`.
Final status: `POSITIVE_TEST_CANDIDATE`; F051 SHORT params `INTERNAL`, `break_buffer_pct=0.07`, `confirm_bars=2`, `require_bias=NOT_BULLISH`. Needs follow-up validation because OOS has only one trade.
Validation: `py_compile PASS`; focused B018 tests `3/3 OK`; matrix compile PASS for F050-F052 LONG/SHORT.

## CANDLE_PATTERNS F053-F060 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b019_candle_patterns_f053_f060_audit_20260622T190530Z.md`.
Current fact: user supplied `CANDLE_PATTERNS_F053_F060_strict_passport.md`; implemented B019 `CANDLE_PATTERNS свечные паттерны`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/CANDLE_PATTERNS_F053_F060_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B019`.
Matrices: `F055_pinbull_entry_filter.yaml`, `F056_pinbear_entry_filter.yaml`, `F059_engulfbull_entry_filter.yaml`, `F060_engulfbear_entry_filter.yaml`, `F057_hammer_entry_filter.yaml`, `F058_shootingstar_entry_filter.yaml`, `F054_insidebar_entry_filter.yaml`, `F053_doji_entry_filter.yaml`.
Clean result: F055 LONG/SHORT `0%/0`; F056 LONG/SHORT `0%/0`; F059 LONG `-60.087983%/22`, SHORT `0%/0`; F060 LONG/SHORT `0%/0`; F057 LONG/SHORT `0%/0`; F058 LONG/SHORT `0%/0`; F054 LONG `0%/0`, SHORT `-8.438667%/2`; F053 LONG `-11.213252%/3`, SHORT `0%/0`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B019 tests `3/3 OK`; matrix compile PASS for F053-F060 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T190822Z.json`.

## DIVERGENCE_PATTERNS F061-F066 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b020_divergence_patterns_f061_f066_audit_20260622T193300Z.md`.
Current fact: user supplied `DIVERGENCE_PATTERNS_F061_F066_strict_passport.md`; implemented B020 `DIVERGENCE_PATTERNS дивергенции`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/DIVERGENCE_PATTERNS_F061_F066_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B020`.
Matrices: `F061_rsibulldiv_entry_filter.yaml`, `F062_rsibeardiv_entry_filter.yaml`, `F063_macdbulldiv_entry_filter.yaml`, `F064_macdbeardiv_entry_filter.yaml`, `F065_obvbulldiv_entry_filter.yaml`, `F066_obvbeardiv_entry_filter.yaml`.
Clean result: F061 LONG `-7.123789%/2`, SHORT `0%/0`; F062 LONG/SHORT `0%/0`; F063 LONG `-37.837211%/12`, SHORT `0%/0`; F064 LONG/SHORT `0%/0`; F065 LONG `-10.822526%/4`, SHORT `0%/0`; F066 LONG/SHORT `0%/0`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B020 tests `3/3 OK`; matrix compile PASS for F061-F066 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T193442Z.json`.

## PATTERN_QUALITY F067-F068 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b021_pattern_quality_f067_f068_audit_20260622T194700Z.md`.
Current fact: user supplied `PATTERN_QUALITY_F067_F068_strict_passport.md`; implemented B021 `PATTERN_QUALITY качество паттерна`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_QUALITY_F067_F068_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B021`.
Matrices: `F067_patternstrength_entry_filter.yaml`, `F068_patternage_entry_filter.yaml`.
Clean result: F067 LONG `0%/0`, F067 SHORT `-18.202040%/6`; F068 LONG `-6.153364%/2`, F068 SHORT `-59.898861%/26`.
Final status: `NO_GO`; no candidate promoted. Best non-negative result was F067 LONG with zero OOS trades.
Validation: `py_compile PASS`; focused B021 tests `3/3 OK`; matrix compile PASS for F067/F068 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T194938Z.json`.

## CHART_PATTERNS F069-F077 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b022_chart_patterns_f069_f077_audit_20260622T202100Z.md`.
Current fact: user supplied `CHART_PATTERNS_F069_F077_strict_passport.md`; implemented B022 `CHART_PATTERNS графические паттерны`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/CHART_PATTERNS_F069_F077_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B022`.
Matrices: `F077_rangeflag_entry_filter.yaml`, `F073_triangle_entry_filter.yaml`, `F074_pennant_entry_filter.yaml`, `F075_wedgerising_entry_filter.yaml`, `F076_wedgefalling_entry_filter.yaml`, `F069_doublebottom_entry_filter.yaml`, `F070_doubletop_entry_filter.yaml`, `F071_headshoulders_entry_filter.yaml`, `F072_invheadshoulders_entry_filter.yaml`.
Clean result: F077 LONG `-19.434440%/7`, SHORT `-17.890148%/3`; F073/F074/F075/F076/F071 zero-trade on both sides; F069 LONG `-49.737441%/21`, SHORT `-13.225011%/3`; F070 LONG `0%/0`, SHORT `-21.410449%/7`; F072 LONG `-6.837599%/1`, SHORT `-10.765093%/3`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F072 LONG but still negative.
Validation: `py_compile PASS`; focused B022 tests `3/3 OK`; matrix compile PASS for F069-F077 LONG/SHORT; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T202309Z.json`.

## PATTERN_CONFIRMATION F078-F079 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b023_pattern_confirmation_f078_f079_audit_20260622T203700Z.md`.
Current fact: user supplied `PATTERN_CONFIRMATION_F078_F079_strict_passport(1).md`; implemented B023 `PATTERN_CONFIRMATION confirmation of existing pattern_event`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_CONFIRMATION_F078_F079_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B023`.
Matrices: `F079_patternlevelconf_entry_filter.yaml`, `F078_patternvolconf_entry_filter.yaml`.
Clean result: F079 LONG `0%/0`, F079 SHORT `0%/0`; F078 LONG `-27.682109%/7`; F078 SHORT `-7.323394%/4`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F078 SHORT but still negative.
Validation: `py_compile PASS`; focused B023 tests `3/3 OK`; matrix compile PASS for F079/F078 LONG/SHORT; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T204015Z.json`.

## PATTERN_COMPOSITE_ENTRY F080-F081 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b024_pattern_composite_entry_f080_f081_audit_20260622T205500Z.md`.
Current fact: user supplied `PATTERN_COMPOSITE_ENTRY_F080_F081_strict_passport.md`; implemented B024 `PATTERN_COMPOSITE_ENTRY kompozitnyy pattern entry`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_COMPOSITE_ENTRY_F080_F081_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B024`.
Matrices: `F080_patternlong_entry_filter.yaml`, `F081_patternshort_entry_filter.yaml`.
Runtime/backtest: dataset emits `F080_PATTERNLONG_ALLOW` and `F081_PATTERNSHORT_ALLOW`; backtest treats F080 as LONG-only and F081 as SHORT-only if both columns are present.
Clean result: F080 LONG `0%/0`; F081 SHORT `-5.359455%/1`, exit `timeout=1`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B024 tests `3/3 OK`; matrix compile PASS; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T210111Z.json`.

## PATTERN_TRADE_CONTEXT F082-F083 Passport Run 2026-06-22
Status: `done / no_go`.
Artifact: `reports/qa_gate/b025_pattern_trade_context_f082_f083_audit_20260622T211600Z.md`.
Current fact: user supplied `PATTERN_TRADE_CONTEXT_F082_F083_strict_passport.md`; implemented B025 `PATTERN_TRADE_CONTEXT SL/TP context`.
Project passport: `docs/CALIBRATION_NODE_CURRENT/passports/features/PATTERN_TRADE_CONTEXT_F082_F083_strict_passport.md`.
Registry: `configs/calibration_action_passports.yaml`, `B025`.
Matrices: `F082_patternslbuf_entry_filter.yaml`, `F083_patterntpladder_entry_filter.yaml`.
Runtime/backtest: dataset emits side-aware gates `F082_PATTERNSLBUF_ALLOW_LONG/SHORT` and `F083_PATTERNTPLADDER_ALLOW_LONG/SHORT`; backtest applies side-aware action columns when present.
Clean result: F082 LONG `0%/0`; F082 SHORT `-25.094610%/7`; F083 LONG `-35.921536%/12`; F083 SHORT `-70.280106%/35`.
Final status: `NO_GO`; no candidate promoted because only non-negative run has zero trades and all tradeful runs are negative.
Validation: `py_compile PASS`; focused B025 tests `3/3 OK`; matrix compile/passport allowlist PASS; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T211551Z.json`.

## F001-F083 Passport Route Full Audit 2026-06-23
Status: `WARN_WITH_COMPLETENESS_GAPS`.
Artifact: `reports/qa_gate/f001_f083_passport_full_audit_20260623.md`.
Existing executable passport matrices are clean and isolated: `73` active/combined entries compile x `long_only/short_only` = `146` spaces, no legacy params outside allowlists.
Completeness gaps in the pre-F024 audit snapshot: F024 was open then and is closed below; `F026/F027/F028/F030/F031/F032/F038/F039` planned only; `F017/F018` combined as `F017_F018`.
Runtime/backtest warning: normal passport flow is isolated, but stale pre-existing `F*_ALLOW` columns in a DataFrame would be applied by global backtest gate discovery.
Next: close planned passports, decide F017/F018 split vs combined, and harden active action-column selection.

## F024 VWAP Distance Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f024_vwap_distance_long_short_audit_20260623T055200Z.md`.
Current fact: implemented previously open `F024` as standalone late-closure block `B026/F024`, action `F024_VWAPDIST_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F024_vwapdist_entry_filter.yaml`.
Runtime/backtest: dataset emits `F024_VWAPDIST_ALLOW` from previous closed-bar VWAP distance; backtest gate columns in both OOS reports are exactly `['F024_VWAPDIST_ALLOW']`.
Clean result: LONG `-17.894975%/8`, SHORT `0%/0`; final `NO_GO`, but the F024 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed in order to planned Density/VPOC gaps `F026/F027/F028/F030/F031/F032`, then `F038/F039`, then decide/split `F017/F018`, plus stale-action-column hardening.

## F026 Density Bin Share 60 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f026_binshare60_long_short_audit_20260623T060100Z.md`.
Current fact: implemented `B013/F026`, action `F026_BINSHARE60_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F026_binshare60_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F026_BINSHARE60_ALLOW']`.
Clean result: LONG `-1.145944%/1`, SHORT `-24.712835%/9`; final `NO_GO`, but the F026 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F027 density_cluster_share_60_1m`.

## F027 Density Cluster Share 60 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f027_clustershare60_long_short_audit_20260623T062300Z.md`.
Current fact: implemented `B013/F027`, action `F027_CLUSTERSHARE60_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F027_clustershare60_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F027_CLUSTERSHARE60_ALLOW']`.
Clean result: LONG `-6.153364%/2`, SHORT `-18.625751%/6`; final `NO_GO`, but the F027 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F028 density_vpoc_share_60_1m`.

## F028 Density VPOC Share 60 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f028_vpocshare60_long_short_audit_20260623T064000Z.md`.
Current fact: implemented `B013/F028`, action `F028_VPOCSHARE60_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F028_vpocshare60_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F028_VPOCSHARE60_ALLOW']`.
Clean result: LONG `-1.145944%/1`, SHORT `-18.625751%/6`; final `NO_GO`, but the F028 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F030 density_bin_share_240_1m`.

## F030 Density Bin Share 240 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f030_binshare240_long_short_audit_20260623T070000Z.md`.
Current fact: implemented `B013/F030`, action `F030_BINSHARE240_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F030_binshare240_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F030_BINSHARE240_ALLOW']`.
Clean result: LONG `-13.432324%/3`, selected `LESS` with `share_thr_pct=4.0`; SHORT `-24.712835%/9`, selected `LESS` with `share_thr_pct=19.0`; final `NO_GO`, but the F030 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F031 density_cluster_share_240_1m`.

## F031 Density Cluster Share 240 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f031_clustershare240_long_short_audit_20260623T071000Z.md`.
Current fact: implemented `B013/F031`, action `F031_CLUSTERSHARE240_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F031_clustershare240_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F031_CLUSTERSHARE240_ALLOW']`.
Clean result: LONG `-6.153364%/2`, selected `LESS` with `share_thr_pct=27.0`; SHORT `-55.142239%/26`, selected `LESS` with `share_thr_pct=40.0`; final `NO_GO`, but the F031 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F032 density_vpoc_share_240_1m`.

## F032 Density VPOC Share 240 Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f032_vpocshare240_long_short_audit_20260623T072500Z.md`.
Current fact: implemented `B013/F032`, action `F032_VPOCSHARE240_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F032_vpocshare240_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F032_VPOCSHARE240_ALLOW']`.
Clean result: LONG `-6.153364%/2`, selected `LESS` with `share_thr_pct=20.5`; SHORT `-18.625751%/6`, selected `LESS` with `share_thr_pct=15.5`; final `NO_GO`, but the F032 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F038 position_in_range_1m`.

## F038 Position In Range Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f038_rangepose_long_short_audit_20260623T074000Z.md`.
Current fact: implemented `B014/F038`, action `F038_RANGEPOSE_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F038_rangepose_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F038_RANGEPOSE_ALLOW']`.
Clean result: LONG `-13.432324%/3`, selected `LOW` with `level=70.0`; SHORT `-4.489987%/1`, selected `HIGH` with `level=56.0`; final `NO_GO`, but the F038 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: proceed to `F039 trend_channel_pos_1m`.

## F039 Trend Channel Position Gap Closure 2026-06-23
Status: `done / no_go`.
Artifact: `reports/qa_gate/f039_channelpos_long_short_audit_20260623T080500Z.md`.
Current fact: implemented `B014/F039`, action `F039_CHANNELPOS_ALLOW`, matrix `configs/calibration_matrices/passport_actions/F039_channelpos_entry_filter.yaml`.
Runtime/backtest: OOS gate columns in both reports are exactly `['F039_CHANNELPOS_ALLOW']`.
Clean result: LONG `-17.392676%/3`, selected `LOWER` with `level=40.0`, `outside_thr=45.0`; SHORT `0.000000%/0`, selected `UPPER` with `level=85.0`, `outside_thr=0.0`; final `NO_GO`, but the F039 coverage gap is closed.
Validation: py_compile PASS; focused unittest `3/3 OK`; matrix compile PASS for `long_only`/`short_only`; launcher ledger/text_guard PASS.
Next: planned gaps are closed; remaining decisions are `F017/F018` combined-vs-split and stale action-column hardening.
## ML Trade Dataset Stage 2.2 Passport Context 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive passport context columns before CSV write: `block_id`, `passport_id`, `action_id`, `calibration_params_json`, `entry_action_gate_columns`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Boundary: this is not full ML-ready CSV yet; trade identity starts at `2.3`, then duration/hit labels/MAE-MFE follow.

Next strict step: `2.3 Добавить trade identity`.
## ML Trade Dataset Stage 2.3 Trade Identity 2026-06-23
Status: `done / closed_pass`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.

Current fact: pipeline and OOS trade CSV outputs now receive stable trade identity columns before CSV write: `trade_id`, `entry_signal_time_utc`.

Implementation: `src/mlbotnav/ml_trade_dataset_enrichment.py`, `src/mlbotnav/pipeline_train_eval.py`, `src/mlbotnav/oos_evaluate.py`.

Boundary: this is not full ML-ready CSV yet; duration labels start at `2.4`, then hit labels/MAE-MFE follow.

Next strict step: `2.4 Добавить duration labels`.

## B001 Single-Worker Fast Finish 2026-06-24
Status: `diagnosed / not_worker_failure`.
Artifact: `reports/qa_gate/b001_single_worker_fast_finish_audit_20260624T180000Z_RU.md`.

Checked latest run `reports/logs/optuna_pool_long_only_20260624T175647Z_w1.log`.
The single-worker profile was applied correctly: `max_threads=9`, `search_workers=9`, `workers_used=9`, `n_trials_override=42`.

The run finished in `00:00:23` because B001 family-unified strict `5/5` leaves no candles after entry-action gate. Best candidate: `EMPTY_ACTION_GATE`, `0` trades, `signal_count_after_entry_action_gates=0`.

Next: keep single-worker `1x9/9`, generate/run B001 family-unified `4/5` 1д/1д; if empty, try `3/5`. Do not promote anything to ML.

## Optuna Worker Profile Correction 2026-06-24
Status: `profile_rule_corrected`.
Artifact: `reports/qa_gate/optuna_1x9_vs_3x3_worker_audit_20260624T183000Z_RU.md`.

Important correction: `1x9/9` is not physically equivalent to the old `3x3/9` mode. Old mode starts three Python processes, each with `--max-threads 3`, `--search-workers 3`; new single-worker mode starts one Python process with `--max-threads 9`, `--search-workers 9`.

For real B001 diagnostics, use `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`. Keep `1x9/9` only when one Optuna history is explicitly needed.
## Visual Entry Signal-Entry Contract v2 2026-06-25
Статус: `dev_signal_entry_contract_ready_needs_user_visual_confirm`.

Старый `v1` manual entries помечен как `SUPERSEDED_BY_V2_SIGNAL_ENTRY_CONTRACT`; он не должен быть целью для новых scorer/runner.

Новый v2-контракт: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/manual_entries.json`.

Правило: `signal_candle_time_utc` = закрытая свеча с фитилем/дном, `target_entry_time_utc` = open следующей свечи. LONG execution price: `entry_open_price * (1 + slippage_bps / 10000)`, сейчас `slippage_bps=5`.

PNG для согласования:
1. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_overlay_2026-05-12_20260625T102817Z.png`;
2. `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_zoom_panels_20260625T102849Z.png`.

Времена v2: `01:43 -> 01:44`, `04:15 -> 04:16`, `09:15 -> 09:16`, `12:34 -> 12:35`, `15:29 -> 15:30`, `16:59 -> 17:00`.

Следующий шаг: пользователь визуально подтверждает или правит v2-точки; после этого заново гонять scorer/solo/combo уже по v2.

## Visual Entry Instrument Stack Audit 2026-06-25
Статус: `dev_audit_ready_next_noise_suppression_runner`.
Аудит: `reports/final_review/visual_entry_v3/instrument_stack_audit/visual_entry_instrument_stack_audit_20260625_RU.md`.

Решение: не расширять сразу Optuna/ML. `DQ01/DQ03` оставить как high-recall карту дна (`DQ01 10/11 + 73 false`, `DQ03 11/11 + 95 false`) и следующим шагом сделать diagnostic runner `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`.

Следующий runner должен взять manual v3 и результаты `DQ01/DQ03`, посчитать паспортные голоса для manual hit и false-entry, протестировать роли context/trigger/confirm/suppress, сгруппировать сигналы в кластеры падение -> дно -> reclaim, выбрать максимум один вход на кластер и отрендерить PNG с входами.

Первый круг признаков: `F035/F038/F009/F010/F012/F017_F018/F023/F020/F055/F057/F059`. Второй круг: `F024/F025/F028/F032/F040/F041`. Третий круг: `F050/F052/F061/F063/F065`. Четвертый круг: `F069/F072/F076/F077/F078/F079/F080`, только после проверки no-lookahead для `pattern_event`.

## Visual Entry Noise Suppression Runner 2026-06-25
Статус: `dev_runner_done_no_ml`.

Добавлено:
1. `src/mlbotnav/visual_entry_noise_suppression_cluster_priority_runner.py`;
2. `tests/test_visual_entry_noise_suppression_cluster_priority_runner.py`.

DEV-прогон:
```powershell
$env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m mlbotnav.visual_entry_noise_suppression_cluster_priority_runner --manual-entries reports\manual_entries\SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows\manual_entries.json --out-dir reports\final_review\visual_entry_v3\noise_suppression_cluster_priority --render-top 8
```

Лучший результат `CP01_DQ01_CLUSTER10_SCORE12`: `9/11`, `28` false, `37` entries, precision `0.2432`, recall `0.8182`, f1 `0.3750`. Пропущены `08:26` и `17:00`.

Главный PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp01_dq01_cluster10_score12_20260625T150100Z.png`.

Проверки: py_compile PASS; новый unittest `2/2 OK`; вместе с deep runner `3/3 OK`; render test `1/1 OK`; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260625T150159Z.json`; процесс-хвостов не осталось.

Следующий шаг: не ML. Добрать `08:26` и `17:00` отдельным мягким подслоем cluster priority, не возвращаясь к шуму `DQ01/DQ03`.

## Visual Entry CP06 Recover 2026-06-25
Статус: `dev_recover_done_11_of_11_no_ml`.

`CP06_CP01_RECOVER_NOWICK_LATE_RETEST` добавлен в `src/mlbotnav/visual_entry_noise_suppression_cluster_priority_runner.py`.

Результат DEV `2026-05-12`: `11/11`, `0` missed, `28` false, `39` entries, precision `0.2821`, recall `1.0000`, f1 `0.4400`.

Recover добавил:
1. `08:25 -> 08:26`: `RECOVER_NOWICK_SUPPORT_PULLBACK` из `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP`;
2. `16:59 -> 17:00`: `RECOVER_D03_LATE_RETEST` из `DQ01_EQ01_PLUS_DEEP_RECLAIM`.

Главный PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp06_cp01_recover_nowick_late_retest_20260625T151725Z.png`.
Отчет: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_noise_suppression_cluster_priority_20260512_DEV_RU.md`.

Проверки: py_compile PASS; новый recover regression включен; `tests.test_visual_entry_noise_suppression_cluster_priority_runner` `3/3 OK`; visual-entry set `5/5 OK`; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260625T151851Z.json`; процесс-хвостов нет.

Следующий шаг: визуально согласовать PNG с пользователем. Потом без подкрутки прогнать `2026-05-13` validation и `2026-05-14` holdout. В ML ничего не передавать.

## Handoff 2026-06-29 Visual Entry RBKD V0
Текущий статус: `DEV_RBKD_V0_BUILT_TOO_NOISY_NO_ML_NEXT_SWING_SUPPORT_EVENT`.

Сделано: добавлен diagnostic runner `src/mlbotnav/visual_entry_reversal_bottom_knife_drop_runner.py` и тест `tests/test_visual_entry_reversal_bottom_knife_drop_runner.py`. Runner соблюдает контракт `signal candle -> next candle open`, `slippage_bps=5`, `lookahead=NO`, `ml_transfer_allowed=false`.

Результаты:

1. `2026-05-13`: лучший `RBKD03_PULLBACK_AFTER_RECLAIM`, `2/9` hits, `81` false, `83` entries.
2. `2026-05-14`: лучший `RBKD03_PULLBACK_AFTER_RECLAIM`, `1/17` hits, `83` false, `84` entries.

Аудит: `reports/final_review/visual_entry_v3/reversal_bottom_knife_drop/visual_entry_reversal_bottom_knife_drop_audit_20260629T090101Z_RU.md`.

Важно: слой не кандидат и не передается в ML. Следующий рабочий шаг - `SWING_SUPPORT_RETEST_EVENT_V1`: online event-state, где событие дна/ретеста открывается по прошлым свечам, внутри события берется только первый валидный вход, затем cooldown. Не возвращаться к offline cluster-winner, потому что это дает lookahead-подобный выбор.

Проверки закрытия: `py_compile PASS`; focused unittest `2/2 OK`; совместные visual-entry tests `5/5 OK`; `text_guard PASS`; зависшие `python.exe -` PID `14996` и `228` остановлены, повторный process-check пустой.
## Handoff 2026-06-29 Visual Entry SSRE V1
Текущий статус: `DEV_SSRE_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Сделано: добавлен entry-only runner `src/mlbotnav/visual_entry_swing_support_retest_event_runner.py` и тест `tests/test_visual_entry_swing_support_retest_event_runner.py`.

Контракт: ищем только входы у low/дна. Signal-свеча закрылась, вход LONG на `open` следующей свечи, `slippage_bps=5`, `lookahead=NO`, `future_trade_outcome_used=false`, `ml_transfer_allowed=false`.

Результаты:

1. `2026-05-13`: `SSRE02_TREND_DIP_FIRST_LOW_ENTRY`, `1/9` hits, `29` false.
2. `2026-05-14`: `SSRE01_SUPPORT_RETEST_FIRST_LOW_ENTRY`, `1/17` hits, `26` false.

Аудит: `reports/final_review/visual_entry_v3/swing_support_retest_event/visual_entry_swing_support_retest_event_audit_20260629T092400Z_RU.md`.

Решение: не ML, не promotion. V1 стал менее шумным, но часто входит раньше нужного пользовательского low. Следующий шаг - `SIGNIFICANT_LOW_SELECTOR_V1`: выбрать именно значимую signal-low свечу, а не первый похожий микролой в зоне. Не использовать TP/SL, будущую доходность, MFE/MAE или entry-свечу как feature.
## Handoff 2026-06-29 Fresh Strategy Overlay
Текущий статус: `DEV_FRESH_OVERLAY_DONE_ENTRY_ONLY_NO_CALIBRATION_NO_ML`.

Добавлен свежий clean overlay runner: `src/mlbotnav/visual_entry_strategy_fresh_overlay.py`.

Он заново рендерит чистый график из `source_csv`, а не использует старые картинки с разметкой. Поверх кладет ручные low-входы и 4 default strategy layers: `Support Retest`, `Trend Dip`, `Deep Knife`, `Hot Continuation`.

Аудит: `reports/final_review/visual_entry_v3/fresh_strategy_overlay/visual_entry_fresh_strategy_overlay_audit_20260629T113100Z_RU.md`.

Важно: combined PNG плотный, для работы глазами использовать отдельные PNG по стратегиям. Дефолты не кандидат и не ML. Следующий шаг - визуально выбрать живые стратегии и только потом делать грубую калибровку.
## Handoff 2026-06-29 User Red Arrows V2 Fixed
Текущий статус: `HOLDOUT_DAY_USER_RED_ARROWS_V2_FIXED_AUTO_DETECTED_NEEDS_VISUAL_CONFIRM`.

Пользователь прислал новый скрин `SOLUSDT 1m 2026-05-14` с красными стрелками. Скрин сохранен и автоматически переведен в `manual_entries.json`.

Новая база сравнения:

`reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries.json`

Контрольный PNG:

`reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries_v2_fixed_signal_entry_verify_20260629T115000Z.png`

## Handoff 2026-06-29 Significant Low Selector V1
Текущий статус: `DEV_SIGNIFICANT_LOW_SELECTOR_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Сделано: добавлен runner `src/mlbotnav/visual_entry_significant_low_selector_runner.py`, тест `tests/test_visual_entry_significant_low_selector_runner.py`, PNG/JSON/MD в `reports/final_review/visual_entry_v3/significant_low_selector`, аудит `visual_entry_significant_low_selector_audit_20260629T125000Z_RU.md`.

Итог на `17` пользовательских входах `2026-05-14`: fresh default4 `3/17`, `260` false; `SLS06` `5/17`, `71` false; `SLS05` `2/17`, `20` false; `SLS11` `9/17`, `174` false; `SLS10` `13/17`, `463` false.

Главный PNG: `reports/final_review/visual_entry_v3/significant_low_selector/visual_entry_family_overlay_2026-05-14_sls_v1_01_sls06_hot_reclaim_strict_false_control_20260629T124723Z.png`.

Решение: V1 не кандидат и не ML. Следующее действие - `LOW_CLUSTER_RANKER_V2`: выбрать один главный low внутри активной зоны по past-only признакам, без TP/SL/future return и без cooldown-сеток `30/45/60/90`.

## Handoff 2026-06-29 Low Cluster Ranker V2
Текущий статус: `DEV_LOW_CLUSTER_RANKER_V2_ENTRY_ONLY_DONE_REDUCED_FALSE_LOW_RECALL_NO_ML`.

Добавлены `src/mlbotnav/visual_entry_low_cluster_ranker_runner.py` и `tests/test_visual_entry_low_cluster_ranker_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/low_cluster_ranker/visual_entry_low_cluster_ranker_audit_20260629T133000Z_RU.md`.

Итог на `17` пользовательских входах `2026-05-14`: `LCR04` = `3/17`, `10` false; `LCR07` = `2/17`, `4` false; `LCR06` = `7/17`, `64` false.

Главный PNG: `reports/final_review/visual_entry_v3/low_cluster_ranker/visual_entry_family_overlay_2026-05-14_lcr_v2_01_lcr04_late_low_with_reclaim_cluster_20260629T132833Z.png`.

Решение: V2 не кандидат и не ML. Он доказал, что кластерный выбор режет false, но один общий режим теряет много пользовательских входов. Следующий шаг - разложить miss по режимам и строить отдельные режимные слои.

Снято `17` входов. Предыдущая авторазметка на `18` входов была кривой: один тонкий фрагмент красной линии ошибочно попал как отдельная стрелка и удален. Время снято по красным стрелкам со скрина и имеет статус `NEEDS_VISUAL_CONFIRM`, допуск временно `±1` бар. До подтверждения не использовать для ML/export/promotion.
# Handoff 2026-06-29 Regime Split Ranker V1
Текущий статус: `DEV_REGIME_SPLIT_RANKER_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_regime_split_ranker_runner.py` и тест `tests/test_visual_entry_regime_split_ranker_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/regime_split_ranker/visual_entry_regime_split_ranker_audit_20260629T134600Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/regime_split_ranker/visual_entry_family_overlay_2026-05-14_regime_split_v1_01_rsr07_structure_bos_fibo_volume_cluster_20260629T134448Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: `STRUCTURE` лучший `7/17` при `84` false, `TREND` `7/17` при `95` false, `HOT` `6/17` при `87` false, `DEEP` `2/17` при `12` false. V1 не кандидат и не ML.

Важное решение: слой переведен в online-style `first_qualified_no_future_rewrite`, чтобы будущий более сильный low не переписывал уже выбранный вход.

Следующий шаг: `REGIME_FALSE_SUPPRESSION_V2` по отдельным шумным режимам, без сделок, без TP/SL/MFE/MAE/future return и без ML.

# Handoff 2026-06-29 Regime False Suppression V2
Текущий статус: `DEV_REGIME_FALSE_SUPPRESSION_V2_ENTRY_ONLY_DONE_STILL_TOO_NOISY_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_regime_false_suppression_runner.py` и тест `tests/test_visual_entry_regime_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_regime_false_suppression_audit_20260629T135843Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_family_overlay_2026-05-14_regime_false_suppression_v2_01_fsv21_union_strict_false_control_20260629T135626Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: лучший union `FSV21` = `7/17`, `41` false; trend `FSV05` = `6/17`, `40` false; чистый deep `FSV02` = `2/17`, `4` false.

Решение: V2 не кандидат и не ML. Он полезен как suppress-диагностика, но ложных входов все еще много. Следующий шаг - `ONLINE_LOW_EVENT_QUALITY_V3`: добавить состояние low/support-события, возраст события, порядок кандидата внутри события, расстояние до event-low и suppress горячих верхних полок, без будущих данных и без сделок.

# Handoff 2026-06-29 Online Low Event Quality V3
Текущий статус: `DEV_ONLINE_LOW_EVENT_QUALITY_V3_ENTRY_ONLY_DONE_CLEANER_LOW_RECALL_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_online_low_event_quality_runner.py` и тест `tests/test_visual_entry_online_low_event_quality_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_online_low_event_quality_audit_20260629T141715Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_family_overlay_2026-05-14_online_low_event_quality_v3_01_olev20_union_event_quality_balanced_20260629T141647Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: лучший `OLEV20` = `3/17`, `7` false, `10` entries, f1 `0.2222`. Это чище V2 (`41` false), но recall низкий.

Решение: V3 не кандидат и не ML. Следующий шаг - `DEEP_RECOVERY_AND_HOT_RECALL_V4`: добирать пропущенные deep/hot/trend входы отдельными кирпичами, не расширяя чистый event-quality union обратно в шум.

# Handoff 2026-06-29 Deep Recovery And Hot Recall V4
Текущий статус: `DEV_DEEP_RECOVERY_AND_HOT_RECALL_V4_ENTRY_ONLY_DONE_BETTER_BALANCE_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_deep_recovery_hot_recall_runner.py` и тест `tests/test_visual_entry_deep_recovery_hot_recall_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_deep_recovery_hot_recall_audit_20260629T144050Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_family_overlay_2026-05-14_deep_recovery_hot_recall_v4_01_drhr20_olev20_plus_deep_recovery_20260629T144015Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: основной `DRHR20` = `5/17`, `13` false, `18` entries, f1 `0.2857`. Он ловит `03:24`, `06:42`, `12:07`, `16:53`, `17:35`.

Решение: V4 не кандидат и не ML, но это лучший баланс текущей цепочки. Hot/trend diagnostic ловит `8/17`, но дает `43` false, поэтому не включен в рабочий union. Следующий шаг - `HOT_TREND_FALSE_SUPPRESSION_V5`.

# Handoff 2026-06-29 Hot Trend False Suppression V5
Текущий статус: `DEV_HOT_TREND_FALSE_SUPPRESSION_V5_ENTRY_ONLY_DONE_RECALL_UP_FALSE_STILL_HIGH_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_hot_trend_false_suppression_runner.py` и тест `tests/test_visual_entry_hot_trend_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_hot_trend_false_suppression_audit_20260629T145900Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_family_overlay_2026-05-14_hot_trend_false_suppression_v5_01_htfs20_union_htfs01_hot_trend_strict_false_suppression_20260629T145736Z.png`.

Чистый hot/trend PNG: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_family_overlay_2026-05-14_hot_trend_false_suppression_v5_04_htfs01_hot_trend_strict_false_suppression_20260629T145745Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: лучший union `HTFS20_UNION_HTFS01` = `9/17`, `14` false, `23` entries, f1 `0.4500`. Чистый `HTFS01` = `4/17`, `1` false, `5` entries, precision `0.8000`.

Решение: V5 не ML-кандидат, но `HTFS01` можно оставить как чистый hot/trend-кирпич. Следующий шаг - `BASE_FALSE_SUPPRESSION_V6`: резать ложные входы базовой V4-части, не ухудшая `HTFS01`.

# Handoff 2026-06-29 Base False Suppression V6
Текущий статус: `DEV_BASE_FALSE_SUPPRESSION_V6_ENTRY_ONLY_DONE_BEST_CURRENT_ONE_DAY_NO_ML`.

Сделано: добавлен `src/mlbotnav/visual_entry_base_false_suppression_runner.py` и тест `tests/test_visual_entry_base_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_base_false_suppression_audit_20260629T151215Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_family_overlay_2026-05-14_base_false_suppression_v6_01_bfs20_union_bfs01_base_source_split_strict_false_suppression_plus_htfs01_20260629T151147Z.png`.

Результат на пользовательских `17` low-входах `2026-05-14`: лучший union `BFS20_UNION_BFS01...PLUS_HTFS01` = `9/17`, `1` false, `10` entries, f1 `0.6667`. Базовая V4-часть очищена: `BFS01` = `5/17`, `0` false.

Решение: это лучший текущий слой, но он проверен только на одном holdout-дне, поэтому `NO_ML`. Следующий шаг - прогнать V6 без изменения параметров на `2026-05-13` validation и отдельно разобрать false `18:47`.

# Handoff 2026-06-29 V6 Validation Fail
Текущий статус: `VALIDATION_FAIL_V6_DOES_NOT_GENERALIZE_NO_ML`.

V6 запущен на `2026-05-13` validation без изменения параметров.

Аудит: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_base_false_suppression_validation_audit_20260629T155000Z_RU.md`.

Главный PNG validation: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_family_overlay_2026-05-13_bfs_v6_03_u_bfs01_bss_s_fs_h01_20260629T154949Z.png`.

Результат: лучший V6 union на `2026-05-13` = `0/9`, `1` false, `1` entry. Сырой base V4 = `0/9`, `17` false.

Решение: V6 не обобщился, не ML. Первый validation-запуск падал из-за длинного имени PNG; исправлен только короткий render label, параметры стратегии не менялись.

Следующий шаг: `GENERALIZATION_V7`, разбор missed validation-целей и новый режимный слой для проверки сразу на `2026-05-13` + `2026-05-14`.
# Handoff 2026-06-29 Visual Entry NEGATIVE_CONTEXT_SUPPRESSION_V8

Статус: `NEGATIVE_CONTEXT_SUPPRESSION_V8_PARTIAL_BRICK_NO_ML`.

Добавлено:

1. `src/mlbotnav/visual_entry_negative_context_suppression_v8_runner.py`;
2. `tests/test_visual_entry_negative_context_suppression_v8_runner.py`;
3. аудит `reports/final_review/visual_entry_v3/negative_context_suppression_v8/visual_entry_negative_context_suppression_v8_audit_20260629T173500Z_RU.md`.

V8 построен как suppress-слой поверх V7, не как новый recall-режим. После агентского аудита добавлены `NCS01_SIDEWAYS_MICRO_LOW`, `NCS02_HOT_UPPER_SHELF`, `NCS03_RETEST_SERIES_SATURATION`, `NCS04_POST_IMPULSE_NO_PULLBACK`, `NCS05_WEAK_RECLAIM_NO_LOCAL_LOW`.

Итог:

1. Validation `2026-05-13`: `V8_02_HOT_CHAIN_EVENT_LOW_SUPPRESSION` = `1/9`, `0` false, `1` entry. Чистый кирпич для `08:48`.
2. Holdout `2026-05-14`: `V8_01_HOT_FIRST_NEGATIVE_SUPPRESSION` = `4/17`, `29` false, `33` entries. Лучше V7, но все еще noisy.
3. `V8_20_UNION_NEGATIVE_SUPPRESSION` не использовать: на holdout `11/17`, но `168` false.

Решение: ничего в ML не передавать. Следующий шаг `V9_BRICK_BY_BRICK_SELECTOR`: закреплять отдельные чистые кирпичи и не собирать общий union, пока каждый режим сам не выглядит чисто на PNG.

# Handoff 2026-06-29 Visual Entry GENERALIZATION_V7

Статус: `GENERALIZATION_V7_DIAGNOSTIC_FAIL_NO_ML`.

Добавлено:

1. `src/mlbotnav/visual_entry_generalization_v7_runner.py`;
2. `tests/test_visual_entry_generalization_v7_runner.py`;
3. аудит `reports/final_review/visual_entry_v3/generalization_v7/visual_entry_generalization_v7_audit_20260629T172000Z_RU.md`.

Проверено на двух днях без разных параметров:

1. Validation `2026-05-13`: best `G7_02_HOT_CHAIN_DIP_DIAG` = `1/9`, `22` false, `23` entries, f1 `0.0625`.
2. Holdout `2026-05-14`: best by f1 `G7_01_HOT_FIRST_RECLAIM_DIAG` = `4/17`, `43` false, `47` entries, f1 `0.1250`; union = `11/17`, но `203` false.

Решение: V7 не стратегия и не ML-кандидат. Он только показал, что простые hot/warm/deep режимы ловят отдельные пользовательские входы, но дают слишком много ложных микролоев.

Следующий шаг: `NEGATIVE_CONTEXT_SUPPRESSION_V8` - не расширять recall, а подавлять боковые микролои, горячие верхние полки и повторные ложные retest-серии. Контракт прежний: `signal close -> next open`, `lookahead=NO`, `5 bps`, без TP/SL/MFE/MAE/future return/entry-candle OHLCV.
# Handoff 2026-06-30 Fresh Target-Led Visual Entry Workflow

Статус: `FRESH_TARGET_LED_WORKFLOW_READY_NO_ML`.

# Handoff 2026-06-30 C02 Split/Router Current

Статус: `C02_SPLIT_ROUTER_DECISION_V0_COMPLETE_NO_SCORER_NO_ML_NO_OPTUNA`.

Работать только по fresh target-led рельсам. Старые V7/V8/V9/V10/V11, старые Optuna-переборы и ML-export не продолжать как очередь.

Завершен пункт `8.3 C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`.

Итог:
- `C02A_TRUE_DEEP_CAPITULATION_CORE`: `C02E03/M01`, `C02E04/M02`, `C02E10/M08`;
- router `SUPPORT_RETEST_LOW`: `C02E05`, `C02E06`, `C02E07`;
- router `HOT_RECLAIM_SUPPORT`: `C02E08`, `C02E11`;
- router `SWING_LOW_RECLAIM`: `C02E09`, `C02E12`;
- negative controls: `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.png`.

Следующий подпункт: `8.3.1_DESIGN_C02A_TRUE_DEEP_CAPITULATION_CORE_RULES_FROM_PAST_ONLY_FEATURES_NO_SCORER_YET`.

До завершения `8.3.1` запрещены scorer, target-lock, multi-day, Optuna, ML/export/promotion.

Поправка визуала после замечания пользователя:
- цена входа не потеряна; для `M01..M19` она лежит в target ledger, для `C02E01..C02E16` создана отдельная таблица;
- рабочие C02 визуалы теперь должны использовать `price_clarity_fix_v0`, где есть zoom-sheet, high-res full-day и SVG;
- следующие скрины обязательно должны показывать `signal`, `entry`, `entry_open_price`, `entry + 5 bps`;
- цена входа остается execution-only и запрещена как признак выбора входа.

Главный рабочий визуал C02 после фикса:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_ZOOM_SHEET_V0_20260630.png`.

C02A rules draft `8.3.1` создан без scorer:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_V0_20260630_RU.md`.

Рабочий визуал для review:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_VISUAL_V0_20260630.png`.

Следующий подпункт: `8.3.1_USER_VISUAL_REVIEW_C02A_RULES_V0_BEFORE_SCORER`. До решения пользователя scorer, target-lock, multi-day, Optuna и ML/export/promotion запрещены.

Активный новый протокол: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_FRESH_PROCESS_TZ_RU.md`.

Следующий чат должен начинать не с продолжения старых V7/V8/V9/V10/V11, а с чистого target-led процесса:

1. чистый график;
2. ручные цели `T01..T10`;
3. тип входа для каждой цели;
4. стратегия под один тип;
5. паспорт-контракт;
6. entry-only PNG/scorer;
7. target-lock;
8. Optuna только внутри готового паспорта;
9. ML только после отдельного `APPROVED_FOR_ML`.

Старые слои и отчеты использовать только как архив идей и справочные артефакты. Не брать старую хронологию как очередь задач.

Первый практический шаг нового чата: выбрать один день, подтвердить `T01..T10`, создать `target_ledger`, разложить входы по типам и выбрать первый кластер из 2-4 похожих входов.

# Handoff 2026-06-30 Fresh Target-Led Start Done

Статус: `FRESH_TARGET_LED_DAY_SELECTED_LEDGER_READY_NO_ML`.

Выбран день чистого старта: `2026-05-14`, `SOLUSDT`, `1m`, `core`.

Сделано без Optuna и без ML:
1. добавлена утилита `src/mlbotnav/visual_entry_fresh_target_ledger.py`;
2. создан чистый график без старых сигналов: `reports/final_review/visual_entry_v3/fresh_target_led/fresh_target_led_clean_chart_SOLUSDT_1m_2026-05-14_20260630T062202Z.png`;
3. создан ledger: `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10.json`;
4. создан русский отчет: `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10_RU.md`.

T01..T10 взяты из `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries.json` и имеют статус `candidate_needs_visual_confirm`. Это еще не target-lock.

Первый кластер-кандидат после visual review: `HOT_RECLAIM_SUPPORT`, точки `T07`, `T08`.

`T04` была показана пользователю на полном графике и отклонена как неподходящая точка входа. В lock и паспорт ее не включать.

`T07` исправлена пользователем: правильный signal `2026-05-14T10:42:00Z`, правильный LONG entry `2026-05-14T10:43:00Z`; старое автоположение `10:48 -> 10:49` позднее и не подходит.

`T08` исправлена по пользовательской нарисованной метке: предполагаемый signal `2026-05-14T12:00:00Z`, предполагаемый LONG entry `2026-05-14T12:01:00Z`. Нужно коротко подтвердить точное время.

Следующий исполнитель должен получить confirm по `T08 = 12:01` или поправить ее. Старые V7/V8/V9/V10/V11 не продолжать как очередь задач.

Рельсы fresh target-led процесса зафиксированы: `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_RAILS_RU.md`. Работать до результата по ним: confirm целей -> один кластер -> паспорт -> entry-only PNG/scorer -> lock -> только потом Optuna/ML-gate.
# Handoff 2026-06-30 Fresh Target-Led User Marked Order

Статус: `USER_MARKED_DEVELOPMENT_ORDER_NEEDS_ZOOM_CONFIRM_NO_ML`.

Новый источник порядка разработки: пользовательский full-day скрин с красными прямоугольниками. Работать слева направо по `M01..M15`, а не пытаться добить ровно 10 точек из старого `T01..T10`.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514.json`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/user_marked_development_order/user_marked_development_order_20260514_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M01_user_marked_order_zoom_signal_0323_entry_0324.png`.

`T08` подтверждена пользователем: signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`, статус `gold_user_visual_confirmed`.

Следующий шаг: показать `M01` zoom-кандидат `signal 03:23 -> LONG entry 03:24` и принять ручное решение `подходит / не подходит / сдвинуть`.

Запреты сохраняются: без Optuna до паспорта, без ML/export/promotion до `APPROVED_FOR_ML`, не продолжать старые V7/V8/V9/V10/V11 как очередь задач.
