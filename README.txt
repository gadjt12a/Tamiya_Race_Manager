Tamiya Race Manager v9.14
=========================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WINDOWS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Double-click "START RACE MANAGER.bat"

That's it. No installation needed. Works offline.
Python is bundled in the python-bundle folder.

The app opens in your browser automatically.
Closes automatically when you close the browser tab.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 MAC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

First time only:
  Right-click "Start Race Manager.command" → Open → Open
  (macOS security check, only needed once)

Every time after:
  Double-click "Start Race Manager.command"

If it says Python is not installed:
  Connect to internet, go to python.org/downloads,
  install Python 3, then launch again.
  Modern Macs (2019+) usually have Python 3 already.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 MOVING TO ANOTHER MACHINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copy the entire race-manager folder.
The python-bundle folder moves with it — no setup needed.
Data is in data/racedata.json — moves with the folder.
Use Export/Import on home screen to backup to USB.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FOLDER CONTENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  START RACE MANAGER.bat          Windows launcher
  Start Race Manager.command      Mac launcher
  race-manager.html               The app
  server.py                       Local server
  README.txt                      This file
  data/
    racedata.json                 All race data
  python-bundle/                  Windows Python (no install needed)
    python.exe

  BUILD PYTHON BUNDLE.bat         Admin only — rebuilds python-bundle
                                  if needed (requires internet)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 RACE LOGIC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Main:       Winner stays. Losers drop to 2nd Chance.
  2nd Chance: Winner stays. Loser eliminated.
  Final:      1 from Main + 2 from 2nd Chance = 3 racers.
  2 losses = eliminated. Everyone races at least twice.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 POINTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Standard:      10, 9, 8, 7, 6, 5, 4, 3, 2, 1
  Double Points: 20, 18, 16, 14, 12, 10, 8, 6, 4, 2
  Toggle x2 PTS on setup screen before starting.
  EVO Junior points tracked separately.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VERSION: v9.14
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
