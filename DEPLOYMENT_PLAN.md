# Tamiya Race Manager — v10 Packaging & Deployment Plan

*Created: 2026-07-16 · Branch: `v10-packaging` · Status: IN PROGRESS*

---

## Goals

1. **One-click install** — a single Windows installer with a desktop icon. No Python
   download step, no admin bat files, no zip juggling.
2. **Updates can never damage a club's database.** Data and app are physically
   separated so an installer cannot touch race data, by construction.
3. **Backups happen automatically.** Clubs that never back up are still protected.
4. **Backward-compatible data import** — old backups always load into new versions;
   a clear, friendly refusal (never corruption) when a file is too *new* for the app.
5. `main` stays the stable v9.x line until this branch is proven rock solid.

## Branch strategy

| Branch | Purpose |
|---|---|
| `main` | Stable v9.27 — what clubs run today. Only critical fixes land here until merge. |
| `v10-packaging` | All work in this plan. Merged to `main` only after the full test matrix passes. |

Tag `v9.27` on `main` before merge so the last pre-installer version is always
recoverable and downloadable.

---

## Architecture changes (the core of the safety guarantee)

### 1. Data moves out of the app folder

| | Location |
|---|---|
| App (replaceable) | `%LOCALAPPDATA%\Programs\TamiyaRaceManager\` |
| Data (never touched by installer) | `%LOCALAPPDATA%\TamiyaRaceManager\racedata.json` |
| Backups | `%LOCALAPPDATA%\TamiyaRaceManager\backups\` |

**One-time migration on first launch of v10:** if a legacy `data/racedata.json`
exists next to the app (or in the folder of a previous zip install) and the new
location is empty, it is **copied** (not moved) to the new location. The original
is left in place as a fossil backup. The app shows a one-time notice telling the
user where their data now lives.

### 2. Schema version + forward migrations

`racedata.json` already carries `"version": 1`. From v10 onward:

- Every breaking change to the data format bumps `version` and ships a migration
  function (`v1→v2`, `v2→v3`, …). Migrations are cumulative and **never removed**,
  so a file from any past version can always be walked forward to current.
- Before any migration runs, the untouched original is saved to
  `backups/pre-upgrade-v{N}-{date}.json`. Migration failure = app refuses to
  start the upgrade and points at the backup; the original file is never modified
  in place.
- **File newer than the app** (`version` > supported): the app refuses to load or
  import it with a clear message — *"This data file was created by a newer version
  of Race Manager. Please update the app first — your data has not been changed."*
  Same rule for the Import Data button. A too-new file is never written to.

### 3. Automatic rolling backups

- On every save, the server keeps one backup per day: `backups/racedata-YYYY-MM-DD.json`
  (first save of the day creates it — i.e. it preserves *yesterday's final state*).
- Keep the most recent 14 daily backups, prune older automatically.
- Export Data button remains for USB/off-machine backups and is still recommended
  in the docs after every race night.

---

## Work phases

### Phase 1 — Data-safety fixes (no format changes, could even be back-ported to v9)
*Completed 2026-07-16 as v9.28 — needs field-style manual testing (matrix #7, #8, #11).*
- [x] `saveDB()` checks `response.ok`; on failure falls back to localStorage **and**
      shows a persistent on-screen warning banner (not just a toast).
- [x] Server watchdog made sleep-tolerant: a large wall-clock jump (laptop slept)
      resets the ping timer instead of killing the server.
- [x] App detects a dead server mid-session (failed pings) and shows a loud
      persistent banner: data is not reaching disk; how to recover.
- [x] Import Data validates structure, shows a summary confirm
      ("3 seasons, 42 racers — replace current data?"), and snapshots the current
      DB (browser storage, `tamiya_race_db_preimport`) before replacing it.
- [x] Automatic daily rolling backups (server side, `data/backups/`, keep 14).
- [x] `saveEditResult()` calls `saveActiveRace()` so corrections survive a crash.
- [x] Season standings keyed by roster id — `res.rosterId`, falling back to
      name→id lookup then raw name for typed-in racers and pre-v9.28 events.

### Phase 2 — Data relocation & migration framework
*Completed 2026-07-17 as v9.29 — server endpoints + migration tested end-to-end
against real test data (copy, idempotency, /save round-trip verified identical).*
- [x] Server stores data in `%LOCALAPPDATA%\TamiyaRaceManager\` (Windows),
      `~/Library/Application Support/TamiyaRaceManager` (Mac); `TAMIYA_DATA_DIR`
      env-var override for portable use. `/data/racedata.json` is routed to the
      new home so the app's fetch path is unchanged.
- [x] Legacy-data auto-migration (copy, never move; legacy backups copied too;
      `DATA-HAS-MOVED.txt` note left behind) + one-time in-app notice via `/info`.
- [x] Schema version gate on load and on import (refuse-newer rule; `dbReadOnly`
      blocks all writes when refused).
- [x] Migration scaffolding (`SCHEMA_VERSION`/`MIGRATIONS` walk-forward) with a
      tagged pre-upgrade backup via new `POST /backup` endpoint.

### Phase 3 — Single executable
- [ ] PyInstaller build: `TamiyaRaceManager.exe` bundling server + HTML + icon.
- [ ] Friendly handling of port 8765 conflicts (detect an already-running instance
      and just open the browser to it, instead of a traceback).
- [ ] Browser opens only after the server is confirmed listening.
- [ ] Single source of truth for the version string (shown in app header, server
      console, installer, and About).

### Phase 4 — Installer
- [ ] Inno Setup script: per-user install (no admin), desktop icon, Start Menu
      entry, proper uninstaller.
- [ ] Installer welcome page states plainly: **"Your race data is stored separately
      and is not modified by this installer."** plus the standard advice to Export
      Data before any update.
- [ ] Installer detects a legacy zip-style install (if upgrading in place) and
      explains what will happen to the old folder.
- [ ] Document the SmartScreen "unsigned app" click-through with screenshots
      (code signing deferred — cost).

### Phase 5 — Test matrix (all must pass before merge)

| # | Scenario | Expected |
|---|---|---|
| 1 | Fresh install, no prior data | Clean first run, empty DB created in new location |
| 2 | Install over machine with v9.x zip + existing `data/racedata.json` | Data auto-copied, original untouched, seasons/points intact |
| 3 | Run installer twice (update over v10) | App files replaced, data + backups untouched |
| 4 | Import a v9.x export file into v10 | Loads and migrates cleanly |
| 5 | Import a v10 export into v9.x *(downgrade)* | v9 has no version gate — documented as unsupported; release notes warn |
| 6 | Import a future-versioned file into v10 | Friendly refusal, no data written |
| 7 | Laptop sleep mid-event, wake, continue racing | Server alive, saves still hit disk |
| 8 | Kill server mid-event | Persistent warning banner appears; localStorage holds data; recovery path documented |
| 9 | Race night crash + relaunch | Resume modal restores in-progress race (existing feature, re-verify) |
| 10 | Port 8765 already in use | Friendly message / reuse, no traceback |
| 11 | Import wrong/garbage JSON | Rejected with message, DB unchanged |
| 12 | Full race night simulation on packaged exe (Box+EVO+Pro, juniors, edit result, display window, exports) | Identical behaviour to v9.27 |

### Phase 6 — Release & merge
- [ ] Tag `v9.27` on `main` (last zip-style release, kept downloadable).
- [ ] `BUILD.md` — how to produce the exe + installer from a clean checkout.
- [ ] Release notes template incl. the **pre-update checklist for clubs**:
      1. Open old version → Export Data → save to USB.
      2. Run the new installer.
      3. Launch, confirm seasons & standings look right.
      4. Keep the USB export until confident.
- [ ] Merge `v10-packaging` → `main`, tag `v10.0`, publish GitHub release with
      installer + plain zip (portable fallback).

---

## Known risks — advertised, with instructions

| Risk | Who is affected | Mitigation / instruction |
|---|---|---|
| **localStorage-mode data doesn't carry over.** A club that ran v9.x *without* Python (opened the HTML directly) has data in the browser under a `file://` origin. The packaged app serves from `localhost:8765` — a different origin — so that data will NOT appear automatically. | Only clubs that never had Python working (no `data/racedata.json` on disk) | Release notes + installer text: *before updating*, open the old version and use **Export Data**, then **Import Data** in the new version. This is the universal bridge and must be stated prominently. |
| Downgrading (v10 file → v9 app) is not supported | Anyone rolling back | Keep the pre-upgrade backup + v9.27 zip download available; document that rolling back means restoring the pre-upgrade backup file, not the v10 file. |
| SmartScreen warning on unsigned exe | All new installs | Documented click-through with screenshots; consider code signing later if budget allows. |
| Club on a very old v9.x with a hand-edited/odd JSON | Rare | Import validation reports *what* is wrong instead of silently accepting; pre-upgrade backup always taken first. |

## Compatibility policy (plain English, for release notes)

- **Old data into a new app: always works.** Migrations ship forever.
- **New data into an old app: politely refused, never corrupted.** The fix is to
  update the app, which is always free and safe.
- **The Export Data JSON is the universal interchange format** across every
  version, storage mode, and machine move.
