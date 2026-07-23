param(
    [ValidateSet("R2", "R3", "R4")]
    [string]$Round = "R2",

    [string]$ForwardRunId = "",

    [string]$Days = "",

    [switch]$BollingerPreview,

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

$argsList = @(
    "-m", "mlbotnav.stas5_v5c_review_gallery",
    "--round-id", $Round
)
if ($ForwardRunId) { $argsList += @("--forward-run-id", $ForwardRunId) }
if ($Days) { $argsList += @("--days", $Days) }
if ($BollingerPreview) { $argsList += "--bollinger-preview" }

$output = & $Python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5c_review_gallery failed with exit code $LASTEXITCODE"
}

$result = ($output -join "`n").Trim() | ConvertFrom-Json
Write-Host "== STAS5 V5C Review Gallery =="
Write-Host "Status:  $($result.status)"
Write-Host "Round:   $($result.round_id)"
Write-Host "Forward: $($result.forward_run_id)"
Write-Host "Days:    $($result.days)"
Write-Host "Folder:  $($result.gallery_dir)"

if ($OpenFolder) {
    $dir = Join-Path $RepoRoot $result.gallery_dir
    if (Test-Path -LiteralPath $dir) {
        Invoke-Item -LiteralPath $dir
    }
}
