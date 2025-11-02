#!/bin/bash
# Setup script for aws_infoblox_vpc_manager_complete.py
# This script creates a virtual environment and installs dependencies

set -e  # Exit on error

echo "=========================================="
echo "AWS InfoBlox VPC Manager Setup"
echo "=========================================="
echo ""

# Prompt for Python path
read -p "Enter the path to your Python executable (default: python3): " PYTHON_PATH
PYTHON_PATH=${PYTHON_PATH:-python3}

# Verify Python exists
if ! command -v "$PYTHON_PATH" &> /dev/null; then
    echo "❌ Error: Python executable not found at '$PYTHON_PATH'"
    echo "Please ensure Python 3.8+ is installed and provide the correct path."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$("$PYTHON_PATH" --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"

# Check if version is 3.8+
MIN_VERSION="3.8"
if ! "$PYTHON_PATH" -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Python 3.8 or higher is required"
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "📁 Working directory: $SCRIPT_DIR"

# Create virtual environment
VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    read -p "Virtual environment already exists. Recreate it? (y/N): " RECREATE
    if [[ $RECREATE =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    else
        echo "✅ Using existing virtual environment"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "🔨 Creating virtual environment..."
    "$PYTHON_PATH" -m venv "$VENV_DIR"
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Check for config file
echo ""
echo "🔧 Checking configuration..."
if [ ! -f "config.env" ]; then
    if [ -f "config.env.template" ]; then
        cp config.env.template config.env
        echo "✅ Created config.env from template"
        echo "⚠️  Please edit config.env with your InfoBlox details before running the tool"
    else
        echo "⚠️  No config.env found. You may need to create one."
    fi
else
    echo "✅ config.env already exists"
fi

echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "To use the script:"
echo "  1. Activate the virtual environment:"
echo "     source $VENV_DIR/bin/activate"
echo ""
echo "  2. Edit config.env with your InfoBlox credentials"
echo ""
echo "  3. Run the script:"
echo "     python aws_infoblox_vpc_manager_complete.py --help"
echo ""
echo "  4. Example usage (quiet mode with -q flag):"
echo "     python aws_infoblox_vpc_manager_complete.py -q --dry-run"
echo ""
echo "  5. Example usage (silent mode - minimal output):"
echo "     python aws_infoblox_vpc_manager_complete.py --silent --dry-run"
echo ""
echo "  6. Example usage (non-interactive automation mode):"
echo "     python aws_infoblox_vpc_manager_complete.py --no-interactive --create-missing"
echo ""
echo "  7. When done, deactivate the environment:"
echo "     deactivate"
echo ""
echo "🔒 Remember: Always test with --dry-run first!"
echo ""
