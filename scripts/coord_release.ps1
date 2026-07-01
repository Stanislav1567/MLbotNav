param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId,
    [Parameter(Mandatory = $true)]
    [string]$OwnerChat,
    [ValidateSet("runtime", "governance")]
    [string]$Kind = "runtime",
    [string]$Note = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$MetaDir = Join-Path $ProjectRoot "data\meta"
$StatePath = Join-Path $MetaDir "live_coord_state.json"
$EventsPath = Join-Path $MetaDir "live_coord_events.jsonl"
$StageStatePath = Join-Path $MetaDir "stage_runtime_state.json"

function Get-UtcNowIso {
    return (Get-Date).ToUniversalTime().ToString("o")
}

function Read-JsonFile([string]$path) {
    if (-not (Test-Path $path)) { return $null }
    $raw = Get-Content -Path $path -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
    return ($raw | ConvertFrom-Json)
}

function Write-JsonFile([string]$path, $obj) {
    $obj | ConvertTo-Json -Depth 20 | Set-Content -Path $path -Encoding UTF8
}

$lockName = "Global\MLbotNav_live_coord_lock"
$mutex = New-Object System.Threading.Mutex($false, $lockName)
$lockAcquired = $false
$eventJson = $null

try {
    $lockAcquired = $mutex.WaitOne(15000)
    if (-not $lockAcquired) {
        throw "Coord lock timeout: unable to acquire state lock in 15s."
    }

    $state = Read-JsonFile $StatePath
    if (-not $state) {
        throw "State file not found: $StatePath"
    }

    $ownerProp = if ($Kind -eq "runtime") { "runtime_owner" } else { "governance_owner" }
    $currentOwner = $state.$ownerProp
    if (-not $currentOwner) {
        throw "No active owner for kind '$Kind'."
    }

    $sameTask = [string]$currentOwner.task_id -eq $TaskId
    $sameOwner = [string]$currentOwner.owner_chat -eq $OwnerChat
    if (-not $Force -and (-not $sameTask -or -not $sameOwner)) {
        throw "Release denied: active owner is task_id='$($currentOwner.task_id)' owner_chat='$($currentOwner.owner_chat)'."
    }

    $now = Get-UtcNowIso
    $nextEventId = [int]$state.last_event_id + 1

    $event = [ordered]@{
        event_id = $nextEventId
        ts_utc = $now
        event = "release"
        kind = $Kind
        task_id = $TaskId
        owner_chat = $OwnerChat
        note = $Note
    }

    $state.$ownerProp = $null
    $state.last_event_id = $nextEventId
    $state.updated_at_utc = $now
    Write-JsonFile -path $StatePath -obj $state
    ($event | ConvertTo-Json -Compress) | Add-Content -Path $EventsPath -Encoding UTF8

    # Mirror to stage_runtime_state.
    $stageState = Read-JsonFile $StageStatePath
    if (-not $stageState) {
        $stageState = [ordered]@{
            status = "init"
            updated_at_utc = $null
            note = "autocreated for runtime path consistency"
        }
    }
    $stageState.status = "released"
    $stageState.updated_at_utc = $now
    $stageState.note = "task_id=$TaskId;owner_chat=$OwnerChat;kind=$Kind"
    Write-JsonFile -path $StageStatePath -obj $stageState

    $eventJson = ($event | ConvertTo-Json -Compress)
}
finally {
    if ($lockAcquired) {
        [void]$mutex.ReleaseMutex()
    }
    $mutex.Dispose()
}

try {
    [console]::Beep(800, 160)
} catch {}

if ($eventJson) {
    Write-Output $eventJson
}
