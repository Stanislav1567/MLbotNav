param(
    [string]$StartDay = "2026-01-27",

    [string]$EndDay = "2026-02-27",

    [string]$GalleryRoot = "",

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
    "-m", "mlbotnav.stas5_v5_base_review_gallery",
    "--start-day", $StartDay,
    "--end-day", $EndDay
)
if ($GalleryRoot) { $argsList += @("--gallery-root", $GalleryRoot) }

$output = & $Python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5_base_review_gallery failed with exit code $LASTEXITCODE"
}

$result = ($output -join "`n").Trim() | ConvertFrom-Json
Write-Host "== STAS5 V5 Base R2-style Review Gallery =="
Write-Host "Status: $($result.status)"
Write-Host "Range:  $($result.start_day)..$($result.end_day)"
Write-Host "Days:   $($result.days)"
Write-Host "Rows:   $($result.rows_total)"
Write-Host "GOOD:   $($result.entry_good_total)"
Write-Host "BAD:    $($result.entry_bad_total)"
Write-Host "Folder: $($result.gallery_dir)"

if ($OpenFolder) {
    $dir = Join-Path $RepoRoot $result.gallery_dir
    if (Test-Path -LiteralPath $dir) {
        Invoke-Item -LiteralPath $dir
    }
}
