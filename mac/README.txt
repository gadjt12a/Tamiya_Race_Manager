TAMIYA RACE MANAGER - MAC (OSX)
===============================

*** PLEASE NOTE: the Mac version was first run successfully on a Mac
*** on 2026-08-08 - a full race, exports, printing, data storage and
*** shutdown all behaved correctly. It has been tested on ONE Mac, by
*** the developer, and never yet at a real race night.
***
*** It also runs differently from Windows: the app opens in your web
*** BROWSER with a Terminal window behind it, and the audience display
*** is a browser pop-up rather than a second app window. You need
*** Python 3 installed (see REQUIREMENTS below); the Windows version
*** bundles everything and needs nothing.
***
*** Please report anything broken.

WHAT'S IN THIS PACKAGE
----------------------
  Start Race Manager.command   <- double-click this to run
  app/                         <- the application files
  README.txt                   <- this file

REQUIREMENTS
------------
Python 3 (modern Macs from ~2019 usually have it). If not:
install from https://www.python.org/downloads/ and run again.

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

Data lives outside this folder, so replacing the app with a newer
package never touches it. Still: click "Export Data" to a USB
stick after every race night.
