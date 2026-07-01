param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainDate = "2026-05-19",
    [string]$TestDate = "2026-05-20",
    [int]$Repeats = 1,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [double]$GoalNetReturnPct = 100.0,
    [double]$Leverage = 10.0,
    [string]$StepLabel = "P7.3",
    [switch]$AllowSubgoalCandidates
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($StepLabel)) {
    throw "StepLabel is required (example: P7.7)"
}

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

function Invoke-Adaptive([string]$SignalMode) {
    $args = @(
        "-m", "mlbotnav.adaptive_auto_train",
        "--symbol", $Symbol,
        "--timeframe", $Timeframe,
        "--train-start", $TrainDate,
        "--train-end", $TrainDate,
        "--test-day", $TestDate,
        "--window-policy", "fixed_1d",
        "--signal-mode", $SignalMode,
        "--repeats", "$Repeats",
        "--goal-net-return-pct", "$GoalNetReturnPct",
        "--min-train-rows", "500",
        "--n-folds", "2",
        "--fee-bps", "10",
        "--slippage-bps", "5",
        "--stop-loss-pct", "0.004",
        "--take-profit-pct", "0.05",
        "--tp-min-factor", "0.7",
        "--cooldown-bars", "20",
        "--notional-usd", "10",
        "--leverage", "$Leverage",
        "--cpu-max-pct", "85",
        "--max-threads", "$Threads",
        "--search-workers", "$SearchWorkers",
        "--speed-profile", "turbo",
        "--temporary-unlock-readiness",
        "--unlock-reason", "P7.3 unified cycle launcher"
    )
    if ($AllowSubgoalCandidates) {
        $args += "--allow-subgoal-candidates"
    }
    & $python @args
}

function Resolve-OosReportFromLongSummary {
    $summaryPattern = "reports/adaptive/long_only/adaptive_loop_${Symbol}_${Timeframe}_${TestDate}_*.json"
    $summaryFile = Get-ChildItem $summaryPattern | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $summaryFile) {
        throw "Long summary not found by pattern: $summaryPattern"
    }
    $summary = Get-Content $summaryFile.FullName -Encoding UTF8 | ConvertFrom-Json
    $oos = $null
    if ($summary.PSObject.Properties.Name -contains "oos_report") {
        $oos = $summary.oos_report
    }
    if (-not $oos -and $summary.PSObject.Properties.Name -contains "history" -and $summary.history.Count -gt 0) {
        $last = $summary.history[$summary.history.Count - 1]
        if ($last.PSObject.Properties.Name -contains "oos_report") {
            $oos = $last.oos_report
        }
    }
    if (-not $oos) {
        throw "OOS report not found inside long summary: $($summaryFile.FullName)"
    }
    if (-not (Test-Path $oos)) {
        throw "Resolved OOS report does not exist: $oos"
    }
    return $oos
}

Write-Host "=== SHORT cycle ==="
Invoke-Adaptive -SignalMode "short_only"

Write-Host "=== LONG cycle ==="
Invoke-Adaptive -SignalMode "long_only"

Write-Host "=== Audits ==="
& $python -m mlbotnav.features_block_audit --config configs/features_block.yaml --out-dir reports/qa_gate
& $python -m mlbotnav.hypothesis_coverage_audit --contour-id short_only --features-config configs/features_block.yaml
& $python -m mlbotnav.hypothesis_coverage_audit --contour-id long_only --features-config configs/features_block.yaml

Write-Host "=== Table convergence + gate ==="
& $python -m mlbotnav.table_canon_pack --symbol $Symbol --timeframe $Timeframe --start-date $TestDate --end-date $TestDate --horizon-bars 1 --layer raw --output-mode stable

$latestOos = Resolve-OosReportFromLongSummary
Write-Host "Resolved OOS report: $latestOos"

& $python -m mlbotnav.table_convergence_5plus --oos-report $latestOos
& $python -m mlbotnav.tz_gate_runner --step $StepLabel --symbol $Symbol --timeframe $Timeframe --start-date $TestDate --end-date $TestDate --horizon-bars 1 --layer raw --oos-report $latestOos
& $python -m mlbotnav.p72_freeze_ready_check

Write-Host "Done: run + audits + convergence + gate completed."



