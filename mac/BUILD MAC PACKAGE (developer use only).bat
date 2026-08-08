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

REM  Same build number as the Windows packages: the commit count, so a
REM  Mac zip and a Windows installer from the same commit share a number.
set BUILDNO=0
for /f "delims=" %%i in ('git rev-list --count HEAD 2^>nul') do set BUILDNO=%%i
> app\BUILD echo %BUILDNO%

echo.
echo  Building Mac package v%APPVERSION%.%BUILDNO% ...

set STAGE=dist\mac-stage\TamiyaRaceManager
if exist "dist\mac-stage" rmdir /s /q "dist\mac-stage"
mkdir "%STAGE%\app"

copy /y "mac\Start Race Manager.command" "%STAGE%\" >nul
copy /y "mac\README.txt" "%STAGE%\" >nul
copy /y "app\server.py" "%STAGE%\app\" >nul
copy /y "app\race-manager.html" "%STAGE%\app\" >nul
copy /y "app\VERSION" "%STAGE%\app\" >nul
REM  Without BUILD the app reports build 0 on the Mac
copy /y "app\BUILD" "%STAGE%\app\" >nul

powershell -Command "Compress-Archive -Force -Path 'dist\mac-stage\TamiyaRaceManager' -DestinationPath 'dist\TamiyaRaceManager-Mac-%APPVERSION%.%BUILDNO%.zip'"
rmdir /s /q "dist\mac-stage"

if not exist "dist\TamiyaRaceManager-Mac-%APPVERSION%.%BUILDNO%.zip" (
    echo  BUILD FAILED.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Done: dist\TamiyaRaceManager-Mac-%APPVERSION%.%BUILDNO%.zip
echo  ==========================================
echo.
pause
