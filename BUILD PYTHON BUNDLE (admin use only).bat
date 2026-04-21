@echo off
title Build Python Bundle
echo.
echo  ==========================================
echo   BUILD PYTHON BUNDLE - Admin Use Only
echo  ==========================================
echo.
echo  This downloads and prepares the Python bundle
echo  that gets shipped with the app.
echo.
echo  Run this ONCE on any internet-connected machine.
echo  Then copy the resulting python-bundle folder
echo  into the race-manager folder before distributing.
echo.
echo  Requires: internet connection, ~15MB download
echo.
pause

if exist "%~dp0python-bundle\python.exe" (
    echo.
    echo  Python bundle already exists at:
    echo  %~dp0python-bundle\python.exe
    echo.
    echo  Delete the python-bundle folder first if you want to rebuild.
    pause
    exit /b 0
)

mkdir "%~dp0python-bundle" 2>nul
cd "%~dp0python-bundle"

echo.
echo  Downloading Python 3.11.9 embeddable package...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python-embed.zip' -UseBasicParsing}"

if not exist "python-embed.zip" (
    echo  Download failed. Check internet connection.
    pause
    exit /b 1
)

echo  Extracting...
powershell -Command "Expand-Archive -Path 'python-embed.zip' -DestinationPath '.' -Force"
del "python-embed.zip"

echo  Configuring...
powershell -Command "(Get-Content 'python311._pth') -replace '#import site','import site' | Set-Content 'python311._pth'"

if exist "python.exe" (
    echo.
    echo  ==========================================
    echo   SUCCESS
    echo  ==========================================
    echo.
    echo  python-bundle folder is ready.
    echo  Include this folder when distributing the app.
    echo.
    echo  Users will not need internet or Python installed.
    echo.
) else (
    echo  Something went wrong. python.exe not found.
)

pause
