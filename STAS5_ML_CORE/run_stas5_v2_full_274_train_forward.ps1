param(
    [string]$RunId = ("stas5_v2_full274_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [string]$ForwardStartDay = "2026-05-15",
    [string]$ForwardEndDay = "2026-05-20",
    [double]$EnterThreshold = 0.65,
    [double]$UnsureThreshold = 0.45,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

$env:PYTHONPATH = Join-Path $ProjectRoot "src"

$ForwardStas2RunDir = Join-Path $ProjectRoot "STAS5_ML_CORE\artifacts\forward_source\stas2_runs\stas5_forward_stas2_20260515_20260520_20260710_163714"
$ForwardComboCsv = Join-Path $ProjectRoot "STAS5_ML_CORE\artifacts\v2\features\stas5_v2_combo_features_20260515_20260520_forward_v0.csv"
$ForwardComboManifest = Join-Path $ProjectRoot "STAS5_ML_CORE\artifacts\v2\features\stas5_v2_combo_features_20260515_20260520_forward_v0.manifest.json"

Write-Host "STAS5 V2 FULL 274 RUN: $RunId"
Write-Host "Train: 2026-05-01..2026-05-14"
Write-Host "Forward: $ForwardStartDay..$ForwardEndDay"

Write-Host "Step 1/8: rebuild train V2 combo features"
& $Python -m mlbotnav.stas5_v2_combo_feature_exporter

Write-Host "Step 2/8: rebuild train V2 feature snapshot"
& $Python -m mlbotnav.stas5_v2_feature_snapshot_builder

Write-Host "Step 3/8: run leakage guard"
& $Python -m mlbotnav.stas5_v2_leakage_guard

Write-Host "Step 4/8: run pre-ML audit"
& $Python -m mlbotnav.stas5_v2_pre_ml_audit

Write-Host "Step 5/8: refresh numeric coverage audit for 2026-05-04"
& $Python -m mlbotnav.stas5_v2_numeric_coverage_audit --day 2026-05-04

Write-Host "Step 6/8: rebuild forward V2 combo features"
& $Python -m mlbotnav.stas5_v2_combo_feature_exporter `
    --stas2-run-dir $ForwardStas2RunDir `
    --start-day $ForwardStartDay `
    --end-day $ForwardEndDay `
    --output-csv $ForwardComboCsv `
    --manifest-path $ForwardComboManifest

Write-Host "Step 7/8: train model on full_v2_all_274"
& $Python -m mlbotnav.stas5_v2_entry_ranker_train `
    --model-feature-set full_v2_all_274 `
    --run-id $RunId `
    --enter-threshold $EnterThreshold `
    --unsure-threshold $UnsureThreshold

$ModelManifest = Join-Path $ProjectRoot "STAS5_ML_CORE\artifacts\v2\model\runs\$RunId\stas5_v2_entry_ranker_20260501_20260514_v0.manifest.json"
if (-not (Test-Path -LiteralPath $ModelManifest)) {
    throw "Model manifest not found: $ModelManifest"
}
$ModelPayload = Get-Content -Raw -Encoding UTF8 -LiteralPath $ModelManifest | ConvertFrom-Json
if ($ModelPayload.model_feature_set -ne "full_v2_all_274") {
    throw "Wrong model feature set: $($ModelPayload.model_feature_set)"
}
if ([int]$ModelPayload.feature_count -ne 274) {
    throw "Wrong feature count: $($ModelPayload.feature_count), expected 274"
}

Write-Host "Step 8/8: render blind forward review"
& $Python -m mlbotnav.stas5_v2_forward_entry_review `
    --run-id $RunId `
    --start-day $ForwardStartDay `
    --end-day $ForwardEndDay `
    --stas2-run-dir $ForwardStas2RunDir `
    --v2-combo-path $ForwardComboCsv

$ForwardRunDir = Join-Path $ProjectRoot "STAS5_ML_CORE\artifacts\v2\forward\runs\$RunId"
$ForwardManifest = Join-Path $ForwardRunDir "STAS5_V2_FORWARD_ENTRY_REVIEW_MANIFEST.json"
if (-not (Test-Path -LiteralPath $ForwardManifest)) {
    throw "Forward manifest not found: $ForwardManifest"
}
$ForwardPayload = Get-Content -Raw -Encoding UTF8 -LiteralPath $ForwardManifest | ConvertFrom-Json
if ($ForwardPayload.model_feature_set -ne "full_v2_all_274") {
    throw "Forward used wrong model feature set: $($ForwardPayload.model_feature_set)"
}

Write-Host "DONE"
Write-Host "Model manifest: $ModelManifest"
Write-Host "Forward folder: $ForwardRunDir"
Write-Host "Forward decisions:"
$ForwardPayload.decision_counts_total | ConvertTo-Json -Compress

if (-not $NoOpen) {
    Invoke-Item -LiteralPath $ForwardRunDir
}
