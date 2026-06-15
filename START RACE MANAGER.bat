@echo off
title Tamiya Race Manager
echo.
echo  ==========================================
echo   TAMIYA RACE MANAGER v9.13
echo  ==========================================
echo.

REM ── Use bundled Python (included in this folder) ─────────────
if exist "%~dp0python-bundle\python.exe" (
    echo  Starting Race Manager...
    echo  [Closes automatically when you close the browser tab]
    echo.
    "%~dp0python-bundle\python.exe" "%~dp0server.py"
    goto end
)

REM ── Bundled Python missing ────────────────────────────────────
echo  ERROR: Python bundle not found.
echo.
echo  The python-bundle folder is missing from this app folder.
echo  Please contact your system administrator to restore it.
echo.
echo  Expected location:
echo  %~dp0python-bundle\python.exe
echo.
pause

:end
