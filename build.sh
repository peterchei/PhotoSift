#!/bin/bash

# Exit on any error
set -e

echo "Building PhotoSift for Linux..."

# Project directory (absolute path)
PROJECT_DIR="/home/peterchei/projects/PhotoSift"
cd "$PROJECT_DIR"

# Clean up previous build artifacts
echo "Cleaning up..."
rm -rf dist build __pycache__ build_env_linux

# Create and activate virtual environment
echo "Creating virtual environment using /usr/bin/python3 (Python 3.10)..."
/usr/bin/python3 -m venv build_env_linux
source build_env_linux/bin/activate

# Install required packages
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
pip install pyinstaller
pip install -e .

# Ensure the icon exists (needed for the build process even if not used as native icon on Linux)
if [ ! -f "resources/app.ico" ]; then
    echo "Creating icon..."
    python3 create_icon.py
fi

# Build executable with PyInstaller
echo "Building executable with PyInstaller..."
# On Linux, we use the same spec file but some options might behave differently
pyinstaller PhotoSift.spec

if [ ! -f "dist/PhotoSift" ]; then
    echo "ERROR: PyInstaller failed to create the executable."
    echo "Please check the output above for error messages."
    exit 1
fi

echo "Build complete! Check the dist directory for the executable 'PhotoSift'."

# Deactivate virtual environment
deactivate
