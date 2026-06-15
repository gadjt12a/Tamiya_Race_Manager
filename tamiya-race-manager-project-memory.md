# Tamiya Race Manager — Project Memory

*Last updated: May 2026*

---

## Project Overview

A race management application built in **HTML + vanilla JavaScript**, designed to run on a single laptop connected to two screens:

- **Screen 1 (Coordinator):** Race coordinator enters results, confirms races, manages the event
- **Screen 2 (Display):** Public audience display showing current race and next race up

The app is a fully standalone, real-world-usable tool. No frameworks. Data persists via a local Python HTTP server writing to a JSON file, with localStorage fallback.

---

## Application Architecture

### Files
```
race-manager/
├── race-manager.html       # Main app (all HTML/CSS/JS in one file)
├── server.py               # Python local HTTP server (data persistence + shutdown watchdog)
├── START RACE MANAGER.bat  # Windows launcher (auto-detects Python, falls back to direct open)
├── data/
│   └── racedata.json       # Persistent data store
└── (optional) README/help text built into app
```

### Data Layer
- `server.py` runs on `localhost:8765`, serves static files + handles `/save` POST and `/ping` GET
- Watchdog thread in server: if no ping received for 12 seconds (browser tab closed), server self-terminates
- App falls back to `localStorage` if no server is detected
- Export/Import data buttons on home screen for USB backup

---

## Race Logic (Core Bracket Rules)

### Double-Elimination Style
- All racers start in the **Main bracket**
- Races prefer groups of **3**; groups of 2 are used when required
- **Losers from Main** drop to **2nd Chance bracket**
- **Winners from 2nd Chance** stay in 2nd Chance bracket
- **Losers from 2nd Chance** are **eliminated** (2 total losses = out)
- Everyone is guaranteed at least 2 races

### Round Alternation (Critical Rule)
Rounds alternate strictly — **all Main races finish before any 2nd Chance races begin**, and vice versa:
```
Main Round → 2nd Chance Round → Main Round → 2nd Chance Round → ... → Final
```

### The Final
- Requires **exactly 3 racers**: 1 Main winner + 2 separate 2nd Chance winners
- Final is triggered when `mainPool.length === 1` AND `secondPool.length === 2`
- The last 2nd Chance round must be structured to produce **2 separate winners** (not 1) — requires careful batch sizing when 3 racers remain in 2nd Chance

### Batch Sizing (`makeBatches`)
Modulo arithmetic to avoid solo races:
- `n % 3 === 0` → all groups of 3
- `n % 3 === 2` → one group of 2, rest groups of 3
- `n % 3 === 1` → two groups of 2, rest groups of 3

**Never produces groups of 1.**

---

## Race Classes

Three classes run **independently and sequentially**:
1. **Box Class**
2. **EVO Class** (also has a parallel Junior points table)
3. **Pro Class**

Each class has its own racer list, bracket, and points table.

**Special Events** also supported — separate points scheme, not linked to season standings unless specified.

---

## Points System

- Top finishers per class event earn points (winner = 10, descending)
- Points accumulate across the season per class per racer
- EVO has a **parallel Junior table** — juniors compete in the same bracket but have their own standings
- Junior flag is a **toggle** on each racer when entering names
- Test races do **not** count toward season points
- Three points schemes: Standard, Double, Podium Only

---

## Season Management

- Start a new season with a name and start date (one active season at a time)
- View current standings: Box, EVO, Pro, EVO Juniors
- Close a season (becomes read-only archive)
- View previous seasons from archive
- Data file: `racedata.json` (JSON, versioned)

---

## Key Features

| Feature | Notes |
|---|---|
| ✏️ Edit Names | Edit racer names mid-event without affecting bracket logic |
| 📺 Display Window | Pop-up second screen (requires browser pop-ups allowed) |
| Export HTML | Self-contained webpage, good for emailing |
| Export CSV | Opens in Excel, full results + race history |
| Print / PDF | Print-ready page, use "Save as PDF" |
| Edit Last Result | Can correct the most recent race result without corrupting pool state |
| Delayed Race | Can swap to a different queued race if there's a hold-up |
| Roster / Racer DB | Persistent racer list — quickly add known racers to a new event |

---

## Technical History & Bug Fixes

### Two Full Rewrites
State management complexity accumulated through iterative patching. Two full rewrites were more effective than continued patching.

### Key Bugs Resolved

| Bug | Root Cause | Fix |
|---|---|---|
| Confirm button not firing on 2-person races | `!p[3]` guard blocking 2-racer confirmation | Removed guard, handled 2-racer case explicitly |
| Variable shadowing in place-checking | Local `p1/p2/p3` variables shadowing object properties | Switched to explicit `r.p1`, `r.p2`, `r.p3` properties on race objects |
| Solo racers in queues | Pool forming races before enough racers available | Require 2+ in pool before forming any race |
| Only 2 finalists in final | Pool bleeding between rounds | Strict round-based flushing — build entire round from pool snapshot, clear pool atomically |
| Batch sizing producing groups of 1 | Naive grouping with remainder = 1 | `makeBatches()` with modulo arithmetic |
| 2 finalists instead of 3 (real-world catch) | Final 2nd Chance round with 3 racers produced only 1 winner instead of 2 | Fixed final 2nd Chance structure to guarantee 2 separate winners |

### Architecture Decisions
- **Explicit `p1`, `p2`, `p3`** on race objects (not a `places` object) — avoids variable shadowing
- **Separate `mainPool` / `secondPool`** arrays with strict round-based flushing
- **`makeBatches()`** centralises all grouping logic
- **`buildNextRound()`** called only when `roundQueue` is empty (i.e., full round completed)

---

## Simulators / Testing Tools

### Standalone Race Logic Simulator
- Add names manually or paste a list
- Run with randomised results
- Validates: no solo races, correct eliminations, everyone races at least twice, final race validity
- Pre-loaded with the 21-name test pool

### Bulk Simulator (100+ runs)
- Random subsets of 5–21 racers from the 21-name pool
- 100+ simulation runs per batch
- Checks: solo races, incorrect eliminations, minimum race counts, final race composition
- Built in direct response to a real-world edge case that single simulation missed

---

## Test Racer Name Pool

```
John, James, Mike, Paul, Steve, Jessie, Jamie G, Kris, Geoff, Jamie H,
Dave, Snake, Barry, Billy, Zara, Nick, Nate, Kirsten, Ryan, Anton, Stella
```
(21 racers — odd number intentional for edge case testing)

---

## Known Remaining / Future Items

At time of last session:
- Special Events points wiring — partially built, needs verification
- Delayed race swap — button exists, needs end-to-end test
- Previous seasons archive view — built, needs real-data test
- Edit Last Result with pool state — rebuilt with snapshot approach, needs test
- Display window live standings for audience — **deliberately deferred** (will be released when ready)

---

## Deployment Notes

- Runs entirely on a single laptop
- Python 3 required for data persistence (`server.py`)
- If no Python: app opens directly but data won't persist between sessions
- `.bat` launcher auto-detects Python, handles both `python` and `python3` commands
- Browser pop-ups must be allowed for the second screen display window
- Data backup: `Export Data` button → save to USB after every race night

---

## Chat History References

| Chat | Topic |
|---|---|
| "Tamiya Racing App with Multiscreen" | Original build, full rewrites, simulator, bulk tester, multiscreen, bug fixes |
| "Race tournament logic and points management system" | Full multi-class expansion — points, seasons, juniors, server, exports, .bat launcher |
