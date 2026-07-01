# TZ_OPTUNA_SCOPE_LOCK_2026-05-31_RU

Дата фиксации: 2026-05-31  
Контур: только S-code в `C:\Users\007\Desktop\MLbotNav` и Optuna/APTuna калибровочный контур.

## 1. Жесткая зона работ (MUST)
1. Рабочий корень: `C:\Users\007\Desktop\MLbotNav`.
2. Исполняемый калибровочный контур:
1. `C:\Users\007\Desktop\MLbotNav\APTuna`
2. `C:\Users\007\Desktop\MLbotNav\src\mlbotnav` (только Optuna/Adaptive ветка)
3. `C:\Users\007\Desktop\MLbotNav\reports\qa_gate`
4. `C:\Users\007\Desktop\MLbotNav\reports\adaptive`
5. `C:\Users\007\Desktop\MLbotNav\reports\logs`

## 2. Что запрещено в этом цикле
1. Не трогать ML runtime-контур.
2. Не подключать ML-сигналы в Optuna-прогонах.
3. Не смешивать режимы long/short в одном запуске.

## 3. Фактический режим запусков
1. Launcher: `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`.
2. Python: `C:\Users\007\Desktop\MLbotNav\.venv\Scripts\python.exe`.
3. ML backend для запусков: `OptunaMlSignalBackend=off`.
4. Режимы: строго `long_only` и `short_only` раздельно.

## 4. Каноническая цель
1. Довести калибровочный контур до воспроизводимого `GO` по accepted gate.
2. Держать полный аудит-след: `RUN -> CHECKPOINT -> POST-SYNC AUDIT -> TEXT AUDIT -> READINESS`.
