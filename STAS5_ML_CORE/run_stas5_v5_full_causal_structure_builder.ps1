param(
    [string]$Day = "2026-01-27",
    [switch]$OpenFolder,
    [switch]$NoStrict,
    [switch]$NoPlot
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$env:PYTHONPATH = "src"

$argsList = @(
    "-m",
    "mlbotnav.stas5_v5_full_causal_structure_builder",
    "--day",
    $Day
)

if ($NoStrict) {
    $argsList += "--no-strict"
}

if ($NoPlot) {
    $argsList += "--no-plot"
}

python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5_full_causal_structure_builder failed with exit code $LASTEXITCODE"
}

$compactDay = $Day.Replace("-", "")
$outDir = Join-Path $repoRoot "STAS5_ML_CORE\artifacts\v5\market_passports\$compactDay"

if ($OpenFolder) {
    Invoke-Item -LiteralPath $outDir
}
