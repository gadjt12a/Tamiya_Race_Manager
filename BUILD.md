# Building Tamiya Race Manager from source

How to produce all three release packages from a clean checkout.
Everything builds on a Windows machine (including the Mac package).

## One-time setup

1. **Windows 10/11** with [Python 3.11+](https://www.python.org/downloads/)
   on PATH (`python --version` to check).
2. Python build tools:
   ```
   python -m pip install pyinstaller pywebview
   ```
3. **Inno Setup 6** (for the Windows installer):
   ```
   winget install JRSoftware.InnoSetup
   ```
   (Per-user install is fine; the build script finds it in
   `%LOCALAPPDATA%\Programs\Inno Setup 6` or Program Files.)
4. **Git** — Windows does *not* ship with it, so `git clone` fails on a fresh
   PC with "'git' is not recognized". Check with `git --version`; if it's
   missing, install it:
   ```
   winget install --id Git.Git -e
   ```
   Then **close and reopen the terminal** (the installer adds Git to PATH, and
   existing windows don't pick that up).
5. Get the source (see next section).

## Getting the source

### With Git (recommended — lets you pull updates and switch branches)

Clone, then check out the branch you actually want. `git clone` on its own
gives you `main` only:

```
git clone https://github.com/gadjt12a/Tamiya_Race_Manager
cd Tamiya_Race_Manager
git checkout v10-packaging
```

Or do it in one step:

```
git clone -b v10-packaging https://github.com/gadjt12a/Tamiya_Race_Manager
```

Branches in use:

| Branch | What it is |
|---|---|
| `main` | stable released v9.x |
| `v10-packaging` | v10 installer/packaging work — **build test deployments from here** |

Already cloned and on the wrong branch? Fetch and switch:

```
git fetch origin
git checkout v10-packaging
git pull
```

### Without Git (one-off test deployment)

You don't need Git at all to build once — download a branch as a zip:

1. Go to
   `https://github.com/gadjt12a/Tamiya_Race_Manager/tree/v10-packaging`
2. Green **Code** button → **Download ZIP** (this downloads the branch you're
   viewing, not `main` — check the branch selector first).
3. Right-click the zip → **Properties** → tick **Unblock** → OK, then extract.
   Windows marks downloaded zips as blocked, and the `.bat` files may refuse
   to run otherwise.

Or from PowerShell, no browser needed:

```powershell
$b = "v10-packaging"
Invoke-WebRequest "https://github.com/gadjt12a/Tamiya_Race_Manager/archive/refs/heads/$b.zip" -OutFile "$env:TEMP\trm.zip"
Expand-Archive "$env:TEMP\trm.zip" -DestinationPath "$HOME\Downloads" -Force
```

That gives you `Tamiya_Race_Manager-v10-packaging\`. The zip has no `.git`
folder, so you can't pull updates or commit from it — re-download for a newer
build, or use the Git route instead.

## Version and build numbers

Packages are named `<version>.<build>`, e.g. `9.39.21`:

- **version** — `app/VERSION`, bumped by hand when you decide to release
  something. Single source of truth for the app header, server console,
  installer name and file version.
- **build** — generated at build time from `git rev-list --count HEAD`, the
  number of commits on the branch. It ticks up with **every commit**, so it
  identifies the *source*, not the machine: two people building the same
  commit produce the same number, and two different commits can never be
  confused for each other. The build scripts write it to `app/BUILD`, which
  is gitignored (committing it would change the count it comes from).

Building without git available — a source-zip download, say — gives build
`0`. That still works; you just lose the ability to tell builds apart.

The full number shows in the app header, `app.log`, the installer filename
and the exe's Properties → Details.

## Releasing a new version

1. Update `app/VERSION` (the build number looks after itself).
2. Add a `CHANGELOG.txt` entry at the top, and update the header version in
   `HOW TO USE.txt`.
3. Build the packages (below), smoke-test, commit, tag.

## Build the Windows packages

Run **`windows\BUILD INSTALLER (developer use only).bat`** (double-click).
It builds, in order:

| Output | What it is |
|---|---|
| `dist\TamiyaRaceManager\` | the app itself — exe + `_internal\` (intermediate) |
| `dist\installer\TamiyaRaceManager-Setup-<ver>.exe` | the Windows installer |
| `dist\TamiyaRaceManager-WindowsPortable-<ver>.zip` | portable zip (app folder + README) |

`windows\BUILD EXE (developer use only).bat` builds just the app folder when
you're iterating and don't need the installer.

**This is a PyInstaller *onedir* build** (since v9.39). `TamiyaRaceManager.exe`
only runs with its `_internal\` folder beside it — never ship or copy the exe
on its own. The installer handles this; for the portable zip, users must
extract the whole folder before running.

## Build the Mac package

Run **`mac\BUILD MAC PACKAGE (developer use only).bat`**. Output:
`dist\TamiyaRaceManager-Mac-<ver>.zip` (launcher + `app/` + Mac README).
No Mac is needed to *build* it — but it should be *tested* on one
(currently untested; the Mac README says so).

## Smoke test before publishing

1. Run `dist\TamiyaRaceManager\TamiyaRaceManager.exe` — app opens in its own
   window, version in the top-left matches `app/VERSION`.
2. Run the installer normally (not silent) — read the data-safety info page,
   finish, launch from the desktop icon.
3. Open the Display window; run a quick 3-racer test race (Test mode —
   nothing is recorded).
4. Close the window — confirm the process exits (no orphaned
   TamiyaRaceManager.exe in Task Manager).

## Gotchas

- **Keep the `.bat` files ASCII-only.** `cmd.exe` reads them in the ANSI
  codepage; fancy Unicode characters get mangled and can execute as garbage.
- **The loading screen is `LOADING_HTML` in `app/app.py`**, shown in the real
  window before the server starts, then swapped for the app by `boot()`.
  Note `webview.start(boot, main_win)` passes the window *into* the callback,
  so `boot` must accept that argument.
- **Don't add `--splash`.** It was tried in v9.38 and removed in v9.39.
  PyInstaller's splash is Tcl/Tk, which pulls `tcl86t.dll`, `tk86t.dll` and
  the `_tcl_data`/`_tk_data` trees into an app that otherwise has no Tk at
  all. On a test PC it produced a stack of "Failed to load Tcl DLL" and
  "File already exists but should not" dialogs before the app would start.
  Onedir launches fast enough that no splash is needed.
- **The exe is unsigned**, so SmartScreen warns on first run of a fresh
  download ("More info" → "Run anyway"). Code signing is a future option
  (~US$100+/yr).
- **WebView2 runtime**: the desktop window needs Microsoft Edge WebView2,
  preinstalled on Windows 11 and current Windows 10. If it's missing, the app
  falls back to browser mode automatically.
- The icon is `app/icon.ico` (multi-size). To change it: replace the file and
  rebuild. Regenerate from a square-ish source image with Pillow:
  ```python
  from PIL import Image
  img = Image.open("source.png").convert("RGBA").resize((256, 256))
  img.save("app/icon.ico", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
  ```
- Build artefacts (`build/`, `dist/`, `*.spec`) and live data (`data/`) are
  gitignored — never commit them.
