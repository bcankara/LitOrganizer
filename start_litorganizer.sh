#!/bin/bash

# ============================================================================
# LitOrganizer v2.0 - macOS/Linux Launcher
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
DIM='\033[2m'
NC='\033[0m'

echo ""
echo "  LitOrganizer v2.0"
echo "  Academic Literature Organizer"
echo -e "  ${DIM}─────────────────────────────${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detect OS
OS_TYPE="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
fi

# ============================================================================
# STEP 1: Check for Python
# ============================================================================
echo -e "${BLUE}[1/4]${NC} Checking Python..."

PYTHON_CMD=""

# Check python3 first
if command -v python3 &> /dev/null; then
    PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python3"
    echo -e "  ${GREEN}[OK]${NC} Python $PY_VER"
elif command -v python &> /dev/null; then
    PY_VER=$(python --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python"
    echo -e "  ${GREEN}[OK]${NC} Python $PY_VER"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo -e "  ${RED}[ERROR]${NC} Python is not installed!"
    echo ""
    if [ "$OS_TYPE" == "macos" ]; then
        echo "  Install via Homebrew:"
        echo "    brew install python"
        echo ""
        if command -v brew &> /dev/null; then
            read -p "  Install now via Homebrew? (y/n): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                brew install python
                PYTHON_CMD="python3"
                PY_VER=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
                echo -e "  ${GREEN}[OK]${NC} Python $PY_VER installed"
            else
                exit 1
            fi
        fi
    elif [ "$OS_TYPE" == "linux" ]; then
        echo "  Install using your package manager:"
        echo "    Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
        echo "    Fedora:        sudo dnf install python3"
        echo "    Arch:          sudo pacman -S python"
    fi

    if [ -z "$PYTHON_CMD" ]; then
        echo "  After installing Python, run this script again."
        exit 1
    fi
fi

echo ""

# ============================================================================
# STEP 2: Virtual Environment
# ============================================================================
echo -e "${BLUE}[2/4]${NC} Setting up environment..."

if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
    echo -e "  ${GREEN}[OK]${NC} Virtual environment exists"
else
    echo "  Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "  ${RED}[ERROR]${NC} Failed to create virtual environment!"
        echo "  On some Linux systems: sudo apt install python3-venv"
        exit 1
    fi
    echo -e "  ${GREEN}[OK]${NC} Created"
fi

source .venv/bin/activate
echo ""

# ============================================================================
# STEP 3: Install Dependencies
# ============================================================================
echo -e "${BLUE}[3/4]${NC} Checking dependencies..."

python -m pip install --upgrade pip --quiet 2>/dev/null

python -c "import flask; import fitz; import pdfplumber" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  Installing packages (first run may take a minute)..."
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo "  Retrying with explicit packages..."
        pip install Flask flask-socketio PyMuPDF pdfplumber pdf2image pytesseract Pillow python-docx pandas openpyxl requests python-dateutil tqdm
    fi
else
    echo -e "  ${GREEN}[OK]${NC} All dependencies installed"
fi
echo ""

# ============================================================================
# STEP 4: Launch
# ============================================================================
echo -e "${BLUE}[4/4]${NC} Starting LitOrganizer..."
echo "  ─────────────────────────────"
echo ""

python litorganizer.py

deactivate 2>/dev/null

echo ""
echo "  LitOrganizer closed."
