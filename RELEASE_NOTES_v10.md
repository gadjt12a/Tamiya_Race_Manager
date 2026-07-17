# Tamiya Race Manager v10.0 — Release Notes

> **STATUS: DRAFT** — will accompany the GitHub release when the v10 test
> matrix is signed off. Screenshot placeholders marked `[SCREENSHOT]`.

Race Manager is now a proper desktop application with a one-click installer.
This is the biggest update since the app was built — but your race data is
safer than it has ever been, and bringing it across takes one step.

---

## ⭐ Before you update — 2-minute checklist

1. Open your **current** Race Manager one last time.
2. Click **⬆ Export Data** and save the file to a USB stick.
3. Keep that USB stick until you're happy the new version has everything.

That's it. Updates are designed so they *cannot* touch your race data — the
export is belt-and-braces, and good practice after every race night anyway.

---

## Installing (Windows)

1. Download **`TamiyaRaceManager-Setup-10.0.exe`** from this release.
2. Run it. Windows SmartScreen will likely show **"Windows protected your
   PC"** — this is normal for a small club app that isn't code-signed:
   click **More info**, then **Run anyway**. `[SCREENSHOT]`
3. The installer shows a data-safety page (worth reading once), then installs
   in seconds. No admin rights needed.
4. Launch from the **desktop icon**. The app opens in its own window — no
   black console window, no browser tab.

Prefer nothing installed? **`TamiyaRaceManager-WindowsPortable-10.0.zip`** is
the same app in a zip — unzip anywhere (USB fine) and run the exe.

### Bringing your data across from the old zip version (one time)

Your old data is untouched in the old race-manager folder. In the new app:
**⬇ Import Data** (top right) → choose **`data\racedata.json`** inside your
old race-manager folder → done. Seasons, racers and points all come across.
(The app shows this hint on first run too.)

⚠ If your old version ran **without Python** (it warned about "browser
storage mode"): open the OLD version first, click **Export Data**, and import
that file instead — there is no data file on disk in that mode.

## Installing (Mac / OSX) — ⚠ untested

**`TamiyaRaceManager-Mac-10.0.zip`** contains the same core app (needs
Python 3, runs in your browser). We develop on Windows and have not been able
to test it — please report anything broken. See the README inside the zip.

---

## What's new since v9.27

### The app itself
- **Real desktop app** — own window, desktop icon, Start Menu entry. Closing
  the window shuts everything down. No console, no browser tab.
- **One-click updates** — just run the newer installer over the top.

### Your data (the important part)
- Race data now lives **outside the app** in
  `%LOCALAPPDATA%\TamiyaRaceManager\`, so installing, updating or
  uninstalling can **never** touch it.
- **Automatic daily backups** (last 14 days) kept next to the data.
- If saving ever fails mid-event, a **red warning banner** appears with
  recovery instructions instead of data silently going nowhere.
- Laptop lid closed during a break? The app survives sleep/wake now.
- Import is validated and confirmed before anything is replaced; a data file
  from a *newer* app version is politely refused, never overwritten.

### Race night
- **The 2nd-screen display no longer goes stale** — and after a class
  finishes, the **winners stay on screen** for call-ups and prize-giving
  until the next race starts.
- **EVO prize screen**: class winners on the left, **Junior winners on the
  right**.
- With a second monitor connected, the display window goes **full-screen on
  the projector automatically**.
- Roster lists are **alphabetical** everywhere.
- Season roster now has a **JNR/ADL switch** per racer — juniors can return
  next season as adults without re-entry.
- New seasons pre-tick last season's racers — regulars carry over in one
  click.

---

## Notes & known limitations

- **Downgrading is not supported.** A v10 data file will not load in v9.x.
  To roll back, reinstall v9.27 (kept downloadable) and restore from
  `%LOCALAPPDATA%\TamiyaRaceManager\backups\` or a pre-update export.
- **WebView2**: the desktop window uses Microsoft Edge WebView2 (built into
  Windows 11 / current Windows 10). If missing, the app opens in your
  browser instead — everything still works.
- The exe is **not code-signed** (cost) — hence the one-time SmartScreen
  prompt above.
- The **Mac package is untested** — feedback wanted.

## Files in this release

| File | Platform |
|---|---|
| `TamiyaRaceManager-Setup-10.0.exe` | Windows installer (recommended) |
| `TamiyaRaceManager-WindowsPortable-10.0.zip` | Windows portable |
| `TamiyaRaceManager-Mac-10.0.zip` | Mac / OSX (untested) |
