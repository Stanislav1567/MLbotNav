param(
    [ValidateSet("TrainingGuard", "Train", "Forward", "TrainForward", "RenderForward")]
    [string]$Mode = "TrainForward",
    [string]$TrainRunId = "",
    [string]$ForwardRunId = "",
    [string]$ForwardStartDay = "2026-02-28",
    [string]$ForwardEndDay = "2026-03-06",
    [switch]$ForceFull274Collect,
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

function Invoke-V5TwoBlock {
    param([string[]]$ArgsList)
    & $Python @ArgsList
    if ($LASTEXITCODE -ne 0) {
        throw "stas5_v5_two_block_ml failed with exit code $LASTEXITCODE"
    }
}

function Invoke-V5VisualReview {
    param([string[]]$ArgsList)
    & $Python @ArgsList
    if ($LASTEXITCODE -ne 0) {
        throw "stas5_v5_forward_visual_review failed with exit code $LASTEXITCODE"
    }
}

function Get-V5ForwardRunDir {
    if ($ForwardRunId) {
        return Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5\forward\runs\$ForwardRunId"
    }
    $latestForward = Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5\forward\STAS5_V5_LATEST_TWO_BLOCK_FORWARD_RUN.json"
    if (-not (Test-Path -LiteralPath $latestForward)) {
        throw "Latest V5 forward pointer not found: $latestForward"
    }
    $payload = Get-Content -LiteralPath $latestForward -Raw | ConvertFrom-Json
    return Join-Path $RepoRoot $payload.run_dir
}

if ($Mode -eq "RenderForward") {
    $runDir = Get-V5ForwardRunDir
    $argsList = @(
        "-m", "mlbotnav.stas5_v5_forward_visual_review",
        "--forward-run-dir", $runDir,
        "--start-day", $ForwardStartDay,
        "--end-day", $ForwardEndDay
    )
    if ($NoStrict) { $argsList += "--no-strict" }
    Invoke-V5VisualReview -ArgsList $argsList
    if ($OpenFolder) {
        Invoke-Item -LiteralPath (Join-Path $runDir "visual_review")
    }
    return
}

if ($Mode -eq "TrainingGuard") {
    $argsList = @("-m", "mlbotnav.stas5_v5_two_block_ml", "--mode", "training-guard")
    if ($TrainRunId) { $argsList += @("--run-id", $TrainRunId) }
    if ($NoStrict) { $argsList += "--no-strict" }
    Invoke-V5TwoBlock -ArgsList $argsList
    return
}

if ($Mode -eq "Train" -or $Mode -eq "TrainForward") {
    $argsList = @("-m", "mlbotnav.stas5_v5_two_block_ml", "--mode", "train")
    if ($TrainRunId) { $argsList += @("--run-id", $TrainRunId) }
    if ($NoStrict) { $argsList += "--no-strict" }
    Invoke-V5TwoBlock -ArgsList $argsList
}

if ($Mode -eq "Forward" -or $Mode -eq "TrainForward") {
    foreach ($day in (Get-DayRange -StartDay $ForwardStartDay -EndDay $ForwardEndDay)) {
        Ensure-Full274 -Day $day
    }
    $argsList = @(
        "-m", "mlbotnav.stas5_v5_two_block_ml",
        "--mode", "forward",
        "--start-day", $ForwardStartDay,
        "--end-day", $ForwardEndDay
    )
    if ($ForwardRunId) { $argsList += @("--run-id", $ForwardRunId) }
    if ($NoStrict) { $argsList += "--no-strict" }
    if ($SkipVisualReview) { $argsList += "--skip-visual-review" }
    Invoke-V5TwoBlock -ArgsList $argsList
}

if ($OpenFolder) {
    $latestForward = Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5\forward\STAS5_V5_LATEST_TWO_BLOCK_FORWARD_RUN.json"
    if (Test-Path -LiteralPath $latestForward) {
        $payload = Get-Content -LiteralPath $latestForward -Raw | ConvertFrom-Json
        Invoke-Item -LiteralPath (Join-Path $RepoRoot $payload.run_dir)
    } else {
        $latestModel = Join-Path $RepoRoot "STAS5_ML_CORE\artifacts\v5\model\STAS5_V5_LATEST_TWO_BLOCK_MODEL_RUN.json"
        if (Test-Path -LiteralPath $latestModel) {
            $payload = Get-Content -LiteralPath $latestModel -Raw | ConvertFrom-Json
            Invoke-Item -LiteralPath (Join-Path $RepoRoot $payload.run_dir)
        }
    }
}
