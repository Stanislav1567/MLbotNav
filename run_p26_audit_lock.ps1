param(
    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string]$TestDate = "2026-05-20",
    [string]$SourceP23ReportPath = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot
$env:PYTHONPATH = "src"
$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = ""
    try {
        $cmd = Get-Command python -ErrorAction Stop
        $python = [string]$cmd.Source
    } catch {}
    if ([string]::IsNullOrWhiteSpace($python)) {
        throw "Python runtime not found. Checked local venv and PATH."
    }
}

function Get-Latest([string]$pattern){
    Get-ChildItem $pattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
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

$rawPatterns = & $python -m mlbotnav.qa_required_patterns --role p26 --require-stress true 2>&1
if ($LASTEXITCODE -ne 0) { throw "qa_required_patterns(p26) failed with exit code $LASTEXITCODE" }
$patternsObj = Parse-JsonObject (($rawPatterns | Out-String))
if (-not $patternsObj) { throw "qa_required_patterns(p26) output JSON not found" }
$requiredReports = @($patternsObj.required_patterns)
if ($requiredReports.Count -eq 0) { throw "qa_required_patterns(p26) returned empty required_patterns" }

$rawExpect = & $python -m mlbotnav.qa_audit_lock_expectations --role p26 2>&1
if ($LASTEXITCODE -ne 0) { throw "qa_audit_lock_expectations(p26) failed with exit code $LASTEXITCODE" }
$expectObj = Parse-JsonObject (($rawExpect | Out-String))
if (-not $expectObj) { throw "qa_audit_lock_expectations(p26) output JSON not found" }
$requiredTables = @($expectObj.required_table_files)
if ($requiredTables.Count -eq 0) { throw "qa_audit_lock_expectations(p26) returned empty required_table_files" }
$lockFiles = @($expectObj.lock_files)
if ($lockFiles.Count -eq 0) { throw "qa_audit_lock_expectations(p26) returned empty lock_files" }

$resolvedSourceP23 = $null
$sourceP23Mode = ""
if (-not [string]::IsNullOrWhiteSpace($SourceP23ReportPath)) {
    if (-not (Test-Path $SourceP23ReportPath)) { throw "SourceP23ReportPath not found: $SourceP23ReportPath" }
    $resolvedSourceP23 = (Resolve-Path $SourceP23ReportPath).Path
} else {
    $latestP23 = Get-Latest "reports/qa_gate/p23_operator_unified_*.json"
    if ($latestP23) { $resolvedSourceP23 = $latestP23.FullName }
}
if ($resolvedSourceP23) {
    try {
        $p23 = Get-Content $resolvedSourceP23 -Raw | ConvertFrom-Json
        $sourceP23Mode = [string]$p23.mode
    } catch {
        $sourceP23Mode = ""
    }
}

$stampReq = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$reqPath = "reports/qa_gate/p26_contract_request_${stampReq}.json"
$req = [ordered]@{
    project_root = (Resolve-Path $ProjectRoot).Path
    required_patterns = $requiredReports
    source_p23_mode = $sourceP23Mode
}
$req | ConvertTo-Json -Depth 6 | Set-Content -Path $reqPath -Encoding UTF8

$rawContract = & $python -m mlbotnav.p26_audit_lock_contract --request-json $reqPath 2>&1
if ($LASTEXITCODE -ne 0) { throw "p26_audit_lock_contract failed with exit code $LASTEXITCODE" }
$contract = Parse-JsonObject (($rawContract | Out-String))
if (-not $contract) { throw "p26_audit_lock_contract output JSON not found" }

$reports = @($contract.reports)
$missing = @($contract.missing)
$fail = @($contract.non_pass_reports)

$tables = @()
foreach($t in $requiredTables){
    $exists = Test-Path $t
    if(-not $exists){ $missing += $t }
    $item = $null
    if($exists){ $item = Get-Item $t }
    $tables += [ordered]@{ file=(Resolve-Path $t -ErrorAction SilentlyContinue).Path; exists=$exists; bytes=$(if($item){$item.Length}else{0}); updated_utc=$(if($item){$item.LastWriteTimeUtc.ToString("o")}else{$null}) }
}

$hashes = @()
foreach($lf in $lockFiles){
    if(Test-Path $lf){
        $h = Get-FileHash $lf -Algorithm SHA256
        $it = Get-Item $lf
        $hashes += [ordered]@{ file=(Resolve-Path $lf).Path; sha256=$h.Hash; updated_utc=$it.LastWriteTimeUtc.ToString("o") }
    } else {
        $missing += $lf
    }
}

$status = if(($missing.Count -eq 0) -and ($fail.Count -eq 0)) { "PASS" } else { "FAIL" }
$payload = [ordered]@{
    status = $status
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    symbol = $Symbol
    timeframe = $Timeframe
    test_date = $TestDate
    source_p23_report_path = $resolvedSourceP23
    source_p23_mode = $sourceP23Mode
    missing = $missing
    non_pass_reports = $fail
    reports = $reports
    table_files = $tables
    lock_hashes = $hashes
}

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$out = "reports/qa_gate/p26_audit_lock_${stamp}.json"
$payload | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
Write-Output ("{`"status`":`"$status`",`"report_path`":`"$((Resolve-Path $out).Path)`"}")
if($status -ne "PASS"){ exit 1 }
