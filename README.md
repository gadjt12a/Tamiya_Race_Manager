# Tamiya Race Manager

Race night management for Tamiya Mini 4WD clubs — double-elimination brackets
(Main + 2nd Chance), three classes (Box / EVO / Pro) with EVO Junior standings,
season points, a coordinator screen and a public race display for the second
monitor. Runs entirely offline on one laptop.

**Current version:** see [`app/VERSION`](app/VERSION) · full history in
[`CHANGELOG.txt`](CHANGELOG.txt)

---

## Downloads — pick your platform

### 🪟 Windows (recommended)
| Package | What it is |
|---|---|
| `TamiyaRaceManager-Setup-<ver>.exe` | **Normal installer** — desktop icon, Start Menu, no admin rights needed. Updating = run the newer installer. |
| `TamiyaRaceManager-WindowsPortable-<ver>.zip` | The same app in a zip — nothing installed; run from anywhere, USB included. Extract the **whole folder** and keep `TamiyaRaceManager.exe` together with the `_internal` folder beside it. |

The app runs in its own window (no console, no browser tab). Full details:
[`windows/README.txt`](windows/README.txt)

### 🍎 Mac / OSX (**lightly tested** — we develop on Windows)
| Package | What it is |
|---|---|
| `TamiyaRaceManager-Mac-<ver>.zip` | `TamiyaRaceManager.app` — a real Mac app. No Python to install; runs in its own window like the Windows version. |

Run successfully on **one** Mac (macOS 10.13 High Sierra, Intel) by the
developer on 2026-08-08, never yet at a real race night. Newer macOS versions
and Apple Silicon are untested; the app is Intel-only and runs under Rosetta 2
on M-series Macs. It is **not notarized**, so macOS blocks the first launch and
may falsely claim it "is damaged" — right-click → **Open** → **Open**.

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
- **Mac app:** run `mac/BUILD MAC APP (developer use only).command` **on a Mac**
  — PyInstaller cannot cross-compile, so the `.app` can only be built on macOS
  (and only for the architecture of the machine that builds it).
- **Mac Python-zip (legacy fallback):** `mac\BUILD MAC PACKAGE (developer use only).bat`
  builds the older launcher-plus-source package on Windows for Macs where the
  `.app` won't run. Both write to the same filename — see `BUILD.md`.

Outputs land in `dist\` and are named `<version>.<build>` — the version from
`app/VERSION` (bumped by hand) and the build number from
`git rev-list --count HEAD`, so it identifies the commit rather than the
machine that built it. See [`BUILD.md`](BUILD.md).

See [`DEPLOYMENT_PLAN.md`](DEPLOYMENT_PLAN.md) for the v10 release plan, test
matrix and data-safety design, and [`HOW TO USE.txt`](HOW%20TO%20USE.txt) for
the race-night manual.
