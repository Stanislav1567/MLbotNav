param(
    [ValidateSet("BuildBatch", "TrainingGuard", "Train", "Forward", "TrainForward", "All", "RenderForward", "RiskGate")]
    [string]$Mode = "All",
    [string]$TrainRunId = "",
    [string]$ForwardRunId = "",
    [string]$TrainStartDay = "2026-01-27",
    [string]$TrainEndDay = "2026-03-06",
    [string]$ForwardStartDay = "2026-03-07",
    [string]$ForwardEndDay = "2026-03-13",
    [string]$ContextStartDay = "2026-01-27",
    [int]$ContextWarmupMinutes = 720,
    [ValidateSet("Trained", "Normal", "WideReview")]
    [string]$EntryDecisionPolicy = "Trained",
    [string]$TrainManifestPath = "",
    [string[]]$RiskGateUserPassIds = @(),
    [switch]$ForceFull274Collect,
    [switch]$SkipRiskGateML,
    [switch]$DisableRiskGateML,
    [switch]$BollingerPreview,
    [switch]$NoStrict,
    [switch]$SkipVisualReview,
    [switch]$OpenFolder
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
    param([string]$Day)
    return ([datetime]::ParseExact($Day, "yyyy-MM-dd", $null)).ToString("yyyyMMdd")
}

function Get-DayRange {
    param([string]$StartDay, [string]$EndDay)
    $start = [datetime]::ParseExact($StartDay, "yyyy-MM-dd", $null)
    $end = [datetime]::ParseExact($EndDay, "yyyy-MM-dd", $null)
    $days = @()
    for ($d = $start; $d -le $end; $d = $d.AddDays(1)) {
        $days += $d.ToString("yyyy-MM-dd")
    }
    return $days
}

function Get-LatestFull274Run {
    param([string]$Day)
    $compact = Get-CompactDay -Day $Day
    $runsRoot = Join-Path $RepoRoot "STAS5_ML_CORE\runs"
    if (-not (Test-Path -LiteralPath $runsRoot)) {
        return $null
    }
    return Get-ChildItem -LiteralPath $runsRoot -Directory |
        Where-Object { $_.Name -like "full274_feature_collect_${compact}_*" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

function Ensure-Full274 {
    param([string]$Day)
    $existing = Get-LatestFull274Run -Day $Day
    if ($existing -and -not $ForceFull274Collect) {
        Write-Host "FULL274 exists for ${Day}: $($existing.Name)"
        return
    }
    Write-Host "Collect FULL274 for $Day"
    & (Join-Path $RepoRoot "STAS5_ML_CORE\run_stas5_full274_feature_collect.ps1") `
        -Day $Day `
        -OutcomeLookaheadHours 48 `
        -Stas1RenderGoodLimit 0 `
        -Stas2RenderLimit 0
    if ($LASTEXITCODE -ne 0) {
        throw "FULL274 collect failed for $Day with exit code $LASTEXITCODE"
    }
}

function Invoke-V5C {
    param([string[]]$ArgsList)
    & $Python @ArgsList
    if ($LASTEXITCODE -ne 0) {
        throw "stas5_v5_continuous_ml failed with exit code $LASTEXITCODE"
    }
}

function Invoke-V5VisualReview {
    param([string[]]$ArgsList)
    & $Python @ArgsList
    if ($LASTEXITCODE -ne 0) {
        throw "stas5_v5_forward_visual_review failed with exit code $LASTEXITCODE"
    }
}

function Invoke-V5RiskGate {
    param([string[]]$ArgsList)
    & $Python @ArgsList
    if ($LASTEXITCODE -ne 0) {
        throw "stas5_v5c_riskgate_audit failed with exit code $LASTEXITCODE"
    }
}

function Get-V5CForwardRunDir {
    if ($ForwardRunId) {
        return Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5c\forward\runs\$ForwardRunId"
    }
    $latestForward = Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5c\forward\STAS5_V5C_LATEST_TWO_BLOCK_FORWARD_RUN.json"
    if (-not (Test-Path -LiteralPath $latestForward)) {
        throw "Latest V5C forward pointer not found: $latestForward"
    }
    $payload = Get-Content -LiteralPath $latestForward -Raw | ConvertFrom-Json
    return Join-Path $RepoRoot $payload.run_dir
}

if ($Mode -eq "RenderForward") {
    $runDir = Get-V5CForwardRunDir
    $argsList = @(
        "-m", "mlbotnav.stas5_v5_forward_visual_review",
        "--forward-run-dir", $runDir,
        "--start-day", $ForwardStartDay,
        "--end-day", $ForwardEndDay
    )
    if ($NoStrict) { $argsList += "--no-strict" }
    if ($BollingerPreview) { $argsList += "--bollinger-preview" }
    Invoke-V5VisualReview -ArgsList $argsList
    if ($OpenFolder) {
        Invoke-Item -LiteralPath (Join-Path $runDir "visual_review")
    }
    return
}

if ($Mode -eq "RiskGate") {
    $runDir = Get-V5CForwardRunDir
    $argsList = @(
        "-m", "mlbotnav.stas5_v5c_riskgate_audit",
        "--forward-run-dir", $runDir,
        "--start-day", $ForwardStartDay,
        "--end-day", $ForwardEndDay
    )
    if ($RiskGateUserPassIds -and $RiskGateUserPassIds.Count -gt 0) {
        $argsList += @("--user-pass-ids", ($RiskGateUserPassIds -join ","))
    }
    if ($SkipVisualReview) { $argsList += "--skip-visual" }
    if ($NoStrict) { $argsList += "--no-strict" }
    Invoke-V5RiskGate -ArgsList $argsList
    if ($OpenFolder) {
        Invoke-Item -LiteralPath (Join-Path $runDir "riskgate_audit")
    }
    return
}

if ($Mode -eq "BuildBatch" -or $Mode -eq "All") {
    $argsList = @(
        "-m", "mlbotnav.stas5_v5_continuous_ml",
        "--mode", "build-batch",
        "--train-start-day", $TrainStartDay,
        "--train-end-day", $TrainEndDay,
        "--context-start-day", $ContextStartDay,
        "--context-warmup-minutes", "$ContextWarmupMinutes"
    )
    if ($NoStrict) { $argsList += "--no-strict" }
    Invoke-V5C -ArgsList $argsList
    if ($Mode -eq "BuildBatch") { return }
}

if ($Mode -eq "TrainingGuard") {
    $argsList = @(
        "-m", "mlbotnav.stas5_v5_continuous_ml",
        "--mode", "training-guard",
        "--train-start-day", $TrainStartDay,
        "--train-end-day", $TrainEndDay
    )
    if ($TrainRunId) { $argsList += @("--train-run-id", $TrainRunId) }
    if ($NoStrict) { $argsList += "--no-strict" }
    Invoke-V5C -ArgsList $argsList
    return
}

if ($Mode -eq "Train" -or $Mode -eq "TrainForward" -or $Mode -eq "All") {
    $argsList = @(
        "-m", "mlbotnav.stas5_v5_continuous_ml",
        "--mode", "train",
        "--train-start-day", $TrainStartDay,
        "--train-end-day", $TrainEndDay
    )
    if ($TrainRunId) { $argsList += @("--train-run-id", $TrainRunId) }
    if ($SkipRiskGateML) { $argsList += "--skip-riskgate-ml" }
    if ($NoStrict) { $argsList += "--no-strict" }
    Invoke-V5C -ArgsList $argsList
    if ($Mode -eq "Train") { return }
}

if ($Mode -eq "Forward" -or $Mode -eq "TrainForward" -or $Mode -eq "All") {
    foreach ($day in (Get-DayRange -StartDay $ForwardStartDay -EndDay $ForwardEndDay)) {
        Ensure-Full274 -Day $day
    }
    $argsList = @(
        "-m", "mlbotnav.stas5_v5_continuous_ml",
        "--mode", "forward",
        "--forward-start-day", $ForwardStartDay,
        "--forward-end-day", $ForwardEndDay,
        "--context-start-day", $ContextStartDay,
        "--context-warmup-minutes", "$ContextWarmupMinutes"
    )
    if ($EntryDecisionPolicy -eq "Normal") { $argsList += @("--entry-decision-policy", "normal") }
    if ($EntryDecisionPolicy -eq "WideReview") { $argsList += @("--entry-decision-policy", "wide_review") }
    if ($ForwardRunId) { $argsList += @("--forward-run-id", $ForwardRunId) }
    if ($TrainManifestPath) { $argsList += @("--train-manifest-path", $TrainManifestPath) }
    if ($DisableRiskGateML) { $argsList += "--disable-riskgate-ml" }
    if ($NoStrict) { $argsList += "--no-strict" }
    if ($SkipVisualReview) { $argsList += "--skip-visual-review" }
    if ($BollingerPreview) { $argsList += "--bollinger-preview" }
    Invoke-V5C -ArgsList $argsList
}

if ($OpenFolder) {
    $latestForward = Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5c\forward\STAS5_V5C_LATEST_TWO_BLOCK_FORWARD_RUN.json"
    if (Test-Path -LiteralPath $latestForward) {
        $payload = Get-Content -LiteralPath $latestForward -Raw | ConvertFrom-Json
        Invoke-Item -LiteralPath (Join-Path $RepoRoot $payload.run_dir)
    } else {
        $latestModel = Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5c\model\STAS5_V5C_LATEST_TWO_BLOCK_MODEL_RUN.json"
        if (Test-Path -LiteralPath $latestModel) {
            $payload = Get-Content -LiteralPath $latestModel -Raw | ConvertFrom-Json
            Invoke-Item -LiteralPath (Join-Path $RepoRoot $payload.run_dir)
        }
    }
}
