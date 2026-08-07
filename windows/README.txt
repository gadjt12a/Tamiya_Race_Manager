TAMIYA RACE MANAGER - WINDOWS
=============================

WHICH DOWNLOAD DO I WANT?
-------------------------
  TamiyaRaceManager-Setup-<version>.exe   <- RECOMMENDED
      Normal Windows installer. Desktop icon, Start Menu entry,
      no admin rights needed. Updating = run the newer installer.

  TamiyaRaceManager-WindowsPortable-<version>.zip
      Just the app in a zip - nothing is installed. Unzip the WHOLE
      thing anywhere (USB stick is fine), open the TamiyaRaceManager
      folder and double-click TamiyaRaceManager.exe.

      IMPORTANT: extract the zip first - don't run the app from
      inside Windows' zip preview. And keep TamiyaRaceManager.exe
      together with the _internal folder next to it; the app will
      not start if the exe is moved out on its own. To put a
      shortcut on the desktop, right-click the exe > Show more
      options > Send to > Desktop (create shortcut).

FIRST RUN
---------
Windows SmartScreen may show "Windows protected your PC" because
the app is not code-signed. Click "More info" then "Run anyway".
This only happens the first time.

The app opens in its own window. No internet needed, ever.

WHERE IS MY DATA?
-----------------
%LOCALAPPDATA%\TamiyaRaceManager\   (racedata.json + backups\)

Outside the app folder, so installing, updating or uninstalling
the app can NEVER touch your race data. Automatic daily backups
are kept for 14 days. Still: click "Export Data" to a USB stick
after every race night.

UPGRADING FROM THE OLD ZIP VERSION (v9.x with .bat files)?
----------------------------------------------------------
Your old data is safe in the old folder. One-time step:
  1. Launch the new app.
  2. Click "Import Data" (top right).
  3. Pick  data\racedata.json  from your OLD race-manager folder.
If the old version ran in "browser storage mode" (no Python),
open the old version first and click "Export Data", then import
that file instead.
