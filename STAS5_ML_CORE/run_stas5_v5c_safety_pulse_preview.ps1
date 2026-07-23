param(
    [string]$ForwardRunId = "",
    [string]$ForwardRunDir = "",
    [string]$StartDay = "",
    [string]$EndDay = "",
    [ValidateSet("BALANCED_SAFETY_V1", "HARD_BLOCK_ONLY_V1", "NO_RISKGATE_ENTRY_ONLY_V1", "DOWN_CHANNEL_NO_LONG_V1")]
    [string]$Policy = "BALANCED_SAFETY_V1",
    [switch]$BollingerPreview,
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
    "-m", "mlbotnav.stas5_v5c_safety_pulse_preview"
)
if ($ForwardRunId) { $argsList += @("--forward-run-id", $ForwardRunId) }
if ($ForwardRunDir) { $argsList += @("--forward-run-dir", $ForwardRunDir) }
if ($StartDay) { $argsList += @("--start-day", $StartDay) }
if ($EndDay) { $argsList += @("--end-day", $EndDay) }
$argsList += @("--policy", $Policy)
if ($BollingerPreview) { $argsList += "--bollinger-preview" }
if ($NoStrict) { $argsList += "--no-strict" }

& $Python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5c_safety_pulse_preview failed with exit code $LASTEXITCODE"
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
    Invoke-Item -LiteralPath (Join-Path $runDir ("safety_pulse_preview\" + $Policy.ToLower()))
}
