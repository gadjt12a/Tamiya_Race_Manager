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
echo.
echo  Building Tamiya Race Manager v%APPVERSION% ...
echo.

set ICONFLAG=
if exist "app\icon.ico" set ICONFLAG=--icon "app\icon.ico"

python -m PyInstaller --noconfirm --clean --onedir --noconsole ^
  --name TamiyaRaceManager ^
  --add-data "app\race-manager.html;." ^
  --add-data "app\VERSION;." ^
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
echo   Build complete: dist\TamiyaRaceManager\  (v%APPVERSION%)
echo   Run it with:    dist\TamiyaRaceManager\TamiyaRaceManager.exe
echo  ==========================================
echo.
pause
