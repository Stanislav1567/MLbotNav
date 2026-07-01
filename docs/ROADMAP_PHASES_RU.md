# Roadmap По ТЗ (Исполняемый)

## Фаза A. Data Core (в работе)
1. Bybit ingest day UTC: сделано.
2. Incremental ingest + watermark + late data N=3: сделано.
3. DQ отчеты по `symbol+timeframe+day`: сделано.
4. Закрыть ретраи/partial_success по батчам: следующий шаг.

## Фаза B. ML Core (в работе)
1. Baseline train: сделано.
2. Walk-forward и anti-leakage: сделано.
3. Backtest с fee/slippage: сделано.
4. Quality gate pass/fail: сделано.
5. Расширить фичи `Structure/Pattern` из ТЗ: следующий шаг.

## Фаза C. Prod Readiness
1. Champion/challenger registry.
2. Drift/latency мониторинг и алерты.
3. Автооткат по порогам.

## Фаза D. CV + Packs
1. Ingestion скриншотов + integrity.
2. Overlay renderer и слой аннотаций.
3. Packs + index + audit checksums.

## Порядок выполнения
Сейчас идем по схеме: A -> B -> C -> D. До перехода в C все пункты A/B должны быть в статусе done и иметь артефакты в `reports/`.
