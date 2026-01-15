import sys
import os
import winreg
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def register_context_menu():
    # Path to the executable
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
    else:
        # If running from source (development)
        print("Warning: Running from python source. This will register 'python file.py' which might be messy.")
        # We generally expect this to be run FROM the built exe or by pointing TO the exe.
        # But for this helper script, let's assume it's run via 'python src/scripts/register_windows.py'
        # and we want to register the PROJECT's main.py entry point?
        # NO, usually we want to register the binary.
        # Let's assume this script is run BY the user after building, OR included in the build.
        # Let's try to find the dist/FileConverter/FileConverter.exe
        # Search for executable in common locations
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        possible_paths = [
            os.path.join(project_root, "dist", "FileConverter", "FileConverter.exe"), # Standard Build
            os.path.join(os.getcwd(), "FileConverter.exe"), # Running from dist folder
            os.path.join(os.getcwd(), "dist", "FileConverter", "FileConverter.exe"), # Running from root
            os.path.abspath("FileConverter.exe") # Current dir
        ]
        
        exe_path = None
        for p in possible_paths:
            if os.path.exists(p):
                exe_path = p
                break
                
        if not exe_path:
            print("Could not find 'FileConverter.exe'.")
            print(f"Searched in: {possible_paths}")
            print("Please make sure you have built the project or placed this script near the executable.")
            
            # Manual Input Fallback
            exe_path = input("Enter full path to FileConverter.exe: ").strip().strip('"')
            if not os.path.exists(exe_path):
                print("Invalid path. Exiting.")
                return

    exe_path = os.path.abspath(exe_path).replace("/", "\\")
    print(f"Registering context menu for: {exe_path}")

    # Key Name in registry (Background context menu)
    # HKEY_CLASSES_ROOT\*\shell\FileConverter
    
    key_path = r"*\shell\FileConverter"
    
    try:
        # Create Key
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Convert with FileConverter")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path)
        
        # Command Key
        # HKEY_CLASSES_ROOT\*\shell\FileConverter\command
        cmd_key = winreg.CreateKey(key, "command")
        # Command: "Path\To\FileConverter.exe" --quick-convert-menu "%1"
        # We use a special flag --quick-convert-menu or just reuse --quick-convert
        # If we reuse --quick-convert, it usually expects args like 'preset' 'file'.
        # On Linux/Nautilus, scripts are used.
        # On Windows, we need the app to OPEN directly. 
        # If we pass "%1", the app needs to handle: `main.py "%1"`
        # Currently `main.py` checks for `--quick-convert` or `--media-info`.
        # If we just pass the file, does it open in GUI? Yes.
        # But maybe we want the "Convert/Media Info" specific options?
        
        # Let's register standard Open (GUI) and maybe a cascading menu if we were advanced.
        # For now, simple "Open in FileConverter".
        
        # NOTE: To support "Media Info" directly from context menu on Windows, 
        # we would need sub-keys (SubCommands).
        # HKEY_CLASSES_ROOT\*\shell\FileConverter\shell\MediaInfo
        
        # Let's stick to simple Open for now, or check if we can add sub-items.
        # Windows 10/11 supports 'SubCommands'.
        
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'"{exe_path}" "%1"')
        
        print("Successfully registered!")
        
    except Exception as e:
        print(f"Error registering keys: {e}")

if __name__ == "__main__":
    if not is_admin():
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        register_context_menu()
        input("Press Enter to exit...")
