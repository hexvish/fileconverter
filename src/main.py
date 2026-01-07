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
    
    if len(sys.argv) > 1:
        # Context Menu Mode
        file_paths = sys.argv[1:]
        progress_window = ProgressWindow(auto_start=False)
        
        for path in file_paths:
            if os.path.isfile(path):
                file_type = FileDetector.detect(path)
                presets = PresetManager.get_presets(file_type)
                default_preset = next(iter(presets.keys())) if presets else "Unknown"
                progress_window.add_file(path, default_preset)
        
        progress_window.show_window()
    else:
        # GUI Mode
        window = MainWindow()
        window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
