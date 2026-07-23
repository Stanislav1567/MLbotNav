# STAS5 ML Core

Статус: `STAS5_ML_ENTRY_ARCHITECTURE_DRAFT_NO_ML_NO_OPTUNA`.

Дата фиксации: `2026-07-10`.

Эта папка фиксирует новый source-of-truth для STAS-5: ML по входам.

Главная цель STAS-5 - научить ML выбирать хорошие входы из кандидатов Stas1/Stas2, используя Stas2 и Stas4 как контекст, но не ломая старую логику и не превращая стратегии в жесткие фильтры.

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
3. `schemas/stas5_ml_ledger_v0.yaml` - черновая схема ledger-таблицы.
4. `schemas/stas5_feature_snapshot_v0.yaml` - черновая схема feature snapshot.

## Жесткая граница

Этот этап не запускает:

1. ML-обучение;
2. ML-export;
3. Optuna;
4. scorer;
5. target-lock;
6. торговый API;
7. изменение старой Stas1/Stas2/Stas4-логики.

STAS-5 сначала создает правильный ledger, feature snapshot, audit и guardrails. Только после этого возможен controlled ML.
