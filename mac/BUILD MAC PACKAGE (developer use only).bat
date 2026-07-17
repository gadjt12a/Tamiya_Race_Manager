@echo off
title Tamiya Race Manager - Build Mac Package
REM ===============================================================
REM  Builds dist\TamiyaRaceManager-Mac-<ver>.zip - the Mac (OSX)
REM  package: launcher + app files + Mac README. Runs on Windows
REM  (it only stages files and zips them).
REM  NOTE: Mac users may need "chmod +x" on the .command after
REM  unzipping (zip does not preserve the execute permission when
REM  built on Windows) - covered in the Mac README.
REM ===============================================================
setlocal
cd /d "%~dp0.."
set /p APPVERSION=<app\VERSION

echo.
echo  Building Mac package v%APPVERSION% ...

set STAGE=dist\mac-stage\TamiyaRaceManager
if exist "dist\mac-stage" rmdir /s /q "dist\mac-stage"
mkdir "%STAGE%\app"

copy /y "mac\Start Race Manager.command" "%STAGE%\" >nul
copy /y "mac\README.txt" "%STAGE%\" >nul
copy /y "app\server.py" "%STAGE%\app\" >nul
copy /y "app\race-manager.html" "%STAGE%\app\" >nul
copy /y "app\VERSION" "%STAGE%\app\" >nul

powershell -Command "Compress-Archive -Force -Path 'dist\mac-stage\TamiyaRaceManager' -DestinationPath 'dist\TamiyaRaceManager-Mac-%APPVERSION%.zip'"
rmdir /s /q "dist\mac-stage"

if not exist "dist\TamiyaRaceManager-Mac-%APPVERSION%.zip" (
    echo  BUILD FAILED.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Done: dist\TamiyaRaceManager-Mac-%APPVERSION%.zip
echo  ==========================================
echo.
pause
