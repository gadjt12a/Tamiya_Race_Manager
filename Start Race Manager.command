#!/bin/bash

# Tamiya Race Manager — Mac Launcher
cd "$(dirname "$0")"

echo ""
echo "  =========================================="
echo "   TAMIYA RACE MANAGER"
echo "  =========================================="
echo ""

# ── Try Python 3 (standard on modern Macs) ───────────────────
if command -v python3 &>/dev/null; then
    # Verify it's actually Python 3
    VER=$(python3 --version 2>&1)
    if [[ $VER == Python\ 3* ]]; then
        echo "  Starting Race Manager..."
        echo "  [Closes automatically when you close the browser tab]"
        echo ""
        python3 server.py
        exit 0
    fi
fi

# ── Try python alias ──────────────────────────────────────────
if command -v python &>/dev/null; then
    VER=$(python --version 2>&1)
    if [[ $VER == Python\ 3* ]]; then
        echo "  Starting Race Manager..."
        python server.py
        exit 0
    fi
fi

# ── No Python 3 found ─────────────────────────────────────────
echo "  Python 3 is not installed on this Mac."
echo ""
echo "  EASY FIX — choose one of these options:"
echo ""
echo "  Option 1 (Recommended):"
echo "    1. Go to https://www.python.org/downloads/"
echo "    2. Click 'Download Python 3.x.x'"
echo "    3. Run the installer"
echo "    4. Double-click this file again"
echo ""
echo "  Option 2 (If you have Homebrew):"
echo "    Open Terminal and run: brew install python3"
echo "    Then double-click this file again"
echo ""
echo "  Option 3 (Xcode Command Line Tools):"
echo "    Open Terminal and run: xcode-select --install"
echo "    Then double-click this file again"
echo ""
read -p "  Press Enter to close..."
