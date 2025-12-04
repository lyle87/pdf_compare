@echo off
REM PDF Compare Tool - Windows Runner Script
REM This script sets up and runs the PDF comparison tool.

setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

echo.
echo PDF Compare Tool
echo =================
echo.

REM Try python3 first, then python
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python is not installed or not in PATH.
        echo Please install Python 3.8 or higher from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

echo [OK] Python found
echo.

REM Create virtual environment if it doesn't exist
set REBUILD_VENV=
set "WINDOWS_VENV_PY=.venv\Scripts\python.exe"
if exist ".venv" (
    if not exist "%WINDOWS_VENV_PY%" (
        REM Existing venv is missing a Windows python executable (possibly created on Linux/macOS)
        if exist ".venv\bin\python" (
            echo Existing virtual environment was built with POSIX paths. Rebuilding for Windows...
        ) else (
            echo Existing virtual environment is missing a python executable. Rebuilding...
        )
        set REBUILD_VENV=1
    )
)

if defined REBUILD_VENV (
    rmdir /s /q .venv
)

if not exist ".venv" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo Error creating virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Prefer using the venv's python directly (don't rely on activate)
echo Locating virtualenv python executable...

REM Use the Windows virtualenv interpreter path; fallback to system Python only if missing
if exist "%WINDOWS_VENV_PY%" (
    set "VENV_PY=%WINDOWS_VENV_PY%"
) else (
    echo Could not find a python executable inside .venv
    echo Will attempt to use the system python: %PYTHON_CMD%
    set "VENV_PY=%PYTHON_CMD%"
)

REM Install/upgrade dependencies using the venv python
echo Installing dependencies using %VENV_PY%...
"%VENV_PY%" -m pip install --upgrade pip >nul 2>&1 || (
    echo Warning: pip upgrade may have failed, continuing...
)
"%VENV_PY%" -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo Error installing dependencies with %VENV_PY%
    echo You can try: %PYTHON_CMD% -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

if not defined PDF_COMPARE_HOST set "PDF_COMPARE_HOST=127.0.0.1"
if not defined PDF_COMPARE_PORT set "PDF_COMPARE_PORT=5000"

echo Starting PDF Compare Tool...
echo Open your browser to: http://%PDF_COMPARE_HOST%:%PDF_COMPARE_PORT%
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app using the venv python
"%VENV_PY%" app.py

pause
