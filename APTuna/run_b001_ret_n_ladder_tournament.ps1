param(
    [ValidateSet("long_only", "short_only")]
    [string]$Mode = "long_only",
    [ValidateSet("raw", "core")]
    [string]$DataLayer = "core",
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainDate = "2026-05-31",
    [string]$TestDate = "2026-06-01",
    [string]$TrainStart = "",
    [string]$TrainEnd = "",
    [string]$TestStart = "",
    [string]$TestEnd = "",
    [ValidateSet("fixed_1d", "multiday")]
    [string]$WindowPolicy = "fixed_1d",
    [double]$GoalNetReturnPct = 1.0,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [int]$ProcessWorkers = 3,
    [int]$SearchWorkersPerProcess = 3,
    [int]$OptunaTrials = 180,
    [int]$OptunaTimeoutSec = 900,
    [ValidateSet("wide", "medium", "narrow")]
    [string]$CalibrationGridPreset = "wide",
    [ValidateSet("auto", "on", "off")]
    [string]$ForceProfileEdgeCoverage = "on",
    [string]$MatrixManifestPath = "",
    [int]$StartIndex = 1,
    [int]$EndIndex = 5,
    [int]$MaxCombos = 0,
    [switch]$EnableCombinationTournament,
    [switch]$UseTemporaryUnlock,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$AptunaRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $AptunaRoot
Set-Location $ProjectRoot
$env:PYTHONPATH = "src"

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python venv not found: $python"
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

function Resolve-ProjectPath([string]$pathText) {
    if ([string]::IsNullOrWhiteSpace($pathText)) {
        return $null
    }
    if ([System.IO.Path]::IsPathRooted($pathText)) {
        return [System.IO.Path]::GetFullPath($pathText)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $pathText))
}

function Extract-SummaryPath([string]$text, $parsedObj) {
    if ($null -ne $parsedObj -and $null -ne $parsedObj.summary_path) {
        return [string]$parsedObj.summary_path
    }
    $matches = [regex]::Matches($text, '"summary_path"\s*:\s*"([^"]+)"')
    if ($matches.Count -gt 0) {
        return [string]$matches[$matches.Count - 1].Groups[1].Value
    }
    return $null
}

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$trainStartEff = if ([string]::IsNullOrWhiteSpace($TrainStart)) { $TrainDate } else { $TrainStart }
$trainEndEff = if ([string]::IsNullOrWhiteSpace($TrainEnd)) { $trainStartEff } else { $TrainEnd }
$testStartEff = if ([string]::IsNullOrWhiteSpace($TestStart)) { $TestDate } else { $TestStart }
$testEndEff = if ([string]::IsNullOrWhiteSpace($TestEnd)) { $testStartEff } else { $TestEnd }
if ([string]::IsNullOrWhiteSpace($MatrixManifestPath)) {
    $genText = & $python -m mlbotnav.b001_ret_n_ladder_tournament --grid-preset $CalibrationGridPreset 2>&1
    $genObj = Parse-LastJsonObject ($genText -join "`n")
    if ($null -eq $genObj -or [string]::IsNullOrWhiteSpace([string]$genObj.manifest_path)) {
        throw "Failed to generate B001 RET_N tournament matrices. Output: $($genText -join "`n")"
    }
    $MatrixManifestPath = [string]$genObj.manifest_path
}

$manifestFullPath = if ([System.IO.Path]::IsPathRooted($MatrixManifestPath)) {
    [System.IO.Path]::GetFullPath($MatrixManifestPath)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $MatrixManifestPath))
}
if (-not (Test-Path $manifestFullPath)) {
    throw "Manifest not found: $manifestFullPath"
}
$manifest = Get-Content -LiteralPath $manifestFullPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $EnableCombinationTournament -and [int]$EndIndex -gt 5) {
    throw "Combination tournament is diagnostic-only now. Use StartIndex/EndIndex within 1..5 for solo selection, or pass -EnableCombinationTournament explicitly for a non-baseline diagnostic run."
}
$rows = @($manifest.rows | Where-Object {
    ([int]$_.index -ge $StartIndex) -and ([int]$_.index -le $EndIndex)
})
if ($MaxCombos -gt 0) {
    $rows = @($rows | Select-Object -First $MaxCombos)
}
if ($rows.Count -lt 1) {
    throw "No tournament rows selected."
}

$runner = Join-Path $ProjectRoot "APTuna\run_optuna_1d1d_stagec_process_pool.ps1"
$results = @()
Write-Host "=== B001 RET_N ladder tournament ===" -ForegroundColor Cyan
Write-Host "Manifest: $manifestFullPath"
Write-Host "Rows:     $($rows.Count)"
Write-Host "Mode:     $Mode"
Write-Host "Window:   train=$trainStartEff..$trainEndEff test=$testStartEff..$testEndEff ($WindowPolicy)"
Write-Host "Grid:     $CalibrationGridPreset"
Write-Host "Trials:   $OptunaTrials"

foreach ($row in $rows) {
    $matrixPath = [string]$row.matrix_path
    $comboId = [string]$row.combo_id
    Write-Host ("[{0}/{1}] {2} -> {3}" -f $row.index, $manifest.combinations_count, $comboId, $matrixPath) -ForegroundColor Yellow

    $cmdArgs = @(
        "-ExecutionPolicy", "Bypass",
        "-File", $runner,
        "-Mode", $Mode,
        "-DataLayer", $DataLayer,
        "-Symbol", $Symbol,
        "-Timeframe", $Timeframe,
        "-TrainStart", $trainStartEff,
        "-TrainEnd", $trainEndEff,
        "-TestStart", $testStartEff,
        "-TestEnd", $testEndEff,
        "-WindowPolicy", $WindowPolicy,
        "-GoalNetReturnPct", "$GoalNetReturnPct",
        "-Threads", "$Threads",
        "-SearchWorkers", "$SearchWorkers",
        "-ProcessWorkers", "$ProcessWorkers",
        "-SearchWorkersPerProcess", "$SearchWorkersPerProcess",
        "-OptunaTrials", "$OptunaTrials",
        "-OptunaTimeoutSec", "$OptunaTimeoutSec",
        "-CalibrationMatrixPath", $matrixPath,
        "-CalibrationGridPreset", $CalibrationGridPreset,
        "-ForceProfileEdgeCoverage", $ForceProfileEdgeCoverage,
        "-MinCandidateTrades", "1"
    )
    if ($UseTemporaryUnlock) {
        $cmdArgs += "-UseTemporaryUnlock"
    }

    if ($DryRun) {
        $results += [pscustomobject]@{
            index = [int]$row.index
            combo_id = $comboId
            passports = $row.passports
            matrix_path = $matrixPath
            dry_run_command = "powershell " + ($cmdArgs -join " ")
            status = "dry_run"
        }
        continue
    }

    $started = (Get-Date).ToUniversalTime().ToString("o")
    $outText = & powershell @cmdArgs 2>&1
    $exitCode = $LASTEXITCODE
    $combinedText = ($outText -join "`n")
    $parsed = Parse-LastJsonObject $combinedText
    $summaryPath = Extract-SummaryPath $combinedText $parsed
    $summaryFullPath = Resolve-ProjectPath $summaryPath
    $summaryObj = $null
    if ($null -ne $summaryFullPath -and (Test-Path $summaryFullPath)) {
        try {
            $summaryObj = Get-Content -LiteralPath $summaryFullPath -Raw -Encoding UTF8 | ConvertFrom-Json
        } catch {
            $summaryObj = $null
        }
    }
    $best = $null
    if ($null -ne $summaryObj) {
        $best = $summaryObj.best_oos
    } elseif ($null -ne $parsed) {
        $best = $parsed.best_oos
    }
    $results += [pscustomobject]@{
        index = [int]$row.index
        combo_id = $comboId
        passports = $row.passports
        matrix_path = $matrixPath
        status = $(if ($exitCode -eq 0) { "ok" } else { "failed" })
        exit_code = [int]$exitCode
        started_utc = $started
        finished_utc = (Get-Date).ToUniversalTime().ToString("o")
        launcher_summary_path = $summaryPath
        best_oos = $best
    }
}

$qaDir = Join-Path $ProjectRoot "reports\qa_gate"
if (-not (Test-Path $qaDir)) {
    New-Item -ItemType Directory -Path $qaDir -Force | Out-Null
}
$reportJson = Join-Path $qaDir "b001_ret_n_ladder_tournament_${Mode}_${stamp}.json"
$reportMd = Join-Path $qaDir "b001_ret_n_ladder_tournament_${Mode}_${stamp}_RU.md"

$payload = [pscustomobject]@{
    status = $(if (($results | Where-Object { [string]$_.status -eq "failed" }).Count -eq 0) { "OK" } else { "PARTIAL_OR_FAILED" })
    generated_utc = (Get-Date).ToUniversalTime().ToString("o")
    mode = $Mode
    data_layer = $DataLayer
    train_start = $trainStartEff
    train_end = $trainEndEff
    test_start = $testStartEff
    test_end = $testEndEff
    window_policy = $WindowPolicy
    grid_preset = $CalibrationGridPreset
    optuna_trials = $OptunaTrials
    manifest_path = $MatrixManifestPath
    selected_count = $rows.Count
    selection_policy = "best_tradeful_oos_first"
    results = $results
}
$payload | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $reportJson -Encoding UTF8

$md = @()
$md += "# B001 RET_N Ladder Tournament"
$md += ""
$md += "- Status: ``$($payload.status)``"
$md += "- Mode: ``$Mode``"
$md += "- Window: train ``$trainStartEff..$trainEndEff`` / test ``$testStartEff..$testEndEff`` (``$WindowPolicy``)"
$md += "- Grid: ``$CalibrationGridPreset``"
$md += "- Manifest: ``$MatrixManifestPath``"
$md += ""
$md += "| # | Combo | Status | Best OOS % | Trades | Matrix |"
$md += "|---:|---|---|---:|---:|---|"
foreach ($r in $results) {
    $best = $r.best_oos
    $net = ""
    $trades = ""
    if ($null -ne $best) {
        if ($null -ne $best.oos_net_return_pct) {
            $net = [string]$best.oos_net_return_pct
        } elseif ($null -ne $best.net_return_pct) {
            $net = [string]$best.net_return_pct
        }
        if ($null -ne $best.oos_trades) {
            $trades = [string]$best.oos_trades
        } elseif ($null -ne $best.trades) {
            $trades = [string]$best.trades
        }
    }
    $md += "| $($r.index) | ``$($r.combo_id)`` | ``$($r.status)`` | $net | $trades | ``$($r.matrix_path)`` |"
}
$md -join "`n" | Set-Content -LiteralPath $reportMd -Encoding UTF8

Write-Host "Report JSON: $reportJson" -ForegroundColor Green
Write-Host "Report MD:   $reportMd" -ForegroundColor Green
Write-Output ($payload | ConvertTo-Json -Depth 20)
