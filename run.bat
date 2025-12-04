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
set VENV_PY=.venv\Scripts\python.exe
if not exist "%VENV_PY%" (
    REM Fallback: older venvs or alternate layout
    set VENV_PY=.venv\bin\python
)

if not exist "%VENV_PY%" (
    echo Could not find venv python at "%VENV_PY%".
    echo Trying to continue using %PYTHON_CMD% (system python).
    set VENV_PY=%PYTHON_CMD%
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

echo Starting PDF Compare Tool...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app using the venv python
"%VENV_PY%" app.py

pause
