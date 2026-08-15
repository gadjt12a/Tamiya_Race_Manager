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
Run successfully on a Mac on 2026-08-08 (macOS 10.13.6, Intel).

**This is now the fallback, not the main Mac download.** The native `.app`
(below) is what clubs should get; this package is for Macs the `.app` won't
run on. **Both scripts write the same filename** —
`dist\TamiyaRaceManager-Mac-<ver>.<build>.zip` — so from the same commit
whichever runs second overwrites the first. Rename or move one before
publishing, and check what's actually inside the zip you upload.

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

Closing the browser tab shuts the server down via the watchdog — the
browser-mode-only fallback for a tab close being otherwise undetectable.
**The desktop app deliberately runs no watchdog**: closing the window is
the exit route, and the heartbeat could tell it nothing the window does
not. See the gotcha below before reinstating one.

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

**On macOS 10.13/10.14, pin `pywebview==4.4.1`.** pywebview 5+ opens a
window that never renders anything on High Sierra — no error, no console
output, just a blank view. It looks exactly like a packaging bug and is
not one: a one-line pywebview script displaying a plain HTML string is
blank on 6.2.1 and renders correctly on 4.4.1, with no server, bundle or
ATS involved. The build script warns if it sees this combination.

```
python3.13 -m pip install "pywebview==4.4.1"
```

Newer pywebview is the right choice on newer macOS — this pin is only for
the older releases.

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

## Checking the race logic — `stress-test.py`

A developer tool in the repo root, worth running after any change to the
bracket engine, points schemes or roster handling. It simulates 30 race
nights (Box + EVO + Pro each) and validates the results:

```
python stress-test.py [runs]     # default 3 runs
```

It checks bracket correctness for every racer count 3–21, junior points
ranking, double/triple-night multipliers, auto-save upsert (re-saving an
event must not duplicate it), roster active/inactive flags, multi-season
roster continuity, and that the points schemes match `race-manager.html`
exactly. It prints `ALL TESTS PASSED` and an error count.

*Last run 2026-08-15: 90 events, 0 errors.*

**It re-implements the bracket rules rather than importing them**, so it
can drift from the app — change a rule in `app/race-manager.html` and you
must change it here too, or this will keep passing while the app is wrong.

Scratch output goes to `data/stress-test-output.json` (gitignored), which
the app never reads. It used to be written to `data/racedata.json` — the
same name the v10 migration leaves behind as the backup of a club's
pre-v10 data — and on 2026-08-15 a stress-test run duly overwrote one.
Nothing live was affected, but don't point scratch output at a real data
filename.

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

- **Never make a heartbeat responsible for keeping the app alive.**
  Browsers and WebViews throttle timers in unfocused or background
  windows — a `setInterval` asking for every 5 s can be slowed to roughly
  once a minute. The watchdog's 12 s timeout therefore shut the app down
  when it was simply left open and untouched between races, which on race
  night is the worst possible failure. The desktop app no longer runs the
  watchdog at all; browser mode does, at `HEARTBEAT_TIMEOUT = 180`. The
  cost of a generous timeout is a server lingering after a tab closes,
  which nobody notices; the cost of a tight one is losing the app
  mid-event.
- **Old WebKit does not size a flex container from its items.** A row of
  flex children collapses to less than its contents, and because `.panel`
  and `.season-hero` set `overflow:hidden` (for their rounded corners and
  the decorative flag), the overflowing content is silently *cut off*
  rather than pushed out. Hit twice: the ×2/×3 multiplier buttons and the
  season hero's action buttons, both sliced in half on macOS 10.13.
  `min-height` on the *children* does nothing — the container never
  consults them. Fix at the **container**: give it a `min-height`, or set
  `overflow:visible` on that specific element. If a panel's contents look
  trimmed on an old Mac, this is why.
- **Keep `race-manager.html`'s JavaScript at ES2019.** No optional chaining
  (`?.`), no nullish coalescing (`??`), no logical assignment. The macOS
  app renders through the system WebView, which on macOS 10.13 predates
  ES2020 — and because the app is one big `<script>` block, a single
  unsupported token is a *parse* error that kills the entire app: no
  content, every button dead, blank page. This is not hypothetical; it
  happened, and `?.` had to be removed from 38 places.

  **Test in the app's WebView, not in Safari.** Safari gets updated
  separately and is several years ahead of the WebView on the same
  machine — a feature test that passes in Safari proves nothing about the
  bundled app. That mistake sent this investigation the wrong way twice.

  To check before shipping, if node is available:
  ```
  npx acorn --ecma2019 <the script block>   # must parse clean
  ```
  Failing that, the app now paints a red error panel at the bottom of the
  window on any JS error, which is how this was finally caught.
- **Keep the `.bat` files ASCII-only.** `cmd.exe` reads them in the ANSI
  codepage; fancy Unicode characters get mangled and can execute as garbage.
- **The macOS `.app` needs an App Transport Security exception, or it opens
  a black window.** The UI is served over `http://127.0.0.1:8765`, and
  WKWebView refuses plain `http` by default — silently, no error, just a
  blank view. PyInstaller's generated `Info.plist` has no exception, so the
  build script adds one with `PlistBuddy` and re-signs the bundle
  afterwards (editing a bundle invalidates its signature).

  **The obvious keys are the wrong ones**, which cost a long debugging
  session: `NSAllowsLocalNetworking` does *not* cover loopback — it covers
  `*.local`, unqualified hostnames and link-local `169.254/16` — and its
  mere presence makes macOS **ignore** `NSAllowsArbitraryLoads`. Setting
  both therefore blocks `127.0.0.1` while appearing to allow everything.
  What works is `NSAllowsArbitraryLoadsInWebContent` plus an explicit
  `NSExceptionDomains` entry for `127.0.0.1`.

  None of this affects the Python-zip package, which runs in a real
  browser. **Safari is exempt from ATS too**, so "it loads fine in Safari"
  does not mean the bundled app will — that difference is the giveaway.
- **The `.command` scripts must stay bash 3.2 compatible.** macOS still
  ships bash 3.2 (2007 — it's a licensing thing), so anything you test in a
  modern bash may still fail there. The one that bit us: expanding an
  *empty* array under `set -u` raises "unbound variable" in bash < 4.4 but
  is fine in 4.4+. Build optional arguments into the positional parameters
  with `set -- "$@" …` instead, which is safe when empty in every version.
- **Anything authored on Windows for the Mac needs three checks**, none of
  which are visible until it runs on macOS: LF line endings (`.gitattributes`
  handles it), the executable bit (`git update-index --chmod=+x`), and
  forward-slash paths inside any zip (build with `tar`/`ditto`, not
  `Compress-Archive`). All three have broken the Mac package before.
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
