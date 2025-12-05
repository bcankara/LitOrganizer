@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ============================================================================
:: LitOrganizer - Windows Launcher Script
:: This script sets up and runs LitOrganizer on Windows
:: ============================================================================

title LitOrganizer Launcher
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════════════╗
echo  ║                                                                   ║
echo  ║   ██╗     ██╗████████╗ ██████╗ ██████╗  ██████╗  █████╗ ███╗   ██╗ ║
echo  ║   ██║     ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝ ██╔══██╗████╗  ██║ ║
echo  ║   ██║     ██║   ██║   ██║   ██║██████╔╝██║  ███╗███████║██╔██╗ ██║ ║
echo  ║   ██║     ██║   ██║   ██║   ██║██╔══██╗██║   ██║██╔══██║██║╚██╗██║ ║
echo  ║   ███████╗██║   ██║   ╚██████╔╝██║  ██║╚██████╔╝██║  ██║██║ ╚████║ ║
echo  ║   ╚══════╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ║
echo  ║                                                                   ║
echo  ║              Academic Literature Organizer                        ║
echo  ╚═══════════════════════════════════════════════════════════════════╝
echo.

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [INFO] Working directory: %SCRIPT_DIR%
echo.

:: ============================================================================
:: STEP 1: Check for Python 3.11
:: ============================================================================
echo [STEP 1/4] Checking Python installation...

set "PYTHON_CMD="
set "PYTHON_VERSION="

:: Check py launcher first (most reliable on Windows)
where py >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('py -3.11 --version 2^>nul') do set "PYTHON_VERSION=%%i"
    if defined PYTHON_VERSION (
        set "PYTHON_CMD=py -3.11"
        echo [OK] Found !PYTHON_VERSION! via py launcher
        goto :python_found
    )
)

:: Check python3.11 directly
where python3.11 >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python3.11 --version 2^>nul') do set "PYTHON_VERSION=%%i"
    if defined PYTHON_VERSION (
        set "PYTHON_CMD=python3.11"
        echo [OK] Found !PYTHON_VERSION!
        goto :python_found
    )
)

:: Check python command and verify version
where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims= " %%i in ('python --version 2^>nul') do set "PY_VER=%%i"
    echo !PY_VER! | findstr /B "3.11" >nul
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=python"
        set "PYTHON_VERSION=Python !PY_VER!"
        echo [OK] Found Python !PY_VER!
        goto :python_found
    )
    echo [WARNING] Found Python !PY_VER! but version 3.11.x is recommended
)

:: Python 3.11 not found
echo.
echo [ERROR] Python 3.11 is not installed!
echo.
echo Please install Python 3.11 from one of these sources:
echo.
echo   1. Official Python website:
echo      https://www.python.org/downloads/release/python-31110/
echo.
echo   2. Microsoft Store:
echo      https://apps.microsoft.com/detail/9nrwmjp3717k
echo.
echo   3. Using winget (Windows Package Manager):
echo      winget install Python.Python.3.11
echo.
echo IMPORTANT: During installation, make sure to check:
echo   [x] "Add Python to PATH"
echo   [x] "Install py launcher"
echo.
echo After installing Python, please run this script again.
echo.
pause
exit /b 1

:python_found
echo.

:: ============================================================================
:: STEP 2: Create Virtual Environment
:: ============================================================================
echo [STEP 2/4] Setting up virtual environment...

if exist ".venv\Scripts\activate.bat" (
    echo [OK] Virtual environment already exists
) else (
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

:: Activate virtual environment
call .venv\Scripts\activate.bat
echo.

:: ============================================================================
:: STEP 3: Install Dependencies
:: ============================================================================
echo [STEP 3/4] Checking and installing dependencies...

:: Upgrade pip first
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet

:: Check if requirements are installed
python -c "import PyQt5; import fitz; import pdfplumber" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Installing required packages...
    echo [INFO] This may take a few minutes on first run...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies!
        echo [INFO] Trying alternative installation...
        pip install PyQt5 PyMuPDF pdfplumber pdf2image pytesseract Pillow python-docx pandas openpyxl requests python-dateutil tqdm
    )
) else (
    echo [OK] All dependencies are already installed
)
echo.

:: ============================================================================
:: STEP 4: Launch LitOrganizer
:: ============================================================================
echo [STEP 4/4] Launching LitOrganizer...
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

python litorganizer.py

:: Deactivate on exit
call .venv\Scripts\deactivate.bat 2>nul

echo.
echo [INFO] LitOrganizer has closed.
pause
