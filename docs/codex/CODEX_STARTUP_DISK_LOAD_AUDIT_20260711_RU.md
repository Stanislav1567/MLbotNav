# Аудит нагрузки Codex на диск при холодном старте 2026-07-11

Статус: `CODEX_STARTUP_DISK_LOAD_AUDIT_READY_NO_DELETE_NO_CODE_CHANGE`.

## Короткий вывод

Критической аварии сейчас не видно. После запуска система приходит в норму: текущие замеры диска во время аудита были примерно `3.5%..24%`, `git status` выполняется за `0.04..0.07s`, зависшего `git add -A` нет.

Но минутная нагрузка диска после перезагрузки объяснима и ее стоит облегчить: локальная история Codex и рабочая папка уже содержат много крупных файлов, которые Codex, Windows, антивирус и индексатор могут прогревать после холодного старта.

## Главные находки

1. Диск системный нормальный: `ADATA LEGEND 710`, `NVMe SSD`, `Healthy`, свободно около `353.9 GB` из `476 GB`.
2. Автозапуска Codex/VS Code/Git через `Win32_StartupCommand` не найдено.
3. Текущий Git не является активной причиной постоянной нагрузки:
   - `git status --short --untracked-files=normal`: около `41..72 ms`;
   - `git ls-files --others --exclude-standard`: около `57 ms`;
   - `git write-tree`: около `46 ms`;
   - зависшего `git add -A` не найдено.
4. В проекте остаются тяжелые папки:
   - `_codex_offload_20260530`: около `5912 MB`;
   - `models`: около `1517 MB`;
   - `reports`: около `1070 MB`;
   - `STAS2_MARKET_PHASE_REVIEW`: около `845 MB`;
   - `.venv`: около `651 MB`;
   - `.git`: около `641 MB`;
   - `STAS3_PERCENT_LADDER_REVIEW`: около `576 MB`;
   - `STAS1_GOOD_LOW_REVIEW`: около `456 MB`.
5. Главный общий вес Codex вне проекта:
   - `C:\Users\007\.codex`: около `13189 MB`;
   - `C:\Users\007\.codex\sessions`: около `7490 MB`;
   - `C:\Users\007\.codex\sessions_backup_before_restore_20260530-102037`: около `2447 MB`;
   - `C:\Users\007\.codex\archived_sessions`: около `1967 MB`;
   - `C:\Users\007\.codex\logs_2.sqlite`: около `724 MB`, плюс `logs_2.sqlite-wal` около `24 MB`;
   - `C:\Users\007\AppData\Local\OpenAI\Codex`: около `707 MB`.
6. Внутри проекта есть дополнительная копия старой истории Codex: `_codex_offload_20260530`, крупнейший файл там `logs_2.sqlite` около `796 MB`, плюс множество старых `rollout-*.jsonl`.
7. Неигнорируемых Git-файлов сейчас немного по размеру: около `393` файлов на `58.7 MB`, в основном `STAS4_FEATURE_HYPOTHESIS_REVIEW` и `STAS5_ML_CORE`. Поэтому текущий Git быстрый, но Codex/IDE все равно может видеть эти деревья как рабочий контекст.

## Вероятная причина нагрузки при перезагрузке

Наиболее вероятна не одна ошибка, а сумма факторов:

1. Codex при запуске поднимает приложение, app-server, storage service, runtime/plugin metadata и читает локальные SQLite/JSONL-состояния.
2. После холодной перезагрузки Windows еще не держит эти файлы в cache, поэтому чтение `C:\Users\007\.codex` и части рабочего дерева идет с физического диска.
3. Windows Defender/индексация могут параллельно трогать новые или часто меняющиеся `.sqlite`, `.jsonl`, `.png`, `.csv`, `.joblib`, `.venv`, `.git`.
4. В рабочей папке лежит `_codex_offload_20260530` на `5.9 GB`; он уже игнорируется Git/VS Code, но физически остается внутри проекта на рабочем столе.

## Нормально или ненормально

Нормально: если после перезагрузки и открытия Codex диск на `100%` держится около минуты, затем падает до `1..5%`, CPU/RAM спокойные, система не зависает надолго.

Ненормально: если диск держится на `100%` много минут, Codex не открывает треды, появляются зависшие `git add -A`, растет `logs_2.sqlite` каждый запуск на сотни MB, или Windows начинает подвисать при каждом открытии проекта.

## Что делать безопасно

1. Не удалять историю вручную без отдельного решения. В `.codex` лежит рабочая история сессий.
2. Самый сильный безопасный кандидат на разгрузку после подтверждения пользователя: перенести `_codex_offload_20260530` из `C:\Users\007\Desktop\MLbotNav` в отдельный архив вне рабочей папки, например `C:\Users\007\Desktop\Codex_Archive\`.
3. После отдельного подтверждения можно разобрать старые Codex backup/archived-сессии:
   - `C:\Users\007\.codex\sessions_backup_before_restore_20260530-102037`;
   - `C:\Users\007\.codex\archived_sessions`;
   - старые месяцы в `C:\Users\007\.codex\sessions\2026\05` и `2026\06`.
4. Для проекта оставить текущие Git/VS Code исключения. Они уже закрывают `reports`, `models`, `data`, `packs`, `tmp`, `_codex_offload_*`, `STAS1/2/3 runs`.
5. Если нагрузка повторится, отдельным решением можно добавить локальные VS Code excludes для тяжелых STAS4/STAS5 generated artifacts, но не трогать source-of-truth документы.
6. Если есть права администратора, можно добавить в Windows Defender исключения для `C:\Users\007\.codex` и тяжелых архивных папок проекта. Текущий аудит не смог посмотреть Defender exclusions: нужна админ-сессия.

## Контроль после следующей перезагрузки

Сразу после открытия Codex проверить процессы:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -match '^(git|Codex|codex|node_repl|python)\.exe$' -or $_.CommandLine -match 'Codex|MLbotNav|git' } |
  Select-Object ProcessId,ParentProcessId,Name,CommandLine |
  Format-List
```

Проверить диск на 30 секунд:

```powershell
Get-Counter '\PhysicalDisk(_Total)\% Disk Time','\PhysicalDisk(_Total)\Disk Bytes/sec' -SampleInterval 1 -MaxSamples 30
```

Проверить Git:

```powershell
Measure-Command { git status --short --untracked-files=normal | Out-Null }
Measure-Command { git ls-files --others --exclude-standard | Out-Null }
```

## Решение на сейчас

Код не менялся. Файлы, кеши, сессии и артефакты не удалялись и не переносились. Рекомендуемый следующий шаг: получить подтверждение пользователя на перенос `_codex_offload_20260530` из рабочей папки в архив, затем отдельно решить политику очистки старых `.codex` backup/archived-сессий.
