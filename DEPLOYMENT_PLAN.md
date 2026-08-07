# Tamiya Race Manager — v10 Packaging & Deployment Plan

*Created: 2026-07-16 · **Merged to `main` 2026-08-08** · Status: MERGED —
not yet released (see Phase 6 for what's still open)*

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
| `v10-packaging` | All work in this plan. **Merged to `main` on 2026-08-08** at v9.39, ahead of the full test matrix — Kris's call, so the OSX work happens on `main`. The branch is kept for history; new work goes on `main`. |

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
*Completed 2026-07-17 as v9.30 — exe smoke-tested end-to-end (migration from
beside the exe, bundled HTML serving, /info version, already-running guard,
watchdog first-ping gating + tab-close detection). Icon still pending (Kris
supplying artwork — candidates in Working_Files/Images/, untracked).*

> **Superseded by v9.39 (Phase 7).** The onefile build below was replaced by
> a **onedir** build. The exe now ships alongside an `_internal\` folder and
> must never be moved or copied on its own.

- [x] PyInstaller build: `TamiyaRaceManager.exe` (~8 MB onefile) bundling server +
      HTML + VERSION via `BUILD EXE (developer use only).bat`; `--icon` wired in,
      activates when `icon.ico` exists.
- [x] Friendly handling of port 8765 conflicts: an already-running instance is
      detected via `/ping` and the browser is opened to it; a foreign program on
      the port gets a plain-English error instead of a traceback.
- [x] Browser opens only after the server is bound and listening (and a browser
      failure can't kill the server).
- [x] Single source of truth for the version string: `VERSION` file → server
      console, `/info`, app header label, build script.
- [x] *(found in field test)* Watchdog no longer kills the server before the
      browser's **first** ping (SmartScreen/AV/cold-start delays); 5-minute
      give-up if no browser ever connects. Server binds `127.0.0.1` only — no
      Windows Firewall prompt, not visible on the LAN.

### Phase 4 — Installer
*Completed 2026-07-17 as v9.32 — silent install tested on a real machine:
files in `{localappdata}\Programs\TamiyaRaceManager`, Start Menu + desktop
shortcuts created (OneDrive-redirected desktop handled), installed exe runs
and serves v9.32 from the proper data home.*
- [x] Inno Setup script (`TamiyaRaceManager.iss`, built by `BUILD INSTALLER
      (developer use only).bat`): per-user install (PrivilegesRequired=lowest),
      desktop icon (default on, optional), Start Menu entry, uninstaller.
      Installer asks a running instance to shut down gracefully first
      (POST /shutdown) so race-night updates can't hit a locked exe.
- [x] Pre-install info page (`installer-info.txt`): data lives separately and is
      never touched by install/update/uninstall; Export Data advice; explicit
      browser-storage-mode export/import steps. Uninstall shows a
      your-data-is-kept reminder.
- [x] Legacy zip-style installs: covered by the info page + the app's own
      copy-not-move migration on first launch (no installer logic needed).
- [ ] Document the SmartScreen "unsigned app" click-through with screenshots
      (needs a machine that hasn't seen the exe — fold into Phase 6 release
      notes; code signing deferred — cost).

### Phase 4b — Native desktop app (added at Kris's request, v9.33)
*Completed 2026-07-17 — the installed exe now runs as a real desktop app.*
- [x] `app.py` entry point: pywebview native window, server runs invisibly
      inside the process, window close = full shutdown, no console/browser.
- [x] Display feed moved server-side (`/display` + `/display-content`): native
      second window (auto-fullscreen on 2nd monitor), browser popup uses the
      same page; legacy opener-poll popup kept for no-server mode.
- [x] Fallbacks: WebView2/GUI failure → browser mode; windowed build logs to
      `%LOCALAPPDATA%\TamiyaRaceManager\app.log`; zip/console mode unchanged.
- [ ] Kris to run test matrix #13 (exports/print/import + display inside the
      native window — WebView2 handles downloads/popups differently to Chrome).

> **Icon licensing: RESOLVED (v9.37).** `app/icon.ico` is now generated from
> Kris's licence-clean `Race_App_Icon.png` artwork. The earlier watermarked
> stock candidates were never shipped.

### Phase 5 — Test matrix (all must pass before merge)

Scripted results from 2026-07-17 run against the v9.35 packaged exe.

| # | Scenario | Expected | Result |
|---|---|---|---|
| 1 | Fresh install, no prior data | Clean first run, empty DB created in new location | ✅ PASS (scripted) |
| 2a | New exe dropped INTO old zip folder | Data auto-copied, original + legacy backups untouched, moved-note written | ✅ PASS (scripted; hash-verified byte-identical) |
| 2b | Installer-style upgrade — old data in a *different* folder | No false migration (boots empty); Import Data with old `racedata.json` brings everything across; old file untouched. First-run hint + installer text guide the user | ✅ PASS (scripted; import path hash-verified) |
| 3 | Run installer twice (update over v10) | App files replaced, data + backups untouched | ✅ PASS (scripted; data hash+mtime unchanged) |
| 4 | Import a v9.x export file into v10 | Loads cleanly (same JSON as #2b) | ✅ PASS (scripted via #2b) |
| 5 | Import a v10 export into v9.x *(downgrade)* | v9 has no version gate — documented as unsupported; release notes warn | 📋 documentation-only |
| 6 | Future-versioned data file (version 99) | Refused read-only, file never written | ✅ PASS (scripted; full app session in real window, file byte-identical after) — banner visual: Kris |
| 7 | Laptop sleep mid-event, wake, continue racing | Server alive, saves still hit disk | 🧑 KRIS — real hardware |
| 8 | Kill server mid-event | Warning banner ~6s, browser holds data, recovery works | ✅ Kris verified 2026-07-16 (browser mode); re-check once in app window |
| 9 | Race night crash + relaunch | Resume modal restores in-progress race | 🧑 KRIS — with #12 |
| 10 | Port 8765 already in use | Second instance opens window onto running app; foreign program → message window | ✅ already-running scripted (v9.30); foreign-port path code-reviewed |
| 11 | Import wrong/garbage JSON | Rejected with message, DB unchanged | 🧑 KRIS — UI-side, 30 seconds |
| 12 | Full race night simulation on packaged exe (Box+EVO+Pro, juniors, edit result, display window, exports) | Identical behaviour to v9.27 | 🧑 KRIS |
| 13 | Native-window feature pass: display second window (1 + 2 monitors), Export HTML/CSV downloads, Print/PDF, Import Data file picker | All work inside the desktop app window; any WebView2 quirks documented | 🧑 KRIS |

### Phase 4c — Platform separation (added at Kris's request, v9.36)
*Completed 2026-07-17 — repo restructured with `git mv` (history preserved).*
- [x] `app/` (shared core: HTML, server.py, app.py, VERSION, icon),
      `windows/` (installer script, build bats, Windows README),
      `mac/` (launcher, package builder, Mac README with UNTESTED disclaimer).
- [x] Three clean release artefacts: Windows installer, Windows portable zip
      (just the exe — the python-bundle machinery and its three bat files are
      removed as obsolete), Mac zip. All build into `dist\`.
      *(v9.39: the portable zip now contains the whole app folder, not a bare
      exe — the onedir build needs `_internal\` beside it.)*
- [x] Root README.md rewritten as a platform picker; per-platform READMEs ship
      inside the packages.
- [x] Rebuilt + smoke-tested from the new layout (exe serves v9.36); Mac zip
      contents verified; Mac launcher works in both packaged and repo layouts.

### Phase 7 — Field-test fixes from the second PC (v9.39)
*2026-08-07. Everything here came out of Kris deploying to a second machine.
Re-verified by Kris on 2026-08-07: fresh `git clone` → build installer →
install → run, all working.*
- [x] **BUILD.md was unusable on a clean PC** — Windows has no git, so
      `git clone` failed outright, and the clone command checked out `main`
      with no way to reach `v10-packaging`. Added a git install step, a
      branch-aware checkout section, and a no-git zip download path.
- [x] **Launch failure: 14 error dialogs** ("Failed to load Tcl DLL",
      "File already exists but should not"). Cause: the v9.38 `--splash` is
      Tcl/Tk, dragging `tcl86t.dll`/`tk86t.dll`/`_tcl_data`/`_tk_data` into a
      WebView2 app, tripped by a stale `_MEI` dir in `%TEMP%`.
      Fixed by switching **onefile → onedir**, removing per-launch temp
      extraction entirely. Installer 21.7 MB → 15.9 MB.
- [x] **Splash abandoned after three attempts** — Tcl/Tk (broke launches),
      an in-window HTML loading page (visible ~10 ms; WebView2 can't paint
      until it has initialised), and a native Win32 window (declined as not
      worth the machinery). Rationale recorded in `app/app.py`.
- [x] **~2 s wasted on every launch.** `already_running()` probed
      `localhost`, which resolves to IPv6 `::1` first while the server binds
      IPv4 only, so every start burned a timeout on an address that could
      never answer. Now probes `127.0.0.1` with a 0.35 s timeout:
      **3.00 s → 0.48 s** to window. Timing `stamp()` lines kept in
      `app.log` — this was misattributed to WebView2 twice by reasoning
      instead of measuring.
- [x] **Build numbering**: packages are now `<VERSION>.<build>` where build
      is `git rev-list --count HEAD`, so the number tracks the *commit*, not
      the machine or how many times a build was run. Written to gitignored
      `app/BUILD`; shows in installer filename, app header, `app.log` and
      the exe's Properties (which previously had no version info at all).
- [x] Window opens **centred and sized to fit the screen** — Windows was
      cascading it down-and-right, part-way off smaller screens.
- [x] **Full Screen button** (Home + Race topbars, F11). Native pywebview
      window, browser Fullscreen API fallback. *Confirmed working by Kris.*
- [x] **Close Season now warns properly** — names the season, reports its
      event count, spells out what closing does. *Confirmed by Kris.*
- [x] **Reopen an accidentally closed season** from the Season Archive.
      Refuses while another season is active. *Confirmed by Kris on the test
      PC; not yet exercised against a season with recorded events.*
- [x] Home screen holds its alignment when the window is resized (hero
      buttons wrap, `minmax(0,…)` columns, <900px stacking breakpoint).
      *Confirmed by Kris.*

### Phase 6 — Release & merge
- [x] Tag `v9.27` on `main` (last zip-style release, kept downloadable) —
      done 2026-07-16.
- [x] `BUILD.md` — full clean-checkout build guide for all three packages,
      incl. smoke-test checklist and gotchas (ASCII bats, SmartScreen,
      WebView2, icon regeneration).
- [x] `RELEASE_NOTES_v10.md` (DRAFT) — club-facing: pre-update checklist,
      SmartScreen click-through (screenshot placeholders pending a fresh
      machine), zip→installer import step, browser-storage-mode caveat,
      what's-new, downgrade policy, Mac untested disclaimer.
- [ ] Fill in SmartScreen screenshots (needs a machine that hasn't seen the
      exe).
- [ ] Kris's manual test matrix items pass — step-by-step guide in
      `TESTING_MANUAL.md` (T1–T7, incl. the SmartScreen screenshot list).
      Icon licence: resolved in v9.37. **Partial:** fresh clone → build →
      install → run confirmed on a second PC 2026-08-07; the T1–T7 results
      table is still empty.
- [ ] **Upgrade over an existing v9.3x install** — never tested. `{app}`
      goes from a lone exe to exe + `_internal\`. Every test so far has been
      a fresh install or a clean clone. This is the one that touches
      machines clubs already run.
- [ ] **Reopen a season that has recorded events**, then confirm the
      standings still read correctly.
- [ ] Print / PDF export from inside the WebView2 window (test matrix #13)
      — still the most likely thing to misbehave.
- [ ] **Run the Mac package on an actual Mac.** It has been built many times
      and never once executed. Decide before merge whether v10.0 ships it,
      holds it for a point release, or ships it labelled experimental.
- [x] Merge `v10-packaging` → `main` — done 2026-08-08 (`bf56cb3`), at
      v9.39. `BUILD.md`'s "Getting the source" section rewritten for `main`
      at the same time.
- [ ] Retitle release notes to final, remove the DRAFT banner, bump
      `app/VERSION` to `10.0`, tag `v10.0`, publish the GitHub release with
      all three packages attached. **Blocked on:** the SmartScreen
      screenshots, and a decision on whether the Mac package ships in v10.0
      at all given it has never been run.

---

## Known risks — advertised, with instructions

| Risk | Who is affected | Mitigation / instruction |
|---|---|---|
| **Zip → installer upgrades don't auto-migrate.** The installed exe lives in `%LOCALAPPDATA%\Programs\`, so it can't see data in the old zip folder — the app boots looking empty. Data is safe but *looks* lost. | Every club moving from zip to installer | First-run hint on the home screen + installer info page: use **Import Data** with the old folder's `data\racedata.json`. Old file is never touched. (Auto-migration still works when the exe runs from inside the old folder.) |
| **localStorage-mode data doesn't carry over.** A club that ran v9.x *without* Python (opened the HTML directly) has data in the browser under a `file://` origin. The packaged app serves from `localhost:8765` — a different origin — so that data will NOT appear automatically. | Only clubs that never had Python working (no `data/racedata.json` on disk) | Release notes + installer text: *before updating*, open the old version and use **Export Data**, then **Import Data** in the new version. This is the universal bridge and must be stated prominently. |
| **Portable-zip users must extract the whole folder.** The onedir exe needs `_internal\` beside it; running it out of Windows' zip preview, or copying just the exe out, fails to start. | Anyone using the portable zip | Spelled out in `windows/README.txt` and the release notes, including how to make a desktop shortcut instead of moving the exe. |
| **Upgrading over an existing install is untested.** `{app}` changes from a lone exe to exe + `_internal\`. Data lives elsewhere so it should be unaffected, but "should" is not "tested". | Every club already on v9.3x | Test before merge. Data is in `%LOCALAPPDATA%` and untouched by the installer either way; the pre-update export in the release notes remains the safety net. |
| **Port 8765 conflict is not reliably detected on Windows.** Found 2026-08-08: another of Kris's tools (`T-Embed_CC1101_Plus` serialmon daemon, `--ctrl-port 8765`) was holding the port. Race Manager logged "server up" and opened its window as if fine, but no request to it ever answered. `create_server()` sets `allow_reuse_address = True`, and on Windows SO_REUSEADDR permits binding an address already in use — so the OSError the friendly port-conflict screen relies on never fires. The `/ping` guard didn't catch it either, since the other program isn't Race Manager. | Anyone running another tool on 8765 — on race night this looks like the app starting then being dead | **Not yet fixed.** Likely fix: drop `allow_reuse_address` on Windows, or probe the port with `SO_EXCLUSIVEADDRUSE` before binding, so the existing friendly error actually triggers. Note this contradicts the Phase 3 "friendly handling of port 8765 conflicts" tick, which only ever covered a *refused* bind. |
| Downgrading (v10 file → v9 app) is not supported | Anyone rolling back | Keep the pre-upgrade backup + v9.27 zip download available; document that rolling back means restoring the pre-upgrade backup file, not the v10 file. |
| SmartScreen warning on unsigned exe | All new installs | Documented click-through with screenshots; consider code signing later if budget allows. |
| Club on a very old v9.x with a hand-edited/odd JSON | Rare | Import validation reports *what* is wrong instead of silently accepting; pre-upgrade backup always taken first. |

## Compatibility policy (plain English, for release notes)

- **Old data into a new app: always works.** Migrations ship forever.
- **New data into an old app: politely refused, never corrupted.** The fix is to
  update the app, which is always free and safe.
- **The Export Data JSON is the universal interchange format** across every
  version, storage mode, and machine move.
