param(
    [ValidateSet("long", "short", "combined", "table_chain", "all", "full_chain")]
    [string]$Mode = "combined",
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainDate = "2026-05-19",
    [string]$TrainEndDate = "",
    [string]$TestDate = "2026-05-20",
    [string]$TestEndDate = "",
    [int]$Repeats = 1,
    [int]$Threads = 9,
    [int]$SearchWorkers = 9,
    [double]$GoalNetReturnPct = 1.0,
    [int]$HorizonBars = 6,
    [string]$Layer = "core",
    [string]$StepLabel = "P23",
    [string]$OosReportPath = "",
    [ValidateSet("freeze", "release")]
    [string]$FreezeCheckMode = "freeze",
    [string]$RunDir = "reports/table_canon_current",
    [switch]$SkipConvergenceIfFromDaily,
    [int]$PreflightMinTrainRows = 900,
    [int]$PreflightNFolds = 2,
    [string]$PreflightHorizonsGrid = "1,2,3,4,5,6,8,12,16",
    [string]$PreflightPolicyPath = "configs/preflight_policy.yaml"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot
$effectiveTrainEndDate = if ([string]::IsNullOrWhiteSpace($TrainEndDate)) { $TrainDate } else { $TrainEndDate }
$effectiveTestEndDate = if ([string]::IsNullOrWhiteSpace($TestEndDate)) { $TestDate } else { $TestEndDate }
$EffectiveMode = if ($Mode -eq "full_chain") { "all" } else { $Mode }

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
$script:PreflightRawLayer = "raw"
$script:PreflightCoreLayer = "core"
$script:PreflightCoreRequireFullCoverage = $true
$script:PreflightMinTrainRowsResolved = [int]$PreflightMinTrainRows
$script:PreflightNFoldsResolved = [int]$PreflightNFolds
$script:PreflightHorizonsGridResolved = [string]$PreflightHorizonsGrid
$script:HasPreflightMinTrainRowsArg = $PSBoundParameters.ContainsKey("PreflightMinTrainRows")
$script:HasPreflightNFoldsArg = $PSBoundParameters.ContainsKey("PreflightNFolds")
$script:HasPreflightHorizonsGridArg = $PSBoundParameters.ContainsKey("PreflightHorizonsGrid")

function Resolve-PreflightPolicySettings() {
    $policy = $null
    $py = @"
import json
from pathlib import Path
from mlbotnav.preflight_policy import get_core_preflight_cfg, get_raw_preflight_cfg
root = Path(r"$ProjectRoot")
raw = get_raw_preflight_cfg(root, policy_path=r"$PreflightPolicyPath")
core = get_core_preflight_cfg(root, policy_path=r"$PreflightPolicyPath")
print(json.dumps({"raw": raw, "core": core}, ensure_ascii=False))
"@
    $raw = $py | & $python - 2>&1
    $policy = Parse-JsonObject (($raw | Out-String))
    if (-not $policy) {
        Write-Log "WARN preflight policy parse failed; fallback to CLI/defaults. policy_path=$PreflightPolicyPath"
        return
    }

    $rawCfg = $policy.raw
    if ($rawCfg) {
        if (-not $script:HasPreflightMinTrainRowsArg) {
            $script:PreflightMinTrainRowsResolved = [int]$rawCfg.min_train_rows
        }
        if (-not $script:HasPreflightNFoldsArg) {
            $script:PreflightNFoldsResolved = [int]$rawCfg.n_folds
        }
        if (-not $script:HasPreflightHorizonsGridArg) {
            $script:PreflightHorizonsGridResolved = [string]$rawCfg.horizons_grid
        }
        $script:PreflightRawLayer = [string]$rawCfg.layer
    }

    $coreCfg = $policy.core
    if ($coreCfg) {
        $script:PreflightCoreLayer = [string]$coreCfg.layer
        $script:PreflightCoreRequireFullCoverage = [bool]$coreCfg.require_full_coverage
    }
}
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$logPath = "reports\\qa_gate\\p23_operator_unified_${stamp}.log"
$jsonPath = "reports\\qa_gate\\p23_operator_unified_${stamp}.json"
$script:steps = @()
$skipConvFromDaily = $false
if (-not $PSBoundParameters.ContainsKey("SkipConvergenceIfFromDaily")) {
    $skipConvFromDaily = $true
} else {
    $skipConvFromDaily = [bool]$SkipConvergenceIfFromDaily
}

function Write-Log([string]$msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $msg"
    Write-Host $line
    Add-Content -Path $logPath -Value $line -Encoding UTF8
}

function Parse-JsonObject([string]$rawText) {
    if ([string]::IsNullOrWhiteSpace($rawText)) { return $null }
    $lines = $rawText -split "`r?`n"
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = $lines[$i].Trim()
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { return ($line | ConvertFrom-Json) } catch {}
    }
    return $null
}
Resolve-PreflightPolicySettings

function Get-LatestFile([string]$pattern) {
    $f = Get-ChildItem $pattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $f) { throw "File not found by pattern: $pattern" }
    return $f.FullName
}

function Invoke-Step([string]$id, [string]$title, [scriptblock]$action) {
    Write-Log "[$id] START $title"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        & $action
        $sw.Stop()
        $sec = [math]::Round($sw.Elapsed.TotalSeconds, 2)
        $script:steps += [ordered]@{ id = $id; title = $title; status = "PASS"; seconds = $sec }
        Write-Log "[$id] PASS $title (${sec}s)"
    }
    catch {
        $sw.Stop()
        $err = $_.Exception.Message
        $script:steps += [ordered]@{ id = $id; title = $title; status = "FAIL"; seconds = [math]::Round($sw.Elapsed.TotalSeconds, 2); error = $err }
        Write-Log "[$id] FAIL $title :: $err"
        throw
    }
}

function Run-DailyCycle([string]$modesCsv) {
    $raw = & $python -m mlbotnav.daily_long_short_cycle `
      --symbol $Symbol `
      --timeframe $Timeframe `
      --train-start $TrainDate `
      --train-end $effectiveTrainEndDate `
      --test-day $TestDate `
      --test-end-day $effectiveTestEndDate `
      --modes $modesCsv `
      --repeats $Repeats `
      --goal-net-return-pct $GoalNetReturnPct `
      --max-threads $Threads `
      --search-workers $SearchWorkers `
      --preflight-policy $PreflightPolicyPath `
      --run-dir $RunDir 2>&1
    $raw | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "daily_long_short_cycle failed with exit code $LASTEXITCODE" }
    $parsed = Parse-JsonObject (($raw | Out-String))
    if (-not $parsed) { throw "daily_long_short_cycle output JSON not found" }
    $reportPath = [string]$parsed.report_path
    if ([string]::IsNullOrWhiteSpace($reportPath)) { throw "daily_long_short_cycle report_path missing" }
    if (-not (Test-Path $reportPath)) { throw "daily_long_short_cycle report_path not found: $reportPath" }
    return [ordered]@{ parsed = $parsed; report_path = $reportPath }
}

function Run-PreflightRaw() {
    $raw = & $python -m mlbotnav.preflight_window `
      --symbol $Symbol `
      --timeframe $Timeframe `
      --train-start $TrainDate `
      --train-end $effectiveTrainEndDate `
      --test-day $TestDate `
      --test-end-day $effectiveTestEndDate `
      --min-train-rows $script:PreflightMinTrainRowsResolved `
      --n-folds $script:PreflightNFoldsResolved `
      --horizons-grid $script:PreflightHorizonsGridResolved `
      --layer $script:PreflightRawLayer 2>&1
    $raw | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "preflight_window(raw) failed with exit code $LASTEXITCODE" }
    $parsed = Parse-JsonObject (($raw | Out-String))
    if ($parsed -and -not [string]::IsNullOrWhiteSpace([string]$parsed.report_path)) {
        Write-Log "Preflight raw report: $([string]$parsed.report_path)"
    }
}

function Run-CoreWindowReadiness() {
    $requireFullCoveragePy = if ($script:PreflightCoreRequireFullCoverage) { "True" } else { "False" }
    $py = @"
import json
from pathlib import Path
from mlbotnav.data_window_readiness import evaluate_data_window_readiness, write_data_window_readiness_report
root = Path(r"$ProjectRoot")
payload = evaluate_data_window_readiness(
    root,
    symbol="$Symbol",
    timeframe="$Timeframe",
    start_date="$TestDate",
    end_date="$effectiveTestEndDate",
    layer="$script:PreflightCoreLayer",
    require_full_coverage=$requireFullCoveragePy,
)
report_path = write_data_window_readiness_report(root, payload=payload, action_name="p23_operator_core_preflight")
print(json.dumps({"status": payload.get("status"), "report_path": str(report_path), "failed": int((payload.get("summary") or {}).get("missing_days", 0))}, ensure_ascii=False))
raise SystemExit(0 if payload.get("status") == "PASS" else 1)
"@
    $raw = $py | & $python - 2>&1
    $raw | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "data_window_readiness(core) failed with exit code $LASTEXITCODE" }
    $parsed = Parse-JsonObject (($raw | Out-String))
    if ($parsed -and -not [string]::IsNullOrWhiteSpace([string]$parsed.report_path)) {
        Write-Log "Preflight core readiness report: $([string]$parsed.report_path)"
    }
}

function Resolve-OosFromDailyCycleReport([string]$dailyReportPath, [string]$modeName) {
    $obj = Get-Content $dailyReportPath -Raw | ConvertFrom-Json
    $stepId = "table_convergence_5plus_$modeName"
    $step = $obj.steps | Where-Object { $_.task -eq $stepId } | Select-Object -First 1
    if (-not $step) { return $null }
    $oos = [string]$step.oos_report
    if ([string]::IsNullOrWhiteSpace($oos)) { return $null }
    if (-not (Test-Path $oos)) { return $null }
    return $oos
}

function Run-TableCanonPack() {
    if ($RunDir -eq "reports/table_canon_current") {
        & $python -m mlbotnav.table_canon_pack `
          --symbol $Symbol `
          --timeframe $Timeframe `
          --start-date $TestDate `
          --end-date $effectiveTestEndDate `
          --horizon-bars $HorizonBars `
          --layer $Layer `
          --output-mode stable | Out-Host
        if ($LASTEXITCODE -ne 0) { throw "table_canon_pack failed with exit code $LASTEXITCODE" }
        return
    }

    $raw = & $python -m mlbotnav.table_canon_pack `
      --symbol $Symbol `
      --timeframe $Timeframe `
      --start-date $TestDate `
      --end-date $effectiveTestEndDate `
      --horizon-bars $HorizonBars `
      --layer $Layer `
      --output-mode run 2>&1
    $raw | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "table_canon_pack failed with exit code $LASTEXITCODE" }
    $parsed = Parse-JsonObject (($raw | Out-String))
    if (-not $parsed -or [string]::IsNullOrWhiteSpace([string]$parsed.run_dir)) {
        throw "table_canon_pack run-mode output missing run_dir"
    }
    $sourceRunDir = [string]$parsed.run_dir
    if (-not (Test-Path $sourceRunDir)) {
        throw "table_canon_pack run_dir not found: $sourceRunDir"
    }
    if (Test-Path $RunDir) { Remove-Item -Recurse -Force $RunDir }
    New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
    Copy-Item -Recurse -Force "$sourceRunDir\\*" $RunDir
}

function Run-TableConvergence([string]$oosPath) {
    & $python -m mlbotnav.table_convergence_5plus --oos-report $oosPath --run-dir $RunDir | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "table_convergence_5plus failed with exit code $LASTEXITCODE" }
}

function Run-AuditChain([bool]$RequireTrades = $true) {
    $auditArgs = @("-m", "mlbotnav.audit_table_chain", "--run-dir", $RunDir)
    if ($RequireTrades) {
        $auditArgs += "--require-trades"
    }
    & $python @auditArgs | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "audit_table_chain failed with exit code $LASTEXITCODE" }
}

function Run-Gates([string]$oosPath) {
    & $python -m mlbotnav.features_block_audit | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "features_block_audit failed" }

    & $python -m mlbotnav.orderbook_source_audit --expect-status active | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "orderbook_source_audit failed" }

    & $python -m mlbotnav.tz_gate_runner --step $StepLabel --symbol $Symbol --timeframe $Timeframe --start-date $TestDate --end-date $effectiveTestEndDate --horizon-bars $HorizonBars --layer $Layer --oos-report $oosPath | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "tz_gate_runner failed" }

    if ($FreezeCheckMode -eq "freeze") {
        & $python -m mlbotnav.readiness --set-project-ready false --set-reason "P23 freeze gate baseline" --write-report false | Out-Host
        if ($LASTEXITCODE -ne 0) { throw "readiness freeze baseline normalize failed" }
    }

    & $python -m mlbotnav.p72_freeze_ready_check --mode $FreezeCheckMode | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "p72_freeze_ready_check failed" }
}

$latestLongOos = $null
$latestShortOos = $null
$primaryOos = $null
$requireTradesForAudit = $true
$dailyCycleReportPath = $null

Write-Log "P23 unified operator start | mode=$EffectiveMode (requested=$Mode) symbol=$Symbol tf=$Timeframe train=$TrainDate..$effectiveTrainEndDate test=$TestDate..$effectiveTestEndDate"
if ($EffectiveMode -eq "table_chain") {
    if ([string]::IsNullOrWhiteSpace($OosReportPath)) { throw "table_chain strict mode requires -OosReportPath (exact OOS file)." }
    if (-not (Test-Path $OosReportPath)) { throw "table_chain OOS file not found: $OosReportPath" }
}
Invoke-Step "00A" "preflight_window (raw)" { Run-PreflightRaw }
Invoke-Step "00B" "data_window_readiness (core test window)" { Run-CoreWindowReadiness }

if ($EffectiveMode -eq "long" -or $EffectiveMode -eq "short" -or $EffectiveMode -eq "combined" -or $EffectiveMode -eq "all") {
    $modesCsv = switch ($EffectiveMode) {
        "long" { "long_only" }
        "short" { "short_only" }
        default { "long_only,short_only" }
    }
    Invoke-Step "01" "daily_long_short_cycle ($modesCsv)" { 
        $res = Run-DailyCycle -modesCsv $modesCsv
        $script:dailyCycleReportPath = [string]$res.report_path
        Write-Log "Pinned daily cycle report: $script:dailyCycleReportPath"
    }
}

if ($EffectiveMode -eq "long" -or $EffectiveMode -eq "combined" -or $EffectiveMode -eq "all") {
    if ($dailyCycleReportPath) {
        $latestLongOos = Resolve-OosFromDailyCycleReport -dailyReportPath $dailyCycleReportPath -modeName "long_only"
    }
    if (-not $latestLongOos) { throw "Pinned long OOS was not resolved from daily cycle report: $dailyCycleReportPath" }
    Write-Log "Detected long OOS: $latestLongOos"
}
if ($EffectiveMode -eq "short" -or $EffectiveMode -eq "combined" -or $EffectiveMode -eq "all") {
    if ($dailyCycleReportPath) {
        $latestShortOos = Resolve-OosFromDailyCycleReport -dailyReportPath $dailyCycleReportPath -modeName "short_only"
    }
    if (-not $latestShortOos) { throw "Pinned short OOS was not resolved from daily cycle report: $dailyCycleReportPath" }
    Write-Log "Detected short OOS: $latestShortOos"
}
if ($EffectiveMode -eq "table_chain") {
    $latestShortOos = (Resolve-Path $OosReportPath).Path
    Write-Log "Using pinned OOS for table_chain: $latestShortOos"
}

$primaryOos = if ($latestShortOos) { $latestShortOos } elseif ($latestLongOos) { $latestLongOos } else { $null }
if (-not $primaryOos) {
    throw "Primary OOS report was not resolved."
}
$dailyReusable = $false
if ($dailyCycleReportPath -and (Test-Path $dailyCycleReportPath)) {
    try {
        $d = Get-Content $dailyCycleReportPath -Raw | ConvertFrom-Json
        $dailyStatusOk = ([string]$d.status -eq "PASS")
        $conv = @($d.steps | Where-Object { $_.task -like "table_convergence_5plus_*" })
        $convOk = ($conv.Count -gt 0 -and (@($conv | Where-Object { [int]$_.returncode -eq 0 }).Count -eq $conv.Count))
        $dailyReusable = ($dailyStatusOk -and $convOk)
        if (-not $dailyReusable) {
            Write-Log "Daily artifacts are not reusable (status=$($d.status), convergence_ok=$convOk)."
        }
    } catch {
        Write-Log "Daily report parse failed for reuse check; fallback to non-reuse mode."
        $dailyReusable = $false
    }
}
$reuseDailyArtifacts = ($skipConvFromDaily -and $dailyCycleReportPath -and $EffectiveMode -ne "table_chain" -and $dailyReusable)

try {
    $oosObj = Get-Content $primaryOos -Raw | ConvertFrom-Json
    $oosTrades = [int]$oosObj.backtest.trades
    $requireTradesForAudit = ($oosTrades -gt 0)
    Write-Log "Primary OOS trades=$oosTrades => require_trades_for_audit=$requireTradesForAudit"
}
catch {
    Write-Log "Primary OOS trades parse failed, fallback require_trades_for_audit=true"
    $requireTradesForAudit = $true
}

if ($reuseDailyArtifacts) {
    Write-Log "Skip table_canon_pack in P23: reuse artifacts produced by daily_long_short_cycle."
    $script:steps += [ordered]@{
        id = "02"
        title = "table_canon_pack (reused from daily cycle)"
        status = "SKIP"
        reason = "reuse_daily_cycle_artifacts"
    }
} else {
    Invoke-Step "02" "table_canon_pack (stable)" { Run-TableCanonPack }
}

if ($reuseDailyArtifacts) {
    Write-Log "Skip table_convergence in P23: already executed in daily_long_short_cycle for pinned OOS."
    $script:steps += [ordered]@{
        id = "03"
        title = "table_convergence_5plus (reused from daily cycle)"
        status = "SKIP"
        reason = "reuse_daily_cycle_oos"
    }
} else {
    if ($latestLongOos) {
        Invoke-Step "03L" "table_convergence_5plus (long)" { Run-TableConvergence -oosPath $latestLongOos }
    }
    if ($latestShortOos) {
        Invoke-Step "03S" "table_convergence_5plus (short)" { Run-TableConvergence -oosPath $latestShortOos }
    }
    if (-not $latestLongOos -and -not $latestShortOos) {
        Invoke-Step "03" "table_convergence_5plus (primary)" { Run-TableConvergence -oosPath $primaryOos }
    }
}

Invoke-Step "04" "audit_table_chain (adaptive require-trades)" { Run-AuditChain -RequireTrades $requireTradesForAudit }
Invoke-Step "05" "feature/orderbook/tz_gate/freeze checks" { Run-Gates -oosPath $primaryOos }

$summary = [ordered]@{
    status = "PASS"
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    mode = $EffectiveMode
    mode_requested = $Mode
    symbol = $Symbol
    timeframe = $Timeframe
    train_date = $TrainDate
    train_end_date = $effectiveTrainEndDate
    test_date = $TestDate
    test_end_date = $effectiveTestEndDate
    step_label = $StepLabel
    log_path = (Resolve-Path $logPath).Path
    daily_cycle_report_path = $dailyCycleReportPath
    pinned_oos = [ordered]@{
        long_only = $latestLongOos
        short_only = $latestShortOos
        primary = $primaryOos
    }
    steps = $script:steps
}
$summary | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath -Encoding UTF8
Write-Log "P23 unified operator complete. Summary: $(Resolve-Path $jsonPath)"
Write-Output ("{`"status`":`"PASS`",`"report_path`":`"$((Resolve-Path $jsonPath).Path)`"}")



