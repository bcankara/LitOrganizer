@echo off
chcp 65001 >nul

:: ============================================================================
:: LitOrganizer v2.0.0 - Windows Launcher
:: ============================================================================

title LitOrganizer

echo.
echo   LitOrganizer v2.0.0
echo   Organize your academic literature efficiently
echo   ─────────────────────────────
echo.

:: Get script directory and change to it
cd /d "%~dp0"

:: ============================================================================
:: STEP 1: Check for Python
:: ============================================================================
echo [1/4] Checking Python...

:: Try py launcher first
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Python found via py launcher
    set "PYTHON_CMD=py -3"
    goto :setup_venv
)

:: Try python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Python found
    set "PYTHON_CMD=python"
    goto :setup_venv
)

:: Python not found
echo.
echo   [ERROR] Python is not installed!
echo.
echo   Install Python 3.10+ from:
echo     https://www.python.org/downloads/
echo.
echo   Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:: ============================================================================
:: STEP 2: Virtual Environment
:: ============================================================================
:setup_venv
echo.
echo [2/4] Setting up environment...

if exist ".venv\Scripts\python.exe" (
    echo   [OK] Virtual environment exists
) else (
    echo   Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if not exist ".venv\Scripts\python.exe" (
        echo   [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo   [OK] Created
)

:: Activate virtual environment
echo   Activating virtual environment...
call .venv\Scripts\activate.bat

:: Verify activation
where python 2>nul | findstr /i ".venv" >nul
if %errorlevel% neq 0 (
    echo   [WARN] Virtual environment may not be activated properly
)

echo.

:: ============================================================================
:: STEP 3: Install Dependencies
:: ============================================================================
:install_deps
echo [3/4] Checking dependencies...

:: Update pip silently
echo   Updating pip...
python -m pip install --upgrade pip >nul 2>&1

:: Check if core packages exist
python -c "import flask; import fitz; import pdfplumber" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] All dependencies already installed
    goto :launch
)

:: Install dependencies
echo   Installing packages (first run may take a few minutes)...
echo.

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo   [WARN] requirements.txt install had issues, trying explicit packages...
    pip install Flask flask-socketio PyMuPDF pdfplumber pdf2image pytesseract Pillow python-docx pandas openpyxl requests python-dateutil tqdm
)

:: Verify installation
echo.
python -c "import flask; import fitz; import pdfplumber" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] Core dependencies could not be installed!
    echo   Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo   [OK] Dependencies installed successfully
echo.

:: ============================================================================
:: STEP 4: Launch Application
:: ============================================================================
:launch
echo [4/4] Starting LitOrganizer...
echo   ─────────────────────────────
echo.

python litorganizer.py

:: Cleanup
echo.
echo   LitOrganizer closed.
pause
