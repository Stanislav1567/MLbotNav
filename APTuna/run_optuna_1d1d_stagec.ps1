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
    [int]$OptunaTrials = 80,
    [int]$OptunaTimeoutSec = 1200,
    [string]$TrendFilter = "",
    [double]$MinAbsEmaGap = -1.0,
    [double]$MinTpReachProb = -1.0,
    [string]$HorizonsGrid = "",
    [string]$MinExpectedMoveGrid = "",
    [string]$PShortGrid = "",
    [string]$CalibrationMatrixPath = "",
    [switch]$EnableHypothesisProfile,
    [int]$WaitForRuntimeLockSec = 0,
    [switch]$AllowParallelSameChat,
    [ValidateSet("A", "B", "C", "auto")]
    [string]$OptunaStage = "C",
    [ValidateSet("off", "on")]
    [string]$OptunaMlSignalBackend = "off",
    [ValidateSet("auto", "wide", "medium", "narrow")]
    [string]$CalibrationGridPreset = "auto",
    [ValidateSet("auto", "on", "off")]
    [string]$ForceProfileEdgeCoverage = "auto",
    [switch]$UseTemporaryUnlock,
    [switch]$UseProcessPool,
    [int]$ProcessWorkers = 1,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$AptunaRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $AptunaRoot
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
if (-not (Test-Path $envBootstrap)) {
    throw "Env bootstrap not found: $envBootstrap"
}
& $envBootstrap -Threads $Threads | Out-Host

$runner = Join-Path $ProjectRoot "run_p185_optuna_single_pass.ps1"
if (-not (Test-Path $runner)) {
    throw "Runner not found: $runner"
}
if ($UseProcessPool) {
    $poolRunner = Join-Path $AptunaRoot "run_optuna_1d1d_stagec_process_pool.ps1"
    if (-not (Test-Path $poolRunner)) {
        throw "Process-pool runner not found: $poolRunner"
    }
    if ($ProcessWorkers -lt 1) {
        Write-Warning "UseProcessPool enabled, ProcessWorkers raised to 1."
        $ProcessWorkers = 1
    }
    $poolParams = @{
        Mode = $Mode
        Repeats = $Repeats
        Symbol = $Symbol
        Timeframe = $Timeframe
        TrainDate = $TrainDate
        TestDate = $TestDate
        TrainStart = $TrainStart
        TrainEnd = $TrainEnd
        TestStart = $TestStart
        TestEnd = $TestEnd
        WindowPolicy = $WindowPolicy
        GoalNetReturnPct = $GoalNetReturnPct
        Threads = $Threads
        SearchWorkers = $SearchWorkers
        OptunaTrials = $OptunaTrials
        OptunaTimeoutSec = $OptunaTimeoutSec
        TrendFilter = $TrendFilter
        MinAbsEmaGap = $MinAbsEmaGap
        MinTpReachProb = $MinTpReachProb
        HorizonsGrid = $HorizonsGrid
        MinExpectedMoveGrid = $MinExpectedMoveGrid
        PShortGrid = $PShortGrid
        CalibrationMatrixPath = $CalibrationMatrixPath
        OptunaStage = $OptunaStage
        OptunaMlSignalBackend = $OptunaMlSignalBackend
        CalibrationGridPreset = $CalibrationGridPreset
        ForceProfileEdgeCoverage = $ForceProfileEdgeCoverage
        ProcessWorkers = $ProcessWorkers
    }
    if ($EnableHypothesisProfile) {
        $poolParams["EnableHypothesisProfile"] = $true
    }
    if ($UseTemporaryUnlock) {
        $poolParams["UseTemporaryUnlock"] = $true
    }
    if ($DryRun) {
        $poolParams["DryRun"] = $true
    }
    Write-Host "ProcessPool: enabled (workers=$ProcessWorkers)" -ForegroundColor Yellow
    & $poolRunner @poolParams
    exit $LASTEXITCODE
}
if ($WaitForRuntimeLockSec -gt 0) {
    $statePath = Join-Path $ProjectRoot "data\meta\live_coord_state.json"
    $deadline = (Get-Date).AddSeconds([int]$WaitForRuntimeLockSec)
    while ($true) {
        if (-not (Test-Path $statePath)) { break }
        try {
            $state = Get-Content -Path $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            Start-Sleep -Seconds 2
            continue
        }
        $owner = $state.runtime_owner
        $busyByOther = $false
        $busyBySame = $false
        if ($null -ne $owner) {
            $ownerChat = [string]$owner.owner_chat
            if (-not [string]::IsNullOrWhiteSpace($ownerChat) -and $ownerChat -ne "this_chat") {
                $busyByOther = $true
            }
            if (-not [string]::IsNullOrWhiteSpace($ownerChat) -and $ownerChat -eq "this_chat") {
                $busyBySame = $true
            }
        }
        $busy = $busyByOther
        if ((-not $AllowParallelSameChat) -and $busyBySame) {
            $busy = $true
        }
        if (-not $busy) { break }
        if ((Get-Date) -ge $deadline) {
            throw "Runtime lock wait timeout (${WaitForRuntimeLockSec}s): owner_chat=$ownerChat task_id=$($owner.task_id)"
        }
        Start-Sleep -Seconds 5
    }
}

$runnerParams = @{
    Mode = $Mode
    Repeats = $Repeats
    Symbol = $Symbol
    Timeframe = $Timeframe
    TrainDate = $TrainDate
    TestDate = $TestDate
    TrainStart = $TrainStart
    TrainEnd = $TrainEnd
    TestStart = $TestStart
    TestEnd = $TestEnd
    WindowPolicy = $WindowPolicy
    GoalNetReturnPct = $GoalNetReturnPct
    Threads = $Threads
    SearchWorkers = $SearchWorkers
    OptunaTrials = $OptunaTrials
    OptunaTimeoutSec = $OptunaTimeoutSec
    CalibrationMatrixPath = $CalibrationMatrixPath
    OptunaStage = $OptunaStage
    OptunaMlSignalBackend = $OptunaMlSignalBackend
    CalibrationGridPreset = $CalibrationGridPreset
    ForceProfileEdgeCoverage = $ForceProfileEdgeCoverage
}
if (-not [string]::IsNullOrWhiteSpace($MinExpectedMoveGrid)) {
    $runnerParams["MinExpectedMoveGrid"] = $MinExpectedMoveGrid
}
if (-not [string]::IsNullOrWhiteSpace($TrendFilter)) {
    $runnerParams["TrendFilter"] = $TrendFilter
}
if ($MinAbsEmaGap -ge 0.0) {
    $runnerParams["MinAbsEmaGap"] = $MinAbsEmaGap
}
if ($MinTpReachProb -ge 0.0) {
    $runnerParams["MinTpReachProb"] = $MinTpReachProb
}
if (-not [string]::IsNullOrWhiteSpace($HorizonsGrid)) {
    $runnerParams["HorizonsGrid"] = $HorizonsGrid
}
if (-not [string]::IsNullOrWhiteSpace($PShortGrid)) {
    $runnerParams["PShortGrid"] = $PShortGrid
}
if ($EnableHypothesisProfile) {
    $runnerParams["EnableHypothesisProfile"] = $true
}

if ($DryRun) {
    $runnerParams["DryRun"] = $true
}
if ($UseTemporaryUnlock) {
    $runnerParams["UseTemporaryUnlock"] = $true
}
$runnerParams["CpuRampDisable"] = $true

Write-Host "=== APTuna canonical launcher ===" -ForegroundColor Cyan
Write-Host "ProjectRoot: $ProjectRoot"
Write-Host "APTunaRoot:  $AptunaRoot"
Write-Host "Mode:        $Mode"
Write-Host "Repeats:     $Repeats"
Write-Host "Goal:        $GoalNetReturnPct"
if (-not [string]::IsNullOrWhiteSpace($TrainStart) -or -not [string]::IsNullOrWhiteSpace($TrainEnd) -or -not [string]::IsNullOrWhiteSpace($TestStart) -or -not [string]::IsNullOrWhiteSpace($TestEnd) -or $WindowPolicy -eq "multiday") {
    $ts = if ([string]::IsNullOrWhiteSpace($TrainStart)) { $TrainDate } else { $TrainStart }
    $te = if ([string]::IsNullOrWhiteSpace($TrainEnd)) { $TrainDate } else { $TrainEnd }
    $vs = if ([string]::IsNullOrWhiteSpace($TestStart)) { $TestDate } else { $TestStart }
    $ve = if ([string]::IsNullOrWhiteSpace($TestEnd)) { $TestDate } else { $TestEnd }
    Write-Host "Window:      train=$ts..$te test=$vs..$ve ($WindowPolicy)"
} else {
    Write-Host "Window:      train=$TrainDate..$TrainDate test=$TestDate..$TestDate ($WindowPolicy)"
}
Write-Host "Threads:     $Threads"
Write-Host "Workers:     $SearchWorkers"
Write-Host "Trials:      $OptunaTrials"
Write-Host "TimeoutSec:  $OptunaTimeoutSec"
Write-Host "Stage:       $OptunaStage"
Write-Host "MLBackend:   $OptunaMlSignalBackend"
Write-Host "GridPreset:  $CalibrationGridPreset"
Write-Host "EdgeCover:   $ForceProfileEdgeCoverage"
if (-not [string]::IsNullOrWhiteSpace($CalibrationMatrixPath)) {
    Write-Host "Matrix:      $CalibrationMatrixPath"
}

& $runner @runnerParams
