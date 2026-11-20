@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title CONTINUITY - Digital Prop Closet and Scene Tracker

echo.
echo  ===============================================================
echo   CONTINUITY - Digital Prop Closet and Scene Tracker
echo  ===============================================================
echo.

REM Locate Python. The Python launcher is preferred on Windows.
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON=py -3"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON=python"
    ) else (
        echo Python 3 was not found.
        echo Install Python 3.10 or later from https://www.python.org/downloads/
        echo During setup, tick "Add Python to PATH". Then run this file again.
        echo.
        pause
        exit /b 1
    )
)

REM Create an isolated environment only on the first run.
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating the local Python environment...
    call %PYTHON% -m venv .venv
    if ERRORLEVEL 1 goto :error
) else (
    echo [1/3] Local Python environment is ready.
)

echo [2/3] Installing / checking application packages...
call ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if ERRORLEVEL 1 goto :error

echo [3/3] Starting the tracker in your browser...
echo.
echo The app will open automatically at: http://127.0.0.1:5000
echo Keep this window open while using the app. Press Ctrl+C to stop it.
echo.

REM app.py opens the default browser after Flask has had time to start.
set "OPEN_BROWSER=1"
call ".venv\Scripts\python.exe" app.py
exit /b %ERRORLEVEL%

:error
echo.
echo The tracker could not start. Review the message above and try again.
echo.
pause
exit /b 1
