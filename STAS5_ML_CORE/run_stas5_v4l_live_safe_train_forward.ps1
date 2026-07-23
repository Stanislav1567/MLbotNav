param(
  [string]$TrainStartDay = "2026-05-01",
  [string]$TrainEndDay = "2026-05-25",
  [string]$ForwardStartDay = "2026-05-26",
  [string]$ForwardEndDay = "2026-05-30",
  [double]$EnterThreshold = 0.50,
  [double]$UnsureThreshold = 0.35,
  [int]$Stas2RenderLimit = 1,
  [switch]$AllowNonLowestSoFar
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
$env:PYTHONPATH = Join-Path $RepoRoot "src"

if ($TrainStartDay -ne "2026-05-01" -or $TrainEndDay -ne "2026-05-25") {
  throw "V4L wrapper is locked to train window 2026-05-01..2026-05-25 for this corrected ledger."
}

$RunStamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$TrainRunId = "stas5_v4l_train_$RunStamp"
$ForwardStartCompact = $ForwardStartDay.Replace("-", "")
$ForwardEndCompact = $ForwardEndDay.Replace("-", "")
$ForwardRunId = "stas5_v4l_forward_${ForwardStartCompact}_${ForwardEndCompact}_$RunStamp"

Write-Host "== STAS5 V4L live-safe dataset: $TrainStartDay..$TrainEndDay =="
python -m mlbotnav.stas5_v4l_live_safe_dataset

Write-Host "== STAS5 V4L live-safe training: $TrainRunId =="
$TrainArgs = @(
  "-m", "mlbotnav.stas5_v4l_live_safe_train",
  "--run-id", $TrainRunId,
  "--enter-threshold", "$EnterThreshold",
  "--unsure-threshold", "$UnsureThreshold"
)
if ($AllowNonLowestSoFar) {
  $TrainArgs += "--allow-non-lowest-so-far"
}
python @TrainArgs

Write-Host "== STAS5 V4L live-safe blind forward: $ForwardStartDay..$ForwardEndDay =="
python -m mlbotnav.stas5_v4l_live_safe_forward `
  --start-day $ForwardStartDay `
  --end-day $ForwardEndDay `
  --run-id $ForwardRunId `
  --stas2-render-limit $Stas2RenderLimit

Write-Host ""
Write-Host "DONE"
Write-Host "Train run:   STAS5_ML_CORE/artifacts/v4l/model/runs/$TrainRunId"
Write-Host "Forward run: STAS5_ML_CORE/artifacts/v4l/forward/runs/$ForwardRunId"
Write-Host "Latest ptr:  STAS5_ML_CORE/artifacts/v4l/forward/STAS5_V4L_LATEST_FORWARD_RUN.json"
