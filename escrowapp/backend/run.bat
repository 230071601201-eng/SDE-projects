@echo off
echo.
echo ========================================
echo    EscrowPay - Auto Setup and Run
echo ========================================
echo.

py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo [1/4] Python found!

if not exist "venv" (
    echo [2/4] Creating virtual environment...
    py -m venv venv
) else (
    echo [2/4] Virtual environment exists, skipping...
)

echo [3/4] Activating and installing packages...
call venv\Scripts\activate.bat
py -m pip install --quiet fastapi uvicorn python-jose passlib bcrypt python-dotenv pydantic email-validator python-multipart

if not exist ".env" (
    copy .env.example .env >nul
    echo.
    echo IMPORTANT: Fill in your .env file then run again!
    pause
    exit /b 1
)

echo [4/4] Starting server...
echo.
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
py main.py
pause
