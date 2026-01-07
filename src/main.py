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

def main():
    app = QApplication(sys.argv)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick-convert":
        if len(sys.argv) < 3:
            print("Usage: main.py --quick-convert <preset_name> <file1> [file2 ...]")
            sys.exit(1)
            
        preset_name = sys.argv[2]
        files = sys.argv[3:]
        
        # Quick Convert Mode: Direct to ProgressWindow
        progress_window = ProgressWindow(auto_start=True)
        for path in files:
            if os.path.isfile(path):
                 progress_window.add_file(os.path.basename(path), preset_name, path)
        
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
