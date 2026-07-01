# ТЗ: Visual Entry target-lock и multi-strategy library

Статус: `ACTIVE_VISUAL_ENTRY_TARGET_LOCK_TZ`.

Главный полный аудит и ТЗ: `reports/final_review/visual_entry_v3/target_locked_strategy_tz/visual_entry_target_locked_strategy_audit_and_tz_20260629_RU.md`.

## Проблема

V9 ловил больше пользовательских стрелок, но давал много false. V10 стал чище, но потерял часть хороших входов. Значит, текущий процесс улучшения неправильный: он оптимизирует шум, но не защищает уже найденные хорошие попадания.

## Новое правило

Любой хороший вход, который уже пойман V9/V10, должен стать `target-lock`. Следующая версия не имеет права потерять его молча.

Если locked target потерян, статус прогона:

`REGRESSION_LOST_LOCKED_TARGET_NO_ML`.

## Архитектура

Нужна не одна стратегия, а библиотека разных стратегий:

1. `HOT_CHAIN_EVENT_LOW`
2. `DEEP_EARLY_CAPITULATION`
3. `DEEP_TERMINAL_RECLAIM`
4. `WARM_LATE_RETEST_RECLAIM`
5. `HOT_FIRST_STRONG_RECLAIM`
6. `HOT_PULLBACK_LATE_RECLAIM`
7. `STRUCTURAL_SWING_RETEST`
8. `BOS_FIBO_RECLAIM`
9. `VOLUME_ABSORPTION_LOW`

Union разрешен только как diagnostic/approved renderer, не как источник широкой стратегии.

## V11

Следующий слой: `V11_RECOVER_RANKED_MISSES`.

Перед ним обязательно сделать:

1. `target_lock_ledger`;
2. lock-файл по целям `2026-05-13` и `2026-05-14`;
3. отчет `kept / recovered / lost / uncovered / false`.

V11 должен:

1. сохранить `2026-05-13 08:48`;
2. сохранить V10-kept цели `2026-05-14`: `04:07`, `08:15`, `09:46`, `12:07`, `14:40`, `16:53`, `18:10`;
3. вернуть потерянные V9-хиты отдельными подрежимами: `03:24`, `10:49`, `15:19`, `18:50`, `20:50`;
4. не возвращать шумный V9 research union `68 false`;
5. построить отдельные PNG по каждому семейству и compact итоговый PNG.

## V12

После V11 добирать еще не покрытые цели:

`2026-05-14`: `06:42`, `07:40`, `14:14`, `15:46`, `17:35`.

`2026-05-13`: все, кроме `08:48`.

V12 механики: swing/retest, BOS/CHOCH, FIBO reclaim, volume absorption, RSI/MACD/Stoch как подтверждение, trend-dip, support/resistance retest.

## Запреты

1. Не передавать результаты в ML без ручного `APPROVED_FOR_ML`.
2. Не использовать future return, TP/SL, MFE/MAE, entry-candle OHLCV.
3. Не использовать cooldown `30/45/60/90`.
4. Не считать результат улучшением, если потерян locked target.
5. Не использовать noisy union как стратегию.

## Проверки

Каждый следующий прогон обязан:

1. писать JSON/MD ledger;
2. писать PNG по семействам;
3. писать compact PNG;
4. проходить unit tests;
5. проходить `text_guard`;
6. проверять отсутствие живых `python.exe` процессов по `MLbotNav/mlbotnav/APTuna/visual_entry`.
