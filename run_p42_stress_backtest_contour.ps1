param(
    [string]$OosReportPath = "",
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TestDay = "2026-05-20",
    [ValidateSet("both", "long_only", "short_only")]
    [string]$SignalMode = "short_only",
    [string]$Layer = "raw",
    [string]$SlippageProfiles = "base:5,stress_1:10,stress_2:15",
    [double]$FeeBps = 10.0
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot
$env:PYTHONPATH = "src"

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python venv not found: $python. Run: py -m venv .venv; .\\.venv\\Scripts\\Activate.ps1; pip install -r requirements.txt"
}

if ([string]::IsNullOrWhiteSpace($OosReportPath)) {
    $pattern = "reports/final_review/oos_report_${Symbol}_${Timeframe}_${TestDay}_${SignalMode}_*.json"
    $latest = Get-ChildItem $pattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $latest) {
        throw "oos_report not found by pattern: $pattern ; pass -OosReportPath explicitly."
    }
    $OosReportPath = $latest.FullName
}

Write-Host "P42 stress contour source OOS: $OosReportPath"
& $python -m mlbotnav.stress_backtest_contour `
  --oos-report $OosReportPath `
  --layer $Layer `
  --slippage-profiles $SlippageProfiles `
  --fee-bps $FeeBps | Out-Host

if ($LASTEXITCODE -ne 0) {
    throw "stress_backtest_contour failed with exit code $LASTEXITCODE"
}

Write-Host "P42 stress contour complete"
