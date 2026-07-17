# Tamiya Race Manager

Race night management for Tamiya Mini 4WD clubs — double-elimination brackets
(Main + 2nd Chance), three classes (Box / EVO / Pro) with EVO Junior standings,
season points, a coordinator screen and a public race display for the second
monitor. Runs entirely offline on one laptop.

**Current version:** see [`app/VERSION`](app/VERSION) · full history in
[`CHANGELOG.txt`](CHANGELOG.txt)

---

## Downloads — pick your platform

### 🪟 Windows (recommended, fully tested)
| Package | What it is |
|---|---|
| `TamiyaRaceManager-Setup-<ver>.exe` | **Normal installer** — desktop icon, Start Menu, no admin rights needed. Updating = run the newer installer. |
| `TamiyaRaceManager-WindowsPortable-<ver>.zip` | The same app in a zip — nothing installed; run from anywhere, USB included. |

The app runs in its own window (no console, no browser tab). Full details:
[`windows/README.txt`](windows/README.txt)

### 🍎 Mac / OSX (**untested** — we develop on Windows)
| Package | What it is |
|---|---|
| `TamiyaRaceManager-Mac-<ver>.zip` | Launcher + app. Needs Python 3; opens in your browser. |

Please report problems. Details: [`mac/README.txt`](mac/README.txt)

---

## Your data is safe — by construction

Race data lives **outside the app** (`%LOCALAPPDATA%\TamiyaRaceManager\` on
Windows, `~/Library/Application Support/TamiyaRaceManager/` on Mac), so
installing, updating or uninstalling the app can never touch it. The server
keeps automatic daily backups (14 days). If saving ever fails mid-event, a red
banner appears with recovery instructions. **Export Data to a USB stick after
every race night regardless.**

Upgrading from an old zip-style v9.x? Your data stays in the old folder — use
**Import Data** in the new app and pick the old `data\racedata.json`
(one-time step; the app shows a hint on first run).

---

## Repository layout

```
app/       the application: race-manager.html (UI + race engine),
           server.py (data server), app.py (desktop window), VERSION, icon
windows/   Windows packaging: installer script, build bats, Windows README
mac/       Mac packaging: launcher, package build bat, Mac README
```

## Building the packages (developers)

Requirements: Python 3, `pip install pyinstaller pywebview`, and
[Inno Setup 6](https://jrsoftware.org/isinfo.php) (`winget install JRSoftware.InnoSetup`).

- **Windows (installer + portable zip):** run `windows\BUILD INSTALLER (developer use only).bat`
- **Mac package:** run `mac\BUILD MAC PACKAGE (developer use only).bat`

Outputs land in `dist\`. The version everywhere comes from `app/VERSION`.

See [`DEPLOYMENT_PLAN.md`](DEPLOYMENT_PLAN.md) for the v10 release plan, test
matrix and data-safety design, and [`HOW TO USE.txt`](HOW%20TO%20USE.txt) for
the race-night manual.
