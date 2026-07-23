param(
    [Parameter(Mandatory = $true)]
    [string]$Day,

    [Parameter(Mandatory = $true)]
    [string[]]$GoodIds,

    [string]$Full274RunDir = "",
    [switch]$OpenFolder
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$env:PYTHONPATH = "src"

$goodIdsJoined = ($GoodIds -join ",")

$argsList = @(
    "-m",
    "mlbotnav.stas5_v5_approved_passport_builder",
    "--day",
    $Day,
    "--good-ids",
    $goodIdsJoined
)

if ($Full274RunDir -ne "") {
    $argsList += "--full274-run-dir"
    $argsList += $Full274RunDir
}

python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5_approved_passport_builder failed with exit code $LASTEXITCODE"
}

$compactDay = $Day.Replace("-", "")
$outDir = Join-Path $repoRoot "STAS5_ML_CORE\artifacts\v5\market_passports\$compactDay"

if ($OpenFolder) {
    Invoke-Item -LiteralPath $outDir
}
