# Проверка CPU-нагрузки Codex 2026-07-15

Статус: `CODEX_CPU_LOAD_CHECK_READY_NO_KILL_NO_DELETE_NO_CODE_CHANGE`.

## Короткий вывод

Текущая проблема больше похожа не на аварийный диск, а на фоновую CPU-активность Codex из-за внутреннего пересчета Git/diff по большому dirty worktree.

Процессы не останавливались. Файлы не удалялись и не переносились. Код не менялся.

## Замеры

1. Общий CPU по `Get-Counter` во время проверки прыгал примерно `22.8%..44.4%`.
2. Диск в это же время был умеренный: примерно `3.5%..26.1%`, то есть не повторял прежний сценарий постоянных `100%`.
3. Свободной памяти было около `14.3..14.6 GB`.
4. Codex по 10-секундному замеру:
   - первый замер: группа `Codex` около `9.2% CPU`, `~3.6 GB PrivateMB`;
   - повторный замер: группа `Codex` около `5.3% CPU`, `~3.5 GB PrivateMB`.
5. Другие активные группы: `TradingView` около `1.5..2.1%`, `chrome` около `1.3..1.6%`, `Code` около `0.9..1.1%`, `explorer` около `1.6..1.7%`.
6. `git status --short --untracked-files=normal` быстрый: около `51 ms`.
7. `git diff --numstat` быстрый при ручной проверке: около `163 ms`.
8. От Codex наблюдались повторяющиеся Git-процессы:
   - `git diff --no-ext-diff --no-textconv --color=never ... --find-renames --numstat -z`;
   - кратко появлялись `git add -u` и `git add -A` от `Codex.exe`;
   - parent `Codex.exe` PID `3748`;
   - команды меняли PID, но повторялись, то есть это похоже на внутренний пересчет состояния Codex, а не на один пользовательский запуск.
9. После появления `git add -A` проверено: `git diff --cached --name-only` пустой, `.git/index.lock` отсутствует. То есть реального staging файлов не произошло; процесс похож на временный внутренний снимок Codex.

## Что изменилось с аудита 2026-07-11

11 июля неигнорируемых Git-файлов было около `393` на `58.7 MB`.

15 июля стало:

```text
untracked files: 1574
untracked size: 424.8 MB
```

Основной источник:

```text
STAS5_ML_CORE: 1220 untracked files, 389.8 MB
STAS4_FEATURE_HYPOTHESIS_REVIEW: 258 untracked files
src: 47 untracked files
tests: 22 untracked files
```

Именно это хорошо объясняет, почему Codex стал тяжелее: рабочее дерево стало намного грязнее, а Codex периодически считает diff/numstat для своего интерфейса и внутреннего состояния.

## Текущая оценка

Это не выглядит как опасный процесс, который надо срочно убивать. Но это уже ощутимая фоновая нагрузка Codex:

1. `Codex.exe` держит несколько тяжелых renderer/main-процессов;
2. `codex.exe app-server` занимает около `~1 GB PrivateMB`;
3. внутренний Git diff повторяется;
4. кратко появляется внутренний `git add -A`, но без staging в пользовательский индекс;
5. dirty worktree вырос до `1574` неигнорируемых файлов.

## Безопасные действия

1. Не убивать Codex/Git прямо сейчас: `git diff` read-only, признаков зависшего `git add -A` нет.
2. Главная разгрузка - уменьшить dirty worktree:
   - либо зафиксировать/закрыть текущую пачку изменений нормальным Git-коммитом;
   - либо добавить generated artifacts в `.gitignore`, но только после решения, какие STAS5/STAS4 файлы являются source-of-truth;
   - либо перенести тяжелые generated/run artifacts из рабочей зоны в архив.
3. Для немедленного облегчения UI после стабилизации файлов можно перезагрузить окно Codex/VS Code, но не во время важного незавершенного действия.
4. Если CPU снова держится высоко, проверять именно повторяющийся `git diff --numstat`/`git add -A` от `Codex.exe`, а не только общий `git status`.
5. Останавливать Git-процесс имеет смысл только если один и тот же PID висит долго, CPU/диск реально высокие, и после этого обязательно проверить `.git/index.lock`. В текущей проверке процессы не останавливались.

## Команды контроля

CPU по процессам:

```powershell
$n=[Environment]::ProcessorCount
$before=Get-Process | Select-Object Id,ProcessName,CPU,WorkingSet64,PrivateMemorySize64
Start-Sleep -Seconds 10
$after=Get-Process | Select-Object Id,ProcessName,CPU,WorkingSet64,PrivateMemorySize64
```

Текущие Git-процессы:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'git.exe'" |
  Select-Object ProcessId,ParentProcessId,CommandLine |
  Format-List
```

Размер dirty worktree:

```powershell
git ls-files --others --exclude-standard | Measure-Object
git ls-files --others --exclude-standard |
  ForEach-Object { if (Test-Path -LiteralPath $_ -PathType Leaf) { Get-Item -LiteralPath $_ } } |
  Measure-Object -Property Length -Sum
```
