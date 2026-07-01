# Полный Пакет ТЗ (Сборка) 
Дата сборки: 2026-05-21



---
## Источник: C:\Users\007\Desktop\MLbotNav\TECH_SPEC_ML_PLATFORM_RU.md
---

# Техническое задание (ТЗ)
## Проект: AutoML/CV-платформа для анализа крипторынка и разметки графиков

- Версия: 1.0
- Дата: 2026-05-20
- Язык: RU
- Цель документа: зафиксировать архитектуру, требования и критерии приемки, чтобы система обучалась безопасно, обновлялась без деградации и имела отдельный контур для разметки графиков.

## 1) Цели и границы

### 1.1 Бизнес-цели
1. Прогнозировать рыночное движение (вероятность направления и/или доходность на горизонте N свечей).
2. Давать торговые сигналы и визуальную разметку графиков (вход/выход/паттерны/индикаторы).
3. Обеспечить автообучение и автообновление модели без неконтролируемой деградации.
4. Исключить загрязнение данных и ложные/мусорные артефакты в обучении и хранении.

### 1.2 Важное ограничение (честно)
Требование "каждая новая версия только лучше" в ML нельзя гарантировать математически на любом будущем рынке.
Вместо этого вводится правило non-degradation:
- новая модель может попасть в прод только через строгие ворота качества;
- при ухудшении по онлайн-метрикам происходит автoоткат к champion-модели.

### 1.3 In scope
1. Сбор, очистка и версионирование данных.
2. Обучение ML/DL-моделей, валидация, бэктест, paper trading.
3. Деплой модели и мониторинг drift/качества/латентности.
4. Отдельный CV-контур для работы со скриншотами графиков и рисованием.
5. Формирование "ранцев" (пакетов артефактов) по сделкам и сессиям.

### 1.4 Out of scope
1. Гарантия прибыли.
2. Высокочастотный трейдинг (HFT) на первом этапе.

## 2) Термины

1. Champion — текущая прод-модель.
2. Challenger — новая кандидат-модель.
3. Drift — статистическое смещение данных/распределений.
4. Leakage — утечка информации из будущего в обучение.
5. Ранец — неизменяемый пакет артефактов с хешами, метаданными и аудитом.

## 3) Целевая архитектура

Система разделяется на 3 независимых контура.

### 3.1 Контур A: TS-ML (time-series прогноз)
1. Ingestion Service: загрузка OHLCV, funding, OI, внешних факторов.
2. Data Quality Gate: схема, пропуски, дубликаты, свежесть, выбросы.
3. Feature Pipeline: признаки + таргеты без leakage.
4. Training Pipeline: baseline, boosting, нейросети.
5. Validation/Backtest: walk-forward + комиссии/slippage.
6. Registry: реестр моделей и артефактов.
7. Inference Service: онлайн-прогнозы и сигналы.
8. Monitoring & Alerts: drift, performance, latency, ошибки.

### 3.2 Контур B: CV/Chart Annotation (скриншоты и рисование)
1. Screenshot Ingestion: прием скриншотов с source-id.
2. Integrity Layer: hash + perceptual hash + dedup + malware-scan.
3. CV Analyzer: свечи/паттерны/фигуры/индикаторы/уровни.
4. Overlay Renderer: отрисовка линий, точек входа/выхода, комментариев.
5. Artifact Storage: сохранение исходника, разметки, масок, JSON-описания.

### 3.3 Контур C: Governance/Security
1. IAM/RBAC и least privilege.
2. KMS/секреты/шифрование в транзите и на диске.
3. Аудит действий и неизменяемые журналы.
4. Политики хранения/удаления/карантина.

## 4) Стек (рекомендованный)

1. Язык: Python 3.11+.
2. Data/ML: pandas, numpy, scikit-learn, lightgbm/xgboost, pytorch.
3. Тех. индикаторы: ta-lib или pandas-ta.
4. Оркестрация: Prefect (или Airflow).
5. Эксперименты/реестр: MLflow.
6. Версионирование данных: DVC.
7. Drift/качество: Evidently + Great Expectations.
8. Мониторинг: Prometheus + Grafana + Alertmanager.
9. Бэктест: backtrader/freqtrade-style симулятор с комиссиями/slippage.
10. Хранилище артефактов: S3-совместимое (MinIO/S3).
11. Отчеты: parquet + csv + xlsx.

## 5) Данные и контракты

### 5.1 Источники
1. Биржевые свечи OHLCV.
2. Funding rate, open interest.
3. Дополнительные маркеры риска (опционально DXY/VIX/индексы).

### 5.2 Data contract (обязателен)
1. Все timestamps в UTC.
2. Схема полей фиксирована и версионируется.
3. Допустимые диапазоны значений заданы явно.
4. Freshness SLA: новые свечи не старше C минут.

### 5.3 Политика качества данных
1. Пропуски выше порога -> batch в quarantine.
2. Дубликаты -> удаление + запись в audit log.
3. Аномалии -> маркировка, не автоудаление без журнала.
4. Любая очистка воспроизводима и версионируется.

### 5.4 Выгрузка данных из Bybit (обязательно)
1. Источник: `Bybit API v5` (`market/kline`), режим задается `market_type` (`spot`/`linear`).
2. Выгрузка выполняется дневными батчами в UTC: `[00:00:00, 23:59:59.999]`.
3. Таймфреймы выгрузки: `1m,5m,15m,30m,1h,4h,1d`.
4. Инструменты задаются конфигом `cfg_symbols`.
5. Идемпотентность обязательна: повторный запуск за тот же день не создает дублей (upsert).
6. Обязательные поля свечи:
   - `exchange, market_type, symbol, timeframe`;
   - `open_time_utc, close_time_utc`;
   - `open, high, low, close, volume, turnover`;
   - `ingest_run_id, source_ts_utc`.

### 5.5 База данных и структура хранения
1. Схемы БД: `raw`, `core`, `analytics`, `dq`, `meta`.
2. Таблица `raw.bybit_ohlcv` хранит сырые свечи.
3. Уникальный ключ дедупликации: `UNIQUE(exchange, market_type, symbol, timeframe, open_time_utc)`.
4. Поле партиции: `trade_date_utc`.
5. Таблица прогресса `meta.ingest_watermark`:
   - `exchange, market_type, symbol, timeframe`;
   - `last_loaded_open_time_utc, last_success_run_id, updated_at_utc`.
6. Таблица запусков `meta.ingest_run`:
   - `run_id, started_at_utc, ended_at_utc, status`;
   - `rows_read, rows_written, rows_upserted, rows_rejected, error_text`.
7. Для lake-хранилища (parquet) используется путь:
   - `/data/raw/bybit_ohlcv/dt=YYYY-MM-DD/tf=<timeframe>/symbol=<symbol>/part-*.parquet`.

### 5.6 Инкрементальная догрузка новых дней
1. Расписание:
   - каждые 5 минут для `1m` и `5m`;
   - каждые 15 минут для `15m` и `30m`;
   - каждый 1 час для `1h` и `4h`;
   - каждый 1 день для `1d`.
2. Логика догрузки:
   - `from_ts = watermark + timeframe_step`;
   - `to_ts = now_utc` округленный до закрытой свечи таймфрейма.
3. Незакрытые свечи не пишутся.
4. Политика late data: переобработка последних `N=3` дней.
5. Retry-политика: `max_retries=5`, экспоненциальный backoff и jitter.
6. При ошибке по одной паре `symbol+timeframe` остальные пары продолжают обработку; фиксируется `partial_success`.

### 5.7 Контроль полноты и качества Bybit-данных
1. Ожидаемое число свечей в дне:
   - `1m=1440, 5m=288, 15m=96, 30m=48, 1h=24, 4h=6, 1d=1`.
2. Порог полноты:
   - `completeness_pct >= 99.9%` для исторических дней;
   - `completeness_pct >= 99.0%` для текущего дня.
3. Валидность цены:
   - `low <= min(open, close)`;
   - `high >= max(open, close)`;
   - `high >= low`.
4. Валидность времени:
   - `close_time_utc > open_time_utc`;
   - шаг строго равен таймфрейму.
5. DQ-отчет обязателен в `dq.ohlcv_quality_report`:
   - `run_id, symbol, timeframe, trade_date_utc`;
   - `expected_rows, actual_rows, completeness_pct`;
   - `duplicate_rows, invalid_rows, gap_count, status, created_at_utc`.
6. Если `status=FAIL`, данные дня не переходят в `core`.

### 5.8 Визуализация и отчеты (тёмная тема)
1. Тема интерфейса по умолчанию: `dark`.
2. Контраст текста/осей: не ниже `WCAG AA`.
3. Слои графика (переключаемые):
   - свечи, объем, EMA/RSI/MACD;
   - уровни поддержки/сопротивления и тренд-линии;
   - паттерны и торговые сигналы.
4. Таблица уровней `analytics.levels`:
   - `level_id, symbol, timeframe, detected_at_utc`;
   - `level_price, level_type, strength_score, touches_count`;
   - `valid_from_utc, valid_to_utc, run_id`.
5. Таблица паттернов `analytics.pattern_events`:
   - `pattern_id, symbol, timeframe, pattern_type, direction`;
   - `start_time_utc, end_time_utc, confidence_score`;
   - `target_price, stop_price, invalidation_price, run_id`.
6. Таблица сигналов `analytics.signal_events`:
   - `signal_id, symbol, timeframe, signal_time_utc, side`;
   - `entry_price, stop_price, take_profit_price`;
   - `expected_move_pct, tp_reach_prob`;
   - `decision, reason_code, run_id`.
7. В “ранцы” за день сохраняются графики и метаданные:
   - `/data/reports/packs/dt=YYYY-MM-DD/symbol=.../tf=.../chart_*.png` и JSON.

## 6) Признаки, таргеты, модели

### 6.1 Таргет
1. Основной таргет: вероятность достижения целевого движения цены в сторону сделки до стоп-лосса.
2. Вариант классификации: `UP/DOWN` через `N` свечей с отдельным классом `NO_TRADE`.
3. Вариант регрессии: ожидаемое движение `return_N` через `N` свечей для расчета ожидаемого edge.
4. Для всех вариантов таргета обязательно хранить:
   - `expected_move_pct` (ожидаемый ход цены в процентах);
   - `tp_reach_prob` (вероятность достижения TP до SL);
   - `time_to_target` (ожидаемое время достижения цели).
5. Минимальный бизнес-порог на вход: прогнозируемый ход в сторону сделки должен покрывать комиссии/проскальзывание и иметь запас по expected value.

### 6.2 Признаки
1. Признаки формируются как библиотека гипотез (управляемый каталог), а не бесконтрольный набор индикаторов.
2. Блок `Price/Volatility`:
   - лаги доходности: `ret_1, ret_3, ret_6, ret_12, ret_24`;
   - волатильность: `rolling_std`, `ATR`, диапазон свечи.
3. Блок `Trend/Momentum`:
   - `EMA_20/50/200`, наклоны EMA;
   - `RSI`, `MACD`, `ADX`, стохастик.
4. Блок `Volume/Flow`:
   - `volume_zscore`, `delta_volume`, `OBV`, `MFI`.
5. Блок `Structure/TA (технический анализ)` обязателен и формализуется в признаки:
   - уровни: `support_distance`, `resistance_distance`, `level_strength` (количество и качество касаний);
   - структура рынка: `swing_high/low`, `BOS` (break of structure), `CHOCH` (change of character);
   - трендовые конструкции: расстояние до трендовой линии, угол/наклон тренда, положение внутри канала;
   - пробои: `breakout_flag`, `false_breakout_flag`, `retest_flag`;
   - справедливые зоны: `vwap_distance`, position-in-range, дневные/недельные high-low зоны;
   - расширения/коррекции: расстояния до ключевых уровней Фибоначчи в числовом виде.
6. Блок `Pattern (свечные и фигурные паттерны)` обязателен:
   - свечные паттерны: pin bar, engulfing, inside bar, doji, hammer/shooting star;
   - фигурные паттерны: double top/bottom, head and shoulders, triangles, flags/pennants, wedges, ranges;
   - дивергенции/контрдивергенции: RSI/MACD/OBV divergence flags;
   - каждый паттерн хранится как числовая фича: факт наличия, сила паттерна, направление, возраст паттерна.
7. Блок `Entry/Exit Context`:
   - расстояние до ближайшей цели по структуре (TP-контекст);
   - расстояние до защитного уровня (SL-контекст);
   - ожидаемое соотношение `RR` и ожидаемая длительность сделки.
8. Каждая группа признаков проходит ablation-тест (вклад в метрику и в риск), слабые группы удаляются.
9. Запрещено добавлять "все стратегии из интернета" без ограничений; новые гипотезы добавляются пакетами с фиксированным бюджетом экспериментов.
10. Решения по техническому анализу должны быть воспроизводимыми: запрещены неформализованные ручные правила "на глаз" внутри прод-контра.

### 6.3 Линейка моделей
1. Базовый контур (обязательный): `naive + rule-based + logistic`.
2. Основной контур: `LightGBM/XGBoost` как главный рабочий класс моделей для табличных признаков.
3. Расширенный контур: `LSTM/Temporal Transformer` только после доказанного прироста относительно основного контура.
4. Поисковый контур стратегий:
   - генерация кандидатов (индикаторы/паттерны/правила входа-выхода);
   - перебор параметров с ограниченным бюджетом;
   - фильтрация через risk-gates и negative memory.
5. В проде используется только один `active_model`; все остальные кандидаты остаются в офлайн/теневом режиме до подтверждения.

### 6.4 Fallback-правила (если индикаторы не дают edge)
1. Если индикаторный набор не проходит гейты качества, система переключается на структурный fallback:
   - support/resistance;
   - swing high/low;
   - breakout/false-breakout;
   - volume confirmation.
2. Если структурный fallback также не дает статистического edge, включается режим `NO_TRADE`.
3. При fallback запрещено ослаблять risk-gates и пороги комиссий ради увеличения числа сделок.
4. Решение fallback всегда логируется: причина, активированный набор правил, итог по метрикам.

### 6.5 Риск-блок против требования "100% уверенности"
1. Требование 100% точности/уверенности запрещено как некорректное для стохастического рынка.
2. Решение о входе принимается по вероятностной модели и ожидаемому значению сделки (`expected value`), а не по абсолютной уверенности.
3. Для каждой сделки обязательно:
   - оценка `tp_reach_prob`;
   - оценка `sl_hit_prob`;
   - расчет `R-multiple` и `expected value`.
4. Если доверие модели ниже порога или риск-профиль не проходит гейт, вход блокируется (`NO_TRADE`).
5. Любая попытка форсировать вход без прохождения risk-gate считается критическим нарушением.

### 6.6 Ограничения на частоту сделок и минимальный ожидаемый ход
1. Вводится диапазон частоты сделок на инструмент/таймфрейм:
   - `trades_per_day_min` — минимум для статистической значимости;
   - `trades_per_day_max` — максимум для ограничения комиссионной нагрузки.
2. Сделки вне диапазона (`< min` или `> max`) штрафуются в рейтинге и могут блокировать переход этапа.
3. Для каждой сделки обязательный порог `min_expected_move_pct`:
   - ожидаемый ход цены в сторону сделки должен быть не ниже заданного минимума;
   - минимум должен быть выше совокупных издержек (`fee + slippage`) с буфером.
4. Если `expected_move_pct < min_expected_move_pct`, вход запрещен (`NO_TRADE`).
5. Для длинного TP допускается трейлинг/перенос цели только по формализованным правилам структуры, без ручного "дотягивания" постфактум.

### 6.7 Критерии приемки раздела 6
1. Для каждого run подтверждено, что признаки формируются из утвержденной библиотеки гипотез; хаотичные ad-hoc признаки отсутствуют.
2. Fallback-логика отрабатывает детерминированно:
   - индикаторный контур fail -> структурный контур;
   - структурный контур fail -> `NO_TRADE`.
3. В логах 100% сделок есть `expected_move_pct`, `tp_reach_prob`, `sl_hit_prob`, `EV`.
4. В логах 100% отказов есть явная причина (`no_edge`, `risk_gate_fail`, `min_move_fail`, `freq_limit`).
5. Не менее 95% сделок удовлетворяют `expected_move_pct >= min_expected_move_pct` до открытия позиции; оставшиеся <=5% допустимы только как технические исключения с аудитом.
6. Доля сделок, открытых с нарушением частотных лимитов, должна быть 0%.
7. Попытка требования "100% уверенности" не изменяет risk-policy и фиксируется как отклоненная бизнес-ограничением.
8. Для каждого run присутствуют рассчитанные признаки блока `Structure/TA` и `Pattern`; отсутствие любого обязательного подблока = fail этапа.

## 7) Обучение и анти-деградация

### 7.1 Последовательность
1. Baseline -> Core ML -> DL -> Ensemble.
2. Каждая следующая ступень только после успешной приемки предыдущей.

### 7.2 Champion/Challenger
1. Challenger обучается на том же окне и тех же издержках.
2. Публикация в прод только через gate.
3. При нарушении KPI онлайн -> rollback <= 5 минут.

### 7.3 Deployment Gates (обязательные)
1. Data Quality: pass.
2. Leakage tests: pass.
3. Walk-forward: pass.
4. Backtest с fee/slippage: pass.
5. Latency/SLA: pass.
6. Security scan: pass.

### 7.4 Автообучение
1. Schedule retrain: например 1 раз/сутки.
2. Event retrain: при drift/деградации метрик.
3. Если gate не пройден — релиз блокируется, champion остается активным.

## 8) Валидация и бэктест

1. Только time-series split и walk-forward.
2. Запрещен random shuffle для временных рядов.
3. Обязательный учет комиссий и проскальзывания.
4. Отдельные стресс-тесты для волатильных периодов.

Метрики:
1. ML: AUC/F1 (для классификации), MAE/RMSE (для регрессии).
2. Trading: Sharpe, Sortino, Max Drawdown, CAGR, hit-rate.

## 9) Контур CV/рисования на графиках

### 9.1 Требования
1. Отдельный сервис и отдельное хранилище от торгового движка.
2. Поддержка свечей, паттернов, фигур, индикаторов и пользовательских аннотаций.
3. Возможность команды: "нарисуй входы/выходы" с сохранением результата.

### 9.2 Анти-"подмешивание"
1. Каждый скриншот: source-id, timestamp, sha256, perceptual hash.
2. Dedup политика: похожие скрины выше порога -> merge/skip по правилам.
3. Нельзя подменять исходный скрин отрисованной копией без явной версии.
4. Хранить: original, overlay, metadata.json, decision.json.

## 10) Ранцы (пакеты артефактов)

### 10.1 Состав ранца
1. Скриншоты (исходные и разметка).
2. Сделки и сигналы.
3. Индикаторы и промежуточные расчеты.
4. Отчеты CSV/XLSX/Parquet.
5. Model snapshot (id версии), config, run_id.
6. Audit log + checksums.

### 10.2 Формат и хранение
1. Папка/объект вида: `packs/YYYY-MM-DD/session_id/`.
2. Индекс ранцев в каталоге `packs/index.parquet`.
3. Retention policy + архив + cold storage.

## 11) Безопасность

1. RBAC: роли Data Engineer / ML Engineer / Reviewer / Admin.
2. Шифрование TLS 1.2+ и at-rest encryption.
3. Секреты только через vault/KMS.
4. Подпись релизных артефактов.
5. Полный аудит: кто/когда/что изменил.
6. Защита от data poisoning и невалидных источников.

## 12) Нефункциональные требования

1. Доступность инференса: >= 99.5%.
2. P95 latency прогноза: <= 300 мс (без CV-рендера).
3. RTO: <= 30 минут, RPO: <= 5 минут.
4. Воспроизводимость: любой результат по run_id восстанавливается полностью.

## 13) Структура репозитория

```text
crypto-ml-platform/
  data/
    raw/
    interim/
    features/
    quarantine/
  packs/
  models/
  reports/
  logs/
  configs/
    config.yaml
    thresholds.yaml
  src/
    ingestion/
    quality/
    features/
    training/
    validation/
    backtest/
    inference/
    cv/
    governance/
    monitoring/
  tests/
    unit/
    integration/
    e2e/
  notebooks/
  requirements.txt
  README.md
```

## 14) Поэтапный план внедрения (roadmap)

### Этап 0 (1 неделя): фундамент
1. Репозиторий, структура, CI, базовые тесты.
2. Сбор OHLCV, UTC, data contracts.
3. Базовая очистка + quarantine.

### Этап 1 (2 недели): baseline + core ML
1. Baseline и LightGBM.
2. Walk-forward + бэктест с fee/slippage.
3. MLflow + DVC.

### Этап 2 (2 недели): прод-контур
1. Inference сервис.
2. Champion/challenger + gates + rollback.
3. Drift + алерты + дашборды.

### Этап 3 (2 недели): CV-контур
1. Ingestion скриншотов + integrity checks.
2. Отрисовка индикаторов/входов/выходов.
3. Ранцы и экспорт в XLSX.

### Этап 4 (1-2 недели): hardening
1. Нагрузочное тестирование.
2. Security review.
3. Runbook инцидентов и SOP.

## 15) Критерии приемки (Acceptance Criteria)

1. Challenger допускается в прод только при улучшении целевой метрики >= X% и без ухудшения MDD > Y%.
2. Автооткат выполняется <= 5 минут при нарушении порогов PnL/latency/error.
3. 100% прохождение quality/leakage/backtest/security gate.
4. Drift-алерт приходит <= 2 минут после нарушения порога.
5. Любой прод-результат воспроизводится по run_id.
6. Для каждого входного скриншота есть source-id + hash + timestamp + версия пайплайна.
7. Для каждой сессии формируется ранец с графиками, сделками, отчетом и audit-log.
8. Полная историческая выгрузка Bybit за 30 дней по всем заданным таймфреймам проходит без дублей (`duplicate_rows=0`).
9. Для каждой связки `symbol + timeframe + day` сформирован `dq.ohlcv_quality_report`.
10. Инкрементальная догрузка обновляет только новые свечи и не перезаписывает полностью уже подтвержденные исторические дни.
11. Dark UI отображает свечи, объем, индикаторы, уровни, паттерны и сигналы с переключаемыми слоями.

## 16) Минимальный стартовый конфиг (пример)

```yaml
project:
  symbol: BTC/USDT
  timeframe: 1h
  horizon_bars: 24

data_ingest:
  source: bybit_v5
  market_type: linear
  symbols: ["BTCUSDT", "ETHUSDT"]
  timeframes: ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
  day_batch_utc: true
  late_data_reconcile_days: 3
  retry_max: 5

thresholds:
  max_missing_ratio: 0.02
  max_duplicate_ratio: 0.001
  min_auc: 0.55
  max_mdd_degradation: 0.05
  max_p95_latency_ms: 300
  rollback_error_rate: 0.03
  min_expected_move_pct: 1.0
  min_tp_reach_prob: 0.58
  trades_per_day_min: 3
  trades_per_day_max: 40
  max_no_trade_ratio: 0.70

retrain:
  schedule_cron: "0 3 * * *"
  enable_drift_trigger: true

backtest:
  fee_bps: 10
  slippage_bps: 5

ui:
  theme: dark
  min_contrast_standard: WCAG_AA
  overlays: ["candles", "volume", "ema", "rsi", "macd", "sr_levels", "trend_lines", "patterns", "signals"]
```

## 17) Риски и контроль

1. Переобучение -> регуляризация, walk-forward, out-of-time test.
2. Leakage -> строгий feature pipeline и тесты на утечку.
3. Data poisoning/мусор -> источники по allowlist, quarantine, audit.
4. Ложные сигналы CV -> ручной reviewer-loop на ранних этапах.

## 18) Что делать сразу (чеклист на старт)

1. Утвердить символы, таймфрейм, горизонт N.
2. Утвердить пороги gate и rollback.
3. Поднять каркас репозитория и quality gate.
4. Собрать baseline + LightGBM + walk-forward + бэктест.
5. Включить MLflow/DVC/мониторинг.
6. После этого подключать нейросети и CV-контур.

---

## Примечание
Документ проектирует надежный процесс, а не "магическую модель". Ключ к качеству: дисциплина данных, честная валидация и жесткие релизные ворота.

## 19) Спецраздел: Одна модель, поэтапное обучение по дням (D1 -> D90)

### 19.1 Цель раздела
1. Обучать одну модель последовательно, от короткого участка к длинному.
2. Минимизировать вычислительную нагрузку на старте (поиск на D1), затем наращивать горизонт.
3. Исключить повтор нерабочих действий через `negative memory`.
4. Разрешать сделку только при достижимом целевом ходе цены и валидных риск-правилах.

### 19.2 Порядок этапов
1. `D1` (Day-1 exhaustive): полный перебор стратегий/параметров на 1 дне (`M1` и/или `M5`).
2. `D2`: перенос лучших конфигов на 2-й день без изменения логики.
3. `D3`: проверка устойчивости на 3 днях подряд.
4. `D5`: подтверждение устойчивости на 5 днях подряд.
5. `D30 -> D60 -> D90`: масштабирование на длинные окна с walk-forward.

### 19.3 Инварианты
1. В проде активна только одна версия (`active_model`).
2. В проде модель не дообучается на лету.
3. Плохие конфиги не удаляются, а попадают в `negative memory`.
4. Если валидного сигнала нет, система обязана выбрать `NO_TRADE`.

### 19.4 Торговые правила для этапов
1. Для любой сделки обязателен `SL`.
2. Минимальная целевая дистанция `TP >= 1.0%` (без плеча).
3. `Dynamic TP`: тейк-профит ставится по ближайшей сильной структуре (S/R, swing high/low), если дистанция >= 1.0%.
4. Если структурный TP < 1.0%, сделка запрещена (`NO_TRADE`).
5. Разрешен трейлинг TP при движении в сторону сделки и подтвержденной структуре.

### 19.5 Rating/Scoring (0..100)
`R = 0.35*ReturnScore + 0.25*SharpeScore + 0.20*DrawdownScore + 0.10*StabilityScore + 0.10*ExecutionScore`

1. `ReturnScore`: доходность после fee/slippage.
2. `SharpeScore`: риск-скорректированная доходность.
3. `DrawdownScore`: штраф за max drawdown.
4. `StabilityScore`: стабильность по дням/окнам.
5. `ExecutionScore`: корректность исполнения правил (`SL/TP/NO_TRADE`, latency, отсутствие rule_break).

### 19.6 Negative Memory (анти-повтор плохих действий)
1. Проваленный конфиг получает fingerprint: хеш параметров + рыночный контекст.
2. Повтор fingerprint в рамках cooldown запрещен.
3. Причины провала фиксируются: `overfit`, `high_dd`, `tp_lt_1pct`, `unstable`, `rule_break`.
4. Генератор новых гипотез обязан учитывать blacklist и штрафовать похожие зоны параметров.

### 19.7 Stage Gates (критерии перехода)
1. `D1 -> D2`: `R >= 60`, `MaxDD <= 8%`, >=20 валидных сделок, 0 критических нарушений.
2. `D2 -> D3`: `R >= 65`, просадка не хуже D1 более чем на 2 п.п.
3. `D3 -> D5`: `R >= 70`, положительный net PnL на каждом дне.
4. `D5 -> D30`: `R >= 72`, стабильность >= 0.60.
5. `D30 -> D60`: `R >= 75`, `MaxDD <= 12%`, доля `NO_TRADE` обоснована и <=70%.
6. `D60 -> D90`: `R >= 78`, без критической регрессии по Sharpe/MaxDD.
7. `D90 -> Ready`: `R >= 80`, устойчивый walk-forward, воспроизводимость 100% по `run_id`.

### 19.8 Acceptance Criteria раздела
1. Stage D1 покрывает 100% заданного конечного пространства конфигов.
2. В логах каждой сделки фиксируется `TP distance` и причина выбора TP.
3. Сделка без валидного `SL` или без обоснованного `TP` считается критической ошибкой этапа.
4. Повтор проваленных fingerprint в рамках cooldown = 0%.
5. Доля необъяснимых `NO_TRADE` = 0%.
6. Все метрики считаются только после учета комиссий и проскальзывания.
7. Переход этапа невозможен при непрохождении любого gate-пункта.

### 19.9 Псевдокод цикла
```python
stage_plan = ["D1", "D2", "D3", "D5", "D30", "D60", "D90"]
active_model = None
negative_memory = load_negative_memory()

for stage in stage_plan:
    data = quality_gate(load_stage_data(stage))
    candidates = generate_candidates(stage, exclude=negative_memory)

    results = []
    for cfg in candidates:
        bt = backtest(
            config=cfg,
            data=data,
            fees=True,
            slippage=True,
            min_tp_pct=0.01,
            dynamic_tp_by_structure=True,
            allow_no_trade=True,
        )

        if bt.rule_violations > 0:
            negative_memory.add(cfg, reason="rule_break")
            continue

        score = compute_rating(bt)
        if not pass_risk_gates(bt, score, stage):
            negative_memory.add(cfg, reason=bt.fail_reason)
            continue

        results.append((cfg, bt, score))

    if not results:
        raise StageFail(stage, "no_valid_candidate")

    best = select_best(results)
    if pass_stage_transition(best, stage):
        active_model = best.config
        save_stage_artifacts(stage, best, negative_memory)
    else:
        negative_memory.add(best.config, reason="transition_fail")
        raise StageFail(stage, "gate_not_passed")

finalize(active_model)
```

## 20) Режим прод-эксплуатации для одной модели

1. В проде работает только `active_model`.
2. Переобучение выполняется в фоне, но без изменения активной модели до завершения полного цикла проверки.
3. Переключение версии допускается только после успешного прохождения этапов до `D90 -> Ready`.
4. Обязателен rollback на последнюю стабильную версию по команде или по аварийному правилу.

## 21) SQL DDL (таблицы ingest и DQ)

```sql
-- Требуется PostgreSQL 13+ (желательно 14+)
-- Расширение для UUID
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS dq;
CREATE SCHEMA IF NOT EXISTS meta;

-- 1) Сырые свечи Bybit
CREATE TABLE IF NOT EXISTS raw.bybit_ohlcv (
    id BIGSERIAL PRIMARY KEY,
    exchange TEXT NOT NULL,
    market_type TEXT NOT NULL CHECK (market_type IN ('spot', 'linear')),
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL CHECK (timeframe IN ('1m', '5m', '15m', '30m', '1h', '4h', '1d')),
    trade_date_utc DATE NOT NULL,
    open_time_utc TIMESTAMPTZ NOT NULL,
    close_time_utc TIMESTAMPTZ NOT NULL,
    open NUMERIC(20,10) NOT NULL CHECK (open > 0),
    high NUMERIC(20,10) NOT NULL CHECK (high > 0),
    low NUMERIC(20,10) NOT NULL CHECK (low > 0),
    close NUMERIC(20,10) NOT NULL CHECK (close > 0),
    volume NUMERIC(30,10) NOT NULL CHECK (volume >= 0),
    turnover NUMERIC(30,10) CHECK (turnover >= 0),
    ingest_run_id UUID NOT NULL,
    source_ts_utc TIMESTAMPTZ NOT NULL,
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (high >= low),
    CHECK (low <= LEAST(open, close)),
    CHECK (high >= GREATEST(open, close)),
    CHECK (close_time_utc > open_time_utc),
    UNIQUE (exchange, market_type, symbol, timeframe, open_time_utc)
);

CREATE INDEX IF NOT EXISTS idx_bybit_ohlcv_symbol_tf_time
    ON raw.bybit_ohlcv (symbol, timeframe, open_time_utc);

CREATE INDEX IF NOT EXISTS idx_bybit_ohlcv_trade_date
    ON raw.bybit_ohlcv (trade_date_utc);

-- 2) Лог запусков ingestion
CREATE TABLE IF NOT EXISTS meta.ingest_run (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at_utc TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'partial_success', 'failed')),
    rows_read BIGINT NOT NULL DEFAULT 0,
    rows_written BIGINT NOT NULL DEFAULT 0,
    rows_upserted BIGINT NOT NULL DEFAULT 0,
    rows_rejected BIGINT NOT NULL DEFAULT 0,
    error_text TEXT
);

-- 3) Watermark по каждой связке exchange+market_type+symbol+timeframe
CREATE TABLE IF NOT EXISTS meta.ingest_watermark (
    exchange TEXT NOT NULL,
    market_type TEXT NOT NULL CHECK (market_type IN ('spot', 'linear')),
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL CHECK (timeframe IN ('1m', '5m', '15m', '30m', '1h', '4h', '1d')),
    last_loaded_open_time_utc TIMESTAMPTZ NOT NULL,
    last_success_run_id UUID,
    updated_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (exchange, market_type, symbol, timeframe),
    FOREIGN KEY (last_success_run_id) REFERENCES meta.ingest_run (run_id)
);

-- 4) DQ-отчет по свечам
CREATE TABLE IF NOT EXISTS dq.ohlcv_quality_report (
    report_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL CHECK (timeframe IN ('1m', '5m', '15m', '30m', '1h', '4h', '1d')),
    trade_date_utc DATE NOT NULL,
    expected_rows INTEGER NOT NULL CHECK (expected_rows >= 0),
    actual_rows INTEGER NOT NULL CHECK (actual_rows >= 0),
    completeness_pct NUMERIC(6,3) NOT NULL CHECK (completeness_pct >= 0 AND completeness_pct <= 100),
    duplicate_rows INTEGER NOT NULL DEFAULT 0 CHECK (duplicate_rows >= 0),
    invalid_rows INTEGER NOT NULL DEFAULT 0 CHECK (invalid_rows >= 0),
    gap_count INTEGER NOT NULL DEFAULT 0 CHECK (gap_count >= 0),
    status TEXT NOT NULL CHECK (status IN ('PASS', 'WARN', 'FAIL')),
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, symbol, timeframe, trade_date_utc),
    FOREIGN KEY (run_id) REFERENCES meta.ingest_run (run_id)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_quality_symbol_tf_date
    ON dq.ohlcv_quality_report (symbol, timeframe, trade_date_utc);

-- 5) События пропусков свечей
CREATE TABLE IF NOT EXISTS dq.gap_events (
    gap_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL CHECK (timeframe IN ('1m', '5m', '15m', '30m', '1h', '4h', '1d')),
    trade_date_utc DATE NOT NULL,
    missing_open_time_utc TIMESTAMPTZ NOT NULL,
    expected_step_seconds INTEGER NOT NULL CHECK (expected_step_seconds > 0),
    created_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (run_id) REFERENCES meta.ingest_run (run_id)
);

CREATE INDEX IF NOT EXISTS idx_gap_events_symbol_tf_time
    ON dq.gap_events (symbol, timeframe, missing_open_time_utc);
```

---
## Источник: C:\Users\007\Desktop\MLbotNav\docs\TZ_GAP_AUDIT_2026-05-21_RU.md
---

# ТЗ Аудит: Что Не Готово До Полностью Рабочей Модели

Дата: 2026-05-21
Проект: `C:\Users\007\Desktop\MLbotNav`
Источник требований: `TECH_SPEC_ML_PLATFORM_RU.md` (v1.0)

## 1) Блокеры до режима "модель полностью готова"

1. Не реализованы обязательные источники данных кроме OHLCV.
Требование ТЗ: funding rate, open interest, внешние маркеры риска.
Факт: в коде нет ingest-модулей/контрактов для funding/OI/макро-маркеров.

2. Нет полноценного security-контура KMS/Vault/TLS-at-rest.
Требование ТЗ: секреты только через vault/KMS, шифрование в транзите и на диске.
Факт: секреты берутся из `.env`/`SOURCE_ENV_PATH`; signing есть, но KMS/Vault/TLS policy-runtime нет.

3. Нет формализованного malware-scan в CV-контуре.
Требование ТЗ (контур CV): hash + perceptual hash + dedup + malware-scan.
Факт: есть sha256/phash/dedup, malware scan отсутствует.

4. CV Analyzer не завершен до полного состава артефактов.
Требование ТЗ: хранить original/overlay/masks/metadata/decision.
Факт: есть original/overlay/metadata/decision, но `mask` артефакты не формируются.

5. Нет production-расписания retrain/event-trigger.
Требование ТЗ: schedule retrain (например, 1/сутки) + event retrain при drift.
Факт: есть CLI и `prod_cycle`, но нет планировщика/автотриггера retrain.

6. Drift alert <= 2 минут не гарантирован.
Требование ТЗ: дрейф-алерт не позднее 2 минут после нарушения порога.
Факт: alert создается при запуске `monitor_drift`, но SLA доставки/trigger <=2 мин не зафиксирован.

7. SQL DDL слой не внедрен в runtime.
Требование ТЗ (раздел 21): схемы raw/core/analytics/dq/meta в PostgreSQL.
Факт: текущая реализация на CSV/Parquet; DB-слой отсутствует.

8. Неполный набор обязательных торговых полей.
Требование ТЗ: хранить `expected_move_pct`, `tp_reach_prob`, `time_to_target`.
Факт: первые два есть, `time_to_target` отсутствует в backtest/pipeline/inference логах.

9. Неполный набор trading-метрик.
Требование ТЗ: Sharpe, Sortino, Max Drawdown, CAGR, hit-rate.
Факт: есть sharpe_like/hit_rate/MDD, но нет Sortino/CAGR.

10. Нефункциональные SLA (availability 99.5%, inference p95 <=300ms) не закрыты как системные KPI.
Требование ТЗ: измеримые SLA прод-инференса.
Факт: есть `monitor_sla` по шагам цикла, но нет API-сервиса инференса и uptime/latency контура как сервиса.

## 2) Что уже готово и не является блокером

1. Bybit OHLCV ingest day/incremental, watermark, idempotency, late-data reconcile.
2. DQ + quarantine + partial_success + retry/backoff/jitter.
3. Feature pipeline, walk-forward, leakage checks, backtest fee/slippage.
4. Registry, champion/challenger, rollback guard, negative memory, stage ladder.
5. TA контур, inference/paper trading, packs/signatures/audit-chain, CPU budget.
6. Minute-first gate и зафиксированный minute итог.

## 3) Управленческая фиксация

До закрытия блокеров из раздела 1 проект не считается "полностью рабочей моделью" по ТЗ.
Рекомендуемый процесс: инженерные доработки -> повторный audit -> только затем полноценные обучающие прогоны как основной этап.

## Update 2026-05-21 (later)

Блокер по п.1 (funding + open interest ingestion) закрыт:
1. Добавлены `ingest_context_day` и `ingest_context_incremental` (Bybit v5, UTC day-batch/incremental).
2. Добавлены контракты и DQ для market context (`context_contract`, `context_dq`).
3. Добавлены артефакты DQ/meta для контекста:
   - `data/dq/market_context_quality_report.csv`
   - watermark/run журналы в `data/meta`.
4. Приемочный smoke по `SOLUSDT` за `2026-05-20` успешен.

## Update 2026-05-21 (P2 start)

Блокер по SQL runtime (п.7) переведен в статус `IN PROGRESS`:
1. Добавлен PostgreSQL DDL runtime файл: `sql/postgres_storage_runtime.sql`.
2. Добавлен runtime adapter `file|postgres`: `src/mlbotnav/postgres_runtime.py`.
3. `meta_store`/`storage_registry` и ingest контуры поддерживают переключение backend через `STORAGE_MODE`.
4. Финальная приемка п.7 будет закрыта после smoke на окружении с `POSTGRES_DSN`:
   - `python -m mlbotnav.postgres_runtime --ensure-schema --smoke`.

## Update 2026-05-21 (P3 start)

Блокеры по CV hardening (п.3 и п.4) переведены в статус `IN PROGRESS`:
1. В `cv_ingest` добавлен policy-driven malware hook:
   - scanner status (`clean/suspicious/disabled`);
   - mode (`block|quarantine|report`) из `configs/security_governance.yaml`;
   - quarantine path: `data/quarantine/cv/...`;
   - suspicious inputs не допускаются в рабочий CV контур (`allowed_for_cv=false`).
2. В `cv_overlay_pipeline` добавлен `mask` artifact:
   - `*_mask.png` рядом с `original/overlay/metadata/decision`.
3. Metadata/decision расширены полями `mask_file`, `scanner_status`, `pipeline_version`.

## Update 2026-05-21 (P4 start)

Блокер по security hardening (п.2) переведен в `IN PROGRESS`:
1. Добавлен provider-слой секретов (`env|vault|kms`) в `src/mlbotnav/security.py`.
2. Добавлен `security gate` с отчетом `reports/security/security_gate_<stage>_*.json`.
3. `model_registry.promote_if_pass` теперь блокирует promote при `security_gate_fail`.
4. Добавлен CLI-check:
   - `python -m mlbotnav.security --stage promote`.
5. Обновлены конфиги:
   - `configs/security_governance.yaml` (`security.provider`, `security.gate`, `security.cv_scan`).

## Update 2026-05-21 (P5 start)

Блокеры по automation/SLA (п.5 и п.6) переведены в `IN PROGRESS`:
1. Добавлен event-trigger модуль:
   - `src/mlbotnav/drift_retrain_trigger.py`
   - формирует `reports/monitoring/retrain_trigger_*.json` и поле `alert_to_trigger_sec`.
2. `prod_cycle` расширен шагом `drift_retrain_trigger`.
3. Добавлен scheduler runner:
   - `src/mlbotnav/scheduler_runner.py`
   - поддерживает циклы `ingest_incremental|prod_cycle|drift_trigger|all`.
4. `monitor_sla` учитывает breach по drift-trigger SLA.

## Update 2026-05-21 (P6 start)

Блокеры по metric completeness (п.8 и п.9) переведены в `IN PROGRESS`:
1. В backtest добавлены:
   - `time_to_target_bars`, `time_to_target_sec`;
   - summary metrics `sortino`, `cagr`, `time_to_target_*_avg`.
2. В inference events/report добавлен `time_to_target_bars` (оценка по horizon).
3. Gate-логика расширена проверками `min_sortino`, `min_cagr` (в `configs/thresholds.yaml`).

---
## Источник: C:\Users\007\Desktop\MLbotNav\docs\TZ_STRICT_REMAINING_PLAN_2026-05-21_RU.md
---

# Строгий План Доделок По ТЗ (До Полностью Рабочей Модели)

Дата: 2026-05-21
Режим: сначала закрываем инженерные gap, затем выходим на обучение как этап эксплуатации.

## Фаза 0. Freeze и контроль процесса (P0)

1. Ввести кодовый флаг готовности проекта (`project_ready=false`) и блокировать train/retrain/prod-cycle heavy runs, пока не завершены критические пункты.
2. Разрешить только audit/ingest/validation dry-run до статуса ready.
3. Добавить отчет `reports/readiness/readiness_check_*.json`.

Критерий приемки:
1. Любой запуск обучения при `project_ready=false` завершаетcя с явной причиной блокировки.
2. Readiness-отчет показывает checklist по блокерам.

## Фаза 1. Data-source expansion (P1)

1. Добавить ingestion funding rate и open interest (Bybit v5), с UTC, day-batch и incremental.
2. Добавить контракты данных и DQ для funding/OI.
3. Добавить хранение в `raw/core/meta` и связать с текущим watermark/run журналом.

Критерий приемки:
1. По каждой дате есть записи OHLCV + funding + OI без дублей.
2. DQ отчеты формируются для всех источников.

## Фаза 2. Storage/DDL runtime (P2)

1. Реализовать опциональный PostgreSQL storage adapter по разделу 21 (raw/meta/dq).
2. Сохранить совместимость с текущим файловым контуром (режим `file`/`postgres`).
3. Добавить миграционный скрипт и smoke-проверку консистентности.

Критерий приемки:
1. Один и тот же ingest run корректно пишется в выбранный backend.
2. Уникальные ключи и upsert работают по ТЗ.

## Фаза 3. CV hardening (P3)

1. Добавить malware-scan hook в `cv_ingest` (policy-driven: block/quarantine).
2. Добавить генерацию mask-артефактов в `cv_overlay_pipeline`.
3. Расширить metadata/decision схему под masks + scanner status.

Критерий приемки:
1. На каждый CV run есть `original + overlay + mask + metadata + decision`.
2. infected/invalid файлы не проходят в рабочий CV контур.

## Фаза 4. Security hardening (P4)

1. Вынести секреты в provider-слой (`env|vault|kms`) с обязательной политикой выбора.
2. Добавить конфиг-политику TLS/at-rest encryption checks и аудит нарушений.
3. Интегрировать security-gate в release-пайплайн (до promote).

Критерий приемки:
1. Promote блокируется при security-gate fail.
2. В audit есть след policy check и источник секрета.

## Фаза 5. Monitoring/automation (P5)

1. Добавить планировщик (cron/heartbeat runner) для ingest + retrain.
2. Добавить event-trigger retrain от drift alert.
3. Зафиксировать SLA доставки drift-alert <= 2 минут и проверить на smoke.

Критерий приемки:
1. Есть автоматический цикл без ручного старта.
2. Drift breach приводит к alert и retrain-trigger в пределах SLA.

## Фаза 6. Metric completeness (P6)

1. Добавить `time_to_target` в backtest/pipeline/inference logs.
2. Добавить Sortino и CAGR в торговые отчеты.
3. Обновить gate-правила под полный набор метрик ТЗ.

Критерий приемки:
1. 100% сделок/решений содержат обязательные поля ТЗ.
2. Отчеты содержат полный набор ML + Trading метрик.

## Фаза 7. Final readiness audit (P7)

1. Повторный полный audit по ТЗ с чеклистом acceptance criteria.
2. Подтверждение `project_ready=true`.
3. Только после этого запуск полноценного цикла обучения/дообучения.

Критерий приемки:
1. Все пункты из `docs/TZ_GAP_AUDIT_2026-05-21_RU.md` закрыты.
2. Есть финальный отчет `reports/readiness/final_tz_readiness_*.json`.

## Порядок выполнения (строго)

1. P0
2. P1
3. P2
4. P3
5. P4
6. P5
7. P6
8. P7

Переход к следующей фазе допускается только после фиксации артефакта приемки текущей фазы.

## Фиксация Прогресса (2026-05-21)

1. `P0` закрыт:
   - readiness freeze активен;
   - train/prod heavy actions блокируются при `project_ready=false`;
   - readiness reports пишутся в `reports/readiness/readiness_check_*.json`.

2. `P1` закрыт:
   - добавлены `funding + open_interest` ingest контуры:
     - `src/mlbotnav/ingest_context_day.py`
     - `src/mlbotnav/ingest_context_incremental.py`
   - добавлены контракты/DQ:
     - `src/mlbotnav/context_contract.py`
     - `src/mlbotnav/context_dq.py`
   - подключен meta/dq storage:
     - `data/dq/market_context_quality_report.csv`
     - `data/meta/ingest_watermark.csv`
     - `data/meta/ingest_run.csv`
   - приемочный smoke:
     - day run `2026-05-20` по `SOLUSDT` успешен;
     - incremental report: `reports/ingestion/context_incremental_SOLUSDT_20260521T134625Z.json`.
   - источник Bybit для OI интервала `1m` возвращает пусто; интервал помечается как `skipped`, рабочие OI интервалы: `5,15,30,60,240,D`.

3. `P2` в работе (engineering implementation completed, acceptance pending):
   - добавлен runtime-адаптер `file|postgres`:
     - `src/mlbotnav/postgres_runtime.py`
     - `sql/postgres_storage_runtime.sql`
   - `meta_store` и `storage_registry` переключаются по `STORAGE_MODE`.
   - ingest контуры (`ingest_day`, `ingest_context_day`) пишут upsert в `raw.*` при режиме `postgres`.
   - добавлен CLI smoke/migrate:
     - `python -m mlbotnav.postgres_runtime --ensure-schema --smoke`
   - acceptance `P2` будет закрыт после реального smoke на окружении с валидным `POSTGRES_DSN`.

4. `P3` в работе:
   - добавлен malware-scan hook в `src/mlbotnav/cv_ingest.py`:
     - policy `block|quarantine|report`;
     - scanner fields в metadata/index/audit;
     - suspicious файлы не проходят в рабочий CV-контур.
   - добавлен mask-слой в `src/mlbotnav/cv_overlay_pipeline.py`:
     - формируются `original + overlay + mask + metadata + decision`.
   - конфиг сканера вынесен в `configs/security_governance.yaml` (`security.cv_scan`).

5. `P4` в работе:
   - добавлен provider-слой секретов `env|vault|kms` (`src/mlbotnav/security.py`);
   - добавлен `security gate` с артефактами `reports/security/security_gate_<stage>_*.json`;
   - promote в `model_registry` теперь блокируется при `security_gate_fail`.

6. `P5` в работе:
   - добавлен `drift_retrain_trigger` с SLA-полем `alert_to_trigger_sec`;
   - `prod_cycle` запускает trigger шаг после drift-monitor;
   - добавлен `scheduler_runner` для циклических автоматизированных запусков;
   - `monitor_sla` учитывает breach по drift-trigger SLA.

7. `P6` в работе:
   - в backtest добавлены `time_to_target_*`, `sortino`, `cagr`;
   - inference-report дополнен `time_to_target_bars`;
   - gate thresholds дополнены `min_sortino`, `min_cagr`.

---
## Источник: C:\Users\007\Desktop\MLbotNav\docs\TZ_5PLUS_MASTER_CHECKLIST_RU.md
---

# MLbotNav: Master-Checklist "5+" по ТЗ

Дата фиксации: 2026-05-21  
Источник истины: `TECH_SPEC_ML_PLATFORM_RU.md`

## Блок F (Фундамент до обучения/тестов)

1. `F1` Единый статус ТЗ и единый чеклист (этот файл)  
Статус: `DONE`

2. `F2` Версионированный Data Contract для OHLCV  
Статус: `DONE (v1)`  
Артефакты: `src/mlbotnav/data_contract.py`, `contract_version=ohlcv_v1`.

3. `F3` Quarantine + блокировка прохода в `core` при `DQ FAIL/contract FAIL`  
Статус: `DONE (ingest_day + ingest_incremental)`  
Артефакты: `data/raw`, `data/core`, `data/quarantine`.

4. `F4` Retry/backoff/jitter + `partial_success` по `symbol+timeframe`  
Статус: `DONE (v1)`  
Артефакты: `src/mlbotnav/ingest_policy.py`, `data/meta/ingest_pair_status.csv`.

5. `F5` Базовая storage-схема `raw/core/analytics/dq/meta` в локальном контуре  
Статус: `DONE (v1)`  
Артефакты: `src/mlbotnav/storage_registry.py`, `data/analytics/*.csv`, `data/meta/storage_partitions.csv|.parquet(optional)`.

## Блок M (ML-ядро)

6. `M1` Полный набор Structure/Pattern фич по ТЗ  
Статус: `IN PROGRESS`

7. `M2` Stage-engine `D1 -> D2 -> D3 -> D5 -> D30 -> D60 -> D90`  
Статус: `DONE (runtime v2)`

8. `M3` Negative Memory (fingerprint + cooldown + fail reasons)  
Статус: `DONE (runtime v2)`

9. `M4` Торговые инварианты (`TP>=1%`, `trades/day bounds`, строгий `NO_TRADE`)  
Статус: `IN PROGRESS`

10. `M5` Линейка моделей до уровня ТЗ (`LightGBM/XGBoost` + ablation)  
Статус: `DONE (v1)`

## Блок P (Prod/Monitoring/Governance)

11. `P1` Inference + paper trading контур  
Статус: `TODO`

12. `P2` Monitoring SLA (latency/error/perf) + алерты  
Статус: `IN PROGRESS`

13. `P3` Ранцы полного формата (`index.parquet`, xlsx/parquet exports, retention policies)  
Статус: `IN PROGRESS`

14. `P4` Security hardening (`RBAC`, `KMS/vault`, artifact signing, immutable audit`)  
Статус: `TODO`

## Правило исполнения

Блок `F` закрыт на уровне `v1` (инженерный фундамент).  
Текущий рабочий этап: переход в `M1` (расширение Structure/Pattern и торговых инвариантов по ТЗ).

## Progress Update (2026-05-21)
- Foundation block F1..F5 implemented at v1.
- M1/M4 implementation started: expanded Structure/Pattern features, removed future-leakage pattern flag logic, and enabled trades/day gate controls.

## Progress Update (TA, 2026-05-21)
- M1 (Structure/Pattern) upgraded with deterministic TA pipeline to `analytics.levels`, `analytics.pattern_events`, `analytics.signal_events`.
- M4 invariants enforced in TA signals: `TP>=1%`, `min_expected_move_pct`, explicit `NO_TRADE` reasons.
- Prod cycle now includes `technical_analysis` step (`prod.cycle.run_technical_analysis=true`).

## Progress Update (TA wave-2, 2026-05-21)
- Added H&S/inverse H&S/pennant detectors.
- Added ADX/MFI/Stochastic into signal decision context.
- Added fallback event log and parquet/xlsx TA exports.
- 30-day 1m TA rebuild completed with strict invariant gates and deduped fallback table.

## Progress Update (Stage/Backtest/Packs, 2026-05-21)
- `prod_cycle` now runs `stage_engine` automatically after pipeline step (`prod.cycle.run_stage_engine=true`).
- Added runtime stage state file: `data/meta/stage_runtime_state.json` with auto-advance on stage pass.
- Stage criteria expanded toward spec section 19.7: stability/no-trade/day-PnL checks and drawdown regression checks.
- Backtest trade logs now include `expected_move_pct`, `tp_reach_prob`, `sl_hit_prob`, `ev`.
- Packs index now exported to both `packs/index.csv` and `packs/index.parquet`.
- Promotion now checks candidate vs champion guardrails (return delta / drawdown regression / sharpe delta) before promote.

## Progress Update (P2 block-1 done, 2026-05-21)
- Rollback guard upgraded from recommendation-only to executable rollback action via champion history restore.
- Champion lifecycle now writes:
  - `models/registry/champion_history.jsonl`
  - `models/registry/active_model.json`
- Added SLA monitor (`latency/error/perf`) with artifacts:
  - `reports/monitoring/sla_report_*.json`
  - `reports/monitoring/sla_alert_*.json` when breached.
- `prod_cycle` now records per-step execution duration (`duration_ms`) and runs SLA monitoring automatically (`prod.cycle.run_sla_monitor=true`).

## Progress Update (M5 block done v1, 2026-05-21)
- `pipeline_train_eval` upgraded with model-family selection: `logreg`, `lightgbm`, `xgboost`, `auto`.
- Auto model-selection compares candidates on walk-forward + backtest and selects best score.
- Added ablation by feature groups (`price_volatility`, `trend_momentum`, `volume_flow`, `structure_ta`, `pattern`).
- Added ablation artifact export: `reports/pipeline/ablation_*.csv`.

## Progress Update (M2/M3 block done v2, 2026-05-21)
- Added full stage-ladder runtime `D1 -> ... -> D90` runner: `src/mlbotnav/stage_ladder.py`.
- D1 exhaustive search integrated before stage decision with coverage artifact (`total_candidates/pass_candidates`).
- Stage runtime state now stores active stage params and transition history with deterministic replay context.
- `prod_cycle` now passes real stage params/context to `stage_engine` (fixed empty-params fingerprint issue).
- Negative memory enriched with `reason_tags`, `param_signature`, `cooldown_remaining_hours`, and summary API.

---
## Источник: C:\Users\007\Desktop\MLbotNav\docs\TZ_MASTER_PLAN_RU.md
---

# MLbotNav: Мастер-план выполнения оставшихся пунктов ТЗ

Дата плана: 2026-05-21
Источник требований: `TECH_SPEC_ML_PLATFORM_RU.md`

## 1. Текущее состояние

- DONE: ingestion day/incremental, DQ, watermark, baseline train, candles+EMA+volume, unified train-eval pipeline.
- IN PROGRESS: усиление фич и стабильность gate.
- TODO: champion/challenger automation, drift monitor, rollback flow, CV integrity contour, packs with checksums, security/governance hardening.

## 2. План по оставшимся пунктам

### Phase R1: Champion/Challenger + Gates
1. Реестр кандидатов и активной champion-модели.
2. Автоматическое добавление кандидата после каждого pipeline-run.
3. Правило promote только при `gate.pass = true`.
4. Аудит принятия/отклонения в `reports/registry`.

Критерий приемки:
- Есть `models/registry/champion.json` и `models/registry/candidates.jsonl`.

### Phase R2: Drift/Monitoring
1. Ежедневный drift-report по фичам (reference vs current).
2. Пороговый alert-file при превышении drift threshold.
3. История отчётов в `reports/monitoring`.

Критерий приемки:
- Формируется `drift_report_*.json` и `drift_alert_*.json` при нарушении порога.

### Phase R3: Packs (ранцы)
1. Сбор ранца по дню: свечи, dq, pipeline-report, модель, графики.
2. Подсчет sha256 по артефактам.
3. Индекс ранцев `packs/index.csv`.

Критерий приемки:
- Для дня создаётся `packs/YYYY-MM-DD/session_id/manifest.json` + `checksums.csv`.

### Phase R4: CV Integrity Contour (минимальный)
1. Прием скриншота с source-id и timestamp.
2. sha256 и простая perceptual-сигнатура.
3. Metadata JSON + локальный индекс.

Критерий приемки:
- Есть `data/cv/original/...`, `metadata.json`, `cv_index.csv`.

### Phase R5: Security/Governance Hardening (минимум)
1. Централизованный audit-log по ключевым операциям.
2. Политика хранения/маскировки секретов в отчетах.
3. Базовый runbook и SOP-файлы.

Критерий приемки:
- В `logs/audit.log` пишутся операции ingest/train/promote/pack/cv_ingest.

### Phase R6: Улучшение ML-качества до первого PASS
1. Расширить feature-set `Structure/Pattern`.
2. Запустить horizon-scan + threshold-scan.
3. Зафиксировать первый PASS-run и назначить champion.

Критерий приемки:
- Есть как минимум один pipeline report с `gate.pass=true`.

## 3. Последовательность выполнения

1. R1 -> R2 -> R3 -> R4 -> R5 (инфраструктурные контуры).
2. Параллельно R6 до первого PASS.
3. После первого PASS включить регулярный цикл incremental ingest -> train-eval -> registry decision -> drift check -> pack.

## Жесткие правила процесса (обязательно)
1. Сначала полностью закрываем минутный этап на `1m`.
2. Показываем итоговый визуальный отчет: график, точки входа/выхода, метрики.
3. Только после явного подтверждения результата разрешается 30-дневное окно на `1m`.
4. До подтверждения 30-дневный прогон блокируется, остаемся на минутном этапе по gate.
5. Gate-файл: `configs/workflow_gate.yaml`.

---
## Источник: C:\Users\007\Desktop\MLbotNav\docs\TZ_AUDIT_2026-05-21_FINAL_RU.md
---

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

---
## Источник: C:\Users\007\Desktop\MLbotNav\docs\TZ_EXECUTION_PLAN.md
---

# MLbotNav: Декомпозиция ТЗ и статус исполнения

Источник: `TECH_SPEC_ML_PLATFORM_RU.md` (версия 1.0 от 2026-05-20)

## P0: Обязательная база (блокирует все следующее)

1. Контур выгрузки Bybit v5 дневными батчами UTC.
   - Статус: `DONE (MVP)`
   - Что есть: `src/mlbotnav/ingest_day.py`, `src/mlbotnav/bybit_client.py`
2. Туннель к внешним ключам без смешения кода проектов.
   - Статус: `DONE`
   - Что есть: `SOURCE_ENV_PATH` в `.env`, загрузка в `settings.py`
3. Свечной график для ручной проверки данных (candles + EMA + volume).
   - Статус: `DONE`
   - Что есть: `src/mlbotnav/plot_candles.py`
4. Data Quality Gate + отчеты полноты/валидности.
   - Статус: `IN PROGRESS`
   - Что добавляем: `src/mlbotnav/dq.py`, `data/dq/ohlcv_quality_report.csv`
5. Идемпотентность и watermark прогресса загрузки.
   - Статус: `IN PROGRESS`
   - Что добавляем: `data/meta/ingest_run.csv`, `data/meta/ingest_watermark.csv`

## P1: Базовый ML-контур

1. Baseline-модель и отчет метрик.
   - Статус: `DONE (MVP)`
   - Что есть: `src/mlbotnav/train_baseline.py`
2. Walk-forward и leakage-safe фичи.
   - Статус: `TODO`
3. Backtest с fee/slippage.
   - Статус: `TODO`

## P2: Прод-контур (следующий этап)

1. Champion/challenger + quality gates.
2. Drift/latency мониторинг и алерты.
3. Rollback policy.

## P3: CV-контур и ранцы

1. Скриншоты + integrity (hash/phash/dedup).
2. Overlay renderer.
3. Artifact packs + index.

## Правило работы в этом репозитории

Берем из внешнего проекта только доступ к бирже (ключи/endpoint), но вся логика ingest/DQ/ML хранится и развивается локально в `MLbotNav`.

## Rule Fix: Minute-First + User Approval Gate
1. Work only on `1m` timeframe until minute-stage result is fully reviewed.
2. Before user confirmation, any 30-day run is blocked.
3. Only after user confirms final minute-stage result, allow 30-day minute runs.
4. No timeframe switching is allowed while gate is locked to `1m`.
5. Confirmation command (after user approval):
   `python -m mlbotnav.workflow_gate --allow-30d true --mark-minute-study-complete true --confirmation-note "user approved minute final"`
