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
the same app in a zip — unzip the **whole** folder anywhere (USB fine), open
the `TamiyaRaceManager` folder and run the exe.

⚠ Two things to know about the portable version: extract the zip properly
first (don't run the app from inside Windows' zip preview), and keep
`TamiyaRaceManager.exe` together with the `_internal` folder next to it — the
app won't start if the exe is moved out on its own. Want it on the desktop?
Right-click the exe → **Show more options** → **Send to** → **Desktop
(create shortcut)**.

### Bringing your data across from the old zip version (one time)

Your old data is untouched in the old race-manager folder. In the new app:
**⬇ Import Data** (top right) → choose **`data\racedata.json`** inside your
old race-manager folder → done. Seasons, racers and points all come across.
(The app shows this hint on first run too.)

⚠ If your old version ran **without Python** (it warned about "browser
storage mode"): open the OLD version first, click **Export Data**, and import
that file instead — there is no data file on disk in that mode.

## Installing (Mac / OSX)

**`TamiyaRaceManager-Mac-10.0.zip`** — unzip it and drag
**TamiyaRaceManager** to your Applications folder (or anywhere you like).
Everything is included; you do **not** need to install Python.

### ⚠ First launch on a Mac — please read

The app is not registered with Apple (that costs an annual fee we don't pay
for a free club app), so macOS will not open it on the first attempt. **This
is expected and the app is fine.**

Depending on your macOS version you'll see one of:

- *"TamiyaRaceManager can't be opened because it is from an unidentified
  developer"*
- *"Apple could not verify TamiyaRaceManager is free of malware"*
- **"TamiyaRaceManager is damaged and can't be opened. You should move it to
  the Bin."** — ⚠ **This message is wrong.** The app is not damaged. macOS
  says this about any unregistered app you've downloaded. Do **not** delete
  it.

**To open it (one time only):**

1. **Right-click** (or Control-click) the app → choose **Open**
2. The warning appears again, now with an **Open** button → click **Open**

That's it. From then on it opens normally with a double-click. You only have
to do this once per Mac.

If right-click → Open doesn't offer an **Open** button, go to  **System
Settings → Privacy & Security**, scroll down, and click **Open Anyway** next
to the message about TamiyaRaceManager.

### What we've tested

Tested on **macOS 10.13 (High Sierra) on an Intel Mac** — a full race night,
the second-screen display, exports, printing, and data storage all working.

Two honest caveats:

- **Apple Silicon (M1/M2/M3…) is untested.** The app is an Intel build, so it
  runs through Rosetta 2. macOS will offer to install Rosetta the first time
  if you don't have it — accept, and the app should run normally. We have no
  Apple Silicon Mac to confirm this on.
- **Newer macOS versions are untested.** We build and test on an older Mac.

Please tell us how you get on either way — Mac feedback is genuinely useful
to us.

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

### Getting around
- **Full Screen button** on the Home and Race screens (or press **F11**) —
  handy for putting the race screen up on the big monitor.
- The window now opens **centred on your screen**, sized to fit it, instead
  of drifting down and to the right.
- The app **starts in about half a second**.
- The home screen keeps its layout when you resize the window.

### Seasons
- Closing a season now **warns you properly first** — it names the season,
  says how many events it has, and spells out what closing does.
- **Closed a season by mistake?** "View All Seasons" now has a **Reopen**
  button that makes it the active season again. Nothing is deleted when a
  season is closed. (Only one season can be active, so close the current one
  first.)

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
- The **📺 Display** button is now on the **home screen** too, so you can get
  the projector set up while racers are still registering, rather than having
  to start setting up the first race first. It shows "Waiting for racing to
  start…" until the first race begins, and if the display window ends up
  behind the main window, pressing Display again brings it back to the front.
- Fixed: after finishing and saving a race, closing and reopening the app
  wrongly offered to resume that already-saved race. Nothing was ever lost or
  duplicated.

### Mac
- **The Mac version is now a proper Mac app** — no Python to install, opens in
  its own window like the Windows version. See the install notes above.

---

## Notes & known limitations

- **Downgrading is not supported.** A v10 data file will not load in v9.x.
  To roll back, reinstall v9.27 (kept downloadable) and restore from
  `%LOCALAPPDATA%\TamiyaRaceManager\backups\` or a pre-update export.
- **WebView2**: the desktop window uses Microsoft Edge WebView2 (built into
  Windows 11 / current Windows 10). If missing, the app opens in your
  browser instead — everything still works.
- The exe is **not code-signed** (cost) — hence the one-time SmartScreen
  prompt above. The Mac app is likewise not registered with Apple, hence its
  one-time right-click → Open. Both are annual fees we don't think are worth
  it for a free club app; if that ever changes, the warnings go away.
- **Mac: Apple Silicon and newer macOS are untested.** Tested on macOS 10.13
  Intel. See the Mac install section above.

## Files in this release

| File | Platform |
|---|---|
| `TamiyaRaceManager-Setup-10.0.exe` | Windows installer (recommended) |
| `TamiyaRaceManager-WindowsPortable-10.0.zip` | Windows portable |
| `TamiyaRaceManager-Mac-10.0.zip` | Mac / OSX |

Downloads carry a build number after the version, e.g.
`TamiyaRaceManager-Setup-10.0.25.exe`. It goes up every time the app
changes, so if you're ever unsure which download a club laptop is running,
the number in the app's title bar tells you.
