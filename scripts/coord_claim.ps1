param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId,
    [Parameter(Mandatory = $true)]
    [string]$OwnerChat,
    [string]$Scope = "",
    [string]$Note = "",
    [ValidateSet("runtime", "governance")]
    [string]$Kind = "runtime",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$MetaDir = Join-Path $ProjectRoot "data\meta"
$StatePath = Join-Path $MetaDir "live_coord_state.json"
$EventsPath = Join-Path $MetaDir "live_coord_events.jsonl"
$StageStatePath = Join-Path $MetaDir "stage_runtime_state.json"

if (-not (Test-Path $MetaDir)) {
    New-Item -ItemType Directory -Path $MetaDir -Force | Out-Null
}

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
        $state = [ordered]@{
            version = 1
            updated_at_utc = $null
            last_event_id = 0
            runtime_owner = $null
            governance_owner = $null
        }
    }

    $ownerProp = if ($Kind -eq "runtime") { "runtime_owner" } else { "governance_owner" }
    $currentOwner = $state.$ownerProp

    if ($Kind -eq "runtime" -and $currentOwner -and -not $Force) {
        $active = [string]$currentOwner.status -eq "active"
        $sameOwner = [string]$currentOwner.owner_chat -eq $OwnerChat
        if ($active -and -not $sameOwner) {
            throw "Runtime owner lock: task already claimed by '$($currentOwner.owner_chat)' (task_id=$($currentOwner.task_id)). Use -Force only for emergency handoff."
        }
    }

    $now = Get-UtcNowIso
    $nextEventId = [int]$state.last_event_id + 1

    $claim = [ordered]@{
        task_id = $TaskId
        owner_chat = $OwnerChat
        scope = $Scope
        note = $Note
        kind = $Kind
        status = "active"
        claimed_at_utc = $now
    }

    $event = [ordered]@{
        event_id = $nextEventId
        ts_utc = $now
        event = "claim"
        kind = $Kind
        task_id = $TaskId
        owner_chat = $OwnerChat
        scope = $Scope
        note = $Note
    }

    $state.$ownerProp = $claim
    $state.last_event_id = $nextEventId
    $state.updated_at_utc = $now

    Write-JsonFile -path $StatePath -obj $state
    ($event | ConvertTo-Json -Compress) | Add-Content -Path $EventsPath -Encoding UTF8

    # Mirror to stage_runtime_state for existing consumers.
    $stageState = Read-JsonFile $StageStatePath
    if (-not $stageState) {
        $stageState = [ordered]@{
            status = "init"
            updated_at_utc = $null
            note = "autocreated for runtime path consistency"
        }
    }
    $stageState.status = "claimed"
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
    [console]::Beep(1200, 180)
} catch {}

if ($eventJson) {
    Write-Output $eventJson
}
