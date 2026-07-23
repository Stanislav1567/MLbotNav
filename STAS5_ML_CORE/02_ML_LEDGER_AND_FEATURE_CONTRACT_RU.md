# STAS-5: контракт ML-ledger и feature snapshot

Статус: `DRAFT_CONTRACT_NO_ML_NO_OPTUNA`.

Дата фиксации: `2026-07-10`.

## 1. Назначение

Этот контракт фиксирует разделение:

1. human labels;
2. strategy votes;
3. pre-entry features;
4. post-entry labels;
5. audit-only поля.

Главная защита:

```text
human_label != strategy_vote
```

## 2. ML-ledger

ML-ledger - это единая таблица входов `LAxxx`, где каждая строка соответствует одному кандидату входа.

Минимальные поля:

| Поле | Роль |
|---|---|
| `day` | день входа |
| `candidate_id` | `LAxxx` |
| `record_id` | стабильный ID строки источника |
| `entry_time` | время входа |
| `entry_price` | цена входа / execution reference |
| `human_label` | `KEEP_DRAFT`, `CUT_DRAFT`, `KEEP_APPROVED`, `CUT_APPROVED` |
| `label_status` | `DRAFT`, `APPROVED`, `REVIEW_ONLY`, `EXCLUDED` |
| `yellow_x` | есть ли желтый X стратегии |
| `yellow_x_role` | всегда `AUDIT_ONLY` до отдельного решения |
| `yellow_x_conflict` | `1`, если `KEEP` и `yellow_x = 1` |

## 3. Human label

Human label является главным источником будущей ML-разметки.

Разрешенные значения:

1. `KEEP_DRAFT`;
2. `CUT_DRAFT`;
3. `KEEP_APPROVED`;
4. `CUT_APPROVED`;
5. `REVIEW_ONLY`;
6. `EXCLUDED`.

Правило:

```text
KEEP_APPROVED > strategy yellow X
```

## 4. Strategy votes

Strategy votes - это отдельные поля, которые показывают, что думали стратегии или индикаторные блоки.

Они не являются label.

Примеры:

1. `stas4_density_structure_yellow_x`;
2. `structure_ta_trend_momentum_vote`;
3. `volume_flow_vote`;
4. `pattern_structure_vote`;
5. `strategy_vote_source`.

На первом ML-прогоне эти поля не входят в feature matrix. Они используются только для audit.

## 5. Feature snapshot

Feature snapshot собирается на момент до входа.

Обязательное правило:

```text
feature_available_at <= decision_time
```

Если поле известно только после входа, оно не может быть feature.

## 6. Denylist для feature matrix

Запрещены:

1. `future_return`;
2. `hit_*`;
3. `time_to_*`;
4. `mfe*`;
5. `mae*`;
6. `post_entry_*`;
7. `ideal_review_tp_pct`;
8. `max_feasible_review_tp_pct`;
9. `tp_after_entry`;
10. `wave_end_*`;
11. `macro_wave_full_move_pct`, если он включает будущее;
12. `yellow_x`;
13. `would_cut`;
14. `strategy_cut`;
15. `strategy_vote` на первом baseline;
16. entry-candle `high/low/close/volume`, если решение принимается на open этой свечи.

## 7. Guardrails перед обучением

Перед любым training/export:

1. `row_count_before_join == row_count_after_join`;
2. все `KEEP_APPROVED` сохранены;
3. все `KEEP_APPROVED + yellow_x = 1` сохранены;
4. `CUT_DRAFT` не используется как final negative;
5. feature matrix построена через allowlist;
6. denylist-колонки отсутствуют;
7. все `feature_available_at <= decision_time`;
8. train window `2026-05-01..2026-05-14` отделен от forward window `2026-05-15+`;
9. Stas3-поля отсутствуют в feature matrix.

## 8. Первый audit до ML

До первой controlled ML-модели нужно получить отчет:

1. распределение признаков у `KEEP_DRAFT` и `CUT_DRAFT`;
2. список признаков, которые сильнее всего разделяют `KEEP` и `CUT`;
3. список желтых `X`, которые конфликтуют с `KEEP`;
4. фазы и сессии, где больше хороших входов;
5. места, где Stas4 vote ошибался;
6. список join/coverage проблем.

## 9. Первый controlled ML

Первый controlled ML:

1. baseline без yellow-полей;
2. train по дням `2026-05-01..2026-05-14`;
3. метрика `KEEP recall`;
4. отдельная метрика `KEEP_WITH_YELLOW_X recall`;
5. forward check на `2026-05-15+`;
6. результат только как review, не как live trading.

Цель первой модели - не максимальная прибыль, а сохранение пользовательских хороших входов и уменьшение шума.

Forward check должен сохранять CSV и PNG с ML-точками входа. Каждая кандидатная точка на PNG должна иметь статус `ENTER`, `UNSURE` или `SKIP`. TP/Stas3 не участвуют. Forward window `2026-05-15+` не используется для обучения, подбора threshold или ручной доводки. Future outcome после входа допустим только в audit/backtest-отчете и запрещен как feature, target, filter и threshold input.
