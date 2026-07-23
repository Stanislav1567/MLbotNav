param(
    [string]$PackId = "",

    [switch]$Force,
    [switch]$NoStrict,
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
    "-m", "mlbotnav.stas5_v5c_review_pack"
)
if ($PackId) { $argsList += @("--pack-id", $PackId) }
if ($Force) { $argsList += "--force" }
if ($NoStrict) { $argsList += "--no-strict" }

$output = & $Python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "stas5_v5c_review_pack failed with exit code $LASTEXITCODE"
}

$result = ($output -join "`n").Trim() | ConvertFrom-Json
Write-Host "== STAS5 V5C Review Pack R2/R3/R4 =="
Write-Host "Status:     $($result.status)"
Write-Host "Pack:       $($result.pack_id)"
Write-Host "Folder:     $($result.pack_dir)"
Write-Host "Days:       $($result.days)"
Write-Host "ENTRY rows: $($result.entry_rows)"
Write-Host "GOOD/BAD:   $($result.entry_good) / $($result.entry_bad)"
Write-Host "RISK BAD:   $($result.risk_bad)"
Write-Host "Entry CSV:  $($result.outputs.entry_csv)"
Write-Host "Risk CSV:   $($result.outputs.riskgate_csv)"
Write-Host "Guard:      $($result.outputs.guard_json)"

if ($OpenFolder) {
    $dir = Join-Path $RepoRoot $result.pack_dir
    if (Test-Path -LiteralPath $dir) {
        Invoke-Item -LiteralPath $dir
    }
}
