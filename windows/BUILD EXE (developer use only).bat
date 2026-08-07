@echo off
title Tamiya Race Manager - Build EXE
REM ===============================================================
REM  Builds dist\TamiyaRaceManager\TamiyaRaceManager.exe - a DESKTOP app
REM  (native window via pywebview, no console, no browser tab)
REM  bundling the server, the HTML app and the VERSION file.
REM  ONEDIR build: the exe sits beside an _internal\ folder. Do NOT ship
REM  the exe on its own - it needs that folder next to it.
REM  Requires:  python -m pip install pyinstaller pywebview
REM  Version comes from app\VERSION (single source of truth).
REM ===============================================================
setlocal
cd /d "%~dp0.."
set /p APPVERSION=<app\VERSION

REM  Build number = commit count (git rev-list --count HEAD) - identifies
REM  the source commit, not this machine. 0 when git isn't available.
set BUILDNO=0
for /f "delims=" %%i in ('git rev-list --count HEAD 2^>nul') do set BUILDNO=%%i
> app\BUILD echo %BUILDNO%

echo.
echo  Building Tamiya Race Manager v%APPVERSION%.%BUILDNO% ...
echo.

set ICONFLAG=
if exist "app\icon.ico" set ICONFLAG=--icon "app\icon.ico"

python -m PyInstaller --noconfirm --clean --onedir --noconsole ^
  --name TamiyaRaceManager ^
  --add-data "app\race-manager.html;." ^
  --add-data "app\VERSION;." ^
  --add-data "app\BUILD;." ^
  --collect-all webview ^
  %ICONFLAG% ^
  app\app.py

if not exist "dist\TamiyaRaceManager\TamiyaRaceManager.exe" (
    echo.
    echo  BUILD FAILED - see errors above.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Build complete: dist\TamiyaRaceManager\  (v%APPVERSION%.%BUILDNO%)
echo   Run it with:    dist\TamiyaRaceManager\TamiyaRaceManager.exe
echo  ==========================================
echo.
pause
