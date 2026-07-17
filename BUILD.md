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
4. Clone the repo:
   ```
   git clone https://github.com/gadjt12a/Tamiya_Race_Manager
   ```

## Releasing a new version

1. Update `app/VERSION` (single source of truth — it drives the app header,
   server console, installer name and file version everywhere).
2. Add a `CHANGELOG.txt` entry at the top, and update the header version in
   `HOW TO USE.txt`.
3. Build the packages (below), smoke-test, commit, tag.

## Build the Windows packages

Run **`windows\BUILD INSTALLER (developer use only).bat`** (double-click).
It builds, in order:

| Output | What it is |
|---|---|
| `dist\TamiyaRaceManager.exe` | the app itself (intermediate) |
| `dist\installer\TamiyaRaceManager-Setup-<ver>.exe` | the Windows installer |
| `dist\TamiyaRaceManager-WindowsPortable-<ver>.zip` | portable zip (exe + README) |

`windows\BUILD EXE (developer use only).bat` builds just the exe when you're
iterating and don't need the installer.

## Build the Mac package

Run **`mac\BUILD MAC PACKAGE (developer use only).bat`**. Output:
`dist\TamiyaRaceManager-Mac-<ver>.zip` (launcher + `app/` + Mac README).
No Mac is needed to *build* it — but it should be *tested* on one
(currently untested; the Mac README says so).

## Smoke test before publishing

1. Run `dist\TamiyaRaceManager.exe` — app opens in its own window, version
   in the top-left matches `app/VERSION`.
2. Run the installer normally (not silent) — read the data-safety info page,
   finish, launch from the desktop icon.
3. Open the Display window; run a quick 3-racer test race (Test mode —
   nothing is recorded).
4. Close the window — confirm the process exits (no orphaned
   TamiyaRaceManager.exe in Task Manager).

## Gotchas

- **Keep the `.bat` files ASCII-only.** `cmd.exe` reads them in the ANSI
  codepage; fancy Unicode characters get mangled and can execute as garbage.
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
