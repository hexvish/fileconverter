#!/bin/bash

# Nautilus script to launch FileConverter
# Place this in ~/.local/share/nautilus/scripts/

# Determine the absolute path to the main.py
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
# Fix: Go up two levels from src/scripts to get to project root
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")" 

PYTHON_EXEC="$PROJECT_ROOT/.venv/bin/python"
CLI_PY="$PROJECT_ROOT/src/cli.py"

# Check if we have selected files
if [ -z "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" ]; then
    zenity --error --text="No files selected."
    exit 1
fi

# Get the first file to determine presets
FIRST_FILE=$(echo "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS" | head -n 1)

# Fetch presets for this file type
# We use the CLI tool to get the list
PRESETS=$("$PYTHON_EXEC" "$CLI_PY" --list-presets "$FIRST_FILE")

if [ -z "$PRESETS" ]; then
    zenity --error --text="No presets found for this file type."
    exit 1
fi

# Show selection dialog
SELECTED_PRESET=$(echo "$PRESETS" | zenity --list --title="Select Preset" --column="Preset" --height=400)

if [ -z "$SELECTED_PRESET" ]; then
    # User cancelled
    exit 0
fi

# Prepare file list
quoted_paths=""
IFS='
'
for selection in $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS; do
    quoted_paths="$quoted_paths \"$selection\""
done

# Execute conversion in a terminal window so user can see progress (or just run in background?)
# Let's run in a terminal to show progress
gnome-terminal -- bash -c "$PYTHON_EXEC \"$CLI_PY\" $quoted_paths --preset \"$SELECTED_PRESET\"; echo 'Press Enter to close'; read"
