# STAS5 V1 Hard Audit

Дата: `2026-07-13`.

Статус: `STAS5_V1_HARD_AUDIT_DONE_NEEDS_V2_CONTOUR2`.

Назначение: честно проверить, как реально работал первый STAS5 ML baseline, что было подключено, что не было подключено, почему появились неправильные зеленые входы и что нужно исправить во втором контуре.

## 1. Короткий вывод

STAS5 v1 технически собран правильно:

1. ledger собран без потери строк;
2. feature snapshot собран только из pre-entry признаков;
3. leakage guard прошел;
4. model manifest согласован;
5. forward `2026-05-15..2026-05-20` не использовался для обучения или threshold tuning.

Но STAS5 v1 не является финальным рабочим входным ML-контуром.

Главная причина: v1 учился повторять `human KEEP/CUT` по ограниченной матрице Stas1/Stas2 признаков, но не получил полноценный STAS4 combo-spectrum/indicator block и не имел отдельного `LONG_ALLOWED / NO_TRADE` permission gate.

Итоговая формула v1 была:

```text
Stas1/Stas2 candidate + limited pre-entry features -> human KEEP/CUT -> ML_KEEP_SCORE
```

А для рабочего V2 нужна формула:

```text
market regime + combo spectrum + structure/density + risk gate + entry ranker -> ENTER/UNSURE/SKIP
```

## 2. Что было собрано правильно

Артефакты STAS5 v1:

1. ledger: `STAS5_ML_CORE/artifacts/ledger/stas5_ml_ledger_20260501_20260514_v0.csv`;
2. features: `STAS5_ML_CORE/artifacts/features/stas5_feature_snapshot_20260501_20260514_v0.csv`;
3. guard: `STAS5_ML_CORE/artifacts/guard/stas5_leakage_guard_20260501_20260514_v0.json`;
4. audit: `STAS5_ML_CORE/artifacts/audit/STAS5_PRE_ML_AUDIT_20260501_20260514_RU.md`;
5. model: `STAS5_ML_CORE/artifacts/model/stas5_entry_ranker_20260501_20260514_v0.joblib`;
6. model manifest: `STAS5_ML_CORE/artifacts/model/stas5_entry_ranker_20260501_20260514_v0.manifest.json`;
7. forward review: `STAS5_ML_CORE/artifacts/forward/`.

Проверенные факты:

| Проверка | Результат |
|---|---:|
| Train window | `2026-05-01..2026-05-14` |
| Ledger rows | `972` |
| `KEEP_DRAFT` | `115` |
| `CUT_DRAFT` | `857` |
| Yellow X всего | `287` |
| `KEEP_DRAFT + yellow_x` | `30` |
| Feature columns в модели | `111` |
| Leakage guard | `PASS` |
| Pre-ML audit | `READY_FOR_CONTROLLED_BASELINE` |
| Model status | `CONTROLLED_BASELINE_READY` |
| Forward status | `FORWARD_ENTRY_REVIEW_READY` |

## 3. Что v1 реально видел при обучении

Модель v1:

```text
LogisticRegression(class_weight=balanced)
threshold ENTER = 0.65
threshold UNSURE = 0.45
```

В feature matrix вошло:

1. Stas1 low-anchor признаки;
2. `stas1_feature_rsi14`;
3. `stas1_feature_macd_hist`;
4. `range_pos_10/20/60/120`;
5. `ret_15m/30m/60m`;
6. `volume_ratio20`;
7. `pre_5m/pre_15m/pre_30m/pre_60m` фазы;
8. `long_wave` признаки;
9. `session_so_far`;
10. `day_so_far`;
11. `entry_setup_quality_code/rank`;
12. session/day context.

Важное ограничение: это не полный график, который видит человек глазами. Это табличная матрица из 111 признаков.

## 4. Что v1 не видел

В v1 не вошло:

1. `combo_spectrum`;
2. полноценный RSI/MACD/Stoch/ATR block;
3. `F008_ATR14`;
4. `F012_RSI14` как STAS4 indicator block;
5. `F013/F014/F015 MACD line/signal/hist` как STAS4 block;
6. `F017/F018 STOCH K/D`;
7. confirmed divergence features;
8. density profile features `F025-F034`;
9. structure TA features: support/resistance/fib/channel/BOS/CHOCH;
10. strategy marks as passive structured features;
11. `combo_long_score`;
12. `combo_short_pressure`;
13. `long_allowed`;
14. `falling_knife_risk`;
15. `weak_bounce_inside_drop`.

Также намеренно не вошли:

1. `yellow_x`;
2. `strategy_vote`;
3. `would_cut`;
4. Stas3;
5. TP/exit;
6. future outcome;
7. `postfact_*`;
8. MFE/MAE.

Исключение future/TP/Stas3 правильно. Но исключение всего combo-spectrum сделало v1 слишком слепым к качеству рыночного режима.

## 5. Где найден combo-spectrum

Combo-spectrum существует и был внедрен в STAS4 как визуальный audit layer.

Главная папка:

```text
STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum
```

Пример со скрина пользователя:

```text
STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/20260504/STAS4_density_profile+structure_ta_OVERLAY_COMBO_SPECTRUM_20260504_20260710_102322.png
```

Код:

```text
src/mlbotnav/visual_entry_stas4_family_overlay.py
```

Ключевые функции:

1. `_add_combo_spectrum_features`;
2. `_divergence_segments`;
3. `_render_combo_spectrum`.

В JSON этого слоя есть guardrail:

```text
combo_spectrum_is_visual_feature_layer_not_ml_training
```

Значит combo не потерян. Он просто не был подключен к STAS5 v1 feature matrix.

## 6. Почему combo не был подключен к v1

Причина не техническая поломка, а архитектурное ограничение первого baseline.

STAS5 v1 сознательно был построен через allowlist:

```text
stas1_feature_*
pre_*
session_so_far_*
day_so_far_*
session/setup context
```

Это позволило быстро и безопасно собрать первый controlled baseline без future leakage и без hard-cut по yellow X.

Но STAS4 combo-spectrum тогда остался:

```text
visual/review/audit layer
```

а не:

```text
causal model feature exporter
```

Для V2 нужен отдельный exporter, который пересчитает STAS4 indicator/density/structure признаки для каждого candidate до входа и запишет их в feature snapshot.

## 7. Forward-аудит качества

Forward проверка:

```text
2026-05-15..2026-05-20
```

Всего:

| Decision | Rows | hit 0.5% | hit 1.0% | median max up | median drawdown |
|---|---:|---:|---:|---:|---:|
| ENTER | `103` | `74.8%` | `46.6%` | `0.951%` | `-1.453%` |
| UNSURE | `55` | `74.5%` | `38.2%` | `0.796%` | `-1.045%` |
| SKIP | `277` | `46.2%` | `23.5%` | `0.410%` | `-1.023%` |

Вывод: `ENTER` отделяет часть хороших входов, но почти не отделяет риск. `UNSURE` по маленькому движению почти такой же, как `ENTER`.

Самые проблемные дни:

| День | ENTER | hit 0.5% | hit 1.0% | median drawdown |
|---|---:|---:|---:|---:|
| `2026-05-15` | `14` | `50.0%` | `14.3%` | `-2.834%` |
| `2026-05-16` | `12` | `33.3%` | `16.7%` | `-3.205%` |
| `2026-05-17` | `18` | `83.3%` | `50.0%` | `-3.250%` |
| `2026-05-18` | `21` | `100.0%` | `90.5%` | `-1.082%` |
| `2026-05-19` | `20` | `65.0%` | `20.0%` | `-1.120%` |
| `2026-05-20` | `18` | `94.4%` | `66.7%` | `-0.232%` |

По скрину пользователя `2026-05-15` претензия подтверждена цифрами: зеленые часто дают только маленький отскок, а не качественный LONG-вход.

## 8. Почему появились плохие зеленые входы

Причины:

1. v1 target учил модель на `human KEEP/CUT`, а не на отдельном классе `GOOD_LONG_ENTRY_WITH_ACCEPTABLE_RISK`;
2. v1 не имел признака `short_pressure`;
3. v1 не имел признака `falling_knife_risk`;
4. v1 не имел отдельного `LONG_ALLOWED`;
5. combo-spectrum был визуальным, а не числовым ML-блоком;
6. `ML_KEEP_SCORE` не является вероятностью профита;
7. простое поднятие threshold не решает проблему, потому что плохие `ENTER` имеют почти такие же scores, как хорошие.

Факт по score calibration:

```text
bad ENTER median score около 0.797
good ENTER median score около 0.808
```

Значит v2 должен исправлять не только порог, а признаки, target и permission gate.

## 9. Главные ошибки v1

Технических фатальных ошибок не найдено.

Архитектурные ошибки:

1. недостаточная feature matrix;
2. отсутствует STAS4 combo feature exporter;
3. отсутствует phase/permission gate;
4. отсутствует risk target;
5. отсутствует отдельная разметка плохих forward-зеленых;
6. нет классов ошибок вроде `FALLING_KNIFE`, `TOO_HIGH_IN_DROP`, `WEAK_BOUNCE`;
7. модель оптимизирована на похожесть на KEEP, а не на качество входа с учетом риска;
8. нет отдельного анализа `ENTER` против `UNSURE` по risk/reward.

## 10. Что обязательно нужно в V2

V2 должен добавить:

1. `STAS4 Combo Feature Exporter`;
2. `Phase Detector / Phase Gate`;
3. `Long Permission Controller`;
4. `Risk/Noise Filter`;
5. risk-aware labels;
6. forward error ledger;
7. ablation по группам признаков;
8. walk-forward validation;
9. calibration report;
10. feature importance/permutation audit.

## 11. Внешние правила проверки ML

Используем не как замену проектным данным, а как правила валидации:

1. scikit-learn `TimeSeriesSplit` требует time-aware split для временных данных, потому что обычные CV могут обучаться на будущем и оцениваться на прошлом: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
2. scikit-learn cross-validation guide прямо предупреждает, что для time-dependent process безопаснее использовать time-series aware scheme: https://scikit-learn.org/stable/modules/cross_validation.html
3. Для вероятностных решений нужен calibration audit, потому что probability output не всегда хорошо откалиброван: https://scikit-learn.org/stable/modules/calibration.html
4. Для понимания, чем реально пользуется модель, нужен permutation importance или аналогичный feature inspection: https://scikit-learn.org/stable/modules/permutation_importance.html
5. Для финансовых моделей нужен отдельный контроль backtest overfitting и out-of-sample проверки из-за non-stationarity/regime shifts: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4686376

## 12. Решение аудита

STAS5 v1 оставить как:

```text
CONTROLLED_BASELINE / AUDIT REFERENCE
```

Не использовать v1 как:

```text
production entry permission
```

Следующий этап:

```text
STAS5 V2 / CONTOUR 2
```

с обязательным подключением combo-spectrum и отдельного permission/risk gate.
