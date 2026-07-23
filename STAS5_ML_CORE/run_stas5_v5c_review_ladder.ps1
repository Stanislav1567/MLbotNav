param(
    [Parameter(Mandatory = $true)]
    [string]$Day,

    [string]$Round = "R4",

    [string]$ForwardRunId = "",
    [string]$ForwardRunDir = "",

    [string]$Review = "",
    [string]$ReviewFile = "",

    [ValidateSet("Parse", "SaveReview", "BuildEntryDay", "RiskGate", "All", "Open")]
    [string]$Stage = "Parse",

    [switch]$Approve,
    [switch]$Force,
    [switch]$OpenFolder,
    [switch]$NoStrict,
    [switch]$NoPlot
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $RepoRoot
$env:PYTHONPATH = Join-Path $RepoRoot "src"

$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

function Get-CompactDay {
    param([string]$Value)
    return ([datetime]::ParseExact($Value, "yyyy-MM-dd", $null)).ToString("yyyyMMdd")
}

function Invoke-PythonJson {
    param([string[]]$ArgsList)
    $output = & $Python @ArgsList
    if ($LASTEXITCODE -ne 0) {
        throw "stas5_v5c_review_ladder failed with exit code $LASTEXITCODE"
    }
    $json = ($output -join "`n").Trim()
    if (-not $json) {
        throw "stas5_v5c_review_ladder returned empty output"
    }
    return $json | ConvertFrom-Json
}

function To-StringArray {
    param($Value)
    $out = @()
    if ($null -eq $Value) {
        return $out
    }
    foreach ($item in @($Value)) {
        if ($null -ne $item -and "$item" -ne "") {
            $out += "$item"
        }
    }
    return $out
}

if ($Stage -eq "Open") {
    $compact = Get-CompactDay -Value $Day
    $dir = Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5c\review\$($Round.ToLower())_user_review\$compact"
    if (-not (Test-Path -LiteralPath $dir)) {
        throw "Review folder not found: $dir"
    }
    Invoke-Item -LiteralPath $dir
    return
}

if (-not $Review -and -not $ReviewFile) {
    throw "Provide -Review or -ReviewFile."
}

$buildEntry = $Stage -eq "BuildEntryDay" -or $Stage -eq "All"
$runRiskGate = $Stage -eq "RiskGate"

if ($buildEntry -and -not $Approve) {
    Write-Host "Stage $Stage implies approved review because day ladder will be rebuilt."
    $Approve = $true
}

$argsList = @(
    "-m", "mlbotnav.stas5_v5c_review_ladder",
    "--day", $Day,
    "--round-id", $Round
)
if ($ForwardRunId) { $argsList += @("--forward-run-id", $ForwardRunId) }
if ($ForwardRunDir) { $argsList += @("--forward-run-dir", $ForwardRunDir) }
if ($Review) { $argsList += @("--review", $Review) }
if ($ReviewFile) { $argsList += @("--review-file", $ReviewFile) }
if ($Approve) { $argsList += "--approve" }
if ($Force) { $argsList += "--force" }
if ($Stage -eq "Parse") { $argsList += "--dry-run" }

$result = Invoke-PythonJson -ArgsList $argsList

Write-Host "== STAS5 V5C Review Ladder =="
Write-Host "Status:     $($result.status)"
Write-Host "Day:        $($result.day)"
Write-Host "Round:      $($result.round_id)"
Write-Host "Forward:    $($result.forward_run_id)"
Write-Host "ENTRY GOOD: $((To-StringArray $result.entry_good_ids) -join ',')"
Write-Host "ENTRY BAD:  $((To-StringArray $result.entry_bad_ids) -join ',')"
Write-Host "RISK BAD:   $((To-StringArray $result.risk_bad_ids) -join ',')"
if ($result.outputs.all_entries_png) {
    Write-Host "All entries graph: $($result.outputs.all_entries_png)"
}
if ($result.outputs.annotated_png) {
    Write-Host "Annotated graph:   $($result.outputs.annotated_png)"
}
Write-Host ""

if ($buildEntry) {
    $goodIds = To-StringArray $result.entry_good_ids
    if ($goodIds.Count -eq 0) {
        Write-Host "Skip day ladder: no ENTRY GOOD ids." -ForegroundColor Yellow
    } else {
        Write-Host "== Build V5 day package from ENTRY GOOD ids =="
        $dayLadderScript = Join-Path $RepoRoot "STAS5_ML_CORE\run_stas5_v5_day_ladder.ps1"
        & $dayLadderScript `
            -Day $Day `
            -Stage All `
            -GoodIds $goodIds `
            -NoStrict:$NoStrict `
            -NoPlot:$NoPlot
        if ($LASTEXITCODE -ne 0) {
            throw "run_stas5_v5_day_ladder failed with exit code $LASTEXITCODE"
        }
    }
}

if ($runRiskGate) {
    if (-not $ForwardRunId -and -not $ForwardRunDir) {
        Write-Host "Skip RiskGate audit: provide -ForwardRunId or -ForwardRunDir." -ForegroundColor Yellow
    } else {
        Write-Host "== Run RiskGate audit-only overlay =="
        $riskForwardRunId = $ForwardRunId
        if (-not $riskForwardRunId -and $ForwardRunDir) {
            $riskForwardRunId = Split-Path -Leaf $ForwardRunDir
        }
        $riskArgs = @(
            "-Mode", "RiskGate",
            "-ForwardStartDay", $Day,
            "-ForwardEndDay", $Day,
            "-ForwardRunId", $riskForwardRunId
        )
        if ($NoStrict) { $riskArgs += "-NoStrict" }
        & (Join-Path $RepoRoot "STAS5_ML_CORE\run_stas5_v5c_continuous_train_forward.ps1") @riskArgs
        if ($LASTEXITCODE -ne 0) {
            throw "RiskGate audit failed with exit code $LASTEXITCODE"
        }
    }
}

if ($OpenFolder -and $result.outputs.result_json) {
    $resultPath = Join-Path $RepoRoot $result.outputs.result_json
    if (Test-Path -LiteralPath $resultPath) {
        Invoke-Item -LiteralPath (Split-Path -Parent $resultPath)
    }
}
