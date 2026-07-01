param(
    [string]$BlockId = "B001",
    [ValidateSet("long_only", "short_only")]
    [string]$Mode = "long_only",
    [ValidateSet("raw", "core")]
    [string]$DataLayer = "core",
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainStart = "2026-05-11",
    [string]$TrainEnd = "2026-05-24",
    [string]$TestStart = "2026-05-25",
    [string]$TestEnd = "2026-05-31",
    [ValidateSet("fixed_1d", "multiday")]
    [string]$WindowPolicy = "multiday",
    [double]$GoalNetReturnPct = 1.0,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [int]$ProcessWorkers = 3,
    [int]$SearchWorkersPerProcess = 3,
    [int]$OptunaTrials = 40,
    [int]$OptunaTimeoutSec = 900,
    [ValidateSet("auto", "wide", "medium", "narrow")]
    [string]$CalibrationGridPreset = "wide",
    [ValidateSet("auto", "on", "off")]
    [string]$ForceProfileEdgeCoverage = "on",
    [int]$MinCandidateTrades = 1,
    [switch]$UseTemporaryUnlock,
    [switch]$SharedOptunaStudy,
    [string]$SharedStudyId = "",
    [switch]$DryRun,
    [switch]$EmitJson
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
    $matches = [regex]::Matches($text, "\{")
    for ($i = $matches.Count - 1; $i -ge 0; $i--) {
        $candidate = $text.Substring($matches[$i].Index).Trim()
        if ([string]::IsNullOrWhiteSpace($candidate)) { continue }
        try { return ($candidate | ConvertFrom-Json) } catch {}
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

function Read-JsonFile([string]$pathText) {
    $full = Resolve-ProjectPath $pathText
    if ($null -eq $full -or -not (Test-Path $full)) {
        return $null
    }
    try {
        return (Get-Content -LiteralPath $full -Raw -Encoding UTF8 | ConvertFrom-Json)
    } catch {
        return $null
    }
}

function Get-BacktestStats($reportObj) {
    if ($null -eq $reportObj -or $null -eq $reportObj.backtest) {
        return [ordered]@{
            net = ""
            trades = ""
            raw = ""
            mode = ""
            gate = ""
            min_move = ""
            filled = ""
            runtime = ""
            backtest_path = ""
        }
    }
    $bt = $reportObj.backtest
    $diag = $bt.trend_filter_diagnostics
    $artifactPath = ""
    if ($null -ne $reportObj.artifacts -and $null -ne $reportObj.artifacts.backtest_path) {
        $artifactPath = [string]$reportObj.artifacts.backtest_path
    }
    return [ordered]@{
        net = [string]$bt.net_return_pct
        trades = [string]$bt.trades
        raw = $(if ($null -ne $diag) { [string]$diag.signal_count_raw } else { "" })
        mode = $(if ($null -ne $diag) { [string]$diag.signal_count_after_mode } else { "" })
        gate = $(if ($null -ne $diag) { [string]$diag.signal_count_after_entry_action_gates } else { "" })
        min_move = $(if ($null -ne $diag) { [string]$diag.signal_count_after_min_move } else { "" })
        filled = $(if ($null -ne $diag) { [string]$diag.entries_filled } else { "" })
        runtime = $(if ($null -ne $reportObj.runtime_diagnostic_status) { [string]$reportObj.runtime_diagnostic_status } else { "" })
        backtest_path = $artifactPath
    }
}

function Format-BlockResultLine($row) {
    $best = $row.best_oos
    $oos = $null
    $stats = Get-BacktestStats $null
    if ($null -ne $best -and $null -ne $best.oos_report) {
        $oos = Read-JsonFile ([string]$best.oos_report)
        $stats = Get-BacktestStats $oos
    }
    $runtime = $stats.runtime
    if ([string]::IsNullOrWhiteSpace($runtime) -and $null -ne $best -and $null -ne $best.runtime_diagnostic_status) {
        $runtime = [string]$best.runtime_diagnostic_status
    }
    return ("{0,-5} {1,-20} status={2,-6} oos={3,10} trades={4,3} signals raw/mode/gate/min/fill={5}/{6}/{7}/{8}/{9} runtime={10}" -f `
        [string]$row.passport_id,
        [string]$row.action_id,
        [string]$row.status,
        [string]$stats.net,
        [string]$stats.trades,
        [string]$stats.raw,
        [string]$stats.mode,
        [string]$stats.gate,
        [string]$stats.min_move,
        [string]$stats.filled,
        [string]$runtime)
}

function Show-TradeRows([string]$label, [string]$backtestPath, [int]$limit = 3) {
    $full = Resolve-ProjectPath $backtestPath
    if ($null -eq $full -or -not (Test-Path $full)) {
        Write-Host ("  {0}: CSV сделок не найден." -f $label) -ForegroundColor DarkYellow
        return
    }
    $rows = @()
    try {
        $rows = Import-Csv -LiteralPath $full | Where-Object {
            $side = [string]$_.side
            $entry = [string]$_.entry_time_utc
            $exit = [string]$_.exit_time_utc
            -not [string]::IsNullOrWhiteSpace($side) -and $side -ne "0" -and $side -ne "0.0" -and `
                -not [string]::IsNullOrWhiteSpace($entry) -and -not [string]::IsNullOrWhiteSpace($exit)
        } | Select-Object -First $limit
    } catch {
        Write-Host ("  {0}: CSV сделок не прочитан: {1}" -f $label, $_.Exception.Message) -ForegroundColor DarkYellow
        return
    }
    if ($rows.Count -eq 0) {
        Write-Host ("  {0}: сделок с входом/выходом нет." -f $label) -ForegroundColor DarkYellow
        return
    }
    foreach ($t in $rows) {
        $profit = [string]$t.net_return_pct
        if ([string]::IsNullOrWhiteSpace($profit)) { $profit = [string]$t.net_return }
        Write-Host ("  {0}: вход={1} price={2} -> выход={3} price={4} side={5} reason={6} profit%={7} pnl_usd={8}" -f `
            $label,
            [string]$t.entry_time_utc,
            [string]$t.entry_price,
            [string]$t.exit_time_utc,
            [string]$t.exit_price,
            [string]$t.side,
            [string]$t.exit_reason,
            $profit,
            [string]$t.net_pnl_usd) -ForegroundColor Gray
    }
}

function Show-BlockTerminalSummary($payload, [string]$reportJson, [string]$reportMd) {
    Write-Host ""
    Write-Host ("=== Блоковый отбор: {0} / {1} ===" -f $payload.block_id, $payload.mode) -ForegroundColor Cyan
    Write-Host ("Окно: train={0}..{1} test={2}..{3} ({4})" -f $payload.train_start, $payload.train_end, $payload.test_start, $payload.test_end, $payload.window_policy)
    Write-Host ("JSON: {0}" -f $reportJson) -ForegroundColor Green
    Write-Host ("MD:   {0}" -f $reportMd) -ForegroundColor Green
    Write-Host ""
    Write-Host "F-ID  Action               Итог OOS / сигналы"
    foreach ($r in $payload.results) {
        Write-Host (Format-BlockResultLine $r)
    }
    Write-Host ""
    if ($null -ne $payload.block_winner) {
        Write-Host ("Победитель блока: {0} / {1}" -f $payload.block_winner.passport_id, $payload.block_winner.action_id) -ForegroundColor Green
    } else {
        Write-Host "Победитель блока: NO_BLOCK_WINNER" -ForegroundColor Yellow
    }
    if ($null -ne $payload.block_best_available) {
        Write-Host ("Лучший доступный ряд: {0} / {1}" -f $payload.block_best_available.passport_id, $payload.block_best_available.action_id) -ForegroundColor Yellow
        $bestOosReport = $null
        if ($null -ne $payload.block_best_available.best_oos -and $null -ne $payload.block_best_available.best_oos.oos_report) {
            $bestOosReport = Read-JsonFile ([string]$payload.block_best_available.best_oos.oos_report)
        }
        $bestStats = Get-BacktestStats $bestOosReport
        Show-TradeRows "OOS best" ([string]$bestStats.backtest_path) 3
    }
    if ($EmitJson) {
        Write-Output ($payload | ConvertTo-Json -Depth 30)
    }
}

function Candidate-Key($row) {
    $best = $row.best_oos
    $net = -1000000000.0
    $trades = 0
    $dd = 1000000000.0
    $runtimeStatus = ""
    if ($null -ne $best) {
        if ($null -ne $best.oos_net_return_pct) { $net = [double]$best.oos_net_return_pct }
        elseif ($null -ne $best.net_return_pct) { $net = [double]$best.net_return_pct }
        if ($null -ne $best.oos_trades) { $trades = [int]$best.oos_trades }
        elseif ($null -ne $best.trades) { $trades = [int]$best.trades }
        if ($null -ne $best.oos_max_drawdown_pct) { $dd = [Math]::Abs([double]$best.oos_max_drawdown_pct) }
        elseif ($null -ne $best.max_drawdown_pct) { $dd = [Math]::Abs([double]$best.max_drawdown_pct) }
        if ($null -ne $best.runtime_diagnostic_status) { $runtimeStatus = [string]$best.runtime_diagnostic_status }
    }
    $reachable = if ($runtimeStatus -eq "MIN_MOVE_UNREACHABLE") { 0 } else { 1 }
    $tradeful = if ($trades -gt 0) { 1 } else { 0 }
    $positive = if ($net -gt 0.0) { 1 } else { 0 }
    return [pscustomobject]@{
        reachable = $reachable
        tradeful = $tradeful
        positive = $positive
        net = $net
        trades = $trades
        neg_drawdown = -1.0 * $dd
    }
}

$manifestText = & $python -m mlbotnav.block_family_manifest --block-id $BlockId 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Failed to build block manifest for ${BlockId}: $($manifestText -join "`n")"
}
$manifest = ($manifestText -join "`n") | ConvertFrom-Json
$rows = @($manifest.rows)
if ($rows.Count -lt 1) {
    throw "No rows for block $BlockId"
}

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$runner = Join-Path $ProjectRoot "APTuna\run_optuna_1d1d_stagec_process_pool.ps1"
$qaDir = Join-Path $ProjectRoot "reports\qa_gate"
if (-not (Test-Path $qaDir)) {
    New-Item -ItemType Directory -Path $qaDir -Force | Out-Null
}

function Ru([string]$base64Text) {
    return [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($base64Text))
}

Write-Host (Ru "PT09INCR0LvQvtC60L7QstGL0Lkg0L7RgtCx0L7RgCDRgdC10LzQtdC50YHRgtCy0LAgPT09") -ForegroundColor Cyan
Write-Host ((Ru "0JHQu9C+0Lo6ICA=") + $BlockId)
Write-Host ((Ru "0KDQtdC20LjQvDogICA=") + $Mode)
Write-Host ((Ru "0KHRgtGA0L7QujogICA=") + $rows.Count)
Write-Host ((Ru "0J7QutC90L46IHRyYWluPQ==") + "$TrainStart..$TrainEnd" + (Ru "IHRlc3Q9") + "$TestStart..$TestEnd ($WindowPolicy)")
Write-Host (Ru "0J/QvtC70LjRgtC40LrQsDog0L7QtNC40L3QvtGH0L3Ri9C5INC+0YLQsdC+0YAgRiDQstC90YPRgtGA0Lgg0LHQu9C+0LrQsDsg0LHQtdC3INC/0LXRgNC10LTQsNGH0Lgg0LIgTUw=")

$results = @()
foreach ($row in $rows) {
    $passportId = [string]$row.passport_id
    $actionId = [string]$row.action_id
    $matrixPath = [string]$row.matrix_path
    Write-Host ("[{0}] {1} {2} -> {3}" -f $BlockId, $passportId, $actionId, $matrixPath) -ForegroundColor Yellow

    $cmdArgs = @(
        "-ExecutionPolicy", "Bypass",
        "-File", $runner,
        "-Mode", $Mode,
        "-DataLayer", $DataLayer,
        "-Symbol", $Symbol,
        "-Timeframe", $Timeframe,
        "-TrainStart", $TrainStart,
        "-TrainEnd", $TrainEnd,
        "-TestStart", $TestStart,
        "-TestEnd", $TestEnd,
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
        "-MinCandidateTrades", "$MinCandidateTrades"
    )
    if ($UseTemporaryUnlock) {
        $cmdArgs += "-UseTemporaryUnlock"
    }
    if ($SharedOptunaStudy) {
        $cmdArgs += "-SharedOptunaStudy"
        $sharedIdForRow = if (-not [string]::IsNullOrWhiteSpace($SharedStudyId)) {
            "${SharedStudyId}_${passportId}"
        } else {
            "${BlockId}_${Mode}_${passportId}_shared_${stamp}"
        }
        $cmdArgs += @("-SharedStudyId", $sharedIdForRow)
    }

    if ($DryRun) {
        $results += [pscustomobject]@{
            block_id = [string]$BlockId
            passport_id = $passportId
            action_id = $actionId
            matrix_path = $matrixPath
            status = "dry_run"
            dry_run_command = "powershell " + ($cmdArgs -join " ")
        }
        continue
    }

    $started = (Get-Date).ToUniversalTime().ToString("o")
    $outText = & powershell @cmdArgs 2>&1
    $exitCode = [int]$LASTEXITCODE
    $combinedText = ($outText -join "`n")
    $parsed = Parse-LastJsonObject $combinedText
    $summaryPath = $null
    if ($null -ne $parsed -and $null -ne $parsed.best_worker) {
        $summaryPath = $null
        $workers = @($parsed.workers)
        foreach ($w in $workers) {
            if ([string]$w.worker -eq [string]$parsed.best_worker) {
                $summaryPath = [string]$w.summary_path
                break
            }
        }
    }
    $summaryObj = Read-JsonFile $summaryPath
    $best = $null
    if ($null -ne $summaryObj -and $null -ne $summaryObj.best_oos) {
        $best = $summaryObj.best_oos
        if ($null -ne $best.oos_report) {
            $oosObj = Read-JsonFile ([string]$best.oos_report)
            if ($null -ne $oosObj) {
                if ($null -eq $best.runtime_diagnostic_status -and $null -ne $oosObj.runtime_diagnostic_status) {
                    $best | Add-Member -NotePropertyName runtime_diagnostic_status -NotePropertyValue $oosObj.runtime_diagnostic_status -Force
                }
                if ($null -eq $best.runtime_diagnostics -and $null -ne $oosObj.runtime_diagnostics) {
                    $best | Add-Member -NotePropertyName runtime_diagnostics -NotePropertyValue $oosObj.runtime_diagnostics -Force
                }
            }
        }
    }
    $rowStatus = if ($exitCode -ne 0) {
        "failed"
    } elseif ($null -eq $parsed) {
        "missing_process_pool_summary"
    } elseif ($null -eq $summaryPath -or $null -eq $summaryObj) {
        "missing_adaptive_summary"
    } else {
        "ok"
    }

    $results += [pscustomobject]@{
        block_id = [string]$BlockId
        passport_id = $passportId
        action_id = $actionId
        matrix_path = $matrixPath
        status = $rowStatus
        exit_code = $exitCode
        started_utc = $started
        finished_utc = (Get-Date).ToUniversalTime().ToString("o")
        process_pool_summary = $parsed
        adaptive_summary_path = $summaryPath
        best_oos = $best
    }
}

$bestAvailable = $null
$winner = $null
$ranked = @($results | Where-Object { [string]$_.status -eq "ok" -and $null -ne $_.best_oos })
if ($ranked.Count -gt 0) {
    $bestAvailable = $ranked | Sort-Object `
        @{ Expression = { (Candidate-Key $_).reachable }; Descending = $true }, `
        @{ Expression = { (Candidate-Key $_).tradeful }; Descending = $true }, `
        @{ Expression = { (Candidate-Key $_).positive }; Descending = $true }, `
        @{ Expression = { (Candidate-Key $_).net }; Descending = $true }, `
        @{ Expression = { (Candidate-Key $_).trades }; Descending = $true }, `
        @{ Expression = { (Candidate-Key $_).neg_drawdown }; Descending = $true } |
        Select-Object -First 1
    $bestKey = Candidate-Key $bestAvailable
    if ($bestKey.reachable -eq 1 -and $bestKey.tradeful -eq 1 -and $bestKey.positive -eq 1) {
        $winner = $bestAvailable
    }
}

$statusOk = if ($DryRun) {
    (($results | Where-Object { [string]$_.status -ne "dry_run" }).Count -eq 0)
} else {
    (($results | Where-Object { [string]$_.status -ne "ok" }).Count -eq 0)
}

$payload = [ordered]@{
    status = $(if ($statusOk) { "OK" } else { "PARTIAL_OR_FAILED" })
    generated_utc = (Get-Date).ToUniversalTime().ToString("o")
    block_id = [string]$BlockId
    mode = [string]$Mode
    data_layer = [string]$DataLayer
    symbol = [string]$Symbol
    timeframe = [string]$Timeframe
    train_start = [string]$TrainStart
    train_end = [string]$TrainEnd
    test_start = [string]$TestStart
    test_end = [string]$TestEnd
    window_policy = [string]$WindowPolicy
    selection_policy = "reachable_tradeful_positive_oos_first"
    ml_policy = "NO_ML_PROMOTION_FROM_BLOCK_SELECTION"
    manifest = $manifest
    results = $results
    block_best_available = $bestAvailable
    block_winner = $winner
}

$reportJson = Join-Path $qaDir ("block_family_selection_{0}_{1}_{2}.json" -f $BlockId, $Mode, $stamp)
$reportMd = Join-Path $qaDir ("block_family_selection_{0}_{1}_{2}_RU.md" -f $BlockId, $Mode, $stamp)
$payload | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $reportJson -Encoding UTF8

$md = @()
$md += (Ru "IyDQkdC70L7QutC+0LLRi9C5INC+0YLQsdC+0YAg0YHQtdC80LXQudGB0YLQstCwINC/0LDRgdC/0L7RgNGC0L7Qsg==")
$md += ""
$md += (Ru "LSDQodGC0LDRgtGD0YE6IA==") + "``$($payload.status)``"
$md += (Ru "LSDQkdC70L7Qujog") + "``$BlockId``"
$md += (Ru "LSDQoNC10LbQuNC8OiA=") + "``$Mode``"
$md += (Ru "LSDQntC60L3Qvjog") + "``$TrainStart..$TrainEnd`` -> ``$TestStart..$TestEnd``"
$md += (Ru "LSDQn9C+0LvQuNGC0LjQutCwOiDQvtC00LjQvdC+0YfQvdGL0Lkg0L7RgtCx0L7RgCBGLdC/0LDRgdC/0L7RgNGC0L7QsiDQstC90YPRgtGA0Lgg0LHQu9C+0LrQsDsg0LHQtdC3INC/0LXRgNC10LTQsNGH0Lgg0LIgTUw=")
$md += ""
$md += (Ru "fCDQn9Cw0YHQv9C+0YDRgiB8INCU0LXQudGB0YLQstC40LUgfCDQodGC0LDRgtGD0YEgfCDQm9GD0YfRiNC40LkgT09TICUgfCDQodC00LXQu9C60LggfCBSdW50aW1lLdGB0YLQsNGC0YPRgSB8INCc0LDRgtGA0LjRhtCwIHw=")
$md += "|---|---|---|---:|---:|---|---|"
foreach ($r in $results) {
    $best = $r.best_oos
    $net = ""
    $trades = ""
    $runtime = ""
    if ($null -ne $best) {
        if ($null -ne $best.oos_net_return_pct) { $net = [string]$best.oos_net_return_pct }
        elseif ($null -ne $best.net_return_pct) { $net = [string]$best.net_return_pct }
        if ($null -ne $best.oos_trades) { $trades = [string]$best.oos_trades }
        elseif ($null -ne $best.trades) { $trades = [string]$best.trades }
        if ($null -ne $best.runtime_diagnostic_status) { $runtime = [string]$best.runtime_diagnostic_status }
    }
    $md += "| ``$($r.passport_id)`` | ``$($r.action_id)`` | ``$($r.status)`` | $net | $trades | ``$runtime`` | ``$($r.matrix_path)`` |"
}
if ($null -ne $bestAvailable) {
    $md += ""
    $md += (Ru "0JvRg9GH0YjQuNC5INC00L7RgdGC0YPQv9C90YvQuSDRgNGP0LQ6IA==") + "``$($bestAvailable.passport_id)`` / ``$($bestAvailable.action_id)``."
}
if ($null -ne $winner) {
    $md += ""
    $md += (Ru "0J/QvtCx0LXQtNC40YLQtdC70Ywg0LHQu9C+0LrQsDog") + "``$($winner.passport_id)`` / ``$($winner.action_id)``."
} else {
    $md += ""
    $md += (Ru "0J/QvtCx0LXQtNC40YLQtdC70Ywg0LHQu9C+0LrQsDog") + "``NO_BLOCK_WINNER``."
}
$md -join "`n" | Set-Content -LiteralPath $reportMd -Encoding UTF8

Show-BlockTerminalSummary $payload $reportJson $reportMd
