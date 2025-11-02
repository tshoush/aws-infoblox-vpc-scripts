#!/bin/bash
# Setup script for prop_infoblox_import_complete.py
# This script creates a virtual environment and installs dependencies

set -e  # Exit on error

echo "=========================================="
echo "PropInfoBlox Import Complete Setup"
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
VENV_DIR="venv_prop_complete"
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
pip install -r requirements_prop_complete.txt

echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "To use the script:"
echo "  1. Activate the virtual environment:"
echo "     source $VENV_DIR/bin/activate"
echo ""
echo "  2. Run the script:"
echo "     python prop_infoblox_import_complete.py --help"
echo ""
echo "  3. Example usage:"
echo "     python prop_infoblox_import_complete.py --dry-run"
echo ""
echo "  4. When done, deactivate the environment:"
echo "     deactivate"
echo ""
