param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TestDate = "2026-05-20",
    [int]$HorizonBars = 6,
    [string]$Layer = "core",
    [string]$StepLabel = "P22"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot

$env:PYTHONPATH = "src"
$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python venv not found: $python. Run: py -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}

function Get-LatestOos([string]$symbol, [string]$tf, [string]$testDate) {
    $pattern = "reports\\final_review\\oos_report_${symbol}_${tf}_${testDate}_*.json"
    $f = Get-ChildItem $pattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $f) {
        throw "OOS report not found by pattern: $pattern"
    }
    return $f.FullName
}

Write-Host "=== P22 table-chain: table_canon_pack (stable) ==="
& $python -m mlbotnav.table_canon_pack `
  --symbol $Symbol `
  --timeframe $Timeframe `
  --start-date $TestDate `
  --end-date $TestDate `
  --horizon-bars $HorizonBars `
  --layer $Layer `
  --output-mode stable | Out-Host

$oos = Get-LatestOos -symbol $Symbol -tf $Timeframe -testDate $TestDate
Write-Host "Using OOS: $oos"

Write-Host "=== P22 table-chain: table_convergence_5plus ==="
& $python -m mlbotnav.table_convergence_5plus `
  --oos-report $oos `
  --run-dir reports/table_canon_current `
  --with-gate | Out-Host

Write-Host "=== P22 table-chain: audit_table_chain ==="
& $python -m mlbotnav.audit_table_chain `
  --run-dir reports/table_canon_current `
  --require-trades | Out-Host

Write-Host "=== P22 gate/freeze checks ==="
& $python -m mlbotnav.features_block_audit | Out-Host
& $python -m mlbotnav.orderbook_source_audit --expect-status active | Out-Host
& $python -m mlbotnav.tz_gate_runner --step $StepLabel --symbol $Symbol --timeframe $Timeframe --start-date $TestDate --end-date $TestDate --horizon-bars $HorizonBars --layer $Layer --oos-report $oos | Out-Host
& $python -m mlbotnav.p72_freeze_ready_check | Out-Host

Write-Host "=== P22 table-chain complete ==="



