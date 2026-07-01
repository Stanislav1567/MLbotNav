param(
    [string]$SourceP23ReportPath = "",
    [int]$EpochLookbackMinutes = 20,
    [switch]$DisableEpochLock,
    [bool]$RequireStressContour = $true,
    [string[]]$EpochLockBaselineAllowedPatterns = @()
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

function Get-LatestAfter([string]$pattern, [datetime]$cutoffUtc){
    Get-ChildItem $pattern -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTimeUtc -ge $cutoffUtc } |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
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

$rawPatterns = & $python -m mlbotnav.qa_required_patterns --role p24 --require-stress $RequireStressContour 2>&1
if ($LASTEXITCODE -ne 0) { throw "qa_required_patterns(p24) failed with exit code $LASTEXITCODE" }
$patternsObj = Parse-JsonObject (($rawPatterns | Out-String))
if (-not $patternsObj) { throw "qa_required_patterns(p24) output JSON not found" }
$patterns = @($patternsObj.required_patterns)
if ($patterns.Count -eq 0) { throw "qa_required_patterns(p24) returned empty required_patterns" }

$resolvedBypass = @()
if ($PSBoundParameters.ContainsKey("EpochLockBaselineAllowedPatterns")) {
    $resolvedBypass = @($EpochLockBaselineAllowedPatterns)
} else {
    $resolvedBypass = @($patternsObj.epoch_lock_baseline_allowed_patterns)
}
$epochLockBypassPatterns = @($resolvedBypass | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { $_.Trim() })

$resolvedSourceP23 = $null
$sourceP23Mode = ""
$epochFloorUtc = $null
$epochCutoffUtc = $null
if (-not [string]::IsNullOrWhiteSpace($SourceP23ReportPath)) {
    if (-not (Test-Path $SourceP23ReportPath)) { throw "SourceP23ReportPath not found: $SourceP23ReportPath" }
    $resolvedSourceP23 = (Resolve-Path $SourceP23ReportPath).Path
    $p23File = Get-Item $resolvedSourceP23
    $epochFloorUtc = $p23File.LastWriteTimeUtc
    $epochCutoffUtc = $epochFloorUtc.AddMinutes(-1 * [math]::Abs([int]$EpochLookbackMinutes))
    try {
        $p23 = Get-Content $resolvedSourceP23 -Raw | ConvertFrom-Json
        $sourceP23Mode = [string]$p23.mode
    } catch {
        $sourceP23Mode = ""
    }
}

$epochLockEnabled = ($resolvedSourceP23 -ne $null -and -not $DisableEpochLock)

$stampReq = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$reqPath = "reports/qa_gate/p24_contract_request_${stampReq}.json"
$req = [ordered]@{
    project_root = (Resolve-Path $ProjectRoot).Path
    patterns = $patterns
    source_p23_mode = $sourceP23Mode
    resolved_source_p23 = $resolvedSourceP23
    epoch_lock_enabled = [bool]$epochLockEnabled
    epoch_cutoff_utc = $(if($epochCutoffUtc){$epochCutoffUtc.ToString("o")}else{$null})
    epoch_lock_bypass_patterns = $epochLockBypassPatterns
}
$req | ConvertTo-Json -Depth 6 | Set-Content -Path $reqPath -Encoding UTF8

$rawContract = & $python -m mlbotnav.p24_latest_pass_contract --request-json $reqPath 2>&1
if ($LASTEXITCODE -ne 0) { throw "p24_latest_pass_contract failed with exit code $LASTEXITCODE" }
$contract = Parse-JsonObject (($rawContract | Out-String))
if (-not $contract) { throw "p24_latest_pass_contract output JSON not found" }

$items = @($contract.items)
$pass = [int]$contract.pass_count
$nonPass = [int]$contract.non_pass_count
$miss = [int]$contract.missing_count
$epochMiss = [int]$contract.epoch_locked_missing_count
$p23PathUsed = [string]$contract.p23_report_used
$p23Exact = [bool]$contract.p23_exact_match

$out = [ordered]@{
    status = $(if($miss -eq 0 -and $nonPass -eq 0 -and $p23Exact){"PASS"}else{"FAIL"})
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    source_p23_report_path = $resolvedSourceP23
    source_p23_mode = $sourceP23Mode
    p23_report_used = $p23PathUsed
    p23_exact_match = $p23Exact
    epoch_lock_enabled = $epochLockEnabled
    epoch_lock_baseline_allowed_patterns = $epochLockBypassPatterns
    epoch_lookback_minutes = [int]$EpochLookbackMinutes
    epoch_floor_utc = $(if($epochFloorUtc){$epochFloorUtc.ToString("o")}else{$null})
    epoch_cutoff_utc = $(if($epochCutoffUtc){$epochCutoffUtc.ToString("o")}else{$null})
    pass_count = $pass
    non_pass_count = $nonPass
    missing_count = $miss
    epoch_locked_missing_count = $epochMiss
    items = $items
}

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outPath = "reports/qa_gate/p24_latest_pass_${stamp}.json"
$out | ConvertTo-Json -Depth 8 | Set-Content -Path $outPath -Encoding UTF8
Write-Output ("{`"status`":`"$($out.status)`",`"report_path`":`"$((Resolve-Path $outPath).Path)`"}")
