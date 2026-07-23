param(
    [string]$StartDay = "2026-01-27",
    [string]$EndDay = "2026-02-27",
    [switch]$NoStrict,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$env:PYTHONPATH = "src"

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

$argsList = @(
    "-m",
    "mlbotnav.stas5_v5_batch_dataset_builder",
    "--start-day",
    $StartDay,
    "--end-day",
    $EndDay
)

if ($NoStrict) {
    $argsList += "--no-strict"
}

& $python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5_batch_dataset_builder failed with exit code $LASTEXITCODE"
}

$startCompact = ([datetime]::ParseExact($StartDay, "yyyy-MM-dd", $null)).ToString("yyyyMMdd")
$endCompact = ([datetime]::ParseExact($EndDay, "yyyy-MM-dd", $null)).ToString("yyyyMMdd")
$report = Join-Path $repoRoot "STAS5_ML_CORE\artifacts\v5\STAS5_V5_BATCH_${startCompact}_${endCompact}_AUDIT_RU.md"
if ($OpenReport) {
    Invoke-Item -LiteralPath $report
}
