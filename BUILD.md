# Building Tamiya Race Manager from source

How to produce all three release packages from a clean checkout.
All three **build** on a Windows machine, including the Mac package —
it only stages files and zips them, so no Mac is needed to produce it.

Working on the Mac version *itself* is different: you don't build
anything on the Mac, you run the source directly. See
[Working on a Mac](#working-on-a-mac) below.

## One-time setup (Windows)

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

### With Git (recommended — lets you pull updates)

The packaging work merged into `main` on 2026-08-08, so a plain clone is
all you need:

```
git clone https://github.com/gadjt12a/Tamiya_Race_Manager
cd Tamiya_Race_Manager
```

Already have a clone from before the merge? It may still be sitting on the
old `v10-packaging` branch:

```
git checkout main
git pull
```

### Without Git (one-off build)

You don't need Git at all to build once — download the source as a zip:

1. Go to `https://github.com/gadjt12a/Tamiya_Race_Manager`
2. Green **Code** button → **Download ZIP**.
3. Right-click the zip → **Properties** → tick **Unblock** → OK, then extract.
   Windows marks downloaded zips as blocked, and the `.bat` files may refuse
   to run otherwise.

Or from PowerShell, no browser needed:

```powershell
Invoke-WebRequest "https://github.com/gadjt12a/Tamiya_Race_Manager/archive/refs/heads/main.zip" -OutFile "$env:TEMP\trm.zip"
Expand-Archive "$env:TEMP\trm.zip" -DestinationPath "$HOME\Downloads" -Force
```

That gives you `Tamiya_Race_Manager-main\`. The zip has no `.git`
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

Run **`mac\BUILD MAC PACKAGE (developer use only).bat`** (on Windows).
Output: `dist\TamiyaRaceManager-Mac-<ver>.<build>.zip` — the launcher,
`app/` (server, HTML, VERSION, BUILD) and the Mac README.

It only stages files and zips them, so no Mac is needed to *build* it.
It has never been *run* on one — see below.

---

## Working on a Mac

Nothing is compiled for the Mac: it runs `app/server.py` under the Mac's
own Python 3 and opens the app in the default browser. There is no
desktop window (no pywebview/WebView2) and no exe.

### One-time setup (macOS)

1. **Git** — macOS doesn't ship it outright, but the Xcode Command Line
   Tools do. In Terminal:
   ```
   git --version
   ```
   If it's missing, macOS offers to install the tools; or force it with:
   ```
   xcode-select --install
   ```
2. **Python 3** — check with:
   ```
   python3 --version
   ```
   Recent macOS includes it (the Command Line Tools above also provide
   it). Otherwise install from [python.org](https://www.python.org/downloads/),
   or `brew install python3` if you use Homebrew.

   Nothing else is needed — no pip packages. PyInstaller, pywebview and
   Inno Setup are Windows-build-only.

3. **Clone the repo:**
   ```
   git clone https://github.com/gadjt12a/Tamiya_Race_Manager
   cd Tamiya_Race_Manager
   ```

### Running it from the repo

```
./mac/Start\ Race\ Manager.command
```

Or double-click `Start Race Manager.command` in Finder. Two macOS
speed-bumps on first run:

- **"cannot be opened because it is from an unidentified developer"** —
  right-click the file → **Open** → **Open**. One-off per machine.
- **"permission denied"** — the execute bit is missing (a zip built on
  Windows doesn't preserve it):
  ```
  chmod +x "mac/Start Race Manager.command"
  ```

The launcher finds the app in either layout: `app/` beside it (packaged
zip) or `../app/` (repo checkout). It tries `python3` first, then
`python`, and prints install instructions if neither is Python 3.

Closing the browser tab shuts the server down via the watchdog.

### Testing the actual package

To test what a club would download, build the zip on Windows, copy it
across, unzip, `chmod +x` the launcher, and run that — the repo checkout
exercises a different code path (`../app/`) to the packaged one.

### Building the native macOS app (on the Mac)

The Python-zip package above needs the club to install Python 3 first —
stock macOS hasn't shipped a usable `python3` since 12.3, so a Mac user's
first experience is being told to go and install something. The native
`.app` removes that: Python is bundled, same as the Windows exe.

**PyInstaller cannot cross-compile** — a macOS app can only be built on
macOS. That's why this is a separate script from the Windows build.

On the Mac, once you have Python 3 and a clone (see setup above):

```
python3 -m pip install pyinstaller pywebview
./mac/BUILD\ MAC\ APP\ \(developer\ use\ only\).command
```

Or just double-click **`BUILD MAC APP (developer use only).command`** in
Finder (`chmod +x` it first if Finder refuses).

**Use a Python version that has pyobjc wheels — 3.12 or 3.13.** pywebview
talks to Cocoa/WebKit through pyobjc, which ships compiled wheels per
Python version and is slow to publish them for brand-new releases.
Building against a too-new Python was tried on 2026-08-08 with 3.14 and
`pip install pywebview` crashed the interpreter outright ("Python quit
unexpectedly"), after which even `python3 -c "print('ok')"` crashed —
a broken native module can take the interpreter down at start-up rather
than raising an error. None of that is visible on Windows, where
pywebview uses WebView2 and needs no pyobjc at all.

Several Pythons can coexist. The script picks the newest *working* one it
knows about (3.13 → 3.12 → 3.11 → `python3`), testing each by running it,
so a broken install is skipped rather than chosen. To force a specific
one:

```
./mac/BUILD\ MAC\ APP\ \(developer\ use\ only\).command python3.13
PY=/full/path/to/python3 ./mac/BUILD\ MAC\ APP\ \(developer\ use\ only\).command
```

Install the build tools into *that* interpreter, not whatever `python3`
happens to be:

```
python3.13 -m pip install pyinstaller pywebview
python3.13 -c "import webview; print('webview ok')"
```

Output:

| Output | What it is |
|---|---|
| `dist/TamiyaRaceManager.app` | the app bundle |
| `dist/TamiyaRaceManager-Mac-<ver>.<build>.zip` | the shippable zip |

Notes:

- The zip is made with `ditto`, not `zip` — it preserves the execute bits
  and metadata inside the bundle. A plain `zip` can produce an `.app` that
  won't launch once unzipped.
- **The app is unsigned**, so the first launch on any Mac needs
  right-click → **Open** → **Open**. Double-clicking is refused until
  that's been done once. Same trade-off as SmartScreen on Windows.
- `--add-data` uses a **colon** separator on macOS and a **semicolon** on
  Windows. That difference is why the two build scripts can't be shared.
- **Icon:** macOS needs `app/icon.icns`; `app/icon.ico` is Windows-only.
  The script builds without an icon if `.icns` is missing rather than
  failing. To generate one from a square PNG on the Mac:
  ```
  mkdir icon.iconset
  sips -z 16 16   source.png --out icon.iconset/icon_16x16.png
  sips -z 32 32   source.png --out icon.iconset/icon_32x32.png
  sips -z 128 128 source.png --out icon.iconset/icon_128x128.png
  sips -z 256 256 source.png --out icon.iconset/icon_256x256.png
  sips -z 512 512 source.png --out icon.iconset/icon_512x512.png
  iconutil -c icns icon.iconset -o app/icon.icns
  ```
- The app uses pywebview, which on macOS renders through WebKit rather
  than WebView2. Expect rendering differences from Windows, and check the
  second-screen display window in particular.

### Mac data location

`~/Library/Application Support/TamiyaRaceManager/` (`racedata.json` +
`backups/`), outside the app folder, same guarantee as Windows.

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
- **There is no loading screen, and adding one is harder than it looks.**
  The full reasoning and the measured start-up breakdown are in the module
  docstring at the top of `app/app.py` — read that before attempting a
  fourth try.
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
