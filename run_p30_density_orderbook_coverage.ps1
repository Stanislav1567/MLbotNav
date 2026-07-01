param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainDate = "2026-05-19",
    [string]$TestDate = "2026-05-20",
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [double]$Leverage = 10.0,
    [string]$StepLabel = "P30"
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
    throw "Python venv not found: $python. Run: py -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}

$targets = @(
    "hvn_lvn_density_reaction",
    "volume_profile_poc_vah_val_retest",
    "value_area_rotation_vs_breakout",
    "wedge_breakout_plus_profile_acceptance",
    "orderbook_imbalance_l1_l50",
    "spread_pressure_and_delta_absorption"
)

$longSummaries = @()
$shortSummaries = @()

function Get-LatestSummary([string]$mode){
    $pattern = "reports\\adaptive\\$mode\\adaptive_loop_${Symbol}_${Timeframe}_${TestDate}_*.json"
    $f = Get-ChildItem $pattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $f) { throw "summary not found for mode=$mode by pattern=$pattern" }
    return $f.FullName
}

function Run-One([string]$mode, [string]$trendFilter, [string]$unlockReason){
    & $python -m mlbotnav.adaptive_auto_train `
      --symbol $Symbol `
      --timeframe $Timeframe `
      --train-start $TrainDate `
      --train-end $TrainDate `
      --test-day $TestDate `
      --test-end-day $TestDate `
      --window-policy fixed_1d `
      --signal-mode $mode `
      --repeats 1 `
      --trend-filter $trendFilter `
      --min-abs-ema-gap 0.0 `
      --disable-hypothesis-profile `
      --disable-backlog-active-append `
      --goal-net-return-pct 1 `
      --min-train-rows 500 `
      --n-folds 2 `
      --horizons-grid "1,2,3,4,6,8,12,20" `
      --p-long-grid "0.50,0.52,0.54,0.56,0.58,0.60" `
      --p-short-grid "0.50,0.48,0.46,0.44,0.42,0.40" `
      --min-expected-move-grid "0.0,0.0005,0.001,0.002,0.003,0.005" `
      --fee-bps 10 `
      --slippage-bps 5 `
      --stop-loss-pct 0.004 `
      --take-profit-pct 0.05 `
      --tp-min-factor 0.7 `
      --cooldown-bars 0 `
      --notional-usd 10 `
      --leverage $Leverage `
      --execution-mode exchange_like `
      --order-type market `
      --cpu-max-pct 85 `
      --max-threads $Threads `
      --search-workers $SearchWorkers `
      --speed-profile turbo `
      --temporary-unlock-readiness `
      --unlock-reason $unlockReason | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "adaptive_auto_train failed for mode=$mode trend_filter=$trendFilter exit_code=$LASTEXITCODE"
    }
}

Write-Host "=== P30 long target coverage ==="
foreach($h in $targets){
    Write-Host "[P30-L] trend-filter=$h"
    Run-One -mode "long_only" -trendFilter $h -unlockReason "$StepLabel long $h"
    $longSummaries += (Get-LatestSummary -mode "long_only")
}

Write-Host "=== P30 short target coverage ==="
foreach($h in $targets){
    Write-Host "[P30-S] trend-filter=$h"
    Run-One -mode "short_only" -trendFilter $h -unlockReason "$StepLabel short $h"
    $shortSummaries += (Get-LatestSummary -mode "short_only")
}

$latestShortSummary = Get-LatestSummary -mode "short_only"
$latestShortObj = Get-Content $latestShortSummary -Encoding UTF8 | ConvertFrom-Json
$latestShortOos = $latestShortObj.oos_report
if (-not $latestShortOos) {
    if ($latestShortObj.history -and $latestShortObj.history.Count -gt 0) {
        $lastRow = $latestShortObj.history[$latestShortObj.history.Count - 1]
        if ($lastRow.PSObject.Properties.Name -contains "oos_report") {
            $latestShortOos = $lastRow.oos_report
        }
    }
}
if (-not $latestShortOos) {
    $fallback = Get-ChildItem "reports\final_review\oos_report_${Symbol}_${Timeframe}_${TestDate}_short_only_*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($fallback) { $latestShortOos = $fallback.FullName }
}
if (-not $latestShortOos) { throw "oos_report not found in latest short summary and no fallback final_review report found" }

Write-Host "=== P30 chain checks ==="
& $python -m mlbotnav.table_canon_pack --symbol $Symbol --timeframe $Timeframe --start-date $TestDate --end-date $TestDate --horizon-bars 6 --layer core --output-mode stable | Out-Host
& $python -m mlbotnav.table_convergence_5plus --oos-report $latestShortOos --run-dir reports/table_canon_current --with-gate | Out-Host
& $python -m mlbotnav.audit_table_chain --run-dir reports/table_canon_current --require-trades | Out-Host
& $python -m mlbotnav.features_block_audit | Out-Host
& $python -m mlbotnav.orderbook_source_audit --expect-status active | Out-Host
& $python -m mlbotnav.tz_gate_runner --step $StepLabel --symbol $Symbol --timeframe $Timeframe --start-date $TestDate --end-date $TestDate --horizon-bars 6 --layer core --oos-report $latestShortOos | Out-Host
& $python -m mlbotnav.p72_freeze_ready_check | Out-Host

function Collect-Observed([string[]]$summaryPaths){
    $set = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach($p in $summaryPaths | Select-Object -Unique){
        if(-not (Test-Path $p)){ continue }
        $obj = Get-Content $p -Encoding UTF8 | ConvertFrom-Json
        if($obj.history){
            foreach($row in $obj.history){
                $tf = [string]$row.trend_filter
                if(-not [string]::IsNullOrWhiteSpace($tf)){ [void]$set.Add($tf) }
            }
        }
    }
    return @($set)
}

$obsLong = Collect-Observed -summaryPaths $longSummaries
$obsShort = Collect-Observed -summaryPaths $shortSummaries
$missLong = @($targets | Where-Object { $_ -notin $obsLong })
$missShort = @($targets | Where-Object { $_ -notin $obsShort })

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outPath = "reports/qa_gate/p30_density_orderbook_coverage_${stamp}.json"
$payload = [ordered]@{
    status = $(if($missLong.Count -eq 0 -and $missShort.Count -eq 0){"PASS"}else{"FAIL"})
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    step = $StepLabel
    symbol = $Symbol
    timeframe = $Timeframe
    train_date = $TrainDate
    test_date = $TestDate
    targets = [ordered]@{ long_only = $targets; short_only = $targets }
    observed = [ordered]@{ long_only = $obsLong; short_only = $obsShort }
    missing = [ordered]@{ long_only = $missLong; short_only = $missShort }
    summaries = [ordered]@{ long_only = ($longSummaries | Select-Object -Unique); short_only = ($shortSummaries | Select-Object -Unique) }
    latest_short_oos = $latestShortOos
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -Path $outPath -Encoding UTF8
Write-Output ("{`"status`":`"$($payload.status)`",`"report_path`":`"$((Resolve-Path $outPath).Path)`"}")
if($payload.status -ne "PASS"){ exit 2 }



