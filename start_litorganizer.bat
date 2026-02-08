@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ============================================================================
:: LitOrganizer v2.0.0 - Windows Launcher
:: ============================================================================

title LitOrganizer

echo.
echo   LitOrganizer v2.0.0
echo   Academic Literature Organizer
echo   ─────────────────────────────
echo.

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: ============================================================================
:: STEP 1: Check for Python
:: ============================================================================
echo [1/4] Checking Python...

set "PYTHON_CMD="

:: Check py launcher first
where py >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims= " %%i in ('py -3 --version 2^>nul') do set "PY_VER=%%i"
    if defined PY_VER (
        set "PYTHON_CMD=py -3"
        echo   [OK] Python !PY_VER!
        goto :python_found
    )
)

:: Check python command
where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims= " %%i in ('python --version 2^>nul') do set "PY_VER=%%i"
    if defined PY_VER (
        set "PYTHON_CMD=python"
        echo   [OK] Python !PY_VER!
        goto :python_found
    )
)

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

:python_found
echo.

:: ============================================================================
:: STEP 2: Virtual Environment
:: ============================================================================
echo [2/4] Setting up environment...

if exist ".venv\Scripts\activate.bat" (
    echo   [OK] Virtual environment exists
) else (
    echo   Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo   [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo   [OK] Created
)

call .venv\Scripts\activate.bat
echo.

:: ============================================================================
:: STEP 3: Install Dependencies
:: ============================================================================
echo [3/4] Checking dependencies...

python -m pip install --upgrade pip --quiet 2>nul

python -c "import flask; import fitz; import pdfplumber" 2>nul
if %errorlevel% neq 0 (
    echo   Installing packages (first run may take a minute)...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo   Retrying with explicit packages...
        pip install Flask flask-socketio PyMuPDF pdfplumber pdf2image pytesseract Pillow python-docx pandas openpyxl requests python-dateutil tqdm
    )
) else (
    echo   [OK] All dependencies installed
)
echo.

:: ============================================================================
:: STEP 4: Launch
:: ============================================================================
echo [4/4] Starting LitOrganizer...
echo   ─────────────────────────────
echo.

python litorganizer.py

call .venv\Scripts\deactivate.bat 2>nul

echo.
echo   LitOrganizer closed.
pause
