# STAS5 V4

Статус: `STAS5_V4_OFFLINE_GROUP_REVIEW_DONE__V4L_LIVE_SAFE_REQUIRED`.

V4 - это `Human-Style Group Ranker`: модель должна выбирать лучший local low внутри группы кандидатов, а не независимо красить каждую строку в `ENTER/SKIP`.

Главное правило после аудита `2026-07-14`: будущий состав группы тоже считается future leakage. Текущий V4 train/forward полезен как offline review, но не является live-safe моделью, потому что часть group features была рассчитана по уже собранной группе.

Следующий рабочий контур:

```text
STAS5_ML_CORE/08_STAS5_V4L_LIVE_SAFE_GROUP_RANKER_PLAN_RU.md
```

V4L должен считать только `*_so_far` признаки на момент кандидата и проходить `prefix invariance`: score/decision раннего кандидата не меняются после добавления будущих строк.

Текущая рамка данных:

```text
train_base_14 = 2026-05-01..2026-05-14
forward_review_11 = 2026-05-15..2026-05-25
```

`2026-05-15` входит в общий forward-review блок вместе с `2026-05-16..2026-05-25`; отдельный 15-only approved статус superseded. Объединенный ledger остается `DRAFT_NO_TRAINING`, пока не построены group features и не пройден финальный guard.

Главное ТЗ:

```text
STAS5_ML_CORE/07_STAS5_V4_HUMAN_STYLE_GROUP_RANKER_TZ_RU.md
```

Текущий единый forward-review ledger:

```text
STAS5_ML_CORE/artifacts/v4/group_rank_ledger/STAS5_V4_GROUP_RANK_LEDGER.csv
STAS5_ML_CORE/artifacts/v4/group_rank_review/20260515_20260525/STAS5_V4_GROUP_RANK_LEDGER_20260515_20260525_FORWARD_REVIEW_V1.csv
```

Схема ledger:

```text
STAS5_ML_CORE/schemas/STAS5_V4_GROUP_RANK_LEDGER.schema.json
```

Граница: текущий V4 offline train/forward уже был запущен для проверки идеи group-rank, но после no-future аудита он помечен как `OFFLINE_GROUP_REVIEW_NOT_LIVE_SAFE`. Для live/production нужен новый V4L replay dataset, live-safe guard и новое обучение без full-group features.

V4L live-safe контур создан 2026-07-14. Рабочая команда:

```powershell
.\STAS5_ML_CORE\run_stas5_v4l_live_safe_train_forward.ps1
```

Последний проверенный V4L forward:

```text
STAS5_ML_CORE/artifacts/v4l/forward/runs/stas5_v4l_forward_20260526_20260530_20260714_181635
```
