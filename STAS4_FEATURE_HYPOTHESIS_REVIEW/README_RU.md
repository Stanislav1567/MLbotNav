# STAS4 Feature Hypothesis Review

Статус: `STAS4_ROOT_REVIEW_HOME`.

Эта папка является корневым домом STAS4. Раньше артефакты лежали в `reports/final_review/stas4_feature_hypothesis_screen_v0`; теперь рабочий путь:

```text
STAS4_FEATURE_HYPOTHESIS_REVIEW
```

## Назначение

STAS4 хранит фичи, гипотезы, индикаторы, combo spectrum, strategy overlays и ручную review-разметку поверх Stas2-кандидатов входа.

Связка этапов:

```text
STAS1_GOOD_LOW_REVIEW -> STAS2_MARKET_PHASE_REVIEW -> STAS4_FEATURE_HYPOTHESIS_REVIEW -> STAS5_ML_CORE
```

STAS3 сюда не входит: STAS3 отвечает за выходы/TP.

## Главная 14-Дневная Разметка

Папка:

```text
STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels
```

Итог `2026-05-01..2026-05-14`:

- всего входов: `972`;
- `KEEP_DRAFT`: `115`;
- `CUT_DRAFT`: `857`;
- yellow X всего: `287`;
- `KEEP_DRAFT` с yellow X: `30`.

Ключевое правило:

```text
yellow_x_role = AUDIT_ONLY
human KEEP_APPROVED > strategy yellow X
```

Формальный guard:

```text
STAS4_FEATURE_HYPOTHESIS_REVIEW/density_structure_20260501_20260514_combo_spectrum/manual_labels/YELLOW_X_AUDIT_ONLY_RULE_RU.md
```

## Граница

Эта папка содержит review/artifact слой для будущего STAS5 ML. Она не является финальным ML-dataset сама по себе. ML/export/training, Optuna, scorer, target-lock и API запускаются только отдельным утвержденным этапом.
