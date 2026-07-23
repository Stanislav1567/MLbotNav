# Разгрузка Codex CPU/Git 2026-07-16

Статус: `CODEX_UNLOAD_APPLIED_NO_DELETE_NO_PROCESS_KILL_CODEX`.

## Что сделано

1. Файлы не удалялись и не переносились.
2. Процессы `Codex.exe`/`codex.exe` не останавливались.
3. Для процессов `Codex`/`codex` установлен приоритет `BelowNormal`, чтобы Windows давала Codex меньше CPU при конкуренции с другими программами.
4. Проверены повторяющиеся Git-процессы Codex. `git add -A` появлялся повторно, но `.git/index.lock` не было, `git diff --cached --name-only` пустой.
5. В `.gitignore` добавлены generated/run-папки STAS5:
   - `STAS5_ML_CORE/artifacts/`;
   - `STAS5_ML_CORE/runs/`.
6. В `.vscode/settings.json` добавлены локальные исключения для watcher/search/Pylance:
   - `**/STAS5_ML_CORE/artifacts/**`;
   - `**/STAS5_ML_CORE/runs/**`.

## Эффект

До разгрузки:

```text
untracked files: 1574
untracked size: 424.8 MB
```

После разгрузки:

```text
untracked files: 381
untracked size: 41.6 MB
```

Проверка ignore:

```text
STAS5_ML_CORE/artifacts -> ignored by .gitignore
STAS5_ML_CORE/runs -> ignored by .gitignore
```

Контроль после правки:

1. `.vscode/settings.json`: `JSON_OK`;
2. `git status --short --untracked-files=normal`: около `79 ms`, затем около `51 ms`;
3. активных `git.exe` после финального контроля не осталось;
4. диск во время контроля: примерно `3.8%..18.1%`;
5. общий CPU: примерно `13.5%..32.6%`;
6. группа `Codex`: около `4.1% CPU` на 10-секундном замере.

## Почему не триммилась память принудительно

Свободной памяти достаточно: около `13.3..13.5 GB` после разгрузки. Принудительное вытеснение working set у Electron/Codex может временно уменьшить цифру RAM, но часто приводит к повторной подкачке с диска и новым лагам. Поэтому применено более безопасное снижение приоритета и уменьшение Git/VS Code scan-поверхности.

## Дальше

Если Codex снова начнет крутить `git add -A`, сначала проверить, не вырос ли dirty worktree:

```powershell
git ls-files --others --exclude-standard | Measure-Object
```

Если нужно еще сильнее разгрузить, следующий безопасный шаг - определить, какие оставшиеся `STAS4_FEATURE_HYPOTHESIS_REVIEW` и `STAS5_ML_CORE` файлы являются source-of-truth, а какие generated artifacts, и добавить только generated artifacts в ignore.
