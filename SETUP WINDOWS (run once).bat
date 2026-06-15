@echo off
title Tamiya Race Manager - Windows Setup
echo.
echo  ==========================================
echo   TAMIYA RACE MANAGER - First Time Setup
echo  ==========================================
echo.
echo  This will download Python for Windows (~15MB).
echo  You only need to do this once.
echo  An internet connection is required.
echo.
echo  After setup, use "START RACE MANAGER.bat" to launch the app.
echo.
pause

echo.
echo  Checking for existing Python bundle...

if exist "python-bundle\python.exe" (
    echo  Python bundle already installed. Setup complete!
    echo.
    pause
    exit /b 0
)

echo  Downloading Python 3.11 portable...
echo  (This may take a minute)
echo.

mkdir python-bundle 2>nul

REM Download Python embeddable package
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python-bundle\python-embed.zip' -UseBasicParsing}"

if not exist "python-bundle\python-embed.zip" (
    echo.
    echo  ERROR: Download failed. Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo  Extracting Python...
powershell -Command "Expand-Archive -Path 'python-bundle\python-embed.zip' -DestinationPath 'python-bundle' -Force"

del "python-bundle\python-embed.zip"

REM The embeddable Python needs pip and a path config fix to import modules
REM Enable site-packages by uncommenting the import line in the pth file
powershell -Command "(Get-Content 'python-bundle\python311._pth') -replace '#import site','import site' | Set-Content 'python-bundle\python311._pth'"

REM Download pip
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python-bundle\get-pip.py' -UseBasicParsing}"

echo  Installing pip...
"python-bundle\python.exe" "python-bundle\get-pip.py" --no-warn-script-location

del "python-bundle\get-pip.py" 2>nul

if not exist "python-bundle\python.exe" (
    echo.
    echo  ERROR: Setup failed. Please try again or contact support.
    echo.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Setup Complete!
echo  ==========================================
echo.
echo  Python is now bundled with the app.
echo  No internet connection needed from here.
echo.
echo  Double-click "START RACE MANAGER.bat" to launch.
echo.
pause
