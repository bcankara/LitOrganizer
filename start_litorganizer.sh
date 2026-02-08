#!/bin/bash

# ============================================================================
# LitOrganizer v2.0.0 - macOS/Linux Launcher
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
DIM='\033[2m'
NC='\033[0m'

echo ""
echo "  LitOrganizer v2.0.0"
echo "  Organize your academic literature efficiently"
echo -e "  ${DIM}─────────────────────────────${NC}"
echo ""

# Get script directory and change to it
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
    PYTHON_CMD="python3"
    echo -e "  ${GREEN}[OK]${NC} Python found"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "  ${GREEN}[OK]${NC} Python found"
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

if [ -f ".venv/bin/python" ]; then
    echo -e "  ${GREEN}[OK]${NC} Virtual environment exists"
else
    echo "  Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    if [ ! -f ".venv/bin/python" ]; then
        echo -e "  ${RED}[ERROR]${NC} Failed to create virtual environment!"
        echo "  On some Linux systems: sudo apt install python3-venv"
        exit 1
    fi
    echo -e "  ${GREEN}[OK]${NC} Created"
fi

echo "  Activating virtual environment..."
source .venv/bin/activate
echo ""

# ============================================================================
# STEP 3: Install Dependencies
# ============================================================================
echo -e "${BLUE}[3/4]${NC} Checking dependencies..."

# Update pip silently
echo "  Updating pip..."
python -m pip install --upgrade pip >/dev/null 2>&1

# Check if core packages exist
python -c "import flask; import fitz; import pdfplumber" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}[OK]${NC} All dependencies already installed"
else
    # Install dependencies
    echo "  Installing packages (first run may take a few minutes)..."
    echo ""
    
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo -e "  ${RED}[WARN]${NC} requirements.txt install had issues, trying explicit packages..."
        pip install Flask flask-socketio PyMuPDF pdfplumber pdf2image pytesseract Pillow python-docx pandas openpyxl requests python-dateutil tqdm
    fi
    
    # Verify installation
    echo ""
    python -c "import flask; import fitz; import pdfplumber" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "  ${RED}[ERROR]${NC} Core dependencies could not be installed!"
        echo "  Please check the error messages above."
        exit 1
    fi
    
    echo -e "  ${GREEN}[OK]${NC} Dependencies installed successfully"
fi

echo ""

# ============================================================================
# STEP 4: Launch Application
# ============================================================================
echo -e "${BLUE}[4/4]${NC} Starting LitOrganizer..."
echo "  ─────────────────────────────"
echo ""

python litorganizer.py

# Cleanup
deactivate 2>/dev/null
echo ""
echo "  LitOrganizer closed."
