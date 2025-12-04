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

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error activating virtual environment
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo Error installing dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo Starting PDF Compare Tool...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app
python app.py

pause
