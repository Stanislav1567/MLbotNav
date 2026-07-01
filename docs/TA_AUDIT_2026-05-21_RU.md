# TA Audit (2026-05-21)

Источник требований: `TECH_SPEC_ML_PLATFORM_RU.md` (блоки 5.8, 6.2, 6.4, 6.6).

## Что уже закрыто

1. Детект и запись уровней в `analytics.levels`.
2. Детект и запись паттернов в `analytics.pattern_events`.
3. Детект и запись сигналов в `analytics.signal_events`.
4. Строгий `NO_TRADE` с reason-code при непрохождении инвариантов.
5. Инварианты `TP>=1%` и `min_expected_move_pct` в сигнальном контуре.
6. Включение TA-шага в `prod_cycle`.

## Что добавлено в текущем расширении

1. Фигурные паттерны:
   - `double_top`, `double_bottom`, `triangle`, `wedge_falling`, `wedge_rising`, `range`.
2. Дивергенции:
   - `rsi_bull_divergence`, `rsi_bear_divergence`,
   - `macd_bull_divergence`, `obv_bull_divergence`.
3. Entry/Exit контекст:
   - выбор ближайших уровней `support/resistance`,
   - проверка `RR >= 1.0`,
   - отдельные reason-code: `sl_context_invalid`, `rr_below_1`, `tp_lt_1pct`, `expected_move_below_min`.

## Что еще не добито до полного соответствия TA-раздела ТЗ

1. Паттерн `head_and_shoulders` (и inverse H&S) как отдельный детектор.
2. Паттерны `flags/pennants` как отдельные классы (сейчас частично покрыты через wedge/triangle/range).
3. Расчет индикаторов `ADX/MFI/Stochastic` и их явная интеграция в TA signal confidence.
4. Формализованный `fallback`-режим с отдельным журналом решений (`indicator_fail -> structure_fallback -> NO_TRADE`).
5. Экспорт TA-отчетов в `parquet/xlsx` для полной части ранцев по ТЗ.

## План следующего шага (TA-next)

1. Добавить детекторы `head_and_shoulders`, `flag`, `pennant`.
2. Ввести ADX/MFI/Stochastic в скоринг сигнала и confidence.
3. Добавить fallback-log (`reports/technical_analysis/fallback_*.json`).
4. Подключить TA-артефакты в export-слой (`parquet/xlsx`) для ранца.

## TA Audit Update (2026-05-21, wave-2)
Closed now:
1. Added pattern detectors: `head_and_shoulders`, `inverse_head_and_shoulders`, `pennant` (plus existing triangle/wedges/range/double-top-bottom).
2. Added indicator context into signal logic: `ADX(14)`, `MFI(14)`, `Stochastic K/D`.
3. Added formal fallback log: `data/analytics/signal_fallback_events.csv`.
4. Added TA exports: parquet + xlsx artifacts.
5. Dedup fixed for fallback events by `symbol+timeframe+event_time_utc`.

Remaining TA hardening:
1. Threshold calibration profile per timeframe (config-driven, not hardcoded).
2. Pattern quality controls to reduce over-triggering density on long windows.
3. Add ta-unit tests for detectors and invariant checks.
