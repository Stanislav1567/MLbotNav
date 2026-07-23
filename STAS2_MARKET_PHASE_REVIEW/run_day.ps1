param(
    [string]$Day = "2026-05-02",
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$RunLabel = "",
    [string[]]$Stas1RunDir = @(),
    [int]$RenderLimit = 0
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

if ([string]::IsNullOrWhiteSpace($RunLabel)) {
    $RunLabel = "stas2_$($Day.Replace('-', ''))_market_phase_review"
}

$OutDir = Join-Path $Root "STAS2_MARKET_PHASE_REVIEW\runs"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$env:PYTHONPATH = "src"

$argsList = @(
    "-m", "mlbotnav.visual_entry_stas2_market_phase_review",
    "--start-day", $Day,
    "--end-day", $Day,
    "--symbol", $Symbol,
    "--timeframe", $Timeframe,
    "--run-label", $RunLabel,
    "--out-dir", $OutDir,
    "--render-limit", $RenderLimit
)

foreach ($run in $Stas1RunDir) {
    if (-not [string]::IsNullOrWhiteSpace($run)) {
        $argsList += @("--stas1-run-dir", $run)
    }
}

& ".\.venv\Scripts\python.exe" @argsList

Write-Host ""
Write-Host "STAS2 market phase review finished. Open latest result:"
Write-Host ".\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open browse"
Write-Host ".\STAS2_MARKET_PHASE_REVIEW\open_last_run.ps1 -Open xlsx"
Write-Host ""
Write-Host "Python tails:"
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
    Where-Object {
        $_.CommandLine -like '*MLbotNav*' -or
        $_.CommandLine -like '*mlbotnav*' -or
        $_.CommandLine -like '*visual_entry*'
    } |
    Select-Object ProcessId, CommandLine
