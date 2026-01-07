#!/usr/bin/env python3
import os
import json
import stat
import shutil

# Configuration
# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
PRESETS_JSON = os.path.join(PROJECT_ROOT, "src", "resources", "presets.json")

# Potential script directories
TARGET_DIRS = [
    os.path.expanduser("~/.local/share/nautilus/scripts/File Converter"),
    os.path.expanduser("~/.local/share/nemo/scripts/File Converter"),
    os.path.expanduser("~/.gnome2/nemo-scripts/File Converter")
]

def main():
    if not os.path.exists(PRESETS_JSON):
        print(f"Error: presets.json not found at {PRESETS_JSON}")
        return

    # Load Presets
    with open(PRESETS_JSON, 'r') as f:
        data = json.load(f)

    # Template setup
    # Check for override (e.g. from frozen executable)
    custom_exec = os.environ.get("FILECONVERTER_EXEC_PATH")
    if custom_exec:
        python_exec = "" # Not needed if executing binary directly? Wait, binary needs arguments. 
        # If binary, command is: /path/to/binary --quick-convert ...
        # If python, command is: /path/to/python /path/to/main.py --quick-convert ...
        
        # We need to adjust the template based on this.
        # Let's assume custom_exec is the full command prefix to run the app.
        pass
    else:
        python_exec = "python3" # Default
        
    main_py_path = os.path.join(PROJECT_ROOT, "src", "main.py")
    
    # If custom_exec is set (frozen), we use it as the command and ignore main_py_path
    # If not, we try to use venv python + main.py
    
    if custom_exec:
        base_cmd = f'"{custom_exec}"' # The binary itself
        # When running the binary, we don't need "python src/main.py", just the binary path
    else:
        # Development mode
        venv_python = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")
        if os.path.exists(venv_python):
            python_exec = venv_python
        
        base_cmd = f'"{python_exec}" "{main_py_path}"'


    # Determine valid targets
    valid_targets = []
    for path in TARGET_DIRS:
        # Check if parent directory exists (e.g. ~/.local/share/nemo/scripts)
        parent = os.path.dirname(path)
        if os.path.exists(parent):
            valid_targets.append(path)
    
    if not valid_targets:
        print("No compatible file manager script directory found (Nautilus or Nemo).")
        print(f"Checked: {[os.path.dirname(p) for p in TARGET_DIRS]}")
        return

    for target_dir in valid_targets:
        print(f"Installing scripts to: {target_dir}")
        
        # Prepare Directory
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        os.makedirs(target_dir)

        # Generate Scripts
        for category, presets in data.items():
            cat_dir_name = category.title() 
            cat_path = os.path.join(target_dir, cat_dir_name)
            os.makedirs(cat_path, exist_ok=True)
            
            for preset_name in presets.keys():
                safe_name = preset_name.replace("/", "-")
                script_path = os.path.join(cat_path, f"{safe_name}")
                
                # Check for Nemo-specific environment variable if needed
                # Nautilus uses NAUTILUS_SCRIPT_SELECTED_FILE_PATHS
                # Nemo uses NEMO_SCRIPT_SELECTED_FILE_PATHS
                # We can use a unified approach or check both.
                
                script_content = f"""#!/bin/bash
# Generated for preset: {preset_name}

# Unified selection retrieval
SELECTED_FILES="$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS"
if [ -z "$SELECTED_FILES" ]; then
    SELECTED_FILES="$NEMO_SCRIPT_SELECTED_FILE_PATHS"
fi

if [ -z "$SELECTED_FILES" ]; then
    # Fallback or empty
    exit 0
fi

# Quote all selected files
quoted_paths=""
IFS='
'
for selection in $SELECTED_FILES; do
    quoted_paths="$quoted_paths \\"$selection\\""
done

# Execute
eval "{base_cmd} --quick-convert \\"{preset_name}\\" $quoted_paths"
"""
                
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                # Make executable
                st = os.stat(script_path)
                os.chmod(script_path, st.st_mode | stat.S_IEXEC)
                
    print("Done! You may need to restart your file manager (nautilus -q or nemo -q).")

if __name__ == "__main__":
    main()
