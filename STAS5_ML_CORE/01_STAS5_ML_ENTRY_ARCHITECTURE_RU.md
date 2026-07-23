# STAS-5: ML по входам

Статус: `DRAFT_FOR_APPROVAL_NO_ML_NO_OPTUNA`.

Дата фиксации: `2026-07-10`.

## 1. Цель

Научить ML выбирать хорошие входы из кандидатов Stas1/Stas2 по Stas2/Stas4 pre-entry контексту и human KEEP/CUT.

Итоговый STAS-5 должен стать не фильтром входов, а ML-ранжировщиком:

```text
candidate_id -> ML_KEEP_SCORE 0..1 -> ENTER / SKIP / UNSURE
```

Stas3, TP, exit, MFE/MAE и post-entry ladder не входят в STAS-5 entry ML.

## 2. Что уже есть

1. Stas1/Stas2 дают кандидаты входов `LAxxx`.
2. Stas4 дает признаки, контекст, стратегии и индикаторы.
3. Ручная разметка `14` дней: `972` входа, `115` `KEEP_DRAFT`, `857` `CUT_DRAFT`.
4. Желтый `X` зафиксирован как `AUDIT_ONLY`, а не фильтр.

## 3. Главное правило

ML учится не на желтом `X`, не на стратегии, а на решении человека:

```text
candidate entry + pre-entry features -> human KEEP / CUT
```

`human KEEP` всегда главнее любой стратегии.

Если стратегия поставила желтый `X`, но человек оставил вход, это не ошибка человека и не причина выкинуть строку. Это конфликт, который нужно сохранить:

```text
yellow_x_conflict = 1
```

## 4. Этап 1: сделать ML-ledger

Собрать единую таблицу всех входов.

Обязательные поля:

1. `day`;
2. `candidate_id`;
3. `record_id`;
4. `entry_time`;
5. `entry_price`;
6. `human_label`;
7. `label_status`;
8. `yellow_x`;
9. `yellow_x_role`;
10. `yellow_x_conflict`.

Правила статусов:

1. `KEEP_DRAFT` и `CUT_DRAFT` пока являются черновиком.
2. После утверждения они становятся `KEEP_APPROVED` и `CUT_APPROVED`.
3. `yellow_x_role = AUDIT_ONLY`.
4. `yellow_x_conflict = 1`, если человек оставил вход, а стратегия поставила `X`.

## 5. Этап 2: собрать feature snapshot до входа

На каждый `LAxxx` собрать только то, что известно до входа.

Разрешенные группы:

1. Stas2 фон;
2. LONG/SHORT проценты;
3. WAVE только если поле имеет корректный causal/audit scope;
4. сессия;
5. процентная лестница как pre-entry context, если она не использует post-entry исход;
6. combo RSI/MACD/Stoch/ATR;
7. divergence/convergence;
8. ATR/волатильность;
9. volume flow;
10. structure flags;
11. pattern flags;
12. density profile;
13. расстояние до локального low/high;
14. кластер входов рядом;
15. контекст предыдущих свечей.

Запрещено:

1. `future_return`;
2. MFE/MAE после входа;
3. TP после входа;
4. будущие свечи;
5. future WAVE end;
6. любые поля, которые известны только после `entry_time`.

## 6. Этап 3: разделить labels и strategy votes

Human label хранится отдельно.

Strategy votes хранятся отдельно.

Нельзя смешивать:

```text
label != strategy_signal
```

Стратегии не говорят ML, что хорошо или плохо. Они только дают контекст.

## 7. Этап 4: первый ML без yellow X

Первую модель обучать без yellow-полей в признаках.

Запрещены в feature matrix:

1. `yellow_x`;
2. `would_cut`;
3. `strategy_cut`;
4. `strategy_vote`;
5. любые производные hard-cut поля стратегии.

Задача первой модели - понять стиль выбора входов пользователем без давления старой стратегии.

## 8. Этап 5: guardrails

Перед любым обучением проверять:

1. все `KEEP_APPROVED` на месте;
2. ни один `KEEP + yellow_x = 1` не удален;
3. row count до и после join совпадает;
4. признаки только pre-entry;
5. нет future leakage;
6. `CUT_DRAFT` не используется как финальный negative без утверждения.

## 9. Этап 6: первый отчет без финального ML

Сначала не гоним финальную ML.

Делаем audit:

1. какие признаки чаще у `KEEP`;
2. какие признаки чаще у `CUT`;
3. какие признаки отделяют шум;
4. где стратегии ошиблись;
5. какие yellow `X` резали хорошие входы;
6. какие фазы дают лучшие входы;
7. какие сессии дают лучшие входы.

## 10. Этап 7: первый controlled ML и forward review

Только после audit:

1. baseline model без yellow `X`;
2. train по `2026-05-01..2026-05-14`;
3. отдельная метрика по `KEEP + yellow_x`;
4. цель - высокий recall по `KEEP`, особенно по конфликтным входам;
5. forward check на `2026-05-15+`, где human labels не подаются модели;
6. результат forward check - CSV и PNG с ML-точками входа `ENTER/UNSURE/SKIP`.

Forward window `2026-05-15+` не используется для обучения, подбора threshold или ручной доводки. Forward PNG должен помечать каждую кандидатную точку как `ENTER`, `UNSURE` или `SKIP`. Forward PNG не рисует TP, Stas3 exit, MFE/MAE или future ladder. Будущее после входа можно считать только как post-fact audit, не как feature.

## 11. Этап 8: ablation

Потом сравниваем:

1. без Stas4;
2. со Stas4 признаками;
3. с combo-индикатором;
4. с volume flow;
5. с pattern/structure;
6. с yellow `X` только как passive feature.

Если yellow `X` ухудшает recall хороших входов, его не использовать.

## 12. Ответственность блоков

| Блок | Ответственность | Решает вход? |
|---|---|---|
| Stas1/Stas2 | Дают кандидаты `LAxxx` и pre-entry контекст | Нет |
| Human ledger | Дает `KEEP/CUT` как основной label | Да, как источник разметки |
| Stas4 | Дает признаки и strategy votes | Нет |
| Yellow X | Audit-only конфликт/голос стратегии | Нет |
| STAS5 Feature Snapshot | Собирает causal features до входа | Нет |
| STAS5 ML Ranker | Считает `ML_KEEP_SCORE` и entry-статус `ENTER/UNSURE/SKIP` | Да, только для entry review |

## 13. Итог STAS-5

STAS-5 должен сделать ML-ранжировщик, а не жесткий фильтр:

```text
for each Stas2 candidate:
    ML_KEEP_SCORE = 0..1
    decision = ENTER / UNSURE / SKIP
```

Первый приоритет - сохранить хорошие пользовательские входы. Особенно те, которые старая стратегия ошибочно пометила желтым `X`.
