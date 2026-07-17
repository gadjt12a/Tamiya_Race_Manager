# v10 Testing Manual

Hands-on tests that must pass before `v10-packaging` merges to `main`.
These are the test-matrix items a script can't do — they need a human, real
hardware, and eyes on screen. Run them against the **installed desktop app**
(v9.37 or later — check the version in the app's top-left header).

**Before you start:** click **⬆ Export Data** and put the file somewhere safe.
Some tests use your test data; you may want to Import it back afterwards.

Record results in the table at the bottom. For any FAIL: note what you did,
what you expected, what happened, and grab a screenshot if visual.

---

## T1 — Full race night simulation *(matrix #12)*

**Purpose:** the packaged desktop app runs a complete, realistic race night
identically to the proven v9.x behaviour.

1. Launch from the desktop icon. Confirm: opens in its own window, no console
   window, no browser tab, version shows in the header.
2. Start (or continue) a season. Open **👥 Season Racers** — confirm the
   JNR/ADL switches work and save.
3. **Box class:** ~7 racers from the roster panel (confirm the list is
   alphabetical). Race it through to the podium. Watch for: groups of 3
   (2 where needed, never 1), losers dropping to 2nd Chance, strict
   Main→2nd Chance alternation, a 3-racer final.
4. **EVO class:** include at least 2 juniors. Mid-class, deliberately enter a
   wrong result, confirm it, then use **Edit Last Result** to correct it —
   standings must update correctly. Finish the class: podium shows, and the
   **Junior podium** shows alongside.
5. **Pro class:** ~5 racers. Mid-class, use the **delayed race swap** (swap to
   a different queued race), then complete normally.
6. After each class: podium modal auto-saves ("✓ Saved — Return Home").
7. Home screen → **📊 Season Standings**: all three classes' points are there,
   junior table correct, nobody's points split across two rows.
8. Close the app window. Check Task Manager: no `TamiyaRaceManager.exe`
   left running.

**PASS when:** every step behaves, and nothing feels different from the v9.x
you've run in the field (other than the new window).

## T2 — Display window / second screen *(matrix #13a)*

**Purpose:** the native display window works for a real race night +
prize-giving.

*With ONE screen:*
1. During a race, click the Display button — a separate "Race Display" window
   opens (windowed, not fullscreen).
2. Confirm result → display updates to the next race within ~1 second.

*With a SECOND screen/projector connected:*
3. Click Display again — the display should open **full-screen on the second
   screen automatically**.
4. Run a class to completion: winners stay on the display (titled with the
   class) through Return Home, and only change when the next race starts.
5. For EVO: class winners LEFT, Junior winners RIGHT.
6. Close the display window manually mid-class, reopen via the button — it
   should come back with current content.
7. Leave the display up for 15+ minutes during racing — it must never go
   stale or need reopening.

## T3 — Exports, print and import inside the app window *(matrix #13b)*

**Purpose:** WebView2 (the app window's engine) handles downloads, printing
and file pickers differently from Chrome — every export path needs checking.

1. Finish a class → podium modal → **💾 Export HTML**. Where does the file
   go? Does a save dialog appear? Open the file — complete and correct?
2. **📊 Export CSV** — same checks; opens in Excel?
3. **🖨 Print / PDF** — does a print dialog appear at all? Can you save as
   PDF? *(This is the most likely thing to be broken in WebView2 — if it does
   nothing, note it; the workaround is Export HTML → print from a browser,
   and we'll fix or document it.)*
4. Home screen → **⬆ Export Data** — file saves OK?
5. **⬇ Import Data** — file picker opens? Pick your export from step 4:
   summary confirm appears ("X seasons, Y racers"), import works.
6. Repeat 1–5 quickly in **browser mode** (run `python app/server.py` from
   the repo, or the portable exe fallback) if anything failed — that tells us
   whether it's a WebView2 quirk or an app bug.

## T4 — Laptop sleep mid-event *(matrix #7)*

**Purpose:** closing the lid during a break must not kill the night. On
battery, not plugged in (most aggressive sleep).

1. Start a class, confirm 2–3 races.
2. Close the laptop lid. Wait **2+ minutes**. Open it.
3. The app window is still there, no red banner appears (give it ~15s).
4. Confirm another race result, then check the data file timestamp updated:
   `%LOCALAPPDATA%\TamiyaRaceManager\racedata.json` (modified = just now).

## T5 — Crash recovery *(matrix #9, replaces #8 for the desktop app)*

**Purpose:** a crash mid-event loses nothing.

1. Start a class, confirm 2–3 races (note the last result).
2. Kill the app the hard way: Task Manager → `TamiyaRaceManager.exe` →
   End task (both entries if two appear).
3. Relaunch from the desktop icon.
4. The **Resume** modal appears with the right class and race count. Resume —
   bracket state, standings and history are exactly where you left off,
   including any Edit-Last-Result correction.

## T6 — Garbage import *(matrix #11)*

**Purpose:** a wrong file can't destroy the database.

1. Note current data (season name, racer count).
2. **⬇ Import Data** → choose any random `.txt` renamed to `.json`, or any
   non-Race-Manager JSON file.
3. Expect: error toast, nothing changes, no confirm dialog appears.
4. Import a REAL export file → summary confirm → **Cancel**. Nothing changes.
5. Re-check: season and racers exactly as in step 1.

## T7 — Fresh-machine install + SmartScreen *(needs a PC that has never seen the app)*

**Purpose:** verify the first-run experience a club member gets, and capture
the screenshots for the release notes.

Copy `TamiyaRaceManager-Setup-9.37.exe` to a USB stick, take it to another
Windows PC (a club member's laptop is perfect):

1. Run the installer. **📸 SCREENSHOT 1:** the blue **"Windows protected your
   PC"** SmartScreen dialog, exactly as it first appears.
2. Click **More info**. **📸 SCREENSHOT 2:** the same dialog now showing the
   **"Run anyway"** button.
3. Click Run anyway. **📸 SCREENSHOT 3:** the installer's data-safety info
   page (the "YOUR RACE DATA IS SAFE" screen).
4. Finish the install, launch from the desktop icon. **📸 SCREENSHOT 4:** the
   app open on the home screen, desktop icon visible if possible.
5. Also note: did Edge/Chrome show a warning when *downloading* the exe
   (e.g. "isn't commonly downloaded")? If so, **📸 SCREENSHOT 5** of that too.
6. Confirm the fresh install starts with an empty database and the
   "Upgrading from an older version?" hint shows on the home screen.

Screenshot tips: PNG, whole dialog in frame, no personal info visible in the
background. Put them in `Working_Files/Screenshots/` and I'll wire them into
the release notes (they'll be committed to the repo at that point).

---

## Results

| Test | Result (PASS / FAIL / notes) | Date |
|---|---|---|
| T1 Full race night | | |
| T2 Display / second screen | | |
| T3 Exports & import in window | | |
| T4 Sleep mid-event | | |
| T5 Crash recovery | | |
| T6 Garbage import | | |
| T7 Fresh machine + SmartScreen | | |
