#!/bin/bash

# Nautilus script to launch FileConverter
# Place this in ~/.local/share/nautilus/scripts/

# Determine the absolute path to the main.py
# Assuming this script is in src/scripts/ and main.py is in src/
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJECT_ROOT="$(dirname "$dirname "$SCRIPT_DIR")")" # Points to project root

# Adjust this path if installed differently
PYTHON_EXEC="python3"
MAIN_PY="$SCRIPT_DIR/../main.py"

# NAUTILUS_SCRIPT_SELECTED_FILE_PATHS contains newline-separated paths
# We need to quote them properly
quoted_paths=""
check_paths=""

# IFS is Internal Field Separator. set it to newline
IFS='
'
for selection in $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS; do
    quoted_paths="$quoted_paths \"$selection\""
done

# Run the python script
eval "$PYTHON_EXEC \"$MAIN_PY\" $quoted_paths"
