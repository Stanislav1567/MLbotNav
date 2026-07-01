param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainDate = "2026-05-19",
    [string]$TestDate = "2026-05-20",
    [int]$Repeats = 1,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [double]$GoalNetReturnPct = 1.0,
    [double]$Leverage = 10.0,
    [string]$StepLabel = "P17",
    [switch]$AllowSubgoalCandidates
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

function Invoke-Adaptive([string]$SignalMode, [string]$UnlockReason) {
    $args = @(
        "-m", "mlbotnav.adaptive_auto_train",
        "--symbol", $Symbol,
        "--timeframe", $Timeframe,
        "--train-start", $TrainDate,
        "--train-end", $TrainDate,
        "--test-day", $TestDate,
        "--test-end-day", $TestDate,
        "--window-policy", "fixed_1d",
        "--signal-mode", $SignalMode,
        "--use-hypothesis-profile",
        "--contour-id", $SignalMode,
        "--repeats", "$Repeats",
        "--goal-net-return-pct", "$GoalNetReturnPct",
        "--allow-subgoal-candidates",
        "--min-train-rows", "900",
        "--n-folds", "2",
        "--fee-bps", "10",
        "--slippage-bps", "5",
        "--stop-loss-pct", "0.004",
        "--take-profit-pct", "0.05",
        "--tp-min-factor", "0.7",
        "--cooldown-bars", "20",
        "--horizons-grid", "1,2,3,4,6,8,12,20",
        "--p-long-grid", "0.52,0.55,0.58,0.60,0.62,0.65,0.68,0.72",
        "--p-short-grid", "0.45,0.42,0.40,0.38,0.35,0.32,0.30",
        "--min-expected-move-grid", "0.0005,0.001,0.002,0.003,0.005,0.008",
        "--notional-usd", "10",
        "--leverage", "$Leverage",
        "--execution-mode", "exchange_like",
        "--order-type", "market",
        "--cpu-max-pct", "85",
        "--max-threads", "$Threads",
        "--search-workers", "$SearchWorkers",
        "--speed-profile", "turbo",
        "--temporary-unlock-readiness",
        "--unlock-reason", $UnlockReason
    )
    if (-not $AllowSubgoalCandidates) {
        $args = $args | Where-Object { $_ -ne "--allow-subgoal-candidates" }
    }
    & $python @args | Out-Host
}

function Get-LatestFile([string]$Pattern) {
    $f = Get-ChildItem $Pattern | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $f) { throw "File not found by pattern: $Pattern" }
    return $f.FullName
}

Write-Host "=== P17 stable template: long_only ==="
Invoke-Adaptive -SignalMode "long_only" -UnlockReason "P17 stable template long"

Write-Host "=== P17 stable template: short_only ==="
Invoke-Adaptive -SignalMode "short_only" -UnlockReason "P17 stable template short"

$longSummary = Get-LatestFile "reports/adaptive/long_only/adaptive_loop_${Symbol}_${Timeframe}_${TestDate}_*.json"
$shortSummary = Get-LatestFile "reports/adaptive/short_only/adaptive_loop_${Symbol}_${Timeframe}_${TestDate}_*.json"
$longOos = Get-LatestFile "reports/final_review/oos_report_${Symbol}_${Timeframe}_${TestDate}_long_only_*.json"
$shortOos = Get-LatestFile "reports/final_review/oos_report_${Symbol}_${Timeframe}_${TestDate}_short_only_*.json"

Write-Host "=== P17 checks: CSV/XLSX convergence ==="
& $python -m mlbotnav.table_convergence_5plus --oos-report $longOos --run-dir reports/table_canon_current --with-gate | Out-Host
& $python -m mlbotnav.table_convergence_5plus --oos-report $shortOos --run-dir reports/table_canon_current --with-gate | Out-Host

Write-Host "=== P17 checks: hypothesis coverage ==="
& $python -m mlbotnav.hypothesis_coverage_audit --contour-id long_only --summary-path $longSummary | Out-Host
& $python -m mlbotnav.hypothesis_coverage_audit --contour-id short_only --summary-path $shortSummary | Out-Host

Write-Host "=== P17 checks: gate/audit/freeze ==="
& $python -m mlbotnav.features_block_audit | Out-Host
& $python -m mlbotnav.orderbook_source_audit --expect-status active | Out-Host
& $python -m mlbotnav.tz_gate_runner --step $StepLabel --symbol $Symbol --timeframe $Timeframe --start-date $TestDate --end-date $TestDate --horizon-bars 6 --layer core --oos-report $shortOos | Out-Host
& $python -m mlbotnav.p72_freeze_ready_check | Out-Host

Write-Host "=== P17 stable template complete ==="



