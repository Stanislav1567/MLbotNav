param(
    [string]$Day = "2026-05-10",
    [string]$EndDay = "2026-05-12",
    [string]$RunLabel = "stas3_v2_clean_20260510_20260512_long_only",
    [string]$Stas2RunDir = "STAS2_MARKET_PHASE_REVIEW\runs\stas2_20260510_20260512_continuous_wave_v2_20260709_081330",
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [double]$HoldHours = 48
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$env:PYTHONPATH = "src"

.\.venv\Scripts\python.exe -m mlbotnav.visual_entry_stas3_v2_clean_review `
    --root . `
    --stas2-run-dir $Stas2RunDir `
    --start-day $Day `
    --end-day $EndDay `
    --run-label $RunLabel `
    --symbol $Symbol `
    --timeframe $Timeframe `
    --hold-hours $HoldHours
