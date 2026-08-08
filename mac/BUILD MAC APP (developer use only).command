#!/bin/bash
#
# Tamiya Race Manager - build the native macOS app bundle.
#
# RUN THIS ON A MAC. PyInstaller cannot cross-compile: a macOS .app can
# only be built on macOS. (The Windows packages, and the older Python-zip
# Mac package, are built on Windows - see BUILD.md.)
#
# Output:  dist/TamiyaRaceManager.app
#          dist/TamiyaRaceManager-Mac-<ver>.<build>.zip
#
# Requires: Python 3, then  python3 -m pip install pyinstaller pywebview
#
# Which Python? By default it looks for a working one, newest-known-good
# first, because "python3" on a Mac is whatever was installed last and
# that is not always the one with the build tools in it. Override with:
#
#     ./BUILD\ MAC\ APP...command python3.13
#     PY=/full/path/to/python3 ./BUILD\ MAC\ APP...command
#
set -u
cd "$(dirname "$0")/.."

echo ""
echo "  =========================================="
echo "   TAMIYA RACE MANAGER - build macOS app"
echo "  =========================================="
echo ""

# ── Python ────────────────────────────────────────────────────
# A broken or half-installed interpreter can CRASH rather than error
# (a bad pyobjc has been seen taking python down at startup), so every
# candidate is tested by actually running it before it's chosen.
usable() {
    command -v "$1" &>/dev/null && "$1" -c "print(1)" &>/dev/null
}

PY="${1:-${PY:-}}"
if [ -n "$PY" ]; then
    if ! usable "$PY"; then
        echo "  ERROR: '$PY' is not a working Python 3."
        echo "  It is missing, or it crashes on start-up."
        read -r -p "  Press Enter to close..."
        exit 1
    fi
else
    for cand in python3.13 python3.12 python3.11 python3; do
        if usable "$cand"; then PY="$cand"; break; fi
    done
    if [ -z "$PY" ]; then
        echo "  ERROR: no working Python 3 found."
        echo "  Install one from https://www.python.org/downloads/ and try again."
        echo "  (If 'python3' exists but crashes, that install is broken -"
        echo "   install another version and pass it: $0 python3.13)"
        read -r -p "  Press Enter to close..."
        exit 1
    fi
fi
echo "  Python: $("$PY" --version)  [$(command -v "$PY")]"

for mod in PyInstaller webview; do
    if ! "$PY" -c "import $mod" &>/dev/null; then
        echo ""
        echo "  ERROR: Python module '$mod' is missing from $PY. Install both with:"
        echo "      $PY -m pip install pyinstaller pywebview"
        read -r -p "  Press Enter to close..."
        exit 1
    fi
done

# ── Version + build number ────────────────────────────────────
APPVERSION=$(tr -d '[:space:]' < app/VERSION)

# Build number = commit count, same rule as the Windows build, so a Mac
# app and a Windows installer from the same commit share a number.
BUILDNO=0
if command -v git &>/dev/null && git rev-parse --git-dir &>/dev/null 2>&1; then
    BUILDNO=$(git rev-list --count HEAD 2>/dev/null || echo 0)
fi
echo "$BUILDNO" > app/BUILD
echo "  Building v${APPVERSION}.${BUILDNO} ..."
echo ""

# ── Icon (optional) ───────────────────────────────────────────
# macOS needs .icns; app/icon.ico is Windows-only. If icon.icns isn't
# there we build without one rather than failing - see BUILD.md for how
# to generate it from a PNG with sips + iconutil.
ICONFLAG=()
if [ -f "app/icon.icns" ]; then
    ICONFLAG=(--icon "app/icon.icns")
    echo "  Using app/icon.icns"
else
    echo "  NOTE: app/icon.icns not found - building with the default icon."
fi

# ── Build ─────────────────────────────────────────────────────
# --windowed produces the .app bundle. Note --add-data uses a COLON
# separator on macOS, where Windows uses a semicolon.
"$PY" -m PyInstaller --noconfirm --clean --windowed \
    --name TamiyaRaceManager \
    --add-data "app/race-manager.html:." \
    --add-data "app/VERSION:." \
    --add-data "app/BUILD:." \
    --collect-all webview \
    "${ICONFLAG[@]}" \
    app/app.py

if [ ! -d "dist/TamiyaRaceManager.app" ]; then
    echo ""
    echo "  BUILD FAILED - see the errors above."
    read -r -p "  Press Enter to close..."
    exit 1
fi

# ── Zip it ────────────────────────────────────────────────────
# ditto, not zip: it preserves the execute bits and macOS metadata
# inside the .app bundle. A plain zip can produce an app that won't
# launch after being unzipped.
ZIP="dist/TamiyaRaceManager-Mac-${APPVERSION}.${BUILDNO}.zip"
rm -f "$ZIP"
ditto -c -k --sequesterRsrc --keepParent "dist/TamiyaRaceManager.app" "$ZIP"

echo ""
echo "  =========================================="
echo "   Done:"
echo "    dist/TamiyaRaceManager.app"
echo "    $ZIP"
echo "  =========================================="
echo ""
echo "  The app is UNSIGNED. The first time you open it (and on any Mac"
echo "  it's copied to), right-click the app -> Open -> Open. Double-"
echo "  clicking will be refused by Gatekeeper until you've done that once."
echo ""
read -r -p "  Press Enter to close..."
