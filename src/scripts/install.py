
import os
import sys
import shutil
import winreg
import json
from pathlib import Path


def get_project_root():
    return Path(__file__).resolve().parent.parent.parent


def delete_recursive(key, subkey=""):
    try:
        if subkey:
            current_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS)
        else:
            current_key = key

        # Delete all subkeys
        while True:
            try:
                sub = winreg.EnumKey(current_key, 0)
                delete_recursive(current_key, sub)
            except OSError:
                break

        # Delete the key itself
        winreg.CloseKey(current_key)
        if subkey:
            winreg.DeleteKey(key, subkey)
            print(f"Deleted key: {subkey}")

    except Exception as e:
        # Key might not exist
        pass


def install():
    print("Starting installation...")

    # 1. Locate Source
    project_root = get_project_root()
    dist_dir = project_root / "dist" / "FileConverter"
    resources_dir = project_root / "src" / "resources"
    presets_path = resources_dir / "presets.json"

    if not dist_dir.exists():
        print(f"Error: Build directory not found at {dist_dir}")
        print("Please run build_windows.bat first.")
        return False

    if not presets_path.exists():
        print(f"Error: presets.json not found at {presets_path}")
        return False

    # 2. Define Destination
    local_app_data = Path(os.environ["LOCALAPPDATA"])
    install_dir = local_app_data / "Programs" / "FileConverter"

    print(f"Installing to: {install_dir}")

    # 3. Copy Files
    if install_dir.exists():
        print("Remove existing installation...")
        try:
            shutil.rmtree(install_dir)
        except Exception as e:
            print(f"Error removing existing installation: {e}")
            print("Make sure the application is closed.")
            return False

    try:
        shutil.copytree(dist_dir, install_dir)
    except Exception as e:
        print(f"Error copying files: {e}")
        return False

    exe_path = install_dir / "FileConverter.exe"
    if not exe_path.exists():
        print("Error: FileConverter.exe not found in installed files.")
        return False

    # 4. Create Shortcut
    create_shortcut(exe_path)

    # 5. Register Context Menu
    register_context_menu(exe_path, presets_path)

    print("Installation Complete!")
    return True


def create_shortcut(target_exe):
    print("Creating Start Menu shortcut...")
    start_menu = Path(os.environ["APPDATA"]) / \
        "Microsoft" / "Windows" / "Start Menu" / "Programs"
    shortcut_path = start_menu / "FileConverter.lnk"

    vbs_script = f"""
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{target_exe}"
    oLink.WorkingDirectory = "{target_exe.parent}"
    oLink.Save
    """

    vbs_file = Path(os.environ["TEMP"]) / "create_shortcut.vbs"
    try:
        vbs_file.write_text(vbs_script)
        os.system(f"cscript //Nologo {vbs_file}")
        vbs_file.unlink()
    except Exception as e:
        print(f"Warning: Failed to create shortcut: {e}")


def register_context_menu(exe_path, presets_path):
    print("Registering Dynamic Context Menu...")

    # Load Presets
    try:
        with open(presets_path, 'r') as f:
            presets_data = json.load(f)
    except Exception as e:
        print(f"Error loading presets: {e}")
        return

    base_key_path = r"Software\Classes\*\shell\FileConverter"

    # CLEANUP: Delete existing key to remove specific values
    print("Cleaning up old registry keys...")
    try:
        root = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(
            root, r"Software\Classes\*\shell", 0, winreg.KEY_ALL_ACCESS)
        delete_recursive(key, "FileConverter")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Cleanup note (key might not exist): {e}")

    try:
        # 1. Create Root Menu "Convert with FileConverter"
        root_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, base_key_path)
        winreg.SetValueEx(root_key, "", 0, winreg.REG_SZ,
                          "Convert with FileConverter")  # Default Value
        winreg.SetValueEx(root_key, "MUIVerb", 0,
                          winreg.REG_SZ, "Convert with FileConverter")
        winreg.SetValueEx(root_key, "Icon", 0, winreg.REG_SZ, str(exe_path))
        winreg.SetValueEx(root_key, "SubCommands", 0,
                          winreg.REG_SZ, "")  # Required for cascading

        root_shell_key = winreg.CreateKey(root_key, "shell")

        # 2. Add "Media Info"
        mi_key = winreg.CreateKey(root_shell_key, "01_MediaInfo")
        winreg.SetValueEx(mi_key, "", 0, winreg.REG_SZ, "Media Info")
        winreg.SetValueEx(mi_key, "MUIVerb", 0, winreg.REG_SZ, "Media Info")

        mi_cmd_key = winreg.CreateKey(mi_key, "command")
        winreg.SetValueEx(mi_cmd_key, "", 0, winreg.REG_SZ,
                          f'"{exe_path}" --media-info "%1"')

        # 3. Add Categories
        for i, (category, presets) in enumerate(presets_data.items()):
            # Safe key names, sorted by prefix 01_, 02_ etc.
            cat_key_name = f"{i+1:02d}_{category}"

            cat_key = winreg.CreateKey(root_shell_key, cat_key_name)
            winreg.SetValueEx(cat_key, "", 0, winreg.REG_SZ, category.title())
            winreg.SetValueEx(cat_key, "MUIVerb", 0,
                              winreg.REG_SZ, category.title())
            winreg.SetValueEx(cat_key, "SubCommands", 0, winreg.REG_SZ, "")

            cat_shell_key = winreg.CreateKey(cat_key, "shell")

            for j, preset_name in enumerate(presets.keys()):
                preset_key_name = f"{j:02d}_{preset_name.replace(' ', '_')}"

                preset_key = winreg.CreateKey(cat_shell_key, preset_key_name)
                winreg.SetValueEx(preset_key, "", 0,
                                  winreg.REG_SZ, preset_name)
                winreg.SetValueEx(preset_key, "MUIVerb", 0,
                                  winreg.REG_SZ, preset_name)

                cmd_key = winreg.CreateKey(preset_key, "command")
                cmd_str = f'"{exe_path}" --quick-convert "{preset_name}" "%1"'
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, cmd_str)

        print("Context menu registered successfully with cascading options.")

    except Exception as e:
        print(f"Error registering context menu: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    install()
