#!/bin/bash
# PDF Compare Tool - Linux/macOS Runner Script
# This script sets up and runs the PDF comparison tool.

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}PDF Compare Tool${NC}"
echo "================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.8 or higher from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

echo ""
echo -e "${GREEN}Starting PDF Compare Tool...${NC}"
echo -e "Open your browser to: ${BLUE}http://localhost:5000${NC}"
echo "Press ${YELLOW}Ctrl+C${NC} to stop the server"
echo ""

# Run the Flask app
python app.py
