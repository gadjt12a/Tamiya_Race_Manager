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
set -u
cd "$(dirname "$0")/.."

echo ""
echo "  =========================================="
echo "   TAMIYA RACE MANAGER - build macOS app"
echo "  =========================================="
echo ""

# ── Python ────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "  ERROR: python3 not found."
    echo "  Install it from https://www.python.org/downloads/ and try again."
    read -r -p "  Press Enter to close..."
    exit 1
fi
echo "  Python: $(python3 --version)"

for mod in PyInstaller webview; do
    if ! python3 -c "import $mod" &>/dev/null; then
        echo ""
        echo "  ERROR: Python module '$mod' is missing. Install both with:"
        echo "      python3 -m pip install pyinstaller pywebview"
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
python3 -m PyInstaller --noconfirm --clean --windowed \
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
