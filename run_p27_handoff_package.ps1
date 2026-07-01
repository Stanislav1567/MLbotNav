param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TestDate = "2026-05-20",
    [string]$StepLabel = "P27"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot

function Get-Latest([string]$pattern){
    Get-ChildItem $pattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
}

$artifactPatterns = @(
    "reports/qa_gate/p23_operator_unified_*.json",
    "reports/qa_gate/daily_long_short_cycle_*.json",
    "reports/qa_gate/table_convergence_5plus_*.json",
    "reports/table_canon_current/audit_chain_report.json",
    "reports/qa_gate/features_block_audit_*.json",
    "reports/qa_gate/orderbook_source_audit_*.json",
    "reports/qa_gate/tz_gate_*.json",
    "reports/qa_gate/p72_freeze_ready_*.json",
    "reports/qa_gate/p62_runtime_io_manifest_*.json",
    "reports/final_review/stress_backtest_contour_*.json",
    "reports/qa_gate/p24_latest_pass_*.json",
    "reports/qa_gate/p26_audit_lock_*.json"
)

$manifestStamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$manifestOut = "reports/qa_gate/p62_runtime_io_manifest_${manifestStamp}.json"
$srcPath = Join-Path $ProjectRoot "src"
if([string]::IsNullOrWhiteSpace($env:PYTHONPATH)){
    $env:PYTHONPATH = $srcPath
} elseif(-not ($env:PYTHONPATH -split ';' | Where-Object { $_ -eq $srcPath })){
    $env:PYTHONPATH = "$srcPath;$($env:PYTHONPATH)"
}
$pythonExe = Join-Path $ProjectRoot ".venv\\Scripts\\python.exe"
if(Test-Path $pythonExe){
    & $pythonExe -m mlbotnav.runtime_io_manifest --require-stress true --write-json $manifestOut | Out-Null
} else {
    python -m mlbotnav.runtime_io_manifest --require-stress true --write-json $manifestOut | Out-Null
}
if($LASTEXITCODE -ne 0){ throw "P27: runtime_io_manifest export failed" }

$cmds = [ordered]@{
    combined = "powershell -ExecutionPolicy Bypass -File .\\run_p23_operator_unified.ps1 -Mode combined -StepLabel $StepLabel"
    long = "powershell -ExecutionPolicy Bypass -File .\\run_p23_operator_unified.ps1 -Mode long -StepLabel $StepLabel"
    short = "powershell -ExecutionPolicy Bypass -File .\\run_p23_operator_unified.ps1 -Mode short -StepLabel $StepLabel"
    table_chain = "powershell -ExecutionPolicy Bypass -File .\\run_p23_operator_unified.ps1 -Mode table_chain -StepLabel $StepLabel"
    latest_pass = "powershell -ExecutionPolicy Bypass -File .\\run_p24_latest_pass_report.ps1"
    audit_lock = "powershell -ExecutionPolicy Bypass -File .\\run_p26_audit_lock.ps1 -Symbol $Symbol -Timeframe $Timeframe -TestDate $TestDate"
    runtime_io_manifest = "python -m mlbotnav.runtime_io_manifest --require-stress true --write-json <reports/qa_gate/p62_runtime_io_manifest_*.json>"
}

$items = @()
$missing = @()
foreach($p in $artifactPatterns){
    if($p -like "*audit_chain_report.json"){
        if(Test-Path $p){
            $f = Get-Item $p
            $status = "unknown"
            try {
                $j = Get-Content $f.FullName -Raw | ConvertFrom-Json
                if($j.PSObject.Properties.Name -contains "status"){ $status = [string]$j.status }
            } catch {}
            $items += [ordered]@{ pattern=$p; file=$f.FullName; status=$status; updated_utc=$f.LastWriteTimeUtc.ToString("o") }
        } else {
            $missing += $p
            $items += [ordered]@{ pattern=$p; file=$null; status="missing"; updated_utc=$null }
        }
        continue
    }

    $f = Get-Latest $p
    if($null -eq $f){
        $missing += $p
        $items += [ordered]@{ pattern=$p; file=$null; status="missing"; updated_utc=$null }
        continue
    }
    $status = "unknown"
    try {
        $j = Get-Content $f.FullName -Raw | ConvertFrom-Json
        if($j.PSObject.Properties.Name -contains "status"){ $status = [string]$j.status }
    } catch {}
    $items += [ordered]@{ pattern=$p; file=$f.FullName; status=$status; updated_utc=$f.LastWriteTimeUtc.ToString("o") }
}

$requiredPassPatterns = @(
    "reports/qa_gate/p23_operator_unified_*.json",
    "reports/qa_gate/p24_latest_pass_*.json",
    "reports/qa_gate/p26_audit_lock_*.json",
    "reports/table_canon_current/audit_chain_report.json",
    "reports/qa_gate/p72_freeze_ready_*.json",
    "reports/final_review/stress_backtest_contour_*.json"
)

$requiredFailures = @()
foreach($rp in $requiredPassPatterns){
    $m = $items | Where-Object { $_.pattern -eq $rp } | Select-Object -First 1
    if($null -eq $m){
        $requiredFailures += [ordered]@{ pattern=$rp; reason="required_pattern_not_collected" }
        continue
    }
    if($m.status -ne "PASS"){
        $requiredFailures += [ordered]@{ pattern=$rp; reason="required_status_not_pass"; status=$m.status; file=$m.file }
    }
}

$allPass = (($items | Where-Object { $_.status -eq "missing" }).Count -eq 0) -and ($requiredFailures.Count -eq 0)
$status = if($allPass){"PASS"}else{"WARN"}

$payload = [ordered]@{
    status = $status
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    step_label = $StepLabel
    symbol = $Symbol
    timeframe = $Timeframe
    test_date = $TestDate
    commands = $cmds
    artifacts = $items
    missing = $missing
    required_pass_patterns = $requiredPassPatterns
    required_failures = $requiredFailures
}

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$out = "reports/qa_gate/p27_handoff_package_${stamp}.json"
$payload | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
Write-Output ("{`"status`":`"$status`",`"report_path`":`"$((Resolve-Path $out).Path)`"}")
if($status -eq "WARN"){ exit 0 }



