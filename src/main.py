import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from src.ui.mainwindow import MainWindow
from src.ui.progresswindow import ProgressWindow
from src.core.file_detector import FileDetector
from src.core.preset_manager import PresetManager
from src.ui.custom_dialog import CustomPresetDialog
import src.cli as cli_module

def main():
    # Check for CLI-specific arguments first
    cli_flags = ["--list-presets", "--install-integration", "--preset", "-h", "--help"]
    # Check if any argument matches or looks like a CLI operation
    # Note: --quick-convert is a GUI operation
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--list-presets", "--install-integration"] or "--preset" in sys.argv:
             cli_module.main()
             return

    app = QApplication(sys.argv)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick-convert":
        if len(sys.argv) < 3:
            print("Usage: main.py --quick-convert <preset_name> <file1> [file2 ...]")
            sys.exit(1)
            
        preset_name = sys.argv[2]
        files = sys.argv[3:]
        
        custom_config = None
        
        # Handle Custom Preset Interactivity
        if preset_name == "Custom..." and len(files) > 0:
            # We need to detect file type of the first file to show correct options
            first_file = files[0]
            if os.path.exists(first_file):
                file_type = FileDetector.detect(first_file)
                dialog = CustomPresetDialog(file_type.name)
                if dialog.exec():
                    custom_config = dialog.get_config()
                else:
                    # User cancelled
                    sys.exit(0)
        
        # Quick Convert Mode: Direct to ProgressWindow
        progress_window = ProgressWindow(auto_start=True)
        for path in files:
            if os.path.isfile(path):
                 progress_window.add_file(os.path.basename(path), preset_name, path, custom_config)
        
        progress_window.show_window()
        
    else:
        # Standard GUI Mode
        window = MainWindow()
        
        if len(sys.argv) > 1:
            # Load files from arguments
            file_paths = sys.argv[1:]
            for path in file_paths:
                if os.path.isfile(path):
                    window.add_file(path)
        
        window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
