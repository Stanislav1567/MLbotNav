param(
    [string]$Day = "2026-05-02",
    [string]$EndDay = "",
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$RunLabel = "",
    [double]$OutcomeLookaheadHours = 0,
    [int]$RenderGoodLimit = 80
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

if ([string]::IsNullOrWhiteSpace($RunLabel)) {
    $labelEnd = if ([string]::IsNullOrWhiteSpace($EndDay) -or $EndDay -eq $Day) { "" } else { "_$($EndDay.Replace('-', ''))" }
    $RunLabel = "stas1_$($Day.Replace('-', ''))$labelEnd`_0p5"
}

if ([string]::IsNullOrWhiteSpace($EndDay)) {
    $EndDay = $Day
}

$OutDir = Join-Path $Root "STAS1_GOOD_LOW_REVIEW\runs"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$env:PYTHONPATH = "src"

& ".\.venv\Scripts\python.exe" -m mlbotnav.visual_entry_good_1pct_review_pool `
    --start-day $Day `
    --end-day $EndDay `
    --symbol $Symbol `
    --timeframe $Timeframe `
    --run-label $RunLabel `
    --target-pct 0.5 `
    --outcome-lookahead-hours $OutcomeLookaheadHours `
    --out-dir $OutDir `
    --render-good-limit $RenderGoodLimit

Write-Host ""
Write-Host "STAS1 +0.5% run finished. Open latest result:"
Write-Host ".\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1"
Write-Host ""
Write-Host "Python tails:"
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
    Where-Object {
        $_.CommandLine -like '*MLbotNav*' -or
        $_.CommandLine -like '*mlbotnav*' -or
        $_.CommandLine -like '*visual_entry*'
    } |
    Select-Object ProcessId, CommandLine
