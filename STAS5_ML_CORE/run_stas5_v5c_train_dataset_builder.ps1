param(
    [string]$TrainStartDay = "2026-01-27",
    [string]$TrainEndDay = "2026-03-20",
    [switch]$EnableBollingerLayer,
    [string]$BollingerOhlcvCsv = "",
    [switch]$Force,
    [switch]$NoStrict,
    [switch]$OpenFolder
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $RepoRoot
$env:PYTHONPATH = Join-Path $RepoRoot "src"

$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

$argsList = @(
    "-m", "mlbotnav.stas5_v5c_train_dataset_builder",
    "--train-start-day", $TrainStartDay,
    "--train-end-day", $TrainEndDay
)

if ($Force) { $argsList += "--force" }
if ($NoStrict) { $argsList += "--no-strict" }
if ($EnableBollingerLayer) { $argsList += "--enable-bollinger-layer" }
if ($BollingerOhlcvCsv) { $argsList += @("--bollinger-ohlcv-csv", $BollingerOhlcvCsv) }

& $Python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5c_train_dataset_builder failed with exit code $LASTEXITCODE"
}

if ($OpenFolder) {
    Invoke-Item -LiteralPath (Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5c")
}
