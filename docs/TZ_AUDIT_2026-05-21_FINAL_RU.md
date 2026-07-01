# Аудит ТЗ и остатки (на 2026-05-21)

Источник: `TECH_SPEC_ML_PLATFORM_RU.md`  
Контур: `C:\Users\007\Desktop\MLbotNav`

## 1. Закрыто по плану

1. Bybit ingest (day + incremental), watermark, idempotent upsert, DQ отчеты.
2. Minute-first gate (блок 30-дневных прогонов до явного подтверждения).
3. Unified ML pipeline: walk-forward, leakage checks, backtest with fee/slippage.
4. Registry: candidate/champion, promote guardrails, rollback guard + history.
5. Stage runtime: `D1 -> ... -> D90`, negative memory, stage state persistence.
6. TA contour: levels/patterns/signals/fallback, csv/parquet/xlsx artifacts.
7. Inference + paper trading контур в `prod_cycle`.
8. Packs: manifest/checksums/index csv+parquet + подписи.
9. Governance: retention + cold-storage archive, audit-chain.
10. RBAC enforcement и artifact signing в критичных шагах.
11. CV ingest integrity: sha256 + perceptual hash + dedup-policy.

## 2. Что улучшено в этом проходе

1. Расширен `M1`-блок фич в `dataset.py`:
   - momentum/indicator: `RSI`, `MACD`, `ADX`, `Stochastic`;
   - volume/flow: `delta_volume`, `OBV slope`, `MFI`;
   - structure/context: `level_strength`, `tp/sl distance`, `rr_context_estimate`;
   - pattern/divergence flags: `RSI/MACD/OBV` bullish/bearish divergences.
2. Исправлен `build_pack` для стабильного подхвата candidate-модели (`champion_candidate_*_...`).
3. Стабилизирована `logreg`-ветка: `max_iter=1200`.

## 3. Проверки

1. `python -m unittest discover -s tests -v` -> `OK` (17/17).
2. Smoke `pipeline_train_eval` на `1m` выполнен, отчет создан:
   - `reports/pipeline/pipeline_report_SOLUSDT_1m_20260521T103334Z.json`.
3. `search_gate_candidate` синхронизирован с полными gate-правилами pipeline
   (включая `trades_per_day_min/max`), отчет:
   - `reports/pipeline/search_gate_candidate_SOLUSDT_1m_20260521T103524Z.json`.
4. Итоговый minute-stage прогон с `gate.pass=true`:
   - `reports/pipeline/pipeline_report_SOLUSDT_1m_20260521T131603Z.json`.
5. Итоговая визуализация и summary minute-stage:
   - `reports/final_review/minute_final_entry_SOLUSDT_1m_20260521T131614Z.png`
   - `reports/final_review/minute_final_summary_SOLUSDT_1m_20260521T131614Z.json`
   - `reports/final_review/minute_final_summary_SOLUSDT_1m_20260521T131614Z.md`
6. Обновленный артефактный ранец:
   - `packs/2026-05-20/20260521T131621Z`.

## 4. Остаток по ТЗ (строго по процессу)

1. `1m gate PASS` получен; следующий обязательный шаг по процессу — пользовательское подтверждение minute-итога.
2. До явного подтверждения пользователя переход к 30-дневному прогону остается заблокирован.
3. После подтверждения выполняется разблокировка `allow_30d_window` и только затем 30-дневный прогон на `1m`.

## 5. Следующий шаг

Следующий шаг по плану: итерация настройки `1m`-порогов/параметров (через search/stage) до первого валидного `gate.pass` без ослабления risk-ограничений.
