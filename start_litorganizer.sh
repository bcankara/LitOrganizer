#!/bin/bash

# ============================================================================
# LitOrganizer - macOS/Linux Launcher Script
# This script sets up and runs LitOrganizer on macOS and Linux
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print banner
echo ""
echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════════════════════════════════╗"
echo "  ║                                                                   ║"
echo "  ║   ██╗     ██╗████████╗ ██████╗ ██████╗  ██████╗  █████╗ ███╗   ██╗ ║"
echo "  ║   ██║     ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝ ██╔══██╗████╗  ██║ ║"
echo "  ║   ██║     ██║   ██║   ██║   ██║██████╔╝██║  ███╗███████║██╔██╗ ██║ ║"
echo "  ║   ██║     ██║   ██║   ██║   ██║██╔══██╗██║   ██║██╔══██║██║╚██╗██║ ║"
echo "  ║   ███████╗██║   ██║   ╚██████╔╝██║  ██║╚██████╔╝██║  ██║██║ ╚████║ ║"
echo "  ║   ╚══════╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ║"
echo "  ║                                                                   ║"
echo "  ║              Academic Literature Organizer                        ║"
echo "  ╚═══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Get script directory (works even if script is called via symlink)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}[INFO]${NC} Working directory: $SCRIPT_DIR"
echo ""

# Detect OS
OS_TYPE="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
fi

# ============================================================================
# STEP 1: Check for Python 3.11
# ============================================================================
echo -e "${BLUE}[STEP 1/4]${NC} Checking Python installation..."

PYTHON_CMD=""
PYTHON_VERSION=""

# Check for python3.11 first
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo -e "${GREEN}[OK]${NC} Found $PYTHON_VERSION"
# Check for python3 and verify version
elif command -v python3 &> /dev/null; then
    PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
    if [[ "$PY_VER" == 3.11* ]]; then
        PYTHON_CMD="python3"
        PYTHON_VERSION="Python $PY_VER"
        echo -e "${GREEN}[OK]${NC} Found Python $PY_VER"
    else
        echo -e "${YELLOW}[WARNING]${NC} Found Python $PY_VER but version 3.11.x is recommended"
    fi
fi

# If Python 3.11 not found, provide installation instructions
if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo -e "${RED}[ERROR]${NC} Python 3.11 is not installed!"
    echo ""
    
    if [ "$OS_TYPE" == "macos" ]; then
        echo "Please install Python 3.11 using one of these methods:"
        echo ""
        echo "  1. Using Homebrew (recommended):"
        echo -e "     ${CYAN}brew install python@3.11${NC}"
        echo ""
        echo "  2. Using pyenv:"
        echo -e "     ${CYAN}brew install pyenv${NC}"
        echo -e "     ${CYAN}pyenv install 3.11.10${NC}"
        echo -e "     ${CYAN}pyenv global 3.11.10${NC}"
        echo ""
        echo "  3. Official installer:"
        echo "     https://www.python.org/downloads/release/python-31110/"
        echo ""
        echo "If you don't have Homebrew, install it first:"
        echo -e "     ${CYAN}/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
        echo ""
        
        # Offer to install via Homebrew
        if command -v brew &> /dev/null; then
            echo ""
            read -p "Would you like to install Python 3.11 via Homebrew now? (y/n): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${BLUE}[INFO]${NC} Installing Python 3.11 via Homebrew..."
                brew install python@3.11
                if [ $? -eq 0 ]; then
                    PYTHON_CMD="python3.11"
                    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
                    echo -e "${GREEN}[OK]${NC} Python 3.11 installed successfully!"
                else
                    echo -e "${RED}[ERROR]${NC} Installation failed. Please try manually."
                    exit 1
                fi
            else
                echo "Please install Python 3.11 and run this script again."
                exit 1
            fi
        fi
        
    elif [ "$OS_TYPE" == "linux" ]; then
        echo "Please install Python 3.11 using your package manager:"
        echo ""
        echo "  Ubuntu/Debian:"
        echo -e "     ${CYAN}sudo apt update${NC}"
        echo -e "     ${CYAN}sudo apt install python3.11 python3.11-venv python3.11-pip${NC}"
        echo ""
        echo "  If Python 3.11 is not in default repos (Ubuntu < 22.04):"
        echo -e "     ${CYAN}sudo add-apt-repository ppa:deadsnakes/ppa${NC}"
        echo -e "     ${CYAN}sudo apt update${NC}"
        echo -e "     ${CYAN}sudo apt install python3.11 python3.11-venv python3.11-pip${NC}"
        echo ""
        echo "  Fedora:"
        echo -e "     ${CYAN}sudo dnf install python3.11${NC}"
        echo ""
        echo "  Arch Linux:"
        echo -e "     ${CYAN}sudo pacman -S python${NC}"
        echo ""
    fi
    
    if [ -z "$PYTHON_CMD" ]; then
        echo "After installing Python, please run this script again."
        exit 1
    fi
fi

echo ""

# ============================================================================
# STEP 2: Create Virtual Environment
# ============================================================================
echo -e "${BLUE}[STEP 2/4]${NC} Setting up virtual environment..."

if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
    echo -e "${GREEN}[OK]${NC} Virtual environment already exists"
else
    echo -e "${BLUE}[INFO]${NC} Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Failed to create virtual environment!"
        echo ""
        echo "On some Linux systems, you may need to install venv:"
        echo -e "  ${CYAN}sudo apt install python3.11-venv${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Virtual environment created"
fi

# Activate virtual environment
source .venv/bin/activate
echo ""

# ============================================================================
# STEP 3: Install Dependencies
# ============================================================================
echo -e "${BLUE}[STEP 3/4]${NC} Checking and installing dependencies..."

# Upgrade pip first
echo -e "${BLUE}[INFO]${NC} Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Check if main dependencies are installed
python -c "import PyQt5; import fitz; import pdfplumber" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${BLUE}[INFO]${NC} Installing required packages..."
    echo -e "${YELLOW}[INFO]${NC} This may take a few minutes on first run..."
    
    # Install requirements
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[WARNING]${NC} Some packages may have failed. Trying alternative installation..."
        pip install PyQt5 PyMuPDF pdfplumber pdf2image pytesseract Pillow python-docx pandas openpyxl requests python-dateutil tqdm
    fi
else
    echo -e "${GREEN}[OK]${NC} All dependencies are already installed"
fi
echo ""

# ============================================================================
# STEP 4: Launch LitOrganizer
# ============================================================================
echo -e "${BLUE}[STEP 4/4]${NC} Launching LitOrganizer..."
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

python litorganizer.py

# Deactivate on exit
deactivate 2>/dev/null

echo ""
echo -e "${BLUE}[INFO]${NC} LitOrganizer has closed."
