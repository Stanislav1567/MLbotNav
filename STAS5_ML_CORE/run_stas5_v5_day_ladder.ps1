param(
    [Parameter(Mandatory = $true)]
    [string]$Day,

    [ValidateSet("All", "Collect", "BuildApproved", "Audit", "Open")]
    [string]$Stage = "All",

    [string]$Symbol = "SOLUSDT",
    [string]$Timeframe = "1m",
    [string[]]$GoodIds = @(),
    [switch]$ForceCollect,
    [switch]$OpenFolder,
    [switch]$NoStrict,
    [switch]$NoPlot
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$parsedDay = [datetime]::ParseExact($Day, "yyyy-MM-dd", $null)
$compactDay = $parsedDay.ToString("yyyyMMdd")
$dayDir = Join-Path $repoRoot "STAS5_ML_CORE\artifacts\v5\market_passports\$compactDay"
$runsDir = Join-Path $repoRoot "STAS5_ML_CORE\runs"
$prefix = "STAS5_V5_MARKET_PASSPORT_$compactDay"

function Get-LatestFull274Run {
    $item = Get-ChildItem -Path $runsDir -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "full274_feature_collect_$compactDay*" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    return $item
}

function Assert-ApprovedPassportReady {
    $required = @(
        "$prefix`_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv",
        "$prefix`_FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json",
        "$prefix`_PHASE_STATE_REASON_GUARD_V2.json",
        "$prefix`_ENTRY_PHASE_STATE_REASON_LEDGER_USER_APPROVED_V2.csv",
        "$prefix`_PHASE_SEGMENTS_USER_APPROVED_V1.csv",
        "$prefix`_MARKET_STRUCTURE_NUMERIC_V1.csv"
    )

    $missing = @()
    foreach ($name in $required) {
        $path = Join-Path $dayDir $name
        if (-not (Test-Path -LiteralPath $path)) {
            $missing += $name
        }
    }

    if ($missing.Count -gt 0) {
        Write-Host ""
        Write-Host "STOP: approved V5 passport for $Day is not ready yet." -ForegroundColor Yellow
        Write-Host "Need manual/user-approved stage before cs_* and fcs_* builders." -ForegroundColor Yellow
        Write-Host "Missing files:" -ForegroundColor Yellow
        foreach ($name in $missing) {
            Write-Host "  - $name" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "Next manual step: create/approve market passport for this day in:" -ForegroundColor Cyan
        Write-Host "  $dayDir" -ForegroundColor Cyan
        return $false
    }

    return $true
}

function Invoke-Full274Collect {
    $latest = Get-LatestFull274Run
    if ($latest -and -not $ForceCollect) {
        Write-Host "FULL274 run already exists: $($latest.FullName)"
        return
    }

    Write-Host "== Collect FULL274 for $Day =="
    & (Join-Path $repoRoot "STAS5_ML_CORE\run_stas5_full274_feature_collect.ps1") `
        -Day $Day `
        -Symbol $Symbol `
        -Timeframe $Timeframe
}

function Invoke-BuildApproved {
    if ($GoodIds.Count -gt 0) {
        Write-Host "== Create approved passport from user GOOD ids for $Day =="
        & (Join-Path $repoRoot "STAS5_ML_CORE\run_stas5_v5_approved_passport_builder.ps1") `
            -Day $Day `
            -GoodIds $GoodIds
        Write-Host ""
    }

    if (-not (Assert-ApprovedPassportReady)) {
        if ($Stage -eq "BuildApproved") {
            throw "Approved passport is missing for $Day."
        }
        return
    }

    Write-Host "== Build cs_* causal structure for $Day =="
    if ($NoStrict) {
        & (Join-Path $repoRoot "STAS5_ML_CORE\run_stas5_v5_causal_structure_builder.ps1") -Day $Day -NoStrict
    } else {
        & (Join-Path $repoRoot "STAS5_ML_CORE\run_stas5_v5_causal_structure_builder.ps1") -Day $Day
    }

    Write-Host ""
    Write-Host "== Build full fcs_* causal structure for $Day =="
    if ($NoStrict -and $NoPlot) {
        & (Join-Path $repoRoot "STAS5_ML_CORE\run_stas5_v5_full_causal_structure_builder.ps1") -Day $Day -NoStrict -NoPlot
    } elseif ($NoStrict) {
        & (Join-Path $repoRoot "STAS5_ML_CORE\run_stas5_v5_full_causal_structure_builder.ps1") -Day $Day -NoStrict
    } elseif ($NoPlot) {
        & (Join-Path $repoRoot "STAS5_ML_CORE\run_stas5_v5_full_causal_structure_builder.ps1") -Day $Day -NoPlot
    } else {
        & (Join-Path $repoRoot "STAS5_ML_CORE\run_stas5_v5_full_causal_structure_builder.ps1") -Day $Day
    }
}

function Invoke-V5Audit {
    Write-Host "== V5 folder audit =="
    & (Join-Path $repoRoot "STAS5_ML_CORE\run_stas5_v5_folder_audit.ps1")

    $guardPath = Join-Path $dayDir "$prefix`_FULL_CAUSAL_STRUCTURE_GUARD_V1.json"
    if (Test-Path -LiteralPath $guardPath) {
        $guard = Get-Content -LiteralPath $guardPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host ""
        Write-Host "Full guard for ${Day}: $($guard.status)"
        Write-Host "Rows: $($guard.rows); features: $($guard.feature_count); fcs: $($guard.full_causal_feature_count)"
        if ($guard.artifact_counts) {
            Write-Host "Artifacts: levels=$($guard.artifact_counts.levels), channels=$($guard.artifact_counts.channels), regimes=$($guard.artifact_counts.regimes), events=$($guard.artifact_counts.events)"
        }
    }
}

Write-Host "== STAS5 V5 Day Ladder =="
Write-Host "Day:       $Day"
Write-Host "Stage:     $Stage"
Write-Host "DayDir:    $dayDir"
if ($GoodIds.Count -gt 0) {
    Write-Host "GoodIds:   $($GoodIds -join ',')"
} else {
    Write-Host "GoodIds:   not provided"
}
Write-Host "Training:  NOT STARTED"
Write-Host "Forward:   NOT STARTED"
Write-Host ""

switch ($Stage) {
    "Collect" {
        Invoke-Full274Collect
    }
    "BuildApproved" {
        Invoke-BuildApproved
    }
    "Audit" {
        Invoke-V5Audit
    }
    "Open" {
        if (Test-Path -LiteralPath $dayDir) {
            Invoke-Item -LiteralPath $dayDir
        } else {
            $latest = Get-LatestFull274Run
            if ($latest) {
                Invoke-Item -LiteralPath $latest.FullName
            } else {
                throw "No V5 day folder and no FULL274 run found for $Day."
            }
        }
    }
    "All" {
        Invoke-Full274Collect
        Invoke-BuildApproved
        Invoke-V5Audit
    }
}

if ($OpenFolder) {
    if (Test-Path -LiteralPath $dayDir) {
        Invoke-Item -LiteralPath $dayDir
    } else {
        $latest = Get-LatestFull274Run
        if ($latest) {
            Invoke-Item -LiteralPath $latest.FullName
        }
    }
}
