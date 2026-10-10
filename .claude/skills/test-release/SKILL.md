---
name: test-release
description: Prove a Tamiya Race Manager build is safe to put in front of a club before it ships. Use when the user says "test the app", "/test-release", "is this safe to ship", "test before we deploy", or after any change to app/server.py, app/app.py or app/race-manager.html.
---

# Test a build before a club runs a race night on it

The club has one laptop, one database and often nobody present who can fix
anything. A bug here is not an inconvenience, it is a race night lost and
results that cannot be reconstructed. Three releases in a row shipped a defect
the developer had not noticed, which is what this exists to stop.

**The rule that catches the most: every escaped bug so far lived in the USER
FLOW, not in an endpoint.** Exports that reported success and wrote nothing.
A roster that jumped to the top on every click. A display that went black.
All three would pass any amount of unit testing. So the suite below drives the
real app through a real race night and then checks what landed on disk.

Work through the phases in order and **report honestly**, including what you
could not test. A green summary that quietly skipped the browser tests is
worse than no summary.

---

## Before you start: two things that silently invalidate everything

**1. Nothing may be listening on port 8765.** A leftover app or test server
means the thing you start next just attaches to the old one, and every reading
afterwards describes the wrong instance. Check and kill:

```powershell
Get-Process TamiyaRaceManager -ErrorAction SilentlyContinue | Stop-Process -Force
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like '*server.py*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

**2. Close every browser tab pointing at the app.** A tab left open writes its
in-memory data over the data file the moment a server appears on 8765. This
has clobbered a test database and, twice, undone a real file swap for the club.
Close tabs when a phase finishes, not "later".

**Never point any test at real race data.** Always
`TAMIYA_DATA_DIR=<scratch>` and `TAMIYA_ARCHIVE_DIR=<scratch>`. The one test
that uses a real database copies it to scratch first and only ever reads it.

---

## Phase 1 - the engine (fast, always run)

```
python dev/stress-test.py
```

30 race nights x 3 classes, every racer count from 3 to 21, junior ranking,
double and triple points. Expect **0 errors**. It re-implements the bracket
rules rather than importing them, so if a rule changed in
`app/race-manager.html`, change it there too or this passes while the app is
wrong.

## Phase 2 - server, data safety and the display contract (fast, always run)

```
python dev/tests/test_server.py
```

21 checks, unattended, no browser. Covers the things that broke on
2026-10-10: a stalled client must not block anyone, the display page must not
be able to paint itself blank, concurrent saves must not corrupt the database,
and the backup safety nets must behave.

Expect **21 passed, 0 failed**. If a check fails, read what it says it is
protecting against before changing it - each one is there because something
went wrong.

## Phase 3 - a full race night through the real app (the important one)

This is the phase that catches user-flow bugs, and the phase it is most
tempting to skip.

1. Start the app against an empty scratch database:
   ```
   TAMIYA_DATA_DIR=<scratch> TAMIYA_ARCHIVE_DIR=<scratch>/arch python app/server.py --no-browser
   ```
   with `<scratch>/racedata.json` =
   `{"version":1,"seasons":[],"racers":[],"currentSeason":null}`
2. Open `http://127.0.0.1:8765/race-manager.html`.
3. Run `dev/tests/e2e_race_night.js` in the page (paste into the console, or
   serve it from a second port and inject a `<script src>` - the Chrome
   extension evaluates in an isolated world and cannot see page functions, so
   a plain `javascript_tool` call will say `toggleFullScreen is not defined`).
4. It creates a season and runs Box, EVO and Pro to a podium, asserting that
   every heat advances, the display content changes as racing proceeds, and
   finishing positions come out 1..n.
5. **Then check the file on disk**, not just the page:

```python
import json, collections
db = json.load(open(r"<scratch>/racedata.json", encoding="utf-8"))
ev = [e for s in db["seasons"] for e in s["events"]]
ids = {r["id"] for r in db["racers"]}
assert len(ev) == 3
assert not [1 for k,v in collections.Counter(r["id"] for r in db["racers"]).items() if v>1]
assert not [1 for k,v in collections.Counter(e["id"] for e in ev).items() if v>1]
assert all(r.get("rosterId") in ids for e in ev for r in e["results"] if r.get("rosterId"))
assert any(s["id"] == db["currentSeason"] for s in db["seasons"])
```

Also in the same session, because these are the regressions that reached the
club:

- **Crash recovery** - start a race, run a few heats, reload the page. It must
  offer to resume with the right summary, restore the heats, and still finish.
- **Garbage import** - feed `importData` a non-JSON file, a JSON file of the
  wrong shape, an empty file, and one with `version: 99`. Every one must be
  refused with a clear message and **leave the data unchanged**.
- **Roster scroll** - scroll the roster list down, pick a racer, confirm the
  list stays where it was and the search box keeps focus.
- **Full Screen button** - must read "Exit Full Screen" while full screen, on
  both the home and race screens.

## Phase 4 - the upgrade, with a real database (run before every deployment)

```powershell
.\dev\tests\test_upgrade.ps1 `
  -OldInstaller dist\installer\TamiyaRaceManager-Setup-<what the club runs>.exe `
  -NewInstaller dist\installer\TamiyaRaceManager-Setup-<new>.exe `
  -DataFile <a copy of the club's racedata.json>
```

Installs the old build, loads the real database, installs the new build over
the top, and proves the file is byte-identical throughout. This is the exact
sequence the club performs. It refuses to run if port 8765 is busy.

## Phase 5 - what only a human can do

State these as **untested** rather than implying otherwise:

- The **native app window** (pywebview / WebView2). Everything in phases 2-4
  that goes through a browser exercises the same HTML, but the Python bridge
  does not exist in a browser - so **Export Data's Save dialog and the second
  display window are not covered**. Export failing silently in the app window
  while working perfectly in a browser is exactly the v10.1 bug.
- A **real second monitor**, including unplugging it mid-race.
- **SmartScreen** on a machine that has never seen the app.
- **macOS** anything.

---

## Reporting

Give the user a table: phase, result, and what it covered. Then, separately
and plainly, **what was not tested**. If a phase was skipped, say which and
why. If something failed, lead with that - not with the count of passes.

Update the results table at the bottom of `dev/TESTING_MANUAL.md` with the
date and the build number, so the next person knows what was last proven
rather than guessing.
