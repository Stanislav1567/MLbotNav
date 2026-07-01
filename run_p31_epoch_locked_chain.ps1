param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TrainDate = "2026-05-19",
    [string]$TestDate = "2026-05-20",
    [string]$OosReportPath = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot
$env:PYTHONPATH = "src"

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Python venv not found: $python" }
if ([string]::IsNullOrWhiteSpace($OosReportPath)) { throw "Provide -OosReportPath (exact short OOS json)." }
if (-not (Test-Path $OosReportPath)) { throw "OOS not found: $OosReportPath" }

function Parse-LastJson([string]$text){
    $lines = $text -split "`r?`n"
    for($i=$lines.Count-1; $i -ge 0; $i--){
        $l = $lines[$i].Trim()
        if([string]::IsNullOrWhiteSpace($l)){ continue }
        try { return ($l | ConvertFrom-Json) } catch {}
    }
    return $null
}

function Extract-ReportPath([string]$text){
    $obj = Parse-LastJson $text
    if($obj -and $obj.PSObject.Properties.Name -contains "report_path" -and -not [string]::IsNullOrWhiteSpace([string]$obj.report_path)){
        return [string]$obj.report_path
    }
    $m = [regex]::Matches($text, '"report_path"\s*:\s*"([^"]+)"')
    if($m.Count -gt 0){
        return [string]$m[$m.Count-1].Groups[1].Value
    }
    return $null
}

function Extract-ReportPathByPattern([string]$text, [string]$mustContain){
    $lines = $text -split "`r?`n"
    for($i=$lines.Count-1; $i -ge 0; $i--){
        $l = $lines[$i]
        if([string]::IsNullOrWhiteSpace($l)){ continue }
        if($l -match '"report_path"\s*:\s*"([^"]+)"'){
            $rp = [string]$matches[1]
            if($rp -like "*$mustContain*"){ return $rp }
        }
    }
    $m = [regex]::Matches($text, '"report_path"\s*:\s*"([^"]+)"')
    for($i=$m.Count-1; $i -ge 0; $i--){
        $rp = [string]$m[$i].Groups[1].Value
        if($rp -like "*$mustContain*"){ return $rp }
    }
    return $null
}

# 1) P23 strict table_chain pinned OOS
$rawP23 = powershell -ExecutionPolicy Bypass -File .\run_p23_operator_unified.ps1 -Mode table_chain -Symbol $Symbol -Timeframe $Timeframe -TrainDate $TrainDate -TestDate $TestDate -OosReportPath $OosReportPath -StepLabel P23 2>&1 | Out-String
$rawP23 | Out-Host
$p23Path = Extract-ReportPathByPattern $rawP23 "p23_operator_unified_"
if([string]::IsNullOrWhiteSpace($p23Path)){ throw "Cannot parse p23 report_path" }

# 2) P24 strict with epoch-lock + exact p23 match
$rawP24 = powershell -ExecutionPolicy Bypass -File .\run_p24_latest_pass_report.ps1 -SourceP23ReportPath $p23Path 2>&1 | Out-String
$rawP24 | Out-Host
$p24Path = Extract-ReportPathByPattern $rawP24 "p24_latest_pass_"
if([string]::IsNullOrWhiteSpace($p24Path)){ throw "Cannot parse p24 report_path" }
$p24Json = Get-Content $p24Path -Raw | ConvertFrom-Json
if([string]$p24Json.status -ne "PASS"){ throw "p24 status is not PASS: $($p24Json.status)" }

# resolve exact artifact paths from p24 items
function Get-ItemPath([object]$items, [string]$pattern){
    $it = $items | Where-Object { $_.pattern -eq $pattern } | Select-Object -First 1
    if($null -eq $it){ return $null }
    return [string]$it.file
}
$items = $p24Json.items
$conv = Get-ItemPath $items "reports/qa_gate/table_convergence_5plus_*.json"
$feat = Get-ItemPath $items "reports/qa_gate/features_block_audit_*.json"
$orderbook = Get-ItemPath $items "reports/qa_gate/orderbook_source_audit_*.json"
$tz = Get-ItemPath $items "reports/qa_gate/tz_gate_*.json"
$p72 = Get-ItemPath $items "reports/qa_gate/p72_freeze_ready_*.json"

# 3) chain manifest pinned
$rawManifest = & $python -m mlbotnav.akfp_chain_manifest --symbol $Symbol --timeframe $Timeframe --test-day $TestDate --output-dir reports/akfp/chain_manifest --long-pkg reports/akfp/final_long/LONG_FINAL_PACKAGE.json --short-pkg reports/akfp/final_short/SHORT_FINAL_PACKAGE.json --long-oos reports/final_review/oos_report_${Symbol}_${Timeframe}_${TestDate}_long_only_20260525T023454Z.json --short-oos $OosReportPath --p23-report $p23Path --p24-report $p24Path --tz-report $tz --convergence-report $conv --p72-report $p72 --chain-report reports/table_canon_current/audit_chain_report.json 2>&1 | Out-String
$rawManifest | Out-Host
$manifestObj = Parse-LastJson $rawManifest
if(-not $manifestObj -or -not $manifestObj.manifest_path){ throw "Cannot parse manifest_path" }
$manifestPath = [string]$manifestObj.manifest_path

# 4) combined by manifest
$rawCombined = & $python -m mlbotnav.akfp_combined_consistency --test-day $TestDate --output-dir reports/akfp/combined --chain-manifest $manifestPath 2>&1 | Out-String
$rawCombined | Out-Host
$combinedPath = Extract-ReportPathByPattern $rawCombined "akfp_combined_consistency_"
if([string]::IsNullOrWhiteSpace($combinedPath)){ throw "Cannot parse combined report_path" }

# 5) finalize by same manifest + same combined
$rawFinalize = & $python -m mlbotnav.akfp_finalize --policy configs/akfp_policy.yaml --output-dir reports/akfp/finalization --chain-manifest $manifestPath --combined-report $combinedPath 2>&1 | Out-String
$rawFinalize | Out-Host
$finalizePath = Extract-ReportPathByPattern $rawFinalize "akfp_p12_finalize_"
if([string]::IsNullOrWhiteSpace($finalizePath)){ throw "Cannot parse finalize report_path" }

$out = [ordered]@{
    status = "PASS"
    p23_report = $p23Path
    p24_report = $p24Path
    manifest_path = $manifestPath
    combined_report = $combinedPath
    finalize_report = $finalizePath
}
$out | ConvertTo-Json -Depth 6 | Out-Host
