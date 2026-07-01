param(
    [ValidateSet("long_only", "short_only")]
    [string]$Mode = "short_only",
    [int]$Repeats = 1,
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [ValidateSet("raw", "core")]
    [string]$DataLayer = "raw",
    [string]$TrainDate = "2026-05-19",
    [string]$TestDate = "2026-05-20",
    [Alias("TrainStartDate")]
    [string]$TrainStart = "",
    [Alias("TrainEndDate")]
    [string]$TrainEnd = "",
    [Alias("TestStartDate")]
    [string]$TestStart = "",
    [Alias("TestEndDate", "TestEndDay")]
    [string]$TestEnd = "",
    [ValidateSet("fixed_1d", "multiday")]
    [string]$WindowPolicy = "fixed_1d",
    [double]$GoalNetReturnPct = 1.0,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [int]$OptunaTrials = 80,
    [int]$OptunaTimeoutSec = 1200,
    [string]$TrendFilter = "",
    [double]$MinAbsEmaGap = -1.0,
    [double]$MinTpReachProb = -1.0,
    [double]$StopLossPct = -1.0,
    [double]$TakeProfitPct = -1.0,
    [double]$TpMinFactor = -1.0,
    [int]$CooldownBars = -1,
    [string]$HorizonsGrid = "",
    [string]$MinExpectedMoveGrid = "",
    [string]$NotionalUsdGrid = "",
    [string]$PLongGrid = "",
    [string]$PShortGrid = "",
    [int]$MinCandidateTrades = 1,
    [string]$CalibrationMatrixPath = "",
    [switch]$EnableHypothesisProfile,
    [ValidateSet("A", "B", "C", "auto")]
    [string]$OptunaStage = "C",
    [ValidateSet("off", "on")]
    [string]$OptunaMlSignalBackend = "off",
    [ValidateSet("auto", "wide", "medium", "narrow")]
    [string]$CalibrationGridPreset = "auto",
    [ValidateSet("auto", "on", "off")]
    [string]$ForceProfileEdgeCoverage = "auto",
    [switch]$DisableTimeoutExit,
    [switch]$UseTemporaryUnlock,
    [int]$ProcessWorkers = 2,
    [int]$SearchWorkersPerProcess = 0,
    [switch]$SharedOptunaStudy,
    [string]$SharedStudyId = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$AptunaRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $AptunaRoot
Set-Location $ProjectRoot

# Ensure child workers always resolve local package imports even when launcher is
# started from a fresh PowerShell process without inherited env.
$env:PYTHONPATH = "src"

$calibrationMatrixResolved = ""
if (-not [string]::IsNullOrWhiteSpace($CalibrationMatrixPath)) {
    $candidate = if ([System.IO.Path]::IsPathRooted($CalibrationMatrixPath)) {
        [System.IO.Path]::GetFullPath($CalibrationMatrixPath)
    } else {
        [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $CalibrationMatrixPath))
    }
    if (-not (Test-Path $candidate)) {
        throw "Calibration matrix not found: $candidate"
    }
    $calibrationMatrixResolved = $candidate
    # optuna_space.load_calibration_matrix reads this env override.
    $env:MLBOTNAV_CALIBRATION_MATRIX_PATH = $calibrationMatrixResolved
}

if ($ProcessWorkers -lt 1) {
    throw "ProcessWorkers must be >= 1 for process-pool mode."
}

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python venv not found: $python"
}

$trainStartEff = if (-not [string]::IsNullOrWhiteSpace($TrainStart)) { $TrainStart } else { $TrainDate }
$trainEndEff = if (-not [string]::IsNullOrWhiteSpace($TrainEnd)) { $TrainEnd } else { $TrainDate }
$testStartEff = if (-not [string]::IsNullOrWhiteSpace($TestStart)) { $TestStart } else { $TestDate }
$testEndEff = if (-not [string]::IsNullOrWhiteSpace($TestEnd)) { $TestEnd } else { $TestDate }

$threadsPerProc = [Math]::Max(1, [int][Math]::Floor([double]$Threads / [double]$ProcessWorkers))
$trialsPerProc = [Math]::Max(1, [int][Math]::Ceiling([double]$OptunaTrials / [double]$ProcessWorkers))
$searchWorkersRequested = [Math]::Max(1, [int]$SearchWorkers)
$searchWorkersEff = if ($SearchWorkersPerProcess -gt 0) {
    [Math]::Min($SearchWorkersPerProcess, $threadsPerProc)
} else {
    $searchWorkersFromTotal = [Math]::Max(1, [int][Math]::Ceiling([double]$searchWorkersRequested / [double]$ProcessWorkers))
    [Math]::Min($searchWorkersFromTotal, $threadsPerProc)
}

$logsDir = Join-Path $ProjectRoot "reports\logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

$readinessPath = Join-Path $ProjectRoot "configs\\readiness.yaml"
$unlockMarkerDir = Join-Path $ProjectRoot "reports\\readiness"
$unlockMarkerPath = Join-Path $unlockMarkerDir "temp_unlock_marker_pool.json"
$backupTag = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ") + "_" + $Mode + "_" + [System.Guid]::NewGuid().ToString("N").Substring(0, 8)
$readinessBackupPath = Join-Path $logsDir ("readiness_backup_pool_" + $backupTag + ".yaml")
$poolUnlockApplied = $false

function Restore-StalePoolUnlock {
    if (-not (Test-Path $unlockMarkerPath)) { return }
    try {
        $marker = Get-Content -LiteralPath $unlockMarkerPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $ownerPid = 0
        if ($null -ne $marker.owner_pid) {
            $ownerPid = [int]$marker.owner_pid
        }
        $ownerAlive = $false
        if ($ownerPid -gt 0) {
            $ownerAlive = $null -ne (Get-Process -Id $ownerPid -ErrorAction SilentlyContinue)
        }
        if ($ownerAlive) { return }
        $backupPath = [string]$marker.readiness_backup_path
        if (-not [string]::IsNullOrWhiteSpace($backupPath) -and (Test-Path $backupPath)) {
            Copy-Item -LiteralPath $backupPath -Destination $readinessPath -Force
        }
    } catch {}
    Remove-Item -LiteralPath $unlockMarkerPath -Force -ErrorAction SilentlyContinue
}

function Test-LivePoolUnlock {
    if (-not (Test-Path $unlockMarkerPath)) { return $false }
    try {
        $marker = Get-Content -LiteralPath $unlockMarkerPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $ownerPid = 0
        if ($null -ne $marker.owner_pid) {
            $ownerPid = [int]$marker.owner_pid
        }
        if ($ownerPid -gt 0) {
            return $null -ne (Get-Process -Id $ownerPid -ErrorAction SilentlyContinue)
        }
    } catch {}
    return $false
}

function Parse-LastJsonObject([string]$text) {
    if ($null -eq $text -or [string]::IsNullOrWhiteSpace($text)) {
        return $null
    }
    $lines = ($text -split "`r?`n")
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = $lines[$i].Trim()
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { return ($line | ConvertFrom-Json) } catch {}
    }
    return $null
}

Write-Host "=== APTuna ProcessPool launcher ===" -ForegroundColor Cyan
Write-Host "ProjectRoot:    $ProjectRoot"
Write-Host "Mode:           $Mode"
Write-Host "ProcessWorkers: $ProcessWorkers"
Write-Host "Threads total:  $Threads"
Write-Host "Threads/proc:   $threadsPerProc"
Write-Host "Search total:   $searchWorkersRequested"
Write-Host "Search/proc:    $searchWorkersEff"
Write-Host "Trials total:   $OptunaTrials"
Write-Host "Trials/proc:    $trialsPerProc"
Write-Host "TimeoutSec:     $OptunaTimeoutSec"
Write-Host "MLBackend:      $OptunaMlSignalBackend"
Write-Host "DataLayer:      $DataLayer"
Write-Host "GridPreset:     $CalibrationGridPreset"
Write-Host "EdgeCoverage:   $ForceProfileEdgeCoverage"
Write-Host "SharedStudy:    $(if ($SharedOptunaStudy) { 'on' } else { 'off' })"
Write-Host "TimeoutExit:    $(if ($DisableTimeoutExit) { 'off' } else { 'on' })"
Write-Host "Window:         train=$trainStartEff..$trainEndEff test=$testStartEff..$testEndEff ($WindowPolicy)"
if (-not [string]::IsNullOrWhiteSpace($calibrationMatrixResolved)) {
    Write-Host "CalibrationMatrix(env): $calibrationMatrixResolved"
}

$workerSpecs = @()
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$sharedStudyIdEff = ""
if ($SharedOptunaStudy) {
    $rawSharedStudyId = if (-not [string]::IsNullOrWhiteSpace($SharedStudyId)) {
        $SharedStudyId
    } else {
        "${Mode}_shared_pool_${stamp}"
    }
    $sharedStudyIdEff = ($rawSharedStudyId -replace '[^A-Za-z0-9_.:-]', '_')
    if ([string]::IsNullOrWhiteSpace($sharedStudyIdEff)) {
        throw "SharedStudyId resolved to empty value."
    }
    Write-Host "SharedStudyId:  $sharedStudyIdEff"
    $storageScheme = (& $python -c "from pathlib import Path; from mlbotnav.optuna_engine import load_optuna_engine_config, resolve_storage_url; root=Path.cwd(); print(resolve_storage_url(root, load_optuna_engine_config(root)).split(':', 1)[0])").Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to resolve Optuna storage for shared-study preflight."
    }
    if ($storageScheme -eq "sqlite") {
        throw "SharedOptunaStudy requires non-sqlite Optuna storage. Current storage scheme: sqlite."
    }
    Write-Host "SharedStorage:  $storageScheme"
}
for ($i = 1; $i -le $ProcessWorkers; $i++) {
    $wid = "w$i"
    $contourId = "${Mode}_pool_${stamp}_${wid}"
    $logPath = Join-Path $logsDir "optuna_pool_${Mode}_${stamp}_${wid}.log"
    $args = @(
        "-m", "mlbotnav.adaptive_auto_train",
        "--symbol", $Symbol,
        "--timeframe", $Timeframe,
        "--layer", $DataLayer,
        "--train-start", $trainStartEff,
        "--train-end", $trainEndEff,
        "--test-day", $testStartEff,
        "--test-end-day", $testEndEff,
        "--window-policy", $WindowPolicy,
        "--signal-mode", $Mode,
        "--contour-id", $contourId,
        "--repeats", "$Repeats",
        "--goal-net-return-pct", "$GoalNetReturnPct",
        "--max-threads", "$threadsPerProc",
        "--search-workers", "$searchWorkersEff",
        "--process-workers-total", "$ProcessWorkers",
        "--search-engine", "optuna",
        "--optuna-stage", $OptunaStage,
        "--optuna-ml-signal-backend", $OptunaMlSignalBackend,
        "--calibration-grid-preset", $CalibrationGridPreset,
        "--force-profile-edge-coverage", $ForceProfileEdgeCoverage,
        "--optuna-n-trials-override", "$trialsPerProc",
        "--optuna-timeout-sec-override", "$OptunaTimeoutSec",
        "--allow-subgoal-candidates",
        "--disable-backlog-active-append",
        "--enforce-repeats-effective-match",
        "--preflight-policy", "configs/preflight_policy.yaml",
        "--cpu-ramp-disable"
    )
    if ($SharedOptunaStudy) {
        $args += @("--optuna-shared-study-id", $sharedStudyIdEff)
    }
    if ($DisableTimeoutExit) {
        $args += "--disable-timeout-exit"
    }
    if (-not $EnableHypothesisProfile) {
        $args += "--disable-hypothesis-profile"
    }
    if (-not [string]::IsNullOrWhiteSpace($TrendFilter)) {
        $args += @("--trend-filter", $TrendFilter)
    }
    if ($MinAbsEmaGap -ge 0.0) {
        $args += @("--min-abs-ema-gap", "$MinAbsEmaGap")
    }
    if ($MinTpReachProb -ge 0.0) {
        $args += @("--min-tp-reach-prob", "$MinTpReachProb")
    }
    if ($StopLossPct -gt 0.0) {
        $args += @("--stop-loss-pct", "$StopLossPct")
    }
    if ($TakeProfitPct -gt 0.0) {
        $args += @("--take-profit-pct", "$TakeProfitPct")
    }
    if ($TpMinFactor -gt 0.0) {
        $args += @("--tp-min-factor", "$TpMinFactor")
    }
    if ($CooldownBars -ge 0) {
        $args += @("--cooldown-bars", "$CooldownBars")
    }
    if (-not [string]::IsNullOrWhiteSpace($HorizonsGrid)) {
        $args += @("--horizons-grid", $HorizonsGrid)
    }
    if (-not [string]::IsNullOrWhiteSpace($MinExpectedMoveGrid)) {
        $args += @("--min-expected-move-grid", $MinExpectedMoveGrid)
    }
    if (-not [string]::IsNullOrWhiteSpace($NotionalUsdGrid)) {
        $args += @("--notional-usd-grid", $NotionalUsdGrid)
    }
    if (-not [string]::IsNullOrWhiteSpace($PLongGrid)) {
        $args += @("--p-long-grid", $PLongGrid)
    }
    if (-not [string]::IsNullOrWhiteSpace($PShortGrid)) {
        $args += @("--p-short-grid", $PShortGrid)
    }
    if ($MinCandidateTrades -ge 0) {
        $args += @("--min-candidate-trades", "$MinCandidateTrades")
    }
    $workerSpecs += [pscustomobject]@{
        Id = $wid
        Args = $args
        LogPath = $logPath
        ErrPath = ($logPath + ".err")
    }
}

if ($DryRun) {
    foreach ($spec in $workerSpecs) {
        Write-Host ("[DRY] {0}: {1} {2}" -f $spec.Id, $python, ($spec.Args -join " "))
    }
    exit 0
}

Restore-StalePoolUnlock

if ($UseTemporaryUnlock) {
    if (Test-LivePoolUnlock) {
        throw "APTuna process pool temporary unlock is already active ($unlockMarkerPath). Run temporary-unlock process-pool jobs sequentially or wait for the active pool to finish."
    }
    if (Test-Path $readinessPath) {
        Copy-Item -LiteralPath $readinessPath -Destination $readinessBackupPath -Force
    }
    if (-not (Test-Path $unlockMarkerDir)) {
        New-Item -ItemType Directory -Path $unlockMarkerDir -Force | Out-Null
    }
    @{
        owner_pid = [int]$PID
        created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        readiness_backup_path = $readinessBackupPath
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $unlockMarkerPath -Encoding UTF8
    & $python -m mlbotnav.readiness --set-project-ready true --set-reason "APTuna process pool temporary unlock" --write-report false | Out-Null
    $poolUnlockApplied = $true
}

$results = @()
try {
    $procs = @()
    foreach ($spec in $workerSpecs) {
        Write-Host ("Starting {0} -> {1}" -f $spec.Id, $spec.LogPath)
        $p = Start-Process -FilePath $python `
            -ArgumentList $spec.Args `
            -RedirectStandardOutput $spec.LogPath `
            -RedirectStandardError $spec.ErrPath `
            -WindowStyle Hidden `
            -PassThru
        $procs += [pscustomobject]@{
            Id = $spec.Id
            Process = $p
            LogPath = $spec.LogPath
        }
        Start-Sleep -Milliseconds 1300
    }

    foreach ($row in $procs) {
        try {
            $row.Process.WaitForExit()
        } catch {}
        $exitCode = $row.Process.ExitCode
        if ($null -eq $exitCode) { $exitCode = -1 }
        $logText = if (Test-Path $row.LogPath) { Get-Content -Path $row.LogPath -Raw -ErrorAction SilentlyContinue } else { "" }
        if ($null -eq $logText) { $logText = "" }
        $errText = if (Test-Path ($row.LogPath + ".err")) { Get-Content -Path ($row.LogPath + ".err") -Raw -ErrorAction SilentlyContinue } else { "" }
        if ($null -eq $errText) { $errText = "" }
        $combinedText = ($logText + "`n" + $errText)
        $tailObj = Parse-LastJsonObject $combinedText
        $summaryPath = $null
        $oos = $null
        $trades = $null
        $status = "unknown"
        if ($null -ne $tailObj) {
            if ($null -ne $tailObj.summary_path) { $summaryPath = [string]$tailObj.summary_path }
        } else {
            $m = [regex]::Matches($combinedText, '"summary_path"\s*:\s*"([^"]+)"')
            if ($m.Count -gt 0) { $summaryPath = [string]$m[$m.Count - 1].Groups[1].Value }
        }
        if (-not [string]::IsNullOrWhiteSpace($summaryPath) -and (Test-Path $summaryPath)) {
            try {
                $s = Get-Content -Path $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($null -ne $s.best_oos) {
                    $oos = [double]$s.best_oos.oos_net_return_pct
                    $trades = [int]$s.best_oos.oos_trades
                    if ($null -ne $s.best_oos.status) { $status = [string]$s.best_oos.status }
                }
            } catch {}
        }
        if (($status -eq "unknown") -and ([int]$exitCode -ne 0)) {
            $status = "worker_failed"
        }
        if (($exitCode -lt 0) -and (-not [string]::IsNullOrWhiteSpace($summaryPath))) {
            # Some detached Start-Process handles do not return ExitCode reliably.
            # If summary exists, treat as successful completion.
            $exitCode = 0
        }
        $results += [pscustomobject]@{
            worker = $row.Id
            pid = $row.Process.Id
            exit_code = $exitCode
            status = $status
            oos_net_return_pct = $oos
            oos_trades = $trades
            summary_path = $summaryPath
            log_path = $row.LogPath
            err_path = $row.LogPath + ".err"
        }
    }
}
finally {
    if ($poolUnlockApplied) {
        if (Test-Path $readinessBackupPath) {
            Copy-Item -LiteralPath $readinessBackupPath -Destination $readinessPath -Force
        }
        Remove-Item -LiteralPath $unlockMarkerPath -Force -ErrorAction SilentlyContinue
    }
}

$ok = ($results | Where-Object { ([int]$_.exit_code -eq 0) -and ([string]$_.status -ne "worker_failed") }).Count -eq $results.Count
$best = $results |
    Where-Object { $null -ne $_.oos_net_return_pct } |
    Sort-Object `
        @{ Expression = { if ([int]$_.oos_trades -gt 0) { 1 } else { 0 } }; Descending = $true }, `
        @{ Expression = { if ([double]$_.oos_net_return_pct -gt 0.0) { 1 } else { 0 } }; Descending = $true }, `
        @{ Expression = { [double]$_.oos_net_return_pct }; Descending = $true }, `
        @{ Expression = { [int]$_.oos_trades }; Descending = $true } |
    Select-Object -First 1

$out = [ordered]@{
    status = $(if ($ok) { "OK" } else { "PARTIAL_FAIL" })
    mode = $Mode
    process_workers = $ProcessWorkers
    threads_total = $Threads
    threads_per_process = $threadsPerProc
    trials_total = $OptunaTrials
    trials_per_process = $trialsPerProc
    shared_optuna_study = [bool]$SharedOptunaStudy
    shared_study_id = $(if ($SharedOptunaStudy) { $sharedStudyIdEff } else { $null })
    best_worker = $(if ($null -ne $best) { $best.worker } else { $null })
    best_oos_net_return_pct = $(if ($null -ne $best) { $best.oos_net_return_pct } else { $null })
    best_oos_trades = $(if ($null -ne $best) { $best.oos_trades } else { $null })
    workers = $results
}
$out | ConvertTo-Json -Depth 8 | Out-Host
if ($ok) { exit 0 } else { exit 1 }
