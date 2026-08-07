@echo off
title Tamiya Race Manager - Build Windows Packages
REM ===============================================================
REM  Builds BOTH Windows packages into dist\:
REM    1. dist\installer\TamiyaRaceManager-Setup-<ver>.exe  (installer)
REM    2. dist\TamiyaRaceManager-WindowsPortable-<ver>.zip  (portable)
REM  Requires:  python -m pip install pyinstaller pywebview
REM             Inno Setup 6 (winget install JRSoftware.InnoSetup)
REM  Version comes from app\VERSION.
REM ===============================================================
setlocal
cd /d "%~dp0.."
set /p APPVERSION=<app\VERSION

echo.
echo  [1/3] Building TamiyaRaceManager.exe v%APPVERSION% ...
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
    echo  EXE BUILD FAILED - see errors above.
    pause
    exit /b 1
)

echo.
echo  [2/3] Building installer ...
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

%ISCC% /Q "windows\TamiyaRaceManager.iss"
if errorlevel 1 (
    echo  INSTALLER BUILD FAILED - see errors above.
    pause
    exit /b 1
)

echo.
echo  [3/3] Building portable zip ...
REM  Zips the WHOLE TamiyaRaceManager folder - the exe needs _internal\
REM  beside it. Users must extract the zip before running (not run it
REM  from inside the zip viewer).
powershell -Command "Compress-Archive -Force -Path 'dist\TamiyaRaceManager','windows\README.txt' -DestinationPath 'dist\TamiyaRaceManager-WindowsPortable-%APPVERSION%.zip'"

echo.
echo  ==========================================
echo   Done:
echo    dist\installer\TamiyaRaceManager-Setup-%APPVERSION%.exe
echo    dist\TamiyaRaceManager-WindowsPortable-%APPVERSION%.zip
echo  ==========================================
echo.
pause
