param(
    [ValidateSet("long_only", "short_only")]
    [string]$Mode = "long_only",
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [double]$GoalNetReturnPct = 1.0,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [int]$ProcessWorkers = 2,
    [int]$OptunaTrials = 40,
    [int]$OptunaTimeoutSec = 900,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = (Get-Location).Path
}
Set-Location $ProjectRoot

$BaseMatrixPath = Join-Path $ProjectRoot "configs\calibration_full_matrix_v1.yaml"
$MatrixDir = Join-Path $ProjectRoot "configs\calibration_matrices"
$PoolLauncher = Join-Path $ProjectRoot "APTuna\run_optuna_1d1d_stagec_process_pool.ps1"
$OutDir = Join-Path $ProjectRoot "reports\qa_gate"

if (-not (Test-Path $BaseMatrixPath)) {
    throw "Base calibration matrix not found: $BaseMatrixPath"
}
if (-not (Test-Path $PoolLauncher)) {
    throw "Pool launcher not found: $PoolLauncher"
}

New-Item -ItemType Directory -Force -Path $MatrixDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Parse-LastJsonObject([string]$Text) {
    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $null
    }
    $lines = $Text -split "`r?`n"
    $buffer = New-Object System.Collections.Generic.List[string]
    $balance = 0
    $started = $false
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = [string]$lines[$i]
        if ((-not $started) -and ($line -notmatch '\}')) {
            continue
        }
        $started = $true
        $buffer.Insert(0, $line)
        $balance += ([regex]::Matches($line, '\}')).Count
        $balance -= ([regex]::Matches($line, '\{')).Count
        if ($balance -eq 0 -and ($line -match '\{')) {
            $candidate = ($buffer.ToArray() -join "`n").Trim()
            if (-not [string]::IsNullOrWhiteSpace($candidate)) {
                try {
                    return ($candidate | ConvertFrom-Json)
                } catch {}
            }
        }
    }
    return $null
}

function New-PackageAMatrix(
    [string]$OutputPath,
    [string]$Hypothesis,
    [string]$ParamsLiteral
) {
    $lines = Get-Content -Path $BaseMatrixPath -Encoding UTF8
    $hypIdx = -1
    $gridIdx = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^hypothesis_rows:\s*$') {
            $hypIdx = $i
        }
        if ($lines[$i] -match '^search_grid_rows:\s*$') {
            $gridIdx = $i
            break
        }
    }
    if ($hypIdx -lt 0 -or $gridIdx -lt 0 -or $gridIdx -le $hypIdx) {
        throw "Cannot split base calibration matrix into prefix/hypothesis/suffix blocks."
    }

    $prefix = @()
    if ($hypIdx -gt 0) {
        $prefix = $lines[0..($hypIdx - 1)]
    }
    $suffix = $lines[$gridIdx..($lines.Count - 1)]
    $hypBlock = @(
        "hypothesis_rows:",
        "  - hypothesis: $Hypothesis",
        "    calibrate: true",
        "    optuna_toggle: true",
        "    params: [$ParamsLiteral]"
    )

    @($prefix + $hypBlock + $suffix) | Set-Content -Path $OutputPath -Encoding UTF8
}

function Ensure-PackageAMatrices {
    $matrices = @(
        @{
            path = (Join-Path $MatrixDir "optuna_v3_package_a_ah1_long.yaml")
            hypothesis = "swing_hl_hh_long"
            params = "return_lookback, threshold_fine"
        },
        @{
            path = (Join-Path $MatrixDir "optuna_v3_package_a_ah1_short.yaml")
            hypothesis = "swing_lh_ll_short"
            params = "return_lookback, threshold_fine"
        },
        @{
            path = (Join-Path $MatrixDir "optuna_v3_package_a_ah2.yaml")
            hypothesis = "value_area_rotation_vs_breakout"
            params = "density_window_short, density_window_long, density_bin_pct, threshold_fine"
        },
        @{
            path = (Join-Path $MatrixDir "optuna_v3_package_a_ah3.yaml")
            hypothesis = "fib_extension_targets"
            params = "rolling_window, threshold_fine"
        }
    )

    foreach ($m in $matrices) {
        New-PackageAMatrix -OutputPath $m.path -Hypothesis $m.hypothesis -ParamsLiteral $m.params
    }
}

function Get-SlotMap([string]$SignalMode) {
    if ($SignalMode -eq "short_only") {
        return @(
            @{
                slot = "A-H1"
                hypothesis = "swing_lh_ll_short"
                matrix_path = (Join-Path $MatrixDir "optuna_v3_package_a_ah1_short.yaml")
            },
            @{
                slot = "A-H2"
                hypothesis = "value_area_rotation_vs_breakout"
                matrix_path = (Join-Path $MatrixDir "optuna_v3_package_a_ah2.yaml")
            },
            @{
                slot = "A-H3"
                hypothesis = "fib_extension_targets"
                matrix_path = (Join-Path $MatrixDir "optuna_v3_package_a_ah3.yaml")
            }
        )
    }

    return @(
        @{
            slot = "A-H1"
            hypothesis = "swing_hl_hh_long"
            matrix_path = (Join-Path $MatrixDir "optuna_v3_package_a_ah1_long.yaml")
        },
        @{
            slot = "A-H2"
            hypothesis = "value_area_rotation_vs_breakout"
            matrix_path = (Join-Path $MatrixDir "optuna_v3_package_a_ah2.yaml")
        },
        @{
            slot = "A-H3"
            hypothesis = "fib_extension_targets"
            matrix_path = (Join-Path $MatrixDir "optuna_v3_package_a_ah3.yaml")
        }
    )
}

Ensure-PackageAMatrices

$windows = @(
    @{ id = "W1"; train = "2026-05-29"; test = "2026-05-30" },
    @{ id = "W2"; train = "2026-05-30"; test = "2026-05-31" },
    @{ id = "W3"; train = "2026-05-31"; test = "2026-06-01" }
)
$slots = Get-SlotMap -SignalMode $Mode
$ledger = @()

foreach ($window in $windows) {
    foreach ($slot in $slots) {
        Write-Host ("=== V3 Package A === mode={0} slot={1} hypothesis={2} window={3} train={4} test={5}" -f `
            $Mode, $slot.slot, $slot.hypothesis, $window.id, $window.train, $window.test) -ForegroundColor Cyan

        $cmd = @(
            "-ExecutionPolicy", "Bypass",
            "-File", $PoolLauncher,
            "-Mode", $Mode,
            "-Symbol", $Symbol,
            "-Timeframe", $Timeframe,
            "-TrainDate", $window.train,
            "-TestDate", $window.test,
            "-GoalNetReturnPct", "$GoalNetReturnPct",
            "-Threads", "$Threads",
            "-SearchWorkers", "$SearchWorkers",
            "-ProcessWorkers", "$ProcessWorkers",
            "-OptunaTrials", "$OptunaTrials",
            "-OptunaTimeoutSec", "$OptunaTimeoutSec",
            "-CalibrationMatrixPath", $slot.matrix_path,
            "-UseTemporaryUnlock"
        )

        if ($DryRun) {
            Write-Host ("[DRY] powershell {0}" -f ($cmd -join " ")) -ForegroundColor Yellow
            continue
        }

        $raw = & powershell @cmd 2>&1 | Out-String
        $raw | Out-Host
        $exitCode = $LASTEXITCODE
        $tail = Parse-LastJsonObject -Text $raw
        if ($null -eq $tail) {
            throw "Pool launcher did not emit terminal JSON for mode=$Mode slot=$($slot.slot) window=$($window.id)."
        }

        $bestWorker = $null
        $bestSummaryPath = $null
        $bestLogPath = $null
        $bestErrPath = $null
        if ($null -ne $tail.best_worker -and $null -ne $tail.workers) {
            $bestWorker = ($tail.workers | Where-Object { $_.worker -eq $tail.best_worker } | Select-Object -First 1)
        }
        if ($null -ne $bestWorker) {
            $bestSummaryPath = [string]$bestWorker.summary_path
            $bestLogPath = [string]$bestWorker.log_path
            $bestErrPath = [string]$bestWorker.err_path
        }

        $bestOos = $null
        $bestTrades = $null
        $goalPass = $false
        $bestStatus = ""
        if (-not [string]::IsNullOrWhiteSpace($bestSummaryPath) -and (Test-Path $bestSummaryPath)) {
            $summary = Get-Content -Path $bestSummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($null -ne $summary.best_oos) {
                $bestOos = $summary.best_oos.oos_net_return_pct
                $bestTrades = $summary.best_oos.oos_trades
                if ($null -ne $summary.best_oos.goal_pass) {
                    $goalPass = [bool]$summary.best_oos.goal_pass
                }
                if ($null -ne $summary.best_oos.status) {
                    $bestStatus = [string]$summary.best_oos.status
                }
            }
        }

        $ledger += [pscustomobject]@{
            mode = $Mode
            phase = "package_a"
            step = $(if ($Mode -eq "long_only") { 3 } else { 4 })
            slot = $slot.slot
            hypothesis = $slot.hypothesis
            window = $window.id
            train = $window.train
            test = $window.test
            calibration_matrix_path = $slot.matrix_path
            pool_status = [string]$tail.status
            exit_code = [int]$exitCode
            best_worker = [string]$tail.best_worker
            best_oos_net_return_pct = $bestOos
            best_oos_trades = $bestTrades
            goal_pass = $goalPass
            best_status = $bestStatus
            best_summary_path = $bestSummaryPath
            best_log_path = $bestLogPath
            best_err_path = $bestErrPath
            ts_utc = (Get-Date).ToUniversalTime().ToString("o")
        }

        if ([int]$exitCode -ne 0 -or [string]$tail.status -ne "OK") {
            throw "Run failed for mode=$Mode slot=$($slot.slot) window=$($window.id); see worker logs."
        }
    }
}

if ($DryRun) {
    Write-Host "DryRun complete." -ForegroundColor Yellow
    exit 0
}

$runUtc = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$artifactId = if ($Mode -eq "long_only") { "p2022" } else { "p2023" }
$jsonlPath = Join-Path $OutDir ("{0}_optuna_v3_package_a_{1}_runs_{2}.jsonl" -f $artifactId, $Mode, $runUtc)
$summaryPath = Join-Path $OutDir ("{0}_optuna_v3_package_a_{1}_summary_{2}.json" -f $artifactId, $Mode, $runUtc)

$jsonLines = foreach ($row in $ledger) {
    $row | ConvertTo-Json -Depth 8 -Compress
}
$jsonLines | Set-Content -Path $jsonlPath -Encoding UTF8

$tradeful = $ledger | Where-Object { ($null -ne $_.best_oos_trades) -and ([int]$_.best_oos_trades -gt 0) }
$bestTradeful = $tradeful | Sort-Object best_oos_net_return_pct -Descending | Select-Object -First 1
$candidateRows = $ledger | Where-Object {
    $_.goal_pass -eq $true -and
    $null -ne $_.best_oos_trades -and [int]$_.best_oos_trades -gt 0 -and
    $null -ne $_.best_oos_net_return_pct -and [double]$_.best_oos_net_return_pct -gt 0
}

$summaryPayload = [ordered]@{
    status = "DONE"
    phase = "package_a"
    step = $(if ($Mode -eq "long_only") { 3 } else { 4 })
    created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    tz_ref = "docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md"
    audit_ref = "docs/OPTUNA_GLOBAL_LAUNCH_AUDIT_2026-06-02_RU.md"
    mode = $Mode
    windows = @($windows.id)
    slots = @($slots.slot)
    acceptance_rule = @{
        goal_pass = $true
        oos_trades_gt = 0
        oos_net_return_pct_gt = 0
    }
    candidate_count = @($candidateRows).Count
    best_tradeful = $bestTradeful
    experiments = $ledger
    runs_path = $jsonlPath
    next_step = $(if ($Mode -eq "long_only") { "Run Package A short_only on W1-W3." } else { "Publish unified Package A triage." })
}

$summaryPayload | ConvertTo-Json -Depth 8 | Set-Content -Path $summaryPath -Encoding UTF8
Write-Host "Summary: $summaryPath"
Write-Host "Runs:    $jsonlPath"
