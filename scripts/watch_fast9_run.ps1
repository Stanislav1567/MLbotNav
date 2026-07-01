param(
    [int]$DurationSec = 120,
    [int]$PollSec = 10
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if ($PollSec -lt 2) { $PollSec = 2 }
if ($DurationSec -lt $PollSec) { $DurationSec = $PollSec }

$statePath = Join-Path $ProjectRoot "data\meta\live_coord_state.json"
$pipelineDir = Join-Path $ProjectRoot "reports\pipeline"

function Get-LatestPipeline() {
    if (-not (Test-Path $pipelineDir)) { return $null }
    return Get-ChildItem $pipelineDir -Filter "optuna_search_candidate_*.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
}

$deadline = (Get-Date).AddSeconds($DurationSec)
Write-Host "FAST9 monitor started: duration=${DurationSec}s poll=${PollSec}s" -ForegroundColor Cyan

while ((Get-Date) -lt $deadline) {
    $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $owner = "none"
    $task = ""
    if (Test-Path $statePath) {
        try {
            $state = Get-Content $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($null -ne $state.runtime_owner) {
                $owner = [string]$state.runtime_owner.owner_chat
                $task = [string]$state.runtime_owner.task_id
            }
        } catch {}
    }

    $pipe = Get-LatestPipeline
    $storage = "n/a"
    $workersReq = "n/a"
    $workersUsed = "n/a"
    $forced = "n/a"
    $pipeTs = "n/a"

    if ($null -ne $pipe) {
        $pipeTs = $pipe.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
        try {
            $j = Get-Content $pipe.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
            $storage = [string]$j.storage_parallel_guard.storage_scheme
            $workersReq = [string]$j.workers_requested
            $workersUsed = [string]$j.workers_used
            $forced = [string]$j.storage_parallel_guard.forced_single_worker
        } catch {}
    }

    Write-Host ("[{0}] owner={1} task={2} | pipeline_ts={3} storage={4} workers={5}/{6} forced_single={7}" -f $ts,$owner,$task,$pipeTs,$storage,$workersUsed,$workersReq,$forced)
    Start-Sleep -Seconds $PollSec
}

Write-Host "FAST9 monitor done." -ForegroundColor Green
