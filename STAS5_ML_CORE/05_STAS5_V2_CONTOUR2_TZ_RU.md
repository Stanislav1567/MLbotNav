# STAS5 V2 Contour 2 TZ

## Обновление 2026-07-13: V2 controlled forward выполнен

После numeric coverage пользователь подтвердил запуск полного прохода. Выполнено:

1. V2 ablation baseline;
2. controlled train на `2026-05-01..2026-05-14`;
3. blind-forward `2026-05-15..2026-05-20`;
4. PNG-графики по всем forward-дням.

Ablation показал, что полный набор `full_v2_all_274` хуже, чем более чистый `v1_plus_risk_gate`. Поэтому текущая controlled model обучена на `v1_plus_risk_gate`: `126` feature columns, LOO AUC `0.684988`.

Forward result: `106 ENTER`, `45 UNSURE`, `284 SKIP`.

Статус: `STAS5_V2_CONTROLLED_FORWARD_READY_NO_TP_NO_API_NO_STAS3`.

Следующий практический шаг: пользователь смотрит forward PNG за `2026-05-15..2026-05-20` и отмечает, какие `ENTER/UNSURE` реальные, а какие шум. Это review-only; не использовать forward для threshold tuning без отдельного решения.

## Обновление 2026-07-13: numeric coverage после visual approval

После вопроса пользователя “все ли с графика попадает в ML обучение” проведен жесткий numeric coverage audit за день `2026-05-04`.

Решение: визуальные STAS4 strategy-блоки больше не остаются только картинкой. В ML feature matrix добавлены causal числовые группы:

1. `stas4_v2_block_*` - support/conflict/net score по четырем выбранным STAS4-блокам;
2. `stas4_v2_pattern_*` - pattern/candle/divergence/context слой;
3. `stas5_v2_short_wave_*` - SHORT/WAVE давление и отскок по окнам до входа.

Обновленный размер: V2 combo features `103 -> 163`, общий train snapshot `214 -> 274` feature columns. Row parity сохранен: train `972`, forward `435`; `KEEP_DRAFT + yellow_x = 30`; leakage guard `PASS`.

Важно: эти стратегии не дают вход сами. Они дают числовой контекст, по которому ML сможет учиться отличать human `KEEP` от шума. `X/UP`, yellow X, human label, postfact, TP/Stas3/exit не превращаются в признаки.

Статус: `STAS5_V2_NUMERIC_COVERAGE_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`.

Следующий разрешенный шаг только после пользовательского подтверждения: V2 ablation baseline по группам признаков. Не запускать финальное обучение, threshold tuning, API, Optuna или Stas3/TP.

## Обновление 2026-07-13: последний visual approval пункт

Перед ablation baseline approval-график за `2026-05-04` расширен полосой `STAS4 Audit`. На ней отображаются четыре выбранные стратегии:

1. `density_profile+structure_ta`: `X=22`, `UP=2`;
2. `pattern+structure_ta`: `X=38`, `UP=1`;
3. `structure_ta+volume_flow`: `X=52`, `UP=1`;
4. `structure_ta+trend_momentum`: `X=59`, `UP=4`.

Назначение полосы: визуально проверить стратегические risk/vote-слои. Это audit-only, не hard-filter, не label, не торговое разрешение и не обучение.

Дата: `2026-07-13`.

Статус: `STAS5_V2_FEATURE_VISUAL_APPROVAL_READY_WAIT_USER_AFTER_PRE_ML_AUDIT`.

Назначение: спроектировать второй контур STAS5 так, чтобы ML не просто повторял старые `KEEP/CUT`, а выбирал качественные LONG-входы с учетом фазы, combo-индикаторов, структуры, плотности, риска падающего движения и качества локального входа.

## 1. Цель V2

Цель V2:

```text
candidate entry + causal market context -> ENTER / UNSURE / SKIP
```

Но `ENTER` должен означать не просто похожесть на пользовательский KEEP, а:

```text
LONG разрешен + вход качественный + риск falling knife приемлемый
```

V2 не отвечает за TP/exit. Stas3 остается отдельным будущим контуром.

## 2. Архитектура V2

Целевой pipeline:

```text
1. Candidate Source
2. Phase Detector
3. STAS4 Combo Feature Exporter
4. Long Permission Gate
5. Entry Ranker ML
6. Risk/Noise Filter
7. Decision Controller
8. Audit Renderer
```

## 3. Ответственность блоков

| Блок | Ответственность | Вход | Выход |
|---|---|---|---|
| Candidate Source | дает LA-кандидаты | Stas1/Stas2 candidate rows | `candidate_id`, `entry_time`, `entry_price` |
| Phase Detector | определяет режим рынка до входа | OHLCV + Stas2 pre-windows | `phase_state`, `trend_pressure`, `volatility_state` |
| STAS4 Combo Feature Exporter | превращает combo-spectrum из картинки в признаки | OHLCV до входа + STAS4 logic | RSI/MACD/Stoch/ATR/divergence/density/structure features |
| Long Permission Gate | решает, можно ли вообще LONG | phase + combo + risk | `LONG_ALLOWED`, `NO_TRADE`, причины запрета |
| Entry Ranker ML | ранжирует входы | только causal features | `ML_KEEP_SCORE_V2` |
| Risk/Noise Filter | ловит falling knife/too high/no confirmation | risk features + score | `risk_block`, `risk_reason` |
| Decision Controller | итоговое решение | gate + score + risk | `ENTER/UNSURE/SKIP` |
| Audit Renderer | рисует и объясняет | CSV decisions + OHLCV | PNG/CSV/HTML audit |

## 4. Данные V2

Train base остается:

```text
2026-05-01..2026-05-14
```

Forward/audit base:

```text
2026-05-15..2026-05-20
```

Forward `15+` нельзя использовать для подбора threshold. Его можно использовать только как:

1. blind audit;
2. error ledger;
3. материал для следующей отдельно утвержденной ручной разметки.

## 5. Label contract V2

V2 должен хранить несколько типов label, не смешивая их:

| Поле | Значение | Использование |
|---|---|---|
| `human_label` | `KEEP/CUT` | стиль выбора пользователя |
| `outcome_label` | `GOOD/BAD/NEUTRAL` | postfact audit target, не feature |
| `risk_label` | `OK/FALLING_KNIFE/TOO_HIGH/NO_REVERSAL` | обучение risk filter после утверждения |
| `phase_label` | `LONG_ALLOWED/NO_TRADE/SHORT_PRESSURE` | обучение/проверка phase gate |
| `strategy_vote` | STAS4 vote | context/audit, не target |

Первый V2 train не должен превращать yellow X в hard-cut. `KEEP + yellow_x` по-прежнему сохраняется.

## 6. Combo features, которые нужно подключить

### 6.1 Indicator snapshot

Добавить causal snapshot на момент до входа:

```text
stas4_f008_atr14_pct
stas4_f012_rsi14
stas4_f013_macd_line
stas4_f014_macd_signal
stas4_f015_macd_hist
stas4_f015_macd_hist_delta
stas4_f017_stoch_k14
stas4_f018_stoch_d14
stoch_k_minus_d
rsi_minus_signal
```

### 6.2 Combo derived features

```text
combo_atr_regime
combo_rsi_zone
combo_rsi_slope
combo_macd_state
combo_macd_improving
combo_macd_falling
combo_stoch_zone
combo_stoch_cross_up
combo_stoch_cross_down
combo_momentum_score
combo_long_recovery_score
combo_short_pressure_score
```

### 6.3 Divergence features

Только confirmed divergence до входа:

```text
bullish_divergence_recent
hidden_bullish_divergence_recent
bearish_divergence_recent
hidden_bearish_divergence_recent
divergence_age_bars
divergence_type_code
```

Запрет: нельзя брать divergence, которая подтверждается после entry candle.

### 6.4 Density profile features

```text
density_near_vpoc60
density_near_vpoc240
density_cluster60_strength
density_vpoc60_share
density_local_vs_long_ratio
density_vpoc_drift_state
density_support_score
density_conflict_score
```

### 6.5 Structure features

```text
structure_near_support
structure_near_resistance
structure_lower_range_flag
structure_high_range_flag
structure_near_fib_support
structure_channel_position
structure_bos_down_recent
structure_bos_up_recent
structure_choch_recent
structure_support_score
structure_conflict_score
```

## 7. Phase and permission features

V2 должен явно считать:

```text
phase_strength_gate
trend_pressure_direction
long_allowed_raw
long_allowed_final
no_trade_reason
```

Минимальные правила для первого gate-аудита:

1. если `short_pressure_score` высокий и нет bullish reversal evidence -> `LONG_ALLOWED = 0`;
2. если `falling_knife_risk` высокий -> `ENTER` запрещен, максимум `UNSURE`;
3. если `pre_15/30/60m` все отрицательные и нет divergence/reclaim -> `NO_TRADE`;
4. если вход высоко в падающем диапазоне -> `SKIP`;
5. если есть confirmed bullish divergence + density support + lower range -> разрешить `UNSURE/ENTER` по ML score.

## 8. Risk features

Добавить:

```text
knife_risk_pre_entry
negative_window_count_15_30_60
weak_bounce_inside_drop
too_high_in_drop
after_spike_risk
no_clear_low_risk
low_volume_confirmation_risk
asia_weekend_risk
drawdown_proxy_score
```

Особенно важные найденные зоны риска:

1. `ASIA_PACIFIC`;
2. weekend;
3. `pre_60m_long_wave_phase = Микроход`;
4. `pre_15m_long_wave_phase = Нет LONG-волны`;
5. слабоположительный `session_so_far_close_move_pct` внутри общего падения;
6. `CAUTION_NO_CLEAR_LOW` без support/combo confirmation;
7. `CAUTION_AFTER_SPIKE` в падающем режиме.

## 9. Target V2

Нельзя учить только:

```text
human KEEP/CUT
```

Нужно добавить supervised targets:

```text
target_keep_style
target_good_entry
target_bad_risk_entry
target_long_permission
```

Первый practical target для V2:

```text
GOOD_ENTRY = human KEEP and not risk_bad
BAD_RISK_ENTRY = green/user/old candidate with falling_knife/too_high/no_reversal
```

Postfact можно использовать только для target/audit после факта, не как feature.

## 10. Forward error ledger

Создать отдельную таблицу:

```text
STAS5_ML_CORE/artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.csv
```

Поля:

```text
day
candidate_id
entry_time
ML_DECISION_V1
ML_KEEP_SCORE_V1
visual_user_review
postfact_hit_0p5
postfact_hit_1p0
postfact_max_up_pct
postfact_max_drawdown_pct
error_class
error_reason
v2_expected_decision
```

Классы:

```text
GREEN_GOOD
GREEN_BAD_FALLING_KNIFE
GREEN_BAD_TOO_HIGH
GREEN_BAD_NO_REVERSAL
YELLOW_GOOD
YELLOW_BAD
SKIP_MISSED_GOOD
SKIP_CORRECT
```

## 11. Validation V2

Обязательные проверки:

1. no future leakage;
2. feature availability time <= entry decision time;
3. train days раньше validation days;
4. leave-one-day-out только как внутренний sanity check;
5. walk-forward split;
6. no threshold tuning on `2026-05-15+`;
7. calibration report;
8. permutation importance;
9. ablation по группам признаков;
10. отдельная метрика по `KEEP + yellow_x`;
11. отдельная метрика по bad green/falling knife.

Метрики V2:

```text
GOOD_ENTRY recall
BAD_RISK precision
ENTER hit1.0 rate
ENTER median drawdown
ENTER risk/reward median
UNSURE usefulness
SKIP missed good rate
KEEP+yellow_x recall
```

Критерий улучшения:

```text
V2 должен снижать GREEN_BAD / deep drawdown без уничтожения пользовательских KEEP.
```

## 12. Ablation plan

Порядок ablation:

1. V1 baseline;
2. V1 + combo indicators only;
3. V1 + density/structure only;
4. V1 + phase gate only;
5. V1 + risk features only;
6. V2 full without yellow passive;
7. V2 full with yellow passive as audit feature;
8. V2 full with permission gate.

Если yellow passive ухудшает recall хороших `KEEP + yellow_x`, его не включать.

## 13. Что запрещено

Запрещено:

1. использовать `postfact_*` как feature;
2. использовать future candles в combo/divergence;
3. брать Stas3/TP/exit в entry ML;
4. делать hard-cut по yellow X;
5. удалять `KEEP + yellow_x`;
6. подбирать threshold по forward `2026-05-15+`;
7. считать `ML_KEEP_SCORE` вероятностью профита;
8. запускать API/мост Bybit из V2 research;
9. делать Optuna до готового V2 audit dataset.

## 14. Минимальный план реализации

1. Готово: создать `stas5_v2_combo_feature_exporter.py`.
2. Готово: пересчитать STAS4 combo/density/structure features для всех train candidates `2026-05-01..2026-05-14`.
3. Готово: пересчитать те же features для forward candidates `2026-05-15..2026-05-20`.
4. Готово: создать `stas5_v2_feature_snapshot_builder.py`.
5. Готово: создать `stas5_v2_leakage_guard.py`.
6. Готово: создать `stas5_v2_forward_error_ledger.py`.
7. Готово: сделать V2 pre-ML audit.
8. Готово: сделать V2 feature visual approval graph за `2026-05-04`.
9. Следующий шаг: пользователь смотрит approval PNG и подтверждает, что признаки на графике читаются правильно.
10. После визуального подтверждения сделать ablation baseline.
11. Только после ablation обучать V2 controlled model.
12. Нарисовать V2 forward PNG: price + volume + combo spectrum + gate strip + ML decision.

## 14.1. Факт реализации combo exporter

Реализован файл:

```text
src/mlbotnav/stas5_v2_combo_feature_exporter.py
```

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.csv
STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260501_20260514_v0.manifest.json
STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.csv
STAS5_ML_CORE/artifacts/v2/features/stas5_v2_combo_features_20260515_20260520_forward_v0.manifest.json
```

Контроль:

1. train: `PASS`, `972` строк, `103` V2-признака;
2. forward: `PASS`, `435` строк, `103` V2-признака;
3. `feature_time_utc = anchor_time_utc`;
4. `feature_time_utc < entry_time_utc`;
5. forbidden columns `{}`;
6. divergence берется только после подтверждения `confirm_idx <= signal_idx`.

## 14.2. Факт реализации V2 feature snapshot

Реализован файл:

```text
src/mlbotnav/stas5_v2_feature_snapshot_builder.py
```

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.csv
STAS5_ML_CORE/artifacts/v2/features/stas5_v2_feature_snapshot_20260501_20260514_v0.manifest.json
```

Контроль:

1. `PASS`;
2. `972` строк;
3. `214` feature columns;
4. `111` v1/Stas2 признаков;
5. `103` V2 combo признака;
6. `lost_after_combo_join = 0`;
7. `lost_after_ledger_check = 0`;
8. `entry_time_mismatch = 0`;
9. `anchor_time_mismatch = 0`;
10. `v2_combo_feature_available_before_entry_false = 0`;
11. forbidden columns `{}`;
12. `KEEP_DRAFT + yellow_x = 30` сохранены.

## 14.3. Факт реализации V2 leakage guard

Реализован файл:

```text
src/mlbotnav/stas5_v2_leakage_guard.py
```

Артефакт:

```text
STAS5_ML_CORE/artifacts/v2/guard/stas5_v2_leakage_guard_20260501_20260514_v0.json
```

Контроль:

1. `PASS`;
2. `972` строк;
3. `214` feature columns;
4. manifest status `PASS`;
5. `row_count_matches_manifest = true`;
6. `row_count_matches_expected_train = true`;
7. `output_duplicate_keys = 0`;
8. `feature_columns_missing_in_csv = []`;
9. `forbidden_feature_columns = {}`;
10. `label_columns_in_features = []`;
11. `metadata_columns_in_features = []`;
12. `unexpected_forbidden_nonfeature_columns = {}`;
13. `missing_required_metadata_columns = []`;
14. `v2_combo_feature_time_not_before_entry = 0`;
15. `v2_combo_available_before_entry_false = 0`;
16. `v2_combo_entry_time_mismatch = 0`;
17. `v2_combo_anchor_time_mismatch = 0`;
18. `context_max_open_time_after_entry = 0`;
19. `forward_days_present = 0`;
20. `KEEP_DRAFT = 115`, `CUT_DRAFT = 857`;
21. `KEEP_DRAFT + yellow_x = 30` сохранены.

Это закрывает раздел 14, пункт 5.

## 14.4. Факт реализации V2 forward error ledger

Реализован файл:

```text
src/mlbotnav/stas5_v2_forward_error_ledger.py
```

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.csv
STAS5_ML_CORE/artifacts/v2_audit/stas5_forward_error_ledger_20260515_20260520_v0.manifest.json
```

Контроль:

1. `PASS`;
2. `435` forward candidates;
3. source V1 rows `435`;
4. source V2 rows `435`;
5. `missing_v2_rows_after_join = 0`;
6. `duplicate_output_keys = 0`;
7. day counts: `2026-05-15=90`, `2026-05-16=76`, `2026-05-17=63`, `2026-05-18=73`, `2026-05-19=65`, `2026-05-20=68`;
8. V1 decisions: `ENTER=103`, `UNSURE=55`, `SKIP=277`;
9. error classes: `GREEN_BAD_FALLING_KNIFE=46`, `GREEN_BAD_NO_REVERSAL=9`, `GREEN_GOOD=48`, `YELLOW_BAD=34`, `YELLOW_GOOD=21`, `SKIP_CORRECT=212`, `SKIP_MISSED_GOOD=65`;
10. V2 expected decisions: `ENTER=35`, `UNSURE=121`, `SKIP=279`;
11. loaded user-review rows: `90`, пока в основном `PENDING_USER_REVIEW`;
12. postfact поля и user-review label остаются `audit_only`, не feature и не train target.

Это закрывает раздел 14, пункт 6.

## 14.5. Факт реализации V2 pre-ML audit

Реализован файл:

```text
src/mlbotnav/stas5_v2_pre_ml_audit.py
```

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2_audit/STAS5_V2_PRE_ML_AUDIT_20260501_20260520_RU.md
STAS5_ML_CORE/artifacts/v2_audit/stas5_v2_pre_ml_audit_20260501_20260520_v0.json
```

Контроль:

1. status `READY_FOR_V2_ABLATION_BASELINE`;
2. train rows `972`;
3. `KEEP_DRAFT=115`, `CUT_DRAFT=857`;
4. `KEEP_DRAFT + yellow_x = 30`;
5. feature count `214`;
6. V2 guard `PASS`;
7. forward error ledger `PASS`;
8. forbidden feature columns `{}`;
9. forward bad green: `55`;
10. forward good green: `48`;
11. forward missed good SKIP: `65`;
12. strongest train KEEP/CUT groups: `v1_stas1_candidate`, `v1_stas2_pre_windows`, `v2_combo_indicator`, `v2_structure`;
13. top numeric signals include `stas1_feature_ret_15m_pct`, `pre_15m_close_move_pct`, `stas4_v2_structure_fib_0382_dist_pct`, `stas4_v2_combo_ema20_slope5_pct`, `score`, `stas4_v2_volume_obv_slope5`, `stas4_v2_combo_rsi14`.

Это закрывает раздел 14, пункт 7. Перед ablation добавлен обязательный визуальный контроль признаков.

## 14.6. Факт реализации V2 feature visual approval

Реализован файл:

```text
src/mlbotnav/stas5_v2_feature_visual_approval.py
```

Назначение: показать один train-день `2026-05-04` в стиле старого STAS4 overlay, но уже с train labels и V2 causal features. Это не обучение и не trading permission.

Артефакты:

```text
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.png
STAS5_ML_CORE/artifacts/v2/visual_approval/20260504/STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.manifest.json
```

На графике есть:

1. свечи и volume `SOLUSDT 1m`;
2. session shading;
3. полосы `FON`, `LONG`, `SHORT`, `WAVE`;
4. все `74` LA-кандидата дня;
5. human `KEEP/CUT`, yellow X и `KEEP + yellow_x` conflict;
6. density/structure support/conflict;
7. risk/gate: `knife_risk`, `short_pressure`, `long_recovery`, `long_allowed=0`;
8. V2 combo snapshot по кандидатам;
9. старый-style `COMBO SPECTRUM: RSI + MACD + STOCH + ATR + divergence`.

Контроль:

1. status `STAS5_V2_FEATURE_VISUAL_APPROVAL_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3`;
2. rows `74`;
3. labels: `KEEP_DRAFT=9`, `CUT_DRAFT=65`;
4. visual markers: все `KEEP_DRAFT=9` рисуются зелеными KEEP-маркерами;
5. `KEEP + yellow_x_conflict=4` дополнительно получают голубую conflict-накладку, но не перестают быть зелеными KEEP;
6. yellow X на `CUT` рисуется отдельной желтой audit-накладкой: `18`;
7. approval buckets для таблицы: `KEEP=5`, `CONFLICT=4`, `YELLOW_X=18`, `CUT=47`;
8. risk buckets: `HIGH_RISK=38`, `CAUTION=21`, `LOW_RISK=13`, `BLOCKED=2`;
9. KEEP ids: `LA002`, `LA004`, `LA020`, `LA032`, `LA038`, `LA042`, `LA045`, `LA049`, `LA065`;
10. yellow X count `22`, yellow conflicts `4`;
11. image check: `4960x4262`, not blank.

Следующий пункт: пользователь визуально проверяет PNG. Ablation baseline не запускать до подтверждения.

## 15. Ожидаемый вид V2 PNG

На V2 forward PNG должны быть видны:

1. свечи;
2. volume;
3. STAS5 decision markers;
4. combo spectrum strip;
5. `LONG_ALLOWED / NO_TRADE` strip;
6. `short_pressure_score`;
7. `falling_knife_risk`;
8. причина запрета для плохих входов.

Цветовая логика:

```text
green = ENTER
yellow = UNSURE
gray = SKIP
red marker/label = blocked by gate
blue/cyan = confirmed support/reversal evidence
```

## 16. Решение

STAS5 V2 должен быть не просто второй моделью, а вторым контуром:

```text
Combo-aware, phase-aware, risk-aware entry permission system.
```

Главная цель V2:

```text
убрать зеленые входы в падающем движении, не потеряв хорошие пользовательские bottom/reversal KEEP.
```
