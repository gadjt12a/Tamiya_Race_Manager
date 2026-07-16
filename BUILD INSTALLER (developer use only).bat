@echo off
title Tamiya Race Manager - Build Installer
REM ═══════════════════════════════════════════════════════════════
REM  Builds the exe (PyInstaller) then the Windows installer
REM  (Inno Setup) into dist\installer\.
REM  Requires:  python -m pip install pyinstaller
REM             Inno Setup 6 (winget install JRSoftware.InnoSetup)
REM  Version comes from the VERSION file.
REM ═══════════════════════════════════════════════════════════════
setlocal
cd /d "%~dp0"
set /p APPVERSION=<VERSION

echo.
echo  [1/2] Building TamiyaRaceManager.exe v%APPVERSION% ...
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
    echo  EXE BUILD FAILED - see errors above.
    pause
    exit /b 1
)

echo.
echo  [2/2] Building installer ...
echo.

set ISCC="%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo  ERROR: Inno Setup 6 not found.
    echo  Install it with:  winget install JRSoftware.InnoSetup
    pause
    exit /b 1
)

%ISCC% /Q TamiyaRaceManager.iss
if errorlevel 1 (
    echo  INSTALLER BUILD FAILED - see errors above.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Done: dist\installer\TamiyaRaceManager-Setup-%APPVERSION%.exe
echo  ==========================================
echo.
pause
