# ТЗ: Фикс По Расследованию (5 Пунктов)

Дата: 2026-05-22  
Проект: `MLbotNav`  
Контур: `1m`, приоритет `long_only`

## 0) Контекст
- Расследование подтвердило: арифметика сама по себе не «врет», но результаты искажаются из-за смешения режимов симуляции и fallback-логики отбора.
- Цель этого ТЗ: убрать методологические и технические источники «обмана» в отчетах и ранжировании.

## 1) Пять обязательных пунктов фикса

### P0. Запрет скрытого fallback `exchange_like -> research`
Проблема:
- При некоторых условиях симулятор может уйти в исследовательскую ветку, что ломает сопоставимость с реалистичным исполнением.

Где:
- [backtest.py:251](/C:/Users/007/Desktop/MLbotNav/src/mlbotnav/backtest.py:251)

Что сделать:
- Если запрошен `execution_mode=exchange_like`, а обязательных полей нет, завершать run ошибкой (`fail-closed`), а не переключаться автоматически на `research`.

Критерий приемки:
- Запуск в `exchange_like` без нужных OHLC-колонок падает с явной ошибкой режима.
- В OOS отчете нет случаев, где запрошен `exchange_like`, а фактически считалось в `research`.

---

### P0. Исключить `research` из боевого ранжирования TOP
Проблема:
- `research` режим допускает lookahead-эффект и не должен участвовать в прод-отборе.

Где:
- [backtest.py:269](/C:/Users/007/Desktop/MLbotNav/src/mlbotnav/backtest.py:269)
- [backtest.py:271](/C:/Users/007/Desktop/MLbotNav/src/mlbotnav/backtest.py:271)
- [backtest.py:297](/C:/Users/007/Desktop/MLbotNav/src/mlbotnav/backtest.py:297)

Что сделать:
- Для `adaptive_auto_train`/`top_strategy` разрешать публикацию `TOP_LATEST` только из `execution_mode=exchange_like`.
- `research` оставить только как диагностический/экспериментальный режим, с явной маркировкой.

Критерий приемки:
- Любой run в `research` не публикуется как боевой TOP.
- В карточке стратегии явно указан `execution_mode`.

---

### P1. Синхронизировать proxy-логику между search и runtime backtest
Проблема:
- Разные формулы proxy в search и runtime давали разные кандидаты/фильтрацию.

Где:
- Search: [search_gate_candidate.py:105](/C:/Users/007/Desktop/MLbotNav/src/mlbotnav/search_gate_candidate.py:105)
- Runtime: [backtest.py:441](/C:/Users/007/Desktop/MLbotNav/src/mlbotnav/backtest.py:441)

Что сделать:
- Использовать одну и ту же формулу в sanity-check и runtime (`conf * atr * sqrt(hold)`).
- Логировать `proxy_max`, `grid_min`, `horizon` в search-отчете.

Критерий приемки:
- `search_failed` по причине «grid_above_proxy» совпадает с фактической runtime-логикой.
- Нет расхождений «search пропустил, runtime отрезал на том же параметре».

---

### P1. Ужесточить селекцию: не публиковать TOP без `gate_pass`
Проблема:
- Fallback-кандидаты без `gate_pass` давали случайные OOS-всплески и путали интерпретацию.

Где:
- [adaptive_auto_train.py:313](/C:/Users/007/Desktop/MLbotNav/src/mlbotnav/adaptive_auto_train.py:313)
- [adaptive_auto_train.py:821](/C:/Users/007/Desktop/MLbotNav/src/mlbotnav/adaptive_auto_train.py:821)

Что сделать:
- Разделить статусы:
  - `production_top` (только `gate_pass=true`)
  - `experimental_top` (fallback, без публикации как боевой)
- В `TOP_LATEST` писать только production-top.

Критерий приемки:
- В `reports/top_strategy/TOP_LATEST.json` нет стратегии с `gate_pass=false`.
- Экспериментальные результаты сохраняются отдельно и не маскируются под боевые.

---

### P2. Исправить отчетность и воспроизводимость run
Проблема:
- Неверная/неполная интерпретация: например, подпись `1-day test` при multi-day.

Где:
- [top_strategy.py:270](/C:/Users/007/Desktop/MLbotNav/src/mlbotnav/top_strategy.py:270)

Что сделать:
- В `tagline` и карточке всегда отражать фактическое окно (`test_day` + `test_end_day`).
- Добавить manifest воспроизводимости в каждый adaptive run:
  - `execution_mode`
  - `window_policy`
  - `rows_raw/rows_featured`
  - `feature schema hash`
  - `code snapshot hash` (если git не доступен, локальный hash файлов ядра)

Критерий приемки:
- Нет расхождений между текстом карточки и фактическим диапазоном теста.
- Любой run можно повторить по manifest.

---

## 2) Порядок внедрения (строго)
1. P0 fail-closed для `exchange_like`.  
2. P0 запрет `research` для боевого TOP.  
3. P1 sync proxy search/runtime (проверить на 1m smoke).  
4. P1 hard gate для production TOP.  
5. P2 правка отчетности + manifest.

## 3) Smoke-проверки после фикса
- `1m long_only`, train `2026-05-17..2026-05-19`, test `2026-05-20..2026-05-21`.
- Проверить:
  - run не уходит в `research` при `exchange_like`;
  - отчет содержит реальный `execution_mode`;
  - `TOP_LATEST` обновляется только при `gate_pass=true`;
  - `tagline` корректно показывает диапазон теста.

## 4) Ограничения
- CPU-контроль оставить: не выше `85%` sustained.
- Чужие прогоны не останавливать.
- Не менять торговую логику вне 5 пунктов данного ТЗ.

