param(
    [ValidateSet("long_only", "short_only")]
    [string]$Mode = "short_only",
    [int]$Repeats = 1,
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainDate = "2026-05-19",
    [string]$TestDate = "2026-05-20",
    [string]$TrainStart = "",
    [string]$TrainEnd = "",
    [string]$TestStart = "",
    [string]$TestEnd = "",
    [ValidateSet("fixed_1d", "multiday")]
    [string]$WindowPolicy = "fixed_1d",
    [double]$GoalNetReturnPct = 1.0,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [int]$OptunaTrials = 1,
    [int]$OptunaTimeoutSec = 60,
    [string]$TrendFilter = "",
    [double]$MinAbsEmaGap = -1.0,
    [double]$MinTpReachProb = -1.0,
    [string]$HorizonsGrid = "",
    [string]$MinExpectedMoveGrid = "",
    [string]$PShortGrid = "",
    [string]$CalibrationMatrixPath = "",
    [switch]$EnableHypothesisProfile,
    [ValidateSet("A", "B", "C", "auto")]
    [string]$OptunaStage = "B",
    [ValidateSet("off", "on")]
    [string]$OptunaMlSignalBackend = "off",
    [switch]$UseTemporaryUnlock,
    [switch]$CpuRampDisable,
    [switch]$SkipFast9Guard,
    [switch]$SkipLock,
    [switch]$SkipPostAudit,
    [switch]$DryRun
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

# Canonical env bootstrap (loads .env and OPTUNA_STORAGE_URL)
$envBootstrap = Join-Path $ProjectRoot "set_mlbotnav_env.ps1"
if (-not (Test-Path $envBootstrap)) { throw "Env bootstrap not found: $envBootstrap" }
& $envBootstrap -Threads $Threads | Out-Host

if (-not [string]::IsNullOrWhiteSpace($CalibrationMatrixPath)) {
    $matrixPath = $CalibrationMatrixPath
    if (-not [System.IO.Path]::IsPathRooted($matrixPath)) {
        $matrixPath = Join-Path $ProjectRoot $matrixPath
    }
    $matrixResolved = (Resolve-Path -LiteralPath $matrixPath).Path
    $env:MLBOTNAV_CALIBRATION_MATRIX_PATH = $matrixResolved
} else {
    Remove-Item Env:MLBOTNAV_CALIBRATION_MATRIX_PATH -ErrorAction SilentlyContinue
}

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Python venv not found: $python" }
$runLedgerCsv = Join-Path $ProjectRoot "reports\qa_gate\optuna_single_pass_runs.csv"

$trainStartEff = if (-not [string]::IsNullOrWhiteSpace($TrainStart)) { $TrainStart } else { $TrainDate }
$trainEndEff = if (-not [string]::IsNullOrWhiteSpace($TrainEnd)) { $TrainEnd } else { $TrainDate }
$testStartEff = if (-not [string]::IsNullOrWhiteSpace($TestStart)) { $TestStart } else { $TestDate }
$testEndEff = if (-not [string]::IsNullOrWhiteSpace($TestEnd)) { $TestEnd } else { $TestDate }

function Parse-LastJsonObject([string]$text) {
    $lines = ($text -split "`r?`n")
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = $lines[$i].Trim()
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { return ($line | ConvertFrom-Json) } catch {}
    }
    return $null
}

function Get-LatestPipelineReportPath(
    [string]$ProjectRootPath,
    [datetime]$SinceUtc,
    [string]$SymbolName,
    [string]$Tf
) {
    $pipelineDir = Join-Path $ProjectRootPath "reports\pipeline"
    if (-not (Test-Path $pipelineDir)) { return $null }
    $pattern = "optuna_search_candidate_${SymbolName}_${Tf}_*.json"
    $candidates = Get-ChildItem -Path $pipelineDir -Filter $pattern -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTimeUtc -ge $SinceUtc } |
        Sort-Object LastWriteTimeUtc -Descending
    if ($null -eq $candidates -or $candidates.Count -eq 0) { return $null }
    return $candidates[0].FullName
}

$taskTs = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$taskId = "P185-OPTUNA-SINGLE-PASS-$Mode-$taskTs"
$claimArgs = @{
    TaskId = $taskId
    OwnerChat = "this_chat"
    Kind = "runtime"
    Scope = "p185 optuna single-pass launcher"
    Note = "launcher run"
}

$cmd = @(
    "-m", "mlbotnav.adaptive_auto_train",
    "--symbol", $Symbol,
    "--timeframe", $Timeframe,
    "--train-start", $trainStartEff,
    "--train-end", $trainEndEff,
    "--test-day", $testStartEff,
    "--test-end-day", $testEndEff,
    "--window-policy", $WindowPolicy,
    "--signal-mode", $Mode,
    "--repeats", "$Repeats",
    "--goal-net-return-pct", "$GoalNetReturnPct",
    "--max-threads", "$Threads",
    "--search-workers", "$SearchWorkers",
    "--search-engine", "optuna",
    "--optuna-stage", $OptunaStage,
    "--optuna-ml-signal-backend", $OptunaMlSignalBackend,
    "--optuna-n-trials-override", "$OptunaTrials",
    "--optuna-timeout-sec-override", "$OptunaTimeoutSec",
    "--allow-subgoal-candidates",
    "--disable-backlog-active-append",
    "--enforce-repeats-effective-match",
    "--preflight-policy", "configs/preflight_policy.yaml"
)

if (-not $EnableHypothesisProfile) {
    $cmd += "--disable-hypothesis-profile"
}

if (-not [string]::IsNullOrWhiteSpace($MinExpectedMoveGrid)) {
    $cmd += @("--min-expected-move-grid", $MinExpectedMoveGrid)
}
if (-not [string]::IsNullOrWhiteSpace($TrendFilter)) {
    $cmd += @("--trend-filter", $TrendFilter)
}
if ($MinAbsEmaGap -ge 0.0) {
    $cmd += @("--min-abs-ema-gap", "$MinAbsEmaGap")
}
if ($MinTpReachProb -ge 0.0) {
    $cmd += @("--min-tp-reach-prob", "$MinTpReachProb")
}
if (-not [string]::IsNullOrWhiteSpace($HorizonsGrid)) {
    $cmd += @("--horizons-grid", $HorizonsGrid)
}
if (-not [string]::IsNullOrWhiteSpace($PShortGrid)) {
    $cmd += @("--p-short-grid", $PShortGrid)
}

if ($UseTemporaryUnlock) {
    $cmd += @("--temporary-unlock-readiness", "--unlock-reason", "P185 single-pass launcher")
}
if ($CpuRampDisable) {
    $cmd += @("--cpu-ramp-disable")
}

Write-Host "=== P185 launcher ===" -ForegroundColor Cyan
Write-Host "ProjectRoot: $ProjectRoot"
Write-Host "Mode: $Mode"
if ($env:MLBOTNAV_CALIBRATION_MATRIX_PATH) {
    Write-Host "CalibrationMatrix: $($env:MLBOTNAV_CALIBRATION_MATRIX_PATH)"
}
Write-Host "Command: $python $($cmd -join ' ')"

if ($DryRun) {
    Write-Host "DryRun: command not executed." -ForegroundColor Yellow
    exit 0
}

$claimed = $false
try {
    if (-not $SkipLock) {
        & "$ProjectRoot\scripts\coord_claim.ps1" @claimArgs | Out-Host
        $claimed = $true
    }

    $runStartedUtc = (Get-Date).ToUniversalTime()
    $raw = & $python @cmd 2>&1 | Out-String
    $raw | Out-Host

    $tailObj = Parse-LastJsonObject $raw
    if ($null -ne $tailObj) {
        $tailStatus = ""
        if ($null -ne $tailObj.status) {
            $tailStatus = [string]$tailObj.status
        }
        if ($tailStatus -eq "invalid_repeats_effective_policy") {
            $details = ""
            if ($null -ne $tailObj.error) {
                $details = [string]$tailObj.error
            }
            throw "Adaptive run blocked by repeats-effective policy. $details"
        }
    }

    $summaryPath = $null
    $m = [regex]::Matches($raw, '"summary_path"\s*:\s*"([^"]+)"')
    if ($m.Count -gt 0) {
        $summaryPath = [string]$m[$m.Count - 1].Groups[1].Value
    }

    if ([string]::IsNullOrWhiteSpace($summaryPath)) {
        throw "Cannot parse summary_path from adaptive output."
    }
    if (-not (Test-Path $summaryPath)) {
        throw "Summary path not found: $summaryPath"
    }

    $obj = Get-Content -Path $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $bestOos = 0.0
    $bestTrades = 0
    $resultStatus = "search_failed"
    if ($null -ne $obj.best_oos) {
        if ($null -ne $obj.best_oos.oos_net_return_pct -and "$($obj.best_oos.oos_net_return_pct)" -ne "") {
            $bestOos = [double]$obj.best_oos.oos_net_return_pct
        }
        if ($null -ne $obj.best_oos.oos_trades -and "$($obj.best_oos.oos_trades)" -ne "") {
            $bestTrades = [int]$obj.best_oos.oos_trades
        }
        if ($null -ne $obj.best_oos.status -and [string]::IsNullOrWhiteSpace([string]$obj.best_oos.status) -eq $false) {
            $resultStatus = [string]$obj.best_oos.status
        }
    } elseif ($null -ne $obj.status) {
        $statusRaw = [string]$obj.status
        if ($statusRaw -eq "train_failed") {
            $resultStatus = "train_failed"
        } elseif ($statusRaw -eq "search_failed" -or $statusRaw -eq "blocked_readiness") {
            $resultStatus = "search_failed"
        }
    }
    $bestOosInvariant = ([double]$bestOos).ToString("0.################", [System.Globalization.CultureInfo]::InvariantCulture)

    $guardEligible = ($resultStatus -ne "search_failed" -and $resultStatus -ne "train_failed")
    if ((-not $SkipFast9Guard) -and $SearchWorkers -ge 9 -and $guardEligible) {
        $pipelinePath = Get-LatestPipelineReportPath -ProjectRootPath $ProjectRoot -SinceUtc $runStartedUtc.AddSeconds(-10) -SymbolName $Symbol -Tf $Timeframe
        if ([string]::IsNullOrWhiteSpace($pipelinePath) -or (-not (Test-Path $pipelinePath))) {
            throw "FAST9 guard: pipeline report for this run not found (symbol=$Symbol tf=$Timeframe since=$($runStartedUtc.ToString('o')))."
        }
        $pipelineObj = Get-Content -Path $pipelinePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $storageScheme = [string]$pipelineObj.storage_parallel_guard.storage_scheme
        $workersUsed = [int]$pipelineObj.workers_used
        $forcedSingle = [bool]$pipelineObj.storage_parallel_guard.forced_single_worker
        if ($storageScheme -ne "postgresql") {
            throw "FAST9 guard: storage is not postgresql (actual='$storageScheme') in $pipelinePath"
        }
        if ($forcedSingle) {
            throw "FAST9 guard: forced_single_worker=true in $pipelinePath"
        }
        if ($workersUsed -lt 9) {
            throw "FAST9 guard: workers_used=$workersUsed (<9) in $pipelinePath"
        }
    }

    $out = [ordered]@{
        status = "OK"
        task_id = $taskId
        summary_path = $summaryPath
        repeats_requested = [int]$obj.repeats_requested
        repeats_effective = [int]$obj.repeats_effective
        repeats_effective_mismatch = [bool]$obj.repeats_effective_mismatch
        signal_mode = [string]$obj.signal_mode
        run_utc = [string]$obj.run_utc
        result_status = $resultStatus
        oos_net_return_pct = $bestOosInvariant
        oos_trades = $bestTrades
    }

    $ledgerDir = Split-Path -Parent $runLedgerCsv
    if (-not (Test-Path $ledgerDir)) {
        New-Item -ItemType Directory -Path $ledgerDir -Force | Out-Null
    }
    $ledgerRow = [pscustomobject]@{
        ts_utc = (Get-Date).ToUniversalTime().ToString("o")
        task_id = $taskId
        mode = $Mode
        symbol = $Symbol
        timeframe = $Timeframe
        train_date = $TrainDate
        test_date = $TestDate
        optuna_stage = $OptunaStage
        repeats_requested = [int]$obj.repeats_requested
        repeats_effective = [int]$obj.repeats_effective
        repeats_effective_mismatch = [bool]$obj.repeats_effective_mismatch
        result_status = $resultStatus
        oos_net_return_pct = $bestOosInvariant
        oos_trades = $bestTrades
        summary_path = $summaryPath
    }
    if (Test-Path $runLedgerCsv) {
        $ledgerRow | Export-Csv -Path $runLedgerCsv -NoTypeInformation -Append -Encoding UTF8
    } else {
        $ledgerRow | Export-Csv -Path $runLedgerCsv -NoTypeInformation -Encoding UTF8
    }
    $ledgerAuditPath = $null
    $textGuardPath = $null
    if (-not $SkipPostAudit) {
        $rawLedgerAudit = & $python -m mlbotnav.optuna_single_pass_ledger_audit 2>&1 | Out-String
        $rawLedgerAudit | Out-Host
        $ledgerAuditObj = Parse-LastJsonObject $rawLedgerAudit
        if ($null -eq $ledgerAuditObj) {
            throw "Cannot parse ledger audit output."
        }
        if ([string]$ledgerAuditObj.status -ne "PASS") {
            throw "Ledger audit failed: status=$($ledgerAuditObj.status) report_path=$($ledgerAuditObj.report_path)"
        }
        $ledgerAuditPath = [string]$ledgerAuditObj.report_path

        $rawTextGuard = & $python -m mlbotnav.text_guard 2>&1 | Out-String
        $rawTextGuard | Out-Host
        $textGuardObj = Parse-LastJsonObject $rawTextGuard
        if ($null -eq $textGuardObj) {
            throw "Cannot parse text_guard output."
        }
        if ([string]$textGuardObj.status -ne "PASS") {
            throw "text_guard failed: status=$($textGuardObj.status) report_path=$($textGuardObj.report_path)"
        }
        $textGuardPath = [string]$textGuardObj.report_path
    }

    $out["run_ledger_csv"] = $runLedgerCsv
    $out["post_audit_enabled"] = (-not $SkipPostAudit)
    $out["ledger_audit_report_path"] = $ledgerAuditPath
    $out["text_guard_report_path"] = $textGuardPath
    $out | ConvertTo-Json -Depth 6 | Out-Host
}
finally {
    if ($claimed) {
        & "$ProjectRoot\scripts\coord_release.ps1" -TaskId $taskId -OwnerChat "this_chat" -Kind runtime -Note "p185 launcher done" | Out-Host
    }
}
