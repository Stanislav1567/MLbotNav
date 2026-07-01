# Codex Project Instructions

## Source Of Truth
1. The source of truth for this project is the project files in `C:\Users\007\Desktop\MLbotNav`, not chat memory.
2. Chat history is only a helper. If chat and files disagree, read the project files first and treat them as authoritative.
3. Active calibration-node work has a newer source-of-truth override:
   1. `docs/CALIBRATION_NODE_CURRENT/README_RU.md`
   2. `docs/CALIBRATION_NODE_CURRENT/TZ_CALIBRATION_NODE_CURRENT_2026-06-03_RU.md`
   3. `docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md`
   4. `docs/CALIBRATION_NODE_CURRENT/COMMANDS_RU.md`
4. For calibration-node work, old chronology, old journals, and old TZ files are `OLD/FROZEN`: use them only as artifact references when the new source explicitly points to them. Do not derive the next task from old chronology or old session journals.
5. Before starting work, Codex must read:
   1. `docs/codex/handoff.md`
   2. `docs/codex/current_state.md`
   3. `docs/codex/todo.md`
   4. `docs/codex/known_errors.md`
   5. `docs/codex/commands.md`

## Update Rules
1. After important work, update:
   1. `docs/codex/handoff.md`
   2. `docs/codex/current_state.md`
   3. `docs/codex/todo.md`
   4. `docs/codex/known_errors.md`
   5. `docs/codex/session_log.md`
2. Calibration-node override: after this rule is active, do not update `docs/codex/session_log.md` or `docs/CHANGELOG_CHRONOLOGY_RU.md` for ordinary calibration-node progress unless the user explicitly asks. Write progress into `docs/CALIBRATION_NODE_CURRENT/CURRENT_STATUS_RU.md`.
3. Also update project registries when the work touches Optuna launch state, except when the calibration-node override says to keep old registries frozen:
   1. `docs/ACTIVE_WORK_ITEMS_RU.md`
   2. `docs/CHANGELOG_CHRONOLOGY_RU.md`
   3. the active TZ or audit document referenced by the task

## Artifact Policy
1. Do not paste large logs, CSV files, JSON reports, dumps, model outputs, or run results into chat in full.
2. Store large outputs as files in the project.
3. In `docs/codex/*`, write only a short conclusion and the path to the artifact.

## Language Policy
1. Для этого проекта пользовательский язык работы — русский.
2. Все новые рабочие отчеты, аудиты, статусы, handoff/todo/current_state/known_errors/commands и пояснительные Markdown-документы писать на русском языке.
3. Английский разрешен только для машинных идентификаторов, имен файлов, путей, команд, параметров CLI, action_id/passport_id/block_id, enum/status-кодов и неизменяемых технических ключей JSON/YAML.
4. Если создается файл с суффиксом `_RU.md`, весь человекочитаемый текст внутри должен быть на русском.
5. Если агент или инструмент вернул вывод на английском, в итоговый отчет переносить русскую выжимку, а не английский текст.

## Safety
1. Do not delete history, reports, data, caches, sessions, models, logs, or generated artifacts without direct user approval.
2. Do not run destructive git commands such as `git reset --hard` or `git checkout --` unless the user explicitly requests them.
3. If a large existing memory file must be changed, create a local backup next to it first, for example `file.md.bak-YYYYMMDD-HHMMSS`.
4. Preserve current decisions, commands, errors, conclusions, plans, and results.
