# MULTI CHAT COORDINATION PROTOCOL (RU)

Дата: 2026-05-26  
Статус: ACTIVE_MANDATORY  
Область: все рабочие чаты, связанные с MLbotNav/Optuna/AKFP

## 1. Цель
1. Исключить конфликт правок между чатами.
2. Жестко разделить обязанности по задачам и файлам.
3. Сделать прозрачным: кто что делает, где делает, и когда можно мерджить.

## 2. Общие правила (MUST)
1. Работа только через отдельные ветки и отдельные `worktree`.
2. Один активный `task_id` = один владелец `owner_chat`.
3. Чат не правит файлы вне своего `scope_files`.
4. Перед началом шага чат обязан зафиксировать захват в `docs/ACTIVE_WORK_ITEMS_RU.md`.
5. После каждого шага обязательны:
   1. тесты по измененному контуру;
   2. `python -m mlbotnav.text_guard`;
   3. запись в `docs/CHANGELOG_CHRONOLOGY_RU.md`.
6. Без PASS-аудита мердж запрещен.

## 3. Структура веток и рабочих папок
1. Базовая ветка для работы: `main` (только чтение, без прямых коммитов).
2. Формат рабочих веток:
   1. `chat/<chat_name>/<task_id>`
   2. пример: `chat/galileo/P65-16`, `chat/lovelace/P74`
3. Формат `worktree`-папок:
   1. `..\MLbotNav_<chat_name>_<task_id>`

## 4. Старт задачи (процедура)
1. Чат выбирает следующий шаг по ТЗ.
2. В `ACTIVE_WORK_ITEMS_RU.md` обновляет/добавляет строку:
   1. `task_id`
   2. `owner_chat`
   3. `status=IN_PROGRESS`
   4. `scope_files` (строго по факту)
   5. `notes` (что именно делается в этом шаге)
3. Только после фиксации в `ACTIVE` чат начинает менять код.

## 5. Завершение шага
1. Выполнить тесты по измененному контуру.
2. Выполнить `text_guard`.
3. Зафиксировать артефакты (`reports/...`) и статус.
4. Добавить запись в `CHANGELOG_CHRONOLOGY_RU.md`.
5. Обновить строку задачи в `ACTIVE`:
   1. `status=DONE` (или оставить `IN_PROGRESS` если это подшаг длинной задачи).

## 6. Антиконфликтное владение файлами
1. Если файл уже в `scope_files` другой `IN_PROGRESS` задачи, править его нельзя.
2. Исключение: явное согласование владельца в `notes` + отдельная запись в changelog.
3. При конфликте приоритет у чата-владельца текущего `task_id`.

## 7. Обязательный минимум для Optuna-контура
1. Long/short не смешивать.
2. Любые изменения в калибровочных раннерах (`daily_long_short_cycle`, `contour_cycle`, `adaptive_auto_train`) сопровождаются regression-тестом.
3. Любой новый runtime-флаг должен быть протянут сквозь все раннеры, где применимо.

## 8. VS Code workspace rule (MUST)
1. Все рабочие чаты работают только в VS Code.
2. Базовая рабочая папка для всех чатов: `MLbotNav` (единый workspace root).
3. Внутри `MLbotNav` рабочие зоны для текущего контура: `Abtuna` и мосты (bridge-контур).
4. Любой запуск или правка вне `MLbotNav` запрещены без явного согласования и записи в `ACTIVE` и `CHANGELOG`.
5. Любой запуск или правка вне `Abtuna`/bridge-контуров запрещены без отдельной фиксации scope в `ACTIVE`.
6. В каждом шаге в `notes` текущего `task_id` фиксируется `workspace_root`.

## 9. Шаблон статуса для передачи в другой чат
1. `Текущий task_id: ...`
2. `Владелец: ...`
3. `Scope files: ...`
4. `Что сделано: ...`
5. `Что запрещено трогать: ...`
6. `Последний PASS аудит: ...`
7. `Следующий шаг по ТЗ: ...`

## 10. Handoff Lock Rule (MUST)
1. If a blocker is in another chat scope, send official handoff to that owner first.
2. Until owner confirmation, no parallel edits in the same block are allowed.
3. Block owner must record in `ACTIVE`:
1. blocker accepted;
2. exact file scope;
3. no-touch boundaries for other chats.
4. If confirmation times out:
1. blocker is still recorded in `CHANGELOG`;
2. ownership is considered assigned by handoff record;
3. governance chat does not modify owner runtime code path.
5. Any scope overlap without handoff-lock record is a protocol violation.


## 11. Runtime Exclusive Owner (MUST)
1. For each runtime block (`daily_long_short_cycle`, `adaptive_auto_train`, `p23/p24/p26`) there is exactly one active owner chat.
2. Any other chat is forbidden to start the same runtime commands in parallel.
3. If overlap is detected, all duplicated processes must be stopped before next run.
4. Ownership is fixed in `ACTIVE` and mirrored in `CHANGELOG` before launching runs.

## 12. Live Coordination (MUST)
1. Real-time ownership signaling is done via:
   1. `scripts/coord_claim.ps1`
   2. `scripts/coord_release.ps1`
   3. `scripts/coord_watch.ps1`
2. Before starting runtime work, owner chat must run:
   1. `powershell -File .\scripts\coord_claim.ps1 -TaskId <task> -OwnerChat <chat> -Kind runtime -Scope "<paths>" -Note "<step>"`
3. After finishing or handing off, owner chat must run:
   1. `powershell -File .\scripts\coord_release.ps1 -TaskId <task> -OwnerChat <chat> -Kind runtime -Note "<result>"`
4. Other chat can run watcher for live notification:
   1. `powershell -File .\scripts\coord_watch.ps1`
5. The watcher prints new events and emits an audible signal on each claim/release.

## 13. No Cross-Stop Rule (MUST)
1. Any chat is forbidden to stop runtime processes started by another chat.
2. Stop/kill is allowed only for processes that the same chat started and claimed via `coord_claim`.
3. If overlap is detected:
1. do not kill чужой процесс;
2. write conflict event in `CHANGELOG`;
3. wait for owner release (`coord_release`) or request handoff in `ACTIVE`.
4. Processes from other folders/workspaces are never touched.

## 14. Claim/Release Ordering (MUST)
1. `coord_claim` and `coord_release` must be executed sequentially, never in parallel.
2. For one task, the order is strict: `claim -> work -> release`.
3. Any automation that can run commands in parallel must not batch `coord_claim` and `coord_release` together.
4. Coordination scripts use `Global\MLbotNav_live_coord_lock` mutex for atomic state/event updates.

## 15. Unique Owner Identity (MUST)
1. Each chat must use a unique `owner_chat` value (example: `chat_optuna_a`, `chat_optuna_b`).
2. Shared generic owner IDs (like `this_chat`) across multiple chats are forbidden.
3. If duplicate owner identity is detected in events, runtime launches must be paused until owner IDs are separated.
