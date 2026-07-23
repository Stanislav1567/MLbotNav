# STAS5 ML Core

## Обновление 2026-07-13: train-графики за все 14 дней

Статус: `STAS5_V2_TRAIN_VISUAL_BATCH_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

После замечания пользователя, что был создан только один train-график, сделан batch-render всех train-дней `2026-05-01..2026-05-14` из того же V2 feature snapshot, который используется для ML.

Результат:

```text
artifacts/v2/visual_approval/runs/stas5_v2_train_visual_20260713_14d/
```

Проверено: `14/14` PNG, `972` строк, `115 KEEP_DRAFT`, `857 CUT_DRAFT`, `30` KEEP+yellow conflict, STAS5 tests `34 passed`.

Это visual/audit слой; обучение/TP/Stas3/API/Optuna не запускались.

## Обновление 2026-07-13: отдельные папки для каждого V2-прогона

Статус: `STAS5_V2_RUN_ISOLATION_READY`.

Обучение и forward больше не должны писаться поверх старых дневных папок. CLI принимает общий `--run-id`, и артефакты раскладываются так:

```text
artifacts/v2/model/runs/<run_id>/
artifacts/v2/forward/runs/<run_id>/
```

В корне остаются только указатели:

```text
artifacts/v2/model/STAS5_V2_LATEST_MODEL_RUN.json
artifacts/v2/forward/STAS5_V2_LATEST_FORWARD_RUN.json
```

Проверочный прогон: `stas5_v2_run_20260713_190743`. STAS5 tests: `34 passed`.

## Обновление 2026-07-13: V2 controlled model и forward PNG

Статус: `STAS5_V2_CONTROLLED_FORWARD_READY_NO_TP_NO_API_NO_STAS3`.

После numeric coverage выполнен полный рабочий проход:

1. V2 ablation baseline на train `2026-05-01..2026-05-14`;
2. выбор controlled feature set `v1_plus_risk_gate` по train LOO;
3. обучение V2 entry ranker;
4. blind-forward `2026-05-15..2026-05-20`;
5. PNG-графики по каждому forward-дню.

Итог: selected model использует `126` feature columns, LOO AUC `0.684988`. Forward дал `106 ENTER`, `45 UNSURE`, `284 SKIP`.

Главный отчет:

```text
artifacts/v2/model/STAS5_V2_CONTROLLED_MODEL_AND_FORWARD_REPORT_RU.md
```

Граница: forward не использован для обучения или threshold tuning; TP/Stas3/API/Optuna не запускались.

## Обновление 2026-07-13: numeric coverage audit

Проведен аудит вопроса пользователя: все ли важное, что видно на графике STAS5 V2 за `2026-05-04`, передается в ML как числа.

Статус: `STAS5_V2_CONTROLLED_FORWARD_READY_NO_TP_NO_API_NO_STAS3`.

Что подключено в числовую feature matrix:

1. `stas4_v2_block_*` - нейтральные support/conflict/net score для четырех STAS4-блоков: `density_profile+structure_ta`, `pattern+structure_ta`, `structure_ta+volume_flow`, `structure_ta+trend_momentum`;
2. `stas4_v2_pattern_*` - числовой pattern/candle/divergence/context слой;
3. `stas5_v2_short_wave_*` - causal SHORT/WAVE контекст по окнам до входа.

Итог по размерам: V2 combo features увеличены с `103` до `163`, общий V2 snapshot увеличен с `214` до `274` feature columns. Train rows не изменились: `972`; `KEEP_DRAFT + yellow_x = 30` сохранены; leakage guard `PASS`.

Что не является ML-признаком по контракту: PNG/красота графика, human label, yellow X/conflict, postfact outcome, TP/Stas3/exit и старый macro `WAVE` strip как обзорная картинка. Для WAVE используется только causal числовой контекст до входа.

Артефакты:

```text
artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.csv
artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.csv
artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.csv
artifacts/v2/guard/stas5_v2_leakage_guard_20260501_20260514_v0.json
artifacts/v2_audit/STAS5_V2_NUMERIC_COVERAGE_AUDIT_20260504_RU.md
artifacts/v2_audit/stas5_v2_numeric_coverage_audit_20260504_v0.json
```

Граница: обучение, ablation, threshold tuning, TP/Stas3, API/мост Bybit, Optuna/scorer/target-lock не запускались.

## Обновление 2026-07-13: strategy audit strip

В approval-график `2026-05-04` добавлена отдельная полоса `STAS4 Audit` с четырьмя выбранными блоками:

1. `density_profile+structure_ta` - основной yellow-X audit;
2. `pattern+structure_ta` - второй слой проверки;
3. `structure_ta+volume_flow` - жесткий risk-флаг;
4. `structure_ta+trend_momentum` - агрессивный risk-флаг.

Эти блоки на графике не дают финальный вход и не являются ML-target. Они показывают голос/риск стратегии рядом с human `KEEP/CUT`, чтобы перед ablation глазами проверить, не мешают ли они хорошим входам и где режут шум.

Статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_READY_WAIT_USER_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Дата фиксации: `2026-07-13`.

Эта папка фиксирует новый source-of-truth для STAS-5: ML по входам.

Главная цель STAS-5 - научить ML выбирать хорошие входы из кандидатов Stas1/Stas2 по Stas2/Stas4 pre-entry контексту и human KEEP/CUT.

## Текущая рабочая память

Статус: `STAS5_V2_NUMERIC_COVERAGE_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Рабочий маршрут STAS-5:

1. train base: `2026-05-01..2026-05-14`;
2. train labels: `972` входа, `115` `KEEP_DRAFT`, `857` `CUT_DRAFT`;
3. guard: `30` `KEEP_DRAFT` с yellow X сохранены;
4. feature rule: `111` признаков, только известные до входа;
5. first model: controlled entry ranker без yellow/strategy/Stas3/future fields;
6. forward check: `2026-05-15..2026-05-20`, ML показывает точки входа на PNG;
7. hard audit: v1 технически корректен, но не является финальным рабочим входным контуром;
8. V2 combo feature exporter готов: combo-spectrum/STAS4 нижний индикатор превращен в causal-признаки;
9. V2 feature snapshot готов: v1 ledger/Stas2 context объединены с V2 combo features;
10. V2 leakage guard готов: проверены no future/postfact/yellow-as-feature/Stas3/TP/exit и causal time contract;
11. V2 forward error ledger готов: forward `2026-05-15..2026-05-20` разобран на классы ошибок;
12. V2 pre-ML audit готов: train KEEP/CUT и forward error classes разобраны без обучения;
13. V2 forward user-review pages за `2026-05-15` остаются вспомогательным audit-артефактом;
14. V2 feature visual approval за `2026-05-04` готов: train labels и V2 causal features наложены на график в стиле STAS4 overlay;
15. STAS4 strategy/pattern/SHORT-WAVE visual layers переведены в causal numeric features;
16. numeric coverage audit за `2026-05-04` готов;
17. V2 ablation baseline выполнен;
18. V2 controlled model обучен на `v1_plus_risk_gate`;
19. blind-forward `2026-05-15..2026-05-20` и PNG-графики готовы;
20. next route: пользователь смотрит forward PNG и выбирает реальные/шумные входы для следующего улучшения.

Не входит в STAS-5 entry ML:

1. TP/exit;
2. Stas3;
3. Optuna;
4. API/мост Bybit;
5. hard-cut по yellow X;
6. future outcome как feature.

## Главный принцип

ML учится не на желтом `X`, не на стратегии и не на будущем результате сделки.

ML учится на решении человека:

```text
candidate entry + pre-entry features -> human KEEP / CUT
```

Приоритет всегда такой:

```text
human KEEP > strategy vote
```

Если человек оставил вход, а стратегия поставила желтый `X`, вход остается хорошим примером для будущей ML-разметки. Желтый `X` хранится только как `AUDIT_ONLY`.

## Документы

1. `01_STAS5_ML_ENTRY_ARCHITECTURE_RU.md` - архитектура STAS-5 по входам.
2. `02_ML_LEDGER_AND_FEATURE_CONTRACT_RU.md` - контракт ML-ledger, labels, strategy votes и pre-entry features.
3. `03_STAS5_CURRENT_EXECUTION_INSTRUCTION_RU.md` - рабочее ТЗ: train `1-14`, forward `15+`, PNG с ML-входами.
4. `04_STAS5_V1_HARD_AUDIT_RU.md` - жесткий аудит STAS5 v1 и причины плохих зеленых входов.
5. `05_STAS5_V2_CONTOUR2_TZ_RU.md` - новое ТЗ STAS5 V2 / контур 2.
6. `schemas/stas5_ml_ledger_v0.yaml` - черновая схема ledger-таблицы.
7. `schemas/stas5_feature_snapshot_v0.yaml` - черновая схема feature snapshot.

## Готовые артефакты текущего этапа

1. Ledger: `artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.csv`.
2. Feature snapshot: `artifacts/features/stas5_feature_snapshot_20260501_20260514_v0.csv`.
3. Leakage guard: `artifacts/guard/stas5_leakage_guard_20260501_20260514_v0.json`.
4. Pre-ML audit: `artifacts/audit/STAS5_PRE_ML_AUDIT_20260501_20260514_RU.md`.
5. Baseline model: `artifacts/model/stas5_entry_ranker_20260501_20260514_v0.joblib`.
6. Train predictions: `artifacts/model/stas5_entry_ranker_20260501_20260514_v0.train_predictions.csv`.
7. Forward review: `artifacts/forward/20260515..20260520/STAS5_FORWARD_ENTRY_REVIEW_YYYYMMDD.png`.
8. Hard audit: `04_STAS5_V1_HARD_AUDIT_RU.md`.
9. V2 TZ: `05_STAS5_V2_CONTOUR2_TZ_RU.md`.
10. V2 combo train features: `artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.csv`.
11. V2 combo forward features: `artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.csv`.
12. V2 feature snapshot: `artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.csv`.
13. V2 leakage guard: `artifacts/v2/guard/stas5_v2_leakage_guard_20260501_20260514_v0.json`.
14. V2 forward error ledger: `artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.csv`.
15. V2 pre-ML audit: `artifacts/v2_audit/STAS5_V2_PRE_ML_AUDIT_20260501_20260520_RU.md`.
16. V2 forward user review: `artifacts/v2/user_review/20260515/`.
17. V2 feature visual approval: `artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png`.
18. V2 numeric coverage audit: `artifacts/v2_audit/STAS5_V2_NUMERIC_COVERAGE_AUDIT_20260504_RU.md`.
19. V2 controlled model report: `artifacts/v2/model/STAS5_V2_CONTROLLED_MODEL_AND_FORWARD_REPORT_RU.md`.
20. V2 forward review: `artifacts/v2/forward/20260515..20260520/`.

Метрики первого baseline зафиксированы в `artifacts/model/stas5_entry_ranker_20260501_20260514_v0.manifest.json`.

## Решение после hard audit

STAS5 v1 оставить как `CONTROLLED_BASELINE / AUDIT_REFERENCE`.

Не использовать v1 как production entry permission.

Основная причина перехода к V2:

```text
combo-spectrum/STAS4 indicator block был внедрен как visual/audit layer, но не вошел в feature matrix STAS5 v1.
```

V2 должен добавить:

1. `STAS4 Combo Feature Exporter` - готов;
2. `Phase Detector / Phase Gate`;
3. `Long Permission Gate`;
4. `Risk/Noise Filter`;
5. risk-aware labels;
6. forward error ledger;
7. ablation и calibration audit.

## V2 combo exporter

Код:

```text
src/mlbotnav/stas5_v2_combo_feature_exporter.py
```

Что экспортирует по каждому кандидату Stas2:

1. RSI/MACD/Stoch/ATR и combo-derived признаки;
2. confirmed divergence только если подтверждение было до `anchor_time_utc`;
3. density profile 60/240;
4. structure support/resistance/range/channel/BOS/CHOCH;
5. volume flow;
6. первые risk/gate признаки: `knife_pre_entry`, `short_pressure_score`, `long_allowed_raw/final`, `no_trade_reason_code`.

Ключевой causal-контракт:

```text
feature_time_utc = anchor_time_utc < entry_time_utc
```

Проверенные результаты:

1. train `2026-05-01..2026-05-14`: `972/972` строк, `103` V2-признака, manifest `PASS`;
2. forward `2026-05-15..2026-05-20`: `435/435` строк, `103` V2-признака, manifest `PASS`;
3. forbidden feature columns: `{}`;
4. `feature_available_before_entry_false = 0`.

Это еще не финальная V2-модель. Это первый готовый слой данных для следующего шага: V2 feature snapshot, leakage guard и pre-ML audit.

## V2 feature snapshot

Код:

```text
src/mlbotnav/stas5_v2_feature_snapshot_builder.py
```

Артефакты:

```text
artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.csv
artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.manifest.json
```

Проверенные факты:

1. rows: `972`;
2. feature count: `214`;
3. v1/Stas2 feature count: `111`;
4. V2 combo feature count: `103`;
5. `lost_after_combo_join = 0`;
6. `entry_time_mismatch = 0`;
7. `anchor_time_mismatch = 0`;
8. `v2_combo_feature_available_before_entry_false = 0`;
9. forbidden feature columns `{}`;
10. `KEEP_DRAFT + yellow_x = 30` сохранены.

Это закрывает раздел 14, пункт 4 V2 ТЗ.

## V2 leakage guard

Код:

```text
src/mlbotnav/stas5_v2_leakage_guard.py
```

Артефакт:

```text
artifacts/v2/guard/stas5_v2_leakage_guard_20260501_20260514_v0.json
```

Проверенные факты:

1. status: `PASS`;
2. rows: `972`;
3. feature count: `214`;
4. manifest status: `PASS`;
5. row count matches manifest/train ledger;
6. duplicate keys: `0`;
7. forbidden feature columns `{}`;
8. `yellow_x`, labels и metadata не входят в feature columns;
9. `v2_combo_feature_time_utc < entry_time_utc` для всех строк;
10. forward days `2026-05-15+` не попали в train snapshot;
11. `KEEP_DRAFT + yellow_x = 30` сохранены.

Это закрывает раздел 14, пункт 5 V2 ТЗ.

## V2 forward error ledger

Код:

```text
src/mlbotnav/stas5_v2_forward_error_ledger.py
```

Артефакты:

```text
artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.csv
artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.manifest.json
```

Назначение: audit-only таблица ошибок forward `2026-05-15..2026-05-20`. Она соединяет V1 `ML_DECISION/ML_KEEP_SCORE/postfact`, V2 risk/gate признаки и опциональный user-review label.

Проверенные факты:

1. status: `PASS`;
2. rows: `435`;
3. source V1 rows: `435`;
4. source V2 rows: `435`;
5. `missing_v2_rows_after_join = 0`;
6. duplicate output keys: `0`;
7. V1 decisions: `ENTER=103`, `UNSURE=55`, `SKIP=277`;
8. error classes: `GREEN_BAD_FALLING_KNIFE=46`, `GREEN_BAD_NO_REVERSAL=9`, `GREEN_GOOD=48`, `YELLOW_BAD=34`, `YELLOW_GOOD=21`, `SKIP_CORRECT=212`, `SKIP_MISSED_GOOD=65`;
9. V2 expected decisions: `ENTER=35`, `UNSURE=121`, `SKIP=279`;
10. postfact и user-review поля имеют статус `audit_only`, не feature и не train target.

Это закрывает раздел 14, пункт 6 V2 ТЗ. Следующий пункт: V2 pre-ML audit.

## V2 pre-ML audit

Код:

```text
src/mlbotnav/stas5_v2_pre_ml_audit.py
```

Артефакты:

```text
artifacts/v2_audit/STAS5_V2_PRE_ML_AUDIT_20260501_20260520_RU.md
artifacts/v2_audit/stas5_v2_pre_ml_audit_20260501_20260520_v0.json
```

Назначение: audit-only отчет перед любым V2 train. Он сравнивает train `KEEP/CUT` по `214` признакам, проверяет guard/ledger и показывает forward error classes.

Проверенные факты:

1. status: `READY_FOR_V2_ABLATION_BASELINE`;
2. train rows: `972`;
3. `KEEP_DRAFT=115`, `CUT_DRAFT=857`;
4. `KEEP_DRAFT + yellow_x = 30`;
5. feature count: `214`;
6. guard status: `PASS`;
7. forward error ledger status: `PASS`;
8. forbidden feature columns `{}`;
9. плохих зеленых forward: `55`;
10. хороших зеленых forward: `48`;
11. пропущенных хороших SKIP: `65`;
12. сильные группы признаков по KEEP/CUT: `v1_stas1_candidate`, `v1_stas2_pre_windows`, `v2_combo_indicator`, `v2_structure`.

Это закрывает раздел 14, пункт 7 V2 ТЗ. Следующий пункт: ablation baseline.

## V2 forward user review

Код:

```text
src/mlbotnav/stas5_v2_forward_user_review.py
```

Артефакты за `2026-05-15`:

```text
artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_FULL.png
artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_PAGE_01_0000_0300.png
...
artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_20260515_PAGE_08_2100_0000.png
artifacts/v2/user_review/20260515/STAS5_V2_USER_REVIEW_TEMPLATE_20260515.csv
```

Назначение: пользователь выбирает реальные входы `USER_KEEP_FORWARD_AUDIT`, остальные кандидаты становятся `NOISE_FORWARD_AUDIT`. Этот forward-день остается audit-only и не используется для threshold tuning.

## Жесткая граница

Для V2 обучение не запускать до отдельного ablation baseline/controlled model шага. Готовый V2 pre-ML audit дает право проектировать ablation baseline, но не дает право на production trading permission или threshold tuning по forward `15+`.

По-прежнему не запускать в STAS-5 entry ML:

1. Optuna;
2. scorer;
3. target-lock;
4. торговый API;
5. мост Bybit;
6. Stas3/TP/exit;
7. обучение с future outcome;
8. hard-cut по yellow X;
9. изменение старой Stas1/Stas2/Stas4-логики.

Forward `2026-05-15+` не использовать для подбора threshold. Postfact-поля в forward CSV являются audit-only и не являются признаками модели.
