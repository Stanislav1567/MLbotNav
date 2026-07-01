# ТЗ Фиксов: Строгое Исполнение По Плану

Дата: 2026-05-22  
Проект: `C:\Users\007\Desktop\MLbotNav`

## 1. Цель
Довести контур minute-first до стабильного режима, где:
1. выбирается действительно лучший кандидат, а не первый попавшийся;
2. long/short прогоны выполняются раздельно и прозрачно;
3. итоговые артефакты топ-стратегии не смешиваются и читаются без ручного поиска.

## 2. План Фиксов (строгий порядок)
1. F2: исправить выбор кандидата в adaptive loop (best-of-pool).
2. F2.1: убрать ранний выход при `no_goal_candidate` (прогон идет до всех repeats).
3. F5: сохранять прозрачный `selection_mode` в истории прогона.
4. F-LS: закрепить правило раздельного запуска `long_only` и `short_only`.
5. F-VERIFY: сделать smoke-проверку запуска на 1 повторе.

## 3. Статус на сейчас
1. F2: `DONE` — выбор кандидата переведен на ранжирование по качеству.
2. F2.1: `DONE` — нет принудительного break на `no_goal_candidate`.
3. F5: `DONE` — в `history[*].selection_mode` пишется тип отбора.
4. F-LS: `DONE` (документарно) — политика уже зафиксирована в `docs/TZ_LONG_SHORT_CACHE_POLICY_2026-05-22_RU.md`.
5. F-VERIFY: `DONE`.

## 4. Критерии приемки
1. В non-strict режиме fallback берет лучший tradeful кандидат, а не первый.
2. В strict режиме при отсутствии goal-кандидата цикл не падает и не зависает.
3. В summary отчете виден `selection_mode` по каждому повтору.
4. Команды `long_only` и `short_only` дают отдельные независимые результаты.

## 5. Smoke-Артефакты
1. `C:\Users\007\Desktop\MLbotNav\reports\adaptive\adaptive_loop_SOLUSDT_1m_2026-05-20_20260522T144213Z.json`
2. `C:\Users\007\Desktop\MLbotNav\reports\adaptive\adaptive_loop_SOLUSDT_1m_2026-05-20_20260522T144416Z.json`
3. `C:\Users\007\Desktop\MLbotNav\reports\top_strategy\top_SOLUSDT_1m_2026-05-20_20260522T144359Z_MODE-LONG_ONLY_TF-1M_RET-+0.0000pct\trade_simulation.png`
4. `C:\Users\007\Desktop\MLbotNav\reports\top_strategy\top_SOLUSDT_1m_2026-05-20_20260522T144550Z_MODE-SHORT_ONLY_TF-1M_RET-+0.0000pct\trade_simulation.png`
