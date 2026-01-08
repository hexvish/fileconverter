#!/bin/bash
set -e

# Ensure we are in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Use virtual environment python
PYTHON_EXEC=".venv/bin/python"
PIP_EXEC=".venv/bin/pip"
PYINSTALLER_EXEC=".venv/bin/pyinstaller"

if [ ! -f "$PYTHON_EXEC" ]; then
    echo "Error: Virtual environment not found at .venv"
    exit 1
fi

if [ ! -f "$PYINSTALLER_EXEC" ]; then
    echo "PyInstaller not found in venv. Installing..."
    "$PIP_EXEC" install pyinstaller
fi

echo "Building FileConverter..."

# Clean previous build
rm -rf dist build *.spec files_to_convert.txt

# Run PyInstaller
"$PYINSTALLER_EXEC" --noconfirm --onefile --name "FileConverter" \
    --add-data "src/resources/presets.json:src/resources" \
    --add-data "fileconverter.desktop:." \
    --hidden-import "PySide6" \
    --paths "." \
    --hidden-import "src.integration" \
    --hidden-import "Shiboken6" \
    run.py

echo "Build complete! Executable is in 'dist/FileConverter'"
echo "You can verify it by running: ./dist/FileConverter"
echo "To install context menu integration for this binary, run: ./dist/FileConverter --install-integration"
