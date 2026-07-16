@echo off
title Tamiya Race Manager - Build EXE
REM ═══════════════════════════════════════════════════════════════
REM  Builds dist\TamiyaRaceManager.exe - a single-file app bundling
REM  the server, the HTML app and the VERSION file. Requires:
REM    python -m pip install pyinstaller
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

python -m PyInstaller --noconfirm --clean --onefile ^
  --name TamiyaRaceManager ^
  --add-data "race-manager.html;." ^
  --add-data "VERSION;." ^
  %ICONFLAG% ^
  server.py

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
