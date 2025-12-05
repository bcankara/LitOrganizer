#!/bin/bash
# ============================================================================
# LitOrganizer - macOS Double-Click Launcher
# Double-click this file to start LitOrganizer on macOS
# ============================================================================

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the main launcher script
"$SCRIPT_DIR/start_litorganizer.sh"
