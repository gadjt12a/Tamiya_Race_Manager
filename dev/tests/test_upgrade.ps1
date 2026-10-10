<#
    Tamiya Race Manager - upgrade test.

    Installs an OLD build, loads a REAL database into it, installs the NEW
    build over the top, and proves the data came through untouched. This is
    the exact sequence a club performs, and it is the one that must never go
    wrong: the database is the only copy of their season.

    Nothing here touches a real install. It installs to a scratch directory
    with /DIR and points the app at a scratch data folder with
    TAMIYA_DATA_DIR, then uninstalls.

    Usage:
      .\dev\tests\test_upgrade.ps1 -OldInstaller dist\installer\...-10.4.68.exe `
                                   -NewInstaller dist\installer\...-10.6.70.exe `
                                   -DataFile <a real racedata.json>

    IMPORTANT: close every browser tab and app window pointing at port 8765
    first. A live tab writes its in-memory data over the data file as soon as
    a server appears, which silently invalidates this test (and has clobbered
    a database for real).
#>
param(
    [Parameter(Mandatory = $true)][string]$OldInstaller,
    [Parameter(Mandatory = $true)][string]$NewInstaller,
    [Parameter(Mandatory = $true)][string]$DataFile
)

$ErrorActionPreference = "Stop"
$fails = @()
function Check($name, $ok, $detail) {
    if ($ok) { Write-Host "  PASS  $name$(if($detail){"  -> $detail"})" }
    else { Write-Host "  FAIL  $name$(if($detail){"  -> $detail"})"; $script:fails += $name }
}

# Refuse to run with anything already on the port - a stale instance makes
# every reading below meaningless.
try {
    Invoke-WebRequest "http://127.0.0.1:8765/info" -TimeoutSec 2 -UseBasicParsing | Out-Null
    Write-Host "ABORT: something is already serving port 8765."
    Write-Host "Close every Race Manager window and browser tab, then re-run."
    exit 2
} catch { }

$base = Join-Path $env:TEMP ("trm-upgrade-" + (Get-Random))
New-Item -ItemType Directory -Force "$base\data" | Out-Null
Copy-Item $DataFile "$base\data\racedata.json" -Force
$md5Before = (Get-FileHash "$base\data\racedata.json" -Algorithm MD5).Hash
Write-Host "`nscratch: $base"
Write-Host "data   : $md5Before`n"

$env:TAMIYA_DATA_DIR = "$base\data"
$env:TAMIYA_ARCHIVE_DIR = "$base\arch"

function Start-App {
    Start-Process "$base\app\TamiyaRaceManager.exe" | Out-Null
    Start-Sleep -Seconds 10
    $info = (Invoke-WebRequest "http://127.0.0.1:8765/info" -TimeoutSec 6 -UseBasicParsing).Content | ConvertFrom-Json
    $data = (Invoke-WebRequest "http://127.0.0.1:8765/data/racedata.json" -TimeoutSec 15 -UseBasicParsing).Content | ConvertFrom-Json
    $events = ($data.seasons | ForEach-Object { $_.events.Count } | Measure-Object -Sum).Sum
    return @{ ver = $info.fullVersion; racers = $data.racers.Count; events = $events }
}
function Stop-App {
    Get-Process TamiyaRaceManager -ErrorAction SilentlyContinue | ForEach-Object { $null = $_.CloseMainWindow() }
    Start-Sleep -Seconds 7
    Get-Process TamiyaRaceManager -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.Id -Force }
}

Write-Host "OLD BUILD"
Start-Process $OldInstaller -ArgumentList "/VERYSILENT","/SUPPRESSMSGBOXES","/NORESTART","/NOICONS","/DIR=$base\app" -Wait
Start-Sleep -Seconds 2
Check "old build installs" (Test-Path "$base\app\TamiyaRaceManager.exe")
$old = Start-App
Check "old build loads the database" ($old.racers -gt 0) "$($old.ver): $($old.racers) racers, $($old.events) events"
Stop-App
Check "old build leaves the file byte-identical" `
      ((Get-FileHash "$base\data\racedata.json" -Algorithm MD5).Hash -eq $md5Before)
$filesBefore = (Get-ChildItem "$base\app" -Recurse -File | Measure-Object).Count

Write-Host "`nUPGRADE"
Start-Process $NewInstaller -ArgumentList "/VERYSILENT","/SUPPRESSMSGBOXES","/NORESTART","/NOICONS","/DIR=$base\app" -Wait
Start-Sleep -Seconds 3
Check "installer does not touch the data file" `
      ((Get-FileHash "$base\data\racedata.json" -Algorithm MD5).Hash -eq $md5Before) `
      "an installer must never be able to alter race data"
$new = Start-App
Check "new build loads the SAME database" `
      ($new.racers -eq $old.racers -and $new.events -eq $old.events) `
      "$($new.ver): $($new.racers) racers, $($new.events) events"
$disp = (Invoke-WebRequest "http://127.0.0.1:8765/display" -TimeoutSec 6 -UseBasicParsing).Content
Check "display page is served" ($disp -match 'id=.stage.')
Stop-App
Check "data survives the whole cycle" `
      ((Get-FileHash "$base\data\racedata.json" -Algorithm MD5).Hash -eq $md5Before)
Check "an archive snapshot was written on close" `
      (@(Get-ChildItem "$base\arch" -Filter '*.json' -ErrorAction SilentlyContinue).Count -ge 1)

$log = Get-Content "$base\data\app.log" -ErrorAction SilentlyContinue
Check "no errors in app.log" (@($log | Where-Object { $_ -match 'Traceback|Error' }).Count -eq 0)
$filesAfter = (Get-ChildItem "$base\app" -Recurse -File | Measure-Object).Count
Write-Host "  note  install dir: $filesBefore -> $filesAfter files"

if (Test-Path "$base\app\unins000.exe") {
    Start-Process "$base\app\unins000.exe" -ArgumentList "/VERYSILENT","/SUPPRESSMSGBOXES" -Wait
    Start-Sleep -Seconds 4
}
Remove-Item -Recurse -Force $base -ErrorAction SilentlyContinue

Write-Host "`n============================================================"
if ($fails.Count -eq 0) { Write-Host "  UPGRADE TEST PASSED"; exit 0 }
else { Write-Host "  FAILED: $($fails -join ', ')"; exit 1 }
