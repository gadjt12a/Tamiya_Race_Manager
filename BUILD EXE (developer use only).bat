@echo off
title Tamiya Race Manager - Build EXE
REM ═══════════════════════════════════════════════════════════════
REM  Builds dist\TamiyaRaceManager.exe - a single-file DESKTOP app
REM  (native window via pywebview, no console, no browser tab)
REM  bundling the server, the HTML app and the VERSION file.
REM  Requires:  python -m pip install pyinstaller pywebview
REM  Version comes from the VERSION file (single source of truth).
REM  Place icon.ico next to this script to embed the app icon.
REM ═══════════════════════════════════════════════════════════════
setlocal
cd /d "%~dp0"
set /p APPVERSION=<VERSION
echo.
echo  Building Tamiya Race Manager v%APPVERSION% ...
echo.

set ICONFLAG=
if exist "icon.ico" set ICONFLAG=--icon "icon.ico"

python -m PyInstaller --noconfirm --clean --onefile --noconsole ^
  --name TamiyaRaceManager ^
  --add-data "race-manager.html;." ^
  --add-data "VERSION;." ^
  --collect-all webview ^
  %ICONFLAG% ^
  app.py

if not exist "dist\TamiyaRaceManager.exe" (
    echo.
    echo  BUILD FAILED - see errors above.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Build complete: dist\TamiyaRaceManager.exe  (v%APPVERSION%)
echo  ==========================================
echo.
pause
