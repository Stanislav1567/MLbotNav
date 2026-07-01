param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainDate = "2026-05-19",
    [string]$TestDate = "2026-05-20",
    [int]$Repeats = 1,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [double]$GoalNetReturnPct = 1.0
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot

if ($Threads -lt 9) {
    Write-Warning "Accelerated mode enforced: Threads raised from $Threads to 9."
    $Threads = 9
}
if ($SearchWorkers -lt 9) {
    Write-Warning "Accelerated mode enforced: SearchWorkers raised from $SearchWorkers to 9."
    $SearchWorkers = 9
}

$env:PYTHONPATH = "src"
$env:OMP_NUM_THREADS = "$Threads"
$env:MKL_NUM_THREADS = "$Threads"
$env:OPENBLAS_NUM_THREADS = "$Threads"
$env:NUMEXPR_NUM_THREADS = "$Threads"

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python venv not found: $python. Run: py -m venv .venv; .\\.venv\\Scripts\\Activate.ps1; pip install -r requirements.txt"
}

& $python -m mlbotnav.daily_long_short_cycle `
  --symbol $Symbol `
  --timeframe $Timeframe `
  --train-start $TrainDate `
  --train-end $TrainDate `
  --test-day $TestDate `
  --test-end-day $TestDate `
  --modes short_only `
  --repeats $Repeats `
  --goal-net-return-pct $GoalNetReturnPct `
  --max-threads $Threads `
  --search-workers $SearchWorkers `
  --run-dir reports/table_canon_current



