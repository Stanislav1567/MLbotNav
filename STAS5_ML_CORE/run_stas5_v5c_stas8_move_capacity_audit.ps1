param(
    [string]$ForwardRunId = "",
    [string]$ForwardRunDir = "",
    [string]$StartDay = "",
    [string]$EndDay = "",
    [switch]$SkipVisual,
    [switch]$NoStrict,
    [switch]$SoftV2Preview,
    [string]$SoftV2Presets = "strict,balanced,wide",
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
    "-m", "mlbotnav.stas5_v5c_stas8_move_capacity_audit"
)
if ($ForwardRunId) { $argsList += @("--forward-run-id", $ForwardRunId) }
if ($ForwardRunDir) { $argsList += @("--forward-run-dir", $ForwardRunDir) }
if ($StartDay) { $argsList += @("--start-day", $StartDay) }
if ($EndDay) { $argsList += @("--end-day", $EndDay) }
if ($SkipVisual) { $argsList += "--skip-visual" }
if ($NoStrict) { $argsList += "--no-strict" }
if ($SoftV2Preview) { $argsList += "--soft-v2-preview" }
if ($SoftV2Presets) { $argsList += @("--soft-v2-presets", $SoftV2Presets) }

& $Python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5c_stas8_move_capacity_audit failed with exit code $LASTEXITCODE"
}

if ($OpenFolder) {
    if ($ForwardRunDir) {
        $runDir = Resolve-Path -LiteralPath $ForwardRunDir
    } elseif ($ForwardRunId) {
        $runDir = Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5c\forward\runs\$ForwardRunId"
    } else {
        $latestForward = Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5c\forward\STAS5_V5C_LATEST_TWO_BLOCK_FORWARD_RUN.json"
        $payload = Get-Content -LiteralPath $latestForward -Raw | ConvertFrom-Json
        $runDir = Join-Path $RepoRoot $payload.run_dir
    }
    if ($SoftV2Preview) {
        Invoke-Item -LiteralPath (Join-Path $runDir "stas8_move_capacity_audit\soft_capacity_v2")
    } else {
        Invoke-Item -LiteralPath (Join-Path $runDir "stas8_move_capacity_audit\v1")
    }
}
