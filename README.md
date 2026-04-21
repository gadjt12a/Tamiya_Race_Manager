# Tamiya_Race_Manager
Race Manager for Tamiya Mini 4WD racers

Tamiya Race Manager v9.19
HOW TO USE
==========================================


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GETTING STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WINDOWS (first time setup — admin only):
  1. Extract the zip on an internet-connected machine
  2. Double-click "BUILD PYTHON BUNDLE (admin use only).bat"
  3. Wait for it to finish (~15MB download)
  4. Re-zip the race-manager folder — this is your distribution copy
  5. That zip now works on ANY Windows PC, no internet ever needed

WINDOWS (every event):
  Double-click "START RACE MANAGER.bat"
  The app opens in your browser automatically.
  Closes automatically when you close the browser tab.
  No installation. No internet. No admin rights needed.

MAC (first time only):
  Right-click "Start Race Manager.command" → Open → Open
  This is a one-off macOS security check.
  After that, just double-click it normally.

MAC (every event):
  Double-click "Start Race Manager.command"
  If it says Python is not installed, go to python.org/downloads,
  install Python 3, then try again. Modern Macs (2019+) usually
  have Python 3 already.

MOVING TO A DIFFERENT COMPUTER:
  Copy the entire race-manager folder to the new machine.
  On Windows, the python-bundle folder comes with it — no setup needed.
  All your race data moves with it automatically.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 BEFORE RACE NIGHT — SETTING UP A SEASON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Start the app and click "+ Start New Season"
   Enter a season name (e.g. "2026 Season") and start date.
   You only do this once at the start of the year.

2. Build your racer database
   Go to any class setup screen.
   Add each racer by name using the entry box.
   Toggle ADL/JNR for each racer (Junior status saves permanently).
   Once saved, racers appear in the Season Roster for future events.

3. Set up race nights in advance
   Decide which classes run each night (Box, EVO, Pro).
   If it is a Double Points night, note it — you will toggle it
   on the setup screen before starting that class.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 RUNNING A RACE NIGHT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1 — Select the class
  Click Box Class, EVO Class, or Pro Class from the home screen.

STEP 2 — Add racers
  Tick names from the Season Roster on the left to add them quickly.
  New racers not in the roster can be typed in the entry box.
  Toggle ADL/JNR for each racer if needed.
  Paste a list of names (one per line) to bulk add.

STEP 3 — Double Points (if applicable)
  Toggle the "×2 PTS" switch in the Tonight's Racers panel header.
  This doubles all points for this class event (20 down to 2).
  Set this BEFORE clicking Start Race.

STEP 4 — Start Race
  Click "Start Race →" once you have at least 3 racers.
  Racers are automatically randomised into the bracket.

STEP 5 — Run the races
  The coordinator screen shows the current race and upcoming queue.
  For each race, click 1st, 2nd, 3rd to assign places.
  Click "Confirm Result & Next Race" to advance.

  If you need to hold a race:
  Click "Swap Race" to run a different queued race first,
  then come back to the held race when ready.

  If you entered a result incorrectly:
  Click "Edit Last" immediately after confirming — before the
  next race is confirmed. This is the only race you can edit.

STEP 6 — The Final
  The app automatically assembles the Final when:
    - 1 undefeated racer remains from the Main bracket
    - 2 racers remain from the 2nd Chance bracket
  These 3 racers race in the Grand Final.

STEP 7 — Save results
  After the Final, the podium screen appears.
  Check the results and points are correct.
  Click "Save Results & Return Home" to save to the season.
  Or use the Export buttons to save HTML, CSV, or print a PDF.

REPEAT for each class on the night (Box → EVO → Pro).


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 EVO CLASS — JUNIOR RACERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Juniors race alongside adults in the same bracket.
At the end of EVO, two podiums are awarded:

  Overall Podium — top 3 finishers (adults and juniors together)
  Junior Podium  — best placed junior racers on the night
                   (taken from their finishing position in the bracket,
                    not a separate race)

Junior points are tracked in a separate standings table.
The Junior flag is set per racer in the database — toggle it
once and it carries through all future events automatically.

To manage junior flags in bulk:
  On the setup screen, click "✏️ Manage" on the Season Roster.
  Use "All Junior" or "All Adult" buttons with the search filter
  to update multiple racers at once.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 RACE BRACKET LOGIC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Three tables operate in each class event:

MAIN TABLE
  All racers start here.
  Winner of each race stays in Main.
  Losers drop to the 2nd Chance table.
  Races continue until 1 undefeated racer remains.

2ND CHANCE TABLE
  Racers who lost in Main race here.
  Winner stays in 2nd Chance.
  Loser is eliminated (2nd loss = out).
  Races continue until 2 racers remain.

FINAL TABLE
  1 undefeated racer from Main
  + 2 survivors from 2nd Chance
  = 3 racers in the Grand Final.
  One race decides 1st, 2nd, and 3rd.

ROUND ORDER
  Main races all run first each round,
  then 2nd Chance races, then back to Main, and so on.
  Both brackets alternate until the Final is assembled.

GUARANTEE
  Every racer gets at least 2 races before being eliminated.
  No one is knocked out after a single loss.

SPECIAL CASE — ODD NUMBER IN 2ND CHANCE
  If 3 racers remain in 2nd Chance when Main is down to 1,
  the racer with the most wins receives a bye to the Final.
  The other 2 race to determine the second finalist.
  The app handles this automatically with a notification.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 POINTS SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Top 10 finishers in each class earn points per event:

  Position:  1st  2nd  3rd  4th  5th  6th  7th  8th  9th  10th
  Standard:   10    9    8    7    6    5    4    3    2     1
  Double:     20   18   16   14   12   10    8    6    4     2

Points accumulate across the season per class.
EVO Junior points are tracked in a separate table.
Special events have their own separate points table.
Test races record nothing.

DOUBLE POINTS NIGHT
  Toggle "×2 PTS" on the setup screen before starting.
  Applies to all classes raced that night.
  Shows as "✕2 DOUBLE POINTS" on the podium screen.
  Marked with a ×2 badge on the home screen event history.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SPECIAL EVENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Special events (e.g. Club Championship) have their own
separate points table that does not affect season standings.

To run a special event:
  Click "★ Special Event" on the setup screen.
  Enter the event name and select the class.
  Choose a points scheme (Standard, Double, or Podium Only).
  Add racers and start as normal.

You can run multiple classes (Box, EVO, Pro) under the same
event name — they group together automatically in the results.

Special events can run with or without an active season.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SEASON MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

START A NEW SEASON
  Click "+ Start New Season" on the home screen.
  Enter a name and start date.
  Only one season can be active at a time.

VIEW STANDINGS
  Click "📊 Season Standings" on the home screen.
  Shows current points tables for all classes and EVO Juniors.
  Export to HTML, CSV, or Print/PDF using the buttons in the top bar.

CLOSE A SEASON
  Click "Close Season" on the home screen.
  Enter the end date.
  The season becomes read-only and moves to the archive.
  You can still view standings from archived seasons.

VIEW PREVIOUS SEASONS
  Click "📁 View All Seasons" on the home screen.
  Select a season to view its standings.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 EXPORTING RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After each class finishes, three export options appear:

  💾 Export HTML   Saves a self-contained webpage file.
                   Opens in any browser. Good for emailing.

  📊 Export CSV    Saves a spreadsheet file.
                   Opens in Excel. Good for records.

  🖨 Print / PDF   Opens a print-ready page.
                   Use "Save as PDF" in the print dialog.

Files are named automatically:
  e.g. "EVO_Class_12-04-2026.html"
  e.g. "Season_Standings_2026_Season.csv"

Season standings can also be exported from the Standings screen
using the same three buttons in the top right.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 SECOND SCREEN (AUDIENCE DISPLAY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The app supports a second monitor for audience display.

  1. Click "📺 Display" in the race coordinator top bar
  2. Allow pop-ups when your browser asks
  3. Drag the new window to your second monitor
  4. The display shows the current race and next race up
  5. Updates automatically as races are confirmed

Note: pop-ups must be allowed for the app in your browser.
In Chrome: click the pop-up blocked icon in the address bar
and select "Always allow pop-ups from this site".


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 BACKING UP YOUR DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All data is stored in:  race-manager/data/racedata.json

To back up:
  Click "⬆ Export Data" on the home screen.
  Save the file to a USB drive or another location.
  Do this after every race night.

To restore:
  Click "⬇ Import Data" on the home screen.
  Select your backup file.
  This overwrites current data — use with care.

To move to a new computer:
  Copy the entire race-manager folder.
  Or export data and import it on the new machine.

The JSON file is plain text and can be opened in any
text editor (Notepad on Windows, TextEdit on Mac) if
manual corrections are ever needed.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

App won't start (Windows):
  Make sure the python-bundle folder is inside the
  race-manager folder and contains python.exe.
  Contact your administrator if it is missing.

App won't start (Mac):
  Make sure you right-clicked and selected Open the first time.
  If Python is missing, install it from python.org/downloads.

Browser doesn't open automatically:
  Manually open your browser and go to:
  http://localhost:8765/race-manager.html

App seems slow or unresponsive:
  Try a different browser (Chrome or Edge recommended).
  Avoid using Internet Explorer.

Data appears missing after moving computers:
  Check that the data/racedata.json file came across.
  Use the Import Data button to restore from a backup.

Accidentally confirmed a wrong result:
  Click "✏️ Edit Last" in the top bar immediately.
  You can only edit the most recently confirmed race.
  Once the next race is confirmed, the edit window closes.

Race seems stuck / no next race appearing:
  Check the standings — if all racers are eliminated or
  the final has been run, the event may be complete.
  If genuinely stuck, use "✕ End Race" and restart the class.

Pop-up blocked (second screen):
  Click the pop-up blocked icon in your browser address bar.
  Select "Always allow pop-ups from this site".
  Then click the 📺 Display button again.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 QUICK REFERENCE — COORDINATOR BUTTONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✏️ Edit Last    Edit the most recently confirmed race result
  🔄 Swap Race    Delay current race, run a different queued race first
  📺 Display      Open the audience display on a second screen
  ✏️ Names        Edit racer names mid-event (doesn't affect logic)
  ✕ End Race      Abort the current class (no results saved)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VERSION HISTORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  v9.14  Double points toggle. Enriched JSON audit trail.
         Bundled Python for Windows (no install needed).
         Mac launcher. Special events improvements.

  v9.12  Full double-elimination bracket. Season management.
         EVO Junior tracking. Points accumulation.
         Export HTML/CSV/PDF. Edit last result.
         Roster management. Offline operation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
