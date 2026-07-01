# Current State

## Current State 2026-07-01 Git Init MLbotNav

Текущий статус: `GIT_INIT_DONE_WAIT_REMOTE_AND_AUTHOR_FOR_INITIAL_COMMIT`.

Локальный Git-репозиторий создан, активная ветка `main`. Первый коммит пока не сделан, потому что в Git не настроены `user.name`/`user.email`, а remote URL еще не задан.

Подготовлено к первому коммиту: source/config/docs/tests/scripts, `646` staged-файлов, около `11.12 MB`. Исключено из Git: `.env`, `.venv`, `.vscode`, `data/`, `models/`, `reports/`, `logs/`, `packs/`, `tmp/`, `_codex_offload_*`, `_locked_tmp_*`, backup-файлы `*.bak`, `*.bak_*`, `*.bak-*`. Добавлен `.gitattributes`, чтобы стабилизировать окончания строк.

## Current State 2026-07-01 Strategy Passport Gap Audit

Текущий статус: `STRATEGY_PASSPORT_GAP_AUDIT_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь принял визуальный V1 evidence layer по `19+7`, но указал, что на скрине не видны созданные стратегии/паспорта: `swing`, `BOS`, `Fibonacci` и т.д.

Вывод аудита: V1 показывает индикаторные панели и простые подсказки, но не исполняет строгие паспорта `F012-F052` как `ALLOW 1/0`. Не хватает strategy/passport overlay и матрицы `target_id -> какие паспорта поддержали вход`.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_STRATEGY_PASSPORT_GAP_AUDIT_20260701_RU.md`.

Следующий шаг: собрать `INDICATOR_HYPOTHESIS_REVIEW_V2_STRATEGY_PASSPORT_OVERLAY_NO_SCORER_NO_ML_NO_OPTUNA` по тем же ручным входам `M01..M19` и 7 T15.

## Current State 2026-07-01 Codex Agent Launch Kit MLbotNav

Текущий статус: `CODEX_AGENT_LAUNCH_KIT_MLBOTNAV_READY_NO_PROJECT_CODE_CHANGE`.

Для запуска нового агента именно в проекте `MLbotNav` использовать:

```powershell
C:\Users\007\Desktop\Codex Agent\Start MLbotNav Codex Agent.cmd
```

Для продолжения последней Codex-сессии с рабочей папкой `MLbotNav` использовать:

```powershell
C:\Users\007\Desktop\Codex Agent\Resume MLbotNav Codex Agent.cmd
```

Проверено: `codex-cli 0.142.5`, `codex login status` = вход через ChatGPT, проект есть в trusted-конфиге. `codex doctor` завершился без fail: авторизация, сеть, WebSocket, Git и конфиг в порядке. Остались предупреждения про старые записи истории Codex и отсутствие `.git` в проекте.

## Current State 2026-07-01 Indicator/Hypothesis Review V1 19+7

Текущий статус: `INDICATOR_HYPOTHESIS_REVIEW_V1_M01_M19_T15V1_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь поправил порядок: перед паспортом нужен отдельный feature/evidence слой по двум эталонам, а не переход сразу к passport. Создан `indicator_hypothesis_review_v1`.

Состав: `19` входов `M01..M19` за `2026-05-14` и `7` входов `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16` за `2026-05-15` из `draft_ledger_v1`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_M01_M19_20260514.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_FULL_DAY_T15_7_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v1/INDICATOR_HYPOTHESIS_REVIEW_V1_ZOOM_T15_7_20260515.png`.

Следующий шаг: показать пользователю V1 и получить `норм/фиксить`. Passport C01 отложен до review этого второго слоя. Scorer, target-lock, Optuna и ML/export запрещены.

## Current State 2026-07-01 T15 Draft Ledger V1 Confirmed

Текущий статус: `T15_DRAFT_LEDGER_V1_USER_CONFIRMED_NEXT_PASSPORT_C01_NO_SCORER_NO_ML_NO_OPTUNA`.

Пользователь сказал `норм` по `draft_ledger_v1`. Старый `draft_ledger_v0` не использовать.

Рабочие 7 входов: `T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Следующий шаг по рельсам: собрать черновой паспорт-контракт только для `T15_C01_SUPPORT_RETEST_LOW` (`T15L02`, `T15L08`, `T15L16`) и показать PNG/таблицу пользователю. Scorer, target-lock, Optuna и ML/export запрещены.

## Current State 2026-07-01 T15 Draft Ledger V1 Red Arrow Fix

Текущий статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_RED_ARROW_FIX_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Актуальный рабочий слой T15 draft-ledger теперь `draft_ledger_v1`, потому что пользователь поправил три входа красными стрелками:

- `T15L02`: entry `02:35` -> `02:34`;
- `T15L07`: entry `06:23` -> `06:21`;
- `T15L08`: entry `08:32` -> `08:31`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.png`.

RU report:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701_RU.md`.

`draft_ledger_v0` больше не использовать для паспорта. Следующий шаг: дождаться `норм / фиксить` по v1.

## Current State 2026-07-01 T15 Draft Ledger / Cluster Discussion V0

Текущий статус: `T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

Собран рабочий draft-ledger по 7 входам `SOLUSDT 1m 2026-05-15` из `T15_USER_VERDICT_V1`:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Разложение:

- `T15_C01_SUPPORT_RETEST_LOW`: `3` входа, `T15L02/T15L08/T15L16`; первый кандидат на паспортный разбор.
- `T15_C02_DEEP_CAPITULATION_LOW`: `2` входа, `T15L06/T15L13`; отдельный deep-кластер.
- `T15_C03_HOT_RECLAIM_CONTINUATION`: `2` входа, `T15L07/T15L11`; пока observe-only, не смешивать в первый паспорт.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701.png`.

RU report:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/draft_ledger_v0/T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V0_20260701_RU.md`.

Граница: это не target-lock, не scorer, не ML dataset и не Optuna. `entry_open_price` и `entry + 5 bps` только execution/control. Следующий шаг: пользователь смотрит скрин и говорит `норм` или что фиксить.

## Current State 2026-07-01 T15 User Verdict V1

Текущий статус: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: “тут 7 должно входов”. Предыдущий `user_verdict_v0` больше не использовать как рабочий слой.

Актуально подтверждены 7 входов:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.json`.

Следующий шаг: draft-ledger/cluster discussion по всем 7 confirmed entries, без target-lock/scorer/ML/Optuna.

## Current State 2026-07-01 Indicator/Hypothesis Visual Review V0

Текущий статус: `INDICATOR_HYPOTHESIS_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Создан визуальный пакет для проверки гипотез по `SOLUSDT 1m` на `2026-05-14` и `2026-05-15`: price/volume, RSI14, MACD, density, trailing swing, BOS и Fibo на zoom. Это сделано как “лестница для глаз”, а не как scorer.

Состав: `19` manual gold на `2026-05-14`, `15` rejected на `2026-05-15`, `7` pending на `2026-05-15`.

Основные PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260514.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_PENDING_ZOOM_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_20260701.json`.

Следующий шаг: пользователь смотрит visual evidence и дает verdict по инструментам и 7 pending. ML/export/Optuna запрещены.

Ассистентский verdict:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/INDICATOR_HYPOTHESIS_REVIEW_V0_ASSISTANT_VERDICT_20260701_RU.md`.

Итог: RSI/MACD/volume/Fibo не являются готовым правилом. Нужна структура сначала: значимый low/reclaim, не микролой в шуме, room/path до плотной зоны, затем volume/RSI как подтверждение. Приоритет для следующего zoom: `T15L06`, `T15L13`, `T15L16`.

## Current State 2026-07-01 T15 Priority Zoom Review V0

Текущий статус: `T15_PRIORITY_ZOOM_REVIEW_V0_READY_NO_ML_NO_OPTUNA`.

Создан priority zoom-review по `T15L06`, `T15L13`, `T15L16`.

Sheet PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_SHEET_20260515.png`.

Ассистентский verdict:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_ASSISTANT_VERDICT_20260701_RU.md`.

Итог: `T15L06` и `T15L16` выглядят как основные gold-кандидаты для пользовательского подтверждения. `T15L13` оставить possible, но не делать ядром паспорта.

## Current State 2026-07-01 T15 User Verdict V0

Текущий статус: `T15_USER_VERDICT_V0_FIXED_NO_ML_NO_OPTUNA` superseded.

Пользователь ответил “норм” после priority zoom. Зафиксировано:

- `T15L06`, `T15L16`: `gold_candidate_user_confirmed`;
- `T15L13`: `possible_not_primary`;
- `T15L02`, `T15L07`, `T15L08`, `T15L11`: `weak_not_promoted_after_priority_review`;
- feedback v2 rejected сохраняются как `bad_noise`.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v0/T15_USER_VERDICT_V0_20260701.json`.

Этот слой больше не использовать как рабочий: пользователь уточнил, что входов должно быть `7`. Рабочий слой: `T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA`.

## Current State 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V2

Текущий статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V2_FIXED_NO_ML_NO_OPTUNA`.

Актуальный feedback по `T15L01..T15L22`: `15` rejected, `7` pending. Пользователь уточнил, что `T15L10` тоже крест.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L10`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16`.

Feedback PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json`.

Следующий шаг: разобрать 7 pending отдельно. Pending не gold, ML/export/Optuna запрещены.

## Current State 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V1

Текущий статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_V1_FIXED_NO_ML_NO_OPTUNA`.

Актуальный feedback по `T15L01..T15L22`: `14` rejected, `8` pending. Пользователь дополнительным full-day screenshot показал, что `T15L21` тоже rejected.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L21`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`.

Feedback PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v1/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json`.

Следующий шаг: разобрать 8 pending отдельно. Pending не gold, ML/export/Optuna запрещены.

## Current State 2026-07-01 Low Anchor Transfer User Feedback 2026-05-15 V0

Текущий статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь разметил screenshots по `T15L01..T15L22`: красные X/перечеркивания означают `не подходит`.

Итог: `13` rejected, `9` pending.

Rejected:
`T15L01`, `T15L03`, `T15L04`, `T15L05`, `T15L09`, `T15L12`, `T15L14`, `T15L15`, `T15L17`, `T15L18`, `T15L19`, `T15L20`, `T15L22`.

Pending:
`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L10`, `T15L11`, `T15L13`, `T15L16`, `T15L21`.

Feedback PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_20260515.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json`.

Следующий шаг: разобрать pending-кандидаты отдельно и не считать их gold без явного `норм`/`сдвинуть`. ML/export/Optuna запрещены.

## Current State 2026-07-01 Low Anchor Transfer Review 2026-05-15 Compact V0

Текущий статус: `LOW_ANCHOR_TRANSFER_REVIEW_V0_DAY_20260515_READY_NO_ML_NO_OPTUNA`.

Сделан новый out-of-sample visual transfer review для `SOLUSDT 1m 2026-05-15`: проверяем, переносится ли понимание ручных входов `M01..M19` с `2026-05-14` на соседний день.

Итог: broad-кандидатов `89`, compact review-кандидатов `22`, zoom-страниц `2`.

Активный пакет:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/`.

Главный full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_FULL_DAY_20260515.png`.

Zoom pages:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_01_20260515.png`;
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_02_20260515.png`.

Все `T15L##` пока `pending_user_visual_review`. Нельзя использовать как labels, scorer, ML dataset или Optuna objective. EMA не active condition.

## Current State 2026-07-01 Feature Policy EMA Deferred

Текущий статус: `LOW_ANCHOR_FEATURE_POLICY_EMA_DEFERRED_NO_ML_NO_OPTUNA`.

Пользователь уточнил: EMA пока не трогаем. Следующие шаблоны/passport/checklist делаем без EMA как условия входа.

Правило дальше:

- EMA-колонки из audit остаются справочными;
- активные шаблоны строить через структуру движения, положение в диапазоне, low/reclaim, volume/range/wick closed signal candle;
- не добавлять EMA-фильтр в scorer/checklist без отдельного решения пользователя.

## Current State 2026-07-01 Low Anchor No-Lookahead Feature Audit V0

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_READY_NO_ML_NO_OPTUNA`.

Создан no-lookahead feature audit по `85` записям: `19 manual_gold`, `51 bad_noise`, `12 manual_shift_review`, `3 possible_entry`.

Audit использует только закрытую `signal`-свечу и прошлый контекст. Entry-candle OHLCV, future return, TP/SL, MFE/MAE не используются.

Главный вывод: локальный low сам по себе не является входом. Для будущего scorer/passport нужны фильтры контекста до entry: структура движения без EMA, положение в диапазоне, room до recent high, сила reclaim, volume/range/wick signal-свечи.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701.png`.

RU report:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/feature_audit_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_NO_LOOKAHEAD_FEATURE_AUDIT_20260701_RU.md`.

Следующий безопасный шаг: zoom-lock для `manual_shift_review` или draft no-lookahead feature checklist/passport. ML/export/promotion запрещены.

## Current State 2026-07-01 Low Anchor Extra Auto Feedback Summary

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_COMPLETE_NO_ML_NO_OPTUNA`.

Extra auto pool закрыт: `66` кандидатов разобраны пользователем на `6` страницах.

Итог:

- `bad_noise`: `51`;
- `possible_entry`: `3`;
- `manual_shift_review`: `12`.

Summary:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/feedback_summary_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_FEEDBACK_SUMMARY_20260701_RU.md`.

Следующий безопасный шаг: не ML, а аудит признаков: сравнить ручные good entries `M01..M19`, `3 possible_entry`, `12 manual_shift_review` и `51 bad_noise`, выписать no-lookahead признаки для будущего event dataset/scorer.

## Current State 2026-07-01 Low Anchor Extra Auto Page06 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь закрыл page `06`: все `6` кандидатов rejected как плохие входы не по тренду.

Итог:

- `bad_noise`: `6`;
- `bad_noise_countertrend_entry`: `6`;
- `possible_entry`: `0`;
- `manual_shift_review`: `0`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page06_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE06_FEEDBACK_20260701.png`.

## Current State 2026-07-01 Low Anchor Extra Auto Page05 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь разметил page `05`: все `12` кандидатов weak/bad и rejected. Дополнительная причина: часть auto-entry стрелок не совпадает с визуально нужной low/entry-зоной.

Итог:

- `bad_noise`: `12`;
- `bad_noise_weak_context_entry_mismatch`: `12`;
- `possible_entry`: `0`;
- `manual_shift_review`: `0`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page05_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE05_FEEDBACK_20260701.json`.

Следующий безопасный шаг: page `06` visual review, последняя страница extra auto pool.

## Current State 2026-07-01 Low Anchor Extra Auto Page04 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь прислал красный screenshot page `04`: текущие auto-entry не являются готовыми точками входа; рядом показаны более удобные места, которые нужно разбирать отдельно на zoom.

Итог:

- `manual_shift_review`: `12`;
- `auto_entry_not_gold_manual_shift_review`: `12`;
- `possible_entry`: `0`;
- `bad_noise`: `0`.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page04_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE04_FEEDBACK_20260701.json`.

Следующий безопасный шаг: page `05` visual review. Отдельный возможный шаг после страниц: сделать zoom-review для page `04` manual shifts и превратить их в точные ручные target-led времена/цены.

## Current State 2026-07-01 Low Anchor Extra Auto Page03 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь сказал по page `03`: `тут все слабо`. Все `12` кандидатов страницы зафиксированы как `bad_noise / bad_noise_weak_context`.

Смысл: локальный low есть, но контекст не дает уверенного рабочего движения; такие входы визуально не похожи на сделки, в которые стоит заходить.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page03_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE03_FEEDBACK_20260701.json`.

Следующий безопасный шаг: page `04` visual review. Альтернатива перед page `04`: короткий audit первых трех страниц, где уже есть `24` rejected и `3` possible entries.

## Current State 2026-07-01 Low Anchor Extra Auto Page02 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь разметил page `02`: `LA018`, `LA020`, `LA026` можно оставить для работы как `possible_entry_one_percent_followthrough`; остальные `9` кандидатов page `02` rejected как `bad_noise_shallow_bounce`.

Итог:

- `possible_entry`: `3`;
- `bad_noise`: `9`;
- `ML/export`: запрещены.

PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page02_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE02_FEEDBACK_20260701.json`.

Следующий безопасный шаг: page `03` visual review или короткий промежуточный audit по первым двум страницам: какие признаки отличают `possible_entry` от `bad_noise_shallow_bounce` без lookahead.

## Current State 2026-07-01 Low Anchor Extra Auto Page01 Feedback

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_FIXED_NO_ML_NO_OPTUNA`.

Пользователь подтвердил смысл reject для первой страницы extra auto review. `LA001..LA012` зафиксированы как `bad_noise` с причиной `bad_noise_shallow_bounce`.

Чистая формулировка: это мелкие локальные low без нормального продолжения; после входа цена дает короткий отскок или уходит в шум/стоп, часто без нужного трендового контекста. Для нашей системы это anti-example, а не рабочий вход.

PNG фиксации:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page01_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_20260701.json`.

Следующий безопасный шаг: показать page `02` extra auto review или сначала обобщить no-lookahead признаки, которыми отличать `bad_noise_shallow_bounce` от good manual entries.

## Current State 2026-07-01 Low Anchor Extra Auto Review V1

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_READY_NO_ML_NO_OPTUNA`.

Создан visual review pack для `66` extra auto candidates из resolved label-ledger V1. Это не минусы и не обучающий dataset: все строки имеют статус `pending_user_anti_review`.

Итог:

- `66` кандидатов;
- `6` PNG-страниц;
- `12` кандидатов на страницу;
- на каждом zoom показаны `entry_time_utc` и `entry_price_plus_5bps`;
- доступные ручные метки: `bad_noise`, `duplicate`, `possible_entry`, `wrong_type`, `ignore_unclear`.

Страница 01:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_01_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.json`.

Следующий безопасный шаг: пользователь смотрит страницу `01` и говорит, какие кандидаты плохие, дубли, возможные или непонятные. Optuna/ML/export запрещены.

## Current State 2026-07-01 Low Anchor Label Ledger V1 Resolved

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_BY_USER_NO_ML_NO_OPTUNA`.

Пользователь подтвердил pending review по `M05/M14/M15/M16/M17` словом `норм`. Создан resolved label-ledger V1: pending shift review закрыт, ручные времена ledger не переписаны.

Итог:

- `10` exact auto matches;
- `4` auto near not-gold по пользовательскому feedback `M03/M09/M10/M11`;
- `5` user-confirmed auto near-ok `M05/M14/M15/M16/M17`;
- `66` extra auto candidates остаются unlabeled pool.

Resolved JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701.json`.

Следующий безопасный шаг: anti-review/разбор `66` extra auto candidates или draft event dataset без ML/export.

## Current State 2026-07-01 Low Anchor Label Ledger V0

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_READY_NO_ML_NO_OPTUNA`.

Пользователь подтвердил feedback PNG по `M03/M09/M10/M11` словом `норм`. После этого создан label-ledger для `LOW_ANCHOR_ENTRY_SUGGESTER_V0`: `10` точных auto совпадений, `4` user-feedback near-not-gold, `5` pending shift review.

Следующий PNG для ручной проверки:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_PENDING_SHIFT_REVIEW_20260701.png`.

Оставшиеся цели: `M05`, `M14`, `M15`, `M16`, `M17`.

Label-ledger JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_20260701.json`.

Граница: это не ML dataset и не scorer. До ручного решения по pending-точкам они не являются positive/negative labels.

## Current State 2026-07-01 Low Anchor User Feedback M03/M09/M10/M11

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_NO_ML_NO_OPTUNA`.

Пользователь дал visual feedback красными рамками/стрелками по `LOW_ANCHOR_ENTRY_SUGGESTER_V0`: `M03`, `M09`, `M10`, `M11` были рядом по метрике `±3m`, но не считаются gold для эталона.

Создан feedback-pack:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.png`.

JSON:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json`.

Правило дальше: `hit_within_3m` = near-review, не gold. Positive для event dataset брать из ручного ledger; auto near-candidate помечать `near-not-gold`, если пользователь показал другую свечу.

## Current State 2026-07-01 Low Anchor Suggester V0

Текущий статус: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_SEED_DAY_REVIEW_NO_ML_NO_OPTUNA`.

Создан `LOW_ANCHOR_ENTRY_SUGGESTER_V0`: seed-day помощник поиска low-anchor входов на `SOLUSDT 1m 2026-05-14`. Он предлагает `anchor_low -> signal -> entry next open + 5 bps`, без использования future return, TP/SL, MFE/MAE или entry-candle OHLCV для выбора.

Результат: `85` авто-кандидатов после фильтра, `10/19` exact hits по ручным `M01..M19`, `19/19` hits в пределах `±3m`.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_full_day_20260514.png`.

Zoom sheet для review:
`reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_target_nearest_zoom_20260514.png`.

Следующее действие: показать пользователю zoom sheet и собрать verdict по ближайшим кандидатам: `норм / сдвинуть / нет / дубль / рано / поздно`. Это подготовка event dataset, не ML.

## Current State 2026-07-01 Data Scope Monthly Samples

Текущий статус: `SOLUSDT_1M_MONTHLY_FULL_DAY_SAMPLES_CREATED_NO_ML_NO_OPTUNA`.

Создан контрольный визуальный пакет по 126-дневному покрытию `SOLUSDT 1m`: по одному full-day PNG на месяц за `2026-01..2026-05`, плюс общий contact sheet.

Выбранные дни: `2026-01-27`, `2026-02-28`, `2026-03-28`, `2026-04-28`, `2026-05-28`. Все sample-дни имеют `1440` минутных строк и идут от `00:00 UTC` до `00:00 UTC` следующего дня.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701.png`.

Отчет:
`reports/final_review/visual_entry_v3/fresh_target_led/data_scope_audit_126days/monthly_day_samples_20260701/SOLUSDT_1m_MONTHLY_FULL_DAY_SAMPLES_20260701_RU.md`.

Граница: это только audit полноты данных и визуальной шкалы. Scorer/Optuna/ML не запускались.

## Current State 2026-07-01 C01 126 Days Source Audit

Текущий статус: `C01_126_DAYS_SOURCE_AUDIT_COMPLETE_NO_ML_NO_OPTUNA`.

Аудит подтвердил: `126 дней` было реальным числом локальных файлов `SOLUSDT 1m`, а не MTF-прогоном. Scope: `data/core/bybit_ohlcv/dt=*/tf=1m/symbol=SOLUSDT/part-final.csv`, `2026-01-26` .. `2026-05-31`, все файлы по `1440` строк.

Ошибка процесса: исторический `C01_MULTI_DAY_CHECK_V1_20260630.json` не закрепил top-level `symbol`, `timeframe`, `source_csv_pattern`, диапазон дат и команду воспроизведения. Это оформлено как недофиксация источника, не как доказательство ложного результата.

Артефакт:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_126_DAYS_SOURCE_AUDIT_20260701_RU.md`.

Граница: C01 V1 остается остановленным; Optuna/ML/export/promotion запрещены.

## Current State 2026-07-01 C02A Seed-Lock

Текущий статус: `C02A_TARGET_LOCK_SEED_V0_CREATED_NO_ML_NO_OPTUNA`.

C02A seed-lock создан для `M01/M02/M08`: `C02E03`, `C02E04`, `C02E10`. JSON-реестры и Markdown-статусы синхронизированы. Это seed-lock от регрессии, multi-day еще не запускался.

Главный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/target_lock_seed_v0/C02A_TARGET_LOCK_SEED_V0_FULL_DAY_ZOOMS_20260630.png`.

Следующее действие: `9.1_MULTI_DAY_BENCH_OR_USER_DECISION_NEXT_PASSPORT_NO_ML_NO_OPTUNA`.

## Current State 2026-06-30 C02A Entry-Only Scorer V0

Текущий статус: `C02A_ENTRY_ONLY_SCORER_V0_SEED_DAY_READY_FOR_USER_REVIEW_NO_ML_NO_OPTUNA`.

Пункт рельсов `7.1` выполнен на seed-дне: C02A entry-only scorer ловит только `C02E03/M01`, `C02E04/M02`, `C02E10/M08`. Нарушений seed-аудита нет, `entry_open_price` записан только как цена исполнения и не используется для выбора входа.

Главный PNG для проверки глазами:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/entry_only_scorer_v0/C02A_ENTRY_ONLY_SCORER_VISUAL_V0_20260630.png`.

Следующее действие: `7.1_USER_VISUAL_REVIEW_C02A_ENTRY_ONLY_SCORER_V0_BEFORE_TARGET_LOCK`.

До пользовательского `норм` по PNG не делать target-lock, multi-day, Optuna и ML/export.

## Current State 2026-06-30 C02 Good/Bad Audit

Текущий статус: `C02_GOOD_BAD_AUDIT_V0_COMPLETE_NO_ML_NO_OPTUNA`.

Выполнен good/bad аудит C02. Главный вывод: C02 нельзя сразу делать одним scorer, потому что это широкий low-event finder. Он поймал `M01/M02/M08`, но хорошие события также лежат около других типов ручных входов.

Аудит:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/good_bad_audit_v0/C02_GOOD_BAD_AUDIT_V0_20260630_RU.md`.

Следующее действие: `C02_SPLIT_OR_ROUTER_DECISION_BEFORE_ENTRY_ONLY_SCORER_NO_ML_NO_OPTUNA`.

## Current State 2026-06-30 C02 User Labels Complete

Текущий статус: `C02_CANDIDATE_REVIEW_V0_USER_LABELS_COMPLETE_NO_ML_NO_OPTUNA`.

Пользователь завершил ручную разметку C02-кандидатов на seed-дне `SOLUSDT 1m 2026-05-14`: `C02E03..C02E12` помечены как `GOOD_ENTRY`, `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16` как `BAD_ENTRY`. Seed targets `M01/M02/M08` входят в хорошие кандидаты.

Контрольный PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_USER_LABELED_GOOD_BAD_SHEET_20260630.png`.

Следующее действие: аудит отличий `GOOD_ENTRY` против `BAD_ENTRY` и решение, какие условия можно перенести в entry-only scorer. Scorer/Optuna/ML/export/promotion пока не запускать.

## Current State 2026-06-30 Passport Bench Step Plan

Текущий статус: `C02_CANDIDATE_REVIEW_PACK_READY_WAIT_USER_LABELS_NO_ML_NO_OPTUNA`.

Пользователь попросил расписать процесс по пунктам и подпунктам и начать выполнение. Создана рабочая лестница `Passport Bench V0`, выполнена матрица покрытия `M01..M19`, создана папка и паспорт-драфт `C02_DEEP_CAPITULATION_LOW` по `M01/M02/M08`, сделан seed visual C02, затем пользователь подтвердил `норм`. После подтверждения создан C02 candidate layer V0.

Артефакты:

1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_BENCH_V0_STEP_PLAN_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630_RU.md`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/PASSPORT_COVERAGE_MATRIX_V0_20260630.json`.

Паспорт-драфт C02:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/passport_VE_C02_DEEP_CAPITULATION_LOW_M01_M02_M08_V0_RU.md`.

Candidate layer V0: `96` raw, `16` event representatives, seed targets `M01/M02/M08` пойманы.

Full-day PNG:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_layer_v0/C02_CANDIDATE_LAYER_V0_full_day_review_20260630.png`.

Zoom review sheet:
`reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/candidate_review_v0/C02_CANDIDATE_REVIEW_V0_zoom_sheet_C02E01_C02E16_20260630.png`.

Следующее действие: пользовательский review `C02E01..C02E16`: `GOOD_ENTRY / BAD_ENTRY / WRONG_TYPE / LATE_DUPLICATE / NEEDS_SHIFT`. Scorer, Optuna и ML не запускать до разметки.

## Current State 2026-06-30 Fresh Target-Led Passport Bench V0

Текущий статус: `PASSPORT_BENCH_V0_STRUCTURED_NO_ML_NO_OPTUNA`.

Пользователь уточнил ключевой момент: не все паспорта применены к сделкам, поэтому нельзя говорить, что весь подход работает или не работает. Проверен только один узкий C01 по `M05/M06`, и он остановлен как слабый.

Покрытие сейчас: `HOT_RECLAIM_SUPPORT` частично покрыт C01; `DEEP_CAPITULATION_LOW`, `SUPPORT_RETEST_LOW`, `SWING_LOW_RECLAIM`, `TREND_DIP_CONTINUATION` паспортами не покрыты.

Следующее действие: `PASSPORT_COVERAGE_MATRIX_V0`, затем первый новый паспорт вне C01 — `C02_DEEP_CAPITULATION_LOW` по `M01/M02/M08`. Optuna/ML/export/promotion остаются запрещены.

Аудит этапа:
`reports/final_review/visual_entry_v3/fresh_target_led/process_audit/PASSPORT_BENCH_STAGE_AUDIT_20260630_RU.md`.

## Current State 2026-06-30 Fresh Target-Led C01 V1 Stopped

Текущий статус: `C01_V1_STOPPED_TOO_FEW_AND_LOW_QUALITY_NO_ML_NO_OPTUNA`.

Пользователь честно отклонил направление `C01 V1`: сделок мало, а большая часть найденных multi-day входов визуально плохая. Это решение принято как стоп ветки, а не как повод подкручивать Optuna.

Важно: в C01 V1 нет дневного лимита сделок. `max_candidates_per_day=2` является статистикой результата строгого фильтра на 126 днях, а не правилом `максимум 2 сделки в день`.

Следующее действие: перейти от узкого паспорта `M05/M06` к более широкому target-led кандидатному слою по всем `M01..M19`, с full-day PNG на реальной шкале времени и ручной разметкой качества. ML/export/promotion остаются запрещены без `APPROVED_FOR_ML`.

Аудит решения:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/multi_day_check_v1/C01_V1_STOP_DECISION_20260630_RU.md`.

## Current State 2026-06-30 Fresh Target-Led C01 Multi-Day Check V1

Текущий статус: `C01_MULTI_DAY_CHECK_V1_RAW_NEEDS_VISUAL_TUNING_NO_ML`.

Активный свежий пункт: `C01_ENTRY_ONLY_SCORER_V0`.

Паспорт: `VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0`.

Пользователь подтвердил `M05` после сдвига на одну свечу вправо: signal `10:43 UTC` -> entry `10:44 UTC`. `M06` без изменений: signal `12:00 UTC` -> entry `12:01 UTC`.

Старый scorer V0 больше не считается актуальным pass. Новый `C01_ENTRY_ONLY_SCORER_V1` на `SOLUSDT 1m 2026-05-14` поймал `M05/M06`, ложных кандидатов `0`, `M12` не включил. После пользовательского `далее поехали по рельсам` создан seed target-lock: `M05/M06` защищены от регрессии.

PNG для пользовательского решения:
`reports/final_review/visual_entry_v3/fresh_target_led/passports/VE_C01_HOT_RECLAIM_SUPPORT_M05_M06_V0/target_lock_v1/C01_TARGET_LOCK_LEDGER_V1_full_day_M05_M06_20260630.png`.

Raw multi-day check V1: 126 дней, 25 кандидатов, максимум 2 в день. Частота не шумная, но визуальное качество смешанное. Следующее действие: показать zoom contact sheet и руками отметить кандидаты для `C01_QUALITY_FILTER_V2`. Старые V7/V8/V9/V10/V11 не продолжать как очередь задач.

## Visual Entry EVENT_RANKED_BRICKS_V10 2026-06-29

Текущий статус: `EVENT_RANKED_BRICKS_V10_CLEANER_BUT_PARTIAL_NO_ML`.

Активный свежий слой: `src/mlbotnav/visual_entry_event_ranked_bricks_v10_runner.py`.

V10 решает проблему V9 с сериями похожих входов: внутри low-cluster оставляется один rank-winner. Ключ кластера: `low_event_start_idx:event_low_idx`.

Результат: шум снизился, но часть нужных пользовательских входов потеряна.

Validation `2026-05-13`: чистый только `HOT_CHAIN`, `1/9`, `0` false.

Holdout `2026-05-14`: `warm` = `3/17`, `6` false; `hot-first` = `2/17`, `7` false; `deep` = `3/17`, `20` false.

Текущее решение: это не ML-кандидат. Следующий рабочий слой `V11_RECOVER_RANKED_MISSES`: отдельные подрежимы для потерянных warm/hot/deep входов, без широкого union.

## Visual Entry BRICK_BY_BRICK_SELECTOR_V9 2026-06-29

Текущий статус: `BRICK_BY_BRICK_SELECTOR_V9_PARTIAL_DIAGNOSTIC_NO_ML`.

Активный свежий слой: `src/mlbotnav/visual_entry_brick_by_brick_selector_v9_runner.py`.

V9 проверяет не общий шумный union, а отдельные кирпичи входа у лоя:
1. `HOT_CHAIN_EVENT_LOW`
2. `HOT_FIRST_STRONG_RECLAIM`
3. `WARM_STRUCTURAL_RECLAIM`
4. `DEEP_TERMINAL_RECLAIM`

Validation `2026-05-13`: чистый результат есть только у `V9_01_HOT_CHAIN_EVENT_LOW_BRICK`: `1/9`, `0` false, вход `08:48`.

Holdout `2026-05-14`: `warm` ловит `5/17`, но дает `16` false; `hot-first` ловит `4/17`, но дает `20` false; `deep` ловит `4/17`, но дает `33` false.

Главный вывод: направление "кирпичами" правильное, но пока это не стратегия и не ML-кандидат. Общий research union ловит больше целей, но снова создает кашу на графике (`68` false).

Следующее рабочее действие: `V10_EVENT_RANKED_BRICKS`, где внутри каждого low-event выбирается один лучший сигнал. Без cooldown `30/45/60/90`, без будущего, без TP/SL/MFE/MAE, без ML-export.

## Visual Entry manual bottoms validation/holdout 2026-06-25
Текущий статус: `MANUAL_BOTTOMS_EXTRACTED_AUTO_KNIFE_SUGGESTED_CP06_EMPTY_NO_ML`.

Пользовательские красные метки на `2026-05-13` и `2026-05-14` переведены в `manual_entries.json` по правилу `signal candle -> next open entry`:
1. `2026-05-13`: `9` ручных входов, `reports/manual_entries/SOLUSDT_1m_visual_validation_20260625_20260513_user_marked_bottoms/manual_entries.json`.
2. `2026-05-14`: `17` ручных входов, `reports/manual_entries/SOLUSDT_1m_visual_holdout_20260625_20260514_user_marked_bottoms/manual_entries.json`.

Авто-разметка `AK#` построена отдельно и не является целями ML. Контрольные PNG находятся рядом с manual entries и показывают красные `S#`, зеленые `E#`, голубые `AK#`.

CP06 на новых днях без подкрутки не дал ни одного candidate-entry. Это честный diagnostic результат: текущая DEV-12 механика не обобщилась на эти пользовательские входы. Следующий рабочий слой: `REVERSAL_BOTTOM_KNIFE_DROP_V0`.

## Visual Entry CP06 validation/holdout readiness 2026-06-25
Текущий статус: `NEEDS_MANUAL_LABELS_NO_VALIDATION_RUN`.

CP06 `CP06_CP01_RECOVER_NOWICK_LATE_RETEST` визуально закрывает DEV `2026-05-12`, но validation `2026-05-13` и holdout `2026-05-14` пока нельзя честно считать: для них отсутствуют `manual_entries.json`.

Готово:
1. seed PNG/JSON для `2026-05-13`;
2. seed PNG/JSON для `2026-05-14`;
3. core CSV по обоим дням с SHA256;
4. readiness-аудит `reports/final_review/visual_entry_v3/cp06_validation_holdout_readiness/cp06_validation_holdout_readiness_20260625_RU.md`.

Не готово: ручные `entries[].target_entry_time_utc` для validation/holdout.

Граница: не запускать подбор на `2026-05-13`/`2026-05-14`; они должны остаться честной проверкой после пользовательской разметки.

## Visual Entry v3 DEEP_CAPITULATION_RECLAIM 2026-06-25
Текущий активный visual-entry слой: `DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML`.

Runner: `src/mlbotnav/visual_entry_deep_capitulation_reclaim_runner.py`.

Лучший рабочий ensemble `DQ01_EQ01_PLUS_DEEP_RECLAIM`: `10/11` hit, `1` miss, `73` false, `83` entries, `precision=0.1205`, `recall=0.9091`, `f1=0.2128`.

High-recall diagnostic `DQ03_EQ03_HIGH_RECALL_PLUS_DEEP`: `11/11`, но `95` false, поэтому это не ML-кандидат.

Главный аудит: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_deep_capitulation_reclaim_audit_20260625_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/deep_capitulation_reclaim/visual_entry_family_overlay_2026-05-12_deep_reclaim_01_dq01_eq01_plus_deep_reclaim_20260625T142559Z.png`.

Вывод: добрали глубокие пропуски `12:33`, `15:26`, `17:00`; `08:26` ловится только high-risk no-wick режимом. Дальше нужен `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`, в ML ничего не передавать.

## Visual Entry v3 EARLY_FLUSH_REVERSAL 2026-06-25
Текущий активный visual-entry слой: `DEV_EARLY_FLUSH_REVERSAL_DIAGNOSTIC_NO_ML`.

Runner: `src/mlbotnav/visual_entry_early_flush_runner.py`.

Лучший общий результат `EQ01_Q09_SEVERE_SOFT45`: `7/11` hit, `4` miss, `68` false, `75` entries, `precision=0.0933`, `recall=0.6364`, `f1=0.1628`.

Диагностический recall-вариант `EQ03_Q09_SEVERE_SOFT45_NOWICK`: `8/11`, но `90` false; он показывает, что `08:26` можно поймать отдельным no-wick режимом, но пока слишком шумно.

Главный свежий аудит: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_early_flush_reversal_audit_20260625_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/early_flush_reversal/visual_entry_family_overlay_2026-05-12_early_flush_01_eq01_q09_severe_soft45_20260625T134923Z.png`.

Вывод: ранние входы требуют отдельных подсемейств. Это не ML-кандидат; дальше добирать глубокие пропуски `12:33`, `15:26`, `17:00` через `DEEP_CAPITULATION_RECLAIM`.

## Visual Entry v3 quality filter diagnostic 2026-06-25
Текущий активный visual-entry слой: `DEV_QUALITY_FILTER_DIAGNOSTIC_NO_ML`.

Лучший результат `Q09_ENSEMBLE_Q07_Q01`: `4/11` hit, `7` miss, `53` false, `57` entries, `precision=0.0702`, `recall=0.3636`, `f1=0.1176`.

Главный свежий аудит: `reports/final_review/visual_entry_v3/quality_filter/visual_entry_quality_filter_audit_20260625_RU.md`.

Вывод: слой качества улучшил шум относительно micro-bottom, но это не ML-кандидат. Дальше работать только на DEV-дне `2026-05-12`, без validation/holdout и без ML.

## Visual Entry v3 micro-bottom diagnostic 2026-06-25
Текущий активный статус visual-entry ветки: `DEV_MICRO_BOTTOM_SIGNATURE_DIAGNOSTIC_NO_ML`.

Контракт входа подтвержден: закрытая сигнальная свеча -> LONG на `open` следующей свечи, slippage `5 bps`, `lookahead=NO`.

Лучший micro-bottom результат: `4/11` hit, `7` miss, `135` false, `139` entries, `precision=0.0288`, `recall=0.3636`, `f1=0.0533`. Это диагностический результат, не ML-кандидат.

Главный свежий аудит: `reports/final_review/visual_entry_v3/micro_bottom_signature/visual_entry_micro_bottom_signature_audit_20260625_RU.md`.
## Visual Entry v3 passport-family diagnostic 2026-06-25
Текущий статус: `DEV_PASSPORT_FAMILY_DIAGNOSTIC_DONE_NO_ML`.

Новый runner `src/mlbotnav/visual_entry_passport_family_runner.py` проверил no-lookahead семейства по v3-разметке `2026-05-12`: `DEEP_CAPITULATION_NEXT_OPEN`, `SUPPORT_WICK_REVERSAL_NEXT_OPEN`, `DIVERGENCE_AT_SUPPORT_NEXT_OPEN`, `CHOCH_REENTRY_AFTER_BOTTOM_NEXT_OPEN`, `VPOC_RANGE_RECLAIM_NEXT_OPEN`.

Новый overlay показывает `S/E` ручной разметки, `CS` кандидатного сигнала, `H` попадания и ярко-красный `FALSE/X` лишнего входа.

Главный аудит: `reports/final_review/visual_entry_v3/passport_family_runner/visual_entry_passport_family_audit_20260625_RU.md`.

Лучший результат: `DEEP_CAPITULATION_NEXT_OPEN`, `1/11` hits, `20` false, `21` entries, `f1=0.0625`. Это не кандидат. В ML ничего не передавать.

Следующий рабочий слой: `VISUAL_MICRO_BOTTOM_SIGNATURE_V0`, потому что текущие паспорта видят общую тему "дно/перепроданность", но не умеют отделить нужные ручные входы от частых локальных минимумов.

## Visual Entry v3 current state 2026-06-25
Текущий статус: `DEV_V3_ENTRY_ARROWS_READY_NO_CANDIDATE_NO_ML`.

Рабочая разметка v3 под пользовательский стиль создана на `2026-05-12`: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v3_user_entry_arrows/manual_entries.json`. Входы стоят на entry candle, сигнал считается предыдущей свечой, исполнение - следующий `open` + `5 bps`.

No-lookahead runner добавлен: `src/mlbotnav/visual_entry_no_lookahead_candidates.py`. Итоговый честный DEV результат слабый: лучший `UNION_ABC_NEXT_OPEN` дал `3/11`, `34` false. Это не кандидат и не ML.

## Visual Entry Calibration DEV-12 2026-06-25
Текущий статус: `DEV_DAY_MANUAL_ENTRIES_READY_SCORER_READY`.

Создан первый машинный `manual_entries.json` по пользовательскому PNG `2026-05-12`: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v1/manual_entries.json`.

Восстановленные LONG-цели: `01:44`, `04:15`, `09:12`, `12:36`, `15:34`, `17:05` UTC. Это предварительная расшифровка стрелок из PNG; при необходимости можно поправить минуты вручную.

Добавлен visual scorer: `src/mlbotnav/visual_entry_score.py`. Проверка `tests.test_visual_entry_score` прошла.

Первый результат по старому B001 CSV: `3/6` попаданий, `15` лишних входов, `precision=0.16666666666666666`, `recall=0.5`, `f1_visual=0.25`, `net_return_pct=-62.229358575198916`, статус `VISUAL_HITS_WITH_TOO_MANY_FALSE_ENTRIES`. Это diagnostic-only, ML не трогать.

## Visual Entry feature/pre-filter diagnostic 2026-06-25
Текущий статус: `DEV_DIAGNOSTIC_DONE_NEXT_SOLO_SCORER_AND_REVERSAL_FAMILY`.

Feature-аудит и prefilter-поиск завершены. План: `reports/qa_gate/visual_entry_candidate_family_plan_20260512_DEV_RU.md`.

Главный вывод: простые условия reversal/dip сами по себе слишком шумные. Следующий рабочий слой: diagnostic runner по существующим паспортам и новая `REVERSAL_DIP_BUY_LONG v0`.

## Visual Entry solo-passport diagnostic 2026-06-25
Текущий статус: `DEV_SOLO_PASSPORT_DIAGNOSTIC_DONE_NO_ML`.

Solo runner готов: `src/mlbotnav/visual_entry_solo_passport_runner.py`.

Отчет: `reports/final_review/visual_entry_solo_passport_runner_20260512_DEV_RU.md`.

Ключевые результаты DEV-дня `2026-05-12`:
1. `F009_EMAGAP_DOWN`: `2/6` hits, `6` false, `8` entries, `f1_visual=0.2857`;
2. `F059_ENGULFBULL`: `1/6` hits, `0` false, `1` entry, `f1_visual=0.2857`;
3. `F010_EMASLOPE_DOWN`: `2/6` hits, `16` false, `18` entries, `f1_visual=0.1667`;
4. `B001_RET_N_FIXED`: `5/6` hits, но `142` false, поэтому это шумный diagnostic, не кандидат.

Вывод: одиночные паспорта дают детали, но не готовую стратегию. Дальше нужен combo слой: контекст падения/растяжения (`F009`/EMA-down) + чистый reversal trigger (`F059` и родственные свечные признаки) + suppression от частых ложных входов. В ML ничего не передавать.

## Visual Entry Calibration TZ 2026-06-25
Текущий статус: `DESIGN_READY_WAITING_FOR_MARKUP`.

ТЗ: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_CALIBRATION_TZ_RU.md`.

Зафиксирован контур: три seed-графика уже готовы, дальше пользовательская разметка переводится в `manual_entries.json`, scorer считает попадания и ложные входы, затем паспорта и комбо проверяются сначала на DEV, потом на validation/holdout. В ML ничего не передавать без ручного review и `APPROVED_FOR_ML`.

## Visual Entry Calibration seed screenshots 2026-06-25
Текущий статус: `MANUAL_MARKUP_SEED_IMAGES_READY`.

Сгенерированы три скриншота для ручной разметки Visual Entry Calibration: `2026-05-12`, `2026-05-13`, `2026-05-14`, `SOLUSDT 1m`, `data_layer=core`.

Папка: `reports/manual_entries/SOLUSDT_1m_visual_seed_20260625`.

Критичная граница: эти картинки построены из тех же `core` свечей, которые должны быть источником для последующего backtest/Optuna/ML сравнения. Manifest фиксирует SHA256 каждого исходного CSV.

## B001 marked-entry fixed backtest 2026-06-25
Текущий статус: `MARKED_ENTRY_FIXED_BACKTEST_DONE_NEGATIVE`.

Аудит: `reports/qa_gate/b001_marked_entry_fixed_backtest_audit_20260625T073900Z_RU.md`.

Фиксированные пороги B001 `0.02 / 0.04 / 0.10 / 0.95 / 0.35` при `3/5` подтверждениях реально ловят `09:25` и `12:36` на OOS `2026-05-12`, но общий результат отрицательный: `-47.05387771496912%` при `18` сделках с `min_expected_move_pct=0.001` и `-67.41968770852606%` при `30` сделках без min-move.

`17:15` не вошел не из-за F-гейта: на `17:14` есть `4/5`, но `prob_up=0.3748`, ниже `p_enter_long=0.60`. `08:15` и `15:48` не проходят семейный F-гейт. В ML ничего не передавать.

## B001 marked-entry screenshot audit 2026-06-25
Текущий статус: `MARKED_ENTRY_AUDIT_DONE_DIAGNOSTIC_ONLY`.

Аудит: `reports/qa_gate/b001_marked_entry_screenshot_audit_20260625T070500Z_RU.md`.

Результат: текущая B001 `RET_N LONG` family может ловить отмеченные точки только там, где уже есть положительный возврат за последние `1/3/6/12/24` минут. Для ранних "покупок у дна" нужна отдельная reversal/dip-buy family.

## Shared-study profile-edge coverage fix 2026-06-25
Текущий статус: `PROFILE_EDGE_FORCING_FIXED_CONFIRMED`.

Аудит: `reports/qa_gate/shared_study_profile_edge_coverage_fix_20260625T063700Z_RU.md`.

Причина старых coverage warning закрыта в коде: профильные edge-пробы больше не сдвигаются на `profile_edge_worker_offset`, не расходуют edge slot до фактического profile sampling и распределяют min/max edge-задачи между process workers.

Проверки прошли: `py_compile`, `PSParser`, `tests.test_optuna_search_runtime` `73/73 OK`, `text_guard` `PASS`.

Runtime confirmation: `b001_3of5_long_shared_edgefix3_20260625_115056`, final snapshot `w3`: terminal `42/42`, core `5/5 PASS`, profile `7/7 PASS`, forced min/max полный `7/7`.

Старые и новые B001 LONG smoke результаты отрицательные/нулевые, в ML не передавать. Вопрос profile-edge coverage закрыт.

## B001 family-unified 3/5 LONG shared-study 2026-06-24
Текущий статус: `B001_3OF5_LONG_SHARED_DONE_NEGATIVE_EDGE_WARN`.

Аудит: `reports/qa_gate/b001_family_unified_3of5_long_shared_audit_20260624T195200Z_RU.md`.

Диагностический запуск `B001 family-unified 3/5 LONG` прошел на shared-study профиле `3x3/9`.

Факты:
1. `SharedOptunaStudy=true`;
2. `SharedStudyId=b001_3of5_long_shared_20260625T005102`;
3. storage preflight `postgresql`;
4. матрица `reports/qa_gate/b001_family_unified_long_3of5_shared_20260625T005102/B001_F001_F005_FAMILY_UNIFIED_long_3OF5.yaml`;
5. launcher `OK`;
6. best worker `w3`;
7. OOS `-2.0302055441506761`;
8. сделок `1`.

Решение: результат tradeful, но отрицательный. Это не кандидат, ML не трогать.

Ограничение результата: core edge coverage прошел `5/5`, profile edge coverage неполный `4/7`, failed profiles `F002_thr_pct`, `F003_thr_pct`, `F004_thr_pct`. Поэтому результат считать runtime diagnostic с coverage warning.

## Optuna shared-study process-pool 2026-06-24
Текущий статус: `OPTUNA_SHARED_STUDY_3X3_9_READY_NO_PROMOTION`.

Аудит: `reports/qa_gate/optuna_shared_study_process_pool_audit_20260624T190435Z_RU.md`.

Собран режим, где `w1/w2/w3` остаются тремя отдельными Python-процессами для нагрузки, но Optuna study у них общая. Это текущий правильный ответ на задачу "один общий поиск, но мощность как у трех worker".

Ключевые факты:
1. `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`, `OptunaTrials=42`.
2. Включение: `-SharedOptunaStudy -SharedStudyId <RUN_ID>`.
3. Shared study разрешена только на не-`sqlite` storage; проверено на `postgresql`.
4. Worker reports и Optuna artifacts получили worker suffix и не перетираются.
5. Trial-history rows получили worker context.
6. ML выключен: `ml_backend=off`, `decoupled_ml=true`.

Финальный smoke B001 `4/5 LONG` завершился инфраструктурно корректно, но результат отрицательный: OOS `-10.009351008800071`, сделок `2`. В ML ничего не передавалось.

## Optuna single-worker профиль 1x9/9 2026-06-24
Текущий статус: `OPTUNA_SINGLE_WORKER_1X9_9_READY`.

Профиль для одного мощного worker:
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=1`;
4. `SearchWorkersPerProcess=9`;
5. `OptunaTrials=42`.

Dry-run прошел: один worker получает всю мощность и одну Optuna-историю. CPU-нагрузка примерно равна прежнему `3x3/9`, память должна быть спокойнее из-за одного Python-процесса.

## B001 family unified 5/5 2026-06-24
Текущий статус: `B001_FAMILY_UNIFIED_5OF5_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_unified_5of5_audit_20260624T154700Z_RU.md`.

Теперь B001 может калиброваться как одно семейное звено через `B001_family_move`:
1. LONG family: `B001_family_move=1`.
2. SHORT family: `B001_family_move=-1`.
3. Отдельные `F001_move..F005_move` в unified-матрицах отсутствуют.
4. Калибруются только пороги `F001_thr_pct..F005_thr_pct` и подтверждение `entry_action_min_confirmations`.

Smoke strict `5/5` на `2026-05-11 -> 2026-05-12`: LONG и SHORT дали `0` сделок. Причина уже не конфликт направлений, а слишком жесткое совпадение всех пяти горизонтов.

В ML ничего не передавалось. Основной маршрут остается `B003.1 large LONG 2н/1н`.

## B001 family strict 5/5 smoke 2026-06-24
Текущий статус: `B001_FAMILY_STRICT_5OF5_SMOKE_DONE_ZERO_TRADES`.

Аудит: `reports/qa_gate/b001_family_strict_5of5_smoke_audit_20260624T153100Z_RU.md`.

Проверено семейное правило `5 из 5`: все `F001..F005` должны одновременно дать `ALLOW` на одной сигнальной свече. Runtime применил `and_all`.

Результат:
1. LONG: `0` сделок, `EMPTY_ACTION_GATE`, `985 / 573 / 0 / 0 / 0`.
2. SHORT: `0` сделок, `EMPTY_ACTION_GATE`, best OOS `0.0`, сделок `0`.

В ML ничего не передавалось. Основной маршрут остается `B003.1 large LONG 2н/1н`.

## B001_COMBO_DIAG визуальный аудит входов 2026-06-24
Текущий статус: `B001_COMBO_DIAG_GATE_VISUAL_AUDIT_DONE`.

Построены диагностические графики полного дня `2026-05-12`:
1. LONG: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_long_only_20260624T133243Z.png`.
2. SHORT: `reports/final_review/gate_diagnostic_SOLUSDT_1m_2026-05-12_short_only_20260624T133243Z.png`.

Счетчики совпадают с OOS runtime:
1. LONG: `mode=621`, `F-gate=4`, `min_move=4`, `trades=4`.
2. SHORT: `mode=637`, `F-gate=240`, `min_move=2`, `trades=2`.

Вывод: график не обрезан, сырой день полный. Узкая зона входов вызвана фильтрами, а не отсутствием свечей.

## B001_COMBO_DIAG N-of-M 2026-06-24
Текущий статус: `B001_COMBO_DIAG_N_OF_M_SMOKE_DONE_NO_CANDIDATE`.

Аудит: `reports/qa_gate/b001_combo_diag_n_of_m_audit_20260624T125500Z_RU.md`.

Зафиксировано правильное диагностическое действие: для совместной проверки `F001..F005` использовать `entry_action_min_confirmations` и политику `N из M`, а не старый жесткий `AND`.

Smoke 1д/1д на полной комбинации:
1. LONG: OOS `-8.498538882812346%`, `4` сделки, `N=1`.
2. SHORT: tradeful worker OOS `-6.055628696458093%`, `2` сделки, `N=1`.
3. Положительного кандидата нет, ML не тронут.

Основной маршрут остается `B003.1 large LONG 2н/1н`.

## B003 block route 2026-06-24
Текущий статус: `NEXT_B003_1_LARGE_LONG`.

Предыдущий блок `B002` закрыт итогом `B002.3`: `reports/qa_gate/b002_block_summary_b002_3_20260624T100800Z_RU.md`.

Решение по `B002`: LONG `NO_BLOCK_WINNER`; SHORT `NO_BLOCK_WINNER`; ML не тронут.

Следующий блок: `B003`, одиночный паспорт `F007 / F007_RSTD20_ALLOW`.

Активный worker-профиль: `3x3/9`.
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=3`;
4. `SearchWorkersPerProcess=3`.

Следующий строгий шаг: `B003.1 large LONG 2н/1н`, затем `B003.2 large SHORT 2н/1н`. В ML ничего не передавать.

## B002 block route 2026-06-24
Текущий статус: `B002_3_BLOCK_SUMMARY_CLOSED_NEXT_B003`.

Предыдущий блок `B001` закрыт итогом `B001.6`: `reports/qa_gate/b001_block_summary_b001_6_20260624T095800Z_RU.md`.

Решение по `B001`: LONG `F001 / F001_RET1_ALLOW` фиксируется как ручной положительный кандидат; SHORT `NO_BLOCK_WINNER`; ML не тронут.

Следующий блок: `B002`, одиночный паспорт `F006 / F006_HLSPREAD_ALLOW`.

Активный worker-профиль: `3x3/9`.
1. `Threads=9`;
2. `SearchWorkers=9`;
3. `ProcessWorkers=3`;
4. `SearchWorkersPerProcess=3`.

Откат на `2x3/6` допустим только при устойчивой перегрузке CPU/памяти или падении worker-процессов, с записью причины в аудите.

Следующий строгий шаг: `B002.1 large LONG 2н/1н`, затем `B002.2 large SHORT 2н/1н`. В ML ничего не передавать.

## B001.5 large SHORT 2026-06-24
Текущий статус: `B001_5_LARGE_SHORT_CLOSED_NO_BLOCK_WINNER`.

Аудит: `reports/qa_gate/b001_large_short_b001_5_audit_20260624T094057Z_RU.md`.

B001 SHORT на окне `2026-05-11..2026-05-24 -> 2026-05-25..2026-05-31` завершился `OK`, но без победителя.

Итог SHORT: `block_winner=null`; лучший доступный fallback `F004 / F004_RET12_ALLOW`, OOS `0.0`, сделок `0`, runtime `EMPTY_ACTION_GATE`. По OOS у всех `F001..F005` сделок `0`.

Входов/выходов в OOS нет. Train-сделки были у `F002` и `F003`; они зафиксированы в аудите как строки вход/выход/profit и не дают положительного блока.

Фикс терминального вывода: `APTuna/run_block_family_selection.ps1` теперь по умолчанию печатает краткую сводку, а не полный JSON. Полный JSON остается в файле отчета; `-EmitJson` включает машинный stdout.

Следующий строгий номер: `B001.6 итог блока LONG+SHORT`. В ML ничего не передавать.

## B001.4 large LONG 2026-06-24
Текущий статус: `B001_4_LARGE_LONG_PASS_WITH_WINNER`.

Аудит: `reports/qa_gate/b001_large_long_b001_4_audit_20260624T082051Z_RU.md`.

B001 LONG на окне `2026-05-11..2026-05-24 -> 2026-05-25..2026-05-31` завершился `OK`.

Победитель LONG: `F001 / F001_RET1_ALLOW`, OOS `+0.7322559143841945`, сделок `1`, runtime `TRADEFUL_POSITIVE`. Цель `1%` не достигнута, поэтому это положительный ручной кандидат блока, но не автоматический GO в ML.

Исторический следующий номер после этого раздела был `B001.5`; он уже закрыт. Актуальный следующий номер указан сверху: `B001.6 итог блока LONG+SHORT`.

## B001.3 smoke 1д/1д 2026-06-24
Текущий статус: `B001_3_SMOKE_AUDIT_PASS`.

Аудит: `reports/qa_gate/b001_smoke_1d1d_audit_20260624T075006Z_RU.md`.

Smoke проверил блок `B001` как семейство `F001..F005` на `SOLUSDT 1m core`, train `2026-05-11`, OOS `2026-05-12`.

Финальный LONG: `F001 / F001_RET1_ALLOW`, OOS `+2.404470760400401`, сделок `1`, `block_winner=F001`.

Финальный SHORT: лучший доступный `F002 / F002_RET3_ALLOW`, OOS `-0.3092010602366857`, сделок `1`, `block_winner=null`.

Технический smoke пройден. Следующий строгий номер: `B001.4 large LONG 2н/1н`. В ML ничего не передавать.

## Block-Family Route Correction 2026-06-24
Current status: `BLOCK_ROUTE_READY_FOR_B001`.

Audit: `reports/qa_gate/block_family_passport_route_audit_20260624T064900Z.md`.

Current route is block/family calibration, not a linear F-only route. Family blocks run all active solo F-passports in the block, then select one block winner or `NO_BLOCK_WINNER`. Single-passport blocks run through the same block runner with one passport.

Implemented runner: `APTuna/run_block_family_selection.ps1`, backed by `src/mlbotnav/block_family_manifest.py`.

Verified by dry-run: `B001` expands to `F001..F005` and writes block selection reports without ML promotion.

ML state: nothing from block calibration is passed into ML automatically. Final manual approval happens only after the full block route is complete and the user chooses positive blocks/candidates.

Next strict item: run `B001` block LONG, then `B001` block SHORT, sequentially.

## Min-Move Runtime Guard Fix 2026-06-24
Current status: `FIX_APPLIED_SUPERSEDED_BY_BLOCK_ROUTE`.

The route/runtime bug is fixed in code. `MIN_MOVE_UNREACHABLE` is now explicit in backtest/OOS diagnostics, fail-keyed and penalized in Optuna, skipped by adaptive selection when reachable alternatives exist, and the default 1m min-move grid is now `0.0,0.001,0.002,0.003`.

Validation before block-route correction: focused pytest `124 passed`; text_guard `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260624T063715Z.json`; readiness frozen as expected, report `reports/readiness/readiness_check_20260624T063714Z.json`.

Old next item `8.2.19 F068_PATTERNAGE_ALLOW` is superseded by the corrected block-family route.

## Zero-Trade Diagnostic 2026-06-24
Current status: `ROOT_CAUSE_FOUND`.
Artifact: `reports/qa_gate/ml_optuna_zero_trade_min_move_diagnostic_20260624T051535Z.md`.

The current Stage 8.2 zero-trade pattern has a confirmed common cause in non-empty-gate cases: `min_expected_move_pct` can be too high for the `exchange_like` proxy (`confidence * atr14 * sqrt(hold_bars)`) after action gates. F067 LONG is the clearest case: `1415` signals after gate, `0` after min-move because selected `0.01` is above the OOS proxy max `0.005140`.

Historical next pointer `8.2.19 F068_PATTERNAGE_ALLOW` is superseded by the corrected block-family route at the top of this file.

## Route Memory Audit 2026-06-23
Status: `ON_ROUTE`.

Audit: `reports/qa_gate/ml_optuna_route_memory_audit_20260623T205751Z.md`.

Current control audit after F067: `reports/qa_gate/ml_optuna_route_status_audit_after_f067_20260624T044311Z.md`.

Optuna/ML separation is intact. Current F050-F067 large-window results are not approved and must not be packaged, approved, or ingested into ML.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file.

Last updated UTC: 2026-06-23T22:57:00Z

## ML Optuna Calibration Stage 8.2.18 F067 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_18_f067_audit_20260623T225700Z.md`.

Stage 8.2.18 ran F067 Pattern Strength entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Historical next pointer `8.2.19 Run F068_PATTERNAGE_ALLOW large-window candidate` is superseded by the corrected block-family route at the top of this file.

## ML Optuna Calibration Stage 8.2.17 F066 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_17_f066_audit_20260623T224200Z.md`.

Stage 8.2.17 ran F066 OBV Bearish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.18 Run F067_PATTERNSTRENGTH_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.16 F065 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_16_f065_audit_20260623T223100Z.md`.

Stage 8.2.16 ran F065 OBV Bullish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.17 Run F066_OBVBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.15 F064 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_15_f064_audit_20260623T222100Z.md`.

Stage 8.2.15 ran F064 MACD Bearish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.16 Run F065_OBVBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.14 F063 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_14_f063_audit_20260623T221200Z.md`.

Stage 8.2.14 ran F063 MACD Bullish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.15 Run F064_MACDBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.13 F062 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_13_f062_audit_20260623T220200Z.md`.

Stage 8.2.13 ran F062 RSI Bearish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.14 Run F063_MACDBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.12 F061 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_12_f061_audit_20260623T215100Z.md`.

Stage 8.2.12 ran F061 RSI Bullish Divergence entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.13 Run F062_RSIBEARDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.11 F060 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_11_f060_audit_20260623T213900Z.md`.

Stage 8.2.11 ran F060 Bearish Engulfing entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.12 Run F061_RSIBULLDIV_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.10 F059 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_10_f059_audit_20260623T213000Z.md`.

Stage 8.2.10 ran F059 Bullish Engulfing entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.11 Run F060_ENGULFBEAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.9 F058 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_9_f058_audit_20260623T211900Z.md`.

Stage 8.2.9 ran F058 Shooting Star entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.10 Run F059_ENGULFBULL_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.8 F057 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_8_f057_audit_20260623T205000Z.md`.

Stage 8.2.8 ran F057 Hammer entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.9 Run F058_SHOOTINGSTAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.7 F056 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_7_f056_audit_20260623T203800Z.md`.

Stage 8.2.7 ran F056 Bearish Pin Bar entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.8 Run F057_HAMMER_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.6 F055 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_6_f055_audit_20260623T202700Z.md`.

Stage 8.2.6 ran F055 Bullish Pin Bar entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.7 Run F056_PINBEAR_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.5 F054 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_5_f054_audit_20260623T201700Z.md`.

Stage 8.2.5 ran F054 Inside Bar entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.6 Run F055_PINBULL_ALLOW large-window candidate`.

## ML Optuna Calibration Stage 8.2.4 F053 2026-06-23
Current status: `CLOSED_NO_GO_FIX_APPLIED`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_4_f053_audit_20260623T200600Z.md`.

Stage 8.2.4 ran F053 Doji entry filter on the large clean `core` window for both LONG and SHORT.

Final result: LONG OOS `0.0`, trades `0`; SHORT OOS `0.0`, trades `0`.

Fix applied: restored readiness freeze after a parallel `-UseTemporaryUnlock` race and added a guard to reject a second live temporary-unlock process-pool run before workers start.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.5 Run F054_INSIDEBAR_ALLOW large-window candidate`.

## ML Optuna Validation Stage 8.2.3 F052 2026-06-23
Current status: `CLOSED_VALIDATION_FAIL_NO_ML_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_3_f052_fixed_validation_audit_20260623T194700Z.md`.

Stage 8.2.3 validated fixed F052 CHOCH LONG params from the positive Stage 8.2.2 run on the adjacent clean `core` window.

Window: train `2026-05-04..2026-05-17`, OOS `2026-05-18..2026-05-24`.

Final result: train gate `false`; OOS `-5.696708101293968`; OOS trades `1`; OOS goal pass `false`; exit reason `timeout`.

Decision: no candidate package should be built from this validation; do not approve or ingest it into ML.

Final text_guard: `PASS`, report `reports/qa_gate/recovery_r5_text_guard_20260623T195125Z.json`.

Next strict WBS step: continue with the next user-selected passport/action discovery, or define a new validation idea.

## ML Optuna Calibration Stage 8.2.2 F052 2026-06-23
Current status: `CLOSED_POSITIVE_TEST_CANDIDATE_NEEDS_VALIDATION`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_2_f052_audit_20260623T193700Z.md`.

Stage 8.2.2 ran F052 CHOCH on the large clean `core` window for both LONG and SHORT.

Final result: LONG produced `1` OOS trade and `+5.3486475132039635`; SHORT produced `0` trades.

Caveat: LONG train gate failed and the only OOS trade exited by timeout.

Decision: no candidate package should be built automatically; ML training remains not started.

Next strict WBS step: manual decision on validation, draft package approval, or next passport/action discovery.

## ML Optuna Calibration Stage 8.2.1 F050 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_1_f050_audit_20260623T192700Z.md`.

Stage 8.2.1 ran F050 BOSUP on the large clean `core` window.

Final valid run: `long_only`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`, process pool `OK`, OOS trades `0`, OOS return `0.0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: `8.2.2 Run F052_CHOCH_ALLOW large-window candidate`, unless user overrides the target.

## ML Optuna Calibration Stage 8.2 2026-06-23
Current status: `CLOSED_NO_GO`.
Artifact: `reports/qa_gate/ml_optuna_large_clean_stage_8_2_audit_20260623T191900Z.md`.

Stage 8.2 ran F051 BOSDOWN on the large clean `core` window after fixing explicit data-layer propagation through launcher, adaptive runtime, Optuna/grid search, train, and OOS.

Final valid run: `short_only`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`, process pool `OK`, OOS trades `0`, OOS return `0.0`.

Decision: no candidate package should be built from this run; ML training remains not started.

Next strict WBS step: manual decision for next passport/action calibration target or revised `8.2` candidate run.

## ML Large Clean Window Stage 8.1 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_large_clean_window_stage_8_1_audit_20260623T185908Z.md`.

Stage 8.1 is closed: the large clean window is fixed in `configs/ml_large_clean_window_manifest.yaml`.

Window: `SOLUSDT 1m core`, train `2026-05-11..2026-05-24`, test `2026-05-25..2026-05-31`.

Audit: `PASS`, missing files `0`.

Boundary: Optuna calibration and ML training were not started.

Next strict WBS step: `8.2 Run Optuna calibration`.

## ML Smoke Bridge Stage 7 Closeout 2026-06-23
Current status: `STAGE_7_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_stage_7_closeout_20260623T185252Z.md`.

Stage 7 is closed: the smoke bridge from approved Optuna package into ML ingest dataset works end to end.

Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.

Rows total: `1177`.

Boundary: ML training was not started.

Next strict WBS step: `8.1 Fix large clean window`.

## ML Ingest Stage 7.5 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_ingest_stage_7_5_audit_20260623T184913Z.md`.

Stage 7.5 is closed: ML ingest assembled the approved smoke package into a dataset.

Dataset: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.csv`.

Dataset manifest: `reports/ml_datasets/smoke_stage_7_5_SOLUSDT_1m_20260527_short_only.manifest.json`.

Rows total: `1177`.

Boundary: ML training was not started.

Next strict WBS step: `7.6 Stage 7 closeout`.

## ML Approved Registry Stage 7.4 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_7_4_audit_20260623T184338Z.md`.

Stage 7.4 is closed: the smoke package is manually approved in `configs/ml_approved_calibration_packages.yaml`.

Registry approved count: `1`.

Approved package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Boundary: ML ingest/dataset builder was not run in this step, and ML training was not started.

Next strict WBS step: `7.5 Run ML ingest`.

## ML Smoke Package Contract Stage 7.3 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_smoke_package_contract_stage_7_3_audit_20260623T183430Z.md`.

Stage 7.3 is closed: the smoke package trade log satisfies the ML trade dataset contract and package alignment checks.

Package: `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Contract: `PASS`, rows `1177`, failed rows `0`, missing columns `0`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T183955Z.json`.

Registry remains empty: `approved_packages: []`.

Boundary: no ML training started, no ML ingest started, and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `7.4 Add package to approved registry`.

## ML Smoke Package Stage 7.2 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_smoke_package_stage_7_2_audit_20260623T183000Z.md`.

Stage 7.2 is closed: controlled smoke package exists at `reports/ml_candidates/smoke_SOLUSDT_1m_2026-05-27_short_only_20260623T182600Z`.

Package is `DRAFT` and `NO_GO_FOR_ML`; it is ready for `7.3` package contract audit, not ML ingest.

Registry remains empty: `approved_packages: []`.

Boundary: no ML training started, no ML ingest started, and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `7.3 Run package contract audit`.

## ML Smoke Window Stage 7.1 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_smoke_window_stage_7_1_audit_20260623T182242Z.md`.

Stage 7.1 is closed: the clean smoke window is selected and audited in `configs/ml_smoke_run_manifest.yaml`.

Window: `SOLUSDT 1m core`, train `2026-05-25..2026-05-26`, test `2026-05-27..2026-05-27`.

Real audit: `PASS`, report `reports/qa_gate/ml_smoke_window_manifest_audit_20260623T182159845644Z.json`.

Registry remains empty: `approved_packages: []`.

Boundary: no ML training started, no ML ingest started, and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `7.2 Build test package`.

## ML Alignment Stage 6 Closeout 2026-06-23
Current status: `STAGE_6_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_stage_6_closeout_20260623T181313Z.md`.

Stage 6 is closed: approved package alignment now has checks for run_id, passport context, calibration params, data windows, and admission status.

Current registry remains empty: `approved_packages: []`, approved count `0`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181511Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `7.1 Smoke run`.

## ML Alignment Admission Status Stage 6.5 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_admission_status_stage_6_5_audit_20260623T180946Z.md`.

The admission status auditor exists at `src/mlbotnav/ml_alignment_admission_status_audit.py`.

It fails packages unless registry entry, manifest, calibration package, and audit.md all agree on ML admission.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `121/121 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T181123Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.6 Stage 6 closeout`.

## ML Alignment Data Windows Stage 6.4 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_data_windows_stage_6_4_audit_20260623T154628Z.md`.

The data windows alignment auditor exists at `src/mlbotnav/ml_alignment_data_windows_audit.py`.

It fails packages when `manifest.json`, `trade_log.csv`, and package-local `source_reports/oos_report.json` disagree on `data_layer`, `train_start`, `train_end`, `test_start`, or `test_end`.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `115/115 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154759Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.5 Check admission status`.

## ML Alignment Calibration Params Stage 6.3 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_calibration_params_stage_6_3_audit_20260623T154114Z.md`.

The calibration params alignment auditor exists at `src/mlbotnav/ml_alignment_calibration_params_audit.py`.

It fails packages when `calibration_package.json.calibration_params`, `trade_log.csv.calibration_params_json`, and package-local `source_reports/oos_report.json.calibration_params` diverge.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `107/107 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T154240Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.4 Check data windows`.

## ML Alignment Passport Context Stage 6.2 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_passport_context_stage_6_2_audit_20260623T153614Z.md`.

The passport context alignment auditor exists at `src/mlbotnav/ml_alignment_passport_context_audit.py`.

It fails packages when `manifest.json`, `calibration_package.json`, and `trade_log.csv` disagree on `block_id`, `passport_id`, or `action_id`.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `100/100 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153741Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.3 Check calibration params`.

## ML Alignment Run ID Stage 6.1 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_alignment_run_id_stage_6_1_audit_20260623T152830Z.md`.

The run_id alignment auditor exists at `src/mlbotnav/ml_alignment_run_id_audit.py`.

It fails packages when `manifest.json.run_id`, `calibration_package.json.run_id`, and `trade_log.csv.run_id` do not match.

Current real registry result: `PASS / NO_APPROVED_PACKAGES`, packages total `0`, failed packages `0`.

Final focused tests: `94/94 OK`.

Text guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T153207Z.json`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Next strict WBS step: `6.2 Check passport context`.

## ML Stage 5 Closeout 2026-06-23
Current status: `STAGE_5_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_stage_5_closeout_20260623T152140Z.md`.

Stage 5 is closed: ML admission is separated from Optuna through manual registry, source policy, registry reader, dataset builder, and rejection reason log.

Current registry remains empty: `approved_packages: []`, approved count `0`.

Boundary: no ML training started and no package is `APPROVED_FOR_ML`.

Final text_guard: `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T152317Z.json`.

Next strict WBS step: `6.1 Check run_id alignment`.

## ML Rejection Reasons Stage 5.5 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_rejection_reason_log_stage_5_5_audit_20260623T151646Z.md`.

The rejection reason log builder exists at `src/mlbotnav/ml_rejection_reason_log.py`.

It writes machine-readable rejection reasons for unsuitable ML admission packages.

Current real reject-log result: `PASS / NO_REJECTIONS`, registry entries `0`, rejections `0`.

Final checks: registry validator `PASS`; reject-log smoke `PASS / NO_REJECTIONS` at `reports/qa_gate/ml_rejection_reason_log_20260623T151814362998Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151853Z.json`.

Next strict WBS step: `5.6 Stage 5 closeout`.

## ML Trade Dataset Assembly Stage 5.4 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approved_trade_dataset_builder_stage_5_4_audit_20260623T151002Z.md`.

The approved trade dataset builder exists at `src/mlbotnav/ml_approved_trade_dataset_builder.py`.

It builds a combined ML trade dataset only from packages exposed by `ml_approved_package_registry_reader`.

Current real builder result: `PASS / NO_APPROVED_PACKAGES`, approved packages `0`, rows total `0`, dataset path empty.

Final checks: registry validator `PASS`; builder smoke `PASS / NO_APPROVED_PACKAGES` at `reports/qa_gate/ml_approved_trade_dataset_builder_20260623T151131437464Z.json`; text_guard `PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T151207Z.json`.

Next strict WBS step: `5.5 Add rejection reasons`.

## ML Approved Package Registry Reader Stage 5.3 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approved_package_registry_reader_stage_5_3_audit_20260623T145833Z.md`.

The registry reader exists at `src/mlbotnav/ml_approved_package_registry_reader.py`.

It reads `configs/ml_approved_calibration_packages.yaml`, runs the registry validator, applies source-policy checks, and exposes only approved package metadata for the future dataset assembly step.

Current registry reader result: `PASS`, approved count `0`, packages exposed to ML `0`.

Final checks: registry validator `PASS`, `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260623T150511Z.json`.

Next strict WBS step: `5.4 Реализовать сборку ML dataset`.

## ML Ingest Source Policy Stage 5.2 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_ingest_source_policy_stage_5_2_audit_20260623T145342Z.md`.

The source-policy guard exists at `src/mlbotnav/ml_ingest_source_policy.py`.

Direct ML ingest from `reports/optuna`, `reports/pipeline`, and `reports/final_review` is denied by policy.

Allowed source classes are the approval registry and `reports/ml_candidates/<run_id>/...`.

Next strict WBS step: `5.3 Реализовать чтение registry`.

## ML Ingest Entry Point Stage 5.1 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_ingest_entrypoint_stage_5_1_audit_20260623T144832Z.md`.

The current primary ML training ingest entry point is `src/mlbotnav/pipeline_train_eval.py`.

The current orchestrators are `src/mlbotnav/prod_cycle.py`, `src/mlbotnav/stage_ladder.py`, and `src/mlbotnav/adaptive_auto_train.py`.

Current gap: approved registry is not read by training, and package trade logs are not assembled into an ML dataset yet.

Next strict WBS step: `5.2 Запретить прямое чтение Optuna reports`.

## ML Approval Registry Stage 4 Closeout 2026-06-23
Current status: `STAGE_4_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_5_closeout_20260623T144014Z.md`.

Stage 4 Manual ML Approval Registry is closed. The registry exists, the format and bans are recorded, and the validator returns `PASS` on the current empty registry.

Current registry state: `approved_packages: []`, approved count `0`.

No package has `APPROVED_FOR_ML`; ML ingest has not started.

Next strict WBS step: `5.1 Найти текущую точку ML ingest`.

## ML Approval Registry Stage 4.4 Validator 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_4_validator_audit_20260623T143510Z.md`.

Registry validator exists:
`src/mlbotnav/ml_approval_registry_validator.py`.

Real registry validation is `PASS` with approved count `0`.

Next strict WBS step: `4.5 Закрытие этапа 4`.

## ML Approval Registry Stage 4.3 Bans 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_3_bans_audit_20260623T142950Z.md`.

Registry bans are recorded in:
`configs/ml_approved_calibration_packages.yaml`.

The registry is still empty: `approved_packages: []`.

Next strict WBS step: `4.4 Сделать validator registry`.

## ML Approval Registry Stage 4.2 Format 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_2_format_audit_20260623T142545Z.md`.

Registry format is documented in:
`configs/ml_approved_calibration_packages.yaml`.

The registry is still empty: `approved_packages: []`.

Next strict WBS step: `4.3 Добавить запреты registry`.

## ML Approval Registry Stage 4.1 File 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_approval_registry_stage_4_1_create_file_audit_20260623T142205Z.md`.

Registry file exists:
`configs/ml_approved_calibration_packages.yaml`.

The registry is intentionally empty: `approved_packages: []`.

Next strict WBS step: `4.2 Описать формат registry`.

## ML Candidate Package Stage 3 Closeout 2026-06-23
Current status: `STAGE_3_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_7_closeout_20260623T141750Z.md`.

Candidate package is complete as a Stage 3 artifact:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`.

The package remains `DRAFT`; `audit.md` says `NO_GO_FOR_ML` until manual registry approval.

Next strict WBS step: `4.1 Создать registry файл`.

## ML Candidate Package Stage 3.6 Package Audit 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_6_package_audit_md_audit_20260623T141335Z.md`.

Package-local audit exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/audit.md`.

Audit says `NO_GO_FOR_ML` because the package remains `DRAFT`; it is ready for manual review, not ML ingest.

Next strict WBS step: `3.7 Закрытие этапа 3`.

## ML Candidate Package Stage 3.5 Manifest 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_5_manifest_audit_20260623T140720Z.md`.

Package-local manifest exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/manifest.json`.

Manifest is `DRAFT`; no ML approval has been granted.

Next strict WBS step: `3.6 Добавить audit.md`.

## ML Candidate Package Stage 3.4 Source Reports 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_4_source_reports_audit_20260623T135600Z.md`.

Package-local source report index exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports.json`.

Copied reports:
1. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/oos_report.json`.
2. `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/source_reports/pipeline_report.json`.

Optional `optuna_report.json`: `NOT_PROVIDED`.

Next strict WBS step: `3.5 Добавить manifest.json`.

## ML Candidate Package Stage 3.3 Trade Log 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_3_trade_log_audit_20260623T134809Z.md`.

Package-local trade log exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/trade_log.csv`.

Contract validation: `PASS`, `1177` rows, `0` failed rows, `0` missing columns.

Next strict WBS step: `3.4 Добавить исходные отчеты`.

## ML Candidate Package Stage 3.2 Calibration Package 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_2_calibration_package_audit_20260623T134307Z.md`.

Package file exists:
`reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z/calibration_package.json`.

The package remains `DRAFT`; no ML approval has been granted.

Next strict WBS step: `3.3 Добавить trade_log.csv`.

## ML Candidate Package Stage 3.1 Structure 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_candidate_package_stage_3_1_structure_audit_20260623T133735Z.md`.

Builder `src/mlbotnav/ml_candidate_package_builder.py` creates `reports/ml_candidates/<run_id>/` and validates safe `run_id` values.

Created package directory: `reports/ml_candidates/oos_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z`.

Next strict WBS step: `3.2 Добавить calibration_package.json`.

## ML Trade Dataset Stage 2 Closeout 2026-06-23
Current status: `STAGE_2_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_9_closeout_20260623T133249Z.md`.

Stage 2 is closed: pipeline trade CSV and OOS trade CSV pass `ml_trade_dataset_contract`.

Contract evidence:
1. Pipeline: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133238Z.json`.
2. OOS: `reports/qa_gate/ml_trade_dataset_contract_audit_20260623T133240Z.json`.

Next strict WBS step: `3.1 Создать структуру пакета`.

## ML Trade Dataset Stage 2.8 OOS CSV 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_8_oos_csv_audit_20260623T132830Z.md`.

Fresh OOS CSV `reports/final_review/oos_backtest_trades_SOLUSDT_1m_2026-05-27_short_only_20260623T132803Z.csv` passed contract validation with `1177` rows, `0` failed rows, and `0` missing columns.

OOS strategy result: `-0.9395906630311424%`, `3` trades, goal pass `false`.

Next strict WBS step: `2.9 Закрытие этапа 2`.

## ML Trade Dataset Stage 2.7 Pipeline CSV 2026-06-23
Current status: `CLOSED_PASS_AFTER_CONTROLLED_TEMP_UNLOCK`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_7_pipeline_csv_audit_20260623T131731Z.md`.

Pipeline layer handling is fixed: `pipeline_train_eval.py` accepts `--layer`, uses it in `load_ohlcv_range`, and writes it into the ML run context.

Fresh runtime validation completed through controlled temporary unlock. `reports/pipeline/backtest_trades_SOLUSDT_1m_20260623T132424Z.csv` passed contract validation with `2072` rows, `0` failed rows, and `0` missing columns.

Checks passed: changed module `py_compile PASS`; focused tests `59/59 OK`.

Next strict WBS step: `2.8 Проверить OOS CSV`.

## ML Trade Dataset Stage 2.6 MAE/MFE 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_6_mae_mfe_audit_20260623T131012Z.md`.

MAE/MFE labels are now added to pipeline and OOS trade CSV outputs before write. The shared helper emits `mae_pct` and `mfe_pct` for rows where `side != 0`; non-trade rows stay blank.

Checks passed: changed modules `py_compile PASS`; focused tests `59/59 OK`; `text_guard PASS`.

Next strict WBS step: `2.7 Проверить pipeline CSV`.

## ML Trade Dataset Stage 2.5 Hit Labels 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_5_hit_labels_audit_20260623T130320Z.md`.

Hit labels are now added to pipeline and OOS trade CSV outputs before write. Labels are derived from `exit_reason`.

Checks passed: changed modules `py_compile PASS`; focused tests `58/58 OK`; `text_guard PASS`.

Next strict WBS step: `2.6 Добавить MAE/MFE`.

## ML Trade Dataset Stage 2.4 Duration Labels 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_4_duration_labels_audit_20260623T125816Z.md`.

Duration labels are now added to pipeline and OOS trade CSV outputs before write. The shared helper emits `bars_in_trade` and `holding_seconds` for rows where `side != 0`.

Checks passed: changed modules `py_compile PASS`; focused tests `57/57 OK`; `text_guard PASS`.

Next strict WBS step: `2.5 Добавить hit labels`.

## ML Trade Dataset Stage 2.1 Run Context 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_1_run_context_audit_20260623T123600Z.md`.

Run-level context is now added to pipeline and OOS trade CSV outputs before write. The shared helper is `src/mlbotnav/ml_trade_dataset_enrichment.py`.

Checks passed: changed modules `py_compile PASS`; focused ML contract/enrichment tests `5/5 OK`; pipeline/backtest focused tests `48/48 OK`.

Next strict WBS step: `2.2 Добавить passport context`.

## ML Trade Dataset Contract Stage 1 Closeout 2026-06-23
Current status: `STAGE_1_CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_contract_stage_1_closeout_20260623T123000Z.md`.

Stage 1 is closed: the ML trade dataset contract exists, required columns are fixed, `APPROVED_FOR_ML` admission is documented, and the validator/test/CLI smoke path passes.

Current boundary: the contract is ready, but actual trade CSV enrichment starts next. No larger Optuna-to-ML calibration/OOS route should run before Stage 2 fields are emitted and audited.

Next strict WBS step: `2.1 Добавить run-level context`.

## ML Trade Dataset Contract Step 1.6 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_contract_step_1_6_audit_20260623T122406Z.md`.

The project now has an executable ML trade dataset contract validator at `src/mlbotnav/ml_trade_dataset_contract.py`.

It validates the current contract columns and row rules before a trade CSV can be treated as ML-ready. The validator writes JSON audit reports under `reports/qa_gate/ml_trade_dataset_contract_audit_*.json`.

Checks passed: `py_compile PASS`, focused unittest `4/4 OK`, CLI smoke `PASS`.

Next strict WBS step: `1.7 Закрытие этапа 1`.

## Optuna / ML / Entry / Exit Alignment Audit 2026-06-23
Current status: `PASS_WITH_ML_DATASET_GAPS`.
Artifact: `reports/qa_gate/optuna_ml_entry_exit_alignment_audit_20260623T162411Z.md`.
Action plan: `docs/CALIBRATION_NODE_CURRENT/ML_OPTUNA_SEPARATE_CONTOURS_ACTION_PLAN_RU.md`.
Budget: `10-14 hours` engineering work, excluding long runtime waiting.

The current code path correctly carries `calibration_params` from Optuna into train/OOS/backtest and isolates F051 through `F051_BOSDOWN_ALLOW`.

The current report contract is not ML-ready yet: CSV outputs need row-level `action_id`, `passport_id`, `block_id`, `calibration_params_json`, plus trade labels `trade_id`, `bars_in_trade`, `tp_hit`, `sl_hit`, `timeout_hit`, `mae_pct`, and `mfe_pct`.

Clean candle layer for the next larger test is `core` through `2026-05-31`; `2026-06-01` is raw/quarantine only and incomplete.

## Passport Block Registry 2026-06-22T12:57:27Z
`configs/calibration_action_passports.yaml` is the active registry for the new passport-driven calibration route.
Structure is fixed as block ids `B001`, `B002`, ... with Russian block names and technical `block_key`; feature/action passports live inside each block as `F001`, `F002`, ...
Current `B001` is the first passport block with active `RET_N` solo passports `F001-F005`.
Current `B002` is the second passport block `Диапазон свечи High-Low` with active passport `F006`.
`B001_RET_N_TOURNAMENT` remains diagnostic-only after the 2026-06-22 run; baseline mode is solo feature selection only.
Do not use old full/catalog/feature_sweep matrices for new baseline runs unless a passport explicitly migrates that action.

## F006 Passport Run 2026-06-22T13:10:45Z
F006 `hl_spread_1m` is implemented under `B002` with runtime column `F006_HLSPREAD_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `35/35 OK`, py_compile `PASS`.
Clean direct LONG contour result: selected `F006_cmp=-1` (`LESS`), `F006_thr_pct=0.75`; OOS `-6.153363933968025%`, trades `2`, wins `0`; decision `NO_GO`.
Audit artifact: `reports/qa_gate/f006_hl_spread_long_only_audit_20260622T131045Z.json`.
Note: the initial 3-worker pool run had a same-second final_review/top-card artifact mismatch, so use the clean direct contour artifact for the final F006 result.

## F007 Passport Run 2026-06-22T13:33:18Z
F007 `rolling_std_20_1m` is implemented under `B003` with runtime column `F007_RSTD20_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `37/37 OK`, py_compile `PASS`.
Clean direct LONG result: `F007_cmp=1` (`GREATER`), `F007_thr_pct=0.04`; OOS `-1.1459443803135683%`, trades `1`, wins `0`; decision `NO_GO`.
Clean direct SHORT result: `F007_cmp=-1` (`LESS`), `F007_thr_pct=0.34`; OOS `-5.744959575084807%`, trades `3`, wins `0`; decision `NO_GO`.
Audit artifact: `reports/qa_gate/f007_rolling_std20_long_short_audit_20260622T133318Z.json`.

## F008 Passport Run 2026-06-22T13:59:47Z
F008 `atr14_1m` is implemented under `B004` with runtime column `F008_ATR14_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `39/39 OK`, py_compile `PASS`.
Clean direct LONG result: `F008_cmp=-1` (`LESS`), `F008_thr_pct=0.28`; OOS `-1.1459443803135683%`, trades `1`, wins `0`; decision `NO_GO`.
Clean direct SHORT result: `F008_cmp=-1` (`LESS`), `F008_thr_pct=2.33`; OOS `-5.744959575084807%`, trades `3`, wins `0`; decision `NO_GO`.
Audit artifact: `reports/qa_gate/f008_atr14_long_short_audit_20260622T135947Z.json`.

## EMA F009-F011 Passport Run 2026-06-22T14:34:20Z
EMA family passports are implemented under `B005` with runtime columns `F009_EMAGAP_ALLOW`, `F010_EMASLOPE5_ALLOW`, and `F011_EMA200GAP_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `41/41 OK`, py_compile `PASS`.
Clean direct results: F009 LONG `0%/0 trades`; F009 SHORT `-18.167609882040235%/9 trades`; F010 LONG `-29.10662198785241%/10 trades`; F010 SHORT `-18.617757232213172%/5 trades`; F011 LONG `0%/0 trades`; F011 SHORT `0%/0 trades`.
Decision: `NO_GO`, no tradeful non-negative candidate.
Audit artifact: `reports/qa_gate/ema_f009_f011_long_short_audit_20260622T143420Z.json`.

## F012 RSI14 Passport Run 2026-06-22T14:47:50Z
F012 `rsi14_1m` is implemented under `B006` with runtime column `F012_RSI14_ALLOW`.
Checks passed: matrix compile `PASS`, focused tests `43/43 OK`, py_compile `PASS`, `text_guard PASS`.
Clean LONG result: `LEVEL/GREATER/level=88`, OOS `0%`, trades `0`, decision `NO_GO`.
SHORT result: `LEVEL/GREATER/level=30`, OOS `-47.5754123715459%`, trades `22`, wins/losses by net return `1/21`, all exits `timeout`, decision `NO_GO`.
Audit artifact: `reports/qa_gate/f012_rsi14_combined_long_short_audit_20260622T144750Z.json`.

## F017/F018 Combined Decision 2026-06-23T08:10:00Z
`F017/F018` split-vs-combined audit finding is closed.
Decision: keep one combined Stochastic K/D passport `F017_F018` with runtime gate `F017_F018_STOCH14_ALLOW`.
Reason: `%K` and `%D` are two lines of one Stochastic indicator; `KD_CROSS` requires both lines in one action grammar.
This is not old Optuna feature mixing and not a block-combo tournament.
Artifact: `reports/qa_gate/f017_f018_combined_decision_audit_20260623T081000Z.md`.
Next strict audit hardening item: explicit active-action filtering so stale `F*_ALLOW` columns cannot affect backtest/OOS.

## Stale Action Column Hardening 2026-06-23T08:20:00Z
Backtest/OOS stale action-column risk is fixed for the passport route.
`run_prob_backtest` now supports `active_entry_action_columns`; Optuna passport search passes the current `passport_mode.action_id`; if only calibration params are available, backtest infers the active action from `Fxxx_*` passport params.
Regression test confirms stale `F038_RANGEPOSE_ALLOW` is ignored when F039 params/action are active.
Validation: changed modules `py_compile PASS`; focused stale/F039 tests `2/2 OK`; project venv `tests.test_backtest_fields tests.test_optuna_search_runtime` `110/110 OK`; `text_guard PASS` `reports/qa_gate/recovery_r5_text_guard_20260623T081355Z.json`.
Artifact: `reports/qa_gate/stale_action_column_hardening_20260623T082000Z.md`.

## Passport Control Index 2026-06-23T08:41:37Z
Active control index created: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_CONTROL_INDEX_RU.md`.
It is a human control panel, not an executable Optuna config.
Accepted architecture: passport meaning docs, compact registry contract, separate executable matrices, and QA artifacts.
Next route proposal: `F051 SHORT` validation is complete and failed promotion; choose the next passport/feature route or define a new validation idea.
Audit: `reports/qa_gate/passport_control_index_audit_20260623T084500Z.md`.

## Active Calibration Source Override
Active calibration-node work now lives in `docs/CALIBRATION_NODE_CURRENT/`.
Use that folder as the next-task source. Do not derive current calibration tasks from old chronology, old journals, old TZ files, or old P20xx/P21xx chains.

## Optuma Bridge Current Step
`docs/CALIBRATION_NODE_CURRENT/TZ_OPTUMA_BRIDGE_CURRENT_2026-06-04_RU.md` is the active short rule for current Optuma repairs.
Completed Step 1: `calibration_params` selected by Optuna are now passed into train/OOS and saved in reports/model payload.
Completed Steps 2-5: `volume_flow`, `density_profile`, `structure_ta` thresholds, and FIBO profile wiring are repaired against the declared calibration params.
Completed pattern repair: `pattern_structure_volume_entry` adds classic figure-pattern runtime features and the `pattern + structure_ta + volume_flow` entry bundle.
Validation: focused tests `97/97 OK`; changed modules `py_compile PASS`; matrix compile audit `PASS` for 7 YAML matrices x 2 contours x 3 grid presets; latest `text_guard PASS`.
Dry command gate passed, then `pattern long_only narrow` completed OK under CPU limit.
`pattern long_only medium` completed launcher/workers OK but exceeded the CPU limit once: max CPU `97%` vs limit `85%`.
User clarified CPU policy: short spikes are acceptable; sustained `>85%` for `2-5` minutes means reduce profile and continue.
`pattern` block full runtime is now closed through `long_only` and `short_only`, each `narrow/medium/wide`.
Result: `BLOCK_COMPLETE_RUNTIME_OK_NO_CANDIDATE`; best `long_only narrow`, `0%`, trades `0`; block artifact `reports/qa_gate/pattern_block06_full_closeout_20260604T103051Z.json`.
Readable report: `reports/qa_gate/pattern_block06_human_readable_20260604T103051Z_RU.md`.
New finding: search-level candidates include calibrated params, but final fallback `best_oos` records `selected_calibration_params={}`. Treat this as the next calibration-node repair before relying on parameter-specific block06 replay.
Repair completed UTC `2026-06-04T10:43:12Z`: `adaptive_auto_train.py` now prefers full `top_candidates` with `calibration_params` over lite candidates. Focused tests `80/80 OK`; artifact `reports/qa_gate/pattern_fallback_calibration_params_fix_20260604T104312Z_RU.md`. Next step is rerun/replay block06 so new runtime artifacts include `selected_calibration_params`.

## APTuna Block Alignment Audit 2026-06-03T16:48:08Z
Artifact: `reports/qa_gate/aptuna_block_alignment_audit_20260603T164808Z.json`.
Status: `PASS`, `issues=0`, `blockers=0`.
All 6 blocks match between calibrated blocks and APTuna matrices: `price_volatility`, `trend_momentum`, `volume_flow`, `density_profile`, `structure_ta`, `pattern`.
Full matrix contains `68` feature rows (`56` calibratable, `12` fixed) and `20/20` calibratable hypothesis rows.
Catalog block matrices compile for `long_only`/`short_only` and `narrow`/`medium`/`wide`; APTuna uses the matrix path through `MLBOTNAV_CALIBRATION_MATRIX_PATH`.
Next strict sequential step remains `H003` matrix generation/compile.

## Current Sweep State 2026-06-03T13:16:59Z
Active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_HYPOTHESIS_FEATURE_SWEEP_2026-06-03_RU.md`.
Slot `H001` is complete: `long_only` and `short_only` each ran `narrow/medium/wide` with launcher `OK`, workers `3/3 exit_code=0`, no infra failure.
H001 best long: `medium long_only`, `-8.650246602184342%`, trades `4`.
H001 best short: `narrow short_only`, `0%`, trades `0`.
Candidate decision: `NO_CANDIDATE`; runtime/grid coverage is OK.
Closeout artifact: `reports/qa_gate/h001_slot_closeout_20260603T131659Z.json`.
Sweep table: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`, H001 status `slot_complete_runtime_ok_no_candidate_next_H002`.
Next strict action: `H002` matrix compile, then `H002 long_only` full stack.

## Human-Readable Sweep Format 2026-06-03T13:30:00Z
Accepted format: one parent slot plus two child stack cards.
Example: `H001` is the parent feature slot, `H001-LONG` is the long-only stack, `H001-SHORT` is the short-only stack, and `H001-SLOT` is the closeout.
`H002` remains the next feature slot, not a short-side alias.
Readable reports should be in Russian and include block/tool meaning, technical name, calibrated params, ranges, all grid results, best long/short, decision, and artifact path.
Heading correction: each slot heading must be short and use exact RU names from `configs/features_block.yaml`, for example `H003 | Доходность за 6 баров`; H003 is `kind=feature_row`, not a hypothesis.
Full RU names catalog: `docs/CALIBRATION_NODE_CURRENT/RU_NAMES_CATALOG_2026-06-03.md`.
Post-format-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260603T160749Z.json`.
Current readable report file: `reports/optuna_catalog/index/hypothesis_feature_sweep_human_ru.md`.

## Current Sweep State 2026-06-03T15:41:33Z
Slot `H002` is complete: `long_only` and `short_only` each ran `narrow/medium/wide` with launcher `OK`, workers `3/3 exit_code=0`, no infra failure.
H002 best long: `wide long_only`, `-8.650246602184342%`, trades `4`.
H002 best short: `narrow/medium short_only`, `-0.2662724500743341%`, trades `2`.
Candidate decision: `NO_CANDIDATE`; runtime/grid coverage is OK.
Closeout artifact: `reports/qa_gate/h002_slot_closeout_20260603T154133Z.json`.
Sweep table: `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`, H002 status `slot_complete_runtime_ok_no_candidate_next_H003`.
Next strict action: `H003` matrix compile, then `H003 long_only` full stack.

## Current Calibration Node Update 2026-06-03T11:28:24Z
`structure_ta` is closed as `CLOSED_RUNTIME_OK` in the active current folder.
Best block result: `structure_ta wide long_only`, OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production because train gate failed.
The failed first `wide short_only` attempt was infrastructure-only: one worker crashed on empty/unreadable OOS report JSON. The code now uses `_read_json_report_with_retry` for OOS report reads; retest returned launcher `OK`, workers `3/3 exit_code=0`, best OOS `0%`, trades `0`.
`pattern` is closed as `CLOSED_RUNTIME_OK`: `narrow/medium/wide` x `long_only/short_only` all returned launcher `OK` with workers `3/3 exit_code=0`.
Best `pattern` result: `wide long_only`, OOS `+1.5266529420731034%`, trades `1`, `TOP_EXPERIMENTAL`, not production because train gate failed.
Closeout artifact: `reports/qa_gate/calibration_node_pattern_closeout_20260603T112654Z.json`.
Checks after close: focused tests `83/83 OK`, text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T112958Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T112818Z.json`), `pip check PASS`.
Next active command is not production/unfreeze; it requires a separate new TZ or GO package.

## Current Sequential Sweep Update 2026-06-03T12:18:33Z
Current `TOP_EXPERIMENTAL` candidate is paused by user request.
Active work is now sequential min->max verification for every hypothesis/feature slot.
New active TZ: `docs/CALIBRATION_NODE_CURRENT/TZ_HYPOTHESIS_FEATURE_SWEEP_2026-06-03_RU.md`.
Inventory result: `69` logical slots (`H000` baseline/control plus `H001-H068` feature rows), `56` calibratable and `13` non-calibrated including control.
Artifacts:
1. `reports/qa_gate/hypothesis_feature_sweep_inventory_20260603T121643Z.json`
2. `reports/optuna_catalog/index/hypothesis_feature_sweep_table_20260603T121643Z.csv`
3. `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`
4. `reports/qa_gate/h001_feature_sweep_matrix_compile_20260603T121833Z.json`

`H001 narrow long_only` completed: launcher `OK`, workers `3/3 exit_code=0`, best OOS `-30.924389997582892%`, trades `13`, class `negative_runtime_ok`.
Artifact: `reports/qa_gate/h001_narrow_long_only_20260603T122520Z.json`.
TZ corrected: long and short are separate stacks; each stack runs `narrow -> medium -> wide`; standard profile is `3x3/9` with trials/timeouts `narrow=60/300`, `medium=120/600`, `wide=180/900`.
`H001 narrow short_only` completed: launcher `OK`, workers `3/3 exit_code=0`, best OOS `+0.2544418318741748%`, trades `1`, class `provisional_plus_goal_fail`, not candidate.
Artifact: `reports/qa_gate/h001_narrow_short_only_20260603T124931Z.json`.
Next active command: `H001 medium long_only` 1d->1d, then record the result and move to `H001 medium short_only`.

## Works
1. Optuna/APTuna runtime contour is usable.
2. Long/short split works.
3. Process-pool launcher works.
4. Temporary readiness unlock works for calibration.
5. Preflight and artifact emission work.
6. Package-level `text_guard`, readiness check, `pip check`, and encoding audit passed after `Package A`.
7. Existing Optuna coverage contour supports linked profile coverage audits.
8. Catalog folders exist under `reports/optuna_catalog/`.

## Does Not Work For Launch Yet
1. No portable launch candidate exists.
2. Prior cycle-2 local candidate failed mandatory forward stability.
3. `Package A` V3 found no candidate.
4. Production launch is blocked by current `NO_GO` and freeze.
5. Full catalog runner/index emission is not implemented yet for the new catalog workflow.
6. A positive catalog result still needs forward validation before production.

## Checked
1. `P2016`: forward stability final fail after UTC close.
2. `P2017`: final quality decision switched to `NO_GO`.
3. `P2022`: `Package A long_only` completed.
4. `P2023`: `Package A short_only` completed.
5. `P2024`: unified triage returned `NO_CANDIDATE`.
6. `P2025`: post-audit returned `PASS`.
7. `P2026`: full calibration catalog checkpoint created.
8. `P2028`: first catalog task fixed as `1d -> 1d` calibration smoke strategy; no runtime run was launched.
9. `P2029`: ordered execution roadmap fixed; current pointer is Step 1 read-only wiring inventory.
10. `P2030`: Step 1 wiring inventory completed with `PASS`; current pointer moved to Step 2.
11. `P2031`: Step 1 post-sync audit passed; readiness freeze preserved.
12. `P2032`: Step 2 1d->1d smoke command set completed with `PASS`; current pointer moved to Step 3.
13. `P2033`: Step 2 post-sync audit passed; readiness freeze preserved.
14. `P2034`: Step 3 smoke preflight completed with `PASS`.
15. `P2035`: Step 4 long_only smoke completed `NEUTRAL_NO_TRADE`.
16. `P2036`: Step 5 short_only smoke completed `PROVISIONAL_PLUS_GOAL_FAIL`.
17. `P2037`: Step 6 smoke triage returned `GO_TO_MEDIUM_WORK`; current pointer moved to Step 7.
18. `P2038`: Step 6 post-sync audit passed; readiness freeze preserved.
19. `P2039`: Step 7 medium command set completed with `PASS`; current pointer remains Step 7 runtime.
20. `P2040`: Step 7 medium long_only completed as `negative`.
21. `P2041`: Step 7 medium short_only completed as `negative`.
22. `P2042`: Step 7 medium triage returned `GO_TO_WIDE_BATTLE`; current pointer moved to Step 8.
23. `P2043`: Step 7 medium post-sync audit passed; readiness freeze preserved.
24. `P2044`: Step 8 wide command set completed with `PASS`; current pointer remains Step 8 runtime.
25. `P2045`: Step 8 wide long_only completed as `negative`.
26. `P2046`: Step 8 wide short_only completed as `negative`.
27. `P2047`: Step 8 wide triage returned `GO_TO_CATALOG_RANKING`.
28. `P2048`: Step 9 catalog ranking returned `NO_FORWARD_CANDIDATE`.
29. `P2049`: Step 10/11 boundary returned `NO_FORWARD_CANDIDATE_NO_PRODUCTION_GO`.
30. `P2050`: full catalog closeout post-sync audit passed; readiness freeze preserved.
31. `P2051`: block-level catalog cycle setup completed with `PASS`; 6 block-isolated matrices generated and compiled.
32. `P2052`: block01 `price_volatility` narrow command set completed with `PASS`; current pointer is block01 narrow runtime.
33. `P2055`: block01 narrow triage returned `GO_TO_BLOCK01_MEDIUM`.
34. `P2059`: block01 medium triage returned `GO_TO_BLOCK01_WIDE`.
35. `P2063`: block01 full triage returned `GO_TO_BLOCK02_TREND_MOMENTUM`.
36. `P2064`: block01 post-sync audit passed; readiness freeze preserved.
37. `P2065`: block02 `trend_momentum` narrow command set completed with `PASS`.
38. `P2068`: block02 narrow triage returned `GO_TO_BLOCK02_MEDIUM`.
39. `P2069`: block02 `trend_momentum` medium command set completed with `PASS`.
40. `P2072`: block02 medium triage returned `GO_TO_BLOCK02_WIDE`.
41. `P2073`: block02 `trend_momentum` wide command set completed with `PASS`.
42. `P2076`: block02 full triage returned `GO_TO_BLOCK03_VOLUME_FLOW`.
43. `P2077`: block02 post-sync audit passed; readiness freeze preserved.
44. `P2078`: block03 `volume_flow` narrow command set completed with `PASS`.
45. `P2081`: block03 narrow triage returned `GO_TO_BLOCK03_MEDIUM_WITH_FORWARD_CANDIDATE_OBSERVED`.
46. `P2082`: block03 `volume_flow` medium command set completed with `PASS`.
47. `P2085`: block03 medium triage returned `GO_TO_BLOCK03_WIDE_WITH_NARROW_FORWARD_CANDIDATE_PRESERVED`.
48. `P2086`: block03 `volume_flow` wide command set completed with `PASS`.
49. `P2089`: block03 full triage returned `GO_TO_BLOCK04_DENSITY_PROFILE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
50. `P2090`: block03 post-sync audit passed; readiness freeze preserved.
51. `P2091`: block04 `density_profile` narrow command set completed with `PASS`.
52. `P2094`: block04 narrow triage returned `GO_TO_BLOCK04_MEDIUM_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
53. `P2095`: block04 `density_profile` medium command set completed with `PASS`.
54. `P2098`: block04 medium triage returned `GO_TO_BLOCK04_WIDE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
55. `P2099`: block04 `density_profile` wide command set completed with `PASS`.
56. `P2102`: block04 full triage returned `GO_TO_BLOCK05_STRUCTURE_TA_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
57. `P2103`: block04 post-sync audit passed; readiness freeze preserved.
58. `P2104`: block05 `structure_ta` narrow command set completed with `PASS`.
59. `P2107`: block05 narrow triage returned `GO_TO_BLOCK05_MEDIUM_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
60. `P2108`: block05 `structure_ta` medium command set completed with `PASS`.
61. `P2111`: block05 medium triage returned `GO_TO_BLOCK05_WIDE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
62. `P2112`: block05 `structure_ta` wide command set completed with `PASS`.
63. `P2115`: block05 full triage returned `GO_TO_BLOCK06_PATTERN_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
64. `P2116`: block05 post-sync audit passed; readiness freeze preserved.
65. `P2117`: block06 `pattern` narrow command set completed with `PASS`.
66. `P2120`: block06 narrow triage returned `GO_TO_BLOCK06_MEDIUM_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
67. `P2121`: block06 `pattern` medium command set completed with `PASS`.
68. `P2124`: block06 medium triage returned `GO_TO_BLOCK06_WIDE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
69. `P2125`: block06 `pattern` wide command set completed with `PASS`.
70. `P2128`: block06 full triage returned `GO_TO_BLOCK_LEVEL_CATALOG_RANKING_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
71. `P2129`: block06 post-sync audit passed; readiness freeze preserved.
72. `P2130`: block-level catalog ranking returned `FORWARD_CANDIDATE_EXISTS_RUN_FORWARD_STABILITY`.
73. `P2131`: forward boundary confirms production is still blocked; F1/F2 required.
74. `P2132`: block-level catalog closeout post-sync audit passed; readiness freeze preserved.
75. `P2133`: exact F1/F2 command set prepared for candidate `P2079`; command syntax dry-run passed for 3x3 contour, but runtime is `BLOCKED_BY_DATA`.
76. `P2134`: repeated F1/F2 data preflight gate; status `BLOCKED_BY_UTC_CLOSE_AND_DATA`.
77. `P2137`: previous V3 TZ pointer restored. Exact V3 `Package B` slot definition is the unclosed manual branch; P2079 forward automation is paused.
78. `P2138`: previous TZ recovery post-sync audit passed; `text_guard`, readiness, and `pip check` are clean and freeze remains ON.
79. `P2139`: dated Package B step chain fixed. Chain starts UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`, from V3 TZ section 7 (`2026-06-02T06:52:50Z`).
80. `P2139 independent cross-check`: agent and local audit agree route is correct with boundary: next step is read-only `P2140 inventory`, not runtime or P2079 forward.
81. `P2140`: Step 1 inventory completed with `PASS`; current V3 Package B slots/matrices/command set are not defined, old Package B artifacts are historical V2/strict only.
82. `P2141`: Step 2 exact V3 Package B slots completed with `PASS`; slots B-H1 trend/momentum, B-H2 range/reversion, B-H3 flow/absorption are fixed; runtime still blocked.
83. `P2142`: Step 3 matrix slices and command-set/dry-run completed with `PASS`; 4 Package B matrix slices generated, 18 exact commands emitted, dry-run/preflight `18/18 PASS`; next is `P2143 long_only` runtime only.
84. `P2143`: Step 4 Package B `long_only` runtime completed with `PASS`; runtime `9/9 PASS`, catalog class `neutral`, accepted positive candidates `0`; next is `P2144 short_only` runtime only.
85. `P2144`: Step 5 Package B `short_only` runtime completed with `PASS`; runtime `9/9 PASS`, catalog class `neutral`, accepted positive candidates `0`; next is `P2145` unified Package B triage only.
86. `P2145`: Step 6 Package B unified triage completed as `NO_CANDIDATE`; totals positive `0`, neutral `18`, negative `0`, infra_fail `0`; next is `P2146` post-sync audit/docs sync.
87. `P2146`: Step 7 Package B post-sync audit completed with `PASS`; text_guard/readiness/pip/artifact parse clean, readiness freeze preserved; next is `P2147` transition decision.
88. `P2147`: Step 8 Package B closeout transition completed with `PASS`; decision `GO_TO_FINAL_V3_NO_GO_DECISION_PACKAGE`; no next runtime allowed from Package B.
89. `P2148`: final V3 `NO_GO` decision package completed; launch `NO_GO`, no production-ready candidate, launch/unfreeze blocked; next is `P2149` final post-sync audit.
90. `P2149`: final V3 `NO_GO` post-sync audit completed with `PASS`; V3 chain closed, readiness freeze preserved.
91. `P2150`: post-V3 catalog/forward boundary selected P2079 F1 data gate after UTC close; status `ROUTE_SELECTED_WAIT_UTC_CLOSE`; no ingest, preflight, runtime, production, or unfreeze allowed now.
92. `P2151`: P2079 F1 data gate pre-close check completed as `BLOCKED_BY_UTC_CLOSE`; next `P2152` waits until `2026-06-03T00:00:00Z`.
93. `P2152`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2153` waits until `2026-06-03T00:00:00Z`.
94. `P2153`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2154` waits until `2026-06-03T00:00:00Z`.
95. `P2154`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2155` waits until `2026-06-03T00:00:00Z`.
96. `P2155`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2156` waits until `2026-06-03T00:00:00Z`.
97. `P2155` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
98. `P2156`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2157` waits until `2026-06-03T00:00:00Z`.
99. `P2156` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
100. `P2157`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2158` waits until `2026-06-03T00:00:00Z`.
101. `P2157` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
102. `P2158`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2159` waits until `2026-06-03T00:00:00Z`.
103. `P2158` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
104. `P2159`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2160` waits until `2026-06-03T00:00:00Z`.
105. `P2159` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
106. `P2160`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2161` waits until `2026-06-03T00:00:00Z`.
107. `P2160` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
108. `P2161`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2162` waits until `2026-06-03T00:00:00Z`.
109. `P2161` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
110. `P2162`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2163` waits until `2026-06-03T00:00:00Z`.
111. `P2162` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
112. `P2163`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2164` waits until `2026-06-03T00:00:00Z`.
113. `P2163` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
114. `P2164`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2165` waits until `2026-06-03T00:00:00Z`.
115. `P2164` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
116. `P2165`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2166` waits until `2026-06-03T00:00:00Z`.
117. `P2165` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
118. `P2166`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2167` waits until `2026-06-03T00:00:00Z`.
119. `P2166` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
120. `P2167`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2168` waits until `2026-06-03T00:00:00Z`.
121. `P2167` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
122. `P2168`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2169` waits until `2026-06-03T00:00:00Z`.
123. `P2168` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
124. `P2169`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2170` waits until `2026-06-03T00:00:00Z`.
125. `P2169` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
126. `P2170`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2171` waits until `2026-06-03T00:00:00Z`.
127. `P2170` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
128. `P2171`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2172` waits until `2026-06-03T00:00:00Z`.
129. `P2171` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
130. `P2172`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2173` waits until `2026-06-03T00:00:00Z`.
131. `P2172` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
132. `P2173`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2174` waits until `2026-06-03T00:00:00Z`.
133. `P2173` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
134. `P2174`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2175` waits until `2026-06-03T00:00:00Z`.
135. `P2174` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
136. `P2175`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2176` waits until `2026-06-03T00:00:00Z`.
137. `P2175` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
138. `P2176`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2177` waits until `2026-06-03T00:00:00Z`.
139. `P2176` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
140. `P2177`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2178` waits until `2026-06-03T00:00:00Z`.
141. `P2177` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
142. `P2178`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2179` waits until `2026-06-03T00:00:00Z`.
143. `P2178` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
144. `P2179`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2180` waits until `2026-06-03T00:00:00Z`.
145. `P2179` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
146. `P2180`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2181` waits until `2026-06-03T00:00:00Z`.
147. `P2180` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
148. `P2181`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2182` waits until `2026-06-03T00:00:00Z`.
149. `P2181` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
150. `P2182`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2183` waits until `2026-06-03T00:00:00Z`.
151. `P2182` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
152. `P2183`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2184` waits until `2026-06-03T00:00:00Z`.
153. `P2183` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
154. `P2184`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2185` waits until `2026-06-03T00:00:00Z`.
155. `P2184` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
156. `P2185`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2186` waits until `2026-06-03T00:00:00Z`.
157. `P2185` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
158. `P2186`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2187` waits until `2026-06-03T00:00:00Z`.
159. `P2186` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
160. `P2187`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2188` waits until `2026-06-03T00:00:00Z`.
161. `P2187` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
162. `P2188`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2189` waits until `2026-06-03T00:00:00Z`.
163. `P2188` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
164. `P2189`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2190` waits until `2026-06-03T00:00:00Z`.
165. `P2189` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
166. `P2190`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2191` waits until `2026-06-03T00:00:00Z`.
167. `P2190` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
168. `P2191`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2192` waits until `2026-06-03T00:00:00Z`.
169. `P2191` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
170. `P2192`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2193` waits until `2026-06-03T00:00:00Z`.
171. `P2192` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
172. `P2193`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2194` waits until `2026-06-03T00:00:00Z`.
173. `P2193` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
174. `P2194`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2195` waits until `2026-06-03T00:00:00Z`.
175. `P2194` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
176. `P2195`: P2079 F1 UTC-close recheck completed as `BLOCKED_BY_UTC_CLOSE`; next `P2196` waits until `2026-06-03T00:00:00Z`.
177. `P2195` post-sync checks passed: text_guard `PASS`, readiness freeze preserved, `pip check PASS`, artifact parse `PASS`.
178. Quick structural audit completed as `PASS_WITH_ROUTE_CORRECTION`: framework/catalog validation is not blocked by P2079 UTC-close gate; 68 feature rows, 6 blocks, 27 linked profiles, 3x3/9 support, and block catalog `36/36 runtime OK`.
179. Structural big-window command-set/dry-run completed as `PASS`: artifact `reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json`, raw policy preflight `PASS`, compile/dry-run `36/36 PASS`.
180. Structural big-window narrow runtime started, then stopped by user request: artifact `reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`, status `STOPPED_BY_USER_AND_FREEZE_RESTORED`; completed launcher commands `3`, stopped launcher commands `1`, positive candidates `0`.

## Recent Results
1. `Package A candidate_count=0`.
2. Best tradeful branch inside `Package A`: `short_only`, `W2`, `A-H1`, `oos=-4.4808%`, `trades=1`.
3. `readiness`: `project_ready=false`, `enforce_freeze=true`.
4. `pip check`: `No broken requirements found.`
5. New active catalog TZ:
   `docs/TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md`.
6. Post-sync audit after catalog checkpoint: `PASS`.
   Artifact: `reports/qa_gate/p2027_optuna_full_calibration_catalog_post_sync_audit_20260602T083823Z.json`.
7. Step 1 wiring inventory: `PASS`.
   Artifact: `reports/optuna_catalog/index/p2030_step1_wiring_inventory_20260602T092159Z.json`.
   Summary: 6 enabled blocks, 68 feature rows matched runtime columns, 56 tunable feature rows, 20 tunable hypothesis rows, 27/27 profiles linked, profile issues `0`.
   Long/short compiled hypothesis counts: long_only `19`, short_only `17`.
8. Step 2 smoke command set: `PASS`.
   Artifact: `reports/optuna_catalog/index/p2032_step2_1d1d_smoke_command_set_20260602T092710Z.json`.
   Fixed command profile: train `2026-05-31`, test `2026-06-01`, matrix `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=narrow`, `ForceProfileEdgeCoverage=on`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, total workers `9`, trials `60`, timeout `300`.
9. Step 3 smoke preflight: `PASS`.
   Artifact: `reports/qa_gate/p2034_step3_smoke_preflight_20260602T093214Z.json`.
10. Step 4 long_only smoke:
   Runtime `OK`, workers `3/3`, catalog class `neutral`, best OOS `0.0%`, trades `0`.
   Artifact: `reports/optuna_catalog/neutral/p2035_step4_long_only_1d1d_smoke_neutral_20260602T093324Z.json`.
11. Step 5 short_only smoke:
   Runtime `OK`, workers `3/3`, catalog class `neutral`, best OOS `+0.2544%`, trades `1`, but `goal_pass=false`.
   Artifact: `reports/optuna_catalog/neutral/p2036_step5_short_only_1d1d_smoke_provisional_plus_goal_fail_20260602T093604Z.json`.
12. Step 6 smoke triage:
   Decision `GO_TO_MEDIUM_WORK`, accepted positive candidates `0`, provisional positive OOS branches `1`.
   Artifact: `reports/qa_gate/p2037_step6_1d1d_smoke_triage_20260602T093704Z.json`.
13. Step 7 medium command set:
   Artifact: `reports/optuna_catalog/index/p2039_step7_medium_command_set_20260602T095335Z.json`.
   Fixed profile: train `2026-05-31`, test `2026-06-01`, matrix `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=medium`, `ForceProfileEdgeCoverage=on`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, total workers `9`, trials `120`, timeout `600`.
   Compile/dry-run: long_only and short_only `PASS`.
14. Step 7 medium runtime/triage:
   long_only catalog class `negative`, best OOS `-6.9497%`, trades `1`, `goal_pass=false`.
   short_only catalog class `negative`, best OOS `-0.6217%`, trades `1`, `goal_pass=false`.
   Accepted positive candidates `0`; decision `GO_TO_WIDE_BATTLE`.
   Triage artifact: `reports/qa_gate/p2042_step7_medium_triage_20260602T100020Z.json`.
15. Step 7 medium post-sync audit:
   Artifact: `reports/qa_gate/p2043_step7_medium_post_sync_audit_20260602T100235Z.json`.
   JSON parse, compileall, text_guard, readiness, and pip check all `PASS`; freeze preserved.
16. Step 8 wide command set:
   Artifact: `reports/optuna_catalog/index/p2044_step8_wide_command_set_20260602T100351Z.json`.
   Fixed profile: train `2026-05-31`, test `2026-06-01`, matrix `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=wide`, `ForceProfileEdgeCoverage=on`, `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, total workers `9`, trials `180`, timeout `900`.
   Compile/dry-run: long_only and short_only `PASS`.
17. Step 8-11 final catalog result:
   wide long_only `negative`, best OOS `-4.9783%`, trades `1`, `goal_pass=false`.
   wide short_only `negative`, best OOS `-0.2663%`, trades `2`, `goal_pass=false`.
   Catalog ranking totals: positive `0`, neutral `2`, negative `4`, infra_fail `0`.
   Forward stability is not runnable because `candidate_for_forward=0`.
   Production/unfreeze remains blocked.
18. Closeout post-sync audit:
   Artifact: `reports/qa_gate/p2050_full_catalog_closeout_post_sync_audit_20260602T101019Z.json`.
   JSON parse, compileall, text_guard, readiness, and pip check all `PASS`; freeze preserved.
19. New block-level catalog cycle:
   Generated 6 block-isolated matrices under `configs/calibration_matrices/catalog_blocks/`.
   First block: `price_volatility`.
   `P2052` command set fixed: narrow grid, 3x3 workers, total trials `60`, timeout `300`, long/short dry-run `PASS`.
20. Block01 `price_volatility` result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
   Decision: `GO_TO_BLOCK02_TREND_MOMENTUM`.
   Post-sync audit `P2064`: `PASS`, freeze preserved.
21. Block02 `trend_momentum` narrow result:
   long_only catalog class `neutral`, best OOS `0.0%`, trades `0`, with negative tradeful branch `-15.3557%`.
   short_only catalog class `negative`, best OOS `-41.4626%`, trades `15`.
   Accepted positive candidates `0`; decision `GO_TO_BLOCK02_MEDIUM`.
22. Block02 `trend_momentum` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
   Decision: `GO_TO_BLOCK03_VOLUME_FLOW`.
   Post-sync audit `P2077`: `PASS`, freeze preserved.
23. Block03 `volume_flow` narrow result:
   long_only catalog class `positive`, best OOS `+1.9186%`, trades `1`, `goal_pass=true`.
   short_only catalog class `negative`, best OOS `-13.3138%`, trades `4`, `goal_pass=false`.
   Totals: positive `1`, neutral `0`, negative `1`, infra_fail `0`, candidate_for_forward `1`.
24. V3 Package B command set:
   `P2142` completed UTC `2026-06-02T13:05:59Z`, local `2026-06-02 18:05:59 +05:00`.
   Artifact: `reports/qa_gate/p2142_v3_package_b_command_set_20260602T130559Z.json`.
   Matrix slices: `configs/calibration_matrices/optuna_v3_package_b_bh1_long.yaml`, `configs/calibration_matrices/optuna_v3_package_b_bh1_short.yaml`, `configs/calibration_matrices/optuna_v3_package_b_bh2.yaml`, `configs/calibration_matrices/optuna_v3_package_b_bh3.yaml`.
   Dry-run/preflight: `18/18 PASS`; runtime was not executed in `P2142`.
25. V3 Package B `long_only` runtime:
   `P2143` completed UTC `2026-06-02T13:15:35Z`, local `2026-06-02 18:15:35 +05:00`.
   Runtime summary: `reports/qa_gate/p2143_v3_package_b_long_only_summary_20260602T131035Z.json`.
   Catalog artifact: `reports/optuna_catalog/neutral/p2143_v3_package_b_long_only_neutral_20260602T131535Z.json`.
   Runtime `9/9 PASS`; catalog class `neutral`; accepted positive candidates `0`; best tradeful OOS `-1.6687%`.
26. V3 Package B `short_only` runtime:
   `P2144` completed UTC `2026-06-02T13:24:20Z`, local `2026-06-02 18:24:20 +05:00`.
   Runtime summary: `reports/qa_gate/p2144_v3_package_b_short_only_summary_20260602T132020Z.json`.
   Catalog artifact: `reports/optuna_catalog/neutral/p2144_v3_package_b_short_only_neutral_20260602T132420Z.json`.
   Runtime `9/9 PASS`; catalog class `neutral`; accepted positive candidates `0`; best tradeful OOS `-1.6689%`.
27. V3 Package B unified triage:
   `P2145` completed UTC `2026-06-02T13:28:30Z`, local `2026-06-02 18:28:30 +05:00`.
   Artifact: `reports/qa_gate/p2145_v3_package_b_unified_triage_20260602T132830Z.json`.
   Result: `NO_CANDIDATE`; totals positive `0`, neutral `18`, negative `0`, infra_fail `0`; best tradeful OOS `-1.6687%`.
28. V3 Package B post-sync audit:
   `P2146` completed UTC `2026-06-02T13:30:21Z`, local `2026-06-02 18:30:21 +05:00`.
   Artifact: `reports/qa_gate/p2146_v3_package_b_post_sync_audit_20260602T133021Z.json`.
   Checks: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2145 artifact parse `PASS`.
29. V3 Package B closeout transition:
   `P2147` completed UTC `2026-06-02T13:33:30Z`, local `2026-06-02 18:33:30 +05:00`.
   Artifact: `reports/qa_gate/p2147_v3_package_b_closeout_transition_20260602T133330Z.json`.
   Decision: `GO_TO_FINAL_V3_NO_GO_DECISION_PACKAGE`; Package A and Package B both closed with no accepted candidate.
30. V3 final decision:
   `P2148` completed UTC `2026-06-02T13:36:00Z`, local `2026-06-02 18:36:00 +05:00`.
   Artifact: `reports/qa_gate/p2148_v3_final_no_go_decision_20260602T133600Z.json`.
   Decision: final launch `NO_GO`; no production-ready candidate; launch and unfreeze blocked.
31. V3 final post-sync audit:
   `P2149` completed UTC `2026-06-02T13:38:45Z`, local `2026-06-02 18:38:45 +05:00`.
   Artifact: `reports/qa_gate/p2149_v3_final_no_go_post_sync_audit_20260602T133845Z.json`.
   Checks: `text_guard PASS`, readiness freeze preserved, `pip check PASS`, P2148 artifact parse `PASS`; V3 chain closed.
32. Post-V3 catalog/forward boundary:
   `P2150` completed UTC `2026-06-02T13:41:50Z`, local `2026-06-02 18:41:50 +05:00`.
   Artifact: `reports/qa_gate/p2150_post_v3_catalog_forward_boundary_20260602T134150Z.json`.
   Result: route selected to P2079 F1 data gate after `2026-06-03T00:00:00Z`; runtime remains blocked.
33. P2079 F1 data gate pre-close check:
   `P2151` completed UTC `2026-06-02T14:17:11Z`, local `2026-06-02 19:17:11 +05:00`.
   Artifact: `reports/qa_gate/p2151_p2079_f1_data_gate_preclose_check_20260602T141711Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
34. P2079 F1 UTC-close recheck:
   `P2152` completed UTC `2026-06-02T14:20:42Z`, local `2026-06-02 19:20:42 +05:00`.
   Artifact: `reports/qa_gate/p2152_p2079_f1_data_gate_utc_close_recheck_20260602T142042Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
35. P2079 F1 UTC-close recheck:
   `P2153` completed UTC `2026-06-02T14:23:19Z`, local `2026-06-02 19:23:19 +05:00`.
   Artifact: `reports/qa_gate/p2153_p2079_f1_data_gate_utc_close_recheck_20260602T142319Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
36. P2079 F1 UTC-close recheck:
   `P2154` completed UTC `2026-06-02T14:25:53Z`, local `2026-06-02 19:25:53 +05:00`.
   Artifact: `reports/qa_gate/p2154_p2079_f1_data_gate_utc_close_recheck_20260602T142553Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; no ingest/preflight/runtime before `2026-06-03T00:00:00Z`.
37. P2079 F1 UTC-close recheck:
   `P2155` completed UTC `2026-06-02T14:29:20Z`, local `2026-06-02 19:29:20 +05:00`.
   Artifact: `reports/qa_gate/p2155_p2079_f1_data_gate_utc_close_recheck_20260602T142920Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2156` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143136Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T143136Z.json`), `pip check PASS`, artifact parse `PASS`.
38. P2079 F1 UTC-close recheck:
   `P2156` completed UTC `2026-06-02T14:33:08Z`, local `2026-06-02 19:33:08 +05:00`.
   Artifact: `reports/qa_gate/p2156_p2079_f1_data_gate_utc_close_recheck_20260602T143308Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2157` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143445Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T143445Z.json`), `pip check PASS`, artifact parse `PASS`.
39. P2079 F1 UTC-close recheck:
   `P2157` completed UTC `2026-06-02T14:36:25Z`, local `2026-06-02 19:36:25 +05:00`.
   Artifact: `reports/qa_gate/p2157_p2079_f1_data_gate_utc_close_recheck_20260602T143625Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2158` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T143926Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T143925Z.json`), `pip check PASS`, artifact parse `PASS`.
40. P2079 F1 UTC-close recheck:
   `P2158` completed UTC `2026-06-02T14:40:30Z`, local `2026-06-02 19:40:30 +05:00`.
   Artifact: `reports/qa_gate/p2158_p2079_f1_data_gate_utc_close_recheck_20260602T144030Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2159` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144209Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T144207Z.json`), `pip check PASS`, artifact parse `PASS`.
41. P2079 F1 UTC-close recheck:
   `P2159` completed UTC `2026-06-02T14:43:17Z`, local `2026-06-02 19:43:17 +05:00`.
   Artifact: `reports/qa_gate/p2159_p2079_f1_data_gate_utc_close_recheck_20260602T144317Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2160` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144457Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T144456Z.json`), `pip check PASS`, artifact parse `PASS`.
42. P2079 F1 UTC-close recheck:
   `P2160` completed UTC `2026-06-02T14:46:07Z`, local `2026-06-02 19:46:07 +05:00`.
   Artifact: `reports/qa_gate/p2160_p2079_f1_data_gate_utc_close_recheck_20260602T144607Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2161` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T144742Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T144742Z.json`), `pip check PASS`, artifact parse `PASS`.
43. P2079 F1 UTC-close recheck:
   `P2161` completed UTC `2026-06-02T14:49:43Z`, local `2026-06-02 19:49:43 +05:00`.
   Artifact: `reports/qa_gate/p2161_p2079_f1_data_gate_utc_close_recheck_20260602T144943Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2162` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145122Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T145121Z.json`), `pip check PASS`, artifact parse `PASS`.
44. P2079 F1 UTC-close recheck:
   `P2162` completed UTC `2026-06-02T14:52:28Z`, local `2026-06-02 19:52:28 +05:00`.
   Artifact: `reports/qa_gate/p2162_p2079_f1_data_gate_utc_close_recheck_20260602T145228Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2163` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145406Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T145405Z.json`), `pip check PASS`, artifact parse `PASS`.
45. P2079 F1 UTC-close recheck:
   `P2163` completed UTC `2026-06-02T14:55:22Z`, local `2026-06-02 19:55:22 +05:00`.
   Artifact: `reports/qa_gate/p2163_p2079_f1_data_gate_utc_close_recheck_20260602T145522Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2164` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T145702Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T145701Z.json`), `pip check PASS`, artifact parse `PASS`.
46. P2079 F1 UTC-close recheck:
   `P2164` completed UTC `2026-06-02T15:00:19Z`, local `2026-06-02 20:00:19 +05:00`.
   Artifact: `reports/qa_gate/p2164_p2079_f1_data_gate_utc_close_recheck_20260602T150019Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2165` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150225Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T150225Z.json`), `pip check PASS`, artifact parse `PASS`.
47. P2079 F1 UTC-close recheck:
   `P2165` completed UTC `2026-06-02T15:04:36Z`, local `2026-06-02 20:04:36 +05:00`.
   Artifact: `reports/qa_gate/p2165_p2079_f1_data_gate_utc_close_recheck_20260602T150436Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2166` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150617Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T150617Z.json`), `pip check PASS`, artifact parse `PASS`.
48. P2079 F1 UTC-close recheck:
   `P2166` completed UTC `2026-06-02T15:07:32Z`, local `2026-06-02 20:07:32 +05:00`.
   Artifact: `reports/qa_gate/p2166_p2079_f1_data_gate_utc_close_recheck_20260602T150732Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2167` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T150915Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T150915Z.json`), `pip check PASS`, artifact parse `PASS`.
49. P2079 F1 UTC-close recheck:
   `P2167` completed UTC `2026-06-02T15:10:30Z`, local `2026-06-02 20:10:30 +05:00`.
   Artifact: `reports/qa_gate/p2167_p2079_f1_data_gate_utc_close_recheck_20260602T151030Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2168` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151314Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T151314Z.json`), `pip check PASS`, artifact parse `PASS`.
50. P2079 F1 UTC-close recheck:
   `P2168` completed UTC `2026-06-02T15:15:32Z`, local `2026-06-02 20:15:32 +05:00`.
   Artifact: `reports/qa_gate/p2168_p2079_f1_data_gate_utc_close_recheck_20260602T151532Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2169` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T151714Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T151713Z.json`), `pip check PASS`, artifact parse `PASS`.
51. P2079 F1 UTC-close recheck:
   `P2169` completed UTC `2026-06-02T15:18:26Z`, local `2026-06-02 20:18:26 +05:00`.
   Artifact: `reports/qa_gate/p2169_p2079_f1_data_gate_utc_close_recheck_20260602T151826Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2170` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152005Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T152004Z.json`), `pip check PASS`, artifact parse `PASS`.
52. P2079 F1 UTC-close recheck:
   `P2170` completed UTC `2026-06-02T15:21:20Z`, local `2026-06-02 20:21:20 +05:00`.
   Artifact: `reports/qa_gate/p2170_p2079_f1_data_gate_utc_close_recheck_20260602T152120Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2171` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152306Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T152305Z.json`), `pip check PASS`, artifact parse `PASS`.
53. P2079 F1 UTC-close recheck:
   `P2171` completed UTC `2026-06-02T15:25:59Z`, local `2026-06-02 20:25:59 +05:00`.
   Artifact: `reports/qa_gate/p2171_p2079_f1_data_gate_utc_close_recheck_20260602T152559Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2172` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T152826Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T152825Z.json`), `pip check PASS`, artifact parse `PASS`.
54. P2079 F1 UTC-close recheck:
   `P2172` completed UTC `2026-06-02T15:29:40Z`, local `2026-06-02 20:29:40 +05:00`.
   Artifact: `reports/qa_gate/p2172_p2079_f1_data_gate_utc_close_recheck_20260602T152940Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2173` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153127Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T153126Z.json`), `pip check PASS`, artifact parse `PASS`.
55. P2079 F1 UTC-close recheck:
   `P2173` completed UTC `2026-06-02T15:32:42Z`, local `2026-06-02 20:32:42 +05:00`.
   Artifact: `reports/qa_gate/p2173_p2079_f1_data_gate_utc_close_recheck_20260602T153242Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2174` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153429Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T153428Z.json`), `pip check PASS`, artifact parse `PASS`.
56. P2079 F1 UTC-close recheck:
   `P2174` completed UTC `2026-06-02T15:35:32Z`, local `2026-06-02 20:35:32 +05:00`.
   Artifact: `reports/qa_gate/p2174_p2079_f1_data_gate_utc_close_recheck_20260602T153532Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2175` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T153717Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T153716Z.json`), `pip check PASS`, artifact parse `PASS`.
57. P2079 F1 UTC-close recheck:
   `P2175` completed UTC `2026-06-02T15:38:21Z`, local `2026-06-02 20:38:21 +05:00`.
   Artifact: `reports/qa_gate/p2175_p2079_f1_data_gate_utc_close_recheck_20260602T153821Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2176` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154009Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T154008Z.json`), `pip check PASS`, artifact parse `PASS`.
58. P2079 F1 UTC-close recheck:
   `P2176` completed UTC `2026-06-02T15:41:14Z`, local `2026-06-02 20:41:14 +05:00`.
   Artifact: `reports/qa_gate/p2176_p2079_f1_data_gate_utc_close_recheck_20260602T154114Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2177` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154333Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T154333Z.json`), `pip check PASS`, artifact parse `PASS`.
59. P2079 F1 UTC-close recheck:
   `P2177` completed UTC `2026-06-02T15:44:46Z`, local `2026-06-02 20:44:46 +05:00`.
   Artifact: `reports/qa_gate/p2177_p2079_f1_data_gate_utc_close_recheck_20260602T154446Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2178` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T154634Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T154633Z.json`), `pip check PASS`, artifact parse `PASS`.
60. P2079 F1 UTC-close recheck:
   `P2178` completed UTC `2026-06-02T15:48:06Z`, local `2026-06-02 20:48:06 +05:00`.
   Artifact: `reports/qa_gate/p2178_p2079_f1_data_gate_utc_close_recheck_20260602T154806Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2179` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155005Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T155004Z.json`), `pip check PASS`, artifact parse `PASS`.
61. P2079 F1 UTC-close recheck:
   `P2179` completed UTC `2026-06-02T15:51:19Z`, local `2026-06-02 20:51:19 +05:00`.
   Artifact: `reports/qa_gate/p2179_p2079_f1_data_gate_utc_close_recheck_20260602T155119Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2180` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155304Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T155304Z.json`), `pip check PASS`, artifact parse `PASS`.
62. P2079 F1 UTC-close recheck:
   `P2180` completed UTC `2026-06-02T15:54:33Z`, local `2026-06-02 20:54:33 +05:00`.
   Artifact: `reports/qa_gate/p2180_p2079_f1_data_gate_utc_close_recheck_20260602T155433Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2181` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T155722Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T155722Z.json`), `pip check PASS`, artifact parse `PASS`.
63. P2079 F1 UTC-close recheck:
   `P2181` completed UTC `2026-06-02T15:58:51Z`, local `2026-06-02 20:58:51 +05:00`.
   Artifact: `reports/qa_gate/p2181_p2079_f1_data_gate_utc_close_recheck_20260602T155851Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2182` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160102Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T160101Z.json`), `pip check PASS`, artifact parse `PASS`.
64. P2079 F1 UTC-close recheck:
   `P2182` completed UTC `2026-06-02T16:02:18Z`, local `2026-06-02 21:02:18 +05:00`.
   Artifact: `reports/qa_gate/p2182_p2079_f1_data_gate_utc_close_recheck_20260602T160218Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2183` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160404Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T160403Z.json`), `pip check PASS`, artifact parse `PASS`.
65. P2079 F1 UTC-close recheck:
   `P2183` completed UTC `2026-06-02T16:05:16Z`, local `2026-06-02 21:05:16 +05:00`.
   Artifact: `reports/qa_gate/p2183_p2079_f1_data_gate_utc_close_recheck_20260602T160516Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2184` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T160705Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T160704Z.json`), `pip check PASS`, artifact parse `PASS`.
66. P2079 F1 UTC-close recheck:
   `P2184` completed UTC `2026-06-02T16:08:48Z`, local `2026-06-02 21:08:48 +05:00`.
   Artifact: `reports/qa_gate/p2184_p2079_f1_data_gate_utc_close_recheck_20260602T160848Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2185` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161033Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161033Z.json`), `pip check PASS`, artifact parse `PASS`.
67. P2079 F1 UTC-close recheck:
   `P2185` completed UTC `2026-06-02T16:11:50Z`, local `2026-06-02 21:11:50 +05:00`.
   Artifact: `reports/qa_gate/p2185_p2079_f1_data_gate_utc_close_recheck_20260602T161150Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2186` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161336Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161335Z.json`), `pip check PASS`, artifact parse `PASS`.
68. P2079 F1 UTC-close recheck:
   `P2186` completed UTC `2026-06-02T16:15:30Z`, local `2026-06-02 21:15:30 +05:00`.
   Artifact: `reports/qa_gate/p2186_p2079_f1_data_gate_utc_close_recheck_20260602T161530Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2187` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161633Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161632Z.json`), `pip check PASS`, artifact parse `PASS`.
69. P2079 F1 UTC-close recheck:
   `P2187` completed UTC `2026-06-02T16:19:09Z`, local `2026-06-02 21:19:09 +05:00`.
   Artifact: `reports/qa_gate/p2187_p2079_f1_data_gate_utc_close_recheck_20260602T161909Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2188` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T161942Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T161941Z.json`), `pip check PASS`, artifact parse `PASS`.
70. P2079 F1 UTC-close recheck:
   `P2188` completed UTC `2026-06-02T16:22:57Z`, local `2026-06-02 21:22:57 +05:00`.
   Artifact: `reports/qa_gate/p2188_p2079_f1_data_gate_utc_close_recheck_20260602T162257Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2189` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162331Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T162331Z.json`), `pip check PASS`, artifact parse `PASS`.
71. P2079 F1 UTC-close recheck:
   `P2189` completed UTC `2026-06-02T16:25:48Z`, local `2026-06-02 21:25:48 +05:00`.
   Artifact: `reports/qa_gate/p2189_p2079_f1_data_gate_utc_close_recheck_20260602T162548Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2190` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T162627Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T162626Z.json`), `pip check PASS`, artifact parse `PASS`.
72. P2079 F1 UTC-close recheck:
   `P2190` completed UTC `2026-06-02T16:30:21Z`, local `2026-06-02 21:30:21 +05:00`.
   Artifact: `reports/qa_gate/p2190_p2079_f1_data_gate_utc_close_recheck_20260602T163021Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2191` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163046Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163046Z.json`), `pip check PASS`, artifact parse `PASS`.
73. P2079 F1 UTC-close recheck:
   `P2191` completed UTC `2026-06-02T16:33:25Z`, local `2026-06-02 21:33:25 +05:00`.
   Artifact: `reports/qa_gate/p2191_p2079_f1_data_gate_utc_close_recheck_20260602T163325Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2192` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163350Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163349Z.json`), `pip check PASS`, artifact parse `PASS`.
74. P2079 F1 UTC-close recheck:
   `P2192` completed UTC `2026-06-02T16:36:04Z`, local `2026-06-02 21:36:04 +05:00`.
   Artifact: `reports/qa_gate/p2192_p2079_f1_data_gate_utc_close_recheck_20260602T163604Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2193` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163630Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163629Z.json`), `pip check PASS`, artifact parse `PASS`.
75. P2079 F1 UTC-close recheck:
   `P2193` completed UTC `2026-06-02T16:38:39Z`, local `2026-06-02 21:38:39 +05:00`.
   Artifact: `reports/qa_gate/p2193_p2079_f1_data_gate_utc_close_recheck_20260602T163839Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2194` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T163903Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T163902Z.json`), `pip check PASS`, artifact parse `PASS`.
76. P2079 F1 UTC-close recheck:
   `P2194` completed UTC `2026-06-02T16:41:09Z`, local `2026-06-02 21:41:09 +05:00`.
   Artifact: `reports/qa_gate/p2194_p2079_f1_data_gate_utc_close_recheck_20260602T164109Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2195` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164133Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T164132Z.json`), `pip check PASS`, artifact parse `PASS`.
77. P2079 F1 UTC-close recheck:
   `P2195` completed UTC `2026-06-02T16:45:02Z`, local `2026-06-02 21:45:02 +05:00`.
   Artifact: `reports/qa_gate/p2195_p2079_f1_data_gate_utc_close_recheck_20260602T164502Z.json`.
   Result: `BLOCKED_BY_UTC_CLOSE`; next `P2196` is blocked until `2026-06-03T00:00:00Z`; no ingest/preflight/runtime now.
   Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260602T164527Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260602T164526Z.json`), `pip check PASS`, artifact parse `PASS`.
78. Quick structural audit:
   Artifact: `reports/qa_gate/quick_structural_audit_framework_20260602T182715Z.json`.
   Result: `PASS_WITH_ROUTE_CORRECTION`; UTC-close gate is only for P2079 forward/production. Structural big-window validation can be opened on already closed historical data.
   Framework facts: 68 feature rows across 6 blocks, narrow/medium/wide presets, 27 linked parameter profiles, 20 tunable hypotheses, 3x3/9 launcher support, block catalog `36/36 runtime OK`, positive `1`, neutral `18`, negative `17`, infra_fail `0`.
24. Block03 `volume_flow` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `1`, neutral `2`, negative `3`, infra_fail `0`, candidate_for_forward `1`.
   Positive artifact: `reports/optuna_catalog/positive/p2079_block03_volume_flow_narrow_long_only_positive_20260602T103932Z.json`.
   Decision: `GO_TO_BLOCK04_DENSITY_PROFILE_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
   Post-sync audit `P2090`: `PASS`, freeze preserved.
25. Block04 `density_profile` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `4`, negative `2`, infra_fail `0`, candidate_for_forward `0`.
   Prior block03 positive candidate is preserved.
   Decision: `GO_TO_BLOCK05_STRUCTURE_TA_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
   Post-sync audit `P2103`: `PASS`, freeze preserved.
26. Block05 `structure_ta` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
   Prior block03 positive candidate is preserved.
   Decision: `GO_TO_BLOCK06_PATTERN_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
   Post-sync audit `P2116`: `PASS`, freeze preserved.
27. Block06 `pattern` full result:
   narrow/medium/wide runtime completed with `runtime OK` in all 6 runs.
   Totals: positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
   Prior block03 positive candidate is preserved.
   Decision: `GO_TO_BLOCK_LEVEL_CATALOG_RANKING_WITH_BLOCK03_FORWARD_CANDIDATE_PRESERVED`.
28. Block-level catalog ranking:
   All 6 blocks completed, runtime runs `36/36 OK`.
   Totals: positive `1`, neutral `18`, negative `17`, infra_fail `0`, candidate_for_forward `1`.
   Accepted candidate: block03 `volume_flow`, `P2079`, `long_only`, narrow, OOS `+1.9186%`, trades `1`.
   Boundary: forward F1/F2 required; production/unfreeze remains blocked.
29. P2133 forward command set:
   Artifact: `reports/optuna_catalog/index/p2133_p2079_forward_stability_command_set_20260602T112708Z.json`.
   Primary path: fixed-parameter replay of P2079 as singleton grids.
   Secondary path: same block03 narrow Optuna contour with fixed 3x3 profile.
   F1 window `2026-06-01 -> 2026-06-02` preflight `FAIL`: test raw `2026-06-02` absent; `2026-06-01` train is present but partial for WF rows.
   F2 window `2026-06-02 -> 2026-06-03` preflight `FAIL`: train raw `2026-06-02` and test raw `2026-06-03` absent.
30. P2134 forward data gate:
   Artifact: `reports/qa_gate/p2134_p2079_forward_preflight_data_gate_20260602T113136Z.json`.
   Current UTC at check: `2026-06-02T11:31:36Z`; `2026-06-02` is not closed in UTC and `2026-06-03` is future.
   Core max day: `2026-05-31`; raw max day: `2026-06-01`.
   F1 preflight report: `reports/qa_gate/preflight_window_20260602T113056Z.json`, `FAIL`.
   F2 preflight report: `reports/qa_gate/preflight_window_20260602T113105Z.json`, `FAIL`.
31. P2137 previous TZ recovery:
   Artifact: `reports/qa_gate/p2137_previous_tz_recovery_package_b_pointer_20260602T123736Z.json`.
   Previous active V3 requirement: after `Package A NO_CANDIDATE`, define exact `Package B` slots and then run bounded `Package B`.
   Catalog overlay does not cancel this; it requires preserving bounded Package B as catalog knowledge.
   Manual pointer restored to `Package B` definition. P2079 remains preserved only as `candidate_for_forward`; heartbeat is paused.
32. P2138 post-sync audit:
   Artifact: `reports/qa_gate/p2138_previous_tz_recovery_post_sync_audit_20260602T123949Z.json`.
   `text_guard`: `PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260602T123937Z.json`.
   `readiness`: `PASS`, freeze preserved, artifact `reports/readiness/readiness_check_20260602T123936Z.json`.
   `pip check`: `PASS`.
33. P2139 timed step chain:
   Artifact: `reports/qa_gate/p2139_package_b_timed_step_chain_20260602T124520Z.json`.
   Chain timestamp: UTC `2026-06-02T12:45:20Z`, local `2026-06-02 17:45:20 +05:00`.
   From TZ: `docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md`, section 7, `2026-06-02T06:52:50Z`.
   Current step: Step 1 inventory of V3 Package A and old Package B artifacts.
34. P2139 independent agent cross-check:
   Artifact: `reports/qa_gate/p2139_independent_agent_crosscheck_20260602T125117Z.json`.
   Agent conclusion: current path is correct if next action is inventory only.
   Local conclusion: matches global audit Step 8 and V3 section 7; catalog overlay does not cancel Package B.
   Hard stop: no Package B runtime or P2079 forward before `P2140` inventory and Package B command-set/dry-run `PASS`.
35. P2140 V3 Package B inventory:
   Artifact: `reports/qa_gate/p2140_v3_package_b_inventory_20260602T125900Z.json`.
   Status: `PASS`.
   Current V3 Package A: closed `NO_CANDIDATE`, candidate_count `0`, best tradeful `short_only W2 A-H1`, OOS `-4.480772237153707`, trades `1`.
   Old Package B artifacts: `P1995/P1996` V2 and `P2005-P2007` strict execution are historical references only, not current V3 Package B.
   Current V3 Package B: exact slots not defined, matrices not found, command set not defined, runtime not allowed.
36. P2141 exact V3 Package B slots:
   Artifact: `reports/qa_gate/p2141_v3_package_b_exact_slots_20260602T130000Z.json`.
   Status: `PASS`.
   Windows: W1 `2026-05-29 -> 2026-05-30`, W2 `2026-05-30 -> 2026-05-31`, W3 `2026-05-31 -> 2026-06-01`.
   Slots: B-H1 `ema_stack_bull` long / `ema_cross_20_200` short; B-H2 `min_max_range_revert` both; B-H3 `spread_pressure_and_delta_absorption` both.
   Resource profile: `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`.
   Next: `P2142` matrix slices and command-set/dry-run only.

## Current Risks
1. `Package B` is required by V3 but its exact slot composition is not fixed yet.
2. Running `Package B` without a fixed slot table would reintroduce drift.
3. Old historical reports are numerous; always use active files listed in `handoff.md`.
4. The repository is not a git repo in this workspace, so local file backups matter.
5. Old V3 wording can be misread as stopping after `Package B NO_CANDIDATE`; active catalog overlay says to keep structured block/feature/hypothesis cataloging.
6. Running wider medium/wide catalog work before the `1d -> 1d` smoke check could hide wiring or parameter-transfer defects under a large search.
7. Skipping roadmap steps would reintroduce drift; every step now needs an exit artifact/status before moving forward.

## State Version
`V3-NO_GO-P2195-STRUCTURAL-AUDIT-PASS-WITH-ROUTE-CORRECTION-20260602T182715Z`

## Hard Structural Audit 2026-06-02T19:16:09Z
Artifact: `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md`.
Status: `PASS_WITH_FINDINGS`.
Facts: 68 features across 6 blocks, 56 tunable feature rows, 20 tunable hypotheses, 27/27 parameter profiles linked, 0 runtime feature misses, 0 feature-group mismatches, narrow/medium/wide min/max anchors preserved, 18/18 block command sets PASS, block catalog runtime `36/36 OK`.
Finding: block matrices isolate feature rows, but global hypothesis/trend-filter logic can still pull columns from another block. `P2079` is valid as a working catalog candidate, but not proven as pure `volume_flow` only.
Boundary: production remains `NO_GO`; P2079 remains `candidate_for_forward` only until F1/F2 forward validation is `2/2 PASS` and a new GO package exists.

## State Version
`V3-NO_GO-P2195-HARD-STRUCTURAL-AUDIT-PASS-WITH-FINDINGS-20260602T191609Z`

## Structural Big-Window Stop 2026-06-02T19:23:17Z
Command-set artifact: `reports/optuna_catalog/index/structural_big_window_command_set_20260602T191737Z.json`, status `PASS`, compile/dry-run `36/36 PASS`.
Stop artifact: `reports/qa_gate/structural_big_window_runtime_stopped_20260602T192317Z.json`, status `STOPPED_BY_USER_AND_FREEZE_RESTORED`.
Runtime facts: block01 long/short and block02 long completed with launcher `OK`; block02 short was stopped by user; positive candidates `0`; no production/unfreeze touched.

## State Version
`V3-NO_GO-P2195-STRUCTURAL-RUNTIME-STOPPED-BY-USER-FREEZE-RESTORED-20260602T192317Z`

## P2196A Optuna Battle Readiness Audit 2026-06-03T06:09:19Z
Artifact: `reports/qa_gate/p2196a_optuna_battle_readiness_audit_20260603T060919Z.md`.
Status: `NO_GO_FOR_PRODUCTION / GO_TO_STRICT_BLOCK_PURITY_FIX_BEFORE_BATTLE`.
Current facts: structural Optuna contour works, 3x3/9 workers are supported, 36/36 historical block catalog runs were OK, and structural big-window command-set dry-run was 36/36 PASS. The blocking finding remains strict semantics: block matrices isolate feature rows, but hypotheses/trend filters are still global unless filtered by required columns.
Forward data gate: current UTC is after 2026-06-03T00:00:00Z, but raw/core 2026-06-02 and 2026-06-03 SOLUSDT 1m files are missing. P2079 F1 still needs ingest/preflight PASS; F2 waits for closed 2026-06-03.
Next state: `P2196B` strict block-hypothesis compatibility implementation/audit before battle runtime.
Checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T061526Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T061522Z.json`), `pip check PASS`.

## State Version
`V3-NO_GO-P2196A-BATTLE-READINESS-AUDIT-STRICT-PURITY-NEXT-20260603T060919Z`

## P2196B Volume/Volatility Context Wiring
Artifact: `reports/qa_gate/p2196b_volume_context_wiring_audit_20260603T065821Z.json`.
Status: `PASS_CONTEXT_WIRING / STRICT_HYPOTHESIS_FILTER_PENDING`.
Current fact: volume/volatility context is now always included in Optuna feature/profile selection through `volume_flow` and `price_volatility` for full matrix and all 6 catalog block matrices. This does not make raw `volume` tunable; it makes derived volume features participate in calibration and reporting.
Tests: `tests.test_optuna_space_constraints` + `tests.test_optuna_search_runtime` -> `69/69 OK`.
Post-sync checks: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T070000Z.json`), readiness freeze preserved (`reports/readiness/readiness_check_20260603T065959Z.json`), `pip check PASS`.

## State Version
`V3-NO_GO-P2196B-VOLUME-CONTEXT-PASS-STRICT-FILTER-PENDING-20260603T065821Z`

## P2196B Strict Hypothesis Filtering
Artifact: `reports/qa_gate/p2196b_strict_hypothesis_filter_full_audit_20260603T100404Z.json`.
Status: `PASS_STRICT_FILTERING`.
Current fact: block catalog matrices now filter hypotheses/trend filters by required columns within primary enabled block plus always-on context blocks. This closes the known P2079-style mixed-semantics issue where `volume_flow` could select `min_max_range_revert` from `structure_ta`.
Tests: focused strict set -> `77/77 OK`.

## P2196C Strict Command Set Dry-Run
Artifact: `reports/optuna_catalog/index/p2196c_strict_command_set_20260603T100504Z.json`.
Status: `PASS`, `36/36 dry-run PASS`.
Raw preflight: `reports/qa_gate/preflight_window_20260603T100432Z.json`, `PASS`.
Next executable step: `P2196D` strict P2079-equivalent check. Production/unfreeze remains `NO_GO`.
Post-sync checks 2026-06-03T10:08:56Z: text_guard `PASS` (`reports/qa_gate/recovery_r5_text_guard_20260603T100856Z.json`), readiness freeze preserved with calibration-only temporary unlock path (`reports/readiness/readiness_check_20260603T100856Z.json`), `pip check PASS`.

## State Version
`V3-NO_GO-P2196C-STRICT-COMMAND-SET-36-36-PASS-20260603T100504Z`

## P2196D Strict Runtime Calibration Start 2026-06-03T10:14:50Z
Artifact: `reports/adaptive/long_only_pool_20260603t101450z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T101454Z.json`.
Status: `PASS_RUNTIME_OK / EXPERIMENTAL_POSITIVE`.
Current fact: first real strict calibration runtime ran block03 `volume_flow` narrow `long_only` with 3x3/9 workers. Launcher returned `OK`; best OOS was `+1.5266529420731034%` with `1` trade; workers `w2` and `w3` passed the 1% goal.
Boundary: train gate failed, so the result is saved as `TOP_EXPERIMENTAL`, not production/latest. Production/unfreeze remains `NO_GO`.
Next practical action: continue calibration sequence from the next strict battle run; do not expand into old chronology.

## State Version
`V3-NO_GO-P2196D-STRICT-RUNTIME-STARTED-EXPERIMENTAL-POSITIVE-20260603T101450Z`

## P2196E Volume Flow Narrow Short Runtime 2026-06-03T10:21:58Z
Artifact: `reports/adaptive/short_only_pool_20260603t102158z_w3/adaptive_loop_SOLUSDT_1m_2026-06-01_20260603T102202Z.json`.
Status: `PASS_RUNTIME_OK / NO_CANDIDATE`.
Current fact: short side of block03 `volume_flow` narrow was rerun after fixing report-read robustness. Launcher returned `OK`, all 3 workers exited `0`, best OOS `0%`, trades `0`.
Code fix: `src/mlbotnav/adaptive_auto_train.py` now uses `_read_json_report_with_retry` so an empty/unreadable search report becomes a recorded iteration failure instead of crashing a worker.
Validation: focused tests `83/83 OK`.
Next practical action: continue volume_flow calibration to the next grid/profile, or move to the next block runtime if operator chooses block-first ordering.

## State Version
`V3-NO_GO-P2196E-VOLUME-FLOW-NARROW-BOTH-SIDES-CHECKED-20260603T102158Z`

## Calibration Current H006 Pattern Replay
Artifact: `reports/qa_gate/pattern_block06_replay_after_param_retry_fix_20260604T110012Z_RU.md`.
Status: `BLOCK_COMPLETE_RUNTIME_OK_NO_CANDIDATE`.
Current fact: H006 `pattern` was replayed after fixing final parameter transfer and candidate retry. `long_only` and `short_only` each ran `narrow/medium/wide` with `ProcessWorkers=3`, `SearchWorkers=9`, `SearchWorkersPerProcess=3`; all 6 launchers returned `OK`.
Runtime result: no worker crash; every final `best_oos` contains `18` `selected_calibration_params`; no positive candidate. Best tradeful result is `short_only medium`, `-15.6997%`, `6` trades.
Code fix: `src/mlbotnav/adaptive_auto_train.py` preserves `calibration_params`, includes them in candidate signatures, and tries up to `8` current candidates before marking train replay failed.
Tests: focused suite `81/81 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T110352Z.json`.

## State Version
`CALIBRATION-CURRENT-H006-PATTERN-REPLAY-OK-NO-CANDIDATE-20260604T110012Z`

## H006 Grid Edge Coverage Audit Fix
Artifact: `reports/qa_gate/h006_grid_edge_coverage_audit_fix_20260604T111552Z_RU.md`.
Status: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.
Current fact: Optuna search reports now include `grid_edge_coverage_audit`, and a separate `grid_edge_coverage_audit_*.json` artifact is written beside `trial_history`. The audit counts all trials for the current `run_signature`, including pruned trials, so forced min/max coverage is no longer invisible.
Runtime smoke: H006 `pattern long_only narrow`, `2x6`, `24` total trials, launcher `OK`; new audit artifact `reports/optuna/long_only/grid_edge_coverage_audit_20260604T111552Z.json` saw `total=12`, `completed=8`, `pruned=4`, `failed=0` for the best worker search.
Tests: focused suite `94/94 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T111802Z.json`.
Next fact: cascade improvement is not implemented yet; next route is full replay with new edge audit or cascade mode implementation.

## State Version
`CALIBRATION-CURRENT-H006-EDGE-AUDIT-FIX-SMOKE-OK-20260604T111552Z`

## H006 Core Grid Edge Forcing Fix
Artifact: `reports/qa_gate/h006_core_grid_edge_forcing_fix_20260604T113102Z_RU.md`.
Status: `FIXED_FOCUSED_TESTS_PASS_RUNTIME_SMOKE_OK`.
Current fact: core search parameters now have forced min/max seeding and audit fields. The first 5 trials force min for `horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`; the next 5 force max.
Runtime smoke: H006 `pattern long_only narrow`, `2x6`, `24` total trials, launcher `OK`. Audit `reports/optuna/long_only/grid_edge_coverage_audit_20260604T113102Z.json` reports core coverage `pass=5`, `fail=0`.
Tests: focused suite `94/94 OK`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260604T113308Z.json`.
Next fact: profile coverage still needs full-budget replay for proof; cascade improvement is still pending.

## State Version
`CALIBRATION-CURRENT-H006-CORE-EDGE-FORCING-SMOKE-OK-20260604T113102Z`

## H006 Full Replay Edge Coverage Pass
Artifact: `reports/qa_gate/h006_full_replay_edge_audit_after_worker_distribution_20260604T123958Z_RU.md`.
Status: `BLOCK_COMPLETE_RUNTIME_OK_EDGE_COVERAGE_PASS_NO_CANDIDATE`.
Current fact: H006 `pattern` now has a full proof replay after distributed edge coverage. LONG and SHORT each ran `narrow/medium/wide`; every combined grid audit shows profile coverage `18/18` and core coverage `5/5`.
Runtime result: all 6 launchers `OK`, worker crash `0`, positive candidate `0`. Best LONG: `narrow -0.6074%`, `1` trade. Best tradeful SHORT: `wide -20.3243%`, `10` trades.
Tests: focused suite `95/95 OK`.
Next fact: the remaining open feature is cascade candidate improvement: `wide -> medium around best -> narrow around best`, LONG and SHORT separately.

## State Version
`CALIBRATION-CURRENT-H006-FULL-REPLAY-EDGE-PASS-NO-CANDIDATE-20260604T123958Z`

## CASCADE_BLOCK_CALIBRATION Rule Fixed
Artifact: `docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`.
Status: `RULE_FIXED_NO_CODE_CHANGES`.
Current fact: target battle calibration mode is now `CASCADE_BLOCK_CALIBRATION`: one block equals one cascade; LONG and SHORT are separate; `wide` runs first; `medium` narrows around the best tradeful `wide`; `narrow` narrows around the best tradeful `medium`.
Boundary: if `wide` finds no tradeful candidate, do not narrow blindly; record `NO_TRADEFUL_CANDIDATE` and move to the next block. If the best tradeful candidate is negative, continue the cascade to measure the best possible block result. Positive candidates go to positive/top candidates only, not production.
No code changed and no runtime launched for this rule fixation.

## State Version
`CALIBRATION-CURRENT-CASCADE-BLOCK-CALIBRATION-RULE-FIXED-20260604T141745Z`

## C001 Block 01 LONG Wide Runtime
Artifact: `reports/qa_gate/c001_block01_price_volatility_long_wide_20260604T144429Z_RU.md`.
Status: `RUNTIME_OK_TRADEFUL_NEGATIVE`.
Current fact: first cascade runtime step ran `price_volatility` / Block 01 `long_only wide` with `ProcessWorkers=3`, `SearchWorkers=9`, `SearchWorkersPerProcess=3`, `OptunaTrials=180`. Launcher returned `OK`, workers `3/3` exited `0`.
Runtime result: best OOS `-37.0372%` with `9` trades. Candidate is tradeful but negative; production remains `NO_GO`.
Best wide params: `min_abs_ema_gap=0.05`, `period_standard=19`, `return_lookback=18`, `rolling_window=40`, `vol_z_window=180`.
Coverage note: core coverage is `5/5`; profile coverage is `5/5` in one edge audit and `2/5` in another. `w1/w2` point at the same search report timestamp with `contour_id=w2`, likely an artifact naming collision.
Next fact: by `CASCADE_BLOCK_CALIBRATION`, next allowed step is `C001 LONG medium around best`; blind medium/narrow should not run.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260604T144630Z.json`.

## State Version
`CALIBRATION-CURRENT-C001-BLOCK01-LONG-WIDE-RUNTIME-OK-TRADEFUL-NEGATIVE-20260604T144429Z`

## Instrument Knobs Audit TZ
Artifact: `docs/CALIBRATION_NODE_CURRENT/TZ_INSTRUMENT_KNOBS_AUDIT_2026-06-11_RU.md`.
Status: `ACTIVE_READ_ONLY_AUDIT`.
Current fact: user clarified that the next step is not more runtime calibration. The next task is a block-by-block audit of every instrument/feature/indicator/hypothesis knob: what can be tuned, what is currently declared, what is actually used, and which signal-level thresholds/lines are missing.
Boundary: do not run `C001 medium`, Optuna/APTuna runtime, forward, or production actions until the instrument knobs audit is completed and agreed.
Next fact: start with `Block 01 price_volatility instrument knobs audit`, then move block-by-block through all 6 blocks.

## State Version
`CALIBRATION-CURRENT-INSTRUMENT-KNOBS-AUDIT-TZ-ACTIVE-20260611T104735Z`

## Block 01 Price Volatility Knobs Audit
Artifact: `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.
Status: `BLOCK_01_AUDIT_DRAFT`.
Current fact: Block 01 `price_volatility` has a separate mini-TZ now. It confirms the block currently calibrates calculation windows (`return_lookback`, `rolling_window`, `period_standard`), while explicit signal-level thresholds for price move strength, high-low spread regime, volatility regime, and ATR/risk regime are still pending agreement.
Boundary: no runtime launches and no config edits until Block 01 knobs are agreed.
Next fact: agree Block 01 knobs, then move to `Block 02 trend_momentum`.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T105438Z.json`.

## State Version
`CALIBRATION-CURRENT-BLOCK01-PRICE-VOLATILITY-KNOBS-AUDIT-DRAFT-20260611T105100Z`

## Block 01 Live Chart Example
Artifacts:
1. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.png`
2. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z_RU.md`
3. `reports/qa_gate/block01_price_volatility_live_chart_ru_20260611T110200Z.json`

Status: `VISUAL_AUDIT_EXAMPLE`.
Current fact: Block 01 was rendered on real SOLUSDT 1m data from `2026-06-01` using C001 wide calculation params (`return_lookback=18`, `rolling_window=40`, `period_standard=19`). The chart shows candles, `ret_1`, `rolling_std_20`, `atr14`, `hl_spread`, and example actions `LONG_ALLOWED`, `SHORT_ALLOWED`, `NO_TRADE_LOW_VOL`, `NO_TRADE_HIGH_RISK`.
Boundary: visual thresholds are examples for agreement, not production config and not an Optuna runtime.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T113003Z.json`.

## State Version
`CALIBRATION-CURRENT-BLOCK01-LIVE-CHART-EXAMPLE-20260611T110200Z`

## Block 01 Short Rework Visual
Artifacts:
1. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.png`
2. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z_RU.md`
3. `reports/qa_gate/block01_short_rework_chart_20260611T113400Z.json`

Status: `SHORT_REWORK_VISUAL_AUDIT`.
Current fact: the first visual showed why `ret_1 > 0` can be misleading: inside a falling context, local upside is a pullback, not a LONG entry. Block 01 now has a documented proposed SHORT interpretation: `SHORT_MOMENTUM` and `SHORT_AFTER_PULLBACK`.
Proposed knobs: `ret_down_context_threshold`, `ret_pullback_up_threshold`, `ret_short_confirm_threshold`, `confirm_bars`, `vol_min/max`, `atr_min/max`, `hl_spread_max`.
Boundary: no config edits and no Optuna/APTuna runtime were launched.

## State Version
`CALIBRATION-CURRENT-BLOCK01-SHORT-REWORK-VISUAL-20260611T113400Z`

## Block 01 Parameter Range Map
Artifact: `docs/CALIBRATION_NODE_CURRENT/BLOCK_01_PRICE_VOLATILITY_KNOBS_AUDIT_2026-06-11_RU.md`.
Status: `PARAMETER_RANGE_MAP_DRAFT`.
Current fact: Block 01 now has a drafted min/max/step map for calculation windows, up/down context, pullback, confirmation, market activity filters, and primary ATR/target risk. This answers "from where to where" for `return_lookback`, `rolling_window`, `period_standard`, context thresholds, pullback thresholds, `confirm_bars`, `vol_min/max`, `atr_min/max`, and `hl_spread_min/max`.
Boundary: this is a TZ/range draft only. No config/code changes and no Optuna/APTuna runtime were launched.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260611T120336Z.json`.

## State Version
`CALIBRATION-CURRENT-BLOCK01-PARAMETER-RANGE-MAP-DRAFT-20260611T114800Z`

## New Chat Handoff
Artifact: `docs/CALIBRATION_NODE_CURRENT/HANDOFF_TO_NEW_CHAT_2026-06-19_RU.md`.
Status: `NEW_CHAT_HANDOFF_READY`.
Current fact: old chat is too large, so a clean handoff packet was created. It preserves the active source of truth, explains the 6-block route, captures Block 01 `PARAMETER_RANGE_MAP_DRAFT`, lists visual artifacts, and includes a startup prompt for the new chat.
Next fact: new chat should read the handoff and decide whether Block 01 becomes `AGREED/READY_FOR_CODE` or needs one more clarification before Block 02.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260619T184109Z.json`.

## State Version
`CALIBRATION-CURRENT-NEW-CHAT-HANDOFF-READY-20260619`

## F001 Strict Passport Runtime Connected
Artifact: `docs/CALIBRATION_NODE_CURRENT/passports/features/F001_ret_1_RU.md`.
Status: `F001_STRICT_PASSPORT_CONNECTED`.
Current fact: user-provided strict F001 passport is now connected to calibration/runtime. `F001_RET1_ALLOW` is calculated in `dataset.py`, preserved in OOF by validation/Optuna, and applied as an entry gate in `backtest.py`.
Calibration params: `F001_move` values `-1/1`; `F001_thr_pct` range `0.01..0.50`, step `0.01`.
Matrices updated: `configs/calibration_full_matrix_v1.yaml`, `configs/calibration_matrices/catalog_blocks/catalog_block_01_price_volatility.yaml`, `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`.
Validation: `py_compile PASS`; focused tests `25/25 OK`; Optuna runtime tests `65/65 OK`; matrix compile check PASS; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T091458Z.json`.
Next fact: wait for user decision to run F001/H001 or Block 01 with the new passport, or continue strictly to `F002 ret_3`.

## State Version
`CALIBRATION-CURRENT-F001-STRICT-PASSPORT-CONNECTED-20260622T091458Z`

## F001 Strict LONG 1d/1d Runtime
Artifact: `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`.
Status: `F001_LONG_1D1D_DONE_GOAL_FAIL`.
Current fact: ran F001 strict passport in `long_only` on train `2026-05-31`, OOS `2026-06-01`, matrix `configs/calibration_matrices/feature_sweep/h001_price_volatility_ret_1.yaml`, wide grid, 180 trials, 3 process workers.
Important fix: initial OOS showed `F001_RET1_ALLOW_gate_active=false`; `src/mlbotnav/oos_evaluate.py` was fixed to preserve `RUNTIME_ACTION_COLUMNS`. Focused validation after fix: `py_compile PASS`, `84 tests OK`.
Final launcher: `OK`, workers `3/3`, all `exit_code=0`.
Best worker: `w1`; selected params `F001_move=1.0`, `F001_thr_pct=0.19`, `min_abs_ema_gap=0.02`.
Final OOS: `net_return_pct=-5.352332468117016`, `trades=3`, `hit_rate=0.3333333333333333`, `max_drawdown_pct=-5.833320604926396`, `goal_pass=false`, `train_gate_pass=false`.
Gate diagnostics: `F001_RET1_ALLOW_gate_active=true`, raw signals `525`, after LONG mode `281`, after F001 gate `4`, entries filled `3`.
Next fact: F001 LONG on this 1d/1d window is `NO_GO`; user may choose SHORT F001 separately or move to next passport `F002 ret_3`.

## State Version
`CALIBRATION-CURRENT-F001-LONG-1D1D-GOAL-FAIL-20260622T092020Z`

## F001 Strict LONG Trade Map
Artifact: `reports/qa_gate/f001_strict_long_1d1d_trade_map_20260622T092020Z.png`.
Status: `F001_LONG_TRADE_MAP_READY`.
Current fact: generated a QA chart for the best F001 LONG OOS worker `w1`, showing the full OOS day plus three zoom panels. Each trade panel marks signal bar, entry, exit, TP `+1.20%`, and SL `-0.80%`.
Conclusion: all 3 trades exited by `timeout`; `target_reached=false`; TP and SL were not hit.

## State Version
`CALIBRATION-CURRENT-F001-LONG-TRADE-MAP-READY-20260622T092020Z`

## F001 Strict LONG No-Timeout Runtime
Artifact: `reports/qa_gate/f001_strict_long_no_timeout_1d1d_20260622T093702Z_RU.md`.
Chart: `reports/qa_gate/f001_strict_long_no_timeout_trade_map_20260622T093702Z.png`.
Status: `F001_LONG_NO_TIMEOUT_DONE_NO_GO`.
Current fact: timeout exit is now an explicit runtime switch. `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` accepts `-DisableTimeoutExit`, and Python entrypoints accept `--disable-timeout-exit`; backtest closes positions only by TP/SL or `end_of_data` when timeout is disabled.
Validation: `py_compile PASS`; `tests.test_backtest_fields`, `tests.test_pipeline_train_eval_gate_overrides`, `tests.test_optuna_search_runtime`: `78 tests OK`.
Health-check: `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T094448Z.json`.
Runtime: F001 strict LONG rerun on train `2026-05-31`, OOS `2026-06-01`, H001 matrix, wide grid, 180 trials, `TimeoutExit=off`, launcher `OK`, workers `3/3`.
Formal best: worker `w1`, params `F001_move=1.0`, `F001_thr_pct=0.09`, `min_abs_ema_gap=0.07`, OOS `0.0%`, `0` trades, `goal_pass=false`.
Best tradeful: worker `w2/w3`, params `F001_move=1.0`, `F001_thr_pct=0.05`, `min_abs_ema_gap=0.08`, OOS `-47.79331627195255%`, `6` trades, `hit_rate=0.0`, `max_drawdown=-47.79331627195255%`, `goal_pass=false`.
Conclusion: timeout is disabled correctly, but F001 LONG remains `NO_GO`; without timeout, tradeful positions mostly sit until SL.

## State Version
`CALIBRATION-CURRENT-F001-LONG-NO-TIMEOUT-NO-GO-20260622T093702Z`

## F001 Exit Baseline Decision
Status: `EXIT_BASELINE_TIMEOUT_ON`.
Current fact: user decided to keep exits clean and as before for the active calibration baseline: TP, SL, and timeout by `hold_bars`.
Boundary: do not use `-DisableTimeoutExit` for baseline F001/Block 01 runs. The no-timeout mode remains available as a diagnostic switch only.
Active comparison artifact: `reports/qa_gate/f001_strict_long_1d1d_20260622T092020Z_RU.md`; timeout-on OOS was `-5.352332468117016%`, `3` trades, all exits by `timeout`.

## State Version
`CALIBRATION-CURRENT-F001-EXIT-BASELINE-TIMEOUT-ON-20260622`

## Action Passport Calibration Rule
Artifacts:
1. `docs/CALIBRATION_NODE_CURRENT/TZ_ACTION_PASSPORT_CALIBRATION_2026-06-22_RU.md`
2. `configs/calibration_action_passports.yaml`
3. `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`

Status: `ACTION_PASSPORT_CALIBRATION_ACTIVE`.
Current fact: user declared old Optuna calibration proposals/configs were structurally wrong because they mixed feature, hypothesis, runtime, risk, and exit knobs. New baseline rule is passport-first: every calibration/backtest action needs an action passport and an explicit allowlist of tunable params.
Legacy boundary: old `calibration_full_matrix`, `catalog_blocks`, and `feature_sweep` matrices are not deleted, but are `legacy/frozen` for new baseline runs.
Code guard: `src/mlbotnav/optuna_space.py` now supports `passport_mode.enabled=true`; any row/search param outside `allowed_calibration_params` fails compile.
Active F001 allowlist: `F001_move`, `F001_thr_pct`.
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`: `13 tests OK`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; YAML parse PASS; F001 passport matrix compile PASS for `long_only` and `short_only`; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T101720Z.json`.
Next fact: future F001 baseline commands must use `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`; exit/dynamic-exit must wait for separate passports.

## State Version
`CALIBRATION-CURRENT-ACTION-PASSPORT-CALIBRATION-ACTIVE-20260622`

## F001 Passport-Action LONG Runtime
Artifact: `reports/qa_gate/f001_passport_action_long_1d1d_20260622T101953Z_RU.md`.
Status: `F001_PASSPORT_ACTION_LONG_DONE_NO_GO`.
Current fact: ran the clean F001 passport-action matrix `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml` in `long_only`, train `2026-05-31`, OOS `2026-06-01`, wide, 180 trials, timeout exit on.
Compile proof: `passport_mode.enabled=true`; compiled profiles only `F001_move`, `F001_thr_pct`.
Launcher: `OK`, workers `3/3`.
Formal best: `w3`, `0.0%`, `0` trades, not tradeful.
Best tradeful: `w1`, params `F001_move=1.0`, `F001_thr_pct=0.28`, OOS `-5.1298471326372%`, `1` trade, exit `timeout`.
Other tradeful: `w2`, `F001_thr_pct=0.10`, OOS `-28.876033596834784%`, `8` trades.
Conclusion: infrastructure/passport path works, F001 LONG remains `NO_GO`.
Residual cleanup: Optuna core runtime fields are still sampled from engine grids (`horizon_bars`, `p_enter_long`, `p_enter_short`, `min_expected_move_pct`, `notional_usd`); for full passport purity they need a runtime/backtest subpassport or fixed single-value grids.
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `78 tests OK`; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T102340Z.json`.

## State Version
`CALIBRATION-CURRENT-F001-PASSPORT-ACTION-LONG-NO-GO-20260622T101953Z`

## Block Passport Registry
Artifact: `configs/calibration_action_passports.yaml`.
Status: `BLOCK_PASSPORT_REGISTRY_CONNECTED`.
Current fact: user chose one main config for all passports. The registry now has blocks `B001..B006`, Russian names, active/planned passports inside each block, and runtime/backtest subpassport placeholders.
Active F001 location: `blocks.B001.active_passports.F001`; `B001` is `price_volatility` / `Цена и волатильность`.
Planned F002 location: `blocks.B001.planned_passports.F002`; do not use legacy H002 matrix as baseline.
Code guard: `src/mlbotnav/optuna_space.py` now validates passport matrices against the registry (`registry_path`, `registry_block_id`, `registry_passport_id`, `action_id`, allowlist, active matrix path).
Validation: `py_compile PASS`; `tests.test_optuna_space_constraints`, `tests.test_optuna_search_runtime`: `79 tests OK`; env override compile PASS for F001 passport matrix.

## State Version
`CALIBRATION-CURRENT-BLOCK-PASSPORT-REGISTRY-CONNECTED-20260622`

## RET_N F001-F005 Strict Passport Family
Artifact: `docs/CALIBRATION_NODE_CURRENT/passports/features/RET_N_F001_F005_strict_passports.md`.
Status: `RET_N_F001_F005_PASSPORTS_CONNECTED`.
Current fact: user supplied `C:\Users\007\Downloads\RET_N_F001_F005_strict_passports.md`; the project now has active B001 passports for F001-F005 under `configs/calibration_action_passports.yaml`.
Active matrices: `configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml`, `F002_ret3_entry_filter.yaml`, `F003_ret6_entry_filter.yaml`, `F004_ret12_entry_filter.yaml`, `F005_ret24_entry_filter.yaml`.
Runtime fact: `src/mlbotnav/dataset.py` can compute `F001_RET1_ALLOW`, `F002_RET3_ALLOW`, `F003_RET6_ALLOW`, `F004_RET12_ALLOW`, `F005_RET24_ALLOW`; F002-F005 are emitted only when their own passport params are present.
Backtest fact: `src/mlbotnav/backtest.py` now applies present `ENTRY_ACTION_ALLOW` columns as an AND gate and reports `entry_action_gate_columns`.
Validation: `py_compile PASS`; focused tests `96/96 OK`; F001-F005 matrix compile PASS; `text_guard PASS`, artifact `reports/qa_gate/recovery_r5_text_guard_20260622T112135Z.json`.
Resolved fix: `src/mlbotnav/optuna_space.py` now preserves the `max` anchor when `step` does not land on it exactly. F003 `F003_thr_pct` compiles to `60` values and includes `1.20`.
Validation after fix: `py_compile PASS`; focused tests `98/98 OK`; F003 matrix compile proof `60 0.03 [1.17, 1.19, 1.2] True`.

## State Version
`CALIBRATION-CURRENT-RET-N-F001-F005-PASSPORTS-CONNECTED-20260622T112135Z`

## State Version
`CALIBRATION-CURRENT-RET-N-MAX-ANCHOR-FIX-20260622`

## B001 RET_N Ladder Tournament
Status: `B001_RET_N_LADDER_READY_SMOKE_OK`.
Current fact: implemented a tournament path for one block `B001` with five RET_N passports F001-F005. It generates all `31` non-empty passport combinations and runs each combination as a clean passport matrix.
Registry: `configs/calibration_action_passports.yaml` now includes `blocks.B001.active_passports.B001_RET_N_TOURNAMENT`.
Generator: `src/mlbotnav/b001_ret_n_ladder_tournament.py`.
Runner: `APTuna/run_b001_ret_n_ladder_tournament.ps1`.
Manifest artifact: `reports/qa_gate/b001_ret_n_ladder_matrices_20260622T115638Z/manifest.json`.
Smoke artifact: `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T115930Z.json`.
Runtime rule: every combo gates entry with `AND` over present runtime action columns. Example: `F002+F005` means both `F002_RET3_ALLOW` and `F005_RET24_ALLOW` must pass.
Smoke result: one-combo `B001_RET_N_F001` LONG smoke completed through APTuna process pool with exit code `0`; tournament report extracted `best_oos`. The smoke had `0` OOS trades and is not a candidate.
Validation: `py_compile PASS`; generator/space/dataset/backtest focused tests `35/35 OK`; extended focused tests including Optuna runtime `83/83 OK`.
Full run command: `powershell -ExecutionPolicy Bypass -File .\APTuna\run_b001_ret_n_ladder_tournament.ps1 -Mode long_only -TrainDate 2026-05-31 -TestDate 2026-06-01 -GoalNetReturnPct 1 -Threads 9 -SearchWorkers 9 -ProcessWorkers 3 -SearchWorkersPerProcess 3 -OptunaTrials 180 -OptunaTimeoutSec 900 -CalibrationGridPreset wide -ForceProfileEdgeCoverage on -UseTemporaryUnlock`.

## State Version
`CALIBRATION-CURRENT-B001-RET-N-LADDER-READY-SMOKE-OK-20260622T115930Z`

## B001 Solo Selection Decision
Status: `B001_RET_N_SOLO_SELECTION_ONLY`.
Current fact: after full LONG 31-combo run `reports/qa_gate/b001_ret_n_ladder_tournament_long_only_20260622T120806Z.json`, user decided not to use expanded in-block combination calibration as baseline.
Reason: `31/31` combos were technically OK, but `28/31` had zero OOS trades. Best combo `F002+F004` had only `1` OOS trade, `+0.7845424236948562%` at `10x`, exit `timeout`, `target_reached=false`; it is `NO_CANDIDATE`.
Active rule: B001 baseline searches only solo features F001-F005; promote at most one best solo feature if tradeful and non-negative on OOS.
Technical guard: `APTuna/run_b001_ret_n_ladder_tournament.ps1` now defaults to `EndIndex=5`; `EndIndex > 5` is blocked unless `-EnableCombinationTournament` is passed explicitly for diagnostic-only runs.
Registry: `B001_RET_N_TOURNAMENT` is now `diagnostic_only_disabled_for_baseline`.
Validation: default dry-run selected 5 solo rows; `EndIndex=31` without diagnostic switch blocks; `py_compile PASS`; focused tests `35/35 OK`.

## State Version
`CALIBRATION-CURRENT-B001-RET-N-SOLO-SELECTION-ONLY-20260622`

## MACD F013-F015 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/macd_f013_f015_long_short_audit_20260622T151954Z_RU.md`.
Current fact: implemented `B007/MACD импульс` with solo passports F013/F014/F015 and ran clean LONG/SHORT on train `2026-05-31`, OOS `2026-06-01`, wide, 180 trials, timeout exit on.
Matrices: `configs/calibration_matrices/passport_actions/F013_macd_line_1m_entry_filter.yaml`, `F014_macd_signal_1m_entry_filter.yaml`, `F015_macd_hist_1m_entry_filter.yaml`.
Runtime/backtest: dataset emits `F013_MACDLINE_ALLOW`, `F014_MACDSIGNAL_ALLOW`, `F015_MACDHIST_ALLOW`; backtest gates entries by these present action columns.
Fix applied: Optuna `run_signature` now includes `space_signature` so different passport matrices cannot resume each other's stored trials. Pre-fix MACD runs were discarded and rerun.
Clean result: all six launches `OK`; selected params isolation `PASS`; no non-negative tradeful candidate.
Best tradeful by OOS: `F014 LONG`, `-2.9779083375433224%`, `3` trades, `0/3` wins/losses, all exits `timeout`.
Final status: `NO_GO`.
Validation: `py_compile PASS`; focused tests `112/112 OK`; YAML parse PASS; matrix compile PASS; `text_guard PASS` at `reports/qa_gate/recovery_r5_text_guard_20260622T152122Z.json`.

## State Version
`CALIBRATION-CURRENT-MACD-F013-F015-NO-GO-20260622T151954Z`

## F016 ADX14 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f016_adx14_long_short_audit_20260622T153403Z_RU.md`.
Current fact: implemented `B008/ADX14 сила тренда` with solo passport F016 `adx14_1m`; action output is `F016_ADX14_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F016_adx14_1m_entry_filter.yaml`.
Runtime/backtest: dataset emits `F016_ADX14_ALLOW` only when `F016_cmp`/`F016_level` are present; backtest gates entries by this present action column.
Clean result: LONG selected `LESS level=41`, OOS `-13.43232421418481%`, `3` trades, `0/3` wins/losses, all exits `timeout`; SHORT selected `LESS level=28`, OOS `-28.526707456698695%`, `13` trades, `1/12` wins/losses, all exits `timeout`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `114/114 OK`; YAML parse PASS; matrix compile PASS for LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-F016-ADX14-NO-GO-20260622T153403Z`

## STOCH F017-F018 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/stoch_f017_f018_long_short_audit_20260622T154340Z_RU.md`.
Current fact: implemented `B009/Stochastic 14 K/D` with combined passport F017_F018 `stochastic_14_1m`; action output is `F017_F018_STOCH14_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F017_F018_stoch14_combined_entry_filter.yaml`.
Runtime/backtest: dataset emits `F017_F018_STOCH14_ALLOW` only when `F017_F018_*` params are present; backtest gates entries by this present action column.
Clean result: LONG effective params `LEVEL K LESS level=72`, OOS `-84.05333161848922%`, `51` trades, wins/losses `2/49`, exits `timeout=50`, `sl=1`; SHORT effective params `KD_CROSS UP LOW low=40 high=60 gap=0`, OOS `-17.53680624691214%`, `6` trades, wins/losses `0/6`, exits `timeout=6`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `116/116 OK`; YAML parse PASS; matrix compile PASS for LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-STOCH-F017-F018-NO-GO-20260622T154340Z`

## VOLUME F019-F021 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/volume_f019_f021_long_short_audit_20260622T160207Z_RU.md`.
Current fact: implemented `B010/Объем и поток` with solo passports F019 `vol_chg_1m`, F020 `vol_z_20_1m`, F021 `delta_volume_1m`.
Matrices: `configs/calibration_matrices/passport_actions/F019_vol_chg_1m_entry_filter.yaml`, `F020_vol_z20_1m_entry_filter.yaml`, `F021_delta_volume_1m_entry_filter.yaml`.
Runtime/backtest: dataset emits `F019_VOLCHG_ALLOW`, `F020_VOLZ20_ALLOW`, `F021_DELTAVOL_ALLOW` only when matching params are present; backtest gates entries by present action columns.
Fix applied: F021 `TRUE_DELTA` now requires `buy_volume`/`sell_volume`; if absent, signal is `0`. Pre-fix F021 runs were discarded and F021 was rerun.
Clean result: F019 LONG `-57.151405%/26 trades`; F019 SHORT `-11.835584%/4 trades`; F020 LONG `0%/0 trades`; F020 SHORT `-25.290896%/9 trades`; F021 LONG post-fix `-77.699906%/37 trades`; F021 SHORT post-fix `0%/0 trades`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `118/118 OK`; YAML parse PASS; matrix compile PASS for all F019-F021 LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-VOLUME-F019-F021-NO-GO-20260622T160207Z`

## F022 OBV Slope 5 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f022_obv_slope5_long_short_audit_20260622T162356Z_RU.md`.
Current fact: implemented `B011/OBV slope 5` with solo passport F022 `obv_slope_5_1m`; action output is `F022_OBVSLOPE5_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F022_obv_slope5_1m_entry_filter.yaml`.
Runtime/backtest: dataset emits `F022_OBVSLOPE5_ALLOW` only when `F022_slope_dir`/`F022_slope_thr` are present; backtest gates entries by this present action column.
Clean result: LONG selected `UP thr=7.2`, OOS `0.000000%`, `0` trades; SHORT selected `DOWN thr=8.2`, OOS `-17.47906713400207%`, `3` trades, wins/losses `0/3`, exits `timeout=2`, `sl=1`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `120/120 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-F022-OBV-SLOPE5-NO-GO-20260622T162356Z`

## F023 MFI14 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f023_mfi14_long_short_audit_20260622T163809Z_RU.md`.
Current fact: implemented `B012/MFI14` with combined solo passport F023 `mfi14_1m`; action output is `F023_MFI14_ALLOW`.
Matrix: `configs/calibration_matrices/passport_actions/F023_mfi14_1m_combined_entry_filter.yaml`.
Runtime/backtest: dataset emits `F023_MFI14_ALLOW` only when `F023_*` params are present; backtest gates entries by this present action column.
Clean result: LONG selected `LEVEL GREATER level=88`, OOS `-4.474396882494847%`, `1` trade, exit `timeout`; SHORT selected `LEVEL LESS level=81`, OOS `-20.54653686623259%`, `6` trades, wins/losses `0/6`, exits `timeout=6`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `122/122 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-F023-MFI14-NO-GO-20260622T163809Z`

## DENSITY/VPOC Block A F025/F029/F033/F034 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/density_vpoc_block_a_f025_f029_f033_f034_audit_20260622T165812Z_RU.md`.
Current fact: implemented `B013/DENSITY_A_VPOC_CORE` with solo passports F025 `density_vpoc_distance_60_1m`, F029 `density_vpoc_distance_240_1m`, F033 `density_vpoc_drift_20_1m`, and F034 `density_cluster_ratio_60_240_1m`.
Matrix files: `F025_vpocdist60_entry_filter.yaml`, `F029_vpocdist240_entry_filter.yaml`, `F033_vpocdrift20_entry_filter.yaml`, `F034_clusterratio_entry_filter.yaml`.
Runtime/backtest: dataset emits `F025_VPOCDIST60_ALLOW`, `F029_VPOCDIST240_ALLOW`, `F033_VPOCDRIFT20_ALLOW`, `F034_CLUSTERRATIO_ALLOW` only when matching params are present; backtest gates entries by the present action column.
Clean result: F025 LONG `-60.069331%/20`, F025 SHORT `-6.778638%/3`; F029 LONG `0%/0`, F029 SHORT `-18.625751%/6`; F033 LONG `-14.115533%/4`, F033 SHORT `-3.624721%/1`; F034 LONG `0%/0`, F034 SHORT `-10.692022%/3`.
Final status: `NO_GO`; best tradeful was F033 SHORT but still negative.
Validation: `py_compile PASS`; focused tests `124/124 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.
Boundary: Block B (`F026/F027/F030/F031`) and Block C (`F028/F032`) from the same passport file are planned, not run yet.

## State Version
`CALIBRATION-CURRENT-DENSITY-VPOC-BLOCK-A-NO-GO-20260622T165812Z`

## LEVEL/RANGE/CHANNEL Block A F035-F037 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/level_range_channel_block_a_f035_f036_f037_audit_20260622T171500Z_RU.md`.
Current fact: implemented `B014/LEVEL_A уровни поддержки/сопротивления` with solo passports F035 `support_distance_1m`, F036 `resistance_distance_1m`, and F037 `level_strength_1m`.
Matrix files: `F035_supportdist_entry_filter.yaml`, `F036_resdist_entry_filter.yaml`, `F037_levelstrength_entry_filter.yaml`.
Runtime/backtest: dataset emits `F035_SUPPORTDIST_ALLOW`, `F036_RESDIST_ALLOW`, `F037_LEVELSTRENGTH_ALLOW` only when matching params are present; backtest gates entries by the present action column.
Clean result: F035 LONG `-6.153364%/2`, F035 SHORT `-18.625751%/6`; F036 LONG `-12.920893%/3`, F036 SHORT `-13.301553%/4`; F037 LONG `0%/0`, F037 SHORT `-18.104190%/7`.
Final status: `NO_GO`; best tradeful was F035 LONG but still negative.
Validation: `py_compile PASS`; focused tests `126/126 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.
Boundary: F038 `position_in_range_1m` and F039 `trend_channel_pos_1m` from the same passport file are planned, not run yet.

## State Version
`CALIBRATION-CURRENT-LEVEL-RANGE-CHANNEL-BLOCK-A-NO-GO-20260622T171500Z`

## FIBONACCI_GRID F040-F041 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/fibonacci_grid_f040_f041_long_short_audit_20260622T173112Z_RU.md`.
Current fact: implemented `B015/FIBONACCI_GRID anchor grid` with F040 `fib_0382_distance_1m` and F041 `fib_0618_distance_1m`.
Matrix files: `F040_fib0382dist_entry_filter.yaml`, `F041_fib0618dist_entry_filter.yaml`.
Runtime/backtest: dataset computes confirmed pivot fib grid and emits `F040_FIB0382DIST_ALLOW` / `F041_FIB0618DIST_ALLOW` only when matching params are present; backtest gates entries by the present action column.
Clean result: F040 LONG `0%/0`, F040 SHORT `-27.970937%/9`; F041 LONG `0%/0`, F041 SHORT `-9.615680%/4`.
Final status: `NO_GO`; best tradeful was F041 SHORT but still negative.
Validation: `py_compile PASS`; focused tests `128/128 OK`; matrix compile PASS for F040/F041 LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-FIBONACCI-GRID-F040-F041-NO-GO-20260622T173112Z`

## ENTRY_QUALITY_CONTEXT F042-F044 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/entry_quality_context_f042_f044_long_short_audit_20260622T175033Z_RU.md`.
Current fact: implemented `B016/ENTRY_QUALITY_CONTEXT контекст входа` with F044 `rr_context_estimate_1m`, F042 `tp_context_distance_1m`, and F043 `sl_context_distance_1m`.
Matrix files: `F044_rrcontext_entry_filter.yaml`, `F042_tpcontext_entry_filter.yaml`, `F043_slcontext_entry_filter.yaml`.
Runtime/backtest: dataset computes entry context from `SWING_LEVELS`, `DENSITY_VPOC`, or `FIBONACCI_GRID` and emits canonical plus side-aware action columns. Backtest uses side-aware columns by actual LONG/SHORT signal.
Clean result: F044 LONG `-1.145944%/1`, F044 SHORT `-19.784205%/8`; F042 LONG `-17.392676%/3`, F042 SHORT `0%/0`; F043 LONG `0%/0`, F043 SHORT `-30.313954%/10`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused tests `130/130 OK`; matrix compile PASS for all F042-F044 LONG/SHORT; latest text_guard PASS.

## State Version
`CALIBRATION-CURRENT-ENTRY-QUALITY-CONTEXT-F042-F044-NO-GO-20260622T175033Z`

## BREAKOUT_RETEST F045-F049 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b017_breakout_retest_f045_f049_audit_20260622T181600Z.md`.
Current fact: user supplied `BREAKOUT_RETEST_F045_F049_strict_passport.md`; implemented B017 with isolated solo passports F048 `swing_high_break_flag_1m`, F049 `swing_low_break_flag_1m`, F045 `breakout_flag_1m`, F047 `retest_flag_1m`, and F046 `false_breakout_flag_1m`.
Matrix files: `F048_swinghighbreak_entry_filter.yaml`, `F049_swinglowbreak_entry_filter.yaml`, `F045_breakout_entry_filter.yaml`, `F047_retest_entry_filter.yaml`, `F046_falsebreak_entry_filter.yaml`.
Runtime/backtest: dataset computes confirmed swing levels and breakout/retest gates; backtest gates entries by the present single action column.
Clean result: F048 LONG `0%/0`, F048 SHORT `0%/0`; F049 LONG `-12.862590%/6`, F049 SHORT `-20.254568%/4`; F045 LONG `0%/0`, F045 SHORT `-3.482265%/2`; F047 LONG `-11.000000%/1`, F047 SHORT `-12.464525%/3`; F046 LONG `0%/0`, F046 SHORT `-5.366391%/1`.
Final status: `NO_GO`; no candidate promoted. Best tradeful was F045 SHORT, but still negative.
Validation: `py_compile PASS`; focused B017 tests `3/3 OK`; matrix compile PASS for F045-F049 LONG/SHORT; latest text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T181926Z.json`.

## State Version
`CALIBRATION-CURRENT-BREAKOUT-RETEST-F045-F049-NO-GO-20260622T181600Z`

## MARKET_STRUCTURE F050-F052 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_POSITIVE_TEST_CANDIDATE`.
Artifact: `reports/qa_gate/b018_market_structure_f050_f052_audit_20260622T183500Z.md`.
Current fact: user supplied `MARKET_STRUCTURE_F050_F052_strict_passport.md`; implemented B018 with isolated solo passports F050 `bos_up_flag_1m`, F051 `bos_down_flag_1m`, and F052 `choch_flag_1m`.
Matrix files: `F050_bosup_entry_filter.yaml`, `F051_bosdown_entry_filter.yaml`, `F052_choch_entry_filter.yaml`.
Runtime/backtest: dataset computes internal/external market structure state and emits `F050_BOSUP_ALLOW`, `F051_BOSDOWN_ALLOW`, `F052_CHOCH_ALLOW`; backtest gates entries by the present single action column.
Clean result: F050 LONG `0%/0`, F050 SHORT `0%/0`; F051 LONG `0%/0`, F051 SHORT `+2.810523%/1`; F052 LONG `0%/0`, F052 SHORT `0%/0`.
Final status: `POSITIVE_TEST_CANDIDATE`; F051 SHORT is positive but only one OOS trade, so no production GO.
Validation: `py_compile PASS`; focused B018 tests `3/3 OK`; matrix compile PASS for F050-F052 LONG/SHORT.

## State Version
`CALIBRATION-CURRENT-MARKET-STRUCTURE-F050-F052-POSITIVE-TEST-CANDIDATE-20260622T183500Z`

## CANDLE_PATTERNS F053-F060 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b019_candle_patterns_f053_f060_audit_20260622T190530Z.md`.
Current fact: implemented `B019/CANDLE_PATTERNS свечные паттерны` with isolated solo passports F055 `pin_bar_bull_flag_1m`, F056 `pin_bar_bear_flag_1m`, F059 `engulf_bull_flag_1m`, F060 `engulf_bear_flag_1m`, F057 `hammer_flag_1m`, F058 `shooting_star_flag_1m`, F054 `inside_bar_flag_1m`, and F053 `doji_flag_1m`.
Runtime/backtest: dataset uses only closed candles via shift(1)/shift(2) and emits `F053_DOJI_ALLOW`, `F054_INSIDEBAR_ALLOW`, `F055_PINBULL_ALLOW`, `F056_PINBEAR_ALLOW`, `F057_HAMMER_ALLOW`, `F058_SHOOTINGSTAR_ALLOW`, `F059_ENGULFBULL_ALLOW`, `F060_ENGULFBEAR_ALLOW`; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. F059 LONG `-60.087983%/22`; F054 SHORT `-8.438667%/2`; F053 LONG `-11.213252%/3`; all other runs `0%/0`.
Validation: `py_compile PASS`; focused B019 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-CANDLE-PATTERNS-F053-F060-NO-GO-20260622T190530Z`

## DIVERGENCE_PATTERNS F061-F066 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b020_divergence_patterns_f061_f066_audit_20260622T193300Z.md`.
Current fact: implemented `B020/DIVERGENCE_PATTERNS дивергенции` with isolated solo passports F061 `rsi_bull_div_flag_1m`, F062 `rsi_bear_div_flag_1m`, F063 `macd_bull_div_flag_1m`, F064 `macd_bear_div_flag_1m`, F065 `obv_bull_div_flag_1m`, and F066 `obv_bear_div_flag_1m`.
Runtime/backtest: dataset computes confirmed no-repaint price pivot pairs and takes RSI/MACD/OBV values at the same price pivot bars; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. F061 LONG `-7.123789%/2`; F063 LONG `-37.837211%/12`; F065 LONG `-10.822526%/4`; all other runs `0%/0`.
Validation: `py_compile PASS`; focused B020 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-DIVERGENCE-PATTERNS-F061-F066-NO-GO-20260622T193300Z`

## PATTERN_QUALITY F067-F068 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b021_pattern_quality_f067_f068_audit_20260622T194700Z.md`.
Current fact: implemented `B021/PATTERN_QUALITY качество паттерна` with isolated solo passports F067 `pattern_strength_1m` and F068 `pattern_age_bars_1m`.
Runtime/backtest: dataset builds a closed-bar `pattern_event` from already computed pattern flags and emits `F067_PATTERNSTRENGTH_ALLOW` / `F068_PATTERNAGE_ALLOW`; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. F067 LONG `0%/0`; F067 SHORT `-18.202040%/6`; F068 LONG `-6.153364%/2`; F068 SHORT `-59.898861%/26`.
Validation: `py_compile PASS`; focused B021 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-PATTERN-QUALITY-F067-F068-NO-GO-20260622T194700Z`

## CHART_PATTERNS F069-F077 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b022_chart_patterns_f069_f077_audit_20260622T202100Z.md`.
Current fact: implemented `B022/CHART_PATTERNS графические паттерны` with isolated solo passports F069-F077.
Runtime/backtest: dataset computes closed-bar chart-pattern action gates `F069_DOUBLEBOTTOM_ALLOW`, `F070_DOUBLETOP_ALLOW`, `F071_HEADSHOULDERS_ALLOW`, `F072_INVHEADSHOULDERS_ALLOW`, `F073_TRIANGLE_ALLOW`, `F074_PENNANT_ALLOW`, `F075_WEDGERISING_ALLOW`, `F076_WEDGEFALLING_ALLOW`, and `F077_RANGEFLAG_ALLOW`; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. Zero-trade runs are neutral only; tradeful runs are all negative, with best tradeful F072 LONG `-6.837599%/1`.
Validation: `py_compile PASS`; focused B022 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-CHART-PATTERNS-F069-F077-NO-GO-20260622T202100Z`

## PATTERN_CONFIRMATION F078-F079 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b023_pattern_confirmation_f078_f079_audit_20260622T203700Z.md`.
Current fact: implemented `B023/PATTERN_CONFIRMATION confirmation of existing pattern_event` with isolated solo passports F079 `pattern_level_confirm_flag_1m` and F078 `pattern_volume_confirm_flag_1m`.
Runtime/backtest: dataset confirms existing pattern events and emits `F079_PATTERNLEVELCONF_ALLOW` / `F078_PATTERNVOLCONF_ALLOW`; backtest gates entries by the present single action column.
Clean result: no positive tradeful candidate. F079 LONG/SHORT had zero OOS trades; F078 LONG `-27.682109%/7`; F078 SHORT `-7.323394%/4`.
Validation: `py_compile PASS`; focused B023 tests `3/3 OK`; YAML parse/matrix compile PASS; launcher post-audit `text_guard PASS`.

## State Version
`CALIBRATION-CURRENT-PATTERN-CONFIRMATION-F078-F079-NO-GO-20260622T203700Z`

## PATTERN_COMPOSITE_ENTRY F080-F081 Passport Run
Status: `IMPLEMENTED_SIDE_SPECIFIC_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b024_pattern_composite_entry_f080_f081_audit_20260622T205500Z.md`.
Current fact: implemented `B024/PATTERN_COMPOSITE_ENTRY kompozitnyy pattern entry` with side-specific passports F080 `pattern_structure_volume_entry_long_1m` and F081 `pattern_structure_volume_entry_short_1m`.
Runtime/backtest: dataset emits `F080_PATTERNLONG_ALLOW` and `F081_PATTERNSHORT_ALLOW`; backtest treats F080 as LONG-only and F081 as SHORT-only.
Clean result: F080 LONG `0.000000%/0`; F081 SHORT `-5.359455%/1`, exit `timeout=1`.
Final status: `NO_GO`; no candidate promoted.
Validation: `py_compile PASS`; focused B024 tests `3/3 OK`; YAML parse/matrix compile PASS; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T210111Z.json`.

## State Version
`CALIBRATION-CURRENT-PATTERN-COMPOSITE-ENTRY-F080-F081-NO-GO-20260622T205500Z`

## PATTERN_TRADE_CONTEXT F082-F083 Passport Run
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/b025_pattern_trade_context_f082_f083_audit_20260622T211600Z.md`.
Current fact: implemented `B025/PATTERN_TRADE_CONTEXT SL/TP context` with isolated solo passports F082 and F083.
Runtime/backtest: dataset emits side-aware F082/F083 gates and backtest applies them as entry filters; baseline exits remain TP/SL/timeout.
Clean result: F082 LONG `0%/0`, F082 SHORT `-25.094610%/7`; F083 LONG `-35.921536%/12`; F083 SHORT `-70.280106%/35`.
Final status: `NO_GO`; no positive tradeful candidate.
Validation: `py_compile PASS`; focused B025 tests `3/3 OK`; matrix compile/passport allowlist PASS; runtime launcher OK; text_guard PASS `reports/qa_gate/recovery_r5_text_guard_20260622T211551Z.json`.

## State Version
`CALIBRATION-CURRENT-PATTERN-TRADE-CONTEXT-F082-F083-NO-GO-20260622T211600Z`

## F001-F083 Passport Route Full Audit
Status: `WARN_WITH_COMPLETENESS_GAPS`.
Artifact: `reports/qa_gate/f001_f083_passport_full_audit_20260623.md`.
Matrix purity: `PASS` for existing executable passport matrices (`73` entries, `146` compiled spaces).
Completeness in the pre-F024 audit snapshot: not full; F024 was open then and is closed below, `F026/F027/F028/F030/F031/F032/F038/F039` planned only, `F017/F018` combined.
Runtime/backtest: normal single-pass route isolated; hardening needed to ignore stale `F*_ALLOW` columns outside the active passport action.

## State Version
`CALIBRATION-CURRENT-F001-F083-FULL-AUDIT-WARN-WITH-COMPLETENESS-GAPS-20260623`

## F024 VWAP Distance Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f024_vwap_distance_long_short_audit_20260623T055200Z.md`.
Current fact: previously open `F024` is now implemented as `B026/F024` with isolated action `F024_VWAPDIST_ALLOW`.
Runtime/backtest: dataset computes the action from previous closed-bar VWAP distance; OOS diagnostics show only `F024_VWAPDIST_ALLOW` as entry action gate.
Clean result: F024 LONG `-17.894975%/8`; F024 SHORT `0%/0`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F026/F027/F028/F030/F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F024-VWAP-DISTANCE-NO-GO-20260623T055200Z`

## F026 Density Bin Share 60 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f026_binshare60_long_short_audit_20260623T060100Z.md`.
Current fact: `F026` is now implemented under `B013` with isolated action `F026_BINSHARE60_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_bin_share_60`; OOS diagnostics show only `F026_BINSHARE60_ALLOW` as entry action gate.
Clean result: F026 LONG `-1.145944%/1`; F026 SHORT `-24.712835%/9`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F027/F028/F030/F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F026-BINSHARE60-NO-GO-20260623T060100Z`

## F027 Density Cluster Share 60 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f027_clustershare60_long_short_audit_20260623T062300Z.md`.
Current fact: `F027` is now implemented under `B013` with isolated action `F027_CLUSTERSHARE60_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_cluster_share_60`; OOS diagnostics show only `F027_CLUSTERSHARE60_ALLOW` as entry action gate.
Clean result: F027 LONG `-6.153364%/2`; F027 SHORT `-18.625751%/6`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F028/F030/F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F027-CLUSTERSHARE60-NO-GO-20260623T062300Z`

## F028 Density VPOC Share 60 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f028_vpocshare60_long_short_audit_20260623T064000Z.md`.
Current fact: `F028` is now implemented under `B013` with isolated action `F028_VPOCSHARE60_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_vpoc_share_60`; OOS diagnostics show only `F028_VPOCSHARE60_ALLOW` as entry action gate.
Clean result: F028 LONG `-1.145944%/1`; F028 SHORT `-18.625751%/6`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F030/F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F028-VPOCSHARE60-NO-GO-20260623T064000Z`

## F030 Density Bin Share 240 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f030_binshare240_long_short_audit_20260623T070000Z.md`.
Current fact: `F030` is now implemented under `B013` with isolated action `F030_BINSHARE240_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_bin_share_240`; OOS diagnostics show only `F030_BINSHARE240_ALLOW` as entry action gate.
Clean result: F030 LONG `-13.432324%/3`; F030 SHORT `-24.712835%/9`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F031/F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F030-BINSHARE240-NO-GO-20260623T070000Z`

## F031 Density Cluster Share 240 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f031_clustershare240_long_short_audit_20260623T071000Z.md`.
Current fact: `F031` is now implemented under `B013` with isolated action `F031_CLUSTERSHARE240_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_cluster_share_240`; OOS diagnostics show only `F031_CLUSTERSHARE240_ALLOW` as entry action gate.
Clean result: F031 LONG `-6.153364%/2`; F031 SHORT `-55.142239%/26`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F032`, `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F031-CLUSTERSHARE240-NO-GO-20260623T071000Z`

## F032 Density VPOC Share 240 Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f032_vpocshare240_long_short_audit_20260623T072500Z.md`.
Current fact: `F032` is now implemented under `B013` with isolated action `F032_VPOCSHARE240_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar `density_vpoc_share_240`; OOS diagnostics show only `F032_VPOCSHARE240_ALLOW` as entry action gate.
Clean result: F032 LONG `-6.153364%/2`; F032 SHORT `-18.625751%/6`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F038/F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F032-VPOCSHARE240-NO-GO-20260623T072500Z`

## F038 Position In Range Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f038_rangepose_long_short_audit_20260623T074000Z.md`.
Current fact: `F038` is now implemented under `B014` with isolated action `F038_RANGEPOSE_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar 240-bar range position; OOS diagnostics show only `F038_RANGEPOSE_ALLOW` as entry action gate.
Clean result: F038 LONG `-13.432324%/3`; F038 SHORT `-4.489987%/1`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route gaps: `F039`, `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F038-RANGEPOSE-NO-GO-20260623T074000Z`

## F039 Trend Channel Position Gap Closure
Status: `IMPLEMENTED_LONG_SHORT_AUDITED_NO_GO`.
Artifact: `reports/qa_gate/f039_channelpos_long_short_audit_20260623T080500Z.md`.
Current fact: `F039` is now implemented under `B014` with isolated action `F039_CHANNELPOS_ALLOW`.
Runtime/backtest: dataset emits the action from previous closed-bar linear regression channel position; OOS diagnostics show only `F039_CHANNELPOS_ALLOW` as entry action gate.
Clean result: F039 LONG `-17.392676%/3`; F039 SHORT `0.000000%/0`. No promotion.
Validation: `py_compile PASS`; focused tests `3/3 OK`; YAML parse/matrix compile PASS; launcher ledger/text_guard PASS.
Remaining route items: `F017/F018` combined decision, stale-action-column hardening.

## State Version
`CALIBRATION-CURRENT-F039-CHANNELPOS-NO-GO-20260623T080500Z`

## Passport Result Register F001-F083
Status: `ACTIVE_RESULT_REGISTER`.
Artifact: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_RESULT_REGISTER_RU.md`.
Audit: `reports/qa_gate/passport_result_register_audit_20260623T084702Z.md`.

Current fact: the F001-F083 passport route now has a compact result register. It records all feature ids, blocks, decisions, and promotion boundaries.

Important state:
1. Production GO: none.
2. Positive test candidate: `F051 BOS down SHORT`, `+2.810523%`, `1` OOS trade.
3. `F051 SHORT` validation is complete and failed promotion; no current F001-F083 candidate is ready for promotion.
4. Old broad matrices/chronology stay frozen references unless explicitly migrated through passport review.

Validation: id coverage PASS; text_guard PASS, report `reports/qa_gate/recovery_r5_text_guard_20260623T084932Z.json`.

## State Version
`CALIBRATION-CURRENT-F001-F083-RESULT-REGISTER-20260623T084702Z`

## F051 SHORT Multi-Day Validation
Status: `VALIDATION_FAIL_NO_PROMOTION`.
Artifact: `reports/qa_gate/f051_short_multiday_validation_audit_20260623T091000Z.md`.

Current fact: `F051 BOS down SHORT` did not reproduce outside the original one-day positive window.

Validation result:
1. Original baseline `2026-05-31 -> 2026-06-01`: `+2.810523%`, `1` trade.
2. New adjacent windows `2026-05-29`, `2026-05-30`, `2026-05-31`: all `0%`, `0` trades.
3. Gate isolation was clean: `F051_BOSDOWN_ALLOW` only.

State decision: no F001-F083 candidate is promotable after this check.

## State Version
`CALIBRATION-CURRENT-F051-SHORT-VALIDATION-FAIL-20260623T091000Z`

## F001-F083 Passport Route Closeout
Status: `CLOSED_NO_PRODUCTION_GO`.
Artifact: `reports/qa_gate/f001_f083_route_closeout_audit_20260623T091500Z.md`.

Current fact: `F001-F083` is closed for the current route. There is no promotable candidate after F051 validation failed.

Allowed next work:
1. new passport/feature/hypothesis route;
2. new validation idea with an explicit audit boundary;
3. separate exit/risk passports.

## State Version
`CALIBRATION-CURRENT-F001-F083-CLOSED-NO-PRODUCTION-GO-20260623T091500Z`

## Core ML Bot TZ Audit
Status: `PARTIAL_MATCH_WITH_STRONG_CALIBRATION_CORE`.
Artifact: `reports/qa_gate/core_ml_bot_tz_audit_20260623_RU.md`.

Current fact: audited the current project against the user-provided compact 1m ML trading bot core TZ.

Decision: do not create a second `trading_bot/` tree. Use `src/mlbotnav` as the implementation core, add thin contracts/facades, then close missing CORE features, trade-log schema, MAE/MFE, ML labels, and separate exit/risk passports.

## State Version
`CORE-ML-BOT-TZ-AUDIT-PARTIAL-MATCH-20260623T100126Z`
## ML Trade Dataset Stage 2.2 Passport Context 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_2_passport_context_audit_20260623T124407Z.md`.

Passport context is now added to pipeline and OOS trade CSV outputs before write. The shared helper resolves metadata from `configs/calibration_action_passports.yaml`.

Checks passed: changed modules `py_compile PASS`; focused tests `55/55 OK`; `text_guard PASS`.

Next strict WBS step: `2.3 Добавить trade identity`.
## ML Trade Dataset Stage 2.3 Trade Identity 2026-06-23
Current status: `CLOSED_PASS`.
Artifact: `reports/qa_gate/ml_trade_dataset_stage_2_3_trade_identity_audit_20260623T125332Z.md`.

Trade identity is now added to pipeline and OOS trade CSV outputs before write. The shared helper emits deterministic `trade_id` values for rows where `side != 0` and fills `entry_signal_time_utc` from the signal bar.

Checks passed: changed modules `py_compile PASS`; focused tests `56/56 OK`; `text_guard PASS`.

Next strict WBS step: `2.4 Добавить duration labels`.

## B001 Single-Worker Fast Finish 2026-06-24
Status: `diagnosed_not_worker_failure`.
Artifact: `reports/qa_gate/b001_single_worker_fast_finish_audit_20260624T180000Z_RU.md`.

Проверенный запуск `long_only_pool_20260624t175647z_w1` получил профиль `max_threads=9`, `search_workers=9`, `workers_used=9`, `n_trials_override=42`.

Быстрое завершение связано не с недогрузом воркеров, а с пустым семейным входным гейтом B001 strict `5/5`: лучший кандидат `EMPTY_ACTION_GATE`, `0` сделок, `signal_count_after_entry_action_gates=0`.

Следующий диагностический шаг: single-worker `1x9/9`, но family-unified `4/5` на 1д/1д; если пусто, проверить `3/5`.

## Optuna Worker Profile Correction 2026-06-24
Status: `profile_rule_corrected`.
Artifact: `reports/qa_gate/optuna_1x9_vs_3x3_worker_audit_20260624T183000Z_RU.md`.

Факт: `1x9/9` не равен старому `3x3/9` по физической нагрузке. `3x3/9` создает три отдельных Python-процесса, а `1x9/9` один процесс с внутренним `n_jobs=9`.

Рабочий профиль для нагрузочных прогонов снова считать `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, `Threads=9`, `SearchWorkers=9`. `1x9/9` использовать только как диагностику одной Optuna-истории.

## B001 Family-Unified 4/5 LONG 2026-06-24
Status: `done_tradeful_negative_no_promotion`.
Artifact: `reports/qa_gate/b001_family_unified_4of5_long_3x3_audit_20260624T184500Z_RU.md`.

Проверка `1д/1д` на рабочем профиле `3x3/9` завершена. Launcher `OK`, лучший worker `w3`, OOS `-5.071620930989562%`, `1` сделка. Семейный вход `4/5` сработал корректно: `F001..F004=1`, `F005=0`.

Следующий B001 diagnostic: `3/5 LONG` на `3x3/9`, если продолжаем раздушивать семейный вход.
## Visual Entry Signal-Entry Contract v2 2026-06-25
Текущий статус: `DEV_SIGNAL_ENTRY_CONTRACT_READY_NEEDS_USER_VISUAL_CONFIRM`.

Исправлена логика ручной разметки: свеча с фитилем/дном является сигналом после закрытия, а вход считается на open следующей свечи.

Рабочий v2-контракт: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/manual_entries.json`.

Zoom-проверка: `reports/manual_entries/SOLUSDT_1m_visual_dev_20260625_20260512_v2_signal_entry/visual_entry_signal_entry_zoom_panels_20260625T102849Z.png`.

Формула LONG slippage: `entry_price_with_slippage = entry_open_price * (1 + slippage_bps / 10000)`, сейчас `slippage_bps=5`.

До визуального подтверждения пользователем v2 нельзя передавать в ML и нельзя считать финальным scorer target.

## Visual Entry Instrument Stack Audit 2026-06-25
Текущий статус: `DEV_AUDIT_READY_NEXT_NOISE_SUPPRESSION_RUNNER`.

Аудит: `reports/final_review/visual_entry_v3/instrument_stack_audit/visual_entry_instrument_stack_audit_20260625_RU.md`.

Факт: следующий шаг по visual-entry - не ML и не большая Optuna, а diagnostic runner для кластерного подавления шума. `DQ01/DQ03` являются картой зон дна, но не кандидатом на promotion.

Рабочий следующий шаг: `VISUAL_ENTRY_NOISE_SUPPRESSION_CLUSTER_PRIORITY`, цель DEV - сохранить `>=9/11` попаданий и снизить false у `DQ01` с `73` хотя бы до `<=30`, затем сделать PNG-оверлеи.

Граница: ML/export/promotion запрещены до трехдневной проверки `2026-05-12` DEV, `2026-05-13` validation, `2026-05-14` holdout.

## Visual Entry Noise Suppression Runner 2026-06-25
Текущий статус: `DEV_RUNNER_DONE_NO_ML`.

Добавлен cluster-priority runner: `src/mlbotnav/visual_entry_noise_suppression_cluster_priority_runner.py`.

Лучший слой `CP01_DQ01_CLUSTER10_SCORE12` на `2026-05-12`: `9/11`, `28` false, `37` entries, precision `0.2432`, recall `0.8182`, f1 `0.3750`. Это улучшает шум относительно `DQ01` (`73` false), но теряет `08:26` и `17:00`.

Отчет: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_noise_suppression_cluster_priority_20260512_DEV_RU.md`.
PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp01_dq01_cluster10_score12_20260625T150100Z.png`.

В ML ничего не передавать. Следующее действие: добор пропущенных `08:26` и `17:00` с контролем false.

## Visual Entry CP06 Recover 2026-06-25
Текущий статус: `DEV_RECOVER_DONE_11_OF_11_NO_ML`.

`CP06_CP01_RECOVER_NOWICK_LATE_RETEST` закрыл оба пропуска `CP01`: `08:26` и `17:00`.

Итог DEV `2026-05-12`: `11/11`, `0` missed, `28` false, `39` entries, precision `0.2821`, recall `1.0000`, f1 `0.4400`.

PNG: `reports/final_review/visual_entry_v3/noise_suppression_cluster_priority/visual_entry_family_overlay_2026-05-12_noise_cluster_01_cp06_cp01_recover_nowick_late_retest_20260625T151725Z.png`.

Граница: это diagnostic-only visual layer. До validation/holdout и ручного `APPROVED_FOR_ML` в ML ничего не передавать.

## Visual Entry RBKD V0 2026-06-29
Current status: `DEV_RBKD_V0_BUILT_TOO_NOISY_NO_ML_NEXT_SWING_SUPPORT_EVENT`.

`REVERSAL_BOTTOM_KNIFE_DROP_V0` построен и проверен на `2026-05-13` validation и `2026-05-14` holdout. Он работает по честному контракту `next_bar_open_after_signal_close`, но дает слишком много ложных входов:

1. `2026-05-13`: `2/9` hits, `81` false.
2. `2026-05-14`: `1/17` hits, `83` false.

Decision: no ML export, no promotion, no production GO. Следующая механика должна быть `SWING_SUPPORT_RETEST_EVENT_V1`, потому что пользовательские ручные входы часто являются support/retest/trend-dip событиями, а не чистой перепроданностью.

Artifact: `reports/final_review/visual_entry_v3/reversal_bottom_knife_drop/visual_entry_reversal_bottom_knife_drop_audit_20260629T090101Z_RU.md`.
## Visual Entry SSRE V1 2026-06-29
Current status: `DEV_SSRE_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Entry-only runner `SWING_SUPPORT_RETEST_EVENT_V1` проверен. Он не тянет сделки и не использует будущую доходность: только совпадение входа на следующем open с ручными low-входами.

Результат слабый:

1. `2026-05-13`: `1/9` hits, `29` false.
2. `2026-05-14`: `1/17` hits, `26` false.

Decision: no ML export, no promotion. Следующий рабочий слой: `SIGNIFICANT_LOW_SELECTOR_V1`, потому что проблема не в выходе из сделки, а в выборе именно значимого low.

Artifact: `reports/final_review/visual_entry_v3/swing_support_retest_event/visual_entry_swing_support_retest_event_audit_20260629T092400Z_RU.md`.
## Fresh Strategy Overlay 2026-06-29
Current status: `DEV_FRESH_OVERLAY_DONE_ENTRY_ONLY_NO_CALIBRATION_NO_ML`.

Fresh clean overlays созданы для `2026-05-13` и `2026-05-14`. Это entry-only стенд без cooldown и без калибровки.

Artifact: `reports/final_review/visual_entry_v3/fresh_strategy_overlay/visual_entry_fresh_strategy_overlay_audit_20260629T113100Z_RU.md`.

Decision: использовать отдельные PNG по стратегиям, не combined. ML/export/promotion запрещены.
## User Red Arrows V2 Fixed 2026-06-29
Current status: `HOLDOUT_DAY_USER_RED_ARROWS_V2_FIXED_AUTO_DETECTED_NEEDS_VISUAL_CONFIRM`.

Новый пользовательский эталон low-входов сохранен:

`reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries.json`

Всего снято `17` входов. Предыдущая авторазметка на `18` входов была исправлена: один тонкий фрагмент красной линии удален как ложная стрелка. Это auto-detected разметка со скрина, поэтому перед использованием как строгого scorer target нужен визуальный confirm по PNG:

`reports/manual_entries/SOLUSDT_1m_visual_holdout_20260629_20260514_user_red_arrows_v2/manual_entries_v2_fixed_signal_entry_verify_20260629T115000Z.png`

## Significant Low Selector V1 2026-06-29
Current status: `DEV_SIGNIFICANT_LOW_SELECTOR_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Добавлен и прогнан `SIGNIFICANT_LOW_SELECTOR_V1` против `17` пользовательских low-входов `SOLUSDT 1m 2026-05-14`.

Аудит: `reports/final_review/visual_entry_v3/significant_low_selector/visual_entry_significant_low_selector_audit_20260629T125000Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/significant_low_selector/visual_entry_family_overlay_2026-05-14_sls_v1_01_sls06_hot_reclaim_strict_false_control_20260629T124723Z.png`.

Итог: лучший f1 у `SLS06` = `5/17` hits и `71` false; самый широкий `SLS10` = `13/17`, но `463` false. Это не кандидат, не ML, не promotion. Следующий слой: `LOW_CLUSTER_RANKER_V2`.

## Low Cluster Ranker V2 2026-06-29
Current status: `DEV_LOW_CLUSTER_RANKER_V2_ENTRY_ONLY_DONE_REDUCED_FALSE_LOW_RECALL_NO_ML`.

Добавлен кластерный V2: `src/mlbotnav/visual_entry_low_cluster_ranker_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/low_cluster_ranker/visual_entry_low_cluster_ranker_audit_20260629T133000Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/low_cluster_ranker/visual_entry_family_overlay_2026-05-14_lcr_v2_01_lcr04_late_low_with_reclaim_cluster_20260629T132833Z.png`.

Итог: `LCR04` = `3/17`, `10` false; `LCR07` = `2/17`, `4` false; `LCR06` = `7/17`, `64` false. V2 не кандидат и не ML; следующий шаг - режимное разделение missed-входов.
# Visual Entry Regime Split Ranker V1 2026-06-29
Current status: `DEV_REGIME_SPLIT_RANKER_V1_ENTRY_ONLY_DONE_TOO_NOISY_NO_ML`.

Добавлен режимный entry-only слой для пользовательских low-входов `SOLUSDT 1m 2026-05-14`: `src/mlbotnav/visual_entry_regime_split_ranker_runner.py`.

Режимы: `DEEP_CAPITULATION`, `HOT_RECLAIM_SUPPORT`, `TREND_DIP_CONTINUATION`, `STRUCTURE_BOS_FIBO_VOLUME`.

Результат: больше всего целей ловят `STRUCTURE` и `TREND` (`7/17`), но false слишком много (`84-95`). `DEEP` чище (`12` false), но ловит только `2/17`. Это diagnostic-only, в ML ничего не передавать.

Аудит: `reports/final_review/visual_entry_v3/regime_split_ranker/visual_entry_regime_split_ranker_audit_20260629T134600Z_RU.md`.

## Visual Entry Regime False Suppression V2 2026-06-29
Current status: `DEV_REGIME_FALSE_SUPPRESSION_V2_ENTRY_ONLY_DONE_STILL_TOO_NOISY_NO_ML`.

Добавлен suppress-слой по режимам: `src/mlbotnav/visual_entry_regime_false_suppression_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_regime_false_suppression_audit_20260629T135843Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/regime_false_suppression/visual_entry_family_overlay_2026-05-14_regime_false_suppression_v2_01_fsv21_union_strict_false_control_20260629T135626Z.png`.

Итог: лучший `FSV21` = `7/17` hits и `41` false; `FSV02` deep = `2/17` hits и `4` false. V2 не кандидат, не ML, не promotion. Следующий слой: `ONLINE_LOW_EVENT_QUALITY_V3`.

## Visual Entry Online Low Event Quality V3 2026-06-29
Current status: `DEV_ONLINE_LOW_EVENT_QUALITY_V3_ENTRY_ONLY_DONE_CLEANER_LOW_RECALL_NO_ML`.

Добавлен event-quality слой: `src/mlbotnav/visual_entry_online_low_event_quality_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_online_low_event_quality_audit_20260629T141715Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/online_low_event_quality/visual_entry_family_overlay_2026-05-14_online_low_event_quality_v3_01_olev20_union_event_quality_balanced_20260629T141647Z.png`.

Итог: `OLEV20` = `3/17` hits, `7` false, `10` entries. V3 не кандидат, не ML, не promotion. Следующий слой: `DEEP_RECOVERY_AND_HOT_RECALL_V4`.

## Visual Entry Deep Recovery And Hot Recall V4 2026-06-29
Current status: `DEV_DEEP_RECOVERY_AND_HOT_RECALL_V4_ENTRY_ONLY_DONE_BETTER_BALANCE_NO_ML`.

Добавлен V4 runner: `src/mlbotnav/visual_entry_deep_recovery_hot_recall_runner.py`.

Аудит: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_deep_recovery_hot_recall_audit_20260629T144050Z_RU.md`.

Главный PNG: `reports/final_review/visual_entry_v3/deep_recovery_hot_recall/visual_entry_family_overlay_2026-05-14_deep_recovery_hot_recall_v4_01_drhr20_olev20_plus_deep_recovery_20260629T144015Z.png`.

Итог: `DRHR20` = `5/17` hits, `13` false, `18` entries, f1 `0.2857`. V4 не кандидат, не ML, не promotion. Следующий слой: `HOT_TREND_FALSE_SUPPRESSION_V5`.

## Visual Entry Hot Trend False Suppression V5 2026-06-29
Рабочий статус: `DEV_HOT_TREND_FALSE_SUPPRESSION_V5_ENTRY_ONLY_DONE_RECALL_UP_FALSE_STILL_HIGH_NO_ML`.

V5 добавил строгий фильтр для hot/trend diagnostic из V4. Фильтр `HTFS01` оставляет pullback/reclaim рядом с event-low и режет широкую support-полку и перегретый MFI.

Итог:
1. `HTFS20_UNION_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `9/17` hits, `14` false, `23` entries, f1 `0.4500`.
2. `HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `4/17` hits, `1` false, `5` entries.
3. Сырой `HTFS09_BROAD_HOT_TREND_DIAGNOSTIC`: `4/17`, `35` false.

Артефакты:
1. Код: `src/mlbotnav/visual_entry_hot_trend_false_suppression_runner.py`.
2. Тест: `tests/test_visual_entry_hot_trend_false_suppression_runner.py`.
3. Аудит: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_hot_trend_false_suppression_audit_20260629T145900Z_RU.md`.
4. Главный PNG: `reports/final_review/visual_entry_v3/hot_trend_false_suppression/visual_entry_family_overlay_2026-05-14_hot_trend_false_suppression_v5_01_htfs20_union_htfs01_hot_trend_strict_false_suppression_20260629T145736Z.png`.

Контракт сохранен: `signal close -> next open`, `slippage_bps=5`, `lookahead=NO`, без entry-candle OHLCV, без TP/SL/MFE/MAE/future return, без cooldown `30/45/60/90`, без ML.

Следующий шаг: `BASE_FALSE_SUPPRESSION_V6`, цель - уменьшить ложные входы базовой V4-части и не потерять чистые входы `HTFS01`.

## Visual Entry Base False Suppression V6 2026-06-29
Рабочий статус: `DEV_BASE_FALSE_SUPPRESSION_V6_ENTRY_ONLY_DONE_BEST_CURRENT_ONE_DAY_NO_ML`.

V6 разделил базовую V4-часть по источнику: `OLEV20` support-reclaim и `DEEP_RECOVERY` режутся разными past-only правилами. Чистый `HTFS01` из V5 подключен без изменения.

Итог:
1. `BFS20_UNION_BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION_PLUS_HTFS01`: `9/17` hits, `1` false, `10` entries, f1 `0.6667`.
2. `BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION`: `5/17` hits, `0` false.
3. `BFS90_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `4/17` hits, `1` false.

Попадания лучшего union: `03:23`, `06:41`, `10:48`, `12:06`, `14:13`, `15:18`, `15:45`, `16:54`, `17:34`.

Единственный false: `18:47`.

Артефакты:
1. Код: `src/mlbotnav/visual_entry_base_false_suppression_runner.py`.
2. Тест: `tests/test_visual_entry_base_false_suppression_runner.py`.
3. Аудит: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_base_false_suppression_audit_20260629T151215Z_RU.md`.
4. Главный PNG: `reports/final_review/visual_entry_v3/base_false_suppression/visual_entry_family_overlay_2026-05-14_base_false_suppression_v6_01_bfs20_union_bfs01_base_source_split_strict_false_suppression_plus_htfs01_20260629T151147Z.png`.

Контракт сохранен: `signal close -> next open`, `slippage_bps=5`, `lookahead=NO`, без entry-candle OHLCV, без TP/SL/MFE/MAE/future return, без cooldown `30/45/60/90`, без ML.

Следующий шаг: validation `2026-05-13` без изменения параметров V6.

## Visual Entry V6 Validation Fail 2026-06-29
Рабочий статус: `VALIDATION_FAIL_V6_DOES_NOT_GENERALIZE_NO_ML`.

Проверка V6 на `2026-05-13` validation без изменения параметров провалилась:

1. `BFS20_UNION_BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION_PLUS_HTFS01`: `0/9` hits, `1` false, `1` entry.
2. `BFS90_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION`: `0/9` hits, `1` false, `1` entry.
3. `BFS00_BASE_V4_RAW`: `0/9` hits, `17` false, `17` entries.

Validation targets: `00:18`, `01:08`, `03:30`, `07:45`, `08:48`, `12:54`, `16:16`, `19:44`, `22:31`.

Артефакты:
1. Аудит: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_base_false_suppression_validation_audit_20260629T155000Z_RU.md`.
2. JSON: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_base_false_suppression_v6_20260513_VALIDATION_DAY.json`.
3. Главный PNG: `reports/final_review/visual_entry_v3/base_false_suppression_validation/visual_entry_family_overlay_2026-05-13_bfs_v6_03_u_bfs01_bss_s_fs_h01_20260629T154949Z.png`.

Фикс инфраструктуры: укорочен label PNG в `src/mlbotnav/visual_entry_base_false_suppression_runner.py`, потому что Windows упал на слишком длинном имени файла. Логика сигналов не менялась.

Следующий шаг: `GENERALIZATION_V7`, не ML, не Optuna.
# Current State 2026-06-29 Visual Entry NEGATIVE_CONTEXT_SUPPRESSION_V8

Текущий статус: `NEGATIVE_CONTEXT_SUPPRESSION_V8_PARTIAL_BRICK_NO_ML`.

V8 готов как suppress diagnostic:

1. `src/mlbotnav/visual_entry_negative_context_suppression_v8_runner.py`;
2. `tests/test_visual_entry_negative_context_suppression_v8_runner.py`;
3. `reports/final_review/visual_entry_v3/negative_context_suppression_v8/visual_entry_negative_context_suppression_v8_audit_20260629T173500Z_RU.md`.

Главный результат: найден первый чистый кирпич `V8_02_HOT_CHAIN_EVENT_LOW_SUPPRESSION` на validation `2026-05-13`: `1/9`, `0` false, вход `08:48`. Но это не стратегия, потому что recall низкий.

На holdout `2026-05-14` лучший отдельный режим `V8_01_HOT_FIRST_NEGATIVE_SUPPRESSION` дал `4/17`, `29` false. Union все еще шумный: `11/17`, `168` false. В ML ничего не передавать.

Следующий шаг: `V9_BRICK_BY_BRICK_SELECTOR`: отдельный чистый кирпич для hot-chain оставить, затем строить отдельные селекторы для early-hot и deep-terminal без общего noisy union.

# Current State 2026-06-29 Visual Entry GENERALIZATION_V7

Текущий статус: `GENERALIZATION_V7_DIAGNOSTIC_FAIL_NO_ML`.

V7 diagnostic runner готов и проверен:

1. `src/mlbotnav/visual_entry_generalization_v7_runner.py`;
2. `tests/test_visual_entry_generalization_v7_runner.py`;
3. `reports/final_review/visual_entry_v3/generalization_v7/visual_entry_generalization_v7_audit_20260629T172000Z_RU.md`.

Главный итог: V7 не обобщился. На `2026-05-13` лучший режим дал только `1/9` при `22` false; на `2026-05-14` union поймал `11/17`, но дал `203` false. В ML ничего не передавать.

Практический вывод: проблема сейчас не в нехватке recall, а в отсутствии сильного отрицательного контекста. Следующий слой должен резать шум: боковые микролои, верхние горячие полки, повторные retest-серии и ранние сигналы до настоящего значимого low.

# Current State 2026-06-30 C02 Split/Router

Текущий статус: `C02_SPLIT_ROUTER_DECISION_V0_COMPLETE_NO_SCORER_NO_ML_NO_OPTUNA`.

Активный свежий процесс идет по `FRESH_TARGET_LED_WORKFLOW_READY_NO_ML`, а не по старым V7/V8/V9/V10/V11.

Пункт рельсов `8.3` завершен: C02 разделен на ядро, router-ветки и negative controls. Один широкий C02 scorer запрещен.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/C02_SPLIT_ROUTER_DECISION_V0_20260630.png`.

Следующий подпункт: `8.3.1_DESIGN_C02A_TRUE_DEEP_CAPITULATION_CORE_RULES_FROM_PAST_ONLY_FEATURES_NO_SCORER_YET`.

# Current State 2026-06-30 C02 Price/Visual Fix

Текущий статус: `C02_SPLIT_ROUTER_PRICE_CLARITY_FIX_V0_COMPLETE_NO_SCORER_NO_ML_NO_OPTUNA`.

По замечанию пользователя исправлен рабочий визуал C02: добавлены цены входа `entry_open_price`, учетный `entry + 5 bps`, high-res full-day PNG и SVG/zoom-sheet без растрового размытия.

Основные артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_ENTRY_PRICE_TABLE_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_ZOOM_SHEET_V0_20260630.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/split_router_v0/price_clarity_fix_v0/C02_SPLIT_ROUTER_PRICE_CLEAR_FULL_DAY_HIRES_V0_20260630.png`.

Цена входа нужна только для исполнения/учета/визуального контроля и запрещена как признак выбора входа.

# Current State 2026-06-30 C02A Rules Draft

Текущий статус: `C02A_TRUE_DEEP_CAPITULATION_RULES_V0_DRAFT_WAIT_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA`.

Пункт `8.3.1` выполнен как draft без scorer. C02A rules V0 пропускают только `C02E03/M01`, `C02E04/M02`, `C02E10/M08` и отклоняют negative controls `C02E01`, `C02E02`, `C02E13`, `C02E14`, `C02E15`, `C02E16`.

Артефакты:
1. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_V0_20260630_RU.md`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_V0_20260630.json`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/passport_bench_v0/C02_DEEP_CAPITULATION_LOW/c02a_rules_v0/C02A_TRUE_DEEP_CAPITULATION_RULES_VISUAL_V0_20260630.png`.

Следующий подпункт: `8.3.1_USER_VISUAL_REVIEW_C02A_RULES_V0_BEFORE_SCORER`.
# Current State 2026-06-30 Fresh Target-Led Visual Entry Workflow

Текущий статус: `FRESH_TARGET_LED_WORKFLOW_READY_NO_ML`.

Создан новый рабочий протокол: `docs/CALIBRATION_NODE_CURRENT/VISUAL_ENTRY_FRESH_PROCESS_TZ_RU.md`.

Рабочая линия меняется: старые visual-entry версии больше не являются очередью следующего действия. Новый порядок начинается с пользовательских `T01..T10` на чистом графике, затем идет классификация входов, стратегия под один тип, паспорт, entry-only проверка, target-lock, и только потом Optuna.

ML/export/promotion запрещены.

# Current State 2026-06-30 Fresh Target-Led Start

Текущий статус: `FRESH_TARGET_LED_DAY_SELECTED_LEDGER_READY_NO_ML`.

Первый свежий target-led шаг выполнен на одном дне: `2026-05-14`, `SOLUSDT`, `1m`, `core`.

Артефакты:
1. `src/mlbotnav/visual_entry_fresh_target_ledger.py`;
2. `reports/final_review/visual_entry_v3/fresh_target_led/fresh_target_led_clean_chart_SOLUSDT_1m_2026-05-14_20260630T062202Z.png`;
3. `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10.json`;
4. `reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_T01_T10_RU.md`.

Ledger содержит T01..T10. После visual review `T04` отклонена, `T07` подтверждена с ручной правкой времени, остальные точки пока требуют подтверждения.

Первый кластер для ручной проверки после отклонения T04: `HOT_RECLAIM_SUPPORT`, `T07/T08`. Это не стратегия и не lock.

`T04` отклонена пользователем на visual review: не подходящая точка входа.

`T07` подтверждена с ручной правкой времени: signal `2026-05-14T10:42:00Z`, LONG entry `2026-05-14T10:43:00Z`. Старое автоположение `10:48 -> 10:49` не использовать.

`T08` исправлена по пользовательской нарисованной метке: предполагаемый signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`; статус требует короткого подтверждения.

ML/export/promotion и Optuna запрещены.

Активные рельсы процесса: `docs/CALIBRATION_NODE_CURRENT/FRESH_TARGET_LED_RAILS_RU.md`.
# Current State 2026-06-30 Fresh Target-Led User Marked Order

Текущий статус: `USER_MARKED_DEVELOPMENT_ORDER_NEEDS_ZOOM_CONFIRM_NO_ML`.

Пользователь дал новый порядок разработки входов на `SOLUSDT 1m 2026-05-14`: красные прямоугольники на full-day графике слева направо. Машинно снят ordered-ledger `M01..M15`; каждая точка остается `needs_zoom_confirm`, пока пользователь не подтвердит zoom.

`T08` подтверждена: signal `2026-05-14T12:00:00Z`, LONG entry `2026-05-14T12:01:00Z`.

Первый zoom для ручного решения: `M01`, предполагаемый signal `2026-05-14T03:23:00Z`, LONG entry `2026-05-14T03:24:00Z`.

PNG: `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M01_user_marked_order_zoom_signal_0323_entry_0324.png`.

Это еще не стратегия и не target-lock. Optuna/ML/export запрещены.
# Current State 2026-06-30 M01 Confirmed

Текущий статус: `M01_GOLD_USER_VISUAL_CONFIRMED_NEXT_M02_NO_ML`.

`M01` подтвержден пользователем как подходящий: signal `2026-05-14T03:23:00Z`, LONG entry `2026-05-14T03:24:00Z`.

Следующий zoom-кандидат показан: `M02`, предполагаемый signal `2026-05-14T03:58:00Z`, LONG entry `2026-05-14T03:59:00Z`.

PNG: `reports/final_review/visual_entry_v3/fresh_target_led/visual_confirm/M02_user_marked_order_zoom_signal_0358_entry_0359.png`.
