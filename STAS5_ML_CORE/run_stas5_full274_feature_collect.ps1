param(
  [string]$Day = "2026-04-01",
  [string]$Symbol = "SOLUSDT",
  [string]$Timeframe = "1m",
  [double]$OutcomeLookaheadHours = 48,
  [int]$Stas1RenderGoodLimit = 0,
  [int]$Stas2RenderLimit = 0,
  [switch]$OpenFolder
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
$env:PYTHONPATH = Join-Path $RepoRoot "src"

$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  throw "Python venv not found: $Python"
}

function Get-LatestRunDirByPrefix {
  param(
    [Parameter(Mandatory = $true)][string]$BaseDir,
    [Parameter(Mandatory = $true)][string]$Prefix
  )
  $item = Get-ChildItem -Path $BaseDir -Directory |
    Where-Object { $_.Name -like "$Prefix*" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  if (-not $item) {
    throw "Run folder not found under $BaseDir for prefix $Prefix"
  }
  return $item.FullName
}

$ParsedDay = [datetime]::ParseExact($Day, "yyyy-MM-dd", $null)
$CompactDay = $ParsedDay.ToString("yyyyMMdd")
$RunStamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$RunId = "full274_feature_collect_${CompactDay}_$RunStamp"
$RunRoot = Join-Path $RepoRoot "STAS5_ML_CORE\runs\$RunId"
New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null

$Stas1Label = "stas1_${CompactDay}_full274_collect_$RunStamp"
$Stas2Label = "stas2_${CompactDay}_full274_collect_$RunStamp"

$Stas1Script = Join-Path $RepoRoot "STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1"
$Stas2Script = Join-Path $RepoRoot "STAS2_MARKET_PHASE_REVIEW\run_day.ps1"

Write-Host "== STAS5 FULL274 feature collect =="
Write-Host "Day:      $Day"
Write-Host "Symbol:   $Symbol"
Write-Host "Timeframe:$Timeframe"
Write-Host "RunRoot:  $RunRoot"
Write-Host ""

Write-Host "== 1/5 STAS1 candidates =="
& $Stas1Script `
  -Day $Day `
  -EndDay $Day `
  -Symbol $Symbol `
  -Timeframe $Timeframe `
  -OutcomeLookaheadHours $OutcomeLookaheadHours `
  -RunLabel $Stas1Label `
  -RenderGoodLimit $Stas1RenderGoodLimit

$Stas1Dir = Get-LatestRunDirByPrefix `
  -BaseDir (Join-Path $RepoRoot "STAS1_GOOD_LOW_REVIEW\runs") `
  -Prefix $Stas1Label
Write-Host "STAS1 dir: $Stas1Dir"
Write-Host ""

Write-Host "== 2/5 STAS2 context =="
& $Stas2Script `
  -Day $Day `
  -Symbol $Symbol `
  -Timeframe $Timeframe `
  -RunLabel $Stas2Label `
  -Stas1RunDir $Stas1Dir `
  -RenderLimit $Stas2RenderLimit

$Stas2Dir = Get-LatestRunDirByPrefix `
  -BaseDir (Join-Path $RepoRoot "STAS2_MARKET_PHASE_REVIEW\runs") `
  -Prefix $Stas2Label
Write-Host "STAS2 dir: $Stas2Dir"
Write-Host ""

Write-Host "== 3/5 V2 combo/STAS4/STAS5 features (163) =="
$V2ComboCsv = Join-Path $RunRoot "STAS5_V2_COMBO_FEATURES_$CompactDay.csv"
$V2ComboManifest = Join-Path $RunRoot "STAS5_V2_COMBO_FEATURES_$CompactDay.manifest.json"
& $Python -m mlbotnav.stas5_v2_combo_feature_exporter `
  --stas2-run-dir $Stas2Dir `
  --start-day $Day `
  --end-day $Day `
  --output-csv $V2ComboCsv `
  --manifest-path $V2ComboManifest

Write-Host ""
Write-Host "== 4/5 FULL274 snapshot: V1 111 + V2 163 =="
$V1Csv = Join-Path $RunRoot "STAS5_V1_FEATURES_$CompactDay.csv"
$V1Manifest = Join-Path $RunRoot "STAS5_V1_FEATURES_$CompactDay.manifest.json"
$FullCsv = Join-Path $RunRoot "STAS5_FULL274_FEATURE_SNAPSHOT_$CompactDay.csv"
$FullManifest = Join-Path $RunRoot "STAS5_FULL274_FEATURE_SNAPSHOT_$CompactDay.manifest.json"

@'
import sys
from pathlib import Path
from mlbotnav.stas5_common import read_csv, write_json, rel, load_manifest_feature_columns
from mlbotnav.stas5_feature_snapshot_builder import build_feature_snapshot_from_frames
from mlbotnav.stas5_v2_feature_snapshot_builder import build_v2_feature_snapshot_from_frames

stas2_dir = Path(sys.argv[1])
v2_combo_csv = Path(sys.argv[2])
v2_combo_manifest = Path(sys.argv[3])
v1_csv = Path(sys.argv[4])
v1_manifest = Path(sys.argv[5])
full_csv = Path(sys.argv[6])
full_manifest = Path(sys.argv[7])

old_v1_manifest = Path("STAS5_ML_CORE/artifacts/features/stas5_feature_snapshot_20260501_20260514_v0.manifest.json")
if not old_v1_manifest.exists():
    raise SystemExit(f"old V1 feature contract not found: {old_v1_manifest}")

v1_cols = load_manifest_feature_columns(old_v1_manifest)
stas2 = read_csv(stas2_dir / "STAS2_RECORDS.csv")

v1, man1 = build_feature_snapshot_from_frames(
    stas2=stas2,
    ledger=None,
    source_stas2_run=rel(stas2_dir),
    feature_columns=v1_cols,
)
man1["output_csv"] = rel(v1_csv)
man1["manifest_path"] = rel(v1_manifest)
man1["source_old_v1_manifest_for_column_contract"] = rel(old_v1_manifest)
v1.to_csv(v1_csv, index=False, encoding="utf-8-sig")
write_json(v1_manifest, man1)
if man1["status"] != "PASS" or man1["feature_count"] != 111:
    raise SystemExit(f"V1 snapshot bad: {man1['status']} count={man1['feature_count']} checks={man1.get('checks')}")

v2_combo = read_csv(v2_combo_csv)
v2_cols = load_manifest_feature_columns(v2_combo_manifest)
full, man_full = build_v2_feature_snapshot_from_frames(
    v1_snapshot=v1,
    v2_combo=v2_combo,
    v1_feature_columns=v1_cols,
    v2_feature_columns=v2_cols,
    ledger=None,
    source_v1_snapshot=rel(v1_csv),
    source_v2_combo=rel(v2_combo_csv),
)

# A fresh single-day feature smoke may not have human labels yet.
# Keep these fields neutral so the visual renderer can draw candidates without creating fake training labels.
label_defaults = {
    "human_label": "UNLABELED",
    "label_status": "UNLABELED_VISUAL_ONLY",
    "yellow_x": 0,
    "yellow_x_role": "AUDIT_ONLY",
    "yellow_x_conflict": 0,
}
insert_at = min(5, len(full.columns))
for name, value in reversed(list(label_defaults.items())):
    if name not in full.columns:
        full.insert(insert_at, name, value)

man_full["output_csv"] = rel(full_csv)
man_full["manifest_path"] = rel(full_manifest)
man_full["visual_label_policy"] = (
    "Fresh one-day feature collection may have no manual KEEP/CUT labels; "
    "neutral visual-only label fields are added when absent."
)
full.to_csv(full_csv, index=False, encoding="utf-8-sig")
write_json(full_manifest, man_full)
if man_full["status"] != "PASS" or man_full["feature_count"] != 274:
    raise SystemExit(f"FULL274 snapshot bad: {man_full['status']} count={man_full['feature_count']} checks={man_full.get('checks')}")

print({
    "v1_rows": len(v1),
    "v1_features": man1["feature_count"],
    "full_rows": len(full),
    "full_features": man_full["feature_count"],
    "full_csv": rel(full_csv),
})
'@ | & $Python - $Stas2Dir $V2ComboCsv $V2ComboManifest $V1Csv $V1Manifest $FullCsv $FullManifest

Write-Host ""
Write-Host "== 5/5 STAS5 visual approval graph =="
& $Python -m mlbotnav.stas5_v2_feature_visual_approval `
  --day $Day `
  --snapshot-path $FullCsv `
  --stas2-run-dir $Stas2Dir `
  --out-root $RunRoot

$Png = Join-Path (Join-Path $RunRoot $CompactDay) "STAS5_V2_FEATURE_VISUAL_APPROVAL_$CompactDay.png"
$GraphManifest = Join-Path (Join-Path $RunRoot $CompactDay) "STAS5_V2_FEATURE_VISUAL_APPROVAL_$CompactDay.manifest.json"
if (-not (Test-Path $Png)) {
  throw "PNG not created: $Png"
}

$Full = Get-Content $FullManifest -Raw | ConvertFrom-Json
$Combo = Get-Content $V2ComboManifest -Raw | ConvertFrom-Json
$Graph = Get-Content $GraphManifest -Raw | ConvertFrom-Json
if ($Full.status -ne "PASS" -or [int]$Full.feature_count -ne 274) {
  throw "FULL274 check failed: status=$($Full.status), feature_count=$($Full.feature_count)"
}
if ($Combo.status -ne "PASS" -or [int]$Combo.feature_count -ne 163) {
  throw "V2 combo check failed: status=$($Combo.status), feature_count=$($Combo.feature_count)"
}

$RunSummary = [ordered]@{
  status = "PASS"
  run_id = $RunId
  day = $Day
  symbol = $Symbol
  timeframe = $Timeframe
  run_root = $RunRoot.Replace($RepoRoot + "\", "")
  stas1_run_dir = $Stas1Dir.Replace($RepoRoot + "\", "")
  stas2_run_dir = $Stas2Dir.Replace($RepoRoot + "\", "")
  rows = [int]$Full.rows
  feature_count = [int]$Full.feature_count
  v1_feature_count = [int]$Full.v1_feature_count
  v2_feature_count = [int]$Full.v2_feature_count
  v2_combo_feature_count = [int]$Combo.feature_count
  graph_rows = [int]$Graph.rows
  full_csv = $FullCsv.Replace($RepoRoot + "\", "")
  full_manifest = $FullManifest.Replace($RepoRoot + "\", "")
  graph_png = $Png.Replace($RepoRoot + "\", "")
  graph_manifest = $GraphManifest.Replace($RepoRoot + "\", "")
  training_started = $false
  api_used = $false
  tp_stas3_used = $false
}
$SummaryPath = Join-Path $RunRoot "STAS5_FULL274_FEATURE_COLLECT_SUMMARY.json"
$RunSummary | ConvertTo-Json -Depth 6 | Set-Content -Path $SummaryPath -Encoding UTF8

Write-Host ""
Write-Host "DONE"
Write-Host "Status:       PASS"
Write-Host "Rows:         $($Full.rows)"
Write-Host "Features:     $($Full.feature_count) = V1 $($Full.v1_feature_count) + V2 $($Full.v2_feature_count)"
Write-Host "Run root:     $RunRoot"
Write-Host "Full CSV:     $FullCsv"
Write-Host "Graph PNG:    $Png"
Write-Host "Summary JSON: $SummaryPath"
Write-Host "Training:     NOT STARTED"

if ($OpenFolder) {
  explorer.exe (Split-Path $Png -Parent)
}
