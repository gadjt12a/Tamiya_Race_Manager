TAMIYA RACE MANAGER - MAC (OSX)
===============================

*** PLEASE NOTE: the Mac version was first run successfully on a Mac
*** on 2026-08-08 - a full race, exports, printing, data storage and
*** shutdown all behaved correctly. It has been tested on ONE Mac
*** (macOS 10.13 High Sierra, Intel), by the developer, and never yet
*** at a real race night. Newer macOS versions and Apple Silicon Macs
*** are untested.
***
*** Please report anything broken.

THERE ARE TWO MAC DOWNLOADS - MOST PEOPLE WANT THE APP
------------------------------------------------------
  TamiyaRaceManager.app        <- the normal download. A real Mac
                                  app: no Python to install, runs in
                                  its own window like the Windows
                                  version, and the audience display
                                  is a second app window.

  This launcher package        <- the fallback. Use it only if the
  (what you are reading)          .app will not run on your Mac. It
                                  needs Python 3, opens in your web
                                  BROWSER with a Terminal window
                                  behind it, and the audience display
                                  is a browser pop-up you must allow.

Both are built from the same application code and use the same data
file, so you can switch between them freely.

FIRST LAUNCH WARNING (applies to the .app)
------------------------------------------
The app is signed by us but not registered with Apple (notarizing
costs a yearly fee we don't pay for a free club app), so macOS will
refuse the first plain double-click. Depending on your macOS version
it says the developer "cannot be verified", or - alarmingly and
WRONGLY - that the app "is damaged and can't be opened". The app is
not damaged.

  Right-click TamiyaRaceManager.app -> Open -> Open.

Do that once per Mac and it opens normally forever after. If the
option is missing, go to System Settings (or System Preferences) ->
Privacy & Security and click "Open Anyway".

WHAT'S IN THIS PACKAGE (the launcher fallback)
----------------------------------------------
  Start Race Manager.command   <- double-click this to run
  app/                         <- the application files
  README.txt                   <- this file

REQUIREMENTS
------------
Python 3 (modern Macs from ~2019 usually have it). If not:
install from https://www.python.org/downloads/ and run again.
The .app needs nothing installed.

FIRST RUN
---------
1. Right-click "Start Race Manager.command" -> Open -> Open
   (one-off macOS security approval; after that just double-click).
2. If macOS says the file cannot be executed, open Terminal and run:
      chmod +x "Start Race Manager.command"
3. The app opens in your web browser. Closing the browser tab
   shuts everything down automatically.

WHERE IS MY DATA?
-----------------
~/Library/Application Support/TamiyaRaceManager/
(racedata.json + backups/ - automatic daily backups, 14 days)

Data lives outside the app, so replacing the app with a newer
version never touches it. Still: click "Export Data" to a USB
stick after every race night.
