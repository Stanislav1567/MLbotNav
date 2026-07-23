@echo off
chcp 65001 >nul
setlocal

set "START_DIR=%~dp0"
for %%I in ("%START_DIR%..\..") do set "PROJECT_ROOT=%%~fI"
set "CONTROL_ROOT=%PROJECT_ROOT%\STAS9_CONTROL_PLANE"
set "SENTINEL_DIR=%CONTROL_ROOT%\STAS9_AGENTS\STAS9_SENTINEL"
set "GLOBAL_POLICY=%CONTROL_ROOT%\PERMISSIONS\GLOBAL_POLICY.yaml"
set "ACTIVITY_LOG=%CONTROL_ROOT%\LOGS\agent_activity.log"

for /f "usebackq delims=" %%T in (`powershell.exe -NoProfile -Command "(Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')"`) do set "STAS9_NOW=%%T"

if not exist "%SENTINEL_DIR%\CONFIG.yaml" (
  >>"%ACTIVITY_LOG%" echo %STAS9_NOW% ^| STAS9_SENTINEL ^| START ^| ERROR_SENTINEL_CONFIG_MISSING ^| NONE
  echo Ошибка: не найден CONFIG.yaml главного агента.
  exit /b 2
)

if not exist "%GLOBAL_POLICY%" (
  >>"%ACTIVITY_LOG%" echo %STAS9_NOW% ^| STAS9_SENTINEL ^| START ^| ERROR_GLOBAL_POLICY_MISSING ^| NONE
  echo Ошибка: не найден GLOBAL_POLICY.yaml.
  exit /b 3
)

if /I "%~1"=="--check" (
  >>"%ACTIVITY_LOG%" echo %STAS9_NOW% ^| STAS9_SENTINEL ^| START_CHECK ^| PASS_PRIMARY_ONLY_READ_ONLY ^| agent_activity.log
  echo STAS9_SENTINEL: конфигурация запуска проверена.
  echo Режим: READ_ONLY.
  echo Специализированные агенты: только ON_DEMAND.
  exit /b 0
)

where codex.cmd >nul 2>&1
if errorlevel 1 (
  >>"%ACTIVITY_LOG%" echo %STAS9_NOW% ^| STAS9_SENTINEL ^| START ^| ERROR_CODEX_CLI_NOT_FOUND ^| NONE
  echo Ошибка: codex.cmd не найден в PATH.
  pause
  exit /b 4
)

cd /d "%PROJECT_ROOT%"
title STAS9 Главный управляющий агент
>>"%ACTIVITY_LOG%" echo %STAS9_NOW% ^| STAS9_SENTINEL ^| START ^| STARTED_PRIMARY_ONLY_READ_ONLY ^| agent_activity.log

codex.cmd --cd "%PROJECT_ROOT%" --sandbox read-only --ask-for-approval on-request "Ты STAS9_SENTINEL, главный управляющий агент STAS9. Общайся на русском языке. Сначала прочитай STAS9_CONTROL_PLANE/STAS9_AGENTS/STAS9_SENTINEL/README_RU.md, ROLE_RU.md, CONFIG.yaml, PERMISSIONS.yaml и STAS9_CONTROL_PLANE/PERMISSIONS/GLOBAL_POLICY.yaml. Работай по умолчанию только в READ_ONLY. Перед любым изменением запроси явное подтверждение пользователя. Не запускай обучение, Optuna, forward или live trading, не изменяй модели, legacy, STAS5-STAS8 и BROKEN_POINTER. Специализированные роли используй только по необходимости и не запускай всех агентов одновременно. Каждое действие фиксируй в журналах STAS9 с полями time, agent, command, result, changed_files."

set "STAS9_EXIT_CODE=%ERRORLEVEL%"
for /f "usebackq delims=" %%T in (`powershell.exe -NoProfile -Command "(Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')"`) do set "STAS9_NOW=%%T"
>>"%ACTIVITY_LOG%" echo %STAS9_NOW% ^| STAS9_SENTINEL ^| STOP ^| EXIT_CODE_%STAS9_EXIT_CODE% ^| agent_activity.log
exit /b %STAS9_EXIT_CODE%
