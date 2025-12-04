@echo off
REM PDF Compare Tool - Windows Runner Script
REM This script sets up and runs the PDF comparison tool.

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo PDF Compare Tool
echo =================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -q -r requirements.txt
echo [OK] Dependencies installed
echo.

echo Starting PDF Compare Tool...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app
python app.py

pause
