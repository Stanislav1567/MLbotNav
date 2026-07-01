param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainDate = "2026-05-19",
    [string]$TestDate = "2026-05-20",
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [double]$GoalNetReturnPct = 100.0,
    [double]$Leverage = 10.0,
    [string]$StepPrefix = "P8",
    [ValidateSet("both", "long_only", "short_only")]
    [string]$Mode = "both",
    [switch]$AllowSubgoalCandidates,
    [switch]$FailFast,
    [switch]$NoFailFast,
    [switch]$PackPerHypothesis
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

# Strict mode by default: if not explicitly provided, enable fail-fast.
if ($NoFailFast) {
    $FailFast = $false
} elseif (-not $PSBoundParameters.ContainsKey("FailFast")) {
    $FailFast = $true
}

function Invoke-PyJson([string[]]$CmdArgs) {
    if (-not $CmdArgs -or $CmdArgs.Count -eq 0) {
        throw "Invoke-PyJson called with empty args"
    }
    $out = & $python @CmdArgs
    $txt = ($out | Out-String).Trim()
    if (-not $txt) { return $null }
    $lines = $txt -split "`r?`n" | Where-Object { $_.Trim() -ne "" }
    $last = $lines[-1]
    try { return ($last | ConvertFrom-Json) } catch { return $null }
}

function Invoke-PythonStrict([string[]]$CmdArgs, [string]$Label) {
    if (-not $CmdArgs -or $CmdArgs.Count -eq 0) {
        throw "Invoke-PythonStrict called with empty args for label=$Label"
    }

    $merged = & $python @CmdArgs 2>&1
    $code = $LASTEXITCODE
    $stdoutLines = @()
    $stderrLines = @()
    foreach ($x in @($merged)) {
        if ($x -is [System.Management.Automation.ErrorRecord]) {
            $msg = $null
            if ($x.TargetObject) { $msg = [string]$x.TargetObject }
            if ([string]::IsNullOrWhiteSpace($msg)) { $msg = [string]$x.Exception.Message }
            if ([string]::IsNullOrWhiteSpace($msg)) { $msg = [string]$x.ToString() }
            $stderrLines += $msg
            Write-Host $msg
        }
        else {
            $line = [string]$x
            $stdoutLines += $line
            Write-Host $line
        }
    }

    $script:__last_exit_code = $code
    $script:__last_stdout_tail = (($stdoutLines | Select-Object -Last 40) -join "`n")
    $script:__last_stderr_tail = (($stderrLines | Select-Object -Last 40) -join "`n")

    if ($code -ne 0) {
        throw "[$Label] python command failed with exit code $code"
    }
}

function Assert-PassReport([string]$Path, [string]$Label) {
    if (-not (Test-Path $Path)) {
        throw "[$Label] report not found: $Path"
    }
    $obj = Get-Content $Path -Encoding UTF8 | ConvertFrom-Json
    if (-not $obj.status) {
        throw "[$Label] no status field: $Path"
    }
    if ($obj.status -ne "PASS") {
        throw "[$Label] status is $($obj.status): $Path"
    }
}

function Get-LatestReport([string]$Pattern) {
    $f = Get-ChildItem $Pattern | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $f) { throw "Report not found by pattern: $Pattern" }
    return $f.FullName
}

function Get-ActiveHypotheses([string]$Mode) {
    $script = @"
from pathlib import Path
from mlbotnav.hypothesis_registry import load_backlog_registry
root = Path(r'C:\Users\007\Desktop\MLbotNav')
reg = load_backlog_registry(project_root=root, features_config='configs/features_block.yaml', run_signal_mode='$Mode')
print('\n'.join([x.get('name','') for x in reg.get('active_items',[]) if x.get('name')]))
"@
    $names = & $python -c $script
    return @($names | Where-Object { $_ -and $_.Trim() -ne "" } | ForEach-Object { $_.Trim() })
}

function Resolve-OosFromSummary([string]$Mode, [switch]$AllowNoOos) {
    $pattern = "reports/adaptive/$Mode/adaptive_loop_${Symbol}_${Timeframe}_${TestDate}_*.json"
    $summary = Get-ChildItem $pattern | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $summary) {
        if ($AllowNoOos) {
            return @{
                summary = $null
                oos = $null
                state = "summary_missing"
                reason = "summary not found by pattern: $pattern"
            }
        }
        throw "Summary not found for $Mode by $pattern"
    }
    $obj = Get-Content $summary.FullName -Encoding UTF8 | ConvertFrom-Json
    $oos = $null
    if ($obj.PSObject.Properties.Name -contains "oos_report") { $oos = $obj.oos_report }
    if (-not $oos -and $obj.PSObject.Properties.Name -contains "history" -and $obj.history.Count -gt 0) {
        $last = $obj.history[$obj.history.Count - 1]
        if ($last.PSObject.Properties.Name -contains "oos_report") { $oos = $last.oos_report }
    }
    if (-not $oos) {
        if ($AllowNoOos) {
            return @{
                summary = $summary.FullName
                oos = $null
                state = "no_oos_report"
                reason = "oos_report not found in summary: $($summary.FullName)"
            }
        }
        throw "oos_report not found in summary: $($summary.FullName)"
    }
    if (-not (Test-Path $oos)) {
        if ($AllowNoOos) {
            return @{
                summary = $summary.FullName
                oos = $null
                state = "oos_path_missing"
                reason = "oos_report path not found: $oos"
            }
        }
        throw "oos_report path not found: $oos"
    }
    return @{
        summary = $summary.FullName
        oos = $oos
        state = "ok"
        reason = $null
    }
}

function Try-ResolveSummaryPath([string]$Mode) {
    $pattern = "reports/adaptive/$Mode/adaptive_loop_${Symbol}_${Timeframe}_${TestDate}_*.json"
    $summary = Get-ChildItem $pattern | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($summary) { return $summary.FullName }
    return $null
}

function Get-FailureClass([string]$Stage) {
    switch ($Stage) {
        "adaptive_auto_train" { return "MODEL_FAIL" }
        "resolve_oos_report" { return "MODEL_FAIL" }
        "table_canon_pack" { return "CHAIN_FAIL" }
        "table_convergence_5plus" { return "CHAIN_FAIL" }
        "tz_gate_runner" { return "GATE_FAIL" }
        "p72_freeze_ready_check" { return "GATE_FAIL" }
        default { return "CHAIN_FAIL" }
    }
}

$windowsCheck = @(
    @{train=$TrainDate; test=$TestDate}
)
foreach ($w in $windowsCheck) {
    if ([datetime]::Parse($w.test) -ne ([datetime]::Parse($w.train).AddDays(1))) {
        throw "Window must be 1D->next1D. Got train=$($w.train), test=$($w.test)"
    }
}

$reportRows = @()
$failedRows = @()
$modes = if ($Mode -eq "both") { @("long_only", "short_only") } else { @($Mode) }
foreach ($mode in $modes) {
    $hypotheses = Get-ActiveHypotheses -Mode $mode
    if (-not $hypotheses -or $hypotheses.Count -eq 0) {
        throw "No active hypotheses resolved for mode=$mode"
    }
    Write-Host "=== COVERAGE MODE: $mode | active_count=$($hypotheses.Count) ==="

    if (-not $PackPerHypothesis) {
        Write-Host "[PACK_ONCE][$mode] table_canon_pack stable"
        $packCmdMode = @(
            "-m", "mlbotnav.table_canon_pack",
            "--symbol", $Symbol,
            "--timeframe", $Timeframe,
            "--start-date", $TestDate,
            "--end-date", $TestDate,
            "--horizon-bars", "1",
            "--layer", "raw",
            "--output-mode", "stable"
        )
        Invoke-PythonStrict -CmdArgs $packCmdMode -Label "PACK_ONCE $mode table_canon_pack"
    }

    $i = 0
    foreach ($h in $hypotheses) {
        $i++
        $step = "$StepPrefix.$mode.$i"
        Write-Host "[$step] hypothesis=$h"
        $stepSummaryPath = $null
        $stepOosPath = $null
        $stepConvPath = $null
        $stepGatePath = $null
        $stepFreezePath = $null
        $stepFailedStage = $null
        $stepFailedExitCode = $null
        $stepStderrTail = $null
        try {
            $stepFailedStage = "adaptive_auto_train"
            $cmd = @(
                "-m", "mlbotnav.adaptive_auto_train",
                "--symbol", $Symbol,
                "--timeframe", $Timeframe,
                "--train-start", $TrainDate,
                "--train-end", $TrainDate,
                "--test-day", $TestDate,
                "--window-policy", "fixed_1d",
                "--signal-mode", $mode,
                "--repeats", "1",
                "--trend-filter", $h,
                "--min-abs-ema-gap", "0.0",
                "--disable-hypothesis-profile",
                "--disable-backlog-active-append",
                "--goal-net-return-pct", "$GoalNetReturnPct",
                "--min-train-rows", "500",
                "--n-folds", "2",
                "--horizons-grid", "1,2,3,4,6,8,12,20",
                "--p-long-grid", "0.50,0.52,0.54,0.56,0.58,0.60",
                "--p-short-grid", "0.50,0.48,0.46,0.44,0.42,0.40",
                "--min-expected-move-grid", "0.0,0.0005,0.001,0.002,0.003,0.005",
                "--fee-bps", "10",
                "--slippage-bps", "5",
                "--stop-loss-pct", "0.004",
                "--take-profit-pct", "0.05",
                "--tp-min-factor", "0.7",
                "--cooldown-bars", "0",
                "--notional-usd", "10",
                "--leverage", "$Leverage",
                "--cpu-max-pct", "85",
                "--max-threads", "$Threads",
                "--search-workers", "$SearchWorkers",
                "--speed-profile", "turbo",
                "--temporary-unlock-readiness",
                "--unlock-reason", "$step full coverage"
            )
            if ($AllowSubgoalCandidates) { $cmd += "--allow-subgoal-candidates" }
            Invoke-PythonStrict -CmdArgs $cmd -Label "$step adaptive_auto_train"
            $stepSummaryPath = Try-ResolveSummaryPath -Mode $mode
            $stepFailedExitCode = $script:__last_exit_code
            $stepStderrTail = $script:__last_stderr_tail

            if ($PackPerHypothesis) {
                $stepFailedStage = "table_canon_pack"
                $packCmd = @(
                    "-m", "mlbotnav.table_canon_pack",
                    "--symbol", $Symbol,
                    "--timeframe", $Timeframe,
                    "--start-date", $TestDate,
                    "--end-date", $TestDate,
                    "--horizon-bars", "1",
                    "--layer", "raw",
                    "--output-mode", "stable"
                )
                Invoke-PythonStrict -CmdArgs $packCmd -Label "$step table_canon_pack"
                $stepFailedExitCode = $script:__last_exit_code
                $stepStderrTail = $script:__last_stderr_tail
            }

            $stepFailedStage = "resolve_oos_report"
            $resolved = Resolve-OosFromSummary -Mode $mode -AllowNoOos
            $stepSummaryPath = $resolved.summary
            $stepOosPath = $resolved.oos
            if ($resolved.state -ne "ok") {
                $skipReason = "[$step] SKIP_NO_OOS: $($resolved.reason)"
                Write-Host $skipReason
                $reportRows += @{
                    step = $step
                    mode = $mode
                    hypothesis = $h
                    summary_path = $stepSummaryPath
                    oos_report = $stepOosPath
                    convergence_report = $null
                    gate_report = $null
                    freeze_report = $null
                    status = "SKIP_NO_OOS"
                    error = $resolved.reason
                    failed_stage = "resolve_oos_report"
                    fail_class = "MODEL_FAIL"
                    exit_code = $null
                    stderr_tail = $null
                }
                continue
            }

            $stepFailedStage = "table_convergence_5plus"
            Invoke-PythonStrict -CmdArgs @("-m", "mlbotnav.table_convergence_5plus", "--oos-report", $stepOosPath) -Label "$step table_convergence"
            $stepConvPath = Get-LatestReport -Pattern "reports/qa_gate/table_convergence_5plus_*.json"
            Assert-PassReport -Path $stepConvPath -Label "$step table_convergence"
            $stepFailedExitCode = $script:__last_exit_code
            $stepStderrTail = $script:__last_stderr_tail

            $stepFailedStage = "tz_gate_runner"
            Invoke-PythonStrict -CmdArgs @("-m", "mlbotnav.tz_gate_runner", "--step", $step, "--symbol", $Symbol, "--timeframe", $Timeframe, "--start-date", $TestDate, "--end-date", $TestDate, "--horizon-bars", "1", "--layer", "raw", "--oos-report", $stepOosPath) -Label "$step tz_gate"
            $stepGatePath = Get-LatestReport -Pattern "reports/qa_gate/tz_gate_*.json"
            Assert-PassReport -Path $stepGatePath -Label "$step tz_gate"
            $stepFailedExitCode = $script:__last_exit_code
            $stepStderrTail = $script:__last_stderr_tail

            $stepFailedStage = "p72_freeze_ready_check"
            Invoke-PythonStrict -CmdArgs @("-m", "mlbotnav.p72_freeze_ready_check") -Label "$step freeze"
            $stepFreezePath = Get-LatestReport -Pattern "reports/qa_gate/p72_freeze_ready_*.json"
            Assert-PassReport -Path $stepFreezePath -Label "$step freeze"
            $stepFailedExitCode = $script:__last_exit_code
            $stepStderrTail = $script:__last_stderr_tail

            $reportRows += @{
                step = $step
                mode = $mode
                hypothesis = $h
                summary_path = $stepSummaryPath
                oos_report = $stepOosPath
                convergence_report = $stepConvPath
                gate_report = $stepGatePath
                freeze_report = $stepFreezePath
                status = "PASS"
                error = $null
                failed_stage = $null
                exit_code = $null
                stderr_tail = $null
            }
        } catch {
            $err = $_.Exception.Message
            Write-Host "[$step] FAIL: $err"
            if (-not $stepSummaryPath) {
                $stepSummaryPath = Try-ResolveSummaryPath -Mode $mode
            }
            $row = @{
                step = $step
                mode = $mode
                hypothesis = $h
                summary_path = $stepSummaryPath
                oos_report = $stepOosPath
                convergence_report = $stepConvPath
                gate_report = $stepGatePath
                freeze_report = $stepFreezePath
                status = (Get-FailureClass -Stage $stepFailedStage)
                error = $err
                failed_stage = $stepFailedStage
                fail_class = (Get-FailureClass -Stage $stepFailedStage)
                exit_code = $stepFailedExitCode
                stderr_tail = $stepStderrTail
            }
            $reportRows += $row
            $failedRows += $row
            if ($FailFast) { throw }
            continue
        }
    }
}

$utcTag = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outDir = "reports\qa_gate"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$outPath = Join-Path $outDir "p8_full_coverage_${Symbol}_${Timeframe}_${TrainDate}_to_${TestDate}_$utcTag.json"
$payload = @{
    status = $(if ($failedRows.Count -eq 0) { "PASS" } else { "PARTIAL_FAIL" })
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    symbol = $Symbol
    timeframe = $Timeframe
    train_date = $TrainDate
    test_date = $TestDate
    fail_count = $failedRows.Count
    pass_count = @($reportRows | Where-Object { $_.status -eq "PASS" }).Count
    skip_count = @($reportRows | Where-Object { $_.status -like "SKIP_*" }).Count
    rows = $reportRows
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $outPath
Write-Host "Coverage report: $outPath"
if ($failedRows.Count -gt 0) {
    Write-Host "Coverage completed with FAIL items: $($failedRows.Count)"
    exit 2
}



