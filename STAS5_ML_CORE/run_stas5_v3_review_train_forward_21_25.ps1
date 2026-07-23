param(
  [string]$RunId = "",
  [string]$ReviewStartDay = "2026-05-16",
  [string]$ReviewEndDay = "2026-05-20",
  [string]$ForwardStartDay = "2026-05-21",
  [string]$ForwardEndDay = "2026-05-25",
  [string]$ReviewForwardPredictionsPath = "STAS5_ML_CORE\artifacts\v2\forward\STAS5_V2_FORWARD_ALL_PREDICTIONS_20260515_20260520.csv",
  [double]$EnterThreshold = 0.65,
  [double]$UnsureThreshold = 0.45,
  [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

if (-not $RunId) {
  $RunId = "stas5_v3_review_" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  $Python = "python"
}

$env:PYTHONPATH = "src"

function Invoke-StasStep {
  param(
    [string]$Name,
    [string[]]$StepArgs
  )
  Write-Host ""
  Write-Host "== $Name ==" -ForegroundColor Cyan
  & $Python @StepArgs
  if ($LASTEXITCODE -ne 0) {
    throw "Step failed: $Name"
  }
}

Invoke-StasStep "1/5 V3 user-review ledger" @(
  "-m", "mlbotnav.stas5_v3_user_review_ledger",
  "--start-day", $ReviewStartDay,
  "--end-day", $ReviewEndDay,
  "--all-predictions-path", $ReviewForwardPredictionsPath
)

Invoke-StasStep "2/5 V3 train dataset" @(
  "-m", "mlbotnav.stas5_v3_training_dataset_builder",
  "--forward-predictions-path", $ReviewForwardPredictionsPath
)

Invoke-StasStep "3/5 V3 leakage guard" @(
  "-m", "mlbotnav.stas5_v3_leakage_guard"
)

Invoke-StasStep "4/5 V3 train full274" @(
  "-m", "mlbotnav.stas5_v3_entry_ranker_train",
  "--run-id", $RunId,
  "--model-feature-set", "full_v2_all_274",
  "--enter-threshold", ([string]$EnterThreshold),
  "--unsure-threshold", ([string]$UnsureThreshold)
)

Invoke-StasStep "5/5 V3 blind forward 21-25" @(
  "-m", "mlbotnav.stas5_v3_forward_entry_review",
  "--run-id", $RunId,
  "--start-day", $ForwardStartDay,
  "--end-day", $ForwardEndDay
)

$ModelManifestPath = Join-Path $ProjectRoot "STAS5_ML_CORE\artifacts\v3\model\runs\$RunId\stas5_v3_entry_ranker_20260501_20260520_v0.manifest.json"
$ForwardManifestPath = Join-Path $ProjectRoot "STAS5_ML_CORE\artifacts\v3\forward\runs\$RunId\STAS5_V3_FORWARD_ENTRY_REVIEW_MANIFEST.json"

if (-not (Test-Path $ModelManifestPath)) {
  throw "Model manifest not found: $ModelManifestPath"
}
if (-not (Test-Path $ForwardManifestPath)) {
  throw "Forward manifest not found: $ForwardManifestPath"
}

$ModelManifest = Get-Content -Raw -Encoding UTF8 $ModelManifestPath | ConvertFrom-Json
$ForwardManifest = Get-Content -Raw -Encoding UTF8 $ForwardManifestPath | ConvertFrom-Json

if ($ModelManifest.feature_count -ne 274) {
  throw "Unexpected feature_count: $($ModelManifest.feature_count), expected 274"
}
if ($ModelManifest.model_feature_set -ne "full_v2_all_274") {
  throw "Unexpected model_feature_set: $($ModelManifest.model_feature_set)"
}
if ($ForwardManifest.status -ne "STAS5_V3_FORWARD_ENTRY_REVIEW_READY_BLIND_21_25_NO_TP_NO_API_NO_STAS3") {
  throw "Unexpected forward status: $($ForwardManifest.status)"
}

$ReadyDays = @($ForwardManifest.day_outputs | Where-Object { $_.status -eq "READY" })
if ($ReadyDays.Count -ne 5) {
  throw "Unexpected READY day count: $($ReadyDays.Count), expected 5"
}

Write-Host ""
Write-Host "STAS5 V3 ready" -ForegroundColor Green
Write-Host "RunId: $RunId"
Write-Host "Model:   $ModelManifestPath"
Write-Host "Forward: $ForwardManifestPath"
Write-Host "Forward folder: $(Join-Path $ProjectRoot "STAS5_ML_CORE\artifacts\v3\forward\runs\$RunId")"

if (-not $NoOpen) {
  Invoke-Item (Join-Path $ProjectRoot "STAS5_ML_CORE\artifacts\v3\forward\runs\$RunId")
}
