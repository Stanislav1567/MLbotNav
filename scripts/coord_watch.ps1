param(
    [int]$PollSeconds = 2,
    [switch]$NoBeep,
    [switch]$Once
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$EventsPath = Join-Path $ProjectRoot "data\meta\live_coord_events.jsonl"
$StatePath = Join-Path $ProjectRoot "data\meta\live_coord_state.json"

function Read-Lines([string]$path) {
    if (-not (Test-Path $path)) { return @() }
    return @(Get-Content -Path $path -Encoding UTF8)
}

function Print-Event([string]$line, [bool]$beepEnabled) {
    if ([string]::IsNullOrWhiteSpace($line)) { return }
    try {
        $ev = $line | ConvertFrom-Json
        $kind = [string]$ev.kind
        $name = [string]$ev.event
        $task = [string]$ev.task_id
        $owner = [string]$ev.owner_chat
        $ts = [string]$ev.ts_utc
        Write-Host ("[{0}] {1} {2} task={3} owner={4}" -f $ts, $kind, $name, $task, $owner)
        if ($beepEnabled) {
            if ($name -eq "claim") { [console]::Beep(1200, 120) }
            elseif ($name -eq "release") { [console]::Beep(800, 120) }
            else { [console]::Beep(1000, 100) }
        }
    } catch {
        Write-Host ("[RAW] {0}" -f $line)
    }
}

$beepEnabled = -not $NoBeep

if (-not (Test-Path $EventsPath)) {
    New-Item -ItemType File -Path $EventsPath -Force | Out-Null
}
if (-not (Test-Path $StatePath)) {
    "{}" | Set-Content -Path $StatePath -Encoding UTF8
}

$initial = Read-Lines $EventsPath
$seen = $initial.Count
Write-Host ("coord_watch started | events={0} | poll={1}s" -f $seen, $PollSeconds)
Write-Host ("watching: {0}" -f $EventsPath)

if ($Once) {
    foreach ($line in $initial) {
        Print-Event -line $line -beepEnabled $false
    }
    exit 0
}

while ($true) {
    Start-Sleep -Seconds $PollSeconds
    $lines = Read-Lines $EventsPath
    $count = $lines.Count
    if ($count -gt $seen) {
        for ($i = $seen; $i -lt $count; $i++) {
            Print-Event -line $lines[$i] -beepEnabled $beepEnabled
        }
        $seen = $count
    }
}
