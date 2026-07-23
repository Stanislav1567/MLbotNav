param(
    [string]$Day = "2026-05-10",
    [string]$EndDay = "2026-05-12",
    [string]$Stas2RunDir = "STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260510_20260512_continuous_wave_v2_20260709_081330",
    [string]$RunLabel = "stas3_v2_20260510_20260512_long_only",
    [double]$HoldHours = 48.0,
    [int]$PostPlotMinutes = 360,
    [int]$RenderLimit = 0,
    [int]$TpFastMinutes = 120,
    [int]$TpMinSamples = 5,
    [double]$TpHitRateMin = 0.60,
    [double]$TpFastHitRateMin = 0.50
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($EndDay)) {
    $EndDay = $Day
}

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONPATH = "src"

$argsList = @(
    "-m", "mlbotnav.visual_entry_stas3_percent_ladder_review",
    "--start-day", $Day,
    "--end-day", $EndDay,
    "--run-label", $RunLabel,
    "--hold-hours", ([string]$HoldHours),
    "--post-plot-minutes", ([string]$PostPlotMinutes),
    "--render-limit", ([string]$RenderLimit),
    "--tp-fast-minutes", ([string]$TpFastMinutes),
    "--tp-min-samples", ([string]$TpMinSamples),
    "--tp-hit-rate-min", ([string]$TpHitRateMin),
    "--tp-fast-hit-rate-min", ([string]$TpFastHitRateMin)
)

if (-not [string]::IsNullOrWhiteSpace($Stas2RunDir)) {
    $argsList += @("--stas2-run-dir", $Stas2RunDir)
}

& .\.venv\Scripts\python.exe @argsList
