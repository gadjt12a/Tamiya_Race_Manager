TAMIYA RACE MANAGER - MAC (OSX)
===============================

*** PLEASE NOTE: the Mac version has NEVER been run on a Mac. It is
*** built and packaged on Windows, and no one has yet launched it on
*** macOS even once. It uses the same core app, but treat it as
*** experimental and please report anything broken. The Windows
*** version is the tested one - use that if you have the choice.

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
