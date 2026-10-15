# Tamiya Race Manager

Race night management for Tamiya Mini 4WD clubs — double-elimination brackets
(Main + 2nd Chance), three classes (Box / EVO / Pro) with EVO Junior standings,
season points, a coordinator screen and a public race display for the second
monitor. Runs entirely offline on one laptop.

**Current version:** see [`app/VERSION`](app/VERSION) · full history in
[`CHANGELOG.txt`](CHANGELOG.txt)

---

## Downloads — pick your platform

**➡ [Get the latest release](https://github.com/gadjt12a/Tamiya_Race_Manager/releases/latest)**
— everything below is on that page.

### 🪟 Windows (recommended)
| Package | What it is |
|---|---|
| `TamiyaRaceManager-Setup-<ver>.exe` | **Normal installer** — desktop icon, Start Menu, no admin rights needed. Updating = run the newer installer. |
| `TamiyaRaceManager-WindowsPortable-<ver>.zip` | The same app in a zip — nothing installed; run from anywhere, USB included. Extract the **whole folder** and keep `TamiyaRaceManager.exe` together with the `_internal` folder beside it. |

The app runs in its own window (no console, no browser tab). Full details:
[`windows/README.txt`](windows/README.txt)

### 🍎 Mac

**There is no Mac version. This is a Windows app.**

A Mac `.app` was built and run once on an old Intel Mac in August 2026, but it
was never attached to a release, never used at a race night, and is not
supported. The `mac/` folder keeps those build scripts for reference only.

---

## Your data is safe — by construction

Race data lives **outside the app** (`%LOCALAPPDATA%\TamiyaRaceManager\`), so
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
docs/      the two club guides as PDFs - shipped in the installer and the
           portable zip since v10.5
windows/   Windows packaging: installer script, build bats, Windows README
mac/       old Mac packaging scripts - unsupported, kept for reference
dev/       developer material - build guide, release plan, test matrix,
           design notes, stress test. Not needed to use the app.
```

## Building the packages (developers)

Requirements: Python 3, `pip install pyinstaller pywebview`, and
[Inno Setup 6](https://jrsoftware.org/isinfo.php) (`winget install JRSoftware.InnoSetup`).

- **Windows (installer + portable zip):** run `windows\BUILD INSTALLER (developer use only).bat`
- **Mac:** unsupported. The scripts in `mac/` built an Intel `.app` once in
  August 2026; PyInstaller cannot cross-compile, so one can only be built on a
  Mac. Nothing in `mac/` is part of a release.

Outputs land in `dist\` and are named `<version>.<build>` — the version from
`app/VERSION` (bumped by hand) and the build number from
`git rev-list --count HEAD`, so it identifies the commit rather than the
machine that built it. See [`dev/BUILD.md`](dev/BUILD.md).

## Documentation

**New to the app?** Two short guides ship with it, in the `Guides` folder beside
the installed app and on the Start Menu, and are in
[`docs/`](docs) here:

- **Race Manager — Getting Started** (3 pages) — install it, set up a season,
  run a race night.
- **Race Manager — Backing Up Your Results** (2 pages) — the one click that
  keeps a season safe, and how to go back to an earlier night.

[`HOW TO USE.txt`](HOW%20TO%20USE.txt) is the full race-night reference: every
screen, every option, all the troubleshooting detail.

See [`dev/DEPLOYMENT_PLAN.md`](dev/DEPLOYMENT_PLAN.md) for the v10 release plan,
test matrix and data-safety design.
