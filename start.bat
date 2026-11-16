@echo off
REM JOLODHAR - Start Script for Windows / VS Code Terminal
REM Team Aphelion - NASA Space Apps Challenge
REM Usage: start.bat

cd /d "%~dp0"

echo ==========================================
echo   JOLODHAR - Smart IoT-ML Drain Monitoring
echo   Team Aphelion - NASA Space Apps
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo Install: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Step 1: Create venv if not exists
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
)

REM Step 2: Activate venv
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Step 3: Install dependencies
echo [3/4] Installing dependencies this may take a few minutes on first run...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Step 4: Train model if not exists
if not exist "ml\model.pkl" (
    echo [4/4] Training ML model first run only...
    python ml\train_model.py
) else (
    echo [4/4] ML model already trained.
)

echo.
echo ==========================================
echo   Starting JOLODHAR Server
echo ==========================================
echo Public:  http://localhost:5000/public
echo Login:   http://localhost:5000/login
echo          admin / jolodhar2025
echo ==========================================
echo Press Ctrl+C to stop.
echo.

python app.py

pause
