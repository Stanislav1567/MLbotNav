param(
    [string]$Day = "2026-05-10",
    [string]$Stas2RunDir = "STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260510_20260512_continuous_wave_v2_20260709_081330",
    [string]$RunLabel = "stas3_v2_long_only_day",
    [double]$HoldHours = 48.0,
    [int]$PostPlotMinutes = 360,
    [int]$RenderLimit = 0,
    [int]$TpFastMinutes = 120,
    [int]$TpMinSamples = 5,
    [double]$TpHitRateMin = 0.60,
    [double]$TpFastHitRateMin = 0.50
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$params = @{
    Day = $Day
    EndDay = $Day
    RunLabel = $RunLabel
    HoldHours = $HoldHours
    PostPlotMinutes = $PostPlotMinutes
    RenderLimit = $RenderLimit
    TpFastMinutes = $TpFastMinutes
    TpMinSamples = $TpMinSamples
    TpHitRateMin = $TpHitRateMin
    TpFastHitRateMin = $TpFastHitRateMin
}

if (-not [string]::IsNullOrWhiteSpace($Stas2RunDir)) {
    $params["Stas2RunDir"] = $Stas2RunDir
}

& .\STAS3_PERCENT_LADDER_REVIEW\run_range.ps1 @params
