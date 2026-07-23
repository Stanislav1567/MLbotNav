# Аудит нагрузки Codex после обновления 2026-07-22

Статус: `CODEX_UPDATE_LOAD_AUDIT_RELIEF_APPLIED_NO_DELETE`.

## Граница безопасности

- Удалений не было.
- Папки проекта и `STAS*` не изменялись.
- Codex Desktop не закрывался.
- Defender (`MsMpEng`) не отключался, системные настройки безопасности не менялись.

## Что изменилось после обновления

Установленный пакет Codex:

```text
OpenAI.Codex_26.715.10079.0_x64__2p2nqsd0c76g0
Version: 26.715.10079.0
```

После обновления основная оболочка Codex в процессах называется `ChatGPT.exe`, а не `Codex.exe`. Поэтому старое понижение приоритета только для `Codex`/`codex` уже не прижимало главный UI-процесс.

Также был найден отдельный сервер VS Code-расширения:

```text
C:\Users\007\.vscode\extensions\openai.chatgpt-26.715.31925-win32-x64\bin\windows-x86_64\codex.exe -c features.code_mode_host=true app-server
```

## Диагностика до разгрузки

Найдены краткие read-only Git-команды от Codex:

- `git.exe config --null --get core.fsmonitor`;
- `git.exe ... hash-object -- STAS4_FEATURE_HYPOTHESIS_REVIEW/..._RU.md`.

Блокировки Git не было:

```text
NO_INDEX_LOCK
```

`git status` после проверки быстрый:

```text
TotalMilliseconds: 51.753
```

Оставшийся неигнорируемый хвост Git:

```text
untracked: 425 файлов / 42.4 MB
top dirs:
STAS4_FEATURE_HYPOTHESIS_REVIEW: 258
src: 65
STAS5_ML_CORE: 37
tests: 34
docs: 11
```

Именно из-за этого хвоста Codex периодически поднимал `git diff --no-index` / `hash-object` по отдельным файлам. После ожидания цикл мог подниматься снова по следующим файлам; активные read-only `git.exe` были остановлены вручную, блокировки `.git/index.lock` не было.

В коротком CPU-окне до разгрузки основную нагрузку давали процессы Codex/ChatGPT:

- `ChatGPT` main - до `45.0` в delta-метрике `Get-Process`;
- `ChatGPT` renderer - до `31.9`;
- `ChatGPT` gpu - до `20.5`;
- `codex.exe app-server` - около `1.1`.

Системный диск в это время не выглядел как зависший `100%`: системные счетчики показывали примерно `0.3..7.8% Disk Time`, чтение почти нулевое, записи в основном до `~1.2 MB/s`.

## Что разгружено

1. Проверены и остановлены текущие read-only Git-процессы, если они еще были активны.
2. Остановлен отдельный VS Code OpenAI/Codex extension server.
3. Приоритеты выставлены в `Idle` для:
   - `ChatGPT.exe`;
   - `codex.exe`;
   - `Code.exe`;
   - `node_repl.exe`;
   - `codex-code-mode-host.exe`, если активен.

## Контроль после разгрузки

Финальное состояние:

```text
NO_GIT_PROCESS
NO_INDEX_LOCK
NO_VSCODE_CODEX_EXTENSION_SERVER
```

Все найденные `ChatGPT`/`codex`/`Code` процессы стоят в `Idle`.

Системные счетчики после разгрузки:

- CPU: примерно `3.9..9.7%`;
- Disk Time: примерно `0.8..10.4%`;
- Disk Read Bytes/sec: `0` на финальном окне;
- Disk Write Bytes/sec: обычно малые записи, один короткий всплеск около `34.8 MB/s`;
- свободная память: примерно `13.5..13.7 GB`.

По PID-замеру сами процессы не показали накопленного read/write больше `0.1 MB` за финальное окно. Оставшийся CPU идет от активного окна Codex/ChatGPT, особенно `renderer` и `gpu`. Их нельзя безопасно убить, не ломая текущую сессию.

## Вывод

Это похоже не на зависшее обновление и не на опасный Git-цикл. Главная причина текущего ощущения нагрузки после обновления - новая оболочка Codex `ChatGPT.exe`, которую старые правила приоритета не прижимали. После перевода `ChatGPT.exe` в `Idle`, остановки VS Code extension server и проверки Git система стала заметно спокойнее: Git чистый, диск не висит, память не давит.

Что останется после перезапуска: приоритеты Windows сбросятся, а VS Code-расширение может снова поднять свой `codex.exe app-server`. Для постоянной разгрузки отдельным решением можно отключить OpenAI/Codex extension в VS Code, но сейчас расширение не удалялось и глобально не отключалось.

Отдельный постоянный способ снизить Git-сканирование - решить, какие оставшиеся `STAS4_FEATURE_HYPOTHESIS_REVIEW` файлы являются generated/review artifacts и могут быть добавлены в ignore. В этом аудите новые ignore по `STAS4` не добавлялись, чтобы не скрыть рабочие source-of-truth файлы без решения пользователя.

## Уточнение по повторному аудиту 2026-07-23

Вывод выше был промежуточным. После отдельного перезапуска Codex Desktop
нагрузка воспроизвелась снова и была подтверждена как Git review/snapshot
storm: `112 git.exe` и `86 taskkill.exe` за `8` секунд. Окончательный
локальный ремонт, чистый checkpoint, Git fsmonitor/cache, карантин двух
повреждённых неиспользуемых объектов и финальный замер описаны в
`docs/codex/CODEX_PROJECT_CPU_RELIEF_20260723_RU.md`.
